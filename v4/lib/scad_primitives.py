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

    r_tol = 1e-9
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


def cylinder_z(diameter, height, sections=128, base_z=0.0, center=False):
    """cylinder(d=, h=) equivalent, extruded along +Z from base_z (or
    centered on base_z if center=True, matching OpenSCAD's center=true)."""
    z0 = base_z - height / 2.0 if center else base_z
    c = trimesh.creation.cylinder(radius=diameter / 2.0, height=height, sections=sections)
    c.apply_translation([0, 0, z0 + height / 2.0])
    return c


def frustum_z(d1, d2, height, sections=128, base_z=0.0):
    """cylinder(d1=, d2=, h=) equivalent (a cone frustum), base at base_z."""
    profile = [(0.0, 0.0), (d1 / 2.0, 0.0), (d2 / 2.0, height), (0.0, height)]
    m = revolve_polygon(profile, sections=sections)
    m.apply_translation([0, 0, base_z])
    return m


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


def rotate_z(mesh, degrees):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(degrees), [0, 0, 1]))
    return m


def translate(mesh, offset):
    m = mesh.copy()
    m.apply_translation(offset)
    return m


def resin_rod(h, tip_od, tip_l, rod_od, inset, min_rod_height, raft_thickness,
              raft_od, add_raft=True, resin_fn=20, eps=0.01):
    """ResinRod(h) from lib/resin_rod.scad: hull() of a small tapered tip
    (tip_od sphere hulled down to a rod_od sphere, offset tip_l below the
    attachment point h) continued down to a second rod_od sphere near the
    print bed, plus an optional small raft frustum at the very bottom.
    h is the Z height (in the caller's frame) where the rod's tip attaches
    to the model - everything below is fixed (bed-relative), only the tip
    end moves with h."""
    tip_z = -tip_od / 2 + inset + h
    upper_small_z = tip_z - tip_l
    lower_z = -min_rod_height - raft_thickness + rod_od / 2 + eps

    tip_sphere = trimesh.creation.icosphere(subdivisions=2, radius=tip_od / 2)
    tip_sphere.apply_translation([0, 0, tip_z])
    upper_small = trimesh.creation.icosphere(subdivisions=2, radius=rod_od / 2)
    upper_small.apply_translation([0, 0, upper_small_z])
    lower_sphere = trimesh.creation.icosphere(subdivisions=2, radius=rod_od / 2)
    lower_sphere.apply_translation([0, 0, lower_z])

    rod = trimesh.util.concatenate([tip_sphere, upper_small, lower_sphere]).convex_hull

    if not add_raft:
        return rod

    raft = frustum_z(raft_od, raft_od + 1 * raft_thickness, raft_thickness, sections=resin_fn,
                      base_z=-min_rod_height - raft_thickness)
    return union_all([rod, raft])


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
