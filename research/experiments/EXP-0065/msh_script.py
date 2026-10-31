r"""EXP-0065: MSHvSF's section A script, frame and map decoders, under test on XvSF.

Copied from the MSHvSF repository, ``tools/disc/st2_stream.py`` at commit
``40b3ad0`` (last changed in ``3c6cbf5``): ``script_decode``, ``map_decode``,
the section parsers and ``script_frames``, unchanged. Every address, bit
meaning and array in them is an MSHvSF fact (its `EXP-0068`, `EXP-0070`,
`EXP-0073`); on XvSF each is a HYPOTHESIS until this experiment matches the
decoded arrays against RAM.
"""

from __future__ import annotations

from dataclasses import dataclass


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
