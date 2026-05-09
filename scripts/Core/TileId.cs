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

    // Rows 6..12 - per-biome tilesets. Each biome gets one row of 8
    // tiles in this fixed order: Coast, Ground, Vegetation, Hill, Peak,
    // Tree, Bush, Rock. So tile id of biome B's role R is
    // 48 + 8*B + R for B in 0..6 and R in 0..7. The constants below are
    // the same indices spelled out for readability.

    // Row 6 - Plains biome
    public const int PlainsCoast        = 48;
    public const int PlainsGround       = 49;
    public const int PlainsVegetation   = 50;
    public const int PlainsHill         = 51;
    public const int PlainsPeak         = 52;
    public const int PlainsTree         = 53;
    public const int PlainsBush         = 54;
    public const int PlainsRock         = 55;

    // Row 7 - Desert biome
    public const int DesertCoast        = 56;
    public const int DesertGround       = 57;
    public const int DesertVegetation   = 58;
    public const int DesertHill         = 59;
    public const int DesertPeak         = 60;
    public const int DesertTree         = 61;
    public const int DesertBush         = 62;
    public const int DesertRock         = 63;

    // Row 8 - Forest biome
    public const int ForestCoast        = 64;
    public const int ForestGround       = 65;
    public const int ForestVegetation   = 66;
    public const int ForestHill         = 67;
    public const int ForestPeak         = 68;
    public const int ForestTree         = 69;
    public const int ForestBush         = 70;
    public const int ForestRock         = 71;

    // Row 9 - Deep Forest biome
    public const int DeepForestCoast        = 72;
    public const int DeepForestGround       = 73;
    public const int DeepForestVegetation   = 74;
    public const int DeepForestHill         = 75;
    public const int DeepForestPeak         = 76;
    public const int DeepForestTree         = 77;
    public const int DeepForestBush         = 78;
    public const int DeepForestRock         = 79;

    // Row 10 - Icy Tundra biome
    public const int TundraCoast        = 80;
    public const int TundraGround       = 81;
    public const int TundraVegetation   = 82;
    public const int TundraHill         = 83;
    public const int TundraPeak         = 84;
    public const int TundraTree         = 85;
    public const int TundraBush         = 86;
    public const int TundraRock         = 87;

    // Row 11 - Volcanic biome
    public const int VolcanicCoast      = 88;
    public const int VolcanicGround     = 89;
    public const int VolcanicVegetation = 90;
    public const int VolcanicHill       = 91;
    public const int VolcanicPeak       = 92;
    public const int VolcanicTree       = 93;
    public const int VolcanicBush       = 94;
    public const int VolcanicRock       = 95;

    // Row 12 - Mountains biome
    public const int MountainsCoast        = 96;
    public const int MountainsGround       = 97;
    public const int MountainsVegetation   = 98;
    public const int MountainsHill         = 99;
    public const int MountainsPeak         = 100;
    public const int MountainsTree         = 101;
    public const int MountainsBush         = 102;
    public const int MountainsRock         = 103;

    // Rows 13..19 - per-biome town tilesets. Each biome gets one row of
    // 8 town tiles in this fixed order: Floor, Wall, WindowWall,
    // DoorClosed, DoorOpen, Bed, Table, Chair. So tile id of biome B's
    // town role R is 104 + 8*B + R.

    // Row 13 - Plains town
    public const int PlainsTownFloor       = 104;
    public const int PlainsTownWall        = 105;
    public const int PlainsTownWindowWall  = 106;
    public const int PlainsTownDoorClosed  = 107;
    public const int PlainsTownDoorOpen    = 108;
    public const int PlainsTownBed         = 109;
    public const int PlainsTownTable       = 110;
    public const int PlainsTownChair       = 111;

    // Row 14 - Desert town
    public const int DesertTownFloor       = 112;
    public const int DesertTownWall        = 113;
    public const int DesertTownWindowWall  = 114;
    public const int DesertTownDoorClosed  = 115;
    public const int DesertTownDoorOpen    = 116;
    public const int DesertTownBed         = 117;
    public const int DesertTownTable       = 118;
    public const int DesertTownChair       = 119;

    // Row 15 - Forest town
    public const int ForestTownFloor       = 120;
    public const int ForestTownWall        = 121;
    public const int ForestTownWindowWall  = 122;
    public const int ForestTownDoorClosed  = 123;
    public const int ForestTownDoorOpen    = 124;
    public const int ForestTownBed         = 125;
    public const int ForestTownTable       = 126;
    public const int ForestTownChair       = 127;

    // Row 16 - Deep Forest town
    public const int DeepForestTownFloor       = 128;
    public const int DeepForestTownWall        = 129;
    public const int DeepForestTownWindowWall  = 130;
    public const int DeepForestTownDoorClosed  = 131;
    public const int DeepForestTownDoorOpen    = 132;
    public const int DeepForestTownBed         = 133;
    public const int DeepForestTownTable       = 134;
    public const int DeepForestTownChair       = 135;

    // Row 17 - Icy Tundra town
    public const int TundraTownFloor       = 136;
    public const int TundraTownWall        = 137;
    public const int TundraTownWindowWall  = 138;
    public const int TundraTownDoorClosed  = 139;
    public const int TundraTownDoorOpen    = 140;
    public const int TundraTownBed         = 141;
    public const int TundraTownTable       = 142;
    public const int TundraTownChair       = 143;

    // Row 18 - Volcanic town
    public const int VolcanicTownFloor       = 144;
    public const int VolcanicTownWall        = 145;
    public const int VolcanicTownWindowWall  = 146;
    public const int VolcanicTownDoorClosed  = 147;
    public const int VolcanicTownDoorOpen    = 148;
    public const int VolcanicTownBed         = 149;
    public const int VolcanicTownTable       = 150;
    public const int VolcanicTownChair       = 151;

    // Row 19 - Mountains town
    public const int MountainsTownFloor       = 152;
    public const int MountainsTownWall        = 153;
    public const int MountainsTownWindowWall  = 154;
    public const int MountainsTownDoorClosed  = 155;
    public const int MountainsTownDoorOpen    = 156;
    public const int MountainsTownBed         = 157;
    public const int MountainsTownTable       = 158;
    public const int MountainsTownChair       = 159;
}
