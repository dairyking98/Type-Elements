"""
v4 port of v1/Mignon/MignonIndex.scad + MignonIndexLayouts.scad - the
Mignon "index" reference card showing which of the 7x12 physical
keyboard buttons produces which character (and which need Shift). v1
built this as flat 2D OpenSCAD geometry (circle()/square()/text()/
hull()) and exported it via a commented-out projection() call to SVG -
an unconventional but workable use of a solid modeler as a 2D drawing
engine.

v4 doesn't need that indirection: lib/glyph_poc.py already has a real
2D-glyph pipeline (get_glyph_contours_and_advance() +
compose_glyph_polygon() - the same functions the struck-character mesh
pipeline uses, stopped one step before triangulation/extrusion) and
shapely is already a project dependency, so this module builds the
legend directly as shapely 2D geometry and serializes straight to SVG -
no OpenSCAD, no intermediate mesh. generate_legend.py is the CLI entry
point (mirrors generate.py's shape, but this is a completely separate,
2D-only output - not part of the 3D element build at all).

Ported from v1/Mignon/MignonIndex.scad's ACTUAL live code path -
Array2(), the module actually invoked by the file's own closing
statement - and checked directly against a REAL openscad-nightly render
of that exact file (Layout_Selection=5, matching this config's own
default layout), not just read off the source: reading OpenSCAD source
and predicting its behavior turned out to be unreliable here (see the
two real bugs documented below, both only found by actually rendering
it), so ground truth for this port is the rendered SVG, not the
customizer comments. Array1()/CenterRectangle()/LiningRectangle()/
LiningCircle() are dead code in v1 (defined, never called from Array2()
or anywhere else) and are NOT ported here. Every function below is named
after and mirrors its v1 counterpart 1:1 (RadiusRectangle/CheckerPattern/
ClearHoles/ClearShape/LineCircles/SolidShape/ArrangeText), including the
grid math (LocateCenter/LocateBaseline) and the mirrored-column/
unmirrored-character-index split that shows up throughout Array2()'s
tree: a cell's occupied-or-blank check and its displayed CHARACTER both
read array index c, but the cell's drawn POSITION uses the mirrored
index (N_COLS-1-c) - confirmed directly against the real render (e.g.
its physical "B A N I V" / "M T E D L" rows are exactly layout.rows[2]
[1:6] / layout.rows[3][1:6] read in reverse column order, landing at
physical columns 6-10).

Two real, confirmed v1 bugs, found only by rendering the actual file
(not visible from reading the customizer source alone) - NOT ported:
- 2DText()'s mirror([1,0,0]) (MignonIndex.scad:465) does NOT produce
  mirrored/backwards letters in the real render - its own SVG output
  reads with plain, correctly-oriented text throughout (directly
  confirmed: "B A N I V"/"M T E D L" etc. read normally, not reversed).
  Whatever v1's actual net transform chain does, the observable result
  is unmirrored, so _glyph_polygon() below does not mirror either - see
  its own docstring for why that's also the geometrically sensible
  choice for a card meant to be read directly (unlike a struck element).
- Character_Modifieds_Offset (the per-character baseline nudge for
  underscore/descenders/parentheses/ascenders, MignonIndex.scad:61-72)
  is applied WITHOUT indexing by the search() result at line 464
  (`translate([0, Character_Modifieds_Offset, 0])`, not
  `Character_Modifieds_Offset[y[0]]`) - openscad-nightly emits "WARNING:
  Unable to convert translate(...) parameter to a vec3" for exactly this
  and the offset has no visible effect in the real render. legend.
  height_offset_groups below defaults every offset to 0.0 (v1's REAL
  behavior) rather than the nonzero values the customizer comments
  imply - the mechanism itself still works correctly here (unlike v1),
  so it's left as a real, working, opt-in config knob rather than
  deleted, but its ported default matches what v1 actually renders, not
  what its source claims to do.

Deliberate simplification from v1 (documented, not silent divergence):
v1's Weight_Adj mechanism (Horizontal_Weight_Adj/Vertical_Weight_Adj/
Weight_Adj_Mode/Weight_Adj_Shape, MignonIndex.scad:52-59) is a
Minkowski-based glyph-bolding knob whose own code contradicts its
customizer comment about which mode number means Additive vs Subtractive
(line 57's comment says 0=Subtractive/1=Additive; the actual branches at
lines 466-483 do the opposite - 1=Subtractive, 2=Additive, with 1 the
real default), and its real default magnitude (.001mm) is visually a
no-op regardless of which branch runs. Replaced with one config knob,
legend.weight_adjustment_mm, applied as a plain shapely buffer() on the
composed glyph polygon (positive=bolder, negative=thinner, 0=v1's real
default behavior - a true no-op, not an approximation of one). v1's
Scale_Multiplier/Scale_Multiplier_Text ("." only, MignonIndex.scad:83-84)
is separately unported - both its real default values (1.0, ".") make it
a no-op in every real config, same reasoning.

All real numbers (card dimensions, circle/line sizes, the 3 fill-pattern
arrays, character height-offset groups) live in config YAML under
legend: - see config/mignon.yaml. Call configure(path) before using
anything else in this module, same convention as mignon.configure().
"""

import numpy as np
import yaml
from shapely.affinity import rotate as shapely_rotate
from shapely.affinity import scale as shapely_scale
from shapely.affinity import translate as shapely_translate
from shapely.geometry import Point, box
from shapely.ops import unary_union

from glyph_poc import (
    compose_glyph_polygon,
    em_to_mm_scale,
    get_glyph_contours_and_advance,
    load_font_face,
)

# v1 NormalCircleFillArray/NormalBackgroundFillArray/NormalSolidFillAray
# (MignonIndex.scad:126-151) - fallback defaults for configs that predate
# the legend: config section (e.g. a tune.py-migrated *.running.yaml that
# hasn't been regenerated since this module was added) so configure()
# degrades to v1's real defaults instead of a bare KeyError.
_DEFAULT_CIRCLE_FILL = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
_DEFAULT_BACKGROUND_FILL = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
_DEFAULT_SOLID_FILL = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

_configured = False


def configure(config_path):
    """Loads config_path (a Mignon YAML config) and sets this module's
    globals - see mignon.configure()'s docstring for the general scheme.
    Reads layout.rows directly (RAW keyboard-legend order, v1's `Layout`
    array - exactly what this card displays, unlike mignon.py's
    char_legend-remapped DHIATENSOR, which is what actually gets struck
    on the element) rather than importing lib/mignon.py, so this module
    has no dependency on cylinder_machine.py's globals-sync machinery at
    all."""
    global _configured
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if cfg.get("machine") != "mignon":
        raise ValueError(
            f"{config_path}: legend generation is Mignon-only (machine={cfg.get('machine')!r})")

    g = globals()

    layout = cfg["layout"]
    g["ROWS"] = layout["rows"]
    g["N_ROWS"] = len(g["ROWS"])
    g["N_COLS"] = layout["latitude_columns"]

    # .get("legend", {}) + per-key defaults (v1's own real customizer
    # defaults, MignonIndex.scad line-cited in config/mignon.yaml's
    # legend: comments) rather than direct cfg["legend"][...] indexing -
    # lets a config that predates this section (e.g. a not-yet-
    # regenerated *.running.yaml) still build a legend instead of a bare
    # KeyError.
    lg = cfg.get("legend", {})
    # legend.legend_font_path (not the bare font_path config.mignon.yaml's
    # own logo:/font: sections already use - tune.py's patch_yaml_value
    # matches by bare key text across the whole file, not by section, so
    # identical key names under different sections collide) - independent
    # of font.path (the engraved-element typeface): a legend card is
    # laser-cut/printed paper, not the 3D element, so there's no reason it
    # has to share the same font. Defaults to font.path so an existing
    # config with no legend.legend_font_path key yet keeps rendering
    # exactly as before.
    g["FONT_PATH"] = lg.get("legend_font_path", cfg["font"]["path"])
    g["Length"] = lg.get("length_mm", 133.0)
    g["Width"] = lg.get("width_mm", 83.0)
    g["Corner_Radius"] = lg.get("corner_radius_mm", 9.0)
    g["Edge_to_Column"] = lg.get("edge_to_column_mm", 10.5)
    g["Edge_to_Row"] = lg.get("edge_to_row_mm", 9.5)
    g["Circle_Diameter"] = lg.get("circle_diameter_mm", 8.0)
    g["Circle_Height_Bump"] = lg.get("circle_height_bump_mm", 0.8)
    g["Line_Width"] = lg.get("line_width_mm", 0.3)
    g["Square_Pattern_Size"] = lg.get("square_pattern_size_mm", 0.5)
    g["Square_Pattern_Pitch"] = lg.get("square_pattern_pitch_mm", 0.8)
    g["Checker"] = lg.get("checker", False)
    g["Type_Size"] = lg.get("type_size_mm", 5.0)
    g["Height_Offset"] = lg.get("legend_height_offset_mm", 2.1)
    g["Circle_Segments"] = lg.get("circle_segments", 32)
    g["Weight_Adjustment"] = lg.get("weight_adjustment_mm", 0.0)
    g["Inner_Border"] = lg.get("inner_border", False)
    # v4-only - not a v1 concept at all (v1's SVG export has no notion of
    # a background fill, it's just whatever geometry got exported).
    # "transparent" (default) omits any background shape entirely (the
    # card silhouette floats on nothing, same as every render before this
    # option existed); "white" adds an opaque backing rect, e.g. for
    # viewers/pipelines that composite onto a dark background and would
    # otherwise show the checker/circle holes as see-through.
    g["Background_Mode"] = lg.get("background", "transparent")
    g["Circle_Fill"] = lg.get("circle_fill", _DEFAULT_CIRCLE_FILL)
    g["Background_Fill"] = lg.get("background_fill", _DEFAULT_BACKGROUND_FILL)
    g["Solid_Fill"] = lg.get("solid_fill", _DEFAULT_SOLID_FILL)
    g["FLATNESS_TOLERANCE_MM"] = lg.get("legend_flatness_tolerance_mm", 0.01)

    hg = lg.get("height_offset_groups", {})
    g["HEIGHT_OFFSET_GROUPS"] = [
        (hg.get("underscore_chars", "_"), hg.get("underscore_offset_mm", 1.0)),
        (hg.get("descender_chars", "pgqjy"), hg.get("descender_offset_mm", 0.4)),
        (hg.get("parenthesis_chars", "()"), hg.get("parenthesis_offset_mm", 0.4)),
        (hg.get("ascender_chars", "fbldtkh"), hg.get("ascender_offset_mm", -0.5)),
    ]

    _configured = True


def _require_configured():
    if not _configured:
        raise RuntimeError("call mignon_legend.configure(config_path) before using this module")


# --------------------------------------------------------------- Grid math
# v1 MignonIndex.scad:164-169 (LocateCenter/LocateBaseline), generalized
# from v1's hardcoded 11/6 (its fixed 12-column/7-row grid) to N_COLS-1/
# N_ROWS-1, matching mignon.py's own row/column-count-agnostic port of
# cylinder_machine.TextRing.

def _locate_center(r, c):
    x = Edge_to_Column + c * (Length - 2 * Edge_to_Column) / (N_COLS - 1)
    y = Edge_to_Row + (N_ROWS - 1 - r) * (Width - 2 * Edge_to_Row) / (N_ROWS - 1)
    return x, y


def _locate_baseline(r, c):
    x, y = _locate_center(r, c)
    return x, y - Height_Offset


def _cell_size():
    """v1's XY (MignonIndex.scad:169) - one grid cell's [width, height]."""
    return ((Length - 2 * Edge_to_Column) / (N_COLS - 1),
            (Width - 2 * Edge_to_Row) / (N_ROWS - 1))


def _inner_border():
    """v1 LiningRectangle() (MignonIndex.scad:260-267) - a thin rectangular
    ring border around the interior 5x10 grid (the area with a visible
    left/right edge where the checker-textured border frame stops and
    the plain interior begins). This is real v1 geometry, but v1's own
    Array2() (the file's actual live output) never calls it - Array1()
    is the only caller, and Array1() is itself dead code (see the
    module docstring) - so v1 never actually draws this border in any
    real output. Exposed here as a genuine, real, OFF-BY-DEFAULT opt-in
    feature (legend.inner_border) rather than silently left out, since
    the underlying geometry is real (not invented) and some users may
    want the explicit border v1's own dead code would have drawn.

    mid_x/mid_y (v1:73-74) - the interior rectangle's edge sits halfway
    between the border column/row (c/r=0) and the first interior column/
    row (c/r=1); mid_xl/mid_yw (v1:76-77) is the interior rectangle's
    full width/height. v1's own hardcoded 11/6 divisors are again N_COLS-1/
    N_ROWS-1 here, matching every other grid-math function in this
    module."""
    if not Inner_Border:
        return None
    step_x, step_y = _cell_size()
    mid_x = Edge_to_Column + step_x / 2.0
    mid_y = Edge_to_Row + step_y / 2.0
    mid_xl = Length - 2 * mid_x
    mid_yw = Width - 2 * mid_y
    cx, cy = Length / 2.0, Width / 2.0
    outer = box(cx - (mid_xl + Line_Width) / 2.0, cy - (mid_yw + Line_Width) / 2.0,
                cx + (mid_xl + Line_Width) / 2.0, cy + (mid_yw + Line_Width) / 2.0)
    inner = box(cx - (mid_xl - Line_Width) / 2.0, cy - (mid_yw - Line_Width) / 2.0,
                cx + (mid_xl - Line_Width) / 2.0, cy + (mid_yw - Line_Width) / 2.0)
    return outer.difference(inner)


def _circle_yfact():
    """v1's repeated scale([1, (Circle_Diameter+2*Circle_Height_Bump)/
    Circle_Diameter]) - every circle/ellipse in the card is squished
    taller than it is wide by this factor."""
    return (Circle_Diameter + 2 * Circle_Height_Bump) / Circle_Diameter


def _ellipse(center, diameter):
    circle = Point(center).buffer(diameter / 2.0, quad_segs=Circle_Segments)
    return shapely_scale(circle, xfact=1.0, yfact=_circle_yfact(), origin=center)


def _char_height_offset(ch):
    """v1's Character_Modifieds/Character_Modifieds_Offset (MignonIndex.
    scad:61-72) - checked in group order; no character appears in more
    than one group across any real layout, so order is inconsequential
    in practice, same as v1."""
    for chars, offset in HEIGHT_OFFSET_GROUPS:
        if ch in chars:
            return offset
    return 0.0


# ---------------------------------------------------------- Glyph shapes

def _glyph_polygon(ch):
    """v1's 2DText() (MignonIndex.scad:461-485) minus the dead Weight_Adj
    branches (see module docstring) - a composed, centered (v1's
    halign="center") shapely polygon for one character, baseline at
    y=0. None for a space or an empty/undrawable glyph.

    NOT glyph-mirrored, despite v1's own mirror([1,0,0]) call at line
    465 - verified against a REAL openscad-nightly render of the actual
    v1 source (MignonIndex.scad, Layout_Selection=5): its own SVG output
    reads with plain, correctly-oriented letters (confirmed directly,
    e.g. row2's physical "B A N I V"/row3's "M T E D L" block both read
    normally, not backwards) despite that mirror() call in the source.
    This is a reference LEGEND, meant to be read directly by a person -
    unlike build_glyph()'s struck-character mirroring (a real physical
    type-slug reads backwards, like a stamp), there is no equivalent
    physical reason for a card meant to be read straight to show
    reversed text, and the real v1 render doesn't. Do not reintroduce
    this without re-checking against a real render first."""
    if ch == " ":
        return None
    face = load_font_face(FONT_PATH)
    scale = em_to_mm_scale(Type_Size, face.units_per_EM)
    contours_mm, advance_mm = get_glyph_contours_and_advance(
        ch, FLATNESS_TOLERANCE_MM, scale, font_path=FONT_PATH)
    if not contours_mm:
        return None
    x_shift = -advance_mm / 2.0
    centered = [c + np.array([x_shift, 0.0]) for c in contours_mm]
    poly = compose_glyph_polygon(centered)
    if poly is None or poly.is_empty:
        return None
    if Weight_Adjustment:
        poly = poly.buffer(Weight_Adjustment, join_style="round")
    return poly


# ------------------------------------------------------- Array2() members

def _radius_rectangle():
    """v1 RadiusRectangle() (MignonIndex.scad:201-212) - hull() of 4
    corner circles == convex_hull of their union in shapely."""
    corners = [
        (Corner_Radius, Corner_Radius),
        (Length - Corner_Radius, Corner_Radius),
        (Length - Corner_Radius, Width - Corner_Radius),
        (Corner_Radius, Width - Corner_Radius),
    ]
    circles = [Point(c).buffer(Corner_Radius, quad_segs=Circle_Segments) for c in corners]
    return unary_union(circles).convex_hull


def _checker_pattern():
    """v1 CheckerPattern() (MignonIndex.scad:214-224) - off by default
    (v1's own comment: "Apply Checker Border? (slow - do last)"), but
    several of v1's own REAL presets turn it on (MignonIndex.json's
    "New set 3" - matching this config's own Layout_Selection=5/Length=
    133/Width=83 exactly - and others), confirmed by directly rendering
    v1 with Checker=true via openscad-nightly: a fine grid of small
    diamond-shaped perforations cut through the card's solid background,
    not a plain alternating black/white checkerboard.

    v1's square(Square_Pattern_Size) is NOT centered (OpenSCAD's
    default) - it spans (0,0) to (size,size), a CORNER at the local
    origin - and `translate([x,y]) rotate([0,0,45]) square(size)`
    rotates that corner-anchored square 45 degrees about its own local
    origin BEFORE translating to the grid point (x,y), same as
    _radius_rectangle()'s corner circles above use Point(corner).buffer()
    (not a centered box) for the same reason: matching v1's real anchor
    point matters, not just the square's size. Building a centered box
    and rotating about ITS OWN center (this function's first, wrong,
    attempt) silently changes where each diamond's centroid ends up
    relative to the (x,y) grid - confirmed visibly wrong (denser/larger-
    looking holes) against a real openscad-nightly render before this
    fix."""
    if not Checker:
        return None
    s = Square_Pattern_Size
    base = box(0, 0, s, s)
    rotated_unit = shapely_rotate(base, 45, origin=(0, 0))
    squares = []
    x = 0.0
    while x <= Length:
        y = 0.0
        while y <= Width:
            squares.append(shapely_translate(rotated_unit, x, y))
            y += Square_Pattern_Pitch
        x += Square_Pattern_Pitch
    return unary_union(squares) if squares else None


def _clear_holes():
    """v1 ClearHoles() (MignonIndex.scad:232-243) - cuts an ellipse at
    EVERY grid position whose mirrored-index character isn't blank
    (placement uses the unmirrored index c, the occupied check uses
    N_COLS-1-c - transcribed exactly as v1 has it; in practice every
    real layout.rows is fully populated, so this cuts all 7xN_COLS
    positions regardless)."""
    ellipses = []
    for r in range(N_ROWS):
        row = ROWS[r]
        for c in range(N_COLS):
            if row[N_COLS - 1 - c] != " ":
                ellipses.append(_ellipse(_locate_center(r, c), Circle_Diameter))
    return unary_union(ellipses) if ellipses else None


def _clear_shape():
    """v1 ClearShape() (MignonIndex.scad:388-398) - cuts a full grid-cell
    rectangle wherever Background_Fill[r][c]==0 (the border row/col stay
    solid; the whole interior gets cut away, leaving isolated circles/
    text placed back in afterward by LineCircles/ArrangeText/SolidShape
    below)."""
    step_x, step_y = _cell_size()
    rects = []
    for r in range(N_ROWS):
        for c in range(N_COLS):
            if Background_Fill[r][c] == 0:
                cx, cy = _locate_center(r, c)
                rects.append(box(cx - step_x / 2, cy - step_y / 2, cx + step_x / 2, cy + step_y / 2))
    return unary_union(rects) if rects else None


def _line_circles():
    """v1 LineCircles() (MignonIndex.scad:433-442) - a thin ring at every
    mirrored grid position where Circle_Fill[r][c]==0 (an "unshifted"
    key) and the character (checked unmirrored, matching v1) isn't
    blank."""
    rings = []
    for r in range(N_ROWS):
        row = ROWS[r]
        for c in range(N_COLS):
            if Circle_Fill[r][c] == 0 and row[c] != " ":
                center = _locate_center(r, N_COLS - 1 - c)
                outer = _ellipse(center, Circle_Diameter + Line_Width)
                inner = _ellipse(center, Circle_Diameter - Line_Width)
                rings.append(outer.difference(inner))
    return unary_union(rings) if rings else None


def _solid_shape():
    """v1 SolidShape() (MignonIndex.scad:400-417) - a solid grid-cell
    square (with the same ClearHoles() ellipses punched through it as
    the card's own background) wherever Solid_Fill[r][c]==1, at the
    mirrored grid position."""
    step_x, step_y = _cell_size()
    rects = []
    for r in range(N_ROWS):
        for c in range(N_COLS):
            if Solid_Fill[r][c] == 1:
                cx, cy = _locate_center(r, N_COLS - 1 - c)
                rects.append(box(cx - step_x / 2, cy - step_y / 2, cx + step_x / 2, cy + step_y / 2))
    if not rects:
        return None
    solid = unary_union(rects)
    holes = _clear_holes()
    return solid.difference(holes) if holes is not None else solid


def _arrange_text():
    """v1 ArrangeText() (MignonIndex.scad:487-502) - for each grid
    position: Circle_Fill[r][c]==0 draws the character as plain ink at
    LocateBaseline (v1's positive 2DText() call); Circle_Fill[r][c]==1
    draws v1's DarkText() - a solid disc with the character shape cut
    OUT of it (difference), which is what makes a "shifted" key read as
    reversed/light-on-dark once the whole card is rendered as one filled
    silhouette (see render_svg())."""
    parts = []
    for r in range(N_ROWS):
        row = ROWS[r]
        for c in range(N_COLS):
            ch = row[c]
            glyph = _glyph_polygon(ch)
            if glyph is None:
                continue
            dy = _char_height_offset(ch)
            if Circle_Fill[r][c] == 0:
                bx, by = _locate_baseline(r, N_COLS - 1 - c)
                parts.append(shapely_translate(glyph, bx, by + dy))
            else:
                cx, cy = _locate_center(r, N_COLS - 1 - c)
                placed = shapely_translate(glyph, cx, cy - Height_Offset + dy)
                disc = _ellipse((cx, cy), Circle_Diameter + Line_Width)
                parts.append(disc.difference(placed))
    return unary_union(parts) if parts else None


def build_legend_geometry():
    """v1 Array2() (MignonIndex.scad:513-524) - the file's actual (only
    live) top-level shape:

        union(
            difference(RadiusRectangle(), CheckerPattern(), ClearHoles(), ClearShape()),
            LineCircles(), ArrangeText(), SolidShape())

    plus _inner_border() - real v1 geometry (LiningRectangle()) that's
    dead code in v1's own actual output, added here as a genuine,
    off-by-default opt-in (legend.inner_border) - see that function's
    docstring.

    Returns one shapely (Multi)Polygon - the whole card as a single flat
    silhouette, exactly like v1's single extruded 2D shape."""
    _require_configured()
    base = _radius_rectangle()
    for cutter in (_checker_pattern(), _clear_holes(), _clear_shape()):
        if cutter is not None:
            base = base.difference(cutter)
    additions = [g for g in (_line_circles(), _arrange_text(), _solid_shape(), _inner_border()) if g is not None]
    return unary_union([base] + additions)


# --------------------------------------------------------------- SVG output

def _ring_path_d(coords):
    pts = list(coords)
    d = f"M {pts[0][0]:.4f},{pts[0][1]:.4f} "
    d += " ".join(f"L {x:.4f},{y:.4f}" for x, y in pts[1:])
    return d + " Z"


def _geometry_path_d(geom):
    """Every shapely Polygon's exterior + interior (hole) rings become
    their own closed SVG subpath; fill-rule="evenodd" on the single
    <path> that wraps them all then reproduces the same solid/hole
    semantics as the boolean geometry itself, with no per-shape styling
    needed - see render_svg()."""
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


def render_svg(fill="#000000", background=None):
    """Serializes build_legend_geometry() to a self-contained SVG string
    (mm units, viewBox sized to Length x Width). Wrapped in a <g
    transform> that flips Y (shapely/v1-OpenSCAD are Y-up; SVG is
    Y-down) instead of flipping every coordinate by hand.

    background: "transparent" (no backing rect - the default, and every
    render before this option existed) or "white" (an opaque backing
    rect behind the card). None (the default here) reads legend.
    background from the config; pass an explicit value to override it,
    same convention as the fill parameter."""
    background = Background_Mode if background is None else background
    geom = build_legend_geometry()
    d = _geometry_path_d(geom)
    bg_rect = (f'  <rect x="0" y="0" width="{Length}" height="{Width}" fill="#ffffff"/>\n'
               if background == "white" else "")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{Length}mm" height="{Width}mm" '
        f'viewBox="0 0 {Length} {Width}">\n'
        f'{bg_rect}'
        f'  <g transform="translate(0,{Width}) scale(1,-1)">\n'
        f'    <path d="{d}" fill="{fill}" fill-rule="evenodd"/>\n'
        '  </g>\n'
        '</svg>\n'
    )
