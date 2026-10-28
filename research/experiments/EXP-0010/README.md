# EXP-0010: Compare the PS1 US English With the Arcade

Task: REF-006
Status: DONE
Confidence: CONFIRMED

## Observation

The US PS1 image is identity-confirmed (`REF-002`). MSHvSF found its PS1
port storing the arcade's English blocks byte-identically in little-endian
order (MSHvSF `EXP-0032`); for XvSF that was a hypothesis.

## Hypothesis

The XvSF US PS1 disc holds the arcade's English records (`EXP-0008`)
byte-identically apart from byte order.

## Controlled Change

None; read-only analysis of the extracted PS1 files.

## Prediction

Most or all 294 arcade records found in one PS1 file, byte-swapped.

## Inputs and Provenance

- PS1 US image `local/disc_images/xmvsf_ps1_us/X-Men vs. Street Fighter
  (USA).bin` (`13e66a3e…b519`, `references/ps1/README.md`).
- `tools/disc/iso9660.py` (copied from MSHvSF `69c666c`) listed 295 entries
  and extracted 269 files to the ignored `local/ref006/files/`.
- Arcade program `xmvsfu`, 68000 order, from `tools/reference/xvsf_text.py`.

## Tools and Environment

[`compare.py`](compare.py) (offsets and record numbers only; no text).

## Procedure

```bash
./invenv.sh python -m tools.disc.iso9660 \
  "local/disc_images/xmvsf_ps1_us/X-Men vs. Street Fighter (USA).bin" \
  --extract local/ref006/files > local/ref006/listing.json
./invenv.sh python research/experiments/EXP-0010/compare.py \
  local/ref003/xmvsfu-68k.bin local/ref006/files/P/P4/SELECT.BIN
```

Every one of the 294 arcade records was first searched for in all 269
files, in both byte orders.

## Actual Result

- **Location:** 293 of 294 records occur, all in `P/P4/SELECT.BIN`
  (LSN 142996, 167,108 bytes, `3fd5810b…e53c`), little-endian, each
  byte-identical to the arcade record. No other file holds any.
- **Missing:** record 293 only, the arcade's one-line "coming soon" text.
- **Layout per surface:**

  | Surface | Arcade records | PS1 | Comparison |
  | --- | --- | --- | --- |
  | Win quotes | 0-160 | `0x1E8CC`, contiguous, same order | 161 of 161 identical |
  | Endings | 161-269 | `0x10788`, contiguous, same order | 109 of 109 identical |
  | Hints, set A | 270-292 | right after the win quotes | 22 records: the arcade hints in order **without record 286**, identical |
  | Hints, set B | — | after set A | 23 records: 16 arcade records (277 twice; 286 only here) and **7 PS1-only records**, which reword button inputs (`P K`, `P or K` where the arcade has `HP HK`) and the tag-switch advice |
  | "Coming soon" line | 293 | absent | — |

- **Other languages:** the arcade's Spanish, Portuguese and Japanese tables
  occur in no PS1 file (first 64 bytes of each table's slot 0, both byte
  orders).

## Conclusion

**CONFIRMED.**
- The US PS1 is a byte-identical second source for the arcade English **win
  quotes and endings**, and for the arcade hints (set A, less one record).
- It adds one PS1-specific hint variant (set B) with 7 rewritten records.
- It adds no other English for these surfaces.
- It is not a source for Spanish, Portuguese or Japanese.

## Uncertainty and Alternatives

- What selects set B, and which PS1 mode shows it, was not observed. The
  rewrites suggest a mode without tag switching, but that is HYPOTHESIS.
- Attract captions were not compared. They are graphics in the arcade
  (`EXP-0008`), and comparing them needs the PS1 running, which needs a PS1
  BIOS (MSHvSF `EXP-0072` used the user's).
- The JP EX PS1 image (`REF-002`, UNKNOWN identity) was not examined.

## Reproduction

Run the procedure. Expect `found 293`, `missing [293]`, the five groups
above, and the 206-record run listing win quotes, set A and set B.
