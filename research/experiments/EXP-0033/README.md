# EXP-0033 (M5): Regression References for the Confirmed Builds

Task: RE-011
Status: DONE
Confidence: CONFIRMED

## Observation

Three English builds have been confirmed by play checks:

- `EXP-0024`: Ryu, version-2 patch;
- `EXP-0028`: Ryu and Ken, version 3;
- `EXP-0032`: the 18-character roster.

Each was built by hand-run commands, and nothing rebuilt them together or
compared their hashes. Every build reads the US arcade program image
`local/ref003/xmvsfu-68k.bin`, but no command in the repository wrote that
file. It had been assembled by `tools.reference.xvsf_text.build_program`
(`EXP-0008`, found while rewriting the README in `SESSION-0047`). So a
clean checkout could not reproduce any build.

## Hypothesis

The current tools, given only the untouched disc image, the pinned MAME
driver source and the user's `xmvsfu` ROM set, rebuild all three confirmed
builds byte for byte, both from this working copy and from a fresh clone.

## Controlled Change

- **New command:** `tools.reference.xvsf_text --program-out PATH` writes the
  program image that `build_program` already assembled in memory. Nothing
  else about that tool changed.
- **References:** `data/regression/references.json` records each build's
  specs, patch version and the expected SHA-256 of every changed file and of
  Track 01. It also records the source Track 01 and program image hashes.
- **Tool:** `tools.disc.regression` checks the inputs and rebuilds each
  reference with `tools.disc.build_english --image` under
  `build/regression/<name>/`. It compares the hashes, deletes each image
  after hashing (unless `--keep`), and can write `docs/regression_report.md`.

## Prediction

- The new command writes an image equal to the existing
  `local/ref003/xmvsfu-68k.bin` (`1b1a5a26…`).
- All three references match, both in this working copy and in a fresh
  clone of the commit holding the tools.
- A copy of the references with one expected hash changed is reported as a
  mismatch, with exit 1.
- With inputs that differ, the tool exits 2 without building.

## Inputs and Provenance

| Input | Identity |
| --- | --- |
| Source image | `local/disc_images/xmvsf_saturn_jp_3m`, Track 01 `c904a386…` |
| MAME driver source | `local/mame_src/cps2.cpp`, SHA-256 `a8c09ef8…1602` (MAME 0.289 pin, `SESSION-0005`) |
| Arcade ROMs | `local/arcade_roms/xmvsf_mame0289` (`REF-001`) |
| Expected hashes | from the confirmed builds' outputs: `local/re003/b1`, `local/re007/b1/changes.json`, `local/re010/b1/changes.json` and the three `build/` images |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/reference/xvsf_text.py` | `--program-out` (new) |
| `tools/disc/regression.py` | Input check, rebuild, compare, report (new) |
| `tests/unit/test_xvsf_text.py`, `tests/unit/test_regression.py` | Program-image write; refusal to delete outside `build/regression/`; input-mismatch exit; report rendering |

The clean run used a `git clone` of commit `2d4d224` in the session
scratchpad. Its only additions were symlinks for the three ignored inputs
(the source image folder, `cps2.cpp`, the ROM folder). It ran with this
repository's Python environment, and with the clone as the working
directory, Python imports the clone's own `tools` package (checked).

## Procedure

```bash
./invenv.sh python -m tools.reference.xvsf_text --driver local/mame_src/cps2.cpp --set xmvsfu \
  --rompath local/arcade_roms/xmvsf_mame0289 --program-out local/re011/xmvsfu-68k.bin
cmp local/re011/xmvsfu-68k.bin local/ref003/xmvsfu-68k.bin
./invenv.sh python -m tools.disc.regression --report local/re011/report_local.md
# negative control: one expected hash changed
./invenv.sh python -m tools.disc.regression --only ryu_v2 --references local/re011/references_altered.json
# clean clone
git clone . CLEAN && cd CLEAN
mkdir -p local/disc_images local/mame_src local/arcade_roms
ln -s <repo>/local/disc_images/xmvsf_saturn_jp_3m local/disc_images/
ln -s <repo>/local/mame_src/cps2.cpp local/mame_src/
ln -s <repo>/local/arcade_roms/xmvsf_mame0289 local/arcade_roms/
<repo>/.venv/bin/python -m tools.reference.xvsf_text --driver local/mame_src/cps2.cpp --set xmvsfu \
  --rompath local/arcade_roms/xmvsf_mame0289 --program-out local/ref003/xmvsfu-68k.bin
<repo>/.venv/bin/python -m tools.disc.regression --report docs/regression_report.md
```

## Actual Result

| Run | Result |
| --- | --- |
| `--program-out` | `1b1a5a26…`, byte-identical to the image every build used |
| Working copy, 3 references | `ryu_v2`, `ryu_ken_v3` and `roster_v3` match; exit 0, 5 min 24 s |
| Altered hash (`ryu_v2`, `MC09`) | `MISMATCH`: expected `007b1f46…`, got `507b1f46…`; exit 1 |
| Unit test, differing inputs | exit 2, nothing built |
| Clean clone of `2d4d224` | program image `1b1a5a26…` written in the clone. All 3 references match (27 of 27 file and Track 01 hashes); exit 0, 5 min 20 s. The clone's `git status` showed only the new report and log. |

- **Report:** `docs/regression_report.md` is the clean clone's report,
  copied into the repository.
- **Disk:** each rebuilt image (up to 481 MB) was deleted after hashing.
  Only the rebuilt files and build logs remain under the ignored
  `build/regression/`.
- **Tests:** 167 pass.

## Conclusion

**CONFIRMED.** From the untouched disc image, the pinned driver source and
the user's ROM set, one command per step rebuilds all three confirmed
English builds byte for byte, including from a fresh clone. The comparison
catches a single changed hash. M5's tasks are complete.

## Uncertainty and Alternatives

- **Same machine:** the clean run reused this machine's Python environment
  and inputs. A different machine or tool version is not tested.
- **The references are self-consistent, not independent:** the expected
  hashes come from the builds that were play-checked. They guard against
  drift; they do not re-prove the play checks.

## Reproduction

Run the procedure. Expect the same three matches and the `1b1a5a26…`
program image.
