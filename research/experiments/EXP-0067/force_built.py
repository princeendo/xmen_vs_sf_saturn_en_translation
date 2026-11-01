r"""EXP-0067: force every continue-hint index on a built image's code.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/force_built.py \
        CUE STATE MMPACK OUT [INDEX ...]

CUE is the built image, MMPACK its built ``MMPACK.PCA``. For each INDEX
(default 0-15), runs `EXP-0066/continue_run.py` into ``OUT/iNN`` for
``FRAMES`` frames with, at the load (each original checked first):

- every run of bytes where MMPACK's decoded segments differ from the
  untouched file's (`tools.mednafen.route.SOURCE_TRACK`), at each segment's
  load address; the first segment's extension (the hint table) is compared
  with zero, the gap's content in the fight state;
- the starter's ``and #0x0F,r0`` (``0x06066730``, ``C90F``) as
  ``mov #INDEX,r0`` (``E0nn``).

Copies the ``SHOTS`` screenshots (page 1, page 2) to ``OUT/iNN_p1.png`` and
``OUT/iNN_p2.png``, and writes ``OUT/summary.json``: per index, the
pointer values the renderer reached, and whether they are the table records
`tools.disc.continue_hints` maps the index to. OUT is an ignored path.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.continue_hints import SIZE, TABLE, map_bytes
from tools.disc.prs import decompress_entries, split_header
from tools.mednafen.route import SOURCE_TRACK, byte_ranges, track_file

_SPEC = importlib.util.spec_from_file_location(
    "continue_run", "research/experiments/EXP-0066/continue_run.py"
)
assert _SPEC and _SPEC.loader
CONTINUE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(CONTINUE)

MASK = 0x06066730
FRAMES, SHOTS = 3000, (2370, 2760)


def segments(raw: bytes) -> list[tuple[int, bytes]]:
    _, entries = split_header(raw)
    _, decoded, _ = decompress_entries(raw)
    out, at = [], 0
    for dest, size in entries:
        out.append((dest, decoded[at : at + size]))
        at += size
    return out


def code_patches(original: bytes, built: bytes) -> list[str]:
    patches = []
    for (dest, old), (built_dest, new) in zip(
        segments(original), segments(built), strict=True
    ):
        if dest != built_dest or len(new) < len(old):
            raise ValueError(f"{dest:#x}: segments do not line up")
        old = old + bytes(len(new) - len(old))
        for offset, a, b in byte_ranges(old, new):
            patches.append(f"{dest + offset:08X}:{a.hex()}:{b.hex()}")
    return patches


def main(cue: Path, state: Path, mmpack: Path, out: Path, indexes: list[int]) -> int:
    out.mkdir(parents=True, exist_ok=True)
    code = code_patches(track_file(SOURCE_TRACK, "MMPACK.PCA;1"), mmpack.read_bytes())
    first = map_bytes()
    summary = {}
    for index in indexes:
        run = out / f"i{index:02d}"
        CONTINUE.main(
            cue, state, run, FRAMES, [*code, f"{MASK:08X}:C90F:E0{index:02X}"]
        )
        for page, shot in enumerate(SHOTS, 1):
            shutil.copy(
                run / "shots" / f"r{shot:05d}.png", out / f"i{index:02d}_p{page}.png"
            )
        reached = [
            p
            for _, p in json.loads((run / "result.json").read_text())["pointer_changes"]
        ]
        want = [f"{TABLE + SIZE * (first[index] + k):08x}" for k in (0, 1)]
        summary[index] = {
            "reached": reached,
            "want": want,
            "ok": all(w in reached for w in want),
        }
        print(json.dumps({"index": index, **summary[index]}))
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(
        main(
            Path(a[0]),
            Path(a[1]),
            Path(a[2]),
            Path(a[3]),
            [int(x) for x in a[4:]] or list(range(16)),
        )
    )
