r"""EXP-0059: MAME timelines for slot 11 against slot 18 (Alpha Chun-Li), US set.

Copied from the subagent's ``local/spec002/arcade/make_tl.py`` (SPEC-002); the
``b`` variants were separate files there and are generated here.

Run from the repository root:

    python3 research/experiments/EXP-0059/arcade/make_tl.py OUT VARIANT [END]

VARIANT is ``s11``, ``s18``, ``s11b`` or ``s18b``.

The route is `EXP-0048`'s slot 11 route (``make_timeline.py``): partner
default, language English, moves ``uur``, button 1 at frame 1820, the partner's
button from 1900, and CPU vitality ``0xFF4610``/``0xFF4E10`` set to 0 every 20
frames from 3750. ``s18`` adds only ``1810 press 25 1 Player Start`` (the
``r11_start`` method of `EXP-0058`, which gave character word ``0x24``). The
logging below is added; nothing else is written to RAM. The ``b`` variants
add the ending scene jump-table breakpoints and tap.
"""

import sys

SCENE = [
    "3000 debug bpset 6e154,1,{printf "
    '"SCENEJMP slot=%x d1=%x target=%x",b@ff511a,d1,6e156+(d1&ffff);g}',
    '3000 debug bpset 6deda,1,{printf "MUSIC? slot=%x d1=%x",b@ff511a,d1;g}',
    '3000 debug bpset 6f800,1,{printf "PALTAB slot=%x a0=%x",b@ff511a,a0;g}',
    "3000 logopreads 0x06E158 0x06E17F {run}/op_scene_jumptable.txt",
]
LOGS = [
    "2500 logwrites 0xFF4052 {run}/w_ff4052.txt",
    "2500 logwrites 0xFF511A {run}/w_ff511a.txt",
    "2500 logwrites 0xFF5082 {run}/w_ff5082.txt",
    "3000 logreads 0x17E19C 0x17E3FB {run}/ptr_reads.txt",
    "3000 logreads 0x17E3FC 0x19A7FF {run}/rec_reads.txt",
    "3000 logopreads 0x04F3E2 0x04F429 {run}/op_quote_tables.txt",
    "3000 logopreads 0x06F8AA 0x06F8F5 {run}/op_ending_scripts.txt",
    "3000 debug bpset 4f396,1,{printf "
    '"SEL d1=%x fix=%x cnt=%x lang=%x size=%x c4052=%x c4452=%x",'
    "d1,b@ff5083,b@ff5081,w@ff547a,w@ff5478,w@ff4052,w@ff4452;g}",
    '3000 debug bpset 4f3c6,1,{printf "IDX d0=%x",d0;g}',
    "3000 debug bpset 4f3da,1,{printf "
    '"BASE a1=%x d1=%x ptr@%x=%08x",a1,d1,(a1+d1)&ffffff,d@(a1+d1);g}',
    '3000 debug bpset 4f590,1,{printf "REC %08x size=%x",a2+d0,d1;g}',
    "3000 debug bpset f846,1,{printf "
    '"ENDSLOT d0=%x c4052=%x c4452=%x side=%x",d0,w@ff4052,w@ff4452,b@ff5005;g}',
    '3000 debug bpset 6f904,1,{printf "ENDSCRIPT slot=%x a0=%x",b@ff511a,a0;g}',
    "3000 debug bpset 4f53c,1,{printf "
    '"ENDTEXT a1=%x d1=%x ptr@%x=%08x",a1,d1,(a1+d1)&ffffff,d@(a1+d1);g}',
]


def timeline(variant: str, end: int) -> str:
    scene = variant.endswith("b")
    slot = variant.removesuffix("b")
    if slot not in ("s11", "s18"):
        raise SystemExit(f"unknown variant {variant}")
    alpha = " + Start held (Alpha)" if slot == "s18" else ""
    lines = [
        f"# spec002 {slot}: slot 11 route{alpha}",
        "1000 repeat 4 30 8 Coin 1",
        "1200 repeat 10 60 8 1 Player Start",
        "1700 press 8 P1 Up",
        "1740 press 8 P1 Up",
        "1780 press 8 P1 Right",
    ]
    if slot == "s18":
        lines.append("1810 press 25 1 Player Start")
    lines += ["1820 press 8 P1 Button 1", "1900 repeat 20 30 8 P1 Button 1"]
    for f in range(3750, end, 20):
        lines += [f"{f} debug do w@ff4610=0", f"{f} debug do w@ff4e10=0"]
    lines += LOGS + (SCENE if scene else [])
    lines += [f"{f} snap" for f in range(3000, end, 60)]
    return "\n".join([*lines, f"{end} exit", ""])


if __name__ == "__main__":
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 17500
    with open(sys.argv[1], "w") as out:
        out.write(timeline(sys.argv[2], end))
