# Mednafen Vendor Area

The stock Mednafen 1.32.1 source and build stay unmodified in the ignored
`vendor/mednafen/src/` and `vendor/mednafen/build/` (`EMU-001`,
`docs/mednafen.md`). Do not commit source archives, binaries, runtime state,
BIOS files, or game data.

## Agent-Interface Patch (`EMU-021`)

- `patches/0001-agent-interface.patch`, SHA-256
  `c30146efab0cb60bfb7a4465bc95d9935c63c0d7bf172b02f886b4ae2cff5244`, 592
  lines, against 1.32.1. Copied unchanged from the MSHvSF repository
  (`vendor/mednafen/patches/0001-agent-interface.patch`, added in MSHvSF
  commit `b9a6593`; unchanged at `69c666c`). GPL-2.0, like Mednafen.
- Frontend only: adds `src/drivers/agent.inc` and hooks in
  `src/drivers/debugger.cpp`, `debugger.h`, and `main.cpp`. The Saturn core is
  unchanged. Active only when `MEDNAFEN_AGENT_DIR` is set.
- Reuse authorized by the user's `DOC-002` answer (2026-10-27) and
  `AGENTS.md` rule 16, after `EMU-004` and `EMU-020`
  (`docs/mednafen_agent_interface.md`).

Build, from the repository root, with the stock source already extracted:

```bash
cp -R vendor/mednafen/src vendor/mednafen/src-agent
patch -d vendor/mednafen/src-agent -p1 < vendor/mednafen/patches/0001-agent-interface.patch
mkdir -p vendor/mednafen/build-agent && cd vendor/mednafen/build-agent
PKG_CONFIG=/opt/homebrew/bin/pkg-config CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src-agent/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

Run, from the repository root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen_quiet" MEDNAFEN_AGENT_DIR="$PWD/local/RUN/agent" \
  vendor/mednafen/build-agent/src/mednafen \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
```

The client is `tools/mednafen/agent.py`. Validation on XvSF is in
`research/experiments/EXP-0006/README.md`.
