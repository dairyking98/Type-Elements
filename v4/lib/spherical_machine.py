"""
Shared spherical-typeball-family code (Selectric I/II, Selectric Composer,
Selectric III) - the analogue of lib/cylinder_machine.py for this physical
form factor, per CLAUDE.md's "Porting a new machine" taxonomy (IBM/
Selectric is a different form factor from the cylinder family, sharing
nothing with cylinder_machine.py - verified function-by-function against
v2/ibm.scad + v2/lib/layouts/ibm_layouts.scad, not assumed).

v2/ibm.scad models Composer/Selectric I-II/Selectric III as ONE file
indexed by Render_Mode (0/1/2) into parallel arrays - not three separate
designs. This module holds everything that's byte-identical across all
three modes there (FullBody/SolidCleanup/Teeth/Notch/the character-glyph
pipeline/labels/resin supports); the 3 real per-mode divergences
(character/hemisphere layout data, font-size convention, type-test
rendering) live one-per-machine in lib/selectric12.py / lib/
selectric_composer.py / lib/selectric3.py, dynamically dispatched via
_receive_config() exactly like cylinder_machine.py's own mechanism (see
that module's docstring for the general scheme - safe here for the same
reason: generate.py configures exactly one machine per process).

Character-embedding order is NOT the same as glyph_poc.build_glyph()'s
(draft-in-local-space, then place-on-cylinder): v2's SingleMinkowski
POSITIONS the character in world coordinates FIRST (PositionText's real
rotate/translate to its sphere longitude/latitude), THEN Minkowski-sums
with a draft cone built at the ORIGIN (only rotated, never translated).
This is still correct: a Minkowski sum with a small compact shape B is a
purely LOCAL dilation of A by B's own point-set, regardless of where B's
centroid sits in world space - B's points are literally the offset
vectors added to every point of A. Verified by hand against v2's exact
transform stack (rotate/translate order) before writing this, not
assumed compatible with build_glyph's own (different) construction -
build_glyph's cylinder-family-specific PlatenCutout model does NOT
directly generalize to the sphere's PlatenCutout (different transform
composition - PlatenCutout here is built via its OWN rotate/translate
stack sharing longitude/latitude with the character, not expressed
relative to the character's local frame the way build_glyph assumes), so
this module reimplements Text()/PositionText()/PlatenCutout()/
SingleMinkowski() as a direct, literal port instead of reusing build_glyph.

Not yet ported (all default OFF/0 in v2, so this doesn't change default
behavior - explicit callouts per CLAUDE.md's "say so, don't silently
diverge" convention): Font_Weight_Offset/X_Weight_Adjustment/
Y_Weight_Adjustment (Text()'s 2D minkowski-with-square weight adjustment),
Mink_Flat (a debug duplicate flat-preview copy), Rays()/Selective_Render
(dev-only visualization), Drain (the "[Experimental Drain Holes]"
feature), ConsoleCutout()'s echo (Cutout_Test/Draft_Angle_Test/
Mink_Long_Offset_Test/Platen_Diameter_Test console diagnostics - the
underlying per-row Platen_Longitude_Offsets/Minkowski_Longitudinal_Offsets/
Baseline_Longitude_Offsets tuning ARE ported, just not the sweep-test
console output), CalibrationElement/CalibrationAdditive (deferred to a
follow-up pass).
"""

import time

import numpy as np
import trimesh
import freetype
from manifold3d import Manifold, Mesh as ManifoldMesh

from glyph_poc import get_glyph_contours_and_advance, classify_and_triangulate, alignment_x_offset
import scad_primitives as sp
import resin_support
import build_log

_active_machine = None


def _receive_config(source_globals, machine_name):
    global _active_machine
    if _active_machine not in (None, machine_name):
        raise RuntimeError(
            f"spherical_machine already configured for {_active_machine!r}; "
            f"cannot reconfigure for {machine_name!r} in the same process")
    _active_machine = machine_name
    globals().update({k: v for k, v in source_globals.items() if k[:1].isupper() or k == "z"})


def _require_configured():
    if _active_machine is None:
        raise RuntimeError("call <machine>.configure(config_path) before using this module")


def _to_manifold(mesh):
    return Manifold(mesh=ManifoldMesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32)))


def _from_manifold(manifold):
    m = manifold.to_mesh()
    return trimesh.Trimesh(vertices=m.vert_properties, faces=m.tri_verts, process=False)


# --------------------------------------------------------------- Body/Sphere

def FullBody(points_per_mm=None, minkowski_enabled=None, draft_angle_deg=None):
    """FullBody() (v2/ibm.scad:486-494): union(sphere, skirt frustum,
    AssembleMinkowski())."""
    _require_configured()
    ball = trimesh.creation.icosphere(subdivisions=4, radius=Sphere_OD / 2.0)
    skirt = sp.frustum_z(Skirt_Bottom_OD, Skirt_Top_OD, Floor - Center_To_Skirt,
                          sections=Surface_Fn, base_z=-Floor)
    ring = AssembleMinkowski(points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled,
                              draft_angle_deg=draft_angle_deg)
    return sp.union_all([ball, skirt, ring])


# ------------------------------------------------------- Character embedding

def _text2d_contours(char, font_path, font_size_mm, points_per_mm, halign,
                      x_pos_offset, y_pos_offset, custom_h_offset, custom_v_offset):
    """Text() (v2/ibm.scad:497-507) - 2D glyph outline in mm, with v2's
    exact halign -> mirror -> translate order (NOT build_glyph's own
    shift-then-mirror convention - see module docstring). Weight
    adjustment (Font_Weight_Offset/X_Weight_Adjustment/Y_Weight_Adjustment)
    not implemented - see module docstring."""
    face = freetype.Face(font_path)
    scale = font_size_mm / face.units_per_EM
    contours_font_units, advance_mm = get_glyph_contours_and_advance(
        char, points_per_mm, scale, font_path=font_path)
    contours_mm = [c * scale for c in contours_font_units]
    # OpenSCAD text()'s own halign, applied INSIDE text() before Text()'s
    # mirror/translate wrapper - alignment_x_offset with no extra
    # offset params reproduces exactly this (center: -advance/2, left: 0).
    halign_shift = alignment_x_offset(char, advance_mm, mode=halign)
    contours_mm = [c + np.array([halign_shift, 0.0]) for c in contours_mm]
    # mirror([1, 0, 0])
    contours_mm = [c * np.array([-1.0, 1.0]) for c in contours_mm]
    # translate([X_Pos_Offset-customhalign, Y_Pos_Offset+customvalign, 0])
    contours_mm = [c + np.array([x_pos_offset - custom_h_offset, y_pos_offset + custom_v_offset])
                   for c in contours_mm]
    return contours_mm


def SingleMinkowskiChar(char, longitude, latitude, plat_offset, base_offset,
                        minklongoffset, draft_angle, platendia, font_path, font_size_mm,
                        custom_h_offset=0.0, custom_v_offset=0.0,
                        points_per_mm=None, minkowski_enabled=None):
    """SingleMinkowski() (v2/ibm.scad:553-587) - one struck character:
    build the 2D glyph, extrude to a flat block, carve the platen scallop
    (a real cylinder, matching PlatenCutout()'s own construction exactly -
    NOT build_glyph's cylinder-family model, see module docstring), then
    Minkowski-sum with a draft cone. Mink_Flat's extra flat-preview copy
    is not ported (debug-only, defaults off)."""
    _require_configured()
    points_per_mm = DEFAULT_POINTS_PER_MM if points_per_mm is None else points_per_mm
    minkowski_enabled = DEFAULT_MINKOWSKI_ENABLED if minkowski_enabled is None else minkowski_enabled
    contours_mm = _text2d_contours(char, font_path, font_size_mm, points_per_mm,
                                    H_Alignment, X_Pos_Offset, Y_Pos_Offset,
                                    custom_h_offset, custom_v_offset)
    flat = classify_and_triangulate(contours_mm)
    if flat is None:
        return None  # matches v2 rendering an empty/invisible character (e.g. space)

    prism = trimesh.creation.extrude_triangulation(flat.vertices[:, :2], flat.faces,
                                                    Character_Block_Height_Mm)

    # PositionText(longitude, latitude+base_offset): rotate([90-latitude,0,
    # 90+longitude]); translate([0,0,Sphere_R+z]) - source top-to-bottom
    # order, matching sp.scad_transform's documented convention.
    eff_latitude = latitude + base_offset
    positioned = sp.scad_transform(
        prism,
        ("rotate", [90 - eff_latitude, 0, 90 + longitude]),
        ("translate", [0, 0, Sphere_R + z]),
    )

    # PlatenCutout(longitude, latitude+plat_offset, platendia)
    # (v2/ibm.scad:510-516) - built via its OWN transform stack (source
    # top-to-bottom: rotate([0,-latitude,longitude]); translate([Sphere_R+
    # platenr+Type_Altitude,0,0]); rotate([90,0,0])), sharing the SAME
    # longitude/latitude+plat_offset as the character above but NOT
    # expressed relative to the character's own local frame.
    platenr = platendia / 2.0
    cutter = trimesh.creation.cylinder(radius=platenr, height=10.0, sections=Cyl_Fn)
    eff_plat_latitude = latitude + plat_offset
    cutter = sp.scad_transform(
        cutter,
        ("rotate", [0, -eff_plat_latitude, longitude]),
        ("translate", [Sphere_R + platenr + Type_Altitude, 0, 0]),
        ("rotate", [90, 0, 0]),
    )
    scalloped = positioned.difference(cutter, engine="manifold")

    if not minkowski_enabled:
        return scalloped

    # Minkowski draft cone(s), built at the ORIGIN (rotated only, never
    # translated) - see module docstring for why this is still a correct
    # local dilation of the already-positioned `scalloped` solid. Uses
    # v2's own MINK_TEXT_R(draft_angle)=2*tan(.5*draft_angle) formula - a
    # FIXED-height (Mink_Cone_Height_Mm) cone, unlike build_glyph's
    # separation_mm-scaled cone - a real, intentional difference in the
    # v2 source (see spherical_machine's module docstring), not something
    # to reconcile with the cylinder family's formula.
    mink_r = 2.0 * np.tan(np.radians(draft_angle / 2.0))
    cone1 = Manifold.cylinder(Mink_Cone_Height_Mm, mink_r, 0.0, circular_segments=Mink_Fn)
    cone1 = cone1.translate([0, 0, -Mink_Cone_Height_Mm])
    if minklongoffset != 0:
        cone2 = cone1.rotate([-minklongoffset, 0, 0])
        cone_hull = trimesh.util.concatenate(
            [_from_manifold(cone1), _from_manifold(cone2)]).convex_hull
    else:
        cone_hull = _from_manifold(cone1)
    # rotate([90-latitude,0,90+longitude]) - the SAME rotation PositionText
    # used, but on the RAW latitude (no base_offset) - matches v2 exactly,
    # not "fixed" to match the character's own base_offset-adjusted latitude.
    cone_hull = sp.scad_transform(cone_hull, ("rotate", [90 - latitude, 0, 90 + longitude]))

    drafted = _to_manifold(scalloped).minkowski_sum(_to_manifold(cone_hull))
    return _from_manifold(drafted)


def AssembleMinkowski(points_per_mm=None, minkowski_enabled=None, draft_angle_deg=None):
    """AssembleMinkowski() (v2/ibm.scad:618-655) - places every character
    of both cases (lowercase=0, uppercase=1, 180 degrees apart) at its
    real hemisphere position. LONGITUDE_LATITUDE/CASES88 are supplied by
    the calling machine module's configure() (CASES88_LOWER/CASES88_UPPER/
    LONGITUDE_LATITUDE globals) - see lib/layouts/selectric12_layout.py
    for how these are derived. Selective_Render/Rays not ported (dev-only,
    default off - see module docstring).

    Its own from-scratch per-character loop (this module doesn't reuse
    cylinder_machine.TextRing - see module docstring), so it doesn't get
    build_log's "[n/total]" progress instrumentation for free the way
    Blickensderfer/Postal/Mignon/Bennett/Helios/Hammond do; wired by hand
    here per CLAUDE.md's "Keep doing this" convention, matching
    hammond_split.TextAssemble()'s template exactly (per-character
    progress_start/done/skipped, skip-on-exception instead of aborting
    the whole build)."""
    _require_configured()
    draft_angle_deg = Mink_Draft_Angle if draft_angle_deg is None else draft_angle_deg
    parts = []
    skipped = []
    total = 2 * len(LONGITUDE_LATITUDE)
    n = 0
    t_start = time.perf_counter()
    for case_int in (0, 1):
        case_str = CASES88_LOWER if case_int == 0 else CASES88_UPPER
        for longitude_col, latitude_row, _kb_char, kb_index in LONGITUDE_LATITUDE:
            n += 1
            char = case_str[kb_index]
            longitude = longitude_col * Longitude_Step + case_int * 180
            latitude = Row_Latitudes[latitude_row]
            plat_offset = Platen_Longitude_Offsets[latitude_row]
            base_offset = Baseline_Longitude_Offsets[latitude_row]
            minklongoffset = Minkowski_Longitudinal_Offsets[latitude_row]
            font_path = FONT2_PATH if char in Font2_Chars else FONT_PATH
            font_size = Font2_Size if char in Font2_Chars else Font_Size
            custom_h = CUSTOMHALIGNOFFSET if char in CUSTOMHALIGNCHARS else 0.0
            custom_v = CUSTOMVALIGNOFFSET if char in CUSTOMVALIGNCHARS else 0.0
            build_log.progress_start("AssembleMinkowski", n, total,
                                      f"building {char!r} (case={case_int})")
            t0 = time.perf_counter()
            try:
                mesh = SingleMinkowskiChar(char, longitude, latitude, plat_offset, base_offset,
                                           minklongoffset, draft_angle_deg, Platen_OD,
                                           font_path, font_size, custom_h, custom_v,
                                           points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled)
            except Exception as e:
                skipped.append((case_int, char, str(e)))
                build_log.progress_skipped(e)
                continue
            build_log.progress_done(time.perf_counter() - t0)
            if mesh is not None:
                parts.append(mesh)
    build_log.progress_summary("AssembleMinkowski", len(parts), skipped,
                                time.perf_counter() - t_start)
    return sp.union_all(parts)


# -------------------------------------------------------------- Subtractive

def HollowProfile3():
    """HollowProfile3() (v2/ibm.scad:692-708) - a hull() of 3 circles plus
    a square, unioned with a second plain square, revolved. Built as a
    real shapely hull (matching WireBite()'s pattern in
    cylinder_machine.py) rather than a hand-derived polygon, then
    converted to a rotate_extrude profile."""
    from shapely.geometry import Point, box as shapely_box
    from shapely.ops import unary_union
    newroofr = 1.0
    c1 = Point(-newroofr + Inside_R, Boss_To_Center + Boss_Clearance).buffer(newroofr, resolution=32)
    # v2: translate([Boss_R+Boss_Step,0,0]) square([Inside_R-Boss_R-Boss_Step, 1])
    # - a wide, short rectangle from x=Boss_R+Boss_Step to x=Inside_R at
    # y=[0,1] - NOT a 1x(Boss_To_Center+Boss_Clearance) strip (an earlier,
    # wrong transcription of this hull component - fixed after it produced
    # a visibly malformed hollow-cavity wall).
    sq = shapely_box(Boss_R + Boss_Step, 0, Inside_R, 1.0)
    c2 = Point(Boss_R + newroofr + Boss_Step, Boss_To_Center + Boss_Clearance).buffer(newroofr, resolution=32)
    c3 = Point((Inside_R + Boss_R + Boss_Step) / 2,
               Top_Flat_To_Center - Top_Flat_Thickness - newroofr).buffer(newroofr, resolution=32)
    hull_poly = unary_union([c1, sq, c2, c3]).convex_hull
    extra_sq = shapely_box(Boss_R, 0, Boss_R + Boss_Step + z, Boss_To_Center + Boss_Clearance)
    profile_poly = unary_union([hull_poly, extra_sq])
    # rotate_extrude(polygon) sweeps X=radius, Y=Z - extract the exterior
    # ring as an (r, z) point loop for sp.revolve_polygon.
    coords = list(profile_poly.exterior.coords)
    return sp.revolve_polygon(coords, sections=Surface_Fn)


def Tooth():
    """Tooth() (v2/ibm.scad:715-724) - detent tooth profile, scaled in Y
    by Chars_Per_Row_S12/Chars_Per_Row (1.0 for Selectric I/II itself -
    the scale exists so this SAME profile narrows correctly for a machine
    with more teeth per row, e.g. Selectric III's 24)."""
    from shapely.geometry import Polygon as ShapelyPolygon
    scale_y = Chars_Per_Row_Reference / Chars_Per_Row
    poly = np.array([[0, 1.9], [2.2, 0.4], [3.2, 0.14], [3.2, -0.14], [2.2, -0.4], [0, -1.9]])
    mesh = trimesh.creation.extrude_polygon(ShapelyPolygon(poly), 30.0)
    mesh.vertices[:, 1] *= scale_y
    # translate([0,Detent_Valley_To_Center,-Floor-z]) rotate([180,-90,0])
    return sp.scad_transform(
        mesh,
        ("translate", [0, Detent_Valley_To_Center, -Floor - z]),
        ("rotate", [180, -90, 0]),
    )


def Teeth():
    """Teeth() (v2/ibm.scad:728-732) - one Tooth() per character index
    position around the ring."""
    parts = [sp.rotate_z(Tooth(), i * Longitude_Step) for i in range(Chars_Per_Row)]
    return sp.union_all(parts)


def Notch():
    """Notch() (v2/ibm.scad:735-739) - the drive notch cube."""
    box = trimesh.creation.box(extents=[4.0, Drive_Notch_Width, Drive_Notch_Height + Snoot_Droop_Compensation + z])
    box = sp.translate(box, [Shaft_ID / 2 - 0.5 + 2.0, 0, Boss_To_Center - z + (Drive_Notch_Height + Snoot_Droop_Compensation + z) / 2])
    return sp.rotate_z(box, Drive_Notch_Theta)


def Del():
    """Del() (v2/ibm.scad:964-970) - the alignment-marker triangle
    engraved into the top face. Color dropped (v4 has no color concept -
    engraving is done via boolean subtraction, not appearance)."""
    from shapely.geometry import Polygon as ShapelyPolygon
    poly = ShapelyPolygon([[3.4, 0], [0.4, 1.3], [0.4, -1.3]])
    mesh = trimesh.creation.extrude_polygon(poly, Del_Depth + z)
    return sp.translate(mesh, [Del_Base_From_Centre, 0, Top_Flat_To_Center - Del_Depth])


def Labels():
    """Labels() (v2/ibm.scad:984-996) - the number label (disabled for
    Composer - Render_Mode!=0 in v2; Selectric I/II and III both always
    show it, see Labels_Show_Number below, set true by both) plus the
    typeface label."""
    from glyph_poc import build_flat_text
    parts = []
    if Labels_Show_Number:
        no_font = Label_No_Font_Override or FONT_PATH
        # v2 renders the whole Label_No STRING; build_flat_text is per-char -
        # concatenate left-to-right at natural FreeType advance, same
        # convention as cylinder_machine.build_text_string.
        cursor = 0.0
        no_parts = []
        face = freetype.Face(no_font)
        scale = No_Label_Size / face.units_per_EM
        for ch in Label_No:
            _, adv = get_glyph_contours_and_advance(ch, DEFAULT_POINTS_PER_MM, scale, font_path=no_font)
            m = build_flat_text(ch, DEFAULT_POINTS_PER_MM, 0.01, font_size_mm=No_Label_Size, font_path=no_font)
            no_parts.append(sp.translate(m, [cursor, 0, 0]))
            cursor += adv
        no_mesh = sp.translate(sp.union_all(no_parts), [-cursor / 2.0, 0, 0])
        no_mesh = sp.translate(no_mesh, [-0.1 + No_Label_Offset, 14, 0])
        parts.append(no_mesh)

    label_font = Label_Font_Override or FONT_PATH
    label_text = Label_Text_Override or FONT_NAME
    cursor = 0.0
    label_parts = []
    face = freetype.Face(label_font)
    scale = Font_Label_Size / face.units_per_EM
    for ch in label_text:
        if ch == " ":
            cursor += Font_Label_Size * 0.3
            continue
        _, adv = get_glyph_contours_and_advance(ch, DEFAULT_POINTS_PER_MM, scale, font_path=label_font)
        m = build_flat_text(ch, DEFAULT_POINTS_PER_MM, 0.01, font_size_mm=Font_Label_Size, font_path=label_font)
        label_parts.append(sp.translate(m, [cursor, 0, 0]))
        cursor += adv
    label_mesh = sp.translate(sp.union_all(label_parts), [-cursor / 2.0, 0, 0])
    label_mesh = sp.translate(label_mesh, [0, 0.6 + Font_Label_Offset, 0])
    parts.append(label_mesh)
    return sp.union_all(parts)


def FontName():
    """FontName() (v2/ibm.scad:973-981) - embosses Labels() onto the top
    face."""
    labels = Labels()
    labels = sp.translate(labels, [0, 0, 0.01])  # lift the flat text off z=0 before positioning
    return sp.scad_transform(
        labels,
        ("translate", [-8.5, 0, Top_Flat_To_Center - Del_Depth]),
        ("rotate", [0, 0, 270]),
    )


def SolidCleanup():
    """SolidCleanup() (v2/ibm.scad:661-689) - everything subtracted from
    FullBody(). Drain not ported (defaults off - see module docstring)."""
    parts = [
        sp.translate(sp.cylinder_z(2 * (Top_Flat_R + 2), 10.0, sections=Surface_Fn),
                     [0, 0, Top_Flat_To_Center]),
        sp.cylinder_z(Shaft_ID, 40.0, sections=Cyl_Fn, center=True),
        sp.translate(sp.frustum_z(Shaft_ID, Shaft_ID + 2 * Top_Chamfer, Top_Chamfer, sections=Surface_Fn),
                     [0, 0, Top_Flat_To_Center - Top_Chamfer]),
        sp.translate(sp.cylinder_z(Inside_ID, 20.0 + Boss_To_Center, sections=Surface_Fn), [0, 0, -20.0]),
        HollowProfile3(),
        Notch(),
        sp.rotate_z(Teeth(), Detent_Skirt_Clock_Offset),
    ]
    if Arrow:
        parts.append(Del())
    if Label:
        parts.append(FontName())
    return sp.union_all(parts)


def SubtractFromFull(points_per_mm=None, minkowski_enabled=None, draft_angle_deg=None):
    full = FullBody(points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled,
                    draft_angle_deg=draft_angle_deg)
    clean = SolidCleanup()
    result = full.difference(clean, engine="manifold")
    result, _, _, _ = sp.check_and_repair(result, label="SubtractFromFull")
    return result


# ------------------------------------------------------------- Resin support
# ResinRodAssemble() (v2/ibm.scad:790-878) - every real call site in the
# current v2 file uses a1=0 (the angle-tilted-tip variants are commented
# out dead code) - so this ports as straight vertical rods via
# resin_support.resin_rod()/connecting_rod() (the shared, already-generic
# rod/strut primitives every other machine's resin support uses), not a
# bespoke angle-aware system. a1 is therefore NOT a parameter here - a
# dead parameter in the real v2 source, not silently dropped (see module
# docstring's convention).

def _rod(h, tip_od):
    return resin_support.resin_rod(h, tip_od, Tip_H, Rod_D, Tip_In, Min_Rod_H,
                                    Base_H, Base_D, add_raft=True, resin_fn=Resin_Fn)


def ResinRodAssemble():
    _require_configured()
    parts = []
    for i in range(Chars_Per_Row):
        rod = sp.translate(_rod(0.0, Tip_D), [(Skirt_Bottom_OD + Inside_ID) / 4, 0, 0])
        parts.append(sp.rotate_z(rod, i * Longitude_Step + Detent_Skirt_Clock_Offset + Resin_Detent_Clock_Offset))

    for i in range(11):
        # roof-roof support-supports
        p1 = np.array([(Boss_R + Inside_R + Boss_Step) / 2, 0, 6])
        angle2 = np.radians(360 / 11)
        p2 = np.array([(Boss_R + Inside_R + Boss_Step) / 2 * np.cos(angle2),
                        (Boss_R + Inside_R + Boss_Step) / 2 * np.sin(angle2), 0])
        hull1 = resin_support.connecting_rod(p1, p2, Rod_D)
        parts.append(sp.rotate_z(hull1, i * 360 / 11))

        if i != 4:
            inner_x = (Boss_R + Shaft_ID / 2) / 2
            parts.append(sp.rotate_z(sp.translate(_rod(Floor + Boss_To_Center, Tip_D), [inner_x, 0, 0]),
                                      i * 360 / 11))
            hull2 = resin_support.connecting_rod(
                [inner_x, 0, 12], [(Boss_R + Inside_R + Boss_Step) / 2, 0, 8], Rod_D)
            parts.append(sp.rotate_z(hull2, i * 360 / 11))
            if i != 3:
                x_offset = inner_x  # ResinXOffset(0) == 0
                a2 = np.radians(360 / 11)
                hull3 = resin_support.connecting_rod([x_offset, 0, 1],
                                                       [x_offset * np.cos(a2), x_offset * np.sin(a2), 7], Rod_D)
                parts.append(sp.rotate_z(hull3, i * 360 / 11))

        parts.append(sp.rotate_z(sp.translate(_rod(Floor + Roof, Tip_D),
                                               [(Boss_R + Inside_R + Boss_Step) / 2, 0, 0]),
                                  i * 360 / 11))

    n = Tip_Notch_Offset
    inner_x = (Boss_R + Shaft_ID / 2) / 2
    for j, k in enumerate([n, -n]):
        parts.append(sp.rotate_z(sp.translate(_rod(Floor + Boss_To_Center, Tip_Notch_D), [inner_x, 0, 0]),
                                  Drive_Notch_Theta + k))
        # v2's hull() here rotates its TWO spheres by two DIFFERENT
        # angles each (Drive_Notch_Theta-k[j] and l[j]*360/11), computed
        # independently in world coordinates - not a single shared
        # rotation applied to the whole hull afterward like the other
        # strut cases above. A sphere is rotationally symmetric, so
        # "translate then rotate the sphere" reduces to just placing it
        # directly at the rotated point - computed that way here.
        l = [3, 5][j]
        theta1 = np.radians(Drive_Notch_Theta - k)
        theta2 = np.radians(l * 360 / 11)
        p1 = [inner_x * np.cos(theta1), inner_x * np.sin(theta1), 12]
        p2 = [inner_x * np.cos(theta2), inner_x * np.sin(theta2), 7]
        parts.append(resin_support.connecting_rod(p1, p2, Rod_D))
    return sp.union_all(parts)


# ------------------------------------------------------------------ Element

def FullElement(points_per_mm=None, separation_mm=None, render_core_groove=None,
                cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
                minkowski_enabled=None, draft_angle_deg=None):
    """separation_mm/render_core_groove/cone_segments/simplify_tolerance_mm/
    platen_fn are accepted-but-ignored - generate.py's build_fn(...) call
    is uniform across every machine (see CLAUDE.md's "Porting a new
    machine" convention); Selectric has no core-groove concept, no
    separate Minkowski-cone circular-segments knob (Mink_Fn from config
    is used directly - see quality.minkowski_fn), and reuses Cyl_Fn for
    the platen cutter's own facet count (matching v2, which has no
    distinct Platen_Fn variable either - PlatenCutout's cylinder uses
    Cyl_Fn directly, ibm.scad:515)."""
    _require_configured()
    result = SubtractFromFull(points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled,
                              draft_angle_deg=draft_angle_deg)
    build_log.mesh_report(result, "FullElement")
    return result, []


def Additive(points_per_mm=None, separation_mm=None, render_core_groove=None,
             cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
             minkowski_enabled=None, draft_angle_deg=None):
    """No separate additive/subtractive split in the real geometry (unlike
    the cylinder family) - FullBody() is a real union then FullBody minus
    SolidCleanup happens together in SubtractFromFull(). Provided for
    generate.py's uniform dispatch only - see FullElement's docstring for
    the accepted-but-ignored kwargs."""
    _require_configured()
    return FullBody(points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled,
                    draft_angle_deg=draft_angle_deg), []


def ResinPrint(points_per_mm=None, separation_mm=None, render_core_groove=None,
               cone_segments=None, simplify_tolerance_mm=None, platen_fn=None,
               minkowski_enabled=None, draft_angle_deg=None):
    _require_configured()
    full, char_parts = FullElement(points_per_mm=points_per_mm, minkowski_enabled=minkowski_enabled,
                                    draft_angle_deg=draft_angle_deg)
    # v2's ResinPrint() (ibm.scad:881-887): `translate([0,0,Floor])
    # SubtractFromFull(); ResinRodAssemble();` - the main body is shifted
    # up by Floor so the detent teeth land at world z=0, which is the
    # frame EVERY rod height in ResinRodAssemble() assumes (h=0 for teeth
    # supports, Floor+Boss_To_Center for boss supports, Floor+Roof for
    # roof supports - all measured from that same teeth-at-z=0 origin,
    # not the sphere center FullElement() itself is built around). Missing
    # this translate is exactly what put the rods at the wrong heights
    # relative to the body - confirmed visually (rods floating detached
    # from the ball) before this fix.
    full = sp.translate(full, [0, 0, Floor])
    support = ResinRodAssemble()
    build_log.mesh_report(support, "ResinSupport")
    combined = sp.union_all([full, support])
    combined, _, _, _ = sp.check_and_repair(combined, label="ResinPrint")
    return combined, char_parts


# --------------------------------------------------------------- Type Test

def TextGauge(text, cpi):
    """TextGauge() (v2/ibm.scad:890-900) - monospaced CPI type-test gauge,
    shared by Selectric I/II and Selectric III (Composer uses its own
    pica-based system - lib/selectric_composer.py)."""
    from glyph_poc import build_flat_text
    parts = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        m = build_flat_text(ch, DEFAULT_POINTS_PER_MM, 0.4, font_size_mm=Font_Size, font_path=FONT_PATH)
        parts.append(sp.translate(m, [8 + i * 22.0 / cpi, 8, 0]))
    return sp.union_all(parts)
