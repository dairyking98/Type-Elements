"""
Refinement of draft_via_loft.py's island/hole decomposition, recovered after
a crash lost the in-progress version. Same per-piece loft mechanism, but
explicitly capped at one level of nesting instead of treating every Face
build123d's sk.sketch.faces() returns as an independent top-level island.

sketch.faces() flattens nesting: an island sitting inside a hole (e.g. a
counter-punch shape) comes back as its own separate Face, unconnected to its
parent's wire structure except by physical containment (verified experimentally
- see is_nested()). draft_via_loft.py looped over every face as if it were a
top-level island, which silently grows nested islands too - not what the
minkowski(cone) original does, and not what was asked for.

This version instead:
  1. Builds a single flat "plateau" cross-section per top-level face at the
     core/cap boundary (z=-CORE_H) - literally just that face's own
     unoffset shape, reused as the common loft start for both its island-grow
     and its hole-shrink pieces.
  2. Lofts the plateau's outer wire to a grown copy (island) and each of the
     plateau's own inner wires to a shrunk copy (holes) - one layer deep.
  3. Any face nested inside another face's outer boundary (island-in-a-hole)
     is skipped outright: not tapered, not re-added, so it merges into
     whatever cavity encloses it in the tapered cap region. That's the
     intentional "inner island fails" behavior - real Latin glyphs don't
     nest this deep, so it's a deliberate simplification, not an oversight.
"""

from build123d import *

FONT = "DejaVu Sans Mono"
FONT_SIZE = 3.7
TARGET_R2 = 1.04  # minkTextR(55) - Blickensderfer's calibrated draft radius
CAP_H = 2.0        # Mink_H_Fixed
CORE_H = 4.0        # EXTRUDE_DEPTH(6) - CAP_H
TIP_X = 17.5


def _offset_with_fallback(face, amount):
    for kind in (Kind.INTERSECTION, Kind.ARC):
        try:
            return offset(face, amount=amount, kind=kind).faces()[0]
        except Exception:
            continue
    return None


def _loft_from_plateau(wire, add: bool, target_r2=TARGET_R2, min_r2=0.02):
    """Loft a single simple wire (no holes) from its own plateau shape (at
    z=-CORE_H) to an offset profile (at z=-(CORE_H+CAP_H)), shrinking the
    offset radius until it succeeds or gives up. Returns (solid, achieved_r2)
    or (None, 0) if nothing worked."""
    plateau_face = Face(wire)
    r2 = target_r2
    sign = 1 if add else -1
    while r2 >= min_r2:
        grown = _offset_with_fallback(plateau_face, sign * r2)
        if grown is not None:
            try:
                plateau = plateau_face.moved(Location((-CORE_H, 0, 0)))
                tip = grown.moved(Location((-(CORE_H + CAP_H), 0, 0)))
                return loft([plateau, tip]), r2
            except Exception:
                pass
        r2 /= 2
    return None, 0.0


def _is_nested(face, all_faces):
    """True if face's centroid falls within another face's outer boundary
    (holes ignored - a face sitting inside a sibling's hole is nested, even
    though the sibling's own material there is void)."""
    for other in all_faces:
        if other is face:
            continue
        if Face(other.outer_wire()).is_inside(face.center()):
            return True
    return False


def drafted_letter(char, target_r2=TARGET_R2):
    plane = Plane(origin=(TIP_X, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    with BuildSketch(plane) as sk:
        Text(char, font_size=FONT_SIZE, font=FONT, align=(Align.CENTER, Align.CENTER))

    all_faces = sk.sketch.faces()
    top_faces = [f for f in all_faces if not _is_nested(f, all_faces)]
    skipped = len(all_faces) - len(top_faces)

    core_faces = [Face(f.outer_wire(), f.inner_wires()) for f in all_faces]
    core = extrude(Sketch(core_faces), amount=-CORE_H)

    islands, holes, achieved = [], [], []
    for face in top_faces:
        sol, r = _loft_from_plateau(face.outer_wire(), add=True, target_r2=target_r2)
        if sol is not None:
            islands.append(sol)
            achieved.append(r)
        for hw in face.inner_wires():
            sol, r = _loft_from_plateau(hw, add=False, target_r2=target_r2)
            if sol is not None:
                holes.append(sol)
                achieved.append(r)

    result = core
    for p in islands:
        result = result + p
    for h in holes:
        result = result - h
    return result, achieved, skipped


if __name__ == "__main__":
    import string

    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    full, clamped, failed = [], [], []
    nested_total = 0
    for ch in chars:
        try:
            solid, achieved, skipped = drafted_letter(ch)
            nested_total += skipped
            if not achieved:
                failed.append(ch)
            elif min(achieved) >= TARGET_R2 - 1e-9:
                full.append(ch)
            else:
                clamped.append((ch, min(achieved)))
        except Exception as e:
            failed.append(f"{ch}({type(e).__name__})")

    print(f"full target radius ({TARGET_R2}mm): {len(full)}/{len(chars)}  {''.join(full)}")
    print(f"clamped: {len(clamped)}  {clamped}")
    print(f"failed entirely: {len(failed)}  {failed}")
    print(f"nested (depth>1) islands skipped across all chars: {nested_total}")
