from __future__ import annotations

import random
from pathlib import Path

import pytest

from tools.disc.prs import (
    PrsError,
    compress,
    compress_file,
    decompress,
    decompress_file,
    main,
)

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


def sample() -> bytes:
    rng = random.Random(7)
    words = [
        bytes(rng.randrange(4) for _ in range(rng.randrange(1, 12))) for _ in range(40)
    ]
    data = b"".join(rng.choice(words) for _ in range(3000))
    # a long run (extended lengths) and a repeat 0x1FFF back (the window limit)
    return data + bytes(700) + data[-0x1FFF - 50 : -0x1FFF + 50]


def test_compress_round_trips() -> None:
    data = sample()
    stream = compress(data)
    assert decompress(stream) == (data, len(stream))
    assert len(stream) < len(data)


def test_compress_handles_empty_and_tiny_inputs() -> None:
    for data in (b"", b"A", b"AB", b"AAAAAAAAAAAAAAAAAAAA"):
        assert decompress(compress(data))[0] == data


def test_compress_file_pads_and_reaches_min_end() -> None:
    data = sample()
    plain = compress_file(data)
    target = len(plain) + 300
    padded = compress_file(data, size=target, min_end=len(plain) + 200)
    out, used = decompress_file(padded)
    assert out == data
    assert len(padded) == target
    assert len(plain) + 200 <= used <= target
    assert padded[used:] == bytes(target - used)


def test_compress_file_refuses_oversize() -> None:
    with pytest.raises(PrsError, match="limit"):
        compress_file(sample(), size=10)
