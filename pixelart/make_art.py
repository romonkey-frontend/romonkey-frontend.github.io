"""
ROMonkey pixel art: re-renders the logo and buttons at a chosen pixel size,
and draws the "Links" button.

Run from the site folder:   python3 pixelart/make_art.py

Every image is really a small grid of "art pixels" (logo 44x46, buttons
21 rows tall). Each art pixel is drawn as an N x N block of screen pixels.
This script finds the 1x grid, then redraws it with a new block size,
so the result is always pixel-perfect (never blurry). It is safe to run
again: it detects whatever block size the files currently have.

Change the sizes here:
"""
LOGO_SCALE = 4     # was 6 (264x276). 4 gives 176x184.
BUTTON_SCALE = 2   # was 3 (63px tall). 2 gives 42px tall.

import os
from functools import reduce
from math import gcd

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, "..", "images")


def block_size(im):
    """Largest N such that the image is made of N x N blocks."""
    px = im.load()
    w, h = im.size
    runs = []
    for y in range(h):
        r = 1
        for x in range(1, w):
            if px[x, y] == px[x - 1, y]:
                r += 1
            else:
                runs.append(r)
                r = 1
        runs.append(r)
    for x in range(w):
        r = 1
        for y in range(1, h):
            if px[x, y] == px[x, y - 1]:
                r += 1
            else:
                runs.append(r)
                r = 1
        runs.append(r)
    return reduce(gcd, runs)


def load_grid(name):
    im = Image.open(os.path.join(IMAGES, name)).convert("RGBA")
    n = block_size(im)
    return im.resize((im.width // n, im.height // n), Image.NEAREST)


def save(grid, name, scale):
    grid.resize((grid.width * scale, grid.height * scale), Image.NEAREST).save(
        os.path.join(IMAGES, name), optimize=True
    )


# ---- Button layout (in art pixels, measured from the existing buttons) ----
ICON_X, ICON_Y, ICON_W = 19, 4, 11   # 11x11 icon after the banana
TEXT_X, TEXT_Y = 33, 6               # 5x7 capital letters, 1px apart
RIGHT_EDGE = 7                       # white padding + border + shadow columns

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

# Letters not found in the existing buttons, drawn in the same 5x7 style.
EXTRA_LETTERS = {
    "K": [
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ],
}

# Chain-link icon, same 11x11 black-outline style as the other icons.
LINK_ICON = [
    "...........",
    "...........",
    "..###.###..",
    ".#...#...#.",
    "#...#.#...#",
    "#...#.#...#",
    "#...#.#...#",
    ".#...#...#.",
    "..###.###..",
    "...........",
    "...........",
]


def letter_from(button_grid, word, letter):
    """Copy a 5x7 letter out of an existing button (e.g. 'N' from DOWNLOAD)."""
    k = word.index(letter)
    x0 = TEXT_X + 6 * k
    return button_grid.crop((x0, TEXT_Y, x0 + 5, TEXT_Y + 7))


def draw_pattern(grid, pattern, x0, y0):
    px = grid.load()
    for dy, row in enumerate(pattern):
        for dx, ch in enumerate(row):
            px[x0 + dx, y0 + dy] = BLACK if ch == "#" else WHITE


def make_button(word, template, letters):
    """Build a button for `word` from `template` (banana + frame + shadow)."""
    width = TEXT_X + 6 * len(word) - 1 + RIGHT_EDGE
    # Template width and new width differ by an even number, so the
    # dotted bottom-edge pattern lines up exactly.
    assert (template.width - width) % 2 == 0
    out = Image.new("RGBA", (width, template.height))
    left = template.crop((0, 0, width - RIGHT_EDGE, template.height))
    right = template.crop((template.width - RIGHT_EDGE, 0, template.width, template.height))
    out.paste(left, (0, 0))
    out.paste(right, (width - RIGHT_EDGE, 0))

    px = out.load()
    # Wipe the old icon and text, keeping the banana and frame.
    for y in range(ICON_Y, ICON_Y + ICON_W):
        for x in range(ICON_X, width - RIGHT_EDGE):
            px[x, y] = WHITE

    draw_pattern(out, LINK_ICON, ICON_X, ICON_Y)
    for k, ch in enumerate(word):
        x0 = TEXT_X + 6 * k
        if ch in EXTRA_LETTERS:
            draw_pattern(out, EXTRA_LETTERS[ch], x0, TEXT_Y)
        else:
            out.paste(letters[ch], (x0, TEXT_Y))
    return out


def main():
    logo = load_grid("logo.png")
    save(logo, "logo.png", LOGO_SCALE)

    buttons = {n: load_grid(f"btn-{n}.png") for n in ("features", "download", "manual", "history")}
    for name, grid in buttons.items():
        save(grid, f"btn-{name}.png", BUTTON_SCALE)

    letters = {
        "L": letter_from(buttons["download"], "DOWNLOAD", "L"),
        "N": letter_from(buttons["download"], "DOWNLOAD", "N"),
        "I": letter_from(buttons["history"], "HISTORY", "I"),
        "S": letter_from(buttons["features"], "FEATURES", "S"),
    }
    links = make_button("LINKS", buttons["manual"], letters)
    save(links, "btn-links.png", BUTTON_SCALE)

    for f in ("logo.png", "btn-features.png", "btn-download.png", "btn-manual.png",
              "btn-history.png", "btn-links.png"):
        print(f, Image.open(os.path.join(IMAGES, f)).size)


if __name__ == "__main__":
    main()
