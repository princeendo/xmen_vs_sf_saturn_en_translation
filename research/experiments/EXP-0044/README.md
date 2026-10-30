# EXP-0044 (M8): Arcade Pairing for Every Roster Ending

Task: END-012
Status: DONE
Confidence: CONFIRMED (all predictions met)

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

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Arcade set | `xmvsfu`, `local/arcade_roms/xmvsf_mame0289` (`REF-001`); MAME 0.289 |
| NVRAM and configuration | `local/ref004` (`EXP-0009`) |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` |
| Saturn files | the MC files from the untouched source track |
| Roster | `data/text/m8_ending_roster.json` (`END-011`) |

## Tools

| Tool | Use |
| --- | --- |
| [`run_mame.py`](run_mame.py) | One timeline, headless (copied from `EXP-0037`) |
| [`make_timeline.py`](make_timeline.py) | Route for any roster slot, partner and language (Gouki by forcing) |
| [`predict.py`](predict.py) | `predictions.json`, committed in `8caed7c` before the logged runs |
| [`compare.py`](compare.py) | Each run's reads against the predictions |
| [`make_pairing.py`](make_pairing.py) | `data/translations/<name>_ending_pairing.json` |

## Procedure

```bash
T=research/experiments/EXP-0044/timelines
./invenv.sh python research/experiments/EXP-0044/predict.py research/experiments/EXP-0044/predictions.json
# 38 timelines: s<slot>_<partner>_<lang>.txt, for slots 0-7 and 9-17 (default partner, en and jp)
# and slots 0 and 11 (right, en and jp); slot 15 with --force-char 1e
./invenv.sh python research/experiments/EXP-0044/make_timeline.py $T/s0_default_en.txt 0 default en
./invenv.sh python research/experiments/EXP-0044/make_timeline.py $T/s15_default_en.txt 15 default en --force-char 1e
ls $T | grep '^s' | sed 's/\.txt$//' | xargs -P 6 -I{} \
  ./invenv.sh python research/experiments/EXP-0044/run_mame.py local/end012/runs/{} $T/{}.txt
./invenv.sh python research/experiments/EXP-0044/compare.py local/end012/runs local/end012/compare.json
./invenv.sh python research/experiments/EXP-0044/make_pairing.py local/end012/compare.json local/end012/pairing3
# copy all but nash_ending_pairing_exp0044.json into data/translations/
```

Each run takes about 40 s; six ran at once.

## Actual Result

**All 38 runs met every prediction:**

- the slot's table;
- every record address in order (the count is the arcade English or Saturn
  Japanese count);
- the table re-read pages equal to the `MCED` script's scene starts.

For slots 0 and 11, the second partner gave identical reads in both
languages.

| Slot | Partner | Lang | Table | Pages | Table re-read on pages | As predicted |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | default | en | `0x17e318` | 6 | 1, 4 | yes |
| 0 | default | jp | `0x17e2cc` | 7 | 1, 3 | yes |
| 0 | right | en | `0x17e318` | 6 | 1, 4 | yes |
| 0 | right | jp | `0x17e2cc` | 7 | 1, 3 | yes |
| 1 | default | en | `0x17e31c` | 9 | 1, 4, 7 | yes |
| 1 | default | jp | `0x17e2d0` | 7 | 1, 4, 6 | yes |
| 2 | default | en | `0x17e320` | 6 | 1, 4, 5 | yes |
| 2 | default | jp | `0x17e2d4` | 7 | 1, 3, 4 | yes |
| 3 | default | en | `0x17e324` | 6 | 1, 4 | yes |
| 3 | default | jp | `0x17e2d8` | 8 | 1, 4 | yes |
| 4 | default | en | `0x17e328` | 5 | 1, 3 | yes |
| 4 | default | jp | `0x17e2dc` | 6 | 1, 5 | yes |
| 5 | default | en | `0x17e32c` | 6 | 1, 4 | yes |
| 5 | default | jp | `0x17e2e0` | 4 | 1, 3 | yes |
| 6 | default | en | `0x17e330` | 6 | 1, 4 | yes |
| 6 | default | jp | `0x17e2e4` | 9 | 1, 5 | yes |
| 7 | default | en | `0x17e334` | 7 | 1, 3, 5 | yes |
| 7 | default | jp | `0x17e2e8` | 4 | 1, 2, 3 | yes |
| 9 | default | en | `0x17e33c` | 7 | 1, 3, 5 | yes |
| 9 | default | jp | `0x17e2f0` | 6 | 1, 4, 6 | yes |
| 10 | default | en | `0x17e340` | 4 | 1, 4 | yes |
| 10 | default | jp | `0x17e2f4` | 5 | 1, 3 | yes |
| 11 | default | en | `0x17e344` | 6 | 1, 4 | yes |
| 11 | default | jp | `0x17e2f8` | 7 | 1, 3 | yes |
| 11 | right | en | `0x17e344` | 6 | 1, 4 | yes |
| 11 | right | jp | `0x17e2f8` | 7 | 1, 3 | yes |
| 12 | default | en | `0x17e348` | 6 | 1, 3, 4 | yes |
| 12 | default | jp | `0x17e2fc` | 4 | 1, 2, 3 | yes |
| 13 | default | en | `0x17e34c` | 5 | 1, 4 | yes |
| 13 | default | jp | `0x17e300` | 4 | 1, 2 | yes |
| 14 | default | en | `0x17e350` | 5 | 1, 4 | yes |
| 14 | default | jp | `0x17e304` | 4 | 1, 2 | yes |
| 15 | default | en | `0x17e354` | 6 | 1, 6 | yes |
| 15 | default | jp | `0x17e308` | 4 | 1, 4 | yes |
| 16 | default | en | `0x17e358` | 6 | 1, 2, 4, 5 | yes |
| 16 | default | jp | `0x17e30c` | 6 | 1, 3, 5, 6 | yes |
| 17 | default | en | `0x17e35c` | 13 | 1, 2, 6, 7, 9, 10, 12 | yes |
| 17 | default | jp | `0x17e310` | 12 | 1, 3, 6, 7, 10, 11, 12 | yes |

**Consequences:**

- **Scene breaks:** every roster character's Saturn `MCED` script, in both
  languages, has the arcade's scene breaks (where the table is re-read).
- **Cammy:** her arcade Japanese ending reads exactly 12 records, the 12
  that `MC11` holds. That closes the "unbounded block" question
  (`docs/known_unknowns.md`).
- **Pairing files:** 16 new files, `data/translations/<name>_ending_pairing.json`
  (Nash's from `EXP-0037` is kept). Every English page and every Japanese
  record is CONFIRMED. Every Saturn Japanese ending record equals its arcade
  record byte for byte. `make_pairing.py` writes Nash's again as
  `nash_ending_pairing_exp0044.json`, and its English addresses equal
  `EXP-0037`'s.

**Names for the gate:**

| Where | Name | Kind |
| --- | --- | --- |
| Vega's (M. Bison's) English records 1 and 4 (pages 2, 5) | "Bison" | text |
| Nash's English records 1 and 4 | "Charlie" | text (already gated in M7) |
| Gouki's English page 5 | `Akuma` | label |
| Rogue's English page 1 | `Bison` | label |
| Magneto's English page 3 | `Vega` | label. The arcade English shows `Vega` there too (snapshot `s7_default_en` `f15880`): a Shadaloo member speaking after M. Bison's defeat. This is the US arcade's own label. |
| Nash's English pages 4 and 5 | `Charlie`, `Charlie's friend` | labels (M7) |

**Arcade English snapshots** for `END-015` are kept in
`local/end012/runs/*_en/snap/`, every 60 frames from frame 10,000.

## Conclusion

**CONFIRMED** for all 17 M8 roster characters, Gouki by a forced pick:

- page k of the ending reads the point character's ending record k, in
  English and in Japanese;
- the partner changes nothing (checked for two characters);
- the arcade's scene breaks equal the Saturn scripts'.

Each character's English pages pair with arcade English records 0 to
n − 1 (`data/translations/<name>_ending_pairing.json`).

## Uncertainty and Alternatives

- **Gouki** was reached by forcing seven RAM words, not by the arcade's
  unlock input.
- **Pictures and labels** were looked at for the flagged pages only. Every
  page's screens are compared in `END-015`, on the Saturn build, against
  these snapshots.
