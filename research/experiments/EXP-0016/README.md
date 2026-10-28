# EXP-0016 (M1): Change Ryu's Win Quote in Live RAM

Task: RE-001
Status: DONE
Confidence: CONFIRMED

## Observation

The M1 quote is record 10 of a WRAM-L table of 16-bit glyph codes at
`0x0024F5D8`, resident from before the K.O.; hiragana codes are Unicode −
`0x2661` (`EXP-0015`). The user passed `GATE-M0` on 2026-10-28.

## Hypothesis

Writing known codes into record 10 at the `pre_ko` checkpoint changes exactly
those glyphs on the quote screen.

## Controlled Change

One write of 6 bytes (`AGENTS.md` rule 12):

| Field | Value |
| --- | --- |
| Address | WRAM-L `0x0024F8D6` (record 10, line 1, cells 3-5) |
| Original bytes | `0A21 09E5 0AC8` (も う 一) |
| Written bytes | `09E1 09E3 09E5` (あ い う, from Unicode − `0x2661`) |
| Purpose | First live-RAM change of the win quote (M1) |
| Expected | Line 1 reads あいう度鍛え直してこい。; nothing else changes |
| Observed | As expected (below) |

The control runs the same steps from the same state without the write.

## Prediction

Trial: line 1 shows あいう in cells 3-5, the rest of the screen identical to
the control. Control: the original quote, as in the live session.

## Inputs and Provenance

`pre_ko` checkpoint `local/checkpoints/dbg003/f00009769.mcs`
(`911c14d6…b09d`, `EXP-0014`); patched build (`EXP-0006`); silent home.

## Tools and Environment

[`m1_trial.py`](m1_trial.py): load state, pause, read the record, (write),
read back, run 660 frames, screenshot, run 60 more, screenshot, read the
record again.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0016/m1_trial.py local/re001/run1
```

Source image hashed before and after (`local/logs/re001-source-*.json`).

## Actual Result

- **Record:** control unchanged throughout. Trial read back the written
  bytes after the write and still held them at the quote screen.
- **Screens** (agent-reviewed):

  | Run | Screenshots (660, 720 frames) | Line 1 |
  | --- | --- | --- |
  | Control | `e006ebd8…` both, byte-identical to the live session's quote | もう一度鍛え直してこい。 |
  | Trial | `8abc96d6…` both | **あいう度鍛え直してこい。** |

- **Pixel diff, trial vs control:** 318 pixels differ, all within x 75-120,
  y 187-200, which is cells 3-5 of line 1's text row. Line 2, the bubble and
  the portraits are identical.
- `あ`, a glyph the original quote never used, rendered correctly.
- Source image identical before and after.

## Conclusion

**CONFIRMED (M1).** Ryu's win quote was visibly changed in live Saturn RAM by
writing known codes into its WRAM-L record, with a no-write control showing
the original. The hiragana code relation holds for a new glyph.

## Uncertainty and Alternatives

- Only hiragana were tested; Latin letters and the font's capacity are
  `FONT-001`/`FONT-002` (M2).
- Live RAM only. The record's disc source is `DISC-001` (M2).
- One record of one character.

## Reproduction

Run the procedure; expect the two screenshot hashes above.
