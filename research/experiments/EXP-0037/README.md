# EXP-0037 (M6): Arcade English and Indexing for Nash's Ending

Task: END-004
Status: DONE
Confidence: CONFIRMED (predictions 1-3); prediction 4 refuted

## Observation

- **Saturn** (`EXP-0035`, `EXP-0036`): Nash's ending shows six pages, read
  in order from decoded `MC10.SHP` records 16-21. Those are the arcade's
  Japanese ending block for slot 16, records 0-5 (`EXP-0029` census,
  `data/text/ending_census.json`).
- **Arcade:** its English ending block for slot 16 also has 6 records
  (table `0x17E318`, 100-byte records).
- **Unknown:** no arcade ending has been reached, and how the arcade picks
  ending records is unknown.

## Route (found before the predictions)

`timelines/discover1.txt` and `timelines/discover2.txt`, run by
`run_mame.py`:

- **Pick:** Charlie is picked first on `xmvsfu` by Up, Right, Right from the
  start cell (Cyclops), then button 1. The partner is whatever button 1
  picks next; in `discover1` that was Cyclops.
- **Vitality:** the four fighters use 0x400-byte blocks from `0xFF4200`,
  with vitality at +`0x10` (144 at full). It was found from work-RAM dumps
  of an idle fight (`discover1`). Only `0xFF5042`, `0xFF4210` and
  `0xFF4A10` changed as the player's side was hit; `0xFF4610` and
  `0xFF4E10` stayed at 144.
- **No-play route** (`discover2`): `w@ff4610=0` and `w@ff4e10=0` every 20
  frames from frame 3750. Charlie and Cyclops won every stage, Apocalypse
  and a final Charlie-against-Cyclops fight. Charlie's ending followed, in
  English, then the staff roll and `GAME OVER`. (Snapshots every 300
  frames, reviewed by the agent.)

So one combination (partner Cyclops, English) was seen on screen before
these predictions were written. No record read was logged in that run.

## Predictions (registered before the logged runs)

Written and committed before any run that logs reads.

1. **Records follow the point character.** With Charlie first, the ending
   reads slot 16's English ending records 0, 1, 2, 3, 4, 5 in that order,
   one per page, from the slot-16 English pointer at table `0x17E318`. This
   holds with partner **Cyclops** (slot 1) and with partner **Ryu** (slot
   9), with the same six records each time. The partner changes no record.
2. **Japanese:** with the language and size words set to 0 (the `EXP-0022`
   method), the same pages read slot 16's Japanese ending records 0-5 in
   order (table `0x17E2CC`). These are the records the Saturn shows from
   `MC10` records 16-21.
3. **Pairing:** therefore Saturn `MC10` record 16 + k pairs with arcade
   English slot 16 record k, for k = 0-5.
4. **Labels:** the arcade English pages show no speaker label from the text
   tables. If a label appears, it is drawn from somewhere other than the
   ending records. This one is a weak prediction: the `EXP-0035` English
   mode on the Saturn showed a `Charlie` label.

**What would refute them:**

- a different record set or order between the two partners;
- reads outside slot 16's blocks;
- more or fewer than six reads;
- a Japanese run reading other records.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Arcade set | `xmvsfu` (USA 961023), `local/arcade_roms/xmvsf_mame0289` (`REF-001`) |
| Emulator | MAME 0.289 (Homebrew), headless, `-debug -debugger none` |
| NVRAM and configuration | copies of `local/ref004` (`EXP-0009`) |
| Program image | `local/ref003/xmvsfu-68k.bin` `1b1a5a26…` (addresses and decoding) |
| Saturn file | `MC10.SHP;1` from the untouched source track (`07bbfb41…`) |

## Tools

| Tool | Use |
| --- | --- |
| [`run_mame.py`](run_mame.py) | One timeline, headless; `{run}` in the timeline becomes the run folder |
| [`make_timeline.py`](make_timeline.py) | The no-play route for a partner and a language; read logs; snapshots |
| [`make_pairing.py`](make_pairing.py) | `data/translations/nash_ending_pairing.json` from the four read logs |
| `tools/reference/mame_timeline.lua` | `logreads`, `debug do`, `snap`, inputs |

## Procedure

```bash
T=research/experiments/EXP-0037/timelines
./invenv.sh python research/experiments/EXP-0037/run_mame.py local/end004/d1 $T/discover1.txt
./invenv.sh python research/experiments/EXP-0037/run_mame.py local/end004/d2 $T/discover2.txt
./invenv.sh python research/experiments/EXP-0037/make_timeline.py $T/en_cyclops.txt cyclops en
./invenv.sh python research/experiments/EXP-0037/make_timeline.py $T/en_ryu.txt ryu en
./invenv.sh python research/experiments/EXP-0037/make_timeline.py $T/jp_cyclops.txt cyclops jp 14900
./invenv.sh python research/experiments/EXP-0037/make_timeline.py $T/jp_ryu.txt ryu jp 14800
for r in en_cyclops en_ryu jp_cyclops jp_ryu; do
  ./invenv.sh python research/experiments/EXP-0037/run_mame.py local/end004/final/$r $T/$r.txt
done
./invenv.sh python research/experiments/EXP-0037/make_pairing.py local/end004/final \
  data/translations/nash_ending_pairing.json
```

Each run takes about 35 s.

## Actual Result

### A failed partner pick (recorded, then fixed)

- **The fault:** the first "Ryu" run (`local/end004/en_ryu`) pressed Right at
  frame 1860, before the second cursor was active. It picked Cyclops again,
  and its post-boss and partner-fight snapshots show Cyclops. Its reads
  equalled the Cyclops run's, but that compared Cyclops with Cyclops.
- **The fix:** Right at frame 1900, then button 1 from 1940. The select
  snapshot at frame 2000 shows Ryu picked, and the partner fight is Charlie
  against Ryu (`f14400` `85cf1d44…`).
- **The final runs:** all four timelines were regenerated with the fixed
  script and rerun (`local/end004/final`). Their Cyclops-run page
  snapshots are byte-identical to the first Cyclops runs'.

### Reads (`reads.txt`, from frame 12,000)

The table reads are by PC `0x04F53C`; the record reads are by PC `0x04F612`.

| Run | Ending table read | Records read, one per page | Pages where the table is re-read |
| --- | --- | --- | --- |
| en_cyclops | `0x17E358` (English table + 4 × 16) | `0x18D0AE` + 100k, k = 0-5 (frames 15,048-16,982) | 1, 2, 4, 5 |
| en_ryu | `0x17E358` | the same six (frames 14,934-16,868) | 1, 2, 4, 5 |
| jp_cyclops | `0x17E30C` (Japanese table + 4 × 16) | `0x1856E0` + 76k, k = 0-5 (frames 15,048-16,407) | 1, 3, 5, 6 |
| jp_ryu | `0x17E30C` | the same six (frames 14,934-16,293) | 1, 3, 5, 6 |

- **Pointers:** `0x18D0AE` and `0x1856E0` are slot 16's English and
  Japanese ending pointers.
- **The language word** `0xFF547A` is read at each page by PCs
  `0x04F530`-`0x04F5F2` and `0x06F904`. In the Japanese runs it was 0 from
  frame 14,900 (Cyclops) or 14,800 (Ryu), before the first page.
- **The win quote after Apocalypse:** in all four runs, the win selector
  (`0x04F3DA`, table `0x17E228`) read slot 16's English win-quote record 0
  (`0x18A67E`) at frame 13,789 or 13,675. The Japanese words were set only
  later.

### Screens (agent-reviewed snapshots)

| Page | Arcade Japanese: picture, label | Arcade English: picture, label | Lines (JP / EN) |
| --- | --- | --- | --- |
| 1 | black, none | black, none | 1 / 1 |
| 2 | black, none | Charlie captive, none | 2 / 2 |
| 3 | captive, `Nash` | captive, none | 1 / 2 |
| 4 | captive, `Nazo no koe` | black, `Charlie` | 2 / 1 |
| 5 | black, `Nash` | Guile, `Charlie's friend` | 1 / 2 |
| 6 | Guile, `Nash's friend` | Guile, none | 2 / 2 |

- **Arcade Japanese = Saturn:** the arcade Japanese pages match the
  Saturn's (`EXP-0034`) in text, pictures and labels.
- **Snapshots:**

  | Page | Japanese (`jp_cyclops`) | English (`en_cyclops`) |
  | --- | --- | --- |
  | 1 | `f15150` `8d3a7da1…` | `f15150` `02aaf741…` |
  | 2 | `f15390` `345a686b…` | `f15540` `7d17de1f…` |
  | 3 | `f15660` `08bfce3e…` | `f15900` `99eb4d2e…` |
  | 4 | `f15900` `c3f63313…` | `f16320` `3b0a0b9c…` |
  | 5 | `f16200` `bf4100ae…` | `f16710` `8f099586…` |
  | 6 | `f16500` `1513c56f…` | `f17100` `f49c82ad…` |

- **English text on screen** (2 × 25 grid): it matches the records read.
  No speaker label comes from the text area: no read in `0x17E000`-`0x18E179`
  happens besides the records.
- **Around the ending** (English):
  - the post-Apocalypse win-quote screen shows that record 0 (`f13860`
    `8c5e001d…`);
  - `NO CHALLENGERS` is shown at the top right where the Saturn shows
    `⚠乱入禁止`.

### Pairing (`data/translations/nash_ending_pairing.json`)

| Page | Saturn | Arcade Japanese | Arcade English | Reads matched | Confidence | Names that differ |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `MC10` rec 16 (`0x2EC0`) | rec 0 `0x1856E0` | rec 0 `0x18D0AE` | 4/4 | CONFIRMED | — |
| 2 | rec 17 (`0x2F0C`) | rec 1 `0x18572C` | rec 1 `0x18D112` | 4/4 | CONFIRMED | Charlie |
| 3 | rec 18 (`0x2F58`) | rec 2 `0x185778` | rec 2 `0x18D176` | 4/4 | CONFIRMED | — |
| 4 | rec 19 (`0x2FA4`) | rec 3 `0x1857C4` | rec 3 `0x18D1DA` | 4/4 | CONFIRMED | — |
| 5 | rec 20 (`0x2FF0`) | rec 4 `0x185810` | rec 4 `0x18D23E` | 4/4 | CONFIRMED | Charlie |
| 6 | rec 21 (`0x303C`) | rec 5 `0x18585C` | rec 5 `0x18D2A2` | 4/4 | CONFIRMED | — |

- **Bytes:** every Saturn record equals its arcade Japanese record byte for
  byte.
- **Names:** English record 1 also says "Shadaloo". `docs/names.md` does
  not list that as a name that differs between conventions. The labels `Charlie` and `Charlie's friend`
  also use the American name.

## Conclusion

**CONFIRMED:**

1. **Route:** Charlie's arcade ending is reached with no play, by zeroing
   the CPU side's vitality (`0xFF4610`, `0xFF4E10`) every 20 frames, in
   English and, with `0xFF547A`/`0xFF5478` = 0, in Japanese.
2. **Indexing:** page k reads the point character's ending record k, in
   either language. Two partners (Cyclops, Ryu) give the same records in
   both languages; the partner changes nothing. (Predictions 1 and 2 met.)
3. **Pairing:** Saturn `MC10` record 16 + k ↔ arcade English slot 16 record
   k, k = 0-5, each confirmed by four MAME reads (prediction 3).

**Refuted (prediction 4):** the arcade English pages do show speaker
labels, `Charlie` and `Charlie's friend`. They are not read from the text
area.

**Most important for M7:** the scene script depends on the language. The
same six records are shown, but the English script changes:

- which pages start a scene (1, 2, 4, 5 against 1, 3, 5, 6);
- each page's picture;
- the labels: no label is used for the voice; `Charlie` goes on the
  scream, `Charlie's friend` on the dog-tag line.

So English records dropped into the Japanese script would show, for
example, the scream under `Nazo no koe` with the captive picture. The
Saturn's English-mode trial (`EXP-0035`) already showed the `Charlie`
label and a picture change, so the Saturn has an English script of its own.
Whether it matches the arcade's is for M7.

## Uncertainty and Alternatives

- **One character, two partners:** whether every slot follows the same
  rule is for M8.
- **The vitality route** skips every fight's normal play. Endings that
  depend on how a fight was won (if any) would not show.
- **The label source** in the arcade is not traced (the name list at
  `0x503E4` holds speaker labels, `EXP-0011`; HYPOTHESIS).
- **Post-Apocalypse win quote:** the arcade read record 0 of Charlie's
  quotes. Whether the Saturn shows its record 0 there, and through which
  path, is untested (`SPECIAL-001`).
