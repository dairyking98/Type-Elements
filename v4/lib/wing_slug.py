"""
Shared "wing body" type-slug engine - lib/type_slug.py (generic base
engine), lib/vogue_slug.py (Vogue foundry mark replica), and lib/
gauge_slug.py (no-text calibration/measuring gauge) all configure this
module and share everything here, the same "shared engine + thin per-
variant module" pattern lib/spherical_machine.py uses for lib/
selectric12.py/selectric3.py/selectric_composer.py.

Ground truth is v1, not v2: these standalone decorative type-slug
replicas (v1/Type Slugs/*.scad) were never carried into v2 at all (v2's
whole file set is the 7 real typewriter-machine ports, unrelated) - so
"the real v2 source is ground truth" (CLAUDE.md's usual convention)
doesn't apply here; v1/Type Slugs/TypeSlug.scad is the ground truth this
module and config/type_slug.yaml/vogue_slug.yaml/gauge_slug.yaml are
ported from, cross-referenced by v1 line number the same way v2 line
numbers are used for every other machine.

Physical form: NOT a full keyboard/typewriter assembly - one small,
individually-molded/printed type slug (the actual metal-type-style
element a typebar or shuttle carries), novelty/reference objects rather
than functional typewriter parts (except Gauge, see lib/gauge_slug.py's
docstring - a real install-on-the-machine measuring tool, not a novelty).
Because of that, there is no keyboard "layout" (row/column grid) concept
at all - config has no `layout:` section, so tune.py's `"rows" in
layout` check (HAS_LAYOUT_TAB) is naturally False and the Layout tab is
skipped, same mechanism Selectric already relies on for ITS "no editable
keyboard-layout concept" callout, not new/special-cased code.

Function-by-function relationship to v1/Type Slugs/TypeSlug.scad's
MakeSlug() (lines 108-287), verified before writing any of this (per
CLAUDE.md's "diff against source first" rule):
  - BodyHull()/EnvelopeHull() -> the nested hull(){...} body construction
    (lines 115-134, duplicated at 184-206 for the enlarged envelope) -
    both are really just ONE convex hull of the same 6 primitives (4
    corner posts + 2 wing cylinders) at two different corner-post
    heights; v1's own INNER hull() (around just the 4 corners) is
    redundant once everything funnels into a single outer convex hull
    (hull() is idempotent - convex_hull(convex_hull(A) u B) ==
    convex_hull(A u B)), so this module only ever builds ONE real
    trimesh.convex_hull per call, not two nested ones.
  - DraftText() -> "Create Draft Angle Text" (lines 158-181) - two
    stacked struck characters (not build_glyph()'s one-character-per-row
    model; genuinely different real geometry, ported fresh here rather
    than forced through build_glyph, same reasoning spherical_machine's
    own module docstring gives for not reusing build_glyph either).
  - Logo()/VogueMark() -> "SVG Logo" (135-146)/VogueSlug.scad's "Vogue
    Foundry Mark" (109-126) - TypeSlug.scad's OWN "SVG_Vogue_Enable"
    branch (147-157) is a byte-for-byte duplicate of its SVG_Enable
    branch (same SVG_File, not the real vogue-foundry-*.svg files) - i.e.
    dead/redundant leftover from when VogueSlug.scad was forked off of
    it, not a second real feature. NOT ported as a second toggle here;
    logo.vogue_enabled (this module's real 2-piece Vogue mark, matching
    VogueSlug.scad's actual working code) is the only "second logo"
    concept that exists.
  - _clean_exposed_minkowski() -> "Clean Exposed Minkowski Manifold"
    (152-176) - v1 builds this as `(box20 - envelope)` then subtracts
    THAT from the drafted union; implemented here as a direct
    intersection with the envelope instead (equivalent whenever the
    drafted union doesn't extend past the local 20mm box, true for every
    real config here - a small, explicitly-noted simplification, not a
    behavior change).
  - TypebarSlot()/CopyrightText() -> 208-220.
  - ResinSupportGeometry() -> "Resin Support" (223-245) - v1's own
    raft+per-station-wire construction, genuinely different from
    lib/resin_support.py's resin_rod() (single hull-of-3-spheres capsule
    per rod, individual per-rod raft) - NOT force-fit onto that shared
    helper, same "real new lib code when the real geometry differs"
    reasoning CLAUDE.md's geometry-invariants section already establishes
    for Hammond Split's own independent resin-support scheme.
  - Loop() -> "Loop" (247-254) - a torus (rotate_extrude of a small
    offset circle), built via scad_primitives.revolve_polygon like every
    other machine's torus/ring features.
  - Post()/PostHole() -> "Post and Hole" (256-273, 275-279).
  - SideHole() -> "Side Holes" (281-285).
  - Ticks() (gauge_slug.py's own no-text variant) ->
    v1/Type Slugs/GaugeTypeSlugSlug.scad:104-112 - NOT part of
    TypeSlug.scad at all; lives here anyway (not gauge_slug.py) since
    it's config-driven (gauge.enabled) like every other optional feature
    in this shared engine, matching the "shared code lives in the
    shared module" convention.

Resin support is a build.resin_support TOGGLE (ResinPrint vs FullElement
dispatch, same convention every other v4 machine uses), NOT baked
permanently into the geometry the way v1's single `Resin_Support`
customizer variable was - a real, deliberate structural improvement
(cleanly separates "is this a resin print" from the element's own
geometry), not a silent behavior change: build.resin_support: true
reproduces v1's Resin_Support=true default exactly.
"""

import time

import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint

from glyph_poc import (get_glyph_contours_and_advance, classify_and_triangulate,
                        alignment_offset, em_to_mm_scale, load_font_face)
import scad_primitives as sp
import svg_import
import build_log

_active_machine = None


def _receive_config(source_globals, machine_name):
    global _active_machine
    if _active_machine not in (None, machine_name):
        raise RuntimeError(
            f"wing_slug already configured for {_active_machine!r}; "
            f"cannot reconfigure for {machine_name!r} in the same process")
    _active_machine = machine_name
    globals().update({k: v for k, v in source_globals.items() if k[:1].isupper() or k == "z"})


def _require_configured():
    if _active_machine is None:
        raise RuntimeError("call <machine>.configure(config_path) before using this module")


# ------------------------------------------------------------------ Body

def _corner_post_verts(corner_height, fn):
    """The 4 rounded-corner posts of the body's flat base face (v1:118-125/
    190-197), pre-translate (spans z=[0, corner_height] each) - the -
    Face_Thickness Z shift (v1's outer `translate([0,0,-Face_Thickness])`
    wrapping the inner hull()) is applied by the caller once, to the
    combined point cloud, not per-post."""
    positions = [
        (-Body_Width / 2 + Face_Radius, Face_Radius),
        (Body_Width / 2 - Face_Radius, Face_Radius),
        (Body_Width / 2 - Face_Radius, Body_Length - Face_Radius),
        (-Body_Width / 2 + Face_Radius, Body_Length - Face_Radius),
    ]
    verts = []
    for x, y in positions:
        post = sp.cylinder_z(2 * Face_Radius, corner_height, sections=Corner_Fn, base_z=0.0)
        post.apply_translation([x, y, 0.0])
        verts.append(post.vertices)
    return np.concatenate(verts, axis=0)


def _wing_cyl_verts(y_pos):
    """One wing cylinder (v1:128-130/131-133, 200-205) - axis along X
    (rotate([0,90,0])), radius Wing_Radius, length Body_Slot_Width+2*
    Wing_Thickness, at (0, y_pos, -Body_Height+Wing_Radius)."""
    cyl = trimesh.creation.cylinder(radius=Wing_Radius, height=Body_Slot_Width + 2 * Wing_Thickness,
                                     sections=Wing_Fn)
    cyl = sp.scad_transform(cyl, ("translate", [0, y_pos, -Body_Height + Wing_Radius]),
                             ("rotate", [0, 90, 0]))
    return cyl.vertices


def _body_hull(corner_height):
    """hull() of the 4 corner posts (at z=[-Face_Thickness, -Face_Thickness
    +corner_height]) and the 2 wing cylinders - see module docstring for
    why this is ONE convex_hull() call, not v1's nested hull()s."""
    _require_configured()
    corner_v = _corner_post_verts(corner_height, Corner_Fn)
    corner_v = corner_v.copy()
    corner_v[:, 2] -= Face_Thickness
    lower_y = (Body_Height - Wing_Radius) * np.sin(np.radians(Lower_Wing_Angle)) + Wing_Radius
    upper_y = Body_Length - (Body_Height - Wing_Radius) * np.sin(np.radians(Upper_Wing_Angle)) - Wing_Radius
    all_v = np.concatenate([corner_v, _wing_cyl_verts(lower_y), _wing_cyl_verts(upper_y)], axis=0)
    return trimesh.Trimesh(vertices=all_v, process=True).convex_hull


def BodyHull():
    return _body_hull(Face_Thickness)


def EnvelopeHull():
    """The enlarged envelope used only to clip drafted-text/logo overflow
    back to the body's own footprint (v1's "Clean Exposed Minkowski
    Manifold", 184-206) - corner posts extended to Face_Thickness+10 tall
    (see module docstring's _clean_exposed_minkowski note)."""
    return _body_hull(Face_Thickness + 10.0)


# -------------------------------------------------------------- Draft text

def _draft_cone(cone_segments=None, draft_angle_deg=None):
    """v1's draft cone (e.g. 178-180): cylinder(h=Engraving_Depth*
    Minkowski_Multiplier, r1=sin(Draft_Angle)*that height, r2=0),
    translated so its APEX sits at z=0 and its wide base at z=-h - same
    "widen toward the root" construction glyph_poc.build_glyph() uses,
    but v1's OWN real formula (sin(Draft_Angle), not build_glyph's
    cylinder-family tan(half-angle) formula) - a real, different physical
    model, ported as-is rather than reconciled with build_glyph's.
    cone_segments/draft_angle_deg override config's quality.minkowski_fn/
    build.draft_angle_deg when given, matching generate.py's uniform
    per-call CLI-override convention (threaded explicitly, not via global
    mutation - see lib/bennett.py/lib/mignon.py for the same idiom)."""
    fn = Minkowski_Fn if cone_segments is None else cone_segments
    angle = Draft_Angle if draft_angle_deg is None else draft_angle_deg
    h = Engraving_Depth * Minkowski_Multiplier
    r1 = np.sin(np.radians(angle)) * h
    cone = Manifold.cylinder(h, r1, 0.0, circular_segments=fn)
    return cone.translate([0, 0, -h])


def _platen_cyl_pair(y_pos, platen_fn=None):
    """The 2-cylinder platen cutout (e.g. v1:169-175) - built in local
    (pre-rotate) space, THEN rotate([0,90,0])+translate([0,y_pos,
    Engraving_Depth+Platen_Diameter/2]) applied to both, matching v1's
    `translate(...) rotate(...) { cylinder(); translate(...) cylinder();
    }` child order exactly (rotate is the INNER op, translate OUTER -
    scad_transform's own documented top-to-bottom convention)."""
    fn = Platen_Fn if platen_fn is None else platen_fn
    c1 = trimesh.creation.cylinder(radius=Platen_Diameter / 2.0, height=Body_Width, sections=fn)
    c2 = sp.translate(c1.copy(), [0, Platen_Shift_Motion, 0])
    return [sp.scad_transform(m, ("translate", [0, y_pos, Engraving_Depth + Platen_Diameter / 2.0]),
                               ("rotate", [0, 90, 0]))
            for m in (c1, c2)]


def _align_kwargs():
    return dict(mode=Align_Mode, center_offset_mm=Align_Center_Offset_Mm,
                left_offset_mm=Align_Left_Offset_Mm,
                modified_left_chars=Align_Modified_Left_Chars,
                modified_left_offset_mm=Align_Modified_Left_Offset_Mm,
                modified_right_chars=Align_Modified_Right_Chars,
                modified_right_offset_mm=Align_Modified_Right_Offset_Mm,
                caret_drop_mm=Align_Caret_Drop_Mm,
                underscore_lift_mm=Align_Underscore_Lift_Mm)


def DraftText(flatness_tolerance_mm=None, minkowski_enabled=None, draft_angle_deg=None,
              cone_segments=None, platen_fn=None):
    """"Create Draft Angle Text" (v1:158-181) - Lower_Char at y=Baseline,
    Upper_Char at y=Baseline+Baselines_Shift_Motion, both mirrored
    together (matches v1's mirror([1,0,0]) wrapping both children, and
    build_glyph()'s own shift-then-mirror order), unioned into ONE flat
    2D shape, platen-cut (2 real boolean cylinders, BEFORE the Minkowski
    sum per CLAUDE.md's curvature-before-Minkowski invariant), then
    Minkowski-summed with _draft_cone()."""
    _require_configured()
    flatness_tolerance_mm = DEFAULT_FLATNESS_TOLERANCE_MM if flatness_tolerance_mm is None else flatness_tolerance_mm
    minkowski_enabled = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled

    face = load_font_face(FONT_PATH)
    scale = em_to_mm_scale(Font_Size, face.units_per_EM)
    align_kwargs = _align_kwargs()
    contours = []
    for ch, y in ((Lower_Char, Baseline), (Upper_Char, Baseline + Baselines_Shift_Motion)):
        c_contours, advance_mm = get_glyph_contours_and_advance(ch, flatness_tolerance_mm, scale, font_path=FONT_PATH)
        x_shift, y_shift = alignment_offset(ch, advance_mm, **align_kwargs)
        for c in c_contours:
            contours.append(c + np.array([x_shift, y + y_shift]))
    contours = [c * np.array([-1.0, 1.0]) for c in contours]  # mirror([1,0,0]) - struck character

    flat = classify_and_triangulate(contours)
    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces, Character_Block_Height_Mm)

    scalloped = sp.to_manifold(prism)
    for cutter in _platen_cyl_pair(Aligning_Cut, platen_fn=platen_fn):
        scalloped = scalloped - sp.to_manifold(cutter)

    if not minkowski_enabled:
        return sp.from_manifold(scalloped)

    drafted = scalloped.minkowski_sum(_draft_cone(cone_segments=cone_segments, draft_angle_deg=draft_angle_deg))
    return sp.from_manifold(drafted)


# ------------------------------------------------------------------- Logo

def _minkowski_draft_flat2d(flat_mesh, block_height_mm, minkowski_enabled, cone_segments=None, draft_angle_deg=None):
    """Shared by Logo()/VogueMark(): extrude a flat 2D triangulated shape
    to block_height_mm, Minkowski-sum with the SAME _draft_cone()
    construction DraftText() uses (v1 reuses the identical Engraving_
    Depth*Minkowski_Multiplier/Draft_Angle cone for its SVG logo(s) too -
    e.g. v1:142-145/153-156/122-125)."""
    prism = trimesh.creation.extrude_triangulation(flat_mesh.vertices[:, :2], flat_mesh.faces, block_height_mm)
    if not minkowski_enabled:
        return prism
    drafted = sp.to_manifold(prism).minkowski_sum(_draft_cone(cone_segments=cone_segments, draft_angle_deg=draft_angle_deg))
    return sp.from_manifold(drafted)


def Logo(flatness_tolerance_mm=None, minkowski_enabled=None, cone_segments=None, draft_angle_deg=None):
    """"SVG Logo" (v1:135-146) - one imported SVG, scaled/positioned along
    the body's centerline at Body_Length*SVG_Location, Minkowski-drafted
    same as the struck text. Uses Logo_Scale_Mm_Per_Unit - see VogueMark()'s
    docstring for why that's a DIFFERENT global than the one it uses."""
    _require_configured()
    flatness_tolerance_mm = DEFAULT_FLATNESS_TOLERANCE_MM if flatness_tolerance_mm is None else flatness_tolerance_mm
    minkowski_enabled = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled
    flat = svg_import.build_svg_logo_mesh_2d(
        [Logo_Svg_File], flatness_tolerance_mm, Logo_Scale_Mm_Per_Unit,
        offsets=[(0.0, Body_Length * Logo_Location)])
    return _minkowski_draft_flat2d(flat, Logo_Depth_Mm, minkowski_enabled,
                                    cone_segments=cone_segments, draft_angle_deg=draft_angle_deg)


def VogueMark(flatness_tolerance_mm=None, minkowski_enabled=None, cone_segments=None, draft_angle_deg=None):
    """"Vogue Foundry Mark" (v1/VogueSlug.scad:109-126) - the real
    2-piece arrow+V mark, each with its own offset, drafted together as
    ONE combined swept solid (see svg_import.build_svg_logo_mesh_2d's own
    docstring for why the offsets are applied before triangulation, not
    after). Uses its OWN Vogue_Scale_Mm_Per_Unit, not Logo_Scale_Mm_Per_Unit -
    v1 itself has two genuinely different scale variables here (SVG_Scale=
    1/40*SVG_Size for AR1/Logo() vs SVG_V1_Scale=1/80*SVG_V1_Size for this
    mark, VogueSlug.scad:55-56) - a real, if small, self-contained SVG with
    a very different raw-path-unit size than AR1.svg's own much larger
    viewBox. A single shared field here previously gave whichever logo
    WASN'T tuned an ~8x wrong scale - see config/vogue_slug.yaml's logo.
    vogue_scale_mm_per_unit comment."""
    _require_configured()
    flatness_tolerance_mm = DEFAULT_FLATNESS_TOLERANCE_MM if flatness_tolerance_mm is None else flatness_tolerance_mm
    minkowski_enabled = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled
    y0 = Body_Length * Logo_Location
    flat = svg_import.build_svg_logo_mesh_2d(
        [Vogue_Arrow_Svg_File, Vogue_V_Svg_File], flatness_tolerance_mm, Vogue_Scale_Mm_Per_Unit,
        offsets=[(0.2, y0 - 0.5), (-0.5, y0 - 1.2)])
    return _minkowski_draft_flat2d(flat, Logo_Depth_Mm, minkowski_enabled,
                                    cone_segments=cone_segments, draft_angle_deg=draft_angle_deg)


# --------------------------------------------------------------- Cleanup

def _clean_exposed_minkowski(core):
    """"Clean Exposed Minkowski Manifold" (v1:152-176) - see module
    docstring for why this is a direct intersection with EnvelopeHull()
    rather than v1's own box-minus-envelope subtraction."""
    return core.intersection(EnvelopeHull(), engine="manifold")


# --------------------------------------------------------------- Cutters

def TypebarSlot():
    """v1:208-210."""
    _require_configured()
    return sp.box_centered([Body_Slot_Width, Body_Length + 1, Body_Height + 1],
                            [0, Body_Length / 2.0, -Bottom_Thickness - (Body_Height + 1) / 2.0])


def CopyrightText():
    """Engraved copyright text on the side face (v1:217-220 - the working
    block; the commented-out 212-215 alternative is dead in the real
    source and not ported). Left-to-right natural-advance layout,
    centered, matching spherical_machine.Labels()'s own convention for a
    plain engraved string."""
    _require_configured()
    if not Copyright_Text:
        return None
    face = load_font_face(Copyright_Font)
    scale = em_to_mm_scale(Body_Slot_Width * 0.75, face.units_per_EM)
    cursor = 0.0
    parts = []
    for ch in Copyright_Text:
        if ch == " ":
            cursor += Body_Slot_Width * 0.75 * 0.3
            continue
        try:
            _, adv = get_glyph_contours_and_advance(ch, DEFAULT_FLATNESS_TOLERANCE_MM, scale, font_path=Copyright_Font)
        except Exception as e:
            print(f"CopyrightText: skipping {ch!r} ({e})", flush=True)
            continue
        from glyph_poc import build_flat_text
        m = build_flat_text(ch, DEFAULT_FLATNESS_TOLERANCE_MM, Copyright_Depth + 0.01,
                             font_size_mm=Body_Slot_Width * 0.75, font_path=Copyright_Font)
        parts.append(sp.translate(m, [cursor, 0, 0]))
        cursor += adv
    if not parts:
        return None
    text_mesh = sp.translate(sp.union_all(parts), [-cursor / 2.0, 0, 0])
    return sp.scad_transform(
        text_mesh,
        ("translate", [Body_Width / 2.0 - Copyright_Depth, Body_Length / 2.0, -Face_Thickness + 0.1]),
        ("rotate", [90, 0, 90]))


def Ticks():
    """Gauge tick-hole ladder (gauge_slug.py only - v1/Type Slugs/
    GaugeTypeSlugSlug.scad:104-112). Two independent rows of same-
    diameter side-drilled holes at different Z heights: a fine row every
    Gauge_Fine_Pitch_Mm, a coarser row every Gauge_Major_Pitch_Mm - both
    usable as measurement graduations once installed on the real
    machine (this is the ONE real functional/measuring variant of this
    family - see lib/gauge_slug.py's module docstring)."""
    _require_configured()
    holes = []
    n = np.arange(0.0, Body_Length + 1e-9, Gauge_Fine_Pitch_Mm)
    for y in n:
        c = sp.cylinder_z(Gauge_Hole_D_Mm, Body_Height + 0.001, sections=Gauge_Hole_Fn, base_z=Gauge_Fine_Z_Mm)
        holes.append(sp.translate(c, [-Body_Width / 2.0, y, 0]))
    n2 = np.arange(Gauge_Major_Pitch_Mm, Body_Length + 1e-9, Gauge_Major_Pitch_Mm)
    for y in n2:
        c = sp.cylinder_z(Gauge_Hole_D_Mm, Body_Height + 0.001, sections=Gauge_Hole_Fn, base_z=Gauge_Major_Z_Mm)
        holes.append(sp.translate(c, [-Body_Width / 2.0, y, 0]))
    return sp.union_all(holes)


def PostHole():
    _require_configured()
    c = trimesh.creation.cylinder(radius=Post_ID / 2.0, height=10.0, sections=Post_Fn)
    c = sp.scad_transform(c, ("translate", _post_coords()), ("rotate", [0, 90, 0]))
    return c


def SideHole():
    _require_configured()
    c = trimesh.creation.cylinder(radius=Side_Hole_ID / 2.0, height=10.0, sections=Side_Hole_Fn)
    hole_coords = [0, Body_Length - (Body_Height * Side_Hole_Height) * np.sin(np.radians(Upper_Wing_Angle)) - Side_Hole_ID,
                   -Body_Height * Side_Hole_Height]
    return sp.scad_transform(c, ("translate", hole_coords), ("rotate", [0, 90, 0]))


# -------------------------------------------------------- Additive extras

def _post_coords():
    return [0, Body_Length - (Body_Height - Wing_Radius) * np.sin(np.radians(Upper_Wing_Angle)) - Wing_Radius,
            -Body_Height + Wing_Radius]


def Loop():
    """"Loop" (v1:247-254) - a torus, via scad_primitives.torus() (shared
    with lib/box_slug.py's identical Loop() recipe)."""
    _require_configured()
    ring = sp.torus(Loop_Diameter / 2.0 - Loop_Thickness / 2.0, Loop_Thickness,
                     sections=Loop_Fn, tube_sections=Loop_Tube_Fn)
    return sp.scad_transform(ring, ("translate", [0, Body_Length, -Loop_Thickness / 2.0]),
                              ("rotate", [0, Loop_Rotation, 0]))


def Post():
    """"Post and Hole" (v1:256-273) - a small rounded-boss nub via
    shapely (rectangle minus a corner circle, matching v1's
    polygon()-minus-circle profile), revolved."""
    _require_configured()
    r_out = Post_ID / 2.0 + Post_OD / 2.0 + Body_Slot_Width / 2.0
    rect = ShapelyPolygon([(Post_ID / 2.0, 0), (Post_ID / 2.0, Body_Slot_Width),
                            (r_out, Body_Slot_Width), (r_out, 0)])
    corner = ShapelyPoint(r_out, Body_Slot_Width / 2.0).buffer(Body_Slot_Width / 2.0, resolution=Post_Fn // 4)
    profile_poly = rect.difference(corner)
    profile = list(profile_poly.exterior.coords)
    boss = sp.revolve_polygon(profile, sections=Post_Fn)
    return sp.scad_transform(boss, ("translate", _post_coords()),
                              ("translate", [-Body_Slot_Width / 2.0, 0, 0]), ("rotate", [0, 90, 0]))


def ResinSupportGeometry():
    """"Resin Support" (v1:223-245) - a sloped raft plate (hull of 2
    parallel rects at different Z/XY size) plus per-station wire+taper+
    tip-sphere supports along both sides of the typebar slot. See module
    docstring for why this doesn't reuse resin_support.resin_rod()."""
    _require_configured()
    raft_top = sp.box_centered([Body_Width + 4, Body_Length + 4, 0.001],
                                [0, Body_Length / 2.0, -Body_Height - Support_Height])
    raft_bottom = sp.box_centered([Body_Width, Body_Length, 0.001],
                                   [0, Body_Length / 2.0, -Body_Height - Support_Height - Raft_Thickness])
    raft = trimesh.Trimesh(vertices=np.concatenate([raft_top.vertices, raft_bottom.vertices]),
                            process=True).convex_hull

    parts = [raft]
    y_start = (Body_Height - Wing_Radius) * np.sin(np.radians(Lower_Wing_Angle)) + Wing_Radius
    y_end = Body_Length - (Body_Height - Wing_Radius) * np.sin(np.radians(Upper_Wing_Angle)) - Wing_Radius
    for y in np.arange(y_start, y_end + 1e-9, Support_Pitch):
        for side in (1.0, -1.0):
            x = side * (Body_Slot_Width / 2.0 + Wing_Thickness / 2.0)
            z0 = -Body_Height - Support_Height
            wire = sp.cylinder_z(Wire_Thickness, Support_Height - 1.0, sections=Resin_Fn, base_z=z0)
            taper = sp.frustum_z(Wire_Thickness, 0.3, 1.0, sections=Resin_Fn, base_z=z0 + Support_Height - 1.0)
            tip = trimesh.creation.icosphere(subdivisions=2, radius=0.15)
            tip.apply_translation([0, 0, z0 + Support_Height])
            station = trimesh.util.concatenate([wire, taper, tip])
            parts.append(sp.translate(station, [x, y, 0]))
    return sp.union_all(parts)


# ------------------------------------------------------------------ Element

def _assemble_core(flatness_tolerance_mm, minkowski_enabled, draft_angle_deg, cone_segments, platen_fn):
    parts = [BodyHull()]
    drafted_any = False
    if Character_Enabled:
        parts.append(DraftText(flatness_tolerance_mm=flatness_tolerance_mm,
                                minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
                                cone_segments=cone_segments, platen_fn=platen_fn))
        drafted_any = True
    if Logo_Enabled:
        parts.append(Logo(flatness_tolerance_mm=flatness_tolerance_mm, minkowski_enabled=minkowski_enabled,
                           cone_segments=cone_segments, draft_angle_deg=draft_angle_deg))
        drafted_any = True
    if Logo_Vogue_Enabled:
        parts.append(VogueMark(flatness_tolerance_mm=flatness_tolerance_mm, minkowski_enabled=minkowski_enabled,
                                cone_segments=cone_segments, draft_angle_deg=draft_angle_deg))
        drafted_any = True
    core = sp.union_all(parts)
    if drafted_any:
        core = _clean_exposed_minkowski(core)
    return core


def Additive(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
             cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    """separation_mm/render_core_groove are accepted-but-ignored - this
    machine has neither concept (see module docstring's DraftText note
    and CLAUDE.md's Selectric precedent for this exact pattern).
    cone_segments/platen_fn are threaded explicitly down to _draft_cone/
    _platen_cyl_pair (falling back to config's quality.minkowski_fn/
    platen_fn only at that point of use), matching lib/bennett.py's/lib/
    mignon.py's own idiom - not a global-mutation override."""
    _require_configured()
    parts = [_assemble_core(flatness_tolerance_mm, minkowski_enabled, draft_angle_deg, cone_segments, platen_fn)]
    if Element_Loop_Enabled:
        parts.append(Loop())
    if Element_Post_Enabled:
        parts.append(Post())
    return sp.union_all(parts)


def Subtractive():
    _require_configured()
    cutters = [TypebarSlot()]
    copyright_mesh = CopyrightText()
    if copyright_mesh is not None:
        cutters.append(copyright_mesh)
    if Gauge_Enabled:
        cutters.append(Ticks())
    if Element_Post_Enabled:
        cutters.append(PostHole())
    if Element_Side_Hole_Enabled:
        cutters.append(SideHole())
    return sp.union_all(cutters)


def FullElement(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
                cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    additive = Additive(flatness_tolerance_mm=flatness_tolerance_mm, separation_mm=separation_mm,
                         render_core_groove=render_core_groove, cone_segments=cone_segments,
                         platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                         draft_angle_deg=draft_angle_deg)
    result = additive.difference(Subtractive(), engine="manifold")
    result, _, _, _ = sp.check_and_repair(result, label="FullElement")
    build_log.mesh_report(result, "FullElement")
    return result, []


def ResinPrint(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
               cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    full, char_parts = FullElement(flatness_tolerance_mm=flatness_tolerance_mm, separation_mm=separation_mm,
                                    render_core_groove=render_core_groove, cone_segments=cone_segments,
                                    platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                    draft_angle_deg=draft_angle_deg)
    support = ResinSupportGeometry()
    build_log.mesh_report(support, "ResinSupport")
    combined = sp.union_all([full, support])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts
