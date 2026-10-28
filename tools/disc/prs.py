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
