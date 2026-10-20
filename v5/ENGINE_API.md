# v5 Engine API

The contract between a **UI** and the **engine**. A UI is any static web
page (HTML/CSS/JS) that talks only to these endpoints. The engine is v4's
geometry pipeline, which a UI never touches.

Two implementations share this contract:

- **Today:** `v5/server.py`, a local Python server. Run your own UI with:
  ```
  v4/.venv/bin/python3 v5/server.py --ui path/to/your-ui --open
  ```
  The folder must contain an `index.html`. It is served at
  `http://127.0.0.1:8090/app/`, so use relative URLs for your own assets and
  absolute `/api/...` URLs for the engine.
- **In the browser:** `v5/ui/engine_browser.js`, the same methods with v4
  running in a Web Worker (Pyodide + manifold WebAssembly). This is how the
  hosted site works with no server. A UI can import it directly.

The reference UI (`v5/ui/`) keeps every engine call behind `engine.js`, which
picks `engine_http.js` (local server) or `engine_browser.js` (in-browser). Copy
those three into your UI and you have the whole API as JavaScript functions,
on either engine.

The browser engine adds a few things a UI should use:
- `fontData(path)` returns font bytes (it has no font URLs).
- `addFont(name, arrayBuffer)` adds a font the user picked.
- `onStatus(fn)` reports boot progress.
- `config()` results carry `font_substitutions` for fonts that aren't
  available in the browser.

All bodies are JSON. Errors come back as HTTP 4xx with `{"detail": "message"}`.

---

## Concepts

- **machine**: a key like `selectric12`, `blickensderfer`, `hammond`
  (see `GET /api/machines`).
- **master config**: `v4/config/<machine>.yaml`. It is never written.
- **running config**: `<machine>.running.yaml` next to the master. All edits
  land here, and every build reads it. It is shared with v4's `tune.py`.
- **field**: one setting. A UI renders fields from records; it never
  hardcodes them. The engine knows which fields each machine has.
- **job**: a build or tool run. Its output streams back line by line. Only one
  job runs at a time.

### Field record

```json
{
  "key": "size_mm",                 // id used when saving
  "path": ["font", "size_mm"],      // where it lives in the config
  "type": "float",                  // bool | int | float | str | floatlist | textblock
  "label": "Font size (mm)",
  "help": "Em-square size, matches OpenSCAD text(size=).",
  "value": 3.7,
  "options": [],                    // non-empty => pick one of {label, value} (values are strings)
  "list": false,                    // true => edited by a dedicated editor (layout rows), skip it
  "extra": true                     // present on controls tune.py built by hand; render like any other
}
```

How the reference UI treats these (your UI may differ):

- **Font files:** keys `path`, `font2_path`, `font_path`, `label_font_path`
  and `legend_font_path` are font file paths. The reference UI shows them as
  specimens drawn in the font itself.
- **Number steps:** floats step by 0.1, or finer when the current value
  already has more decimals.
- **Alignment:** options that are all of `left` / `center` / `right` /
  `justify` are drawn as paragraph-alignment buttons.

### Section record

```json
{ "section": "Font & Alignment",
  "intro": { "text": "...", "level": "info" | "advanced" } | null,
  "fields": [ /* field records */ ] }
```

`level: "advanced"` marks high-risk settings, such as real machine dimensions
and row baselines. Make those look dangerous.

---

## Endpoints

### Machines and config

| Method & path | Body | Returns |
|---|---|---|
| `GET /api/machines` | — | `{groups: [{group, machines: [{key, label, available}]}]}`. Groups are Cylinders, Shuttles, Spheres and Slugs. |
| `GET /api/config/{m}` | — | The **machine document** (below). Creates or migrates the running copy if needed. |
| `PUT /api/config/{m}` | `{values: {key: value}, rows?: [str], preset?: str}` | Machine document plus `{changed, errors: [str]}`. Only changed values are written. Comments in the YAML are preserved. |
| `POST /api/config/{m}/reset` | — | Machine document, after the running copy is replaced with the master. |
| `GET /api/configs/{m}` | — | `{current, default, configs: [{path, label, kind}]}`: other masters for this machine (variants, saved copies). |
| `POST /api/config/{m}/open` | `{path}` | Machine document, after switching which master `{m}` uses. |

**Machine document:**

```json
{
  "machine": "selectric12", "label": "Selectric I/II",
  "cfg": { /* the whole running config as JSON */ },
  "schema": [ /* section records, in display order */ ],
  "presets": { "US": ["row1", "row2", ...], ... },   // layout presets, may be {}
  "current_preset": "US" | null,                     // preset whose rows equal cfg.layout.rows
  "layout_help": "str" | null,
  "fixed_row_lengths": true,     // rows must keep their exact length (Selectrics)
  "row_cap": 28 | null,          // max chars per row (cylinder/shuttle machines)
  "targets": [{value, label}],   // build targets this machine offers
  "target": "element",           // the current one
  "export_name": "selectric12_FreeSans_2.4mm",   // file name stem for downloads: machine_font_size[_target]; add date/time + extension
  "warning": {short, long} | null,
  "migrated": ["section.key", ...],   // settings just added from the master
  "running_path": "...", "master_path": "..."
}
```

**Layout rows:** these are `cfg.layout.rows`, an array of strings with one per
keyboard row. To change them, send `rows` in the PUT.
- If the rows are a preset, also send `preset: "<name>"`. The engine then sets
  the matching hemisphere map (Selectric) or baselines (Hammond), exactly as
  tune.py does.
- Rows that break `fixed_row_lengths` are refused. The refusal is reported in
  `errors`, and every other change in the PUT still saves.

### Fonts

| Method & path | Body | Returns |
|---|---|---|
| `GET /api/fonts` | — | `[{path, family, style}]`: every installed font (thousands; filter client-side). |
| `GET /api/font?path=` | — | The font file itself. Use it with `new FontFace(name, "url(...)")`. |
| `POST /api/outlines` | `{font, chars}` | `{upem, ascender, descender, glyphs: {char: {d, adv} \| null}}`. `d` is SVG path data in font units with y pointing up, so flip it when drawing. Use this when the browser refuses a font file (`FontFace.load()` rejects); FreeType, and therefore the build, often reads such fonts fine. |
| `POST /api/glyphs` | `{font, chars, font2?, font2_chars?}` | `{status: {char: "ok"\|"missing"\|"blank"}, unused: {letters\|digits/numbers\|punctuation\|symbols: [char]}}`. `missing` and `blank` would build as an empty slot or a box. `unused` lists glyphs the font has that the character set doesn't use, as swap candidates. |
| `GET /api/default-font-dir` | — | `{path}`: a font folder that exists on this machine. |

### Jobs (streamed)

Two endpoints start a job:
- `POST /api/build/{m}` with body `{fast: bool, target: str, cross_section?: bool, cross_section_angle?: number, cut_bodies?: bool}`.
  - `fast: true` means Preview (no draft angle, seconds). `false` means Render (real draft angle, slower).
  - `target` is one of the machine document's `targets`. It is also saved to the config.
- `POST /api/tool/{m}` with body `{tool: "type_test" | "legend" | "coverage" | "coverage_current", chars?, font_dir?, deep?}`.

**Response:** `application/x-ndjson`, one JSON object per line, until the job
finishes:

```
{"line": "a complete log line"}
{"partial": "AssembleMinkowski: [12/88] 'r'..."}   // unterminated progress line, replaced by the next event
{"done": 0}                                          // exit code: 0 ok, >0 failed, <0 stopped
```

- **Progress:** take it from any `[n/total]` in `line` or `partial`. Those
  only count inside loops, so for a smooth bar that tracks time, use
  `v5/ui/progress.js`: it learns each job's timeline from its previous run.
- **Warnings:** lines containing `WARNING` are things the user should see.
  Examples: characters missing from the font, overhang islands, unprintable
  rows.
- **Read it** with `fetch()` and `response.body.getReader()`, splitting on
  `\n`. See `stream()` in `v5/ui/engine.js`.

| Method & path | Returns |
|---|---|
| `POST /api/build-cancel` | `{cancelled: bool}`: stops the running job. |
| `GET /api/stl/{m}` | The last built STL, binary. Add `?t=<now>` to bypass caching. Z is the build direction. |
| `GET /api/legend/{m}` | The last generated legend SVG. |
| `GET /api/coverage-report` | Markdown report of the last coverage job. |
| `POST /api/save-copy/{m}` with body `{last_build?}` | `{path}`: a timestamped STL plus a `.yaml` copy of the config, written to `v4/output/saved/`. |

### Font profiles

Saved sets of Font & Alignment values, shared across machines.

| Method & path | Body | Returns |
|---|---|---|
| `GET /api/profiles/{m}` | — | `[{name, values: {"section.key": value}, skipped, unset, active}]`. `active` means the current settings match the profile. |
| `POST /api/profiles/{m}` | `{name}` | The updated list. Saves the current settings as a profile, so save the config first. |
| `POST /api/profiles/{m}/rename` | `{old, new}` | The updated list. |
| `POST /api/profiles/{m}/delete` | `{name}` | The updated list. |

To apply a profile, the UI maps each `values` path to the field with that
`path` and saves the result like any other edit. The engine has no "apply"
call.

---

## Rules for a UI

1. **Never hardcode fields.** Render whatever `schema` returns. Machines
   differ, and fields get added.
2. **Save before you build.** Builds read the running config from disk.
3. **Treat `advanced` sections as dangerous.** They hold real machine
   measurements.
4. **Only one job at a time.** A second start returns 409.
5. **Nothing here needs a framework.** The reference UI uses Vue and
   three.js from a CDN, but plain JS, React or Svelte all work. Anything
   that builds to static files is fine.
