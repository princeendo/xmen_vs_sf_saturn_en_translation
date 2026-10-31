from __future__ import annotations

from itertools import pairwise

import pytest

from tools.disc import boss_boxes
from tools.disc.boss_boxes import (
    BASE,
    FREE,
    MC08,
    RECORD,
    SETUP,
    first_index,
    index_patch,
    lines,
    load,
    records,
)
from tools.disc.build_english import build_mc, special_patches
from tools.disc.english_mode import FIXED_TABLE, FLAG, as_bytes
from tools.disc.prs import compress_file


def words(text: str) -> list[int]:
    data = as_bytes(text)
    return [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)]


def test_setup_keeps_its_size_and_sets_the_flag_and_base() -> None:
    address, old, new = SETUP
    code = words(new)
    assert len(as_bytes(old)) == len(as_bytes(new))
    assert code[0] == 0xE100 | FLAG  # mov #FLAG,r1
    # mov.l @(disp,pc),r0 at word 4: the literal it loads is MC08 + BASE
    pc = address + 2 * 4
    literal = (pc & ~3) + 4 + 4 * (code[4] & 0xFF)
    at = (literal - address) // 2
    assert code[4] >> 8 == 0xD0
    assert (code[at] << 16 | code[at + 1]) == MC08 + BASE
    # bra at word 5 rejoins the original store at 0x0606681E; its delay slot is a nop
    bra = address + 2 * 5
    displacement = code[5] & 0xFFF
    assert code[5] >> 12 == 0xA and bra + 4 + 2 * displacement == 0x0606681E
    assert code[6] == 0x0009


def test_every_slot_has_a_triple_inside_the_free_ranges() -> None:
    index = first_index()
    assert sorted(index) == list(range(20))
    assert index[8] == index[7] and index[18] == index[19] == index[11]
    spans = sorted(
        (BASE + RECORD * index[s], BASE + RECORD * (index[s] + 3))
        for s in boss_boxes.ORDER
    )
    for start, end in spans:
        assert any(a <= start and end <= b for a, b in FREE)
    for (_, end), (start, _) in pairwise(spans):
        assert end <= start


def test_index_patch_has_one_byte_per_slot() -> None:
    _, old, new = index_patch()
    assert len(as_bytes(old)) == len(as_bytes(new)) == 20


def test_records_follow_the_name_variant_in_slots_14_to_16() -> None:
    data = load()
    assert lines(data, 14, 1, "us")[0].startswith("Bison")
    assert lines(data, 14, 1, "saturn")[0].startswith("Vega")
    assert lines(data, 16, 1, "none") == lines(data, 16, 1, "us")
    assert lines(data, 9, 2, "us") == lines(data, 0, 2, "saturn")
    us, saturn = records(data, "us"), records(data, "saturn")
    assert len(us) == len(saturn) == 51
    assert sum(us[k] != saturn[k] for k in us) == 3


def test_build_mc_writes_extra_edits_and_refuses_overlaps() -> None:
    decoded = bytes(0x400)
    raw = compress_file(decoded, size=0x400)
    changes: list[dict[str, object]] = []
    build_mc(raw, b"\x01" * 4, 0x10, "T", changes, {0x20: b"\x02" * 4})
    assert [c["decompressed_offset"] for c in changes] == ["0x10", "0x20"]
    with pytest.raises(ValueError, match="overlap"):
        build_mc(raw, b"\x01" * 4, 0x10, "T", [], {0x12: b"\x02" * 4})


def test_special_needs_version_4_mc08_and_chun_lis_shared_ending() -> None:
    win = {"mc_file": "MC08.SHP;1", "arcade_slot": 8}
    ending = {"kind": "ending", "arcade_slot": 11, "mced_shared_with": [18]}
    with pytest.raises(ValueError, match="version 4"):
        special_patches([win, ending], 3)
    with pytest.raises(ValueError, match="MC08"):
        special_patches([ending], 4)
    with pytest.raises(ValueError, match="Chun-Li"):
        special_patches([win], 4)
    patches = special_patches([win, ending], 4)
    alpha = {address: new for address, _, new in patches}
    assert alpha[FIXED_TABLE + 36] == "02" and alpha[FIXED_TABLE + 37] == "85"
