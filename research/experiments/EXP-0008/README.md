# EXP-0008: Locate and Decode the Arcade English Text

Task: REF-003
Status: DONE
Confidence: CONFIRMED (location, character map, table shape, regional sameness); HYPOTHESIS (arrow codes, hint grouping, region-to-language selection)

## Observation

The arcade is the translation oracle (`docs/localization_policy.md`).
MSHvSF's arcade quotes were 16-bit codes with `A` = `0x0140` (MSHvSF
`EXP-0029`); for XvSF that is only a hypothesis. CPS-II encryption covers
opcode fetches, so data in the program ROM should be readable as stored.

## Hypothesis

XvSF's English win quotes and endings are stored as fixed-format character
codes in the 68000 program ROM, findable by a relative search that assumes
nothing about the code values.

## Controlled Change

None; read-only analysis of the held zips (`REF-001`).

## Prediction

A constant-offset run for common English words at 8- or 16-bit width, then a
character map that decodes whole tables with no leftover codes.

## Inputs and Provenance

Zips in `local/arcade_roms/xmvsf_mame0289/` (`references/arcade/manifest.json`),
set definitions from the pinned MAME 0.289 `cps2.cpp` (SHA-256
`a8c09ef8…1602`). The `maincpu` region is rebuilt from `ROM_LOAD16_WORD_SWAP`
entries with each 16-bit word swapped into 68000 order (the order in which the
stage names read as ASCII).

## Tools and Environment

[`relsearch.py`](relsearch.py) (exploration); `tools/reference/xvsf_text.py`
(decoder and report; game text goes only to the ignored `local/ref003/`).

## Procedure

```bash
./invenv.sh python -m tools.reference.xvsf_text --driver local/mame_src/cps2.cpp \
  --set xmvsfu --rompath local/arcade_roms/xmvsf_mame0289 --out local/ref003/report-xmvsfu.json
```

Exploration, in order:

1. Relative search of on-screen words: stage names and UI words are plain
   8-bit ASCII near `0x4300`-`0x4D20` (68000 order). Long ASCII runs are boot,
   legal and test-menu text; no quotes.
2. MSHvSF's 16-bit map (`A` = `0x0140`, `a` = `0x0161`, space `0x0020`): **0**
   phrase runs in three sets. **DISPROVEN** for XvSF.
3. Offset histogram of `THE YOU AND YOUR FIGHT` at both widths: peaks at
   16-bit offsets 160 and 1616/1584. Offset 160 (with lowercase text) gave
   **ASCII + 0x80**: Spanish and Portuguese quotes and endings, accents above
   `0x00FF`.
4. Lowercase-tail search (`hadaloo`, offset 1584) found single-case English;
   context fixed a tile-sheet map: code = row base + (ASCII & 0xF), row bases
   `0x20`→`0x0670`, `0x30`→`0x06D0`, `0x40`→`0x0680`, `0x50`→`0x06E0`,
   `0x60`→`0x0690`, `0x70`→`0x06F0`; space `0x0020`.
5. Pointer tables found by scanning for longs into the block; the record
   grid from their targets.

## Actual Result

- **English area:** `0x186EA2`-`0x18E17A` in shared ROM `xvs.06a`, exactly
  294 records of 2 × 25 codes, left-aligned lines padded with spaces:
  - win quotes, records 0-160: table `0x17E1E8`, 19 pointers; 17 slots of 9
    records and one of 8; two slots alias earlier slots (161 unique records);
  - endings, records 161-269: table `0x17E318`, 19 pointers, 4-13 records per
    slot (109 unique records);
  - gameplay hints, records 270-292: no pointer table found;
  - record 293: a one-record "coming soon" line.
- **Other languages:** each English table has Spanish (`0x17E234`,
  `0x17E364`) and Portuguese (`0x17E280`, `0x17E3B0`) twins in ASCII + 0x80,
  and Japanese twins (`0x17E19C`, `0x17E2CC`) in codes `0x09E0`-`0x0Dxx`,
  not decoded.
- **Decoder output:** no unmapped codes in win quotes or endings. The hints
  hold six unmapped codes `0x0134`-`0x013A`.
- **Punctuation, statistically** (win quotes and endings; share in the
  expected context): `.` 248/262 (95%, after a letter and before a space,
  punctuation or end), `!` 102/108 (94%), `,` 66/70 (94%, before a space),
  `?` 30/32 (94%), `'` 91/103 (88%, between letters), `-` 11/11 (100%,
  between letters), `"` 6/8. The exceptions are line-end positions (a full
  25-code line next to the following line's first letter) and word-final
  apostrophes ("talkin'").
- **Cross-checks:** character names in the decoded text agree with the
  plain 16-bit-ASCII name list at `0x503E4` (a different encoding). The two
  Saturn continue hints seen in `EXP-0007` (Advancing Guard; the safe-fall
  input) correspond in content to hint records 272-273 and 282-283. The
  Saturn's ←↙↓ arrows sit where record 282 has `013A 0139 0138`.
- **Regions:** in all 11 held sets the program bytes `0x17E000`-`0x1A0000`
  are identical (SHA-256 prefix `05a0c0e9727d`) except Japan 960909
  (`xmvsfjr4`, `96cef9781b13`). There the same 294 records are identical
  but start `0x4C` bytes earlier (`0x186E56`). No region ROM holds a copy.

## Conclusion

**CONFIRMED:** the arcade English win quotes, endings and hints are fixed
2 × 25-code records in the shared program ROM, decoded by the tile-sheet map
with no leftover codes outside the hints. Every held set carries the same
English (and the Spanish, Portuguese and Japanese twins). MSHvSF's map does
not apply.

## Uncertainty and Alternatives

- **Arrow codes (HYPOTHESIS):** `0x0134`-`0x013A` are joystick arrows
  running clockwise from ↑ (`0x0134` ↑, `0x0136` →, `0x0137` ↘, `0x0138` ↓,
  `0x0139` ↙, `0x013A` ←). This rests on hint context and one Saturn
  screenshot. The decoder still prints them as `{xxxx}`.
- **Hint grouping:** two records per hint fits records 272-273 and 282-283,
  but 23 records cannot all pair. The grouping is UNKNOWN.
- **Region-to-language selection:** which table each region shows is not
  observed; that is `REF-004`.
- **Slot order:** slot 0 is Wolverine; the order of the other slots is not
  established.
- **Display:** that the arcade draws these records as two 25-code lines is
  `REF-004`'s on-screen check.

## Reproduction

Run the procedure for each set. Expect `win_quotes 161`, `endings 109`,
`hints 23` and the same unmapped list.
