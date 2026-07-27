"""Diagnostic-only tool: study how one character's outline gets subdivided
by glyph_poc.contour_to_points() BEFORE anything else touches it (no
triangulation, no extrude, no Minkowski) - built to answer a concrete
question about the shared glyph pipeline (glyph_poc.py, imported by both
lib/cylinder_machine.py and lib/spherical_machine.py): how many of the
sampled polyline points are geometrically redundant (removable without
changing the shape by more than a tolerance) vs. actually load-bearing.

Not part of the generate.py/tune.py build pipeline - read-only, plots
only, never called by production code. Run directly:

    python3 lib/contour_inspect.py A --points-per-mm 8
    python3 lib/contour_inspect.py M --points-per-mm 12 --tol-mm 0.01 --out /tmp/M.png

Redundancy test: walk each closed contour's sampled points in order; a
point is flagged removable if its perpendicular distance to the segment
joining its two NEAREST NON-REMOVABLE neighbors is <= tol_mm (classic
sequential Ramer-Douglas-Peucker-style collinearity check, not a real RDP
pass - deliberately simple since the goal here is to SEE the subdivision,
not to ship a simplifier). This is provenance-agnostic on purpose: it
doesn't matter whether a point came from a straight on-curve segment or a
curve's Bezier sampling in contour_to_points() - if it's within tolerance
of the line between its surviving neighbors, it's not adding shape."""
import argparse
import numpy as np

from glyph_poc import (
    FONT_PATH, FONT_SIZE_MM, load_font_face, em_to_mm_scale,
    get_glyph_contours_and_advance,
)


def point_segment_distance(p, a, b):
    ab = b - a
    denom = np.dot(ab, ab)
    if denom < 1e-12:
        return np.linalg.norm(p - a)
    t = np.clip(np.dot(p - a, ab) / denom, 0.0, 1.0)
    proj = a + t * ab
    return np.linalg.norm(p - proj)


def flag_redundant(points, tol_mm):
    """points: (N,2) closed-contour polyline (no duplicated closing point).
    Returns a bool array, True where a point is removable within tol_mm of
    the line between its surviving neighbors."""
    n = len(points)
    keep = np.ones(n, dtype=bool)
    # Sequential pass: for each point, check against its current (still-kept)
    # neighbors. Iterate a few passes since removing a point changes its
    # neighbors' neighbors - fixed-point, not single-pass.
    for _ in range(6):
        changed = False
        kept_idx = [i for i in range(n) if keep[i]]
        m = len(kept_idx)
        if m <= 3:
            break
        for k in range(m):
            i = kept_idx[k]
            prev_i = kept_idx[(k - 1) % m]
            next_i = kept_idx[(k + 1) % m]
            d = point_segment_distance(points[i], points[prev_i], points[next_i])
            if d <= tol_mm:
                keep[i] = False
                changed = True
        if not changed:
            break
    return ~keep


def inspect(char, points_per_mm, tol_mm, font_path=None, font_size_mm=None):
    fp = font_path or FONT_PATH
    fs = font_size_mm or FONT_SIZE_MM
    face = load_font_face(fp)
    scale = em_to_mm_scale(fs, face.units_per_EM)
    contours_font_units, advance_mm = get_glyph_contours_and_advance(
        char, points_per_mm, scale, font_path=fp)
    contours_mm = [c * scale for c in contours_font_units]

    results = []
    for c in contours_mm:
        redundant = flag_redundant(c, tol_mm)
        results.append((c, redundant))
    return results, advance_mm


def summarize(char, points_per_mm, tol_mm, results):
    total = sum(len(c) for c, _ in results)
    removable = sum(int(r.sum()) for _, r in results)
    print(f"char={char!r} points_per_mm={points_per_mm} tol_mm={tol_mm}")
    print(f"  contours={len(results)}")
    for i, (c, r) in enumerate(results):
        print(f"    contour[{i}]: {len(c)} points, {int(r.sum())} removable "
              f"(<= {tol_mm}mm from surviving-neighbor line), "
              f"{len(c) - int(r.sum())} kept")
    print(f"  TOTAL: {total} points sampled, {removable} removable "
          f"({100.0 * removable / max(total, 1):.1f}%), "
          f"{total - removable} geometrically load-bearing")


def plot(char, points_per_mm, tol_mm, results, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 6))
    for c, r in results:
        closed = np.vstack([c, c[:1]])
        ax.plot(closed[:, 0], closed[:, 1], "-", color="0.75", linewidth=0.8, zorder=1)
        kept = ~r
        ax.scatter(c[kept, 0], c[kept, 1], c="tab:green", s=14, zorder=3, label="kept")
        ax.scatter(c[r, 0], c[r, 1], c="tab:red", s=14, zorder=3, label="removable")
    # de-dup legend
    handles, labels = ax.get_legend_handles_labels()
    seen = {}
    for h, l in zip(handles, labels):
        seen.setdefault(l, h)
    ax.legend(seen.values(), seen.keys(), loc="upper right", fontsize=8)
    ax.set_aspect("equal")
    ax.set_title(f"char={char!r} points_per_mm={points_per_mm} tol_mm={tol_mm}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("chars", nargs="*", default=["A"])
    parser.add_argument("--points-per-mm", type=float, default=8.0)
    parser.add_argument("--tol-mm", type=float, default=0.005,
                         help="collinearity tolerance for flagging a point removable.")
    parser.add_argument("--font-path", default=None)
    parser.add_argument("--font-size-mm", type=float, default=None)
    parser.add_argument("--out", default=None,
                         help="PNG path to plot the first char to. If omitted with "
                              "multiple chars, writes out_<char>.png per char.")
    args = parser.parse_args()

    for ch in args.chars:
        results, advance_mm = inspect(ch, args.points_per_mm, args.tol_mm,
                                       font_path=args.font_path, font_size_mm=args.font_size_mm)
        summarize(ch, args.points_per_mm, args.tol_mm, results)
        out_path = args.out if (args.out and len(args.chars) == 1) else f"out_contour_{ch}.png"
        plot(ch, args.points_per_mm, args.tol_mm, results, out_path)
