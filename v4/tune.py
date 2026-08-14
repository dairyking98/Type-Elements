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
  - RUNNING is a per-MACHINE scratch copy (<machine>.running.yaml, same
    directory as master, gitignored) that every edit/save actually goes
    to - shared by every font-variant master config for that machine
    (e.g. every selectric12_*.yaml Browses to the same selectric12.
    running.yaml), not one file per master. Bootstrapped as a copy of
    master the first time it's needed; "once changed, always changed" -
    it persists across tune.py restarts against the SAME master, picking
    up wherever you left off. A `# source_master:` header line tracks
    which master it was last synced from - Browsing to a DIFFERENT
    master (a different variant of the same machine) resets it fresh
    from that master rather than showing an unrelated variant's edits
    (see _ensure_running_config()). Reset to Defaults (also top of
    screen) overwrites the running copy with a fresh copy of master,
    discarding all accumulated edits. If master has since gained fields
    the running copy predates (e.g. a codebase update adds a new config
    section), they're auto-backfilled from master on load - see
    _migrate_running_config() - without touching anything you've already
    customized.
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

Tabs (in display order). Which ones a given machine gets is decided in
one place, _tab_specs() - the section-nav list down the left of the form
and the TabbedContent panes themselves are both built from it, so they
can't disagree. TabbedContent's own horizontal tab bar is hidden; that
list replaces it (see _compose_tuner_ui):
  Font & Alignment - font.* + alignment.* (combined, both are "how
    characters are placed/rendered" concerns). alignment.mode is a
    dropdown ("center"/"left"), not free text. font.path has two
    pickers: "Installed" lists every font installed on this machine by
    NAME (fontconfig on Linux, the Windows font directories on Windows -
    see lib/system_fonts.py) with a type-to-filter box, and "File" is a
    plain file browser (textual_fspicker.FileOpen, filtered to
    .ttf/.otf/.ttc) opening at the current path's directory, for a font
    that isn't installed. Either way the config still stores a path.
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
  Quality          - quality.* facet counts + build.flatness_tolerance_mm/
    separation_mm/render_core_groove (moved here from Build - these are
    all mesh generation quality/speed knobs, not "what to build"). The
    Minkowski draft sweep itself is NOT exposed
    here - Render always forces it on and Quick Preview always forces
    it off (see _run_build), so a config-file toggle would just be
    dead weight/a second source of truth.
  Logo             - logo.* (font_path also has the same "Installed"/
    "File" pickers as font.path above)
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

import freetype
import yaml
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Resize
from textual.screen import ModalScreen
from textual.widgets import (Button, Footer, Header, Input, OptionList, ProgressBar, Select, SelectionList, Static,
                              Switch, RichLog, TabbedContent, TabPane, TextArea)
from textual.widgets.selection_list import Selection  # noqa: E402
from textual.widgets.option_list import Option
from textual_fspicker import FileOpen, FileSave, Filters, SelectDirectory

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, "lib"))
import f3d_bootstrap  # noqa: E402 - needs the lib/ sys.path.insert above first

# f3d --command-script file: just `set_camera top`, the exact console
# command the "7" key runs - see action_render_type_test's use of it
F3D_TOP_VIEW_SCRIPT = os.path.join(REPO_ROOT, "f3d_top_view_cmds.txt")


def _raise_window_by_pid(pid):
    """Windows equivalent of `wmctrl -a f3d` - best-effort, no wmctrl
    equivalent exists there, so this shells straight to user32 instead.
    Finds the given process's own top-level window (matching by PID,
    same as wmctrl matching by title, since f3d.exe's window is created
    in-process) and raises it. Returns False if no window was found or
    Windows' foreground-lock timeout refused the raise (only guaranteed
    to succeed when tune.py's own console is already the foreground
    window - there's no API to force it otherwise, matching wmctrl's own
    best-effort nature on Linux)."""
    import ctypes
    user32 = ctypes.windll.user32
    SW_RESTORE = 9
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def _enum_proc(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        window_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid:
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(_enum_proc, 0)
    if not found:
        return False
    user32.ShowWindow(found[0], SW_RESTORE)  # in case it's minimized
    return bool(user32.SetForegroundWindow(found[0]))

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

FONT_FILE_FILTERS = Filters(
    ("Font files", lambda p: p.suffix.lower() in (".ttf", ".otf", ".ttc")),
    ("All files", lambda _: True),
)
STL_FILE_FILTERS = Filters(("STL files", lambda p: p.suffix.lower() == ".stl"))
SVG_FILE_FILTERS = Filters(("SVG files", lambda p: p.suffix.lower() == ".svg"))
MD_FILE_FILTERS = Filters(("Markdown files", lambda p: p.suffix.lower() == ".md"))
# Font Coverage tab's scratch output - same fixed-scratch-path-then-Save
# convention as the STL (output.directory/output.stl_name) and the Legend
# SVG (generate_legend.py's default path), just rooted outside any one
# machine's output.directory since this tab is standalone (doesn't read
# or write the loaded config at all).
FONT_COVERAGE_REPORT_PATH = os.path.join(REPO_ROOT, "output", "font_coverage_report.md")
YAML_FILE_FILTERS = Filters(
    ("YAML files", lambda p: p.suffix.lower() in (".yaml", ".yml")),
    ("All files", lambda _: True),
)
# font.path (Font & Alignment tab), logo.font_path (Logo tab), Mignon's
# label.font_path (Logo tab, label_font_path key - see LOGO_FIELDS_MIGNON),
# and Bennett's label.font_path (Label tab, plain font_path key - see
# LABEL_FIELDS_BENNETT) are the font-picking fields - each gets an
# "Installed" button (SystemFontPicker, pick by font name) and a "File"
# button (FileOpen, pick any font file); see _compose_section_tab and
# on_button_pressed's "sysfont-"/"browse-" id handling
FONT_PATH_FIELD_KEYS = ("path", "font_path", "label_font_path", "legend_font_path")


def _font_display_name(path):
    """Reads the font file's own internal family/style name (via
    freetype, not glyph_poc.load_font_face() - avoids pulling in that
    module's trimesh/manifold3d import chain just to read a name table)
    for the "Currently selected: ..." label under every font path field -
    a long absolute path often doesn't visually reveal which font it
    actually is (a renamed/copied file, a version-numbered filename, a
    family with many near-identical style variants in the same
    directory). Never raises - a missing/corrupt file is exactly the
    case this label needs to surface clearly, not crash the TUI over."""
    if not path:
        return "Currently selected: (no path set)"
    if not os.path.isfile(path):
        return "Currently selected: (file not found)"
    try:
        face = freetype.Face(path)
        family = (face.family_name or b"").decode("utf-8", errors="replace")
        style = (face.style_name or b"").decode("utf-8", errors="replace")
    except Exception as e:
        return f"Currently selected: (unreadable - {e})"
    if not family:
        return "Currently selected: (font has no family name)"
    return f"Currently selected: {family}" + (f" {style}" if style and style != "Regular" else "")

# Installed-font enumeration (fontconfig on Linux, the Windows font
# directories on Windows) lives in lib/system_fonts.py, NOT here - see
# that module's docstring for what counts as "installed" per platform.
from lib.system_fonts import display_name as font_display_name  # noqa: E402
from lib.system_fonts import list_system_fonts  # noqa: E402

# Layout presets/help for every machine live in lib/layouts/ (one module
# per machine), NOT here - tune.py hardcodes no layout data of its own.
import lib.font_profiles as font_profiles
from lib.layouts import (  # noqa: E402
    LAYOUT_PICKER_HELP,
    LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE,
    LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE,
    LAYOUT_PRESETS_BY_MACHINE,
)

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
        ("caret_drop_mm", ["alignment", "caret_drop_mm"], float, "Caret drop (mm)",
         "Shifts \"^\" down onto the baseline. Fonts draw U+005E at cap height because there it doubles as the spacing circumflex accent; the Blickensderfer caret sits low. 0 = use the font's own position."),
        ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
         "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
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
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth. Real value 0.5mm."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("body_fn", ["quality", "body_fn"], int, "Body fn", "Main cosmetic cylinder body (Cylinder/ClipCylinder)."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Inner shaft/core bore only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowSpace, SpeedHoles, chamfers...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
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
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "CenterShaft only."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "HollowBody/ElementChamfer/MinkCleanup."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
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
    ("label1a_radial_mm", ["label", "label1a_radial_mm"], float, "Label 1a radial distance (mm)",
     "World-X distance of label1a's text from the shaft center. Independent of label1b/label2 - see LabelText()'s docstring."),
    ("label1b_radial_mm", ["label", "label1b_radial_mm"], float, "Label 1b radial distance (mm)",
     "World-X distance of label1b's text from the shaft center. Independent of label1a/label2 - see LabelText()'s docstring."),
    ("label2_radial_mm", ["label", "label2_radial_mm"], float, "Label 2 radial distance (mm)",
     "World-X distance of label2's text from the shaft center (negative = opposite side from label1a/1b)."),
]

QUALITY_FIELDS_BENNETT = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft/pin fn", "PositionerPins/CenterShaft."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowBody, SpeedHoles, countersinks...)."),
    ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
    ("alignment_hole_fn", ["quality", "alignment_hole_fn"], int, "Alignment hole fn", "AlignmentHoles facet count."),
    ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
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
# these can't share any other machine's field lists. No "Label" key (v2
# has no engraved-TEXT feature - v2's own header: "Sections with no
# Helios equivalent (Logo, Print Tolerances, Shaft Gauge Test) are
# omitted"), no "Gauge" key (same reason). "Logo" IS present below -
# unlike v2, v1's separate SVG_Logo mark (an imported vector image, not
# engraved text) was ported as a deliberate v1-sourced addition - see
# LOGO_FIELDS_HELIOS and config/helios.yaml's logo: section.
QUALITY_FIELDS_HELIOS = [
    ("flatness_tolerance_mm", ["build", "flatness_tolerance_mm"], float, "Flatness tolerance (mm)", "Max allowed deviation between the flattened glyph outline and the true curve - smaller = more points/slower, larger = fewer points/faster."),
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
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
    ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth."),
    ("cyl_fn", ["quality", "cyl_fn"], int, "Cylinder fn", "Shuttle arc body (ShuttleCylinder/Rib/PinSupport)."),
    ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Mirrors cyl_fn - no separate structural tier."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with flatness_tolerance_mm."),
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
    + [CLIP_TO_CELL_FIELD])

FONT_FIELDS_HAMMOND_SPLIT = [
    ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters (Type_Face)."),
    ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Type_Size - em-square size."),
    ("font2_chars", ["font2", "font2_chars"], str, "Font 2 chars", "v2 Char_Mod - characters that use font 2 instead of the main font."),
    ("font2_path", ["font2", "font2_path"], str, "Font 2 path", "v2 Char_Mod_Font."),
    ("font2_size_mm", ["font2", "font2_size_mm"], float, "Font 2 size (mm)", "v2 Char_Mod_Size."),
    ("draft_angle_deg", ["build", "draft_angle_deg"], float, "Draft angle (deg)",
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
    ("caret_drop_mm", ["alignment", "caret_drop_mm"], float, "Caret drop (mm)",
     "Shifts \"^\" down onto the baseline. Fonts draw U+005E at cap height because there it doubles as the spacing circumflex accent; the Blickensderfer caret sits low. 0 = use the font's own position."),
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
    CLIP_TO_CELL_FIELD,
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
    ("caret_drop_mm", ["alignment", "caret_drop_mm"], float, "Caret drop (mm)",
     "Shifts \"^\" down onto the baseline. Fonts draw U+005E at cap height because there it doubles as the spacing circumflex accent. 0 = use the font's own position."),
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
    ("draft_angle_deg", ["build", "draft_angle_deg"], float, "Draft angle (deg)",
     "Half-angle of the Minkowski draft cone each character is swept with. Real value 55."),
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
    ("caret_drop_mm", ["alignment", "caret_drop_mm"], float, "Caret drop (mm)",
     "Shifts \"^\" down onto the baseline. Fonts draw U+005E at cap height because there it doubles as the spacing circumflex accent. 0 = use the font's own position."),
    ("underscore_lift_mm", ["alignment", "underscore_lift_mm"], float, "Underscore lift (mm)",
     "Shifts \"_\" up. Many TTFs sink U+005F below the baseline to clear descenders, which drops it out of the struck character cell. 0 = use the font's own position."),
    ("draft_angle_deg", ["build", "draft_angle_deg"], float, "Draft angle (deg)",
     "Half-angle of the Minkowski draft cone each character is swept with. Real value 55."),
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
    ("character_block_height_mm", ["build", "character_block_height_mm"], float, "Character block height (mm)",
     "v2's linear_extrude(6) construction margin - must exceed any character's real embed depth."),
    ("mink_cone_height_mm", ["build", "mink_cone_height_mm"], float, "Minkowski cone height (mm)", "v2's hardcoded cylinder h=2 in the draft cone."),
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
]

# element: schema is byte-identical across all 3 Selectric machines (same
# physical ball) - one shared table.
ELEMENT_FIELDS_SELECTRIC = [
    ("sphere_od", ["element", "sphere_od"], float, "Sphere OD (mm)", "v2 Sphere_OD."),
    ("max_od", ["element", "max_od"], float, "Max character OD (mm)", "v2 Max_OD - character-concave to character-concave diameter."),
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
]

RESIN_FIELDS_BOX_SLUG = [
    ("resin_fn", ["resin", "resin_fn"], int, "Resin support facets",
     "Declared but not wired to any geometry - Oliver Slug/Lumi Slug have no resin-support geometry at all, see lib/box_slug.py's ResinSupport()."),
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

SECTIONS_BY_MACHINE = {
    "blickensderfer": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_BLICKPOSTAL,
                       "Quality": QUALITY_FIELDS_BLICKPOSTAL, "Resin": RESIN_FIELDS_BLICKPOSTAL,
                       "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_BLICKENSDERFER,
                       "Cosmetics": COSMETICS_FIELDS},
    "postal": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_BLICKPOSTAL,
               "Quality": QUALITY_FIELDS_BLICKPOSTAL, "Resin": RESIN_FIELDS_BLICKPOSTAL,
               "Gauge": GAUGE_FIELDS, "Element": ELEMENT_FIELDS_POSTAL,
                       "Cosmetics": COSMETICS_FIELDS},
    # no "Gauge" key - Mignon has no Shaft Gauge Test (see
    # ELEMENT_FIELDS_MIGNON's neighboring comment) - compose()/
    # _compose_build_tab() check for its absence and skip the tab/dropdown
    # option accordingly, rather than every machine being forced to have one.
    "mignon": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_MIGNON, "Label": LABEL_FIELDS_MIGNON,
               "Quality": QUALITY_FIELDS_MIGNON, "Resin": RESIN_FIELDS_MIGNON,
               "Element": ELEMENT_FIELDS_MIGNON, "Legend": LEGEND_FIELDS_MIGNON},
    # no "Gauge" key - Bennett has no Shaft Gauge Test either (v2/bennett.
    # scad:24: "Sections with no Bennett equivalent (Print Tolerances,
    # Shaft Gauge Test) are omitted"). No "Logo" key - its one engraved-
    # text feature is LABEL_FIELDS_BENNETT's "Label" tab instead (see that
    # list's neighboring comment).
    "bennett": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Label": LABEL_FIELDS_BENNETT,
                "Quality": QUALITY_FIELDS_BENNETT, "Resin": RESIN_FIELDS_BENNETT,
                "Element": ELEMENT_FIELDS_BENNETT},
    # no "Gauge" key - Helios has no Shaft Gauge Test (v2/heliosklimax.
    # scad's own header: "Sections with no Helios equivalent (Logo, Print
    # Tolerances, Shaft Gauge Test) are omitted"). No "Label" key either -
    # same header, no engraved-TEXT feature at all. "Logo" key IS present
    # (LOGO_FIELDS_HELIOS) - v1's separate SVG_Logo mark, a deliberate
    # v1-sourced addition v2 never had - see that list's own comment.
    "helios": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Logo": LOGO_FIELDS_HELIOS, "Quality": QUALITY_FIELDS_HELIOS,
               "Resin": RESIN_FIELDS_HELIOS, "Element": ELEMENT_FIELDS_HELIOS},
    # no "Gauge"/"Logo" key - Hammond has neither (see lib/hammond.py's
    # module docstring) - its two whole-string engraved labels are the
    # "Label" tab instead, same convention as Bennett.
    "hammond": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_CYLINDER, "Label": LABEL_FIELDS_HAMMOND,
                "Quality": QUALITY_FIELDS_HAMMOND, "Resin": RESIN_FIELDS_HAMMOND,
                "Element": ELEMENT_FIELDS_HAMMOND, "Rib": RIB_FIELDS_HAMMOND,
                "Legend": LEGEND_FIELDS_HAMMOND},
    # no "Gauge"/"Logo" key - same reasons as Hammond above. "Font &
    # Alignment" is overridden (not the shared SECTIONS_COMMON one) - see
    # FONT_FIELDS_HAMMOND_SPLIT's own comment for why (no draft_angle_deg
    # field here, plus the char_mod fields no other machine has). "Legend"
    # reuses LEGEND_FIELDS_HAMMOND/lib/hammond_legend.py as-is - see that
    # module's docstring for why the same card shape applies to both.
    "hammond_split": {**SECTIONS_COMMON, "Font & Alignment": FONT_FIELDS_HAMMOND_SPLIT,
                       "Label": LABEL_FIELDS_HAMMOND_SPLIT, "Quality": QUALITY_FIELDS_HAMMOND_SPLIT,
                       "Resin": RESIN_FIELDS_HAMMOND_SPLIT, "Element": ELEMENT_FIELDS_HAMMOND_SPLIT,
                       "Legend": LEGEND_FIELDS_HAMMOND},
    # No SECTIONS_COMMON reuse at all - Selectric's alignment/calibration
    # schema doesn't match the cylinder family's (see FONT_FIELDS_
    # SELECTRIC12's own comment above). No "Gauge"/"Logo"/"Calibration"
    # key - see this dict's own leading comment.
    "selectric12": {"Font & Alignment": FONT_FIELDS_SELECTRIC12, "Label": LABEL_FIELDS_SELECTRIC,
                    "Quality": QUALITY_FIELDS_SELECTRIC, "Resin": RESIN_FIELDS_SELECTRIC,
                    "Element": ELEMENT_FIELDS_SELECTRIC},
    "selectric3": {"Font & Alignment": FONT_FIELDS_SELECTRIC12, "Label": LABEL_FIELDS_SELECTRIC,
                   "Quality": QUALITY_FIELDS_SELECTRIC, "Resin": RESIN_FIELDS_SELECTRIC,
                   "Element": ELEMENT_FIELDS_SELECTRIC},
    "selectric_composer": {"Font & Alignment": FONT_FIELDS_SELECTRIC_COMPOSER, "Label": LABEL_FIELDS_SELECTRIC,
                           "Quality": QUALITY_FIELDS_SELECTRIC, "Resin": RESIN_FIELDS_SELECTRIC,
                           "Element": ELEMENT_FIELDS_SELECTRIC},
    # Type Slug family (see the FIELDS block comment above this dict) -
    # "Font & Alignment" reuses ONLY that one SECTIONS_COMMON list (not
    # the whole dict spread, which would also pull in "Calibration" -
    # not implemented for this family). No "Gauge"/"Calibration" key.
    "type_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                  "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                  "Label": LABEL_FIELDS_SLUG, "Quality": QUALITY_FIELDS_WING_SLUG,
                  "Resin": RESIN_FIELDS_WING_SLUG, "Element": ELEMENT_FIELDS_WING_SLUG},
    "vogue_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                   "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                   "Label": LABEL_FIELDS_SLUG, "Quality": QUALITY_FIELDS_WING_SLUG,
                   "Resin": RESIN_FIELDS_WING_SLUG, "Element": ELEMENT_FIELDS_WING_SLUG},
    # "Ticks" (not "Gauge") - see TICKS_FIELDS_GAUGE_SLUG's own comment
    # for why this deliberately doesn't reuse the existing "Gauge"
    # section name.
    "gauge_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                   "Character": CHARACTER_FIELDS_WING_SLUG, "Logo": LOGO_FIELDS_SLUG,
                   "Label": LABEL_FIELDS_SLUG, "Ticks": TICKS_FIELDS_GAUGE_SLUG,
                   "Quality": QUALITY_FIELDS_WING_SLUG, "Resin": RESIN_FIELDS_WING_SLUG,
                   "Element": ELEMENT_FIELDS_WING_SLUG},
    # No "Label"/"Logo" key - OliverSlug.scad/LumiSlug.scad have no
    # engraved-copyright/SVG-logo concept at all (see lib/box_slug.py's
    # module docstring).
    "oliver_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                    "Character": CHARACTER_FIELDS_BOX_SLUG, "Quality": QUALITY_FIELDS_BOX_SLUG,
                    "Resin": RESIN_FIELDS_BOX_SLUG, "Element": ELEMENT_FIELDS_BOX_SLUG},
    "lumi_slug": {"Font & Alignment": SECTIONS_COMMON["Font & Alignment"],
                  "Character": CHARACTER_FIELDS_BOX_SLUG, "Quality": QUALITY_FIELDS_BOX_SLUG,
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


class ProfileApplyPicker(ModalScreen[list | None]):
    """Choose which of a profile's values to apply. Dismisses with the
    list of chosen target paths, or None if cancelled.

    Exists because applying a profile ACROSS machine families is rarely
    all-or-nothing: you usually want the typeface but not, say, a
    print-critical position offset the target machine sets for its own
    reasons. Everything starts checked, so the common same-family case is
    still one Enter.

    Rows reached through an equivalence (the same knob under this
    family's own name) are labelled with where they came from, since that
    is the case worth a second look before accepting."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, profile_name, applied, aliased, skipped, unset):
        super().__init__()
        self._profile_name = profile_name
        self._applied = applied
        self._aliased = aliased
        self._skipped = skipped
        self._unset = unset

    def compose(self) -> ComposeResult:
        with Vertical(id="fontpicker"):
            yield Static(f"Apply profile: {self._profile_name}", classes="picker-title")
            yield Static(
                "Everything is selected by default. Space toggles a row, Enter applies, "
                "Esc cancels.", classes="picker-help")
            selections = []
            for path in sorted(self._applied):
                selections.append(Selection(f"{path} = {self._applied[path]!r}", path, True))
            for path in sorted(self._aliased):
                value, source = self._aliased[path]
                selections.append(
                    Selection(f"{path} = {value!r}   (from {source})", path, True))
            if selections:
                yield SelectionList(*selections, id="profileapply-list")
            else:
                yield Static("Nothing in this profile applies to this machine.",
                              classes="picker-help")
            if self._skipped:
                yield Static(f"Not on this machine, ignored: {', '.join(self._skipped)}",
                              classes="picker-help")
            if self._unset:
                yield Static(
                    f"This machine has {len(self._unset)} field(s) the profile does not "
                    f"set, which keep their current values: {', '.join(self._unset)}. "
                    f"Usually harmless - they are this family's own extras - but worth a "
                    f"glance if the result looks off.", classes="picker-help")
            with Horizontal(classes="font-btn-row"):
                yield Button("Apply", id="profileapply-ok", classes="sysfont-btn")
                yield Button("Cancel", id="profileapply-cancel", classes="sysfont-btn")

    def on_mount(self) -> None:
        try:
            self.query_one("#profileapply-list", SelectionList).focus()
        except NoMatches:
            pass

    def _chosen(self):
        try:
            return list(self.query_one("#profileapply-list", SelectionList).selected)
        except NoMatches:
            return []

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(self._chosen() if event.button.id == "profileapply-ok" else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ProfileNamePrompt(ModalScreen[str | None]):
    """Asks for a name when saving a Font & Alignment profile. Dismisses
    with the typed name, or None if cancelled. Pre-filled with the
    currently-active profile name so re-saving over it is the default
    action rather than something you have to retype exactly."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, initial=""):
        super().__init__()
        self._initial = initial or ""

    def compose(self) -> ComposeResult:
        with Vertical(id="fontpicker"):
            yield Static("Save Font & Alignment profile", classes="picker-title")
            yield Static(
                "Profiles are machine-independent: applying one to another machine "
                "sets the values that machine has and leaves the rest alone. Saving "
                "over an existing name updates it.",
                classes="picker-help")
            yield Input(value=self._initial, placeholder="profile name",
                         id="profilename-input")
            yield Button("Cancel", id="profilename-cancel")

    def on_mount(self) -> None:
        self.query_one("#profilename-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        self.dismiss(name or None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class SystemFontPicker(ModalScreen[str | None]):
    """The "Installed" button next to every font path field (see
    FONT_PATH_FIELD_KEYS): pick a font BY NAME out of everything
    installed on this machine, instead of hunting for its file with the
    "File" button's FileOpen browser. Dismisses with the chosen font's
    path (the config value is still a plain path - this only changes how
    it's chosen) or None if cancelled.

    A filtered list rather than a plain Select dropdown because the real
    font count is not dropdown-sized - this development machine reports
    ~2200 installed files, and a 2200-row overlay with no way to type at
    it is unusable. The filter matches all whitespace-separated tokens
    against family + style + path together, so "alma bold" and "ocr otf"
    both narrow the way you'd expect.

    EVERY match is listed, deliberately uncapped - browsing the whole
    library by scrolling (rather than knowing what to search for) is a
    real way to use this, and a cap turns that into a dead end at
    whatever number was picked. An earlier 300-item cap was removed once
    measured: rebuilding the full 2214-entry list costs ~21ms in
    add_options plus ~67ms to settle, against ~33ms for 300.

    What the cap WAS covering, and what covers it now: a keystroke whose
    filter still matches nearly everything (typing "a" - every path
    contains one) rebuilds the whole list, measured at 150-240ms, which
    is enough to feel like lag while typing. So the filter is debounced
    by FILTER_DEBOUNCE_SECONDS instead - fast typing schedules one
    rebuild after the last keystroke rather than one per keystroke - and
    that scales with the library instead of truncating it. Enter flushes
    any pending rebuild before picking, so a type-then-immediately-Enter
    never acts on a stale list.

    Enumeration itself (which directories count as "installed" on Linux
    vs Windows) is lib/system_fonts.py's job, not this screen's."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        # Up/down/PageUp/PageDown while the filter Input has focus - an
        # Input doesn't consume vertical arrows or paging keys (it's
        # single-line), so these reach the screen and drive the list's
        # highlight without having to tab away from the filter first.
        # Paging matters here specifically because the list is uncapped:
        # scrolling a couple thousand fonts one arrow-press at a time is
        # not browsing. (The mouse wheel over the list works regardless
        # of focus, and Tab moves focus into the list itself for its own
        # native navigation.)
        ("down", "move(1)", "Next"),
        ("up", "move(-1)", "Previous"),
        ("pagedown", "page(1)", "Page down"),
        ("pageup", "page(-1)", "Page up"),
    ]

    # Long enough that ordinary typing coalesces into one rebuild, short
    # enough that a pause between words still feels immediate.
    FILTER_DEBOUNCE_SECONDS = 0.15

    def __init__(self, current_path=None, title="Installed fonts"):
        super().__init__()
        self._current_path = current_path or ""
        self._title = title
        self._fonts = []
        self._shown = []
        self._filter_timer = None

    def compose(self) -> ComposeResult:
        with Vertical(id="fontpicker"):
            yield Static(self._title, classes="picker-title")
            yield Static(
                "Type to filter, or just scroll the whole list. Up/down and "
                "PageUp/PageDown move, Enter picks, Esc cancels.",
                classes="picker-help")
            yield Input(placeholder="family, style or filename", id="fontpicker-filter")
            yield OptionList(id="fontpicker-list")
            yield Static("", id="fontpicker-path", classes="picker-help")
            yield Static("", id="fontpicker-count", classes="picker-help")
            yield Button("Cancel", id="fontpicker-cancel")

    def on_mount(self) -> None:
        # The currently-configured font is passed in as an extra path so
        # a font living outside any installed location (picked earlier
        # with "File") still appears - and is pre-highlighted - instead
        # of the picker opening on an unrelated font.
        self._fonts = list_system_fonts(extra_paths=(self._current_path,))
        self._repopulate("")
        self.query_one("#fontpicker-filter", Input).focus()

    def _abs_current(self):
        """The configured path in the same absolutized form
        lib/system_fonts.py stores, so identity comparisons against
        enumerated entries actually match."""
        if not self._current_path:
            return ""
        return os.path.abspath(os.path.expanduser(self._current_path))

    def _repopulate(self, query):
        tokens = query.lower().split()
        matches = [e for e in self._fonts
                   if all(t in f"{e.family} {e.style} {e.path}".lower() for t in tokens)]
        # The currently-configured font is pinned to the top of whatever
        # matched (and highlighted, below) - otherwise the picker opens
        # scrolled to "A..." in an alphabetical list of a couple thousand
        # fonts, with no sign of what's actually selected right now.
        current = self._abs_current()
        if current:
            for i, e in enumerate(matches):
                if e.path == current:
                    matches.insert(0, matches.pop(i))
                    break
        self._shown = matches
        option_list = self.query_one("#fontpicker-list", OptionList)
        option_list.clear_options()
        # Options are looked up by INDEX into self._shown, not by an
        # Option id - two installed files can legitimately produce the
        # same display name, and duplicate ids raise.
        option_list.add_options(
            [Option(f"{font_display_name(e)}  -  {os.path.basename(e.path)}") for e in self._shown])
        if self._shown:
            option_list.highlighted = next(
                (i for i, e in enumerate(self._shown) if e.path == current), 0)
        count = self.query_one("#fontpicker-count", Static)
        if tokens:
            count.update(f"{len(matches)} of {len(self._fonts)} installed fonts match")
        else:
            count.update(f"{len(self._fonts)} installed fonts")
        if not self._shown:
            self.query_one("#fontpicker-path", Static).update("")

    def _pick(self, index):
        if index is None or not 0 <= index < len(self._shown):
            return
        self._cancel_pending_filter()
        self.dismiss(self._shown[index].path)

    def _cancel_pending_filter(self):
        if self._filter_timer is not None:
            self._filter_timer.stop()
            self._filter_timer = None

    def _flush_pending_filter(self):
        """Applies a debounced filter rebuild immediately, for the paths
        that can't wait for the timer - Enter (about to act on the
        highlighted row) and dismissal (the timer must not fire against
        a screen that's already gone)."""
        if self._filter_timer is None:
            return
        self._cancel_pending_filter()
        self._repopulate(self.query_one("#fontpicker-filter", Input).value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "fontpicker-filter":
            event.stop()
            self._cancel_pending_filter()
            self._filter_timer = self.set_timer(
                self.FILTER_DEBOUNCE_SECONDS, lambda: self._repopulate(event.value))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter while still typing in the filter picks whatever's
        highlighted, so a narrow-then-Enter never needs a Tab in
        between - flushing first, since typing and hitting Enter inside
        the debounce window would otherwise pick out of the previous
        keystroke's list."""
        if event.input.id == "fontpicker-filter":
            event.stop()
            self._flush_pending_filter()
            self._pick(self.query_one("#fontpicker-list", OptionList).highlighted)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        if 0 <= event.option_index < len(self._shown):
            self.query_one("#fontpicker-path", Static).update(self._shown[event.option_index].path)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self._pick(event.option_index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fontpicker-cancel":
            event.stop()
            self.action_cancel()

    def action_move(self, delta: int) -> None:
        option_list = self.query_one("#fontpicker-list", OptionList)
        if not self._shown:
            return
        option_list.highlighted = max(
            0, min(len(self._shown) - 1, (option_list.highlighted or 0) + delta))

    def action_page(self, direction: int) -> None:
        """PageUp/PageDown by however many rows the list is currently
        showing (minus one for context, the usual pager convention),
        rather than a fixed guess - the modal is sized as a percentage
        of the terminal, so its row count isn't known up front."""
        option_list = self.query_one("#fontpicker-list", OptionList)
        page = max(1, option_list.size.height - 1)
        self.action_move(direction * page)

    def action_cancel(self) -> None:
        self._cancel_pending_filter()
        self.dismiss(None)


class TuneApp(App):
    CSS = """
    Screen { layout: horizontal; }
    /* 58 was the whole form pane before the section-nav list existed;
       it's now the CONTENT half, with the nav's 20 added on top. The
       max-width keeps a narrow terminal from handing the form so much
       that the log pane has nowhere to go. */
    #form { width: 78; max-width: 70%; height: 100%; border: solid $accent; }
    #form-body { height: 1fr; }
    #section-nav { width: 20; height: 1fr; border: none; border-right: solid $accent;
        padding: 0; background: transparent; }
    /* The highlighted row IS "which section you're looking at", so it has
       to read as selected even when focus is in a field somewhere - the
       default styling only stands out while the list itself has focus. */
    #section-nav > .option-list--option-highlighted {
        background: $accent; color: $text; text-style: bold; }
    /* width: 1fr is load-bearing - TabbedContent's own DEFAULT_CSS is
       width: 100%, which inside #form-body means 100% of the WHOLE row,
       not the part left over beside the nav, so without this it lays out
       20 columns wider than the form pane and overlaps the log pane. */
    #tabs { width: 1fr; }
    /* TabbedContent's own horizontal tab bar - replaced by #section-nav */
    #tabs ContentTabs { display: none; }
    #log-pane { width: 1fr; height: 100%; border: solid $accent; padding: 0 1; }
    #log { height: 1fr; }
    #progress-row { height: 1; margin-top: 1; }
    #build-progress { width: 1fr; }
    #build-progress Bar { width: 1fr; }
    #build-elapsed { width: auto; margin-left: 1; color: $text-muted; }
    #btn-cancel-build { width: auto; height: 1; min-width: 12; margin-left: 1; }
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
    .sysfont-btn { width: 11; height: 1; min-width: 11; border: none; margin-left: 1; }
    .font-btn-row { height: 1; align-horizontal: right; }
    SystemFontPicker { align: center middle; }
    #fontpicker { width: 90%; height: 90%; padding: 1 2; background: $surface; border: thick $accent; }
    #fontpicker-filter { height: 1; border: none; padding: 0 1; background: $panel; margin-bottom: 1; }
    #fontpicker-list { height: 1fr; border: none; background: $panel; }
    #fontpicker-path { margin-top: 1; }
    #fontpicker-cancel { width: 100%; height: 3; margin-top: 1; }
    #btn-reset-layout-rows { width: auto; height: 1; min-width: 0; border: none; margin-left: 1; }
    .field-help { color: $text-muted; height: auto; }
    #buttons { height: 11; dock: bottom; padding: 0 1; }
    #btn-render-test-text { height: 3; width: 1fr; text-style: bold; margin-bottom: 1; }
    #primary-buttons { height: 5; }
    #primary-buttons Button { width: 1fr; height: 5; text-style: bold; }
    #legend-buttons { height: 5; margin-top: 1; }
    #legend-buttons Button { width: 1fr; height: 5; text-style: bold; }
    #f3d-row { height: 1; margin-top: 1; }
    #f3d-row .field-label { width: auto; margin-right: 1; }
    #f3d-row Switch { width: auto; height: 1; border: none; padding: 0; }
    #status { height: 1; color: $text-muted; padding: 0 1; }
    #status-row { height: 1; padding: 0 1; }
    #status-row .browse-btn { margin-left: 0; }
    #btn-reset-defaults { width: 1fr; height: 1; border: none; margin-left: 1; }
    #btn-change-machine { width: 1fr; height: 1; border: none; margin-left: 1; }
    #machine-picker { width: 100%; height: 100%; align: center top; padding: 2 1; }
    #machine-picker-columns { width: auto; max-width: 100%; height: auto; align: center top; }
    .machine-picker-column { width: 26; height: auto; margin: 0 1; }
    .machine-picker-column-title { text-style: bold; content-align: center middle; width: 100%;
        border-bottom: solid $accent; margin-bottom: 1; padding-bottom: 1; }
    .picker-title { text-style: bold; content-align: center middle; width: auto; margin-bottom: 1; }
    .picker-subtitle { color: $text-muted; content-align: center middle; width: auto; margin-bottom: 1; }
    .machine-picker-btn { width: 100%; height: 3; margin-bottom: 1; text-style: bold; }
    .machine-picker-warning { color: $warning; text-style: bold; height: auto;
        content-align: center middle; width: 100%; margin: -1 0 1 0; }
    .advanced-warning { color: $warning; text-style: bold; height: auto; padding: 0 0 1 0; }
    .picker-row { height: 3; }
    .picker-help { color: $text-muted; height: auto; }
    .row-preview { height: 1; background: $panel; padding: 0 1; margin-bottom: 1; color: $text-muted; }
    #layout-custom-rows { height: auto; }
    #layout-extra-rows { height: auto; }
    .custom-row-input { height: 1; margin-bottom: 1; border: none; padding: 0 1;
        background: $panel; border-left: thick $warning; }
    #type-test-text { height: 8; }
    #coverage-chars { height: 6; }
    #coverage-buttons { height: 5; margin-top: 1; }
    #coverage-buttons Button { width: 1fr; height: 5; text-style: bold; }
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
        # Only does anything while a job is actually running - see
        # action_cancel_build/_stream_subprocess.
        ("c", "cancel_build", "Cancel build"),
    ]

    def __init__(self, config_path=None):
        super().__init__()
        self.inputs = {}
        self._last_build_info = None
        # The live generate.py/type_test.py/font_coverage.py subprocess, or
        # None when nothing is running - see _stream_subprocess. Tracked so
        # it can actually be KILLED rather than merely abandoned: Textual's
        # run_worker(exclusive=True) cancels the awaiting coroutine, which
        # left the child process running to completion in the background,
        # burning CPU for output nobody would look at.
        self._build_proc = None
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
        machine = self._peek_machine(self.master_config_path)
        self.config_path = self._running_config_path(self.master_config_path, machine)
        self._ensure_running_config()
        self._migrate_running_config()  # no log_line here - RichLog isn't mounted yet
        self.inputs = {}
        self._load_current()
        self.machine = self.cfg.get("machine", "blickensderfer")
        self.SECTIONS = SECTIONS_BY_MACHINE.get(self.machine, SECTIONS_BY_MACHINE["blickensderfer"])
        self.FIELDS = [field for fields in self.SECTIONS.values() for field in fields]
        self.LAYOUT_PRESETS = LAYOUT_PRESETS_BY_MACHINE.get(self.machine, {})
        # HAS_LAYOUT_TAB gates the Layout tab itself (compose()) - true
        # for any machine with an editable layout.rows, including the 3
        # Selectric machines now (8 rows: 4 lowercase + 4 uppercase, see
        # config/selectric12.yaml's layout.rows comment).
        #
        # HAS_BASELINE_CUTOUT is a SEPARATE flag for the Element tab's
        # per-row baseline_row/cutout_row float widgets
        # (_compose_baseline_cutout_fields/_save_to_yaml/
        # _refresh_widgets_from_cfg) - the cylinder family's per-row
        # calibration values. Selectric has HAS_LAYOUT_TAB but NOT this:
        # its own per-row calibration arrays (row_latitudes/
        # platen_longitude_offsets/baseline_longitude_offsets/
        # minkowski_longitudinal_offsets) are a different shape (4 fixed
        # physical ball rows, not tied to layout.rows' 8 keyboard rows)
        # and aren't wired into tune.py yet - decoupled from
        # HAS_LAYOUT_TAB so enabling one doesn't require faking the
        # other.
        self.HAS_LAYOUT_TAB = "rows" in self.cfg.get("layout", {})
        # LAYOUT_MIN_ROWS/LAYOUT_MAX_ROWS/LAYOUT_ROW_COUNT_VARIES - same
        # "row count can differ between this machine's own presets"
        # concept BASELINE_CUTOUT_KEYS below already handles for
        # baseline_row/cutout_row (currently only Hammond: Normal
        # Universal is 3 rows, "Universal, Math" is 4), generalized for the
        # Layout tab's own row preview/edit widgets so picking Math
        # Universal actually shows/allows editing a real 4th row instead
        # of it being silently invisible until a recompose. Derived
        # purely from LAYOUT_PRESETS - not hardcoded to Hammond - so any
        # future machine whose presets vary in row count gets this for
        # free.
        if self.HAS_LAYOUT_TAB:
            preset_row_counts = [len(rows) for rows in self.LAYOUT_PRESETS.values()]
            current_row_count = len(self.cfg["layout"]["rows"])
            self.LAYOUT_MAX_ROWS = max(preset_row_counts + [current_row_count])
            self.LAYOUT_MIN_ROWS = min(preset_row_counts + [current_row_count]) if preset_row_counts else current_row_count
            self.LAYOUT_ROW_COUNT_VARIES = self.LAYOUT_MIN_ROWS != self.LAYOUT_MAX_ROWS
        else:
            self.LAYOUT_MAX_ROWS = self.LAYOUT_MIN_ROWS = 0
            self.LAYOUT_ROW_COUNT_VARIES = False
        self.HAS_BASELINE_CUTOUT = "baseline_row" in self.cfg.get("layout", {})
        if not self.HAS_BASELINE_CUTOUT:
            self.BASELINE_CUTOUT_KEYS = []
        else:
            # row count varies per machine (3 for Blickensderfer/Postal, 7
            # for Mignon) - see BASELINE_CUTOUT_KEYS' module comment.
            # Hammond's own presets additionally vary in row count from
            # EACH OTHER ("Universal, Math" is 4 rows, everything else is 3)
            # - using just the CURRENT config's row count here would only
            # ever show 3 editable baseline/cutout fields, with no way to
            # reach/edit a 4th row until some other action (switching
            # machine and back, restarting) happened to recompose the
            # form with 4 rows on disk. Using the max across every real
            # preset for this machine (falling back to the current config
            # if there are no presets, or it somehow exceeds all of them)
            # means the 4th row field always exists and is editable, even
            # when the 3-row preset is currently selected (it's just not
            # consulted by TextRing in that case).
            n_rows = max([len(self.cfg["layout"]["baseline_row"])]
                         + [len(rows) for rows in self.LAYOUT_PRESETS.values()])
            self.BASELINE_CUTOUT_KEYS = [f"{arr}_{i}" for arr in ("baseline_row", "cutout_row") for i in range(n_rows)]
        # cosmetics.band_z_offsets/band_heights - one band per GAP between
        # adjacent baselines, so N baselines give N-1 bands. Same inline-
        # list-element mechanism as BASELINE_CUTOUT_KEYS above; empty for
        # any machine with no cosmetics: section.
        if "Cosmetics" not in self.SECTIONS:
            self.BAND_KEYS = []
        else:
            n_bands = max(len(self.cfg["layout"]["baseline_row"]) - 1, 0)
            self.BAND_KEYS = [f"{arr}_{i}" for arr in ("band_z_offsets", "band_heights")
                               for i in range(n_bands)]
        # Flat-indexed layout.rows (Selectric family: has rows, but no
        # placement_map) - each row's length is load-bearing, not just an
        # upper bound, since the character content is consumed by flat
        # keyboard index (lib/spherical_machine.AssembleMinkowski), not
        # per-row placement like the cylinder family's placement_map. See
        # _layout_row_caps()/_save_to_yaml's Modify-glyphs validation.
        self.HAS_FLAT_INDEXED_ROWS = (
            self.HAS_LAYOUT_TAB and "placement_map" not in self.cfg["layout"])

    @staticmethod
    def _peek_machine(config_path):
        """Reads just the `machine:` key without going through the full
        master/running/self.cfg bootstrap - needed to name the running
        copy (see _running_config_path) before that bootstrap has run."""
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("machine", os.path.splitext(os.path.basename(config_path))[0])

    @staticmethod
    def _running_config_path(master_path, machine):
        # One scratch file PER MACHINE, not per master config file - every
        # font-variant config (config/selectric12_oriental.yaml etc.) for a
        # given machine shares the same running copy. Keying this by the
        # master's own filename stem used to spawn a brand-new *.running.yaml
        # per variant (selectric12_oriental.running.yaml, selectric12_pxplus_
        # ibm_mda.running.yaml, ...) every time a different variant was
        # loaded - real disk bloat with no purpose, since Save (not the
        # running copy) is the mechanism for durable per-variant snapshots.
        d = os.path.dirname(master_path)
        return os.path.join(d, f"{machine}.running.yaml")

    _SOURCE_MASTER_RE = re.compile(r'^#\s*source_master:\s*(.+?)\s*$', re.MULTILINE)

    def _write_running_from_master(self):
        """(Re)writes self.config_path from self.master_config_path, tagged
        with a `# source_master: <path>` header line so a later load can
        tell whether the existing running copy still belongs to the CURRENTLY
        loaded master or is left over from a different variant of the same
        machine (see _ensure_running_config) - both share one file now, so
        that distinction has to live somewhere."""
        with open(self.master_config_path) as f:
            master_text = f.read()
        header = f"# source_master: {self.master_config_path}\n"
        with open(self.config_path, "w") as f:
            f.write(header + master_text)

    def _ensure_running_config(self):
        if not os.path.exists(self.config_path):
            self._write_running_from_master()
            return
        with open(self.config_path) as f:
            existing_text = f.read()
        m = self._SOURCE_MASTER_RE.search(existing_text)
        if m is not None and m.group(1) != self.master_config_path:
            # Running copy on disk belongs to a different master (a
            # different font variant of this same machine) - it's scratch
            # state for THAT variant, not this one, so start fresh from the
            # newly loaded master rather than showing unrelated customizations.
            self._write_running_from_master()
        elif m is None:
            # Pre-existing running copy from before source_master tracking
            # existed (every machine's <machine>.running.yaml as of this
            # change) - under the OLD per-master-stem naming this file could
            # only ever have come from the one master whose filename stem
            # equals this machine name, so it's unambiguously already
            # "this" master's copy. Stamp it in place rather than treating
            # a missing header as a mismatch - the whole point is to never
            # discard real accumulated customizations just because they
            # predate this tracking mechanism.
            with open(self.config_path, "w") as f:
                f.write(f"# source_master: {self.master_config_path}\n" + existing_text)

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
        ("Universal, Math" is 4 rows, everything else is 3) - the per-row
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

    @staticmethod
    def _section_tab_id(section):
        """A generic (SECTIONS-driven) tab's pane id. Shared with
        _tab_specs, which needs the same id to point the section-nav list
        at the right pane - deriving it in two places is how the nav and
        the panes would drift."""
        return f"tab-{section.lower().replace(' ', '-').replace('&', 'and')}"

    def _compose_section_tab(self, section):
        fields = self.SECTIONS[section]
        tab_id = self._section_tab_id(section)
        with TabPane(section, id=tab_id):
            with VerticalScroll():
                intro = SECTION_INTROS.get(section)
                if intro:
                    text, css_class = intro
                    yield Static(text, classes=css_class)
                if section == "Font & Alignment":
                    yield from self._compose_font_profile_picker()
                for key, path, typ, label, help_text in fields:
                    current = get_nested(self.cfg, path)
                    with Vertical(classes="field-row"):
                        with Horizontal():
                            yield Static(label, classes="field-label")
                            if typ is bool:
                                sw = Switch(value=bool(current), id=f"field-{key}")
                                self.inputs[key] = sw
                                yield sw
                            elif key in SELECT_FIELD_OPTIONS:
                                options = SELECT_FIELD_OPTIONS[key]
                                allowed = [v for _, v in options]
                                val = str(current) if str(current) in allowed else allowed[0]
                                sel = Select(options, value=val, id=f"field-{key}", allow_blank=False)
                                self.inputs[key] = sel
                                yield sel
                            else:
                                inp = Input(value=str(current), id=f"field-{key}")
                                self.inputs[key] = inp
                                yield inp
                        if key in FONT_PATH_FIELD_KEYS:
                            # Two ways to fill the path field above, on
                            # their own row rather than beside the Input
                            # (the form pane is 58 columns - label plus
                            # two buttons would leave a path field too
                            # narrow to read). "Installed" is the normal
                            # one: pick by font name out of everything
                            # installed on this machine (see
                            # SystemFontPicker). "File" is the original
                            # FileOpen browser, kept because a font
                            # doesn't have to be installed to be usable
                            # here - the pipeline just reads the file.
                            with Horizontal(classes="font-btn-row"):
                                yield Button("Installed", id=f"sysfont-{key}", classes="sysfont-btn")
                                yield Button("File", id=f"browse-{key}", classes="browse-btn")
                            yield Static(_font_display_name(current), id=f"font-name-{key}", classes="field-help")
                        if help_text:
                            yield Static(help_text, classes="field-help")
                if section == "Element":
                    yield from self._compose_baseline_cutout_fields()
                if section == "Cosmetics":
                    yield from self._compose_band_fields()
                if section == "Legend":
                    yield from self._compose_legend_extra()

    def _font_field_paths(self):
        return [list(f[1]) for f in self.SECTIONS["Font & Alignment"]]

    def _config_dir(self):
        return os.path.dirname(os.path.abspath(self.master_config_path))

    def _compose_font_profile_picker(self):
        """Named, machine-independent Font & Alignment profiles - save the
        current typeface setup under a name and recall it later, including
        on a DIFFERENT machine (see lib/font_profiles.py). Sits at the top
        of the tab because it acts on everything below it."""
        names = [n for n, _p in font_profiles.list_profiles(self._config_dir())]
        options = [(n, n) for n in names]
        current = self._current_font_profile()
        with Vertical(classes="field-row"):
            with Horizontal():
                yield Static("Profile", classes="field-label")
                yield Select(options, value=current if current in names else Select.NULL,
                             id="font-profile-select", allow_blank=True,
                             prompt="(none)")
            with Horizontal(classes="font-btn-row"):
                yield Button("Save as profile", id="font-profile-save", classes="sysfont-btn")
            yield Static(self._font_profile_status(current), id="font-profile-status",
                          classes="field-help")

    def _current_font_profile(self):
        """Derived by comparing values, not stored in the config - same
        convention as _current_layout_preset(), so hand-editing a field
        correctly clears the selection instead of leaving a stale name."""
        try:
            return font_profiles.matching_profile(
                self._config_dir(), self.cfg, self._font_field_paths())
        except Exception:
            return None

    @staticmethod
    def _font_profile_status(current):
        if current:
            return f"Active: {current}. Editing any field below clears this."
        return ("No profile active. Save one to reuse this typeface setup, "
                "including on other machines.")

    async def _apply_font_profile(self, name):
        """Applies a saved profile to the loaded machine, after letting the
        user choose which values to take (see ProfileApplyPicker).

        Values reach this machine either directly (it has that config path)
        or through an equivalence - the same knob under this family's own
        name, direction-corrected. See font_profiles.EQUIVALENT_PATHS for
        which pairs those are and how their directions were measured.
        Anything with neither is skipped; anything this machine has that
        the profile doesn't reach keeps its current value."""
        match = [p for n, p in font_profiles.list_profiles(self._config_dir()) if n == name]
        if not match:
            self.log_line(f"[red]profile {name!r} not found[/red]")
            return
        try:
            _, values = font_profiles.load_profile(match[0])
        except Exception as e:
            self.log_line(f"[red]could not read profile {name!r}: {e}[/red]")
            return
        applied, aliased, skipped, unset = font_profiles.apply_to(
            values, self._font_field_paths())
        chosen = await self.push_screen_wait(
            ProfileApplyPicker(name, applied, aliased, skipped, unset))
        if chosen is None:
            self.log_line(f"[yellow]profile {name!r} not applied[/yellow]")
            self._sync_font_profile_select()
            return

        by_path = {".".join(f[1]): f[0] for f in self.SECTIONS["Font & Alignment"]}
        n_direct = n_alias = 0
        for path in chosen:
            if path in applied:
                value, n_direct = applied[path], n_direct + 1
            elif path in aliased:
                value, n_alias = aliased[path][0], n_alias + 1
            else:
                continue
            widget = self.inputs.get(by_path.get(path))
            if widget is None:
                continue
            if isinstance(widget, Switch):
                widget.value = bool(value)
            else:
                widget.value = str(value)
        msg = f"[green]applied profile {name!r}[/green] - {n_direct} value(s) set"
        if n_alias:
            msg += f", {n_alias} via an equivalent name"
        self.log_line(msg)
        if skipped:
            self.log_line(f"[yellow]  no field or equivalent here, ignored:[/yellow] "
                           f"{', '.join(skipped)}")
        if unset:
            self.log_line(f"[yellow]  left unchanged (profile doesn't reach them):[/yellow] "
                           f"{', '.join(unset)}")
        self._refresh_font_profile_status()

    def _sync_font_profile_select(self):
        """Puts the dropdown back in step with what is actually loaded -
        used after a cancelled apply, so the picker doesn't keep showing a
        profile that was never applied."""
        try:
            select = self.query_one("#font-profile-select", Select)
        except NoMatches:
            return
        current = self._current_font_profile()
        names = [n for n, _p in font_profiles.list_profiles(self._config_dir())]
        select.value = current if current in names else Select.NULL

    def _refresh_font_profile_status(self):
        try:
            status = self.query_one("#font-profile-status", Static)
        except NoMatches:
            return
        status.update(self._font_profile_status(self._current_font_profile()))

    async def _save_font_profile(self):
        current = self._current_font_profile() or ""
        name = await self.push_screen_wait(ProfileNamePrompt(current))
        if not name:
            return
        values = self._collect_values()
        if values is None:
            return
        self._save_to_yaml(values)
        self._load_current()
        payload = font_profiles.collect_from_config(self.cfg, self._font_field_paths())
        path = font_profiles.save_profile(self._config_dir(), name, payload,
                                           saved_from=self.machine)
        self.log_line(f"[green]saved profile {name!r}[/green] ({len(payload)} values) -> {path}")
        select = self.query_one("#font-profile-select", Select)
        names = [n for n, _p in font_profiles.list_profiles(self._config_dir())]
        select.set_options([(n, n) for n in names])
        select.value = name if name in names else Select.NULL
        self._refresh_font_profile_status()

    def _compose_band_fields(self):
        """Per-band offset/height widgets for the Banded wheel style -
        bespoke for the same reason _compose_baseline_cutout_fields is
        (inline list elements, not scalar keys). One band per gap between
        adjacent baselines."""
        if not self.BAND_KEYS:
            return
        yield Static(
            "Banded style only. Each band sits at the midpoint between two "
            "baselines, plus its offset below. Check the height fits the clear "
            "wall between those rows - characters have ascenders and descenders.",
            classes="picker-help")
        n_bands = len(self.BAND_KEYS) // 2
        for arr_key, label, default in (("band_z_offsets", "Band offset", 0.0),
                                         ("band_heights", "Band height", 2.0)):
            values = self.cfg.get("cosmetics", {}).get(arr_key, [])
            for i in range(n_bands):
                key = f"{arr_key}_{i}"
                current = values[i] if i < len(values) else default
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static(f"{label} {i} (mm)", classes="field-label")
                        inp = Input(value=str(current), id=f"field-{key}")
                        self.inputs[key] = inp
                        yield inp

    def _compose_legend_extra(self):
        """The Legend tab's own background picker + action button +
        status line, appended after its generic LEGEND_FIELDS_*/
        _compose_section_tab fields - same trailing-content pattern as
        Element's _compose_baseline_cutout_fields() above. Generates a
        standalone SVG (lib/<machine>_legend.py via generate_legend.py),
        not an STL - entirely separate from Preview/Render/the f3d
        window, so this bespoke Select (like Build tab's own dropdowns)
        isn't in self.FIELDS - _collect_values/_save_to_yaml/
        _refresh_widgets_from_cfg handle it explicitly."""
        background_now = str(self.cfg.get("legend", {}).get("background", "transparent"))
        if background_now not in ("transparent", "white"):
            background_now = "transparent"
        with Horizontal(classes="picker-row"):
            yield Static("Background", classes="field-label")
            yield Select([("Transparent", "transparent"), ("White", "white")],
                         value=background_now, id="legend-background", allow_blank=False)
        with Horizontal(id="legend-buttons"):
            yield Button("GENERATE LEGEND SVG", id="btn-generate-legend", variant="success")
            yield Button("SAVE LEGEND SVG", id="btn-save-legend", variant="warning")
        yield Static("", id="legend-status", classes="field-help")

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
        # No layout.baseline_row/cutout_row concept at all for machines
        # without it (self.HAS_BASELINE_CUTOUT False, self.BASELINE_
        # CUTOUT_KEYS empty - see that flag's own comment; this includes
        # the Selectric family, which has HAS_LAYOUT_TAB but its own
        # differently-shaped per-row calibration arrays instead).
        if not self.HAS_BASELINE_CUTOUT:
            return
        yield Static(
            "Per-row baseline/platen-cutout (mm). See the Calibration tab "
            "to find these empirically.",
            classes="picker-help")
        # n_rows is the max across every real preset for this machine
        # (see BASELINE_CUTOUT_KEYS' own comment) - may exceed the
        # CURRENTLY selected preset/config's own row count (e.g. Hammond's
        # 3-row Normal Universal vs. its 4-row "Universal, Math"), so every
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

    def _layout_row_caps(self, n_rows=None):
        """Max character length for each editable Layout-tab row Input,
        one entry per row up to n_rows (defaults to self.cfg["layout"]
        ["rows"]'s own current length, matching every call site before
        this parameter existed). The cylinder family shares ONE cap
        across every row (placement_map's column count is uniform per
        row - see this method's caller for why placement_map itself is
        never exposed as a widget) - trivially extends to any n_rows.
        Selectric's rows are NOT uniform width (v2's real keyboard-row
        shape, e.g. Selectric I/II's 12/11/11/10 split) and unlike the
        cylinder family, every row's length is load-bearing there
        (self.HAS_FLAT_INDEXED_ROWS - CASES88_LOWER/UPPER are consumed by
        flat keyboard index, see spherical_machine.AssembleMinkowski), so
        each row's cap is its OWN current on-disk length - long enough
        for every real preset (they all share the same per-row shape -
        see e.g. lib/layouts/selectric_composer_layout.py's own comment) but
        never growable from the widget alone; n_rows beyond what's
        currently on disk pads with 0 (dead code in practice - no
        flat-indexed machine's own presets vary in row count, see
        LAYOUT_ROW_COUNT_VARIES)."""
        if n_rows is None:
            n_rows = len(self.cfg["layout"]["rows"])
        if "placement_map" in self.cfg["layout"]:
            cap = len(self.cfg["layout"]["placement_map"])
            return [cap] * n_rows
        caps = [len(row) for row in self.cfg["layout"]["rows"]]
        return (caps + [0] * n_rows)[:n_rows]

    def _compose_layout_tab(self):
        # named-layout picker only - latitude_columns must stay in sync
        # with placement_map/the physical layout, so it's not exposed
        # here (edit it directly in the YAML if you really mean to)
        n_rows = self.LAYOUT_MAX_ROWS
        row_caps = self._layout_row_caps(n_rows)
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

                # Read-only preview widgets always go up to LAYOUT_MAX_ROWS
                # (not just the CURRENTLY selected preset's own row count)
                # so a longer preset (Hammond's 4-row "Universal, Math" vs.
                # 3-row Normal Universal) has a real widget to update into
                # when picked - see _update_row_widget's own docstring for
                # what silently breaks without this. A row beyond what the
                # active preset actually has just previews blank.
                yield Static("Rows (read-only preview of the preset above):", classes="field-label")
                display_rows = self._display_rows_for_preset()
                for i in range(n_rows):
                    content = display_rows[i] if i < len(display_rows) else ""
                    static = Static(content, id=f"layout-original-row-{i}", classes="row-preview")
                    yield static

                # This machine's own presets vary in row count (currently
                # only Hammond: Normal Universal 3 rows, "Universal, Math" 4)
                # - row count is real DATA (lib/hammond.py's configure()
                # derives Is_Math from len(rows)==4, driving Shuttle_Height/
                # the resin-support array shape), not a Modify-glyphs
                # concept - deliberately its own independent control, ABOVE
                # and separate from Modify glyphs below, not nested under
                # it or gated by it: it stays in sync with the PRESET
                # dropdown above (on_select_changed - matches whichever
                # preset is selected, same live-seed convention as
                # baseline_row/cutout_row), never with Modify glyphs'
                # switch itself turning on/off. When hand-editing via
                # Modify glyphs, this is the explicit, unambiguous
                # declaration of how many rows to actually write -
                # inferring it from whether the extra Input happens to be
                # non-empty would be fragile (an intentionally-blank row
                # and "not decided yet" look identical) - _save_to_yaml
                # reads it directly.
                use_extra_rows_now = len(self.cfg["layout"]["rows"]) >= n_rows
                if self.LAYOUT_ROW_COUNT_VARIES:
                    with Horizontal(classes="picker-row"):
                        yield Static(f"Use {n_rows}-row layout", classes="field-label")
                        yield Switch(value=use_extra_rows_now, id="layout-use-extra-rows")
                    yield Static(
                        f"Independent of Modify glyphs below - just declares row count. "
                        f"On: {n_rows} rows (e.g. a Math-style layout). Off: "
                        f"{self.LAYOUT_MIN_ROWS} rows, this machine's normal shape. Only "
                        "matters for what actually gets SAVED while hand-editing; follows "
                        "the preset dropdown above otherwise.",
                        classes="picker-help")

                with Horizontal(classes="picker-row"):
                    yield Static("Modify glyphs", classes="field-label")
                    modify_now = bool(self.cfg["layout"]["modify_glyphs"])
                    sw = Switch(value=modify_now, id="layout-modify-glyphs")
                    yield sw
                    yield Button("Reset to selected layout", id="btn-reset-layout-rows")
                if self.HAS_FLAT_INDEXED_ROWS:
                    rows_help = (
                        f"Unlocks {len(display_rows)} hand-editable rows, each capped at "
                        "its own current length (shown per row above) - this layout's "
                        "hemisphere map is keyed by flat keyboard index, so shortening a "
                        "row would silently shift every later character's position. "
                        "While on, this edited copy (not the preset above) is what gets "
                        "saved."
                    )
                else:
                    rows_help = (
                        f"Unlocks {self.LAYOUT_MIN_ROWS} hand-editable rows, max {row_caps[0]} "
                        "characters each. Shorter rows just leave some positions unstruck. "
                        "While on, this edited copy (not the preset above) is what gets saved."
                    )
                yield Static(rows_help, classes="picker-help")

                custom_rows_container = Vertical(id="layout-custom-rows")
                custom_rows_container.display = modify_now
                with custom_rows_container:
                    current_rows = self.cfg["layout"]["rows"]
                    for i in range(self.LAYOUT_MIN_ROWS):
                        content = current_rows[i] if i < len(current_rows) else ""
                        inp = Input(value=content, id=f"layout-custom-row-{i}",
                                    max_length=row_caps[i], classes="custom-row-input")
                        yield inp
                    if self.LAYOUT_ROW_COUNT_VARIES:
                        extra_rows_container = Vertical(id="layout-extra-rows")
                        extra_rows_container.display = use_extra_rows_now
                        with extra_rows_container:
                            for i in range(self.LAYOUT_MIN_ROWS, n_rows):
                                content = current_rows[i] if i < len(current_rows) else ""
                                inp = Input(value=content, id=f"layout-custom-row-{i}",
                                            max_length=row_caps[i], classes="custom-row-input")
                                yield inp

    def _compose_build_tab(self):
        has_gauge = "Gauge" in self.SECTIONS
        has_calibration = "Calibration" in self.SECTIONS
        is_hammond = self.machine == "hammond"
        is_hammond_split = self.machine == "hammond_split"
        is_mignon = self.machine == "mignon"
        hammond_parts = ("none",) if is_hammond else ()
        hammond_split_normal_target = ("normal",) if is_hammond_split else ()
        valid_targets = (("element",) + (("calibration",) if has_calibration else ())
                          + (("gauge",) if has_gauge else ())
                          + hammond_parts + hammond_split_normal_target)
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
                        if has_calibration:
                            options.append(("Calibration Element", "calibration"))
                        if is_hammond_split:
                            options.append(("Normal (flat, no resin)", "normal"))
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
                    calibration_help = (
                        " Calibration Element: strikes the same test "
                        "character everywhere, sweeping baseline or cutout per column "
                        "(see the Calibration tab) to find layout.baseline_row/cutout_row."
                    ) if has_calibration else ""
                    # is_hammond_split only - a real second v2 render target
                    # (Render_Mode==0 "Normal"/v1 GenStyle 0/4/5), not this
                    # machine's own version of Shaft Gauge/Calibration -
                    # always resin-free regardless of the checkbox above,
                    # since the real source never calls a resin-rod module
                    # for it (see hammond_split.Assemble()'s own docstring).
                    normal_help = (
                        " Normal: the flat, un-rotated layout (v2 Render_Mode==0, v1 "
                        "GenStyle 0/4/5 \"Normal\"/NormalL/NormalR) - never has resin "
                        "supports regardless of this checkbox."
                    ) if is_hammond_split else ""
                    resin_unavailable = RESIN_SUPPORT_UNAVAILABLE_NOTE.get(self.machine, "")
                    yield Static(
                        "Element: the real element. Turn on Resin supports to add "
                        "rods/breakaway ring (see the Resin tab for those settings)."
                        f"{gauge_help}{calibration_help}"
                        f"{normal_help}{resin_unavailable}",
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

                if is_mignon:
                    orientation_now = str(self.cfg.get("resin", {}).get("orientation", "upside_down"))
                    if orientation_now not in ("upside_down", "right_side_up"):
                        orientation_now = "upside_down"
                    with Horizontal(classes="picker-row"):
                        yield Static("Print orientation", classes="field-label")
                        yield Select([("Upside down", "upside_down"), ("Right side up", "right_side_up")],
                                     value=orientation_now, id="build-orientation", allow_blank=False)
                    yield Static(
                        '"Upside down" (default) is the original v1/v2 orientation - the '
                        "label end sits at the build plate, supports attach there. "
                        '"Right side up" skips that flip: the shaft/keyway end sits at the '
                        "build plate instead, with its own support layout that keeps clear "
                        "of the AlignmentPin notch. Only matters while Resin supports is on.",
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
                    "(ignored for Shaft Gauge/Calibration Element/Normal). Session-only "
                    "debug settings: neither of these is saved to the config.",
                    classes="picker-help")

    def _charset_for_coverage_select_value(self, value):
        """"__current__" -> this config's active layout.rows, a preset
        name -> that preset's rows (LAYOUT_PRESETS_BY_MACHINE, same dict
        the Layout tab's own picker uses - lets you check e.g. Hammond's
        "Universal, Math" without actually switching the loaded config to
        it), anything else (including "__custom__") -> leave whatever's
        already typed in #coverage-chars alone."""
        if value == "__current__":
            return "".join(self.cfg.get("layout", {}).get("rows", []))
        if value in self.LAYOUT_PRESETS:
            return "".join(self.LAYOUT_PRESETS[value])
        return None

    def _compose_font_coverage_tab(self):
        with TabPane("Font Coverage", id="tab-font-coverage"):
            with VerticalScroll():
                yield Static(
                    "Scans a font directory for glyph coverage against a character "
                    "set - which fonts have every glyph, and exactly which "
                    "characters are missing from the close calls. Standalone from "
                    "the rest of this form - doesn't read or write the loaded "
                    "config.",
                    classes="picker-help")

                options = []
                if self.HAS_LAYOUT_TAB:
                    options.append(("Current config's active layout", "__current__"))
                for name in self.LAYOUT_PRESETS:
                    options.append((name, name))
                options.append(("Custom / hand-edited", "__custom__"))
                default_value = options[0][1]
                with Horizontal(classes="picker-row"):
                    yield Static("Character set", classes="field-label")
                    yield Select(options, value=default_value, id="coverage-preset-select",
                                 allow_blank=False)

                initial_chars = self._charset_for_coverage_select_value(default_value) or ""
                yield TextArea(initial_chars, id="coverage-chars")
                yield Static(
                    "Auto-filled from the dropdown above (one-time seed, not "
                    "re-applied on scan) - hand-edit freely before scanning. "
                    "Duplicate characters are ignored.",
                    classes="field-help")

                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("Font directory", classes="field-label")
                        yield Input(value=os.path.expanduser("~/fonts"), id="coverage-font-dir")
                        yield Button("Browse", id="browse-coverage-font-dir", classes="browse-btn")
                    yield Static("Searched recursively for .ttf/.otf/.ttc/.otc files.",
                                 classes="field-help")

                with Horizontal(classes="picker-row"):
                    yield Static("Deep check", classes="field-label")
                    yield Switch(value=False, id="coverage-deep")
                yield Static(
                    "Also runs each glyph through the real contour/triangulate "
                    "pipeline (the same two calls build_glyph/TextRing make) to "
                    "catch the self-intersection/all-off-curve/debris-contour "
                    "issues FONT_AUDIT.md found, not just cmap presence - much "
                    "slower over a large library.",
                    classes="field-help")

                with Horizontal(id="coverage-buttons"):
                    yield Button("SCAN FONTS", id="btn-coverage-scan", variant="success")
                    yield Button("SAVE REPORT", id="btn-coverage-save-report", variant="warning")
                yield Static("", id="coverage-status", classes="field-help")

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
                if self.machine == "selectric_composer":
                    yield Static(
                        "Selectric Composer used real proportional spacing, not fixed-pitch "
                        "CPI - each character has its own width in Units (Composer_Pitch_List), "
                        "converted to mm via Units/inch below (72/84/96 - v2's Red/Yellow/Blue "
                        "wheel). LPI still sets line spacing.",
                        classes="picker-help")
                    with Vertical(classes="field-row"):
                        with Horizontal():
                            yield Static("Units/inch", classes="field-label")
                            yield Input(value=str(self.cfg["type_test"]["units_per_inch"]), id="type-test-units-per-inch")
                        yield Static("v2's Units_Per_Inch - 72 (Red), 84 (Yellow), or 96 (Blue).", classes="field-help")
                else:
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
        None in both cases. One button per MACHINES entry, laid out as
        3 side-by-side columns (one per MACHINE_CATEGORIES entry -
        Cylinders/Shuttles/Spheres) instead of one flat 10-button wall of
        text, and the whole thing sits in a VerticalScroll so a small
        terminal window can still reach every machine instead of just
        clipping the overflow. Picking one loads that machine's config
        and recomposes into the tuner form (see _select_machine)."""
        with VerticalScroll(id="machine-picker"):
            yield Static("Type Elements Tuner", classes="picker-title")
            yield Static("Choose a machine to work on:", classes="picker-subtitle")
            with Horizontal(id="machine-picker-columns"):
                for category, keys in MACHINE_CATEGORIES:
                    with Vertical(classes="machine-picker-column"):
                        yield Static(category, classes="machine-picker-column-title")
                        for key in keys:
                            label, _path = MACHINES[key]
                            btn = Button(label, id=f"pick-machine-{key}", classes="machine-picker-btn")
                            warning = MACHINE_PICKER_WARNINGS.get(key)
                            if warning is not None:
                                short_warning, tooltip_text = warning
                                btn.tooltip = tooltip_text
                                yield btn
                                yield Static(short_warning, classes="machine-picker-warning")
                            else:
                                yield btn

    def _tab_specs(self):
        """(pane id, nav label, compose callable) for every tab THIS
        machine gets, in display order - the one source both the
        section-nav list and the TabbedContent panes are built from, so a
        machine-conditional tab can't appear in one and not the other.

        Which tabs a machine gets is genuinely conditional (Bennett has
        Label where others have Logo, the Selectrics have no Layout or
        Calibration, only the Type Slug family has Character/Ticks), which
        is why this is a method returning a per-machine list rather than a
        module-level table."""
        def section(name):
            return (self._section_tab_id(name), name,
                    lambda name=name: self._compose_section_tab(name))

        specs = [section("Font & Alignment")]
        # "Character" - Type Slug family only (which character(s) get
        # struck - see CHARACTER_FIELDS_WING_SLUG/_BOX_SLUG).
        if "Character" in self.SECTIONS:
            specs.append(section("Character"))
        specs.append(("tab-type-test", "Type Test", self._compose_type_test_tab))
        specs.append(section("Resin"))
        if "Gauge" in self.SECTIONS:
            specs.append(section("Gauge"))
        # "Ticks" - Gauge Slug only (its tick-mark measuring ladder - see
        # TICKS_FIELDS_GAUGE_SLUG's own comment for why this is a separate
        # section from "Gauge" above).
        if "Ticks" in self.SECTIONS:
            specs.append(section("Ticks"))
        # no "Calibration" key for the Selectric family - no
        # CalibrationElement/CalibrationAdditive implemented yet (see
        # SECTIONS_BY_MACHINE's Selectric comment).
        if "Calibration" in self.SECTIONS:
            specs.append(section("Calibration"))
        specs.append(("tab-build", "Build", self._compose_build_tab))
        specs.append(("tab-font-coverage", "Font Coverage", self._compose_font_coverage_tab))
        # no editable keyboard-layout concept for the Selectric family
        # (see self.HAS_LAYOUT_TAB's own comment).
        if self.HAS_LAYOUT_TAB:
            specs.append(("tab-layout", "Layout", self._compose_layout_tab))
        specs.append(section("Quality"))
        # no "Logo" key for Bennett - its one engraved-text feature is the
        # "Label" tab instead (see LABEL_FIELDS_BENNETT).
        if "Logo" in self.SECTIONS:
            specs.append(section("Logo"))
        if "Label" in self.SECTIONS:
            specs.append(section("Label"))
        specs.append(section("Element"))
        # Decorative outer-wall treatment - Blickensderfer/Postal only, the
        # two machines whose bodies cylinder_machine.Cylinder() actually
        # builds (see its "Wheel cosmetics" section).
        if "Cosmetics" in self.SECTIONS:
            specs.append(section("Cosmetics"))
        if "Rib" in self.SECTIONS:
            specs.append(section("Rib"))
        # only machines with an actual v1 index/legend card ported (see
        # lib/mignon_legend.py/lib/hammond_legend.py) get this tab - not
        # every machine has one.
        if "Legend" in self.SECTIONS:
            specs.append(section("Legend"))
        return specs

    def _compose_tuner_ui(self):
        specs = self._tab_specs()
        with Vertical(id="form"):
            yield Static(self._status_text(), id="status")
            with Horizontal(id="status-row"):
                yield Button("Browse", id="browse-config", classes="browse-btn")
                yield Button("Reset to Defaults", id="btn-reset-defaults", variant="error")
                yield Button("Change Machine", id="btn-change-machine")
            # Sections are navigated by the vertical list on the left, not
            # by TabbedContent's own horizontal tab bar (hidden in CSS -
            # see "#tabs ContentTabs"). Reported as "the tab selection is
            # cumbersome to use. you dont see the other options": a
            # machine has up to 14 sections, and the horizontal bar showed
            # about five of them in the form pane's width with no
            # indication the rest existed. A vertical list shows every
            # section at once, and costs width (taken from the log pane)
            # rather than the height a wrapped/two-row tab bar would.
            # TabbedContent itself is kept - it still owns which pane is
            # visible, so every _compose_*_tab method and every tab id is
            # unchanged.
            with Horizontal(id="form-body"):
                yield OptionList(*[Option(title, id=tab_id) for tab_id, title, _fn in specs],
                                 id="section-nav")
                with TabbedContent(id="tabs"):
                    for _tab_id, _title, compose_fn in specs:
                        yield from compose_fn()

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
                # Sits with the progress readout rather than in the main
                # button row: it belongs to the job in flight, and the
                # three primary buttons are equal-width 1fr, so a fourth
                # would narrow all of them for something only meaningful
                # part of the time. Hidden entirely unless a job is
                # running (see _set_build_running).
                cancel = Button("CANCEL [c]", id="btn-cancel-build", variant="error")
                cancel.display = False
                yield cancel

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
        if "Legend" in self.SECTIONS:
            # legend.background - bespoke Legend-tab Select (see
            # _compose_legend_extra), same treatment as Hammond's
            # orientation/horizontal_method above.
            values["background"] = self.query_one("#legend-background", Select).value
        if self.machine == "hammond":
            # orientation/horizontal_method - moved off the Resin tab onto
            # the Build tab (see _compose_build_tab) - not in self.FIELDS
            # for the same reason as groove above.
            values["orientation"] = self.query_one("#build-orientation", Select).value
            values["horizontal_method"] = self.query_one("#build-horizontal-method", Select).value
        if self.machine == "mignon":
            # orientation - same bespoke Build-tab treatment as Hammond's
            # above (see _compose_build_tab's is_mignon branch); Mignon has
            # no horizontal_method equivalent.
            values["orientation"] = self.query_one("#build-orientation", Select).value
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
        lpi_raw = self.query_one("#type-test-lpi", Input).value.strip()
        try:
            values["lpi"] = float(lpi_raw)
        except ValueError:
            self.log_line(f"[red]bad Type Test LPI value: {lpi_raw!r} (expected a number)[/red]")
            return None
        if self.machine == "selectric_composer":
            units_raw = self.query_one("#type-test-units-per-inch", Input).value.strip()
            try:
                values["units_per_inch"] = float(units_raw)
            except ValueError:
                self.log_line(f"[red]bad Units/inch value: {units_raw!r} (expected a number)[/red]")
                return None
        else:
            # CPI doesn't apply to Composer - real proportional spacing
            # (Units/inch above) replaces it entirely, so its widget isn't
            # composed for that machine (see _compose_type_test_tab).
            cpi_raw = self.query_one("#type-test-cpi", Input).value.strip()
            try:
                values["cpi"] = float(cpi_raw)
            except ValueError:
                self.log_line(f"[red]bad Type Test CPI value: {cpi_raw!r} (expected a number)[/red]")
                return None
        # layout.baseline_row/cutout_row per-row fields (Element tab) -
        # bespoke like everything above, since they're list elements, not
        # standalone scalar YAML keys - see BASELINE_CUTOUT_KEYS/
        # patch_yaml_list_item.
        for key in self.BASELINE_CUTOUT_KEYS + self.BAND_KEYS:
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
            if key in self.BASELINE_CUTOUT_KEYS or key in self.BAND_KEYS:
                continue
            text = patch_yaml_value(text, key, value)
        for key in self.BAND_KEYS:
            arr_key, index_str = key.rsplit("_", 1)
            text = patch_yaml_list_item(text, arr_key, int(index_str), values[key])
        for key in self.BASELINE_CUTOUT_KEYS:
            arr_key, index_str = key.rsplit("_", 1)
            text = patch_yaml_list_item(text, arr_key, int(index_str), values[key])
        if self.HAS_LAYOUT_TAB:
            modify_glyphs = self.query_one("#layout-modify-glyphs", Switch).value
            text = patch_yaml_value(text, "modify_glyphs", modify_glyphs)
            if modify_glyphs:
                # the hand-edited copy is authoritative over the preset
                # dropdown while unlocked - "fix" (defensively re-clamp) each
                # row to its own cap in case anything bypassed the Input's
                # own max_length (e.g. a paste) - see _layout_row_caps().
                #
                # How many rows to actually WRITE: for a machine whose own
                # presets vary in row count (LAYOUT_ROW_COUNT_VARIES -
                # currently only Hammond), read the explicit "Use N-row
                # layout" switch rather than inferring it from the
                # previous on-disk row count - row count is real data here
                # (lib/hammond.py's Is_Math derives from len(rows)==4), so
                # it needs an unambiguous source of truth, not a guess from
                # whether the last extra Input happens to be non-empty.
                # Every other machine keeps the old behavior (row count
                # never varies, so the on-disk count is always right).
                if self.LAYOUT_ROW_COUNT_VARIES:
                    n_rows = (self.LAYOUT_MAX_ROWS
                              if self.query_one("#layout-use-extra-rows", Switch).value
                              else self.LAYOUT_MIN_ROWS)
                else:
                    n_rows = len(self.cfg["layout"]["rows"])
                row_caps = self._layout_row_caps(n_rows)
                custom_rows = [self.query_one(f"#layout-custom-row-{i}", Input).value[:row_caps[i]] for i in range(n_rows)]
                if self.HAS_FLAT_INDEXED_ROWS and any(len(row) != cap for row, cap in zip(custom_rows, row_caps)):
                    # Unlike the cylinder family (a short row just leaves
                    # some positions unstruck - see the picker-help text
                    # above), a SHORT row here would shift every later
                    # character in the same case onto the wrong physical
                    # ball position (flat keyboard-index lookup, not
                    # per-row placement - see _layout_row_caps()'s own
                    # comment). Refuse just this edit rather than write
                    # data that would silently corrupt the layout; every
                    # other field on the form still saves normally.
                    self.log_line(
                        "[red]layout row edit NOT saved: each row must stay exactly "
                        f"{row_caps} characters long (got {[len(r) for r in custom_rows]}) - "
                        "shortening a row would silently shift every later character's "
                        "position on this machine's fixed hemisphere map[/red]")
                else:
                    text = patch_yaml_rows(text, custom_rows)
            else:
                layout_select = self.query_one("#layout-select", Select)
                if layout_select.value is not Select.NULL:
                    text = patch_yaml_rows(text, self.LAYOUT_PRESETS[layout_select.value])
                    hemisphere_map = LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE.get(
                        self.machine, {}).get(layout_select.value)
                    if hemisphere_map is not None:
                        text = patch_yaml_value(text, "hemisphere_map", hemisphere_map)
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

    def action_generate_legend(self):
        self.run_worker(self._run_generate_legend(), exclusive=True)

    async def _run_generate_legend(self):
        """Legend tab's "Generate Legend SVG" button - saves the whole
        form first (same as Preview/Render, so this tab's own edits
        aren't lost/left stale on disk), then shells out to generate_
        legend.py the same way _run_build shells out to generate.py.
        Output is a standalone .svg (lib/<machine>_legend.py, see its
        module docstring) - no f3d/mesh involvement at all, so this
        reuses _stream_subprocess's shared progress/elapsed widgets and
        log but overrides its default f3d-flavored success message."""
        values = self._collect_values()
        if values is None:
            return
        self._save_to_yaml(values)
        self.log_line("[bold]--- Generate Legend SVG ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "generate_legend.py"), self.config_path]
        status = self.query_one("#legend-status", Static)
        status.update("generating...")
        returncode = await self._stream_subprocess(cmd, success_message="see the printed path above")
        status.update("done - see log above" if returncode == 0 else f"failed (exit {returncode}) - see log above")

    async def action_save_legend(self):
        """Legend tab's "SAVE LEGEND SVG" button - same durable-snapshot
        pattern as the main Save button (action_save()) above, just for
        generate_legend.py's own default output path (<stem>_legend.svg
        inside output.directory - see generate_legend.py's main()) instead
        of the STL. Requires Generate Legend SVG to have been run first,
        same as Save requires Preview/Render first."""
        stem = os.path.splitext(os.path.basename(self.cfg["output"]["stl_name"]))[0]
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], f"{stem}_legend.svg")
        if not os.path.exists(out_path):
            self.log_line("[yellow]nothing to save yet - Generate Legend SVG first[/yellow]")
            return
        save_dir = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], "saved")
        os.makedirs(save_dir, exist_ok=True)
        base = f"{self.machine}_legend_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        suggested = f"{base}.svg"
        n = 2
        while os.path.exists(os.path.join(save_dir, suggested)):
            suggested = f"{base}_{n}.svg"
            n += 1
        result = await self.push_screen_wait(
            FileSave(save_dir, title="Save legend SVG as", default_file=suggested, filters=SVG_FILE_FILTERS))
        if result is None:
            self.log_line("[yellow]save cancelled[/yellow]")
            return
        svg_path = str(result)
        if not svg_path.lower().endswith(".svg"):
            svg_path += ".svg"
        meta_path = svg_path[:-4] + ".yaml"
        os.makedirs(os.path.dirname(svg_path), exist_ok=True)
        shutil.copy2(out_path, svg_path)
        header = (
            f"# Saved by tune.py's Save Legend SVG button at {datetime.now().isoformat(timespec='seconds')}\n"
            f"# master_config: {os.path.relpath(self.master_config_path, REPO_ROOT)}\n"
            f"# running_config: {os.path.relpath(self.config_path, REPO_ROOT)}\n"
            "# This is a full config snapshot, not just metadata - Browse to\n"
            "# it directly to use it as a master config.\n"
        )
        with open(meta_path, "w") as f:
            f.write(header)
            yaml.dump(self.cfg, f, sort_keys=False, allow_unicode=True)
        self.log_line(f"[green]saved[/green] {svg_path} (+ {os.path.basename(meta_path)})")

    async def _browse_coverage_font_dir(self):
        current = os.path.expanduser(self.query_one("#coverage-font-dir", Input).value)
        start_dir = current if os.path.isdir(current) else os.path.expanduser("~/fonts")
        result = await self.push_screen_wait(SelectDirectory(start_dir))
        if result is not None:
            self.query_one("#coverage-font-dir", Input).value = str(result)

    async def _run_font_coverage_scan(self):
        """Font Coverage tab's "SCAN FONTS" button - shells out to font_
        coverage.py exactly like _run_build/_run_generate_legend shell out
        to generate.py/generate_legend.py, reusing the same log/progress/
        elapsed widgets (font_coverage.py's own "[i/total] scanned" lines
        already match _PROGRESS_RE, no extra wiring needed). Unlike those
        two, this tab never touches self.cfg or self.config_path - it's
        standalone, so no _save_to_yaml call first."""
        chars = self.query_one("#coverage-chars", TextArea).text.replace("\n", "").replace("\r", "")
        if not chars:
            self.log_line("[yellow]character set is empty - pick a layout or type some characters[/yellow]")
            return
        font_dir = os.path.expanduser(self.query_one("#coverage-font-dir", Input).value.strip())
        if not font_dir or not os.path.isdir(font_dir):
            self.log_line(f"[red]not a directory: {font_dir!r}[/red]")
            return
        os.makedirs(os.path.dirname(FONT_COVERAGE_REPORT_PATH), exist_ok=True)
        self.log_line("[bold]--- Font Coverage Scan ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "font_coverage.py"),
               "--chars=" + chars, "--font-dir", font_dir, "--out", FONT_COVERAGE_REPORT_PATH]
        if self.query_one("#coverage-deep", Switch).value:
            cmd.append("--deep")
        status = self.query_one("#coverage-status", Static)
        status.update("scanning...")
        returncode = await self._stream_subprocess(
            cmd, success_message=f"report written to {FONT_COVERAGE_REPORT_PATH}")
        status.update("done - see log above, then Save Report to keep a copy" if returncode == 0
                       else f"failed (exit {returncode}) - see log above")

    async def _save_font_coverage_report(self):
        """Same durable-snapshot pattern as action_save/action_save_legend
        above, for font_coverage.py's scratch report instead of the STL/
        legend SVG. Requires Scan Fonts to have been run first."""
        if not os.path.exists(FONT_COVERAGE_REPORT_PATH):
            self.log_line("[yellow]nothing to save yet - Scan Fonts first[/yellow]")
            return
        save_dir = os.path.join(REPO_ROOT, "output", "saved")
        os.makedirs(save_dir, exist_ok=True)
        suggested = f"font_coverage_{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        result = await self.push_screen_wait(
            FileSave(save_dir, title="Save font coverage report as", default_file=suggested,
                     filters=MD_FILE_FILTERS))
        if result is None:
            self.log_line("[yellow]save cancelled[/yellow]")
            return
        md_path = str(result)
        if not md_path.lower().endswith(".md"):
            md_path += ".md"
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        shutil.copy2(FONT_COVERAGE_REPORT_PATH, md_path)
        self.log_line(f"[green]saved[/green] {md_path}")

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
        if self.HAS_LAYOUT_TAB:
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
            has_calibration = "Calibration" in self.SECTIONS
            valid_targets = (("element",) + (("calibration",) if has_calibration else ())
                              + (("gauge",) if "Gauge" in self.SECTIONS else ())
                              + (("normal",) if self.machine == "hammond_split" else ()))
            if target_now not in valid_targets:
                # "resin" was a valid target value before the Build tab's
                # dropdown was split into target + a separate Resin supports
                # checkbox - a running copy saved before that change could
                # still have it on disk; map it back to plain "element" (the
                # checkbox itself carries whether resin support is on now).
                # Also catches "gauge" for a machine with no Gauge tab, and
                # "shuttle_minus_rib"/"shuttle_plus_rib"/"rib_only" from before
                # those 3 FDM targets were folded into None + the Rib checkbox.
                target_now = "element"
            self.query_one("#build-select", Select).value = target_now
        self.query_one("#build-resin-support", Switch).value = bool(self.cfg["build"]["resin_support"])
        if "Legend" in self.SECTIONS:
            background_now = str(self.cfg.get("legend", {}).get("background", "transparent"))
            self.query_one("#legend-background", Select).value = (
                background_now if background_now in ("transparent", "white") else "transparent")
        if self.machine == "hammond":
            orientation_now = str(self.cfg.get("resin", {}).get("orientation", "vertical"))
            self.query_one("#build-orientation", Select).value = (
                orientation_now if orientation_now in ("vertical", "horizontal") else "vertical")
            hm_now = str(self.cfg.get("resin", {}).get("horizontal_method", "resin_rod"))
            self.query_one("#build-horizontal-method", Select).value = (
                hm_now if hm_now in ("cut_groove", "resin_rod") else "resin_rod")
        if self.machine == "mignon":
            orientation_now = str(self.cfg.get("resin", {}).get("orientation", "upside_down"))
            self.query_one("#build-orientation", Select).value = (
                orientation_now if orientation_now in ("upside_down", "right_side_up") else "upside_down")
        if self.machine == "hammond_split":
            b = self.cfg.get("build", {})
            self.query_one("#build-render-left", Switch).value = bool(b.get("render_left", True))
            self.query_one("#build-render-right", Switch).value = bool(b.get("render_right", True))
        self.query_one("#type-test-lpi", Input).value = str(self.cfg["type_test"]["lpi"])
        if self.machine == "selectric_composer":
            self.query_one("#type-test-units-per-inch", Input).value = str(self.cfg["type_test"]["units_per_inch"])
        else:
            self.query_one("#type-test-cpi", Input).value = str(self.cfg["type_test"]["cpi"])
        self.query_one("#type-test-text", TextArea).text = self.cfg["type_test"]["text"]
        if self.HAS_LAYOUT_TAB:
            display_rows = self._display_rows_for_preset()
            for i in range(self.LAYOUT_MAX_ROWS):
                self._update_row_widget("layout-original-row", i, display_rows[i] if i < len(display_rows) else "")
            modify_glyphs = bool(self.cfg["layout"]["modify_glyphs"])
            self.query_one("#layout-modify-glyphs", Switch).value = modify_glyphs
            self.query_one("#layout-custom-rows").display = modify_glyphs
            current_rows = self.cfg["layout"]["rows"]
            for i in range(self.LAYOUT_MAX_ROWS):
                self._update_row_widget("layout-custom-row", i, current_rows[i] if i < len(current_rows) else "")
            if self.LAYOUT_ROW_COUNT_VARIES:
                use_extra_rows_now = len(current_rows) >= self.LAYOUT_MAX_ROWS
                try:
                    self.query_one("#layout-use-extra-rows", Switch).value = use_extra_rows_now
                    self.query_one("#layout-extra-rows").display = use_extra_rows_now
                except NoMatches:
                    pass
        if self.HAS_BASELINE_CUTOUT:
            for arr_key in ("baseline_row", "cutout_row"):
                arr = self.cfg["layout"][arr_key]
                for i in range(len(arr)):
                    # self.inputs (a plain dict, not query_one) - same row-
                    # count-mismatch reasoning as _update_row_widget above,
                    # but a dict lookup raises KeyError, not NoMatches.
                    w = self.inputs.get(f"{arr_key}_{i}")
                    if w is not None:
                        w.value = str(arr[i])
        if self.BAND_KEYS:
            for arr_key in ("band_z_offsets", "band_heights"):
                arr = self.cfg.get("cosmetics", {}).get(arr_key, [])
                for i in range(len(arr)):
                    w = self.inputs.get(f"{arr_key}_{i}")
                    if w is not None:
                        w.value = str(arr[i])

    def action_reload(self):
        self._load_current()
        self._refresh_widgets_from_cfg()
        self.log_line("[cyan]reloaded values from disk[/cyan]")

    def action_reset_defaults(self):
        self._write_running_from_master()
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
        self.config_path = self._running_config_path(self.master_config_path, new_machine)
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
                # off the event loop thread: a first-run bootstrap download
                # can take a while and would otherwise freeze the whole TUI
                f3d_path = await asyncio.to_thread(
                    f3d_bootstrap.ensure_f3d_path,
                    lambda msg: self.call_from_thread(self.log_line, msg))
                self._f3d_proc = subprocess.Popen(
                    [f3d_path, "--watch", out_path, "-g", "-x", *camera_flags],
                    cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._f3d_out_path = out_path
                self.log_line(f"[cyan]launched f3d --watch on {out_path}[/cyan]")
            except (FileNotFoundError, RuntimeError) as exc:
                self.log_line(f"[red]couldn't launch f3d: {exc}[/red]")
            return
        await asyncio.sleep(0.3)  # let f3d's own file watcher reload first
        if sys.platform == "win32":
            if not _raise_window_by_pid(self._f3d_proc.pid) and not self._warned_no_wmctrl:
                self._warned_no_wmctrl = True
                self.log_line("[yellow]f3d already open with the updated model, but couldn't "
                               "bring it to front automatically - click its taskbar icon[/yellow]")
        elif shutil.which("wmctrl"):
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
        elif values["target"] == "normal":
            # Hammond Split only: v2's real Render_Mode==0 "Normal" (v1
            # GenStyle 0/4/5 "Normal"/NormalL/NormalR) - flat, un-rotated,
            # never resin-supported (see hammond_split.NormalElement()'s
            # docstring), a genuine second render target, not a debug
            # mode. Render Left/Right (already wired above) pick NormalL/
            # NormalR/combined the same way they already do for Element/
            # Resin. DOES go through build_glyph/TextRing (NormalElement()
            # still strikes real characters), so Minkowski is forced the
            # same way as the other real-glyph-pipeline branches.
            # build-resin-support's checkbox value is simply never turned
            # into a flag here - the real Normal target has no resin
            # geometry at all (see build_log-adjacent picker-help text).
            cmd += ["--hammond-split-normal"]
            if fast:
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
        if self.machine == "selectric_composer":
            # No CPI widget for Composer (see _compose_type_test_tab) -
            # real proportional spacing (Units/inch, --composer-config
            # below) replaces it entirely, so the value passed here is
            # never actually used by build_type_test_line.
            cpi = self.cfg["type_test"]["cpi"]
        else:
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
        # Selectric Composer sizes type by cap-height (font.
        # composer_cap_height/2.834 = Font_Size_Selected, see lib/
        # selectric_composer.py's configure()) instead of a direct
        # font.size_mm - every other machine (including Selectric I/II &
        # III) has "size_mm" in self.inputs directly.
        if "size_mm" in self.inputs:
            font_size_mm = self.inputs["size_mm"].value
        else:
            font_size_mm = str(float(self.inputs["composer_cap_height"].value) / 2.834)
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
        self.log_line(f"[bold]--- Type Test (overwrites {out_path}) ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "type_test.py"), text,
               "--cpi", str(cpi), "--lpi", str(lpi), "--font-path", font_path, "--font-size-mm", font_size_mm]
        # same horizontal-alignment convention as the real element
        # (advance-box center/left + modified_left/right nudges) - read
        # live off the Font & Alignment tab's own widgets. Selectric
        # (mode only, no center_offset_mm/left_offset_mm/modified_*
        # concept - see FONT_FIELDS_SELECTRIC12) just passes --align-mode
        # and lets type_test.py's own defaults (0/empty) cover the rest -
        # this is a v4-only flat preview, not required to replicate the
        # real element's alignment pipeline exactly for any machine.
        if "mode" in self.inputs:
            cmd += ["--align-mode", self.inputs["mode"].value]
        if "center_offset_mm" in self.inputs:
            cmd += ["--center-offset-mm", self.inputs["center_offset_mm"].value]
        if "left_offset_mm" in self.inputs:
            cmd += ["--left-offset-mm", self.inputs["left_offset_mm"].value]
        if "modified_left_chars" in self.inputs:
            # "=" form, not space-separated, in case the chars field
            # starts with "-" (would otherwise look like another flag)
            cmd += ["--modified-left-chars=" + self.inputs["modified_left_chars"].value]
        if "modified_left_offset_mm" in self.inputs:
            cmd += ["--modified-left-offset-mm", self.inputs["modified_left_offset_mm"].value]
        if "modified_right_chars" in self.inputs:
            cmd += ["--modified-right-chars=" + self.inputs["modified_right_chars"].value]
        if "modified_right_offset_mm" in self.inputs:
            cmd += ["--modified-right-offset-mm", self.inputs["modified_right_offset_mm"].value]
        if "caret_drop_mm" in self.inputs:
            cmd += ["--caret-drop-mm", self.inputs["caret_drop_mm"].value]
        if "underscore_lift_mm" in self.inputs:
            cmd += ["--underscore-lift-mm", self.inputs["underscore_lift_mm"].value]
        # Secondary font ("font 2") - characters that use a different font
        # and size from the main one. type_test.py implements it as
        # --mod-chars/--mod-font-path/--mod-font-size-mm; without this
        # passthrough a Type Test would render every character in the base
        # font even where the real element switches. ONE branch for every
        # machine that has the feature, which is what unifying Hammond
        # Split's char_mod:* onto the Selectric family's font2:* spelling
        # bought - it used to need two. The Composer is the one machine
        # sizing font 2 by CAP HEIGHT rather than mm (see
        # FONT_FIELDS_SELECTRIC_COMPOSER), hence the conversion.
        if "font2_chars" in self.inputs and self.inputs["font2_chars"].value:
            if "font2_size_mm" in self.inputs:
                font2_size = self.inputs["font2_size_mm"].value
            else:
                font2_size = str(float(self.inputs["font2_composer_cap_height"].value) / 2.834)
            cmd += ["--mod-chars=" + self.inputs["font2_chars"].value,
                    "--mod-font-path", self.inputs["font2_path"].value,
                    "--mod-font-size-mm", font2_size]
        # Selectric Composer's real proportional-spacing convention
        # (Composer_Pitch_List/cumulativeSum - see type_test.py's
        # --composer-config docstring) - self.config_path was already
        # rewritten by _save_to_yaml above (including the just-edited
        # Units/inch widget), so type_test.py reads type_test.pitch_list/
        # units_per_inch/default_units straight off disk. No-op for every
        # other machine.
        if self.machine == "selectric_composer":
            cmd += ["--composer-config", self.config_path]
        cmd += ["--out", out_path]
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

    async def _pick_system_font(self, key):
        """The "Installed" button - pick a font by name (see
        SystemFontPicker) rather than by file. Sets the same Input
        _browse_font() does, so everything downstream (the "Currently
        selected" label via on_input_changed, _collect_values,
        _save_to_yaml) is unchanged - the config still stores a path."""
        current = self.inputs[key].value
        # Which of the (up to four) font fields this is - the picker
        # looks identical for all of them otherwise
        label = next((f[3] for f in self.FIELDS if f[0] == key), "font")
        result = await self.push_screen_wait(
            SystemFontPicker(current_path=current, title=f"Installed fonts - {label}"))
        if result is not None:
            self.inputs[key].value = str(result)

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

    def _set_build_running(self, proc):
        """Show/hide the Cancel button with the job it belongs to."""
        self._build_proc = proc
        try:
            self.query_one("#btn-cancel-build", Button).display = proc is not None
        except NoMatches:
            pass  # called before compose (or after teardown) - nothing to show

    @staticmethod
    def _kill_proc(proc):
        """SIGTERM the child if it is still alive. Python installs no
        SIGTERM handler, so the OS default action applies immediately -
        which matters because these jobs spend most of their time inside
        manifold3d's C++ boolean/Minkowski code, where a SIGINT-style
        KeyboardInterrupt would not be raised until control returned to
        the interpreter (i.e. possibly minutes later, which is exactly
        the wait being cancelled)."""
        if proc is None or proc.returncode is not None:
            return
        try:
            proc.terminate()
        except ProcessLookupError:
            pass  # exited between the check and the signal

    def action_cancel_build(self):
        if self._build_proc is None:
            return
        self.log_line("[yellow]cancelling...[/yellow]")
        self._kill_proc(self._build_proc)

    async def _stream_subprocess(self, cmd, success_message=None):
        # Kill anything still running before starting. run_worker(
        # exclusive=True) cancels the previous WORKER, but cancellation is
        # asynchronous, so without this the old subprocess could outlive
        # the start of the new one - the reported "press Render then
        # Preview, preview loads but the render keeps going" case.
        if self._build_proc is not None:
            self.log_line("[yellow]superseded - stopping the running job[/yellow]")
            self._kill_proc(self._build_proc)
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
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=REPO_ROOT,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            self._set_build_running(proc)
            async for line in proc.stdout:
                text = line.decode(errors="replace").rstrip()
                self.log_line(text)
                self._update_progress(text)
            await proc.wait()
        finally:
            timer.stop()
            # Always kill OUR child, even on cancellation - this is the
            # whole point (a cancelled worker used to abandon a live
            # process). Only clear the shared handle if it is still ours:
            # the replacement job may already have installed its own by
            # the time this cancelled coroutine's finally block runs.
            self._kill_proc(proc)
            if self._build_proc is proc:
                self._set_build_running(None)
        dt = time.time() - t0
        elapsed.update(f"{dt:.1f}s")
        if proc.returncode == 0:
            self.query_one("#build-progress", ProgressBar).update(progress=100)
            msg = success_message or "f3d (if running with --watch) should refresh"
            self.log_line(f"[green]done in {dt:.1f}s[/green] - {msg}")
        elif proc.returncode is not None and proc.returncode < 0:
            # Killed by a signal - our own terminate(), i.e. Cancel or a
            # supersede. Not an error worth painting red.
            self.query_one("#build-progress", ProgressBar).update(progress=0)
            self.log_line(f"[yellow]cancelled after {dt:.1f}s[/yellow]")
        else:
            self.log_line(f"[red]exited {proc.returncode} after {dt:.1f}s[/red]")
        return proc.returncode

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "font-profile-select":
            if event.value is not Select.NULL:
                self.run_worker(self._apply_font_profile(str(event.value)), exclusive=False)
            return
        if event.select.id == "coverage-preset-select":
            chars = self._charset_for_coverage_select_value(event.value)
            if chars is not None:
                self.query_one("#coverage-chars", TextArea).text = chars
            return
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
        for i in range(self.LAYOUT_MAX_ROWS):
            self._update_row_widget("layout-original-row", i, display_rows[i] if i < len(display_rows) else "")
        # Live-seed "Use N-row layout" from whichever preset is now
        # selected - this is the switch's ONLY automatic sync (see its
        # own comment in _compose_layout_tab: deliberately unlinked from
        # Modify glyphs, which no longer touches it at all).
        if self.LAYOUT_ROW_COUNT_VARIES:
            try:
                use_extra = self.query_one("#layout-use-extra-rows", Switch)
            except NoMatches:
                pass
            else:
                use_extra.value = len(display_rows) >= self.LAYOUT_MAX_ROWS
                try:
                    self.query_one("#layout-extra-rows").display = use_extra.value
                except NoMatches:
                    pass
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

    def on_input_changed(self, event: Input.Changed) -> None:
        """Keeps every "Currently selected: ..." font-name label (see
        _font_display_name()) live as its Input changes - by typing, by
        Browse setting .value programmatically (Textual's Input.value is
        reactive, so a programmatic set fires this same Changed message,
        no separate wiring needed in _browse_font()), or by
        _refresh_widgets_from_cfg() repopulating every field on
        Reload/Reset/switching config."""
        input_id = event.input.id or ""
        if not input_id.startswith("field-"):
            return
        key = input_id.removeprefix("field-")
        if key not in FONT_PATH_FIELD_KEYS:
            return
        try:
            label = self.query_one(f"#font-name-{key}", Static)
        except NoMatches:
            return
        label.update(_font_display_name(event.value))

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Section-nav list -> which TabbedContent pane is showing. On
        HIGHLIGHTED rather than SELECTED so arrowing through the list
        moves through the sections live, the way the old tab bar's
        left/right did - a click highlights too, so mouse use is
        unaffected. (SystemFontPicker's own list never reaches here - that
        screen stops its own OptionList messages.)"""
        if event.option_list.id != "section-nav":
            return
        event.stop()
        tab_id = event.option.id
        if tab_id:
            self.query_one("#tabs", TabbedContent).active = tab_id

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "layout-use-extra-rows":
            # explicit "does this hand-edited layout use the extra
            # row(s)" declaration - see its own Switch's comment in
            # _compose_layout_tab. Just toggles which Inputs are visible;
            # _save_to_yaml reads the switch itself, not this container's
            # display, to decide how many rows to write.
            try:
                self.query_one("#layout-extra-rows").display = event.value
            except NoMatches:
                pass
            return
        if event.switch.id != "layout-modify-glyphs":
            return
        container = self.query_one("#layout-custom-rows")
        container.display = event.value
        if event.value:
            # freshly unlocked - seed the editable copy from the current
            # read-only preview (whatever preset's selected in the
            # dropdown right now, or the existing custom rows if
            # "custom"), so it starts as an exact copy to hand-edit from
            self._reset_layout_rows_to_selected_preset()

    def _reset_layout_rows_to_selected_preset(self):
        """"Reset to selected layout" button, next to Modify glyphs -
        discards whatever's been hand-typed into the custom row Inputs
        and reseeds them from the Layout tab's own dropdown (whatever
        preset is currently selected there, or the on-disk custom rows
        for Select.NULL/an unrecognized value - see
        _rows_for_layout_select_value). Same reseed logic Modify glyphs'
        own "freshly unlocked" case already uses, just re-triggerable on
        demand instead of only once at the moment the switch flips on -
        useful after hand-edits have drifted and you want to start over
        from the preset without toggling the switch off and back on."""
        # Deliberately does NOT touch "Use N-row layout" - that switch is
        # unlinked from Modify glyphs entirely (see its own comment in
        # _compose_layout_tab) and stays in sync with the PRESET dropdown
        # instead (on_select_changed), not with this Modify-glyphs-
        # triggered reseed.
        layout_select_value = self.query_one("#layout-select", Select).value
        display_rows = self._rows_for_layout_select_value(layout_select_value)
        for i in range(self.LAYOUT_MAX_ROWS):
            self._update_row_widget("layout-custom-row", i, display_rows[i] if i < len(display_rows) else "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("pick-machine-"):
            self.run_worker(self._select_machine(button_id.removeprefix("pick-machine-")), exclusive=True)
        elif button_id == "btn-change-machine":
            self.run_worker(self._change_machine(), exclusive=True)
        elif button_id == "font-profile-save":
            self.run_worker(self._save_font_profile(), exclusive=True)
        elif button_id == "btn-cancel-build":
            self.action_cancel_build()
        elif button_id == "btn-render":
            self.action_render()
        elif button_id == "btn-preview":
            self.action_preview()
        elif button_id == "btn-generate-legend":
            self.action_generate_legend()
        elif button_id == "btn-save-legend":
            self.run_worker(self.action_save_legend(), exclusive=True)
        elif button_id == "btn-save":
            self.run_worker(self.action_save(), exclusive=True)
        elif button_id == "btn-render-test-text":
            self.run_worker(self.action_render_type_test(), exclusive=True)
        elif button_id == "btn-reset-defaults":
            self.action_reset_defaults()
        elif button_id == "btn-reset-layout-rows":
            self._reset_layout_rows_to_selected_preset()
        elif button_id == "btn-coverage-scan":
            self.run_worker(self._run_font_coverage_scan(), exclusive=True)
        elif button_id == "btn-coverage-save-report":
            self.run_worker(self._save_font_coverage_report(), exclusive=True)
        elif button_id == "browse-config":
            # checked before the generic "browse-" prefix below - this
            # one isn't a font field, it switches the whole app's config
            self.run_worker(self._browse_config())
        elif button_id == "browse-coverage-font-dir":
            # also checked before the generic "browse-" prefix below - a
            # directory picker (SelectDirectory), not _browse_font's
            # font-FILE picker (FileOpen)
            self.run_worker(self._browse_coverage_font_dir())
        elif button_id.startswith("browse-"):
            # not exclusive - browsing for a font shouldn't cancel (or be
            # blocked by) an in-progress build worker
            self.run_worker(self._browse_font(button_id.removeprefix("browse-")))
        elif button_id.startswith("sysfont-"):
            # same non-exclusive reasoning as browse- above; this one
            # picks by font NAME instead of by file (SystemFontPicker)
            self.run_worker(self._pick_system_font(button_id.removeprefix("sysfont-")))


if __name__ == "__main__":
    # No args: starts at the machine picker (see MACHINES/
    # _compose_machine_picker). A config path skips the picker and loads
    # straight into that config's machine - the old direct-launch usage,
    # kept for power users; the picker's "Change Machine" button is still
    # available afterward either way.
    TuneApp(sys.argv[1] if len(sys.argv) > 1 else None).run()
