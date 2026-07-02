//Blickensderfer Typewriter Element
//File Start Jan 16 2025
//Leonard Chau
//www.leonardchau.com
//
//v2.0: glyph pipeline extracted to lib/glyph_pipeline.scad. See
//docs/refactoring-plan.md. Original preserved at Blickensderfer/Blickensderfer2.scad. This file was Blickensderfer3.scad, moved to v2/blickensderfer.scad.


/* [Global Parameters] */
//to help with z fighting
z=.01;
//minkowski facet number
Mink_Fn=20;
//text facet number
Text_Fn=40;
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
X_Section_Theta=0;

/* [Testing Stuff] */
include <lib/testing.scad>
//enable cutout test
Cutout_Test=false;
//cutout test range start
Cutout_Test_Start=0;//.1
//cutout test interval
Cutout_Test_Int=.05;
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
Test_Char="X";
//which keyboard the console echo identifies positions against (independent
//of Element_Layout_Array_Selection below - your physical keyboard's key labels
//don't change just because you're test-printing a different layout)
Reference_Layout_Selection=0;//[0:dhiatensor, 1:qwerty, 2:scandi, 3:hebrew english, 4:charienstu german, 5:charienstu de mod]

/* [Key Mapping] */
//layout for keyboard
//keyboardLayoutArray=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
////keyboard to element map
//Element_Layout_Array_Map=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];

include <lib/layouts/blick_layouts.scad>

Element_Layout_Arrays=[DHIATENSOR, QWERTY, SCANDI, HEBREW_ENGL, CHARIENSTU_DE, CHARIENSTU_DE_MOD];
Element_Layout_Array_Selection=0;//[0:dhiatensor, 1:qwerty, 2:scandi, 3:hebrew english, 4:charienstu german, 5:charienstu de mod]
Element_Layout_Array=Element_Layout_Arrays[Element_Layout_Array_Selection];
Element_Layout_Array_Map=[13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14]
;
//Reference_Physical_Layout: same Element_Layout_Array_Map hardware remap as
//Physical_Layout below, but built from Reference_Layout_Selection instead of
//Element_Layout_Array_Selection - used only by the console echo, see
//lib/glyph_pipeline.scad's header comment.
Reference_Layout_Array=Element_Layout_Arrays[Reference_Layout_Selection];
Reference_Physical_Layout=[for (row=[0:2]) [for (col=[0:27]) Reference_Layout_Array[row][Element_Layout_Array_Map[col]]]];

//baseline values for characters from top of element
Baseline=[-4, -10.3, -16.1];
//baseline values for platen cutouts from top of element
Cutout=[-2.55, -8.66, -14.45];
//latitude spacing
Latitude_Int=360/28;

/* [Typeface Stuff] */
//element typeface
Font="Blick_Script_Leo";
//type size
Font_Size=3.7;
Character_Modifieds="";
Character_Modifieds_Font="LTCRemingtonTypewriterW10";
Character_Modifieds_Size=4.5;//.1
Character_Modifieds_Offset=0;//.05
Font_Hebrew="Drugulin CLM Mod";
Font_Hebrew_Size=3.3;
Font_Hebrew_Insert_Niqqud=false;
//Font weight offset +/-
Font_Weight_Offset=0;
//Font x weight adjustment 0+
X_Font_Weight_Adj=0;
//Font y weight adjustment 0+
Y_Font_Weight_Adj=0;
Char_Replace="";
Char_Replacewith="";

/* [Glyph Quality (unified across all v2 machines)] */
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
Typeface_2="Arial";
Type_2_Size=3.7;
Typeface_2_Chars="";



/* [Element Dimensions] */
//OD of platen
Platen_Diameter=32.258;
//OD of element at non-text section
Element_Diameter=34;
//OD of element between two characters (minimum distance in concave section)
Min_Final_Character_Diameter=35;
//minimum text protrustion distance
Char_Protrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//element height/thickness
Element_Height=17.15;
//minimum wall thickness of element
Wall_Min_Thickness=1.5;
//inside wall chamfer size
Wall_Chamfer=.5;
//roof center height offset to reduce pulling forces when printing (reduces past min wall thickness)
Roof_Offset=.5;
//speed hole diameter
Speed_Hole_ID=5.568;
//speed hole quantity
Speed_Hole_Qty=8;
//speed hole radial distance
Speed_Hole_Radial=11.25;
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
Core_Bottom_Offset=2.5;
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
Drive_Pin_Widthmm=3.737;
//drive pin length
Drive_Pin_Length=3.6;
//drive pin square hole radial distance (center of square)
Drive_Pin_Radial=10.9;
//drive pin countersink
Drive_Pin_Countersink_Depth=2;
//drive pin internal support radial offset from countersink id
Drive_Pin_Support_Radial_Offset=.5;//.1
//drive pin internal support height
Drive_Pin_Support_Height=2;

Drive_Pin_Style=0;//[0:later, 1:early]
Drive_Pin_Width_Oldmm=2.05;
Drive_Pin_Length_Old=3.5;
Drive_Pin_Length_Start_Old=9.3;

Drive_Pin_Radial_Old=Drive_Pin_Length_Start_Old+Drive_Pin_Length_Old/2;


/* [Logo] */
//Logo Offset From Pin (Degrees)
Logo_Position_Offset=180;
//Logo Text Orientation
Logo_Text_Offset=180;
//Logo Text
Logo_Text="Leonard Chau 2025";
//Logo Size
Logo_Text_Size=2.5;
//Logo Font
Logo_Font="FreeMono:style=Bold";
Logo_Text_Spacing=8;
Logo_Radius=Element_Diameter/2-2.0;

/* [Print Tolerances] */
//adds this much mm to the minor diameter of the elements shaft
Core_ID_Offset=.14;//.001
Drive_Pin_Width_Offset=.15;
Shaft_Diameter=Core_ID_Mm+Core_ID_Offset;
Drive_Pin_Width=Drive_Pin_Widthmm+Drive_Pin_Width_Offset;
Drive_Pin_Width_Old=Drive_Pin_Width_Oldmm+Drive_Pin_Width_Offset;

Drive_Pin_Countersink_ID=sqrt(Drive_Pin_Width^2+Drive_Pin_Length^2);

/* [Shaft Gauge Test] */
Gauge_Offset_Start=0;//.001
Gauge_Offset_Int=.025;

/* [Type Test] */
Test_String="now is the time";
Test_CPI=10;

/* [Resin Printing] */
//resin support enable
Resin_Support=true;
//resin rod diameter
Resin_Rod_OD=1.0;
//resin tip diameter
Resin_Tip_OD=.6;
//resin tip length
Resin_Tip_L=1;
//resin rod inset in part
Resin_Inset=.3;
//resin rod minimum height
Resin_Min_Rod_Height=4;
//resin rod base diameter
Resin_Raft_OD=2;
//resin rod raft thickness
Resin_Raft_Thickness=1;
//resin cut groove diameter
Resin_Groove_OD=.8;
//resin cut groove min thickness
Resin_Groove_Thickness=.3;
//resin bottom radial support counts (2 or greater to enable)
Resin_Bottom_Support_Count=0;

//OD top clip section
Clip_OD=Shaft_Diameter+2*Wall_Min_Thickness;

/* [Glyph pipeline lib wiring] */
//Physical_Layout: Element_Layout_Array is already stored in physical column
//order, so this is a direct pass-through except for Blick's two per-char
//content substitutions (niqqud insertion, Char_Replace), computed here since
//the shared lib expects character content already fully resolved.
Physical_Layout=[for (row=[0:2]) [for (col=[0:27])
    let (char_prime=Element_Layout_Array[row][col])
    (Font_Hebrew_Insert_Niqqud==true && char_prime=="ך")?"ךְ":
    char_prime==Char_Replace?Char_Replacewith:char_prime
]];

//Element_Layout_Array_Map remaps the PLACEMENT angle (not character content) in
//this file - pass straight through as the lib's Placement_Map.
Placement_Map=Element_Layout_Array_Map;

//Hebrew layout uses a distinct Font/size on row 0 only, and always wins over
//any charMods match on that row (matches original precedence).
Row_Font=[Element_Layout_Array_Selection==3?Font_Hebrew:Font, Font, Font];
Row_Font_Size=[Element_Layout_Array_Selection==3?Font_Hebrew_Size:Font_Size, Font_Size, Font_Size];
Row_Font_Lock=[Element_Layout_Array_Selection==3, false, false];

//Baseline_Z_Offset: Blick2's Baseline/Cutout arrays are negative-from-clip-end,
//so this shifts every character placement to an absolute height. Distinct
//from the Element_Height dimension itself even though the value matches.
Baseline_Z_Offset=Element_Height;
//row names for TextRingDebug's console output (Cutout_Test/Baseline_Test/Test_Layout)
Row_Labels=["lowercase", "uppercase", "figs"];

include <lib/glyph_pipeline.scad>
//Blickensderfer2 needs no resin_support overrides: Resin_Rod_Raft, Cut_Groove_Inner_X,
//Bottom_Support_Fractions, and Bottom_Support_Inner_Angle_Offset all use lib defaults.
include <lib/resin_support.scad>

/* [Core/shaft lib wiring] */
//Shaft_Diameter already declared natively above - no bridging needed.
Core_Top_Z=Element_Height+Clip_Height;
Core_Bottom_Z=Core_Bottom_Offset;
//Core_Taper_Top_Z: SecondaryCore/CoreEllipses' taper stops below the clip
//(plain Element_Height), not at the absolute top (Element_Height+Clip_Height) - this is
//the one landmark that genuinely differs from Core_Top_Z here, unlike Bennett
//which has no clip and can use the lib's default (same as Core_Top_Z).
Core_Taper_Top_Z=Element_Height;
//Core_Chamfer_Top defaults to true, matching Blickensderfer2's two-sided chamfer.

include <lib/core_shaft.scad>

//main cylinder
module Cylinder(){
    cylinder(d=Element_Diameter, h=Element_Height, $fn=Surface_Fn);
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
    difference(){
        rotate_extrude()
        polygon([[Shaft_Diameter/2+Wall_Min_Thickness, Wall_Min_Thickness+Wall_Chamfer+Core_Bottom_Offset], [Shaft_Diameter/2+Wall_Min_Thickness, Element_Height-Wall_Min_Thickness-Wall_Chamfer], [Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer, Element_Height-Wall_Min_Thickness], [(Shaft_Diameter+Element_Diameter)/4, Element_Height-Wall_Min_Thickness+Roof_Offset], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, Element_Height-Wall_Min_Thickness], [Element_Diameter/2-Wall_Min_Thickness, Element_Height-Wall_Min_Thickness-Wall_Chamfer], [Element_Diameter/2-Wall_Min_Thickness, Wall_Min_Thickness+Wall_Chamfer], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, Wall_Min_Thickness], [Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer, Wall_Min_Thickness+Core_Bottom_Offset]]);

        CountersinkID=Drive_Pin_Style==0?Drive_Pin_Countersink_ID:Drive_Pin_Length_Old;
        Radius=Drive_Pin_Style==0?Drive_Pin_Radial:Drive_Pin_Radial_Old;


        translate([Radius, 0, 0])
        cylinder(d=CountersinkID+2*Drive_Pin_Support_Radial_Offset, h=Drive_Pin_Countersink_Depth+Drive_Pin_Support_Height, $fn=Surface_Fn);
    }
}


module BottomSlopedSpace(){
    $fn=Surface_Fn;
    rotate_extrude(){
        polygon([[0, -z-5], [0, Core_Bottom_Offset], [bottomX(Core_Bottom_Offset), Core_Bottom_Offset], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer, 0], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer+5, 0], [Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer+5, -z-5]]);
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

module DrivePin(){
    if (Drive_Pin_Style==0){
        translate([Drive_Pin_Radial, 0, -z+2.5])
        rotate([0, 0, 90])
        cube([Drive_Pin_Width, Drive_Pin_Length, 5], center=true);
        translate([Drive_Pin_Radial, 0, -z])
        cylinder(d=Drive_Pin_Countersink_ID, h=z+Drive_Pin_Countersink_Depth, $fn=Surface_Fn);
    }

    if (Drive_Pin_Style==1){

        translate([Drive_Pin_Radial_Old, 0, -z]){
            hull(){
                translate([Drive_Pin_Length_Old/2-Drive_Pin_Width_Old/2, 0, 0])
                cylinder(d=Drive_Pin_Width_Old, h=5, $fn=Surface_Fn);
                translate([-Drive_Pin_Length_Old/2+Drive_Pin_Width_Old/2, 0, 0])
                cylinder(d=Drive_Pin_Width_Old, h=5, $fn=Surface_Fn);
            }

            cylinder(d=Drive_Pin_Length_Old, h=z+Drive_Pin_Countersink_Depth, $fn=Surface_Fn);
        }

    }
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
//come from lib/resin_support.scad (included above). DrivePinSupport is
//generic there (radius, halfExtentX, halfExtentY) since Blick2's circular
//countersink footprint and Postal's rectangular drive-pin footprint are the
//same formula with different half-extents - resolve Blick2's two Drive_Pin_Style
//variants to a radius/halfExtent pair here, matching original geometry exactly.
module ResinSupport(){
    _countersinkID=Drive_Pin_Style==0?Drive_Pin_Countersink_ID:Drive_Pin_Length_Old;
    _radius=Drive_Pin_Style==0?Drive_Pin_Radial:Drive_Pin_Radial_Old;
    union(){
        CutGroove();
        SpeedHoleSupports();
        DrivePinSupport(_radius, _countersinkID/2, _countersinkID/2);
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
    Test_String=str(Element_Layout_Array[0], Element_Layout_Array[1], Element_Layout_Array[2]);
    for (n=[0:len(Test_String)-1]){
            char_prime=Test_String[n];

        char=(Font_Hebrew_Insert_Niqqud==true && char_prime==
        "ך"
        )?//2 characters below
        "ךְ"
        :
        char_prime==Char_Replace?Char_Replacewith:char_prime;

        Font=(Element_Layout_Array_Selection==3 && baseline==0)?Font_Hebrew:
        search(char, Character_Modifieds)==[]?Font:Character_Modifieds_Font;

        Font_Size=(Element_Layout_Array_Selection==3 && baseline==0)?Font_Hebrew_Size:
        search(char, Character_Modifieds)==[]?Font_Size:Character_Modifieds_Size;

        baselineOffset=search(char, Character_Modifieds)==[]?0:Character_Modifieds_Offset;

        translate([1/Test_CPI*25.4*n, baselineOffset, 0])
        text(text=char, size=Font_Size, font=Font, halign="center", valign="baseline", $fn=Text_Fn);


    }
    translate([-2.54/2, -5, 0])
    text(text=Test_String, size=Font_Size, font=Font, halign="left", valign="baseline", $fn=Text_Fn);
}

//render
//module Render() was renamed away (it collided with the Render variable
//above) and inlined below, matching every other v2 machine's top-level gate.
if (Render==true){
    difference(){
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
