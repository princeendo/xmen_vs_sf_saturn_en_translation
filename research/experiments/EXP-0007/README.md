# EXP-0007: Recorded Play Session and Text-Surface Inventory

Task: REF-005
Status: DONE
Confidence: CONFIRMED (surfaces seen); UNKNOWN (arcade English for win quotes and hints)

## Observation

`REF-005` needs one recorded play session to list where the Saturn release
shows Japanese text. `EMU-021` made agent-driven recording possible.

## Hypothesis

Not a mechanism test: an inventory. The question is which screens reached by
ordinary play show Japanese text, and whether the US arcade shows English in
the same place.

## Controlled Change

None to the game. Patched build (`EXP-0006`) in the interactive home
(`local/mednafen/`, pad bindings, sound) with `MEDNAFEN_AGENT_DIR`; the user
played; `tools/mednafen/session_recorder.py` (copied from MSHvSF `69c666c`)
saved a screenshot each second and a state each 3 s (newest 60 kept).

## Prediction

Japanese text at least on win quotes (as in the arcade's Japanese sets);
other surfaces unknown.

## Inputs and Provenance

Source, BIOS and patched binary (`290d4717…f9f8`) as `EXP-0006`. The
interactive home's backup RAM from the `EMU-005` session was present. MAME
0.289 with `local/arcade_roms/xmvsf_mame0289/` (`REF-001`).

## Tools and Environment

`session_recorder.py`; ffmpeg 9.0.1 contact sheets (no text filter in this
build, so tiles were mapped to frames by position); MAME
`tools/reference/mame_snap_frames.lua`.

## Procedure

1. Smoke test: 25 s unattended in the silent home: 22 screenshots, 8 states;
   the recorder stopped by itself 10 s after Mednafen exited.
2. Session: the agent launched Mednafen and the recorder; the user followed
   a 13-step table (attract 2 min, arcade mode, win one fight, lose with a
   continue, lose to game over, options, F12). User report: "done, no
   surprises".
3. Review: 514 screenshots, 414 unique by SHA-256, as 14 contact sheets;
   samples viewed at full size.
4. Arcade check: `xmvsfu` and `xmvsfjr2` headless with snapshots every 150
   frames to frame 7200 (48 each), reviewed as contact sheets and at full
   size.

```bash
SNAP_FRAMES="$(seq 150 150 7200 | tr '\n' ' ')" mame xmvsfu \
  -rompath local/arcade_roms/xmvsf_mame0289 -video none -sound none -nothrottle \
  -skip_gameinfo -nomouse -cfg_directory local/mame_arcade/ref005/cfg \
  -nvram_directory local/mame_arcade/ref005/nvram \
  -snapshot_directory local/mame_arcade/ref005/xmvsfu/snap \
  -homepath local/mame_arcade/ref005 -autoboot_script tools/reference/mame_snap_frames.lua
```

## Actual Result

- Session: 2026-10-28 21:13:40-21:22:31 UTC, frames 142-30380; Mednafen
  exit 0; log `SGID: T-1226G`, `Cart: 4MiB Extended RAM`, pad
  `0xecccd365…0000`.
- Three Japanese surfaces: attract captions (4), win quotes (player and CPU
  wins), continue-screen hints (two different tips). Everything else seen
  was English. Table, samples and hashes: `docs/text_surfaces.md`.
- Arcade: the US set shows English captions in the attract-caption slots,
  the JP set Japanese ones; one US caption scrolls and was seen in part.
  The arcade attract does not reach win quotes or the continue screen.
- Caption wording is kept in the ignored `local/ref005/notes.md`, not in
  git.

## Conclusion

The ordinary-play Japanese surfaces are attract captions, win quotes and
continue hints. The US arcade has English attract captions (observed). For
win quotes and hints the arcade's English is not yet observed.

## Uncertainty and Alternatives

- One session; screens shorter than the 1 s sampling may be missed.
- Not reached: endings, story/pre-fight text, bosses, versus mode, options
  sub-screens, save messages, rare text (`docs/text_surfaces.md`).
- Caption pairing between the US and Japanese sets is by order only.

## Reproduction

Launch as in the procedure (`docs/mednafen.md`, `vendor/mednafen/README.md`),
run `./invenv.sh python -m tools.mednafen.session_recorder OUT --agent-dir
OUT/agent`, play the same route, and review the screenshots.
