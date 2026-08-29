#!/usr/bin/env python3
"""Smoke tests for the Looper Inkscape extension (no Inkscape needed)."""
import io
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "..", "looper.py")
SVG = os.path.join(HERE, "test.svg")

sys.path.insert(0, os.path.join(HERE, ".."))
from lxml import etree

SVGNS = "{http://www.w3.org/2000/svg}"
FAILS = []


def run(args):
    cmd = [sys.executable, EXT] + args + [SVG]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError("exit {}: {}".format(res.returncode, res.stderr))
    if res.stderr.strip():
        print("  stderr:", res.stderr.strip())
    return etree.fromstring(res.stdout.encode("utf-8"))


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print("[{}] {} {}".format(status, name, detail))
    if not cond:
        FAILS.append(name)


def get_looper_group(root):
    groups = [g for g in root.iter(SVGNS + "g")
              if (g.get("{http://www.inkscape.org/namespaces/inkscape}label")
                  or "").endswith("_looper")]
    return groups


def parse_matrix(s):
    m = re.match(r"matrix\(([^)]*)\)", s or "")
    if m:
        return [float(v) for v in re.split(r"[\s,]+", m.group(1).strip())]
    m = re.match(r"translate\(([^)]*)\)", s or "")
    if m:
        vals = [float(v) for v in re.split(r"[\s,]+", m.group(1).strip())]
        tx = vals[0]
        ty = vals[1] if len(vals) > 1 else 0.0
        return [1.0, 0.0, 0.0, 1.0, tx, ty]
    return None


# --- Test 1: default rotate-auto, 6 copies -------------------------------
root = run(["--id=rect1", "--copies=6"])
gs = get_looper_group(root)
check("t1 group created", len(gs) == 1)
copies = list(gs[0]) if gs else []
check("t1 copy count", len(copies) == 6, "got {}".format(len(copies)))
check("t1 first copy has no transform", copies and copies[0].get("transform") is None)
mat = parse_matrix(copies[1].get("transform")) if len(copies) > 1 else None
# copy 2 should be rotated by 360/6 = 60 degrees: a = cos(60) = 0.5
check("t1 copy2 rotated 60deg", mat is not None and abs(mat[0] - 0.5) < 1e-6
      and abs(mat[1] - math.sin(math.radians(60))) < 1e-6,
      str(mat))
check("t1 original untouched",
      next(root.iter(SVGNS + "rect")).get("style") in (None, ""))
check("t1 unique ids", len(set(c.get("id") for c in copies)) == len(copies))

# --- Test 2: grid 3x2 with fadeout opacity --------------------------------
root = run(["--id=rect1", "--grid_enable=true", "--grid_cols=3",
            "--grid_rows=2", "--grid_margin_x=100", "--grid_margin_y=80",
            "--rotate_enable=false", "--opacity_mode=fadeout"])
gs = get_looper_group(root)
copies = list(gs[0]) if gs else []
check("t2 grid copy count", len(copies) == 6, "got {}".format(len(copies)))
# copy 2 should be translated +100 in x (e=100, f=0)
mat = parse_matrix(copies[1].get("transform"))
check("t2 grid x spacing", mat and abs(mat[4] - 100) < 1e-6 and abs(mat[5]) < 1e-6, str(mat))
# copy 4 starts new row: e=0, f=80
mat = parse_matrix(copies[3].get("transform"))
check("t2 grid row wrap", mat and abs(mat[4]) < 1e-6 and abs(mat[5] - 80) < 1e-6, str(mat))
# fadeout opacities: i*100/6 decreasing: 83.33, 66.67, ... last = 0
op_first = copies[0].get("style", "")
op_last = copies[-1].get("style", "")
check("t2 fadeout first", "opacity:0.8333" in op_first, op_first)
check("t2 fadeout last", "opacity:0" in op_last, op_last)

# --- Test 3: move vertical + scale percentage on transformed group --------
root = run(["--id=grp1", "--copies=4", "--rotate_enable=false",
            "--move_enable=true", "--move_dir=vertical", "--move_inc=50",
            "--scale_enable=true", "--scale_mode=percentage",
            "--scale_pr=50", "--scale_dir=both"])
gs = get_looper_group(root)
copies = list(gs[0]) if gs else []
check("t3 copy count", len(copies) == 4, "got {}".format(len(copies)))
# first copy of transformed group keeps the original transform
mat = parse_matrix(copies[0].get("transform"))
c10, s10 = math.cos(math.radians(10)), math.sin(math.radians(10))
check("t3 copy1 preserves source transform",
      mat and abs(mat[0] - c10) < 1e-6 and abs(mat[1] - s10) < 1e-6
      and abs(mat[4] - 300) < 1e-6 and abs(mat[5] - 200) < 1e-6, str(mat))
# copy 2: scaled to 50% => overall scale factor 0.5 embedded in matrix
mat = parse_matrix(copies[1].get("transform"))
det = mat[0] * mat[3] - mat[1] * mat[2] if mat else 0
check("t3 copy2 scale 50%", abs(det - 0.25) < 1e-6, "det={}".format(det))
check("t3 children lost ids",
      all(ch.get("id") is None for c in copies for ch in c))

# --- Test 4: random modes with fixed seed are reproducible ----------------
args = ["--id=rect1", "--copies=5", "--rotate_enable=true",
        "--rotate_mode=manual", "--rotate_inc=random", "--angle=10",
        "--angle_rnd=20", "--opacity_mode=random", "--seed=42"]
r1 = run(args)
r2 = run(args)
t1 = [c.get("transform") for c in get_looper_group(r1)[0]]
t2 = [c.get("transform") for c in get_looper_group(r2)[0]]
check("t4 seeded runs identical", t1 == t2)

# --- Test 5: hide original + sinusoidal ----------------------------------
root = run(["--id=rect1", "--copies=10", "--rotate_mode=manual",
            "--rotate_inc=sin", "--sin_factor=5", "--hide_original=true"])
orig = next(r for r in root.iter(SVGNS + "rect") if r.get("id") == "rect1")
check("t5 original hidden", "display:none" in (orig.get("style") or ""))
check("t5 sin copies", len(get_looper_group(root)[0]) == 10)

# --- Test 6: error on no selection ----------------------------------------
res = subprocess.run([sys.executable, EXT, SVG], capture_output=True, text=True)
check("t6 no-selection message", "Select an object" in res.stderr, res.stderr.strip()[:60])

print()
if FAILS:
    print("FAILED:", ", ".join(FAILS))
    sys.exit(1)
print("All tests passed.")
