"""
Generalizes the island/hole decomposition idea: instead of draft() on the
whole complex solid (fails on any curved stroke - see glyph_poc.py) or a
single offset+loft on the whole face-with-holes (fails whenever an island's
growth and a hole's shrink land on sections with different hole counts),
decompose each glyph into its individual simple pieces - one per island
(outer wire) and one per hole (inner wire) - and loft each piece to its own
offset profile independently, then boolean-reassemble:
    result = union(island_taper_i) - union(hole_taper_j)

Two more fixes found by experiment, both handled per-piece with a
try/fallback since no single choice covers every glyph:
  - offset() corner style: Kind.INTERSECTION (straight miters) succeeds on
    "L" where the default Kind.ARC (rounded) fails outright; Kind.ARC
    succeeds on "g" where INTERSECTION fails outright. Try INTERSECTION
    first, fall back to ARC.
  - offset radius: a fixed r2 can exceed a small hole's own half-width and
    close it entirely (offset() raises rather than silently producing
    garbage). Retry with a halved radius up to a few times and report the
    radius actually achieved per piece, rather than assuming the calibrated
    target is always reachable.
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


def _taper_piece(wire, add: bool, target_r2=TARGET_R2, min_r2=0.02):
    """Loft a single simple wire (no holes) from its own shape to an offset
    profile, shrinking the offset radius until it succeeds or gives up.
    Returns (solid, achieved_r2) or (None, 0) if nothing worked."""
    face = Face(wire)
    r2 = target_r2
    sign = 1 if add else -1
    while r2 >= min_r2:
        grown = _offset_with_fallback(face, sign * r2)
        if grown is not None:
            try:
                base = face.moved(Location((-CORE_H, 0, 0)))
                top = grown.moved(Location((-(CORE_H + CAP_H), 0, 0)))
                return loft([base, top]), r2
            except Exception:
                pass
        r2 /= 2
    return None, 0.0


def drafted_letter(char, target_r2=TARGET_R2):
    plane = Plane(origin=(TIP_X, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    with BuildSketch(plane) as sk:
        Text(char, font_size=FONT_SIZE, font=FONT, align=(Align.CENTER, Align.CENTER))

    core_faces = [Face(f.outer_wire(), f.inner_wires()) for f in sk.sketch.faces()]
    core = extrude(Sketch(core_faces), amount=-CORE_H)

    islands, holes = [], []
    achieved = []
    for face in sk.sketch.faces():
        sol, r = _taper_piece(face.outer_wire(), add=True, target_r2=target_r2)
        if sol is not None:
            islands.append(sol)
            achieved.append(r)
        for hw in face.inner_wires():
            sol, r = _taper_piece(hw, add=False, target_r2=target_r2)
            if sol is not None:
                holes.append(sol)
                achieved.append(r)

    result = core
    for p in islands:
        result = result + p
    for h in holes:
        result = result - h
    return result, achieved


if __name__ == "__main__":
    import string

    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    full, clamped, failed = [], [], []
    for ch in chars:
        try:
            solid, achieved = drafted_letter(ch)
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
