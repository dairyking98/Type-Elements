# The glyph pipeline

Split out of `README.md` to keep it direct - see
[`README.md`](README.md) for setup, usage and the machine list.

## The glyph pipeline (`lib/glyph_poc.py`)

For one character (`build_glyph`):

1. **`get_glyph_contours_and_advance`**: walk FreeType's outline (on/
   off-curve tagged points) into flat polylines, subdividing curved spans
   adaptively to `build.flatness_tolerance_mm` via recursive de Casteljau
   (`flatten_quadratic`/`flatten_cubic`). Straight segments get ZERO
   subdivision; a curve gets exactly as many points as its own curvature
   needs. This replaced a fixed `points_per_mm` rate, which subdivided
   straight strokes as densely as curves. Both quadratic (TrueType) and
   cubic (CFF/OpenType) outlines are handled - the cubic path was a real
   bug once, now fixed (see [`LIMITATIONS.md`](LIMITATIONS.md)).
2. **`classify_and_triangulate`**: classify each closed contour by
   nesting-depth parity (even=solid island, odd=hole - not just "contained
   by something", which breaks on genuinely nested glyphs like DejaVu's
   `0` with its slash mark nested inside its own counter) and triangulate
   each island (with its holes) via `triangle`. Flat, z=0.
3. **Build a block** (`trimesh.creation.extrude_triangulation`) sitting at
   the tip end, tall enough to contain the real platen cut for this
   specific glyph's own Y-extent (computed from the exact circle-sag
   formula, not a fixed guess - see "Real platen cutout") - the
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
   for a fast, undrafted preview - see "Performance".
6. **`alignment_x_offset`**: horizontal placement within the glyph's own
   advance box (see "Alignment") - applied to the contours before
   step 2, not listed in pipeline order above.

`manifold3d`'s raw `minkowski_sum` output is drastically over-triangulated
on flat regions (a single straight wall came out as ~24 near-coplanar
micro-triangles with normals wobbling by a fraction of a degree from
floating-point noise - visible as faceting on straight strokes). A
`Manifold.simplify()` post-pass was tried to collapse that cleanly, but
was removed fleet-wide after it was found to reintroduce its own thin
spike/sliver defects against the adaptive contour method's sparser input
(see `CLAUDE.md`'s "Geometry invariants" - the adaptive contour tracing
itself, not a `simplify()` post-pass, is what keeps triangle count in
check now).

`cylinder_machine.TextRing` (shared, not per-machine) calls `build_glyph`
84 times for Blickensderfer (3 rows x 28 columns) and places each result
on the cylinder via `place_on_cylinder`.

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


### Performance

The draft taper is a real Minkowski sum (`manifold3d`), not plain
coordinate math, so generation time is real and tunable via two knobs
(`quality.minkowski_fn` / `--cone-segments` and
`build.flatness_tolerance_mm` / `--flatness-tolerance-mm`, both
config-driven) - `manifold3d`'s own docs warn
Minkowski cost scales with the *product* of the two operands' face counts.
Measured for the full 84-character ring + assembly. **These numbers are
historical**: they were taken under the old fixed-rate `points_per_mm`
sampling, which no longer exists, so the left column is not a knob you
can set today and the timings are not directly comparable to a current
build. Kept for the shape of the tradeoff (cost falls off steeply as
either knob drops), not as current figures. The adaptive tracer that
replaced `points_per_mm` measured a 1.3x-4.5x build-time reduction on
its own, with no correctness loss.

| points_per_mm (removed) | minkowski_fn | full ring + assembly |
|---|---|---|
| 15 (then-default) | 16 (config default) | ~60-70s |
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

