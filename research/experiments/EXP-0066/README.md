# EXP-0066 (UI): Continue Hints: Census, Storage, Selector and the Arcade's English

Task: HINT-001
Status: DONE
Confidence: CONFIRMED (the Saturn table, starter and every index forced and
shown; the arcade starter, map and every index forced in both languages; the
Saturn's own English path drawing arcade records in the hint box)

## Observation

`EXP-0007` saw a boxed two-line Japanese tip under `CONTINUE?`, different on
two continues. `EXP-0009` saw the US arcade draw English hint records 270 and
271 as two pages there. `EXP-0008` decoded 23 English hint records (area
records 270-292), with no pointer table, and left the grouping and the arrow
codes open. MSHvSF's playbook (a **HYPOTHESIS** here) warns that its Saturn
kept the arcade's English hint map behind a region test, found only by a code
trace.

## Hypothesis

The continue hint is a Saturn quote-renderer record: the renderer's record
pointer `0x060F2490` (`tools.mednafen.route.POINTER`) names it, and its writer
leads to the table and the code that picks the record.

## Controlled Change

None for the census run (input only: the player's vitality set to 0, so the
CPU wins). Then one RAM change per forced run: the Saturn starter's
`and #0x0F,r0` (`0x06066730`, `C90F`) replaced by `mov #i,r0` (`E0ii`); and in
MAME, D0 set to `i` right after the arcade starter's `andi.w #$f, D0`.

## Prediction

The pointer changes once on the continue screen to a record of a fixed-size
table; forcing index `i` shows record `i`.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Saturn image | Untouched source, `references/saturn_jp/README.md` |
| `pre_ko` checkpoint | `local/checkpoints/dbg003/f00009769.mcs` (`EXP-0014`), SHA-256 `911c14d6…b09d` |
| Arcade program | `local/ref003/xmvsfu-68k.bin` (`EXP-0008`), SHA-256 `1b1a5a26…2dd1` |
| Arcade route | `EXP-0009`'s, with its NVRAM and configuration (`local/ref004`) |

## Tools and Environment

- Mednafen 1.32.1 with the agent interface (`290d4717…f9f8`, `EMU-021`).
- MAME 0.289 (Homebrew), headless, `-debug -debugger none`.
- Scripts:
  - [`continue_run.py`](continue_run.py): the loss, the pointer log, writes
    to it, screenshots, and WRAM dumps at the end;
  - [`trace_run.py`](trace_run.py): log-mode PC and write breakpoints over a
    frame window;
  - [`force_hints.py`](force_hints.py): one run per index;
  - [`arcade_hints.py`](arcade_hints.py): adapted from `EXP-0022/run_pair.py`;
  - [`fit_run.py`](fit_run.py): the Saturn's own English path in RAM with
    two arcade English records (below, "Fit");
  - [`hint_pairing.py`](hint_pairing.py): writes
    `data/translations/hint_pairing.json` (addresses and hashes, no text).

## Procedure

```bash
CUE="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
STATE=local/checkpoints/dbg003/f00009769.mcs
./invenv.sh python research/experiments/EXP-0066/continue_run.py "$CUE" "$STATE" local/hint001/run3 2400
./invenv.sh python research/experiments/EXP-0066/trace_run.py "$CUE" "$STATE" local/hint001/trace1 2300 2360 \
  pc:06066728 pc:06066734 pc:060667B8 pc:06066874 pc:060668A2 pc:06066920 pc:06066948 write:060F248C-060F2493
./invenv.sh python research/experiments/EXP-0066/force_hints.py "$CUE" "$STATE" local/hint001/force
./invenv.sh python research/experiments/EXP-0066/arcade_hints.py local/hint001/arcade \
  $(for i in $(seq 0 15); do echo en:$i jp:$i; done)
./invenv.sh python research/experiments/EXP-0066/fit_run.py "$CUE" "$STATE" local/hint001/fit1b 285 286
./invenv.sh python research/experiments/EXP-0066/fit_run.py "$CUE" "$STATE" local/hint001/fit2 274 282
./invenv.sh python research/experiments/EXP-0066/fit_run.py "$CUE" "$STATE" local/hint001/fit3 284 271
./invenv.sh python research/experiments/EXP-0066/hint_pairing.py local/ref003/xmvsfu-68k.bin \
  local/hint001/run3/wram_h.bin local/hint001/arcade/summary.json data/translations/hint_pairing.json
```

The `pre_ko` state is Ryu's winning blow, so the player wins stage 1; the
loss is forced in stage 2 (frames 1,500-3,000 from the load; `run1` zeroed
too early and is recorded only as that).

## Actual Result

### The Saturn

- **The record:** the pointer changes to `0x0608583C` at frame 2,350
  (`run2`, `run3`; the same in both), written by the renderer
  (`0x0606698C`/`0x06066990`). The screen shows the throw-escape hint
  (`run2/shots/r02370.png` `623d0280…`). The record is in decoded
  `MMPACK.PCA` at `0x70C9C` (segment 2, loaded at `0x0601F000`); no other
  disc file holds it.
- **The table:** 21 records of 76 bytes (2 lines × 19 codes) at
  `0x06085544`-`0x06085B80`, preceded on disc by `0x9999` padding (work
  RAM). Rendered with the game font (`records_0.png` `6b9de5ab…`,
  `records_1.png` `64b85922…`):
  - records 0-11: twelve distinct gameplay hints;
  - records 12-15: repeats of records 4, 2, 9 and 3;
  - record 16: an "X-Men vs. Street Fighter, now in development" notice;
  - records 17-20: a list of the 18 roster names and a second Chun-Li, in
    fields of 9-10 cells.
- **The starter** (`trace1`, frame 2,348): `0x06066728` takes the value of
  the routine at `0x06056B54` and masks it, `and #0x0F` (`0x06066730`):
  R0 = `0x0A` at `0x06066734`, the record shown. `0x06066734` then:
  - allocates the text task (`R6` = `0x060F8B80`);
  - if the word `0x060F547A` is nonzero, maps the index through the bytes
    at `0x060667A8` (`00 02 04 … 16 00 02 04 06`);
  - stores the index (task `+38`) and 2 (task `+39`);
  - stores the base, by that word, from the longs at `0x06066798`:
    `0x06085544` (word 0) or `0x06085B80`.
- **The renderer** (`0x06066948`): record = base (task `+52`) + index ×
  76, or × 100 when the word `0x060F5478` is nonzero.
- **No English on the disc:** `0x06085B80` holds a pointer table
  (`0x06086184`, `0x06086190`, …), not text. None of the arcade's English
  hint records 270, 272 or 289 occurs in any disc file, raw or decoded.
- **Every index forced** (`force/i00`-`i15`): each run's pointer is
  `0x06085544 + 76 i` and its screen shows record `i`
  (`force_sheet.png` `1a66a404…`, all 16 hint boxes, checked against the
  rendered table: 12-15 show records 4, 2, 9 and 3's text, as stored).

### The arcade

- **The starter** (`0x04F42A`, MAME's decrypted-opcode disassembly
  `local/pair001/dasm_04f000.txt` from `EXP-0022`):
  - `jsr $1608` (random), `andi.w #$f, D0`, then the task (`jsr $37c0`);
  - if `0xFF547A` is nonzero, D0 = the byte at `0x04F476 + D0`;
  - task `+0x26` = D0, `+0x27` = 2, `+0x4E` = `0x180`;
  - task `+0x34` = the long at `0x04F466 + 2 × 0xFF547A`: `0x0018397C`
    (0) or `0x0018D81A`.

  The Saturn code is this routine, word for word in effect, with
  `0x060F5478`/`0x060F547A` in place of `0xFF5478`/`0xFF547A` (`EXP-0022`'s
  record-size and language words).
- **Every index forced, both languages** (`arcade/summary.json`):
  - English (the US set's word 2): index `i` reads area records
    `270 + m` and `271 + m` (`m` = the map byte) at frames 6,515 and 6,897;
  - Japanese (both words 0 at frame 6,100): index `i` reads record `i` of
    `0x18397C`, one page.
- **On screen** (`arcade_en.png` `aaa7cdb4…`, both pages of every index):
  - indices 0-7 pair with the Saturn's hints 0-7;
  - from index 8 the pairs are out of step with the Japanese, because the
    super-jump hint (index 7) is one record (284) and the map assumes two:
    - index 7 shows 284 and 285 (super jump, then attacking during one);
    - index 8: 286 and 287 (combos in the air, then switching when low);
    - index 9: 288 and 289 (recovery while resting, then the throw input);
    - index 10: 290 and 291 (the throw escape, then the dash input);
    - index 11: 292 and 293 (closing the distance, then "X-MEN VS STREET
      FIGHTER / COMING SOON");
  - indices 12-15 repeat 0-3 in English, but the Saturn's 12-15 repeat
    4, 2, 9 and 3.
- **The two Japanese tables:** the arcade's records 1-16 equal the Saturn's
  byte for byte. Record 0 differs: the arcade's second line starts with
  レバー ("lever"), the Saturn's does not (`rec0_saturn_arcade.png`
  `a41c9b91…`). Records 17-20 (the name list) differ.
- `data/translations/hint_pairing.json`: the arcade map from these runs
  equals the Saturn's bytes at `0x060667A8`.

### Fit

Every English hint record is 2 lines of at most 25 codes (the arcade
format; an arrow is one code). The Saturn's own English path was run in RAM
(`fit1`-`fit3`), with:

- the index forced to 0;
- the English base long `0x0606679C` set to `0x06085544`;
- `0x060F5478` and `0x060F547A` set to 2, the US arcade's values;
- two arcade English records written at `0x06085544`.

The renderer read `0x06085544`, then `0x060855A8` (100 bytes on) at frame
2,730: both pages, in the English mode, inside the hint box. The first runs
were inline; `fit_run.py` repeats them (`fit1b`: both screenshots
byte-identical to `fit1`'s).

- `fit1` (`fit_pages.png` `fa2b96d1…`): records 285 and 286, two lines of
  25 codes; both lines fit the box with room to spare.
- `fit2`, `fit3` (`fit_arrows.png` `85db4334…`): records 274, 282, 284 and
  271. Every arrow draws: `0x0134` ↑, `0x0136` →, `0x0137` ↘, `0x0138` ↓,
  `0x0139` ↙, `0x013A` ←.

## Conclusion

**CONFIRMED.**

- The Saturn's continue hints are records 0-15 of a 76-byte Japanese table
  at `0x06085544` in `MMPACK.PCA` (decoded `0x70C9C` is record 10), chosen
  by the starter at `0x06066728` as `random & 0x0F`.
- The starter is the arcade's (`0x04F42A`) with the same English map and
  two-page task. The Saturn kept the English path but not the English
  records: its English base points at unrelated data.
- The arcade's English for each index is fixed by its map: records
  `270 + map[i]` and `271 + map[i]` (`data/translations/hint_pairing.json`).
- All 24 English records fit the Saturn hint box in its own English mode,
  and every arrow code draws.

## Uncertainty and Alternatives

- The routine at `0x06056B54` is taken to be the random source from its use;
  its distribution is not measured.
- Records 16-20 are not reached by the starter (index ≤ 15). Whether other
  code shows them is not traced; `0x06066B20` holds record 17's address
  (`docs/known_unknowns.md`).
- The fit runs set both region words for the whole run; only the hint was
  inspected.
- `0x0135` (likely ↗) occurs in no hint.

## Reproduction

The commands under "Procedure". Outputs are under the ignored
`local/hint001/`.
