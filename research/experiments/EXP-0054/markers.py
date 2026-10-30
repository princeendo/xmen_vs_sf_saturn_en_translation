r"""EXP-0054: write ERR1-ERR5.BIN, each with a marker band, for a test build.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0054/markers.py OUT

Each ``ERRn.BIN`` is read from the untouched data track
(`tools.disc.build_english.read_file`, checked against the listing). In
picture rows ``BAND_TOP + 40n`` to ``+ 3`` (top-down, as shown: screen row =
picture row + 8, `EXP-0054`), columns ``LEFT`` to ``RIGHT``, every pixel is
set to colour index ``MARK`` (14, shown as ``c00000``). Nothing else
changes; the size stays the same. ``OUT/ERRn.BIN`` and ``OUT/changes.json``
(per file: rows, the byte range of each changed BMP row with its original and
new bytes' SHA-256, and the file hashes; AGENTS.md rule 12) are written. OUT
is an ignored path; the files are game data and are never committed.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file

BAND_TOP, BAND_ROWS, LEFT, RIGHT, MARK = 0, 4, 8, 343, 14


def mark(data: bytes, n: int) -> tuple[bytes, list[dict[str, object]]]:
    out = bytearray(data)
    offset = struct.unpack_from("<I", data, 10)[0]
    width, height = struct.unpack_from("<ii", data, 18)
    stride = (width * 4 + 31) // 32 * 4
    changes = []
    for row in range(BAND_TOP + 40 * n, BAND_TOP + 40 * n + BAND_ROWS):
        start = offset + (height - 1 - row) * stride
        old = bytes(out[start : start + stride])
        for x in range(LEFT, RIGHT + 1):
            byte = start + x // 2
            if x % 2 == 0:
                out[byte] = (MARK << 4) | (out[byte] & 0x0F)
            else:
                out[byte] = (out[byte] & 0xF0) | MARK
        new = bytes(out[start : start + stride])
        changes.append(
            {
                "picture_row": row,
                "file_offset": f"{start:#x}",
                "length": stride,
                "original_sha256": hashlib.sha256(old).hexdigest(),
                "modified_sha256": hashlib.sha256(new).hexdigest(),
            }
        )
    return bytes(out), changes


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    record: dict[str, object] = {}
    for n in range(1, 6):
        name = f"ERR{n}.BIN"
        data = read_file(f"{name};1")
        marked, changes = mark(data, n)
        (out / name).write_bytes(marked)
        record[name] = {
            "original_sha256": hashlib.sha256(data).hexdigest(),
            "marked_sha256": hashlib.sha256(marked).hexdigest(),
            "rows": changes,
        }
    (out / "changes.json").write_text(json.dumps(record, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
