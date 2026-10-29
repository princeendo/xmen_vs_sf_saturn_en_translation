"""EXP-0028: pick a character with an image mounted and check the file that loads.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0028/pick_load.py CASE CUE BUILD OUT

Generalized from `research/experiments/EXP-0018/pick_load.py` (this
repository, commit ``7b02ab1``): the pick button is held on a session state
with the cursor on the character (CASE ``ryu``: `EXP-0013` state 5696;
``ken``: `EXP-0025` state 2973), using the scratch home
``local/mednafen_keys`` (pad A on K; `EXP-0025` ``catch_loader.py``). After
4 s the run pauses and reads the decompressed file at WRAM-L ``0x0024D000``.

The check decodes the character's MC file from BUILD and asks whether RAM
equals it, except for 32-bit fields (2-byte aligned) holding file value +
``0x0024D040`` (the relocation, `EXP-0025`). The table must also hold BUILD's
English bytes. Outputs (the RAM copy, a screenshot and ``result.json``) go to
the ignored OUT.
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
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
from analyze import fixups
from catch_loader import hold_k, keys_home

from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
BASE = 0x0024D000
CASES = {
    "ryu": (Path("local/dbg003/session/states/f00005696.mcs"), "MC09.SHP", 0x25D8),
    "ken": (Path("local/checkpoints/re004/f00002973.mcs"), "MC0A.SHP", 0x2A4C),
}


def main(case: str, cue: Path, build: Path, out: Path) -> int:
    state, file_name, table = CASES[case]
    decoded, _ = decompress_file((build / file_name).read_bytes())
    out.mkdir(parents=True, exist_ok=False)
    home = keys_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"case": case, "cue": str(cue)}
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
            agent.loadstate(state.resolve())
            time.sleep(0.5)
            hold_k(process.pid, 0.2)
            time.sleep(4)
            agent.pause()
            ram = agent.bus_read(BASE, len(decoded))
            (out / "buffer.bin").write_bytes(ram)
            agent.screenshot((out / "after_pick.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    total, unaligned, exact = fixups(decoded, ram, BASE + 0x40)
    result.update(
        {
            "fixups": total,
            "fixups_2_aligned": unaligned,
            "ram_equals_build_plus_fixups": exact,
            "english_table_loaded": ram[table : table + 800]
            == decoded[table : table + 800],
        }
    )
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    )
