r"""EXP-0069: every write to the toggle's candidate RAM over a route to an ending.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0069/session_writes.py \
        CUE OUT FIRST SECOND [FRAMES] [--key]

`tools.mednafen.route.run` (picks FIRST and SECOND from the route's select
state, then FRAMES frames, default ``FRAMES``) with its ``--area``
read-breakpoint log turned into a log-mode **write** breakpoint on every
range in ``RANGES`` (and each range's cache-through mirror, + ``0x20000000``):

- the names byte ``0x0601E370`` (in the saved settings block, `EXP-0068`);
- the setting word ``0x060F3720`` (R11's reach, `EXP-0068`);
- the zero runs in `MMPACK.PCA`'s first segment that could hold data:
  ``0x0601D89F`` (191), ``0x0601D974`` (160), ``0x0601E138`` (256),
  ``0x0601E270`` (72).

The route's ``read_hits`` in ``OUT/result.json`` are then writes, grouped
by PC; every hit's registers go to ``OUT/hits.json`` too. With ``--key``,
only ``KEY_RANGES`` are watched (the first run, ``writes1``, found the other
ranges written). OUT is an ignored path.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen import route
from tools.mednafen.agent import Agent

RANGES = (
    (0x0601E370, 0x0601E370),
    (0x060F3720, 0x060F3721),
    (0x0601D89F, 0x0601D95D),
    (0x0601D974, 0x0601DA13),
    (0x0601E138, 0x0601E237),
    (0x0601E270, 0x0601E2B7),
)
KEY_RANGES = RANGES[:2] + RANGES[4:]
FRAMES = 30000
_ORIGINAL = Agent.breakpoints
_PARSE = route.parse_hit
_HITS: list[dict[str, str]] = []
_WATCHED = list(RANGES)


def _keep(line: str) -> dict[str, str]:
    hit = _PARSE(line)
    _HITS.append(hit)
    return hit


def _writes(self: Agent, kind: str, ranges: Sequence[str] = ()) -> None:
    if kind == "read" and ranges:
        ranges = [
            f"{lo | mirror:08X}-{hi | mirror:08X}"
            for lo, hi in _WATCHED
            for mirror in (0, 0x20000000)
        ]
        kind = "write"
    _ORIGINAL(self, kind, ranges)


def main(cue: Path, out: Path, first: int, second: int, frames: int, key: bool) -> int:
    if key:
        _WATCHED[:] = KEY_RANGES
    Agent.breakpoints = _writes  # type: ignore[method-assign]
    route.parse_hit = _keep
    route.run(cue, out, first, second, area=RANGES[0], frames=frames)
    (out / "hits.json").write_text(json.dumps(_HITS, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    key = "--key" in sys.argv
    a = [x for x in sys.argv[1:] if x != "--key"]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            int(a[2]),
            int(a[3]),
            int(a[4]) if len(a) > 4 else FRAMES,
            key,
        )
    )
