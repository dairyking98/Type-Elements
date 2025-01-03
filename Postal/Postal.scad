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
//platen OD
platenOD=31.9;
//cylinder OD
cylOD=32.8;
//text OD
textOD=34.1;
//text protrustion
textProtrusion=(textOD-cylOD)/2;
//cylinder height
cylHeight=17.4;
//min wall thickness
minWallThickness=1.5;
//inside wall radius
wallRad=1;
//speed hole diameter
speedHoleID=5.2;
//speed hole quantity
speedHoleQty=8;
//speed hole radial distance
speedHoleRadial=10.3;
//core ID
coreID=5;
//drive pin width
drivePinWidth=2.5;
//drive pin length
drivePinLength=3.6;
//drive pin square hole center from center
drivePinRadius=10.2;

/* [Print Tolerances] */

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

module Core(){
    translate([0, 0, -z])
    cylinder(d=coreID, h=cylHeight+2*z, $fn=cylFn);
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
        hull(){
        
            //bottom inner
            translate([coreID/2+minWallThickness+wallRad, minWallThickness+wallRad])
            circle(r=wallRad);
            
            //bottom outer
            translate([cylOD/2-minWallThickness-wallRad, minWallThickness+wallRad])
            circle(r=wallRad);
            
            //top inner
            translate([coreID/2+minWallThickness+wallRad, cylHeight-minWallThickness-wallRad-1])
            circle(r=wallRad);
            
            //top outer
            translate([cylOD/2-minWallThickness-wallRad, cylHeight-minWallThickness-wallRad-1])
            circle(r=wallRad);
            
            //top center
            translate([(coreID+cylOD)/4, cylHeight-minWallThickness-wallRad])
            circle(r=wallRad);
            
        }
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
}

module Subtractive(){
    Core();
    SpeedHoles();
    HollowSpace();
    DrivePin();
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
        FullElement();
        if (xSection==true){
            rotate([0, 0, xSectionTheta])
            translate([-50, -100, -50])
            cube(100);
        }
    
    }
}

if (render==true) Render();