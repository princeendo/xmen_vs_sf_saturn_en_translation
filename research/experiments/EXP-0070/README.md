# EXP-0070 (Names): COMBO GAUGE Beside NAMES

Task: LOC-010
Status: DONE (2026-11-01)
Confidence: CONFIRMED (cold boots with the flag clear and set, a fight with
the gauge on, the user's check of the everyday screen)

## Observation

The first toggle build (`EXP-0069`) took the hidden COMBO GAGE row for
NAMES. The user chose to keep both ("Keep both rows"), spelled "COMBO GAUGE"
(`docs/localization_policy.md`).

## The Options Menu, Traced (static, untouched `MMPACK.PCA`)

- **States:** the menu's state byte `0x0601E335` indexes a handler table
  at `0x06028128` (literal `0x06027F78`, dispatcher `0x06027F5C`): 0 setup
  (`0x060285A0`), 1 wait (`0x060285FC`), 2-10 the nine rows, 11 COMBO GAGE
  (`0x060289B6`). The button-config screen's dispatcher (`0x06027F7C`,
  state `0x0601E336`) indexes the same words from `0x06028158`, so the
  menu's slot 12 is its slot 0.
- **Cursor:** each row handler calls `0x060289E0` (or `0x06028A40`,
  `0x06028A84`), which steps the state with `0x06029CB4`/`0x06029C0C`
  between 2 and 10, or 11 when `0x0601E36C` is set (`mov #10/#11,r7` at
  `0x060289EA`, `0x06028A02`, `0x06028A56`, `0x06028A6E`, `0x06028A9A`,
  `0x06028AB2`). Start is handled by `0x06028AD0`, which every row handler
  calls; it is not a state.
- **Labels:** `0x06028538` prints each label of the chosen offset list two
  lines apart from line 5, highlighting the one whose state equals the
  cursor; then "PRESS START BUTTON TO EXIT" at line 25 (`mov #25,r2`,
  `0x0602856E`). R2 then already holds the next free line.
- **Values:** `0x06028B28` draws each row's value at fixed lines; COMBO
  GAGE's (line 23, only with the flag) is the block `0x06028BF8`-`0x06028C16`
  (literals `0x06028C60` flag, `0x06028C64` byte, `0x06028C68` list
  `0x0602A500`).

## Hypothesis

With a copied handler table (thirteen entries, the last a COMBO GAUGE
handler), new row lists (NAMES tenth, COMBO GAUGE eleventh with the flag),
the cursor's maximum raised by one, the exit line following the last row,
and row 10's value drawing replaced by a call that draws NAMES always and
COMBO GAUGE (line 25) with the flag, both rows work; with the flag clear
the screen is as in `EXP-0069`.

## The Build (`tools/disc/name_toggle.py` `menu_blob`, `menu_patches`)

The third segment holds the routine (208 bytes) and then the menu blob (540
bytes: the four lists, their strings copied from the game's, the NAMES value
list, the 13-entry table, the COMBO GAUGE handler, the drawing routine and
their literals), ending at `0x002FFBEC`.

## Actual Result

- **Build** (19:57-20:05, `build/loc010_toggle`): exit 0; Track 01
  `68813e93…`; only `MMPACK.PCA` differs from `continue_hints_us_v4`.
- **Flag clear** (`menu1`, cold boot, `EXP-0068/opt_walk.py`): ten rows, the
  tenth `NAMES  U.S.`, "PRESS START BUTTON TO EXIT" at its usual line:
  as `EXP-0069`.
- **Flag set** (`0x0601E36C` = 1 at the main menu): eleven rows, the
  eleventh `COMBO GAUGE  NORMAL` (line 25), the exit text two lines lower
  (line 27), no overlap. (`menu1` was then disturbed by the user's own key
  presses; `menu2` repeated it.)
- **Values** (`menu2`): the state 2 at entry; ten downs, 12 (COMBO GAUGE);
  right, `0x0601E359` = 1 (`FULL` on screen); up, 11 (NAMES); right,
  `0x0601E370` = 1 (`SATURN`); down and left, `0x0601E359` = 0
  (`NORMAL`). The highlight follows the cursor on both rows.
- **The gauge** (`gauge`, `EXP-0069/toggle_ram.py --gauge`, the route with
  `0x0601E359` = 1, 1,500 frames): both super gauges full (LEVEL 3) in the
  first fight; at LEVEL 0 without it (`EXP-0069` `ram2_v0`, same frame).
- **The user's check** (`play_check.py local/loc010/play1`, 88 s): "Looks
  right".
- **Reference:** `name_toggle_v4` updated to this build (Track 01
  `68813e93…`) and rebuilt with `--only`.

## Conclusion

NAMES and COMBO GAUGE both work in the toggle build. What sets the flag
that shows COMBO GAUGE was not traced (`docs/known_unknowns.md`).

## Reproduction

```bash
# build as README.md, "The one-image toggle", into build/loc010_toggle
CUE="build/loc010_toggle/X-Men vs. Street Fighter (Japan) (3M).cue"
T=local/loc005/title_ref.png; M=local/loc005/menu_ref.png
# a home: a copy of local/loc008/home_opt1 with a good save (local/loc008/bkr_after_opt4.bkr)
COLD_WALK_HOME=$PWD/local/loc010/home_m ./invenv.sh python research/experiments/EXP-0068/opt_walk.py \
  "$CUE" local/loc010/menu2 wait:1800 await:$T:6000 wait:150 press:s:$M:15 wait:30 \
  poke:0601E36C:01 keys:dd wait:60 keys:s wait:180 shot:flag peek:0601E335:1 \
  keys:dddddddddd wait:30 shot:on_gauge peek:0601E335:1 keys:r wait:30 shot:full \
  peek:0601E359:1 keys:u wait:30 peek:0601E335:1 keys:r wait:30 shot:saturn \
  peek:0601E370:1 keys:d wait:30 keys:l wait:30 shot:normal peek:0601E359:1
./invenv.sh python research/experiments/EXP-0069/toggle_ram.py "$CUE" \
  local/loc010/files_toggle/MMPACK.PCA build/regression/continue_hints_us_v4/files \
  build/regression/continue_hints_saturn_v4/files local/loc010/gauge 14 15 0 1500 --gauge
./invenv.sh python research/experiments/EXP-0070/play_check.py local/loc010/play1
```
