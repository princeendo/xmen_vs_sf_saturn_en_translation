"""EXP-0019: cold-boot an image, press Start, and read the quote font.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0019/cold_font.py CUE OUT [WAIT]

Adapted from ``font_load.py``. Cold-boots CUE in the patched build with the
scratch home ``local/mednafen_keys_start`` (pad Start on the K key), lets it run
WAIT seconds (default 60) with no input, then holds K for 0.2 s and lets the
game run 6 s. It then saves a state, pauses, and saves the 209,285 bytes at
WRAM-L ``0x002C3EA0`` (the quote font after the copy from cart RAM), plus a
screenshot. Every disc read comes from CUE. Outputs go to the ignored OUT.
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
KEYS_HOME = Path("local/mednafen_keys_start")
KEY_SCANCODE = 14  # SDL scancode for K
BUFFER, SIZE = 0x002C3EA0, 209285


def keys_home() -> Path:
    configure()
    KEYS_HOME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(QUIET_HOME / "mednafen.cfg", KEYS_HOME / "mednafen.cfg")
    firmware = KEYS_HOME / "firmware"
    if not firmware.exists():
        firmware.symlink_to(Path("..") / "mednafen" / "firmware")
    apply_settings(
        KEYS_HOME / "mednafen.cfg",
        {"ss.input.port1.gamepad.start": f"keyboard 0x0 {KEY_SCANCODE}"},
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


def main(cue: Path, out: Path, wait: float) -> int:
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
            time.sleep(wait)
            hold_k(process.pid, 0.2)
            time.sleep(6)
            agent.savestate((out / "after_start.mcs").resolve())
            time.sleep(1)
            agent.pause()
            result["status"] = agent.status()
            (out / "font.bin").write_bytes(agent.bus_read(BUFFER, SIZE))
            agent.screenshot((out / "after_start.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
            (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), wait))
