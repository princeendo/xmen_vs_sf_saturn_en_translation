# EXP-0006: Validate the Reused Agent Interface on XvSF (V1-V4)

Task: EMU-021
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-020` concluded that the MSHvSF agent-interface patch should be reused.
`AGENTS.md` rule 16 requires its validations V1-V4 to pass on XvSF before its
output is evidence. MSHvSF's V4 used an MSHvSF quote buffer; XvSF needs its
own target. `EXP-0004` halted the stock debugger at `06021B26 mov.b r0,@r9`
with R9 `060C9047`.

## Hypothesis

The patch applies unchanged to 1.32.1 and builds. The patched binary (V1)
behaves like stock without `MEDNAFEN_AGENT_DIR` and answers smoke commands
with it. (V2) `read` equals a validated extraction of a state saved in the
same poll. (V3) Writes round-trip and restore; pause, step, run and frame
counts work. (V4) A log-mode write breakpoint on `060C9047` records hits at
the store `EXP-0004` showed, without halting.

## Controlled Change

The patched binary in place of the stock one; nothing else. Same image,
BIOS and silent home; `sav/` emptied before each run.

## Prediction

V1: 89 of 89 per-second frames equal `EXP-0001`. V2: four regions identical
to `mcs_extract` of the same-poll state. V3: exact round trip; `frames 30`
halts 30 frames later. V4: hits with R9 `060C9047` including PC `06021B26`,
frames advancing.

## Inputs and Provenance

- Patch `vendor/mednafen/patches/0001-agent-interface.patch`, SHA-256
  `c30146ef…5244`, from MSHvSF `b9a6593` (see `vendor/mednafen/README.md`).
  Applied with `patch -p1` to a copy of the stock source; the patched
  `src/drivers` equals MSHvSF's patched tree (`diff -r`, no output).
- Built binary `vendor/mednafen/build-agent/src/mednafen`, 21,379,144 bytes,
  SHA-256 `290d471736a54afb254b8a00b0031f00699bf22007de466c6c7b9906e07df9f8`
  (same configure options and host as `EMU-001`; only the generic
  position-independent-code warnings that the stock build also prints). The
  stock binary hash (`892bb60a…29dd`) was the same before and after.
- Client `tools/mednafen/agent.py` and `tests/unit/test_agent.py`, copied from
  MSHvSF `69c666c` (two tests of MSHvSF-only tools dropped).
- Source image, BIOS and home as `EXP-0004`.

## Tools and Environment

`tools/mednafen/cold_boot.py --mednafen vendor/mednafen/build-agent/src/mednafen`
(V1 equivalence, `MEDNAFEN_AGENT_DIR` unset);
[`validate.py`](validate.py) (V1 smoke, V2-V4); `tools/memory/mcs_extract.py`.

## Procedure

```bash
env -u MEDNAFEN_AGENT_DIR ./invenv.sh python -m tools.mednafen.cold_boot \
  "local/disc_images/xmvsf_saturn_jp_3m/X-Men vs. Street Fighter (Japan) (3M).cue" \
  local/emu021/v1-stock-equiv --seconds 90 --mednafen vendor/mednafen/build-agent/src/mednafen
./invenv.sh python research/experiments/EXP-0006/validate.py local/emu021/run2
./invenv.sh python -m tools.memory.mcs_extract local/emu021/run2/v2.mc0 \
  --out-dir research/memory_dumps/emu021/run2-v2
cmp local/emu021/run2/wram_h.bin research/memory_dumps/emu021/run2-v2/wram_h.bin   # and the others
```

`validate.py` runs to frame 4200 (`frames`), resumes, and sends one command
file with four `read`s, `savestate`, `screenshot` and `status` (V2); pauses
and writes `EMU-021 WRITE OK` at WRAM-H `0xF0000`, reads back, restores,
steps, runs, and runs `frames 30` (V3); sets `bpmode log` with
`bp write 060C9047-060C9047 260C9047-260C9047` for 1,800 frames (V4); then
halt mode on all of WRAM-H (V4b). Run 1 used 120 frames for V4.

## Actual Result

- **V1 equivalence.** Without the agent directory, all 89 per-second frames
  equal `EXP-0001` boot 1; log `SGID: T-1226G`, `Cart: 4MiB Extended RAM`.
- **V1 smoke.** `status` answered at frame 4; `spaces` listed 13 spaces
  (`physical`, `workraml`, `workramh`, `scspram`, `scspmprog`, `scsptemp`,
  `scspmems`, `dspprog`, `backup`, `vdp1vram`, `vdp1fb0`, `vdp1fb1`,
  `vdp2vram`); `regs` returned SH-2 and on-chip registers.
- **V2.** In both runs, `read` of `workraml`, `workramh`, `vdp1vram` and
  `vdp2vram` is byte-identical to `mcs_extract` of the same-poll state
  (run 1 state `cb233583…be4b`, run 2 `7fd53ec6…fb59`, each 3,493,834 bytes;
  run 1 WRAM-H `4d55460a…`). The screenshot (352x240) shows the title.
- **V3.** Round trip exact (before `66666790…`, written = pattern, restored =
  before). `pause` halted at frame 4206; `step` moved PC `0601F464` to
  `0601F460`; `run` resumed; `frames 30` from 4209 halted at 4239;
  `savestate` while halted was refused ("not allowed while halted").
- **V4.** Run 1 (frames 4240-4360): no hits. Run 2 (1,800 frames): 6 hits,
  all R9 `060C9047`, PCs `06021B6A` (frames 4511, 4658, 4785, 5272, …) and
  `06021B26` (frame 4917, R0 `00000021`); frames kept advancing (log mode).
- **V4b.** Halt mode on all of WRAM-H halted at frame 6038, PC `06000846`;
  `regs` returned the registers as text.
- Source manifests identical before and after; both runs exited 0.

## Conclusion

**CONFIRMED.** The reused agent interface builds unchanged, is
frame-identical to stock when inactive, and on XvSF reads (equal to validated
state extraction), writes, controls halts, and logs write breakpoints that
agree with the stock debugger's halt in `EXP-0004`. Its output may be used as
evidence for XvSF.

## Uncertainty and Alternatives

- V4's agreement with `EXP-0004` is at the level of instruction address and
  target register; the stock halt's R0 (`00000042`, read by eye) came from a
  different instant and was not expected to match.
- `06021B6A` is a second store with R9 `060C9047`; its instruction was not
  disassembled here.
- V2 covers two title-screen instants.

## Reproduction

Run the procedure. Expect the V1 frame comparison 89/89, four identical
`cmp`s, `round_trip: true`, and V4 hits with R9 `060C9047`.
