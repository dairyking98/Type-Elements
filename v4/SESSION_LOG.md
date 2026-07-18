# v4 session log

Chronological record of this session's work, for resuming later. See
`README.md` for the architecture/usage reference of the *current* state;
this file is the history and the "what's next."

## Where things stand right now

- **Active branch: `v2-refactor`**, commit `cc396ac` - the naive per-vertex
  offset draft mechanism (`build_glyph`/`make_back`/`orthogonal_offset_vertex`
  in `lib/glyph_poc.py`), fully working: `generate.py config/blickensderfer.yaml`
  runs clean end-to-end (`FullElement`/`ResinPrint` both
  watertight/winding-consistent/`is_volume=True`).
- **`v4-real-offset` branch** (2 commits ahead of `cc396ac`: `7e6eeda`,
  `5941e00`) holds a from-scratch rewrite of the draft mechanism (shapely
  `buffer()`-based lofted taper) that fixed real bugs but hit a genuine,
  unresolved geometric limitation on some glyphs (`e`). Not merged. Kept
  for reference - see "The lofted-draft attempt" below before touching it
  again.
- Known-accepted, still-open items (present in both branches, unchanged
  this session): 71/84 characters have a self-intersecting draft offset
  (detection only, not repaired - `H`/`h`/`e`-type narrow gaps); 57
  inter-character collisions (detection only).

## 1. Built v4 from scratch this session

A friend's 2023 "TypeCylinder" tool (Python + trimesh, found in
`~/Downloads`) does the same job OpenSCAD's `minkowski(cone)` draft step
does - taper a struck character's base wider than its print face - but
via direct per-vertex mesh manipulation instead of a boolean/CSG kernel:
triangulate the flat glyph outline once, then reshape that fixed-topology
mesh with plain coordinate math (parabolic Z-warp for the platen scallop,
a per-vertex outward push for the draft taper). Investigated it, compared
it against `v2/lib/glyph_pipeline.scad`'s real minkowski-cone mechanism,
and re-parameterized the technique against the real Blickensderfer
geometry (`v2/blickensderfer.scad`) instead of the original's arbitrary
pixel constants - that became `v4/`.

Real defects found and fixed while porting (all still in place on
`v2-refactor`):
- **Nesting-depth hole classification**: the original only handled one
  level of "contained by something = hole"; broke on genuinely nested
  glyphs (DejaVu's `0` has a slash mark nested inside its own counter -
  shapely correctly rejects a hole-within-a-hole). Fixed with nesting-
  depth parity (even=solid, odd=hole).
- **Draft direction inverted**: originally had the root flush at the
  surface with the tip protruding outward - backwards. Corrected: the
  platen-bite point (tip) is pinned at the real
  `Element_Diameter/2 + Char_Protrusion`, and the root pushes *inward*
  from there by `separation_mm` (like a nail driven in with a wide head
  proud, not a flush base that only widens sideways).
- **`WireBite` orientation**: was extruding along a pre-rotated axis
  *and* getting the SCAD-order rotation applied a second time -
  double-rotated. Rebuilt with a true 2D shapely hull extruded once along
  local Z, then the transform stack applied exactly once in source
  order.
- **`place_on_cylinder` corruption bug**: reconstructing a mesh via
  `trimesh.Trimesh(vertices=..., faces=...)` with default `process=True`
  silently re-runs vertex merging and can corrupt already-valid geometry
  (reproduced with an *identity* transform alone: vertex count dropped,
  `watertight` flipped `True`->`False` - nothing to do with the actual
  rotation/translation). Fixed with `process=False` since placement is a
  pure coordinate move, no topology change needed. This fix is unrelated
  to the draft-mechanism work and stays regardless of which draft
  approach is active.
- `HollowSpace()`, `CoreGrooves()`, `BottomSlopedSpace()` etc. ported from
  their real `rotate_extrude()`/`linear_extrude(twist=)` SCAD definitions
  via a generic `scad_primitives.revolve_polygon`/`linear_extrude_twist` -
  including a fix for axis-touching profile points creating degenerate
  fan triangles (found via edge-adjacency counts, not by eyeballing).

## 2. Full element assembly + resin supports

Ported `Additive()`/`Subtractive()`/`FullElement()` from
`v2/blickensderfer.scad` close to 1:1 (same origin/orientation
convention), then `lib/resin_rod.scad`/`lib/resin_support.scad`'s
supports (`ResinRod`, `CutGroove`, `SpeedHoleSupport(s)`,
`DrivePinSupport`, `BottomSupports`, `ResinSupport`, `ResinPrint`).
`CutGroove()`'s breakaway ring is built as
`revolve(profile) - revolve(hole1) - revolve(hole2)` since the real
file's 2D difference happens *before* the revolve (each hole becomes a
full 360deg score line, not point perforations).

Found along the way: `HollowSpace`'s real profile (a chamfered/roofed
barrel, not a plain bore) reaches `Element_Diameter/2 - Wall_Min_Thickness
= 15.5mm`; with `separation_mm=2.0` the character root lands at *exactly*
15.5mm too - zero real clearance. This is why the element is built
solid-then-hollowed (one `manifold3d` boolean at the end) rather than
pre-calibrated: the boolean handles either case cleanly regardless of how
tight the margin is.

## 3. Config-driven reorg

Moved from a flat pile of scripts to:
```
generate.py                 entry point
config/blickensderfer.yaml  every real machine parameter + build/alignment settings
lib/{glyph_poc,scad_primitives,blickensderfer}.py
output/                     generated STL + experiments/ (dev-time diagnostic renders)
```
A second machine (Bennett, Postal, ...) is a new YAML file, not a code
change. `lib/blickensderfer.py`'s `configure(path)` loads the YAML and
derives computed values (`Shaft_Diameter`, `Clip_OD`, `Bottom_Slope`,
etc.) the same way the real SCAD file does.

## 4. Character alignment system

Added `glyph_poc.alignment_x_offset`: two base modes (`center` - advance-
box centering, matching `v2`'s native `halign=center` convention, not ink
bbox; `left` - natural FreeType pen origin) each with their own offset,
plus two independent modified-character override groups
(`modified_left_chars`/`modified_right_chars`, each with their own
additional offset). All offsets default to 0 until set in the config -
not yet tuned to real values.

## 5. Detection mechanisms (not repair, by design)

- `back_loops_are_simple()` (shapely `Polygon.is_simple`) flags glyphs
  whose draft offset self-intersects. At `separation_mm=2.0`, 71/84
  characters fail this (confirmed: it's the common case, not an edge
  case) - narrow gaps (`H`/`h`), hole boundaries (`o`/`O`), mouths (`e`).
  **Explicitly accepted as-is** (user call): the resulting solids are
  still watertight/manifold, just not simple.
- `_check_inter_character_collisions()` uses
  `trimesh.collision.CollisionManager` correctly this time (across
  *different* registered objects - what it's actually for; an earlier,
  meaningless attempt in this project's history called it on a single
  mesh expecting self-intersection detection, which it never provided).
  57 adjacent-character pairs currently collide. Accepted as-is.
- `scad_primitives.check_and_repair()`: detect + best-effort auto-repair
  (`trimesh.repair.fill_holes/fix_winding/fix_inversion/fix_normals`) on
  the final assembled solid. Targets combinatorial defects only (holes,
  winding, normals) - confirmed it never actually triggers in practice,
  since self-intersecting-but-otherwise-valid meshes already report
  `watertight`/`winding_consistent`/`is_volume` all `True`.

## 6. The lofted-draft attempt (`v4-real-offset` branch, not merged)

User found a visible artifact on `H` (an X-shaped fold where the two
strokes' expanded bases cross). Investigated a fix:

**Self-union attempt** (`mesh.union(mesh, engine="manifold")`) - tried
first, in-line, before branching. Cleanly resolves outer-boundary
self-intersection (confirmed on `H`: volume 20.24->15.88mm3, fold became
a proper pinched valley) but on hole-boundary self-intersection (`o`/`O`)
the same operation caps the hole with a spurious flat membrane - a
*different*, worse defect. Reverted; this is why detection-only (not
auto-repair) was the accepted state going into the branch.

**The branch**: replaced the per-vertex offset mechanism itself with a
lofted `shapely.buffer()`-based taper (round joins, matching a true
Minkowski-with-cone taper) sliced into N depth slabs between the fully-
expanded back and the zero-offset front, with per-hole tunnel tracking
(a hole gets a flat cap sealing the bottom of its tunnel wherever it
closes). This is architecturally the *right* fix - `buffer()` shrinks/
collapses holes correctly by construction, unlike the naive offset - and
it worked for most letters:

- Fixed two real, separate bugs found in the process:
  1. Cap boundaries and the loft's matching ring were built as separate
     vertex arrays (positionally coincident, index-distinct) - needed one
     explicit `mesh.merge_vertices()` pass to stitch the seams (different
     from the `process=False` corruption bug above - this merge is
     deliberate, not accidental reprocessing).
  2. Winding conventions for outer wall / hole walls / back cap / front
     cap / dead-end caps were verified via actual flip-combination sweeps
     against `is_volume`/`winding_consistent`, not assumed by symmetry -
     an initial "hole walls are the opposite of the outer wall" guess was
     wrong.
- Confirmed clean (watertight/winding-consistent/`is_volume`/visually
  correct, no fold, no membrane) on `H`, `h`, `A`, `l`, `o`, `O`.
- **Did not fully resolve `e`**: a visible spiral/kink near the front cap.
  Root-caused to phase-alignment drift in the arc-length ring
  correspondence between consecutive slabs (`_align_phase`'s discrete
  best-rotation search picked an ~18/96-point, ~67deg jump in a single
  step, right where `e`'s mouth region changes fastest).
- **Two alternative correspondence methods tried, both rejected**:
  - Single-center radial sampling (`resample_ring_by_angle`): silently
    WRONG on non-star-shaped letters - `H`/`h`'s concave notch isn't
    visible from the centroid, so a ray cast toward it sails past
    entirely, producing a geometrically incorrect (but still "valid" by
    the watertight/is_volume checks!) shape. Caught by directly rendering
    the resampled ring against the original, not by trusting the
    validity checks.
  - Nearest-point projection of a fixed reference ring (tried both
    directions: back->front and front->back): can collapse multiple
    reference points onto the same target point where a notch/feature
    merges, producing degenerate zero-area faces and non-manifold edges.
- **Final attempt**: capped `_align_phase`'s search to a small window
  (±`n/20`) so it can never pick a large jump. Fixed `H`/`O`/`A`/`l`/`h`/`o`
  completely. Did **not** fix `e` - confirmed independent of slab count
  (tested up to 96 slabs; the same capped shift is needed at the same
  junction every time). Diagnosis: the remaining correspondence error is
  **non-uniform across the ring** at that junction - no single whole-ring
  rotation can fix a per-region error. This is a real limitation of
  arc-length parameterization + rigid rotation, not a tuning problem.

**Decision**: given the scope this had grown to, reverted the active
branch back to the naive-offset state (`v2-refactor`/`cc396ac`) rather
than ship a partially-working rewrite. The `v4-real-offset` branch and
both its commits are preserved.

## Resuming tomorrow - options for the draft mechanism

If picking this back up, the real options going in (in rough order of
effort):

1. **Leave it as detection-only naive offset** (current `v2-refactor`
   state) - simplest, already working, self-intersection is cosmetic-only
   for print purposes per earlier user calls.
2. **Revisit the lofted approach with a genuinely per-region
   correspondence method** instead of a single global rotation - e.g.
   split each ring into arcs between "landmark" points (sharp corners,
   found via curvature) and align/resample each arc independently, or
   look at established "compatible triangulation" / mesh-morphing
   literature instead of continuing to hand-roll the correspondence
   search. This is real work, not a quick parameter tweak - budget for it
   accordingly. Start from `v4-real-offset`'s `5941e00`, not from scratch;
   the buffer()-based slab structure and the winding-convention findings
   are correct and reusable, only the ring correspondence step needs
   replacing.
3. **Self-union as a per-glyph opt-in**, not blanket: since it's
   confirmed correct for outer-boundary self-intersection and wrong for
   hole-boundary self-intersection, and `back_loops_are_simple()` already
   tells you which contour (outer vs. hole, by index) failed, a
   loop-type-aware version (self-union only when the *outer* loop is the
   one that's non-simple, leave holes alone) was flagged as worth trying
   but never actually attempted this session.

Also still open regardless of which draft mechanism: the 57 inter-
character collisions (no simple automatic fix - would need redoing
placement/size for the colliding pairs) and alignment offsets (mechanism
built, all values still at their 0.0 no-op defaults).
