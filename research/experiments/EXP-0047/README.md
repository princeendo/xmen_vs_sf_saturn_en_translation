# EXP-0047 (M8): Verify Every Roster Ending

Task: END-015
Status: DONE
Confidence: CONFIRMED (route pages, reads, forced draws, play check, a
second pick's ending); HYPOTHESIS (who gets the partner fight)

## Observation

- **The build:** `build/m8_roster_endings` (`EXP-0046`, D-041) holds every
  roster character's English win quotes and English ending, and every
  built file loads into both team buffers.
- **Not yet shown:** any of those endings on screen, except Nash's (M7).
- **Arcade references:** the English snapshots of all 17 arcade endings,
  taken every 60 frames (`EXP-0044`, `local/end012/runs/*_en/snap/`), and
  each page's first frame (`local/end012/compare.json`).

## Hypothesis

On the build, each roster character picked first reaches its ending by
the route. Every page k then shows the arcade's English page k: the same
picture, label, text, line breaks and scene breaks. The English ending
bytes are read only while the ending shows them. The win quotes are
unchanged from M5.

## Change

- **Route tool:** Gouki is picked from his cell above Juggernaut's
  (`GOUKI_CELL`; `EXP-0046`), first or second, like any other character.
  This replaces `GOUKI_STATE` and its RAM patching. 1 new test.
- No change to the build.

## Prediction

- **Pages:** for each of the 17 characters, the quote pointer steps
  through quote table + 800 + 100k for k = 0 to n − 1. The screenshot of
  page k matches arcade page k, as checked by the agent.
- **Nash:** pages byte-identical to M7's approved pages.
- **Reads:** the English ending area is read only during the ending.
- **Win quotes:** every win-quote pointer is quote table + 100r with
  r < 8. Ryu's and Ken's 16 forced draws are byte-identical to M5's.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Image | `build/m8_roster_endings`, Track 01 `7bb8ab82…` (`EXP-0046`) |
| Code written by the route | `local/end014/b1/MMPACK.PCA` (`36179171…`) |
| Select state | `local/checkpoints/re004/f00002973.mcs` (route `STATE`) |
| Arcade | `local/end012/runs/s<slot>_default_en` and `local/end012/compare.json` (`EXP-0044`) |
| M5 forced draws | `local/re010/draws_ryu`, `local/re010/draws_ken` (`EXP-0032`) |

## Tools

| Tool | Use |
| --- | --- |
| [`run_endings.py`](run_endings.py) | One route run per roster slot. Up to 4 at once, started 75 s apart; retried on a failed load check |
| [`compare_pages.py`](compare_pages.py) | Each Saturn page's screenshot beside the arcade page's snapshot, one sheet per character |
| [`force_draws.py`](force_draws.py) | `EXP-0032`'s forced draws, with version-4 code and the ending bytes |
| [`play_pages.py`](play_pages.py) | Finds each route page in the play session (whole screen, or text box and label) |
| [`state_reads.py`](state_reads.py) | Quote pointer, fighter blocks and buffer contents from session states |
| [`quote_screens.py`](quote_screens.py) | The session's quote screens, by the bubble colour, on one sheet |
| `research/experiments/EXP-0046/load_check.py` | `verdict` for Rogue's buffer |

## Procedure

```bash
B="build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0047/run_endings.py "$B" local/end014/b1/MMPACK.PCA local/end015/r1 \
  15 17 0 1 2 3 4 5 6 7 9 10 11 12 13 14 16
./invenv.sh python research/experiments/EXP-0047/compare_pages.py local/end015/r1 local/end012/compare.json \
  local/end012/runs local/end015/pages
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0047/force_draws.py ryu local/end014/b1 local/end015/draws_ryu
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0047/force_draws.py ken local/end014/b1 local/end015/draws_ken
# play check (the user plays; interactive home)
MEDNAFEN_HOME=$PWD/local/mednafen MEDNAFEN_AGENT_DIR=$PWD/local/end015/session/agent \
  vendor/mednafen/build-agent/src/mednafen "$B"
./invenv.sh python -m tools.mednafen.session_recorder local/end015/session \
  --agent-dir local/end015/session/agent --state-interval 3 --keep-states 300
./invenv.sh python research/experiments/EXP-0047/play_pages.py local/end015/pages/pages.json \
  local/end015/session local/end015/play_pages.json 17 9 0
S=local/end015/session/states
./invenv.sh python research/experiments/EXP-0047/state_reads.py "$B" local/end015/state_reads2 \
  $S/f00146470.mcs $S/f00146811.mcs $S/f00147150.mcs
./invenv.sh python research/experiments/EXP-0047/quote_screens.py local/end015/session local/end015/quotes
```

The block readings across the boss and partner fights are
`local/end015/state_reads3` and `state_reads4` (every 6th state from
frame 120,000, then every state from 141,527 to 142,551). The contact
sheets `local/end015/boss_end.png`, `cammy_boss.png` and
`cammy_boss_end.png` were made with ffmpeg `xstack` from the session
screenshots.

Each sheet in `local/end015/pages/` was viewed by the agent at full size.
Cammy's labelled rows were also cropped and viewed at full size.

## Actual Result

### Runs

There were 20 runs for 17 characters:

- **Rogue:** `s03_a1` reached her ending, with 305 + 1 reads. Its strict
  load check failed only on her four game-written longs (`verdict`: "pass
  (Rogue's words)"). `s03_a2` was a wrong pick (Ken's file, a lost key).
  `s03_a3` passed.
- **Dhalsim:** `s12_a1` stopped before its pick (Mednafen was not in front;
  the route refuses to send keys blind). `s12_a2` passed.

Every final run loaded both members correctly, and the quote pointer
stepped through every English ending record in order.

### Pages

All 112 pages match the arcade's: the picture, the speaker label (or
none), the text, the line breaks and the scene breaks. Some pictures'
backgrounds cycle colour over time (Cyclops's and Ryu's handshake,
Zangief's Colossus, Cammy's Delta Red), so the two sides can catch
different colours of the same picture.

| Slot | Character | Run | Pages | Labels seen | Saturn page SHA-256 (first 8) |
| --- | --- | --- | --- | --- | --- |
| 0 | Wolverine | `s00_a1` | 6 | Jubilee, Wolverine | `8682da64` `dce8fd77` `bf6a24ef` `172af392` `1f24b102` `e3cfdd14` |
| 1 | Cyclops | `s01_a1` | 9 | Cyclops, Ryu | `2a5bc70b` `087b6a9c` `315eab8f` `f687e373` `cf11f9c4` `c7d90925` `db5774ff` `9b7fe95d` `8f6d4e9f` |
| 2 | Storm | `s02_a1` | 6 | none | `951b249b` `0f6864e3` `7711ca9b` `11ad7f14` `abe81bfa` `5109d97c` |
| 3 | Rogue | `s03_a3` | 6 | Bison, Rogue, Chun-Li | `a5ac59ee` `97e65a06` `87a12050` `c5878bf0` `d7a0936d` `08f32c13` |
| 4 | Gambit | `s04_a1` | 5 | Gambit | `a7d87c4a` `7048bcf4` `d93700af` `ff52ffc8` `69fb4f5e` |
| 5 | Sabretooth | `s05_a1` | 6 | Birdie, Sabretooth, Wolverine | `ea94e4d9` `6dafc778` `9bcd88ba` `695e1b2b` `a521a31a` `7e62f8f0` |
| 6 | Juggernaut | `s06_a1` | 6 | Juggernaut | `06824de8` `4d8e1e00` `806a90c4` `7c739698` `bf1ba0c5` `1c66b8fe` |
| 7 | Magneto | `s07_a1` | 7 | Magneto, Vega | `50cbb27b` `37c79d2b` `474430bd` `7245b750` `46e24f15` `b17b0d33` `75ce306f` |
| 9 | Ryu | `s09_a1` | 7 | Cyclops, Ryu | `3dca1353` `a6954422` `a20ac72f` `76f9c2f2` `a343877d` `42f2b35c` `af3b7e55` |
| 10 | Ken | `s10_a1` | 4 | Ken, His son, Eliza | `e24e2010` `6813dc81` `a5abe592` `e6a6874a` |
| 11 | Chun-Li | `s11_a1` | 6 | Professor X, Iceman, Beast, Archangel | `4aa412bd` `51e41ca3` `a86d5ac0` `0063c056` `5e80c4b7` `ec16525a` |
| 12 | Dhalsim | `s12_a2` | 6 | Dhalsim, Wife | `1161a14c` `55472d40` `ec263b72` `7b5e0d78` `b7c67e08` `3be5ef2c` |
| 13 | Zangief | `s13_a1` | 5 | Zangief, Colossus | `ca6b20ed` `777065b6` `d506a9de` `fa55b977` `51be6677` |
| 14 | Vega | `s14_a1` | 5 | none ("Bison" in the text, pages 2 and 5) | `1644be56` `8cf25854` `e710e10e` `6636b90b` `3f0e969f` |
| 15 | Gouki | `s15_a1` | 6 | Wolverine, Akuma | `f86fa844` `6500966d` `68ba114e` `50d1366f` `854af803` `b7b41970` |
| 16 | Nash | `s16_a1` | 6 | Charlie, Charlie's friend | `65ae6f95` `456fee1d` `a5661877` `fc8fe0c5` `bdfbd8b7` `55a9d2cd` (= M7's approved pages) |
| 17 | Cammy | `s17_a1` | 13 | Matsuo Tsurayaba, Cammy, Psylocke | `0db35cf9` `73c61fe0` `53c5cebf` `c64e625e` `addf01a1` `89c3ed64` `bbc901ea` `82847e63` `65485c7a` `9fc10459` `54a3f9ac` `1febd732` `4a72c13b` |

The gated names show as the arcade shows them:

- `Bison` (Rogue's page 1);
- `Vega` (Magneto's page 3);
- `Akuma` (Gouki's page 5);
- "Bison" in Vega's text.

### Reads of the English ending area

Every read was by `0x06066A84`, the renderer. Reads came only during the
ending, with one exception: the 20 frames in which a win quote showing
English record 7 began.

- **Pattern:**
  - every character with an early read showed record 7 then (for
    example, Wolverine at frame 7,300);
  - every character without one showed no record 7.
- **Counts:** the ending reads are 51 per page minus 1 (for example, 305
  for 6 pages and 662 for Cammy's 13). Each record-7 win quote adds one,
  for 16 of the 17 characters. Dhalsim (one record-7 quote at frame 660)
  has 307, one more.
- **Interpretation:** this is the M7 effect (`EXP-0041`): the renderer
  reads once just past the record it draws. Past record 7 lie the English
  ending's first bytes, where M5 had left-over Japanese bytes. The forced
  draws below show that it changes nothing on screen.

### Win quotes

- **Pointers:** in all 17 runs, every win-quote pointer before the ending
  is the first pick's quote table + 100r with r in 0-7. No pointer fell
  anywhere else in the first buffer.
- **Forced draws:** Ryu's and Ken's 16 draws and the controls all have
  the predicted pointer and codes. All 34 screenshots and VDP1 VRAM dumps
  are byte-identical to M5's (`EXP-0032`, `local/re010/draws_*`). That
  includes draws 7 and 15, which show record 7.

### Play check

**Session:** `local/end015/session`. A cold boot of the build, played by
the user, 2026-10-30 14:47-15:31 UTC, frames 1-150,228. It has 2,575
screenshots and the last 300 states. Kept checkpoints in
`local/checkpoints/end015/`:

- `f00137457.mcs` `7bd584aa…`: the Apocalypse fight, Ryu active;
- `f00142552.mcs` `7cd1c299…`: the partner fight, Ryu against Wolverine;
- `f00146470.mcs` `1035bd66…`: Ryu's ending, page 1.

**Play-through 1: Cammy first, Ryu second.**

- Cammy lost to Apocalypse once (his English win quote, M5), and the user
  continued.
- Cammy beat his first form, and Ryu finished the second.
- The partner fight was Cammy (player) against Ryu (CPU), and Cammy won.
- Her ending followed. All 13 pages were found in the session
  (`play_pages.py`). Pages 1-11 and 13 are byte-identical to the route's
  screens. Page 12 (Delta Red, a colour-cycling background) matched in its
  text box, and the agent checked its picture.

**Play-through 2: Wolverine first, Ryu second, with tags.**

- **Tag:** the user tagged with Z + C (strong punch and strong kick)
  throughout. The blocks swap (`0x060F4200` and `0x060F4A00` change
  between 0 and 9).
- **Boss:** the Apocalypse fight began with Ryu active (`f00137457`).
  Ryu finished it ("RYU / WOLVERINE WIN").
- **After the boss:** Ryu's English win quote, read from the second buffer
  (`0x060B263C`, record 1).
- **Partner fight:** Ryu (player, `0x060F4A00` = 9) against Wolverine
  (CPU, `0x060F4E00` = 0). Ryu won.
- **Ending:** **Ryu's ending, a second pick's**, followed. All 7 pages were
  found. Pages 3-7 are byte-identical to the route's screens; pages 1-2
  (colour-cycling handshake) matched in their text box, and the agent
  checked their pictures.
- **Where it is read from** (`state_reads.py`, three states in the
  ending): the quote pointer was `0x060B28F8`, `0x060B295C` and
  `0x060B29C0`. That is the second buffer + Ryu's table (`0x25D8`) + 800
  + 100k, version 4's rule for a second pick's copy (`EXP-0045`
  hypothesis 2). The first buffer held `MC00` (Wolverine) and the second
  `MC09` (Ryu), both equal to the build's files plus fix-ups.

**Win quotes in the session:** 15 quote screens (`quote_screens.py`, by
the bubble colour; a 16th match was a super-move splash). All are
English: Cammy, Ryu, Wolverine and Apocalypse quotes. Apocalypse's
pre-fight line is still Japanese (`SPECIAL-001`).

**Who gets the partner fight:** in play-through 1, Ryu (second) finished
the boss but Cammy (first) got the player's side. In play-through 2, Ryu
(second) got it. Both runs fit "the character active at the start of the
boss fight": Cammy started it in run 1, Ryu in run 2. In `EXP-0045` the
first pick started it and got the partner fight. Alternatives remain, for
example who K.O.s Apocalypse's first form (Cammy in run 1; not seen in
run 2).

**One block reading did not fit:** at `f00142042`, just before the
boss's K.O. screen, `0x060F4200` held Wolverine (0) while the screen
showed Ryu. So that block is not a reliable "who is active" signal at a
K.O.

## Conclusion

**CONFIRMED:**

- **Route:** all 17 roster endings show on `build/m8_roster_endings` in
  the official arcade English. Every one of their 112 pages matches the
  arcade's page in picture, label, text, line breaks and scene breaks.
  Nash's are byte-identical to M7's.
- **Reads:** the English ending bytes are read only during the ending,
  plus one renderer read past English win-quote record 7. That read
  changes nothing on screen: Ryu's and Ken's forced draws are
  byte-identical to M5's.
- **Win quotes:** unchanged.
- **Play check:** booted cold and played by the user, Cammy's and Ryu's
  endings match the route's screens.
- **Second pick's ending:** it can be reached in normal play (Ryu,
  picked second, after tagging). It is read from the second member's
  buffer at quote table + 800 + 100k, and it shows in English. This
  answers `EXP-0045`'s open question, and version 4's second-pick rule is
  now tested.
- **Tag input:** Z + C pressed by hand tags, on the user's pad.

**HYPOTHESIS:** the character active at the start of the boss fight gets
the player's side of the partner fight, and so the ending (two plays and
`EXP-0045`'s routes agree; alternatives remain).

`END-015`'s criteria are met. `END-016` (coverage and regression) is next.

## Uncertainty and Alternatives

- **Snapshot timing:** the page screenshots are the route's (every 120
  frames) and the arcade's (every 60). Text was compared when complete on
  both; how the text draws over time was not compared.
- **Partner:** every route run used the second cursor's start cell
  (Cyclops, or Wolverine for Cyclops). `END-012` showed that the partner
  changes nothing in the arcade.
- **Dhalsim's extra read** is not explained in detail. It falls in the 20
  frames of his record-7 win quote.
