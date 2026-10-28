"""EXP-0015: search a dump for the M1 quote's two-line equality structure.

Line 1 is 12 distinct glyphs; line 2 is 10 glyphs whose 9th equals line 1's
2nd (う, the VDP1 cell shared between the lines) and whose others are distinct
from each other and from line 1. The lines may be separated by up to MAX_GAP
values of anything. Prints offsets only.

    ./invenv.sh python research/experiments/EXP-0015/two_line_search.py DUMP BASE
"""

from __future__ import annotations

import sys
from pathlib import Path

LINE1, LINE2, SHARED_1, SHARED_2, MAX_GAP = 12, 10, 1, 8, 64


def values(data: bytes, width: int) -> list[int]:
    return [
        int.from_bytes(data[i : i + width], "big")
        for i in range(0, len(data) - width + 1, width)
    ]


def search(seq: list[int]) -> list[tuple[int, int]]:
    hits = []
    for p in range(len(seq) - LINE1):
        one = seq[p : p + LINE1]
        if len(set(one)) != LINE1:
            continue
        for q in range(p + LINE1, min(p + LINE1 + MAX_GAP, len(seq) - LINE2) + 1):
            two = seq[q : q + LINE2]
            if two[SHARED_2] != one[SHARED_1]:
                continue
            rest = two[:SHARED_2] + two[SHARED_2 + 1 :]
            if len(set(rest)) == len(rest) and not set(rest) & set(one):
                hits.append((p, q))
    return hits


def main(path: Path, base: int) -> int:
    data = path.read_bytes()
    for width in (2, 1):
        hits = search(values(data, width))
        print(f"{path.name} width {width}: {len(hits)} hits")
        for p, q in hits[:10]:
            one, two = base + p * width, base + q * width
            print(f"  line1 {one:#010x}  line2 {two:#010x}  gap {q - p - LINE1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2], 0)))
