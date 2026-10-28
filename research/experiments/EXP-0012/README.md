# EXP-0012: Choose the First Character and Win Quote (M1 Target)

Task: REF-008
Status: DONE
Confidence: CONFIRMED (on-screen text and transcription); HYPOTHESIS (speaker identity, arcade slot)

## Observation

M1 needs one ordinary character's win quote, captured on screen and
transcribed. The `EXP-0007` session showed three Saturn win-quote screens: one
after the player's win (team Ryu and Gouki) and two after CPU wins (team
Chun-Li and Rogue).

## Choice

**Ryu**, and the quote shown after the player's win in the `EXP-0007` session
(frame 11244). Reasons:

- Ryu is an ordinary character: not a boss, not a secret (rule 24).
- The quote followed a **player** win, so the user can reach it again by
  picking Ryu and winning the first fight. The two CPU quotes depend on the
  CPU's team.
- It was captured on screen by the agent interface, with no input from the
  agent.
- Ryu has a win-quote slot in the arcade English table. By the region-ROM
  name-list order (anchored at slot 0 = Wolverine and slot 12 = Dhalsim,
  `EXP-0009`), that is slot 9, with 9 records at `0x188DE2`: **HYPOTHESIS**.
  Which English record pairs with this Japanese line is for game-logic
  pairing, not for this task.

## Evidence

- Screenshot `local/ref005/session1/shots/f00011244.png`, 352x240, SHA-256
  `8428bf99…11a6` (`EXP-0007`). The team portraits show Ryu in front and Gouki
  behind; the speech bubble holds two lines.
- The session's select and VS screens show the team as RYU then GOUKI.

## Transcription

```text
この道の先になにがあるのか……
おれはそれが知りたい！
```

- The agent transcribed it from a 3x enlargement.
- A separate agent's blind transcription of the same screenshot is
  identical, including the line break, the six dots (read as two `…`) and
  the full-width `！`.
- Kanji: 道, 先, 知; the rest is hiragana.
- Whether the six dots are stored as two ellipsis codes or six dot codes is
  not visible; the RAM search (`DBG-005`) will show it.
- Agent's gloss, for orientation only (not a translation for the disc): "I
  wonder what lies at the end of this road... I want to know!"

## Uncertainty and Alternatives

- **Speaker:** the line is taken to be Ryu's because he is the front
  (point) portrait and the player's first pick. Which character a team win
  quote belongs to is not established (`DBG-003`).
- **Checkpoint:** the session's rolling states (the last 3 minutes) do not
  include this win. A pre-KO state needs a new user session (`DBG-003`,
  `DBG-004`).

## Reproduction

View the screenshot and compare with the transcription.
