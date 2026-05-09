"""
Generate the tile atlas using the actual EGA 16-color palette.

Saved as a normal RGBA PNG painted with the 16 EGA colors. You can open it
in any image editor (Aseprite/GIMP/Photoshop/Pixelorama) and edit it freely
as long as you stick to the 16 EGA colors. A reference swatch
(ega_palette.png) is also written that you can load as a palette.

The shader at runtime matches each pixel to the closest EGA color to find
its index 0..15, then looks up the active per-map palette at that index --
so the same tile graphics can carry many moods (day/night, dungeon, fire,
ice, ...) by swapping a single 16-color palette texture.

Atlas: 8 cols x 8 rows of 16x16 tiles (128 px x 128 px).
Tile id = row * 8 + col.
"""

from __future__ import annotations

import os
from PIL import Image

# EGA palette (RGB; 0xAA = 170, 0x55 = 85)
EGA: list[tuple[int, int, int, int]] = [
    (  0,   0,   0, 255),  # 0  black
    (  0,   0, 170, 255),  # 1  blue
    (  0, 170,   0, 255),  # 2  green
    (  0, 170, 170, 255),  # 3  cyan
    (170,   0,   0, 255),  # 4  red
    (170,   0, 170, 255),  # 5  magenta
    (170,  85,   0, 255),  # 6  brown
    (170, 170, 170, 255),  # 7  light gray
    ( 85,  85,  85, 255),  # 8  dark gray
    ( 85,  85, 255, 255),  # 9  bright blue
    ( 85, 255,  85, 255),  # 10 bright green
    ( 85, 255, 255, 255),  # 11 bright cyan
    (255,  85,  85, 255),  # 12 bright red
    (255,  85, 255, 255),  # 13 bright magenta
    (255, 255,  85, 255),  # 14 bright yellow
    (255, 255, 255, 255),  # 15 bright white
]

TRANSPARENT = (0, 0, 0, 0)

# '.' = transparent.  '0'..'9','a'..'f' = EGA palette index 0..15.
CHAR_TO_INDEX: dict[str, int] = {'.': -1}
for i, c in enumerate('0123456789abcdef'):
    CHAR_TO_INDEX[c] = i

TILE = 16
COLS = 8
ROWS = 20
ATLAS_W = TILE * COLS
ATLAS_H = TILE * ROWS


def t(*rows: str) -> list[str]:
    """Tile constructor that fails LOUDLY on malformed input."""
    if len(rows) != TILE:
        raise AssertionError(f'tile must have {TILE} rows, got {len(rows)}')
    for i, row in enumerate(rows):
        if len(row) != TILE:
            raise AssertionError(
                f'row {i} length {len(row)} (need {TILE}): {row!r}'
            )
        for c in row:
            if c not in CHAR_TO_INDEX:
                raise AssertionError(f'row {i}: bad char {c!r} in {row!r}')
    return list(rows)


# Color cheat sheet:
#   0 black       4 red         8 dark gray   c bright red
#   1 blue        5 magenta     9 bright blue d bright magenta
#   2 green       6 brown       a bright grn  e bright yellow
#   3 cyan        7 light gray  b bright cyan f bright white
TILES: dict[int, list[str]] = {}

# ---- Row 0: terrain 0..7 ----------------------------------------------------
TILES[0] = t(  # Void
    '................', '................', '................',
    '................', '................', '................',
    '................', '................', '................',
    '................', '................', '................',
    '................', '................', '................',
    '................',
)

TILES[1] = t(  # Deep Water
    '1111111111111111',
    '1111911111111111',
    '1119911111119111',
    '1111111111199111',
    '1111111111119111',
    '1111111111111111',
    '1119111111111111',
    '1191111111111119',
    '1111111111111199',
    '1111111111111119',
    '1119111111111111',
    '1111911111111111',
    '1111991111119111',
    '1111111119911111',
    '1111111111119111',
    '1111111111111111',
)

TILES[2] = t(  # Shallow Water
    '9999999999999999',
    '9999b99999999999',
    '999bb999999b9999',
    '9999999999bbb999',
    '9999999999b99999',
    '999b9999999999b9',
    '99bb99999bb99999',
    '999b9999b9999999',
    '9999999999999b99',
    '999999999999bb99',
    '99bbb999999999b9',
    '9999999999b99999',
    '9999b99bb99999b9',
    '99b9999999999999',
    '9999999999999999',
    '9999999999999999',
)

TILES[3] = t(  # Sand: bright/brown 50/50 dither = perceived "tan"
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
)

TILES[4] = t(  # Grass: green/bright-green dither with brown tufts
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a26a2a2a2a',
    '2a2a26a2a2a2a26a',
    'a2a2a2a2a2a2a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a26a2a2a2a26a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a26a2a2a2a',
    '2a26a2a2a2a26a2a',
    'a2a2a2a2a2a2a2a2',
    '2a2a2a26a2a2a2a2',
    'a26a2a2a2a26a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a26a2a2a2a26',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[5] = t(  # Forest: tree silhouette on dithered grass
    '2a2a2a2a2a2a2a2a',
    'a2a2a2aaaa2a2a2a',
    '2a2a2aaaaaaa2a2a',
    'a2a2aaaaaaaaaa2a',
    '2a2aaaaaaaaaaa2a',
    'a2aaa2aaa2aaaa2a',
    '2a2aaaa2aaaa2a2a',
    'a2a2aaaaaaaa2a2a',
    '2a2a2aa66aa2a2a2',
    'a2a2a2a66a2a2a2a',
    '2a2a2a2662a2a2a2',
    'a2a2a26666a2a2a2',
    '2a2a266666a62a2a',
    'a2a266666666a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[6] = t(  # Hills: brown/yellow rocky mound on dithered grass
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a26a2a2a',
    '2a2a2a26e6e2a2a2',
    'a2a2a6e6e6e6a2a2',
    '2a26e6e6e6e6e62a',
    'a26e6e6e6e6e6e62',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'a26e6e6e6e6e6e62',
    '2a26e6e6e6e6e62a',
    'a2a26e6e6e6e6a2a',
    '2a2a26e6e6e62a2a',
    'a2a2a26e6e62a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[7] = t(  # Mountains: snowy peak gradient on dithered grass
    '2a2a2a2a2a2a2a2a',
    'a2a2a2af7fa2a2a2',
    '2a2a2af7f7f2a2a2',
    'a2a2af7f8f7fa2a2',
    '2a27f7f888f7f72a',
    'a2af78ff888f7872',
    '2af78fff888f7878',
    'af78fff7f7f87878',
    '78fff7f7f7878787',
    '8f78f87f878f8787',
    '7878787878787878',
    '8787878787878787',
    '7887787878787878',
    '8787878787878787',
    '2882882a2882882a',
    '2a2a2a2a2a2a2a2a',
)

# ---- Row 1: structures 8..15 -----------------------------------------------
TILES[8] = t(  # Swamp
    '2868282228262822',
    '8222886822262228',
    '2226668222226822',
    '8228222266822226',
    '2222286622222266',
    '6688222222226822',
    '2222226668222222',
    '2228222222226666',
    '2266822226822222',
    '8222222222222286',
    '2222266822222222',
    '6622222222268822',
    '2228822222226822',
    '2222222266822222',
    '2266288222266822',
    '8222222268282266',
)

TILES[9] = t(  # Town
    '2222222222222222',
    '22222222c2222222',
    '2222222ccc222222',
    '222222ccccc22222',
    '22222ccccccc2222',
    '2222ccccccccc222',
    '222ccccccccccc22',
    '2266aaaaaaaa6622',
    '226aaaaaaaaaa622',
    '226aaa6aa6aaa622',
    '226aaa666666a622',
    '226aaa6aa6aaa622',
    '226aa6aaa66aa622',
    '226aaaaaa6aaa622',
    '2266666666666622',
    '2222222222222222',
)

TILES[10] = t(  # Castle
    '2222222c22222222',
    '2222222c22222222',
    '2222222cc2222222',
    '7878787877878787',
    '7777777787777777',
    '78aaaaa8aaaaa087',
    '78a000a8a000a087',
    '78a000a8a000a087',
    '78aaaaa8aaaaa087',
    '7888888888888887',
    '78aaaaaaaaaaaa87',
    '78a000aaaaa0a087',
    '78a000aaaaa0a087',
    '78aaaaaaaaaaaa87',
    '7888888888888888',
    '2222222222222222',
)

TILES[11] = t(  # Dungeon Entrance
    '2222222222222222',
    '2228888888888222',
    '2287777777778822',
    '2877088888807782',
    '8770000888000778',
    '8700000088000078',
    '8700000000000078',
    '8000000000000008',
    '8000000000000008',
    '8000000000000008',
    '8000000000000008',
    '8000000000000008',
    '8000000000000008',
    '8000000000000008',
    '8888888888888888',
    '2222222222222222',
)

TILES[12] = t(  # Bridge horizontal (over water)
    '9999999999999999',
    '9999999999999999',
    '6666666666666666',
    'eeeeeeeeeeeeeeee',
    '6e6e6e6e6e6e6e6e',
    '6666666666666666',
    'eeeeeeeeeeeeeeee',
    '6666666666666666',
    '6666666666666666',
    'eeeeeeeeeeeeeeee',
    '6e6e6e6e6e6e6e6e',
    '6666666666666666',
    'eeeeeeeeeeeeeeee',
    '6666666666666666',
    '9999999999999999',
    '9999999999999999',
)

TILES[13] = t(  # Bridge vertical
    '99666e9966966e99',
    '99666e9966966e99',
    '99eee69966666e99',
    '996e6e9966e6ee99',
    '99666e9966666e99',
    '99e66e9966666e99',
    '996e6e9966e66e99',
    '99eee69966666e99',
    '99666e9966666e99',
    '996e6e9966e6ee99',
    '99eee69966966e99',
    '99666e9966666e99',
    '996e6e9966966e99',
    '99eee69966666e99',
    '99666e9966666e99',
    '996e6e9966966e99',
)

TILES[14] = t(  # Path
    '2266222266662266',
    '6e6e2e66e66e6e26',
    '6666e66666e66666',
    '6666666666e66666',
    '66e6666666666666',
    '6666666e66666666',
    '6666666666666e66',
    '6666e6e666666666',
    '6666666666666666',
    '66e66666e6666e66',
    '666666666e666666',
    '66e66666666e6666',
    '666666e666666666',
    '6666666666666666',
    '6626666666626662',
    '2266226666226622',
)

TILES[15] = t(  # Signpost
    '2222222222222222',
    '2222222222222222',
    '2222ffffffff2222',
    '2222f000000ef222',
    '2222f00ee000ef22',
    '2222f00e0e00ef22',
    '2222f00e000eef22',
    '2222ffffffffff22',
    '22222266622222e2',
    '2222226e6e2222e2',
    '2222226666222222',
    '2222226662222222',
    '2222226662222222',
    '2222226e62222222',
    '2222266662222222',
    '2222222222222222',
)

# ---- Row 2: world detail / interactive 16..23 ------------------------------
TILES[16] = t(  # Tree
    '2222222a22222222',
    '2222222aa2222222',
    '222222aaaa222222',
    '22222aaaaaa22222',
    '2222aaaaaaaa2222',
    '222aaa2aaa2aa222',
    '222aaaaaaaaaa222',
    '2222aaaaaaaa2222',
    '22222aa66aa22222',
    '2222222662222222',
    '2222222662222222',
    '2222226666222222',
    '2222266666622222',
    '2222226666222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[17] = t(  # Bush
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222aa2222222',
    '222222aaaa222222',
    '22222aaaaaa22222',
    '2222aaaa2aaa2222',
    '222aaa2aa2aaa222',
    '2222aaaa2aaa2222',
    '22222aaaaaa22222',
    '222222aaaa222222',
    '2222222aa2222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[18] = t(  # Rock
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222227777222222',
    '222227ff7f722222',
    '22227ff7f7f72222',
    '2227ffff7f8f7222',
    '227fff8ff8ff8722',
    '27ffff8888fff872',
    '27f8888888888872',
    '2788888888888887',
    '2788888888888887',
    '2788888888888887',
    '2227888888888722',
    '2222288888882222',
    '2222222222222222',
)

TILES[19] = t(  # Well
    '2222222222222222',
    '2222222ee2222222',
    '2222226662222222',
    '2222226662222222',
    '2228888888888222',
    '2287777777777822',
    '2287000000007822',
    '2287000110007822',
    '2287001111007822',
    '2287000110007822',
    '2287000000007822',
    '2287777777777822',
    '2288888888888822',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[20] = t(  # Fence horizontal
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '6266626662666266',
    '6666666666666666',
    'e6e6e6e6e6e6e6e6',
    '6666666666666666',
    '6266626662666266',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[21] = t(  # Fence vertical
    '2226666222266662',
    '2226666222266662',
    '2266666666666666',
    '2226666222266662',
    '6666666666666666',
    '2226666222266662',
    '6666666666666666',
    '2226666222266662',
    '6666666666666666',
    '2226666222266662',
    '6666666666666666',
    '2226666222266662',
    '6666666666666666',
    '2226666222266662',
    '6266662222666622',
    '2266666666666666',
)

TILES[22] = t(  # Stairs Up
    '2222222222222222',
    '2222222222222222',
    '8888888888888888',
    '8777777777777778',
    '8788888888888878',
    '8788ffffffff8878',
    '8788f8f8f8ff8878',
    '8788ffff8888ff78',
    '8788f8f8f8f8ff78',
    '8788ffff8888fff8',
    '8788f8f8f8ff8878',
    '8788ffffffff8878',
    '8788888888888878',
    '8777777777777778',
    '8888888888888888',
    '2222222222222222',
)

TILES[23] = t(  # Stairs Down
    '2222222222222222',
    '8888888888888888',
    '8777777777777778',
    '8000000000000008',
    '8088888888888008',
    '8000000000000008',
    '8088888888888008',
    '8000000000000008',
    '8088888888888008',
    '8000000000000008',
    '8088888888888008',
    '8777777777777778',
    '8888888888888888',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
)

# ---- Row 3: floors and walls 24..31 ----------------------------------------
TILES[24] = t(  # Stone Floor: dithered light/dark gray flagstones
    '8888888888888888',
    '8787878887878787',
    '8787878887878787',
    '7878787887878788',
    '7878787887878788',
    '8787878887878787',
    '8888888888888888',
    '7878787787878787',
    '7878787787878787',
    '8787878787878788',
    '8787878787878788',
    '7878787787878787',
    '7878787787878787',
    '8888888888888888',
    '8787878887878787',
    '8787878887878787',
)

TILES[25] = t(  # Wood Floor
    '8888888888888888',
    '6e6666666e666666',
    '666666e6666666e6',
    '6666666666666666',
    '666e6666666e6666',
    '8888888888888888',
    '6666e6666666e666',
    '66e66666e6666666',
    '6666666666666666',
    '6666e666666666e6',
    '8888888888888888',
    '666666e6666e6666',
    '6e66666666666666',
    '66666e66666666e6',
    '6666666666666666',
    '8888888888888888',
)

TILES[26] = t(  # Brick Floor: bright/dark red dither bricks with gray grout
    '7777777777777777',
    '7c4c4c47c4c4c477',
    '74c4c4c74c4c4c77',
    '7c4c4c47c4c4c477',
    '7777777777777777',
    'c4c4c47c4c4c47c4',
    '4c4c4c74c4c4c74c',
    'c4c4c47c4c4c47c4',
    '7777777777777777',
    '7c4c4c47c4c4c477',
    '74c4c4c74c4c4c77',
    '7c4c4c47c4c4c477',
    '7777777777777777',
    'c4c4c47c4c4c47c4',
    '4c4c4c74c4c4c74c',
    'c4c4c47c4c4c47c4',
)

TILES[27] = TILES[4][:]  # Grass Floor: same as world grass

TILES[28] = t(  # Stone Wall: dithered gray blocks with dark grout
    '8888888888888888',
    '8787878887878788',
    '7878787887878787',
    '8787878887878788',
    '7878787887878787',
    '8787878887878788',
    '7878787887878787',
    '8888888888888888',
    '7878787787878788',
    '8787878787878787',
    '7878787787878788',
    '8787878787878787',
    '7878787787878788',
    '8787878787878787',
    '7878787787878788',
    '8888888888888888',
)

TILES[29] = t(  # Wood Wall
    '6e6666e6e66666e6',
    '6e6666e6e66666e6',
    '6e6666e6e66666e6',
    '6e6666e6e66666e6',
    '6e6666e6e66666e6',
    '8888888888888888',
    '66e6666666e66666',
    '66e6666666e66666',
    '66e6666666e66666',
    '66e6666666e66666',
    '66e6666666e66666',
    '8888888888888888',
    '6666e6e66666e666',
    '6666e6e66666e666',
    '6666e6e66666e666',
    '6666e6e66666e666',
)

TILES[30] = t(  # Brick Wall: dithered red bricks with gray grout
    '7777777777777777',
    'c4c4c47c4c4c47c4',
    '4c4c4c74c4c4c74c',
    'c4c4c47c4c4c47c4',
    '7777777777777777',
    '7c4c4c47c4c4c47c',
    '74c4c4c74c4c4c74',
    '7c4c4c47c4c4c47c',
    '7777777777777777',
    'c4c4c47c4c4c47c4',
    '4c4c4c74c4c4c74c',
    'c4c4c47c4c4c47c4',
    '7777777777777777',
    '7c4c4c47c4c4c47c',
    '74c4c4c74c4c4c74',
    '7c4c4c47c4c4c47c',
)

TILES[31] = t(  # Window Wall: dithered stone with cyan/bright cyan window
    '8888888888888888',
    '8787878787878788',
    '7878787878787878',
    '8788888888888788',
    '878bbbbbbbbbb878',
    '8783b3b3b3b3b378',
    '8783b3b3b3b3b378',
    '878b3b3b3b3b3b78',
    '878b3b3b3b3b3b78',
    '8783b3b3b3b3b378',
    '8783b3b3b3b3b378',
    '878bbbbbbbbbb878',
    '8788888888888788',
    '7878787878787878',
    '8787878787878788',
    '8888888888888888',
)

# ---- Row 4: furniture 32..39 -----------------------------------------------
TILES[32] = t(  # Door Closed
    '8888888888888888',
    '8666666666666668',
    '866ee666666e6668',
    '866e6e66666e6668',
    '866e6e66666e6668',
    '866e6e66ee6e6668',
    '866e6e66e66e6668',
    '866e6e66e66e6668',
    '866e6e66e66e6668',
    '866e6e66e6ee6668',
    '866e6e66666e6668',
    '866e6e66666e66e8',
    '866e6e66666e66e8',
    '866ee666666e6668',
    '8666666666666668',
    '8888888888888888',
)

TILES[33] = t(  # Door Open
    '8888888888888888',
    '8888888888888888',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8888888888888888',
    '8888888888888888',
)

TILES[34] = t(  # Bed: dithered white pillow + dithered red blanket
    '8888888888888888',
    '8666666666666668',
    '86f7f7f664c4c468',
    '867f7f7664c4c468',
    '86f7f7f64c4c4c68',
    '867f7f7664c4c468',
    '8666666666666668',
    '866c4c4c4c4c4668',
    '8664c4c4c4c4c668',
    '866c4c4c4c4c4668',
    '8664c4c4c4c4c668',
    '866c4c4c4c4c4668',
    '8664c4c4c4c4c668',
    '866c4c4c4c4c4668',
    '8666666666666668',
    '8888888888888888',
)

TILES[35] = t(  # Table
    '7777777777777777',
    '7777777777777777',
    '8888888888888888',
    '8666666666666668',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '8666666666666668',
    '8888888888888888',
    '7766777777776677',
    '7766777777776677',
    '7766777777776677',
    '7766777777776677',
    '7777777777777777',
    '7777777777777777',
)

TILES[36] = t(  # Chair
    '7777777777777777',
    '7777666666667777',
    '7776e66666e66777',
    '7776e66666e66777',
    '7776e66666e66777',
    '7776666666666777',
    '7776666666666777',
    '7776666666666777',
    '7777666666667777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777666666667777',
    '7777777777777777',
)

TILES[37] = t(  # Counter: dithered wood top with brown/gray base
    '7777777777777777',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8888888888888888',
    '7777777777777777',
)

TILES[38] = t(  # Chest
    '7777777777777777',
    '7777777777777777',
    '777eeeeeeeeee777',
    '77e666666666e677',
    '77e6eeeeeeee6e77',
    '77e6e666666e6e77',
    '77e6e6eeee6e6e77',
    '77e6e6eeee6e6e77',
    '77e6e666666e6e77',
    '77e6eeeeeeee6e77',
    '77e6666e6666e677',
    '77e666eee6666e77',
    '77e6666e6666ee77',
    '77eeeeeeeeeeee77',
    '7777777777777777',
    '7777777777777777',
)

TILES[39] = t(  # Barrel
    '7777777777777777',
    '7778688888888677',
    '7768e66e6e6e6877',
    '7786e6e6e6e6e687',
    '7786e6e6e6e6e687',
    '7768888888888877',
    '7786e6e6e6e6e687',
    '7786e6e6e6e6e687',
    '7768888888888877',
    '7786e6e6e6e6e687',
    '7786e6e6e6e6e687',
    '7768888888888877',
    '7786e6e6e6e6e687',
    '7786e6e6e6e6e687',
    '7777888888888777',
    '7777777777777777',
)

# ---- Row 5: characters 40..47 (transparent backgrounds) --------------------
TILES[40] = t(  # Player South
    '................',
    '................',
    '......8888......',
    '.....866668.....',
    '.....86ee68.....',
    '.....86fe68.....',
    '.....8eeee8.....',
    '......8888......',
    '....88848888....',
    '...844444448....',
    '...844444448....',
    '....88844488....',
    '.....66886......',
    '.....66.66......',
    '.....66.66......',
    '.....88..88.....',
)

TILES[41] = t(  # Player North
    '................',
    '................',
    '......8888......',
    '.....866668.....',
    '.....866668.....',
    '.....866668.....',
    '.....866668.....',
    '......8888......',
    '....88848888....',
    '...844444448....',
    '...844444448....',
    '....88844488....',
    '.....66886......',
    '.....66.66......',
    '.....66.66......',
    '.....88..88.....',
)

TILES[42] = t(  # Player East
    '................',
    '................',
    '......8888......',
    '.....86668e.....',
    '.....86eef8.....',
    '.....8666e8.....',
    '.....8eee68.....',
    '......8888......',
    '....8884888.....',
    '...84444488.....',
    '...84444488.....',
    '....8844488.....',
    '....66888.66....',
    '....66....66....',
    '....66....66....',
    '....88....88....',
)

TILES[43] = t(  # Player West
    '................',
    '................',
    '......8888......',
    '.....e86668.....',
    '.....8fee68.....',
    '.....8e6668.....',
    '.....86eee8.....',
    '......8888......',
    '....8884888.....',
    '....88444448....',
    '....88444448....',
    '....88444888....',
    '...66.88866.....',
    '...66....66.....',
    '...66....66.....',
    '...88....88.....',
)

TILES[44] = t(  # Merchant
    '................',
    '......6666......',
    '.....666666.....',
    '.....86ee68.....',
    '.....86fe68.....',
    '.....8eeee8.....',
    '......8888......',
    '....88c111c8....',
    '...8c1c11c1c8...',
    '...8c111111c8...',
    '....8c1111c8....',
    '....8cffffc8....',
    '....8cffffc8....',
    '....88ffff88....',
    '....66.66.66....',
    '....88.88.88....',
)

TILES[45] = t(  # Peasant
    '................',
    '......eee.......',
    '.....66666......',
    '.....86ee68.....',
    '.....86fe68.....',
    '.....8eeee8.....',
    '......8888......',
    '....88862888....',
    '...8666226668...',
    '...8662222668...',
    '....86222268....',
    '....88222288....',
    '....66...66.....',
    '....66...66.....',
    '....66...66.....',
    '....88...88.....',
)

TILES[46] = t(  # Guard
    '................',
    '.....877788.....',
    '.....87f7f8.....',
    '.....86ee68.....',
    '.....86fe68.....',
    '.....8eeee8.....',
    '......8788......',
    '....88c777c8....',
    '...8c777c777c...',
    '...8c77ccc77c...',
    '....8c77777c8...',
    '.....8c777c8....',
    '....88c7c7c88...',
    '....66.7.7.66...',
    '....66.....66...',
    '....88.....88...',
)

TILES[47] = t(  # Innkeeper
    '................',
    '......6666......',
    '.....666666.....',
    '.....86ee68.....',
    '.....86fe68.....',
    '....66eeee66....',
    '....66666666....',
    '....88c777c8....',
    '...8c7777777c...',
    '...8cfffffffc...',
    '....8cffffc8....',
    '....8cffffc8....',
    '....8cffffc8....',
    '....88ffff88....',
    '....66.66.66....',
    '....88.88.88....',
)

# ---- Per-biome tilesets (rows 6..12) ---------------------------------------
# Each biome occupies one row of 8 tiles, in this order:
#   Coast, Ground, Vegetation, Hill, Peak, Tree, Bush, Rock
# So tile id of biome B's role R = 48 + 8*B + R (B in 0..6, R in 0..7).

# ---- Row 6: Plains 48..55 --------------------------------------------------
TILES[48] = t(  # Plains Coast: dithered sand with grass tufts at the back
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e2e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e2e6e6e6e6e6e',
    'e6e6e6e6e6e6e2e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e2e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e2e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e2e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e2e6e6e6e6e6e',
    'e6e6e6e6e6e6e2e6',
    '6e6e6e6e6e6e6e6e',
)

TILES[49] = t(  # Plains Ground: dithered green grass with brown clumps
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a26a2a2a2a',
    '2a2a26a2a2a2a26a',
    'a2a2a2a2a2a2a2a2',
    '2a2a2a2a2a2a2a2a',
    'a26a2a2a2a26a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a26a2a2a2a',
    '2a26a2a2a2a26a2a',
    'a2a2a2a2a2a2a2a2',
    '2a2a2a2a26a2a2a2',
    'a26a2a2a2a26a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2a2a26a2a2a2a26',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[50] = t(  # Plains Vegetation: tall grass with yellow flowers
    '2a2a2a2a2a2a2a2a',
    'aaa2aae2aaa2aae2',
    'aaa2aae2aaa2aae2',
    '2a2a2a2a2a2a2a2a',
    'aae2aaa2aae2aaa2',
    'aae2aaa2aae2aaa2',
    '2a2a2a2a2a2a2a2a',
    'aaa2aaa2aae2aaa2',
    'aaa2aaa2aae2aaa2',
    '2a2a2a2a2a2a2a2a',
    'aae2aaa2aaa2aae2',
    'aae2aaa2aaa2aae2',
    '2a2a2a2a2a2a2a2a',
    'aaa2aae2aaa2aaa2',
    'aaa2aae2aaa2aaa2',
    '2a2a2a2a2a2a2a2a',
)

TILES[51] = t(  # Plains Hill: dithered grassy mound with brown rocks
    '2a2a2a2a2a2a2a2a',
    'a2a2a26666a2a2a2',
    '2a2a26a6a662a2a2',
    'a2a26a6a6a6a2a2a',
    '2a26a6a6a6a6a2a2',
    'a26a6a6a6a6a6a62',
    '6a6a6a6a6a6a6a6a',
    'a6a6a6a6a6a6a6a6',
    '6a6a6a6a6a6a6a6a',
    'a26a6a6a6a6a6a62',
    '2a26a6a6a6a6a62a',
    'a2a26a6a6a6a6a2a',
    '2a2a26a6a6a62a2a',
    'a2a2a266662a2a2a',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[52] = t(  # Plains Peak: dithered snow/stone gradient
    '2a2a2a2a2a2a2a2a',
    'a2a2a2afffa2a2a2',
    '2a2a2af7f7fa2a2a',
    'a2a2af7f8f7fa2a2',
    '2a2a7f78878f7a2a',
    'a2a7f78f8f878f72',
    '2af78f87878f8788',
    'a7f8787878787888',
    '7f87878787878787',
    '8787878787878788',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '2882288228822882',
    '2a2a2a2a2a2a2a2a',
)

TILES[53] = t(  # Plains Tree: leafy oak
    '2222222a22222222',
    '2222222aa2222222',
    '222222aaaa222222',
    '22222aaaaaa22222',
    '2222aaaaaaaa2222',
    '222aaa2aaa2aa222',
    '222aaaaaaaaaa222',
    '2222aaaaaaaa2222',
    '22222aa66aa22222',
    '2222222662222222',
    '2222222662222222',
    '2222226666222222',
    '2222266666622222',
    '2222226666222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[54] = t(  # Plains Bush: leafy shrub
    '2222222222222222',
    '2222222222222222',
    '2222222aa2222222',
    '222222aaaa222222',
    '22222aaaaaa22222',
    '2222aaaa2aaa2222',
    '222aaa2aa2aaa222',
    '2222aaaa2aaa2222',
    '22222aaaaaa22222',
    '222222aaaa222222',
    '2222222aa2222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[55] = t(  # Plains Rock: gray boulder
    '2222222222222222',
    '2222222222222222',
    '2222227777222222',
    '222227ff7f722222',
    '22227ff7f7f72222',
    '2227ffff7f8f7222',
    '227fff8ff8ff8722',
    '27ffff8888fff872',
    '27f8888888888872',
    '2788888888888887',
    '2788888888888887',
    '2788888888888887',
    '2227888888888722',
    '2222288888882222',
    '2222222222222222',
    '2222222222222222',
)

# ---- Row 7: Desert 56..63 --------------------------------------------------
TILES[56] = t(  # Desert Coast: dithered tan sand
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
)

TILES[57] = t(  # Desert Ground: cracked sand with brown veins
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e666e6e6e6e6e6',
    '6e6e66e6e6e666e6',
    'e6e6e6e6e66e6e6e',
    '6e6e6e6e6e66e6e6',
    'e6e6e66666e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e666',
    '6e6e6e6e6e6e66e6',
    'e6e66e6e6e6e6e6e',
    '6666e6e6e6e6e6e6',
    'e6e6e6e6e6666e6e',
    '6e6e6e6e6e6e6e6e',
    'e6e6e66e6e6e6e6e',
    '6e6e6e6e6e6e6e6e',
)

TILES[58] = t(  # Desert Vegetation: dithered dune mound
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e666e6e6e6e',
    'e6e6e66666e6e6e6',
    '6e6e66eeee6e6e6e',
    'e6e6e6eeee66e6e6',
    '6e6e66eeeeee6e6e',
    'e6e66eeeeeee6e6e',
    '6e66eeeeeeeee6e6',
    'e66eeeeeeeeee6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
)

TILES[59] = t(  # Desert Hill: dithered red sandstone mesa on tan ground
    'e6e6e6e6e6e6e6e6',
    '6e6e6c4c4c4ce6e6',
    'e6e6c4c4c4c4c6e6',
    '6e6c4c4c4c4c4c6e',
    'e6c4c4c4c4c4c4c6',
    '6c4c4c4c4c4c4c4c',
    'c4c4c4c4c4c4c4c4',
    '4c4c4c4c4c4c4c4c',
    'c4c4c4c4c4c4c4c4',
    '4c4c4c4c4c4c4c4c',
    '6c4c4c4c4c4c4c4c',
    'e6c4c4c4c4c4c4c6',
    '6e6c4c4c4c4c4c6e',
    'e6e6c4c4c4c4c6e6',
    '6e6e6c4c4c4ce6e6',
    'e6e6e6e6e6e6e6e6',
)

TILES[60] = t(  # Desert Peak: red sandstone spire with dither
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6c4c6e6e6e',
    'e6e6e6c4c4c6e6e6',
    '6e6e6c4c4c4c6e6e',
    'e6e6c4c4c4c4c6e6',
    '6e6c4c4c4c4c4c6e',
    'e6c4c4c4c4c4c4c6',
    '6c4c4c4c4c4c4c4c',
    'c4c4c4c4c4c4c4c4',
    '4c4c4c4c4c4c4c4c',
    'c4c4c4c4c4c4c4c4',
    '4c4c4c4c4c4c4c4c',
    'c4c4c4c4c4c4c4c4',
    '4c4c4c4c4c4c4c4c',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
)

TILES[61] = t(  # Desert Tree: cactus
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeaeeeeeee',
    'eeeeeeeaaaeeeeee',
    'eeeaeeea2aeeaeee',
    'eeaaaeea2aeaaaee',
    'eea2aeea2aeea2ae',
    'eea2aaaa2aaaa2ae',
    'eea2222a2a2222ae',
    'eea22aaaaaaa22ae',
    'eea22a22a22a22ae',
    'eea22a22a22a22ae',
    'eeaaa22a22a22aae',
    'eeeea22a22a22aee',
    'eeeeaaaaaaaaaeee',
    'eeeeee6666eeeeee',
    'eeeeee6666eeeeee',
)

TILES[62] = t(  # Desert Bush: dry tumbleweed
    'eeeeeeeeeeeeeeee',
    'eeeeeeee6eeeeeee',
    'eeeeee666e6eeeee',
    'eeeee66e66e6eeee',
    'eeee6e6e6e6e6eee',
    'eee66e66e66e66ee',
    'ee6e6e6e6e6e6e6e',
    'ee6e66e6e6e66e6e',
    'ee6e6e6e6e6e6e6e',
    'ee6e66e6e6e66e6e',
    'eee66e66e66e66ee',
    'eeee6e6e6e6e6eee',
    'eeeee66e66e6eeee',
    'eeeeee666e6eeeee',
    'eeeeeeee6eeeeeee',
    'eeeeeeeeeeeeeeee',
)

TILES[63] = t(  # Desert Rock: red sandstone boulder
    'eeeeeeeeeeeeeeee',
    'eeeeec44cceeeeee',
    'eeec4cc4cc4ceeee',
    'eec4ccc44ccc4cee',
    'ec4ccc4444ccc4ce',
    'c4cc4444444cccce',
    'c4c444c44c44cccc',
    'cc44c444444c4ccc',
    'cc44cc4444cc4ccc',
    'cc4cccc44ccccc4c',
    'cccccccccccccccc',
    'eccccc4444ccccce',
    'eecccc4444ccccce',
    'eeec4cccccc4ceee',
    'eeeec4cccc4ceeee',
    'eeeeeeeeeeeeeeee',
)

# ---- Row 8: Forest 64..71 --------------------------------------------------
TILES[64] = t(  # Forest Coast: mossy shore between water and forest
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e2e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e2e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e2e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '2828282828282828',
    '8282828282828282',
    '2828282828282828',
    '8282828282828282',
    '2828282828282828',
    '8282828282828282',
    '2828282828282828',
)

TILES[65] = t(  # Forest Ground: green/dark dither = mossy turf
    '2828282828282828',
    '8282828a82828282',
    '2828282828282828',
    '8282828282828282',
    '28282828a8282828',
    '8282828282828282',
    '28282a2828282828',
    '8282828282828282',
    '2828282828282828',
    '8282828a82828282',
    '2828282828282828',
    '8282828282828a82',
    '28282828a8282828',
    '8282828282828282',
    '2828a82828282828',
    '8282828282828282',
)

TILES[66] = t(  # Forest Vegetation: dense bright-green/green dither
    'a2a2a2a2a2a2a2a2',
    '2a2a2a2a2a2a2a2a',
    'a2aaa2aaaaa2a2a2',
    '2a2aaa2aaa2aaa2a',
    'a2a2a2aaaa2a2a2a',
    '2a2a2a2aaa2a2a2a',
    'a2a2aaaaa2aaa2a2',
    '2a2aaa2a2aaa2a2a',
    'a2a2aaa2aaaaa2a2',
    '2a2a2a2aaa2a2a2a',
    'a2aaa2aaaaa2a2a2',
    '2a2aaa2aaa2aaa2a',
    'a2a2a2aaaa2a2a2a',
    '2a2a2a2aaa2a2a2a',
    'a2a2aaaaa2aaa2a2',
    '2a2a2a2a2a2a2a2a',
)

TILES[67] = t(  # Forest Hill: dithered tree-cloaked rise on dithered grass
    '2a2a2a2a2a2a2a2a',
    'a2a2a2aaaa2a2a2a',
    '2a2aaaa66aaa2a2a',
    'a2aaaa6666aaaa2a',
    '2aaaaaa66aaaaaa2',
    'aaaaaaaaaaaaaaaa',
    '6a6a6a6a6a6a6a6a',
    'a6a6a6a6a6a6a6a6',
    '6a6a6a6a6a6a6a6a',
    'aaaaaaaaaaaaaaaa',
    'aaaaaaa66aaaaaaa',
    'aaaaa666666aaaaa',
    'aa266666666662aa',
    '2a26666666662a2a',
    'a2a266666662a2a2',
    '2a2a2a2a2a2a2a2a',
)

TILES[68] = t(  # Forest Peak: pine canopy over snowy peak
    '2a2a2a2a2a2a2a2a',
    'a2a2a2aaaa2a2a2a',
    '2a2aaaaffaaa2a2a',
    'a2aaaaf7f7faaa2a',
    '2aaaaf7f8f7faaa2',
    'aaaaf78f8f87aaaa',
    'aaaf78ff8f78faaa',
    'aaf78fffffff8aaa',
    'a78fffff7878787a',
    '787f8787878787a8',
    '8787878787878778',
    '7878787878787877',
    '8787878787878787',
    '7887787787787878',
    '2a2a2a2a2a2a2a2a',
    'a2a2a2a2a2a2a2a2',
)

TILES[69] = t(  # Forest Tree: lush deciduous
    '22222aaa2222a222',
    '2222aaaaa2aaaa22',
    '222aaaaaaaaaaa22',
    '22aaa2aaaaaaaaa2',
    '2aaaaaaaa2aaaaa2',
    '2aaa2aaaaaaaaaa2',
    '2aaaaaa2aaaaaaa2',
    '22aaaaaaaaaaaa22',
    '222aaaaaaaaaa222',
    '22222aa66aa22222',
    '2222226666222222',
    '2222266666622222',
    '2222266666622222',
    '2222266666622222',
    '2226666666666222',
    '2222222222222222',
)

TILES[70] = t(  # Forest Bush: berry bush
    '2222222222222222',
    '22222222a2222222',
    '2222222aaaa22222',
    '222222aac4caa222',
    '22222aaaaaaaaa22',
    '22a2aac4aac4aa22',
    '22aaaaaaaaaaa222',
    '2aaac4aaaa4caa22',
    '2aaaaaaaaaaaaa22',
    '22aaaa4caaaaa222',
    '222aaaaaaaaa2222',
    '2222aaaaaaa22222',
    '22222aaaaa222222',
    '2222226662222222',
    '2222226662222222',
    '2222222222222222',
)

TILES[71] = t(  # Forest Rock: moss-covered boulder
    '2222222222222222',
    '2222222222222222',
    '2222227777222222',
    '222226aaaaa62222',
    '22226aaaaaaa6222',
    '2227aa8aaa8aa722',
    '227aa8888888aa72',
    '27aaa8aaaaa8aaa2',
    '27aaaaaaaaaaaaa2',
    '2788aaaaaaaaa882',
    '2788888888888882',
    '2788888888888882',
    '2278888888888722',
    '2222288888882222',
    '2222222222222222',
    '2222222222222222',
)

# ---- Row 9: Deep Forest 72..79 ---------------------------------------------
TILES[72] = t(  # DeepForest Coast: peaty/dark waterline
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '0202020202020202',
    '2020202020202020',
    '0202020202020202',
    '2020202020202020',
    '0202020202020202',
    '2020202020202020',
    '0202020202020202',
    '2020202020202020',
    '0202020202020202',
)

TILES[73] = t(  # DeepForest Ground: dark green/black dither = shadow floor
    '0202020202020202',
    '2020202020202020',
    '0202022020202020',
    '2020202020202020',
    '0202020202020202',
    '2020202020220202',
    '0202020202020202',
    '2020202020202020',
    '0202020202020202',
    '2020202220202020',
    '0202020202020202',
    '2020202020202020',
    '0202020202022202',
    '2020202020202020',
    '0202020202020202',
    '2020202020202020',
)

TILES[74] = t(  # DeepForest Vegetation: dense black/green canopy
    '0202020202020202',
    '2020a02020a02020',
    '0a020a0a0a020a02',
    '2020a0a0a0a02020',
    '0a020a0a0a020a02',
    '2020a020a02a02a0',
    '0a020a0a0a020a02',
    '2020a0a0a0a02020',
    '0a020a0a0a020a02',
    '2020a020a02a02a0',
    '0a020a0a0a020a02',
    '2020a0a0a0a02020',
    '0a020a0a0a020a02',
    '2020a020a02a02a0',
    '0a020a020a020a02',
    '2020202020202020',
)

TILES[75] = t(  # DeepForest Hill: pine-clad slope on shadow ground
    '0202020202020202',
    '2020a020a0202020',
    '02a02aaa2aa02020',
    '2aaa0aaaaaaaa020',
    'a0aaaaaaaaaaaaa0',
    '2aaaa202a202aaaa',
    '0aa20aaaaa20aa02',
    '2a20aaa6aaa20a20',
    '0202aa66666aa202',
    '2020a266666220a0',
    '0202a266666220a2',
    '2020a266666220a0',
    '0202a266666220a2',
    '2020a266666220a0',
    '0202020266220202',
    '2020202020202020',
)

TILES[76] = t(  # DeepForest Peak: snowy pine peak with gradient
    '0202020202020202',
    '2020a02faf02a020',
    '02a02af7f7fa02a2',
    '2a20af7f8f7fa202',
    '0aaa7f78878f7a0a',
    '2aa7f78f8f878f72',
    'af78f87878f87878',
    '7f8787878787878a',
    '8787878787878787',
    '78787878a8787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7887787887787887',
    '0202020202020202',
    '2020202020202020',
)

TILES[77] = t(  # DeepForest Tree: tall pine
    '22222222a2222222',
    '2222222a2a222222',
    '222222a222a22222',
    '2222222aaa222222',
    '222222a222a22222',
    '22222a22222a2222',
    '222222aaaaa22222',
    '222222a222a22222',
    '22222a22222a2222',
    '2222a2222222a222',
    '222222aaaaa22222',
    '222222a222a22222',
    '22222a22222a2222',
    '2222226662222222',
    '2222266666222222',
    '2222226662222222',
)

TILES[78] = t(  # DeepForest Bush: dark fern
    '2222222222222222',
    '22222a22222a2222',
    '2222a2a222a2a222',
    '2222a2a222a2a222',
    '222a2a2a2a2a2a22',
    '222a2aaa2aaa2a22',
    '2a22a2a222a2a22a',
    '2a2a2a2aaa2a2a2a',
    '22a2aaaaaaaaa2a2',
    '22aaaaaaaaaaaaa2',
    '222aaaaaaaaaaa22',
    '2222aaaaaaaaa222',
    '222226aaaaa62222',
    '2222266aaa662222',
    '2222226666222222',
    '2222222222222222',
)

TILES[79] = t(  # DeepForest Rock: dark mossy boulder
    '2222222222222222',
    '2222220880222222',
    '2222088aa8802222',
    '22208aaaa8aa8022',
    '208aaa8a8aaaa802',
    '08a888888a8aaa80',
    '08a8000888888a80',
    '8a800a888a888aa0',
    '8a8a8a8a888aa8a8',
    '8aa888aa8a8aa8a8',
    '8a888a888a8888a8',
    '08aa888888a888a0',
    '08a8a8a8a8a8a800',
    '008a888a8a888800',
    '00088888888800ee',
    '2222222222222222',
)

# ---- Row 10: Icy Tundra 80..87 ---------------------------------------------
TILES[80] = t(  # Tundra Coast: dithered icy shore between water and snow
    '9b9b9b9b9b9b9b9b',
    'b9b9b9b9b9b9b9b9',
    '9b9b9b9b9b9b9b9b',
    'b9b9b9b9b9b9b9b9',
    '9b9b9b9b9b9b9b9b',
    'b9b9b9b9b9b9b9b9',
    '9b9b9b9b9b9b9b9b',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
)

TILES[81] = t(  # Tundra Ground: white/light-gray dither = soft snow
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7fbf7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7fbf7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7fbf7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7fbf7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7fbf7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7fbf',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
)

TILES[82] = t(  # Tundra Vegetation: cyan/white dither = frost patches
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
)

TILES[83] = t(  # Tundra Hill: snowy hill with ice patches
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7fffff7f7f7',
    '7f7f7ffbbbff7f7f',
    'f7f7fbbfffbbf7f7',
    '7f7fbffbffffbf7f',
    'f7fbffffffffbf77',
    '7fbfbffbffffffbf',
    'fbfffffffffffbff',
    '7fbffbffffffffbf',
    'f7fbffffffffbf77',
    '7f7fbffbffffbf7f',
    'f7f7fbbfffbbf7f7',
    '7f7f7ffbbbff7f7f',
    'f7f7f7fffff7f7f7',
    '7f7f7f7f7f7f7f7f',
)

TILES[84] = t(  # Tundra Peak: dithered snow peak gradient
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7fff7f7f7f',
    'f7f7f7fffff7f7f7',
    '7f7f7ffbbbff7f7f',
    'f7f7fbb7b7bbf7f7',
    '7f7fbb7888b7bf7f',
    'f7fbb78ff8b7bbf7',
    '7fbb78ffff87bbf7',
    'fbb78ffffff87bbf',
    'bb787f7f7f7f8bb7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7878787878787878',
    '8787878787878787',
)

TILES[85] = t(  # Tundra Tree: snowy pine
    'ffffffffffffffff',
    'fffffffafffffffe',
    'ffffffafafffffff',
    'fffffffafffffeff',
    'ffffffafafffffff',
    'fffffaaaaafffeff',
    'ffffffafafffffff',
    'fffffaafaafffeff',
    'ffffaaffffaafefe',
    'fffffafafafffeff',
    'ffffaaaffffaffff',
    'ffff6afffaa6ffff',
    'ffffff666fffffff',
    'fffff66666ffffff',
    'ffffff666fffffff',
    'ffffffffffffffff',
)

TILES[86] = t(  # Tundra Bush: frosted shrub
    'ffffffffffffffff',
    'ffffffffffffffff',
    'fffffffffffffeff',
    'fffffffabffefffe',
    'ffffffaaffffffff',
    'fffffabbabffffff',
    'fffabaffabaffeff',
    'ffabaffffabaeefe',
    'ffabffffafabffff',
    'ffaabaaaaabaffef',
    'fffabbbbabffffff',
    'fffffabbafffffff',
    'ffffffabffefffff',
    'ffffffffffffffff',
    'ffffffffffffffff',
    'ffffffffffffffff',
)

TILES[87] = t(  # Tundra Rock: ice-glazed rock
    'ffffffffffffffff',
    'ffffffffffffffff',
    'ffffffbbbbffffff',
    'fffffbbbbbbfffff',
    'ffffbb7bbb7bffff',
    'fffbbbbbbb7bbfff',
    'ffbbb7b8b8bb7bff',
    'fbbb7b8888b7bbbf',
    'fbb7b8888888bb7f',
    'fbb7888888888b7f',
    'fbbb888888888b7f',
    'fbbbb88888888bff',
    'ffbbbb888888bfff',
    'fffbbbb8888bffff',
    'ffffbbbbbbffffff',
    'fffffbbbbbffffff',
)

# ---- Row 11: Volcanic 88..95 -----------------------------------------------
TILES[88] = t(  # Volcanic Coast: dark ash dither at water's edge
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
)

TILES[89] = t(  # Volcanic Ground: charcoal/black dither
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080408080808',
    '8080808080808080',
    '0808080808080808',
    '8084808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
)

TILES[90] = t(  # Volcanic Vegetation: lava-veined ash dither
    '8080808080808080',
    '0c0c08080c0c0808',
    '4c4c08084c4c0808',
    '0c0c4c4c0c0c4c4c',
    '8080cccc8080cccc',
    '0808c4c40808c4c4',
    '8080cccc8080cccc',
    '0c0c4c4c0c0c4c4c',
    '4c4c08084c4c0808',
    '0c0c08080c0c0808',
    '8080808080808080',
    '0808c4c40808c4c4',
    '8080cccc8080cccc',
    '0c0c4c4c0c0c4c4c',
    '4c4c08084c4c0808',
    '0c0c08080c0c0808',
)

TILES[91] = t(  # Volcanic Hill: lava-rock pile on ash
    '8080808080808080',
    '0808084cc4080808',
    '80804cc4cc480808',
    '0804cc44cccc4808',
    '804cc4444444cc40',
    '4cc4444cccc44cc4',
    'c44cc4cccccc44cc',
    '4cccccc4444cccc4',
    'cccc44ccccccccc4',
    '4cccccc44cccccc4',
    'c4cccccccccccc4c',
    'cc4cccccccccc4cc',
    '8c4ccccccccc4c80',
    '08c4cccccccc4c08',
    '808c4ccccccc4080',
    '8080808080808080',
)

TILES[92] = t(  # Volcanic Peak: bright lava spire dithered
    '8080808080808080',
    '0808084c4c080808',
    '80808c4cc4c80808',
    '0808c4cccccc4808',
    '808c4ccccccccc40',
    '80c4cccceeecccc4',
    '0c4ccceeeeeccccc',
    'c4cceeeeeeeeeccc',
    'cceeeeeeeeeeeecc',
    'eeeeeeeeeeeeeeee',
    'ecececececececec',
    'cecececececececc',
    'ccecececececeecc',
    '4ccccecececeecc4',
    '8080808080808080',
    '0808080808080808',
)

TILES[93] = t(  # Volcanic Tree: dead twisted tree
    '8888888888888888',
    '6888888886888888',
    '8688888668888888',
    '866888666888c488',
    '8866666666884c88',
    '888c6666666c4888',
    '8888c66c66c48888',
    '8888666c6666e888',
    '8884c66c666c4888',
    '88884c6666c48888',
    '888884c66c488888',
    '88888866c4888888',
    '88888866c4888888',
    '88888866c4888888',
    '88888866c4888888',
    '88888866c4888888',
)

TILES[94] = t(  # Volcanic Bush: charred shrub
    '8888888888888888',
    '8888888c48888888',
    '8888884c4c488888',
    '888884cc4cc48888',
    '88884cc44cc48888',
    '888c4cc44cc4c888',
    '88c4cccc4ccc4c88',
    '8c4ccccccccc4c88',
    '8cc44ccccc44cc88',
    '88cc4cccccc4cc88',
    '888cccccc4ccc888',
    '8888cccccccc8888',
    '8888c4ccccc48888',
    '88888c4cccc88888',
    '888888c4c4888888',
    '8888888888888888',
)

TILES[95] = t(  # Volcanic Rock: obsidian
    '8888888888888888',
    '8800888888888888',
    '8800888888888008',
    '8000888888888008',
    '8000088888880088',
    '8000008888880008',
    '8000080888800088',
    '8000088000800808',
    '8000088000800088',
    '8000080000800088',
    '8000800800000088',
    '8000888800000888',
    '8800888880008888',
    '8888888888888888',
    '8888888888888888',
    '8888888888888888',
)

# ---- Row 12: Mountains 96..103 ---------------------------------------------
TILES[96] = t(  # Mountains Coast: rocky gravel shore
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
)

TILES[97] = t(  # Mountains Ground: dithered rocky terrain
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878f87878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787f78787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787f78',
    '8787878787878787',
    '7878787878787878',
    '8787878787f78787',
    '7878787878787878',
    '8787878787878787',
)

TILES[98] = t(  # Mountains Vegetation: alpine grass tufts on rock
    '7878787878787878',
    '8787a87878a87878',
    '787a787a78787a78',
    '8a878a87878a8787',
    '78787a78a8787878',
    '8787878787a87878',
    '7a787878787a7878',
    '8787a8787a878787',
    '78787a7878a87878',
    '8a87878787878787',
    '7878a878a8787878',
    '8787878787a87a87',
    '78a87a78787a7878',
    '8787878a87878787',
    '7a78787878787a78',
    '8787a8787878a878',
)

TILES[99] = t(  # Mountains Hill: rocky ridge with snow caps
    '7878787878787878',
    '8787878787878787',
    '7878787f78787878',
    '8787878fff878787',
    '78787f78fff87878',
    '8787f78fff8f8787',
    '787f78ff8f8f7878',
    '8f78ff8f8f8f8787',
    'f78f8f8f8f8f8f87',
    '7f8f8f8f8f8f8f78',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
    '8787878787878787',
    '7878787878787878',
)

TILES[100] = t(  # Mountains Peak: tall snow-capped peak gradient
    '7878787878787878',
    '8787878fff878787',
    '787878f7f7f87878',
    '8787f7fffff7f787',
    '787f7fff7fff7878',
    '8f7fff7f7f7f8f87',
    'f7fff7f7f7f8f878',
    '7fff7f7f7f8f8787',
    'fff8f8f8f8f8f878',
    'ff8f8f8f8f8f8787',
    'f8f8f8f8f8f8f878',
    '8f8f8f8f8f8f8787',
    'f8f8f8f8f8f8f878',
    '8f8f8f8f8f8f8787',
    '8787878787878787',
    '7878787878787878',
)

TILES[101] = t(  # Mountains Tree: hardy alpine pine
    '7777777a7777777a',
    '777777a7a777777a',
    '77777aaaaa77777a',
    '7777aa777aa77777',
    '7777aa7a7aa77777',
    '777aa7aaa7aa7777',
    '77aa77a7a77aa777',
    '777aa7aaa7aa7777',
    '7777aa7a7aa77777',
    '777aaaaaaaaa7777',
    '7777aaaaaaa77777',
    '77777aaaaa777777',
    '777776aaa6777777',
    '7777766666777777',
    '7777776667777777',
    '7777777777777777',
)

TILES[102] = t(  # Mountains Bush: alpine shrub
    '7777777777777777',
    '7777777777777777',
    '7777777a77777777',
    '777777aaa7777777',
    '77777aa6aa777777',
    '7777aa666aa77777',
    '777aa66666aa7777',
    '77aa6666666aa777',
    '777aa66666aa7777',
    '7777aa666aa77777',
    '77777aa6aa777777',
    '777777aaa7777777',
    '7777777a77777777',
    '7777777777777777',
    '7777777777777777',
    '7777777777777777',
)

TILES[103] = t(  # Mountains Rock: massive boulder
    '7777777777777777',
    '7777887878887777',
    '777878fff7f87777',
    '77787ffff7ff8777',
    '7787ffff8fff8777',
    '787f8fff7f7ff877',
    '78ff7ff8ff7f8f77',
    '8fff8ffff8fff8f8',
    '8fff8888888888f8',
    '8888888888888888',
    '8888888888888888',
    '8888888888888888',
    '8888888888888888',
    '7888888888888887',
    '7777788888887777',
    '7777777777777777',
)

# ---- Per-biome town tilesets (rows 13..19) ---------------------------------
# Each biome gets a contiguous row of 8 town tiles in this fixed order:
#   Floor, Wall, WindowWall, DoorClosed, DoorOpen, Bed, Table, Chair
# So tile id of biome B's town role R = 104 + 8*B + R.

# ---- Row 13: Plains town 104..111 ------------------------------------------
TILES[104] = t(  # Plains Town Floor: dithered wood plank
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
)

TILES[105] = t(  # Plains Town Wall: dithered stone block with dark seams
    '8888888888888888',
    '8787878887878787',
    '7878787887878788',
    '8787878887878787',
    '7878787887878788',
    '8787878887878787',
    '7878787887878788',
    '8888888888888888',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8888888888888888',
)

TILES[106] = t(  # Plains Town Window Wall: stone with cyan window
    '8888888888888888',
    '8777777777777778',
    '8777777777777778',
    '8788888888888778',
    '878bbbbbbbbbb878',
    '8783333333333878',
    '8783333333333878',
    '8783333333333878',
    '8783333333333878',
    '8783333333333878',
    '8783333333333878',
    '878bbbbbbbbbb878',
    '8788888888888778',
    '8777777777777778',
    '8777777777777778',
    '8888888888888888',
)

TILES[107] = t(  # Plains Town Door Closed: planked wood door
    '8888888888888888',
    '8666666666666668',
    '866ee666666e6668',
    '866e6e66666e6668',
    '866e6e66666e6668',
    '866e6e66ee6e6668',
    '866e6e66e66e6668',
    '866e6e66e66e6668',
    '866e6e66e66e6668',
    '866e6e66e6ee6668',
    '866e6e66666e6668',
    '866e6e66666e66e8',
    '866e6e66666e66e8',
    '866ee666666e6668',
    '8666666666666668',
    '8888888888888888',
)

TILES[108] = t(  # Plains Town Door Open: open doorway
    '8888888888888888',
    '8888888888888888',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8888888888888888',
    '8888888888888888',
)

TILES[109] = t(  # Plains Town Bed: linen + red blanket
    '8888888888888888',
    '8666666666666668',
    '86fffff66c4c4c68',
    '86fffff64c4c4c68',
    '86fffff6cccccc68',
    '86fffff64c4c4c68',
    '8666666666666668',
    '866cccccccccc668',
    '8664c4c4c4c4c668',
    '866cccccccccc668',
    '8664c4c4c4c4c668',
    '866cccccccccc668',
    '8664c4c4c4c4c668',
    '866cccccccccc668',
    '8666666666666668',
    '8888888888888888',
)

TILES[110] = t(  # Plains Town Table: oak top
    '7777777777777777',
    '7777777777777777',
    '8888888888888888',
    '8666666666666668',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '866eeeeeeeeeee68',
    '8666666666666668',
    '8888888888888888',
    '7766777777776677',
    '7766777777776677',
    '7766777777776677',
    '7766777777776677',
    '7777777777777777',
    '7777777777777777',
)

TILES[111] = t(  # Plains Town Chair: oak chair
    '7777777777777777',
    '7777666666667777',
    '7776e66666e66777',
    '7776e66666e66777',
    '7776e66666e66777',
    '7776666666666777',
    '7776666666666777',
    '7776666666666777',
    '7777666666667777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777666666667777',
    '7777777777777777',
)

# ---- Row 14: Desert town 112..119 ------------------------------------------
TILES[112] = t(  # Desert Town Floor: dithered terracotta tile
    '6666666666666666',
    '6c4c4c46c4c4c466',
    '64c4c4c64c4c4c66',
    '6c4c4c46c4c4c466',
    '64c4c4c64c4c4c66',
    '6666666666666666',
    'c4c4c46c4c4c46c4',
    '4c4c4c64c4c4c64c',
    'c4c4c46c4c4c46c4',
    '4c4c4c64c4c4c64c',
    '6666666666666666',
    '6c4c4c46c4c4c466',
    '64c4c4c64c4c4c66',
    '6c4c4c46c4c4c466',
    '64c4c4c64c4c4c66',
    '6666666666666666',
)

TILES[113] = t(  # Desert Town Wall: dithered adobe brick
    '6666666666666666',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6666666666666666',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    '6666666666666666',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '6666666666666666',
)

TILES[114] = t(  # Desert Town Window Wall: adobe with arched window
    '6666666666666666',
    '6eeeeeeeeeeeeee6',
    '6eeeeeeeeeeeeee6',
    '6eee666666666ee6',
    '6ee6cccccccc6ee6',
    '6e6c33333333c6e6',
    '6e6c33333333c6e6',
    '6e6c33333333c6e6',
    '6e6c33333333c6e6',
    '6e6c33333333c6e6',
    '6e6c33333333c6e6',
    '6e6cccccccccc6e6',
    '6ee6666666666ee6',
    '6eeeeeeeeeeeeee6',
    '6eeeeeeeeeeeeee6',
    '6666666666666666',
)

TILES[115] = t(  # Desert Town Door Closed: adobe arched door
    '6666666666666666',
    '6eeeeeeeeeeeeee6',
    '6eee666666666ee6',
    '6ee6c66666666e66',
    '6ee6c666c66666e6',
    '6ee6c66666666e66',
    '6ee6c666c66666e6',
    '6ee6c66666666e66',
    '6ee6c666c66666e6',
    '6ee6c66666666e66',
    '6ee6c666c66666e6',
    '6ee6c66666666e66',
    '6ee6c666c66666e6',
    '6ee6c66666666e66',
    '6eee666666666ee6',
    '6666666666666666',
)

TILES[116] = t(  # Desert Town Door Open: open arch
    '6666666666666666',
    '6eeeeeeeeeeeeee6',
    '6eee666666666ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6ee6000000000ee6',
    '6666000000000666',
)

TILES[117] = t(  # Desert Town Bed: woven mat with cushion
    '6666666666666666',
    '6eeeeeeeeeeeeee6',
    '6e6666cccccccce6',
    '6e6c6cc444c44ce6',
    '6e6c6c4c4c4c4ce6',
    '6e6c6cccccccccee',
    '6666666666666666',
    '6eeeeeeeeeeeeee6',
    '6e666666666666e6',
    '6ec6cccccccc6ee6',
    '6ec6c444c4c46ee6',
    '6ec6cc4c4cc46ee6',
    '6ec6c4c4c4c46ee6',
    '6ec6cccccccc6ee6',
    '6e666666666666e6',
    '6666666666666666',
)

TILES[118] = t(  # Desert Town Table: terracotta low table
    '6666666666666666',
    '6666666666666666',
    '6cccccccccccccc6',
    '6c44c44c44c44cc6',
    '6c4cc4cc4cc4cc46',
    '6c44c44c44c44cc6',
    '6cccccccccccccc6',
    '6666666666666666',
    '6e6e6e6e6e6e6e6e',
    '6e6e6e6e6e6e6e6e',
    '6666666666666666',
    '6e66666666666e66',
    '6e66666666666e66',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
)

TILES[119] = t(  # Desert Town Chair: cushioned stool
    '6666666666666666',
    '666666cccc666666',
    '6666c4cccc4c6666',
    '6666c4cccc4c6666',
    '6666c4444c4c6666',
    '6666c4cccc4c6666',
    '6666cccccccc6666',
    '666eeeeeeeeee666',
    '666e66666666e666',
    '666e66666666e666',
    '666e66666666e666',
    '666e66666666e666',
    '6666666666666666',
    '666e6666666e6666',
    '666e6666666e6666',
    '6666666666666666',
)

# ---- Row 15: Forest town 120..127 ------------------------------------------
TILES[120] = t(  # Forest Town Floor: dithered rough plank
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
    '6e6e6e6e6e6e6e6e',
    'e6e6e6e6e6e6e6e6',
    '8888888888888888',
)

TILES[121] = t(  # Forest Town Wall: dithered stacked logs
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8888888888888888',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8888888888888888',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8888888888888888',
    '6868686868686868',
    '8686868686868686',
    '6868686868686868',
    '8888888888888888',
)

TILES[122] = t(  # Forest Town Window Wall: log wall with shuttered window
    '6666666666666666',
    '6e66666666e66666',
    '8888888888888888',
    '666e6666666e6666',
    '6e6666666666e666',
    '8888888888888888',
    '6666e8888888e666',
    '666683333333e666',
    '666683333333e666',
    '666683333333e666',
    '666683333333e666',
    '6666e8888888e666',
    '8888888888888888',
    '66e666666666e666',
    '6666666e66666e66',
    '8888888888888888',
)

TILES[123] = t(  # Forest Town Door Closed: planked door
    '8888888888888888',
    '8666666666666668',
    '8666666666666668',
    '866e66e66666e668',
    '866e66e66666e668',
    '8666666666666668',
    '866e66e66e66e668',
    '866e66e66e66e668',
    '8666666666666668',
    '866e66e66e66e668',
    '866e66e66e66e668',
    '8666666666666668',
    '866e66e66e66ee68',
    '866666666666e668',
    '8666666666666668',
    '8888888888888888',
)

TILES[124] = t(  # Forest Town Door Open: open arch
    '8888888888888888',
    '8888888888888888',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8888888888888888',
    '8888888888888888',
)

TILES[125] = t(  # Forest Town Bed: leafy mattress with hide
    '8888888888888888',
    '8666666666666668',
    '866aaaaaa6666668',
    '866aaaaaa6666668',
    '866aaaaaa6666668',
    '866aaaaaa6666668',
    '8666666666666668',
    '866666666666e668',
    '866c4c4c4c44ee68',
    '8664c4c4c4c4ee68',
    '866c4c4c4c44ee68',
    '8664c4c4c4c4ee68',
    '866c4c4c4c44ee68',
    '866666666666e668',
    '8666666666666668',
    '8888888888888888',
)

TILES[126] = t(  # Forest Town Table: log table
    '8888888888888888',
    '8888888888888888',
    '6666666666666666',
    '6e6666e6666666e6',
    '666e6666e66666e6',
    '6666e66666e66666',
    '66e666e66666e666',
    '6666666666666666',
    '8888888888888888',
    '8888888888888888',
    '6666666666666666',
    '6e66666666666e66',
    '6e66666666666e66',
    '8888888888888888',
    '7777777777777777',
    '7777777777777777',
)

TILES[127] = t(  # Forest Town Chair: stump stool
    '7777777777777777',
    '7777777777777777',
    '7777666666667777',
    '7776e6e6e6e66777',
    '7776666666666777',
    '7776e6e6e6e66777',
    '7776666666666777',
    '7777666666667777',
    '7777677777767777',
    '7777677777767777',
    '7777677777767777',
    '7777666666667777',
    '7777677777767777',
    '7777677777767777',
    '7777666666667777',
    '7777777777777777',
)

# ---- Row 16: Deep Forest town 128..135 -------------------------------------
TILES[128] = t(  # DeepForest Town Floor: dithered dark plank
    '0000000000000000',
    '6868686868686868',
    '8686868686868686',
    '0000000000000000',
    '6868686868686868',
    '8686868686868686',
    '0000000000000000',
    '6868686868686868',
    '8686868686868686',
    '0000000000000000',
    '6868686868686868',
    '8686868686868686',
    '0000000000000000',
    '6868686868686868',
    '8686868686868686',
    '0000000000000000',
)

TILES[129] = t(  # DeepForest Town Wall: dithered dark stone with moss
    '8888888888888888',
    '8080808080808080',
    '0808080a08080808',
    '8080808080808080',
    '0808080808080808',
    '80808a8080808080',
    '0808080808080808',
    '8888888888888888',
    '0808080808080808',
    '80808080808a8080',
    '0808080808080808',
    '8080a08080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8888888888888888',
)

TILES[130] = t(  # DeepForest Town Window Wall: dark stone with cold window
    '8888888888888888',
    '8000000000000008',
    '8000000000000008',
    '8000888888880008',
    '800833333333a008',
    '800833333333a008',
    '8008333333333008',
    '8008333333333008',
    '8008333333333008',
    '8008333333333008',
    '800a3333333a3008',
    '800888888888a008',
    '8008888888888008',
    '8000000000000008',
    '8000000000000008',
    '8888888888888888',
)

TILES[131] = t(  # DeepForest Town Door Closed: dark plank door
    '8888888888888888',
    '8666666666666668',
    '866888666688866e',
    '866868666686866e',
    '866868866686866e',
    '866868666686866e',
    '866868666686866e',
    '866868666686866e',
    '866868666686866e',
    '866868666686866e',
    '866868666686866e',
    '866868666686866e',
    '866868866686866e',
    '866888666688866e',
    '8666666666666668',
    '8888888888888888',
)

TILES[132] = t(  # DeepForest Town Door Open: open
    '8888888888888888',
    '8888888888888888',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8800000000000088',
    '8888888888888888',
    '8888888888888888',
)

TILES[133] = t(  # DeepForest Town Bed: ferns and dark hide
    '8888888888888888',
    '8666666666666668',
    '866a2a2a2666666e',
    '8662a2a2a6666666',
    '866a2a2a2666666e',
    '8662a2a2a6666666',
    '8666666666666668',
    '866066666666666e',
    '8666666666666668',
    '866066666666666e',
    '8666666666666668',
    '866066666666666e',
    '8666666666666668',
    '866066666666666e',
    '8666666666666668',
    '8888888888888888',
)

TILES[134] = t(  # DeepForest Town Table: dark log
    '0000000000000000',
    '0000000000000000',
    '8888888888888888',
    '6e6666666e666666',
    '666e6666666e6666',
    '666666e6666666e6',
    '6e6666e6666666e6',
    '666666666e666666',
    '8888888888888888',
    '0000000000000000',
    '8866666666666688',
    '8666666666666668',
    '8666666666666668',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
)

TILES[135] = t(  # DeepForest Town Chair: dark stump
    '0000000000000000',
    '0000000000000000',
    '0000888888880000',
    '00086666666e8000',
    '0008666666e68000',
    '00086e66666e8000',
    '00086e66666e8000',
    '00086666666e8000',
    '0000888888880000',
    '0000866666e80000',
    '0000866666e80000',
    '0000866666680000',
    '0000866666e80000',
    '0000866666e80000',
    '0000888888880000',
    '0000000000000000',
)

# ---- Row 17: Icy Tundra town 136..143 --------------------------------------
TILES[136] = t(  # Tundra Town Floor: dithered packed snow
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
    'f7f7f7f7f7f7f7f7',
    '7f7f7f7f7f7f7f7f',
)

TILES[137] = t(  # Tundra Town Wall: dithered ice block with cyan seams
    'bbbbbbbbbbbbbbbb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bbbbbbbbbbbbbbbb',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bfbfbfbfbfbfbfbf',
    'fbfbfbfbfbfbfbfb',
    'bbbbbbbbbbbbbbbb',
)

TILES[138] = t(  # Tundra Town Window Wall: ice with frosted window
    'bbbbbbbbbbbbbbbb',
    'bfffffffffffffff',
    'bfffffffffffffff',
    'bffffbbbbbbbffff',
    'bfffb333333bffff',
    'bfffb33ff33bffff',
    'bfffb3ffff3bffff',
    'bfffb3ffff3bffff',
    'bfffb3ffff3bffff',
    'bfffb3ffff3bffff',
    'bfffb33ff33bffff',
    'bfffb333333bffff',
    'bffffbbbbbbbffff',
    'bfffffffffffffff',
    'bfffffffffffffff',
    'bbbbbbbbbbbbbbbb',
)

TILES[139] = t(  # Tundra Town Door Closed: ice slab door
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bbfffffffffffffb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbffbfffffbfffbb',
    'bbfffffffffffffb',
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
)

TILES[140] = t(  # Tundra Town Door Open: open
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bb00000000000bbb',
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
)

TILES[141] = t(  # Tundra Town Bed: fur bedroll
    'bbbbbbbbbbbbbbbb',
    'bfffffffffffffff',
    'bf66666666666666',
    'bf6e6e6e6e6e6666',
    'bf66666666666666',
    'bf6e6e6e6e6e6666',
    'bfffffffffffffff',
    'bfffffffffffffff',
    'bf66666666666666',
    'bf6e6e6e6e6e6666',
    'bf66666666666666',
    'bf6e6e6e6e6e6666',
    'bf66666666666666',
    'bf6e6e6e6e6e6666',
    'bfffffffffffffff',
    'bbbbbbbbbbbbbbbb',
)

TILES[142] = t(  # Tundra Town Table: ice block table
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bbfffffffffffffb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbfffffffffffffb',
    'bbbbbbbbbbbbbbbb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbfbbbbbbbbbbbfb',
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
)

TILES[143] = t(  # Tundra Town Chair: ice block stool
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bbbbffffffffbbbb',
    'bbbbfbbbbbbfbbbb',
    'bbbbfbbbbbbfbbbb',
    'bbbbfbbbbbbfbbbb',
    'bbbbfbbbbbbfbbbb',
    'bbbbffffffffbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbfbbbbfbbbbb',
    'bbbbbbbbbbbbbbbb',
    'bbbbbbbbbbbbbbbb',
)

# ---- Row 18: Volcanic town 144..151 ----------------------------------------
TILES[144] = t(  # Volcanic Town Floor: dithered dark stone with red veins
    '8888888888888888',
    '8080808888080808',
    '0808088884080808',
    '8080804c40808088',
    '0808884c44888080',
    '8080808888080808',
    '0808080808080808',
    '8888888888888888',
    '0808080808080808',
    '80808088c4808080',
    '08080884cc480888',
    '8080808884c40808',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8888888888888888',
)

TILES[145] = t(  # Volcanic Town Wall: dithered obsidian
    '8888888888888888',
    '8080808880808080',
    '0808080880808080',
    '8080808880808080',
    '0808080880808080',
    '8080808880808080',
    '0808080880808080',
    '8888888888888888',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8080808080808080',
    '0808080808080808',
    '8888888888888888',
)

TILES[146] = t(  # Volcanic Town Window Wall: obsidian with lava window
    '8888888888888888',
    '8000000000000008',
    '8000000000000008',
    '8000444444440008',
    '800c44444444c008',
    '800c4cccccc4c008',
    '800c4eeeeec4c008',
    '800c4eeeeec4c008',
    '800c4eeeeec4c008',
    '800c4eeeeec4c008',
    '800c4cccccc4c008',
    '800c44444444c008',
    '8000444444440008',
    '8000000000000008',
    '8000000000000008',
    '8888888888888888',
)

TILES[147] = t(  # Volcanic Town Door Closed: iron-plated door
    '8888888888888888',
    '8000000000000008',
    '8077777777777008',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8070707707070708',
    '8077777777777008',
    '8000000000000008',
    '8888888888888888',
)

TILES[148] = t(  # Volcanic Town Door Open: open
    '8888888888888888',
    '8000000000000008',
    '8000000000000008',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '0000000000000000',
    '8000000000000008',
    '8000000000000008',
    '8888888888888888',
)

TILES[149] = t(  # Volcanic Town Bed: stone slab with hide
    '8888888888888888',
    '8000000000000008',
    '80777777ccccc008',
    '8077777744cc4008',
    '80777777cc44c008',
    '8077777744cc4008',
    '8000000000000008',
    '8077777777777008',
    '8077c7c7c7c77008',
    '80777777777ee008',
    '8077c7c7c7c77008',
    '80777777777ee008',
    '8077c7c7c7c77008',
    '8077777777777008',
    '8000000000000008',
    '8888888888888888',
)

TILES[150] = t(  # Volcanic Town Table: stone slab
    '8888888888888888',
    '8888888888888888',
    '8000000000000008',
    '8077777777777008',
    '8077777777777008',
    '8077c777777c7008',
    '8077777777777008',
    '8077777777777008',
    '8000000000000008',
    '8888888888888888',
    '8088888008888808',
    '8088888008888808',
    '8088888008888808',
    '8088888008888808',
    '8888888888888888',
    '8888888888888888',
)

TILES[151] = t(  # Volcanic Town Chair: stone stool
    '8888888888888888',
    '8888888888888888',
    '8888777777778888',
    '888707777707888c',
    '888707777707888c',
    '888707777707888c',
    '888707777707888c',
    '888707777707888c',
    '888777777777888c',
    '888807777708888c',
    '888807777708888c',
    '888807777708888c',
    '888807777708888c',
    '888807777708888c',
    '888888888888888c',
    '8888888888888888',
)

# ---- Row 19: Mountains town 152..159 ---------------------------------------
TILES[152] = t(  # Mountains Town Floor: dithered cut stone
    '7777777777777777',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7777777777777777',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7878787787878787',
    '8787878787878788',
    '7777777777777777',
)

TILES[153] = t(  # Mountains Town Wall: dithered massive blocks with snow caps
    '7777777777777777',
    '7878787f78787878',
    '8787878f87878787',
    '7878787f78787878',
    '8787878f87878787',
    '7878787787878787',
    '8787878887878787',
    '7777777777777777',
    '878787878787f878',
    '787878787878f787',
    '878787878787f878',
    '787878787878f787',
    '878787878787f878',
    '787878787878f787',
    '878787878787f878',
    '7777777777777777',
)

TILES[154] = t(  # Mountains Town Window Wall: stone with shuttered window
    '7777777777777777',
    '7888888888888887',
    '7888888888888887',
    '7888888888888887',
    '7777777777777777',
    '7777333333337777',
    '7773bbbbbbbb3777',
    '7773bbbbbbbb3777',
    '7773bbbbbbbb3777',
    '7773bbbbbbbb3777',
    '7773bbbbbbbb3777',
    '7777333333337777',
    '7777777777777777',
    '7888888888888887',
    '7888888888888887',
    '7777777777777777',
)

TILES[155] = t(  # Mountains Town Door Closed: heavy oak with iron bands
    '7777777777777777',
    '7888888888888887',
    '7866666666666687',
    '7866e66666e66687',
    '7866e66666e66687',
    '7888888888888887',
    '7866666666666687',
    '7866e66666e66687',
    '7866e66666e66687',
    '7888888888888887',
    '7866666666666687',
    '7866e66666e66687',
    '7866e66666e66687',
    '7866666666666687',
    '7888888888888887',
    '7777777777777777',
)

TILES[156] = t(  # Mountains Town Door Open: open
    '7777777777777777',
    '7888888888888887',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7800000000000087',
    '7888888888888887',
    '7777777777777777',
)

TILES[157] = t(  # Mountains Town Bed: stone bed with brown hide
    '7777777777777777',
    '7888888888888887',
    '78ffffff66666687',
    '78ffffff666e6687',
    '78ffffff66666687',
    '78ffffff666e6687',
    '7888888888888887',
    '78c66666666666c7',
    '78ce66666666ec87',
    '78c66666666666c7',
    '78ce66666666ec87',
    '78c66666666666c7',
    '78ce66666666ec87',
    '78c66666666666c7',
    '7888888888888887',
    '7777777777777777',
)

TILES[158] = t(  # Mountains Town Table: stone slab on legs
    '7777777777777777',
    '7777777777777777',
    '7888888888888887',
    '78ffffff7fffff87',
    '78ffffff7fffff87',
    '78ffffff7fffff87',
    '78ffffff7fffff87',
    '78ffffff7fffff87',
    '7888888888888887',
    '7777777777777777',
    '7788777777778877',
    '7788777777778877',
    '7788777777778877',
    '7788777777778877',
    '7777777777777777',
    '7777777777777777',
)

TILES[159] = t(  # Mountains Town Chair: stone stool
    '7777777777777777',
    '7777888888887777',
    '7778fffffffffe77',
    '7778fff7777ffe77',
    '7778ff7777ffffe7',
    '7778fff7777fffe7',
    '7778ffffffffffe7',
    '7777888888887777',
    '7778877777788777',
    '7778877777788777',
    '7778877777788777',
    '7777888888887777',
    '7778877777788777',
    '7778877777788777',
    '7777888888887777',
    '7777777777777777',
)

# Slots 160..159 reserved for future tiles
for tid in range(160, 160):
    TILES[tid] = t(*(['................'] * 16))


# ---- build atlas -----------------------------------------------------------
def parse_tile(rows: list[str]) -> list[tuple[int, int, int, int]]:
    pixels: list[tuple[int, int, int, int]] = []
    for row in rows:
        for c in row:
            idx = CHAR_TO_INDEX[c]
            pixels.append(TRANSPARENT if idx < 0 else EGA[idx])
    return pixels


def build_atlas(out_path: str) -> None:
    img = Image.new('RGBA', (ATLAS_W, ATLAS_H), TRANSPARENT)
    px = img.load()
    for tid in range(COLS * ROWS):
        rows = TILES[tid]
        col = tid % COLS
        row = tid // COLS
        ox = col * TILE
        oy = row * TILE
        tp = parse_tile(rows)
        for j in range(TILE):
            for i in range(TILE):
                px[ox + i, oy + j] = tp[j * TILE + i]
    img.save(out_path)


def build_palette_swatch(out_path: str) -> None:
    sw = 32
    img = Image.new('RGBA', (sw * 16, sw), TRANSPARENT)
    px = img.load()
    for i, color in enumerate(EGA):
        for y in range(sw):
            for x in range(sw):
                px[i * sw + x, y] = color
    img.save(out_path)


if __name__ == '__main__':
    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'tiles')
    )
    os.makedirs(out_dir, exist_ok=True)
    build_atlas(os.path.join(out_dir, 'atlas.png'))
    build_palette_swatch(os.path.join(out_dir, 'ega_palette.png'))
    print(f'Wrote atlas.png and ega_palette.png to {out_dir}')
