"""Parse XvSF's attract streams (``OPENING*.ST2``) and decode their graphics blocks.

Layout (`EXP-0064`, D-056):

- **Header sector** (0x800 bytes): up to eight big-endian u32 section sizes,
  zero-terminated. The sections follow back to back from 0x800, each a
  multiple of 0x800. ``OPENING*.ST2`` has three; the third (section C) is one
  graphics block. The roles of the first two are not traced on XvSF.
- **Stream** (after the sections): 0x800-byte sectors. Sectors that start with
  the tag ``MISS`` carry 0x7FC bytes of the graphics stream; the others are
  interleaved data. The concatenated ``MISS`` payloads hold graphics blocks,
  each 4-byte aligned, with zero words between some of them.
- **Graphics block**: u32 compressed size, u32 decompressed size, then the
  compressed data, decoded by the SH-2 routine at ``0x06021AF6``
  (``lz_decode``): flag bytes, most significant bit first; 0 = a literal byte;
  1 = a big-endian word ``w`` that copies ``(w & 0xF) + 3`` bytes from **ring
  position** ``w >> 4`` of a 0x1000-byte ring (WRAM-H ``0x06021BF8``). Every
  output byte is also written to the ring, at a write index starting at 0.
  The game decodes into WRAM-H ``0x06080000`` and then writes the block's
  size into the decoded word at offset 0x10 itself.

The container layout and the ``MISS`` tag are as in the MSHvSF repository's
``tools/disc/st2_stream.py`` (commit ``40b3ad0``, last changed in
``3c6cbf5``). Its graphics LZ took the copy field as a distance back from the
output end; that is wrong for XvSF, so it is rewritten here as the ring above,
which reproduces the game's RAM (`EXP-0064`). MSHvSF's section A script and
map decoders are left out: they are not validated on XvSF.

The output is game-derived data: write it under ``local/`` only (``AGENTS.md``
rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Iterator, Sequence
from pathlib import Path

SECTOR = 0x800
TAG = b"MISS"
RING = 0x1000


def sections(data: bytes) -> list[tuple[int, int]]:
    """(offset, size) of each header section."""
    found, offset = [], SECTOR
    for index in range(8):
        (size,) = struct.unpack_from(">I", data, 4 * index)
        if size == 0:
            break
        found.append((offset, size))
        offset += size
    return found


def stream_start(data: bytes) -> int:
    return sum(size for _, size in sections(data)) + SECTOR


def miss_sectors(data: bytes) -> list[int]:
    """File offsets of the ``MISS`` sectors, in order."""
    return [
        offset
        for offset in range(stream_start(data), len(data), SECTOR)
        if data[offset : offset + len(TAG)] == TAG
    ]


def miss_payload(data: bytes) -> bytes:
    """The concatenated payloads of the stream's ``MISS`` sectors."""
    return b"".join(data[o + len(TAG) : o + SECTOR] for o in miss_sectors(data))


def lz_decode(
    data: bytes, start: int = 0, ring: bytes = bytes(RING)
) -> tuple[bytes, int]:
    """Decode one graphics block at ``start``; return (output, end offset).

    ``ring`` is the ring's starting contents; the game does not clear it.
    """
    _, size = struct.unpack_from(">II", data, start)
    position, write = start + 8, 0
    window = bytearray(ring)
    out = bytearray()
    while len(out) < size:
        flags = data[position]
        position += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                word = (data[position] << 8) | data[position + 1]
                position += 2
                read = word >> 4
                for _ in range((word & 0xF) + 3):
                    value = window[read]
                    read = (read + 1) % RING
                    out.append(value)
                    window[write] = value
                    write = (write + 1) % RING
            else:
                value = data[position]
                position += 1
                out.append(value)
                window[write] = value
                write = (write + 1) % RING
    return bytes(out[:size]), position


def blocks(payload: bytes) -> Iterator[tuple[int, bytes]]:
    """(payload offset, decoded block) for each graphics block of a stream."""
    position = 0
    while position + 8 <= len(payload):
        compressed, size = struct.unpack_from(">II", payload, position)
        if compressed == 0:
            position += 4
            continue
        if compressed > len(payload) - position or size == 0:
            return
        out, end = lz_decode(payload, position)
        yield position, out
        position = (end + 3) & ~3


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("st2", type=Path, help="an extracted .ST2 file")
    parser.add_argument("--out-dir", type=Path, required=True, help="ignored path")
    args = parser.parse_args(argv)
    data = args.st2.read_bytes()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    found = sections(data)
    decoded: list[dict[str, object]] = []
    if len(found) > 2:
        out, _ = lz_decode(data, found[2][0])
        (args.out_dir / "section_c.bin").write_bytes(out)
        decoded.append({"name": "section_c", "size": len(out)})
    for index, (offset, out) in enumerate(blocks(miss_payload(data))):
        name = f"block{index:02d}"
        (args.out_dir / f"{name}.bin").write_bytes(out)
        decoded.append({"name": name, "payload_offset": f"0x{offset:X}"})
    for entry in decoded:
        blob = (args.out_dir / f"{entry['name']}.bin").read_bytes()
        entry["size"] = len(blob)
        entry["sha256"] = hashlib.sha256(blob).hexdigest()
    report = {
        "file": args.st2.name,
        "sections": [{"offset": f"0x{o:X}", "size": f"0x{s:X}"} for o, s in found],
        "miss_sectors": len(miss_sectors(data)),
        "decoded": decoded,
    }
    (args.out_dir / "stream.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({"file": args.st2.name, "blocks": len(decoded)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
