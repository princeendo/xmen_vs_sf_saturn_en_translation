# EXP-0032 (M5): The Roster Image, Built and Verified

Task: RE-010
Status: DONE
Confidence: CONFIRMED

## Observation

The M4 mechanism (version-3 slot table, specs, `k mod 8` pairing) built Ryu
and Ken from the source image (`EXP-0028`). For the M5 roster (all 18
characters of slots 0-17, `RE-008`), the following were established:

- every file maps to its slot (`EXP-0029`);
- every slot pairs `k mod 8` (`EXP-0030`);
- every file fits its sectors with its English (`EXP-0031`);
- the user passed `GATE-TRANSLATION` for all 18 (`SESSION-0046`).

## Hypothesis

`tools.disc.build_english`, given the 18 specs, builds an image in one command
in which every roster character shows its official English win quotes, whether
it speaks as the first member, the second member or a CPU opponent. Ryu and
Ken stay as in `EXP-0028`, and the continue hint stays Japanese.

## Controlled Change

The build changes only `MMPACK.PCA` (version 3, slots 0-17) and the 18 roster
MC files (English records 0-7 over the start of each table). No tool code
changed. Sixteen specs were added by
[`make_spec.py`](make_spec.py), a copy of `EXP-0028`'s with one fix: it counts
English records the way the census does. The old count used slot + 1's
pointer, which gave Cammy (slot 17) a wrong count, because slot 18 aliases
slot 11.

## Prediction

- **Build:** only Track 01 differs. Exactly the 19 files change, all sectors
  pass EDC/ECC, the layout is unchanged, two builds are identical, and the
  decoded code differs only at `patches_v3(0-17)` sites. Each MC file equals
  `EXP-0031`'s predicted rebuild.
- **Records:** all 144 English records (18 × 8) draw cell for cell as compiled
  in the English grid (50/50 at 12 px).
- **Ryu and Ken:** their 17 forced runs each are byte-identical to `EXP-0028`.
- **Loads:** each picked character's file loads from the built disc, equal to
  the built file plus fix-ups.
- **Play:** English for a first-member win, a second-member win and a CPU
  win; the continue hint stays Japanese.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m`, Track 01 `c904a386…`, unchanged |
| Specs | `data/translations/<name>_win_quotes.json`, 18 (16 new) |
| English | US program `local/ref003/xmvsfu-68k.bin` (`EXP-0008`) |
| Record check state | Ryu `pre_ko`, `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0013`), paused seed 8520 |
| Pick states | `local/checkpoints/re004/f00002973.mcs` (cursor on Ken, first pick); `local/re004/session/states/f00009348.mcs` (Gouki cell visible) |
| Regression reference | `local/re007/draws_ryu`, `local/re007/draws_ken` (`EXP-0028`) |
| Play session | `local/re010/session/` (1,074 screenshots; the newest 200 states, frames 30062-63975) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`make_spec.py`](make_spec.py) | Specs (copy of `EXP-0028`'s, record count fixed) |
| `tools/disc/build_english.py` | The build, `--image` |
| [`image_checks.py`](image_checks.py) | Components, sectors, layout, changed files, builds, code bytes |
| [`force_records.py`](force_records.py) | Draws any roster character's 8 records through Ryu's quote with the roster code |
| [`force_draws.py`](force_draws.py) | `EXP-0028`'s draw script with the roster's slot table |
| [`pick_roster.py`](pick_roster.py) | Moves the select cursor (scratch home `local/mednafen_pick`, directions on I/M/J/L, A on K) and compares the loaded file |
| [`play_pointers.py`](play_pointers.py) | `EXP-0028`'s pointer reader over every roster table |
| `research/experiments/EXP-0023/cell_check_en.py` | Cell check |
| `tools/mednafen/session_recorder.py` | Play-session recording |

Running several Mednafen instances on one home needs `MEDNAFEN_ALLOWMULTI=1`
(see Actual Result). These runs never write settings.

## Procedure

```bash
# specs (Ryu and Ken reproduce, apart from the description)
./invenv.sh python research/experiments/EXP-0032/make_spec.py \
  data/translations/<name>_win_quotes.json <Name> <slot> "<MCxx>.SHP;1" <offset> \
  data/translations/<name>_pairing.json "user decision 2026-10-29, SESSION-0046"
SPECS=$(cat local/re010/specs.txt)   # the 18 specs in slot order
./invenv.sh python -m tools.disc.build_english $SPECS local/re010/b1 --image build/re010_roster_english
./invenv.sh python -m tools.disc.build_english $SPECS local/re010/b2
./invenv.sh python research/experiments/EXP-0032/image_checks.py build/re010_roster_english \
  local/re010/b1 local/re010/b2 local/re010/image_checks.json
# all 144 records, six instances
for g in "0 1 2" "3 4 5" "6 7 8" "9 10 11" "12 13 14" "15 16 17"; do
  MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0032/force_records.py \
    local/re010/b1 local/re010/rec_${g// /_} $g &
done; wait
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/re010/rec_<group> local/ref007/saturn_files/FIX.PRS
# Ryu and Ken regression
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0032/force_draws.py ryu local/re010/b1 local/re010/draws_ryu
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0032/force_draws.py ken local/re010/b1 local/re010/draws_ken
# picks from the built disc
CUE="build/re010_roster_english/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0032/pick_roster.py "$CUE" local/re010/b1 local/re010/pick_grid \
  local/checkpoints/re004/f00002973.mcs lll:0 ll:1 uull:2 ull:3 ulll:4 uulll:5 uuull:6 uuulll:7 \
  l:9 -:10 uul:11 uuul:12 uu:13 uuu:14 u:16 ul:17
./invenv.sh python research/experiments/EXP-0032/pick_roster.py "$CUE" local/re010/b1 local/re010/pick_retry \
  local/checkpoints/re004/f00002973.mcs uull:2 uuull:6
# play check (the user plays the cold-booted image; interactive home)
./invenv.sh python -m tools.mednafen.session_recorder local/re010/session \
  --agent-dir local/re010/session/agent --state-interval 3 --keep-states 200
S=local/re010/session/states
./invenv.sh python research/experiments/EXP-0032/play_pointers.py "$CUE" local/re010/b1 local/re010/play_pointers \
  $S/f00037361.mcs $S/f00043855.mcs $S/f00050841.mcs $S/f00057489.mcs $S/f00063634.mcs $S/f00063803.mcs
```

Quote screens in the session were found by the speech bubble's colour
(average of a 60 × 6 strip at x = 140, y = 222 near (224, 160, 32), from a
known quote screen). Each was then read by the agent.

## Actual Result

### Specs and build

- **Specs:** 16 new specs were written. Ryu's and Ken's reproduce apart from
  the description (Ken's byte for byte). Cammy's spec lists her English
  record 8 as unused only after the count fix.
- **Image** `build/re010_roster_english`: Track 01 `36672c5d…`, `MMPACK.PCA`
  `4e81b64f…`. The checks all passed:

| Check | Result |
| --- | --- |
| Components | only Track 01 differs; every source component still matches the manifest |
| Sectors | 0 invalid |
| Layout | same paths, LSNs and sizes as the source listing |
| Changed files | exactly `MC00`-`MC11` and `MMPACK.PCA` |
| Builds | `b1` = `b2` for all 19 files; the image holds `b1`'s |
| Code | 58 bytes differ (`EXP-0028`'s 42, plus 16 slot bytes), all at `patches_v3(0-17)` sites |
| MC files | each equals `EXP-0031`'s predicted rebuild |

### Every record, live

- **First attempt:** five of six parallel groups stopped at start. Mednafen
  refuses a second instance on the same home unless `MEDNAFEN_ALLOWMULTI=1`
  is set, and the first group, which got the lock, ran normally. The five
  were rerun with the variable set (failed outputs kept as
  `local/re010/failed_lock_*`).
- **Result:**
  - 144/144 records showed the predicted pointer and bytes, and drew 50/50
    cells at 12 px.
  - The six controls drew 38/38 at 16 px, and their screenshots are
    identical (`e006ebd8…`).
  - The agent read one quote box per character, and all were legible
    English.

### Ryu and Ken

All 17 runs of each match `EXP-0028`'s screenshots and VDP1 VRAM byte for
byte.

### Loads from the built disc

| Slot | Character | Moves from Ken | Fix-ups (2-byte aligned) | RAM = built + fix-ups | English table loaded |
| --- | --- | --- | --- | --- | --- |
| 0 | Wolverine | `lll` | 328 (118) | yes | yes |
| 1 | Cyclops | `ll` | 398 (128) | yes | yes |
| 2 | Storm | `uull` | 351 (131) | yes | yes |
| 3 | Rogue | `ull` | 430 (161) | yes | yes |
| 4 | Gambit | `ulll` | 283 (99) | yes | yes |
| 5 | Sabretooth | `uulll` | 341 (137) | yes | yes |
| 6 | Juggernaut | `uuull` | 302 (104) | yes | yes |
| 7 | Magneto | `uuulll` | 354 (109) | yes | yes |
| 9 | Ryu | `l` | 259 (106) | yes | yes |
| 10 | Ken | `-` | 302 (123) | yes | yes |
| 11 | Chun-Li | `uul` | 436 (218) | yes | yes |
| 12 | Dhalsim | `uuul` | 333 (110) | yes | yes |
| 13 | Zangief | `uu` | 289 (95) | yes | yes |
| 14 | Vega | `uuu` | 370 (128) | yes | yes |
| 16 | Nash | `u` | 263 (109) | yes | yes |
| 17 | Cammy | `ul` | 316 (120) | yes | yes |

Storm and Juggernaut failed on the first pass, because keys were dropped:

- **Storm:** the cursor reached her, but the A press did not register, so
  nothing was picked.
- **Juggernaut:** the two left moves were lost, so Vega was picked.

The screenshots show both. The retry passed.

- **Gouki:** five "up" moves from Cyclops in state 9348 stopped on
  Juggernaut, and nothing was picked. Gouki's cell sits above the grid, and
  the move that reaches it is not known. His load is covered in play
  (below).
- **Apocalypse:** cannot be picked. His load is covered in play (below).

### Play check (user, cold boot of the built image)

| Screen | Win | Speaker | Shown | Record |
| --- | --- | --- | --- | --- |
| `f00019120` | player (Gouki and Cyclops) | Gouki, first member | English | Gouki English 1 (text match; no state) |
| `f00024675` | player (Gouki and Cyclops) | Cyclops, **second member** | English | Cyclops English 0 (text match; no state) |
| `f00029067` | **CPU** (Storm and Nash) | Storm | English | Storm English 4 (text match; no state) |
| `f00029244`-… | continue | hint | **Japanese**, normal | — |
| `f00037343` | player (Nash and Ken) | Nash, first member | English | pointer `0x0024FBF4` = `MC10` English 5 (state 37361) |
| `f00043873` | player | Ken, **second member** | English | pointer `0x060B2BDC` = `MC0A` English 4, the WRAM-H copy (state 43855) |
| `f00050849` | player | Nash | English | `0x0024FB90` = `MC10` English 4 (state 50841) |
| `f00057539` | player | Ken, second member | English | `0x060B2C40` = `MC0A` English 5 (state 57489) |
| `f00063731` | **CPU** (Apocalypse) | Apocalypse | English | `0x060C1AA0` = opponent base `0x060C1000` + `0xAA0`, `MC08` English 0 (states 63634, 63803) |

- **Text match:** for the three quotes without a state, the text the
  agent read was searched in the roster's decoded English (locally). Each
  matched exactly one record.
- **Loads in play:** the English bytes on screen show that Gouki's `MC0F`
  (first member) and Apocalypse's `MC08` (opponent) were loaded from the
  built disc.
- **Not a quote:** at frames 58,191-58,366, before the Apocalypse fight, a
  two-line Japanese box at the top of the screen carries his pre-fight
  line. It is boss pre-fight text (`SPECIAL-001`), outside M5 and
  unchanged.
- **Recorder:** it ran the whole session (about 18 minutes) without a stall.

**Tests:** 162 pass.

## Conclusion

**CONFIRMED.** One command builds, from the untouched source, an image in
which all 18 roster characters show their official arcade English win
quotes, with Saturn record `k` showing English record `k mod 8`.

- All 144 records draw as compiled.
- Every grid character's file loads from the disc as built.
- In play, English appeared for a first-member win, two second-member wins
  (Cyclops; Ken from the WRAM-H copy) and two CPU wins (Storm; Apocalypse
  as the boss, from the opponent's copy).
- Ryu and Ken are byte-identical to `EXP-0028`, and the continue hint is
  unchanged.

## Uncertainty and Alternatives

- **No Japanese win quotes remain in ordinary play.** Every ordinary speaker
  is in the roster. Slot 18, if any speaker uses it, would read Chun-Li's
  file (`MC0B`), whose table now starts with English records. Its slot byte
  is 0, so it would draw them in the Japanese grid. Which character uses
  slot 18 is unknown (`docs/known_unknowns.md`).
- **Loads by trace:** Gouki's and Apocalypse's loads are shown by English
  on screen and, for Apocalypse, the pointer. They were not traced at
  the pick. The other 16 were checked from the disc by RAM comparison.
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect the `image_checks.py` summary above (exit 0),
144/144 records at 50/50, 34 byte-identical Ryu and Ken runs, the load
table, and the play-check pointers when the same states are loaded.
