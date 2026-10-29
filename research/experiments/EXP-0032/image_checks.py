"""EXP-0032: check a built English image against the source and the build criteria.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0032/image_checks.py \\
        IMAGE_DIR B1 B2 OUT_JSON

IMAGE_DIR is a ``build/`` directory from ``tools.disc.build_english --image``.
B1 and B2 are the file outputs of two independent builds from the same specs
(B1 made the image). The script checks:

- **Components:** only Track 01 differs from the source. Every source
  component still hashes to a value in `references/saturn_jp/README.md`.
- **Sectors:** every sector of the built Track 01 passes Mode 1 EDC/ECC
  (`tools.disc.sector.verify_track`).
- **Layout:** the built ISO listing (`tools/disc/iso9660.py --check`) has the
  same paths, LSNs and sizes as `references/saturn_jp/iso_listing.json`. The
  files whose hashes differ are exactly ``MMPACK.PCA`` and the specs' MC
  files.
- **Builds:** B1 and B2 hold byte-identical files, and each built file
  equals the file in the image.
- **Code:** the decoded ``MMPACK.PCA`` differs from the original only at
  `tools.disc.english_mode.patches_v3` sites for the slots of the changed MC
  files (from `data/text/m5_roster.json`), and holds the new bytes there.

It writes a summary to OUT_JSON and prints it. Only hashes, counts and names
are written.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.build_english import TRACK, read_file
from tools.disc.english_mode import as_bytes, patches_v3
from tools.disc.prs import decompress_entries, split_header
from tools.disc.sector import verify_track

MANIFEST = Path("references/saturn_jp/README.md")
LISTING = Path("references/saturn_jp/iso_listing.json")
ROSTER = Path("data/text/m5_roster.json")  # MC file -> slot


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def code(raw: bytes) -> tuple[bytes, int]:
    _, entries = split_header(raw)
    _, decoded, _ = decompress_entries(raw)
    (_, first_size), (second_dest, _) = entries
    return decoded, second_dest - first_size


def main(image: Path, b1: Path, b2: Path, out: Path) -> int:
    source = TRACK.parent
    known = set(re.findall(r"[0-9a-f]{64}", MANIFEST.read_text()))
    built_track = image / TRACK.name
    differing = [
        p.name for p in sorted(source.iterdir()) if sha256(p) != sha256(image / p.name)
    ]
    source_ok = all(sha256(p) in known for p in source.iterdir() if p.is_file())
    invalid = verify_track(built_track)
    listing = json.loads(
        subprocess.run(
            [sys.executable, "-m", "tools.disc.iso9660", "--check", str(built_track)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    original = json.loads(LISTING.read_text())
    same_layout = len(listing["files"]) == len(original["files"]) and all(
        (f["path"], f["lsn"], f["size_bytes"]) == (g["path"], g["lsn"], g["size_bytes"])
        for f, g in zip(original["files"], listing["files"], strict=True)
    )
    changed = sorted(
        f["path"]
        for f, g in zip(original["files"], listing["files"], strict=True)
        if f["sha256"] != g["sha256"]
    )
    changes = json.loads((b1 / "changes.json").read_text())["files"]
    expected = sorted(k for k in changes if k.endswith(";1"))
    built = {k: changes[k]["rebuilt_sha256"] for k in expected}
    in_image = {
        g["path"]: g["sha256"] for g in listing["files"] if g["path"] in expected
    }
    builds_same = all(
        (b1 / k.split(";")[0]).read_bytes() == (b2 / k.split(";")[0]).read_bytes()
        for k in expected
    )
    by_file = {
        m["mc_file"]: int(m["slot"]) for m in json.loads(ROSTER.read_text())["roster"]
    }
    slots = sorted(by_file[k] for k in expected if k != "MMPACK.PCA;1")
    patches = patches_v3(slots)
    original_code, base = code(read_file("MMPACK.PCA;1"))
    new_code, new_base = code((b1 / "MMPACK.PCA").read_bytes())
    sites: set[int] = set()
    placed = True
    for address, _, new in patches:
        data = as_bytes(new)
        offset = address - base
        sites.update(range(offset, offset + len(data)))
        placed &= new_code[offset : offset + len(data)] == data
    diff = {i for i in range(len(new_code)) if new_code[i] != original_code[i]}
    summary = {
        "differing_components": differing,
        "source_components_in_manifest": source_ok,
        "built_track_sha256": sha256(built_track),
        "invalid_sectors": len(invalid),
        "same_paths_lsn_size": same_layout,
        "changed_files": changed,
        "changed_files_are_expected": changed == expected,
        "built_files_in_image": built == in_image,
        "b1_equals_b2": builds_same,
        "slots": slots,
        "code_base_same": base == new_base,
        "code_differing_bytes": len(diff),
        "code_diff_inside_patch_sites": diff <= sites,
        "code_patches_in_place": placed,
    }
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    ok = (
        differing == [TRACK.name]
        and source_ok
        and not invalid
        and same_layout
        and changed == expected
        and built == in_image
        and builds_same
        and base == new_base
        and diff <= sites
        and placed
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    )
