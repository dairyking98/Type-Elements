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
from textual.widgets import (Button, Footer, Header, Input, Select, Static, Switch,
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
# font.path (Font & Alignment tab) and logo.font_path (Logo tab) are the
# only two font-picking fields - both get a "Browse" button, see
# _compose_section_tab and on_button_pressed's "browse-" id handling
FONT_PATH_FIELD_KEYS = ("path", "font_path")

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
    "Logo": [
        ("font_path", ["logo", "font_path"], str, "Logo font path", "Font for the engraved LogoText."),
        ("text", ["logo", "text"], str, "Logo text", "The engraved text itself."),
        ("text_size_mm", ["logo", "text_size_mm"], float, "Logo text size (mm)", ""),
        ("text_spacing", ["logo", "text_spacing"], float, "Logo char spacing (deg)", "Angular spacing between logo characters."),
        ("position_offset_deg", ["logo", "position_offset_deg"], float, "Logo position offset (deg)", ""),
        ("text_offset_deg", ["logo", "text_offset_deg"], float, "Logo text offset (deg)", ""),
        ("radial_offset_mm", ["logo", "radial_offset_mm"], float, "Logo radius offset (mm)", "Placement radius = Logo_Radius + this."),
    ],
    "Quality": [
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
    ],
    "Resin": [
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
    ],
    "Gauge": [
        # keys must be the literal YAML key names (patch_yaml_value matches
        # by bare key, not the full path) - confirmed no collision with any
        # other field in the file
        ("offset_start", ["gauge", "offset_start"], float, "Offset start (mm)",
         "First pocket's core_id_offset value - usually 0."),
        ("offset_int", ["gauge", "offset_int"], float, "Offset increment (mm)",
         "Added per pocket - pocket n tests offset_start + n*offset_int."),
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

SECTIONS_BY_MACHINE = {
    "blickensderfer": {**SECTIONS_COMMON, "Element": ELEMENT_FIELDS_BLICKENSDERFER},
    "postal": {**SECTIONS_COMMON, "Element": ELEMENT_FIELDS_POSTAL},
}

# Static intro banner shown above a section tab's fields, keyed by section
# name - (text, css class). Only sections that need one appear here.
SECTION_INTROS = {
    "Element": ("ADVANCED - real machine dimensions.\nGenerally shouldn't need to change these.",
                "advanced-warning"),
    "Gauge": (
        "Shaft Gauge Test (v2's GaugeTestSet()) - a small 6-pocket\n"
        "calibration test print, NOT part of the real element. Each pocket\n"
        "bores the shaft passage at offset_start + n*offset_int (n=0..5),\n"
        "engraved with its own value. Print it, test-fit each numbered\n"
        "pocket on the real machine's shaft, and set Element > Core ID\n"
        "offset to whichever number fits. Select \"Shaft Gauge\" on the\n"
        "Build tab, then Preview/Render as usual to build this instead.",
        "picker-help"),
    "Calibration": (
        "A real element, but every physical position strikes the SAME\n"
        "test character, and Vary baselines/Vary cutouts (usually only\n"
        "one checked at a time) get a different swept value per column\n"
        "instead of its row's normal value. The sweep is centered on the\n"
        "MASTER config's baseline/cutout row, not this running copy's -\n"
        "so it stays a fixed target even after you've already dialed in\n"
        "a value here. Print it, test-fit each position on the real\n"
        "machine, and read off which column's value looks/fits best from\n"
        "the Render log (or the .txt file Save writes alongside the STL)\n"
        "- then enter it in that row's baseline/cutout field on the\n"
        "Element tab. Select \"Calibration Element\" on the Build tab,\n"
        "then Preview/Render as usual to build this instead.",
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

LAYOUT_PRESETS_BY_MACHINE = {
    "blickensderfer": LAYOUT_PRESETS,
    "postal": LAYOUT_PRESETS_POSTAL,
}

# layout.baseline_row/cutout_row per-row fields (Element tab - see
# TuneApp._compose_baseline_cutout_fields). Bespoke, not in
# self.FIELDS/SECTIONS - these are list ELEMENTS (patch_yaml_list_item),
# not standalone scalar YAML keys patch_yaml_value can patch.
BASELINE_CUTOUT_KEYS = [f"{arr}_{i}" for arr in ("baseline_row", "cutout_row") for i in range(3)]


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
    item is ever exposed the same way."""
    pattern = re.compile(rf'^(\s*{re.escape(key)}:\s*\[)([^\]]*)(\])', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        raise ValueError(f"key {key!r} not found in config text - was it renamed/removed?")
    items = [x.strip() for x in m.group(2).split(",")]
    if index >= len(items):
        raise ValueError(f"{key!r} has only {len(items)} items, index {index} out of range")
    val_str = f"{value:.6f}".rstrip("0").rstrip(".")
    if "." not in val_str and "e" not in val_str.lower():
        val_str += ".0"
    items[index] = val_str
    return text[:m.start()] + m.group(1) + ", ".join(items) + m.group(3) + text[m.end():]


def patch_yaml_rows(text, rows):
    """layout.rows is a 3-item YAML block list, not a single-line scalar -
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


class TuneApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #form { width: 58; height: 100%; border: solid $accent; }
    #log-pane { width: 1fr; height: 100%; border: solid $accent; padding: 0 1; }
    #log { height: 1fr; }
    TabbedContent { height: 1fr; }
    TabPane { padding: 0 1; }
    .field-row { height: 2; }
    .field-row Horizontal { height: 1; }
    .field-label { width: 26; height: 1; content-align: left middle; }
    .field-row Input { width: 1fr; height: 1; border: none; padding: 0 1; background: $panel; }
    .field-row Switch { width: auto; height: 1; border: none; padding: 0; }
    .field-row Select { width: 1fr; height: 1; border: none; }
    .field-row Select > SelectCurrent { border: none; padding: 0 1; background: $panel; }
    .browse-btn { width: 10; height: 1; min-width: 10; border: none; margin-left: 1; }
    .field-help { color: $text-muted; height: 1; }
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
    .advanced-warning { color: $warning; text-style: bold; height: 2; padding: 0 0 1 0; }
    .picker-row { height: 3; }
    .picker-help { color: $text-muted; height: 1; }
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
    ROW_LABELS = ["lowercase", "uppercase", "figs"]

    def _compose_baseline_cutout_fields(self):
        yield Static(
            "Per-row baseline/platen-cutout (mm below the clip end) - see\n"
            "the Calibration tab for empirically finding these.",
            classes="picker-help")
        for arr_key, label in (("baseline_row", "Baseline"), ("cutout_row", "Cutout")):
            values = self.cfg["layout"][arr_key]
            for i, row_label in enumerate(self.ROW_LABELS):
                key = f"{arr_key}_{i}"
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static(f"{label} row {i} ({row_label})", classes="field-label")
                        inp = Input(value=str(values[i]), id=f"field-{key}")
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
                if self.machine == "blickensderfer":
                    yield Static(
                        "Ported from v2/lib/layouts/blick_layouts.scad. All share the same\n"
                        "physical placement_map - only glyph content per row changes.\n"
                        "HEBREW_ENGL needs a Hebrew-capable font.path to render correctly\n"
                        "(v2 auto-switches fonts per layout; v4 does not).",
                        classes="picker-help")
                elif options:
                    yield Static(
                        "Postal has only one physical layout (v2/postal.scad has no\n"
                        "preset-switching menu) - QWERTY is it. Use Modify glyphs below\n"
                        "to hand-edit the 3 rows if you need something else.",
                        classes="picker-help")
                else:
                    yield Static(
                        "No named layout presets for this machine yet - use Modify glyphs\n"
                        "below to hand-edit the 3 rows directly.",
                        classes="picker-help")

                yield Static("Rows (read-only preview of the preset above):", classes="field-label")
                display_rows = self._display_rows_for_preset()
                for i in range(3):
                    static = Static(display_rows[i], id=f"layout-original-row-{i}", classes="row-preview")
                    yield static

                with Horizontal(classes="picker-row"):
                    yield Static("Modify glyphs", classes="field-label")
                    modify_now = bool(self.cfg["layout"]["modify_glyphs"])
                    sw = Switch(value=modify_now, id="layout-modify-glyphs")
                    yield sw
                yield Static(
                    f"Unlocks a hand-editable copy of the 3 rows below, capped at\n"
                    f"{char_cap} characters each (placement_map's length - more than that\n"
                    "would crash TextRing). Fewer than that just leaves some physical\n"
                    "positions unstruck. While on, this edited copy - not the preset\n"
                    "dropdown above - is what gets saved to layout.rows.",
                    classes="picker-help")

                custom_rows_container = Vertical(id="layout-custom-rows")
                custom_rows_container.display = modify_now
                with custom_rows_container:
                    current_rows = self.cfg["layout"]["rows"]
                    for i in range(3):
                        inp = Input(value=current_rows[i], id=f"layout-custom-row-{i}",
                                    max_length=char_cap, classes="custom-row-input")
                        yield inp

    def _compose_build_tab(self):
        with TabPane("Build", id="tab-build"):
            with VerticalScroll():
                with Vertical(classes="picker-row"):
                    yield Static("Build target", classes="field-label")
                    target_now = self.cfg.get("build", {}).get("target", "element")
                    if target_now not in ("element", "gauge", "calibration"):
                        target_now = "element"
                    build_select = Select(
                        [("Element", "element"), ("Shaft Gauge", "gauge"),
                         ("Calibration Element", "calibration")],
                        value=target_now, id="build-select", allow_blank=False)
                    yield build_select
                with Horizontal(classes="picker-row"):
                    yield Static("Resin supports", classes="field-label")
                    resin_now = bool(self.cfg.get("build", {}).get("resin_support"))
                    sw = Switch(value=resin_now, id="build-resin-support")
                    yield sw
                yield Static(
                    "Element = FullElement(), or ResinPrint() (adds ResinSupport()'s\n"
                    "rods/breakaway ring) if Resin supports is on - see the Resin tab\n"
                    "for its own settings, which only matter when this is on. Shaft\n"
                    "Gauge = GaugeTestSet() (see the Gauge tab) - a calibration test\n"
                    "print, not part of the real element; always has its own resin\n"
                    "supports built in regardless of this checkbox. Calibration\n"
                    "Element = a real element with the SAME test character struck at\n"
                    "every position, sweeping baseline or platen cutout per column\n"
                    "(see the Calibration tab) - for empirically finding\n"
                    "layout.baseline_row/cutout_row.",
                    classes="picker-help")

    def _compose_type_test_tab(self):
        with TabPane("Type Test", id="tab-type-test"):
            with VerticalScroll():
                yield Static(
                    "Flat, fixed-pitch (CPI) test block - matches v2's TypeTest()\n"
                    "spacing convention. Uses the Font tab's path/size. NOT part of\n"
                    "the real element - overwrites the same scratch output STL as\n"
                    "Render/Quick Preview, so the same f3d --watch window shows it.\n"
                    "Multiple lines are supported (stacked vertically).",
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
                yield from self._compose_section_tab("Gauge")
                yield from self._compose_section_tab("Calibration")
                yield from self._compose_build_tab()
                yield from self._compose_layout_tab()
                yield from self._compose_section_tab("Quality")
                yield from self._compose_section_tab("Logo")
                yield from self._compose_section_tab("Element")

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
            yield RichLog(id="log", wrap=True, markup=True, min_width=1)

    def log_line(self, text):
        self.query_one("#log", RichLog).write(text)

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
        values["target"] = self.query_one("#build-select", Select).value
        values["resin_support"] = self.query_one("#build-resin-support", Switch).value
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
        for key in BASELINE_CUTOUT_KEYS:
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
            if key in BASELINE_CUTOUT_KEYS:
                continue
            text = patch_yaml_value(text, key, value)
        for key in BASELINE_CUTOUT_KEYS:
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
            custom_rows = [self.query_one(f"#layout-custom-row-{i}", Input).value[:char_cap] for i in range(3)]
            text = patch_yaml_rows(text, custom_rows)
        else:
            layout_select = self.query_one("#layout-select", Select)
            if layout_select.value is not Select.NULL:
                text = patch_yaml_rows(text, self.LAYOUT_PRESETS[layout_select.value])
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
        if target_now not in ("element", "gauge", "calibration"):
            # "resin" was a valid target value before the Build tab's
            # dropdown was split into target + a separate Resin supports
            # checkbox - a running copy saved before that change could
            # still have it on disk; map it back to plain "element" (the
            # checkbox itself carries whether resin support is on now)
            target_now = "element"
        self.query_one("#build-select", Select).value = target_now
        self.query_one("#build-resin-support", Switch).value = bool(self.cfg["build"]["resin_support"])
        self.query_one("#type-test-cpi", Input).value = str(self.cfg["type_test"]["cpi"])
        self.query_one("#type-test-lpi", Input).value = str(self.cfg["type_test"]["lpi"])
        self.query_one("#type-test-text", TextArea).text = self.cfg["type_test"]["text"]
        display_rows = self._display_rows_for_preset()
        for i in range(3):
            self.query_one(f"#layout-original-row-{i}", Static).update(display_rows[i])
        modify_glyphs = bool(self.cfg["layout"]["modify_glyphs"])
        self.query_one("#layout-modify-glyphs", Switch).value = modify_glyphs
        self.query_one("#layout-custom-rows").display = modify_glyphs
        current_rows = self.cfg["layout"]["rows"]
        for i in range(3):
            self.query_one(f"#layout-custom-row-{i}", Input).value = current_rows[i]
        for arr_key in ("baseline_row", "cutout_row"):
            arr = self.cfg["layout"][arr_key]
            for i in range(3):
                self.inputs[f"{arr_key}_{i}"].value = str(arr[i])

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
        what shows the picker (see compose())."""
        self._save_before_exit()
        self.machine = None
        await self.recompose()

    async def _ensure_f3d_after_build(self, out_path, camera_flags=()):
        """Called after a successful Preview/Render/Render Text. If f3d
        isn't running (or the process we launched has since exited),
        launch it fresh - it'll show the just-written STL immediately.
        camera_flags (only meaningful on a fresh launch - f3d has no way
        to change an already-running instance's camera from the CLI) let
        the caller pick a starting view, e.g. top-down for flat text.
        If f3d is already running, its own --watch reloads the model
        automatically (keeping whatever camera the user's since set); we
        just try to raise the window, after a short pause so the reload
        has actually happened first (raising it to show the STALE model
        would defeat the point)."""
        if not self.query_one("#f3d-preview-checkbox", Switch).value:
            return
        if self._f3d_proc is None or self._f3d_proc.poll() is not None:
            try:
                self._f3d_proc = subprocess.Popen(
                    ["f3d", "--watch", out_path, "-g", "-x", *camera_flags],
                    cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        if values["target"] == "gauge":
            # GaugeTestSet() doesn't touch TextRing/build_glyph at all, so
            # the Minkowski/points-per-mm knobs don't apply here - only
            # --no-core-groove (still worth skipping for a quick check)
            cmd += ["--gauge"]
            if fast:
                cmd += ["--no-core-groove"]
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
                cmd += ["--no-minkowski", "--no-core-groove"]
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
            if fast:
                cmd += ["--no-minkowski", "--no-core-groove"]
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

    async def _stream_subprocess(self, cmd):
        t0 = time.time()
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=REPO_ROOT,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        async for line in proc.stdout:
            self.log_line(line.decode(errors="replace").rstrip())
        await proc.wait()
        dt = time.time() - t0
        if proc.returncode == 0:
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
        for i in range(3):
            self.query_one(f"#layout-original-row-{i}", Static).update(display_rows[i])

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
            for i in range(3):
                self.query_one(f"#layout-custom-row-{i}", Input).value = display_rows[i]

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
