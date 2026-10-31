r"""EXP-0065: per-file room for the English captions, as build metadata.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/room_metadata.py DISC CAP002 OUT

DISC holds the extracted ``OPENING0``-``7.ST2``; CAP002 the experiment's
local outputs (``full<k>/timeline.json`` from `vram_visible.py`). Writes OUT
(JSON, derived metadata: block numbers, bases, frames and index lists, no game
data). Per file:

- **caption 1:** section C, base = part 0's size / 32; extra indices from
  slots section C writes that nothing shows (`free_windows.free`), as
  index = slot - base / 4;
- **caption 2, caption 3:** the stream block holding the caption's glyphs
  (``C2_BLOCK``, ``C3_BLOCK``, from `EXP-0064`'s cell search), base = that
  block's part 1 VRAM address / 32 (``C2_BASE``, ``C3_BASE`` from the
  snapshots);
- **caption 4:** the blocks before and after the script's re-index frame
  (``C4``, from the snapshots), their bases, the re-index frame (the
  caption window's second update of more than 900 words, if any), and per
  block the indices whose VRAM slot is shown only during the banner or free,
  limited to the block's part 1. For the banner, a slot's last write may be
  inside the window (the second block loads during the banner): it is usable
  if nothing but NBG1 during the banner shows it from that write on.
"""

from __future__ import annotations

import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from free_windows import free

from tools.disc.st2_stream import (
    blocks,
    lz_decode,
    map_decode,
    miss_payload,
    script_decode,
    script_frames,
    sections,
)

TARGET = 0x06033020
OPEN = 1720  # timeline frame before every file's section C load
C2_BLOCK = {0: 3, 1: 2, 2: 3, 3: 2, 4: 2, 5: 2, 6: 3, 7: 2}
C3_BLOCK = {0: 6, 1: 5, 2: 6, 3: 5, 4: 5, 5: 5, 6: 6, 7: 5}
C3_BASE = {
    0: 0x195C,
    1: 0x15C,
    2: 0x1970,
    3: 0x170,
    4: 0x178,
    5: 0x178,
    6: 0x1988,
    7: 0x188,
}
C4 = {  # (block, base) before and after the re-index frame
    0: [(9, 0x120), (10, 0x1804)],
    1: [(8, 0x1920), (9, 0x4)],
    2: [(9, 0x11C), (10, 0x1804)],
    3: [(8, 0x191C), (9, 0x4)],
    4: [(8, 0x1920), (9, 0x4)],
    5: [(8, 0x1920)],
    6: [(9, 0x120)],
    7: [(8, 0x1920)],
}


def part1_chars(block: bytes) -> int:
    first, second = struct.unpack_from(">II", block, 4)
    return (second - first) // 128


def usable_slots(t: list[dict], w0: int, w1: int) -> set[int]:
    own = set().union(*(set(r["used"]["NBG1"]) for r in t if w0 <= r["frame"] <= w1))
    writes: defaultdict[int, list[int]] = defaultdict(list)
    outside: defaultdict[int, list[int]] = defaultdict(list)
    for r in t:
        for s in r["changed"]:
            writes[s].append(r["frame"])
        for layer, slots in r["used"].items():
            for s in slots:
                if not (layer == "NBG1" and w0 <= r["frame"] <= w1):
                    outside[s].append(r["frame"])
    found = set()
    for s in own:
        # the last write before the window ends: a block loaded during the
        # banner (after a re-index) writes its slots inside the window
        before = [f for f in writes.get(s, []) if OPEN <= f <= w1]
        if not before:
            continue
        tw = before[-1]
        later = [f for f in writes.get(s, []) if f > tw]
        tn = later[0] if later else 10**9
        if any(tw <= f < tn for f in outside.get(s, [])):
            continue
        found.add(s)
    for slots in free(t, w0, w1, own, OPEN).values():
        found |= set(slots)
    return found


def main(disc: Path, local: Path, out: Path) -> int:
    report: dict[str, object] = {}
    for k in range(8):
        data = (disc / f"OPENING{k}.ST2").read_bytes()
        found = sections(data)
        script, _ = script_decode(data, found[0][0])
        frames = script_frames(script)
        section_c, _ = lz_decode(data, found[2][0])
        stream = [out_ for _, out_ in blocks(miss_payload(data))]
        t = json.loads((local / f"full{k}" / "timeline.json").read_text())
        base1 = struct.unpack_from(">I", section_c, 4)[0] - 0x20
        base1 //= 32
        mine1 = set(range(base1 // 4, base1 // 4 + 107))
        w = [
            r["frame"]
            for r in t
            if r["frame"] > OPEN
            and r["base"] == base1
            and r["used"]["NBG1"]
            and set(r["used"]["NBG1"]) <= mine1
        ]
        extra = sorted(
            s - base1 // 4
            for slots in free(t, w[0], w[-1], mine1, OPEN).values()
            for s in slots
        )
        reindex = [
            n
            for n in range(952, 1118)
            for sec in frames[n].sections
            if sec.kind == "map"
            and sec.target == TARGET
            and sum(1 for v in map_decode(script, sec.start)[0][:0x1000] if v != 0xFFFF)
            > 900
        ]
        moving = [
            r["frame"]
            for i, r in enumerate(t[1:], 1)
            if r["scroll"][3] == 16
            and r["scroll"][2] != t[i - 1]["scroll"][2]
            and r["frame"] > 2520
        ]
        slots4 = usable_slots(t, moving[0], moving[-1])
        caption4 = []
        for block, base in C4[k]:
            limit = part1_chars(stream[block])
            indices = sorted(
                j for j in ((s - base // 4) % 4096 for s in slots4) if j < limit
            )
            caption4.append({"block": block, "base": base, "indices": indices})
        report[f"OPENING{k}"] = {
            "caption1": {"block": "C", "base": base1, "extra": extra},
            "caption2": {"block": C2_BLOCK[k]},
            "caption3": {"block": C3_BLOCK[k], "base": C3_BASE[k]},
            "caption4": {
                "reindex": reindex[0] if reindex else None,
                "blocks": caption4,
            },
        }
        print(
            k,
            "c1 extra",
            len(extra),
            "reindex",
            reindex,
            "c4",
            [(c["block"], hex(c["base"]), len(c["indices"])) for c in caption4],
        )
    out.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
