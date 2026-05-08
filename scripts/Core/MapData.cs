using System.Collections.Generic;

namespace UltimaLikeRoguelike.Core;

public enum MapKind
{
    World,
    Town,
    Dungeon,
    Interior,
}

/// <summary>
/// A transition that fires when the player steps onto a tile. The target
/// map is identified by its string id. Optional EntryX/Y override the
/// target map's default entry position (used for "back to where I came
/// from on the parent map" behavior).
/// </summary>
public sealed record MapTransition(
    string TargetMapId,
    int? EntryX = null,
    int? EntryY = null
);

/// <summary>
/// All data for one map: tile grid, transitions, palette, and how to
/// return to the parent map.
/// </summary>
public sealed class MapData
{
    public string Id { get; }
    public MapKind Kind { get; }
    public int Width { get; }
    public int Height { get; }

    /// <summary>Row-major tile grid of length <c>Width * Height</c>.</summary>
    public int[] Tiles { get; }

    /// <summary>Name into <see cref="PaletteDatabase"/>.</summary>
    public string PaletteName { get; set; }

    /// <summary>Tiles that, when stepped on, trigger a transition.</summary>
    public Dictionary<(int X, int Y), MapTransition> Transitions { get; } = new();

    /// <summary>Default entry position when entering this map fresh.</summary>
    public int EntryX { get; set; }
    public int EntryY { get; set; }

    /// <summary>If non-null, "exit" transitions on this map go here.</summary>
    public string? ParentMapId { get; set; }
    public int ParentX { get; set; }
    public int ParentY { get; set; }

    public MapData(string id, MapKind kind, int width, int height, string paletteName)
    {
        Id = id;
        Kind = kind;
        Width = width;
        Height = height;
        Tiles = new int[width * height];
        PaletteName = paletteName;
    }

    public bool InBounds(int x, int y)
        => x >= 0 && y >= 0 && x < Width && y < Height;

    public int GetTile(int x, int y)
        => InBounds(x, y) ? Tiles[y * Width + x] : TileId.Void;

    public void SetTile(int x, int y, int id)
    {
        if (InBounds(x, y))
            Tiles[y * Width + x] = id;
    }

    /// <summary>Fill a rectangle (inclusive) with one tile id.</summary>
    public void Fill(int x0, int y0, int x1, int y1, int id)
    {
        for (int y = y0; y <= y1; y++)
            for (int x = x0; x <= x1; x++)
                SetTile(x, y, id);
    }

    /// <summary>Stroke a rectangle outline with one tile id.</summary>
    public void Rect(int x0, int y0, int x1, int y1, int id)
    {
        for (int x = x0; x <= x1; x++) { SetTile(x, y0, id); SetTile(x, y1, id); }
        for (int y = y0; y <= y1; y++) { SetTile(x0, y, id); SetTile(x1, y, id); }
    }
}
