"""EXP-0036: census of every roster file's ending records against the arcade's.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/census_endings.py OUT_JSON

For each roster slot (0-17, `data/text/m5_roster.json`) it records:

- the MC file and its quote-table offset (`EXP-0029` census);
- the ending offset, table + ``0x4C0`` (16 records of 76 bytes), the place
  Nash's ending is read from (`EXP-0035`);
- ``saturn_records``: how many records from there equal the slot's arcade
  Japanese ending records in order (`EXP-0029` counted these as
  ``ending_records_after``; recounted here from the decoded file);
- ``arcade_records``: the arcade's Japanese ending block length for the
  slot. A block ends at the next Japanese text pointer of any kind (quote
  or ending table), or at ``ENDINGS_END`` when no pointer follows, in which
  case the length is only an upper bound (``arcade_block_ends_at``);
- ``arcade_english_records``: the English ending block length (table
  ``0x17E318``): to the next English ending pointer, or to ``0x18D81A``
  where the hints start;
- whether the record after the matched run is still Japanese text, judged by
  whether all its codes are ``0x0020`` or in ``0x0900-0x0DFF`` (the
  quote-font kana and kanji range seen in `EXP-0035`). This is a heuristic
  that only flags files to look at.

Only offsets, counts and booleans are written (AGENTS.md rule 21).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0029"))
from census import (
    ENDINGS,
    ENDINGS_END,
    JAPANESE,
    JP_RECORD,
    PROGRAM,
    long,
)

from tools.disc.build_english import read_file
from tools.disc.prs import decompress_file

ROSTER = Path("data/text/m5_roster.json")
EN_ENDINGS, EN_RECORD = 0x17E318, 100
EN_ENDINGS_END = 0x18D81A  # hints follow (tools.reference.xvsf_text TABLES)
QUOTES = 16 * JP_RECORD  # 0x4C0
SLOTS = 19


def text_like(record: bytes) -> bool:
    codes = [int.from_bytes(record[i : i + 2], "big") for i in range(0, 76, 2)]
    return all(c == 0x0020 or 0x0900 <= c <= 0x0DFF for c in codes)


def block_lengths(program: bytes, table: int, bounds: set[int], size: int) -> list[int]:
    pointers = [long(program, table + 4 * s) for s in range(SLOTS)]
    ordered = sorted(bounds)
    return [(next(b for b in ordered if b > p) - p) // size for p in pointers]


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    japanese = {long(program, JAPANESE + 4 * s) for s in range(SLOTS)}
    jp_endings = [long(program, ENDINGS + 4 * s) for s in range(SLOTS)]
    jp_lengths = block_lengths(
        program, ENDINGS, japanese | set(jp_endings) | {ENDINGS_END}, JP_RECORD
    )
    en_endings = [long(program, EN_ENDINGS + 4 * s) for s in range(SLOTS)]
    en_lengths = block_lengths(
        program,
        EN_ENDINGS,
        set(en_endings) | {EN_ENDINGS_END},
        EN_RECORD,
    )
    rows = []
    for member in json.loads(ROSTER.read_text())["roster"]:
        slot = member["slot"]
        decoded, _ = decompress_file(read_file(member["mc_file"]))
        start = int(member["table_offset"], 16) + QUOTES
        count = 0
        while (
            decoded[start + count * JP_RECORD : start + (count + 1) * JP_RECORD]
            == program[
                jp_endings[slot] + count * JP_RECORD : jp_endings[slot]
                + (count + 1) * JP_RECORD
            ]
        ):
            count += 1
        after = decoded[start + count * JP_RECORD : start + (count + 1) * JP_RECORD]
        bound = min(
            b
            for b in japanese | set(jp_endings) | {ENDINGS_END}
            if b > jp_endings[slot]
        )
        rows.append(
            {
                "slot": slot,
                "mc_file": member["mc_file"],
                "table_offset": member["table_offset"],
                "ending_offset": f"{start:#x}",
                "saturn_records": count,
                "arcade_records": jp_lengths[slot],
                "arcade_block_ends_at": "next pointer"
                if bound != ENDINGS_END
                else "ENDINGS_END (no later pointer; length is an upper bound)",
                "all_arcade_records_present": count >= jp_lengths[slot],
                "next_record_text_like": len(after) == JP_RECORD and text_like(after),
                "arcade_english_records": en_lengths[slot],
                "arcade_japanese_alias_of": jp_endings.index(jp_endings[slot])
                if jp_endings.index(jp_endings[slot]) != slot
                else None,
                "arcade_english_alias_of": en_endings.index(en_endings[slot])
                if en_endings.index(en_endings[slot]) != slot
                else None,
            }
        )
    out.write_text(
        json.dumps(
            {
                "source": "EXP-0036 census_endings.py",
                "program": str(PROGRAM),
                "slots": rows,
            },
            indent=1,
        )
        + "\n"
    )
    for row in rows:
        print(
            row["slot"],
            row["mc_file"],
            row["saturn_records"],
            row["arcade_records"],
            row["arcade_english_records"],
            row["next_record_text_like"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
