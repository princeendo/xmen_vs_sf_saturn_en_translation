from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.disc import regression


def test_clear_refuses_paths_outside_build_regression(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not under"):
        regression.clear(tmp_path)


def test_inputs_that_differ_stop_before_any_build(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    references = tmp_path / "references.json"
    references.write_text(
        json.dumps(
            {
                "source_track01_sha256": "0" * 64,
                "program": {"path": str(tmp_path / "absent.bin"), "sha256": "0" * 64},
                "references": [],
            }
        )
    )
    assert regression.main(["--references", str(references)]) == 2
    assert "nothing was rebuilt" in capsys.readouterr().out


def test_report_lists_references_and_marks_mismatches() -> None:
    references: dict[str, object] = {
        "references": [
            {
                "name": "demo",
                "experiment": "EXP-0000",
                "task": "RE-000",
                "specs": ["a.json"],
                "patch_version": 3,
                "files": {"MC00.SHP;1": "a" * 64},
                "track01_sha256": "b" * 64,
            }
        ]
    }
    entry = {"expected": "a" * 64, "built": "c" * 64, "match": False}
    run: dict[str, object] = {
        "date": "2026-10-29T00:00:00+00:00",
        "commit": "abc1234",
        "python": "3.13",
        "source_track01": "d" * 64,
        "source_ok": True,
        "program": "e" * 64,
        "program_ok": True,
        "results": [{"name": "demo", "files": {"MC00.SHP;1": entry}}],
        "match": False,
    }
    text = regression.report_text(references, run)
    assert "| `demo` | `EXP-0000` | `RE-000` | 1 | 3 | 1 | `bbbbbbbb…` |" in text
    assert "| **no** |" in text
    assert "Result: **mismatch**." in text
