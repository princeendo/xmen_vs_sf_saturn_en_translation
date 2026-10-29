# EXP-0030 (M5): The Pairing for Every Roster Character

Task: PAIR-003
Status: DONE
Confidence: CONFIRMED

## Observation

The arcade win-quote selector (`0x04F396`, `xmvsfu`) draws
`r = rand() & 0x0F`. It shows Japanese record `r`, or English record
`remap[r]` with `remap = [0..7, 0..7]` (`EXP-0022`, D-017). This was confirmed
in MAME for Ryu (slot 9) and Ken (slot 10, `EXP-0026`). The M5 roster is
slots 0-17 (`RE-008`, `data/text/m5_roster.json`). Slot 8 (Apocalypse) has 8
English records, and the others have 9 (`EXP-0029`).

## Hypothesis

The selector and its remap are shared by every slot. So for every roster
slot, a forced draw `r` reads English record `r mod 8` and Japanese record
`r`, from that slot's own pointers. That includes the 8-record slot.

## Controlled Change

Per run, MAME forces only the speaker's slot (D1 = 2 × slot at the
selector's entry) and the draw (the low word of D0 after the random call).
The game's data is never written.

## Prediction

- For all 18 slots and all 16 draws, the English run's first text read is
  the slot's English pointer + 100 × (`r mod 8`).
- For draws 3, 8, 9 and 15, the Japanese run's first read is the slot's
  Japanese pointer + 76 × `r`.
- The unforced controls equal `EXP-0026`'s.
- Ryu's and Ken's English addresses equal their committed pairing files.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Arcade | `xmvsfu` in MAME 0.289, ROMs `local/arcade_roms/xmvsf_mame0289`, `EXP-0009` route with its NVRAM and configuration (`local/ref004`) |
| Program image | `local/ref003/xmvsfu-68k.bin` (`EXP-0008`) |
| Roster and census | `data/text/m5_roster.json`, `data/text/slot_census.json` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`run_pair.py`](run_pair.py) | Copied from `EXP-0022`; the text-read log now starts at `0x17E000` |
| [`make_pairing.py`](make_pairing.py) | Pairing tables for the whole roster, keyed by MC file and offset; writes no file for a slot with a failed run; `--check` compares |
| [`fit_check.py`](fit_check.py) | Recompile, glyph and name checks of every roster English record |

## Procedure

```bash
# one batch per slot, six in parallel (local/pair003b/batch.sh):
#   run_pair.py local/pair003b/s<slot> en:<slot>:0 … en:<slot>:15 jp:<slot>:3 jp:<slot>:8 jp:<slot>:9 jp:<slot>:15
./invenv.sh python research/experiments/EXP-0030/run_pair.py local/pair003b/control en:-:- jp:-:-
seq 0 17 | xargs -P 6 -I{} local/pair003b/batch.sh {}
./invenv.sh python research/experiments/EXP-0030/make_pairing.py local/pair003b data/translations --check
./invenv.sh python research/experiments/EXP-0030/make_pairing.py local/pair003b data/translations
./invenv.sh python research/experiments/EXP-0030/fit_check.py data/translations/m5_english_fit.json
```

## Actual Result

**First batch (`local/pair003`, `EXP-0022`'s `run_pair.py` unchanged).**

- All 288 English runs read the predicted record.
- On slots 0-5, 23 of the 24 Japanese runs logged no read. Their records
  lie at `0x17E3FC`-`0x17FFFF`, below the read log's start (`0x180000`).
  Sabretooth's draw 15 (`0x180030`) was logged and matched.
- The selector's logged steps in those runs still showed the forced slot
  and index `r`. So this was a gap in the logging, not a failure of the
  rule.
- The script was copied with the read log starting at `0x17E000`, and the
  whole set was rerun.

**Rerun (`local/pair003b`), all 360 forced runs:**

| Check | Result |
| --- | --- |
| English, 18 slots × 16 draws | 288/288 read slot pointer + 100 × (`r mod 8`) |
| Japanese, 18 slots × draws 3, 8, 9, 15 | 72/72 read slot pointer + 76 × `r` |
| Selector steps | every run shows D1 = 2 × slot and index `r & 7` (English) or `r` (Japanese) |
| English reads against the first batch | identical, 288/288 |
| Controls | English `0x189936` (slot 12, record 2), Japanese `0x181FF4` (record 10), equal to `EXP-0026` and to the first batch |
| Ryu, Ken | English addresses equal `ryu_pairing.json` and `ken_pairing.json` |

Apocalypse (8 records) behaves like the rest: draw 15 reads English record
7, and no draw reads past his block.

**Pairing files.** These are new for 16 characters, written as
`data/translations/<name>_pairing.json`: Wolverine, Cyclops, Storm,
Rogue, Gambit, Sabretooth, Juggernaut, Magneto, Apocalypse, Chun-Li,
Dhalsim, Zangief, Vega, Gouki, Nash and Cammy.

- Each has 16 CONFIRMED entries, keyed by MC file and decompressed offset.
- Each lists the unreachable English record 8 (none for Apocalypse).
- Ryu's and Ken's files are unchanged. They key the Saturn side by WRAM-L
  address instead.

**Fit** (`data/translations/m5_english_fit.json`, 161 records, 144 shown):

- Every record recompiles exactly. The longest line is 25 codes.
- No shown record uses `@`, `{`, `|` or `}`.
- **Names:** only Cammy's English records 0 and 4 (Saturn records 0, 8, 4
  and 12) name a character whose names differ: "Bison", the US name of the
  Saturn's Vega (`docs/names.md`). No shown record names Akuma, Gouki,
  Charlie, Nash, Vega, Balrog or Sagat. No unshown record names any of
  them.

## Conclusion

**CONFIRMED.** Every M5 roster character follows `r mod 8`. Saturn record
`k` of slot `s` shows slot `s`'s official English record `k mod 8`, and
English record 8 is never shown. All 144 shown English records fit
2 × 25, recompile exactly and draw as the expected glyphs. One name needs
a gate decision: "Bison" in two of Cammy's records.

## Uncertainty and Alternatives

- **Japanese draws:** 4 of 16 per slot were checked in Japanese. The rest
  follow from the same code path and the census's byte-identical tables.
- **One arcade set:** this is the US set only. The English is identical in
  every held set (`EXP-0008`).
- **Saturn side:** the Saturn runs a port of the selector (`EXP-0021`).
  Saturn behaviour for these slots is tested by `RE-010`, not here.

## Reproduction

Run the procedure. Expect 360/360 matching runs, the same controls, and
`make_pairing.py --check` to exit 0. The pairing files and
`m5_english_fit.json` should reproduce byte for byte.
