"""Relative search (EXP-0008): find WORD where every code is ASCII + k for one k.

Usage: python relsearch.py MAINCPU_RAW.bin WORD... ; tries the raw and 16-bit
swapped byte orders at 8- and 16-bit widths and prints hit offsets with k.
"""

import sys
from pathlib import Path


def variants(img):
    sw = bytearray(len(img))
    sw[0::2] = img[1::2]
    sw[1::2] = img[0::2]
    return {"raw": bytes(img), "swapped": bytes(sw)}


def relsearch(data, word, width, step):
    letters = [ord(c) for c in word]
    n = len(letters)
    hits = []
    if width == 1:
        vals = data
        for i in range(0, len(vals) - n * step + 1):
            k = vals[i] - letters[0]
            ok = True
            for j in range(1, n):
                if vals[i + j * step] - letters[j] != k:
                    ok = False
                    break
            if ok:
                hits.append((i, k))
    else:
        for i in range(0, len(data) - 2 * n * step + 1, 2):
            k = int.from_bytes(data[i : i + 2], "big") - letters[0]
            ok = True
            for j in range(1, n):
                if (
                    int.from_bytes(data[i + 2 * j * step : i + 2 * j * step + 2], "big")
                    - letters[j]
                    != k
                ):
                    ok = False
                    break
            if ok:
                hits.append((i, k))
    return hits


img = Path(sys.argv[1]).read_bytes()
for word in sys.argv[2:]:
    for vname, data in variants(img).items():
        for width in (1, 2):
            h = relsearch(data, word, width, 1)
            if h:
                print(
                    word, vname, "width", width, len(h), [(hex(o), k) for o, k in h[:6]]
                )
