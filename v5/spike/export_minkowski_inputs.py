#!/usr/bin/env python3
"""
Spike, step 1: capture the exact Minkowski-sum inputs v4 uses for a real
Selectric ball (every character's platen-cut glyph prism + its draft cone,
in the canonical frame SingleMinkowskiChar sums them in), time each sum
natively, and write them to minkowski_inputs.json for the browser
benchmark (bench.html) to replay through manifold's WebAssembly build.

    v4/.venv/bin/python3 v5/spike/export_minkowski_inputs.py [config]

Throwaway measurement code - not part of the app.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V4 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "v4")
sys.path.insert(0, os.path.join(V4, "lib"))
os.chdir(V4)

import numpy as np  # noqa: E402
import selectric12  # noqa: E402
import spherical_machine as sm  # noqa: E402
from manifold3d import Manifold, Mesh  # noqa: E402

cfg = sys.argv[1] if len(sys.argv) > 1 else os.path.join(V4, "config", "selectric12.yaml")
selectric12.configure(cfg)

# SingleMinkowskiChar converts, in order: the positioned scalloped glyph, the
# glyph rotated into the cone's canonical frame, the cone hull, the result.
# Calls 2 and 3 of each character are exactly minkowski_sum's two operands.
calls = []
real = sm._to_manifold
sm._to_manifold = lambda mesh: (calls.append((np.asarray(mesh.vertices, np.float32), np.asarray(mesh.faces, np.uint32))), real(mesh))[1]

pairs = []
orig_single = sm.SingleMinkowskiChar


def capture(*a, **k):
    calls.clear()
    out = orig_single(*a, **k)
    if len(calls) >= 3:
        pairs.append((a[0], calls[1], calls[2]))
    return out


sm.SingleMinkowskiChar = capture
sm.AssembleMinkowski(flatness_tolerance_mm=sm.DEFAULT_FLATNESS_TOLERANCE_MM, minkowski_enabled=True)

records, native_total = [], 0.0
for ch, (gv, gf), (cv, cf) in pairs:
    a = Manifold(mesh=Mesh(vert_properties=gv, tri_verts=gf))
    b = Manifold(mesh=Mesh(vert_properties=cv, tri_verts=cf))
    t0 = time.perf_counter()
    r = a.minkowski_sum(b)
    _ = r.num_tri()
    dt = time.perf_counter() - t0
    native_total += dt
    records.append({"char": ch, "glyph": {"v": gv.ravel().round(6).tolist(), "f": gf.ravel().tolist()},
                    "cone": {"v": cv.ravel().round(6).tolist(), "f": cf.ravel().tolist()},
                    "native_s": round(dt, 4), "native_tris": r.num_tri(), "native_vol": round(r.volume(), 6)})

out = os.path.join(HERE, "minkowski_inputs.json")
with open(out, "w") as f:
    json.dump({"config": os.path.basename(cfg), "flatness_tolerance_mm": sm.DEFAULT_FLATNESS_TOLERANCE_MM,
               "native_total_s": round(native_total, 3), "count": len(records), "pairs": records}, f)
print(f"\n{len(records)} Minkowski sums, native total {native_total:.2f}s "
      f"(threads: manifold default) -> {out} ({os.path.getsize(out) / 1e6:.1f} MB)")
