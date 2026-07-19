"""
v4 full-fidelity Blickensderfer body - ports v2/blickensderfer.scad's
Additive()/Subtractive()/FullElement() structure directly, using the SAME
origin/orientation convention as the OpenSCAD file (Z=0 at the bottom face
of the main disk, Z+ up through the clip end; Baseline_Z_Offset shifts the
negative-from-clip-end Baseline/Cutout arrays into this absolute frame).

All real-machine numbers live in config/blickensderfer.yaml, not here -
call configure(path) once before using anything else in this module (see
generate.py). Derived values (Shaft_Diameter, Clip_OD, etc.) are computed
in configure() from that file's base parameters, matching how
v2/blickensderfer.scad itself derives them.

Everything structurally shared with Postal (Cylinder/Subtractive/
FullElement/ResinPrint/the Gauge family/...) lives in cylinder_machine.py
instead - see that module's docstring for the dynamic-dispatch mechanism.
Only the "drive pin trio" (HollowSpace/DrivePin/ResinSupport - the one
place v2's two machines genuinely diverge in code, not just parameter
values) lives here.
"""

import numpy as np
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
    """Loads config_path (YAML) and sets this module's globals - base
    parameters copied straight from the file, derived ones computed the
    same way v2/blickensderfer.scad (and lib/core_shaft.scad,
    lib/resin_support.scad) derive them from their own base parameters."""
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
    # real v2 value - the logo ring's placement radius = Logo_Radius +
    # this. Exposed as a tunable: at the real value, the logo's angular
    # spacing can coincidentally land very close to a DHIATENSOR column
    # (confirmed once, on this exact layout - see SESSION_LOG.md) since
    # nothing forces separation between the two independent layouts.
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
    g["Drive_Pin_Countersink_Depth"] = e["drive_pin_countersink_depth"]
    g["Drive_Pin_Support_Radial_Offset"] = e["drive_pin_support_radial_offset"]
    g["Drive_Pin_Support_Height"] = e["drive_pin_support_height"]
    g["Drive_Pin_Style"] = e["drive_pin_style"]
    g["Core_ID_Offset"] = e["core_id_offset"]
    g["Drive_Pin_Width_Offset"] = e["drive_pin_width_offset"]

    g["Shaft_Diameter"] = g["Core_ID_Mm"] + g["Core_ID_Offset"]
    g["Drive_Pin_Width"] = g["Drive_Pin_Widthmm"] + g["Drive_Pin_Width_Offset"]
    g["Drive_Pin_Countersink_ID"] = np.sqrt(g["Drive_Pin_Width"] ** 2 + g["Drive_Pin_Length"] ** 2)
    g["Clip_OD"] = g["Shaft_Diameter"] + 2 * g["Wall_Min_Thickness"]
    g["Logo_Radius"] = g["Element_Diameter"] / 2 - 2.0

    g["Core_Top_Z"] = g["Element_Height"] + g["Clip_Height"]
    g["Core_Bottom_Z"] = g["Core_Bottom_Offset"]
    g["Core_Taper_Top_Z"] = g["Element_Height"]

    q = cfg["quality"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Groove_Fn"] = q["groove_fn"]
    # Body_Fn: the main visible/cosmetic element body (Cylinder/
    # ClipCylinder) - kept separate from Surface_Fn (everything else
    # structural: HollowSpace, SpeedHoles, chamfers, resin details) and
    # from Cyl_Fn (the inner shaft/core bore only) per user direction -
    # not merged into either even though it may be set to the same value.
    g["Body_Fn"] = q.get("body_fn", q["surface_fn"])
    # Platen_Fn: circular segments for the real platen cutout cylinder in
    # glyph_poc.build_glyph (see its docstring) - not in older configs, so
    # defaults to glyph_poc's own default rather than requiring every
    # config file to be updated.
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
    # circular segments for build_glyph's Minkowski cone kernel - see
    # glyph_poc.DEFAULT_CONE_SEGMENTS docstring. Lives under quality.
    # minkowski_fn now (grouped with the other facet-count knobs); still
    # falls back to the older build.cone_segments key, then glyph_poc's
    # own default, so existing configs don't need to be updated.
    g["DEFAULT_CONE_SEGMENTS"] = q.get("minkowski_fn", b.get("cone_segments", GLYPH_DEFAULT_CONE_SEGMENTS))
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM)
    # Off = skip build_glyph's Minkowski sweep entirely (fast, undrafted
    # preview - see glyph_poc.DEFAULT_MINKOWSKI_ENABLED docstring).
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", GLYPH_DEFAULT_MINKOWSKI_ENABLED)
    # Minkowski draft cone's half-angle source (see glyph_poc's module
    # docstring/build_glyph's draft_angle_deg) - real machine value 55deg,
    # previously a fixed glyph_poc.py constant with no config override.
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
    # resin.raft: false (default, matches v2's original Blickensderfer
    # behavior) = each rod grows its own small raft; true = one
    # continuous raft plate shared by every rod (v2's original Postal
    # behavior) - see cylinder_machine.resin_raft_config's docstring.
    # Shared with postal.py so the two stay exactly in sync.
    g["Resin_Rod_Raft"], g["Cut_Groove_Inner_X"] = cylinder_machine.resin_raft_config(
        g["Element_Diameter"], g["Wall_Min_Thickness"], r.get("raft", False))
    g["Bottom_Support_Fractions"] = r["bottom_support_fractions"]
    g["Bottom_Support_Inner_Angle_Offset"] = r["bottom_support_inner_angle_offset"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    # [Shaft Gauge Test] - see GaugeTestSet()'s docstring. .get() with v2's
    # own defaults so older configs without a `gauge:` section still work.
    gauge = cfg.get("gauge", {})
    g["Gauge_Offset_Start"] = gauge.get("offset_start", 0.0)
    g["Gauge_Offset_Int"] = gauge.get("offset_int", 0.025)

    # bottomZ/bottomX, ported exactly from lib/resin_support.scad
    # (Blickensderfer takes the lib defaults - no override in
    # blickensderfer.scad).
    g["Bottom_Slope"] = g["Core_Bottom_Offset"] / (
        (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
        - (g["Element_Diameter"] / 2 - g["Wall_Min_Thickness"] - g["Wall_Chamfer"]))
    g["Bottom_Z_Offset"] = (-g["Bottom_Slope"] * (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
                            + g["Core_Bottom_Offset"])

    # BottomSlopedSpace()'s floor-Z literal - Blickensderfer uses 0 (v2:
    # blickensderfer.scad ~414-419), Postal uses -z (postal.scad ~362-367,
    # both files' own comment: "to help with z fighting"). A real, if
    # cosmetic (0.01mm), textual divergence beyond the drive-pin trio.
    g["Bottom_Sloped_Space_Floor_Z"] = 0.0

    _configured = True
    cylinder_machine._receive_config(g, "blickensderfer")


def _require_configured():
    if not _configured:
        raise RuntimeError("call blickensderfer.configure(config_path) before using this module")


def HollowSpace():
    body = sp.revolve_polygon(cylinder_machine._hollow_space_profile(), sections=Surface_Fn)
    countersink_id = Drive_Pin_Countersink_ID if Drive_Pin_Style == 0 else None
    radius = Drive_Pin_Radial if Drive_Pin_Style == 0 else None
    cutter = sp.cylinder_z(countersink_id + 2 * Drive_Pin_Support_Radial_Offset,
                            Drive_Pin_Countersink_Depth + Drive_Pin_Support_Height,
                            sections=Surface_Fn)
    cutter = sp.translate(cutter, [radius, 0, 0])
    return body.difference(cutter, engine="manifold")


def DrivePin():
    if Drive_Pin_Style != 0:
        raise NotImplementedError("Drive_Pin_Style=1 (old) not ported")
    pin = trimesh.creation.box(extents=[Drive_Pin_Width, Drive_Pin_Length, 5])
    pin = sp.scad_transform(
        pin,
        ("translate", [Drive_Pin_Radial, 0, -z + 2.5]),
        ("rotate", [0, 0, 90]),
    )
    sink = sp.cylinder_z(Drive_Pin_Countersink_ID, z + Drive_Pin_Countersink_Depth, sections=Surface_Fn)
    sink = sp.translate(sink, [Drive_Pin_Radial, 0, -z])
    return sp.union_all([pin, sink])


def ResinSupport():
    """Blickensderfer's drive-pin-support geometry is countersink-sized
    (Drive_Pin_Countersink_ID/2), unlike Postal's plain-pin version - see
    postal.py's ResinSupport()."""
    _require_configured()
    countersink_id = Drive_Pin_Countersink_ID
    radius = Drive_Pin_Radial
    parts = [
        cylinder_machine.CutGroove(),
        cylinder_machine.SpeedHoleSupports(),
        cylinder_machine.DrivePinSupport(radius, countersink_id / 2, countersink_id / 2),
        cylinder_machine.BottomSupports(),
    ]
    return sp.union_all(parts)
