"""
Generic mesh primitives mirroring OpenSCAD operations used throughout
v2/blickensderfer.scad and lib/core_shaft.scad, so the body assembly can
port each module close to 1:1 instead of hand-deriving transforms per part.
"""

import numpy as np
import trimesh


def revolve_polygon(profile, sections=128):
    """rotate_extrude() equivalent: profile is a closed polygon loop of
    (r, z) points (matches OpenSCAD's polygon([[r,z], ...]) argument to
    rotate_extrude() - X becomes radius, Y becomes Z). The loop is swept
    around the Z axis. No separate end caps are built or needed: since the
    profile itself is already a closed 2D loop, the swept surface is a
    closed 2-manifold on its own (like a torus) - this holds even when the
    profile touches r=0 (the ring at that angle degenerates to a shared
    point, same harmless artifact as a UV-sphere's poles)."""
    profile = np.asarray(profile, dtype=float)
    # Drop consecutive coincident (r,z) points (e.g. a caller-supplied
    # profile with a zero-height "wall" segment, like Core_Taper_Top_Z==
    # Core_Top_Z's repeated point in cylinder_machine.SecondaryCore/
    # CoreEllipses when a machine has no clip - see this function's
    # module-level test/SESSION_LOG for the discovery). Left in, the swept
    # quad between them has zero width, but the two vertex RINGS at that
    # (r,z) stay numerically distinct (indexed by different profile
    # positions) - each only stitches to its OTHER neighbor, leaving a
    # real crack rather than a harmless zero-area face (confirmed:
    # SecondaryCore was not watertight for Bennett, the first machine to
    # hit this). Deduplicating here removes the extra ring entirely so
    # there's nothing to leave unstitched.
    r_tol = 1e-9
    keep = np.ones(len(profile), dtype=bool)
    for j in range(len(profile)):
        j_prev = j - 1
        if np.hypot(*(profile[j] - profile[j_prev])) <= r_tol:
            keep[j] = False
    profile = profile[keep]
    n = len(profile)
    theta = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    r = profile[:, 0][None, :]
    z = profile[:, 1][None, :]
    ct = np.cos(theta)[:, None]
    st = np.sin(theta)[:, None]
    x = r * ct
    y = r * st
    zz = np.broadcast_to(z, (sections, n))
    verts = np.stack([x, y, zz], axis=-1).reshape(-1, 3)

    def idx(i_theta, j_profile):
        return (i_theta % sections) * n + (j_profile % n)

    faces = []
    for i in range(sections):
        i_next = i + 1
        for j in range(n):
            j_next = (j + 1) % n
            if profile[j, 0] <= r_tol and profile[j_next, 0] <= r_tol:
                # both endpoints on the rotation axis: this edge is a
                # segment ON the axis, not swept surface - every angular
                # slice would otherwise emit the same degenerate edge,
                # breaking manifoldness (see conversation: BottomSlopedSpace
                # profile has exactly this case).
                continue
            a, b, c, d = idx(i, j), idx(i_next, j), idx(i_next, j_next), idx(i, j_next)
            j_on_axis = profile[j, 0] <= r_tol
            j_next_on_axis = profile[j_next, 0] <= r_tol
            if j_on_axis:
                # a and b coincide (same axis point regardless of theta) -
                # the quad degenerates to one fan triangle, not two.
                faces.append((a, c, d))
            elif j_next_on_axis:
                # c and d coincide.
                faces.append((a, b, c))
            else:
                faces.append((a, b, c))
                faces.append((a, c, d))
    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def revolve_polygon_partial(profile, start_deg, end_deg, sections=128):
    """rotate_extrude(angle=) equivalent - a PARTIAL sweep of profile
    around the Z axis, from start_deg to end_deg (degrees), unlike
    revolve_polygon's always-360-degree sweep. A partial sweep needs two
    flat end-cap faces the full version doesn't (the swept surface
    doesn't close on itself) - built here as a full 360-degree
    revolve_polygon(), intersected with a wedge solid spanning [start_deg,
    end_deg]. This is mathematically identical to a true partial
    rotate_extrude (sweeping only through that angular range IS the same
    shape as sweeping the full circle then keeping just that wedge), and
    reuses the already-correct/tested full revolve plus a real manifold3d
    boolean instead of hand-triangulating two N-gon (possibly non-convex)
    end caps."""
    profile_arr = np.asarray(profile, dtype=float)
    full = revolve_polygon(profile_arr, sections=sections)
    max_r = np.abs(profile_arr[:, 0]).max() + 1.0
    min_z = profile_arr[:, 1].min() - 1.0
    max_z = profile_arr[:, 1].max() + 1.0
    n_arc = max(2, sections)
    thetas = np.linspace(np.radians(start_deg), np.radians(end_deg), n_arc)
    arc_pts = [(max_r * np.cos(t), max_r * np.sin(t)) for t in thetas]
    from shapely.geometry import Polygon as _ShapelyPolygon
    wedge_poly = _ShapelyPolygon([(0.0, 0.0)] + arc_pts)
    wedge = trimesh.creation.extrude_polygon(wedge_poly, max_z - min_z)
    wedge.apply_translation([0, 0, min_z])
    return full.intersection(wedge, engine="manifold")


def linear_extrude_twist(profile_2d, height, twist_degrees, z_steps=64, base_z=0.0):
    """linear_extrude(height=, twist=) equivalent for an arbitrary closed 2D
    profile (list of (x,y) points, e.g. a discretized circle already
    positioned at its radial offset): at height fraction t=z/height, the
    profile is rotated by twist_degrees*t about the Z axis (matches
    OpenSCAD's twist semantics - unrotated at the base, full twist at the
    top). Caps top and bottom with a simple fan triangulation (valid for
    any convex profile, e.g. a circle - the only shape this is used for
    here)."""
    profile_2d = np.asarray(profile_2d, dtype=float)
    m = len(profile_2d)
    verts = []
    for k in range(z_steps + 1):
        t = k / z_steps
        ang = np.radians(twist_degrees * t)
        ca, sa = np.cos(ang), np.sin(ang)
        rot = np.array([[ca, -sa], [sa, ca]])
        pts = profile_2d @ rot.T
        zc = base_z + height * t
        verts.append(np.column_stack([pts, np.full(m, zc)]))
    verts = np.concatenate(verts, axis=0)

    def idx(k, j):
        return k * m + (j % m)

    faces = []
    for k in range(z_steps):
        for j in range(m):
            a, b, c, d = idx(k, j), idx(k, j + 1), idx(k + 1, j + 1), idx(k + 1, j)
            faces.append((a, b, c))
            faces.append((a, c, d))
    # bottom cap (fan from centroid, facing -Z) and top cap (facing +Z)
    bottom_center_idx = len(verts)
    top_center_idx = len(verts) + 1
    bottom_centroid = verts[0:m].mean(axis=0)
    top_centroid = verts[z_steps * m:(z_steps + 1) * m].mean(axis=0)
    verts = np.vstack([verts, bottom_centroid, top_centroid])
    for j in range(m):
        j_next = (j + 1) % m
        faces.append((bottom_center_idx, idx(0, j_next), idx(0, j)))
        faces.append((top_center_idx, idx(z_steps, j), idx(z_steps, j_next)))

    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def cylinder_z(diameter, height, sections=128, base_z=0.0, center=False,
                z_segments=1):
    """cylinder(d=, h=) equivalent, extruded along +Z from base_z (or
    centered on base_z if center=True, matching OpenSCAD's center=true).

    z_segments splits the SIDE WALL into that many bands of triangles.
    Geometrically identical either way - it only changes how the wall is
    triangulated, which matters for a cylinder other solids get unioned
    INTO (trimesh's default is two triangles per section spanning the
    entire height)."""
    z0 = base_z - height / 2.0 if center else base_z
    if z_segments <= 1:
        c = trimesh.creation.cylinder(radius=diameter / 2.0, height=height, sections=sections)
        c.apply_translation([0, 0, z0 + height / 2.0])
        return c
    zs = np.linspace(0.0, height, int(z_segments) + 1)
    profile = [(0.0, 0.0)] + [(diameter / 2.0, z) for z in zs] + [(0.0, height)]
    c = revolve_polygon(np.array(profile, dtype=float), sections=sections)
    c.apply_translation([0, 0, z0])
    return c


# Target height of one wall band, in mm. Measured, not guessed: sweeping
# the band count on the two machines banding actually helps shows the
# worst sliver plateauing well before the bands get fine, and the FACE
# COUNT turning back up past the plateau -
#
#   bennett   3 bands (6.0mm) -> worst 9.800mm, 247914 faces
#             9 bands (2.0mm) -> worst 9.800mm, 236630 faces  <- best
#            22 bands (0.8mm) -> worst 9.800mm, 237584 faces
#            44 bands (0.4mm) -> worst 9.800mm, 239824 faces
#   mignon   12 bands (3.9mm) -> worst 5.415mm,  71950 faces  <- knee
#           286 bands (0.2mm) -> worst 5.415mm,  77226 faces
#
# so ~2mm sits at or just past both knees while staying near the face
# minimum. This used to be derived from the caller's facet count instead,
# which tied it to a SMOOTHNESS choice rather than to anything the banding
# is protecting against: at Surface_Fn=360 that produced 286 bands of
# 0.163mm on Mignon, costing 5276 faces for zero improvement.
_BAND_TARGET_HEIGHT_MM = 2.0


def square_z_segments(diameter, height, sections=None):
    """How many bands to split a wall into, so the boolean that unions
    characters into it never has a full-height face to shatter. `sections`
    is accepted and ignored - kept so existing call sites need no change,
    and because the angular facet count is deliberately NOT the driver
    (see _BAND_TARGET_HEIGHT_MM)."""
    return max(1, int(round(height / _BAND_TARGET_HEIGHT_MM)))


def frustum_z(d1, d2, height, sections=128, base_z=0.0):
    """cylinder(d1=, d2=, h=) equivalent (a cone frustum), base at base_z."""
    profile = [(0.0, 0.0), (d1 / 2.0, 0.0), (d2 / 2.0, height), (0.0, height)]
    m = revolve_polygon(profile, sections=sections)
    m.apply_translation([0, 0, base_z])
    return m


def torus(center_radius, tube_diameter, sections=128, tube_sections=32):
    """rotate_extrude(){translate([center_radius,0]) circle(d=tube_diameter);}
    equivalent - a torus (ring) profile swept around Z, offset outward by
    center_radius. First shared call sites: lib/wing_slug.py's and lib/
    box_slug.py's Loop() - the same real torus recipe, byte-identical
    between v1/Type Slugs/TypeSlug.scad's and LumiSlug.scad's own Loop
    blocks, extracted here per CLAUDE.md's "when two machines share a
    derivation, extract it" convention rather than hand-copied twice.

    sections drives the sweep-around-the-ring resolution (matches v1's
    own rotate_extrude($fn=360)); tube_sections drives the tube's own
    small-circle cross-section point count SEPARATELY (v1 also uses
    $fn=360 there - circle(d=tube_diameter, $fn=360) - but reusing one
    $fn=360 for BOTH axes of a torus this small is a real, measured
    100x-facet-count blow-up (360*360=129600 vertices for a single
    keyring-style loop torus, confirmed on Lumi Slug's real config
    values, vs. the same shape at tube_sections=32: ~11500 - both
    watertight/valid, only the wasted-density one differs) with no
    visible quality gain on a sub-1mm tube radius - not ported as a
    literal 1:1 facet count for that reason, per CLAUDE.md's "if there's
    no real reason to invent a special-cased number, don't" (here read
    as: an accidentally-uniform $fn in the real v1 source is not itself
    a real reason to keep two geometrically independent axes coupled).
    Exposed as its own config knob (quality.loop_tube_fn) rather than a
    hardcoded default, same as every other facet count in this
    pipeline."""
    theta = np.linspace(0, 2 * np.pi, tube_sections, endpoint=False)
    profile = [(center_radius + tube_diameter / 2.0 * np.cos(t), tube_diameter / 2.0 * np.sin(t)) for t in theta]
    return revolve_polygon(profile, sections=sections)


def angular_wedge(center_deg, width_deg, z_lo, z_hi, r_out):
    """A solid pie-slice about the Z axis: the region within +/-
    width_deg/2 of center_deg, spanning z_lo..z_hi.

    Used to trim a placed character to its own angular slot so a
    Minkowski draft skirt cannot bleed into the neighbouring character's
    (see cylinder_machine._clip_to_cell). Generic on purpose - the
    cylinder, shuttle and spherical families all distribute characters by
    rotation about Z, so all three clip with this same shape.

    Built as ONE triangle (the axis plus a point at each boundary angle)
    extruded in Z, not an arc sector: only the two flat sides ever cut,
    and as planes through the axis they are exact at any radius. The
    chord closing the triangle bows inward by r_out*(1-cos(width/2)),
    so r_out only has to be comfortably beyond the geometry being
    trimmed - it is not a precision surface.
    """
    a0 = np.radians(center_deg - width_deg / 2.0)
    a1 = np.radians(center_deg + width_deg / 2.0)
    verts = np.array([[0.0, 0.0],
                       [r_out * np.cos(a0), r_out * np.sin(a0)],
                       [r_out * np.cos(a1), r_out * np.sin(a1)]])
    wedge = trimesh.creation.extrude_triangulation(
        vertices=verts, faces=np.array([[0, 1, 2]]), height=z_hi - z_lo)
    wedge.apply_translation([0.0, 0.0, z_lo])
    return wedge


def clip_to_angular_cell(mesh, center_deg, width_deg, r_out, margin=1.0):
    """Intersects `mesh` with its own angular cell (see angular_wedge).
    The wedge spans the mesh's own Z extent plus `margin` at each end, so
    it only ever cuts in the angular direction."""
    lo, hi = mesh.bounds[0][2] - margin, mesh.bounds[1][2] + margin
    return mesh.intersection(
        angular_wedge(center_deg, width_deg, lo, hi, r_out), engine="manifold")


def box_centered(extents, center):
    """cube(size, center=true) equivalent placed at an arbitrary center."""
    b = trimesh.creation.box(extents=extents)
    b.apply_translation(center)
    return b


def scad_transform(mesh, *ops):
    """Applies a sequence of ('rotate',[a,b,c]) / ('translate',[x,y,z]) ops
    to mesh, composed in the SAME top-to-bottom order they'd appear in
    OpenSCAD source (rotate(A) translate(B) children() means
    point' = RotA @ (TranslateB @ point), i.e. matrices multiplied
    left-to-right in written order and applied to the child)."""
    combined = np.eye(4)
    for kind, args in ops:
        if kind == "rotate":
            a, b, c = np.radians(args)
            m = trimesh.transformations.euler_matrix(a, b, c, axes="sxyz")
        elif kind == "translate":
            m = trimesh.transformations.translation_matrix(args)
        else:
            raise ValueError(kind)
        combined = combined @ m
    out = mesh.copy()
    out.apply_transform(combined)
    return out


def to_manifold(mesh):
    """trimesh.Trimesh -> manifold3d.Manifold. Promoted from glyph_poc.py's
    private _to_manifold/_from_manifold (build_glyph()/build_flat_text_
    drafted()'s own Minkowski-sum plumbing) once hammond_split.py needed the
    identical conversion for its own from-scratch draft-cone Minkowski sum
    (Minkowski_Cone_Height/Mink_Radius are independent of the extrusion depth there,
    unlike either shared glyph_poc helper - see lib/hammond_split.py's
    _letter_text_drafted()) - a third call site, past this repo's "extract
    shared derivations" threshold. glyph_poc._to_manifold/_from_manifold
    are kept as thin pass-throughs so existing call sites there don't need
    to change."""
    from manifold3d import Manifold, Mesh as ManifoldMesh
    return Manifold(mesh=ManifoldMesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32)))


def from_manifold(manifold):
    """manifold3d.Manifold -> trimesh.Trimesh. See to_manifold()."""
    m = manifold.to_mesh()
    return trimesh.Trimesh(vertices=m.vert_properties, faces=m.tri_verts, process=False)


def mirror(mesh, normal):
    """mirror(v) equivalent: reflects across the plane through the origin
    perpendicular to normal (a 3-vector, not required to be unit length -
    matches OpenSCAD's mirror(), which also normalizes internally).
    Reflection has determinant -1, which flips face winding/normals - but
    trimesh's own Trimesh.apply_transform() already detects a negative-
    determinant transform and corrects winding internally (confirmed: a
    manual .invert() call after apply_transform() here double-flipped it
    back to inverted-normal/negative-volume, is_volume=False - apply_
    transform alone is already correct, do not add a second invert).
    First caller: hammond_split's Mirror(side) (v2/hammond_split.scad),
    mirror([0,1,0]) - the only machine with a real left/right mirrored-
    body pair."""
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    reflect = np.eye(3) - 2.0 * np.outer(n, n)
    m4 = np.eye(4)
    m4[:3, :3] = reflect
    out = mesh.copy()
    out.apply_transform(m4)
    return out


def rotate_z(mesh, degrees):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(degrees), [0, 0, 1]))
    return m


def translate(mesh, offset):
    m = mesh.copy()
    m.apply_translation(offset)
    return m


def union_all(meshes, engine="manifold"):
    """Unions all meshes into one solid. Uses manifold3d's Manifold.
    batch_boolean directly rather than trimesh's mesh.union() folded
    sequentially over the list (result = result.union(m) repeated) -
    confirmed ~30x faster on a real 86-part case (2.43s -> 0.08s,
    identical resulting volume) since batch_boolean doesn't re-grow and
    re-process an ever-larger accumulated mesh on every pairwise step."""
    meshes = [m for m in meshes if m is not None]
    if len(meshes) == 1:
        return meshes[0]
    if engine == "manifold":
        from manifold3d import Manifold, Mesh as ManifoldMesh, OpType
        manifolds = [Manifold(mesh=ManifoldMesh(
            vert_properties=np.array(m.vertices, dtype=np.float32),
            tri_verts=np.array(m.faces, dtype=np.uint32))) for m in meshes]
        result = Manifold.batch_boolean(manifolds, OpType.Add).to_mesh()
        return trimesh.Trimesh(vertices=result.vert_properties, faces=result.tri_verts, process=False)
    result = meshes[0]
    for m in meshes[1:]:
        result = result.union(m, engine=engine)
    return result


def _validity(mesh):
    return {
        "watertight": mesh.is_watertight,
        "winding_consistent": mesh.is_winding_consistent,
        "is_volume": mesh.is_volume,
    }


def check_and_repair(mesh, label="mesh"):
    """Detect + best-effort auto-repair for a combined/assembled mesh
    (e.g. the final Additive-Subtractive result) using trimesh's own
    repair utilities, then re-check and report whether it actually
    worked. This is NOT a fix for inter-part self-intersection (that has
    no simple automatic geometric fix - see
    blickensderfer._check_inter_character_collisions, detection only) -
    it targets the combinatorial defects trimesh.repair already knows how
    to fix: non-manifold holes, inconsistent face winding, inverted
    normals."""
    import trimesh.repair as repair

    before = _validity(mesh)
    print(f"{label}: pre-repair validity = {before}", flush=True)
    if all(before.values()):
        return mesh, before, before, False

    repaired = mesh.copy()
    repair.fill_holes(repaired)
    repair.fix_winding(repaired)
    repair.fix_inversion(repaired)
    repair.fix_normals(repaired)

    after = _validity(repaired)
    print(f"{label}: post-repair validity = {after}", flush=True)
    improved = after != before
    if not all(after.values()):
        print(f"{label}: WARNING - repair did not fully resolve all issues, "
              f"remaining: {[k for k, v in after.items() if not v]}", flush=True)
    return repaired, before, after, improved
