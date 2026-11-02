r"""EXP-0069: the toggle build's routine, in RAM, over a route.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0069/toggle_ram.py \
        CUE MMPACK US_FILES SATURN_FILES OUT FIRST SECOND VALUE [FRAMES] [--gauge]

CUE is the toggle image and MMPACK its built ``MMPACK.PCA``. US_FILES and
SATURN_FILES hold the two name variants' built files (the regression's
``continue_hints_us_v4`` and ``continue_hints_saturn_v4``).

`tools.mednafen.route.run` (picks FIRST and SECOND from the route's select
state, FRAMES frames, default ``FRAMES``) with its ``--mmpack`` ranges
replaced by MMPACK's decoded differences from the untouched file
(each segment, as `EXP-0067/force_built.py` ``code_patches`` does; the
first segment's extension and any extra segment compared with zero) and
the setting byte ``SETTING`` set to VALUE (0 American, 1 Saturn). At every
screenshot it also records (with ``--gauge``, the COMBO GAUGE byte
``GAUGE`` is set to 1 too, `EXP-0070`):

- the 10 name sites' opcodes (``E002`` American, ``00BD`` Saturn);
- for each file whose variants differ, at each fighter buffer, whether the
  bytes of its runs are the American ones, the Saturn ones, or neither
  (another file is there).

A log-mode write breakpoint on ``TAIL`` (the end of WRAM-L that holds the
routine, `EXP-0069`) replaces the route's read log, so the route's
``read_hits`` are writes there. Writes ``OUT/toggle.json`` (the changes of
state, with frames) besides the route's own output. OUT is an ignored path.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.name_toggle import BASES, GAUGE, SETTING, SITES, runs
from tools.disc.prs import (
    decompress_file,
)
from tools.mednafen import route
from tools.mednafen.agent import Agent

_SPEC = importlib.util.spec_from_file_location(
    "force_built", "research/experiments/EXP-0067/force_built.py"
)
assert _SPEC and _SPEC.loader
FORCE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(FORCE)

FRAMES = 30000
TAIL = (0x002FF8C1, 0x002FFFFF)
FILES = ("MC08.SHP", "MC0E.SHP", "MC10.SHP", "MC11.SHP", "MCED.SHP")


def main(
    cue: Path,
    mmpack: Path,
    us_dir: Path,
    saturn_dir: Path,
    out: Path,
    first: int,
    second: int,
    value: int,
    frames: int,
    gauge: bool = False,
) -> int:
    original = FORCE.segments(route.track_file(route.SOURCE_TRACK, "MMPACK.PCA;1"))
    built = FORCE.segments(mmpack.read_bytes())
    code = []
    for k, (dest, new) in enumerate(built):
        old = original[k][1] if k < len(original) else b""
        old += bytes(len(new) - len(old))
        for offset, a, b in route.byte_ranges(old, new):
            code.append(f"{dest + offset:08X}:{a.hex()}:{b.hex()}")
    ranges = [
        (int(a, 16), bytes.fromhex(o), bytes.fromhex(n))
        for a, o, n in (p.split(":") for p in code)
    ]
    ranges.append((SETTING, bytes(1), bytes([value])))
    if gauge:
        ranges.append((GAUGE, bytes(1), bytes([1])))
    route.code_ranges = lambda original, built: ranges
    checks = []
    for name in FILES:
        us = decompress_file((us_dir / name).read_bytes())[0]
        sat = decompress_file((saturn_dir / name).read_bytes())[0]
        found = runs(us, sat)
        checks.append(
            (
                name,
                [(o, us[o : o + len(d)]) for o, d in found],
                [o for o, _ in found],
                found,
            )
        )
    log: list[dict[str, object]] = []
    last: dict[str, object] = {}
    original = Agent.screenshot

    def screenshot(self: Agent, path: Path) -> None:
        original(self, path)
        frame = self.status().get("frame")
        state: dict[str, object] = {
            "sites": "".join(
                {0xE002: "u", 0x00BD: "s"}.get(
                    int.from_bytes(self.bus_read(s, 2), "big"), "?"
                )
                for s in SITES
            )
        }
        for name, us_runs, _, sat_runs in checks:
            for base in BASES:
                got = [self.bus_read(base + o, len(b)) for o, b in us_runs]
                if got == [b for _, b in us_runs]:
                    state[f"{name}@{base:08x}"] = "us"
                elif got == [d for _, d in sat_runs]:
                    state[f"{name}@{base:08x}"] = "saturn"
        if state != last:
            log.append({"frame": frame, "shot": path.name, **state})
            last.clear()
            last.update(state)

    breakpoints = Agent.breakpoints

    def writes(self: Agent, kind: str, ranges: Sequence[str] = ()) -> None:
        if kind == "read" and ranges:
            kind, ranges = "write", [f"{TAIL[0]:08X}-{TAIL[1]:08X}"]
        breakpoints(self, kind, ranges)

    Agent.screenshot = screenshot  # type: ignore[method-assign]
    Agent.breakpoints = writes  # type: ignore[method-assign]
    route.run(cue, out, first, second, mmpack=mmpack, area=TAIL, frames=frames)
    (out / "toggle.json").write_text(json.dumps(log, indent=1) + "\n")
    for row in log:
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    gauge = "--gauge" in sys.argv
    a = [x for x in sys.argv[1:] if x != "--gauge"]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            Path(a[3]),
            Path(a[4]),
            int(a[5]),
            int(a[6]),
            int(a[7]),
            int(a[8]) if len(a) > 8 else FRAMES,
            gauge,
        )
    )
