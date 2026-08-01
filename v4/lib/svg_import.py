"""
Minimal SVG <path> importer, for the Vogue foundry mark and the generic
AR1 logo (lib/wing_slug.py's Logo feature, ported from v1/Type Slugs/
TypeSlug.scad's/VogueSlug.scad's `import(SVG_File, center=true)` +
minkowski() draft). v1 relied on OpenSCAD's own built-in SVG importer;
v4 has none (see requirements.txt - no svg/xml geometry library), so
this is a real, from-scratch path-data parser, not a shortcut - per
CLAUDE.md's geometry invariants, the logo still has to go through the
same real Minkowski/boolean pipeline as every struck character.

Scope: only <path d="..."> elements are read (no <rect>/<circle>/<use>/
gradient/clip content in any SVG this repo actually uses - AR1.svg,
vogue-foundry-*.svg, helios-klimax.svg - confirmed by inspection), across
the standard SVG path command set (M/L/H/V/C/S/Q/T/A, upper absolute +
lower relative, Z close). Curve flattening reuses glyph_poc's adaptive de
Casteljau subdivision (flatten_cubic/flatten_quadratic) - same
flatness_tolerance_mm knob, same technique, not a separate/second
curve-flattening scheme.

<g transform="..."> IS handled (translate/scale/rotate/matrix, chained,
inherited down the tree) - added when porting Helios's logo
(helios-klimax.svg, a potrace-style export) surfaced a real case: its
paths sit inside `<g transform="translate(0,906) scale(0.1,-0.1)">`, a
10x-oversized-then-rescaled-and-Y-flipped coordinate convention common to
potrace/Illustrator output. AR1.svg/vogue-foundry-*.svg happen to have no
such wrapper (flat <path> list, identity transform), which is why the
original "confirmed by inspection" scope note above didn't catch this -
inspect the SPECIFIC file being ported, not just the two already in use,
before assuming this stays true for a new one. flatness_tolerance_mm's
conversion to raw-unit tolerance (see parse_svg_contours_mm) only
accounts for scale_mm_per_unit, not any additional <g> scale - a nested
group scale just means curves get flattened a bit finer than strictly
necessary, never coarser/wrong, so this is a performance nit, not a
correctness gap.

Coordinate convention: SVG authoring space is Y-DOWN; this module
returns Y-UP mm contours (negates Y after scaling) so a parsed logo
reads right-side-up next to the rest of v4's Y-up geometry - a
DELIBERATE v4-only convention, not a port of OpenSCAD's own import(svg)
pixel/DPI scaling (which OpenSCAD derives from a 96px/inch assumption
baked into its importer - reproducing that exactly would need empirical
calibration against openscad-nightly the way glyph_poc.
OPENSCAD_TEXT_DPI_FACTOR was for text(), and this is a decorative logo
mark, not a physically-toleranced struck character, so it isn't worth
that same calibration effort). Callers pick their own mm-per-SVG-unit
scale explicitly (config's logo.svg_scale_mm_per_unit / logo.
svg_v1_scale_mm_per_unit) rather than inheriting v1's SVG_Scale=1/40
constants, which were tuned against OpenSCAD's own (different) import
convention and would not mean the same thing here.
"""

import re
import xml.etree.ElementTree as ET

import numpy as np

from glyph_poc import flatten_cubic, flatten_quadratic


_TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
_TRANSFORM_FN_RE = re.compile(r"(\w+)\s*\(([^)]*)\)")


def _tokenize(d):
    return _TOKEN_RE.findall(d)


def _parse_transform(s):
    """SVG transform="..." -> 3x3 homogeneous 2D affine matrix. Supports
    translate/scale/rotate/matrix (every function actually seen in this
    repo's SVGs), applied left-to-right per the SVG spec (each function
    right-multiplies onto the accumulated matrix, same composition order
    as nesting that many individual <g> elements)."""
    m = np.eye(3)
    for name, args in _TRANSFORM_FN_RE.findall(s):
        vals = [float(v) for v in re.split(r"[,\s]+", args.strip()) if v]
        if name == "translate":
            tx, ty = vals[0], (vals[1] if len(vals) > 1 else 0.0)
            f = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
        elif name == "scale":
            sx = vals[0]
            sy = vals[1] if len(vals) > 1 else sx
            f = np.array([[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]])
        elif name == "rotate":
            a = np.radians(vals[0])
            cx, cy = (vals[1], vals[2]) if len(vals) > 2 else (0.0, 0.0)
            c, sn = np.cos(a), np.sin(a)
            rot = np.array([[c, -sn, 0.0], [sn, c, 0.0], [0.0, 0.0, 1.0]])
            to_origin = np.array([[1.0, 0.0, -cx], [0.0, 1.0, -cy], [0.0, 0.0, 1.0]])
            back = np.array([[1.0, 0.0, cx], [0.0, 1.0, cy], [0.0, 0.0, 1.0]])
            f = back @ rot @ to_origin
        elif name == "matrix":
            a, b, c, d, e, ff = vals
            f = np.array([[a, c, e], [b, d, ff], [0.0, 0.0, 1.0]])
        else:
            continue
        m = m @ f
    return m


def _apply_affine(pts, m):
    homo = np.concatenate([pts, np.ones((len(pts), 1))], axis=1)
    return (homo @ m.T)[:, :2]


def _flatten_arc(p0, rx, ry, phi_deg, large_arc, sweep, p1, tol):
    """Elliptical arc (SVG path A/a) -> flattened points. Endpoint-to-
    center parameterization (SVG 1.1 spec appendix F.6), then split into
    cubic Bezier segments <=90deg each via the standard unit-circle-arc
    control-point formula (k = 4/3*tan(delta/4)), transformed by
    (rx,ry,phi) and flattened at the real flatness_tolerance_mm via
    glyph_poc.flatten_cubic. Degenerate rx/ry/coincident-endpoint cases
    fall back to a straight line, matching the spec's own "treat as
    line" rule."""
    x1, y1 = p0
    x2, y2 = p1
    if (x1, y1) == (x2, y2):
        return []
    rx_, ry_ = abs(rx), abs(ry)
    if rx_ < 1e-9 or ry_ < 1e-9:
        return [np.array([x2, y2])]

    phi = np.radians(phi_deg)
    cphi, sphi = np.cos(phi), np.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cphi * dx2 + sphi * dy2
    y1p = -sphi * dx2 + cphi * dy2

    lam = (x1p ** 2) / (rx_ ** 2) + (y1p ** 2) / (ry_ ** 2)
    if lam > 1:
        s = np.sqrt(lam)
        rx_, ry_ = rx_ * s, ry_ * s

    sign = -1.0 if large_arc == sweep else 1.0
    num = rx_ ** 2 * ry_ ** 2 - rx_ ** 2 * y1p ** 2 - ry_ ** 2 * x1p ** 2
    denom = rx_ ** 2 * y1p ** 2 + ry_ ** 2 * x1p ** 2
    co = sign * np.sqrt(max(0.0, num / denom)) if denom > 1e-12 else 0.0
    cxp = co * rx_ * y1p / ry_
    cyp = -co * ry_ * x1p / rx_

    cx = cphi * cxp - sphi * cyp + (x1 + x2) / 2.0
    cy = sphi * cxp + cphi * cyp + (y1 + y2) / 2.0

    def _angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        length = np.hypot(ux, uy) * np.hypot(vx, vy)
        ang = np.arccos(np.clip(dot / length, -1.0, 1.0))
        return ang if (ux * vy - uy * vx) >= 0 else -ang

    ux, uy = (x1p - cxp) / rx_, (y1p - cyp) / ry_
    vx, vy = (-x1p - cxp) / rx_, (-y1p - cyp) / ry_
    theta1 = _angle(1.0, 0.0, ux, uy)
    dtheta = _angle(ux, uy, vx, vy)
    if sweep == 0 and dtheta > 0:
        dtheta -= 2 * np.pi
    elif sweep == 1 and dtheta < 0:
        dtheta += 2 * np.pi

    n_segments = max(1, int(np.ceil(abs(dtheta) / (np.pi / 2.0))))
    delta = dtheta / n_segments
    k = 4.0 / 3.0 * np.tan(delta / 4.0)

    def _point(theta):
        ex = rx_ * np.cos(theta)
        ey = ry_ * np.sin(theta)
        return np.array([cphi * ex - sphi * ey + cx, sphi * ex + cphi * ey + cy])

    def _deriv(theta):
        ex = -rx_ * np.sin(theta)
        ey = ry_ * np.cos(theta)
        return np.array([cphi * ex - sphi * ey, sphi * ex + cphi * ey])

    out = []
    cur = np.array([x1, y1])
    for i in range(n_segments):
        t0 = theta1 + i * delta
        t1 = t0 + delta
        p_end = _point(t1)
        c1 = cur + k * _deriv(t0)
        c2 = p_end - k * _deriv(t1)
        out.extend(flatten_cubic(cur, c1, c2, p_end, tol))
        cur = p_end
    return out


def _parse_path_d(d, flatness_tolerance_mm):
    """Walks one <path>'s d= command string into a list of closed
    subpaths (each a list of (x,y) np.arrays, absolute user-space
    units). Multiple M-started subpaths in one d= string are common
    (a glyph-like mark with a counter/hole) - each becomes its own
    closed contour, left for the caller's classify_and_triangulate()
    nesting-depth fill logic to sort hole vs. island, same as a font's
    multi-contour glyph."""
    tokens = _tokenize(d)
    i = 0
    n = len(tokens)

    def read_floats(count):
        nonlocal i
        vals = [float(tokens[i + k]) for k in range(count)]
        i += count
        return vals

    subpaths = []
    cur = np.array([0.0, 0.0])
    subpath_start = cur
    current_pts = None
    cmd = None
    prev_cubic_ctrl = None
    prev_quad_ctrl = None

    while i < n:
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
        # else: implicit repeat of the previous command (SVG shorthand)
        is_rel = cmd.islower()
        c = cmd.upper()

        if c == "M":
            x, y = read_floats(2)
            if is_rel and current_pts is not None:
                x, y = cur[0] + x, cur[1] + y
            cur = np.array([x, y])
            if current_pts:
                subpaths.append(current_pts)
            current_pts = [cur]
            subpath_start = cur
            cmd = "l" if is_rel else "L"  # subsequent bare coord pairs are lineto
        elif c == "L":
            x, y = read_floats(2)
            if is_rel:
                x, y = cur[0] + x, cur[1] + y
            cur = np.array([x, y])
            current_pts.append(cur)
        elif c == "H":
            (x,) = read_floats(1)
            if is_rel:
                x = cur[0] + x
            cur = np.array([x, cur[1]])
            current_pts.append(cur)
        elif c == "V":
            (y,) = read_floats(1)
            if is_rel:
                y = cur[1] + y
            cur = np.array([cur[0], y])
            current_pts.append(cur)
        elif c == "C":
            x1, y1, x2, y2, x, y = read_floats(6)
            if is_rel:
                x1, y1 = cur[0] + x1, cur[1] + y1
                x2, y2 = cur[0] + x2, cur[1] + y2
                x, y = cur[0] + x, cur[1] + y
            p1, p2, p3 = np.array([x1, y1]), np.array([x2, y2]), np.array([x, y])
            current_pts.extend(flatten_cubic(cur, p1, p2, p3, flatness_tolerance_mm))
            prev_cubic_ctrl = p2
            cur = p3
        elif c == "S":
            x2, y2, x, y = read_floats(4)
            if is_rel:
                x2, y2 = cur[0] + x2, cur[1] + y2
                x, y = cur[0] + x, cur[1] + y
            p1 = 2 * cur - prev_cubic_ctrl if prev_cubic_ctrl is not None else cur
            p2, p3 = np.array([x2, y2]), np.array([x, y])
            current_pts.extend(flatten_cubic(cur, p1, p2, p3, flatness_tolerance_mm))
            prev_cubic_ctrl = p2
            cur = p3
        elif c == "Q":
            x1, y1, x, y = read_floats(4)
            if is_rel:
                x1, y1 = cur[0] + x1, cur[1] + y1
                x, y = cur[0] + x, cur[1] + y
            p1, p2 = np.array([x1, y1]), np.array([x, y])
            current_pts.extend(flatten_quadratic(cur, p1, p2, flatness_tolerance_mm))
            prev_quad_ctrl = p1
            cur = p2
        elif c == "T":
            x, y = read_floats(2)
            if is_rel:
                x, y = cur[0] + x, cur[1] + y
            p1 = 2 * cur - prev_quad_ctrl if prev_quad_ctrl is not None else cur
            p2 = np.array([x, y])
            current_pts.extend(flatten_quadratic(cur, p1, p2, flatness_tolerance_mm))
            prev_quad_ctrl = p1
            cur = p2
        elif c == "A":
            rx, ry, xrot, large_arc, sweep, x, y = read_floats(7)
            if is_rel:
                x, y = cur[0] + x, cur[1] + y
            end = np.array([x, y])
            current_pts.extend(_flatten_arc(cur, rx, ry, xrot, int(large_arc), int(sweep), end,
                                             flatness_tolerance_mm))
            cur = end
        elif c == "Z":
            cur = subpath_start
            if current_pts and not np.allclose(current_pts[-1], subpath_start):
                current_pts.append(subpath_start)
        else:
            raise ValueError(f"unsupported SVG path command {c!r}")

        if c not in ("C", "S", "Q", "T"):
            prev_cubic_ctrl = None
            prev_quad_ctrl = None

    if current_pts:
        subpaths.append(current_pts)

    out = []
    for pts in subpaths:
        arr = np.array([p for p in pts])
        if len(arr) >= 2 and np.allclose(arr[0], arr[-1]):
            arr = arr[:-1]
        if len(arr) >= 3:
            out.append(arr)
    return out


def parse_svg_contours_mm(svg_path, flatness_tolerance_mm, scale_mm_per_unit, center=True):
    """Reads every <path> in svg_path (namespace-agnostic - SVG's default
    xmlns means ElementTree tags come back as "{http://www.w3.org/2000/
    svg}path", matched here via a local-name check rather than a
    hardcoded namespace string), flattens each into closed 2D contours,
    scales to mm, and flips Y (SVG authoring convention is Y-down - see
    module docstring). Returns a flat list of (x,y) np.ndarrays ready
    for glyph_poc.classify_and_triangulate() - multiple <path> elements
    and multiple M-subpaths within one path are both just more contours
    in that same flat list, correctly resolved into solid/hole material
    by classify_and_triangulate's own nesting-depth logic (no separate
    per-path handling needed).

    center=True (the default, matching v1's only usage - `import(file,
    center=true)` at every real call site) shifts every contour so the
    WHOLE file's combined bounding box is centered on the origin.
    Centering commutes with the uniform scale/Y-flip already applied
    above (no rotation/skew involved), so doing it here in output mm
    space rather than in raw SVG-unit space beforehand is equivalent to
    OpenSCAD's own pre-transform centering, just simpler to express."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    contours = []
    tol_units = flatness_tolerance_mm / scale_mm_per_unit

    def walk(elem, parent_m):
        tag = elem.tag.split("}")[-1]
        t = elem.get("transform")
        m = parent_m @ _parse_transform(t) if t else parent_m
        if tag == "path":
            d = elem.get("d")
            if d:
                for contour in _parse_path_d(d, tol_units):
                    contour = _apply_affine(contour, m)
                    pts = contour * scale_mm_per_unit
                    pts[:, 1] *= -1.0
                    contours.append(pts)
        for child in elem:
            walk(child, m)

    walk(root, np.eye(3))
    if center and contours:
        all_pts = np.concatenate(contours, axis=0)
        bbox_center = (all_pts.min(axis=0) + all_pts.max(axis=0)) / 2.0
        contours = [c - bbox_center for c in contours]
    return contours


def build_svg_logo_mesh_2d(svg_paths, flatness_tolerance_mm, scale_mm_per_unit, offsets=None):
    """Parses one or more SVG files (e.g. VogueSlug's separate arrow +
    V marks, each with its own placement offset - v1/Type Slugs/
    VogueSlug.scad:113-121) into ONE combined flat (z=0) triangulated
    trimesh.Trimesh, via glyph_poc.classify_and_triangulate - the same
    hole/island nesting-depth fill logic used for real font glyphs,
    reused here since a multi-path logo mark has exactly the same
    "which contour is solid vs. a hole" problem. offsets, if given, is a
    list of (dx, dy) mm shifts applied per svg_paths entry BEFORE fill
    classification (so two marks placed side by side don't need their
    own separate triangulation/union - matching v1's own single
    minkowski(){ linear_extrude { import(); import(); } } construction,
    which drafts the two pieces as one combined swept solid, not two
    separately-drafted ones unioned after)."""
    from glyph_poc import classify_and_triangulate

    if offsets is None:
        offsets = [(0.0, 0.0)] * len(svg_paths)
    all_contours = []
    for svg_path, (dx, dy) in zip(svg_paths, offsets):
        contours = parse_svg_contours_mm(svg_path, flatness_tolerance_mm, scale_mm_per_unit)
        for c in contours:
            all_contours.append(c + np.array([dx, dy]))
    return classify_and_triangulate(all_contours)
