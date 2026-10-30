from __future__ import annotations

import pytest

from tools.disc.english_mode import (
    ENDING_BIT,
    ENGLISH,
    FIXED_LOW,
    FIXED_TABLE,
    LITERALS_V4,
    MCED_RELOCATION,
    MCED_SCRIPTS,
    PATCHES,
    SELECTOR_READ_V2,
    SELECTOR_V3,
    SELECTOR_V4,
    SLOTS,
    apply,
    as_bytes,
    check,
    ending_slot_patches,
    mced_english_scripts,
    patches_v3,
    patches_v4,
    slot_patches,
)
from tools.sh2.disasm import decode

BASE = 0x06066000
# The fixed-index table as the game holds it (EXP-0027): 19 words, values 0-7.
FIXED = [5, 2, 3, 0, 7, 1, 0, 1, 0, 1, 7, 5, 4, 0, 7, 0, 0, 6, 5]
LITERAL = 0x060666D8  # holds FIXED_TABLE


def original_memory() -> bytearray:
    memory = bytearray(0x1000)
    for address, old, _ in patches_v3([]):
        data = as_bytes(old)
        memory[address - BASE : address - BASE + len(data)] = data
    for slot, value in enumerate(FIXED):
        offset = FIXED_TABLE - BASE + 2 * slot
        memory[offset : offset + 2] = value.to_bytes(2, "big")
    literal = LITERAL - BASE
    memory[literal : literal + 4] = FIXED_TABLE.to_bytes(4, "big")
    for address, old, _ in (SELECTOR_V4, LITERALS_V4):
        data = as_bytes(old)
        memory[address - BASE : address - BASE + len(data)] = data
    return memory


def test_slot_patches_set_the_high_byte_only() -> None:
    assert slot_patches([10, 9]) == [
        (FIXED_TABLE + 18, "00", f"{ENGLISH:02X}"),
        (FIXED_TABLE + 20, "00", f"{ENGLISH:02X}"),
    ]


@pytest.mark.parametrize("slot", [-1, SLOTS])
def test_slot_patches_reject_unknown_slots(slot: int) -> None:
    with pytest.raises(ValueError, match="outside"):
        slot_patches([slot])


def test_v3_keeps_version_2_outside_the_selector() -> None:
    assert patches_v3([])[1:] == PATCHES[1:]
    assert SELECTOR_V3[0] == PATCHES[0][0]
    assert SELECTOR_V3[1] == PATCHES[0][1]
    assert len(as_bytes(SELECTOR_V3[2])) == len(as_bytes(SELECTOR_V3[1]))


def test_apply_v3_marks_only_the_chosen_slots() -> None:
    memory = original_memory()
    chosen = patches_v3([9, 10])
    assert check(bytes(memory), BASE, patches=chosen) == []
    apply(memory, BASE, patches=chosen)
    assert check(bytes(memory), BASE, new=True, patches=chosen) == []
    for slot, value in enumerate(FIXED):
        offset = FIXED_TABLE - BASE + 2 * slot
        high = ENGLISH if slot in (9, 10) else 0
        assert memory[offset : offset + 2] == bytes([high, value])


def test_apply_v3_refuses_a_slot_already_marked() -> None:
    memory = original_memory()
    memory[FIXED_TABLE - BASE + 18] = 0x01
    with pytest.raises(ValueError, match="original bytes differ"):
        apply(memory, BASE, patches=patches_v3([9]))


def test_v3_selector_decodes_as_designed() -> None:
    memory = original_memory()
    apply(memory, BASE, patches=patches_v3([9]))
    lines = [decode(bytes(memory), BASE, 0x06066668 + 2 * i)[1] for i in range(11)]
    assert lines == [
        "mov.l @(0x060666D8),r1   ! 0x060666E0",
        "mov.w @(6,gbr),r0",
        "mov.b @(r0,r1),r2",
        "tst r2,r2",
        "mov.w @(2,gbr),r0",
        "bt 0x06066682",
        "and #0x07,r0",
        "mov #92,r1",
        "add r6,r1",
        "bra 0x06066682",
        "mov.b r2,@r1",
    ]


def test_fixed_low_matches_the_test_table() -> None:
    assert FIXED_LOW == FIXED


def test_ending_slot_patches_set_bit_7_of_the_low_byte() -> None:
    assert ending_slot_patches([16, 0]) == [
        (FIXED_TABLE + 1, "05", "85"),
        (FIXED_TABLE + 33, "00", "80"),
    ]


@pytest.mark.parametrize("slot", [-1, SLOTS])
def test_ending_slot_patches_reject_unknown_slots(slot: int) -> None:
    with pytest.raises(ValueError, match="outside"):
        ending_slot_patches([slot])


def test_v4_needs_english_win_quotes_for_an_english_ending() -> None:
    with pytest.raises(ValueError, match="need English win quotes"):
        patches_v4([9], [16])


def test_v4_replaces_only_the_ending_selector() -> None:
    v4 = patches_v4([9, 16], [16])
    v3 = patches_v3([9, 16])
    assert SELECTOR_READ_V2 in v3
    assert SELECTOR_READ_V2 not in v4
    assert [p for p in v3 if p != SELECTOR_READ_V2] == v4[: len(v3) - 1]
    for _, old, new in (SELECTOR_V4, LITERALS_V4):
        assert len(as_bytes(old)) == len(as_bytes(new))


def test_apply_v4_marks_only_the_ending_slot() -> None:
    memory = original_memory()
    chosen = patches_v4([9, 16], [16])
    assert check(bytes(memory), BASE, patches=chosen) == []
    apply(memory, BASE, patches=chosen)
    for slot, value in enumerate(FIXED):
        offset = FIXED_TABLE - BASE + 2 * slot
        high = ENGLISH if slot in (9, 16) else 0
        low = value | ENDING_BIT if slot == 16 else value
        assert memory[offset : offset + 2] == bytes([high, low])


def test_v4_selector_decodes_as_designed() -> None:
    memory = original_memory()
    apply(memory, BASE, patches=patches_v4([16], [16]))
    lines = [decode(bytes(memory), BASE, 0x060668C2 + 2 * i)[1] for i in range(15)]
    assert lines == [
        "mov.l @(0x0606690C),r7   ! 0x060854F8",
        f"mov.l @(0x06066910),r1   ! 0x{FIXED_TABLE + 1:08X}",
        "mov.w @(6,gbr),r0",
        "mov.b @(r0,r1),r2",
        "add r0,r0",
        "mov.l @(r0,r7),r0",
        "cmp/pz r2",
        "bt 0x060668DE",
        "mov.w @(0x06066914),r1   ! 0xFE60",
        "add r1,r0",
        "mov #92,r1",
        "add r6,r1",
        "mov #2,r2",
        "mov.b r2,@r1",
        "nop",
    ]


def mced(bases: list[int]) -> bytearray:
    data = bytearray(0x3000)
    for slot, base in enumerate(bases):
        offset = MCED_SCRIPTS + 4 * slot
        data[offset : offset + 4] = base.to_bytes(4, "big")
        header = base + MCED_RELOCATION
        data[header : header + 4] = bytes.fromhex("0008 0038".replace(" ", ""))
    return data


def test_mced_english_scripts_rewrites_the_language_0_header_word() -> None:
    bases = [0x2800 + 0x40 * s for s in range(SLOTS)]
    data = mced(bases)
    header = bases[16] + MCED_RELOCATION
    assert mced_english_scripts(bytes(data), [16]) == [
        (header, bytes.fromhex("0008"), bytes.fromhex("0038"))
    ]


def test_mced_english_scripts_refuses_a_shared_script() -> None:
    bases = [0x2800 + 0x40 * s for s in range(SLOTS)]
    bases[9] = bases[8]
    data = mced(bases)
    with pytest.raises(ValueError, match="shares its script with \\[8\\]"):
        mced_english_scripts(bytes(data), [9])
    assert len(mced_english_scripts(bytes(data), [8, 9])) == 1


def test_mced_english_scripts_switches_a_listed_shared_script() -> None:
    bases = [0x2800 + 0x40 * s for s in range(SLOTS)]
    bases[8] = bases[9]
    data = mced(bases)
    header = bases[9] + MCED_RELOCATION
    assert mced_english_scripts(bytes(data), [9], shared=[8]) == [
        (header, bytes.fromhex("0008"), bytes.fromhex("0038"))
    ]


def test_mced_english_scripts_refuses_a_shared_slot_that_shares_nothing() -> None:
    bases = [0x2800 + 0x40 * s for s in range(SLOTS)]
    data = mced(bases)
    with pytest.raises(ValueError, match="slot 8 shares no script"):
        mced_english_scripts(bytes(data), [9], shared=[8])
    with pytest.raises(ValueError, match="shared slot 9 is an ending slot"):
        mced_english_scripts(bytes(data), [9], shared=[9])
