"""EXP-0037: Nash's ending pairing, from the MAME read logs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0037/make_pairing.py RUNS OUT_JSON

RUNS holds the `run_mame.py` outputs ``en_cyclops``, ``en_ryu``,
``jp_cyclops`` and ``jp_ryu``. In each run's ``reads.txt``, the ending's
record reads are those by PC ``0x04F612`` after the first ending-table read
(PC ``0x04F53C``). Page k is the k-th such read. A pair is:

- Saturn ``MC10.SHP`` record 16 + k (decoded offset ``0x2EC0`` + 76k,
  `EXP-0035`);
- the arcade Japanese record read on page k (expected: slot 16's Japanese
  pointer + 76k);
- the arcade English record read on page k (expected: slot 16's English
  pointer + 100k).

Each language is checked with both partners.

A pair is CONFIRMED when all four runs read the expected addresses and the
Saturn record's bytes equal the arcade Japanese record's. For the gate it
also flags English records that contain a name whose American and Saturn
forms differ (`docs/names.md`): only the flag is written, not the text.
Only addresses, indices, hashes and flags are written (AGENTS.md rule 21).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.prs import decompress_file
from tools.reference.xvsf_text import long, read_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
SLOT = 16
JP_ENDINGS, EN_ENDINGS = 0x17E2CC, 0x17E318
JP_SIZE, EN_SIZE = 76, 100
SATURN_FILE, SATURN_OFFSET, SATURN_FIRST = "MC10.SHP;1", 0x2EC0, 16
TABLE_PC, RECORD_PC = "04f53c", "04f612"
RUNS = {"en_cyclops": "en", "en_ryu": "en", "jp_cyclops": "jp", "jp_ryu": "jp"}
NAMES = ("Charlie", "Bison", "Akuma", "Nash", "Vega", "Gouki")


def ending_reads(path: Path) -> list[int]:
    rows = [line.split() for line in path.read_text().splitlines() if line.strip()]
    start = next(i for i, row in enumerate(rows) if row[1] == TABLE_PC)
    return [int(row[2], 16) for row in rows[start:] if row[1] == RECORD_PC]


def main(runs: Path, out: Path) -> int:
    program = PROGRAM.read_bytes()
    saturn, _ = decompress_file(read_file(SATURN_FILE))
    jp_base = long(program, JP_ENDINGS + 4 * SLOT)
    en_base = long(program, EN_ENDINGS + 4 * SLOT)
    reads = {name: ending_reads(runs / name / "reads.txt") for name in RUNS}
    pairs = []
    for k in range(6):
        offset = SATURN_OFFSET + JP_SIZE * k
        record = saturn[offset : offset + JP_SIZE]
        jp_address, en_address = jp_base + JP_SIZE * k, en_base + EN_SIZE * k
        checks = []
        for name, lang in RUNS.items():
            expected = jp_address if lang == "jp" else en_address
            got = reads[name][k] if k < len(reads[name]) else None
            checks.append(
                {
                    "run": name,
                    "language": lang,
                    "read": f"{got:#x}" if got is not None else None,
                    "expected": f"{expected:#x}",
                    "match": got == expected,
                }
            )
        same_bytes = record == program[jp_address : jp_address + JP_SIZE]
        text = " ".join(read_record(program, en_address))
        pairs.append(
            {
                "page": k + 1,
                "saturn_record": SATURN_FIRST + k,
                "saturn_file": SATURN_FILE,
                "saturn_file_offset": f"{offset:#x}",
                "saturn_sha256": hashlib.sha256(record).hexdigest(),
                "arcade_jp_record": k,
                "arcade_jp_address": f"{jp_address:#x}",
                "saturn_equals_arcade_jp": same_bytes,
                "arcade_en_record": k,
                "arcade_en_address": f"{en_address:#x}",
                "arcade_en_sha256": hashlib.sha256(
                    program[en_address : en_address + EN_SIZE]
                ).hexdigest(),
                "en_names": [n for n in NAMES if n in text],
                "runs": checks,
                "confidence": "CONFIRMED"
                if same_bytes and all(c["match"] for c in checks)
                else "NOT CONFIRMED",
            }
        )
    document = {
        "description": (
            "Nash (arcade slot 16) ending: the Saturn page k shows MC10 record "
            "16 + k; the arcade shows Japanese and English ending record k on "
            "page k, whatever the partner (EXP-0037)."
        ),
        "rule": (
            "page k (k = 0-5) reads ending record k of the point character's "
            "slot, in either language; the partner does not change the records"
        ),
        "program": str(PROGRAM),
        "reads_per_run": {name: len(r) for name, r in reads.items()},
        "pairs": pairs,
    }
    out.write_text(json.dumps(document, indent=1) + "\n")
    print(
        json.dumps(
            [[p["page"], p["confidence"], p["en_names"]] for p in pairs], indent=None
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
