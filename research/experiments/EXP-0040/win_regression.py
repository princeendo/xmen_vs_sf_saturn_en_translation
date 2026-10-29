"""EXP-0040: Ryu's eight English win-quote draws under version 3 and version 4.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0040/win_regression.py OUT

Adapted from `research/experiments/EXP-0032/force_records.py` (this
repository, commit ``d569bb1``): Ryu's `pre_ko` state, paused at seed 8520,
660 frames to the quote, the seeds for draws 0-7, and his 800 English bytes
from the roster build's ``MC09.SHP`` (``local/re010/b1``). For each draw,
three code variants are written into RAM before the quote:

- ``v3``: `patches_v3` for slots 0-17 (the roster build's code);
- ``v4``: version 4 (`v4_trial.v4_code`), no ending bit;
- ``v4_bit``: version 4 with Ryu's own slot (9) marked for an English
  ending (bit 7 of its fixed-table low byte). That bit must not change his
  win quotes.

Prediction: for every draw, ``v4`` and ``v4_bit`` give the same pointer,
the same 100 bytes and the same screenshot as ``v3``. Outputs go to the
ignored OUT.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0040"))
from v4_trial import ENDING_BIT, v4_code

from tools.disc.english_mode import FIXED_TABLE, as_bytes, patches_v3
from tools.disc.prs import decompress_file
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
BUILD_MC09 = Path("local/re010/b1/MC09.SHP")
STATE = Path("local/checkpoints/dbg003/f00009769.mcs")
STATE_SEED, FRAMES, TABLE_RAM, TABLE_OFFSET = 8520, 660, 0x0024F5D8, 0x25D8
SEED, POINTER, SLOT = 0x060F545A, 0x060F2490, 9
SEEDS = [2, 12, 15, 8, 21, 33, 17, 27029]  # draws 0-7 (EXP-0028)
SLOTS = list(range(18))


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    table, _ = decompress_file(BUILD_MC09.read_bytes())
    english = table[TABLE_OFFSET : TABLE_OFFSET + 800]
    variants = {
        "v3": patches_v3(SLOTS),
        "v4": v4_code(),
        "v4_bit": v4_code(),
    }
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, dict[str, object]] = {}
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
            for draw, seed in enumerate(SEEDS):
                for name, code in variants.items():
                    for _ in range(20):
                        agent.loadstate(STATE.resolve())
                        agent.pause()
                        if int.from_bytes(agent.bus_read(SEED, 2), "big") == STATE_SEED:
                            break
                        agent.run()
                    else:
                        raise RuntimeError(f"never paused at seed {STATE_SEED}")
                    for address, old, new in code:
                        found = agent.bus_read(address, len(as_bytes(old)))
                        if found != as_bytes(old):
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, as_bytes(new))
                    if name == "v4_bit":
                        at = FIXED_TABLE + 2 * SLOT + 1
                        low = agent.bus_read(at, 1)[0]
                        agent.bus_write(at, bytes([low | ENDING_BIT]))
                    agent.bus_write(TABLE_RAM, english)
                    agent.bus_write(SEED, seed.to_bytes(2, "big"))
                    agent.frames(FRAMES)
                    agent.wait_halted(120.0)
                    shot = (out / f"{draw}-{name}.png").resolve()
                    agent.screenshot(shot)
                    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                    result[f"{draw}-{name}"] = {
                        "pointer": f"{pointer:#010x}",
                        "codes": agent.bus_read(pointer, 100).hex(),
                        "sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                    }
                    agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    differ = [
        f"{draw}-{name}"
        for draw in range(len(SEEDS))
        for name in ("v4", "v4_bit")
        if result[f"{draw}-{name}"] != result[f"{draw}-v3"]
    ]
    expected = [
        draw
        for draw in range(len(SEEDS))
        if result[f"{draw}-v3"]["pointer"] != f"{TABLE_RAM + 100 * draw:#010x}"
    ]
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"differ_from_v3": differ, "v3_not_record_r": expected}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
