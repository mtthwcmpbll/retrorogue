using System.Collections.Generic;

namespace UltimaLikeRoguelike.Core;

/// <summary>
/// Registry of named biomes used by the world generator. Each biome
/// brings its own tileset (coast, ground, vegetation, hill, peak, tree,
/// bush, rock), so a region's biome determines what every tile in that
/// region looks like.
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
            Coast:        TileId.PlainsCoast,
            Ground:       TileId.PlainsGround,
            Vegetation:   TileId.PlainsVegetation,
            Hill:         TileId.PlainsHill,
            Peak:         TileId.PlainsPeak,
            Tree:         TileId.PlainsTree,
            Bush:         TileId.PlainsBush,
            Rock:         TileId.PlainsRock,
            TreeChance:   0.04f,
            BushChance:   0.03f,
            RockChance:   0.01f
        ));

        Add(new Biome(
            Name:         Desert,
            Coast:        TileId.DesertCoast,
            Ground:       TileId.DesertGround,
            Vegetation:   TileId.DesertVegetation,
            Hill:         TileId.DesertHill,
            Peak:         TileId.DesertPeak,
            Tree:         TileId.DesertTree,
            Bush:         TileId.DesertBush,
            Rock:         TileId.DesertRock,
            TreeChance:   0.04f,
            BushChance:   0.03f,
            RockChance:   0.04f
        ));

        Add(new Biome(
            Name:         Forest,
            Coast:        TileId.ForestCoast,
            Ground:       TileId.ForestGround,
            Vegetation:   TileId.ForestVegetation,
            Hill:         TileId.ForestHill,
            Peak:         TileId.ForestPeak,
            Tree:         TileId.ForestTree,
            Bush:         TileId.ForestBush,
            Rock:         TileId.ForestRock,
            TreeChance:   0.18f,
            BushChance:   0.06f,
            RockChance:   0.02f
        ));

        Add(new Biome(
            Name:         DeepForest,
            Coast:        TileId.DeepForestCoast,
            Ground:       TileId.DeepForestGround,
            Vegetation:   TileId.DeepForestVegetation,
            Hill:         TileId.DeepForestHill,
            Peak:         TileId.DeepForestPeak,
            Tree:         TileId.DeepForestTree,
            Bush:         TileId.DeepForestBush,
            Rock:         TileId.DeepForestRock,
            TreeChance:   0.32f,
            BushChance:   0.08f,
            RockChance:   0.02f
        ));

        Add(new Biome(
            Name:         IcyTundra,
            Coast:        TileId.TundraCoast,
            Ground:       TileId.TundraGround,
            Vegetation:   TileId.TundraVegetation,
            Hill:         TileId.TundraHill,
            Peak:         TileId.TundraPeak,
            Tree:         TileId.TundraTree,
            Bush:         TileId.TundraBush,
            Rock:         TileId.TundraRock,
            TreeChance:   0.05f,
            BushChance:   0.02f,
            RockChance:   0.03f
        ));

        Add(new Biome(
            Name:         Volcanic,
            Coast:        TileId.VolcanicCoast,
            Ground:       TileId.VolcanicGround,
            Vegetation:   TileId.VolcanicVegetation,
            Hill:         TileId.VolcanicHill,
            Peak:         TileId.VolcanicPeak,
            Tree:         TileId.VolcanicTree,
            Bush:         TileId.VolcanicBush,
            Rock:         TileId.VolcanicRock,
            TreeChance:   0.06f,
            BushChance:   0.04f,
            RockChance:   0.06f
        ));

        Add(new Biome(
            Name:         Mountains,
            Coast:        TileId.MountainsCoast,
            Ground:       TileId.MountainsGround,
            Vegetation:   TileId.MountainsVegetation,
            Hill:         TileId.MountainsHill,
            Peak:         TileId.MountainsPeak,
            Tree:         TileId.MountainsTree,
            Bush:         TileId.MountainsBush,
            Rock:         TileId.MountainsRock,
            TreeChance:   0.05f,
            BushChance:   0.04f,
            RockChance:   0.08f
        ));
    }

    private static void Add(Biome b) => _biomes[b.Name] = b;

    public static Biome Get(string name)
        => _biomes.TryGetValue(name, out var b) ? b : _biomes[Plains];

    /// <summary>All biome names in registration order.</summary>
    public static IReadOnlyCollection<string> Names => _biomes.Keys;
}
