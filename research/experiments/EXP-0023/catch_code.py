"""EXP-0023: halt on the first write to the quote script code when Start is pressed.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/catch_code.py OUT

Adapted from `EXP-0019`'s ``catch_font.py`` (scratch home with Start on K, the
`EXP-0013` session state 5116, K held for 0.2 s). The halt-mode write
breakpoint covers WRAM-H ``0x06066640``-``0x0606667F``, part of the quote
selector (`EXP-0021`), which appears between states 5116 and 5169. On the halt
the script saves registers, the events, the stack and work RAM. Outputs go to
the ignored OUT.
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
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/dbg003/session/states/f00005116.mcs")
KEYS_HOME = Path("local/mednafen_keys_start")
KEY_SCANCODE = 14  # SDL scancode for K
TABLE = ("06066640-0606667F", "26066640-2606667F")


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


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = keys_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.clear_events()
            agent.bpmode("halt")
            agent.breakpoints("write", TABLE)
            time.sleep(0.5)
            agent.screenshot((out / "before.png").resolve())
            hold_k(process.pid, 0.2)
            try:
                status = agent.wait_halted(40.0)
            except AgentError as error:
                result["halt"] = str(error)
                agent.screenshot((out / "no_halt.png").resolve())
                return 1
            regs = agent.regs()
            result["status"] = status
            result["regs"] = {k: f"{v:08X}" for k, v in regs.items()}
            result["events"] = agent.events()[:4]
            result["stack"] = agent.bus_read(regs["R15"], 64).hex()
            for space in ("workraml", "workramh"):
                agent.command(f"read {space} 0 {1 << 20} {(out / space).resolve()}.bin")
            agent.screenshot((out / "halt.png").resolve())
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
            (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "regs"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
