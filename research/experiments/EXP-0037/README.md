# EXP-0037 (M6): Arcade English and Indexing for Nash's Ending

Task: END-004
Status: IN_PROGRESS
Confidence: UNKNOWN (predictions registered; runs pending)

## Observation

- **Saturn** (`EXP-0035`, `EXP-0036`): Nash's ending shows six pages, read
  in order from decoded `MC10.SHP` records 16-21. Those are the arcade's
  Japanese ending block for slot 16, records 0-5 (`EXP-0029` census,
  `data/text/ending_census.json`).
- **Arcade:** its English ending block for slot 16 also has 6 records
  (table `0x17E318`, 100-byte records).
- **Unknown:** no arcade ending has been reached, and how the arcade picks
  ending records is unknown.

## Route (found before the predictions)

`timelines/discover1.txt` and `timelines/discover2.txt`, run by
`run_mame.py`:

- **Pick:** Charlie is picked first on `xmvsfu` by Up, Right, Right from the
  start cell (Cyclops), then button 1. The partner is whatever button 1
  picks next; in `discover1` that was Cyclops.
- **Vitality:** the four fighters use 0x400-byte blocks from `0xFF4200`,
  with vitality at +`0x10` (144 at full). It was found from work-RAM dumps
  of an idle fight (`discover1`). Only `0xFF5042`, `0xFF4210` and
  `0xFF4A10` changed as the player's side was hit; `0xFF4610` and
  `0xFF4E10` stayed at 144.
- **No-play route** (`discover2`): `w@ff4610=0` and `w@ff4e10=0` every 20
  frames from frame 3750. Charlie and Cyclops won every stage, Apocalypse
  and a final Charlie-against-Cyclops fight. Charlie's ending followed, in
  English, then the staff roll and `GAME OVER`. (Snapshots every 300
  frames, reviewed by the agent.)

So one combination (partner Cyclops, English) was seen on screen before
these predictions were written. No record read was logged in that run.

## Predictions (registered before the logged runs)

Written and committed before any run that logs reads.

1. **Records follow the point character.** With Charlie first, the ending
   reads slot 16's English ending records 0, 1, 2, 3, 4, 5 in that order,
   one per page, from the slot-16 English pointer at table `0x17E318`. This
   holds with partner **Cyclops** (slot 1) and with partner **Ryu** (slot
   9), with the same six records each time. The partner changes no record.
2. **Japanese:** with the language and size words set to 0 (the `EXP-0022`
   method), the same pages read slot 16's Japanese ending records 0-5 in
   order (table `0x17E2CC`). These are the records the Saturn shows from
   `MC10` records 16-21.
3. **Pairing:** therefore Saturn `MC10` record 16 + k pairs with arcade
   English slot 16 record k, for k = 0-5.
4. **Labels:** the arcade English pages show no speaker label from the text
   tables. If a label appears, it is drawn from somewhere other than the
   ending records. This one is a weak prediction: the `EXP-0035` English
   mode on the Saturn showed a `Charlie` label.

**What would refute them:**

- a different record set or order between the two partners;
- reads outside slot 16's blocks;
- more or fewer than six reads;
- a Japanese run reading other records.
