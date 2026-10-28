"""Cold-boot an image in stock Mednafen with no input and keep per-second frames.

Stock Mednafen has no scripted screenshot, so the run records its own video
(`-qtrecord`, default CamStudio codec, no setting changed) and is stopped with
SIGTERM after a fixed time; Mednafen catches the signal and closes the file.
ffmpeg then scales one frame per second to `--size` (the recording is a wide
common-multiple canvas, not native resolution) and builds a contact sheet. The
video is deleted afterwards unless `--keep-video`; its size and SHA-256 are kept
in `run.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

MEDNAFEN = Path("vendor/mednafen/build/src/mednafen")
QUIET_HOME = Path("local/mednafen_quiet")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def boot(
    image: Path, out: Path, seconds: float, home: Path, mednafen: Path
) -> dict[str, object]:
    """Run one cold boot; return the run record (also written to run.json)."""
    out.mkdir(parents=True, exist_ok=False)
    video, log = out / "boot.mov", out / "mednafen.log"
    env = {**os.environ, "MEDNAFEN_HOME": str(home.resolve())}
    command = [str(mednafen), "-qtrecord", str(video), str(image)]
    with log.open("wb") as handle:
        process = subprocess.Popen(
            command, env=env, stdout=handle, stderr=subprocess.STDOUT
        )
        started = time.time()
        time.sleep(seconds)
        process.send_signal(signal.SIGTERM)
        code = process.wait(timeout=30)
    return {
        "command": command,
        "home": str(home),
        "seconds": seconds,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "exit_code": code,
        "log_sha256": sha256(log),
        "video_size": video.stat().st_size,
        "video_sha256": sha256(video),
    }


def extract_frames(out: Path, size: str, columns: int) -> list[dict[str, str]]:
    """Write frames/NNN.png (one per second) and sheet-K.png contact sheets."""
    frames = out / "frames"
    frames.mkdir()
    video = out / "boot.mov"
    scale = f"scale={size.replace('x', ':')}:flags=area"
    ffmpeg = ["ffmpeg", "-v", "error", "-i", str(video), "-an"]
    subprocess.run(
        [*ffmpeg, "-vf", f"fps=1,{scale}", str(frames / "%03d.png")], check=True
    )
    tile = f"tile={columns}x{columns}"
    subprocess.run(
        [*ffmpeg, "-vf", f"fps=1,{scale},{tile}", str(out / "sheet-%d.png")],
        check=True,
    )
    return [
        {"file": str(path.relative_to(out)), "sha256": sha256(path)}
        for path in sorted([*frames.glob("*.png"), *out.glob("sheet-*.png")])
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="disc image .cue")
    parser.add_argument("out", type=Path, help="new output folder")
    parser.add_argument("--seconds", type=float, default=90.0)
    parser.add_argument("--home", type=Path, default=QUIET_HOME)
    parser.add_argument("--mednafen", type=Path, default=MEDNAFEN)
    parser.add_argument("--size", default="352x240", help="frame size WxH")
    parser.add_argument("--columns", type=int, default=5, help="sheet is NxN")
    parser.add_argument("--keep-video", action="store_true")
    args = parser.parse_args(argv)

    record = boot(args.image, args.out, args.seconds, args.home, args.mednafen)
    record["frames"] = extract_frames(args.out, args.size, args.columns)
    if not args.keep_video:
        (args.out / "boot.mov").unlink()
    (args.out / "run.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k != "frames"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
