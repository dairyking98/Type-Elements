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
//Glyph Quality, Element Dimensions, Logo, Resin Printing, lib wiring) so all
//four v2 machine files are organized the same way. Sections with no Mignon
//equivalent (Print Tolerances, Shaft Gauge Test, Type Test) are omitted
//rather than left empty.

/* [Global Parameters] */
//to help with z fighting
z=.001;
//surface facet number
surface_fn=360;
//critical (shaft/pin) cylinder facet number
criticalcyl_fn=360;
//resin support facet number
resin_fn=20;
//minkowski facet number
mink_fn=10;
//text facet number
text_fn=44;

/* [Render Parameters] */
//render something? Mignon's original used the older V1 "Assert=true;
//assert(false,...)" gate (per docs/glyph-pipeline.md's V1/V2 pattern note) -
//switched to the same Render=false; boolean gate Bennett/Blick2/Postal use.
Render=false;
XSection=false;
XSectionTheta=180;
//Speedy Preview and Render with No Minkowski
Debug_No_Minkowski=true;//Speedy Preview and Render with No Minkowski
minkOn=!Debug_No_Minkowski;
//Mignon's original cone (r1=.75*6,r2=0,h=6) was never a calibrated dimension -
//uses the shared angle-derived formula instead, same draft angle as Blick2/
//Postal since Mignon never had its own draft-angle concept.
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
//which keyboard the console echo identifies positions against (independent
//of Layout_Selection below - your physical keyboard's key labels don't
//change just because you're test-printing a different language layout).
//Defaults to the same value as Layout_Selection - set this to whichever
//language your actual physical keyboard is labeled in.
referenceLayoutSelection=5; //[0:Custom Layout,1:English 2,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]

/* [Key Mapping] */
CharLegend=[7,8,9,10,11,0,1,2,3,4,5,6];

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
//referencePhysicalLayout: same CharLegend hardware remap as physicalLayout
//below, but built from referenceLayoutSelection - used only by the console
//echo, see lib/glyph_pipeline.scad's header comment.
referenceLayout=Layouts[referenceLayoutSelection];
referencePhysicalLayout=[for (row=[0:6]) [for (col=[0:11]) referenceLayout[row][CharLegend[col]]]];
//Tallen Element? For Plakatschrift. Also Offsets Baselines by Tallen Baseline Offset
Tallen=false;
Tallen_Baseline_Offset=-1.25;
//Row Height
Baseline_Regular=[2.25, 7.55, 12.75, 17.8, 22.8, 28, 32.8];
Baseline_Tallen=Baseline_Regular+[for (n=[0:1:6]) Tallen_Baseline_Offset];
Baseline=Tallen?Baseline_Tallen:Baseline_Regular;
//Platen Cutout Height
Cutout=[2.7, 8.25, 13.6, 18.7, 23.7, 28.7, 33.6];
//latitudeInt negative + angleHalfStep=0: Mignon's Theta=-(360/cols*col) has
//no half-column-step term at all (unlike Blick2/Postal/Bennett).
latitudeInt=-360/len(Layout[0]);
angleHalfStep=0;

/* [Typeface Stuff] */
//Primary font name
Typeface_="Iosevka Etoile";//As Installed on PC
Type_Size=2.45;//[1:.05:10]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
//Character_Modifieds only ever shifted baseline in Mignon's original (no
//font swap - that's the separate Typeface_2Chars system below), so these
//alias to Mignon's own font/size for a no-op swap.
Character_Modifieds_Font=Typeface_;
Character_Modifieds_Size=Type_Size;
//offset()-based stroke weight (Blickensderfer2/Postal's system) - Mignon
//never had this, 0 = no-op, layered independently of Weight_Adj_Mode below.
fontWeightOffset=0;
xFontWeightAdj=0;
yFontWeightAdj=0;
font=Typeface_;
fontSize=Type_Size;

/* [Glyph Quality (unified across all v2 machines)] */
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;//0.01
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//Y Scale Text
Y_Scale=1;
//Secondary font name
Typeface_2="Times new roman";
Type_2Size=2.75;//[1:.05:10]
//Secondary font characters
Typeface_2Chars="";

/* [Element Dimensions] */
//Platen Diameter
Platen_Diameter=26.5;
//Main Cylinder Diameter
Element_Diameter=18.64;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=19.4;
CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
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
//physicalLayout: Layout is in keyboard order; CharLegend remaps CHARACTER
//SELECTION (same role as Postal/Bennett's map).
physicalLayout=[for (row=[0:6]) [for (col=[0:11]) Layout[row][CharLegend[col]]]];
//Element_Diameter, Platen_Diameter, CharProtrusion, Baseline, Cutout,
//Character_Modifieds*, Typeface_2*, Weight_Adj_*, Scale_Multiplier*, Y_Scale
//all already declared natively above - no bridging needed.
//baselineZOffset=0: Baseline/Cutout are already absolute heights from the
//bottom face, same convention as Bennett.
baselineZOffset=0;
//quality variable name bridging (Bennett's underscore-style names)
cylFn=criticalcyl_fn;
surfaceFn=surface_fn;
textFn=text_fn;
minkFn=mink_fn;
//Mignon's placement radius is the raw Element_Diameter/2 (no protrusion
//added there - embed depth comes from letterExtrudeOffset below instead).
letterPlacementProtrusion=0;
letterExtrudeOffset=-1;
letterExtrudeDepth=4;

include <lib/glyph_pipeline.scad>

/* [Core/shaft lib wiring] */
//Mignon's original had no SecondaryCore/CoreGrooves/CoreChamfer/CoreEllipses
//at all - its shaft bore is a plain rotate_extrude() polygon (HollowBody
//below), so lib/core_shaft.scad is NOT included here. Nothing to bridge.

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
        cylinder(d=Cylinder_Top_Diameter, h=Cylinder_Top_Height_Offset+z, $fn=surface_fn);
        cylinder(d1=Cylinder_Top_Diameter+Cylinder_Top_Chamfer*2, d2=Cylinder_Top_Diameter, h=Cylinder_Top_Chamfer, $fn=surface_fn);
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
            if (Debug_No_Minkowski!=true)
            scale([1,1,3])
            sphere(r=.05);
        }
    }
}

module CenterShaft(){
    translate([0,0,-z])
        cylinder(h=Element_Height+2*z,d=Cylinder_Top_Shaft_Diameter, $fn=criticalcyl_fn);
}


module HollowBody(){
    rotate_extrude($fn=surface_fn){//Hollow Out Cylinder
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
                    circle(d=Pin_Width, $fn=criticalcyl_fn);
                    translate([0,Pin_Height-Pin_Width/2])
                    circle(d=Pin_Width, $fn=criticalcyl_fn);
                }
            }
        }
    }
}

module ResinSupport(){
$fn=resin_fn;
translate([0,0,-Resin_Support_Height+z]){
        rotate_extrude(){
                polygon([[Element_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,Resin_Support_Thickness], [Element_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
            }
            for (n=[0:1:11]){
                r1=(Element_Diameter+Cylinder_Bottom_Shaft_Diameter)/4-.1;
                theta=360/12*n+360/12;
                translate([r1*cos(theta),r1*sin(theta),1]){
                    cylinder(h=Resin_Support_Height-2+Cylinder_Top_Height_Offset,d=Resin_Support_Wire_Thickness);
                    translate([0,0,Resin_Support_Height-2+Cylinder_Top_Height_Offset])
                    cylinder(h=1, d2=Resin_Support_Contact_Point_Diameter, d1=Resin_Support_Wire_Thickness);
                }
                r2=(Cylinder_Top_Shaft_Diameter+Cylinder_Top_Diameter)/4;
                translate([r2*cos(theta+360/24),r2*sin(theta+360/24),1]){
                    if (n%2==0){
                        cylinder(h=-2+Resin_Support_Height,d=Resin_Support_Wire_Thickness);
                        translate([0,0,-2+Resin_Support_Height])
                        cylinder(h=1, d2=Resin_Support_Contact_Point_Diameter, d1=Resin_Support_Wire_Thickness);
                    }
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
                    cylinder(d=Element_Diameter, h=Element_Height-Cylinder_Top_Height_Offset, $fn=surface_fn);
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

if (Render==true){

difference(){
    ResinPrint();
    if (XSection==true)
    rotate([0, 0, XSectionTheta])
    translate([-50, 0, -50])
    cube(100);
}

}
