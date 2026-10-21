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
# fonts from a folder the user synced (v5/ui/fontsync.js): copied in for this
# session only, as they're needed - a whole font library is too big to keep
# in browser storage, and the folder itself is re-read on every visit
SYNCED = "/fonts/synced"
FONT_KEYS = ("path", "font2_path", "font_path", "label_font_path", "legend_font_path", "label_font_override", "label_no_font_override")
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


def coverage_scan(body):
    """core.coverage_scan over this browser's fonts (bundled + added)."""
    return core.coverage_scan(body, fonts())


def add_synced_font(name, data):
    """A font file from the user's synced folder, for this session."""
    os.makedirs(SYNCED, exist_ok=True)
    base = os.path.basename(name).replace("/", "_") or "font.ttf"
    path = os.path.join(SYNCED, base)
    with open(path, "wb") as f:
        f.write(bytes(data))
    return {"path": path}


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


# Fonts configs name that we can't ship, mapped to a free look-alike we do.
STAND_INS = {
    "ocr-a ii regular.ttf": "OCRA-TE.ttf",   # Monotype's OCR-A II -> public-domain OCR-A, rescaled to match
}


def _font_key(name):
    """'Antikor Mono-Hairline.ttf' and 'AntikorMono-Hairline.otf' (the name a
    font added from this computer's installed fonts gets) -> one key."""
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(os.path.basename(name))[0].lower())


def _replacement(path):
    """Where a config's font that isn't in this browser comes from: the same
    font among the user's own (added or synced from a fonts folder, matched
    by file name), the same file shipped with the app, a stand-in we ship,
    else FreeMono."""
    want = _font_key(path)
    for d in (SYNCED, USER_FONTS):
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.lower().endswith(FONT_EXTS) and _font_key(fn) == want:
                    return os.path.join(d, fn)
    same = os.path.join(BUNDLED, os.path.basename(path))
    if os.path.isfile(same):
        return same
    stand_in = STAND_INS.get(os.path.basename(path).lower())
    if stand_in:
        return os.path.join(BUNDLED, stand_in)
    return os.path.join(BUNDLED, "FreeMono.ttf")


def _wanted_path(machine):
    return os.path.join(core.RUNNING_DIR or "/persist/running", f"{machine}.fonts_wanted.json")


def _font_aliases(machine):
    """{stand-in path in the config: the font path it stands in for}."""
    try:
        with open(_wanted_path(machine), encoding="utf-8") as fh:
            wanted = json.load(fh)
    except (OSError, ValueError):
        return {}
    return {w["to"]: w["from"] for w in wanted.values() if w.get("to")}


def profiles(machine):
    """core.profiles, comparing each font as the one the config asked for
    (so a profile using a font this browser stands in for still shows active)."""
    return core.profiles(machine, _font_aliases(machine))


def profile_save(machine, body):
    """Saved with the fonts the config asked for, not this browser's
    stand-ins, so the profile means the same thing everywhere."""
    core.profile_save(machine, body, _font_aliases(machine))
    return profiles(machine)


def settings_file(machine, body=None):
    """core.settings_file, noting any font that is this browser's stand-in
    for the one the config asked for."""
    body = dict(body or {})
    aliases = _font_aliases(machine)
    if aliases:
        body["font_stand_ins"] = {os.path.basename(k): v for k, v in aliases.items()}
    return core.settings_file(machine, body)


def import_settings(body):
    """core.import_settings, first putting back the fonts a browser stood in
    for (te-settings font_stand_ins) - the file then asks for the real font
    again, and this browser substitutes or finds it as for any config."""
    text = body.get("text") or ""
    for line in text.splitlines()[:5]:
        if line.startswith(core.SETTINGS_TAG):
            try:
                stand_ins = json.loads(line[len(core.SETTINGS_TAG):]).get("font_stand_ins") or {}
            except ValueError:
                stand_ins = {}
            import yaml
            cfg = yaml.safe_load(text) or {}
            for sec in cfg.values():
                if not isinstance(sec, dict):
                    continue
                for key in FONT_KEYS:
                    v = sec.get(key)
                    if isinstance(v, str) and os.path.basename(v) in stand_ins:
                        text = core.tune.patch_yaml_value(text, key, stand_ins[os.path.basename(v)])
            break
    return core.import_settings({"text": text})


def profile_rename(machine, body):
    core.profile_rename(machine, body)
    return profiles(machine)


def profile_delete(machine, body):
    core.profile_delete(machine, body)
    return profiles(machine)


def resolve_font(path):
    """{path, kind} for a font path from somewhere else (a profile, another
    computer's config): the file itself if it's here ("same"), else this
    browser's copy of the same font ("yours"/"bundled"), else the path
    unchanged with kind "missing"."""
    if path and os.path.isfile(path):
        return {"path": path, "kind": "same"}
    to = _replacement(path or "")
    if to.startswith((USER_FONTS + "/", SYNCED + "/")):
        return {"path": to, "kind": "yours"}
    if os.path.basename(to) == os.path.basename(path or ""):
        return {"path": to, "kind": "bundled"}
    return {"path": path, "kind": "missing"}


def get_config(machine):
    """core.get_config, after swapping any font file that doesn't exist in
    this browser for one that does (_replacement), patched into the running
    copy so builds use it. The font the config really asked for is
    remembered (<machine>.fonts_wanted.json), so once the user adds or
    syncs it, the stand-in is replaced by the real thing. Every swap still
    in place is listed in the result as `font_substitutions`, with `kind`:
    "yours" (the user's own copy of that font), "bundled" (the same font
    shipped with the app) or "stand-in" (a different font)."""
    doc = core.get_config(machine)
    _master, running = core.paths(machine)
    try:
        with open(_wanted_path(machine), encoding="utf-8") as fh:
            wanted = json.load(fh)
    except (OSError, ValueError):
        wanted = {}
    before = json.dumps(wanted, sort_keys=True)
    subs, patches = [], {}
    for s in doc["schema"]:
        for f in s["fields"]:
            key, v = f["key"], f["value"]
            if key not in FONT_KEYS or not isinstance(v, str) or not v:
                continue
            w = wanted.get(key)
            if not os.path.isfile(os.path.expanduser(v)):
                w = wanted[key] = {"from": v, "to": None}
            elif not w or w.get("to") != v:
                wanted.pop(key, None)                    # the user chose this font themselves
                continue
            to = _replacement(w["from"])
            if to != v:
                patches[key] = to
            w["to"] = to
            kind = ("yours" if to.startswith((USER_FONTS + "/", SYNCED + "/")) else
                    "bundled" if os.path.basename(to) == os.path.basename(w["from"]) else "stand-in")
            subs.append({"key": key, "label": f["label"], "from": w["from"], "to": to, "kind": kind})
    if patches:
        with open(running, encoding="utf-8") as fh:
            text = fh.read()
        for key, to in patches.items():
            text = core.tune.patch_yaml_value(text, key, to)
        with open(running, "w", encoding="utf-8") as fh:
            fh.write(text)
        doc = core.get_config(machine)
    if json.dumps(wanted, sort_keys=True) != before:
        with open(_wanted_path(machine), "w", encoding="utf-8") as fh:
            json.dump(wanted, fh)
    doc["font_substitutions"] = subs
    doc["engine"] = "browser"
    return doc


def put_config(machine, body):
    """core.put_config, keeping its `changed`/`errors` report (the UI needs
    both - dropping them made every save in the browser throw in the page,
    so anything chained after a save, like a build or type test, never ran)."""
    res = core.put_config(machine, body)
    return {**get_config(machine), "changed": res["changed"], "errors": res["errors"]}


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
    loops = 1
    if machine == "hammond_split":   # one character loop per rendered half
        b = cfg.get("build") or {}
        loops = int(bool(b.get("render_left", True))) + int(bool(b.get("render_right", True))) or 1
    # The worker pool helps any build that draws real draft angles - decided
    # here from the actual flags, not from target names in the page (Hammond's
    # "shuttle_with_rib" is the plain element plus a groove, and was missed).
    pool = kind == "build" and "--minkowski" in cmd and "--cut-bodies" not in cmd
    return {"argv": [os.path.relpath(cmd[1], core.V4)] + cmd[2:], "glyph_loops": loops, "pool": pool,
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
    except _StopPass1:
        return STOPPED_FOR_POOL
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return 1
    finally:
        sys.argv = old
        os.chdir(cwd)
        sys.stdout.flush()


# Minkowski worker pool. A Render's slow part is one Minkowski (draft-taper)
# sum per character. To run them in parallel:
#   pass 1  build with each sum *recorded* instead of computed (the glyph
#           passes through un-drafted). Stops as soon as the character
#           loop(s) finish - the body, supports and export of this pass would
#           be thrown away anyway;
#   pool    the page computes every recorded sum on parallel workers;
#   pass 2  build again, each sum answered from those results.
# Results are cached by the exact operand geometry, so a re-render whose
# glyphs didn't change (supports, body dimensions, quality...) is answered
# entirely from the cache in pass 1 - one pass, no pool, no rebuild.
import hashlib  # noqa: E402

_cache = {}        # operand hash -> (vertex bytes, triangle bytes)
_misses = []       # [(hash, glyph verts, glyph tris, cone verts, cone tris)]
_CACHE_MAX = 800   # entries - a few full layouts' worth
STOPPED_FOR_POOL = 99


class _StopPass1(Exception):
    """Raised at the end of the character loop(s) in pass 1."""


def _key(ma, mb):
    h = hashlib.blake2b(digest_size=16)
    for arr in (ma.vert_properties, ma.tri_verts, mb.vert_properties, mb.tri_verts):
        h.update(arr.tobytes())
    return h.hexdigest()


def _from_cache(key):
    from manifold3d import Manifold, Mesh
    import numpy as np
    v, f = _cache[key]
    return Manifold(mesh=Mesh(vert_properties=np.frombuffer(v, np.float32), tri_verts=np.frombuffer(f, np.uint32)))


def pool_record(glyph_loops=1):
    """Arm pass 1: cached sums are answered, the rest recorded; after the
    machine's `glyph_loops` character loops, stop if anything was recorded."""
    import manifold3d
    import build_log
    _misses.clear()
    seen = {"loops": 0}

    def record(a, b):
        ma, mb = a.to_mesh(), b.to_mesh()
        key = _key(ma, mb)
        if key in _cache:
            return _from_cache(key)
        _misses.append((key, ma.vert_properties.ravel(), ma.tri_verts.ravel(),
                        mb.vert_properties.ravel(), mb.tri_verts.ravel()))
        return a
    manifold3d.set_minkowski_hook(record)

    original = getattr(build_log, "_te_original_summary", build_log.progress_summary)
    build_log._te_original_summary = original

    def summary(*args, **kwargs):
        original(*args, **kwargs)
        seen["loops"] += 1
        if seen["loops"] == glyph_loops:
            if _misses:
                raise _StopPass1()
            # said now, not after the run: the worker turns it into the
            # progress bar's "one pass" stage (engine_worker.js ONE_PASS)
            print("--- every draft angle came from the cache: one pass, no rebuild", flush=True)
    build_log.progress_summary = summary


def pool_jobs():
    """The recorded sums as flat float32/uint32 buffers (cheap to hand to JS)."""
    return [(gv.astype("float32").tobytes(), gf.astype("uint32").tobytes(),
             cv.astype("float32").tobytes(), cf.astype("uint32").tobytes()) for _k, gv, gf, cv, cf in _misses]


def pool_replay(results):
    """Arm pass 2: store the pool's results in the cache, then answer every
    sum from it (anything not there - recorded after pass 1 stopped - is
    computed directly, so nothing is ever missed)."""
    import manifold3d
    import build_log
    if hasattr(build_log, "_te_original_summary"):   # pass 2 runs to the end
        build_log.progress_summary = build_log._te_original_summary
    if len(_cache) + len(results) > _CACHE_MAX:
        _cache.clear()
    for (key, *_rest), (v, f) in zip(_misses, results):
        _cache[key] = (bytes(v), bytes(f))

    def replay(a, b):
        key = _key(a.to_mesh(), b.to_mesh())
        return _from_cache(key) if key in _cache else None
    manifold3d.set_minkowski_hook(replay)


def pool_clear():
    import manifold3d
    import build_log
    manifold3d.set_minkowski_hook(None)
    if hasattr(build_log, "_te_original_summary"):
        build_log.progress_summary = build_log._te_original_summary
    _misses.clear()


# ------------------------------------------------------------------ dispatch

_CORE = {"machines", "list_configs", "outlines", "glyphs", "stl_path", "legend_path"}


def call(method, args_json):
    args = json.loads(args_json or "[]")
    try:
        fn = globals().get(method) if method not in _CORE else getattr(core, method)
        if fn is None or method.startswith("_"):
            raise core.EngineError(400, f"unknown engine call {method!r}")
        return json.dumps({"result": fn(*args)})
    except core.EngineError as e:
        return json.dumps({"error": {"status": e.status, "detail": e.detail}})
