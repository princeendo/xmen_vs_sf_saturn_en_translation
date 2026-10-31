r"""EXP-0065: NBG1's scroll words and line-scroll table at chosen frames.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/line_scroll.py \
        CUE STATE OUT FILE FRAME [FRAME ...]

As `snapshots.py` (attract file FILE forced, frames counted from the load),
but at each FRAME writes ``OUT/f<frame>.json``: the scroll words at WRAM-H
``0x06020C5C``-``0x06020C67`` and the first 0x400 bytes of the line-scroll
table at ``0x060234D4`` (RAM) and VDP2 VRAM ``0x63C00``, as hex.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.replay_state import BINARY, connect, quiet_home

PICK, PICK_OLD = 0x06021736, bytes.fromhex("0003")


def main(cue: Path, state: Path, out: Path, file: int, targets: list[int]) -> int:
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
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            if agent.bus_read(PICK, 2) != PICK_OLD:
                raise SystemExit("the file pick is not where expected")
            agent.bus_write(PICK, bytes([0xE0, file]))
            frame = int(agent.status()["frame"])
            for target in sorted(targets):
                agent.frames(target - frame)
                agent.wait_halted(max(60.0, (target - frame) / 30))
                frame = int(agent.status()["frame"])
                record = {
                    "frame": frame,
                    "scroll_words": agent.bus_read(0x06020C5C, 12).hex(),
                    "line_ram": agent.bus_read(0x060234D4, 0x400).hex(),
                    "line_vram": agent.read("vdp2vram", 0x63C00, 0x400).hex(),
                }
                (out / f"f{target:05d}.json").write_text(json.dumps(record) + "\n")
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), [int(x) for x in a[4:]])
    )
