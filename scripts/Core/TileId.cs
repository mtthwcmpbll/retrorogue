namespace UltimaLikeRoguelike.Core;

/// <summary>
/// Tile IDs in the atlas. The atlas is 8 columns x 8 rows of 16x16 tiles.
/// Tile id = row * 8 + col. Keep this in sync with tools/generate_tiles.py.
/// </summary>
public static class TileId
{
    // Row 0 - terrain
    public const int Void           = 0;
    public const int DeepWater      = 1;
    public const int ShallowWater   = 2;
    public const int Sand           = 3;
    public const int Grass          = 4;
    public const int Forest         = 5;
    public const int Hills          = 6;
    public const int Mountains      = 7;

    // Row 1 - structures
    public const int Swamp          = 8;
    public const int Town           = 9;
    public const int Castle         = 10;
    public const int Dungeon        = 11;
    public const int BridgeH        = 12;
    public const int BridgeV        = 13;
    public const int Path           = 14;
    public const int Signpost       = 15;

    // Row 2 - world detail / interactive
    public const int Tree           = 16;
    public const int Bush           = 17;
    public const int Rock           = 18;
    public const int Well           = 19;
    public const int FenceH         = 20;
    public const int FenceV         = 21;
    public const int StairsUp       = 22;
    public const int StairsDown     = 23;

    // Row 3 - floors and walls
    public const int StoneFloor     = 24;
    public const int WoodFloor      = 25;
    public const int BrickFloor     = 26;
    public const int GrassFloor     = 27;
    public const int StoneWall      = 28;
    public const int WoodWall       = 29;
    public const int BrickWall      = 30;
    public const int WindowWall     = 31;

    // Row 4 - furniture
    public const int DoorClosed     = 32;
    public const int DoorOpen       = 33;
    public const int Bed            = 34;
    public const int Table          = 35;
    public const int Chair          = 36;
    public const int Counter        = 37;
    public const int Chest          = 38;
    public const int Barrel         = 39;

    // Row 5 - characters
    public const int PlayerSouth    = 40;
    public const int PlayerNorth    = 41;
    public const int PlayerEast     = 42;
    public const int PlayerWest     = 43;
    public const int Merchant       = 44;
    public const int Peasant        = 45;
    public const int Guard          = 46;
    public const int Innkeeper      = 47;

    // Row 6 - biome terrain
    public const int DesertSand     = 48;
    public const int Cactus         = 49;
    public const int SnowGround     = 50;
    public const int IcePatch       = 51;
    public const int PineTree       = 52;
    public const int DeadTree       = 53;
    public const int AshGround      = 54;
    public const int Lava           = 55;

    // Row 7 - biome detail
    public const int VolcanicRock   = 56;
    public const int DenseForest    = 57;
    public const int SnowyPine      = 58;
    public const int SandDune       = 59;
}
