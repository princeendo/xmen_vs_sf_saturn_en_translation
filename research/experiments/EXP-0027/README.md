# EXP-0027 (M4): An English-Slot Table for the Win-Quote Selector

Task: RE-006
Status: DONE
Confidence: CONFIRMED

## Observation

The version-2 English-mode patch tests one slot in code: `@(6,gbr) == 0x12`
(Ryu) at `0x06066668` (`EXP-0023`). Its 11-word block has no spare words. The
task suggested reusing the arcade's remap table at `0x06066718`. That table
has 16 bytes, which cannot hold a byte for each of the 19 win-quote slots
(`EXP-0008`), and SH-2 has no variable shift for a bitmask.

The selector's data area holds a better candidate: the fixed-index table at
`0x060666E0`.

- It has one big-endian word per slot (19 words), with values 0-7.
- The high byte of every word is 0.
- It is read through the literal at `0x060666D8`, which the fixed-index path
  loads at `0x06066688`.

The other data around it:

- the language table at `0x06066708` (4 longs), read at `0x060666AE`;
- the remap table at `0x06066718`;
- the type-6 routine at `0x06066728`, which uses its own remap table at
  `0x060667A8`.

## Hypothesis

Only the fixed-index path reads the fixed-index table, and arcade play never
takes that path. If so, each word's spare high byte can carry the slot's
quote language (0 = Japanese, 2 = English). The selector test can then read
that byte with `mov.b @(r0,r1),r2` and store it as the task flag, in the same
11 words. Adding a character then changes one data byte.

## Controlled Change

Version 3 replaces only version 2's selector block (`0x06066668`, 11 words)
and adds one byte per English slot (`FIXED_TABLE + 2 × slot`, `00` → `02`).
The rest of version 2 (the fixed-path rejoin, the renderer and the ending
selector) is unchanged, and the remap table is not touched.

```text
06066668 D11B  mov.l @(0x060666D8),r1   ; 0x060666E0
0606666A C503  mov.w @(6,gbr),r0       ; slot x 2
0606666C 021C  mov.b @(r0,r1),r2       ; high byte: 0 or 2
0606666E 2228  tst r2,r2
06066670 C501  mov.w @(2,gbr),r0       ; r, or the fixed word
06066672 8906  bt 0x06066682           ; Japanese: index unchanged
06066674 C907  and #7,r0               ; English: r & 7
06066676 E15C  mov #92,r1
06066678 316C  add r6,r1               ; task + 0x5C
0606667A A002  bra 0x06066682
0606667C 2120  mov.b r2,@r1            ; flag = 2
```

On the fixed path, an English slot's word is `0x02xx`. The `and #7` keeps
`xx`, the arcade's fixed index (which has no remap in either language). A
Japanese slot's word is unchanged.

## Prediction

- **No other reader:** no static reference to `0x060666E0`-`0x06066707`
  except the literal at `0x060666D8`, which only `0x06066688` loads. No live
  read of the table in arcade play.
- **Ken:** with v3 code and Ken's English records in RAM, removing slot 10
  from the table gives the unpatched screen byte for byte. Adding it gives
  English record `14 & 7 = 6`, 50/50 cells.
- **Ryu:** all 16 draws equal `EXP-0024`'s version-2 runs byte for byte.
- **A third character (Storm):** v3 equals the unpatched game byte for byte.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Ken `pre_ko` | `local/checkpoints/re004/f00007684.mcs` (`EXP-0025`); paused seed 9501 (1977 one frame later) |
| Ryu `pre_ko` | `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0013`); paused seed 8520 |
| Storm | `local/layout001/session/states/f00019207.mcs` (`EXP-0023` play session; RAM holds version-1 code) |
| RAM dumps | `local/re004/dumps*` (`EXP-0025`) |
| English | US program `local/ref003/xmvsfu-68k.bin`, Ryu `0x188DE2`, Ken `0x189166` (records 0-7) |
| Regression reference | `local/re003/draws_a`, `draws_b` (`EXP-0024`) |
| Images | Source (Ryu, Ken). Storm used `build/re003_ryu_english`, since the version-1 image it was saved on was deleted; nothing is read from disc between that state and the quote (`EXP-0023`). |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`table_refs.py`](table_refs.py) | Static search of WRAM-L and WRAM-H for literals in a range and for PC-relative loads (`mov.w`, `mov.l`, `mova`) into it |
| `tools/mednafen/replay_state.py` | Read-breakpoint logs over replays |
| `tools/disc/english_mode.py` | `SELECTOR_V3`, `slot_patches`, `patches_v3` (new); `check` and `apply` take a patch list |
| [`v3_live.py`](v3_live.py) | Live runs: v3 code and slot table, English records, and seed steering (`EXP-0024`'s seeds for Ryu) |
| `research/experiments/EXP-0023/cell_check_en.py` | Cell check |
| `tests/unit/test_english_mode.py` | Slot-table data, originals check, and a disassembly of the v3 block |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0027/table_refs.py 0x060666E0 0x06066708 \
  local/re004/dumps/f00007684 local/re004/dumps/f00008410 local/re004/dumps/f00003302 \
  local/re004/dumps_ryu/f00009769
./invenv.sh python research/experiments/EXP-0027/table_refs.py 0x060666D8 0x060666DC \
  local/re004/dumps/f00007684 local/re004/dumps_ryu/f00009769
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
C=local/checkpoints/re004
# one per run: ken_preko $C/f00007684 8x120; ryu_preko dbg003/f00009769 8x120;
# ken_fight $C/f00003302 10x200; ken_after_quote $C/f00008410 10x200;
# gouki_ken_fight $C/f00010074 10x200
./invenv.sh python -m tools.mednafen.replay_state "$CUE" $C/f00007684.mcs local/re006/reads_ken_preko \
  --steps 8 --step-frames 120 --bp "read:060666E0-06066707,260666E0-26066707" \
  --agent-dir local/re006/agent_ken_preko
# positive control: the language table
./invenv.sh python -m tools.mednafen.replay_state "$CUE" $C/f00007684.mcs local/re006/reads_control \
  --steps 8 --step-frames 120 --bp "read:06066708-06066717,26066708-26066717" \
  --agent-dir local/re006/agent_control
./invenv.sh python research/experiments/EXP-0027/v3_live.py local/re006/ken \
  ken_orig:ken:orig:- ken_ryu_only:ken:9:- ken_v3:ken:9+10:- ken_orig2:ken:orig:-
./invenv.sh python research/experiments/EXP-0027/v3_live.py local/re006/ryu control:ryu:orig:- \
  0:ryu:9+10:0 1:ryu:9+10:1 … 15:ryu:9+10:15
./invenv.sh python research/experiments/EXP-0027/v3_live.py local/re006/storm \
  storm_orig:storm:orig:- storm_v3:storm:9+10:- storm_v3b:storm:9+10:-
./invenv.sh python research/experiments/EXP-0023/cell_check_en.py local/re006/ken local/ref007/saturn_files/FIX.PRS
```

## Actual Result

**Version 3 against the original code.** All original bytes match the
decoded `MMPACK.PCA`. The disassembly of the patched code is the listing
above. Ryu's word becomes `0x0201` and Ken's `0x0207`, keeping their fixed
indices 1 and 7.

**No other reader of the fixed-index table.**

- **Static:** in four dumps, both regions, the only value in the range is the
  literal at `0x060666D8` (= `0x060666E0`). No PC-relative load targets the
  table. The only load of `0x060666D8` is `D113` at `0x06066688`, the
  fixed-index path.
- **Live, read breakpoint on `0x060666E0`-`0x06066707` and the mirror:** 0
  events in each replay.

  | Replay | Covered |
  | --- | --- |
  | Ken `pre_ko`, 960 frames | K.O., quote, next stage |
  | Ryu `pre_ko`, 960 frames | K.O. and quote |
  | Ken from 3302, 2,000 frames | select screens |
  | Ken from the quote, 2,000 frames | stage 2 select and fight |
  | Gouki and Ken's fight, 2,000 frames | fight |

- **Positive control:** the same Ken replay with the breakpoint on the
  language table logged reads at `0x060666AE` and `0x060666B2`. So the
  breakpoint catches reads here.

**Ken** (natural draw 14, reloaded to seed 9501):

| Run | Code in RAM | Slot table | Index | Flag | Pointer | Cells | Screenshot / VDP1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ken_orig` | original | — | 14 | 0 | `0x0024FE74` | 38/38 (16 px) | reference |
| `ken_ryu_only` | v3 + Ken's English | 9 | 14 | 0 | `0x0024FE74` | 38/38 (16 px) | **identical to `ken_orig`** |
| `ken_v3` | v3 + Ken's English | 9, 10 | 6 | 2 | `0x0024FCA4` (English record 6) | 50/50 (12 px) | English |
| `ken_orig2` | original | — | 14 | 0 | `0x0024FE74` | 38/38 | identical to `ken_orig` |

`ken_ryu_only` and `ken_v3` differ in exactly one byte (`0x060666F4`), so
that byte alone decides Ken's language.

**Ryu regression:** the control and all 16 draws with v3 (slots 9 and 10)
have pointers and codes equal to `EXP-0024`'s. Their screenshots and VDP1
VRAM are **byte-identical** to `EXP-0024`'s version-2 runs (17 of 17).

**Third character (Storm):** `storm_v3` and `storm_v3b` have screenshots
(`da85e4a3…`) and VDP1 VRAM (`1bc2549f…`) byte-identical to `storm_orig`.
The quote is a CPU win:

- Storm knocks out the player's character, then speaks.
- Her record 12 (arcade Japanese slot 2 record 12) is read from her file in
  WRAM-H: table `0x060C50D4`, file base `0x060C1000`, `MC02` offset
  `0x40D4`.
- The bytes at `0x060F8AC0` + 38 and + `0x5C` (1 and 48 in every Storm run)
  are therefore not her quote task's.

The patch finds the task through r6, as version 2 did.

**Tests:** 157 pass (7 new in `tests/unit/test_english_mode.py`).

## Conclusion

**CONFIRMED.** Version 3 makes English a per-slot data byte:

- The high byte of the slot's fixed-index word (`0x060666E0` + 2 × slot)
  set to 2 switches that speaker's win quote to the English mode.
- Only the fixed-index path reads that table, and it keeps the low byte.
- Ken switches with his byte and stays byte-identical to the unpatched game
  without it.
- Ryu's 16 draws are byte-identical to version 2.
- Storm, whose slot is not marked, is byte-identical to the unpatched game.

The remap table at `0x06066718` is not needed and stays unchanged.

## Uncertainty and Alternatives

- **The fixed-index path is still not reached in play.** Its English
  behaviour (fixed index, flag 2) follows from the code, not from a run.
- **CPU speakers:** an English slot also switches a CPU speaker's quote. This
  is expected, since the build changes the character's MC file wherever it
  loads, but no CPU win by Ryu or Ken was run.
- **The build still uses version 2.** `tools.disc.build_english` uses version
  2 (`PATCHES`) until `RE-007` generalizes it.
- **The quote task's address varies** (Storm's run). The patch does not
  depend on it, but `EXP-0024`-style checks that read `0x060F8AC0` apply only
  to player wins like those observed.
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect the tables above: 0 table reads (and control
hits), Ken's three outcomes, 17 byte-identical Ryu runs, and identical Storm
runs.
