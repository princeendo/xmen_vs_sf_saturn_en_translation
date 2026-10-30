"""EXP-0044: write a no-play timeline to any roster character's arcade ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/make_timeline.py \\
        OUT SLOT PARTNER LANG [--force-char HEX]

Generalized from `research/experiments/EXP-0037/make_timeline.py` (this
repository, commit ``606467a``):

- **First pick:** ``MOVES[SLOT]`` from the start cell (Cyclops, bottom row),
  one press every 40 frames from 1700, then button 1. The select grid is
  the `EXP-0037` snapshot's, and every pick is checked on the run's select
  snapshots.
- **Partner:** PARTNER is ``default`` (button 1 on whatever cell the second
  cursor starts on, from frame 1900) or ``right`` (one Right at 1900, then
  button 1 from 1940).
- **Route:** the CPU side's vitality (``0xFF4610``, ``0xFF4E10``) is set to
  0 every 20 frames from 3750, as in `EXP-0037`.
- **Language:** LANG is ``en`` or ``jp``. For ``jp``, the language and size
  words (``0xFF547A``, ``0xFF5478``) are set to 0 every 20 frames from
  ``LOG_FROM``.
- **Gouki** (``--force-char``) is not on the grid. The value HEX (slot x 2)
  is written to each word in ``CHAR_WORDS`` every 4 frames from 1830 to
  3700, after the pick. These are the 7 words that held the first pick's
  slot x 2 at frames 2,300 and 3,000 in three runs (Wolverine, Ryu, Charlie;
  `EXP-0044` README).
- **Logs** from ``LOG_FROM``: reads of the arcade text area
  ``0x17E000``-``0x18E179``.
- **Snapshots:** every 20 frames over the select screen (1800-2380), and
  every ``SNAP_EVERY`` frames from ``LOG_FROM`` to ``END``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LOG_FROM, END, SNAP_EVERY = 10000, 24000, 60
# from the start cell (row 4, column 2: Cyclops); grid rows top to bottom:
# Magneto Juggernaut Dhalsim Bison / Sabretooth Storm Chun-Li Zangief /
# Gambit Rogue Cammy Charlie / Wolverine Cyclops Ryu Ken
MOVES = {
    0: "l",
    1: "",
    2: "uu",
    3: "u",
    4: "ul",
    5: "uul",
    6: "uuu",
    7: "uuul",
    9: "r",
    10: "rr",
    11: "uur",
    12: "uuur",
    13: "uurr",
    14: "uuurr",
    16: "urr",
    17: "ur",
}
FIELDS = {"u": "P1 Up", "d": "P1 Down", "l": "P1 Left", "r": "P1 Right"}
CHAR_WORDS = (0xFF4052, 0xFF44B4, 0xFF4A22, 0xFF4CB4, 0xFF50B0, 0xFF7062, 0xFFA012)


def timeline(slot: int, partner: str, lang: str, force_char: int | None) -> str:
    moves = MOVES.get(slot, "")
    lines = [
        f"# EXP-0044: slot {slot} first, partner {partner}, language {lang}",
        "1000 repeat 4 30 8 Coin 1",
        "1200 repeat 10 60 8 1 Player Start",
    ]
    frame = 1700
    for move in moves:
        lines.append(f"{frame} press 8 {FIELDS[move]}")
        frame += 40
    lines.append(f"{max(frame, 1820)} press 8 P1 Button 1")
    if partner == "right":
        lines += ["1900 press 8 P1 Right", "1940 repeat 20 30 8 P1 Button 1"]
    elif partner == "default":
        lines.append("1900 repeat 20 30 8 P1 Button 1")
    else:
        raise ValueError(partner)
    if force_char is not None:
        for f in range(1830, 3700, 4):
            for word in CHAR_WORDS:
                lines.append(f"{f} debug do w@{word:x}={force_char:x}")
    for f in range(3750, END, 20):
        lines += [f"{f} debug do w@ff4610=0", f"{f} debug do w@ff4e10=0"]
    lines.append(f"{LOG_FROM} logreads 0x17E000 0x18E179 {{run}}/reads.txt")
    if lang == "jp":
        for f in range(LOG_FROM, END, 20):
            lines += [f"{f} debug do w@ff547a=0", f"{f} debug do w@ff5478=0"]
    elif lang != "en":
        raise ValueError(lang)
    lines += [f"{f} snap" for f in range(1800, 2400, 20)]
    lines += [f"{f} snap" for f in range(LOG_FROM, END, SNAP_EVERY)]
    lines += [f"{END} exit", ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("slot", type=int)
    parser.add_argument("partner", choices=("default", "right"))
    parser.add_argument("lang", choices=("en", "jp"))
    parser.add_argument("--force-char", type=lambda v: int(v, 16))
    args = parser.parse_args(argv)
    if args.slot not in MOVES and args.force_char is None:
        parser.error(f"slot {args.slot} has no grid cell; give --force-char")
    args.out.write_text(timeline(args.slot, args.partner, args.lang, args.force_char))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
