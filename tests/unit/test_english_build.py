from __future__ import annotations

import hashlib

import pytest

from tools.disc.build_english import compile_records, mmpack_patches
from tools.disc.english_mode import (
    PATCHES,
    apply,
    as_bytes,
    check,
    patches_v3,
    patches_v4,
)
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
