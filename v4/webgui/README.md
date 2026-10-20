# Web UI (branch `web-gui`)

The replacement for `tune.py`: a **static web app** (`webgui/static/`, plain
HTML/CSS/JS, no build step) plus a small **local engine server**
(`webgui/server.py`, FastAPI) that runs the existing pipeline.

```
.venv/bin/python3 webgui/server.py --open        # Linux   -> http://127.0.0.1:8090
.venv\Scripts\python webgui\server.py --open     # Windows
```

Options: `--config-dir DIR` (scratch config copies for testing), `--port`,
`--host` (default 127.0.0.1 = this computer only).

## Why this shape

End goal: publish the UI on GitHub Pages and run everything **in the
visitor's browser** - no server. `static/engine.js` is the only file that
knows where the work happens; today it talks HTTP to `server.py`, later it
talks to an in-browser engine with the same methods:

- Pyodide (Python in WebAssembly) ships numpy, scipy, shapely, pyyaml,
  fontTools.
- manifold has an official WebAssembly build with `minkowskiSum`
  (manifold-3d 3.4+), replacing the manifold3d Python wheel.
- Three dependencies have no browser build and need small adapter modules:
  freetype-py (-> fontTools), triangle (-> shapely/earcut), python-fcl.
- Fonts come from the visitor's own files (browser file picker), never
  uploaded anywhere.

## What the server reuses

`server.py` imports tune.py for its field tables, comment-preserving YAML
patchers and running-config migration, and runs `generate.py`,
`type_test.py`, `generate_legend.py` and `font_coverage.py` as subprocesses
with exactly the flags tune.py uses. Both front ends read and write the same
`config/<machine>.running.yaml`, so they can be used side by side.

## UI map

Settings regrouped by task instead of tune.py's 17 tabs:

| Page | Contains |
|---|---|
| Typeface | font, font 2 (specimens drawn in the real font), size, alignment, font profiles |
| Layout | keyboard grid in the real font, missing characters flagged, click a slot to swap (including the font's unused glyphs), presets (sets hemisphere map / Hammond baselines like tune.py), row baselines/cutouts |
| Element | Element, Cosmetics, bands, Rib, Ticks |
| Logo & label | Logo, Label (font specimens show the actual logo/label text) |
| Print prep | resin supports, orientation, Hammond horizontal method, Hammond Split halves, Resin |
| Quality | facet counts |
| Tests & tools | Calibration and Shaft gauge (with build buttons), Type test plate, Legend sheet (preview + download), Font coverage |

Always visible: 3D viewer, build target, Preview / Render / Stop, progress,
warnings summary, log, Download STL, Save a copy (timestamped STL + config
sidecar in `output/saved/`). Search (`/`) across every setting. `Ctrl+S`
saves, `Ctrl+Enter` previews. Light/dark. Works down to phone width.

## Not done yet

- Browse to a different master config (tune.py's Browse).
- In-browser engine (the GitHub Pages step).
- Single-file packaging.
