"""
v4 port of v1/Hammond/HammondIndex.scad - the Hammond "index" reference
card showing which of the 30 physical shuttle keys produces which
character. Same family of tool as lib/mignon_legend.py (see that
module's docstring for the general "why not OpenSCAD" rationale) but a
genuinely different design, ported fresh rather than copied: Hammond's
physical type shuttle is one linear arc of 30 keys (not Mignon's 7x12
grid), and its real v1 index displays that arc as a conventional
QWERTY-style 3-row x 10-column keyboard, with up to 3 stacked labels
(a big CAP letter, a small FIG char above it, a small lowercase/
punctuation char below it) plus an outline ring per key - not per-key
shift-state fill/no-fill like Mignon.

Ported from v1/Hammond/HammondIndex.scad's ACTUAL live code path -
Print()/TextLayout2() (Locate()/TextLayout() are v1's own earlier/
simpler-taper attempt, dead code - Print() only ever calls
ProjectedPrint()->Print()->TextLayout2(), never TextLayout()). Checked
directly against a real openscad-nightly render of the actual v1 file
(wrapped in a projection() to get a 2D top view, since v1's own Print()
is a real linear_extrude()'d cut - see below) rather than trusting the
source alone, the same lesson learned porting Mignon's legend.

Grid math: v1's Locate2(n) walks n=0..29 (the physical shuttle position)
and derives (col, row) via col=n//3, row=n%3 - v1's own `X_Column=n/3-
n%3/3` reduces to exactly n//3 algebraically (n%3 IS row by
construction, so the row/3 terms cancel), just expressed without a
floor-division operator. Column x-position is NOT a plain linear
n*pitch - v1 adds a row-dependent taper term
(ModRowSpace(n)*row/2) modeling the real shuttle's physical fan/arc
(the bottom FIG/number row spans measurably wider than the top CAP row)
- ported as _locate() below, exactly reproducing v1's arithmetic.

Content lookup uses the MIRRORED index ((N_COLS-1)-n) into layout.rows
while placement uses the UNMIRRORED n directly - the opposite split from
Mignon's (mirrored placement/unmirrored content) - confirmed correct
against the real render (e.g. its physical top-left key is "Q": layout.
rows[1][29] == "Q", placed at n=0/col=0/row=0). Unlike Mignon,
HammondIndex.scad's Text()/TextFIGs() never call mirror() - there is no
glyph-mirroring step here at all, and the real render confirms plain,
correctly-oriented letters throughout, consistent with this being a
read-directly reference card (see mignon_legend.py's docstring for the
same reasoning).

A confirmed-broken/no-op v1 mechanism, NOT ported (found only by
rendering, not visible from reading the source): OffsetChars (a per-
character extra nudge for two Unicode glyphs, "☼"/"☞", HammondIndex.
scad:27) is looked up via `search(Char, OffsetChars)` where OffsetChars
is a list of [char, offset] PAIRS, not a flat character string -
openscad-nightly's real render emits "ECHO: undef" for every single key
(confirmed: Offset[0] is undef every time, i.e. this search() never
matches), so the nudge never applies in real v1 output either.

Deliberate divergence from v1 (documented, not silent): v1's Print()
literally cuts the whole design (every circle ring + every character)
OUT of a solid rectangular plate (`difference(cube(...), TextLayout2())`
- a negative/stencil plate, not ink-on-paper). Rendered literally, that
polarity is hard to read at a glance (many small holes crowded close
together read as one confusing blob rather than legible circles/
letters). This module renders the same content the other way up - the
circles and characters as a positive (ink-on-transparent) silhouette,
no background plate at all - a genuinely more legible reference card,
matching the same "readable legend" goal mignon_legend.py's own
divergences (no glyph mirror) serve.

All real numbers (shuttle/plate dimensions, circle size, label sizes/
offsets, the CAPFIG_Mod/Lowercase_Mod/FIG_Dupe character-class strings)
live in config YAML under legend: - see config/hammond.yaml. Call
configure(path) before using anything else in this module, same
convention as mignon_legend.configure().
"""

import yaml
from shapely.affinity import translate as shapely_translate
from shapely.geometry import Point
from shapely.ops import unary_union

from glyph_poc import (
    compose_glyph_polygon,
    em_to_mm_scale,
    get_glyph_contours_and_advance,
    load_font_face,
)

# machine: values this legend understands - Hammond and Hammond Split
# are a genuinely different machine/layout each (different lib/*.py,
# different config/*.yaml layout.rows - confirmed: hammond_split.yaml's
# rows are a real, different key arrangement, not just a font swap) but
# share the exact same 3-row/30-column shuttle-arc STRUCTURE this legend
# draws, so both are accepted here.
_SUPPORTED_MACHINES = ("hammond", "hammond_split")

_configured = False


def configure(config_path):
    """Loads config_path (a Hammond or Hammond Split YAML config) and
    sets this module's globals - see mignon_legend.configure()'s
    docstring for the general scheme (same reasoning applies: reads
    layout.rows directly rather than importing lib/hammond.py, no
    dependency on cylinder_machine.py's globals-sync machinery)."""
    global _configured
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    machine = cfg.get("machine")
    if machine not in _SUPPORTED_MACHINES:
        raise ValueError(
            f"{config_path}: legend generation supports {_SUPPORTED_MACHINES}, got machine={machine!r}")

    g = globals()
    g["FONT_PATH"] = cfg["font"]["path"]

    layout = cfg["layout"]
    g["ROWS"] = layout["rows"]
    g["N_COLS"] = layout["latitude_columns"]

    lg = cfg.get("legend", {})
    g["QP_Length"] = lg.get("qp_length_mm", 178.0)
    g["ZExclamation_Length"] = lg.get("z_exclamation_length_mm", 200.4)
    g["Center_to_Center_Height"] = lg.get("center_to_center_height_mm", 40.0)
    g["Margin"] = lg.get("margin_mm", 5.0)
    g["Circle_ID"] = lg.get("circle_id_mm", 14.0)
    g["Circle_Thickness"] = lg.get("circle_thickness_mm", 0.5)
    g["CAP_Size"] = lg.get("cap_size_mm", 6.0)
    g["FIG_Size"] = lg.get("fig_size_mm", 4.0)
    g["CAPFIG_ModSize"] = lg.get("capfig_mod_size_mm", 4.0)
    g["FIG_Offset"] = lg.get("fig_offset_mm", 2.5)
    g["Lowercase_Offset"] = lg.get("lowercase_offset_mm", -5.5)
    g["CAP_Offset"] = lg.get("cap_offset_mm", -4.5)
    g["FIG_Dupe_Offset"] = lg.get("fig_dupe_offset_mm", 3.0)
    g["CAPFIG_Offset"] = lg.get("capfig_offset_mm", -1.5)
    g["CAPFIG_Mod"] = lg.get("capfig_mod_chars", "!:?-\"&")
    g["Lowercase_Mod"] = lg.get("lowercase_mod_chars", ";,'")
    g["FIG_Dupe"] = lg.get("fig_dupe_chars", ".")
    g["Circle_Segments"] = lg.get("circle_segments", 32)
    g["FLATNESS_TOLERANCE_MM"] = lg.get("legend_flatness_tolerance_mm", 0.01)

    g["QW_Spacing"] = QP_Length / 9.0
    g["Y_Spacing"] = Center_to_Center_Height / 2.0
    g["RowSpaceMax"] = ZExclamation_Length - QP_Length

    _configured = True


def _require_configured():
    if not _configured:
        raise RuntimeError("call hammond_legend.configure(config_path) before using this module")


# --------------------------------------------------------------- Grid math

def _locate(n):
    """v1 Locate2(n) (HammondIndex.scad:78-90) - col=n//3 (v1's `n/3-
    n%3/3`, algebraically identical - see module docstring), row=n%3,
    plus a row-dependent taper term modeling the shuttle's real physical
    fan (only rows 1/2 get any of it, row 2 gets it in full)."""
    row = n % 3
    col = n // 3
    mod_row_space = RowSpaceMax * n / (N_COLS - 1)
    x = col * QW_Spacing + (row / 2.0) * mod_row_space
    y = -row * Y_Spacing
    return x, y


def _outlined_circle(center):
    """v1 OutlinedCircle() (HammondIndex.scad:92-97)."""
    outer = Point(center).buffer((Circle_ID + 2 * Circle_Thickness) / 2.0, quad_segs=Circle_Segments)
    inner = Point(center).buffer(Circle_ID / 2.0, quad_segs=Circle_Segments)
    return outer.difference(inner)


# ---------------------------------------------------------- Glyph shapes

def _glyph_polygon(ch, size_mm):
    """v1's Text()/TextFIGs() (HammondIndex.scad:64-70 - identical
    bodies in the real source, both plain text() calls) - a composed,
    centered (v1's halign="center") shapely polygon for one character at
    the given size, baseline at y=0. Not mirrored - see module
    docstring. None for a space or an empty/undrawable glyph."""
    if ch is None or ch == " ":
        return None
    face = load_font_face(FONT_PATH)
    scale = em_to_mm_scale(size_mm, face.units_per_EM)
    contours_mm, advance_mm = get_glyph_contours_and_advance(
        ch, FLATNESS_TOLERANCE_MM, scale, font_path=FONT_PATH)
    if not contours_mm:
        return None
    x_shift = -advance_mm / 2.0
    centered = [c + [x_shift, 0.0] for c in contours_mm]
    poly = compose_glyph_polygon(centered)
    if poly is None or poly.is_empty:
        return None
    return poly


def _key_parts(n):
    """v1 TextLayout2()'s per-key body (HammondIndex.scad:143-187) - the
    CAP letter (with the CAPFIG_Mod/FIG_Dupe-dependent vertical-offset
    arithmetic transcribed exactly, see module docstring), the FIG char
    (blanked if it's a FIG_Dupe marker), the lowercase/punctuation char
    (blanked unless it's actually a Lowercase_Mod character), and the
    outline ring - all at physical position n (v1's Locate2(n)), reading
    layout.rows at the MIRRORED index."""
    idx = (N_COLS - 1) - n
    cap_char = ROWS[1][idx]
    fig_char_raw = ROWS[2][idx]
    lower_char_raw = ROWS[0][idx]

    cap_mod = cap_char in CAPFIG_Mod
    fig_dupe = fig_char_raw in FIG_Dupe
    lower_mod = lower_char_raw in Lowercase_Mod

    cap_size = CAPFIG_ModSize if cap_mod else CAP_Size
    fig_char = None if fig_dupe else fig_char_raw
    lower_char = lower_char_raw if lower_mod else None

    cap_y_offset = ((0.0 if cap_mod else CAP_Offset) +
                     (0.0 if not fig_dupe else FIG_Dupe_Offset) +
                     (0.0 if not cap_mod else CAPFIG_Offset))

    cx, cy = _locate(n)
    parts = [shapely_translate(_outlined_circle((0, 0)), cx, cy)]

    cap_glyph = _glyph_polygon(cap_char, cap_size)
    if cap_glyph is not None:
        parts.append(shapely_translate(cap_glyph, cx, cy + cap_y_offset))

    fig_glyph = _glyph_polygon(fig_char, FIG_Size)
    if fig_glyph is not None:
        parts.append(shapely_translate(fig_glyph, cx, cy + FIG_Offset))

    lower_glyph = _glyph_polygon(lower_char, FIG_Size)
    if lower_glyph is not None:
        parts.append(shapely_translate(lower_glyph, cx, cy + Lowercase_Offset))

    return parts


def build_legend_geometry():
    """v1 TextLayout2() (HammondIndex.scad:143-187), unioned across all
    30 keys - see module docstring for why this is rendered as a
    positive silhouette (ink), not v1's literal cut-through-a-plate
    polarity."""
    _require_configured()
    parts = []
    for n in range(N_COLS):
        parts.extend(_key_parts(n))
    return unary_union(parts)


# --------------------------------------------------------------- SVG output

def _ring_path_d(coords):
    pts = list(coords)
    d = f"M {pts[0][0]:.4f},{pts[0][1]:.4f} "
    d += " ".join(f"L {x:.4f},{y:.4f}" for x, y in pts[1:])
    return d + " Z"


def _geometry_path_d(geom):
    if geom.geom_type == "Polygon":
        polys = [geom]
    elif geom.geom_type == "MultiPolygon":
        polys = list(geom.geoms)
    elif geom.geom_type == "GeometryCollection":
        polys = [g for g in geom.geoms if g.geom_type == "Polygon"]
    else:
        polys = []
    parts = []
    for poly in polys:
        parts.append(_ring_path_d(poly.exterior.coords))
        for interior in poly.interiors:
            parts.append(_ring_path_d(interior.coords))
    return " ".join(parts)


def render_svg(fill="#000000"):
    """Serializes build_legend_geometry() to a self-contained SVG string,
    padded by (Circle_ID+Margin)/2 around the real content bounds (v1's
    own cube() padding, HammondIndex.scad:200 - `+Circle_ID+5` around
    ZExclamation_Length/Center_to_Center_Height) rather than v1's exact
    plate dimensions, since this module's content bounds already reflect
    the real taper (see _locate()) and don't need re-deriving from
    QP_Length/ZExclamation_Length a second time."""
    geom = build_legend_geometry()
    minx, miny, maxx, maxy = geom.bounds
    pad = (Circle_ID + Margin) / 2.0
    minx, miny, maxx, maxy = minx - pad, miny - pad, maxx + pad, maxy + pad
    width, height = maxx - minx, maxy - miny
    d = _geometry_path_d(geom)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <g transform="translate({-minx},{maxy}) scale(1,-1)">\n'
        f'    <path d="{d}" fill="{fill}" fill-rule="evenodd"/>\n'
        '  </g>\n'
        '</svg>\n'
    )
