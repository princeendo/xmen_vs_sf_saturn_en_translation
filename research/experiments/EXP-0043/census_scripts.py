"""EXP-0043: census of every roster ending's scripts, aliases, labels and space.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0043/census_scripts.py OUT_JSON

Static: it reads only the untouched source track (``MCED.SHP``, the MC
files), the roster build's MC files (``local/re010/b1``, English win quotes,
`EXP-0032`) and the US arcade program image. Nothing is run in an emulator.

**Scripts** (`EXP-0038` format, read from decoded ``MCED.SHP``):

- the slot table at ``MCED_SCRIPTS`` holds a value per slot (+
  ``MCED_RELOCATION`` = decoded offset of the slot's script);
- the script starts with 4 header words, one per language 0, 2, 4 and 6,
  each the offset of that language's script from the script start;
- a language's script starts with a table of scene offsets (its first entry
  / 2 = the number of scenes);
- each scene is a list of (page length, record x 256 + label) word pairs,
  ended by ``FFFF`` and a trailing word.

For each slot 0-18 the census records:

- both scripts: scenes, pages, record indices, page lengths and labels;
- the slots sharing the script;
- whether the English script shows records 0 to (arcade English count -
  1) once each, in order, and the Japanese script records 0 to (Saturn
  Japanese count - 1);
- whether each trailing word repeats the scene's last page word.

**Labels:** each label index is resolved in ``MCED``'s 16-bit ASCII list
(``LABELS``), and flagged if it contains a name whose two conventions
differ (``DIFFERING``, `docs/names.md`).

**Space** (roster slots 0-17):

- the English ending bytes (100 x the arcade English count) against the
  free bytes after the English win quotes (416 + 76 x the Saturn Japanese
  count);
- the compressed fit: the roster build's MC file with the arcade English
  ending records written at quote table + 800, re-encoded lazily, against
  the file's size.

Only indices, counts, offsets, sizes, hashes, label names and flags are
written. Label names are the game's speaker labels, which `docs/names.md`
already lists; no dialogue text is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.english_mode import ENDING_RECORDS, MCED_RELOCATION, MCED_SCRIPTS
from tools.disc.prs import compress, decompress_file

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m5_roster.json")
CENSUS = Path("data/text/ending_census.json")
BUILD = Path("local/re010/b1")
EN_ENDINGS, EN_RECORD, JP_RECORD = 0x17E318, 100, 76
LABELS, LABEL_SIZE, LABEL_COUNT = 0x3DA8, 32, 40
SLOTS = 19
DIFFERING = ("Nash", "Charlie", "Vega", "Bison", "Gouki", "Akuma")


def word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def labels(mced: bytes) -> list[str]:
    out = []
    for i in range(LABEL_COUNT):
        raw = mced[LABELS + LABEL_SIZE * i : LABELS + LABEL_SIZE * (i + 1)]
        out.append(
            "".join(chr(raw[j + 1]) for j in range(0, len(raw), 2) if raw[j + 1])
        )
    return out


def parse(mced: bytes, start: int) -> dict[str, object]:
    count = word(mced, start) // 2
    scenes = []
    trailing_ok = True
    for index in range(count):
        at = start + word(mced, start + 2 * index)
        pages = []
        while word(mced, at) != 0xFFFF:
            length, command = word(mced, at), word(mced, at + 2)
            pages.append(
                {"length": length, "record": command >> 8, "label": command & 0xFF}
            )
            at += 4
        trailing = word(mced, at + 2)
        if pages and trailing != (pages[-1]["record"] << 8 | pages[-1]["label"]):
            trailing_ok = False
        scenes.append(pages)
    return {"scenes": scenes, "trailing_repeats_last": trailing_ok}


def main(out: Path) -> int:
    program = PROGRAM.read_bytes()
    mced, _ = decompress_file(read_file("MCED.SHP;1"))
    names = labels(mced)
    census = {r["slot"]: r for r in json.loads(CENSUS.read_text())["slots"]}
    roster = {m["slot"]: m for m in json.loads(ROSTER.read_text())["roster"]}
    values = [
        int.from_bytes(mced[MCED_SCRIPTS + 4 * s : MCED_SCRIPTS + 4 * s + 4], "big")
        for s in range(SLOTS)
    ]
    rows = []
    for slot in range(SLOTS):
        base = values[slot] + MCED_RELOCATION
        header = [word(mced, base + 2 * i) for i in range(4)]
        scripts = {
            "japanese": parse(mced, base + header[0]),
            "english": parse(mced, base + header[1]),
        }
        row: dict[str, object] = {
            "slot": slot,
            "label_name": names[slot + 1] if slot + 1 < len(names) else None,
            "script_offset": f"{base:#x}",
            "shared_with": [
                s for s in range(SLOTS) if s != slot and values[s] == values[slot]
            ],
            "header": [f"{h:#x}" for h in header],
            "english_header_same_for_2_4_6": header[1] == header[2] == header[3],
        }
        en_pointer = int.from_bytes(
            program[EN_ENDINGS + 4 * slot : EN_ENDINGS + 4 * slot + 4], "big"
        )
        row["arcade_english_pointer"] = f"{en_pointer:#x}"
        for language, script in scripts.items():
            scenes = script["scenes"]
            assert isinstance(scenes, list)
            pages = [p for scene in scenes for p in scene]
            used = sorted({p["label"] for p in pages if p["label"]})
            row[language] = {
                "scenes": len(scenes),
                "pages": len(pages),
                "records": [p["record"] for p in pages],
                "records_per_scene": [[p["record"] for p in scene] for scene in scenes],
                "page_lengths": [p["length"] for p in pages],
                "labels": [p["label"] for p in pages],
                "label_names": {f"{i:#04x}": names[i] for i in used},
                "flagged_labels": [
                    names[i] for i in used if any(n in names[i] for n in DIFFERING)
                ],
                "trailing_repeats_last": script["trailing_repeats_last"],
            }
        if slot in census:
            info = census[slot]
            en_count = info["arcade_english_records"]
            jp_count = info["saturn_records"]
            row["arcade_english_records"] = en_count
            row["saturn_japanese_records"] = jp_count
            en = row["english"]
            jp = row["japanese"]
            assert isinstance(en, dict) and isinstance(jp, dict)
            row["english_records_in_order"] = en["records"] == list(range(en_count))
            row["japanese_records_in_order"] = jp["records"] == list(range(jp_count))
        if slot in roster:
            member = roster[slot]
            info = census[slot]
            en_bytes = EN_RECORD * info["arcade_english_records"]
            free = 16 * JP_RECORD - ENDING_RECORDS + JP_RECORD * info["saturn_records"]
            name = member["mc_file"].split(";")[0]
            built = (BUILD / name).read_bytes()
            decoded, _ = decompress_file(built)
            data = bytearray(decoded)
            table = int(member["table_offset"], 16)
            at = table + ENDING_RECORDS
            data[at : at + en_bytes] = program[en_pointer : en_pointer + en_bytes]
            natural = len(compress(bytes(data), lazy=True))
            row["space"] = {
                "mc_file": member["mc_file"],
                "english_ending_bytes": en_bytes,
                "free_after_win_quotes": free,
                "fits_free_space": en_bytes <= free,
                "file_size": len(built),
                "natural_lazy_with_ending": natural,
                "compressed_margin": len(built) - natural,
            }
        rows.append(row)
    document = {
        "source": "EXP-0043 census_scripts.py",
        "labels": names,
        "slots": rows,
    }
    out.write_text(json.dumps(document, indent=1) + "\n")
    for row in rows:
        en, jp, space = row["english"], row["japanese"], row.get("space", {})
        assert isinstance(en, dict) and isinstance(jp, dict) and isinstance(space, dict)
        print(
            row["slot"],
            row["label_name"],
            "shared",
            row["shared_with"],
            "JP",
            jp["records_per_scene"],
            "EN",
            en["records_per_scene"],
            row.get("english_records_in_order"),
            row.get("japanese_records_in_order"),
            en["label_names"],
            space.get("compressed_margin"),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
