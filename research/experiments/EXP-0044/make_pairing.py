"""EXP-0044: an ending pairing file for every M8 roster character.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/make_pairing.py \\
        COMPARE_JSON OUT_DIR

Generalized from `research/experiments/EXP-0037/make_pairing.py` (this
repository, commit ``8caed7c``). The English layout (`LAYOUT-002`) shows a
character's English script, so its English pages and its Japanese records
are paired separately:

- **English pages:** page k (k = 0 to the arcade English count - 1) shows
  arcade English record k. It is CONFIRMED when every English run of the
  slot read that address on page k (``compare.py`` output).
- **Japanese records:** Saturn record 16 + k (decoded quote table + 0x4C0 +
  76k) equals arcade Japanese record k byte for byte. It is CONFIRMED when
  every Japanese run read that address on page k.

For the gate, each English record also gets the names it contains whose two
conventions differ (``NAMES``, `docs/names.md`), as a flag only. Only
addresses, indices, hashes and flags are written (AGENTS.md rule 21).
Writes ``OUT_DIR/<name>_ending_pairing.json``, named after the Saturn name
list like the win-quote specs. Nash's file in ``data/translations``
(`EXP-0037`) is kept, so his is written as ``nash_ending_pairing_exp0044.json``
for comparison and not copied.
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
ROSTER = Path("data/text/m8_ending_roster.json")
CENSUS = Path("data/text/ending_census.json")
EN_TABLE, JP_TABLE, EN_SIZE, JP_SIZE = 0x17E318, 0x17E2CC, 100, 76
QUOTES = 16 * JP_SIZE
NAMES = ("Charlie", "Bison", "Akuma", "Nash", "Vega", "Gouki")


def file_name(member: dict[str, object]) -> str:
    return str(member["name"]).lower().replace("-", "_").replace(" ", "_")


def main(compare: Path, out_dir: Path) -> int:
    program = PROGRAM.read_bytes()
    results = json.loads(compare.read_text())
    census = {r["slot"]: r for r in json.loads(CENSUS.read_text())["slots"]}
    summary = []
    for member in json.loads(ROSTER.read_text())["members"]:
        slot = member["slot"]
        runs = {
            lang: [
                v["read"]["records"]
                for k, v in results.items()
                if k.startswith(f"s{slot}_") and k.endswith(f"_{lang}") and "read" in v
            ]
            for lang in ("en", "jp")
        }
        en_base = long(program, EN_TABLE + 4 * slot)
        jp_base = long(program, JP_TABLE + 4 * slot)
        decoded, _ = decompress_file(read_file(str(member["mc_file"])))
        table = int(str(member["table_offset"]), 16)
        english = []
        for k in range(census[slot]["arcade_english_records"]):
            address = en_base + EN_SIZE * k
            text = " ".join(read_record(program, address))
            reads = [r[k] if k < len(r) else None for r in runs["en"]]
            english.append(
                {
                    "page": k + 1,
                    "arcade_en_record": k,
                    "arcade_en_address": f"{address:#x}",
                    "arcade_en_sha256": hashlib.sha256(
                        program[address : address + EN_SIZE]
                    ).hexdigest(),
                    "en_names": [n for n in NAMES if n in text],
                    "runs": len(reads),
                    "confidence": "CONFIRMED"
                    if reads and all(r == f"{address:#x}" for r in reads)
                    else "NOT CONFIRMED",
                }
            )
        japanese = []
        for k in range(census[slot]["saturn_records"]):
            address = jp_base + JP_SIZE * k
            offset = table + QUOTES + JP_SIZE * k
            same = (
                decoded[offset : offset + JP_SIZE]
                == program[address : address + JP_SIZE]
            )
            reads = [r[k] if k < len(r) else None for r in runs["jp"]]
            japanese.append(
                {
                    "saturn_record": 16 + k,
                    "saturn_file_offset": f"{offset:#x}",
                    "arcade_jp_record": k,
                    "arcade_jp_address": f"{address:#x}",
                    "saturn_equals_arcade_jp": same,
                    "runs": len(reads),
                    "confidence": "CONFIRMED"
                    if same and reads and all(r == f"{address:#x}" for r in reads)
                    else "NOT CONFIRMED",
                }
            )
        document = {
            "description": (
                f"{member['name']} (arcade slot {slot}) ending: with the English "
                "layout (LAYOUT-002), page k shows arcade English record k; the "
                "Japanese records pair with the arcade's by index (EXP-0044)."
            ),
            "rule": (
                "page k reads the point character's ending record k, "
                "in either language, whatever the partner"
            ),
            "slot": slot,
            "mc_file": member["mc_file"],
            "table_offset": member["table_offset"],
            "english_pages": english,
            "japanese_records": japanese,
        }
        name = file_name(member)
        target = out_dir / (
            f"{name}_ending_pairing.json"
            if slot != 16
            else f"{name}_ending_pairing_exp0044.json"
        )
        target.write_text(json.dumps(document, indent=1) + "\n")
        summary.append(
            (
                slot,
                member["name"],
                all(e["confidence"] == "CONFIRMED" for e in english),
                all(j["confidence"] == "CONFIRMED" for j in japanese),
                [(e["page"], e["en_names"]) for e in english if e["en_names"]],
            )
        )
    for row in summary:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
