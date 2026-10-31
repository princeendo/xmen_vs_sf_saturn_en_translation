# EXP-0059 (Special): Official English for the Special Cases

Task: SPEC-002
Status: DONE
Confidence: CONFIRMED unless marked

## Observation

`EXP-0058` (D-052) found three special surfaces:

- the boss stage's boxes (three per player character, in `MC08.SHP`);
- the fixed quote after Apocalypse;
- slot 18, Alpha Chun-Li.

It also found that the US arcade skips the boxes. Slot 18's fixed-table
entry in the builds is `0x0005`, with no English flag.

## Hypotheses

1. **Boxes:** no official English exists for the boss boxes in any
   release this project holds.
2. **Post-boss quote:** the English after Apocalypse is each slot's fixed
   English record, as in the arcade.
3. **Alpha Chun-Li:** the official English is Chun-Li's, in the arcade and
   on the Saturn. In the builds her text is wrong only because her slot's
   flag byte is unset.

## Tools

| Tool | Use |
| --- | --- |
| [`ps1_scan.py`](ps1_scan.py) | Lists the long English runs in the US PlayStation image |
| [`post_boss_pairing.py`](post_boss_pairing.py) | Finds the English record each `EXP-0051` route run showed after the boxes |
| [`fit_patches.py`](fit_patches.py) | RAM writes that put test English into Ryu's boxes |
| `research/experiments/EXP-0058/render_records.py` | Draws the Japanese boxes for reading |
| `research/experiments/EXP-0051/cold_walk.py`, `EXP-0049/patch_run.py` | Saturn walks and controlled changes |
| [`arcade/`](arcade/) (subagent, MAME 0.289 `xmvsfu` only) | `make_tl.py` (timelines), `run_mame.py` (runner, a copy of `EXP-0044`'s), `mame_timeline_op.lua` (a copy of `tools/reference/mame_timeline.lua` plus the verb `logopreads`, which taps the decrypted-opcode space, where the 68000 reads PC-relative tables) |

## Procedure

```bash
U="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
B="build/boot004_us/X-Men vs. Street Fighter (Japan) (3M).cue"
E=research/experiments/EXP-0059
# 1. the PlayStation release
./invenv.sh python $E/ps1_scan.py "local/disc_images/xmvsf_ps1_us/X-Men vs. Street Fighter (USA).bin" \
  --flat local/spec002/ps1_us_flat.bin
# 2. the post-boss quote, from the EXP-0051 route runs (American build)
./invenv.sh python $E/post_boss_pairing.py local/loc005/endings
# 3. the room in the boxes (untouched image, from EXP-0058's walk2 state p0)
for f in 200 300 420; do
  ./invenv.sh python research/experiments/EXP-0049/patch_run.py "$U" local/spec002/fit_$f \
    local/spec001/walk2/p0.mcs $f $(./invenv.sh python $E/fit_patches.py)
  ./invenv.sh python research/experiments/EXP-0049/patch_run.py "$U" local/spec002/fits_$f \
    local/spec001/walk2/p0.mcs $f $(./invenv.sh python $E/fit_patches.py --no-language)
done
# 4. Alpha Chun-Li in the American build
PICK="wait:1800 await:local/loc005/title_ref.png:6000 wait:150 press:s:local/loc005/select_ref.png:15
  wait:60 keys:uur wait:30 chord:sa wait:60 keys:a wait:120 keys:a wait:150 peek:060F4052:2"
ST="wait:600 ko:900 wait:900"
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$B" local/spec002/alpha_us ${=PICK} \
  ${=ST} ${=ST} ${=ST} ${=ST} ${=ST} ${=ST} wait:1500 ko:900 wait:900 wait:600 ko:900 wait:900 wait:6000
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$B" local/spec002/alpha_q ${=PICK} \
  wait:600 ko:300 save:q0 wait:200 save:q1 wait:900 peek:06066704:2
for f in 400 480; do
  ./invenv.sh python research/experiments/EXP-0049/patch_run.py "$B" local/spec002/alpha_flag_$f \
    local/spec002/alpha_q/q0.mcs $f 06066704:0005:0205
done
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$B" local/spec002/alpha_e ${=PICK} \
  ${=ST} ${=ST} ${=ST} ${=ST} ${=ST} ${=ST} wait:1500 ko:900 wait:900 \
  wait:600 ko:200 save:e0 wait:100 save:e1 ko:600 wait:900 wait:1500
for f in 600 1200 1800; do
  ./invenv.sh python research/experiments/EXP-0049/patch_run.py "$B" local/spec002/alpha_end_$f \
    local/spec002/alpha_e/e0.mcs $f 06066704:0005:0285
done
# 5. the arcade (MAME); s11b/s18b add the ending scene breakpoints
A=$E/arcade
for v in s11 s18 s11b s18b; do
  python3 $A/make_tl.py local/spec002/arcade/timelines/$v.txt $v
  python3 $A/run_mame.py local/spec002/arcade/runs/$v local/spec002/arcade/timelines/$v.txt
done
```

The walks' `PICK` step was the alpha walks' literal step list. In
`alpha_us`, `shot:picked` came after the chord and `shot:vs1` after the
second `a`; both are only screenshots.

## Actual Result

### 1. The boss boxes: no official English anywhere

- **Arcade (`EXP-0058`, code trace):** the intro `0x031798` skips the
  box object and its text when the language word is not 0. The English
  branch's base is a placeholder.
- **PlayStation (US):** `ps1_scan.py` found 21 runs of 30 or more English
  codes (the PlayStation stores the arcade's codes little-endian). They
  are the win quotes and endings, the staff credits, and the hint texts.
  Two mention Apocalypse:
  - an ending's narration ("…the destruction of Apocalypse's base…");
  - a win quote ("The age of Apocalypse is at hand!").

  Neither is a box. The release has no box English. This is a data search,
  so it supports the arcade trace; it is not a trace of its own.
- **So:** the boxes need either a new translation or to be skipped, as
  the arcade does (`SPEC-003`).

### Names in the boxes

The agent read the 54 Japanese records (`local/spec002/boxes_0-2.png`,
drawn from decoded `MC08.SHP`):

- The second box (Apocalypse's answer) names the player in every slot.
- Only three of those names differ between the two name variants, and
  only that box holds them:
  - slot 14, ベガ: American "Bison", Saturn "Vega";
  - slot 15, ゴウキ: American "Akuma", Saturn "Gouki";
  - slot 16, ナッシュ: American "Charlie", Saturn "Nash".

  Every other name is the same in both variants (`docs/names.md`).

### 2. The post-boss quote: the fixed English record

`post_boss_pairing.py` checked the 17 route runs of the American build
(`EXP-0051`). In each, the first quote pointer after the boxes is the
slot's English table + 100 × its fixed index (`0x060666E0`). The result
is 17 of 17. The arcade uses the same fixed values and, in fixed mode,
reads that English index directly (`EXP-0058`). So the pairing is the
ordinary win-quote pairing (`PAIR-001`) at a known index. The records are
already English and use the variant names since `LOC-005`/`LOC-006`.

### 3. The room in the boxes

The test wrote three English records at an English stride (100 bytes) in
RAM, from `walk2/p0` (frame 18,780, just before the boxes):

| Run | Change | Boxes |
| --- | --- | --- |
| `fit_200/300/420` | language word `0x060F547A` = 2, region word `0x060F5478` = 2, records | **none drawn**: the boss intro skips them, as in the arcade (patched `c5c7b0bb…`, `e7dba7f7…`, `a71384b5…`) |
| `fits_200/300/420` | region word = 2, records (no language word) | the test English, drawn (patched `15367705…`, `31f40ae7…`, `ced5e2c9…`) |
| controls | none | Ryu's Japanese boxes (`ad97ae53…`, `dd6efe7c…`, `7665541b…`) |

In the `fits` runs:

- With the region word at 2, the box code takes the records at 100 bytes
  each from the same table base (`0x060C2090` + 100 × index; Ryu's index 27
  at byte 2,700).
- It still draws the **Japanese layout**: 2 lines × 19 cells at about
  16 px per cell, reading the first 38 codes of the record.
  - `W`×25 + `M`×25 showed as 19 `W`, then 6 `W` and 13 `M`.
  - "Ryu, you lost warrior." became "Ryu, you lost warri / or. Your fists ca".
- The quote font's Latin glyphs draw correctly in the boxes.

**Room:** the box renderer as it is holds 38 cells per box, in two rows of
19 wide cells. An English record of 2 × 25 cells at 12 px, like the
quotes, would need a renderer change like the quotes' English mode. That
change is not tried. **HYPOTHESIS:** it is feasible, since the quotes
needed one.

### 4. Alpha Chun-Li in the American build

The character word read `0024` in every walk.

**As built** (`alpha_us`):

- **Win quotes:** English letters in the Japanese layout, cut off and
  misaligned. For example, "at was a poor displ / ay." and "omething from
  you!H / ey, welcome!".
- **Boss boxes:** Chun-Li's Japanese boxes.
- **Post-boss quote:** garbled, the same way.
- **Ending:** two pages of garbled English ("…aining room!", "…as
  Jean!"), then Japanese pages (みなさんすばらしい方ばかりで…, やあミス・リー！…,
  おいおいアイスマン…, さあさあ君らは…), then the credits.

  The `alpha_e` walk reproduced this ending.

**One byte, quotes** (`alpha_flag_400`, `alpha_flag_480`, from `q0` at frame
5,790, `292b64c0…`). Write `0x06066704` (slot 18's fixed-table word):
`0005` → `0205`, the English flag of `D-022`.

- Patched: a clean English quote, "My victory was / like lightning!", in
  the English layout (`73b5519a…`).
- Control: the garbled box (`d1e3659a…`).
- The write held to the end.

**One byte, ending** (`alpha_end_600/1200/1800`, from `e0` at frame 23,390,
`55eb3b21…`). Write `0x06066704`: `0005` → `0285`, the English flag plus
the ending bit `0x80` that `ending_slot_patches` sets for slots 0-17.

| Frames | Control | Patched |
| --- | --- | --- |
| 600 | Professor X, "ld see our tr / aining room!" (`f23443e6…`) | Professor X, "Chun-Li..." (`4aa412bd…`) |
| 1,200 | Iceman, やあミス・リー！… (`8adbbd57…`) | Iceman, "Hey, welcome!" (`fa55bf12…`) |
| 1,800 | Archangel, さあさあ君らは… (`270b1397…`) | Archangel, "You're as cute as Jean!" (`05d89822…`) |

The patched pages are Chun-Li's English ending, the lines the arcade shows
for slot 18 (below). Slot 18 already runs Chun-Li's English script in the
builds (`mced_shared_with`, `END-014`). Only its table byte is missing.

### 5. The arcade's slot 18 (subagent, `local/spec002/arcade/`)

Two routed runs: `s11` (Chun-Li) and `s18` (the same route with Start
held). In `s18` the character word `0xFF4052` was written only as `0x0024`.
`s11b` and `s18b` reproduced them exactly.

**Win quotes:**

- The selector `0x04F396` indexes the language's pointer list by the
  character word. Slot 11's entry `0x17E214` and slot 18's entry `0x17E230`
  both hold `0x001894EA`.
- The random index does not use the character. Both runs drew 2, 2, 0, 0,
  2, 0, and read the same records: `rec_reads.txt` is identical,
  `3afb6c3a…`.
- The fixed table read 5 for both (offsets `0x04F3F8` and `0x04F406`), and
  both read record `0x1896DE`.
- On screen: "I expected better. / Why do I expect so much?" (frame 4,320)
  and "I am the strongest woman / in this or any world!" (13,740), in both
  runs.
- **Limitation:** only random indices 0 and 2 occurred. The others are
  covered by the code only.

**Ending:**

- The ending slot `0xFF511A` = character word >> 1: `0x12` for slot 18,
  `0x0B` for slot 11.
- The script table `0x06F8AA` gives `0x0006FCE6` to both.
- The text pointers `0x17E360` (slot 18) and `0x17E344` (slot 11) both hold
  `0x0018C5BE`. Both runs show the same six pages (`0x18C5BE` to
  `0x18C7B2`), pixel-identical on pages 1-3 (`2cddcbd9…`).
- **Art, not text:** from frame 15,720 the arcade draws Chun-Li in her
  Alpha costume in the second scene. The scene jump table `0x06E158` has
  its own entry for slot 18 (handler `0x06E5B8`, against `0x06E7A0` for
  slot 11). How that scene draws the costume is UNKNOWN.

  The Saturn's patched ending showed her usual outfit in that scene. The
  agent read it; there is no pixel comparison.

## Conclusion

**CONFIRMED:**

- **Boxes:** the boss boxes have no official English (arcade code trace).
  The US PlayStation release has none either (data search).
- **Room:** the Saturn box renderer draws 2 × 19 wide cells. With the
  region word at 2 it reads 100-byte records; with the language word at 2
  it skips the boxes.
- **Post-boss quote:** each slot's fixed English record, 17 of 17 in the
  American build; this is the arcade's pairing.
- **Slot 18, arcade:** it uses Chun-Li's English win quotes and ending
  text, at the same addresses.
- **Slot 18, builds:** she shows garbled English and then Japanese, because
  her table word lacks the flags. Writing `0x0205` fixed her quote, and
  `0x0285` fixed her ending, each by one controlled change.

**Names:** only the second box of slots 14-16 depends on the name variant.

## Uncertainty

- **A 2 × 25 box renderer:** not tried (HYPOTHESIS that it is feasible).
- **Alpha Chun-Li's ending art** differs from the arcade's (UNKNOWN
  mechanism; art, outside the text scope).
- **Her other random quotes:** in the builds, only the draws seen in these
  walks were checked with the flag. The arcade covers the rest by code.
