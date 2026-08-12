# Interactive tuner (`tune.py`)

Split out of `README.md` to keep it direct - see
[`README.md`](README.md) for setup, usage and the machine list.

## Interactive tuner (`tune.py`)

```
python3 tune.py                              # machine picker first
python3 tune.py config/blickensderfer.yaml   # skip the picker, load directly
```

A `textual` TUI for iterating on the config without hand-editing YAML or
re-running the CLI. Tabs: **Font & Alignment**, **Type Test**, **Resin**,
**Gauge**, **Build**, **Layout**, **Quality**, **Logo**, **Element** (the
last flagged as advanced - core geometry, not usually touched). A
persistent **RENDER TEST TEXT** button (outside the tab area, always
visible) launches/raises `f3d` in orthographic Top View
(`f3d_top_view_cmds.txt`, `set_camera top` - reverse-engineered from
`libf3d.so`'s own command strings after a hand-derived
`--camera-direction` guess came out rotated 90°) to preview the flat
Type Test text.

**Config tiers**: the master YAML (`config/blickensderfer.yaml`) is never
written to by the TUI. All edits/saves go to a gitignored per-master
scratch copy, `config/blickensderfer.running.yaml`, created on first run
and auto-migrated (`_migrate_running_config`) to backfill any top-level or
nested keys that exist in master but not yet in a stale running copy,
without touching your own customizations. "Reset to Defaults" discards the
running copy and starts fresh from master. "Save" writes the running copy
to a location you choose (`textual-fspicker`'s file browser) - that's how
a tuning session becomes a real, committable config.

**Picking a font**: every font path field (Font & Alignment's `font.path`,
Logo's `logo.font_path`, the per-machine label/legend font paths) has two
buttons. **Installed** opens a searchable list of every font installed on
this machine, by name - fontconfig's own list on Linux (so anything
`fc-list` knows about, including per-user directories added to
`fonts.conf`), `%WINDIR%\Fonts` plus the per-user
`%LOCALAPPDATA%\Microsoft\Windows\Fonts` on Windows; see
[`lib/system_fonts.py`](lib/system_fonts.py). Type to filter on family,
style or filename; the currently-selected font is pinned to the top of
the list. **File** is the original file browser, for a font that isn't
installed anywhere - the config stores a plain path either way, so
nothing downstream changes.

**Build tab**: a 2-option dropdown (Element / Shaft Gauge) plus an
independent "Resin supports" checkbox. Element builds `FullElement()`, or
`ResinPrint()` (adds `ResinSupport()`'s rods/breakaway ring - see the
Resin tab) when the checkbox is on. Shaft Gauge builds `GaugeTestSet()`
(see the Gauge tab/section below) regardless of the checkbox - a gauge
print always carries its own resin supports since it can't stand on its
own.

**Quirks worth knowing**: `q` alone doesn't quit while any text field has
focus (Textual consumes it as literal input) - `ctrl+q` always works, and
either quit path saves the running config first. Quitting/closing the
terminal also kills any `f3d` process the tuner launched.

