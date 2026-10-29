"""EXP-0032: pick roster characters on the select screen and check the file that loads.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0032/pick_roster.py \\
        CUE BUILD OUT STATE MOVES:SLOT [MOVES:SLOT ...]

Generalized from `research/experiments/EXP-0028/pick_load.py` (this repository,
commit ``1a6d268``), which picked the character under the cursor in a fixed
state. Here the cursor is moved first.

- STATE is a select-screen state.
- MOVES is a string of ``u``, ``d``, ``l`` and ``r``, or ``-`` for none.
- The scratch home ``local/mednafen_pick`` is the ``local/mednafen_keys``
  home (pad A on K; `EXP-0025` ``catch_loader.py``) with the pad's
  directions on I (up), M (down), J (left) and L (right). Keys are sent
  through System Events while Mednafen is frontmost, as ``hold_k`` does.

For each MOVES:SLOT, the run:

1. reloads STATE and screenshots it;
2. sends the moves and screenshots the cursor;
3. holds A for 0.2 s, waits 4 s, pauses, and screenshots;
4. reads WRAM-L from ``0x0024D000`` for the size of SLOT's decoded MC file
   from BUILD.

The check: RAM equals that file except for 32-bit fields (2-byte aligned)
holding file value + ``0x0024D040`` (`EXP-0025` ``fixups``), and the table
holds BUILD's English bytes. Outputs go to the ignored OUT.
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
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
from analyze import fixups
from catch_loader import keys_home

from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import apply_settings
from tools.mednafen.hotkeys import activate, frontmost_pid, osascript

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
PICK_HOME = Path("local/mednafen_pick")
ROSTER = Path("data/text/m5_roster.json")
BASE, TABLE_SIZE = 0x0024D000, 800
KEYS = {"u": ("i", 12), "d": ("m", 16), "l": ("j", 13), "r": ("l", 15)}


def pick_home() -> Path:
    source = keys_home()
    PICK_HOME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / "mednafen.cfg", PICK_HOME / "mednafen.cfg")
    firmware = PICK_HOME / "firmware"
    if not firmware.exists():
        firmware.symlink_to(Path("..") / "mednafen" / "firmware")
    names = {"u": "up", "d": "down", "l": "left", "r": "right"}
    apply_settings(
        PICK_HOME / "mednafen.cfg",
        {
            f"ss.input.port1.gamepad.{names[m]}": f"keyboard 0x0 {code}"
            for m, (_, code) in KEYS.items()
        },
    )
    return PICK_HOME


def press(pid: int, keys: list[tuple[str, float]]) -> None:
    previous = frontmost_pid()
    activate(pid)
    time.sleep(0.4)
    if frontmost_pid() != pid:
        raise RuntimeError("Mednafen is not frontmost; key not sent")
    script = 'tell application "System Events"\n'
    for key, hold in keys:
        script += f'key down "{key}"\ndelay {hold}\nkey up "{key}"\ndelay 0.35\n'
    osascript(script + "end tell")
    if previous != pid:
        activate(previous)


def main(cue: Path, build: Path, out: Path, state: Path, picks: list[str]) -> int:
    roster = {m["slot"]: m for m in json.loads(ROSTER.read_text())["roster"]}
    out.mkdir(parents=True, exist_ok=False)
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"cue": str(cue), "state": str(state)}
    rams: dict[str, bytes] = {}
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
            for pick in picks:
                moves, slot = pick.split(":")
                member = roster[int(slot)]
                name = f"s{int(slot):02d}"
                decoded, _ = decompress_file(
                    (build / member["mc_file"].split(";")[0]).read_bytes()
                )
                agent.loadstate(state.resolve())
                time.sleep(0.5)
                agent.screenshot((out / f"{name}-start.png").resolve())
                steps = [] if moves == "-" else [(KEYS[m][0], 0.1) for m in moves]
                if steps:
                    press(process.pid, steps)
                agent.screenshot((out / f"{name}-cursor.png").resolve())
                press(process.pid, [("k", 0.2)])
                time.sleep(4)
                agent.pause()
                ram = agent.bus_read(BASE, len(decoded))
                agent.screenshot((out / f"{name}-after.png").resolve())
                rams[name] = ram
                table = int(member["table_offset"], 16)
                total, unaligned, exact = fixups(decoded, ram, BASE + 0x40)
                result[name] = {
                    "slot": int(slot),
                    "file": member["mc_file"],
                    "moves": moves,
                    "fixups": total,
                    "fixups_2_aligned": unaligned,
                    "ram_equals_build_plus_fixups": exact,
                    "english_table_loaded": ram[table : table + TABLE_SIZE]
                    == decoded[table : table + TABLE_SIZE],
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    for name, ram in rams.items():
        (out / f"{name}-buffer.bin").write_bytes(ram)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            Path(sys.argv[4]),
            sys.argv[5:],
        )
    )
