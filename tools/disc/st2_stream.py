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
map decoders (``script_decode``, ``map_decode``, ``script_frames``) are
copied unchanged from the same file: on XvSF they decode all eight scripts to
their end, and replaying the map updates and palette records reproduces the
game's map arrays (``0x06033020``) and source palette (``0x0602E020``)
exactly (`EXP-0065`).

The output is game-derived data: write it under ``local/`` only (``AGENTS.md``
rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
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


def script_decode(data: bytes, start: int = 0) -> tuple[bytes, int]:
    """Decode section A's bit-flag LZ (``0x06022750``); return (script, end offset).

    Flag bits are read LSB first from bytes. 1 = literal byte. 0 then 0 = short
    copy: two more flag bits (MSB first) give length 2-5, then a byte b gives the
    offset ``b - 0x100``. 0 then 1 = long copy: a big-endian word ``w`` gives the
    offset ``(w | ~0xFFFF) >> 3`` (arithmetic); length ``(w & 7) + 2`` if nonzero,
    else the next byte c gives ``c + 1``, and c = 0 ends the stream.
    """
    position, out, flags, left = start, bytearray(), 0, 0

    def bit() -> int:
        nonlocal position, flags, left
        if left == 0:
            flags, left = data[position], 8
            position += 1
        value = flags & 1
        flags >>= 1
        left -= 1
        return value

    while True:
        if bit():
            out.append(data[position])
            position += 1
            continue
        if not bit():
            length = ((bit() << 1) | bit()) + 2
            offset = data[position] - 0x100
            position += 1
        else:
            word = (data[position] << 8) | data[position + 1]
            position += 2
            offset = ((word | 0xFFFF0000) - (1 << 32)) >> 3
            if word & 7:
                length = (word & 7) + 2
            else:
                count = data[position]
                position += 1
                if count == 0:
                    return bytes(out), position
                length = count + 1
        source = len(out) + offset
        for k in range(length):
            out.append(out[source + k])


def map_decode(data: bytes, start: int) -> tuple[list[int], int]:
    """Decode one word-LZ map update (``0x0602234C``); return (0x2000 words, end).

    Control bytes are read LSB first. 1 = literal big-endian word. 0 = copy back
    in the output, from a byte b:

    - b >= 0x80: distance ``(b & 15) + 1``, length ``((b >> 4) & 7) + 1``;
    - 0 < b < 0x80: length b, then a byte d gives distance ``d + 1``;
    - b == 0: a word w; mode ``w >> 13``: 0 = length ``(w & 0x1FFF) + 1`` and a
      word distance + 1; 1 = the same length and a byte distance + 1;
      2 = distance ``(w & 0x1FFF) + 1`` and a byte length + 1.

    The game copies every word except ``0xFFFF`` (= keep) into its target array.
    """
    position, out = start, list[int]()
    while len(out) < 0x2000:
        control = data[position]
        position += 1
        for _ in range(8):
            if len(out) >= 0x2000:
                break
            if control & 1:
                out.append((data[position] << 8) | data[position + 1])
                position += 2
            else:
                byte = data[position]
                position += 1
                if byte >= 0x80:
                    distance, length = (byte & 15) + 1, ((byte >> 4) & 7) + 1
                elif byte:
                    length, distance = byte, data[position] + 1
                    position += 1
                else:
                    word = (data[position] << 8) | data[position + 1]
                    position += 2
                    mode = word >> 13
                    if mode == 0:
                        length = (word & 0x1FFF) + 1
                        distance = ((data[position] << 8) | data[position + 1]) + 1
                        position += 2
                    elif mode == 1:
                        length, distance = (word & 0x1FFF) + 1, data[position] + 1
                        position += 1
                    elif mode == 2:
                        distance, length = (word & 0x1FFF) + 1, data[position] + 1
                        position += 1
                    else:
                        raise ValueError(f"map copy mode {mode} at 0x{position:X}")
                source = len(out) - distance
                if source < 0:
                    raise ValueError("map copy reaches before the output start")
                for k in range(length):
                    out.append(out[source + k])
            control >>= 1
    if len(out) != 0x2000:
        raise ValueError("map update overran 0x2000 words")
    return out, position


MAP_TARGETS = {5: 0x0602F020, 6: 0x06033020, 7: 0x06037020}  # frame bit -> array


@dataclass(frozen=True)
class Section:
    kind: str  # "deltas", "palette", "map", "objects"
    start: int
    end: int
    target: int = 0  # map: destination array


@dataclass(frozen=True)
class Frame:
    offset: int
    word: int
    sections: tuple[Section, ...]


def _palette_end(data: bytes, p: int) -> int:
    """End of a palette section (``0x0602214C``): a flag byte, then up to four
    lists. Bits 0, 2 and 4 select 3-byte records (fade up, fade down, set
    brightness) and bit 5 ``[u16 index delta][u16 count][count words]``
    records; each list ends at a byte of ``0xFF``."""
    flags = data[p]
    p += 1
    for bit in (0, 2, 4):
        if flags >> bit & 1:
            while data[p] != 0xFF:
                p += 3
            p += 1
    if flags >> 5 & 1:
        while data[p] != 0xFF:
            p += 4 + 2 * int.from_bytes(data[p + 2 : p + 4], "big")
        p += 1
    return p


def _objects_end(data: bytes, p: int) -> int:
    """End of an object list (``0x06022426``): records with a big-endian header
    word, until a byte of ``0xFF``. Bits 10-12 of the header select the
    record's extra bytes (bits 13-15 a subtype for types 6 and 7)."""
    while data[p] != 0xFF:
        word = int.from_bytes(data[p : p + 2], "big")
        p += 2
        kind, sub = (word >> 10) & 7, (word >> 13) & 7
        if kind == 0:
            p += 6
        elif kind in (2, 3, 4):
            p += 1
        elif kind == 5:
            p += 2
        elif kind == 6:
            p += 1 + (0, 1, 1, 1, 2)[sub]
        elif kind == 7:
            p += (6, 5, 2, 6)[sub]
    return p + 1


def script_frames(data: bytes) -> list[Frame]:
    """Parse a decoded section-A script into frames (``0x06021FE4``).

    Each frame is a big-endian command word: 0 is an idle frame and 0xFFFF
    ends the script. Its bits select sections, read in bit order: 0 (a mask
    byte, then a word per set bit of 4), 1 (two words), 2 (a mask byte, then
    per set bit of 6 a byte, or a zero byte and a word), 3 (two words),
    4 (palette), 5-7 (word-LZ map updates, ``map_decode``), 8 (object list),
    9 (a mask byte, then a word per set bit of 6), 10 (a flag only).
    """
    frames, p = [], 0
    while True:
        start = p
        word = int.from_bytes(data[p : p + 2], "big")
        p += 2
        if word == 0xFFFF:
            frames.append(Frame(start, word, ()))
            return frames
        sections = []
        for bit in range(10):
            if not word >> bit & 1:
                continue
            begin = p
            if bit == 0:
                mask = data[p]
                p += 1 + 2 * bin(mask & 0xF).count("1")
                kind = "deltas"
            elif bit in (1, 3):
                p += 4
                kind = "deltas"
            elif bit == 2:
                mask = data[p]
                p += 1
                for k in range(6):
                    if mask >> k & 1:
                        p += 3 if data[p] == 0 else 1
                kind = "deltas"
            elif bit == 9:
                mask = data[p]
                p += 1 + 2 * bin(mask & 0x3F).count("1")
                kind = "deltas"
            elif bit == 4:
                p = _palette_end(data, p)
                kind = "palette"
            elif bit in MAP_TARGETS:
                p = map_decode(data, p)[1]
                sections.append(Section("map", begin, p, MAP_TARGETS[bit]))
                continue
            else:
                p = _objects_end(data, p)
                kind = "objects"
            sections.append(Section(kind, begin, p))
        frames.append(Frame(start, word, tuple(sections)))


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
