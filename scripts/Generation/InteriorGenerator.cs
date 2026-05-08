using System;
using UltimaLikeRoguelike.Core;

namespace UltimaLikeRoguelike.Generation;

/// <summary>
/// Generates a small building interior. The southern door is a transition
/// back to the parent town (caller fills in the parent coordinates).
/// </summary>
public static class InteriorGenerator
{
    public const int Width = 12;
    public const int Height = 10;

    public static MapData Generate(string mapId, int seed)
    {
        var rng = new Random(seed);
        var map = new MapData(mapId, MapKind.Interior, Width, Height, PaletteDatabase.Interior);

        // Outer wall surrounds a wood floor.
        int floor = rng.NextDouble() < 0.5 ? TileId.WoodFloor : TileId.StoneFloor;
        map.Fill(0, 0, Width - 1, Height - 1, TileId.StoneWall);
        map.Fill(1, 1, Width - 2, Height - 2, floor);

        // Door in the south wall.
        int doorX = Width / 2;
        int doorY = Height - 1;
        map.SetTile(doorX, doorY, TileId.DoorOpen);
        map.Transitions[(doorX, doorY)] = new MapTransition("__parent__");

        // Window on the north wall.
        map.SetTile(Width / 2, 0, TileId.WindowWall);

        // Furniture: bed in a corner, table with chairs, chest, a counter.
        // All optional and randomized so each interior feels different.
        Place(map, rng, 1, 1, TileId.Bed);
        if (rng.NextDouble() < 0.7)
        {
            int tx = rng.Next(3, Width - 4);
            int ty = rng.Next(3, Height - 3);
            map.SetTile(tx, ty, TileId.Table);
            map.SetTile(tx - 1, ty, TileId.Chair);
            map.SetTile(tx + 1, ty, TileId.Chair);
        }
        if (rng.NextDouble() < 0.6)
        {
            map.SetTile(Width - 2, 1, TileId.Chest);
        }
        if (rng.NextDouble() < 0.5)
        {
            int cy = rng.Next(2, Height - 3);
            map.SetTile(1, cy, TileId.Counter);
            map.SetTile(2, cy, TileId.Counter);
        }
        if (rng.NextDouble() < 0.4)
        {
            map.SetTile(Width - 2, Height - 2, TileId.Barrel);
        }

        // One NPC of a random kind, somewhere on the floor.
        int npc = rng.Next(0, 4) switch
        {
            0 => TileId.Merchant,
            1 => TileId.Peasant,
            2 => TileId.Guard,
            _ => TileId.Innkeeper,
        };
        for (int attempt = 0; attempt < 30; attempt++)
        {
            int nx = rng.Next(2, Width - 2);
            int ny = rng.Next(2, Height - 2);
            if (map.GetTile(nx, ny) == floor)
            {
                map.SetTile(nx, ny, npc);
                break;
            }
        }

        // Player entry: just inside the door.
        map.EntryX = doorX;
        map.EntryY = doorY - 1;

        return map;
    }

    private static void Place(MapData map, Random rng, int minX, int minY, int tile)
    {
        int x = rng.Next(minX, map.Width - minX - 1);
        int y = rng.Next(minY, map.Height - minY - 1);
        map.SetTile(x, y, tile);
    }
}
