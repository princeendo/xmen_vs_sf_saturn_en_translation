r"""EXP-0050: poll the mixer's channel records while the game runs.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/channel_poll.py \
        CUE OUT STATE PREP_MOVES PRESS_MOVES SECONDS [ADDRESS:OLD:NEW ...]

Loads STATE (route pick home, silent), writes each ADDRESS:OLD:NEW (hex,
work RAM, after checking OLD), sends PREP_MOVES (for example the
cursor moves to a character) and runs 60 frames. It then lets the game run
in real time, sends PRESS_MOVES, and for SECONDS reads the 16 channel
records (``0x0601776C``, 28 bytes each) over and over through the agent.
Every (channel, start, end) seen with a non-zero start is logged with the
wall-clock time of its first sighting, in ``OUT/channels.json``. Sound RAM
is dumped at the end (``OUT/scspram.bin``) for decoding.

Polling is used because write breakpoints on the records never fire
(`EXP-0050`). The mixer likely runs on the slave SH-2, which the
breakpoints do not watch (HYPOTHESIS).
"""

from __future__ import annotations

import json
import os
import signal
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.route import BINARY, pick_home, send

CHANNELS, RECORD = 0x0601776C, 28


def main(
    cue: Path,
    out: Path,
    state: Path,
    prep: str,
    press: str,
    seconds: float,
    patches: list[str] | None = None,
) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    seen: dict[tuple[int, int, int], float] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=30.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            time.sleep(2)
            agent.loadstate(state.resolve())
            agent.pause()
            for spec in patches or []:
                address, old, new = spec.split(":")
                found = agent.bus_read(int(address, 16), len(bytes.fromhex(old)))
                if found != bytes.fromhex(old):
                    raise RuntimeError(f"{address}: found {found.hex()}")
                agent.bus_write(int(address, 16), bytes.fromhex(new))
            if prep:
                agent.run()
                send(process.pid, prep)
                agent.pause()
            agent.frames(60)
            agent.wait_halted(60.0)
            agent.run()
            presser = threading.Thread(target=send, args=(process.pid, press))
            t0 = time.monotonic()
            presser.start()
            while time.monotonic() - t0 < seconds:
                data = agent.bus_read(CHANNELS, 16 * RECORD)
                now = time.monotonic() - t0
                for channel in range(16):
                    _, start, end = struct.unpack_from(">III", data, RECORD * channel)
                    key = (channel, start, end)
                    if start and key not in seen:
                        seen[key] = now
            presser.join()
            agent.pause()
            (out / "scspram.bin").write_bytes(agent.read("scspram", 0, 0x80000))
            (out / "wram_h.bin").write_bytes(agent.bus_read(0x06000000, 0x100000))
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    rows = [
        {"channel": c, "start": f"{s:#x}", "end": f"{e:#x}", "first_seen": round(t, 3)}
        for (c, s, e), t in sorted(seen.items(), key=lambda kv: kv[1])
    ]
    (out / "channels.json").write_text(json.dumps(rows, indent=1) + "\n")
    print(json.dumps(rows))
    return 0


if __name__ == "__main__":
    a = sys.argv
    raise SystemExit(
        main(Path(a[1]), Path(a[2]), Path(a[3]), a[4], a[5], float(a[6]), a[7:])
    )
