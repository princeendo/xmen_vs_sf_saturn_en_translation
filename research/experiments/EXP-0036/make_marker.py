"""EXP-0036: build a same-size marker edit in Nash's first ending record.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/make_marker.py OUT

``MC10.SHP;1`` is read from the untouched source track (checked against the
ISO listing by `tools.disc.build_english.read_file`) and decoded. The first
``CODES`` codes of record 16 (decoded ``0x2EC0``, page 1 of Nash's ending,
`EXP-0035`) are replaced with the first ``CODES`` codes of record 21
(``0x303C``, page 6). Nothing else changes. The file is re-encoded to its
original size with `tools.disc.build_english.build_mc` (its stream ending in
the last sector) and written to OUT with ``changes.json``. Build the image
with `tools.disc.patch_image`.

Prediction: page 1's first ``CODES`` cells show page 6's first ``CODES``
glyphs, and every other cell of the ending is unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import build_mc, read_file
from tools.disc.prs import decompress_file

NAME = "MC10.SHP;1"
RECORD, SIZE = 0x2EC0, 76  # records 16-21 start here (EXP-0035)
SOURCE_RECORD = RECORD + 5 * SIZE  # record 21, page 6
CODES = 4


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    raw = read_file(NAME)
    decoded, _ = decompress_file(raw)
    marker = decoded[SOURCE_RECORD : SOURCE_RECORD + 2 * CODES]
    changes: list[dict[str, object]] = []
    rebuilt = build_mc(raw, marker, RECORD, NAME, changes)
    (out / "MC10.SHP").write_bytes(rebuilt)
    summary = {
        "file": NAME,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "built_sha256": hashlib.sha256(rebuilt).hexdigest(),
        "size": len(rebuilt),
        "changes": changes,
    }
    (out / "changes.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
