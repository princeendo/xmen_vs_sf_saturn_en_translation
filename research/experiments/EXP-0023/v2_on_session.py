"""EXP-0023: run patch version 2 on states from the version-1 play session.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/v2_on_session.py OUT RUN...

Each RUN is ``NAME:STATE:FRAMES:MODE``:

* ``STATE`` is a state from the version-1 play check (``local/layout001/session``).
* ``FRAMES`` is how far to run, to a moment when the quote is on screen.
* ``MODE`` is ``v1``, to run the state as recorded (its RAM holds the
  version-1 code); ``v2``, to replace every patch site with version 2
  first; or ``orig``, to restore every site's original bytes (the unpatched
  game, as a control).

For ``v2``, every site must hold version-1 or original bytes before the write.
Each run saves a screenshot, VDP1 VRAM, the record pointer and the 100 bytes
it points at (``codes_at_quote``) for ``cell_check_en.py``. The image is the
version-1 build, though nothing is read from disc between the state and the
quote. Outputs go to the ignored OUT.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from english_patch import PATCHES, PATCHES_V1_SELECTOR, as_bytes

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path("build/layout001_english/X-Men vs. Street Fighter (Japan) (3M).cue")
STATES = Path("local/layout001/session/states")
POINTER = 0x060F2490


def upgrade(agent: Agent, restore: bool = False) -> None:
    v1: dict[int, int] = {}
    for address, text in PATCHES_V1_SELECTOR:
        for i, value in enumerate(as_bytes(text)):
            v1[address + i] = value
    for address, old, new in PATCHES:
        original = as_bytes(old)
        size = len(original)
        found = agent.bus_read(address, size)
        as_v1 = bytes(v1.get(address + i, original[i]) for i in range(size))
        if found not in {original, as_v1, as_bytes(new)}:
            raise RuntimeError(f"{address:#x}: unexpected {found.hex()}")
        agent.bus_write(address, original if restore else as_bytes(new))
    # 0x0606668E held version 1's branch; both versions 2 and orig need the store.
    if agent.bus_read(0x0606668E, 2) == bytes.fromhex("AFEC"):
        agent.bus_write(0x0606668E, bytes.fromhex("C101"))


def main(out: Path, specs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
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
            for spec in specs:
                name, state, frames, mode = spec.split(":")
                agent.loadstate((STATES / f"{state}.mcs").resolve())
                agent.pause()
                if mode in ("v2", "orig"):
                    upgrade(agent, restore=mode == "orig")
                agent.frames(int(frames))
                agent.wait_halted(60.0)
                agent.screenshot((out / f"{name}.png").resolve())
                (out / f"{name}-vdp1.bin").write_bytes(
                    agent.read("vdp1vram", 0, 0x80000)
                )
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                result[name] = {
                    "state": state,
                    "mode": mode,
                    "pointer": f"{pointer:#010x}",
                    "codes_at_quote": agent.bus_read(pointer, 100).hex(),
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {k: v["pointer"] for k, v in result.items() if isinstance(v, dict)},
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))
