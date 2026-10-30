r"""EXP-0049: dump the screen, VRAM and work RAM at save states.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/dump_screen.py \
        CUE OUT STATE [STATE ...]

Each STATE is loaded into a silent Mednafen on CUE, run one frame, paused,
and written to
``OUT/<state stem>/``:

- ``screen.png``;
- ``vdp1.bin`` (VDP1 VRAM, 512 KiB) and ``vdp2.bin`` (VDP2 VRAM, 512 KiB);
- ``wram_l.bin`` (``0x00200000``-``0x002FFFFF``) and ``wram_h.bin``
  (``0x06000000``-``0x060FFFFF``), read over the bus while paused;
- ``cart.bin``, the 4 MB RAM cartridge (``0x22400000``-``0x227FFFFF``),
  read through Mednafen's ``physical`` space (address ``0x02400000``).
  ``physical_check`` in ``OUT/<state>/checks.txt`` compares that space's
  view of WRAM-H with ``workramh``.
  Its rationale (AGENTS.md, artifact discipline): the life-bar name cells
  reached VDP1 VRAM with no CPU write and from no work-RAM copy
  (`EXP-0049`), so a DMA source outside work RAM was looked for.

The dumps are read live over the agent, not extracted from the state file,
so they are what the game holds at that paused instant. Outputs go to the
ignored OUT.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.mednafen.route import BINARY

WRAM_L, WRAM_H, WRAM_SIZE = 0x00200000, 0x06000000, 0x100000
VRAM_SIZE = 0x80000
CART, CART_SIZE = 0x02400000, 0x400000  # physical-space address of 0x22400000


def main(cue: Path, out: Path, states: list[Path]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
        "MEDNAFEN_ALLOWMULTI": "1",
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=30.0)
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
            for state in states:
                target = out / state.stem
                target.mkdir()
                agent.loadstate(state.resolve())
                agent.pause()
                # one frame, so that the screenshot is drawn from this state
                agent.frames(1)
                agent.wait_halted(30.0)
                agent.screenshot((target / "screen.png").resolve())
                (target / "vdp1.bin").write_bytes(agent.read("vdp1vram", 0, VRAM_SIZE))
                (target / "vdp2.bin").write_bytes(agent.read("vdp2vram", 0, VRAM_SIZE))
                (target / "wram_l.bin").write_bytes(agent.bus_read(WRAM_L, WRAM_SIZE))
                (target / "wram_h.bin").write_bytes(agent.bus_read(WRAM_H, WRAM_SIZE))
                (target / "cart.bin").write_bytes(
                    agent.read("physical", CART, CART_SIZE)
                )
                same = agent.read("physical", WRAM_H, 0x1000) == agent.read(
                    "workramh", 0, 0x1000
                )
                (target / "checks.txt").write_text(f"physical_check {same}\n")
                print(f"dumped {state.name}", flush=True)
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]])
    )
