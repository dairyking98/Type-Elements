"""
v4 full-fidelity Bennett body - ports v2/bennett.scad's Assemble()/
ResinPrint() structure directly, using the SAME origin/orientation
convention as v2 (Z=0 at the bottom face of the main disk, Z+ up through
the top face - Baseline_Z_Offset=0, Bennett's Baseline/Cutout arrays are
already absolute heights from the bottom face, same convention Mignon
uses, unlike Blickensderfer/Postal's negative-from-clip-end convention).

All real-machine numbers live in config/bennett.yaml, not here - call
configure(path) once before using anything else in this module (see
generate.py).

Bennett shares the glyph placement/text pipeline (TextRing/
CalibrationTextRing, place_on_cylinder with placement_protrusion=0 - see
that function's docstring, which already anticipated Bennett by name) and
lib/core_shaft.scad's shared SecondaryCore/CoreGrooves/CoreChamfer/
CoreEllipses (Core_Chamfer_Top=False - no clip, so unlike Blickensderfer/
Postal there's no top chamfer under one; Core_Taper_Top_Z=Core_Top_Z - the
taper's own top landmark coincides with the absolute top, again because
there's no clip pushing it down, matching lib/core_shaft.scad's own
documented default for exactly this case) with cylinder_machine.py.
Unlike Mignon, Bennett does NOT override Angle_Half_Step (v2 never sets
it, so it stays at the shared lib's default 0.5 - verified algebraically:
Bennett's own Theta=-(360/28*col+360/(2*28)) reduces to exactly
(0.5+col)*Latitude_Int, the same formula shape as Blickensderfer/Postal,
just with LATITUDE_INT negative instead of positive - a sign difference,
not a structural one).

Everything else is fully bespoke - confirmed by direct comparison against
v2/bennett.scad: two positioner pins with a small top chamfer
(PositionerPins) instead of a wire clip, a 9-point rotate_extrude()
polygon shaft bore (HollowBody) instead of core_shaft.scad's
HollowSpace()+BottomSlopedSpace() combination, a full 3-row x 28-column
grid of physical alignment/screw holes (AlignmentHoles) with no
Blickensderfer/Postal equivalent at all, two independent flat
whole-string engraved-text groups cut into the bottom face near the shaft
(LabelText - v2 calls text() directly per whole string with
halign=valign="center", not a ring of individually angle-placed
characters like Blickensderfer/Postal's LogoText or Mignon's
ElementLogo/ElementLabel), a simple fixed 8-hole SpeedHoles ring (own
diameter/radius names, no core-groove-family relationship), top+bottom
countersinks and an indicator hole/roof taper (TopCountersink/
BottomCountersink/RoofTaper/IndicatorHole), and fully bespoke
resin-support placement (own ring+groove+raft rotate_extrude, 8+8+4
ResinRod() calls at three different radii/heights - no CutGroove/
SpeedHoleSupport/DrivePinSupport/BottomSupports concepts at all, though it
DOES reuse cylinder_machine._resin_rod() for the rod primitive itself,
same as Mignon - see lib/resin_rod.scad's header comment).

No Shaft Gauge Test (v2/bennett.scad:24 - "Sections with no Bennett
equivalent (Print Tolerances, Shaft Gauge Test) are omitted rather than
left empty" - confirmed, Blickensderfer/Postal-only, same as Mignon).
"""

import numpy as np
import trimesh
import freetype

from glyph_poc import (
    build_flat_text,
    get_glyph_contours_and_advance,
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
    blickensderfer.configure()'s docstring for the general scheme."""
    global _configured
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["FONT_SIZE_MM"] = font["size_mm"]

    label = cfg["label"]
    g["LABEL_FONT_PATH"] = label["font_path"]
    g["Shuttle_Label1a"] = label["label1a"]
    g["Shuttle_Label1b"] = label["label1b"]
    g["Shuttle_Label2"] = label["label2"]
    g["Shuttle_Label_Size"] = label["size_mm"]
    g["Shuttle_Label_Depth"] = label["depth_mm"]

    e = cfg["element"]
    g["z"] = 0.001
    g["Platen_Diameter"] = e["platen_diameter"]
    g["Element_Diameter"] = e["element_diameter"]
    g["Min_Final_Character_Diameter"] = e["min_final_character_diameter"]
    g["Char_Protrusion"] = (e["min_final_character_diameter"] - e["element_diameter"]) / 2.0
    g["Element_Height"] = e["element_height"]
    g["Shaft_Diameter"] = e["shaft_diameter"]
    g["Element_Positioner_Pin_Diameter"] = e["positioner_pin_diameter"]
    g["Element_Positioner_Pin_Radius"] = e["positioner_pin_radius"]
    g["Indicator_Diameter"] = e["indicator_diameter"]
    g["Alignment_Hole_Diameter"] = e["alignment_hole_diameter"]
    g["Alignment_Hole_Depth"] = e["alignment_hole_depth"]
    g["Alignment_Hole_Chamfer"] = e["alignment_hole_chamfer"]
    g["Alignment_Hole"] = e["alignment_hole_height"]
    g["Speed_Hole_Diameter"] = e["speed_hole_diameter"]
    g["Speed_Hole_Radius"] = e["speed_hole_radius"]
    g["Speed_Hole_Quantity"] = e["speed_hole_quantity"]
    g["Countersink_Diameter"] = e["countersink_diameter"]
    g["Top_Countersink_Depth"] = e["top_countersink_depth"]
    g["Bottom_Countersink_Depth"] = e["bottom_countersink_depth"]
    g["Shell_Size"] = e["shell_size"]
    g["Core_Groove_Qty"] = e["core_groove_qty"]
    g["Core_Groove_D"] = e["core_groove_d"]
    g["Core_Chamfer"] = e["core_chamfer"]
    g["Core_Bottom_Offset"] = e["core_bottom_offset"]
    g["Core_Contact_Length"] = e["core_contact_length"]
    g["Core_Web_Width"] = e["core_web_width"]
    g["Core_Web_Qty"] = e["core_web_qty"]
    g["Core_Web_Length"] = e["core_web_length"]
    g["Core_Secondary_ID_Offset"] = e["core_groove_d"] / 2.0 + g["z"]

    # s=.2 - Bennett's own small fudge-factor constant for the core/shaft
    # taper landmarks below (v2/bennett.scad:239, a plain top-level
    # assignment, never a customizer slider - kept as a code literal here
    # too, same treatment as z).
    s = 0.2
    g["Core_Top_Z"] = g["Element_Height"] - g["Top_Countersink_Depth"] - 1 + s
    g["Core_Bottom_Z"] = g["Bottom_Countersink_Depth"]
    # No clip (unlike Blickensderfer/Postal) - the secondary-core taper's
    # own top landmark coincides with the absolute top, lib/core_shaft.
    # scad's documented default for exactly this case (see this module's
    # docstring). Core_Chamfer_Top=False is passed directly as a
    # cylinder_machine.CoreChamfer() call-site kwarg instead (not a
    # global - see Subtractive() below).
    g["Core_Taper_Top_Z"] = g["Core_Top_Z"]

    q = cfg["quality"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Groove_Fn"] = q["groove_fn"]
    g["Alignment_Hole_Fn"] = q["alignment_hole_fn"]
    g["Platen_Fn"] = q.get("platen_fn", GLYPH_DEFAULT_PLATEN_FN)

    layout = cfg["layout"]
    g["BASELINE_ROW"] = layout["baseline_row"]
    g["CUTOUT_ROW"] = layout["cutout_row"]
    # v2/bennett.scad:112 - Latitude_Int=-360/28 - NEGATIVE, same sign
    # convention as Mignon (see this module's docstring for the algebraic
    # verification against Bennett's own Theta formula).
    g["LATITUDE_INT"] = -360.0 / layout["latitude_columns"]
    g["BASELINE_Z_OFFSET"] = 0.0
    g["PLACEMENT_MAP"] = layout["placement_map"]
    # v2/bennett.scad:290-293 - Physical_Layout=[for (row) [for (col)
    # Layout[row][Char_Legend[col]]]] - same keyboard-legend-order storage
    # + Char_Legend content remap scheme config/mignon.yaml's layout.
    # char_legend already uses (see lib/mignon.py's configure() for the
    # full explanation) - applied once here rather than baked into the
    # stored data.
    char_legend = layout.get("char_legend", list(range(layout["latitude_columns"])))
    g["CHAR_LEGEND"] = char_legend
    g["DHIATENSOR"] = [[row[char_legend[c]] for c in range(len(char_legend))] for row in layout["rows"]]

    g["PLATEN_RADIUS_MM"] = 1.0 / g["Platen_Diameter"]

    # v2/bennett.scad:309 - Letter_Placement_Protrusion=0 (placement
    # radius is the raw Element_Diameter/2, not +Char_Protrusion) - same
    # override Mignon/Helios use, threaded through cylinder_machine.
    # place_on_cylinder as an explicit kwarg (see TextRing/
    # CalibrationTextRing calls below). Angle_Half_Step is NOT overridden
    # (v2 never sets it) - every call below omits that kwarg, leaving it
    # at the shared lib's own default (0.5), matching Blickensderfer/
    # Postal's behavior exactly.
    g["Placement_Protrusion"] = 0.0

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
    g["DEFAULT_RENDER_CORE_GROOVE"] = b.get("render_core_groove", True)
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]
    g["DEFAULT_CONE_SEGMENTS"] = q.get("minkowski_fn", GLYPH_DEFAULT_CONE_SEGMENTS)
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM)
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", GLYPH_DEFAULT_MINKOWSKI_ENABLED)
    g["DEFAULT_DRAFT_ANGLE_DEG"] = b.get("draft_angle_deg", GLYPH_DEFAULT_DRAFT_ANGLE_DEG)
    # Generate_Support - Bennett's own name for the same real toggle every
    # other machine calls build.resin_support - also gates RoofTaper()'s
    # cut (v2/bennett.scad:465-469's `if (Generate_Support==true)`), not
    # just whether ResinPrint() itself gets built.
    g["Generate_Support"] = g["DEFAULT_RESIN_SUPPORT"]

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Resin_Support_Wire_Thickness"] = r["rod_od"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Support_Height"] = r["support_height"]
    g["Resin_Support_Thickness"] = r["support_thickness"]
    # Resin_Raft_Thickness=Resin_Support_Thickness, Resin_Min_Rod_Height=
    # -Resin_Raft_Thickness (v2/bennett.scad:363-364) - two derived names
    # for one config value, not independently stored.
    g["Resin_Raft_Thickness"] = r["support_thickness"]
    g["Resin_Min_Rod_Height"] = -g["Resin_Raft_Thickness"]
    # v2/bennett.scad:354 - Resin_Rod_Raft=true (unlike Mignon's false) -
    # Bennett's own ring/raft only reaches the outer edge, so every rod
    # still needs its own small individual raft.
    g["Resin_Rod_Raft"] = True
    g["Resin_Support_Cut_Groove_Diameter"] = r["cut_groove_diameter"]
    g["Resin_Support_Cut_Groove_Thickness"] = r["cut_groove_thickness"]
    g["Pyramidzoffset"] = 1.0 / np.cos(np.arctan(2.0 / g["Countersink_Diameter"]))

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    # Calibration - see blickensderfer.configure()'s matching comment /
    # cylinder_machine.CalibrationTextRing's docstring. Bennett's real
    # Testing_Offsets=[-.65,-.6,...,.7] (28 columns) is exactly
    # testSweepArray(-0.65, 0.05, 28); unlike every other machine, v2's
    # own real Testing_Baseline/Testing_Cutout defaults are BOTH false.
    calibration = cfg.get("calibration", {})
    g["Calibration_Test_Char"] = calibration.get("test_char", "H")
    g["Calibration_Vary_Baseline"] = calibration.get("vary_baseline", False)
    g["Calibration_Vary_Cutout"] = calibration.get("vary_cutout", False)
    g["Calibration_Start"] = calibration.get("start", -0.65)
    g["Calibration_Interval"] = calibration.get("interval", 0.05)

    _configured = True
    cylinder_machine._receive_config(g, "bennett")


def _require_configured():
    if not _configured:
        raise RuntimeError("call bennett.configure(config_path) before using this module")


# ------------------------------------------------------------------- Body

def Cylinder():
    return sp.cylinder_z(Element_Diameter, Element_Height, sections=Surface_Fn)


def PositionerPins():
    """v2/bennett.scad:372-383 - two positioner pins (opposite each other,
    theta=90/270deg) with a small chamfer cone at their base to clean up
    print artifacts that would otherwise drag on the alignment pins."""
    parts = []
    for n in (0, 1):
        theta_deg = 180 * n + 90
        x = Element_Positioner_Pin_Radius * np.cos(np.radians(theta_deg))
        y = Element_Positioner_Pin_Radius * np.sin(np.radians(theta_deg))
        pin = sp.cylinder_z(Element_Positioner_Pin_Diameter, Element_Height + 2 * z, sections=Cyl_Fn)
        chamfer = sp.frustum_z(Element_Positioner_Pin_Diameter, Element_Positioner_Pin_Diameter + 1, 2,
                                sections=Cyl_Fn, base_z=Bottom_Countersink_Depth + Shell_Size)
        group = sp.union_all([pin, chamfer])
        parts.append(sp.translate(group, [x, y, -z]))
    return sp.union_all(parts)


def HollowBody():
    """v2/bennett.scad:386-395 - a 9-point rotate_extrude() polygon shaft
    bore, built from two small landmark arrays (XArray/YArray) and an
    index pattern (XYPattern) rather than a literal point list - ported
    mechanically (same arrays/pattern), not hand-simplified. Asd/Drop are
    Bennett's own unexposed plain top-level constants (v2/bennett.scad:
    384-385, never customizer sliders), kept as code literals here, same
    treatment as s/z."""
    Asd = 1.0
    Drop = 0.5
    roof_slope = 1.0 / (Countersink_Diameter / 2.0)
    x_array = [
        Shaft_Diameter / 2 + Shell_Size + Core_Secondary_ID_Offset,
        Shaft_Diameter / 2 + Shell_Size + Core_Secondary_ID_Offset + Asd,
        ((Element_Diameter / 2 - Shell_Size) + (Shaft_Diameter / 2 + Shell_Size + Core_Secondary_ID_Offset)) / 2,
        Element_Diameter / 2 - Shell_Size - Asd,
        Element_Diameter / 2 - Shell_Size,
    ]
    y_array = [
        Bottom_Countersink_Depth + Shell_Size,
        Bottom_Countersink_Depth + Shell_Size + Drop,
        Bottom_Countersink_Depth + Shell_Size + Drop + Asd,
        Element_Height - Top_Countersink_Depth - Shell_Size - Asd,
        Element_Height - Top_Countersink_Depth - Shell_Size,
        Element_Height - Top_Countersink_Depth - Shell_Size - Asd - roof_slope * (Countersink_Diameter / 2 - x_array[0]),
        Element_Height - Top_Countersink_Depth - Shell_Size - roof_slope * (Countersink_Diameter / 2 - x_array[0]),
    ]
    xy_pattern = [(0, 2), (0, 5), (1, 6), (3, 4), (4, 3), (4, 2), (3, 1), (2, 0), (1, 1)]
    profile = [(x_array[xi], y_array[yi]) for xi, yi in xy_pattern]
    return sp.revolve_polygon(profile, sections=Surface_Fn)


def AlignmentHoles():
    """v2/bennett.scad:397-416 - a full 3-row x 28-column grid of physical
    alignment/screw holes (no Blickensderfer/Postal equivalent at all),
    each a straight bore + a hull()-chamfer at the outer face + a small
    sphere at the inner end. theta uses the SAME (0.5+col)*Latitude_Int
    formula place_on_cylinder uses (verified algebraically - see this
    module's docstring), over every physical column regardless of which
    character (if any) is assigned there."""
    parts = []
    n_rows = len(DHIATENSOR)
    n_cols = len(PLACEMENT_MAP)
    scale_y = (Alignment_Hole_Diameter + 2 * Alignment_Hole_Chamfer) / Alignment_Hole_Diameter
    for row in range(n_rows):
        for n in range(n_cols):
            theta_deg = (0.5 + n) * LATITUDE_INT
            ca, sa = np.cos(np.radians(theta_deg)), np.sin(np.radians(theta_deg))

            hole = sp.cylinder_z(Alignment_Hole_Diameter, Alignment_Hole_Depth - Alignment_Hole_Diameter / 2,
                                  sections=Alignment_Hole_Fn)
            disk_a = sp.cylinder_z(Alignment_Hole_Diameter, z, sections=Alignment_Hole_Fn,
                                    base_z=Alignment_Hole_Chamfer)
            disk_b = sp.cylinder_z(Alignment_Hole_Diameter, 1.0, sections=Alignment_Hole_Fn, base_z=-1.0)
            disk_b.vertices[:, 1] *= scale_y
            chamfer_hull = trimesh.util.concatenate([disk_a, disk_b]).convex_hull
            group = sp.union_all([hole, chamfer_hull])
            group = sp.scad_transform(
                group,
                ("translate", [Element_Diameter / 2 * ca, Element_Diameter / 2 * sa, Alignment_Hole[row]]),
                ("rotate", [0, -90, theta_deg]),
            )
            parts.append(group)

            ball_r = Element_Diameter / 2 - Alignment_Hole_Depth + Alignment_Hole_Diameter / 2
            ball = trimesh.creation.icosphere(subdivisions=2, radius=Alignment_Hole_Diameter / 2)
            ball = sp.translate(ball, [ball_r * ca, ball_r * sa, Alignment_Hole[row]])
            parts.append(ball)
    return sp.union_all(parts)


def _build_text_string(text, size, font_path, depth, points_per_mm=20.0):
    """v2's text(text=<whole string>, halign="center", valign="center") -
    ported as build_flat_text() called per character at its natural
    FreeType pen-origin advance (no align_kwargs), summed left to right,
    then the WHOLE assembled string shifted by -total_advance/2 - the same
    "native halign=center centers the ADVANCE box" convention already
    verified/established elsewhere in this codebase (see lib/
    glyph_pipeline.scad's AlignedText comment). Vertically, stays at
    baseline (y=0) rather than attempting true valign=center - the same
    simplification cylinder_machine.LogoText()/mignon.ElementLabel()
    already make for their own decorative text (see those functions'
    docstrings) - fine for an engraved label, not attempted to match
    exactly."""
    fp = font_path
    face = freetype.Face(fp)
    scale = size / face.units_per_EM
    parts = []
    cursor = 0.0
    for ch in text:
        _, advance_mm = get_glyph_contours_and_advance(ch, points_per_mm, scale, font_path=fp)
        if ch != " ":
            mesh = build_flat_text(ch, points_per_mm, depth, font_size_mm=size, font_path=fp)
            parts.append(sp.translate(mesh, [cursor, 0, 0]))
        cursor += advance_mm
    whole = sp.union_all(parts)
    return sp.translate(whole, [-cursor / 2.0, 0, 0])


def LabelText(points_per_mm=20.0):
    """v2/bennett.scad:418-432 - two independent flat engraved-text groups
    cut into the bottom face near the shaft (SUBTRACTED in Assemble(), not
    additive like every other machine's decorative text - Bennett has no
    ring-wrapped/chamfer-mounted text at all). Right group: Shuttle_
    Label1b at local y=0, Shuttle_Label1a at local y=2.25 (two-line
    "Chau"/"Leonard" stack, matching v2's own linear_extrude(){text();
    translate([0,2.25,0])text();} nesting exactly). Left group: Shuttle_
    Label2 alone. The 2mm extrude depth is a literal in v2 (never a
    customizer slider), kept as a code literal here too."""
    right_1b = _build_text_string(Shuttle_Label1b, Shuttle_Label_Size, LABEL_FONT_PATH, 2.0, points_per_mm)
    right_1a = sp.translate(
        _build_text_string(Shuttle_Label1a, Shuttle_Label_Size, LABEL_FONT_PATH, 2.0, points_per_mm),
        [0, 2.25, 0])
    right = sp.union_all([right_1b, right_1a])
    right = sp.scad_transform(
        right,
        ("translate", [Shaft_Diameter / 2 + 1.5 + 0.25, 0, Bottom_Countersink_Depth + Shuttle_Label_Depth]),
        ("rotate", [180, 0, 90]),
    )
    left = _build_text_string(Shuttle_Label2, Shuttle_Label_Size, LABEL_FONT_PATH, 2.0, points_per_mm)
    left = sp.scad_transform(
        left,
        ("translate", [-Shaft_Diameter / 2 - 1.75 - 0.5, 0, Bottom_Countersink_Depth + Shuttle_Label_Depth]),
        ("rotate", [180, 0, 90]),
    )
    return sp.union_all([right, left])


def SpeedHoles():
    parts = []
    for n in range(Speed_Hole_Quantity):
        # v2/bennett.scad:437 - theta=360/Qty*n+360/(Qty*2) - a half-step
        # phase offset (22.5deg at the real Qty=8), unlike cylinder_
        # machine.SpeedHoles' un-offset 360/Qty*n.
        theta_deg = 360.0 / Speed_Hole_Quantity * n + 360.0 / (Speed_Hole_Quantity * 2)
        h = sp.cylinder_z(Speed_Hole_Diameter, Element_Height + 2 * z, sections=Surface_Fn, base_z=-z)
        h = sp.translate(h, [Speed_Hole_Radius * np.cos(np.radians(theta_deg)),
                              Speed_Hole_Radius * np.sin(np.radians(theta_deg)), 0])
        parts.append(h)
    return sp.union_all(parts)


def MinkCleanup():
    top = sp.translate(sp.cylinder_z(Element_Diameter + 5, 5, sections=20), [0, 0, Element_Height])
    bottom = sp.cylinder_z(Element_Diameter + 5, 5, sections=20, base_z=-5)
    return sp.union_all([top, bottom])


def CenterShaft():
    return sp.cylinder_z(Shaft_Diameter, Element_Height + 2 * z, sections=Cyl_Fn, base_z=-z)


def TopCountersink():
    return sp.cylinder_z(Countersink_Diameter, Top_Countersink_Depth + z, sections=Surface_Fn,
                          base_z=Element_Height - Top_Countersink_Depth)


def BottomCountersink():
    return sp.cylinder_z(Countersink_Diameter, Bottom_Countersink_Depth + z, sections=Surface_Fn, base_z=-z)


def RoofTaper():
    """v2/bennett.scad:465-469 - only cut when Generate_Support is on
    (gates the resin-support roof-contact taper prep, independent of
    whether THIS particular build actually calls ResinPrint())."""
    if not Generate_Support:
        return None
    return sp.frustum_z(0.0, Countersink_Diameter, 1 + z, sections=Surface_Fn,
                         base_z=Element_Height - Top_Countersink_Depth - 1)


def IndicatorHole():
    return sp.translate(
        sp.cylinder_z(Indicator_Diameter, 5, sections=Surface_Fn),
        [Element_Diameter / 2 - Shell_Size - Indicator_Diameter / 2, 0,
         Element_Height - Top_Countersink_Depth - Shell_Size - z - 1])


# ---------------------------------------------------------------- Element

def Additive(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
             draft_angle_deg=None):
    text_ring, char_parts = cylinder_machine.TextRing(
        points_per_mm=points_per_mm, separation_mm=separation_mm, align_kwargs=align_kwargs,
        cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Placement_Protrusion)
    return sp.union_all([text_ring, Cylinder()]), char_parts


def _subtractive_parts(render_core_groove):
    parts = [
        PositionerPins(),
        HollowBody(),
        AlignmentHoles(),
        LabelText(),
        SpeedHoles(),
        MinkCleanup(),
        CenterShaft(),
        TopCountersink(),
        BottomCountersink(),
        IndicatorHole(),
        cylinder_machine.SecondaryCore(0),
        cylinder_machine.CoreChamfer(0, chamfer_top=False),
        cylinder_machine.CoreEllipses(),
    ]
    roof = RoofTaper()
    if roof is not None:
        parts.append(roof)
    if render_core_groove:
        parts.append(cylinder_machine.CoreGrooves(0))
    return parts


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                 cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
                 draft_angle_deg=None):
    _require_configured()
    render_core_groove = DEFAULT_RENDER_CORE_GROOVE if render_core_groove is None else render_core_groove
    additive, char_parts = Additive(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                     cone_segments=cone_segments,
                                     simplify_tolerance_mm=simplify_tolerance_mm,
                                     platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                     draft_angle_deg=draft_angle_deg)
    print(f"Additive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    subtractive = sp.union_all(_subtractive_parts(render_core_groove))
    print(f"Subtractive (unioned): verts={len(subtractive.vertices)} faces={len(subtractive.faces)} "
          f"watertight={subtractive.is_watertight}", flush=True)
    full = additive.difference(subtractive, engine="manifold")
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
        placement_protrusion=Placement_Protrusion)
    return sp.union_all([text_ring, Cylinder()]), mapping_lines


def CalibrationElement(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                        reference_baseline_row=None, reference_cutout_row=None,
                        points_per_mm=None, separation_mm=None, render_core_groove=None,
                        align_kwargs=None, cone_segments=None, simplify_tolerance_mm=None,
                        platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    render_core_groove = DEFAULT_RENDER_CORE_GROOVE if render_core_groove is None else render_core_groove
    additive, mapping_lines = CalibrationAdditive(
        test_char, vary_baseline, vary_cutout, start, interval,
        reference_baseline_row, reference_cutout_row, points_per_mm, separation_mm,
        align_kwargs=align_kwargs, cone_segments=cone_segments,
        simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
        minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg)
    print(f"CalibrationAdditive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    subtractive = sp.union_all(_subtractive_parts(render_core_groove))
    print(f"Subtractive (unioned): verts={len(subtractive.vertices)} faces={len(subtractive.faces)} "
          f"watertight={subtractive.is_watertight}", flush=True)
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="CalibrationElement")
    return full, mapping_lines


# ------------------------------------------------------------- Resin support

def ResinSupport():
    """v2/bennett.scad:477-514 - entirely bespoke: its own ring (with a
    snap-groove cut) + flat raft flange (both rotate_extrude()s, not the
    shared CutGroove), then 8 ResinRod() calls at the countersink radius
    (straight, full support height), 8 more at Countersink_Diameter/3
    (alternating with the first ring, tall enough to reach RoofTaper()'s
    sloped underside at that radius), and 4 more near the shaft (same
    roof-contact formula at a smaller radius) - no speed-hole/drive-pin/
    bottom-sloped-space support concepts at all. Reuses cylinder_machine.
    _resin_rod() for the rod primitive itself (Resin_Rod_Raft=True, so
    each rod ALSO grows its own small raft - see configure()'s comment)."""
    _require_configured()
    ring_outer = sp.translate(sp.cylinder_z(Element_Diameter, Resin_Support_Height - 0.5, sections=Surface_Fn),
                               [0, 0, 0.5])
    ring_inner_d = 2 * (Element_Diameter / 2 - Resin_Support_Cut_Groove_Diameter / 2
                         - Resin_Support_Cut_Groove_Thickness)
    ring_inner = sp.cylinder_z(ring_inner_d, Resin_Support_Height + 2 * z, sections=Surface_Fn, base_z=-z)
    groove_r = Resin_Support_Cut_Groove_Diameter / 2
    theta_c = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    groove_profile = np.column_stack([
        Element_Diameter / 2 + groove_r * np.cos(theta_c),
        Resin_Support_Height - Resin_Support_Cut_Groove_Diameter / 2 + groove_r * np.sin(theta_c),
    ])
    groove = sp.revolve_polygon(groove_profile, sections=Surface_Fn)
    ring = ring_outer.difference(ring_inner, engine="manifold").difference(groove, engine="manifold")

    raft_profile = [
        (Element_Diameter / 2, 0),
        (Element_Diameter / 2 - Resin_Support_Thickness, 0),
        (Element_Diameter / 2 - Resin_Support_Thickness, Resin_Support_Thickness),
        (Element_Diameter / 2 + Resin_Support_Thickness, Resin_Support_Thickness),
    ]
    raft = sp.revolve_polygon(raft_profile, sections=Resin_Fn)

    parts = [ring, raft]
    for n in range(8):
        theta_deg = 360.0 / 8 * n
        ca, sa = np.cos(np.radians(theta_deg)), np.sin(np.radians(theta_deg))
        r1 = (Countersink_Diameter + Resin_Support_Wire_Thickness) / 2.0
        parts.append(sp.translate(cylinder_machine._resin_rod(Resin_Support_Height), [r1 * ca, r1 * sa, 0]))
        r2 = Countersink_Diameter / 3.0
        h2 = (Resin_Support_Height + Pyramidzoffset + Top_Countersink_Depth
              - (2.0 / Countersink_Diameter) * (Countersink_Diameter / 3.0))
        parts.append(sp.translate(cylinder_machine._resin_rod(h2), [r2 * ca, r2 * sa, 0]))
    for n in range(4):
        theta_deg = 90.0 * n
        ca, sa = np.cos(np.radians(theta_deg)), np.sin(np.radians(theta_deg))
        r3 = Shaft_Diameter / 2.0 + 1.0
        h3 = (Resin_Support_Height + Pyramidzoffset + Top_Countersink_Depth
              - (2.0 / Countersink_Diameter) * (Shaft_Diameter / 2.0 + 1.0))
        parts.append(sp.translate(cylinder_machine._resin_rod(h3), [r3 * ca, r3 * sa, 0]))

    whole = sp.union_all(parts)
    return sp.translate(whole, [0, 0, -Resin_Support_Height + z])


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
               draft_angle_deg=None):
    """v2/bennett.scad:544-551 - same upside-down flip Mignon's ResinPrint
    uses (translate([0,0,Element_Height]) rotate([0,180,0]) before adding
    supports) - the bottom face (where LabelText()/ResinSupport() live)
    ends up facing the build plate."""
    full, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                    cone_segments=cone_segments,
                                    simplify_tolerance_mm=simplify_tolerance_mm,
                                    platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                    draft_angle_deg=draft_angle_deg)
    flipped = sp.scad_transform(full, ("translate", [0, 0, Element_Height]), ("rotate", [0, 180, 0]))
    support = ResinSupport()
    print(f"ResinSupport: verts={len(support.vertices)} faces={len(support.faces)} "
          f"watertight={support.is_watertight}", flush=True)
    combined = sp.union_all([flipped, support])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts
