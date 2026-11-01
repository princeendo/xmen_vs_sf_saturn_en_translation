r"""EXP-0066: write the continue-hint pairing (index -> Saturn and arcade records).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0066/hint_pairing.py \
        PROGRAM SATURN_WRAM_H ARCADE_SUMMARY OUT_JSON

PROGRAM is the `xmvsfu` 68000-order program (`local/ref003/xmvsfu-68k.bin`);
SATURN_WRAM_H a WRAM-H dump at the continue screen (`continue_run.py`);
ARCADE_SUMMARY the ``summary.json`` of `arcade_hints.py` runs ``en:0``-``en:15``
and ``jp:0``-``jp:15``. The arcade map is taken from those runs (the first
English page each index showed), because the program file holds it in
encrypted form: the starter reads it PC-relative, through the decrypted
opcode space. Checks that every English run showed ``map[i]`` then
``map[i] + 1``, every Japanese run record ``i``, and that the map equals the
Saturn's bytes at ``SATURN_MAP``, then writes, for each index 0-15, the
Saturn record, the arcade Japanese record and the two English records the
arcade shows (``map[i]`` and ``map[i] + 1``), with each record's address and
SHA-256, and whether the arcade's Japanese record equals the Saturn's. No
game text is written.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ARCADE_MAP, SATURN_MAP = 0x04F476, 0x060667A8  # arcade: decrypted space
ARCADE_JP, ARCADE_EN = 0x18397C, 0x18D81A
SATURN_JP = 0x06085544
JP_SIZE, EN_SIZE, INDEXES = 76, 100, 16
WRAM_H = 0x06000000
FIRST_AREA_RECORD = 270  # area record number of ARCADE_EN (EXP-0008)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def observed_map(summary: Path) -> bytes:
    runs = {
        r["run"]: [p["record"] for p in r["pages"]]
        for r in json.loads(summary.read_text())
    }
    found = []
    for index in range(INDEXES):
        first, second = runs[f"en:{index}"]
        if second != first + 1 or runs[f"jp:{index}"] != [index]:
            raise SystemExit(f"index {index}: unexpected pages")
        found.append(int(first))
    return bytes(found)


def main(program: Path, wram_h: Path, summary: Path, out: Path) -> int:
    prog, ram = program.read_bytes(), wram_h.read_bytes()
    arcade_map = observed_map(summary)
    saturn_map = ram[SATURN_MAP - WRAM_H : SATURN_MAP - WRAM_H + INDEXES]
    if arcade_map != saturn_map:
        raise SystemExit("the arcade and Saturn index maps differ")
    hints = []
    for index in range(INDEXES):
        saturn_at = SATURN_JP + JP_SIZE * index
        saturn = ram[saturn_at - WRAM_H : saturn_at - WRAM_H + JP_SIZE]
        jp_at = ARCADE_JP + JP_SIZE * index
        english = []
        for record in (arcade_map[index], arcade_map[index] + 1):
            at = ARCADE_EN + EN_SIZE * record
            english.append(
                {
                    "record": record,
                    "area_record": FIRST_AREA_RECORD + record,
                    "address": f"{at:#x}",
                    "sha256": digest(prog[at : at + EN_SIZE]),
                }
            )
        hints.append(
            {
                "index": index,
                "saturn_record": index,
                "saturn_address": f"{saturn_at:#010x}",
                "saturn_sha256": digest(saturn),
                "arcade_jp_address": f"{jp_at:#x}",
                "arcade_jp_equal": prog[jp_at : jp_at + JP_SIZE] == saturn,
                "english_pages": english,
            }
        )
    report = {
        "description": (
            "Continue hints (HINT-001, EXP-0066): for each index (rand & 0x0F) the "
            "Saturn's Japanese record and the two English records the US arcade "
            "shows for the same index, as forced in both."
        ),
        "rule": (
            "index = rand() & 0x0F; Japanese: record index, one page; English: "
            "records map[index] and map[index] + 1, two pages"
        ),
        "index_map": arcade_map.hex(" "),
        "arcade": {
            "program": "xmvsfu, 68000 order (EXP-0008)",
            "starter": "0x04f42a",
            "map": f"{ARCADE_MAP:#x}",
            "japanese_table": f"{ARCADE_JP:#x}",
            "english_table": f"{ARCADE_EN:#x}",
        },
        "saturn": {
            "file": "MMPACK.PCA (decoded segment 2, loaded at 0x0601f000)",
            "starter": "0x06066728",
            "map": f"{SATURN_MAP:#010x}",
            "japanese_table": f"{SATURN_JP:#010x}",
            "english_table_pointer": "0x06085b80 (not English text, EXP-0066)",
        },
        "hints": hints,
    }
    out.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), Path(a[3])))
