# Web GUI (branch `web-gui`)

A local web app to replace `tune.py`: Python backend (NiceGUI on FastAPI),
UI in the browser. Same on Linux and Windows, renders every Unicode
character, 3D preview built in (no f3d).

```
.venv/bin/python3 webgui/app.py            # Linux  - opens http://127.0.0.1:8090
.venv\Scripts\python webgui\app.py         # Windows
```

Options: `--machine selectric12` (open with), `--port`, `--no-browser`,
`--host` (default 127.0.0.1 = this machine only), `--config-dir DIR`
(test against scratch config copies, never the real files).

It reads and writes the same `config/<machine>.running.yaml` files tune.py
does, with tune.py's own field tables and YAML patchers (`import tune`), and
builds with the same `generate.py` subprocess. Both front ends can be used
side by side while this grows.

## Done (slice 1, 2026-10-19)

- Machine picker; every scalar settings field from tune.py's per-machine
  tables, tooltips from their help text; Save.
- Preview (no Minkowski) / Render (Minkowski) of the element target: live
  log with WARNING lines highlighted, progress bar from the `[n/total]`
  lines, elapsed time.
- 3D viewer of the built STL, refreshed after each build.
- Layout grid drawn **in the configured font**, characters the font lacks
  flagged red (same check as the build-time "Characters not found").

## Next

1. Layout editing in the grid (click a slot, pick a character — including
   the font's unused glyphs as swap candidates), presets, hemisphere maps.
2. Build targets: gauge, calibration, Hammond rib/normal, cross-section,
   cut bodies, resin on/off.
3. Font picker (installed fonts list via `lib/system_fonts.py`), font 2,
   font profiles.
4. Font Coverage, Type Test, Legend tabs.
5. Move the field tables out of tune.py into a `lib/` module both import.
6. Native window + single-exe packaging (NiceGUI `native=True` / PyInstaller)
   — see `PACKAGING_PLAN.md`; f3d download step no longer needed.
