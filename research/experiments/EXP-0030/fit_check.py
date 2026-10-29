"""EXP-0030: check that every roster character's English records fit and draw right.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0030/fit_check.py OUT_JSON

For each slot in `data/text/m5_roster.json`, the English records 0-7 (and
record 8 where it exists, for the record) are read from the ignored US
program ``local/ref003/xmvsfu-68k.bin`` (table ``0x17E1E8``, `EXP-0008`).
Each record is checked as follows:

- **Recompile:** decode with `tools.text.caption.decode_record`, recompile
  with ``compile_record``, and require identical bytes. This also proves the
  record is 2 x 25 codes with every code mapped.
- **Glyphs:** list any code whose Saturn quote-font glyph is not the
  expected character: ``0x0680`` (``@``, drawn as a heart) and
  ``0x06FB``-``0x06FD`` (``{ | }``, drawn as two fractions and infinity;
  D-015).
- **Names:** list the character names whose American and Saturn forms
  differ (`docs/names.md`) and that occur in the record as whole words, case
  ignored.

OUT_JSON holds slots, record numbers, addresses, hashes, line lengths and the
names found. It holds no quote text (AGENTS.md rule 21).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.text.caption import compile_record, decode_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m5_roster.json")
EN_TABLE, RECORD = 0x17E1E8, 100
OTHER_GLYPHS = {0x0680: "@ (heart)", 0x06FB: "{", 0x06FC: "|", 0x06FD: "}"}
NAMES = ["Akuma", "Gouki", "Charlie", "Nash", "Bison", "Vega", "Balrog", "Sagat"]


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())["roster"]
    report = []
    problems = 0
    for member in roster:
        slot = int(member["slot"])
        base = int.from_bytes(program[EN_TABLE + 4 * slot : EN_TABLE + 4 * slot + 4])
        for index in range(int(member["english_records"])):
            address = base + RECORD * index
            data = program[address : address + RECORD]
            lines = decode_record(data)
            exact = compile_record(lines) == data
            codes = [int.from_bytes(data[i : i + 2]) for i in range(0, RECORD, 2)]
            glyphs = sorted({OTHER_GLYPHS[c] for c in codes if c in OTHER_GLYPHS})
            text = " ".join(lines)
            names = [n for n in NAMES if re.search(rf"\b{n}\b", text, re.IGNORECASE)]
            problems += not exact
            report.append(
                {
                    "slot": slot,
                    "character": member["name_list"],
                    "english_record": index,
                    "shown": index < 8,
                    "address": f"{address:#x}",
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "line_lengths": [len(line.rstrip()) for line in lines],
                    "recompiles_exactly": exact,
                    "other_glyphs": glyphs,
                    "names": names,
                }
            )
    out.write_text(json.dumps(report, indent=1) + "\n")
    shown = [r for r in report if r["shown"]]
    print(
        json.dumps(
            {
                "records_shown": len(shown),
                "not_exact": [
                    (r["slot"], r["english_record"])
                    for r in report
                    if not r["recompiles_exactly"]
                ],
                "other_glyphs": [
                    (r["slot"], r["english_record"], r["other_glyphs"])
                    for r in shown
                    if r["other_glyphs"]
                ],
                "names": [
                    (r["slot"], r["character"], r["english_record"], r["names"])
                    for r in shown
                    if r["names"]
                ],
                "longest_line": max(max(r["line_lengths"]) for r in shown),
            },
            indent=1,
        )
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
