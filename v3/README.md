# v3 experiment: build123d (Open Cascade B-rep) instead of OpenSCAD

Exploring whether a Python + build123d pipeline can replace `v2/lib/glyph_pipeline.scad`'s
`minkowski(diff_result, draft_cone)` draft-angle step (`LetterText()`, v2/lib/glyph_pipeline.scad:356)
with native B-rep operations. v1 and v2 are untouched — this is a separate, parallel tree.

## Setup

```
cd v3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## `glyph_poc.py`

Ports a single character's `LetterText()` (extrude glyph → platen cutout →
draft angle) using Blickensderfer's real constants (`Element_Diameter=34`,
`Platen_Diameter=32.258`, `Char_Protrusion=0.5`, `Font_Size=3.7`,
`Mink_Draft_Angle=55`). Font swapped to DejaVu Sans Mono since
`Blick_Script_Leo` isn't installed on this machine — only pipeline mechanics
are under test, not the real typeface.

Run it:

```
source .venv/bin/activate
python3 glyph_poc.py
```

Produces `out_carved_no_draft.stl`, `out_drafted.stl`, `out_drafted.step`.

## Finding: `draft()` does not cleanly replace `minkowski(cone)`

OCC's classic draft algorithm (`BRepOffsetAPI_DraftAngle`, exposed as
build123d's `draft()`) was tested against several letterforms and angles:

| char | 2°  | 5°  | 10° | 27.5° (real target, = Mink_Draft_Angle/2) |
|------|-----|-----|-----|------|
| L (straight strokes) | OK | OK | OK | OK |
| A (straight strokes) | OK | fail (self-intersect) | fail | fail |
| I (straight, narrow) | OK | OK | fail (self-intersect) | fail |
| O (curved strokes)   | fail | fail | fail | fail |

Two distinct failure modes:
- **Self-intersection** (`Standard_ConstructionError`): expected — a 27.5°
  taper over a 6mm extrude depth exceeds most stroke widths. Not a build123d
  bug, just geometry; minkowski has the same limit, it just silently produces
  garbage/self-intersecting mesh instead of erroring.
- **Curved strokes rejected outright** (`ValueError: Draft not supported on
  face(s) with geometry: EXTRUSION`), independent of angle or the platen
  boolean (reproduced on the bare extruded "O" with no cutout at all). OCC's
  classic draft only accepts side faces swept from straight-line profile
  segments; b-spline-swept faces from curved letterforms (i.e. most real
  fonts, most letters) are rejected unconditionally.

**Read:** `minkowski(cone)` in OpenSCAD is slow but shape-agnostic. `draft()`
is fast but only usable on all-straight-stroke glyphs at shallow angles — not
viable as a drop-in replacement for the real 27.5° draft across a real font.

**Next thing to try:** `loft()` between two profiles (base glyph outline +
a scaled/offset top profile) instead of `draft()`. Loft builds a NURBS
surface between arbitrary wire profiles and isn't restricted to straight-line
sweeps, so it should handle curved letterforms where `draft()` can't. Not
yet implemented here.

## `draft_via_loft.py` / `draft_via_plateau.py`: 2D wire `offset()` + `loft()`

Decomposes each glyph into per-piece wires - one per island (outer wire),
one per hole (inner wire) - and lofts each piece independently between its
own un-offset shape (at the core/cap boundary, the "plateau") and a 2D
`offset()` copy of that wire (grown for islands, shrunk for holes), then
boolean-reassembles: `result = core + union(islands) - union(holes)`.
`draft_via_plateau.py` adds a nesting-depth cutoff on top of this (a face
whose centroid falls inside another face's *outer* boundary - ignoring that
other face's own holes, which matters: a point inside a hole is *not*
inside that face's material - is treated as a second-level island and
skipped rather than mistakenly grown as if it were independent top-level
island; verified experimentally that build123d's `sketch.faces()` already
flattens nested islands into separate top-level `Face` objects with no
parent/child link, so without this check every nesting depth gets grown).

**Finding: 2D wire `offset()` cannot reliably shrink concave/pinched holes.**
Built a synthetic "hourglass" hole (two lobes joined by a 1.2mm-wide waist)
and swept the shrink radius: works fine up to radius 0.5, then at exactly
0.6 (where the waist would close) `offset()` doesn't split into two loops -
it throws `RuntimeError: Unexpected result type` with no way to recover the
correct two-separate-cones topology. Worse: on the real font, character
`'q'` doesn't throw at all, it **hangs** (still running after 30s) - so the
halve-the-radius-and-retry fallback in these two scripts isn't even safe,
it can stall indefinitely depending on glyph geometry. This is a dead end
for the reason stated up front: constant-draft-angle tapering needs to
survive arbitrary real-font topology, not just the shapes that happen not
to pinch.

## `draft_via_slabs.py`: 3D solid offset, stacked by depth (in progress)

**Key discovery:** build123d's `offset()` is not the same operation as 2D
wire offset when given a `Solid` - `Solid.offset_3d()` calls OCC's
`BRepOffsetAPI_MakeThickSolid`, a genuine **3D solid offset** (grow/shrink
the whole boundary by a distance in 3D, not a planar-curve offset). Verified
on the same synthetic hourglass shape, but as a solid peg instead of a bare
wire: this operation *does* split a pinch into two separate, correctly-sized,
symmetric solids (confirmed by volume and centroid), and degrades gracefully
to two zero-volume points at the extreme, instead of throwing or hanging.
This is the topological robustness `minkowski(cone)` has (it's a true
Minkowski sum, handled by CGAL's Nef polyhedra under OpenSCAD) that 2D wire
`offset()` doesn't.

The catch: **build123d's own `offset()` wrapper never surfaces this**, it
calls `Solid.cast()` on the raw OCC result, which only knows how to unwrap
a single `Solid` and throws `KeyError: TopAbs_COMPOUND` the instant OCC
legitimately returns multiple solids from a split - i.e. it crashes on
exactly the case that matters. `draft_via_slabs.py` bypasses the wrapper
and talks to `BRepOffsetAPI_MakeThickSolid` directly (`_robust_offset_3d`),
downcasting whatever comes back (bare `Solid`, bare `Shell`, or a
`Compound` of either) into a list of `Solid`s itself.

A second discovery: offsetting a **whole real glyph in one large step**
(single offset amount, no per-piece decomposition, no depth-slicing) is
*not* reliable even with the robust primitive - characters with multiple
simultaneous topology events (`'g'`'s bowl+descender, `'%'`'s three
disjoint loops) fail outright or return inverted/self-intersecting volumes.
The fix attempted: discretize `CAP_H` into `N_SLABS` thin slabs, offset each
by a small, linearly-increasing-with-depth amount, and union the slabs -
each step small enough to stay inside what the primitive resolves cleanly,
letting whatever branching happens at a given depth fall out automatically
instead of being detected/split by hand. This also means no per-piece
island/hole decomposition is needed at all: a single positive offset on the
*whole* cross-section simultaneously grows the outer boundary and shrinks
holes (growing material into the void is exactly what "shrinking a hole"
means), so the nesting-depth logic from `draft_via_plateau.py` becomes
unnecessary if this works out.

Tried and abandoned: passing the slab's own end caps as `openings=` (so
only the side walls would move, and depth would stay exact without needing
a trim step) - fails immediately (`BRep_API: command not done`) on real
glyph geometry even at trivial offsets, despite working fine on the
synthetic test solid. Root cause not chased down. Sidestepped instead: offset
the whole thin slab including its caps (which does work structurally), then
trim back to the slab's true z-range with a box intersection to undo the
caps' incidental shift.

**Status: not working yet, and found a real correctness bug, not just a
reliability one.** `'A'` runs clean end-to-end (0/12 slab failures, correct
bbox, sane volume) but most other characters fail most slabs. Worse than a
clean failure: `'a'` produced *silently corrupt* output - a 6674mm³ volume
with a ±100mm bounding box, meaning the 200mm trim box itself leaked into
the unioned result unclipped, with no exception raised. Volume-only sanity
filtering (`> 1e-9`) does not catch this. Suspect the thin slabs
(`dz ≈ CAP_H/N_SLABS ≈ 0.17mm` at `N_SLABS=12`) are pushing the offset
tolerance (`tol=1e-4`, left at default) into numerically unstable territory,
but this has not been verified - no run yet with fewer/thicker slabs or a
tighter tolerance, and no bbox-vs-slab-footprint sanity check has been added
to catch corrupt results before they enter the union. Both are the natural
next steps before trusting this approach further.
