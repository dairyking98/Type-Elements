---
layout: page
title: How it works
---

## The draft taper: a real Minkowski sum

Every struck character needs a draft angle - the print face is narrower
than the root that embeds it in the type element body, like a rivet.
v4 builds this by taking the flat, triangulated glyph outline and
computing a real Minkowski sum (`manifold3d.Manifold.minkowski_sum`)
against a cone. A Minkowski sum can't produce a self-intersecting result
on any input topology, which is the whole reason it replaced v4's first
approach: a hand-rolled per-vertex outline offset (adapted from a
friend's 2023 "TypeCylinder" tool) that folded through itself on narrow
glyph features - 71 of 84 characters failed a `shapely` simplicity check
under that scheme. OpenSCAD's own `minkowski()` was also ruled out, for
being too slow at production scale.

## Real booleans, not concatenation

Assembling the type element - characters onto the cylinder, the platen
cutout, the final `Additive - Subtractive` - goes through real
`manifold3d` boolean operations (`sp.union_all()` /
`Manifold.batch_boolean()`), never `trimesh.util.concatenate()`.
Concatenation just merges vertex/face arrays with no boolean resolution
at all - wherever two surfaces overlapped, both stayed fully intact and
superimposed, with no new edge at the actual intersection. This shipped
as a real bug once, caught via a 1148mm³ double-counted-overlap volume
discrepancy.

## Adaptive glyph outline sampling

Glyph outlines are sampled with recursive de Casteljau Bezier
subdivision to a flatness tolerance in mm, not a fixed points-per-mm
rate. Straight strokes get zero extra subdivision (they're already
flat); curves get exactly as many points as their own curvature needs.
The old fixed-rate scheme left 46-71% of a straight-stroke glyph's
points geometrically redundant - and since Minkowski cost scales with
the product of the two operands' face counts, that redundancy directly
inflated build time. Switching to adaptive sampling measured a
1.3x-4.5x real build-time reduction with no correctness loss (volumes
matched the old output to within 0.03-1% across both quadratic/TrueType
and cubic/CFF fonts).

## Curvature is applied before the sum, never after

Curvature or warp on the base solid (the platen cutout, for example) is
applied to the flat shape *before* the Minkowski sum runs, never patched
onto the already-swept result afterward. A draft angle is only valid for
the exact shape it was summed with; patching a curve on after the fact
leaves the walls built as if the tip were still flat.

## Real machine numbers live in config, not code

Every physical dimension, tolerance, offset, and facet-count/resolution
constant lives in that machine's `config/*.yaml`, never hardcoded in
Python. This holds even for numbers that feel like implementation
details (circle segments, revolve sections) - if a facet count needs
tuning for a real reason, it's a new knob in the config's `quality:`
section, the same as every other one.

## No manual help needed for the platen cut

An early investigation suspected the real platen boolean needed manual
Y-breakpoint insertion to cut cleanly along a long, adaptively
unsubdivided straight edge (a stem on 'd'/'l'/'k', for example). A
breakpoint-insertion mechanism was built, found to introduce its own
defect (a fan of degenerate triangles wherever a breakpoint-dense edge
met an already-dense curve region), and removed again once a properly
size-normalized check confirmed the original concern was a false
positive - 0 faces exceeding 1.5x a character's own bounding-box
diagonal, across every character in both the cylinder and spherical
glyph families. The real boolean subdivides a stem's wall finely
wherever the platen curve actually changes, and leaves it as one larger
(but still correct) facet wherever it doesn't - for free, with no
pre-conditioning of the input contour.
