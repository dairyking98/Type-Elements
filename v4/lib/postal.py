"""
v4 full-fidelity Postal body - ports v2/postal.scad's Additive()/
Subtractive()/FullElement() structure directly, using the SAME origin/
orientation convention as blickensderfer.py (Z=0 at the bottom face of the
main disk, Z+ up through the clip end).

All real-machine numbers live in config/postal.yaml, not here - call
configure(path) once before using anything else in this module (see
generate.py).

Everything structurally shared with Blickensderfer (Cylinder/Subtractive/
FullElement/ResinPrint/the Gauge family/...) lives in cylinder_machine.py -
see that module's docstring for the dynamic-dispatch mechanism. Only the
"drive pin trio" (HollowSpace/DrivePin/ResinSupport) lives here - Postal's
versions are simpler than Blickensderfer's: no drive-pin countersink at
all (HollowSpace is a plain revolve, DrivePin a plain centered box, no
sink cylinder unioned on)."""

import trimesh
import yaml

from glyph_poc import (
    DEFAULT_CONE_SEGMENTS as GLYPH_DEFAULT_CONE_SEGMENTS,
    DEFAULT_SIMPLIFY_TOLERANCE_MM as GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM,
    DEFAULT_PLATEN_FN as GLYPH_DEFAULT_PLATEN_FN,
    DEFAULT_MINKOWSKI_ENABLED as GLYPH_DEFAULT_MINKOWSKI_ENABLED,
    DEFAULT_DRAFT_ANGLE_DEG as GLYPH_DEFAULT_DRAFT_ANGLE_DEG,
)
import scad_primitives as sp
import cylinder_machine
from cylinder_machine import FullElement, ResinPrint, GaugeTestSet  # re-exported for callers

_configured = False


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - see
    blickensderfer.configure()'s docstring for the general scheme. Postal
    has no drive-pin countersink, so its element: section has no
    drive_pin_countersink_depth/drive_pin_support_radial_offset/
    drive_pin_support_height/drive_pin_style keys - and Drive_Pin_Width
    reuses Core_ID_Offset directly as its tolerance addition (v2/
    postal.scad:215-217: `Drive_Pin_Width=Drive_Pin_Widthmm+
    Core_ID_Offset`), unlike Blickensderfer's dedicated
    Drive_Pin_Width_Offset key."""
    global _configured
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
    g["Logo_Text_Offset"] = logo["text_offset_deg"]
    g["Logo_Radial_Offset"] = logo.get("radial_offset_mm", 1.5)

    e = cfg["element"]
    g["z"] = 0.01
    g["Element_Diameter"] = e["element_diameter"]
    g["Platen_Diameter"] = e["platen_diameter"]
    g["Min_Final_Character_Diameter"] = e["min_final_character_diameter"]
    g["Char_Protrusion"] = (e["min_final_character_diameter"] - e["element_diameter"]) / 2.0
    g["Element_Height"] = e["element_height"]
    g["Wall_Min_Thickness"] = e["wall_min_thickness"]
    g["Wall_Chamfer"] = e["wall_chamfer"]
    g["Roof_Offset"] = e["roof_offset"]
    g["Speed_Hole_ID"] = e["speed_hole_id"]
    g["Speed_Hole_Qty"] = e["speed_hole_qty"]
    g["Speed_Hole_Radial"] = e["speed_hole_radial"]
    g["Core_ID_In"] = e["core_id_in"]
    g["Core_ID_Mm"] = e["core_id_in"] * 25.4
    g["Core_Groove_Qty"] = e["core_groove_qty"]
    g["Core_Groove_D"] = e["core_groove_d"]
    g["Core_Chamfer"] = e["core_chamfer"]
    g["Core_Bottom_Offset"] = e["core_bottom_offset"]
    g["Core_Contact_Length"] = e["core_contact_length"]
    g["Core_Web_Width"] = e["core_web_width"]
    g["Core_Web_Qty"] = e["core_web_qty"]
    g["Core_Web_Length"] = e["core_web_length"]
    g["Core_Secondary_ID_Offset"] = e["core_groove_d"] / 2 + g["z"]
    g["Clip_Height"] = e["clip_height"]
    g["Clip_Wire_OD"] = e["clip_wire_od"]
    g["Clip_Opening"] = e["clip_opening"]
    g["Clip_Bite"] = e["clip_bite"]
    g["Drive_Pin_Widthmm"] = e["drive_pin_widthmm"]
    g["Drive_Pin_Length"] = e["drive_pin_length"]
    g["Drive_Pin_Radial"] = e["drive_pin_radial"]
    g["Core_ID_Offset"] = e["core_id_offset"]

    g["Shaft_Diameter"] = g["Core_ID_Mm"] + g["Core_ID_Offset"]
    # Postal reuses Core_ID_Offset directly - no dedicated width-offset key
    g["Drive_Pin_Width"] = g["Drive_Pin_Widthmm"] + g["Core_ID_Offset"]
    g["Clip_OD"] = g["Shaft_Diameter"] + 2 * g["Wall_Min_Thickness"]
    g["Logo_Radius"] = g["Element_Diameter"] / 2 - 2.0

    g["Core_Top_Z"] = g["Element_Height"] + g["Clip_Height"]
    g["Core_Bottom_Z"] = g["Core_Bottom_Offset"]
    g["Core_Taper_Top_Z"] = g["Element_Height"]

    q = cfg["quality"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Groove_Fn"] = q["groove_fn"]
    # v2/postal.scad's own Cylinder()/ClipCylinder() use DIFFERENT Fn
    # values (Cyl_Fn=360 / Surface_Fn=120 respectively) - unlike
    # Blickensderfer, where both already use the same value. v4's shared
    # cylinder_machine.Cylinder()/ClipCylinder() use a single Body_Fn knob
    # for both (an existing simplification, not new to this port) - set
    # to Postal's Cyl_Fn value here, which makes Cylinder() exact and
    # ClipCylinder() slightly over-faceted (harmless - more circle
    # segments than the real file uses there, not fewer).
    g["Body_Fn"] = q.get("body_fn", q["cyl_fn"])
    g["Platen_Fn"] = q.get("platen_fn", GLYPH_DEFAULT_PLATEN_FN)

    layout = cfg["layout"]
    g["BASELINE_ROW"] = layout["baseline_row"]
    g["CUTOUT_ROW"] = layout["cutout_row"]
    g["LATITUDE_INT"] = 360.0 / layout["latitude_columns"]
    g["BASELINE_Z_OFFSET"] = g["Element_Height"]
    g["PLACEMENT_MAP"] = layout["placement_map"]
    g["DHIATENSOR"] = layout["rows"]

    g["PLATEN_RADIUS_MM"] = 1.0 / g["Platen_Diameter"]

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
    g["DEFAULT_RENDER_CORE_GROOVE"] = b["render_core_groove"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]
    g["DEFAULT_CONE_SEGMENTS"] = q.get("minkowski_fn", b.get("cone_segments", GLYPH_DEFAULT_CONE_SEGMENTS))
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM)
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", GLYPH_DEFAULT_MINKOWSKI_ENABLED)
    g["DEFAULT_DRAFT_ANGLE_DEG"] = b.get("draft_angle_deg", GLYPH_DEFAULT_DRAFT_ANGLE_DEG)

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Min_Rod_Height"] = r["min_rod_height"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Raft_Thickness"] = r["raft_thickness"]
    g["Resin_Groove_OD"] = r["groove_od"]
    g["Resin_Groove_Thickness"] = r["groove_thickness"]
    g["Resin_Rod_Raft"] = r["rod_raft"]
    g["Cut_Groove_Inner_X"] = r["cut_groove_inner_x"]
    g["Bottom_Support_Fractions"] = r["bottom_support_fractions"]
    g["Bottom_Support_Inner_Angle_Offset"] = r["bottom_support_inner_angle_offset"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    gauge = cfg.get("gauge", {})
    g["Gauge_Offset_Start"] = gauge.get("offset_start", 0.0)
    g["Gauge_Offset_Int"] = gauge.get("offset_int", 0.025)

    g["Bottom_Slope"] = g["Core_Bottom_Offset"] / (
        (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
        - (g["Element_Diameter"] / 2 - g["Wall_Min_Thickness"] - g["Wall_Chamfer"]))
    g["Bottom_Z_Offset"] = (-g["Bottom_Slope"] * (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
                            + g["Core_Bottom_Offset"])

    # BottomSlopedSpace()'s floor-Z literal - Postal uses -z (v2/
    # postal.scad ~362-367: "to help with z fighting"), vs
    # Blickensderfer's 0 - see blickensderfer.configure()'s matching note.
    g["Bottom_Sloped_Space_Floor_Z"] = -g["z"]

    _configured = True
    cylinder_machine._receive_config(g, "postal")


def _require_configured():
    if not _configured:
        raise RuntimeError("call postal.configure(config_path) before using this module")


def HollowSpace():
    """No countersink at all - unlike Blickensderfer's HollowSpace(),
    which subtracts a drive-pin-countersink cylinder from the same
    profile (v2/postal.scad:355-360 is a plain rotate_extrude, no
    difference())."""
    return sp.revolve_polygon(cylinder_machine._hollow_space_profile(), sections=Surface_Fn)


def DrivePin():
    """A single centered box, no countersink cylinder unioned on (v2/
    postal.scad:378-383: linear_extrude(5) of a centered
    [Drive_Pin_Width, Drive_Pin_Length] square, extruded from z=0 to 5 -
    unlike Blickensderfer's countersink-sized version). v2's DrivePin(Offset)
    takes an unused Offset parameter (Subtractive() always calls it with
    none) - dropped here since nothing ever passes one."""
    pin = trimesh.creation.box(extents=[Drive_Pin_Width, Drive_Pin_Length, 5])
    pin = sp.scad_transform(
        pin,
        ("translate", [Drive_Pin_Radial, 0, 2.5]),
        ("rotate", [0, 0, 90]),
    )
    return pin


def ResinSupport():
    """Postal's drive-pin-support geometry is the plain pin's own half-
    extents (Drive_Pin_Length/2, Drive_Pin_Width/2), unlike
    Blickensderfer's countersink-sized version - v2/postal.scad:433-440."""
    _require_configured()
    parts = [
        cylinder_machine.CutGroove(),
        cylinder_machine.SpeedHoleSupports(),
        cylinder_machine.DrivePinSupport(Drive_Pin_Radial, Drive_Pin_Length / 2, Drive_Pin_Width / 2),
        cylinder_machine.BottomSupports(),
    ]
    return sp.union_all(parts)
