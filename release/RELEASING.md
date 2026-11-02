# Making a Release

Adapted from MSHvSF's `release/RELEASING.md` (commit `7d4c587`) for XvSF
(`REL-001`). The examples use `0.1.0`.

The agent does steps 1-6. You do steps 7-9 on github.com, because `gh` on
this machine is signed in as the work account, which this project never uses.

## Before You Start

- [ ] Every open task in `TASKS.md` is done, or you have deferred it.
- [ ] The release image has been played (Mednafen, or real hardware).
- [ ] `git status` is clean, on `main`, and up to date with `origin/main`.
- [ ] `git config user.email` prints
      `13876322+princeendo@users.noreply.github.com`.
- [ ] The local files the top-level `README.md` lists are in place, and
      `xdelta3 --version` reports 3.2.2.

## 1. Rebuild and Check

```bash
./invenv.sh python -m tools.disc.regression --report docs/regression_report.md
./invenv.sh python -m tools.disc.regression --keep --only name_toggle_v4
```

Every reference must match. The release image lands in
`build/regression/name_toggle_v4/image/`.

## 2. The Patches and Their Records

The commands are in [`README.md`](README.md), "Rebuild the Patch". The
`--record` files in `release/` are committed; the zips and docs are checked
against them.

## 3. The Zips, Twice, and the Check

```bash
./invenv.sh python research/experiments/EXP-0071/make_zips.py 0.1.0 build/release/v0.1.0
./invenv.sh python research/experiments/EXP-0071/make_zips.py 0.1.0 build/release/v0.1.0-again
shasum -a 256 build/release/v0.1.0/*.zip build/release/v0.1.0-again/*.zip
bash research/experiments/EXP-0071/check_zips.sh 0.1.0 build/release/v0.1.0 local/rel/v0.1.0-check
```

Both builds must hash the same, and every patch from the unpacked zips must
give the reference track 01. Also apply the `.ssp` with `saturn-patcher-egui`
(`EXP-0071`).

## 4. The Notes

`release/notes_v0.1.0.md`: what changed, the two zips with their sizes and
SHA-256, how to apply, known limits.

## 5. Records

- `TASKS.md`: the `REL-` task with the zip hashes.
- `research_log.md`: the session.

Stage only the files above: never the zips, patches or images (`AGENTS.md`
rule 21).

## 6. Commit, Tag, Push

```bash
git -c user.name=Colin -c user.email=13876322+princeendo@users.noreply.github.com commit ...
git tag -a v0.1.0 -m "X-Men vs. Street Fighter (Saturn) English 0.1.0"
git push origin main v0.1.0
```

## 7-9. Publish (You, on github.com)

| Do this | What you should see |
| --- | --- |
| Open the repository's Releases page, "Draft a new release", choose the tag `v0.1.0`. | The tag is listed. |
| Title "0.1.0", paste `release/notes_v0.1.0.md` as the description. | The notes render. |
| Drag in `build/release/v0.1.0/xmvsf_saturn_en_0.1.0_xdelta.zip` and `xmvsf_saturn_en_0.1.0_ssp.zip`, then publish. | Both files listed under the description. |

Afterwards the agent checks each asset's size and `sha256:` digest through
the public API against the zips built in step 3, and links the release from
the top-level README.
