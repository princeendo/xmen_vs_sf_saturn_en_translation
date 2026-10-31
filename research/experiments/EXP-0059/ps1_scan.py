r"""EXP-0059: list the long English text runs in the US PlayStation image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0059/ps1_scan.py BIN [--flat OUT]

BIN is the raw (2,352-byte sector) PlayStation image. The 2,048-byte user data
of each sector is joined into one flat image (written to ``--flat`` if given,
an ignored path). Its 16-bit words are read little-endian, as the PlayStation
stores the arcade's codes byte-swapped, and every run of at least ``MIN_RUN``
codes that `tools.reference.xvsf_text.DECODE` knows is printed with its flat
offset, its length and its first 110 characters. Runs that mention the boss
stage's words (``BOSS_WORDS``) are counted at the end.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.xvsf_text import DECODE

SECTOR, HEADER, DATA = 2352, 24, 2048
MIN_RUN = 30
BOSS_WORDS = r"Apocalypse|true form|Behold|behold|your life|this form|So you"


def flatten(raw: bytes) -> bytes:
    return b"".join(
        raw[s * SECTOR + HEADER : s * SECTOR + HEADER + DATA]
        for s in range(len(raw) // SECTOR)
    )


def runs(flat: bytes) -> list[tuple[int, str]]:
    words = [flat[i] | flat[i + 1] << 8 for i in range(0, len(flat) - 1, 2)]
    found, start = [], None
    for i, word in enumerate([*words, None]):
        if word in DECODE:
            start = i if start is None else start
            continue
        if start is not None and i - start >= MIN_RUN:
            found.append((2 * start, "".join(DECODE[w] for w in words[start:i])))
        start = None
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bin", type=Path)
    parser.add_argument("--flat", type=Path)
    args = parser.parse_args()
    flat = flatten(args.bin.read_bytes())
    if args.flat:
        args.flat.write_bytes(flat)
    found = runs(flat)
    for offset, text in found:
        print(f"{offset:#010x} {len(text)} {' '.join(text.split())[:110]!r}")
    boss = [offset for offset, text in found if re.search(BOSS_WORDS, text)]
    print(f"{len(found)} runs; {len(boss)} mention the boss stage's words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
