"""
v4 Selectric Composer typeball - ports the Render_Mode==0 branch of
v2/ibm.scad (+ v2/lib/layouts/ibm_layouts.scad's Composer-specific
section, US language only - see lib/layouts/selectric_composer_layout.py).

All real-machine numbers live in config/selectric_composer.yaml, not
here - call configure(path) once before using anything else in this
module (see generate.py).

Everything structurally shared with Selectric I/II/III (FullBody/
SolidCleanup/Teeth/Notch/the character-glyph pipeline/labels/resin
supports) lives in lib/spherical_machine.py - see that module's docstring
for the dynamic-dispatch mechanism. Composer's own pica/units type-test
system (v2's TextGaugeComposerLine2/Composer_Pitch_List/cumulativeSum) is
NOT ported in this pass - genuinely different code from Selectric I/II &
III's shared CPI TextGauge(), and not required for FullElement/
ResinPrint (a separate print-test-gauge render variant) - deferred like
Calibration/drain holes were for the other two Selectric machines.

IMPORTANT: alignment.x_pos_offset/y_pos_offset/h_alignment/
custom_h_offset/custom_v_offset in config/selectric_composer.yaml are
print-critical per explicit user directive - verified line-by-line
against v2/ibm.scad's X_Pos_Offset_Composer_/Y_Pos_Offset_Composer/
All_H_Alignments[0], not approximated or defaulted from Selectric I/II's
values despite sharing the same physical ball class.
"""

import yaml

import spherical_machine
from spherical_machine import FullElement, ResinPrint, Additive  # re-exported for callers
from layouts.selectric_composer_layout import LOWERCASECOMPOSER_US, UPPERCASECOMPOSER_US, longitude_latitude

_configured = False


def configure(config_path):
    global _configured
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg
    g["z"] = 0.001

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    # v2: Font_Size_Selected = Composer_Cap_Height/2.834 (ibm.scad:186,190) -
    # Composer's cap-height sizing convention, NOT Selectric I/II & III's
    # direct point size.
    g["Font_Size"] = font["composer_cap_height"] / 2.834
    g["FONT_NAME"] = font["name"]

    font2 = cfg["font2"]
    g["FONT2_PATH"] = font2["font2_path"]
    g["Font2_Size"] = font2["font2_composer_cap_height"] / 2.834
    g["Font2_Chars"] = font2["font2_chars"]

    align = cfg["alignment"]
    g["H_Alignment"] = align["mode"]
    g["X_Pos_Offset"] = align["x_pos_offset"]
    g["Y_Pos_Offset"] = align["y_pos_offset"]
    g["CUSTOMHALIGNCHARS"] = align["custom_h_chars"]
    g["CUSTOMHALIGNOFFSET"] = align["custom_h_offset"]
    g["CUSTOMVALIGNCHARS"] = align["custom_v_chars"]
    g["CUSTOMVALIGNOFFSET"] = align["custom_v_offset"]

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
    g["DEFAULT_POINTS_PER_MM"] = b["points_per_mm"]
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

    # Character/hemisphere layout - see lib/layouts/selectric_composer_layout.py
    g["CASES88_LOWER"] = LOWERCASECOMPOSER_US
    g["CASES88_UPPER"] = UPPERCASECOMPOSER_US
    g["LONGITUDE_LATITUDE"] = longitude_latitude()

    _configured = True
    spherical_machine._receive_config(g, "selectric_composer")


def _require_configured():
    if not _configured:
        raise RuntimeError("call selectric_composer.configure(config_path) before using this module")
