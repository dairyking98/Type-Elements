//Bennett Type Element
//September 14, 2023
//Leonard Chau
//
//v2.0: glyph pipeline unified with Blickensderfer2/Postal's shared
//lib/glyph_pipeline.scad. Bennett's platen-cutout composition looked
//structurally different (nested in the glyph's local frame vs. Blick2's
//independent world-space module) but was numerically verified to be the
//exact same operation, just parameterized differently - solving for Blick2's
//radial/theta/z from Bennett's actual transform gave radial = Element_Diameter
///2 + Platen_Diameter/2 + Char_Protrusion (the same formula shape as Blick2's
//cylOD/2+platenOD/2+textProtrusion) with zero angular offset and platenBaseline
//= Cutout[row] directly, and the resulting cylinder axis matched Bennett's
//original to within floating point. Layout data moved to
//lib/layouts/bennett_layouts.scad (identical content, just relocated).
//Resin support and core/body geometry are Bennett-specific and stay local -
//see docs/refactoring-plan.md and docs/resin-supports.md, neither of which
//found a shareable pattern there. Original preserved at Bennett/BennettElement.scad. This file was BennettElement2.scad, moved to v2/bennett.scad.
//
//Customizer sections below follow Blickensderfer's canonical layout (Global
//Parameters, Render Parameters, Testing Stuff, Key Mapping, Typeface Stuff,
//Glyph Quality, Element Dimensions, Logo, Type Test, Resin Printing, lib
//wiring) so all four v2 machine files are organized the same way. Sections
//with no Bennett equivalent (Print Tolerances, Shaft Gauge Test) are omitted
//rather than left empty.

/* [Global Parameters] */
//to help with z fighting
z=.001;
//minkowski facet number (renamed from mink_fn, to match every other v2 machine)
Mink_Fn=10;
//text facet number (renamed from text_fn)
Text_Fn=10;
//critical (shaft/pin) cylinder facet number (renamed from criticalcyl_fn)
Cyl_Fn=360;
//surface facet number (renamed from surface_fn)
Surface_Fn=120;
//resin support facet number (renamed from resin_fn)
Resin_Fn=20;
//groove facet number
Groove_Fn=40;
//alignment hole facet number (Bennett-only, no shared equivalent - renamed
//from alignmenthole_fn to match every other quality var's camelCase)
Alignment_Hole_Fn=40;

/* [Render Parameters] */
//render something?
Render=false;
//render mode
Render_Mode=0;//[0:Resin Print, 1:Type Test]
//turn minkowski on
Mink_On=false;
//Bennett's original cone (r1=.75,r2=0,h=1) was never a calibrated dimension -
//uses the shared angle-derived formula instead, same draft angle as Blick2/
//Postal since Bennett never had its own draft-angle concept.
Mink_Draft_Angle=55;
//view cross section (reordered after Mink_On/Mink_Draft_Angle to match
//Blick2/Postal's canonical Render Parameters order)
X_Section=false;
X_Section_Theta=180;

/* [Testing Stuff] */
Testing_Baseline=false;
Testing_Cutout=false;
Testing_Layout=false;
//[Lowercase, Uppercase, Figures] Alignment Hole Height Offset - Bennett used
//one shared array for both cutout and baseline sweeps (Blick2 keeps two
//separate arrays; that's a genuine structural difference, not just naming).
Testing_Offsets=[-.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7];
Cutout_Test=Testing_Cutout;
Baseline_Test=Testing_Baseline;
Test_Layout=Testing_Layout;
Cutout_Test_Array=Testing_Offsets;
Baseline_Test_Array=Testing_Offsets;
Test_Char="H";
//which keyboard the console echo identifies positions against (independent
//of Layout_Selection below - your physical keyboard's key labels don't
//change just because you're test-printing a different layout)
Reference_Layout_Selection=0; //[0:English, 1:British, 2:Custom, 3:International]

/* [Key Mapping] */
Char_Legend=[12,22,3,11,21,2,10,20,1,9,19,0,8,18,27,17,7,26,16,6,25,15,5,24,14,4,23,13];

//Custom Layout As Seen on Keyboard. Left to Right, Top to Bottom
Lowercase="qweruiopasdftyjkl,zxcvghbnm.";
Uppercase="QWERUIOPASDFTYJKL,ZXCVGHBNM.";
Figs="12347890\"#$%56;?:,£@_(&-)/'.";
CUSTOMLAYOUT=[Lowercase,Uppercase,Figs];
include <lib/layouts/bennett_layouts.scad>

//Layout Selection
Layout_Selection=0; //[0:English, 1:British, 2:Custom, 3:International]
Layout=LAYOUTS[Layout_Selection];
//Reference_Physical_Layout: same Char_Legend hardware remap as Physical_Layout
//below, but built from Reference_Layout_Selection - used only by the console
//echo, see lib/glyph_pipeline.scad's header comment.
Reference_Layout=LAYOUTS[Reference_Layout_Selection];
Reference_Physical_Layout=[for (row=[0:2]) [for (col=[0:27]) Reference_Layout[row][Char_Legend[col]]]];
//[Lowercase, Uppercase, Figures] Row Height
Baseline=[14.9,9.2,2.95];//[-1:.05:1][14.95,8.8,2.35]
///baseline defaults before: [15.25,9.1,2.65]
//[Lowercase, Uppercase, Figures] Platen Cutout Height
Cutout=[16.15,10.35,4.35];//[-1:.05:1][16.35,10.65,4.5]
//Latitude_Int negative: Bennett's Theta=-(360/cols*col+360/(2*28)) is exactly
//Blick2's (.5+col)*Latitude_Int formula with a negated Latitude_Int (both reduce
//to the same 360/56 half-column-step magnitude) - verified numerically
//alongside the platen-cutout check (thetaOffset came back exactly 0).
Latitude_Int=-360/28;

/* [Typeface Stuff] */
//Typeface
Typeface_="Average Mono";
Type_Size=3.00;//[1:.05:10]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=.1;//[-1.5:.05:1.5]
//Character_Modifieds only ever shifted baseline in Bennett's original (no
//Font swap), so these alias to Bennett's own Font/size for a no-op swap.
Character_Modifieds_Font=Typeface_;
Character_Modifieds_Size=Type_Size;
//offset()-based stroke weight (Blickensderfer2/Postal's system) - Bennett
//never had this, 0 = no-op, layered independently of Weight_Adj_Mode below.
Font_Weight_Offset=0;
X_Font_Weight_Adj=0;
Y_Font_Weight_Adj=0;
Font=Typeface_;
Font_Size=Type_Size;

/* [Glyph Quality (unified across all v2 machines)] */
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//vertical glyph scale before extrusion - Bennett never had this, 1 = no-op.
Y_Scale=1;
//secondary typeface for specific characters - Bennett never had this.
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
Element_Diameter=31.9;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=32.9;
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//Element Height
Element_Height=18;
//Shaft Diameter
Shaft_Diameter=3.4;
//Element Positioner Pin Diameter
Element_Positioner_Pin_Diameter=2.5;
//Element Positioner Pin - Radial Position
Element_Positioner_Pin_Radius=4.813;
//Indicator Hole Diameter
Indicator_Diameter=2.2;
//Alignment Pin Hole Diameter
Alignment_Hole_Diameter=1.8;//.1
//1.94 a kiss too tight, bumping to 2.0
//Alignment Hole Depth
Alignment_Hole_Depth=2.4;
//Alignment Hole Chamfer Size
Alignment_Hole_Chamfer=.3;//.01
//Speed Hole Diameter
Speed_Hole_Diameter=6.1;
//Speed Hole - Radial Position
Speed_Hole_Radius=10.801;
//Number of Speed Holes
Speed_Hole_Quantity=8;
//Countersink Diameter
Countersink_Diameter=23.4;
//Top Countersink Depth
Top_Countersink_Depth=.7;
//Bottom Countersink Depth
Bottom_Countersink_Depth=0.5;//.01
//Minimum Cylinder Thickness
Shell_Size=1;
//Radius of Inside Corners
Inside_Radius=.5;
//core groove qty
Core_Groove_Qty=16;
//core groove diameter
Core_Groove_D=.6;
//core chamfer
Core_Chamfer=.5;
//core bottom offset from bottom plane
Core_Bottom_Offset=0;
//core contact length from ends where sliding fits occur for shaft to reduce friction
Core_Contact_Length=4;
//core web width
Core_Web_Width=2;
//core web hole quantity
Core_Web_Qty=3;
//core web length
Core_Web_Length=6;
//secondary core with larger diameter to focus friction at ends of shaft hole along core contact lengths
Core_Secondary_ID_Offset=Core_Groove_D/2+z;
//[Lowercase, Uppercase, Figures] Alignment Hole Height
Alignment_Hole=[13.19,7,1.19];//.01;
//[-1:.05:1]
//small fudge-factor constant used by the core/shaft taper landmarks below -
//must be defined before use since OpenSCAD evaluates top-level (non-module)
//assignments in file order, not whole-file lookahead like module bodies get.
s=.2;

/* [Type Test] */
//characters per inch for the flat type-test string
Test_CPI=10;
//thin semi-transparent frame around each character's window (25.4/Test_CPI
//wide), so ink position can be checked against the slot - preview (F5) only
Show_Align_Bounds=false;

/* [Logo] */
//Shuttle Label 1
Shuttle_Label1a="Leonard";
Shuttle_Label1b="Chau";
//Shuttle Label 2
Shuttle_Label2="2025";
//Shuttle Label Size
Shuttle_Label_Size=1.7;
//Shuttle Label Font
Shuttle_Label_Font="Courier New:style=bold";
//Shuttle Label Extrusion Deptth
Shuttle_Label_Depth=.2;

/* [Resin Printing] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.2;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=1;//.001
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=1;
Resin_Support_Contact_Point_Diameter=.7;
Resin_Support_Buildplate_Diameter=1.2;
Pyramidzoffset=1/cos(atan(2/Countersink_Diameter));

/* [Glyph pipeline lib wiring] */
//Physical_Layout: Layout is in keyboard order; Char_Legend remaps CHARACTER
//SELECTION (same role as Postal's elementLayoutArrayMap) - bake that in so
//the lib receives characters already in physical column order.
Physical_Layout=[for (row=[0:2]) [for (col=[0:27]) Layout[row][Char_Legend[col]]]];
//Element_Diameter, Platen_Diameter, Char_Protrusion, Baseline, Cutout,
//Character_Modifieds*, Weight_Adj_*, Scale_Multiplier*, Y_Scale, Typeface_2*
//all already declared natively above - no bridging needed (the lib reads
//these canonical names directly).
//Baseline_Z_Offset=0: Bennett's Baseline/Cutout are already absolute heights
//from the bottom face (unlike Blick2/Postal's negative-from-clip-end
//convention), so this shift must be a no-op here.
Baseline_Z_Offset=0;
//row names for TextRingDebug's console output (Cutout_Test/Baseline_Test/Test_Layout)
Row_Labels=["lowercase", "uppercase", "figs"];
//Cyl_Fn/Surface_Fn/Text_Fn/Mink_Fn already declared natively above (Global
//Parameters) - no bridging needed now that Bennett uses the canonical names
//directly instead of its old underscore-style names.
//Bennett's placement radius is the raw Element_Diameter/2 (no protrusion
//added there - embed depth comes from Letter_Extrude_Offset below instead).
Letter_Placement_Protrusion=0;
//Bennett's raw pre-cutout extrusion block, trimmed down by the (verified)
//PlatenCutout afterward.
Letter_Extrude_Offset=-.5;
Letter_Extrude_Depth=2;

include <lib/glyph_pipeline.scad>

/* [Core/shaft lib wiring] */
//Shaft_Diameter already declared natively above - no bridging needed.
//Core_Top_Z/Core_Bottom_Z: Bennett's absolute top/bottom landmarks (no clip, so
//unlike Blick2/Postal, Core_Taper_Top_Z is left undefined - it defaults to
//Core_Top_Z, exactly matching Bennett's original polygon which used a single
//landmark for all of SecondaryCore's upper points).
Core_Top_Z=Element_Height-Top_Countersink_Depth-1+s;
Core_Bottom_Z=Bottom_Countersink_Depth;
//Core_Chamfer_Top=false: Bennett's original CoreChamfer had no top chamfer call
//at all (commented out - no clip to chamfer under).
Core_Chamfer_Top=false;

include <lib/core_shaft.scad>

/* [Resin lib wiring] */
//Bennett's own Resin_Support_* knobs, mapped onto the canonical names
//lib/resin_rod.scad's shared ResinRod() expects.
Resin_Rod_OD=Resin_Support_Wire_Thickness;
Resin_Tip_OD=Resin_Support_Contact_Point_Diameter;
//matches the old local ResinRod's hardcoded 1mm cone taper segment.
Resin_Tip_L=1;
//faithful port: the old local ResinRod centered its tip sphere AT z=h
//(translate([0,0,h]) sphere(d=dc)), so the sphere's actual apex sat at
//h+dc/2, not h - matching that requires an inset of exactly dc/2 here
//(the lib's apex is at h+Resin_Inset).
Resin_Inset=Resin_Support_Contact_Point_Diameter/2;
//Bennett's own big raft/groove ring in ResinSupport() below only reaches
//the outer edge (Element_Diameter/2) - the middle and inner rod rings sit
//much closer to center and never touch it. The old local ResinRod gave
//every rod its own small base flare (hardcoded d1=2.4, tapering to
//d2=1.2+2*Resin_Support_Thickness) for exactly this reason - disabling it
//during the migration (assuming the big ring covered everything) was wrong
//and left the middle/inner rods with no raft at all. Restored, using
//Resin_Support_Thickness (already an exposed Bennett parameter) for the
//taper instead of the old formula's disconnected literal - same idea, a
//couple tenths of a mm different at the default thickness, immaterial for
//a print support's actual job.
Resin_Rod_Raft=true;
Resin_Raft_OD=2.4;
//lib's raft cylinder spans [-Min_Rod_Height-Raft_Thickness, -Min_Rod_Height] -
//the old local ResinRod's raft (and the big outer "Create Raft" ring right
//below) both sit at local z=[0, Resin_Support_Thickness], ABOVE the
//datum, not below it. Min_Rod_Height=0 (tried first) put the per-rod raft
//at z=[-thickness, 0] instead - the wrong side of z=0, not coplanar with
//the outer ring. Min_Rod_Height=-Resin_Raft_Thickness cancels that out so
//the raft spans [0, Resin_Support_Thickness], matching both.
Resin_Raft_Thickness=Resin_Support_Thickness;
Resin_Min_Rod_Height=-Resin_Raft_Thickness;

include <lib/resin_rod.scad>

module Cylinder(){
    cylinder(h=Element_Height,d=Element_Diameter, $fn=Surface_Fn);
}

module PositionerPins(){
    for (n=[0:1:1]){
        theta=180*n+90;
        translate([Element_Positioner_Pin_Radius*cos(theta),Element_Positioner_Pin_Radius*sin(theta),-z]){
        cylinder(h=Element_Height+2*z,d=Element_Positioner_Pin_Diameter, $fn=Cyl_Fn);

        //lil chamfer to clean up post print booger that drags on alignment pins
        translate([0, 0, Bottom_Countersink_Depth+Shell_Size])
        cylinder(h=2,d1=Element_Positioner_Pin_Diameter, d2=Element_Positioner_Pin_Diameter+1, $fn=Cyl_Fn);
        }
    }
}
Asd=1;
Drop=.5;
module HollowBody(){
    RoofSlope=1/(Countersink_Diameter/2);
    XArray=[Shaft_Diameter/2+Shell_Size+Core_Secondary_ID_Offset, Shaft_Diameter/2+Shell_Size+Core_Secondary_ID_Offset+Asd, ((Element_Diameter/2-Shell_Size)+(Shaft_Diameter/2+Shell_Size+Core_Secondary_ID_Offset))/2, Element_Diameter/2-Shell_Size-Asd, Element_Diameter/2-Shell_Size];
    YArray=[Bottom_Countersink_Depth+Shell_Size, Bottom_Countersink_Depth+Shell_Size+Drop, Bottom_Countersink_Depth+Shell_Size+Drop+Asd, Element_Height-Top_Countersink_Depth-Shell_Size-Asd, Element_Height-Top_Countersink_Depth-Shell_Size, Element_Height-Top_Countersink_Depth-Shell_Size-Asd-RoofSlope*(Countersink_Diameter/2-XArray[0]), Element_Height-Top_Countersink_Depth-Shell_Size-RoofSlope*(Countersink_Diameter/2-XArray[0])];
    XYPattern=[[0, 2], [0, 5], [1, 6], [3, 4], [4, 3], [4, 2], [3, 1], [2, 0], [1, 1]];
    polygonpath=[for (n=[0:len(XYPattern)-1]) [XArray[XYPattern[n][0]], YArray[XYPattern[n][1]]]];
    rotate_extrude($fn=Surface_Fn){
        polygon(polygonpath);
    }
}

module AlignmentHoles(){
    for (row=[0:1:len(Layout)-1]){
        for (n=[0:1:len(Layout[0])-1]){
            theta=-(360/(len(Layout[0]))*n+360/(2*28));
            translate([(Element_Diameter)/2*cos(theta),(Element_Diameter)/2*sin(theta),Alignment_Hole[row]])
            rotate([0,-90,theta]){
                cylinder(h=Alignment_Hole_Depth-Alignment_Hole_Diameter/2,d=Alignment_Hole_Diameter, $fn=Alignment_Hole_Fn);
                hull(){
                    translate([0, 0, Alignment_Hole_Chamfer])
                    cylinder(h=z, d=Alignment_Hole_Diameter, $fn=Alignment_Hole_Fn);
                    translate([0, 0, -1])
                    scale([1, (Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer)/Alignment_Hole_Diameter, 1])
                    cylinder(h=1, d=Alignment_Hole_Diameter, $fn=Alignment_Hole_Fn);
                }
            }
            translate([((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*cos(theta),((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*sin(theta),Alignment_Hole[row]])
            sphere(d=Alignment_Hole_Diameter, $fn=Alignment_Hole_Fn);
        }
    }
}

module LabelText(){
    translate([Shaft_Diameter/2+1.5+.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, 90])
    linear_extrude(2){
    text(text=Shuttle_Label1b, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");
    translate([0, 2.25, 0])
    text(text=Shuttle_Label1a, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");

    }
    translate([-Shaft_Diameter/2-1.75-.5, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, 90])
    linear_extrude(2)
    text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");

}

module SpeedHoles(){
    translate([0, 0, -z])
    for (n=[0:1:7]){
        theta=360/Speed_Hole_Quantity*n+360/(Speed_Hole_Quantity*2);
        translate([Speed_Hole_Radius*cos(theta),Speed_Hole_Radius*sin(theta),0])
        cylinder(h=Element_Height+2*z,d=Speed_Hole_Diameter, $fn=Surface_Fn);
    }
}

module MinkCleanup(){
    translate([0,0,Element_Height])
    cylinder(h=5,d=Element_Diameter+5, $fn=20);
    rotate([180, 0, 0])
    cylinder(h=5,d=Element_Diameter+5, $fn=20);
}

module CenterShaft(){
    translate([0, 0, -z])
    cylinder(h=Element_Height+2*z,d=Shaft_Diameter, $fn=Cyl_Fn);
}

module TopCountersink(){
    translate([0,0,Element_Height-Top_Countersink_Depth])
    cylinder(h=Top_Countersink_Depth+z,d=Countersink_Diameter, $fn=Surface_Fn);
}

module BottomCountersink(){
    translate([0, 0, -z])
    cylinder(h=Bottom_Countersink_Depth+z,d=Countersink_Diameter, $fn=Surface_Fn);
}

module RoofTaper(){
    if (Generate_Support==true)
    translate([0, 0, Element_Height-Top_Countersink_Depth-1])
    cylinder(h=1+z, d2=Countersink_Diameter, d1=0, $fn=Surface_Fn);
}


module IndicatorHole(){
    translate([Element_Diameter/2-Shell_Size-Indicator_Diameter/2,0,Element_Height-Top_Countersink_Depth-Shell_Size-z-1])
    cylinder(h=5,d=Indicator_Diameter, $fn=Surface_Fn);
}

module ResinSupport(){
$fn=Resin_Fn;
    translate([0,0,-Resin_Support_Height+z]){
        difference(){
            //Create Ring
            translate([0, 0, .5])
            cylinder(d=Element_Diameter, h=Resin_Support_Height-.5, $fn=Surface_Fn);
            translate([0,0,-z])
            cylinder(h=Resin_Support_Height+2*z, r=Element_Diameter/2-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=Surface_Fn);
            //Cut Groove
            rotate_extrude($fn=Surface_Fn){
                translate([Element_Diameter/2,Resin_Support_Height-Resin_Support_Cut_Groove_Diameter/2])
                circle(r=Resin_Support_Cut_Groove_Diameter/2);
            }
        }
        //Create Raft
        rotate_extrude($fn=Resin_Fn){
            polygon([[Element_Diameter/2,0], [Element_Diameter/2-Resin_Support_Thickness,0], [Element_Diameter/2-Resin_Support_Thickness,Resin_Support_Thickness], [Element_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
        }
        //Create Outer 2 Rings of 8 Supports
        for (n=[0:1:7]){
            theta=360/8*n;
            translate([(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*cos(theta),(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*sin(theta),0]){
            ResinRod (Resin_Support_Height);
            }
            translate([Countersink_Diameter*cos(theta)/3,Countersink_Diameter*sin(theta)/3,0]){
            ResinRod (Resin_Support_Height+Pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Countersink_Diameter/3));
            }
        }
        //Create Inner Ring of 4 Supports
        for (n=[0:1:3]){
            theta=90*n;
            translate([(Shaft_Diameter/2+1)*cos(theta),(Shaft_Diameter/2+1)*sin(theta),0]){
                ResinRod (Resin_Support_Height+Pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Shaft_Diameter/2+1));
            }
        }
    }
}

//SecondaryCore, CoreGrooves, CoreChamferShape, CoreChamfer, CoreEllipses now
//come from lib/core_shaft.scad (included above). s is defined earlier now,
//alongside the Core_Top_Z bridging that needs it.

module Assemble(){
    difference(){
        union(){
            Cylinder();
            TextRing();
        }
        PositionerPins();
        HollowBody();
        AlignmentHoles();
        LabelText();
        SpeedHoles();
        MinkCleanup();
        CenterShaft();
        TopCountersink();
        BottomCountersink();
        RoofTaper();
        IndicatorHole();
        SecondaryCore(0);
        CoreGrooves(0);
        CoreChamfer(0);
        CoreEllipses();
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
