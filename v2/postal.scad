//Postal Typewriter Element
//File Start Jan 02 2025
//Leonard Chau
//www.leonardchau.com

//Modeled off a Model 3 Postal, SN 14550
//
//v2.0: glyph pipeline extracted to lib/glyph_pipeline.scad. See
//docs/refactoring-plan.md. Original preserved at Postal/Postal.scad. This file was Postal2.scad, moved to v2/postal.scad.

/* [Global Parameters] */
//to help with z fighting
z=.01;
//minkowski facet number
Mink_Fn=20;
//text facet number
Text_Fn=20;
//cylinder facet number
Cyl_Fn=360;
//surface facet number
Surface_Fn=120;
//resin support facet number
Resin_Fn=20;
//groove facet number
Groove_Fn=20;

/* [Render Parameters] */
//render something (renamed from render, to match every other v2 machine)
Render=false;
//render mode
Render_Mode=0;//[0:Normal, 1:Resin print, 2:Gauge Set, 3:Type Test]
//turn minkowski on
Mink_On=false;
//draft angle
Mink_Draft_Angle=55;
//turn off core grooves (slow)
Render_Core_Groove=true;
//view cross section (renamed from xSection)
X_Section=false;
//cross section angle (renamed from xSectionTheta)
X_Section_Theta=270;

/* [Testing Stuff] */
include <lib/testing.scad>
//enable cutout test
Cutout_Test=false;
//cutout test range start
Cutout_Test_Start=.7;//.1
//cutout test interval
Cutout_Test_Int=-.05;
//cutout test array
Cutout_Test_Array=testSweepArray(Cutout_Test_Start, Cutout_Test_Int, 28);
//enable baseline test
Baseline_Test=false;
//baseline test offset range start
Baseline_Test_Start=0;
//baseline test interval
Baseline_Test_Int=.05;
//baseline test array
Baseline_Test_Array=testSweepArray(Baseline_Test_Start, Baseline_Test_Int, 28);
//enable test layout
Test_Layout=false;
//test character
Test_Char="l";

/* [Key Mapping] */
//layout for keyboard
Keyboard_Layout_Array=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
//keyboard to element map
Element_Layout_Array_Map=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];
//baseline values for characters from top of element
Baseline=[-3.6, -10, -15.7];
//baseline values for platen cutouts from top of element
Cutout=[-2.65, -9.1, -14.5];//.05
//latitude spacing
Latitude_Int=360/28;

/* [Typeface Stuff] */
//element typeface
Font="Alma Mono";
//type size
Font_Size=2.4;
//Font weight offset +/-
Font_Weight_Offset=0;
//Font x weight adjustment 0+
X_Font_Weight_Adj=0;
//Font y weight adjustment 0+
Y_Font_Weight_Adj=0;

/* [Glyph Quality (unified across all v2 machines)] */
//per-character baseline offset + Font/size override (Postal originally had
//no such system - Character_Modifieds="" means it never matches, a no-op)
Character_Modifieds="";
Character_Modifieds_Offset=0;
Character_Modifieds_Font="Alma Mono";
Character_Modifieds_Size=2.4;
//minkowski erosion/growth stroke-weight system, independent of and layered
//with Font_Weight_Offset/X_Font_Weight_Adj/Y_Font_Weight_Adj above.
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//per-character size override (e.g. make "." larger)
Scale_Multiplier_Text="";
Scale_Multiplier=1.0;
//vertical glyph scale before extrusion
Y_Scale=1;
//secondary typeface for specific characters
Typeface_2="Alma Mono";
Type_2_Size=2.4;
Typeface_2_Chars="";
//horizontal alignment method for TwoDText/AlignedText, see docs/text-centering.md.
//Methods 1/2 require OpenSCAD's "Text Metrics" experimental feature enabled
//(Preferences>Features, or --enable=textmetrics) - without it this silently
//renders unshifted, no error.
Text_Align_Method=0;//[0:Advance Center (native), 1:Ink Center, 2:Ink Left (fixed CPI pitch)]
//universal fine-tune nudge (mm), layered on top of whichever method above is selected
Text_Align_X_Offset=0;

/* [Element Dimensions] */
//OD of platen
Platen_Diameter=31.9;
//OD of element at non-text section
Element_Diameter=32.8;
//OD of element between two characters (minimum distance in concave section)
Min_Final_Character_Diameter=34.1;
//minimum text protrustion distance
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//element height/thickness
Element_Height=17.4;
//minimum wall thickness of element
Wall_Min_Thickness=1.5;
//inside wall chamfer size
Wall_Chamfer=.5;
//roof center height offset to reduce pulling forces when printing (reduces past min wall thickness)
Roof_Offset=.5;
//speed hole diameter
Speed_Hole_ID=5.2;
//speed hole quantity
Speed_Hole_Qty=8;
//speed hole radial distance
Speed_Hole_Radial=10.3;
//core ID in inches
Core_ID_In=.125;
Core_ID_Mm=Core_ID_In*25.4;
//core groove qty
Core_Groove_Qty=16;
//core groove diameter
Core_Groove_D=.6;
//core chamfer
Core_Chamfer=.5;
//core bottom offset from bottom plane
Core_Bottom_Offset=1;
//core contact length from ends where sliding fits occur for shaft to reduce friction
Core_Contact_Length=4;
//core web width
Core_Web_Width=2;
//core web hole quantity
Core_Web_Qty=3;
//core web length
Core_Web_Length=7;
//secondary core with larger diameter to focus friction at ends of shaft hole along core contact lengths
Core_Secondary_ID_Offset=Core_Groove_D/2+z;
//height of top clip section
Clip_Height=3;
//clip wire diameter
Clip_Wire_OD=.554;
//clip opening distance
Clip_Opening=1;
//amount of bite for the clip from shaft diameter
Clip_Bite=.7;
//drive pin width
Drive_Pin_Widthmm=2.5;
//drive pin length
Drive_Pin_Length=3.6;
//drive pin square hole radial distance (center of square)
Drive_Pin_Radial=11.5;

/* [Logo] */
//Logo Offset From Pin (Degrees)
Logo_Position_Offset=180;
//Logo Text Orientation
Logo_Text_Offset=180;
//Logo Text
Logo_Text="Leonard Chau 2025";
//Logo Size
Logo_Text_Size=3;
//Logo Font
Logo_Font="FreeMono:style=Bold";
Logo_Text_Spacing=10;
Logo_Radius=Element_Diameter/2-2.0;

/* [Print Tolerances] */
//adds this much mm to the minor diameter of the elements shaft
Core_ID_Offset=.20;//.001
Shaft_Diameter=Core_ID_Mm+Core_ID_Offset;
Drive_Pin_Width=Drive_Pin_Widthmm+Core_ID_Offset;

/* [Shaft Gauge Test] */
Gauge_Offset_Start=.2;//.001
Gauge_Offset_Int=.02;

/* [Type Test] */
Test_String="Alma Mono";
Test_Size=3;//.01
Test_Font="Alma Mono";
Test_CPI=10;
//thin semi-transparent frame around each character's window (25.4/Test_CPI
//wide), so ink position can be checked against the slot - preview (F5) only
Show_Align_Bounds=false;

/* [Resin Printing] */
//resin support enable
Resin_Support=true;
//resin rod diameter
Resin_Rod_OD=1;
//resin tip diameter
Resin_Tip_OD=.6;
//resin tip length
Resin_Tip_L=1;
//resin rod inset in part
Resin_Inset=.3;
//resin rod minimum height
Resin_Min_Rod_Height=2;
//resin rod base diameter
Resin_Raft_OD=4;
//resin rod raft thickness
Resin_Raft_Thickness=2;
//resin cut groove diameter
Resin_Groove_OD=.8;
//resin cut groove min thickness
Resin_Groove_Thickness=.3;

//OD top clip section
Clip_OD=Shaft_Diameter+2*Wall_Min_Thickness;

/* [Glyph pipeline lib wiring] */
//Keyboard_Layout_Array is in KEYBOARD order; Element_Layout_Array_Map here remaps
//CHARACTER SELECTION (not placement, unlike Blickensderfer2) - bake that
//into Physical_Layout so the lib receives characters already in physical
//column order, matching what the original AssembleMinkowski produced.
Physical_Layout=[for (row=[0:2]) [for (col=[0:27])
    Keyboard_Layout_Array[row][Element_Layout_Array_Map[col]]
]];
//No Placement_Map override: Postal places column N at raw latitude N (the lib
//defaults Placement_Map to identity when left undefined).
//No Row_Font/Row_Font_Size/charMods: Postal never had a per-row or per-char Font
//override system, so the lib's single global Font/Font_Size defaults apply.

//Postal's original Text() set $fn=Mink_Fn locally (Blickensderfer2's didn't);
//preserve that per-machine behavior via the lib's Text_2D_Fn hook.
Text_2D_Fn=Mink_Fn;
//Baseline_Z_Offset: Postal's Baseline/Cutout arrays are negative-from-clip-end,
//so this shifts every character placement to an absolute height.
Baseline_Z_Offset=Element_Height;
//row names for TextRingDebug's console output (Cutout_Test/Baseline_Test/Test_Layout)
Row_Labels=["lowercase", "uppercase", "figs"];

include <lib/glyph_pipeline.scad>

//Postal's CutGroove polygon originally extended to the element's center axis,
//forming one continuous raft plate shared by every support rod - so its
//ResinRod()s grow no individual raft of their own (Blick2's did).
Resin_Rod_Raft=false;
Cut_Groove_Inner_X=-Element_Diameter/2+Wall_Min_Thickness;
//Postal's original BottomSupports placed 5 rods per sector (a to b inclusive,
//quarter steps) with the near-core rod at the un-offset sector angle.
Bottom_Support_Fractions=[0, .25, .5, .75, 1];
Bottom_Support_Inner_Angle_Offset=0;

include <lib/resin_support.scad>

/* [Core/shaft lib wiring] */
//Shaft_Diameter already declared natively above - no bridging needed.
Core_Top_Z=Element_Height+Clip_Height;
Core_Bottom_Z=Core_Bottom_Offset;
Core_Taper_Top_Z=Element_Height;
//Core_Chamfer_Top defaults to true, matching Postal's two-sided chamfer.

include <lib/core_shaft.scad>

//main cylinder
module Cylinder(){
    cylinder(d=Element_Diameter, h=Element_Height, $fn=Cyl_Fn);
}

module ClipCylinder(Offset){
    translate([0, 0, Element_Height-z])
    cylinder(d=Clip_OD+Offset, h=Clip_Height+z, $fn=Surface_Fn);
}

module WireBite(){
    $fn=Surface_Fn;
    rotate([0, 0, -90])
    translate([Shaft_Diameter/2-Clip_Bite, Clip_OD/2+z, Element_Height])
    rotate([90, 0, 0])
    linear_extrude(Clip_OD+2*z)
    hull(){
        translate([Clip_Wire_OD/2, Clip_Wire_OD/2])
        circle(d=Clip_Wire_OD);
        translate([Clip_Bite+(Clip_OD-Shaft_Diameter)/2, 0])
        square([z, Clip_Opening]);
    }
}

module Core(Offset){
    translate([0, 0, -z])
    cylinder(d=Shaft_Diameter+Offset, h=Element_Height+Clip_Height+2*z, $fn=Cyl_Fn);
}

//SecondaryCore, CoreGrooves, CoreChamferShape, CoreChamfer, CoreEllipses now
//come from lib/core_shaft.scad (included above).

module SpeedHoles(){
    for (n=[0:Speed_Hole_Qty-1])
    rotate([0, 0, 360/Speed_Hole_Qty*n])
    translate([Speed_Hole_Radial, 0, -z+(n==0?Element_Height/2:0)])
    cylinder(d=Speed_Hole_ID, h=Element_Height+2*z, $fn=Surface_Fn);
}

module HollowSpace(){
    $fn=Surface_Fn;
    rotate_extrude(){
        polygon([[Shaft_Diameter/2+Wall_Min_Thickness, Wall_Min_Thickness+Wall_Chamfer+Core_Bottom_Offset], [Shaft_Diameter/2+Wall_Min_Thickness, Element_Height-Wall_Min_Thickness-Wall_Chamfer], [Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer, Element_Height-Wall_Min_Thickness], [(Shaft_Diameter+Element_Diameter)/4, Element_Height-Wall_Min_Thickness+Roof_Offset], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, Element_Height-Wall_Min_Thickness], [Element_Diameter/2-Wall_Min_Thickness, Element_Height-Wall_Min_Thickness-Wall_Chamfer], [Element_Diameter/2-Wall_Min_Thickness, Wall_Min_Thickness+Wall_Chamfer], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, Wall_Min_Thickness], [Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer, Wall_Min_Thickness+Core_Bottom_Offset]]);
    }
}

module BottomSlopedSpace(){
    $fn=Surface_Fn;
    rotate_extrude(){
        polygon([[0, -z-5], [0, Core_Bottom_Offset], [bottomX(Core_Bottom_Offset), Core_Bottom_Offset], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, -z], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer+5, -z], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer+5, -z-5]]);
    }
}

module TopMinkCleanup(){
    translate([0, 0, Element_Height]){
        difference(){
            cylinder(d=Element_Diameter, h=5);
            cylinder(d=Element_Diameter-15, h=15, center=true);
        }
    }
}

module DrivePin(Offset){
linear_extrude(5)
    translate([Drive_Pin_Radial, 0, -z])
    rotate([0, 0, 90])
    square([Drive_Pin_Width, Drive_Pin_Length], center=true);
}

module LogoText(){
    for (n=[0:len(Logo_Text)-1]){
            rotate([0,0,Logo_Position_Offset-90+Logo_Text_Spacing*n-(len(Logo_Text)-1)*Logo_Text_Spacing/2])

            translate([0, Logo_Radius+1.5, Element_Height-.3])
            linear_extrude(.4)
            rotate([0, 0, Logo_Text_Offset])
            text(text=Logo_Text[n], size=Logo_Text_Size, font=Logo_Font, valign="baseline", halign="center", $fn=Text_Fn);
    }
}

module Additive(){
    union(){
        color("red")
        TextRing();
        Cylinder();
        ClipCylinder(0);
    }
}

module Subtractive(){
    union(){
        Core(0);
        if (Render_Core_Groove==true) CoreGrooves(0);
        CoreChamfer(0);
        WireBite();
        SpeedHoles();
        HollowSpace();
        DrivePin();
        BottomSlopedSpace();
        SecondaryCore(0);
        CoreEllipses();
        TopMinkCleanup();
        LogoText();
    }
}

module FullElement(){
    difference(){
        Additive();
        Subtractive();
    }
}

//ResinRod, CutGroove, SpeedHoleSupport(s), BottomSupports, bottomZ/bottomX now
//come from lib/resin_support.scad (included above, with Postal's raft/groove
//overrides set there). DrivePinSupport is generic there (radius, halfExtentX,
//halfExtentY) - Postal's rectangular footprint maps directly onto it.
module ResinSupport(){
    union(){
        CutGroove();
        SpeedHoleSupports();
        DrivePinSupport(Drive_Pin_Radial, Drive_Pin_Length/2, Drive_Pin_Width/2);
        BottomSupports();
    }
}

module CylinderGauge(Offset){
    translate([0, 0, Core_Bottom_Offset])
    cylinder(d=Shaft_Diameter+2*Wall_Min_Thickness+Offset, h=Element_Height+Clip_Height-Core_Bottom_Offset, $fn=Surface_Fn);
}

module GaugeResinSupport(Offset){
    $fn=Resin_Fn;
    for (n=[0:7]){
        rotate([0, 0, n*360/8])
        translate([Shaft_Diameter/2+Offset/2+Wall_Min_Thickness/2, 0, 0])
        ResinRod(Core_Bottom_Offset);
    }
}

module GaugeResinSupportsRaft(){
    translate([0, 0, -Resin_Min_Rod_Height-Resin_Raft_Thickness])
    cylinder(d1=3*(Shaft_Diameter+2*Wall_Min_Thickness), d2=3*(Shaft_Diameter+2*Wall_Min_Thickness)+2*Resin_Raft_Thickness, h=Resin_Raft_Thickness);
}

module RevolverSolid(){
    $fn=Surface_Fn;
    hull(){
        for (n=[0:5])
        rotate([0, 0, n*360/6])
        translate([Shaft_Diameter+Wall_Min_Thickness*2-Wall_Min_Thickness/2, 0, 0])
        CylinderGauge(0);
    }

}

module GaugeTestSubtractive(Offset){
    Core(Offset);
    if (Render_Core_Groove==true) CoreGrooves(Offset);
    CoreChamfer(Offset);
    SecondaryCore(Offset);
    echo (str(Offset));
    GaugeText(Offset);
    rotate([0, 0, 180])
    CoreEllipses();
}

module GaugeText(Offset){
    if (Offset!=0)
    translate([Shaft_Diameter/2+Wall_Min_Thickness-Wall_Min_Thickness/2+Core_Secondary_ID_Offset/2, 0, Core_Bottom_Offset+(Element_Height+Clip_Height-Core_Bottom_Offset)/2])
    rotate([0, 90, 0])
    linear_extrude(4)
    text(text=str(Offset), halign="center", valign="center", $fn=Text_Fn, size=3, font="Consolas");
}

module GaugeTestSet(){
    union(){
        difference(){
            difference(){
                RevolverSolid();
                GaugeTestSubtractive(0);
            }
            for (n=[0:5]){
                rotate([0, 0, n*360/6])
                translate([Shaft_Diameter+Wall_Min_Thickness*2-Wall_Min_Thickness/2, 0, 0])
                GaugeTestSubtractive(Gauge_Offset_Start+(n)*Gauge_Offset_Int);
            }
        }

        union(){
            for (n=[0:5]){
                rotate([0, 0, n*360/6])
                translate([Shaft_Diameter+Wall_Min_Thickness*2-Wall_Min_Thickness/2, 0, 0])
                GaugeResinSupport(Gauge_Offset_Start+(n+1)*Gauge_Offset_Int);
            }
            GaugeResinSupportsRaft();
        }
    }
}

module ResinPrint(){
    FullElement();
    ResinSupport();
}

module TypeTest(){
    Test_String=str(Keyboard_Layout_Array[0], Keyboard_Layout_Array[1], Keyboard_Layout_Array[2]);
    for (n=[0:len(Test_String)-1]){
        translate([1/Test_CPI*25.4*n, 0, 0]){
            AlignedText(Test_String[n], Test_Font, Test_Size);
            if (Show_Align_Bounds) AlignBoundsBox(25.4/Test_CPI, Test_Size*1.5);
        }
    }
}

//render
//module Render() was renamed away (it collided with the Render variable
//above) and inlined below, matching every other v2 machine's top-level gate.
if (Render==true){
    difference(){
//        color("lightblue")
        if (Render_Mode==0) FullElement();
        else if (Render_Mode==1) ResinPrint();
        else if (Render_Mode==2) GaugeTestSet();
        else if (Render_Mode==3)
        TypeTest();
        if (X_Section==true){
            rotate([0, 0, X_Section_Theta])
            translate([-50, -100, -50])
            cube(100);
        }

    }
}
