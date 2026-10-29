# EXP-0025 (M4): Map Ken's Quote File, Slot and Load Addresses

Task: RE-004
Status: DONE
Confidence: CONFIRMED

## Observation

Ryu's quote table comes from `MC09.SHP`, which loads to WRAM-L `0x0024D000`
(`EXP-0017`, D-012). The win-quote selector picks `RNG() & 0x0F`, and the
version-2 English-mode patch tests the slot word `@(6,gbr)` against Ryu's
`0x12` (`EXP-0021`, `EXP-0023`). The arcade's 16-bit name list orders the
characters Wolverine, Cyclops, Storm, Rogue, Gambit, Sabretooth, Juggernaut,
Magneto, Apocalypse, Ryu, Ken, Chun-Li, Dhalsim, Zangief, Vega, Gouki, Nash,
Cammy, … (region ROM `0x503E4`, `EXP-0011`). Slots 0, 9 and 12 had matched
this order before (`EXP-0009`, `EXP-0015`).

**Choice.** The user chose **Ken** (2026-10-29). Their answer, verbatim, to
a choice of Ken, Wolverine, Cyclops and Zangief (each offered with slot, file
and English record count): "Ken (Recommended)". Ken is arcade slot 10 by the
name list, with 9 English records, and plays like Ryu.

## Hypothesis

Ken's quote table is loaded from `MC0A.SHP` (`MCxx` holds slot `0xXX`) by the
same loader as Ryu's, when Ken is picked. The selector then sees slot word
`0x0014`, and the table equals the arcade's Japanese slot 10 records.

**Static prediction (before the live trace).** The decoded `MC0A.SHP` (48,060
bytes) holds the arcade Japanese slot 10 records 0-15 at offset `0x2A4C`,
then 5 of slot 10's ending records (Ryu's file has 6). If the file loads at
`0x0024D000` like Ryu's, the table is at WRAM-L `0x0024FA4C`.

## Controlled Change

One variable: the pick. From session state 2973 (cursor on Ken, before the
first pick), with a halt-mode write breakpoint on `0x0024FA4C`-`0x00250087`
(21 records) and its `0x2024…` mirror:

- **Control:** no input for 120 frames.
- **Trial:** Saturn pad A (key K in the scratch home) for 0.2 s, twice.

## Prediction

- The control has no hit.
- The trial halts in Ryu's loader at `0x0600D124` with R12 = `0x0024FA4C`
  and a file size of `0x5ADA` (23,258 bytes, `MC0A.SHP`'s size).
- After the load, RAM at `0x0024D000` equals the decoded file except for
  relocation fields.
- At the selector, `@(6,gbr)` = `0x0014`.

## Inputs and Provenance

- **User session** (2026-10-29, interactive home, patched build `EXP-0006`,
  untouched source image): `session_recorder.py --state-interval 1
  --keep-states 0`, 186 states and screenshots, frames 67-10074, in the
  ignored `local/re004/session/`. Route:
  - Ken first, Cammy second. A win over Chun-Li and Rogue, finished with a
    super, then the Japanese quote.
  - Reset (F10). Gouki first, Ken second, up to the first fight.
- **Checkpoints** in the ignored `local/checkpoints/re004/`:

  | State | Moment | SHA-256 |
  | --- | --- | --- |
  | `f00002973.mcs` | cursor on Ken, before the pick | `c412271e…9b8326d5` |
  | `f00003083.mcs` | Ken picked, cursor on the partner | `dc93f7d6…d0eed9cc` |
  | `f00007684.mcs` | Ken's finishing super, before the K.O. (`pre_ko`) | `8e4a8b01…cf9c56d4` |
  | `f00008410.mcs` | Ken's quote visible | `ec25e21d…4cca8fa9` |
  | `f00010074.mcs` | Gouki and Ken, first fight | `ff680211…ce876330` |

  Others kept: 2917, 3027, 3302, 7633, 7789, 9503, 9555, 9606 and 9711.
- **Reference:** `local/checkpoints/dbg003/f00009769.mcs` (Ryu and Gouki,
  `pre_ko`, `EXP-0013`).
- **Source:** Track 01 SHA-256 `c904a386…da70`, checked before the session.
- **Arcade:** the US program `local/ref003/xmvsfu-68k.bin` (`EXP-0008`).
  Japanese win-quote table `0x17E19C`, endings `0x17E2CC`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/mednafen/session_recorder.py` | The user's session |
| [`dump_states.py`](dump_states.py) | WRAM-L and WRAM-H at each checkpoint, plus the record pointer |
| [`catch_loader.py`](catch_loader.py) | The control and trial. Adapted from `EXP-0017`'s, with Ken's state and table. |
| [`slot_at_selector.py`](slot_at_selector.py) | Halts at the English-mode test site `0x06066668` and reads `@(2,gbr)` and `@(6,gbr)` |
| [`analyze.py`](analyze.py) | Matches MC files, arcade records and dumps. It prints only offsets, counts and addresses. |
| `tools/sh2/disasm.py` | Selector disassembly |

## Procedure

```bash
C=local/checkpoints/re004
./invenv.sh python research/experiments/EXP-0025/dump_states.py local/re004/dumps \
  $C/f00002973.mcs $C/f00003083.mcs $C/f00003302.mcs $C/f00007684.mcs $C/f00008410.mcs \
  $C/f00009503.mcs $C/f00009606.mcs $C/f00009711.mcs $C/f00010074.mcs
./invenv.sh python research/experiments/EXP-0025/dump_states.py local/re004/dumps_ryu \
  local/checkpoints/dbg003/f00009769.mcs
./invenv.sh python research/experiments/EXP-0025/catch_loader.py local/re004/control --control
./invenv.sh python research/experiments/EXP-0025/catch_loader.py local/re004/catch1
./invenv.sh python research/experiments/EXP-0025/catch_loader.py local/re004/catch2
./invenv.sh python research/experiments/EXP-0025/slot_at_selector.py local/re004/slot1 \
  $C/f00007684.mcs local/checkpoints/dbg003/f00009769.mcs
./invenv.sh python research/experiments/EXP-0025/analyze.py local/re004/dumps/f00003083 \
  local/re004/dumps/f00007684 local/re004/dumps/f00010074 \
  local/re004/dumps_ryu/f00009769 > local/re004/analysis.json
./invenv.sh python -m tools.sh2.disasm local/re004/dumps/f00007684-workramh.bin \
  --base 0x06000000 --start 0x0606663C --end 0x06066694
```

## Actual Result

**Trace.**

- **Control:** 0 breakpoint events in 120 frames (the screen still
  animated: before and after screenshots differ).
- **Trial (catch1, frame 310):** halted at PC `0x0600D124` (`mov.l
  r2,@r12`), R12 = `0x0024FA4C`.
  - R5 = R9 = `0x5ADA`, the file size. Only `MC0A.SHP;1` has this size in
    the listing.
  - R6 = R10 = `0x0024D000`, the destination.
  - GBR = `0x06001FC0`.
- **Repeat (catch2, frame 290):** identical registers and byte-identical
  WRAM-L. The frame differs only by key timing.
- **Final script (catch3):** the helpers first imported from `EXP-0017` were
  copied in unchanged, for strict typing. A third run gave the same registers
  and WRAM-L.
- At the halt, WRAM-L `0x0024D000`-`0x0024FA4B` equals the first `0x2A4C`
  bytes of the decoded `MC0A.SHP`.

**File to RAM.** In every dump where the file is resident, RAM equals the
decoded file except for big-endian 32-bit fields holding the file value +
base + `0x40`. Some of those fields are only 2-byte aligned. None is in the
quote table.

| Character (file) | Quote offset | Endings after | Fields (2-aligned) | Bases seen |
| --- | --- | --- | --- | --- |
| Ken (`MC0A`) | `0x2A4C` | 5 | 302 (123) | `0x0024D000` (first: 3083, 7684), `0x060B0000` (second: 10074) |
| Ryu (`MC09`) | `0x25D8` | 6 | 259 (106) | `0x0024D000` (first: 9769) |
| Gouki (`MC0F`) | `0x2E0C` | 4 | 328 (136) | `0x0024D000` (first: 10074), `0x060B0000` (second: 9769) |
| Cammy (`MC11`) | `0x2F1C` | 12 | 316 (120) | `0x060B0000` (Ken's partner: 7684), `0x060C1000` (opponent: 9769) |
| Chun-Li (`MC0B`) | `0x349C` | 7 | 436 (218) | `0x060C1000` (opponent: 7684, 10074) |
| Rogue (`MC03`) | `0x3F94` | 8 | 430 (161) | `0x060D2000` (opponent: 7684, 9769, 10074); 8 bytes at file offsets `0x9333`-`0xBDE6` are unexplained, none near the table |

Ryu's 259 fields agree with `EXP-0017`, which also counted them as longs.

**Slot.** The halt at `0x06066668`, unpatched, from `pre_ko`:

| State | GBR | `@(2,gbr)` draw | `@(6,gbr)` | Caller (PR) |
| --- | --- | --- | --- | --- |
| Ken `f00007684` | `0x06001FC0` | `0x000E` (14) | **`0x0014`** (slot 10 × 2) | `0x0602D86E` |
| Ryu `f00009769` | `0x06001FC0` | `0x000A` (10) | `0x0012` (slot 9 × 2) | `0x0602D86E` |

Draw 14 gives `0x0024FA4C` + 14 × 76 = `0x0024FE74`, the record pointer
(`0x060F2490`) read at the quote screen (state 8410). Ryu's draw 10 is the M1
record (`EXP-0016`).

**Identity.** Ken's table (RAM and file) equals the arcade's Japanese
win-quote slot 10 records 0-15, byte for byte. Records 16-20 equal slot 10's
first 5 Japanese ending records. The next 76 bytes are not text, so Ken's
table has 21 records against Ryu's 22.

**Disassembly note.** Unpatched, the selector reads `@(6,gbr)` only on the
fixed-index path (`0x0606668A`). The patch reads it at `0x06066668`, where
it holds the speaker's slot × 2 for both characters.

## Conclusion

**CONFIRMED** (`RE-004`):

- Ken's quote table is loaded from `MC0A.SHP` by the loader at `0x0600D124`
  when Ken is picked. It sits at decompressed offset `0x2A4C`.
- The table loads at WRAM-L `0x0024FA4C` (file base `0x0024D000`) when Ken is
  first. It loads at WRAM-H `0x060B2A4C` (file base `0x060B0000`) when he is
  second. The same two bases held Ryu's and Gouki's files.
- The selector sees slot word `0x0014` (arcade slot 10) when Ken speaks.
- Records 0-15 are the arcade Japanese slot 10 quotes. The table holds 21
  records (16 quotes, 5 ending records).

`MCxx` holds slot `0xXX` is **CONFIRMED** for slots 9 and 10 (traced). It is
**SUPPORTED** for slots 3, 11, 15 and 17 (content and RAM match, no trace).

**Correction.** `TASKS.md` said a partner's file was at WRAM-H `0x060D5F94`.
That address is Rogue's record 0, in an **opponent's** file (base
`0x060D2000`). The second team member's file loads at `0x060B0000`.

## Uncertainty and Alternatives

- **Who speaks when the second member wins:** in both sessions the speaker
  was the first member, read from WRAM-L. Whether a second-member speaker
  reads its own table from WRAM-H is not observed. `RE-007`'s build must
  cover both files' tables either way, since a character can be first or
  second.
- **The bases may depend on mode or team:** they were seen in arcade mode
  with three teams. Other modes are untested.
- **Table length:** quote tables differ in length (21 records for Ken, 22 for
  Ryu), so the 16 quotes are the only fixed part. The English build writes
  over records 0-7 only.
- **Rogue's 8 unexplained bytes:** probably runtime state, not examined.
- **Real hardware:** not tested.

## Reproduction

Run the procedure. Expect:

- control: no events;
- trial: halts at `0x0600D124` with R12 = `0x0024FA4C` and R5 = `0x5ADA`,
  and the two halts identical;
- selector: `0x0014` for Ken, `0x0012` for Ryu;
- `analysis.json` as in the table above.
