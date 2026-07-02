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
minkFn=20;
//text facet number
textFn=20;
//cylinder facet number
cylFn=360;
//surface facet number
surfaceFn=120;
//resin support facet number
resinFn=20;
//groove facet number
grooveFn=20;

/* [Render Parameters] */
//render something (renamed from render, to match every other v2 machine)
Render=false;
//render mode
renderMode=0;//[0:Normal, 1:Resin print, 2:Gauge Set, 3:Type Test]
//turn minkowski on
minkOn=false;
//draft angle
minkDraftAngle=55;
//turn off core grooves (slow)
renderCoreGroove=true;
//view cross section (renamed from xSection)
XSection=false;
//cross section angle (renamed from xSectionTheta)
XSectionTheta=270;

/* [Testing Stuff] */
include <lib/testing.scad>
//enable cutout test
cutoutTest=false;
//cutout test range start
cutoutTestStart=.7;//.1
//cutout test interval
cutoutTestInt=-.05;
//cutout test array
cutoutTestArray=testSweepArray(cutoutTestStart, cutoutTestInt, 28);
//enable baseline test
baselineTest=false;
//baseline test offset range start
baselineTestStart=0;
//baseline test interval
baselineTestInt=.05;
//baseline test array
baselineTestArray=testSweepArray(baselineTestStart, baselineTestInt, 28);
//enable test layout
testLayout=false;
//test character
testChar="l";

/* [Key Mapping] */
//layout for keyboard
keyboardLayoutArray=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
//keyboard to element map
elementLayoutArrayMap=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];
//baseline values for characters from top of element
Baseline=[-3.6, -10, -15.7];
//baseline values for platen cutouts from top of element
Cutout=[-2.65, -9.1, -14.5];//.05
//latitude spacing
latitudeInt=360/28;

/* [Typeface Stuff] */
//element typeface
font="Alma Mono";
//type size
fontSize=2.4;
//font weight offset +/-
fontWeightOffset=0;
//font x weight adjustment 0+
xFontWeightAdj=0;
//font y weight adjustment 0+
yFontWeightAdj=0;

/* [Glyph Quality (unified across all v2 machines)] */
//per-character baseline offset + font/size override (Postal originally had
//no such system - Character_Modifieds="" means it never matches, a no-op)
Character_Modifieds="";
Character_Modifieds_Offset=0;
Character_Modifieds_Font="Alma Mono";
Character_Modifieds_Size=2.4;
//minkowski erosion/growth stroke-weight system, independent of and layered
//with fontWeightOffset/xFontWeightAdj/yFontWeightAdj above.
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
Type_2Size=2.4;
Typeface_2Chars="";

/* [Element Dimensions] */
//OD of platen
Platen_Diameter=31.9;
//OD of element at non-text section
Element_Diameter=32.8;
//OD of element between two characters (minimum distance in concave section)
Min_Final_Character_Diameter=34.1;
//minimum text protrustion distance
CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//element height/thickness
Element_Height=17.4;
//minimum wall thickness of element
wallMinThickness=1.5;
//inside wall chamfer size
wallChamfer=.5;
//roof center height offset to reduce pulling forces when printing (reduces past min wall thickness)
roofOffset=.5;
//speed hole diameter
speedHoleID=5.2;
//speed hole quantity
speedHoleQty=8;
//speed hole radial distance
speedHoleRadial=10.3;
//core ID in inches
coreIDin=.125;
coreIDmm=coreIDin*25.4;
//core groove qty
coreGrooveQty=16;
//core groove diameter
coreGrooveD=.6;
//core chamfer
coreChamfer=.5;
//core bottom offset from bottom plane
coreBottomOffset=1;
//core contact length from ends where sliding fits occur for shaft to reduce friction
coreContactLength=4;
//core web width
coreWebWidth=2;
//core web hole quantity
coreWebQty=3;
//core web length
coreWebLength=7;
//secondary core with larger diameter to focus friction at ends of shaft hole along core contact lengths
coreSecondaryIDOffset=coreGrooveD/2+z;
//height of top clip section
clipHeight=3;
//clip wire diameter
clipWireOD=.554;
//clip opening distance
clipOpening=1;
//amount of bite for the clip from shaft diameter
clipBite=.7;
//drive pin width
drivePinWidthmm=2.5;
//drive pin length
drivePinLength=3.6;
//drive pin square hole radial distance (center of square)
drivePinRadial=11.5;

/* [Logo] */
//Logo Offset From Pin (Degrees)
logoPositionOffset=180;
//Logo Text Orientation
logoTextOffset=180;
//Logo Text
logoText="Leonard Chau 2025";
//Logo Size
logoTextSize=3;
//Logo Font
logoFont="FreeMono:style=Bold";
logoTextSpacing=10;
logoRadius=Element_Diameter/2-2.0;

/* [Print Tolerances] */
//adds this much mm to the minor diameter of the elements shaft
coreIDOffset=.20;//.001
Shaft_Diameter=coreIDmm+coreIDOffset;
drivePinWidth=drivePinWidthmm+coreIDOffset;

/* [Shaft Gauge Test] */
gaugeOffsetStart=.2;//.001
gaugeOffsetInt=.02;

/* [Type Test] */
testString="Alma Mono";
testSize=3;//.01
testFont="Alma Mono";
testCPI=10;

/* [Resin Printing] */
//resin support enable
resinSupport=true;
//resin rod diameter
resinRodOD=1;
//resin tip diameter
resinTipOD=.6;
//resin tip length
resinTipL=1;
//resin rod inset in part
resinInset=.3;
//resin rod minimum height
resinMinRodHeight=2;
//resin rod base diameter
resinRaftOD=4;
//resin rod raft thickness
resinRaftThickness=2;
//resin cut groove diameter
resinGrooveOD=.8;
//resin cut groove min thickness
resinGrooveThickness=.3;

//OD top clip section
clipOD=Shaft_Diameter+2*wallMinThickness;

/* [Glyph pipeline lib wiring] */
//keyboardLayoutArray is in KEYBOARD order; elementLayoutArrayMap here remaps
//CHARACTER SELECTION (not placement, unlike Blickensderfer2) - bake that
//into physicalLayout so the lib receives characters already in physical
//column order, matching what the original AssembleMinkowski produced.
physicalLayout=[for (row=[0:2]) [for (col=[0:27])
    keyboardLayoutArray[row][elementLayoutArrayMap[col]]
]];
//No placementMap override: Postal places column N at raw latitude N (the lib
//defaults placementMap to identity when left undefined).
//No rowFont/rowFontSize/charMods: Postal never had a per-row or per-char font
//override system, so the lib's single global font/fontSize defaults apply.

//Postal's original Text() set $fn=minkFn locally (Blickensderfer2's didn't);
//preserve that per-machine behavior via the lib's text2DFn hook.
text2DFn=minkFn;
//baselineZOffset: Postal's Baseline/Cutout arrays are negative-from-clip-end,
//so this shifts every character placement to an absolute height.
baselineZOffset=Element_Height;
//row names for TextRingDebug's console output (cutoutTest/baselineTest/testLayout)
rowLabels=["lowercase", "uppercase", "figs"];

include <lib/glyph_pipeline.scad>

//Postal's CutGroove polygon originally extended to the element's center axis,
//forming one continuous raft plate shared by every support rod - so its
//ResinRod()s grow no individual raft of their own (Blick2's did).
resinRodRaft=false;
cutGrooveInnerX=-Element_Diameter/2+wallMinThickness;
//Postal's original BottomSupports placed 5 rods per sector (a to b inclusive,
//quarter steps) with the near-core rod at the un-offset sector angle.
bottomSupportFractions=[0, .25, .5, .75, 1];
bottomSupportInnerAngleOffset=0;

include <lib/resin_support.scad>

/* [Core/shaft lib wiring] */
//Shaft_Diameter already declared natively above - no bridging needed.
coreTopZ=Element_Height+clipHeight;
coreBottomZ=coreBottomOffset;
coreTaperTopZ=Element_Height;
//coreChamferTop defaults to true, matching Postal's two-sided chamfer.

include <lib/core_shaft.scad>

//main cylinder
module Cylinder(){
    cylinder(d=Element_Diameter, h=Element_Height, $fn=cylFn);
}

module ClipCylinder(Offset){
    translate([0, 0, Element_Height-z])
    cylinder(d=clipOD+Offset, h=clipHeight+z, $fn=surfaceFn);
}

module WireBite(){
    $fn=surfaceFn;
    rotate([0, 0, -90])
    translate([Shaft_Diameter/2-clipBite, clipOD/2+z, Element_Height])
    rotate([90, 0, 0])
    linear_extrude(clipOD+2*z)
    hull(){
        translate([clipWireOD/2, clipWireOD/2])
        circle(d=clipWireOD);
        translate([clipBite+(clipOD-Shaft_Diameter)/2, 0])
        square([z, clipOpening]);
    }
}

module Core(Offset){
    translate([0, 0, -z])
    cylinder(d=Shaft_Diameter+Offset, h=Element_Height+clipHeight+2*z, $fn=cylFn);
}

//SecondaryCore, CoreGrooves, CoreChamferShape, CoreChamfer, CoreEllipses now
//come from lib/core_shaft.scad (included above).

module SpeedHoles(){
    for (n=[0:speedHoleQty-1])
    rotate([0, 0, 360/speedHoleQty*n])
    translate([speedHoleRadial, 0, -z+(n==0?Element_Height/2:0)])
    cylinder(d=speedHoleID, h=Element_Height+2*z, $fn=surfaceFn);
}

module HollowSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[Shaft_Diameter/2+wallMinThickness, wallMinThickness+wallChamfer+coreBottomOffset], [Shaft_Diameter/2+wallMinThickness, Element_Height-wallMinThickness-wallChamfer], [Shaft_Diameter/2+wallMinThickness+wallChamfer, Element_Height-wallMinThickness], [(Shaft_Diameter+Element_Diameter)/4, Element_Height-wallMinThickness+roofOffset], [Element_Diameter/2-wallMinThickness-wallChamfer, Element_Height-wallMinThickness], [Element_Diameter/2-wallMinThickness, Element_Height-wallMinThickness-wallChamfer], [Element_Diameter/2-wallMinThickness, wallMinThickness+wallChamfer], [Element_Diameter/2-wallMinThickness-wallChamfer, wallMinThickness], [Shaft_Diameter/2+wallMinThickness+wallChamfer, wallMinThickness+coreBottomOffset]]);
    }
}

module BottomSlopedSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, -z-5], [0, coreBottomOffset], [bottomX(coreBottomOffset), coreBottomOffset], [Element_Diameter/2-wallMinThickness-wallChamfer, -z], [Element_Diameter/2-wallMinThickness-wallChamfer+5, -z], [Element_Diameter/2-wallMinThickness-wallChamfer+5, -z-5]]);
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
    translate([drivePinRadial, 0, -z])
    rotate([0, 0, 90])
    square([drivePinWidth, drivePinLength], center=true);
}

module LogoText(){
    for (n=[0:len(logoText)-1]){
            rotate([0,0,logoPositionOffset-90+logoTextSpacing*n-(len(logoText)-1)*logoTextSpacing/2])

            translate([0, logoRadius+1.5, Element_Height-.3])
            linear_extrude(.4)
            rotate([0, 0, logoTextOffset])
            text(text=logoText[n], size=logoTextSize, font=logoFont, valign="baseline", halign="center", $fn=textFn);
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
        if (renderCoreGroove==true) CoreGrooves(0);
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
        DrivePinSupport(drivePinRadial, drivePinLength/2, drivePinWidth/2);
        BottomSupports();
    }
}

module CylinderGauge(Offset){
    translate([0, 0, coreBottomOffset])
    cylinder(d=Shaft_Diameter+2*wallMinThickness+Offset, h=Element_Height+clipHeight-coreBottomOffset, $fn=surfaceFn);
}

module GaugeResinSupport(Offset){
    $fn=resinFn;
    for (n=[0:7]){
        rotate([0, 0, n*360/8])
        translate([Shaft_Diameter/2+Offset/2+wallMinThickness/2, 0, 0])
        ResinRod(coreBottomOffset);
    }
}

module GaugeResinSupportsRaft(){
    translate([0, 0, -resinMinRodHeight-resinRaftThickness])
    cylinder(d1=3*(Shaft_Diameter+2*wallMinThickness), d2=3*(Shaft_Diameter+2*wallMinThickness)+2*resinRaftThickness, h=resinRaftThickness);
}

module RevolverSolid(){
    $fn=surfaceFn;
    hull(){
        for (n=[0:5])
        rotate([0, 0, n*360/6])
        translate([Shaft_Diameter+wallMinThickness*2-wallMinThickness/2, 0, 0])
        CylinderGauge(0);
    }

}

module GaugeTestSubtractive(Offset){
    Core(Offset);
    if (renderCoreGroove==true) CoreGrooves(Offset);
    CoreChamfer(Offset);
    SecondaryCore(Offset);
    echo (str(Offset));
    GaugeText(Offset);
    rotate([0, 0, 180])
    CoreEllipses();
}

module GaugeText(Offset){
    if (Offset!=0)
    translate([Shaft_Diameter/2+wallMinThickness-wallMinThickness/2+coreSecondaryIDOffset/2, 0, coreBottomOffset+(Element_Height+clipHeight-coreBottomOffset)/2])
    rotate([0, 90, 0])
    linear_extrude(4)
    text(text=str(Offset), halign="center", valign="center", $fn=textFn, size=3, font="Consolas");
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
                translate([Shaft_Diameter+wallMinThickness*2-wallMinThickness/2, 0, 0])
                GaugeTestSubtractive(gaugeOffsetStart+(n)*gaugeOffsetInt);
            }
        }

        union(){
            for (n=[0:5]){
                rotate([0, 0, n*360/6])
                translate([Shaft_Diameter+wallMinThickness*2-wallMinThickness/2, 0, 0])
                GaugeResinSupport(gaugeOffsetStart+(n+1)*gaugeOffsetInt);
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
    testString=str(keyboardLayoutArray[0], keyboardLayoutArray[1], keyboardLayoutArray[2]);
    for (n=[0:len(testString)-1]){
        translate([1/testCPI*25.4*n, 0, 0])
        text(text=testString[n], size=testSize, font=testFont, halign="center", valign="baseline", $fn=textFn);
    }
}

//render
//module Render() was renamed away (it collided with the Render variable
//above) and inlined below, matching every other v2 machine's top-level gate.
if (Render==true){
    difference(){
//        color("lightblue")
        if (renderMode==0) FullElement();
        else if (renderMode==1) ResinPrint();
        else if (renderMode==2) GaugeTestSet();
        else if (renderMode==3)
        TypeTest();
        if (XSection==true){
            rotate([0, 0, XSectionTheta])
            translate([-50, -100, -50])
            cube(100);
        }

    }
}
