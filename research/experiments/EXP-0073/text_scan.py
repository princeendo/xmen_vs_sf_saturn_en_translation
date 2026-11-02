r"""EXP-0073: find every block of quote-font text on the disc (TXT-001).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0073/text_scan.py OUT

Reads every file of the untouched source track (`tools.mednafen.route`
``SOURCE_TRACK``, the ISO listing in ``references/saturn_jp/iso_listing.json``),
decoded with `tools.disc.prs` when it decodes (one stream, or a header of
segments), raw otherwise. In each, a **run** is a word-aligned stretch of
big-endian 16-bit codes that are all text codes (``TEXT``: the space
``0x0020``, the quote font's ``0x0900``-``0x0DFF``, the arrows
``0x0130``-``0x013F``; measured on Ryu's table, `EXP-0073` README) and at
least ``MIN_WORDS`` long with at least ``MIN_GLYPHS`` non-space codes. Runs
closer than ``JOIN`` bytes form a **block**. Each block is marked with the
known table it overlaps (the specs' quote tables, ``KNOWN``) or ``unknown``.

Writes ``OUT`` (JSON, ignored path): per block, the file, offset, size, run
count, glyph count and the known table, never the codes. Prints a summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import PrsError, decompress_entries, decompress_file
from tools.mednafen.route import SOURCE_TRACK, track_file

MIN_WORDS, MIN_GLYPHS, JOIN = 19, 4, 64
QUOTE_TABLE = 22 * 76
KNOWN = {  # file -> [(start, end, name)], beyond the specs' quote tables
    "MMPACK.PCA": [
        (
            0x06085544 - 0x0601F000 + 0xA460,
            0x06085544 - 0x0601F000 + 0xA460 + 21 * 76,
            "hint table (D-058)",
        )
    ],
    "MC08.SHP": [(0x1090, 0x1090 + 18 * 76, "Apocalypse's boss boxes (D-052)")],
}


def is_text(word: int) -> bool:
    return word == 0x0020 or 0x0900 <= word < 0x0E00 or 0x0130 <= word < 0x0140


def decode(raw: bytes) -> bytes:
    try:
        if int.from_bytes(raw[:4], "big") == 0:
            return decompress_file(raw)[0]
        return decompress_entries(raw)[1]
    except (PrsError, ValueError, IndexError):
        return raw


def runs(data: bytes) -> list[tuple[int, int, int]]:
    """(start, end, glyphs) of each run."""
    out, start, glyphs = [], None, 0
    for at in range(0, len(data) - 1, 2):
        word = int.from_bytes(data[at : at + 2], "big")
        if is_text(word):
            if start is None:
                start, glyphs = at, 0
            glyphs += word != 0x0020
            continue
        if (
            start is not None
            and (at - start) // 2 >= MIN_WORDS
            and glyphs >= MIN_GLYPHS
        ):
            out.append((start, at, glyphs))
        start = None
    return out


def main(out: Path) -> int:
    listing = json.loads(Path("references/saturn_jp/iso_listing.json").read_text())
    known = dict(KNOWN)
    for spec in Path("data/translations").glob("*_win_quotes.json"):
        s = json.loads(spec.read_text())
        name = str(s["mc_file"]).split(";")[0]
        at = int(str(s["table_offset"]), 16)
        known.setdefault(name, []).append(
            (at, at + QUOTE_TABLE, f"{s['character']}'s quote table")
        )
    blocks = []
    for entry in listing["files"]:
        if entry["is_dir"]:
            continue
        path = entry["path"]
        name = path.split("/")[-1].split(";")[0]
        data = decode(track_file(SOURCE_TRACK, path if ";" in path else f"{path};1"))
        found = runs(data)
        group: list[tuple[int, int, int]] = []
        for run in [*found, (1 << 62, 1 << 62, 0)]:
            if group and run[0] - group[-1][1] > JOIN:
                start, end = group[0][0], group[-1][1]
                tags = [n for a, b, n in known.get(name, []) if a < end and start < b]
                blocks.append(
                    {
                        "file": name,
                        "offset": f"{start:#x}",
                        "size": end - start,
                        "runs": len(group),
                        "glyphs": sum(g for _, _, g in group),
                        "known": tags or ["unknown"],
                    }
                )
                group = []
            group.append(run)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(blocks, indent=1) + "\n")
    for b in blocks:
        print(
            b["file"],
            b["offset"],
            b["size"],
            b["runs"],
            b["glyphs"],
            "; ".join(b["known"]),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
