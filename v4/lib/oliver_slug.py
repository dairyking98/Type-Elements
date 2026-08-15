"""
v4 Oliver Slug - ports v1/Type Slugs/OliverSlug.scad, a replica modeled
after a real Oliver typewriter type slug (novelty/reference, not a
functional part - per the user's own framing). Shares lib/box_slug.py's
engine with lib/lumi_slug.py - see that module's docstring for the
shared geometry pipeline and the v1-is-ground-truth callout.

All real numbers live in config/oliver_slug.yaml - call configure(path)
once before using anything else in this module (see generate.py).
"""

import yaml

import box_slug
from box_slug import FullElement, ResinPrint, Additive  # re-exported for callers

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
    # per-character baseline overrides (both default 0.0) - see
    # glyph_poc.ALIGN_CARET_DROP_MM. .get() so a config predating
    # these keys still loads.
    g["Align_Caret_Drop_Mm"] = align.get("caret_drop_mm", 0.0)
    g["Align_Underscore_Lift_Mm"] = align.get("underscore_lift_mm", 0.0)

    char = cfg["character"]
    g["Character_Chars"] = char["chars"]
    g["Baseline"] = char["baseline_mm"]
    g["Baselines_Shift_Motion"] = char["baselines_shift_motion_mm"]

    e = cfg["element"]
    g["Body_Width"] = e["body_width_mm"]
    g["Body_Length"] = e["body_length_mm"]
    g["Body_Height"] = e["body_height_mm"]
    g["Platen_Shift_Motion"] = e["platen_shift_motion_mm"]
    g["Body_Slot_Width"] = e["body_slot_width_mm"]
    g["Wing_Thickness"] = e["wing_thickness_mm"]
    g["Aligning_Cut"] = e["aligning_cut_mm"]
    g["Platen_Diameter"] = e["platen_diameter_mm"]
    g["Bottom_Thickness"] = e["bottom_thickness_mm"]
    g["Upper_Wing_Angle"] = e["upper_wing_angle_deg"]
    g["Element_Loop_Enabled"] = e["loop_enabled"]
    g["Loop_Thickness"] = e["loop_thickness_mm"]
    g["Loop_Diameter"] = e["loop_diameter_mm"]
    g["Loop_Rotation"] = e["loop_rotation_deg"]

    b = cfg["build"]
    g["DEFAULT_FLATNESS_TOLERANCE_MM"] = b["flatness_tolerance_mm"]
    g["DEFAULT_MINKOWSKI_ENABLED"] = b["minkowski_enabled"]
    g["Draft_Angle"] = b["draft_angle_deg"]
    g["Engraving_Depth"] = b["engraving_depth_mm"]
    # Cone height is stored absolutely (minkowski_cone_height_mm) like every
    # other machine; the engine still wants v1's multiplier form, so derive
    # it back. Engraving_Depth * Multiplier == the configured height.
    g["Minkowski_Multiplier"] = b["minkowski_cone_height_mm"] / b["engraving_depth_mm"]
    g["Character_Block_Height_Mm"] = b["character_block_height_mm"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]

    q = cfg["quality"]
    g["Minkowski_Fn"] = q["minkowski_fn"]
    g["Platen_Fn"] = q["platen_fn"]
    g["Loop_Fn"] = q["loop_fn"]
    g["Loop_Tube_Fn"] = q["loop_tube_fn"]

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    tt = cfg.get("type_test", {})
    g["Test_CPI"] = tt.get("cpi", 10.0)
    g["Test_String_Custom"] = tt.get("text", "")

    _configured = True
    box_slug._receive_config(g, "oliver_slug")


def _require_configured():
    if not _configured:
        raise RuntimeError("call oliver_slug.configure(config_path) before using this module")
