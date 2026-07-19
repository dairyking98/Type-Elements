# v4 session log

Chronological record of this session's work, for resuming later. See
`README.md` for the architecture/usage reference of the *current* state;
this file is the history and the "what's next."

## Where things stand right now

- **Active branch: `v2-refactor`.** The draft taper mechanism has been
  completely rewritten this session: `build_glyph` in `lib/glyph_poc.py`
  now builds it via a real Minkowski sum (`manifold3d.Manifold.
  minkowski_sum`), replacing the per-vertex outline-offset approach (and
  its self-union patch, added and then removed again this same session -
  see below) entirely. That old code is gone, not kept behind a flag.
- Every character that was broken at any point this session - `H`, `e`,
  `m`, `^`, `M`, `A`, `i`, `o`, `0` - is now confirmed clean: watertight,
  winding-consistent, `is_volume=True`, no self-intersection possible by
  construction, correct platen scallop on both curvy and straight-stroke
  letters.
- **Real cost accepted: generation time.** A boolean CSG call replaces
  plain coordinate math. ~60-70s for the full 84-character ring + assembly
  at the config's default quality (`points_per_mm=15`, `cone_segments=16`),
  ~16-35s at faster settings (`--points-per-mm 8 --cone-segments 12` or
  lower) with only minor visual quality loss - see README's "Performance"
  section.
- **Known-accepted, still open, unrelated to the draft mechanism:** 61
  inter-character collisions at `separation_mm=2.0` (confirmed real via
  direct boolean intersection, sitting at the embedded root end - not
  visible from outside), and the `HollowSpace` margin flag (flickers
  `True`/`False` run to run from floating-point noise at a razor-thin
  boundary - documented, not new).
- **Reverted and NOT currently reapplied:** earlier in this session,
  `separation_mm=1.0` was found to eliminate the inter-character
  collisions entirely (at the cost of less embedding-depth margin), and a
  `logo.radial_offset_mm` config knob was added to pull `LogoText` off a
  near-miss with DHIATENSOR column 2. Both were undone by a full revert to
  the last commit partway through this session (see "The detour" below)
  and were not reintroduced during the Minkowski rewrite that followed -
  the config right now still has `separation_mm=2.0` and no
  `logo.radial_offset_mm` override. Worth deciding whether to reapply
  these, since they were real, verified fixes for real, verified problems.

## 1. Started from last session's resume point: the naive-offset baseline

Picked up with the per-vertex draft offset (`make_back`/
`orthogonal_offset_vertex`/`join_front_back`) still in its accepted,
detection-only state (self-intersection on tight glyphs, not repaired).
Investigated a visible artifact on the ring: the `H` self-intersecting
fold, first suspected to be caused by `LogoText`'s "Leonard Chau 2025"
engraving crossing the DHIATENSOR `k`/`K`/`_` column (a real, separate,
near-miss - the logo character `a` in "Leonard" landed within 0.17deg of
that column's angle, only 0.37mm of Z clearance) - fixed by adding a
`logo.radial_offset_mm` knob and re-sweeping it against both the character
band and `SpeedHoles` clearance.

But the fold on `H`/`k`/`K` turned out to be a separate, pre-existing
issue: the same self-intersecting-draft-offset limitation documented in
`README.md`, just grown large enough to be visually obvious once
`DEFAULT_SEPARATION_MM` had been bumped from the real 0.5mm to 2.0mm in an
earlier session (for embedding-depth margin - see the code comment history
for why). Swept `separation_mm` from 0.5 to 2.0 and confirmed the fold's
*magnitude* scales with it (expansion width = `separation_mm *
tan(27.5deg)`), even though the underlying self-intersection is present at
every value tested, even the real 0.5mm.

This led to checking the actual physical tradeoff directly:
`embedding_depth_mm = separation_mm - Char_Protrusion` - at the real
0.5mm value, the character root lands EXACTLY on the main cylinder's own
surface radius, zero embedding. Confirmed the self-intersecting fold
becomes visually obvious somewhere between `separation_mm=0.6` and `0.7`.

## 2. Gated self-union repair - implemented, then found to be unsafe

Implemented a loop-type-aware self-union repair in `build_glyph`:
classify each outline loop as outer-island vs. hole using the *un-offset
front loop's* signed area (a severely self-intersecting hole, like `e`'s,
can flip its own post-offset signed area, so classification has to happen
before the offset is applied) - self-union only when every non-simple loop
is an outer island, never a hole (confirmed earlier: self-union caps a
hole with a spurious flat membrane instead of fixing it). This cut
unresolved self-intersection from 71/84 to 11/84 at `separation_mm=0.5`.

User found this had NOT actually fixed everything - `^` still showed a
visible artifact. Investigation found the real problem: `manifold3d`'s
`mesh.union(mesh)` on a MULTI-ISLAND glyph (a disjoint dot separate from
its stem - `i`, `j`, `;`, `?`) doesn't reliably keep the islands separate;
it can weld them together and lose real volume (confirmed on `i`:
12.47+3.25=15.72mm3 of real islands before repair, only 10.85mm3 survived
after, replaced by zero-volume debris). Also found manifold3d's boolean
routinely produces dozens of disconnected zero-volume debris slivers even
on genuinely single-island repairs (36/48 repaired characters, up to 94
slivers on `8`) - harmless to `watertight`/`is_volume` checks but real
debris in the final STL.

Fixed both: gated self-union to single-island glyphs only (multi-island
non-simple glyphs, 4/84, stay detection-only), and stripped near-zero-
volume components after any self-union. Net result at that point: 44
auto-repaired, 27 genuinely unrepaired (down from 71 broken originally).

## 3. The detour: "completely reapproach this at a different angle"

Tried `separation_mm=2.0` (the original, most-broken setting) with the
gated self-union repair active - 48 auto-repaired, 23 still unrepaired,
watertight throughout. But then `m` still showed a visible fold even with
the repair in place, and the user called for a full stop: "characters
still fucking up... undo all measures we did." Reverted `config/
blickensderfer.yaml`, `lib/blickensderfer.py`, `lib/glyph_poc.py` to the
last commit (`67ea8d4`) - back to the naive-offset baseline, detection-
only, no self-union, none of the separation/logo-radius tuning above.

Discussed real alternatives instead of continuing to patch the per-vertex
technique: (1) resume the unfinished `shapely.buffer()`-based lofted taper
on the (still-preserved) `v4-real-offset` branch, or (2) check whether a
REAL Minkowski sum via `manifold3d` (which this whole project originally
avoided for performance reasons) is viable now. Checked - `manifold3d`
exposes `Manifold.minkowski_sum`/`Manifold.cylinder` directly. Prototyped
it on `H`/`e`/`m`/`o`/`i`/`^` (the hardest failures): all watertight,
winding-consistent, `is_volume=True`, zero self-intersection by
construction - including `e` and `m`, which nothing in the naive-offset
line of work had ever fully resolved. Measured cost: ~16-66s for the full
ring depending on quality settings, vs. ~3-6s before. Decided to build
this in as the real replacement.

## 4. Building the real Minkowski-sum draft mechanism

Rewrote `build_glyph` in `lib/glyph_poc.py`: extrude the flat glyph into a
thin prism, `Manifold.cylinder()` for the draft cone, `minkowski_sum()`,
convert back to `trimesh`. Removed the now-dead `back_loops_are_simple`/
`classify_back_loops`/self-union machinery entirely (kept `make_back`/
`orthogonal_offset_vertex`/`join_front_back`/`make_front`, since
`build_flat_text` - `LogoText`'s flat-engrave pipeline - still uses them
with zero offset, which never had a self-intersection problem). Wired a
new `cone_segments` knob through `TextRing`/`Additive`/`FullElement`/
`ResinPrint`/`generate.py`/the config, alongside `points_per_mm`. Updated
`TextRing`'s reporting to drop the now-impossible self-intersection
checks, keeping only inter-character collision detection (a genuinely
separate, placement-driven issue).

Found and fixed three real, separate bugs while building this, in order:

**Bug 1 - doubled depth.** First version extruded the prism to the full
`separation_mm` height AND gave the cone its own full `separation_mm`
height. Minkowski sum ADDS extents in each dimension, so the result came
out `[0, 2*separation_mm]`, not `[0, separation_mm]` (confirmed: `H`'s
z-range was `[0, 4.0]` at `separation_mm=2.0`). Fixed by shrinking the
prism to a thin sliver (`tip_h`, ~0.01mm) sitting at the tip end, letting
the cone alone carry (almost) the full depth.

**Bug 2 - cone origin/dilation direction reversed.** User caught this:
"the minkowski cone shape origin is wrong, the origin should be at the
tip." `manifold3d`'s `cylinder()` places its local origin at the
`radius_low` end - the first fix attempt flipped `radius_low`/
`radius_high` AND translated, which canceled out and put the dilation
back at the TIP instead of the root (confirmed directly: tip came out
wider than root, exactly backwards - `watertight`/`is_volume` don't catch
a reversed-but-still-valid draft, only checking cross-section width at
`z=0` vs. `z=separation_mm` does). Fixed by keeping the cone's original
wide-at-bottom/apex-at-top construction and only translating the whole
cone by `-cone_height`, landing the apex exactly at the origin. Verified:
root width minus tip width = exactly `2*expansion_width_mm`.

**Bug 3 - manifold3d's raw triangulation noise.** User spotted "facet
angles are inconsistent... like a poorly done minkowski" on straight
edges (`M`'s strokes). Confirmed: a single straight wall came out as ~24
near-coplanar micro-triangles with normals wobbling by a fraction of a
degree - real CSG-algorithm noise, not a geometry error (face-normal
check on the wall showed the wobble directly; `Manifold.simplify()`
collapsed 2918 triangles down to 182 at even 0.0005mm tolerance, into a
single flat face per straight run). Added `simplify_tolerance_mm` (default
0.005mm, config + CLI knob) applied to the `minkowski_sum` result.

User also asked whether reducing the prism's height ("just do a slice of
the curved part") would speed up the Minkowski call. Tested directly:
face count (and timing) is unaffected by `tip_h` - a straight extrusion's
face count depends on its 2D cross-section, not its Z-thickness. The real
cost driver is `points_per_mm` (already exposed), and the cap
triangulation is already minimal (`triangle_args='p'`, no added Steiner
points) - no free win available there.

## 5. Bug 4 - platen curve applied in the wrong order

User: "are you doing minkowski first, then adjusting the top surface for
platen curvature? ... the draft angle loses angle spec after adjustment."
Correct diagnosis. The version at that point warped only the SWEPT
RESULT's top ring into the platen parabola, after the Minkowski sum -
meaning the cone's own geometry (and therefore the realized draft angle)
was only ever valid for a flat tip; nudging just the final ring left the
walls built as if the tip were still flat. Visible specifically on
horizontal runs far from `radius_y_offset` (the platen's tangent point) -
`M`/`A`'s bottoms, not `L`/`I`'s mostly-vertical runs which stay close to
it. Confirmed this also matches how the real `v2/lib/glyph_pipeline.scad`
avoids the problem: `PlatenCutout()` is subtracted from the base
extrusion BEFORE the `minkowski()` call there, never patched onto the
result after.

Fixed by moving the platen Z-warp to the PRISM's top cap, before the
Minkowski sum, instead of the swept result's top ring after. Verified
numerically (root width minus tip width still exactly
`2*expansion_width_mm` - the warp doesn't disturb the dilation amount)
and visually (`M`/`A`'s bottoms now match `L`/`I`'s clean quality, no
faceting).

Also had to re-verify the earlier `simplify()`-before-warp ordering bug
from step 4 didn't reappear: `simplify()` must run on the CURVED result
now (after the prism warp + Minkowski sum), not on a still-flat
intermediate, or it aggressively over-collapses large flat regions before
they're curved (confirmed: straight-stroke letters lost platen-curve
fidelity while curvy letters looked fine only because their outline's own
curve-driven vertex density happened to survive). Final order per
character: warp prism top cap -> Minkowski sum -> simplify.

## Resuming later

1. **Reapply or re-decide on the reverted `separation_mm`/`logo.
   radial_offset_mm` fixes** (see "Where things stand" above) - they were
   real, verified fixes, just not part of the Minkowski rewrite's scope.
2. **Inter-character collisions** (61 at `separation_mm=2.0`) - no
   automatic fix short of redoing placement/size, or accepting the
   `separation_mm=1.0` tradeoff (verified to eliminate them, at the cost
   of embedding-depth margin).
3. **Performance** - if ~60-70s at full quality becomes annoying, the
   `points_per_mm`/`cone_segments` knobs are the lever; both are already
   wired through config + CLI.
4. Alignment offsets (mechanism built, all values still at their 0.0
   no-op defaults) - untouched this session.
