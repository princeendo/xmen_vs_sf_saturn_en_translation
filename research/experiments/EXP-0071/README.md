# EXP-0071 (Release): Patches and Zips for the Toggle Build

Task: REL-001
Status: IN_PROGRESS (tools and a trial run done; publishing waits for the
open tasks, by the user's choice)
Confidence: CONFIRMED for the trial patches and zips below

## Choices (the user's, `docs/localization_policy.md`)

xdelta and SSP; version 0.1.0; the toggle build only (`name_toggle_v4`);
the open tasks done before publishing.

## Tools (copied with provenance, rule 26)

| File | From MSHvSF (commit) | Changed |
| --- | --- | --- |
| `tools/disc/make_patch.py` | `tools/disc/make_patch.py` (`5e8d4ec`) | source folder, manifest, baseline, track 01 name |
| `tools/disc/make_ssp.py` | `tools/disc/make_ssp.py` (`5e8d4ec`) | author, URL, title, apply text |
| `tests/unit/test_disc_make_patch.py`, `tests/unit/test_make_ssp.py` | same paths (`5e8d4ec`) | one track name |
| `make_zips.py`, `check_zips.sh` | `research/experiments/EXP-0102/` (`7d4c587`) | one build; XvSF's names, tracks (02-41) and repository |

## Trial Run (2026-11-01, `build/loc010_toggle`, Track 01 `68813e93…`)

- **xdelta** (`make_patch`, xdelta3 3.2.2, `-e -9 -S none -A -W 16777216
  -f`): only track 01 differs; `xmvsf_saturn_en_toggle.Track01.xdelta`,
  4,007,441 bytes, `8005c1b8…`; encoded twice identically; decoded to the
  reference. Record: `release/name_toggle.json`.
- **SSP** (`make_ssp`): `xmvsf_saturn_en_toggle.ssp`, 4,872,268 bytes,
  `2772e3d7…`, 35 changed files; built twice identically; applied by the
  tool's own applier to the reference. Record: `release/name_toggle.ssp.json`.
  **Second patcher** (the user approved the download): `saturn-patcher-egui`
  (<https://github.com/ralfguth/saturn-patcher-egui>, GPL-3.0, commit
  `20837e06…` of 2026-06-22, the one MSHvSF verified), cloned into the
  ignored `local/tools_ext/` and built with `cargo build --release --bin
  saturn-patcher` (cargo 1.99.1, 17 s). Applied from the unpacked zip to a
  copy of the untouched track 01: each source file's MD5 checked, 35 files
  written back with EDC/ECC regenerated, result `68813e93…`, the reference.
- **Zips** (`make_zips.py 0.1.0`, twice): `xmvsf_saturn_en_0.1.0_xdelta.zip`
  `8de3a7e6…` (3,852,177 bytes) and `xmvsf_saturn_en_0.1.0_ssp.zip`
  `7347d30e…` (4,872,893 bytes), identical both times. `check_zips.sh`:
  both patches from the unpacked zips give track 01 `68813e93…`.

The patch sizes (about 4 MB) come from the re-compressed files (fighter
files, `MMPACK.PCA`, the eight `OPENING*.ST2`); MSHvSF's splicing was not
needed for a usable size.

## Release Documents

`release/README.md` (what changes, how to apply each format, how to
rebuild), `release/RELEASING.md` (the steps, adapted from MSHvSF's at
`7d4c587`), `release/notes_v0.1.0.md`. Every open task was settled the same
day (`ENV-007`, `DOC-003`, `UI-005`, `TXT-001`), so the trial build is the
release build: its zips above are the 0.1.0 assets unless a rebuild
differs.

## Still To Do

The tag, your publication on github.com, and the asset-hash check through
the public API.

## Reproduction

```bash
./invenv.sh python -m tools.disc.make_patch --built-dir build/loc010_toggle \
  --reference name_toggle_v4 --stem xmvsf_saturn_en_toggle \
  --out-dir build/release/toggle --record release/name_toggle.json
./invenv.sh python -m tools.disc.make_ssp --built-dir build/loc010_toggle \
  --reference name_toggle_v4 --stem xmvsf_saturn_en_toggle --release-version 0.1.0 \
  --description "English win quotes, endings, captions, hints and UI; American or Saturn names, chosen in Options (NAMES)." \
  --out-dir build/release/toggle --record release/name_toggle.ssp.json
./invenv.sh python research/experiments/EXP-0071/make_zips.py 0.1.0 build/release/v0.1.0
bash research/experiments/EXP-0071/check_zips.sh 0.1.0 build/release/v0.1.0 local/rel/v0.1.0-check
```
