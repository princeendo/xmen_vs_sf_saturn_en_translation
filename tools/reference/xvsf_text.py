"""Decode the XvSF arcade (CPS-II) Latin text tables from the program ROM (`REF-003`).

The 68000 program region is rebuilt in memory from the set's zips (clone, then
parent) using the pinned MAME driver definition; each 16-bit word is swapped
into 68000 byte order. Nothing is written except the requested report, which
contains game text and must go to an ignored local path.

Empirical character map (`EXP-0008`): a code is ``row_base[ascii >> 4] +
(ascii & 0xF)``, the ASCII table laid out as a tile sheet, plus space
``0x0020``. Codes not in the map are shown as ``{xxxx}``, never guessed.

Layout (shared ROM ``xvs.06a``, identical in every held set): the English area
is 294 records of two 25-code lines from ``0x186EA2`` to ``0x18E17A``. Win
quotes and endings each have a table of 19 big-endian 32-bit pointers to
per-slot blocks; a slot's record count is the distance to the next higher
pointer in its block. Continue-screen hints follow the endings with no pointer
table found (`EXP-0008`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path

from tools.reference.mame_audit import RomSet, parse_driver

SPACE = 0x0020
ROW_BASES = {
    0x2: 0x0670,
    0x3: 0x06D0,
    0x4: 0x0680,
    0x5: 0x06E0,
    0x6: 0x0690,
    0x7: 0x06F0,
}
DECODE = {
    base + column: chr(row * 16 + column)
    for row, base in ROW_BASES.items()
    for column in range(16)
    if 0x21 <= row * 16 + column <= 0x7E
} | {SPACE: " "}
LINE_CODES = 25
RECORD_CODES = 2 * LINE_CODES
SLOTS = 19
# English pointer tables and the block each points into (program addresses).
TABLES = {
    "win_quotes": (0x17E1E8, 0x186EA2, 0x18AD86),
    "endings": (0x17E318, 0x18AD86, 0x18D81A),
}
# Records 270-292 of the English area: gameplay hints (no pointer table found).
HINTS = (0x18D81A, 23)


def find_member(
    bundles: Sequence[zipfile.ZipFile], name: str, sha1: str
) -> bytes | None:
    """A member by name, else by SHA-1 (older zips use older labels, REF-001)."""
    for bundle in bundles:
        if name in bundle.namelist():
            return bundle.read(name)
    for bundle in bundles:
        for info in bundle.infolist():
            data = bundle.read(info)
            if hashlib.sha1(data).hexdigest() == sha1:
                return data
    return None


def build_program(archives: Sequence[Path], romset: RomSet) -> bytes:
    """Rebuild the maincpu region in 68000 byte order from clone/parent zips."""
    entries = [rom for rom in romset.roms if rom.region == "maincpu"]
    image = bytearray(max(rom.offset + rom.size for rom in entries))
    bundles = [zipfile.ZipFile(path) for path in archives]
    for rom in entries:
        if rom.loader != "ROM_LOAD16_WORD_SWAP":
            raise ValueError(f"unsupported loader {rom.loader} for {rom.name}")
        data = find_member(bundles, rom.name, rom.sha1)
        if data is None:
            raise ValueError(f"{rom.name} not in {[str(p) for p in archives]}")
        if len(data) != rom.size:
            raise ValueError(f"{rom.name}: {len(data)} bytes, expected {rom.size}")
        swapped = bytearray(len(data))
        swapped[0::2] = data[1::2]
        swapped[1::2] = data[0::2]
        image[rom.offset : rom.offset + rom.size] = swapped
    return bytes(image)


def word(image: bytes, address: int) -> int:
    return int.from_bytes(image[address : address + 2], "big")


def long(image: bytes, address: int) -> int:
    return int.from_bytes(image[address : address + 4], "big")


def decode_codes(codes: Sequence[int]) -> str:
    return "".join(DECODE.get(code, f"{{{code:04x}}}") for code in codes)


def read_record(image: bytes, address: int) -> list[str]:
    """Two decoded lines, trailing spaces removed."""
    codes = [word(image, address + 2 * i) for i in range(RECORD_CODES)]
    return [
        decode_codes(codes[:LINE_CODES]).rstrip(),
        decode_codes(codes[LINE_CODES:]).rstrip(),
    ]


def read_table(
    image: bytes, table: int, start: int, end: int
) -> list[dict[str, object]]:
    """Slots of a pointer table, each with its records."""
    pointers = [long(image, table + 4 * i) for i in range(SLOTS)]
    bounds = sorted({p for p in pointers if start <= p < end} | {end})
    slots: list[dict[str, object]] = []
    for slot, pointer in enumerate(pointers):
        if not start <= pointer < end or (pointer - start) % (2 * RECORD_CODES):
            raise ValueError(
                f"slot {slot}: pointer {pointer:#x} outside the block grid"
            )
        stop = next(b for b in bounds if b > pointer)
        count = (stop - pointer) // (2 * RECORD_CODES)
        first = pointers.index(pointer)
        slots.append(
            {
                "slot": slot,
                "pointer": f"{pointer:#08x}",
                "alias_of": first if first != slot else None,
                "records": [
                    read_record(image, pointer + 2 * RECORD_CODES * i)
                    for i in range(count)
                ],
            }
        )
    return slots


def read_records(image: bytes, start: int, count: int) -> list[list[str]]:
    return [read_record(image, start + 2 * RECORD_CODES * i) for i in range(count)]


def unmapped(records: Sequence[Sequence[str]]) -> list[str]:
    text = " ".join(line for record in records for line in record)
    return sorted(set(re.findall(r"\{[0-9a-f]{4}\}", text)))


def code_contexts(image: bytes, start: int, end: int) -> dict[str, dict[str, int]]:
    """For each non-letter, non-space code: counts of (previous, next) class pairs.

    Classes: L letter, S space, P mapped punctuation or digit, X unmapped.
    """

    def kind(code: int) -> str:
        if code == SPACE:
            return "S"
        char = DECODE.get(code)
        if char is None:
            return "X"
        return "L" if char.isalpha() else "P"

    codes = [word(image, a) for a in range(start, end, 2)]
    table: dict[int, Counter[str]] = defaultdict(Counter)
    for i, code in enumerate(codes):
        if kind(code) in "LS":
            continue
        before = kind(codes[i - 1]) if i else "^"
        after = kind(codes[i + 1]) if i + 1 < len(codes) else "$"
        table[code][before + after] += 1
    return {
        f"{code:04x} {DECODE.get(code, '?')}": dict(counter)
        for code, counter in sorted(table.items(), key=lambda kv: -sum(kv[1].values()))
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True, help="MAME cps2.cpp")
    parser.add_argument("--set", dest="set_name", default="xmvsfu")
    parser.add_argument(
        "--rompath", type=Path, required=True, help="folder with <set>.zip"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="JSON report (ignored path)"
    )
    args = parser.parse_args(argv)
    sets = parse_driver(args.driver.read_text())
    romset = sets[args.set_name]
    archives = [args.rompath / f"{args.set_name}.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    image = build_program(archives, romset)
    report: dict[str, object] = {"set": args.set_name}
    for name, (table, start, end) in TABLES.items():
        slots = read_table(image, table, start, end)
        unique = {str(slot["pointer"]): slot["records"] for slot in slots}
        records: list[list[str]] = [r for rs in unique.values() for r in rs]  # type: ignore[attr-defined]
        report[name] = {
            "table": f"{table:#08x}",
            "block": [f"{start:#08x}", f"{end:#08x}"],
            "unique_records": len(records),
            "unmapped_codes": unmapped(records),
            "contexts": code_contexts(image, start, end),
            "slots": slots,
        }
        print(name, len(records), "unique records; unmapped", unmapped(records))
    hints = read_records(image, *HINTS)
    report["hints"] = {
        "block": [f"{HINTS[0]:#08x}", f"{HINTS[0] + 2 * RECORD_CODES * HINTS[1]:#08x}"],
        "unmapped_codes": unmapped(hints),
        "records": hints,
    }
    print("hints", len(hints), "records; unmapped", unmapped(hints))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
