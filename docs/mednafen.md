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

## Project-Local Configuration (`EMU-002`, 2026-10-28)

Mednafen never reads the user's global configuration here: every run sets
`MEDNAFEN_HOME` to an ignored folder in this checkout.

| Home | Use |
| --- | --- |
| `local/mednafen/` | Interactive runs (the user plays, hears the game). |
| `local/mednafen_quiet/` | Unattended runs: `sound.volume 0`, `video.glvsync 0`, `video.blit_timesync 0`; `firmware/` is a symlink to `../mednafen/firmware`; own `sav/` and `mcs/`. |

The silent home follows the user's DOC-002 answer "Silent unattended runs".
Sound stays enabled at volume 0, so emulation timing is unchanged. MSHvSF
found that, with vsync on, emulation stalls while the display sleeps (MSHvSF
`docs/mednafen.md`, 2026-10-27). That is a **HYPOTHESIS** here until an
unattended XvSF run shows it.

Each configuration is the file Mednafen 1.32.1 generated on its first run
(`-help` with that home), then pinned by:

```bash
./invenv.sh python -m tools.mednafen.home
```

`tools/mednafen/home.py` rewrites only existing `key value` lines and fails
on a key that has no line. It creates the quiet home from the interactive
one if it is missing. Mednafen saves command-line settings into the
configuration on exit, so rerun the tool after any run that passed settings
on the command line. A second run reports `no change` for both homes.

Pinned settings (both homes):

| Setting | Value | Purpose |
| --- | --- | --- |
| `filesys.path_firmware` | `firmware` | BIOS files below the home. |
| `filesys.path_sav` | `sav` | Saturn backup RAM. |
| `filesys.path_savbackup` | `b` | Backup-RAM backups. |
| `filesys.path_state` | `mcs` | Save states. |
| `filesys.path_snap` | `snaps` | Screenshots. |
| `filesys.path_movie` | `mcm` | Movies. |
| `filesys.path_pgconfig` | `pgconfig` | Per-game overrides. |
| `filesys.path_cheat` | `cheats` | Cheats. |
| `filesys.fname_state` | `%f.%M%X` | Stable state filenames. |
| `filesys.fname_snap` | `%f-%p.%x` | Stable screenshot filenames. |
| `autosave` | `0` | No implicit state at load or exit. |
| `debugger.autostepmode` | `0` | No debugger step mode at launch. |
| `ss.bios_jp` | `sega_101.bin` | Japanese BIOS. |
| `ss.bios_na_eu` | `mpr-17933.bin` | North American/European BIOS. |
| `ss.bios_sanity` | `1` | BIOS sanity checks on. |
| `ss.cart` | `auto` | Cart chosen by Mednafen's database (see below). |
| `ss.region_autodetect` | `1` | Region taken from the disc. |

All 17 values equal the 1.32.1 defaults, so pinning changed nothing in the
interactive home. Pinning them guards against settings saved from a
command-line run. `ss.cart auto`: Mednafen 1.32.1's `src/ss/db.cpp` lists
`T-1226G`, "X-Men vs. Street Fighter (Japan)", as `CART_EXTRAM_4M`, "Game
requirement". That the running game gets the 4 MiB cart is `EMU-004`'s test.
Pad bindings are not set yet (`EMU-005`).

Result: with each home, `-help` reports `Base directory:` that home and
`Loaded 7904 valid settings and 0 unknown settings`, and both files' SHA-256
are unchanged afterwards:

| File | Size | SHA-256 |
| --- | ---: | --- |
| `local/mednafen/mednafen.cfg` | 652,752 | `48a7cf6b03224ab6fc485965ec13a0a9d657f678b3f187d3791469686ab228fc` |
| `local/mednafen_quiet/mednafen.cfg` | 652,750 | `ef89728844860b8334411d3bbd6195b84828956c5e446744efdc9e59ea305019` |

`diff` between the two shows only the three quiet settings.

### Saturn BIOS

Copied unchanged (`cp -p`, `cmp` clean) from the MSHvSF ignored
`local/mednafen/firmware/` into `local/mednafen/firmware/`. Each matches the
SHA-256 that Mednafen 1.32.1's own `Documentation/ss.html` (from the verified
archive above) gives for its default filename:

| File | Size | SHA-256 | Mednafen use |
| --- | ---: | --- | --- |
| `sega_101.bin` | 524,288 | `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac` | `ss.bios_jp`, "Required for Japan-region games" |
| `mpr-17933.bin` | 524,288 | `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` | `ss.bios_na_eu` |

MSHvSF records `sega_101.bin` as a copy of the user-supplied
`Bios Saturn 1.01 (J) [!].bin`. Whether the BIOS boots XvSF is `EMU-003`'s
test.

### Launch Commands

Interactive, from the repository root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
```

Unattended: the same with `MEDNAFEN_HOME="$PWD/local/mednafen_quiet"`, with
stdout and stderr redirected to a file under the ignored `local/logs/`.
Stock Mednafen has no log-directory setting.

## Unattended Cold Boot (`EMU-003`, `EXP-0001`)

Stock Mednafen has no scripted screenshot. `tools/mednafen/cold_boot.py` lets
the agent see unattended runs without input or the agent interface:

```bash
rm -f local/mednafen_quiet/sav/*   # start with no backup RAM
./invenv.sh python -m tools.mednafen.cold_boot \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/emu003/bootN --seconds 90
```

- It adds `-qtrecord FILE`, a command-line option that is not saved to the
  configuration. Mednafen catches SIGTERM, prints "Signal has been caught and
  dealt with: SIGTERM", exits 0 and finalizes the movie.
- The movie is a 10560x480 CamStudio (`cscd`) canvas (30 × 352). Frames are
  scaled to 352x240 with ffmpeg 9.0.1, so they approximate native
  screenshots. The movie is deleted afterwards (about 960 MB per 90 s); its
  hash stays in `run.json`.
- Result: title screen at about 68-75 s, identical across three boots
  (`docs/discoveries.md` D-001).

## 4 MiB Cart (`EMU-004`, `EXP-0002`)

`ss.cart auto` stays the project setting: forced `-ss.cart extram4` gives the
same log cart line and byte-identical frames. With `-ss.cart none` the game
stops on a cart-missing warning (D-002). A wrong cart setting therefore shows
as that warning at about 14 s after launch.

`cold_boot.py --setting KEY=VALUE` passes a per-run setting. Mednafen saves it
into the home on exit, so run `./invenv.sh python -m tools.mednafen.home`
afterwards; the quiet home's config SHA-256 should return to `ef897288…5019`.

## Pad Mapping (`EMU-005`, 2026-10-28)

The port 1 gamepad bindings were copied from the MSHvSF interactive
configuration (`/Users/colinwhite/workspace/personal/msh_vs_sf_saturn_en_translation/local/mednafen/mednafen.cfg`,
SHA-256 `b308aab2…9a50`, modified 2026-10-28 11:02) into both homes:

```bash
./invenv.sh python -m tools.mednafen.home --bindings-from \
  ../msh_vs_sf_saturn_en_translation/local/mednafen/mednafen.cfg
```

This is the mapping MSHvSF was last played with. It differs from the M30
table in MSHvSF's `docs/mednafen.md` (D-pad buttons 12-15, Start button 9),
which is out of date there; the configuration file is the source used.

| Saturn control | Binding (joystick `0xecccd365fc40db2f0006000c00010000`) |
| --- | --- |
| Up / Down | `abs_1-` / `abs_1+` |
| Left / Right | `abs_0-` / `abs_0+` |
| A / B / C | `button_0` / `button_1` / `button_10` |
| X / Y / Z | `button_2` / `button_3` / `button_9` |
| Start | `button_6` |
| L / R | `keyboard 0x0 19` (both; no pad button) |

- The joystick ID is the 8BitDo M30 in its wired PS4-compatible mode (MSHvSF
  `EMU-006`). A silent probe boot on 2026-10-28 logged
  `ID: 0xecccd365fc40db2f0006000c00010000 - PS4 Controller`, the ID the
  bindings use.
- Physical button labels for each SDL index are not recorded here; the
  in-game check names what each one does.
- Both configurations load 7,904 settings, 0 unknown. New SHA-256:
  `local/mednafen/mednafen.cfg` `cb1c2d3b…a1e9`,
  `local/mednafen_quiet/mednafen.cfg` `aad9a7ef…57cf`.
- Hotkeys (1.32.1 defaults): F9 screenshot, F12 exit.
- In-game check (2026-10-28): the user played the interactive home through
  the steps in `research_log.md` `SESSION-0009` (menu, character select, a
  fight with all six face buttons and the D-pad, Start to pause) and
  reported "Everything worked as expected". The session log
  (`local/emu005/session.log`) shows the bound pad ID, `SGID: T-1226G` and
  `Cart: 4MiB Extended RAM`; exit 0; configuration unchanged.
- Not recorded: which physical button label gives which attack. L/R were
  not tested (no pad binding).

## Screenshots and States by Hotkey (`EMU-006`, `EXP-0003`)

Stock 1.32.1 offers screenshots and states only as hotkeys (defaults F9
screenshot, F5 save, F7 load, F12 exit). `tools/mednafen/hotkeys.py` presses
them at fixed times in an unattended run:

```bash
./invenv.sh python -m tools.mednafen.hotkeys IMAGE.cue local/RUN.log \
  --at 70:F9 --at 71:F5 --at 85:F9 --at 86:F7 --at 87:F9
```

- It sends macOS key codes through System Events. Before each key it brings
  Mednafen (by PID) to the front and checks it is frontmost; otherwise it
  stops without sending. Afterwards it returns focus to the previous app.
  Each key takes about 1.1 s.
- Permission: macOS attributes the keystrokes to the Claude Code bundle
  under `~/Library/Application Support/Claude/claude-code/<version>/…/claude.app`
  (Claude.app starts it through a `disclaimer` helper), so Accessibility
  must be on for that entry. Without it, osascript fails with error 1002.
  The path contains the Claude Code version, so an update may need a new
  grant.
- Outputs: `snaps/<image>-NNNN.png` (352x240; 330x240 seen in a boot screen),
  numbered by `snaps/<image>-counter.txt`; states
  `mcs/<image>.<md5>.mc0` (slot 0), about 3.5 MB at the title.

## Stock Debugger, Unattended (`EMU-007`, `EXP-0004`)

`tools/mednafen/hotkeys.py --script FILE --keep-focus` drives the debugger;
example step files are in `research/experiments/EXP-0004/steps/`.

| Need | Steps | Notes |
| --- | --- | --- |
| Freeze | `option+a` | Frame advance; `F5` then saves this instant. |
| Debugger | `option+d` | Opens on the CPU view; again to hide. |
| Memory editor | `option+3`, then `period`/`comma` | Starts at "SH-2 External Bus (TODO)"; one `period` = Low Work RAM, two = High Work RAM. |
| Dump | `d`, `type=00000000 000fffff PATH`, `return` | End is inclusive. |
| Write | `l`, `type=START END PATH`, `return` | Freeze first; restore before running. |
| Resume | `option+d` (hide), `option+r` | `option+r` with the debugger shown did not resume. |
| Write breakpoint | CPU view: `shift+w`, `type=A-B C-D`, `return` | Checked only for the active CPU. |
| See the screen | `window=PATH` | Window-ID capture; shows the overlay. |

- Option chords must arrive as **left** Option: the debugger's view switch
  tests SDL's `KMOD_LALT`. The tool posts left-Option CoreGraphics events.
  With System Events' `using option down`, `option+3` was ignored and the CPU
  view stayed active; there `l` opens "Trace Log(filename end_pc)", which
  swallowed typed paths.
- Prompt errors appear only on screen, so use `window=` to check prompts.
- Mednafen's `%08x` parse accepts a leading `+`, so `00000000 +00100000 FILE`
  is read by the inclusive-end form and dumps `0x100001` bytes. Use
  `00000000 000fffff FILE`.
- Window capture needs Screen Recording for the same Claude Code bundle.
  macOS showed the user a dialog about bypassing the private window picker on
  the first capture; captures worked.
