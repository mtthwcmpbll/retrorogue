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
    }

    private static void Add(TileDefinition def) => _defs[def.Id] = def;

    public static TileDefinition Get(int id)
        => _defs.TryGetValue(id, out var def)
            ? def
            : new TileDefinition(id, $"unknown:{id}", false, false);

    public static bool IsPassable(int id) => Get(id).Passable;
    public static bool IsTransition(int id) => Get(id).IsTransition;
}
