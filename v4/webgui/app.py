#!/usr/bin/env python3
"""
Type Elements web GUI - first slice of the tune.py replacement (branch
web-gui). A local web app: a Python backend (NiceGUI, on FastAPI) with the
UI in a browser tab, so it looks and behaves the same on Linux and
Windows, renders every Unicode character, and shows the built STL in an
in-page 3D viewer instead of the external f3d window.

    .venv/bin/python3 webgui/app.py                 # opens http://localhost:8090
    .venv/bin/python3 webgui/app.py --config-dir /tmp/scratch-configs

Deliberately reuses tune.py rather than copying it: the per-machine field
tables (SECTIONS_BY_MACHINE, SECTION_INTROS, SELECT_FIELD_OPTIONS), the
comment-preserving YAML patchers, the running-config bootstrap/migration,
and the "[n/total]" progress regex all come from `import tune`. Importing
tune.py does not start the TUI (that only happens under its __main__), so
both front ends read and write the same <machine>.running.yaml files the
same way, and the build itself is the same generate.py subprocess tune.py
runs. When this GUI replaces tune.py, those tables move to a lib/ module
both can import; until then tune.py stays untouched.

--config-dir points the app at a directory of master configs other than
v4/config (running copies are created next to them) - for testing against
scratch copies, never the real files.

First slice covers: machine picker, every scalar settings field, Save,
Preview (no Minkowski) / Render (Minkowski) of the element target with a
live log and progress bar, the 3D viewer, and the layout grid drawn in the
configured font with missing characters flagged. Not yet: layout editing,
calibration/gauge/type-test targets, font coverage, legend, profiles.
"""

import argparse
import asyncio
import os
import shutil
import sys
import time
from types import SimpleNamespace

import freetype
import yaml
from fastapi import HTTPException
from fastapi.responses import FileResponse
from nicegui import app, ui

V4 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, V4)
sys.path.insert(0, os.path.join(V4, "lib"))
import tune  # noqa: E402  (field tables + YAML patchers + migration, no TUI started)

PROGRESS_RE = tune.TuneApp._PROGRESS_RE
FONT_EXTS = (".ttf", ".otf", ".ttc", ".otc")


class State:
    """Single-user local app - one shared state object is enough."""
    config_dir = os.path.join(V4, "config")
    machine = None
    master_path = None
    running_path = None
    cfg = {}
    inputs = {}        # field key -> (widget, field tuple)
    building = False
    proc = None


S = State()


# ------------------------------------------------------------------ config

def machine_choices():
    out = {}
    for key, (label, _path) in tune.MACHINES.items():
        if os.path.isfile(os.path.join(S.config_dir, f"{key}.yaml")):
            out[key] = label
    return out


def load_machine(machine):
    """Same running-copy convention as tune.py: <machine>.running.yaml next
    to the master, bootstrapped as a copy, then back-filled with any keys
    the master gained since (tune.TuneApp._migrate_running_config, called
    unbound - it only uses these two attributes)."""
    S.machine = machine
    S.master_path = os.path.join(S.config_dir, f"{machine}.yaml")
    S.running_path = os.path.join(S.config_dir, f"{machine}.running.yaml")
    if not os.path.exists(S.running_path):
        shutil.copyfile(S.master_path, S.running_path)
    migrated = tune.TuneApp._migrate_running_config(
        SimpleNamespace(master_config_path=S.master_path, config_path=S.running_path))
    with open(S.running_path, encoding="utf-8") as f:
        S.cfg = yaml.safe_load(f) or {}
    return migrated


def field_value(path):
    try:
        return tune.get_nested(S.cfg, path)
    except (KeyError, TypeError):
        return None


def collect_and_save():
    """Patches every changed scalar field into the running copy with
    tune.py's own comment-preserving patcher. Returns (n_changed, errors)."""
    with open(S.running_path, encoding="utf-8") as f:
        text = f.read()
    changed, errors = 0, []
    for key, (widget, field) in S.inputs.items():
        _k, path, typ, label, _help = field
        raw = widget.value
        try:
            if typ is bool:
                val = bool(raw)
            elif typ is int:
                val = int(raw)
            elif typ is float:
                val = float(raw)
            else:
                val = "" if raw is None else str(raw)
        except (TypeError, ValueError):
            errors.append(f"{label}: {raw!r} is not a valid {typ.__name__}")
            continue
        if val == field_value(path):
            continue
        try:
            text = tune.patch_yaml_value(text, key, val)
            changed += 1
        except ValueError as e:
            errors.append(f"{label}: {e}")
    if changed:
        with open(S.running_path, "w", encoding="utf-8") as f:
            f.write(text)
        S.cfg = yaml.safe_load(text) or {}
    return changed, errors


def output_stl_path():
    out = S.cfg.get("output") or {}
    return os.path.join(V4, out.get("directory", "output"), out.get("stl_name", "out.stl"))


def current_font_path():
    return os.path.expanduser(str((S.cfg.get("font") or {}).get("path") or ""))


def glyph_status(font_path, chars):
    """{char: "ok" | "missing" | "blank"} - same two failure kinds as
    font_coverage.check_font / glyph_poc's build-time warning."""
    status = {}
    try:
        face = freetype.Face(font_path)
    except Exception:
        return {c: "missing" for c in chars}
    for c in chars:
        if c.isspace():
            status[c] = "ok"
            continue
        gid = face.get_char_index(ord(c))
        if gid == 0:
            status[c] = "missing"
            continue
        face.load_glyph(gid, freetype.FT_LOAD_NO_SCALE)
        status[c] = "ok" if face.glyph.outline.n_contours else "blank"
    return status


# ------------------------------------------------------------------ routes

@app.get("/stl")
def serve_stl():
    path = output_stl_path() if S.machine else ""
    if not os.path.isfile(path):
        raise HTTPException(404, "no STL built yet")
    return FileResponse(path, media_type="model/stl")


@app.get("/font")
def serve_font():
    """Serves ONLY the loaded config's own font file, for the layout grid's
    @font-face - never an arbitrary path from the request."""
    path = current_font_path() if S.machine else ""
    if not (os.path.isfile(path) and path.lower().endswith(FONT_EXTS)):
        raise HTTPException(404, "font not found")
    return FileResponse(path)


# ------------------------------------------------------------------ UI

def log_class(line):
    """Colour for a build-log line: build_log.warn()'s fixed WARNING marker,
    tracebacks/failures red."""
    if "WARNING" in line:
        return "text-orange-9 text-weight-bold"
    if line.startswith(("Traceback", "  File ")) or "Error" in line or "FAILED" in line:
        return "text-negative"
    return None


def build_field(field):
    key, path, typ, label, help_text = field
    val = field_value(path)
    if typ is bool:
        w = ui.switch(label, value=bool(val))
    elif key in tune.SELECT_FIELD_OPTIONS:
        opts = {v: lab for lab, v in tune.SELECT_FIELD_OPTIONS[key]}
        w = ui.select(opts, label=label, value=str(val) if str(val) in opts else None).classes("w-full")
    elif typ in (int, float):
        w = ui.number(label, value=val, format="%g" if typ is float else "%d").classes("w-full")
    else:
        w = ui.input(label, value="" if val is None else str(val)).classes("w-full")
    if help_text:
        w.tooltip(help_text)
    S.inputs[key] = (w, field)


def layout_grid():
    rows = (S.cfg.get("layout") or {}).get("rows")
    if not rows:
        ui.label("This machine has no editable layout rows.").classes("text-grey-7")
        return
    font = current_font_path()
    chars = "".join(rows)
    status = glyph_status(font, dict.fromkeys(chars))
    bad = [c for c, s in status.items() if s != "ok"]
    stamp = int(time.time())
    ui.add_css(f"@font-face {{ font-family: 'CfgFont{stamp}'; src: url('/font?t={stamp}'); }}")
    ui.label(f"Font: {os.path.basename(font) or '(none)'}").classes("text-sm text-grey-8")
    if bad:
        ui.label(f"Character not found in this font: {''.join(bad)}").classes(
            "text-white bg-red-7 q-pa-sm rounded")
    else:
        ui.label(f"All {len(status)} characters are in the font.").classes("text-positive")
    for r, row in enumerate(rows):
        with ui.row().classes("gap-0.5 items-center no-wrap"):
            ui.label(f"{r + 1}").classes("w-5 text-grey-6 text-right text-xs")
            for c in row:
                s = status.get(c, "ok")
                cell = ui.label(c if not c.isspace() else "␣").style(
                    f"font-family: 'CfgFont{stamp}', sans-serif; font-size: 20px; width: 28px; height: 34px;"
                    "display:flex; align-items:center; justify-content:center; border-radius:4px;"
                    + ("background:#c62828; color:white;" if s != "ok" else "background:#f3f3f3;"))
                cell.tooltip(f"U+{ord(c):04X}" + ("" if s == "ok" else f" - {s} in this font"))


@ui.page("/")
def index():
    ui.page_title("Type Elements")
    ui.query("body").style("background:#fafafa")

    with ui.header().classes("items-center gap-4 bg-blue-grey-9"):
        ui.label("Type Elements").classes("text-h6")
        machine_select = ui.select(machine_choices(), value=S.machine, label="Machine").props(
            "dark dense outlined").classes("w-56")
        config_label = ui.label("").classes("text-xs text-grey-4")
        ui.space()
        save_btn = ui.button("Save", icon="save")
        preview_btn = ui.button("Preview", icon="visibility").props("color=positive")
        render_btn = ui.button("Render", icon="view_in_ar").props("color=primary")

    with ui.splitter(value=42).classes("w-full").style("height: calc(100vh - 80px)") as split:
        with split.before:
            form_area = ui.column().classes("w-full q-pa-sm")
        with split.after:
            with ui.column().classes("w-full q-pa-sm gap-2"):
                scene = ui.scene(width=900, height=560, grid=(120, 24), background_color="#e8eaed")
                scene.move_camera(x=0, y=-45, z=38, look_at_z=10)
                with ui.row().classes("w-full items-center"):
                    progress = ui.linear_progress(value=0, show_value=False).classes("col")
                    elapsed = ui.label("").classes("text-sm text-grey-7 w-20")
                log = ui.log(max_lines=3000).classes("w-full").style("height: 260px; font-size: 12px")

    def show_stl():
        if os.path.isfile(output_stl_path()):
            scene.clear()
            scene.stl(f"/stl?t={time.time()}")

    def render_form():
        S.inputs = {}
        form_area.clear()
        if not S.machine:
            with form_area:
                ui.label("Pick a machine above.").classes("text-grey-7")
            return
        sections = tune.SECTIONS_BY_MACHINE.get(S.machine, {})
        names = ["Layout"] + list(sections)
        with form_area:
            with ui.row().classes("w-full no-wrap items-start"):
                tabs = ui.tabs(value=names[0]).props("vertical dense").classes("w-36")
                with tabs:
                    for n in names:
                        ui.tab(n)
                with ui.tab_panels(tabs, value=names[0]).props("vertical").classes("col"):
                    with ui.tab_panel("Layout"):
                        layout_grid()
                    for n, fields in sections.items():
                        with ui.tab_panel(n):
                            intro = tune.SECTION_INTROS.get(n)
                            if isinstance(intro, str) and intro:
                                ui.label(intro).classes("text-sm text-grey-7")
                            for field in fields:
                                if isinstance(field_value(field[1]), (list, dict)):
                                    continue  # list-valued keys need their own editors (layout rows etc.)
                                build_field(field)

    def select_machine(machine):
        if not machine:
            return
        migrated = load_machine(machine)
        config_label.text = os.path.basename(S.running_path)
        config_label.tooltip(S.running_path)
        if migrated:
            log.push(f"running config back-filled from master: {', '.join(migrated)}")
        render_form()
        scene.clear()
        show_stl()

    def save():
        if not S.machine:
            return False
        n, errors = collect_and_save()
        for e in errors:
            ui.notify(e, type="negative")
        if n:
            ui.notify(f"saved {n} field(s) to {os.path.basename(S.running_path)}", type="positive")
        return not errors

    async def build(fast):
        if S.building or not S.machine:
            return
        if not save():
            return
        S.building = True
        for b in (preview_btn, render_btn, save_btn):
            b.disable()
        progress.value = 0
        cmd = [sys.executable, os.path.join(V4, "generate.py"), S.running_path]
        cmd += ["--no-minkowski", "--no-minkowski-text"] if fast else ["--minkowski"]
        log.push(f"--- {'Preview' if fast else 'Render'} ---")
        t0 = time.time()

        async def tick():
            while S.building:
                elapsed.text = f"{time.time() - t0:.0f}s"
                await asyncio.sleep(0.5)

        ticker = asyncio.create_task(tick())
        try:
            S.proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=V4, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
            buf = b""
            while True:
                chunk = await S.proc.stdout.read(4096)
                if not chunk:
                    break
                buf += chunk
                # progress_start() prints without a newline, so split on \n
                # but also surface the unterminated tail for the progress bar
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    line = raw.decode("utf-8", errors="replace")
                    log.push(line, classes=log_class(line))
                    m = PROGRESS_RE.search(line)
                    if m:
                        progress.value = 0.95 * int(m.group(1)) / max(int(m.group(2)), 1)
                m = PROGRESS_RE.search(buf.decode("utf-8", errors="replace"))
                if m:
                    progress.value = 0.95 * int(m.group(1)) / max(int(m.group(2)), 1)
            if buf:
                log.push(buf.decode("utf-8", errors="replace"))
            rc = await S.proc.wait()
        finally:
            S.building = False
            ticker.cancel()
            for b in (preview_btn, render_btn, save_btn):
                b.enable()
        if rc == 0:
            progress.value = 1.0
            log.push(f"done in {time.time() - t0:.1f}s")
            show_stl()
        else:
            log.push(f"FAILED (exit {rc})", classes="text-negative text-weight-bold")
            ui.notify(f"build failed (exit {rc}) - see log", type="negative")

    machine_select.on_value_change(lambda e: select_machine(e.value))
    save_btn.on_click(save)
    preview_btn.on_click(lambda: build(True))
    render_btn.on_click(lambda: build(False))

    if S.machine:
        select_machine(S.machine)
    else:
        render_form()


def main():
    p = argparse.ArgumentParser(description="Type Elements web GUI")
    p.add_argument("--config-dir", default=None, help="directory of master configs (default: v4/config)")
    p.add_argument("--machine", default=None, help="machine to open with, e.g. selectric12")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--host", default="127.0.0.1",
                   help="interface to listen on - localhost only by default; 0.0.0.0 exposes it to the network")
    p.add_argument("--no-browser", action="store_true", help="don't open a browser tab")
    args = p.parse_args()
    if args.config_dir:
        S.config_dir = os.path.abspath(args.config_dir)
    if args.machine:
        load_machine(args.machine)
    ui.run(title="Type Elements", host=args.host, port=args.port, show=not args.no_browser, reload=False,
           favicon="\U0001f5a8")


if __name__ in {"__main__", "__mp_main__"}:
    main()
