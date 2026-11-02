# EXP-0069 (Names): The In-Game Name Toggle

Task: LOC-009
Status: DONE (2026-11-01)
Confidence: CONFIRMED (RAM routes in both settings, cold boots of the built
image, the user's play of both settings)

## Observation

`EXP-0068` (D-060): the variants differ in 243 bytes; one word switches the
art and voice; the hidden tenth Options row exists; leaving Options does
not save the settings. The user chose the full toggle.

## Settings and the Save (`EXP-0068/opt_walk.py`)

- **BACK UP: SAVE** (`s1`: from `menu_opt.mcs`, Start, DIFFICULTY right,
  seven downs to BACK UP, right to SAVE, A): the save file changed at
  `0x1FA` (1 → 2, DIFFICULTY), `0x205` (0 → 1, BACK UP), its date and two
  bytes at `0x4E6`-`0x4E9`. The game saves its settings when the player
  chooses SAVE. A log-mode write breakpoint on `0x00180000`-`0x0018FFFF`
  logged nothing during that save, so `EXP-0068`'s empty log on leaving
  Options was no evidence (the watch does not see these writes).
- **The saved block:** the save's data (900 bytes from its blocks, the
  file's 34-byte header and block list removed) holds RAM
  `0x0601E350`-`0x0601E417` from data offset 294, byte for byte.

## The Hidden Row's Byte

- `COMBO GAGE` stores `0x0601E359` (values NORMAL, FULL;
  `0x0602A500`), which play reads: `0x06061CDA` and `0x06061D04` each
  frame (one per side) and `0x0604126A` (a fighter's gauge set to `0x90`
  when non-zero) (`combo_reads`, route Vega/Gouki, 3,000 frames, read log).
  So the row can be repurposed but its byte cannot.
- The row's code is per row: the flag `0x0601E36C` (literals `0x06028564`,
  `0x06028C60`) picks the 10-row lists and the cursor's limit (11 entries
  rather than 10, `0x06028A6E`); the value stepper (`0x060289B6`, max 1)
  and the drawing (`0x06028BF8`) take the byte from literal `0x06028C64`
  and the strings from `0x06028C68`.

## The Hook

The main V-blank-in handler is `0x060148CC` (`MMPACK.PCA` first segment) in
177 of the 225 dumps, endings included; the attract uses `0x06020E98`. It
saves every register, then sets a flag and increments a frame counter
(`0x060148F2`-`0x060148FE`). The counter's literal (`0x06014958`) has no
other reader, so the increment can become a call to a routine that does it
first.

## Free Room and the Setting, Over a Session (`session_writes.py`)

`writes1` (route Vega first, Gouki second, policy `first`, 30,000 frames,
16:46-17:00, to the boss and partner fights; log-mode write breakpoints on
the names byte, the setting word and four zero runs of the first segment):

| PC | Writes | Frames | Target |
| --- | --- | --- | --- |
| `0x0601D5CE`, `0x0601D614` | 5,015 and 21,074 | 1,380-20,400 | a 64-long table at `0x0601D914` (covers `0x0601D974`) |
| `0x0601D798` | 1 | 20,400 | `0x0601D814` + 4n (the `0x0601D89F` run) |
| `0x06021B26`, `0x06021B6A` | 3 and 37 | 20,500-29,400 | not known: the code at those addresses in the ending dumps writes elsewhere |

So `0x0601D89F` and `0x0601D974` are in use. `writes2` repeats the route
watching only the names byte, the setting word, `0x0601E138` and
`0x0601E270`, and keeps each hit's registers.

`writes2` (the same route, 17:00-17:14, watching only the names byte, the
setting word, `0x0601E138`-`0x0601E237` and `0x0601E270`-`0x0601E2B7`, with
each hit's registers kept): 16 writes, all to the **setting word**
`0x060F3720`-`0x060F3721` (R9), from a copy loop during the ending (frames
20,500-29,820; the code there then is not `MMPACK.PCA`'s). Nothing wrote the
names byte or the two runs. So:

- **Rejected:** a setting word at `0x060F3720` written by the routine every
  frame; it would overwrite the ending's data. The art and voice are
  switched instead by writing the 10 sites' own instruction each frame
  (`E002` or `00BD`), only while the words around each site are the
  site's own (other modules replace that code at times).
- `0x0601E370` (the names byte) and `0x0601E138` (256 bytes) are used.

## The Build (`tools/disc/name_toggle.py`, `build_english --names toggle`)

- The fighter files and `MCED.SHP` are the American variant's (equal to
  `continue_hints_us_v4`'s); `MMPACK.PCA` has the name sites unpatched (as
  `none`/`saturn`) plus:
  - the hook: literal `0x06014958` → `0x0601E138`, and `0x060148FA`
    `6102 7101 2012` → `400B 0009 0009` (`jsr @r0`);
  - the routine at `0x0601E138` (208 bytes, `tools/sh2/asm.py`);
  - its tables after the hints (512 bytes: the 10 sites, then the five
    files' entries, 4-byte signatures);
  - the row: flag literals `0x06028564`, `0x06028C60` → `0x0602A345` (the
    label, never zero), value literal `0x06028C64` → `0x0601E370`, label
    `NAMES`, values `U.S.` and `SATURN`.
- `build_mmpack` now maps first-segment patch addresses from the first
  segment's own address (it mapped every address as the second
  segment's; no earlier patch was in the first segment).
- Build (17:17-17:25, `build/loc009_toggle`): the decoded `MMPACK.PCA`
  differs from the Saturn variant's only at those places.

## The Routine in RAM (`toggle_ram.py`)

Route on `build/loc009_toggle` (Vega first, Gouki second, 30,000 frames),
the built `MMPACK.PCA`'s decoded differences (523 ranges) written into RAM at
the select state, and the setting byte set; at each screenshot the 10 sites
and each changed file's runs in the four buffers were read:

| | `ram_v1` (setting 1, Saturn; 17:30-17:44) | `ram_v0` (setting 0, American; 17:46-18:04) |
| --- | --- | --- |
| Picks | Vega, then Juggernaut (the second pick slipped) | Gouki and Cyclops (both slipped) |
| Sites | all `00BD` from frame 497; `??????????` at 30,095 (another module there, left alone) | all `E002` from 371; `??????????` at 29,779 |
| Files | Saturn bytes: `MC0E` at `0x0024D000` (frame 1,152), `MC11` and `MC10` at `0x060C1000`, `MC08` at `0x060C1000` and `MCED` at `0x060D2000` (12,455 to 24,455) | American bytes: `MC11`, `MC10`, `MC0E` (CPU Vega), `MC08`, `MCED` |
| On screen | VS `VEGA`; Apocalypse's second box "Vega, lower than trash, …"; Vega's ending "But Vega's Psycho Power …", "Vega turns his attention …" | VS `AKUMA` / `CYCLOPS`; the second box "Akuma, however strong, …" |

The route's load check reports both buffers false in both runs: the picks
slipped (the route's key timing), and in `ram_v1` the buffers hold the
Saturn bytes by then. Neither is the toggle's doing.

## The Interrupt Table: a Hang and Wrecked Saves

- **Menu test, first image** (`menu1`, `menu2`, cold boots of the toggle
  image): the title never came. A plain boot (`boot1`) showed the backup
  warning (`ERR1.BIN`'s English), and the untouched image then showed it
  too with that home (`boot_jp`): the save had been overwritten, all
  32 KB, with a repeated `0000FE9D`, its format header gone. Every home
  was a throwaway copy; no user save was touched.
- **Not the routine's stores** (`boot_stores.py`, `diag1`, `diag2`): the
  routine first runs at frame 2,084 and stores only the 10 sites (`E002`);
  `MMPACK.PCA` loads intact (the routine, hints and tables equal the file
  from frame 2,100). It runs every frame to 2,577, when the title module
  takes over; the screen then stays black, and the save is wrecked.
- **Bisected by pokes on the untouched image** (frame 2,100, title checked
  at 4,200): the 512 table bytes at `0x0601EDC0` leave the title showing;
  the 208 routine bytes at `0x0601E138` give a black screen.
- **Why** (`watch1`: read and write log on `0x0601E138`-`0x0601E2B7` from
  power-on to frame 7,200): at the hand-over (frame 2,578) `0x0601DF98`
  walks 64 longs from `0x0601E138` and then 32 from `0x0601E238`, and passes
  each non-zero one to the BIOS (`0x06000310`, `0x06000300`) as an
  interrupt handler. Zero there means "no handler". **Rejected:**
  `0x0601E138` as free room; zero in every dump and unwritten in play, it
  is the game's interrupt-handler table, read only at mode changes.
- **Rejected** too: `0x0602712C` (169 zero bytes in the second segment); two
  literals point into it (`0x06027124`, `0x060271D0`).
- **The routine moves** to a third `MMPACK.PCA` segment at `0x002FF900`,
  the end of WRAM-L: `VS00.PRS` (34,961 bytes, loaded at `0x002F7030`) ends
  at `0x002FF8C1`, and `0x002FF8C1`-`0x002FFFFF` is zero in all 177 WRAM-L
  dumps on hand. To be shown: that the loader honours a third header entry,
  and that nothing reads, writes or clears that tail in any mode.

## The Third Segment, Cold Boot and Menu

- **Build** (18:35-18:43, `build/loc009_toggle`): `MMPACK.PCA` has three
  header entries; the third is `0x002FF900`, 52 longs (the routine).
- **Cold boot** (`diag3`, `boot_stores.py --watch 002FF8C1-002FFFFF`, a good
  save, 7,200 frames): the loader writes the third segment (52 writes from
  `0x0600D124`, the same loader store that writes the first two); nothing
  else reads or writes the tail but the BIOS's power-on clear; the routine
  runs from frame 2,084; the title shows at 4,200 and the attract at 6,000;
  the save's only change is its date byte (`0x9D`). The loader honours a
  third entry: **CONFIRMED**.
- **The row** (`menu1`, `menu2`, `opt_walk.py`, two cold boots in one home):
  Options shows ten rows, the tenth `NAMES  U.S.` (`0x0601E370` = 0); right
  gives `NAMES  SATURN` (1); BACK UP: SAVE, A, exit (still 1). The second
  cold boot opens Options on `NAMES  SATURN`, the byte 1 from the save.
  (Two earlier attempts stopped when the Mednafen window lost focus.)

## The Routine in RAM, on the Third-Segment Image (`toggle_ram.py`)

Route (Vega first, Gouki second, 30,000 frames, through the boss, the
partner fight and the ending), 524 ranges written (the third segment
included), with a log-mode write breakpoint on `0x002FF8C1`-`0x002FFFFF`:

| | `ram2_v0` (American; 18:55-19:14) | `ram2_v1` (Saturn; 19:14-19:33) |
| --- | --- | --- |
| Load check | both true | first false (its buffer holds the Saturn bytes), second true |
| Sites | `E002` throughout | `00BD` throughout |
| Late in the ending (frame ~22,700) | `uu????????`: eight sites replaced by another module, left alone | `ss????????`, the same |
| Files | American: `MC0E` (player), `MC11`, `MC10`, `MC08`, `MCED` | Saturn: `MC0E` (player, frame 713), `MC11`, `MC08`, `MCED` |
| Writes to the tail | none | none |

(A first `ram2_v1` stopped at its first key: the window lost focus.)

## The User's Play Check (`play_check.py`)

`play_check.py local/loc009/play1` opened `build/loc009_toggle` (a fresh copy
of the user's home with a valid save; 310 s). The user (verbatim): "Both
settings right".

## Regression

Full run after the build changes (`english_files`, the first-segment
address fix; 17:32-18:35): all 17 references match. `name_toggle_v4` added
(Track 01 `53b24d27…`; every file but `MMPACK.PCA` equals
`continue_hints_us_v4`'s) and rebuilt with `--only` (18:54-19:03): match.

## Conclusion

The toggle works: one image, a NAMES row in Options, every name surface
switched, the choice saved with the other settings. The hidden COMBO GAGE
row is gone in that build.

## Reproduction

```bash
SPECS="data/translations/{wolverine,...,cammy}_win_quotes.json data/translations/{...}_ending.json"
./invenv.sh python -m tools.disc.build_english $SPECS local/loc009/files_toggle \
  --patch-version 4 --names toggle --boot-warnings --special --no-challengers \
  --attract-captions local/cap002/art --continue-hints --image build/loc009_toggle
CUE="build/loc009_toggle/X-Men vs. Street Fighter (Japan) (3M).cue"
# a home: a copy of local/loc008/home_opt1 with a good save (local/loc008/bkr_after_opt4.bkr)
MEDNAFEN_HOME=$PWD/local/loc009/home_t5 ./invenv.sh python research/experiments/EXP-0069/boot_stores.py \
  "$CUE" local/loc009/diag3 7200 --watch 002FF8C1-002FFFFF
for v in 0 1; do ./invenv.sh python research/experiments/EXP-0069/toggle_ram.py "$CUE" \
  local/loc009/files_toggle/MMPACK.PCA build/regression/continue_hints_us_v4/files \
  build/regression/continue_hints_saturn_v4/files local/loc009/ram2_v$v 14 15 $v; done
./invenv.sh python research/experiments/EXP-0069/session_writes.py \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/loc009/writes2 14 15 --key
./invenv.sh python research/experiments/EXP-0069/play_check.py local/loc009/play1
```

The menu runs (`menu1`, `menu2`) are `EXP-0068/opt_walk.py` with the steps
in "The Third Segment, Cold Boot and Menu".
