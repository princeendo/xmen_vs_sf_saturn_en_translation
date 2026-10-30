r"""EXP-0046: load-check every roster character, picked first and second.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/load_check.py CUE OUT \
        [FIRST:SECOND ...]

For the 16 grid characters in roster order, team i is (G[i], G[i + 1]),
wrapping, so each is picked once first and once second. Gouki (not on the
grid) is picked first from `tools.mednafen.route.GOUKI_STATE`, with Cyclops
second. Given FIRST:SECOND pairs, only those teams are run.

Each attempt is one `tools.mednafen.route.run` with ``frames=0``: the picks,
then both buffers, saved. Runs are made one at a time (each brings Mednafen
to the front for the picks). Each buffer is then judged against CUE's MC
files (decoded, plus fix-ups):

- **pass:** it equals the intended file. For Rogue (slot 3), differences
  confined to ``ROGUE_WORDS`` also pass: the game writes those ``9999``
  words after loading, on the untouched image too (`EXP-0046` control);
- **wrong pick:** it holds another character's file exactly (a key was
  lost; `EXP-0046`). The team is tried again, up to ``ATTEMPTS`` times;
- **fail:** anything else.

Writes ``OUT/summary.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from identify_buffers import differences

from tools.disc.prs import decompress_file
from tools.mednafen.route import (
    FIRST_BUFFER,
    GOUKI,
    SECOND_BUFFER,
    fixups_match,
    run,
    track_file,
)

ROSTER = Path("data/text/m8_ending_roster.json")
M5_ROSTER = Path("data/text/m5_roster.json")
ATTEMPTS = 4
ROGUE = 3
ROGUE_WORDS = (0x9332, 0xA446, 0xB018, 0xBDE4)  # 4 bytes each, 9999 9999 in MC03


def teams(slots: list[int]) -> list[tuple[int, int]]:
    grid = [s for s in slots if s != GOUKI]
    pairs = [(grid[i], grid[(i + 1) % len(grid)]) for i in range(len(grid))]
    return [*pairs, (GOUKI, 1)]


def verdict(intended: int, ram: bytes, base: int, files: dict[int, bytes]) -> str:
    delta = base + 0x40
    diff = differences(files[intended], ram, delta)
    if not diff:
        return "pass"
    if intended == ROGUE and all(
        any(w <= i < w + 4 for w in ROGUE_WORDS) for i in diff
    ):
        return "pass (Rogue's words)"
    if any(fixups_match(data, ram, delta) for data in files.values()):
        return "wrong pick"
    return "fail"


def main(cue: Path, out: Path, chosen: list[str]) -> int:
    out.mkdir(parents=True, exist_ok=False)
    track = cue.parent / f"{cue.stem} (Track 01).bin"
    files = {
        m["slot"]: decompress_file(track_file(track, m["mc_file"]))[0]
        for m in json.loads(M5_ROSTER.read_text())["roster"]
    }
    slots = json.loads(ROSTER.read_text())["roster_slots"]
    pairs = teams(slots)
    if chosen:
        pairs = [(int(a), int(b)) for a, b in (c.split(":") for c in chosen)]
    summary: list[dict[str, object]] = []
    final: list[dict[str, str]] = []
    for first, second in pairs:
        attempts: list[dict[str, str]] = []
        for attempt in range(1, ATTEMPTS + 1):
            name = f"t{first:02d}_{second:02d}_a{attempt}"
            run(cue, out / name, first, second, frames=0)
            row = {"run": name}
            for member, slot, base in (
                ("first", first, FIRST_BUFFER),
                ("second", second, SECOND_BUFFER),
            ):
                ram = (out / name / f"{member}_buffer.bin").read_bytes()
                row[member] = verdict(slot, ram, base, files)
            attempts.append(row)
            print(json.dumps(row), flush=True)
            if "wrong pick" not in row.values():
                break
        summary.append({"team": [first, second], "attempts": attempts})
        final.append(attempts[-1])
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    ok = all(row[m].startswith("pass") for row in final for m in ("first", "second"))
    print("all pass" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))
