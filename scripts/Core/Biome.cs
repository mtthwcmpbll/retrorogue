namespace UltimaLikeRoguelike.Core;

/// <summary>
/// A biome's complete tileset: the world generator picks a biome per cell
/// and asks it for the right tile id given the cell's elevation band
/// (Coast / Ground / Vegetation / Hill / Peak) plus probabilistic
/// decoration tiles (Tree / Bush / Rock) sprinkled on top of the Ground.
/// <para/>
/// Each biome owns a contiguous row in the atlas, so swapping biomes
/// gives every tile (ground, trees, rocks, hills, peaks) a distinct
/// look.
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
    float RockChance
);
