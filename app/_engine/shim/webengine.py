"""
The in-browser engine's Python side, run by v5/ui/engine_worker.js inside
Pyodide. It is engine_core (the same code the local server runs) plus what
only a browser needs:

  * persistent state lives under /persist (IndexedDB-backed): running
    configs in /persist/running, font profiles in /persist/profiles, fonts the
    user adds in /persist/fonts;
  * fonts: a config's font paths point at files on someone else's computer,
    so any font that doesn't exist here is swapped for a bundled one (same
    file name if we ship it, else FreeMono) and the swap is reported to the
    UI; the font list is bundled + user-added fonts;
  * the Minkowski record/replay hooks the worker pool drives.

Every call returns plain JSON-able data; errors come back as
{"error": {"status", "detail"}} like the HTTP engine's.
"""
import json
import os
import re
import sys

BUNDLED = "/fonts/bundled"
USER_FONTS = "/persist/fonts"
FONT_KEYS = ("path", "font2_path", "font_path", "label_font_path", "legend_font_path")
FONT_EXTS = (".ttf", ".otf", ".ttc", ".otc")

sys.path[:0] = ["/shim", "/v5", "/v4/lib", "/v4"]
import engine_core as core  # noqa: E402

core.configure(v4_dir="/v4", running_dir="/persist/running", profiles_dir="/persist/profiles")
os.makedirs(USER_FONTS, exist_ok=True)
os.makedirs("/v4/output", exist_ok=True)


# ------------------------------------------------------------------ fonts

def _font_entry(path):
    import freetype
    try:
        f = freetype.Face(path)
        return {"path": path, "family": f.family_name.decode() or os.path.basename(path),
                "style": f.style_name.decode(), "source": "bundled" if path.startswith(BUNDLED) else "yours"}
    except Exception:
        return None


def fonts():
    out = []
    for d in (USER_FONTS, BUNDLED):
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.lower().endswith(FONT_EXTS):
                    e = _font_entry(os.path.join(d, fn))
                    if e:
                        out.append(e)
    return out


def add_font(name, data):
    """Store a font the user picked (installed font via the Local Font Access
    API, or an uploaded file). Returns its font-list entry."""
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "font"
    if not base.lower().endswith(FONT_EXTS):
        base += ".ttf"
    path = os.path.join(USER_FONTS, base)
    with open(path, "wb") as f:
        f.write(bytes(data))
    e = _font_entry(path)
    if e is None:
        os.remove(path)
        raise core.EngineError(400, f"{name} isn't a font file this engine can read")
    return e


def font_bytes(path):
    if not core.allowed_font(path):
        raise core.EngineError(404, "font not available")
    with open(path, "rb") as f:
        return f.read()


def _replacement(path):
    same = os.path.join(BUNDLED, os.path.basename(path))
    if os.path.isfile(same):
        return same
    return os.path.join(BUNDLED, "FreeMono.ttf")


def get_config(machine):
    """core.get_config, after swapping any font file that doesn't exist in
    this browser for a bundled one (patched into the running copy so builds
    use it) - the swaps are listed in the result as `font_substitutions`."""
    doc = core.get_config(machine)
    _master, running = core.paths(machine)
    subs = []
    for s in doc["schema"]:
        for f in s["fields"]:
            v = f["value"]
            if f["key"] in FONT_KEYS and isinstance(v, str) and v and not os.path.isfile(os.path.expanduser(v)):
                subs.append({"key": f["key"], "label": f["label"], "from": v, "to": _replacement(v)})
    if subs:
        with open(running, encoding="utf-8") as fh:
            text = fh.read()
        for sub in subs:
            text = core.tune.patch_yaml_value(text, sub["key"], sub["to"])
        with open(running, "w", encoding="utf-8") as fh:
            fh.write(text)
        doc = core.get_config(machine)
    doc["font_substitutions"] = subs
    doc["engine"] = "browser"
    return doc


def put_config(machine, body):
    core.put_config(machine, body)
    return get_config(machine)


def reset_config(machine):
    core.reset_config(machine)
    return get_config(machine)


def open_config(machine, body):
    core.open_config(machine, body)
    return get_config(machine)


def default_dir():
    return {"path": USER_FONTS}


# ------------------------------------------------------------------ jobs

def job_argv(kind, machine, body):
    """argv for a build or tool, exactly as the local engine would run it
    (minus the interpreter), plus where its outputs land."""
    cmd = core.build_command(machine, body) if kind == "build" else core.tool_command(machine, body)
    cfg, _t, _m = core.load_running(machine)
    return {"argv": [os.path.relpath(cmd[1], core.V4)] + cmd[2:],
            "stl": core.output_path(cfg), "legend": core.output_path(cfg, "_legend.svg"),
            "report": core.COVERAGE_REPORT}


def run_job(argv):
    """Runs one v4 script in-process with this argv. Returns its exit code;
    output goes to stdout, which the worker streams to the page."""
    import runpy
    import traceback
    old, cwd = sys.argv, os.getcwd()
    sys.argv = list(argv)
    os.chdir(core.V4)   # v4's scripts resolve output/ and assets/ from v4/, as when the local engine runs them
    try:
        runpy.run_path(os.path.join(core.V4, argv[0]), run_name="__main__")
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return 1
    finally:
        sys.argv = old
        os.chdir(cwd)
        sys.stdout.flush()


# Minkowski worker pool: pass 1 records every sum instead of computing it
# (the glyph passes through un-drafted so the build still completes), the
# page computes them all in parallel, pass 2 answers each sum from those
# results in the same order.
_jobs, _results = [], iter(())


def pool_record():
    import manifold3d
    _jobs.clear()

    def record(a, b):
        ma, mb = a.to_mesh(), b.to_mesh()
        _jobs.append((ma.vert_properties.ravel(), ma.tri_verts.ravel(), mb.vert_properties.ravel(), mb.tri_verts.ravel()))
        return a
    manifold3d.set_minkowski_hook(record)


def pool_jobs():
    """The recorded sums as flat float32/uint32 buffers (cheap to hand to JS)."""
    return [(gv.astype("float32").tobytes(), gf.astype("uint32").tobytes(),
             cv.astype("float32").tobytes(), cf.astype("uint32").tobytes()) for gv, gf, cv, cf in _jobs]


def pool_replay(results):
    import numpy as np
    import manifold3d
    from manifold3d import Manifold, Mesh
    global _results
    _results = iter([(np.frombuffer(bytes(v), np.float32), np.frombuffer(bytes(f), np.uint32)) for v, f in results])

    def replay(a, b):
        v, f = next(_results)
        return Manifold(mesh=Mesh(vert_properties=v, tri_verts=f))
    manifold3d.set_minkowski_hook(replay)


def pool_clear():
    import manifold3d
    manifold3d.set_minkowski_hook(None)
    _jobs.clear()


# ------------------------------------------------------------------ dispatch

_CORE = {"machines", "list_configs", "outlines", "glyphs", "profiles", "profile_save",
         "profile_rename", "profile_delete", "stl_path", "legend_path"}


def call(method, args_json):
    args = json.loads(args_json or "[]")
    try:
        fn = globals().get(method) if method not in _CORE else getattr(core, method)
        if fn is None or method.startswith("_"):
            raise core.EngineError(400, f"unknown engine call {method!r}")
        return json.dumps({"result": fn(*args)})
    except core.EngineError as e:
        return json.dumps({"error": {"status": e.status, "detail": e.detail}})
