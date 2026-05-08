using System;
using System.Collections.Generic;
using UltimaLikeRoguelike.Core;

namespace UltimaLikeRoguelike.Generation;

/// <summary>
/// Generates a single-level dungeon with rectangular rooms connected by
/// L-shaped corridors. Stairs-up at the entry tile transitions back to
/// the world map (the caller fills in the world coordinates).
/// </summary>
public static class DungeonGenerator
{
    public const int Width = 32;
    public const int Height = 32;

    public static MapData Generate(string mapId, int seed)
    {
        var rng = new Random(seed);
        var map = new MapData(mapId, MapKind.Dungeon, Width, Height, PaletteDatabase.Dungeon);

        // 1. Fill with stone walls.
        map.Fill(0, 0, Width - 1, Height - 1, TileId.StoneWall);

        // 2. Carve random rooms.
        int roomTarget = rng.Next(6, 11);
        var rooms = new List<(int X, int Y, int W, int H)>();
        for (int i = 0; i < roomTarget; i++)
        {
            for (int attempt = 0; attempt < 60; attempt++)
            {
                int rw = rng.Next(4, 8);
                int rh = rng.Next(4, 7);
                int rx = rng.Next(1, Width - rw - 1);
                int ry = rng.Next(1, Height - rh - 1);
                if (RoomOverlaps(rooms, rx, ry, rw, rh, padding: 1)) continue;
                map.Fill(rx, ry, rx + rw - 1, ry + rh - 1, TileId.StoneFloor);
                rooms.Add((rx, ry, rw, rh));
                break;
            }
        }

        if (rooms.Count == 0)
        {
            // Fallback: a single room dead centre.
            int rx = Width / 2 - 4;
            int ry = Height / 2 - 3;
            map.Fill(rx, ry, rx + 7, ry + 5, TileId.StoneFloor);
            rooms.Add((rx, ry, 8, 6));
        }

        // 3. Connect rooms with L-shaped corridors.
        for (int i = 1; i < rooms.Count; i++)
        {
            var a = RoomCenter(rooms[i - 1]);
            var b = RoomCenter(rooms[i]);
            CarveCorridor(map, a.X, a.Y, b.X, b.Y, rng);
        }

        // 4. Sprinkle barrels and chests in rooms for atmosphere.
        foreach (var room in rooms)
        {
            int decorCount = rng.Next(0, 3);
            for (int i = 0; i < decorCount; i++)
            {
                int dx = rng.Next(room.X + 1, room.X + room.W - 1);
                int dy = rng.Next(room.Y + 1, room.Y + room.H - 1);
                if (map.GetTile(dx, dy) != TileId.StoneFloor) continue;
                double r = rng.NextDouble();
                int t = r < 0.6 ? TileId.Barrel : TileId.Chest;
                map.SetTile(dx, dy, t);
            }
        }

        // 5. Stairs up in the first room: the player's entry point and
        //    the way back to the world.
        var first = RoomCenter(rooms[0]);
        map.SetTile(first.X, first.Y, TileId.StairsUp);
        map.Transitions[(first.X, first.Y)] = new MapTransition("world");
        map.EntryX = first.X;
        map.EntryY = first.Y;

        return map;
    }

    private static (int X, int Y) RoomCenter((int X, int Y, int W, int H) r)
        => (r.X + r.W / 2, r.Y + r.H / 2);

    private static bool RoomOverlaps(
        List<(int X, int Y, int W, int H)> rooms,
        int x, int y, int w, int h, int padding)
    {
        foreach (var r in rooms)
        {
            if (x + w + padding <= r.X) continue;
            if (x >= r.X + r.W + padding) continue;
            if (y + h + padding <= r.Y) continue;
            if (y >= r.Y + r.H + padding) continue;
            return true;
        }
        return false;
    }

    private static void CarveCorridor(MapData map, int x0, int y0, int x1, int y1, Random rng)
    {
        // Random L: horizontal-then-vertical or vertical-then-horizontal.
        if (rng.NextDouble() < 0.5)
        {
            CarveH(map, x0, x1, y0);
            CarveV(map, y0, y1, x1);
        }
        else
        {
            CarveV(map, y0, y1, x0);
            CarveH(map, x0, x1, y1);
        }
    }

    private static void CarveH(MapData map, int x0, int x1, int y)
    {
        int lo = Math.Min(x0, x1);
        int hi = Math.Max(x0, x1);
        for (int x = lo; x <= hi; x++)
            if (map.GetTile(x, y) == TileId.StoneWall)
                map.SetTile(x, y, TileId.StoneFloor);
    }

    private static void CarveV(MapData map, int y0, int y1, int x)
    {
        int lo = Math.Min(y0, y1);
        int hi = Math.Max(y0, y1);
        for (int y = lo; y <= hi; y++)
            if (map.GetTile(x, y) == TileId.StoneWall)
                map.SetTile(x, y, TileId.StoneFloor);
    }
}
