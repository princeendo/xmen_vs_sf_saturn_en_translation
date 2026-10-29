"""EXP-0028: read the quote pointer from play-check states and name the record it shows.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0028/play_pointers.py \\
        CUE BUILD OUT STATE [STATE ...]

Each STATE (from the user's play session, `tools.mednafen.session_recorder`)
is loaded with CUE mounted and paused. The run reads the quote pointer
(``0x060F2490``) and the 100 bytes it points to, and saves a screenshot. It
then looks for those bytes in BUILD's decoded MC files for Ryu and Ken and
reports the file and English record (0-7) that hold them, or none. Outputs
(screenshots and ``result.json``) go to the ignored OUT.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
POINTER, RECORD = 0x060F2490, 100
TABLES = {"MC09.SHP": 0x25D8, "MC0A.SHP": 0x2A4C}  # Ryu, Ken (EXP-0017, EXP-0025)


def english_records(build: Path) -> dict[bytes, str]:
    records = {}
    for name, offset in TABLES.items():
        decoded, _ = decompress_file((build / name).read_bytes())
        for index in range(8):
            start = offset + RECORD * index
            records[decoded[start : start + RECORD]] = f"{name} English {index}"
    return records


def main(cue: Path, build: Path, out: Path, states: list[Path]) -> int:
    records = english_records(build)
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"cue": str(cue)}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            time.sleep(3)
            for state in states:
                agent.loadstate(state.resolve())
                agent.pause()
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                shown = agent.bus_read(pointer, RECORD)
                agent.screenshot((out / f"{state.stem}.png").resolve())
                result[state.stem] = {
                    "pointer": f"{pointer:#010x}",
                    "record": records.get(shown),
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            [Path(p) for p in sys.argv[4:]],
        )
    )
