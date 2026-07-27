"""Prototype-only, standalone: tests ONE isolated change to the shared
glyph pipeline (glyph_poc.py, used by both cylinder_machine.py and
spherical_machine.py) - swapping glyph_poc.contour_to_points()'s
fixed-points_per_mm contour sampling for adaptive/recursive Bezier
flattening - while keeping everything else (real boolean platen
cylinder subtraction, real Minkowski draft sweep) byte-identical to
today's build_glyph(). An earlier version of this file also tried
replacing the platen's real boolean cut with a per-vertex height-field
Z-warp - abandoned: it produced MORE post-Minkowski faces than the real
pipeline in every character tested (contour points down 46-71%, final
faces still up 24-52%), and separately had a sign error (bulged the
wrong direction - caught by eye, not by the volume-match check, which
barely moved since the platen bulge is tiny next to the Minkowski
taper). Keeping the real boolean cut avoids both problems entirely, so
this version only touches contour generation.

glyph_poc.contour_to_points() subdivides EVERY segment (straight lines
included) at a fixed points_per_mm rate. contour_inspect.py measured
this leaving 90%+ of a straight-stroke glyph's points geometrically
redundant (collinear within DEFAULT_SIMPLIFY_TOLERANCE_MM). Here, curves
are flattened by real adaptive/recursive de Casteljau subdivision with a
flatness-tolerance stopping test (the standard technique behind cairo/
Skia/AGG curve flattening - confirmed against matplotlib.path.Path.
to_polygons(), which implements the same idea, before writing this), and
straight on-curve segments get ZERO subdivision (already flat) - each
curve gets exactly as many points as ITS OWN curvature needs at a given
tol_mm, instead of a length-based guess needing post-hoc simplify()
cleanup.

Produces, per character, exactly 2 STLs for direct A/B comparison:
  <char>_current_pipeline.stl  - build_glyph(), today's real, unmodified
                                  pipeline (fixed points_per_mm contour)
  <char>_adaptive_contour.stl  - same real boolean platen cut + same real
                                  Minkowski sweep, only the contour comes
                                  from adaptive flattening instead

Not part of generate.py/tune.py - never imported by production code.
Run directly:

    python3 lib/heightfield_poc.py A M O l --tol-mm 0.01 --out-dir /tmp/hf
"""
import argparse
import os

import numpy as np
import trimesh
import freetype
from manifold3d import Manifold

import scad_primitives as sp
from glyph_poc import (
    FONT_PATH, FONT_SIZE_MM, PLATEN_RADIUS_MM, CUTOUT_ROW, BASELINE_ROW, TEST_ROW,
    DEFAULT_SEPARATION_MM, MINK_DRAFT_ANGLE, DEFAULT_CONE_SEGMENTS, DEFAULT_SIMPLIFY_TOLERANCE_MM,
    DEFAULT_PLATEN_FN, DEFAULT_MINKOWSKI_ENABLED,
    load_font_face, em_to_mm_scale, alignment_x_offset, classify_and_triangulate,
    get_glyph_contours_and_advance, build_glyph,
)

DEFAULT_DRAFT_ANGLE_DEG = MINK_DRAFT_ANGLE


# --- Adaptive Bezier flattening (recursive de Casteljau + flatness test) ---

def _quad_flat_enough(p0, p1, p2, tol):
    chord = p2 - p0
    norm = np.linalg.norm(chord)
    if norm < 1e-12:
        return np.linalg.norm(p1 - p0) <= tol
    cross = abs(chord[0] * (p1[1] - p0[1]) - chord[1] * (p1[0] - p0[0]))
    return (cross / norm) <= tol


def flatten_quadratic(p0, p1, p2, tol, depth=0, max_depth=20):
    if depth >= max_depth or _quad_flat_enough(p0, p1, p2, tol):
        return [p2]
    q0 = (p0 + p1) / 2.0
    q1 = (p1 + p2) / 2.0
    q2 = (q0 + q1) / 2.0
    return (flatten_quadratic(p0, q0, q2, tol, depth + 1) +
            flatten_quadratic(q2, q1, p2, tol, depth + 1))


def _cubic_flat_enough(p0, p1, p2, p3, tol):
    chord = p3 - p0
    norm = np.linalg.norm(chord)
    if norm < 1e-12:
        return max(np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p0)) <= tol
    d1 = abs(chord[0] * (p1[1] - p0[1]) - chord[1] * (p1[0] - p0[0])) / norm
    d2 = abs(chord[0] * (p2[1] - p0[1]) - chord[1] * (p2[0] - p0[0])) / norm
    return max(d1, d2) <= tol


def flatten_cubic(p0, p1, p2, p3, tol, depth=0, max_depth=20):
    if depth >= max_depth or _cubic_flat_enough(p0, p1, p2, p3, tol):
        return [p3]
    p01 = (p0 + p1) / 2.0
    p12 = (p1 + p2) / 2.0
    p23 = (p2 + p3) / 2.0
    p012 = (p01 + p12) / 2.0
    p123 = (p12 + p23) / 2.0
    p0123 = (p012 + p123) / 2.0
    return (flatten_cubic(p0, p01, p012, p0123, tol, depth + 1) +
            flatten_cubic(p0123, p123, p23, p3, tol, depth + 1))


def contour_to_points_adaptive(points, tags, scale, tol_mm):
    """Same FreeType on/off-curve walk as glyph_poc.contour_to_points, but
    straight on-curve segments pass through with NO subdivision and
    curves are flattened adaptively (see module docstring). Returns
    points already scaled to mm (glyph_poc.contour_to_points returns font
    units - kept in mm here since this is a standalone prototype, not a
    drop-in replacement yet)."""
    n = len(points)
    on = [bool(t & 1) for t in tags]
    is_cubic = [(t & 0x3) == 2 for t in tags]

    if n and not any(on):
        mx = (points[-1][0] + points[0][0]) / 2.0
        my = (points[-1][1] + points[0][1]) / 2.0
        points = [(mx, my)] + list(points)
        tags = [1] + list(tags)
        on = [True] + on
        is_cubic = [False] + is_cubic
        n += 1

    if not on[0]:
        start = next(i for i in range(n) if on[i])
        points = points[start:] + points[:start]
        on = on[start:] + on[:start]
        is_cubic = is_cubic[start:] + is_cubic[:start]

    pts_mm = [np.array(p, dtype=float) * scale for p in points]

    out = [pts_mm[0]]
    i = 1
    cur = out[0]
    while i <= n:
        idx = i % n
        p = pts_mm[idx]
        if on[idx]:
            out.append(p)
            cur = p
            i += 1
        elif is_cubic[idx]:
            ctrl2_idx = (i + 1) % n
            end_idx = (i + 2) % n
            ctrl2 = pts_mm[ctrl2_idx]
            end = pts_mm[end_idx]
            out.extend(flatten_cubic(cur, p, ctrl2, end, tol_mm))
            cur = end
            i += 3
        else:
            nxt_idx = (i + 1) % n
            nxt = pts_mm[nxt_idx]
            if on[nxt_idx]:
                end = nxt
                consumed = 2
            else:
                end = (p + nxt) / 2.0
                consumed = 1
            out.extend(flatten_quadratic(cur, p, end, tol_mm))
            cur = end
            i += consumed
    if np.allclose(out[-1], out[0]):
        out.pop()
    return np.array(out)


def get_glyph_contours_adaptive_mm(char, tol_mm, scale, font_path=None):
    face = load_font_face(font_path or FONT_PATH)
    face.set_char_size(face.units_per_EM)
    face.load_char(char, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
    outline = face.glyph.outline
    advance_mm = face.glyph.advance.x * scale
    contours = []
    start = 0
    for end in outline.contours:
        pts = outline.points[start:end + 1]
        tags = outline.tags[start:end + 1]
        contours.append(contour_to_points_adaptive(pts, tags, scale, tol_mm))
        start = end + 1
    return contours, advance_mm


# --- build_glyph_adaptive_contour: byte-identical to glyph_poc.build_glyph
# except the contour source - real boolean platen cut, real Minkowski
# sweep, unchanged from production ---

def build_glyph_adaptive_contour(char, tol_mm, expansion_width_mm=None,
                                  separation_mm=DEFAULT_SEPARATION_MM, row=TEST_ROW,
                                  align_kwargs=None, font_path=None, font_size_mm=None,
                                  radius_y_offset_mm=None, platen_radius_mm=None,
                                  cone_segments=DEFAULT_CONE_SEGMENTS,
                                  simplify_tolerance_mm=DEFAULT_SIMPLIFY_TOLERANCE_MM,
                                  platen_fn=DEFAULT_PLATEN_FN,
                                  minkowski_enabled=DEFAULT_MINKOWSKI_ENABLED,
                                  draft_angle_deg=DEFAULT_DRAFT_ANGLE_DEG):
    if expansion_width_mm is None:
        expansion_width_mm = separation_mm * np.tan(np.radians(draft_angle_deg / 2.0))
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = load_font_face(fp)
    scale = em_to_mm_scale(fs, face.units_per_EM)

    # --- the one changed line vs. glyph_poc.build_glyph(): adaptive
    # contour instead of get_glyph_contours_and_advance(char,
    # points_per_mm, scale, ...) + the separate "* scale" step it needs
    # (get_glyph_contours_adaptive_mm already returns mm) ---
    contours_mm, advance_mm = get_glyph_contours_adaptive_mm(char, tol_mm, scale, font_path=fp)

    x_shift = alignment_x_offset(char, advance_mm, **(align_kwargs or {}))
    contours_mm = [c + np.array([x_shift, 0.0]) for c in contours_mm]
    contours_mm = [c * np.array([-1.0, 1.0]) for c in contours_mm]  # mirror, same as build_glyph

    if radius_y_offset_mm is None:
        radius_y_offset_mm = CUTOUT_ROW[row] - BASELINE_ROW[row]
    if platen_radius_mm is None:
        platen_radius_mm = PLATEN_RADIUS_MM

    flat = classify_and_triangulate(contours_mm)

    tip_h = min(0.01, separation_mm * 0.01)
    cone_h = separation_mm - tip_h
    block_h = tip_h if minkowski_enabled else separation_mm
    block_z0 = separation_mm - tip_h if minkowski_enabled else 0.0

    if platen_radius_mm > 0:
        platen_radius_real_mm = 1.0 / (2.0 * platen_radius_mm)
        y_min, y_max = flat.vertices[:, 1].min(), flat.vertices[:, 1].max()
        dy_max = max(abs(y_min - radius_y_offset_mm), abs(y_max - radius_y_offset_mm))
        bulge_max = platen_radius_real_mm - np.sqrt(max(platen_radius_real_mm ** 2 - dy_max ** 2, 0.0))
        block_margin = bulge_max * 1.1 + 0.005
    else:
        block_margin = 0.0

    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces,
                                                     block_h + block_margin)
    prism.apply_translation([0, 0, block_z0])

    if platen_radius_mm > 0:
        x_min, x_max = flat.vertices[:, 0].min(), flat.vertices[:, 0].max()
        cyl_length = (x_max - x_min) + 2.0
        cyl_center_x = (x_min + x_max) / 2.0
        platen_radius_real_mm = 1.0 / (2.0 * platen_radius_mm)
        platen_cyl = Manifold.cylinder(cyl_length, platen_radius_real_mm, platen_radius_real_mm,
                                        circular_segments=platen_fn, center=True)
        platen_cyl = platen_cyl.rotate([0, 90, 0])
        platen_cyl = platen_cyl.translate([cyl_center_x, radius_y_offset_mm,
                                            separation_mm + platen_radius_real_mm])
        scalloped = sp.to_manifold(prism) - platen_cyl
    else:
        scalloped = sp.to_manifold(prism)

    if not minkowski_enabled:
        if simplify_tolerance_mm > 0:
            scalloped = scalloped.simplify(simplify_tolerance_mm)
        return sp.from_manifold(scalloped)

    cone = Manifold.cylinder(cone_h, expansion_width_mm, 0.0, circular_segments=cone_segments)
    cone = cone.translate([0, 0, -cone_h])

    drafted = scalloped.minkowski_sum(cone)
    if simplify_tolerance_mm > 0:
        drafted = drafted.simplify(simplify_tolerance_mm)
    return sp.from_manifold(drafted)


def report(mesh, label):
    print(f"  {label}: verts={len(mesh.vertices)} faces={len(mesh.faces)} "
          f"watertight={mesh.is_watertight} winding_consistent={mesh.is_winding_consistent} "
          f"is_volume={mesh.is_volume} volume={mesh.volume:.6f}mm3")


def run_char(char, tol_mm, separation_mm, draft_angle_deg, cone_segments, simplify_tolerance_mm,
             points_per_mm_baseline, out_dir, font_path=None, font_size_mm=None):
    print(f"=== char={char!r} tol_mm={tol_mm} separation_mm={separation_mm} ===")

    mesh_baseline = build_glyph(char, points_per_mm_baseline, separation_mm=separation_mm,
                                 cone_segments=cone_segments,
                                 simplify_tolerance_mm=simplify_tolerance_mm,
                                 draft_angle_deg=draft_angle_deg,
                                 font_path=font_path, font_size_mm=font_size_mm)
    report(mesh_baseline, "current_pipeline")

    mesh_adaptive = build_glyph_adaptive_contour(char, tol_mm, separation_mm=separation_mm,
                                                  cone_segments=cone_segments,
                                                  simplify_tolerance_mm=simplify_tolerance_mm,
                                                  draft_angle_deg=draft_angle_deg,
                                                  font_path=font_path, font_size_mm=font_size_mm)
    report(mesh_adaptive, "adaptive_contour")

    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    scale = em_to_mm_scale(fs, load_font_face(fp).units_per_EM)
    total_old = sum(len(c) for c in
                     get_glyph_contours_and_advance(char, points_per_mm_baseline, scale, font_path=fp)[0])
    total_new = sum(len(c) for c in
                     get_glyph_contours_adaptive_mm(char, tol_mm, scale, font_path=fp)[0])
    print(f"  contour points: old(points_per_mm={points_per_mm_baseline})={total_old} "
          f"new(adaptive tol_mm={tol_mm})={total_new}")

    delta_faces = len(mesh_adaptive.faces) - len(mesh_baseline.faces)
    pct = 100.0 * delta_faces / len(mesh_baseline.faces)
    print(f"  final faces: {len(mesh_baseline.faces)} -> {len(mesh_adaptive.faces)} "
          f"({'+' if delta_faces >= 0 else ''}{delta_faces}, {pct:+.1f}%)")

    os.makedirs(out_dir, exist_ok=True)
    safe = char if char.isalnum() else f"u{ord(char):04x}"
    mesh_baseline.export(os.path.join(out_dir, f"{safe}_current_pipeline.stl"))
    mesh_adaptive.export(os.path.join(out_dir, f"{safe}_adaptive_contour.stl"))
    print(f"  wrote {out_dir}/{safe}_current_pipeline.stl and {safe}_adaptive_contour.stl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("chars", nargs="*", default=["A"])
    parser.add_argument("--tol-mm", type=float, default=DEFAULT_SIMPLIFY_TOLERANCE_MM,
                         help="adaptive contour flatness tolerance (default matches "
                              "glyph_poc.DEFAULT_SIMPLIFY_TOLERANCE_MM).")
    parser.add_argument("--separation-mm", type=float, default=DEFAULT_SEPARATION_MM)
    parser.add_argument("--draft-angle", type=float, default=DEFAULT_DRAFT_ANGLE_DEG)
    parser.add_argument("--cone-segments", type=int, default=DEFAULT_CONE_SEGMENTS)
    parser.add_argument("--simplify-tolerance-mm", type=float, default=DEFAULT_SIMPLIFY_TOLERANCE_MM)
    parser.add_argument("--points-per-mm-baseline", type=float, default=8.0,
                         help="points_per_mm for the current_pipeline build_glyph() "
                              "call and the 'old' contour-point-count comparison.")
    parser.add_argument("--font-path", default=None)
    parser.add_argument("--font-size-mm", type=float, default=None)
    parser.add_argument("--out-dir", default="/tmp/heightfield_poc")
    args = parser.parse_args()

    for ch in args.chars:
        run_char(ch, args.tol_mm, args.separation_mm, args.draft_angle, args.cone_segments,
                  args.simplify_tolerance_mm, args.points_per_mm_baseline, args.out_dir,
                  font_path=args.font_path, font_size_mm=args.font_size_mm)
