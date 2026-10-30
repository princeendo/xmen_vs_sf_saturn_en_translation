# EXP-0048 (LOC-001), Arcade Side: Name Surfaces in `xmvsfu` and `xmvsfjr2`

Status: arcade census done (agent session, 2026-10-30). This file holds
only the arcade side. Nothing here is a Saturn fact.

## Question

The US and Japanese arcade sets use different names for three characters:

- slot 14: Bison / Vega (Shadaloo's leader);
- slot 15: Akuma / Gouki;
- slot 16: Charlie / Nash.

For each set and each of these characters picked first, what name does
each on-screen surface show? Also: does the attract-mode ranking name
characters, and who speaks Magneto's US ending page 3 (label `Vega`)?

## Inputs and Tools

| Item | Identity |
| --- | --- |
| MAME | 0.289 (`/opt/homebrew/bin/mame`), headless, via `research/experiments/EXP-0044/run_mame.py` (unchanged) |
| US set | `local/arcade_roms/xmvsf_mame0289/xmvsfu.zip` `a112cf7b…c8679` (title screen: "961023 USA") |
| JP set | `local/arcade_roms/xmvsf_mame0289/xmvsfjr2.zip` `888e8682…23760` (title screen: "961004 JAPAN") |
| NVRAM/config | `local/ref004` (`EXP-0009`). It has only an `xmvsfu` EEPROM. `xmvsfjr2` runs started without NVRAM, so they used the game's defaults. |
| Timelines | [`make_timeline.py`](make_timeline.py): copy of `EXP-0044/make_timeline.py` (commit `8caed7c`) with `--snap`, `--moves`, `--end` and `--no-coin` added. The changes are listed in its docstring. |
| Viewing aids | [`sheet.py`](sheet.py) (contact sheets) and [`zoom.py`](zoom.py) (crop and enlarge with nearest-neighbour). ffmpeg 9.0.1. |
| Python | 3.13.13 via `./invenv.sh` |

Every name below was read by the agent from the PNG, enlarged with
`zoom.py`. Sheets were used only to find scenes. All outputs, including
`evidence_sha256.txt` (full SHA-256 of every snapshot cited), are in the
ignored `local/loc001/arcade/`.

## Commands

```bash
M=research/experiments/EXP-0048/arcade/make_timeline.py
RUN=research/experiments/EXP-0044/run_mame.py
T=local/loc001/arcade/timelines; R=local/loc001/arcade/runs
# 1. Gouki probe: is there a genuine grid cell? (moves from the Cyclops start cell)
./invenv.sh python $M $T/probe_gouki_uuuu.txt 15 default en --moves uuuu --snap 1690 2400 10 --end 2400
./invenv.sh python $M $T/probe_gouki_uuuul.txt 15 default en --moves uuuul --snap 1690 2400 10 --end 2400
for s in xmvsfu xmvsfjr2; do for m in uuuu uuuul; do
  ./invenv.sh python $RUN $R/probe_gouki_${m}_$s $T/probe_gouki_$m.txt $s & done; done; wait
# 2. Census runs: snapshots every 20 frames from 1800 to the end (24000)
./invenv.sh python $M $T/s14.txt 14 default en --snap 1800 24000 20
./invenv.sh python $M $T/s15.txt 15 default en --moves uuuu --snap 1800 24000 20
./invenv.sh python $M $T/s16.txt 16 default en --snap 1800 24000 20
./invenv.sh python $M $T/s7.txt 7 default en --snap 1800 24000 20
for s in xmvsfu xmvsfjr2; do for c in 14 15 16; do
  ./invenv.sh python $RUN $R/s${c}_$s $T/s$c.txt $s & done; done
./invenv.sh python $RUN $R/s7_xmvsfjr2 $T/s7.txt xmvsfjr2 & wait
# 3. Attract mode: no coins, no input, snapshot every 60 frames to 30000
./invenv.sh python $M $T/attract.txt 0 default en --no-coin --snap 0 30000 60 --end 30000
for s in xmvsfu xmvsfjr2; do ./invenv.sh python $RUN $R/attract_$s $T/attract.txt $s & done; wait
# 4. Viewing (examples)
./invenv.sh python research/experiments/EXP-0048/arcade/sheet.py $R/s15_xmvsfu/snap local/loc001/arcade/sheets/s15_xmvsfu 1800 24000 100 4 4
./invenv.sh python research/experiments/EXP-0048/arcade/zoom.py $R/s15_xmvsfu/snap/xmvsfu_f02300.png local/loc001/arcade/zoom/s15_xmvsfu_life.png 0 0 384 40 4
```

All 13 runs exited normally (`mame.log` ends with "Average speed").
Census runs took about 27 s each, seven at once.

`lang` was `en` in every run, so no language words were written. On
`xmvsfjr2` the game showed its own (Japanese) text.

## Validations Before Use

- **Genuine Gouki pick (CONFIRMED, both sets).** From the Cyclops start
  cell, four Ups move the cursor to a cell above the grid. The big
  portrait and label become Gouki's: `xmvsfu` label `AKUMA` (probe
  f01850 `f7e5f334`), `xmvsfjr2` label `GOUKI` (probe f01850
  `901b92c1`). Button 1 at 1860 picks him. In the census runs he fights
  as the first pick on both sets. So **no `--force-char` was used**; every
  Gouki result here comes from a genuine grid pick. The `uuuul` probe was
  not needed.
- **Grid moves on `xmvsfjr2` (CONFIRMED for slots 14, 15, 16 and 7).**
  The select snapshots show the intended character's portrait and label
  (table below; Magneto from the fight and ending snapshots).
- **CPU vitality words `0xFF4610`/`0xFF4E10` on `xmvsfjr2` (SUPPORTED).**
  Writes start at 3750. In `s14_xmvsfjr2` the CPU bars (GAMBIT/KEN) are
  green at f03760 and red (empty) at f03860 (`519a6d50`). The K.O. comes
  at f03780 and the win banner names the player's team. All four
  `xmvsfjr2` runs then reach stage 2, Apocalypse and the ending. Not
  CONFIRMED because there was no run with the write disabled on this set.
- **First VS screen (stage 1).** At 20-frame spacing it shows in at most
  one snapshot (f02160), and only part-way through: two runs show it,
  four show a flash or the stage card. HYPOTHESIS: the partner-pick
  button presses (every 30 frames until 2470) cut it short. The stage-2
  VS screen is full and stable over about 80 frames, so it is the
  evidence below.

## Results: Player's First Pick

Frame = MAME screen frame; hash = first 8 hex of the snapshot's SHA-256.
Paths are `local/loc001/arcade/runs/<run>/snap/<set>_f<frame>.png`.

### `xmvsfu` (US)

| Surface | Slot 14 (`s14_xmvsfu`) | Slot 15 (`s15_xmvsfu`) | Slot 16 (`s16_xmvsfu`) |
| --- | --- | --- | --- |
| 1. Select label (hover/pick) | `BISON` f01880 `29298c61` | `AKUMA` f01840 `37675f39` | `CHARLIE` f01800 `c06159b5` |
| 2. VS screen (stage 2) | `BISON` / `CYCLOPS` vs `CAMMY` / `ROGUE`, f04820 `accf8ad6` | `AKUMA` / `CYCLOPS` vs `WOLVERINE` / `CAMMY`, f04800 `5587c463` | `CHARLIE` / `CYCLOPS` vs `CAMMY` / `ROGUE`, f04900 `226b55b3` |
| 2a. VS screen (stage 1, partial) | not shown (flash) f02160 `f9bf9418` | `AKUMA` vs `ROGUE` f02160 `469b7b4b` | not shown (tiles) f02160 `c8b51ecf` |
| 3. Life-bar label (P1, top) | `BISON` (over `CYCLOPS`) f02300 `feb2f552` | `AKUMA` (over `CYCLOPS`) f02300 `832cb71f` | `CHARLIE` (over `CYCLOPS`) f02300 `21d8078d` |
| 4. Win banner | `BISON` / `CYCLOPS` / `WIN` f03940 `9a1aee1a` | `AKUMA` / `CYCLOPS` / `WIN` f03920 `286d85bf` | `CHARLIE` / `CYCLOPS` / `WIN` f03980 `dc845928` |
| 5. Win-quote screen | no name shown (portraits and quote only): "I am amused by your incompetence." f04260 `0cbc7551` | no name shown: "Instant Hell Murder. I think I've heard of it..." f04400 `7ede298d` | no name shown: "I do it for my country." f04380 `b8087a37` |
| 6a. Ending speaker labels | none: the ending is narration. The narration text names `Bison` ("But Bison's Psycho Power…" f15400 `1e89e69f`; "Bison turns his attention…" f16400 `c2af96a9`) | `Akuma` f16400 `999d728c` (also `Wolverine`) | `Charlie` f16400 `3b0a0b9c`; `Charlie's friend` f16800 `8f099586` |
| 6b. Other | not examined beyond the surfaces above | Teammate VS `AKUMA` vs `CYCLOPS` f14120 `bb0ec1b7`. Name entry after game over shows only initials (f21840 `8b51e1ae`) | No pre-Apocalypse dialogue box (f12100-12700, every 40 frames; f12500 `bac39d3b`) |

### `xmvsfjr2` (Japan)

| Surface | Slot 14 (`s14_xmvsfjr2`) | Slot 15 (`s15_xmvsfjr2`) | Slot 16 (`s16_xmvsfjr2`) |
| --- | --- | --- | --- |
| 1. Select label (hover/pick) | `VEGA` f01880 `295e3bfd` | `GOUKI` f01840 `88772ccc` | `NASH` f01800 `04b0b791` |
| 2. VS screen (stage 2) | `VEGA` / `CYCLOPS` vs `ROGUE` / `CHUN-LI`, f04900 `3e5ef20f` | `GOUKI` / `CYCLOPS` vs `ZANGIEF` / `JUGGERNAUT`, f04900 `d897ea2e` | `NASH` / `CYCLOPS` vs `CHUN-LI` / `ROGUE`, f04900 `b137e5a7` |
| 2a. VS screen (stage 1, partial) | not shown (stage card) f02160 `6463264a` | not shown (stage card) f02160 `09b2e388` | `NASH` vs `RYU` f02160 `d608f429` |
| 3. Life-bar label (P1, top) | `VEGA` (over `CYCLOPS`) f02300 `b7b1593b` | `GOUKI` (over `CYCLOPS`) f02300 `0030169f` | `NASH` (over `CYCLOPS`) f02300 `1bc36858` |
| 4. Win banner | `VEGA` / `CYCLOPS` / `WIN` f03940 `7d769696` | `CYCLOPS` / `GOUKI` / `WIN` f04020 `6967933b`. Cyclops was on point at the K.O., so his name came first. Later stages show `GOUKI` / `CYCLOPS` / `WIN`, f07000 `db558f43`. | `NASH` / `CYCLOPS` / `WIN` f03940 `40d2645f` |
| 5. Win-quote screen | no Latin name. The Japanese quote contains the katakana ベガ, f04260 `f8ce6187` | no Latin name. Stage 1's quote is Cyclops's, f04340 `d7bb52b4`. Gouki's quote after Apocalypse contains ゴウキ, f14200 `71c860e8` | no Latin name; Japanese quote, f04260 `e7534d1f` |
| 6a. Ending speaker labels | `Vega` (every page) f15400 `a34cb05e` | `Gouki` f16400 `ddb3ab8d`; `Wolverine` f16000 `80a216b3` | `Nash` f16000 `cf02d1a1`; `Nazo no koe` f16200 `e70974c9`; `Nash's friend` f16800 `0dc791be` |
| 6b. Other | **JP-only pre-Apocalypse dialogue box** (top of screen, Japanese). It opens with ベガ, f12600 `0feaec0d` | Same box, Japanese, f12400-12600 (no Latin name) | Same box; it contains ナッシュ, f12600 `37b116de` |

The katakana are named only as name tokens. The Japanese text is not
translated here.

### Same Names Shown as the CPU Opponent (US, from `s15_xmvsfu`)

| Surface | Name | Evidence |
| --- | --- | --- |
| Stage 5 VS | `CHARLIE` / `STORM` | f09200 `c622ffca` |
| Stage 5 life bar (P2 side) | `CHARLIE` | f09440 `8d415e11` |
| Stage 6 VS | `MAGNETO` / `BISON` | f10640 `b700503a` |

The same name art serves both sides. The CPU opponents in the JP runs
were not inventoried for these three names.

### Summary by Surface

On every surface the US set shows **BISON, AKUMA, CHARLIE** and the
Japanese set shows **VEGA, GOUKI, NASH**: select label, VS screen, life
bar, win banner and ending speaker labels. Win quotes never show a Latin
name. CONFIRMED for the frames listed: each was read from the image, and
the runs are reproducible with the commands above.

## Attract Mode (Ranking)

| Set | Screen | Content | Evidence |
| --- | --- | --- | --- |
| `xmvsfu` | SCORE RANKING | rank, score, three-letter initials (JON, MES, BNA, PON, HAC); **no character name, no portrait** | f03960 `a6f9e681` |
| `xmvsfu` | VS RANKING | rank, "2WINS", initials (ISI, KWA, YUM, HRS, MOF); **no character name** | f07200 `eed8a8fd` |
| `xmvsfjr2` | SCORE RANKING | same layout and entries; **no character name** | f03780 `7827cbca` |
| `xmvsfjr2` | VS RANKING | same layout and entries; **no character name** | f06840 `332b8064` |

The attract demo fights in both sets show no HUD (no life-bar names). The
Japanese attract text panels are Japanese. Caveat: the tables held only
default entries. The US set's EEPROM copy showed defaults, and the JP set
started with no NVRAM. Whether a player's entry adds a character is
UNKNOWN. The name-entry screen in `s15_xmvsfu` (f21840) shows only
initials, and no ranking was displayed between it and the title screen.

## Magneto's Ending, Page 3 (`Vega`)

**US** (`local/end012/runs/s7_default_en/snap/`, `xmvsfu`, from `END-012`).
Frame numbers are corrected from the brief's estimate:

| Page | Frame | Hash | Label | Text |
| --- | --- | --- | --- | --- |
| 1 | 15040 | `0b63c6d8` | `Magneto` | "Your failed dream of genetic mutation is over." |
| 2 | 15400 | `1657d85d` | `Magneto` | "I could not let your pathetic quest complete." |
| 3 | 15760-16000 (15880) | `63c8c3e8` | `Vega` | "You've defeated our leader. We follow you." |
| 4 | 16120-16360 (16240) | `cb89df8c` | none | "Will you allow us to serve you as Acolytes?" |
| 5 | 16480 | `a4f51989` | none | "Magneto begins his quest for world domination." |

**Picture, pages 1-4** (one picture; enlarged in
`local/loc001/arcade/zoom/mag_us_p3_pic.png`):

- Magneto stands over a defeated man in red. Only his face (mouth open)
  and a large fist show in the foreground.
- Behind him, on the left, are three figures:
  - a dark-haired, heavily built man in blue and orange (the boxer);
  - a blond figure with a white mask (the claw fighter);
  - a bald, muscular man.

**Page 5** (`mag_us_p5_pic.png`): Magneto with the masked blond figure
(three claw blades visible), the boxer, and the bald man, now with an
eyepatch (Sagat).

**JP set** (`s7_xmvsfjr2`): the ending has 4 pages, as in `EXP-0044`.

| Page | Frame | Hash | Label | Picture and text |
| --- | --- | --- | --- | --- |
| 1 | 15360 | `7f3c3c91` | `Magneto` | Same picture as US pages 1-4. The Japanese text contains シャドルーのベガ (Shadaloo + ベガ). |
| 2 | 15600 | `6d0ed9be` | `Magneto` | Same picture; Japanese text. |
| 3 | 16080 | `985de77a` | **none** | Group picture (as US page 5); Japanese text. |
| 4 | 16320 | `dfed69c0` | **none** | Group picture; Japanese text. |

The Japanese ending has **no `Vega`-labelled page** and no label other
than `Magneto`.

**Finding:**

- **Who is depicted (SUPPORTED).** The defeated man is Shadaloo's leader
  (US "M. Bison", JP "Vega"). Pages 1-4 show him beaten under Magneto.
  The JP page 1 text, spoken by `Magneto`, names him with the katakana
  ベガ. His other three Shadaloo members watch, then line up behind
  Magneto on page 5: the claw fighter (US Vega / JP Balrog), the boxer
  (US Balrog / JP M. Bison) and Sagat.
- **Who speaks page 3 (HYPOTHESIS, fairly strong).** The line says "our
  leader", so the speaker is one of the three subordinates. Under the US
  naming convention, the label `Vega` names the masked claw fighter, who
  is in the picture. Under the Japanese convention, `Vega` would be the
  defeated leader himself, who cannot say "you've defeated our leader".
  So in the US English the label `Vega` most plausibly means the claw
  fighter speaking for the three. It is not M. Bison.
- **What would settle it.** Nothing on screen links the label to one
  figure: no portrait changes and no mouth moves. The label is
  US-convention text inside a US-convention script.
- **Implication (HYPOTHESIS, for the Saturn work, not tested here).**
  - If an English Saturn build shows this label in Japanese-convention
    names, `Vega` would name the wrong person there; the claw fighter is
    `Balrog` in that convention.
  - In the American-name build, `Vega` is consistent.

## Failures, Invalid Runs and Corrections

- No run failed. The `probe_gouki_uuuul_*` runs were made but not used,
  because `uuuu` already reached Gouki.
- Some snapshots are tiny (886 bytes): 3-27 per run, single-colour flash
  frames. None is cited as evidence.
- During analysis, two frames were first misread from a sheet index and
  then corrected on the single image. The teammate VS in `s15_xmvsfu` is
  f14120, not f13280 (that is the post-Apocalypse win banner). Magneto's
  US page 1 is f15040, not f14680 (that is the pre-ending fight). Only
  the corrected frames are cited above and in `evidence_sha256.txt`.
- The first (stage 1) VS screen was not cleanly captured in any run. See
  "Validations"; stage-2 VS screens are the evidence.

## UNKNOWN

- The JP set's CPU-vitality mechanism: SUPPORTED, not CONFIRMED. No
  control run was made without the writes.
- The cause of the clipped stage-1 VS screen: HYPOTHESIS (button presses).
- Whether ranking tables with real entries show a character: UNKNOWN.
  Only default entries were seen.
- In the JP runs, the CPU-side appearances of Vega, Gouki and Nash were
  not inventoried. In the US runs only `s15_xmvsfu`'s were.
- Win quotes against other opponents (one per fight) were not all read.
  The US quotes seen never name a character. The JP quotes can contain
  katakana names (ベガ, ゴウキ).
- The US set shows no pre-Apocalypse dialogue box in the frames checked
  (`s16_xmvsfu` f12100-12700, every 40 frames). Whether it ever shows
  one was not established.
- Voice was not examined (`-sound none`).
- The page-3 speaker's identity: HYPOTHESIS, as stated above.
