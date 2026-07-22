#!/usr/bin/env python3
"""
Interactive terminal GUI for tuning config/blickensderfer.yaml and
triggering rebuilds. The "f3d preview" checkbox (on by default) controls
an f3d --watch window: after a successful Preview, Render, or Render
Test Text, if f3d isn't already running (or the one we launched has
exited), it's opened fresh on the output STL; if it's already running,
we just wait a beat for its own file watcher to reload the updated
model and then try to raise the window to the front (best-effort -
needs wmctrl on PATH; a one-time log message says so if it's missing).
Uncheck the box to stop all of that and drive f3d yourself.

Workflow: Quick Preview (fast, undrafted) until it looks right, Render
(full quality, slow) to confirm, then Save to keep it. Preview/Render/
Type Test all overwrite the SAME fixed scratch path
(output.directory/output.stl_name) - it's a temp file for the current
TUI session, not a keeper. Save opens a textual_fspicker.FileSave dialog
pre-filled with a suggested output/saved/<timestamp>.stl name (override
the name/location freely, or just accept it) and copies that temp STL
there plus a same-named .yaml sidecar - not just metadata, a full
config snapshot at the top level (saved_at/master_config/running_config/
last_build go in a comment header instead, so they don't pollute the
config namespace) - Browse (see below) to it directly to reuse those
exact settings later. Only Save actually keeps anything.

Machine picker: shown on startup (unless a config path was given on the
command line - see Usage) and via the "Change Machine" button (top of
the tuner form, next to Browse/Reset to Defaults). Picking a machine
loads its default config (MACHINES) and rebuilds the whole form -
Postal's Element tab has fewer fields than Blickensderfer's (no
drive-pin countersink) and its own Layout presets, so this is a full
recompose, not just repopulating values. Browse (below) only switches
between different configs of the SAME machine - switching machines is
Change Machine's job, not Browse's (Browse refuses and points you at
Change Machine if you pick a config for a different machine).

Config file: three tiers, master/running/saved.
  - MASTER is whatever config the machine picker (or the command line)
    pointed at - tune.py NEVER writes to it. Browse (top of the screen,
    next to "master:") switches to a different master of the SAME
    machine, live.
  - RUNNING is a per-master scratch copy (<master-stem>.running.yaml,
    same directory, gitignored) that every edit/save actually goes to.
    Bootstrapped as a copy of master the first time it's needed;
    "once changed, always changed" - it persists across tune.py
    restarts against the same master, picking up wherever you left off.
    Reset to Defaults (also top of screen) overwrites the running copy
    with a fresh copy of master, discarding all accumulated edits. If
    master has since gained fields the running copy predates (e.g. a
    codebase update adds a new config section), they're auto-backfilled
    from master on load - see _migrate_running_config() - without
    touching anything you've already customized.
  - SAVED is whatever Save produces (see above) - a deliberate,
    named/timestamped snapshot, independent of both master and running.

Usage:
    python3 tune.py                        # machine picker first (see MACHINES)
    python3 tune.py config/blickensderfer.yaml   # skip the picker, load directly

Edits are NOT round-tripped through a YAML parser/dumper - the config
file has extensive prose comments documenting where every real-machine
value comes from, and a naive yaml.safe_load()+yaml.dump() would silently
strip all of them. Instead, each field is patched in place via a regex
matching just its value token on its own line (or, for layout.rows, the
whole 3-item block), leaving everything else (comments, formatting,
unrelated keys) untouched.

Tabs (in display order):
  Font & Alignment - font.* + alignment.* (combined, both are "how
    characters are placed/rendered" concerns). alignment.mode is a
    dropdown ("center"/"left"), not free text. font.path has a "Browse"
    button (textual_fspicker.FileOpen, filtered to .ttf/.otf/.ttc)
    opening at the current path's directory.
  Type Test        - NOT part of the real element. A flat, CPI/LPI-spaced
    test block (matches v2's TypeTest() fixed-pitch convention; LPI is
    the vertical equivalent for multi-line text, default 6) using the
    Font & Alignment tab's live values (path/size, align mode, all the
    center/left/modified_left/modified_right offsets - same
    alignment_x_offset() convention the real element uses), for instant
    text/legibility checks. Overwrites the same output STL path as
    Render/Quick Preview (so the same f3d --watch window shows it) -
    that output STL is a scratch preview, not saved anywhere else (see
    Save) - but the text/CPI/LPI inputs themselves ARE persisted to
    config's type_test.* section like every other field, so they
    survive a TUI restart. Triggered by the "RENDER TEST TEXT" button,
    which - unlike this tab's other widgets - lives in the always-visible button panel
    (below the tabs), not inside this TabPane, so it stays clickable
    from the Font & Alignment tab (or any tab) without switching here
    first. Triggers the same auto-open/raise f3d behavior as Preview/
    Render (see the "f3d preview" checkbox, below), and additionally
    starts f3d in camera view 7 (Top View) - only takes effect on a
    fresh launch, since f3d has no CLI way to change an already-running
    instance's camera.
  Resin            - resin.* including the "Continuous raft" checkbox
    (resin.raft) - off (default, both machines) gives each rod its own
    small raft; on gives one continuous raft plate shared by every rod,
    reaching the element's center axis (v2's original Postal-only
    behavior, now a real option for either machine - see
    cylinder_machine.resin_raft_config's docstring).
  Gauge            - gauge.offset_start/offset_int, the Shaft Gauge Test's
    only tunables (ported from v2's [Shaft Gauge Test]/GaugeTestSet() -
    see blickensderfer.GaugeTestSet's docstring for the full port notes).
    Not part of the real element - a small 6-pocket calibration test
    print for finding element.core_id_offset. Select "Shaft Gauge" on
    the Build tab to actually build it via Preview/Render.
  Calibration      - calibration.test_char/vary_baseline/vary_cutout/
    start/interval, ported from v2's Cutout_Test/Baseline_Test/
    Test_Layout mechanism (lib/testing.scad + lib/glyph_pipeline.scad's
    TextRing/TextRingDebug - see cylinder_machine.CalibrationTextRing's
    docstring for the full port notes). Not part of the real element -
    every physical position strikes the same test_char while Vary
    baselines/Vary cutouts (independent checkboxes - usually only one on
    at a time) get a per-column swept offset (start + interval*col)
    instead of its row's normal value, for empirically finding
    layout.baseline_row/cutout_row. Select "Calibration Element" on the
    Build tab to actually build it via Preview/Render.
  Build            - a dropdown, Element / Shaft Gauge / Calibration
    Element (build.target - see the Gauge/Calibration tabs for what those build),
    plus an independent "Resin supports" checkbox (build.resin_support)
    that only matters for Element (FullElement() vs ResinPrint()) - Shaft
    Gauge always includes its own resin supports regardless, Calibration
    never does. Resin tab's own fields only matter when Resin supports is
    checked.
  Layout           - a dropdown of named Blickensderfer keyboard layouts
    (ported from v2/lib/layouts/blick_layouts.scad), a read-only 3-row
    preview of whichever one's selected, and a "Modify glyphs" switch
    that unlocks a hand-editable copy of those 3 rows (seeded from the
    preview when unlocked), each capped at len(placement_map) chars -
    more would index out of PLACEMENT_MAP and crash TextRing; fewer just
    leaves some physical positions unstruck. Saving writes the preset's
    rows to layout.rows when the switch is off (as before), or the
    edited copy when it's on - both the switch state and the edited
    rows persist to config like everything else. layout.latitude_columns
    is not exposed - it must stay in sync with placement_map/the
    physical layout, not something to change casually; edit it directly
    in the YAML if you really mean to.
  Quality          - quality.* facet counts + build.points_per_mm/
    separation_mm/render_core_groove/simplify_tolerance_mm (moved here
    from Build - these are all mesh generation quality/speed knobs, not
    "what to build"). The Minkowski draft sweep itself is NOT exposed
    here - Render always forces it on and Quick Preview always forces
    it off (see _run_build), so a config-file toggle would just be
    dead weight/a second source of truth.
  Logo             - logo.* (font_path also has the same "Browse" button
    as font.path above)
  Element          - element.* - flagged ADVANCED: real machine geometry,
    not something you'd normally tune - plus layout.baseline_row/
    cutout_row's 6 per-row fields at the bottom (bespoke, see
    BASELINE_CUTOUT_KEYS/patch_yaml_list_item - these are the values the
    Calibration tab is for finding). Last tab on purpose.

List/array-valued config entries other than layout.rows and
baseline_row/cutout_row (placement_map, bottom_support_fractions) are
still NOT exposed - they don't fit a single-value text field safely and
are rare to tune interactively. Edit those directly in the YAML.
"""

import asyncio
import atexit
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime

import yaml
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Resize
from textual.widgets import (Button, Footer, Header, Input, ProgressBar, Select, Static, Switch,
                              RichLog, TabbedContent, TabPane, TextArea)
from textual_fspicker import FileOpen, FileSave, Filters

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
# f3d --command-script file: just `set_camera top`, the exact console
# command the "7" key runs - see action_render_type_test's use of it
F3D_TOP_VIEW_SCRIPT = os.path.join(REPO_ROOT, "f3d_top_view_cmds.txt")

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
}

FONT_FILE_FILTERS = Filters(
    ("Font files", lambda p: p.suffix.lower() in (".ttf", ".otf", ".ttc")),
    ("All files", lambda _: True),
)
STL_FILE_FILTERS = Filters(("STL files", lambda p: p.suffix.lower() == ".stl"))
YAML_FILE_FILTERS = Filters(
    ("YAML files", lambda p: p.suffix.lower() in (".yaml", ".yml")),
    ("All files", lambda _: True),
)
# font.path (Font & Alignment tab), logo.font_path (Logo tab), Mignon's
# label.font_path (Logo tab, label_font_path key - see LOGO_FIELDS_MIGNON),
# and Bennett's label.font_path (Label tab, plain font_path key - see
# LABEL_FIELDS_BENNETT) are the font-picking fields - each gets a "Browse"
# button, see _compose_section_tab and on_button_pressed's "browse-" id
# handling
FONT_PATH_FIELD_KEYS = ("path", "font_path", "label_font_path")

# Named Blickensderfer keyboard layouts, ported verbatim from
# v2/lib/layouts/blick_layouts.scad's DHIATENSOR/QWERTY/SCANDI/
# HEBREW_ENGL/CHARIENSTU_DE/CHARIENSTU_DE_MOD arrays. All share the same
# 3-row structure and the same physical placement_map/latitude_columns -
# only the glyph content per row differs, so switching presets only ever
# rewrites layout.rows. HEBREW_ENGL needs a Hebrew-capable font
# (font.path) to actually render correctly - v2 auto-switches Font_Hebrew
# when this layout is selected, v4 does not (no per-layout font-switching
# wired up), so you'll need to set font.path yourself too.
LAYOUT_PRESETS = {
    "DHIATENSOR": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    "QWERTY": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
        "\"#$%_/-¢@;23456789:!^1.&'(0)",
    ],
    "SCANDI": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:",
    ],
    "HEBREW_ENGL": [
        "זךכגװפףץצדהעאתןנםשרלסמיטבוקח",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    "CHARIENSTU_DE": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJU",
        "(%¨+-/'\"ö1234567890äü!;?=ß§)",
    ],
    "CHARIENSTU_DE_MOD": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJU",
        "(%*+-/'\"^1234567890`´!;?=@§)",
    ],
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
        ("draft_angle_deg", ["build", "draft_angle_deg"], float, "Draft angle (deg)",
         "Half-angle of the Minkowski draft cone each character is swept with. Real value 55."),
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
    ("radial_offset_mm", ["logo", "radial_offset_mm"], float, "Logo radius offset (mm)", "Placement radius = Logo_Radius + this."),
]

QUALITY_FIELDS_BLICKPOSTAL = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth. Real value 0.5mm."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    ("body_fn", ["quality", "body_fn"], int, "Body fn", "Main cosmetic cylinder body (Cylinder/ClipCylinder)."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Inner shaft/core bore only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowSpace, SpeedHoles, chamfers...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
]

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
     "uses the same draft_angle_deg/minkowski_fn/simplify_tolerance_mm as "
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

QUALITY_FIELDS_MIGNON = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "CenterShaft only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "HollowBody/ElementChamfer/MinkCleanup."),
    ("resin_fn", ["quality", "resin_fn"], int, "Resin fn", ""),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
]

RESIN_FIELDS_MIGNON = [
    ("rod_od", ["resin", "rod_od"], float, "Rod OD (mm)", ""),
    ("tip_od", ["resin", "tip_od"], float, "Tip OD (mm)", ""),
    ("tip_l", ["resin", "tip_l"], float, "Tip length (mm)", ""),
    ("inset", ["resin", "inset"], float, "Inset (mm)", ""),
    ("min_rod_height", ["resin", "min_rod_height"], float, "Min rod height (mm)", ""),
    ("support_height", ["resin", "support_height"], float, "Support height (mm)",
     "Raft ring's Z offset below the element, and the outer ring of rods' base height."),
    ("support_thickness", ["resin", "support_thickness"], float, "Support thickness (mm)", "Raft ring thickness."),
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
# radial_offset_mm concept at all, so it gets its own "Label" tab (not
# "Logo") matching v2's own Shuttle_Label naming and config/bennett.yaml's
# `label:` section.
LABEL_FIELDS_BENNETT = [
    ("font_path", ["label", "font_path"], str, "Label font path", "Font for the engraved LabelText."),
    ("label1a", ["label", "label1a"], str, "Label 1a (top line, right group)", "Shuttle_Label1a - e.g. a first name."),
    ("label1b", ["label", "label1b"], str, "Label 1b (bottom line, right group)", "Shuttle_Label1b - e.g. a last name."),
    ("label2", ["label", "label2"], str, "Label 2 (left group)", "Shuttle_Label2 - e.g. a year."),
    ("label_size_mm", ["label", "label_size_mm"], float, "Label text size (mm)", ""),
    ("depth_mm", ["label", "depth_mm"], float, "Label depth offset (mm)", "Added to Bottom_Countersink_Depth for the cut's Z start."),
]

QUALITY_FIELDS_BENNETT = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft/pin fn", "PositionerPins/CenterShaft."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowBody, SpeedHoles, countersinks...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("alignment_hole_fn", ["quality", "alignment_hole_fn"], int, "Alignment hole fn", "AlignmentHoles facet count."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
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
# these can't share any other machine's field lists. No "Logo"/"Label" key
# at all (v2 has no engraved-text feature - v2's own header: "Sections
# with no Helios equivalent (Logo, Print Tolerances, Shaft Gauge Test) are
# omitted"), no "Gauge" key (same reason).
QUALITY_FIELDS_HELIOS = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves",
     "16 twisted friction grooves (v4-only, see the core_shaft note on the Element tab) - slow, off for quick iteration."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    # cyl_fn is now genuinely used (Core()'s shaft-bore facet count, via
    # the v4-only core_shaft reuse - see config/helios.yaml's element
    # section comment) - previously declared-but-unused.
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Core() shaft-bore facet count."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Every other cylinder/revolve in the body (HollowingElement, MinkCleanup, clip...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
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
    ("drive_pin_style", ["element", "drive_pin_style"], int, "Drive pin style", "0=current, 1=old (not ported - will error)."),
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
                     "drive_pin_support_height", "drive_pin_style", "drive_pin_width_offset")
]

LABEL_FIELDS_HAMMOND = [
    ("font_path", ["label", "font_path"], str, "Label font path", "Font for the two engraved Shuttle_Label strings."),
    ("label1", ["label", "label1"], str, "Label 1", "Shuttle_Label1 - e.g. a name."),
    ("label2", ["label", "label2"], str, "Label 2", "Shuttle_Label2 - e.g. a year."),
    ("label_size_mm", ["label", "label_size_mm"], float, "Label text size (mm)", ""),
    ("depth_mm", ["label", "depth_mm"], float, "Label depth (mm)", "Shuttle_Label_Depth."),
]

QUALITY_FIELDS_HAMMOND = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Shuttle arc body (ShuttleCylinder/Rib/PinSupport)."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Mirrors cyl_fn - no separate structural tier."),
    ("text_fn", ["quality", "text_fn"], int, "Text fn", "Glyph curve smoothness."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
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
]

ELEMENT_FIELDS_HAMMOND = [
    ("shrinkage_multiplier", ["element", "shrinkage_multiplier"], float, "Arc shrinkage multiplier", "Shuttle_Arc_Radius_Shrinkage_Multiplier."),
    ("anvil_od", ["element", "anvil_od"], float, "Anvil OD (mm)", "Element_Diameter = this * shrinkage_multiplier."),
    ("anvil_id_raw", ["element", "anvil_id_raw"], float, "Anvil ID raw (mm)", ""),
    ("shuttle_thickness", ["element", "shuttle_thickness"], float, "Shuttle thickness (mm)", "Also the glyph placement protrusion."),
    ("shuttle_text_protrusion", ["element", "shuttle_text_protrusion"], float, "Text protrusion (mm)", ""),
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
# cone height (Mink_Height) is independent of the character's own
# extrusion depth (Glyph_Height, Element tab), unlike every other
# machine's coupled draft-cone convention (see lib/hammond_split.py's
# _letter_text_drafted() docstring) - so it needs its own second knob.
# Like draft_angle_deg elsewhere, whether the draft actually RUNS is never
# a config toggle (Quick Preview always skips it, Render always applies
# it - see tune.py's _run_build) - only its angle/height are tunable here.
FONT_FIELDS_HAMMOND_SPLIT = [
    ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters (Type_Face)."),
    ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Type_Size - em-square size."),
    ("char", ["char_mod", "char"], str, "Modified character(s)", "Char_Mod - characters using the separate font/size below."),
    ("char_mod_font_path", ["char_mod", "char_mod_font_path"], str, "Modified char font path", ""),
    ("char_mod_size_mm", ["char_mod", "char_mod_size_mm"], float, "Modified char size (mm)", "Char_Mod_Size."),
    ("mink_draft_angle_deg", ["build", "mink_draft_angle_deg"], float, "Draft angle (deg)",
     "Mink_Draft_Angle - only takes effect on Render (Quick Preview always skips the draft sweep)."),
    ("mink_height", ["build", "mink_height"], float, "Draft cone height (mm)",
     "Mink_Height - the draft cone's own height, independent of Glyph height (Element tab). "
     "Only takes effect on Render."),
    ("mode", ["alignment", "mode"], str, "Align mode", '"center" or "left".'),
    ("center_offset_mm", ["alignment", "center_offset_mm"], float, "Center offset (mm)", ""),
    ("left_offset_mm", ["alignment", "left_offset_mm"], float, "Left offset (mm)", ""),
    ("modified_left_chars", ["alignment", "modified_left_chars"], str, "Modified-left chars", "Chars getting an extra left shift."),
    ("modified_left_offset_mm", ["alignment", "modified_left_offset_mm"], float, "Modified-left offset (mm)", ""),
    ("modified_right_chars", ["alignment", "modified_right_chars"], str, "Modified-right chars", "Chars getting an extra right shift."),
    ("modified_right_offset_mm", ["alignment", "modified_right_offset_mm"], float, "Modified-right offset (mm)", ""),
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
]

QUALITY_FIELDS_HAMMOND_SPLIT = [
    ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)",
     "Collapses minkowski_sum's CSG noise. 0 disables. Only matters while Minkowski (Build tab) is on."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Arc/Center/Rib/Tube/etc. body facet count."),
    ("mink_fn", ["quality", "mink_fn"], int, "Minkowski fn", "Draft cone segments - only matters while Minkowski (Build tab) is on."),
    ("text_fn", ["quality", "text_fn"], int, "Text fn", "Not currently consumed - v4's freetype pipeline uses Outline density instead."),
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
]

ELEMENT_FIELDS_HAMMOND_SPLIT = [
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
    ("glyph_height", ["element", "glyph_height"], float, "Glyph height (mm)", "Struck character engraving depth."),
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

SECTIONS_BY_MACHINE = {
    "blickensderfer": {**SECTIONS_COMMON, "Logo": LOGO_FIELDS_BLICKPOSTAL,
                       "Quality": QUALITY_FIELDS_BLICKPOSTAL, "Resin": RESIN_FIELDS_BLICKPOSTAL,
                       "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_BLICKENSDERFER},
    "postal": {**SECTIONS_COMMON, "Logo": LOGO_FIELDS_BLICKPOSTAL,
               "Quality": QUALITY_FIELDS_BLICKPOSTAL, "Resin": RESIN_FIELDS_BLICKPOSTAL,
               "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_POSTAL},
    # no "Gauge" key - Mignon has no Shaft Gauge Test (see
    # ELEMENT_FIELDS_MIGNON's neighboring comment) - compose()/
    # _compose_build_tab() check for its absence and skip the tab/dropdown
    # option accordingly, rather than every machine being forced to have one.
    "mignon": {**SECTIONS_COMMON, "Logo": LOGO_FIELDS_MIGNON, "Label": LABEL_FIELDS_MIGNON,
               "Quality": QUALITY_FIELDS_MIGNON, "Resin": RESIN_FIELDS_MIGNON,
               "Element": ELEMENT_FIELDS_MIGNON},
    # no "Gauge" key - Bennett has no Shaft Gauge Test either (v2/bennett.
    # scad:24: "Sections with no Bennett equivalent (Print Tolerances,
    # Shaft Gauge Test) are omitted"). No "Logo" key - its one engraved-
    # text feature is LABEL_FIELDS_BENNETT's "Label" tab instead (see that
    # list's neighboring comment).
    "bennett": {**SECTIONS_COMMON, "Label": LABEL_FIELDS_BENNETT,
                "Quality": QUALITY_FIELDS_BENNETT, "Resin": RESIN_FIELDS_BENNETT,
                "Element": ELEMENT_FIELDS_BENNETT},
    # no "Gauge" key - Helios has no Shaft Gauge Test (v2/heliosklimax.
    # scad's own header: "Sections with no Helios equivalent (Logo, Print
    # Tolerances, Shaft Gauge Test) are omitted"). No "Logo"/"Label" key
    # either - same header, no engraved-text feature at all.
    "helios": {**SECTIONS_COMMON, "Quality": QUALITY_FIELDS_HELIOS, "Resin": RESIN_FIELDS_HELIOS,
               "Element": ELEMENT_FIELDS_HELIOS},
    # no "Gauge"/"Logo" key - Hammond has neither (see lib/hammond.py's
    # module docstring) - its two whole-string engraved labels are the
    # "Label" tab instead, same convention as Bennett.
    "hammond": {**SECTIONS_COMMON, "Label": LABEL_FIELDS_HAMMOND,
                "Quality": QUALITY_FIELDS_HAMMOND, "Resin": RESIN_FIELDS_HAMMOND,
                "Element": ELEMENT_FIELDS_HAMMOND, "Rib": RIB_FIELDS_HAMMOND},
    # no "Gauge"/"Logo" key - same reasons as Hammond above. "Font &
    # Alignment" is overridden (not the shared SECTIONS_COMMON one) - see
    # FONT_FIELDS_HAMMOND_SPLIT's own comment for why (no draft_angle_deg
    # field here, plus the char_mod fields no other machine has).
    "hammond_split": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_HAMMOND_SPLIT,
                       "Label": LABEL_FIELDS_HAMMOND_SPLIT, "Quality": QUALITY_FIELDS_HAMMOND_SPLIT,
                       "Resin": RESIN_FIELDS_HAMMOND_SPLIT, "Element": ELEMENT_FIELDS_HAMMOND_SPLIT},
}

# Static intro banner shown above a section tab's fields, keyed by section
# name - (text, css class). Only sections that need one appear here.
SECTION_INTROS = {
    "Element": ("ADVANCED - real machine dimensions. Rarely need changing.",
                "advanced-warning"),
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

# Postal has exactly ONE named layout preset - v2/postal.scad has only
# one physical layout, no preset-switching menu like Blickensderfer's (see
# LAYOUT_PRESETS above) - so "QWERTY" is both the only option and the
# default (matches config/postal.yaml's own layout.rows exactly: v2's
# Physical_Layout = Keyboard_Layout_Array[row][Element_Layout_Array_Map[col]],
# postal.scad:271-274 - same values, computed once in config/postal.yaml's
# comment rather than re-derived here).
LAYOUT_PRESETS_POSTAL = {
    "QWERTY": [
        "byhnujmik,ol.pqazwsxedcrfvtg",
        "BYHNUJMIK&OL?PQAZWSXEDCRFVTG",
        "!6_+7;=8:§9'-%\"(£2)ä3@ö4/ü5$",
    ],
}

# Mignon's 30 real named layouts from v2/lib/layouts/mignon_layouts.scad's
# Layouts=[] array (33 total minus 3 empty placeholders - CUSTOMLAYOUT,
# DEUTSCH_FRAKTUR_GOTISCH, DEUTSCH_FRAKTUR_PROF_STIEHL - all-empty-string
# rows in the real source, never finished/used there either). A few source
# rows had a 13th character v2 itself never reads (Char_Legend only ever
# indexes 0-11) - truncated to 12 to match what v2 actually uses (Georgian
# rows 2/4, Greek rows 3/4).
#
# Stored here in RAW KEYBOARD-LEGEND order - i.e. v2's own `Layout` array,
# exactly as printed on the physical keyboard/manual - NOT the Char_Legend-
# remapped `Physical_Layout` order used for actual glyph placement. The two
# differ by a fixed rotation: physical = keyboard[7:12] + keyboard[0:7]
# (Char_Legend=[7,8,9,10,11,0,1,2,3,4,5,6]), equivalently keyboard =
# physical[5:] + physical[:5] - the exact "move the first 5 characters to
# the end" transform the user asked for, applied once here to what used to
# be stored (physical order, from the original import) to reach the
# canonical keyboard-legend representation. mignon.py's configure() applies
# the Char_Legend remap itself when loading layout.rows into DHIATENSOR, so
# the actual built geometry is unchanged - only this display/edit
# representation moved to match what a person reads off the machine.
LAYOUT_PRESETS_MIGNON = {
    'English 2': [
        '\'"%&(£$);:,.',
        '?PFUGQpfugq¼',
        '!VINABvinab½',
        '_LDETMldetm¾',
        'JKOSRZkosrzj',
        '/YCHWXychwx@',
        '#1234567890-',
    ],
    'English 3': [
        '()&\'".,:¼½¾⅛',
        '?PFUGQpfugq⅜',
        '=VINABvinab⅝',
        '+LDETMldetm⅞',
        'JKOSRZkosrzj',
        '/YCHWXychwx_',
        '£23456789%@-',
    ],
    'English 4': [
        '()&\'".,:¼½¾⅛',
        '?PFUGQpfugq⅜',
        '=VINABvinab⅝',
        '$LDETMldetm⅞',
        'JKOSRZkosrzj',
        '/YCHWXychwx_',
        '£23456789%@-',
    ],
    'German 2': [
        '§%&():,.äöü¾',
        '"PFUGQpfugq½',
        '?VINABvinab¼',
        "_LDETMldetm'",
        'JKOSRZkosrzj',
        '/YCHWXychwx!',
        '„1234567890-',
    ],
    'German 4': [
        '&():"!?\'äöü_',
        '§PFUGQpfugq;',
        'JVINABvinabj',
        '/LDETMldetm,',
        '%KOSRZkosrz=',
        '¾YCHWXychwx+',
        '½¼23456789.-',
    ],
    'German-French': [
        '§%&():,.äöüè',
        '"PFUGQpfugqà',
        '?VINABvinabé',
        "_LDETMldetm'",
        'JKOSRZkosrzj',
        '/YCHWXychwxç',
        '^1234567890-',
    ],
    'Bohemian 3': [
        '!?´%23456789',
        'PFUGJpfugjů"',
        'VNIABvniabíá',
        'LDETMldetméě',
        'KOSRZkosrzšř',
        'YCHWXychwxžú',
        '&ˇ§Qqýč/,:.-',
    ],
    'Bulgarian': [
        '§ЮЯЛЦVюялць&',
        '№ПРХСУпрхсуй',
        '/ЩШКАМщшкам!',
        'ЗОВЪТѢовътѣз',
        '%ГИНЕДгинед?',
        'IЖФѪБЧжфѫбч"',
        '2456789.-,;:',
    ],
    'Cyrillic': [
        '§%№VI:"!,?=-',
        'ЂПФУГJпфугjђ',
        'ЧВИНАБвинабч',
        'ШЛДЕТМлдетмш',
        'ЋКОСРЗкосрзћ',
        'ЏЉЦХЊЖљцхњжџ',
        '/123456789._',
    ],
    'Danish 2': [
        'Æ§&?()_\'¨:"æ',
        'ØPFUGQpfugqø',
        'JVINABvinabj',
        '%LDETMldetm,',
        '/KOSRZkosrz÷',
        '¼YCHWXychwx+',
        '½¾23456789.-',
    ],
    'Danish 3': [
        'Æ§&?()_\'¨:"æ',
        'ØPFUGQpfugqø',
        'JVINABvinabj',
        '%LDETMldetm,',
        '/KOSRZkosrz÷',
        '¼YCHWXychwx+',
        '½¾23456789.=',
    ],
    'Esperanto': [
        '()23456789é"',
        "'PFUGQpfugq:",
        '!VINABvinab.',
        '?LDETMldetm,',
        'JKOSRZkosrzj',
        '^YCHWXychwx-',
        'ĴŜĈĤĜŬŝĉĥĝŭĵ',
    ],
    'French 3': [
        'K&()?:,"_çùk',
        'WJFQBYjfqbyw',
        '§VNIAPvniapà',
        "/DOUT'doutéè",
        '%CSERGcserg^',
        '½HLMZXhlmzx+',
        '¼23456789.-=',
    ],
    'Georgian': [
        '[]!":.,-;?*\'',
        'IV&წძცყქღჷა^',
        'XCგბეიულტჲ¨=',
        'LDჩუმდაႱზჱ§,',
        '$Mჴვროთხნჵჶ№',
        '£§ჰჭჟჯფპკ#ჳ/',
        '1234567890%½',
    ],
    'Greek (new ortography)': [
        '£123456789-;',
        "&ΠΡΚΓΞπρκγξ'",
        '½ΛΤΗΑΒλτηαβ͂',
        '¼ΜΔΕΝΨμδενψ̇',
        '_ΘΟΥΙΖθουιζ.',
        '%ΧΩΣͅΦχωσϛφ,',
        '$()/„῟῞῏῎´᾿¨',
    ],
    'Dutch 2': [
        '&():"?\'¨`^´_',
        '£PFUGQpfugqĳ',
        'JVINABvinabj',
        '/LDETMldetm,',
        '%KOSRZkosrz+',
        '¾YCHWXychwx=',
        '½¼2345ƒ6789.',
    ],
    'Italian 3': [
        '"%&()^àèìòùé',
        '?WFUGQwfugq!',
        'JVINABvinabj',
        "_LDETMldetm'",
        '=KOSRZkosrz,',
        '/YCHPXychpx:',
        '+º23456789.-',
    ],
    'Croatian-Slovenian': [
        '%+=_:,.!?"-´',
        '&PFUGKpfugkć',
        'QVINAJvinajq',
        'ĐLDETMldetmđ',
        '§ČOSŠZčosšz/',
        'WBCHRŽbchržw',
        'YX23456789xy',
    ],
    'Latvian': [
        '32ļģŗņķ?!=/̦',
        '4PFUGCpfugc"',
        '5VINABvinab-',
        '6LDETMldetm,',
        '7KOSRZkosrz.',
        '8HJX%§hjxāūē',
        '9ČŠŽ()čšžī:̄',
    ],
    'Lithuanian': [
        "!'23456789;-",
        'ŲPFUGĄpfugąų',
        'ĮVINABvinabį',
        ',LDETMldetm?',
        '_KOSĘZkosęz/',
        '.YCHRJychrj"',
        '%ŽĖŠČŪžėščū§',
    ],
    'Polish 2': [
        '?§&óśńźćąę\'"',
        '%PFUGQpfugq!',
        'ŻVINABvinabż',
        'ŁLDETMldetmł',
        'JKOSRZkosrzj',
        '/YCHWXychwx,',
        '|:23456789.-',
    ],
    'Portuguese 2': [
        '&?Ç!º̃áéêóç#',
        '%PFUGQpfugq£',
        ':VINABvinab$',
        '(LDETMldetm)',
        'JKOSRZkosrzj',
        "'YCHWXychwx,",
        '"/23456789.-',
    ],
    'Romanian 1': [
        '§W()"?w\';:!_',
        '&KFOMHkfomhî',
        '/DCESBdcesbș',
        '=GPARUgparuă',
        '+LTINVltinvț',
        '%YXJZQyxjzqâ',
        '½23456789,.-',
    ],
    'Russian (new ortography)': [
        '№ХЬЯЛУхьялу!',
        '1ТГСЮЙтгсюй/',
        '2РПОИЫрпоиы"',
        '3ЧВЕНДчвендз',
        "4ЦАМКБцамкб'",
        '5ЖЩШЭФжщшэф.',
        '6789%$£§/,:-',
    ],
    'Russian 3': [
        'ЭХЯЛЬГэхяльг',
        'ОПРСЮУпрсюуо',
        'IЩШЧТНщшчтнi',
        'ЗФЦКАЕфцкаез',
        '2БИМВДбимвд?',
        '4ЖЙЫЪѢжйыъѣ!',
        '56789№§.-:,/',
    ],
    'Spanish-American': [
        '&?¿!¡;áéíóúñ',
        '%PFUGQpfugq£',
        ':VINABvinab$',
        '(LDETMldetm)',
        'JKOSRZkosrzj',
        "'YCHWXychwx,",
        '"/23456789.-',
    ],
    'International Script': [
        '123456789-,_',
        '&PFUGQpfugq.',
        'JVINABvinabj',
        '=LDETMldetmé',
        '%KOSRZkosrzç',
        '/YCHWXychwx:',
        '§!?()"´`^ˇ˚˜',
    ],
    'Swedish 2': [
        '§()ÄÖ:"\',äö+',
        'QPFUGÅpfugåq',
        '?VINABvinab=',
        '&LDETMldetm_',
        '%KOSRJkosrj.',
        'XYCHWZychwzx',
        '/¼½¾23456789',
    ],
    'Ukrainian': [
        'ҐХЯЛЬГґхяльг',
        "%ПРСЮУпрсюу'",
        'IЩШЧТНщшчтнi',
        '2ФЦКАЕфцкае?',
        'ЗБИМВДбимвдз',
        '4ЖОЙЄЇжойєї!',
        '56789№§.-:,/',
    ],
    'Hungarian 2': [
        '?:!"ÖÜ,űőöüú',
        'ÉPFUGYpfugyé',
        'ÓVINABvinabó',
        'ÁLDETMldetmá',
        'JKOSRZkosrzj',
        '/QCHWXqchwx.',
        '+%23456789§-',
    ],
}

# Bennett's 4 named layouts, ported verbatim from v2/lib/layouts/
# bennett_layouts.scad's ENGLISH/BRITISH/INTERNATIONAL arrays plus
# v2/bennett.scad's own CUSTOMLAYOUT (Lowercase/Uppercase/Figs - identical
# content to ENGLISH by default, a real, if redundant, 4th LAYOUTS entry
# in v2's own source, not an omission here). All 4 share the same
# 3-row/28-column structure and identity placement_map. Rows are shown in
# keyboard-legend order (as printed on the physical keyboard), matching
# config/bennett.yaml's layout.char_legend remap - see lib/bennett.py's
# configure().
LAYOUT_PRESETS_BENNETT = {
    "ENGLISH": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"#$%56;?:,£@_(&-)/'.",
    ],
    "BRITISH": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"¾$%56;?:½£@_(&-)/'¼",
    ],
    "CUSTOM": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"#$%56;?:,£@_(&-)/'.",
    ],
    "INTERNATIONAL": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKLÖZXCVGHBNMÄ",
        "1234789üà#£%56?Ååö§@:(&-)/\"ä",
    ],
}

# Helios's 2 inline layout arrays from v2/heliosklimax.scad's [Key
# Mapping] section - GERMAN and GERMAN_MOD (LAYOUT=GERMAN_MOD is what v2
# actually assigns/uses; GERMAN is a real, if superseded, second array in
# the source, exposed here the same way Bennett's redundant CUSTOM preset
# is). Both share the same 4-row/21-column structure and identity
# placement_map (Physical_Layout=LAYOUT directly, no CharLegend remap).
LAYOUT_PRESETS_HELIOS = {
    "GERMAN_MOD": [
        "wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
        "\"()Z⁄J=,;XY¢ß&%/-_§?Q",
    ],
    "GERMAN": [
        "wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
        "\"()Z⅟J=,;XY₰ß&%/-_§?Q",
    ],
}

# v2/lib/layouts/hammond_layouts.scad's LAYOUTS[0]/LAYOUTS[2] (Normal_U/
# Math_U) - the two real presets that differ in ROW COUNT (3 vs 4), which
# no other machine's layout presets do. "Math Universal" is the "math
# shuttle" variant - confirmed identical in v1/Hammond/HammondShuttle.scad
# (the pre-v2-migration original), nothing extra hiding there. Is_Math
# auto-derives from len(rows)==4 (lib/hammond.py's configure()), so
# selecting this preset alone is enough to switch Shuttle_Height/the Xx
# resin-support array - see LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE below
# for how baseline_row/cutout_row (which ALSO need a 4th entry for this
# preset) get resized to match.
LAYOUT_PRESETS_HAMMOND = {
    "Normal Universal": [
        "-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1",
    ],
    "Math Universal": [
        "√·p.lo,kimjunhybgtvfrcdexswzaq",
        "∫:P∂LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0>)9<(8|'7*÷6]Γ5[∝4+Δ3×∑2_\"1",
        "―ₙ₀πλ₉ωκ₈φε₇τη₆βγ₅θψ₄ρδ₃ξσ₂ζα₁",
    ],
}

# layout.baseline_row/cutout_row that go WITH each of the row-count-
# varying presets above - only Hammond needs this (every other machine's
# presets keep the machine's one fixed row count). Applied in
# _save_to_yaml alongside patch_yaml_rows, since the generic per-row
# Input widgets (BASELINE_CUTOUT_KEYS) are sized for whatever row count
# was on disk at compose() time and can't grow/shrink themselves mid-
# session - see SESSION_LOG.md's Hammond chapter.
LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE = {
    "hammond": {
        "Normal Universal": [3.74, -1.21, -5.71],
        "Math Universal": [3.74, -1.21, -5.71, -9.89],
    },
}

LAYOUT_PRESETS_BY_MACHINE = {
    "blickensderfer": LAYOUT_PRESETS,
    "postal": LAYOUT_PRESETS_POSTAL,
    "mignon": LAYOUT_PRESETS_MIGNON,
    "bennett": LAYOUT_PRESETS_BENNETT,
    "helios": LAYOUT_PRESETS_HELIOS,
    "hammond": LAYOUT_PRESETS_HAMMOND,
}

# Layout tab's picker-help banner, one flowing string per machine (see
# CLAUDE.md's tooltip/help-text rules - no manual \n; add the next
# machine's entry here instead of an if/elif in _compose_layout_tab).
LAYOUT_PICKER_HELP = {
    "blickensderfer": (
        "All layouts share the same physical placement_map - only glyph "
        "content per row changes. HEBREW_ENGL needs a Hebrew-capable font "
        "path; v4 doesn't auto-switch fonts per layout like v2 did."
    ),
    "postal": (
        "Postal has only one physical layout, QWERTY. Use Modify glyphs "
        "below to hand-edit the rows for anything else."
    ),
    "mignon": (
        "30 named layouts, all sharing the same 7-row/12-column physical "
        "layout - only glyph content changes per row. Rows are shown in "
        "keyboard-legend order; char_legend remaps this to build order "
        "internally."
    ),
    "bennett": (
        "Ported from v2/lib/layouts/bennett_layouts.scad's ENGLISH/BRITISH/"
        "INTERNATIONAL plus v2/bennett.scad's own CUSTOM (identical to "
        "ENGLISH by default - edit it via Modify glyphs below). All share "
        "the same 3-row/28-column layout. Rows are shown in keyboard-legend "
        "order (as printed on the physical keyboard/manual) - "
        "layout.char_legend remaps this to build order internally."
    ),
    "helios": (
        "GERMAN_MOD is v2's real default/only-used layout; GERMAN is a "
        "second array present in the source but superseded there. Both "
        "share the same 4-row/21-column physical layout, identity "
        "placement_map."
    ),
    "hammond": (
        "Math Universal has 4 rows instead of 3 - selecting it switches "
        "Shuttle_Height and the resin-support layout to the Math shuttle "
        "variant automatically (Is_Math is derived from the row count, "
        "not a separate toggle), and resizes baseline_row/cutout_row to "
        "match. Both are real v2 presets - v1's original source has "
        "nothing extra beyond these two."
    ),
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
    (Math Universal is 4 rows, everything else 3): the Element tab
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
    cutout_row growing from 3 to 4 entries when the Math Universal layout
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


class ReflowingRichLog(RichLog):
    """RichLog only wraps text at write()-time - the width used for each
    line is computed once (from the widget's CURRENT scrollable width,
    per RichLog.write()'s own default expand=False/shrink=True logic)
    and baked permanently into the stored Strip objects. It is NOT
    recomputed on resize (confirmed by reading RichLog's own source -
    its on_resize() only flushes deferred first-render writes, nothing
    else touches already-written lines). Reported: "if i expand it, the
    console text history stays constricted... if its wide and i shrink
    it, it goes off page" - both are exactly this: old lines stay
    wrapped at whatever width was current when they were written.

    Keeps its own plain-text history and fully re-writes it (clear() +
    write() every stored line) whenever this widget's OWN width actually
    changes after its first known size, so resizing genuinely reflows
    the existing scrollback instead of leaving it wrapped stale. Skips
    the very first resize (before `_size_known` was already true) since
    that's RichLog's own initial-size-becomes-known event, already
    handled by the base class's deferred-render flush - re-writing there
    too would duplicate every line written before the widget was first
    sized."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: list[str] = []
        self._reflow_width: int | None = None

    def write(self, content, *args, **kwargs):
        if isinstance(content, str):
            self._history.append(content)
        return super().write(content, *args, **kwargs)

    def on_resize(self, event: Resize) -> None:
        had_known_size = self._size_known
        super().on_resize(event)
        new_width = event.size.width
        if had_known_size and new_width and new_width != self._reflow_width and self._history:
            super().clear()
            for line in self._history:
                super().write(line)
        self._reflow_width = new_width


class TuneApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #form { width: 58; height: 100%; border: solid $accent; }
    #log-pane { width: 1fr; height: 100%; border: solid $accent; padding: 0 1; }
    #log { height: 1fr; }
    #progress-row { height: 1; margin-top: 1; }
    #build-progress { width: 1fr; }
    #build-progress Bar { width: 1fr; }
    #build-elapsed { width: auto; margin-left: 1; color: $text-muted; }
    TabbedContent { height: 1fr; }
    TabPane { padding: 0 1; }
    .field-row { height: auto; margin-bottom: 1; }
    .field-row Horizontal { height: 1; }
    .field-label { width: 26; height: 1; content-align: left middle; }
    .field-row Input { width: 1fr; height: 1; border: none; padding: 0 1; background: $panel; }
    .field-row Switch { width: auto; height: 1; border: none; padding: 0; }
    .field-row Select { width: 1fr; height: 1; border: none; }
    .field-row Select > SelectCurrent { border: none; padding: 0 1; background: $panel; }
    .browse-btn { width: 10; height: 1; min-width: 10; border: none; margin-left: 1; }
    .field-help { color: $text-muted; height: auto; }
    #buttons { height: 11; dock: bottom; padding: 0 1; }
    #btn-render-test-text { height: 3; width: 1fr; text-style: bold; margin-bottom: 1; }
    #primary-buttons { height: 5; }
    #primary-buttons Button { width: 1fr; height: 5; text-style: bold; }
    #f3d-row { height: 1; margin-top: 1; }
    #f3d-row .field-label { width: auto; margin-right: 1; }
    #f3d-row Switch { width: auto; height: 1; border: none; padding: 0; }
    #status { height: 1; color: $text-muted; padding: 0 1; }
    #status-row { height: 1; padding: 0 1; }
    #status-row .browse-btn { margin-left: 0; }
    #btn-reset-defaults { width: 1fr; height: 1; border: none; margin-left: 1; }
    #btn-change-machine { width: 1fr; height: 1; border: none; margin-left: 1; }
    #machine-picker { width: 100%; height: 100%; align: center middle; }
    .picker-title { text-style: bold; content-align: center middle; width: auto; margin-bottom: 1; }
    .picker-subtitle { color: $text-muted; content-align: center middle; width: auto; margin-bottom: 1; }
    .machine-picker-btn { width: 30; height: 3; margin-bottom: 1; text-style: bold; }
    .advanced-warning { color: $warning; text-style: bold; height: auto; padding: 0 0 1 0; }
    .picker-row { height: 3; }
    .picker-help { color: $text-muted; height: auto; }
    .row-preview { height: 1; background: $panel; padding: 0 1; margin-bottom: 1; color: $text-muted; }
    #layout-custom-rows { height: auto; }
    .custom-row-input { height: 1; margin-bottom: 1; border: none; padding: 0 1;
        background: $panel; border-left: thick $warning; }
    #type-test-text { height: 8; }
    """
    BINDINGS = [
        # "q" alone doesn't fire while any Input/TextArea has focus - a
        # focused text widget consumes plain letter keys as literal
        # typed characters instead of letting them reach app-level
        # bindings (confirmed: pressing "q" while typing just appends a
        # "q" to the field, quit never happens - this is what "quitting
        # with q, Type Test doesn't save" turned out to actually be:
        # not a save bug, this key silently never fired). ctrl+q is a
        # control combination, not a printable character, so text
        # widgets never intercept it - always works. Kept "q" too since
        # it's still fine (and documented in the footer) whenever
        # nothing has focus, e.g. right after clicking a button.
        ("q", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("p", "preview", "Quick Preview"),
        ("b", "render", "Render"),
        ("s", "save", "Save"),
        ("r", "reload", "Reload from file"),
    ]

    def __init__(self, config_path=None):
        super().__init__()
        self.inputs = {}
        self._last_build_info = None
        self._f3d_proc = None
        self._f3d_out_path = None  # see _ensure_f3d_after_build's own comment
        self._warned_no_wmctrl = False
        # kill any f3d we launched when this app exits, whether that's a
        # normal 'q' quit (atexit fires once python3 tune.py's process
        # shuts down normally) or the terminal itself getting closed
        # (SIGHUP/SIGTERM, registered in on_mount - see there for why
        # plain signal.signal() isn't used)
        atexit.register(self._kill_f3d)
        # self.machine is None until a machine is picked - compose()
        # shows the machine-picker screen in that state (see
        # _compose_machine_picker), the full tuner form otherwise. Passing
        # a config_path (the old CLI usage, `python3 tune.py config/x.yaml`)
        # skips the picker and loads straight into that config's machine,
        # for backward compat / power users who already know what they want.
        self.machine = None
        if config_path is not None:
            self._load_machine(config_path)

    def _load_machine(self, config_path):
        """Bootstraps all machine/config-dependent state (master/running
        config split, self.cfg, and the per-machine SECTIONS/FIELDS/
        LAYOUT_PRESETS - see SECTIONS_BY_MACHINE's comment) from a given
        master config path. Called once at startup if a config_path was
        given on the command line, or from the machine picker
        (_select_machine) otherwise - either way, compose()/recompose()
        must run AFTER this, since the tuner form's shape (Element tab's
        field set, Layout tab's presets) depends on self.machine."""
        self.master_config_path = os.path.abspath(config_path)
        self.config_path = self._running_config_path(self.master_config_path)
        self._ensure_running_config()
        self._migrate_running_config()  # no log_line here - RichLog isn't mounted yet
        self.inputs = {}
        self._load_current()
        self.machine = self.cfg.get("machine", "blickensderfer")
        self.SECTIONS = SECTIONS_BY_MACHINE.get(self.machine, SECTIONS_BY_MACHINE["blickensderfer"])
        self.FIELDS = [field for fields in self.SECTIONS.values() for field in fields]
        self.LAYOUT_PRESETS = LAYOUT_PRESETS_BY_MACHINE.get(self.machine, {})
        # row count varies per machine (3 for Blickensderfer/Postal, 7 for
        # Mignon) - see BASELINE_CUTOUT_KEYS' module comment. Hammond's
        # own presets additionally vary in row count from EACH OTHER
        # (Math Universal is 4 rows, everything else is 3) - using just
        # the CURRENT config's row count here would only ever show 3
        # editable baseline/cutout fields, with no way to reach/edit a
        # 4th row until some other action (switching machine and back,
        # restarting) happened to recompose the form with 4 rows on disk.
        # Using the max across every real preset for this machine (falling
        # back to the current config if there are no presets, or it
        # somehow exceeds all of them) means the 4th row field always
        # exists and is editable, even when the 3-row preset is currently
        # selected (it's just not consulted by TextRing in that case).
        n_rows = max([len(self.cfg["layout"]["baseline_row"])]
                     + [len(rows) for rows in self.LAYOUT_PRESETS.values()])
        self.BASELINE_CUTOUT_KEYS = [f"{arr}_{i}" for arr in ("baseline_row", "cutout_row") for i in range(n_rows)]

    @staticmethod
    def _running_config_path(master_path):
        d = os.path.dirname(master_path)
        stem, ext = os.path.splitext(os.path.basename(master_path))
        return os.path.join(d, f"{stem}.running{ext}")

    def _ensure_running_config(self):
        if not os.path.exists(self.config_path):
            shutil.copy2(self.master_config_path, self.config_path)

    def _migrate_running_config(self):
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
        with open(self.master_config_path) as f:
            master_text = f.read()
        master_cfg = yaml.safe_load(master_text)
        with open(self.config_path) as f:
            running_text = f.read()
        running_cfg = yaml.safe_load(running_text) or {}
        migrated = []

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
                sub_m = re.search(rf'(^|\n)((?:[ \t]*#[^\n]*\n)*[ \t]+{re.escape(sk)}:.*?)(?=\n[ \t]*\S|\Z)',
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
            with open(self.config_path, "w") as f:
                f.write(running_text)
        return migrated

    def _status_text(self):
        # kept short - #status is squeezed into a 1-row-tall Horizontal
        # alongside the Browse/Reset to Defaults/Change Machine buttons,
        # no wrapping; the full explanation lives in the module docstring
        machine_label = MACHINES.get(self.machine, (self.machine,))[0]
        master_rel = os.path.relpath(self.master_config_path, REPO_ROOT)
        return f"machine: {machine_label}  |  master: {master_rel}"

    def _kill_f3d(self):
        if self._f3d_proc is not None and self._f3d_proc.poll() is None:
            self._f3d_proc.terminate()
        # Reset immediately (don't wait for the OS to reap the terminated
        # process) - _ensure_f3d_after_build's "is it already running"
        # check uses this same attribute, and the app keeps running after
        # a call here (unlike the atexit/quit callers), so the NEXT build
        # must see "not running" right away and launch fresh, not race
        # against .poll() still returning None for a moment after
        # .terminate() (SIGTERM is asynchronous).
        self._f3d_proc = None
        self._f3d_out_path = None

    def _save_before_exit(self):
        # Every build action (Preview/Render/Render Test Text) already
        # saves the whole form unconditionally before running - but just
        # typing into a field and quitting without ever clicking one of
        # those saved nothing, which reads as "it's not saving" (reported
        # specifically for Type Test's text/CPI/LPI, easy to edit and
        # quit without an intervening render). Quitting now saves too,
        # consistent with everything else. Skips saving (not quitting)
        # on a bad value - _collect_values() already logs why - since
        # trapping the user in the app over a typo would be worse.
        #
        # self.machine is None (never picked a machine, still on the
        # picker screen - no config loaded, self.FIELDS/self.SECTIONS
        # never set) means there's nothing to collect/save at all -
        # quitting from the picker used to crash here with an
        # AttributeError on self.FIELDS.
        if self.machine is None:
            return
        values = self._collect_values()
        if values is not None:
            self._save_to_yaml(values)

    async def on_mount(self) -> None:
        # plain signal.signal() handlers can sit unfired for a long time
        # while asyncio's event loop is blocked in epoll_wait - the
        # loop's own add_signal_handler uses its self-pipe wakeup so the
        # handler actually runs promptly (confirmed via a real SIGTERM
        # test: the signal.signal() version left the f3d child alive).
        # Must be called from a running loop, hence on_mount not __init__.
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
            if sig is None:
                continue
            try:
                loop.add_signal_handler(sig, self._handle_term_signal)
            except (NotImplementedError, RuntimeError):
                pass  # e.g. unsupported on this platform

    def _handle_term_signal(self):
        # add_signal_handler fully replaces the OS default disposition -
        # without also exiting here, the signal would just be silently
        # swallowed and tune.py would keep running instead of quitting
        self._save_before_exit()
        self._kill_f3d()
        self.exit()

    async def action_quit(self) -> None:
        self._save_before_exit()
        self.exit()

    def _load_current(self):
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)

    def _current_layout_preset(self):
        current_rows = self.cfg.get("layout", {}).get("rows")
        for name, rows in self.LAYOUT_PRESETS.items():
            if rows == current_rows:
                return name
        return None  # custom/unrecognized - leave as-is unless explicitly changed

    def _update_row_widget(self, id_prefix, i, value):
        """Sets a #{id_prefix}-{i} widget's displayed value if a matching
        widget actually exists - silently no-ops otherwise instead of
        raising. Needed because Hammond's layout presets can have a
        DIFFERENT row count than whatever was on disk at compose() time
        (Math Universal is 4 rows, everything else is 3) - the per-row
        preview/edit widgets are a fixed set sized once at compose time
        and can't grow reactively when a longer preset is picked
        mid-session. A recompose (switching machine and back, or
        restarting) picks up the new row count properly; this just
        avoids crashing in the meantime."""
        try:
            w = self.query_one(f"#{id_prefix}-{i}")
        except NoMatches:
            return
        if isinstance(w, Static):
            w.update(value)
        else:
            w.value = value

    def _compose_section_tab(self, section):
        fields = self.SECTIONS[section]
        tab_id = f"tab-{section.lower().replace(' ', '-').replace('&', 'and')}"
        with TabPane(section, id=tab_id):
            with VerticalScroll():
                intro = SECTION_INTROS.get(section)
                if intro:
                    text, css_class = intro
                    yield Static(text, classes=css_class)
                for key, path, typ, label, help_text in fields:
                    current = get_nested(self.cfg, path)
                    with Vertical(classes="field-row"):
                        with Horizontal():
                            yield Static(label, classes="field-label")
                            if typ is bool:
                                sw = Switch(value=bool(current), id=f"field-{key}")
                                self.inputs[key] = sw
                                yield sw
                            elif key == "mode":
                                val = str(current) if str(current) in ("center", "left") else "center"
                                sel = Select([("center", "center"), ("left", "left")],
                                             value=val, id=f"field-{key}", allow_blank=False)
                                self.inputs[key] = sel
                                yield sel
                            else:
                                inp = Input(value=str(current), id=f"field-{key}")
                                self.inputs[key] = inp
                                yield inp
                                if key in FONT_PATH_FIELD_KEYS:
                                    yield Button("Browse", id=f"browse-{key}", classes="browse-btn")
                        if help_text:
                            yield Static(help_text, classes="field-help")
                if section == "Element":
                    yield from self._compose_baseline_cutout_fields()

    # layout.baseline_row/cutout_row - per-row (lowercase/uppercase/figs)
    # inline numeric arrays, calibrated via the Calibration tab (see
    # cylinder_machine.CalibrationTextRing) and previously only editable
    # by hand in the YAML (list-valued, doesn't fit the generic FIELDS
    # mechanism's one-scalar-per-key assumption). Bespoke like Layout's
    # custom rows / Type Test's fields, using patch_yaml_list_item to
    # patch a single element of the inline list rather than the whole
    # thing. self.inputs keys are "baseline_row_{i}"/"cutout_row_{i}",
    # not in self.FIELDS - _collect_values/_save_to_yaml/
    # _refresh_widgets_from_cfg handle them explicitly, same pattern as
    # the Layout/Type Test tabs' own bespoke widgets.
    # Only meaningful for Blickensderfer/Postal's 3 real shift rows
    # (lowercase/uppercase/figs) and Hammond's 4th row (the Math
    # Universal preset's own extra row, no shift-key equivalent - just
    # labeled "math" so it isn't shown as an unlabeled row when that
    # preset's selected) - Mignon's 7 rows have no such semantic names
    # (v2 itself has no per-row label concept, see lib/glyph_pipeline.
    # scad's Row_Labels comment: "default: numeric 'row N'" for machines
    # with no 3-entry meaning). Rows beyond this list's length just show
    # as "Row N" with no parenthetical.
    ROW_LABELS = ["lowercase", "uppercase", "figs", "math"]

    def _compose_baseline_cutout_fields(self):
        yield Static(
            "Per-row baseline/platen-cutout (mm). See the Calibration tab "
            "to find these empirically.",
            classes="picker-help")
        # n_rows is the max across every real preset for this machine
        # (see BASELINE_CUTOUT_KEYS' own comment) - may exceed the
        # CURRENTLY selected preset/config's own row count (e.g. Hammond's
        # 3-row Normal Universal vs. its 4-row Math Universal), so every
        # row up to n_rows is always composed/editable here, even ones
        # not used by the layout that's active right now - missing values
        # (not yet present in self.cfg) default to 0.0, a "not set yet"
        # placeholder the user can just type over.
        n_rows = len(self.BASELINE_CUTOUT_KEYS) // 2
        for arr_key, label in (("baseline_row", "Baseline"), ("cutout_row", "Cutout")):
            values = self.cfg["layout"][arr_key]
            for i in range(n_rows):
                key = f"{arr_key}_{i}"
                row_label = f" ({self.ROW_LABELS[i]})" if i < len(self.ROW_LABELS) else ""
                current = values[i] if i < len(values) else 0.0
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static(f"{label} row {i}{row_label}", classes="field-label")
                        inp = Input(value=str(current), id=f"field-{key}")
                        self.inputs[key] = inp
                        yield inp

    def _display_rows_for_preset(self):
        """The 3 rows to show as the read-only "original" reference,
        reflecting DISK state (self.cfg) - correct at compose()/
        _refresh_widgets_from_cfg() time, when the dropdown and self.cfg
        are still in sync. NOT correct for reacting to the dropdown
        itself changing (see _rows_for_layout_select_value) - self.cfg
        only updates on an actual save, so this would keep returning the
        OLD preset's rows while the user is still just browsing the
        dropdown pre-save."""
        preset_now = self._current_layout_preset()
        return self.LAYOUT_PRESETS[preset_now] if preset_now else self.cfg["layout"]["rows"]

    def _rows_for_layout_select_value(self, value):
        """The 3 rows to preview for a given #layout-select VALUE
        (typically its live current value, mid-browse and not yet
        saved) - the preset's own rows, or self.cfg's current custom
        rows for Select.NULL/an unrecognized value."""
        if value is Select.NULL or value not in self.LAYOUT_PRESETS:
            return self.cfg["layout"]["rows"]
        return self.LAYOUT_PRESETS[value]

    def _compose_layout_tab(self):
        # named-layout picker only - latitude_columns must stay in sync
        # with placement_map/the physical layout, so it's not exposed
        # here (edit it directly in the YAML if you really mean to)
        char_cap = len(self.cfg["layout"]["placement_map"])
        with TabPane("Layout", id="tab-layout"):
            with VerticalScroll():
                with Vertical(classes="picker-row"):
                    yield Static("Keyboard layout", classes="field-label")
                    preset_now = self._current_layout_preset()
                    options = [(name, name) for name in self.LAYOUT_PRESETS]
                    prompt = "(custom - not a known preset)" if options else "(no named presets for this machine)"
                    select = Select(options, value=preset_now if preset_now else Select.NULL,
                                    id="layout-select", allow_blank=True, prompt=prompt)
                    yield select
                if self.machine in LAYOUT_PICKER_HELP:
                    yield Static(LAYOUT_PICKER_HELP[self.machine], classes="picker-help")
                elif options:
                    yield Static(
                        "Use Modify glyphs below to hand-edit the rows for anything "
                        "other than the selected preset.",
                        classes="picker-help")
                else:
                    yield Static(
                        "No named layout presets yet - use Modify glyphs below to edit "
                        "the rows directly.",
                        classes="picker-help")

                yield Static("Rows (read-only preview of the preset above):", classes="field-label")
                display_rows = self._display_rows_for_preset()
                for i in range(len(display_rows)):
                    static = Static(display_rows[i], id=f"layout-original-row-{i}", classes="row-preview")
                    yield static

                with Horizontal(classes="picker-row"):
                    yield Static("Modify glyphs", classes="field-label")
                    modify_now = bool(self.cfg["layout"]["modify_glyphs"])
                    sw = Switch(value=modify_now, id="layout-modify-glyphs")
                    yield sw
                yield Static(
                    f"Unlocks {len(display_rows)} hand-editable rows, max {char_cap} "
                    "characters each. Shorter rows just leave some positions unstruck. "
                    "While on, this edited copy (not the preset above) is what gets saved.",
                    classes="picker-help")

                custom_rows_container = Vertical(id="layout-custom-rows")
                custom_rows_container.display = modify_now
                with custom_rows_container:
                    current_rows = self.cfg["layout"]["rows"]
                    for i in range(len(current_rows)):
                        inp = Input(value=current_rows[i], id=f"layout-custom-row-{i}",
                                    max_length=char_cap, classes="custom-row-input")
                        yield inp

    def _compose_build_tab(self):
        has_gauge = "Gauge" in self.SECTIONS
        is_hammond = self.machine == "hammond"
        is_hammond_split = self.machine == "hammond_split"
        hammond_parts = ("none",) if is_hammond else ()
        valid_targets = ("element", "calibration") + (("gauge",) if has_gauge else ()) + hammond_parts
        with TabPane("Build", id="tab-build"):
            with VerticalScroll():
                with Vertical(classes="picker-row"):
                    yield Static("Build target", classes="field-label")
                    if is_hammond:
                        # Consolidates the old target dropdown (Shuttle/
                        # Calibration Shuttle/None) + separate Rib checkbox
                        # into one control - see HAMMOND_BUILD_TARGET_GROOVE's
                        # own comment for exactly what (target, groove) pair
                        # each option maps to.
                        target_now = self.cfg.get("build", {}).get("target", "element")
                        groove_now = bool(self.cfg.get("element", {}).get("groove"))
                        value_now = _hammond_build_dropdown_value(target_now, groove_now)
                        yield Select(HAMMOND_BUILD_OPTIONS, value=value_now,
                                     id="build-select", allow_blank=False)
                    else:
                        target_now = self.cfg.get("build", {}).get("target", "element")
                        if target_now not in valid_targets:
                            target_now = "element"
                        options = [("Element", "element")]
                        if has_gauge:
                            options.append(("Shaft Gauge", "gauge"))
                        options.append(("Calibration Element", "calibration"))
                        build_select = Select(options, value=target_now, id="build-select", allow_blank=False)
                        yield build_select
                with Horizontal(classes="picker-row"):
                    yield Static("Resin supports", classes="field-label")
                    resin_now = bool(self.cfg.get("build", {}).get("resin_support"))
                    sw = Switch(value=resin_now, id="build-resin-support")
                    yield sw
                if is_hammond:
                    resin_unavailable = RESIN_SUPPORT_UNAVAILABLE_NOTE.get(self.machine, "")
                    yield Static(
                        'Shuttle: groove-cut shell, no rib. Rib: just the rib+pin-boss '
                        'piece, with a flange (Element tab\'s Rib interface offset) to '
                        'snap into a Shuttle. Shuttle with Rib: the fused one-piece '
                        'default. The two Calibration options mirror the same split. '
                        f"Resin supports not available for Rib.{resin_unavailable}",
                        classes="picker-help")
                else:
                    gauge_help = (
                        " Shaft Gauge: a small calibration print (see the Gauge tab) - "
                        "always includes its own resin supports regardless of this "
                        "checkbox."
                    ) if has_gauge else ""
                    resin_unavailable = RESIN_SUPPORT_UNAVAILABLE_NOTE.get(self.machine, "")
                    yield Static(
                        "Element: the real element. Turn on Resin supports to add "
                        "rods/breakaway ring (see the Resin tab for those settings)."
                        f"{gauge_help} Calibration Element: strikes the same test "
                        "character everywhere, sweeping baseline or cutout per column "
                        "(see the Calibration tab) to find layout.baseline_row/cutout_row."
                        f"{resin_unavailable}",
                        classes="picker-help")

                if is_hammond:
                    orientation_now = str(self.cfg.get("resin", {}).get("orientation", "vertical"))
                    if orientation_now not in ("vertical", "horizontal"):
                        orientation_now = "vertical"
                    with Horizontal(classes="picker-row"):
                        yield Static("Print orientation", classes="field-label")
                        yield Select([("Vertical", "vertical"), ("Horizontal", "horizontal")],
                                     value=orientation_now, id="build-orientation", allow_blank=False)
                    yield Static(
                        '"Vertical" stands the shuttle up on end. "Horizontal" prints it flat, '
                        "as-built. Only matters while Resin supports is on.",
                        classes="field-help")

                    hm_now = str(self.cfg.get("resin", {}).get("horizontal_method", "resin_rod"))
                    if hm_now not in ("cut_groove", "resin_rod"):
                        hm_now = "resin_rod"
                    with Horizontal(classes="picker-row"):
                        yield Static("Horizontal support method", classes="field-label")
                        yield Select([("Cut Groove", "cut_groove"), ("Resin Rod", "resin_rod")],
                                     value=hm_now, id="build-horizontal-method", allow_blank=False)
                    yield Static(
                        'Only used for horizontal orientation. "Cut Groove": a swept perforated '
                        'breakaway-groove ring around the outer wall. "Resin Rod": individual rods '
                        'along the outer wall instead. Independent of Build target above - whenever '
                        'it builds a body with a rib ("Shuttle with Rib"), its own resin-rod supports '
                        "are always added too, regardless of this setting.",
                        classes="field-help")

                if is_hammond_split:
                    with Horizontal(classes="picker-row"):
                        yield Static("Render left half", classes="field-label")
                        yield Switch(value=bool(self.cfg.get("build", {}).get("render_left", True)),
                                     id="build-render-left")
                    with Horizontal(classes="picker-row"):
                        yield Static("Render right half", classes="field-label")
                        yield Switch(value=bool(self.cfg.get("build", {}).get("render_right", True)),
                                     id="build-render-right")
                    yield Static(
                        "Turn either off to build/print just one shuttle half at a time. "
                        "Both halves ship in one STL, laid out side by side (not overlapping) "
                        "when both are on. Minkowski draft itself (like every machine) isn't a "
                        "config toggle - Quick Preview always skips it, Render always applies it; "
                        "its angle/height live on the Font & Alignment tab.",
                        classes="field-help")

                yield Static("Debug", classes="field-label")
                with Horizontal(classes="picker-row"):
                    yield Static("Cross section", classes="field-label")
                    yield Switch(value=False, id="build-xsection-enabled")
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("Angle of plane (deg)", classes="field-label")
                        yield Input(value="0", id="build-xsection-angle")
                    yield Static(
                        "Only applies while Cross section is on. Clips the built "
                        "mesh to one side of a vertical plane through the machine's "
                        "central axis at this angle.",
                        classes="field-help")
                with Horizontal(classes="picker-row"):
                    yield Static("Render only the cut bodies", classes="field-label")
                    yield Switch(value=False, id="build-cut-bodies")
                yield Static(
                    "Exports the negative/cutter tool bodies (HollowSpace, drive "
                    "pin, core grooves, ...) instead of the real element, so you "
                    "can verify what's actually being removed - independent of "
                    "Cross section, and only applies to Element/Resin builds "
                    "(ignored for Shaft Gauge/Calibration Element). Session-only "
                    "debug settings: neither of these is saved to the config.",
                    classes="picker-help")

    def _compose_type_test_tab(self):
        with TabPane("Type Test", id="tab-type-test"):
            with VerticalScroll():
                yield Static(
                    "Flat, fixed-pitch (CPI) test block using the Font tab's "
                    "path/size. Not part of the real element - overwrites the same "
                    "scratch STL as Render/Quick Preview, so the same f3d window "
                    "shows it. Supports multiple lines, stacked vertically.",
                    classes="picker-help")
                yield Static("Test text", classes="field-label")
                yield TextArea(self.cfg["type_test"]["text"], id="type-test-text")
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("CPI", classes="field-label")
                        yield Input(value=str(self.cfg["type_test"]["cpi"]), id="type-test-cpi")
                    yield Static("Characters per inch (v2's Test_CPI).", classes="field-help")
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("LPI", classes="field-label")
                        yield Input(value=str(self.cfg["type_test"]["lpi"]), id="type-test-lpi")
                    yield Static("Lines per inch - vertical spacing for multi-line text.", classes="field-help")

    def compose(self) -> ComposeResult:
        yield Header()
        if self.machine is None:
            yield from self._compose_machine_picker()
        else:
            yield from self._compose_tuner_ui()
        yield Footer()

    def _compose_machine_picker(self):
        """Shown on startup (unless a config was given on the command
        line) and whenever "Change Machine" is pressed - self.machine is
        None in both cases. One button per MACHINES entry; picking one
        loads that machine's config and recomposes into the tuner form
        (see _select_machine)."""
        with Vertical(id="machine-picker"):
            yield Static("Type Elements Tuner", classes="picker-title")
            yield Static("Choose a machine to work on:", classes="picker-subtitle")
            for key, (label, _path) in MACHINES.items():
                yield Button(label, id=f"pick-machine-{key}", classes="machine-picker-btn")

    def _compose_tuner_ui(self):
        with Vertical(id="form"):
            yield Static(self._status_text(), id="status")
            with Horizontal(id="status-row"):
                yield Button("Browse", id="browse-config", classes="browse-btn")
                yield Button("Reset to Defaults", id="btn-reset-defaults", variant="error")
                yield Button("Change Machine", id="btn-change-machine")
            with TabbedContent():
                yield from self._compose_section_tab("Font & Alignment")
                yield from self._compose_type_test_tab()
                yield from self._compose_section_tab("Resin")
                if "Gauge" in self.SECTIONS:
                    yield from self._compose_section_tab("Gauge")
                yield from self._compose_section_tab("Calibration")
                yield from self._compose_build_tab()
                yield from self._compose_layout_tab()
                yield from self._compose_section_tab("Quality")
                # no "Logo" key for Bennett - its one engraved-text feature
                # is the "Label" tab instead (see LABEL_FIELDS_BENNETT).
                if "Logo" in self.SECTIONS:
                    yield from self._compose_section_tab("Logo")
                if "Label" in self.SECTIONS:
                    yield from self._compose_section_tab("Label")
                yield from self._compose_section_tab("Element")
                if "Rib" in self.SECTIONS:
                    yield from self._compose_section_tab("Rib")

            with Vertical(id="buttons"):
                # short, wide, and OUTSIDE the TabbedContent (unlike the
                # old per-tab "Render Text" button it replaces) so it
                # stays visible/clickable no matter which tab is active -
                # in particular while tuning Font & Alignment, without
                # needing to flip to the Type Test tab just to re-render
                yield Button("RENDER TEST TEXT", id="btn-render-test-text", variant="primary")
                with Horizontal(id="primary-buttons"):
                    yield Button("PREVIEW [p]", id="btn-preview", variant="success")
                    yield Button("RENDER [b]", id="btn-render", variant="primary")
                    yield Button("SAVE [s]", id="btn-save", variant="warning")
                with Horizontal(id="f3d-row"):
                    yield Static("f3d preview", classes="field-label")
                    yield Switch(value=True, id="f3d-preview-checkbox")
        with Vertical(id="log-pane"):
            yield ReflowingRichLog(id="log", wrap=True, markup=True, min_width=1)
            with Horizontal(id="progress-row"):
                # show_eta=False - see _stream_subprocess's own comment:
                # Textual's built-in ETA only recomputes on update(), and
                # character placement (0-95%) finishes almost instantly
                # while the actual slow part (resin supports etc., no
                # per-item signal) never calls update() at all - the
                # countdown would freeze at a stale value the moment
                # characters finish, not visibly broken so much as
                # actively misleading. A plain elapsed-time counter
                # (#build-elapsed) needs no speed extrapolation and can't
                # go stale the same way.
                yield ProgressBar(total=100, id="build-progress", show_eta=False)
                yield Static("", id="build-elapsed")

    def log_line(self, text):
        self.query_one("#log", ReflowingRichLog).write(text)

    def _collect_values(self):
        values = {}
        for key, path, typ, label, help_text in self.FIELDS:
            widget = self.inputs[key]
            if typ is bool:
                values[key] = widget.value
            elif typ is str:
                values[key] = widget.value
            else:
                raw = widget.value.strip()
                try:
                    values[key] = typ(raw)
                except ValueError:
                    self.log_line(f"[red]bad value for {key!r}: {raw!r} (expected {typ.__name__})[/red]")
                    return None
        # build target dropdown (element/gauge) + its own independent
        # "Resin supports" checkbox - resin_support only actually matters
        # when target is "element" (GaugeTestSet() always builds its own
        # supports regardless, see _run_build)
        if self.machine == "hammond":
            # Hammond's dropdown value is one of HAMMOND_BUILD_OPTIONS'
            # keys (shuttle/rib/shuttle_with_rib/calibration), not a real
            # build.target value directly - translate via
            # HAMMOND_BUILD_TARGET_GROOVE (see _compose_build_tab).
            dropdown_value = self.query_one("#build-select", Select).value
            values["target"], values["groove"] = HAMMOND_BUILD_TARGET_GROOVE[dropdown_value]
        else:
            values["target"] = self.query_one("#build-select", Select).value
        values["resin_support"] = self.query_one("#build-resin-support", Switch).value
        if self.machine == "hammond":
            # orientation/horizontal_method - moved off the Resin tab onto
            # the Build tab (see _compose_build_tab) - not in self.FIELDS
            # for the same reason as groove above.
            values["orientation"] = self.query_one("#build-orientation", Select).value
            values["horizontal_method"] = self.query_one("#build-horizontal-method", Select).value
        if self.machine == "hammond_split":
            # render_left/render_right - bespoke Build-tab widgets (see
            # _compose_build_tab's is_hammond_split branch), same treatment
            # as Hammond's orientation/horizontal_method above. Minkowski
            # draft angle/height are plain self.FIELDS entries (Font &
            # Alignment tab) instead - not bespoke, since (like every
            # machine's draft_angle_deg) they're real tunable parameters,
            # unlike whether the draft runs at all (never a config toggle -
            # forced by which button was pressed, see _run_build).
            values["render_left"] = self.query_one("#build-render-left", Switch).value
            values["render_right"] = self.query_one("#build-render-right", Switch).value
        # Type Test's own cpi/lpi - bespoke widgets, not in self.FIELDS, but
        # persisted the same as everything else (text is handled
        # separately in _save_to_yaml - it's a multi-line block scalar,
        # patch_yaml_value's one-token regex doesn't apply)
        cpi_raw = self.query_one("#type-test-cpi", Input).value.strip()
        lpi_raw = self.query_one("#type-test-lpi", Input).value.strip()
        try:
            values["cpi"] = float(cpi_raw)
            values["lpi"] = float(lpi_raw)
        except ValueError:
            self.log_line(f"[red]bad Type Test CPI/LPI value: {cpi_raw!r}/{lpi_raw!r} (expected numbers)[/red]")
            return None
        # layout.baseline_row/cutout_row per-row fields (Element tab) -
        # bespoke like everything above, since they're list elements, not
        # standalone scalar YAML keys - see BASELINE_CUTOUT_KEYS/
        # patch_yaml_list_item.
        for key in self.BASELINE_CUTOUT_KEYS:
            raw = self.inputs[key].value.strip()
            try:
                values[key] = float(raw)
            except ValueError:
                self.log_line(f"[red]bad value for {key!r}: {raw!r} (expected a number)[/red]")
                return None
        return values

    def _save_to_yaml(self, values):
        with open(self.config_path) as f:
            text = f.read()
        for key, value in values.items():
            if key in self.BASELINE_CUTOUT_KEYS:
                continue
            text = patch_yaml_value(text, key, value)
        for key in self.BASELINE_CUTOUT_KEYS:
            arr_key, index_str = key.rsplit("_", 1)
            text = patch_yaml_list_item(text, arr_key, int(index_str), values[key])
        modify_glyphs = self.query_one("#layout-modify-glyphs", Switch).value
        text = patch_yaml_value(text, "modify_glyphs", modify_glyphs)
        if modify_glyphs:
            # the hand-edited copy is authoritative over the preset
            # dropdown while unlocked - "fix" (defensively re-clamp) each
            # row to the placement_map cap in case anything bypassed the
            # Input's own max_length (e.g. a paste)
            char_cap = len(self.cfg["layout"]["placement_map"])
            n_rows = len(self.cfg["layout"]["rows"])
            custom_rows = [self.query_one(f"#layout-custom-row-{i}", Input).value[:char_cap] for i in range(n_rows)]
            text = patch_yaml_rows(text, custom_rows)
        else:
            layout_select = self.query_one("#layout-select", Select)
            if layout_select.value is not Select.NULL:
                text = patch_yaml_rows(text, self.LAYOUT_PRESETS[layout_select.value])
                # baseline_row/cutout_row themselves are NOT force-
                # overwritten here from LAYOUT_PRESET_BASELINE_ROW_BY_
                # MACHINE on every save - an earlier version of this did
                # that unconditionally, which silently discarded any
                # manual edit to those fields every time a save happened
                # while a preset remained selected (i.e. essentially
                # always, since "custom" requires Modify glyphs). The
                # BASELINE_CUTOUT_KEYS loop above already saves whatever
                # is actually showing in the (now always-4-rows-wide,
                # see _compose_baseline_cutout_fields) widgets, appending
                # a 4th entry via patch_yaml_list_item if needed - that's
                # the real, editable, save-preserving value. The preset's
                # own real defaults are instead pre-filled into those
                # SAME widgets live, the moment the dropdown selection
                # changes (see on_select_changed) - a one-time seed the
                # user can still hand-edit before saving, not a
                # recurring overwrite.
        type_test_text = self.query_one("#type-test-text", TextArea).text
        text = patch_yaml_text_block(text, "text", type_test_text)
        with open(self.config_path, "w") as f:
            f.write(text)
        self._load_current()

    def action_render(self):
        self.run_worker(self._run_build(fast=False), exclusive=True)

    def action_preview(self):
        self.run_worker(self._run_build(fast=True), exclusive=True)

    def _refresh_widgets_from_cfg(self):
        """(Re)populate every widget from self.cfg. Shared by Reload
        (re-read the running config), Reset to Defaults (overwrite
        running with master, then re-read), and switching to a
        different master config entirely - all three are "throw away
        whatever's in the widgets and repopulate from whatever
        self.cfg now is"."""
        for key, path, typ, label, help_text in self.FIELDS:
            current = get_nested(self.cfg, path)
            widget = self.inputs[key]
            if typ is bool:
                widget.value = bool(current)
            else:
                widget.value = str(current)
        preset_now = self._current_layout_preset()
        self.query_one("#layout-select", Select).value = preset_now if preset_now else Select.NULL
        target_now = self.cfg.get("build", {}).get("target", "element")
        if self.machine == "hammond":
            # Hammond's dropdown shows a consolidated Shuttle/Rib/Shuttle
            # with Rib/Calibration Shuttle value, not a raw build.target -
            # see HAMMOND_BUILD_OPTIONS/_hammond_build_dropdown_value.
            groove_now = bool(self.cfg.get("element", {}).get("groove"))
            self.query_one("#build-select", Select).value = (
                _hammond_build_dropdown_value(target_now, groove_now))
        else:
            valid_targets = ("element", "calibration") + (("gauge",) if "Gauge" in self.SECTIONS else ())
            if target_now not in valid_targets:
                # "resin" was a valid target value before the Build tab's
                # dropdown was split into target + a separate Resin supports
                # checkbox - a running copy saved before that change could
                # still have it on disk; map it back to plain "element" (the
                # checkbox itself carries whether resin support is on now).
                # Also catches "gauge" for a machine with no Gauge tab.
                target_now = "element"
            self.query_one("#build-select", Select).value = target_now
        self.query_one("#build-resin-support", Switch).value = bool(self.cfg["build"]["resin_support"])
        if self.machine == "hammond":
            orientation_now = str(self.cfg.get("resin", {}).get("orientation", "vertical"))
            self.query_one("#build-orientation", Select).value = (
                orientation_now if orientation_now in ("vertical", "horizontal") else "vertical")
            hm_now = str(self.cfg.get("resin", {}).get("horizontal_method", "resin_rod"))
            self.query_one("#build-horizontal-method", Select).value = (
                hm_now if hm_now in ("cut_groove", "resin_rod") else "resin_rod")
        if self.machine == "hammond_split":
            b = self.cfg.get("build", {})
            self.query_one("#build-render-left", Switch).value = bool(b.get("render_left", True))
            self.query_one("#build-render-right", Switch).value = bool(b.get("render_right", True))
        self.query_one("#type-test-cpi", Input).value = str(self.cfg["type_test"]["cpi"])
        self.query_one("#type-test-lpi", Input).value = str(self.cfg["type_test"]["lpi"])
        self.query_one("#type-test-text", TextArea).text = self.cfg["type_test"]["text"]
        display_rows = self._display_rows_for_preset()
        for i in range(len(display_rows)):
            self._update_row_widget("layout-original-row", i, display_rows[i])
        modify_glyphs = bool(self.cfg["layout"]["modify_glyphs"])
        self.query_one("#layout-modify-glyphs", Switch).value = modify_glyphs
        self.query_one("#layout-custom-rows").display = modify_glyphs
        current_rows = self.cfg["layout"]["rows"]
        for i in range(len(current_rows)):
            self._update_row_widget("layout-custom-row", i, current_rows[i])
        for arr_key in ("baseline_row", "cutout_row"):
            arr = self.cfg["layout"][arr_key]
            for i in range(len(arr)):
                # self.inputs (a plain dict, not query_one) - same row-
                # count-mismatch reasoning as _update_row_widget above,
                # but a dict lookup raises KeyError, not NoMatches.
                w = self.inputs.get(f"{arr_key}_{i}")
                if w is not None:
                    w.value = str(arr[i])

    def action_reload(self):
        self._load_current()
        self._refresh_widgets_from_cfg()
        self.log_line("[cyan]reloaded values from disk[/cyan]")

    def action_reset_defaults(self):
        shutil.copy2(self.master_config_path, self.config_path)
        self._load_current()
        self._refresh_widgets_from_cfg()
        self.log_line("[yellow]reset to master defaults - all customizations to the running "
                       "copy discarded (master itself was never touched)[/yellow]")

    async def _browse_config(self):
        start_dir = os.path.dirname(self.master_config_path)
        result = await self.push_screen_wait(
            FileOpen(start_dir, title="Choose config YAML", filters=YAML_FILE_FILTERS))
        if result is None:
            return
        self._switch_master_config(str(result))

    def _switch_master_config(self, new_master_path):
        new_master_path = os.path.abspath(new_master_path)
        # self.SECTIONS/self.FIELDS/self.LAYOUT_PRESETS (and every widget
        # compose() already built for the CURRENT machine) depend on
        # self.machine - a config for a DIFFERENT machine (e.g. switching
        # from Blickensderfer to Postal via Browse) has a different
        # Element field set entirely (get_nested() would KeyError against
        # fields Postal's config doesn't have) and needs a full recompose
        # (see _select_machine), not just repopulating these widgets.
        # Refuse the switch instead of crashing - use Change Machine
        # instead, which does the recompose properly.
        with open(new_master_path) as f:
            new_machine = (yaml.safe_load(f) or {}).get("machine", "blickensderfer")
        if new_machine != self.machine:
            self.log_line(
                f"[red]can't switch to a {new_machine!r} config while tuning {self.machine!r} - "
                f"use the \"Change Machine\" button instead[/red]")
            return
        self.master_config_path = new_master_path
        self.config_path = self._running_config_path(self.master_config_path)
        self._ensure_running_config()
        migrated = self._migrate_running_config()
        self._load_current()
        self._refresh_widgets_from_cfg()
        self.query_one("#status", Static).update(self._status_text())
        self.log_line(f"[cyan]switched to {os.path.relpath(self.master_config_path, REPO_ROOT)}[/cyan]")
        if migrated:
            self.log_line(f"[cyan]backfilled missing section(s) from master: {', '.join(migrated)}[/cyan]")

    async def _select_machine(self, machine_key):
        """Machine-picker button handler - loads the picked machine's
        default config and recomposes into the tuner form. Fresh
        self.inputs/self.SECTIONS/etc from _load_machine means the
        recompose below builds a form correctly shaped for the NEW
        machine, not a stale one repopulated with wrong fields."""
        _, config_path = MACHINES[machine_key]
        self._load_machine(config_path)
        await self.recompose()
        self.log_line(f"[cyan]tuning {self.machine}[/cyan]")

    async def _change_machine(self):
        """"Change Machine" button - saves the current form first (same
        courtesy as quitting - see _save_before_exit), then goes back to
        the machine picker. self.machine=None + recompose() is exactly
        what shows the picker (see compose()).

        Also closes any f3d window left open from the machine being left
        behind - otherwise it keeps --watch-ing that machine's own STL
        path (e.g. output/hammond_running.stl) forever, since a
        Render/Preview on whichever machine gets picked next writes to a
        DIFFERENT path (output/blickensderfer_running.stl, etc.) that
        f3d was never told about. Without this, _ensure_f3d_after_build's
        own "already running, just raise the window" branch would keep
        reusing that stale watch, so the old machine's model just sits
        there unrefreshed while the new one silently never appears -
        reported as "hammond_running i just refreshed [instead of
        blickensderfer showing]". Killing it here means the next
        Preview/Render always launches a fresh f3d pointed at the
        newly-picked machine's own real output path."""
        self._kill_f3d()
        self._save_before_exit()
        self.machine = None
        await self.recompose()

    async def _ensure_f3d_after_build(self, out_path, camera_flags=()):
        """Called after a successful Preview/Render/Render Text. If f3d
        isn't running (or the process we launched has since exited) OR
        it's currently watching a DIFFERENT path than out_path, launch it
        fresh - it'll show the just-written STL immediately. camera_flags
        (only meaningful on a fresh launch - f3d has no way to change an
        already-running instance's camera from the CLI) let the caller
        pick a starting view, e.g. top-down for flat text.

        The out_path check (self._f3d_out_path) matters beyond just
        "switched machines" (already handled by _kill_f3d in that flow) -
        f3d loads whatever "current file" is AT LAUNCH and then watches it
        for further changes; if out_path didn't exist yet the moment some
        earlier f3d instance launched against it (e.g. the very first
        Preview for a brand new machine/output path, before this session
        ever wrote it, or the user having started f3d by hand pointed at
        a not-yet-built path), that instance shows an empty scene and its
        filesystem watch has no existing inode to attach to - it never
        recovers on its own even once the file is later created, reported
        as f3d's window persistently showing "[EMPTY]" no matter how many
        successful builds follow. Tracking out_path here and forcing a
        fresh relaunch whenever it changes (which includes "first
        successful build for this path this session," when self._f3d_
        out_path is still None) guarantees f3d only ever gets pointed at
        out_path AFTER a build has already confirmed it exists on disk,
        never in a state where it could have started empty.

        If f3d is already running and watching the SAME out_path, its own
        --watch reloads the model automatically (keeping whatever camera
        the user's since set); we just try to raise the window, after a
        short pause so the reload has actually happened first (raising it
        to show the STALE model would defeat the point)."""
        if not self.query_one("#f3d-preview-checkbox", Switch).value:
            return
        if self._f3d_proc is None or self._f3d_proc.poll() is not None or self._f3d_out_path != out_path:
            self._kill_f3d()
            try:
                self._f3d_proc = subprocess.Popen(
                    ["f3d", "--watch", out_path, "-g", "-x", *camera_flags],
                    cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._f3d_out_path = out_path
                self.log_line(f"[cyan]launched f3d --watch on {out_path}[/cyan]")
            except FileNotFoundError:
                self.log_line("[red]f3d not found on PATH[/red]")
            return
        await asyncio.sleep(0.3)  # let f3d's own file watcher reload first
        if shutil.which("wmctrl"):
            subprocess.run(["wmctrl", "-a", "f3d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif not self._warned_no_wmctrl:
            self._warned_no_wmctrl = True
            self.log_line("[yellow]f3d already open with the updated model, but can't bring it "
                           "to front - install wmctrl (sudo apt install wmctrl) to enable that[/yellow]")

    async def _run_build(self, fast):
        values = self._collect_values()
        if values is None:
            return
        self._save_to_yaml(values)
        label = "Quick Preview" if fast else "Render"
        self.log_line(f"[bold]--- {label} ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "generate.py"), self.config_path]
        # Debug section's controls - session-only (never saved to the
        # config, see _compose_build_tab), so read straight from the
        # widgets here rather than through values/_collect_values. Both
        # are independent of each other and of the build target below -
        # --cut-bodies is simply ignored by generate.py for the gauge/
        # calibrate branches (see its own docstring).
        if self.query_one("#build-xsection-enabled", Switch).value:
            angle_raw = self.query_one("#build-xsection-angle", Input).value.strip()
            try:
                angle = float(angle_raw)
            except ValueError:
                self.log_line(f"[red]bad cross-section angle: {angle_raw!r} (expected a number)[/red]")
                return
            cmd += ["--cross-section-angle-deg", str(angle)]
        if self.query_one("#build-cut-bodies", Switch).value:
            cmd += ["--cut-bodies"]
        if values["target"] == "none":
            # Hammond only: no main shuttle/calibration body, just
            # hammond.RibOnly() - a plain FDM part export, no resin
            # supports either way (generate.py's --hammond-part branch
            # runs before the resin dispatch, so build-resin-support's
            # checkbox value is simply never consulted). RibOnly() skips
            # TextRing/build_glyph entirely (no characters at all), same
            # reasoning as --gauge below, so Minkowski doesn't apply here.
            cmd += ["--hammond-part", "rib_only"]
        elif values["target"] == "gauge":
            # GaugeTestSet() doesn't touch TextRing/build_glyph at all, so
            # the Minkowski/points-per-mm knobs don't apply here.
            cmd += ["--gauge"]
        elif values["target"] == "calibration":
            # CalibrationElement() DOES go through build_glyph/TextRing
            # (same real draft/placement machinery, just a different
            # character grid) - Minkowski forced the same way as a normal
            # element build, below. --calibration-reference-config points
            # at the MASTER (not self.config_path, the running copy) so
            # the sweep always anchors on a fixed value - editing/saving
            # a baseline_row/cutout_row value found from a PREVIOUS
            # calibration pass (Element tab) must not move the target for
            # the next one, or you'd be chasing a moving reference.
            cmd += ["--calibrate", "--calibration-reference-config", self.master_config_path]
            if fast:
                # --no-minkowski-text: no-op for non-Mignon machines (see
                # generate.py) - Mignon's CalibrationElement() also renders
                # Logo/Label text, same reasoning as the normal element
                # branch below. --no-core-groove is deliberately NOT forced
                # here - Quick Preview follows build.render_core_groove same
                # as a real Render (see 48e501c).
                cmd += ["--no-minkowski", "--no-minkowski-text"]
            else:
                cmd += ["--minkowski"]
        else:
            # Minkowski draft sweep is not a config field the user tunes -
            # it's entirely determined by which button was pressed, forced
            # explicitly either way so the config's build.minkowski_enabled
            # default is never consulted here. Resin supports is NOT
            # forced here though - both buttons defer to whatever
            # build.resin_support was just saved from the Build tab's own
            # checkbox, so Quick Preview still shows resin supports when
            # that's checked.
            #
            # logo.minkowski_text (Mignon only) is different: unlike
            # minkowski_enabled, Render does NOT force it on - it only
            # ever applies if BOTH the checkbox is on AND this is a real
            # Render, never during Quick Preview, regardless of the
            # checkbox. So Preview forces it off explicitly; Render passes
            # nothing, deferring to whatever was just saved from the
            # checkbox (which --save-to-yaml already wrote before this
            # subprocess launches).
            if fast:
                cmd += ["--no-minkowski", "--no-minkowski-text"]
            else:
                cmd += ["--minkowski"]
        returncode = await self._stream_subprocess(cmd)
        if returncode == 0:
            self._last_build_info = {
                "kind": "preview" if fast else "render",
                "target": values["target"],
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
            await self._ensure_f3d_after_build(out_path)

    async def action_render_type_test(self):
        # save the whole form first, same as Preview/Render - this is
        # the only place Type Test's own text/cpi/lpi actually get
        # persisted to disk, so they survive a TUI restart
        values = self._collect_values()
        if values is None:
            return
        self._save_to_yaml(values)

        text = self.query_one("#type-test-text", TextArea).text
        cpi_raw = self.query_one("#type-test-cpi", Input).value.strip()
        try:
            cpi = float(cpi_raw)
        except ValueError:
            self.log_line(f"[red]bad CPI value: {cpi_raw!r}[/red]")
            return
        lpi_raw = self.query_one("#type-test-lpi", Input).value.strip()
        try:
            lpi = float(lpi_raw)
        except ValueError:
            self.log_line(f"[red]bad LPI value: {lpi_raw!r}[/red]")
            return
        if not text.strip():
            self.log_line("[red]test text is empty[/red]")
            return
        font_path = self.inputs["path"].value
        font_size_mm = self.inputs["size_mm"].value
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
        self.log_line(f"[bold]--- Type Test (overwrites {out_path}) ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "type_test.py"), text,
               "--cpi", str(cpi), "--lpi", str(lpi), "--font-path", font_path, "--font-size-mm", font_size_mm,
               # same horizontal-alignment convention as the real element
               # (advance-box center/left + modified_left/right nudges) -
               # read live off the Font & Alignment tab's own widgets
               "--align-mode", self.inputs["mode"].value,
               "--center-offset-mm", self.inputs["center_offset_mm"].value,
               "--left-offset-mm", self.inputs["left_offset_mm"].value,
               # "=" form, not space-separated, in case the chars field
               # starts with "-" (would otherwise look like another flag)
               "--modified-left-chars=" + self.inputs["modified_left_chars"].value,
               "--modified-left-offset-mm", self.inputs["modified_left_offset_mm"].value,
               "--modified-right-chars=" + self.inputs["modified_right_chars"].value,
               "--modified-right-offset-mm", self.inputs["modified_right_offset_mm"].value,
               "--out", out_path]
        returncode = await self._stream_subprocess(cmd)
        if returncode == 0:
            self._last_build_info = {
                "kind": "type_test",
                "text": text,
                "cpi": cpi,
                "lpi": lpi,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            # camera view 7 (Top View), orthographic - matches the flat
            # text's natural viewing angle with no perspective distortion.
            # Uses f3d's own `set_camera top` console command (the exact
            # thing the "7" key runs - see F3D_TOP_VIEW_SCRIPT) rather
            # than hand-derived --camera-direction/--camera-view-up
            # vectors: an earlier attempt at the latter LOOKED like a
            # correct top-down view offscreen but was actually rotated
            # 90 degrees from what pressing 7 interactively gives. Only
            # applies on a fresh f3d launch, see _ensure_f3d_after_build.
            await self._ensure_f3d_after_build(
                out_path, camera_flags=[f"--command-script={F3D_TOP_VIEW_SCRIPT}", "--camera-orthographic"])

    async def action_save(self):
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
        if not os.path.exists(out_path):
            self.log_line("[yellow]nothing to save yet - Preview or Render first[/yellow]")
            return
        save_dir = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], "saved")
        os.makedirs(save_dir, exist_ok=True)
        # suggest a collision-free timestamped name, same as before, but
        # it's now just the file picker's starting point - the picker
        # lets you navigate elsewhere or rename before confirming
        base = f"{self.machine}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        suggested = f"{base}.stl"
        n = 2
        while os.path.exists(os.path.join(save_dir, suggested)):
            suggested = f"{base}_{n}.stl"
            n += 1
        result = await self.push_screen_wait(
            FileSave(save_dir, title="Save STL as", default_file=suggested, filters=STL_FILE_FILTERS))
        if result is None:
            self.log_line("[yellow]save cancelled[/yellow]")
            return
        stl_path = str(result)
        if not stl_path.lower().endswith(".stl"):
            stl_path += ".stl"
        meta_path = stl_path[:-4] + ".yaml"
        os.makedirs(os.path.dirname(stl_path), exist_ok=True)
        shutil.copy2(out_path, stl_path)
        # YAML, not JSON, and self.cfg dumped directly at the TOP LEVEL
        # (not nested under a "config" key) - the whole point is this
        # file is itself a valid, loadable config: Browse to it (the
        # config Browse button above, or font-picker filters - it's
        # filtered to .yaml/.yml) and it just works as a new master.
        # The save context goes in a comment header instead, since a
        # real key would pollute the config namespace and comments are
        # invisible to yaml.safe_load anyway.
        header = (
            f"# Saved by tune.py's Save button at {datetime.now().isoformat(timespec='seconds')}\n"
            f"# master_config: {os.path.relpath(self.master_config_path, REPO_ROOT)}\n"
            f"# running_config: {os.path.relpath(self.config_path, REPO_ROOT)}\n"
            f"# last_build: {self._last_build_info}\n"
            "# This is a full config snapshot, not just metadata - Browse to\n"
            "# it directly to use it as a master config.\n"
        )
        with open(meta_path, "w") as f:
            f.write(header)
            yaml.dump(self.cfg, f, sort_keys=False, allow_unicode=True)
        extra = [os.path.basename(meta_path)]
        # Calibration builds also write a keyboard-key/position -> tested-
        # value .txt sidecar next to the scratch STL (see generate.py's
        # --calibrate) - copy it alongside the saved STL too, same as the
        # .yaml metadata, rather than regenerating it (it's already
        # exactly what the last build produced).
        mapping_src = os.path.splitext(out_path)[0] + "_mapping.txt"
        if self._last_build_info and self._last_build_info.get("target") == "calibration" \
                and os.path.exists(mapping_src):
            mapping_dst = stl_path[:-4] + "_mapping.txt"
            shutil.copy2(mapping_src, mapping_dst)
            extra.append(os.path.basename(mapping_dst))
        self.log_line(f"[green]saved[/green] {stl_path} (+ {', '.join(extra)})")

    async def _browse_font(self, key):
        current = self.inputs[key].value
        start_dir = os.path.dirname(current) if current and os.path.isdir(os.path.dirname(current)) \
            else os.path.expanduser("~")
        result = await self.push_screen_wait(
            FileOpen(start_dir, title="Choose font", filters=FONT_FILE_FILTERS))
        if result is not None:
            self.inputs[key].value = str(result)

    # Matches generate.py's own "[n/total]" progress markers - both
    # cylinder_machine.TextRing ("TextRing: [45/90] building ...") and
    # CalibrationTextRing ("[45/2700] row 1 col 14 (...)") print this same
    # shape, so one regex covers every machine/build-target that goes
    # through either (i.e. every real Element/Calibration Element build -
    # see _update_progress's own docstring for what's NOT covered).
    _PROGRESS_RE = re.compile(r"\[(\d+)/(\d+)\]")

    def _update_progress(self, line):
        """Character placement (TextRing/CalibrationTextRing) is mapped to
        0-95% of the bar - it's the real, fine-grained, per-item work unit
        generate.py already reports; everything after it (Additive/
        Subtractive booleans, resin supports, check_and_repair, the STL
        write) has no comparable per-item signal to report progress
        against, so it's just "the last 5%, then done" - _stream_subprocess
        jumps to 100% on a successful exit. Builds with no TextRing/
        CalibrationTextRing call at all (Shaft Gauge, Hammond's None/
        RibOnly target) never print a "[n/total]" line, so the bar just
        sits at 0% until the same jump to 100% on completion - no
        per-item signal exists to show for those, not a bug."""
        m = self._PROGRESS_RE.search(line)
        if not m:
            return
        n, total = int(m.group(1)), int(m.group(2))
        if total <= 0:
            return
        self.query_one("#build-progress", ProgressBar).update(progress=min(95.0, 95.0 * n / total))

    async def _stream_subprocess(self, cmd):
        t0 = time.time()
        self.query_one("#build-progress", ProgressBar).update(progress=0)
        elapsed = self.query_one("#build-elapsed", Static)
        elapsed.update("0.0s")
        # Plain wall-clock counter, ticking independently of any progress
        # signal - see the "show_eta=False" comment at this widget's
        # compose() call site for why a speed-extrapolated ETA can't work
        # here (it'd freeze stale for most of the build, not just look
        # imprecise) - always accurate since it doesn't extrapolate
        # anything, just counts real elapsed time.
        timer = self.set_interval(0.2, lambda: elapsed.update(f"{time.time() - t0:.1f}s"))
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=REPO_ROOT,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            async for line in proc.stdout:
                text = line.decode(errors="replace").rstrip()
                self.log_line(text)
                self._update_progress(text)
            await proc.wait()
        finally:
            timer.stop()
        dt = time.time() - t0
        elapsed.update(f"{dt:.1f}s")
        if proc.returncode == 0:
            self.query_one("#build-progress", ProgressBar).update(progress=100)
            self.log_line(f"[green]done in {dt:.1f}s[/green] - f3d (if running with --watch) should refresh")
        else:
            self.log_line(f"[red]exited {proc.returncode} after {dt:.1f}s[/red]")
        return proc.returncode

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "layout-select":
            return
        # keep the read-only "original" preview in sync with whichever
        # preset is now selected - deliberately does NOT touch the
        # editable custom rows (would silently blow away in-progress
        # hand edits), even while Modify glyphs is on. Uses event.value
        # (the dropdown's own live value), NOT _display_rows_for_preset()
        # (which re-derives "current preset" from self.cfg on disk) -
        # self.cfg only updates on an actual save, so that would have
        # kept showing the OLD preset while just browsing the dropdown.
        display_rows = self._rows_for_layout_select_value(event.value)
        for i in range(len(display_rows)):
            self._update_row_widget("layout-original-row", i, display_rows[i])
        # Live-seed baseline_row/cutout_row's own editable widgets from
        # the newly-selected preset's real defaults (Hammond's Math
        # Universal needs a real 4th value, -9.89, that a freshly-
        # switched-to preset wouldn't otherwise show) - a one-time seed
        # on the dropdown changing, same convention as on_switch_changed's
        # "freshly unlocked" seeding below, NOT a recurring overwrite
        # (unlike an earlier version of this that re-applied on every
        # save regardless of whether the preset had actually changed,
        # silently discarding hand edits - see _save_to_yaml's comment).
        preset_baseline = LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE.get(self.machine, {}).get(event.value)
        if preset_baseline is not None:
            for i, val in enumerate(preset_baseline):
                for arr_key in ("baseline_row", "cutout_row"):
                    key = f"{arr_key}_{i}"
                    if key in self.inputs:
                        self.inputs[key].value = str(val)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id != "layout-modify-glyphs":
            return
        container = self.query_one("#layout-custom-rows")
        container.display = event.value
        if event.value:
            # freshly unlocked - seed the editable copy from the current
            # read-only preview (whatever preset's selected in the
            # dropdown right now, or the existing custom rows if
            # "custom"), so it starts as an exact copy to hand-edit from
            layout_select_value = self.query_one("#layout-select", Select).value
            display_rows = self._rows_for_layout_select_value(layout_select_value)
            for i in range(len(display_rows)):
                self._update_row_widget("layout-custom-row", i, display_rows[i])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("pick-machine-"):
            self.run_worker(self._select_machine(button_id.removeprefix("pick-machine-")), exclusive=True)
        elif button_id == "btn-change-machine":
            self.run_worker(self._change_machine(), exclusive=True)
        elif button_id == "btn-render":
            self.action_render()
        elif button_id == "btn-preview":
            self.action_preview()
        elif button_id == "btn-save":
            self.run_worker(self.action_save(), exclusive=True)
        elif button_id == "btn-render-test-text":
            self.run_worker(self.action_render_type_test(), exclusive=True)
        elif button_id == "btn-reset-defaults":
            self.action_reset_defaults()
        elif button_id == "browse-config":
            # checked before the generic "browse-" prefix below - this
            # one isn't a font field, it switches the whole app's config
            self.run_worker(self._browse_config())
        elif button_id.startswith("browse-"):
            # not exclusive - browsing for a font shouldn't cancel (or be
            # blocked by) an in-progress build worker
            self.run_worker(self._browse_font(button_id.removeprefix("browse-")))


if __name__ == "__main__":
    # No args: starts at the machine picker (see MACHINES/
    # _compose_machine_picker). A config path skips the picker and loads
    # straight into that config's machine - the old direct-launch usage,
    # kept for power users; the picker's "Change Machine" button is still
    # available afterward either way.
    TuneApp(sys.argv[1] if len(sys.argv) > 1 else None).run()
