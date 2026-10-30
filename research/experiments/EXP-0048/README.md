# EXP-0048 (Names): Census of Every Name Surface

Task: LOC-001
Status: DONE
Confidence:

- CONFIRMED: every surface and name in the tables, read from the images;
- SUPPORTED: who speaks Magneto's page 3;
- UNKNOWN: at which moments the names are spoken.

## Observation

- **Names that differ between conventions** (`docs/names.md`, `EXP-0011`):
  Gouki / Akuma, Nash / Charlie, and Vega / Bison (Shadaloo's leader).
- **Seen before:** the Saturn's select labels for Gouki and Nash, and the
  arcade select label for Gouki / Akuma. Never observed: Vega's labels,
  every other surface, and voice.
- **The M8 build** (`build/m8_roster_endings`) has American-name English
  text and ending labels.

## Question

For each of the three names, which surfaces show or speak it? What does
each surface show on the Saturn, on the US arcade (`xmvsfu`) and on the
Japanese arcade (`xmvsfjr2`)? And who speaks Magneto's US page 3, labelled
`Vega`?

This experiment only observes. Nothing on the disc changed.

## Inputs and Tools

| Item | Identity |
| --- | --- |
| Saturn image | `build/m8_roster_endings`, Track 01 `7bb8ab82…` (`EXP-0046`) |
| Saturn route screens | `local/end015/r1/s14_a1`, `s15_a1`, `s16_a1` (`EXP-0047`; Vega, Gouki and Nash first, screenshots every 120 frames) |
| Saturn play sessions | `local/end015/session` (`EXP-0047`) and `local/loc001/session` (this experiment, user, 2026-10-30, frames 1-31,668, sound on) |
| Arcade | MAME 0.289, `xmvsfu` and `xmvsfjr2`. Run by a subagent; see [`arcade/RESULTS.md`](arcade/RESULTS.md) |
| [`saturn/menu_walk.py`](saturn/menu_walk.py) | Boots an image cold and walks it with scripted keys, screenshots, and a wait-for-screen step |
| Route key map | `tools.mednafen.route.KEYS` gained Start (N) and B (H), for menus |

## Procedure

**Saturn screens:** contact sheets and enlarged crops (ffmpeg) of:

- the route screens: select, VS screen, fights, win banners, quotes, the
  boss stage and endings;
- the END-015 session: boot, initials entry, staff roll.

```bash
B="build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python research/experiments/EXP-0048/saturn/menu_walk.py "$B" local/loc001/saturn/attract1 wait:9000
```

**Menus:** the scripted walks `menu1` to `menu8` did not reach Option
Mode (below). The user opened it in the voice session instead.

**Voice:** the user played the M8 build with sound on.

- **Option Mode:** they went through Option Mode and Button Config.
- **Select:** they hovered over Vega, Nash and Gouki.
- **Fights:** they played Gouki (first) with Vega (second), then Nash
  first to his first win.
- **Report:** "Heard 'Vega' and 'Gouki' and 'Nash'."

```bash
MEDNAFEN_HOME=$PWD/local/mednafen MEDNAFEN_AGENT_DIR=$PWD/local/loc001/session/agent \
  vendor/mednafen/build-agent/src/mednafen "$B"
./invenv.sh python -m tools.mednafen.session_recorder local/loc001/session \
  --agent-dir local/loc001/session/agent --state-interval 3 --keep-states 200
```

**Arcade:** `arcade/RESULTS.md` lists the commands.

- **Runs:** 13 headless MAME runs: Vega, Gouki and Nash first in both
  sets, Magneto in the Japanese set, Gouki probes, and attract mode.
- **Reading:** every name was read from an enlarged snapshot.
- **Spot-check:** the agent re-cropped four of the subagent's life-bar
  snapshots itself (`local/loc001/spot_lifebars.png`) and viewed the page-5
  picture. Both agree with `RESULTS.md`.

## Actual Result

### Name surfaces

| Surface | Saturn (M8 build) | US arcade | Japanese arcade |
| --- | --- | --- | --- |
| Select label | `VEGA` / `GOUKI` / `NASH` (route `first_cursor.png`) | `BISON` / `AKUMA` / `CHARLIE` | `VEGA` / `GOUKI` / `NASH` |
| VS screen | `VEGA` / `GOUKI` / `NASH` over `CYCLOPS` | `BISON` / `AKUMA` / `CHARLIE` | `VEGA` / `GOUKI` / `NASH` |
| Life bar (player's side) | `VEGA` / `GOUKI` / `NASH` | `BISON` / `AKUMA` / `CHARLIE` (also as the CPU opponent) | `VEGA` / `GOUKI` / `NASH` |
| Win banner | "VEGA / CYCLOPS / WIN", "GOUKI / CYCLOPS / WIN", "NASH / CYCLOPS / WIN" | `BISON` / `AKUMA` / `CHARLIE` | `VEGA` / `GOUKI` / `NASH` (the point character first) |
| Win-quote screen | no name label; the English quotes name "Bison" (Cammy's 0 and 4) | no name label | no Latin label; the Japanese quotes can name ベガ or ゴウキ |
| Ending text | "Charlie" (Nash's 1 and 4), "Bison" (Vega's 1 and 4) | the same | Japanese text, Japanese names |
| Ending labels | `Charlie`, `Charlie's friend`, `Akuma`, `Bison` (Rogue's page 1), `Vega` (Magneto's page 3) | the same | `Nash`, `Nazo no koe`, `Nash's friend`, `Gouki`, `Vega` (Rogue's page 1; every page of Vega's) |
| Apocalypse's pre-fight boxes (boss stage) | Japanese; Apocalypse's line names the player's character in katakana: ベガよ… (Vega run, r009840), ゴウキよ… (Gouki, r009840), あわれなりナッシュ。 (Nash, r009960) | none seen | Japanese; the same kind of naming (ベガ, ナッシュ) |
| Voice | the user heard "Vega", "Gouki" and "Nash" (moments not recorded) | not checked (MAME runs silent) | not checked |

**No character names:**

- **Saturn:** stage cards; the staff roll; initials entry ("1st _");
  attract mode (intro movie with Japanese captions, demo fights with no
  HUD, SCORE RANKING and VS RANKING with initials only); the title menu;
  Option Mode and Button Config.
- **Arcade:** the rankings and initials entry in both sets.

Rankings were seen with default entries only.

**Two observations for later tasks (not names):**

- **Option Mode** labels the taunt button with the romanized `CHOUHATU`.
- **Gouki's cell** is reachable on the arcade grid too: four Ups from
  Cyclops, in both sets.

### Magneto's page 3 (`Vega`)

- **Who is shown:** pages 1-4 show Magneto over Shadaloo's defeated
  leader, with the boxer, the masked claw fighter and a bald man behind.
  Page 5 shows Magneto with the masked claw fighter, the boxer and Sagat
  (`local/loc001/arcade/zoom/mag_us_p5_pic.png`, viewed by the agent).
- **Who speaks (SUPPORTED, not CONFIRMED):** "You've defeated our leader.
  We follow you." is spoken by a subordinate. In US naming, "Vega" is the
  masked claw fighter, who is in the picture. So the label most plausibly
  means him (Saturn naming: Balrog). Nothing on screen ties the label to
  one figure.
- **The Japanese ending** has 4 pages and no `Vega`-labelled page. Its
  page 1 text names シャドルーのベガ (the leader, in Japanese naming).
- **The Saturn's label list** (`MCED`) has `Vega` (`0x0F`), which its
  Japanese scripts use for the leader (Rogue's page 1). It has no
  `Balrog`.

### Failed or invalid attempts

1. **`menu1` to `menu8`** (scripted menu walks):
   - **Timing:** the attract cycle's timing changes with disc loading, so
     fixed frame counts landed Start presses on different screens.
   - **Await step:** the wait-for-screen step matched attract mode's own
     title display, which ignores input.
   - **Learned:** Start during a demo fight brings up the real title
     (`menu5`). A second Start there opens Arcade / Versus / Option
     (`menu6`). Option Mode was not entered by script; the user opened it.
2. **First life-bar crop:** it used transition frames; it was redone from
   mid-fight frames.
3. **Arcade side:** see `arcade/RESULTS.md`. All 13 MAME runs completed.
   The Japanese set's vitality route is SUPPORTED there; it has no
   control run.

## Conclusion

**CONFIRMED** (images read by the agent, evidence above and in
`arcade/RESULTS.md`):

- **Saturn art:** on the select label, the VS screen, the life bar and
  the win banner, the Saturn shows the Japanese convention (`VEGA`,
  `GOUKI`, `NASH`), like the Japanese arcade. The US arcade shows `BISON`,
  `AKUMA` and `CHARLIE` on the same surfaces.
- **The M8 build is mixed:** Saturn-convention art and voice, with
  American-convention English text and ending labels.
- **Boss-stage text:** the Saturn's Japanese pre-Apocalypse boxes name the
  player's character in katakana. Translating them (`SPECIAL-001`) adds
  name mentions that each variant must follow.
- **Rankings, initials, menus, attract mode and the staff roll** name no
  character.

**User-reported:** "Vega", "Gouki" and "Nash" are spoken on the Saturn.
That is the Japanese convention, so the American variant's voice is a
`LOC-003` question.

**SUPPORTED:** Magneto's page 3 speaker is the claw fighter. A
Saturn-names variant would need "Balrog" there, which the label list
lacks (`LOC-004`).

## Uncertainty and Alternatives

- **Voice moments:** when each name is spoken (select, VS, round start,
  win, tag) was not recorded. That is `LOC-003`'s first step.
- **Shadaloo's leader as a CPU opponent** on the Saturn was seen on the
  VS screen only as the player's pick. As the arcade shows, the same name
  art likely serves both sides (HYPOTHESIS for the Saturn).
- **Rankings** were seen with default entries only.
- **Other katakana mentions** in the Japanese win quotes and story text
  were not inventoried. They are Japanese text, outside the English build
  until translated.
