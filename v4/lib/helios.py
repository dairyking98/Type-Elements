"""
v4 full-fidelity Helios Klimax body - ports v2/heliosklimax.scad's
Assemble()/TypeTest() structure directly, using the SAME origin/orientation
convention as v2 (Z=0 at the bottom face of the main disk, Z+ up through
the clip end - Baseline_Z_Offset=Element_Height, Helios's Baseline/Cutout
arrays are negative-from-clip-end, the SAME convention Blickensderfer/
Postal use, NOT Bennett/Mignon's absolute-from-bottom convention - see
v2/heliosklimax.scad's own file-header CORRECTION note).

All real-machine numbers live in config/helios.yaml, not here - call
configure(path) once before using anything else in this module (see
generate.py).

Diverges from cylinder_machine.py across essentially the whole body-
construction pipeline, same as Mignon/Bennett - confirmed by direct
comparison against v2/heliosklimax.scad: no SecondaryCore/CoreGrooves/
CoreChamfer/CoreEllipses/core_shaft.scad family at all (v2's own header:
"not applicable - Helios has no SecondaryCore/CoreGrooves/CoreChamfer/
CoreEllipses system in the original"), a 5-point-hull rotate_extrude()
hollow cavity (HollowingElement, true circular corner rounding via a real
shapely hull of circles - unlike cylinder_machine._hollow_space_profile's
hand-rounded point list) instead of HollowSpace()+BottomSlopedSpace(), a
plain boss+through-hole alignment pin (AlignmentPinSupport/AlignmentPinHole)
instead of a countersunk drive pin, and a hulled-cylinder wire clip
(WireClip) instead of core_shaft.scad's WireBite() shapely-hull-and-extrude
version - structurally similar in spirit (v2's own header: "similar in
spirit to Blick2/Postal's") but never extracted to a shared lib in v2
either, so not shared here. Only the glyph placement/text pipeline
(TextRing/CalibrationTextRing, reused directly with placement_protrusion=
-0.05/angle_half_step=0 - v2's Letter_Placement_Protrusion=-.05/
Angle_Half_Step=0, see place_on_cylinder's docstring) is genuinely shared.

Two-stage difference (NOT a simple Additive-Subtractive split): v2's real
Assemble() nests THREE difference()s, not one - AlignmentPinSupport()/
ClipRetainer() are added AFTER the first round of cuts (HollowingElement/
MinkCleanup/IndicatorHole) and are THEN themselves cut by the second round
(AlignmentPinHole/CenterShaftHole/WireClip). Flattening this into one
"additive union minus subtractive union" (like every other machine's
FullElement) would be WRONG here: HollowingElement's cavity genuinely
overlaps AlignmentPinSupport's boss position (radius 8.92mm falls inside
the cavity's radial span [Shaft_Diameter/2+Shell+Inside, Element_Diameter/2
-Shell-Inside], and the boss's z-range [1.5, 4.5] falls inside the
cavity's height span too - verified against v2's real x_min/x_max/y_min/
y_max formulas) - subtracting HollowingElement from a single flattened
union would eat the boss v2 never actually cuts there, since v2 only adds
the boss AFTER that cut already happened. Additive() below reproduces the
real staged construction (stage-1 cut, THEN union the bosses); FullElement's
own final difference is only the genuine outer-scope cut (AlignmentPinHole/
CenterShaftHole/WireClip).

No SecondaryCore-family Cyl_Fn user, no Logo/Label engraved text, no Shaft
Gauge Test (v2's own header: "Sections with no Helios equivalent (Logo,
Print Tolerances, Shaft Gauge Test) are omitted"). v2 also declares
Resin_Support/Resin_Support_* parameters but never builds any support
geometry with them (v2's own header, confirmed: no ResinRod/CutGroove-
equivalent module anywhere in the file) - ResinSupport()/ResinPrint() below
are a no-op/alias to FullElement(), matching that reality rather than
inventing a resin-support system that was never there.
"""

import trimesh

from glyph_poc import (
    DEFAULT_CONE_SEGMENTS as GLYPH_DEFAULT_CONE_SEGMENTS,
    DEFAULT_SIMPLIFY_TOLERANCE_MM as GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM,
    DEFAULT_PLATEN_FN as GLYPH_DEFAULT_PLATEN_FN,
    DEFAULT_MINKOWSKI_ENABLED as GLYPH_DEFAULT_MINKOWSKI_ENABLED,
    DEFAULT_DRAFT_ANGLE_DEG as GLYPH_DEFAULT_DRAFT_ANGLE_DEG,
)
import scad_primitives as sp
import cylinder_machine

_configured = False


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - see
    blickensderfer.configure()'s docstring for the general scheme. Helios's
    element: section has no wall/clip-height-under-a-drive-pin/core-groove
    keys at all - see the module docstring for why (no core_shaft.scad
    family, no drive pin)."""
    global _configured
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["FONT_SIZE_MM"] = font["size_mm"]

    e = cfg["element"]
    # v2/heliosklimax.scad:59 - z=.01, same magnitude as Blickensderfer/
    # Postal (not Mignon/Bennett's 0.001) - no divergence to explain.
    g["z"] = 0.01
    g["Platen_Diameter"] = e["platen_diameter"]
    g["Element_Diameter"] = e["element_diameter"]
    g["Min_Final_Character_Diameter"] = e["min_final_character_diameter"]
    g["Char_Protrusion"] = (e["min_final_character_diameter"] - e["element_diameter"]) / 2.0
    g["Element_Height"] = e["element_height"]
    g["Shaft_Diameter"] = e["shaft_diameter"]
    g["Element_Square_Hole_Position"] = e["element_square_hole_position"]
    g["Element_Square_Hole_Width"] = e["element_square_hole_width"]
    g["Element_Square_Hole_Length"] = e["element_square_hole_length"]
    g["Element_Square_Hole_Support_Height"] = e["element_square_hole_support_height"]
    g["Element_Indicator_Hole_Position"] = e["element_indicator_hole_position"]
    g["Element_Indicator_Hole_Diameter"] = e["element_indicator_hole_diameter"]
    g["Element_Shell_Thickness"] = e["element_shell_thickness"]
    g["Element_Inside_Radius"] = e["element_inside_radius"]
    g["Element_Clip_Height"] = e["element_clip_height"]
    g["Element_Clip_Diameter"] = e["element_clip_diameter"]
    g["Element_Wire_Diameter"] = e["element_wire_diameter"]
    g["Element_Clip_Bite"] = e["element_clip_bite"]
    g["Element_Clip_Angle"] = e["element_clip_angle"]

    q = cfg["quality"]
    # Cyl_Fn: declared for schema parity only - see config/helios.yaml's
    # matching comment, never referenced by any function below (verified
    # against v2's real Assemble()/TypeTest() - every cylinder there uses
    # Surface_Fn).
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Platen_Fn"] = q.get("platen_fn", GLYPH_DEFAULT_PLATEN_FN)

    layout = cfg["layout"]
    g["BASELINE_ROW"] = layout["baseline_row"]
    g["CUTOUT_ROW"] = layout["cutout_row"]
    g["LATITUDE_INT"] = 360.0 / layout["latitude_columns"]
    g["BASELINE_Z_OFFSET"] = g["Element_Height"]
    g["PLACEMENT_MAP"] = layout["placement_map"]
    # Physical_Layout=LAYOUT directly in v2 (no Char_Legend remap, unlike
    # Bennett/Mignon) - layout.rows is already in physical placement order.
    g["DHIATENSOR"] = layout["rows"]

    g["PLATEN_RADIUS_MM"] = 1.0 / g["Platen_Diameter"]

    # v2/heliosklimax.scad:268 - Letter_Placement_Protrusion=-.05 (a small
    # built-in 0.05mm radial inset - see the module docstring's CORRECTION
    # reference) and Angle_Half_Step=0 (no half-column centering term, like
    # Mignon) - threaded through cylinder_machine.place_on_cylinder as
    # explicit overrides (None everywhere else preserves Blickensderfer/
    # Postal's original hardcoded behavior).
    g["Placement_Protrusion"] = -0.05
    g["Angle_Half_Step"] = 0.0

    align = cfg["alignment"]
    g["ALIGN_KWARGS"] = {
        "mode": align["mode"],
        "center_offset_mm": align["center_offset_mm"],
        "left_offset_mm": align["left_offset_mm"],
        "modified_left_chars": align["modified_left_chars"],
        "modified_left_offset_mm": align["modified_left_offset_mm"],
        "modified_right_chars": align["modified_right_chars"],
        "modified_right_offset_mm": align["modified_right_offset_mm"],
    }

    b = cfg["build"]
    g["DEFAULT_POINTS_PER_MM"] = b["points_per_mm"]
    g["DEFAULT_SEPARATION_MM"] = b["separation_mm"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]
    g["DEFAULT_CONE_SEGMENTS"] = q.get("minkowski_fn", GLYPH_DEFAULT_CONE_SEGMENTS)
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM)
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", GLYPH_DEFAULT_MINKOWSKI_ENABLED)
    g["DEFAULT_DRAFT_ANGLE_DEG"] = b.get("draft_angle_deg", GLYPH_DEFAULT_DRAFT_ANGLE_DEG)

    # resin.* - declared-but-unused, see the module docstring/config
    # comment. Stored only so tune.py's Resin tab has something to show;
    # no function below reads these.
    r = cfg.get("resin", {})
    g["Resin_Support_Base_Thickness"] = r.get("resin_support_base_thickness", 2.0)
    g["Resin_Support_Rod_Thickness"] = r.get("resin_support_rod_thickness", 0.4)
    g["Resin_Support_Min_Height"] = r.get("resin_support_min_height", 1.0)
    g["Resin_Support_Spacing"] = r.get("resin_support_spacing", 3.0)
    g["Resin_Support_Contact_Radius"] = r.get("resin_support_contact_radius", 0.2)

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    # Calibration - see blickensderfer.configure()'s matching comment /
    # cylinder_machine.CalibrationTextRing's docstring. Helios's own real
    # Testing_Offsets=[-.5,-.4,...,.6] (12 columns) is exactly
    # testSweepArray(-0.5, 0.1, 12), the same start/interval Mignon's real
    # defaults use; vary_baseline/vary_cutout both false, same as Bennett.
    calibration = cfg.get("calibration", {})
    g["Calibration_Test_Char"] = calibration.get("test_char", "H")
    g["Calibration_Vary_Baseline"] = calibration.get("vary_baseline", False)
    g["Calibration_Vary_Cutout"] = calibration.get("vary_cutout", False)
    g["Calibration_Start"] = calibration.get("start", -0.5)
    g["Calibration_Interval"] = calibration.get("interval", 0.1)

    _configured = True
    cylinder_machine._receive_config(g, "helios")


def _require_configured():
    if not _configured:
        raise RuntimeError("call helios.configure(config_path) before using this module")


# ------------------------------------------------------------------- Body

def Cylinder():
    return sp.cylinder_z(Element_Diameter, Element_Height + 2 * z, sections=Surface_Fn, base_z=-z)


def HollowingElement():
    """v2/heliosklimax.scad ~286-320 - a rotate_extrude() of the 2D convex
    hull of 5 circles (Element_Inside_Radius each), i.e. a true rounded
    pentagon-ish cross-section, not cylinder_machine._hollow_space_profile's
    hand-rounded point list. Built the same way cylinder_machine.WireBite()/
    mignon.AlignmentPin() build a real shapely hull before revolving/
    extruding it."""
    from shapely.geometry import Point
    from shapely.ops import unary_union

    x_min = Shaft_Diameter / 2 + Element_Shell_Thickness + Element_Inside_Radius
    x_max = Element_Diameter / 2 - Element_Shell_Thickness - Element_Inside_Radius
    y_min = Element_Shell_Thickness + Element_Inside_Radius
    y_max = Element_Height - Element_Shell_Thickness - Element_Inside_Radius
    r = Element_Inside_Radius
    centers = [
        (x_min, y_min),               # Bottom Left
        (x_min, y_max - 0.5),         # Top Left
        (x_max, y_max - 0.5),         # Top Right
        ((x_min + x_max) / 2, y_max),  # Top
        (x_max, y_min),               # Bottom Right
    ]
    circles = [Point(px, py).buffer(r, resolution=32) for px, py in centers]
    hull_poly = unary_union(circles).convex_hull
    profile = list(hull_poly.exterior.coords)
    return sp.revolve_polygon(profile, sections=Surface_Fn)


def MinkCleanup():
    """v2 ~322-326 - top and bottom cleanup cylinders, $fn left unspecified
    in the source (defaults to OpenSCAD's low facet default) - a fixed 20,
    matching Bennett/Mignon's own precedent for this same kind of
    invisible-beyond-the-model cleanup cylinder, not a calibrated value."""
    top = sp.cylinder_z(Element_Diameter + 5, 5, sections=20, base_z=Element_Height)
    bottom = sp.cylinder_z(Element_Diameter + 5, 5, sections=20, base_z=-5)
    return sp.union_all([top, bottom])


def IndicatorHole():
    h = sp.cylinder_z(Element_Indicator_Hole_Diameter, 6, sections=Surface_Fn, center=True)
    return sp.translate(h, [Element_Indicator_Hole_Position, 0, Element_Height - Element_Shell_Thickness / 2])


def AlignmentPinSupport():
    """v2 ~333-335 - a boss the alignment pin hole is later cut through
    (see AlignmentPinHole()). $fn unspecified in source, same treatment as
    MinkCleanup() above - Surface_Fn here instead of a fixed 20 since this
    IS visible/functional model geometry, not a cleanup-only shape."""
    c = sp.cylinder_z(Element_Square_Hole_Width + 2, Element_Square_Hole_Support_Height, sections=Surface_Fn)
    return sp.translate(c, [-Element_Square_Hole_Position, 0, Element_Shell_Thickness - z])


def ClipRetainer():
    return sp.cylinder_z(Element_Clip_Diameter, Element_Clip_Height, sections=Surface_Fn,
                          base_z=Element_Height - z)


def AlignmentPinHole():
    return sp.box_centered(
        [Element_Square_Hole_Length, Element_Square_Hole_Width, 10],
        [-Element_Square_Hole_Position, 0, Element_Shell_Thickness / 2])


def CenterShaftHole():
    return sp.cylinder_z(Shaft_Diameter, Element_Height + Element_Clip_Height + 2 * z,
                          sections=Surface_Fn, base_z=-z)


def WireClip():
    """v2 ~350-359 - hull() of two cylinders (each tipped to lie along X),
    a tapered wire-bite channel - built as trimesh.util.concatenate(...).
    convex_hull (both inputs are convex), the same technique
    cylinder_machine.CoreEllipses()/RevolverSolid() use for a hull of
    solids trimesh has no direct primitive for."""
    c1 = sp.cylinder_z(Element_Wire_Diameter, 8, sections=Surface_Fn, center=True)
    c1 = sp.scad_transform(c1, ("rotate", [0, -90, 0]))
    c2 = sp.cylinder_z(Element_Wire_Diameter + 1.0, 8, sections=Surface_Fn, center=True)
    c2 = sp.scad_transform(c2, ("translate", [0, -5, 0.5]), ("rotate", [0, -90, 0]))
    hull = trimesh.util.concatenate([c1, c2]).convex_hull
    return sp.scad_transform(
        hull,
        ("rotate", [0, 0, Element_Clip_Angle]),
        ("translate", [0, -Shaft_Diameter / 2 - Element_Wire_Diameter / 2 + Element_Clip_Bite,
                        Element_Height + Element_Wire_Diameter / 2]),
    )


def HollowSpace():
    """Alias for HollowingElement() - exposed under this name too so
    generate.py's optional 'does any character root reach the hollow
    cavity' diagnostic (gated by hasattr(bd, 'HollowSpace')) works for
    Helios the same way it does for Blickensderfer/Postal, even though
    Helios has no core_shaft.scad-family HollowSpace() of its own."""
    return HollowingElement()


# ---------------------------------------------------------------- Element
# See the module docstring's "Two-stage difference" note - _assemble()
# reproduces v2's real nested difference()s: stage-1 cuts (HollowingElement/
# MinkCleanup/IndicatorHole) happen BEFORE AlignmentPinSupport()/
# ClipRetainer() are added, so those bosses are never touched by stage-1's
# cuts, only by the genuine final-stage ones (AlignmentPinHole/
# CenterShaftHole/WireClip - see _final_cut()).

def _assemble(text_ring):
    base = sp.union_all([text_ring, Cylinder()])
    stage1_cut = sp.union_all([HollowingElement(), MinkCleanup(), IndicatorHole()])
    stage1_body = base.difference(stage1_cut, engine="manifold")
    return sp.union_all([stage1_body, AlignmentPinSupport(), ClipRetainer()])


def _final_cut():
    return sp.union_all([AlignmentPinHole(), CenterShaftHole(), WireClip()])


def Additive(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
             draft_angle_deg=None):
    text_ring, char_parts = cylinder_machine.TextRing(
        points_per_mm=points_per_mm, separation_mm=separation_mm, align_kwargs=align_kwargs,
        cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Placement_Protrusion, angle_half_step=Angle_Half_Step)
    return _assemble(text_ring), char_parts


def Subtractive(render_core_groove=None):
    """Not literally what's subtracted in one boolean step in FullElement
    (that's staged - see the module docstring) - unions EVERY negative/
    cutter shape from both stages together, only for generate.py's
    --cut-bodies debug visualization, which just wants to see every
    negative shape at once. render_core_groove: accepted (matching every
    other machine's Subtractive() signature/generate.py's uniform
    build_fn(...) call) but unused - no core groove system at all (see the
    module docstring)."""
    return sp.union_all([HollowingElement(), MinkCleanup(), IndicatorHole(),
                          AlignmentPinHole(), CenterShaftHole(), WireClip()])


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                 cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
                 draft_angle_deg=None):
    _require_configured()
    additive, char_parts = Additive(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                     cone_segments=cone_segments,
                                     simplify_tolerance_mm=simplify_tolerance_mm,
                                     platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                     draft_angle_deg=draft_angle_deg)
    print(f"Additive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    full = additive.difference(_final_cut(), engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="FullElement")
    return full, char_parts


# ---------------------------------------------------------------- Calibration

def CalibrationAdditive(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                         reference_baseline_row=None, reference_cutout_row=None,
                         points_per_mm=None, separation_mm=None, align_kwargs=None,
                         cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                         minkowski_enabled=None, draft_angle_deg=None):
    text_ring, mapping_lines = cylinder_machine.CalibrationTextRing(
        test_char, vary_baseline, vary_cutout, start, interval,
        reference_baseline_row, reference_cutout_row, points_per_mm, separation_mm,
        align_kwargs=align_kwargs, cone_segments=cone_segments,
        simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
        minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Placement_Protrusion, angle_half_step=Angle_Half_Step)
    return _assemble(text_ring), mapping_lines


def CalibrationElement(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                        reference_baseline_row=None, reference_cutout_row=None,
                        points_per_mm=None, separation_mm=None, render_core_groove=None,
                        align_kwargs=None, cone_segments=None, simplify_tolerance_mm=None,
                        platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    additive, mapping_lines = CalibrationAdditive(
        test_char, vary_baseline, vary_cutout, start, interval,
        reference_baseline_row, reference_cutout_row, points_per_mm, separation_mm,
        align_kwargs=align_kwargs, cone_segments=cone_segments,
        simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
        minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg)
    print(f"CalibrationAdditive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    full = additive.difference(_final_cut(), engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="CalibrationElement")
    return full, mapping_lines


# ------------------------------------------------------------- Resin support
# v2 declares Resin_Support/Resin_Support_* parameters but never builds any
# support geometry with them (see the module docstring) - ResinSupport()/
# ResinPrint() are therefore a plain no-op/alias to FullElement(), matching
# that reality rather than inventing a resin-support system that was never
# actually there. Kept as real functions (not simply omitted) so tune.py's
# always-present "Resin supports" checkbox (see tune.py's _compose_build_tab)
# does something sane for Helios instead of crashing with AttributeError.

def ResinSupport():
    return None


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
               draft_angle_deg=None):
    return FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                        cone_segments=cone_segments,
                        simplify_tolerance_mm=simplify_tolerance_mm,
                        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                        draft_angle_deg=draft_angle_deg)
