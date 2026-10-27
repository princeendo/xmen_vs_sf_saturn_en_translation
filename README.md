# X-Men vs. Street Fighter (Saturn) English Translation

Research tooling and records for an English translation of the Japanese Sega
Saturn release of X-Men vs. Street Fighter (`T-1226G`). The translation will use
Capcom's own English text from the arcade release, not new writing.

This repository contains no game data. Disc images, BIOS files, arcade ROMs,
extracted files, save states, memory dumps and screenshots stay in ignored local
folders. The repository holds scripts, hashes, addresses and research records.

## Status

Setup. Nothing has been confirmed about the game's internals yet. See
`TASKS.md` for the plan and the current state.

## Method

The work follows an empirical reverse-engineering method, defined in
`AGENTS.md` and `docs/research_protocol.md`. It repeats the method of the
completed Marvel Super Heroes vs. Street Fighter (MSHvSF) Saturn translation,
recorded in `docs/playbook_from_mshvsf.md`. No MSHvSF result is assumed to hold
for this game.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
./setup_venv.sh
./invenv.sh pytest
```

## Layout

| Path | Contents |
| --- | --- |
| `AGENTS.md` | Rules for every agent session |
| `TASKS.md` | Dependency-controlled task list |
| `research_log.md` | Chronological record, including failures |
| `docs/` | Confirmed discoveries, known unknowns, protocol, playbook |
| `references/` | Source identities and reference-release notes |
| `research/experiments/` | One folder per significant experiment |
| `tools/`, `tests/` | Python tooling and its tests |
| `local/`, `build/` | Ignored: source images and derived builds |
