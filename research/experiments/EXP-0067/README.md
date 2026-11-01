# EXP-0067 (UI): The Continue Hints in English, Matched to Each Saturn Hint

Task: HINT-002
Status: DONE (2026-11-01)
Confidence: CONFIRMED on the built code for all 16 indices (forced), for
the table's load from a cold boot, and in the user's play check

## Observation

`EXP-0066` (D-058): the Saturn's hint starter is the arcade's, with its
English map, but the Saturn has no English hint records, and its English
base points at unrelated data. The arcade's own map is out of step with the
Japanese hints from index 8.

## The User's Plan

Samples of both options were drawn by the Saturn's own English path
(`EXP-0066/fit_run.py`; `local/hint002/samples.png` `b3f3d1a8…`): option A,
the arcade's map, at indices 8 and 11; option B, each hint's own English, at
indices 7, 8 and 11. The user chose B, with the arcade's wording as written
(verbatim in `docs/localization_policy.md`).

## Hypothesis

A same-size change to the hint starter, which sets the task's English byte
(the byte the English builds' renderer already reads) and a new base, with a
matched index map and the 24 records in the 2,976-byte gap after
`MMPACK.PCA`'s first segment, shows each hint's own English on two pages and
leaves every other text task as it was.

## Design (`tools/disc/continue_hints.py`)

- **Table:** area records 270-283, 284 twice (the super-jump hint has one
  page), 285-292: 24 × 100 bytes at `0x0601E460`.
- **Map** (`0x060667A8`): `00 02 04 06 08 0A 0C 0E 10 12 14 16 08 04 12 06`;
  indices 12-15 repeat the Saturn's own hints 4, 2, 9 and 3.
- **Starter** (`0x06066746`-`0x0606678B`, 70 bytes): always maps; task +38 =
  page, +39 = 2, +`0x5C` = 2 (English), +78 = `0x180`, +52 = `0x0601E460`
  (literal `0x06066798`); leaves r14 = −1, T = 1 and `@(6,gbr)` = 0 as the
  original Japanese path did.
- **Page step** (`0x06066504`): the hint task's state-0 handler showed page
  2 only when the global language word was set (the first RAM run showed
  page 1 only). `9017 00BD` → `E05C 00CC`: it reads the task's English byte.
  The handler serves type-2 (hint) tasks only: the dispatch at `0x06066486`
  selects by task byte +39, then a state table.
- **Storage:** the gap `0x0601E460`-`0x0601EFFF` is zero in every gameplay
  dump on hand (attract, select, fights, continue, boss, ending); only an
  early boot dump, before `MMPACK.PCA` loads, holds data there. No disc file
  but `MMPACK.PCA` has a load segment near it. `MMPACK.PCA`'s second segment
  is replaced during the attract (another module at `0x0601F000`); the first
  segment is not.
- **Build:** `build_english --continue-hints` (version 4) extends the first
  segment's size word (header offset 8: `0x2918` → `0x2B70` longs) and
  inserts the table; the file still compresses into its original size
  (1,263 bytes to spare with the table, before the other patches).

## Actual Result

- **RAM, first run** (`ram_natural`, untouched image, `pre_ko` state, the
  renderer patches of the English builds plus the starter, map, base and
  table): the natural index 10 read table record 20 (`0x0601EC30`, area
  record 289, the throw input) and drew it in English; no second page.
- **RAM, with the page step** (`ram_natural2`): pages at `0x0601EC30`
  (frame 2,350) and `0x0601EC94` (2,730): the throw input, then "You'll
  escape from the throw move!" (`pages.png` `02f38062…`; screenshots
  `r02370.png` `be015ba5…`, `r02760.png` `29e1fe39…`). The CPU's win quote
  before it read the same record as without the change (`0x060C4890`).
- **Builds** (`build_english` with the README's release flags plus
  `--continue-hints`; files in `local/hint002/files_{us,saturn}`, images in
  `build/hint002_{us,saturn}`): both exit 0. Track 01 `84b1dd22…` (US) and
  `94dcd067…` (Saturn names); `MMPACK.PCA` `ba1cf968…` and `89ba6af9…`,
  258,319 bytes each. Checked offline: first segment `0x06014000`, size
  `0xADC0`; the decoded table at `0x0601E460` equals
  `continue_hints.table()` (SHA-256 `9a13cb00…`); every hint patch is in
  place; every other built file equals the `attract_captions_*_v4`
  reference.

- **Cold boot** (`cold_gap.py`, no input, WRAM-H at frames 900, 3,000,
  6,000, 9,000 and 12,000; both built images and, as the control, the
  untouched image with its own `MMPACK.PCA`):
  - the gap is zero at 900 and holds exactly `continue_hints.table()` from
    3,000 to 12,000 on both built images; it stays zero on the untouched
    image;
  - gap writes: the untouched image's come only from BIOS code (`0x2B0`,
    `0x2364`, `0x1FE4`, `0x1FFE`, `0x258A`: 4,624 writes, frames 8-2,033);
    the built images have those plus 600 from `0x0600D124` (600 longs, the
    table's 2,400 bytes), and none after frame 2,033;
  - the built images' decoded first segment, up to the table, equals the
    untouched file's. RAM there differs from the decoded file on every
    image, the control included (runtime data); the built and untouched
    dumps differ there by 1 byte at frames 6,000 and 12,000 and by 222 and
    3,368 at 3,000 and 9,000 (attract state, not code).
  - Dumps at 12,000: `97b739cf…` (US), `f1067c3e…` (Saturn names),
    `525b96a6…` (untouched).
- **Forced on the built code** (`force_built.py`, the `pre_ko` state; the
  built `MMPACK.PCA`'s decoded differences, 452 runs US and 442 Saturn
  names, the table included, then the mask as `mov #INDEX,r0`): for all 16
  indices on both variants the renderer's pointer reached exactly table
  records `2·map[i]` and `2·map[i]+1` (`summary.json`, all `ok`). The
  page-1/page-2 sheet (`force_us/sheet.png` `beda4a17…`) is identical for
  both variants (the hints name no character): every page English, the
  arrows drawn, index 7 the super-jump hint on both pages, indices 12-15
  the same as 4, 2, 9 and 3. Index 10's screenshots equal the RAM run's
  (`be015ba5…`, `29e1fe39…`).

- **The user's play check** (`play_check.py local/hint002/play1`: the
  US-names image for 247 s, then the Saturn-names image for 132 s, each
  from a cold boot): three continue screens, three different hints
  (indices 1, 2 or 13, and 6), each English on both pages
  (`play1/sheet.png` `83e99347…`). The user (verbatim): "Both look right".
- **Register:** references `continue_hints_us_v4` and
  `continue_hints_saturn_v4`; README; `docs/coverage_exceptions.md`
  (continue hints); `docs/text_surfaces.md`; D-059.

## Conclusion

`HINT-002` is done. The hint task alone takes the English path; the
table's room is empty in every gameplay dump and is written only by its
load. Records 16-20 are unchanged (`docs/known_unknowns.md`).

## Reproduction

```bash
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
STATE=local/checkpoints/dbg003/f00009769.mcs
./invenv.sh python research/experiments/EXP-0067/ram_hints.py "$CUE" "$STATE" local/hint002/ram_natural2
# after building with --continue-hints (README build command):
US="build/hint002_us/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0067/cold_gap.py "$US" local/hint002/files_us/MMPACK.PCA local/hint002/cold_us 900 3000 6000 9000 12000
./invenv.sh python research/experiments/EXP-0067/cold_gap.py "$CUE" local/hint002/files_jp/MMPACK.PCA local/hint002/cold_jp 900 3000 6000 9000 12000
./invenv.sh python research/experiments/EXP-0067/force_built.py "$US" "$STATE" local/hint002/files_us/MMPACK.PCA local/hint002/force_us
./invenv.sh python research/experiments/EXP-0067/play_check.py local/hint002/play1
```

`local/hint002/files_jp/MMPACK.PCA` is the untouched file, read from the
source Track 01 (`tools.mednafen.route.track_file`).
