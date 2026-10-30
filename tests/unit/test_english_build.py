from __future__ import annotations

import hashlib

import pytest

from tools.disc.build_english import compile_records, mmpack_patches, with_names
from tools.disc.english_mode import (
    MCED_RELOCATION,
    MCED_SCRIPTS,
    PATCHES,
    apply,
    as_bytes,
    check,
    patches_v3,
    patches_v4,
)
from tools.disc.names import US_SITES, edit_lines, label_cells, label_edits
from tools.text.caption import compile_record

BASE = 0x06066000


def memory_with(originals: bool) -> bytearray:
    memory = bytearray(0x1000)
    for address, old, new in PATCHES:
        data = as_bytes(old if originals else new)
        memory[address - BASE : address - BASE + len(data)] = data
    return memory


def test_apply_writes_every_site_and_check_confirms() -> None:
    memory = memory_with(originals=True)
    assert check(bytes(memory), BASE) == []
    apply(memory, BASE)
    assert check(bytes(memory), BASE, new=True) == []
    assert bytes(memory) == bytes(memory_with(originals=False))


def test_apply_refuses_unexpected_bytes() -> None:
    memory = memory_with(originals=True)
    memory[PATCHES[0][0] - BASE] ^= 0xFF
    with pytest.raises(ValueError, match="original bytes differ"):
        apply(memory, BASE)


def spec_for(program: bytes, addresses: list[int]) -> dict[str, object]:
    return {
        "records": [
            {
                "english_record": index,
                "source_address": f"{address:#x}",
                "sha256": hashlib.sha256(program[address : address + 100]).hexdigest(),
            }
            for index, address in enumerate(addresses)
        ]
    }


def test_compile_records_reproduces_sources() -> None:
    first = compile_record(["Practice more.", "Then come back!"])
    second = compile_record(["Who taught you?", "Next time, listen."])
    program = bytes(16) + first + bytes(8) + second
    spec = spec_for(program, [16, 124])
    assert compile_records(spec, program, fix_grammar=False) == first + second


def test_compile_records_checks_hashes() -> None:
    record = compile_record(["A", "B"])
    program = bytes(4) + record
    spec = spec_for(program, [4])
    tampered = bytes(4) + compile_record(["A", "C"])
    with pytest.raises(ValueError, match="source hash differs"):
        compile_records(spec, tampered, fix_grammar=False)


def test_grammar_fix_is_opt_in() -> None:
    record = compile_record(["Your a fool.", ""])
    program = record
    spec = spec_for(program, [0])
    records = spec["records"]
    assert isinstance(records, list)
    records[0]["grammar_fix"] = ["You're a fool.", ""]
    assert compile_records(spec, program, fix_grammar=False) == record
    fixed = compile_records(spec, program, fix_grammar=True)
    assert fixed == compile_record(["You're a fool.", ""])


def character(slot: int, mc_file: str) -> dict[str, object]:
    return {"arcade_slot": slot, "mc_file": mc_file}


def test_version_3_marks_every_spec_slot() -> None:
    specs = [character(9, "MC09.SHP;1"), character(10, "MC0A.SHP;1")]
    assert mmpack_patches(specs, 3) == patches_v3([9, 10])


def test_version_2_builds_ryu_alone() -> None:
    assert mmpack_patches([character(9, "MC09.SHP;1")], 2) == PATCHES
    with pytest.raises(ValueError, match="Ryu"):
        mmpack_patches([character(10, "MC0A.SHP;1")], 2)
    with pytest.raises(ValueError, match="Ryu"):
        mmpack_patches([character(9, "MC09.SHP;1"), character(10, "MC0A.SHP;1")], 2)


@pytest.mark.parametrize(
    "specs",
    [
        [character(9, "MC09.SHP;1"), character(9, "MC0A.SHP;1")],
        [character(9, "MC09.SHP;1"), character(10, "MC09.SHP;1")],
    ],
)
def test_rejects_repeated_slot_or_file(specs: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError, match="appears twice"):
        mmpack_patches(specs, 3)


def test_rejects_unknown_patch_version() -> None:
    with pytest.raises(ValueError, match="unknown patch version"):
        mmpack_patches([character(9, "MC09.SHP;1")], 5)


def win(slot: int, mc_file: str, table: str = "0x2a00") -> dict[str, object]:
    return {"arcade_slot": slot, "mc_file": mc_file, "table_offset": table}


def ending(slot: int, mc_file: str, table: str = "0x2a00") -> dict[str, object]:
    return {**win(slot, mc_file, table), "kind": "ending"}


def test_version_4_marks_endings_for_ending_specs_only() -> None:
    specs = [win(9, "MC09.SHP;1"), win(16, "MC10.SHP;1"), ending(16, "MC10.SHP;1")]
    assert mmpack_patches(specs, 4) == patches_v4([9, 16], [16])


def test_ending_specs_need_version_4() -> None:
    specs = [win(16, "MC10.SHP;1"), ending(16, "MC10.SHP;1")]
    with pytest.raises(ValueError, match="need patch version 4"):
        mmpack_patches(specs, 3)


@pytest.mark.parametrize(
    "specs",
    [
        [win(9, "MC09.SHP;1"), ending(16, "MC10.SHP;1")],
        [win(16, "MC09.SHP;1"), ending(16, "MC10.SHP;1")],
    ],
)
def test_ending_needs_its_win_quote_spec(specs: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError, match="no win-quote spec"):
        mmpack_patches(specs, 4)


def test_ending_and_win_tables_must_agree() -> None:
    specs = [win(16, "MC10.SHP;1"), ending(16, "MC10.SHP;1", "0x2a02")]
    with pytest.raises(ValueError, match="table offsets differ"):
        mmpack_patches(specs, 4)


def test_a_win_and_an_ending_spec_may_share_a_file() -> None:
    specs = [win(16, "MC10.SHP;1"), ending(16, "MC10.SHP;1")]
    assert mmpack_patches(specs, 4) == patches_v4([16], [16])


def test_names_us_adds_one_region_read_per_site() -> None:
    patches = with_names(patches_v4([0, 16], [16]), "us")
    added = patches[len(patches_v4([0, 16], [16])) :]
    assert [a for a, _, _ in added] == sorted(US_SITES)
    assert all((old, new) == ("00BD", "E002") for _, old, new in added)


def test_names_none_and_saturn_add_no_code() -> None:
    assert with_names(PATCHES, "none") == PATCHES
    assert with_names(PATCHES, "saturn") == PATCHES
    with pytest.raises(ValueError, match="unknown"):
        with_names(PATCHES, "japan")


def test_name_edits_recompile_the_record_and_are_logged() -> None:
    record = compile_record(["Lord Bison must", "be protected!"])
    spec = spec_for(record, [0])
    log: list[dict[str, object]] = []
    edits = {0: [(0, "Bison", "Vega")]}
    built = compile_records(spec, record, False, edits, log)
    assert built == compile_record(["Lord Vega must", "be protected!"])
    assert log[0]["edits"] == [[0, "Bison", "Vega"]]
    assert log[0]["source_sha256"] == hashlib.sha256(record).hexdigest()


def test_name_edits_need_one_occurrence_and_an_existing_record() -> None:
    assert edit_lines(["Bison", "x"], [(0, "Bison", "Vega")]) == ["Vega", "x"]
    with pytest.raises(ValueError, match="0 times"):
        edit_lines(["Vega", "x"], [(0, "Bison", "Vega")])
    with pytest.raises(ValueError, match="2 times"):
        edit_lines(["Bison Bison", "x"], [(0, "Bison", "Vega")])
    record = compile_record(["A", "B"])
    with pytest.raises(ValueError, match="missing records"):
        compile_records(spec_for(record, [0]), record, False, {1: [(0, "A", "C")]})


def test_label_cells_are_16_bit_ascii_padded_to_16() -> None:
    cells = label_cells("Balrog")
    assert len(cells) == 32
    assert cells[:4] == b"\0B\0a" and cells[-2:] == b"\0 "
    with pytest.raises(ValueError, match="does not fit"):
        label_cells("Charlie's friends")


def mced_with(script: bytes) -> bytes:
    """A decoded MCED with slot 0's script: 4 headers, all languages at + 8."""
    data = bytearray(0x3000)
    start = 0x2800
    value = start - MCED_RELOCATION
    data[MCED_SCRIPTS : MCED_SCRIPTS + 4] = value.to_bytes(4, "big")
    data[start : start + 8] = bytes.fromhex("0008 0008 0008 0008")
    data[start + 8 : start + 8 + len(script)] = script
    return bytes(data)


def test_label_edits_switch_pages_and_the_scene_end_word() -> None:
    # two scenes: (page 1 label 0x15, page 2 label 0x00) | (page 3 label 0x15)
    script = bytes.fromhex(
        "0004 0010  0180 0015 0180 0100 FFFF 0100  0180 0215 FFFF 0215"
    )
    saturn = {"labels": [{"slot": 0, "pages": [1, 3], "old": 0x15, "new": 0x11}]}
    edits = label_edits(mced_with(script), saturn, [0])
    start = 0x2808
    assert [e[0] - start for e in edits] == [7, 19, 23]
    assert all(e[1:] == (b"\x15", b"\x11") for e in edits)
    assert label_edits(mced_with(script), saturn, [1]) == []
    saturn["labels"][0]["pages"] = [1]
    with pytest.raises(ValueError, match="pages"):
        label_edits(mced_with(script), saturn, [0])


def test_name_patches_never_overlap_text_patches() -> None:
    slots = list(range(18))
    for patches in (PATCHES, patches_v3(slots), patches_v4(slots, slots)):
        with_names(patches, "us")
    with pytest.raises(ValueError, match="overlaps"):
        with_names([(0x060639E6, "00BD", "0009")], "us")
