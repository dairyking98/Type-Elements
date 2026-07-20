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
import shapely.ops
from manifold3d import Manifold, Mesh as ManifoldMesh

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

# Circular segments for the Minkowski cone kernel (see build_glyph). Purely a
# speed/roundness knob on the cone itself - manifold3d's own docs warn cost
# scales with the PRODUCT of the two operands' face counts, so this is kept
# modest rather than matching Surface_Fn-style smoothness counts elsewhere.
DEFAULT_CONE_SEGMENTS = 16

# manifold3d's raw minkowski_sum output is drastically over-triangulated on
# nominally FLAT regions (confirmed: a single straight wall facet came out
# as ~24 separate near-coplanar micro-triangles whose normals wobble by a
# fraction of a degree from pure floating-point/algorithmic noise, visible
# as faceting/rippling on straight edges like 'M's strokes - not a real
# draft-angle inconsistency). Manifold.simplify(tolerance) collapses this
# cleanly (2918->182 triangles at even 0.0005mm tolerance in testing,
# single flat face per straight run) without visibly affecting real
# curvature (0.005mm is far below any meaningful glyph feature size).
DEFAULT_SIMPLIFY_TOLERANCE_MM = 0.005

# Circular segments for the REAL platen cutout cylinder (see build_glyph) -
# unlike DEFAULT_CONE_SEGMENTS, this doesn't get multiplied against another
# operand's face count in the same way (the block being cut is far smaller
# than the cylinder's own circumference resolution matters for), so it can
# reasonably run much higher than the Minkowski cone's segment count without
# the same cost concern.
DEFAULT_PLATEN_FN = 360

# When False, skips the Minkowski sweep entirely (by far the most expensive
# step - see build_glyph's cost note) and returns the scalloped-but-
# undrafted block: correct platen curve and glyph footprint/placement, no
# taper. For fast layout/placement iteration, not a final export.
DEFAULT_MINKOWSKI_ENABLED = True

# Real machine draft angle (half-angle of the Minkowski draft cone, see
# module docstring's BASE_EXPANSION_WIDTH note) - was a fixed module
# constant (MINK_DRAFT_ANGLE) with no way for a caller to override it per
# machine/config; now build_glyph() accepts it explicitly, defaulting to
# that same constant for standalone/diagnostic use.
DEFAULT_DRAFT_ANGLE_DEG = MINK_DRAFT_ANGLE


def quadratic_bezier(p0, p1, p2, n):
    t = np.linspace(0, 1, n + 1)[1:]  # exclude t=0 (p0 already added by caller)
    t = t[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def cubic_bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n + 1)[1:]  # exclude t=0 (p0 already added by caller)
    t = t[:, None]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
             + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def contour_to_points(points, tags, points_per_mm, scale):
    """Walk one FreeType contour (on/off-curve tagged points) into a flat
    polyline, sampling curved spans at points_per_mm (post-scale) density -
    this is the single knob that drives both glyph-curve smoothness and
    taper-wall smoothness (see module docstring on the fn=8 discussion).

    Handles both TrueType-flavored (glyf table, quadratic) and CFF-flavored
    (PostScript/OTF-native, cubic) outlines - FreeType normalizes both into
    the same FT_Outline point/tag arrays, distinguished by the tag's low 2
    bits (FT_CURVE_TAG: 1=on-curve, 0=quadratic off-curve, 2=cubic
    off-curve). A cubic off-curve point is always followed by exactly one
    more cubic off-curve point, then an on-curve endpoint (unlike
    quadratic's single-or-implied-midpoint-pair convention below) - CFF's
    format guarantees this pairing, so no fallback is needed. Confirmed
    against a real CFF font (Alma Mono.otf) after this font was found to
    silently mis-render: every off-curve point there was misread as a lone
    quadratic control, producing a plausible-looking but geometrically
    wrong curve with no error raised."""
    n = len(points)
    on = [bool(t & 1) for t in tags]
    is_cubic = [(t & 0x3) == 2 for t in tags]

    # All-off-curve contour: a legal, common TrueType shorthand for smooth
    # loops (e.g. a small dot/bubble, like '%'s two "o"s or 'i'/'.''s dot) -
    # every consecutive off-curve pair implies its own on-curve midpoint, so
    # a contour can close with no EXPLICIT on-curve point anywhere. FreeType/
    # FontForge both render these correctly. Without this, `next(i for i in
    # range(n) if on[i])` below (which needs a real anchor to seed the walk)
    # finds nothing and raises StopIteration, mis-flagging a perfectly valid
    # glyph as broken. Fix: synthesize the same implied on-curve point
    # FreeType would use to start on - the midpoint of the last and first
    # points (both off-curve here) - then walk normally; the existing
    # consecutive-off-curve handling below already covers the rest of the
    # loop once a real anchor exists.
    if n and not any(on):
        mx = (points[-1][0] + points[0][0]) / 2.0
        my = (points[-1][1] + points[0][1]) / 2.0
        points = [(mx, my)] + list(points)
        tags = [1] + list(tags)
        on = [True] + on
        is_cubic = [False] + is_cubic
        n += 1

    # rotate so we start on an on-curve point
    if not on[0]:
        start = next(i for i in range(n) if on[i])
        points = points[start:] + points[:start]
        on = on[start:] + on[:start]
        is_cubic = is_cubic[start:] + is_cubic[:start]

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
        elif is_cubic[idx]:
            ctrl2_idx = (i + 1) % n
            end_idx = (i + 2) % n
            ctrl2 = np.array(points[ctrl2_idx], dtype=float)
            end = np.array(points[end_idx], dtype=float)
            ctrl_len_mm = (np.linalg.norm((p - cur) * scale) +
                           np.linalg.norm((ctrl2 - p) * scale) +
                           np.linalg.norm((end - ctrl2) * scale))
            npts = max(2, int(np.ceil(ctrl_len_mm * points_per_mm)))
            curve_pts = cubic_bezier(cur, p, ctrl2, end, npts)
            out.extend(list(curve_pts))
            cur = end
            i += 3
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
    ADDITIONAL shift of +modified_left_offset_mm; characters in
    modified_right_chars get +modified_right_offset_mm. Both are plain
    signed x-offsets (negative = left, positive = right), same
    convention as center_offset_mm/left_offset_mm - deliberately
    symmetric, unlike an earlier version of this function which negated
    modified_left_offset_mm (meant to read as "how far left to push",
    but that made a negative value push RIGHT - confusing, and there's
    no v2 convention to match here (this whole scheme is v4-only, see
    the module docstring above), so there was no reason to keep it). A
    char matching both resolves to left (checked first), matching v2's
    Modified/Modified2 precedence convention."""
    if mode == "center":
        base = -advance_mm / 2.0 + center_offset_mm
    elif mode == "left":
        base = left_offset_mm
    else:
        raise ValueError(f"unknown alignment mode {mode!r}")

    if char in modified_left_chars:
        base += modified_left_offset_mm
    elif char in modified_right_chars:
        base += modified_right_offset_mm
    return base


# Anything smaller than this (mm^2) is floating-point noise from boolean-op
# cleanup (buffer(0)/difference() on self-intersecting input can leave
# slivers down around 1e-18 mm^2), not a real decorative detail - the
# smallest genuine feature seen in practice (a script font's fine serif
# loop) is ~0.005 mm^2, several orders of magnitude above this.
_MIN_PART_AREA_MM2 = 1e-6


def _polygon_parts(geom):
    """Flattens a Polygon/MultiPolygon/GeometryCollection (as produced by
    shapely boolean ops) into a list of real-area Polygons, dropping
    degenerate slivers and non-area geometry (stray LineString/Point
    artifacts buffer(0) can leave behind when cleaning up a
    self-intersection)."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom] if geom.area > _MIN_PART_AREA_MM2 else []
    if geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        out = []
        for g in geom.geoms:
            out.extend(_polygon_parts(g))
        return out
    return []


def classify_and_triangulate(contours_mm):
    """Mirrors MeshMaker.py: classify each closed contour as outer island
    or hole via containment, boolean-compose them into real filled
    polygons (union same-depth material, subtract same-depth holes,
    ascending by nesting depth), triangulate, concatenate. Returns a flat
    (z=0) trimesh.

    His original (and this port's first pass) only handled ONE level of
    nesting: "contained by something -> hole". That breaks on genuinely
    nested glyphs - e.g. DejaVu Sans Mono's '0' has a small slash mark
    nested INSIDE its counter/hole, to distinguish it from 'O' - shapely
    correctly rejects a hole-within-a-hole ("Holes are nested"). Fixed
    with nesting-DEPTH parity (same problem v3/draft_via_plateau.py solved
    for build123d's face nesting): even depth = solid island (material
    again, like the slash mark), odd depth = hole.

    A second, later problem with the ORIGINAL per-shell approach (assign
    each hole to its single tightest-containing shell via
    Polygon(shell=..., holes=[...]), triangulate each shell independently):
    it assumes outer islands never overlap each other. That's false for
    hand-digitized script fonts, which are routinely built from several
    separately-drawn pen-stroke shapes that deliberately overlap where
    they should join (confirmed on Blick Script's '3'/'E' - real,
    non-self-intersecting stroke shapes whose overlap zone contains a tiny
    decorative loop-hole, so shapely's raw contains() count reported that
    hole as "contained by" every one of the overlapping strokes at once,
    an inconsistent depth chain no single-shell assignment can represent
    correctly). Real per-level boolean union/difference handles overlap
    natively - union doesn't care whether its inputs already intersect -
    so it needs no per-shell assignment at all, just depth parity to know
    which polygons are material and which are voids at each level.

    A third, unrelated problem this same rewrite absorbs: individual
    contours that are internally self-intersecting (e.g. AverageMono's
    '6', Mono Fraktur's 'T', Rotunda Pommerania's 's', Spencerian's 'R' -
    all confirmed pre-existing, sub-visual glitches in hand-digitized
    outlines, not something any of THESE fonts' edits introduced).
    shapely's raw Polygon(c) rejects those outright ("invalid shapely
    polygon passed!" from trimesh's triangulate_polygon). `.buffer(0)` is
    the standard shapely self-repair idiom for exactly this - it resolves
    a self-intersecting ring into the equivalent valid (Multi)Polygon,
    confirmed here to reproduce the same silhouette area as the raw
    (invalid) shape, i.e. a real, harmless, sub-visual fix, not a
    reshaping.

    A fourth, also-unrelated problem: FreeType occasionally hands back a
    contour with fewer than 3 points - a single stray on/off-curve point
    (confirmed on real fonts: e.g. Tremble 308's 'b', Blackletter
    Asterisk's 'R') or a duplicated-point 2-point "contour", both leftover
    editing debris from whatever tool last touched the glyph, not real
    geometry. A <3-point contour can never enclose area, so it's always
    safe to drop outright - Polygon() itself agrees, rejecting it before
    even .buffer(0) gets a chance ("A linearring requires at least 4
    coordinates" - 3 points plus the auto-closing repeat of the first)."""
    contours_mm = [c for c in contours_mm if len(c) >= 3]
    raw_polys = [Polygon(c) for c in contours_mm]
    # .buffer(0) BEFORE depth classification too: contains() on an invalid
    # (self-intersecting) polygon is undefined/unreliable, so depth needs
    # the same repaired shapes the union/difference pass below uses.
    polys = [p.buffer(0) for p in raw_polys]
    n = len(polys)
    depth = [sum(1 for j in range(n) if j != i and polys[j].contains(polys[i]))
             for i in range(n)]

    result = None
    for d in range(max(depth, default=-1) + 1):
        level = [polys[i] for i in range(n) if depth[i] == d]
        if not level:
            continue
        level_union = shapely.ops.unary_union(level) if len(level) > 1 else level[0]
        if result is None:
            result = level_union          # depth 0 always starts as material
        elif d % 2 == 0:
            result = result.union(level_union)       # even depth: material again
        else:
            result = result.difference(level_union)  # odd depth: a hole

    mesh_compound = None
    for poly in _polygon_parts(result):
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


def build_flat_text(char, points_per_mm, depth, font_size_mm=None, font_path=None, align_kwargs=None):
    """Plain flat linear_extrude(depth) of one character - no platen
    scallop, no draft taper. Used for LogoText() (an engraved surface
    label, not a struck type character): reuses the same
    triangulate/front/back/join pipeline with platen_radius=0,
    radius_y_offset=0, expansion_width=0, which reduces make_front's
    scallop to a flat lift by `depth` and make_back's offset to a no-op -
    i.e. the general pipeline degenerates to a plain flat extrusion
    without needing separate code.

    align_kwargs, if given, is passed to alignment_x_offset() exactly as
    build_glyph() does for the real element - same advance-box
    center/left mode plus modified_left/right_chars nudges - so callers
    like type_test.py can match the real pipeline's horizontal alignment
    convention. None (the default) applies no shift at all, i.e. the
    glyph sits at its raw FreeType pen origin - LogoText() relies on
    this to do its own separate ink-bbox centering for baseline
    alignment across a radial run of characters."""
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = freetype.Face(fp)
    scale = fs / face.units_per_EM
    contours_font_units, advance_mm = get_glyph_contours_and_advance(char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]
    if align_kwargs is not None:
        x_shift = alignment_x_offset(char, advance_mm, **align_kwargs)
        contours_mm = [c + np.array([x_shift, 0.0]) for c in contours_mm]
    flat = classify_and_triangulate(contours_mm)
    front = make_front(flat, 0.0, 0.0, depth)
    back, front_outline = make_back(front, 0.0)
    return join_front_back(front, back, front_outline)


def build_flat_text_drafted(char, points_per_mm, depth, font_size_mm=None, font_path=None,
                             align_kwargs=None, draft_angle_deg=DEFAULT_DRAFT_ANGLE_DEG,
                             cone_segments=DEFAULT_CONE_SEGMENTS,
                             simplify_tolerance_mm=DEFAULT_SIMPLIFY_TOLERANCE_MM):
    """build_flat_text()'s real-draft-cone counterpart, for machines that
    want their engraved Logo/Label text tapered rather than a plain flat
    extrude (Mignon's minkowski_text option - see lib/mignon.py). Same
    flat, UN-mirrored contour extraction as build_flat_text (this is
    decorative text read directly off the element, never struck through a
    platen - the mirror step in build_glyph() below is specific to struck
    characters and does NOT belong here), Minkowski-summed with a real
    draft cone using the SAME construction build_glyph() uses (tip sliver
    + cone, apex at z=depth, wide base at z=0 - see build_glyph's own
    comment for the derivation), minus its platen-scallop carve, which
    has no equivalent on a flat engraved label. depth plays separation_mm's
    role: expansion_width_mm = depth * tan(draft_angle_deg/2)."""
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = freetype.Face(fp)
    scale = fs / face.units_per_EM
    contours_font_units, advance_mm = get_glyph_contours_and_advance(char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]
    if align_kwargs is not None:
        x_shift = alignment_x_offset(char, advance_mm, **align_kwargs)
        contours_mm = [c + np.array([x_shift, 0.0]) for c in contours_mm]
    flat = classify_and_triangulate(contours_mm)

    expansion_width_mm = depth * np.tan(np.radians(draft_angle_deg / 2.0))
    tip_h = min(0.01, depth * 0.01)
    cone_h = depth - tip_h

    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces, tip_h)
    prism.apply_translation([0, 0, depth - tip_h])

    cone = Manifold.cylinder(cone_h, expansion_width_mm, 0.0, circular_segments=cone_segments)
    cone = cone.translate([0, 0, -cone_h])

    drafted = _to_manifold(prism).minkowski_sum(cone)
    if simplify_tolerance_mm > 0:
        drafted = drafted.simplify(simplify_tolerance_mm)
    return _from_manifold(drafted)


def _to_manifold(mesh):
    return Manifold(mesh=ManifoldMesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32)))


def _from_manifold(manifold):
    m = manifold.to_mesh()
    return trimesh.Trimesh(vertices=m.vert_properties, faces=m.tri_verts, process=False)


def build_glyph(char, points_per_mm, expansion_width_mm=None,
                 separation_mm=DEFAULT_SEPARATION_MM, row=TEST_ROW,
                 align_kwargs=None, font_path=None, font_size_mm=None,
                 radius_y_offset_mm=None, platen_radius_mm=None,
                 cone_segments=DEFAULT_CONE_SEGMENTS,
                 simplify_tolerance_mm=DEFAULT_SIMPLIFY_TOLERANCE_MM,
                 platen_fn=DEFAULT_PLATEN_FN,
                 minkowski_enabled=DEFAULT_MINKOWSKI_ENABLED,
                 draft_angle_deg=DEFAULT_DRAFT_ANGLE_DEG):
    """Builds one struck-character solid via a REAL Minkowski sum
    (manifold3d's Manifold.minkowski_sum), replacing the per-vertex
    outline-offset approximation this function used before (fixed-distance
    push per outline vertex, then stitch front/back caps - see git history).
    That approach had no topology awareness: on any glyph with a locally
    narrow feature (H's inter-stroke gap, k/m's diagonal junctions, o/e's
    counters) the offset outline could fold through itself, and per-glyph
    patching (a self-union repair, gated by hole-vs-island classification)
    didn't fully resolve it without its own new failure modes - self-union
    on a multi-island glyph (e.g. 'i', dot separate from stem) was found to
    weld the islands together and lose real volume, and 'm' still produced
    a visible fold even with that repair in place.

    A true Minkowski sum can't produce that defect: dilating a shape by a
    convex kernel (a cone here) is mathematically guaranteed to stay a
    valid, simple solid on ANY input topology (holes, disjoint islands,
    arbitrarily narrow gaps) - so there is no self-intersection case left
    to detect or repair, and no per-glyph special-casing needed at all.

    Mechanism: build the flat (un-drafted) glyph as a simple prism (extrude
    the 2D outline up by more than separation_mm - see platen note below),
    carve the platen scallop into its top with a REAL boolean cylinder
    subtraction (matching the real machine / v2's PlatenCutout(), not a
    per-vertex parabola approximation - see "Real platen cutout" below),
    then Minkowski-sum the resulting (already-scalloped) solid with a draft
    cone (apex at the tip where its radius is 0, base at the root/z=0 where
    its radius is expansion_width_mm) - the sum's cross-section at any
    depth is exactly the scalloped shape dilated by the cone's radius
    there, i.e. the widen-toward-the-root taper, computed by a real CSG
    kernel instead of approximated per-vertex.

    Real platen cutout: platen_radius_mm is the small-angle-approximation
    coefficient (1/(2*Rp), same as before) - inverted here to recover the
    real platen radius Rp, then used to build an actual cylinder (axis
    along X, tangent to the tip plane at y=radius_y_offset_mm, radius Rp,
    platen_fn segments), boolean-subtracted from the prism BEFORE the
    Minkowski sum. Doing this before (not after, as an earlier version of
    this function did) matters: the cone's own geometry - and therefore
    the realized draft angle - is only valid for whatever shape it's
    actually summed with. Carving the scallop in first means the cone
    sweeps the true curved shape throughout, so the draft angle is
    preserved everywhere by construction, not just near the tangent point
    (confirmed wrong before: warping only the swept result's top ring
    left the walls built as if the tip were still flat, visibly wrong on
    edges far from radius_y_offset_mm like 'M'/'A's bottoms).

    manifold3d's raw minkowski_sum output is also drastically over-
    triangulated on nominally FLAT regions - a single straight wall facet
    (e.g. 'M's strokes) came out as ~24 separate near-coplanar micro-
    triangles whose normals wobble by a fraction of a degree from pure
    floating-point/algorithmic noise, visible as faceting on straight
    edges even though the true geometry is flat there. simplify_tolerance_mm
    (via Manifold.simplify()) collapses this cleanly before it's ever
    converted back to trimesh.

    Real cost: manifold3d warns Minkowski performance scales with the
    PRODUCT of the two operands' face counts, confirmed empirically at
    ~0.2-1.2s per character (vs. a few ms before) depending on
    points_per_mm/cone_segments - roughly 16-66s for the full 84-character
    TextRing depending on quality settings, vs. ~3-6s before. Accepted
    tradeoff: this is offline batch generation, not interactive, in
    exchange for eliminating an entire class of per-glyph bugs rather than
    chasing them one at a time.

    font_path/font_size_mm/radius_y_offset_mm/platen_radius_mm default to
    this module's own reference constants (FONT_PATH/FONT_SIZE_MM/
    CUTOUT_ROW-BASELINE_ROW/PLATEN_RADIUS_MM) when not given, so this
    still works standalone for the CLI/diagnostic sweeps below - but a
    caller driving a specific machine's config (e.g. lib/blickensderfer.py)
    should pass its own config-derived values explicitly instead of
    relying on these being coincidentally the same numbers."""
    if expansion_width_mm is None:
        expansion_width_mm = separation_mm * np.tan(np.radians(draft_angle_deg / 2.0))
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = freetype.Face(fp)
    scale = fs / face.units_per_EM

    contours_font_units, advance_mm = get_glyph_contours_and_advance(char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]
    x_shift = alignment_x_offset(char, advance_mm, **(align_kwargs or {}))
    contours_mm = [c + np.array([x_shift, 0.0]) for c in contours_mm]
    # A struck type element carries a MIRROR-IMAGE of the desired printed
    # glyph (same reason a rubber stamp or hot-metal slug is cut reversed -
    # striking is a reflection through the contact plane, same as v2's
    # TwoDText: `mirror([1,0,0])` wrapped around the whole aligned/shifted
    # glyph, lib/glyph_pipeline.scad ~line 292). v4 has no OpenSCAD-style
    # mirror() primitive, so it's done directly on the contour points here -
    # negate x on the ALREADY-shifted contours (mirror wraps translate in
    # v2, i.e. this must come after x_shift, not before, to match). This
    # only belongs on the real struck-character path (build_glyph) - NOT
    # build_flat_text (LogoText's engraved label and Type Test's preview
    # are both read directly, never struck, so they must stay un-mirrored).
    contours_mm = [c * np.array([-1.0, 1.0]) for c in contours_mm]

    if radius_y_offset_mm is None:
        radius_y_offset_mm = CUTOUT_ROW[row] - BASELINE_ROW[row]
    if platen_radius_mm is None:
        platen_radius_mm = PLATEN_RADIUS_MM

    flat = classify_and_triangulate(contours_mm)

    # Minkowski sum ADDS extents in each dimension - a full-separation_mm
    # prism summed with a full-separation_mm cone doubles the Z depth
    # (confirmed: bbox came out [0, 2*separation_mm], not [0,
    # separation_mm]). Fix: the prism is a thin sliver sitting at the TIP
    # end (just enough thickness to be a valid non-degenerate solid - a
    # truly flat/zero-volume shape isn't valid minkowski_sum input), and
    # the CONE carries (almost) the entire separation_mm depth. Critically,
    # the cone's own origin must be at its APEX (the radius=0 point), not
    # its base: manifold3d's cylinder() places the local origin at the
    # radius_low end, so building it wide-at-bottom/apex-at-top
    # (radius_low=expansion_width_mm, radius_high=0, matching how the
    # non-translated version was built) then translating by -cone_height
    # puts the apex at z=0 and the wide base BELOW it (negative z) -
    # summed with the tip sliver (sitting at [separation_mm-tip_h,
    # separation_mm]), the apex contributes zero offset at the tip and the
    # base contributes the full expansion at z=0, giving exactly the
    # intended [0, separation_mm] range. (First attempt at this got the
    # radius_low/radius_high swapped AND translated, which cancelled out
    # and put the dilation back at the tip instead of the root - verified
    # by checking cross-section width at z=0 vs z=separation_mm directly,
    # not just watertightness/volume, which don't catch a reversed draft.)
    tip_h = min(0.01, separation_mm * 0.01)
    cone_h = separation_mm - tip_h
    # Preview path (minkowski_enabled=False) doesn't need the thin sliver at
    # all - that's only a construction detail for feeding the Minkowski sum
    # (see above), and returning it AS the preview shape makes for a
    # razor-thin, hard-to-see sliver (~tip_h+block_margin, well under
    # 0.3mm) instead of something actually comparable in size to a real
    # drafted character. Use the full separation_mm as the extrusion depth
    # instead - same bottom-at-z=0 registration as the drafted root, still
    # skips the expensive Minkowski sweep entirely.
    block_h = tip_h if minkowski_enabled else separation_mm
    block_z0 = separation_mm - tip_h if minkowski_enabled else 0.0

    # Platen scallop applied as a REAL boolean cylinder subtraction, BEFORE
    # the Minkowski sum - not a per-vertex parabola-warp approximation (the
    # small-angle approximation of the same circle) applied to whatever
    # vertices happened to survive triangulation/simplify. This is exactly
    # how the real machine's cutter (and v2/lib/glyph_pipeline.scad's
    # PlatenCutout()) works: an actual cylinder of the platen's real
    # diameter, tangent to the tip plane at radius_y_offset_mm, carved out
    # of the block. platen_radius_mm here is the SAME small-angle
    # approximation coefficient as before (1/(2*Rp)) - inverted to recover
    # the real platen radius Rp, rather than adding a redundant parameter.
    #
    # The cylinder's own axis position/radius depend only on
    # radius_y_offset_mm and Rp - both per-ROW constants, identical for
    # every character in a row - so the underlying curve is the exact same
    # real cylinder machine-wide per row, not independently approximated
    # per glyph; only the intersection with each glyph's own silhouette
    # differs, which is correct.
    platen_radius_real_mm = 1.0 / (2.0 * platen_radius_mm)

    # Block must be tall enough that its ORIGINAL flat top sits above the
    # cylinder's reach at every Y this glyph actually spans, or the corners
    # farthest from radius_y_offset_mm survive uncut (still flat, not
    # following the real curve) instead of being carved down to it -
    # confirmed by testing with an under-sized margin. Sized per-glyph from
    # its own Y-extent, not a fixed guess.
    y_min, y_max = flat.vertices[:, 1].min(), flat.vertices[:, 1].max()
    dy_max = max(abs(y_min - radius_y_offset_mm), abs(y_max - radius_y_offset_mm))
    bulge_max = platen_radius_real_mm - np.sqrt(max(platen_radius_real_mm ** 2 - dy_max ** 2, 0.0))
    block_margin = bulge_max * 1.1 + 0.005

    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces,
                                                     block_h + block_margin)
    prism.apply_translation([0, 0, block_z0])

    x_min, x_max = flat.vertices[:, 0].min(), flat.vertices[:, 0].max()
    cyl_length = (x_max - x_min) + 2.0
    cyl_center_x = (x_min + x_max) / 2.0
    platen_cyl = Manifold.cylinder(cyl_length, platen_radius_real_mm, platen_radius_real_mm,
                                    circular_segments=platen_fn, center=True)
    platen_cyl = platen_cyl.rotate([0, 90, 0])
    platen_cyl = platen_cyl.translate([cyl_center_x, radius_y_offset_mm,
                                        separation_mm + platen_radius_real_mm])

    scalloped = _to_manifold(prism) - platen_cyl

    if not minkowski_enabled:
        # Fast preview path: skip the Minkowski sweep entirely (the
        # expensive step - see the cost note above) and return the
        # scalloped block as-is, undrafted (constant cross-section from
        # root to tip). Correct platen curve and glyph footprint/placement,
        # no taper - for quick layout iteration, not a final export.
        if simplify_tolerance_mm > 0:
            scalloped = scalloped.simplify(simplify_tolerance_mm)
        return _from_manifold(scalloped)

    cone = Manifold.cylinder(cone_h, expansion_width_mm, 0.0, circular_segments=cone_segments)
    cone = cone.translate([0, 0, -cone_h])

    drafted = scalloped.minkowski_sum(cone)
    if simplify_tolerance_mm > 0:
        drafted = drafted.simplify(simplify_tolerance_mm)
    return _from_manifold(drafted)


def report(mesh, label):
    print(f"--- {label} ---")
    print(f"  vertices={len(mesh.vertices)} faces={len(mesh.faces)}")
    print(f"  volume={mesh.volume:.6f} mm3  watertight={mesh.is_watertight} "
          f"winding_consistent={mesh.is_winding_consistent} is_volume={mesh.is_volume}")
    print(f"  bbox={mesh.bounds.tolist()}")


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
    parser.add_argument("--cone-segments", type=int, default=DEFAULT_CONE_SEGMENTS,
                         help="circular segments for the Minkowski cone kernel - "
                              "trades roundness for speed (manifold3d's cost "
                              "scales with the product of the two operands' "
                              "face counts, so this and --points-per-mm both "
                              "matter for generation time).")
    parser.add_argument("--simplify-tolerance-mm", type=float, default=DEFAULT_SIMPLIFY_TOLERANCE_MM,
                         help="Manifold.simplify() tolerance applied to the raw "
                              "minkowski_sum output - collapses the drastic "
                              "over-triangulation/faceting noise manifold3d "
                              "produces on flat regions (e.g. straight strokes "
                              "like 'M's). 0 disables.")
    parser.add_argument("--platen-fn", type=int, default=DEFAULT_PLATEN_FN,
                         help="circular segments for the real platen cutout cylinder.")
    parser.add_argument("--no-minkowski", dest="minkowski_enabled", action="store_false",
                         default=DEFAULT_MINKOWSKI_ENABLED,
                         help="skip the Minkowski draft sweep (fast, undrafted preview - "
                              "correct platen curve/placement, no taper).")
    args = parser.parse_args()

    expansion_mm = args.separation_mm * np.tan(np.radians(args.draft_angle / 2.0))

    print(f"SCALE derivation basis: FONT_SIZE_MM={FONT_SIZE_MM}")
    print(f"separation_mm={args.separation_mm:.6f} (real Char_Protrusion={FRONT_BACK_SEPARATION_MM})")
    print(f"PLATEN_RADIUS_MM={PLATEN_RADIUS_MM:.6f}")
    print(f"RADIUS_Y_OFFSET_MM={RADIUS_Y_OFFSET_MM:.6f}")
    print(f"draft_angle={args.draft_angle} (fixed, real value) -> BASE_EXPANSION_WIDTH_MM={expansion_mm:.6f}")
    print()

    for ch in args.chars:
        mesh = build_glyph(ch, args.points_per_mm, expansion_mm, args.separation_mm,
                            cone_segments=args.cone_segments,
                            simplify_tolerance_mm=args.simplify_tolerance_mm,
                            platen_fn=args.platen_fn,
                            minkowski_enabled=args.minkowski_enabled)
        report(mesh, f"char='{ch}' points_per_mm={args.points_per_mm} "
                     f"separation_mm={args.separation_mm} draft_angle={args.draft_angle} "
                     f"cone_segments={args.cone_segments} "
                     f"simplify_tolerance_mm={args.simplify_tolerance_mm} "
                     f"platen_fn={args.platen_fn} minkowski_enabled={args.minkowski_enabled}")
        safe = ch if ch.isalnum() else f"u{ord(ch):04x}"
        mesh.export(f"out_{safe}_ppm{int(args.points_per_mm)}_sep{args.separation_mm:.2f}.stl")
