# X-Men vs. Street Fighter (Saturn): English Translation

This repository builds an English patch for the Japanese Sega Saturn release of
**X-Men vs. Street Fighter** (XvSF). Wherever an official English text exists,
the patch uses it: the US arcade release's English. Where none exists, it uses
a new translation, marked as such.

The repository holds the tools, the translation data, and the expected hashes.
It holds no game data. The ready-made patches are on the
[releases page](#download). You can also build them yourself from your own
disc image (see [Build the Patch](#build-the-patch)). How the work was done is
recorded in [TASKS.md](TASKS.md), [research_log.md](research_log.md), and
`research/experiments/`.

## Download

The latest release is
[0.1.0](https://github.com/princeendo/xmen_vs_sf_saturn_en_translation/releases/tag/v0.1.0):

- [xmvsf_saturn_en_0.1.0_xdelta.zip](https://github.com/princeendo/xmen_vs_sf_saturn_en_translation/releases/download/v0.1.0/xmvsf_saturn_en_0.1.0_xdelta.zip):
  an xdelta patch for track 01;
- [xmvsf_saturn_en_0.1.0_ssp.zip](https://github.com/princeendo/xmen_vs_sf_saturn_en_translation/releases/download/v0.1.0/xmvsf_saturn_en_0.1.0_ssp.zip):
  the same patch as a Sega Saturn Patcher (`.ssp`) file.

Each zip holds one patch and a `README.txt` with every expected hash. One
image serves both name variants: you choose the names in Options (see
"Names" below). You supply your own Japanese disc image. To apply a patch, see
[Applying a Patch](#applying-a-patch).

The game needs the **4 MB RAM cartridge** (拡張ラムカートリッジ4MB), on a
real Saturn or in an emulator (Mednafen: `ss.cart auto`). Without it, the
game stops at boot on a warning page, which the patch shows in English.

## What's Changed

- **Win quotes in English:** all 8 win quotes of each of the 18 characters
  (Apocalypse, the boss, included), in the US arcade's official English. Each
  Saturn quote shows the English quote the arcade shows for the same random
  draw.
- **Endings in English:** the ending of each of the 17 playable characters,
  in the US arcade's official English. The Saturn already holds an English
  layout for each ending (the arcade's scene breaks, pictures and speaker
  labels), and the patch switches to it.
- **Apocalypse's boxes:** the three text boxes before the boss fight. The US
  arcade skips them, so they are a new translation. The second box names your
  character, spelled as the chosen name variant spells it.
- **Alpha Chun-Li** (hold Start on Chun-Li): her win quotes, boxes and ending
  are Chun-Li's official English, as in the arcade.
- **Attract mode:** the four captions in the attract loop are the US arcade's
  English art, and the flash before the third reads TO EXECUTE. "UNCCANY" is
  respelled UNCANNY from the arcade's own letters.
- **CONTINUE? hints:** the tip under the countdown is the US arcade's
  English, on two pages, with the game's own joystick arrows.
- **"No challengers" sign:** after Apocalypse, the top-right sign reads
  `NO CHALLENGERS` instead of ⚠乱入禁止, from the arcade's English sign
  that the game still holds.
- **Boot warnings:** the five warnings shown at boot (the 4 MB RAM cartridge
  missing or not working; the save memory unformatted, damaged or full) are a
  new translation, in the game's own English quote font.
- **Names:** a NAMES row in Options picks the variant, and BACK UP: SAVE keeps
  the choice like the game's other settings.
  - **U.S.** (the default): BISON, AKUMA and CHARLIE, as in the US arcade.
  - **SATURN:** the Saturn's own VEGA, GOUKI and NASH. The English text uses
    the same names (six lines and five speaker labels change, name only).

  The choice applies on the select screen, VS screen, life bars, win
  banners, spoken name calls, the quotes and the ending labels.
- **COMBO GAUGE:** the game's hidden COMBO GAGE option (a full super gauge,
  shown only when the game unlocks it) is kept, as an eleventh Options row
  spelled COMBO GAUGE.

**Not changed:** the menus that are already English, the voices (apart from
the name calls), and one Japanese trademark line in the QSound notice after
the credits (its English is on the same screen). Versus mode beyond its
select screen was not surveyed. The full list is in
[docs/coverage_exceptions.md](docs/coverage_exceptions.md).

Only track 01 of the disc changes; tracks 02-41 (audio) and the CUE sheet stay
as they are. The full list, with evidence for each item, is in
[release/README.md](release/README.md#what-the-patch-changes).

## Patch Files

The release zips ([Download](#download)) hold these files. They are GitHub
Release assets only and are never committed to the repository (`AGENTS.md`
rule 21). You can also build them yourself (the next section). The two
formats give the same patched track 01:

| xdelta file | Sega Saturn Patcher file | Patched track 01 SHA-256 |
| --- | --- | --- |
| `xmvsf_saturn_en_toggle.Track01.xdelta` | `xmvsf_saturn_en_toggle.ssp` | `68813e93108f433a9b64e4b2e420baebbabb136634c2b927b938f56addf9ad1a` |

The `.ssp` hash holds when an in-place applier such as
[saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui) applies
it. The official Sega Saturn Patcher rebuilds the disc; it has not been tried
with this game. For MSHvSF its track 01 differed in the disc-length field, so
expect the hash not to match.

### Applying a Patch

These patch files cannot be applied by anything in this repository; use one
of the tools below. Either way, patch an untouched copy of the image, never
one already patched. The project tests the result in Mednafen with the 4 MB
RAM cartridge; it has not been reported on a real Saturn.

| Tool | Patch file | Platforms | Tested here | How-to |
| --- | --- | --- | --- | --- |
| [xdelta3](https://github.com/jmacd/xdelta) (command line) | `.xdelta` | macOS (`brew install xdelta`), Linux, Windows ([releases](https://github.com/jmacd/xdelta-gpl/releases)) | yes, 3.2.2 | the command below |
| [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) | `.xdelta` | any web browser; nothing to install | no | choose the track 01 `.bin` as the ROM file, the patch as the patch file, then "Apply patch" ([source and help](https://github.com/marcrobledo/RomPatcher.js)) |
| [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher) | `.xdelta` | Windows, macOS, Linux ([releases](https://github.com/marco-calautti/DeltaPatcher/releases)) | no | choose the track 01 `.bin` as the original file, the patch as the xdelta patch, then "Apply patch" |
| [saturn-patcher-egui](https://github.com/ralfguth/saturn-patcher-egui) | `.ssp` | Windows, Linux ([releases](https://github.com/ralfguth/saturn-patcher-egui/releases)); macOS by building from source | yes, commit `20837e0` | `saturn-patcher PATCH.ssp "Track 01 copy.bin"` patches the copy in place ([README](https://github.com/ralfguth/saturn-patcher-egui#usage)) |
| [Sega Saturn Patcher](https://segaxtreme.net/resources/sega-saturn-patcher.73/) (Knight0fDragon) | `.ssp` | Windows; needs the [.NET 5 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/5.0) | no | "Select Saturn Game" → "CD Image" (the `.cue`), "+ Game Patch (SSP)", then "Patch Image"; it writes a new image |

With xdelta3:

```bash
xdelta3 -d -s "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" \
  xmvsf_saturn_en_toggle.Track01.xdelta "Track 01 patched.bin"
```

**After any of the xdelta tools or saturn-patcher-egui:**
1. Check the patched track's SHA-256 against the table above.
2. Put it in place of track 01 under its original filename.
3. Keep tracks 02-41 and the CUE as they are.

Sega Saturn Patcher instead writes a complete new image (CUE and tracks):
load that.

The full steps, hashes, and what the patch changes are in
[release/README.md](release/README.md#apply-the-patch).

## Build the Patch

### Files You Need

None of these are in the repository. Put them at these paths (all ignored by
git):

| File | Where it goes | What it is |
| --- | --- | --- |
| `X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin` to `… (Track 41).bin` and `X-Men vs. Street Fighter (Japan) (3M).cue` | `local/disc_images/xmvsf_saturn_jp_3m/` | The Japanese Saturn disc as BIN/CUE: the data track, 40 audio tracks, and the CUE sheet. It is Redump disc 62395; the cart-bundle discs 1745 and 62394 have the same track 01. Every file must match the SHA-256 values in [references/saturn_jp/README.md](references/saturn_jp/README.md); track 01 is `c904a386…da70` (169,127,616 bytes). |
| `xmvsfu.zip` and its parent set `xmvsf.zip` | `local/arcade_roms/xmvsf_mame0289/` | The MAME 0.289 sets for the US arcade release (USA 961023) and its parent. The official English is read from them once, into the program image below. Identities in [references/arcade/README.md](references/arcade/README.md). |
| `cps2.cpp` | `local/mame_src/` | MAME's public CPS-II driver source at commit `f34f02505e32c1993c6a782b6814232cbfc74e36` (SHA-256 `a8c09ef8…1602`). It describes the arcade ROM layout. Downloaded by a command below. |
| `xmvsfu-68k.bin` | `local/ref003/` | The arcade's 68000 program, written from the two above by a command below. |
| the arcade caption art | `local/cap002/art/` | The US arcade's attract captions, cut from MAME `xmvsfu` snapshots, as described in [EXP-0065's README](research/experiments/EXP-0065/README.md#the-arcade-art) ("The Arcade Art"). |

### Set Up

- [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer (uv can install
  Python).
- xdelta3. The recorded patch was made with 3.2.2 (`brew install xdelta` on
  macOS); another version may give a different patch file, but the same
  patched track.

```bash
./setup_venv.sh
mkdir -p local/mame_src
curl -sSfLo local/mame_src/cps2.cpp https://raw.githubusercontent.com/mamedev/mame/f34f02505e32c1993c6a782b6814232cbfc74e36/src/mame/capcom/cps2.cpp
./invenv.sh python -m tools.reference.xvsf_text --driver local/mame_src/cps2.cpp \
  --set xmvsfu --rompath local/arcade_roms/xmvsf_mame0289 \
  --program-out local/ref003/xmvsfu-68k.bin
```

### Build the Release Patches

```bash
# 1. Build the release image from the untouched disc and check its hashes.
./invenv.sh python -m tools.disc.regression --keep --only name_toggle_v4

# 2. Make the patch from the image (checked against its reference).
./invenv.sh python -m tools.disc.make_patch \
  --built-dir build/regression/name_toggle_v4/image --reference name_toggle_v4 \
  --stem xmvsf_saturn_en_toggle --out-dir build/release/toggle

# 3. The same patch as a Sega Saturn Patcher (.ssp) file (no extra tool needed).
./invenv.sh python -m tools.disc.make_ssp \
  --built-dir build/regression/name_toggle_v4/image --reference name_toggle_v4 \
  --stem xmvsf_saturn_en_toggle --release-version 0.1.0 \
  --description "English win quotes, endings, captions, hints and UI; American or Saturn names, chosen in Options (NAMES)." \
  --out-dir build/release/toggle
```

The patches are written to `build/release/toggle/`. Step 1 stops if any hash
differs from the recorded one. Leave out `--only …` to rebuild all 18
regression references (the last run is in
[docs/regression_report.md](docs/regression_report.md)). The full procedure,
with expected hashes and the release zips, is in
[release/README.md](release/README.md#rebuild-the-patch-from-this-repository).

### Build Options

The images are built by `tools.disc.build_english`, from the per-character
specs in `data/translations/` and the options below.
[data/regression/references.json](data/regression/references.json) lists each
reference image's exact specs and options.

| Option | What it does | Release image |
| --- | --- | --- |
| `SPEC … OUT` | The win-quote specs (`*_win_quotes.json`) and ending specs (`*_ending.json`) to build, then the folder for the built files. | all 18 win-quote and 17 ending specs |
| `--patch-version 2` / `3` / `4` | The code patch that turns on the English modes. Endings need 4; 3 is the default. | `4` |
| `--names us` / `saturn` / `toggle` / `none` | American names (the default), Saturn names, both with the NAMES row in Options, or the names as the Saturn has them (the earliest builds). | `toggle` |
| `--boot-warnings` | The five boot warnings in English (new translation). | on |
| `--special` | Apocalypse's boxes (new translation) and Alpha Chun-Li's English. Needs `--patch-version 4` and Apocalypse's win-quote spec. | on |
| `--no-challengers` | The arcade's NO CHALLENGERS sign. | on |
| `--attract-captions DIR` | The arcade's attract captions, from the art in `DIR` (`local/cap002/art`). | on |
| `--continue-hints` | The arcade's CONTINUE? hints. | on |
| `--fix-grammar` | Applies the specs' opt-in grammar fixes to the official English. None are written yet, so it changes nothing. | off |
| `--program PATH` | The arcade program image (default `local/ref003/xmvsfu-68k.bin`). | default |
| `--image DIR` | Also builds the full disc image in `DIR`. | on |

To build an image of your own, such as fixed American names without the
Options row:

```bash
./invenv.sh python -m tools.disc.build_english \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,apocalypse,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_win_quotes.json \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_ending.json \
  local/build_us --patch-version 4 --names us --boot-warnings --special \
  --no-challengers --attract-captions local/cap002/art --continue-hints \
  --image build/names_us
./invenv.sh python -m tools.disc.make_patch --built-dir build/names_us \
  --stem xmvsf_saturn_en_custom --out-dir build/release/custom
```

This one is the regression reference `continue_hints_us_v4` (track 01
`84b1dd22…`); with `--names saturn` it is `continue_hints_saturn_v4`
(`94dcd067…`). Pass `--reference NAME` to `make_patch` to check an image
against a recorded reference. A custom image has none, and `make_patch`'s
other checks still run.

## Development

### Further Files for Research

Building the patch needs only the files above. The research tools also read
these, at these paths (all ignored by git):

| File | Where it goes | What it is |
| --- | --- | --- |
| the other `xmvsf*` arcade sets, their keys, and `qsound.zip` | `local/arcade_roms/xmvsf/` and `local/arcade_roms/xmvsf_mame0289/` | The other regions, used to check how text pairs across releases, and what MAME needs to run the arcade game. Identities in [references/arcade/README.md](references/arcade/README.md). |
| the PlayStation releases (US, and the Japanese EX Edition) | `local/disc_images/xmvsf_ps1_us/`, `local/disc_images/xmvsf_ps1_jp_ex/` | Secondary references. Identities in [references/ps1/README.md](references/ps1/README.md). |
| `sega_101.bin` (and `mpr-17933.bin`) | `local/mednafen/firmware/` | The Saturn BIOS (Japanese 1.01; North American/European) for Mednafen. Hashes in [docs/mednafen.md](docs/mednafen.md#saturn-bios). |
| `mednafen-1.32.1.tar.xz` | extracted to `vendor/mednafen/src/` | Mednafen's source. The project builds it with an agent-interface patch, which lets the tools drive the emulator; see [vendor/mednafen/README.md](vendor/mednafen/README.md). |

### Python Tooling

Run every Python command through `./invenv.sh`, without activating a virtual
environment:

```bash
./invenv.sh pytest
./invenv.sh ruff check .
./invenv.sh ruff format --check .
./invenv.sh mypy tools
```

Record a source image's identity before research:

```bash
./invenv.sh python -m tools.disc.hash_source \
  --description "XvSF Saturn JP, local source" \
  --json /path/to/source-image.cue
```

### Method

The work follows an empirical reverse-engineering method, defined in
[AGENTS.md](AGENTS.md) and [docs/research_protocol.md](docs/research_protocol.md).
It repeats the method of the completed
[MSHvSF Saturn translation](https://github.com/princeendo/msh_vs_sf_saturn_en_translation),
recorded in [docs/playbook_from_mshvsf.md](docs/playbook_from_mshvsf.md). No
MSHvSF result is assumed to hold for this game: every result is confirmed by
an experiment under `research/experiments/` and recorded in
[docs/discoveries.md](docs/discoveries.md).

### Local Data

Keep original images outside the repository or under an ignored path such as
`local/disc_images/`, and treat them as read-only. Generated images go only in
`build/`. Mednafen's runtime configuration belongs in the ignored
`local/mednafen/`; its provenance and setup are in
[docs/mednafen.md](docs/mednafen.md) and
[vendor/mednafen/README.md](vendor/mednafen/README.md).

Research records are kept by purpose:

- `research/experiments/`: one directory per significant experiment;
- `data/translations/`: per-character specs and pairing tables (addresses
  and hashes, no text);
- `data/text/`: the quote-file census, roster and capacity results;
- `data/regression/`: the expected hashes of every confirmed build;
- `references/`: source identities and reference-release notes;
- `docs/discoveries.md`: confirmed durable findings only;
- `docs/known_unknowns.md`: unresolved questions;
- `research_log.md`: chronological successes and failures.

### Project Guides

- [AGENTS.md](AGENTS.md): authoritative operating rules
- [TASKS.md](TASKS.md): dependency-controlled research plan; its "Current State" is the running summary
- [research_log.md](research_log.md): chronological journal
- [docs/research_protocol.md](docs/research_protocol.md): experiment protocol
- [docs/playbook_from_mshvsf.md](docs/playbook_from_mshvsf.md): the method carried over from MSHvSF
- [docs/localization_policy.md](docs/localization_policy.md): the user's translation decisions
- [docs/text_surfaces.md](docs/text_surfaces.md) and [docs/names.md](docs/names.md): where text and names appear
- [docs/coverage_exceptions.md](docs/coverage_exceptions.md): what the build deliberately leaves alone
- [docs/references.md](docs/references.md): source bibliography and evidence rules
- [docs/mednafen.md](docs/mednafen.md): the emulator setup
- [release/RELEASING.md](release/RELEASING.md): how to make and publish a release
