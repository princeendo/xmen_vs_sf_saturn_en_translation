# EXP-0022: Pair Ryu's Saturn Records With the Arcade English

Task: PAIR-001
Status: DONE
Confidence: CONFIRMED

## Observation

The Saturn copies the arcade's 16 Japanese win quotes for Ryu, slot 9
(`EXP-0015`). The arcade has only 9 English records for that slot
(`EXP-0008`). The Saturn picks a record as `RNG() & 0x0F` (`EXP-0021`). Its
selector also has an unused mode with 100-byte records (the English record
size) and an index remap table `[0..7, 0..7]` at `0x06066718`.

## Hypothesis

The arcade uses the same selector:

- it draws `r = rand() & 0x0F`;
- Japanese shows record `r`;
- English (language word nonzero) shows record `remap[r] = r mod 8`.

So for the same game situation (the same draw), Saturn record `k` pairs with
English record `k mod 8`.

## Controlled Change

In MAME, one state and one route per run (`xmvsfu`, `EXP-0009`'s route,
NVRAM and configuration):

| Variable | How it is set | Where it applies |
| --- | --- | --- |
| Draw `r` | forced into D0 right after the random call (`0x04F3B2`) | the draw |
| Language | English is the set's own value (2); Japanese sets the language word `0xFF547A` and the record-size word `0xFF5478` to 0 at frame 6100 | language |
| Speaker slot | forced to 9 (D1 = 18 at the routine entry `0x04F396`) | the slot |

The control runs the same route with nothing forced, in both languages. No
game data is written; only registers and the two language words are set.

## Prediction

For each run, the first text read (PC `0x04F612`) is at the slot base + size
× index:

- Japanese: index `r`, size 76, slot 9 base `0x180EBC`;
- English: index `r mod 8`, size 100, slot 9 base `0x188DE2`.

The snapshot shows that record.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Emulator and ROMs | MAME 0.289; ROM set `xmvsfu` (`references/arcade/`) |
| Route state | `EXP-0009`'s `local/ref004/nvram` and `cfg`, copied per run |
| Decoded tables | `local/ref003/xmvsfu-68k.bin` (`EXP-0008`) |
| Saturn side | `EXP-0021`; WRAM-H dump `local/font001/s10336/wram_h.bin` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/reference/mame_timeline.lua` | Its `debug` event drives MAME's debugger with `-debug -debugger none -debuglog` |
| `timelines/dasm.txt` | Disassembly of the decrypted opcodes |
| [`run_pair.py`](run_pair.py) | The runs |
| [`make_pairing.py`](make_pairing.py) | The pairing table |
| `timelines/en_r9.txt`, `probe.txt`, `probe2.txt` | The first attempts, kept for the record |

What went wrong in those attempts:

- `en_r9.txt` used a fresh NVRAM, so the route diverged and the selection came at frame 6194, before the slot force.
- `probe.txt` used the wrong language-word address.
- `probe2.txt` found the right address (`0xFF547A`).

## Procedure

```bash
MAME_TIMELINE=research/experiments/EXP-0022/timelines/dasm.txt mame xmvsfu \
  -rompath local/arcade_roms/xmvsf_mame0289 -video none -sound none -nothrottle \
  -skip_gameinfo -nomouse -cfg_directory local/pair001/t/cfg \
  -nvram_directory local/pair001/t/nvram -homepath local/pair001/t \
  -debug -debugger none -autoboot_script tools/reference/mame_timeline.lua
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair001/r1 en:-:- jp:-:-
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair001/r2 en:9:9 jp:9:9 en:9:3 jp:9:3
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair001/r3 en:9:15 jp:9:15 en:9:8 jp:9:8
./invenv.sh python research/experiments/EXP-0022/run_pair.py local/pair001/r4 \
  en:9:0 en:9:1 en:9:2 en:9:4 en:9:5 en:9:6 en:9:7 en:9:10 en:9:11 en:9:12 en:9:13 en:9:14
./invenv.sh python research/experiments/EXP-0022/make_pairing.py data/translations/ryu_pairing.json \
  local/pair001/r2/summary.json local/pair001/r3/summary.json local/pair001/r4/summary.json
```

## Actual Result

**Arcade selector** (MAME's decrypted-opcode disassembly, `0x04F396`):

```text
r = rand() & 0xF            (jsr $1608)
if byte [A5-0x2F7D]: index = fixed[slot]      (word table 0x04F3E2, no remap)
elif word [A5-0x2B86]: index = remap[r]       (byte table 0x04F41A = 0..7, 0..7)
else: index = r
base = tables[lang word][slot]   (0x04F40A: 0x17E19C JP, 0x17E1E8 EN, 0x17E234, 0x17E280)
record = base + index * (100 if word [A5-0x2B88] else 76)   (0x04F56A)
```

- A5 = `0xFF8000`, so the language word is `0xFF547A` and the size word is
  `0xFF5478`. A first run looked for the language word at `0xFFD47A` (my
  arithmetic error) and read 0 there. The debugger showed the real address.
- The raw ROM bytes at these PC-relative tables are encrypted noise, while
  the CPU reads the decrypted values: the run-time base for English slot 12
  is `0x18986E`, as in `EXP-0009`.
- **Same as the Saturn:** the remap and fixed-index tables match the
  Saturn's byte for byte, and the record-pointer offset `0xA490` matches
  (`EXP-0021`). The Saturn code is a port of this routine with the language
  word left at 0 (Japanese).

**Natural draw, both languages** (no forcing, slot 12):

| Language | Draw | Language word | Index | First text read |
| --- | --- | --- | --- | --- |
| English | `0x4D0A` → r = 10 | 2 | 2 | `0x189936`, slot 12 record 2 (as in `EXP-0009`) |
| Japanese | same | 0 | 10 | `0x181FF4`, Japanese slot 12 record 10 |

**Ryu's slot, forced draws** (16 English and 4 Japanese runs):

| r | Japanese record (read) | English record (read) |
| --- | --- | --- |
| 0-7 | — | 0-7 (`0x188DE2` + 100 r) |
| 3 | 3 (`0x180FA0`) | 3 (`0x188F0E`) |
| 8 | 8 (`0x18111C`) | 0 (`0x188DE2`) |
| 9 | 9 (`0x181168`) | 1 (`0x188E46`) |
| 10-14 | — | 2-6 |
| 15 | 15 (`0x181330`) | 7 (`0x18909E`) |

Every read is at the predicted address.

**On screen** (draw 9, agent-reviewed snapshot at frame 6280): English shows
slot 9 record 1. Japanese shows いいライバルに なれそうだ！, which is
Japanese record 9 and Saturn record 9.

**Pairing table:** `data/translations/ryu_pairing.json`. Saturn record `k`
pairs with English record `k mod 8`, and all 16 entries are CONFIRMED by a
forced English run.

## Conclusion

**CONFIRMED.** For the same random draw, the arcade shows Japanese record `r`
and English record `r mod 8`:

- Saturn records `k` and `k + 8` both pair with English record `k` (0-7).
- Ryu's English record 8 is never chosen by the win-quote selector.
- In the fixed-index mode, Ryu's index is 1 in both languages.

This is the game's own selection logic, as the policy requires.

## Uncertainty and Alternatives

- **Other selectors:** other routines on this dispatcher choose records by
  other rules (`0x04F42A` hints, `0x04F486` a table-driven index, `0x04F4FA`
  and `0x04F518` endings). Whether any of them shows Ryu's English record 8,
  or another slot-9 record, is not traced.
- **Fixed-index mode:** what sets the byte at `0xFF5083`, and when, is not
  traced.
- **Japanese draws:** Japanese was forced for 4 draws only. Japanese index =
  `r` is the identity the Saturn already uses (`EXP-0021`).
- **The other two tables:** `0x17E234` and `0x17E280` (language words 4 and
  6) were not displayed. They may be the Spanish and Portuguese tables
  (`EXP-0008`).

## Reproduction

Run the procedure. Expect:

- the reads above;
- 16 CONFIRMED entries from `make_pairing.py`.
