"""
Constant-draft-angle taper via stacked thin-slab 3D solid offsets, replacing
every earlier attempt in this directory (draft(), 2D wire offset()+loft(),
per-piece island/hole decomposition). None of those survive real glyph
topology - see glyph_poc.py (draft() rejects curved strokes outright) and
draft_via_loft.py / draft_via_plateau.py (2D offset() either self-intersects
or, on a pinched hole like an "8"'s waist, hangs or throws with no way to
recover the correct split-into-two-cones topology - confirmed experimentally,
not guessed).

Key discovery: build123d's offset() wrapper is not the same as OCC's actual
offset capability. It calls Solid.offset_3d(), which calls OCC's
BRepOffsetAPI_MakeThickSolid - a genuine 3D solid offset (grow/shrink the
whole boundary by a distance), NOT a 2D wire offset. This primitive already
handles topology changes (a pinched shape splitting into two disjoint
solids) automatically and correctly - verified experimentally on a synthetic
hourglass solid: it returns a Compound containing two separate Shells with
correct, symmetric volumes, degenerating cleanly to zero-volume points at
the extreme. build123d's wrapper never surfaces this: Solid.cast() only
knows how to unwrap a single Solid and throws KeyError the moment OCC
legitimately returns a Compound. This module bypasses the wrapper and talks
to BRepOffsetAPI_MakeThickSolid directly (_robust_offset_3d).

Second discovery: applying one large offset to a whole real glyph in a
single call is NOT reliable (multiple simultaneous topology events - e.g.
"%"'s three separate loops, "g"'s bowl+descender - exceed what even this
robust primitive resolves in one shot; some characters returned inverted/
self-intersecting garbage). The fix is to discretize depth into many thin
slabs and apply a small, incrementally growing offset per slab, then union
the slabs together. Each step is small enough to stay inside what the
primitive can resolve cleanly, and whatever branching happens at a given
depth (a hole pinching shut and splitting, in either direction) falls out
of the per-slab offset automatically - no manual pinch detection, no wire
splitting, no island/hole/nesting classification.

This directly encodes "constant draft angle relative to a fixed axis": the
offset direction is the solid's own boundary normal at every slab, and the
offset magnitude grows linearly with depth along the same fixed axis for
every slab, matching what minkowski(cone) does in v2 (grows the boundary by
a depth-dependent radius) without borrowing its 2D-curve machinery. Not yet
attempted: making the offset axis follow the platen's cylindrical radius
instead of a flat linear depth, which would need the reference direction
per-slab to be recomputed relative to the platen center rather than assumed
constant - left for a follow-up once the flat-axis version is validated.

The "exclude the end caps from the offset" (openings=) parameter of
BRepOffsetAPI_MakeThickSolid was tried and found unreliable on real glyph
geometry (fails immediately even at trivial offsets, works fine on
synthetic test solids) - root cause not chased down. Sidestepped instead:
offset the whole thin slab including its own caps (which does work), then
trim the result back to the slab's true z-range with a box intersection to
undo the caps' incidental shift.
"""

from build123d import *
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
from OCP.TopTools import TopTools_ListOfShape
from OCP.GeomAbs import GeomAbs_JoinType
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCP.TopAbs import TopAbs_ShapeEnum
from OCP.TopoDS import TopoDS

FONT = "DejaVu Sans Mono"
FONT_SIZE = 3.7
TARGET_R2 = 1.04  # minkTextR(55) - Blickensderfer's calibrated draft radius
CAP_H = 2.0        # Mink_H_Fixed
CORE_H = 4.0        # EXTRUDE_DEPTH(6) - CAP_H
TIP_X = 17.5
N_SLABS = 12


def _robust_offset_3d(solid, amount, join=GeomAbs_JoinType.GeomAbs_Intersection, tol=1e-4):
    """3D solid offset via the raw OCC call. build123d's Solid.offset_3d()
    wraps the same underlying BRepOffsetAPI_MakeThickSolid but crashes
    (KeyError on TopAbs_COMPOUND) exactly when the offset legitimately
    splits the shape into multiple solids - which is the case we need to
    handle, not avoid. Returns a list of Solids (usually 1, sometimes more
    at a split, occasionally 0 if fully collapsed)."""
    empty = TopTools_ListOfShape()
    builder = BRepOffsetAPI_MakeThickSolid()
    builder.MakeThickSolidByJoin(
        solid.wrapped, empty, amount, tol,
        Intersection=True, RemoveIntEdges=True, Join=join,
    )
    builder.Build()
    if not builder.IsDone():
        raise RuntimeError("offset not done")
    raw = builder.Shape()
    if raw is None or raw.IsNull():
        raise ValueError("null shape")

    shape_type = raw.ShapeType()
    if shape_type == TopAbs_ShapeEnum.TopAbs_SOLID:
        solids = [Solid(raw)]
    elif shape_type == TopAbs_ShapeEnum.TopAbs_SHELL:
        solids = [Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(raw)).Solid())]
    else:
        comp = Compound(raw)
        solids = list(comp.get_type(Solid))
        if not solids:
            solids = [
                Solid(BRepBuilderAPI_MakeSolid(shell.wrapped).Solid())
                for shell in comp.get_type(Shell)
            ]

    fixed = []
    for s in solids:
        if s.volume < 0:
            s.wrapped.Reverse()
        if s.volume > 1e-9:
            fixed.append(s)
    return fixed


def _trim_to_slab(solid, z0, z1, half_extent=100.0):
    """Offsetting a thin slab shifts its own end caps too (no reliable way
    found to hold them fixed - see module docstring). Undo that by cutting
    back to the slab's true depth range with a box intersection."""
    box = Box(2 * half_extent, 2 * half_extent, z1 - z0)
    box = box.moved(Location((0, 0, (z0 + z1) / 2)))
    try:
        result = solid.intersect(box)
    except Exception:
        return []
    if result is None:
        return []
    solids = result.solids() if hasattr(result, "solids") else [result]
    return [s for s in solids if s.volume > 1e-9]


def drafted_letter_slabs(char, target_r2=TARGET_R2, n_slabs=N_SLABS, font_size=FONT_SIZE):
    with BuildSketch() as sk:
        Text(char, font_size=font_size, font=FONT, align=(Align.CENTER, Align.CENTER))
    sketch = sk.sketch

    core = extrude(sketch, amount=-CORE_H)

    dz = CAP_H / n_slabs
    pieces = []
    slab_failures = 0
    for k in range(n_slabs):
        z_near = -(CORE_H + k * dz)       # closer to plateau (less offset)
        z_far = -(CORE_H + (k + 1) * dz)  # closer to tip (more offset)
        amount = target_r2 * (k + 1) / n_slabs  # offset at this slab's far edge

        thin = extrude(sketch, amount=-dz).moved(Location((0, 0, z_near)))
        try:
            offset_solids = _robust_offset_3d(thin, amount)
        except Exception:
            slab_failures += 1
            continue

        for s in offset_solids:
            pieces.extend(_trim_to_slab(s, z_far, z_near))

    result = core
    for p in pieces:
        try:
            result = result + p
        except Exception:
            pass
    return result, slab_failures, n_slabs


if __name__ == "__main__":
    import string

    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    ok, partial, failed = [], [], []
    for ch in chars:
        try:
            solid, slab_failures, n_slabs = drafted_letter_slabs(ch)
            if slab_failures == 0:
                ok.append(ch)
            else:
                partial.append((ch, slab_failures, n_slabs))
        except Exception as e:
            failed.append(f"{ch}({type(e).__name__})")

    print(f"clean (0 slab failures): {len(ok)}/{len(chars)}  {''.join(ok)}")
    print(f"partial (some slabs failed but char completed): {len(partial)}  {partial}")
    print(f"failed entirely: {len(failed)}  {failed}")
