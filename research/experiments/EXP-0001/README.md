# EXP-0001: Unattended Cold Boots of XvSF to the Title Screen

Task: EMU-003
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-002` pinned a project-local Mednafen home with the Japanese BIOS
(`sega_101.bin`, matching Mednafen 1.32.1's documented hash). The game had not
been run. Stock Mednafen has no scripted screenshot, and the agent interface
may not be used before `EMU-020`.

## Hypothesis

Stock Mednafen 1.32.1, with the silent project home and no input, cold-boots
the untouched XvSF Saturn image to a stable title screen, and does so the same
way each time.

## Controlled Change

None to the game, BIOS, binary or configuration. Each run adds only the
command-line option `-qtrecord FILE` (not a saved setting; config hashes are
unchanged afterwards) so the agent can see the screen without sending input.
Before each run the silent home's `sav/` is emptied, so every boot starts with
no backup RAM.

## Prediction

Each of three boots logs `SGID: T-1226G`, shows the title screen within 90
seconds with no input, and leaves all 42 source components unchanged.

## Inputs and Provenance

- Source: `local/disc_images/xmvsf_saturn_jp_3m/` (42 components,
  `references/saturn_jp/README.md`), via
  `X-Men vs. Street Fighter (Japan) (3M).cue`.
- BIOS: `local/mednafen/firmware/sega_101.bin`, SHA-256 `dcfef4b9…deac`
  (`docs/mednafen.md`).
- Emulator: `vendor/mednafen/build/src/mednafen`, stock 1.32.1, SHA-256
  `892bb60a…29dd`.
- Home: `local/mednafen_quiet/` (config SHA-256 `ef897288…5019`), firmware
  linked to `local/mednafen/firmware/`.

## Tools and Environment

- macOS 26.7.1, Darwin 25.6.0 arm64; ffmpeg 9.0.1 (Homebrew).
- `tools/mednafen/cold_boot.py` (this repository): runs Mednafen with
  `-qtrecord`, sends SIGTERM after `--seconds`, extracts one frame per second
  scaled to 352x240 (`scale=352:240:flags=area`), builds 5x5 contact sheets,
  writes `run.json` with log, video and frame hashes, then deletes the video.
- The recording canvas is 10560x480 (30 × 352 wide, a common multiple of the
  Saturn's horizontal resolutions), CamStudio (`cscd`) video. Frames are
  scaled from it, so they are not native emulator screenshots.

## Procedure

Pilot (20 s, `local/emu003/pilot.log`): SIGTERM is caught ("Signal has been
caught and dealt with: SIGTERM"), the process exits 0, and the movie is
finalized (ffprobe: 1134 frames in 18.97 s). The pilot showed only the BIOS
and SEGA licence screens, so the runs use 90 s.

```bash
./invenv.sh python -m tools.disc.hash_source --json \
  local/disc_images/xmvsf_saturn_jp_3m/* > local/emu003/source-before.json
for n in 1 2 3; do
  rm -f local/mednafen_quiet/sav/*
  ./invenv.sh python -m tools.mednafen.cold_boot \
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
    local/emu003/boot$n --seconds 90
done
./invenv.sh python -m tools.disc.hash_source --json \
  local/disc_images/xmvsf_saturn_jp_3m/* > local/emu003/source-after.json
cmp local/emu003/source-before.json local/emu003/source-after.json
```

## Actual Result

| Boot | Start (UTC) | Exit | Log SHA-256 | Video size / SHA-256 (deleted) |
| ---: | --- | ---: | --- | --- |
| 1 | 2026-10-28 19:24:14 | 0 | `52987f19…6bd6` | 963,463,285 / `799abb0e…` |
| 2 | 2026-10-28 19:25:55 | 0 | `c7a09004…826b` | 963,167,818 / `1099068e…` |
| 3 | 2026-10-28 19:27:37 | 0 | `32cf8923…7978` | 963,167,818 / `8cc8518e…` |

- Every log (5,887 bytes) shows `SGID: T-1226G`, `SGNAME: X-MEN VS STREET
  FIGHTER`, `SGAREA: J`, `Region: 0x1`, `Cart: 4MiB Extended RAM`. The logs
  differ only in the line naming the output file. Other "Error"/"Failed"
  lines are absent optional files: the `.sbi`, `ss.cfg`, the per-game
  `pgconfig` file, and `cheats/ss.cht`.
- All 89 per-second frames are byte-identical across the three boots. The
  container hashes differ, but the frames do not.
- Sequence (agent-reviewed, frame N ≈ second N-1): BIOS 1.01 animation and
  logo, SEGA licence, Capcom logo, `NOW LOADING`, attract scenes with Japanese
  captions and `PRESS START BUTTON`, the Ryu-Cyclops handshake (066-067),
  **the title logo with `PRESS START BUTTON` (068-075)**, black (076), an
  attract fight with the copyright notice (077-085), and `SCORE RANKING`
  (086-089).
- Title frame `frames/070.png` (352x240): SHA-256
  `ebfbb7da304032613e6d1f43c207517b81a13464ee3c40994856998ee477e662` in all
  three boots.
- The 42 source components are identical before and after (`cmp` of the two
  manifests); both config files and the binary hash as before.

## Conclusion

**CONFIRMED.** Stock Mednafen 1.32.1 with the project's silent home and the
Japanese BIOS cold-boots the untouched image to a stable title screen with
no input, about 68 s after launch, identically in three runs at one-second
sampling.

## Uncertainty and Alternatives

- Identical per-second frames do not prove frame-exact determinism between
  samples, or with input.
- `Cart: 4MiB Extended RAM` comes from `ss.cart auto`. Whether the game
  needs the cart, and what happens without it, is `EMU-004`.
- Real-time pacing: the pilot recorded about 59.8 frames per second. Whether
  emulation stalls when the display sleeps (the MSHvSF vsync observation) was
  not tested.
- A Mednafen window opens during each run; the runs are silent, not hidden.

## Reproduction

Run the procedure above from the repository root. Evidence stays in the
ignored `local/emu003/` (`boot*/run.json`, `mednafen.log`, `frames/`,
`sheet-*.png`; `title_066_077.png`; source manifests). Expect frame 070 to
hash `ebfbb7da…e662`.
