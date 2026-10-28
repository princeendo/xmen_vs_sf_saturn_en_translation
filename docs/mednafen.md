# Mednafen

Stock Mednafen first (`AGENTS.md` rule 16). The agent-interface patch from
MSHvSF may be reused only after `EMU-004` and `EMU-020`.

## Selected Stock Release (`EMU-001`, 2026-10-28)

Mednafen `1.32.1`, the release MSHvSF used (MSHvSF `EMU-001`), so the MSHvSF
agent-interface patch can apply unchanged.

- Upstream project: <https://mednafen.github.io/>; releases:
  <https://mednafen.github.io/releases/>.
- Source archive URL:
  <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Retrieved 2026-10-28 19:12 UTC with `curl -fsSL` (curl 8.7.1), with the
  user's approval, into the new, ignored `local/downloads/mednafen-1.32.1/`.
- Archive: `mednafen-1.32.1.tar.xz`, 3,571,236 bytes, SHA-256
  `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`. This
  equals the size and hash MSHvSF recorded for its 2026-08-24 download.
- License: GNU GPL version 2 (`COPYING` in the archive).

The archive's single top-level folder `mednafen/` was extracted with
`bsdtar -xf` and renamed to the ignored `vendor/mednafen/src/`. It is not
modified.

## Exact Stock Build

Host: macOS 26.7.1 (25G241), Darwin 25.6.0 arm64, Apple clang 21.0.0
(clang-2100.3.34.2), GNU Make 3.81, `pkg-config` 3.0.10, Homebrew 7.0.11,
SDL2 2.32.74, libFLAC 1.5.0, zlib 1.2.12. These build dependencies were
already installed on this host; nothing was installed for this task.

From the ignored `vendor/mednafen/build/`:

```bash
PKG_CONFIG=/opt/homebrew/bin/pkg-config \
CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

Both exited 0. Logs: ignored `local/logs/emu001-configure.log` and
`local/logs/emu001-make.log`.

Binary: `vendor/mednafen/build/src/mednafen`, Mach-O 64-bit arm64, 21,328,328
bytes, SHA-256
`892bb60a1aed0c2478142bc9da528deb09cd4b498b001047a030a65c845929dd`. It differs
from the MSHvSF stock binary (`ca9bec5f…2587`), which was built from the same
archive on an older host (macOS 26.5.2, SDL2 2.32.70); a byte-identical binary
is not expected across toolchains.

## `-help` Banner

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" vendor/mednafen/build/src/mednafen -help
```

Output (ignored `local/logs/emu001-help.log`) begins:

```text
Starting Mednafen 1.32.1
 Build information:
   Compiled with gcc Apple LLVM 21.0.0 (clang-2100.3.34.2)
   Compiled against zlib 1.2.12, running with zlib 1.2.12(flags=0x000002a9)
   Compiled against libiconv 11.1, running with libiconv 11.1
   Compiled against SDL 2.32.74(SDL-release-2.32.74-0-ge4df8a5), running with SDL 2.32.74(SDL-2.32.74-no-vcs)
   Running with libFLAC 1.5.0
 Emulation modules: apple2 nes snes gb gba pce lynx md pcfx ngp psx ss ssfplay vb wswan sms gg sasplay snes_faust pce_fast demo cdplay
```

The Saturn module `ss` is present. The process prints the usage text and exits
with status 255. The MSHvSF stock binary exits 255 for the same command with a
fresh `MEDNAFEN_HOME`, so this is how 1.32.1 handles `-help`, not a build
fault. The first run created a default `local/mednafen/mednafen.cfg`; project
settings are `EMU-002`'s work.
