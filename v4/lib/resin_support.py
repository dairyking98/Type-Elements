"""
Resin-support geometry shared across every machine that needs it -
Blickensderfer/Postal/Mignon/Bennett/Hammond all end up here one way or
another (Helios has no resin support at all - see lib/helios.py). Used to
be split across lib/scad_primitives.py (the raw rod/strut shapes) and
lib/cylinder_machine.py (resin_raft_config, and the config-driven
_resin_rod wrapper every non-cylinder machine still reaches into
cylinder_machine for) - consolidated here per explicit request, since the
underlying geometry itself has nothing to do with the cylinder-machine
family specifically. cylinder_machine._resin_rod() and
cylinder_machine.resin_raft_config() are kept as thin pass-throughs to
this module (see their own docstrings) so existing call sites in
blickensderfer.py/postal.py/mignon.py/bennett.py/hammond.py don't need to
change at all - only hammond.py's direct sp.connecting_rod() calls moved
to resin_support.connecting_rod().
"""

import trimesh

import scad_primitives as sp


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

    raft = sp.frustum_z(raft_od, raft_od + 1 * raft_thickness, raft_thickness, sections=resin_fn,
                         base_z=-min_rod_height - raft_thickness)
    return sp.union_all([rod, raft])


def connecting_rod(p1, p2, diameter, subdivisions=2):
    """ConnectingRod(p1, p2, t) from v2/hammond.scad:419 - hull() of two
    equal-diameter spheres at arbitrary points p1/p2 (a capsule strut, not
    tied to any single axis the way resin_rod's tip/rod/raft stack is).
    Ported for Hammond's angled reinforcement rods between adjacent
    resin-support rods (gusseting) - doesn't exist for any other machine's
    resin-support system, since none of them brace rods against each
    other, only against the part/buildplate."""
    s1 = trimesh.creation.icosphere(subdivisions=subdivisions, radius=diameter / 2.0)
    s1.apply_translation(p1)
    s2 = trimesh.creation.icosphere(subdivisions=subdivisions, radius=diameter / 2.0)
    s2.apply_translation(p2)
    return trimesh.util.concatenate([s1, s2]).convex_hull


def vertical_rod(h1, shift, tip_od, tip_l, rod_od, inset, min_rod_height, raft_thickness,
                  raft_od, add_raft=True, resin_fn=20):
    """ResinRod(h1) rebased into a vertical-print-orientation frame, for
    machines (currently only Hammond) whose v2 source wraps the WHOLE
    resin-support union in its own translate([0,0,-shift]) (v2/hammond.scad:
    611's VertResinSupport2, shift=Resin_Support_Min_Height+Resin_Support_
    Base_Thickness). v2's own ResinRod(h1) convention has the raft sit at
    z=0 and the tip at z=h1; this shared resin_rod() (this module's own
    function above) instead has the raft fixed at
    z=-min_rod_height-raft_thickness with the tip at h - subtracting shift
    from h1 here is exactly what reconciles the two conventions, matching
    what every point/height in the caller's v2-faithful coordinate frame
    already assumes. Kept alongside vertical_connecting_rod/rod_tip below
    since all three need the same shift to stay in one consistent frame -
    see hammond.ResinSupport()'s own docstring for the full derivation."""
    return resin_rod(h1 - shift, tip_od, tip_l, rod_od, inset, min_rod_height, raft_thickness,
                      raft_od, add_raft=add_raft, resin_fn=resin_fn)


def vertical_connecting_rod(p1, p2, diameter, shift):
    """connecting_rod(), with both endpoints rebased by the same shift as
    vertical_rod() above - see that function's docstring."""
    return connecting_rod([p1[0], p1[1], p1[2] - shift], [p2[0], p2[1], p2[2] - shift], diameter)


def rod_tip(x, theta_deg, s, z_offset, arc_radius, rod_od, tip_od, tip_l=1.0, sections=128):
    """RodTip() from v2/hammond.scad:596-600 plus its own placement
    (v2:621-624/632-635) - a small oriented needle-point (a cone tapering
    from rod_od down to the narrower tip_od over tip_l, then a tip_od-
    radius sphere) used as the vertical resin support's actual contact
    point against the arc surface - a real, separate shape from
    connecting_rod's own capsule end (which is a plain sphere at the full
    rod_od diameter, with no directional dependence on theta at all).
    The whole needle ROTATES about the X axis by theta_deg*s before being
    translated into position, so its pointed end tilts to follow the arc
    surface's own curvature/normal at that angular position rather than
    pointing in a fixed direction. Op order matches v2 source top-to-
    bottom: translate to the caller's rebased Z0' (z_offset - the same
    shift-cancelled value vertical_rod/vertical_connecting_rod already
    assume - v2's own Z0'=-Z_Offset+Resin_Support_Min_Height+Resin_
    Support_Base_Thickness minus shift reduces to exactly -z_offset),
    rotate by theta_deg*s, THEN translate the raw shape to
    (0,0,arc_radius-tip_l), so the needle's own point reaches exactly
    radius arc_radius before anything else moves it."""
    cone = sp.frustum_z(rod_od, tip_od, tip_l, sections=sections)
    tip_sphere = trimesh.creation.icosphere(subdivisions=2, radius=tip_od / 2.0)
    tip_sphere.apply_translation([0, 0, tip_l])
    shape = sp.union_all([cone, tip_sphere])
    return sp.scad_transform(
        shape,
        ("translate", [x, 0, -z_offset]),
        ("rotate", [theta_deg * s, 0, 0]),
        ("translate", [0, 0, arc_radius - tip_l]),
    )


def raft_config(element_diameter, wall_min_thickness, raft_enabled):
    """Derives (Resin_Rod_Raft, Cut_Groove_Inner_X) from the single
    resin.raft config toggle - called from both Blickensderfer's and
    Postal's configure(), so the two behaviors stay exactly in sync
    rather than risking drift between two independently hand-set YAML
    values.

    raft_enabled=False (Blickensderfer's original v2 default): each
    resin support rod grows its own small individual raft cone
    (Resin_Rod_Raft=True), and CutGroove()'s ring sits right at the wall
    (Cut_Groove_Inner_X=0.0) - many small rafts, no big plate.

    raft_enabled=True (Postal's original v2 default): CutGroove()'s inner
    profile point is pushed all the way to the element's center axis
    (Cut_Groove_Inner_X = -(element_diameter/2 - wall_min_thickness), so
    radius+inner_x lands exactly at X=0), forming ONE continuous raft
    plate shared by every rod - so the rods themselves grow no individual
    raft of their own (Resin_Rod_Raft=False).

    Was two separate, independently-set per-machine config values
    (resin.rod_raft/resin.cut_groove_inner_x) that happened to only ever
    ship in these two combinations - collapsed into one shared toggle
    since Postal's "continuous raft" is a legitimate option for either
    machine, not something inherently Postal-only."""
    if raft_enabled:
        return False, -(element_diameter / 2 - wall_min_thickness)
    return True, 0.0
