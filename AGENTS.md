# Agent Operating Contract

This file is authoritative for every AI-agent session in this repository. The
project is an empirical reverse-engineering investigation of the Japanese Sega
Saturn release of X-Men vs. Street Fighter (XvSF), not a speculative
implementation exercise.

A sibling project, the Marvel Super Heroes vs. Street Fighter (MSHvSF) Saturn
English translation, completed the same kind of work first. Its method is
recorded in `docs/playbook_from_mshvsf.md`. That file is a method, not a map:
**nothing in it is a fact about XvSF.**

## Before Each Session

1. Read `local_agent_guidance.md` if it exists. It holds this machine's user
   preferences, git identity, and local paths. It is ignored by git and is never
   committed.
2. Read the "Current State" section of `TASKS.md`.

## Required Method

Use this cycle for each investigation:

```text
OBSERVE -> FORM ONE HYPOTHESIS -> DESIGN A DISCRIMINATING EXPERIMENT
        -> RUN IT -> RECORD RESULT -> ACCEPT / REJECT / REFINE
        -> UPDATE DOCUMENTATION
```

Use confidence labels precisely:

- **UNKNOWN**: no meaningful conclusion yet.
- **HYPOTHESIS**: plausible explanation with insufficient experimental evidence.
- **SUPPORTED**: evidence is consistent, but alternatives remain.
- **CONFIRMED**: a controlled experiment produced the predicted result and is
  reproducible.
- **DISPROVEN**: evidence contradicts the hypothesis.

Plausibility, visual similarity, a matching byte sequence, or an analogous game
is not confirmation. An MSHvSF result is an analogous game.

## Mandatory Rules

1. Never modify original disc images. Derived builds go under `build/` and patch
   commands default to a distinct output path.
2. Record SHA-256, size, filename, and release description for every source-image
   component before research.
3. Never treat a hypothesis as fact or invent missing addresses, offsets, text,
   citations, correspondences, commands, or results.
4. Test one controlled hypothesis at a time when practical. Prefer experiments
   that change exactly one variable.
5. Document every confirmed discovery in `docs/discoveries.md` with evidence and
   reproduction instructions.
6. Record plausible but disproven hypotheses in `research_log.md` so future agents
   do not unknowingly retry them.
7. Do not bypass a blocker or dependency in `TASKS.md`.
8. Do not begin a later milestone because it appears easy. Nothing past M1 begins
   before M1 is confirmed; no generalization begins before M2 works from an
   untouched source image.
9. Preserve exact commands, tool versions, inputs, outputs, and hashes required to
   reproduce results.
10. Prefer reusable scripted extraction and analysis over undocumented manual work.
11. Support visible game modifications with before/after screenshots or equivalent
    evidence and a deterministic checkpoint.
12. For every binary modification, record original bytes, modified bytes, file
    offset or memory address, purpose, expected result, and observed result.
13. Never assume XvSF and MSHvSF share structures, offsets, encodings, file names,
    compression formats, fonts, functions, memory addresses, selection logic, or
    renderer behavior. Every MSHvSF fact, including each one in
    `docs/playbook_from_mshvsf.md`, is at most a **HYPOTHESIS** for XvSF until an
    XvSF experiment confirms it.
14. Never assume CPS-II, PlayStation, and Saturn structures are identical.
15. Use reference releases as evidence and translation oracles, not templates.
16. Use stock Mednafen first. The MSHvSF frontend-only agent-interface patch may
    be reused once stock Mednafen boots XvSF (`EMU-004`) and `EMU-020` records
    why stock Mednafen is insufficient here. Re-run the interface validations
    V1-V4 on XvSF before using it as evidence.
17. Any Mednafen change beyond that patch is the smallest useful change, with the
    upstream URL, version/revision, patches, rationale, and build steps preserved.
18. Python 3.12+ is the default implementation language. Avoid large dependencies
    without a demonstrated need.
19. Run Python tooling through `./invenv.sh`; do not rely on an activated shell.
20. Update `TASKS.md` and `research_log.md` before ending a substantial session.
21. Never commit copyrighted game images, BIOS files, extracted game contents,
    save states, memory dumps, screenshots, or emulator binaries.
    Exception (carried from MSHvSF, user decision 2026-10-26): the release patch
    files themselves (xdelta and SSP, and zips of them) may be published as
    GitHub Release assets. They are still never committed to git history.
22. Keep binary evidence locally under ignored paths. Commit hashes, addresses,
    scripts, schemas, small synthetic fixtures, and derived factual metadata.
23. Do not work on endings before the post-fight pipeline is proven and generalized.
24. Do not work on special cases (secret or hidden characters, bosses, and other
    exceptions, once XvSF's own are identified) before the ordinary-character
    pipeline is mature and a task explicitly permits it.
25. Do not modify the MSHvSF repository, its source images, or its tools from
    this repository. Copy a tool here, with its provenance, before changing it.
26. Code copied from MSHvSF keeps a provenance note (source path and commit).
    Anything that hard-codes an MSHvSF address, offset, file name, or format is
    parameterized or rewritten, then re-validated on XvSF before its output is
    evidence.

## Task Discipline

Allowed statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and
`REJECTED`. Keep at most one reverse-engineering experiment `IN_PROGRESS`. Code or
notes alone do not make a task `DONE`; all acceptance criteria must be supported by
evidence. If prerequisites change, update dependencies and blockers before work.

When blocked, state the unknown, available evidence, competing explanations, and
the smallest discriminating experiment. Do not respond with speculative systems or
premature abstractions.

## Artifact Discipline

Significant experiments use `research/experiments/EXP-NNNN/`, based on the template
in `research/experiments/README.md`. Do not create empty evidence files. Every
experiment records the observation, hypothesis, single change, prediction, actual
result, conclusion, and uncertainty.

Save states are checkpoints, not analyzable RAM snapshots. Dump identical Saturn
memory regions from each checkpoint into stable raw files before differential
analysis. There are two sources for those raw files:

- stock debugger dumps;
- a save-state extractor (to be copied from MSHvSF `tools/memory/mcs_extract.py`).

Use extracted data for a region only after that region's extraction has matched,
byte for byte, a stock debugger dump of the same paused instant **on XvSF**, as
recorded in `docs/discoveries.md`. Unvalidated regions remain `HYPOTHESIS`
evidence. Never analyze the compressed state file directly.

Begin with WRAM-L `0x00200000-0x002FFFFF` and WRAM-H `0x06000000-0x060FFFFF`.
Expand to cartridge RAM or VDP VRAM only with the rationale recorded in the
experiment.

`docs/discoveries.md` contains only durable `CONFIRMED` findings. Put hypotheses and
failures in `research_log.md`; put unresolved questions in
`docs/known_unknowns.md`.

## Session Closeout

Before ending substantial work:

1. Run relevant tests, lint, formatting, and typing checks.
2. Record commands and outcomes in `research_log.md`.
3. Update task status only when acceptance criteria are met.
4. Identify the next unblocked task without beginning a gated milestone.
5. Check that no copyrighted or machine-local artifact is staged for commit,
   including `local_agent_guidance.md`.
6. After each successfully completed user-requested task, run the relevant
   verification, inspect the status and diff, stage only intended files, create
   a concise commit, and push it to the configured upstream branch. Never force-
   push or commit prohibited artifacts or secrets; report an unavailable
   upstream or failed push as a blocker.
