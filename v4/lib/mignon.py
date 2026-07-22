"""
v4 full-fidelity Mignon body - ports v2/mignon.scad's Assemble()/
ResinPrint() structure directly, using the SAME origin/orientation
convention as v2 (Z=0 at the bottom face of the main body, Z+ up through
the top/label end).

All real-machine numbers live in config/mignon.yaml, not here - call
configure(path) once before using anything else in this module (see
generate.py).

Unlike Blickensderfer/Postal (which diverge only in the "drive pin trio"),
Mignon diverges from cylinder_machine.py across essentially the whole
body-construction half of the pipeline - confirmed by direct comparison
against v2/mignon.scad: no Core/ClipCylinder/WireBite/SpeedHoles/
core_shaft.scad-family at all (v2/mignon.scad:293-296, its shaft bore is
a plain rotate_extrude() polygon), a 12-sided polygon main body instead
of a round cylinder (PolygonCylinder, Cylinder_Shape=0 default), a
stepped-boss+chamfer top feature instead of a wire-clip (ElementChamfer),
a plain cut-through alignment keyway instead of a countersunk drive pin
(AlignmentPin), top+bottom Minkowski cleanup instead of top-only
(MinkCleanup), and fully bespoke resin-support placement (no
CutGroove/SpeedHoleSupport/DrivePinSupport/BottomSupports - a raft ring
+ 12+6 ResinRod() calls at two radii, ResinSupport() below). Only the
glyph placement/text pipeline (TextRing, reused directly with
placement_protrusion=0/angle_half_step=0 - see cylinder_machine.
place_on_cylinder's docstring) and the Calibration mechanism
(CalibrationTextRing, reused directly the same way) are genuinely
shared/reusable as-is.

Mignon has 7 physical rows (not 3) and 12 columns (not 28) -
cylinder_machine.TextRing/CalibrationTextRing were made row-count-
agnostic (range(len(DHIATENSOR)) instead of a hardcoded (0,1,2)) to
support this; Blickensderfer/Postal are unaffected since their 3-row
configs reduce to the exact same loop.

No Shaft Gauge Test (v2/mignon.scad:30: "Print Tolerances, Shaft Gauge
Test... omitted" - confirmed, Blickensderfer/Postal-only)."""

import numpy as np
import trimesh

from glyph_poc import (
    build_flat_text,
    build_flat_text_drafted,
    DEFAULT_CONE_SEGMENTS as GLYPH_DEFAULT_CONE_SEGMENTS,
    DEFAULT_SIMPLIFY_TOLERANCE_MM as GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM,
    DEFAULT_PLATEN_FN as GLYPH_DEFAULT_PLATEN_FN,
    DEFAULT_MINKOWSKI_ENABLED as GLYPH_DEFAULT_MINKOWSKI_ENABLED,
    DEFAULT_DRAFT_ANGLE_DEG as GLYPH_DEFAULT_DRAFT_ANGLE_DEG,
)
import scad_primitives as sp
import cylinder_machine
import build_log

_configured = False


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - see
    blickensderfer.configure()'s docstring for the general scheme.
    Mignon's element: section is shaped very differently from
    Blickensderfer/Postal's (no wall/chamfer/speed-hole/core-groove/
    clip/drive-pin keys at all - see the module docstring for why)."""
    global _configured
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["FONT_SIZE_MM"] = font["size_mm"]

    logo = cfg["logo"]
    g["LOGO_FONT_PATH"] = logo["font_path"]
    g["Logo_Text"] = logo["text"]
    g["Logo_Text_Size"] = logo["text_size_mm"]
    g["Logo_Text_Spacing"] = logo["text_spacing"]
    g["Logo_Position_Offset"] = logo["position_offset_deg"]
    # Cylinder_Label_Height_Offset - the local radial nudge off the chamfer
    # surface (ElementLogo's own transform, unrelated to Blickensderfer/
    # Postal's Logo_Radial_Offset - Mignon's logo/label sit on an angled
    # chamfer surface, not the flat top face, so their geometry needs a
    # different placement chain entirely, see _render_engraved_text()).
    g["Logo_Height_Offset"] = logo["height_offset_mm"]
    # v4-only, not a v2 field - v2's ElementLabel() hardcodes .09. Exposed
    # because height_offset_mm ALONE can't reliably clear the chamfer's
    # curvature: it's a CURVED surface and the text is a FLAT panel resting
    # tangent to it, so a thin extrusion only exposes a razor sliver near
    # the tangent point (confirmed visually: v2's real 0.09mm at the old
    # 0.5mm offset default left ~50% of each character embedded/invisible,
    # only its silhouette edge grazing the surface). A deeper extrusion
    # spans from solidly-embedded (anchored, printable) to solidly-exposed
    # (visible) at a modest offset, instead of needing a huge offset that
    # detaches the text into a floating, unattached island.
    g["Logo_Text_Depth"] = logo.get("text_depth_mm", 0.3)
    # v4-only - v2 has no toggle here at all, LetterText()'s small sphere-
    # minkowski rounding is unconditional there (gated only by the global
    # Mink_On preview flag). One checkbox covers both Logo and Label - see
    # _render_engraved_text()'s docstring.
    g["Minkowski_Text"] = logo.get("minkowski_text", False)

    # Label: NOT a v2 concept (v2/mignon.scad has exactly one engraved-text
    # feature, Cylinder_Label, which is what Logo_* above already is - see
    # ElementLogo()'s docstring) - a v4-only second engraved-text feature,
    # same rendering chain as Logo, always placed 180 degrees around from
    # it (Label_Position_Offset is DERIVED, not stored - "180 degrees
    # opposite from Logo text" is an invariant, not just an initial value).
    # label_* keys (not font_path/text/... like logo above) - config's own
    # comment explains why: tune.py's patch_yaml_value matches by bare key
    # text across the whole file, so identical key names under logo:/
    # label: would collide.
    label = cfg["label"]
    g["LABEL_FONT_PATH"] = label["label_font_path"]
    g["Label_Text"] = label["label_text"]
    g["Label_Text_Size"] = label["label_text_size_mm"]
    g["Label_Text_Spacing"] = label["label_text_spacing"]
    g["Label_Height_Offset"] = label["label_height_offset_mm"]
    g["Label_Text_Depth"] = label.get("label_text_depth_mm", 0.3)
    g["Label_Position_Offset"] = logo["position_offset_deg"] + 180.0

    e = cfg["element"]
    g["z"] = 0.001
    g["Element_Diameter"] = e["element_diameter"]
    g["Platen_Diameter"] = e["platen_diameter"]
    g["Min_Final_Character_Diameter"] = e["min_final_character_diameter"]
    g["Char_Protrusion"] = (e["min_final_character_diameter"] - e["element_diameter"]) / 2.0
    # v2/mignon.scad:109-115,197 - Tallen (Plakatschrift, a display-type
    # variant): Element_Height=Cylinder_Height_+Height_Increase when on
    # (element_height below is Cylinder_Height_, the base/untallened
    # value), and every Baseline row shifts by Tallen_Baseline_Offset -
    # Cutout is NOT affected (v2 has no Cutout_Tallen variant, confirmed
    # by its absence from the source - a real asymmetry, not an omission).
    # Previously not ported at all (element_height stored the untallened
    # value directly, no toggle) - now a real, off-by-default option.
    g["Tallen"] = e.get("tallen", False)
    g["Height_Increase"] = e.get("height_increase_mm", 3.0)
    g["Tallen_Baseline_Offset"] = e.get("tallen_baseline_offset_mm", -1.25)
    g["Element_Height"] = e["element_height"] + (g["Height_Increase"] if g["Tallen"] else 0.0)
    g["Cylinder_Top_Height_Offset"] = e["cylinder_top_height_offset"]
    g["Cylinder_Top_Chamfer"] = e["cylinder_top_chamfer"]
    g["Cylinder_Top_Diameter"] = e["cylinder_top_diameter"]
    g["Cylinder_Top_Shaft_Diameter"] = e["cylinder_top_shaft_diameter"]
    g["Cylinder_Bottom_Shaft_Diameter"] = e["cylinder_bottom_shaft_diameter"]
    g["Pin_Height"] = e["pin_height"]
    g["Pin_Width"] = e["pin_width"]
    g["Pin_Depth"] = e["pin_depth"]
    g["Pin_Through"] = e["pin_through"]
    g["Cylinder_Shape"] = e.get("cylinder_shape", 0)

    q = cfg["quality"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Resin_Fn"] = q["resin_fn"]
    g["Platen_Fn"] = q.get("platen_fn", GLYPH_DEFAULT_PLATEN_FN)

    layout = cfg["layout"]
    g["BASELINE_ROW"] = ([b + g["Tallen_Baseline_Offset"] for b in layout["baseline_row"]]
                          if g["Tallen"] else layout["baseline_row"])
    g["CUTOUT_ROW"] = layout["cutout_row"]
    # v2/mignon.scad:120 - Latitude_Int=-360/len(Layout[0]) - NEGATIVE,
    # unlike Blickensderfer/Postal's positive 360/columns. Columns wrap
    # the opposite rotational direction - not just a different magnitude,
    # a real sign difference, confirmed directly from source.
    g["LATITUDE_INT"] = -360.0 / layout["latitude_columns"]
    # v2/mignon.scad:281 - Baseline_Z_Offset=0 (Baseline/Cutout are already
    # absolute heights from the bottom face, unlike Blickensderfer/Postal's
    # negative-from-clip-end convention - see cylinder_machine.
    # place_on_cylinder's docstring for what this shifts).
    g["BASELINE_Z_OFFSET"] = 0.0
    g["PLACEMENT_MAP"] = layout["placement_map"]
    # v2/mignon.scad:88,275 - Char_Legend=[7,8,9,10,11,0,1,2,3,4,5,6],
    # Physical_Layout=[for (row) [for (col) Layout[row][Char_Legend[col]]]].
    # layout.rows (config, and tune.py's LAYOUT_PRESETS_MIGNON) is stored in
    # RAW KEYBOARD-LEGEND order (v2's `Layout` - what's printed on the
    # physical keyboard/manual), so it can be typed/read the way a person
    # actually reads the legend; DHIATENSOR needs the Char_Legend-remapped
    # PHYSICAL order (what TextRing/place_on_cylinder actually place by
    # column index) - this is that remap, applied once here rather than
    # baked into the stored data, so editing the legend never requires
    # re-deriving the physical order by hand.
    char_legend = layout.get("char_legend", list(range(layout["latitude_columns"])))
    g["CHAR_LEGEND"] = char_legend
    g["DHIATENSOR"] = [[row[char_legend[c]] for c in range(len(char_legend))] for row in layout["rows"]]

    g["PLATEN_RADIUS_MM"] = 1.0 / g["Platen_Diameter"]

    # v2/mignon.scad:118-121 - Letter_Placement_Protrusion=0 (placement
    # radius is the raw Element_Diameter/2, not +Char_Protrusion) and
    # Angle_Half_Step=0 (no half-column centering term) - both threaded
    # through cylinder_machine.place_on_cylinder as explicit overrides
    # (None everywhere else preserves Blickensderfer/Postal's original
    # hardcoded behavior).
    g["Placement_Protrusion"] = 0.0
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

    r = cfg["resin"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Min_Rod_Height"] = r["min_rod_height"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Raft_Thickness"] = r["raft_thickness"]
    # Mignon builds its own raft ring directly in ResinSupport() (like
    # Bennett) - the shared _resin_rod() primitive's per-rod raft stays
    # off unconditionally (v2/mignon.scad:311, no config toggle - unlike
    # Blickensderfer/Postal's resin.raft, there's no "continuous plate"
    # concept here to toggle between, just always-off).
    g["Resin_Rod_Raft"] = False
    g["Resin_Support_Height"] = r["support_height"]
    g["Resin_Support_Thickness"] = r["support_thickness"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    # Calibration - see blickensderfer.configure()'s matching comment /
    # cylinder_machine.CalibrationTextRing's docstring. Mignon's own v2
    # defaults (Testing_Offsets=[-.5,-.4,...,.6], 12 columns) are exactly
    # testSweepArray(-0.5, 0.1, 12) - expressed here as start/interval,
    # same as every other machine's calibration.* fields.
    calibration = cfg.get("calibration", {})
    g["Calibration_Test_Char"] = calibration.get("test_char", "H")
    g["Calibration_Vary_Baseline"] = calibration.get("vary_baseline", False)
    g["Calibration_Vary_Cutout"] = calibration.get("vary_cutout", True)
    g["Calibration_Start"] = calibration.get("start", -0.5)
    g["Calibration_Interval"] = calibration.get("interval", 0.1)

    _configured = True
    cylinder_machine._receive_config(g, "mignon")


def _require_configured():
    if not _configured:
        raise RuntimeError("call mignon.configure(config_path) before using this module")


# ------------------------------------------------------------------- Body

def _regular_polygon_points(order, diameter):
    theta = np.linspace(0, 2 * np.pi, order, endpoint=False)
    r = diameter / 2.0
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])


def PolygonCylinder():
    """v2/mignon.scad:325-331 - the default (Cylinder_Shape=0) main body:
    a 12-sided polygon prism, not a round cylinder. rotate([0,0,360/24])
    is applied to the 2D polygon before extrusion (centers a flat facet
    on the +X axis instead of a vertex)."""
    from shapely.geometry import Polygon as ShapelyPolygon
    pts = _regular_polygon_points(12, Element_Diameter)
    angle = np.radians(360.0 / 24)
    ca, sa = np.cos(angle), np.sin(angle)
    rotated = np.stack([pts[:, 0] * ca - pts[:, 1] * sa, pts[:, 0] * sa + pts[:, 1] * ca], axis=1)
    shape = trimesh.creation.extrude_polygon(ShapelyPolygon(rotated), Element_Height + 6)
    return sp.translate(shape, [0, 0, -1])


def ElementChamfer():
    """v2/mignon.scad:333-339 - a stepped cylindrical boss (Cylinder_Top_
    Diameter) with a flared frustum chamfer at its base, both starting at
    the SAME base_z (siblings inside one translate() scope in the source,
    not stacked - their union is the intended shape: the frustum flares
    the boss's base outward, the straight cylinder continues the boss up
    to full height)."""
    base_z = Element_Height - Cylinder_Top_Height_Offset - z
    top = sp.cylinder_z(Cylinder_Top_Diameter, Cylinder_Top_Height_Offset + z,
                         sections=Surface_Fn, base_z=base_z)
    frustum = sp.frustum_z(Cylinder_Top_Diameter + Cylinder_Top_Chamfer * 2, Cylinder_Top_Diameter,
                            Cylinder_Top_Chamfer, sections=Surface_Fn, base_z=base_z)
    return sp.union_all([top, frustum])


def _render_engraved_text(text, text_size, text_spacing, position_offset, height_offset,
                           font_path, text_depth, points_per_mm=20.0):
    """Shared placement chain for ElementLogo()/ElementLabel() - v2/
    mignon.scad:341-355's ElementLabel(), placed on ElementChamfer()'s
    angled chamfer surface (rotate([45,0,90])), not flat on the top face
    like Blickensderfer/Postal's LogoText() - a genuinely different
    placement chain, not just different parameter values (see the module
    docstring).

    text_depth: v2 hardcodes this at .09 (paired with its own small
    sphere-minkowski edge-rounding, LetterText()'s r=.05 - not the big
    draft-cone taper struck characters get). At that thin default it's
    nearly invisible here: the chamfer is a CURVED frustum and the text is
    a rigid FLAT panel resting tangent to it at one point, so a thin
    extrusion only clears the surface right at that tangent point - the
    rest of each character's own footprint dips back under the curve and
    stays embedded/invisible, only its silhouette edge grazing through as
    a sliver (confirmed visually). A deeper extrusion (config default
    0.3mm - see configure()'s Logo_Text_Depth/Label_Text_Depth comment)
    spans from solidly-embedded (anchored into the body, printable) to
    solidly-exposed (visible) using a modest height_offset, instead of
    needing a height_offset big enough to clear the WHOLE curve on its
    own, which detaches the text into an unattached floating island long
    before that happens.

    Minkowski_Text (logo.minkowski_text, one checkbox covering both Logo
    and Label - v4-only) opts into a real draft-cone taper via
    build_flat_text_drafted() instead of a plain flat extrude - the SAME
    mechanism/DEFAULT_DRAFT_ANGLE_DEG struck characters use, not v2's
    separate small-sphere rounding."""
    n_chars = len(text)
    parts = []
    for n, ch in enumerate(text):
        if ch == " ":
            continue
        if Minkowski_Text:
            mesh = build_flat_text_drafted(ch, points_per_mm, text_depth, font_size_mm=text_size,
                                            font_path=font_path, draft_angle_deg=DEFAULT_DRAFT_ANGLE_DEG,
                                            cone_segments=DEFAULT_CONE_SEGMENTS,
                                            simplify_tolerance_mm=DEFAULT_SIMPLIFY_TOLERANCE_MM)
        else:
            mesh = build_flat_text(ch, points_per_mm, text_depth, font_size_mm=text_size,
                                    font_path=font_path)
        center_x = (mesh.bounds[0][0] + mesh.bounds[1][0]) / 2.0
        mesh.apply_translation([-center_x, 0, 0])
        angle_n = text_spacing * n + position_offset - (n_chars - 1) * text_spacing / 2
        placed = sp.scad_transform(
            mesh,
            ("rotate", [0, 0, angle_n]),
            ("translate", [Cylinder_Top_Diameter / 2 + Cylinder_Top_Chamfer, 0,
                            Element_Height - Cylinder_Top_Height_Offset]),
            ("rotate", [45, 0, 90]),
            ("translate", [0, height_offset, -0.05]),
        )
        parts.append(placed)
    return sp.union_all(parts)


def ElementLogo(points_per_mm=20.0):
    """v2/mignon.scad's actual (only) engraved-text feature - v2 calls
    this "Cylinder_Label" internally, but it's what Blickensderfer/
    Postal's config schema and this app's UI call "Logo" (logo.* config
    keys) for schema-reuse convenience - see configure()'s docstring."""
    return _render_engraved_text(Logo_Text, Logo_Text_Size, Logo_Text_Spacing,
                                  Logo_Position_Offset, Logo_Height_Offset,
                                  LOGO_FONT_PATH, Logo_Text_Depth, points_per_mm)


def ElementLabel(points_per_mm=20.0):
    """v4-only second engraved-text feature (NOT a v2 concept - see
    configure()'s docstring) - same placement chain as ElementLogo(),
    always 180 degrees opposite it (Label_Position_Offset is derived from
    Logo_Position_Offset, not independently stored)."""
    return _render_engraved_text(Label_Text, Label_Text_Size, Label_Text_Spacing,
                                  Label_Position_Offset, Label_Height_Offset,
                                  LABEL_FONT_PATH, Label_Text_Depth, points_per_mm)


def MinkCleanup():
    """v2/mignon.scad:407-412 - cleans up BOTH the top (Minkowski overrun
    above the element) AND the bottom (below z=0) - unlike Blickensderfer/
    Postal's TopMinkCleanup(), which only handles the top (they have no
    Minkowski overrun risk at the bottom, since their characters don't
    extend past z=0 the way Mignon's do at this stage of Assemble())."""
    top = sp.translate(sp.cylinder_z(30, 10, sections=Surface_Fn),
                        [0, 0, Element_Height - Cylinder_Top_Height_Offset])
    bottom = sp.cylinder_z(30, 10, sections=Surface_Fn, base_z=-10)
    return sp.union_all([top, bottom])


def CenterShaft():
    return sp.cylinder_z(Cylinder_Top_Shaft_Diameter, Element_Height + 2 * z,
                          sections=Cyl_Fn, base_z=-z)


def HollowBody():
    """v2/mignon.scad:363-370 - a plain 4-point rotate_extrude() polygon,
    tapering from Cylinder_Bottom_Shaft_Diameter to Cylinder_Top_Shaft_
    Diameter - replaces Blickensderfer/Postal's whole Core()+HollowSpace()+
    BottomSlopedSpace() combination with one simple shape (no core-shaft
    groove family at all, see the module docstring)."""
    profile = [
        (Cylinder_Bottom_Shaft_Diameter / 2, 0 - z),
        (Cylinder_Bottom_Shaft_Diameter / 2, Element_Height - Cylinder_Top_Height_Offset - 4),
        (Cylinder_Top_Shaft_Diameter / 2 - z, Element_Height - Cylinder_Top_Height_Offset),
        (0 + z, -z),
    ]
    return sp.revolve_polygon(profile, sections=Surface_Fn)


def AlignmentPin():
    """v2/mignon.scad:372-384 - a plain cut-through alignment keyway (a
    hull of two circles, extruded and rotated into the shaft bore) - not
    a countersunk drive pin like Blickensderfer/Postal's DrivePin(), no
    HollowSpace()-style countersink concept at all."""
    from shapely.geometry import Point
    from shapely.ops import unary_union
    depth = Cylinder_Bottom_Shaft_Diameter / 2 + Pin_Depth + (5 if Pin_Through else 0)
    c1 = Point(0, 0).buffer(Pin_Width / 2, resolution=32)
    c2 = Point(0, Pin_Height - Pin_Width / 2).buffer(Pin_Width / 2, resolution=32)
    hull_poly = unary_union([c1, c2]).convex_hull
    shape = trimesh.creation.extrude_polygon(hull_poly, depth)
    return sp.scad_transform(shape, ("rotate", [90, 0, 90]))


# ---------------------------------------------------------------- Element

def Additive(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
             draft_angle_deg=None):
    text_ring, char_parts = cylinder_machine.TextRing(
        points_per_mm=points_per_mm, separation_mm=separation_mm, align_kwargs=align_kwargs,
        cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Placement_Protrusion, angle_half_step=Angle_Half_Step)
    if Cylinder_Shape == 0:
        body = PolygonCylinder()
    else:
        body = sp.cylinder_z(Element_Diameter, Element_Height - Cylinder_Top_Height_Offset,
                              sections=Surface_Fn)
    inner = sp.union_all([text_ring, body])
    cleaned = inner.difference(MinkCleanup(), engine="manifold")
    return sp.union_all([cleaned, ElementChamfer(), ElementLogo(), ElementLabel()]), char_parts


def Subtractive(render_core_groove=None):
    # render_core_groove: accepted (matching cylinder_machine.Subtractive's
    # signature/generate.py's uniform build_fn(...) call) but unused -
    # Mignon has no core grooves at all (no core_shaft.scad family, see
    # the module docstring).
    return sp.union_all([CenterShaft(), HollowBody(), AlignmentPin()])


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                 cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
                 draft_angle_deg=None):
    _require_configured()
    additive, char_parts = Additive(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                     cone_segments=cone_segments,
                                     simplify_tolerance_mm=simplify_tolerance_mm,
                                     platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                     draft_angle_deg=draft_angle_deg)
    build_log.mesh_report(additive, "Additive")
    subtractive = Subtractive(render_core_groove)
    build_log.mesh_report(subtractive, "Subtractive (unioned)")
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="FullElement")
    return full, char_parts


# ---------------------------------------------------------------- Calibration
# cylinder_machine.CalibrationElement() can't be reused directly - its
# CalibrationAdditive() unconditionally builds Cylinder()+ClipCylinder()
# (Blickensderfer/Postal's round body + wire-clip mechanism, neither of
# which Mignon has - it would also crash outright, since Body_Fn/Clip_OD/
# Clip_Height are never set in Mignon's globals). Mirrors
# Additive()/FullElement() above exactly, swapping in
# cylinder_machine.CalibrationTextRing() for TextRing() - the one part
# that IS genuinely shared/reusable (see the module docstring).

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
    if Cylinder_Shape == 0:
        body = PolygonCylinder()
    else:
        body = sp.cylinder_z(Element_Diameter, Element_Height - Cylinder_Top_Height_Offset,
                              sections=Surface_Fn)
    inner = sp.union_all([text_ring, body])
    cleaned = inner.difference(MinkCleanup(), engine="manifold")
    return sp.union_all([cleaned, ElementChamfer(), ElementLogo(), ElementLabel()]), mapping_lines


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
    build_log.mesh_report(additive, "CalibrationAdditive")
    subtractive = Subtractive(render_core_groove)
    build_log.mesh_report(subtractive, "Subtractive (unioned)")
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="CalibrationElement")
    return full, mapping_lines


# ------------------------------------------------------------- Resin support

def ResinSupport():
    """v2/mignon.scad:386-405 - entirely bespoke: its own raft ring (a
    direct rotate_extrude() polygon, not the shared CutGroove) plus 12
    ResinRod() calls at one radius (every sector) and 6 more (alternating
    sectors) at a second, smaller radius near the top boss - no speed-hole/
    drive-pin/bottom-sloped-space support concepts at all (see the module
    docstring). Reuses cylinder_machine._resin_rod() for the rod
    primitive itself (the one thing that IS shared - v2/lib/resin_rod.scad's
    header: "machines whose rod placement differs... can still reuse the
    one universal rod shape")."""
    _require_configured()
    base_z = -Resin_Support_Height + z
    raft_profile = [
        (Element_Diameter / 2, 0),
        (Cylinder_Top_Shaft_Diameter / 2, 0),
        (Cylinder_Top_Shaft_Diameter / 2, Resin_Support_Thickness),
        (Element_Diameter / 2 + Resin_Support_Thickness, Resin_Support_Thickness),
    ]
    parts = [sp.translate(sp.revolve_polygon(raft_profile, sections=Resin_Fn), [0, 0, base_z])]
    r1 = (Element_Diameter + Cylinder_Bottom_Shaft_Diameter) / 4 - 0.1
    r2 = (Cylinder_Top_Shaft_Diameter + Cylinder_Top_Diameter) / 4
    for n in range(12):
        theta = np.radians(360.0 / 12 * n + 360.0 / 12)
        rod1 = cylinder_machine._resin_rod(Resin_Support_Height + Cylinder_Top_Height_Offset)
        parts.append(sp.translate(rod1, [r1 * np.cos(theta), r1 * np.sin(theta), base_z]))
        if n % 2 == 0:
            theta2 = theta + np.radians(360.0 / 24)
            rod2 = cylinder_machine._resin_rod(Resin_Support_Height)
            parts.append(sp.translate(rod2, [r2 * np.cos(theta2), r2 * np.sin(theta2), base_z]))
    return sp.union_all(parts)


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
               draft_angle_deg=None):
    """v2/mignon.scad:436-444 - unlike Blickensderfer/Postal's ResinPrint
    (plain union(FullElement(), ResinSupport())), Mignon's FLIPS the whole
    element upside-down first (translate([0,0,Element_Height])
    rotate([0,180,0])) before adding supports - the decorative/label end
    ends up facing the build plate (where ResinSupport() attaches, below
    the new z=0), the shaft-bore/mechanical end faces up, away from
    supports. A real, deliberate part of Mignon's print orientation, not
    an oversight - ported faithfully."""
    full, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                    cone_segments=cone_segments,
                                    simplify_tolerance_mm=simplify_tolerance_mm,
                                    platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                    draft_angle_deg=draft_angle_deg)
    flipped = sp.scad_transform(full, ("translate", [0, 0, Element_Height]), ("rotate", [0, 180, 0]))
    support = ResinSupport()
    build_log.mesh_report(support, "ResinSupport")
    combined = sp.union_all([flipped, support])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts
