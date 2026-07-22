"""
v4 port of v2/hammond_split.scad ("Split Hammond 1 Shuttle") - a SEPARATE
machine from Hammond (config/hammond.yaml/lib/hammond.py) in everything but
name, per SESSION_LOG.md's Hammond audit chapter (part 29) and this file's
own v2 header comment. hammond_split.scad has ZERO include statements (fully
self-contained - not wired to v2/lib/glyph_pipeline.scad at all) and its own
header calls it "closer to IBM's spherical geometry" than the cylinder
family. Nothing here reuses cylinder_machine.py's placement layer - not even
the "fake cylinder" trick lib/hammond.py's own TextRing() uses - because this
machine's real v2 text pipeline is structurally different (see "Glyph
pipeline" below).

Two-piece assembly: Left (side=0) and Right (side=1) are mirror images of
each other about the Y=0 plane (v2's Mirror(side) - scad_primitives.mirror())
for every BODY feature (Rib/Center/Spoke/Tube/FolderClearance/etc.), but the
struck TEXT is independently placed per side (TextAssemble(side)'s own
per-side angle-sign/character-index formula, not a mirror of the same
glyphs - each side carries different characters). Both halves ship in ONE
STL as physically separate, non-overlapping, print-oriented solids (see
ResinPrint()/FullElement()) - matching v2's real AssembleResin() layout, not
v2's Assemble()/Render_Mode==0 preview (which nests both halves in the same
frame, useful for visualizing the folded-together assembly but not itself
printable).

Glyph pipeline (v2:337-391): builds a flat, un-curved extrusion of each
character (linear_extrude, no per-glyph curved-surface mapping the way
build_glyph()/place_on_cylinder do for the cylinder family and for Hammond's
own non-split TextRing()), places it via a rotate+translate+rotate transform
identical in spirit to TextPlacement(), then trims the result to the Arc's
real thickness band via a real boolean intersection() rather than build_
glyph()'s platen-cylinder subtraction - the curvature the character needs to
follow comes entirely from the Arc's own swept surface, not from deforming
the glyph mesh. Mink_On=false (v2's real default - the only variant that
actually gets tested/printed) reduces LetterText() to a plain flat mirrored/
centered/baseline extrusion, which IS exactly glyph_poc.build_glyph() with
platen_radius_mm=0 (no curved platen - same "Skip_Platen_Cutout" trick
lib/hammond.py's own configure() already established) and minkowski_
enabled=False - reused directly (see LetterText()). Mink_On=true needs its
own bespoke helper (_letter_text_drafted()) instead: v2's real minkowski
cone has an INDEPENDENT fixed height (Mink_Height=2mm) decoupled from the
extrusion depth (Glyph_Height=0.8mm) - neither build_glyph() nor build_
flat_text_drafted() support that (both tie the cone's height to the
extrusion depth itself), so this machine gets its own small Minkowski
helper built from scad_primitives.to_manifold/from_manifold directly,
faithfully reproducing v2's real translate/rotate/trim sequence (see that
function's docstring for the derivation, including why the realized taper
ends up much subtler than a normal "wide root, narrow tip" draft once
Glyph_Height+1 < Mink_Height with the real default numbers).

Resin support (v2:202-265, 551-745) is a THIRD independent resin-support
scheme (neither cylinder_machine's placement layer, nor Hammond's own
VertResinSupport2) - a tiered grid (Arc/Folder/Ring, each its own fixed
Res_*_Div point grid, faithfully ported as real numpy-derived point arrays
in configure(), matching v2's own range-comprehension arithmetic exactly,
including one real quirk: Res_Folder_X_Pts's range step uses len(Res_Folder_
Div)==2 - the ARRAY's length, not an index into it - always giving exactly
3 points regardless of the div config values, ported literally not "fixed")
plus a diagonal cross-bracing "fence" lattice (ResinFence() et al.) built
from resin_support.connecting_rod() - the same hull-of-two-spheres capsule
primitive Hammond's own ConnectingRod gusset reuses, but used here in a full
lattice rather than a single-purpose brace. Individual rod/tip shape
(ResinRod/ResinTip/ResinRodClean) is its own faithful port, NOT resin_
support.resin_rod()/rod_tip() - those were specifically derived for
Hammond's own (hammond.scad) coordinate/shift convention (see resin_
support.rod_tip()'s own docstring, which cites v2/hammond.scad line numbers
directly) and don't match this file's real transform order.

Debug limitation: generate.py's --cut-bodies flag calls bd.Subtractive(x)
with a single positional arg meant as render_core_groove (a bool/None) for
every other machine - this machine's Subtractive(side) needs a real 0/1
side index instead, so --cut-bodies is not meaningful here (same category
as Helios having no resin support at all - not every debug flag needs to
work identically on every machine).
"""

import time

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon as ShapelyPolygon
from shapely.affinity import scale as shapely_scale

import scad_primitives as sp
import resin_support
import cylinder_machine
import glyph_poc
import build_log

_configured = False


def _require_configured():
    if not _configured:
        raise RuntimeError("call hammond_split.configure(config_path) before using this module")


def _circ_res(fn):
    """Shapely's Point.buffer(resolution=) is points-per-quarter-circle;
    OpenSCAD's $fn is total segments for a full circle - same helper as
    lib/hammond.py's."""
    return max(1, round(fn / 4.0))


def _mirror_side(mesh, side):
    """Mirror(side) (v2:489-495) - mirror([0,1,0]) for side==1, identity
    for side==0."""
    return mesh if side == 0 else sp.mirror(mesh, [0, 1, 0])


def _transform_point(point, *ops):
    """Applies the same ('rotate',[a,b,c])/('translate',[x,y,z]) op
    sequence as sp.scad_transform(), but to a single 3D point instead of a
    whole mesh - used by the resin-support fence lattice, which only needs
    the transformed CENTER of a sphere (not a full mesh) to feed
    resin_support.connecting_rod()."""
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
    p = np.array([point[0], point[1], point[2], 1.0])
    return (combined @ p)[:3]


def _sphere(d, center):
    s = trimesh.creation.icosphere(subdivisions=2, radius=d / 2.0)
    s.apply_translation(center)
    return s


def _torus_partial(r_center, z_center, tube_r, start_deg, end_deg, sections):
    """rotate_extrude(angle=) of a small circle at (r_center,z_center) in
    the meridian plane - a full or partial torus segment, used for Rib()'s
    two rounded ridges and GlueGroove()'s full ring."""
    n = max(8, sections // 4)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    profile = [(r_center + tube_r * np.cos(ti), z_center + tube_r * np.sin(ti)) for ti in t]
    if end_deg - start_deg >= 360.0:
        return sp.revolve_polygon(profile, sections=sections)
    return sp.revolve_polygon_partial(profile, start_deg, end_deg, sections=sections)


def _ellipse_poly(x_scale, y_scale, res):
    """scale([x_scale,y_scale]) circle(d=1) (Spoke2D(), v2:277-280) - an
    ellipse with semi-axes x_scale/2, y_scale/2."""
    circle = Point(0, 0).buffer(0.5, resolution=res)
    return shapely_scale(circle, x_scale, y_scale, origin=(0, 0))


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - see
    lib/blickensderfer.configure()'s docstring for the general scheme."""
    global _configured
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg
    # v2's real value is .01 (v2/hammond_split.scad:46) - matching the more
    # recent Mignon/Bennett/Helios/Hammond 0.001 convention instead, per
    # this repo's "pick one convention" rule (no reason for this machine to
    # be the one holdout).
    g["z"] = 0.001

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["Type_Size"] = font["size_mm"]
    g["FONT_SIZE_MM"] = font["size_mm"]  # for type_test.py/tune.py parity with every other machine

    cm = cfg["char_mod"]
    g["Char_Mod"] = cm["char"]
    g["CHAR_MOD_FONT_PATH"] = cm["char_mod_font_path"]
    g["Char_Mod_Size"] = cm["char_mod_size_mm"]

    label = cfg["label"]
    g["LOGO_FONT_PATH"] = label["font_path"]
    g["Logo_Text_1"] = label["label1"]
    g["Logo_Text_2"] = label["label2"]
    g["Logo_Size"] = label["label_size_mm"]
    g["Logo_Depth"] = label["depth_mm"]

    g["Layout"] = cfg["layout"]["rows"]
    # Baselines[row] (v2:103-107, Baseline_Gaps[row]+Baseline_Offset) -
    # stored as the final absolute per-row value directly in layout.
    # baseline_row, matching every other machine's convention (see
    # config/hammond_split.yaml's matching comment) rather than as
    # separate live gaps/offset keys.
    g["Baselines"] = np.array(cfg["layout"]["baseline_row"], dtype=float)

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

    e = cfg["element"]
    g["Pin_ID_Mm"] = e["pin_id_mm"]
    g["Pin_Radial"] = e["pin_radial"]
    g["Pin_Theta"] = e["pin_theta"]
    g["Pin_ID_Chamfer"] = e["pin_id_chamfer"]
    g["Tube_OD_Mm"] = e["tube_od_mm"]
    g["Tube_Chamfer"] = e["tube_chamfer"]
    g["Arc_OD"] = e["arc_od"]
    g["Arc_Thickness"] = e["arc_thickness"]
    g["Arc_Height"] = e["arc_height"]
    g["Arc_Height_Offset"] = e["arc_height_offset"]
    g["Folder_Degree_Offset"] = e["folder_degree_offset"]
    g["Folder_Degrees"] = e["folder_degrees"]
    g["Folder_ID_Mm"] = e["folder_id_mm"]
    g["Folder_OD"] = e["folder_od"]
    g["Folder_Thickness"] = e["folder_thickness"]
    g["Folder_Close_Gap"] = e["folder_close_gap"]
    g["Folder_Arc_Start"] = g["Folder_Close_Gap"] / 2.0
    g["Folder_Glue_Hole_ID_Mm"] = e["folder_glue_hole_id_mm"]
    g["Folder_Glue_Groove_R"] = e["folder_glue_groove_r"]
    g["Folder_Glue_Groove_Depth"] = e["folder_glue_groove_depth"]
    g["Glyph_Height"] = e["glyph_height"]
    g["Finger_Thickness"] = e["finger_thickness"]
    g["Spoke_Thickness"] = e["spoke_thickness"]
    g["Spoke_Height"] = e["spoke_height"]
    g["Spoke_Count"] = e["spoke_count"]
    g["Spoke_Extent"] = e["spoke_extent"]
    g["Spoke_Spacing"] = g["Spoke_Extent"] / (g["Spoke_Count"] - 1)
    g["Spoke_Chamfer"] = e["spoke_chamfer"]
    g["Rib_OD"] = e["rib_od"]
    g["Rib_Thickness"] = e["rib_thickness"]
    g["Rib_Radius"] = e["rib_radius"]
    # Char_Theta = 360/angular_divisions (v2:167's literal 360/96) - the
    # full-circle character-slot pitch, NOT a partial-arc concept (unlike
    # hammond.yaml's angular_span_deg/angular_divisions).
    g["Char_Theta"] = 360.0 / e["angular_divisions"]

    id_offset = e["id_offset"]
    g["ID_Offset"] = id_offset
    g["Folder_Radial_Gap"] = e["folder_radial_gap"]
    g["Folder_Squash_Clearance"] = e["folder_squash_clearance"]
    g["Tube_OD"] = [t + id_offset for t in g["Tube_OD_Mm"]]
    g["Pin_ID"] = g["Pin_ID_Mm"] + id_offset
    g["Folder_ID"] = [g["Folder_ID_Mm"] + g["Folder_Radial_Gap"], g["Folder_ID_Mm"] - g["Folder_Radial_Gap"]]
    g["Folder_Glue_Hole_ID"] = g["Folder_Glue_Hole_ID_Mm"] + id_offset

    # Handy Variables (v2:218-224)
    g["Folder_Half_Thickness"] = (g["Folder_Thickness"] - g["Folder_Squash_Clearance"]) / 2.0
    g["Arc_Start"] = np.degrees(np.arcsin(g["Finger_Thickness"] / g["Arc_OD"]))
    g["Arc_End"] = 15 * g["Char_Theta"] + g["Char_Theta"] / 2.0
    g["Arc_Extent"] = g["Arc_End"] - g["Arc_Start"]
    g["Folder_Arc_End"] = g["Folder_Degrees"] + g["Folder_Degree_Offset"]
    g["Folder_Arc"] = g["Folder_Arc_End"] - g["Folder_Arc_Start"]

    q = cfg["quality"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Text_Fn"] = q["text_fn"]  # not consumed directly - v4's freetype pipeline uses points_per_mm instead
    g["DEFAULT_MINK_FN"] = q["mink_fn"]
    g["Mink_Fn"] = g["DEFAULT_MINK_FN"]

    b = cfg["build"]
    g["DEFAULT_POINTS_PER_MM"] = b["points_per_mm"]
    g["POINTS_PER_MM"] = g["DEFAULT_POINTS_PER_MM"]
    g["Render_Left"] = bool(b["render_left"])
    g["Render_Right"] = bool(b["render_right"])
    g["DEFAULT_RESIN_SUPPORT"] = bool(b["resin_support"])
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", 0.005)
    g["SIMPLIFY_TOLERANCE_MM"] = g["DEFAULT_SIMPLIFY_TOLERANCE_MM"]
    g["DEFAULT_MINKOWSKI_ENABLED"] = bool(b.get("minkowski_enabled", False))
    g["Mink_On"] = g["DEFAULT_MINKOWSKI_ENABLED"]
    g["DEFAULT_MINK_DRAFT_ANGLE"] = b.get("mink_draft_angle_deg", 60.0)
    g["Mink_Draft_Angle"] = g["DEFAULT_MINK_DRAFT_ANGLE"]
    g["Mink_Height"] = b.get("mink_height", 2.0)
    g["Mink_Radius"] = np.tan(np.radians(g["Mink_Draft_Angle"] / 2.0)) * g["Mink_Height"]

    tt = cfg.get("type_test", {})
    g["Test_CPI"] = tt.get("cpi", 10.0)

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Min_Rod_Height"] = r["min_rod_height"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Raft_Thickness"] = r["raft_thickness"]
    g["Res_Spacing"] = r["fence_spacing"]
    g["Res_Angle"] = r["fence_angle_deg"]

    arc_div = r["arc_div"]
    folder_div = r["folder_div"]
    folder_face_div = r["folder_face_div"]
    ring_div = r["ring_div"]
    ring_start_end = r["ring_start_end_deg"]

    # Resin Support Variables (v2:226-265) - real v2 formulas, faithfully
    # reproduced with numpy in place of OpenSCAD range comprehensions
    # ([start:step:end], always N evenly-spaced points inclusive of both
    # ends == np.linspace(start,end,N)).
    g["Res_Z_Raise"] = g["Folder_ID"][1] / 2.0
    g["Res_X_Rot"] = g["Arc_Start"] + g["Arc_Extent"] / 2.0

    g["Res_Arc_Theta_Pts"] = np.linspace(-g["Arc_Extent"] / 2.0, g["Arc_Extent"] / 2.0, arc_div[0])
    _arc_r = g["Arc_OD"] / 2.0 - g["Arc_Thickness"]
    g["Res_Arc_Y_Pts"] = np.sin(np.radians(g["Res_Arc_Theta_Pts"])) * _arc_r
    g["Res_Arc_Z_Pts"] = np.cos(np.radians(g["Res_Arc_Theta_Pts"])) * _arc_r
    g["Res_Arc_X_Pts"] = np.linspace(g["Arc_Height_Offset"], g["Arc_Height_Offset"] + g["Arc_Height"], arc_div[1])

    g["Res_Folder_Face_X_Pts"] = np.linspace(0.0, g["Folder_Thickness"], folder_face_div[1])
    g["Res_Folder_Face_R_Pts"] = np.linspace(g["Folder_ID"][0] / 2.0, g["Folder_OD"] / 2.0, folder_face_div[0])
    _face_angle = g["Folder_Arc_End"] - g["Res_X_Rot"]
    g["Res_Folder_Face_Y_Pts"] = np.sin(np.radians(_face_angle)) * g["Res_Folder_Face_R_Pts"]
    g["Res_Folder_Face_Z_Pts"] = np.cos(np.radians(_face_angle)) * g["Res_Folder_Face_R_Pts"]

    # Res_Folder_X_Pts (v2:257) - the range step is (FHT+FSC)/len(Res_
    # Folder_Div), i.e. divided by the DIV ARRAY's length (2), not
    # Res_Folder_Div[1]-1 - always exactly 3 points from 0 to Folder_Half_
    # Thickness+Folder_Squash_Clearance regardless of folder_div's actual
    # values. A real v2 quirk, ported literally, not "fixed".
    g["Res_Folder_X_Pts"] = np.linspace(0.0, g["Folder_Half_Thickness"] + g["Folder_Squash_Clearance"], 3)
    g["Res_Folder_Theta_Pts"] = np.linspace(g["Folder_Arc_Start"] - g["Res_X_Rot"],
                                             g["Folder_Arc_End"] - g["Res_X_Rot"], folder_div[0])
    g["Res_Folder_Y_Pts"] = np.sin(np.radians(g["Res_Folder_Theta_Pts"])) * g["Folder_ID"][0] / 2.0
    g["Res_Folder_Z_Pts"] = np.cos(np.radians(g["Res_Folder_Theta_Pts"])) * g["Folder_ID"][0] / 2.0

    g["Res_Ring_X_Pts"] = np.linspace(0.0, g["Folder_Half_Thickness"], ring_div[1])
    g["Res_Ring_Theta_Pts"] = np.linspace(ring_start_end[0], ring_start_end[1], ring_div[0])
    g["Res_Ring_Y_Pts"] = np.sin(np.radians(g["Res_Ring_Theta_Pts"])) * g["Folder_ID"][1] / 2.0
    g["Res_Ring_Z_Pts"] = -np.cos(np.radians(g["Res_Ring_Theta_Pts"])) * g["Folder_ID"][1] / 2.0

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    calibration = cfg.get("calibration", {})
    g["Calibration_Test_Char"] = calibration.get("test_char", "H")
    g["Calibration_Vary_Baseline"] = calibration.get("vary_baseline", False)
    g["Calibration_Vary_Cutout"] = calibration.get("vary_cutout", False)
    g["Calibration_Start"] = calibration.get("start", -0.7)
    g["Calibration_Interval"] = calibration.get("interval", 0.05)

    _configured = True


# ------------------------------------------------------------------- Body

def Arc(extra):
    """v2:267-271 - rotate_extrude(0..Arc_End) of a rectangle spanning
    radius [Arc_OD/2-Arc_Thickness, Arc_OD/2-Arc_Thickness+Arc_Thickness+
    extra], z [Arc_Height_Offset, Arc_Height_Offset+Arc_Height]."""
    r0 = Arc_OD / 2.0 - Arc_Thickness
    w = Arc_Thickness + extra
    z0 = Arc_Height_Offset
    h = Arc_Height
    profile = [(r0, z0), (r0 + w, z0), (r0 + w, z0 + h), (r0, z0 + h)]
    return sp.revolve_polygon_partial(profile, 0.0, Arc_End, sections=Cyl_Fn)


def Center():
    return sp.cylinder_z(Folder_OD, Folder_Thickness, sections=Cyl_Fn)


def Spoke2D():
    return _ellipse_poly(Spoke_Thickness, Spoke_Height, _circ_res(Cyl_Fn))


def SpokeChamfer():
    res = _circ_res(Cyl_Fn)
    base = _ellipse_poly(Spoke_Thickness, Spoke_Height, res)
    wide = _ellipse_poly(Spoke_Thickness + 2 * Spoke_Chamfer, Spoke_Height + 2 * Spoke_Chamfer, res)
    base3d = trimesh.creation.extrude_polygon(base, z)
    wide3d = trimesh.creation.extrude_polygon(wide, z)
    wide3d = sp.translate(wide3d, [0, 0, Spoke_Chamfer])
    return trimesh.util.concatenate([base3d, wide3d]).convex_hull


def Spoke():
    poly = Spoke2D()
    length = Arc_OD / 2.0 - Arc_Thickness + z
    rod = trimesh.creation.extrude_polygon(poly, length)
    chamfer = sp.translate(SpokeChamfer(), [0, 0, Arc_OD / 2.0 - Arc_Thickness - Spoke_Chamfer])
    combined = sp.union_all([rod, chamfer])
    return sp.scad_transform(combined, ("translate", [0, 0, Folder_Thickness / 2.0]), ("rotate", [90, 0, 90]))


def SpokeArranged():
    spoke = Spoke()
    spokes = [sp.rotate_z(spoke, i * Spoke_Spacing) for i in range(Spoke_Count)]
    return sp.rotate_z(sp.union_all(spokes), Folder_Degree_Offset)


def Rib():
    """v2:310-335 - union of two independent hull() groups."""
    a = 5.0
    b = 4.0

    shape_a = _torus_partial(Rib_OD / 2.0 - Rib_Radius, Folder_Thickness / 2.0, Rib_Radius,
                              0.0, Spoke_Extent + a, sections=Cyl_Fn)
    shape_a = sp.rotate_z(shape_a, Folder_Degree_Offset - a / 2.0)
    shape_b = _torus_partial(Folder_OD / 2.0 - b / 2.0 - z, Folder_Thickness / 2.0, b / 2.0,
                              0.0, 120.0, sections=Cyl_Fn)
    shape_b = sp.rotate_z(shape_b, Folder_Degree_Offset)
    hull1 = trimesh.util.concatenate([shape_a, shape_b]).convex_hull

    tri = ShapelyPolygon([
        (Folder_OD / 2.0 - z, Folder_Thickness / 2.0 - Spoke_Height / 2.0),
        (Folder_OD / 2.0 - z, Folder_Thickness / 2.0 + Spoke_Height / 2.0),
        (Folder_OD / 2.0 - z + Folder_Thickness / 2.0, Folder_Thickness / 2.0),
    ])
    shape_c = sp.revolve_polygon_partial(list(tri.exterior.coords)[:-1], 0.0, Spoke_Extent, sections=Cyl_Fn)
    shape_c = sp.rotate_z(shape_c, Folder_Degree_Offset)
    shape_d = sp.cylinder_z(3.0, 10.5, sections=Cyl_Fn)
    shape_d = sp.scad_transform(shape_d, ("translate", [0, 0, Folder_Thickness / 2.0]), ("rotate", [-90, 0, 0]))
    hull2 = trimesh.util.concatenate([shape_c, shape_d]).convex_hull

    return sp.union_all([hull1, hull2])


def LeftAdditive():
    return sp.union_all([Arc(0.0), Center(), SpokeArranged(), Rib()])


# --------------------------------------------------------------- Glyph pipeline

def _text_placement_ops(angle, height):
    """TextPlacement(angle,height) (v2:342-347)."""
    return [("rotate", [0, 0, angle]), ("translate", [Arc_OD / 2.0 - 1.0, 0, height]), ("rotate", [90, 0, 90])]


def _letter_text_drafted(char, font_path, font_size_mm, depth):
    """LetterText() (v2:349-364) for Mink_On==true - see this module's
    docstring for why this can't reuse build_glyph()/build_flat_text_
    drafted() (both tie the draft cone's height to the extrusion depth;
    this machine's real cone height (Mink_Height) is independent of it).

    Builds the same flat (mirrored/centered/baseline) block LetterText()
    uses for Mink_On==false (via build_glyph(minkowski_enabled=False)),
    then reproduces v2's real minkowski()+difference(cube) sequence
    directly: minkowski-sum with a cone spanning z=[-Mink_Height,0] (wide
    at the bottom, apex at 0), then subtract everything below z=0. Net
    effect on the real default numbers (Glyph_Height+1=1.8 < Mink_Height=2):
    since the cone's height is independent of the block's own depth, the
    growth visible within the kept [0,depth] range is bounded by how much
    of the cone's radius profile can still reach that range - here that
    caps out well short of the cone's own full Mink_Radius, so the
    resulting taper is a mild, monotonically-shrinking-to-zero flare
    (maximal at z=0, zero at z=depth), not a normal "wide root" draft.
    This is what the real v2 numbers actually produce, not an approximation
    of some intended fuller taper."""
    flat = glyph_poc.build_glyph(char, POINTS_PER_MM, align_kwargs=ALIGN_KWARGS,
                                  font_path=font_path, font_size_mm=font_size_mm,
                                  separation_mm=depth, platen_radius_mm=0.0, radius_y_offset_mm=0.0,
                                  minkowski_enabled=False, simplify_tolerance_mm=0.0)
    cone = sp.frustum_z(2 * Mink_Radius, 0.0, Mink_Height, sections=Mink_Fn, base_z=-Mink_Height)
    summed = sp.to_manifold(flat).minkowski_sum(sp.to_manifold(cone))
    summed = sp.from_manifold(summed)
    # difference(translate([0,0,-10]) cube(20,center=true)) - removes z in
    # [-20,0]. XY extent widened to 200 (well past Arc_OD~75) since the
    # real 20mm v2 sentinel is sized for v2's own coordinate scale near the
    # origin - harmless to over-size, same convention as _wedge_complement_
    # poly's far=100/GrooveShape's tab_length=50 sentinels elsewhere.
    trimmer = sp.box_centered([200.0, 200.0, 20.0], [0, 0, -10.0])
    trimmed = summed.difference(trimmer, engine="manifold")
    if SIMPLIFY_TOLERANCE_MM > 0:
        trimmed = sp.from_manifold(sp.to_manifold(trimmed).simplify(SIMPLIFY_TOLERANCE_MM))
    return trimmed


def LetterText(char, font_path, font_size_mm):
    """v2:349-364. Mink_On==false (the real default - see module docstring)
    reuses build_glyph() directly: platen_radius_mm=0 (no curved platen,
    same trick lib/hammond.py's configure() established) + minkowski_
    enabled=False + align_kwargs mode=center reproduces LetterText()'s
    plain `linear_extrude(Glyph_Height+1) Text(...)` exactly (mirror +
    halign=center + valign=baseline, build_glyph()'s own struck-character
    convention)."""
    depth = Glyph_Height + 1.0
    if not Mink_On:
        return glyph_poc.build_glyph(char, POINTS_PER_MM, align_kwargs=ALIGN_KWARGS,
                                      font_path=font_path, font_size_mm=font_size_mm,
                                      separation_mm=depth, platen_radius_mm=0.0, radius_y_offset_mm=0.0,
                                      minkowski_enabled=False, simplify_tolerance_mm=SIMPLIFY_TOLERANCE_MM)
    return _letter_text_drafted(char, font_path, font_size_mm, depth)


def TextAssemble(side):
    """v2:366-383. Prints "[n/total] building ..." progress lines matching
    cylinder_machine.TextRing's own convention (tune.py's progress bar
    parses this exact shape via its _PROGRESS_RE - see _update_progress's
    docstring) - this machine builds its own from-scratch character loop
    instead of reusing TextRing, so it doesn't get that instrumentation
    for free the way Mignon/Bennett/Helios/Hammond do; without a matching
    print here the Build tab's progress bar just sits at 0% for the whole
    build. Also matches TextRing's per-character skip-on-exception
    behavior (one bad glyph doesn't abort the whole build)."""
    parts = []
    skipped = []
    total = 3 * 15
    n = 0
    t_start = time.perf_counter()
    for baseline in range(3):
        height = Baselines[baseline]
        for i in range(15):
            n += 1
            angle = (1 + i) * Char_Theta if side == 0 else (-1 - (14 - i)) * Char_Theta
            char = Layout[baseline][14 - i] if side == 0 else Layout[baseline][29 - i]
            prefix = f"TextAssemble side={side}"
            build_log.progress_start(prefix, n, total, f"building {char!r} (row {baseline})")
            t0 = time.perf_counter()
            try:
                is_mod = char in Char_Mod
                font_path = CHAR_MOD_FONT_PATH if is_mod else FONT_PATH
                size = Char_Mod_Size if is_mod else Type_Size
                letter = LetterText(char, font_path, size)
            except Exception as e:
                skipped.append((baseline, i, char, str(e)))
                build_log.progress_skipped(e)
                continue
            build_log.progress_done(time.perf_counter() - t0)
            letter = sp.scad_transform(letter, *_text_placement_ops(angle, height))
            parts.append(letter)
    build_log.progress_summary(f"TextAssemble side={side}", len(parts), skipped,
                                time.perf_counter() - t_start)
    return sp.union_all(parts)


def TextRing(side):
    """v2:385-391 - trims TextAssemble(side) to the Arc's real thickness
    band via a real boolean intersection (this machine's substitute for a
    curved-platen mapping - see module docstring)."""
    assembled = TextAssemble(side)
    arc = _mirror_side(Arc(Glyph_Height + 1.0), side)
    return assembled.intersection(arc, engine="manifold")


# ------------------------------------------------------------- Subtractive

def Tube(side):
    d = Tube_OD[side]
    main = sp.cylinder_z(d, 25.0, sections=Cyl_Fn, base_z=-z)
    chamferbump = -z if side == 0 else (Folder_Half_Thickness + Folder_Squash_Clearance)
    c1 = sp.frustum_z(d + 2 * Tube_Chamfer, d, Tube_Chamfer + z, sections=Cyl_Fn, base_z=-z)
    c1 = sp.translate(c1, [0, 0, chamferbump])
    c2 = sp.frustum_z(d, d + 2 * Tube_Chamfer, Tube_Chamfer + z, sections=Cyl_Fn,
                       base_z=Folder_Half_Thickness - Tube_Chamfer)
    c2 = sp.translate(c2, [0, 0, chamferbump])
    return sp.union_all([main, c1, c2])


def FolderClearance(side):
    hoffset = (Folder_Thickness / 2.0 - Folder_Squash_Clearance / 2.0) if side == 0 else -z
    hstart = hoffset if side == 0 else -z
    h = 15.0 if side == 0 else (z + Folder_Thickness / 2.0 + Folder_Squash_Clearance / 2.0)
    return sp.cylinder_z(Folder_ID[0], h, sections=Cyl_Fn, base_z=hstart)


def FolderCutaway(side):
    r = 30.0
    a0 = np.radians(Folder_Arc_Start)
    a1 = np.radians(Folder_Arc_End)
    xy0 = (r * np.cos(a0), r * np.sin(a0))
    xy1 = (r * np.cos(a1), r * np.sin(a1))
    poly = ShapelyPolygon([xy0, (0, 0), xy1, (-r, r), (-r, -r), (r, -r)])
    shape = trimesh.creation.extrude_polygon(poly, 25.0)
    shape = sp.translate(shape, [0, 0, -5.0])
    shape = _mirror_side(shape, side)
    cutter = sp.cylinder_z(Folder_ID[1], 40.0, sections=Cyl_Fn, base_z=-20.0)
    return shape.difference(cutter, engine="manifold")


def Finger():
    tx, ty, tz = Arc_OD / 2.0 - 5.0, -Finger_Thickness / 2.0, -10.0
    center = [tx + 5.0, ty + Finger_Thickness / 2.0, tz + 20.0]
    return sp.box_centered([10.0, Finger_Thickness, 40.0], center)


def PinHole():
    main = sp.cylinder_z(Pin_ID, 20.0, sections=Cyl_Fn, base_z=-z)
    bottom_chamfer = sp.frustum_z(Pin_ID + 2 * Pin_ID_Chamfer, Pin_ID, Pin_ID_Chamfer, sections=Cyl_Fn, base_z=-z)
    top_chamfer = sp.frustum_z(Pin_ID, Pin_ID + 2 * Pin_ID_Chamfer, Pin_ID_Chamfer + z, sections=Cyl_Fn,
                                base_z=Folder_Thickness - Pin_ID_Chamfer)
    return sp.union_all([main, bottom_chamfer, top_chamfer])


def PinHoles(side):
    hole = PinHole()
    parts = []
    for pin in (0, 1):
        h = sp.translate(hole, [Pin_Radial, 0, 0])
        h = sp.rotate_z(h, Pin_Theta[pin])
        parts.append(h)
    return _mirror_side(sp.union_all(parts), side)


def GlueHoles(side):
    # v2:456-457 locally shadows the module-global Folder_Glue_Hole_ID
    # (1.28mm) with a literal 0.8mm for this module only - a real v2
    # quirk, faithfully preserved rather than "fixed".
    hole_id = 0.8
    height = Folder_Half_Thickness / 2.0 if side == 0 else Folder_Thickness - Folder_Half_Thickness / 2.0
    parts = []
    for n in (0, 180):
        hole = sp.cylinder_z(hole_id, Folder_ID[1] / 2.0, sections=Cyl_Fn, base_z=0.0)
        chamfer = sp.frustum_z(hole_id, hole_id + 2 * Pin_ID_Chamfer, 1.0, sections=Cyl_Fn,
                                base_z=Folder_ID[1] / 2.0 - 1.0)
        piece = sp.union_all([hole, chamfer])
        piece = sp.scad_transform(piece, ("rotate", [0, 90, Folder_Arc_Start - (360 - Folder_Arc) / 2.0 + 90 + n]))
        parts.append(piece)
    combined = _mirror_side(sp.union_all(parts), side)
    return sp.translate(combined, [0, 0, height])


def GlueGroove(side):
    height = Folder_Half_Thickness / 2.0 if side == 0 else Folder_Thickness - Folder_Half_Thickness / 2.0
    r_center = Tube_OD[side] / 2.0 - Folder_Glue_Groove_R + Folder_Glue_Groove_Depth
    torus = _torus_partial(r_center, 0.0, Folder_Glue_Groove_R, 0.0, 360.0, sections=Cyl_Fn)
    return sp.translate(torus, [0, 0, height])


def Logo(side):
    """v2:476-487 - engraved surface label (two lines, read directly, never
    struck - halign=center/valign=center in v2). Reuses cylinder_machine.
    build_text_string(), which already stays at baseline (y=0) instead of
    attempting true valign=center - the same accepted simplification
    LogoText()/mignon.ElementLabel()/hammond.Label() already make for
    decorative text, per that function's own docstring."""
    depth = Logo_Depth * 2.0
    line1 = cylinder_machine.build_text_string(Logo_Text_1, Logo_Size, LOGO_FONT_PATH, depth)
    line2 = cylinder_machine.build_text_string(Logo_Text_2, Logo_Size, LOGO_FONT_PATH, depth)
    line2 = sp.translate(line2, [0, -2.0, 0])
    combined = sp.union_all([line1, line2])
    combined = sp.translate(combined, [0, 0, -depth / 2.0])  # linear_extrude(...,center=true)
    angle = Folder_Arc_Start if side == 0 else -Folder_Arc_Start
    z_rot2 = 0.0 if side == 0 else 180.0
    return sp.scad_transform(
        combined,
        ("rotate", [0, 0, angle]),
        ("translate", [16.0, 0, Folder_Thickness / 2.0]),
        ("rotate", [90, 0, z_rot2]),
    )


def Subtractive(side):
    return sp.union_all([Tube(side), FolderClearance(side), FolderCutaway(side), Finger(),
                          PinHoles(side), GlueHoles(side), GlueGroove(side), Logo(side)])


def Additive(side):
    body = _mirror_side(LeftAdditive(), side)
    return sp.union_all([body, TextRing(side)])


def AssembleSide(side):
    return Additive(side).difference(Subtractive(side), engine="manifold")


def Assemble(render_left=None, render_right=None):
    """v2:544-549 - v2's real "Normal" render target (Render_Mode==0, see
    v2:60's own customizer comment: `Render_Mode=1;//[0:Normal,
    1:ResinPrint, 2:Type Test]`). v1/Hammond/HammondSplitShuttle.scad:16's
    GenStyle customizer names this same target explicitly: `GenStyle =
    1; //[0:Normal, 1:ResinPrint, 2:ResinPrintL, 3:ResinPrintR, 4:NormalL,
    5:NormalR]` - GenStyle 0/4/5 (v1:720-733) are this function's three
    real combinations (both/left-only/right-only, i.e. exactly
    render_left/render_right). Neither v1's LeftShuttleAssembled/
    RightShuttleAssembled nor either version's Assemble() ever calls a
    resin-rod module - Normal is unconditionally resin-free in the real
    source, not a v4 simplification.

    Despite an earlier version of this docstring claiming otherwise, the
    two halves do NOT overlap: side==1's own Mirror() (_mirror_side, a
    pure Y-reflection with no translation) leaves both halves sharing the
    same X/Z frame with only a Y sign flip, so their bounding boxes
    overlap in Y but their actual solids are disjoint - confirmed
    empirically (Assemble(render_left=True, render_right=True)'s union
    volume equals AssembleSide(0)'s volume + AssembleSide(1)'s volume to
    float precision, and the result is watertight/is_volume=True). This
    IS a real, printable layout - see NormalElement() for the wired CLI/
    tune.py entry point. ResinPrint()/FullElement() are the OTHER real
    target (v2 Render_Mode==1/v1 GenStyle 1-3, vertical + resin
    supports), not a "more real" version of this one."""
    _require_configured()
    rl = Render_Left if render_left is None else render_left
    rr = Render_Right if render_right is None else render_right
    if not rl and not rr:
        raise ValueError("hammond_split: Render Left and Render Right are both off - "
                          "nothing to build. Turn at least one back on (Build tab).")
    parts = []
    if rl:
        parts.append(AssembleSide(0))
    if rr:
        parts.append(AssembleSide(1))
    return sp.union_all(parts)


# --------------------------------------------------------------- Resin support

def _res_y_offset(theta_deg):
    return -np.sin(np.radians(theta_deg)) * (Resin_Tip_L + Resin_Tip_OD / 2.0 - Resin_Inset)


def _res_z_offset(theta_deg):
    return -np.cos(np.radians(theta_deg)) * (Resin_Tip_L + Resin_Tip_OD / 2.0 - Resin_Inset)


def ResinTip(theta_deg):
    s1 = _sphere(Resin_Tip_OD, [0, 0, -Resin_Tip_OD / 2.0 + Resin_Inset])
    s2 = _sphere(Resin_Rod_OD, [0, 0, -Resin_Tip_OD / 2.0 + Resin_Inset - Resin_Tip_L])
    hull = trimesh.util.concatenate([s1, s2]).convex_hull
    return sp.scad_transform(hull, ("rotate", [-theta_deg, 0, 0]))


def ResinRodClean(h, theta_deg):
    z_off = _res_z_offset(theta_deg)
    center = [0, 0, -Resin_Tip_OD / 2.0 + Resin_Inset - Resin_Tip_L]
    lo = _sphere(Resin_Rod_OD, center)
    lo = sp.scad_transform(lo, ("translate", [0, 0, -Resin_Min_Rod_Height - z_off]), ("rotate", [-theta_deg, 0, 0]))
    hi = _sphere(Resin_Rod_OD, center)
    hi = sp.scad_transform(hi, ("translate", [0, 0, h]), ("rotate", [-theta_deg, 0, 0]))
    return trimesh.util.concatenate([lo, hi]).convex_hull


def ResinRod(h, theta_deg):
    tip = sp.translate(ResinTip(theta_deg), [0, 0, h])
    clean = ResinRodClean(h, theta_deg)
    raft = sp.frustum_z(Resin_Raft_OD, Resin_Raft_OD + 2 * Resin_Raft_Thickness, Resin_Raft_Thickness,
                         sections=Resin_Fn, base_z=0.0)
    raft = sp.translate(raft, [0, _res_y_offset(theta_deg), -Resin_Min_Rod_Height - Resin_Raft_Thickness])
    return sp.union_all([tip, clean, raft])


def _fence_center(h, theta_deg):
    """Center of ResinFenceTopSphere(h,theta) (v2:596-603) after its own
    translate/rotate/translate/translate chain - just the point, not a full
    mesh (fed to resin_support.connecting_rod() for the fence lattice's
    hull-of-two-spheres braces)."""
    local = [0.0, 0.0, -Resin_Tip_OD / 2.0 + Resin_Inset - Resin_Tip_L]
    return _transform_point(local, ("translate", [0, 0, h]), ("rotate", [-theta_deg, 0, 0]))


def ResinFenceArcTop():
    parts = []
    n = len(Res_Arc_Y_Pts)
    for yi in range(1, n):
        c1 = _fence_center(Res_Arc_Z_Pts[yi] + Res_Z_Raise, Res_Arc_Theta_Pts[yi]) + np.array([0, Res_Arc_Y_Pts[yi], 0])
        c0 = _fence_center(Res_Arc_Z_Pts[yi - 1] + Res_Z_Raise, Res_Arc_Theta_Pts[yi - 1]) \
            + np.array([0, Res_Arc_Y_Pts[yi - 1], 0])
        parts.append(resin_support.connecting_rod(c0, c1, Resin_Rod_OD))
    return sp.union_all(parts)


def ResinFenceArcSide(yint):
    base = _fence_center(Res_Arc_Z_Pts[0] + Res_Z_Raise, Res_Arc_Theta_Pts[yint])
    n = len(Res_Arc_X_Pts)
    c0 = base + np.array([-Res_Arc_X_Pts[0], 0, 0])
    c1 = base + np.array([-Res_Arc_X_Pts[n - 1], 0, 0])
    return resin_support.connecting_rod(c0, c1, Resin_Rod_OD)


def ResinArcSupports():
    parts = []
    nx, ny = len(Res_Arc_X_Pts), len(Res_Arc_Y_Pts)
    for xi in range(nx):
        for yi in range(ny):
            if xi == 0 or xi == nx - 1 or yi == 0 or yi == ny - 1:
                rod = ResinRod(Res_Arc_Z_Pts[yi] + Res_Z_Raise, Res_Arc_Theta_Pts[yi])
                rod = sp.translate(rod, [-Res_Arc_X_Pts[xi], Res_Arc_Y_Pts[yi], 0])
                parts.append(rod)
    return sp.union_all(parts)


def ResinKeepY():
    parts = []
    for yi in range(len(Res_Arc_Y_Pts)):
        rc = ResinRodClean(Res_Arc_Z_Pts[yi] + Res_Z_Raise, Res_Arc_Theta_Pts[yi])
        rc = sp.translate(rc, [0, Res_Arc_Y_Pts[yi], 0])
        parts.append(rc)
    return trimesh.util.concatenate(parts).convex_hull


def ResinKeepX(yint):
    parts = []
    n = len(Res_Arc_X_Pts)
    for xi in (0, n - 1):
        rc = ResinRodClean(Res_Arc_Z_Pts[0] + Res_Z_Raise, Res_Arc_Theta_Pts[yint])
        rc = sp.translate(rc, [-Res_Arc_X_Pts[xi], 0, 0])
        parts.append(rc)
    return trimesh.util.concatenate(parts).convex_hull


def ResinParallelBars():
    bars = []
    for n in range(-20, 21):
        c = sp.cylinder_z(Resin_Rod_OD, 100.0, sections=Resin_Fn, base_z=0.0, center=True)
        c = sp.translate(c, [0, n * Res_Spacing, 0])
        bars.append(c)
    return sp.union_all(bars)


def ResinFence():
    bars = ResinParallelBars()
    a = sp.scad_transform(bars, ("rotate", [-Res_Angle, 0, 0]))
    b = sp.scad_transform(bars, ("rotate", [Res_Angle, 0, 0]))
    return sp.union_all([a, b])


def ResinArcFenceSupport():
    parts = []
    nx = len(Res_Arc_X_Pts)
    fence = ResinFence()
    keep_y = ResinKeepY()
    for xi in (0, nx - 1):
        dx = -Res_Arc_X_Pts[xi]
        brace = sp.translate(keep_y.intersection(fence, engine="manifold"), [dx, 0, 0])
        parts.append(brace)
        parts.append(sp.translate(ResinFenceArcTop(), [dx, 0, 0]))

    ny = len(Res_Arc_Y_Pts)
    for yi in (0, ny - 1):
        dy = Res_Arc_Y_Pts[yi]
        theta = Res_Arc_Theta_Pts[yi]
        keep_x = ResinKeepX(yi)
        rotated_fence = sp.scad_transform(fence, ("translate", [0, _res_y_offset(theta), 0]), ("rotate", [0, 0, 90]))
        brace = sp.translate(keep_x.intersection(rotated_fence, engine="manifold"), [0, dy, 0])
        parts.append(brace)
        parts.append(sp.translate(ResinFenceArcSide(yi), [0, dy, 0]))
    return sp.union_all(parts)


def ResinFolderSupports(side):
    face_parts = []
    nxf, nyf = len(Res_Folder_Face_X_Pts), len(Res_Folder_Face_Y_Pts)
    theta_face = Folder_Arc_End - Res_X_Rot - 90.0
    for xi in range(nxf):
        for yi in range(nyf):
            place = (side == 0 and (yi != 0 or (xi + 1) / nxf > 0.5)) or \
                    (side == 1 and (yi != 0 or (xi + 1) / nxf <= 0.5))
            if place:
                rod = ResinRod(Res_Folder_Face_Z_Pts[yi] + Res_Z_Raise, theta_face)
                rod = sp.translate(rod, [-Res_Folder_Face_X_Pts[xi], Res_Folder_Face_Y_Pts[yi], 0])
                face_parts.append(rod)

    result = []
    if face_parts:
        result.append(_mirror_side(sp.union_all(face_parts), side))

    nx, ny = len(Res_Folder_X_Pts), len(Res_Folder_Y_Pts)
    for xi in range(nx):
        for yi in range(ny):
            theta = 0.0 if yi == 0 else Res_Folder_Theta_Pts[yi]
            if side == 0 and xi != 0 and yi != ny - 1:
                rod = ResinRod(Res_Folder_Z_Pts[yi] + Res_Z_Raise, theta)
                rod = sp.translate(rod, [-Res_Folder_X_Pts[xi] - Folder_Half_Thickness, Res_Folder_Y_Pts[yi], 0])
                result.append(rod)
            if side == 1 and xi != nx - 1 and yi != ny - 1:
                rod = ResinRod(Res_Folder_Z_Pts[yi] + Res_Z_Raise, theta)
                rod = sp.translate(rod, [-Res_Folder_X_Pts[xi], Res_Folder_Y_Pts[yi], 0])
                rod = _mirror_side(rod, side)
                result.append(rod)
    return sp.union_all(result)


def ResinRingSupports(side):
    parts = []
    nx, ny = len(Res_Ring_X_Pts), len(Res_Ring_Y_Pts)
    for xi in range(nx):
        for yi in range(ny):
            rod = ResinRod(Res_Ring_Z_Pts[yi] + Res_Z_Raise, Res_Ring_Theta_Pts[yi])
            if side == 0:
                dx = -Res_Ring_X_Pts[xi]
            else:
                dx = -Res_Ring_X_Pts[xi] - (Folder_Half_Thickness + Folder_Squash_Clearance)
            rod = sp.translate(rod, [dx, -Res_Ring_Y_Pts[yi], 0])
            parts.append(rod)
    return sp.union_all(parts)


def ResinSupports(side):
    return sp.union_all([ResinArcSupports(), ResinFolderSupports(side), ResinRingSupports(side),
                          ResinArcFenceSupport()])


def ResPrintOrient(mesh, side):
    pole = -1.0 if side == 0 else 1.0
    return sp.scad_transform(mesh, ("translate", [0, 0, Res_Z_Raise]), ("rotate", [0, -90, 0]),
                              ("rotate", [0, 0, pole * Res_X_Rot]))


def ResinPrintHalf(side):
    body = ResPrintOrient(AssembleSide(side), side)
    return sp.union_all([body, ResinSupports(side)])


def AssembleResin():
    """v2:738-745 - the real printable layout: both halves print-oriented
    and separated in space (unlike Assemble()'s overlapping preview)."""
    left = sp.scad_transform(ResinPrintHalf(0), ("translate", [0, 7, 0]), ("rotate", [0, 0, -90]))
    right = sp.scad_transform(ResinPrintHalf(1), ("translate", [0, -7, 0]), ("rotate", [0, 0, 90]))
    return sp.union_all([left, right])


# ------------------------------------------------------------- Calibration

def CalibrationTextRing(side, test_char, vary_baseline, start, interval):
    """v4-only - see CalibrationElement()'s docstring. Same structure as
    TextAssemble()/TextRing() but every character is test_char, and
    vary_baseline shifts each of the 3 baseline ROWS by start+row*
    interval instead of looking up the real per-column layout height."""
    parts = []
    mapping_lines = []
    total = 3 * 15
    n = 0
    for baseline in range(3):
        height = Baselines[baseline]
        if vary_baseline:
            height = height + start + baseline * interval
        for i in range(15):
            n += 1
            angle = (1 + i) * Char_Theta if side == 0 else (-1 - (14 - i)) * Char_Theta
            build_log.progress_line(f"CalibrationTextRing side={side}", n, total,
                                     f"building {test_char!r} (row {baseline})")
            letter = LetterText(test_char, FONT_PATH, Type_Size)
            letter = sp.scad_transform(letter, *_text_placement_ops(angle, height))
            parts.append(letter)
            mapping_lines.append(
                f"side={side} baseline_row={baseline} col={i} char={test_char!r} height_mm={height:.4f}")
    assembled = sp.union_all(parts)
    arc = _mirror_side(Arc(Glyph_Height + 1.0), side)
    return assembled.intersection(arc, engine="manifold"), mapping_lines


def CalibrationAdditive(side, test_char, vary_baseline, start, interval):
    body = _mirror_side(LeftAdditive(), side)
    text_ring, mapping_lines = CalibrationTextRing(side, test_char, vary_baseline, start, interval)
    return sp.union_all([body, text_ring]), mapping_lines


def CalibrationAssembleSide(side, test_char, vary_baseline, start, interval):
    additive, mapping_lines = CalibrationAdditive(side, test_char, vary_baseline, start, interval)
    return additive.difference(Subtractive(side), engine="manifold"), mapping_lines


def CalibrationElement(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                        reference_baseline_row=None, reference_cutout_row=None,
                        points_per_mm=None, separation_mm=None, render_core_groove=None,
                        cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                        minkowski_enabled=None, draft_angle_deg=None):
    """v4-only - v2/hammond_split.scad has no calibration render mode at
    all (unlike hammond.scad, which reuses the shared lib's real
    Calibration_Element - see cylinder_machine.CalibrationTextRing).
    Strikes test_char at every real placement slot instead of the real
    per-column layout character; vary_baseline shifts each of the 3
    baseline ROWS (not per-column - this machine's real Baselines are one
    fixed value per row, not a per-physical-column array the way
    cylinder_machine.CalibrationTextRing sweeps) by start+row*interval.
    vary_cutout/reference_baseline_row/reference_cutout_row are accepted-
    but-ignored - no curved-platen/cutout concept exists anywhere in this
    machine's real geometry (see module docstring), matching hammond.
    yaml's own documented "Cutout is unused" precedent for the same
    underlying reason. Uses the same print-oriented, laid-apart layout as
    FullElement (not resin-supported), NOT NormalElement()'s flat/nested
    Normal layout (a real, different v2 render target now wired up
    separately - see NormalElement()'s own docstring) - Calibration
    predates that wiring and there's no requirement to make it switchable
    too, so it just keeps its own fixed vertical layout regardless of
    which build target the user last picked."""
    _require_configured()
    if not Render_Left and not Render_Right:
        raise ValueError("hammond_split: Render Left and Render Right are both off - "
                          "nothing to build. Turn at least one back on (Build tab).")
    char = Calibration_Test_Char if test_char is None else test_char
    vb = Calibration_Vary_Baseline if vary_baseline is None else vary_baseline
    st = Calibration_Start if start is None else start
    iv = Calibration_Interval if interval is None else interval

    global POINTS_PER_MM
    pts = DEFAULT_POINTS_PER_MM if points_per_mm is None else points_per_mm
    old_pts = POINTS_PER_MM
    POINTS_PER_MM = pts
    try:
        parts = []
        mapping_lines = []
        if Render_Left:
            half, m = CalibrationAssembleSide(0, char, vb, st, iv)
            half = ResPrintOrient(half, 0)
            half = sp.scad_transform(half, ("translate", [0, 7, 0]), ("rotate", [0, 0, -90]))
            parts.append(half)
            mapping_lines.extend(m)
        if Render_Right:
            half, m = CalibrationAssembleSide(1, char, vb, st, iv)
            half = ResPrintOrient(half, 1)
            half = sp.scad_transform(half, ("translate", [0, -7, 0]), ("rotate", [0, 0, 90]))
            parts.append(half)
            mapping_lines.extend(m)
        full = sp.union_all(parts)
        full, _, _, _ = sp.check_and_repair(full, label="hammond_split calibration")
        return full, mapping_lines
    finally:
        POINTS_PER_MM = old_pts


# --------------------------------------------------------------- Entry points

def _build(points_per_mm, cone_segments, simplify_tolerance_mm, minkowski_enabled, draft_angle_deg, with_resin):
    global POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius
    if not Render_Left and not Render_Right:
        # sp.union_all([]) silently returns a 0-vertex Trimesh rather than
        # raising - with both Build tab switches off that would otherwise
        # export a genuinely empty, valid-looking STL with no error at
        # all (reported as f3d showing "[EMPTY]" with no explanation).
        raise ValueError("hammond_split: Render Left and Render Right are both off - "
                          "nothing to build. Turn at least one back on (Build tab).")
    pts = DEFAULT_POINTS_PER_MM if points_per_mm is None else points_per_mm
    fn = DEFAULT_MINK_FN if cone_segments is None else cone_segments
    tol = DEFAULT_SIMPLIFY_TOLERANCE_MM if simplify_tolerance_mm is None else simplify_tolerance_mm
    mink_on = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled
    draft = DEFAULT_MINK_DRAFT_ANGLE if draft_angle_deg is None else draft_angle_deg

    old = (POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius)
    POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle = pts, tol, mink_on, fn, draft
    Mink_Radius = np.tan(np.radians(draft / 2.0)) * Mink_Height
    try:
        parts = []
        if Render_Left:
            half = ResPrintOrient(AssembleSide(0), 0)
            if with_resin:
                half = sp.union_all([half, ResinSupports(0)])
            half = sp.scad_transform(half, ("translate", [0, 7, 0]), ("rotate", [0, 0, -90]))
            parts.append(half)
        if Render_Right:
            half = ResPrintOrient(AssembleSide(1), 1)
            if with_resin:
                half = sp.union_all([half, ResinSupports(1)])
            half = sp.scad_transform(half, ("translate", [0, -7, 0]), ("rotate", [0, 0, 90]))
            parts.append(half)
        full = sp.union_all(parts)
        full, _, _, _ = sp.check_and_repair(full, label="hammond_split")
        return full, []  # char_parts always empty - see module docstring on why
    finally:
        (POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius) = old


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                 cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                 minkowski_enabled=None, draft_angle_deg=None):
    """Both halves, print-oriented and laid out apart (AssembleResin()'s
    real layout), WITHOUT resin supports - separation_mm/render_core_
    groove/align_kwargs/platen_fn accepted-but-ignored (no equivalent
    concept here), matching this repo's convention for machine-specific
    kwargs generate.py's uniform build_fn(...) call passes to every
    machine."""
    _require_configured()
    return _build(points_per_mm, cone_segments, simplify_tolerance_mm, minkowski_enabled, draft_angle_deg,
                  with_resin=False)


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                minkowski_enabled=None, draft_angle_deg=None):
    """FullElement() plus each half's own ResinSupports() - the real
    AssembleResin() print target."""
    _require_configured()
    return _build(points_per_mm, cone_segments, simplify_tolerance_mm, minkowski_enabled, draft_angle_deg,
                  with_resin=True)


def NormalElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                   cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                   minkowski_enabled=None, draft_angle_deg=None):
    """v2:544-549/v2:60 "Normal" (Render_Mode==0) - v1/HammondSplitShuttle.
    scad's GenStyle 0/4/5 "Normal"/NormalL/NormalR (v1:16,720-733), the
    OTHER real render target alongside ResinPrint()/FullElement() (v2
    Render_Mode==1/v1 GenStyle 1-3) - not a v4 invention, see Assemble()'s
    own docstring for the full derivation and the empirical proof that
    the two halves don't actually overlap. Flat, un-rotated (no
    ResPrintOrient()) and unconditionally resin-free, matching the real
    source exactly - Render_Left/Render_Right (same module globals/Build-
    tab switches FullElement/ResinPrint already use) pick NormalL/NormalR/
    combined. separation_mm/render_core_groove/align_kwargs/platen_fn
    accepted-but-ignored, same convention as FullElement/ResinPrint."""
    _require_configured()
    global POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius
    pts = DEFAULT_POINTS_PER_MM if points_per_mm is None else points_per_mm
    fn = DEFAULT_MINK_FN if cone_segments is None else cone_segments
    tol = DEFAULT_SIMPLIFY_TOLERANCE_MM if simplify_tolerance_mm is None else simplify_tolerance_mm
    mink_on = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled
    draft = DEFAULT_MINK_DRAFT_ANGLE if draft_angle_deg is None else draft_angle_deg

    old = (POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius)
    POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle = pts, tol, mink_on, fn, draft
    Mink_Radius = np.tan(np.radians(draft / 2.0)) * Mink_Height
    try:
        full = Assemble()  # reads Render_Left/Render_Right - Assemble() itself raises if both are off
        full, _, _, _ = sp.check_and_repair(full, label="hammond_split normal")
        return full, []  # char_parts always empty - see _build()'s matching comment
    finally:
        (POINTS_PER_MM, SIMPLIFY_TOLERANCE_MM, Mink_On, Mink_Fn, Mink_Draft_Angle, Mink_Radius) = old
