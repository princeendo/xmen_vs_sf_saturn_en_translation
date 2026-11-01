from __future__ import annotations

import pytest

from tools.disc import continue_hints
from tools.disc.build_english import build_mmpack, with_extra
from tools.disc.continue_hints import (
    GAP_END,
    HINT_PAGES,
    ORDER,
    SIZE,
    TABLE,
    map_bytes,
    patches,
    table,
)
from tools.disc.english_mode import FLAG, as_bytes, patches_v4
from tools.disc.prs import compress_file, decompress_entries


def test_every_patch_keeps_its_size() -> None:
    for _, old, new in patches():
        assert len(as_bytes(old)) == len(as_bytes(new))


def test_each_index_shows_its_own_hints_pages() -> None:
    first = map_bytes()
    for index, pages in HINT_PAGES.items():
        assert (ORDER[first[index]], ORDER[first[index] + 1]) == pages


def test_the_starter_sets_the_english_byte_and_the_table_base() -> None:
    starter = as_bytes(continue_hints.STARTER[2])
    assert bytes.fromhex(f"E0{FLAG:02X}0614") in starter
    assert as_bytes(continue_hints.BASE_LITERAL[2]) == TABLE.to_bytes(4, "big")


def test_the_table_fits_the_gap_and_reads_each_record() -> None:
    program = bytearray(0x190000)
    for k, record in enumerate(range(270, 294)):
        at = continue_hints.ENGLISH_AREA + SIZE * k
        program[at : at + SIZE] = bytes([record - 270]) * SIZE
    data = table(bytes(program))
    assert len(data) == SIZE * len(ORDER) and TABLE + len(data) <= GAP_END
    assert [data[SIZE * k] for k in range(len(ORDER))] == [r - 270 for r in ORDER]


def test_it_combines_with_version_4_without_overlap() -> None:
    combined = with_extra(patches_v4([9], [9]), patches(), "continue-hints")
    assert len(combined) == len(patches_v4([9], [9])) + len(patches())


def test_appended_bytes_extend_the_first_segment() -> None:
    first, second = 0x06014000, 0x06014100
    header = (2).to_bytes(4, "big") + b"".join(
        dest.to_bytes(4, "big") + (0x40 // 4).to_bytes(4, "big")
        for dest in (first, second)
    )
    raw = compress_file(bytes(range(0x80)), header=header) + bytes(64)
    changes: list[dict[str, object]] = []
    rebuilt = build_mmpack(raw, changes, [], b"\xaa" * 8)
    new_header, decoded, _ = decompress_entries(rebuilt)
    assert int.from_bytes(new_header[8:12], "big") == (0x40 + 8) // 4
    assert decoded == bytes(range(0x40)) + b"\xaa" * 8 + bytes(range(0x40, 0x80))
    assert len(rebuilt) == len(raw) and changes[0]["header_offset"] == "0x8"
    with pytest.raises(ValueError, match="gap"):
        build_mmpack(raw, [], [], b"\xaa" * 0xC4)
