using Godot;
using UltimaLikeRoguelike.Core;
using UltimaLikeRoguelike.Game;

namespace UltimaLikeRoguelike.View;

/// <summary>
/// Draws the visible region of a <see cref="MapData"/> centered on the
/// player. The palette-swap shader is applied to this node's CanvasItem
/// material so every drawn tile (including the player overlay) is
/// recolored according to the active map's palette.
/// </summary>
public partial class MapRenderer : Node2D
{
    [Export] public Texture2D? Atlas { get; set; }
    [Export] public Shader? PaletteShader { get; set; }

    public const int TileSize = 16;
    public const int ViewTilesX = 11;
    public const int ViewTilesY = 14;

    public MapData? Map { get; private set; }
    public Player? Player { get; set; }

    private ShaderMaterial? _material;

    public override void _Ready()
    {
        if (PaletteShader != null)
        {
            _material = new ShaderMaterial { Shader = PaletteShader };
            Material = _material;
        }
    }

    /// <summary>Switch to a different map and refresh the active palette.</summary>
    public void SetMap(MapData map)
    {
        Map = map;
        if (_material != null)
        {
            var palette = PaletteDatabase.Get(map.PaletteName);
            _material.SetShaderParameter("palette", palette.Texture);
        }
        QueueRedraw();
    }

    public override void _Draw()
    {
        if (Map == null || Atlas == null || this.Player == null) return;

        int halfX = ViewTilesX / 2;
        int halfY = ViewTilesY / 2;
        int startX = this.Player.X - halfX;
        int startY = this.Player.Y - halfY;

        for (int dy = 0; dy < ViewTilesY; dy++)
        {
            for (int dx = 0; dx < ViewTilesX; dx++)
            {
                int mapX = startX + dx;
                int mapY = startY + dy;
                int tileId = Map.InBounds(mapX, mapY)
                    ? Map.GetTile(mapX, mapY)
                    : TileId.Void;
                DrawTile(tileId, dx, dy);
            }
        }

        // Player on top, at the centre of the view.
        DrawTile(this.Player.TileId, halfX, halfY);
    }

    private void DrawTile(int tileId, int dx, int dy)
    {
        if (Atlas == null) return;
        int col = tileId % 8;
        int row = tileId / 8;
        var src = new Rect2(col * TileSize, row * TileSize, TileSize, TileSize);
        var dst = new Rect2(dx * TileSize, dy * TileSize, TileSize, TileSize);
        DrawTextureRectRegion(Atlas, dst, src);
    }
}
