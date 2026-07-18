//Minkowski draft-angle tester
//Standalone harness around lib/glyph_pipeline.scad's LetterText() - the same
//extrude -> platen cutout -> minkowski(cone) pipeline every v2 machine
//renders through - using Blickensderfer's element geometry as the reference
//dimensions (see v2/blickensderfer.scad). Renders each character in
//Test_Chars through that exact pipeline in isolation (no full element, no
//circular layout - latitude is fixed at 0 for every character) and lines
//the results up along +X for side-by-side inspection/export. Exists to
//produce reference geometry for comparing against v3's minkowski(cone)
//replacement experiments - see v3/README.md.

/* [Test] */
//characters to render, each spaced out along +X for side-by-side comparison
Test_Chars="H";
//spacing between characters along +X (mm)
Char_Spacing=10;
//which row's Baseline/Cutout to use for every test character (Blickensderfer's
//arrays are per-row: 0=lowercase, 1=uppercase, 2=figs)
Test_Row=1;//[0:lowercase, 1:uppercase, 2:figs]

/* [Global Parameters] */
//to help with z fighting
z=.01;
//minkowski facet number
Mink_Fn=12;
//text facet number
Text_Fn=20;
//wire Text_Fn into the lib's Text_2D_Fn hook so glyph curves use a dedicated
//value instead of silently inheriting Surface_Fn - see blickensderfer.scad.
Text_2D_Fn=Text_Fn;
//cylinder facet number
Cyl_Fn=360;
//surface facet number
Surface_Fn=120;

/* [Render Parameters] */
//turn minkowski on
Mink_On=true;
//draft angle
Mink_Draft_Angle=55;

/* [Typeface Stuff] */
Font="Blick_Script_Leo";
Font_Size=3.7;
Font_Weight_Offset=0;
X_Font_Weight_Adj=0;
Y_Font_Weight_Adj=0;

/* [Glyph Quality] */
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
Horizontal_Weight_Adj=.001;
Vertical_Weight_Adj=.001;
Scale_Multiplier_Text="";
Scale_Multiplier=1.0;
Y_Scale=1;
Typeface_2="Arial";
Type_2_Size=3.7;
Typeface_2_Chars="";

/* [Element Dimensions] (Blickensderfer reference) */
//OD of platen
Platen_Diameter=32.258;
//OD of element at non-text section
Element_Diameter=34;
//OD of element between two characters (minimum distance in concave section)
Min_Final_Character_Diameter=35;
//minimum text protrusion distance
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//element height/thickness
Element_Height=17.15;
//latitude spacing
Latitude_Int=360/28;
//baseline values for characters from top of element
Baseline=[-4, -10.3, -16.1];
//baseline values for platen cutouts from top of element
Cutout=[-2.55, -8.66, -14.45];
//Blickensderfer's Baseline/Cutout are negative-from-clip-end, so this shifts
//placement to an absolute height - see blickensderfer.scad.
Baseline_Z_Offset=Element_Height;

include <lib/glyph_pipeline.scad>

module MinkGlyphTester(){
    for (n=[0:len(Test_Chars)-1])
    translate([n*Char_Spacing, 0, 0])
    translate([0, 0, Baseline_Z_Offset])
    LetterText(Test_Chars[n], Font, Font_Size, Cutout[Test_Row], Baseline[Test_Row], 0);
}

MinkGlyphTester();
