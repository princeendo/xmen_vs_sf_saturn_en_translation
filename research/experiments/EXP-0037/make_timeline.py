"""EXP-0037: write a no-play timeline to Charlie's arcade ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0037/make_timeline.py \\
        OUT PARTNER LANG [JP_FRAME]

The route is ``timelines/discover2.txt``'s: coins and Start, Charlie picked
first (Up, Right, Right from Cyclops, button 1), then the partner, then the
CPU side's vitality words ``0xFF4610`` and ``0xFF4E10`` set to 0 every 20
frames from frame 3750.

- PARTNER is ``cyclops`` (button 1 on the cell the second cursor starts
  on) or ``ryu`` (one Right at frame 1900 first, then button 1 from 1940).
- LANG is ``en`` (the US set's own words) or ``jp``. For ``jp``, the
  language and size words ``0xFF547A`` and ``0xFF5478`` are set to 0 at
  JP_FRAME, then every 20 frames to the end, as `EXP-0022` did once for a
  win quote.

Logged from ``LOG_FROM``:

- reads of the arcade text area ``0x17E000``-``0x18E179`` (``reads.txt``);
- reads of the language word (``lang_reads.txt``).

Snapshots are taken every 20 frames over the select screen (1800-2380) and
every 30 frames from ``SNAP_FROM`` to ``END``. Paths use
``{run}``, which `run_mame.py` fills in.
"""

from __future__ import annotations

import sys
from pathlib import Path

LOG_FROM, SNAP_FROM, END = 12000, 13500, 20000


def timeline(partner: str, lang: str, jp_frame: int | None) -> str:
    lines = [
        f"# EXP-0037: Charlie first, partner {partner}, language {lang}",
        "1000 repeat 4 30 8 Coin 1",
        "1200 repeat 10 60 8 1 Player Start",
        "1700 press 8 P1 Up",
        "1740 press 8 P1 Right",
        "1780 press 8 P1 Right",
        "1820 press 8 P1 Button 1",
    ]
    if partner == "ryu":
        # the second cursor is on Cyclops by frame 1900 (discover1 snapshots);
        # a Right at 1860 was lost (run en_ryu picked Cyclops)
        lines += ["1900 press 8 P1 Right", "1940 repeat 20 30 8 P1 Button 1"]
    elif partner == "cyclops":
        lines.append("1900 repeat 20 30 8 P1 Button 1")
    else:
        raise ValueError(partner)
    for frame in range(3750, END, 20):
        lines += [f"{frame} debug do w@ff4610=0", f"{frame} debug do w@ff4e10=0"]
    lines += [
        f"{LOG_FROM} logreads 0x17E000 0x18E179 {{run}}/reads.txt",
        f"{LOG_FROM} logreads 0xFF547A 0xFF547B {{run}}/lang_reads.txt",
    ]
    if lang == "jp":
        if jp_frame is None:
            raise ValueError("jp needs JP_FRAME")
        for frame in range(jp_frame, END, 20):
            lines += [f"{frame} debug do w@ff547a=0", f"{frame} debug do w@ff5478=0"]
    elif lang != "en":
        raise ValueError(lang)
    lines += [f"{frame} snap" for frame in range(1800, 2400, 20)]
    lines += [f"{frame} snap" for frame in range(SNAP_FROM, END, 30)]
    lines += [f"{END} exit", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    jp = int(sys.argv[4]) if len(sys.argv) > 4 else None
    Path(sys.argv[1]).write_text(timeline(sys.argv[2], sys.argv[3], jp))
