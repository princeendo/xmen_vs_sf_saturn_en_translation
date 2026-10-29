# EXP-0034 (M6): Reach Nash's Ending and Inventory Its Text

Task: END-001
Status: DONE
Confidence: CONFIRMED (reach, inventory and repeatability); the team rule
is SUPPORTED only

## Observation

No Saturn ending had been reached (`TASKS.md`, Phase K). Before the session,
the user was given the candidates with each one's arcade English ending
record count, Saturn after-table record count and whether the user could
beat Apocalypse with them. The user chose "Nash (Recommended)". Nash is
slot 16 (`MC10.SHP`): 6 arcade English ending records (`0x17E318`) and 6
after-table records in `MC10` (`data/text/slot_census.json`).

## Hypothesis

A cold-boot arcade run on the untouched source image, with Nash picked
first, reaches Nash's ending after Apocalypse. From a checkpoint taken just
before the final K.O., the ending replays with no input and gives the same
screens every time.

## Controlled Change

None to the game. The user played the untouched image. The agent recorded
it and then replayed from the session's own checkpoints in stock-input
Mednafen (the quiet home, no pad mapped).

## Prediction

- The ending shows Japanese text pages after the final K.O.
- Two no-input replays from the pre-K.O. checkpoint are pixel-identical to
  each other at every page, and the ending pages equal the session's
  screenshots at the same frames.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m`, Track 01 `c904a386…` (checked at the start) |
| Emulator | `vendor/mednafen/build-agent/src/mednafen` (agent build, `EMU-020`), home `local/mednafen` for play, `local/mednafen_quiet` for replays |
| Session | `local/end001/session`, 2026-10-29 18:30-19:38 UTC, frames 134-229,689: 3,935 screenshots, 1,345 states (all kept, 6.5 GB) |
| Kept checkpoints | `local/checkpoints/end001/` (below) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools.mednafen.session_recorder` | `--state-interval 3 --keep-states 0` (screenshot each second, state every 3 s, none pruned) |
| `ffmpeg` (tiles, crops, raw RGB) | Contact sheets; region hashes |
| `replay_ending.py` | Loads a checkpoint, runs to fixed frames with no input, screenshots and hashes the whole image, the text box (`crop=300:44:30:180`) and the picture window (`crop=160:96:96:40`); compares with the session's screenshot at the same frame |

## Procedure

```bash
# play (user), recorded by the agent
MEDNAFEN_HOME=$PWD/local/mednafen MEDNAFEN_AGENT_DIR=$PWD/local/end001/session/agent \
  vendor/mednafen/build-agent/src/mednafen "<source cue>"
./invenv.sh python -m tools.mednafen.session_recorder local/end001/session \
  --agent-dir local/end001/session/agent --state-interval 3 --keep-states 0
# replays (two processes at once)
export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python research/experiments/EXP-0034/replay_ending.py \
  local/checkpoints/end001/f00220064.mcs local/end001/replay/r1
./invenv.sh python research/experiments/EXP-0034/replay_ending.py \
  local/checkpoints/end001/f00220064.mcs local/end001/replay/r2
# losing the partner fight: no input from the fight's start, every 300 frames
./invenv.sh python research/experiments/EXP-0034/replay_ending.py \
  local/checkpoints/end001/f00217852.mcs local/end001/replay/partner 9000 300
```

(The replays above were run from `local/end001/session/states/`, of which
`local/checkpoints/end001/` holds byte copies.)

## Actual Result

### The route

The team was Nash (first pick, point) and Ryu. Every screenshot below was
checked by the agent.

| Frames (session) | What is on screen |
| --- | --- |
| ~210,184 | A story line in the win-quote layout (Nash and Ryu, two Japanese lines in the bubble) before the boss stage |
| ~211,000-216,444 | Apocalypse fight; `NASH RYU WIN` at ~216,559 |
| ~216,914 | Black screen with Nash's sprite; `⚠乱入禁止` ("no challengers") at top right, shown from here to the end of the partner fight |
| ~217,028-217,265 | Win-quote screen, two Japanese lines |
| ~217,378-220,117 | `NASH VS RYU`, then the **partner fight: Nash against Ryu**; the player's last hit lands at ~220,002-220,064, `K.O.` at 220,117, `NASH WIN`, bonus tally |
| 220,539-222,930 | **Nash's ending: six pages** (below) |
| ~222,981-226,589 | Staff roll over a galaxy, all in English, then `THANK YOU FOR PLAYING / PRESENTED BY CAPCOM` |
| ~226,838-226,953 | `Presented by CAPCOM` with the QSound notice (English, plus one Japanese trademark line) |
| ~227,068-228,466 | `GAME OVER` initials entry, score ranking (English) |
| ~228,591- | Capcom logo, attract |

So the final K.O. before the ending is the **partner fight's**, not
Apocalypse's.

### The six pages

One layout: a picture window at the top centre (black on pages 1, 2 and 5),
a purple box at the bottom with up to two lines of Japanese, and on pages
3-6 a small speaker label in Latin letters just above the box. Text is not
copied here (rule 21).

| Page | First shot (frame) | Lines | Speaker label | Picture | Sample SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 1 | 220,591 | 1 | none | black | `f00220654.png` `9d66b488…ddbd` |
| 2 | 220,825 | 2 | none | black | `f00220887.png` `361438a2…48f6` |
| 3 | 221,112 | 1 | `Nash` | Nash captive | `f00221112.png` `4c3ef8e4…3d8e` |
| 4 | 221,342 | 2 | `Nazo no koe` (romanized Japanese, "mysterious voice") | Nash captive | `f00221342.png` `388c0716…8dcc` |
| 5 | 221,630 | 1 | `Nash` | black | `f00221690.png` `78a2207a…91df` |
| 6 | 221,925 | 2 | `Nash's friend` | Guile | `f00222037.png` `ab2f6006…fa94` |

Pages 1-5 last about 4 s each; page 6 about 17 s. There is no input
prompt; the pages advance on a timer.

### Repeatability

| Target frame | r1 = r2 (whole image) | Replay = session (image, box, picture) |
| --- | --- | --- |
| 220,654 (p1) | yes | yes, yes, yes |
| 220,887 (p2) | yes | yes, yes, yes |
| 221,112 (p3) | yes | yes, yes, yes |
| 221,342 (p4) | yes | yes, yes, yes |
| 221,690 (p5) | yes | yes, yes, yes |
| 222,037 (p6) | yes | yes, yes, yes |
| 223,044 (credits) | yes | no: the scrolling staff roll is about 3 px lower in the replay (same names) |

Both processes exited 0. The credits difference is consistent with the
session's screenshot being taken a frame or so away from its labelled frame
on a slowly scrolling screen; the static pages are unaffected.

### Losing the partner fight

From the partner fight's first checkpoint (`f00217852`, `FIGHT!`), 9,000
frames with no input: Ryu wins, Ryu's win quote, `CONTINUE?` (with a
Japanese hint and the `⚠乱入禁止` warning), `GAME OVER`, initials, score
ranking, attract. **No ending plays.**

### Kept checkpoints (`local/checkpoints/end001/`)

| File | SHA-256 (first 16) | Moment |
| --- | --- | --- |
| `f00210163.mcs` | `28a8bdee26287f35` | Pre-boss story line |
| `f00216311.mcs` | `a1fbe6f73fb05384` | Apocalypse fight, just before his K.O. |
| `f00217852.mcs` | `1000ddbd2079d09e` | Partner fight, `FIGHT!` |
| `f00219894.mcs` | `1e0aadf0067daec1` | Partner fight, during the final combo |
| `f00220064.mcs` | `7c5a7257065b2ca1` | After the last hit, before `K.O.` (the replay checkpoint) |
| `f00220576.mcs` | `70c8db20d38e9db2` | Fade into page 1 |
| `f00220745.mcs` | `171b74068251eaec` | Page 1 |
| `f00220917.mcs` | `11f2cf90ccad93e7` | Page 2 |
| `f00221258.mcs` | `dbad90c0412c80f7` | Page 3 |
| `f00221426.mcs` | `42e49734401fa9e7` | Page 4 |
| `f00221763.mcs` | `99f28549c3d3db26` | Page 5 |
| `f00221934.mcs` | `5db9632fe7b73950` | Page 6 (picture fading in) |

## Conclusion

**CONFIRMED:** Nash's ending is reached on the untouched image by winning
the partner fight that follows Apocalypse. It is six timed pages in one
boxed layout, with Latin speaker labels on four of them, and it replays
pixel-identically from `f00220064` with no input. Losing that fight gives a
continue screen and no ending.

**Team (SUPPORTED, not confirmed):** the ending followed Nash, who was the
first pick, the point character, and the winner of the partner fight. One
run cannot separate these. That a lost partner fight gives no ending
suggests the ending belongs to whoever the player controls in that fight;
`END-004` tests it in MAME.

**Count match (HYPOTHESIS):** six Japanese pages, six arcade English
records, six after-table records in `MC10`. Nothing yet ties them together;
that is `END-003` and `END-004`.

## Uncertainty and Alternatives

- **Partner choice:** whether the player can ever control the partner in the
  final fight (and get the partner's ending) was not tried.
- **Continue after the partner fight:** not tried; whether continuing
  replays the partner fight or ends the run is unknown.
- **Speaker labels:** they are already Latin text, but `Nazo no koe` is
  romanized Japanese. Whether the arcade English ending has labels at all is
  for `END-004`.
- **Win screens around the boss:** the pre-boss story line and the
  post-Apocalypse win quote use the win-quote layout. Whether they come from
  the quote table (and so would already be English in the roster build) is
  unknown; Apocalypse-specific text belongs to `SPECIAL-001`.

## Reproduction

Run the replay commands above against `local/checkpoints/end001/`. Expect
r1 = r2 everywhere, and the six page hashes above.
