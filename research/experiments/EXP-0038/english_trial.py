"""EXP-0038: Nash's ending with the English path turned on for the ending only, in RAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/english_trial.py \\
        OUT [japanese-script]

From ``f00220064.mcs`` (`EXP-0034`, after the partner fight's last hit), on
the untouched image with no input, two runs:

- **control:** nothing written;
- **english:** the ending's own language reads return 2, with the global
  size and language words left at 0:
  - the scene-script reader in ``MCED`` (``0x060D4738``);
  - the type-4 selector (``0x060668C4``);
  - the renderer's six reads of the two words (``RENDERER``, the sites
    version 3 patches for win quotes, `EXP-0023`).

  Each ``mov.w @(r0,r11),r0`` (``00BD``) becomes ``mov #2,r0`` (``E002``).
  The selector's language-2 list pointer (the words at ``0x06066914``) is
  pointed at a 19-long list at ``LIST``. Its slot-16 entry points at
  ``RECORDS``, where the six arcade English records of slot 16
  (``0x18D0AE`` + 100k, from the program image) are written. ``LIST`` and
  ``RECORDS`` lie in WRAM-L ``0x00259050``-``0x0025E3DF``, which is zero at
  the checkpoint, at page 1 and after the credits (``dump_ram.py``).

With ``japanese-script`` (`LAYOUT-002` option (b)), the scene-script reader
``0x060D4738`` is left alone, so the Japanese script (scenes, page lengths,
labels, pictures) runs with the English records in the English grid.

Every original byte is checked before it is written. Each run screenshots
every ``STEP`` frames from ``FIRST`` to ``LAST``, with the quote pointer, and
saves VDP1 VRAM where the pointer changes. The scratch region is read back at
the end to show that nothing else wrote it. Outputs go to the ignored OUT.
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
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00220064.mcs")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
EN_RECORDS, EN_SIZE, COUNT, SLOT = 0x18D0AE, 100, 6, 16
READ, TWO = bytes.fromhex("00BD"), bytes.fromhex("E002")
SCRIPT_READ, SELECTOR_READ = 0x060D4738, 0x060668C4
RENDERER = [0x0606696A, 0x0606699E, 0x060669CC, 0x060669F6, 0x06066A10, 0x06066A3A]
LIST_POINTER = 0x06066914  # high, low words of the language-2 list address
OLD_LIST = bytes.fromhex("06085544")
LIST, RECORDS = 0x00259100, 0x00259200
SCRATCH = (0x00259050, 0x0025E3E0)
POINTER = 0x060F2490
FIRST, LAST, STEP = 220500, 223200, 30


def changes(program: bytes, script: bool = True) -> list[tuple[int, bytes, bytes]]:
    english = program[EN_RECORDS : EN_RECORDS + EN_SIZE * COUNT]
    table = bytearray(4 * 19)
    table[4 * SLOT : 4 * SLOT + 4] = RECORDS.to_bytes(4, "big")
    reads = [SCRIPT_READ] if script else []
    edits = [(a, READ, TWO) for a in (*reads, SELECTOR_READ, *RENDERER)]
    edits.append((LIST_POINTER, OLD_LIST, LIST.to_bytes(4, "big")))
    edits.append((LIST, bytes(len(table)), bytes(table)))
    edits.append((RECORDS, bytes(len(english)), english))
    return edits


def main(out: Path, script: bool = True) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    program = PROGRAM.read_bytes()
    start = int(STATE.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "english_script": script}
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
            for run in ("control", "english"):
                (out / run).mkdir()
                agent.loadstate(STATE.resolve())
                agent.pause()
                written = []
                if run == "english":
                    for address, old, new in changes(program, script):
                        found = agent.bus_read(address, len(old))
                        if found != old:
                            raise RuntimeError(f"{address:#x}: {found.hex()}")
                        agent.bus_write(address, new)
                        written.append(
                            {"address": f"{address:#010x}", "length": len(new)}
                        )
                expected = agent.bus_read(SCRATCH[0], SCRATCH[1] - SCRATCH[0])
                frames: list[dict[str, object]] = []
                now, last_pointer = start, None
                for target in range(FIRST, LAST + 1, STEP):
                    agent.frames(target - now)
                    agent.wait_halted(120.0)
                    now = target
                    agent.screenshot((out / run / f"f{target:08d}.png").resolve())
                    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                    if pointer != last_pointer:
                        (out / run / f"f{target:08d}-vdp1.bin").write_bytes(
                            agent.read("vdp1vram", 0, 0x80000)
                        )
                        last_pointer = pointer
                    frames.append({"frame": target, "pointer": f"{pointer:#010x}"})
                after = agent.bus_read(SCRATCH[0], SCRATCH[1] - SCRATCH[0])
                result[run] = {
                    "written": written,
                    "scratch_unchanged": after == expected,
                    "words_at_end": agent.bus_read(0x060F5478, 4).hex(),
                    "frames": frames,
                }
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    for run in ("control", "english"):
        entry = result[run]
        assert isinstance(entry, dict)
        changes_seen = []
        last = None
        for f in entry["frames"]:
            if f["pointer"] != last:
                changes_seen.append((f["frame"], f["pointer"]))
                last = f["pointer"]
        print(run, entry["scratch_unchanged"], entry["words_at_end"], changes_seen)
    return 0


if __name__ == "__main__":
    script = not (len(sys.argv) > 2 and sys.argv[2] == "japanese-script")
    raise SystemExit(main(Path(sys.argv[1]), script))
