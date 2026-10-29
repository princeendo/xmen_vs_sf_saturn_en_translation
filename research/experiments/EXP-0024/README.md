# EXP-0024 (M3): All of Ryu's Win Quotes in English From the Source Image

Task: RE-003
Status: DONE
Confidence: CONFIRMED

## Observation

The game's own English quote mode works for Ryu through a code patch in
`MMPACK.PCA` and English records in `MC09.SHP` (`EXP-0023`). The user passed
`GATE-TRANSLATION` for Ryu's win quotes: official arcade English, no
rewording, and Saturn record `k` shows English record `k mod 8` (`EXP-0022`).

## Hypothesis

A caption compiler turns the official English into exactly the arcade's record
codes. A spec-driven build then reproduces the confirmed image. With it, each
of Ryu's 16 Saturn draws shows its paired English record, cell for cell.

## Controlled Change

The build changes only `MMPACK.PCA` (the `tools/disc/english_mode.py` patch)
and `MC09.SHP` (800 bytes at decompressed offset `0x25D8`: English records 0-7,
100 bytes each). Original and new bytes are in the ignored
`local/re003/b1/changes.json` (rule 12).

## Prediction

- Compiling each record's decoded text reproduces its source bytes.
- The build equals the `EXP-0023` version-2 files.
- Draw `r` (0-15) shows English record `r & 7` with every cell as compiled.
- A cold-boot Ryu win shows English.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| English | US set `xmvsfu` program (`EXP-0008`), slot 9 records 0-7 at `0x188DE2` + 100k. Their hashes are in `data/translations/ryu_win_quotes.json`; the text is not committed (AGENTS.md rule 21). |
| Pairing | `data/translations/ryu_pairing.json` (`EXP-0022`) |
| Source image | Hashes unchanged (`local/logs/re003-source-after.json`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/caption.py` | The compiler: arcade map, 25 cells per line, 2 lines, left-aligned with space padding. It rejects long lines and unmapped characters. |
| `tools/disc/english_mode.py` | The `EXP-0023` version-2 patch, promoted |
| `tools/disc/build_english.py` | Spec-driven build. It decodes the ROM records, recompiles them, requires identical bytes (unless an opt-in `grammar_fix` is used; there are none), and builds both files. |
| [`make_spec.py`](make_spec.py) | Writes the spec |
| [`seed_scan.py`](seed_scan.py) | Finds the seed for each draw |
| [`force_draws.py`](force_draws.py) | Shows each draw live |
| `research/experiments/EXP-0023/cell_check_en.py` | Cell check |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0024/make_spec.py data/translations/ryu_win_quotes.json
./invenv.sh python -m tools.disc.build_english data/translations/ryu_win_quotes.json local/re003/b1   # and b2
./invenv.sh python -m tools.disc.patch_image --source-dir local/disc_images/xmvsf_saturn_jp_3m \
  --manifest references/saturn_jp/README.md --track "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin" \
  --file "MC09.SHP;1" --data local/re003/b1/MC09.SHP --file "MMPACK.PCA;1" --data local/re003/b1/MMPACK.PCA \
  --out-dir build/re003_ryu_english
./invenv.sh python research/experiments/EXP-0024/seed_scan.py local/re003/scan1 $(seq 1 40)   # and scan2, 41-60, spread
./invenv.sh python research/experiments/EXP-0024/force_draws.py local/re003/b1 local/re003/draws_a control 0 1 2 3 4 5 6 7
./invenv.sh python research/experiments/EXP-0024/force_draws.py local/re003/b1 local/re003/draws_b 8 9 10 11 12 13 14 15
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/re003/draws_a local/ref007/saturn_files/FIX.PRS
```

## Actual Result

**Compiler.** All 9 of Ryu's English records decode and re-encode to their
exact bytes. Line lengths of records 0-7 are 19-25 characters.

**Build.**

- **Files:** `MC09.SHP` `507b1f46…`, `MMPACK.PCA` `9a7ab3e7…`. Two builds are
  identical, and both files are byte-identical to `EXP-0023`'s version-2
  files.
- **Image:** `build/re003_ryu_english`, Track 01 `1034b8d7…`. All 42
  components equal the play-checked `EXP-0023` image, whose duplicate copy
  was deleted.
- **Sectors:** 138 changed (all of `MMPACK.PCA` and `MC09.SHP`). All 71,908
  pass EDC/ECC, and the ISO layout is unchanged.

**Forcing the draw.**

- **`onhit` does not work here.** An `onhit` write right after the draw's
  store at `0x06066666` was applied (agent event
  `action … pc=06066668 write …`), but the selector, reading the value two
  instructions later, still used the original draw. The read hits the SH-2
  data cache, which a debugger write does not update (HYPOTHESIS for the
  mechanism; the effect is reproducible).
- **Seeds instead.** The draw was steered through the RNG seed word at
  `pre_ko`. `pause` lands 0 or 1 frames after `loadstate`, so each run
  reloads until the paused seed reads 8520.
- **Scans:** seeds 1-40, twice, gave identical draws. Seeds 41-60 and a
  spread of 24 more filled draw 7.

| Draw | Seed | Draw | Seed |
| --- | --- | --- | --- |
| 0 | 2 | 8 | 5 |
| 1 | 12 | 9 | 26 |
| 2 | 15 | 10 | 1 |
| 3 | 8 | 11 | 13 |
| 4 | 21 | 12 | 35 |
| 5 | 33 | 13 | 19 |
| 6 | 17 | 14 | 3 |
| 7 | 27029 | 15 | 6 |

**All 16 draws, live from `pre_ko`, with the built code and table**
(`force_draws.py`, cell check):

| Run | Pointer | Record = compiler's prediction | Grid | Cells |
| --- | --- | --- | --- | --- |
| control | `0x0024F8D0` (Japanese 10) | — | 19 × 16 px | 38/38 |
| r = 0-7 | `0x0024F5D8` + 100r | yes, all | 25 × 12 px | 50/50 each |
| r = 8-15 | `0x0024F5D8` + 100(r − 8) | yes, all | 25 × 12 px | 50/50 each |

**User play check** (2026-10-28, cold boot of `build/re003_ryu_english`,
agent-reviewed): two Ryu wins showed English records 0 and 1.

## Conclusion

**CONFIRMED (M3).**

- All of Ryu's win quotes are handled programmatically: a spec of source
  addresses and hashes, a compiler, and a build tool produce the image from
  the untouched source.
- Every one of the 16 Saturn draws shows its paired official English record,
  exactly as compiled.
- A cold boot shows English in two independent wins.

## Uncertainty and Alternatives

- **Draws vs records:** draws `k` and `k + 8` show one English record, by the
  user's pairing. Ryu's English record 8 is unused.
- **Fixed-index mode, endings and type-6 text:** not reached (`EXP-0023`).
- **SH-2 cache:** the cache explanation for the failed `onhit` is a
  HYPOTHESIS. Later forcing should write well before the read, or steer
  inputs such as the seed.
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect:

- the file and track hashes above;
- 16 draws with 50/50 cells, and the control with 38/38.
