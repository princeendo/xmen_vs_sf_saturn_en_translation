"""Apocalypse's boss-stage boxes in English (`SPEC-003`, `SPEC-004`).

The boxes are drawn by the win-quote renderer (``0x06066948``), whose layout
the English-mode patch already takes from the task byte ``FLAG``
(`tools.disc.english_mode`): 0 gives 2 x 19 wide cells from 76-byte records,
2 gives 2 x 25 cells from 100-byte records. The box setup (``0x060667C4``,
in ``MMPACK.PCA``) never sets that byte. It stores the box task's first
record index, a byte from ``INDEX_TABLE`` by slot (`EXP-0058`), at task + 38,
and the record base, from a table chosen by the global language word (0 on
the Saturn: ``MC08.SHP`` ``0x1090``), at task + 52. Each later box adds 1 to
the index (``0x060665DE``).

``SETUP`` rewrites the base lookup: the task byte ``FLAG`` is set to 2, and
the base becomes ``MC08 + BASE``. The English records are 100 bytes each, in
``MC08.SHP`` (loaded at WRAM-H ``MC08``, `EXP-0058`), and each slot's three
boxes are consecutive (box 0, box 1, box 2). The 17 distinct triples (slot 8
repeats slot 7's) need 5,100 bytes, more than any free run, so:

- 16 triples fill ``BASE`` to ``BASE`` + 4,800 (decoded ``0xDC0``-``0x2080``),
  what the English builds leave unused: Apocalypse's Japanese win-quote
  records 8-15 (his English quotes end at ``0xDC0``), slot 8's 4 Japanese
  ending records (never shown, `docs/coverage_exceptions.md`) and the
  Japanese box table (``0x1090``-``0x2098``);
- the last triple is at index ``FAR_INDEX`` (decoded ``0x4A4C``), inside a run
  of 1,792 zero bytes (``0x4A3C``-``0x513C``) that nothing read or wrote from
  the boxes to the partner fight (`EXP-0061`).

``INDEX_TABLE`` (20 bytes, slots 0-19) then gives each slot its triple; slot
8 shares slot 7's, and slots 18 and 19 share Chun-Li's, as in the original
table. Each entry is (WRAM-H address, original bytes, new bytes); the
originals are checked before any write.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.disc.english_mode import FLAG
from tools.text.caption import compile_record

DATA = Path("data/translations/boss_boxes.json")
MC08 = 0x060C1000  # MC08.SHP during the boss stage (EXP-0058)
BASE = 0xDC0  # decoded MC08 offset of English record 0
RECORD = 100
NEAR = 16  # triples from BASE
FAR_INDEX = 155  # the last triple: BASE + 15,500 = 0x4A4C
FREE = [(0xDC0, 0x2098), (0x4A3C, 0x513C)]  # decoded MC08 ranges the records may use
ORDER = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
]  # slots with a triple

SETUP = (
    0x06066804,
    "9014 00BD C101 C501 300C C101 D109 C501 021D 70FE 011D 6029 201D",
    # mov #FLAG,r1; add r6,r1; mov #2,r0; mov.b r0,@r1; mov.l @(lit),r0;
    # bra 0x0606681E (store r0 at task + 52, as before); nop x 4; lit; nop
    f"E1{FLAG:02X} 316C E002 2100 D002 A006 0009 0009 0009 0009"
    f" {(MC08 + BASE) >> 16:04X} {(MC08 + BASE) & 0xFFFF:04X} 0009",
)
INDEX_TABLE = 0x0606684C
INDEX_ORIGINAL = "00 03 06 09 0C 0F 12 15 18 1B 1E 21 24 27 2A 2D 30 33 21 21"
CHUN_LI, MAGNETO, APOCALYPSE = 11, 7, 8


def first_index() -> dict[int, int]:
    """Each slot's first English record index (slots 0-19)."""
    index = {slot: 3 * k for k, slot in enumerate(ORDER[:NEAR])}
    index[ORDER[NEAR]] = FAR_INDEX
    index[APOCALYPSE] = index[MAGNETO]
    index[18] = index[19] = index[CHUN_LI]
    return index


def index_patch() -> tuple[int, str, str]:
    index = first_index()
    new = " ".join(f"{index[slot]:02X}" for slot in range(20))
    return (INDEX_TABLE, INDEX_ORIGINAL, new)


def patches() -> list[tuple[int, str, str]]:
    """The ``MMPACK.PCA`` code and table changes."""
    return [SETUP, index_patch()]


def load(path: Path = DATA) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def lines(data: dict[str, Any], slot: int, box: int, names: str) -> list[str]:
    """The approved English of one box; ``names`` picks slots 14-16's variant."""
    if box == 2:
        group = next(g for g in data["record_2"].values() if slot in g["slots"])
        return [str(line) for line in group["lines"]]
    entry = data["slots"][str(slot)][f"record_{box}"]
    chosen = (
        entry["lines"]
        if "lines" in entry
        else entry["saturn" if names == "saturn" else "us"]
    )
    return [str(line) for line in chosen]


def records(data: dict[str, Any], names: str) -> dict[int, bytes]:
    """Decoded ``MC08.SHP`` offset -> compiled record, for every English box."""
    index = first_index()
    out = {}
    for slot in ORDER:
        for box in range(3):
            offset = BASE + RECORD * (index[slot] + box)
            if not any(a <= offset and offset + RECORD <= b for a, b in FREE):
                raise ValueError(
                    f"slot {slot} box {box} at {offset:#x} is outside FREE"
                )
            out[offset] = compile_record(lines(data, slot, box, names))
    return out


def edit_mc08(decoded: bytes, data: dict[str, Any], names: str) -> bytes:
    """``decoded`` (MC08.SHP, decompressed) with the English box records."""
    edited = bytearray(decoded)
    for offset, record in records(data, names).items():
        edited[offset : offset + RECORD] = record
    return bytes(edited)
