"""
Shared "box body" type-slug engine - lib/oliver_slug.py (Oliver
typewriter slug replica) and lib/lumi_slug.py (novelty pendant) both
configure this module and share everything here, same "shared engine +
thin per-variant module" pattern lib/wing_slug.py uses for lib/
type_slug.py/vogue_slug.py/gauge_slug.py.

Ground truth is v1 (v1/Type Slugs/OliverSlug.scad, v1/Type Slugs/
LumiSlug.scad), not v2 - see lib/wing_slug.py's module docstring for why
(this whole family was never carried into v2). A genuinely different
form factor from the wing body family despite being another "type slug"
- a plain rectangular prism body (no rounded hull/wing-radius cylinders),
straight polygon-cut wing tapers instead of a curved hull silhouette,
N stacked struck characters (3 for Oliver, 4 for Lumi - config-driven
list, not a fixed pair), N platen cutout cylinders to match, no resin
support at all, no SVG logo, no post/side-hole. Verified function-by-
function against both real v1 sources before writing anything, per
CLAUDE.md's "diff against source first" rule (adapted to v1 here).

Function-by-function relationship to v1/Type Slugs/OliverSlug.scad
(lines 29-98 - LumiSlug.scad's own structure is byte-identical except
for its extra 4th character and the trailing Loop union, both ported
as config-driven options here, not separate code paths):
  - BodyBox() -> "Create Solid Type Body" (32-33).
  - DraftText() -> "Create Draft Angle Text" (35-59) - N stacked struck
    characters (character.chars, config-driven length), same shift-then-
    mirror-then-platen-cut-then-Minkowski-sum construction as lib/
    wing_slug.py's own DraftText(), but this family's OWN real cone
    formula (h=Engraving_Depth*1.5, a HARDCODED 1.5 in v1 - not the
    customizable Minkowski_Multiplier the wing family has - still routed
    through build.minkowski_multiplier here since it's a real geometry-
    affecting constant either way, just a different real default per
    CLAUDE.md's "keep the numeric constant in that machine's YAML"
    rule) and N platen cylinders, not the wing family's fixed pair.
  - _typebar_and_wing_taper_cuts() -> "Cut Typebar Slot"/"Cut Wing
    Tapers" (68-82), both real children of one shared rotate([-90,0,0])
    group - built here as 3 local (pre-rotate) meshes unioned first, one
    rotate applied once (linear op, safe to batch - same simplification
    lib/wing_slug.py's EnvelopeHull already makes for its own nested
    hull()s).
  - _wing_angle_cut() -> "Cut Upper/Lower Wing Angle" (85-95) - TWO
    separate top-level cuts, both real. v1's own Lower_Wing_Angle
    variable (declared line 20) is NEVER referenced by either cut - both
    literally use Upper_Wing_Angle (line 89's own polygon() call, and
    line 95's IDENTICAL polygon() call) - a real, preserved v1 quirk,
    not a transcription choice made here. Not ported as a usable
    config key at all (dead in the real source), per CLAUDE.md's
    "say so explicitly instead of silently diverging" convention -
    see config/oliver_slug.yaml's/lumi_slug.yaml's own comment.
  - Loop() -> LumiSlug.scad's own trailing "if (Loop==true)" block
    (113-120) - byte-identical recipe to lib/wing_slug.py's Loop(),
    both now built via the shared scad_primitives.torus() (see that
    function's own docstring). OliverSlug.scad has no Loop concept at
    all - element.loop_enabled: false for oliver_slug.yaml is the real
    behavior, not a placeholder.
  - No resin support anywhere in either real v1 source (unlike the wing
    family) - ResinPrint() here is a real no-op passthrough to
    FullElement(), same pattern lib/helios.py's own ResinPrint()
    establishes for a machine with no resin-support geometry modeled
    (see tune.py's RESIN_SUPPORT_UNAVAILABLE_NOTE for the matching UI
    callout, extended here for oliver_slug/lumi_slug).

Assembly order for the Loop, faithfully preserved even though it looks
almost like lib/wing_slug.py's own Loop handling: LumiSlug.scad's Loop
is added AFTER (outside) the difference() that applies the typebar-
slot/wing-taper/wing-angle cuts (`union(){ difference(){...cuts...};
loop; }`), so it is NEVER itself subject to any of those cuts - a real,
different assembly order from lib/wing_slug.py's Loop (which sits
INSIDE the union that later gets its own final typebar-slot/copyright/
hole cuts applied, physically a no-op there since Loop sits well clear
of those cutters, but structurally different source code, ported as
such rather than unified).
"""

import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import Polygon as ShapelyPolygon

from glyph_poc import (get_glyph_contours_and_advance, classify_and_triangulate,
                        alignment_offset, em_to_mm_scale, load_font_face)
import scad_primitives as sp
import build_log

_active_machine = None


def _receive_config(source_globals, machine_name):
    global _active_machine
    if _active_machine not in (None, machine_name):
        raise RuntimeError(
            f"box_slug already configured for {_active_machine!r}; "
            f"cannot reconfigure for {machine_name!r} in the same process")
    _active_machine = machine_name
    globals().update({k: v for k, v in source_globals.items() if k[:1].isupper() or k == "z"})


def _require_configured():
    if _active_machine is None:
        raise RuntimeError("call <machine>.configure(config_path) before using this module")


# ------------------------------------------------------------------ Body

def BodyBox():
    """"Create Solid Type Body" (v1:32-33)."""
    _require_configured()
    return sp.box_centered([Body_Width, Body_Length, Body_Height],
                            [0.0, Body_Length / 2.0, -Body_Height / 2.0])


# -------------------------------------------------------------- Draft text

def _draft_cone(cone_segments=None, draft_angle_deg=None):
    """v1's draft cone (e.g. :62-64): cylinder(h=Engraving_Depth*1.5,
    r1=sin(Draft_Angle)*that height, r2=0) - same "widen toward the
    root" construction as lib/wing_slug.py's own _draft_cone(), same
    real sin(Draft_Angle) formula, just this family's own 1.5 multiplier
    (build.minkowski_multiplier - see module docstring)."""
    fn = Minkowski_Fn if cone_segments is None else cone_segments
    angle = Draft_Angle if draft_angle_deg is None else draft_angle_deg
    h = Engraving_Depth * Minkowski_Multiplier
    r1 = np.sin(np.radians(angle)) * h
    cone = Manifold.cylinder(h, r1, 0.0, circular_segments=fn)
    return cone.translate([0, 0, -h])


def _platen_cylinders(platen_fn=None):
    """N platen cutout cylinders (v1:50-58 - 3 for Oliver, 4 for Lumi),
    stacked at Aligning_Cut + n*Platen_Shift_Motion. Built in local
    (pre-rotate) space then rotate([0,90,0])+translate([0,Aligning_Cut,
    Engraving_Depth+Platen_Diameter/2]) applied to the whole stack -
    same translate-outer/rotate-inner order as lib/wing_slug.py's own
    _platen_cyl_pair (v1:51-58 - `translate(...) rotate(...){cylinder();
    translate() cylinder(); translate() cylinder();}`)."""
    fn = Platen_Fn if platen_fn is None else platen_fn
    base = trimesh.creation.cylinder(radius=Platen_Diameter / 2.0, height=Body_Width, sections=fn)
    cyls = [sp.translate(base.copy(), [0, n * Platen_Shift_Motion, 0]) for n in range(len(Character_Chars))]
    return [sp.scad_transform(m, ("translate", [0, Aligning_Cut, Engraving_Depth + Platen_Diameter / 2.0]),
                               ("rotate", [0, 90, 0]))
            for m in cyls]


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
    """"Create Draft Angle Text" (v1:35-59) - character.chars stacked at
    y=Baseline + n*Baselines_Shift_Motion (bottom to top: Figure_Char,
    Lower_Char, Upper_Char for Oliver; +fun_char for Lumi), mirrored
    together, unioned into ONE flat 2D shape, platen-cut (N real boolean
    cylinders, BEFORE the Minkowski sum per CLAUDE.md's curvature-
    before-Minkowski invariant), then Minkowski-summed with
    _draft_cone()."""
    _require_configured()
    flatness_tolerance_mm = DEFAULT_FLATNESS_TOLERANCE_MM if flatness_tolerance_mm is None else flatness_tolerance_mm
    minkowski_enabled = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled

    face = load_font_face(FONT_PATH)
    scale = em_to_mm_scale(Font_Size, face.units_per_EM)
    align_kwargs = _align_kwargs()
    contours = []
    for n, ch in enumerate(Character_Chars):
        y = Baseline + n * Baselines_Shift_Motion
        c_contours, advance_mm = get_glyph_contours_and_advance(ch, flatness_tolerance_mm, scale, font_path=FONT_PATH)
        x_shift, y_shift = alignment_offset(ch, advance_mm, **align_kwargs)
        for c in c_contours:
            contours.append(c + np.array([x_shift, y + y_shift]))
    contours = [c * np.array([-1.0, 1.0]) for c in contours]  # mirror([1,0,0]) - struck character

    flat = classify_and_triangulate(contours)
    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces, Character_Block_Height_Mm)

    scalloped = sp.to_manifold(prism)
    for cutter in _platen_cylinders(platen_fn=platen_fn):
        scalloped = scalloped - sp.to_manifold(cutter)

    if not minkowski_enabled:
        return sp.from_manifold(scalloped)

    drafted = scalloped.minkowski_sum(_draft_cone(cone_segments=cone_segments, draft_angle_deg=draft_angle_deg))
    return sp.from_manifold(drafted)


# --------------------------------------------------------------- Cutters

def _wing_taper_local(mirror_x):
    """One wing-taper profile (v1:78/80-81), extruded along Z by
    Body_Length+.002 then shifted by the shared translate([0,0,-.001])
    both copies sit under (v1:76)."""
    pts = [(Body_Width / 2.0, 0.0), (Body_Width / 2.0, -Engraving_Depth),
           (Body_Width / 2.0 + 1.0, -Engraving_Depth), (Body_Width / 2.0 + 1.0, Body_Height),
           (Body_Slot_Width / 2.0 + Wing_Thickness, Body_Height)]
    if mirror_x:
        pts = [(-x, y) for x, y in pts]
    mesh = trimesh.creation.extrude_polygon(ShapelyPolygon(pts), Body_Length + 0.002)
    mesh.apply_translation([0, 0, -0.001])
    return mesh


def _typebar_and_wing_taper_cuts():
    """"Cut Typebar Slot"/"Cut Wing Tapers" (v1:68-82) - both real
    children of one shared rotate([-90,0,0]) group (v1:68). See module
    docstring for why this is one batched rotate over the union, not
    three separate per-part transforms."""
    slot = sp.box_centered([Body_Slot_Width, 10.0, Body_Length + 0.002],
                            [0.0, Bottom_Thickness + 5.0, Body_Length / 2.0])
    local = sp.union_all([slot, _wing_taper_local(False), _wing_taper_local(True)])
    return sp.scad_transform(local, ("rotate", [-90, 0, 0]))


def _wing_angle_cut(translate_xyz, rotate_xyz, angle_deg):
    """"Cut Upper/Lower Wing Angle" (v1:85-95) - both real cuts use
    Upper_Wing_Angle (see module docstring's Lower_Wing_Angle note)."""
    h15 = Body_Height * 1.5
    pts = [(-0.001, 0.0),
           (h15 * np.sin(np.radians(angle_deg)), -h15 * np.cos(np.radians(angle_deg))),
           (-Engraving_Depth, -h15), (-Engraving_Depth, Engraving_Depth), (0.0, Engraving_Depth)]
    mesh = trimesh.creation.extrude_polygon(ShapelyPolygon(pts), 10.0)
    return sp.scad_transform(mesh, ("translate", translate_xyz), ("rotate", rotate_xyz))


def Subtractive():
    _require_configured()
    cuts = [_typebar_and_wing_taper_cuts(),
            _wing_angle_cut([5.0, Body_Length, 0.0], [90, 0, -90], Upper_Wing_Angle),
            _wing_angle_cut([-5.0, 0.0, 0.0], [90, 0, 90], Upper_Wing_Angle)]
    return sp.union_all(cuts)


# -------------------------------------------------------- Additive extras

def Loop():
    """LumiSlug.scad's trailing Loop block (v1:113-120) - see module
    docstring for the shared scad_primitives.torus() recipe."""
    _require_configured()
    ring = sp.torus(Loop_Diameter / 2.0 - Loop_Thickness / 2.0, Loop_Thickness,
                     sections=Loop_Fn, tube_sections=Loop_Tube_Fn)
    return sp.scad_transform(ring, ("translate", [0, Body_Length, -Loop_Thickness / 2.0]),
                              ("rotate", [0, Loop_Rotation, 0]))


# ------------------------------------------------------------------ Element

def Additive(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
             cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    """separation_mm/render_core_groove are accepted-but-ignored - this
    machine has neither concept, same pattern lib/wing_slug.py's own
    Additive() and the Selectric family establish."""
    _require_configured()
    return sp.union_all([
        BodyBox(),
        DraftText(flatness_tolerance_mm=flatness_tolerance_mm, minkowski_enabled=minkowski_enabled,
                  draft_angle_deg=draft_angle_deg, cone_segments=cone_segments, platen_fn=platen_fn),
    ])


def FullElement(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
                cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    """v1's `union(){ difference(){additive; cuts;}; loop; }` (see module
    docstring - Loop, when enabled, sits OUTSIDE the cut difference, not
    inside it)."""
    _require_configured()
    additive = Additive(flatness_tolerance_mm=flatness_tolerance_mm, separation_mm=separation_mm,
                         render_core_groove=render_core_groove, cone_segments=cone_segments,
                         platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                         draft_angle_deg=draft_angle_deg)
    result = additive.difference(Subtractive(), engine="manifold")
    if Element_Loop_Enabled:
        result = sp.union_all([result, Loop()])
    result, _, _, _ = sp.check_and_repair(result, label="FullElement")
    build_log.mesh_report(result, "FullElement")
    return result, []


def ResinSupport():
    """No resin-support geometry exists anywhere in either real v1
    source for this family (see module docstring) - real function
    returning None, same convention lib/helios.py's own ResinSupport()
    establishes for a machine with none modeled."""
    return None


def ResinPrint(flatness_tolerance_mm=None, separation_mm=None, render_core_groove=None,
               cone_segments=None, platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    """Real no-op passthrough to FullElement() - see module docstring
    and lib/helios.py's own ResinPrint() for the established precedent."""
    _require_configured()
    return FullElement(flatness_tolerance_mm=flatness_tolerance_mm, separation_mm=separation_mm,
                        render_core_groove=render_core_groove, cone_segments=cone_segments,
                        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                        draft_angle_deg=draft_angle_deg)
