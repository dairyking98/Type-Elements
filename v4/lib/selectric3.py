"""
v4 Selectric III typeball - ports the Render_Mode==2 branch of
v2/ibm.scad (+ v2/lib/layouts/ibm_layouts.scad's S3-specific section).

All real-machine numbers live in config/selectric3.yaml, not here - call
configure(path) once before using anything else in this module (see
generate.py).

Everything structurally shared with Selectric I/II/Selectric Composer
(FullBody/SolidCleanup/Teeth/Notch/the character-glyph pipeline/labels/
resin supports) lives in lib/spherical_machine.py - see that module's
docstring for the dynamic-dispatch mechanism. Only the character/
hemisphere layout data (lib/layouts/selectric3_layout.py, 96 chars/4 rows
of 24 instead of Selectric I/II's 88/22) and this configure() are
Selectric-III-specific; Selectric I/II and III share the CPI/monospaced
TextGauge() type-test convention (in spherical_machine.py).
"""

import yaml

import spherical_machine
from spherical_machine import FullElement, ResinPrint, Additive, TextGauge  # re-exported for callers
from layouts.selectric3_layout import longitude_latitude, HEMISPHERE_MAPS

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
    g["FONT_NAME"] = font["name"]

    font2 = cfg["font2"]
    g["FONT2_PATH"] = font2["font2_path"]
    g["Font2_Size"] = font2["font2_size_mm"]
    g["Font2_Chars"] = font2["font2_chars"]

    align = cfg["alignment"]
    g["H_Alignment"] = align["mode"]
    g["X_Pos_Offset"] = align["x_pos_offset"]
    g["Y_Pos_Offset"] = align["y_pos_offset"]
    g["CUSTOMHALIGNCHARS"] = align["custom_h_chars"]
    g["CUSTOMHALIGNOFFSET"] = align["custom_h_offset"]
    g["CUSTOMVALIGNCHARS"] = align["custom_v_chars"]
    g["CUSTOMVALIGNOFFSET"] = align["custom_v_offset"]
    # v4-only per-character baseline overrides, both default 0.0 (see
    # glyph_poc.ALIGN_CARET_DROP_MM). Distinct from CUSTOMVALIGN* above,
    # which is v2-faithful and a different shape - see
    # spherical_machine._text2d_contours's docstring. .get() so a config
    # predating these keys still loads.
    g["Align_Caret_Drop_Mm"] = align.get("caret_drop_mm", 0.0)
    g["Align_Underscore_Lift_Mm"] = align.get("underscore_lift_mm", 0.0)

    e = cfg["element"]
    g["Sphere_OD"] = e["sphere_od"]
    g["Sphere_R"] = e["sphere_od"] / 2.0
    g["Max_OD"] = e["max_od"]
    g["Type_Altitude"] = (e["max_od"] - e["sphere_od"]) / 2.0
    g["Top_Flat_To_Center"] = e["top_flat_to_center"]
    g["Top_Flat_Thickness"] = e["top_flat_thickness"]
    g["Top_Flat_R"] = (g["Sphere_R"] ** 2 - e["top_flat_to_center"] ** 2) ** 0.5
    g["Top_Chamfer"] = e["top_chamfer"]
    g["Inside_ID"] = e["inside_id"]
    g["Inside_R"] = e["inside_id"] / 2.0
    g["Boss_OD"] = e["boss_od"]
    g["Boss_R"] = e["boss_od"] / 2.0
    g["Boss_Clearance"] = e["boss_clearance"]
    g["Boss_Step"] = e["boss_step"]
    g["Boss_To_Center"] = e["boss_to_center_base"] + e["snoot_droop_compensation"]
    g["Snoot_Droop_Compensation"] = e["snoot_droop_compensation"]
    g["Shaft_ID"] = e["shaft_id"]
    g["Skirt_Top_OD"] = e["skirt_top_od"]
    g["Skirt_Bottom_OD"] = e["skirt_bottom_od"]
    skirt_top_r = e["skirt_top_od"] / 2.0
    g["Center_To_Skirt"] = (g["Sphere_R"] ** 2 - skirt_top_r ** 2) ** 0.5
    g["Platen_OD"] = e["platen_diameter"]
    g["Drive_Notch_Width"] = e["drive_notch_width"]
    g["Drive_Notch_Height"] = e["drive_notch_height"]
    g["Detent_Skirt_Clock_Offset"] = e["detent_skirt_clock_offset"]
    g["Drive_Notch_Theta"] = e["drive_notch_theta"] + e["detent_skirt_clock_offset"]
    g["Detent_Valley_To_Center"] = e["detent_valley_to_center"]

    g["Floor"] = e["floor"]
    g["Roof"] = g["Top_Flat_To_Center"] - g["Top_Flat_Thickness"]

    layout = cfg["layout"]
    g["Chars_Per_Row"] = layout["chars_per_row"]
    g["Chars_Per_Row_Reference"] = layout["chars_per_row_reference"]
    g["Longitude_Step"] = 360.0 / layout["chars_per_row"]
    g["Row_Latitudes"] = layout["row_latitudes"]
    g["Platen_Longitude_Offsets"] = layout["platen_longitude_offsets"]
    g["Baseline_Longitude_Offsets"] = layout["baseline_longitude_offsets"]
    g["Minkowski_Longitudinal_Offsets"] = layout["minkowski_longitudinal_offsets"]

    lbl = cfg["label"]
    g["Label"] = lbl["enabled"]
    g["Arrow"] = lbl["arrow_enabled"]
    g["Labels_Show_Number"] = lbl["show_number"]
    g["Label_No"] = lbl["label_no"]
    g["Label_Text_Override"] = lbl["label_text_override"]
    g["Label_No_Font_Override"] = lbl["label_no_font_override"]
    g["Label_Font_Override"] = lbl["label_font_override"]
    g["No_Label_Size"] = lbl["no_label_size"]
    g["No_Label_Offset"] = lbl["no_label_offset"]
    g["Font_Label_Size"] = lbl["font_label_size"]
    g["Font_Label_Offset"] = lbl["font_label_offset"]
    g["Del_Base_From_Centre"] = lbl["del_base_from_centre"]
    g["Del_Depth"] = lbl["del_depth"]

    b = cfg["build"]
    g["DEFAULT_FLATNESS_TOLERANCE_MM"] = b["flatness_tolerance_mm"]
    g["Mink_Draft_Angle"] = b["draft_angle_deg"]
    g["DEFAULT_MINKOWSKI_ENABLED"] = b["minkowski_enabled"]
    g["Character_Block_Height_Mm"] = b["character_block_height_mm"]
    g["Mink_Cone_Height_Mm"] = b["mink_cone_height_mm"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]

    q = cfg["quality"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Mink_Fn"] = q["minkowski_fn"]

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Tip_D"] = r["tip_od"]
    g["Tip_Notch_D"] = r["tip_notch_od"]
    g["Tip_Notch_Offset"] = r["tip_notch_offset"]
    g["Tip_In"] = r["tip_in"]
    g["Tip_H"] = r["tip_h"]
    g["Rod_D"] = r["rod_od"]
    g["Base_D"] = r["base_od"]
    g["Base_H"] = r["base_h"]
    g["Min_Rod_H"] = r["min_rod_h"]
    g["Resin_Detent_Clock_Offset"] = r["resin_detent_clock_offset"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    tt = cfg.get("type_test", {})
    g["Test_CPI"] = tt.get("cpi", 10.0)
    g["Test_String_Custom"] = tt.get("text", "")

    # Character/hemisphere layout - editable via tune.py's Layout tab
    # (layout.rows: 4 lowercase rows then 4 uppercase rows, keyboard
    # reading order - see lib/layouts/selectric3_layout.py for the fixed
    # hemisphere permutation this gets zipped against).
    rows = layout["rows"]
    cases_lower = "".join(rows[:4])
    cases_upper = "".join(rows[4:])
    assert len(cases_upper) == 48, (
        f"layout.rows' 4 uppercase rows must concatenate to exactly 48 "
        f"characters (same fixed hemisphere permutation as lowercase) - "
        f"got {len(cases_upper)}")
    g["CASES88_LOWER"] = cases_lower
    g["CASES88_UPPER"] = cases_upper
    # layout.hemisphere_map - v4-only, not a v1/v2 concept (v2 never had
    # a language variant for Selectric III) - which physical keyboard-
    # index -> typeball-slot permutation applies (see lib/layouts/
    # selectric3_layout.py's HEMISPHERE_MAPS/module docstring: NOT
    # character-aware, only correct if layout.rows' i-th character is
    # genuinely the same physical key the permutation was calibrated
    # against). "us" (default) for the real v2 US layout; tune.py's
    # layout-preset picker keeps this in sync with whichever named preset
    # (United States/Finnish-Swedish) is selected - hand-editing
    # layout.rows via Modify glyphs must set this explicitly to whichever
    # real map the custom rows were built against.
    hemisphere_map = HEMISPHERE_MAPS[layout.get("hemisphere_map", "us")]
    g["LONGITUDE_LATITUDE"] = longitude_latitude(cases_lower, hemisphere_map)

    _configured = True
    spherical_machine._receive_config(g, "selectric3")


def _require_configured():
    if not _configured:
        raise RuntimeError("call selectric3.configure(config_path) before using this module")
