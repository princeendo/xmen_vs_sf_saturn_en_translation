r"""EXP-0068: the 10 name sites reading a setting word instead of the region word.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0068/toggle_names.py \
        CUE OUT FIRST SECOND VALUE [FRAMES]

`tools.mednafen.route.run` (picks FIRST and SECOND from the route's select
state, then FRAMES frames, default ``FRAMES``, a screenshot every ``SHOT``)
with its ``--mmpack`` ranges replaced by these RAM changes, each original
checked first:

- the six literals the 10 name sites load (``LITERALS``): ``0xD478`` (the
  region word, R11 + ``0xD478`` = ``0x060F5478``) becomes ``WORD`` - R11;
- the sound request that shares the name calls' literal (``PIN``,
  ``0x0604FD02``, request ``0x9E`` or ``0x9F``): ``mov.w @(r0,r11),r0``
  becomes ``mov #0,r0``, so it stays as the Saturn has it;
- ``WORD`` (``0x060F3720``, zero in every WRAM-H dump on hand) set to VALUE.

VALUE 0 should give the Saturn's names, VALUE 2 the American ones. OUT is
an ignored path.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen import route

R11, REGION, WORD = 0x060F8000, 0xD478, 0x060F3720
LITERALS = (0x0604FD14, 0x06063A08, 0x0606E048, 0x06073B2E, 0x0607FE68, 0x06080026)
PIN = (0x0604FD02, "00BD", "E000")
FRAMES, SHOT = 3000, 30


def ranges(value: int) -> list[tuple[int, bytes, bytes]]:
    offset = (WORD - R11) & 0xFFFF
    out = [
        (lit, REGION.to_bytes(2, "big"), offset.to_bytes(2, "big")) for lit in LITERALS
    ]
    out.append((PIN[0], bytes.fromhex(PIN[1]), bytes.fromhex(PIN[2])))
    out.append((WORD, bytes(2), value.to_bytes(2, "big")))
    return out


def main(cue: Path, out: Path, first: int, second: int, value: int, frames: int) -> int:
    route.code_ranges = lambda original, built: ranges(value)
    route.run(cue, out, first, second, mmpack=cue, frames=frames, shot_every=SHOT)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            int(a[2]),
            int(a[3]),
            int(a[4]),
            int(a[5]) if len(a) > 5 else FRAMES,
        )
    )
