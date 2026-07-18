"""
v4 proof-of-concept: TypeCylinder's mesh-vertex-remap technique (his
Outliner/MeshMaker/MeshFront/MeshBackCompound/MeshJoiner pipeline), ported
into a single script and re-parameterized against the REAL geometric
constants already established in v2/blickensderfer.scad and
v3/glyph_poc.py, instead of his original arbitrary pixel constants
(BASE_EXPANSION_WIDTH=300px, PLATEN_RADIUS=0.0002, FRONT_BACK_SEPARATION=200px,
SCALE_FROM_TTF_TO_REAL_WORLD=1/400, BASELINE_OFFSET=840).

Ported constants (v2/blickensderfer.scad, same set v3/glyph_poc.py used):
  Element_Diameter=34, Platen_Diameter=32.258, Char_Protrusion=0.5,
  Font_Size=3.7, Mink_Draft_Angle=55
  Baseline=[-4,-10.3,-16.1], Cutout=[-2.55,-8.66,-14.45] (per-row, mm from
  clip end - Test_Row=1/uppercase used here to match v2/mink_glyph_tester.scad's
  default)

Font swapped to DejaVu Sans Mono (Blick_Script_Leo isn't installed here),
same substitution v3/glyph_poc.py made - only the pipeline mechanics are
under test, not the real typeface.

--- Parameter derivation (his constant -> ours, and why) ---

SCALE (his SCALE_FROM_TTF_TO_REAL_WORLD): derived, not guessed. FreeType
gives outline coordinates in font units (DejaVu Sans Mono: 2048 units/em).
OpenSCAD's text(size=Font_Size) scales its font so the em-square is
Font_Size mm, so SCALE = FONT_SIZE_MM / units_per_EM.

FRONT_BACK_SEPARATION (his fixed distance from back/root plane to the
nominal front/print-face plane, before scalloping): this is exactly what
Char_Protrusion means in the v2 model - "how far the character stands
proud of the element surface" (mink_glyph_tester.scad's own comment). So
FRONT_BACK_SEPARATION_mm = Char_Protrusion = 0.5.

PLATEN_RADIUS (his 2nd-order coefficient for the parabolic platen
scallop, z = (y-offset)^2 * PLATEN_RADIUS): v2 carves this scallop by
subtracting an actual cylinder of radius Rp = Platen_Diameter/2. For small
lateral distance y from the tangent point, a circle's sag is the standard
circle/parabola approximation y^2/(2*Rp). So
PLATEN_RADIUS_mm = 1/(2*Rp) = 1/Platen_Diameter.
radius_y_offset (his descender-based scallop-symmetry axis): v2 keeps
textBaseline and platenBaseline as independent, separately-calibrated
values (docs/glyph-pipeline.md Step 3) - their difference is the offset
between the glyph's own baseline and the platen cutout's axis, so
radius_y_offset_mm = Cutout[row] - Baseline[row].

BASE_EXPANSION_WIDTH (his fixed outward push on the back/root outline -
this IS the draft): v2's draft cone has half-angle Mink_Draft_Angle/2
(see v2/lib/glyph_pipeline.scad minkTextR() and v3/glyph_poc.py's docstring
finding on this), so growth over a depth d is d*tan(half_angle).
BASE_EXPANSION_WIDTH_mm = FRONT_BACK_SEPARATION_mm * tan(Mink_Draft_Angle/2).

--- On "rounding out" the taper (the fn=8-octagon discussion) ---

There are NOT two independent facet knobs here the way OpenSCAD has
Text_Fn (glyph curve smoothness) and Mink_Fn (swept-cone smoothness/
roundness) as separate things. His MeshJoiner stitches side walls directly
between matching front/back vertices along the SAME outline loop used for
the glyph curve itself - so one knob (outline point density) drives both.
Also worth being precise about what Mink_Fn actually rounds: minkowski
with a CONE only adds a straight linear taper (no axial curvature - that
would need summing with a sphere/torus instead); what Mink_Fn's facet
count controls is how many flat panels appear going AROUND the taper,
same axis as this script's POINTS_PER_MM. So the fix demonstrated below is
raising outline point density, not adding intermediate Z-layers.
"""

import argparse
import numpy as np
import freetype
import trimesh
from shapely.geometry import Polygon
from shapely.affinity import scale as shapely_scale

# --- Parameters ported from v2/blickensderfer.scad ---
ELEMENT_DIAMETER = 34.0
PLATEN_DIAMETER = 32.258
CHAR_PROTRUSION = 0.5
FONT_SIZE_MM = 3.7
MINK_DRAFT_ANGLE = 55.0
BASELINE_ROW = [-4, -10.3, -16.1]
CUTOUT_ROW = [-2.55, -8.66, -14.45]
TEST_ROW = 1  # uppercase, matches v2/mink_glyph_tester.scad default

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# --- Derived parameters (see module docstring) ---
FRONT_BACK_SEPARATION_MM = CHAR_PROTRUSION  # real machine value - physical reference only
PLATEN_RADIUS_MM = 1.0 / PLATEN_DIAMETER
RADIUS_Y_OFFSET_MM = CUTOUT_ROW[TEST_ROW] - BASELINE_ROW[TEST_ROW]
DRAFT_HALF_ANGLE_RAD = np.radians(MINK_DRAFT_ANGLE / 2.0)
BASE_EXPANSION_WIDTH_MM = FRONT_BACK_SEPARATION_MM * np.tan(DRAFT_HALF_ANGLE_RAD)

# Default separation used by the CLI/build_glyph is intentionally LONGER than
# the real 0.5mm Char_Protrusion: on a steeply curved element surface a thin
# root gets clipped by the curvature at the mounting stage, so extra depth
# gives margin there. This trades against the opposite direction: longer
# separation grows BASE_EXPANSION_WIDTH_MM (same draft angle, more depth to
# apply it over), which is exactly what pushed 'o'/'e' into self-intersecting
# offset loops in the hole-closing sweep earlier in the conversation.
# Confirmed acceptable: STLs at these depths open and look correct, and
# self-intersection on tight glyphs (already present for 'e' even at the real
# 0.5mm) is fine for this use case - not treating it as a defect to avoid.
DEFAULT_SEPARATION_MM = 2.0


def quadratic_bezier(p0, p1, p2, n):
    t = np.linspace(0, 1, n + 1)[1:]  # exclude t=0 (p0 already added by caller)
    t = t[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def contour_to_points(points, tags, points_per_mm, scale):
    """Walk one FreeType contour (on/off-curve tagged points, TrueType
    quadratic-only) into a flat polyline, sampling curved spans at
    points_per_mm (post-scale) density - this is the single knob that
    drives both glyph-curve smoothness and taper-wall smoothness (see
    module docstring on the fn=8 discussion)."""
    n = len(points)
    on = [bool(t & 1) for t in tags]

    # rotate so we start on an on-curve point
    if not on[0]:
        start = next(i for i in range(n) if on[i])
        points = points[start:] + points[:start]
        on = on[start:] + on[:start]

    out = [np.array(points[0], dtype=float)]
    i = 1
    cur = out[0]
    while i <= n:
        idx = i % n
        p = np.array(points[idx], dtype=float)
        if on[idx]:
            seg_len_mm = np.linalg.norm((p - cur) * scale)
            npts = max(1, int(np.ceil(seg_len_mm * points_per_mm)))
            for k in range(1, npts + 1):
                out.append(cur + (p - cur) * (k / npts))
            cur = p
            i += 1
        else:
            nxt_idx = (i + 1) % n
            nxt = np.array(points[nxt_idx], dtype=float)
            if on[nxt_idx]:
                end = nxt
                consumed = 2
            else:
                end = (p + nxt) / 2.0  # implied on-curve midpoint
                consumed = 1
            ctrl_len_mm = (np.linalg.norm((p - cur) * scale) +
                           np.linalg.norm((end - p) * scale))
            npts = max(2, int(np.ceil(ctrl_len_mm * points_per_mm)))
            curve_pts = quadratic_bezier(cur, p, end, npts)
            out.extend(list(curve_pts))
            cur = end
            i += consumed
    # drop the duplicated closing point (== out[0])
    if np.allclose(out[-1], out[0]):
        out.pop()
    return np.array(out)


def get_glyph_contours(char, points_per_mm, scale, font_path=None):
    contours, _advance = get_glyph_contours_and_advance(char, points_per_mm, scale, font_path)
    return contours


def get_glyph_contours_and_advance(char, points_per_mm, scale, font_path=None):
    face = freetype.Face(font_path or FONT_PATH)
    face.set_char_size(face.units_per_EM)
    face.load_char(char, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
    outline = face.glyph.outline
    advance_mm = face.glyph.advance.x * scale
    contours = []
    start = 0
    for end in outline.contours:
        pts = outline.points[start:end + 1]
        tags = outline.tags[start:end + 1]
        contours.append(contour_to_points(pts, tags, points_per_mm, scale))
        start = end + 1
    return contours, advance_mm


# --- Horizontal alignment (character centering behavior) ---
# Two base modes ("center"/"left"), each with their own universal x
# nudge, plus two independent modified-character groups that get an
# additional signed offset layered on top of whichever base mode is
# active - distinct from and simpler than v2/lib/glyph_pipeline.scad's
# AlignedText (4 methods with textmetrics-based fixed-pitch variants);
# this is a from-scratch scheme per the user's spec, not a port.
ALIGN_MODE = "center"  # "center" or "left"
ALIGN_CENTER_OFFSET_MM = 0.0
ALIGN_LEFT_OFFSET_MM = 0.0
ALIGN_MODIFIED_LEFT_CHARS = "!,.;:)"
ALIGN_MODIFIED_LEFT_OFFSET_MM = 0.0
ALIGN_MODIFIED_RIGHT_CHARS = "("
ALIGN_MODIFIED_RIGHT_OFFSET_MM = 0.0


def alignment_x_offset(char, advance_mm,
                        mode=ALIGN_MODE,
                        center_offset_mm=ALIGN_CENTER_OFFSET_MM,
                        left_offset_mm=ALIGN_LEFT_OFFSET_MM,
                        modified_left_chars=ALIGN_MODIFIED_LEFT_CHARS,
                        modified_left_offset_mm=ALIGN_MODIFIED_LEFT_OFFSET_MM,
                        modified_right_chars=ALIGN_MODIFIED_RIGHT_CHARS,
                        modified_right_offset_mm=ALIGN_MODIFIED_RIGHT_OFFSET_MM):
    """Returns the total x-shift (mm) to add to a glyph's raw FreeType
    contour coordinates (pen origin at the left-side bearing, x=0).

    - mode="center": shift by -advance_mm/2 (centers the ADVANCE box, same
      convention v2 uses for its native halign=center - see
      docs/text-centering.md - not the ink bbox) plus center_offset_mm.
    - mode="left": no centering shift, just left_offset_mm (0 = glyph's
      natural left-side-bearing origin, unmoved).
    Then, independently of mode: characters in modified_left_chars get an
    ADDITIONAL shift of -modified_left_offset_mm (further left);
    characters in modified_right_chars get +modified_right_offset_mm
    (further right). A char matching both resolves to left (checked
    first), matching v2's Modified/Modified2 precedence convention."""
    if mode == "center":
        base = -advance_mm / 2.0 + center_offset_mm
    elif mode == "left":
        base = left_offset_mm
    else:
        raise ValueError(f"unknown alignment mode {mode!r}")

    if char in modified_left_chars:
        base -= modified_left_offset_mm
    elif char in modified_right_chars:
        base += modified_right_offset_mm
    return base


def classify_and_triangulate(contours_mm):
    """Mirrors MeshMaker.py: classify each closed contour as outer island
    or hole via containment, triangulate each outer island (with its
    holes) independently, concatenate. Returns a flat (z=0) trimesh.

    His original (and this port's first pass) only handled ONE level of
    nesting: "contained by something -> hole". That breaks on genuinely
    nested glyphs - e.g. DejaVu Sans Mono's '0' has a small slash mark
    nested INSIDE its counter/hole, to distinguish it from 'O' - shapely
    correctly rejects a hole-within-a-hole ("Holes are nested"). Fixed
    with nesting-DEPTH parity instead of raw containment (same problem
    v3/draft_via_plateau.py solved for build123d's face nesting): even
    depth = solid island (material again, like the slash mark), odd depth
    = hole of its immediate (tightest-containing) parent."""
    polys = [Polygon(c) for c in contours_mm]
    n = len(polys)
    depth = [sum(1 for j in range(n) if j != i and polys[j].contains(polys[i]))
             for i in range(n)]
    is_hole = [d % 2 == 1 for d in depth]

    def immediate_parent(i):
        candidates = [j for j in range(n) if j != i and polys[j].contains(polys[i])
                      and depth[j] == depth[i] - 1]
        return min(candidates, key=lambda j: polys[j].area)

    outer_idx = [i for i, h in enumerate(is_hole) if not h]

    mesh_compound = None
    for oi in outer_idx:
        holes = [contours_mm[hi] for hi in range(n) if is_hole[hi] and immediate_parent(hi) == oi]
        poly = Polygon(shell=contours_mm[oi], holes=holes if holes else None)
        vertices, faces = trimesh.creation.triangulate_polygon(
            poly, triangle_args='p', engine="triangle")
        vertices = np.hstack((vertices, np.zeros((len(vertices), 1))))
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh_compound = mesh if mesh_compound is None else trimesh.util.concatenate(mesh_compound, mesh)
    return mesh_compound


def make_front(mesh, radius_y_offset_mm, platen_radius_mm, separation_mm):
    """Mirrors MeshFront.py: parabolic platen-scallop Z-warp, no boolean."""
    v = mesh.vertices.copy()
    y = v[:, 1]
    v[:, 2] = (y - radius_y_offset_mm) ** 2 * platen_radius_mm + separation_mm
    return trimesh.Trimesh(vertices=v, faces=mesh.faces)


def orthogonal_offset_vertex(p_prev, p_next, p_curr, width_mm):
    """Mirrors MeshBackCompound.py's calculate_expanded_base_vertex: move
    p_curr outward along the bisector implied by its neighbors, by a fixed
    distance. Winding order (p_prev vs p_next) determines outward
    direction, so islands and holes - opposite winding by construction -
    naturally expand/shrink correctly with the SAME formula (see module
    docstring's open question from earlier in the conversation - this is
    what actually resolves it: no hole/island special-casing needed)."""
    vec = p_next - p_prev
    length = np.linalg.norm(vec)
    if length < 1e-9:
        return p_curr
    nx, ny = vec[1] * width_mm / length, -vec[0] * width_mm / length
    return p_curr + np.array([nx, ny])


def back_loops_are_simple(mesh, expansion_width_mm):
    """Real self-intersection check for the offset step, replacing an
    earlier attempt that used trimesh's FCL CollisionManager on a single
    mesh object - that never actually flagged anything (in_collision_internal
    isn't a self-intersection test), which is how the direction bug and
    later this pinch case both went unnoticed until checked directly. This
    checks each offset outline loop's own 2D simplicity with shapely,
    which IS a real, direct check of exactly the failure mode in question
    (see conversation: found the 'o' hole self-intersects between 80-85 deg
    draft angle at Blickensderfer's Font_Size/Char_Protrusion)."""
    from shapely.geometry import Polygon
    outline = mesh.outline()
    results = []
    for path in outline.entities:
        idx = [n[0] for n in path.nodes]
        loop = mesh.vertices[idx][:, :2]
        results.append(Polygon(loop).is_simple)
    return results


def make_back(mesh, expansion_width_mm):
    """Mirrors MeshBackCompound.py: for each outline loop independently,
    push outline vertices outward by a fixed distance; interior vertices
    are left untouched (collapsed to origin, matching his implementation -
    harmless here since MeshJoiner only reads the outline loops)."""
    outline = mesh.outline()
    v = np.zeros_like(mesh.vertices)
    for path in outline.entities:
        nodes = path.nodes
        for j, n in enumerate(nodes):
            curr = n[0]
            prev = nodes[j - 1][1] if j != 0 else nodes[-1][1]
            nxt = n[1]
            # swapped (nxt, prev) order below - matches his CHARACTER_REVERSED=True
            # branch. Verified empirically: with (prev, nxt) the outer boundary
            # shrank (4.22->2.47mm^2 on 'O') and the hole grew (1.95->3.58mm^2) -
            # exactly backwards. Swapped, the outer boundary grows and the hole
            # shrinks, as a wider/embedded base should (see report() area check
            # in the conversation this was diagnosed from).
            v[curr, :2] = orthogonal_offset_vertex(
                mesh.vertices[nxt, :2], mesh.vertices[prev, :2],
                mesh.vertices[curr, :2], expansion_width_mm)
    return trimesh.Trimesh(vertices=v, faces=mesh.faces), outline


def join_front_back(mesh_front, mesh_back, front_outline):
    """Mirrors MeshJoiner.py: stack front+back vertices/faces, then stitch
    a side wall strip between matching front/back vertices along each
    outline loop."""
    v_back = mesh_back.vertices
    v_front = mesh_front.vertices
    v_all = np.concatenate((v_back, v_front))
    offset = len(v_front)

    # NOTE: his MeshJoiner.py appends mesh_front.faces as-is for BOTH caps
    # (reusing faces_front's winding for the offset back cap too) plus the
    # side strip below, unmodified. Empirically (see conversation - swept
    # all 2x2 flip combinations against trimesh's is_winding_consistent/
    # is_volume) that combination is the one that's actually correct: the
    # only defect is the front cap's own winding relative to the assembly
    # (the 2D triangulator's default CCW-from-above convention comes out
    # facing the wrong way once placed as the "outward, larger-z" cap) -
    # back cap and side walls below are otherwise identical to his code.
    faces = [[f[0], f[2], f[1]] for f in mesh_front.faces]
    faces += [f + offset for f in mesh_back.faces]

    for path in front_outline.entities:
        nodes = path.nodes
        for n in nodes[:-1]:
            c = n[0]
            faces.append([c, c + offset, c + offset + 1])
            faces.append([c, c + offset + 1, c + 1])
        first = nodes[0][0]
        last = nodes[-1][0]
        faces.append([last, last + offset, first + offset])
        faces.append([last, first + offset, first])

    return trimesh.Trimesh(vertices=v_all, faces=np.array(faces))


def build_flat_text(char, points_per_mm, depth, font_size_mm=None, font_path=None):
    """Plain flat linear_extrude(depth) of one character - no platen
    scallop, no draft taper. Used for LogoText() (an engraved surface
    label, not a struck type character): reuses the same
    triangulate/front/back/join pipeline with platen_radius=0,
    radius_y_offset=0, expansion_width=0, which reduces make_front's
    scallop to a flat lift by `depth` and make_back's offset to a no-op -
    i.e. the general pipeline degenerates to a plain flat extrusion
    without needing separate code."""
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = freetype.Face(fp)
    scale = fs / face.units_per_EM
    contours_font_units = get_glyph_contours(char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]
    flat = classify_and_triangulate(contours_mm)
    front = make_front(flat, 0.0, 0.0, depth)
    back, front_outline = make_back(front, 0.0)
    return join_front_back(front, back, front_outline)


def build_glyph(char, points_per_mm, expansion_width_mm=None,
                 separation_mm=DEFAULT_SEPARATION_MM, row=TEST_ROW,
                 align_kwargs=None, font_path=None, font_size_mm=None,
                 radius_y_offset_mm=None, platen_radius_mm=None):
    """font_path/font_size_mm/radius_y_offset_mm/platen_radius_mm default to
    this module's own reference constants (FONT_PATH/FONT_SIZE_MM/
    CUTOUT_ROW-BASELINE_ROW/PLATEN_RADIUS_MM) when not given, so this
    still works standalone for the CLI/diagnostic sweeps below - but a
    caller driving a specific machine's config (e.g. lib/blickensderfer.py)
    should pass its own config-derived values explicitly instead of
    relying on these being coincidentally the same numbers."""
    if expansion_width_mm is None:
        expansion_width_mm = separation_mm * np.tan(DRAFT_HALF_ANGLE_RAD)
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = freetype.Face(fp)
    scale = fs / face.units_per_EM

    contours_font_units, advance_mm = get_glyph_contours_and_advance(char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]
    x_shift = alignment_x_offset(char, advance_mm, **(align_kwargs or {}))
    contours_mm = [c + np.array([x_shift, 0.0]) for c in contours_mm]

    if radius_y_offset_mm is None:
        radius_y_offset_mm = CUTOUT_ROW[row] - BASELINE_ROW[row]
    if platen_radius_mm is None:
        platen_radius_mm = PLATEN_RADIUS_MM
    flat = classify_and_triangulate(contours_mm)
    front = make_front(flat, radius_y_offset_mm, platen_radius_mm, separation_mm)
    back, front_outline = make_back(front, expansion_width_mm)
    loop_simple = back_loops_are_simple(back, expansion_width_mm)
    joined = join_front_back(front, back, front_outline)
    return joined, loop_simple


def report(mesh, loop_simple, label):
    print(f"--- {label} ---")
    print(f"  vertices={len(mesh.vertices)} faces={len(mesh.faces)}")
    print(f"  volume={mesh.volume:.6f} mm3  watertight={mesh.is_watertight} "
          f"winding_consistent={mesh.is_winding_consistent} is_volume={mesh.is_volume}")
    print(f"  bbox={mesh.bounds.tolist()}")
    print(f"  back_outline_loops_simple={loop_simple}"
          + ("  <-- offset self-intersected on at least one loop!" if not all(loop_simple) else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("chars", nargs="*", default=["O", "A", "e"])
    parser.add_argument("--points-per-mm", type=float, default=8.0)
    parser.add_argument("--draft-angle", type=float, default=MINK_DRAFT_ANGLE,
                         help="overrides Mink_Draft_Angle (deg), real value 55. "
                              "Kept fixed when sweeping depth instead (see "
                              "--separation-mm) - angle controls STEEPNESS, "
                              "not length.")
    parser.add_argument("--separation-mm", type=float, default=DEFAULT_SEPARATION_MM,
                         help="taper LENGTH (front-to-back depth). Real machine "
                              "value is Char_Protrusion=0.5mm; default here is "
                              "longer (2.0mm) for clipping margin on steeply "
                              "curved elements - see DEFAULT_SEPARATION_MM "
                              "comment. At a fixed draft angle, expansion_mm = "
                              "separation_mm * tan(angle/2), so this also grows "
                              "the outward push, same as a steeper angle would.")
    args = parser.parse_args()

    expansion_mm = args.separation_mm * np.tan(np.radians(args.draft_angle / 2.0))

    print(f"SCALE derivation basis: FONT_SIZE_MM={FONT_SIZE_MM}")
    print(f"separation_mm={args.separation_mm:.6f} (real Char_Protrusion={FRONT_BACK_SEPARATION_MM})")
    print(f"PLATEN_RADIUS_MM={PLATEN_RADIUS_MM:.6f}")
    print(f"RADIUS_Y_OFFSET_MM={RADIUS_Y_OFFSET_MM:.6f}")
    print(f"draft_angle={args.draft_angle} (fixed, real value) -> BASE_EXPANSION_WIDTH_MM={expansion_mm:.6f}")
    print()

    for ch in args.chars:
        mesh, loop_simple = build_glyph(ch, args.points_per_mm, expansion_mm, args.separation_mm)
        report(mesh, loop_simple, f"char='{ch}' points_per_mm={args.points_per_mm} "
                                   f"separation_mm={args.separation_mm} draft_angle={args.draft_angle}")
        safe = ch if ch.isalnum() else f"u{ord(ch):04x}"
        mesh.export(f"out_{safe}_ppm{int(args.points_per_mm)}_sep{args.separation_mm:.2f}.stl")
