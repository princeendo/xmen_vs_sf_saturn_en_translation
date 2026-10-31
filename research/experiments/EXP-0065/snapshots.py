r"""EXP-0065: VDP2 VRAM and NBG1 arrays at chosen frames, attract file forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/snapshots.py \
        CUE STATE OUT FILE FRAME [FRAME ...]

Loads STATE into a silent Mednafen on CUE, forces attract file FILE (0-7) by
replacing the pick at ``0x06021736`` with ``mov #FILE,r0`` (`EXP-0065`), and
at each FRAME (counted from the load, as `vram_visible.py`'s frames) halts and
writes ``OUT/f<frame>/vdp2.bin`` (VDP2 VRAM), ``arrays.bin`` (WRAM-H
``0x06033020``, 0x4000 bytes: NBG1's index and attribute arrays) and
``state.json`` (NBG1's base and scroll). OUT is an ignored path.
"""

from __future__ import annotations

import json
import os
import struct
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
                folder = out / f"f{target:05d}"
                folder.mkdir()
                (folder / "vdp2.bin").write_bytes(agent.read("vdp2vram", 0, 0x80000))
                (folder / "arrays.bin").write_bytes(agent.bus_read(0x06033020, 0x4000))
                base = struct.unpack(">I", agent.bus_read(0x06020BBC, 4))[0]
                x, y = struct.unpack(">2H", agent.bus_read(0x06020C60, 4))
                (folder / "state.json").write_text(
                    json.dumps({"frame": frame, "base": base, "scroll": [x, y]}) + "\n"
                )
        finally:
            proc.terminate()
            proc.wait(10)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(Path(a[0]), Path(a[1]), Path(a[2]), int(a[3]), [int(x) for x in a[4:]])
    )
