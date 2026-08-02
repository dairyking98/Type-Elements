---
layout: page
title: Behind the scenes
---

A few of the concrete bugs and dead ends that shaped v4's current
design. The full, chronological version of all of this lives in the
[changelog](changelog).

## The double-counted overlap

Early assembly code used `trimesh.util.concatenate()` to combine
characters onto the cylinder and cut the platen. Concatenation just
merges vertex/face arrays - it doesn't resolve any boolean intersection.
Wherever a character's embedded root overlapped the main cylinder, or
two characters overlapped each other, both surfaces stayed fully intact
and superimposed, with no new edge formed at the real intersection. This
was caught by a 1148mm³ volume discrepancy where a naive sum of parts
didn't match the assembled whole. Every assembly boolean now goes
through real `manifold3d` operations instead.

## The per-vertex draft offset that couldn't be trusted

Before the Minkowski sum, v4's draft taper was a per-vertex outline
offset adapted from a friend's 2023 mesh-manipulation tool. It had no
topology awareness: a fixed-distance offset can't detect when a glyph's
local geometry - a narrow gap, a tight concave corner - is too small to
support that distance, and just folds through itself instead of
erroring. A gated self-union repair patched most single-island glyphs
but both left some broken (`e`'s hole boundary still folded) and broke
others that had been fine (`i`'s dot got welded into its stem, losing
real volume). A real Minkowski sum can't self-intersect on any input
topology, which is why it replaced the per-vertex approach and all its
patches outright rather than getting patched further itself.

## The sail that wasn't there

A "sail/spike" artifact was suspected mid-development - a triangle
appearing to span nearly a character's full height and depth on
AverageMono's 'd'/'p'/'k'/'N'/'V'. The working theory was that the real
platen boolean needed help cutting cleanly along a long, adaptively
unsubdivided straight edge, so a shared-Y-breakpoint mechanism was built
to match the platen cylinder's own facet step. It introduced a new
defect of its own (degenerate thin triangles wherever a breakpoint-dense
edge met an already-dense curve region, since inserting a boundary
vertex doesn't constrain the interior triangulation to actually connect
across the stroke). Once the original concern was re-checked with a
properly size-normalized metric - no face may exceed 1.5x that
character's own bounding-box diagonal - the answer was zero faces
exceeding that bound, across every character in both the cylinder and
spherical glyph families. The breakpoint mechanism was removed; the real
boolean was already subdividing exactly where it needed to, for free.

## Un-simplifying

`Manifold.simplify()` used to run at several points in the glyph
pipeline, intended as output cleanup. It was disabled everywhere first
(commented out, in case a real regression needed it back), then deleted
outright once that risk was confirmed gone in practice. One call site
had a real, independently-documented reason to exist: a 552x speedup
avoiding a 2206-second build on a single character (Alma Mono 'M'), by
shrinking the Minkowski sum's *input* face count rather than cleaning
its output. Disabled anyway, then re-tested directly against that exact
regression case - the same character, font, and real Minkowski sum
completed in 5.75 seconds with zero `simplify()` calls anywhere. The
adaptive contour tracing that replaced the old fixed-rate glyph sampling
had already fixed the root cause that call was compensating for: a
bloated, CSG-noise-heavy boolean-cut mesh no longer exists to explode
through Minkowski in the first place.
