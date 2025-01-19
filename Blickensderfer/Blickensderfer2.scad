//Blickensderfer Typewriter Element
//File Start Jan 16 2025
//Leonard Chau
//www.leonardchau.com


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
//render something
render=false;
//render mode
renderMode=0;//[0:Normal, 1:Resin print, 2:Gauge Set, 3:Type Test]
//turn minkowski on
minkOn=false;
//draft angle
minkDraftAngle=55;
//turn off core grooves (slow)
renderCoreGroove=true;
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
cutoutTestStart=0;//.1
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
//keyboardLayoutArray=["qwertyuiopasdfghjklzxcvbnm,.","QWERTYUIOPASDFGHJKLZXCVBNM&?","\"23456789%()@/$_;:'£äöü!+=§-"];
////keyboard to element map
//elementLayoutArrayMap=[23, 5, 15, 24, 6, 16, 25, 7, 17, 26, 8, 18, 27, 9, 0, 10, 19, 1, 11, 20, 2, 12, 21, 3, 13, 22, 4, 14];

DHIATENSOR=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-^_(./'\"!1234567890;?%¢$)@#:"];
QWERTY=["qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
       "\"#$%_/-¢@;23456789:!^1.&'(0)"];
SCANDI=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:"];

elementLayoutArrays=[DHIATENSOR, QWERTY, SCANDI];
elementLayoutArraySelection=0;//[0:dhiatensor, 1:qwerty, 2:scandi]
elementLayoutArray=elementLayoutArrays[elementLayoutArraySelection];
elementLayoutArrayMap=[14,15,16,17,18,19,20,21,22,23,24,25,26,27,0,1,2,3,4,5,6,7,8,9,10,11,12,13];
            
//baseline values for characters from top of element
charBaselines=[-4, -10.3, -16.1];
//baseline values for platen cutouts from top of element
platenBaselines=[-2.6, -8.66, -14.6];
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
platenOD=32.258;
//OD of element at non-text section
cylOD=34;
//OD of element between two characters (minimum distance in concave section)
textOD=35;
//minimum text protrustion distance
textProtrusion=(textOD-cylOD)/2;
//element height/thickness
cylHeight=16.75;
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
secondaryCoreIDOffset=coreGrooveD/2+z;
//height of top clip section
clipHeight=3;
//clip wire diameter
clipWireOD=.554;
//clip opening distance
clipOpening=1;
//amount of bite for the clip from shaft diameter
clipBite=.5;
//drive pin width
drivePinWidthmm=3.737;
//drive pin length
drivePinLength=3.6;
//drive pin square hole radial distance (center of square)
drivePinRadial=11.25;
//drive pin countersink
drivePinCountersinkDepth=2;
//drive pin internal support radial offset from countersink id
drivePinSupportRadialOffset=.5;//.1
//drive pin internal support height
drivePinSupportHeight=2;

/* [Print Tolerances] */
//adds this much mm to the minor diameter of the elements shaft
coreIDOffset=.20;//.001
coreID=coreIDmm+coreIDOffset;
drivePinWidth=drivePinWidthmm+coreIDOffset;

drivePinCountersinkID=sqrt(drivePinWidth^2+drivePinLength^2);

/* [Shaft Gauge Test] */
gaugeOffsetStart=0;//.001
gaugeOffsetInt=.025;

/* [Type Test] */
testString="now is the time";
testSize=3;//.01
testFont="Consolas";
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
clipOD=coreID+2*wallMinThickness;

//slope of bottom of element in sloped section
bottomSlope=coreBottomOffset/((coreID/2+wallMinThickness+wallChamfer)-(cylOD/2-wallMinThickness-wallChamfer));
//z offset for equation for height of z point on bottom sloped section of element
bottomZOffset=-bottomSlope*(coreID/2+wallMinThickness+wallChamfer)+coreBottomOffset;
//function for obtaining z height of radial point X on bottom of element in sloped section 
function bottomZ(X)=bottomSlope*X+bottomZOffset;
function bottomX(Z)=(Z-bottomZOffset)/bottomSlope;

//text char
module Text(char, font, size){
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
    translate([cylOD/2+textProtrusion-z, 0, 0])
    rotate([90, 0, 90])
    children();
}

//minkowski single char
module SingleMinkowski(char, font, size, platenBaseline, textBaseline, latitude){
    $fn=surfaceFn;//???
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
        char=testLayout==false?elementLayoutArray[baseline][latitude]:testChar;
        platenBaseline=platenBaselines[baseline]+
        (cutoutTest==true?cutoutTestArray[latitude]:0);
        charBaseline=charBaselines[baseline]+(baselineTest==true?baselineTestArray[latitude]:0);
        latitudeint=elementLayoutArrayMap[latitude];
        translate([0, 0, cylHeight])
        SingleMinkowski(char, font, fontSize, platenBaseline, charBaseline, latitudeint);
        if (cutoutTest || baselineTest || testLayout)
            TestDebug(baseline, latitude, platenBaseline, charBaseline);
    }
}


module TestDebug(baseline, latitude, platenBaseline, charBaseline){
    kbchar=elementLayoutArray[baseline][latitude];
    shifts=["lowercase", "uppercase", "figs"];
    oclock=(1-latitude/28)*12;
    echo(str("character ", kbchar, " on ", shifts[baseline], " row at the ", round(oclock), "oclock position with platen cutout at ", platenBaseline, "mm and character baseline at ", charBaseline, "mm"));
}

//main cylinder
module Cylinder(){
    cylinder(d=cylOD, h=cylHeight, $fn=surfaceFn);
}

module ClipCylinder(Offset){
    translate([0, 0, cylHeight-z])
    cylinder(d=clipOD+Offset, h=clipHeight+z, $fn=surfaceFn);
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

module Core(Offset){
    translate([0, 0, -z])
    cylinder(d=coreID+Offset, h=cylHeight+clipHeight+2*z, $fn=cylFn);
}

module SecondaryCore(Offset){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, coreBottomOffset+coreContactLength], [0, cylHeight+clipHeight-coreContactLength], [coreID/2+Offset/2, cylHeight+clipHeight-coreContactLength], [coreID/2+Offset/2+secondaryCoreIDOffset, cylHeight+clipHeight-coreContactLength-secondaryCoreIDOffset], [coreID/2+Offset/2+secondaryCoreIDOffset, coreBottomOffset+coreContactLength+secondaryCoreIDOffset], [coreID/2+Offset/2, coreBottomOffset+coreContactLength]]);
    }
}

module CoreGrooves(Offset){
    for (n=[0:coreGrooveQty-1]){
        rotate([0, 0, 360/coreGrooveQty*n])
        linear_extrude(cylHeight+clipHeight+2*z,  twist=360*(cylHeight+clipHeight-coreBottomOffset+2*z)/(PI*(coreID+Offset))*(n%2==0?1:-1), $fn=surfaceFn)
        translate([coreID/2+Offset/2, 0, -z])
        translate([0, 0, -z])
        circle(d=coreGrooveD, $fn=grooveFn);
    }
}

module CoreChamferShape(Offset){
    cylinder(d1=coreID+Offset+2*coreChamfer, d2=coreID+Offset, h=coreChamfer+z, $fn=surfaceFn);
}

module CoreChamfer(Offset){
    translate([0, 0, coreBottomOffset-z])
    CoreChamferShape(Offset);
    translate([0, 0, cylHeight+clipHeight+z])
    rotate([180, 0, 0])
    CoreChamferShape(Offset);
}

module CoreEllipses(){
    $fn=surfaceFn;
    for (n=[0:coreWebQty-1])
    rotate([0, 0, n*360/coreWebQty])
    translate([0, 0, coreBottomOffset+(cylHeight-coreBottomOffset+clipHeight)/2-coreWebLength/2])
    rotate([90, 0, 90])
    hull(){
        translate([0, coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
        translate([0, coreWebLength-coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
    }
}

module SpeedHoles(){
    for (n=[0:speedHoleQty-1])
    rotate([0, 0, 360/speedHoleQty*n])
    translate([speedHoleRadial, 0, -z+(n==0?cylHeight/2:0)])
    cylinder(d=speedHoleID, h=cylHeight+2*z, $fn=surfaceFn);
}

module HollowSpace(){
    $fn=surfaceFn;
    difference(){
        rotate_extrude()
        polygon([[coreID/2+wallMinThickness, wallMinThickness+wallChamfer+coreBottomOffset], [coreID/2+wallMinThickness, cylHeight-wallMinThickness-wallChamfer], [coreID/2+wallMinThickness+wallChamfer, cylHeight-wallMinThickness], [(coreID+cylOD)/4, cylHeight-wallMinThickness+roofOffset], [cylOD/2-wallMinThickness-wallChamfer, cylHeight-wallMinThickness], [cylOD/2-wallMinThickness, cylHeight-wallMinThickness-wallChamfer], [cylOD/2-wallMinThickness, wallMinThickness+wallChamfer], [cylOD/2-wallMinThickness-wallChamfer, wallMinThickness], [coreID/2+wallMinThickness+wallChamfer, wallMinThickness+coreBottomOffset]]);
        
        translate([drivePinRadial, 0, 0])
        cylinder(d=drivePinCountersinkID+2*drivePinSupportRadialOffset, h=drivePinCountersinkDepth+drivePinSupportHeight, $fn=surfaceFn);
    }
}


module BottomSlopedSpace(){
    $fn=surfaceFn;
    rotate_extrude(){
        polygon([[0, -z-5], [0, coreBottomOffset], [bottomX(coreBottomOffset), coreBottomOffset], [cylOD/2-wallMinThickness-wallChamfer, 0], [cylOD/2-wallMinThickness-wallChamfer+5, 0], [cylOD/2-wallMinThickness-wallChamfer+5, -z-5]]);
    }
}

module TopMinkCleanup(){
    translate([0, 0, cylHeight]){
        difference(){
            cylinder(d=cylOD, h=5);
            cylinder(d=cylOD-15, h=15, center=true);
        }
    }
}

module DrivePin(Offset){
linear_extrude(5)
    translate([drivePinRadial, 0, -z])
    rotate([0, 0, 90])
    square([drivePinWidth, drivePinLength], center=true);
    
    translate([drivePinRadial, 0, -z])
    cylinder(d=drivePinCountersinkID, h=z+drivePinCountersinkDepth, $fn=surfaceFn);
}

module Additive(){
    union(){
        AssembleMinkowski();
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
    }
}

module FullElement(){
    difference(){
        Additive();
        Subtractive();
    }
}

module ResinRod(h){
    $fn=resinFn;
    hull(){
    translate([0, 0, -resinTipOD/2+resinInset+h]){
            sphere(d=resinTipOD);
            translate([0, 0, -resinTipL])
            sphere(d=resinRodOD);
        }
        translate([0, 0, -resinMinRodHeight-resinRaftThickness+resinRodOD/2+z])
        sphere(d=resinRodOD);
    }
//        translate([0, 0, -resinMinRodHeight-resinRaftThickness])
//        cylinder(d1=resinRaftOD, d2=resinRaftOD+2*resinRaftThickness, h=resinRaftThickness);
}

module CutGroove(){
    $fn=surfaceFn;
    rotate_extrude()
    translate([cylOD/2-wallMinThickness, 0, 0])
    difference(){
        polygon([[-cylOD/2+wallMinThickness, -resinMinRodHeight-resinRaftThickness], [-cylOD/2+wallMinThickness, -resinMinRodHeight], [0, -resinMinRodHeight], [wallMinThickness-resinGrooveOD-resinGrooveThickness, -resinGrooveOD], [wallMinThickness-resinGrooveOD-resinGrooveThickness, z], [wallMinThickness, z], [wallMinThickness, -resinMinRodHeight], [wallMinThickness+resinRaftThickness, -resinMinRodHeight], [wallMinThickness, -resinMinRodHeight-resinRaftThickness]]); 
        translate([wallMinThickness, -resinGrooveOD/2])
        circle(d=resinGrooveOD);
        translate([wallMinThickness-resinGrooveOD-resinGrooveThickness, -resinGrooveOD/2])
        circle(d=resinGrooveOD);
   }
}

module SpeedHoleSupport(){
    translate([speedHoleRadial+speedHoleID/2+resinTipOD/2, 0, 0])
    ResinRod(bottomZ(speedHoleRadial+speedHoleID/2+resinTipOD/2));
    translate([speedHoleRadial-speedHoleID/2-resinTipOD/2, 0, 0])
    ResinRod(bottomZ(speedHoleRadial-speedHoleID/2+-resinTipOD/2));
    translate([speedHoleRadial, speedHoleID/2+resinTipOD/2, 0])
    ResinRod(bottomZ((speedHoleRadial^2+(speedHoleID/2+resinTipOD/2)^2)^.5));
    translate([speedHoleRadial, -speedHoleID/2-resinTipOD/2, 0])
    ResinRod(bottomZ((speedHoleRadial^2+(-speedHoleID/2-resinTipOD/2)^2)^.5));
}

module SpeedHoleSupports(){
    for (n=[0:speedHoleQty-1])
    if (n!=0)
    rotate([0, 0, 360/speedHoleQty*n])
    SpeedHoleSupport();
}



module DrivePinSupport(){
    translate([drivePinRadial+drivePinCountersinkID/2+resinTipOD/2, 0, 0])
    ResinRod(bottomZ(drivePinRadial+drivePinCountersinkID/2+resinTipOD/2));
    translate([drivePinRadial-drivePinCountersinkID/2-resinTipOD/2, 0, 0])
    ResinRod(bottomZ(drivePinRadial-drivePinCountersinkID/2-resinTipOD/2));
    translate([drivePinRadial, drivePinCountersinkID/2+resinTipOD/2, 0])
    ResinRod(bottomZ((drivePinRadial^2+(drivePinCountersinkID/2+resinTipOD/2)^2)^.5));
    translate([drivePinRadial, -drivePinCountersinkID/2-resinTipOD/2, 0])
    ResinRod(bottomZ((drivePinRadial^2+(-drivePinCountersinkID/2-resinTipOD/2)^2)^.5));
}

module BottomSupports(){
    for (n=[0:speedHoleQty-1]){
        rotate([0, 0, (n+.5)*360/speedHoleQty]){
            a=bottomX(coreBottomOffset);
            b=cylOD/2-wallMinThickness-wallChamfer;
            for (s=[a:(b-a)/4:b])
            translate([s, 0, 0])
            ResinRod(bottomZ(s));
        }
        rotate([0, 0, (n)*360/speedHoleQty])
        translate([coreID/2+coreChamfer+resinTipOD/2, 0, 0])
        ResinRod(coreBottomOffset);
    }
}

module ResinSupport(){
    union(){
        CutGroove();
        SpeedHoleSupports();
        DrivePinSupport();
        BottomSupports();
    }
}

module CylinderGauge(Offset){
    translate([0, 0, coreBottomOffset])
    cylinder(d=coreID+2*wallMinThickness+Offset, h=cylHeight+clipHeight-coreBottomOffset, $fn=surfaceFn);
}

module GaugeResinSupport(Offset){
    $fn=resinFn;
    for (n=[0:7]){
        rotate([0, 0, n*360/8])
        translate([coreID/2+Offset/2+wallMinThickness/2, 0, 0])
        ResinRod(coreBottomOffset);
    }
}

module GaugeResinSupportsRaft(){
    translate([0, 0, -resinMinRodHeight-resinRaftThickness])
    cylinder(d1=3*(coreID+2*wallMinThickness), d2=3*(coreID+2*wallMinThickness)+2*resinRaftThickness, h=resinRaftThickness);
}

module RevolverSolid(){
    $fn=surfaceFn;
    hull(){
        for (n=[0:5])
        rotate([0, 0, n*360/6])
        translate([coreID+wallMinThickness*2-wallMinThickness/2, 0, 0])
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
    translate([coreID/2+wallMinThickness-wallMinThickness/2+secondaryCoreIDOffset/2, 0, coreBottomOffset+(cylHeight+clipHeight-coreBottomOffset)/2])
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
                translate([coreID+wallMinThickness*2-wallMinThickness/2, 0, 0])
                GaugeTestSubtractive(gaugeOffsetStart+(n)*gaugeOffsetInt);
            }
        }
        
        union(){
            for (n=[0:5]){
                rotate([0, 0, n*360/6])
                translate([coreID+wallMinThickness*2-wallMinThickness/2, 0, 0])
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
    testString=str(DHIATENSOR[0], DHIATENSOR[1], DHIATENSOR[2]);
    for (n=[0:len(testString)-1]){
        translate([1/testCPI*25.4*n, 0, 0])
        text(text=testString[n], size=testSize, font=testFont, halign="center", valign="baseline", $fn=textFn);
    }
}

//render
module Render(){
    difference(){
        color("lightblue")
        if (renderMode==0) FullElement();
        else if (renderMode==1) ResinPrint();
        else if (renderMode==2) GaugeTestSet();
        else if (renderMode==3)
        TypeTest();
        if (xSection==true){
            rotate([0, 0, xSectionTheta])
            translate([-50, -100, -50])
            cube(100);
        }
    
    }
}

if (render==true) Render();