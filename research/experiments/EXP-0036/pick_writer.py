"""EXP-0036: pick Nash first and catch what writes his ending records.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/pick_writer.py CUE MC10 OUT

Adapted from `research/experiments/EXP-0032/pick_roster.py` (this repository,
commit ``4929cf8``): same select-screen state (cursor on Ken, first pick),
same key home and key sending, one pick only (``u``: Nash). New here:

- write breakpoints in log mode cover the six ending records (``RECORDS``,
  `EXP-0035`) and their cache-through mirror from just before A is pressed;
- after the pick, the records in RAM are compared with records 16-21 of
  MC10 (a decoded-file source: the ``MC10.SHP`` to expect, original or
  marker), and the whole buffer with MC10 plus the `EXP-0025` fix-ups.

CUE is the image to boot (the untouched source or the `EXP-0036` marker
image). The state was saved on the untouched image; the pick loads MC10
from CUE. Outputs go to the ignored OUT.
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
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0032"))
from analyze import fixups
from pick_roster import KEYS, pick_home, press

from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
STATE = Path("local/checkpoints/re004/f00002973.mcs")  # cursor on Ken
MOVES = "u"  # Ken -> Nash
BASE = 0x0024D000
RECORDS, SIZE, COUNT = 0x0024FEC0, 76, 6
OFFSET = RECORDS - BASE  # decoded MC10 offset 0x2EC0


def send(pid: int, keys: list[tuple[str, float]]) -> None:
    """``press``, retried when Mednafen was not frontmost (nothing was sent)."""
    for attempt in range(5):
        try:
            press(pid, keys)
            return
        except RuntimeError:
            if attempt == 4:
                raise
            time.sleep(1.0)


def parse(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def main(cue: Path, mc10: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    decoded, _ = decompress_file(mc10.read_bytes())
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    low, high = RECORDS, RECORDS + SIZE * COUNT - 1
    ranges = [
        f"{low:08X}-{high:08X}",
        f"{low | 0x20000000:08X}-{high | 0x20000000:08X}",
    ]
    result: dict[str, object] = {
        "cue": str(cue),
        "mc10": str(mc10),
        "state": str(STATE),
    }
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
            agent.screenshot((out / "start.png").resolve())
            before = agent.bus_read(low, high - low + 1)
            send(process.pid, [(KEYS[m][0], 0.1) for m in MOVES])
            agent.screenshot((out / "cursor.png").resolve())
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", ranges)
            send(process.pid, [("k", 0.2)])
            time.sleep(4)
            agent.pause()
            agent.breakpoints("write", [])
            agent.bpmode("halt")
            hits = [parse(h) for h in agent.events() if h.startswith("hit")]
            pcs: dict[str, int] = {}
            for hit in hits:
                pcs[hit.get("PC", "?")] = pcs.get(hit.get("PC", "?"), 0) + 1
            agent.screenshot((out / "after.png").resolve())
            ram = agent.bus_read(BASE, len(decoded))
            (out / "buffer.bin").write_bytes(ram)
            total, unaligned, exact = fixups(decoded, ram, BASE + 0x40)
            result.update(
                {
                    "hits": len(hits),
                    "writer_pcs": pcs,
                    "first_hits": hits[:3],
                    "records_before": before[:16].hex(),
                    "records_after": ram[OFFSET : OFFSET + 16].hex(),
                    "records_equal_mc10": ram[OFFSET : OFFSET + SIZE * COUNT]
                    == decoded[OFFSET : OFFSET + SIZE * COUNT],
                    "fixups": total,
                    "fixups_2_aligned": unaligned,
                    "ram_equals_mc10_plus_fixups": exact,
                }
            )
            agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
