#!/usr/bin/env python3
"""
Interactive terminal GUI for tuning config/blickensderfer.yaml and
triggering rebuilds, meant to run alongside an f3d --watch window (f3d
auto-reloads whenever the STL file it's watching changes on disk, so a
Render/Quick Preview here just needs to overwrite that same fixed path).
f3d is never launched automatically - use the "Launch f3d" button (or
run it yourself) whenever you actually want to look.

Usage:
    python3 tune.py config/blickensderfer.yaml

Then in another terminal:
    f3d --watch output/blickensderfer_full_element.stl -g -x
(or use the "Launch f3d" button here, which does exactly that)

Edits are NOT round-tripped through a YAML parser/dumper - the config
file has extensive prose comments documenting where every real-machine
value comes from, and a naive yaml.safe_load()+yaml.dump() would silently
strip all of them. Instead, each field is patched in place via a regex
matching just its value token on its own line, leaving everything else
(comments, formatting, unrelated keys) untouched.

Fields are grouped into tabs matching the config file's own sections.
List/array-valued config entries (baseline_row, cutout_row, placement_map,
the DHIATENSOR layout rows, bottom_support_fractions) are NOT exposed
here - they don't fit a single-value text field safely, and are rare to
tune interactively. Edit those directly in the YAML.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import time

import yaml
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Static, Switch, RichLog, TabbedContent, TabPane

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Each section becomes one tab. Field tuples: (yaml key - must be unique
# across the whole file, section path for reading the current value, type,
# label, help text). type is float/int/bool/str.
SECTIONS = {
    "Font": [
        ("path", ["font", "path"], str, "Font path", "TrueType font for the struck characters."),
        ("size_mm", ["font", "size_mm"], float, "Font size (mm)", "Em-square size, matches OpenSCAD text(size=)."),
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
        ("body_fn", ["quality", "body_fn"], int, "Body fn", "Main cosmetic cylinder body (Cylinder/ClipCylinder)."),
        ("cyl_fn", ["quality", "cyl_fn"], int, "Shaft fn", "Inner shaft/core bore only."),
        ("surface_fn", ["quality", "surface_fn"], int, "Surface fn", "Other structural detail (HollowSpace, SpeedHoles, chamfers...)."),
        ("groove_fn", ["quality", "groove_fn"], int, "Groove fn", "CoreGrooves twist angular sampling."),
        ("platen_fn", ["quality", "platen_fn"], int, "Platen fn", "Real platen cutout cylinder segments."),
        ("minkowski_fn", ["quality", "minkowski_fn"], int, "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
    ],
    "Layout": [
        ("latitude_columns", ["layout", "latitude_columns"], int, "Latitude columns", "Columns around the ring (DHIATENSOR row length)."),
    ],
    "Alignment": [
        ("mode", ["alignment", "mode"], str, "Mode", '"center" or "left".'),
        ("center_offset_mm", ["alignment", "center_offset_mm"], float, "Center offset (mm)", ""),
        ("left_offset_mm", ["alignment", "left_offset_mm"], float, "Left offset (mm)", ""),
        ("modified_left_chars", ["alignment", "modified_left_chars"], str, "Modified-left chars", "Chars getting an extra left shift."),
        ("modified_left_offset_mm", ["alignment", "modified_left_offset_mm"], float, "Modified-left offset (mm)", ""),
        ("modified_right_chars", ["alignment", "modified_right_chars"], str, "Modified-right chars", "Chars getting an extra right shift."),
        ("modified_right_offset_mm", ["alignment", "modified_right_offset_mm"], float, "Modified-right offset (mm)", ""),
    ],
    "Build": [
        ("points_per_mm", ["build", "points_per_mm"], float, "Outline density (pts/mm)", "Glyph curve sampling density."),
        ("separation_mm", ["build", "separation_mm"], float, "Draft depth (mm)", "Root-to-tip taper depth. Real value 0.5mm."),
        ("render_core_groove", ["build", "render_core_groove"], bool, "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
        ("resin_support", ["build", "resin_support"], bool, "Resin supports", "ResinPrint() support rods/breakaway ring."),
        ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float, "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
        ("minkowski_enabled", ["build", "minkowski_enabled"], bool, "Minkowski draft sweep",
         "Off = fast full-depth undrafted preview (~3s vs ~30-70s)."),
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
        ("rod_raft", ["resin", "rod_raft"], bool, "Rod raft", "Resin_Rod_Raft."),
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
        val_str = json.dumps(value)  # always quoted, handles embedded quotes/specials
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
    .field-help { color: $text-muted; height: 1; }
    #buttons { height: 8; dock: bottom; padding: 0 1; }
    #btn-render { height: 5; width: 1fr; text-style: bold; }
    #secondary-buttons { height: 3; }
    #secondary-buttons Button { width: 1fr; }
    #status { height: 1; color: $text-muted; padding: 0 1; }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "render", "Render"),
        ("p", "preview", "Quick Preview"),
        ("f", "launch_f3d", "Launch f3d"),
        ("r", "reload", "Reload from file"),
    ]

    def __init__(self, config_path):
        super().__init__()
        self.config_path = os.path.abspath(config_path)
        self.inputs = {}
        self._load_current()

    def _load_current(self):
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form"):
            yield Static(f"config: {os.path.relpath(self.config_path, REPO_ROOT)}", id="status")
            with TabbedContent():
                for section, fields in SECTIONS.items():
                    with TabPane(section, id=f"tab-{section.lower()}"):
                        with VerticalScroll():
                            for key, path, typ, label, help_text in fields:
                                current = get_nested(self.cfg, path)
                                with Vertical(classes="field-row"):
                                    with Horizontal():
                                        yield Static(label, classes="field-label")
                                        if typ is bool:
                                            sw = Switch(value=bool(current), id=f"field-{key}")
                                            self.inputs[key] = sw
                                            yield sw
                                        else:
                                            inp = Input(value=str(current), id=f"field-{key}")
                                            self.inputs[key] = inp
                                            yield inp
                                    if help_text:
                                        yield Static(help_text, classes="field-help")
            with Vertical(id="buttons"):
                yield Button("RENDER [b]", id="btn-render", variant="primary")
                with Horizontal(id="secondary-buttons"):
                    yield Button("Quick Preview [p]", id="btn-preview", variant="success")
                    yield Button("Launch f3d [f]", id="btn-f3d")
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
        return values

    def _save_to_yaml(self, values):
        with open(self.config_path) as f:
            text = f.read()
        for key, value in values.items():
            text = patch_yaml_value(text, key, value)
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
        self.log_line("[cyan]reloaded values from disk[/cyan]")

    def action_launch_f3d(self):
        out_path = os.path.join(REPO_ROOT, self.cfg["output"]["directory"],
                                 self.cfg["output"]["stl_name"])
        if not os.path.exists(out_path):
            self.log_line(f"[yellow]{out_path} doesn't exist yet - Render/Quick Preview first[/yellow]")
            return
        try:
            subprocess.Popen(["f3d", "--watch", out_path, "-g", "-x"],
                              cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log_line(f"[cyan]launched f3d --watch on {out_path}[/cyan]")
        except FileNotFoundError:
            self.log_line("[red]f3d not found on PATH[/red]")

    async def _run_build(self, fast):
        values = self._collect_values()
        if values is None:
            return
        self._save_to_yaml(values)
        label = "Quick Preview" if fast else "Render"
        self.log_line(f"[bold]--- {label} ---[/bold]")
        cmd = [sys.executable, os.path.join(REPO_ROOT, "generate.py"), self.config_path]
        if fast:
            cmd += ["--no-minkowski", "--no-core-groove", "--no-resin-support"]
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
            self.log_line(f"[red]generate.py exited {proc.returncode} after {dt:.1f}s[/red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-render":
            self.action_render()
        elif event.button.id == "btn-preview":
            self.action_preview()
        elif event.button.id == "btn-f3d":
            self.action_launch_f3d()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} config/blickensderfer.yaml")
        sys.exit(1)
    TuneApp(sys.argv[1]).run()
