# EXP-0017: Trace the Quote Table to Its Disc File

Task: DISC-001
Status: DONE
Confidence: CONFIRMED

## Observation

The quote table is 22 records of 38 big-endian 16-bit codes at WRAM-L
`0x0024F5D8`-`0x0024FC60` (1,672 bytes, `EXP-0015`). In the `EXP-0013`
session it appears between states 5696 (cursor on Ryu, before the pick) and
5750 (after the pick). MSHvSF found its quote data in a compressed file, by
halting its decompressor with a write breakpoint (playbook; a HYPOTHESIS for
XvSF).

## Hypothesis

The table is loaded from one data-track file when Ryu is picked. A write
breakpoint on the table halts in the loader, and the loader identifies the
file and its storage format.

## Controlled Change

One variable: the pick. From state 5696, with a halt-mode write breakpoint
on `0x0024F5D8`-`0x0024FC5F` (and the `0x2024…` cache-through mirror):

- **Control:** no input for 120 frames.
- **Trial:** Saturn pad A, the pick button, held for 0.2 s.

## Prediction

The control has no hit. The trial halts in a copy or decompression routine.
Its registers or literals name a destination and size, which lead to one file
whose decoded bytes contain the table exactly.

## Inputs and Provenance

- Session state `local/dbg003/session/states/f00005696.mcs` (`EXP-0013`).
- Untouched Track 01, SHA-256 `c904a386…da70`, hashed again after the work
  (`local/logs/disc001-source-after.json`).
- Patched build (`EXP-0006`).
- Reference table: `research/memory_dumps/dbg005/quote_visible/wram_l.bin`
  `[0x4F5D8:0x4FC60]`, SHA-256 `31d77550…f950`.
- The data-track files were extracted by `tools/disc/iso9660.py` to the
  ignored `local/ref007/saturn_files/` (`EXP-0011`).

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/iso9660.py` | ISO 9660 listing with sector checks |
| `tools/mednafen/replay_state.py` | The control |
| [`catch_loader.py`](catch_loader.py) | The trial. It uses a scratch home, `local/mednafen_keys`, with pad A bound to the K key; the user's homes are unchanged. |
| `tools/sh2/disasm.py` | SH-2 disassembly. Copied from MSHvSF `69c666c` with provenance; `bsrf`/`braf` were added. |
| `tools/disc/prs.py` | The decoder, rewritten to the executed format |

## Procedure

```bash
T="local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
./invenv.sh python -m tools.disc.iso9660 --check "$T" > local/disc001/iso_listing.json
# control
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/dbg003/session/states/f00005696.mcs local/disc001/trace1 --steps 2 \
  --step-frames 60 --bp "write:0024F5D8-0024FC5F,2024F5D8-2024FC5F" \
  --agent-dir local/disc001/agent
# trial, twice
./invenv.sh python research/experiments/EXP-0017/catch_loader.py local/disc001/catch1
./invenv.sh python research/experiments/EXP-0017/catch_loader.py local/disc001/catch2
./invenv.sh python -m tools.sh2.disasm local/disc001/catch1/workramh.bin \
  --base 0x06000000 --start 0x0600CF40 --end 0x060108C4
./invenv.sh python -m tools.disc.prs local/ref007/saturn_files/MC09.SHP
./invenv.sh python -m tools.memory.mcs_extract \
  local/dbg003/session/states/f00005750.mcs --out-dir local/disc001/s5750
```

## Actual Result

**ISO layout.** The data track has 71,908 sectors, all Mode 1, with no bad
sync and no address mismatch. The listing has 236 files and is identical to
the `EXP-0011` listing. It is committed with LSN, size and SHA-256 in
[`references/saturn_jp/iso_listing.json`](../../../references/saturn_jp/iso_listing.json).

**Earlier tests (before the trace).**

- A raw search of all 236 files for the table: no hit.
- A standard PRS decoder (little-endian long word, from offset 0) failed at
  output 0 on all 60 `.PRS` files (`local/disc001/prs.log`).
- These are explained by the format below: a 4-byte header and a big-endian
  long word.

**Control.** No input, 120 frames: 0 breakpoint hits (`trace1/events.log` is
empty).

**Trial.** Both runs halted on the first table write, at PC `0x0600D124`
(`mov.l r2,@r12`), with R12 = `0x0024F5D8`.

| Run | Frame | Registers | WRAM-L at the halt |
| --- | --- | --- | --- |
| catch1 | 313 | (reference) | (reference) |
| catch2 | 296 | identical to catch1 | byte-identical to catch1 |

The frame differs only by key timing. WRAM-H differs in 4,776 bytes, none in
the loader code or its buffers (`0x0600CF00`-`0x060128C4`).

**The loader, from the disassembly at the halt.**

- `0x0600D09C` (called from `0x0600D082`) reads sectors to a 0x800-byte buffer
  at `0x0600FE9C`. The caller passed file size R5 = R9 = `0x50CE` and the
  destination list at `0x0600D168`: `0x0024D000`, size `0xFFFFFFFF`.
- The file's first longword is an entry count. A count of 0 means one stream to
  the caller's destination.
- The routine then runs a streaming decompressor at `0x0601077C`. It writes
  into an 8 KiB ring at `0x060108C4`, and longwords are copied from the ring to
  the destination (the halting `mov.l`).
- **Decompressor:**
  - Control bits are taken LSB first (`shlr`); 1 is a literal.
  - 0,0 then two bits (first high) and an offset byte: copy n + 2 bytes from
    byte − `0x100`.
  - 0,1 then a **big-endian** word (`shll8` on the first byte): copy
    (v & 7) + 2 bytes from (v >> 3) − `0x2000`.
  - When v & 7 is 0, a count byte gives n + 1 bytes, and n = 0 ends the stream.

**The file.** Only one file is `0x50CE` = 20,686 bytes: **`MC09.SHP`**. It is at
LSN 53,719, 11 sectors, SHA-256 `e9a5605b…641a`. It is character 09 (arcade
slot 9 is Ryu, `EXP-0015`).

**Decoding with the executed format** (`tools/disc/prs.py`):

- All 20,686 input bytes are consumed and give 43,064 bytes, SHA-256
  `9af0c678…f273`.
- The 1,672-byte table is at output offset **`0x25D8`**, byte-identical
  (`0x0024D000` + `0x25D8` = `0x0024F5D8`).
- The first `0x25D8` bytes equal WRAM-L `0x0024D000`-`0x0024F5D7` at the halt
  (what the loader had already written).
- At state 5750, after the load, the 43,064 bytes at `0x0024D000` equal the
  output except for 777 bytes. These are exactly 259 big-endian 32-bit fields,
  each holding the file value + `0x0024D040` (fix-ups applied after the load).
  None is in the table.

**Same format elsewhere.** The decoder consumes 50 files completely, with
nothing left over:

- `MC00`-`MC11.SHP` (18) and `MCED.SHP`;
- `MS00`-`MS0A.SHP`;
- `PL00AP`-`PL17AP.PCA`, `CPK.PCA`, `LOADING.PCA` and `XVSOPEN.PCA`.

The `.PRS` files have nonzero first longwords (multi-entry headers) and were
not decoded.

## Conclusion

**CONFIRMED.** Ryu's win-quote table is loaded, when Ryu is picked, from
`MC09.SHP` (LSN 53,719). The file is a 4-byte entry count of 0 followed by one
LZ77 stream in the format above. Decompressed, the table is at offset `0x25D8`
and is loaded to `0x0024D000`, so the M1 record 10 is at decompressed offset
`0x28D0`. The table bytes are not changed after the load.

## Uncertainty and Alternatives

- The loader code read here has no checksum or length check beyond the
  stream's end marker. A check elsewhere (for example on the decompressed
  data) is not excluded. A rebuilt image will test this (`DISC-002`).
- The 259 fix-ups (+`0x0024D040`) suggest the first `0x40` bytes are a header
  and the fields are offsets from its end. The routine that applies them was
  not traced (HYPOTHESIS).
- Re-insertion needs an encoder whose output this decoder (and the game)
  accepts. The new file must fit the 11 sectors or be relocated; not tested.
- Multi-entry (`.PRS`) files and the other `MC*.SHP` characters are assumed,
  not shown, to carry their quote tables the same way.

## Reproduction

Run the procedure. Expect:

- no control hits;
- trial halts at `0x0600D124` with R12 = `0x0024F5D8`;
- `MC09.SHP: 20686 -> 43064 bytes, used 20686, 9af0c678…`;
- the table at output offset `0x25D8`.
