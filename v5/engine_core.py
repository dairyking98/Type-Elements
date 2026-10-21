"""
v5 engine core - everything the engine API does, as plain functions with no
web framework attached, shared by both engine implementations:

  * v5/server.py   - the local engine (FastAPI over HTTP, builds run as
                     subprocesses with v4's own scripts)
  * the in-browser engine - Pyodide in a Web Worker (v5/ui/engine_worker.js),
                     builds run in-process with the same argv

Every function maps to an endpoint in ENGINE_API.md and raises EngineError
(an HTTP-style status + message) on bad input. Paths come from configure():
the v4 directory and the folder of master configs - the real repo locally,
an in-memory filesystem in the browser.

Reuses v4's lib/tune_tables.py (tune.py's field tables, comment-preserving
YAML patchers, running-config migration) - no logic is copied from v4.
"""
import os
import re
import shutil
import sys
from datetime import datetime

import yaml

V4 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v4")
CONFIG_DIR = os.path.join(V4, "config")
COVERAGE_REPORT = os.path.join(V4, "output", "font_coverage_report.md")
RUNNING_DIR = None    # None = running copies sit next to their master (tune.py's convention)
PROFILES_DIR = None   # None = <config dir>/profiles (tune.py's convention)


def configure(v4_dir=None, config_dir=None, running_dir=None, profiles_dir=None):
    """Point the core at a v4 tree (and optionally a different folder of
    master configs) and make v4's modules importable. running_dir /
    profiles_dir let the in-browser engine keep the user's own state in
    persistent browser storage while the masters ship with the site."""
    global V4, CONFIG_DIR, COVERAGE_REPORT, RUNNING_DIR, PROFILES_DIR
    if v4_dir:
        V4 = os.path.abspath(v4_dir)
        CONFIG_DIR = os.path.join(V4, "config")
    if config_dir:
        CONFIG_DIR = os.path.abspath(config_dir)
    if running_dir:
        RUNNING_DIR = os.path.abspath(running_dir)
        os.makedirs(RUNNING_DIR, exist_ok=True)
    if profiles_dir:
        PROFILES_DIR = os.path.abspath(profiles_dir)
    COVERAGE_REPORT = os.path.join(V4, "output", "font_coverage_report.md")
    for p in (os.path.join(V4, "lib"), V4):
        if p not in sys.path:
            sys.path.insert(0, p)


configure()

from lib import tune_tables as tune  # noqa: E402
import font_coverage  # noqa: E402
from lib import font_profiles  # noqa: E402
from lib.layouts import (LAYOUT_PRESETS_BY_MACHINE, LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE,  # noqa: E402
                         LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE, LAYOUT_PICKER_HELP)


class EngineError(Exception):
    """An HTTP-style failure: status (400 bad input, 404 not found, 409 busy)
    plus a message for the user."""

    def __init__(self, status, detail):
        super().__init__(detail)
        self.status, self.detail = status, detail


FONT_EXTS = (".ttf", ".otf", ".ttc", ".otc")
TYPE_NAMES = {bool: "bool", int: "int", float: "float", str: "str"}






# ------------------------------------------------------------------ helpers

MASTER_OVERRIDE = {}   # machine -> a different master opened with "Open config" (tune.py's Browse)


def paths(machine):
    """(master, running). Running is always <master's dir>/<machine>.running.yaml
    - tune.py's convention, so opening a config elsewhere gets its own
    running copy next to it."""
    if machine not in tune.MACHINES:
        raise EngineError(404, f"unknown machine {machine!r}")
    if machine in MASTER_OVERRIDE:
        master = MASTER_OVERRIDE[machine]
        return master, os.path.join(os.path.dirname(master), f"{machine}.running.yaml")
    master = os.path.join(CONFIG_DIR, f"{machine}.yaml")
    if not os.path.isfile(master):
        raise EngineError(404, f"no config for {machine!r} in {CONFIG_DIR}")
    return master, os.path.join(RUNNING_DIR or CONFIG_DIR, f"{machine}.running.yaml")


def load_running(machine):
    """tune.py's convention: a per-machine running copy, bootstrapped from
    the master and back-filled with keys the master gained since."""
    master, running = paths(machine)
    if not os.path.exists(running):
        shutil.copyfile(master, running)
    migrated = tune.migrate_running_config(master, running)
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
    "Per-row and per-half values": {"level": "advanced", "text":
        "ADVANCED - real machine measurements, one value per row or per shuttle half. Rarely need changing."},
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
        build += [_f("orientation", ["resin", "orientation"], "select", "Print orientation",
                     "How the shuttle sits on the build plate: vertical stands it on one end; horizontal prints it flat, held up by the method below.",
                     [("Vertical", "vertical"), ("Horizontal", "horizontal")]),
                  _f("horizontal_method", ["resin", "horizontal_method"], "select", "Horizontal support method",
                     "For a flat-printed shuttle: support its outer wall with a breakaway cut-groove ring, or with resin rods.",
                     [("Cut groove", "cut_groove"), ("Resin rod", "resin_rod")])]
    if machine == "mignon":
        build += [_f("orientation", ["resin", "orientation"], "select", "Print orientation",
                     "Which end of the Mignon element sits on the build plate: upside down puts the label end down, right side up the shaft end.",
                     [("Upside down", "upside_down"), ("Right side up", "right_side_up")])]
    if machine == "hammond_split":
        build += [_f("render_left", ["build", "render_left"], "bool", "Render left half",
                     "Include the left half of the split shuttle in the build. Turn one half off to print or check them separately."),
                  _f("render_right", ["build", "render_right"], "bool", "Render right half",
                     "Include the right half of the split shuttle in the build.")]
    secs["Build"] = build
    lay = cfg.get("layout") or {}
    if "baseline_row" in lay:
        secs["Row baselines"] = [
            _f("baseline_row", ["layout", "baseline_row"], "floatlist", "Baseline per row (mm)",
               "Height of each row's text baseline on the element, top row first. Find the right numbers with a calibration print rather than guessing."),
            _f("cutout_row", ["layout", "cutout_row"], "floatlist", "Platen cutout per row (mm)",
               "Height where each row's curved platen cutout is centred, top row first. It shapes the character faces to match the platen.")]
    if "row_latitudes" in lay:          # the Selectric balls: their own per-row placement, in degrees
        secs["Row baselines"] = [
            _f("row_latitudes", ["layout", "row_latitudes"], "floatlist", "Row latitude (deg)",
               "Where each row of characters sits on the ball, in degrees above (+) or below (-) the equator, top row first."),
            _f("baseline_longitude_offsets", ["layout", "baseline_longitude_offsets"], "floatlist", "Baseline offset per row (deg)",
               "Nudges each row's characters up (+) or down (-) on the ball - the per-row baseline, like the other machines' row baselines."),
            _f("platen_longitude_offsets", ["layout", "platen_longitude_offsets"], "floatlist", "Platen cutout offset per row (deg)",
               "Moves each row's platen-shaped face curve up or down relative to its characters - the per-row platen cutout."),
            _f("minkowski_longitudinal_offsets", ["layout", "minkowski_longitudinal_offsets"], "floatlist", "Draft offset per row (deg)",
               "Tilts each row's draft taper up or down. 0 keeps the taper square to the ball.")]
    el = cfg.get("element") or {}
    lists = []
    if "alignment_hole_height" in el:
        lists.append(_f("alignment_hole_height", ["element", "alignment_hole_height"], "floatlist", "Alignment hole height (mm)",
                        "Height of the alignment hole for each row (lowercase, uppercase, figures). Real machine measurements."))
    if "pin_theta" in el:
        lists.append(_f("pin_theta", ["element", "pin_theta"], "floatlist", "Pin hole angle (deg)",
                        "Angle of the pin hole on the left and right halves. Real machine measurements."))
    if "tube_od_mm" in el:
        lists.append(_f("tube_od_mm", ["element", "tube_od_mm"], "floatlist", "Tube diameter (mm)",
                        "Outer diameter of the hub tube on the left and right halves. Real machine measurements."))
    if lists:
        secs["Per-row and per-half values"] = lists
    cos = cfg.get("cosmetics") or {}
    if "band_z_offsets" in cos:
        secs["Bands"] = [
            _f("band_z_offsets", ["cosmetics", "band_z_offsets"], "floatlist", "Band offsets (mm)",
               "Height of each decorative band on the element body."),
            _f("band_heights", ["cosmetics", "band_heights"], "floatlist", "Band heights (mm)",
               "How tall each decorative band is.")]
    if "Legend" in tune.SECTIONS_BY_MACHINE.get(machine, {}) and get_path(cfg, ["legend", "background"]) is not None:
        secs["Legend output"] = [_f("background", ["legend", "background"], "select", "Legend background",
                                    "Leave the legend sheet transparent, or give it a white background for printing on coloured card.",
                                    [("Transparent", "transparent"), ("White", "white")])]
    tt = cfg.get("type_test") or {}
    if tt:
        f = [_f("type_test_text", ["type_test", "text"], "textblock", "Test text",
                "The text printed on the flat type-test plate - use it to check spacing, alignment and size before cutting a whole element.")]
        if machine == "selectric_composer" and "units_per_inch" in tt:
            f.append(_f("units_per_inch", ["type_test", "units_per_inch"], "float", "Units per inch",
                              "Composer escapement units per inch for the type-test plate; each character advances by its own unit count."))
        elif "cpi" in tt:
            f.append(_f("cpi", ["type_test", "cpi"], "float", "Characters per inch",
                              "Character spacing on the type-test plate. 10 = pica, 12 = elite."))
        if "lpi" in tt:
            f.append(_f("lpi", ["type_test", "lpi"], "float", "Lines per inch",
                              "Line spacing on the type-test plate. 6 is standard single spacing."))
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


# ------------------------------------------------------------------ layout views
# The same layout.rows slots, arranged two ways for the Layout page:
#   "keyboard" - the typewriter's keys, each with its shift levels (or, on
#                the Mignon, its index card);
#   "element"  - where each character physically sits on the wheel / ball /
#                shuttle.
# Every cell is a [row, index] reference into layout.rows, so either view
# edits the same characters. Derived from each machine's own build
# mapping (placement_map, char_legend, hemisphere maps, the Hammond legend's
# key grid); a machine whose keyboard plate isn't known (Blickensderfer,
# Helios) gets the element view only. Key-row splits marked inferred were
# read from the layouts' structure, not from a transcribed keyboard.

_LEVELS = ["lowercase", "UPPERCASE", "figures", "math"]


# Blickensderfer: which wheel column each key strikes depends on the
# keyboard, and the two keyboards differ (Leonard, 2026-10-20). Key rows,
# top to bottom, all centred:
#   Scientific (DHIATENSOR):  ZXKGBVQJ / .PWFULCMY, / DHIATENSOR
#   Universal (QWERTY):       QWERTYUIOP / ASDFGHJKL. / ZXCVBNM,
# read against the DHIATENSOR and QWERTY wheels. The keyboard follows the
# layout's preset - for edited rows, the preset they're closest to
# (CHARIENSTU and the other language wheels are Scientific-keyboard ones).
_BLICK_KEY_ROWS = {
    "scientific": [[0, 1, 2, 3, 24, 25, 26, 27], [4, 5, 6, 7, 8, 19, 20, 21, 22, 23], list(range(9, 19))],
    "universal": [[0, 1, 2, 3, 4, 23, 24, 25, 26, 27], [5, 6, 7, 8, 9, 18, 19, 20, 21, 22], list(range(10, 18))],
}


def blick_keyboard(lay):
    rows = [r for r in (lay.get("rows") or []) if isinstance(r, str)]
    best, score = "universal", -1
    for name, preset in LAYOUT_PRESETS_BY_MACHINE.get("blickensderfer", {}).items():
        sc = sum(a == b for r, pr in zip(rows, preset) for a, b in zip(r, pr))
        if sc > score:
            best, score = ("universal" if name.upper().startswith("QWERTY") else "scientific"), sc
    return best


def _blick_keyboard(lay, rows, key):
    """Both keyboards' key rows ("variants"), so the page can switch the
    moment the layout's preset changes, saved or not; "rows" is the one for
    the saved config. "variant_of_preset" maps each preset to its keyboard."""
    kb = blick_keyboard(lay)
    variants = {name: [[key(i) for i in krow] for krow in krows] for name, krows in _BLICK_KEY_ROWS.items()}
    return {"id": "keyboard", "label": "Keyboard order", "kind": "keys", "align": "center",
            "rows": variants[kb], "variant": kb, "variants": variants,
            "variant_labels": {"scientific": "Scientific (DHIATENSOR) keyboard.", "universal": "Universal (QWERTY) keyboard."},
            "variant_of_preset": {n: ("universal" if n.upper().startswith("QWERTY") else "scientific")
                                  for n in LAYOUT_PRESETS_BY_MACHINE.get("blickensderfer", {})},
            "levels": _LEVELS[:len(rows)], "note": None}


def _hammond_keyboard(element_order, key, n_rows, grid_slot):
    """The Hammond's keyboard depends on the shuttle's keyboard (Leonard,
    2026-10-20), so both are sent as variants, picked by the layout's preset:
      Universal - a regular 3-row QWERTY keyboard, 10 keys a row: key n
                  (row n % 3, column n // 3, the legend's grid) strikes
                  grid_slot(n);
      Ideal     - the curved two-row staggered keyboard: the keys follow
                  the shuttle's element order from its Q end, alternating
                  bottom, top, bottom, ... with Cap (top), the space bar
                  (bottom) and Fig (top) between the two halves, the second
                  half carrying straight on after Fig.
    Items are slot keys or {"label"} for the shift keys/space bar."""
    seq = [key(i) for i in element_order[:15]] + [{"label": "Cap"}, {"label": "Space"}, {"label": "Fig"}] \
        + [key(i) for i in element_order[15:]]
    variants = {
        "universal": {"rows": [[key(grid_slot(3 * c + kr)) for c in range(10)] for kr in range(3)], "align": None},
        "ideal": {"rows": [seq[1::2], seq[0::2]], "align": "stagger"},
    }
    presets = LAYOUT_PRESETS_BY_MACHINE.get("hammond", {})
    return {"id": "keyboard", "label": "Keyboard order", "kind": "keys", "levels": _LEVELS[:n_rows],
            "variants": variants, "variant": "universal", "rows": variants["universal"]["rows"],
            "variant_labels": {"universal": "Universal keyboard: three QWERTY rows.",
                               "ideal": "Ideal keyboard: two curved, staggered rows in shuttle order from the Q end."},
            "variant_of_preset": {n: ("ideal" if n.startswith("Ideal") else "universal")
                                  for n in list(presets) + list(LAYOUT_PRESETS_BY_MACHINE.get("hammond_split", {}))},
            "note": None}


def layout_views(machine, cfg):
    lay = cfg.get("layout") or {}
    rows = [list(r) for r in (lay.get("rows") or []) if isinstance(r, str)]
    if not rows:
        return []
    n_rows, width = len(rows), min(len(r) for r in rows)
    views = []

    def key(slot, levels=None):
        return [[r, slot] for r in (levels if levels is not None else range(n_rows))]

    def keyboard(splits, slot_of, note=None):
        out, k = [], 0
        for length in splits:
            out.append([key(slot_of(k + j)) for j in range(length)])
            k += length
        return {"id": "keyboard", "label": "Keyboard order", "kind": "keys", "rows": out,
                "levels": _LEVELS[:n_rows], "note": note}

    def element(order, rows_top_down=None, note=None, labels=None):
        rr = rows_top_down if rows_top_down is not None else list(range(n_rows))
        return {"id": "element", "label": "Element order", "kind": "grid",
                "rows": [[[r, i] for i in order] for r in rr],
                "row_labels": labels or [_LEVELS[r] if r < 4 else f"Row {r + 1}" for r in rr], "note": note}

    pm = lay.get("placement_map")
    legend = lay.get("char_legend") or list(range(width))

    if machine == "blickensderfer" and width == 28:
        views.append(_blick_keyboard(lay, rows, key))
    if machine in ("blickensderfer", "postal", "bennett", "helios") and pm and len(pm) == width:
        inv = [0] * width
        for slot, pos in enumerate(pm):
            inv[pos] = slot
        views.append(element([legend[inv[p]] for p in range(width)],
                             note="Around the wheel from the starting position; rows top to bottom."))
        if machine == "postal" and width == 28:
            inv_m = [14, 17, 20, 23, 26, 1, 4, 7, 10, 13, 15, 18, 21, 24, 27, 2, 5, 8, 11,
                     16, 19, 22, 25, 0, 3, 6, 9, 12]
            views.insert(0, keyboard([10, 9, 9], lambda k: inv_m[k]))
        elif machine == "helios" and width == 21:
            # two staggered rows (Leonard, 2026-10-20): read in a zigzag,
            # top, bottom, top, ... from the top-left w - "waesr...mp" - the
            # top row is element slots 0-10 (w ... p), the bottom row, half a
            # key in, slots 11-20 (a ... m)
            views.insert(0, {"id": "keyboard", "label": "Keyboard order", "kind": "keys", "align": "stagger",
                             "offset_row": 1, "levels": ["lowercase", "UPPERCASE", "level 3", "level 4"][:n_rows],
                             "rows": [[key(i) for i in range(0, 11)], [key(i) for i in range(11, 21)]]})
        elif machine == "bennett" and width == 28:
            # a grid of 10 x 3; the top row has the space bar in the two
            # places between R and U (None = no key)
            top = [0, 1, 2, 3, None, None, 4, 5, 6, 7]
            views.insert(0, {"id": "keyboard", "label": "Keyboard order", "kind": "keys", "levels": _LEVELS[:n_rows],
                             "rows": [[key(i) if i is not None else None for i in top],
                                      [key(i) for i in range(8, 18)], [key(i) for i in range(18, 28)]],
                             "align": "grid", "note": "The gap in the top row is the space bar."})
    elif machine == "hammond" and pm and len(pm) == width:
        order = sorted(range(width), key=lambda i: -pm[i])          # +angle first, like the catalog
        views.append(element(order, note="Across the shuttle from the Q end; rows top to bottom."))
        if width == 30:
            views.insert(0, _hammond_keyboard(order, key, n_rows, lambda n: 29 - n))
    elif machine == "hammond_split":
        views.append(element(list(range(width)), note="Across the shuttle from the Q end; rows top to bottom."))
        if width == 30:
            views.insert(0, _hammond_keyboard(list(range(width)), key, n_rows, lambda n: n))
    elif machine == "mignon":
        fill = (cfg.get("legend") or {}).get("circle_fill") or []
        shifted = [[bool(fill[r][i]) if r < len(fill) and i < len(fill[r]) else False for i in range(width)]
                   for r in range(n_rows)]
        # read as the index card shows it - each stored row right to left
        # (mignon_legend draws cell i at column 11 - i; confirmed by Leonard)
        views.append({"id": "keyboard", "label": "Index order", "kind": "grid",
                      "rows": [[[r, i] for i in reversed(range(width))] for r in range(n_rows)],
                      "row_labels": [f"Row {r + 1}" for r in range(n_rows)], "shifted": shifted,
                      "note": "As on the index card; a dot marks characters typed with Shift."})
        views.append(element([legend[p] for p in range(width)], rows_top_down=list(range(n_rows))[::-1],
                             labels=[f"Row {r + 1}" for r in range(n_rows)][::-1],
                             note="Around the element; top of the element first."))
    elif machine in ("selectric12", "selectric3", "selectric_composer") and n_rows == 8:
        from lib.layouts import selectric12_layout, selectric3_layout, selectric_composer_layout
        if machine == "selectric_composer":
            mp, cols = selectric_composer_layout.COMPOSER_HEMISPHERE_MAP, 11
        else:
            mod = selectric12_layout if machine == "selectric12" else selectric3_layout
            mp = mod.HEMISPHERE_MAPS.get(lay.get("hemisphere_map") or "us") or next(iter(mod.HEMISPHERE_MAPS.values()))
            cols = 11 if machine == "selectric12" else 12
        flat = [(r, i) for r in range(4) for i in range(len(rows[r]))]
        if len(mp) == len(flat) == 4 * cols:
            inv = {h: k for k, h in enumerate(mp)}
            ball = []
            for lat in range(4):
                line = []
                for L in range(2 * cols):
                    case, col = divmod(L, cols)
                    r, i = flat[inv[lat * cols + col]]
                    line.append([r + 4 * case, i])
                ball.append(line)
            views.append({"id": "element", "label": "Element order", "kind": "grid", "rows": ball,
                          "row_labels": ["Top row", "Row 2", "Row 3", "Bottom row"],
                          "note": "Around the ball: the lowercase half, then the uppercase half."})
        views.insert(0, {"id": "keyboard", "label": "Keyboard order", "kind": "keys",
                         "rows": [[[[r, i], [r + 4, i]] for i in range(len(rows[r]))] for r in range(4)],
                         "levels": ["lowercase", "UPPERCASE"], "note": None})
    return views


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

def machines():
    groups = []
    for name, keys in tune.MACHINE_CATEGORIES:
        groups.append({"group": name, "machines": [
            {"key": k, "label": tune.MACHINES[k][0],
             "available": os.path.isfile(os.path.join(CONFIG_DIR, f"{k}.yaml")),
             # e.g. Selectric III: "UNTESTED - notch/teeth fitment" (tune.py's MACHINE_PICKER_WARNINGS)
             "warning": (tune.MACHINE_PICKER_WARNINGS[k][0].lstrip("⚠ ").strip()
                         if k in tune.MACHINE_PICKER_WARNINGS else None)}
            for k in keys if k in tune.MACHINES]})
    return {"groups": groups}


def export_name(machine, cfg, target=None):
    """Download/save-copy file name stem: machine, font, size, plus the build
    target when it isn't the plain element - e.g.
    selectric12_FreeSans_2.4mm or hammond_IosevkaTermSlab_3.1mm_calibration.
    The caller appends the build's date/time and extension."""
    font = cfg.get("font") or {}
    stem = os.path.splitext(os.path.basename(str(font.get("path") or "")))[0]
    stem = re.sub(r"\(.*?\)", "", stem)                     # "FreeMono (Leonard Chau)" -> "FreeMono"
    stem = re.sub(r"[^A-Za-z0-9-]", "", stem.replace(" - ", "-"))[:24].strip("-") or "font"
    if font.get("size_mm") is not None:
        size = f"{float(font['size_mm']):g}mm"
    elif font.get("composer_cap_height") is not None:       # Composer sizes type by cap height, in points
        size = f"{float(font['composer_cap_height']):g}pt"
    else:
        size = None
    parts = [machine, stem] + ([size] if size else [])
    if target and target not in ("element", "normal"):
        parts.append(target)
    return "_".join(parts)


def get_config(machine):
    cfg, _text, migrated = load_running(machine)
    master, running = paths(machine)
    targets, target = build_targets(machine, cfg)
    warning = tune.MACHINE_PICKER_WARNINGS.get(machine)
    lay = cfg.get("layout") or {}
    presets = LAYOUT_PRESETS_BY_MACHINE.get(machine, {})
    current_preset = next((n for n, rows in presets.items() if rows == lay.get("rows")), None)
    return {"machine": machine, "label": tune.MACHINES[machine][0], "cfg": cfg,
            "schema": schema(machine, cfg), "migrated": migrated, "section_targets": tune.SECTION_TARGETS,
            "layout_views": layout_views(machine, cfg),
            "running_path": running, "master_path": master,
            "presets": presets, "current_preset": current_preset,
            # baselines a preset sets when saved (Hammond: a 4-row Math preset adds a 4th)
            "preset_baselines": LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE.get(machine, {}),
            "layout_help": LAYOUT_PICKER_HELP.get(machine),
            # Selectric rows are flat-indexed onto a fixed hemisphere: every row
            # must keep its exact length (tune.py refuses the edit otherwise)
            "fixed_row_lengths": "rows" in lay and "placement_map" not in lay,
            "row_cap": len(lay["placement_map"]) if "placement_map" in lay else None,
            "targets": targets, "target": target,
            "export_name": export_name(machine, cfg, target),
            "warning": {"short": warning[0], "long": warning[1]} if isinstance(warning, tuple) else warning}


def put_config(machine, body):
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
                given = body.get("values") or {}
                for key in ("baseline_row", "cutout_row"):   # values sent with the save win over the preset's
                    if seeds and key not in given:
                        text = tune.patch_yaml_inline_list(text, key, seeds)
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


def list_configs(machine):
    master, _r = paths(machine)
    return {"current": master, "default": os.path.join(CONFIG_DIR, f"{machine}.yaml"),
            "configs": config_candidates(machine)}


def open_config(machine, body):
    path = os.path.abspath(body.get("path") or "")
    if path not in {c["path"] for c in config_candidates(machine)}:
        raise EngineError(400, "not a config for this machine")
    if path == os.path.join(CONFIG_DIR, f"{machine}.yaml"):
        MASTER_OVERRIDE.pop(machine, None)
    else:
        MASTER_OVERRIDE[machine] = path
    return get_config(machine)


def reset_config(machine):
    master, running = paths(machine)
    shutil.copyfile(master, running)
    return get_config(machine)


def _added_fonts_dir():
    return os.path.join(V4, "output", "added_fonts")


def fonts():
    """The fonts this engine can build with: the computer's installed fonts,
    plus any added through the page (add_font_file)."""
    from lib.system_fonts import list_system_fonts
    out = [{"path": e.path, "family": e.family, "style": e.style} for e in list_system_fonts()]
    d = _added_fonts_dir()
    if os.path.isdir(d):
        fix_collections(d)
        have = {e["path"] for e in out}
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if fn.lower().endswith(FONT_EXTS) and p not in have:
                out.append({"path": p, **_font_names(p), "source": "yours"})
    return out


def _font_names(path):
    try:
        from fontTools.ttLib import TTFont
        n = TTFont(path, lazy=True, fontNumber=0)["name"]
        return {"family": n.getBestFamilyName() or os.path.basename(path), "style": n.getBestSubFamilyName() or ""}
    except Exception:
        return {"family": os.path.splitext(os.path.basename(path))[0], "style": ""}


def split_collection(name, data):
    """A font collection (.ttc/.otc - Windows ships Cambria Math inside
    cambria.ttc, beside Cambria) split into its faces: [(file name, bytes,
    PostScript name)]. Anything else comes back as the one file it is.
    Saving a whole collection would leave every reader on its FIRST face -
    picking 'Cambria Math' would quietly build in plain Cambria."""
    import io
    if data[:4] != b"ttcf":
        return [(name, data, None)]
    from fontTools.ttLib import TTCollection
    out = []
    for face in TTCollection(io.BytesIO(data)).fonts:
        ps = face["name"].getDebugName(6) or face["name"].getBestFullName() or f"face{len(out)}"
        buf = io.BytesIO()
        face.save(buf)
        out.append((ps + ".ttf", buf.getvalue(), ps))
    return out


def pick_face(name, data):
    """The faces split_collection() finds, and the one `name` asks for (its
    stem matched to a face's PostScript name, e.g. 'CambriaMath.ttf' - the
    name a browser's installed font arrives with), else the first."""
    faces = split_collection(name, data)
    stem = re.sub(r"[^a-z0-9]", "", os.path.splitext(os.path.basename(name or ""))[0].lower())
    want = next((f for f in faces if f[2] and re.sub(r"[^a-z0-9]", "", f[2].lower()) == stem), faces[0])
    return faces, want


def fix_collections(folder):
    """Repair fonts saved before collections were split: any whole .ttc kept
    under a single-font name (e.g. 'CambriaMath.ttf' holding all of
    cambria.ttc) becomes just the face its name asks for - same file name,
    so configs pointing at it keep working - and the other faces are added
    beside it. Returns how many were fixed."""
    fixed = 0
    if not os.path.isdir(folder):
        return 0
    for fn in sorted(os.listdir(folder)):
        path = os.path.join(folder, fn)
        try:
            with open(path, "rb") as f:
                if f.read(4) != b"ttcf":
                    continue
            with open(path, "rb") as f:
                faces, want = pick_face(fn, f.read())
        except Exception:
            continue
        for fname, fdata, _ps in faces:
            other = os.path.join(folder, re.sub(r"[^A-Za-z0-9._ -]+", "_", fname))
            if fname != want[0] and not os.path.exists(other):
                with open(other, "wb") as f:
                    f.write(fdata)
        with open(path, "wb") as f:
            f.write(want[1])
        fixed += 1
    return fixed


def add_font_file(name, data):
    """A font file sent from the page (uploaded, or one of the browser
    computer's installed fonts) - kept with this engine so builds can use it.
    Returns its font-list entry."""
    d = _added_fonts_dir()
    os.makedirs(d, exist_ok=True)
    try:
        faces, want = pick_face(name, data)
    except Exception:
        raise EngineError(400, f"{name} isn't a font file this engine can read")
    chosen = None
    for fname, fdata, _ps in faces:          # a collection adds every face; the one asked for is chosen
        base = re.sub(r"[^A-Za-z0-9._ -]+", "_", os.path.basename(fname or "")).strip(" ._") or "font"
        if not base.lower().endswith(FONT_EXTS):
            base += ".ttf"
        path = os.path.join(d, base)
        with open(path, "wb") as f:
            f.write(fdata)
        try:
            from fontTools.ttLib import TTFont
            TTFont(path, lazy=True, fontNumber=0)["cmap"]
        except Exception:
            os.remove(path)
            continue
        if fname == want[0]:
            chosen = path
    if not chosen:
        raise EngineError(400, f"{name} isn't a font file this engine can read")
    return {"path": chosen, **_font_names(chosen), "source": "yours"}


def coverage_scan(body, font_list=None):
    """Which characters each of this engine's fonts has - the same fonts
    the font picker lists (font_list, else fonts()), or just body["paths"].
    Reads each font's character map only (fontTools, lazy), so a whole
    library is quick. -> [{path, family, style, missing}], missing being
    the characters of body["chars"] (whitespace ignored) the font lacks;
    unreadable files are left out."""
    from fontTools.ttLib import TTFont
    chars = [c for c in dict.fromkeys(body.get("chars") or "") if not c.isspace()]
    entries = font_list if font_list is not None else fonts()
    if body.get("paths"):
        want = set(body["paths"])
        entries = [e for e in entries if e["path"] in want] + \
                  [{"path": p, "family": os.path.basename(p), "style": ""} for p in want if p not in {e["path"] for e in entries}]
    out = []
    for e in entries:
        try:
            mtime = os.path.getmtime(e["path"])
            hit = _CMAP_CACHE.get(e["path"])
            if not hit or hit[0] != mtime:          # read once per file version
                hit = _CMAP_CACHE[e["path"]] = (mtime, frozenset((TTFont(e["path"], lazy=True, fontNumber=0).getBestCmap() or {}).keys()))
            cmap = hit[1]
        except Exception:
            continue
        out.append({**e, "missing": "".join(c for c in chars if ord(c) not in cmap)})
    return out


_CMAP_CACHE = {}   # font path -> (mtime, codepoints) for coverage_scan


def default_dir():
    from lib.system_fonts import default_font_dir
    return {"path": default_font_dir()}


def outline_svg(points, tags, contours):
    """SVG path data for one FreeType outline (font units, y up): on-curve
    points (tag bit 0), quadratic off-curve (tag 0, consecutive ones imply
    an on-curve midpoint) and cubic off-curve pairs (tag 2). Walks the raw
    arrays instead of FreeType's decompose(), so it also works with the
    browser's fontTools-backed freetype adapter."""
    d, start = [], 0
    for end in contours:
        pts = [tuple(p) for p in points[start:end + 1]]
        tg = [t & 3 for t in tags[start:end + 1]]
        start = end + 1
        n = len(pts)
        if not n:
            continue
        on = [t == 1 for t in tg]
        if not any(on):   # all-off-curve TrueType contour: start at an implied midpoint
            pts = [((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2)] + pts
            tg, on, n = [1] + tg, [True] + on, n + 1
        k = on.index(True)
        pts, tg = pts[k:] + pts[:k], tg[k:] + tg[:k]
        d.append(f"M{pts[0][0]} {pts[0][1]}")
        i = 1
        while i <= n:
            p, t = pts[i % n], tg[i % n]
            if t == 1:
                d.append(f"L{p[0]} {p[1]}")
                i += 1
            elif t == 2:   # cubic: two controls then an on-curve point
                c2, e = pts[(i + 1) % n], pts[(i + 2) % n]
                d.append(f"C{p[0]} {p[1]} {c2[0]} {c2[1]} {e[0]} {e[1]}")
                i += 3
            else:          # quadratic, with implied midpoints between consecutive controls
                nxt, nt = pts[(i + 1) % n], tg[(i + 1) % n]
                if nt == 1:
                    d.append(f"Q{p[0]} {p[1]} {nxt[0]} {nxt[1]}")
                    i += 2
                else:
                    mid = ((p[0] + nxt[0]) / 2, (p[1] + nxt[1]) / 2)
                    d.append(f"Q{p[0]} {p[1]} {mid[0]} {mid[1]}")
                    i += 1
        d.append("Z")
    return " ".join(d)


def outlines(body):
    """Glyph outlines as SVG path data, read with FreeType - the same
    library the build uses. The UI draws these when the browser refuses a
    font file (Chrome's sanitizer rejects some fonts FreeType reads fine,
    e.g. OCR-A II), so every preview still shows the real shapes.
    Coordinates are font units, y up; the UI flips them."""
    import freetype
    path = os.path.expanduser(body.get("font") or "")
    if not allowed_font(path):
        raise EngineError(404, "font not available")
    face = freetype.Face(path)
    out = {}
    for ch in dict.fromkeys(body.get("chars") or ""):
        gid = face.get_char_index(ord(ch))
        if gid == 0:
            out[ch] = None
            continue
        face.load_glyph(gid, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
        o = face.glyph.outline
        out[ch] = {"d": outline_svg(list(o.points), list(o.tags), list(o.contours)), "adv": face.glyph.advance.x}
    return {"upem": face.units_per_EM, "ascender": face.ascender, "descender": face.descender, "glyphs": out}


def glyphs(body):
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


def output_path(cfg, suffix=None):
    out = cfg.get("output") or {}
    p = os.path.join(V4, out.get("directory", "output"), out.get("stl_name", "out.stl"))
    return p if suffix is None else os.path.splitext(p)[0] + suffix


def type_test_command(machine, cfg):
    """Mirrors tune.py's action_render_type_test flag-for-flag, reading the
    saved running config."""
    _master, running = paths(machine)
    v = {f["key"]: f["value"] for s in schema(machine, cfg) for f in s["fields"]}
    tt = cfg.get("type_test") or {}
    text = str(tt.get("text") or "").strip("\n")
    if not text.strip():
        raise EngineError(400, "type test text is empty")
    size = v.get("size_mm")
    if size is None and v.get("composer_cap_height") is not None:
        size = float(v["composer_cap_height"]) / 2.834
    cmd = [sys.executable, os.path.join(V4, "type_test.py"), text,
           "--cpi", str(tt.get("cpi", 10.0)), "--lpi", str(tt.get("lpi", 6.0)),
           "--font-path", str(v.get("path")), "--font-size-mm", str(size)]
    flags = {"mode": "--align-mode", "center_offset_mm": "--center-offset-mm", "left_offset_mm": "--left-offset-mm",
             "modified_left_offset_mm": "--modified-left-offset-mm", "modified_right_offset_mm": "--modified-right-offset-mm",
             "underscore_lift_mm": "--underscore-lift-mm"}
    for key, flag in flags.items():
        if v.get(key) is not None:
            cmd += [flag, str(v[key])]
    if "caret_drop_mm" in v:   # the total, auto-drop included - same as the element gets
        import glyph_poc
        cmd += ["--caret-drop-mm", f"{glyph_poc.effective_caret_drop_mm(cfg):.4f}"]
    if "per_auto_baseline" in v or "per_raise_mm" in v:   # the per sign, as the element places it
        import glyph_poc
        cmd += ["--per-raise-mm", f"{glyph_poc.effective_per_raise_mm(cfg):.4f}"]
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


def save_copy(machine, body=None):
    """tune.py's Save button: a timestamped copy of the last output in
    output/saved/, plus a .yaml sidecar holding the full config it was
    built from (loadable as a master later)."""
    cfg, _t, _m = load_running(machine)
    master, running = paths(machine)
    src = output_path(cfg)
    if not os.path.isfile(src):
        raise EngineError(404, "nothing built yet")
    save_dir = os.path.join(os.path.dirname(src), "saved")
    os.makedirs(save_dir, exist_ok=True)
    target = (body.get("last_build") or {}).get("target")
    base = f"{export_name(machine, cfg, target)}_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
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



# ------------------------------------------------------------------ settings files
# Every download carries the settings it was built from: the running config
# exactly as saved (so the file loads straight back in, here or in tune.py)
# under a header of what a reader can't see in the YAML itself - when, what
# was built, the caret's total raise, and a fingerprint of each font file so
# a rebuild can tell it has the same font, not just one with the same name.

SETTINGS_TAG = "# te-settings: "


def _font_fingerprint(path):
    import hashlib
    try:
        with open(os.path.expanduser(path), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        return None


def settings_file(machine, body=None):
    """{name, text}: the running config as a self-describing settings file."""
    import json
    import glyph_poc
    body = body or {}
    cfg, text, _m = load_running(machine)
    fonts = {}
    for s in schema(machine, cfg):
        for f in s["fields"]:
            if f["key"] in ("path", "font2_path", "font_path", "label_font_path", "legend_font_path", "label_font_override", "label_no_font_override") and f["value"]:
                fonts[f["key"]] = {"file": os.path.basename(str(f["value"])), "sha256_16": _font_fingerprint(str(f["value"]))}
    meta = {"machine": machine, "saved": datetime.now().isoformat(timespec="seconds"),
            "build": body.get("last_build"), "engine": body.get("engine"), "app": body.get("app"),
            "caret_drop_total_mm": round(glyph_poc.effective_caret_drop_mm(cfg), 4), "fonts": fonts}
    if body.get("font_stand_ins"):     # browser: which of these fonts stand in for one the user doesn't have here
        meta["font_stand_ins"] = body["font_stand_ins"]
    head = ("# Type Elements settings - load this file back with Open config > Load a settings file\n"
            "# (or as a config in tune.py) to rebuild exactly this element.\n"
            + SETTINGS_TAG + json.dumps(meta, ensure_ascii=False) + "\n")
    name = (body.get("last_build") or {}).get("name") or export_name(machine, cfg)
    return {"name": f"{name}.settings.yaml", "text": head + text}


def import_settings(body):
    """Makes a settings file (or any config YAML for a known machine) that
    machine's running copy. {machine} - the caller loads that machine."""
    text = body.get("text") or ""
    try:
        cfg = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise EngineError(400, f"not a readable settings file: {e}")
    machine = (cfg or {}).get("machine") if isinstance(cfg, dict) else None
    if machine not in tune.MACHINES:
        raise EngineError(400, "this file doesn't say which machine it's for (no machine: key)")
    _master, running = paths(machine)
    with open(running, "w", encoding="utf-8") as f:
        f.write(text)
    load_running(machine)          # back-fill / convert anything older than this engine
    return {"machine": machine}


# ------------------------------------------------------------------ font profiles

def _profiles_root():
    """font_profiles keeps profiles in <root>/profiles/font_and_alignment."""
    return PROFILES_DIR or CONFIG_DIR


def profile_field_paths(machine):
    return [list(f[1]) for f in tune.SECTIONS_BY_MACHINE.get(machine, {}).get("Font & Alignment", [])]


def _profile_entries(machine):
    """[(name, path, builtin)]: the user's profiles, then the built-in ones
    that ship in v4/config (read-only, and only listed separately when the
    user's profiles live elsewhere - the browser keeps them in /persist).
    A user profile with a built-in's name replaces it."""
    mine = [(n, p, False) for n, p in font_profiles.list_profiles(_profiles_root(), machine)]
    if _profiles_root() == CONFIG_DIR:
        return mine
    have = {n for n, _p, _b in mine}
    builtin = [(n, p, True) for n, p in font_profiles.list_profiles(CONFIG_DIR, machine) if n not in have]
    return sorted(mine + builtin, key=lambda e: e[0].lower())


def profiles(machine, font_aliases=None):
    """font_aliases {path in the config: path it stands in for} - the browser
    engine's font stand-ins, so a profile still reads as active when the
    config holds this browser's copy of the profile's font."""
    cfg, _t, _m = load_running(machine)
    paths_ = profile_field_paths(machine)
    current = font_profiles.collect_from_config(cfg, paths_)
    if font_aliases:
        current = {k: font_aliases.get(v, v) if isinstance(v, str) else v for k, v in current.items()}
    out = []
    for name, path, builtin in _profile_entries(machine):
        _n, values = font_profiles.load_profile(path)
        applied, aliased, skipped, unset = font_profiles.apply_to(values, paths_)
        merged = {**applied, **{k: v for k, (v, _src) in aliased.items()}}
        active = bool(merged) and all(current.get(k) == v for k, v in merged.items())
        out.append({"name": name, "values": merged, "skipped": skipped, "unset": unset, "active": active,
                    "builtin": builtin})
    return out


def _not_builtin(machine, name):
    if any(n == name and b for n, _p, b in _profile_entries(machine)):
        raise EngineError(400, f'"{name}" ships with the app and can\'t be changed - save your settings under a new name instead')


def profile_save(machine, body, font_aliases=None):
    cfg, _t, _m = load_running(machine)
    name = (body.get("name") or "").strip()
    if not name:
        raise EngineError(400, "profile needs a name")
    values = font_profiles.collect_from_config(cfg, profile_field_paths(machine))
    if font_aliases:
        values = {k: font_aliases.get(v, v) if isinstance(v, str) else v for k, v in values.items()}
    font_profiles.save_profile(_profiles_root(), name, values, saved_from=machine)
    return profiles(machine)


def profile_rename(machine, body):
    _not_builtin(machine, body.get("old", ""))
    try:
        font_profiles.rename_profile(_profiles_root(), body["old"], body["new"])
    except (KeyError, ValueError, FileExistsError, FileNotFoundError) as e:
        raise EngineError(400, str(e))
    return profiles(machine)


def profile_delete(machine, body):
    _not_builtin(machine, body.get("name", ""))
    font_profiles.delete_profile(_profiles_root(), body.get("name", ""))
    return profiles(machine)




def tool_command(machine, body):
    """argv for a non-build job: type_test, legend, coverage (scan a font
    directory) or coverage_current (the configured font, then replacements)."""
    cfg, _t, _m = load_running(machine)
    _master, running = paths(machine)
    name = body.get("tool")
    if name == "type_test":
        return type_test_command(machine, cfg)
    if name == "legend":
        return [sys.executable, os.path.join(V4, "generate_legend.py"), running]
    if name in ("coverage", "coverage_current"):
        chars = (body.get("chars") or "").replace("\n", "").replace("\r", "")
        font_dir = os.path.expanduser(body.get("font_dir") or "")
        if not chars or not os.path.isdir(font_dir):
            raise EngineError(400, "need a character set and an existing font directory")
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
        return cmd
    raise EngineError(400, f"unknown tool {name!r}")


def stl_path(machine):
    cfg, _t, _m = load_running(machine)
    path = output_path(cfg)
    if not os.path.isfile(path):
        raise EngineError(404, "not built yet")
    return path


def mapping_path(machine):
    """A calibration build's position -> tested value sidecar."""
    cfg, _t, _m = load_running(machine)
    path = output_path(cfg, "_mapping.txt")
    if not os.path.isfile(path):
        raise EngineError(404, "no calibration mapping yet")
    return path


def legend_path(machine):
    cfg, _t, _m = load_running(machine)
    path = output_path(cfg, "_legend.svg")
    if not os.path.isfile(path):
        raise EngineError(404, "no legend generated yet")
    return path
