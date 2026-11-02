"""Copied from the MSHvSF repository, ``tests/unit/test_disc_make_patch.py`` at commit
``5e8d4ec``, for XvSF's ``REL-001``."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.disc import make_patch, make_ssp
from tools.disc.iso9660 import RAW_SECTOR, SYNC
from tools.disc.make_patch import (
    TRACK01,
    compare_images,
    components,
    decode,
    encode,
    patch_name,
    ra_hash,
    ra_header,
)


def write(directory: Path, files: dict[str, bytes]) -> dict[str, Path]:
    directory.mkdir()
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / "notes.txt").write_text("ignored")
    return components(directory)


def test_compare_images_lists_differing_and_unchanged(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1", "x.cue": b"c"})
    built = write(tmp_path / "b", {"x (Track 01).bin": b"2", "x.cue": b"c"})
    assert compare_images(source, built) == (["x (Track 01).bin"], ["x.cue"])


def test_compare_images_rejects_different_component_sets(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1"})
    built = write(tmp_path / "b", {"y (Track 01).bin": b"1"})
    with pytest.raises(ValueError):
        compare_images(source, built)


def test_patch_name_uses_the_track_label() -> None:
    name = "X-Men vs. Street Fighter (Japan) (3M) (Track 01).bin"
    assert patch_name("m8", name) == "m8.Track01.xdelta"
    assert patch_name("m8", "disc.bin") == "m8.disc.xdelta"


@pytest.mark.skipif(shutil.which("xdelta3") is None, reason="needs xdelta3")
def test_xdelta_round_trip_and_wrong_source(tmp_path: Path) -> None:
    source, target = tmp_path / "s.bin", tmp_path / "t.bin"
    data = bytes(range(256)) * 400
    source.write_bytes(data)
    target.write_bytes(data[:1000] + b"ENGLISH" + data[1007:])
    patch, out = tmp_path / "p.xdelta", tmp_path / "o.bin"
    encode("xdelta3", source, target, patch)
    decode("xdelta3", source, patch, out)
    assert out.read_bytes() == target.read_bytes()
    wrong = tmp_path / "w.bin"
    wrong.write_bytes(bytes(len(data)))
    with pytest.raises(subprocess.CalledProcessError):
        decode("xdelta3", wrong, patch, tmp_path / "w_out.bin")


def mode1_track(*users: bytes) -> bytes:
    """Mode 1/2352 sectors; the header's address bytes are not read here."""
    return b"".join(
        SYNC + b"\x00\x02\x00\x01" + u.ljust(2048, b"\x00") + bytes(RAW_SECTOR - 2064)
        for u in users
    )


HEADER = b"SEGA SEGASATURN SEGA TP T-12    T-1226G   V1.002".ljust(512, b" ")


def test_ra_header_is_sector_0_user_data_only(tmp_path: Path) -> None:
    a, b = tmp_path / "a.bin", tmp_path / "b.bin"
    a.write_bytes(mode1_track(HEADER + b"boot code", b"files"))
    b.write_bytes(mode1_track(HEADER + b"other code", b"english"))
    assert ra_header(a) == HEADER
    assert ra_hash(a) == ra_hash(b) == hashlib.md5(HEADER).hexdigest()


def header_images(tmp_path: Path) -> list[str]:
    """A source and a built image whose disc headers differ, and a manifest."""
    source, built = tmp_path / "source", tmp_path / "built"
    source.mkdir()
    built.mkdir()
    (source / TRACK01).write_bytes(mode1_track(HEADER, b"files"))
    (built / TRACK01).write_bytes(mode1_track(HEADER.replace(b"V1.002", b"V1.003")))
    manifest = tmp_path / "manifest.md"
    manifest.write_text(hashlib.sha256((source / TRACK01).read_bytes()).hexdigest())
    return [
        *("--source-dir", str(source), "--built-dir", str(built)),
        *("--manifest", str(manifest), "--stem", "t", "--out-dir", "build/release"),
    ]


@pytest.mark.skipif(shutil.which("xdelta3") is None, reason="needs xdelta3")
def test_make_patch_refuses_a_changed_disc_header(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        make_patch.main(header_images(tmp_path))
    assert "RetroAchievements" in capsys.readouterr().err


def test_make_ssp_refuses_a_changed_disc_header(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        make_ssp.main([*header_images(tmp_path), "--release-version", "0"])
    assert "RetroAchievements" in capsys.readouterr().err
