//Mignon 2, 3, 4 Type Cylinder
//September 13, 2023
//Leonard Chau
//
//v2.0: glyph pipeline unified with Blickensderfer2/Postal/Bennett's shared
//lib/glyph_pipeline.scad - Mignon's transform chain turned out to be
//structurally identical to Bennett's (same nested-local-frame composition,
//which was numerically verified equivalent to the shared world-frame formula
//- see bennett.scad's header), differing only in a few parameters
//(no half-column-step angle offset, a secondary-typeface-by-character
//system, different extrude/cone dimensions) all of which the lib already
//supports via optional overrides. Core/shaft groove family not applicable -
//Mignon's shaft bore is a plain rotate_extrude() polygon, no groove system.
//Layout data moved to lib/layouts/mignon_layouts.scad (identical content,
//just relocated). Resin support and cylinder body geometry are
//Mignon-specific and stay local. Original preserved at
//Mignon/MignonCylinder.scad. This file was MignonCylinder2.scad, moved to
//v2/mignon.scad.
//
//Row1..Row7 replace the original's 1st_Row..7th_Row - OpenSCAD identifiers
//starting with a digit hit a hard parser error in testing (not just the
//deprecation warning the language reference implies), so they're renamed
//here. They're empty-string CUSTOMLAYOUT placeholders either way, zero
//geometry impact.
//
//Customizer sections below follow Blickensderfer's canonical layout (Global
//Parameters, Render Parameters, Testing Stuff, Key Mapping, Typeface Stuff,
//Glyph Quality, Element Dimensions, Logo, Type Test, Resin Printing, lib
//wiring) so all four v2 machine files are organized the same way. Sections
//with no Mignon equivalent (Print Tolerances, Shaft Gauge Test) are omitted
//rather than left empty.

/* [Global Parameters] */
//to help with z fighting
z=.001;
//minkowski facet number (renamed from mink_fn, to match every other v2 machine)
Mink_Fn=10;
//text facet number (renamed from text_fn)
Text_Fn=44;
//critical (shaft/pin) cylinder facet number (renamed from criticalcyl_fn)
Cyl_Fn=360;
//surface facet number (renamed from surface_fn)
Surface_Fn=360;
//resin support facet number (renamed from resin_fn)
Resin_Fn=20;

/* [Render Parameters] */
//render something? Mignon's original used the older V1 "Assert=true;
//assert(false,...)" gate (per docs/glyph-pipeline.md's V1/V2 pattern note) -
//switched to the same Render=false; boolean gate Bennett/Blick2/Postal use.
Render=false;
//render mode
Render_Mode=0;//[0:Resin Print, 1:Type Test]
//turn minkowski on
Mink_On=false;
//Mignon's original cone (r1=.75*6,r2=0,h=6) was never a calibrated dimension -
//uses the shared angle-derived formula instead, same draft angle as Blick2/
//Postal since Mignon never had its own draft-angle concept.
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
//which keyboard the console echo identifies positions against (independent
//of Layout_Selection below - your physical keyboard's key labels don't
//change just because you're test-printing a different language layout).
//Defaults to the same value as Layout_Selection - set this to whichever
//language your actual physical keyboard is labeled in.
Reference_Layout_Selection=5; //[0:Custom Layout,1:English 2,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]

/* [Key Mapping] */
Char_Legend=[7,8,9,10,11,0,1,2,3,4,5,6];

//Custom Layout
Row1="";
Row2="";
Row3="";
Row4="";
Row5="";
Row6="";
Row7="";
CUSTOMLAYOUT=[Row1,Row2,Row3,Row4,Row5,Row6,Row7];
include <lib/layouts/mignon_layouts.scad>

//Layout Selection
Layout_Selection=5; //[0:Custom Layout,1:English 2,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]
Layout=Layouts[Layout_Selection];
//Reference_Physical_Layout: same Char_Legend hardware remap as Physical_Layout
//below, but built from Reference_Layout_Selection - used only by the console
//echo, see lib/glyph_pipeline.scad's header comment.
Reference_Layout=Layouts[Reference_Layout_Selection];
Reference_Physical_Layout=[for (row=[0:6]) [for (col=[0:11]) Reference_Layout[row][Char_Legend[col]]]];
//Tallen Element? For Plakatschrift. Also Offsets Baselines by Tallen Baseline Offset
Tallen=false;
Tallen_Baseline_Offset=-1.25;
//Row Height
Baseline_Regular=[2.25, 7.55, 12.75, 17.8, 22.8, 28, 32.8];
Baseline_Tallen=Baseline_Regular+[for (n=[0:1:6]) Tallen_Baseline_Offset];
Baseline=Tallen?Baseline_Tallen:Baseline_Regular;
//Platen Cutout Height
Cutout=[2.7, 8.25, 13.6, 18.7, 23.7, 28.7, 33.6];
//Latitude_Int negative + Angle_Half_Step=0: Mignon's Theta=-(360/cols*col) has
//no half-column-step term at all (unlike Blick2/Postal/Bennett).
Latitude_Int=-360/len(Layout[0]);
Angle_Half_Step=0;

/* [Typeface Stuff] */
//Primary Font name
Typeface_="Iosevka Etoile";//As Installed on PC
Type_Size=2.45;//[1:.05:10]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
//Character_Modifieds only ever shifted baseline in Mignon's original (no
//Font swap - that's the separate Typeface_2_Chars system below), so these
//alias to Mignon's own Font/size for a no-op swap.
Character_Modifieds_Font=Typeface_;
Character_Modifieds_Size=Type_Size;
//offset()-based stroke weight (Blickensderfer2/Postal's system) - Mignon
//never had this, 0 = no-op, layered independently of Weight_Adj_Mode below.
Font_Weight_Offset=0;
X_Font_Weight_Adj=0;
Y_Font_Weight_Adj=0;
Font=Typeface_;
Font_Size=Type_Size;

/* [Glyph Quality (unified across all v2 machines)] */
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;//0.01
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//Y Scale Text
Y_Scale=1;
//Secondary Font name
Typeface_2="Times new roman";
Type_2_Size=2.75;//[1:.05:10]
//Secondary Font characters
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
Platen_Diameter=26.5;
//Main Cylinder Diameter
Element_Diameter=18.64;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=19.4;
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//Element Height Increase
Height_Increase=3;
//Total Cylinder Height
Cylinder_Height_=40.5;
Element_Height= Tallen==true ? Cylinder_Height_+Height_Increase : Cylinder_Height_;
//Height Drop From Top
Cylinder_Top_Height_Offset=3;
//Height Drop Chamfer Size
Cylinder_Top_Chamfer=2;
//Height Drop Diameter
Cylinder_Top_Diameter=10.5;
//Inner Shaft Diameter
Cylinder_Top_Shaft_Diameter=7.3;
//Inner Mounting Diameter
Cylinder_Bottom_Shaft_Diameter=14.6;
//Max Pin Height
Pin_Height=1.8;
//Max Pin Width
Pin_Width=1.7;
//Pin Depth
Pin_Depth=1;
//Pin All the way through?
Pin_Through=false;
Cylinder_Shape=0;//[0:Polygonal, 1:Cylindrical]

/* [Logo] */
//Label Font Override
Cylinder_Label_Font_Override="";
//Label Text Override
Cylinder_Label_Override="";
//Label Size
Cylinder_Label_Size_Override=0;//.1
//Label Text
Cylinder_Label= Cylinder_Label_Override== "" ? Typeface_ : Cylinder_Label_Override;
//Label Size
Cylinder_Label_Size=Cylinder_Label_Size_Override==0?0.51*Type_Size:Cylinder_Label_Size_Override*0.51;
//Label Font
Cylinder_Label_Font= Cylinder_Label_Font_Override== "" ?  Typeface_ : Cylinder_Label_Font_Override;
//Label Height Offset From Chamfer Base
Cylinder_Label_Height_Offset=.5;
//Spacing Between Characters (Degrees)
Cylinder_Label_Spacing=15;
//Label Offset From Pin (Degrees)
Cylinder_Label_Offset=0;

/* [Type Test] */
//characters per inch for the flat type-test string
Test_CPI=10;
//thin semi-transparent frame around each character's window (25.4/Test_CPI
//wide), so ink position can be checked against the slot - preview (F5) only
Show_Align_Bounds=false;

/* [Resin Printing] */
//Generate Print Support?
Generate_Support=true;
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.1;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=1.0;
//Resin Support Contact Point Diameter
Resin_Support_Contact_Point_Diameter=.6;

/* [Glyph pipeline lib wiring] */
//Physical_Layout: Layout is in keyboard order; Char_Legend remaps CHARACTER
//SELECTION (same role as Postal/Bennett's map).
Physical_Layout=[for (row=[0:6]) [for (col=[0:11]) Layout[row][Char_Legend[col]]]];
//Element_Diameter, Platen_Diameter, Char_Protrusion, Baseline, Cutout,
//Character_Modifieds*, Typeface_2*, Weight_Adj_*, Scale_Multiplier*, Y_Scale
//all already declared natively above - no bridging needed.
//Baseline_Z_Offset=0: Baseline/Cutout are already absolute heights from the
//bottom face, same convention as Bennett.
Baseline_Z_Offset=0;
//Cyl_Fn/Surface_Fn/Text_Fn/Mink_Fn already declared natively above (Global
//Parameters) - no bridging needed now that Mignon uses the canonical names
//directly instead of its old underscore-style names.
//Mignon's placement radius is the raw Element_Diameter/2 (no protrusion
//added there - embed depth comes from Letter_Extrude_Offset below instead).
Letter_Placement_Protrusion=0;
Letter_Extrude_Offset=-1;
Letter_Extrude_Depth=4;

include <lib/glyph_pipeline.scad>

/* [Core/shaft lib wiring] */
//Mignon's original had no SecondaryCore/CoreGrooves/CoreChamfer/CoreEllipses
//at all - its shaft bore is a plain rotate_extrude() polygon (HollowBody
//below), so lib/core_shaft.scad is NOT included here. Nothing to bridge.

/* [Resin lib wiring] */
//Mignon's own Resin_Support_* knobs, mapped onto the canonical names
//lib/resin_rod.scad's shared ResinRod() expects.
Resin_Rod_OD=Resin_Support_Wire_Thickness;
Resin_Tip_OD=Resin_Support_Contact_Point_Diameter;
//matches the old inline rod's hardcoded 1mm cone tip segment.
Resin_Tip_L=1;
//faithful port: the old inline rod had zero embed/overlap at the tip.
Resin_Inset=0;
//Mignon's raft is its own separate rotate_extrude ring built directly in
//ResinSupport() below (same reasoning as Bennett), so the shared
//primitive's per-rod raft is disabled and its base datum pinned to local
//z=0, matching where Mignon's own raft ring already sits.
Resin_Rod_Raft=false;
Resin_Min_Rod_Height=0;
Resin_Raft_Thickness=0;
Resin_Raft_OD=Resin_Rod_OD; //unused since Resin_Rod_Raft=false, defined for clarity only

include <lib/resin_rod.scad>

 module regular_polygon(order,SomeCylinder_Diameter){
     angles=[ for (i = [0:order-1]) i*(360/order) ];
     coords=[ for (th=angles) [SomeCylinder_Diameter/2*cos(th), SomeCylinder_Diameter/2*sin(th)] ];
     polygon(coords);
 }


//Polygonal Shape
module PolygonCylinder(){
translate([0, 0, -1])
    linear_extrude(Element_Height+6)
    rotate([0,0,360/24])
    regular_polygon(12,Element_Diameter);
}

module ElementChamfer(){
    translate([0,0,Element_Height-Cylinder_Top_Height_Offset-z]){
        //Chamfer Top
        cylinder(d=Cylinder_Top_Diameter, h=Cylinder_Top_Height_Offset+z, $fn=Surface_Fn);
        cylinder(d1=Cylinder_Top_Diameter+Cylinder_Top_Chamfer*2, d2=Cylinder_Top_Diameter, h=Cylinder_Top_Chamfer, $fn=Surface_Fn);
    }
}

module ElementLabel(){
    for (n=[0:len(Cylinder_Label)-1]){
        rotate([0,0,Cylinder_Label_Spacing*n+Cylinder_Label_Offset-(len(Cylinder_Label)-1)*Cylinder_Label_Spacing/2])
        translate([Cylinder_Top_Diameter/2+Cylinder_Top_Chamfer, 0, Element_Height-Cylinder_Top_Height_Offset])
        rotate([45, 0, 90])
        translate([0, Cylinder_Label_Height_Offset, -.05])
        minkowski(){
            linear_extrude(.09)
            text(text=Cylinder_Label[n], size=Cylinder_Label_Size, font=Cylinder_Label_Font, valign="baseline", halign="center");
            if (Mink_On==true)
            scale([1,1,3])
            sphere(r=.05);
        }
    }
}

module CenterShaft(){
    translate([0,0,-z])
        cylinder(h=Element_Height+2*z,d=Cylinder_Top_Shaft_Diameter, $fn=Cyl_Fn);
}


module HollowBody(){
    rotate_extrude($fn=Surface_Fn){//Hollow Out Cylinder
        polygon([[Cylinder_Bottom_Shaft_Diameter/2,0-z],
            [Cylinder_Bottom_Shaft_Diameter/2,Element_Height-Cylinder_Top_Height_Offset-4],
            [Cylinder_Top_Shaft_Diameter/2-z,Element_Height-Cylinder_Top_Height_Offset],
            [0+z,-z]]);
    }
}

module AlignmentPin(){
    rotate([90,0,90]){
        linear_extrude(Cylinder_Bottom_Shaft_Diameter/2+Pin_Depth+(Pin_Through==true?5:0)){//Cut Pin
            union(){
                hull(){
                    circle(d=Pin_Width, $fn=Cyl_Fn);
                    translate([0,Pin_Height-Pin_Width/2])
                    circle(d=Pin_Width, $fn=Cyl_Fn);
                }
            }
        }
    }
}

module ResinSupport(){
$fn=Resin_Fn;
translate([0,0,-Resin_Support_Height+z]){
        rotate_extrude(){
                polygon([[Element_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,Resin_Support_Thickness], [Element_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
            }
            for (n=[0:1:11]){
                r1=(Element_Diameter+Cylinder_Bottom_Shaft_Diameter)/4-.1;
                theta=360/12*n+360/12;
                translate([r1*cos(theta),r1*sin(theta),0])
                ResinRod(Resin_Support_Height+Cylinder_Top_Height_Offset);
                r2=(Cylinder_Top_Shaft_Diameter+Cylinder_Top_Diameter)/4;
                translate([r2*cos(theta+360/24),r2*sin(theta+360/24),0])
                if (n%2==0){
                    ResinRod(Resin_Support_Height);
                }
            }
        }

}

module MinkCleanup(){
translate([0, 0, Element_Height-Cylinder_Top_Height_Offset])
    cylinder(h=10, d=30);
    rotate([180, 0, 0])
    cylinder(h=10, d=30);
}

module Assemble(){
    difference(){
        union(){
            difference(){
                union(){
                    TextRing();
                    if (Cylinder_Shape==0)
                    PolygonCylinder();
                    if (Cylinder_Shape==1)
                    cylinder(d=Element_Diameter, h=Element_Height-Cylinder_Top_Height_Offset, $fn=Surface_Fn);
                }
                MinkCleanup();
            }
            ElementChamfer();
            ElementLabel();
        }
        CenterShaft();
        HollowBody();
        AlignmentPin();
    }
}

module ResinPrint(){
    union(){
        translate([0, 0, Element_Height])
        rotate([0, 180, 0])
        Assemble();
        ResinSupport();
    }

}

//flat readable layout of the whole character set, for checking kerning/
//legibility at print size before generating full element geometry - same
//role as Blickensderfer/Postal's TypeTest.
module TypeTest(){
    Test_Chars=[for (row=[0:len(Layout)-1]) for (col=[0:len(Layout[row])-1]) Layout[row][col]];
    for (n=[0:len(Test_Chars)-1]){
        char=Test_Chars[n];
        charModsMatch=search(char, Character_Modifieds)!=[];
        font=charModsMatch?Character_Modifieds_Font:Font;
        size=charModsMatch?Character_Modifieds_Size:Font_Size;
        baselineOffset=charModsMatch?Character_Modifieds_Offset:0;
        translate([1/Test_CPI*25.4*n, baselineOffset, 0]){
            AlignedText(char, font, size);
            if (Show_Align_Bounds) AlignBoundsBox(25.4/Test_CPI, size*1.5);
        }
    }
}

if (Render==true){

if (Render_Mode==0)
difference(){
    ResinPrint();
    if (X_Section==true)
    rotate([0, 0, X_Section_Theta])
    translate([-50, 0, -50])
    cube(100);
}

if (Render_Mode==1)
TypeTest();

}
