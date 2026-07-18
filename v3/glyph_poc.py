"""
v3 proof-of-concept: single-glyph LetterText() ported from v2/lib/glyph_pipeline.scad
to build123d, replacing minkowski(diff_result, draft_cone) with native draft().

Ported constants (v2/blickensderfer.scad):
  Element_Diameter=34, Platen_Diameter=32.258, Char_Protrusion=0.5,
  Font_Size=3.7, Letter_Extrude_Depth=6 (module default), Mink_Draft_Angle=55

Font swapped to DejaVu Sans Mono (Blick_Script_Leo isn't installed here) - only
the pipeline mechanics are under test, not the real typeface.

Draft angle: OpenSCAD's cone is r1=0, r2=minkTextR(angle)=2*tan(angle/2), h=2,
so the cone's half-angle-from-axis is atan(r2/h) = atan(tan(angle/2)) = angle/2.
That's the actual wall lean added to each face, so draft() would want angle/2
(27.5 deg for Blickensderfer's Mink_Draft_Angle=55), not Mink_Draft_Angle
directly.

FINDING (see side-experiment run below the main script): build123d's native
draft() - OCC's classic BRepOffsetAPI_DraftAngle - does NOT reliably replace
minkowski(cone) for this use case:
  - Straight-walled letters ("L", "I") draft fine at shallow angles but
    self-intersect (Standard_ConstructionError) well before 27.5 deg once
    the taper exceeds the stroke width over a 6mm depth.
  - Curved letters ("O", and any glyph with bezier/spline strokes, which is
    most real fonts) fail outright at ANY angle: "Draft not supported on
    face(s) with geometry: EXTRUSION". OCC's classic draft algorithm only
    accepts side faces from straight-line-segment profiles; b-spline-swept
    side faces (from curved letterforms) are rejected regardless of depth
    or platen cutout.
Practical read: minkowski(cone) is slow but shape-agnostic; draft() is fast
but only usable on letters built from straight strokes, and only up to a
few degrees. A loft() between two offset/scaled profiles (not draft()) is
the more promising native-B-rep replacement to try next, since it doesn't
share draft's curve-type restriction. DRAFT_ANGLE below is clamped to 2 deg
so the demo actually succeeds end-to-end; see clamp note.
"""

from build123d import *

# --- Parameters ported from v2/blickensderfer.scad ---
ELEMENT_DIAMETER = 34.0
PLATEN_DIAMETER = 32.258
CHAR_PROTRUSION = 0.5
FONT_SIZE = 3.7
EXTRUDE_DEPTH = 6.0
MINK_DRAFT_ANGLE = 55.0
_TARGET_DRAFT_ANGLE = MINK_DRAFT_ANGLE / 2  # 27.5 deg - see module docstring
DRAFT_ANGLE = 2.0  # clamped: 27.5 deg self-intersects on this glyph/depth

FONT = "DejaVu Sans Mono"
CHAR = "A"

R = ELEMENT_DIAMETER / 2
placement_radius = R + CHAR_PROTRUSION
text_baseline = 0.0
platen_baseline = 0.0

# Plane tangent to the element cylinder at latitude 0 (angle=0 -> +X).
# local x -> circumference (global Y), local y -> element axis (global Z),
# local z (normal) -> outward radial (global X). Mirrors LetterPlacement's
# rotate([90,0,90]) + translate(R,0,0) without composing OpenSCAD's exact
# rotation stack.
glyph_plane = Plane(
    origin=(placement_radius, 0, text_baseline),
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0),
)

with BuildSketch(glyph_plane) as glyph_sketch:
    Text(CHAR, font_size=FONT_SIZE, font=FONT, align=(Align.CENTER, Align.CENTER))

# LetterText(): extrude the glyph inward, embedding it into the element body
# with its outward tip flush at the platen-tangent radius (Step 1-2), then
# carve the concave platen cutout into that tip (Step 3).
glyph_boss = extrude(glyph_sketch.sketch, amount=-EXTRUDE_DEPTH)

platen_cutter = (
    Cylinder(radius=PLATEN_DIAMETER / 2, height=40)
    .rotate(Axis.X, 90)
    .translate((placement_radius + PLATEN_DIAMETER / 2, 0, platen_baseline))
)

carved = glyph_boss - platen_cutter

# Step 4: draft angle on the side walls (faces roughly parallel to the
# radial extrude direction). Neutral plane sits at the outward print face
# (the tip, unchanged) so the boss grows wider toward the embedded base -
# same intent as minkowski(cone), per the module docstring: "Print face
# grows outward at the base, narrows at the tip".
side_faces = [
    f for f in carved.faces() if abs(f.normal_at().to_tuple()[0]) < 0.9
]

neutral_plane = Plane(
    origin=(placement_radius, 0, text_baseline),
    x_dir=glyph_plane.x_dir,
    z_dir=glyph_plane.z_dir,
)

drafted = draft(side_faces, neutral_plane=neutral_plane, angle=DRAFT_ANGLE)

print(f"target angle (Mink_Draft_Angle/2) = {_TARGET_DRAFT_ANGLE} deg -> "
      f"clamped to {DRAFT_ANGLE} deg (see module docstring FINDING)")
print(f"side faces drafted: {len(side_faces)}")
print(f"carved  volume={carved.volume:.3f}mm3  bbox={carved.bounding_box()}")
print(f"drafted volume={drafted.volume:.3f}mm3  bbox={drafted.bounding_box()}")

export_stl(carved, "out_carved_no_draft.stl")
export_stl(drafted, "out_drafted.stl")
export_step(drafted, "out_drafted.step")

# reorient so the print face (local +X/radial) faces the viewer (+Z) for a
# sensible top-down 2D projection
viewable = drafted.rotate(Axis.Y, -90)
svg = ExportSVG(unit=Unit.MM, line_weight=0.2)
svg.add_shape(viewable)
svg.write("out_drafted_top.svg")
