# EXP-0009: Confirm Decoded Arcade Text on Screen, and Its Selector

Task: REF-004
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0008` decoded 294 English records from the arcade program ROM but had
not seen any of them on the arcade screen. The playbook warns that a pointer
seen in RAM may persist and is not necessarily the selector (MSHvSF
`EXP-0030`).

## Hypothesis

A scripted MAME route on the US set reaches a win quote. The arcade then
reads one decoded record and draws exactly its text. A work-RAM pointer
selects which record is read.

## Controlled Change

Input only (route), then one forced RAM word per run (`force16`, which
replaces CPU writes to that word).

## Prediction

The read tap on the English area logs the shown record; the screen shows the
decoder's text for it. Forcing the selector to another slot's base makes the
game read and draw that slot's record at the same index.

## Inputs and Provenance

`xmvsfu` (USA 961023) from `local/arcade_roms/xmvsf_mame0289/` (`REF-001`),
MAME 0.289. Decoder `tools/reference/xvsf_text.py`. Timeline script
`tools/reference/mame_timeline.lua`, copied from MSHvSF `69c666c` (body
unchanged).

## Tools and Environment

Headless MAME (`-video none -sound none -nothrottle`); timelines in
[`timelines/`](timelines/).

## Procedure

```bash
MAME_TIMELINE=research/experiments/EXP-0009/timelines/run3.txt mame xmvsfu \
  -rompath local/arcade_roms/xmvsf_mame0289 -video none -sound none -nothrottle \
  -skip_gameinfo -nomouse -cfg_directory local/ref004/cfg -nvram_directory local/ref004/nvram \
  -snapshot_directory local/ref004/run3/snap -homepath local/ref004 \
  -autoboot_script tools/reference/mame_timeline.lua
```

- Route (run 3): four coins at frame 1000 (the set's coinage is 2 coins per
  credit; runs 1-2 with one coin stayed at "CREDIT 0(1/2)"), Start every 60
  frames from 1200, button 1 every 30 frames from 1900 to 3100, then no
  input; `logreads 0x186EA2 0x18E179` from frame 1; a snapshot every 60
  frames.
- Run 4: same route with work-RAM dumps (`0xFF0000`-`0xFFFFFF`) at frames
  6100-6600. Run 5: `force16 0xFF2492 0x986E`. Run 6: write logs on
  `0xFF2490`, `0xFF2492`, `0xFF8BB4`, `0xFF8BB6`. Run 7:
  `force16 0xFF8BB6 0x6EA2`.

## Actual Result

- Run 3: the CPU team (Dhalsim, Sabretooth) won. Reads logged:
  frame 6211 PC `0x04F612` at `0x189936`; frame 6515 at `0x18D81A`;
  frame 6897 at `0x18D87E`. That is win-quote slot 12, record 2 (record 109
  of the area), then hint records 270 and 271.
- **On screen** (agent-reviewed): the speech bubble at frame 6280 shows both
  lines of record 109 exactly, including its `;` (`0x06DB`) (snapshot
  `961030f4…791e`). The continue screen shows record 270 at frame 6520
  (`e8fd7499…6e6f`), then record 271 at frame 6940 (`2da4f238…d3f3`); code
  `0x0134` is drawn as ↑.
- Run 4 reproduced run 3 exactly (same read log; frame 6280 snapshot
  byte-identical). Two-state search: `0xFF2490` holds `0x00189936` at frames
  6215-6400 and not at 6210; `0xFF8BB4` holds `0x0018986E` (slot 12's base).
- Run 5 (force `0xFF2492`): no change; the game still read `0x189936` and
  drew record 109.
- Run 6: in frame 6211, PC `0x04F3DA` writes `0x0018986E` to `0xFF8BB4`,
  then PC `0x04F594` writes the record address to `0xFF2490`, then
  `0x04F612` reads the text. At 6515 and 6897 `0x04F594` writes the hint
  record addresses.
- **Run 7** (force `0xFF8BB6` to `0x6EA2`, slot 0's base): the game read
  `0x186F6A` (slot 0, record 2) and drew its two lines, exactly the
  decoder's prediction (`643a8338…feb5`).

## Conclusion

**CONFIRMED.**
- The arcade draws the decoded records as two lines, both for win quotes
  and for continue hints (one hint page per record).
- Code `0x0134` is ↑.
- Work RAM `0xFF8BB4` holds the speaker's win-quote slot base, from which
  the record address is computed. Forcing it chooses the slot shown.
- `0xFF2490` is a copy of the printed record's address, not the selector.
- The US set shows the English table.

## Uncertainty and Alternatives

- How the record index (2 here) is chosen is not traced; the index came
  from the game, not from RAM forced here.
- Only one win quote and one hint were shown; the other arrow codes remain
  HYPOTHESIS.
- Only the US region was run; which table other regions show is not
  observed.

## Reproduction

Run `timelines/run3.txt` and `run7.txt` as above. Expect the read logs and
the two speech-bubble texts listed in "Actual Result".
