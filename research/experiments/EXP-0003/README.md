# EXP-0003: Screenshots and Save/Load States by Hotkey

Task: EMU-006
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0001` showed the title screen at about 68-75 s after launch, then an
attract fight. Stock Mednafen 1.32.1 has no command-line screenshot or state
option; F9 (screenshot), F5 (save state) and F7 (load state) are its default
hotkeys.

## Hypothesis

F9 writes a screenshot to the home's `snaps/`, F5 writes a state to `mcs/`,
and F7 restores the saved screen, both later in the same session and after a
fresh cold boot.

## Controlled Change

No change to binary, BIOS, configuration or source. Hotkeys are pressed by
`tools/mednafen/hotkeys.py` through macOS System Events, after the user
granted Accessibility (see Tools). `sav/` and `mcs/` were emptied before run
1; `sav/` was emptied before run 2 (the run 1 state was kept).

## Prediction

- Run 1: the screenshot at ~71 s shows the title; the one at ~86 s shows the
  attract fight; the one ~1 s after F7 shows the title again.
- Run 2: the screenshot at ~21 s shows a boot screen, not the title; ~2 s
  after F7 it shows the title, which a normal boot reaches only at ~68 s.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/xmvsf_saturn_jp_3m/` (42
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock 1.32.1 binary
(`892bb60a…29dd`), home `local/mednafen_quiet/` with the MSHvSF pad bindings
(`aad9a7ef…57cf`).

## Tools and Environment

- `tools/mednafen/hotkeys.py`: launches Mednafen; for each `--at SECONDS:KEY`
  it brings the Mednafen process (by PID) to the front, checks it is
  frontmost, sends the macOS key code, and restores the previous front app;
  sends F12 at the end.
- Permission: the first attempts failed with `osascript is not allowed to
  send keystrokes. (1002)`. Commands here run under Claude.app → `disclaimer`
  → the Claude Code `claude.app` bundle in
  `~/Library/Application Support/Claude/claude-code/2.1.304/…`. After the user
  granted Accessibility ("I flipped a switch"), a pilot (F9 at 10 s) wrote a
  352x240 screenshot of the Saturn BIOS logo, kept in
  `local/emu006/pilot_snaps/`.

## Procedure

```bash
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
find local/mednafen_quiet/sav local/mednafen_quiet/mcs -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys "$CUE" local/emu006/run1.log \
  --at 70:F9 --at 71:F5 --at 85:F9 --at 86:F7 --at 87:F9
# move snaps/*.png to local/emu006/run1_snaps/; hash mcs/*.mc0
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys "$CUE" local/emu006/run2.log \
  --at 20:F9 --at 22:F7 --at 24:F9
# move snaps/*.png to local/emu006/run2_snaps/; re-check the state hash
```

Source manifests were taken before and after (`local/emu006/source-*.json`).

## Actual Result

Key times (seconds after launch): run 1 F9 71.17, F5 72.30, F9 86.13, F7
87.30, F9 88.40, F12 89.56; run 2 F9 21.14, F7 23.15, F9 25.12, F12 26.21.
Both exited 0.

| Shot | When | Size | Screen (agent-reviewed) | SHA-256 |
| --- | --- | --- | --- | --- |
| `-0001` | run 1, 71 s | 352x240 | Title logo | `1ba0f99f…3226` |
| `-0002` | run 1, 86 s | 352x240 | Attract fight with copyright notice | `b98328b3…0732` |
| `-0003` | run 1, 1.1 s after F7 | 352x240 | Title logo, `PRESS START BUTTON` | `b33972bc…1d07` |
| `-0004` | run 2, 21 s | 330x240 | Black (boot) | `091e40d8…58ba` |
| `-0005` | run 2, 2.0 s after F7 | 352x240 | Title logo, `PRESS START BUTTON` | `5f5cb6a3…8103` |

- State: `local/mednafen_quiet/mcs/X-Men vs. Street Fighter (Japan)
  (3M).cead02d9d3cc1b97c82dbf063fba19bf.mc0`, 3,508,722 bytes, SHA-256
  `739ef207…2f2d`, unchanged after being loaded in run 2.
- ffmpeg SSIM (All): `-0001`/`-0003` 0.822, `-0003`/`-0005` 0.896,
  `-0001`/`-0005` 0.823; title `-0001` against the fight `-0002` 0.091.
- The title shots are not byte-identical: the title background is animated
  and each shot was taken 1-2 s after its save or load.
- Source manifests identical before and after. `git check-ignore` covers the
  state, the screenshots (`local/`), and `*.mc*`/`*.png` under
  `research/experiments/`.

## Conclusion

**CONFIRMED.** F9 screenshots and F5/F7 states work in stock 1.32.1 and are
stored under ignored paths. Loading the state brings the game back to the
saved title screen, both later in the same session and in a fresh cold boot
about 45 s before the title would otherwise appear.

## Uncertainty and Alternatives

- Byte-identical reproduction of the saved instant was not tested; it needs
  a frozen frame (frame advance) at save, screenshot and load. `EMU-007`
  uses the debugger and frame advance.
- Hotkeys briefly take focus from the user's front app. The tool returns
  focus after each key and refuses to send a key unless Mednafen is
  frontmost.
- The Accessibility grant belongs to a Claude Code bundle path that includes
  its version (`2.1.304`); after an update it may need granting again.

## Reproduction

Run the procedure above. Expect `-0002` to be the attract fight and `-0003`
and `-0005` to be the title. Evidence stays in the ignored `local/emu006/`
and `local/mednafen_quiet/mcs/`.
