"""
tune.py's per-machine field tables, machine list and comment-preserving YAML
helpers, as plain data with no UI dependency - so the v5 engines (the local
server and the in-browser Pyodide engine, which can't load Textual) share
them with tune.py instead of copying them. Moved out of tune.py verbatim;
tune.py imports everything back, so its behaviour is unchanged.
"""
import json
import os
import re

import yaml

# tune.py lives in v4/, this module in v4/lib/ - same root either way.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Machines the picker screen (shown on startup, or via the "Change
# Machine" button - see _compose_machine_picker/_select_machine) offers,
# each mapped to its own master config. Order here is the order shown.
MACHINES = {
    "blickensderfer": ("Blickensderfer", os.path.join(REPO_ROOT, "config", "blickensderfer.yaml")),
    "postal": ("Postal", os.path.join(REPO_ROOT, "config", "postal.yaml")),
    "mignon": ("Mignon", os.path.join(REPO_ROOT, "config", "mignon.yaml")),
    "bennett": ("Bennett", os.path.join(REPO_ROOT, "config", "bennett.yaml")),
    "helios": ("Helios Klimax", os.path.join(REPO_ROOT, "config", "helios.yaml")),
    "hammond": ("Hammond", os.path.join(REPO_ROOT, "config", "hammond.yaml")),
    "hammond_split": ("Hammond Split", os.path.join(REPO_ROOT, "config", "hammond_split.yaml")),
    "selectric12": ("Selectric I/II", os.path.join(REPO_ROOT, "config", "selectric12.yaml")),
    "selectric3": ("Selectric III", os.path.join(REPO_ROOT, "config", "selectric3.yaml")),
    "selectric_composer": ("Selectric Composer", os.path.join(REPO_ROOT, "config", "selectric_composer.yaml")),
    "type_slug": ("Type Slug", os.path.join(REPO_ROOT, "config", "type_slug.yaml")),
    "vogue_slug": ("Vogue Slug", os.path.join(REPO_ROOT, "config", "vogue_slug.yaml")),
    "gauge_slug": ("Gauge Slug", os.path.join(REPO_ROOT, "config", "gauge_slug.yaml")),
    "oliver_slug": ("Oliver Slug", os.path.join(REPO_ROOT, "config", "oliver_slug.yaml")),
    "lumi_slug": ("Lumi Slug", os.path.join(REPO_ROOT, "config", "lumi_slug.yaml")),
}

# Groups MACHINES by real-world type-element mechanism (not code-sharing -
# see CLAUDE.md's "Machine taxonomy" section for why those are different
# axes) so the machine picker can present short categories instead of
# one flat wall of buttons. Cylinders = type-wheel machines
# (Blickensderfer/Postal/Mignon/Bennett/Helios, per each module's own
# "cylinder"/"disk" docstring language); Shuttles = the arc-shaped type
# shuttle (Hammond/Hammond Split, per lib/hammond.py's and lib/
# hammond_split.py's own "shuttle" docstrings); Spheres = the IBM/
# Selectric typeball family (lib/spherical_machine.py's docstring);
# Slugs = the standalone novelty/reference type-slug replicas (lib/
# wing_slug.py's/lib/box_slug.py's own docstrings) - not full keyboard/
# typewriter assemblies like the other three groups, one small element
# each.
MACHINE_CATEGORIES = [
    ("Cylinders", ["blickensderfer", "postal", "mignon", "bennett", "helios"]),
    ("Shuttles", ["hammond", "hammond_split"]),
    ("Spheres", ["selectric12", "selectric3", "selectric_composer"]),
    ("Slugs", ["type_slug", "vogue_slug", "gauge_slug", "oliver_slug", "lumi_slug"]),
]

# Machine picker warnings - a machine present here gets a short warning
# line under its button (always visible, not hover-only) plus a fuller
# explanation as the button's own hover tooltip. Dict keyed by machine
# name per CLAUDE.md's "Keep doing this" convention (never an if/elif
# chain in _compose_machine_picker) - empty unless a real, specific
# concern exists for that machine; remove the entry once resolved rather
# than leaving a stale warning around.
MACHINE_PICKER_WARNINGS = {
    # 2026-08-10: Selectric III's character-ring rotation/mapping was
    # independently verified against a real third-party reference
    # (SelectricElement96.scad) and matches exactly (see SESSION_LOG.md).
    # Two OTHER real-machine-fit values remain unverified for Selectric
    # III SPECIFICALLY:
    #  - Drive_Notch_Theta (131deg, config/selectric3.yaml element.
    #    drive_notch_theta) - the shaft drive notch that keys the ball
    #    onto the tilt ring.
    #  - Detent_Skirt_Clock_Offset (0.0deg, config/selectric3.yaml
    #    element.detent_skirt_clock_offset) - the detent tooth skirt's
    #    phase relative to the character ring (lib/spherical_machine.py's
    #    SolidCleanup/ResinRodAssemble both rotate Teeth()/the resin rods
    #    by this same offset) - controls which tooth the tilt ring's
    #    detent pawl lands in, so a wrong value could seat the ball
    #    rotationally off from where the character ring/notch expect it
    #    to be, even if the notch angle itself is right.
    # Both are LITERALLY THE SAME shared mechanism/code (lib/spherical_
    # machine.py's Notch()/Teeth()) and the SAME v2-ported values as
    # Selectric I/II, which HAS been printed and used on a real machine
    # with no reported notch/fitment issue (only the separate character-
    # rotation bug this session already fixed) - so there's decent
    # inherited confidence, but Selectric III itself has never been
    # physically fitment-tested, and its own ball/skirt dimensions could
    # still interact with the same angle differently. The third-party
    # reference (SelectricElement96.scad) can't help verify this either -
    # it uses a completely different boss-slot mounting mechanism, not
    # Selectric I/II's shaft notch.
    "selectric3": (
        "⚠ UNTESTED - notch/teeth fitment",
        "Selectric III is untested on real hardware. Character layout and "
        "Del alignment triangle are independently verified, but the drive "
        "notch (Drive_Notch_Theta) and detent tooth skirt clock offset "
        "(Detent_Skirt_Clock_Offset) - same mechanism and values as "
        "Selectric I/II, which HAS been printed successfully - have never "
        "been fitment-tested on a real Selectric III. Needs real hardware "
        "testing before relying on a print.",
    ),
}


# Each section becomes one tab (except Layout/Build/Type Test, which have
# bespoke widgets - see compose()). Field tuples: (yaml key - must be
# unique across the whole file, section path for reading the current
# value, type, label, help text). type is float/int/bool/str.
#
# Element is the one section that genuinely differs between machines -
# Postal has no drive-pin countersink at all (see lib/postal.py), so its
# element: config has no drive_pin_countersink_depth/
# drive_pin_support_radial_offset/drive_pin_support_height/
# drive_pin_style/drive_pin_width_offset keys; get_nested() would KeyError
# against those for a Postal config. Every other section's schema is
# identical between machines. SECTIONS_BY_MACHINE below is built from one
# shared dict plus a per-machine Element field list - see
# TuneApp.__init__'s self.SECTIONS/self.FIELDS (instance attributes,
# fixed once at startup from the launch config's `machine:` key - tune.py
# does not support hot-swapping to a config of a DIFFERENT machine mid-
# session, since the Element tab's widget set would need to be rebuilt,
# not just repopulated - see _switch_master_config's guard).
# Draft angle sits with the font, not under Quality: how steep a character's
# walls can be depends on the face (a hairline needs a different draft
# than a heavy one), so it travels with a font profile.
DRAFT_ANGLE_FIELD = ("draft_angle_deg", ["build", "draft_angle_deg"], float, "Draft angle (deg)",
                     "Half-angle of the Minkowski draft cone each character is swept with. Only takes effect on "
                     "Render - Quick Preview always skips the draft sweep.")

SECTIONS_COMMON = {
    "Font & Alignment": [
        ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters."),
        ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Em-square size, matches OpenSCAD text(size=)."),
        ("mode", ["alignment", "mode"], str, "Align mode", '"center" or "left".'),
        ("center_offset_mm", ["alignment", "center_offset_mm"], float, "Center offset (mm)", ""),
        ("left_offset_mm", ["alignment", "left_offset_mm"], float, "Left offset (mm)", ""),
        ("modified_left_chars", ["alignment", "modified_left_chars"], str, "Modified-left chars", "Chars getting an extra left shift."),
        ("modified_left_offset_mm", ["alignment", "modified_left_offset_mm"], float, "Modified-left offset (mm)", ""),
        ("modified_right_chars", ["alignment", "modified_right_chars"], str, "Modified-right chars", "Chars getting an extra right shift."),
        ("modified_right_offset_mm", ["alignment", "modified_right_offset_mm"], float, "Modified-right offset (mm)", ""),
        ("caret_auto_raise", ["alignment", "caret_auto_raise"], bool, "Auto-raise caret",
         "Puts the top of \"^\" on the font's cap height (the top of its capitals, from the font's own data) - the raised caret typewriters had. Caret raise below adds to it."),
        ("caret_raise_mm", ["alignment", "caret_raise_mm"], float, "Caret raise (mm)",
         "Moves \"^\" up (negative = down), on top of auto-raise if that is on. Fonts draw U+005E wherever their circumflex accent sits, which rarely matches a typewriter face; a Blickensderfer caret on the baseline is about -0.6 x the font size."),
        DRAFT_ANGLE_FIELD,
        ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
         "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
    ],
    "Calibration": [
        ("test_char", ["calibration", "test_char"], str, "Test character",
         "Struck at every physical position - keep it simple/legible."),
        ("vary_baseline", ["calibration", "vary_baseline"], bool, "Vary baselines",
         "Sweep the character baseline per column. Usually only one of "
         "these two is on at a time."),
        ("vary_cutout", ["calibration", "vary_cutout"], bool, "Vary cutouts",
         "Sweep the platen cutout per column. Usually only one of these "
         "two is on at a time."),
        ("start", ["calibration", "start"], float, "Sweep start (mm)",
         "Offset added at column 0. Default -0.7 tests both below and "
         "above the reference value, not just above it."),
        ("interval", ["calibration", "interval"], float, "Sweep interval (mm)",
         "Added per column - column n tests start + n*interval."),
    ],
}

# Logo/Quality/Resin/Gauge are shared between Blickensderfer/Postal (same
# config schema) but NOT Mignon - its logo placement, facet-count knobs,
# and resin-support mechanism are all structurally different (see
# lib/mignon.py's module docstring), and it has no Shaft Gauge Test at
# all (v2/mignon.scad:30 - "Shaft Gauge Test... omitted"). Named
# *_BLICKPOSTAL rather than folded into SECTIONS_COMMON for that reason -
# SECTIONS_BY_MACHINE below assembles each machine's own combination.
LOGO_FIELDS_BLICKPOSTAL = [
    ("font_path", ["logo", "font_path"], str, "Logo font path", "Font for the engraved LogoText."),
    ("text", ["logo", "text"], str, "Logo text", "The engraved text itself."),
    ("text_size_mm", ["logo", "text_size_mm"], float, "Logo text size (mm)", ""),
    ("text_spacing", ["logo", "text_spacing"], float, "Logo char spacing (deg)", "Angular spacing between logo characters."),
    ("position_offset_deg", ["logo", "position_offset_deg"], float, "Logo position offset (deg)", ""),
    ("text_offset_deg", ["logo", "text_offset_deg"], float, "Logo text offset (deg)", ""),
    ("outer_inset_mm", ["logo", "outer_inset_mm"], float, "Logo inset from outer radius (mm)",
     "Placement radius = outer radius - this."),
]

# Per-slot draft clipping - offered only for the machines that actually
# implement it: the cylinder family (cylinder_machine._clip_to_cell, via
# TextRing) and the Hammond Split shuttle (its own from-scratch
# TextAssemble loop). NOT offered to the slug family, which strikes one
# character per element and so has no neighbouring slot to leak into, nor
# to the Selectrics, whose ball spaces characters far enough apart that it
# never bites. The config key and the geometry ARE wired for those too, so
# behavior stays uniform fleet-wide - only the checkbox is withheld, per
# explicit user direction to expose it for cylinder and shuttle.
CLIP_TO_CELL_FIELD = (
    "clip_to_cell", ["build", "clip_to_cell"], bool, "Clip draft to slot",
    "Trims each character's Minkowski draft skirt at its own slot boundary so it "
    "cannot bleed into the neighbouring character. Leave off for a plain element "
    "where the merged skirts stay buried in the wall anyway.")

# SECTIONS_COMMON's Font & Alignment plus the two features only the
# cylinder family and Hammond implement: a secondary font (font2:) and
# per-slot draft clipping. Deliberately NOT in SECTIONS_COMMON - the
# slug family shares that table and has neither, and a field whose
# config path does not exist raises rather than degrading.
QUALITY_FIELDS_BLICKPOSTAL = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float, "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block itself, before the Minkowski sum. Its top is the strike face. Small = the block floats just above the cylinder surface."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float, "Minkowski cone height (mm)",
     "Height of the draft cone, added BELOW the glyph block - this is what sinks the character into the cylinder. Total depth is glyph height + cone height."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("body_fn", ["quality", "body_fn"], int, "Body fn", "Main cosmetic cylinder body (Cylinder/ClipCylinder)."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Inner shaft/core bore only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowSpace, SpeedHoles, chamfers...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
    ("notch_fn", ["quality", "notch_fn"], int, "Notch fn",
     "Facet count for the notch groove cutter (notched wheel style only). A sub-millimetre score line does not need the body's own facet count - lower it freely."),
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
    CLIP_TO_CELL_FIELD,
]

# Shared by every machine's Resin tab - lib/overhang.py reads the same
# key for all of them, so one definition rather than nine copies.
OVERHANG_WARN_FIELD = ("overhang_warn_deg", ["resin", "overhang_warn_deg"], float, "Overhang warning (deg)",
                       "The build log flags downward faces, and Selectric glyph rows, shallower than this above horizontal.")

RESIN_FIELDS_BLICKPOSTAL = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("min_rod_height", ["resin", "min_rod_height"], float, "Min rod height (mm)", ""),
    ("raft_od", ["resin", "raft_od"], float, "Raft OD (mm)", ""),
    ("raft_thickness", ["resin", "raft_thickness"], float, "Raft thickness (mm)", ""),
    ("groove_od", ["resin", "groove_od"], float, "Groove OD (mm)", ""),
    ("groove_thickness", ["resin", "groove_thickness"], float, "Groove thickness (mm)", ""),
    ("raft", ["resin", "raft"], bool, "Continuous raft",
     "Off: each rod grows its own small raft. On: one continuous raft "
     "plate shared by every rod, reaching the element's center axis."),
    ("bottom_support_inner_angle_offset", ["resin", "bottom_support_inner_angle_offset"], float,
     "Bottom support angle offset (deg)", ""),
    OVERHANG_WARN_FIELD,
]

GAUGE_FIELDS = [
    # keys must be the literal YAML key names (patch_yaml_value matches
    # by bare key, not the full path) - confirmed no collision with any
    # other field in the file
    ("offset_start", ["gauge", "offset_start"], float, "Offset start (mm)",
     "First pocket's core_id_offset value - usually 0."),
    ("offset_int", ["gauge", "offset_int"], float, "Offset increment (mm)",
     "Added per pocket - pocket n tests offset_start + n*offset_int."),
]

# Mignon-specific tabs - see lib/mignon.py's module docstring for why
# these can't share Blickensderfer/Postal's field lists.
LOGO_FIELDS_MIGNON = [
    ("font_path", ["logo", "font_path"], str, "Logo font path", "Font for the engraved ElementLogo."),
    ("text", ["logo", "text"], str, "Logo text", "The engraved text itself."),
    ("text_size_mm", ["logo", "text_size_mm"], float, "Logo text size (mm)", ""),
    ("text_spacing", ["logo", "text_spacing"], float, "Logo char spacing (deg)", "Angular spacing between logo characters."),
    ("position_offset_deg", ["logo", "position_offset_deg"], float, "Logo position offset (deg)",
     "The Label tab's own text always sits 180 degrees opposite this "
     "value - moving Logo also moves Label."),
    ("height_offset_mm", ["logo", "height_offset_mm"], float, "Logo height offset (mm)",
     "Local nudge off the curved chamfer the logo sits on (not "
     "Blickensderfer/Postal's flat-face radial offset). Since the text "
     "panel is flat but the chamfer is curved, characters away from "
     "center stay partly embedded unless text_depth_mm below is also "
     "increased."),
    ("text_depth_mm", ["logo", "text_depth_mm"], float, "Logo extrusion depth (mm)",
     "How far the raised text extends - thicker is more visible and more "
     "forgiving of the chamfer's curvature clipping it. v2's real value: "
     "a thin 0.09mm."),
    ("minkowski_text", ["logo", "minkowski_text"], bool, "Minkowski text",
     "Draft-cone taper for BOTH Logo and Label text (not a v2 option) - "
     "uses the same draft_angle_deg/minkowski_fn as "
     "struck characters. Off: plain flat extrude (fast)."),
]

# Label: not a v2 concept - a second engraved-text feature, own tab, same
# field format as Logo above, always placed 180 degrees opposite it (no
# position_offset_deg field here - it's derived, see Logo's help text
# above and lib/mignon.py's configure()). Keys prefixed label_* since
# "font_path"/"text"/etc. above are already taken by Logo's own fields
# (self.inputs keys must be unique within one machine's field set) - AND
# the actual config/mignon.yaml keys are also prefixed label_*, not just
# these internal field keys: patch_yaml_value matches by bare key TEXT
# across the whole file, not by section, so identical YAML key names
# under logo:/label: would collide and patch the wrong one.
LABEL_FIELDS_MIGNON = [
    ("label_font_path", ["label", "label_font_path"], str, "Label font path", "Font for the engraved ElementLabel."),
    ("label_text", ["label", "label_text"], str, "Label text", "The engraved text itself."),
    ("label_text_size_mm", ["label", "label_text_size_mm"], float, "Label text size (mm)", ""),
    ("label_text_spacing", ["label", "label_text_spacing"], float, "Label char spacing (deg)", "Angular spacing between label characters."),
    ("label_height_offset_mm", ["label", "label_height_offset_mm"], float, "Label height offset (mm)",
     "Local nudge off the curved chamfer the label sits on - see Logo's "
     "height_offset_mm; label_text_depth_mm below usually needs "
     "increasing together with this."),
    ("label_text_depth_mm", ["label", "label_text_depth_mm"], float, "Label extrusion depth (mm)",
     "How far the raised text extends - thicker is more visible and more "
     "forgiving of the chamfer's curvature clipping it. v2's real value: "
     "a thin 0.09mm."),
]

# lib/mignon_legend.py's flat 2D SVG reference card (see its module
# docstring - a v1/Mignon/MignonIndex.scad port, unrelated to the 3D
# element above). legend_height_offset_mm/legend_flatness_tolerance_mm
# are renamed from the bare height_offset_mm/flatness_tolerance_mm the
# YAML comments describe them as ported from - patch_yaml_value matches
# by bare key text across the WHOLE file, and logo.height_offset_mm/
# build.flatness_tolerance_mm already own those literal names (same
# collision label_*/GAUGE_FIELDS already had to avoid - see those
# fields' own comments). The 3 fill-pattern arrays (legend.circle_fill/
# background_fill/solid_fill) and legend.height_offset_groups are
# deliberately NOT exposed here (list/nested-dict values, don't fit this
# generic scalar mechanism - edit them directly in the YAML, same
# treatment as layout.placement_map/char_legend).
LEGEND_FIELDS_MIGNON = [
    # legend_font_path, not the bare font_path every other font field
    # here uses - Mignon's own Logo tab (LOGO_FIELDS_MIGNON above)
    # already owns that key, both as this file's self.inputs dict key
    # and as patch_yaml_value's bare-text-matched YAML key - see the
    # LABEL_FIELDS_MIGNON comment above for the exact same collision
    # already worked around once.
    ("legend_font_path", ["legend", "legend_font_path"], str, "Legend font path",
     "Independent of the Font tab's font - the legend is a laser-cut/printed card, not the 3D element."),
    ("length_mm", ["legend", "length_mm"], float, "Card length (mm)", ""),
    ("width_mm", ["legend", "width_mm"], float, "Card width (mm)", ""),
    ("corner_radius_mm", ["legend", "corner_radius_mm"], float, "Corner radius (mm)", ""),
    ("edge_to_column_mm", ["legend", "edge_to_column_mm"], float, "Edge to column center (mm)", ""),
    ("edge_to_row_mm", ["legend", "edge_to_row_mm"], float, "Edge to row center (mm)", ""),
    ("circle_diameter_mm", ["legend", "circle_diameter_mm"], float, "Circle diameter (mm)", ""),
    ("circle_height_bump_mm", ["legend", "circle_height_bump_mm"], float, "Circle height bump (mm)",
     "Every circle/ellipse is squished taller than wide by this much extra."),
    ("line_width_mm", ["legend", "line_width_mm"], float, "Ring/border line width (mm)", ""),
    ("checker", ["legend", "checker"], bool, "Checkerboard border", "Slow decorative fill - off by default, matching v1."),
    ("square_pattern_size_mm", ["legend", "square_pattern_size_mm"], float, "Checker square size (mm)", "Checkerboard border only."),
    ("square_pattern_pitch_mm", ["legend", "square_pattern_pitch_mm"], float, "Checker square pitch (mm)", "Checkerboard border only."),
    ("type_size_mm", ["legend", "type_size_mm"], float, "Character size (mm)",
     "A paper/laser-cut card, unrelated to the Font tab's engraved-element size."),
    ("legend_height_offset_mm", ["legend", "legend_height_offset_mm"], float, "Circle center to baseline (mm)", ""),
    ("weight_adjustment_mm", ["legend", "weight_adjustment_mm"], float, "Character bolding (mm)",
     "Plain outline buffer, positive=bolder, negative=thinner, 0=off. "
     "Replaces v1's own self-contradictory/no-op-by-default bolding knob."),
    ("circle_segments", ["legend", "circle_segments"], int, "Circle segments", ""),
    ("legend_flatness_tolerance_mm", ["legend", "legend_flatness_tolerance_mm"], float, "Glyph outline tolerance (mm)", ""),
    ("inner_border", ["legend", "inner_border"], bool, "Inner border",
     "Draws an explicit border around the interior circle grid (v1's own "
     "LiningRectangle() - real geometry, but dead code in v1's actual "
     "output, off by default here too)."),
]

QUALITY_FIELDS_MIGNON = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float, "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block itself, before the Minkowski sum. Its top is the strike face. Small = the block floats just above the cylinder surface."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float, "Minkowski cone height (mm)",
     "Height of the draft cone, added BELOW the glyph block - this is what sinks the character into the cylinder. Total depth is glyph height + cone height."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "CenterShaft only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "HollowBody/ElementChamfer/MinkCleanup."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
    CLIP_TO_CELL_FIELD,
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
]

RESIN_FIELDS_MIGNON = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("min_rod_height", ["resin", "min_rod_height"], float, "Min rod height (mm)", ""),
    ("support_height", ["resin", "support_height"], float, "Support height (mm)",
     "Raft ring's Z offset below the element, and the outer ring of rods' base height."),
    ("support_thickness", ["resin", "support_thickness"], float, "Support thickness (mm)", "Raft ring thickness."),
    ("rod_count", ["resin", "rod_count"], int, "Rod count",
     "Number of evenly-spaced rods around the support ring, either print orientation (see the Build "
     "tab's Print orientation). Upside down also adds half this many more, on alternating sectors, at "
     "a second radius near the top boss."),
    OVERHANG_WARN_FIELD,
]

ELEMENT_FIELDS_MIGNON = [
    ("element_diameter", ["element", "element_diameter"], float, "Element diameter (mm)", ""),
    ("platen_diameter", ["element", "platen_diameter"], float, "Platen diameter (mm)", ""),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final char diameter (mm)", "Char_Protrusion = (this - element_diameter)/2."),
    ("element_height", ["element", "element_height"], float, "Base element height (mm)",
     "Cylinder_Height_ - the untallened height. Actual built height adds "
     "height_increase_mm below when Tallen is on."),
    ("tallen", ["element", "tallen"], bool, "Tallen (Plakatschrift)",
     "Display-type variant: adds height_increase_mm to element height and "
     "shifts every baseline row by tallen_baseline_offset_mm. Cutout rows "
     "are unaffected. Off for a standard element."),
    ("height_increase_mm", ["element", "height_increase_mm"], float, "Tallen height increase (mm)",
     "Added to base element height when Tallen is on."),
    ("tallen_baseline_offset_mm", ["element", "tallen_baseline_offset_mm"], float, "Tallen baseline offset (mm)",
     "Added to every baseline row when Tallen is on."),
    ("cylinder_top_height_offset", ["element", "cylinder_top_height_offset"], float, "Top height offset (mm)", ""),
    ("cylinder_top_chamfer", ["element", "cylinder_top_chamfer"], float, "Top chamfer size (mm)", ""),
    ("cylinder_top_diameter", ["element", "cylinder_top_diameter"], float, "Top diameter (mm)", ""),
    ("cylinder_top_shaft_diameter", ["element", "cylinder_top_shaft_diameter"], float, "Top shaft diameter (mm)", ""),
    ("cylinder_bottom_shaft_diameter", ["element", "cylinder_bottom_shaft_diameter"], float, "Bottom shaft diameter (mm)", ""),
    ("pin_height", ["element", "pin_height"], float, "Alignment pin height (mm)", ""),
    ("pin_width", ["element", "pin_width"], float, "Alignment pin width (mm)", ""),
    ("pin_depth", ["element", "pin_depth"], float, "Alignment pin depth (mm)", ""),
    ("pin_through", ["element", "pin_through"], bool, "Pin all the way through", ""),
    ("cylinder_shape", ["element", "cylinder_shape"], int, "Body shape", "0=Polygonal (12-gon), 1=Cylindrical."),
]

# Bennett-specific tabs - see lib/bennett.py's module docstring for why
# these can't share Blickensderfer/Postal/Mignon's field lists. Bennett's
# only engraved-text feature (LabelText - two independent flat whole-
# string groups cut into the bottom face, not a ring of individually
# angle-placed characters) has no text_spacing/position_offset_deg/
# outer_inset_mm concept at all, so it gets its own "Label" tab (not
# "Logo") matching v2's own Shuttle_Label naming and config/bennett.yaml's
# `label:` section.
LABEL_FIELDS_BENNETT = [
    ("font_path", ["label", "font_path"], str, "Label font path", "Font for the engraved LabelText."),
    ("label1a", ["label", "label1a"], str, "Label 1a (top line, right group)", "Shuttle_Label1a - e.g. a first name."),
    ("label1b", ["label", "label1b"], str, "Label 1b (bottom line, right group)", "Shuttle_Label1b - e.g. a last name."),
    ("label2", ["label", "label2"], str, "Label 2 (left group)", "Shuttle_Label2 - e.g. a year."),
    ("label_size_mm", ["label", "label_size_mm"], float, "Label text size (mm)", ""),
    ("depth_mm", ["label", "depth_mm"], float, "Label depth offset (mm)", "Added to Bottom_Countersink_Depth for the cut's Z start."),
    ("label1a_radial_mm", ["label", "label1a_radial_mm"], float, "Label 1a radial distance (mm)",
     "World-X distance of label1a's text from the shaft center. Independent of label1b/label2 - see LabelText()'s docstring."),
    ("label1b_radial_mm", ["label", "label1b_radial_mm"], float, "Label 1b radial distance (mm)",
     "World-X distance of label1b's text from the shaft center. Independent of label1a/label2 - see LabelText()'s docstring."),
    ("label2_radial_mm", ["label", "label2_radial_mm"], float, "Label 2 radial distance (mm)",
     "World-X distance of label2's text from the shaft center (negative = opposite side from label1a/1b)."),
]

QUALITY_FIELDS_BENNETT = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float, "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block itself, before the Minkowski sum. Its top is the strike face. Small = the block floats just above the cylinder surface."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float, "Minkowski cone height (mm)",
     "Height of the draft cone, added BELOW the glyph block - this is what sinks the character into the cylinder. Total depth is glyph height + cone height."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft/pin fn", "PositionerPins/CenterShaft."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowBody, SpeedHoles, countersinks...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("alignment_hole_fn", ["quality", "alignment_hole_fn"], int, "Alignment hole fn", "AlignmentHoles facet count."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
    CLIP_TO_CELL_FIELD,
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
]

RESIN_FIELDS_BENNETT = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("raft_od", ["resin", "raft_od"], float, "Raft OD (mm)", ""),
    ("support_height", ["resin", "support_height"], float, "Support height (mm)",
     "Ring/raft Z offset below the element, and every rod's base height."),
    ("support_thickness", ["resin", "support_thickness"], float, "Support thickness (mm)",
     "Also doubles as the per-rod raft frustum's thickness (Resin_Raft_Thickness)."),
    ("cut_groove_diameter", ["resin", "cut_groove_diameter"], float, "Cut groove diameter (mm)", ""),
    ("cut_groove_thickness", ["resin", "cut_groove_thickness"], float, "Cut groove thickness (mm)", ""),
    OVERHANG_WARN_FIELD,
]

# alignment_hole_height (3 values, per-row - like baseline_row/cutout_row)
# is NOT exposed here - patch_yaml_value/self.FIELDS only handle scalar
# values, and baseline_row/cutout_row's per-row widgets are bespoke to
# those two keys (see TuneApp._compose_baseline_cutout_fields) - edit it
# directly in the YAML if you need to change it, same as placement_map.
ELEMENT_FIELDS_BENNETT = [
    ("element_diameter", ["element", "element_diameter"], float, "Element diameter (mm)", ""),
    ("platen_diameter", ["element", "platen_diameter"], float, "Platen diameter (mm)", ""),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final char diameter (mm)", "Char_Protrusion = (this - element_diameter)/2."),
    ("element_height", ["element", "element_height"], float, "Element height (mm)", ""),
    ("shaft_diameter", ["element", "shaft_diameter"], float, "Shaft diameter (mm)", ""),
    ("positioner_pin_diameter", ["element", "positioner_pin_diameter"], float, "Positioner pin diameter (mm)", ""),
    ("positioner_pin_radius", ["element", "positioner_pin_radius"], float, "Positioner pin radius (mm)", ""),
    ("indicator_diameter", ["element", "indicator_diameter"], float, "Indicator hole diameter (mm)", ""),
    ("alignment_hole_diameter", ["element", "alignment_hole_diameter"], float, "Alignment hole diameter (mm)", ""),
    ("alignment_hole_depth", ["element", "alignment_hole_depth"], float, "Alignment hole depth (mm)", ""),
    ("alignment_hole_chamfer", ["element", "alignment_hole_chamfer"], float, "Alignment hole chamfer (mm)", ""),
    ("speed_hole_diameter", ["element", "speed_hole_diameter"], float, "Speed hole diameter (mm)", ""),
    ("speed_hole_radius", ["element", "speed_hole_radius"], float, "Speed hole radial (mm)", ""),
    ("speed_hole_quantity", ["element", "speed_hole_quantity"], int, "Speed hole qty", ""),
    ("countersink_diameter", ["element", "countersink_diameter"], float, "Countersink diameter (mm)", ""),
    ("top_countersink_depth", ["element", "top_countersink_depth"], float, "Top countersink depth (mm)", ""),
    ("bottom_countersink_depth", ["element", "bottom_countersink_depth"], float, "Bottom countersink depth (mm)", ""),
    ("shell_size", ["element", "shell_size"], float, "Shell size (mm)", "Minimum cylinder wall thickness."),
    ("core_groove_qty", ["element", "core_groove_qty"], int, "Core groove qty", ""),
    ("core_groove_d", ["element", "core_groove_d"], float, "Core groove depth (mm)", ""),
    ("core_chamfer", ["element", "core_chamfer"], float, "Core chamfer (mm)", ""),
    ("core_bottom_offset", ["element", "core_bottom_offset"], float, "Core bottom offset (mm)", ""),
    ("core_contact_length", ["element", "core_contact_length"], float, "Core contact length (mm)", ""),
    ("core_web_width", ["element", "core_web_width"], float, "Core web width (mm)", ""),
    ("core_web_qty", ["element", "core_web_qty"], int, "Core web qty", ""),
    ("core_web_length", ["element", "core_web_length"], float, "Core web length (mm)", ""),
]

# Helios-specific tabs - see lib/helios.py's module docstring for why
# these can't share any other machine's field lists. No "Label" key (v2
# has no engraved-TEXT feature - v2's own header: "Sections with no
# Helios equivalent (Logo, Print Tolerances, Shaft Gauge Test) are
# omitted"), no "Gauge" key (same reason). "Logo" IS present below -
# unlike v2, v1's separate SVG_Logo mark (an imported vector image, not
# engraved text) was ported as a deliberate v1-sourced addition - see
# LOGO_FIELDS_HELIOS and config/helios.yaml's logo: section.
QUALITY_FIELDS_HELIOS = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float, "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block itself, before the Minkowski sum. Its top is the strike face. Small = the block floats just above the cylinder surface."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float, "Minkowski cone height (mm)",
     "Height of the draft cone, added BELOW the glyph block - this is what sinks the character into the cylinder. Total depth is glyph height + cone height."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves",
     "16 twisted friction grooves (v4-only, see the core_shaft note on the Element tab) - slow, off for quick iteration."),
    # cyl_fn is now genuinely used (Core()'s shaft-bore facet count, via
    # the v4-only core_shaft reuse - see config/helios.yaml's element
    # section comment) - previously declared-but-unused.
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Core() shaft-bore facet count."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Every other cylinder/revolve in the body (HollowingElement, MinkCleanup, clip...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
    CLIP_TO_CELL_FIELD,
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
]

# v2's own header comment: "the original file declares Resin_Support/
# Resin_Support_* parameters but never actually generates any resin
# support geometry with them" - preserved as declared-but-unused, same as
# v2 itself (its Customizer showed these fields too, despite nothing ever
# reading them) - lib/helios.py's ResinPrint() is a no-op alias to
# FullElement() regardless of these values, see its docstring.
RESIN_FIELDS_HELIOS = [
    ("resin_support_base_thickness", ["resin", "resin_support_base_thickness"], float,
     "Support base thickness (mm)", "Declared but not wired to any geometry - see lib/helios.py's ResinPrint()."),
    ("resin_support_rod_thickness", ["resin", "resin_support_rod_thickness"], float,
     "Support rod thickness (mm)", "Declared but not wired to any geometry - see lib/helios.py's ResinPrint()."),
    ("resin_support_min_height", ["resin", "resin_support_min_height"], float,
     "Support min height (mm)", "Declared but not wired to any geometry - see lib/helios.py's ResinPrint()."),
    ("resin_support_spacing", ["resin", "resin_support_spacing"], float,
     "Support spacing (mm)", "Declared but not wired to any geometry - see lib/helios.py's ResinPrint()."),
    ("resin_support_contact_radius", ["resin", "resin_support_contact_radius"], float,
     "Support contact radius (mm)", "Declared but not wired to any geometry - see lib/helios.py's ResinPrint()."),
    OVERHANG_WARN_FIELD,
]

LOGO_FIELDS_HELIOS = [
    ("logo_enabled", ["logo", "logo_enabled"], bool, "SVG logo enabled",
     "v1's SVG_Logo mark, cut into the top face - defaults off, see config/helios.yaml's logo: section for why."),
    ("svg_file", ["logo", "svg_file"], str, "Logo SVG file", ""),
    ("scale_mm_per_unit", ["logo", "scale_mm_per_unit"], float, "Logo scale (mm per SVG unit)",
     "v4-only knob - see lib/svg_import.py's module docstring for why this isn't a port of v1's own SVG_Scale."),
    ("logo_depth_mm", ["logo", "logo_depth_mm"], float, "Logo engraving depth (mm)", "v1 Element_Label_Depth."),
    ("x_offset_mm", ["logo", "x_offset_mm"], float, "Logo X offset (mm)", "v1's fixed translate([x_offset,0,...])."),
]

ELEMENT_FIELDS_HELIOS = [
    ("element_diameter", ["element", "element_diameter"], float, "Element diameter (mm)", ""),
    ("platen_diameter", ["element", "platen_diameter"], float, "Platen diameter (mm)", ""),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final char diameter (mm)", "Char_Protrusion = (this - element_diameter)/2."),
    ("element_height", ["element", "element_height"], float, "Element height (mm)", ""),
    ("shaft_diameter", ["element", "shaft_diameter"], float, "Shaft diameter (mm)", ""),
    ("element_square_hole_position", ["element", "element_square_hole_position"], float,
     "Alignment pin radial position (mm)", ""),
    ("element_square_hole_width", ["element", "element_square_hole_width"], float, "Alignment pin hole width (mm)", ""),
    ("element_square_hole_length", ["element", "element_square_hole_length"], float, "Alignment pin hole length (mm)", ""),
    ("element_square_hole_support_height", ["element", "element_square_hole_support_height"], float,
     "Alignment pin support height (mm)", ""),
    ("element_indicator_hole_position", ["element", "element_indicator_hole_position"], float,
     "Indicator hole radial position (mm)", ""),
    ("element_indicator_hole_diameter", ["element", "element_indicator_hole_diameter"], float,
     "Indicator hole diameter (mm)", ""),
    ("element_shell_thickness", ["element", "element_shell_thickness"], float, "Shell thickness (mm)", ""),
    ("element_inside_radius", ["element", "element_inside_radius"], float, "Inside corner radius (mm)",
     "HollowingElement()'s hull-circle rounding radius."),
    ("element_clip_height", ["element", "element_clip_height"], float, "Clip retainer height (mm)", ""),
    ("element_clip_diameter", ["element", "element_clip_diameter"], float, "Clip retainer diameter (mm)", ""),
    ("element_wire_diameter", ["element", "element_wire_diameter"], float, "Wire diameter (mm)", ""),
    ("element_clip_bite", ["element", "element_clip_bite"], float, "Clip bite (mm)", ""),
    ("element_clip_angle", ["element", "element_clip_angle"], float, "Clip angle (deg)", ""),
    # core_shaft family (v4-only enhancement, NOT ported from v2 - v2's own
    # Helios had no SecondaryCore/CoreGrooves/CoreChamfer/CoreEllipses at
    # all. Values below are starting estimates scaled from Bennett's
    # config (closest shaft diameter), not real Helios dimensions - see
    # config/helios.yaml's header and lib/helios.py's module docstring.
    ("core_chamfer", ["element", "core_chamfer"], float, "Core chamfer (mm)", "Estimated, not from v2 - see the note above."),
    ("core_bottom_offset", ["element", "core_bottom_offset"], float, "Core bottom offset (mm)", "Estimated, not from v2 - see the note above."),
    ("core_contact_length", ["element", "core_contact_length"], float, "Core contact length (mm)", "Estimated, not from v2 - see the note above."),
    ("core_web_width", ["element", "core_web_width"], float, "Core web width (mm)", "Estimated, not from v2 - see the note above."),
    ("core_web_qty", ["element", "core_web_qty"], int, "Core web qty", "Estimated, not from v2 - see the note above."),
    ("core_web_length", ["element", "core_web_length"], float, "Core web length (mm)", "Estimated, not from v2 - see the note above."),
    ("core_groove_qty", ["element", "core_groove_qty"], int, "Core groove qty", "Estimated, not from v2 - see the note above."),
    ("core_groove_d", ["element", "core_groove_d"], float, "Core groove depth (mm)", "Estimated, not from v2 - see the note above."),
]

# Scalar fields that render as a dropdown instead of a free-text Input,
# keyed by field name: {field key: [(display label, stored value), ...]}.
# Stored values are always STRINGS (Select's own value type); the field's
# declared type in its FIELDS entry is what converts back on save, so an
# int-typed field lists "0"/"1" here and round-trips as int. A dict rather
# than an if/elif chain in _compose_section_tab for the same reason
# LAYOUT_PICKER_HELP is one - a new dropdown field should mean one entry
# here, not another branch (see CLAUDE.md's "Pick one convention").
SELECT_FIELD_OPTIONS = {
    "mode": [("center", "center"), ("left", "left")],
    "drive_pin_style": [("Later (rectangular pin)", "0"), ("Early (radial slot)", "1")],
    "wheel_style": [("Round", "round"), ("Notched", "notched"), ("Banded", "banded")],
}

ELEMENT_FIELDS_BLICKENSDERFER = [
    ("element_diameter", ["element", "element_diameter"], float, "Element diameter (mm)", ""),
    ("platen_diameter", ["element", "platen_diameter"], float, "Platen diameter (mm)", "Real platen cylinder diameter."),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final char diameter (mm)", "Char_Protrusion = (this - element_diameter)/2."),
    ("element_height", ["element", "element_height"], float, "Element height (mm)", ""),
    ("wall_min_thickness", ["element", "wall_min_thickness"], float, "Wall min thickness (mm)", ""),
    ("wall_chamfer", ["element", "wall_chamfer"], float, "Wall chamfer (mm)", ""),
    ("roof_offset", ["element", "roof_offset"], float, "Roof offset (mm)", ""),
    ("speed_hole_id", ["element", "speed_hole_id"], float, "Speed hole ID (mm)", ""),
    ("speed_hole_qty", ["element", "speed_hole_qty"], int, "Speed hole qty", ""),
    ("speed_hole_radial", ["element", "speed_hole_radial"], float, "Speed hole radial (mm)", ""),
    ("core_id_in", ["element", "core_id_in"], float, "Core ID (in)", "Core_ID_Mm = this * 25.4."),
    ("core_groove_qty", ["element", "core_groove_qty"], int, "Core groove qty", ""),
    ("core_groove_d", ["element", "core_groove_d"], float, "Core groove depth (mm)", ""),
    ("core_chamfer", ["element", "core_chamfer"], float, "Core chamfer (mm)", ""),
    ("core_bottom_offset", ["element", "core_bottom_offset"], float, "Core bottom offset (mm)", ""),
    ("core_contact_length", ["element", "core_contact_length"], float, "Core contact length (mm)", ""),
    ("core_web_width", ["element", "core_web_width"], float, "Core web width (mm)", ""),
    ("core_web_qty", ["element", "core_web_qty"], int, "Core web qty", ""),
    ("core_web_length", ["element", "core_web_length"], float, "Core web length (mm)", ""),
    ("clip_height", ["element", "clip_height"], float, "Clip height (mm)", ""),
    ("clip_wire_od", ["element", "clip_wire_od"], float, "Clip wire OD (mm)", ""),
    ("clip_opening", ["element", "clip_opening"], float, "Clip opening (mm)", ""),
    ("clip_bite", ["element", "clip_bite"], float, "Clip bite (mm)", ""),
    ("drive_pin_widthmm", ["element", "drive_pin_widthmm"], float, "Drive pin width (mm)", ""),
    ("drive_pin_length", ["element", "drive_pin_length"], float, "Drive pin length (mm)", ""),
    ("drive_pin_radial", ["element", "drive_pin_radial"], float, "Drive pin radial (mm)", ""),
    ("drive_pin_countersink_depth", ["element", "drive_pin_countersink_depth"], float,
     "Drive pin countersink depth (mm)", ""),
    ("drive_pin_support_radial_offset", ["element", "drive_pin_support_radial_offset"], float,
     "Drive pin support radial offset (mm)", ""),
    ("drive_pin_support_height", ["element", "drive_pin_support_height"], float,
     "Drive pin support height (mm)", ""),
    ("drive_pin_style", ["element", "drive_pin_style"], int, "Drive pin style",
     "Which drive fitting the element is cut for. Later is a rectangular pin; Early is a radial slot. Changes the pin cut, the countersink support boss and the resin drive-pin support together."),
    ("drive_pin_width_oldmm", ["element", "drive_pin_width_oldmm"], float, "Early slot width (mm)",
     "Only used when Drive pin style is Early. Before the width offset below is added."),
    ("drive_pin_length_old", ["element", "drive_pin_length_old"], float, "Early slot length (mm)",
     "Only used when Drive pin style is Early. Doubles as the countersink diameter."),
    ("drive_pin_length_start_old", ["element", "drive_pin_length_start_old"], float, "Early slot inner radius (mm)",
     "Only used when Drive pin style is Early. The slot's inner end; its radial centre is this plus half the length."),
    ("core_id_offset", ["element", "core_id_offset"], float, "Core ID offset (mm)", "Print-tolerance addition."),
    ("drive_pin_width_offset", ["element", "drive_pin_width_offset"], float, "Drive pin width offset (mm)", ""),
]

# Postal has no drive-pin countersink at all (lib/postal.py's HollowSpace/
# DrivePin/ResinSupport) - no drive_pin_countersink_depth/
# drive_pin_support_radial_offset/drive_pin_support_height/drive_pin_style
# keys in its config, and it reuses core_id_offset directly in place of a
# dedicated drive_pin_width_offset (see lib/postal.py's configure()).
ELEMENT_FIELDS_POSTAL = [
    f for f in ELEMENT_FIELDS_BLICKENSDERFER
    if f[0] not in ("drive_pin_countersink_depth", "drive_pin_support_radial_offset",
                     "drive_pin_support_height", "drive_pin_style", "drive_pin_width_offset",
                     "drive_pin_width_oldmm", "drive_pin_length_old", "drive_pin_length_start_old")
]

LABEL_FIELDS_HAMMOND = [
    ("font_path", ["label", "font_path"], str, "Label font path", "Font for the two engraved Shuttle_Label strings."),
    ("label1", ["label", "label1"], str, "Label 1", "Shuttle_Label1 - e.g. a name."),
    ("label2", ["label", "label2"], str, "Label 2", "Shuttle_Label2 - e.g. a year."),
    ("label_size_mm", ["label", "label_size_mm"], float, "Label text size (mm)", ""),
    ("depth_mm", ["label", "depth_mm"], float, "Label depth (mm)", "Shuttle_Label_Depth."),
]

# lib/hammond_legend.py's flat 2D SVG reference card (see its module
# docstring - a v1/Hammond/HammondIndex.scad port, unrelated to the 3D
# shuttle above). Shared as-is by both "hammond" and "hammond_split" (see
# SECTIONS_BY_MACHINE) - same field set, same lib/hammond_legend.py
# module, just a different config's layout.rows/legend: values.
# legend_flatness_tolerance_mm is renamed from the bare
# flatness_tolerance_mm QUALITY_FIELDS_HAMMOND below already owns (same
# global-bare-key-text collision LABEL_FIELDS_MIGNON's own comment
# explains) - every other key here has no such collision.
LEGEND_FIELDS_HAMMOND = [
    # legend_font_path, not bare font_path - both Hammond's and Hammond
    # Split's own Label tab (LABEL_FIELDS_HAMMOND/LABEL_FIELDS_HAMMOND_
    # SPLIT) already own that key, same collision LEGEND_FIELDS_MIGNON's
    # own comment explains.
    ("legend_font_path", ["legend", "legend_font_path"], str, "Legend font path",
     "Independent of the Font tab's font - the legend is a laser-cut/printed card, not the 3D element."),
    ("qp_length_mm", ["legend", "qp_length_mm"], float, "Q-to-P span (mm)", "Top row, real measured key-to-key distance."),
    ("a_colon_length_mm", ["legend", "a_colon_length_mm"], float, "A-to-: span (mm)", "Middle row, real measured key-to-key distance."),
    ("z_exclamation_length_mm", ["legend", "z_exclamation_length_mm"], float, "Z-to-! span (mm)", "Bottom row, real measured key-to-key distance."),
    ("row_separation_mm", ["legend", "row_separation_mm"], float, "Row pitch (mm)", "Vertical spacing, both Q<->A and A<->Z."),
    ("left_margin_mm", ["legend", "left_margin_mm"], float, "Left margin (mm)", "Card's left edge to the shared Q/A/Z start column - all 3 rows are vertically aligned."),
    ("bottom_margin_mm", ["legend", "bottom_margin_mm"], float, "Bottom margin (mm)", "Card's bottom edge to the Z row."),
    ("card_width_mm", ["legend", "card_width_mm"], float, "Card width (mm)", "Real fixed cut size, not derived from content."),
    ("card_height_mm", ["legend", "card_height_mm"], float, "Card height (mm)", ""),
    ("card_corner_radius_mm", ["legend", "card_corner_radius_mm"], float, "Corner radius (mm)", "Top two corners only - bottom corners stay sharp."),
    ("card_corner_center_y_mm", ["legend", "card_corner_center_y_mm"], float, "Corner arc center height (mm)",
     "Independent measurement, not derived from card height - radius may fall short of the top edge, needing a straight vertical bridge."),
    ("card_border_stroke_mm", ["legend", "card_border_stroke_mm"], float, "Border stroke width (mm)", "The cut outline's SVG stroke width (black)."),
    ("circle_id_mm", ["legend", "circle_id_mm"], float, "Circle diameter (mm)", ""),
    ("circle_thickness_mm", ["legend", "circle_thickness_mm"], float, "Circle ring thickness (mm)", ""),
    ("cap_size_mm", ["legend", "cap_size_mm"], float, "CAP letter size (mm)", "The big central character on each key."),
    ("fig_size_mm", ["legend", "fig_size_mm"], float, "FIG/lowercase char size (mm)",
     "Used for both the small FIG label above and the lowercase/punctuation label below."),
    ("capfig_mod_size_mm", ["legend", "capfig_mod_size_mm"], float, "CAPFIG-mod char size (mm)",
     "Size for a CAP-row character that's actually a symbol (see capfig_mod_chars)."),
    ("fig_offset_mm", ["legend", "fig_offset_mm"], float, "FIG label offset (mm)", "Height above center."),
    ("lowercase_offset_mm", ["legend", "lowercase_offset_mm"], float, "Lowercase label offset (mm)", "Height above center (negative = below)."),
    ("cap_offset_mm", ["legend", "cap_offset_mm"], float, "CAP label offset (mm)", "Height above center (negative = below)."),
    ("fig_dupe_offset_mm", ["legend", "fig_dupe_offset_mm"], float, "FIG-dupe extra offset (mm)",
     "Added to the CAP label's offset when this key's FIG position is blanked (a duplicate marker, see fig_dupe_chars)."),
    ("capfig_offset_mm", ["legend", "capfig_offset_mm"], float, "CAPFIG-mod offset (mm)",
     "Used instead of the normal CAP offset when this key's CAP position is actually a symbol."),
    ("capfig_mod_chars", ["legend", "capfig_mod_chars"], str, "CAPFIG-mod characters",
     "CAP-row characters treated as symbols (smaller size, different vertical offset) rather than real letters."),
    ("lowercase_mod_chars", ["legend", "lowercase_mod_chars"], str, "Lowercase-mod characters",
     "The only lowercase-row characters actually drawn as a separate small label - everything else in that row is blank (redundant with the CAP letter above it)."),
    ("fig_dupe_chars", ["legend", "fig_dupe_chars"], str, "FIG-dupe characters",
     "FIG-row characters treated as a blank placeholder rather than a real character."),
    ("circle_segments", ["legend", "circle_segments"], int, "Circle segments", ""),
    ("legend_flatness_tolerance_mm", ["legend", "legend_flatness_tolerance_mm"], float, "Glyph outline tolerance (mm)", ""),
]

QUALITY_FIELDS_HAMMOND = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float, "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block itself, before the Minkowski sum. Its top is the strike face. Small = the block floats just above the cylinder surface."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float, "Minkowski cone height (mm)",
     "Height of the draft cone, added BELOW the glyph block - this is what sinks the character into the cylinder. Total depth is glyph height + cone height."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Shuttle arc body (ShuttleCylinder/Rib/PinSupport)."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Mirrors cyl_fn - no separate structural tier."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
    CLIP_TO_CELL_FIELD,
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
]

RESIN_FIELDS_HAMMOND = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("min_rod_height", ["resin", "min_rod_height"], float, "Min rod height (mm)", ""),
    ("raft_thickness", ["resin", "raft_thickness"], float, "Raft thickness (mm)", ""),
    ("raft_od", ["resin", "raft_od"], float, "Raft OD (mm)", ""),
    ("spacing", ["resin", "spacing"], float, "Support grid spacing (mm)",
     "Rod pitch (vertical: real theta step along the arc; horizontal: raycast grid pitch)."),
    ("edge_gap", ["resin", "edge_gap"], float, "Edge gap (mm)", "Resin_Support_Edge_Gap - only used for vertical orientation."),
    # "orientation"/"horizontal_method" used to live here as generic FIELDS
    # Selects - moved to the Build tab (see _compose_build_tab), above the
    # Debug section, per explicit user request ("maybe Print Orientation
    # and Horizontal Support Method should be moved to Build"). Handled
    # like target/resin_support/groove there - _collect_values/
    # _refresh_widgets_from_cfg read/write #build-orientation/
    # #build-horizontal-method directly instead of going through the
    # generic self.FIELDS loop.
    OVERHANG_WARN_FIELD,
]

ELEMENT_FIELDS_HAMMOND = [
    ("shrinkage_multiplier", ["element", "shrinkage_multiplier"], float, "Arc shrinkage multiplier", "Shuttle_Arc_Radius_Shrinkage_Multiplier."),
    ("anvil_od", ["element", "anvil_od"], float, "Anvil OD (mm)", "Element_Diameter = this * shrinkage_multiplier."),
    ("anvil_id_raw", ["element", "anvil_id_raw"], float, "Anvil ID raw (mm)", ""),
    ("shuttle_thickness", ["element", "shuttle_thickness"], float, "Shuttle thickness (mm)", "Also the glyph placement protrusion."),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final character diameter (mm)",
     "Diameter across two opposing character tips - the same value the cylinder machines use. "
     "Protrusion above the shuttle surface is half the difference from it. No minimum-vs-maximum "
     "here: a flat anvil, so no platen scallop varies it."),
    ("normal_shuttle_height", ["element", "normal_shuttle_height"], float, "Normal shuttle height (mm)", ""),
    ("math_shuttle_height", ["element", "math_shuttle_height"], float, "Math shuttle height (mm)", "Used when is_math=true."),
    ("shuttle_height_offset", ["element", "shuttle_height_offset"], float, "Shuttle height offset (mm)", ""),
    ("shuttle_rib_plane_base", ["element", "shuttle_rib_plane_base"], float, "Rib plane base (mm)", ""),
    ("shuttle_rib_thickness", ["element", "shuttle_rib_thickness"], float, "Rib thickness (mm)", ""),
    ("shuttle_rib_width", ["element", "shuttle_rib_width"], float, "Rib width (mm)", ""),
    ("shuttle_square_hole_offset", ["element", "shuttle_square_hole_offset"], float, "Square hole offset (mm)", ""),
    ("shuttle_square_hole_width", ["element", "shuttle_square_hole_width"], float, "Square hole width (mm)", ""),
    ("shuttle_square_hole_length", ["element", "shuttle_square_hole_length"], float, "Square hole length (mm)", ""),
    ("shuttle_square_hole_radius", ["element", "shuttle_square_hole_radius"], float, "Square hole radius (mm)", ""),
    ("shuttle_pin_support_height", ["element", "shuttle_pin_support_height"], float, "Pin support height (mm)", ""),
    ("shuttle_pin_support_base_width", ["element", "shuttle_pin_support_base_width"], float, "Pin support base width (mm)", ""),
    ("shuttle_pin_support_base_length", ["element", "shuttle_pin_support_base_length"], float, "Pin support base length (mm)", ""),
    ("shuttle_pin_support_height_offset", ["element", "shuttle_pin_support_height_offset"], float, "Pin support height offset (mm)", ""),
    ("shuttle_rib_hump_distance", ["element", "shuttle_rib_hump_distance"], float, "Rib hump distance (mm)", ""),
    ("shuttle_rib_circle", ["element", "shuttle_rib_circle"], float, "Rib circle radius (mm)", ""),
    ("shuttle_rib_circle_radius", ["element", "shuttle_rib_circle_radius"], float, "Rib circle fillet radius (mm)", ""),
    ("shuttle_taper_deg", ["element", "shuttle_taper_deg"], float, "Taper angle (deg)", ""),
    ("shuttle_taper_step", ["element", "shuttle_taper_step"], float, "Taper step (mm)", ""),
    ("angular_span_deg", ["element", "angular_span_deg"], float, "Angular span (deg)", "Angle_Pitch = (this/angular_divisions)/shrinkage_multiplier."),
    ("angular_divisions", ["element", "angular_divisions"], int, "Angular divisions", ""),
    ("rib_fillet_resin_clearance", ["element", "rib_fillet_resin_clearance"], float, "Rib fillet clearance (mm)", ""),
    # "groove" (element.groove, bool) used to live here as a Select ("Rib"/
    # "No Rib (Groove)") - moved to the Build tab as a plain "Rib" checkbox
    # instead (see _compose_build_tab), since that's where the Build
    # target dropdown's None/Shuttle/Calibration Shuttle choice already
    # needs it (None+Rib=on is how you export just the rib alone). Kept
    # out of ELEMENT_FIELDS_HAMMOND/self.FIELDS entirely now - _collect_
    # values/_refresh_widgets_from_cfg handle it explicitly, same as
    # target/resin_support below it.
    ("shuttle_groove_nub_angle", ["element", "shuttle_groove_nub_angle"], float, "Groove nub angle (deg)", "Only used for Build target Shuttle/Rib (the without-rib/groove body and its interface flange)."),
    ("groove_tab_width", ["element", "groove_tab_width"], float, "Groove tab width (mm)", "Only used for Build target Shuttle (the without-rib/groove body's own cut slot - Rib's flange omits the tab, see hammond.py)."),
    ("groove_opening_offset", ["element", "groove_opening_offset"], float, "Groove opening offset (mm)", "Only used for Build target Shuttle (the without-rib/groove body)."),
    ("support_groove_thickness", ["element", "support_groove_thickness"], float, "Resin chamfer thickness (mm)", "Its ResinChamfer() consumer is currently disabled (commented out) - only used by the Resin tab's Cut Groove support method now (unrelated feature, same constant - see config comment)."),
]

# v4-specific "Rib" tab (Hammond only) - FDM print-fit tuning for the
# standalone Build target Rib part (RibOnly()), kept separate from the
# Element tab's real-machine-dimension fields since every value here is
# purely a v4 print-fit knob, not a v2/real-machine number. Every field's
# help text should make clear it only affects Rib-only FDM printing, not
# the fused Shuttle-with-Rib resin print or the Shuttle body itself.
RIB_FIELDS_HAMMOND = [
    ("rib_interface_offset_mm", ["element", "rib_interface_offset_mm"], float, "Interface offset (mm)",
     "FDM print-fit clearance for the Rib-only flange (Build target Rib) - shrinks the "
     "flange (the piece being test-fit into a Shuttle body's cut slot) so it actually slides "
     "in after printing. 0 reproduces the exact nominal/uncompensated fit; increase if the "
     "flange prints too tight for your printer/filament. Only affects Build target Rib."),
    ("rib_nub_growth_mm", ["element", "rib_nub_growth_mm"], float, "Nub clearance growth (mm)",
     "FDM print-fit margin for the Rib-only flange's 4 nub-clearance cutouts, independent of "
     "Interface offset above. Increase if the flange's clearance holes print too tight to "
     "clear the Shuttle's nub geometry. Only affects Build target Rib."),
    ("rib_flat_bottom", ["element", "rib_flat_bottom"], bool, "Flat bottom",
     "Only render the bottom pin support boss, not the top one, so the Rib-only part can be "
     "printed flat on the buildplate with no overhang on the other side. Only affects Build "
     "target Rib."),
]

# Split Hammond 1 Shuttle - a SEPARATE machine from Hammond (see lib/
# hammond_split.py's module docstring). "draft_angle_deg" is replaced by
# TWO fields here (mink_draft_angle_deg + mink_height, not SECTIONS_
# COMMON's single shared draft_angle_deg key) - this machine's real draft
# cone height (Minkowski_Cone_Height) is independent of the character's own
# extrusion depth (Glyph_Height, Element tab), unlike every other
# machine's coupled draft-cone convention (see lib/hammond_split.py's
# _letter_text_drafted() docstring) - so it needs its own second knob.
# Like draft_angle_deg elsewhere, whether the draft actually RUNS is never
# a config toggle (Quick Preview always skips it, Render always applies
# it - see tune.py's _run_build) - only its angle/height are tunable here.
FONT_FIELDS_CYLINDER = (
    SECTIONS_COMMON["Font & Alignment"]
    + [
        ("font2_path", ["font2", "font2_path"], str, "Font 2 path",
         "Secondary font for the characters listed below - blank uses the main font."),
            ("font2_size_mm", ["font2", "font2_size_mm"], float, "Font 2 size (mm)",
         "0 uses the main font size."),
            ("font2_chars", ["font2", "font2_chars"], str, "Font 2 chars",
         "Characters struck in font 2 instead of the main font. Useful where a typewriter face lacks fractions, currency or a whole script."),
    ]
    )

FONT_FIELDS_HAMMOND_SPLIT = [
    ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters (Type_Face)."),
    ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Type_Size - em-square size."),
    ("font2_chars", ["font2", "font2_chars"], str, "Font 2 chars", "v2 Char_Mod - characters that use font 2 instead of the main font."),
    ("font2_path", ["font2", "font2_path"], str, "Font 2 path", "v2 Char_Mod_Font."),
    ("font2_size_mm", ["font2", "font2_size_mm"], float, "Font 2 size (mm)", "v2 Char_Mod_Size."),
    ("mode", ["alignment", "mode"], str, "Align mode", '"center" or "left".'),
    ("center_offset_mm", ["alignment", "center_offset_mm"], float, "Center offset (mm)", ""),
    ("left_offset_mm", ["alignment", "left_offset_mm"], float, "Left offset (mm)", ""),
    ("modified_left_chars", ["alignment", "modified_left_chars"], str, "Modified-left chars", "Chars getting an extra left shift."),
    ("modified_left_offset_mm", ["alignment", "modified_left_offset_mm"], float, "Modified-left offset (mm)", ""),
    ("modified_right_chars", ["alignment", "modified_right_chars"], str, "Modified-right chars", "Chars getting an extra right shift."),
    ("modified_right_offset_mm", ["alignment", "modified_right_offset_mm"], float, "Modified-right offset (mm)", ""),
    ("caret_auto_raise", ["alignment", "caret_auto_raise"], bool, "Auto-raise caret",
     "Puts the top of \"^\" on the font's cap height (the top of its capitals, from the font's own data) - the raised caret typewriters had. Caret raise below adds to it."),
    ("caret_raise_mm", ["alignment", "caret_raise_mm"], float, "Caret raise (mm)",
     "Moves \"^\" up (negative = down), on top of auto-raise if that is on. Fonts draw U+005E wherever their circumflex accent sits, which rarely matches a typewriter face; a Blickensderfer caret on the baseline is about -0.6 x the font size."),
    DRAFT_ANGLE_FIELD,
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
]

# Logo (v2's real name) is a whole-string engraved label (two lines, read
# directly, never struck) - same "Label" tab convention as Bennett/Hammond
# (LABEL_FIELDS_BENNETT/LABEL_FIELDS_HAMMOND), named for what kind of
# feature it is, not the v2 variable name.
LABEL_FIELDS_HAMMOND_SPLIT = [
    ("font_path", ["label", "font_path"], str, "Label font path", "Font for the two engraved Logo_Text lines."),
    ("label1", ["label", "label1"], str, "Label 1", "Logo_Text_1 - e.g. a name."),
    ("label2", ["label", "label2"], str, "Label 2", "Logo_Text_2 - e.g. a year."),
    ("label_size_mm", ["label", "label_size_mm"], float, "Label text size (mm)", "Logo_Size."),
    ("depth_mm", ["label", "depth_mm"], float, "Label depth (mm)", "Logo_Depth."),
    ("radial_offset_mm", ["label", "radial_offset_mm"], float, "Radial offset (mm)",
     "Logo_Radial_Offset - distance from the hub axis both label lines are center-anchored on, "
     "along the first inner spoke's own centerline."),
]

QUALITY_FIELDS_HAMMOND_SPLIT = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Arc/Center/Rib/Tube/etc. body facet count."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - only matters while Minkowski (Build tab) is on."),
    CLIP_TO_CELL_FIELD,
    ("min_band_height_mm", ["quality", "min_band_height_mm"], float, "Min band height (mm)",
     "Wall banding. The body is pre-split into horizontal bands so the boolean that unions the characters in has no full-height face to shatter into slivers. Bands are never made shorter than this; 0 = auto, one band per facet width. Raise it to coarsen an over-fine wall."),
]

RESIN_FIELDS_HAMMOND_SPLIT = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("min_rod_height", ["resin", "min_rod_height"], float, "Min rod height (mm)", ""),
    ("raft_od", ["resin", "raft_od"], float, "Raft OD (mm)", ""),
    ("raft_thickness", ["resin", "raft_thickness"], float, "Raft thickness (mm)", ""),
    ("fence_spacing", ["resin", "fence_spacing"], float, "Fence lattice spacing (mm)", "Res_Spacing - diagonal cross-bracing rod pitch."),
    ("fence_angle_deg", ["resin", "fence_angle_deg"], float, "Fence lattice angle (deg)", "Res_Angle."),
    # arc_div/folder_div/folder_face_div/ring_div/ring_start_end_deg
    # (list-valued grid-division counts) are deliberately YAML-only - edit
    # config/hammond_split.yaml directly - same treatment as layout.
    # placement_map/char_legend elsewhere, per this repo's "a list-valued
    # config key needs an explicit decision" rule.
    OVERHANG_WARN_FIELD,
]

ELEMENT_FIELDS_HAMMOND_SPLIT = [
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final character diameter (mm)",
     "Diameter across two opposing character tips, measured from arc_od. Sets how far the "
     "characters stand proud of the arc, independently of the glyph height."),
    ("arc_od", ["element", "arc_od"], float, "Arc OD (mm)", "Arc_OD."),
    ("arc_thickness", ["element", "arc_thickness"], float, "Arc thickness (mm)", ""),
    ("arc_height", ["element", "arc_height"], float, "Arc height (mm)", ""),
    ("arc_height_offset", ["element", "arc_height_offset"], float, "Arc height offset (mm)", ""),
    ("folder_degree_offset", ["element", "folder_degree_offset"], float, "Folder degree offset (deg)", ""),
    ("folder_degrees", ["element", "folder_degrees"], float, "Folder degrees (deg)", ""),
    ("folder_id_mm", ["element", "folder_id_mm"], float, "Folder ID (mm)", "Folder_ID_Mm - +/- folder_radial_gap gives the real left/right IDs."),
    ("folder_od", ["element", "folder_od"], float, "Folder OD (mm)", ""),
    ("folder_thickness", ["element", "folder_thickness"], float, "Folder thickness (mm)", ""),
    ("folder_close_gap", ["element", "folder_close_gap"], float, "Folder close gap (deg)", "Folder_Arc_Start = this/2."),
    ("folder_glue_hole_id_mm", ["element", "folder_glue_hole_id_mm"], float, "Glue hole ID (mm)", ""),
    ("folder_glue_groove_r", ["element", "folder_glue_groove_r"], float, "Glue groove radius (mm)", ""),
    ("folder_glue_groove_depth", ["element", "folder_glue_groove_depth"], float, "Glue groove depth (mm)", ""),
    ("finger_thickness", ["element", "finger_thickness"], float, "Finger thickness (mm)", "Alignment finger tip width."),
    ("spoke_thickness", ["element", "spoke_thickness"], float, "Spoke thickness (mm)", ""),
    ("spoke_height", ["element", "spoke_height"], float, "Spoke height (mm)", ""),
    ("spoke_count", ["element", "spoke_count"], int, "Spoke count", ""),
    ("spoke_extent", ["element", "spoke_extent"], float, "Spoke extent (deg)", ""),
    ("spoke_chamfer", ["element", "spoke_chamfer"], float, "Spoke chamfer (mm)", ""),
    ("rib_od", ["element", "rib_od"], float, "Rib OD (mm)", ""),
    ("rib_thickness", ["element", "rib_thickness"], float, "Rib thickness (mm)", ""),
    ("rib_radius", ["element", "rib_radius"], float, "Rib radius (mm)", ""),
    ("angular_divisions", ["element", "angular_divisions"], int, "Angular divisions", "Char_Theta = 360/this."),
    ("pin_id_mm", ["element", "pin_id_mm"], float, "Pin hole ID (mm)", ""),
    ("pin_radial", ["element", "pin_radial"], float, "Pin radial distance (mm)", ""),
    ("pin_id_chamfer", ["element", "pin_id_chamfer"], float, "Pin hole chamfer (mm)", ""),
    ("tube_chamfer", ["element", "tube_chamfer"], float, "Tube chamfer (mm)", ""),
    # pin_theta/tube_od_mm (2-element [left,right] lists) are deliberately
    # YAML-only, same reason as the resin div arrays above.
    ("id_offset", ["element", "id_offset"], float, "ID offset (mm)", "Tube/pin hole resin/FDM print-fit growth."),
    ("folder_radial_gap", ["element", "folder_radial_gap"], float, "Folder radial gap (mm)", "Folder_ID[0]/[1] +/- split."),
    ("folder_squash_clearance", ["element", "folder_squash_clearance"], float, "Folder squash clearance (mm)", ""),
]

# Selectric I/II, Selectric III, and Selectric Composer (spherical
# typeball family, see lib/spherical_machine.py) share the EXACT SAME
# config schema across all three machines (unlike Bennett/Mignon/Helios,
# which each diverge structurally) - so one shared field-table set covers
# all three, except Font & Alignment: Composer sizes type by cap-height
# (font.composer_cap_height) instead of direct point size (font.size_mm),
# so it gets its own table. No Logo/Gauge/Layout/Calibration tabs for any
# of the three - no engraved logo text, no Shaft Gauge Test, no editable
# keyboard-layout concept (the hemisphere character map is fixed, not a
# user-selectable preset - see lib/layouts/selectric12_layout.py), and no
# Calibration entry points implemented yet (CalibrationElement/
# CalibrationAdditive - see lib/spherical_machine.py's module docstring's
# "not yet ported" list) - compose()/_compose_build_tab gate the
# Calibration tab/Build-target option on "Calibration" in self.SECTIONS,
# and self.HAS_LAYOUT_TAB (set in _load_machine) gates the Layout tab and
# every baseline_row/cutout_row-style widget, same pattern as the "Gauge"
# key already used for machines with no Shaft Gauge Test.
FONT_FIELDS_SELECTRIC12 = [
    ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters."),
    ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Direct point size (v2 Font_Size), not Composer's cap-height convention."),
    ("font2_path", ["font2", "font2_path"], str, "Font 2 path", "Secondary font for font2_chars below."),
    ("font2_size_mm", ["font2", "font2_size_mm"], float, "Font 2 size (mm)", ""),
    ("font2_chars", ["font2", "font2_chars"], str, "Font 2 chars", "Characters that use font2 instead of font."),
    ("mode", ["alignment", "mode"], str, "Align mode", '"center" or "left" (v2 H_Alignment).'),
    ("x_pos_offset", ["alignment", "x_pos_offset"], float, "X position offset (mm)", "v2 X_Pos_Offset."),
    ("y_pos_offset", ["alignment", "y_pos_offset"], float, "Y position offset (mm)", "v2 Y_Pos_Offset."),
    ("custom_h_chars", ["alignment", "custom_h_chars"], str, "Custom H-align chars", "Get an extra horizontal offset (below)."),
    ("custom_h_offset", ["alignment", "custom_h_offset"], float, "Custom H-align offset (mm)", ""),
    ("custom_v_chars", ["alignment", "custom_v_chars"], str, "Custom V-align chars", "Get an extra vertical offset (below)."),
    ("custom_v_offset", ["alignment", "custom_v_offset"], float, "Custom V-align offset (mm)", ""),
    ("caret_auto_raise", ["alignment", "caret_auto_raise"], bool, "Auto-raise caret",
     "Puts the top of \"^\" on the font's cap height (the top of its capitals, from the font's own data) - the raised caret typewriters had. Caret raise below adds to it."),
    ("caret_raise_mm", ["alignment", "caret_raise_mm"], float, "Caret raise (mm)",
     "Moves \"^\" up (negative = down), on top of auto-raise if that is on. Fonts draw U+005E wherever their circumflex accent sits, which rarely matches a typewriter face; a Blickensderfer caret on the baseline is about -0.6 x the font size."),
    DRAFT_ANGLE_FIELD,
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
]

# Composer-only: sizes type by CAP HEIGHT (font.composer_cap_height/2.834
# = Font_Size_Selected, v2's own fixed conversion, ibm.scad:186,190) - not
# direct point size like Selectric I/II & III. custom_h_chars is
# especially print-critical here - see config/selectric_composer.yaml's
# header comment (explicit user directive on alignment fidelity).
FONT_FIELDS_SELECTRIC_COMPOSER = [
    ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters."),
    ("composer_cap_height", ["font", "composer_cap_height"], float, "Cap height (pt)",
     "v2 Composer_Cap_Height - Font_Size_Selected = this/2.834, not a direct point size."),
    ("font2_path", ["font2", "font2_path"], str, "Font 2 path", "Secondary font for font2_chars below."),
    ("font2_composer_cap_height", ["font2", "font2_composer_cap_height"], float, "Font 2 cap height (pt)", ""),
    ("font2_chars", ["font2", "font2_chars"], str, "Font 2 chars", "Characters that use font2 instead of font."),
    ("mode", ["alignment", "mode"], str, "Align mode", '"center" or "left" (v2 H_Alignment) - CRITICAL, real value "left".'),
    ("x_pos_offset", ["alignment", "x_pos_offset"], float, "X position offset (mm)",
     "v2 X_Pos_Offset_Composer_ - CRITICAL, print-affecting, verified against v2 line-by-line."),
    ("y_pos_offset", ["alignment", "y_pos_offset"], float, "Y position offset (mm)",
     "v2 Y_Pos_Offset_Composer - CRITICAL, print-affecting, verified against v2 line-by-line."),
    ("custom_h_chars", ["alignment", "custom_h_chars"], str, "Custom H-align chars", "Get an extra horizontal offset (below)."),
    ("custom_h_offset", ["alignment", "custom_h_offset"], float, "Custom H-align offset (mm)", ""),
    ("custom_v_chars", ["alignment", "custom_v_chars"], str, "Custom V-align chars", "Get an extra vertical offset (below)."),
    ("custom_v_offset", ["alignment", "custom_v_offset"], float, "Custom V-align offset (mm)", ""),
    ("caret_auto_raise", ["alignment", "caret_auto_raise"], bool, "Auto-raise caret",
     "Puts the top of \"^\" on the font's cap height (the top of its capitals, from the font's own data) - the raised caret typewriters had. Caret raise below adds to it."),
    ("caret_raise_mm", ["alignment", "caret_raise_mm"], float, "Caret raise (mm)",
     "Moves \"^\" up (negative = down), on top of auto-raise if that is on. Fonts draw U+005E wherever their circumflex accent sits, which rarely matches a typewriter face; a Blickensderfer caret on the baseline is about -0.6 x the font size."),
    DRAFT_ANGLE_FIELD,
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
]

LABEL_FIELDS_SELECTRIC = [
    ("enabled", ["label", "enabled"], bool, "Label enabled", "v2 Label - typeface name engraved on the top face."),
    ("arrow_enabled", ["label", "arrow_enabled"], bool, "Arrow enabled", "v2 Arrow - alignment marker triangle."),
    ("show_number", ["label", "show_number"], bool, "Show number label", "v2: on for Selectric I/II & III, off for Composer."),
    ("label_no", ["label", "label_no"], str, "Number label text", "v2 Label_No, e.g. \"10\"."),
    ("label_text_override", ["label", "label_text_override"], str, "Typeface label override", "Blank adopts the font's own name (font.name)."),
    ("label_no_font_override", ["label", "label_no_font_override"], str, "Number label font override", "Blank adopts font.path."),
    ("label_font_override", ["label", "label_font_override"], str, "Typeface label font override", "Blank adopts font.path."),
    ("no_label_size", ["label", "no_label_size"], float, "Number label size (mm)", ""),
    ("no_label_offset", ["label", "no_label_offset"], float, "Number label vertical offset (mm)", ""),
    ("font_label_size", ["label", "font_label_size"], float, "Typeface label size (mm)", ""),
    ("font_label_offset", ["label", "font_label_offset"], float, "Typeface label vertical offset (mm)", ""),
    ("del_base_from_centre", ["label", "del_base_from_centre"], float, "Arrow distance from center (mm)", ""),
    ("del_depth", ["label", "del_depth"], float, "Label/arrow deboss depth (mm)", ""),
]

QUALITY_FIELDS_SELECTRIC = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("minkowski_enabled", ["build", "minkowski_enabled"], bool, "Minkowski draft", "Off: fast undrafted preview (correct platen curve/placement, no taper)."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Sphere/skirt/roof/boss facet count."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Shaft bore and the real platen cutout cylinder (v2 shares one Cyl_Fn for both)."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
]

RESIN_FIELDS_SELECTRIC = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin fn", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", "v2 Tip_D."),
    ("tip_notch_od", ["resin", "tip_notch_od"], float, "Notch tip OD (mm)", "v2 Tip_Notch_D - used for the drive-notch's own supports."),
    ("tip_notch_offset", ["resin", "tip_notch_offset"], float, "Notch support angle offset (deg)", "v2 Tip_Notch_Offset."),
    ("tip_in", ["resin", "tip_in"], float, "Tip inset (mm)", "v2 Tip_In."),
    ("tip_h", ["resin", "tip_h"], float, "Tip height (mm)", "v2 Tip_H."),
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", "v2 Rod_D."),
    ("base_od", ["resin", "base_od"], float, "Raft OD (mm)", "v2 Base_D - mapped to the shared resin_support.resin_rod()'s raft_od."),
    ("base_h", ["resin", "base_h"], float, "Raft thickness (mm)", "v2 Base_H - mapped to raft_thickness (v2's own base-chamfer ratio isn't replicated, see the resin: section comment)."),
    ("min_rod_h", ["resin", "min_rod_h"], float, "Min rod height (mm)", "v2 Min_Rod_H."),
    ("resin_detent_clock_offset", ["resin", "resin_detent_clock_offset"], float, "Detent support clock offset (deg)", "v2 Resin_Detent_Clock_Offset."),
    OVERHANG_WARN_FIELD,
]

# element: schema is byte-identical across all 3 Selectric machines (same
# physical ball) - one shared table.
ELEMENT_FIELDS_SELECTRIC = [
    ("sphere_od", ["element", "sphere_od"], float, "Sphere OD (mm)", "v2 Sphere_OD."),
    ("min_final_character_diameter", ["element", "min_final_character_diameter"], float,
     "Min final character diameter (mm)",
     "Diameter across two opposing character tips (v2 Max_OD) - the same key the cylinder and "
     "shuttle machines use. Protrusion above the ball is half the difference from sphere_od."),
    ("top_flat_to_center", ["element", "top_flat_to_center"], float, "Top flat to center (mm)", "v2 Top_Flat_To_Center."),
    ("top_flat_thickness", ["element", "top_flat_thickness"], float, "Top flat thickness (mm)", ""),
    ("top_chamfer", ["element", "top_chamfer"], float, "Top shaft chamfer (mm)", "v2 Top_Chamfer."),
    ("inside_id", ["element", "inside_id"], float, "Inside ID (mm)", "v2 Inside_ID."),
    ("boss_od", ["element", "boss_od"], float, "Boss OD (mm)", ""),
    ("boss_clearance", ["element", "boss_clearance"], float, "Boss clearance (mm)", ""),
    ("boss_step", ["element", "boss_step"], float, "Boss step thickness (mm)", ""),
    ("boss_to_center_base", ["element", "boss_to_center_base"], float, "Boss to center, base (mm)", "v2 Boss_To_Center_ - snoot_droop_compensation is added on top."),
    ("snoot_droop_compensation", ["element", "snoot_droop_compensation"], float, "Snoot droop compensation (mm)",
     "CRITICAL print-fit value - v2's own echo() warning: adjust until a printed boss measures 8.5mm to the top flat."),
    ("shaft_id", ["element", "shaft_id"], float, "Shaft ID (mm)", ""),
    ("skirt_top_od", ["element", "skirt_top_od"], float, "Skirt top OD (mm)", ""),
    ("skirt_bottom_od", ["element", "skirt_bottom_od"], float, "Skirt bottom OD (mm)", ""),
    ("platen_diameter", ["element", "platen_diameter"], float, "Platen diameter (mm)", "v2 Platen_OD - 36 for Selectric I/II & III, 43 for Composer."),
    ("drive_notch_width", ["element", "drive_notch_width"], float, "Drive notch width (mm)", ""),
    ("drive_notch_height", ["element", "drive_notch_height"], float, "Drive notch height (mm)", ""),
    ("drive_notch_theta", ["element", "drive_notch_theta"], float, "Drive notch angle (deg)", "v2 Drive_Notch_Theta_."),
    ("detent_valley_to_center", ["element", "detent_valley_to_center"], float, "Detent valley to center (mm)", ""),
    ("detent_skirt_clock_offset", ["element", "detent_skirt_clock_offset"], float, "Detent skirt clock offset (deg)", ""),
    ("floor", ["element", "floor"], float, "Floor - center to detent teeth tips (mm)",
     "v2's own measured reference value, not derived from other fields here."),
]

# --- Type Slug family (lib/wing_slug.py + lib/type_slug.py/vogue_slug.py/
# gauge_slug.py, and lib/box_slug.py + lib/oliver_slug.py/lumi_slug.py) -
# small standalone novelty/reference type-slug replicas, ground truth is
# v1 not v2 (see lib/wing_slug.py's/lib/box_slug.py's own module
# docstrings). No Layout tab (no `layout:` config section - HAS_LAYOUT_
# TAB is naturally False, same mechanism Selectric's own "no editable
# keyboard-layout concept" already relies on) and no Calibration tab
# (CalibrationElement/CalibrationAdditive aren't implemented for this
# family either - same "deferred" precedent lib/spherical_machine.py's
# own module docstring sets), so these reuse SECTIONS_COMMON's "Font &
# Alignment" list ONLY (schema matches exactly - font.path/size_mm,
# alignment.*, build.draft_angle_deg), not the whole dict spread (which
# would also pull in "Calibration").
CHARACTER_FIELDS_WING_SLUG = [
    ("char_enabled", ["character", "char_enabled"], bool, "Character enabled",
     "Off for Gauge Slug - no struck character exists in that real v1 source at all."),
    ("lower_char", ["character", "lower_char"], str, "Lower character", ""),
    ("upper_char", ["character", "upper_char"], str, "Upper character", ""),
]

# character.chars (oliver_slug/lumi_slug) is a list (3 items for Oliver,
# 4 for Lumi, bottom-to-top stack order) - deliberately YAML-only, no
# tune.py field, per CLAUDE.md's "list-valued config key" convention
# (option (b): a one-line comment here stands in for the explicit
# decision, same as layout.placement_map/char_legend elsewhere). Only
# the two scalar siblings are exposed.
CHARACTER_FIELDS_BOX_SLUG = [
    ("baseline_mm", ["character", "baseline_mm"], float, "Baseline (mm)", ""),
    ("baselines_shift_motion_mm", ["character", "baselines_shift_motion_mm"], float,
     "Baseline shift per character (mm)", ""),
]

LOGO_FIELDS_SLUG = [
    ("logo_enabled", ["logo", "logo_enabled"], bool, "Generic SVG logo enabled",
     "The AR1.svg-style single-mark logo - off for Vogue Slug/Gauge Slug (see vogue_enabled below for Vogue Slug's own real logo)."),
    ("svg_file", ["logo", "svg_file"], str, "Logo SVG file", ""),
    ("scale_mm_per_unit", ["logo", "scale_mm_per_unit"], float, "Logo scale (mm per SVG unit)",
     "v4-only knob - see lib/svg_import.py's module docstring for why this isn't a port of v1's own SVG_Scale. "
     "AR1.svg's own value - a DIFFERENT SVG viewBox/scale than the Vogue Foundry mark below, not interchangeable."),
    ("logo_depth_mm", ["logo", "logo_depth_mm"], float, "Logo engraving depth (mm)", ""),
    ("location_frac", ["logo", "location_frac"], float, "Logo position (fraction of body length)", ""),
    ("vogue_enabled", ["logo", "vogue_enabled"], bool, "Vogue Foundry mark enabled",
     "The real 2-piece arrow+V mark - only ever on for Vogue Slug."),
    ("vogue_arrow_svg_file", ["logo", "vogue_arrow_svg_file"], str, "Vogue arrow SVG file", ""),
    ("vogue_v_svg_file", ["logo", "vogue_v_svg_file"], str, "Vogue V SVG file", ""),
    ("vogue_scale_mm_per_unit", ["logo", "vogue_scale_mm_per_unit"], float, "Vogue mark scale (mm per SVG unit)",
     "The Vogue Foundry mark's OWN scale - separate from scale_mm_per_unit above (AR1.svg has a much larger "
     "viewBox than the arrow/V marks; v1 itself uses two different scale variables here, SVG_Scale vs SVG_V1_Scale)."),
]

LABEL_FIELDS_SLUG = [
    ("text", ["label", "text"], str, "Copyright text", ""),
    ("font_path", ["label", "font_path"], str, "Copyright font path", ""),
    ("label_depth_mm", ["label", "label_depth_mm"], float, "Copyright engraving depth (mm)", ""),
]

ELEMENT_FIELDS_WING_SLUG = [
    ("body_width_mm", ["element", "body_width_mm"], float, "Body width (mm)", "v1 Body_Width."),
    ("body_length_mm", ["element", "body_length_mm"], float, "Body length (mm)", "v1 Body_Length."),
    ("body_height_mm", ["element", "body_height_mm"], float, "Body height (mm)", "v1 Body_Height."),
    ("face_thickness_mm", ["element", "face_thickness_mm"], float, "Face thickness (mm)", "v1 Face_Thickness."),
    ("face_radius_mm", ["element", "face_radius_mm"], float, "Face corner radius (mm)", "v1 Face_Radius."),
    ("wing_radius_mm", ["element", "wing_radius_mm"], float, "Wing radius (mm)", "v1 Wing_Radius."),
    ("platen_shift_motion_mm", ["element", "platen_shift_motion_mm"], float, "Platen shift motion (mm)", "v1 Platen_Shift_Motion."),
    ("baselines_shift_motion_mm", ["element", "baselines_shift_motion_mm"], float, "Baseline shift motion (mm)", "v1 Baselines_Shift_Motion."),
    ("body_slot_width_mm", ["element", "body_slot_width_mm"], float, "Typebar slot width (mm)", "v1 Body_Slot_Width."),
    ("wing_thickness_mm", ["element", "wing_thickness_mm"], float, "Wing minimum thickness (mm)", "v1 Wing_Thickness."),
    ("aligning_cut_mm", ["element", "aligning_cut_mm"], float, "Aligning cut position (mm)", "v1 Aligning_Cut."),
    ("baseline_mm", ["element", "baseline_mm"], float, "Baseline (mm)", "v1 Baseline."),
    ("platen_diameter_mm", ["element", "platen_diameter_mm"], float, "Platen diameter (mm)", "v1 Platen_Diameter."),
    ("bottom_thickness_mm", ["element", "bottom_thickness_mm"], float, "Bottom thickness (mm)", "v1 Bottom_Thickness."),
    ("upper_wing_angle_deg", ["element", "upper_wing_angle_deg"], float, "Upper wing angle (deg)", "v1 Upper_Wing_Angle."),
    ("lower_wing_angle_deg", ["element", "lower_wing_angle_deg"], float, "Lower wing angle (deg)", "v1 Lower_Wing_Angle."),
    ("loop_enabled", ["element", "loop_enabled"], bool, "Loop enabled", "v1 Loop."),
    ("loop_thickness_mm", ["element", "loop_thickness_mm"], float, "Loop tube thickness (mm)", "v1 Loop_Thickness."),
    ("loop_diameter_mm", ["element", "loop_diameter_mm"], float, "Loop outer diameter (mm)", "v1 Loop_Diameter."),
    ("loop_rotation_deg", ["element", "loop_rotation_deg"], float, "Loop rotation (deg)", "v1 Loop_Rotation."),
    ("post_enabled", ["element", "post_enabled"], bool, "Mounting post enabled", "v1 Post."),
    ("post_id_mm", ["element", "post_id_mm"], float, "Post hole ID (mm)", "v1 Post_ID."),
    ("post_od_mm", ["element", "post_od_mm"], float, "Post boss OD (mm)", "v1 Post_OD."),
    ("side_hole_enabled", ["element", "side_hole_enabled"], bool, "Side hole enabled", "v1 Side_Hole."),
    ("side_hole_id_mm", ["element", "side_hole_id_mm"], float, "Side hole diameter (mm)", "v1 Side_Hole_ID."),
    ("side_hole_height_frac", ["element", "side_hole_height_frac"], float, "Side hole height (fraction of body height)", "v1 Side_Hole_Height."),
]

ELEMENT_FIELDS_BOX_SLUG = [
    ("body_width_mm", ["element", "body_width_mm"], float, "Body width (mm)", "v1 Body_Width."),
    ("body_length_mm", ["element", "body_length_mm"], float, "Body length (mm)", "v1 Body_Length."),
    ("body_height_mm", ["element", "body_height_mm"], float, "Body height (mm)", "v1 Body_Height."),
    ("platen_shift_motion_mm", ["element", "platen_shift_motion_mm"], float, "Platen shift motion (mm)", "v1 Platen_Shift_Motion."),
    ("body_slot_width_mm", ["element", "body_slot_width_mm"], float, "Typebar slot width (mm)", "v1 Body_Slot_Width."),
    ("wing_thickness_mm", ["element", "wing_thickness_mm"], float, "Wing taper thickness (mm)", "v1 Wing_Thickness."),
    ("aligning_cut_mm", ["element", "aligning_cut_mm"], float, "Aligning cut position (mm)", "v1 Aligning_Cut."),
    ("platen_diameter_mm", ["element", "platen_diameter_mm"], float, "Platen diameter (mm)", "v1 Platen_Diameter."),
    ("bottom_thickness_mm", ["element", "bottom_thickness_mm"], float, "Bottom thickness (mm)", "v1 Bottom_Thickness."),
    ("upper_wing_angle_deg", ["element", "upper_wing_angle_deg"], float, "Wing angle (deg)",
     "v1 Upper_Wing_Angle - used for BOTH wing-angle cuts (Lower_Wing_Angle is dead in the real v1 source, see lib/box_slug.py's module docstring)."),
    ("loop_enabled", ["element", "loop_enabled"], bool, "Loop enabled", "v1 Loop - Lumi Slug only, Oliver Slug has no Loop concept at all."),
    ("loop_thickness_mm", ["element", "loop_thickness_mm"], float, "Loop tube thickness (mm)", "v1 Loop_Thickness."),
    ("loop_diameter_mm", ["element", "loop_diameter_mm"], float, "Loop outer diameter (mm)", "v1 Loop_Diameter."),
    ("loop_rotation_deg", ["element", "loop_rotation_deg"], float, "Loop rotation (deg)", "v1 Loop_Rotation."),
]

RESIN_FIELDS_WING_SLUG = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin support facets", ""),
    ("raft_thickness_mm", ["resin", "raft_thickness_mm"], float, "Raft thickness (mm)", "v1 Raft_Thickness."),
    ("wire_thickness_mm", ["resin", "wire_thickness_mm"], float, "Wire thickness (mm)", "v1 Wire_Thickness."),
    ("support_height_mm", ["resin", "support_height_mm"], float, "Support height (mm)", "v1 Support_Height."),
    ("support_pitch_mm", ["resin", "support_pitch_mm"], float, "Support pitch (mm)", "v1 Support_Pitch."),
    OVERHANG_WARN_FIELD,
]

RESIN_FIELDS_BOX_SLUG = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin support facets",
     "Declared but not wired to any geometry - Oliver Slug/Lumi Slug have no resin-support geometry at all, see lib/box_slug.py's ResinSupport()."),
    OVERHANG_WARN_FIELD,
]

QUALITY_FIELDS_WING_SLUG = [
    ("corner_fn", ["quality", "corner_fn"], int, "Body corner facets", ""),
    ("wing_fn", ["quality", "wing_fn"], int, "Wing cylinder facets", ""),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen cutout facets", ""),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Draft cone facets", ""),
    ("loop_fn", ["quality", "loop_fn"], int, "Loop sweep facets", ""),
    ("loop_tube_fn", ["quality", "loop_tube_fn"], int, "Loop tube cross-section facets",
     "Kept independent from Loop sweep facets - see scad_primitives.torus()'s docstring."),
    ("post_fn", ["quality", "post_fn"], int, "Post facets", ""),
    ("side_hole_fn", ["quality", "side_hole_fn"], int, "Side hole facets", ""),
    ("gauge_hole_fn", ["quality", "gauge_hole_fn"], int, "Gauge hole fn",
     "Facet count for the gauge's pitch holes."),
]

QUALITY_FIELDS_BOX_SLUG = [
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Draft cone facets", ""),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen cutout facets", ""),
    ("loop_fn", ["quality", "loop_fn"], int, "Loop sweep facets", ""),
    ("loop_tube_fn", ["quality", "loop_tube_fn"], int, "Loop tube cross-section facets",
     "Kept independent from Loop sweep facets - see scad_primitives.torus()'s docstring."),
]

# Named "Ticks", NOT "Gauge" - deliberately avoids colliding with the
# existing Blickensderfer/Postal "Gauge" concept (a Shaft Gauge Test
# CALIBRATION PRINT, gated by has_gauge/GaugeTestSet() in
# _compose_build_tab). Gauge Slug's ticks are real element geometry
# (gauge_slug.py's own Ticks(), gated by gauge.gauge_enabled), not a
# build-target option - reusing "Gauge" here would make
# _compose_build_tab wrongly offer a "Shaft Gauge" build target that
# calls a GaugeTestSet() gauge_slug.py doesn't implement.
TICKS_FIELDS_GAUGE_SLUG = [
    ("fine_pitch_mm", ["gauge", "fine_pitch_mm"], float, "Fine tick pitch (mm)", "v1 GaugeTypeSlugSlug.scad's fine-row loop step."),
    ("major_pitch_mm", ["gauge", "major_pitch_mm"], float, "Major tick pitch (mm)", "v1 GaugeTypeSlugSlug.scad's major-row loop step."),
    ("hole_d_mm", ["gauge", "hole_d_mm"], float, "Tick hole diameter (mm)", ""),
    ("fine_z_mm", ["gauge", "fine_z_mm"], float, "Fine row Z position (mm)", ""),
    ("major_z_mm", ["gauge", "major_z_mm"], float, "Major row Z position (mm)", ""),
    ("hole_fn", ["gauge", "hole_fn"], int, "Tick hole facets", ""),
]

# Wheel cosmetics (Blickensderfer/Postal) - decorative treatment of the
# outer wall. band_z_offsets/band_heights are NOT here: they are inline
# list ELEMENTS, so they get bespoke per-band widgets exactly like
# layout.baseline_row/cutout_row do (see TuneApp._compose_band_fields and
# self.BAND_KEYS), resolved as option (a) under CLAUDE.md's "list-valued
# config key needs an explicit decision" rule.
COSMETICS_FIELDS = [
    ("wheel_style", ["cosmetics", "wheel_style"], str, "Wheel style",
     "Round is the plain body. Notched and Banded both facet the wall, one facet per character "
     "column, with a facet corner falling between columns."),
    ("notch_diameter", ["cosmetics", "notch_diameter"], float, "Notch diameter (mm)",
     "Groove cut at each facet corner. Notched style only."),
    ("notch_extension", ["cosmetics", "notch_extension"], float, "Notch extension (mm)",
     "How far the notch cutter is hulled outward past the facet corner, so it trims the characters' draft flare instead of stopping short of it. Notched style only."),
    ("band_depth", ["cosmetics", "band_depth"], float, "Band depth (mm)",
     "How far inside the facet's minor diameter a band cuts. Banded style only."),
]

# The three build values every machine has, in the same order at the head of
# every Quality tab. They were scattered before: the cylinder family and the
# Selectrics carried them on Quality, Hammond Split had the two depths on
# Font & Alignment instead, and the five slug machines exposed none of them
# at all despite all three being in their configs. One list, spliced in by
# _quality_with_core(), so a machine cannot silently miss them again.
QUALITY_CORE_FIELDS = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)",
     "Max deviation when flattening curves to line segments. Lower = rounder curves, more faces, slower."),
    ("pre_minkowski_char_height_mm", ["build", "pre_minkowski_char_height_mm"], float,
     "Pre-Minkowski glyph height (mm)",
     "Height of the extruded glyph block before the Minkowski sum. On the cylinder family and Hammond "
     "Split this sets the character's depth (total = this + cone); on the spherical and slug families "
     "the body boolean trims the block, so any sufficient value gives the same result."),
    ("minkowski_cone_height_mm", ["build", "minkowski_cone_height_mm"], float,
     "Minkowski cone height (mm)",
     "Height of the draft cone. It has to reach far enough into the body that a wide character's roots "
     "mesh into the surface instead of cutting off abruptly - taller is the safer direction."),
]


def _quality_with_core(fields):
    """Quality tab = the shared core, then this machine's own fields with
    any duplicate of a core key dropped (order within the core is fixed, so
    every machine's tab opens the same way)."""
    core_keys = {f[0] for f in QUALITY_CORE_FIELDS}
    return QUALITY_CORE_FIELDS + [f for f in fields if f[0] not in core_keys]


SECTIONS_BY_MACHINE = {
    "blickensderfer": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_BLICKPOSTAL,
                       "Quality": _quality_with_core(QUALITY_FIELDS_BLICKPOSTAL), "Resin": RESIN_FIELDS_BLICKPOSTAL,
                       "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_BLICKENSDERFER,
                       "Cosmetics": COSMETICS_FIELDS},
    "postal": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_BLICKPOSTAL,
               "Quality": _quality_with_core(QUALITY_FIELDS_BLICKPOSTAL), "Resin": RESIN_FIELDS_BLICKPOSTAL,
               "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_POSTAL,
                       "Cosmetics": COSMETICS_FIELDS},
    # no "Gauge" key - Mignon has no Shaft Gauge Test (see
    # ELEMENT_FIELDS_MIGNON's neighboring comment) - compose()/
    # _compose_build_tab() check for its absence and skip the tab/dropdown
    # option accordingly, rather than every machine being forced to have one.
    "mignon": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_MIGNON, "Label": LABEL_FIELDS_MIGNON,
               "Quality": _quality_with_core(QUALITY_FIELDS_MIGNON), "Resin": RESIN_FIELDS_MIGNON,
               "Element": ELEMENT_FIELDS_MIGNON, "Legend": LEGEND_FIELDS_MIGNON},
    # no "Gauge" key - Bennett has no Shaft Gauge Test either (v2/bennett.
    # scad:24: "Sections with no Bennett equivalent (Print Tolerances,
    # Shaft Gauge Test) are omitted"). No "Logo" key - its one engraved-
    # text feature is LABEL_FIELDS_BENNETT's "Label" tab instead (see that
    # list's neighboring comment).
    "bennett": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Label": LABEL_FIELDS_BENNETT,
                "Quality": _quality_with_core(QUALITY_FIELDS_BENNETT), "Resin": RESIN_FIELDS_BENNETT,
                "Element": ELEMENT_FIELDS_BENNETT},
    # no "Gauge" key - Helios has no Shaft Gauge Test (v2/heliosklimax.
    # scad's own header: "Sections with no Helios equivalent (Logo, Print
    # Tolerances, Shaft Gauge Test) are omitted"). No "Label" key either -
    # same header, no engraved-TEXT feature at all. "Logo" key IS present
    # (LOGO_FIELDS_HELIOS) - v1's separate SVG_Logo mark, a deliberate
    # v1-sourced addition v2 never had - see that list's own comment.
    "helios": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_HELIOS, "Quality": _quality_with_core(QUALITY_FIELDS_HELIOS),
               "Resin": RESIN_FIELDS_HELIOS, "Element": ELEMENT_FIELDS_HELIOS},
    # no "Gauge"/"Logo" key - Hammond has neither (see lib/hammond.py's
    # module docstring) - its two whole-string engraved labels are the
    # "Label" tab instead, same convention as Bennett.
    "hammond": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Label": LABEL_FIELDS_HAMMOND,
                "Quality": _quality_with_core(QUALITY_FIELDS_HAMMOND), "Resin": RESIN_FIELDS_HAMMOND,
                "Element": ELEMENT_FIELDS_HAMMOND, "Rib": RIB_FIELDS_HAMMOND,
                "Legend": LEGEND_FIELDS_HAMMOND},
    # no "Gauge"/"Logo" key - same reasons as Hammond above. "Font &
    # Alignment" is overridden (not the shared SECTIONS_COMMON one) - see
    # FONT_FIELDS_HAMMOND_SPLIT's own comment for why (no draft_angle_deg
    # field here, plus the char_mod fields no other machine has). "Legend"
    # reuses LEGEND_FIELDS_HAMMOND/lib/hammond_legend.py as-is - see that
    # module's docstring for why the same card shape applies to both.
    "hammond_split": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_HAMMOND_SPLIT,
                       "Label": LABEL_FIELDS_HAMMOND_SPLIT, "Quality": _quality_with_core(QUALITY_FIELDS_HAMMOND_SPLIT),
                       "Resin": RESIN_FIELDS_HAMMOND_SPLIT, "Element": ELEMENT_FIELDS_HAMMOND_SPLIT,
                       "Legend": LEGEND_FIELDS_HAMMOND},
    # No SECTIONS_COMMON reuse at all - Selectric's alignment/calibration
    # schema doesn't match the cylinder family's (see FONT_FIELDS_
    # SELECTRIC12's own comment above). No "Gauge"/"Logo"/"Calibration"
    # key - see this dict's own leading comment.
    "selectric12": {"Font & Alignment": FONT_FIELDS_SELECTRIC12, "Label": LABEL_FIELDS_SELECTRIC,
                    "Quality": _quality_with_core(QUALITY_FIELDS_SELECTRIC), "Resin": RESIN_FIELDS_SELECTRIC,
                    "Element": ELEMENT_FIELDS_SELECTRIC},
    "selectric3": {"Font & Alignment": FONT_FIELDS_SELECTRIC12, "Label": LABEL_FIELDS_SELECTRIC,
                   "Quality": _quality_with_core(QUALITY_FIELDS_SELECTRIC), "Resin": RESIN_FIELDS_SELECTRIC,
                   "Element": ELEMENT_FIELDS_SELECTRIC},
    "selectric_composer": {"Font & Alignment": FONT_FIELDS_SELECTRIC_COMPOSER, "Label": LABEL_FIELDS_SELECTRIC,
                           "Quality": _quality_with_core(QUALITY_FIELDS_SELECTRIC), "Resin": RESIN_FIELDS_SELECTRIC,
                           "Element": ELEMENT_FIELDS_SELECTRIC},
    # Type Slug family (see the FIELDS block comment above this dict) -
    # "Font & Alignment" reuses ONLY that one SECTIONS_COMMON list (not
    # the whole dict spread, which would also pull in "Calibration" -
    # not implemented for this family). No "Gauge"/"Calibration" key.
    "type_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                  "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                  "Label": LABEL_FIELDS_SLUG, "Quality": _quality_with_core(QUALITY_FIELDS_WING_SLUG),
                  "Resin": RESIN_FIELDS_WING_SLUG, "Element": ELEMENT_FIELDS_WING_SLUG},
    "vogue_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                   "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                   "Label": LABEL_FIELDS_SLUG, "Quality": _quality_with_core(QUALITY_FIELDS_WING_SLUG),
                   "Resin": RESIN_FIELDS_WING_SLUG, "Element": ELEMENT_FIELDS_WING_SLUG},
    # "Ticks" (not "Gauge") - see TICKS_FIELDS_GAUGE_SLUG's own comment
    # for why this deliberately doesn't reuse the existing "Gauge"
    # section name.
    "gauge_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                   "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                   "Label": LABEL_FIELDS_SLUG, "Ticks": TICKS_FIELDS_GAUGE_SLUG,
                   "Quality": _quality_with_core(QUALITY_FIELDS_WING_SLUG), "Resin": RESIN_FIELDS_WING_SLUG,
                   "Element": ELEMENT_FIELDS_WING_SLUG},
    # No "Label"/"Logo" key - OliverSlug.scad/LumiSlug.scad have no
    # engraved-copyright/SVG-logo concept at all (see lib/box_slug.py's
    # module docstring).
    "oliver_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                    "Character": CHARACTER_FIELDS_BOX_SLUG, "Quality": _quality_with_core(QUALITY_FIELDS_BOX_SLUG),
                    "Resin": RESIN_FIELDS_BOX_SLUG, "Element": ELEMENT_FIELDS_BOX_SLUG},
    "lumi_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                  "Character": CHARACTER_FIELDS_BOX_SLUG, "Quality": _quality_with_core(QUALITY_FIELDS_BOX_SLUG),
                  "Resin": RESIN_FIELDS_BOX_SLUG, "Element": ELEMENT_FIELDS_BOX_SLUG},
}

# Static intro banner shown above a section tab's fields, keyed by section
# name - (text, css class). Only sections that need one appear here.
SECTION_INTROS = {
    "Element": ("ADVANCED - real machine dimensions. Rarely need changing.",
                "advanced-warning"),
    "Legend": (
        "A flat 2D reference card - which key produces which character - "
        "not part of the 3D element/build above. Generates a standalone "
        ".svg file, not an STL; press Generate Legend SVG below (also "
        "saves this tab's fields first, like Render/Preview do). The SVG's "
        "width/height are already real mm (matches its viewBox 1:1) for "
        "true-scale printing - when printing or exporting to PDF, pick "
        "\"Actual Size\"/100%, not \"Fit to Page\", or the mm units get "
        "silently rescaled.",
        "picker-help"),
    "Rib": ("v4-specific FDM print-fit tuning, not real machine dimensions - these values are "
            "for Build target Rib only (the standalone printed flange), never the fused "
            "Shuttle with Rib resin print or the Shuttle body itself.",
            "advanced-warning"),
    "Gauge": (
        "Small 6-pocket calibration print, not the real element. Each "
        "pocket bores its shaft passage at offset_start + n*offset_int. "
        "Test-fit each pocket on the real shaft, then set Element > Core "
        "ID offset to the best-fitting number. Select \"Shaft Gauge\" on "
        "the Build tab to build it.",
        "picker-help"),
    "Calibration": (
        "A real element where every position strikes the same test "
        "character. Turn on Vary baselines or Vary cutouts (usually just "
        "one) to sweep that value per column instead of each row's normal "
        "value, centered on the MASTER config's row so it stays a fixed "
        "target. Test-fit each column on the real machine, then enter the "
        "best-fitting value in that row's Element tab field. Select "
        "\"Calibration Element\" on the Build tab to build it.",
        "picker-help"),
}
















# Build tab's "Resin supports" checkbox (see _compose_build_tab) is
# always shown, every machine - but has no effect for machines with no
# resin-support geometry modeled at all (lib/helios.py's ResinSupport()
# returns None, ResinPrint() is a no-op alias to FullElement()). Extra
# note appended to that checkbox's help text, keyed by machine name, per
# CLAUDE.md's per-machine-banner-text rule (no if/elif chain) - empty
# string (via .get()) for every machine that DOES have real resin
# supports modeled.
RESIN_SUPPORT_UNAVAILABLE_NOTE = {
    "helios": (
        " This checkbox has no effect for Helios - no resin support "
        "geometry is modeled (see ResinPrint() in lib/helios.py)."
    ),
    "oliver_slug": (
        " This checkbox has no effect for Oliver Slug - no resin support "
        "geometry is modeled (see ResinPrint() in lib/box_slug.py)."
    ),
    "lumi_slug": (
        " This checkbox has no effect for Lumi Slug - no resin support "
        "geometry is modeled (see ResinPrint() in lib/box_slug.py)."
    ),
}

# Hammond's Build target dropdown consolidates the old separate target
# dropdown (Shuttle/Calibration Shuttle/None) + Rib checkbox into one
# control, per explicit request ("remove Rib checkbox, and just go with
# dropdown options Shuttle, Rib, Shuttle with Rib") - each option maps
# directly to a (build.target, element.groove) pair. "Rib"'s groove
# value doesn't really matter (RibOnly() ignores element.groove
# entirely - see lib/hammond.py), True just keeps it consistent with
# "Shuttle"'s own meaning (the without-rib/groove body). Calibration
# mirrors the same Rib/Without-Rib split as the real Shuttle - "will
# also need Calibration Shuttle with Rib" (an earlier version only had
# one Calibration option, always forced to groove=False regardless of
# whichever of the other 3 was picked - wrong, since Calibration should
# be able to validate EITHER real body variant, not just one hardcoded
# choice).
HAMMOND_BUILD_OPTIONS = [
    ("Shuttle", "shuttle"),
    ("Rib", "rib"),
    ("Shuttle with Rib", "shuttle_with_rib"),
    ("Calibration Shuttle", "calibration"),
    ("Calibration Shuttle with Rib", "calibration_with_rib"),
]
HAMMOND_BUILD_TARGET_GROOVE = {
    "shuttle": ("element", True),
    "rib": ("none", True),
    "shuttle_with_rib": ("element", False),
    "calibration": ("calibration", True),
    "calibration_with_rib": ("calibration", False),
}


def _hammond_build_dropdown_value(target, groove):
    """Reverse of HAMMOND_BUILD_TARGET_GROOVE - derives the dropdown's
    displayed value from a loaded config's real (target, groove) pair
    (used by _refresh_widgets_from_cfg). "none" always means "rib" (the
    only real use for Build target None); any other target picks the
    with-Rib/without-Rib variant of itself from groove, same rule for
    both "element" (shuttle/shuttle_with_rib) and "calibration"
    (calibration/calibration_with_rib)."""
    if target == "none":
        return "rib"
    if target == "calibration":
        return "calibration" if groove else "calibration_with_rib"
    return "shuttle" if groove else "shuttle_with_rib"

# layout.baseline_row/cutout_row per-row fields (Element tab - see
# TuneApp._compose_baseline_cutout_fields). Bespoke, not in
# self.FIELDS/SECTIONS - these are list ELEMENTS (patch_yaml_list_item),
# not standalone scalar YAML keys patch_yaml_value can patch. Row count
# varies per machine (3 for Blickensderfer/Postal, 7 for Mignon), so
# self.BASELINE_CUTOUT_KEYS is computed per-instance in _load_machine(),
# not a fixed module constant - see there.


def get_nested(d, path):
    for k in path:
        d = d[k]
    return d


def patch_yaml_value(text, key, value):
    if isinstance(value, bool):
        val_str = "true" if value else "false"
    elif isinstance(value, float):
        val_str = f"{value:.6f}".rstrip("0").rstrip(".")
        if "." not in val_str and "e" not in val_str.lower():
            val_str += ".0"
    elif isinstance(value, str):
        val_str = json.dumps(value, ensure_ascii=False)  # always quoted, handles embedded
        # quotes/specials; ensure_ascii=False keeps literal UTF-8 (matches
        # the file's existing style, e.g. "¢"/"Å"/"ä") instead of escaping
        # to \uXXXX - both are valid YAML, but literal matches everywhere else
    else:
        val_str = str(value)
    # value token is either a double-quoted string (handles embedded
    # escaped quotes) or a bare non-whitespace token - matters for string
    # fields like logo.text ("Leonard Chau 2025", with spaces).
    pattern = re.compile(rf'^(\s*{re.escape(key)}:\s*)("(?:[^"\\]|\\.)*"|\S+)', re.MULTILINE)
    new_text, n = pattern.subn(lambda m: m.group(1) + val_str, text, count=1)
    if n == 0:
        raise ValueError(f"key {key!r} not found in config text - was it renamed/removed?")
    return new_text


def patch_yaml_list_item(text, key, index, value):
    """Patches ONE element of an inline flow-style YAML list (key: [a, b,
    c], e.g. layout.baseline_row/cutout_row - a per-row array, but
    numeric and inline, not a block list like layout.rows) - neither
    patch_yaml_value's one-token regex nor patch_yaml_rows' block-list
    regex applies. Only float values needed so far (baseline_row/
    cutout_row), so that's all this formats - extend if a bool/str list
    item is ever exposed the same way.

    index==len(items) APPENDS a new item instead of raising - needed for
    Hammond, the first machine whose own presets vary in row count
    ("Universal, Math" is 4 rows, everything else 3): the Element tab
    always composes an editable field for every row any real preset
    could need (see _compose_baseline_cutout_fields), even ones the
    CURRENTLY selected preset doesn't use yet, so the underlying array
    must be able to grow when that field is saved - TextRing iterates
    len(DHIATENSOR)/the active layout's own row count, not len(
    baseline_row), so an unused extra trailing entry is harmless.
    index>len(items) (skipping entries) is still a real error."""
    pattern = re.compile(rf'^(\s*{re.escape(key)}:\s*\[)([^\]]*)(\])', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        raise ValueError(f"key {key!r} not found in config text - was it renamed/removed?")
    items = [x.strip() for x in m.group(2).split(",")]
    if index > len(items):
        raise ValueError(f"{key!r} has only {len(items)} items, index {index} out of range")
    val_str = f"{value:.6f}".rstrip("0").rstrip(".")
    if "." not in val_str and "e" not in val_str.lower():
        val_str += ".0"
    if index == len(items):
        items.append(val_str)
    else:
        items[index] = val_str
    return text[:m.start()] + m.group(1) + ", ".join(items) + m.group(3) + text[m.end():]


def patch_yaml_inline_list(text, key, values):
    """Replaces the WHOLE inline flow-style YAML list (key: [a, b, c]),
    not just one element like patch_yaml_list_item - needed when the
    list's own LENGTH changes, e.g. Hammond's layout.baseline_row/
    cutout_row growing from 3 to 4 entries when the "Universal, Math" layout
    preset is selected (see LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE) - a
    per-index patch can't add/remove elements."""
    pattern = re.compile(rf'^(\s*{re.escape(key)}:\s*\[)([^\]]*)(\])', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        raise ValueError(f"key {key!r} not found in config text - was it renamed/removed?")

    def _fmt(v):
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        if "." not in s and "e" not in s.lower():
            s += ".0"
        return s

    return text[:m.start()] + m.group(1) + ", ".join(_fmt(v) for v in values) + m.group(3) + text[m.end():]


def patch_yaml_rows(text, rows):
    """layout.rows is a multi-item YAML block list (3 items for
    Blickensderfer/Postal, 7 for Mignon - row-count-agnostic here, just
    writes however many items `rows` has), not a single-line scalar -
    patch_yaml_value's one-token regex doesn't apply. Matches the `rows:`
    line plus every immediately-following more-indented `- "..."` line
    and replaces the whole block, preserving the existing indent style."""
    pattern = re.compile(r'^(\s*)rows:[ \t]*\n((?:\1  - .*\n?)+)', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        raise ValueError("layout.rows block not found in config text")
    indent = m.group(1)
    item_indent = indent + "  "
    new_block = "".join(f"{item_indent}- {json.dumps(r, ensure_ascii=False)}\n" for r in rows)
    return text[:m.start()] + f"{indent}rows:\n{new_block}" + text[m.end():]


def patch_yaml_text_block(text, key, value):
    """type_test.text is a literal block scalar (`key: |-` followed by
    indented lines), not a single-line scalar or a list - can't use
    patch_yaml_value (one-token regex) or patch_yaml_rows (list-item
    regex). Matches the `key: |...` line plus every immediately-
    following more-indented line (blank lines included - YAML block
    scalars allow those with no indent required) and replaces the whole
    block, always re-emitting as `|-` (strip trailing newline) regardless
    of the original block style, preserving the existing indent."""
    pattern = re.compile(
        rf'^(\s*){re.escape(key)}:[ \t]*\|[-+]?[ \t]*\n((?:\1  .*\n|[ \t]*\n)*)', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        raise ValueError(f"{key!r} block scalar not found in config text")
    indent = m.group(1)
    item_indent = indent + "  "
    lines = value.split("\n")
    new_block = "".join(f"{item_indent}{line}\n" if line else "\n" for line in lines)
    return text[:m.start()] + f"{indent}{key}: |-\n{new_block}" + text[m.end():]


def migrate_running_config(master_config_path, config_path):
    """A running copy can predate a later codebase update that added
    new config fields (e.g. this session's `gauge:` section and
    `build.target`) - "once changed, always changed" means it never
    auto-resyncs with master, so it'd be missing them entirely and
    crash (patch_yaml_value raises if a field it tries to save doesn't
    exist to patch). Back-fills, verbatim (comments included) from
    master's raw text: whole top-level sections the running copy is
    missing entirely, AND individual missing keys within a section
    that DOES already exist in both (e.g. build.target, added to the
    existing build: section) - inserted right after that section's
    header line, order doesn't matter in a YAML mapping. Never
    touches a key that already exists in the running copy, so no
    customization is ever overwritten. Returns the list of
    section/section.key strings backfilled (empty if none)."""
    with open(master_config_path) as f:
        master_text = f.read()
    master_cfg = yaml.safe_load(master_text)
    with open(config_path) as f:
        running_text = f.read()
    running_cfg = yaml.safe_load(running_text) or {}
    migrated = []

    # Renamed keys, converted in place before anything is backfilled.
    # alignment.caret_drop_mm (positive = down) became caret_raise_mm
    # (positive = up) plus caret_auto_raise (2026-10-20): a copy that never
    # touched it (0) takes the new auto default, one that dialled a drop
    # in keeps exactly that position.
    align = running_cfg.get("alignment")
    if isinstance(align, dict) and "caret_drop_mm" in align and "caret_raise_mm" not in align:
        m = re.search(r'^([ \t]+)caret_drop_mm:[ \t]*([^\s#]+)[^\n]*$', running_text, re.MULTILINE)
        if m:
            try:
                drop = float(m.group(2))
            except ValueError:
                drop = 0.0
            ind = m.group(1)
            auto = "true" if drop == 0 else "false"
            running_text = (running_text[:m.start()] + f"{ind}caret_auto_raise: {auto}\n"
                            f"{ind}caret_raise_mm: {-drop + 0.0}" + running_text[m.end():])
            running_cfg = yaml.safe_load(running_text) or {}
            migrated.append("alignment.caret_drop_mm -> caret_raise_mm")

    for key in master_cfg:
        if key in running_cfg:
            continue
        m = re.search(rf'(^|\n)((?:#[^\n]*\n)*{re.escape(key)}:.*?)(?=\n\S|\Z)',
                       master_text, re.DOTALL)
        if m:
            running_text = running_text.rstrip("\n") + "\n\n" + m.group(2).rstrip("\n") + "\n"
            migrated.append(key)

    for key, master_val in master_cfg.items():
        if key in migrated or not isinstance(master_val, dict):
            continue
        running_val = running_cfg.get(key)
        if not isinstance(running_val, dict):
            continue
        missing_subkeys = [sk for sk in master_val if sk not in running_val]
        if not missing_subkeys:
            continue
        sec_m = re.search(rf'(^|\n)(\s*){re.escape(key)}:[ \t]*\n', master_text)
        if not sec_m:
            continue
        sec_start = sec_m.end()
        sec_end_m = re.search(r'\n\S', master_text[sec_start:])
        sec_body = master_text[sec_start:sec_start + sec_end_m.start() + 1] if sec_end_m \
            else master_text[sec_start:]
        additions = []
        for sk in missing_subkeys:
            # Terminating lookahead must require the SAME indentation as
            # the subkey's own line (\3, backreferenced), not just "any
            # indented non-blank line" - a block-list value (e.g.
            # layout.rows) has its "- ..." items indented DEEPER than the
            # `rows:` line itself, and those items also satisfy a bare
            # "[ \t]*\S" lookahead, so the old regex stopped matching
            # right after the `key:` line and silently dropped every
            # list item, backfilling a blank `rows:` (i.e. YAML null)
            # into the running copy - confirmed live: a selectric_
            # composer.running.yaml whose layout: section predated
            # layout.rows existing in master got exactly this, corrupting
            # `rows` to null and crashing _layout_row_caps() on load.
            # Requiring \3 (same indent) means only a true sibling key
            # ends the match.
            sub_m = re.search(rf'(^|\n)((?:[ \t]*#[^\n]*\n)*([ \t]+){re.escape(sk)}:.*?)(?=\n\3\S|\Z)',
                               sec_body, re.DOTALL)
            if sub_m:
                additions.append(sub_m.group(2).rstrip("\n"))
        if not additions:
            continue
        run_sec_m = re.search(rf'(^|\n)(\s*){re.escape(key)}:[ \t]*\n', running_text)
        if not run_sec_m:
            continue
        insert_at = run_sec_m.end()
        running_text = running_text[:insert_at] + "\n".join(additions) + "\n" + running_text[insert_at:]
        migrated.append(f"{key}.{','.join(missing_subkeys)}")

    if migrated:
        with open(config_path, "w") as f:
            f.write(running_text)
    return migrated
