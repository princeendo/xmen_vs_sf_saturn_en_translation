# EXP-0050 (Names): Name Calls in Voice

Task: LOC-003
Status: DONE
Confidence:

- CONFIRMED: the bank, the decoder, the call table (controlled change),
  and the clips the user identified;
- SUPPORTED: the Gouki and Nash calls (played on the call channel at their
  picks; not heard in isolation);
- UNKNOWN: the second table's role, and the VS-screen clip.

## Observation

- **`EXP-0048`:** the user heard "Vega", "Gouki" and "Nash" in play, at
  moments not recorded.
- **MSHvSF** (`docs/playbook_from_mshvsf.md`; MSHvSF `docs/discoveries.md`
  LOC-005) found ADPCM clip banks, a software mixer on the SH-2, and a
  name-call table in sound RAM with US calls after the roster. None of
  that was assumed here (rule 13).

## Questions

- When is a name spoken?
- Which clip is it, where is the clip stored, and what picks it?
- Are "Bison", "Akuma" and "Charlie" calls on the disc?

## Tools

| Tool | Use |
| --- | --- |
| [`voice_record.py`](voice_record.py) | Mednafen's `-soundrecord` WAV of scripted steps from a state, with the WAV length logged at each step |
| [`sound_dump.py`](sound_dump.py) | Sound RAM, WRAM-L/H and a save state after scripted steps |
| [`channel_poll.py`](channel_poll.py) | Real-time polling of the mixer's 16 channel records around a key press, with optional checked RAM patches; logs every clip that starts |
| [`sound_bank.py`](sound_bank.py) | The bank in sound RAM; `check` (decoder against live channel state); `export` (WAV). The decoder is copied from MSHvSF `tools/audio/sound_bank.py` at `6161166` |
| `research/experiments/EXP-0049/write_log.py` | Breakpoint logs (SCU, sound chip, channel records) |

## Procedure

```bash
B="build/m8_roster_endings/X-Men vs. Street Fighter (Japan) (3M).cue"
S=local/checkpoints/re004/f00002973.mcs          # route select state
./invenv.sh python research/experiments/EXP-0050/voice_record.py "$B" local/loc003/r1 $S \
  shot:start wait:60 keys:uuu wait:120 shot:hover_vega keys:a wait:180 shot:picked_vega keys:a wait:600 shot:after
ffmpeg -i local/loc003/r1/sound.wav -ss 9.4 -to 11.0 local/loc003/clips/clip1_vega_pick.wav
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll1 $S uuu a 4
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_gouki $S uuullu a 4
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_nash $S u a 4
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_patchA $S uuu a 4 0601BA96:0121:0147
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_patchB $S uuu a 4 0601BB92:0121:0147
W=local/loc001/session/states
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_win $W/f00029551.mcs "" "" 9 060F4610:0019:0000
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_winA $W/f00029551.mcs "" "" 9 060F4610:0019:0000 0601BAAE:0149:0147
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_winB $W/f00029551.mcs "" "" 9 060F4610:0019:0000 0601BBAA:0149:0147
./invenv.sh python research/experiments/EXP-0050/channel_poll.py "$B" local/loc003/poll_vs $W/f00030578.mcs "" "" 9
./invenv.sh python research/experiments/EXP-0050/sound_bank.py check local/loc003/poll1
./invenv.sh python research/experiments/EXP-0050/sound_bank.py export local/loc003/poll1 local/loc003/bank3 3 5 45 34
```

Clips were sent to the user one at a time, without saying which name was
expected.

## Actual Result

### The sound path

- **Music:** the `.ADP` files are stereo 4-bit ADPCM music streams (two
  predictors per byte; the routine at `0x06016708`).
  - `002_SELE.ADP` and `004_VS.ADP` are byte-equal to `INITDATA.PCA`
    parts 3 and 4, which go into the cart at boot.
  - The step rule and the 16.16 multiplier table (`0x060168F4`: 0.9 ×4,
    1.2, 1.6, 2.0, 2.4) are MSHvSF's.
- **Clip bank:** `INITDATA.PCA` part 5 (500,680 bytes) is loaded into
  sound RAM at `0x5C00`. It holds:
  - a u32 count (113);
  - one (u16 ID, u16 length, u32 offset) entry per clip;
  - the clip data from `0x5F8C`. Each offset is the running sum of the
    lengths.
- **Mixer:** 16 channel records of 28 bytes at WRAM-H `0x0601776C`
  (current pointer, start, end, step, predictor, volume, flag; set up at
  `0x060168A4`). The mixed output goes to two rings in sound RAM
  (`0x0C00`, `0x2C00`).
  - Write breakpoints on the records and on sound RAM never fire, while
    the sound chip's registers do. The mixer most likely runs on the
    slave SH-2 (HYPOTHESIS), so the records were polled instead.
- **Decoder check:** the MSHvSF decoder, replayed from each active
  channel's start to its current pointer, gives the stored step and
  predictor in **102 of 102** sound-RAM channel records. That covers 10
  dumps: pick, win, VS screen and the patched runs. Channels playing from
  the cart are skipped (not in the dump).

### When names are spoken, and which clips

`channel_poll.py`: the clips that start after a pick (first sighting
about 1.1-1.2 s after the key is sent):

| Pick | Channel 10 (name call) | Channel 12 | Channel 8 (the character's own voice) |
| --- | --- | --- | --- |
| Vega | `0x121` (bank #35) | `0x1C5` | `0x0B3` (#102) |
| Gouki | `0x01D` (#4) | `0x1C5` | `0x0B7` (#103) |
| Nash | `0x149` (#47) | `0x1C5` | `0x1A0` (#111) |

On the win screen (Nash's win, `f00029551`, CPU vitality 0), channel 10
plays Nash's call `0x149`, about 2.2 s into the run.

**The user's identifications** (each clip sent alone):

| Clip | Source | User |
| --- | --- | --- |
| 1 (`614446c4…`) | the recording at Vega's pick, with music | "Vega" |
| 2 (`02b8f730…`) | bank `0x1C6` | "a random sound effect", no name |
| 3 (`52e58fd0…`) | bank `0x1C8` | a sound effect, not Vega |
| 4 (`c46e9ee2…`) | bank `0x121` | "Vega" |
| 5 (`dc219310…`) | bank `0x147` | "Bison" |
| 6 (`e42a4355…`) | bank `0x021` | "Akuma" |
| 7 (`d6b68843…`) | bank `0x01B` | "Charlie" |

Clips 2 and 3 came from a dump taken too late: stale records from before
the state. That led to the polling method.

### The call table

**Table A** is in `MMPACK.PCA` (decoded `0x79EE`, in the stream loaded at
`0x06014000`, so WRAM-H `0x0601B9EE`). It has 12-byte records indexed by
slot, with the call ID first:

| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | **14** | **15** | **16** | 17 | **18** | **19** | **20** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ID | `0F9` | `0E9` | `123` | `12B` | `12C` | `0F5` | `102` | `099` | `0E7` | `14A` | `162` | `0F3` | `122` | `101` | `121` Vega | `01D` Gouki | `149` Nash | `148` | `147` "Bison" | `021` "Akuma" | `01B` "Charlie" |

The other fields are `0020 0010 0010 8178` for every slot. Entries 19
and 20 are past slot 18, and entry 20 is also the record before table B.

**Controlled changes** (each checked against the original bytes; the call
read from channel 10):

| Run | Patch | Result |
| --- | --- | --- |
| `poll_patchA` | table A entry 14 (`0x0601BA96`): `0121` → `0147` | Vega's pick plays `0x147` (bank #45) |
| `poll_winA` | table A entry 16 (`0x0601BAAE`): `0149` → `0147` | Nash's win plays `0x147` |
| `poll_patchB` | table B entry 14 (`0x0601BB92`): `0121` → `0147` | no change (`0x121`) |
| `poll_winB` | table B entry 16 (`0x0601BBAA`): `0149` → `0147` | no change (`0x149`) |

So table A picks the name call at the select screen and at the win
screen. Table B (same IDs, other fields `0010 FFFF 0010 8178`) was not
used in either.

## Conclusion

**CONFIRMED:**

- **When:** the Saturn calls the character's name when they are picked and
  on the win screen.
- **Clips:** the calls are clips of the 113-clip bank that `INITDATA.PCA`
  puts in sound RAM. The SH-2 mixer decodes them with MSHvSF's ADPCM
  algorithm (102 of 102 channel states reproduced).
- **The choice:** the call ID is the first word of table A in
  `MMPACK.PCA`, indexed by slot. Changing an entry changes the call at
  both moments.
- **American calls:** the disc holds "Bison" `0x147` (slot 18's call),
  "Akuma" `0x021` and "Charlie" `0x01B` (entries 19 and 20), as identified
  by the user. An American variant needs only table A entries 14, 15
  and 16 changed to `0x147`, `0x021` and `0x01B`.

**SUPPORTED:** Gouki's call is `0x01D` and Nash's is `0x149`. Both play on
the call channel at their picks (and Nash's on his win), and the user
heard those names in play.

## Uncertainty and Alternatives

- **Table B's role** is unknown. It may serve the other player's side or
  another screen.
- **The VS screen** played one clip from the cart (`0x0240FBD7`), not from
  the bank; it was not identified.
- **`poll_winA`:** one channel played a cart clip (`0x02404C32`) in place
  of Nash's own voice. Whether that is caused by the patch or is a random
  win voice is unknown.
- **Slave SH-2:** that the mixer runs there is a HYPOTHESIS, drawn from
  the breakpoints never firing.
- **`RATE`:** the export rate (12,016 Hz, from MSHvSF) was not measured.
  The user did not report a wrong pitch.
- **Slot 18's** own call is "Bison". Who uses slot 18 is `SPECIAL-001`.
