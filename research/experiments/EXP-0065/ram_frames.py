r"""EXP-0065: WRAM-H at chosen frames, attract file forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/ram_frames.py \
        CUE STATE OUT FILE FRAME [FRAME ...]

As `snapshots.py` (attract file FILE forced, frames counted from the load),
but at each FRAME writes ``OUT/f<frame>.bin``: WRAM-H ``0x06000000``-
``0x060FFFFF`` from the stock debugger read. OUT is an ignored path.
"""

from __future__ import annotations

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
                data = b"".join(
                    agent.bus_read(0x06000000 + at, 0x10000)
                    for at in range(0, 0x100000, 0x10000)
                )
                (out / f"f{target:05d}.bin").write_bytes(data)
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), [int(x) for x in a[4:]])
    )
