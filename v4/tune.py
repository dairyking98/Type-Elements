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
TUI session, not a keeper. Save copies that temp STL to
output/saved/<timestamp>.stl plus a <timestamp>.json sidecar recording
the full config and what produced it (preview/render/type_test, resin
support on/off, timestamp) - only Save actually keeps anything.

Usage:
    python3 tune.py config/blickensderfer.yaml

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
    dropdown ("center"/"left"), not free text.
  Type Test        - NOT part of the real element. A flat, CPI/LPI-spaced
    test block (matches v2's TypeTest() fixed-pitch convention; LPI is
    the vertical equivalent for multi-line text, default 6) using the
    Font & Alignment tab's live values (path/size, align mode, all the
    center/left/modified_left/modified_right offsets - same
    alignment_x_offset() convention the real element uses), for instant
    text/legibility checks. Overwrites the same output STL path as
    Render/Quick Preview (so the same f3d --watch window shows it) -
    it's a scratch preview, not saved anywhere else (see Save).
    Triggered by the "RENDER TEST TEXT" button, which - unlike this
    tab's other widgets - lives in the always-visible button panel
    (below the tabs), not inside this TabPane, so it stays clickable
    from the Font & Alignment tab (or any tab) without switching here
    first. Triggers the same auto-open/raise f3d behavior as Preview/
    Render (see the "f3d preview" checkbox, below), and additionally
    starts f3d in camera view 7 (Top View) - only takes effect on a
    fresh launch, since f3d has no CLI way to change an already-running
    instance's camera.
  Build            - stripped down to ONE dropdown: Element Only vs.
    Element + Resin Print (build.resin_support). Resin tab's own fields
    only matter when Resin Print is selected.
  Resin            - resin.* (Resin_Rod_Raft is not exposed - Blickensderfer
    always uses the default true, no reason to flip it interactively)
  Layout           - a dropdown of named Blickensderfer keyboard layouts
    (ported from v2/lib/layouts/blick_layouts.scad) that rewrites
    layout.rows. layout.latitude_columns is not exposed - it must stay
    in sync with placement_map/the physical layout, not something to
    change casually; edit it directly in the YAML if you really mean to.
  Quality          - quality.* facet counts + build.points_per_mm/
    separation_mm/render_core_groove/simplify_tolerance_mm (moved here
    from Build - these are all mesh generation quality/speed knobs, not
    "what to build"). The Minkowski draft sweep itself is NOT exposed
    here - Render always forces it on and Quick Preview always forces
    it off (see _run_build), so a config-file toggle would just be
    dead weight/a second source of truth.
  Logo             - logo.*
  Element          - element.* - flagged ADVANCED: real machine geometry,
    not something you'd normally tune. Last tab on purpose.

List/array-valued config entries other than layout.rows (baseline_row,
cutout_row, placement_map, bottom_support_fractions) are still NOT
exposed - they don't fit a single-value text field safely and are rare
to tune interactively. Edit those directly in the YAML.
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

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
# f3d --command-script file: just `set_camera top`, the exact console
# command the "7" key runs - see action_render_type_test's use of it
F3D_TOP_VIEW_SCRIPT = os.path.join(REPO_ROOT, "f3d_top_view_cmds.txt")

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

DEFAULT_TYPE_TEST_TEXT = "The quick brown fox jumps over the lazy dog 1234567890"  # v2's own default

# Each section becomes one tab (except Layout/Build/Type Test, which have
# bespoke widgets - see compose()). Field tuples: (yaml key - must be
# unique across the whole file, section path for reading the current
# value, type, label, help text). type is float/int/bool/str.
SECTIONS = {
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
    "Element": [
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
        ("cut_groove_inner_x", ["resin", "cut_groove_inner_x"], float, "Cut groove inner X (mm)", ""),
        ("bottom_support_inner_angle_offset", ["resin", "bottom_support_inner_angle_offset"], float,
         "Bottom support angle offset (deg)", ""),
    ],
}

FIELDS = [field for fields in SECTIONS.values() for field in fields]


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
    .field-help { color: $text-muted; height: 1; }
    #buttons { height: 11; dock: bottom; padding: 0 1; }
    #btn-render-test-text { height: 3; width: 1fr; text-style: bold; margin-bottom: 1; }
    #primary-buttons { height: 5; }
    #primary-buttons Button { width: 1fr; height: 5; text-style: bold; }
    #f3d-row { height: 1; margin-top: 1; }
    #f3d-row .field-label { width: auto; margin-right: 1; }
    #f3d-row Switch { width: auto; height: 1; border: none; padding: 0; }
    #status { height: 1; color: $text-muted; padding: 0 1; }
    .advanced-warning { color: $warning; text-style: bold; height: 2; padding: 0 0 1 0; }
    .picker-row { height: 3; }
    .picker-help { color: $text-muted; height: 1; }
    #type-test-text { height: 8; }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "preview", "Quick Preview"),
        ("b", "render", "Render"),
        ("s", "save", "Save"),
        ("r", "reload", "Reload from file"),
    ]

    def __init__(self, config_path):
        super().__init__()
        self.config_path = os.path.abspath(config_path)
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
        self._load_current()

    def _kill_f3d(self):
        if self._f3d_proc is not None and self._f3d_proc.poll() is None:
            self._f3d_proc.terminate()

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
        self._kill_f3d()
        self.exit()

    def _load_current(self):
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)

    def _current_layout_preset(self):
        current_rows = self.cfg.get("layout", {}).get("rows")
        for name, rows in LAYOUT_PRESETS.items():
            if rows == current_rows:
                return name
        return None  # custom/unrecognized - leave as-is unless explicitly changed

    def _compose_section_tab(self, section):
        fields = SECTIONS[section]
        tab_id = f"tab-{section.lower().replace(' ', '-').replace('&', 'and')}"
        with TabPane(section, id=tab_id):
            with VerticalScroll():
                if section == "Element":
                    yield Static(
                        "ADVANCED - real machine dimensions.\nGenerally shouldn't need to change these.",
                        classes="advanced-warning")
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
                        if help_text:
                            yield Static(help_text, classes="field-help")

    def _compose_layout_tab(self):
        # named-layout picker only - latitude_columns must stay in sync
        # with placement_map/the physical layout, so it's not exposed
        # here (edit it directly in the YAML if you really mean to)
        with TabPane("Layout", id="tab-layout"):
            with VerticalScroll():
                with Vertical(classes="picker-row"):
                    yield Static("Keyboard layout", classes="field-label")
                    preset_now = self._current_layout_preset()
                    options = [(name, name) for name in LAYOUT_PRESETS]
                    select = Select(options, value=preset_now if preset_now else Select.BLANK,
                                    id="layout-select", allow_blank=True, prompt="(custom - not a known preset)")
                    yield select
                yield Static(
                    "Ported from v2/lib/layouts/blick_layouts.scad. All share the same\n"
                    "physical placement_map - only glyph content per row changes.\n"
                    "HEBREW_ENGL needs a Hebrew-capable font.path to render correctly\n"
                    "(v2 auto-switches fonts per layout; v4 does not).",
                    classes="picker-help")

    def _compose_build_tab(self):
        with TabPane("Build", id="tab-build"):
            with VerticalScroll():
                with Vertical(classes="picker-row"):
                    yield Static("Build target", classes="field-label")
                    resin_now = bool(self.cfg.get("build", {}).get("resin_support"))
                    build_select = Select(
                        [("Element Only", False), ("Element Resin Print", True)],
                        value=resin_now, id="build-select", allow_blank=False)
                    yield build_select
                yield Static(
                    "Element Only = FullElement() (build.resin_support: false).\n"
                    "Element Resin Print = ResinPrint(), adds ResinSupport()'s rods/\n"
                    "breakaway ring (build.resin_support: true) - see the Resin tab\n"
                    "for its own settings, which only matter in this mode.",
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
                yield TextArea(DEFAULT_TYPE_TEST_TEXT, id="type-test-text")
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("CPI", classes="field-label")
                        yield Input(value="10", id="type-test-cpi")
                    yield Static("Characters per inch (v2's Test_CPI).", classes="field-help")
                with Vertical(classes="field-row"):
                    with Horizontal():
                        yield Static("LPI", classes="field-label")
                        yield Input(value="6", id="type-test-lpi")
                    yield Static("Lines per inch - vertical spacing for multi-line text.", classes="field-help")

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form"):
            yield Static(f"config: {os.path.relpath(self.config_path, REPO_ROOT)}", id="status")
            with TabbedContent():
                yield from self._compose_section_tab("Font & Alignment")
                yield from self._compose_type_test_tab()
                yield from self._compose_build_tab()
                yield from self._compose_section_tab("Resin")
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
        yield Footer()

    def log_line(self, text):
        self.query_one("#log", RichLog).write(text)

    def _collect_values(self):
        values = {}
        for key, path, typ, label, help_text in FIELDS:
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
        # build target dropdown -> resin_support
        values["resin_support"] = self.query_one("#build-select", Select).value
        return values

    def _save_to_yaml(self, values):
        with open(self.config_path) as f:
            text = f.read()
        for key, value in values.items():
            text = patch_yaml_value(text, key, value)
        layout_select = self.query_one("#layout-select", Select)
        if layout_select.value is not Select.BLANK:
            text = patch_yaml_rows(text, LAYOUT_PRESETS[layout_select.value])
        with open(self.config_path, "w") as f:
            f.write(text)
        self._load_current()

    def action_render(self):
        self.run_worker(self._run_build(fast=False), exclusive=True)

    def action_preview(self):
        self.run_worker(self._run_build(fast=True), exclusive=True)

    def action_reload(self):
        self._load_current()
        for key, path, typ, label, help_text in FIELDS:
            current = get_nested(self.cfg, path)
            widget = self.inputs[key]
            if typ is bool:
                widget.value = bool(current)
            else:
                widget.value = str(current)
        preset_now = self._current_layout_preset()
        self.query_one("#layout-select", Select).value = preset_now if preset_now else Select.BLANK
        self.query_one("#build-select", Select).value = bool(self.cfg["build"]["resin_support"])
        self.log_line("[cyan]reloaded values from disk[/cyan]")

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
        # Minkowski draft sweep is not a config field the user tunes - it's
        # entirely determined by which button was pressed, forced explicitly
        # either way so the config's build.minkowski_enabled default is
        # never consulted here. Build target (Element Only vs. Resin Print)
        # is NOT forced here though - both buttons defer to whatever
        # build.resin_support was just saved from the Build tab's dropdown,
        # so Quick Preview still shows resin supports when that's selected.
        if fast:
            cmd += ["--no-minkowski", "--no-core-groove"]
        else:
            cmd += ["--minkowski"]
        returncode = await self._stream_subprocess(cmd)
        if returncode == 0:
            self._last_build_info = {
                "kind": "preview" if fast else "render",
                "resin_support": values["resin_support"],
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
            await self._ensure_f3d_after_build(out_path)

    async def action_render_type_test(self):
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

    def action_save(self):
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], self.cfg["output"]["stl_name"])
        if not os.path.exists(out_path):
            self.log_line("[yellow]nothing to save yet - Preview or Render first[/yellow]")
            return
        save_dir = os.path.join(REPO_ROOT, self.cfg["output"]["directory"], "saved")
        os.makedirs(save_dir, exist_ok=True)
        base = f"blickensderfer_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        stl_path = os.path.join(save_dir, f"{base}.stl")
        meta_path = os.path.join(save_dir, f"{base}.json")
        n = 2
        while os.path.exists(stl_path):
            stl_path = os.path.join(save_dir, f"{base}_{n}.stl")
            meta_path = os.path.join(save_dir, f"{base}_{n}.json")
            n += 1
        shutil.copy2(out_path, stl_path)
        metadata = {
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "source_config": os.path.relpath(self.config_path, REPO_ROOT),
            "last_build": self._last_build_info,
            "config": self.cfg,
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        self.log_line(f"[green]saved[/green] {os.path.relpath(stl_path, REPO_ROOT)} "
                       f"(+ {os.path.basename(meta_path)})")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-render":
            self.action_render()
        elif event.button.id == "btn-preview":
            self.action_preview()
        elif event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-render-test-text":
            self.run_worker(self.action_render_type_test(), exclusive=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} config/blickensderfer.yaml")
        sys.exit(1)
    TuneApp(sys.argv[1]).run()
