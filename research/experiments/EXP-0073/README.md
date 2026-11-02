# EXP-0073 (Text): A Static Scan for Rare Text

Task: TXT-001
Status: DONE (2026-11-01)
Confidence: CONFIRMED for the quote-font text on the disc (a scan with a
measured filter); other encodings are outside it

## Observation

`TXT-001` asked for text the normal game never shows. The user chose a
static scan first ("Static scan, then decide (Recommended)").

## Method (`text_scan.py`)

Every file of the untouched track (236 in the ISO listing), decoded with
`tools.disc.prs` when it decodes, was scanned for runs of quote-font codes
(the space `0x0020`, `0x0900`-`0x0DFF`, the arrows `0x0130`-`0x013F`; on
Ryu's table, non-space codes run `0x09E1`-`0x0DDE`), at least 19 words with
at least 4 non-space codes, joined within 64 bytes into blocks
(`local/txt001/blocks.json`, 92 blocks). Each block was profiled: share of
spaces, share of distinct codes, high-byte spread.

## Result

- **Text:** every block with spaces is a table already known: the 18 quote
  tables (which hold the Japanese endings), Apocalypse's boxes (`MC08`
  `0x1090`) and the hint table (`MMPACK.PCA`). Their spaces run 19-63% of
  codes, distinct codes 9-24%.
- **Not text:** every other block has no spaces at all and mostly distinct,
  often consecutive codes (`CPK.CPK`, `BGCELL09.PCA`, the `MSxx.SHP`
  files, small blocks in the fighter files and `MCED.SHP`): number tables.
  The one with spaces, `MMPACK.PCA` decoded `0x6C138` (RAM `0x06080CD8`), is
  a space-separated descending run `0x0959`-`0x0950`, referenced from
  `0x0607ED34` beside the life-bar code: display cells, not a sentence.
- **`.TXT` files:** `ABS.TXT`, `BIB.TXT`, `CPY.TXT` are the disc's
  abstract, bibliographic and copyright files named by its volume
  descriptor; the game does not display them.
- **Unreached records** in the known tables are already recorded: hint
  records 16-20 (D-058, `docs/known_unknowns.md`); each slot's English
  record 8 (D-025); slot 8's ending records, the tails of the old Japanese
  endings and the unused Japanese scripts (`docs/coverage_exceptions.md`,
  M8 register); the sign's two other variants (`NOCH-001`).

## Uncertainty

Text in another encoding (a different font's codes, Shift-JIS, pictures)
would not be found by this filter. The screens found so far that use
pictures (warnings, captions, signs, the QSound notice) are inventoried in
`docs/text_surfaces.md`.

## Reproduction

```bash
./invenv.sh python research/experiments/EXP-0073/text_scan.py local/txt001/blocks.json
```

**The user's decision** (verbatim): "Leave them (Recommended)".
