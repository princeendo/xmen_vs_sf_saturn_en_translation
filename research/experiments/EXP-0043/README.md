# EXP-0043 (M8): Census of Every Roster Ending's Scripts and Space

Task: END-010
Status: DONE
Confidence: CONFIRMED (static facts); the script-to-screen links for slots
other than 16 are SUPPORTED until `END-012` and `END-015` show them

## Observation

M7 proved one ending (Nash, D-029 to D-037). M8 needs, for every roster
slot:

- the `MCED` scripts;
- what the shared scripts and arcade pointer aliases mean;
- the labels;
- whether the English records fit.

## Hypothesis

Every roster slot 0-17 has an English script in `MCED.SHP` that shows the
slot's arcade English ending records 0 to n − 1, once each, in order (as
Nash's does). Every MC file can hold its English ending after its English
win quotes, both in free space and compressed.

## Method

Static only. `census_scripts.py` reads:

- decoded `MCED.SHP` and the MC files from the untouched track;
- the roster build's MC files (`local/re010/b1`, English win quotes);
- the arcade program image.

The script format is `EXP-0038`'s, now read in full:

| Level | Layout |
| --- | --- |
| Slot table | `MCED` `0x26C4`, 19 longs; value + `0x40` = script offset |
| Script header | 4 words, offsets for language 0, 2, 4, 6 |
| Language script | scene-offset table (first entry / 2 = scenes) |
| Scene | (page length, record × 256 + label) word pairs, then `FFFF`, then a trailing word |

The labels are resolved in `MCED`'s 40-entry list (`0x3DA8`).

**Space:**

- free bytes after the English win quotes: 416 + 76 × the Saturn Japanese
  count;
- compressed fit: the roster build's MC file with the arcade English
  ending written at table + 800, lazily re-encoded.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0043/census_scripts.py data/text/ending_script_census.json
```

## Actual Result

Output: `data/text/ending_script_census.json`. Records per scene; a label
column lists the label names the English script uses:

| Slot | Name | Japanese scenes | English scenes | EN in order | JP in order | English labels |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Wolverine | 0-1, 2-6 | 0-2, 3-5 | yes | yes | Wolverine, Jubilee |
| 1 | Cyclops | 0-2, 3-4, 5-6 | 0-2, 3-5, 6-8 | yes | yes | Cyclops, Ryu |
| 2 | Storm | 0-1, 2, 3-6 | 0-2, 3, 4-5 | yes | yes | — |
| 3 | Rogue | 0-2, 3-7 | 0-2, 3-5 | yes | yes | Rogue, Chun-Li, **Bison** |
| 4 | Gambit | 0-3, 4-5 | 0-1, 2-4 | yes | yes | Gambit |
| 5 | Sabretooth | 0-1, 2-3 | 0-2, 3-5 | yes | yes | Wolverine, Sabretooth, Birdie |
| 6 | Juggernaut | 0-3, 4-8 | 0-2, 3-5 | yes | yes | Juggernaut |
| 7 | Magneto | 0, 1, 2-3 | 0-1, 2-3, 4-6 | yes | yes | Magneto, **Vega** |
| 8 | Apocalypse | (Ryu's script) | (Ryu's script) | yes | **no** | Cyclops, Ryu |
| 9 | Ryu | 0-2, 3-4, 5 | 0-1, 2-3, 4-6 | yes | yes | Cyclops, Ryu |
| 10 | Ken | 0-1, 2-4 | 0-2, 3 | yes | yes | Ken, Eliza, His son |
| 11 | Chun-Li | 0-1, 2-6 | 0-2, 3-5 | yes | yes | Professor X, Iceman, Beast, Archangel |
| 12 | Dhalsim | 0, 1, 2-3 | 0-1, 2, 3-5 | yes | yes | Dhalsim, Wife |
| 13 | Zangief | 0, 1-3 | 0-2, 3-4 | yes | yes | Zangief, Colossus |
| 14 | Vega | 0, 1-3 | 0-2, 3-4 | yes | yes | — |
| 15 | Gouki | 0-2, 3 | 0-4, 5 | yes | yes | Wolverine, **Akuma** |
| 16 | Nash | 0-1, 2-3, 4, 5 | 0, 1-2, 3, 4-5 | yes | yes | **Charlie**, **Charlie's friend** |
| 17 | Cammy | 7 scenes, 0-11 | 7 scenes, 0-12 | yes | yes | Cammy, Matsuo Tsurayaba, Psylocke |
| 18 | (name list: Bison) | (Chun-Li's script) | (Chun-Li's script) | — | — | as Chun-Li |

- **Header:** in every slot, the English header word is the same for
  languages 2, 4 and 6.
- **Trailing word:** in every Japanese script, each scene's trailing word
  repeats its last page word. In six English scripts (slots 2, 7, 12, 14,
  15, 16) some do not. Nash's ending (16) plays correctly anyway, so the
  trailing word's meaning is unknown and not needed.

### Shared scripts and aliases

- **Slots 8 and 9 → Ryu's ending.**
  - The shared script's labels are Cyclops and Ryu. Its English records
    are 0-6, Ryu's English count, and its Japanese records 0-5, Ryu's
    Saturn count.
  - The arcade English pointer for slot 8 equals slot 9's (`0x18C172`).
  - So Apocalypse's "ending" entries all lead to Ryu's.
  - Apocalypse's own file `MC08` holds 4 Japanese records equal to
    Magneto's block. That is the arcade Japanese alias 8 = 7. Apocalypse's
    script (Ryu's) would read 6 of them, so slot 8's Japanese script does
    not match his file.
  - Apocalypse is the boss and not selectable. That he never gets an ending
    in play is a HYPOTHESIS.
- **Slots 11 and 18 → Chun-Li's ending.** They share the script, and the
  arcade English and Japanese pointers. The name list calls entry 19
  (slot 18) "Bison". Which character, if any, uses slot 18 is still
  `SPECIAL-001`.

### Names for the gate (labels)

- **Akuma:** Gouki's English script labels `Akuma` (Japanese: `Gouki`).
- **Charlie:** Nash's labels `Charlie` and `Charlie's friend` (already in
  the M7 gate).
- **Bison:** Rogue's English script labels `Bison` (Japanese: `Vega`).
- **Vega in an English script:** Magneto's English script labels `Vega`,
  which is unusual. Whether the arcade English shows `Vega` there is for
  `END-012`.

### Space (bytes)

| Slot | English | Free after win quotes | Compressed margin |
| --- | --- | --- | --- |
| 0 | 600 | 948 | 808 |
| 1 | 900 | 948 | 633 |
| 2 | 600 | 948 | 782 |
| 3 | 600 | 1,024 | 862 |
| 4 | 500 | 872 | 726 |
| 5 | 600 | 720 | 716 |
| 6 | 600 | 1,100 | 637 |
| 7 | 700 | 720 | 914 |
| 8 | 700 | 720 | 259 |
| 9 | 700 | 872 | 606 |
| 10 | 400 | 796 | 607 |
| 11 | 600 | 948 | 1,293 |
| 12 | 600 | 720 | 631 |
| 13 | 500 | 720 | 784 |
| 14 | 500 | 720 | 494 |
| 15 | 600 | 720 | 561 |
| 16 | 600 | 872 | 814 (equals the M7 build) |
| 17 | 1,300 | 1,328 | 659 |

Every roster file fits, both in free space and compressed.

## Conclusion

**CONFIRMED (static):**

- every roster slot 0-17 has an English script showing its arcade English
  records 0 to n − 1 in order;
- every MC file can hold its English ending after its English win quotes
  (the smallest compressed margin is 259 bytes, Apocalypse);
- the 8/9 and 11/18 sharing is explained: Apocalypse leads to Ryu's
  ending, and slot 18 to Chun-Li's.

The version-4 method (`EXP-0040`) therefore applies to every ordinary
roster ending without new code. Each needs:

- its slot bit;
- its English records at table + 800;
- its `MCED` header switch.

`mced_english_scripts` refuses slot 9 alone (shared with 8), so marking
Ryu needs a decision for slot 8 too (`END-011`).

## Uncertainty and Alternatives

- **Static only:** the scripts' pictures and screens for slots other than
  16 are untested. `END-012` gives the arcade screens and `END-015` the
  Saturn ones.
- **The trailing word** is not understood.
- **Gouki's and Cammy's endings:** whether they are reachable in normal
  play (Gouki's unlock) is not part of this census.
