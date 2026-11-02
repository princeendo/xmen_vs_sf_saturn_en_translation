"""REL-001: zip the release patches, one zip per format, each with a readme.

Copied from the MSHvSF repository, ``research/experiments/EXP-0102/make_zips.py``
at commit ``7d4c587`` (its REL-004), for XvSF's ``REL-001``. Changed: one
build (the toggle, ``name_toggle_v4``; the user's choice), and XvSF's names,
tracks and repository.

Reads the committed release records for hashes and the built patches from
build/release/. Zip members get a fixed timestamp, so the zips are reproducible.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0071/make_zips.py VERSION OUT
"""

import json
import sys
import zipfile
from pathlib import Path

VERSION = sys.argv[1]
OUT = Path(sys.argv[2])
VARIANTS = (  # (record stem, build dir, label)
    (
        "name_toggle",
        "toggle",
        "One image: American or Saturn names, chosen in Options (NAMES)",
    ),
)
TRACK = "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
REPO = "https://github.com/princeendo/xmen_vs_sf_saturn_en_translation"
STAMP = (2026, 11, 1, 0, 0, 0)
APPLY = {
    "xdelta": [
        f'xdelta3 -d -s "{TRACK}" \\',
        '  <patch>.Track01.xdelta "Track 01 patched.bin"',
    ],
    "ssp": [
        'saturn-patcher <patch>.ssp "Track 01 patched.bin"',
        "(saturn-patcher-egui). The official Sega Saturn Patcher rebuilds the",
        "disc instead: its track 01 differs only in the disc-length field.",
    ],
}


def add(bundle: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, STAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    bundle.writestr(info, data)


def readme(kind: str, rows: list[str], source: str) -> str:
    return "\n".join(
        [
            f"X-Men vs. Street Fighter (Saturn) English {VERSION}",
            f"({kind} patches)",
            "",
            'For the Japanese Saturn image "X-Men vs. Street Fighter (Japan) (3M)".',
            "Only track 01 changes; keep tracks 02-41 and the CUE sheet.",
            "",
            "Untouched track 01 SHA-256:",
            f"  {source}",
            "",
            *rows,
            "Apply:",
            *(f"  {line}" for line in APPLY[kind]),
            "Then put the patched file in place of track 01, under the same name.",
            "",
            "Full instructions, the change list and known limits:",
            f"  {REPO}/blob/main/release/README.md",
            "",
        ]
    )


OUT.mkdir(parents=True, exist_ok=True)
for kind in ("xdelta", "ssp"):
    rows, files, sources = [], [], set()
    for stem, build, label in VARIANTS:
        suffix = ".ssp.json" if kind == "ssp" else ".json"
        record = json.loads(Path(f"release/{stem}{suffix}").read_text())
        patch = record["patches"][0] if kind == "xdelta" else record
        sources.add(patch["source_sha256"])
        path = Path("build/release", build, patch["patch"])
        assert path.stat().st_size == patch["patch_size"], path
        rows += [
            label,
            f"  {patch['patch']} ({patch['patch_size']:,} bytes)",
            f"  file SHA-256:     {patch['patch_sha256']}",
            f"  patched track 01: {patch['target_sha256']}",
            "",
        ]
        files.append(path)
    assert len(sources) == 1
    name = OUT / f"xmvsf_saturn_en_{VERSION}_{kind}.zip"
    with zipfile.ZipFile(name, "w") as bundle:
        add(bundle, "README.txt", readme(kind, rows, sources.pop()).encode())
        for path in files:
            add(bundle, path.name, path.read_bytes())
    print(name)
