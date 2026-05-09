# ADR 001: Tile and Map Authoring Pipeline

## Status

Accepted — 2026-05-09

## Context

The project supports three kinds of authoring that need to coexist:

1. **Hand-painted graphics** — pixel art for tiles, palettes, and animations, authored by humans in a tool that gives them direct visual control.
2. **Hand-built maps** — unique towns, buildings, and set pieces authored by humans in a tool that lets them paint tiles onto a grid and see the result immediately.
3. **Procedurally generated content** — both maps (existing) and tile graphics (new), authored as code by humans or AI agents.

The existing renderer (`scripts/View/MapRenderer.cs`) decouples graphics from gameplay metadata via the EGA palette-swap shader: a tile is "16 EGA-indexed pixels in an atlas region" plus a separate gameplay description, and the renderer doesn't care how either was produced. That decoupling is the foundation this ADR builds on.

What's missing today is a defined pipeline: where graphics come from, how tile metadata stays in sync with pixels, where hand-built maps live, and how runtime-generated tiles coexist with statically authored ones. Without that, contributors (human or AI) don't know which file to edit for a given change, and asset edits drift out of sync with code.

A second goal: AI agents and humans should both be productive contributors. Humans gravitate to visual tools; agents gravitate to text and code. The pipeline should give each side a natural surface to work on without forcing the other side through it.

## Decision

A three-layer pipeline with clearly separated responsibilities and a single shared abstraction (`MapData`) downstream of all three.

### Layer 1 — Aseprite (humans): graphics, palettes, animations

- `assets/aseprite/atlas.aseprite` is the source of truth for hand-painted tile pixels. Tiles are organized as Aseprite **slices** with names matching tile semantics (`grass`, `water_0`, `door_closed`).
- The 16 EGA reference colors live in `assets/aseprite/palettes/ega.gpl`. Mood palettes (`dungeon.gpl`, `fire.gpl`, …) are sibling files in the same directory.
- Animations are Aseprite **tags** (`water: 0–3 loop`, `torch: 4–7 ping-pong`).
- A build step invokes the Aseprite CLI to export:
  - `assets/tiles/aseprite_atlas.png`
  - `assets/tiles/aseprite_manifest.json` (slice rects + tag frame ranges + per-frame durations)
  - `assets/palettes/*.png` (16×1 textures, one per `.gpl`)

### Layer 2 — C# build-time generator (humans + agents): procedural variants and parametric families

- `tools/Tilegen/` is a C# console app (`dotnet run --project tools/Tilegen`) that produces additional tiles algorithmically.
- Operates on a `TileCanvas` (16×16 grid of `byte` EGA indices) using a shared library of pixel-art primitives: `Fill`, `Border`, `Dither`, `Noise`, `Stamp`, `Compose`, etc.
- Recipes are deterministic functions of `(seed, params)` — same inputs always produce the same pixels.
- Outputs:
  - `assets/tiles/procedural_atlas.png`
  - `assets/tiles/procedural_manifest.json`

### Layer 2 (continued) — Merge step and downstream artifacts

A merge step combines the Aseprite and procedural outputs into the final build artifacts that everything else consumes:

- `assets/tiles/atlas.png` — the runtime atlas
- `assets/tiles/atlas_manifest.json` — flat list of named tiles with regions and animation tags
- `assets/tiles/tileset.tres` — Godot `TileSet` resource generated from the manifest
- `scripts/Core/TileId.generated.cs` — strongly-typed tile references (see invariant 6 below)

All of these are generated artifacts and all are checked in (see invariant 10).

### Layer 2 (continued) — Godot editor (humans): hand-built maps

- Hand-built maps are `.tscn` files under `maps/` with one or more `TileMapLayer` nodes referencing `tileset.tres`.
- Humans paint them in the Godot editor.
- A `MapLoader` reads a `.tscn` into `MapData` at startup. The renderer doesn't care whether a map was hand-built or procedurally generated.

### Layer 2 (continued) — C# procedural map generators (agents primarily)

- Existing generators in `scripts/Generation/` continue to emit `MapData` directly.
- Unchanged by this ADR.

### Layer 3 — C# runtime tile generator (agents primarily): per-instance variants

- `scripts/View/Tilegen/` contains `ITileRecipe` implementations operating on the same `TileCanvas` and primitives as the build-time generator. The two generators share the canvas library; only their drivers differ.
- A `RuntimeTileAtlas` wraps an `Image` + `ImageTexture` allocated at game start; generators write into it.
- A `RuntimeTileRegistry` exposes `Bake(BakeRequest) -> TileBakeResult` returning one or more `TileRef` handles. Map generators call this when they want per-dungeon, per-town, or per-instance variation.
- Animations work via the same call: a recipe can declare N frames, and the registry bakes them as N tiles plus an animation tag.

### Slot mechanism — bridging hand-built maps and runtime recipes

To let humans paint hand-built maps that still benefit from runtime variation:

- The `TileSet` includes **slot tiles** named `slot_<recipe>` (e.g., `slot_dungeon_stone`, `slot_torch`).
- Each slot tile carries a custom data layer field `recipe: "<recipe_name>"`.
- Humans paint slots into hand-built maps in the Godot editor as if they were ordinary tiles.
- At map load, a `MapPostProcess` step scans for slot occurrences, calls `registry.Bake(recipe, seed=(map_seed, x, y))`, and replaces the slot's `TileRef` with the baked one. The result is stored in `MapData`.
- This gives hand-built maps the same per-instance variety procedural maps get, without making humans deal with runtime tiles directly.

### Data flow

```
.aseprite ──Aseprite CLI──> aseprite_atlas.png + aseprite_manifest.json
tools/Tilegen/   ─dotnet run─> procedural_atlas.png + procedural_manifest.json
                                         │
                              merge step ┘
                                    │
                                    ▼
              atlas.png + atlas_manifest.json + palette PNGs
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
            tileset.tres     TileId.generated.cs   (runtime)
                  │                 │                 │
                  ▼                 ▼                 │
         maps/*.tscn        scripts/Generation/       │
         (humans paint)     (procedural maps)         │
                  │                 │                 │
                  └────────┬────────┴────────┬────────┘
                           ▼                 ▼
                       MapData    +    RuntimeTileRegistry.Bake()
                           │                 │
                           └────────┬────────┘
                                    ▼
                          MapPostProcess (slot resolution)
                                    │
                                    ▼
                                MapRenderer
```

## Invariants

These are architectural contracts, not guidelines. Violating them breaks the pipeline.

### 1. Single source of truth per tile

A given tile is *either* hand-painted in Aseprite, *or* build-time procedural, *or* runtime procedural — never authored in more than one place. Naming convention makes the source visible at a glance:

- Hand-painted: simple semantic names (`grass`, `door_closed`).
- Build-time procedural: descriptive names with a structural suffix (`grass_var_a`, `wall_n`, `wall_ne`).
- Runtime: no stable name in the static atlas; identified by `TileRef` returned from the registry.

### 2. EGA-index-only output discipline

Both generators write `byte` 0–15 indices into a `TileCanvas`. The canvas resolves indices → RGB once, against the EGA reference palette, when committing pixels to an `Image`. Generator code never touches RGB. This guarantees the palette-swap shader works on every generated pixel.

### 3. Determinism contract for runtime recipes

`ITileRecipe.Generate(canvas, params)` must be a pure function of `params` (which includes `Seed`). Same inputs → identical pixels, every run. Enables snapshot tests, reproducible bug reports, and stable visuals across save/load.

### 4. Aseprite is required only for asset edits, not for builds

The committed `aseprite_atlas.png` + `aseprite_manifest.json` are the build inputs from Layer 1. Contributors who only touch C# or maps don't need Aseprite installed. CI optionally verifies that regenerating from `.aseprite` files produces no diff against the committed outputs, guarding against drift.

### 5. `MapData` is the abstraction boundary

Renderer and game logic only see `MapData`. Hand-built `.tscn` files, procedural map generators, and runtime-baked tiles all converge there. Nothing downstream of `MapData` knows which producer made a cell.

### 6. Tile id namespacing via enums, not numeric ranges

Tiles are referenced by a typed handle:

```csharp
public enum TileSource { Static, Runtime }

public readonly record struct TileRef(TileSource Source, int Index)
{
    public static TileRef Static(int i)  => new(TileSource.Static, i);
    public static TileRef Runtime(int i) => new(TileSource.Runtime, i);
}
```

`MapData` stores `TileRef`. The renderer pattern-matches on `Source` to pick between the static and runtime atlas textures. The generated `TileId.generated.cs` exposes named static tiles as `TileRef` constants. The registry returns runtime tiles as `TileRef` values. Source mistakes become compile errors instead of mysteriously wrong-looking pixels.

### 7. Atlas merge collision policy: fail loud

If the Aseprite manifest and the build-time generator both declare a tile named `X`, the merge step aborts with a clear error. No silent precedence, no implicit overrides.

### 8. Slot tile signaling

Slot tiles are declared in the `TileSet` with names prefixed `slot_` and a custom data layer field `recipe: "<recipe_name>"`. The map-load post-process is the only code that interprets this convention. Recipe authors don't need to know slots exist; map authors don't need to write code to use them.

### 9. Mood palettes: `.gpl` is source of truth

Aseprite `.gpl` files in `assets/aseprite/palettes/` export to 16×1 PNGs at build. `PaletteDatabase.cs` references the PNGs by name. Hand-coded RGB constants in C# are not allowed for palettes.

### 10. Generated build artifacts are committed

`atlas.png`, `atlas_manifest.json`, palette PNGs, `tileset.tres`, and `TileId.generated.cs` are all checked in. The repository opens cleanly in Godot without running the build, and AI agents can read manifests and IDs from a static checkout. CI verifies that running the build produces no diff.

### 11. Runtime tile pool: permanent, fixed budget

Runtime tiles are baked once per game seed and never evicted. Pool size is a constant (initial value: 256 slots) with a runtime warning when exceeded. Eviction is not implemented unless the budget is hit in practice.

### 12. Single language for procedural generation

Both build-time and runtime tile generators are C#, sharing `TileCanvas` and the pixel-art primitive library. There is no Python in the asset pipeline. Style cohesion between generators is structural — they call the same `Dither`, `Border`, and `Outline` functions — not aspirational.

### 13. Recipes live with their consumers

- Build-time recipes: `tools/Tilegen/Recipes/`
- Runtime recipes: `scripts/View/Tilegen/Recipes/`
- Shared canvas + primitives: `scripts/Core/Tilegen/` (referenced by both)

Snapshot tests for recipes live next to the recipe code.

## Consequences

### Positive

- **Clear authoring surfaces.** Humans use Aseprite and the Godot editor; agents use C#. Neither has to context-switch into the other's tool.
- **Renderer simplicity preserved.** The existing custom `_Draw` + palette-swap shader continues to work unchanged. `TileMapLayer` is added only on the authoring side, not the rendering side; the loader translates `.tscn` content into `MapData`.
- **Variety scales without atlas growth.** Runtime baking means a dungeon can have unique stone without committing N PNG variants per dungeon.
- **Per-tile source of truth means no drift.** Invariants 1, 4, and 10 together ensure that for any given tile, exactly one file is authoritative and the rest are reproducible from it.
- **AI-first procedural authoring.** Recipes are deterministic, snapshot-testable C# functions — exactly the shape AI agents work well with.

### Negative

- **More moving parts.** Aseprite CLI, build-time generator, merge step, TileSet generator, TileId codegen, runtime registry, slot resolver. Each is small but together they're a pipeline to maintain.
- **Runtime tiles are invisible at edit time.** Humans can't paint a specific runtime variant in the Godot editor. The slot mechanism mitigates this for common cases but doesn't eliminate it.
- **Asset diffs are noisier.** Generated PNGs and `.tres` files change whenever generator code or Aseprite sources change. Reviewers need to look at source changes, not committed artifacts.
- **Style cohesion still requires discipline.** Shared primitives prevent mechanical drift, but a hand-painted tile and a procedural tile can still feel mismatched if the recipe doesn't honor the same visual conventions.

### Watch-outs

- **Generator startup cost.** Runtime baking happens at game start (and at map entry). Stay under the budget by keeping recipes O(pixels) and avoiding allocations in tight loops.
- **TileSet drift.** If Aseprite slice names change, `TileId.generated.cs` regenerates, and any C# code referencing renamed constants breaks at compile time. This is intended — the build catches the drift — but it means renames are not free.
- **Snapshot test churn.** Changing a shared primitive (e.g., the Bayer dither pattern) will flip every snapshot that uses it. Treat shared primitive changes as deliberate, reviewed events.

## Alternatives Considered

### A. TileMapLayer for everything (no custom `_Draw`)

Use Godot's `TileMapLayer` as the renderer too. Rejected because the project's existing palette-swap shader integrates more cleanly with a single-node custom renderer, the per-frame work `TileMapLayer` does is wasted in a turn-based game, and the README's existing tradeoff explanation already documents why custom drawing was chosen. This ADR keeps that decision.

### B. Aseprite-only (no procedural tiles)

Author every tile by hand in Aseprite. Rejected because per-instance variation (per-dungeon stone, per-town accent colors) would require committing many near-duplicate tiles, and AI agents would have no path to author tile graphics without binary file editing.

### C. Runtime-only (no static atlas)

Generate every tile at game start. Rejected because hand-painted art is genuinely faster to author for unique, characterful tiles, and humans can't preview runtime tiles in the Godot editor — making hand-built maps would be impractical.

### D. Mixed-language generators (Python build-time, C# runtime)

The earlier draft of this design had Python for build-time and C# for runtime. Rejected in favor of a single language so generators can share `TileCanvas` and primitives by direct reference rather than by convention. The cost is slightly slower iteration than Python; the benefit is structural style cohesion and one fewer toolchain.

### E. ASCII map format as source of truth

Make a custom text format the canonical representation of hand-built maps, with a converter that round-trips to `.tscn`. Deferred, not rejected. `.tscn` is the source of truth for now because humans painting in the Godot editor is the dominant authoring case. If AI-driven map authoring becomes important, a round-tripping ASCII format can be added without changing this ADR's other decisions.

### F. Tile gameplay metadata in the TileSet (custom data layers)

Move walkability, transition kind, etc. onto the `TileSet`'s custom data layers so they're visible in the Godot editor. Rejected because gameplay logic already reads `TileDefinition.cs`, agents edit C# fluently, and splitting metadata across two files would make refactors harder. Metadata stays in C#.
