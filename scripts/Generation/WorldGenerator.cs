using System;
using System.Collections.Generic;
using UltimaLikeRoguelike.Core;

namespace UltimaLikeRoguelike.Generation;

/// <summary>
/// Produces a random overworld map. Embeds transitions for towns and
/// dungeons; their target map ids resolve to maps generated lazily by the
/// other generators when first entered.
/// <para/>
/// The map is split into biome regions via Voronoi-style scattering, and
/// the borders between regions are softened by per-cell probabilistic
/// blending: cells near a boundary occasionally pick the runner-up
/// biome's tile, so a forest fades into plains instead of stopping at a
/// hard edge. Each cell's elevation is then translated through the
/// chosen biome's tileset (Coast/Ground/Vegetation/Hill/Peak), and
/// Ground tiles get sprinkled with biome-appropriate trees, bushes, and
/// rocks.
/// </summary>
public static class WorldGenerator
{
    public const int Width = 64;
    public const int Height = 64;

    private const int TownCount = 5;
    private const int DungeonCount = 3;

    // Number of biome "cells" (Voronoi sites) sprinkled across the map.
    // Each site claims its surrounding territory, producing irregular
    // biome regions of roughly Width*Height / BiomeSiteCount tiles each.
    private const int BiomeSiteCount = 9;

    public sealed record Result(
        MapData Map,
        IReadOnlyList<(int X, int Y, string MapId)> Towns,
        IReadOnlyList<(int X, int Y, string MapId)> Dungeons
    );

    public static Result Generate(int seed)
    {
        var rng = new Random(seed);
        var map = new MapData("world", MapKind.World, Width, Height, PaletteDatabase.WorldDay);

        // 1. Generate elevation field via simple smoothed value noise.
        float[] elevation = GenerateElevation(rng);

        // 2. Generate a biome field: each cell points at a Biome (with
        //    blended borders so transitions feather instead of cutting).
        Biome[] biomes = GenerateBiomeField(rng);

        // 3. Convert (elevation, biome) -> terrain tile.
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                float e = elevation[y * Width + x];
                Biome biome = biomes[y * Width + x];
                int tile = BiomeTileForElevation(biome, e);
                map.SetTile(x, y, tile);
            }
        }

        // 4. Sprinkle biome-appropriate decoration on Ground tiles.
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                Biome biome = biomes[y * Width + x];
                if (map.GetTile(x, y) != biome.Ground) continue;
                double r = rng.NextDouble();
                float treeT = biome.TreeChance;
                float bushT = treeT + biome.BushChance;
                float rockT = bushT + biome.RockChance;
                if (r < treeT) map.SetTile(x, y, biome.Tree);
                else if (r < bushT) map.SetTile(x, y, biome.Bush);
                else if (r < rockT) map.SetTile(x, y, biome.Rock);
            }
        }

        // 5. Place towns on grass, well-spaced.
        var towns = new List<(int X, int Y, string MapId)>();
        var occupied = new List<(int X, int Y)>();
        for (int i = 0; i < TownCount; i++)
        {
            if (TryFindSpot(map, rng, occupied, IsGoodTownSpot, minDistance: 10, out int tx, out int ty))
            {
                string mapId = $"town:{i}";
                map.SetTile(tx, ty, TileId.Town);
                map.Transitions[(tx, ty)] = new MapTransition(mapId);
                towns.Add((tx, ty, mapId));
                occupied.Add((tx, ty));
            }
        }

        // 6. Place dungeons in or near elevated rocky terrain.
        var dungeons = new List<(int X, int Y, string MapId)>();
        for (int i = 0; i < DungeonCount; i++)
        {
            if (TryFindSpot(map, rng, occupied, IsGoodDungeonSpot, minDistance: 8, out int dx, out int dy))
            {
                string mapId = $"dungeon:{i}";
                map.SetTile(dx, dy, TileId.Dungeon);
                map.Transitions[(dx, dy)] = new MapTransition(mapId);
                dungeons.Add((dx, dy, mapId));
                occupied.Add((dx, dy));
            }
        }

        // 7. Choose a player entry point: a passable tile near a town if
        //    possible, otherwise any passable tile.
        if (towns.Count > 0)
        {
            var (tx, ty, _) = towns[0];
            int ex = tx, ey = Math.Min(Height - 1, ty + 1);
            if (TileDatabase.IsPassable(map.GetTile(ex, ey)))
            {
                map.EntryX = ex;
                map.EntryY = ey;
            }
            else
            {
                map.EntryX = tx;
                map.EntryY = ty;
            }
        }
        else
        {
            FindAnyPassable(map, rng, out int ex, out int ey);
            map.EntryX = ex;
            map.EntryY = ey;
        }

        return new Result(map, towns, dungeons);
    }

    // -------- helpers --------------------------------------------------

    private static float[] GenerateElevation(Random rng)
    {
        // Generate a small random grid and bilinearly upsample to map size.
        // Then smooth a few passes for organic blobs.
        const int LowRes = 12;
        var low = new float[LowRes * LowRes];
        for (int i = 0; i < low.Length; i++)
            low[i] = (float)rng.NextDouble();

        var hi = new float[Width * Height];
        for (int y = 0; y < Height; y++)
        {
            float fy = (float)y / Height * (LowRes - 1);
            int y0 = (int)fy;
            int y1 = Math.Min(y0 + 1, LowRes - 1);
            float ty = fy - y0;
            for (int x = 0; x < Width; x++)
            {
                float fx = (float)x / Width * (LowRes - 1);
                int x0 = (int)fx;
                int x1 = Math.Min(x0 + 1, LowRes - 1);
                float tx = fx - x0;

                float a = low[y0 * LowRes + x0];
                float b = low[y0 * LowRes + x1];
                float c = low[y1 * LowRes + x0];
                float d = low[y1 * LowRes + x1];
                float ab = a + (b - a) * tx;
                float cd = c + (d - c) * tx;
                hi[y * Width + x] = ab + (cd - ab) * ty;
            }
        }

        // Pull edges down so the world is surrounded by water.
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                float dx = Math.Abs(x - Width / 2f) / (Width / 2f);
                float dy = Math.Abs(y - Height / 2f) / (Height / 2f);
                float dist = Math.Min(1f, MathF.Sqrt(dx * dx + dy * dy));
                hi[y * Width + x] *= 1f - 0.85f * MathF.Pow(dist, 3);
            }
        }

        // Smooth a couple of passes.
        for (int pass = 0; pass < 2; pass++)
            hi = Smooth(hi);

        return hi;
    }

    private static float[] Smooth(float[] src)
    {
        var dst = new float[src.Length];
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                float sum = 0;
                int count = 0;
                for (int dy = -1; dy <= 1; dy++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        int nx = x + dx, ny = y + dy;
                        if (nx < 0 || ny < 0 || nx >= Width || ny >= Height) continue;
                        sum += src[ny * Width + nx];
                        count++;
                    }
                }
                dst[y * Width + x] = sum / count;
            }
        }
        return dst;
    }

    /// <summary>
    /// Builds a per-cell biome assignment using Voronoi-style scattering
    /// of biome "sites" with feathered borders. Each cell normally falls
    /// to its closest site, but cells near a boundary (where the
    /// nearest two sites are roughly equidistant) probabilistically pick
    /// the runner-up biome instead. The result: large irregular biome
    /// regions whose borders have a wavy, blended transition zone
    /// rather than a hard polygon edge.
    /// <para/>
    /// The first site is pinned to <see cref="BiomeDatabase.Plains"/>
    /// so towns - which require grass - always have somewhere to land.
    /// </summary>
    private static Biome[] GenerateBiomeField(Random rng)
    {
        var biomeNames = new List<string>(BiomeDatabase.Names);

        var sites = new (int X, int Y, Biome Biome)[BiomeSiteCount];
        for (int i = 0; i < BiomeSiteCount; i++)
        {
            int sx = rng.Next(Width);
            int sy = rng.Next(Height);
            string name = i == 0
                ? BiomeDatabase.Plains
                : biomeNames[rng.Next(biomeNames.Count)];
            sites[i] = (sx, sy, BiomeDatabase.Get(name));
        }

        var field = new Biome[Width * Height];
        for (int y = 0; y < Height; y++)
        {
            for (int x = 0; x < Width; x++)
            {
                // Find the two closest sites for this cell.
                int best = 0, second = 0;
                int bestDist = int.MaxValue, secondDist = int.MaxValue;
                for (int i = 0; i < sites.Length; i++)
                {
                    int dx = sites[i].X - x;
                    int dy = sites[i].Y - y;
                    int d = dx * dx + dy * dy;
                    if (d < bestDist)
                    {
                        secondDist = bestDist; second = best;
                        bestDist = d; best = i;
                    }
                    else if (d < secondDist)
                    {
                        secondDist = d; second = i;
                    }
                }

                // Border feathering: when bestDist is close to secondDist
                // (we're near the boundary between two biomes), pick the
                // runner-up with probability that grows toward 0.5 at
                // the exact boundary and falls off quickly inside the
                // dominant biome's territory.
                Biome biome = sites[best].Biome;
                if (secondDist < int.MaxValue && bestDist > 0)
                {
                    float ratio = (float)bestDist / secondDist; // 0..1
                    // At boundary ratio ~ 1 -> swap probability ~ 0.5.
                    // Deep inside dominant ratio ~ 0 -> swap ~ 0.
                    float pSwap = 0.5f * ratio * ratio;
                    if (rng.NextDouble() < pSwap)
                        biome = sites[second].Biome;
                }
                field[y * Width + x] = biome;
            }
        }
        return field;
    }

    /// <summary>
    /// Translate elevation through a biome's tileset. Water is universal
    /// (every biome has shores). Above the waterline the biome supplies
    /// its own coast / ground / vegetation / hill / peak tiles.
    /// </summary>
    private static int BiomeTileForElevation(Biome biome, float e)
    {
        if (e < 0.20f) return TileId.DeepWater;
        if (e < 0.30f) return TileId.ShallowWater;
        if (e < 0.34f) return biome.Coast;
        if (e < 0.55f) return biome.Ground;
        if (e < 0.70f) return biome.Vegetation;
        if (e < 0.82f) return biome.Hill;
        return biome.Peak;
    }

    private static bool IsGoodTownSpot(MapData map, int x, int y)
    {
        // Towns settle on flat, walkable ground - any biome's Ground or
        // Coast tile counts. Also accept the legacy Grass/Sand tiles
        // that other generators (TownGenerator etc.) still produce.
        int t = map.GetTile(x, y);
        if (t == TileId.Grass || t == TileId.Sand) return true;
        foreach (var name in BiomeDatabase.Names)
        {
            var b = BiomeDatabase.Get(name);
            if (t == b.Ground || t == b.Coast) return true;
        }
        return false;
    }

    private static bool IsGoodDungeonSpot(MapData map, int x, int y)
    {
        // Dungeons are carved into a biome's elevated rocky terrain:
        // any Hill or Peak tile across all biomes counts, plus the
        // legacy Hills/Mountains tiles.
        int t = map.GetTile(x, y);
        bool elevated = t == TileId.Hills || t == TileId.Mountains;
        if (!elevated)
        {
            foreach (var name in BiomeDatabase.Names)
            {
                var b = BiomeDatabase.Get(name);
                if (t == b.Hill || t == b.Peak) { elevated = true; break; }
            }
        }
        if (!elevated) return false;

        // Require at least one passable neighbor so the player can
        // actually step onto the dungeon tile from the world map.
        for (int dy = -1; dy <= 1; dy++)
        {
            for (int dx = -1; dx <= 1; dx++)
            {
                if (dx == 0 && dy == 0) continue;
                int nx = x + dx, ny = y + dy;
                int nt = map.GetTile(nx, ny);
                if (TileDatabase.IsPassable(nt)) return true;
            }
        }
        return false;
    }

    private static bool TryFindSpot(
        MapData map,
        Random rng,
        List<(int X, int Y)> occupied,
        Func<MapData, int, int, bool> ok,
        int minDistance,
        out int x,
        out int y)
    {
        for (int attempt = 0; attempt < 1000; attempt++)
        {
            int cx = rng.Next(2, Width - 2);
            int cy = rng.Next(2, Height - 2);
            if (!ok(map, cx, cy)) continue;
            if (TooClose(occupied, cx, cy, minDistance)) continue;
            x = cx;
            y = cy;
            return true;
        }
        x = -1;
        y = -1;
        return false;
    }

    private static bool TooClose(List<(int X, int Y)> occupied, int x, int y, int minDistance)
    {
        foreach (var (ox, oy) in occupied)
        {
            int dx = ox - x;
            int dy = oy - y;
            if (dx * dx + dy * dy < minDistance * minDistance)
                return true;
        }
        return false;
    }

    private static void FindAnyPassable(MapData map, Random rng, out int x, out int y)
    {
        for (int attempt = 0; attempt < 5000; attempt++)
        {
            int cx = rng.Next(Width);
            int cy = rng.Next(Height);
            if (TileDatabase.IsPassable(map.GetTile(cx, cy)))
            {
                x = cx;
                y = cy;
                return;
            }
        }
        // Fallback to centre.
        x = Width / 2;
        y = Height / 2;
    }
}
