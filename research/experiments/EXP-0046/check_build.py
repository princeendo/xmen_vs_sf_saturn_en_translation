"""EXP-0046: check the M8 build's files against the specs and censuses.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/check_build.py BUILD_OUT REPORT

BUILD_OUT is the ``tools.disc.build_english`` output directory. For each
roster slot this checks, in the decoded rebuilt MC file:

- the bytes at the quote table are the 8 English win quotes, then the English
  ending records from the US arcade program (pointer from the spec), and
  every other byte equals the original file;
- the compressed margin: file size minus the natural lazy PRS length.

For ``MCED.SHP`` it checks that the changes are exactly one header word per
distinct roster script, each set to that script's language-2 word
(``data/text/ending_script_census.json``), and nothing else. For
``MMPACK.PCA`` it checks the changes against ``patches_v4`` with slots 0-17
and the roster's ending slots. Writes REPORT (JSON: offsets, hashes and sizes
only).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import read_file
from tools.disc.english_mode import (
    ENDING_RECORDS,
    as_bytes,
    patches_v4,
)
from tools.disc.prs import compress, decompress_file

PROGRAM = Path("local/ref003/xmvsfu-68k.bin")
ROSTER = Path("data/text/m8_ending_roster.json")
SCRIPTS = Path("data/text/ending_script_census.json")
SPECS = Path("data/translations")


def stem(name: str) -> str:
    return name.lower().replace("-", "_")


def check_mc(out: Path, member: dict[str, object], program: bytes) -> dict[str, object]:
    name = str(member["mc_file"])
    spec = json.loads((SPECS / f"{stem(str(member['name']))}_ending.json").read_text())
    wins = json.loads(
        (SPECS / f"{stem(str(member['name']))}_win_quotes.json").read_text()
    )
    built = (out / name.split(";")[0]).read_bytes()
    original, _ = decompress_file(read_file(name))
    decoded, _ = decompress_file(built)
    table = int(str(member["table_offset"]), 16)
    english = b"".join(
        program[int(r["source_address"], 16) : int(r["source_address"], 16) + 100]
        for r in [*wins["records"], *spec["records"]]
    )
    end = table + len(english)
    same_outside = (
        decoded[:table] == original[:table] and decoded[end:] == original[end:]
    )
    natural = len(compress(decoded, lazy=True))
    return {
        "mc_file": name,
        "english_bytes": len(english),
        "ending_from": f"{table + ENDING_RECORDS:#x}",
        "english_matches": decoded[table:end] == english,
        "same_outside": same_outside,
        "file_size": len(built),
        "natural_lazy": natural,
        "compressed_margin": len(built) - natural,
        "rebuilt_sha256": hashlib.sha256(built).hexdigest(),
    }


def main(out: Path, report: Path) -> int:
    program = PROGRAM.read_bytes()
    roster = json.loads(ROSTER.read_text())
    changes = json.loads((out / "changes.json").read_text())["changes"]
    rows = [check_mc(out, m, program) for m in roster["members"]]

    scripts = json.loads(SCRIPTS.read_text())["slots"]
    expected: dict[str, str] = {}
    for row in scripts:
        if row["slot"] in roster["roster_slots"]:
            # script_offset is the decoded offset (table value + 0x40)
            expected[row["script_offset"]] = f"{int(row['header'][1], 16):04x}"
    mced = {
        c["decompressed_offset"]: c["modified"]
        for c in changes
        if c["file"] == "MCED.SHP;1"
    }
    mced_ok = mced == expected and all(
        c["original"] == "0008" for c in changes if c["file"] == "MCED.SHP;1"
    )

    ending_slots = list(roster["roster_slots"])
    planned = patches_v4(list(range(18)), ending_slots)
    mmpack = [
        (int(c["ram_address"], 16), c["original"], c["modified"])
        for c in changes
        if c["file"] == "MMPACK.PCA"
    ]
    mmpack_ok = mmpack == [
        (a, as_bytes(o).hex(), as_bytes(n).hex()) for a, o, n in planned
    ]

    result = {
        "mc_files": rows,
        "all_mc_ok": all(r["english_matches"] and r["same_outside"] for r in rows),
        "smallest_margin": min(int(str(r["compressed_margin"])) for r in rows),
        "mced_edits": len(mced),
        "mced_ok": mced_ok,
        "mmpack_patches": len(mmpack),
        "mmpack_ok": mmpack_ok,
    }
    report.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "mc_files"}))
    for r in rows:
        print(r["mc_file"], r["english_bytes"], r["compressed_margin"])
    return 0 if result["all_mc_ok"] and mced_ok and mmpack_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
