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
minkFn=20;
//text facet number
textFn=40;
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
XSectionTheta=0;

/* [Testing Stuff] */
include <lib/testing.scad>
//enable cutout test
cutoutTest=false;
//cutout test range start
cutoutTestStart=0;//.1
//cutout test interval
cutoutTestInt=.05;
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
testChar="X";
//which keyboard the console echo identifies positions against (independent
//of elementLayoutArraySelection below - your physical keyboard's key labels
//don't change just because you're test-printing a different layout)
referenceLayoutSelection=0;//[0:dhiatensor, 1:qwerty, 2:scandi, 3:hebrew english, 4:charienstu german, 5:charienstu de mod]

/* [Key Mapping] */
//layout for keyboard
//keyboardLayoutArray=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
////keyboard to element map
//elementLayoutArrayMap=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];

include <lib/layouts/blick_layouts.scad>

elementLayoutArrays=[DHIATENSOR, QWERTY, SCANDI, HEBREW_ENGL, CHARIENSTU_DE, CHARIENSTU_DE_MOD];
elementLayoutArraySelection=0;//[0:dhiatensor, 1:qwerty, 2:scandi, 3:hebrew english, 4:charienstu german, 5:charienstu de mod]
elementLayoutArray=elementLayoutArrays[elementLayoutArraySelection];
elementLayoutArrayMap=[13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14]
;
//referencePhysicalLayout: same elementLayoutArrayMap hardware remap as
//physicalLayout below, but built from referenceLayoutSelection instead of
//elementLayoutArraySelection - used only by the console echo, see
//lib/glyph_pipeline.scad's header comment.
referenceLayoutArray=elementLayoutArrays[referenceLayoutSelection];
referencePhysicalLayout=[for (row=[0:2]) [for (col=[0:27]) referenceLayoutArray[row][elementLayoutArrayMap[col]]]];

//baseline values for characters from top of element
Baseline=[-4, -10.3, -16.1];
//baseline values for platen cutouts from top of element
Cutout=[-2.55, -8.66, -14.45];
//latitude spacing
latitudeInt=360/28;

/* [Typeface Stuff] */
//element typeface
font="Blick_Script_Leo";
//type size
fontSize=3.7;
Character_Modifieds="";
Character_Modifieds_Font="LTCRemingtonTypewriterW10";
Character_Modifieds_Size=4.5;//.1
Character_Modifieds_Offset=0;//.05
fontHebrew="Drugulin CLM Mod";
fontHebrewSize=3.3;
fontHebrewInsertNiqqud=false;
//font weight offset +/-
fontWeightOffset=0;
//font x weight adjustment 0+
xFontWeightAdj=0;
//font y weight adjustment 0+
yFontWeightAdj=0;
char_replace="";
char_replacewith="";

/* [Glyph Quality (unified across all v2 machines)] */
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
Typeface_2="Arial";
Type_2Size=3.7;
Typeface_2Chars="";



/* [Element Dimensions] */
//OD of platen
Platen_Diameter=32.258;
//OD of element at non-text section
Element_Diameter=34;
//OD of element between two characters (minimum distance in concave section)
Min_Final_Character_Diameter=35;
//minimum text protrustion distance
CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;
//element height/thickness
Element_Height=17.15;
//minimum wall thickness of element
wallMinThickness=1.5;
//inside wall chamfer size
wallChamfer=.5;
//roof center height offset to reduce pulling forces when printing (reduces past min wall thickness)
roofOffset=.5;
//speed hole diameter
speedHoleID=5.568;
//speed hole quantity
speedHoleQty=8;
//speed hole radial distance
speedHoleRadial=11.25;
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
coreBottomOffset=2.5;
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
drivePinWidthmm=3.737;
//drive pin length
drivePinLength=3.6;
//drive pin square hole radial distance (center of square)
drivePinRadial=10.9;
//drive pin countersink
drivePinCountersinkDepth=2;
//drive pin internal support radial offset from countersink id
drivePinSupportRadialOffset=.5;//.1
//drive pin internal support height
drivePinSupportHeight=2;

drivePinStyle=0;//[0:later, 1:early]
drivePinWidthOldmm=2.05;
drivePinLengthOld=3.5;
drivePinLengthStartOld=9.3;

drivePinRadialOld=drivePinLengthStartOld+drivePinLengthOld/2;


/* [Logo] */
//Logo Offset From Pin (Degrees)
logoPositionOffset=180;
//Logo Text Orientation
logoTextOffset=180;
//Logo Text
logoText="Leonard Chau 2025";
//Logo Size
logoTextSize=2.5;
//Logo Font
logoFont="FreeMono:style=Bold";
logoTextSpacing=8;
logoRadius=Element_Diameter/2-2.0;

/* [Print Tolerances] */
//adds this much mm to the minor diameter of the elements shaft
coreIDOffset=.14;//.001
drivePinWidthOffset=.15;
Shaft_Diameter=coreIDmm+coreIDOffset;
drivePinWidth=drivePinWidthmm+drivePinWidthOffset;
drivePinWidthOld=drivePinWidthOldmm+drivePinWidthOffset;

drivePinCountersinkID=sqrt(drivePinWidth^2+drivePinLength^2);

/* [Shaft Gauge Test] */
gaugeOffsetStart=0;//.001
gaugeOffsetInt=.025;

/* [Type Test] */
testString="now is the time";
testCPI=10;

/* [Resin Printing] */
//resin support enable
resinSupport=true;
//resin rod diameter
resinRodOD=1.0;
//resin tip diameter
resinTipOD=.6;
//resin tip length
resinTipL=1;
//resin rod inset in part
resinInset=.3;
//resin rod minimum height
resinMinRodHeight=4;
//resin rod base diameter
resinRaftOD=2;
//resin rod raft thickness
resinRaftThickness=1;
//resin cut groove diameter
resinGrooveOD=.8;
//resin cut groove min thickness
resinGrooveThickness=.3;
//resin bottom radial support counts (2 or greater to enable)
resinBottomSupportCount=0;

//OD top clip section
clipOD=Shaft_Diameter+2*wallMinThickness;

/* [Glyph pipeline lib wiring] */
//physicalLayout: elementLayoutArray is already stored in physical column
//order, so this is a direct pass-through except for Blick's two per-char
//content substitutions (niqqud insertion, char_replace), computed here since
//the shared lib expects character content already fully resolved.
physicalLayout=[for (row=[0:2]) [for (col=[0:27])
    let (char_prime=elementLayoutArray[row][col])
    (fontHebrewInsertNiqqud==true && char_prime=="ך")?"ךְ":
    char_prime==char_replace?char_replacewith:char_prime
]];

//elementLayoutArrayMap remaps the PLACEMENT angle (not character content) in
//this file - pass straight through as the lib's placementMap.
placementMap=elementLayoutArrayMap;

//Hebrew layout uses a distinct font/size on row 0 only, and always wins over
//any charMods match on that row (matches original precedence).
rowFont=[elementLayoutArraySelection==3?fontHebrew:font, font, font];
rowFontSize=[elementLayoutArraySelection==3?fontHebrewSize:fontSize, fontSize, fontSize];
rowFontLock=[elementLayoutArraySelection==3, false, false];

//baselineZOffset: Blick2's Baseline/Cutout arrays are negative-from-clip-end,
//so this shifts every character placement to an absolute height. Distinct
//from the Element_Height dimension itself even though the value matches.
baselineZOffset=Element_Height;
//row names for TextRingDebug's console output (cutoutTest/baselineTest/testLayout)
rowLabels=["lowercase", "uppercase", "figs"];

include <lib/glyph_pipeline.scad>
//Blickensderfer2 needs no resin_support overrides: resinRodRaft, cutGrooveInnerX,
//bottomSupportFractions, and bottomSupportInnerAngleOffset all use lib defaults.
include <lib/resin_support.scad>

/* [Core/shaft lib wiring] */
//Shaft_Diameter already declared natively above - no bridging needed.
coreTopZ=Element_Height+clipHeight;
coreBottomZ=coreBottomOffset;
//coreTaperTopZ: SecondaryCore/CoreEllipses' taper stops below the clip
//(plain Element_Height), not at the absolute top (Element_Height+clipHeight) - this is
//the one landmark that genuinely differs from coreTopZ here, unlike Bennett
//which has no clip and can use the lib's default (same as coreTopZ).
coreTaperTopZ=Element_Height;
//coreChamferTop defaults to true, matching Blickensderfer2's two-sided chamfer.

include <lib/core_shaft.scad>

//main cylinder
module Cylinder(){
    cylinder(d=Element_Diameter, h=Element_Height, $fn=surfaceFn);
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
    difference(){
        rotate_extrude()
        polygon([[Shaft_Diameter/2+wallMinThickness, wallMinThickness+wallChamfer+coreBottomOffset], [Shaft_Diameter/2+wallMinThickness, Element_Height-wallMinThickness-wallChamfer], [Shaft_Diameter/2+wallMinThickness+wallChamfer, Element_Height-wallMinThickness], [(Shaft_Diameter+Element_Diameter)/4, Element_Height-wallMinThickness+roofOffset], [Element_Diameter/2-wallMinThickness-wallChamfer, Element_Height-wallMinThickness], [Element_Diameter/2-wallMinThickness, Element_Height-wallMinThickness-wallChamfer], [Element_Diameter/2-wallMinThickness, wallMinThickness+wallChamfer], [Element_Diameter/2-wallMinThickness-wallChamfer, wallMinThickness], [Shaft_Diameter/2+wallMinThickness+wallChamfer, wallMinThickness+coreBottomOffset]]);

        CountersinkID=drivePinStyle==0?drivePinCountersinkID:drivePinLengthOld;
        Radius=drivePinStyle==0?drivePinRadial:drivePinRadialOld;


        translate([Radius, 0, 0])
        cylinder(d=CountersinkID+2*drivePinSupportRadialOffset, h=drivePinCountersinkDepth+drivePinSupportHeight, $fn=surfaceFn);
    }
}


module BottomSlopedSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, -z-5], [0, coreBottomOffset], [bottomX(coreBottomOffset), coreBottomOffset], [Element_Diameter/2-wallMinThickness-wallChamfer, 0], [Element_Diameter/2-wallMinThickness-wallChamfer+5, 0], [Element_Diameter/2-wallMinThickness-wallChamfer+5, -z-5]]);
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
    if (drivePinStyle==0){
        translate([drivePinRadial, 0, -z+2.5])
        rotate([0, 0, 90])
        cube([drivePinWidth, drivePinLength, 5], center=true);
        translate([drivePinRadial, 0, -z])
        cylinder(d=drivePinCountersinkID, h=z+drivePinCountersinkDepth, $fn=surfaceFn);
    }

    if (drivePinStyle==1){

        translate([drivePinRadialOld, 0, -z]){
            hull(){
                translate([drivePinLengthOld/2-drivePinWidthOld/2, 0, 0])
                cylinder(d=drivePinWidthOld, h=5, $fn=surfaceFn);
                translate([-drivePinLengthOld/2+drivePinWidthOld/2, 0, 0])
                cylinder(d=drivePinWidthOld, h=5, $fn=surfaceFn);
            }

            cylinder(d=drivePinLengthOld, h=z+drivePinCountersinkDepth, $fn=surfaceFn);
        }

    }
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
//come from lib/resin_support.scad (included above). DrivePinSupport is
//generic there (radius, halfExtentX, halfExtentY) since Blick2's circular
//countersink footprint and Postal's rectangular drive-pin footprint are the
//same formula with different half-extents - resolve Blick2's two drivePinStyle
//variants to a radius/halfExtent pair here, matching original geometry exactly.
module ResinSupport(){
    _countersinkID=drivePinStyle==0?drivePinCountersinkID:drivePinLengthOld;
    _radius=drivePinStyle==0?drivePinRadial:drivePinRadialOld;
    union(){
        CutGroove();
        SpeedHoleSupports();
        DrivePinSupport(_radius, _countersinkID/2, _countersinkID/2);
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
    testString=str(elementLayoutArray[0], elementLayoutArray[1], elementLayoutArray[2]);
    for (n=[0:len(testString)-1]){
            char_prime=testString[n];

        char=(fontHebrewInsertNiqqud==true && char_prime==
        "ך"
        )?//2 characters below
        "ךְ"
        :
        char_prime==char_replace?char_replacewith:char_prime;

        font=(elementLayoutArraySelection==3 && baseline==0)?fontHebrew:
        search(char, Character_Modifieds)==[]?font:Character_Modifieds_Font;

        fontSize=(elementLayoutArraySelection==3 && baseline==0)?fontHebrewSize:
        search(char, Character_Modifieds)==[]?fontSize:Character_Modifieds_Size;

        baselineOffset=search(char, Character_Modifieds)==[]?0:Character_Modifieds_Offset;

        translate([1/testCPI*25.4*n, baselineOffset, 0])
        text(text=char, size=fontSize, font=font, halign="center", valign="baseline", $fn=textFn);


    }
    translate([-2.54/2, -5, 0])
    text(text=testString, size=fontSize, font=font, halign="left", valign="baseline", $fn=textFn);
}

//render
//module Render() was renamed away (it collided with the Render variable
//above) and inlined below, matching every other v2 machine's top-level gate.
if (Render==true){
    difference(){
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
