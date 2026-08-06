"""
v4 Vogue Slug - ports v1/Type Slugs/VogueSlug.scad, the faithful replica
(modeled from real drawings) carrying the real 2-piece "Vogue Foundry"
mark (arrow + V, imported from vogue-foundry-arrow.svg/vogue-foundry-
v.svg) plus its own True_Vogue typeface default. Shares lib/wing_slug.py's
engine with lib/type_slug.py/lib/gauge_slug.py - see that module's
docstring for the shared geometry pipeline and the v1-is-ground-truth
callout (VogueSlug.scad was never carried into v2 either).

All real numbers live in config/vogue_slug.yaml - call configure(path)
once before using anything else in this module (see generate.py).
"""

import yaml

import wing_slug
from wing_slug import FullElement, ResinPrint, Additive  # re-exported for callers

_configured = False


def configure(config_path):
    global _configured
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg
    g["z"] = 0.001

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["Font_Size"] = font["size_mm"]

    align = cfg["alignment"]
    g["Align_Mode"] = align["mode"]
    g["Align_Center_Offset_Mm"] = align["center_offset_mm"]
    g["Align_Left_Offset_Mm"] = align["left_offset_mm"]
    g["Align_Modified_Left_Chars"] = align["modified_left_chars"]
    g["Align_Modified_Left_Offset_Mm"] = align["modified_left_offset_mm"]
    g["Align_Modified_Right_Chars"] = align["modified_right_chars"]
    g["Align_Modified_Right_Offset_Mm"] = align["modified_right_offset_mm"]

    char = cfg["character"]
    g["Character_Enabled"] = char["char_enabled"]
    g["Lower_Char"] = char["lower_char"]
    g["Upper_Char"] = char["upper_char"]

    logo = cfg["logo"]
    g["Logo_Enabled"] = logo["logo_enabled"]
    g["Logo_Svg_File"] = logo["svg_file"]
    g["Logo_Scale_Mm_Per_Unit"] = logo["scale_mm_per_unit"]
    g["Logo_Depth_Mm"] = logo["logo_depth_mm"]
    g["Logo_Location"] = logo["location_frac"]
    g["Logo_Vogue_Enabled"] = logo["vogue_enabled"]
    g["Vogue_Arrow_Svg_File"] = logo["vogue_arrow_svg_file"]
    g["Vogue_V_Svg_File"] = logo["vogue_v_svg_file"]
    g["Vogue_Scale_Mm_Per_Unit"] = logo["vogue_scale_mm_per_unit"]

    lbl = cfg["label"]
    g["Copyright_Text"] = lbl["text"]
    g["Copyright_Font"] = lbl["font_path"]
    g["Copyright_Depth"] = lbl["label_depth_mm"]

    e = cfg["element"]
    g["Body_Width"] = e["body_width_mm"]
    g["Body_Length"] = e["body_length_mm"]
    g["Body_Height"] = e["body_height_mm"]
    g["Face_Thickness"] = e["face_thickness_mm"]
    g["Face_Radius"] = e["face_radius_mm"]
    g["Wing_Radius"] = e["wing_radius_mm"]
    g["Platen_Shift_Motion"] = e["platen_shift_motion_mm"]
    g["Baselines_Shift_Motion"] = e["baselines_shift_motion_mm"]
    g["Body_Slot_Width"] = e["body_slot_width_mm"]
    g["Wing_Thickness"] = e["wing_thickness_mm"]
    g["Aligning_Cut"] = e["aligning_cut_mm"]
    g["Baseline"] = e["baseline_mm"]
    g["Platen_Diameter"] = e["platen_diameter_mm"]
    g["Bottom_Thickness"] = e["bottom_thickness_mm"]
    g["Upper_Wing_Angle"] = e["upper_wing_angle_deg"]
    g["Lower_Wing_Angle"] = e["lower_wing_angle_deg"]
    g["Element_Loop_Enabled"] = e["loop_enabled"]
    g["Loop_Thickness"] = e["loop_thickness_mm"]
    g["Loop_Diameter"] = e["loop_diameter_mm"]
    g["Loop_Rotation"] = e["loop_rotation_deg"]
    g["Element_Post_Enabled"] = e["post_enabled"]
    g["Post_ID"] = e["post_id_mm"]
    g["Post_OD"] = e["post_od_mm"]
    g["Element_Side_Hole_Enabled"] = e["side_hole_enabled"]
    g["Side_Hole_ID"] = e["side_hole_id_mm"]
    g["Side_Hole_Height"] = e["side_hole_height_frac"]

    b = cfg["build"]
    g["DEFAULT_FLATNESS_TOLERANCE_MM"] = b["flatness_tolerance_mm"]
    g["DEFAULT_MINKOWSKI_ENABLED"] = b["minkowski_enabled"]
    g["Draft_Angle"] = b["draft_angle_deg"]
    g["Engraving_Depth"] = b["engraving_depth_mm"]
    g["Minkowski_Multiplier"] = b["minkowski_multiplier"]
    g["Character_Block_Height_Mm"] = b["character_block_height_mm"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]

    q = cfg["quality"]
    g["Corner_Fn"] = q["corner_fn"]
    g["Wing_Fn"] = q["wing_fn"]
    g["Platen_Fn"] = q["platen_fn"]
    g["Minkowski_Fn"] = q["minkowski_fn"]
    g["Loop_Fn"] = q["loop_fn"]
    g["Loop_Tube_Fn"] = q["loop_tube_fn"]
    g["Post_Fn"] = q["post_fn"]
    g["Side_Hole_Fn"] = q["side_hole_fn"]

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Raft_Thickness"] = r["raft_thickness_mm"]
    g["Wire_Thickness"] = r["wire_thickness_mm"]
    g["Support_Height"] = r["support_height_mm"]
    g["Support_Pitch"] = r["support_pitch_mm"]

    gauge = cfg["gauge"]
    g["Gauge_Enabled"] = gauge["gauge_enabled"]
    g["Gauge_Fine_Pitch_Mm"] = gauge["fine_pitch_mm"]
    g["Gauge_Major_Pitch_Mm"] = gauge["major_pitch_mm"]
    g["Gauge_Hole_D_Mm"] = gauge["hole_d_mm"]
    g["Gauge_Fine_Z_Mm"] = gauge["fine_z_mm"]
    g["Gauge_Major_Z_Mm"] = gauge["major_z_mm"]
    g["Gauge_Hole_Fn"] = gauge["hole_fn"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    tt = cfg.get("type_test", {})
    g["Test_CPI"] = tt.get("cpi", 10.0)
    g["Test_String_Custom"] = tt.get("text", "")

    _configured = True
    wing_slug._receive_config(g, "vogue_slug")


def _require_configured():
    if not _configured:
        raise RuntimeError("call vogue_slug.configure(config_path) before using this module")
