r"""EXP-0047: run every roster ending on the M8 build with the route tool.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/run_endings.py \
        CUE MMPACK OUT [SLOT ...]

For each roster slot (``data/text/m8_ending_roster.json``, or the SLOTs
given), one `tools.mednafen.route` run with:

- the slot picked first and the second cursor's start cell picked second
  (Cyclops, or Wolverine when Cyclops is first), so the partner takes no
  cursor moves;
- policy ``first``, and the build's code written into RAM (``--mmpack``);
- a read log on the slot's English ending records in the first buffer
  (quote table + 800 to + 800 + 100n - 1);
- ``14,000 + 450n`` frames, n being the slot's English ending count. The
  M7 and `END-013` endings started near frame 12,800, and pages last at
  most about 460 frames.

Up to ``PARALLEL`` runs go at once, each started at least ``STAGGER``
seconds after the last, so that no two pick phases overlap (keys go to the
frontmost window). A run whose load check fails (a lost key; `EXP-0046`)
is started again, up to ``ATTEMPTS`` times. Writes ``OUT/runs.json``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.english_mode import ENDING_RECORDS
from tools.mednafen.route import FIRST_BUFFER, SECOND_START, WOLVERINE

ROSTER = Path("data/text/m8_ending_roster.json")
PARALLEL, STAGGER, ATTEMPTS = 4, 75.0, 3


def frames(count: int) -> int:
    return 14000 + 450 * count


def command(cue: Path, mmpack: Path, out: Path, member: dict[str, object]) -> list[str]:
    slot = int(str(member["slot"]))
    count = int(str(member["english_ending_records"]))
    start = FIRST_BUFFER + int(str(member["table_offset"]), 16) + ENDING_RECORDS
    second = WOLVERINE if slot == SECOND_START else SECOND_START
    return [
        *(sys.executable, "-m", "tools.mednafen.route", str(cue), str(out)),
        *("--first", str(slot), "--second", str(second), "--policy", "first"),
        *("--mmpack", str(mmpack), "--frames", str(frames(count))),
        *("--area", f"{start:08X}:{start + 100 * count - 1:08X}"),
    ]


def main(cue: Path, mmpack: Path, out: Path, chosen: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    members = json.loads(ROSTER.read_text())["members"]
    if chosen:
        members = [m for m in members if m["slot"] in chosen]
    queue = [(m, 1) for m in members]
    running: list[tuple[subprocess.Popen[bytes], dict[str, object], int, Path]] = []
    runs: list[dict[str, object]] = []
    last_start = 0.0
    env = {**os.environ, "MEDNAFEN_ALLOWMULTI": "1"}
    while queue or running:
        if (
            queue
            and len(running) < PARALLEL
            and time.monotonic() - last_start > STAGGER
        ):
            member, attempt = queue.pop(0)
            target = out / f"s{int(str(member['slot'])):02d}_a{attempt}"
            log = (out / f"{target.name}.log").open("wb")
            process = subprocess.Popen(
                command(cue, mmpack, target, member), stdout=log, stderr=log, env=env
            )
            running.append((process, member, attempt, target))
            last_start = time.monotonic()
            print(f"started {target.name}", flush=True)
        for entry in list(running):
            process, member, attempt, target = entry
            if process.poll() is None:
                continue
            running.remove(entry)
            result_path = target / "result.json"
            check = (
                json.loads(result_path.read_text())["load_check"]
                if result_path.exists()
                else None
            )
            ok = bool(check and check["first"] and check["second"])
            runs.append(
                {
                    "run": target.name,
                    "slot": member["slot"],
                    "exit": process.returncode,
                    "load_check": check,
                }
            )
            print(f"finished {target.name} load ok={ok}", flush=True)
            if not ok and attempt < ATTEMPTS:
                queue.append((member, attempt + 1))
        time.sleep(2)
    (out / "runs.json").write_text(json.dumps(runs, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
            Path(sys.argv[3]),
            [int(s) for s in sys.argv[4:]],
        )
    )
