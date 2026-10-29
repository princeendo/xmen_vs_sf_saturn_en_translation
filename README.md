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

**Still Japanese:**

- endings;
- continue-screen hints;
- attract-mode captions;
- Apocalypse's pre-fight line;
- the 4 MB RAM cart warning;
- the ending text stored in each quote file.

Character names on screen still follow the Saturn (Japanese) convention, for
example GOUKI and NASH. The quotes use the arcade English as written.

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
never modified.

```bash
./invenv.sh python -m tools.disc.build_english \
  data/translations/{wolverine,cyclops,storm,rogue,gambit,sabretooth,juggernaut,magneto,apocalypse,ryu,ken,chun_li,dhalsim,zangief,vega,gouki,nash,cammy}_win_quotes.json \
  local/build_files --image build/roster_english
```

The expected hashes are in `data/regression/references.json` (Track 01
`36672c5d…`). To rebuild every confirmed build and check its hashes, run
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
