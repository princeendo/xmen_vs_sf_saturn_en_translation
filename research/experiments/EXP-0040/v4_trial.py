"""EXP-0040: the version-4 patch (English endings per slot) on Nash's ending, in RAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0040/v4_trial.py OUT

From ``f00220064.mcs`` (`EXP-0034`, after the partner fight's last hit), on
the untouched image with no input, three runs:

- **control:** nothing written;
- **v4_off:** the version-3 code for the roster (`patches_v3`, slots 0-17)
  plus the version-4 selector (``V4_SELECTOR``, ``V4_LITERALS``). No slot is
  marked for an English ending. Prediction: every screenshot equals control;
- **v4_on:** ``v4_off`` plus three data changes:
  - slot 16's English-ending bit (``ENDING_BIT``) in the fixed-index table's
    low byte;
  - Nash's ``MCED`` script header word for language 0 → his English script
    (``MCED_HEADER``);
  - the six arcade English records at quote table + 800 (``RECORDS``).

  Prediction: every screenshot equals `EXP-0038` ``trial1/english`` at the
  same frame.

Every original byte is checked before it is written. Each run screenshots
every 30 frames from 220,500 to 223,200 and records the quote pointer and
the renderer task's flag. Outputs go to the ignored OUT.
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
from tools.disc.english_mode import FIXED_TABLE, as_bytes, patches_v3
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
STATE = Path("local/checkpoints/end001/f00220064.mcs")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
SLOTS = list(range(18))

# Type-4 (ending) selector, 0x060668C2-0x060668EF, replacing the language
# read, the language table lookup and the word-by-word list read:
#   060668C2 D712  mov.l @(0x0606690C),r7   ; language-0 list 0x060854F8
#   060668C4 D112  mov.l @(0x06066910),r1   ; FIXED_TABLE + 1 (low bytes)
#   060668C6 C503  mov.w @(6,gbr),r0       ; slot x 2
#   060668C8 021C  mov.b @(r0,r1),r2       ; fixed-table low byte (sign-extended)
#   060668CA 300C  add r0,r0               ; slot x 4
#   060668CC 007E  mov.l @(r0,r7),r0       ; the slot's ending pointer
#   060668CE 4211  cmp/pz r2               ; bit 7 clear: Japanese ending
#   060668D0 8905  bt 0x060668DE
#   060668D2 911F  mov.w @(0x06066914),r1  ; -0x1A0
#   060668D4 301C  add r1,r0               ; quote table + 800
#   060668D6 E15C  mov #0x5C,r1            ; FLAG
#   060668D8 316C  add r6,r1               ; r6 = task
#   060668DA E202  mov #2,r2
#   060668DC 2120  mov.b r2,@r1            ; task + FLAG = 2 (English grid)
#   060668DE-EE    nop x 9
# 0x060668F0 onward (store the pointer at task + 0x34) is unchanged.
V4_SELECTOR = (
    0x060668C2,
    "90D7 00BD C101 C501 300C C101 D10F C501 021D 70FE 011D 6029 201D 6703"
    " C503 300C C103 C503 017D 7002 027D 6029 201D",
    "D712 D112 C503 021C 300C 007E 4211 8905 911F 301C E15C 316C E202 2120"
    " 0009 0009 0009 0009 0009 0009 0009 0009 0009",
)
# The selector's old literal and language table (only it referenced them):
# 0x0606690C list 0x060854F8, 0x06066910 FIXED_TABLE + 1, 0x06066914 -0x1A0.
V4_LITERALS = (
    0x0606690C,
    "06066912 060854F8 06085544",
    "060854F8 060666E1 FE600000",
)
V3_SELECTOR_READ = (0x060668C4, "00BD", "E000")  # replaced by V4_SELECTOR
ENDING_BIT = 0x80
SLOT = 16
MCED_HEADER = (0x060D4CF0, "0008", "0038")  # Nash's script, language-0 offset
TABLE_RAM = 0x0024D000 + 0x2A00  # MC10 quote table in WRAM-L
RECORDS = TABLE_RAM + 800
EN_RECORDS, EN_SIZE, COUNT = 0x18D0AE, 100, 6
POINTER, FIRST, LAST, STEP = 0x060F2490, 220500, 223200, 30
TRIAL1 = Path("local/end005/trial1/english")


def v4_code() -> list[tuple[int, str, str]]:
    v3 = [p for p in patches_v3(SLOTS) if p != V3_SELECTOR_READ]
    return [*v3, V4_SELECTOR, V4_LITERALS]


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    program = PROGRAM.read_bytes()
    english = program[EN_RECORDS : EN_RECORDS + EN_SIZE * COUNT]
    start = int(STATE.stem[1:])
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE)}
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
            for run in ("control", "v4_off", "v4_on"):
                (out / run).mkdir()
                agent.loadstate(STATE.resolve())
                agent.pause()
                edits: list[tuple[int, bytes, bytes]] = []
                if run != "control":
                    edits += [(a, as_bytes(o), as_bytes(n)) for a, o, n in v4_code()]
                if run == "v4_on":
                    bit_at = FIXED_TABLE + 2 * SLOT + 1
                    low = agent.bus_read(bit_at, 1)
                    edits.append((bit_at, low, bytes([low[0] | ENDING_BIT])))
                    a, o, n = MCED_HEADER
                    edits.append((a, as_bytes(o), as_bytes(n)))
                    edits.append(
                        (RECORDS, agent.bus_read(RECORDS, len(english)), english)
                    )
                for address, old, new in edits:
                    found = agent.bus_read(address, len(old))
                    if found != old:
                        raise RuntimeError(f"{address:#x}: {found.hex()}")
                    agent.bus_write(address, new)
                frames = []
                now = start
                for target in range(FIRST, LAST + 1, STEP):
                    agent.frames(target - now)
                    agent.wait_halted(120.0)
                    now = target
                    shot = (out / run / f"f{target:08d}.png").resolve()
                    agent.screenshot(shot)
                    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                    frames.append(
                        {
                            "frame": target,
                            "pointer": f"{pointer:#010x}",
                            "sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                        }
                    )
                result[run] = {"edits": len(edits), "frames": frames}
                agent.run()
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    control = result["control"]["frames"]  # type: ignore[index]
    off = result["v4_off"]["frames"]  # type: ignore[index]
    on = result["v4_on"]["frames"]  # type: ignore[index]
    result["off_equals_control"] = [
        a["frame"]
        for a, b in zip(control, off, strict=True)
        if a["sha256"] != b["sha256"]
    ]
    trial1 = [
        hashlib.sha256((TRIAL1 / f"f{f['frame']:08d}.png").read_bytes()).hexdigest()
        for f in on
    ]
    result["on_equals_trial1"] = [
        f["frame"] for f, t in zip(on, trial1, strict=True) if f["sha256"] != t
    ]
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                "frames": len(on),
                "v4_off_frames_differing_from_control": result["off_equals_control"],
                "v4_on_frames_differing_from_exp0038": result["on_equals_trial1"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
