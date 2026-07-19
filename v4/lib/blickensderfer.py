"""
v4 full-fidelity Blickensderfer body - ports v2/blickensderfer.scad's
Additive()/Subtractive()/FullElement() structure directly, using the SAME
origin/orientation convention as the OpenSCAD file (Z=0 at the bottom face
of the main disk, Z+ up through the clip end; Baseline_Z_Offset shifts the
negative-from-clip-end Baseline/Cutout arrays into this absolute frame).

All real-machine numbers live in config/blickensderfer.yaml, not here -
call configure(path) once before using anything else in this module (see
generate.py). Derived values (Shaft_Diameter, Clip_OD, etc.) are computed
in configure() from that file's base parameters, matching how
v2/blickensderfer.scad itself derives them.
"""

import time

import freetype
import numpy as np
import trimesh
import yaml

from glyph_poc import (
    build_glyph, build_flat_text, get_glyph_contours_and_advance,
    DEFAULT_CONE_SEGMENTS as GLYPH_DEFAULT_CONE_SEGMENTS,
    DEFAULT_SIMPLIFY_TOLERANCE_MM as GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM,
    DEFAULT_PLATEN_FN as GLYPH_DEFAULT_PLATEN_FN,
    DEFAULT_MINKOWSKI_ENABLED as GLYPH_DEFAULT_MINKOWSKI_ENABLED,
)
import scad_primitives as sp

_configured = False


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - base
    parameters copied straight from the file, derived ones computed the
    same way v2/blickensderfer.scad (and lib/core_shaft.scad,
    lib/resin_support.scad) derive them from their own base parameters."""
    global _configured
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["FONT_SIZE_MM"] = font["size_mm"]

    logo = cfg["logo"]
    g["LOGO_FONT_PATH"] = logo["font_path"]
    g["Logo_Text"] = logo["text"]
    g["Logo_Text_Size"] = logo["text_size_mm"]
    g["Logo_Text_Spacing"] = logo["text_spacing"]
    g["Logo_Position_Offset"] = logo["position_offset_deg"]
    g["Logo_Text_Offset"] = logo["text_offset_deg"]
    # real v2 value - the logo ring's placement radius = Logo_Radius +
    # this. Exposed as a tunable: at the real value, the logo's angular
    # spacing can coincidentally land very close to a DHIATENSOR column
    # (confirmed once, on this exact layout - see SESSION_LOG.md) since
    # nothing forces separation between the two independent layouts.
    g["Logo_Radial_Offset"] = logo.get("radial_offset_mm", 1.5)

    e = cfg["element"]
    g["z"] = 0.01
    g["Element_Diameter"] = e["element_diameter"]
    g["Platen_Diameter"] = e["platen_diameter"]
    g["Min_Final_Character_Diameter"] = e["min_final_character_diameter"]
    g["Char_Protrusion"] = (e["min_final_character_diameter"] - e["element_diameter"]) / 2.0
    g["Element_Height"] = e["element_height"]
    g["Wall_Min_Thickness"] = e["wall_min_thickness"]
    g["Wall_Chamfer"] = e["wall_chamfer"]
    g["Roof_Offset"] = e["roof_offset"]
    g["Speed_Hole_ID"] = e["speed_hole_id"]
    g["Speed_Hole_Qty"] = e["speed_hole_qty"]
    g["Speed_Hole_Radial"] = e["speed_hole_radial"]
    g["Core_ID_In"] = e["core_id_in"]
    g["Core_ID_Mm"] = e["core_id_in"] * 25.4
    g["Core_Groove_Qty"] = e["core_groove_qty"]
    g["Core_Groove_D"] = e["core_groove_d"]
    g["Core_Chamfer"] = e["core_chamfer"]
    g["Core_Bottom_Offset"] = e["core_bottom_offset"]
    g["Core_Contact_Length"] = e["core_contact_length"]
    g["Core_Web_Width"] = e["core_web_width"]
    g["Core_Web_Qty"] = e["core_web_qty"]
    g["Core_Web_Length"] = e["core_web_length"]
    g["Core_Secondary_ID_Offset"] = e["core_groove_d"] / 2 + g["z"]
    g["Clip_Height"] = e["clip_height"]
    g["Clip_Wire_OD"] = e["clip_wire_od"]
    g["Clip_Opening"] = e["clip_opening"]
    g["Clip_Bite"] = e["clip_bite"]
    g["Drive_Pin_Widthmm"] = e["drive_pin_widthmm"]
    g["Drive_Pin_Length"] = e["drive_pin_length"]
    g["Drive_Pin_Radial"] = e["drive_pin_radial"]
    g["Drive_Pin_Countersink_Depth"] = e["drive_pin_countersink_depth"]
    g["Drive_Pin_Support_Radial_Offset"] = e["drive_pin_support_radial_offset"]
    g["Drive_Pin_Support_Height"] = e["drive_pin_support_height"]
    g["Drive_Pin_Style"] = e["drive_pin_style"]
    g["Core_ID_Offset"] = e["core_id_offset"]
    g["Drive_Pin_Width_Offset"] = e["drive_pin_width_offset"]

    g["Shaft_Diameter"] = g["Core_ID_Mm"] + g["Core_ID_Offset"]
    g["Drive_Pin_Width"] = g["Drive_Pin_Widthmm"] + g["Drive_Pin_Width_Offset"]
    g["Drive_Pin_Countersink_ID"] = np.sqrt(g["Drive_Pin_Width"] ** 2 + g["Drive_Pin_Length"] ** 2)
    g["Clip_OD"] = g["Shaft_Diameter"] + 2 * g["Wall_Min_Thickness"]
    g["Logo_Radius"] = g["Element_Diameter"] / 2 - 2.0

    g["Core_Top_Z"] = g["Element_Height"] + g["Clip_Height"]
    g["Core_Bottom_Z"] = g["Core_Bottom_Offset"]
    g["Core_Taper_Top_Z"] = g["Element_Height"]

    q = cfg["quality"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Groove_Fn"] = q["groove_fn"]
    # Body_Fn: the main visible/cosmetic element body (Cylinder/
    # ClipCylinder) - kept separate from Surface_Fn (everything else
    # structural: HollowSpace, SpeedHoles, chamfers, resin details) and
    # from Cyl_Fn (the inner shaft/core bore only) per user direction -
    # not merged into either even though it may be set to the same value.
    g["Body_Fn"] = q.get("body_fn", q["surface_fn"])
    # Platen_Fn: circular segments for the real platen cutout cylinder in
    # glyph_poc.build_glyph (see its docstring) - not in older configs, so
    # defaults to glyph_poc's own default rather than requiring every
    # config file to be updated.
    g["Platen_Fn"] = q.get("platen_fn", GLYPH_DEFAULT_PLATEN_FN)

    layout = cfg["layout"]
    g["BASELINE_ROW"] = layout["baseline_row"]
    g["CUTOUT_ROW"] = layout["cutout_row"]
    g["LATITUDE_INT"] = 360.0 / layout["latitude_columns"]
    g["BASELINE_Z_OFFSET"] = g["Element_Height"]
    g["PLACEMENT_MAP"] = layout["placement_map"]
    g["DHIATENSOR"] = layout["rows"]

    g["PLATEN_RADIUS_MM"] = 1.0 / g["Platen_Diameter"]

    align = cfg["alignment"]
    g["ALIGN_KWARGS"] = {
        "mode": align["mode"],
        "center_offset_mm": align["center_offset_mm"],
        "left_offset_mm": align["left_offset_mm"],
        "modified_left_chars": align["modified_left_chars"],
        "modified_left_offset_mm": align["modified_left_offset_mm"],
        "modified_right_chars": align["modified_right_chars"],
        "modified_right_offset_mm": align["modified_right_offset_mm"],
    }

    b = cfg["build"]
    g["DEFAULT_POINTS_PER_MM"] = b["points_per_mm"]
    g["DEFAULT_SEPARATION_MM"] = b["separation_mm"]
    g["DEFAULT_RENDER_CORE_GROOVE"] = b["render_core_groove"]
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]
    # circular segments for build_glyph's Minkowski cone kernel - see
    # glyph_poc.DEFAULT_CONE_SEGMENTS docstring. Lives under quality.
    # minkowski_fn now (grouped with the other facet-count knobs); still
    # falls back to the older build.cone_segments key, then glyph_poc's
    # own default, so existing configs don't need to be updated.
    g["DEFAULT_CONE_SEGMENTS"] = q.get("minkowski_fn", b.get("cone_segments", GLYPH_DEFAULT_CONE_SEGMENTS))
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", GLYPH_DEFAULT_SIMPLIFY_TOLERANCE_MM)
    # Off = skip build_glyph's Minkowski sweep entirely (fast, undrafted
    # preview - see glyph_poc.DEFAULT_MINKOWSKI_ENABLED docstring).
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", GLYPH_DEFAULT_MINKOWSKI_ENABLED)

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Min_Rod_Height"] = r["min_rod_height"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Raft_Thickness"] = r["raft_thickness"]
    g["Resin_Groove_OD"] = r["groove_od"]
    g["Resin_Groove_Thickness"] = r["groove_thickness"]
    g["Resin_Rod_Raft"] = r["rod_raft"]
    g["Cut_Groove_Inner_X"] = r["cut_groove_inner_x"]
    g["Bottom_Support_Fractions"] = r["bottom_support_fractions"]
    g["Bottom_Support_Inner_Angle_Offset"] = r["bottom_support_inner_angle_offset"]

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    # [Shaft Gauge Test] - see GaugeTestSet()'s docstring. .get() with v2's
    # own defaults so older configs without a `gauge:` section still work.
    gauge = cfg.get("gauge", {})
    g["Gauge_Offset_Start"] = gauge.get("offset_start", 0.0)
    g["Gauge_Offset_Int"] = gauge.get("offset_int", 0.025)

    # bottomZ/bottomX, ported exactly from lib/resin_support.scad
    # (Blickensderfer takes the lib defaults - no override in
    # blickensderfer.scad).
    g["Bottom_Slope"] = g["Core_Bottom_Offset"] / (
        (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
        - (g["Element_Diameter"] / 2 - g["Wall_Min_Thickness"] - g["Wall_Chamfer"]))
    g["Bottom_Z_Offset"] = (-g["Bottom_Slope"] * (g["Shaft_Diameter"] / 2 + g["Wall_Min_Thickness"] + g["Wall_Chamfer"])
                            + g["Core_Bottom_Offset"])

    _configured = True


def _require_configured():
    if not _configured:
        raise RuntimeError("call blickensderfer.configure(config_path) before using this module")


# ---------------------------------------------------------------- Additive

def Cylinder():
    return sp.cylinder_z(Element_Diameter, Element_Height, sections=Body_Fn)


def ClipCylinder(Offset):
    c = sp.cylinder_z(Clip_OD + Offset, Clip_Height + z, sections=Body_Fn)
    return sp.translate(c, [0, 0, Element_Height - z])


def place_on_cylinder(mesh, row, col, separation_mm):
    """LetterPlacement() equivalent - see conversation for the full
    derivation from rotate([90,0,90])+translate((R+protrusion),0,0)+
    translate(0,0,textBaseline)+rotate([0,0,angle]).

    Radial anchor: the platen-bite point (the print face's deepest/
    narrowest point, at y=radius_y_offset where the scallop is zero, i.e.
    mesh z_local=separation_mm exactly) sits at
    Element_Diameter/2+Char_Protrusion - a FIXED real-machine value, not
    separation_mm. The root (z_local=0) sits INWARD from that anchor by
    separation_mm - the base pushes toward the axis as it widens (like a
    nail driven in with a wide head sitting proud), not flush-and-sideways."""
    v = mesh.vertices
    x_local, y_local, z_local = v[:, 0], v[:, 1], v[:, 2]
    radial = (Element_Diameter / 2.0 + Char_Protrusion - separation_mm) + z_local
    axial = BASELINE_Z_OFFSET + BASELINE_ROW[row] + y_local
    lateral = x_local
    placement_col = PLACEMENT_MAP[col]
    angle = np.radians((0.5 + placement_col) * LATITUDE_INT)
    ca, sa = np.cos(angle), np.sin(angle)
    world_x = radial * ca - lateral * sa
    world_y = radial * sa + lateral * ca
    new_v = np.stack([world_x, world_y, axial], axis=1)
    # process=False: this is a pure coordinate move (rotation+translation),
    # topology is unchanged - trimesh's default process=True re-runs vertex
    # merging on construction, which was found to CORRUPT already-valid
    # self-unioned meshes here (identity-transform reconstruction alone
    # reproduced it: 2195->1507 vertices, watertight True->False - nothing
    # to do with the rotation/translation itself, purely re-processing a
    # mesh that's already correct).
    return trimesh.Trimesh(vertices=new_v, faces=mesh.faces, process=False)


def TextRing(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None):
    """Per-character self-intersection ('the draft offset folds through
    itself on narrow features like H's inter-stroke gap or m's diagonal
    junctions') used to be a real, unsolved problem here - build_glyph now
    builds the draft via a real Minkowski sum (manifold3d), which cannot
    produce that defect on any input topology (see build_glyph's
    docstring). So there's nothing left to detect/report per character;
    only inter-character collisions (a placement/spacing issue, unrelated
    to a single glyph's own geometry) are still checked below."""
    _require_configured()
    points_per_mm = DEFAULT_POINTS_PER_MM if points_per_mm is None else points_per_mm
    separation_mm = DEFAULT_SEPARATION_MM if separation_mm is None else separation_mm
    align_kwargs = ALIGN_KWARGS if align_kwargs is None else align_kwargs
    cone_segments = DEFAULT_CONE_SEGMENTS if cone_segments is None else cone_segments
    simplify_tolerance_mm = (DEFAULT_SIMPLIFY_TOLERANCE_MM if simplify_tolerance_mm is None
                              else simplify_tolerance_mm)
    platen_fn = Platen_Fn if platen_fn is None else platen_fn
    minkowski_enabled = (DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None
                          else minkowski_enabled)
    parts = []
    skipped = []
    total = sum(len(DHIATENSOR[r]) for r in (0, 1, 2))
    n = 0
    t_start = time.perf_counter()
    for row in (0, 1, 2):
        for col, ch in enumerate(DHIATENSOR[row]):
            n += 1
            # flush=True: generate.py's stdout is piped (not a TTY) when
            # run from tune.py's subprocess, which defaults to full block
            # buffering - without an explicit flush every line here would
            # sit in the buffer and only appear as one dump at exit,
            # defeating the point of live per-character progress
            print(f"TextRing: [{n}/{total}] building {ch!r} (row {row}, col {col})...",
                  end="", flush=True)
            t0 = time.perf_counter()
            try:
                mesh = build_glyph(
                    ch, points_per_mm, separation_mm=separation_mm, row=row,
                    align_kwargs=align_kwargs, font_path=FONT_PATH, font_size_mm=FONT_SIZE_MM,
                    radius_y_offset_mm=CUTOUT_ROW[row] - BASELINE_ROW[row],
                    platen_radius_mm=PLATEN_RADIUS_MM, cone_segments=cone_segments,
                    simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
                    minkowski_enabled=minkowski_enabled)
            except Exception as e:
                skipped.append((row, col, ch, str(e)))
                print(f" SKIPPED ({e})", flush=True)
                continue
            print(f" {time.perf_counter() - t0:.2f}s", flush=True)
            parts.append(place_on_cylinder(mesh, row, col, separation_mm))
    print(f"TextRing: all characters built in {time.perf_counter() - t_start:.1f}s", flush=True)
    print(f"TextRing: placed {len(parts)}, skipped {len(skipped)}: {skipped}", flush=True)

    collisions = _check_inter_character_collisions(parts)
    if collisions:
        print(f"TextRing: {len(collisions)} inter-character collisions detected "
              f"(detection only, not repaired): {sorted(collisions)}", flush=True)

    # Real union, not trimesh.util.concatenate: characters routinely overlap
    # each other (the collisions just reported above) and every character's
    # root overlaps the main Cylinder() by design (that's the whole point of
    # "embedded"). concatenate() just merges vertex/face arrays with no
    # boolean resolution at all - both surfaces stay fully intact and
    # superimposed wherever they overlap, so no new edge forms where they
    # actually intersect (confirmed: concatenating text_ring+Cylinder+
    # ClipCylinder measured 1148mm3 MORE volume than a real union of the
    # same parts - the double-counted overlap). sp.union_all() uses
    # manifold3d's real boolean union instead.
    return sp.union_all(parts), parts


def _check_inter_character_collisions(parts):
    """Real mesh-vs-mesh collision check between DIFFERENT character
    parts (trimesh.collision.CollisionManager IS designed for exactly
    this - between distinct registered objects - unlike the earlier,
    meaningless single-mesh use of in_collision_internal() from the
    conversation history, which never flags anything because there's
    nothing else registered to collide with)."""
    cm = trimesh.collision.CollisionManager()
    for i, part in enumerate(parts):
        cm.add_object(str(i), part)
    _, names = cm.in_collision_internal(return_names=True)
    return names


def Additive(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None):
    text_ring, char_parts = TextRing(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                      cone_segments=cone_segments,
                                      simplify_tolerance_mm=simplify_tolerance_mm,
                                      platen_fn=platen_fn, minkowski_enabled=minkowski_enabled)
    return sp.union_all([text_ring, Cylinder(), ClipCylinder(0)]), char_parts


# ------------------------------------------------------------- Subtractive

def Core(Offset):
    c = sp.cylinder_z(Shaft_Diameter + Offset, Element_Height + Clip_Height + 2 * z,
                       sections=Cyl_Fn)
    return sp.translate(c, [0, 0, -z])


def SpeedHoles():
    parts = []
    for n in range(Speed_Hole_Qty):
        h = sp.cylinder_z(Speed_Hole_ID, Element_Height + 2 * z, sections=Surface_Fn,
                           base_z=-z + (Element_Height / 2.0 if n == 0 else 0.0))
        h = sp.translate(h, [Speed_Hole_Radial, 0, 0])
        h = sp.rotate_z(h, 360.0 / Speed_Hole_Qty * n)
        parts.append(h)
    return sp.union_all(parts)


def _hollow_space_profile():
    return [
        (Shaft_Diameter / 2 + Wall_Min_Thickness, Wall_Min_Thickness + Wall_Chamfer + Core_Bottom_Offset),
        (Shaft_Diameter / 2 + Wall_Min_Thickness, Element_Height - Wall_Min_Thickness - Wall_Chamfer),
        (Shaft_Diameter / 2 + Wall_Min_Thickness + Wall_Chamfer, Element_Height - Wall_Min_Thickness),
        ((Shaft_Diameter + Element_Diameter) / 4, Element_Height - Wall_Min_Thickness + Roof_Offset),
        (Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer, Element_Height - Wall_Min_Thickness),
        (Element_Diameter / 2 - Wall_Min_Thickness, Element_Height - Wall_Min_Thickness - Wall_Chamfer),
        (Element_Diameter / 2 - Wall_Min_Thickness, Wall_Min_Thickness + Wall_Chamfer),
        (Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer, Wall_Min_Thickness),
        (Shaft_Diameter / 2 + Wall_Min_Thickness + Wall_Chamfer, Wall_Min_Thickness + Core_Bottom_Offset),
    ]


def HollowSpace():
    body = sp.revolve_polygon(_hollow_space_profile(), sections=Surface_Fn)
    countersink_id = Drive_Pin_Countersink_ID if Drive_Pin_Style == 0 else None
    radius = Drive_Pin_Radial if Drive_Pin_Style == 0 else None
    cutter = sp.cylinder_z(countersink_id + 2 * Drive_Pin_Support_Radial_Offset,
                            Drive_Pin_Countersink_Depth + Drive_Pin_Support_Height,
                            sections=Surface_Fn)
    cutter = sp.translate(cutter, [radius, 0, 0])
    return body.difference(cutter, engine="manifold")


def _bottom_x(zval):
    return (zval - Bottom_Z_Offset) / Bottom_Slope


def BottomSlopedSpace():
    profile = [
        (0, -z - 5),
        (0, Core_Bottom_Offset),
        (_bottom_x(Core_Bottom_Offset), Core_Bottom_Offset),
        (Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer, 0),
        (Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer + 5, 0),
        (Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer + 5, -z - 5),
    ]
    return sp.revolve_polygon(profile, sections=Surface_Fn)


def TopMinkCleanup():
    outer = sp.cylinder_z(Element_Diameter, 5, sections=Surface_Fn, base_z=Element_Height)
    inner = sp.cylinder_z(Element_Diameter - 15, 15, sections=Surface_Fn,
                           base_z=Element_Height, center=True)
    return outer.difference(inner, engine="manifold")


def WireBite():
    """WireBite(): rotate([0,0,-90]) translate([...]) rotate([90,0,0])
    linear_extrude(Clip_OD+2z) hull(circle, square). Built as: true 2D
    shapely hull (matching OpenSCAD's hull() exactly) -> extrude_polygon
    along LOCAL Z (matching linear_extrude's own axis) -> the full
    rotate/translate/rotate stack applied via scad_transform, in the same
    top-to-bottom order as the SCAD source."""
    from shapely.geometry import Point, box as shapely_box
    from shapely.ops import unary_union

    circle_poly = Point(Clip_Wire_OD / 2, Clip_Wire_OD / 2).buffer(Clip_Wire_OD / 2, resolution=32)
    sq_x0 = Clip_Bite + (Clip_OD - Shaft_Diameter) / 2
    square_poly = shapely_box(sq_x0, 0, sq_x0 + z, Clip_Opening)
    hull_poly = unary_union([circle_poly, square_poly]).convex_hull

    shape = trimesh.creation.extrude_polygon(hull_poly, Clip_OD + 2 * z)

    out = sp.scad_transform(
        shape,
        ("rotate", [0, 0, -90]),
        ("translate", [Shaft_Diameter / 2 - Clip_Bite, Clip_OD / 2 + z, Element_Height]),
        ("rotate", [90, 0, 0]),
    )
    return out


def SecondaryCore(Offset):
    """lib/core_shaft.scad - Blickensderfer sets Core_Taper_Top_Z=Element_Height
    (below the clip), distinct from Core_Top_Z=Element_Height+Clip_Height."""
    taper_top_z = Core_Taper_Top_Z
    profile = [
        (0, Core_Bottom_Z + Core_Contact_Length),
        (0, Core_Top_Z),
        (Shaft_Diameter / 2 + Offset / 2 + Core_Secondary_ID_Offset, Core_Top_Z),
        (Shaft_Diameter / 2 + Offset / 2 + Core_Secondary_ID_Offset, taper_top_z),
        (Shaft_Diameter / 2 + Offset / 2, taper_top_z - Core_Secondary_ID_Offset),
        (Shaft_Diameter / 2 + Offset / 2, taper_top_z - Core_Contact_Length),
        (Shaft_Diameter / 2 + Offset / 2 + Core_Secondary_ID_Offset,
         taper_top_z - Core_Contact_Length - Core_Secondary_ID_Offset),
        (Shaft_Diameter / 2 + Offset / 2 + Core_Secondary_ID_Offset,
         Core_Bottom_Z + Core_Contact_Length + Core_Secondary_ID_Offset),
        (Shaft_Diameter / 2 + Offset / 2, Core_Bottom_Z + Core_Contact_Length),
    ]
    return sp.revolve_polygon(profile, sections=Surface_Fn)


def CoreGrooves(Offset):
    parts = []
    circle_theta = np.linspace(0, 2 * np.pi, Groove_Fn, endpoint=False)
    r = Core_Groove_D / 2.0
    radial = Shaft_Diameter / 2 + Offset / 2
    profile = np.column_stack([radial + r * np.cos(circle_theta), r * np.sin(circle_theta)])
    height = Core_Top_Z + 2 * z
    twist_span = Core_Top_Z - Core_Bottom_Z + 2 * z
    for n in range(Core_Groove_Qty):
        sign = 1 if n % 2 == 0 else -1
        twist = 360 * twist_span / (np.pi * (Shaft_Diameter + Offset)) * sign
        groove = sp.linear_extrude_twist(profile, height=height, twist_degrees=twist,
                                          z_steps=96, base_z=-z)
        groove = sp.rotate_z(groove, 360.0 / Core_Groove_Qty * n)
        parts.append(groove)
    return sp.union_all(parts)


def CoreChamferShape(Offset):
    return sp.frustum_z(Shaft_Diameter + Offset + 2 * Core_Chamfer,
                         Shaft_Diameter + Offset, Core_Chamfer + z, sections=Surface_Fn)


def CoreChamfer(Offset, chamfer_top=True):
    bottom = sp.translate(CoreChamferShape(Offset), [0, 0, Core_Bottom_Z - z])
    parts = [bottom]
    if chamfer_top:
        top_shape = CoreChamferShape(Offset + Core_Secondary_ID_Offset / 2)
        top = sp.scad_transform(top_shape,
                                 ("translate", [0, 0, Core_Top_Z + z]),
                                 ("rotate", [180, 0, 0]))
        parts.append(top)
    return sp.union_all(parts)


def CoreEllipses():
    taper_top_z = Core_Taper_Top_Z
    parts = []
    for n in range(Core_Web_Qty):
        c1 = sp.cylinder_z(Core_Web_Width, 5, sections=32, base_z=0)
        c1 = sp.translate(c1, [0, Core_Web_Width / 2.0, 0])
        c2 = sp.cylinder_z(Core_Web_Width, 5, sections=32, base_z=0)
        c2 = sp.translate(c2, [0, Core_Web_Length - Core_Web_Width / 2.0, 0])
        shape = trimesh.util.concatenate([c1, c2]).convex_hull
        shape = sp.scad_transform(
            shape,
            ("translate", [0, 0, Core_Bottom_Z + (taper_top_z - Core_Bottom_Z) / 2 - Core_Web_Length / 2]),
            ("rotate", [90, 0, 90]),
        )
        shape = sp.rotate_z(shape, n * 360.0 / Core_Web_Qty)
        parts.append(shape)
    return sp.union_all(parts)


def LogoText(points_per_mm=20.0):
    """LogoText(): each character gets its own angular position, sitting
    flat on the XY plane (extruded along Z, not wrapped radially like
    TextRing characters) near the top face. halign=center in the real
    file centers on the advance box (see docs/text-centering.md); this
    port centers on the ink bbox HORIZONTALLY instead - a simplification,
    fine for a decorative logo, not attempted to match exactly.

    Vertically, characters are aligned by BASELINE (y=0, FreeType's own
    pen-origin convention - get_glyph_contours applies no baseline shift),
    not by ink-bbox center. Centering each character on its own ink bbox
    independently (the original approach) put every character at a
    different height depending on its own ascender/descender/x-height -
    e.g. 'L' (cap-height, no descender) and 'e' (x-height only) would
    each get centered on a different Y, breaking a common baseline across
    the ring. Baseline alignment is the standard convention for setting
    multi-character text for exactly this reason."""
    n_chars = len(Logo_Text)
    parts = []
    for n, ch in enumerate(Logo_Text):
        if ch == " ":
            continue
        mesh = build_flat_text(ch, points_per_mm, 0.4, font_size_mm=Logo_Text_Size,
                                font_path=LOGO_FONT_PATH)
        center_x = (mesh.bounds[0][0] + mesh.bounds[1][0]) / 2.0
        mesh.apply_translation([-center_x, 0, 0])

        angle_n = Logo_Position_Offset - 90 + Logo_Text_Spacing * n - (n_chars - 1) * Logo_Text_Spacing / 2
        placed = sp.scad_transform(mesh, ("rotate", [0, 0, Logo_Text_Offset]))
        placed = sp.translate(placed, [0, Logo_Radius + Logo_Radial_Offset, Element_Height - 0.3])
        placed = sp.rotate_z(placed, angle_n)
        parts.append(placed)
    return sp.union_all(parts)


def DrivePin():
    if Drive_Pin_Style != 0:
        raise NotImplementedError("Drive_Pin_Style=1 (old) not ported")
    pin = trimesh.creation.box(extents=[Drive_Pin_Width, Drive_Pin_Length, 5])
    pin = sp.scad_transform(
        pin,
        ("translate", [Drive_Pin_Radial, 0, -z + 2.5]),
        ("rotate", [0, 0, 90]),
    )
    sink = sp.cylinder_z(Drive_Pin_Countersink_ID, z + Drive_Pin_Countersink_Depth, sections=Surface_Fn)
    sink = sp.translate(sink, [Drive_Pin_Radial, 0, -z])
    return sp.union_all([pin, sink])


# ------------------------------------------------------------------ Element

def Subtractive(render_core_groove=None):
    render_core_groove = DEFAULT_RENDER_CORE_GROOVE if render_core_groove is None else render_core_groove
    parts = [
        Core(0),
        CoreChamfer(0),
        WireBite(),
        SpeedHoles(),
        HollowSpace(),
        DrivePin(),
        BottomSlopedSpace(),
        SecondaryCore(0),
        CoreEllipses(),
        TopMinkCleanup(),
        LogoText(),
    ]
    if render_core_groove:
        parts.append(CoreGrooves(0))
    print("Subtractive: unioning", len(parts), "parts", flush=True)
    return sp.union_all(parts)


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                 cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None):
    _require_configured()
    additive, char_parts = Additive(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                     cone_segments=cone_segments,
                                     simplify_tolerance_mm=simplify_tolerance_mm,
                                     platen_fn=platen_fn, minkowski_enabled=minkowski_enabled)
    print(f"Additive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    subtractive = Subtractive(render_core_groove)
    print(f"Subtractive (unioned): verts={len(subtractive.vertices)} faces={len(subtractive.faces)} "
          f"watertight={subtractive.is_watertight}", flush=True)
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="FullElement")
    return full, char_parts


# ------------------------------------------------------------- Resin support
# lib/resin_rod.scad + lib/resin_support.scad - cylinder-machine-family
# (Blickensderfer/Postal only) print supports. ResinSupport() is UNIONED
# onto FullElement() (support material to be broken off after printing),
# not subtracted - matches ResinPrint() = union(FullElement(), ResinSupport()).

def _resin_rod(h, add_raft=None):
    add_raft = Resin_Rod_Raft if add_raft is None else add_raft
    return sp.resin_rod(h, Resin_Tip_OD, Resin_Tip_L, Resin_Rod_OD, Resin_Inset,
                         Resin_Min_Rod_Height, Resin_Raft_Thickness, Resin_Raft_OD,
                         add_raft=add_raft, resin_fn=Resin_Fn)


def _bottom_z(xval):
    return Bottom_Slope * xval + Bottom_Z_Offset


def CutGroove():
    """CutGroove(): rotate_extrude() of (ring profile - 2 circular holes),
    at radius Element_Diameter/2-Wall_Min_Thickness. The 2D difference
    happens BEFORE the revolve in the real file, so each hole becomes a
    full 360deg toroidal channel (a continuous score line to snap the
    support ring off), not discrete point perforations. Built as
    revolve(profile) - revolve(hole1) - revolve(hole2), since revolving is
    linear with respect to this kind of cross-section boolean."""
    inner_x = Cut_Groove_Inner_X
    wmt = Wall_Min_Thickness
    radius = Element_Diameter / 2 - Wall_Min_Thickness
    profile = [
        (radius + inner_x, -Resin_Min_Rod_Height - Resin_Raft_Thickness),
        (radius + inner_x, -Resin_Min_Rod_Height),
        (radius + wmt - Resin_Groove_OD - Resin_Groove_Thickness, -Resin_Groove_OD),
        (radius + wmt - Resin_Groove_OD - Resin_Groove_Thickness, z),
        (radius + wmt, z),
        (radius + wmt, -Resin_Min_Rod_Height),
        (radius + wmt + Resin_Raft_Thickness, -Resin_Min_Rod_Height),
        (radius + wmt, -Resin_Min_Rod_Height - Resin_Raft_Thickness),
    ]
    base = sp.revolve_polygon(profile, sections=Surface_Fn)

    hole_r = Resin_Groove_OD / 2
    theta = np.linspace(0, 2 * np.pi, 32, endpoint=False)

    def circle_profile(cx, cz):
        return np.column_stack([cx + hole_r * np.cos(theta), cz + hole_r * np.sin(theta)])

    hole1 = sp.revolve_polygon(circle_profile(radius + wmt, -Resin_Groove_OD / 2), sections=Surface_Fn)
    hole2 = sp.revolve_polygon(
        circle_profile(radius + wmt - Resin_Groove_OD - Resin_Groove_Thickness, -Resin_Groove_OD / 2),
        sections=Surface_Fn)

    return base.difference(hole1, engine="manifold").difference(hole2, engine="manifold")


def SpeedHoleSupport():
    parts = []
    r1 = Speed_Hole_Radial + Speed_Hole_ID / 2 + Resin_Tip_OD / 2
    parts.append(sp.translate(_resin_rod(_bottom_z(r1)), [r1, 0, 0]))
    r2 = Speed_Hole_Radial - Speed_Hole_ID / 2 - Resin_Tip_OD / 2
    parts.append(sp.translate(_resin_rod(_bottom_z(r2)), [r2, 0, 0]))
    r3 = np.hypot(Speed_Hole_Radial, Speed_Hole_ID / 2 + Resin_Tip_OD / 2)
    parts.append(sp.translate(_resin_rod(_bottom_z(r3)), [Speed_Hole_Radial, Speed_Hole_ID / 2 + Resin_Tip_OD / 2, 0]))
    r4 = np.hypot(Speed_Hole_Radial, Speed_Hole_ID / 2 + Resin_Tip_OD / 2)
    parts.append(sp.translate(_resin_rod(_bottom_z(r4)), [Speed_Hole_Radial, -(Speed_Hole_ID / 2 + Resin_Tip_OD / 2), 0]))
    return sp.union_all(parts)


def SpeedHoleSupports():
    parts = []
    for n in range(Speed_Hole_Qty):
        if n == 0:
            continue
        parts.append(sp.rotate_z(SpeedHoleSupport(), 360.0 / Speed_Hole_Qty * n))
    return sp.union_all(parts)


def DrivePinSupport(radius, half_extent_x, half_extent_y):
    parts = []
    x1 = radius + half_extent_x + Resin_Tip_OD / 2
    parts.append(sp.translate(_resin_rod(_bottom_z(x1)), [x1, 0, 0]))
    x2 = radius - half_extent_x - Resin_Tip_OD / 2
    parts.append(sp.translate(_resin_rod(_bottom_z(x2)), [x2, 0, 0]))
    r3 = np.hypot(radius, half_extent_y + Resin_Tip_OD / 2)
    parts.append(sp.translate(_resin_rod(_bottom_z(r3)), [radius, half_extent_y + Resin_Tip_OD / 2, 0]))
    parts.append(sp.translate(_resin_rod(_bottom_z(r3)), [radius, -(half_extent_y + Resin_Tip_OD / 2), 0]))
    return sp.union_all(parts)


def BottomSupports():
    fractions = Bottom_Support_Fractions
    inner_angle_offset = Bottom_Support_Inner_Angle_Offset
    a = _bottom_x(Core_Bottom_Offset)
    b = Element_Diameter / 2 - Wall_Min_Thickness - Wall_Chamfer
    parts = []
    for n in range(Speed_Hole_Qty):
        outer_rods = [sp.translate(_resin_rod(_bottom_z(a + (b - a) * f)), [a + (b - a) * f, 0, 0])
                      for f in fractions]
        parts.append(sp.rotate_z(sp.union_all(outer_rods), (n + 0.5) * 360.0 / Speed_Hole_Qty))

        inner_x = Shaft_Diameter / 2 + Core_Chamfer + Resin_Tip_OD / 2
        inner_rod = sp.translate(_resin_rod(Core_Bottom_Offset), [inner_x, 0, 0])
        parts.append(sp.rotate_z(inner_rod, (n + inner_angle_offset) * 360.0 / Speed_Hole_Qty))
    return sp.union_all(parts)


def ResinSupport():
    _require_configured()
    countersink_id = Drive_Pin_Countersink_ID
    radius = Drive_Pin_Radial
    parts = [
        CutGroove(),
        SpeedHoleSupports(),
        DrivePinSupport(radius, countersink_id / 2, countersink_id / 2),
        BottomSupports(),
    ]
    return sp.union_all(parts)


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None):
    full, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                    cone_segments=cone_segments,
                                    simplify_tolerance_mm=simplify_tolerance_mm,
                                    platen_fn=platen_fn, minkowski_enabled=minkowski_enabled)
    support = ResinSupport()
    print(f"ResinSupport: verts={len(support.vertices)} faces={len(support.faces)} "
          f"watertight={support.is_watertight}", flush=True)
    combined = sp.union_all([full, support])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts


# ------------------------------------------------------------ Shaft Gauge
# Ported from v2/blickensderfer.scad's [Shaft Gauge Test] section
# (Render_Mode==2 -> GaugeTestSet(), lines 265-267/517-589). A 6-pocket
# "revolver" test print: each pocket bores the real shaft passage
# (Core/CoreChamfer/SecondaryCore/CoreGrooves, all Offset-parameterized,
# already ported above and reused verbatim here) at
# Gauge_Offset_Start + n*Gauge_Offset_Int for n=0..5, engraved with its
# own offset value so you can tell pockets apart after printing. Workflow:
# print it, test-fit each numbered pocket on the real machine's shaft, and
# set element.core_id_offset (config) to whichever number fits. Blickensderfer/
# Postal-only in v2 (the other machine families explicitly omit it) -
# v4 currently only has Blickensderfer, so no gating needed here.

def CylinderGauge(offset):
    h = Element_Height + Clip_Height - Core_Bottom_Offset
    c = sp.cylinder_z(Shaft_Diameter + 2 * Wall_Min_Thickness + offset, h, sections=Surface_Fn)
    return sp.translate(c, [0, 0, Core_Bottom_Offset])


def GaugeResinSupport(offset):
    parts = []
    for n in range(8):
        rod = sp.translate(_resin_rod(Core_Bottom_Offset),
                            [Shaft_Diameter / 2 + offset / 2 + Wall_Min_Thickness / 2, 0, 0])
        parts.append(sp.rotate_z(rod, n * 360.0 / 8))
    return sp.union_all(parts)


def GaugeResinSupportsRaft():
    d = 3 * (Shaft_Diameter + 2 * Wall_Min_Thickness)
    return sp.frustum_z(d, d + 2 * Resin_Raft_Thickness, Resin_Raft_Thickness, sections=Resin_Fn,
                         base_z=-Resin_Min_Rod_Height - Resin_Raft_Thickness)


def RevolverSolid():
    """hull() of 6 CylinderGauge(0) posts on a hexagonal ring - trimesh has
    no hull-of-solids primitive, so (as with CoreEllipses() above)
    concatenate their vertices and take .convex_hull; valid here because
    every input is itself convex, matching hull(union(convex_i)) ==
    convex_hull(union(vertices_i))."""
    radius = Shaft_Diameter + Wall_Min_Thickness * 2 - Wall_Min_Thickness / 2
    posts = []
    for n in range(6):
        c = sp.translate(CylinderGauge(0), [radius, 0, 0])
        posts.append(sp.rotate_z(c, n * 360.0 / 6))
    return trimesh.util.concatenate(posts).convex_hull


def GaugeText(offset):
    """GaugeText(Offset) - blickensderfer.scad:558-564. Engraves the
    pocket's calibration offset (e.g. "0.025") on its outer wall, using
    natural (advance-based) character spacing, not the fixed-pitch CPI
    convention type_test.py uses - this is a plain label, not simulating
    struck type. Reuses the logo's engraved font (v2 uses "Consolas"
    specifically for this, which isn't a font v4 has a config slot for -
    the logo font serves the same "small engraved label" role). Skipped
    entirely for Offset==0, matching v2's `if (Offset!=0)`."""
    if offset == 0:
        return None
    label = f"{round(offset, 4):g}"
    size_mm = 3.0
    depth = 4.0
    face = freetype.Face(LOGO_FONT_PATH)
    scale = size_mm / face.units_per_EM

    parts = []
    advances = []
    cursor = 0.0
    for ch in label:
        _, advance_mm = get_glyph_contours_and_advance(ch, 8.0, scale, font_path=LOGO_FONT_PATH)
        mesh = build_flat_text(ch, 8.0, depth, font_size_mm=size_mm, font_path=LOGO_FONT_PATH)
        mesh.apply_translation([cursor, 0, 0])
        parts.append(mesh)
        advances.append(advance_mm)
        cursor += advance_mm
    total_width = cursor
    text_mesh = sp.union_all(parts)
    text_mesh.apply_translation([-total_width / 2.0, 0, 0])

    # v2 source order is translate() THEN rotate([0,90,0]) (translate
    # outermost) - scad_transform's ops list must match that top-to-bottom
    # source order, not the reverse
    return sp.scad_transform(
        text_mesh,
        ("translate", [Shaft_Diameter / 2 + Wall_Min_Thickness - Wall_Min_Thickness / 2
                        + Core_Secondary_ID_Offset / 2,
                        0, Core_Bottom_Offset + (Element_Height + Clip_Height - Core_Bottom_Offset) / 2]),
        ("rotate", [0, 90, 0]),
    )


def GaugeTestSubtractive(offset, render_core_groove=None):
    render_core_groove = DEFAULT_RENDER_CORE_GROOVE if render_core_groove is None else render_core_groove
    parts = [Core(offset), CoreChamfer(offset), SecondaryCore(offset), sp.rotate_z(CoreEllipses(), 180)]
    if render_core_groove:
        parts.append(CoreGrooves(offset))
    text = GaugeText(offset)
    if text is not None:
        parts.append(text)
    return sp.union_all(parts)


def GaugeTestSet(render_core_groove=None, gauge_offset_start=None, gauge_offset_int=None):
    _require_configured()
    gauge_offset_start = Gauge_Offset_Start if gauge_offset_start is None else gauge_offset_start
    gauge_offset_int = Gauge_Offset_Int if gauge_offset_int is None else gauge_offset_int
    radius = Shaft_Diameter + Wall_Min_Thickness * 2 - Wall_Min_Thickness / 2

    subtractive_parts = [GaugeTestSubtractive(0, render_core_groove)]
    for n in range(6):
        offset = gauge_offset_start + n * gauge_offset_int
        pocket = sp.translate(GaugeTestSubtractive(offset, render_core_groove), [radius, 0, 0])
        subtractive_parts.append(sp.rotate_z(pocket, n * 360.0 / 6))
    subtractive = sp.union_all(subtractive_parts)
    print(f"GaugeTestSet: subtractive unioned, {len(subtractive_parts)} parts", flush=True)

    body = RevolverSolid().difference(subtractive, engine="manifold")

    support_parts = []
    for n in range(6):
        offset = gauge_offset_start + (n + 1) * gauge_offset_int
        support = sp.translate(GaugeResinSupport(offset), [radius, 0, 0])
        support_parts.append(sp.rotate_z(support, n * 360.0 / 6))
    support_parts.append(GaugeResinSupportsRaft())
    supports = sp.union_all(support_parts)

    combined = sp.union_all([body, supports])
    combined, _, _, _ = sp.check_and_repair(combined, label="GaugeTestSet")
    return combined
