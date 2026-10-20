"""
Print-orientation overhang analysis for every generate.py output - a
read-only diagnostic, never touches geometry.

Two parts:

- mesh_overhangs()/report_mesh(): works on ANY finished mesh, every
  machine, in the orientation it is exported in (+Z = build direction,
  i.e. away from the build plate - the frame every ResinPrint() already
  builds in). For each downward-facing face, the overhang angle is the
  face's angle above horizontal: 0 deg = a flat ceiling (worst), 90 deg =
  a vertical wall. Also finds island seeds: downward-facing vertices
  strictly lower than every neighbour, above the part's lowest point. On a polyhedral surface
  a strict vertex minimum is a genuine local minimum, i.e. a spot where a
  layer prints in mid-air unless something below holds it up. On a
  ResinPrint() mesh (supports unioned in) any such seed is a real island;
  on a FullElement() mesh the seeds are exactly where supports have to
  go, so they are expected there.

- spherical_row_overhangs(): the Selectric special case. A spherical
  element's glyphs sit on rows at different latitudes, so their worst
  wall angle depends on the row, and on whether the ball is printed
  upright (teeth down, the ResinPrint() orientation) or inverted. Each
  glyph's draft walls lean draft_angle/2 off the glyph axis (the
  Minkowski cone is built with mink_r = 2*tan(draft/2) over a 2mm
  height - see spherical_machine.SingleMinkowskiChar), and the glyph axis
  is tilted by the row latitude, so a glyph's downward-facing wall rises
  at latitude + draft/2 above horizontal upright, and -latitude + draft/2
  inverted. Negative means the wall faces downward past horizontal: a
  guaranteed island on every glyph in that row. This answers it per row,
  before slicing, without needing the Minkowski build at all.

Thresholds come from config (resin.overhang_warn_deg); this module holds
no machine numbers. The only constant is a relative epsilon for "at the
part's lowest point", same role as the machines' `z` epsilons.
"""

import numpy as np

import build_log

# Relative to the part's largest extent - "is this vertex at the bottom
# of the part", not a machine dimension.
_BASE_EPS_REL = 1e-6
# |normal.z| this close to 1 counts as a horizontal face (float noise).
_FLAT_EPS = 1e-9


def mesh_overhangs(mesh, warn_deg):
    """Returns a dict of overhang statistics for a mesh in print
    orientation. warn_deg may be None (statistics only, no area-below-
    threshold figure)."""
    verts = mesh.vertices
    z = verts[:, 2]
    z0 = float(z.min())
    eps = _BASE_EPS_REL * float(max(mesh.extents.max(), 1.0))

    normals = mesh.face_normals
    areas = mesh.area_faces
    face_zmax = z[mesh.faces].max(axis=1)
    on_base = face_zmax <= z0 + eps
    down = (normals[:, 2] < 0) & ~on_base
    angle = np.degrees(np.arccos(np.clip(-normals[down, 2], 0.0, 1.0)))
    down_area = areas[down]

    edges = mesh.edges_unique
    nbr_min = np.full(len(verts), np.inf)
    np.minimum.at(nbr_min, edges[:, 0], z[edges[:, 1]])
    np.minimum.at(nbr_min, edges[:, 1], z[edges[:, 0]])
    # A strict minimum only seeds an island where the material is ABOVE
    # it (downward-facing vertex normal) - the floor of an upward-facing
    # bowl (e.g. a concave platen-cut glyph face tilted up) is a z minimum
    # too, but it rests on solid material below.
    facing_down = mesh.vertex_normals[:, 2] < 0
    seeds = np.nonzero((z < nbr_min - eps) & (z > z0 + eps) & facing_down)[0]
    seeds = seeds[np.argsort(z[seeds])]

    flat = -normals[down, 2] >= 1.0 - _FLAT_EPS  # numerically horizontal ceilings
    stats = {
        "z0": z0,
        "down_area": float(down_area.sum()),
        "min_angle": float(angle.min()) if len(angle) else None,
        "flat_ceiling_area": float(down_area[flat].sum()),
        "seed_points": verts[seeds],
        "warn_deg": warn_deg,
        "below_warn_area": float(down_area[angle < warn_deg].sum()) if warn_deg is not None else None,
    }
    return stats


def report_mesh(mesh, label, warn_deg, has_supports):
    """Prints the mesh overhang summary through build_log and returns the
    stats dict. has_supports: whether `mesh` already includes support
    geometry (ResinPrint) - decides whether island seeds are a problem or
    simply where supports belong. None = unknown (side outputs like the
    gauge/calibration sets), worded neutrally."""
    s = mesh_overhangs(mesh, warn_deg)
    prefix = f"Overhang {label}"
    if s["min_angle"] is None:
        build_log.note(prefix, "no downward-facing surface above the base")
        return s
    detail = (f"steepest downward face {s['min_angle']:.1f} deg above horizontal, "
              f"downward area {s['down_area']:.1f}mm2")
    if s["below_warn_area"] is not None:
        detail += f", {s['below_warn_area']:.1f}mm2 below {s['warn_deg']:g} deg"
    if s["flat_ceiling_area"] > 0:
        detail += f", {s['flat_ceiling_area']:.2f}mm2 flat ceiling"
    build_log.note(prefix, detail)

    pts = s["seed_points"]
    if len(pts):
        where = "; ".join(f"({p[0]:.2f}, {p[1]:.2f}, z={p[2] - s['z0']:.2f})" for p in pts[:5])
        more = f" (+{len(pts) - 5} more)" if len(pts) > 5 else ""
        msg = (f"{len(pts)} island seed(s), z {pts[0][2] - s['z0']:.2f}-{pts[-1][2] - s['z0']:.2f}mm "
               f"above the base: {where}{more}")
        if has_supports:
            build_log.warn(prefix, msg + " - unsupported local minima, these WILL print as islands")
        elif has_supports is None:
            build_log.note(prefix, msg + " - islands unless this output's supports reach them")
        else:
            build_log.note(prefix, msg + " - no supports in this output, so these are where supports must go")
    elif s["below_warn_area"]:
        # A note, not a warning: support rods land on exactly these
        # shallow faces, and a mesh can't tell a supported ceiling from an
        # unsupported one - the island seeds above are the hard signal.
        build_log.note(prefix, f"no islands; {s['below_warn_area']:.1f}mm2 of overhang is shallower than "
                               f"{s['warn_deg']:g} deg (includes faces the supports hold up)")
    return s


def spherical_row_overhangs(row_latitudes, draft_angle_deg):
    """[(row_index, latitude, upright_deg, inverted_deg), ...] - the
    downward-facing glyph wall's angle above horizontal per row, see
    module docstring."""
    half = draft_angle_deg / 2.0
    return [(i, lat, lat + half, -lat + half) for i, lat in enumerate(row_latitudes)]


def report_spherical_rows(row_latitudes, draft_angle_deg, warn_deg):
    rows = spherical_row_overhangs(row_latitudes, draft_angle_deg)
    prefix = "Overhang rows"
    build_log.note(prefix, f"glyph draft {draft_angle_deg:g} deg (walls lean {draft_angle_deg / 2:g} deg); "
                           f"downward glyph wall angle above horizontal, upright / inverted:")
    for i, lat, up, inv in rows:
        build_log.note(prefix, f"row {i + 1} lat {lat:+.1f}: upright {up:+.1f} deg, inverted {inv:+.1f} deg")
    for orient, k in (("upright", 2), ("inverted", 3)):
        worst = min(rows, key=lambda r: r[k])
        ang = worst[k]
        where = f"row {worst[0] + 1} (lat {worst[1]:+.1f})"
        if ang < 0:
            build_log.warn(prefix, f"{orient}: {where} walls face downward ({ang:+.1f} deg) - "
                                   f"islands on every glyph in that row")
        elif warn_deg is not None and ang < warn_deg:
            build_log.warn(prefix, f"{orient}: {where} walls rise only {ang:.1f} deg, under the "
                                   f"{warn_deg:g} deg threshold - expect droop and single-pixel islands")
    return rows
