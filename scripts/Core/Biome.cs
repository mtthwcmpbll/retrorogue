namespace UltimaLikeRoguelike.Core;

/// <summary>
/// A biome's "tile atlas": a mapping from logical terrain roles (coast,
/// ground, vegetation, highland, peak) to specific tile ids. The world
/// generator picks a biome per cell and then translates the cell's
/// elevation into one of these slots, so the same elevation noise can
/// produce snow, ash, sand, or grass depending on the local biome.
/// <para/>
/// <see cref="DecorTree"/> and <see cref="DecorAlt"/> are sprinkled on top
/// of <see cref="Ground"/> tiles to add visual variety: e.g. cacti on
/// desert sand, pines in deep forest, bare rocks in volcanic flats.
/// </summary>
public sealed record Biome(
    string Name,
    int Coast,
    int Ground,
    int Vegetation,
    int Highland,
    int Peak,
    int DecorTree,
    int DecorAlt,
    float DecorChance
);
