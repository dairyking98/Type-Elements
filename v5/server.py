#!/usr/bin/env python3
"""
Type Elements v5 - local engine server.

v5 splits the program in two:

  * the ENGINE - v4's geometry pipeline (generate.py and friends, untouched)
    behind the JSON API in this file, documented in ENGINE_API.md;
  * the UI - any static web front end (default: v5/ui/) that talks only to
    that API. Swap it with --ui to try a completely different interface
    without touching a line of geometry.

    v4/.venv/bin/python3 v5/server.py --open                 # http://127.0.0.1:8090
    v4/.venv/bin/python3 v5/server.py --ui path/to/my-ui     # someone else's front end
    v4/.venv/bin/python3 v5/server.py --config-dir DIR       # scratch configs for testing

Later the same API gets an in-browser implementation (Pyodide + manifold's
WebAssembly build), so a UI can be published as a plain static site with
no server at all.

Reuses tune.py (field tables, comment-preserving YAML patchers, running-
config migration) and runs v4's scripts as subprocesses with exactly the
flags tune.py uses - no logic is copied. Localhost-only unless --host says
otherwise.
"""

import argparse
import asyncio
import json
import os
import shutil
import sys
from types import SimpleNamespace

import uvicorn
import yaml
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

V5 = os.path.dirname(os.path.abspath(__file__))
V4 = os.path.join(os.path.dirname(V5), "v4")      # the geometry engine v5 drives - never edited from here
DEFAULT_UI = os.path.join(V5, "ui")
sys.path.insert(0, V4)
sys.path.insert(0, os.path.join(V4, "lib"))

import tune  # noqa: E402  (tables + patchers + migration; importing does not start the TUI)
import font_coverage  # noqa: E402
from lib import font_profiles  # noqa: E402
from lib.layouts import (LAYOUT_PRESETS_BY_MACHINE, LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE,  # noqa: E402
                         LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE, LAYOUT_PICKER_HELP)
from lib.system_fonts import list_system_fonts  # noqa: E402
from datetime import datetime  # noqa: E402

FONT_EXTS = (".ttf", ".otf", ".ttc", ".otc")
TYPE_NAMES = {bool: "bool", int: "int", float: "float", str: "str"}

app = FastAPI(title="Type Elements engine")
CONFIG_DIR = os.path.join(V4, "config")
BUILD = SimpleNamespace(proc=None)


# ------------------------------------------------------------------ helpers

MASTER_OVERRIDE = {}   # machine -> a different master opened with "Open config" (tune.py's Browse)


def paths(machine):
    """(master, running). Running is always <master's dir>/<machine>.running.yaml
    - tune.py's convention, so opening a config elsewhere gets its own
    running copy next to it."""
    if machine not in tune.MACHINES:
        raise HTTPException(404, f"unknown machine {machine!r}")
    if machine in MASTER_OVERRIDE:
        master = MASTER_OVERRIDE[machine]
        return master, os.path.join(os.path.dirname(master), f"{machine}.running.yaml")
    master = os.path.join(CONFIG_DIR, f"{machine}.yaml")
    if not os.path.isfile(master):
        raise HTTPException(404, f"no config for {machine!r} in {CONFIG_DIR}")
    return master, os.path.join(CONFIG_DIR, f"{machine}.running.yaml")


def load_running(machine):
    """tune.py's convention: a per-machine running copy, bootstrapped from
    the master and back-filled with keys the master gained since."""
    master, running = paths(machine)
    if not os.path.exists(running):
        shutil.copyfile(master, running)
    migrated = tune.TuneApp._migrate_running_config(
        SimpleNamespace(master_config_path=master, config_path=running))
    with open(running, encoding="utf-8") as f:
        text = f.read()
    return yaml.safe_load(text) or {}, text, migrated


def get_path(cfg, path):
    try:
        return tune.get_nested(cfg, path)
    except (KeyError, TypeError):
        return None


def intro_text(intro):
    if isinstance(intro, tuple):
        return {"text": intro[0], "level": "advanced" if "advanced" in intro[1] else "info"}
    if isinstance(intro, str):
        return {"text": intro, "level": "info"}
    return None


def _f(key, path, typ, label, help_text="", options=None):
    return (key, path, typ, label, help_text, options or [])


EXTRA_INTROS = {
    "Row baselines": {"level": "advanced", "text":
        "ADVANCED - measured per machine. A wrong value shifts a whole row of characters off the platen "
        "line. Find the right numbers with the Calibration element, not by guessing."},
}


def extra_sections(machine, cfg):
    """Controls tune.py builds by hand instead of from SECTIONS_BY_MACHINE
    (its Build/Layout/Element/Cosmetics/Legend/Type Test extras), as the
    same field records - so every one of them is saved the way tune.py
    saves it. Only keys the config actually has are offered."""
    secs = {}
    build = [_f("resin_support", ["build", "resin_support"], "bool", "Resin supports",
                "Add the support rods/raft to Element builds." + tune.RESIN_SUPPORT_UNAVAILABLE_NOTE.get(machine, ""))]
    if machine == "hammond":
        build += [_f("orientation", ["resin", "orientation"], "select", "Print orientation", "",
                     [("Vertical", "vertical"), ("Horizontal", "horizontal")]),
                  _f("horizontal_method", ["resin", "horizontal_method"], "select", "Horizontal support method", "",
                     [("Cut groove", "cut_groove"), ("Resin rod", "resin_rod")])]
    if machine == "mignon":
        build += [_f("orientation", ["resin", "orientation"], "select", "Print orientation", "",
                     [("Upside down", "upside_down"), ("Right side up", "right_side_up")])]
    if machine == "hammond_split":
        build += [_f("render_left", ["build", "render_left"], "bool", "Render left half"),
                  _f("render_right", ["build", "render_right"], "bool", "Render right half")]
    secs["Build"] = build
    lay = cfg.get("layout") or {}
    if "baseline_row" in lay:
        secs["Row baselines"] = [
            _f("baseline_row", ["layout", "baseline_row"], "floatlist", "Baseline per row (mm)",
               "Vertical position of each row's text baseline, top row first."),
            _f("cutout_row", ["layout", "cutout_row"], "floatlist", "Platen cutout per row (mm)",
               "Where each row's platen scallop is centred.")]
    cos = cfg.get("cosmetics") or {}
    if "band_z_offsets" in cos:
        secs["Bands"] = [
            _f("band_z_offsets", ["cosmetics", "band_z_offsets"], "floatlist", "Band offsets (mm)"),
            _f("band_heights", ["cosmetics", "band_heights"], "floatlist", "Band heights (mm)")]
    if "Legend" in tune.SECTIONS_BY_MACHINE.get(machine, {}) and get_path(cfg, ["legend", "background"]) is not None:
        secs["Legend output"] = [_f("background", ["legend", "background"], "select", "Legend background", "",
                                    [("Transparent", "transparent"), ("White", "white")])]
    tt = cfg.get("type_test") or {}
    if tt:
        f = [_f("type_test_text", ["type_test", "text"], "textblock", "Test text",
                "Rendered flat as a type-test plate, to check spacing and alignment.")]
        if machine == "selectric_composer" and "units_per_inch" in tt:
            f.append(_f("units_per_inch", ["type_test", "units_per_inch"], "float", "Units per inch"))
        elif "cpi" in tt:
            f.append(_f("cpi", ["type_test", "cpi"], "float", "Characters per inch"))
        if "lpi" in tt:
            f.append(_f("lpi", ["type_test", "lpi"], "float", "Lines per inch"))
        secs["Type test"] = f
    return {name: [x for x in fields if get_path(cfg, x[1]) is not None] for name, fields in secs.items()}


def schema(machine, cfg):
    out = []
    for section, fields in tune.SECTIONS_BY_MACHINE.get(machine, {}).items():
        items = []
        for key, path, typ, label, help_text in fields:
            val = get_path(cfg, path)
            items.append({
                "key": key, "path": path, "type": TYPE_NAMES.get(typ, "str"),
                "label": label, "help": help_text, "value": val,
                "options": [{"label": l, "value": v} for l, v in tune.SELECT_FIELD_OPTIONS.get(key, [])],
                "list": isinstance(val, (list, dict)),
            })
        out.append({"section": section, "intro": intro_text(tune.SECTION_INTROS.get(section)),
                    "fields": items})
    for section, fields in extra_sections(machine, cfg).items():
        if not fields:
            continue
        out.append({"section": section, "intro": EXTRA_INTROS.get(section), "fields": [{
            "key": key, "path": path, "type": "str" if typ == "select" else typ, "label": label,
            "help": help_text, "value": get_path(cfg, path),
            "options": [{"label": l, "value": v} for l, v in opts], "list": False, "extra": True,
        } for key, path, typ, label, help_text, opts in fields]})
    return out


def build_targets(machine, cfg):
    """Build-target choices exactly as tune.py's #build-select offers them,
    plus the current value derived from the config."""
    secs = tune.SECTIONS_BY_MACHINE.get(machine, {})
    target = get_path(cfg, ["build", "target"]) or "element"
    if machine == "hammond":
        return ([{"value": v, "label": l} for l, v in tune.HAMMOND_BUILD_OPTIONS],
                tune._hammond_build_dropdown_value(target, get_path(cfg, ["element", "groove"])))
    opts = [("Element", "element")]
    if "Gauge" in secs:
        opts.append(("Shaft gauge test", "gauge"))
    if "Calibration" in secs:
        opts.append(("Calibration element", "calibration"))
    if machine == "hammond_split":
        opts.append(("Normal (flat, no resin)", "normal"))
    values = [v for _l, v in opts]
    return [{"value": v, "label": l} for l, v in opts], (target if target in values else "element")


def coerce(value, typ):
    if typ == "floatlist":
        return [float(v) for v in value]
    if typ == "textblock":
        return str(value)
    if typ == "bool":
        return bool(value)
    if typ == "int":
        return int(value)
    if typ == "float":
        return float(value)
    return "" if value is None else str(value)


def allowed_font(path):
    """Any existing font file. The server only listens on localhost by
    default and only hands out files with a font extension, so this is no
    wider than the fonts the user can already pick - and a path typed into
    the UI previews before it is saved."""
    path = os.path.abspath(os.path.expanduser(path))
    return path.lower().endswith(FONT_EXTS) and os.path.isfile(path)


# ------------------------------------------------------------------ API

@app.get("/api/machines")
def machines():
    groups = []
    for name, keys in tune.MACHINE_CATEGORIES:
        groups.append({"group": name, "machines": [
            {"key": k, "label": tune.MACHINES[k][0],
             "available": os.path.isfile(os.path.join(CONFIG_DIR, f"{k}.yaml"))}
            for k in keys if k in tune.MACHINES]})
    return {"groups": groups}


@app.get("/api/config/{machine}")
def get_config(machine):
    cfg, _text, migrated = load_running(machine)
    master, running = paths(machine)
    targets, target = build_targets(machine, cfg)
    warning = tune.MACHINE_PICKER_WARNINGS.get(machine)
    lay = cfg.get("layout") or {}
    presets = LAYOUT_PRESETS_BY_MACHINE.get(machine, {})
    current_preset = next((n for n, rows in presets.items() if rows == lay.get("rows")), None)
    return {"machine": machine, "label": tune.MACHINES[machine][0], "cfg": cfg,
            "schema": schema(machine, cfg), "migrated": migrated,
            "running_path": running, "master_path": master,
            "presets": presets, "current_preset": current_preset,
            "layout_help": LAYOUT_PICKER_HELP.get(machine),
            # Selectric rows are flat-indexed onto a fixed hemisphere: every row
            # must keep its exact length (tune.py refuses the edit otherwise)
            "fixed_row_lengths": "rows" in lay and "placement_map" not in lay,
            "row_cap": len(lay["placement_map"]) if "placement_map" in lay else None,
            "targets": targets, "target": target,
            "warning": {"short": warning[0], "long": warning[1]} if isinstance(warning, tuple) else warning}


@app.put("/api/config/{machine}")
def put_config(machine, body: dict = Body(...)):
    """body: {"values": {key: value}, "rows": [..]?}. Scalars go through
    tune.patch_yaml_value (bare-key match, same as tune.py); layout rows
    through tune.patch_yaml_rows."""
    cfg, text, _ = load_running(machine)
    _master, running = paths(machine)
    types = {f["key"]: (f["type"], f["path"]) for s in schema(machine, cfg) for f in s["fields"]}
    errors, changed = [], 0
    for key, raw in (body.get("values") or {}).items():
        if key not in types:
            errors.append(f"{key}: not a field of {machine}")
            continue
        typ, path = types[key]
        try:
            val = coerce(raw, typ)
        except (TypeError, ValueError):
            errors.append(f"{key}: {raw!r} is not a valid {typ}")
            continue
        if val == get_path(cfg, path):
            continue
        try:
            if typ == "floatlist":
                text = tune.patch_yaml_inline_list(text, key, val)
            elif typ == "textblock":
                text = tune.patch_yaml_text_block(text, "text", val)
            else:
                text = tune.patch_yaml_value(text, key, val)
            changed += 1
        except ValueError as e:
            errors.append(str(e))
    if body.get("rows") is not None:
        lay = cfg.get("layout") or {}
        rows = [str(r) for r in body["rows"]]
        preset = body.get("preset")
        presets = LAYOUT_PRESETS_BY_MACHINE.get(machine, {})
        if "placement_map" in lay:
            cap = len(lay["placement_map"])
            rows = ["".join(list(r)[:cap]) for r in rows]
        elif "rows" in lay and preset not in presets:
            # Selectric: flat-indexed onto the hemisphere, lengths are fixed
            bad = [i + 1 for i, (r, old) in enumerate(zip(rows, lay["rows"])) if len(r) != len(old)]
            if bad or len(rows) != len(lay["rows"]):
                errors.append(f"layout rows {bad or 'count'} must keep their exact length on this machine - row edit not saved")
                rows = None
        if rows is not None and rows != lay.get("rows"):
            text = tune.patch_yaml_rows(text, rows)
            changed += 1
            if preset in presets and presets[preset] == rows:
                text = tune.patch_yaml_value(text, "modify_glyphs", False)
                hmap = LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE.get(machine, {}).get(preset)
                if hmap:
                    text = tune.patch_yaml_value(text, "hemisphere_map", hmap)
                seeds = LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE.get(machine, {}).get(preset)
                if seeds:
                    text = tune.patch_yaml_inline_list(text, "baseline_row", seeds)
                    text = tune.patch_yaml_inline_list(text, "cutout_row", seeds)
            elif "modify_glyphs" in lay:
                text = tune.patch_yaml_value(text, "modify_glyphs", True)
    if changed:
        with open(running, "w", encoding="utf-8") as f:
            f.write(text)
    return {"changed": changed, "errors": errors, **get_config(machine)}


def config_candidates(machine):
    """Masters that can be opened for this machine: every config in the
    config folder (variants included) and every saved-copy sidecar in
    output/saved/ whose machine: matches - the same rule tune.py's Browse
    enforces."""
    found = []
    saved = os.path.join(V4, "output", "saved")
    for folder, kind in ((CONFIG_DIR, "config"), (saved, "saved copy")):
        if not os.path.isdir(folder):
            continue
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith(".yaml") or fn.endswith(".running.yaml"):
                continue
            path = os.path.join(folder, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    m = (yaml.safe_load(f) or {}).get("machine", "blickensderfer")
            except Exception:
                continue
            if m == machine:
                found.append({"path": path, "label": fn, "kind": kind})
    return found


@app.get("/api/configs/{machine}")
def list_configs(machine):
    master, _r = paths(machine)
    return {"current": master, "default": os.path.join(CONFIG_DIR, f"{machine}.yaml"),
            "configs": config_candidates(machine)}


@app.post("/api/config/{machine}/open")
def open_config(machine, body: dict = Body(...)):
    path = os.path.abspath(body.get("path") or "")
    if path not in {c["path"] for c in config_candidates(machine)}:
        raise HTTPException(400, "not a config for this machine")
    if path == os.path.join(CONFIG_DIR, f"{machine}.yaml"):
        MASTER_OVERRIDE.pop(machine, None)
    else:
        MASTER_OVERRIDE[machine] = path
    return get_config(machine)


@app.post("/api/config/{machine}/reset")
def reset_config(machine):
    master, running = paths(machine)
    shutil.copyfile(master, running)
    return get_config(machine)


@app.get("/api/fonts")
def fonts():
    return [{"path": e.path, "family": e.family, "style": e.style} for e in list_system_fonts()]


@app.get("/api/default-font-dir")
def default_dir():
    from lib.system_fonts import default_font_dir
    return {"path": default_font_dir()}


@app.get("/api/font")
def font_file(path: str):
    if not allowed_font(path):
        raise HTTPException(404, "font not available")
    return FileResponse(os.path.abspath(os.path.expanduser(path)))


@app.post("/api/outlines")
def outlines(body: dict = Body(...)):
    """Glyph outlines as SVG path data, read with FreeType - the same
    library the build uses. The UI draws these when the browser refuses a
    font file (Chrome's sanitizer rejects some fonts FreeType reads fine,
    e.g. OCR-A II), so every preview still shows the real shapes.
    Coordinates are font units, y up; the UI flips them."""
    import freetype
    path = os.path.expanduser(body.get("font") or "")
    if not allowed_font(path):
        raise HTTPException(404, "font not available")
    face = freetype.Face(path)
    out = {}
    for ch in dict.fromkeys(body.get("chars") or ""):
        gid = face.get_char_index(ord(ch))
        if gid == 0:
            out[ch] = None
            continue
        face.load_glyph(gid, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
        cmds = []

        def move_to(a, _ctx):
            if cmds:
                cmds.append("Z")
            cmds.append(f"M{a.x} {a.y}")

        def line_to(a, _ctx):
            cmds.append(f"L{a.x} {a.y}")

        def conic_to(a, b, _ctx):
            cmds.append(f"Q{a.x} {a.y} {b.x} {b.y}")

        def cubic_to(a, b, c, _ctx):
            cmds.append(f"C{a.x} {a.y} {b.x} {b.y} {c.x} {c.y}")

        face.glyph.outline.decompose(None, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to)
        if cmds:
            cmds.append("Z")
        out[ch] = {"d": " ".join(cmds), "adv": face.glyph.advance.x}
    return {"upem": face.units_per_EM, "ascender": face.ascender, "descender": face.descender, "glyphs": out}


@app.post("/api/glyphs")
def glyphs(body: dict = Body(...)):
    """Per-character status of `chars` in `font` (font2 for font2_chars),
    plus the font's unused glyphs - font_coverage's own checks."""
    font = os.path.expanduser(body.get("font") or "")
    chars = list(dict.fromkeys(body.get("chars") or ""))
    font2 = os.path.expanduser(body.get("font2") or "") or font
    font2_chars = body.get("font2_chars") or ""
    status, spare = {}, {}
    for path in {font, font2}:
        if not path:
            continue
        mine = [c for c in chars if (font2 if c in font2_chars else font) == path]
        if not os.path.isfile(path):
            status.update({c: "missing" for c in mine})
            continue
        r = font_coverage.check_font(path, mine)
        status.update({c: "ok" for c in r.get("ok", [])})
        status.update({c: "missing" for c in r.get("missing", [])})
        status.update({c: "blank" for c in r.get("blank", [])})
        if path == font:
            spare = font_coverage.unused_glyphs(path, chars)
    return {"status": status, "unused": spare}


@app.get("/api/stl/{machine}")
def stl(machine):
    cfg, _t, _m = load_running(machine)
    out = cfg.get("output") or {}
    path = os.path.join(V4, out.get("directory", "output"), out.get("stl_name", ""))
    if not os.path.isfile(path):
        raise HTTPException(404, "not built yet")
    return FileResponse(path, media_type="model/stl", filename=os.path.basename(path))


def save_target(machine, choice):
    """Persists the build target the way tune.py does (build.target, and
    element.groove for Hammond's combined dropdown); returns the generate.py
    target to build."""
    _master, running = paths(machine)
    with open(running, encoding="utf-8") as f:
        text = f.read()
    if machine == "hammond":
        target, groove = tune.HAMMOND_BUILD_TARGET_GROOVE.get(choice, ("element", True))
        text = tune.patch_yaml_value(text, "groove", groove)
    else:
        target = choice or "element"
    text = tune.patch_yaml_value(text, "target", target)
    with open(running, "w", encoding="utf-8") as f:
        f.write(text)
    return target


def build_command(machine, opts):
    """Mirrors tune.py's _run_build flag-for-flag."""
    master, running = paths(machine)
    fast = bool(opts.get("fast"))
    target = save_target(machine, opts.get("target"))
    cmd = [sys.executable, os.path.join(V4, "generate.py"), running]
    if opts.get("cross_section"):
        cmd += ["--cross-section-angle-deg", str(float(opts.get("cross_section_angle") or 0))]
    if opts.get("cut_bodies"):
        cmd += ["--cut-bodies"]
    minkowski = ["--no-minkowski", "--no-minkowski-text"] if fast else ["--minkowski"]
    if target == "none":
        cmd += ["--hammond-part", "rib_only"]
    elif target == "gauge":
        cmd += ["--gauge"]
    elif target == "calibration":
        cmd += ["--calibrate", "--calibration-reference-config", master] + minkowski
    elif target == "normal":
        cmd += ["--hammond-split-normal"] + minkowski
    else:
        cmd += minkowski
    return cmd


def run_streamed(cmd):
    """Runs one subprocess (generate.py, type_test.py, generate_legend.py,
    font_coverage.py) and streams its output as NDJSON lines ({"line": ...},
    {"partial": ...} for an unterminated progress line, then {"done": rc})."""
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")

    async def stream():
        yield json.dumps({"line": "$ " + " ".join(os.path.basename(c) if i < 2 else c
                                                    for i, c in enumerate(cmd))}) + "\n"
        BUILD.proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=V4, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
        buf = b""
        while True:
            chunk = await BUILD.proc.stdout.read(4096)
            if not chunk:
                break
            buf += chunk
            *lines, buf = buf.split(b"\n")
            for raw in lines:
                yield json.dumps({"line": raw.decode("utf-8", errors="replace")}) + "\n"
            if buf:  # progress_start() prints without a newline - surface the partial line too
                yield json.dumps({"partial": buf.decode("utf-8", errors="replace")}) + "\n"
        if buf:
            yield json.dumps({"line": buf.decode("utf-8", errors="replace")}) + "\n"
        rc = await BUILD.proc.wait()
        yield json.dumps({"done": rc}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


def output_path(cfg, suffix=None):
    out = cfg.get("output") or {}
    p = os.path.join(V4, out.get("directory", "output"), out.get("stl_name", "out.stl"))
    return p if suffix is None else os.path.splitext(p)[0] + suffix


@app.post("/api/build/{machine}")
async def build(machine, body: dict = Body(...)):
    """generate.py, one job at a time - see run_streamed."""
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")
    return run_streamed(build_command(machine, body))


def type_test_command(machine, cfg):
    """Mirrors tune.py's action_render_type_test flag-for-flag, reading the
    saved running config."""
    _master, running = paths(machine)
    v = {f["key"]: f["value"] for s in schema(machine, cfg) for f in s["fields"]}
    tt = cfg.get("type_test") or {}
    text = str(tt.get("text") or "").strip("\n")
    if not text.strip():
        raise HTTPException(400, "type test text is empty")
    size = v.get("size_mm")
    if size is None and v.get("composer_cap_height") is not None:
        size = float(v["composer_cap_height"]) / 2.834
    cmd = [sys.executable, os.path.join(V4, "type_test.py"), text,
           "--cpi", str(tt.get("cpi", 10.0)), "--lpi", str(tt.get("lpi", 6.0)),
           "--font-path", str(v.get("path")), "--font-size-mm", str(size)]
    flags = {"mode": "--align-mode", "center_offset_mm": "--center-offset-mm", "left_offset_mm": "--left-offset-mm",
             "modified_left_offset_mm": "--modified-left-offset-mm", "modified_right_offset_mm": "--modified-right-offset-mm",
             "caret_drop_mm": "--caret-drop-mm", "underscore_lift_mm": "--underscore-lift-mm"}
    for key, flag in flags.items():
        if v.get(key) is not None:
            cmd += [flag, str(v[key])]
    for key, flag in (("modified_left_chars", "--modified-left-chars"), ("modified_right_chars", "--modified-right-chars")):
        if v.get(key) is not None:
            cmd.append(f"{flag}={v[key]}")
    if v.get("font2_chars"):
        f2size = v.get("font2_size_mm")
        if f2size is None and v.get("font2_composer_cap_height") is not None:
            f2size = float(v["font2_composer_cap_height"]) / 2.834
        cmd += [f"--mod-chars={v['font2_chars']}", "--mod-font-path", str(v.get("font2_path") or v.get("path")),
                "--mod-font-size-mm", str(f2size)]
    if machine == "selectric_composer":
        cmd += ["--composer-config", running]
    return cmd + ["--out", output_path(cfg)]


COVERAGE_REPORT = os.path.join(V4, "output", "font_coverage_report.md")


@app.post("/api/tool/{machine}")
async def tool(machine, body: dict = Body(...)):
    """The non-build jobs: type_test, legend, coverage (scan a font
    directory) and coverage_current (the configured font, then
    replacements). Streams like /api/build."""
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")
    cfg, _t, _m = load_running(machine)
    _master, running = paths(machine)
    name = body.get("tool")
    if name == "type_test":
        return run_streamed(type_test_command(machine, cfg))
    if name == "legend":
        return run_streamed([sys.executable, os.path.join(V4, "generate_legend.py"), running])
    if name in ("coverage", "coverage_current"):
        chars = (body.get("chars") or "").replace("\n", "").replace("\r", "")
        font_dir = os.path.expanduser(body.get("font_dir") or "")
        if not chars or not os.path.isdir(font_dir):
            raise HTTPException(400, "need a character set and an existing font directory")
        os.makedirs(os.path.dirname(COVERAGE_REPORT), exist_ok=True)
        cmd = [sys.executable, os.path.join(V4, "font_coverage.py"), "--chars=" + chars,
               "--font-dir", font_dir, "--out", COVERAGE_REPORT]
        if name == "coverage_current":
            v = {f["key"]: f["value"] for s in schema(machine, cfg) for f in s["fields"]}
            cmd += ["--font", os.path.expanduser(str(v.get("path") or ""))]
            if v.get("font2_chars"):
                cmd += ["--font2-chars=" + v["font2_chars"]]
                if v.get("font2_path"):
                    cmd += ["--font2", os.path.expanduser(v["font2_path"])]
        if body.get("deep"):
            cmd.append("--deep")
        return run_streamed(cmd)
    raise HTTPException(400, f"unknown tool {name!r}")


@app.get("/api/legend/{machine}")
def legend_svg(machine):
    cfg, _t, _m = load_running(machine)
    path = output_path(cfg, "_legend.svg")
    if not os.path.isfile(path):
        raise HTTPException(404, "no legend generated yet")
    return FileResponse(path, media_type="image/svg+xml", filename=os.path.basename(path))


@app.get("/api/coverage-report")
def coverage_report():
    if not os.path.isfile(COVERAGE_REPORT):
        raise HTTPException(404, "no report yet")
    return FileResponse(COVERAGE_REPORT, media_type="text/markdown", filename="font_coverage_report.md")


@app.post("/api/save-copy/{machine}")
def save_copy(machine, body: dict = Body(default={})):
    """tune.py's Save button: a timestamped copy of the last output in
    output/saved/, plus a .yaml sidecar holding the full config it was
    built from (loadable as a master later)."""
    cfg, _t, _m = load_running(machine)
    master, running = paths(machine)
    src = output_path(cfg)
    if not os.path.isfile(src):
        raise HTTPException(404, "nothing built yet")
    save_dir = os.path.join(os.path.dirname(src), "saved")
    os.makedirs(save_dir, exist_ok=True)
    base = f"{machine}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    dst = os.path.join(save_dir, base + ".stl")
    shutil.copyfile(src, dst)
    with open(os.path.splitext(dst)[0] + ".yaml", "w", encoding="utf-8") as f:
        f.write(f"# Saved by the web UI at {datetime.now().isoformat(timespec='seconds')}\n"
                f"# master_config: {master}\n# running_config: {running}\n"
                f"# last_build: {body.get('last_build')!r}\n")
        yaml.dump(cfg, f, sort_keys=False, allow_unicode=True)
    mapping = os.path.splitext(src)[0] + "_mapping.txt"
    if (body.get("last_build") or {}).get("target") == "calibration" and os.path.isfile(mapping):
        shutil.copyfile(mapping, os.path.splitext(dst)[0] + "_mapping.txt")
    return {"path": dst}


# ------------------------------------------------------------------ font profiles

def profile_field_paths(machine):
    return [list(f[1]) for f in tune.SECTIONS_BY_MACHINE.get(machine, {}).get("Font & Alignment", [])]


@app.get("/api/profiles/{machine}")
def profiles(machine):
    cfg, _t, _m = load_running(machine)
    paths_ = profile_field_paths(machine)
    current = font_profiles.collect_from_config(cfg, paths_)
    out = []
    for name, path in font_profiles.list_profiles(CONFIG_DIR):
        _n, values = font_profiles.load_profile(path)
        applied, aliased, skipped, unset = font_profiles.apply_to(values, paths_)
        merged = {**applied, **{k: v for k, (v, _src) in aliased.items()}}
        active = bool(merged) and all(current.get(k) == v for k, v in merged.items())
        out.append({"name": name, "values": merged, "skipped": skipped, "unset": unset, "active": active})
    return out


@app.post("/api/profiles/{machine}")
def profile_save(machine, body: dict = Body(...)):
    cfg, _t, _m = load_running(machine)
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "profile needs a name")
    font_profiles.save_profile(CONFIG_DIR, name, font_profiles.collect_from_config(cfg, profile_field_paths(machine)),
                               saved_from=machine)
    return profiles(machine)


@app.post("/api/profiles/{machine}/rename")
def profile_rename(machine, body: dict = Body(...)):
    try:
        font_profiles.rename_profile(CONFIG_DIR, body["old"], body["new"])
    except (KeyError, ValueError, FileExistsError, FileNotFoundError) as e:
        raise HTTPException(400, str(e))
    return profiles(machine)


@app.post("/api/profiles/{machine}/delete")
def profile_delete(machine, body: dict = Body(...)):
    font_profiles.delete_profile(CONFIG_DIR, body.get("name", ""))
    return profiles(machine)


@app.post("/api/build-cancel")
def cancel():
    if BUILD.proc and BUILD.proc.returncode is None:
        BUILD.proc.terminate()
        return {"cancelled": True}
    return {"cancelled": False}


@app.get("/")
def root():
    return RedirectResponse("/app/")


def main():
    global CONFIG_DIR
    p = argparse.ArgumentParser(description="Type Elements local engine + web UI")
    p.add_argument("--config-dir", default=None, help="directory of master configs (default v4/config)")
    p.add_argument("--host", default="127.0.0.1", help="localhost only by default")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--open", action="store_true", help="open the UI in the default browser")
    p.add_argument("--ui", default=DEFAULT_UI,
                   help="directory of the front end to serve (default v5/ui). Any static site that "
                        "speaks ENGINE_API.md works - point this at your own to swap the whole UI.")
    args = p.parse_args()
    if not os.path.isfile(os.path.join(args.ui, "index.html")):
        p.error(f"--ui {args.ui!r} has no index.html")
    app.mount("/app", StaticFiles(directory=os.path.abspath(args.ui), html=True), name="ui")
    if args.config_dir:
        CONFIG_DIR = os.path.abspath(args.config_dir)
    if args.open:
        import threading
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{args.host}:{args.port}/")).start()
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
