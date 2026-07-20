# v4: Minkowski-draft type element pipeline

Builds struck-character type elements (starting with Blickensderfer) as
watertight solids. The draft taper (the cone-shaped widening from a
character's print face down to its embedded root) is built via a REAL
Minkowski sum (`manifold3d.Manifold.minkowski_sum`) between the flat glyph
shape and a cone - not OpenSCAD's `minkowski(cone)` (too slow at the scale
this needs, which is why v4 exists), and not a hand-rolled per-vertex
outline offset (v4's first approach, abandoned - see below). Every part of
the assembly (characters onto the cylinder, the platen cutout, the final
`Additive - Subtractive`) is a real `manifold3d` boolean now too -
`sp.union_all()`/`Manifold.batch_boolean()`, not `trimesh.util.concatenate`
(an earlier bug: `TextRing()`/`Additive()` used plain concatenation, which
just merges vertex/face arrays with no boolean resolution at all, so
wherever a character's embedded root overlapped the main cylinder or two
characters overlapped each other, both surfaces stayed fully intact and
superimposed - no new edge formed at the actual intersection, confirmed via
a 1148mm3 double-counted-overlap volume discrepancy - see `SESSION_LOG.md`).

v4 started from a per-vertex mesh-manipulation technique adapted from a
friend's 2023 "TypeCylinder" tool (Python + trimesh) - triangulate the flat
glyph outline once, then reshape that fixed-topology mesh with plain
coordinate math instead of any boolean call. That approach had no topology
awareness: a fixed-distance offset can't detect when a glyph's local
geometry (a narrow gap, a tight concave corner) is too small to support
that distance, and just folds through itself instead of erroring. A later
session tried patching this with a gated self-union repair, which fixed
most single-island glyphs but both left some (`e`'s hole-boundary fold) and
*broke* others (`i`'s dot got welded into its stem, losing real volume) -
band-aiding a fundamentally topology-blind technique one glyph at a time.
The per-vertex approach and its patches are gone from the code now (see git
history / `SESSION_LOG.md` if you want the full blow-by-blow); a real
Minkowski sum can't produce a self-intersecting result on ANY input
topology, so there's no per-glyph failure case left to chase. The real cost
is generation time (a boolean CSG call vs. plain coordinate math) - see
"Performance" below.

See `SESSION_LOG.md` for the chronological development history and the
current status/resume point for ongoing work.

## Setup

```
cd v4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```
python3 generate.py config/blickensderfer.yaml
python3 generate.py config/blickensderfer.yaml --points-per-mm 20 --separation-mm 1.5
python3 generate.py config/blickensderfer.yaml --no-core-groove   # skip the slow twisted grooves
python3 generate.py config/blickensderfer.yaml --resin-support    # add ResinPrint()'s support rods
python3 generate.py config/blickensderfer.yaml --out /tmp/test.stl
python3 generate.py config/blickensderfer.yaml --points-per-mm 8 --cone-segments 12   # faster iteration
```

All real-machine numbers live in the config file, not in code. A second
machine is mostly just a new YAML file under `config/` - `machine:
postal` in `config/postal.yaml` tells `generate.py`/`export_glyphs.py`
which Python module to import (see "Multiple machines" below). See
`config/blickensderfer.yaml` for the full parameter set; every value
there is commented with which `v2/blickensderfer.scad` (or
`lib/core_shaft.scad` / `lib/resin_support.scad`) variable it corresponds
to.

## Multiple machines (`lib/cylinder_machine.py`)

Blickensderfer and Postal are both "cylinder machines" - same physical
form, same v2 shared lib includes (`core_shaft.scad`, `resin_rod.scad`,
`resin_support.scad`, `glyph_pipeline.scad`), same `TextRing` radial-wrap
placement scheme. Everything structurally shared between them
(`Cylinder`/`Subtractive`/`FullElement`/`ResinPrint`/the whole Gauge
family/...) lives in `lib/cylinder_machine.py`. The only place the two
machines genuinely diverge in CODE, not just parameter values, is the
"drive pin trio" - `HollowSpace()`/`DrivePin()`/`ResinSupport()` -
Blickensderfer has a drive-pin countersink (2 selectable styles),
Postal has none at all. Those three functions live one-per-machine in
`lib/blickensderfer.py`/`lib/postal.py`.

**Dispatch mechanism**: each machine's `configure()` calls
`cylinder_machine._receive_config(g, name)` at the end, which copies
every config value AND the three trio function objects into
`cylinder_machine`'s own `globals()`. A function's `__globals__` is a
live reference to its defining module's dict, not a snapshot - so
`Subtractive()` (defined in `cylinder_machine.py`) calling `HollowSpace()`
as a bare name resolves it dynamically, against whichever machine
configured most recently. This directly mirrors OpenSCAD's own "last
include wins" dynamic module redefinition, which is how v2's shared lib
files achieve machine-specific behavior in the first place. Safe here
because `generate.py`/`export_glyphs.py` each configure exactly one
machine per process and exit - `tune.py` never imports these modules at
all, it only edits YAML and shells out to `generate.py` as a subprocess.
An `_active_machine` guard raises if a script ever tries to configure two
machines in the same process (not a real risk today, cheap insurance).

`config/postal.yaml`'s font paths point to the real fonts (`Alma
Mono.otf`, `FreeMono-Bold.otf`) - v2's real Postal font is a system font
family name ("Alma Mono" / "FreeMono:style=Bold"), not a file path, so
these are the actual matching files rather than a name lookup. Both are
CFF/cubic-curve OTFs, which used to silently mis-render (see "TrueType-
only outlines - RESOLVED" in "Known limitations" below) - now handled
correctly and verified end-to-end.

`python3 tune.py` (no args) starts at a machine picker - pick
Blickensderfer or Postal and it loads that machine's default config
(`MACHINES` in `tune.py`) into a Postal-scoped Element tab (27 fields vs.
Blickensderfer's 32, since Postal has no drive-pin countersink) and its
own Layout tab (a single "QWERTY" preset - v2/postal.scad has only one
physical layout, no preset-switching menu like Blickensderfer's 6 - still
hand-editable via Modify glyphs if you need something else). The tuner
form's status row gains a "Change Machine" button once a machine is
picked, which saves the current form and returns to the picker (uses
Textual's `recompose()` to fully rebuild the form - `TuneApp.SECTIONS`/
`.FIELDS`/`.LAYOUT_PRESETS` are instance attributes reset by
`_load_machine()` on every pick, not fixed for the process lifetime). The
old direct-launch usage (`python3 tune.py config/postal.yaml`) still
works and skips the picker. The Browse button (separate from Change
Machine) only switches between different configs of the SAME machine -
picking a config for a different machine there is refused with a log
message pointing at Change Machine instead, since Browse repopulates the
existing widgets in place rather than recomposing.

### Mignon (`lib/mignon.py`) - NOT a "cylinder machine"

Unlike Postal, Mignon does **not** share `cylinder_machine.py`'s body
construction - only its glyph placement pipeline (`TextRing`,
`CalibrationTextRing`) is genuinely reusable. Confirmed by direct
function-by-function comparison against `v2/mignon.scad`: no
`Core`/`ClipCylinder`/`WireBite`/`SpeedHoles`/`core_shaft.scad` family at
all (its shaft bore is one plain `rotate_extrude()` polygon), a 12-sided
polygon main body instead of a round cylinder, a stepped-boss+chamfer top
feature instead of a wire clip, a plain cut-through alignment keyway
instead of a countersunk drive pin, Minkowski cleanup at **both** ends
instead of top-only, and fully bespoke resin-support placement (no
`CutGroove`/`SpeedHoleSupport`/`DrivePinSupport`/`BottomSupports` - just a
raft ring plus rods at two radii). `lib/mignon.py` reimplements all of
this locally rather than extending `cylinder_machine.py`; see its module
docstring for the full comparison.

Two shared-module changes DID come out of this port (both backward-
compatible, regression-verified against Blickensderfer/Postal):

- **Row count.** `TextRing`/`CalibrationTextRing` hardcoded `for row in
  (0, 1, 2):` - Mignon has 7 physical rows, not 3 (`v2/mignon.scad`'s
  `Baseline_Regular`/`Cutout` are both 7-entry arrays). Changed to
  `range(len(DHIATENSOR))`, which reduces to the exact same 3-row loop
  for Blickensderfer/Postal's configs.
- **Placement formula overrides.** `place_on_cylinder()` hardcoded
  `Char_Protrusion` (the placement-stage radial protrusion) and `0.5`
  (the angle-half-step column-centering constant). Mignon's v2 source
  overrides both to 0 (`Letter_Placement_Protrusion`/`Angle_Half_Step`,
  `v2/mignon.scad:118-121` via `lib/glyph_pipeline.scad`'s own documented
  optional-override mechanism) - added as optional `placement_protrusion`/
  `angle_half_step` params, `None` (every Blickensderfer/Postal call site)
  preserving the exact original hardcoded behavior.

Also has no Shaft Gauge Test at all (`v2/mignon.scad:30`: "Shaft Gauge
Test... omitted" - confirmed, along with Bennett and Helios Klimax, via
the same explicit comment in their own files). `tune.py` handles this
generically - `SECTIONS_BY_MACHINE["mignon"]` simply has no `"Gauge"` key,
and both the Gauge tab and the Build tab's "Shaft Gauge" option check for
that key's presence rather than assuming every machine has one.

One real bug caught and fixed during this port: `v2/mignon.scad:120`'s
`Latitude_Int=-360/len(Layout[0])` is **negative** (columns wrap the
opposite rotational direction from Blickensderfer/Postal's positive
`360/columns`) - missed on the first pass (copied the positive formula
literally), caught via a direct render comparison, fixed by hardcoding
the sign flip in `mignon.py`'s own `configure()` (machine-specific, not a
`cylinder_machine.py` change).

**Layout tab.** `tune.py`'s Layout tab was written when Blickensderfer/
Postal (3 rows each) were the only machines and had "3" hardcoded as a
literal in nine places (`BASELINE_CUTOUT_KEYS`, row-preview widget
construction, custom-row seeding, save round-trip, etc.) - all now derive
the row count from the config (`len(layout.baseline_row)`, etc.), which
reduces to the same 3-row behavior for Blickensderfer/Postal
(regression-verified) and correctly handles Mignon's 7. All 30 of
Mignon's real named layout presets (German 4, Cyrillic, Bulgarian,
Georgian, etc.) were ported from `v2/lib/layouts/mignon_layouts.scad`
into `LAYOUT_PRESETS_MIGNON` (3 placeholder-empty presets in v2's own
source were excluded; two anomalous 13-character rows in v2's Georgian/
Greek data, unreachable by v2's own `Char_Legend` indexing, were
truncated to 12). `layout.rows`/`LAYOUT_PRESETS_MIGNON` are stored in RAW
KEYBOARD-LEGEND order (v2's own `Layout` array - what's printed on the
physical keyboard/manual), not the `Char_Legend`-remapped `Physical_
Layout` build order - `lib/mignon.py`'s `configure()` applies
`layout.char_legend` (`[7,8,9,10,11,0,1,2,3,4,5,6]`, matching
`v2/mignon.scad:88` exactly) to compute the actual build-time `DHIATENSOR`
itself, so the legend can be read/edited the way a person actually reads
it off the machine without hand-deriving the build order. See
SESSION_LOG.md parts 20-21 for the full account.

**Label - a genuine second engraved-text feature, not in v2.** v2/
mignon.scad's real `[Logo]` customizer section (confirmed end to end) has
exactly ONE engraved-text feature (`Cylinder_Label`), which is what this
app's `logo.*` config/"Logo" tab already drives. A second, independent
`label.*` feature was added anyway (v4-only, not a v2 port), with its
own "Label" tab - same field format as Logo (font/text/size/spacing/
height-offset), always placed 180
degrees opposite Logo's `position_offset_deg` (computed in `configure()`
as an invariant, not independently stored - moving Logo moves Label with
it). Defaults to empty text rather than duplicating Logo's default
verbatim: at Logo's real 15deg/char spacing a normal-length label already
spans most of the ring, so two identical strings 180 degrees apart would
overlap rather than sit cleanly opposite each other.

**Tallen (Plakatschrift) mode.** A display-type variant
(`v2/mignon.scad:109-115,197`, off by default like this file's real
untallened German 4 element) that adds `height_increase_mm` (3mm) to the
element height and shifts every baseline row by
`tallen_baseline_offset_mm` (-1.25mm) - cutout rows are NOT affected, a
real asymmetry in v2's own source, not an oversight. Previously
acknowledged-but-not-ported; now a real `element.tallen` toggle plus its
two magnitude fields, all exposed on the Element tab.

### Bennett (`lib/bennett.py`) - shares the glyph pipeline, bespoke body

Like Mignon, Bennett shares `cylinder_machine.py`'s glyph placement/text
pipeline (`TextRing`/`CalibrationTextRing`, `place_on_cylinder` with
`placement_protrusion=0` - Bennett's own `Letter_Placement_Protrusion=0`,
same override Mignon/Helios use) and, unlike Mignon, also reuses
`lib/core_shaft.scad`'s shared `SecondaryCore`/`CoreGrooves`/`CoreChamfer`/
`CoreEllipses` directly (`Core_Chamfer_Top=False` - no clip, so unlike
Blickensderfer/Postal there's no top chamfer under one; `Core_Taper_Top_Z`
= `Core_Top_Z` - the taper's own top landmark coincides with the absolute
top, again because there's no clip pushing it down). Bennett does NOT
override `Angle_Half_Step` the way Mignon does - v2 never sets it, so it
stays at the shared lib's default 0.5, verified algebraically: Bennett's
own `Theta=-(360/28*col+360/(2*28))` reduces to exactly
`(0.5+col)*Latitude_Int`, the same formula shape as Blickensderfer/Postal,
just with `Latitude_Int` negative instead of positive (same sign
convention as Mignon).

Everything else is fully bespoke, confirmed by direct comparison against
`v2/bennett.scad`: two positioner pins with a small chamfer cone
(`PositionerPins`) instead of a wire clip, a 9-point `rotate_extrude()`
polygon shaft bore (`HollowBody`, built from landmark arrays + an index
pattern, ported mechanically) instead of `core_shaft.scad`'s
`HollowSpace()`+`BottomSlopedSpace()` combination, a full 3-row x
28-column grid of physical alignment/screw holes (`AlignmentHoles`, no
Blickensderfer/Postal equivalent at all), two independent flat
whole-string engraved-text groups cut into the bottom face near the shaft
(`LabelText` - v2 calls `text()` directly per whole string with
`halign=valign="center"`, not a ring of individually angle-placed
characters like Blickensderfer/Postal's `LogoText` or Mignon's
`ElementLogo`/`ElementLabel` - see `_build_text_string()`'s docstring for
how whole-string layout was ported: each character placed at its natural
FreeType advance, the assembled string centered on its total advance
width - the same "native halign=center centers the ADVANCE box"
convention this codebase already established for `AlignedText`), a simple
fixed 8-hole `SpeedHoles` ring (own diameter/radius names, plus a
half-step angular phase offset Blickensderfer/Postal/Mignon's own
`SpeedHoles` don't have), top+bottom countersinks and an indicator
hole/roof taper, and fully bespoke resin-support placement (own
ring+groove+raft `rotate_extrude()`, 8+8+4 `ResinRod()` calls at three
different radii/heights - no `CutGroove`/`SpeedHoleSupport`/
`DrivePinSupport`/`BottomSupports` concepts at all, though it DOES reuse
`cylinder_machine._resin_rod()` for the rod primitive itself, same as
Mignon).

No Shaft Gauge Test (`v2/bennett.scad:24`: "Sections with no Bennett
equivalent (Print Tolerances, Shaft Gauge Test) are omitted" - same as
Mignon). Its one engraved-text feature lives under its own `label:` config
section/"Label" tab (not "Logo" - the field shapes don't correspond to
Blickensderfer/Postal/Mignon's Logo schema at all, no text_spacing/
position_offset_deg/radial_offset_mm concept). Composing this exposed a
latent `tune.py` bug: `_compose_tuner_ui()` unconditionally composed a
"Logo" tab for every machine (never previously exercised, since
Blickensderfer/Postal/Mignon all have one) - now guarded by `"Logo" in
self.SECTIONS`, matching the existing `"Label"`/`"Gauge"` guards right
next to it.

### Performance

The draft taper is a real Minkowski sum (`manifold3d`), not plain
coordinate math, so generation time is real and tunable via two knobs
(`quality.minkowski_fn` / `--cone-segments` and `build.points_per_mm` /
`--points-per-mm`, both config-driven) - `manifold3d`'s own docs warn
Minkowski cost scales with the *product* of the two operands' face counts.
Measured for the full 84-character ring + assembly:

| points_per_mm | minkowski_fn | full ring + assembly |
|---|---|---|
| 15 (config default) | 16 (config default) | ~60-70s |
| 8 | 12 | ~30-35s |
| 6 | 8 | ~16s |

Quality difference between the fast and default settings is minor
(confirmed visually on `e`/`m`, the hardest glyphs). Use the fast settings
while iterating, the config defaults for a final export.

For the fastest possible iteration (placement/layout only, no draft),
set `build.minkowski_enabled: false` or pass `--no-minkowski` - this skips
the Minkowski sweep entirely (by far the most expensive step) and returns
each character as an undrafted block: correct platen curve and glyph
footprint/placement, no taper. Measured: the full ring + assembly in
~3s instead of ~30-70s. Not a substitute for a real export - re-enable
before generating anything meant to be printed.

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

## Layout

```
generate.py                 entry point - loads a config, builds, exports
tune.py                     interactive TUI for editing the config (see above)
type_test.py                flat CPI/LPI-spaced text preview used by tune.py's Type Test tab
export_glyphs.py            exports every configured character to its own STL, for visual inspection
config/
  blickensderfer.yaml        every real machine parameter + build/alignment settings
  blickensderfer.running.yaml   gitignored scratch copy tune.py actually edits/saves (see above)
  postal.yaml                 Postal's parameters - see "Multiple machines" below
  mignon.yaml                 Mignon's parameters - see "Mignon" below (own schema, not shared with Blick/Postal)
lib/
  glyph_poc.py               single-glyph mesh pipeline (the core technique)
  scad_primitives.py         revolve_polygon/extrude/transform helpers, generic (not machine-specific)
  cylinder_machine.py         shared cylinder-machine-family code (Blickensderfer/Postal) - see "Multiple machines"
  blickensderfer.py          Blickensderfer's own configure() + drive-pin trio (HollowSpace/DrivePin/ResinSupport)
  postal.py                   Postal's own configure() + drive-pin trio
  mignon.py                   Mignon's own configure() + full body/shaft/resin-support (see "Mignon" below)
output/
  blickensderfer_running.stl         latest generated result (scratch/working file, not a keeper - see tune.py's Save button)
  experiments/                       diagnostic renders/sweeps from development (not regenerated by generate.py)
```

## The glyph pipeline (`lib/glyph_poc.py`)

For one character (`build_glyph`):

1. **`get_glyph_contours_and_advance`**: walk FreeType's TrueType outline
   (on/off-curve tagged points) into flat polylines, sampling curved spans
   at `points_per_mm` density. **TrueType (quadratic) only** - a CFF/
   OpenType font's cubic curves will silently mis-parse (see "Known
   limitations").
2. **`classify_and_triangulate`**: classify each closed contour by
   nesting-depth parity (even=solid island, odd=hole - not just "contained
   by something", which breaks on genuinely nested glyphs like DejaVu's
   `0` with its slash mark nested inside its own counter) and triangulate
   each island (with its holes) via `triangle`. Flat, z=0.
3. **Build a block** (`trimesh.creation.extrude_triangulation`) sitting at
   the tip end, tall enough to contain the real platen cut for this
   specific glyph's own Y-extent (computed from the exact circle-sag
   formula, not a fixed guess - see "Real platen cutout" below) - the
   undrafted, undilated glyph shape, plus margin.
4. **Carve the platen scallop with a REAL cylinder subtraction**
   (`manifold3d` boolean, not a per-vertex approximation) - see "Real
   platen cutout" below.
5. **Minkowski-sum the scalloped block with a draft cone**
   (`manifold3d.Manifold.minkowski_sum`) - apex (`radius=0`) registered
   exactly at the world origin so it lines up with the tip, wide base
   (`radius=expansion_width_mm`) below it at `z=-cone_height`. The sum's
   cross-section at the tip is therefore the block's own (curved, per step
   4) top surface unchanged; at the root (`z=0`) it's that same surface
   dilated/offset outward by `expansion_width_mm` - the draft taper, with
   no self-intersection possible on any input topology (holes, disjoint
   islands, arbitrarily narrow gaps - a real Minkowski sum can't fold).
   Skippable via `build.minkowski_enabled: false` (or `--no-minkowski`)
   for a fast, undrafted preview - see "Performance" above.
6. **`Manifold.simplify(simplify_tolerance_mm)`**: `manifold3d`'s raw
   `minkowski_sum` output is drastically over-triangulated on flat regions
   (a single straight wall came out as ~24 near-coplanar micro-triangles
   with normals wobbling by a fraction of a degree from floating-point
   noise - visible as faceting on straight strokes). Collapses that
   cleanly (e.g. `H`: 1156->42 vertices) without visibly affecting real
   curvature - the tolerance is far below any meaningful glyph feature
   size.
7. **`alignment_x_offset`**: horizontal placement within the glyph's own
   advance box (see "Alignment" below) - applied to the contours before
   step 2, not listed in pipeline order above.

`blickensderfer.TextRing` calls `build_glyph` 84 times (3 rows x 28
columns) and places each result on the cylinder via `place_on_cylinder`.

### Real platen cutout

The platen scallop is a REAL boolean cylinder subtraction (matching the
real machine and v2's `PlatenCutout()`), not a per-vertex parabola
approximation (an earlier version of this pipeline used the small-angle
approximation of the same circle, `z = (y-radius_y_offset)^2 *
platen_radius + separation_mm`, applied to whatever vertices happened to
survive triangulation). `platen_radius_mm` is still that same
approximation coefficient (`1/(2*Rp)`) - inverted internally to recover
the real platen radius `Rp`, rather than adding a redundant parameter -
used to build an actual cylinder (axis along X, tangent to the tip plane
at `y=radius_y_offset`, `platen_fn` segments), boolean-subtracted from the
block *before* the Minkowski sum.

Before, not after, matters: an earlier version subtracted nothing and
instead nudged only the *swept result's* top ring into the parabola after
the Minkowski sum. That's wrong - the cone's geometry, and therefore the
realized draft angle, is only valid for whatever shape it's actually
summed with. Nudging just the final ring left the walls built as if the
tip were still flat, so wherever the platen bulge is large (far from
`radius_y_offset` - e.g. the bottom of `M`/`A`, vs. `L`/`I`'s mostly-
vertical runs which stay close to it) the wall no longer tapered at the
specified angle over the actual (now longer) distance to the tip - visible
as inconsistent facets on those specific edges. Carving the scallop in
first means the cone (unmodified, exactly as specified) sweeps a surface
that's already the correct curved shape, so the draft angle is preserved
everywhere by construction.

The cylinder's axis position/radius depend only on `radius_y_offset` and
`Rp` - both per-row constants, identical for every character in a row -
so the underlying curve is the exact same real cylinder machine-wide per
row, not independently approximated per glyph; only where it intersects
each glyph's own silhouette differs, which is correct.

### Character mirroring

A struck type element carries a MIRROR-IMAGE of the desired printed glyph
- striking is a reflection through the contact plane, same reason a rubber
stamp or hot-metal slug is cut reversed. `v2`'s `TwoDText` wraps the whole
aligned/shifted glyph in `mirror([1,0,0])`; `v4` never did this until this
was found and fixed in `build_glyph()` (negating X on the already-shifted
contours, after `x_shift`, matching v2's translate-then-mirror order).
Fixing this also resolved a previously-reported "x offset wrong direction"
bug as a side effect - both were the same missing mirror. Scoped to
`build_glyph()` (struck characters) only - `build_flat_text()` (`LogoText`,
Type Test) is deliberately untouched, since that text is read directly,
never struck.

### Draft angle is configurable

`build.draft_angle_deg` (config + `--draft-angle-deg` CLI override, also
on tune.py's Font & Alignment tab) sets the Minkowski draft cone's
half-angle - `expansion_width_mm = separation_mm * tan(draft_angle_deg /
2)`. Defaults to `55.0`, the real machine value. Previously a fixed
`glyph_poc.py` module constant with no override.

### Draft direction (character protrusion)

The print face's deepest/narrowest point (at `y=radius_y_offset`, where the
platen scallop is zero) sits at a FIXED radius,
`Element_Diameter/2 + Char_Protrusion` - matching where
`PlatenCutout()`'s cylinder actually touches the character in
`v2/lib/glyph_pipeline.scad`. The root (the wider, `separation_mm`-drafted
end) sits **inward** from that anchor by `separation_mm` - like a nail
driven in with a wide head sitting proud, not a flush base that only
widens sideways. This means the root's reach toward the hollow chamber
scales directly with `separation_mm`; it is not automatically safe just
because it's "the embedded end" (see the HollowSpace margin note below).

## Element assembly (`lib/blickensderfer.py`)

Ports `Additive()`/`Subtractive()`/`FullElement()` from
`v2/blickensderfer.scad` close to 1:1, in the same origin/orientation
convention (Z=0 at the bottom face of the main disk, Z+ up through the
clip end). `Subtractive()`'s parts are unioned into one mesh, then
subtracted from `Additive()` in a single `manifold3d` boolean - the same
build-solid-then-hollow order the real file already uses.

Ported features: `Cylinder`, `ClipCylinder`, `TextRing`, `Core`,
`CoreGrooves` (16 twisted friction grooves), `CoreChamfer`, `SecondaryCore`
(tapered friction-fit profile), `CoreEllipses` (web slots), `SpeedHoles`,
`HollowSpace` (the real chamfered/roofed barrel profile, not a plain
bore - see `scad_primitives.revolve_polygon`), `WireBite`, `DrivePin`,
`BottomSlopedSpace`, `TopMinkCleanup`, `LogoText`.

Not ported (out of scope so far): `Drive_Pin_Style=1` (old drive pin
variant).

### Facet-count knobs (`quality:` in the config)

Five separate `_fn` values, kept independent rather than sharing one
catch-all, per user direction - each covers a distinct surface family:

- `body_fn` - the main visible/cosmetic element body (`Cylinder`,
  `ClipCylinder`) only.
- `cyl_fn` - the inner shaft/core bore (`Core()`) only. Kept separate from
  `body_fn` even though both currently default to the same value (360).
- `surface_fn` - everything else structural: `HollowSpace`, `SpeedHoles`,
  chamfers, resin details.
- `platen_fn` - the real platen cutout cylinder (see "Real platen cutout"
  above) - independent of the other four since it's a per-glyph boolean,
  not a body-level revolve.
- `minkowski_fn` - the draft cone kernel (see "Performance" above) - by
  far the most cost-sensitive of the five, since `manifold3d`'s Minkowski
  cost scales with the product of face counts against `points_per_mm`.

### Resin print supports (`ResinPrint`)

Ports `lib/resin_rod.scad` (`ResinRod` -> `scad_primitives.resin_rod`, a
generic hull-of-spheres tapered support rod, reusable across future
machines) and `lib/resin_support.scad`'s cylinder-machine-family placement
logic (`CutGroove`, `SpeedHoleSupport(s)`, `DrivePinSupport`,
`BottomSupports`, `ResinPrint`) - shared between machines in
`lib/cylinder_machine.py` (see "Multiple machines" above); only
`ResinSupport()` itself is machine-specific (the drive-pin trio).
`CutGroove()` - the breakaway ring - is built as `revolve(profile) -
revolve(hole1) - revolve(hole2)`: the real file's 2D difference happens
*before* `rotate_extrude()`, so each hole becomes a full 360deg toroidal
score line around the circumference, not discrete perforation points.

`ResinPrint()` unions `ResinSupport()` onto `FullElement()` (support
material to be broken off after printing, not subtracted). Off by default
(`build.resin_support: false` in the config) since it's only needed right
before slicing for print; enable via `--resin-support` or the config.

**`resin.raft`** (also on tune.py's Resin tab as "Continuous raft"): `false`
(default, both machines) - each support rod grows its own small raft
cone. `true` - one continuous raft plate shared by every rod, reaching
all the way to the element's center axis. This was originally two
separate hardcoded per-machine values (v2's Blickensderfer always used
individual rafts, Postal always used the continuous plate) - collapsed
into one shared, user-facing toggle (`cylinder_machine.resin_raft_config`
derives `Resin_Rod_Raft`/`Cut_Groove_Inner_X` from it) since the
continuous-plate option is genuinely useful for either machine, not
something that should silently differ by default between them. Verified
all 4 combinations (each machine x both settings) watertight/winding-
consistent/`is_volume`, and confirmed both machines' `false` default and
Postal's `true` reproduce byte-identical geometry to before this change.

### Shaft Gauge Test (`GaugeTestSet`)

Ported from v2's `[Shaft Gauge Test]` section (`blickensderfer.scad`
~265-267/517-589). Not part of the real element - a standalone 6-pocket
"revolver" calibration print for empirically finding
`element.core_id_offset` (the print-tolerance addition to the shaft's
minor diameter). Each of the 6 pockets bores the shaft passage at
`gauge.offset_start + n * gauge.offset_int` (n=0..5) and is engraved with
its own offset value (`GaugeText`) so you can read off which pocket you
test-fit on the real machine. `RevolverSolid()` (the hull of the 6
cylinder pockets) uses `trimesh.util.concatenate(...).convex_hull`, the
same pattern `CoreEllipses()` already used, since trimesh has no
hull-of-solids primitive. Build via `generate.py --gauge` or tune.py's
Build tab ("Shaft Gauge").

### Calibration (`CalibrationElement`)

Ported from v2's `Cutout_Test`/`Baseline_Test`/`Test_Layout` mechanism
(`lib/testing.scad`'s `testSweepArray` + `lib/glyph_pipeline.scad`'s
`TextRing`/`TextRingDebug`, ~line 407-451) - a real, already-designed v2
feature for empirically finding the right `layout.baseline_row`/
`cutout_row` values, not invented for v4. Unlike the Shaft Gauge Test,
this IS a real element (same `Subtractive()` hollow-out as a normal
build) - only the additive text ring differs: every physical position
strikes the SAME `calibration.test_char` (v2's `Test_Layout`, always on
here - the whole point is a consistent reference shape to compare across
positions), while `calibration.vary_baseline`/`vary_cutout` (independent
booleans, matching v2's own separate `Cutout_Test`/`Baseline_Test` flags
- usually only one is on at a time, but both CAN be on together, moving
by the same shared offset) get a per-column swept offset
(`calibration.start + calibration.interval * col`, matching
`testSweepArray`) instead of its row's normal fixed value. Default
`start: -0.7` (`interval: 0.05` unchanged) sweeps from -0.7mm to +0.65mm
across the 28 columns - both below AND above the reference, not just
above it.

**The reference (the row's own normal value being swept around) is
fixed, not read from whatever config is being built.** `generate.py
--calibrate`'s reference defaults to the config being built (same as
before, for direct CLI use), but `--calibration-reference-config PATH`
loads `layout.baseline_row`/`cutout_row` from a SEPARATE file instead -
tune.py always passes the MASTER config here, never the running copy.
This matters because the Element tab's baseline/cutout fields (see
below) write to the RUNNING copy: without a fixed reference, dialing in
a value from one calibration pass would shift where the NEXT pass
centers its sweep - chasing an already-moving target instead of
converging on the master's stable original value. `CalibrationTextRing`
always prints which reference arrays it's actually using, so this is
never ambiguous from the log.

Build via `generate.py --calibrate` (plus `--calibration-char`/
`--calibration-vary-baseline`/`--calibration-no-vary-baseline`/
`--calibration-vary-cutout`/`--calibration-no-vary-cutout`/
`--calibration-start`/`--calibration-interval`/
`--calibration-reference-config` overrides) or tune.py's Build tab
("Calibration Element") + its Calibration tab's two checkboxes. Prints
one line per
physical position - keyboard key, real placement angle, and the exact
cutout/baseline value used there (computed from the actual physical
placement angle via `PLACEMENT_MAP`, not v2's raw content-order `col` -
more directly useful for correlating against the printed part, and
avoids relying on Blickensderfer's non-identity `placement_map` lining up
with v2's o'clock-from-content-order convention, which only happens to
hold for Postal's identity map). `--calibrate` also writes a `.txt`
sidecar next to the STL with the same per-position lines; tune.py's Save
copies that sidecar alongside the saved STL too (like the existing
`.yaml` metadata sidecar), when the last build was a Calibration build.

Test-fit each position on the real machine, read off which column's value
looks/fits best, and enter it directly in that row's baseline/cutout field
on tune.py's Element tab (`layout.baseline_row`/`cutout_row` - list-valued,
so not part of the generic FIELDS mechanism, but exposed as 6 bespoke
per-row fields, `patch_yaml_list_item` patching just that one element of
the inline YAML list).

### HollowSpace margin is razor-thin by design at the current settings

At `separation_mm=2.0`, the character root lands at
`Element_Diameter/2 + Char_Protrusion - separation_mm = 15.5mm` - which is
*exactly* `HollowSpace`'s outer wall radius for the rows that fall in its
wide z-band. Zero real clearance; `generate.py` prints whether any root
vertex actually lands inside `HollowSpace` for the current settings (it
flips between `True`/`False` run to run at low `points_per_mm` purely from
floating-point/mesh-resolution noise at this exact boundary - not a new
bug, just confirmation of how tight it is). This is exactly why the
element is built solid-then-hollowed rather than pre-calibrated: the
boolean handles either case cleanly, precise pre-calculation would be
fragile here.

## Alignment (character centering)

Two base modes, plus two independent modified-character override groups
layered on top - a from-scratch scheme (not a port of
`v2/lib/glyph_pipeline.scad`'s 4-method `AlignedText`), configured under
`alignment:` in the YAML:

- `mode: center` - shift by `-advance/2` (centers the ADVANCE box, same
  convention v2's native `halign=center` uses - not the ink bounding box)
  plus `center_offset_mm`.
- `mode: left` - no centering shift, just `left_offset_mm` (0 = the
  glyph's natural FreeType pen origin, unmoved).
- `modified_left_chars` (default `"!,.;:)"`) get an *additional* shift of
  `-modified_left_offset_mm`; `modified_right_chars` (default `"("`) get
  `+modified_right_offset_mm`. A character matching both resolves to the
  left group (checked first).

All offsets default to `0.0` (no-op) until set in the config.

## Known limitations

- **TrueType-only outlines - RESOLVED.** CFF/OpenType (cubic-curve) fonts
  used to mis-parse silently - `contour_to_points` (`lib/glyph_poc.py`)
  only checked FreeType's on/off-curve bit, so a cubic off-curve point got
  misread as a lone quadratic control point, producing plausible-looking
  but geometrically wrong curves with no error raised (confirmed on
  `FreeMono-Bold.otf`: watertight-but-winding-inconsistent geometry).
  Fixed by checking the tag's low 2 bits (`FT_CURVE_TAG`: 0=quadratic,
  2=cubic) and evaluating a real cubic Bézier (`cubic_bezier()`) for cubic
  spans instead. Verified against real CFF fonts (`Alma Mono.otf`,
  `FreeMono-Bold.otf`) end-to-end through `generate.py config/postal.yaml`
  - fully watertight/winding-consistent/`is_volume`, 0 skipped characters
  - and confirmed byte-identical output on the quadratic (TrueType) path
  for Blickensderfer before/after. Note this is only about which curve
  format is INSIDE the file - `.otf` itself doesn't imply cubic (some OTF
  files are TrueType-flavored internally) and `.ttf` doesn't guarantee
  quadratic either; the code now handles either correctly regardless of
  file extension.
- **Self-intersecting drafts - RESOLVED.** The old per-vertex outline
  offset could fold through itself on narrow glyph features (71/84
  characters failed a `shapely` simplicity check at production settings -
  see git history for the detection/gated-repair machinery this used to
  need). A real Minkowski sum cannot produce a self-intersecting result on
  any input topology, so there is nothing left to detect or repair here;
  `TextRing()` no longer reports on this at all.
- **`place_on_cylinder()` needs `process=False`.** Reconstructing a mesh
  via `trimesh.Trimesh(vertices=..., faces=...)` with the default
  `process=True` silently re-runs vertex merging and corrupts already-valid
  geometry post-placement (reproduced with an identity transform alone:
  2195->1507 vertices, `watertight` True->False, nothing to do with the
  rotation/translation itself). Placement is a pure coordinate move - no
  topology change, no reprocessing needed.
- **Inter-character collisions are detected, not repaired.**
  `_check_inter_character_collisions()` in `lib/blickensderfer.py` uses
  `trimesh.collision.CollisionManager` across all 84 placed parts (this is
  what that tool is actually for - checking DIFFERENT registered objects
  against each other - unlike an earlier, meaningless attempt earlier in
  this project's history that called it on a single mesh expecting
  self-intersection detection, which it never provided). At
  `separation_mm=2.0`, 61 adjacent-character pairs currently collide -
  confirmed real via a direct boolean intersection check (not just the
  collision manager's flag), and confirmed to sit right at the embedded
  root end (radius ~15.6mm, vs. the root anchor at 15.5mm), not near the
  visible outer surface - which is why it isn't visible just looking at
  the assembled ring from outside. Accepted as-is; there's no simple
  automatic geometric fix for two overlapping solids short of redoing
  their placement/size (or reducing `separation_mm`, which shrinks how far
  each root reaches - confirmed to eliminate collisions entirely at
  `separation_mm=1.0`, at the cost of less embedding-depth margin into the
  main body).
- **`FullElement`/`ResinPrint` run a detect + best-effort auto-repair
  pass** (`scad_primitives.check_and_repair()`) using trimesh's own
  `fill_holes`/`fix_winding`/`fix_inversion`/`fix_normals` on the final
  assembled solid, re-checking and reporting whether it actually helped.
  This targets combinatorial defects only (holes, inconsistent
  winding/normals) - it has no effect on overlapping geometry like the
  inter-character collisions above (confirmed: it never even runs there,
  since `watertight`/`winding_consistent`/`is_volume` all already report
  `True` for two overlapping-but-otherwise-valid solids).
- **`LogoText` centers horizontally on the ink bounding box, not the
  advance box** - unlike `TextRing` (which now does real advance-box
  centering, see "Alignment" above). Fine for a decorative logo, not
  attempted to match `v2`'s exact `halign=center` behavior there.
  Vertically, characters ARE aligned by baseline (`y=0`, FreeType's own
  pen-origin convention) rather than each character's own ink-bbox
  center - centering each character independently on its own ink bbox
  put 'L' (cap-height, no descender) and 'e' (x-height only) at different
  heights, breaking a common baseline across the ring.
- **`Drive_Pin_Style=1`** (the older drive pin variant) raises
  `NotImplementedError` - only the current/default style is ported.
- **`BottomSlopedSpace`'s `bottomX()`** is ported from the real
  `lib/resin_support.scad` formula (`Bottom_Slope`/`Bottom_Z_Offset`), not
  approximated - flagging here only because an earlier draft of this file
  used a wrong approximation before the real formula was found; the
  current code is correct.
