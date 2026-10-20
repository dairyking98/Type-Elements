# Type Elements v5

v5 is the app around v4's geometry engine: a **swappable web UI** on top of a
documented **engine API**. v4 (the geometry pipeline) is unchanged; v5 never
edits it.

```
v4/.venv/bin/python3 v5/server.py --open        # Linux   -> http://127.0.0.1:8090
v4\.venv\Scripts\python v5\server.py --open     # Windows
```

| Path | What it is |
|---|---|
| `v5/server.py` | local engine server (FastAPI) - the API below, driving v4 |
| `v5/ENGINE_API.md` | **the contract** - every endpoint, field record, the job stream |
| `v5/ui/` | reference UI (static, no build step); `engine.js` is its only API client |

Options: `--ui DIR` (serve a different front end), `--config-dir DIR`
(scratch config copies for testing), `--port`, `--host` (default 127.0.0.1 =
this computer only). First time: `v4/.venv/bin/python3 -m pip install fastapi uvicorn`.

**Try it:** [type-elements.leonardchau.com/app/](https://type-elements.leonardchau.com/app/)
(the hosted UI - it connects to the engine on your computer until the
in-browser engine lands).

## Performance

Rendering in the browser is not the slow option: spread across Web Workers,
the slowest stage of a Selectric Render runs **faster than native Python**
(16.7 s vs 30.4 s on an 8-core laptop), and two workers already halve it.
Chart, method and caveats: [PERFORMANCE](docs/PERFORMANCE.md).

## Writing your own UI

Make a folder with an `index.html`, copy `v5/ui/engine.js` in, build whatever
you like against [ENGINE_API.md](ENGINE_API.md), run with `--ui your-folder`.
You can't break the geometry from there - the engine owns all of it.

## Why this shape

End goal: publish the UI on GitHub Pages and run everything **in the
visitor's browser** - no server. `ui/engine.js` is the only file that
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

`server.py` imports v4's tune.py for its field tables, comment-preserving YAML
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

## Status and roadmap

| | |
|---|---|
| done | engine API + local server; reference UI covering every v4 parameter; hosted UI at /app/; Minkowski-in-WebAssembly spike (worker pool beats native) |
| **now - phase 2** | v4's Python running in the page (Pyodide) with the worker-pool Minkowski; then an engine switch: *in-browser* (no install, default) or *local engine* (desktop) |
| later | single-file desktop launcher; vendored libraries for offline use |
