"""EXP-0025: halt on the first write to Ken's quote table when Ken is picked.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/catch_loader.py OUT [--control]

Adapted from `research/experiments/EXP-0017/catch_loader.py` (this repository,
commit ``01a70b7``, with ``keys_home`` and ``hold_k`` copied unchanged): the
state and the table range are Ken's. It uses the same
scratch home (``local/mednafen_keys``, Saturn pad A on the K key). From session
state 2973 (cursor on Ken, before the first pick; `RE-004` session), a
halt-mode write breakpoint covers Ken's 21 records at WRAM-L ``0x0024FA4C``
(and the ``0x2024…`` cache-through mirror). The trial holds K for 0.2 s; the
control presses nothing and runs 120 frames. On a halt the script saves
registers, events, the stack and work RAM. Outputs go to the ignored OUT.
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
STATE = Path("local/checkpoints/re004/f00002973.mcs")
KEYS_HOME = Path("local/mednafen_keys")
KEY_SCANCODE = 14  # SDL scancode for K
TABLE = ("0024FA4C-00250087", "2024FA4C-20250087")  # 21 records x 76 bytes


def keys_home() -> Path:
    """Copied unchanged from `EXP-0017`'s ``catch_loader.py``."""
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
    """Copied unchanged from `EXP-0017`'s ``catch_loader.py``."""
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


def main(out: Path, control: bool) -> int:
    out.mkdir(parents=True, exist_ok=False)
    home = keys_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"control": control}
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
            if control:
                agent.pause()
                agent.frames(120)
                try:
                    agent.wait_halted(30.0)
                except AgentError as error:
                    result["halt"] = str(error)
                result["events"] = agent.events()
                agent.screenshot((out / "after.png").resolve())
                return 0
            hold_k(process.pid, 0.2)
            try:
                status = agent.wait_halted(20.0)
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
    raise SystemExit(main(Path(sys.argv[1]), "--control" in sys.argv[2:]))
