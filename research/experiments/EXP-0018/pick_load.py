"""EXP-0018: pick Ryu from a saved state with a given image mounted; read the load.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/pick_load.py CUE OUT

Mounts CUE in the patched build with the scratch home ``local/mednafen_keys``
(pad A on the K key, `EXP-0017`), loads the `EXP-0013` session state 5696
(cursor on Ryu, before the pick), holds K for 0.2 s, lets the game run 4 s,
pauses, and saves the 43,064 bytes at WRAM-L ``0x0024D000`` where ``MC09.SHP``
is decompressed (`EXP-0017`), plus a screenshot. If a state replays with later
disc reads coming from the mounted image (MSHvSF `EXP-0036`; a hypothesis for
XvSF), the saved bytes come from CUE's ``MC09.SHP``. Outputs go to the ignored
OUT.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, apply_settings, configure
from tools.mednafen.hotkeys import activate, frontmost_pid, osascript

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
STATE = Path("local/dbg003/session/states/f00005696.mcs")
KEYS_HOME = Path("local/mednafen_keys")
KEY_SCANCODE = 14  # SDL scancode for K
BUFFER, SIZE = 0x0024D000, 43064


def keys_home() -> Path:
    configure()
    KEYS_HOME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(QUIET_HOME / "mednafen.cfg", KEYS_HOME / "mednafen.cfg")
    firmware = KEYS_HOME / "firmware"
    if not firmware.exists():
        firmware.symlink_to(Path("..") / "mednafen" / "firmware")
    apply_settings(
        KEYS_HOME / "mednafen.cfg",
        {"ss.input.port1.gamepad.a": f"keyboard 0x0 {KEY_SCANCODE}"},
    )
    return KEYS_HOME


def hold_k(pid: int, seconds: float) -> None:
    previous = frontmost_pid()
    activate(pid)
    time.sleep(0.4)
    if frontmost_pid() != pid:
        raise RuntimeError("Mednafen is not frontmost; key not sent")
    osascript(
        'tell application "System Events"\nkey down "k"\n'
        f'delay {seconds}\nkey up "k"\nend tell'
    )
    if previous != pid:
        activate(previous)


def main(cue: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = keys_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
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
            agent.loadstate(STATE.resolve())
            time.sleep(0.5)
            hold_k(process.pid, 0.2)
            time.sleep(4)
            agent.pause()
            result["status"] = agent.status()
            (out / "buffer.bin").write_bytes(agent.bus_read(BUFFER, SIZE))
            agent.screenshot((out / "after_pick.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
            (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
