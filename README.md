# Ultima-like Roguelike

A tile-based roguelike inspired by [Ultima IV](https://wiki.ultimacodex.com/wiki/Ultima_IV_internal_formats). Built in **Godot 4 with C#**, designed for **portrait mobile**, with hand-painted **EGA palette** tiles and **per-map palette swaps** for mood.

You can build, edit, and run this project entirely from **VS Code** or **JetBrains Rider** — no Godot editor required for day-to-day work, though the Godot editor is the easiest way to run it the first time.

This project intentionally implements **only world generation and navigation**. Combat and conversation are out of scope.

---

## What's interesting about this project

### 1. Real EGA colors as the "palette index"

Tiles in `assets/tiles/atlas.png` are painted with the **actual original 16 EGA RGB values** (#000000, #0000AA, #00AA00, ...). When you open the atlas in Aseprite, GIMP, or Photoshop, you see real recognizable colors — blue water, green grass, gray stone — and you can edit them like any normal pixel-art file. Use `assets/tiles/ega_palette.png` as a reference swatch in your editor.

At runtime, the **palette-swap shader** (`assets/shaders/palette_swap.gdshader`) takes each rendered pixel, finds the closest EGA reference color (16 distance comparisons), and looks up the corresponding color in the **active per-map palette**. So:

- The "WorldDay" palette **is** the EGA palette → tiles render unchanged.
- The "Dungeon" palette swaps cool stone-grays for the EGA values → same tiles, different mood.
- The "Fire" palette swaps hot reds and oranges → walking into a burning town would look that way.

Switching maps simply swaps a 16x1 palette texture as a shader uniform. **No tile graphics ever change.**

### 2. Map types and structure

- `MapKind.World` — overworld (~64×64), generated with smoothed value noise. Towns appear on grass; dungeon entrances appear in mountains.
- `MapKind.Town` — fenced 32×32 area with rectangular buildings, paths, a south gate. Each building has a door.
- `MapKind.Dungeon` — 32×32 stone level with rooms and L-shaped corridors. Stairs-up returns to the world.
- `MapKind.Interior` — 12×10 building interior with furniture and an NPC. South door returns to the town.

Maps are pre-generated at startup and held in memory (35–40 maps total, well under 1 MB). Transitions between maps fire when stepping onto a transition tile (town, dungeon, door, stairs).

---

## Prerequisites

- **Godot 4.3+ with Mono / .NET support**.  
  Download from <https://godotengine.org/download> — the **".NET" build**, not the GDScript-only build.
- **.NET 8 SDK**.  
  Download from <https://dotnet.microsoft.com/download>.

Optional but recommended:

- **VS Code** with extensions **Godot Tools** (`geequlim.godot-tools`) and **C# Dev Kit** (`ms-dotnettools.csdevkit`).
- **JetBrains Rider** with the bundled Godot support plugin.
- **Python 3 + Pillow** if you want to regenerate the tile atlas from `tools/generate_tiles.py`.

---

## First-time setup

The very first time you open the project, **let Godot create the build files**:

1. Launch the Godot editor (.NET build).
2. **Import** → pick the `project.godot` in this folder.
3. Godot will create the `.godot/` cache. Close it.
4. From this folder, run `dotnet build`. This produces `.godot/mono/temp/bin/...` artifacts that Godot needs.

After that, you can iterate entirely from VS Code or Rider.

---

## Building and running from VS Code

1. Open this folder in VS Code.
2. Install the recommended extensions when prompted.
3. Configure the Godot binary in **Settings → Extensions → Godot Tools → Editor Path** (point at your `Godot_v4.3_mono` executable).
4. Run **Ctrl+Shift+B** (or *Tasks: Run Build Task*) to build the C# project.
5. Press **F5** to launch via the godot-mono debugger.

The included `tasks.json` also has a **regenerate tiles** task that re-runs `tools/generate_tiles.py`.

## Building and running from JetBrains Rider

1. Open `UltimaLikeRoguelike.sln` in Rider.
2. Open **Settings → Languages & Frameworks → Godot Engine** and set the Godot executable.
3. Hit **Build** and then run via Rider's Godot configuration.

---

## Controls

| Action | Keyboard | Touch |
|---|---|---|
| Move N/S/E/W | Arrow keys or WASD | On-screen ↑ ↓ ← → buttons |
| Turn in place | Walk into a wall | Tap toward the wall |

Step onto a town, dungeon entrance, or door to enter that map. Step onto the stairs / south door / town gate to leave.

The status bar at the top shows the current map name and your position.

---

## Project layout

```
UltimaLikeRoguelike/
├── project.godot                   Godot project descriptor
├── UltimaLikeRoguelike.csproj      C# project (net8.0, Godot.NET.Sdk 4.3.0)
├── UltimaLikeRoguelike.sln         Solution file (for Rider / VS)
├── icon.svg                        Project icon
├── README.md                       This file
├── assets/
│   ├── tiles/
│   │   ├── atlas.png               128x128 atlas, 8x8 tiles, EGA-painted
│   │   └── ega_palette.png         Reference swatch for editing
│   └── shaders/
│       └── palette_swap.gdshader   Color-match → palette lookup
├── scenes/
│   └── Main.tscn                   Trivial root scene; everything in code
├── scripts/
│   ├── Core/
│   │   ├── TileId.cs               Atlas tile id constants
│   │   ├── TileDefinition.cs       Per-tile properties + TileDatabase
│   │   ├── Palette.cs              16-color palette + 16x1 ImageTexture
│   │   ├── PaletteDatabase.cs      Named palettes (WorldDay, Dungeon, ...)
│   │   └── MapData.cs              MapKind, MapTransition, MapData
│   ├── Generation/
│   │   ├── WorldGenerator.cs       Overworld via smoothed value noise
│   │   ├── TownGenerator.cs        Fenced town with buildings + paths
│   │   ├── DungeonGenerator.cs     Rooms + L-shaped corridors
│   │   └── InteriorGenerator.cs    Single-room building interior
│   ├── View/
│   │   └── MapRenderer.cs          Custom Node2D._Draw of visible region
│   └── Game/
│       ├── Player.cs               Position + facing
│       └── Main.cs                 Orchestrator: world build, input, transitions
└── tools/
	└── generate_tiles.py           Builds atlas.png from ASCII tile art
```

---

## Editing tiles

1. Open `assets/tiles/atlas.png` in your image editor.
2. Load `assets/tiles/ega_palette.png` as a reference swatch — those are the only 16 colors you should paint with.
3. Save. Godot will reimport on next launch.

> **Stay within the 16 EGA colors.** The shader matches each pixel to the closest EGA color to find its index. Off-palette pixels will snap to the nearest match, which might not be what you wanted.

If you'd rather edit the ASCII tile art and regenerate:

```sh
python3 tools/generate_tiles.py
```

Each tile is 16 strings of 16 characters. `'0'`–`'9'`, `'a'`–`'f'` are the EGA palette indices; `'.'` is transparent. The `t()` helper in `tools/generate_tiles.py` asserts every row is exactly 16 characters wide so width drift fails loudly.

---

## Adding a new mood palette

Edit `scripts/Core/PaletteDatabase.cs`:

```csharp
Add("UnderwaterMoonlight", new[]
{
    Hex("#000000"), Hex("#001020"), Hex("#103060"), Hex("#1a4a78"),
    // ... 12 more
});
```

Then assign that name to a map's `PaletteName` (e.g. in a generator) and it will be used the next time the player enters that map.

---

## Why custom drawing instead of TileMapLayer?

The renderer in `scripts/View/MapRenderer.cs` overrides `_Draw()` and draws the visible 11×14-tile region with `DrawTextureRectRegion` calls. This avoids configuring TileMapLayer atlases and gives complete control over per-frame redraw, which is fine for a turn-based roguelike that only redraws when the player moves or the palette changes.

The shader is applied as a single `ShaderMaterial` on the `MapRenderer` node, so every drawn tile (including the player overlay) is recolored by whatever palette texture is currently set as the `palette` uniform.
