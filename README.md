# X-Men vs. Street Fighter (Saturn) English Translation

Research tooling and records for an English translation of the Japanese Sega
Saturn release of X-Men vs. Street Fighter (`T-1226G`). The translation uses
Capcom's own English text from the US arcade release, not new writing.

This repository contains no game data. Disc images, BIOS files, arcade ROMs,
extracted files, save states, memory dumps and screenshots stay in ignored local
folders. The repository holds scripts, hashes, addresses and research records.

## Status

**Win quotes: all 18 characters in English** (milestone M5, complete 2026-10-29).
These are Wolverine, Cyclops, Storm, Rogue, Gambit, Sabretooth, Juggernaut,
Magneto, Apocalypse, Ryu, Ken, Chun-Li, Dhalsim, Zangief, Vega, Gouki, Nash
and Cammy.

- **How:** the Saturn port still contains the arcade's own English quote
  mode, which draws a quote as 2 × 25 characters. A small patch turns it on
  per character, and each character's 8 official English quotes replace the
  start of its Japanese quote table.
- **Which quote:** each Saturn quote shows the English quote the arcade
  shows for the same random draw (record `k` shows English record `k mod 8`).
- **Checks:** every one of the 144 English quotes was drawn in the
  emulator and matched cell for cell. A cold-boot play check showed English
  for player wins, wins finished by the second team member, and CPU wins,
  the boss included. See `docs/discoveries.md` (D-018 to D-027).

**Endings: all 17 playable characters in English** (milestone M8,
2026-10-30). Every character but Apocalypse, the boss.

- **What it shows:** each ending shows the official arcade English in the
  Saturn's own English layout: the arcade's scene breaks and pictures, and
  its speaker labels (for example `Charlie`, `Akuma` and `Bison`).
- **How:** the game already holds an English script for each ending in
  `MCED.SHP`. A small code change (patch version 4) switches each
  character's ending to it, and its English pages sit right after its
  English win quotes.
- **Checks:** every page of all 17 endings was shown in the emulator and
  matched the arcade's English page. A cold-boot play check showed Cammy's
  ending, and Ryu's when he was picked second and the player tagged him
  in. See `docs/discoveries.md` (D-029 to D-042). What M8 leaves is listed
  in `docs/coverage_exceptions.md`.

**Still Japanese:**

- continue-screen hints;
- attract-mode captions.

**"No challengers" sign: the arcade's English** (`NOCH-001`, 2026-10-31).
After Apocalypse, the top-right sign reads `NO CHALLENGERS` in place of
⚠乱入禁止. The game still holds the arcade's English sign (its art, width and
position) and picks it by the region setting; the build reads the region as
US at that one place. The user saw it in play. See `docs/discoveries.md`
(D-055).

**Special cases: Apocalypse's boxes and Alpha Chun-Li** (`SPEC-001` to
`SPEC-005`, 2026-10-31).

- **Apocalypse's boxes:** the three boxes before the boss fight are in
  English, in the win quotes' 2 × 25 layout. There is no official English
  for them (the US arcade skips them), so they are a new translation,
  approved by the user. The second box names the player's character, as
  each name variant spells it.
- **Alpha Chun-Li** (hold Start on Chun-Li): her win quotes, boxes,
  post-boss quote and ending are Chun-Li's official English, as in the
  arcade.
- **Checks:** every box of all 17 roster characters was shown in the
  emulator, and the user played to the boss stage from a cold boot on each
  name variant (Alpha Chun-Li, then Vega). See `docs/discoveries.md`
  (D-052 to D-054).

**Boot warnings: all five in English** (`BOOT-001` to `BOOT-005`,
2026-10-30). The game shows a full-screen warning at boot when the 4 MB RAM
cart is missing (or not working) or when the save memory is unformatted,
damaged or too full. There is no official English for these, so they are a
new translation, approved by the user, drawn in the game's own English quote
font and colours. Each was shown from a cold boot, and the user checked them
on both name variants. See `docs/text_surfaces.md` and `docs/discoveries.md` (D-049 to D-051).

**Character names: two variants** (`LOC-004` to `LOC-007`, 2026-10-30).

- **American (the default):** BISON, AKUMA and CHARLIE on the select
  screen, VS screen, life bars and win banner, and in the spoken name
  calls, as in the US arcade. The game keeps the arcade's own American name
  lists; the build makes the 10 places that pick a name read them. The
  quotes and endings use the arcade English as written ("Bison", "Akuma",
  "Charlie").
- **Saturn names:** the Saturn's own VEGA, GOUKI and NASH in the art and
  voice, and the same names in the English: six lines and five speaker
  labels changed, name only, and Magneto's page 3 speaker labelled
  `Balrog`.
- **Checks:** each variant was played from a cold boot by the user, and
  every edited quote and ending page was shown in the emulator. See
  `docs/names.md` and `docs/discoveries.md` (D-044 to D-048).

**Not released.** No patch has been published yet. Release patches (xdelta
and SSP) are planned once the open tasks are done (`REL-001`).

`TASKS.md` has the full plan. Its "Current State" section is the running
summary, and `research_log.md` holds every session.

## Method

The work follows an empirical reverse-engineering method, defined in
`AGENTS.md` and `docs/research_protocol.md`. It repeats the method of the
completed Marvel Super Heroes vs. Street Fighter (MSHvSF) Saturn translation,
recorded in `docs/playbook_from_mshvsf.md`. No MSHvSF result is assumed to hold
for this game. Every result is confirmed by an experiment under
`research/experiments/`.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
./setup_venv.sh
./invenv.sh pytest
```

## Building the English image (research build)

You need your own copies of the following:

- **The Japanese Saturn disc image** (3M, BIN/CUE). Put it in
  `local/disc_images/xmvsf_saturn_jp_3m/`. Its components must match the
  hashes in `references/saturn_jp/README.md`.
- **The US arcade program** (`xmvsfu`, MAME 0.289 set) in 68000 byte order,
  at `local/ref003/xmvsfu-68k.bin`. The English text is read from it at
  build time, so it is never stored in the repository. Write it from the
  `xmvsfu` ROM zips and MAME 0.289's `cps2.cpp` driver source (SHA-256
  `a8c09ef8…1602`):

  ```bash
  ./invenv.sh python -m tools.reference.xvsf_text --driver local/mame_src/cps2.cpp \
    --set xmvsfu --rompath local/arcade_roms/xmvsf_mame0289 \
    --program-out local/ref003/xmvsfu-68k.bin
  ```

Then one command builds the image under `build/`. The source image is
never modified. The American-names variant (the default):

```bash
./invenv.sh python -m tools.disc.build_english \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,apocalypse,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_win_quotes.json \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_ending.json \
  local/build_us --patch-version 4 --names us --boot-warnings --special \
  --no-challengers --image build/names_us
```

The Saturn-names variant: the same specs, with
`local/build_saturn --patch-version 4 --names saturn --boot-warnings --special --no-challengers --image build/names_saturn`.

The expected hashes are in `data/regression/references.json`: Track 01
`6820f12d…` (American, `no_challengers_us_v4`) and `57c397ea…` (Saturn
names, `no_challengers_saturn_v4`). Without `--no-challengers` the sign
stays Japanese (`5d1f76e4…`, `special_us_v4`; `a4e3e98e…`,
`special_saturn_v4`). Without `--special` too, Apocalypse's boxes and Alpha
Chun-Li stay as before (`e8c9cc4f…`, `boot_warnings_us_v4`; `f53d2378…`,
`boot_warnings_saturn_v4`). Without `--boot-warnings` too, the boot warnings stay
Japanese (`441c9cfc…`, `names_us_v4`; `b11c8cd9…`, `names_saturn_v4`). `--names none` leaves the names as the Saturn has them
and reproduces the earlier builds: with every ending, Track 01 `7bb8ab82…`
(M8); without the `_ending.json` specs and `--patch-version 4`, the win
quotes alone (`36672c5d…`). To rebuild every confirmed build and check its hashes, run
`./invenv.sh python -m tools.disc.regression`. The last run is in
`docs/regression_report.md`. The image needs the 4 MB RAM cartridge (in Mednafen,
`ss.cart auto`); see `docs/mednafen.md`.

## Layout

| Path | Contents |
| --- | --- |
| `AGENTS.md` | Rules for every agent session |
| `TASKS.md` | Dependency-controlled task list and current state |
| `research_log.md` | Chronological record, including failures |
| `docs/discoveries.md` | Confirmed findings, each with evidence and reproduction |
| `docs/known_unknowns.md` | Open questions and the experiments that would answer them |
| `docs/localization_policy.md` | The user's translation decisions (source, names, gates) |
| `docs/coverage_exceptions.md` | What the win-quote build deliberately leaves alone |
| `docs/` (other) | Protocol, playbook, text surfaces, names, Mednafen notes |
| `data/translations/` | Per-character specs and pairing tables (addresses and hashes, no text) |
| `data/text/` | Quote-file census, roster, capacity results |
| `data/regression/` | Expected hashes of every confirmed build |
| `references/` | Source identities and reference-release notes |
| `research/experiments/` | One folder per significant experiment |
| `tools/`, `tests/` | Python tooling and its tests |
| `local/`, `build/` | Ignored: source images, evidence and derived builds |
