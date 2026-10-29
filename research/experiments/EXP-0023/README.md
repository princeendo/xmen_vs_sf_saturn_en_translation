# EXP-0023: Fit English Quotes With the Game's Own English Mode

Task: LAYOUT-001
Status: DONE
Confidence: CONFIRMED

## Observation

None of Ryu's 9 arcade English quotes fits the Saturn's 2 × 19 cells
(43-50 characters, lines of up to 25; `EXP-0020`). The Saturn's win-quote
selector is a port of the arcade's, including its English branch. A nonzero
language word picks a remapped index, a second base list and 100-byte
records (`EXP-0021`, `EXP-0022`).

## Hypotheses

1. The Saturn renderer also keeps the arcade's English layout.
2. Win quotes can use it without changing hints, endings or other
   characters.

## Routes Measured

| Route | What it needs | Capacity | Status |
| --- | --- | --- | --- |
| (a) Pair glyphs: 2 letters per 16 px cell | Data only (`FIX.PRS` + MC files). Ryu needs 113 pair glyphs; the roster needs 430, against 409 kanji codes unused by any Japanese quote or ending. Letters are 8 px (offline mock-up). | 2 × 38 characters | Measured offline, not built |
| (b)/(c) Other grid or pitch | Code changes | — | Subsumed by (d): the game has the grid already |
| (d) Native English mode | A code patch in `MMPACK.PCA` and English records in the MC files | 2 × 25 characters, the arcade record format; all 161 quotes fit as written | **Chosen by the user**, built and tested |

User decision, 2026-10-28, verbatim: "Use route (d), the game's native
English mode. Build and test it from disc."

## Findings Behind Route (d)

- **Renderer English mode (live RAM, `english_mode.py`).** From `pre_ko`, with
  the language word (`0x060F547A`) and the size word (`0x060F5478`) set to 2:
  - the pointer moved to the second base list plus 100 × (r mod 8);
  - the quote drew 2 rows × 25 sprites at a 12 px pitch (x 24-312, y 176
    and 192, color word `0x7000`).
- **Readers of the global words.** The language word is read only in the
  quote code, at 14 sites. The size word is a mode word that 45 sites
  compare with 4 and 10, every frame. So the global words cannot simply be
  set.
- **Selectors** (twins of the arcade's): win quotes `0x0606663C` (type 0),
  hints `0x06066728` (type 2), endings `0x060668A2` (type 4) and
  `0x060667B8` (type 6). They share the renderer `0x06066948`. The ending
  selector loads the renderer's language literal.
- **Code location.** The quote code is in `MMPACK.PCA` (LSN 45,462, 258,319
  bytes). The file holds 2 entries (to `0x06014000`, 42,080 bytes; to
  `0x0601F000`, 588,380 bytes) and is loaded after Start. A first catch
  attempt halted on `OPENPACK.PCA` (the attract pack) overwriting the same
  region about 18 s later. The code itself arrives without CPU writes there.
- **Free task byte.** Task + `0x5C` is untouched between the quote's setup
  (frame 725 from `pre_ko`) and its release (frame 1040).

## Controlled Change: The Patch (`english_patch.py`, version 2)

Same-size changes to the decoded `MMPACK.PCA` (rule 12). The originals are
checked before every write.

| Address | Original | New | Purpose |
| --- | --- | --- | --- |
| `0x06066668` (11 words) | `90E2 00BD 2008 3EEA 890E D104 C501 001C C003 A009 0009` | `C503 8812 C501 8B08 C907 E15C 316C E202 2120 A002 0009` | Win selector. If slot × 2 = 18 (Ryu): index = r & 7, task + `0x5C` = 2. Otherwise index = r. |
| `0x06066682` (3 words) | `0009 0606 6718` | `EEFF A005 0018` | Exit: r14 = -1, T = 1, continue at `0x06066692` (the old remap-table pointer, now unused) |
| `0x06066690` | `C403` | `AFEA` | Fixed-index path rejoins the slot test |
| `0x0606696A`, `0x0606699E`, `0x060669CC`, `0x060669F6`, `0x06066A10`, `0x06066A3A` | `00BD` | `00CC` | Renderer reads the task flag (`mov.b @(r0,r12)`) instead of the global words |
| `0x06066A70`, `0x06066A74` | `D478`, `D47A` | `005C`, `005C` | The renderer's literals point at the flag offset |
| `0x060668C4` | `00BD` | `E000` | The ending selector's language read becomes 0, its value as before |

**Data.** `MC09.SHP`'s decompressed offset `0x25D8` (Ryu's table): 800 bytes
of 8 official English records (`xmvsfu` program `0x188DE2`-`0x189102`, slot
9 records 0-7), over the first 10.5 of the 16 Japanese records. The ending
records 16-21 at `+0x4C0` are untouched. Original bytes are in the ignored
`local/layout001/v2b1/changes.json`.

**Version 1** (no slot test; it switched every character) is recorded in
`PATCHES_V1_SELECTOR`. The first play check rejected it (below).

## Prediction

- Ryu's win quotes draw his English record `r & 7` = `r mod 8` (`PAIR-001`)
  in the 2 × 25 grid.
- Every other quote, hint and ending draws as in the unpatched game.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | Hashes unchanged (`local/logs/layout001-source-after.json`) |
| Checkpoints | `pre_ko` (`EXP-0014`); session states 5116 and 5696 (`EXP-0013`) |
| English | US set `xmvsfu` (`references/arcade/`), read at run time |
| Emulator | patched build (`EXP-0006`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/prs.py` | New: `lazy` matching, `split_header`, `decompress_entries`, and `compress_file(header=...)`, with tests |
| [`english_mode.py`](english_mode.py) | The renderer's English mode, global words |
| [`catch_code.py`](catch_code.py) | The code's loader |
| [`english_patch.py`](english_patch.py) | The patch table |
| [`english_trial.py`](english_trial.py) | Live-RAM trial |
| [`v2_on_session.py`](v2_on_session.py) | Version 2 on the play-check states |
| [`cell_check_en.py`](cell_check_en.py) | Cell check in either grid |
| [`build_english.py`](build_english.py) | Builds the two files |
| `tools/disc/patch_image.py` | Builds the image |

## Procedure

```bash
SRC=local/disc_images/xmvsf_saturn_jp_3m; T="X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
./invenv.sh python research/experiments/EXP-0023/english_mode.py local/layout001/em1
./invenv.sh python research/experiments/EXP-0023/english_trial.py local/layout001/trial2
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/layout001/trial2 local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0023/build_english.py local/layout001/v2b1   # and v2b2
./invenv.sh python -m tools.disc.patch_image --source-dir $SRC --manifest references/saturn_jp/README.md \
  --track "$T" --file "MMPACK.PCA;1" --data local/layout001/v2b1/MMPACK.PCA \
  --file "MC09.SHP;1" --data local/layout001/v2b1/MC09.SHP --out-dir build/layout001_english_v2
./invenv.sh python -m tools.disc.sector "build/layout001_english_v2/$T"
./invenv.sh python research/experiments/EXP-0019/cold_font.py "build/layout001_english_v2/X-Men vs. Street Fighter (Japan) (3M).cue" local/layout001/cold2
./invenv.sh python research/experiments/EXP-0018/pick_load.py "build/layout001_english_v2/X-Men vs. Street Fighter (Japan) (3M).cue" local/layout001/pick2
./invenv.sh python research/experiments/EXP-0023/v2_on_session.py local/layout001/v2s_orig \
  storm_orig:f00019207:240:orig storm_v2:f00019207:240:v2
```

## Actual Result

**Live RAM, version 2** (`trial2`, cell check):

| Run | Index | Flag | Pointer | Grid | Cells |
| --- | --- | --- | --- | --- | --- |
| control | 10 | 0 | `0x0024F8D0` | 19 × 16 px | 38/38 |
| natural | 2 (r = 10) | 2 | `0x0024F6A0` | 25 × 12 px | 50/50 |
| forced 0, 3, 7 | 0, 3, 7 | 2 | base + 100k | 25 × 12 px | 50/50 each |

**Build.**

- **Files:** `MMPACK.PCA` was re-encoded lazily to `9a7ab3e7…` (the greedy
  encoder is 5 bytes too large; lazy is 2,146 bytes smaller). `MC09.SHP` is
  `507b1f46…`. Both keep their original sizes, with their streams ending in
  the last sector, and two builds are identical.
- **Image:** Track 01 `1034b8d7…`. 138 sectors changed: all 127 of
  `MMPACK.PCA` and all 11 of `MC09.SHP`. All 71,908 sectors pass EDC/ECC,
  and the ISO layout is unchanged.
- **Cold boot and Start:** WRAM-H holds the version-2 code exactly.
- **Pick from state 5696:** the 800 English bytes load. The 777 other
  differing bytes are the 259 fix-ups.

**Play check 1 (version 1, user, cold boot).**

- Two Ryu wins showed English.
- The continue hint was Japanese and correct.
- **Storm's win quote was broken**: her Japanese records drew in the 25 ×
  12 px grid. Version 1 had switched every speaker, and only Ryu has English
  records. This was reproduced from her session state (`storm_v1`).

**Version 2 on version-1 session states** (`v2_on_session.py`):

| Run | Result |
| --- | --- |
| `storm_v2` | Screenshot and VDP1 VRAM byte-identical to `storm_orig` (all patch sites restored to original bytes), and reproducible |
| `ryu2_v2` | English, 50/50 cells |

**Play check 2 (version 2, user, cold boot, 2026-10-28).**

- **Ryu's win:** English "Forget about a rematch. Practice more instead."
- **Wolverine's win:** Japanese, 2 × 19, 38/38 cells from the session state
  (version-2 code in RAM, flag 0).
- **Continue hint:** Japanese, 38/38 cells (same renderer, flag 0).

## Conclusion

**CONFIRMED.** The Saturn keeps the arcade's English quote layout (2 × 25 at
12 px). A per-task patch in `MMPACK.PCA` turns it on for Ryu's win quotes
only, with his official English records replacing the start of his Japanese
quote table in `MC09.SHP`. From a cold boot of the rebuilt image, Ryu's
quotes show in English, while other characters' quotes and the continue
hints draw exactly as in the unpatched game. Every arcade English record
fits as written.

## Uncertainty and Alternatives

- **Endings** (gated, rule 23): not reached. The ending selector's language
  read is now a constant 0, the value it read before.
- **Fixed-index mode** (`0xD083`): not reached. Its path now goes through
  the slot test.
- **Type-6 selector:** not reached. Its own language read is unchanged and
  reads the global word, which is still 0.
- **Other characters:** each needs its slot added to the test. The test
  compares a single slot now; more need a small table (`RE-005`).
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect:

- the file and track hashes above;
- 50/50 cells for English runs and 38/38 for others;
- `storm_v2` byte-identical to `storm_orig`.
