using System.Collections.Generic;
using Godot;

namespace UltimaLikeRoguelike.Core;

/// <summary>
/// Registry of named 16-color palettes. The map specifies a palette by
/// name; the renderer feeds <c>Get(name).Texture</c> into the shader.
/// <para/>
/// "WorldDay" is the identity palette (= original EGA). Tiles look exactly
/// the way they do when edited. Other palettes substitute different colors
/// for each EGA slot to give a different mood.
/// </summary>
public static class PaletteDatabase
{
    private static readonly Dictionary<string, Palette> _palettes = new();

    public const string WorldDay   = "WorldDay";
    public const string WorldNight = "WorldNight";
    public const string Town       = "Town";
    public const string Dungeon    = "Dungeon";
    public const string Interior   = "Interior";
    public const string Swamp      = "Swamp";
    public const string Fire       = "Fire";

    static PaletteDatabase()
    {
        // Original EGA palette - this is the "no swap" default. Editors
        // see exactly these colors and the runtime renders them unchanged.
        Add(WorldDay, new[]
        {
            //  0 black           1 blue            2 green           3 cyan
            Hex("#000000"), Hex("#0000aa"), Hex("#00aa00"), Hex("#00aaaa"),
            //  4 red             5 magenta         6 brown           7 lt gray
            Hex("#aa0000"), Hex("#aa00aa"), Hex("#aa5500"), Hex("#aaaaaa"),
            //  8 dk gray         9 br blue        10 br green       11 br cyan
            Hex("#555555"), Hex("#5555ff"), Hex("#55ff55"), Hex("#55ffff"),
            // 12 br red         13 br magenta     14 br yellow      15 br white
            Hex("#ff5555"), Hex("#ff55ff"), Hex("#ffff55"), Hex("#ffffff"),
        });

        // Night: cool, desaturated, blue-shifted. Greens become muted teals,
        // browns become slate, whites become soft moonlight.
        Add(WorldNight, new[]
        {
            Hex("#000000"), Hex("#0a0a40"), Hex("#0e3a4a"), Hex("#1a4a5a"),
            Hex("#3a1830"), Hex("#3a1840"), Hex("#3a2818"), Hex("#404a5a"),
            Hex("#1a1a28"), Hex("#3050a0"), Hex("#4a8088"), Hex("#5aaab0"),
            Hex("#80384a"), Hex("#80388a"), Hex("#a08838"), Hex("#a8b0c8"),
        });

        // Town: warm tans and rusty reds; gentle daytime feel.
        Add(Town, new[]
        {
            Hex("#1a0e08"), Hex("#3a3088"), Hex("#3a8030"), Hex("#3a8a8a"),
            Hex("#a03020"), Hex("#a040a0"), Hex("#aa6840"), Hex("#d8c8a0"),
            Hex("#5a4a3a"), Hex("#6080d8"), Hex("#80d860"), Hex("#80e8e0"),
            Hex("#ff7050"), Hex("#ff80f0"), Hex("#ffe080"), Hex("#fff0d8"),
        });

        // Dungeon: cold stone, dim light. Everything pushed toward blue-gray.
        Add(Dungeon, new[]
        {
            Hex("#000000"), Hex("#101a30"), Hex("#1a3030"), Hex("#1a4040"),
            Hex("#601818"), Hex("#401838"), Hex("#403028"), Hex("#606878"),
            Hex("#2a2a30"), Hex("#3050a0"), Hex("#588070"), Hex("#5aa0a8"),
            Hex("#a04040"), Hex("#803868"), Hex("#a09058"), Hex("#c8d0d8"),
        });

        // Interior: warm wood, candlelight, soft shadows.
        Add(Interior, new[]
        {
            Hex("#100808"), Hex("#1a2868"), Hex("#1a5818"), Hex("#1a6868"),
            Hex("#882010"), Hex("#882088"), Hex("#a86838"), Hex("#c8a878"),
            Hex("#403028"), Hex("#5070d0"), Hex("#80d870"), Hex("#80d8d8"),
            Hex("#f06850"), Hex("#e060c0"), Hex("#ffd860"), Hex("#fff0c8"),
        });

        // Swamp: olive-green murk, brown muck.
        Add(Swamp, new[]
        {
            Hex("#000000"), Hex("#202848"), Hex("#385a18"), Hex("#3a5a48"),
            Hex("#682418"), Hex("#582858"), Hex("#583820"), Hex("#787058"),
            Hex("#282818"), Hex("#506098"), Hex("#80a050"), Hex("#80a890"),
            Hex("#985840"), Hex("#985898"), Hex("#c8b860"), Hex("#d8d0a8"),
        });

        // Fire: red/orange shifted, for fiery dungeons or burning towns.
        Add(Fire, new[]
        {
            Hex("#100000"), Hex("#400010"), Hex("#601008"), Hex("#681838"),
            Hex("#a01000"), Hex("#a02018"), Hex("#a04000"), Hex("#c08068"),
            Hex("#401818"), Hex("#a04030"), Hex("#e06020"), Hex("#f0a060"),
            Hex("#ff5020"), Hex("#ff60a0"), Hex("#ffd040"), Hex("#fff0c0"),
        });
    }

    private static void Add(string name, Color[] colors)
        => _palettes[name] = new Palette(name, colors);

    private static Color Hex(string s) => Palette.Hex(s);

    public static Palette Get(string name)
        => _palettes.TryGetValue(name, out var p) ? p : _palettes[WorldDay];
}
