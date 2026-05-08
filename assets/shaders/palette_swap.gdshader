// Palette-swap shader for Ultima-like Roguelike.
//
// Tile atlases are PAINTED in the 16 EGA colors. This shader takes each
// rendered pixel, finds which EGA index it matches, then looks up the
// replacement color from a 16-color palette texture supplied per map.
//
// When the active palette texture IS the EGA palette (default world day),
// the output equals the input -- the swap is identity. For any other
// palette, every EGA color in every tile gets mapped to a new color,
// which is how each map can carry its own mood (night, dungeon, fire,
// ice, etc.) without changing any tile graphics.
//
// Inputs:
//   palette       16x1 texture, one pixel per palette slot, sampled
//                 with nearest-neighbor filtering and no repeat.
//
// The matching is nearest-RGB-distance to be robust against any image
// import resampling that might shift colors slightly. Since artists
// paint with the 16 EGA colors directly, the match is virtually always
// exact in practice.
shader_type canvas_item;

uniform sampler2D palette : filter_nearest, repeat_disable;

// EGA reference colors, normalized to 0..1.  0xAA / 255 ≈ 0.6667,
// 0x55 / 255 ≈ 0.3333.  Order MUST match tools/generate_tiles.py.
const vec3 EGA[16] = vec3[](
    vec3(0.0,    0.0,    0.0   ), //  0 black
    vec3(0.0,    0.0,    0.6667), //  1 blue
    vec3(0.0,    0.6667, 0.0   ), //  2 green
    vec3(0.0,    0.6667, 0.6667), //  3 cyan
    vec3(0.6667, 0.0,    0.0   ), //  4 red
    vec3(0.6667, 0.0,    0.6667), //  5 magenta
    vec3(0.6667, 0.3333, 0.0   ), //  6 brown
    vec3(0.6667, 0.6667, 0.6667), //  7 light gray
    vec3(0.3333, 0.3333, 0.3333), //  8 dark gray
    vec3(0.3333, 0.3333, 1.0   ), //  9 bright blue
    vec3(0.3333, 1.0,    0.3333), // 10 bright green
    vec3(0.3333, 1.0,    1.0   ), // 11 bright cyan
    vec3(1.0,    0.3333, 0.3333), // 12 bright red
    vec3(1.0,    0.3333, 1.0   ), // 13 bright magenta
    vec3(1.0,    1.0,    0.3333), // 14 bright yellow
    vec3(1.0,    1.0,    1.0   )  // 15 bright white
);

void fragment() {
    vec4 src = texture(TEXTURE, UV);

    // Preserve transparency (character tiles depend on it).
    if (src.a < 0.01) {
        discard;
    }

    // Find nearest EGA index by squared RGB distance.
    int best = 0;
    float best_d2 = 1e9;
    for (int i = 0; i < 16; i++) {
        vec3 d = src.rgb - EGA[i];
        float d2 = dot(d, d);
        if (d2 < best_d2) {
            best_d2 = d2;
            best = i;
        }
    }

    // Sample the active palette at the matched index.  The 16x1 palette
    // is addressed by sampling at the *center* of the relevant texel.
    vec3 mapped = texture(palette, vec2((float(best) + 0.5) / 16.0, 0.5)).rgb;

    COLOR = vec4(mapped, src.a);
}
