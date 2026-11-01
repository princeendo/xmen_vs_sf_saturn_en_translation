# EXP-0068 (Names): What an In-Game Name Toggle Would Take

Task: LOC-008
Status: DONE (2026-11-01)
Confidence: CONFIRMED for the census, group A in RAM, the settings byte,
the hidden row and the loader's caller; UNKNOWN when settings are saved

## Observation

The two name variants are separate builds (`LOC-005` to `LOC-007`,
D-047, D-048). The user asked what an in-game choice between them would
take, before deciding whether to build one.

## Difference Census (`census.py`)

Input: the files of the regression references `continue_hints_us_v4` and
`continue_hints_saturn_v4` (`build/regression/<name>/files`, rebuilt and
hash-matched on 2026-11-01). Six files differ, each the same stored size in
both variants; 243 decoded bytes differ in all:

| Group | File | Loaded | Differing bytes (runs, joined within 16 bytes) | What |
| --- | --- | --- | --- | --- |
| A. Art and voice | `MMPACK.PCA` segment 2 | at boot; resident | 20 (10 runs of 2) | exactly the 10 sites of `tools/disc/names.py` (`00BD` / `E002`) |
| B. Quote and ending records | `MC0E`, `MC10`, `MC11` | with that character, into the fight buffer of its side | 161 (6 runs, 244 bytes long) | the approved name edits (`data/translations/saturn_names.json`) |
| C. Apocalypse's boxes | `MC08` | with the boss | 46 (3 runs, 71 bytes long) | the second box for slots 14-16 |
| D. Ending labels | `MCED.SHP` | at the ending, `0x060D2000` | 16 (5 runs, 31 bytes long) | the label bytes of slots 3, 7, 15 and 16, and label entry 9 (decoded `0x3EC8`) |

Load buffers (D-012, D-022, D-033): the first member's file at WRAM-L
`0x0024D000`, the second's at `0x060B0000`, opponents' at `0x060C1000` and
`0x060D2000`; `MCED` at `0x060D2000`. Fonts and art do not differ: every
name's art is on the disc in both conventions (D-045), so MSHvSF's "a
second font does not fit" does not arise here.

## Group A: the Name Sites' Literals (static)

Each of the 10 sites is `mov.w @(lit),r0` (`0xD478`) then
`mov.w @(r0,r11),r0` (R11 = `0x060F8000`, so the region word
`0x060F5478`). The sites use six literals: `0x0604FD14` (both name calls),
`0x06063A08`, `0x0606E048`, `0x06073B2E`, `0x0607FE68` (two life-bar
sites), `0x06080026` (three). A scan of both segments for every
`mov.w @(disp,pc)` found one other reader: `0x0604FD00`, the
region-dependent sound request (`0x0604FD02`, `0x9E` or `0x9F`;
`docs/coverage_exceptions.md`). So pointing the six literals at a setting
word switches every name surface, and the sound request would follow
unless its read becomes `mov #0,r0` (as both variants now play it).

## Free Space (`free_space.py`)

225 WRAM-H dumps on hand (every 1 MB file under `local/` whose
`0x06014000` holds `MMPACK.PCA`'s first segment) were combined. 50 runs of
64+ bytes are zero in all of them. The ones that matter:

- `0x0601EDC0`-`0x0601EFFF` (576 bytes): the rest of the gap after the
  hint table; loaded from disc by extending `MMPACK.PCA`'s first segment
  again, as `HINT-002` did.
- R11's reach (`0x060F0000`-`0x060FFFFF`) for a setting word: runs at
  `0x060F1FA1` (73), `0x060F3720` (64), `0x060F871F` (65), `0x060FA330`
  (71) and others; `0x060FEA38`-`0x060FFFFF` (about 4 KB in five runs)
  is likely the stack. Zero in snapshots does not prove unwritten.
- Zero runs inside `MMPACK.PCA`'s first segment (largest `0x0601792C`, 932
  bytes, near the sound mixer's records) are zero in the file too: likely
  buffers, not usable without a write log.

## Tools and Environment

`./invenv.sh` (Python 3.12), Mednafen with the agent interface
(`tools/mednafen`), the route's select state
`local/checkpoints/re004/f00002973.mcs` on the untouched image.

## Reproduction

```bash
./invenv.sh python research/experiments/EXP-0068/census.py \
  build/regression/continue_hints_us_v4/files build/regression/continue_hints_saturn_v4/files \
  local/loc008/census.json
./invenv.sh python research/experiments/EXP-0068/free_space.py \
  local/hint002/files_jp/MMPACK.PCA local/loc008/free_space.json
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
for v in 0 2; do ./invenv.sh python research/experiments/EXP-0068/toggle_names.py \
  "$CUE" local/loc008/names_v$v 14 15 $v; done
T=local/loc005/title_ref.png; M=local/loc005/menu_ref.png
# each opt run: a copy of local/mednafen_pick as COLD_WALK_HOME (firmware linked)
COLD_WALK_HOME=$PWD/local/loc008/home_opt2 ./invenv.sh python research/experiments/EXP-0068/opt_walk.py \
  "$CUE" local/loc008/opt2 wait:1800 await:$T:6000 wait:150 press:s:$M:15 wait:30 \
  keys:dd wait:60 shot:menu_opt save:menu_opt keys:s wait:180 shot:opt_s
S=local/loc008/opt2/menu_opt.mcs
COLD_WALK_HOME=$PWD/local/loc008/home_opt3 ./invenv.sh python research/experiments/EXP-0068/opt_walk.py \
  "$CUE" local/loc008/opt3 wait:60 load:$S wait:30 keys:s wait:120 dump:o0 keys:r wait:30 dump:o1 \
  keys:r wait:30 dump:o2 keys:ll wait:30 dump:o3 keys:s wait:240 dump:o4
COLD_WALK_HOME=$PWD/local/loc008/home_opt4 ./invenv.sh python research/experiments/EXP-0068/opt_walk.py \
  "$CUE" local/loc008/opt4 wait:60 load:$S wait:30 poke:0601E36C:01 keys:s wait:120 \
  keys:ddddddddd wait:30 shot:o_combo keys:s wait:240 dump:after
COLD_WALK_HOME=$PWD/local/loc008/home_opt8 ./invenv.sh python research/experiments/EXP-0068/opt_walk.py \
  "$CUE" local/loc008/opt8 wait:60 load:$S wait:30 watch:00180000-0018FFFF keys:s wait:120 \
  events:enter keys:r wait:30 keys:s wait:1200 events:exit
./invenv.sh python research/experiments/EXP-0068/trace_loader.py \
  "$CUE" local/checkpoints/re004/f00003302.mcs local/loc008/trace3 a 900 0600D056
```

## Group A in RAM (`toggle_names.py`)

The route (`tools.mednafen.route.run`, untouched image, select state
`re004/f00002973.mcs`, Vega first, Gouki second, 3,000 frames) with its
code ranges replaced by: the six literals `0xD478` → `0xB720` (R11 +
sign-extended `0xB720` = `0x060F3720`), the sound-request read
`0x0604FD02` `00BD` → `E000`, and the word `0x060F3720` set to VALUE.
All 8 originals checked before writing.

| Surface | VALUE 0 (`names_v0`) | VALUE 2 (`names_v2`) |
| --- | --- | --- |
| Select label | not shown: the second pick slipped to Cyclops (load check `second: false`) | AKUMA (`second_cursor.png`) |
| VS screen | VEGA / CYCLOPS | BISON / AKUMA |
| Life bar | VEGA (`r001680`) | BISON (`r001680`) |
| Win banner | VEGA / CYCLOPS WIN | BISON / AKUMA WIN (`r000300`) |
| Name call | not heard (silent run) | not heard |

Each run took about 1 min 50 s (16:06-16:10). **CONFIRMED** in RAM for
four surfaces: a single word, read through the six literals, switches
the art. The name calls read the same redirected literal (`0x0604FD14`),
so they are **SUPPORTED**, not observed.

## The Options Screen and the Settings (`opt_walk.py`)

`opt_walk.py` is `EXP-0051/cold_walk.py` with `dump`, `load` and `poke`
steps. Each run uses a copy of the route's pick home
(`local/loc008/home_optN`, its backup RAM copied from
`local/mednafen_pick`), so no user home is written.

- **Reaching it** (`opt1`, `opt2`, cold boots of the untouched image): the
  menu cursor moves with down; A does not open OPTION MODE, Start does
  (`opt2`, state `menu_opt.mcs` saved on OPTION MODE).
- **The screen:** OPTION MODE, nine rows: DIFFICULTY, TIME LIMIT, TURBO
  SPEED, SHORT CUT, AUDIO, SOUND TEST, BUTTON CONFIG., BACK UP, PANEL, all
  already in English. No language or name row.
- **The rows** (static, untouched `MMPACK.PCA`): plain ASCII, 17 bytes each,
  at `0x0602A288` (16 spaces) and `0x0602A299`-`0x0602A345` (the nine and
  a tenth, `COMBO GAGE`). Four lists of 16-bit offsets (relative to each
  list's start) pick the rows:

  | List | Rows | Row 8 | Row 10 |
  | --- | --- | --- | --- |
  | `0x0602A234` | 9 | BACK UP | — |
  | `0x0602A248` | 10 | BACK UP | COMBO GAGE |
  | `0x0602A25E` | 9 | blank | — |
  | `0x0602A272` | 10 | blank | COMBO GAGE |

  The code at `0x060284EE`-`0x06028536` picks the blank-row lists when a
  call (`0x06028A18`) returns 0 and the byte at `0x0601E335` is at least 2,
  and the COMBO GAGE lists when the byte **`0x0601E36C`** is non-zero.
- **The settings** (`opt3`: from `menu_opt.mcs`, Start, DIFFICULTY right,
  right, left, left, Start; WRAM-H dumped at each step): one byte stepped
  with the stars, **`0x0601E350`** (1, 2, 3, 1; two, three, four, two stars
  on screen), in `MMPACK.PCA`'s first segment, whose file bytes hold the
  defaults. (`0x060FFCF2` stepped too; it is in the probable stack.)
- **The save:** leaving Options rewrote the backup-RAM file; with the value
  put back, only bytes `0x9C`-`0x9D` changed (the file's date). The save
  holds 105 bytes equal to RAM `0x0601E351`-`0x0601E3B9` (from `0x1FF`),
  the settings block with the COMBO GAGE byte. Whether the game saves and
  restores that block as a whole is tested next (`opt4`, `opt5`).
- **The hidden row** (`opt4`: from `menu_opt.mcs`, `0x0601E36C` set to 1,
  then Start): Options showed ten rows, the tenth `COMBO GAGE  NORMAL`.
  **CONFIRMED.** What the row controls was not traced.
- **Persistence** (`opt4`-`opt8`):
  - leaving Options with the flag set, or with DIFFICULTY one higher, left
    the save's data unchanged, even 1,200 frames after the exit (`opt7`);
  - a cold boot with that save (`opt5`) had the flag at 0 and nine rows;
  - a log-mode write breakpoint on `0x00180000`-`0x0018FFFF` recorded no
    write while entering or leaving Options (`opt8`; no positive control);
  - the date change seen in `opt3` came with the state: Mednafen states
    carry the backup RAM, and `menu_opt.mcs` was saved just after a cold
    boot, so the game writes its save at boot.

  So leaving Options does not save the settings. When (or whether) a
  setting reaches the save is **UNKNOWN**.

## The Loader's Caller (`trace_loader.py`)

From `re004/f00003302.mcs` (Ken picked, cursor on Cammy), A, 900 frames,
log-mode PC breakpoints (a halting breakpoint did not hold while the key
was sent, `trace1`):

| Run | Breakpoint | Frame | PR | R5 (size) | Note |
| --- | --- | --- | --- | --- | --- |
| `trace2` | `0x0600D09C` | 283 | `0x0600D088` | `0x6F4E` (`MC11.SHP`) | R6 = `0x060B0000`, the second member's buffer |
| `trace2` | `0x0600D09C` | 298 | `0x0600D088` | `0x1167D` | R6 = `0x02411870` (cart RAM) |
| `trace3` | `0x0600D056` | 282, 298 | `0x0600CF40` | as above | R7 = `0x060F021C` |

`0x0600CF00` (main program, not `MMPACK.PCA`) reads a file's directory
record (`bsr 0x0600CF78`, fields from + 11), then calls `0x0600D056` to
read it; it returns through `0x0600CF48` on success. Every file load seen
here passes through it, so a hook there would see each load; the files'
relocation is applied elsewhere, after the load, and touches none of the
changed records (D-012).

## Options Put to the User

| | What switches | Measured cost | Unknowns and risks |
| --- | --- | --- | --- |
| **1. No toggle** (as now) | Nothing; two images, one per name convention | None | None |
| **2. Art and voice only** | Group A: select label, VS screen, life bar, win banner, name calls | 7 two-byte changes (six literals, one pin) and one setting word in R11's reach | The text (quotes, endings, Apocalypse's boxes, labels) keeps one convention, so screen and text can disagree; the setting word needs a session-long write log |
| **3. Everything** | Groups A-D | Group A as in 2; for B-D, about 400 bytes of Saturn-name data (14 runs) and about 100 bytes of code that patch each file after it loads, in the 576 bytes left after the hint table, with a hook in the main program's load routine (`0x0600CF00`); a copy of the setting into the word group A reads | The hook changes the main program; the 576 bytes leave little room; every surface needs checking in both settings |
| **Setting, for 2 or 3** | An Options row | The game already has a ten-row menu (`COMBO GAGE`, shown when `0x0601E36C` is non-zero); its row text is plain ASCII in RAM | Repurposing COMBO GAGE hides whatever it controls (not traced); the row's handler and value storage are not found yet; leaving Options does not save settings, so the choice may reset at each power-on unless the save path is found |

## Conclusion

Measured: a toggle is technically possible. Art and voice switch with
one word (shown in RAM). The text needs a load hook and a little room, and
the room exists. The setting has a ready slot in the menu, but saving it
across power-offs is not yet understood.

**The user's decision** (verbatim): "Build the full toggle". Recorded in
`docs/localization_policy.md`; the build is `LOC-009`.
