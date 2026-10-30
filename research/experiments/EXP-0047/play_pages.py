"""EXP-0047: find the route's ending pages in a recorded play session.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0047/play_pages.py \
        PAGES SESSION OUT SLOT [SLOT ...]

PAGES is `compare_pages.py`'s ``pages.json``. For each page of each SLOT,
every screenshot in ``SESSION/shots`` is compared with the route's page
screenshot:

- **screen:** the whole screenshot is byte-identical;
- **text box:** the decoded pixels of the text box and label
  (``BOX``: x 16-336, y 170-226, the `EXP-0042` box plus the label row)
  are identical. This covers pages whose picture's background cycles
  colour, which a whole-screen hash only matches at the same moment.

Writes ``OUT`` (JSON): per page, the first and last matching session frame
and the number of matches of each kind.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

BOX = (16, 170, 320, 56)  # x, y, width, height


def box_pixels(path: Path) -> bytes:
    x, y, w, h = BOX
    return subprocess.run(
        [
            *("ffmpeg", "-v", "error", "-i", str(path)),
            *("-vf", f"crop={w}:{h}:{x}:{y}", "-f", "rawvideo", "-pix_fmt", "rgb24"),
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout


def main(pages_path: Path, session: Path, out: Path, slots: list[str]) -> int:
    pages = json.loads(pages_path.read_text())
    shots = sorted((session / "shots").glob("f*.png"))
    targets = {(s, t["page"]): t for s in slots for t in pages[s]["pages"]}
    boxes = {key: box_pixels(Path(t["saturn_shot"])) for key, t in targets.items()}
    screen_hits: dict[tuple[str, int], list[str]] = {key: [] for key in targets}
    box_hits: dict[tuple[str, int], list[str]] = {key: [] for key in targets}
    for shot in shots:
        digest = hashlib.sha256(shot.read_bytes()).hexdigest()
        pixels = box_pixels(shot)
        for key, target in targets.items():
            if digest == target["saturn_sha256"]:
                screen_hits[key].append(shot.stem)
            if pixels == boxes[key]:
                box_hits[key].append(shot.stem)
    report: dict[str, list[dict[str, object]]] = {}
    for (slot, page), _ in targets.items():
        screen, box = screen_hits[(slot, page)], box_hits[(slot, page)]
        report.setdefault(slot, []).append(
            {
                "page": page,
                "screen_matches": len(screen),
                "screen_first": screen[0] if screen else None,
                "box_matches": len(box),
                "box_first": box[0] if box else None,
                "box_last": box[-1] if box else None,
            }
        )
    out.write_text(json.dumps(report, indent=1) + "\n")
    for slot, rows in report.items():
        for row in rows:
            print(slot, json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4:])
    )
