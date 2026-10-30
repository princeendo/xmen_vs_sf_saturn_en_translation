"""EXP-0048 (LOC-001, arcade side): a no-play timeline with a dense snapshot schedule.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/arcade/make_timeline.py \\
        OUT SLOT PARTNER LANG [--force-char HEX] [--moves MOVES] \\
        [--snap FIRST LAST STEP] [--end FRAME] [--no-coin]

Copied from `research/experiments/EXP-0044/make_timeline.py` (this
repository, commit ``8caed7c``). Changes, kept minimal:

- ``--snap FIRST LAST STEP`` (repeatable) adds snapshots every STEP frames
  from FIRST to LAST (exclusive), on top of the original select-screen and
  ending schedules. Duplicate frames are written once.
- ``--moves`` replaces ``MOVES[SLOT]`` (letters ``u``, ``d``, ``l``, ``r``)
  for the first pick, so a cell not in ``MOVES`` (Gouki) can be tried as a
  genuine grid pick. A slot given only this way needs no ``--force-char``.
- ``--end`` replaces ``END`` (the exit frame and the end of the vitality,
  language and ending-snapshot schedules).
- ``--no-coin`` writes an attract-mode timeline instead: no input, no RAM
  write, no read log, snapshots only from ``--snap``, exit at ``--end``.

Everything else is the `EXP-0044` route, unchanged:

- **First pick:** ``MOVES[SLOT]`` from the start cell (Cyclops, bottom row),
  one press every 40 frames from 1700, then button 1. The select grid was
  validated on ``xmvsfu`` only; on any other set every pick is checked on
  the run's select snapshots.
- **Partner:** PARTNER is ``default`` (button 1 on whatever cell the second
  cursor starts on, from frame 1900) or ``right`` (one Right at 1900, then
  button 1 from 1940).
- **Route:** the CPU side's vitality (``0xFF4610``, ``0xFF4E10``) is set to
  0 every 20 frames from 3750. Found on ``xmvsfu``; a HYPOTHESIS on any
  other set until a run's snapshots show it working.
- **Language:** LANG is ``en`` or ``jp``. For ``jp``, the language and size
  words (``0xFF547A``, ``0xFF5478``) are set to 0 every 20 frames from
  ``LOG_FROM``. ``en`` writes nothing.
- **Forced character** (``--force-char``): the value HEX (slot x 2) is
  written to each word in ``CHAR_WORDS`` every 4 frames from 1830 to 3700,
  after the pick (``xmvsfu`` words, `EXP-0044`).
- **Logs** from ``LOG_FROM``: reads of the arcade text area
  ``0x17E000``-``0x18E179``.
- **Snapshots:** every 20 frames over the select screen (1800-2380), and
  every ``SNAP_EVERY`` frames from ``LOG_FROM`` to the end.
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


def snaps(extra: list[tuple[int, int, int]], end: int, attract: bool) -> list[str]:
    frames: set[int] = set()
    if not attract:
        frames.update(range(1800, 2400, 20))
        frames.update(range(LOG_FROM, end, SNAP_EVERY))
    for first, last, step in extra:
        frames.update(range(first, min(last, end), step))
    return [f"{f} snap" for f in sorted(frames)]


def timeline(
    slot: int,
    partner: str,
    lang: str,
    force_char: int | None,
    moves: str,
    extra: list[tuple[int, int, int]],
    end: int,
) -> str:
    lines = [
        f"# EXP-0048: slot {slot} first ({moves or 'no moves'}), partner {partner},"
        f" language {lang}, force {force_char}",
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
    for f in range(3750, end, 20):
        lines += [f"{f} debug do w@ff4610=0", f"{f} debug do w@ff4e10=0"]
    lines.append(f"{LOG_FROM} logreads 0x17E000 0x18E179 {{run}}/reads.txt")
    if lang == "jp":
        for f in range(LOG_FROM, end, 20):
            lines += [f"{f} debug do w@ff547a=0", f"{f} debug do w@ff5478=0"]
    elif lang != "en":
        raise ValueError(lang)
    lines += snaps(extra, end, attract=False)
    lines += [f"{end} exit", ""]
    return "\n".join(lines)


def attract_timeline(extra: list[tuple[int, int, int]], end: int) -> str:
    lines = ["# EXP-0048: attract mode, no coins, no input"]
    lines += snaps(extra, end, attract=True)
    lines += [f"{end} exit", ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("slot", type=int)
    parser.add_argument("partner", choices=("default", "right"))
    parser.add_argument("lang", choices=("en", "jp"))
    parser.add_argument("--force-char", type=lambda v: int(v, 16))
    parser.add_argument("--moves")
    parser.add_argument(
        "--snap", nargs=3, type=int, action="append", default=[], metavar="N"
    )
    parser.add_argument("--end", type=int, default=END)
    parser.add_argument("--no-coin", action="store_true")
    args = parser.parse_args(argv)
    extra = [(a, b, c) for a, b, c in args.snap]
    if args.no_coin:
        args.out.write_text(attract_timeline(extra, args.end))
        return 0
    if args.moves is not None and set(args.moves) - set(FIELDS):
        parser.error(f"--moves takes only {''.join(FIELDS)}")
    moves = args.moves if args.moves is not None else MOVES.get(args.slot)
    if moves is None and args.force_char is None:
        parser.error(f"slot {args.slot} has no grid cell; give --force-char or --moves")
    text = timeline(
        args.slot,
        args.partner,
        args.lang,
        args.force_char,
        moves or "",
        extra,
        args.end,
    )
    args.out.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
