"""Reach any roster character's ending on the Saturn with no play.

Run from the repository root:

    ./invenv.sh python -m tools.mednafen.route CUE OUT --first SLOT --second SLOT
        [--policy {first,second,tag,cpu_final}] [--mmpack BUILT_MMPACK]
        [--area FIRST:LAST] [--frames N]

Promoted from `research/experiments/EXP-0041/saturn_route.py` (this
repository, commit ``f8526c0``) for `END-013`, and generalized:

- **Picks.** From the select state ``STATE`` (untouched image, after Start,
  cursor on Ken), the first pick is reached with ``grid_moves`` from Ken and
  confirmed with button A. The second cursor starts on Cyclops
  (`EXP-0041`), so the second pick uses moves from there. Keys go through
  System Events with Mednafen brought to the front (pad A on K, directions
  on I, M, J and L; the ``local/mednafen_pick`` home). A key that cannot be
  sent is retried, and the run stops if it still cannot be sent.
- **Gouki** (slot 15) is not on the grid, and no cursor move to his cell is
  known. For ``--first 15`` the run starts from ``GOUKI_STATE`` instead.
  That state is the second pick, with Gouki already picked first
  (`EXP-0045`), so only the second pick is made. Its RAM holds the untouched
  ``MC0F.SHP``. When CUE's ``MC0F`` differs, every differing decoded byte
  is written into the first buffer after checking the original, as for the
  code below.
- **Code.** The select state already holds the untouched ``MMPACK.PCA``
  code. With ``--mmpack``, every byte where the built file's decoded
  streams differ is written into RAM first, after checking the original
  bytes (`EXP-0041`).
- **Load check.** After both picks, the first member's buffer
  (``0x0024D000``) and the second's (``0x060B0000``) are compared with
  their MC files from CUE's own track, plus the `EXP-0025` fix-ups (file
  value + buffer + ``0x40``).
- **Fights.** The four fighter blocks (``BLOCKS``) hold each fighter's
  character at + ``0x23`` (slot x 2) and vitality at + ``0x10``
  (`EXP-0045`). Every ``STEP`` frames, ``Route.targets`` decides which
  vitality words to set to 0, from the blocks' characters:
  - ``first``: always the CPU side, so the first pick finishes every
    fight;
  - ``second``: as ``first``, except that once Apocalypse (slot 8) is on
    the CPU side, the first pick's own block is set to 0 until the second
    pick is the active fighter (block ``PLAYER[0]``, `EXP-0045`). Only then
    is the CPU side set to 0 again, so the second pick finishes the boss.
    The partner only counts once the first pick has been seen active in the
    boss phase: during Apocalypse's dialogue the active block can already
    hold the partner, before the game puts the first pick back in for the
    fight. ``KNOCKOUT_STEPS`` caps the wait. Three earlier versions failed:
    - a single write (`EXP-0045` runs ``r2``, ``r5``, ``r7``);
    - a fixed 900 frames from Apocalypse's arrival, which ran out during his
      pre-fight dialogue (runs ``r2b``, ``r5b``, ``r7b``);
    - "until the partner is active", which was already true in that dialogue
      (runs ``r2c``, ``r5c``, ``r7c``);
  - ``tag``: as ``first``, except in the boss fight. Once the first pick is
    seen active, nothing is zeroed, and the pad's Z + C chord (the tag) is
    sent every ``TAG_EVERY`` steps until the second pick is the active
    fighter. Then the CPU side is zeroed again;
  - ``cpu_final``: as ``first``, except in the partner fight (the CPU side
    holds a team member, after the boss), where the player's side is set
    to 0.
- **Logs.** Phase changes, the player side's characters at the partner
  fight, every change of the quote pointer ``0x060F2490``, and a screenshot
  every ``SHOT_EVERY`` frames. With ``--area``, a read-breakpoint log
  (`EXP-0041`).

Outputs go to OUT (an ignored path): ``result.json``, ``shots/``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from tools.disc.patch_image import find_entry
from tools.disc.prs import decompress_entries, decompress_file, split_header
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, apply_settings, configure
from tools.mednafen.hotkeys import activate, frontmost_pid, osascript

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
STATE = Path("local/checkpoints/re004/f00002973.mcs")
GOUKI, GOUKI_STATE = 15, Path("local/re004/session/states/f00009348.mcs")
PICK_HOME = Path("local/mednafen_pick")
SOURCE_TRACK = Path(
    "local/disc_images/xmvsf_saturn_jp_3m/"
    "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
)
# Saturn select grid, rows top to bottom (EXP-0025, EXP-0032)
GRID = (
    (7, 6, 12, 14),
    (5, 2, 11, 13),
    (4, 3, 17, 16),
    (0, 1, 9, 10),
)
FIRST_START, SECOND_START = 10, 1  # Ken; Cyclops
KEYS = {
    "u": ("i", 12),
    "d": ("m", 16),
    "l": ("j", 13),
    "r": ("l", 15),
    "a": ("k", 14),
    "z": ("o", 18),
    "c": ("u", 24),
}
PLAYER, CPU = (0x060F4200, 0x060F4A00), (0x060F4600, 0x060F4E00)
BLOCKS = PLAYER + CPU
CHAR, VITALITY = 0x23, 0x10
APOCALYPSE = 8
FIRST_BUFFER, SECOND_BUFFER = 0x0024D000, 0x060B0000
POINTER = 0x060F2490
STEP, SHOT_EVERY, PRESS_GAP = 20, 120, 1.0
KNOCKOUT_STEPS = 600  # at most 12,000 frames of knocking out the first pick
POLICIES = ("first", "second", "tag", "cpu_final")
TAG_EVERY = 15  # steps between tag chords (300 frames)


def cell(slot: int) -> tuple[int, int]:
    for row, cells in enumerate(GRID):
        if slot in cells:
            return row, cells.index(slot)
    raise ValueError(f"slot {slot} is not on the select grid")


def grid_moves(target: int, start: int) -> str:
    """Cursor moves from ``start`` to ``target``: vertical first, then horizontal."""
    (r0, c0), (r1, c1) = cell(start), cell(target)
    vertical = "u" * (r0 - r1) if r1 < r0 else "d" * (r1 - r0)
    horizontal = "l" * (c0 - c1) if c1 < c0 else "r" * (c1 - c0)
    return vertical + horizontal


@dataclass
class Route:
    """Which vitality words to zero, given each block's character."""

    first: int
    second: int
    policy: str
    phase: str = "stages"
    first_out: bool = False
    knockout_steps: int = 0
    seen_first_active: bool = False
    tag_request: bool = False
    tag_steps: int = 0
    events: list[tuple[str, dict[int, int]]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise ValueError(f"unknown policy {self.policy}")

    def targets(self, chars: dict[int, int], vitality: dict[int, int]) -> list[int]:
        team = {2 * self.first, 2 * self.second}
        cpu = {chars[b] for b in CPU}
        if self.phase == "stages" and 2 * APOCALYPSE in cpu:
            self.phase = "boss"
            self.events.append(("boss", dict(chars)))
        elif self.phase == "boss" and cpu & team:
            self.phase = "partner"
            self.events.append(("partner", dict(chars)))
        if self.policy == "second" and self.phase == "boss" and not self.first_out:
            mine = [b for b in PLAYER if chars[b] == 2 * self.first]
            if chars[PLAYER[0]] == 2 * self.first:
                self.seen_first_active = True
            partner_active = chars[PLAYER[0]] == 2 * self.second
            done = self.seen_first_active and partner_active
            if not done and mine and self.knockout_steps < KNOCKOUT_STEPS:
                self.knockout_steps += 1
                return mine
            self.first_out = True
            self.events.append(("first_out", dict(chars)))
        self.tag_request = False
        if self.policy == "tag" and self.phase == "boss" and not self.first_out:
            if chars[PLAYER[0]] == 2 * self.first:
                self.seen_first_active = True
            if self.seen_first_active and chars[PLAYER[0]] == 2 * self.second:
                self.first_out = True
                self.events.append(("tagged", dict(chars)))
            elif self.knockout_steps < KNOCKOUT_STEPS:
                self.knockout_steps += 1
                if self.seen_first_active:
                    self.tag_request = self.tag_steps % TAG_EVERY == 0
                    self.tag_steps += 1
                return []
        if self.policy == "cpu_final" and self.phase == "partner":
            return list(PLAYER)
        return list(CPU)


def pick_home() -> Path:
    configure()
    PICK_HOME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(QUIET_HOME / "mednafen.cfg", PICK_HOME / "mednafen.cfg")
    firmware = PICK_HOME / "firmware"
    if not firmware.exists():
        firmware.symlink_to(Path("..") / "mednafen" / "firmware")
    names = {
        "u": "up",
        "d": "down",
        "l": "left",
        "r": "right",
        "a": "a",
        "z": "z",
        "c": "c",
    }
    apply_settings(
        PICK_HOME / "mednafen.cfg",
        {
            f"ss.input.port1.gamepad.{names[k]}": f"keyboard 0x0 {code}"
            for k, (_, code) in KEYS.items()
        },
    )
    return PICK_HOME


def send(pid: int, moves: str, hold: float = 0.1) -> None:
    """Press each move key in turn with Mednafen frontmost (retried, never blind)."""
    for attempt in range(5):
        previous = frontmost_pid()
        activate(pid)
        time.sleep(0.4)
        if frontmost_pid() == pid:
            break
        if attempt == 4:
            raise RuntimeError("Mednafen is not frontmost; key not sent")
        time.sleep(1.0)
    script = 'tell application "System Events"\n'
    for move in moves:
        key = KEYS[move][0]
        script += f'key down "{key}"\ndelay {hold}\nkey up "{key}"\ndelay 0.35\n'
    osascript(script + "end tell")
    if previous != pid:
        activate(previous)


def send_chord(pid: int, moves: str, hold: float = 0.15) -> None:
    """Hold the keys for ``moves`` together, with Mednafen frontmost."""
    previous = frontmost_pid()
    activate(pid)
    time.sleep(0.3)
    if frontmost_pid() != pid:
        return  # skipped; the next request tries again
    keys = [KEYS[m][0] for m in moves]
    script = 'tell application "System Events"\n'
    script += "".join(f'key down "{k}"\n' for k in keys)
    script += f"delay {hold}\n" + "".join(f'key up "{k}"\n' for k in keys)
    osascript(script + "end tell")
    if previous != pid:
        activate(previous)


def track_file(track: Path, name: str) -> bytes:
    lsn, size = find_entry(track, name)
    data = bytearray()
    with track.open("rb") as stream:
        for index in range(lsn, lsn + (size + 2047) // 2048):
            stream.seek(index * 2352 + 16)
            data += stream.read(2048)
    return bytes(data[:size])


def fixups_match(decoded: bytes, ram: bytes, delta: int) -> bool:
    """RAM equals ``decoded``, except longs holding value + ``delta`` (`EXP-0025`)."""
    i = 0
    while i < len(decoded):
        if ram[i] != decoded[i]:
            start = i - (i % 2)
            for at in (start, start - 2):
                if at < 0 or at + 4 > len(decoded):
                    continue
                value = (
                    int.from_bytes(decoded[at : at + 4], "big") + delta
                ) & 0xFFFFFFFF
                if value.to_bytes(4, "big") == ram[at : at + 4]:
                    i = at + 4
                    break
            else:
                return False
            continue
        i += 1
    return True


def code_ranges(original: bytes, built: bytes) -> list[tuple[int, bytes, bytes]]:
    """(RAM address, original, built) for each run of differing decoded MMPACK bytes."""
    _, entries = split_header(original)
    (_, first_size), (second_dest, _) = entries
    base = second_dest - first_size
    _, old, _ = decompress_entries(original)
    _, new, _ = decompress_entries(built)
    if len(old) != len(new):
        raise ValueError("decoded MMPACK sizes differ")
    return [(base + offset, a, b) for offset, a, b in byte_ranges(old, new)]


def byte_ranges(old: bytes, new: bytes) -> list[tuple[int, bytes, bytes]]:
    """(offset, old, new) for each run of differing bytes (equal lengths)."""
    if len(old) != len(new):
        raise ValueError("lengths differ")
    ranges, start = [], None
    for i in range(len(old) + 1):
        same = i == len(old) or old[i] == new[i]
        if not same and start is None:
            start = i
        if same and start is not None:
            ranges.append((start, old[start:i], new[start:i]))
            start = None
    return ranges


def parse_hit(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def run(
    cue: Path,
    out: Path,
    first: int,
    second: int,
    policy: str = "first",
    mmpack: Path | None = None,
    area: tuple[int, int] | None = None,
    frames: int = 30000,
) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=False)
    (out / "shots").mkdir()
    route = Route(first, second, policy)
    track = cue.parent / f"{cue.stem} (Track 01).bin"
    roster = {
        m["slot"]: m
        for m in json.loads(Path("data/text/m5_roster.json").read_text())["roster"]
    }
    files = {
        slot: decompress_file(track_file(track, roster[slot]["mc_file"]))[0]
        for slot in (first, second)
    }
    home = pick_home()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {
        "cue": str(cue),
        "first": first,
        "second": second,
        "policy": policy,
        "first_moves": "" if first == GOUKI else grid_moves(first, FIRST_START),
        "second_moves": grid_moves(second, SECOND_START),
    }
    pointers: list[tuple[int, str]] = []
    hits: dict[str, list[int]] = {}
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
            agent.loadstate((GOUKI_STATE if first == GOUKI else STATE).resolve())
            if first == GOUKI:
                agent.pause()
                original = decompress_file(
                    track_file(SOURCE_TRACK, roster[GOUKI]["mc_file"])
                )[0]
                ranges_mc = byte_ranges(original, files[GOUKI])
                for offset, old, new in ranges_mc:
                    if agent.bus_read(FIRST_BUFFER + offset, len(old)) != old:
                        raise RuntimeError(f"{offset:#x}: not the original MC0F")
                    agent.bus_write(FIRST_BUFFER + offset, new)
                result["mc0f_ranges"] = len(ranges_mc)
                agent.run()
            if mmpack is not None:
                agent.pause()
                ranges = code_ranges(
                    track_file(SOURCE_TRACK, "MMPACK.PCA;1"), mmpack.read_bytes()
                )
                for address, old, new in ranges:
                    if agent.bus_read(address, len(old)) != old:
                        raise RuntimeError(f"{address:#x}: not the original code")
                    agent.bus_write(address, new)
                result["mmpack_ranges"] = len(ranges)
                agent.run()
            time.sleep(0.5)
            if first != GOUKI:
                send(process.pid, str(result["first_moves"]) + "a")
                time.sleep(PRESS_GAP * 2)
            send(process.pid, str(result["second_moves"]) + "a")
            for _ in range(5):
                time.sleep(PRESS_GAP)
                send(process.pid, "a")
            agent.pause()
            agent.screenshot((out / "after_pick.png").resolve())
            result["load_check"] = {
                "first": fixups_match(
                    files[first],
                    agent.bus_read(FIRST_BUFFER, len(files[first])),
                    FIRST_BUFFER + 0x40,
                ),
                "second": fixups_match(
                    files[second],
                    agent.bus_read(SECOND_BUFFER, len(files[second])),
                    SECOND_BUFFER + 0x40,
                ),
            }
            if area is not None:
                agent.bpmode("log")
                agent.breakpoints(
                    "read",
                    [
                        f"{area[0]:08X}-{area[1]:08X}",
                        f"{area[0] | 0x20000000:08X}-{area[1] | 0x20000000:08X}",
                    ],
                )
            frame, last = 0, None
            while frame < frames:
                chars = {b: agent.bus_read(b + CHAR, 1)[0] for b in BLOCKS}
                vitality = {
                    b: int.from_bytes(agent.bus_read(b + VITALITY, 2), "big")
                    for b in BLOCKS
                }
                for block in route.targets(chars, vitality):
                    agent.bus_write(block + VITALITY, bytes(2))
                if route.tag_request:
                    agent.run()
                    send_chord(process.pid, "zc")
                    agent.pause()
                if area is not None:
                    agent.clear_events()
                agent.frames(STEP)
                agent.wait_halted(60.0)
                frame += STEP
                pointer = int.from_bytes(agent.bus_read(POINTER, 4), "big")
                if pointer != last:
                    pointers.append((frame, f"{pointer:#010x}"))
                    last = pointer
                if area is not None:
                    for line in agent.events():
                        if line.startswith("hit"):
                            hits.setdefault(parse_hit(line).get("PC", "?"), []).append(
                                frame
                            )
                if frame % SHOT_EVERY == 0:
                    agent.screenshot((out / "shots" / f"r{frame:06d}.png").resolve())
            if area is not None:
                agent.breakpoints("read", [])
                agent.bpmode("halt")
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    result["events"] = [
        {"event": name, "chars": {f"{b:#010x}": c for b, c in chars.items()}}
        for name, chars in route.events
    ]
    result["pointer_changes"] = pointers
    result["read_hits"] = {
        pc: {"count": len(f), "frames": [f[0], f[-1]]} for pc, f in hits.items()
    }
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--first", type=int, required=True)
    parser.add_argument("--second", type=int, required=True)
    parser.add_argument("--policy", choices=POLICIES, default="first")
    parser.add_argument("--mmpack", type=Path)
    parser.add_argument("--area")
    parser.add_argument("--frames", type=int, default=30000)
    args = parser.parse_args(argv)
    area = None
    if args.area:
        low, high = (int(v, 16) for v in args.area.split(":"))
        area = (low, high)
    result = run(
        args.cue,
        args.out,
        args.first,
        args.second,
        args.policy,
        args.mmpack,
        area,
        args.frames,
    )
    print(json.dumps({k: result[k] for k in ("load_check", "events")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
