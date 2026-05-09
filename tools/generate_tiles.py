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

TILES[3] = t(  # Sand
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeeeeeee6e',
    'eeeeeeeeeeeeeeee',
    'e6eeeeeeeeeeeeee',
    'eeeeeeeee6eeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeee6eeeeeee',
    'e6eeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeee6eeeee',
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeee6eeeeee',
)

TILES[4] = t(  # Grass
    '2222222222222222',
    '222a2222222a2222',
    '2222222222262222',
    '6222222222222a22',
    '2222a2222222222a',
    '2222226222222222',
    '22a22222222a2222',
    '2222222222222222',
    '2222226222222226',
    '22a22222a2222222',
    '2222222222262222',
    '2226222222222a22',
    '222222a222222222',
    '22222a2222222262',
    '6222222222222222',
    '2222226222222222',
)

TILES[5] = t(  # Forest
    '2222222222222222',
    '22222222a2222222',
    '22222a2aaa222222',
    '2222aaaaaaa22222',
    '222aaaaaaaaa2222',
    '22aaa2aaa2aaa222',
    '222aaaa2aaaa2222',
    '2222aaaaaaa22222',
    '22222aa6aa222222',
    '2222222662222222',
    '2222222662222222',
    '2222222662222222',
    '2222226666222222',
    '2222266666622222',
    '2222266666622222',
    '2222222222222222',
)

TILES[6] = t(  # Hills
    '2222222222222222',
    '2222222222222222',
    '2222226e6622222e',
    '22226e6e6ee62222',
    '2226e66666666e22',
    '226e666666666e62',
    '6e666666666666e6',
    '6666e66666e66666',
    '6666666666666666',
    '266e6666e66e6622',
    '2226666666e62222',
    '22222e6e66222222',
    '2222226666222222',
    '2222226e62222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[7] = t(  # Mountains
    '2222222222222222',
    '22222222ff222222',
    '2222222f7f7f2222',
    '2222227ff8f72222',
    '222227f7888f7222',
    '22227f78ff887722',
    '2227f78fff8888a2',
    '227f78fff7f88882',
    '27f78fff7f7f8888',
    '7f78fff7f7f78888',
    '7778877777f78888',
    '8888887777778888',
    '8888888888888888',
    '8888888888888888',
    '2222222222222222',
    '2222222222222222',
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
TILES[24] = t(  # Stone Floor
    '8888888888888888',
    '8777777787777777',
    '8777777787777777',
    '8777777787777777',
    '8777777787777777',
    '8777777787777777',
    '8888888888888888',
    '7777777877777778',
    '7777777877777778',
    '7777777877777778',
    '7777777877777778',
    '7777777877777778',
    '7777777877777778',
    '8888888888888888',
    '8777777787777777',
    '8777777787777777',
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

TILES[26] = t(  # Brick Floor
    '7777777777777777',
    '7c7cccc7cccc7c77',
    '7c7cccc7cccc7c77',
    '7c7cccc7cccc7c77',
    '7777777777777777',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    '7777777777777777',
    '7c7cccc7cccc7c77',
    '7c7cccc7cccc7c77',
    '7c7cccc7cccc7c77',
    '7777777777777777',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
)

TILES[27] = TILES[4][:]  # Grass Floor: same as world grass

TILES[28] = t(  # Stone Wall
    '8888888888888888',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8888888888888888',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
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

TILES[30] = t(  # Brick Wall
    '7777777777777777',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    '7777777777777777',
    '7ccccc7cccc7cccc',
    '7ccccc7cccc7cccc',
    '7ccccc7cccc7cccc',
    '7777777777777777',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    'cccc7cccc7cccc7c',
    '7777777777777777',
    '7ccccc7cccc7cccc',
    '7ccccc7cccc7cccc',
    '7ccccc7cccc7cccc',
)

TILES[31] = t(  # Window Wall
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

TILES[34] = t(  # Bed
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

TILES[37] = t(  # Counter
    '7777777777777777',
    '8888888888888888',
    '6e6666666e666666',
    '666666e6666666e6',
    '6666666666666666',
    '666e6666666e6666',
    '8888888888888888',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
    '6666666666666666',
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
TILES[48] = t(  # Plains Coast: pale sand sprinkled with grass tufts
    'eeeeeeeeee2eeeee',
    'eeee2eeeeeeeeeee',
    'eeeeeeee2eeeeeee',
    'eeeeeeeeeeeee6ee',
    'eee2eeeeeeeeeeee',
    'eeeeeeeeeeeeeee2',
    'eeeeee6eeeeeeeee',
    'e2eeeeeeeeeeeeee',
    'eeeeeeeeeee2eeee',
    'eeeeeeeeeeeeeeee',
    'eeeee2eeeeee6eee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeee2eeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeeeee2eee',
    'eeeeeeeeeeeeeeee',
)

TILES[49] = t(  # Plains Ground: bright grass with light specks
    '2222222222222222',
    '222a22222222a222',
    '22222226222222a2',
    '2a2222222222222e',
    '2222a22222222222',
    '6222222a22222e22',
    '22222a22222222a2',
    '2222222222e22222',
    '22a2222222222e22',
    '222222a222a22222',
    '22e222222222a222',
    '2222a22222222222',
    '2222222222e2222a',
    '22a22222222222e2',
    '2222222a22222222',
    '222222222222a222',
)

TILES[50] = t(  # Plains Vegetation: tall grass and wildflowers
    '2222222222222222',
    '2a22e2a222a22e22',
    '2a2a2a2a2a2a2a22',
    '2222a2a2a2a22222',
    '22e2a2a22a2a2222',
    '2a2a2a2a2a2a2a22',
    '2222a2a22a2a2222',
    '22e22a22a22e2222',
    '2a2a2a2a2a2a2a22',
    '2222a2a22a2a2222',
    '22a22a22a22a2222',
    '2a2a2a2a2a2a2a22',
    '2222a2a22a2a22e2',
    '22e2a2a22a2a2222',
    '2a2a2a2a2a2a2a22',
    '2222222222222222',
)

TILES[51] = t(  # Plains Hill: gentle grassy mound
    '2222222222222222',
    '2222226666222222',
    '2222266a66622222',
    '222266aaaa6e2222',
    '22266aa66aa66222',
    '226aa6aaaa6aa622',
    '226a6aaaaaa6a622',
    '26aaaaaaaaaaaa62',
    '266aaaaaaaaaa662',
    '2266aaaaaaaa6622',
    '22266aaaaaa66222',
    '2226666aa66e2222',
    '22222666666e2222',
    '2222226662222222',
    '2222222222222222',
    '2222222222222222',
)

TILES[52] = t(  # Plains Peak: classic gray mountain
    '2222222222222222',
    '22222222ff222222',
    '2222222f7f7f2222',
    '2222227ff8f72222',
    '222227f7888f7222',
    '22227f78ff887722',
    '2227f78fff8888a2',
    '227f78fff7f88882',
    '27f78fff7f7f8888',
    '7f78fff7f7f78888',
    '7778877777f78888',
    '8888887777778888',
    '8888888888888888',
    '8888888888888888',
    '2222222222222222',
    '2222222222222222',
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
TILES[56] = t(  # Desert Coast: pale sand at water's edge
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeeeeeee6e',
    'eeeeeeeeeeeeeeee',
    'e6eeeeeeeeeeeeee',
    'eeeeeeeee6eeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeee6eeeeeee',
    'e6eeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeeee6eeeee',
    'eeeeeeeeeeeeeeee',
    'eeee6eeeeeeeeeee',
    'eeeeeeeee6eeeeee',
)

TILES[57] = t(  # Desert Ground: cracked, parched sand
    'eee6eeeeeeeeeeee',
    'ee66eeeeeeee6eee',
    'eee6eeeeeeee66ee',
    'eeeeeeeeeeeee6ee',
    'eeeeeeee666eeeee',
    '6eeeeeeeeee6eeee',
    '6eeeeeeeeeee6eee',
    '6eeeee6eeeeee6ee',
    'eeeeee66eeeeeeee',
    'eeeeeeee6eeeeeee',
    'eeeeeeeee6eee6ee',
    'eeeeee6eeeeee6ee',
    'eeeee66eeeeeeeee',
    'eeeee6eeeeeee666',
    'eeeeeeeeeeeeeeee',
    'eeee666eeeeeeeee',
)

TILES[58] = t(  # Desert Vegetation: rolling sand dune
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeee6eeeeeeeee',
    'eeee666666eeeeee',
    'eee66666666eeeee',
    'ee66eeeeee666eee',
    'eee6eeeeeeee6eee',
    'eeeee666eeeee6ee',
    'eeee66e66eeeee6e',
    'eee6eeee66eeeeee',
    'ee6eeeeeee6eeeee',
    'e66eeeeeeee666ee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
)

TILES[59] = t(  # Desert Hill: red rocky mesa
    'eeeeeeeeeeeeeeee',
    'eeeeeee44eeeeeee',
    'eeeeec4cc4eeeeee',
    'eeeec4cccc4ceeee',
    'eeec4cccccc4cee4',
    'eec4ccccccccc4c4',
    'ec4cccc44ccccc4c',
    'cccccc4444cccccc',
    'cccc44444444cccc',
    'c4cccc4444cccc4c',
    'cc4cccccccccc4cc',
    'cccc4cccccc4cccc',
    'eeec4cccccc4ceee',
    'eeec4cccccc4ceee',
    'eeeec4ccccc4eeee',
    'eeeeeeeeeeeeeeee',
)

TILES[60] = t(  # Desert Peak: red sandstone spire
    'eeeeeeeeeeeeeeee',
    'eeeeeeeec4eeeeee',
    'eeeeeeec44ceeeee',
    'eeeeeec4cc4ceeee',
    'eeeeec4cccc4ceee',
    'eeeec4cccccc4cee',
    'eeec4cccc44cc4ce',
    'eec4cccc4444c4cc',
    'ec4cccc44cc44ccc',
    'c4cccc44cccc44cc',
    'cccc4444cccc4444',
    '4444444444444444',
    '4444444444444444',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
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
TILES[64] = t(  # Forest Coast: mossy shore
    'eeeeeee2eeeeeeee',
    'ee2eeeeeeeeeeeee',
    'eeeeeeeee2eeeeee',
    'eeeeee2eeeeeeeee',
    'eeeeeeeeeeee2eee',
    'e2eeeeeeeeeeeeee',
    'eeeeeeeeeeeeeeee',
    'eeee2eeeeeeeeeee',
    'eeeeeeeeeeeeee2e',
    'eee6eeeee2eeeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeeeee6eeeee',
    'eeeeeeeeeeeeeeee',
    'eeeeeeee2eeeeeee',
    'ee2eeeeeeeeeee2e',
    'eeeeeeeeeeeeeeee',
)

TILES[65] = t(  # Forest Ground: dark mossy turf
    '2222222222222222',
    '8222222822228222',
    '2222822222222222',
    '2228222222a22222',
    '2222222a2222a282',
    '2228222222222222',
    '22a2222222a22282',
    '2222222222222222',
    '2222822222822222',
    '8228222a22228222',
    '2222222222a22222',
    '2222a282222a2222',
    '2222222222222222',
    '22a22222822228a2',
    '2222822222a22222',
    '2222222822222222',
)

TILES[66] = t(  # Forest Vegetation: dense undergrowth
    '2222a2222a222222',
    '22a2a2a2a2a22a22',
    '2a2a2a2a2a2a2a22',
    '22a2aaa2a2aaa2a2',
    '2a2aaa2a2aa222a2',
    '2a2a2a2aaa2a2a22',
    '22aaa2a2aa2a2a22',
    '2a2a2aa2a2aaa2a2',
    '22aaa2a22a22a2a2',
    '2a2aa2a2a2aaa2a2',
    '22a2aa2aaa2a2a22',
    '2aaa2a2a22aa2a22',
    '2a22a2aaa2a2a2a2',
    '22aa2a2aa2a2a2a2',
    '2a22a2a2aa2a2aa2',
    '2222222222222222',
)

TILES[67] = t(  # Forest Hill: tree-cloaked rise
    '2222222a22222222',
    '22222aaaaa222222',
    '2222aaa66aaa2222',
    '222aaa6666aaa222',
    '22aaaaa66aaaaa22',
    '226aaaaaaaa6a622',
    '226aaaaaaaaaa622',
    '226aaaaaaaaaa622',
    '266aaaaaaaaaa662',
    '266aaaaaaaaaa662',
    '266aaaaaaaaaa662',
    '266aaaaaaaaaa662',
    '2266aaaaaaaa6622',
    '22266666666e2222',
    '2222266666622222',
    '2222222222222222',
)

TILES[68] = t(  # Forest Peak: forested mountain
    '2222222222222222',
    '22222222a2222222',
    '222222aaaa222222',
    '22222aaaa6a22222',
    '2222aaaa6f7a2222',
    '222aaaa6f87aa222',
    '222aaa6788faa222',
    '22aaa6788fff8a22',
    '22aa67888fff88a2',
    '2aaa78fff7f8888a',
    'aa78fff7f7878888',
    '888887778888888a',
    '8888888888888888',
    '2228888888888222',
    '2222222222222222',
    '2222222222222222',
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
TILES[72] = t(  # DeepForest Coast: peaty waterline
    '6666666666666666',
    '8666666886666666',
    '666886666666e666',
    '666666666688e666',
    '6886666666666666',
    '6666666666666666',
    '6886666688666666',
    '666666666666e666',
    '666688866666e666',
    '6666666666886666',
    '6886666886666666',
    '666666666666e666',
    '666886666666e666',
    '6666666666666666',
    '6886666688666666',
    '6666666666666666',
)

TILES[73] = t(  # DeepForest Ground: shadowed forest floor
    '2828282828282828',
    '8222222222a22282',
    '2228222222222222',
    '2822822222a22222',
    '22a282222222822a',
    '2222222822822822',
    '2228222222a22222',
    '8222222822222222',
    '22a82222222a2222',
    '2222822822822222',
    '2222a22222a22228',
    '2228222822222222',
    '2222222222a22822',
    '2228222222822222',
    '2222a22822a22222',
    '8228282828282828',
)

TILES[74] = t(  # DeepForest Vegetation: dense canopy
    '0202220222200222',
    '2222222222220222',
    '0220222222222222',
    '2222000022222200',
    '0222222220222222',
    '2222222222222222',
    '2200222222002222',
    '2222220222222222',
    '0222222222222220',
    '2200222222220022',
    '2222222200222222',
    '2222222222222222',
    '0022222220022222',
    '2222220022222222',
    '0222222222222200',
    '2200022222200222',
)

TILES[75] = t(  # DeepForest Hill: pine-clad slope
    '2222222a22222222',
    '22222a2a2a222222',
    '22a22aaaaa2a2222',
    '2aaa2aaaaa2aaa22',
    'aaaaa222a222aaaa',
    '2aaa222aaa222aaa',
    '2aa222aaaaa222aa',
    'aa22aaaaaaaaa22a',
    '2222aaaaaaaaa222',
    '22222aaa6aaa2222',
    '2266662266662266',
    '2666266666626666',
    '6266666666666626',
    '6666266666626666',
    '2266662266662266',
    '2222222222222222',
)

TILES[76] = t(  # DeepForest Peak: snow-touched pine peak
    '2222222f22222222',
    '222222ff7f222222',
    '22222f78887f2222',
    '2222f78fff8f7222',
    '222f78fffff87722',
    '22f78fff77f88882',
    '27f78fff7f7f8888',
    '78fff77f7f78878a',
    '7787777f7787888a',
    '887778888778aaaa',
    '88a8888aaaaaaaaa',
    '8aaaaaaaaaaaaa8a',
    '8aa6aaa6aa6aaaa8',
    '88886888888a8888',
    '2222222222222222',
    '2222222222222222',
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
TILES[80] = t(  # Tundra Coast: icy shoreline
    'fffffffffffffffe',
    'fffbfffbffffffff',
    'ffbbbffffbbfffff',
    'fffbfffffbbbffff',
    'ffffbfffffbfffff',
    'fbfffffffffffbff',
    'bbbfffffbfffbbbf',
    'fbfffffbbbffbfff',
    'ffffffffbfffffff',
    'ffffffbfffffffff',
    'ffffbbbfffffbfff',
    'fffbfffffffbbbff',
    'ffffffffffffbfff',
    'fbfffffffffffbff',
    'bbbfffffffffbbbf',
    'fbfffffffffffbff',
)

TILES[81] = t(  # Tundra Ground: snow with subtle flecks
    'fffffffffffffffe',
    'ffffefffffffffff',
    'fffffffffffefeff',
    'ffeffffffffffffe',
    'ffffffffefffffff',
    'fffffffffffffeff',
    'fefffffffffffeff',
    'ffffffffeffffffe',
    'ffffefffffffffff',
    'fffffffffffefffe',
    'feffffffffffffff',
    'ffffffefffffffff',
    'fffffffffeffffff',
    'fffefffffffffffe',
    'fffffffffeffffff',
    'effffffffffffeff',
)

TILES[82] = t(  # Tundra Vegetation: ice patch on snow
    'ffffffffffffffff',
    'ffbfffffffffffff',
    'fbbbffffffbfffff',
    'ffbfffffffbbbfff',
    'fffffffbfffbffff',
    'ffffffbbbffffffe',
    'fffffffbfffffbff',
    'feffffffffffbbbf',
    'fffefffffffffbff',
    'ffffefffbfffffff',
    'ffffffbbbfffffff',
    'fffffbfbfbffffff',
    'fffffffbfffffeff',
    'fefffffffffffbff',
    'ffffffffffffbbbf',
    'ffffffffffffbfff',
)

TILES[83] = t(  # Tundra Hill: snowy mound with ice
    'ffffffffffffffff',
    'ffffffbbbbffffff',
    'fffbbbfffbbbffff',
    'ffbfffbbfffbbfff',
    'fbffffffffffbfff',
    'fbfffffffffffbff',
    'bffffffffffffbff',
    'bfffffffffffffbf',
    'bfffffffffffffff',
    'bfffbbffffffffbf',
    'fbfbfffbbbffffbf',
    'fbbfffffffbfffbf',
    'fffbbbfffffbbbff',
    'ffffffbbbbbfffff',
    'ffffffffffffffff',
    'ffffffffffffffff',
)

TILES[84] = t(  # Tundra Peak: snow-capped mountain
    'ffffffffffffffff',
    'ffffffffffffffff',
    'fffffffffffffffe',
    'ffffffffffffffff',
    'fffffffffeffffff',
    'fffffffffffffeff',
    'ffffffffffffffff',
    'ffffffefffffffff',
    'ffffffffffffeeff',
    'fffffffeffffffff',
    'ffffffffffffffff',
    'feffffefefefffff',
    '7777fffeffffefef',
    '8877777777777777',
    '8888887777777777',
    '8888888888888888',
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
TILES[88] = t(  # Volcanic Coast: hot ash beach
    '8888888888888888',
    '8804888888880888',
    '8884c888888c4888',
    '8888c488884c8888',
    '8888c488884c8888',
    '8888888888888888',
    '8884c4888884c488',
    '8884c4888884c488',
    '8888888888888888',
    '888c4888c48c4888',
    '888c4888c4ec4888',
    '888c488884c4eee8',
    '8888888888888888',
    '88884c4888884c48',
    '88884c4888884c48',
    '8888888888888888',
)

TILES[89] = t(  # Volcanic Ground: dark ash flats
    '8888888888888888',
    '8808888888880888',
    '8888888880888888',
    '8888080888888888',
    '8888888888880888',
    '8088888008888880',
    '8888888888888888',
    '8888880888880888',
    '8888888888888888',
    '8088088888888008',
    '8888888888888888',
    '8888888080888888',
    '8888888888880888',
    '0888888888888880',
    '8888080888888888',
    '8888888888080888',
)

TILES[90] = t(  # Volcanic Vegetation: lava-veined ash
    '8888c4888888c888',
    '888c4888888c4888',
    '8884c4888884c488',
    '8884c4ee8884c488',
    '8888c44e88884c88',
    '88884c44e8884c88',
    '88884c4eee8c4888',
    '8888c4eeec4c4888',
    '888c4eeeeec48888',
    '88c4eeeeeec48888',
    '88c4eeeeec488888',
    '888c4eeec4888888',
    '8884c4ec4c488888',
    '8884c4c4ec488888',
    '88884c44eec48888',
    '88888c44eec48888',
)

TILES[91] = t(  # Volcanic Hill: pile of volcanic rock
    '8888888888888888',
    '8888884cc4888888',
    '888884cccc488888',
    '88884cc44cc48888',
    '8884cc4444cc4888',
    '884cc444444cc488',
    '84cc44ccccc44cc4',
    '4cc44cc44cc44ccc',
    '4cc4cc4444c4ccc4',
    '4ccccc444cccccc4',
    '4cccccccccccccc4',
    '4cc4cccccccc4cc4',
    '84cccccccccccc48',
    '884cccccccccc488',
    '88884ccccccc4888',
    '8888888888888888',
)

TILES[92] = t(  # Volcanic Peak: lava-spilling peak
    '8888888888888888',
    '888888884c488888',
    '88888884ccc48888',
    '8888884ccecc4888',
    '888884ccceccc488',
    '88884ccceeeccc48',
    '8884cccceeeeccce',
    '884ccccceeec4eee',
    '84cccc4eeec44eee',
    '4ccc44eee4444eee',
    'cc444eeeec44eeee',
    'cccc444eeeeeeec4',
    'ccccccc4eeeec444',
    'cccccccc4444c44e',
    '8888888888888888',
    '8888888888888888',
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
TILES[96] = t(  # Mountains Coast: rocky shore
    '8787787877878787',
    '7777787787777787',
    '7777878877787777',
    '7787877878787877',
    '8787877878787787',
    '7787877878787877',
    '8787787787787787',
    '7777787877787787',
    '7787877787787787',
    '8787877878787877',
    '7787787877878787',
    '7777787787777787',
    '7777878877787777',
    '7787877878787877',
    '7787787877878787',
    '7777787787777787',
)

TILES[97] = t(  # Mountains Ground: rocky terrain
    '7777777777777777',
    '7787877878787877',
    '8787787877878787',
    '7777787787777787',
    '7777878877787777',
    '7787877878787877',
    '8787877878787787',
    '7787877878787877',
    '8787787787787787',
    '7777787877787787',
    '7787877787787787',
    '8787877878787877',
    '7787787877878787',
    '7777787787777787',
    '7777878877787777',
    '7787877878787877',
)

TILES[98] = t(  # Mountains Vegetation: hardy alpine grass
    '7777777777777777',
    '772a7787787a7878',
    '787787a787787787',
    '772a78787a787877',
    '7872a7878787a787',
    '7787a7878787a787',
    '8a87787787787787',
    '77877a78787a7787',
    '8787787a7878a787',
    '7777787877787787',
    '77a7877787787a87',
    '8a87877878787a77',
    '7787a877878a7787',
    '7777787a7877a787',
    '8a87878a877a7777',
    '77877878a8787a87',
)

TILES[99] = t(  # Mountains Hill: rocky hill
    '7777777777777777',
    '7777778887777777',
    '7777788ff8877777',
    '7777878fff8f7777',
    '777787888fff8777',
    '77787f78fff8877a',
    '7787f78ffff88882',
    '787f78ffff888888',
    '78fff7f88888888a',
    'f78fff8888788888',
    '7787888888788888',
    '8888888888888888',
    '8888888888888888',
    '7777788888887777',
    '7777777777777777',
    '7777777777777777',
)

TILES[100] = t(  # Mountains Peak: tall snow-capped mountain
    '7777777777777777',
    '777777fff7777777',
    '7777f7fffff77777',
    '777f7fff7fff7777',
    '77f7fff7f7f8f777',
    '7f7fff7f7f78f877',
    'f7fff7f7f7888887',
    '7fff7f7f78888888',
    'fffff8f888888888',
    'f88f8888888887ff',
    '88888887778fffff',
    '88887777ffffffff',
    '7777ffffffffffff',
    '77fffffffffff777',
    'ffffffffffff7777',
    '7777777777777777',
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
TILES[104] = t(  # Plains Town Floor: warm wood plank
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

TILES[105] = t(  # Plains Town Wall: dressed stone block
    '8888888888888888',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8777777787777778',
    '8888888888888888',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
    '7777787777777877',
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
TILES[112] = t(  # Desert Town Floor: terracotta tile
    '6666666666666666',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6666666666666666',
    'c6cccc6cccc6cccc',
    'c6cccc6cccc6cccc',
    'c6cccc6cccc6cccc',
    'c6cccc6cccc6cccc',
    '6666666666666666',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6cccc6cccc6ccccc',
    '6666666666666666',
)

TILES[113] = t(  # Desert Town Wall: adobe brick
    '6666666666666666',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
    '6666666666666666',
    'eeee6eeeeeee6eee',
    'eeee6eeeeeee6eee',
    'eeee6eeeeeee6eee',
    'eeee6eeeeeee6eee',
    '6666666666666666',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
    '6eeeeeee6eeeeeee',
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
TILES[120] = t(  # Forest Town Floor: rough plank with knots
    '8888888888888888',
    '6666e666666666e6',
    '66e66666e6666666',
    '8888888888888888',
    '6666666e6666e666',
    '66e6666666e66666',
    '8888888888888888',
    '666666e6666e6666',
    '6666666666666666',
    '8888888888888888',
    '6e66666e66666666',
    '666666666666e666',
    '8888888888888888',
    '66e66666e6666e66',
    '6666666666666666',
    '8888888888888888',
)

TILES[121] = t(  # Forest Town Wall: stacked logs
    '6666666666666666',
    '6e66666666e66666',
    '6e66e66666e6e666',
    '8888888888888888',
    '666e6666666e6666',
    '6666666e6666e666',
    '66e66666e6666666',
    '8888888888888888',
    '6e66666666e66666',
    '666666e6666666e6',
    '6666e66666e66666',
    '8888888888888888',
    '666e6666e6666e66',
    '66e6666666e66666',
    '6666666e6666e666',
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
TILES[128] = t(  # DeepForest Town Floor: dark plank
    '0000000000000000',
    '8666666886666688',
    '6666886666666666',
    '0000000000000000',
    '8866666886666666',
    '6666666688666666',
    '0000000000000000',
    '6666886666666666',
    '8666666688666666',
    '0000000000000000',
    '6688666666666886',
    '6666666886666666',
    '0000000000000000',
    '8866666666886666',
    '6666886666666666',
    '0000000000000000',
)

TILES[129] = t(  # DeepForest Town Wall: dark stone with moss patches
    '8888888888888888',
    '8000000080000008',
    '8002a00080020008',
    '8000000080000008',
    '8000000080000008',
    '8000a00080000008',
    '8000000080000008',
    '8888888888888888',
    '0000800000008000',
    '00008000200a8000',
    '0000800000008000',
    '0000800a00008000',
    '0000800000008000',
    '0000800000008000',
    '0000800000008000',
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
TILES[136] = t(  # Tundra Town Floor: hard packed snow
    'ffffffffffffffff',
    'ffffffbfffffffff',
    'fffffffffffbffff',
    'ffbfffffffffffff',
    'ffffffffbfffffff',
    'ffffffffffffffff',
    'ffffbfffffffbfff',
    'fffffffffbffffff',
    'ffffffffffffffff',
    'fffbfffffffffbff',
    'ffffffffbfffffff',
    'ffffffffffffffff',
    'fffffbfffffffbff',
    'ffffffffffffffff',
    'fffffffbfffffbff',
    'ffffffffffffffff',
)

TILES[137] = t(  # Tundra Town Wall: ice block
    'bbbbbbbbbbbbbbbb',
    'bfffffffbfffffff',
    'bfffffffbfffffff',
    'bfffffffbfffffff',
    'bfffffffbfffffff',
    'bfffffffbfffffff',
    'bfffffffbfffffff',
    'bbbbbbbbbbbbbbbb',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
    'fffbfffffffbffff',
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
TILES[144] = t(  # Volcanic Town Floor: dark stone with red veins
    '8888888888888888',
    '8004488888884008',
    '8888c8888884c888',
    '8888c4888884c888',
    '8888888888888888',
    '88884c8888884c88',
    '88884c8888884c88',
    '8888888888888888',
    '4c8888884c888888',
    '4c8888884c888888',
    '8888888888888888',
    '888884c4888884c4',
    '888884c4888884c4',
    '8888888888888888',
    '88884c4888884c48',
    '8888888888888888',
)

TILES[145] = t(  # Volcanic Town Wall: obsidian block
    '8888888888888888',
    '8000000080000008',
    '8000000080000008',
    '8000000080000008',
    '8004400080000008',
    '8000000080000008',
    '8000000080000008',
    '8888888888888888',
    '0000800000008000',
    '0000800000008000',
    '0000800440008000',
    '0000800000008000',
    '0000800000008000',
    '0000800000008000',
    '0000800000008000',
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
TILES[152] = t(  # Mountains Town Floor: cut stone tile
    '7777777777777777',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7777777777777777',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '7777777777777777',
)

TILES[153] = t(  # Mountains Town Wall: massive cut block
    '7777777777777777',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7888888878888887',
    '7777777777777777',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
    '8888788888888788',
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
