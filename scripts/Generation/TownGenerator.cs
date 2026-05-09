using System;
using System.Collections.Generic;
using UltimaLikeRoguelike.Core;

namespace UltimaLikeRoguelike.Generation;

/// <summary>
/// Generates a town map: 32x32 of the host biome's ground, 4-7
/// rectangular buildings each with a door, a perimeter fence with a
/// southern gate that exits to the world, and decorative trees / wells
/// / signposts. The host <see cref="Biome"/> supplies every tile that
/// makes the town feel "of that biome": ground, walls, windows, doors,
/// floors, and the trees/bushes scattered between buildings.
/// </summary>
public static class TownGenerator
{
    public const int Width = 32;
    public const int Height = 32;

    /// <summary>Returned alongside the map so the caller can lazily generate interiors.</summary>
    public sealed record Building(int DoorX, int DoorY, string InteriorMapId, int Seed);

    public sealed record Result(MapData Map, IReadOnlyList<Building> Buildings);

    public static Result Generate(string mapId, int seed, string biomeName)
    {
        var rng = new Random(seed);
        var biome = BiomeDatabase.Get(biomeName);
        var map = new MapData(mapId, MapKind.Town, Width, Height, PaletteDatabase.Town);

        // 1. Fill with the biome's ground tile.
        map.Fill(0, 0, Width - 1, Height - 1, biome.Ground);

        // 2. Perimeter fence with a southern gate.
        for (int x = 0; x < Width; x++)
        {
            map.SetTile(x, 0, TileId.FenceH);
            map.SetTile(x, Height - 1, TileId.FenceH);
        }
        for (int y = 0; y < Height; y++)
        {
            map.SetTile(0, y, TileId.FenceV);
            map.SetTile(Width - 1, y, TileId.FenceV);
        }
        int gateX = Width / 2;
        // Gate is just a path tile at the southern edge.
        map.SetTile(gateX, Height - 1, TileId.Path);

        // 3. Lay down a north-south main path from the gate.
        int pathY = 1;
        for (int y = pathY; y < Height - 1; y++)
            map.SetTile(gateX, y, TileId.Path);

        // 4. Place buildings on either side of the main path.
        int targetCount = rng.Next(4, 8);
        var buildings = new List<Building>();
        var occupiedRects = new List<(int X0, int Y0, int X1, int Y1)>();
        // Reserve the path corridor.
        occupiedRects.Add((gateX - 1, 0, gateX + 1, Height - 1));

        for (int i = 0; i < targetCount; i++)
        {
            // Building footprint: 5..8 wide, 4..6 tall (interior is footprint minus 2)
            int bw = rng.Next(5, 9);
            int bh = rng.Next(4, 7);
            // Find a placement that doesn't overlap.
            for (int attempt = 0; attempt < 80; attempt++)
            {
                int bx = rng.Next(2, Width - bw - 2);
                int by = rng.Next(3, Height - bh - 3);
                var r = (bx, by, bx + bw - 1, by + bh - 1);
                if (Overlaps(occupiedRects, r, padding: 1)) continue;
                PlaceBuilding(map, biome, rng, bx, by, bw, bh, buildings);
                occupiedRects.Add(r);
                break;
            }
        }

        // 5. Light decoration (biome-themed trees/bushes).
        SprinkleDecor(map, biome, rng);

        // 6. Wire each building's door to its interior id and seed.
        for (int i = 0; i < buildings.Count; i++)
        {
            var b = buildings[i];
            // Update with the proper interior id now that we know the index.
            string interiorId = $"{mapId}:interior:{i}";
            buildings[i] = b with { InteriorMapId = interiorId };
            map.Transitions[(b.DoorX, b.DoorY)] = new MapTransition(interiorId);
        }

        // 7. Gate transition back to the world map. Caller fills in the
        //    target world coordinates after construction.
        map.Transitions[(gateX, Height - 1)] = new MapTransition("world");

        // 8. Player entry point: just inside the gate.
        map.EntryX = gateX;
        map.EntryY = Height - 2;

        return new Result(map, buildings);
    }

    private static void PlaceBuilding(
        MapData map, Biome biome, Random rng,
        int x, int y, int w, int h,
        List<Building> buildings)
    {
        int x1 = x + w - 1;
        int y1 = y + h - 1;

        // Floor and walls come straight from the biome's town tileset
        // - no per-building variation here; the variation is across
        // biomes, not across buildings within a town.
        map.Fill(x + 1, y + 1, x1 - 1, y1 - 1, biome.TownFloor);
        map.Rect(x, y, x1, y1, biome.TownWall);

        // Add a window or two on the north wall.
        if (w >= 6)
        {
            map.SetTile(x + w / 2 - 1, y, biome.TownWindowWall);
            map.SetTile(x + w / 2 + 1, y, biome.TownWindowWall);
        }
        else
        {
            map.SetTile(x + w / 2, y, biome.TownWindowWall);
        }

        // Door on the south wall, near centre. Will become a transition.
        int doorX = x + w / 2;
        int doorY = y1;
        map.SetTile(doorX, doorY, biome.TownDoorClosed);

        // Connect the door to the main path via a short stub.
        // Walk south from the door until we hit the main path.
        for (int yy = doorY + 1; yy < map.Height - 1; yy++)
        {
            int t = map.GetTile(doorX, yy);
            if (t == TileId.Path) break;
            map.SetTile(doorX, yy, TileId.Path);
        }
        // Then connect horizontally to the main path column.
        int connectorY = doorY + 1;
        if (connectorY < map.Height - 1)
        {
            int gateX = map.Width / 2;
            int xx = doorX;
            int step = doorX < gateX ? 1 : -1;
            while (xx != gateX)
            {
                xx += step;
                if (map.GetTile(xx, connectorY) == biome.Ground)
                    map.SetTile(xx, connectorY, TileId.Path);
            }
        }

        buildings.Add(new Building(doorX, doorY, InteriorMapId: "", Seed: rng.Next()));
    }

    private static void SprinkleDecor(MapData map, Biome biome, Random rng)
    {
        for (int i = 0; i < 25; i++)
        {
            int x = rng.Next(1, map.Width - 1);
            int y = rng.Next(1, map.Height - 1);
            if (map.GetTile(x, y) != biome.Ground) continue;
            double r = rng.NextDouble();
            if (r < 0.5) map.SetTile(x, y, biome.Tree);
            else if (r < 0.8) map.SetTile(x, y, biome.Bush);
            else if (r < 0.92) map.SetTile(x, y, TileId.Well);
            else map.SetTile(x, y, TileId.Signpost);
        }
    }

    private static bool Overlaps(
        List<(int X0, int Y0, int X1, int Y1)> rects,
        (int X0, int Y0, int X1, int Y1) r,
        int padding)
    {
        foreach (var o in rects)
        {
            if (r.X1 + padding < o.X0) continue;
            if (r.X0 - padding > o.X1) continue;
            if (r.Y1 + padding < o.Y0) continue;
            if (r.Y0 - padding > o.Y1) continue;
            return true;
        }
        return false;
    }
}
