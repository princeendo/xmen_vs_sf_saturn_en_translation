"""Rebuild every confirmed English build from the untouched source and compare hashes.

Run from the repository root:

    ./invenv.sh python -m tools.disc.regression [--only NAME ...] [--keep]
        [--report docs/regression_report.md] [--references PATH]

The references are `data/regression/references.json` (`RE-011`). Each one
names the specs, the patch version, the name variant (``names``; ``none``
when absent, as for every reference made before `LOC-005`), whether the
boot-warning pictures are built (``boot_warnings``, `BOOT-004`), whether the
special cases are (``special``, `SPEC-004`) and the expected
SHA-256 of every changed file and of the built Track 01. The checks run in this order:

1. **Inputs:** the source Track 01 and the US arcade program image
   (``local/ref003/xmvsfu-68k.bin``) must hash to the recorded values. Write
   the program image with
   ``python -m tools.reference.xvsf_text --driver CPS2_CPP --set xmvsfu
   --rompath ROMS --program-out local/ref003/xmvsfu-68k.bin``.
2. **Rebuild:** `tools.disc.build_english` runs once per reference, with
   ``--image``, writing under ``build/regression/<name>/``. That directory is
   replaced on every run.
3. **Compare:** every built file and the built Track 01 against the
   reference.

Unless ``--keep`` is given, each rebuilt image (hundreds of MB) is deleted
after hashing. Only ``build/regression/`` is ever deleted. With ``--report``,
a Markdown report of the references and this run is written. Exit 0 means
every reference matched.

When to run all of them (user decision, 2026-10-31): only after a change to
the build tools. Otherwise rebuild only newly added references with
``--only``; the others stand as matched by the last full run.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import io
import json
import platform
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from tools.disc import build_english

REFERENCES = Path("data/regression/references.json")
ROOT = (Path("build") / "regression").resolve()
TRACK = build_english.TRACK


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def clear(path: Path) -> None:
    resolved = path.resolve()
    if ROOT not in resolved.parents:
        raise ValueError(f"refusing to delete {resolved}: not under {ROOT}")
    if resolved.exists():
        shutil.rmtree(resolved)


def rebuild(reference: dict[str, object]) -> dict[str, object]:
    name = str(reference["name"])
    work = ROOT / name
    clear(work)
    work.mkdir(parents=True)
    files, image = work / "files", work / "image"
    specs = [str(s) for s in reference["specs"]]  # type: ignore[attr-defined]
    argv = [
        *specs,
        str(files),
        "--patch-version",
        str(reference["patch_version"]),
        "--names",
        str(reference.get("names", "none")),
        *(["--boot-warnings"] if reference.get("boot_warnings") else []),
        *(["--special"] if reference.get("special") else []),
        "--image",
        str(image),
    ]
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        code = build_english.main(argv)
    (work / "build.log").write_text(log.getvalue())
    expected = reference["files"]
    assert isinstance(expected, dict)
    results = {}
    for file_name, want in expected.items():
        got = sha256(files / file_name.split(";")[0])
        results[file_name] = {"expected": want, "built": got, "match": got == want}
    track = sha256(image / TRACK.name)
    want_track = str(reference["track01_sha256"])
    results["Track 01"] = {
        "expected": want_track,
        "built": track,
        "match": track == want_track,
    }
    return {
        "name": name,
        "build_exit": code,
        "files": results,
        "match": code == 0 and all(r["match"] for r in results.values()),
        "image": str(image),
    }


def report_text(references: dict[str, object], run: dict[str, object]) -> str:
    lines = [
        "# Regression Report",
        "",
        "Every confirmed English build is rebuilt from the untouched source by",
        "`tools.disc.regression`, and its hashes are compared with",
        "`data/regression/references.json` (`RE-011`). This file is written by",
        "the script with `--report`; the last run is below.",
        "",
        "## References",
        "",
        "| Name | Experiment | Task | Specs | Patch version | Files | Track 01 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for ref in references["references"]:  # type: ignore[attr-defined]
        lines.append(
            f"| `{ref['name']}` | `{ref['experiment']}` | `{ref['task']}` | "
            f"{len(ref['specs'])} | {ref['patch_version']} | {len(ref['files'])} | "
            f"`{ref['track01_sha256'][:8]}…` |"
        )
    lines += [
        "",
        "## Last Run",
        "",
        f"- Date: {run['date']}",
        f"- Commit: `{run['commit']}`",
        f"- Python: {run['python']}",
        f"- Source Track 01: `{str(run['source_track01'])[:8]}…` "
        f"({'matches' if run['source_ok'] else 'DIFFERS'})",
        f"- Program image: `{str(run['program'])[:8]}…` "
        f"({'matches' if run['program_ok'] else 'DIFFERS'})",
        "",
        "| Reference | File | Expected | Built | Match |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in run["results"]:  # type: ignore[attr-defined]
        for file_name, entry in result["files"].items():
            lines.append(
                f"| `{result['name']}` | `{file_name}` | `{entry['expected'][:8]}…` | "
                f"`{entry['built'][:8]}…` | {'yes' if entry['match'] else '**no**'} |"
            )
    verdict = "all references match" if run["match"] else "**mismatch**"
    lines += ["", f"Result: {verdict}.", ""]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="+", help="reference names to run")
    parser.add_argument("--keep", action="store_true", help="keep rebuilt images")
    parser.add_argument("--report", type=Path, help="write a Markdown report")
    parser.add_argument(
        "--references", type=Path, default=REFERENCES, help="references JSON"
    )
    args = parser.parse_args(argv)
    references = json.loads(args.references.read_text())
    chosen = [
        r
        for r in references["references"]
        if args.only is None or r["name"] in args.only
    ]
    if args.only and len(chosen) != len(args.only):
        parser.error(f"unknown reference in {args.only}")
    source = sha256(TRACK) if TRACK.exists() else "missing"
    program_path = Path(references["program"]["path"])
    program = sha256(program_path) if program_path.exists() else "missing"
    run: dict[str, object] = {
        "date": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "commit": subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "python": platform.python_version(),
        "source_track01": source,
        "source_ok": source == references["source_track01_sha256"],
        "program": program,
        "program_ok": program == references["program"]["sha256"],
        "results": [],
    }
    if not (run["source_ok"] and run["program_ok"]):
        print(json.dumps(run, indent=1))
        print("inputs differ from the references; nothing was rebuilt")
        return 2
    results = []
    for reference in chosen:
        result = rebuild(reference)
        if not args.keep:
            clear(Path(str(result["image"])))
        results.append(result)
        verdict = "match" if result["match"] else "MISMATCH"
        print(f"{result['name']}: {verdict}")
        for file_name, entry in result["files"].items():  # type: ignore[attr-defined]
            if not entry["match"]:
                print(
                    f"  {file_name}: expected {entry['expected']}, got {entry['built']}"
                )
    run["results"] = results
    run["match"] = all(r["match"] for r in results)
    if args.report is not None:
        args.report.write_text(report_text(references, run))
    return 0 if run["match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
