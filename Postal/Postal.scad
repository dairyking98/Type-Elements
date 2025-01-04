//Postal Typewriter Element
//File Start Jan 02 2025
//Leonard Chau
//www.leonardchau.com

//Modeled off a Model 3 Postal, SN 14550

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

/* [Render Parameters] */
//render something
render=false;
//render mode
renderMode=0;//[0:Normal, 1:Resin print]
//turn minkowski on
minkOn=false;
//draft angle
minkDraftAngle=55;
//mink bottom radius size
function minkTextR(draft_angle)=2*tan(.5*draft_angle);
//view cross section
xSection=false;
//cross section angle
xSectionTheta=0;

/* [Testing Stuff] */
//enable cutout test
cutoutTest=false;
//cutout test range start
cutoutTestStart=0;
//cutout test interval
cutoutTestInt=.05;
//cutout test array
cutoutTestArray=[for (n=[0:27]) cutoutTestStart+cutoutTestInt*n];
//enable baseline test
baselineTest=false;
//baseline test offset range start
baselineTestStart=0;
//baseline test interval
baselineTestInt=.05;
//baseline test array
baselineTestArray=[for (n=[0:27]) baselineTestStart+baselineTestInt*n];
//enable test layout
testLayout=false;
//test character
testChar="X";

/* [Key Mapping] */
//layout for keyboard
keyboardLayoutArray=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
//keyboard to element map
elementLayoutArrayMap=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];
//baseline values for characters from top of element
charBaselines=[-3.8, -10.2, -15.7];
//baseline values for platen cutouts from top of element
platenBaselines=[-3.4, -9.8, -15.3];
//latitude spacing
latitudeInt=360/28;

/* [Typeface Stuff] */
//element typeface
font="Arial";
//type size
fontSize=2.4;
//font weight offset +/-
fontWeightOffset=0;
//font x weight adjustment 0+
xFontWeightAdj=0;
//font y weight adjustment 0+
yFontWeightAdj=0;

/* [Element Dimensions] */
//OD of platen
platenOD=31.9;
//OD of element at non-text section
cylOD=32.8;
//OD of element between two characters (minimum distance in concave section)
textOD=34.1;
//minimum text protrustion distance
textProtrusion=(textOD-cylOD)/2;
//element height/thickness
cylHeight=17.4;
//minimum wall thickness of element
minWallThickness=1.5;
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
coreBottomOffset=2.5;
//core contact length from ends where sliding fits occur for shaft to reduce friction
coreContactLength=4;
//secondary core with larger diameter to focus friction at ends of shaft hole along core contact lengths
secondaryCoreIDOffset=coreGrooveD/2;
//height of top clip section
clipHeight=3;
//clip wire diameter
clipWireOD=.554;
//clip opening distance
clipOpening=1;
//amount of bite for the clip from shaft diameter
clipBite=.7;
//drive pin width
drivePinWidth=2.5;
//drive pin length
drivePinLength=3.6;
//drive pin square hole center from center
drivePinRadius=10.2;

/* [Print Tolerances] */
coreIDOffset=.10;
coreID=coreIDmm+coreIDOffset;


//OD top clip section
clipOD=coreID+2*minWallThickness;

//slope of bottom of element in sloped section
bottomSlope=coreBottomOffset/(coreID/2-cylOD/2);
//z offset for equation for height of z point on bottom sloped section of element
bottomZOffset=-bottomSlope*(coreID/2+minWallThickness);
//function for obtaining z height of radial point X on bottom of element in sloped section 
function bottomZ(X)=bottomSlope*X+bottomZOffset;

//text char
module Text(char, font, size){
    $fn=minkFn;
    offset(fontWeightOffset);
    minkowski(){
        mirror([1, 0, 0])
        text(text=char, size=size, font=font, valign="baseline", halign="center", $fn=textFn);
        if (xFontWeightAdj>0 || yFontWeightAdj>0)
        square([z+xFontWeightAdj, z+yFontWieghtAdj], center=true);
    }
}

//platen cutout
module PlatenCutout(platenBaseline, latitude){
    rotate([0, 0, (.5+latitude)*latitudeInt])
    translate([cylOD/2+platenOD/2+textProtrusion, 0, platenBaseline])
    rotate([90, 0, 0])
    cylinder(d=platenOD, h=10, center=true, $fn=cylFn);
}

//position text
module PositionText(textBaseline, latitude){
    rotate([0, 0, (.5+latitude)*latitudeInt])
    translate([0, 0, textBaseline])
    translate([cylOD/2-2, 0, 0])
    rotate([90, 0, 90])
    children();
}

//minkowski single char
module SingleMinkowski(char, font, size, platenBaseline, textBaseline, latitude){
    minkowski(){
        difference(){
            PositionText(textBaseline, latitude)
            linear_extrude(6)
            Text(char, font, size);
            PlatenCutout(platenBaseline, latitude);
        }
        if (minkOn==true){
            rotate([0, -90, (.5+latitude)*latitudeInt])
            cylinder(r1=0, r2=minkTextR(minkDraftAngle), h=2, $fn=minkFn);
        }
    }
}

//assemble minkowski chars
module AssembleMinkowski(){
    for (baseline=[0:2])
    for (latitude=[0:27]){
        char=testLayout==false?keyboardLayoutArray[baseline][elementLayoutArrayMap[latitude]]:testChar;
        platenBaseline=platenBaselines[baseline]+
        (cutoutTest==true?cutoutTestArray[latitude]:0);
        charBaseline=charBaselines[baseline]+(baselineTest==true?baselineTestArray[latitude]:0);
        translate([0, 0, cylHeight])
        SingleMinkowski(char, font, fontSize, platenBaseline, charBaseline, latitude);
    }
}

//main cylinder
module Cylinder(){
    cylinder(d=cylOD, h=cylHeight, $fn=cylFn);
}

module ClipCylinder(){
    translate([0, 0, cylHeight-z])
    cylinder(d=clipOD, h=clipHeight+z, $fn=surfaceFn);
}

module WireBite(){
    $fn=surfaceFn;
    rotate([0, 0, -90])
    translate([coreID/2-clipBite, clipOD/2+z, cylHeight])
    rotate([90, 0, 0])
    linear_extrude(clipOD+2*z)
    hull(){
        translate([clipWireOD/2, clipWireOD/2])
        circle(d=clipWireOD);
        translate([clipBite+(clipOD-coreID)/2, 0])
        square([z, clipOpening]);
    }
}

module Core(){
    translate([0, 0, -z])
    cylinder(d=coreID, h=cylHeight+clipHeight+2*z, $fn=cylFn);
}

module SecondaryCore(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, coreBottomOffset+coreContactLength], [0, cylHeight+clipHeight-coreContactLength], [coreID/2, cylHeight+clipHeight-coreContactLength], [coreID/2+secondaryCoreIDOffset, cylHeight+clipHeight-coreContactLength-secondaryCoreIDOffset], [coreID/2+secondaryCoreIDOffset, coreBottomOffset+coreContactLength+secondaryCoreIDOffset], [coreID/2, coreBottomOffset+coreContactLength]]);
    }
}

module CoreGrooves(){
    for (n=[0:coreGrooveQty-1]){
        rotate([0, 0, 360/coreGrooveQty*n])
        linear_extrude(cylHeight+clipHeight+2*z,  twist=360*(cylHeight+clipHeight-coreBottomOffset+2*z)/(PI*coreID)*(n%2==0?1:-1), $fn=surfaceFn)
        translate([coreID/2, 0, -z])
        translate([0, 0, -z])
        circle(d=coreGrooveD, $fn=surfaceFn);
    }
}

module CoreChamferShape(){
    cylinder(d1=coreID+2*coreChamfer, d2=coreID, h=coreChamfer+z, $fn=surfaceFn);
}

module CoreChamfer(){
    translate([0, 0, coreBottomOffset-z])
    CoreChamferShape();
    translate([0, 0, cylHeight+clipHeight+z])
    rotate([180, 0, 0])
    CoreChamferShape();
}

module SpeedHoles(){
    for (n=[0:speedHoleQty-1])
    rotate([0, 0, 360/speedHoleQty*n])
    translate([speedHoleRadial, 0, -z+(n==0?cylHeight/2:0)])
    cylinder(d=speedHoleID, h=cylHeight+2*z, $fn=surfaceFn);
}

module HollowSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[coreID/2+minWallThickness, minWallThickness+wallChamfer+coreBottomOffset], [coreID/2+minWallThickness, cylHeight-minWallThickness-wallChamfer], [coreID/2+minWallThickness+wallChamfer, cylHeight-minWallThickness], [(coreID+cylOD)/4, cylHeight-minWallThickness+roofOffset], [cylOD/2-minWallThickness-wallChamfer, cylHeight-minWallThickness], [cylOD/2-minWallThickness, cylHeight-minWallThickness-wallChamfer], [cylOD/2-minWallThickness, minWallThickness+wallChamfer], [cylOD/2-minWallThickness-wallChamfer, minWallThickness], [coreID/2+minWallThickness+wallChamfer, minWallThickness+coreBottomOffset]]);
    }
}

module BottomSlopedSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, -z], [0, coreBottomOffset], [coreID+minWallThickness, coreBottomOffset], [cylOD/2-minWallThickness, -z]]);
    }
}

module DrivePin(){
linear_extrude(5)
    translate([drivePinRadius, 0, -z])
    rotate([0, 0, 90])
    square([drivePinWidth, drivePinLength], center=true);
}

module Additive(){
    AssembleMinkowski();
    Cylinder();
    ClipCylinder();
}

module Subtractive(){
    Core();
    CoreGrooves();
    CoreChamfer();
    WireBite();
    SpeedHoles();
    HollowSpace();
    DrivePin();
    BottomSlopedSpace();
    SecondaryCore();
}

module FullElement(){
    difference(){
        Additive();
        Subtractive();
    }
}


//render
module Render(){
    difference(){
        color("lightblue")
        FullElement();
        if (xSection==true){
            rotate([0, 0, xSectionTheta])
            translate([-50, -100, -50])
            cube(100);
        }
    
    }
}

if (render==true) Render();