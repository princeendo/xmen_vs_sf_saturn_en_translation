r"""EXP-0068: every byte that differs between the two name variants' files.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0068/census.py US_DIR SATURN_DIR OUT

US_DIR and SATURN_DIR hold one build's files each (as
``build/regression/<name>/files``). For each file whose bytes differ, both
copies are decoded (`MMPACK.PCA` by segment, the others as one stream) and
compared byte by byte. Runs of differing bytes closer than ``JOIN`` bytes
are joined. Writes ``OUT`` (JSON, ignored path): per file, the stored and
decoded sizes of each variant and each run's decoded offset, length, count
of differing bytes and, for `MMPACK.PCA`, RAM address. Prints a summary
line per file. No game bytes are written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_entries, decompress_file, split_header

JOIN = 16


def decoded(raw: bytes) -> list[tuple[int | None, bytes]]:
    """(load address or None, bytes) for each segment."""
    if int.from_bytes(raw[:4], "big") == 0:
        return [(None, decompress_file(raw)[0])]
    _, entries = split_header(raw)
    _, data, _ = decompress_entries(raw)
    out: list[tuple[int | None, bytes]] = []
    at = 0
    for dest, size in entries:
        out.append((dest, data[at : at + size]))
        at += size
    return out


def runs(a: bytes, b: bytes) -> list[dict[str, int]]:
    out: list[dict[str, int]] = []
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            continue
        if out and i - (out[-1]["offset"] + out[-1]["length"]) < JOIN:
            out[-1]["length"] = i + 1 - out[-1]["offset"]
            out[-1]["differing"] += 1
        else:
            out.append({"offset": i, "length": 1, "differing": 1})
    return out


def main(us: Path, saturn: Path, out: Path) -> int:
    result = {}
    for path in sorted(us.iterdir()):
        other = saturn / path.name
        if path.suffix == ".json" or path.read_bytes() == other.read_bytes():
            continue
        a, b = path.read_bytes(), other.read_bytes()
        segments: list[dict[str, Any]] = []
        for (dest, x), (_, y) in zip(decoded(a), decoded(b), strict=True):
            found = runs(x, y)
            if dest is not None:
                for run in found:
                    run["ram"] = dest + run["offset"]
            segments.append(
                {
                    "load": None if dest is None else f"{dest:#010x}",
                    "decoded": [len(x), len(y)],
                    "differing": sum(r["differing"] for r in found),
                    "runs": found,
                }
            )
        result[path.name] = {"stored": [len(a), len(b)], "segments": segments}
        print(
            path.name,
            "stored",
            len(a),
            len(b),
            "; ".join(
                f"{s['load'] or 'stream'}: {s['decoded'][0]}/{s['decoded'][1]} bytes, "
                f"{s['differing']} differ in {len(s['runs'])} runs"
                for s in segments
            ),
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2])))
