r"""EXP-0047: pair each Saturn ending page with the arcade's, for review.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/compare_pages.py \
        RUNS ARCADE_COMPARE ARCADE_RUNS OUT

RUNS is `run_endings.py`'s output. For each slot's last run whose load check
passed:

- **Saturn pages:** the quote pointer log gives each page's first frame,
  where the pointer is quote table + 800 + 100k (version 4). The page's
  screenshot is the last route screenshot (every 120 frames) before the
  next page starts. For the last page it is the last one within 360 frames
  of its start.
- **Arcade pages:** `EXP-0044`'s ``compare.json`` gives each English
  page's first frame (``s<slot>_default_en``). The page's snapshot is the
  last one (every 60 frames) at least 60 frames before the next page. For
  the last page it is the last one within 360 frames of its start.

For each slot, OUT gets ``s<slot>.png``: one row per page, Saturn on the
left and arcade on the right, both at 352 x 240. It also gets
``pages.json``, with the frames and files used and the pages' SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.english_mode import ENDING_RECORDS
from tools.mednafen.route import FIRST_BUFFER

ROSTER = Path("data/text/m8_ending_roster.json")
LAST_PAGE = 360


def last_before(frames: dict[int, Path], limit: int, start: int) -> Path | None:
    chosen = [f for f in frames if start <= f < limit]
    return frames[max(chosen)] if chosen else None


def saturn_pages(run: Path, member: dict[str, object]) -> list[tuple[int, Path | None]]:
    result = json.loads((run / "result.json").read_text())
    base = FIRST_BUFFER + int(str(member["table_offset"]), 16) + ENDING_RECORDS
    count = int(str(member["english_ending_records"]))
    wanted = {base + 100 * k: k for k in range(count)}
    starts: dict[int, int] = {}
    for frame, pointer in result["pointer_changes"]:
        k = wanted.get(int(pointer, 16))
        if k is not None and k not in starts:
            starts[k] = frame
    shots = {int(p.stem[1:]): p for p in (run / "shots").glob("r*.png")}
    pages: list[tuple[int, Path | None]] = []
    for k in range(count):
        if k not in starts:
            pages.append((-1, None))
            continue
        end = starts.get(k + 1, starts[k] + LAST_PAGE + 1)
        pages.append((starts[k], last_before(shots, end, starts[k])))
    return pages


def arcade_pages(
    compare: dict[str, object], runs: Path, slot: int
) -> list[tuple[int, Path | None]]:
    name = f"s{slot}_default_en"
    entry = compare[name]
    assert isinstance(entry, dict)
    starts = entry["read"]["frames"]
    snaps = {
        int(p.stem.split("_f")[1]): p for p in (runs / name / "snap").glob("*.png")
    }
    pages: list[tuple[int, Path | None]] = []
    for k, start in enumerate(starts):
        end = starts[k + 1] - 59 if k + 1 < len(starts) else start + LAST_PAGE + 1
        pages.append((start, last_before(snaps, end, start)))
    return pages


def sha(path: Path | None) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else None


def sheet(rows: list[tuple[Path | None, Path | None]], out: Path) -> None:
    inputs: list[str] = []
    filters = []
    for i, (left, right) in enumerate(rows):
        for j, path in enumerate((left, right)):
            if path is None:
                inputs += ["-f", "lavfi", "-i", "color=c=red:s=352x240:d=1"]
            else:
                inputs += ["-i", str(path)]
            filters.append(f"[{2 * i + j}:v]scale=352:240,setsar=1[v{i}_{j}]")
        filters.append(f"[v{i}_0][v{i}_1]hstack=inputs=2[r{i}]")
    rows_in = "".join(f"[r{i}]" for i in range(len(rows)))
    filters.append(f"{rows_in}vstack=inputs={len(rows)}[out]")
    if len(rows) == 1:
        filters[-1] = "[r0]null[out]"
    subprocess.run(
        [
            *("ffmpeg", "-v", "error", "-y", *inputs),
            *("-filter_complex", ";".join(filters), "-map", "[out]"),
            *("-frames:v", "1", str(out)),
        ],
        check=True,
    )


def main(runs: Path, compare_path: Path, arcade_runs: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    compare = json.loads(compare_path.read_text())
    passed = {
        r["slot"]: r["run"]
        for r in json.loads((runs / "runs.json").read_text())
        if r["load_check"] and r["load_check"]["first"] and r["load_check"]["second"]
    }
    report: dict[str, object] = {}
    for member in json.loads(ROSTER.read_text())["members"]:
        slot = int(str(member["slot"]))
        if slot not in passed:
            report[str(slot)] = {"error": "no run with a passing load check"}
            continue
        saturn = saturn_pages(runs / passed[slot], member)
        arcade = arcade_pages(compare, arcade_runs, slot)
        if len(saturn) != len(arcade):
            raise ValueError(f"slot {slot}: {len(saturn)} vs {len(arcade)} pages")
        sheet(
            [(s[1], a[1]) for s, a in zip(saturn, arcade, strict=True)],
            out / f"s{slot:02d}.png",
        )
        report[str(slot)] = {
            "run": passed[slot],
            "pages": [
                {
                    "page": k + 1,
                    "saturn_start": s[0],
                    "saturn_shot": str(s[1]),
                    "saturn_sha256": sha(s[1]),
                    "arcade_start": a[0],
                    "arcade_snap": str(a[1]),
                }
                for k, (s, a) in enumerate(zip(saturn, arcade, strict=True))
            ],
        }
    (out / "pages.json").write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*(Path(a) for a in sys.argv[1:5])))
