using System.Collections.Generic;

namespace UltimaLikeRoguelike.Core;

/// <summary>
/// Per-tile properties used by movement and interaction logic.
/// Visual appearance lives entirely in the atlas + shader.
/// </summary>
public sealed record TileDefinition(
    int Id,
    string Name,
    bool Passable,
    bool IsTransition
);

/// <summary>
/// Static registry of tile definitions, keyed by tile id.
/// </summary>
public static class TileDatabase
{
    private static readonly Dictionary<int, TileDefinition> _defs = new();

    static TileDatabase()
    {
        // Helpers
        TileDefinition Def(int id, string name, bool passable, bool isTransition = false)
            => new(id, name, passable, isTransition);

        // Row 0 - terrain
        Add(Def(TileId.Void,         "void",          passable: false));
        Add(Def(TileId.DeepWater,    "deep water",    passable: false));
        Add(Def(TileId.ShallowWater, "shallow water", passable: false));
        Add(Def(TileId.Sand,         "sand",          passable: true));
        Add(Def(TileId.Grass,        "grass",         passable: true));
        Add(Def(TileId.Forest,       "forest",        passable: true));
        Add(Def(TileId.Hills,        "hills",         passable: true));
        Add(Def(TileId.Mountains,    "mountains",     passable: false));

        // Row 1 - structures
        Add(Def(TileId.Swamp,        "swamp",         passable: true));
        Add(Def(TileId.Town,         "town",          passable: true,  isTransition: true));
        Add(Def(TileId.Castle,       "castle",        passable: true,  isTransition: true));
        Add(Def(TileId.Dungeon,      "dungeon",       passable: true,  isTransition: true));
        Add(Def(TileId.BridgeH,      "bridge",        passable: true));
        Add(Def(TileId.BridgeV,      "bridge",        passable: true));
        Add(Def(TileId.Path,         "path",          passable: true));
        Add(Def(TileId.Signpost,     "signpost",      passable: false));

        // Row 2 - detail
        Add(Def(TileId.Tree,         "tree",          passable: false));
        Add(Def(TileId.Bush,         "bush",          passable: true));
        Add(Def(TileId.Rock,         "rock",          passable: false));
        Add(Def(TileId.Well,         "well",          passable: false));
        Add(Def(TileId.FenceH,       "fence",         passable: false));
        Add(Def(TileId.FenceV,       "fence",         passable: false));
        Add(Def(TileId.StairsUp,     "stairs up",     passable: true,  isTransition: true));
        Add(Def(TileId.StairsDown,   "stairs down",   passable: true,  isTransition: true));

        // Row 3 - floors and walls
        Add(Def(TileId.StoneFloor,   "stone floor",   passable: true));
        Add(Def(TileId.WoodFloor,    "wood floor",    passable: true));
        Add(Def(TileId.BrickFloor,   "brick floor",   passable: true));
        Add(Def(TileId.GrassFloor,   "grass",         passable: true));
        Add(Def(TileId.StoneWall,    "stone wall",    passable: false));
        Add(Def(TileId.WoodWall,     "wood wall",     passable: false));
        Add(Def(TileId.BrickWall,    "brick wall",    passable: false));
        Add(Def(TileId.WindowWall,   "window wall",   passable: false));

        // Row 4 - furniture
        Add(Def(TileId.DoorClosed,   "door",          passable: true,  isTransition: true));
        Add(Def(TileId.DoorOpen,     "open door",     passable: true,  isTransition: true));
        Add(Def(TileId.Bed,          "bed",           passable: false));
        Add(Def(TileId.Table,        "table",         passable: false));
        Add(Def(TileId.Chair,        "chair",         passable: false));
        Add(Def(TileId.Counter,      "counter",       passable: false));
        Add(Def(TileId.Chest,        "chest",         passable: false));
        Add(Def(TileId.Barrel,       "barrel",        passable: false));

        // Per-biome tilesets. Coasts/Grounds/Vegetations/Hills are
        // passable; Peaks (mountain peaks, lava) and Trees/Bushes/Rocks
        // block movement. Order matches TileId rows 6..12.

        // Plains
        Add(Def(TileId.PlainsCoast,         "shore",         passable: true));
        Add(Def(TileId.PlainsGround,        "grass",         passable: true));
        Add(Def(TileId.PlainsVegetation,    "tall grass",    passable: true));
        Add(Def(TileId.PlainsHill,          "hill",          passable: true));
        Add(Def(TileId.PlainsPeak,          "mountain",      passable: false));
        Add(Def(TileId.PlainsTree,          "oak",           passable: false));
        Add(Def(TileId.PlainsBush,          "bush",          passable: false));
        Add(Def(TileId.PlainsRock,          "rock",          passable: false));

        // Desert
        Add(Def(TileId.DesertCoast,         "sand",          passable: true));
        Add(Def(TileId.DesertGround,        "cracked sand",  passable: true));
        Add(Def(TileId.DesertVegetation,    "dune",          passable: true));
        Add(Def(TileId.DesertHill,          "mesa",          passable: true));
        Add(Def(TileId.DesertPeak,          "sandstone peak",passable: false));
        Add(Def(TileId.DesertTree,          "cactus",        passable: false));
        Add(Def(TileId.DesertBush,          "tumbleweed",    passable: false));
        Add(Def(TileId.DesertRock,          "sandstone",     passable: false));

        // Forest
        Add(Def(TileId.ForestCoast,         "mossy shore",   passable: true));
        Add(Def(TileId.ForestGround,        "moss",          passable: true));
        Add(Def(TileId.ForestVegetation,    "undergrowth",   passable: true));
        Add(Def(TileId.ForestHill,          "wooded hill",   passable: true));
        Add(Def(TileId.ForestPeak,          "wooded peak",   passable: false));
        Add(Def(TileId.ForestTree,          "tree",          passable: false));
        Add(Def(TileId.ForestBush,          "berry bush",    passable: false));
        Add(Def(TileId.ForestRock,          "mossy rock",    passable: false));

        // Deep Forest
        Add(Def(TileId.DeepForestCoast,     "peat shore",    passable: true));
        Add(Def(TileId.DeepForestGround,    "shadow floor",  passable: true));
        Add(Def(TileId.DeepForestVegetation,"dense canopy",  passable: true));
        Add(Def(TileId.DeepForestHill,      "pine slope",    passable: true));
        Add(Def(TileId.DeepForestPeak,      "pine peak",     passable: false));
        Add(Def(TileId.DeepForestTree,      "pine",          passable: false));
        Add(Def(TileId.DeepForestBush,      "fern",          passable: false));
        Add(Def(TileId.DeepForestRock,      "boulder",       passable: false));

        // Icy Tundra
        Add(Def(TileId.TundraCoast,         "icy shore",     passable: true));
        Add(Def(TileId.TundraGround,        "snow",          passable: true));
        Add(Def(TileId.TundraVegetation,    "ice patch",     passable: true));
        Add(Def(TileId.TundraHill,          "snow hill",     passable: true));
        Add(Def(TileId.TundraPeak,          "icy peak",      passable: false));
        Add(Def(TileId.TundraTree,          "snowy pine",    passable: false));
        Add(Def(TileId.TundraBush,          "frost shrub",   passable: false));
        Add(Def(TileId.TundraRock,          "ice rock",      passable: false));

        // Volcanic
        Add(Def(TileId.VolcanicCoast,       "ash shore",     passable: true));
        Add(Def(TileId.VolcanicGround,      "ash",           passable: true));
        Add(Def(TileId.VolcanicVegetation,  "lava cracks",   passable: true));
        Add(Def(TileId.VolcanicHill,        "lava field",    passable: true));
        Add(Def(TileId.VolcanicPeak,        "lava peak",     passable: false));
        Add(Def(TileId.VolcanicTree,        "dead tree",     passable: false));
        Add(Def(TileId.VolcanicBush,        "charred bush",  passable: false));
        Add(Def(TileId.VolcanicRock,        "obsidian",      passable: false));

        // Mountains
        Add(Def(TileId.MountainsCoast,      "rocky shore",   passable: true));
        Add(Def(TileId.MountainsGround,     "rocky ground",  passable: true));
        Add(Def(TileId.MountainsVegetation, "alpine grass",  passable: true));
        Add(Def(TileId.MountainsHill,       "ridge",         passable: true));
        Add(Def(TileId.MountainsPeak,       "snowy peak",    passable: false));
        Add(Def(TileId.MountainsTree,       "alpine pine",   passable: false));
        Add(Def(TileId.MountainsBush,       "alpine shrub",  passable: false));
        Add(Def(TileId.MountainsRock,       "boulder",       passable: false));

        // Per-biome town tilesets. Floors are passable, walls/windows
        // block movement, doors are passable transitions, beds/tables/
        // chairs block movement. Order matches TileId rows 13..19.

        AddTownSet(TileId.PlainsTownFloor);
        AddTownSet(TileId.DesertTownFloor);
        AddTownSet(TileId.ForestTownFloor);
        AddTownSet(TileId.DeepForestTownFloor);
        AddTownSet(TileId.TundraTownFloor);
        AddTownSet(TileId.VolcanicTownFloor);
        AddTownSet(TileId.MountainsTownFloor);
    }

    /// <summary>
    /// Register a biome's 8-tile town set in the canonical order
    /// starting at <paramref name="floorId"/>: Floor, Wall, WindowWall,
    /// DoorClosed, DoorOpen, Bed, Table, Chair.
    /// </summary>
    private static void AddTownSet(int floorId)
    {
        TileDefinition Def(int id, string name, bool passable, bool isTransition = false)
            => new(id, name, passable, isTransition);

        Add(Def(floorId + 0, "floor",       passable: true));
        Add(Def(floorId + 1, "wall",        passable: false));
        Add(Def(floorId + 2, "window wall", passable: false));
        Add(Def(floorId + 3, "door",        passable: true,  isTransition: true));
        Add(Def(floorId + 4, "open door",   passable: true,  isTransition: true));
        Add(Def(floorId + 5, "bed",         passable: false));
        Add(Def(floorId + 6, "table",       passable: false));
        Add(Def(floorId + 7, "chair",       passable: false));
    }

    private static void Add(TileDefinition def) => _defs[def.Id] = def;

    public static TileDefinition Get(int id)
        => _defs.TryGetValue(id, out var def)
            ? def
            : new TileDefinition(id, $"unknown:{id}", false, false);

    public static bool IsPassable(int id) => Get(id).Passable;
    public static bool IsTransition(int id) => Get(id).IsTransition;
}
