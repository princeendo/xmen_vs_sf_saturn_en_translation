from __future__ import annotations

import pytest

from tools.disc.english_mode import (
    ENGLISH,
    FIXED_TABLE,
    PATCHES,
    SELECTOR_V3,
    SLOTS,
    apply,
    as_bytes,
    check,
    patches_v3,
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
