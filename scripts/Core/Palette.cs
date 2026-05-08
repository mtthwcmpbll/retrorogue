using Godot;

namespace UltimaLikeRoguelike.Core;

/// <summary>
/// A 16-color palette plus a 16x1 ImageTexture ready to be passed as the
/// <c>palette</c> shader uniform. The shader matches each pixel to one of
/// the 16 EGA reference colors and substitutes <see cref="Colors"/>[index].
/// </summary>
public sealed class Palette
{
    public string Name { get; }
    public Color[] Colors { get; }   // length 16; index N replaces EGA color N
    public Texture2D Texture { get; }

    public Palette(string name, Color[] colors)
    {
        if (colors.Length != 16)
            throw new System.ArgumentException(
                $"Palette '{name}' must have exactly 16 colors (got {colors.Length})");

        Name = name;
        Colors = colors;

        var image = Image.CreateEmpty(16, 1, false, Image.Format.Rgba8);
        for (int i = 0; i < 16; i++)
        {
            image.SetPixel(i, 0, colors[i]);
        }
        Texture = ImageTexture.CreateFromImage(image);
    }

    /// <summary>Hex helper: "AABBCC" or "AABBCCDD" -> Color.</summary>
    public static Color Hex(string s) => new(s);
}
