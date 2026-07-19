#!/usr/bin/env python3
"""
Interactive terminal GUI for tuning config/blickensderfer.yaml and
triggering rebuilds, meant to run alongside an f3d --watch window (f3d
auto-reloads whenever the STL file it's watching changes on disk, so a
Preview/Full Build here just needs to overwrite that same fixed path).

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
"""

import asyncio
import os
import re
import subprocess
import sys
import time

import yaml
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Static, Switch, RichLog

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# (yaml key - must be unique across the whole file, section path for
# reading the current value, type, label, help text)
FIELDS = [
    ("separation_mm", ["build", "separation_mm"], float,
     "Draft depth (mm)", "Root-to-tip taper depth. Real value 0.5mm."),
    ("points_per_mm", ["build", "points_per_mm"], float,
     "Outline density (pts/mm)", "Glyph curve sampling density."),
    ("minkowski_enabled", ["build", "minkowski_enabled"], bool,
     "Minkowski draft sweep", "Off = fast undrafted preview (~3s vs ~30-70s)."),
    ("render_core_groove", ["build", "render_core_groove"], bool,
     "Core grooves", "16 twisted friction grooves - slow, off for quick iteration."),
    ("resin_support", ["build", "resin_support"], bool,
     "Resin supports", "ResinPrint() support rods/breakaway ring."),
    ("simplify_tolerance_mm", ["build", "simplify_tolerance_mm"], float,
     "Simplify tolerance (mm)", "Collapses minkowski_sum's CSG noise. 0 disables."),
    ("minkowski_fn", ["quality", "minkowski_fn"], int,
     "Minkowski fn", "Draft cone segments - biggest cost lever with points_per_mm."),
    ("platen_fn", ["quality", "platen_fn"], int,
     "Platen fn", "Real platen cutout cylinder segments."),
    ("body_fn", ["quality", "body_fn"], int,
     "Body fn", "Main cosmetic cylinder body segments."),
    ("cyl_fn", ["quality", "cyl_fn"], int,
     "Shaft fn", "Inner shaft/core bore segments."),
    ("surface_fn", ["quality", "surface_fn"], int,
     "Surface fn", "Other structural detail (HollowSpace, SpeedHoles, chamfers...)."),
    ("radial_offset_mm", ["logo", "radial_offset_mm"], float,
     "Logo radius offset (mm)", "LogoText placement radius = Logo_Radius + this."),
]


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
    else:
        val_str = str(value)
    pattern = re.compile(rf"^(\s*{re.escape(key)}:\s*)\S+", re.MULTILINE)
    new_text, n = pattern.subn(lambda m: m.group(1) + val_str, text, count=1)
    if n == 0:
        raise ValueError(f"key {key!r} not found in {text[:0]!r} config text - "
                          f"was it renamed/removed?")
    return new_text


class TuneApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #form { width: 54; height: 100%; border: solid $accent; padding: 0 1; }
    #log-pane { width: 1fr; height: 100%; border: solid $accent; padding: 0 1; }
    #log { height: 1fr; }
    .field-row { height: 2; }
    .field-row Horizontal { height: 1; }
    .field-label { width: 24; height: 1; content-align: left middle; }
    .field-row Input { width: 1fr; height: 1; border: none; padding: 0 1; background: $panel; }
    .field-row Switch { width: auto; height: 1; border: none; padding: 0; }
    .field-help { color: $text-muted; height: 1; }
    #buttons { height: 3; dock: bottom; }
    #buttons Button { width: 1fr; }
    #status { height: 1; color: $text-muted; }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "preview", "Quick Preview"),
        ("b", "full_build", "Full Build"),
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
        with VerticalScroll(id="form"):
            yield Static(f"config: {os.path.relpath(self.config_path, REPO_ROOT)}", id="status")
            for key, path, typ, label, help_text in FIELDS:
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
                    yield Static(help_text, classes="field-help")
            with Horizontal(id="buttons"):
                yield Button("Quick Preview [p]", id="btn-preview", variant="success")
                yield Button("Full Build [b]", id="btn-full", variant="primary")
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

    def action_preview(self):
        self.run_worker(self._run_build(fast=True), exclusive=True)

    def action_full_build(self):
        self.run_worker(self._run_build(fast=False), exclusive=True)

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
            self.log_line(f"[yellow]{out_path} doesn't exist yet - run a Preview/Full Build first[/yellow]")
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
        label = "Quick Preview" if fast else "Full Build"
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
        if event.button.id == "btn-preview":
            self.action_preview()
        elif event.button.id == "btn-full":
            self.action_full_build()
        elif event.button.id == "btn-f3d":
            self.action_launch_f3d()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} config/blickensderfer.yaml")
        sys.exit(1)
    TuneApp(sys.argv[1]).run()
