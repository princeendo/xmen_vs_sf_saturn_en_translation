r"""EXP-0065: sample screens of the English attract captions for the user's choice.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/samples.py SNAPS BANNER SATURN OUT

SNAPS holds the arcade snapshots (`stitch_banner.py`'s run), BANNER the
respelled banner, SATURN a Saturn caption screenshot (352 x 240) whose
``PRESS START BUTTON`` row is kept. Each arcade caption (frames 1,440, 1,800,
2,055: rows 0-199, columns 16-367) is pasted at Saturn y = SATURN_TOP over
the Saturn background, and the banner's first 352 columns at the arcade
banner's height; once in the arcade's colours (A) and once with the seven
letter shades mapped onto the Saturn caption palette's grey ramp (B). Writes
``OUT/a<n>.png``, ``OUT/b<n>.png`` and the full banner in both treatments.
Game-derived: OUT goes under ``local/``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

W, H = 352, 240
SATURN_TOP = 12
BACKGROUND = bytes.fromhex("111111")
GREYS = {  # arcade shade -> Saturn caption palette grey (index 15 down to 9)
    "ffffff": "f8f8f8",
    "ffff99": "e8e8e8",
    "ffee00": "d8d8d8",
    "ffcc00": "c8c8c8",
    "ffaa00": "b8b8b8",
    "ff8811": "a8a8a8",
    "dd6622": "989898",
}


def read(path: Path, crop: str | None = None) -> tuple[int, int, bytes]:
    probe = subprocess.run(
        [
            *("ffprobe", "-v", "error", "-show_entries", "stream=width,height"),
            *("-of", "csv=p=0", str(path)),
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    width, height = (int(v) for v in probe.split(","))
    args = ["ffmpeg", "-loglevel", "error", "-i", str(path)]
    if crop:
        args += ["-vf", f"crop={crop}"]
        width, height = (int(v) for v in crop.split(":")[:2])
    raw = subprocess.run(
        [*args, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return width, height, raw


def write(path: Path, width: int, height: int, raw: bytes) -> None:
    subprocess.run(
        [
            *(
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
            ),
            *("-s", f"{width}x{height}", "-i", "-", str(path)),
        ],
        input=raw,
        check=True,
    )


def grey(raw: bytes) -> bytes:
    out = bytearray(raw)
    for i in range(0, len(raw), 3):
        shade = GREYS.get(raw[i : i + 3].hex())
        if shade:
            out[i : i + 3] = bytes.fromhex(shade)
    return bytes(out)


def screen(base: bytes, art: tuple[int, int, bytes], top: int) -> bytes:
    width, height, raw = art
    out = bytearray(base)
    for y in range(min(height, 210 - top)):
        row = raw[y * width * 3 : (y * width + min(width, W)) * 3]
        start = ((top + y) * W) * 3
        out[start : start + len(row)] = row
    return bytes(out)


def main(snaps: Path, banner: Path, saturn: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    _, _, base = read(saturn)
    blank = bytearray(base)
    blank[: 210 * W * 3] = BACKGROUND * (210 * W)
    arts = [
        read(snaps / f"xmvsfu_f{f:05d}.png", "352:200:16:0") for f in (1440, 1800, 2055)
    ]
    bw, bh, braw = read(banner)
    strip = b"".join(braw[y * bw * 3 : (y * bw + W) * 3] for y in range(bh))
    arts.append((W, bh, strip))
    tops = [SATURN_TOP] * 3 + [96]
    for n, (art, top) in enumerate(zip(arts, tops, strict=True), start=1):
        width, height, raw = art
        write(out / f"a{n}.png", W, H, screen(bytes(blank), art, top))
        write(
            out / f"b{n}.png",
            W,
            H,
            screen(bytes(blank), (width, height, grey(raw)), top),
        )
    write(out / "banner_a.png", bw, bh, braw)
    write(out / "banner_b.png", bw, bh, grey(braw))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), Path(a[2]), Path(a[3])))
