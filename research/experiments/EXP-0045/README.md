# EXP-0045 (M8): Saturn Route to Any Roster Ending; Whose Ending Plays

Task: END-013
Status: DONE
Confidence:

- CONFIRMED: the route tool, the fighter blocks, and "the player's win
  gives the first pick's ending; the partner's win gives none";
- SUPPORTED: no second-pick ending in play;
- UNKNOWN: how to make the second pick finish the boss.

## Observation

- **The route:** `EXP-0041`'s `saturn_route.py` reached Nash's ending with
  no play, but it picked only Nash and its partner was whoever came next.
- **Team rule:** M8 must show whose ending plays for any team, and where a
  second pick's ending text would be read from. `END-011` included
  second-pick endings.

## Hypotheses

1. A route tool can pick any grid character first or second, and reach
   that team's ending.
2. The ending belongs to whoever the player controls in the partner fight.
   If the second pick is active when Apocalypse falls, the player controls
   the second pick there, and the second pick's ending is read from its
   WRAM-H buffer `0x060B0000` + table + `0x4C0` (+ `0x320` with version 4).

## Tool

`tools/mednafen/route.py` (promoted from `EXP-0041`; 11 unit tests in
`tests/unit/test_route.py`):

- **Picks:** `grid_moves` from Ken (first cursor) and from Cyclops (second
  cursor). The tests check them against the `EXP-0032` pick strings.
  Gouki (slot 15) starts from `GOUKI_STATE`, which already has Gouki as
  the first pick. On a built image, `MC0F`'s changed bytes are written
  into the first buffer.
- **Load check:** both members' buffers are compared with their MC files
  from CUE's track, plus fix-ups.
- **Fighter blocks:** found here from the `EXP-0041` dumps:
  - `0x060F4200`, `0x060F4A00` (player side) and `0x060F4600`,
    `0x060F4E00` (CPU side), the arcade's `0xFF4xxx` layout at
    `0x060Fxxxx`;
  - character at + `0x23` (slot × 2), vitality at + `0x10`;
  - `0x060F4200` holds the player's active fighter: its contents swap with
    `0x060F4A00` at a tag (`+0x20`, `+0x23`, `+0x51`, `+0x52` and
    vitality all swap).
- **Policies:**
  - `first` (zero the CPU side);
  - `second` (knock out the first pick at the boss);
  - `tag` (send the pad's Z + C chord at the boss);
  - `cpu_final` (zero the player's side in the partner fight).

  The phases (boss, partner) are detected from the blocks' characters.
- **Code:** `--mmpack` writes the build's code into RAM (`EXP-0041`).

## Procedure

```bash
O="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
B="build/m7_nash_ending/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r1 --first 16 --second 9 --policy first --frames 18500
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r3 --first 16 --second 9 --policy cpu_final --frames 18500
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r4 --first 0 --second 17 --policy first --frames 18500
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r6 --first 0 --second 17 --policy cpu_final --frames 18500
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r2d --first 16 --second 9 --policy second --frames 20000
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r5d --first 0 --second 17 --policy second --frames 20000
./invenv.sh python -m tools.mednafen.route "$B" local/end013/r7d --first 9 --second 16 --policy second \
  --frames 20000 --mmpack local/end007/b1/MMPACK.PCA
./invenv.sh python -m tools.mednafen.route "$O" local/end013/r2t --first 16 --second 9 --policy tag --frames 20000
./invenv.sh python -m tools.mednafen.route "$O" local/end013/g1 --first 15 --second 1 --policy first --frames 20000
./invenv.sh python research/experiments/EXP-0045/gouki_pick.py local/end013/gouki1 ruuuu uuuu ruuu
```

Each run brings Mednafen to the front for the picks (and for each tag
chord). The runs were made one at a time, from a Python driver. A first
attempt in zsh passed the command as one word, and nothing ran.

## Actual Result

The load checks passed in every run, for both members.

| Run | Team (first, second) | Policy | Partner fight (player's side) | Outcome | Pointer |
| --- | --- | --- | --- | --- | --- |
| r1 | Nash, Ryu | first | Nash | Nash's ending | `0x0024FEC0` + 76k (first buffer) |
| r3 | Nash, Ryu | cpu_final | Nash, beaten by Ryu | Ryu's win quote, continue, no ending | `0x060B2624` (Ryu's quote, second buffer) |
| r4 | Wolverine, Cammy | first | Wolverine | Wolverine's ending | `0x00250DFC` + 76k (`MC00` table + `0x4C0`) |
| r6 | Wolverine, Cammy | cpu_final | Wolverine, beaten by Cammy | Cammy's win quote, continue, no ending | `0x060B30E4` (second buffer) |
| g1 | Gouki, Cyclops | first | Gouki | Gouki's ending | `0x002502CC` + 76k (`MC0F` table + `0x4C0`) |
| r7 (first try) | Ryu, Nash (M7 build) | second, ineffective | Ryu | Ryu's Japanese ending (Ryu is not marked in M7) | `0x0024FA98` + 76k |

**Making the second pick finish the boss (not achieved):**

| Attempt | What happened |
| --- | --- |
| `second`, one write (r2, r5, r7) | The first pick was not knocked out. Apocalypse fell to the first pick ("PERFECT"), and the ending was the first pick's. |
| `second`, 900 frames from Apocalypse's arrival (r2b, r5b, r7b) | The window ran out during his pre-fight dialogue. Same outcome. |
| `second`, until the partner is active (r2c, r5c, r7c) | The partner was already in the active block during the dialogue, so it stopped at once. Same outcome. |
| `second`, once the first pick has been seen active (r2d, r5d, r7d) | The first pick was knocked out, and **the match ended**: Apocalypse won, the continue screen followed, and the partner never came in. |
| `tag`, Z + C every 300 frames (r2t) | No tag happened. The first pick stayed in, and Apocalypse won. Whether the keys arrived, or the tag needs another input, is unknown: the chord sender skips silently when Mednafen is not in front. |

**Gouki:**

- `GOUKI_STATE` (`local/re004/session/states/f00009348.mcs`) is the second
  pick, with Gouki already picked first. In it, moves up from Cyclops reach
  Juggernaut or Dhalsim, not Gouki's cell. How to reach the cell is still
  unknown.
- From that state, the route reaches Gouki's ending (g1).

## Conclusion

**CONFIRMED:**

- `tools.mednafen.route` reaches any roster character's ending as the first
  pick, Gouki included (from his state), with both members' files loading
  correctly.
- In every run, the partner fight puts the first pick on the player's side.
- When the player wins it, the first pick's ending plays, read from the
  first member's buffer (WRAM-L).
- When the partner (CPU) wins, its win quote is read from the second
  member's buffer (WRAM-H `0x060B0000` + its table), and the run goes to
  the continue screen with no ending.

**SUPPORTED:**

- No second pick's ending was reached by any route.
- Knocking out the first pick at the boss loses the match.
- The game's tag could not be triggered.
- Whether the player can ever face the partner fight as the second pick
  (for example by tagging in play before Apocalypse falls) is UNKNOWN.
  `END-015`'s user play check should try it by hand.

**For M8:** first-pick endings cover every roster character. Version 4's
rule for a second pick's copy (`0x060B0000` + table + `0x320`) remains
untested on screen.

## Uncertainty and Alternatives

- **The tag input** (Z + C) is a HYPOTHESIS from the Saturn pad layout
  (X, Y, Z punches; A, B, C kicks), and it was not seen to work.
- **Two teams** (plus Gouki's) were run per policy; other teams were not.
