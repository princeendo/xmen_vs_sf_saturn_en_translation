# EXP-0020: Latin Codes, Line Length and Cell Grid in the Win Quote

Task: FONT-002
Status: DONE
Confidence: CONFIRMED

## Observation

The quote font is `FIX.PRS`, decoded by `tools/text/font.py` (`EXP-0019`).
The arcade's English text uses a tile-sheet ASCII map: printable ASCII row
`0x2_`-`0x7_` starts at `0x670`, `0x6D0`, `0x680`, `0x6E0`, `0x690` and
`0x6F0`, and space is `0x0020` (`EXP-0008`). A Saturn quote record is 2 × 19
codes (`EXP-0015`); an arcade English record is 2 × 25.

## Hypothesis

The Saturn font holds Latin glyphs at the arcade English codes. Written into
a quote record, they draw as predicted in all 2 × 19 cells.

## Controlled Change

From `pre_ko`, paused, each trial writes 38 codes (76 bytes) over record 10
at WRAM-L `0x0024F8D0`. The original bytes are recorded per run in
`result.json`; the M1 record is `EXP-0016`'s. The control writes nothing.

| Trial | Line 1 | Line 2 |
| --- | --- | --- |
| `upper_lower` | `ABCDEFGHIJKLMNOPQRS` | `abcdefghijklmnopqrs` |
| `rest_digits` | `TUVWXYZ0123456789!?` | `tuvwxyz.,'-:;()&"/%` |
| `symbols` | ``#$*+<=>@[\]^_`{\|}~`` (18) | blank |

Codes come from `tools.reference.xvsf_text.DECODE`; padding is `0x0020`.

## Prediction

- Every drawn VDP1 cell equals `font.glyph(code)` decoded from `FIX.PRS`.
- Both lines show all 19 cells.
- The control is byte-identical to the live capture (`e006ebd8…`).

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| `pre_ko` checkpoint | `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0014`) |
| Emulator | patched build (`EXP-0006`), silent home |
| Font | `FIX.PRS` `68032831…0bab` (`references/saturn_jp/iso_listing.json`) |
| Arcade English | `local/ref003/xmvsf-68k.bin` (`EXP-0008`) |
| Source image | hashes match `references/saturn_jp/README.md` afterwards (`local/logs/font002-source-after.json`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/font.py` | Atlas renders and per-code checks |
| [`latin_trial.py`](latin_trial.py) | Runs the trials; reads VDP1 VRAM through the agent's `vdp1vram` space |
| [`cell_compare.py`](cell_compare.py) | Compares drawn cells with decoded glyphs |

## Procedure

```bash
./invenv.sh python -m tools.text.font local/ref007/saturn_files/FIX.PRS \
  --region file --first 0x600 --count 512 --render local/font002/atlas.png
./invenv.sh python research/experiments/EXP-0020/latin_trial.py local/font002/run1
./invenv.sh python research/experiments/EXP-0020/cell_compare.py local/font002/run1 \
  local/ref007/saturn_files/FIX.PRS
./invenv.sh python research/experiments/EXP-0020/latin_trial.py local/font002/run2
```

## Actual Result

**Latin sets in the font** (atlas, agent-reviewed):

| Codes | Contents |
| --- | --- |
| `0x0021`-`0x007E` | small ASCII |
| `0x00A1`-`0x00FF` | italic ASCII |
| `0x0100`-`0x013F` | accented letters |
| around `0x01F0` | bold outlined alphanumerics |
| `0x0660`-`0x06FF` | **quote-style 16×16 italic** set, in the arcade map's layout, with accented letters at `0x06A0`-`0x06BF` |

- All 94 printable-ASCII codes of the arcade map have non-empty glyphs.
- Spot renders match the map: `0x0681` A, `0x0691` a, `0x06D0` 0, `0x06E0`
  P, `0x06F0` p, `0x0671` !.
- Four codes are not ASCII glyphs: `0x0680` (`@`) is ♥, and `0x06FB`-`0x06FD`
  (`{ | }`) are two fraction signs and ∞.

**Live display** (two runs, byte-identical screenshots and VDP1 VRAM):

| Run | Screenshots (660 and 720 frames) | Cells exact | Distinct cells |
| --- | --- | --- | --- |
| control | `e006ebd8…` both (= live capture) | 38/38 | 22 |
| `upper_lower` | `7827979f…` both | 38/38 | 38 |
| `rest_digits` | `885617c9…` both | 38/38 | 38 |
| `symbols` | `6f484263…` both | 38/38 | 19 |

- **Layout:** every run draws 38 sprites in two rows (y = 178, 194) at
  x = 26-314, step 16, inside the bubble. All 19 cells of each line are shown.
- **Cell capacity:** 38 distinct glyph cells were allocated without
  corruption.
- **On screen** (agent-reviewed crops): the trial strings are legible, in
  gray italic.

**Glyph widths.** The ink, shadow included, spans 6-15 of 16 columns for
A-Z, 6-13 for a-z and 6-14 for digits. These are full-cell glyphs.

**Capacity against the arcade English.**

- 161 win-quote records, left-aligned, with lines ending at code 6-25.
- 25 fit 2 × 19 as written.
- **59 fit after re-wrapping at word boundaries; 159 would fit 3 × 19.**
- The longest is 51 characters.

## Conclusion

**CONFIRMED:**

- The Saturn quote font draws the arcade English codes directly: the same
  tile-sheet ASCII map, with space `0x0020`. The exceptions are `@ { | }`
  (♥, two fractions, ∞).
- A quote line is 19 cells of 16 px, and a record is 2 lines (38 cells).
  Every cell, and 38 distinct glyphs, display.
- Only 59 of 161 arcade English win quotes fit the 2 × 19 grid after
  re-wrapping. The rest need a layout change: shorter glyphs packed two per
  cell, a third line, or edited wording. That is a later task.

## Uncertainty and Alternatives

- Tested from one checkpoint, on record 10 only.
- Whether a record can grow (more lines, or wider cells) without code changes
  is not tested.
- The gray look of the Latin set and its readability on a real TV are not
  assessed.
- The other Latin sets (small, italic, bold, accented) were not displayed.

## Reproduction

Run the procedure. Expect:

- the screenshot hashes above;
- 38/38 exact cells per run from `cell_compare.py`.
