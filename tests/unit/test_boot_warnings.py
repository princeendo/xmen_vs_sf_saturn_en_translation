from __future__ import annotations

import struct

import pytest

from tools.disc.boot_warnings import (
    HEIGHT,
    PIXELS,
    STRIDE,
    WIDTH,
    check,
    packed,
    render,
    shown,
    spans,
)
from tools.text.font import Font

STYLE: dict[str, object] = {
    "pitch": 12,
    "line": 14,
    "title": "WARNING",
    "title_top": 24,
    "top": 52,
}


class BlockFont(Font):
    """Every glyph is a 10 x 12 block of pen 2 with a pen-7 shadow column."""

    def __init__(self) -> None:
        super().__init__(b"", 0, 0)

    def glyph(self, code: int) -> tuple[bytes, str]:
        cell = bytearray(128)
        for row in range(12):
            for column in range(11):
                pen = 7 if column == 10 else 2
                byte = row * 8 + column // 2
                cell[byte] |= pen << 4 if column % 2 == 0 else pen
        return bytes(cell), "raw"


def original() -> bytes:
    header = bytearray(PIXELS)
    header[:2] = b"BM"
    struct.pack_into("<I", header, 10, PIXELS)
    struct.pack_into("<iiHH", header, 18, WIDTH, HEIGHT, 1, 4)
    header[54 + 4 * 6 : 54 + 4 * 6 + 3] = b"\xf8\xf8\xf8"
    return bytes(header) + bytes(STRIDE * HEIGHT)


def test_spans_colour_the_marked_text() -> None:
    assert spans("a {b} [c] d") == [
        ("a ", "white"),
        ("b", "cyan"),
        (" ", "white"),
        ("c", "red"),
        (" d", "white"),
    ]
    for bad in ("a {b", "a b}", "[a"):
        with pytest.raises(ValueError, match="unbalanced"):
            spans(bad)


def test_packed_puts_the_top_row_last_high_nibble_first() -> None:
    pixels = bytearray(WIDTH * HEIGHT)
    pixels[0], pixels[1] = 1, 2
    data = packed(bytes(pixels))
    assert data[(HEIGHT - 1) * STRIDE] == 0x12
    assert len(data) == STRIDE * HEIGHT


def test_render_keeps_the_header_and_shows_text_eight_rows_down() -> None:
    source = original()
    built = render(source, ["A"], BlockFont(), STYLE)
    check(source, built)
    screen = shown(built)
    # the line's block starts at picture row 52, so screen row 60; white
    # (f8) shows as c0 under the game's colour rule
    left = (WIDTH - 11) // 2
    pixel = (60 * WIDTH + left) * 3
    assert screen[pixel : pixel + 3] == b"\xc0\xc0\xc0"
    above = (59 * WIDTH + left) * 3
    assert screen[above : above + 3] == bytes(3)


def test_render_refuses_text_that_does_not_fit() -> None:
    with pytest.raises(ValueError, match="pixels wide"):
        render(original(), ["A" * 30], BlockFont(), STYLE)
    with pytest.raises(ValueError, match="picture row 224"):
        render(original(), ["A"] * 13, BlockFont(), {**STYLE, "top": 45})
    render(original(), ["A"] * 13, BlockFont(), {**STYLE, "top": 44})


def test_check_refuses_a_changed_palette_or_size() -> None:
    source = original()
    built = bytearray(render(source, ["A"], BlockFont(), STYLE))
    built[60] ^= 1
    with pytest.raises(ValueError, match="palette"):
        check(source, bytes(built))
    with pytest.raises(ValueError):
        check(source, bytes(built[:-1]))


def test_rows_below_the_display_are_not_shown() -> None:
    source = original()
    built = bytearray(source)
    # picture row 224 (BMP row 15 from the bottom) set to colour 6
    built[PIXELS + 15 * STRIDE : PIXELS + 16 * STRIDE] = b"\x66" * STRIDE
    screen = shown(bytes(built))
    assert not any(screen[232 * WIDTH * 3 : 233 * WIDTH * 3])
