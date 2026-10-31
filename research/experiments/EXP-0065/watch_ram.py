r"""EXP-0065: watch NBG1's scroll and index array every frame, to align script frames.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/watch_ram.py CUE STATE OUT COUNT

Loads STATE into a silent Mednafen on CUE, then COUNT times advances one
frame, halts and records NBG1's x and y scroll (RAM ``0x06020C60``, copied
to the registers every frame) and a CRC of the NBG1 index and attribute
arrays (``0x06033020``, 0x4000 bytes; changed only by the script's map
updates). Writes ``OUT/watch.json``. OUT is an ignored path.
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


def main(cue: Path, state: Path, out: Path, count: int) -> int:
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
    records: list[list[int]] = []
    with (out / "mednafen.log").open("w") as log:
        proc = subprocess.Popen(
            [str(BINARY.resolve()), str(cue)], env=env, stdout=log, stderr=log
        )
        try:
            agent = connect(agent_dir)
            agent.loadstate(state.resolve())  # refused while halted
            agent.pause()
            agent.wait_halted()
            for _ in range(count):
                agent.frames(1)
                agent.wait_halted(60.0)
                x, y = struct.unpack(">2H", agent.bus_read(0x06020C60, 4))
                arrays = zlib.crc32(agent.bus_read(0x06033020, 0x4000))
                records.append([int(agent.status()["frame"]), x, y, arrays])
        finally:
            proc.terminate()
            proc.wait(10)
    (out / "watch.json").write_text(json.dumps(records) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3])))
