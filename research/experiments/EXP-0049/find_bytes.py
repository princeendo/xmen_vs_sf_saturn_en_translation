r"""EXP-0049: find a block of VRAM bytes in RAM dumps and in every disc file.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/find_bytes.py \
        DUMP_DIR VRAM START LENGTH [--files DIR] [--min CHUNK]

Takes LENGTH bytes at START of ``DUMP_DIR/VRAM`` (``vdp1.bin`` or
``vdp2.bin``, from ``dump_screen.py``) and looks for them:

- in ``DUMP_DIR``'s ``wram_l.bin`` and ``wram_h.bin``, reported as bus
  addresses;
- in every file of DIR (default ``local/ref007/saturn_files``, the files
  of the untouched data track), raw, and decoded with `tools.disc.prs`
  where it decodes (single stream or ``PCA`` entries).

The block is searched whole, and also in CHUNK-byte pieces (default 32),
so that data stored in another order (for example cell by cell) still
shows where each piece lives. A piece that is all one byte value is
skipped. Prints JSON.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_entries, decompress_file

FILES = Path("local/ref007/saturn_files")
WRAM = {"wram_l.bin": 0x00200000, "wram_h.bin": 0x06000000}


def views(path: Path) -> dict[str, bytes]:
    raw = path.read_bytes()
    out = {"raw": raw}
    # not every file is a PRS stream or a PCA pack
    with contextlib.suppress(Exception):
        out["prs"] = decompress_file(raw)[0]
    with contextlib.suppress(Exception):
        out["pca"] = decompress_entries(raw)[1]
    return out


def find_all(data: bytes, needle: bytes) -> list[int]:
    hits: list[int] = []
    at = data.find(needle)
    while at >= 0 and len(hits) < 20:
        hits.append(at)
        at = data.find(needle, at + 1)
    return hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dump", type=Path)
    parser.add_argument("vram")
    parser.add_argument("start", type=lambda v: int(v, 0))
    parser.add_argument("length", type=lambda v: int(v, 0))
    parser.add_argument("--files", type=Path, default=FILES)
    parser.add_argument("--min", type=int, default=32, dest="chunk")
    args = parser.parse_args(argv)
    block = (args.dump / args.vram).read_bytes()[args.start : args.start + args.length]
    pieces = [
        (offset, block[offset : offset + args.chunk])
        for offset in range(0, len(block), args.chunk)
    ]
    pieces = [(o, p) for o, p in pieces if len(set(p)) > 1]
    result: dict[str, object] = {"block_hits": {}, "piece_hits": {}}
    sources: dict[str, bytes] = {}
    for name, base in WRAM.items():
        path = args.dump / name
        if path.exists():
            sources[f"{name}@{base:#010x}"] = path.read_bytes()
    for path in sorted(args.files.iterdir()):
        for kind, data in views(path).items():
            sources[f"{path.name}:{kind}"] = data
    block_hits = result["block_hits"]
    piece_hits = result["piece_hits"]
    assert isinstance(block_hits, dict) and isinstance(piece_hits, dict)
    for name, data in sources.items():
        hits = find_all(data, block)
        if hits:
            block_hits[name] = [f"{h:#x}" for h in hits]
        found = {
            f"{o:#x}": [f"{h:#x}" for h in find_all(data, p)]
            for o, p in pieces
            if p in data
        }
        if found:
            piece_hits[name] = found
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
