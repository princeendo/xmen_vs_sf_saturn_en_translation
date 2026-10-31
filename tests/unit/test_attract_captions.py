from __future__ import annotations

import struct

import pytest

from tools.disc.attract_captions import (
    BLANK,
    ENTRIES,
    PALETTE_ZERO,
    Frame,
    assign,
    char_bytes,
    join_frames,
    parse_frames,
    recolour,
    word_index,
)


def test_a_character_is_four_cells_left_pixel_high() -> None:
    cell = tuple((y * 16 + x) % 16 for y in range(16) for x in range(16))
    data = char_bytes(cell)
    assert len(data) == 128
    assert data[0] == 0x01  # top-left cell, row 0: pixels 0 and 1
    assert data[32] == 0x89  # top-right cell starts at x = 8
    assert data[64] == 0x01  # bottom-left cell, row 8: (8 * 16) % 16 = 0


def test_the_index_array_runs_down_columns_by_quarter_page() -> None:
    assert word_index(0, 0) == 0
    assert word_index(0, 1) == 1
    assert word_index(1, 0) == 16
    assert word_index(32, 0) == 512  # page 1, top half
    assert word_index(0, 16) == 1024  # page 0, bottom half
    assert word_index(63, 31) == 2047


def script_with(frames: list[bytes], tail: bytes = b"") -> bytes:
    return b"".join(frames) + b"\xff\xff" + tail


def test_frames_join_back_with_a_trailing_pad_byte() -> None:
    scroll = (1 << 2).to_bytes(2, "big") + bytes([0x04, 0x08])
    idle = bytes(2)
    script = script_with([scroll, idle, scroll], tail=b"\x00")
    frames = parse_frames(script)
    assert len(frames) == 4
    assert frames[0].parts == {2: bytes([0x04, 0x08])}
    assert join_frames(frames) == script


def test_recolour_puts_the_arcade_colours_in_palette_zero() -> None:
    count = 0x20
    record = struct.pack(">HH", 0x3F0, count) + bytes(2 * count)
    frame = Frame(1 << 4, {4: bytes([0x20]) + record + b"\xff"})
    recolour(frame)
    part = frame.parts[4]
    for entry, colour in ENTRIES.values():
        offset = 1 + 4 + 2 * (PALETTE_ZERO + entry - 0x3F0)
        assert struct.unpack_from(">H", part, offset)[0] == colour


def test_assign_refuses_more_characters_than_room() -> None:
    a = tuple([2] * 256)
    b = tuple([3] * 256)
    cells = {(0, 0): a, (1, 0): b, (2, 0): a, (3, 0): BLANK}
    index, writes = assign({k: v for k, v in cells.items() if v != BLANK}, [5, 6, 7], 6)
    assert index == {a: 5, b: 7}
    assert sorted(i for i, _ in writes) == [5, 7]
    with pytest.raises(ValueError, match="room"):
        assign(cells, [5], 0)
