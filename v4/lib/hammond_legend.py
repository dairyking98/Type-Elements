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

Grid math: n=0..29 is the physical shuttle position, (col, row) =
(n//3, n%3). DELIBERATE v4 divergence from v1's own Locate2(n): v1 used
a row-dependent taper term to derive each row's x-span from the
narrowest (Q-to-P) row plus a single measured ZExclamation_Length
constant for the widest row, with the middle row's own span an
unmeasured, purely-interpolated side effect of that formula (see git
history for the original port of v1's real arithmetic). Replaced with
absolute, independently-specified per-row geometry against a real hand-
measured original card: each row is a plain linear span of its own
real measured length (Q-to-P/A-to-:/Z-to-!), all three rows sharing the
same left starting x (a real physical fact - Q/A/Z sit in one vertical
column on the real machine), positioned by an absolute bottom margin
(Z row) and row-to-row pitch, not derived from any other row's span.
See _locate() below.

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

import math

import yaml
from shapely.affinity import translate as shapely_translate
from shapely.geometry import Point, Polygon
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

    layout = cfg["layout"]
    g["ROWS"] = layout["rows"]
    g["N_COLS"] = layout["latitude_columns"]

    lg = cfg.get("legend", {})
    # legend.legend_font_path - not bare font_path (this config's own
    # label:/font: sections already use that key - see mignon_legend.
    # configure()'s matching comment for why that collides). Independent
    # of font.path, see that same comment.
    g["FONT_PATH"] = lg.get("legend_font_path", cfg["font"]["path"])
    # Real per-row hand-measured spans (top/mid/bottom physical row,
    # Q-to-P/A-to-:/Z-to-!) - see module docstring's divergence note.
    g["QP_Length"] = lg.get("qp_length_mm", 178.0)
    g["AColon_Length"] = lg.get("a_colon_length_mm", 188.0)
    g["ZExclamation_Length"] = lg.get("z_exclamation_length_mm", 198.0)
    # Row-to-row vertical pitch (same for both gaps: Q<->A and A<->Z) and
    # the absolute placement anchors - bottom margin measured up from the
    # card's own bottom edge to the Z row, left margin measured in from
    # the card's own left edge to every row's shared starting column
    # (Q/A/Z are vertically aligned on the real machine).
    g["Row_Separation"] = lg.get("row_separation_mm", 18.45)
    g["Left_Margin"] = lg.get("left_margin_mm", 38.0)
    g["Bottom_Margin"] = lg.get("bottom_margin_mm", 9.2)
    # Card outline - a real fixed cut size, not derived from content
    # bounds (unlike Mignon's own edge-to-content margins, this card's
    # margins are genuinely asymmetric - only the top two corners are
    # rounded, matching the real original card - see _card_border()).
    g["Card_Width"] = lg.get("card_width_mm", 274.0)
    g["Card_Height"] = lg.get("card_height_mm", 60.0)
    g["Card_Corner_Radius"] = lg.get("card_corner_radius_mm", 19.0)
    # The rounding circle's own center height, measured from the card's
    # bottom edge - NOT derived as Card_Height-Card_Corner_Radius, a real
    # independent measurement. center_y+radius (38+19=57mm) falls short
    # of Card_Height (60mm), so the arc alone doesn't reach the top edge -
    # see _card_border()'s docstring for the straight vertical bridge
    # this requires.
    g["Card_Corner_Center_Y"] = lg.get("card_corner_center_y_mm", 38.0)
    g["Card_Border_Stroke"] = lg.get("card_border_stroke_mm", 0.1)
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
    # v4-only, not a v1 concept - see mignon_legend.configure()'s matching
    # comment. "transparent" (default, no backing rect) or "white".
    g["Background_Mode"] = lg.get("background", "transparent")

    # Row index (n%3): 0=Q (top), 1=A (middle), 2=Z (bottom) - see
    # module docstring. Each row's own 9-gap/10-key pitch, and each row's
    # absolute y (height above the card's bottom edge) - Q is 2 row-
    # separations above Z, A is 1 above Z.
    g["Row_Lengths"] = [QP_Length, AColon_Length, ZExclamation_Length]
    g["Row_Y"] = [Bottom_Margin + 2 * Row_Separation, Bottom_Margin + Row_Separation, Bottom_Margin]

    _configured = True


def _require_configured():
    if not _configured:
        raise RuntimeError("call hammond_legend.configure(config_path) before using this module")


# --------------------------------------------------------------- Grid math

def _locate(n):
    """Absolute per-row placement - see module docstring's divergence
    note from v1's own taper formula. col=n//3, row=n%3; each row is a
    plain linear span of its OWN measured length (Row_Lengths[row]),
    starting at the shared Left_Margin (Q/A/Z are vertically aligned),
    at that row's own absolute height above the card's bottom edge
    (Row_Y[row])."""
    row = n % 3
    col = n // 3
    pitch = Row_Lengths[row] / 9.0
    x = Left_Margin + col * pitch
    y = Row_Y[row]
    return x, y


def _outlined_circle(center):
    """v1 OutlinedCircle() (HammondIndex.scad:92-97)."""
    outer = Point(center).buffer((Circle_ID + 2 * Circle_Thickness) / 2.0, quad_segs=Circle_Segments)
    inner = Point(center).buffer(Circle_ID / 2.0, quad_segs=Circle_Segments)
    return outer.difference(inner)


def _arc_points(cx, cy, r, start_deg, end_deg, n):
    """n+1 points along the circle centered (cx,cy) radius r, sweeping
    from start_deg to end_deg (degrees, standard math convention -
    0=+X axis, 90=+Y axis, increasing counter-clockwise)."""
    angles = [math.radians(start_deg + (end_deg - start_deg) * i / n) for i in range(n + 1)]
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in angles]


def _card_border():
    """v4-only, not a v1 concept - the real physical card's cut outline
    (Card_Width x Card_Height, origin at the bottom-left corner), rounded
    at the top two corners only with sharp bottom corners - matches a
    real hand-measured original card, not a plain Mignon-style all-4-
    corners rounded rect.

    NOT a simple tangent-rounded-rect (unlike mignon_legend.
    _radius_rectangle()'s hull-of-corner-circles): the rounding circle's
    center height (Card_Corner_Center_Y) is a real independent
    measurement, not derived as Card_Height-Card_Corner_Radius, and
    center_y+radius falls short of Card_Height (e.g. 38+19=57 < 60) - the
    arc alone doesn't reach the top edge. So each top corner is: straight
    up the side edge to the point where it's tangent to the rounding
    circle, a quarter-circle arc up to the circle's own topmost point,
    then a straight VERTICAL bridge the rest of the way up to the top
    edge at that same x - not a single smooth curve reaching the corner.
    Traced explicitly as one polygon boundary rather than any hull/
    boolean trick, since the two arcs here don't touch two tangent edges
    each (only one - the side edge) the way a real rounded-rect corner's
    circle does."""
    r = Card_Corner_Radius
    cy = Card_Corner_Center_Y
    left_cx, right_cx = r, Card_Width - r
    segs = max(Circle_Segments // 4, 4)  # a quarter-circle's share of the full-circle segment count

    coords = [(0.0, 0.0), (0.0, cy)]
    coords += _arc_points(left_cx, cy, r, 180, 90, segs)  # (0,cy) -> (left_cx, cy+r)
    coords += [(left_cx, Card_Height), (right_cx, Card_Height)]
    coords += _arc_points(right_cx, cy, r, 90, 0, segs)  # (right_cx, cy+r) -> (Card_Width, cy)
    coords += [(Card_Width, 0.0)]
    return Polygon(coords)


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


def render_svg(fill="#000000", background=None, border_stroke="#000000"):
    """Serializes build_legend_geometry() (the ink content: circles/
    characters) plus _card_border() (the real cut outline) to a self-
    contained SVG string, sized to the card's own fixed Card_Width x
    Card_Height (a real physical cut size, not derived from content
    bounds - see _card_border()'s docstring).

    The border is emitted as its own stroke-only path (border_stroke,
    stroke-width=Card_Border_Stroke), separate from the filled content
    path rather than merged into it - it's the cut outline, not part of
    the ink silhouette.

    background: see mignon_legend.render_svg()'s matching docstring -
    same "transparent"/"white" convention, None reads legend.background
    from the config. The background rect (when "white") covers the
    whole card, not just the content bounds."""
    background = Background_Mode if background is None else background
    geom = build_legend_geometry()
    content_d = _geometry_path_d(geom)
    border = _card_border()
    border_d = _ring_path_d(border.exterior.coords)
    bg_rect = (f'  <rect x="0" y="0" width="{Card_Width}" height="{Card_Height}" fill="#ffffff"/>\n'
               if background == "white" else "")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{Card_Width}mm" height="{Card_Height}mm" '
        f'viewBox="0 0 {Card_Width} {Card_Height}">\n'
        f'{bg_rect}'
        f'  <g transform="translate(0,{Card_Height}) scale(1,-1)">\n'
        f'    <path d="{border_d}" fill="none" stroke="{border_stroke}" stroke-width="{Card_Border_Stroke}"/>\n'
        f'    <path d="{content_d}" fill="{fill}" fill-rule="evenodd"/>\n'
        '  </g>\n'
        '</svg>\n'
    )
