"""EXP-0035: Nash's ending under the version-3 patch and under the global English words.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0035/ending_modes.py OUT [STATE]

STATE defaults to `EXP-0034`'s replay checkpoint ``f00220064.mcs`` (untouched
source image, no input). Three runs, each loaded fresh from STATE and paused,
then run to each page frame in ``TARGETS``:

- **control:** nothing written;
- **v3:** the version-3 patch for the roster (`tools.disc.english_mode.patches_v3`,
  slots 0-17) written over the code in RAM, after checking that every site
  holds its original bytes. The only difference from control is the patch;
- **english:** the size and language words (``0x060F5478``, ``0x060F547A``)
  set to 2, as `EXP-0023` ``english_mode.py`` did for win quotes.

At STATE it also reads the type-4 selector's two base lists (``LISTS``,
filled at run time) and the two words. At each page it saves a screenshot,
VDP1 VRAM, the quote pointer and the 100 bytes there. Outputs go to the
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
from tools.disc.english_mode import as_bytes, patches_v3
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00220064.mcs")
TARGETS = [220654, 220887, 221112, 221342, 221690, 222037]
POINTER = 0x060F2490
SIZE, LANGUAGE = 0x060F5478, 0x060F547A
# the type-4 selector's lists for language 0 and 2 (its table at 0x06066910)
LISTS = {"language_0": 0x060854F8, "language_2": 0x06085544}
SLOTS = list(range(18))


def main(out: Path, state: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    start = int(state.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(state)}
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
            for run in ("control", "v3", "english"):
                agent.loadstate(state.resolve())
                agent.pause()
                entry: dict[str, object] = {}
                if run == "control":
                    result["lists"] = {
                        name: [
                            f"0x{agent.bus_read(a + 4 * i, 4).hex()}" for i in range(19)
                        ]
                        for name, a in LISTS.items()
                    }
                    result["words"] = agent.bus_read(SIZE, 4).hex()
                if run == "v3":
                    for address, old, new in patches_v3(SLOTS):
                        original, data = as_bytes(old), as_bytes(new)
                        found = agent.bus_read(address, len(original))
                        if found != original:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, data)
                    entry["patched_sites"] = len(patches_v3(SLOTS))
                if run == "english":
                    agent.bus_write(SIZE, bytes.fromhex("00020002"))
                    entry["words_written"] = agent.bus_read(SIZE, 4).hex()
                now = start
                pages = {}
                for target in TARGETS:
                    agent.frames(target - now)
                    agent.wait_halted(180.0)
                    now = target
                    stem = f"{run}-f{target:08d}"
                    shot = (out / f"{stem}.png").resolve()
                    agent.screenshot(shot)
                    vdp1 = agent.read("vdp1vram", 0, 0x80000)
                    (out / f"{stem}-vdp1.bin").write_bytes(vdp1)
                    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                    try:
                        codes = agent.bus_read(pointer, 100).hex()
                    except AgentError:
                        codes = "not work RAM"
                    pages[str(target)] = {
                        "pointer": f"{pointer:#010x}",
                        "codes_at_quote": codes,
                        "words": agent.bus_read(SIZE, 4).hex(),
                        "screenshot": hashlib.sha256(shot.read_bytes()).hexdigest(),
                    }
                entry["pages"] = pages
                result[run] = entry
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    state = Path(sys.argv[2]) if len(sys.argv) > 2 else STATE
    raise SystemExit(main(Path(sys.argv[1]), state))
