# EXP-0039 (M7): Layout Options for Nash's English Ending

Task: LAYOUT-002
Status: DONE
Confidence: CONFIRMED (both trials); the choice is the user's

## Observation

`EXP-0038` (D-033) showed the Saturn has its own English scene script for
Nash's ending. With it, the arcade English records reproduce the arcade's
English ending page for page. `LAYOUT-002` asks the user to choose a layout
from measured options, each with RAM-trial screenshots of all six pages.

## Options Measured

| Option | RAM trial | Code reads switched to English | Data |
| --- | --- | --- | --- |
| (a) English script | `EXP-0038` `english_trial.py` (`local/end005/trial1`) | `MCED` script reader `0x060D4738`, type-4 selector `0x060668C4`, renderer's six grid reads | 6 × 100 bytes plus a record pointer |
| (b) Japanese script, English text | `english_trial.py ... japanese-script` (`local/end005/trial_b`) | type-4 selector and renderer only | the same |

Both trials start from `local/checkpoints/end001/f00220064.mcs` (untouched
image, no input). The global words stay 0. In both, the scratch region in
WRAM-L held only the written bytes at the end. Trial (b) made 10 writes,
because the script reader was left alone.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0038/english_trial.py local/end005/trial1
./invenv.sh python research/experiments/EXP-0038/english_trial.py local/end005/trial_b japanese-script
```

`english_trial.py` gained the `japanese-script` option for this task.
Without it, the script runs exactly as in `EXP-0038`.

## Actual Result

### Option (b): page changes

The pointer read `0x00259200` + 100k, one record per page, on the Japanese
timing: frames 220,560, 220,830, 221,070, 221,340, 221,610, 221,940. That
is about 4.3 s per page; the arcade's English pages are about 6.4 s.

### Side by side (agent-reviewed, mid-page screenshots)

| Page | English text | (a) picture, label | (b) picture, label | Fit in (b) |
| --- | --- | --- | --- | --- |
| 1 | record 0 | black, none | black, none | same |
| 2 | record 1 (names Charlie) | captive, none | black, none | picture missing |
| 3 | record 2 (the operation) | captive, none | captive, `Nash` | label added |
| 4 | record 3 (the scream) | black, `Charlie` | captive, `Nazo no koe` | the scream is credited to the "mysterious voice" |
| 5 | record 4 (the dog tags; names Charlie) | Guile, `Charlie's friend` | black, `Nash` | Guile's line labelled `Nash`, no picture |
| 6 | record 5 (revenge) | Guile, none | Guile, `Nash's friend` | label added |

Screenshot hashes:

| Page | (a) | (b) |
| --- | --- | --- |
| 1 | `f00220680` `65ae6f95…` | `f00220680` `65ae6f95…` |
| 2 | `f00221070` `456fee1d…` | `f00220950` `e9ca6ab3…` |
| 3 | `f00221460` `a5661877…` | `f00221220` `99992c4d…` |
| 4 | `f00221850` `fc8fe0c5…` | `f00221460` `8e39e9a0…` |
| 5 | `f00222240` `bdfbd8b7…` | `f00221760` `99742c21…` |
| 6 | `f00222630` `55a9d2cd…` | `f00222120` `f866a3ca…` |

Page 1 is identical in both.

### Costs

- **(a):** one more code read to switch (the `MCED` script reader). The
  pictures, labels, timing and text all match the arcade. The labels need
  no data change.
- **(b):** one fewer read. Pages 2-6 differ from the arcade, three of them
  in meaning (pages 4 and 5, and page 3's label), and the labels say `Nash`
  while the text says "Charlie".
- **Data:** the same 600 bytes of records for both.

## User Decision (2026-10-29)

The user was shown the six pages of both options side by side.

| Question | Answer (verbatim) |
| --- | --- |
| "Which layout should Nash's English ending use?" | "(a) English layout (Recommended)" |
| "Which speaker names should the English ending show?" | "Arcade names (Recommended)" |

Recorded in `docs/localization_policy.md`.

## Conclusion

Nash's English ending uses the Saturn's own English scene script (option
(a)), with the arcade's labels `Charlie` and `Charlie's friend`. `END-006`
must switch the `MCED` script reader, the type-4 selector and the renderer
to English for slot 16's ending only. `END-007` places the six records.
Before `END-008`, the `GATE-TRANSLATION` extension for Nash's ending is
still needed.
