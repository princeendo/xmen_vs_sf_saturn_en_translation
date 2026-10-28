"""Run stock Mednafen and press its hotkeys at fixed times (macOS).

Stock Mednafen takes screenshots and saves or loads states only through
hotkeys. This tool launches it, and at each `--at SECONDS:KEY` brings the
Mednafen process (by PID) to the front, checks that it is frontmost, sends the
key with System Events, and returns focus to the app that was frontmost before.
If Mednafen is not frontmost the key is not sent and the run stops, so a key
never reaches another app. Needs Accessibility permission for System Events.

Keys are Mednafen 1.32.1 default hotkeys: F5 save state, F7 load state,
F9 screenshot, F12 exit (sent last automatically).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.cold_boot import MEDNAFEN, QUIET_HOME, sha256

# macOS virtual key codes.
KEY_CODES = {"F5": 96, "F7": 98, "F9": 101, "F12": 111}


def osascript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"osascript failed: {result.stderr.strip()}")
    return result.stdout.strip()


def frontmost_pid() -> int:
    return int(
        osascript(
            'tell application "System Events" to get unix id of first process '
            "whose frontmost is true"
        )
    )


def press(pid: int, key: str) -> None:
    """Send ``key`` to process ``pid``; restore the previous front app."""
    previous = frontmost_pid()
    osascript(
        'tell application "System Events" to set frontmost of first process '
        f"whose unix id is {pid} to true"
    )
    time.sleep(0.3)
    if frontmost_pid() != pid:
        raise RuntimeError(f"Mednafen (pid {pid}) is not frontmost; {key} not sent")
    osascript(f'tell application "System Events" to key code {KEY_CODES[key]}')
    if previous != pid:
        osascript(
            'tell application "System Events" to set frontmost of first process '
            f"whose unix id is {previous} to true"
        )


def parse_step(text: str) -> tuple[float, str]:
    seconds, _, key = text.partition(":")
    if key not in KEY_CODES:
        raise argparse.ArgumentTypeError(f"unknown key {key!r}")
    return float(seconds), key


def run(
    image: Path,
    log: Path,
    steps: Sequence[tuple[float, str]],
    home: Path,
    mednafen: Path,
) -> dict[str, object]:
    env = {**os.environ, "MEDNAFEN_HOME": str(home.resolve())}
    command = [str(mednafen), str(image)]
    pressed = []
    with log.open("wb") as handle:
        process = subprocess.Popen(
            command, env=env, stdout=handle, stderr=subprocess.STDOUT
        )
        started = time.time()
        try:
            for at, key in sorted(steps):
                time.sleep(max(0.0, started + at - time.time()))
                press(process.pid, key)
                pressed.append({"at": round(time.time() - started, 2), "key": key})
            press(process.pid, "F12")
            pressed.append({"at": round(time.time() - started, 2), "key": "F12"})
            code = process.wait(timeout=30)
        except BaseException:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
            raise
    return {
        "command": command,
        "home": str(home),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "pressed": pressed,
        "exit_code": code,
        "log_sha256": sha256(log),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("log", type=Path, help="new log file; run.json beside it")
    parser.add_argument(
        "--at", dest="steps", action="append", type=parse_step, default=[]
    )
    parser.add_argument("--home", type=Path, default=QUIET_HOME)
    parser.add_argument("--mednafen", type=Path, default=MEDNAFEN)
    args = parser.parse_args(argv)
    if args.log.exists():
        parser.error(f"{args.log} exists")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    record = run(args.image, args.log, args.steps, args.home, args.mednafen)
    args.log.with_suffix(".json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
