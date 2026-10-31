r"""EXP-0059: RAM writes that put test English into Ryu's boss boxes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0059/fit_patches.py [--no-language]

Prints `EXP-0049/patch_run.py` items: the language word ``0x060F547A`` and the
region word ``0x060F5478`` set to 2 (``--no-language`` leaves the language
word out), and three English records (`tools.text.caption.compile_record`,
2 lines of 25 cells, 100 bytes) written where an English stride would put
Ryu's (slot 9) boxes: ``MC08.SHP`` at WRAM-H ``0x060C1000``, box table
``0x1090``, records 27-29 at 100 bytes each. Each item carries the bytes the
untouched file holds there, so ``patch_run.py`` checks them first.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.prs import decompress_file
from tools.text.caption import compile_record

MC08, BOXES, FIRST, STRIDE = 0x060C1000, 0x1090, 27, 100
RECORDS = [
    ["W" * 25, "M" * 25],
    ["Ryu, you lost warrior.", "Your fists cannot touch me."[:25]],
    ["Behold my true form!", "Now offer up your life!!"],
]


def main(language: bool) -> int:
    decoded, _ = decompress_file(read_file("MC08.SHP;1"))
    items = ["060F547A:0000:0002"] if language else []
    items.append("060F5478:0000:0002")
    for k, lines in enumerate(RECORDS):
        offset = BOXES + (FIRST + k) * STRIDE
        old, new = decoded[offset : offset + STRIDE], compile_record(lines)
        items.append(f"{MC08 + offset:08X}:{old.hex()}:{new.hex()}")
    print(" ".join(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--no-language" not in sys.argv[1:]))
