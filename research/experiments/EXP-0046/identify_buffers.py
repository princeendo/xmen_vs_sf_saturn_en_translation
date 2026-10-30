r"""EXP-0046: say which MC file each saved team buffer holds.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/identify_buffers.py \
        CUE RUN_DIR [...]

For each RUN_DIR (a `tools.mednafen.route` output with ``first_buffer.bin``
and ``second_buffer.bin``), each buffer is compared with every MC file of
CUE's track (decoded, plus fix-ups, `tools.mednafen.route.fixups_match`).
For the intended file it also gives the number of differing bytes and the
first differing offset (after fix-ups are allowed for).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.prs import decompress_file
from tools.mednafen.route import (
    FIRST_BUFFER,
    SECOND_BUFFER,
    fixups_match,
    track_file,
)

ROSTER = Path("data/text/m5_roster.json")


def differences(decoded: bytes, ram: bytes, delta: int) -> list[int]:
    """Offsets of bytes that differ and are not part of a fixed-up long."""
    out = []
    i = 0
    while i < len(decoded):
        if ram[i] == decoded[i]:
            i += 1
            continue
        start = i - (i % 2)
        for at in (start, start - 2):
            if at >= 0 and at + 4 <= len(decoded):
                value = (int.from_bytes(decoded[at : at + 4], "big") + delta) & (
                    0xFFFFFFFF
                )
                if value.to_bytes(4, "big") == ram[at : at + 4]:
                    i = at + 4
                    break
        else:
            out.append(i)
            i += 1
    return out


def main(cue: Path, runs: list[Path]) -> int:
    track = cue.parent / f"{cue.stem} (Track 01).bin"
    roster = json.loads(ROSTER.read_text())["roster"]
    files = {
        m["slot"]: decompress_file(track_file(track, m["mc_file"]))[0] for m in roster
    }
    for run in runs:
        result = json.loads((run / "result.json").read_text())
        for member, base in (("first", FIRST_BUFFER), ("second", SECOND_BUFFER)):
            ram = (run / f"{member}_buffer.bin").read_bytes()
            holds = [
                s for s, data in files.items() if fixups_match(data, ram, base + 0x40)
            ]
            intended = result[member]
            diff = differences(files[intended], ram, base + 0x40)
            print(
                json.dumps(
                    {
                        "run": run.name,
                        "member": member,
                        "intended": intended,
                        "holds": holds,
                        "differing_bytes": len(diff),
                        "first_differing": f"{diff[0]:#x}" if diff else None,
                        "last_differing": f"{diff[-1]:#x}" if diff else None,
                    }
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]))
