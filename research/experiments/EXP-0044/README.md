# EXP-0044 (M8): Arcade Pairing for Every Roster Ending

Task: END-012
Status: IN_PROGRESS
Confidence: UNKNOWN (predictions registered; logged runs pending)

## Observation

- **Arcade** (`EXP-0037`, D-032): Charlie's arcade ending reads his ending
  record k on page k in either language, with either partner.
- **Saturn** (`EXP-0043`, D-038): every M8 roster slot (`END-011`: slots
  0-7 and 9-17) has a Saturn English script showing its arcade English
  records in order.
- **What remains:** that each character's arcade ending reads its records
  that way, and what each English page shows.

## Route (found before the predictions)

`make_timeline.py` and `run_mame.py`, generalized from `EXP-0037`:

- **Grid picks:** the first pick is made with the cursor moves in
  `MOVES`, from the start cell (Cyclops). Probe runs (`timelines/probe_*`,
  select snapshots at frame 2,000) showed the intended character's
  portrait for all 16 grid characters. The partner is whoever button 1
  picks next, unless `right` is given.
- **The character word:** Gouki is not on the grid. Work-RAM dumps at
  frames 2,300 and 3,000 after three picks (Wolverine, Ryu, Charlie;
  `timelines/charword_*`) held the first pick's slot × 2 (0, 18, 32) in
  seven words: `0xFF4052`, `0xFF44B4`, `0xFF4A22`, `0xFF4CB4`, `0xFF50B0`,
  `0xFF7062` and `0xFFA012`.
- **Gouki by forcing:** writing `0x1E` (slot 15 × 2) to all seven every 4
  frames, from 1,830 to 3,700, made Gouki the first pick
  (`timelines/gouki_probe.txt`):
  - the win selector read slot 15's table (`0x17E224`) and the ending
    selector `0x17E354`;
  - the snapshots show Gouki's win quote and an English ending of Gouki and
    Wolverine.

  This is a forced pick, not a play route.
- **Seen before the predictions:** the Gouki probe ran to the ending and
  showed English table reads at frames 15,058 and 16,719. It is the only
  roster ending seen before the predictions (besides Charlie's in
  `EXP-0037`).

## Predictions (registered before the logged runs)

`predictions.json` (written by `predict.py` from the censuses, committed
before any read-logged run). For each roster slot and language:

1. **Table:** the ending selector reads the slot's table entry
   (`0x17E318` + 4·slot, or `0x17E2CC` + 4·slot).
2. **Records:** page k reads pointer + 100k (English) or + 76k
   (Japanese), for k = 0 to n − 1. n is the arcade English count, or the
   Saturn Japanese count.
3. **Scenes:** the selector re-reads its table on exactly the pages where
   the slot's `MCED` script of that language starts a scene. For Charlie
   that gives 1, 2, 4, 5 and 1, 3, 5, 6, as measured in `EXP-0037`.
4. **Partners:** for slots 0 (Wolverine) and 11 (Chun-Li), a second
   partner changes nothing.

**What would refute them:** any other table or record, another count or
order, table re-reads on other pages, or a partner effect.
