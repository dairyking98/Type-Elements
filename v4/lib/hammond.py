"""
v4 full-fidelity Hammond shuttle body - ports v2/hammond.scad's
RibbedShuttle()/VertResinPrint2() structure. All real-machine numbers live
in config/hammond.yaml, not here - call configure(path) once before using
anything else in this module (see generate.py).

Hammond is a different form factor from the cylinder-machine family
(Blickensderfer/Postal/Mignon/Bennett/Helios) - it's a thin arc-shaped
shuttle, not a cylinder - but it DOES genuinely share the glyph-placement
pipeline with them: v2/hammond.scad's own header comment proves its arc-
placement Theta formula reduces algebraically to the shared lib's
(Angle_Half_Step+latitude)*Latitude_Int, by treating the arc as a "fake
cylinder" of diameter 2*Shuttle_Arc_Radius. So this module reuses
cylinder_machine.place_on_cylinder/TextRing/CalibrationTextRing (same as
Mignon/Bennett/Helios) and cylinder_machine._resin_rod() for the
individual resin-support rod shape (same as Mignon/Bennett) - but builds
its own body geometry from scratch (ShuttleCylinder/AnvilShape/Rib/
PinSupport/ShuttleTaper/Label), since v2/lib/resin_support.scad's own
header explicitly excludes Hammond (along with IBM) from the cylinder
family's placement-layer/body assumptions, and Hammond's real body has no
cylinder wall/core/shaft topology at all.

placement_protrusion=Shuttle_Thickness+Shuttle_Text_Protrusion (NOT the
default Char_Protrusion, which is 0/unused here - see configure()).
Shuttle_Thickness alone (v2:380's Letter_Placement_Protrusion) is only
where the character's BLOCK ROOT/anchor sits (flush with the shell's own
outer surface, Shuttle_Arc_Radius+Shuttle_Thickness) - v2's real extrude
chain (Letter_Extrude_Offset=-.5, Letter_Extrude_Depth=Shuttle_Text_
Protrusion+.5, v2:381-382) pushes the ink-bearing FRONT face an
additional Shuttle_Text_Protrusion (0.9mm) past that anchor - confirmed
by measuring a real built character: with placement_protrusion=Shuttle_
Thickness alone, the front face landed at the same radius as the bare
shell's own surface (~37.94mm vs 37.935mm - essentially flush, no real
protrusion), reported as "letters aren't protruding correctly." Adding
Shuttle_Text_Protrusion here reproduces v2's real relief height. angle_
half_step is left at the shared lib's default 0.5 - v2's own header
comment already verified its Theta formula reduces to (Angle_Half_Step+
latitude)*Latitude_Int with the lib's own default half-step, no override
needed.

Skip_Platen_Cutout (v2:384, Hammond strikes a flat anvil, not a curved
platen) translates to PLATEN_RADIUS_MM=0 - build_glyph's scallop formula
z=(y-offset)^2*platen_radius_mm vanishes identically for every y when
platen_radius_mm=0, the exact v4 equivalent, not an approximation. See
configure().

hammond_split.scad (a completely different two-piece spoke/folder
assembly, self-contained with its own inlined glyph placement) is a
SEPARATE machine in everything but name and is NOT covered here - see
config/hammond.yaml's header comment and SESSION_LOG.md's Hammond audit
chapter.

Groove (config/hammond.yaml's element.groove) picks between v2's two
real, mutually-exclusive BODY ASSEMBLY mechanisms: false (default) is the
internal rib + square drive-pin boss (Rib()/PinSupport()/
PinSupportHole(), unioned onto the shell); true is a snap-fit groove cut
directly into the shell (GrooveShape()/ResinChamfer(), subtracted -
see GrooveShape()'s docstring). Note the module-level function is named
GrooveShape(), not Groove() - Python has one namespace for module
globals, unlike OpenSCAD's separate module/variable namespaces, so it
can't share the name with the Groove config boolean. tune.py's Build tab
shows this as the "Rib" checkbox (inverted) - user-facing wording is
"Without Rib" for Groove=true, to keep it distinct from the UNRELATED
resin.horizontal_method "Cut Groove" support scheme below (both used to
just be called "groove", with no way to tell them apart by name alone -
see config/hammond.yaml's matching comment).

Resin support for the "vertical" print orientation (ResinSupport()) is a
faithful port of v2's real VertResinSupport2() - same tiers, same
coordinates, same ConnectingRod/ResinRod call sites - after an earlier
from-scratch grid+raycast redesign (rod SHAPE reused, but placement
re-derived from the built mesh's own surface) repeatedly didn't match
v2's real connecting-rod pattern. Individual rod SHAPE still reuses
cylinder_machine._resin_rod() (the shared primitive Mignon/Bennett also
reuse) in place of v2's own bespoke ResinRod(); ConnectingRod is
resin_support.connecting_rod() (ported literally from
v2/hammond.scad:419's hull-of-two-spheres) - the one primitive that
doesn't exist for any other machine's resin-support system, since none
of them brace rods against each other.

"horizontal" print orientation has TWO real v2 outer-wall support
schemes, picked by resin.horizontal_method (v4-specific, independent of
Groove/the Rib checkbox - see config/hammond.yaml's matching comment and
ResinPrint()'s own docstring for the full derivation): "cut_groove" is
HorizGroovedResinSupport(), a faithful port of HorizGroovedResin3() - a
swept, perforated breakaway-groove support RING (Resin2Profile(),
revolved +-60 degrees via sp.revolve_polygon_partial()), not individual
rods - v2's real "Cut Groove" support, distinct from the Groove config
boolean above despite the shared word. "resin_rod" is
HorizWallRodSupport(), the outer-wall tier of HorizResinSupport2's real
per-rod scheme (_rod2(), a THIRD bespoke rod primitive after ResinRod/
ResinRod2). Whenever the body actually has a rib (Groove=false),
HorizRibResinSupport() - the REST of that same HorizResinSupport2 port,
supporting along the rib's own back edge and around the center
drive-pin hole - is always added too, regardless of horizontal_method
(no cut-groove equivalent exists for that geometry). v2's own
ResinPrint() dispatcher (v2:1060-1073) only calls
VertResinPrint2()/HorizGroovedResin3() directly, but
HorizResinPrint2()/HorizResinSupport2() are real, complete, carefully-
built functions in the source (confirmed identical in v1's pre-migration
original too) - just not wired into that particular dispatcher's two
Resin_Support_Orientation values in the exported customizer. An earlier
version of this port (a) used a from-scratch grid+raycast redesign for
ALL of "horizontal" (reported as "totally fucked up"), (b) then
force-used GroovedShuttle()/HorizGroovedResin3 unconditionally for
"horizontal" after finding v2:1006-1021 never checks Groove, and (c)
then coupled the wall-support choice 1:1 to Groove (matching v2's own
per-scheme body pairing) - corrected across those three: first once the
user confirmed the ribbed body can print horizontally too with its own
proper support scheme, then again once the user pointed out the wall
method should be a genuinely independent choice from whether the body
has a rib, since the ring never touches the rib either way.
"""

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon as ShapelyPolygon
from shapely.ops import unary_union

import scad_primitives as sp
import cylinder_machine
import resin_support

_configured = False


def _require_configured():
    if not _configured:
        raise RuntimeError("call hammond.configure(config_path) before using this module")


def _circ_res(fn):
    """Shapely's Point.buffer(resolution=) is points-per-quarter-circle;
    OpenSCAD's $fn is total segments for a full circle."""
    return max(1, round(fn / 4.0))


def _wedge_complement_poly(p1, apex, p3, far=100.0):
    """v2's recurring hexagon-shaped polygon(p1, apex, p3, (0,far),
    (-far,0), (0,-far)) construction (AnvilShape() v2:437, Rib()'s final
    trim v2:478) - the COMPLEMENT of the wedge between p1 and p3 (as seen
    from apex), extended far enough (far=100, an arbitrary "big enough"
    construction sentinel, not a real dimension - same category as
    cylinder_machine.TopMinkCleanup's inline 15/5 sentinels) to cover the
    rest of the relevant area regardless of the real part's radius."""
    return ShapelyPolygon([p1, apex, p3, (0, far), (-far, 0), (0, -far)])


def configure(config_path):
    """Loads config_path (YAML) and sets this module's globals - see
    blickensderfer.configure()'s docstring for the general scheme."""
    global _configured
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    g = globals()
    g["CONFIG"] = cfg
    # Blickensderfer/Postal use z=0.01; Mignon/Bennett/Helios use 0.001 -
    # matching that more recent convention here too (also matches v2's own
    # z=.001 at v2/hammond.scad:77).
    g["z"] = 0.001

    font = cfg["font"]
    g["FONT_PATH"] = font["path"]
    g["FONT_SIZE_MM"] = font["size_mm"]

    label = cfg["label"]
    g["LABEL_FONT_PATH"] = label["font_path"]
    g["Shuttle_Label1"] = label["label1"]
    g["Shuttle_Label2"] = label["label2"]
    g["Shuttle_Label_Size"] = label["label_size_mm"]
    g["Shuttle_Label_Depth"] = label["depth_mm"]

    e = cfg["element"]
    g["Shuttle_Arc_Radius_Shrinkage_Multiplier"] = e["shrinkage_multiplier"]
    g["Anvil_OD"] = e["anvil_od"]
    g["Shuttle_Arc_Radius"] = (e["anvil_od"] / 2.0) * e["shrinkage_multiplier"]
    g["Shuttle_Thickness"] = e["shuttle_thickness"]
    g["Shuttle_Text_Protrusion"] = e["shuttle_text_protrusion"]
    g["Shuttle_Height_Offset"] = e["shuttle_height_offset"]
    # Is_Math (v2:128) is a derived tag lookup on the SELECTED layout
    # preset in v2 - simplified here to "does the active layout have 4
    # rows" (the Math Universal preset is the only real 4-row layout;
    # every other preset has 3), per explicit user direction, rather than
    # a separate manually-set config toggle that could drift out of sync
    # with the actual layout.rows content.
    g["Is_Math"] = len(cfg["layout"]["rows"]) == 4
    g["Shuttle_Height"] = ((e["math_shuttle_height"] if g["Is_Math"] else e["normal_shuttle_height"])
                            + e["shuttle_height_offset"])
    g["Shuttle_Rib_Plane"] = e["shuttle_rib_plane_base"] + e["shuttle_height_offset"]
    g["Shuttle_Rib_Thickness"] = e["shuttle_rib_thickness"]
    g["Shuttle_Rib_Width"] = e["shuttle_rib_width"]
    g["Shuttle_Square_Hole_Offset"] = e["shuttle_square_hole_offset"]
    g["Shuttle_Square_Hole_Width"] = e["shuttle_square_hole_width"]
    g["Shuttle_Square_Hole_Length"] = e["shuttle_square_hole_length"]
    g["Shuttle_Square_Hole_Radius"] = e["shuttle_square_hole_radius"]
    g["Shuttle_Pin_Support_Height"] = e["shuttle_pin_support_height"]
    g["Shuttle_Pin_Support_Base_Width"] = e["shuttle_pin_support_base_width"]
    g["Shuttle_Pin_Support_Base_Length"] = e["shuttle_pin_support_base_length"]
    g["Shuttle_Pin_Support_Height_Offset"] = e["shuttle_pin_support_height_offset"]
    g["Shuttle_Pin_Support_Height2"] = e["shuttle_pin_support_height2"]
    g["Shuttle_Rib_Hump_Distance"] = e["shuttle_rib_hump_distance"]
    g["Shuttle_Rib_Circle"] = e["shuttle_rib_circle"]
    g["Shuttle_Rib_Circle_Radius"] = e["shuttle_rib_circle_radius"]
    g["Shuttle_Taper"] = e["shuttle_taper_deg"]
    g["Shuttle_Taper_Step"] = e["shuttle_taper_step"]
    g["Anvil_ID_Raw"] = e["anvil_id_raw"]
    g["Anvil_IR_Offset"] = g["Shuttle_Arc_Radius"] - e["anvil_od"] / 2.0
    g["Anvil_ID"] = e["anvil_id_raw"] + 2 * g["Anvil_IR_Offset"]
    g["Rib_Fillet_Resin_Clearance"] = e["rib_fillet_resin_clearance"]
    # Angle_Pitch (v2:203) = (angular_span_deg/angular_divisions)/
    # shrinkage_multiplier - the shuttle's real 120deg/32-division arc.
    g["Angle_Pitch"] = (e["angular_span_deg"] / float(e["angular_divisions"])) / e["shrinkage_multiplier"]

    # Groove (v2:258) - see config/hammond.yaml's matching comment. Shuttle_
    # Groove_Depth/Shuttle_Groove_Nub_Size (v2:259-260) are both derived
    # from Shuttle_Thickness, not independently tunable.
    g["Groove"] = bool(e.get("groove", False))
    g["Shuttle_Groove_Depth"] = g["Shuttle_Thickness"] / 2.0
    g["Shuttle_Groove_Nub_Size"] = g["Shuttle_Thickness"] / 2.0
    g["Shuttle_Groove_Nub_Angle"] = e["shuttle_groove_nub_angle"]
    g["Groove_Tab_Width"] = e["groove_tab_width"]
    g["Groove_Opening_Offset"] = e["groove_opening_offset"]
    g["Support_Groove_Thickness"] = e["support_groove_thickness"]
    g["Support_Groove_R"] = 0.5 * (g["Shuttle_Thickness"] - g["Support_Groove_Thickness"])
    # v4-specific, not a v2 value - FDM print-fit clearance for RibOnly()'s
    # groove-interface flange (see GrooveShape()'s shrink parameter and
    # RibOnly()'s own docstring). Shrinks the flange (the "male" piece,
    # printed separately from the Shuttle) rather than growing the
    # Shuttle's own groove cut, per explicit request.
    g["Rib_Interface_Offset"] = e.get("rib_interface_offset_mm", 0.15)

    q = cfg["quality"]
    g["Cyl_Fn"] = q["cyl_fn"]
    g["Surface_Fn"] = q["surface_fn"]
    g["Text_Fn"] = q["text_fn"]
    g["Text_2D_Fn"] = q["text_fn"]

    # ---- glyph placement wiring (shared cylinder_machine.py reuse) ----
    g["Element_Diameter"] = 2.0 * g["Shuttle_Arc_Radius"]
    g["Char_Protrusion"] = 0.0  # unused - no curved platen, see PLATEN_RADIUS_MM
    g["Platen_Diameter"] = 0.0  # unused, same reason
    # Skip_Platen_Cutout (v2:384) == platen_radius_mm=0 (see module docstring).
    # NOT derived as 1/Platen_Diameter like every other machine (would divide
    # by zero) - explicitly 0 here.
    g["PLATEN_RADIUS_MM"] = 0.0

    layout = cfg["layout"]
    n_cols = len(layout["rows"][0])
    g["DHIATENSOR"] = layout["rows"]
    g["BASELINE_ROW"] = layout["baseline_row"]
    # Cutout_Row - see config/hammond.yaml's matching comment (dead, since
    # Skip_Platen_Cutout means the scallop term is always multiplied by
    # PLATEN_RADIUS_MM=0 regardless of this value).
    g["CUTOUT_ROW"] = layout["cutout_row"]
    g["LATITUDE_INT"] = g["Angle_Pitch"]
    g["BASELINE_Z_OFFSET"] = (g["Shuttle_Height"] - g["Shuttle_Rib_Plane"]
                               - g["Shuttle_Rib_Thickness"])  # Rib_Bottom_Z, v2:337
    # Placement_Map (v2:371) - col<=14 ? col-16 : col-14, the arc's real
    # non-identity physical-column seam mapping. Stored literally in YAML
    # (like every other machine's placement_map) rather than computed from
    # n_cols here, so tune.py's Layout tab (which reads layout.
    # placement_map/latitude_columns directly) works unmodified.
    g["PLACEMENT_MAP"] = layout["placement_map"]
    assert len(g["PLACEMENT_MAP"]) == n_cols, "layout.placement_map/rows column count mismatch"

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
    g["DEFAULT_RENDER_CORE_GROOVE"] = False  # no core groove concept at all
    g["DEFAULT_RESIN_SUPPORT"] = b["resin_support"]
    g["Resin_Support"] = g["DEFAULT_RESIN_SUPPORT"]  # v2's Resin_Support (v2:298)
    g["DEFAULT_CONE_SEGMENTS"] = q["minkowski_fn"]
    g["DEFAULT_SIMPLIFY_TOLERANCE_MM"] = b.get("simplify_tolerance_mm", 0.005)
    g["DEFAULT_MINKOWSKI_ENABLED"] = b.get("minkowski_enabled", False)
    g["DEFAULT_DRAFT_ANGLE_DEG"] = b.get("draft_angle_deg", 55.0)
    g["Platen_Fn"] = q["cyl_fn"]  # no separate platen surface (no platen at all)

    r = cfg["resin"]
    g["Resin_Fn"] = r["resin_fn"]
    g["Resin_Rod_OD"] = r["rod_od"]
    g["Resin_Tip_OD"] = r["tip_od"]
    g["Resin_Tip_L"] = r["tip_l"]
    g["Resin_Inset"] = r["inset"]
    g["Resin_Min_Rod_Height"] = r["min_rod_height"]
    g["Resin_Raft_Thickness"] = r["raft_thickness"]
    g["Resin_Raft_OD"] = r["raft_od"]
    g["Resin_Rod_Raft"] = True  # each rod grows its own small raft (no shared raft ring here)
    g["Resin_Support_Spacing"] = r["spacing"]
    g["Resin_Support_Edge_Gap"] = r.get("edge_gap", 0.1)
    # No longer consulted by any geometry function - _rod2()'s real v2
    # interference depth didn't transfer to the substituted shared rod
    # shape (see _rod2()'s own docstring for the full derivation) and was
    # replaced there with a different, deliberately-computed value. Kept
    # as a real, documented v2 machine value (still real data, just not
    # currently wired to anything) rather than deleted.
    g["Tip_Interference"] = r.get("tip_interference", 1.2)
    g["Resin_Support_Orientation"] = r.get("orientation", "vertical")
    # horizontal_method - v4-specific, independent of Groove/the Build tab's
    # Rib checkbox. See config/hammond.yaml's matching comment and
    # ResinPrint()'s docstring below for the full derivation.
    g["Horizontal_Support_Method"] = r.get("horizontal_method", "resin_rod")

    g["OUTPUT_DIR"] = cfg["output"]["directory"]
    g["OUTPUT_STL_NAME"] = cfg["output"]["stl_name"]

    calibration = cfg.get("calibration", {})
    g["Calibration_Test_Char"] = calibration.get("test_char", "H")
    g["Calibration_Vary_Baseline"] = calibration.get("vary_baseline", False)
    g["Calibration_Vary_Cutout"] = calibration.get("vary_cutout", False)
    g["Calibration_Start"] = calibration.get("start", -0.7)
    g["Calibration_Interval"] = calibration.get("interval", 0.05)

    # ---- Rib() derived geometry (v2:333-354) ----
    R = g["Shuttle_Arc_Radius"]
    half_ang_deg = g["Angle_Pitch"] * 16.0
    g["Z_Offset"] = R * np.cos(np.radians(half_ang_deg))
    g["X_Max"] = g["Shuttle_Height"] - g["Shuttle_Rib_Plane"] - g["Shuttle_Rib_Thickness"] / 2.0
    g["X_Min"] = g["Shuttle_Height"] - g["X_Max"]
    g["Shuttle_Rib_Circle_Offset"] = g["Z_Offset"] + g["Shuttle_Rib_Circle"] + g["Shuttle_Rib_Hump_Distance"]
    y_prime = (1.0 / (2 * g["Shuttle_Rib_Circle_Offset"])) * (
        g["Shuttle_Rib_Circle_Offset"] ** 2
        + (R - g["Shuttle_Rib_Circle_Radius"] - g["Shuttle_Rib_Width"]) ** 2
        - (g["Shuttle_Rib_Circle_Radius"] + g["Shuttle_Rib_Circle"]) ** 2)
    x_prime = np.sqrt((R - g["Shuttle_Rib_Circle_Radius"] - g["Shuttle_Rib_Width"]) ** 2 - y_prime ** 2)
    g["Y_Prime"] = y_prime
    g["X_Prime"] = x_prime
    theta_a = np.degrees(np.arctan(y_prime / x_prime))
    theta_2 = np.degrees(np.arctan((g["Shuttle_Rib_Circle_Offset"] - y_prime) / x_prime))
    g["Cp_1_X"] = R * np.cos(np.radians(theta_a)) - g["Rib_Fillet_Resin_Clearance"]
    g["Cp_1_Y"] = R * np.sin(np.radians(theta_a))
    g["Cp_2_X"] = x_prime - g["Shuttle_Rib_Circle_Radius"] * np.cos(np.radians(theta_2))
    g["Cp_2_Y"] = y_prime + g["Shuttle_Rib_Circle_Radius"] * np.sin(np.radians(theta_2))
    # v2:343-344 - used by VertResinSupport2's "Under Rib - Rib Thickness
    # on Edges" tier (ResinSupport()).
    g["Inner_Arc_Intercept"] = np.sqrt((R - g["Shuttle_Rib_Width"]) ** 2 - g["Z_Offset"] ** 2)
    g["Outer_Arc_Intercept"] = np.sqrt(R ** 2 - g["Z_Offset"] ** 2)

    # ---- ShuttleTaper() derived geometry (v2:326-330) ----
    g["Taper_Inset_X"] = (R - g["z"]) * np.cos(np.radians(half_ang_deg - g["Shuttle_Taper"]))
    g["Taper_Inset_Y"] = (R - g["z"]) * np.sin(np.radians(half_ang_deg - g["Shuttle_Taper"]))
    g["Taper_Outset_X"] = np.cos(np.radians(half_ang_deg + g["z"])) * (R + g["Shuttle_Taper_Step"])
    g["Taper_Outset_Y"] = np.sin(np.radians(half_ang_deg + g["z"])) * (R + g["Shuttle_Taper_Step"])

    _configured = True
    cylinder_machine._receive_config(g, "hammond")


# --------------------------------------------------------------- Body shell

def ShuttleCylinder():
    return sp.cylinder_z(2 * (Shuttle_Arc_Radius + Shuttle_Thickness), Shuttle_Height + 2 * z,
                          sections=Cyl_Fn, base_z=-z)


def AnvilShape():
    """v2:434-440 - union(wedge-complement polygon, circle(r=Shuttle_Arc_
    Radius)), extruded. Subtracting this from ShuttleCylinder() keeps only
    the annular arc segment within +-16*Angle_Pitch (the shuttle's real
    angular half-extent) between radius Shuttle_Arc_Radius and Shuttle_
    Arc_Radius+Shuttle_Thickness."""
    R = Shuttle_Arc_Radius
    half_ang_rad = np.radians(Angle_Pitch * 16.0)
    reach = R * 3.0
    p1 = (reach * np.cos(half_ang_rad), -reach * np.sin(half_ang_rad))
    p3 = (reach * np.cos(half_ang_rad), reach * np.sin(half_ang_rad))
    wedge_complement = _wedge_complement_poly(p1, (0.0, 0.0), p3)
    circle = Point(0, 0).buffer(R, resolution=_circ_res(Cyl_Fn))
    poly2d = unary_union([wedge_complement, circle])
    shape = trimesh.creation.extrude_polygon(poly2d, Shuttle_Height + 10)
    return sp.translate(shape, [0, 0, -5])


def MinkCleanup():
    R = Shuttle_Arc_Radius
    bottom = sp.cylinder_z(2 * (R + 5), 5, sections=Cyl_Fn, base_z=-5)
    top = sp.cylinder_z(2 * (R + 5), 5, sections=Cyl_Fn, base_z=Shuttle_Height)
    return sp.union_all([bottom, top])


def Rib():
    """v2:451-482. Faithful transliteration of the 2D polygon/circle
    boolean sequence (not a from-scratch re-derivation) - see this
    module's docstring for why."""
    R = Shuttle_Arc_Radius
    res = _circ_res(Cyl_Fn)
    half_ang_rad = np.radians(Angle_Pitch * 16.0)

    outer = Point(0, 0).buffer(R + z, resolution=res)
    inner = Point(0, 0).buffer(R - Shuttle_Rib_Width, resolution=res)
    tri = ShapelyPolygon([(0, 0),
                           (R * np.cos(half_ang_rad), R * np.sin(half_ang_rad)),
                           (R * np.cos(half_ang_rad), -R * np.sin(half_ang_rad))])
    main_band = outer.difference(inner).difference(tri)

    rib_circle_full = Point(Shuttle_Rib_Circle_Offset, 0).buffer(Shuttle_Rib_Circle, resolution=res)
    main_circle = Point(0, 0).buffer(R, resolution=res)
    rib_circle_region = rib_circle_full.intersection(main_circle)

    fillets = []
    for n in (-1, 1):
        pts = [
            (Y_Prime, n * X_Prime),
            (Cp_1_Y, n * Cp_1_X),
            (30, n * 20),
            (np.sqrt(R ** 2 - (n * Cp_2_X) ** 2), n * Cp_2_X),
            (Cp_2_Y, n * Cp_2_X),
        ]
        poly = ShapelyPolygon(pts)
        hole = Point(Y_Prime, n * X_Prime).buffer(Shuttle_Rib_Circle_Radius, resolution=res)
        fillets.append(poly.difference(hole))

    unioned = unary_union([main_band, rib_circle_region] + fillets)

    p1 = (R * np.cos(half_ang_rad), -R * np.sin(half_ang_rad))
    p3 = (R * np.cos(half_ang_rad), R * np.sin(half_ang_rad))
    trim = _wedge_complement_poly(p1, (Z_Offset, 0.0), p3)
    final_2d = unioned.difference(trim)

    shape = trimesh.creation.extrude_polygon(final_2d, Shuttle_Rib_Thickness)
    return sp.translate(shape, [0, 0, BASELINE_Z_OFFSET])  # Rib_Bottom_Z


def _radius_square(x, y, r, fn):
    """RadiusSquare(x,y,r,fn) (v2:405-417) - hull() of 4 circles at the
    inset corners, exactly a rounded rectangle for r>0."""
    res = _circ_res(fn)
    centers = [(r, r), (x - r, r), (r, y - r), (x - r, y - r)]
    circles = [Point(cx, cy).buffer(r, resolution=res) for cx, cy in centers]
    return unary_union(circles).convex_hull


def PinSupportHull():
    top_2d = _radius_square(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width,
                             Shuttle_Square_Hole_Radius, Cyl_Fn)
    top_3d = trimesh.creation.extrude_polygon(top_2d, z)
    top_3d = sp.translate(top_3d, [0, -Shuttle_Square_Hole_Width / 2.0, Shuttle_Pin_Support_Height])

    base_2d = _radius_square(Shuttle_Pin_Support_Base_Length, Shuttle_Pin_Support_Base_Width,
                              Shuttle_Square_Hole_Radius, Cyl_Fn)
    base_3d = trimesh.creation.extrude_polygon(base_2d, z)
    base_3d = sp.translate(base_3d, [
        -Shuttle_Pin_Support_Base_Length / 2.0 + Shuttle_Square_Hole_Length / 2.0 + Shuttle_Pin_Support_Height_Offset,
        -Shuttle_Pin_Support_Base_Width / 2.0, 0])

    return trimesh.util.concatenate([top_3d, base_3d]).convex_hull


def PinSupport():
    top = sp.translate(PinSupportHull(),
                        [Shuttle_Arc_Radius - Shuttle_Square_Hole_Offset, 0,
                         Shuttle_Height - Shuttle_Rib_Plane - z])
    bottom = sp.scad_transform(PinSupportHull(), ("rotate", [180, 0, 0]))
    bottom = sp.translate(bottom,
                           [Shuttle_Arc_Radius - Shuttle_Square_Hole_Offset, 0,
                            Shuttle_Height - Shuttle_Rib_Plane - Shuttle_Rib_Thickness + z])
    boss = sp.union_all([top, bottom])

    outer_disk = sp.cylinder_z(Anvil_ID + 10, 40, sections=Cyl_Fn, base_z=-20)
    inner_disk = sp.cylinder_z(2 * (Anvil_ID / 2.0 + 0.3), 41, sections=Cyl_Fn, base_z=-20.5)
    clearance_ring = outer_disk.difference(inner_disk, engine="manifold")

    return boss.difference(clearance_ring, engine="manifold")


def PinSupportHole():
    poly2d = _radius_square(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width,
                             Shuttle_Square_Hole_Radius, Cyl_Fn)
    shape = trimesh.creation.extrude_polygon(poly2d, Shuttle_Height + z)
    return sp.translate(shape, [Shuttle_Arc_Radius - Shuttle_Square_Hole_Offset,
                                 -Shuttle_Square_Hole_Width / 2.0, -z])


def RibAssembled():
    combined = sp.union_all([Rib(), PinSupport()])
    return combined.difference(PinSupportHole(), engine="manifold")


def RibOnly():
    """Not a v2 function - a v4-specific FDM export target. The rib
    +pin-support assembly (RibAssembled()), PLUS a groove-interface
    flange, as its own separate printable part, for printing the
    shuttle shell and rib as two separate FDM pieces instead of one
    fused resin print - see generate.py's --hammond-part=rib_only and
    tune.py's Build tab. No resin supports at all (FDM's own slicer
    handles that, not Hammond's resin-print machinery).

    The flange is GrooveShape() itself, reused as a POSITIVE addition
    here instead of the cutter it normally is (see that function's own
    docstring) - real v2 never does this (v2's Groove assembly REPLACES
    Rib()/PinSupport() entirely, no separate printed rib piece exists in
    that path at all), so this is a deliberate v4-only mechanism, added
    per explicit request: "the rib would have negative space of the
    nubs, and positive space for the slot" - which is exactly the DISK
    portion of GrooveShape()'s own shape (disk minus the 4 nub
    cylinders) - the SAME geometry that cuts the slot's circumferential
    channel into a Groove=true shell also happens to be the correct
    shape for a flange that fills that same channel and clears its 4
    retention ridges, just added instead of subtracted.
    include_tab=False - the "tab" portion is EXCLUDED here: it only ever
    makes sense as a cutter (an oversized box reaching to x=50,
    guaranteeing a clean through-cut regardless of the shell's real
    wall thickness - see GrooveShape()'s own docstring). Reused as
    positive material it would just be a 50mm spike sticking out of the
    printed part - the tab creates the INSERTION OPENING on the shell
    side; the flange being inserted through that opening doesn't need
    an equivalent feature of its own. shrink=Rib_Interface_Offset gives
    the flange (the "male" piece here, since it's the one being
    test-fit into an already-cut slot) FDM print clearance - shrinking
    the male side rather than growing the Shuttle's own groove cut, per
    explicit request."""
    _require_configured()
    rib = sp.union_all([RibAssembled(),
                         GrooveShape(shrink=Rib_Interface_Offset, include_tab=False, trim_to_arc=True)])
    rib, _, _, _ = sp.check_and_repair(rib, label="RibOnly")
    return rib


def GrooveShape(shrink=0.0, include_tab=True, trim_to_arc=False):
    """v2:484-500 - circumferential snap-fit slot cut into the shell,
    opening from its INNER surface (a solid disk r=Shuttle_Arc_Radius+
    Shuttle_Groove_Depth, unioned with a radial "tab" box reaching out to
    x=50 - a construction sentinel, not a real dimension, same as
    _wedge_complement_poly's far=100), minus 4 nub-shaped retention-detent
    clearances at +-29/+-58deg. Z-spans [Rib_Bottom_Z, Rib_Bottom_Z+
    Shuttle_Rib_Thickness] for the disk, [Rib_Bottom_Z-Groove_Opening_
    Offset/2, Rib_Bottom_Z+Shuttle_Rib_Thickness+Groove_Opening_Offset/2]
    for the tab (v2's translate() only wraps the cube, not the cylinder -
    two different Z depths, built as separate solids here rather than one
    shared extrusion). Subtracted from the shell in the Groove=true
    assembly path, replacing Rib()/PinSupport()/PinSupportHole() entirely
    - no separate rib piece in this assembly at all.

    shrink (v4-specific, NOT a v2 term - default 0.0 reproduces the
    original shell-cutter shape exactly): reduces the disk radius and
    tab half-width by this amount, shrinking the flange's outer/side
    boundary uniformly for FDM print-fit clearance when this same shape
    gets reused as a positive addition elsewhere (see RibOnly()) - the 4
    nub-clearance notches are left at their real size/position, only the
    outer positive footprint shrinks. Never applied at this function's
    own original call site (the shell cutter), where shrink stays 0.0 -
    only RibOnly()'s new flange use passes a nonzero value.

    include_tab (v4-specific - default True reproduces the original
    shell-cutter shape exactly): set False to omit the tab box entirely
    - see RibOnly()'s own docstring for why its positive-flange use
    needs this off (the tab's x=50 overshoot only makes sense as a
    cutter).

    trim_to_arc (v4-specific - default False reproduces the original
    shell-cutter shape exactly, a FULL 360deg disk): set True to trim
    the disk down to the shuttle's real angular span, using the exact
    same wedge-complement trim Rib() applies to itself (same apex/
    half_ang_rad, just re-derived at THIS disk's own, larger radius
    rather than Rib()'s R - the trim is angle-defined from a fixed
    apex, not radius-defined, so re-deriving p1/p3 at the flange's own
    radius keeps the trim boundary reaching all the way to its actual
    edge). Needed because GrooveShape()'s disk is meant to be subtracted
    from a FULL circular shell in its real cutter use (no trim needed
    there - the shell itself gets trimmed elsewhere), but RibOnly()'s
    positive-flange use adds it to Rib(), which is already trimmed to
    the real ~120deg arc - without this, the flange would be a full
    360deg disk floating mostly in empty space beyond the rib's own
    actual angular footprint."""
    res = _circ_res(Cyl_Fn)
    disk_2d = Point(0, 0).buffer(Shuttle_Arc_Radius + Shuttle_Groove_Depth - shrink, resolution=res)
    if trim_to_arc:
        half_ang_rad = np.radians(Angle_Pitch * 16.0)
        disk_r = Shuttle_Arc_Radius + Shuttle_Groove_Depth - shrink
        p1 = (disk_r * np.cos(half_ang_rad), -disk_r * np.sin(half_ang_rad))
        p3 = (disk_r * np.cos(half_ang_rad), disk_r * np.sin(half_ang_rad))
        disk_2d = disk_2d.difference(_wedge_complement_poly(p1, (Z_Offset, 0.0), p3))
    disk = trimesh.creation.extrude_polygon(disk_2d, Shuttle_Rib_Thickness)

    parts = [disk]
    if include_tab:
        tab_half_width = Groove_Tab_Width / 2.0 - shrink
        tab_2d = ShapelyPolygon([
            (0, -tab_half_width), (50, -tab_half_width),
            (50, tab_half_width), (0, tab_half_width),
        ])
        tab = trimesh.creation.extrude_polygon(tab_2d, Shuttle_Rib_Thickness + Groove_Opening_Offset)
        tab = sp.translate(tab, [0, 0, -Groove_Opening_Offset / 2.0])
        parts.append(tab)

    shape = sp.union_all(parts)
    for n in (-2, -1, 1, 2):
        nub = sp.cylinder_z(2 * Shuttle_Groove_Nub_Size, Shuttle_Rib_Thickness + 2 * z,
                             sections=Cyl_Fn, base_z=-z)
        nub = sp.translate(nub, [Shuttle_Arc_Radius + Shuttle_Groove_Depth, 0, 0])
        nub = sp.rotate_z(nub, Shuttle_Groove_Nub_Angle * n)
        shape = shape.difference(nub, engine="manifold")

    return sp.translate(shape, [0, 0, BASELINE_Z_OFFSET])  # Rib_Bottom_Z


def ResinChamfer():
    """v2:789-792 - cone frustum subtracted from the shell's bottom-inner
    edge (r1=Anvil_OD/2+Support_Groove_R at z=0, tapering to r2=Anvil_OD/2
    at z=Support_Groove_R) - a small chamfer at the shell's bottom face.
    Real v2 only ever calls this from GroovedShuttle() (RibbedShuttle()
    never does). Currently UNUSED - both call sites (Additive()/
    CalibrationAdditive()) are commented out: briefly made unconditional
    (independent of Groove/the Rib checkbox) per an earlier request, then
    disabled per explicit follow-up rather than properly conditioning it
    on which circumferential edge actually needs it (the one without
    resin supports touching it already) - real work, deferred for now.
    Kept defined (not deleted) for whenever that per-edge conditional is
    worth doing."""
    return sp.frustum_z(2 * (Anvil_OD / 2.0 + Support_Groove_R), Anvil_OD,
                         Support_Groove_R, sections=Cyl_Fn, base_z=0.0)


def ShuttleTaper(force_groove=None):
    parts = []
    b = [-z, Shuttle_Height - Shuttle_Rib_Plane]
    # v2:571's c=[Rib_Bottom_Z+z+(Groove?2:0), 10] - the Groove=true
    # assembly needs 2mm more taper depth at the bottom (BASELINE_Z_OFFSET
    # is Rib_Bottom_Z). force_groove: threaded from Subtractive()/
    # Additive() so the horizontal print path's forced-groove body (see
    # Additive()'s docstring) gets a taper depth that actually matches
    # its own body, regardless of the config's own Groove setting.
    use_groove = Groove if force_groove is None else force_groove
    c = [BASELINE_Z_OFFSET + z + (2.0 if use_groove else 0.0), 10.0]
    half_ang_rad = np.radians(Angle_Pitch * 16.0 + z)
    p3x = (Shuttle_Arc_Radius - z) * np.cos(half_ang_rad)
    p3y = (Shuttle_Arc_Radius - z) * np.sin(half_ang_rad)
    for a in range(2):
        for sign in (1, -1):
            poly = ShapelyPolygon([
                (Taper_Inset_X, sign * Taper_Inset_Y),
                (Taper_Outset_X, sign * Taper_Outset_Y),
                (p3x, sign * p3y),
            ])
            shape = trimesh.creation.extrude_polygon(poly, c[a])
            parts.append(sp.translate(shape, [0, 0, b[a]]))
    return sp.union_all(parts)


def Label():
    """v2:582-593 - two flat text() calls (halign=center, valign=baseline
    - matching cylinder_machine.build_text_string()'s own baseline
    convention exactly, no approximation needed here)."""
    depth = 2.0
    right = cylinder_machine.build_text_string(Shuttle_Label1, Shuttle_Label_Size, LABEL_FONT_PATH, depth)
    right = sp.scad_transform(
        right,
        ("rotate", [0, 0, Angle_Pitch * 0.25]),
        ("translate", [Shuttle_Arc_Radius + Shuttle_Thickness - Shuttle_Label_Depth, 0,
                        (Shuttle_Height - Shuttle_Height_Offset) / 2.0]),
        ("rotate", [0, 90, 0]),
    )
    left = cylinder_machine.build_text_string(Shuttle_Label2, Shuttle_Label_Size, LABEL_FONT_PATH, depth)
    left = sp.scad_transform(
        left,
        ("rotate", [0, 0, -Angle_Pitch + Angle_Pitch * 0.25]),
        ("translate", [Shuttle_Arc_Radius + Shuttle_Thickness - Shuttle_Label_Depth, 0,
                        (Shuttle_Height - Shuttle_Height_Offset) / 2.0]),
        ("rotate", [0, 90, 0]),
    )
    return sp.union_all([right, left])


# ---------------------------------------------------------------- Element

def Additive(points_per_mm=None, separation_mm=None, align_kwargs=None, cone_segments=None,
             simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
             draft_angle_deg=None, force_groove=None):
    text_ring, char_parts = cylinder_machine.TextRing(
        points_per_mm=points_per_mm, separation_mm=separation_mm, align_kwargs=align_kwargs,
        cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Shuttle_Thickness + Shuttle_Text_Protrusion)
    shell = sp.union_all([text_ring, ShuttleCylinder()])
    shell = shell.difference(AnvilShape(), engine="manifold")
    shell = shell.difference(MinkCleanup(), engine="manifold")
    # ResinChamfer() (v2:789-792) is only ever called from GroovedShuttle()
    # in real v2 - RibbedShuttle() never applies it at all. Briefly made
    # unconditional here (independent of Groove/the Rib checkbox) per an
    # earlier request, then reverted per explicit follow-up: the chamfer
    # should really only apply to the side that doesn't already have
    # resin supports touching it (the OTHER circumferential edge, per the
    # Rib/Groove-conditional split that would take real work to do
    # properly) - rather than leave it unconditional (wrong for the
    # support-adjacent edge) or half-solve it, commented out entirely for
    # now. Revisit with the real per-edge conditional if/when it's worth
    # the effort.
    # shell = shell.difference(ResinChamfer(), engine="manifold")
    # Groove (config/hammond.yaml's element.groove) picks between v2's two
    # real, mutually-exclusive assembly mechanisms - GroovedShuttle()
    # (snap-fit groove, no separate rib piece) vs. RibbedShuttle() (rib +
    # square drive-pin boss, the default/original path). See GrooveShape()'s
    # docstring for the full derivation. force_groove overrides the config
    # flag - v2's real HorizGroovedResin3 (horizontal print orientation)
    # ALWAYS uses GroovedShuttle() regardless of Groove (v2:1006-1021 never
    # checks the Groove variable at all, unlike VertResinPrint2 which
    # does) - see ResinPrint()'s docstring.
    use_groove = Groove if force_groove is None else force_groove
    if use_groove:
        shell = shell.difference(GrooveShape(), engine="manifold")
        return shell, char_parts
    return sp.union_all([shell, RibAssembled()]), char_parts


def Subtractive(render_core_groove=None, force_groove=None):
    # render_core_groove: accepted (matching cylinder_machine.Subtractive's
    # signature/generate.py's uniform build_fn(...) call) but unused -
    # Hammond has no core groove concept at all (see module docstring).
    return sp.union_all([ShuttleTaper(force_groove=force_groove), Label()])


def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
                cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
                draft_angle_deg=None, force_groove=None):
    _require_configured()
    additive, char_parts = Additive(points_per_mm, separation_mm, align_kwargs=align_kwargs,
                                     cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
                                     platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                     draft_angle_deg=draft_angle_deg, force_groove=force_groove)
    print(f"Additive: verts={len(additive.vertices)} faces={len(additive.faces)} "
          f"watertight={additive.is_watertight}", flush=True)
    subtractive = Subtractive(render_core_groove, force_groove=force_groove)
    print(f"Subtractive (unioned): verts={len(subtractive.vertices)} faces={len(subtractive.faces)} "
          f"watertight={subtractive.is_watertight}", flush=True)
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="FullElement")
    return full, char_parts


# ------------------------------------------------------------- Calibration

def CalibrationAdditive(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                         reference_baseline_row=None, reference_cutout_row=None,
                         points_per_mm=None, separation_mm=None, align_kwargs=None,
                         cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                         minkowski_enabled=None, draft_angle_deg=None):
    text_ring, mapping_lines = cylinder_machine.CalibrationTextRing(
        test_char, vary_baseline, vary_cutout, start, interval,
        reference_baseline_row, reference_cutout_row, points_per_mm, separation_mm,
        align_kwargs=align_kwargs, cone_segments=cone_segments,
        simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
        minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg,
        placement_protrusion=Shuttle_Thickness + Shuttle_Text_Protrusion)
    shell = sp.union_all([text_ring, ShuttleCylinder()])
    shell = shell.difference(AnvilShape(), engine="manifold")
    shell = shell.difference(MinkCleanup(), engine="manifold")
    # ResinChamfer() commented out - see Additive()'s matching comment.
    # shell = shell.difference(ResinChamfer(), engine="manifold")
    if Groove:
        shell = shell.difference(GrooveShape(), engine="manifold")
        return shell, mapping_lines
    return sp.union_all([shell, RibAssembled()]), mapping_lines


def CalibrationElement(test_char=None, vary_baseline=None, vary_cutout=None, start=None, interval=None,
                        reference_baseline_row=None, reference_cutout_row=None,
                        points_per_mm=None, separation_mm=None, render_core_groove=None,
                        align_kwargs=None, cone_segments=None, simplify_tolerance_mm=None,
                        platen_fn=None, minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    additive, mapping_lines = CalibrationAdditive(
        test_char, vary_baseline, vary_cutout, start, interval,
        reference_baseline_row, reference_cutout_row, points_per_mm, separation_mm,
        align_kwargs=align_kwargs, cone_segments=cone_segments,
        simplify_tolerance_mm=simplify_tolerance_mm, platen_fn=platen_fn,
        minkowski_enabled=minkowski_enabled, draft_angle_deg=draft_angle_deg)
    subtractive = Subtractive(render_core_groove)
    full = additive.difference(subtractive, engine="manifold")
    full, _, _, _ = sp.check_and_repair(full, label="CalibrationElement")
    return full, mapping_lines


# ------------------------------------------------------------- Resin support

def HorizGroovedResinSupport():
    """v2:1006-1021 HorizGroovedResin3's real support structure -
    Resin2Profile() (v2:1023-1038), a wall-hugging trough cross-section
    with two circular breakaway-groove perforations at its top corners
    (the "cut groove" - lets the support ring snap cleanly off the wall
    after printing), swept +-60 degrees around the shuttle's own real
    angular extent (matching v2's rotate([0,0,-60]) rotate_extrude(
    angle=120) - see sp.revolve_polygon_partial). This is a CONTINUOUS
    perforated support platform hugging the outer wall (radius Anvil_OD/2
    to Anvil_OD/2+Shuttle_Thickness), not individual rods at all - a
    completely different real v2 support architecture from
    VertResinSupport2's rod grid, which an earlier grid+raycast
    redesign incorrectly used for this orientation too (reported as
    "totally fucked up" - this replaces it).

    ShuttleTaper() (translated down by Resin_Min_Rod_Height, matching
    v2:1017-1018) is subtracted from the whole ring, clearing space for
    the shuttle's own tapered end faces - built directly in the same
    0-centered angular frame ShuttleTaper() itself already uses, no
    extra rotation needed."""
    _require_configured()
    r0 = Anvil_OD / 2.0
    main_pts = [
        (r0 + 0.0, 0.0),
        (r0 + Shuttle_Thickness, 0.0),
        (r0 + Shuttle_Thickness, -Resin_Min_Rod_Height),
        (r0 + Shuttle_Thickness / 2.0 + Resin_Raft_OD / 2.0 + Resin_Raft_Thickness, -Resin_Min_Rod_Height),
        (r0 + Shuttle_Thickness / 2.0 + Resin_Raft_OD / 2.0, -Resin_Min_Rod_Height - Resin_Raft_Thickness),
        (r0 + Shuttle_Thickness / 2.0 - Resin_Raft_OD / 2.0, -Resin_Min_Rod_Height - Resin_Raft_Thickness),
        (r0 + Shuttle_Thickness / 2.0 - Resin_Raft_OD / 2.0 - Resin_Raft_Thickness, -Resin_Min_Rod_Height),
        (r0 + 0.0, -Resin_Min_Rod_Height),
    ]

    def _circle_pts(cr, cz, radius, n=32):
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return [(cr + radius * np.cos(ti), cz + radius * np.sin(ti)) for ti in t]

    ring = sp.revolve_polygon_partial(main_pts, -60.0, 60.0, sections=Cyl_Fn)
    hole1 = sp.revolve_polygon_partial(
        _circle_pts(r0 + Shuttle_Thickness, -Support_Groove_R, Support_Groove_R), -60.0, 60.0, sections=Cyl_Fn)
    hole2 = sp.revolve_polygon_partial(
        _circle_pts(r0 + 0.0, -Support_Groove_R, Support_Groove_R), -60.0, 60.0, sections=Cyl_Fn)
    ring = ring.difference(hole1, engine="manifold")
    ring = ring.difference(hole2, engine="manifold")

    taper = sp.translate(ShuttleTaper(), [0, 0, -Resin_Min_Rod_Height])
    ring = ring.difference(taper, engine="manifold")
    return ring


def _rod2(h):
    """v2's ResinRod2(h) (v2:850-861) - Hammond's OTHER bespoke rod
    primitive (distinct from ResinRod(h1,r1,r2,h2,r3), used only by
    HorizResinSupport2/HorizGroovedResin/HorizGroovedResin2 - the last
    two are unreferenced legacy, only HorizResinSupport2 is real). Its
    raft always sits at a FIXED z (built from a literal "2" in v2 that
    numerically matches Resin_Support_Min_Height - treated as the same
    value, not an independent constant, since using two different names
    for one number is far more likely to be an unreferenced-literal
    shortcut in the original than a deliberate second value) - this
    already matches cylinder_machine._resin_rod()'s own fixed raft
    position with NO re-basing needed.

    Tip_Interference (v2:324, ~1.2mm) does NOT transfer to this port:
    v2's real ResinRod2 cone section is a literal `cylinder(...,h=2)` -
    hardcoded 2mm, unrelated to any of our config's Resin_Tip_L. v2's
    own author calibrated Tip_Interference against THAT real 2mm cone.
    This function's SHAPE was already substituted with the shared
    resin_rod() primitive (Resin_Tip_L=1.0mm default - see this module's
    own docstring: "rod SHAPE reuses cylinder_machine._resin_rod()...
    in place of v2's own bespoke ResinRod2... a minor,
    explicitly-accepted simplification"), so Tip_Interference no longer
    has a real cone to be calibrated against here and is not used.

    Simply delegates to cylinder_machine._resin_rod(h) - the exact same
    call _rod() (this file's OTHER straight-rod helper, used throughout
    ResinSupport()) already makes, with NO extra offset of any kind.
    _resin_rod() already applies this config's own Resin_Inset
    (documented in config/hammond.yaml as "tip_od/2, same convention as
    bennett.yaml") via resin_support.resin_rod()'s own tip_z=-tip_od/2+
    inset+h formula - with inset=tip_od/2 those two terms cancel exactly,
    landing the tip sphere's own CENTER precisely at h, i.e. right at
    the target surface itself. Per explicit correction: "with inset half
    of tip diameter, the center of the sphere tip is at the surface of
    the shuttle edge" - this is that exact, already-existing behavior;
    no new formula, no new constant, nothing hardcoded beyond what
    Resin_Inset/Resin_Tip_OD already are. Two earlier attempts both
    invented extra push terms (first stacking Tip_Interference on top of
    the automatic Resin_Inset - a double-count; then replacing that with
    a different invented constant, Resin_Inset+Resin_Tip_OD) chasing a
    "too far into the shuttle" report - both wrong; the fix was to
    subtract, not add: stop applying Tip_Interference at all."""
    return cylinder_machine._resin_rod(h)


def HorizWallRodSupport():
    """v2:864-950 HorizResinSupport2()'s OUTER-WALL tier only (v2:868-884) -
    individual rods (_rod2(0.0), not HorizGroovedResinSupport's swept
    ring) along the outer wall and the tapered ends, at the same radial
    band (r0..r0+Shuttle_Thickness) HorizGroovedResinSupport's ring
    covers. This is the "resin_rod" alternative to that ring for
    resin.horizontal_method - independent of Groove/element.groove/the
    Rib checkbox, since this tier never touches the rib feature either
    way (split out of the original HorizRibbedResinSupport() - see
    HorizRibResinSupport() below for the rest of that function, the part
    that DOES depend on the rib existing)."""
    _require_configured()
    r0 = Anvil_OD / 2.0
    parts = []

    thetamax = np.radians(Angle_Pitch * 32.0) - 2.0 * np.radians(Shuttle_Taper)

    # Outer Supports (v2:868-874) - 23 positions from -60 to 60deg (step
    # 120/22), both wall-adjacent radii, EXCLUDING the exact +-60
    # endpoints (v2's own "abs(theta)<59.9 || x==Anvil_OD/2+Shuttle_
    # Thickness" condition - the x== disjunct never actually fires since
    # neither radius equals that exactly, so the real effect is just
    # "skip the two endpoints").
    outer_thetas = np.linspace(-60.0, 60.0, 23)
    for theta_deg in outer_thetas[1:-1]:
        for x in (r0 + Resin_Tip_OD / 2.0, r0 + Shuttle_Thickness - Resin_Tip_OD / 2.0):
            parts.append(sp.rotate_z(sp.translate(_rod2(0.0), [x, 0, 0]), theta_deg))

    # thetamax edge supports (v2:876-879)
    for theta_deg in (np.degrees(thetamax / 2.0), -np.degrees(thetamax / 2.0)):
        parts.append(sp.rotate_z(sp.translate(_rod2(0.0), [r0, 0, 0]), theta_deg))

    # taper-step edge supports (v2:881-884)
    for theta_deg in (60.0, -60.0):
        parts.append(sp.rotate_z(sp.translate(_rod2(0.0), [r0 + Shuttle_Taper_Step, 0, 0]), theta_deg))

    return sp.union_all(parts)


def HorizRibResinSupport():
    """v2:864-950 HorizResinSupport2()'s RIB-specific tiers (v2:886-946) -
    individual rods (_rod2()) along the rib's own back/bottom plane and
    around the square drive-pin hole, in the flipped print frame. Only
    meaningful when the body actually HAS a rib (element.groove=false,
    the Build tab's Rib checkbox on) - there's no cut-groove equivalent
    for this geometry, so ResinPrint() adds this unconditionally
    whenever Groove is false, regardless of resin.horizontal_method
    (which only picks the OUTER-WALL scheme - see HorizWallRodSupport()/
    HorizGroovedResinSupport() and ResinPrint()'s docstring).

    Several v2 tiers here are loop-invariant (rebuilt identically on
    every outer theta/s iteration in v2, since neither the "under
    Pinhole" block nor the three dense fan patterns actually depend on
    the outer loop's y/theta - theta gets shadowed by an inner loop of
    the same name) - hoisted out and built once here, the same harmless
    optimization as ResinSupport()'s "at the taper" block.

    rib_h/pin_boss_h: v2's real HorizResinSupport2 gives every tier here
    (Inner_Arc_Intercept, the 3 fan patterns, Under Rib Outer/Radius/
    Center) the SAME height, Shuttle_Height-Shuttle_Rib_Plane-Shuttle_
    Rib_Thickness, EXCEPT "under Pinhole" which subtracts a further
    (Shuttle_Pin_Support_Height2-1) - confirmed by reading v2:886-946
    directly (this is NOT shared with VertResinSupport2's OWN "Under Rib"
    tier, v2:662-686, which uses a completely different, position-
    dependent sqrt formula - the two aren't related the way an earlier
    version of this fix assumed).

    That constant is Rib()'s own local BOTTOM z (confirmed: default value
    6.66 exactly equals Rib()'s local z-min) - correct as a target for
    UNFLIPPED vertical printing (a rod growing up from z=0 meets the
    rib's bottom face first). Horizontal's body DOES get flipped
    (rotate([180,0,0]), see ResinPrint()) before HorizResinSupport2's
    rods (built in the same fixed, unrotated frame either way) are added
    as a sibling - flipping REVERSES which local extreme is nearest the
    support: a rod growing up now meets whichever local z is LARGEST
    first, not smallest. Rib() is a uniform-thickness extrusion (its
    local z is the exact same range everywhere in its footprint, not
    just at one point) - the rib's OWN target is Shuttle_Height minus its
    local max, i.e. Shuttle_Rib_Plane (algebraically: Shuttle_Height -
    (Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness+Shuttle_Rib_
    Thickness)). "under Pinhole" specifically targets the pin-boss area,
    where PinSupport()'s OWN "top" piece (local max (Shuttle_Height-
    Shuttle_Rib_Plane)+Shuttle_Pin_Support_Height, taller than the plain
    rib slab - see PinSupport()) becomes the feature nearest the support
    after the flip (the flip reverses "nearest", so the TALLER-locally
    piece becomes the SHORTER-reach one) - giving pin_boss_h =
    Shuttle_Rib_Plane - Shuttle_Pin_Support_Height. v2's own
    (Shuttle_Pin_Support_Height2-1) offset was calibrated to reach into
    PinSupport's OTHER ("bottom", downward-hanging) piece - the one that
    matters pre-flip, not post-flip - so it's dropped here rather than
    reapplied to the wrong base.

    Reported as "resin rods for the rib support ... do not go to the
    right height of the rib, contacting the rib" (twice - an earlier
    single-constant fix used pin_boss_h's value, 8.2, for EVERY tier
    including the plain rib ones, which need the taller 9.7 target;
    still confirmed short afterward). Both constants verified directly:
    Rib()'s own local z range is [6.66, 6.90] everywhere in its
    footprint (confirming rib_h=Shuttle_Rib_Plane=9.7 as its flipped
    target), and RibAssembled()'s (Rib+PinSupport unioned) local max is
    8.40 - exactly Rib()'s own max (6.90) plus Shuttle_Pin_Support_Height
    (1.5), confirming PinSupport() is the taller feature driving
    pin_boss_h. Not visible from the overall assembly's watertight/
    is_volume checks (per-component, not per-contact) - see
    HorizWallRodSupport()'s docstring for why the assembly still unions
    into one connected component regardless. v2 never corrects any of
    this (this function isn't wired into v2's own ResinPrint() dispatcher
    at all - see this module's docstring) - a deliberate v4 divergence,
    not a port artifact, per explicit user confirmation."""
    _require_configured()
    parts = []

    thetamax = np.radians(Angle_Pitch * 32.0) - 2.0 * np.radians(Shuttle_Taper)
    thetaspacing = Resin_Support_Spacing / Shuttle_Arc_Radius
    # rib_h targets Rib()'s own flat slab (a UNIFORM-thickness extrusion -
    # local z is [BASELINE_Z_OFFSET, BASELINE_Z_OFFSET+Shuttle_Rib_Thickness]
    # everywhere in its footprint, confirmed - so its flipped-bottom global z
    # is the same constant, Shuttle_Height - (BASELINE_Z_OFFSET+Shuttle_Rib_
    # Thickness) = Shuttle_Rib_Plane, for every tier below EXCEPT "under
    # Pinhole"). "under Pinhole" needs a DIFFERENT, shorter target: it's
    # meant to support the pin-boss area specifically, where PinSupport()'s
    # own "top" piece (local z up to (Shuttle_Height-Shuttle_Rib_Plane)+
    # Shuttle_Pin_Support_Height, i.e. taller than the plain rib slab) is
    # the feature actually closest to the support AFTER the flip (flip
    # reverses which side is "nearest" - the piece with the LARGER local z
    # becomes the one with the SMALLER, nearer, global z) - so pin_boss_h
    # is Shuttle_Rib_Plane - Shuttle_Pin_Support_Height, not the plain rib_h.
    # v2's own pin_h (rib_h - (Shuttle_Pin_Support_Height2-1)) was
    # calibrated to reach partway into PinSupport's OTHER ("bottom",
    # downward-hanging) piece - the one that matters in VertResinSupport2's
    # UNFLIPPED context, not this one - reusing that same offset here (as
    # the previous fix did, applying one constant height everywhere) still
    # left every non-pinhole tier short. Reported as "still not touching
    # the rib" - both rib_h (was 8.2, wrong for the plain slab) and
    # pin_boss_h (needed to target PinSupport's TOP piece, not compute an
    # offset from the wrong base) are corrected below; a deliberate v4
    # divergence, not a port artifact, per explicit user confirmation.
    rib_h = Shuttle_Rib_Plane
    pin_boss_h = Shuttle_Rib_Plane - Shuttle_Pin_Support_Height

    # Inner_Arc_Intercept supports (v2:886-889)
    for s in (-1, 1):
        parts.append(sp.translate(_rod2(rib_h), [Z_Offset, s * Inner_Arc_Intercept, 0]))

    # under Pinhole (v2:921-929) - loop-invariant, built once. base_x
    # matches PinSupportHole()'s own pin-hole center X.
    base_x = Shuttle_Arc_Radius - Shuttle_Square_Hole_Offset
    for r_deg in (0.0, 180.0):
        p_a = sp.rotate_z(sp.translate(_rod2(pin_boss_h), [0, -Shuttle_Square_Hole_Width / 2.0 - Resin_Tip_OD / 2.0, 0]), r_deg)
        p_b = sp.rotate_z(sp.translate(_rod2(pin_boss_h), [Shuttle_Square_Hole_Length / 2.0 + Resin_Tip_OD / 2.0, 0, 0]), r_deg)
        parts.append(sp.translate(p_a, [base_x, 0, 0]))
        parts.append(sp.translate(p_b, [base_x, 0, 0]))

    # three dense fan patterns (v2:931-946) - loop-invariant, built once.
    for theta_deg in np.arange(-40.0, 40.0 + 1e-9, 5.0):
        parts.append(sp.rotate_z(sp.translate(_rod2(rib_h), [Shuttle_Arc_Radius - 2.5, 0, 0]), theta_deg))
    for s in (-1, 1):
        for theta_deg in np.arange(5.0, 25.0 + 1e-9, 5.0):
            parts.append(sp.rotate_z(sp.translate(_rod2(rib_h), [Shuttle_Arc_Radius - 5.0, 0, 0]), s * theta_deg))
        for theta_deg in np.arange(3.0, 15.0 + 1e-9, 6.0):
            parts.append(sp.rotate_z(sp.translate(_rod2(rib_h), [Shuttle_Arc_Radius - 7.5, 0, 0]), s * theta_deg))

    # Under Rib - Outer/Radius/Center (v2:894-919) - the only tiers that
    # actually depend on the outer loop's y (via theta/s), so these stay
    # in the loop.
    for s in (-1, 1):
        theta = 0.0
        while theta <= thetamax / 2.0 + 1e-9:
            y = (Shuttle_Arc_Radius - 1) * np.cos(np.pi / 2.0 + theta * s)
            ay = abs(y)
            if Cp_1_X < ay <= Inner_Arc_Intercept:
                x = np.sqrt(max((Shuttle_Arc_Radius - Shuttle_Rib_Width) ** 2 - y ** 2, 0.0))
                parts.append(sp.translate(_rod2(rib_h), [x, y, 0]))
            elif Cp_2_X < ay <= Cp_1_X:
                x = np.sqrt(max(Shuttle_Rib_Circle_Radius ** 2 - (ay - X_Prime) ** 2, 0.0)) + Y_Prime
                parts.append(sp.translate(_rod2(rib_h), [x, y, 0]))
            elif ay <= Cp_2_X:
                x = Shuttle_Rib_Circle_Offset - np.sqrt(max(Shuttle_Rib_Circle ** 2 - y ** 2, 0.0)) + z
                parts.append(sp.translate(_rod2(rib_h), [x, y, 0]))
            theta += thetaspacing

    # NOTE: does NOT apply v2's own translate([-Z_Offset,0,0]) (v2:866) -
    # left to the caller (ResinPrint()), which applies the same shift to
    # the body+support union as a whole, matching HorizGroovedResinSupport()'s
    # convention for consistency (both real v2 functions DO each wrap
    # themselves in that translate independently, but the net effect on
    # the final union is identical either way, since translate is linear).
    return sp.union_all(parts)


def ResinSupport():
    """Faithful port of v2's VertResinSupport2() (v2:609-735) - only used
    for the "vertical" print orientation (v2's own real, matching
    orientation). After repeated feedback that a from-scratch grid+
    raycast redesign didn't match v2's real connecting-rod placement,
    this reproduces v2's actual tiers, coordinates, and ConnectingRod/
    ResinRod call sites directly, rather than re-deriving placement from
    the built mesh's own surface.

    Rod SHAPE reuses cylinder_machine._resin_rod() (the shared primitive
    Mignon/Bennett also reuse) in place of v2's own bespoke ResinRod
    (h1,r1,r2,h2,r3) - r1/r3 always match the shared primitive's
    Resin_Rod_OD/2 and Resin_Raft_OD/2 anyway; r2 (tip diameter) is
    simplified to the single configured Resin_Tip_OD rather than v2's
    two-tier Resin_Support_Contact_Diameter/_Rib distinction - a minor,
    explicitly-accepted simplification (this is NOT the thing reported as
    wrong). ConnectingRod is resin_support.connecting_rod() (v2:419,
    ported literally as a hull of two spheres).

    Coordinate frame: v2 wraps the WHOLE union in
    translate([0,0,-Resin_Support_Min_Height-Resin_Support_Base_Thickness])
    (v2:611) - reproduced by computing every point/height exactly as v2
    writes it (its own pre-shift convention: ResinRod's raft sits at
    z=0, tip at z=h1) and re-basing per-primitive: _rod() subtracts
    (Resin_Min_Rod_Height+Resin_Raft_Thickness) from h1 before calling
    cylinder_machine._resin_rod (whose own raft-at-that-same-negative-z
    convention already IS that shift); _crod() subtracts it explicitly
    from each endpoint's z. Must be added directly alongside the ALREADY
    print-oriented body with no further transform (see ResinPrint()),
    matching v2's own VertResinPrint2 - RibbedShuttle() and
    VertResinSupport2() are siblings in one union(), not nested."""
    _require_configured()
    # v2:611 wraps the whole VertResinSupport2 union in translate([0,0,
    # -Resin_Support_Min_Height-Resin_Support_Base_Thickness]) - shift is
    # that same rebasing constant, shared by all three resin_support.py
    # placement helpers below (vertical_rod/vertical_connecting_rod/
    # rod_tip) so they stay in one consistent coordinate frame. All the
    # actual shape-building AND placement/rotation logic for these three
    # lives in lib/resin_support.py now (see each function's own
    # docstring there) - this function only supplies Hammond's own
    # config values and the per-part coordinates.
    shift = Resin_Min_Rod_Height + Resin_Raft_Thickness

    def _rod(h1, add_raft=True):
        # NOT clamped - an earlier floor here (max(h, -Resin_Raft_
        # Thickness+0.05)) was reported as a broken/misaligned rod ("the
        # base is missing"). Checked the real math: every constant h1 in
        # this function (including the smallest, h_edge2=Resin_Raft_
        # Thickness giving h=-Resin_Min_Rod_Height=-2.0 with default
        # values) stays well above the actual degenerate threshold (where
        # the tip sphere would invert past the base sphere, around -2.58
        # with default values - see resin_support.resin_rod's tip_z/
        # lower_z formulas) - the floor was clamping an already-VALID
        # value to the wrong height for no reason, not preventing a real
        # defect. v2 itself has no such guard on ResinRod() either.
        return resin_support.vertical_rod(h1, shift, Resin_Tip_OD, Resin_Tip_L, Resin_Rod_OD,
                                           Resin_Inset, Resin_Min_Rod_Height, Resin_Raft_Thickness,
                                           Resin_Raft_OD, add_raft=add_raft, resin_fn=Resin_Fn)

    def _crod(p1, p2):
        return resin_support.vertical_connecting_rod(p1, p2, Resin_Rod_OD, shift)

    def _rod_tip(x, theta_deg, s):
        # Missing this shape entirely was the reported bug ("the theta of
        # the tip") - see resin_support.rod_tip()'s docstring for the
        # full v2 source derivation and coordinate-frame explanation, and
        # for why its placement is NOT pushed by any extra offset here -
        # this needle's (x,theta) position must stay aligned with the
        # separate _rod()/_crod() pair placed at the same (x,theta) below.
        return resin_support.rod_tip(x, theta_deg, s, Z_Offset, Shuttle_Arc_Radius,
                                      Resin_Rod_OD, Resin_Tip_OD, sections=Cyl_Fn)

    parts = []

    # Xx/Xxx (v2:602-607)
    if not Is_Math:
        Xx = [-X_Min + Resin_Tip_OD / 2.0, -X_Min * 2 / 3.0, -X_Min / 3.0,
              X_Max / 3.0, X_Max * 2 / 3.0, X_Max - Resin_Tip_OD / 2.0]
        Xxx = 3.0
    else:
        Xx = [-X_Min + Resin_Tip_OD / 2.0, -X_Min * 2 / 3.0, -X_Min / 3.0,
              X_Max / 4.0, X_Max * 2 / 4.0, X_Max * 3 / 4.0, X_Max - Resin_Tip_OD / 2.0]
        Xxx = 4.0

    thetamax = np.radians(Angle_Pitch * 32.0) - 2.0 * np.radians(Shuttle_Taper)
    thetaspacing = Resin_Support_Spacing / Shuttle_Arc_Radius  # radians (arc-length/radius)
    n_theta_steps = max(1, int(np.floor((thetamax / 2.0) / thetaspacing + 1e-9)))
    thetas = [i * thetaspacing for i in range(n_theta_steps + 1)]

    # ---- Under Large Arc (v2:613-689) ----
    for s in (-1, 1):
        for x in Xx:
            # at the taper (v2:631-638) - constant per (s,x), doesn't
            # depend on theta despite living inside v2's theta loop
            # (harmless duplication there since union() merges overlaps;
            # built once here instead).
            theta_t = thetamax / 2.0
            y1 = (Shuttle_Arc_Radius - 1) * np.cos(np.pi / 2.0 + theta_t * s)
            z1 = (Shuttle_Arc_Radius - 1) * np.sin(np.pi / 2.0 + theta_t * s)
            p_a = [x, y1, z1 - Z_Offset + Resin_Raft_Thickness + Resin_Min_Rod_Height]
            p_b = [x, y1 - 0.5 * (-s), Resin_Rod_OD]
            parts.append(_crod(p_a, p_b))
            parts.append(_rod_tip(x, np.degrees(theta_t), s))

            for theta in thetas:
                # theta==0's y/za/rotation are all exactly s-independent
                # (0*s==0 for either sign) - s=-1 and s=+1 build IDENTICAL
                # parts here across every sub-tier below (Under Shuttle
                # Arc Radius/ConRods/Rib Supports all keyed off the same
                # s-independent y). v2's own nested s/theta loop has this
                # same exact duplication (union() silently no-ops on the
                # coincident geometry there); skipping the redundant pass
                # here is a pure performance fix - the s=1 pass alone
                # already produces this iteration's geometry, so this
                # doesn't change the built shape at all, just the part
                # count feeding the boolean union (confirmed: this was
                # the "redundancy" flagged when investigating why the
                # vertical build's part count looked excessive).
                if s == -1 and theta == 0.0:
                    continue
                y = (Shuttle_Arc_Radius - 1) * np.cos(np.pi / 2.0 + theta * s)
                za = (Shuttle_Arc_Radius - 1) * np.sin(np.pi / 2.0 + theta * s)
                z_common = za - Z_Offset + Resin_Raft_Thickness + Resin_Min_Rod_Height

                # Under Shuttle Arc Radius (v2:619-630)
                parts.append(_rod_tip(x, np.degrees(theta), s))
                parts.append(_crod([x, y, z_common], [x, y, Resin_Rod_OD]))
                parts.append(sp.translate(_rod(Resin_Min_Rod_Height), [x, y, 0]))

                # Under Shuttle Arc ConRods (v2:640-660)
                if abs(y) <= Taper_Inset_Y - Resin_Support_Spacing:
                    for n in (0, 1):
                        xa = [-X_Min * 2 / 3.0, X_Max * (2.0 if not Is_Math else 3.0) / Xxx][n]
                        xb = [-(X_Min - Resin_Tip_OD / 2.0), X_Max - Resin_Tip_OD / 2.0][n]
                        parts.append(_crod([xa, y, z_common - 2], [xb, y, z_common - 2 - 3]))

                        xc = [-X_Min / 3.0, X_Max * 1 / Xxx][n]
                        xd = [-X_Min * 2 / 3.0, X_Max * 2 / Xxx][n]
                        parts.append(_crod([xc, y, z_common - 2], [xd, y, z_common - 2 - 3]))

                        if Is_Math:
                            xe = [-X_Min / 3.0, X_Max * 2 / Xxx][n]
                            xf = [-X_Min * 2 / 3.0, X_Max * 3 / Xxx][n]
                            parts.append(_crod([xe, y, z_common - 2], [xf, y, z_common - 2 - 3]))

                # Under Rib Supports (v2:662-686)
                if not Groove:
                    ay = abs(y)
                    if Cp_2_X < ay <= Cp_1_X:
                        h = np.sqrt(max(Shuttle_Rib_Circle_Radius ** 2 - (ay - X_Prime) ** 2, 0.0)) \
                            + Y_Prime - Z_Offset + Resin_Min_Rod_Height + Resin_Raft_Thickness
                        parts.append(sp.translate(_rod(h), [0, y, 0]))
                        if h - 1 >= 3 + Resin_Raft_Thickness + Resin_Min_Rod_Height:
                            for n in (-X_Min / 3.0, X_Max / Xxx):
                                parts.append(_crod([0, y, h - 1], [n, y, h - 4]))
                    if ay <= Cp_2_X:
                        d = Shuttle_Rib_Circle_Offset - Z_Offset + Resin_Min_Rod_Height + Resin_Raft_Thickness
                        h = d - np.sqrt(max(Shuttle_Rib_Circle ** 2 - y ** 2, 0.0)) + z
                        parts.append(sp.translate(_rod(h), [0, y, 0]))
                        if h - 1 >= 3 + Resin_Raft_Thickness + Resin_Min_Rod_Height:
                            for n in (-X_Min / 3.0, X_Max / Xxx):
                                parts.append(_crod([0, y, h - 1], [n, y, h - 4]))

    # ---- Under Rib - Rib Thickness on Edges (v2:691-711) ----
    half_ang_rad2 = np.radians(90.0 - Angle_Pitch * 16.0)
    y_component_taper = (Shuttle_Arc_Radius + Shuttle_Taper_Step) * np.cos(half_ang_rad2)
    z_component = Shuttle_Taper_Step * np.sin(half_ang_rad2)

    if not Groove:
        h1 = Resin_Min_Rod_Height + Resin_Raft_Thickness
        # v2:704,710 pass h2=0 (no raft) for the two Inner_Arc_Intercept
        # rods here - reported as "a single resin rod on either side is
        # missing the raft to the buildplate, that shouldn't happen."
        # Every resin rod needs its own real connection to the buildplate
        # to be printable at all, so this is always add_raft=True now,
        # not a faithful port of v2's h2=0 - a deliberate correction, not
        # a port artifact.
        parts.append(sp.translate(_rod(h1, add_raft=True),
                                   [0, -Outer_Arc_Intercept + Resin_Support_Edge_Gap, 0]))
        parts.append(sp.translate(_rod(h1, add_raft=True),
                                   [0, -Inner_Arc_Intercept - Resin_Support_Edge_Gap, 0]))
        parts.append(sp.translate(_rod(h1, add_raft=True),
                                   [0, Outer_Arc_Intercept - Resin_Support_Edge_Gap, 0]))
        parts.append(sp.translate(_rod(h1, add_raft=True),
                                   [0, Inner_Arc_Intercept + Resin_Support_Edge_Gap, 0]))

    # ---- Outer Edge Supports (v2:713-732) - regardless of Groove ----
    # Same correction as above - v2:716,721 pass h2=0 for this first pair
    # of loops; always add_raft=True here too, every rod gets a real raft.
    h_edge1 = Resin_Min_Rod_Height + z_component + Resin_Raft_Thickness
    h_edge2 = Resin_Raft_Thickness
    for x in Xx:
        parts.append(sp.translate(_rod(h_edge1, add_raft=True), [x, y_component_taper, 0]))
    for x in Xx:
        parts.append(sp.translate(_rod(h_edge1, add_raft=True), [x, -y_component_taper, 0]))
    for x in Xx:
        parts.append(sp.translate(_rod(h_edge2, add_raft=True), [x, y_component_taper, 0]))
    for x in Xx:
        parts.append(sp.translate(_rod(h_edge2, add_raft=True), [x, -y_component_taper, 0]))

    print(f"ResinSupport: {len(parts)} parts (v2-faithful VertResinSupport2 port)", flush=True)
    return sp.union_all(parts)


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None, align_kwargs=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None, minkowski_enabled=None,
               draft_angle_deg=None):
    """v2:1060-1073's real ResinPrint() dispatcher:

        if (Resin_Support){
            if (Resin_Support_Orientation==0) VertResinPrint2();
            if (Resin_Support_Orientation==1) HorizGroovedResin3();
        }
        if (!Resin_Support){
            if (Groove) GroovedShuttle();
            if (!Groove) RibbedShuttle();
        }

    When resin support is OFF, v2 returns the plain body for EITHER
    orientation - no VertResinPrint2/HorizGroovedResin3 reorientation
    happens at all (both only exist to add print-orientation supports).
    Reproduced as a bare FullElement() (respecting Groove, unrotated).

    "vertical" (Resin_Support_Orientation==0) - v2:811-822
    VertResinPrint2's real orientation: rotate([0,-90,0]) then
    translate(-Z_Offset,0,-X_Max), respecting Groove (RibbedShuttle or
    GroovedShuttle), with ResinSupport() (a faithful VertResinSupport2
    port) added as a sibling in the same union - both rely on the same
    real Z_Offset/X_Max constants to land in the right place relative to
    each other, no extra normalization step exists in v2 or here.

    "horizontal" (Resin_Support_Orientation==1) - v2 actually has TWO real
    horizontal-print functions, HorizGroovedResin3 (v2:1006-1021) and
    HorizResinPrint2 (v2:952-963). Both apply the same flip transform
    (rotate([180,0,0]) then translate(0,0,-Shuttle_Height) - proven
    algebraically equivalent to v2:952-957's reversed-order translate/
    rotate for HorizResinPrint2) to whatever body Groove/element.groove
    (the Build tab's Rib checkbox, inverted) already selected -
    GroovedShuttle() or RibbedShuttle(), same as FullElement() always
    builds. What used to be forced 1:1 with that same Groove flag is
    just the OUTER-WALL support scheme, now resin.horizontal_method
    (v4-specific, independent selector - not itself a v2 customizer
    field, see config/hammond.yaml's comment) instead:

    - horizontal_method="cut_groove": HorizGroovedResinSupport() - v2's
      real HorizGroovedResin3 support, a swept perforated breakaway-
      groove ring (v2's real "Cut Groove" support) hugging the outer
      wall band only (r0..r0+Shuttle_Thickness) - never touches the rib
      feature either way.
    - horizontal_method="resin_rod": HorizWallRodSupport() - the outer-
      wall tier of v2's real HorizResinPrint2/HorizResinSupport2 rod
      scheme (v2:868-884), covering that same wall band with individual
      rods instead of a ring.

    Independent of Groove because the ring/wall-rod choice above never
    interacts with the rib feature - but whenever the body actually HAS
    a rib (Groove=false), the rib's own back/bottom plane and the
    square drive-pin hole (v2:886-946) still always need their own
    resin-rod supports regardless of horizontal_method - there's no
    cut-groove equivalent for that geometry (HorizGroovedResinSupport's
    ring doesn't reach it) - so HorizRibResinSupport() (the rest of the
    original HorizResinSupport2 port) is added unconditionally whenever
    Groove is false. An earlier version of this port forced
    GroovedShuttle()/the ring unconditionally for ALL of "horizontal",
    misreading HorizGroovedResin3 as the only real option; corrected
    after the user pointed out the ribbed body can print horizontally
    too, if properly supported - then, once the ribbed-body case was
    ported as a real Groove-coupled dispatch, further split so the wall
    method (ring vs rod) is a genuinely independent choice from the
    body/rib-support question, per explicit user request (the two
    "groove" concepts - the body's snap-fit assembly groove and the
    resin support's cut-breakaway groove - were sharing one confusing
    name/dispatch flag with no way to combine them).

    Whole assembly (body+support) gets one final translate(-Z_Offset,0,0),
    matching v2's own outer wrapper (present in both real functions, just
    also independently duplicated inside HorizResinSupport2 itself in v2 -
    applying it once to the union has the same net effect)."""
    if not Resin_Support:
        full, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                        cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
                                        platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                        draft_angle_deg=draft_angle_deg)
        combined, _, _, _ = sp.check_and_repair(full, label="ResinPrint")
        return combined, char_parts

    if Resin_Support_Orientation == "horizontal":
        full_body, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                             cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
                                             platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                             draft_angle_deg=draft_angle_deg)
        body = sp.scad_transform(full_body, ("rotate", [180, 0, 0]), ("translate", [0, 0, -Shuttle_Height]))
        if Horizontal_Support_Method == "cut_groove":
            support_parts = [HorizGroovedResinSupport()]
            label = "HorizGroovedResinSupport"
        else:
            support_parts = [HorizWallRodSupport()]
            label = "HorizWallRodSupport"
        if not Groove:
            # Rib is present - always needs its own resin-rod supports
            # regardless of Horizontal_Support_Method, see ResinPrint()'s
            # docstring.
            support_parts.append(HorizRibResinSupport())
            label += "+HorizRibResinSupport"
        support = sp.union_all(support_parts)
        print(f"{label}: verts={len(support.vertices)} faces={len(support.faces)} "
              f"watertight={support.is_watertight}", flush=True)
        combined = sp.translate(sp.union_all([body, support]), [-Z_Offset, 0, 0])
        combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
        return combined, char_parts

    full, char_parts = FullElement(points_per_mm, separation_mm, render_core_groove, align_kwargs,
                                    cone_segments=cone_segments, simplify_tolerance_mm=simplify_tolerance_mm,
                                    platen_fn=platen_fn, minkowski_enabled=minkowski_enabled,
                                    draft_angle_deg=draft_angle_deg)
    oriented = sp.scad_transform(full, ("rotate", [0, -90, 0]), ("translate", [-Z_Offset, 0, -X_Max]))
    combined = sp.union_all([oriented, ResinSupport()])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts
