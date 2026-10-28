# EXP-0013: Does the Win Quote Vary From One Pre-KO State?

Task: DBG-003
Status: DONE
Confidence: CONFIRMED

## Observation

The M1 target is Ryu's win quote after a player win (`EXP-0012`). Whether
replaying one checkpoint always shows the same quote decides how checkpoints
must be planned (`DBG-004`).

## Hypothesis

Replaying one state saved before the K.O. shows the same quote every time.

## Controlled Change

None to the game. The same state is replayed unattended, with no input,
several times.

## Prediction

The speech-bubble pixels are identical across replays of one state.

## Inputs and Provenance

- A new recorded user session (2026-10-28, from 22:07:47 UTC, frames
  140-10544): interactive home, patched build (`EXP-0006`),
  `session_recorder.py --state-interval 1 --keep-states 180`. All 180 states
  were kept.
- Route: Ryu and Gouki, a win in the first fight (Rogue and Cammy
  opponents), finished with a super move.
- Checkpoints, copied to the ignored `local/checkpoints/dbg003/`:

  | State | Moment | Size | SHA-256 |
  | --- | --- | ---: | --- |
  | `f00009769.mcs` | finishing super connecting, before the K.O. | 5,136,397 | `911c14d6…b09d` |
  | `f00009874.mcs` | K.O. on screen | | `579df1f9…e902` |
  | `f00009975.mcs` | `RYU GOUKI WIN` banner | | `1679e26f…499c` |
  | `f00010285.mcs` | transition before the quote screen | | `dc1bde9a…89fe` |
  | `f00010336.mcs` | quote visible | | `70865a0f…b29e` |

## Tools and Environment

`tools/mednafen/replay_state.py` (`DBG-002`), silent home; speech-bubble
comparison by SHA-256 of a raw RGB crop (`crop=280:40:60:190` of the 352x240
screenshot).

## Procedure

```bash
for s in 9769 9874 9975 10285; do for n in 1 2 3; do
  ./invenv.sh python -m tools.mednafen.replay_state \
    "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
    local/dbg003/session/states/f0000$s.mcs local/dbg003/replay/s$s-r$n \
    --steps 8 --step-frames 120 --agent-dir local/dbg003/replay/agent
done; done
```

## Actual Result

- **Live session quote** (frame 10336, `e006ebd8…7cc0`, agent-read):

  ```text
  もう一度鍛え直してこい。
  その時にまた会おう！
  ```

  The same Ryu-and-Gouki screen as the `EXP-0012` quote, but a different
  line.
- **All 12 replays** (4 states × 3) show this same speech bubble: the crop
  hash equals the live one in every replay, 2-3 steps each. From state 9769
  the replay shows the K.O., the quote, then the stage 2 card, with no
  input (agent-reviewed).
- Screens before and after the quote differ between replays by animation
  phase (other crop hashes), as MSHvSF also saw (asynchronous pause).

## Conclusion

**CONFIRMED.**
- From a fixed state, as early as the finishing super before the K.O., the
  win quote is fixed: 12 of 12 replays showed the same quote.
- Across play sessions it varies: two sessions with the same team and a
  first-fight win showed different quotes.
- So one checkpoint yields one quote. Seeing others needs other checkpoints,
  or forcing the selector in RAM (the arcade's is the slot base `0xFF8BB4`,
  `EXP-0009`; the Saturn's is unknown).

## Uncertainty and Alternatives

- When the choice is made (at the K.O., earlier in the fight, or from a seed
  in the state) is not known; only that it is fixed by frame 9769.
- The speaker is still taken to be Ryu (front portrait); not confirmed.
- Three replays per state; a rare roll could still differ.

## Reproduction

Run the procedure with the kept checkpoints; expect the live bubble hash in
every replay.
