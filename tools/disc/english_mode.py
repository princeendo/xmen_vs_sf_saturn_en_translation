"""The code patch that turns on the arcade's English quote mode for chosen speakers.

Promoted from `research/experiments/EXP-0023/english_patch.py` (version 2,
confirmed in `EXP-0023`) unchanged except for this paragraph and the removal of
the version-1 table.

The Saturn quote code (in ``MMPACK.PCA``, loaded to WRAM-H from ``0x06014BA0``)
keeps the arcade's English branch, which the global language word
(R11 + ``0xD47A``, always 0 on the Saturn) selects (`EXP-0022`, `EXP-0023`).
Turning the global word on would also switch hints and endings, which have no
English data on the Saturn. So this patch makes English mode a property of
the win-quote task only:

* **Win-quote selector** (``0x06066668``-``0x06066686``, around the two
  literals at ``0x0606667E``/``0x06066680``; the remap-table pointer at
  ``0x06066684`` is no longer loaded).
  - If the speaker's slot x 2 (``@(6,gbr)``) is ``ENGLISH_SLOT2`` (Ryu,
    slot 9), the index becomes ``r & 7``, which equals the remap table
    ``[0..7, 0..7]``, and the byte at task + ``FLAG`` is set to 2.
  - Any other slot keeps ``r`` (0-15) and the flag stays 0, so its Japanese
    records render as before. Version 1 of this patch switched every
    character and drew other characters' Japanese quotes in the English grid
    (`EXP-0023` play check).
  - Both cases leave r0 = index, r14 = -1 and T = 1, as the original
    no-remap path did, then continue at ``0x06066692``.
* **Fixed-index path** (``0x06066690``). After storing its index, it branches
  back into the same slot test, as the arcade's English mode would also use
  the fixed index.
* **Renderer** (``0x06066948`` onward). Its six reads of the global words
  (five of the language word, one of the size word) read the task byte
  instead (``mov.b @(r0,r12),r0``; r12 is the task). The two literals they
  load become ``FLAG``.
* **Ending selector** (``0x060668C4``). It shares the renderer's literal, so
  its read of the language word becomes ``mov #0,r0``, the value it always
  read.

Hint, ending and other tasks are cleared before setup, so their flag byte is
0 and they render as before. Each entry is (WRAM-H address, original bytes,
new bytes); the originals are checked before any write.
"""

from __future__ import annotations

FLAG = 0x5C  # task byte, unwritten between quote setup and release (EXP-0023)
ENGLISH_SLOT2 = 0x12  # slot x 2 of the characters with English records: Ryu (9)
CODE_BASE = 0x06014BA0  # MMPACK.PCA's decoded stream loads here

PATCHES: list[tuple[int, str, str]] = [
    # win-quote selector: Ryu's slot -> index = r & 7 and task+FLAG = 2;
    # other slots -> index = r. Then r14 = -1, T = 1, continue at 0x06066692.
    (
        0x06066668,
        "90E2 00BD 2008 3EEA 890E D104 C501 001C C003 A009 0009",
        f"C503 88{ENGLISH_SLOT2:02X} C501 8B08 C907 E1{FLAG:02X} 316C E202 2120"
        " A002 0009",
    ),
    (0x06066682, "0009 0606 6718", "EEFF A005 0018"),
    # fixed-index path: after storing its index, rejoin the slot test
    (0x06066690, "C403", "AFEA"),
    # renderer: size and language tests read the task flag byte
    (0x0606696A, "00BD", "00CC"),
    (0x0606699E, "00BD", "00CC"),
    (0x060669CC, "00BD", "00CC"),
    (0x060669F6, "00BD", "00CC"),
    (0x06066A10, "00BD", "00CC"),
    (0x06066A3A, "00BD", "00CC"),
    (0x06066A70, "D478", f"00{FLAG:02X}"),  # size literal (0x06066A72 is another)
    (0x06066A74, "D47A", f"00{FLAG:02X}"),  # language literal
    # ending selector: shares the literal; keep reading 0
    (0x060668C4, "00BD", "E000"),
]


def as_bytes(text: str) -> bytes:
    return bytes.fromhex(text.replace(" ", ""))


def check(memory: bytes, base: int, new: bool = False) -> list[str]:
    """Return a mismatch line for every patch whose bytes differ from the expected."""
    problems = []
    for address, old, replacement in PATCHES:
        expected = as_bytes(replacement if new else old)
        offset = address - base
        found = memory[offset : offset + len(expected)]
        if found != expected:
            problems.append(
                f"{address:#010x}: found {found.hex()}, expected {expected.hex()}"
            )
    return problems


def apply(memory: bytearray, base: int) -> None:
    problems = check(bytes(memory), base)
    if problems:
        raise ValueError("original bytes differ: " + "; ".join(problems))
    for address, _, replacement in PATCHES:
        data = as_bytes(replacement)
        memory[address - base : address - base + len(data)] = data
