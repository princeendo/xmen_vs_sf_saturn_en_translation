# EXP-0042 (M7): Play Check of Nash's English Ending

Task: END-008
Status: DONE
Confidence: CONFIRMED

## Observation

`build/m7_nash_ending` (`EXP-0041`, D-035) was built from the untouched
source. It holds:

- all 18 roster characters' English win quotes;
- Nash's English ending records;
- version 4 of the code patch;
- Nash's `MCED` script switched to English.

The no-play route showed the six pages with the build's code written into
RAM, not booted from the disc. `END-008` asks for a cold-boot play check
by the user.

## Hypothesis

Booted cold from the build, with Nash picked first and played to his
ending:

- the six pages are the layout the user chose (`LAYOUT-002`), byte for
  byte;
- every win quote in the session is English.

## Change

None beyond the build. The image is `build/m7_nash_ending`, Track 01
`2abe9771…`, checked before the session.

## Prediction

- **Ending:** every page shows the same screen as `EXP-0041`'s route and
  `EXP-0038`'s RAM trial:
  - page 1 `65ae6f95…`;
  - page 2 `456fee1d…`;
  - page 3 `a5661877…`;
  - page 4 `fc8fe0c5…`;
  - page 5 `bdfbd8b7…`;
  - page 6 `55a9d2cd…`.
- **No Japanese** in any ending box.
- **Win quotes:** every one is English, including the one after
  Apocalypse.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Image | `build/m7_nash_ending` (`EXP-0041`), Track 01 `2abe9771…` |
| Session | `local/end008/session`: cold boot, user playing, 2026-10-30 01:20-01:36 UTC, frames 257-54,094, 915 screenshots, last 150 states kept |
| Kept checkpoints | `local/checkpoints/end008/f00050413.mcs` `0a2dd9bb…` (before page 1), `f00050757.mcs` `2855400e…` (page 1) |
| Approved pages | `local/end007/route_after2/shots` (`EXP-0041`) |

## Procedure

```bash
MEDNAFEN_HOME=$PWD/local/mednafen MEDNAFEN_AGENT_DIR=$PWD/local/end008/session/agent \
  vendor/mednafen/build-agent/src/mednafen "build/m7_nash_ending/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python -m tools.mednafen.session_recorder local/end008/session \
  --agent-dir local/end008/session/agent --state-interval 3 --keep-states 150
```

Analysis:

- **Ending:** text-box hashes (`crop=300:44:30:180`) and whole-screenshot
  SHA-256 of the session against the six approved pages.
- **Quotes:** contact sheets of every 3rd screenshot from frame 7,000 to
  50,600, each quote screen checked at full size.

## Actual Result

**Team:** Nash and Ryu, Nash picked first. Nash won every stage, beat
Apocalypse and won the partner fight.

### Ending

| Page | First matching shot | Session shots byte-identical to the approved page | Text box |
| --- | --- | --- | --- |
| 1 | `f00050791` | 6 | same as approved |
| 2 | `f00051146` | 6 | same |
| 3 | `f00051510` | 7 | same |
| 4 | `f00051924` | 7 | same |
| 5 | `f00052329` | 6 | same |
| 6 | `f00052683` | 11 | same |

- **Text:** the pages are English: black / "Victory has a price.";
  captive; captive; black / `Charlie` / the scream; Guile / `Charlie's
  friend` / dog tags; Guile / revenge. No Japanese in any box.
- **Credits:** the staff roll and `GAME OVER` followed as before.
- **Before and after:** the untouched image's pages are `EXP-0034`'s
  `9d66b488…`, `361438a2…`, `4c3ef8e4…`, `388c0716…`, `78a2207a…`,
  `ab2f6006…`.

### Win quotes (all English)

| Frame | SHA-256 | Quote |
| --- | --- | --- |
| 7,739 | `b428230c…` | Nash: "I break the sound barrier…" |
| 12,305 | `d45a75f6…` | Nash: "I do it for my country." |
| 18,827 | `5069e46a…` | Nash: "I'm just following orders." |
| 24,113 | `0fd15d04…` | Nash: "I do it for my country." |
| 32,906 | `3f0ac0b9…` | Nash: "Didn't even scratch my lens." |
| 38,906 | `f989512b…` | Ryu, second member, before the boss stage: "So many I have fought…" |
| 46,192 | `51f88902…` | Nash, after Apocalypse: "You don't have the mettle to be a fighter." |

**Still Japanese, as expected:**

- Apocalypse's pre-fight line (`SPECIAL-001`);
- the `⚠乱入禁止` warning (`UI-001`).

## Conclusion

**CONFIRMED:**

- Booted cold from `build/m7_nash_ending` and played by the user, Nash's
  ending shows the official arcade English in the Saturn's English layout.
  It is screen-identical to the layout the user chose.
- Every win quote in the session is English.

M7's build and play check are done. `END-009` adds the build to the
regression references.

## Uncertainty and Alternatives

- **One team:** Nash and Ryu, Nash first. Nash as the second pick is not
  covered (`END-013`).
- **Screen hash match:** the session's page screenshots equal the route's
  byte for byte. So the cold boot and the route's code-in-RAM method agree
  for this ending.
