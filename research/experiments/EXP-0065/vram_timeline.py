r"""EXP-0065: which VDP2 character slots are written, and which are used, over time.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/vram_timeline.py \
        CUE STATE OUT STEP COUNT

Loads STATE into a silent Mednafen on CUE, then COUNT times advances STEP
frames, halts and reads VDP2 VRAM (the ``vdp2vram`` space). VRAM is split
into 128-byte slots (one 2 x 2-cell character, or four 8 x 8 cells). For
each step it records:

- ``changed``: the slots whose bytes differ from the previous step;
- ``used``: per layer, the slots its map pages reference, with the layer
  settings every saved state from the first caption on shares (`EXP-0065`):
  NBG0 1 x 1 cells, page ``0x64000``; NBG3 1 x 1, ``0x68000``; NBG1 2 x 2,
  ``0x6C000``-``0x6FFFF``; NBG2 2 x 2, ``0x70000``-``0x7FFFF``; all 2-word
  pattern names. A page counts only if at least 90% of its entries have no
  bits set outside the character, palette and flip fields (pages of
  leftover data are skipped). Scroll is not known, so a counted page counts
  whole: a conservative over-estimate of use.

Writes ``OUT/timeline.json``. OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

SLOT = 128
VRAM = 0x80000
LAYERS = {
    "NBG0": (False, [0x64000 + 0x4000 * k for k in range(1)], 0x4000),
    "NBG3": (False, [0x68000 + 0x4000 * k for k in range(1)], 0x4000),
    "NBG1": (True, [0x6C000 + 0x1000 * k for k in range(4)], 0x1000),
    "NBG2": (True, [0x70000 + 0x1000 * k for k in range(16)], 0x1000),
}
STRAY = 0x3F80  # upper-word bits outside palette (0-6) and flips (14-15)


def used_slots(vram: bytes) -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}
    for name, (big, pages, size) in LAYERS.items():
        slots: set[int] = set()
        for page in pages:
            entries = struct.unpack_from(f">{size // 4}I", vram, page)
            clean = sum(1 for e in entries if not (e >> 16) & STRAY)
            if clean < 0.9 * len(entries):
                continue
            for entry in entries:
                char = entry & 0x7FFF
                start = (char * 32) % VRAM
                end = start + (128 if big else 32)
                slots.update(range(start // SLOT, (end - 1) // SLOT + 1))
        found[name] = sorted(slots)
    return found


def main(cue: Path, state: Path, out: Path, step: int, count: int) -> int:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = out / "agent"
    agent_dir.mkdir()
    env = dict(
        os.environ,
        MEDNAFEN_HOME=str(quiet_home().resolve()),
        MEDNAFEN_AGENT_DIR=str(agent_dir),
        MEDNAFEN_ALLOWMULTI="1",
    )
    records: list[dict[str, object]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            previous: list[int] = []
            for _ in range(count):
                agent.frames(step)
                agent.wait_halted(60.0)
                vram = agent.read("vdp2vram", 0, VRAM)
                hashes = [zlib.crc32(vram[i : i + SLOT]) for i in range(0, VRAM, SLOT)]
                changed = [
                    i for i, h in enumerate(hashes) if previous and h != previous[i]
                ]
                previous = hashes
                records.append(
                    {
                        "frame": int(agent.status()["frame"]),
                        "changed": changed,
                        "used": used_slots(vram),
                    }
                )
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "timeline.json").write_text(json.dumps(records) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), int(a[4])))
