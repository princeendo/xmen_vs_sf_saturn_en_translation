# EXP-0026 (M4): Pair Ken's Saturn Records With the Arcade English

Task: PAIR-002
Status: DONE
Confidence: CONFIRMED

## Observation

Ken's Saturn quote table holds the arcade's Japanese win quotes for slot 10,
records 0-15 (`EXP-0025`). For Ryu (slot 9), the arcade selector at
`0x04F396` shows Japanese record `r` and English record `r mod 8` for the same
draw `r = rand() & 0x0F` (`EXP-0022`). The arcade has 9 English records for
slot 10 (pointer table `0x17E1E8`).

## Hypothesis

Ken follows the same rule. Saturn record `k` pairs with English slot 10
record `k mod 8`, and English record 8 is never chosen.

## Controlled Change

The method and tool are `EXP-0022`'s (`run_pair.py`, unchanged): MAME
`xmvsfu`, the `EXP-0009` route, NVRAM and configuration. Per run:

- the speaker slot is forced to 10 (D1 = `0x14` at `0x04F396`);
- the draw is forced into D0 after the random call (`0x04F3B2`);
- Japanese runs set the language word `0xFF547A` and the size word
  `0xFF5478` to 0.

The control runs the route with nothing forced, in both languages.

## Prediction

The first text read (PC `0x04F612`) is:

- Japanese: `0x18137C` + 76 × `r` (slot 10 base);
- English: `0x189166` + 100 × (`r mod 8`) (slot 10 base).

The control repeats `EXP-0022`'s natural run: slot 12, draw 10, English record
2, Japanese record 10.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Emulator and ROMs | MAME 0.289; ROM set `xmvsfu` |
| Route state | `local/ref004/nvram` and `cfg` (`EXP-0009`), copied per run |
| Arcade tables | `local/ref003/xmvsfu-68k.bin` (`EXP-0008`): slot 10 bases read from `0x17E19C` and `0x17E1E8` |
| Saturn table | `MC0A.SHP` offset `0x2A4C`, WRAM-L `0x0024FA4C` (`EXP-0025`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `research/experiments/EXP-0022/run_pair.py` | The runs (unchanged) |
| [`make_pairing.py`](make_pairing.py) | The pairing table. Generalized from `EXP-0022`'s: the slot and Saturn address are arguments, and the arcade bases are read from the ROM. |
| `tools/text/caption.py` | The fit check |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair002/r1 \
  en:-:- jp:-:- en:10:3 jp:10:3 en:10:8 jp:10:8 en:10:9
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair002/r2 \
  jp:10:9 en:10:15 jp:10:15 en:10:0 en:10:1 en:10:2 en:10:4
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair002/r3 \
  en:10:5 en:10:6 en:10:7 en:10:10 en:10:11 en:10:12 en:10:13 en:10:14
./invenv.sh python research/experiments/EXP-0026/make_pairing.py \
  data/translations/ken_pairing.json Ken 10 0x0024FA4C \
  local/pair002/r1/summary.json local/pair002/r2/summary.json local/pair002/r3/summary.json
```

The three batches ran in parallel, each in its own output folder.

The fit check decoded each of the 9 English records with
`tools.text.caption.decode_record`, recompiled it with `compile_record`, and
compared the bytes.

## Actual Result

**Control:** draw `0x4D0A` (r = 10), slot 12. English reads `0x189936`
(record 2) and Japanese reads `0x181FF4` (record 10), as in `EXP-0022`.

**Ken's slot, forced draws** (16 English and 4 Japanese runs; every entry
logged D1 = `0x14`):

| r | Japanese record (read) | English record (read) |
| --- | --- | --- |
| 0-7 | — | 0-7 (`0x189166` + 100 r) |
| 3 | 3 (`0x181460`) | 3 (`0x189292`) |
| 8 | 8 (`0x1815DC`) | 0 (`0x189166`) |
| 9 | 9 (`0x181628`) | 1 (`0x1891CA`) |
| 10-14 | — | 2-6 |
| 15 | 15 (`0x1817F0`) | 7 (`0x189422`) |

All 20 reads are at the predicted address.

**On screen** (draw 9, frame 6280, agent-reviewed): the English bubble shows
the decoder's two lines for slot 10 English record 1. The Japanese bubble's
hiragana and punctuation pattern matches Ken's Saturn record 9, which equals
arcade Japanese record 9. The portraits are the route's team, Dhalsim and
Sabretooth, because only the text routine's slot is forced.

**Fit:** all 9 English records decode and recompile to their exact bytes,
with lines of 25 characters or fewer. Records 0-7 have line lengths 25/21,
19/23, 20/20, 22/24, 23/22, 20/8, 20/0 and 22/23. None names Bison, Charlie,
Vega, Gouki, Nash, Akuma or Shadaloo (`docs/names.md`).

**Pairing table:** `data/translations/ken_pairing.json` holds addresses and
record numbers only. All 16 entries are CONFIRMED by a forced English run,
and English record 8 is unreachable.

## Conclusion

**CONFIRMED.** Ken follows the same rule as Ryu. Saturn records `k` and
`k + 8` both pair with English slot 10 record `k` (0-7). English record 8 is
never chosen by the win-quote selector. Ken's English records 0-7 fit the
native English grid (2 × 25) without changes.

## Uncertainty and Alternatives

- **Fixed-index mode:** Ken's fixed index (table `0x04F3E2`) was not read.
  The mode is not reached in arcade play so far (`EXP-0021`, `EXP-0023`).
- **Other selectors:** as for Ryu, the other routines on the dispatcher are
  not traced (`EXP-0022`).
- **Japanese draws:** 4 of 16 were forced. Japanese index = `r` is also the
  Saturn's own rule.

## Reproduction

Run the procedure. Expect the reads above, and 16 CONFIRMED entries from
`make_pairing.py`.
