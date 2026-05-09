using System.Collections.Generic;

namespace UltimaLikeRoguelike.Core;

/// <summary>
/// Registry of named biomes used by the world generator. Each biome maps
/// the elevation bands (coast/ground/vegetation/highland/peak) to specific
/// tile ids, so a single elevation field can render as desert, tundra,
/// volcanic, or temperate terrain depending on which biome region the
/// cell falls into.
/// </summary>
public static class BiomeDatabase
{
    private static readonly Dictionary<string, Biome> _biomes = new();

    public const string Plains      = "Plains";
    public const string Desert      = "Desert";
    public const string Forest      = "Forest";
    public const string DeepForest  = "DeepForest";
    public const string IcyTundra   = "IcyTundra";
    public const string Volcanic    = "Volcanic";
    public const string Mountains   = "Mountains";

    static BiomeDatabase()
    {
        Add(new Biome(
            Name:         Plains,
            Coast:        TileId.Sand,
            Ground:       TileId.Grass,
            Vegetation:   TileId.Forest,
            Highland:     TileId.Hills,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.Tree,
            DecorAlt:     TileId.Bush,
            DecorChance:  0.04f
        ));

        Add(new Biome(
            Name:         Desert,
            Coast:        TileId.Sand,
            Ground:       TileId.DesertSand,
            Vegetation:   TileId.SandDune,
            Highland:     TileId.Hills,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.Cactus,
            DecorAlt:     TileId.Rock,
            DecorChance:  0.06f
        ));

        Add(new Biome(
            Name:         Forest,
            Coast:        TileId.Sand,
            Ground:       TileId.Grass,
            Vegetation:   TileId.Forest,
            Highland:     TileId.Forest,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.Tree,
            DecorAlt:     TileId.Bush,
            DecorChance:  0.18f
        ));

        Add(new Biome(
            Name:         DeepForest,
            Coast:        TileId.Grass,
            Ground:       TileId.Forest,
            Vegetation:   TileId.DenseForest,
            Highland:     TileId.DenseForest,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.PineTree,
            DecorAlt:     TileId.Tree,
            DecorChance:  0.30f
        ));

        Add(new Biome(
            Name:         IcyTundra,
            Coast:        TileId.SnowGround,
            Ground:       TileId.SnowGround,
            Vegetation:   TileId.SnowGround,
            Highland:     TileId.IcePatch,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.SnowyPine,
            DecorAlt:     TileId.IcePatch,
            DecorChance:  0.07f
        ));

        Add(new Biome(
            Name:         Volcanic,
            Coast:        TileId.AshGround,
            Ground:       TileId.AshGround,
            Vegetation:   TileId.VolcanicRock,
            Highland:     TileId.VolcanicRock,
            Peak:         TileId.Lava,
            DecorTree:    TileId.DeadTree,
            DecorAlt:     TileId.Rock,
            DecorChance:  0.10f
        ));

        Add(new Biome(
            Name:         Mountains,
            Coast:        TileId.Sand,
            Ground:       TileId.Hills,
            Vegetation:   TileId.Hills,
            Highland:     TileId.Mountains,
            Peak:         TileId.Mountains,
            DecorTree:    TileId.Rock,
            DecorAlt:     TileId.Tree,
            DecorChance:  0.08f
        ));
    }

    private static void Add(Biome b) => _biomes[b.Name] = b;

    public static Biome Get(string name)
        => _biomes.TryGetValue(name, out var b) ? b : _biomes[Plains];

    /// <summary>All biome names in registration order.</summary>
    public static IReadOnlyCollection<string> Names => _biomes.Keys;
}
