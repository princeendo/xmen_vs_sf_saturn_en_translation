# EXP-0058 (Special): Census of the Special Cases

Task: SPEC-001
Status: DONE
Confidence: CONFIRMED unless marked

## Observation

- `EXP-0034`, `EXP-0048`: Japanese boxes on the boss stage name the player's
  character in katakana; a story-like quote before the boss stage.
- `docs/known_unknowns.md`: slot 18's character unknown; Gouki's cell open
  in this project's saves; how the boss stage's text is stored unknown.

## Sources and Tools

| Source or tool | What |
| --- | --- |
| `local/loc005/endings/s<slot>_a<n>/` (`EXP-0051`) | 17 route runs (American build): a screenshot every 120 frames, every change of the quote pointer `0x060F2490` |
| `local/end001/session/` (`EXP-0034`) | The user's Nash session, untouched image |
| `local/checkpoints/end015/f00137457.mcs` | Ryu against Apocalypse (M8 build), dumped with `EXP-0049/dump_screen.py` |
| `research/experiments/EXP-0051/cold_walk.py` | Cold boots of the untouched image: walks to the boss stage (`walk2`), a fresh save (`gouki_fresh`), a Start-held pick (`alpha_chun`); it gained `chord:` and `peek:` steps |
| [`render_records.py`](render_records.py) | 76-byte Japanese records drawn with the quote font, for the agent to read |
| `research/experiments/EXP-0049/patch_run.py`, `write_log.py` | The controlled change and the flag log |
| A subagent, MAME 0.289 `xmvsfu` only | The arcade side, evidence in `local/spec001/arcade/` (below) |

```bash
U="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue"
STAGE="wait:600 ko:900 wait:900"
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$U" local/spec001/walk2 \
  wait:1800 await:local/loc005/title_ref.png:6000 wait:150 press:s:local/loc005/select_ref.png:15 \
  wait:60 keys:r wait:60 keys:a wait:120 keys:a wait:120 keys:a wait:150 \
  $STAGE $STAGE $STAGE $STAGE $STAGE wait:600 ko:900 wait:300 \
  save:p0 wait:100 save:p1 ... save:p9 wait:600
./invenv.sh python research/experiments/EXP-0049/patch_run.py "$U" local/spec001/box_swap \
  local/spec001/walk2/p0.mcs 200 060C2894:<record 0>:<record 2>
./invenv.sh python research/experiments/EXP-0049/write_log.py "$U" local/spec001/flag_log \
  local/spec001/walk2/p9.mcs 060F5080:060F5083 1800 write 060F4610:0090:0000
./invenv.sh python research/experiments/EXP-0051/cold_walk.py "$U" local/spec001/alpha_chun \
  wait:1800 await:local/loc005/title_ref.png:6000 wait:150 press:s:local/loc005/select_ref.png:15 \
  wait:60 keys:uur wait:30 shot:hover chord:sa wait:60 shot:picked peek:060F4052:2 peek:060F4852:2 \
  keys:a wait:120 keys:a wait:150 shot:vs wait:500 shot:fight peek:060F4052:2
COLD_WALK_HOME=$PWD/local/spec001/home_fresh ./invenv.sh python research/experiments/EXP-0051/cold_walk.py \
  "$U" local/spec001/gouki_fresh wait:1800 await:local/loc005/title_ref.png:6000 wait:150 \
  press:s:local/loc005/select_ref.png:15 wait:60 shot:select0 keys:u wait:30 ... keys:u wait:30 shot:u4
```

`home_fresh` is the silent home with the key map, the 4 MB cart and a
formatted backup memory holding no save of this game (`backup_ram free509`).
A first walk (`walk1_derailed`) picked the wrong character after a stray
keystroke; a second (`walk1`) saved its states too late (inside the boss
fight). Both are kept and not used as evidence.

## Actual Result

### The boss stage's boxes

- **Three per player character**, shown at the top of the screen before
  Apocalypse transforms. Ryu (slot 9), read with the quote font: record 0 is
  his line to Apocalypse, record 1 Apocalypse's answer naming him
  (迷える戦士リュウよ…), record 2 Apocalypse's "behold my true form"
  (`walk2`, frames 18,940-19,240).
- **Storage:** a table of 18 slots × 3 records × 76 bytes in decoded
  `MC08.SHP` (Apocalypse's file) from `0x1090`; during the boss stage the
  file is at WRAM-H `0x060C1000`, so slot s starts at `0x060C2090` +
  `0xE4` × s. The route runs' quote pointer stepped through exactly these
  records for all 17 slots.
- **Controlled change:** from `p0` (frame 18,780, just before the boxes),
  Ryu's record 0 replaced by his record 2 in RAM (checked first): the first
  box showed "behold my true form" (`patched.png` `14287752…`); the
  control showed his own line (`control.png` `ad97ae53…`).
- **Variety:** records 0 and 1 differ per slot (slots 7 and 8 share record
  1); record 2 has two versions, for {0, 1, 2, 7, 8, 9, 10, 11, 14, 16}
  and {3, 4, 5, 6, 12, 13, 15, 17}. There is no slot 18 row (zeros).
- **Index table:** decoded `MMPACK.PCA` `0x51CAC` (WRAM-H `0x0606684C`)
  holds the arcade's start-record table, 3 × slot for slots 0-17 and 33 (=
  Chun-Li's) for slots 18 and 19, followed by its second copy.

### The quotes before and after the boss

- **Before (the sixth win):** a random draw. Ryu showed Japanese record 13
  in `walk1` and record 12 in `walk2`; Nash's story-like record 9 in the
  `END-001` session was a draw too.
- **After (the seventh win, Apocalypse):** the fixed record. At the knock-out
  `0x0604EBDA` writes the win count 7 to `0x060F5081` and `0x0604EC0C` sets
  `0x060F5083` to `FF` (`flag_log`); the selector then takes the fixed-index
  path (`0x06066652`: the byte at R11 + `0xD083`).
- **Fixed table** (`0x060666E0`, low bytes): `05 02 03 00 07 01 00 01 00 01
  07 05 04 00 07 00 00 06 05` for slots 0-18.

### Characters

| Slot | Character | How it is chosen (Saturn) | Evidence |
| --- | --- | --- | --- |
| 15 | Gouki | His cell above Juggernaut's, open with a fresh save (no unlock) | `gouki_fresh/shots/u4.png` `1ea0308d…` |
| 18 | Chun-Li in her Alpha costume | Chun-Li picked with Start held: her character word `0x060F4052` reads `0x0024` (slot 18) after the pick and in the fight; she fights in the blue Alpha outfit | `alpha_chun`, `fight.png` `539277b0…` |
| 8 | Apocalypse | The boss only; not selectable | `EXP-0045`, `EXP-0047` |

Slot 18 shares Chun-Li's quote and ending pointers and scripts (`EXP-0029`,
`EXP-0043`), and Chun-Li's boss boxes through the index table. **But its
fixed-table entry is `0x0005`**, with no English flag in the high byte (the
builds mark slots 0-17 only), so in the English builds Alpha Chun-Li's win
quotes are most likely still Japanese (HYPOTHESIS, for `SPEC-002`).

### The arcade side (subagent, MAME `xmvsfu`, `local/spec001/arcade/`)

- **Slot 18** is Chun-Li's Alpha costume there too: confirm code
  `0x00B1D4`/`0x00B30E` turns ID `0x16` into `0x24` when that player's Start
  is held (runs `r11`, `r11_start`, `r18_force`). CONFIRMED.
- **Apocalypse's boxes have no English:** his intro (`0x031798`) tests the
  language word and skips the box object and the box text (`0x04F486`)
  whenever it is not 0. With language 2 no box showed (`r16_en`); with 0,
  three Japanese boxes showed from the Japanese table `0x185D6A` (18 × 3 ×
  76 bytes, `r16_jp`). The English branch's base is a placeholder (the win
  quotes' pointer table). CONFIRMED.
- **Fixed-index flag:** set by the seventh win (`0x00F5A8`-`0x00F5D4`), as on
  the Saturn; table `0x04F3E2` = `5,2,3,0,7,1,0,1,0,1,7,5,4,0,7,0,0,6,5,0`, the
  Saturn's values. In fixed mode the arcade's English index is used directly.
  CONFIRMED.
- **Note:** `local/ref003/xmvsfu-68k.bin` holds the encrypted opcodes; the
  subagent dumped MAME's `:decrypted_opcodes` share
  (`local/spec001/arcade/dasm/`) for code. Data reads from that image remain
  valid.

### Other surfaces from the boss stage to the credits

- Stage card "APOCALYPSE NOW!", the VS screen and the boss fight: no other
  text.
- The partner fight's `⚠乱入禁止` sprite: `NOCH-001`.
- The win quote after the partner fight: an ordinary quote (English since
  M5).
- Slot 8's ending: never reached (HYPOTHESIS, `docs/coverage_exceptions.md`).

## Conclusion

**CONFIRMED:**

- The special text on the boss stage is three boxes per player character,
  stored in `MC08.SHP` (18 slots × 3 records), shown by controlled change.
- The quote after Apocalypse is the fixed record; the one before is random.
  The Saturn's fixed table equals the arcade's.
- Slot 18 is Alpha Chun-Li (Start held over Chun-Li), on the Saturn and in
  the arcade; she uses Chun-Li's boxes.
- Gouki needs no unlock on the Saturn.
- The US arcade shows none of the boxes and has no English for them.

**DISPROVEN:** "the pre-boss quote is a fixed story line" (it is a random
draw); "Gouki is save-gated on the Saturn".

## Uncertainty and Alternatives

- **Alpha Chun-Li's quotes in the English builds:** most likely Japanese
  (her fixed-table entry has no English flag); to be shown in `SPEC-002`.
- **Slot 8's ending**, **the arcade's 4 records after its box table** and
  **its second index table**: unknown use.
