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

``PATCHES`` is version 2 (one English slot in code), still used by
`tools.disc.build_english`. Version 3 (``patches_v3``, below; `RE-006`,
`EXP-0027`) keeps the English slots in a table instead.
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


# Version 3 (`RE-006`, `EXP-0027`): the English slots are data, not code.
#
# The fixed-index table (``FIXED_TABLE``, one big-endian word per slot, 19
# slots) holds values 0-7, so each word's high byte is spare. Only the
# fixed-index path reads the table (``0x06066688``, through the literal at
# ``0x060666D8``); arcade play never takes it (`EXP-0027`). Version 3 stores
# the slot's quote language in that high byte: 0 for Japanese, ``ENGLISH`` (the
# arcade's language-word value) for English. The selector test reads it with
# ``mov.b @(r0,r1),r2`` and, for English, stores it as the task flag. The
# fixed path keeps the whole word, and ``and #7`` drops the high byte.
#
#   06066668 D11B  mov.l @(0x060666D8),r1   ; FIXED_TABLE
#   0606666A C503  mov.w @(6,gbr),r0       ; slot x 2
#   0606666C 021C  mov.b @(r0,r1),r2       ; high byte: language
#   0606666E 2228  tst r2,r2
#   06066670 C501  mov.w @(2,gbr),r0       ; r, or the fixed word
#   06066672 8906  bt 0x06066682           ; Japanese: index unchanged
#   06066674 C907  and #7,r0               ; English: r & 7 (the remap)
#   06066676 E15C  mov #FLAG,r1
#   06066678 316C  add r6,r1               ; r6 = task
#   0606667A A002  bra 0x06066682
#   0606667C 2120  mov.b r2,@r1            ; task + FLAG = ENGLISH
#
# The rest of version 2 is unchanged, and the remap table at ``0x06066718``
# is not used. Adding a character is one byte: ``slot_patches``.
FIXED_TABLE = 0x060666E0
SLOTS = 19  # win-quote slots 0-18 (EXP-0008)
ENGLISH = 2  # the arcade's language word for English (EXP-0022)

SELECTOR_V3 = (
    0x06066668,
    "90E2 00BD 2008 3EEA 890E D104 C501 001C C003 A009 0009",
    f"D11B C503 021C 2228 C501 8906 C907 E1{FLAG:02X} 316C A002 2120",
)


def slot_patches(slots: list[int]) -> list[tuple[int, str, str]]:
    """The table bytes that make each slot in ``slots`` English (high byte 0 -> 2)."""
    for slot in slots:
        if not 0 <= slot < SLOTS:
            raise ValueError(f"slot {slot} is outside 0-{SLOTS - 1}")
    return [(FIXED_TABLE + 2 * slot, "00", f"{ENGLISH:02X}") for slot in sorted(slots)]


def patches_v3(slots: list[int]) -> list[tuple[int, str, str]]:
    """Version 3 code plus the slot table for ``slots``."""
    return [SELECTOR_V3, *PATCHES[1:], *slot_patches(slots)]


def as_bytes(text: str) -> bytes:
    return bytes.fromhex(text.replace(" ", ""))


def check(
    memory: bytes,
    base: int,
    new: bool = False,
    patches: list[tuple[int, str, str]] | None = None,
) -> list[str]:
    """Return a mismatch line for every patch whose bytes differ from the expected."""
    problems = []
    for address, old, replacement in PATCHES if patches is None else patches:
        expected = as_bytes(replacement if new else old)
        offset = address - base
        found = memory[offset : offset + len(expected)]
        if found != expected:
            problems.append(
                f"{address:#010x}: found {found.hex()}, expected {expected.hex()}"
            )
    return problems


def apply(
    memory: bytearray, base: int, patches: list[tuple[int, str, str]] | None = None
) -> None:
    chosen = PATCHES if patches is None else patches
    problems = check(bytes(memory), base, patches=chosen)
    if problems:
        raise ValueError("original bytes differ: " + "; ".join(problems))
    for address, _, replacement in chosen:
        data = as_bytes(replacement)
        memory[address - base : address - base + len(data)] = data
