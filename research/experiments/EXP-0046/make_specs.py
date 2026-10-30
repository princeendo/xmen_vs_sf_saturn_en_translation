"""EXP-0046: write the ending spec of every M8 roster character.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/make_specs.py OUT_DIR

Generalizes `EXP-0041` ``make_spec.py`` (Nash only) to the `END-011`
roster (``data/text/m8_ending_roster.json``). For each member it reads
``data/translations/<stem>_ending_pairing.json`` (`EXP-0037` for Nash,
`EXP-0044` for the others) and the US arcade program image, and writes
``OUT_DIR/<stem>_ending.json``. Each English record gets its source address,
SHA-256 and line lengths; no text (AGENTS.md rule 21).

Checks, per member:

- every English page is CONFIRMED and its source hash matches;
- the pages are English records 0 to n - 1 in order, n being the roster's
  count;
- the English bytes (800 + 100n from the quote table) fit in the Japanese
  records they replace (16 win quotes and the ending, 76 bytes each,
  ``data/text/ending_census.json``).

A slot whose ``MCED`` script is shared (Ryu with 8, Chun-Li with 18) gets
``mced_shared_with``, which lets `tools.disc.build_english` switch that
shared script (`GATE-TRANSLATION`, 2026-10-30).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.english_mode import ENDING_RECORDS
from tools.text.caption import decode_record

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m8_ending_roster.json")
CENSUS = Path("data/text/ending_census.json")
PAIRINGS = Path("data/translations")
RECORD = 100
JAPANESE = 76
WIN_QUOTES = 16


def stem(name: str) -> str:
    return name.lower().replace("-", "_")


def english_pages(pairing: dict[str, object]) -> list[dict[str, object]]:
    # EXP-0037 (Nash) names the list "pairs"; EXP-0044 "english_pages"
    pages = pairing.get("english_pages", pairing.get("pairs"))
    assert isinstance(pages, list)
    return pages


def make_spec(
    member: dict[str, object], census: dict[str, object], program: bytes
) -> dict[str, object]:
    name = str(member["name"])
    path = PAIRINGS / f"{stem(name)}_ending_pairing.json"
    pairing = json.loads(path.read_text())
    pages = english_pages(pairing)
    count = int(str(member["english_ending_records"]))
    japanese = int(str(census["saturn_records"]))
    if [p["arcade_en_record"] for p in pages] != list(range(count)):
        raise ValueError(f"{name}: pages are not English records 0-{count - 1}")
    used = ENDING_RECORDS + RECORD * count
    space = (WIN_QUOTES + japanese) * JAPANESE
    if used > space:
        raise ValueError(f"{name}: {used} English bytes exceed {space}")
    records = []
    for page in pages:
        if page["confidence"] != "CONFIRMED":
            raise ValueError(f"{name} page {page['page']} is not confirmed")
        address = int(str(page["arcade_en_address"]), 16)
        source = program[address : address + RECORD]
        if hashlib.sha256(source).hexdigest() != page["arcade_en_sha256"]:
            raise ValueError(f"{name} page {page['page']}: source hash differs")
        k = int(str(page["arcade_en_record"]))
        records.append(
            {
                "english_record": k,
                "page": page["page"],
                "saturn_record": WIN_QUOTES + k if k < japanese else None,
                "source_address": page["arcade_en_address"],
                "sha256": page["arcade_en_sha256"],
                "line_lengths": [len(line) for line in decode_record(source)],
                "grammar_fix": None,
            }
        )
    spec: dict[str, object] = {
        "kind": "ending",
        "description": (
            f"{name}'s ending in English: the official arcade English, paired "
            "by GATE-TRANSLATION (M8 extension, user decision 2026-10-30, "
            "SESSION-0069; page k shows English record k), shown with the "
            "Saturn's own English ending script through patch version 4."
        ),
        "character": name,
        "arcade_slot": member["slot"],
        "mc_file": member["mc_file"],
        "table_offset": member["table_offset"],
        "records_offset": f"{ENDING_RECORDS:#x}",
        "english_bytes": used,
        "japanese_space": space,
        "script": "MCED.SHP;1 (tools.disc.english_mode.mced_english_scripts)",
        "source": {
            "set": "xmvsfu (MAME 0.289, references/arcade/)",
            "program_order": "68000 (EXP-0008)",
            "english_endings_table": "0x17e318",
            "slot_base": pages[0]["arcade_en_address"],
        },
        "pairing": str(path),
        "records": records,
    }
    shared = member["mced_script_shared_with"]
    if shared:
        spec["mced_shared_with"] = shared
    return spec


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())
    census = {s["slot"]: s for s in json.loads(CENSUS.read_text())["slots"]}
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for member in roster["members"]:
        spec = make_spec(member, census[member["slot"]], program)
        if spec["mc_file"] != census[member["slot"]]["mc_file"]:
            raise ValueError(f"{member['name']}: MC files differ")
        name = f"{stem(str(member['name']))}_ending.json"
        (out / name).write_text(json.dumps(spec, indent=1) + "\n")
        summary[name] = [spec["english_bytes"], spec["japanese_space"]]
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
