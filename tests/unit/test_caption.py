from __future__ import annotations

import pytest

from tools.text.caption import (
    ENGLISH_CELLS,
    CaptionError,
    compile_record,
    decode_record,
    encode_line,
)


def test_encode_line_maps_and_pads() -> None:
    codes = encode_line("Ab 1!", cells=8)
    assert codes == [0x0681, 0x0692, 0x0020, 0x06D1, 0x0671, 0x0020, 0x0020, 0x0020]


def test_compile_and_decode_round_trip() -> None:
    lines = ["Practice, then come back.", "You'll do better (maybe)!"]
    record = compile_record(lines)
    assert len(record) == 2 * 2 * ENGLISH_CELLS
    assert decode_record(record) == lines


def test_japanese_grid_width() -> None:
    record = compile_record(["ABC", ""], cells=19)
    assert len(record) == 76
    assert decode_record(record, cells=19) == ["ABC", ""]


def test_rejects_long_line() -> None:
    with pytest.raises(CaptionError, match="limit is 25"):
        compile_record(["x" * 26, ""])


def test_rejects_unmapped_character() -> None:
    with pytest.raises(CaptionError, match="no code"):
        compile_record(["café", ""])


def test_rejects_wrong_line_count() -> None:
    with pytest.raises(CaptionError, match="2 lines"):
        compile_record(["one"])


def test_decode_rejects_unknown_code() -> None:
    with pytest.raises(CaptionError, match="no character"):
        decode_record(bytes(100))
