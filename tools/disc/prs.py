"""Decompress the LZ77 streams of XvSF Saturn files such as ``MC09.SHP``.

The format is the one executed by the game's streaming decompressor at WRAM-H
``0x0601077C`` (`EXP-0017`); it resembles Sega's PRS but is not identical:

* control bits are read one at a time, least significant bit first, from
  control bytes interleaved with the data;
* bit 1: copy one literal byte;
* bits 0, 0, then two more bits n (first bit high): a short copy of n + 2 bytes
  from offset ``byte - 0x100`` (back up to 256 bytes);
* bits 0, 1: read a **big-endian** 16-bit word v; the offset is
  ``(v >> 3) - 0x2000`` (back up to 8 KiB) and the length is ``(v & 7) + 2``;
  when ``v & 7`` is 0 the next byte n gives the length n + 1, and n = 0 ends
  the stream.

Copies may overlap their own output (run-length repeats). A file starts with a
big-endian 32-bit entry count; for a count of 0 the single stream follows at
offset 4 (`EXP-0017`). Files with a nonzero count are not handled.

`compress` writes such a stream (greedy matching, offsets up to 0x1FFF back);
`compress_file` adds the header and can pad the file to a fixed size, with
leading literals added until the stream ends at or after ``min_end`` (`DISC-002`).
"""

from __future__ import annotations

import argparse
import hashlib
from collections.abc import Sequence
from pathlib import Path


class PrsError(ValueError):
    """Raised when a stream ends early or copies from before its start."""


def decompress(data: bytes) -> tuple[bytes, int]:
    """Return the decompressed bytes and the number of input bytes consumed."""
    out = bytearray()
    pos = 0
    control = 0
    left = 0

    def read_byte() -> int:
        nonlocal pos
        if pos >= len(data):
            raise PrsError(f"stream ends early at input offset {pos:#x}")
        value = data[pos]
        pos += 1
        return value

    def bit() -> int:
        nonlocal control, left
        if left == 0:
            control = read_byte()
            left = 8
        value = control & 1
        control >>= 1
        left -= 1
        return value

    while True:
        if bit():
            out.append(read_byte())
            continue
        if bit():
            word = (read_byte() << 8) | read_byte()
            offset = (word >> 3) - 0x2000
            size = word & 7
            if size == 0:
                size = read_byte()
                if size == 0:
                    return bytes(out), pos
                size += 1
            else:
                size += 2
        else:
            size = ((bit() << 1) | bit()) + 2
            offset = read_byte() - 0x100
        start = len(out) + offset
        if start < 0:
            raise PrsError(f"copy from before the start at output {len(out):#x}")
        for i in range(size):
            out.append(out[start + i])


def decompress_file(data: bytes) -> tuple[bytes, int]:
    """Decompress a whole single-stream file (entry count 0)."""
    count = int.from_bytes(data[:4], "big")
    if count != 0:
        raise PrsError(f"entry count {count} is not handled")
    out, used = decompress(data[4:])
    return out, used + 4


MAX_OFFSET = 0x1FFF
MAX_LENGTH = 256


class _Writer:
    def __init__(self) -> None:
        self.out = bytearray()
        self.control = -1
        self.used = 8

    def bit(self, value: int) -> None:
        if self.used == 8:
            self.control = len(self.out)
            self.out.append(0)
            self.used = 0
        self.out[self.control] |= value << self.used
        self.used += 1


def _longest(data: bytes, pos: int, chains: dict[bytes, list[int]]) -> tuple[int, int]:
    best_size, best_offset = 0, 0
    limit = min(MAX_LENGTH, len(data) - pos)
    for start in reversed(chains.get(data[pos : pos + 2], [])):
        if pos - start > MAX_OFFSET:
            break
        size = 0
        while size < limit and data[start + size] == data[pos + size]:
            size += 1
        if size > best_size:
            best_size, best_offset = size, start - pos
            if size == limit:
                break
    return best_size, best_offset


def compress(data: bytes, literals: int = 0) -> bytes:
    """Return a stream that `decompress` turns back into ``data``.

    The first ``literals`` bytes are always written as literals.
    """
    writer = _Writer()
    out = writer.out
    chains: dict[bytes, list[int]] = {}
    pos = 0
    indexed = 0

    def index(upto: int) -> None:
        nonlocal indexed
        while indexed < upto:
            chains.setdefault(data[indexed : indexed + 2], []).append(indexed)
            indexed += 1

    while pos < len(data):
        size, offset = (0, 0) if pos < literals else _longest(data, pos, chains)
        short = size >= 2 and offset >= -0x100 and size <= 5
        if size < 2 or (size == 2 and not short):
            writer.bit(1)
            out.append(data[pos])
            size = 1
        elif short:
            writer.bit(0)
            writer.bit(0)
            writer.bit((size - 2) >> 1)
            writer.bit((size - 2) & 1)
            out.append(offset + 0x100)
        else:
            writer.bit(0)
            writer.bit(1)
            word = (offset + 0x2000) << 3
            if size <= 9:
                out += (word | (size - 2)).to_bytes(2, "big")
            else:
                out += word.to_bytes(2, "big")
                out.append(size - 1)
        pos += size
        index(pos)
    writer.bit(0)
    writer.bit(1)
    out += bytes(3)
    return bytes(out)


def compress_file(data: bytes, size: int | None = None, min_end: int = 0) -> bytes:
    """Return a whole file (count 0 + stream), zero-padded to ``size`` if given.

    Leading literals are added until the stream (with its header) ends at or
    after ``min_end`` bytes.
    """
    literals = 0
    while True:
        body = bytes(4) + compress(data, literals)
        if len(body) >= min_end or literals >= len(data):
            break
        literals += max(1, (min_end - len(body)) * 8 // 9)
    if size is not None:
        if len(body) > size:
            raise PrsError(f"compressed file is {len(body)} bytes; limit {size}")
        body += bytes(size - len(body))
    return body


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="compressed files")
    parser.add_argument("--out-dir", type=Path, help="write <name>.bin here")
    args = parser.parse_args(argv)
    for path in args.files:
        raw = path.read_bytes()
        try:
            data, used = decompress_file(raw)
        except PrsError as error:
            print(f"{path.name}: error: {error}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        print(f"{path.name}: {len(raw)} -> {len(data)} bytes, used {used}, {digest}")
        if args.out_dir:
            args.out_dir.mkdir(parents=True, exist_ok=True)
            (args.out_dir / f"{path.stem}.bin").write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
