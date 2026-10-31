# EXP-0060 (Special): The User's Plan for the Special Cases

Task: SPEC-003
Status: DONE
Confidence: CONFIRMED (the user's answers, recorded verbatim; every
approved line checked against its source record and the layout)

## Observation

`EXP-0059` (D-053) found the following:

- **Boss boxes:** no official English exists for Apocalypse's boxes. The
  US arcade skips them. The Saturn box code draws 2 × 19 wide cells.
- **Post-boss quote:** each slot's fixed English record, already built.
- **Alpha Chun-Li:** she shows garbled English, then Japanese, in the
  builds. Her table word at `0x0285` showed Chun-Li's English, as the
  arcade does.

## The Questions

Two questions were put to the user, with Ryu's boxes as a sample in both
layouts:

| Question (short) | Options | Answer |
| --- | --- | --- |
| What should the builds show in Apocalypse's boxes? | New English in the quote layout (2 × 25; needs a box-code change, not yet tried); new English in the existing 2 × 19 wide layout; skip them like the US arcade; leave them Japanese | "New English, quote layout (Recommended)" |
| Switch Alpha Chun-Li to Chun-Li's official English? | Yes (word `0x0285`); no | "Yes, Chun-Li's English (Recommended)" |

## The Translation

The agent read the 54 Japanese records (`EXP-0059`, `boxes_0-2.png`) and
drafted English for the 36 distinct ones:

- 17 player lines;
- 17 replies by Apocalypse;
- 2 versions of "behold my true form".

Slot 8 repeats slot 7's records, and its third record is version A
([`draft.json`](draft.json)).

- **Names:** the second box of slots 14-16 names the player per variant:
  Bison/Vega, Akuma/Gouki, Charlie/Nash (`docs/names.md`).
- **Changes from the Japanese:**
  - Juggernaut: "Learn that I am stronger" for "know that one stronger
    exists".
  - Magneto: his title "Master of Magnetism" is dropped.
  - Sabretooth: "slaughterer" became "killer".
  - Cammy: her reply is shortened.
  - Version B runs "true form" across the line break.

  All of these were stated to the user before approval.

[`check_draft.py`](check_draft.py) checks every slot and record:

- the draft's source hash prefix matches the record's 76 bytes;
- each English version compiles to a 2 × 25 record.

```bash
./invenv.sh python research/experiments/EXP-0060/check_draft.py
./invenv.sh python research/experiments/EXP-0060/check_draft.py data/translations/boss_boxes.json
```

Result: 54 records, 0 problems, for both files. The first check found one
26-letter line (Cammy's reply), which was shortened before the user saw
the draft.

The user saw every line in a table, with the changes listed, and was
asked: "Approve these 36 lines as the new English for Apocalypse's
boxes?" Answer: "Approve all (Recommended)".

## Result

- `data/translations/boss_boxes.json`: the approved lines (the draft,
  with its description marked approved).
- `GATE-TRANSLATION` extended (`TASKS.md`) and the policy recorded
  (`docs/localization_policy.md`).
- **Unlocks:** none to decide. Gouki is open with a fresh save, and Alpha
  Chun-Li is chosen by holding Start (`EXP-0058`); neither is locked.

## Uncertainty

- **The 2 × 25 box layout** needs a box-code change that has not been
  tried (`SPEC-004`). If it cannot be made, the choice goes back to the
  user, as the answer's option said.
