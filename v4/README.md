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

All real-machine numbers live in the config file, not in code - a second
machine (Bennett, Postal, ...) is a new YAML file under `config/`, not a
code change. See `config/blickensderfer.yaml` for the full parameter set;
every value there is commented with which `v2/blickensderfer.scad` (or
`lib/core_shaft.scad` / `lib/resin_support.scad`) variable it corresponds
to.

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

## Layout

```
generate.py                 entry point - loads a config, builds, exports
config/
  blickensderfer.yaml        every real machine parameter + build/alignment settings
lib/
  glyph_poc.py               single-glyph mesh pipeline (the core technique)
  scad_primitives.py         revolve_polygon/extrude/transform helpers, generic (not machine-specific)
  blickensderfer.py          machine assembly (Additive/Subtractive/FullElement) - config-driven
output/
  blickensderfer_full_element.stl    latest generated result
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
`BottomSupports`, `ResinSupport`) in `lib/blickensderfer.py`.
`CutGroove()` - the breakaway ring - is built as `revolve(profile) -
revolve(hole1) - revolve(hole2)`: the real file's 2D difference happens
*before* `rotate_extrude()`, so each hole becomes a full 360deg toroidal
score line around the circumference, not discrete perforation points.

`ResinPrint()` unions `ResinSupport()` onto `FullElement()` (support
material to be broken off after printing, not subtracted). Off by default
(`build.resin_support: false` in the config) since it's only needed right
before slicing for print; enable via `--resin-support` or the config.

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

- **TrueType only.** CFF/OpenType (cubic-curve) fonts mis-parse silently -
  confirmed on `FreeMono-Bold.otf` vs. the real `.ttf` (see
  `LOGO_FONT_PATH`'s comment in `lib/blickensderfer.py`): the `.otf`
  produced watertight-but-winding-inconsistent geometry with no error
  raised. Same limitation the original TypeCylinder tool had (it raised
  `ValueError` on cubic curves instead of silently mis-parsing them, which
  is arguably safer - worth matching eventually).
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
