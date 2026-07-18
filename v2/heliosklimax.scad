//Helios Klimax Type Element
//Leonard Chau
//
//v2.0: glyph pipeline unified with Blickensderfer2/Postal/Bennett/Mignon's
//shared lib/glyph_pipeline.scad. Helios's platen cutout radius
//Platen_Diameter/2+Min_Final_Character_Diameter/2 expands to
//Element_Diameter/2+Platen_Diameter/2+Char_Protrusion (same as Blick2's
//formula, since Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2
//cancels the Element_Diameter/2 term). Its Character_Modifieds baseline
//shift is a plain world-Z addition after the radial placement translate,
//matching the lib's TextRing charBaseline computation directly.
//
//CORRECTION (2026-07-08): the first pass of this file had two bugs, found by
//byte-comparing rendered STLs against v1/HeliosKlimax/HeliosKlimaxElement.scad
//(see docs, byte-check parameter sets dated 2026-07-08):
//  1. Baseline_Z_Offset was set to 0 with Baseline/Cutout copied verbatim as
//     positive values, on the mistaken premise that Helios's arrays were
//     already absolute-from-bottom like Bennett/Mignon's. They are not - the
//     original computed Element_Height-Baselines[row]/Element_Height-
//     Cutouts[row] (top-down), the same negative-from-clip-end convention
//     Blick2/Postal use. This placed every character near the wrong end of
//     the element. Fixed by negating Baseline/Cutout and setting
//     Baseline_Z_Offset=Element_Height.
//  2. The placement radius was assumed to be the raw Element_Diameter/2
//     (Bennett/Mignon's convention, Letter_Placement_Protrusion=0), but the
//     original actually passed (Element_Diameter-.1) as the placement
//     diameter - a small built-in 0.05mm radial inset that only affects
//     placement, not the platen-cutout radius. Fixed with
//     Letter_Placement_Protrusion=-.05.
//Both fixes verified against v1's render: topology now matches exactly
//(same genus) once the shared lib's z-fighting epsilon inset on the
//placement radius (lib/glyph_pipeline.scad's LetterPlacement, same effect
//documented in hammond.scad) is zeroed out for comparison. A residual
//sub-thousandth-mm vertex-level difference remains from that epsilon inset,
//well below print resolution - same known/accepted residual as Hammond's,
//not specific to this fix.
//Core/shaft groove family
//not applicable - Helios has no SecondaryCore/CoreGrooves/CoreChamfer/
//CoreEllipses system in the original. Clip+wire-bite system (similar in
//spirit to Blick2/Postal's) stays local, same as Blick2/Postal's own
//clip/wire-bite (never extracted to a shared lib). Original preserved at
//HeliosKlimax/HeliosKlimaxElement.scad.
//
//NOTE: the original file declares Resin_Support/Resin_Support_* parameters
//but never actually generates any resin support geometry with them (no
//ResinRod/CutGroove-equivalent module, nothing calls them) - preserved as
//declared-but-unused, matching the original exactly rather than inventing a
//resin support system that wasn't there.
//
//Customizer sections below follow Blickensderfer's canonical layout (Global
//Parameters, Render Parameters, Testing Stuff, Key Mapping, Typeface Stuff,
//Glyph Quality, Element Dimensions, Type Test, Resin Printing, lib wiring)
//so all v2 machine files are organized the same way. Sections with no Helios
//equivalent (Logo, Print Tolerances, Shaft Gauge Test) are omitted rather
//than left empty.

/* [Global Parameters] */
//to help with z fighting
z=.01;
//minkowski facet number - Helios's original had no dedicated value at all
//(the minkowski cone reused text_fn's facet count); given its own literal
//here to match every other v2 machine's independent Mink_Fn. Inert unless
//Mink_On is enabled (off by default).
Mink_Fn=12;
//text facet number (renamed from text_fn)
Text_Fn = $preview ? 10 : 20;
//Helios's original Text() set $fn=text_fn locally (it's also what the
//minkowski cone reused - see Mink_Fn above); wire that into the lib's
//Text_2D_Fn hook so glyph curves use this instead of silently inheriting
//Surface_Fn (every v2 machine should set this - see blickensderfer.scad).
Text_2D_Fn=Text_Fn;
//critical (shaft/pin) cylinder facet number (renamed from criticalcyl_fn)
Cyl_Fn = $preview ? 60 : 360;
//surface facet number (renamed from surface_fn)
Surface_Fn = $preview ? 60 : 360;

/* [Render Parameters] */
//render something?
Render=false;
//render mode
Render_Mode=0;//[0:Normal, 1:Type Test]
//turn minkowski on
Mink_On=false;
//Helios's original cone (r1=0,r2=.75,h=1.5) already matched Blick2/Postal's
//r1=0,r2=X convention (unlike Bennett/Mignon's reversed r1=X,r2=0) - still
//not a calibrated dimension, uses the shared angle-derived formula.
Mink_Draft_Angle=55;
//view cross section (reordered after Mink_On/Mink_Draft_Angle to match
//Blick2/Postal's canonical Render Parameters order)
X_Section=false;
X_Section_Theta=180;

/* [Testing Stuff] */
Testing_Baseline=false;
Testing_Cutout=false;
Testing_Layout=false;
Testing_Offsets=[-.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, .6];
Cutout_Test=Testing_Cutout;
Baseline_Test=Testing_Baseline;
Test_Layout=Testing_Layout;
Cutout_Test_Array=Testing_Offsets;
Baseline_Test_Array=Testing_Offsets;
Test_Char="H";

/* [Key Mapping] */
GERMAN=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⅟J=,;XY₰ß&%/-_§?Q"];

GERMAN_MOD=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⁄J=,;XY¢ß&%/-_§?Q"];
LAYOUT=GERMAN_MOD;
//Row Height (negative-from-clip-end, same convention as Blick2/Postal -
//the original computed Element_Height-Baselines[row], not an absolute
//from-bottom height; see Baseline_Z_Offset below)
Baseline=[-3.0, -7.8, -12.5, -17.3];
//Platen Cutout Height (negative-from-clip-end, see Baseline above)
Cutout=[-2.5, -7.3, -12, -16.8];
//Latitude_Int/Angle_Half_Step: Helios's Theta=theta*column with theta=360/21 has
//no half-column-step term (like Mignon), and places column N at raw Theta
//(no CharLegend-style remap - LAYOUT is already in physical column order).
Latitude_Int=360/21;
Angle_Half_Step=0;

/* [Typeface Stuff] */
Typeface_="Kurinto Type";//"Consolas";
Type_Size=2.7;//2;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
//Character_Modifieds only ever shifted baseline in Helios's original (no
//Font swap), so these alias to Helios's own Font/size for a no-op swap.
Character_Modifieds_Font=Typeface_;
Character_Modifieds_Size=Type_Size;
//offset()-based stroke weight (Blickensderfer2/Postal's system) - Helios
//never had this, 0 = no-op, layered independently of Weight_Adj_Mode below.
Font_Weight_Offset=0;
X_Font_Weight_Adj=0;
Y_Font_Weight_Adj=0;
Font=Typeface_;
Font_Size=Type_Size;

/* [Glyph Quality (unified across all v2 machines)] */
//Helios never had per-character size scaling; "." isn't specially sized in
//the original despite Scale_Multiplier_Text/Scale_Multiplier being declared
//there (they were declared but Scale_Multiplier_Text's default "." was
//already present in the original - preserved as-is).
Scale_Multiplier_Text=".";
Scale_Multiplier=1.5;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Helios's original had no Weight_Adj_Shape (only ever used the square
//profile inline) - default 0 (Square) matches exactly.
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//vertical glyph scale before extrusion - Helios never had this, 1 = no-op.
Y_Scale=1;
//secondary typeface for specific characters - Helios never had this.
Typeface_2=Typeface_;
Type_2_Size=Type_Size;
Typeface_2_Chars="";
//horizontal alignment method for TwoDText/AlignedText, see docs/text-centering.md.
//Methods 1/2 require OpenSCAD's "Text Metrics" experimental feature enabled
//(Preferences>Features, or --enable=textmetrics) - without it this silently
//renders unshifted, no error.
Text_Align_Method=0;//[0:Advance Center (native), 1:Ink Center, 2:Ink Left (fixed CPI pitch), 3:Ink Right (fixed CPI pitch)]
//universal fine-tune nudge (mm), layered on top of whichever method above is selected
Text_Align_X_Offset=0;//[-5:.01:5]
//characters that get their OWN alignment method + offset, separate from
//the pair above (e.g. thin punctuation ".,:;") - lets the main alphabet
//stay on native centering while these get independent treatment. See
//AlignedText() in glyph_pipeline.scad. ""=no-op.
Text_Align_Modified_Chars="";
//alignment method (same enum as Text_Align_Method above) applied only to
//characters in Text_Align_Modified_Chars.
Text_Align_Method_Modified=0;//[0:Advance Center (native), 1:Ink Center, 2:Ink Left (fixed CPI pitch), 3:Ink Right (fixed CPI pitch)]
//fine-tune nudge (mm) applied only to characters in Text_Align_Modified_Chars.
Text_Align_X_Offset_Modified=0;//[-5:.01:5]
//second, independent per-character override set (e.g. characters needing
//right-alignment via method 3 while Text_Align_Modified_Chars above handles
//a different subset) - a character matching BOTH sets resolves to this one.
//See AlignedText() in glyph_pipeline.scad. ""=no-op.
Text_Align_Modified2_Chars="";
//alignment method (same enum as Text_Align_Method above) applied only to
//characters in Text_Align_Modified2_Chars.
Text_Align_Method_Modified2=0;//[0:Advance Center (native), 1:Ink Center, 2:Ink Left (fixed CPI pitch), 3:Ink Right (fixed CPI pitch)]
//fine-tune nudge (mm) applied only to characters in Text_Align_Modified2_Chars.
Text_Align_X_Offset_Modified2=0;//[-5:.01:5]

/* [Element Dimensions] */
//Platen Diameter
Platen_Diameter=30;
//Element Diameter
Element_Diameter=27.15;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=28.19;
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//Element Height
Element_Height=18.7;
//Shaft Diameter
Shaft_Diameter=4.16;
Element_Square_Hole_Position=8.92;
Element_Square_Hole_Width=4.10;
Element_Square_Hole_Length=2.88;
Element_Square_Hole_Support_Height=3;
Element_Indicator_Hole_Position=10;
Element_Indicator_Hole_Diameter=2;
Element_Shell_Thickness=1.5;
Element_Inside_Radius=1;
Element_Clip_Height=3;
Element_Clip_Diameter=7;
Element_Wire_Diameter=.554;
Element_Clip_Bite=.7;
Element_Clip_Angle=180;

/* [Type Test] */
//characters per inch for the flat type-test string
Test_CPI=10;
//Default reconstructs today's behavior (every character in the current
//physical layout, row by row); Test String instead prints
//Test_String_Text verbatim, replacing the default on BOTH the
//embossed/CPI-spaced character row and the flat reference caption line
//beneath it, for direct comparison against the physical printout.
Test_Content=0;//[0:Default, 1:Test String]
Test_String_Text="The quick brown fox jumps over the lazy dog 1234567890";
//flat reference caption line beneath the embossed/CPI-spaced character
//row (same text as Test_Content above, at natural/proportional spacing) -
//off hides it, leaving only the embossed row.
Show_Reference_Line=true;
//thin semi-transparent frame around each character's window (25.4/Test_CPI
//wide), so ink position can be checked against the slot - preview (F5) only
Show_Align_Bounds=false;

/* [Resin Printing] */
//NOTE: declared but unused in the original - see file header. Preserved
//as-is rather than inventing a resin support system.
Resin_Support=true;
Resin_Support_Base_Thickness=2;
Resin_Support_Rod_Thickness=.4;
Resin_Support_Min_Height=1;
Resin_Support_Spacing=3;
Resin_Support_Contact_Radius=.2;

/* [Glyph pipeline lib wiring] */
//Physical_Layout: LAYOUT is already in physical column order (no CharLegend
//remap in the original), so this is a direct pass-through.
Physical_Layout=LAYOUT;
//Element_Diameter, Platen_Diameter, Char_Protrusion, Baseline, Cutout,
//Character_Modifieds*, Weight_Adj_*, Scale_Multiplier*, Y_Scale, Typeface_2*
//all already declared natively above - no bridging needed.
//Baseline_Z_Offset=Element_Height: Helios's original computed
//Element_Height-Baselines[row]/Element_Height-Cutouts[row] (top-down), the
//same negative-from-clip-end convention as Blick2/Postal, not the
//absolute-from-bottom convention Bennett/Mignon use. Baseline/Cutout above
//were corrected to negative values to match.
Baseline_Z_Offset=Element_Height;
//Cyl_Fn/Surface_Fn/Text_Fn/Mink_Fn already declared natively above (Global
//Parameters) - no bridging needed now that Helios uses the canonical names
//directly instead of its old underscore-style names.
//Helios's original passed (Element_Diameter-.1) as the placement diameter
//(not the raw Element_Diameter) - a small built-in 0.05mm radial inset,
//independent of the platen-cutout radius which does use the full
//Element_Diameter/2. Reproduced here as a small negative protrusion rather
//than 0.
Letter_Placement_Protrusion=-.05;
//Helios's raw pre-cutout extrusion block: starts exactly at the placement
//radius (no offset), extends 2mm outward, trimmed down by the (verified)
//PlatenCutout afterward.
Letter_Extrude_Offset=0;
Letter_Extrude_Depth=2;

include <lib/glyph_pipeline.scad>

/* [Core/shaft lib wiring] */
//Helios's original had no SecondaryCore/CoreGrooves/CoreChamfer/CoreEllipses
//at all, so lib/core_shaft.scad is NOT included here. Nothing to bridge.

//Helios's original had NO render gate at all - the geometry rendered
//unconditionally on load, unlike every other v2 machine. Wrapped in the same
//Render/X_Section gate Bennett/Mignon/Blick2/Postal use for consistency (and
//so opening the file in Customizer doesn't force a full render every time).
module Assemble(){
difference(){
    union(){
        difference(){
            union(){
                //Join Cylinder and LetterText
                TextRing();
                translate([0, 0, -.01])
                cylinder(h=Element_Height+2*.01, d=Element_Diameter, $fn=Surface_Fn);
            }

            //Hollowing Element
            x_min=Shaft_Diameter/2+Element_Shell_Thickness+Element_Inside_Radius;
                    x_max=Element_Diameter/2-Element_Shell_Thickness-Element_Inside_Radius;
                    y_min=Element_Shell_Thickness+Element_Inside_Radius;
                    y_max=Element_Height-Element_Shell_Thickness-Element_Inside_Radius;
            rotate_extrude($fn=Surface_Fn){
                hull(){
                    //Bottom Left
                    translate([x_min, y_min])
                    circle(r=Element_Inside_Radius, $fn=Surface_Fn);
                    //Top Left

                    translate([x_min, y_max-.5])
                    circle(r=Element_Inside_Radius, $fn=Surface_Fn);
                    //Top Right
                    translate([x_max, y_max-.5])
                    circle(r=Element_Inside_Radius, $fn=Surface_Fn);
                    //Top
                    translate([(x_min+x_max)/2, y_max])
                    circle(r=Element_Inside_Radius, $fn=Surface_Fn);
                    //Bottom Right
                    translate([x_max, y_min])
                    circle(r=Element_Inside_Radius, $fn=Surface_Fn);
                }
            }

            //Cleaning Top and Bottom Minkowski
            translate([0, 0, Element_Height])
            cylinder(d=Element_Diameter+5, h=5);
            rotate([0, 180, 0])
            cylinder(d=Element_Diameter+5, h=5);

            //Cutting Indicator Hole
            translate([Element_Indicator_Hole_Position, 0, Element_Height-Element_Shell_Thickness/2])
            cylinder(h=6, d=Element_Indicator_Hole_Diameter, $fn=Surface_Fn, center=true);
        }

        //Adding Alignment Pin Support
        translate([-Element_Square_Hole_Position, 0,Element_Shell_Thickness-.01])
        cylinder(h=Element_Square_Hole_Support_Height, d=Element_Square_Hole_Width+2);

        //Adding Clip Retainer
        translate([0, 0, Element_Height-.01])
        cylinder(h=Element_Clip_Height, d=Element_Clip_Diameter, $fn=Surface_Fn);
    }

    //Cutting Alignment Pin Hole
    translate([-Element_Square_Hole_Position, 0,Element_Shell_Thickness/2])
    cube([Element_Square_Hole_Length, Element_Square_Hole_Width, 10], center=true);

    //Cutting Center Shaft Hole
    translate([0, 0, -.01])
    cylinder(h=Element_Height+Element_Clip_Height+2*.01, d=Shaft_Diameter, $fn=Surface_Fn);

    //Cutting Wire Clip
    rotate([0, 0, Element_Clip_Angle])
    translate([0, -Shaft_Diameter/2-Element_Wire_Diameter/2+Element_Clip_Bite, Element_Height+Element_Wire_Diameter/2])
        hull(){
            rotate([0,-90,0])
            cylinder(r=Element_Wire_Diameter/2,h=8,center=true, $fn=Surface_Fn);
            translate([0,-5,.5])
            rotate([0,-90,0])
            cylinder(r=Element_Wire_Diameter/2+.5,h=8,center=true, $fn=Surface_Fn);
        }
}
}

//flat readable layout of the whole character set, for checking kerning/
//legibility at print size before generating full element geometry - same
//role as Blickensderfer/Postal's TypeTest.
module TypeTest(){
    _defaultTestString=JoinRows(LAYOUT);
    _testString=Test_Content==1?Test_String_Text:_defaultTestString;
    for (n=[0:len(_testString)-1]){
        char=_testString[n];
        charModsMatch=search(char, Character_Modifieds)!=[];
        font=charModsMatch?Character_Modifieds_Font:Font;
        size=charModsMatch?Character_Modifieds_Size:Font_Size;
        baselineOffset=charModsMatch?Character_Modifieds_Offset:0;
        translate([1/Test_CPI*25.4*n, baselineOffset, 0]){
            AlignedText(char, font, size);
            if (Show_Align_Bounds) AlignBoundsBox(25.4/Test_CPI, size*1.5);
        }
    }
    if (Show_Reference_Line)
    translate([-2.54/2, -5, 0])
    text(text=_testString, size=Font_Size, font=Font, halign="left", valign="baseline", $fn=Text_Fn);
}

if (Render==true){

if (Render_Mode==0)
difference(){
    Assemble();
    if (X_Section==true)
    rotate([0, 0, X_Section_Theta])
    translate([-50, 0, -50])
    cube(100);
}

if (Render_Mode==1)
TypeTest();

}
