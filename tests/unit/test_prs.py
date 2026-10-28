from __future__ import annotations

from pathlib import Path

import pytest

from tools.disc.prs import PrsError, decompress, decompress_file, main

# Control 0x93 (LSB first): literal A, literal B, short copy (n = 2: 4 bytes from
# -2), long copy (word 0xFFD1: 3 bytes from -6). Control 0x0A: long copy (word
# 0xFFF8, count byte 4: 5 bytes from -1), long word 0x0000 with count byte 0: end.
STREAM = bytes.fromhex("93 41 42 FE FFD1 0A FFF8 04 0000 00")
FILE = bytes(4) + STREAM


def test_decompress_all_forms() -> None:
    assert decompress(STREAM) == (b"ABABABABAAAAAA", len(STREAM))


def test_decompress_file_skips_the_count() -> None:
    assert decompress_file(FILE) == (b"ABABABABAAAAAA", len(FILE))


def test_nonzero_count_is_refused() -> None:
    with pytest.raises(PrsError, match="entry count 1"):
        decompress_file(b"\x00\x00\x00\x01" + STREAM)


def test_truncated_stream() -> None:
    with pytest.raises(PrsError, match="ends early"):
        decompress(STREAM[:-1])


def test_copy_before_start() -> None:
    with pytest.raises(PrsError, match="before the start"):
        decompress(bytes.fromhex("00 FF"))


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "X.SHP"
    source.write_bytes(FILE)
    assert main([str(source), "--out-dir", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "X.bin").read_bytes() == b"ABABABABAAAAAA"
    assert "X.SHP: 17 -> 14 bytes, used 17" in capsys.readouterr().out
