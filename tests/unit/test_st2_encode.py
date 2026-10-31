from __future__ import annotations

import random
import struct

from tools.disc.st2_encode import lz_encode, map_encode, script_encode
from tools.disc.st2_stream import lz_decode, map_decode, script_decode


def sample(seed: int, size: int) -> bytes:
    rng = random.Random(seed)
    out = bytearray()
    while len(out) < size:
        if out and rng.random() < 0.6:
            start = rng.randrange(max(0, len(out) - 5000), len(out))
            out += out[start : start + rng.randrange(3, 40)]
        else:
            out += bytes(rng.randrange(4) for _ in range(rng.randrange(1, 9)))
    return bytes(out[:size])


def test_graphics_lz_round_trips_past_the_ring() -> None:
    data = sample(1, 20000)  # longer than the 0x1000 ring, with far copies
    encoded = lz_encode(data)
    compressed, size = struct.unpack_from(">II", encoded)
    assert size == len(data) and compressed == len(encoded) - 8
    assert lz_decode(encoded)[0] == data
    assert len(encoded) < len(data)


def copies(encoded: bytes) -> list[tuple[int, int]]:
    """(ring position, length) of each copy token, in order."""
    found, position, produced = [], 8, 0
    size = struct.unpack_from(">I", encoded, 4)[0]
    while produced < size:
        flags = encoded[position]
        position += 1
        for bit in range(8):
            if produced >= size:
                break
            if flags & (0x80 >> bit):
                word = int.from_bytes(encoded[position : position + 2], "big")
                found.append((word >> 4, (word & 0xF) + 3))
                produced += (word & 0xF) + 3
                position += 2
            else:
                produced += 1
                position += 1
    return found


def test_a_copy_is_written_as_a_ring_position() -> None:
    # "ABCDEFGHIJ" then copies of it: ring positions 0 and 3, not distances
    assert copies(lz_encode(b"ABCDEFGHIJ" * 3)) == [(0, 3), (3, 17)]


def test_script_and_map_codecs_round_trip() -> None:
    script = sample(2, 30000)
    assert script_decode(script_encode(script))[0] == script
    rng = random.Random(3)
    words = [0xFFFF] * 0x2000
    for k in range(0x400, 0x600):
        words[k] = rng.randrange(0x40) * 4
    encoded = map_encode(words)
    assert map_decode(encoded, 0)[0] == words
