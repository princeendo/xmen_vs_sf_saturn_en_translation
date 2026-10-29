# EXP-0018 (M2): Reproduce the Quote Change From a Rebuilt Image

Task: DISC-002
Status: DONE
Confidence: CONFIRMED

## Observation

Ryu's quote table is decompressed from `MC09.SHP` (LSN 53,719, 20,686
bytes) at the pick (`EXP-0017`). In that file it sits at offset `0x25D8`;
record 10, the M1 record, is at `0x28D0`. The stream ends in the file's last
sector, and the loader asks for every sector. Which record is shown varies
between sessions (`EXP-0007`, `EXP-0013`), and the selector is unknown.

## Hypothesis

An image built from the untouched source, with only `MC09.SHP` re-encoded to
carry あいう, shows あいう in Ryu's win quotes after a cold boot.

## Controlled Change

One variable is changed: the content of `MC09.SHP`, re-encoded at the
original size. Every other file and sector is copied unchanged.

The marker writes `09E1 09E3 09E5` (あいう) over line-1 cells 3-5 of all 16
win-quote records (rule 12; every original value is in the ignored
`local/disc002/marker1/changes.json`). Two examples:

| Record | Decompressed offset | Original | Modified |
| --- | --- | --- | --- |
| 0 | `0x25DE` | `0A2B 0A0E 0A9C` | `09E1 09E3 09E5` |
| 10 (M1) | `0x28D6` | `0A21 09E5 0AC8` | `09E1 09E3 09E5` |

Each record's cells sit at `0x25DE` + 76 × record. In all, 80 decompressed
bytes change.

Control: the original image, run through the same steps.

## Prediction

- Only `MC09.SHP`'s sectors change, and every sector passes EDC/ECC.
- A pick loads the marked table with the rebuilt image mounted, and the
  original table with the original image.
- A cold-booted Ryu win shows あいう in cells 3-5 of line 1.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m/`, 42 files, hashes in `references/saturn_jp/README.md`; unchanged afterwards (`local/logs/disc002-source-after.json`) |
| `MC09.SHP` | read from Track 01 and checked against `references/saturn_jp/iso_listing.json` |
| Session state | `local/dbg003/session/states/f00005696.mcs` (`EXP-0013`) |
| Emulator | patched build (`EXP-0006`) for the agent runs; stock build for the cold-boot videos |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/prs.py` | Now includes `compress` and `compress_file`: greedy matching, offsets up to `0x1FFF`, padding, and a minimum stream end. |
| `tools/disc/sector.py`, `tools/disc/patch_image.py` | Copied unchanged from MSHvSF `69c666c`. |
| [`build_marker.py`](build_marker.py) | Builds the marker `MC09.SHP`. |
| [`boot_trace.py`](boot_trace.py) | Logs writes to the table range during a boot. |
| [`boot_ram_scan.py`](boot_ram_scan.py) | Hashes WRAM each second of a boot. |
| [`pick_load.py`](pick_load.py) | Picks Ryu from state 5696 with a given image mounted and reads the load. |
| `tools/mednafen/session_recorder.py`, `tools/memory/mcs_extract.py` | The user's session. |

## Procedure

```bash
SRC=local/disc_images/xmvsf_saturn_jp_3m
T="X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
CUE="X-Men vs. Street Fighter (Japan) (3M).cue"
./invenv.sh python -m tools.disc.sector "$SRC/$T"              # EDC/ECC of the source
./invenv.sh python research/experiments/EXP-0018/build_marker.py local/disc002/marker1
./invenv.sh python -m tools.disc.patch_image --source-dir $SRC \
  --manifest references/saturn_jp/README.md --track "$T" --file "MC09.SHP;1" \
  --data local/disc002/marker1/MC09.SHP --out-dir build/disc002_marker1   # and _marker2
./invenv.sh python -m tools.disc.sector "build/disc002_marker1/$T"
./invenv.sh python -m tools.disc.iso9660 --check "build/disc002_marker1/$T"
./invenv.sh python -m tools.mednafen.cold_boot "build/disc002_marker1/$CUE" local/disc002/boot1 --seconds 90
./invenv.sh python -m tools.mednafen.cold_boot "$SRC/$CUE" local/disc002/boot_orig --seconds 90
./invenv.sh python research/experiments/EXP-0018/pick_load.py "$SRC/$CUE" local/disc002/pick_orig
./invenv.sh python research/experiments/EXP-0018/pick_load.py "build/disc002_marker1/$CUE" local/disc002/pick_built
```

User play check: the agent launched the rebuilt image from power-on in the
interactive home, with `session_recorder.py --state-interval 3 --keep-states
120` (`local/disc002/session/`). The user picked Ryu and won two fights.

## Actual Result

**Encoder.**
- Re-encoding the original decoded `MC09.SHP` gives the original file **byte
  for byte**. So do 40 of the 51 files the decoder reads completely; the other
  11 differ only in match choices.
- The marker file: 20,686 bytes, SHA-256 `60f2d10e…ff75`. Its stream ends at
  byte 20,659, in the last sector, and it is zero-padded to the original size.
- It decodes exactly to the marked data (`49bbbce6…b114`), and two builds of
  it are identical.

**Image.**
- **Source EDC/ECC:** the copied routine reproduces the stored EDC/ECC of all
  71,908 source sectors (0 invalid).
- **Rebuilt Track 01:** `9b819618…ac32`. All 71,908 sectors are valid, and the
  ISO check has no errors.
- **Changed sectors:** LSN 53,722-53,729 only, all inside `MC09.SHP`
  (53,719-53,729). The file's first three sectors re-encode identically.
- **Listing:** every path, LSN and size is unchanged; only `MC09.SHP`'s hash
  differs.
- **Other files:** the other 41 components are byte-identical, and two builds
  gave identical hashes. Source hashes are unchanged.

**Cold boot (stock build, 90 s).** The rebuilt image's frames (2026-10-29
00:34 UTC) equal an original boot run 8 minutes later, 93 of 93. Both differ
from the `EMU-003` boots (2026-10-28 19:24-19:27 UTC) from second 43 on. That
divergence comes with the time of the run, not the image (see Uncertainty).

**Boot traces (patched build, no input).**
- In 60 s the only writes to the table range are the BIOS RAM clear at frame
  2 (418 longwords, PC `0x000002B0`), so the attract sequence does not load it.
- WRAM, hashed each second for 45 s: two runs of the original differ from each
  other in 6-9 WRAM-H bytes from second 11 on. The rebuilt run differs from
  both only in those same bytes.

**Pick from state 5696 (the state's later disc reads come from the mounted
image).**

| Image mounted | Table | Whole 43,064-byte buffer |
| --- | --- | --- |
| Original | original | = original decode + the 259 `+0x0024D040` fix-ups |
| Rebuilt | marker in all 16 records | = marked decode + the same 259 fix-ups |

**User play check, from power-on** (agent-reviewed):

| Win | Screenshot | SHA-256 | Record | Line 1 |
| --- | --- | --- | --- | --- |
| 1 | `f00008307.png` | `bd067afe…` | 1 | **あいう**るえが止まらない…… |
| 2 | `f00012528.png` | `afe904a8…` | 8 | 教え**あいう**、 |

In both, あいう is in cells 3-5. The rest of each quote and the screen are
normal: no freeze or garbling, and the next stage loaded. In the session's
last state (frame 12,688), the WRAM-L table equals the marked decode exactly.

## Conclusion

**CONFIRMED (M2).** An image rebuilt from the untouched source shows the M1
glyph change in Ryu's win quotes after a cold boot. Only `MC09.SHP` was
re-encoded, at the original size, with only its own sectors rewritten. The
original image is the control at every step. Record 10 itself was not drawn
in the two wins (records 1 and 8 were). It loads from disc with exactly the
M1 bytes, shown in RAM.

## Uncertainty and Alternatives

- **Boot-frame divergence.** Original boots about five hours apart diverge
  from second 43; boots minutes apart match. A host-time input, such as the
  Saturn clock taken from the host, is a HYPOTHESIS. D-001's frame hashes
  reproduce only for boots close in time.
- **Re-encoded sizes.** The re-encoded file is no larger than the original.
  Longer content (English) may not fit 11 sectors; relocation or a better
  encoder is not tested.
- **Padding.** Zero padding after the end marker is accepted here. A file
  whose stream ends before its last sector is not tested.
- **Real hardware.** Not tested.

## Reproduction

Run the procedure. Expect:

- the marker `MC09.SHP` `60f2d10e…`;
- Track 01 `9b819618…`;
- changed LSNs 53,722-53,729;
- the pick results above.

A user Ryu win on the rebuilt image shows あいう in line 1, cells 3-5.
