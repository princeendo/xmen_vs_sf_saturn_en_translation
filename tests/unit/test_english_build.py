from __future__ import annotations

import hashlib

import pytest

from tools.disc.build_english import compile_records
from tools.disc.english_mode import PATCHES, apply, as_bytes, check
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
