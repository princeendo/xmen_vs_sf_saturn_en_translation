from __future__ import annotations

from pathlib import Path

import pytest

from tools.mednafen.home import (
    PROJECT_SETTINGS,
    QUIET_SETTINGS,
    apply_settings,
    configure,
)

KEYS = {**PROJECT_SETTINGS, **QUIET_SETTINGS}


def generated_config(path: Path, overrides: dict[str, str] | None = None) -> Path:
    """A synthetic Mednafen configuration with every pinned key present."""
    values = {key: "default" for key in KEYS} | (overrides or {})
    body = [";VERSION 1.32.1", ";comment \x85 kept"]
    body += [f"{key} {value}" for key, value in sorted(values.items())]
    body += ["other.setting 7", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("\n".join(body).encode("latin-1"))
    return path


def test_apply_settings_rewrites_only_named_lines(tmp_path: Path) -> None:
    config = generated_config(tmp_path / "mednafen.cfg", {"autosave": "0"})

    changed = apply_settings(config, {"autosave": "0", "ss.cart": "auto"})

    assert changed == ["ss.cart"]
    lines = config.read_bytes().decode("latin-1").split("\n")
    assert "ss.cart auto" in lines
    assert "other.setting 7" in lines
    assert ";comment \x85 kept" in lines


def test_apply_settings_refuses_unknown_key(tmp_path: Path) -> None:
    config = generated_config(tmp_path / "mednafen.cfg")
    before = config.read_bytes()

    with pytest.raises(KeyError, match=r"no\.such"):
        apply_settings(config, {"no.such": "1"})

    assert config.read_bytes() == before


def test_configure_creates_quiet_home_sharing_firmware(tmp_path: Path) -> None:
    home = tmp_path / "mednafen"
    generated_config(home / "mednafen.cfg")
    (home / "firmware").mkdir()
    quiet = tmp_path / "mednafen_quiet"

    configure(home, quiet)

    home_lines = (home / "mednafen.cfg").read_text("latin-1").split("\n")
    quiet_lines = (quiet / "mednafen.cfg").read_text("latin-1").split("\n")
    assert "ss.bios_jp sega_101.bin" in home_lines
    assert "sound.volume default" in home_lines
    assert "sound.volume 0" in quiet_lines
    assert "ss.bios_jp sega_101.bin" in quiet_lines
    assert (quiet / "firmware").resolve() == (home / "firmware").resolve()
    assert configure(home, quiet) == {str(home): [], str(quiet): []}
