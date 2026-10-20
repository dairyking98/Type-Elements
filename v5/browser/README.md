# v5 in-browser engine (phase 2)

v4's own Python (`generate.py` + `lib/`, unmodified) running inside a browser
tab: no install, no server doing the work. This is the engine a GitHub Pages
copy of the app will use.

## How it works

- **Pyodide** (Python 3.14 compiled to WebAssembly) runs the code. It ships
  numpy, scipy, shapely, pyyaml, networkx and fontTools. trimesh installs as a
  pure-Python wheel.
- **Three adapters** in `py/` stand in for libraries that have no WebAssembly
  build. Each covers exactly the surface v4 (and trimesh) actually call:

  | adapter | replaces | built on | checked against the real library |
  |---|---|---|---|
  | `freetype.py` | freetype-py | fontTools | identical points, tags, contours and advances. 4 fonts (TrueType + CFF) x 90 characters |
  | `triangle.py` | Triangle (`'p'` mode) | shapely constrained Delaunay | identical vertices and area. 86 glyphs, worst area difference 5e-16 |
  | `manifold3d.py` | manifold3d wheel | manifold-3d 3.5.4 WebAssembly | whole-build output identical (below) |

- **Files:** v4's files and the fonts a config uses are written into
  Pyodide's in-memory filesystem *at their real paths*, so configs work
  unchanged.
- **Minkowski worker pool:** Minkowski sums can run on a pool of Web Workers
  (see [PERFORMANCE](../docs/PERFORMANCE.md)). The build runs twice:
  1. Every Minkowski sum is recorded instead of computed, and the glyph passes
     through un-drafted so the rest of the build continues.
  2. The pool computes all the recorded sums in parallel.
  3. The build reruns and each sum is answered from the pool's results, in
     order.

  This needs no change to v4 at all; it's a hook in the `manifold3d`
  adapter.

## Results

Selectric I/II, measured 2026-10-20 on the laptop in PERFORMANCE.

| | native (Python) | browser | output |
|---|---|---|---|
| engine load (first visit downloads ~30 MB, cached after) | - | 6.4 s | - |
| Preview | 2.6 s | 6.7 s | **identical**: verts 50334, faces 100864, volume 7900.804 mm3 |
| Render, one thread | 32.0 s | 96.0 s | **identical**: verts 76312, faces 153000, volume 8054.660 mm3 |
| **Render, 16-worker pool** | 32.0 s | **28.3 s** | volume **identical** (8054.660 mm3); 2 fewer vertices (76310), see note |

Pool breakdown:

| step | time |
|---|---|
| pass 1, Minkowski recorded | 7.8 s |
| 88 sums on 16 workers | 11.3 s |
| pass 2, results replayed | 9.1 s |

**What this shows:**

- v4's own code runs unmodified in a browser tab, and its output matches the
  native build: the same summary line v4's hard-gate check compares.
- A full Selectric Render with the worker pool is **faster in the browser than
  native Python**.

**The 2-vertex note:** sums that come back from workers are rebuilt from plain
meshes, which drops a little of manifold's internal vertex bookkeeping. The
solid and its volume are unchanged. Passing manifold's merge vectors back
with each result would close this gap.

**Next:** run Pyodide itself inside a Web Worker, so the page stays responsive
during the two build passes (here they block the tab). Then wire this up as
the app's in-browser engine.

## Run it

```
python3 v5/browser/make_manifest.py selectric12      # lists v4 files, copies the config's fonts to _fonts/
python3 -m http.server 8093 --bind 127.0.0.1          # from the REPO ROOT
#   http://127.0.0.1:8093/v5/browser/phase2.html
```

`phase2.html` is a measurement harness, not the app. The app's `engine.js`
gets an in-browser implementation built on this next.
