using System.Collections.Generic;
using Godot;

namespace UltimaLikeRoguelike.Tests;

/// <summary>
/// Smoke test scene: instantiates the real Main scene, lets it run long
/// enough for shaders to compile and the first draw to land, then samples
/// the rendered viewport and asserts the map area is not a single solid
/// color.
///
/// A solid-color map area is the symptom of a failed canvas_item shader
/// compile (the bug fixed when const arrays were moved out of global
/// scope in palette_swap.gdshader). Run as:
///
///     xvfb-run -a godot --rendering-driver opengl3 \
///         --rendering-method gl_compatibility \
///         res://tests/SceneSmokeTest.tscn
///
/// Exit code 0 = pass, non-zero = fail.
/// </summary>
public partial class SceneSmokeTest : Node
{
    // Wait long enough for the C# scripts to run their _Ready, the
    // shader to compile, and the renderer to do its first draw.
    private const int FramesBeforeCheck = 30;

    // Bail out hard if we somehow never reach the check (scene failed to
    // load and nothing is calling Quit).
    private const int FramesHardTimeout = 600;

    // Map area in the 180x320 viewport, matching Main.cs constants.
    private const int MapAreaX = 2;
    private const int MapAreaY = 32;
    private const int MapAreaW = 176;
    private const int MapAreaH = 224;

    private int _frames;
    private bool _checked;

    public override void _Ready()
    {
        GD.Print("[smoke] loading res://scenes/Main.tscn");
        var packed = GD.Load<PackedScene>("res://scenes/Main.tscn");
        if (packed == null)
        {
            Fail("could not load res://scenes/Main.tscn");
            return;
        }

        var instance = packed.Instantiate();
        if (instance == null)
        {
            Fail("Main.tscn failed to instantiate");
            return;
        }
        AddChild(instance);
    }

    public override void _Process(double delta)
    {
        _frames++;

        if (!_checked && _frames >= FramesBeforeCheck)
        {
            _checked = true;
            Check();
            return;
        }

        if (_frames >= FramesHardTimeout)
        {
            Fail($"hard timeout after {FramesHardTimeout} frames");
        }
    }

    private void Check()
    {
        var image = GetViewport().GetTexture().GetImage();
        if (image == null)
        {
            Fail("viewport texture had no image (renderer likely disabled)");
            return;
        }

        // Sample a 5x5 grid across the map area and count distinct colors.
        // A working render shows multiple terrain tiles (water, grass,
        // forest, etc.) plus the player sprite, so we expect several
        // distinct colors. A broken shader paints the whole canvas item
        // a single fallback color.
        var seen = new HashSet<Color>();
        for (int sy = 0; sy < 5; sy++)
        {
            for (int sx = 0; sx < 5; sx++)
            {
                int px = MapAreaX + (MapAreaW * (sx * 2 + 1)) / 10;
                int py = MapAreaY + (MapAreaH * (sy * 2 + 1)) / 10;
                seen.Add(Quantize(image.GetPixel(px, py)));
            }
        }

        const int minDistinctColors = 3;
        if (seen.Count < minDistinctColors)
        {
            int cx = MapAreaX + MapAreaW / 2;
            int cy = MapAreaY + MapAreaH / 2;
            var sample = image.GetPixel(cx, cy);
            Fail(
                $"map area has only {seen.Count} distinct color(s); " +
                $"sample at ({cx},{cy}) = {sample}. " +
                "this is the symptom of a shader compile failure -- " +
                "check stderr above for shader errors.");
            return;
        }

        GD.Print($"[smoke] OK: map area has {seen.Count} distinct colors");
        GetTree().Quit(0);
    }

    private void Fail(string reason)
    {
        GD.PrintErr($"[smoke] FAIL: {reason}");
        GetTree().Quit(1);
    }

    private static Color Quantize(Color c)
    {
        // Round to a 16-step grid so tiny rasterizer rounding differences
        // between drivers don't make near-identical pixels look distinct.
        const float n = 16f;
        return new Color(
            Mathf.Round(c.R * n) / n,
            Mathf.Round(c.G * n) / n,
            Mathf.Round(c.B * n) / n);
    }
}
