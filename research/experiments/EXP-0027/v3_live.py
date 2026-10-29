"""EXP-0027: run the version-3 English-mode patch in live RAM for chosen slots.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/v3_live.py OUT RUN...

Each RUN is ``NAME:CASE:SLOTS:DRAW``:

* ``CASE`` picks a checkpoint:
  - ``ryu``: `pre_ko` of `EXP-0013` (Ryu speaks);
  - ``ken``: `pre_ko` of `EXP-0025` (Ken speaks);
  - ``storm``: state 19207 of the `EXP-0023` play session (Storm speaks).
    Its RAM holds version-1 code, so every patch site is first restored to the
    original bytes.
* ``SLOTS`` is ``orig`` (no patch: the unpatched game), or a ``+``-separated
  slot list (``9+10``). The list gives the English slots of
  `tools.disc.english_mode.patches_v3`, and the run writes those bytes. For
  ``ryu`` and ``ken`` it also writes the character's 8 English records (from
  the ignored ``local/ref003/xmvsfu-68k.bin``, recompiled by
  `tools.text.caption`, which must reproduce them) over the start of its
  table. That table is written whether or not its slot is in the list.
* ``DRAW`` is ``-`` (the state's own draw) or a draw 0-15 for ``ryu``,
  steered through the RNG seed with `EXP-0024`'s seeds.

``ryu`` and ``ken`` reload until the paused seed reads their state's value,
so every run starts at the same RNG position. Each run saves a screenshot,
VDP1 VRAM, the record pointer, the 100 bytes it points at, the index byte and
the task flag. Outputs go to the ignored OUT.
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
from tools.disc.english_mode import FLAG, as_bytes, patches_v3
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.text.caption import compile_record, decode_record

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
SOURCE = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
)
# The play-session states were saved on the version-1 image (since deleted);
# nothing is read from disc between the state and the quote (EXP-0023).
SESSION = Path("build/re003_ryu_english/X-Men vs. Street Fighter (Japan) (3M).cue")
SEED, TASK, POINTER = 0x060F545A, 0x060F8AC0, 0x060F2490
INDEX = TASK + 38
CASES: dict[str, dict[str, object]] = {
    "ryu": {
        "state": "local/checkpoints/dbg003/f00009769.mcs",
        "seed": 8520,
        "frames": 660,
        "table": 0x0024F5D8,
        "english": 0x188DE2,
    },
    "ken": {
        "state": "local/checkpoints/re004/f00007684.mcs",
        "seed": 9501,
        "frames": 700,
        "table": 0x0024FA4C,
        "english": 0x189166,
    },
    "storm": {"state": "local/layout001/session/states/f00019207.mcs", "frames": 240},
}
# draw -> seed from Ryu's pre_ko (EXP-0024)
RYU_SEEDS = [2, 12, 15, 8, 21, 33, 17, 27029, 5, 26, 1, 13, 35, 19, 3, 6]
# version-1 bytes found in the play-session RAM (EXP-0023 english_patch.py)
V1 = [
    (0x06066668, "C501 C907 C003 E15C 316C E202 2120 EEFF A00B 0018 0009"),
    (0x06066682, "0009 0606 6718"),
    (0x0606668E, "AFEC 0009"),
]
FIXED_STORE = (0x0606668E, "C101")  # the fixed path's store, overwritten by v1


def english_table(program: bytes, base: int) -> bytes:
    out = b""
    for k in range(8):
        source = program[base + 100 * k : base + 100 * k + 100]
        if compile_record(decode_record(source)) != source:
            raise RuntimeError(f"English record {k} does not recompile")
        out += source
    return out


def restore(agent: Agent) -> None:
    """Return every v3 site (and the fixed path's store) to the original bytes."""
    v1: dict[int, int] = {}
    for address, text in V1:
        for i, value in enumerate(as_bytes(text)):
            v1[address + i] = value
    for address, old, new in patches_v3([]):
        original = as_bytes(old)
        found = agent.bus_read(address, len(original))
        as_v1 = bytes(v1.get(address + i, b) for i, b in enumerate(original))
        if found not in {original, as_v1, as_bytes(new)}:
            raise RuntimeError(f"{address:#x}: unexpected {found.hex()}")
        agent.bus_write(address, original)
    address, store = FIXED_STORE
    found = agent.bus_read(address, 2)
    if found not in {as_bytes(store), bytes.fromhex("AFEC")}:
        raise RuntimeError(f"{address:#x}: unexpected {found.hex()}")
    agent.bus_write(address, as_bytes(store))


def write_v3(agent: Agent, slots: list[int]) -> None:
    for address, old, new in patches_v3(slots):
        found = agent.bus_read(address, len(as_bytes(old)))
        if found != as_bytes(old):
            raise RuntimeError(f"{address:#x}: found {found.hex()}, not original")
        agent.bus_write(address, as_bytes(new))


def run(agent: Agent, out: Path, spec: str, program: bytes) -> dict[str, object]:
    name, case_name, slots_text, draw = spec.split(":")
    case = CASES[case_name]
    state = Path(str(case["state"])).resolve()
    for _ in range(20):
        agent.loadstate(state)
        agent.pause()
        if "seed" not in case:
            break
        if int.from_bytes(agent.bus_read(SEED, 2), "big") == case["seed"]:
            break
        agent.run()
    else:
        raise RuntimeError(f"{case_name}: never paused at seed {case['seed']}")
    entry: dict[str, object] = {"case": case_name, "slots": slots_text, "draw": draw}
    if case_name == "storm":
        restore(agent)
    if slots_text != "orig":
        slots = [int(s) for s in slots_text.split("+")]
        write_v3(agent, slots)
        if "table" in case:
            table = int(str(case["table"]))
            english = english_table(program, int(str(case["english"])))
            agent.bus_write(table, english)
    if draw != "-":
        agent.bus_write(SEED, RYU_SEEDS[int(draw)].to_bytes(2, "big"))
    agent.frames(int(str(case["frames"])))
    agent.wait_halted(120.0)
    agent.screenshot((out / f"{name}.png").resolve())
    (out / f"{name}-vdp1.bin").write_bytes(agent.read("vdp1vram", 0, 0x80000))
    pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
    entry["pointer"] = f"{pointer:#010x}"
    entry["codes_at_quote"] = agent.bus_read(pointer, 100).hex()
    entry["index"] = agent.bus_read(INDEX, 1)[0]
    entry["flag"] = agent.bus_read(TASK + FLAG, 1)[0]
    agent.run()
    return entry


def main(out: Path, specs: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    program = PROGRAM.read_bytes()
    image = SESSION if any(":storm:" in s for s in specs) else SOURCE
    if image == SESSION and any(":storm:" not in s for s in specs):
        raise SystemExit("run storm cases separately (they use the session image)")
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"image": str(image)}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(image)], env=env, stdout=log, stderr=subprocess.STDOUT
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
                result[spec.split(":")[0]] = run(agent, out, spec, program)
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        k: (v["pointer"], v["index"], v["flag"])
        for k, v in result.items()
        if isinstance(v, dict)
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))
