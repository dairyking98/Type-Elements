// Synthetic proxy for v2/lib/glyph_pipeline.scad's LetterText() (line 356),
// used today to benchmark backend choice (CGAL vs Manifold) and quality
// settings (Mink_Fn/Text_Fn) without needing the real font/full element.
//
// platen_cutout() is NOT a faithful reproduction of the real PlatenCutout()
// formula - an earlier version tried to be (tangent exactly at the
// extrusion's tip, using Element_Diameter/Platen_Diameter/Char_Protrusion),
// but that construction is degenerate: tangent-only contact removes zero
// volume (verified directly - identical STL bounding boxes with/without the
// cutout). Testing against the real v2/lib/glyph_pipeline.scad + real
// Blickensderfer constants directly showed the real relationship is much
// more aggressive (>99% of a test glyph's volume removed for row 0), which
// isn't yet understood well enough here to reproduce faithfully - it likely
// depends on how the full element assembly uses this piece, not just
// PlatenCutout in isolation. Rather than guess further, platen_cutout()
// below is an intentionally simplified, clearly-visible demo cut (tunable
// via Cut_Depth) for sanity-checking geometry and timing impact - not a
// stand-in for the real carve depth/shape.
//
// Still NOT the real typeface (built-in OpenSCAD font instead) or the full
// element body (no core grooves, no resin supports, no cylindrical shell).
// Treat results as directionally representative, not a guarantee of the
// real pipeline's absolute numbers.
//
// To reproduce today's before/after comparison from the GUI:
//   - Open this file, set Mink_Fn/Text_Fn/Glyph_Count in Customizer.
//   - "before" (what Blickensderfer was actually running pre-fix): Mink_Fn=20,
//     Text_Fn=120 (simulates the un-wired Text_2D_Fn silently inheriting
//     Surface_Fn=120).
//   - "after" (the new v2 shared defaults as of today): Mink_Fn=12, Text_Fn=20.
//   - Render (F6) and check the status bar / console for render time, or
//     from a terminal:
//       time openscad-nightly --backend Manifold -o out.stl \
//           -D Mink_Fn=12 -D Text_Fn=20 -D Glyph_Count=84 \
//           v3/perf_test_synthetic_glyph.scad
//   - Preferences > Features: confirm "manifold" is enabled, or pass
//     --backend CGAL / --backend Manifold explicitly to compare.

/* [Test Parameters] */
//how many glyphs to render side by side, combined in one CSG tree
Glyph_Count = 84; //[1:1:96]
//minkowski draft cone facet count (matches v2's Mink_Fn)
Mink_Fn = 12;
//glyph outline curve facet count (matches v2's Text_Fn, wired via Text_2D_Fn)
Text_Fn = 20;
//built-in-font glyph extrude depth (matches v2's Letter_Extrude_Depth default)
Extrude_Depth = 6;
//draft cone base radius (matches v2's minkTextR(Mink_Draft_Angle) at 55deg)
Draft_Radius = 1.04;
//draft cone height (matches v2's Mink_H_Fixed)
Draft_Height = 2;
//characters to cycle through (built-in OpenSCAD font, not the real typeface)
Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-*/=()";

/* [Platen Cutout - demo cut, see header note] */
//platen (print roller) diameter, sets the cutout's curvature (v2's Platen_Diameter)
Platen_Diameter = 32.258;
//how deep the demo cut bites into the glyph's flat tip at its center
Cut_Depth = 1.5;
//platen cutout cylinder facet count (matches v2's Cyl_Fn)
Cyl_Fn = 360;

// Demo cutout: a cylinder of the real Platen_Diameter, positioned so its
// near surface dips Cut_Depth below the extrusion's flat tip at the glyph's
// center (x=0) and tapers back up toward the tip at the edges - a visible
// concave scoop, not the tangent-only (zero-volume) construction from
// before. See header note: not a faithful reproduction of the real
// PlatenCutout() carve depth/shape, just a stand-in with comparable
// geometric complexity for timing/visual sanity checks.
module platen_cutout() {
    translate([0, 0, Extrude_Depth - Cut_Depth + Platen_Diameter/2])
    rotate([90, 0, 0])
    cylinder(d=Platen_Diameter, h=20, center=true, $fn=Cyl_Fn);
}

module one_glyph(x_pos, y_pos, ch) {
    translate([x_pos, y_pos, 0])
    minkowski($fn=Mink_Fn) {
        difference() {
            linear_extrude(height=Extrude_Depth)
                translate([-3,-3,0]) text(ch, size=6, $fn=Text_Fn);
            platen_cutout();
        }
        cylinder(r1=0, r2=Draft_Radius, h=Draft_Height, $fn=Mink_Fn);
    }
}

//lay glyphs out in a grid (20 per row) instead of a single row, so glyphs
//past #20 don't all land back at x=0..285,y=0 on top of the first 20
Glyphs_Per_Row = 20;
Row_Spacing = 15;
for (i = [0 : Glyph_Count - 1])
    one_glyph((i % Glyphs_Per_Row) * 15, floor(i / Glyphs_Per_Row) * Row_Spacing, Chars[i % len(Chars)]);
