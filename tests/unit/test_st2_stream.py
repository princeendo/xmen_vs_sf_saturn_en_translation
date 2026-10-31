from __future__ import annotations

import struct

from tools.disc.st2_stream import (
    SECTOR,
    TAG,
    blocks,
    lz_decode,
    miss_payload,
    sections,
)


def block(size: int, body: bytes) -> bytes:
    return struct.pack(">II", len(body), size) + body


def test_literals_and_a_copy_from_a_ring_position() -> None:
    # flags 0b0000_0001: seven literals, then a copy of 3 bytes from ring 0
    body = bytes([0x01]) + b"ABCDEFG" + bytes([0x00, 0x00])
    out, end = lz_decode(block(10, body))
    assert out == b"ABCDEFGABC"
    assert end == 8 + len(body)


def test_a_copy_reads_the_ring_not_a_distance_back() -> None:
    # ring position 2 after five literals is "C", not 2 bytes back ("DE")
    body = bytes([0x04]) + b"ABCDE" + bytes([0x00, 0x20])
    out, _ = lz_decode(block(8, body))
    assert out == b"ABCDECDE"


def test_the_starting_ring_is_read_before_it_is_written() -> None:
    body = bytes([0x80, 0xFF, 0xE0])
    out, _ = lz_decode(block(3, body))
    assert out == bytes(3)
    ring = bytearray(0x1000)
    ring[0xFFE:0x1000] = b"XY"
    out, _ = lz_decode(block(3, body), ring=bytes(ring))
    # the copy wraps to ring position 0, where its own first byte was written
    assert out == b"XYX"


def test_sections_payload_and_blocks() -> None:
    header = struct.pack(">II", SECTOR, 0) + bytes(SECTOR - 8)
    section = bytes(SECTOR)
    one = block(3, bytes([0x00]) + b"abc")
    stream = TAG + bytes(4) + one + bytes(SECTOR - len(TAG) - 4 - len(one))
    other = bytes(SECTOR)
    data = header + section + stream + other
    assert sections(data) == [(SECTOR, SECTOR)]
    payload = miss_payload(data)
    assert len(payload) == SECTOR - len(TAG)
    assert list(blocks(payload)) == [(4, b"abc")]
