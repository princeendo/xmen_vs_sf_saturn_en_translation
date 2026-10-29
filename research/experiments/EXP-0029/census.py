"""EXP-0029: census the Saturn quote files against the arcade win-quote slots.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0029/census.py OUT_JSON

Static only. The quote files come from the untouched data track
(`tools.disc.build_english.read_file`, which checks each file against
`references/saturn_jp/iso_listing.json`). The arcade program is the ignored
``local/ref003/xmvsfu-68k.bin`` (`EXP-0008`).

For each of the 19 arcade slots the script records:

- the name at that slot's position in the 16-bit name list (``0x503E4``,
  `EXP-0011`), whose first entry is blank, so slot ``s`` is entry ``s + 1``;
- the Japanese and English pointers (tables ``0x17E19C`` and ``0x17E1E8``),
  any alias to an earlier slot, and the English record count;
- the Saturn files holding its Japanese table (for an alias, the first
  slot's table).

For each ``MC*.SHP`` file it records:

- its size, sector count and SHA-256;
- whether the stream decodes and ends in the file's last sector;
- every place where a slot's 16 Japanese quote records (16 x 76 bytes) sit
  in the decoded file;
- how many of that slot's Japanese ending records (table ``0x17E2CC``)
  follow the table, counted only;
- for a file with no whole table, how many single Japanese quote records,
  and how many Japanese ending records, of each slot it holds anywhere.

Only offsets, counts, sizes, hashes and names are written, no game text
(AGENTS.md rule 21).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import LISTING, read_file
from tools.disc.prs import PrsError, decompress_file

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
JAPANESE, ENGLISH, ENDINGS = 0x17E19C, 0x17E1E8, 0x17E2CC
ENGLISH_END = 0x18AD86  # end of the English win-quote block (EXP-0008)
ENDINGS_END = 0x186EA2  # the English area follows the Japanese text
NAMES, NAME_SIZE = 0x503E4, 32  # 16 characters of 16-bit ASCII each
SLOTS, RECORDS, JP_RECORD, EN_RECORD = 19, 16, 76, 100
SECTOR = 2048


def long(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def name(program: bytes, index: int) -> str:
    raw = program[NAMES + NAME_SIZE * index : NAMES + NAME_SIZE * (index + 1)]
    return raw[1::2].decode("ascii").strip()


def slots(program: bytes) -> list[dict[str, object]]:
    english = [long(program, ENGLISH + 4 * s) for s in range(SLOTS)]
    japanese = [long(program, JAPANESE + 4 * s) for s in range(SLOTS)]
    bounds = sorted(set(english) | {ENGLISH_END})
    result = []
    for slot in range(SLOTS):
        stop = next(b for b in bounds if b > english[slot])
        result.append(
            {
                "slot": slot,
                "name_list": name(program, slot + 1),
                "japanese_pointer": f"{japanese[slot]:#x}",
                "japanese_alias_of": japanese.index(japanese[slot])
                if japanese.index(japanese[slot]) != slot
                else None,
                "english_pointer": f"{english[slot]:#x}",
                "english_alias_of": english.index(english[slot])
                if english.index(english[slot]) != slot
                else None,
                "english_records": (stop - english[slot]) // EN_RECORD,
            }
        )
    return result


def find_all(data: bytes, needle: bytes) -> list[int]:
    found, start = [], 0
    while (at := data.find(needle, start)) >= 0:
        found.append(at)
        start = at + 1
    return found


def census_file(program: bytes, file_name: str) -> dict[str, object]:
    raw = read_file(file_name)
    entry: dict[str, object] = {
        "file": file_name,
        "size": len(raw),
        "sectors": -(-len(raw) // SECTOR),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    try:
        decoded, used = decompress_file(raw)
    except PrsError as error:
        entry["decodes"] = False
        entry["decode_error"] = str(error)
        return entry
    entry.update(
        {
            "decodes": True,
            "stream_bytes": used,
            "ends_in_last_sector": -(-used // SECTOR) == entry["sectors"],
            "decoded_size": len(decoded),
            "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
        }
    )
    tables = []
    for slot in range(SLOTS):
        pointer = long(program, JAPANESE + 4 * slot)
        if long(program, JAPANESE + 4 * slot) in [
            long(program, JAPANESE + 4 * s) for s in range(slot)
        ]:
            continue  # an alias: reported under the first slot
        block = program[pointer : pointer + RECORDS * JP_RECORD]
        for offset in find_all(decoded, block):
            endings = long(program, ENDINGS + 4 * slot)
            start = offset + RECORDS * JP_RECORD
            count = 0
            while (
                decoded[start + count * JP_RECORD : start + (count + 1) * JP_RECORD]
                == program[
                    endings + count * JP_RECORD : endings + (count + 1) * JP_RECORD
                ]
            ):
                count += 1
            tables.append(
                {
                    "slot": slot,
                    "offset": f"{offset:#x}",
                    "ending_records_after": count,
                    "bytes_after_endings": len(decoded) - start - count * JP_RECORD,
                }
            )
    entry["quote_tables"] = tables
    if not tables:
        partial = {}
        for slot in range(SLOTS):
            pointer = long(program, JAPANESE + 4 * slot)
            hits = sum(
                decoded.find(
                    program[pointer + JP_RECORD * k : pointer + JP_RECORD * (k + 1)]
                )
                >= 0
                for k in range(RECORDS)
            )
            if hits:
                partial[str(slot)] = hits
        entry["single_record_hits"] = partial
        runs: dict[str, int] = {}
        for slot in range(SLOTS):
            pointer = long(program, ENDINGS + 4 * slot)
            hits = 0
            while (at := pointer + JP_RECORD * hits) < ENDINGS_END and decoded.find(
                program[at : at + JP_RECORD]
            ) >= 0:
                hits += 1
            if hits:
                runs[str(slot)] = hits
        entry["ending_record_runs"] = runs
    return entry


def list_of(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    files = sorted(
        f["path"]
        for f in json.loads(LISTING.read_text())["files"]
        if f["path"].startswith("MC") and f["path"].endswith(".SHP;1")
    )
    slot_list = slots(program)
    file_list = [census_file(program, f) for f in files]
    for slot in slot_list:
        source = slot["japanese_alias_of"]
        wanted = slot["slot"] if source is None else source
        slot["saturn_file"] = [
            f["file"]
            for f in file_list
            if any(
                isinstance(q, dict) and q["slot"] == wanted
                for q in list_of(f.get("quote_tables"))
            )
        ]
    report = {
        "program": {
            "path": str(PROGRAM),
            "sha256": hashlib.sha256(program).hexdigest(),
        },
        "slots": slot_list,
        "files": file_list,
    }
    out.write_text(json.dumps(report, indent=1) + "\n")
    for f in file_list:
        print(
            f["file"],
            f["size"],
            f["sectors"],
            f.get("ends_in_last_sector"),
            f.get("quote_tables", f.get("decode_error")),
            f.get("single_record_hits", ""),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
