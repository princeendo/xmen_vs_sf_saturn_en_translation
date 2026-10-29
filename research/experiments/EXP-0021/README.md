# EXP-0021: Identify the Win-Quote Selector and Force Any Record

Task: RE-002
Status: DONE
Confidence: CONFIRMED

## Observation

Ryu's 16 win-quote records sit in WRAM-L from `0x0024F5D8` (`EXP-0015`). The
quote shown is the same in every replay from `pre_ko` but differs between
sessions (`EXP-0013`, `EXP-0018`). MSHvSF found an index store and a record
pointer between the K.O. and the quote (MSHvSF `EXP-0025`), which is a
HYPOTHESIS here.

## Hypothesis

One code path reads the shown record through a pointer computed from an
index. Writing a chosen index right after the game stores its own makes that
record appear.

## Controlled Change

Each forced run makes one write, the byte at WRAM-H `0x060F8AE6` (rule 12):

| Field | Value |
| --- | --- |
| Address | WRAM-H `0x060F8AE6` (quote task `0x060F8AC0` + 38) |
| Original byte | `0x0A` (the game's random choice from `pre_ko`) |
| Written byte | the forced index, applied by the agent's `onhit` right after the store at `0x06066696` |
| Purpose | Force the shown record |
| Expected | Pointer `0x060F2490` = `0x0024F5D8` + 76 × index, and that record is drawn |
| Observed | As expected for indices 0, 1, 5, 8 and 15 |

The control sets the same write breakpoint with no `onhit` write.

## Prediction

- Each forced run shows record `k` exactly: all 38 drawn cells equal the
  glyphs decoded from `FIX.PRS` for record `k`'s codes.
- The control shows record 10, byte-identical to the live capture.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Checkpoints | `pre_ko` `f00009769.mcs` and `pre_quote` `f00010285.mcs` (`EXP-0014`); WRAM-H/L extracted to `local/font001/s*/` |
| Emulator | patched build (`EXP-0006`), silent home |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/mednafen/replay_state.py` | Read and write logs |
| `tools/sh2/disasm.py` | Disassembly |
| [`force_record.py`](force_record.py) | The forcing runs |
| `research/experiments/EXP-0020/cell_compare.py` | Cell check |

## Procedure

```bash
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
  local/checkpoints/dbg003/f00009769.mcs local/re002/reads --steps 12 \
  --step-frames 60 --bp "read:0024F5D8-0024FC5F,2024F5D8-2024FC5F"
./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
  local/checkpoints/dbg003/f00010285.mcs local/re002/ptr_writes --steps 2 \
  --step-frames 60 --bp "write:060F2490-060F2493,260F2490-260F2493"
./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
  local/checkpoints/dbg003/f00010285.mcs local/re002/idx_writes --steps 2 \
  --step-frames 60 --bp "write:060F8AE6-060F8AE6,260F8AE6-260F8AE6,060F8AF4-060F8AF7,260F8AF4-260F8AF7"
./invenv.sh python research/experiments/EXP-0021/force_record.py local/re002/force1
./invenv.sh python research/experiments/EXP-0021/force_record.py local/re002/force2 control 5 1 8
./invenv.sh python research/experiments/EXP-0020/cell_compare.py local/re002/force1 \
  local/ref007/saturn_files/FIX.PRS
```

## Actual Result

**Reader.** From `pre_ko` to the quote screen there are exactly 38 reads of
the table, all at `0x06066A84`. At the first one, R8 = `0x0024F8D0` (record
10) and MACL = `0x2F8` (10 × 76). The surrounding code is a script
interpreter: `trapa #62` calls the address in the next longword and
`trapa #63` returns. It loads R8 from the longword at WRAM-H `0x060F2490`
(R11 + `0xA490`), and adds 38 for line 2.

**Pointer.**

- `0x060F2490` is 0 at `pre_ko`, `after_ko`, `win_banner` and `pre_quote`, and
  `0x0024F8D0` at `quote_visible`.
- Its only writer, `0x0606698C`, computes base + index × size:
  - base = the longword at task + 52;
  - index = the byte at task + 38;
  - size = 76, or 100 when the word at R11 + `0xD478` is nonzero.
- Here the task is `0x060F8AC0` (R12).

**Index.** In one frame, after a clear of the task (`0x06081F1E`):

- `0x06066696` stores the index;
- `0x060666D0` stores the table base `0x0024F5D8`;
- the pointer is computed.

The index is the return value of `0x06056B54` & `0x0F`. That routine is the
game's random-number generator: seed word at WRAM-H `0x060F545A`, seed =
seed × `0xB0` mod `0x7FED`, then returned.

Two flags change the choice:
- the word at R11 + `0xD47A` nonzero: remap through a table at `0x06066718`;
- the byte at R11 + `0xD083` nonzero: take a fixed index from a table at
  `0x060666E0`.

Both were 0 in these runs.

**Forcing** (two sessions):

| Run | Index | Pointer | Cells exact | Screenshot |
| --- | --- | --- | --- | --- |
| control (×2) | 10 | `0x0024F8D0` | 38/38 | `e006ebd8…` (= live capture), identical across sessions |
| 0 | 0 | `0x0024F5D8` | 38/38 | `cb99b2c9…` |
| 1 | 1 | `0x0024F624` | 38/38 | — |
| 5 (×2) | 5 | `0x0024F754` | 38/38 | `21cbd826…`, identical across sessions |
| 8 | 8 | `0x0024F838` | 38/38 | — |
| 15 | 15 | `0x0024FA4C` | 38/38 | `cb83b073…` |

- In every run the drawn record equals table record `k` at `quote_visible`.
- The game's own choice, the setter's R0, was 10 every time.
- The task was at `0x060F8AC0` in every run.
- Five PCs write the index byte in these runs; the byte is reused task
  memory.

## Conclusion

**CONFIRMED:**

- The shown record is chosen when the quote starts, after the K.O. (between
  `pre_quote` and `quote_visible`), as `RNG() & 0x0F`.
- It is fixed from `pre_ko` only because the generator's seed is saved in
  the state.
- The record pointer is `0x060F2490`, and the index byte is quote task + 38
  (`0x060F8AE6` here).
- An `onhit` write after `0x06066696` forces any record. The prediction
  held for 5 distinct indices across two sessions, against a control equal
  to the live capture.
- This is a debug harness only; it never ships.

## Uncertainty and Alternatives

- **Task address:** the quote task was at `0x060F8AC0` in every run from this
  checkpoint. MSHvSF's quote task landed in one of two slots, so another
  session may put it elsewhere (HYPOTHESIS). The script then needs the
  setter's R6. A PC-keyed write to R6 + 38 would be address-independent.
- **The two flags:** the meaning of `0xD47A` (100-byte records, remap) and
  `0xD083` (fixed index) is not tested. They might be versus mode, a special
  opponent or a language setting.
- **Other characters:** whether they use the same path is not tested (M4).
- **Arcade comparison:** that the arcade draws its English index the same
  way is `PAIR-001`.

## Reproduction

Run the procedure. Expect:

- the pointers and screenshot hashes above;
- 38/38 cells per run.
