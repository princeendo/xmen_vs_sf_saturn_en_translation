r"""EXP-0065: free VDP2 slots for captions 1 and 4, from a `vram_visible.py` timeline.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/free_windows.py TIMELINE BASE1 OPEN

OPEN is a frame before the opening's section C load (the earliest write the
build can control). Caption 1's window: NBG1's base is BASE1 (hex) and every
NBG1 slot on screen is one of its 107 own indices. Caption 4's window: NBG1
at y = 16 with its x scroll moving; its own slots are those NBG1 shows then.
For each window a slot is free if it was last written between OPEN and the
window's start, is not written again before the window ends, and no layer
shows it from that write to its next write (the caption's own use in its
window aside; the font area ``0x60000``-``0x63FFF`` excluded). Prints JSON:
per caption, the window, the own slot count and the free slots by write frame.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

FONT = range(0x60000 // 128, 0x64000 // 128)


def free(
    t: list[dict], w0: int, w1: int, own: set[int], opened: int
) -> dict[int, list[int]]:
    writes: defaultdict[int, list[int]] = defaultdict(list)
    uses: defaultdict[int, list[int]] = defaultdict(list)
    for r in t:
        for s in r["changed"]:
            writes[s].append(r["frame"])
        for layer, slots in r["used"].items():
            for s in slots:
                if not (layer == "NBG1" and w0 <= r["frame"] <= w1 and s in own):
                    uses[s].append(r["frame"])
    groups: defaultdict[int, list[int]] = defaultdict(list)
    for s in range(0, 0x64000 // 128):
        if s in FONT or s in own:
            continue
        before = [f for f in writes.get(s, []) if opened <= f <= w0]
        if not before:
            continue
        tw = before[-1]
        later = [f for f in writes.get(s, []) if f > tw]
        tn = later[0] if later else 10**9
        if tn <= w1 or any(tw <= f < tn for f in uses.get(s, [])):
            continue
        groups[tw].append(s)
    return dict(groups)


def main(path: Path, base1: int, opened: int) -> int:
    t = json.loads(path.read_text())
    mine1 = set(range(base1 // 4, base1 // 4 + 107))
    w1 = [
        r["frame"]
        for r in t
        if r["frame"] > opened
        and r["base"] == base1
        and r["used"]["NBG1"]
        and set(r["used"]["NBG1"]) <= mine1
    ]
    moving = [
        r["frame"]
        for i, r in enumerate(t[1:], 1)
        if r["scroll"][3] == 16
        and r["scroll"][2] != t[i - 1]["scroll"][2]
        and r["frame"] > opened + 800
    ]
    own4 = set().union(
        *(
            set(r["used"]["NBG1"])
            for r in t
            if moving and moving[0] <= r["frame"] <= moving[-1]
        )
    )
    report = {}
    for name, (window, own) in {
        "caption1": (w1, mine1),
        "caption4": (moving, own4),
    }.items():
        a, b = window[0], window[-1]
        groups = free(t, a, b, own, opened)
        report[name] = {
            "window": [a, b],
            "own": len(own),
            "free": sum(len(v) for v in groups.values()),
            "by_write": {
                str(k): [len(v), f"{v[0] * 128:#x}", f"{v[-1] * 128 + 128:#x}"]
                for k, v in sorted(groups.items())
            },
        }
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), int(a[1], 16), int(a[2])))
