# EXP-0051 (Names): The American-Names Variant

Task: LOC-005
Status: DONE
Confidence: see "Conclusion"

## Observation

- **`LOC-002`** (`EXP-0049`, D-045): the American art for the life bar
  (`FIX.PRS` cells) and the select label (`VS00.PRS` frames
  `0xA8`-`0xAA`) is on the disc. The VS screen and the win banner spell
  their names from `VS00` letter fonts, from a letter list whose source
  was UNKNOWN.
- **`LOC-003`** (`EXP-0050`, D-046): the "Bison", "Akuma" and "Charlie"
  calls are on the disc, as table A entries 18-20.
- **`LOC-004`:** the user chose the American variant from the disc's own
  assets, with no exception for the VS screen and the banner.

## Tracing the choice (before the hypothesis)

- **Life bar:** a PC log on the cell decoder (`0x06024CF0`) from the VS
  screen (`f00007177`) showed GOUKI's cells `0x08A3`-`0x08A5` and VEGA's
  `0x089B`-`0x089D` decoded at the round start. Their 32-byte cell request
  records were written by `0x060249C8` from a sprite list at `0x060E3020`,
  where each code is the cell + `0x5400`.
- **The lists:** WRAM-H `0x06080F00` holds four 19-word lists of those
  codes, each followed by its American twin 38 bytes later:

  | List | Slot 14 | Slot 15 | Slot 16 |
  | --- | --- | --- | --- |
  | `0x06080F00` (CPU side) | `0x5C74` | `0x5C79` | `0x5C65` |
  | `0x06080F26` (its twin) | `0x5C76` | `0x5C7C` | `0x57C8` (CHARLIE, `0x03C8`) |
  | `0x06080F4C` (player side) | `0x5C9B` VEGA | `0x5CA3` GOUKI | `0x5C84` NASH |
  | `0x06080F72` (its twin) | `0x5CA0` | `0x5CA6` | `0x57CC` (CHARLIE, `0x03CC`) |

  The widths follow at `0x06080F98` (CHARLIE: 4 cells).
- **The switch:** the routine at `0x0607FE00` adds 38 to the list offset
  when the word at R11 + `0xD478` is non-zero. R11 is `0x060F8000`, so the
  word is **`0x060F5478`**, the arcade's `0xFF5478`. D-018 called it the
  size word; D-032 found the US arcade sets it.

## Hypothesis

The Saturn keeps the US arcade's region choice for every name surface:
with the word `0x060F5478` non-zero, each surface shows the American name.
Each surface reads the word itself, so the reads can be changed one by
one, leaving the word (and the quote and ending layout it also controls,
D-018) at 0.

## Controlled Changes

1. **The word itself**, in RAM (`patch_run.py`, `060F5478:0000:0002`), as a
   test of the hypothesis only.
2. **Only the reads:** each name surface's read of the word,
   `mov.w @(r0,r11),r0` (`00BD`), changed to `mov #2,r0` (`E002`), with the
   word left at 0. The 10 sites (`tools/disc/names.py`):

   | Address | Surface | How it was found |
   | --- | --- | --- |
   | `0x060639E6` | select label | the only name read in a read log of the word on the select screen |
   | `0x06073A28` | VS-screen name | read log on the VS screen; it picks `0x060845D8` or `0x060845FE` (+38) |
   | `0x0607FDA8`, `0x0607FE0E`, `0x0607FE94`, `0x0607FEFA` | life bar | the four routines that read the lists above, +38 |
   | `0x0607FFA2` | life bar | moves the name 8 px when the slot is 15 and the region non-zero (AKUMA) |
   | `0x0606E004` | win-banner name | read log at the banner; it picks `0x0606E348` or `0x0606E36E` (+38), laid out as the VS lists |
   | `0x0604FBDA`, `0x0604FC52` | name call | read log at the banner; they pick `0x0604FBFC` or `0x0604FC22` (+38) |

   The voice lists hold a sound request per slot: `0xA0` + slot, and in
   the American list `0xB2`, `0xB3`, `0xB4` for slots 14-16. Those are
   table A entries 18-20 (`0xA0` + index), the "Bison", "Akuma" and
   "Charlie" calls (`EXP-0050`).

   **Completeness:** a static scan of the decoded `MMPACK.PCA` for every
   `mov.w` whose literal is `0xD478` found 45 readers. The other 35 are
   region jump tables (`0x0605CDDA`, `0x0605E91E`, `0x0606251E`…),
   comparisons with other region values (4, 6, 8, 10), the four per-frame
   mode checks, constants (`0x0604FD02`: request `0x9E` or `0x9F`;
   `0x0605F784`, `0x0605F838`, `0x06074DDA`), or the quote renderer
   (`0x06066968`, `english_mode`). None of them picks a per-character list.

## Prediction

- Change 1 turns every art surface American.
- Change 2 turns the select label, VS screen, life bar and banner
  American, and plays "Bison", "Akuma" and "Charlie" at the picks and the
  win, with the word still 0.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source Track 01 | `c904a386…da70` (untouched) |
| M8 build | `build/m8_roster_endings`, Track 01 `7bb8ab82…eaf0` (reference `roster_endings_v4`) |
| States (M8 build) | `local/loc001/session/states/` (`EXP-0048`): `f00007004` (Mode Select, Gouki/Vega), `f00007177` (VS screen), `f00007522` (fight), `f00029551` (Nash's win, before the banner); route select state `local/checkpoints/re004/f00002973.mcs` |
| US arcade references | `local/loc001/arcade/zoom/s14`/`s15`/`s16_xmvsfu_*.png` (`EXP-0048`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `research/experiments/EXP-0049/write_log.py` | PC, write and read logs |
| `research/experiments/EXP-0049/patch_run.py` | control and patched runs |
| `research/experiments/EXP-0050/channel_poll.py` | the call channel, with patches |
| `tools/disc/names.py` | the 10 sites; `build_english --names` |
| [`cold_walk.py`](cold_walk.py) | cold boot of a built image with scripted keys, sound recording, and CPU knock-outs |
| `tools.sh2.disasm` | disassembly of the WRAM-H dumps |

## Actual Result

### RAM tests (M8 build)

| Run | Change | Result |
| --- | --- | --- |
| `g_life` | 1 | life bar `AKUMA` / `BISON` (control `GOUKI` / `VEGA`) |
| `g_ban0` / `g_ban1` | CPU vitality 0 / + change 1 | banner `NASH` / `CHARLIE` |
| `g_sel` | 1 | select label `BISON` |
| `g_vs2` | 1 | VS screen `AKUMA` / `BISON` |
| `s_life` | 2 | life bar `AKUMA` / `BISON` |
| `s_ban` | 2 + CPU vitality 0 | banner `CHARLIE` (against `g_ban0`) |
| `s_sel_vega`, `s_sel_gouki`, `s_sel_nash` | 2 | select labels `BISON`, `AKUMA`, `CHARLIE` |
| `s_vs` | 2 | VS screen `AKUMA` / `BISON` |
| `v_vega`, `v_gouki`, `v_nash` | 2 | call channel 10 plays `0x147`, `0x021`, `0x01B` at the pick |
| `v_win` | 2 + CPU vitality 0 | Nash's win plays `0x01B` |

Every patch was checked against the original bytes and held to the end of
its run. The CPU teams on the VS screen differ between some control and
patched runs; they differ between two unpatched-word control runs as well
(`g_vs2` and `s_vs` controls), so they follow the key timing.

### The build

```bash
SPECS=$(python3 -c "import json;r=[x for x in json.load(open('data/regression/references.json'))['references'] if x['name']=='roster_endings_v4'][0];print(' '.join(r['specs']))")
./invenv.sh python -m tools.disc.build_english ${=SPECS} local/loc005/files_us \
  --patch-version 4 --names us --image build/loc005_names_us
./invenv.sh python -m tools.disc.sector "build/loc005_names_us/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
```

- **Image:** `build/loc005_names_us`, Track 01 `441c9cfc…92f3`, from the
  untouched Track 01 `c904a386…da70`.
- **Files:** `MMPACK.PCA` `b5b7927c…ec6e` (original `60dddde3…a79a`).
  The 19 other changed files (17 MC files, `MCED.SHP`…) equal the
  `roster_endings_v4` reference byte for byte.
- **`MMPACK.PCA`:** decoded, it differs from the M8 build's in exactly 20
  bytes, the 10 sites, `00BD` → `E002` each (`local/loc005/files_us/changes.json`).
- **Sectors:** 71,908 checked, 0 invalid (EDC/ECC).

### Cold boot of the built image

`cold_walk.py` boots the image with no save state, so every byte of code
comes from the new disc. It waits for the title, presses Start until the
select screen matches, then plays with the CPU's vitality held at 0.

```bash
N="build/loc005_names_us/X-Men vs. Street Fighter (Japan) (3M).cue"
T=local/loc005/title_ref.png; L=local/loc005/select_ref.png
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$N" local/loc005/coldA2 \
  wait:1800 await:$T:6000 wait:150 press:s:$L:15 wait:60 shot:select0 \
  keys:uuurr wait:60 shot:hover_vega keys:dd wait:60 shot:hover_nash keys:uullu wait:60 shot:hover_gouki \
  keys:a wait:120 shot:pick_gouki keys:uuurr wait:60 shot:hover2_vega keys:a wait:120 shot:pick_vega \
  keys:a wait:150 shot:vs1 wait:150 shot:vs2 wait:450 shot:fight ko:900 wait:600 shot:after
STAGE="wait:600 ko:900 wait:900"
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$N" local/loc005/coldB \
  wait:1800 await:$T:6000 wait:150 press:s:$L:15 wait:60 shot:select0 \
  keys:urr wait:60 shot:hover_nash keys:a wait:120 shot:pick_nash keys:r wait:60 shot:hover2_ryu \
  keys:a wait:120 shot:pick_ryu keys:a wait:150 shot:vs1 ${=STAGE} ${=STAGE} ${=STAGE} ${=STAGE} ${=STAGE} ${=STAGE}
```

`title_ref.png` and `select_ref.png` are screenshots of the title and the
select screen from earlier cold boots (`boot2`, `coldA`). On a cold boot
the select cursor starts on Cyclops (the route's state had it on Ken).

| Surface | Run | Saturn (built image) | US arcade (`EXP-0048`) |
| --- | --- | --- | --- |
| Select label | `coldA2` | `BISON`, `CHARLIE`, `AKUMA` | `BISON`, `AKUMA`, `CHARLIE` (`s14`/`s15`/`s16_xmvsfu_select`) |
| VS screen | `coldA2`, `coldB` | `AKUMA` / `BISON`; `CHARLIE` / `RYU`; CPU `AKUMA` / `WOLVERINE` (stage 6) | `AKUMA` (`s15_xmvsfu_vs_names`) |
| Life bar, player | `coldA2`, `coldB` | `AKUMA` / `BISON`; `CHARLIE` (4 cells, whole) / `RYU` | `AKUMA` (`s15_xmvsfu_lifebar`) |
| Life bar, CPU | `coldB` stage 6 | `AKUMA` / `WOLVERINE` | `CHARLIE` as an opponent (`s15us_opp_charlie_life`) |
| Win banner | `coldA2`, `coldB` | "AKUMA / BISON / WIN"; "CHARLIE / RYU / WIN" (6 times) | "AKUMA / CYCLOPS" (`s15_xmvsfu_win`) |

Same fonts and colours as the arcade; every screenshot was viewed by the
agent (life bars enlarged 3 ×). The boss stage's Japanese box still names
ナッシュ (Nash): it is `SPECIAL-001`'s, outside both variants (`LOC-004`).

**Not seen on the built image:** BISON and CHARLIE on the CPU side (no
CPU team held them). The CPU lists are the same structure as the player's
and the CPU side's AKUMA came from them.

### No other change (the M8 checks on the built image)

```bash
N="build/loc005_names_us/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0047/run_endings.py "$N" local/loc005/files_us/MMPACK.PCA \
  local/loc005/endings 15 17 0 1 2 3 4 5 6 7 9 10 11 12 13 14 16
./invenv.sh python research/experiments/EXP-0047/compare_pages.py local/loc005/endings \
  local/end012/compare.json local/end012/runs local/loc005/pages
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0051/force_draws.py ryu local/loc005/files_us local/loc005/draws_ryu
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0051/force_draws.py ken local/loc005/files_us local/loc005/draws_ken
```

- **Endings:** all 17 roster endings ran on the built image, with the
  built `MMPACK.PCA` written by the route (`--mmpack`, 28 ranges: the
  M8 text patches plus the 10 name sites). Every load check passed; 7
  runs needed a second attempt (lost keys, as in `END-014`; one failed
  run had Ken as the second pick instead of Wolverine).
- **Pages:** 109 pages. 91 screenshots equal `END-015`'s byte for byte.
  The other 18 started at other frames, so their screenshots fall at
  other moments of the pictures' colour cycling; each pair was viewed
  side by side, and the text and labels are the same. The labels stay as
  M8 has them (Rogue's page 1 `Bison`, …): the American variant leaves
  the ending text and labels as written (`LOC-004`).
- **Forced quote draws** (`force_draws.py`: `EXP-0047`'s, plus the 10
  name sites written from the built `MMPACK.PCA`):
  - Ken: all 17 screenshots and 17 VDP1 dumps equal `END-015`'s byte
    for byte.
  - Ryu: all 17 screenshots equal. Every VDP1 dump differs in 29 bytes
    (`0x1FF7`-`0x1FFB`, `0x2112`-`0x217F`). Those are cell-cache records
    of `VS00.PRS` frames (descriptor `0x06025808`) left from the win
    banner: Ryu's case state has Gouki as his partner, and the records
    now hold AKUMA's banner letters (`0xB8`, A) instead of GOUKI's
    (`0xCC`, `0xC5`…). They are the name change itself, not shown on
    the quote screen.

### Voice on the built image (for the user)

Clips cut from the cold-boot recordings (`sound.wav`, 48 kHz stereo):

Each clip was sent alone, without saying which name was expected.

| Clip | Run | Moment | SHA-256 | The user heard |
| --- | --- | --- | --- | --- |
| 1 | `coldA2` | Gouki picked (93.2-96.8 s) | `6a860f46…` | "I heard Akuma." |
| 2 | `coldA2` | Vega picked (102.1-105.7 s) | `c8ab02da…` | "I think I heard \"Bison\"." |
| 3 | `coldA2` | Gouki's team wins (121.5-129.5 s) | `0b945b77…` | "Akuma" |
| 4 | `coldB` | Nash picked (85.4-89.0 s) | `1941f6df…` | "Charlie" |
| 5 | `coldB` | Nash's team wins, stage 1 (113.0-121.0 s) | `37f6165b…` | "Charlie" |

```bash
ffmpeg -i local/loc005/coldA2/sound.wav -ss 93.2 -to 96.8 local/loc005/clips/clip1.wav
```

(and likewise for the others, with the times above).

## Conclusion

**CONFIRMED:**

- **The switch:** the word at `0x060F5478` (R11 + `0xD478`, the arcade's
  `0xFF5478`) chooses a Japanese or an American list for the select
  label, VS screen, life bar, win banner and name call (change 1, and
  each surface's list traced).
- **The sites:** changing only the 10 reads in `tools/disc/names.py` to
  return 2 gives the American names on every surface and the American
  calls, with the word left at 0 (change 2, in RAM and on the built
  image).
- **The build:** `build_english --names us` builds it from the untouched
  source. A cold boot shows BISON, AKUMA and CHARLIE on every art surface
  as the US arcade does, and the user heard "Akuma", "Bison" and
  "Charlie" at the picks and the wins.
- **No other change:** the M8 endings and the forced quote draws match
  `END-015`, apart from the names.

## Uncertainty and Alternatives

- **CPU-side BISON and CHARLIE** were not seen on the built image (no CPU
  team held them). The CPU lists hold them (`0x06080F26`), and the CPU
  side's AKUMA came from the same list.
- **Other readers:** 35 readers of the word were judged not to pick a
  per-character list from their code. One (`0x0604FD02`, request `0x9E`
  or `0x9F`) chooses a region-dependent sound; it was left as the Saturn
  has it.
- **Two-player screens** (Versus Mode, a second player's side) were not
  played. They draw through the same routines (the four life-bar
  routines cover both sides and both team members).
- **Opponent order:** the CPU teams differed between runs. Unpatched
  control runs differ as well, so that was taken as key timing, not the
  patch.
- **The select label's US path** skips a per-slot offset that the
  Japanese path applies (`0x060639EE`-`0x06063A28`). The labels look as
  in the US arcade; the offset's purpose was not traced.

## Reproduction

The build, cold-boot and regression commands are in the sections "The
build", "Cold boot of the built image" and "No other change" above. The
RAM tests:

```bash
B="build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M).cue"
W=local/loc001/session/states; P=research/experiments/EXP-0049/patch_run.py
SITES=$(./invenv.sh python -c "from tools.disc.names import patches; print(' '.join(f'{a:08X}:{o}:{n}' for a,o,n in patches('us')))")
./invenv.sh python $P "$B" local/loc005/g_life $W/f00007177.mcs 420 060F5478:0000:0002
./invenv.sh python $P "$B" local/loc005/s_life $W/f00007177.mcs 420 ${=SITES}
./invenv.sh python $P "$B" local/loc005/s_ban $W/f00029551.mcs 200 060F4610:0019:0000 ${=SITES}
./invenv.sh python $P "$B" local/loc005/s_sel_vega local/checkpoints/re004/f00002973.mcs 60 ${=SITES} keys:uuu
./invenv.sh python $P "$B" local/loc005/s_vs $W/f00007004.mcs 160 ${=SITES} keys:a
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc005/v_vega \
  local/checkpoints/re004/f00002973.mcs uuu a 4 ${=SITES}
```
