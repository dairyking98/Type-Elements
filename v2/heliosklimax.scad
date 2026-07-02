//Helios Klimax Type Element
//Leonard Chau
//
//v2.0: glyph pipeline unified with Blickensderfer2/Postal/Bennett/Mignon's
//shared lib/glyph_pipeline.scad. Helios's transform reduces to the exact
//same world-frame formula algebraically (not approximately): its platen
//cutout radius Platen_Diameter/2+Min_Final_Character_Diameter/2 expands to
//Element_Diameter/2+Platen_Diameter/2+CharProtrusion (same as Blick2's
//formula, since CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2
//cancels the Element_Diameter/2 term), and its placement radius is the raw
//Element_Diameter/2 (Bennett/Mignon's convention, needs
//letterPlacementProtrusion=0). Its Character_Modifieds baseline shift is a
//plain world-Z addition after the radial placement translate, matching the
//lib's TextRing charBaseline computation directly. Core/shaft groove family
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
//Glyph Quality, Element Dimensions, Resin Printing, lib wiring) so all v2
//machine files are organized the same way. Sections with no Helios
//equivalent (Logo, Print Tolerances, Shaft Gauge Test, Type Test) are
//omitted rather than left empty.

/* [Global Parameters] */
//to help with z fighting
z=.01;
//surface facet number
surface_fn = $preview ? 60 : 360;
//critical (shaft/pin) cylinder facet number
criticalcyl_fn = $preview ? 60 : 360;
//text facet number
text_fn = $preview ? 22 : 44;

/* [Render Parameters] */
//render something?
Render=false;
XSection=false;
XSectionTheta=180;
//Speedy Preview and Render with No Minkowski
Debug_No_Minkowski=true;
minkOn=!Debug_No_Minkowski;
//Helios's original cone (r1=0,r2=.75,h=1.5) already matched Blick2/Postal's
//r1=0,r2=X convention (unlike Bennett/Mignon's reversed r1=X,r2=0) - still
//not a calibrated dimension, uses the shared angle-derived formula.
minkDraftAngle=55;

/* [Testing Stuff] */
testing_baseline=false;
testing_cutout=false;
testing_layout=false;
Testing_Offsets=[-.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, .6];
cutoutTest=testing_cutout;
baselineTest=testing_baseline;
testLayout=testing_layout;
cutoutTestArray=Testing_Offsets;
baselineTestArray=Testing_Offsets;
testChar="H";

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
//Row Height
Baseline=[3.0, 7.8, 12.5, 17.3];
//Platen Cutout Height
Cutout=[2.5, 7.3, 12, 16.8];
//latitudeInt/angleHalfStep: Helios's Theta=theta*column with theta=360/21 has
//no half-column-step term (like Mignon), and places column N at raw Theta
//(no CharLegend-style remap - LAYOUT is already in physical column order).
latitudeInt=360/21;
angleHalfStep=0;

/* [Typeface Stuff] */
Typeface_="Kurinto Type";//"Consolas";
Type_Size=2.7;//2;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
//Character_Modifieds only ever shifted baseline in Helios's original (no
//font swap), so these alias to Helios's own font/size for a no-op swap.
Character_Modifieds_Font=Typeface_;
Character_Modifieds_Size=Type_Size;
//offset()-based stroke weight (Blickensderfer2/Postal's system) - Helios
//never had this, 0 = no-op, layered independently of Weight_Adj_Mode below.
fontWeightOffset=0;
xFontWeightAdj=0;
yFontWeightAdj=0;
font=Typeface_;
fontSize=Type_Size;

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
Type_2Size=Type_Size;
Typeface_2Chars="";

/* [Element Dimensions] */
//Platen Diameter
Platen_Diameter=30;
//Element Diameter
Element_Diameter=27.15;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=28.19;
CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//Element Height
Element_Height=18.7;
//Shaft Diameter
Shaft_Diameter=4.16;
Element_SquareHole_Position=8.92;
Element_SquareHole_Width=4.10;
Element_SquareHole_Length=2.88;
Element_SquareHole_SupportHeight=3;
Element_IndicatorHole_Position=10;
Element_IndicatorHole_Diameter=2;
Element_Shell_Thickness=1.5;
Element_Inside_Radius=1;
Element_ClipHeight=3;
Element_ClipDiameter=7;
Element_WireDiameter=.554;
Element_ClipBite=.7;
Element_ClipAngle=180;

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
//physicalLayout: LAYOUT is already in physical column order (no CharLegend
//remap in the original), so this is a direct pass-through.
physicalLayout=LAYOUT;
//Element_Diameter, Platen_Diameter, CharProtrusion, Baseline, Cutout,
//Character_Modifieds*, Weight_Adj_*, Scale_Multiplier*, Y_Scale, Typeface_2*
//all already declared natively above - no bridging needed.
//baselineZOffset=0: Helios's Baseline/Cutout are already absolute heights
//from the bottom face, same convention as Bennett/Mignon.
baselineZOffset=0;
//quality variable name bridging
cylFn=criticalcyl_fn;
surfaceFn=surface_fn;
textFn=text_fn;
//Helios never declared a separate minkowski facet count - text_fn served
//that role too in the original ($fn=$preview?22:44 used everywhere,
//including the (unused when Debug_No_Minkowski=true) draft cone).
minkFn=text_fn;
//Helios's placement radius is the raw Element_Diameter/2 (no protrusion
//added there - Bennett/Mignon's convention, not Blick2/Postal's).
letterPlacementProtrusion=0;
//Helios's raw pre-cutout extrusion block: starts exactly at the placement
//radius (no offset), extends 2mm outward, trimmed down by the (verified)
//PlatenCutout afterward.
letterExtrudeOffset=0;
letterExtrudeDepth=2;

include <lib/glyph_pipeline.scad>

/* [Core/shaft lib wiring] */
//Helios's original had no SecondaryCore/CoreGrooves/CoreChamfer/CoreEllipses
//at all, so lib/core_shaft.scad is NOT included here. Nothing to bridge.

//Helios's original had NO render gate at all - the geometry rendered
//unconditionally on load, unlike every other v2 machine. Wrapped in the same
//Render/XSection gate Bennett/Mignon/Blick2/Postal use for consistency (and
//so opening the file in Customizer doesn't force a full render every time).
module Assemble(){
difference(){
    union(){
        difference(){
            union(){
                //Join Cylinder and LetterText
                TextRing();
                translate([0, 0, -.01])
                cylinder(h=Element_Height+2*.01, d=Element_Diameter, $fn=surface_fn);
            }

            //Hollowing Element
            x_min=Shaft_Diameter/2+Element_Shell_Thickness+Element_Inside_Radius;
                    x_max=Element_Diameter/2-Element_Shell_Thickness-Element_Inside_Radius;
                    y_min=Element_Shell_Thickness+Element_Inside_Radius;
                    y_max=Element_Height-Element_Shell_Thickness-Element_Inside_Radius;
            rotate_extrude($fn=surface_fn){
                hull(){
                    //Bottom Left
                    translate([x_min, y_min])
                    circle(r=Element_Inside_Radius, $fn=surface_fn);
                    //Top Left

                    translate([x_min, y_max-.5])
                    circle(r=Element_Inside_Radius, $fn=surface_fn);
                    //Top Right
                    translate([x_max, y_max-.5])
                    circle(r=Element_Inside_Radius, $fn=surface_fn);
                    //Top
                    translate([(x_min+x_max)/2, y_max])
                    circle(r=Element_Inside_Radius, $fn=surface_fn);
                    //Bottom Right
                    translate([x_max, y_min])
                    circle(r=Element_Inside_Radius, $fn=surface_fn);
                }
            }

            //Cleaning Top and Bottom Minkowski
            translate([0, 0, Element_Height])
            cylinder(d=Element_Diameter+5, h=5);
            rotate([0, 180, 0])
            cylinder(d=Element_Diameter+5, h=5);

            //Cutting Indicator Hole
            translate([Element_IndicatorHole_Position, 0, Element_Height-Element_Shell_Thickness/2])
            cylinder(h=6, d=Element_IndicatorHole_Diameter, $fn=surface_fn, center=true);
        }

        //Adding Alignment Pin Support
        translate([-Element_SquareHole_Position, 0,Element_Shell_Thickness-.01])
        cylinder(h=Element_SquareHole_SupportHeight, d=Element_SquareHole_Width+2);

        //Adding Clip Retainer
        translate([0, 0, Element_Height-.01])
        cylinder(h=Element_ClipHeight, d=Element_ClipDiameter, $fn=surface_fn);
    }

    //Cutting Alignment Pin Hole
    translate([-Element_SquareHole_Position, 0,Element_Shell_Thickness/2])
    cube([Element_SquareHole_Length, Element_SquareHole_Width, 10], center=true);

    //Cutting Center Shaft Hole
    translate([0, 0, -.01])
    cylinder(h=Element_Height+Element_ClipHeight+2*.01, d=Shaft_Diameter, $fn=surface_fn);

    //Cutting Wire Clip
    rotate([0, 0, Element_ClipAngle])
    translate([0, -Shaft_Diameter/2-Element_WireDiameter/2+Element_ClipBite, Element_Height+Element_WireDiameter/2])
        hull(){
            rotate([0,-90,0])
            cylinder(r=Element_WireDiameter/2,h=8,center=true, $fn=surface_fn);
            translate([0,-5,.5])
            rotate([0,-90,0])
            cylinder(r=Element_WireDiameter/2+.5,h=8,center=true, $fn=surface_fn);
        }
}
}

if (Render==true){

difference(){
    Assemble();
    if (XSection==true)
    rotate([0, 0, XSectionTheta])
    translate([-50, 0, -50])
    cube(100);
}

}
