# v4: Minkowski-draft type element pipeline

Generates struck-character type elements - typewheels, shuttles,
typeballs, slugs - for **15 antique typewriters**, as watertight solids
ready to print in resin. Each machine is driven by its own config YAML,
with an interactive TUI for editing and previewing it.

The draft taper (the cone-shaped widening from a character's print face
down to its embedded root) is a real Minkowski sum
(`manifold3d.Manifold.minkowski_sum`) between the flat glyph shape and a
cone - not OpenSCAD's `minkowski()`, which is far too slow at this scale,
and not a per-vertex outline offset, which can silently fold through
itself on narrow features. Every assembly step is a real `manifold3d`
boolean too.

**Machines**: Blickensderfer, Postal, Mignon, Bennett, Helios Klimax,
Hammond, Hammond Split, Selectric I/II, Selectric III, Selectric
Composer, Type Slug, Vogue Slug, Gauge Slug, Oliver Slug, Lumi Slug.

## Documentation

This README covers setup, usage and the file layout. Everything else
lives in its own document so this one stays short:

| Document | What's in it |
|---|---|
| [`PIPELINE.md`](PIPELINE.md) | The glyph pipeline end to end - contour tracing, platen cutout, the Minkowski sweep, mirroring, alignment, performance |
| [`MACHINES.md`](MACHINES.md) | Per-machine architecture, what each shares with the others, element assembly, resin supports, calibration |
| [`TUNER.md`](TUNER.md) | `tune.py` - the interactive tuner and its config tiers |
| [`LAYOUT_TRANSCRIPTION.md`](LAYOUT_TRANSCRIPTION.md) | How the keyboard layouts were transcribed from real manufacturer type catalogs, and what's still un-transcribed |
| [`LIMITATIONS.md`](LIMITATIONS.md) | Known limitations, and resolved ones worth remembering |
| [`CLAUDE.md`](CLAUDE.md) | Conventions and hard-won invariants - read before changing geometry code |
| [`SESSION_LOG.md`](SESSION_LOG.md) | Chronological development history and the current resume point |

Rendered at **[type-elements.leonardchau.com](https://type-elements.leonardchau.com)**.
The project story - collaborators, real prints, the machines themselves -
is at [leonardchau.com/projects/type-elements](https://leonardchau.com/projects/type-elements/).

## Setup

Linux/macOS:

```
cd v4
./lin_setup.sh      # creates .venv, installs requirements.txt
./lin_start.sh      # launches tune.py
```

Windows:

```
cd v4
win_setup.bat
win_start.bat
```

Either script is equivalent to the manual `python -m venv .venv` /
`pip install -r requirements.txt` steps, just idempotent (safe to
re-run, e.g. after `requirements.txt` changes) and consistent across
platforms. `tune.py` shells out to `f3d` for the live preview window -
`lib/f3d_bootstrap.py` finds one already on `PATH` if installed, or
downloads a pinned build automatically the first time it's needed (see
`PACKAGING_PLAN.md`), so no separate f3d install step is required on
either platform.

## Usage

```
.venv/bin/python3 generate.py config/blickensderfer.yaml
.venv/bin/python3 generate.py config/blickensderfer.yaml --flatness-tolerance-mm 0.002 --separation-mm 1.5
.venv/bin/python3 generate.py config/blickensderfer.yaml --no-core-groove   # skip the slow twisted grooves
.venv/bin/python3 generate.py config/blickensderfer.yaml --resin-support    # add ResinPrint()'s support rods
.venv/bin/python3 generate.py config/blickensderfer.yaml --out /tmp/test.stl
.venv/bin/python3 generate.py config/blickensderfer.yaml --flatness-tolerance-mm 0.05 --cone-segments 12   # faster iteration
```

`.venv/bin/python3` rather than bare `python3` - `trimesh`/`manifold3d`
and the rest of the build stack are only installed in the venv Setup
creates (or activate it first). `--flatness-tolerance-mm` is the glyph
outline's flatness budget in mm: SMALLER is finer and slower (config
default `0.005`), larger is coarser and faster. It replaced the old
fixed-rate `--points-per-mm`, which no longer exists.

All real-machine numbers live in the config file, not in code. A second
machine is mostly just a new YAML file under `config/` - `machine:
postal` in `config/postal.yaml` tells `generate.py`/`export_glyphs.py`
which Python module to import (see [`MACHINES.md`](MACHINES.md)). See
`config/blickensderfer.yaml` for the full parameter set; every value
there is commented with which `v2/blickensderfer.scad` (or
`lib/core_shaft.scad` / `lib/resin_support.scad`) variable it corresponds
to.

## Layout

```
generate.py                 entry point - loads a config, builds, exports
tune.py                     interactive TUI for editing the config (see above)
type_test.py                flat CPI/LPI-spaced text preview used by tune.py's Type Test tab
export_glyphs.py            exports every configured character to its own STL, for visual inspection
font_coverage.py            scans a font library for glyph coverage against a layout/config/string
generate_legend.py          keyboard-legend sheet renderer
generate_supports.py        standalone resin-support generator
generate_thumbnails.py      batch thumbnail renders
config/
  <machine>.yaml             every real machine parameter + build/alignment settings, one per machine
  <machine>.running.yaml     gitignored scratch copy tune.py actually edits/saves (see above)
                             15 machines: blickensderfer, postal, mignon, bennett, helios,
                             hammond, hammond_split, selectric12, selectric3,
                             selectric_composer, type_slug, vogue_slug, gauge_slug,
                             oliver_slug, lumi_slug
lib/
  glyph_poc.py               single-glyph mesh pipeline (the core technique)
  scad_primitives.py         revolve_polygon/extrude/transform helpers, generic (not machine-specific)
  build_log.py               the ONE progress/mesh-report/atomic-export format (see CLAUDE.md)
  resin_support.py           shared resin-support geometry
  svg_import.py              SVG path -> polygon import (logos/marks)
  f3d_bootstrap.py           finds or downloads the pinned f3d used by tune.py's preview
  contour_inspect.py         standalone contour diagnostic (not in the build path)
  heightfield_poc.py         abandoned height-field experiment, kept for reference; nothing imports it
  -- shared family modules --
  cylinder_machine.py        Blickensderfer/Postal shared code - see MACHINES.md
  spherical_machine.py       shared by the 3 IBM/Selectric machines
  wing_slug.py               shared by type_slug/vogue_slug/gauge_slug
  box_slug.py                shared by oliver_slug/lumi_slug
  -- one per machine --
  blickensderfer.py          configure() + drive-pin trio (HollowSpace/DrivePin/ResinSupport)
  postal.py                  configure() + drive-pin trio
  mignon.py                  configure() + full body/shaft/resin-support (see [`MACHINES.md`](MACHINES.md))
  bennett.py                 see [`MACHINES.md`](MACHINES.md)
  helios.py                  see [`MACHINES.md`](MACHINES.md)
  hammond.py / hammond_split.py
  selectric12.py / selectric3.py / selectric_composer.py
  type_slug.py / vogue_slug.py / gauge_slug.py / oliver_slug.py / lumi_slug.py
  hammond_legend.py, mignon_legend.py    keyboard-legend sheets for those machines
  layouts/                   ALL machines' keyboard/typeball layout presets - one
                             <machine>_layout.py each, aggregated by __init__.py.
                             tune.py imports from here and hardcodes no layout data.
                             See LAYOUT_TRANSCRIPTION.md for where the values came from.
output/
  <machine>_running.stl      latest generated result (scratch/working file, not a keeper - see tune.py's Save button)
  experiments/               diagnostic renders/sweeps from development (not regenerated by generate.py)
assets/                      SVG logos/marks (see svg_import.py)
docs/                        per-machine accessory docs (e.g. mignon_index_holder)
```

**Machines documented in detail below**: Blickensderfer/Postal
("Multiple machines"), Mignon, Bennett, Helios Klimax. The other ten -
Hammond, Hammond Split, the three Selectrics and the five Type Slug
machines - are ported and working but have no prose section here yet;
their own module docstrings and `CLAUDE.md`'s "Porting a new machine"
section carry that detail for now.

## Accessories

Non-parametric companion parts that print alongside a machine's type
elements but aren't generated by this pipeline (no `config/`/`lib/`
counterpart) live under `docs/`. See `docs/mignon_index_holder.md` for the
first one - a legend-card holder that goes with the Mignon element.

