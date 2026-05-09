namespace UltimaLikeRoguelike.Core;

/// <summary>
/// A biome's complete tileset for both world map and town/interior maps.
/// The world generator picks a biome per cell and asks it for the right
/// tile id given the cell's elevation band (Coast/Ground/Vegetation/
/// Hill/Peak), plus probabilistic decoration tiles (Tree/Bush/Rock).
/// <para/>
/// The town/interior generators receive a biome and use its
/// TownFloor/TownWall/TownWindowWall/TownDoorClosed/TownDoorOpen/
/// TownBed/TownTable/TownChair tiles, so a town in the volcanic biome
/// is built from obsidian and lava-veined stone, while a tundra town
/// is ice blocks and fur bedding.
/// </summary>
public sealed record Biome(
    string Name,
    int Coast,
    int Ground,
    int Vegetation,
    int Hill,
    int Peak,
    int Tree,
    int Bush,
    int Rock,
    float TreeChance,
    float BushChance,
    float RockChance,
    int TownFloor,
    int TownWall,
    int TownWindowWall,
    int TownDoorClosed,
    int TownDoorOpen,
    int TownBed,
    int TownTable,
    int TownChair
);
