# EXP-0014: Named Checkpoints Around the M1 Quote

Task: DBG-004
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0013` kept states from a Ryu-and-Gouki first-fight win. The M1 target is
that session's quote (user decision, 2026-10-28, `EXP-0012`). `DBG-004` needs
reproducible checkpoints before the fight ends, after the K.O., with the quote
visible, and after it disappears.

## Hypothesis

Loading each kept state shows its moment immediately. Running 480 frames from
the quote-visible state reaches a screen after the quote, which can be saved
and reloaded.

## Controlled Change

None to the game; states loaded and one new state saved by the agent.

## Prediction

Each reload shows its named screen; the new state reloads to a screen without
the quote.

## Inputs and Provenance

States in the ignored `local/checkpoints/dbg003/` (hashes in `EXP-0013`).
Patched build, silent home.

## Tools and Environment

[`checkpoints.py`](checkpoints.py).

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0014/checkpoints.py local/dbg004/run2
cp -p local/dbg004/run2/after_quote.mcs local/checkpoints/dbg003/after_quote.mcs
```

A first run failed at saving: `savestate` is refused while halted, even
when `run` comes first in the same command file. The script now sends `run`
and then `savestate` in separate exchanges.

## Actual Result

Named checkpoints (agent-reviewed reload screenshots):

| Name | State | SHA-256 | Reloaded screen |
| --- | --- | --- | --- |
| `pre_ko` | `f00009769.mcs` | `911c14d6…b09d` | Ryu's finishing super connecting |
| `after_ko` | `f00009874.mcs` | `579df1f9…e902` | `K.O.` |
| `win_banner` | `f00009975.mcs` | `1679e26f…499c` | `RYU GOUKI WIN` |
| `pre_quote` | `f00010285.mcs` | `dc1bde9a…89fe` | transition to the quote screen |
| `quote_visible` | `f00010336.mcs` | `70865a0f…b29e` | the M1 quote (two lines); the reload screenshot is byte-identical to the live session's (`e006ebd8…7cc0`) |
| `after_quote` | `after_quote.mcs` (480 frames after `quote_visible`) | `08d1e799…6257` | yellow transition after the quote; reloading it shows the same screen |

## Conclusion

**CONFIRMED:** six named checkpoints bracket the M1 quote. Each reloads to
its screen, and from `pre_ko` the quote is fixed (`EXP-0013`).

## Uncertainty and Alternatives

- `after_quote` was saved a poll or two after the 480-frame halt; its exact
  frame is not recorded.
- Reload screenshots are taken at once after `loadstate`; animated screens can
  differ in phase between launches (asynchronous pause), so comparison is
  visual.

## Reproduction

Run the procedure; expect the six screens listed.
