//Split Hammond 1 Shuttle
//Leonard Chau
//Jan 14, 2026
        
/* [Rendering] */
//render something?
render=false;
//render mode
renderMode=1;//[0:Normal, 1:ResinPrint];
//which parts?
renderSides=0;//[0:Both, 1:Left, 2:Right];
//apply text chamfer?
minkText=false;
//mink draft angle
minkAngle=60;
//mink cone height
minkHeight=2;
//mink radius
minkRadius=tan(minkAngle/2)*minkHeight;
//to fix z fighting
z=.01;
cylFn=120;
minkFn=20;
textFn=30;

/* [Element Layout] */
idealElement=["?zxqkjgdmpcfld,.taherisounwyv:",
       "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
       "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔"];
        
qwertyElement = ["qazwsxedcrfvtgbyhnujmik,ol.p;-",
          "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
          "1\"@2#⅌3$+4%£5_¢6&*7'§8(°9).0=/"];
          
layouts = [[0, idealElement],
            [1, qwertyElement]];
layoutSelection = 0; //[0:Ideal, 1:Qwerty]
layout=layouts[layoutSelection][1];

/* [Font/Typeface] */
//font name
typeFace="Average Mono";
//font size
typeSize=2.95;
//modified characters
charMod="⅌";
//modified character font
charModFont="Noto Sans Mono";
//modified character size
charModSize=2.7;

/* [Dimensions] */
//baseline gaps
baselineGaps=[9.45, 4.725, 0];
//baseline offset
baselineOffset=-1.9;
//baselines
baselines=baselineGaps+[baselineOffset, baselineOffset, baselineOffset];
//pin hole diameter
pinIDmm=1.92;
//pin hole radial distance
pinRadial=7.95;
//pin holes angular positions
pinTheta=[68.2683, 109.968];
//pin hole chamfer
pinIDChamfer=.25;
//left and right tube diameters
tubeODmm=[6.6548, 5.842];
//tube chamfer size
tubeChamfer=.5;
//arc diameter
arcOD=75;
//arc thickness
arcThickness=1.6;
//arc height
arcHeight=13.26;
//arc height offset
arcHeightOffset=-2.62;
//folder degree offset from center
folderDegreeOffset=8.3;
//folder degree rotational extrusion
folderDegrees=115.8;
//folding section ID
folderIDmm=12;
//folding section OD
folderOD=21;
//folder thickness
folderThickness=9.525;
//folder close angular gap
folderCloseGap=6;
folderArcStart=folderCloseGap/2;
//glyph height
glyphHeight=.8;
//alignment finger tip width
fingerThickness=1.8;
//spoke thickness
spokeThickness=2.2;
//spoke height
spokeHeight=8.3;
//spoke count
spokeCount=5;
//spoke angular extent
spokeExtent=45;
//spoke spacing
spokeSpacing=spokeExtent/(spokeCount-1);
//spoke chamfer size
spokeChamfer=1.5;
//rib OD
ribOD=46.8;
//rib thickness
ribThickness=2.6;
//rib radius
ribRadius=1;
//degrees per character
charTheta=360/96;


/* [Logo] */
//enable logo?
logo=true;
//logo text
logoText="Leonard Chau 2025";
//logo font
logoFont="OCR\\A-II";
//logo size
logoSize=1.9;
//logo depth
logoDepth=.3;

/* [Resin Offsets] */
//tube and pin offset
IDOffset=.13;
//folder radial offset
folderRadialGap=.4;
//folder squash/sandwich offset
folderSquashClearance=.3;

//correction for tube and pin diameters
tubeOD=tubeODmm+[IDOffset, IDOffset];
pinID=pinIDmm+IDOffset;
//left and right folder IDs
folderID=[folderIDmm+folderRadialGap, folderIDmm-folderRadialGap];


/* [Resin Supports] */
//rod diameter
rodOD=1.0;
//tip diameter
tipOD=.6;
//tip length
tipLength=1;
//tip inside part distance
tipIn=.3;

/* [Handy Variables] */
folderHalfThickness=(folderThickness-folderSquashClearance)/2;
arcStart=asin(fingerThickness/arcOD);
arcEnd=15*charTheta+charTheta/2;
arc=arcEnd-arcStart;
folderArcEnd=folderDegrees+folderDegreeOffset;
folderArc=folderArcEnd-folderArcStart;

module Arc(extra){
    rotate_extrude(15*charTheta+charTheta/2)
    translate([arcOD/2-arcThickness, arcHeightOffset])
    square([arcThickness+extra, arcHeight]);
}

module Center(){
    cylinder(d=folderOD, h=folderThickness);
}

module Spoke2D(){
    scale([spokeThickness, spokeHeight])
    circle(d=1);
}

module SpokeChamfer(){
    hull(){
        translate([0, 0, spokeChamfer])
        linear_extrude(z)
        scale([(spokeThickness+2*spokeChamfer)/spokeThickness, (spokeHeight+2*spokeChamfer)/spokeHeight])
        Spoke2D();
        linear_extrude(z)
        Spoke2D();
    }
}

module Spoke(){
    translate([0, 0, folderThickness/2])
    rotate([90, 0, 90]){
        linear_extrude(arcOD/2-arcThickness+z)
        Spoke2D();
        translate([0, 0, arcOD/2-arcThickness-spokeChamfer])
        SpokeChamfer();
    }
}

module SpokeArranged(){
    rotate([0, 0, folderDegreeOffset])
    for (i=[0:spokeCount-1])
        rotate([0, 0, i*spokeSpacing])
        Spoke();
} 

module Rib(){
    a=5;//outer angular padding for rib
    b=4;//inner thickness for rib
    hull(){
        rotate([0, 0, folderDegreeOffset-a/2])
        rotate_extrude(spokeExtent+a)
        translate([ribOD/2-ribRadius, folderThickness/2])
        circle(r=ribRadius);
        
        rotate([0, 0, folderDegreeOffset])
        rotate_extrude(120)
        translate([folderOD/2-b/2-z, folderThickness/2])
        circle(d=b);
    }
    
    hull(){
        rotate([0, 0, folderDegreeOffset])
        rotate_extrude(spokeExtent)
        translate([folderOD/2-z, 0, 0])
        polygon([[0,folderThickness/2-spokeHeight/2], [0,folderThickness/2+spokeHeight/2], [folderThickness/2, folderThickness/2]]);
        
        translate([0, 0, folderThickness/2])
        rotate([-90, 0, 0])
        cylinder(d=3, h=10.5);
    }
}

module Text(char, font, size){
    mirror([1, 0, 0])
    text(char, font=font, size=size, halign="center", valign="baseline");
}

module TextPlacement(angle, height){
    rotate([0, 0, angle])
    translate([arcOD/2-1, 0, height])
    rotate([90, 0, 90])
    children();
}

module LetterText(char, font, size){
    difference(){
        minkowski(){
            linear_extrude(glyphHeight+1)
            Text(char, font, size);
            
            if (minkText==true){
                translate([0, 0, -minkHeight])
                cylinder(r1=minkRadius, r2=0, h=minkHeight, $fn=minkFn);
            }
        }
        
        translate([0, 0, -10])
        cube(20, center=true);
    }
}


module TextAssemble(side){
    //for (side=[0, 1])
    for (baseline=[0, 1, 2])
    for (int=[0:14]){
        height=baselines[baseline];
        angle=side==0?
            ((1+int)*charTheta): /*left side*/
            ((-1-(14-int))*charTheta); //right side
        char=side==0?
            layout[baseline][14-int]: /*left side*/
            layout[baseline][29-int];
        ismod=search(char, charMod)==[]?false:true;
        font=ismod?charModFont:typeFace;
        size=ismod?charModSize:typeSize;
        
        TextPlacement(angle, height)
        LetterText(char, font, size);
    }
}

module TextRing(side){
    intersection(){
        TextAssemble(side);
        Mirror(side)
        Arc(glyphHeight+1);
    }
}

module Tube(side){
    chamferbump=side==0?-z:(folderHalfThickness+folderSquashClearance);
    translate([0, 0, -z])
    cylinder(d=tubeOD[side], h=25);
    translate([0, 0, chamferbump]){
        translate([0, 0, -z])
        cylinder(d1=tubeOD[side]+2*tubeChamfer, d2=tubeOD[side], h=tubeChamfer+z);
        translate([0, 0, folderHalfThickness-tubeChamfer])
        cylinder(d2=tubeOD[side]+2*tubeChamfer, d1=tubeOD[side], h=tubeChamfer+z);
    }
}

module FolderClearance(side){
    //height offset of cylinder
    hoffset=side==0?(folderThickness/2-folderSquashClearance/2):-z;
    //start height of cylinder
    hstart=side==0?hoffset:-z;
    //height of cylinder
    h=side==0?15:(z+folderThickness/2+folderSquashClearance/2);
    translate([0, 0, hstart])
    cylinder(d=folderID[0], h=h);
}

module FolderCutaway(side){
    r=30;
    angles=[folderArcStart, folderArcEnd];
    xy=[[cos(angles[0])*r, sin(angles[0])*r], [cos(angles[1])*r, sin(angles[1])*r]];
    
    
    difference(){
        Mirror(side)
        translate([0, 0, -5])
        linear_extrude(25)
        polygon([xy[0], [0,0], xy[1], [-r, r], [-r, -r], [r, -r]]);
        
        translate([0, 0, -20])
        cylinder(d=folderID[1], h=40);
    }
}

module Finger(){
    translate([arcOD/2-5, -fingerThickness/2, -10])
    cube([10, fingerThickness, 40]);
}

module PinHole(){
    translate([0, 0, -z]){
        cylinder(h=20, d=pinID);
        cylinder(d1=pinID+2*pinIDChamfer, d2=pinID, h=pinIDChamfer);
    }
    translate([0, 0, folderThickness-pinIDChamfer])
    cylinder(d1=pinID, d2=pinID+2*pinIDChamfer, h=pinIDChamfer+z);
}

module PinHoles(side){
    Mirror(side)
    for (pin=[0,1]){
        rotate([0, 0, pinTheta[pin]])
        translate([pinRadial, 0, 0])
        PinHole();
    }
}

module GlueHoles(side){
    height=side==0?folderHalfThickness/2:folderThickness-folderHalfThickness/2;
    holer=.8;
    translate([0, 0, height])
    Mirror(side)
    for (n=[0, 180])
    rotate([0, 90, folderArcStart-(360-folderArc)/2+90+n]){
        cylinder(h=folderID[1]/2, r=holer);
        translate([0, 0, folderID[1]/2-pinIDChamfer])
        cylinder(r1=holer, r2=holer+2*pinIDChamfer, h=pinIDChamfer);
    }
}

module GlueGroove(side){
    groover=.8;
    groovein=.2;
    height=side==0?folderHalfThickness/2:folderThickness-folderHalfThickness/2;
    translate([0, 0, height])
    rotate_extrude()
    translate([tubeOD[side]/2-groover+groovein, 0, 0])
    circle(r=groover);
}

module Mirror(side){
    if (side==1)
        mirror([0, 1, 0])
        children();
    else
        children();
}

module LeftAdditive(){
    $fn=cylFn;
    union(){
        Arc(0);
        Center();
        SpokeArranged();
        Rib();
    }
}

module Additive(side){
    union(){
        Mirror(side)
        LeftAdditive();
        TextRing(side);
    }
}

module Subtractive(side){
    $fn=120;
    union(){
        Tube(side);
        FolderClearance(side);
        FolderCutaway(side);
        Finger();
        PinHoles(side);
        GlueHoles(side);
        GlueGroove(side);
    }
}

module AssembleHalf(side){
    difference(){
        Additive(side);
        Subtractive(side);
    }
}

module ResPrintOrient(side){
    pole=side==0?-1:1;
    rotate([0, -90, 0])
    rotate([0, 0, pole*(arcStart+arc/2)])
    children();
}

module Assemble(){
    AssembleSide(0);
    AssembleSide(1);
}

module ResinSupports(side){

}

module ResinPrintHalf(side){
    ResPrintOrient(side)
    AssembleHalf(side);
    ResinSupports(side);
}

module Render(){
    if (render==true){
        if (renderMode==0)
            Assemble();
        if (renderMode==1)
            ResinPrintHalf(0);
    }
}



//FolderCutaway(0);

//Subtractive(0);
//color("red")
//translate([0, z, 0])
//ResPrintOrient(1)
//Assemble(1);
//translate([0, -z, 0])
Assemble(0);
//Subtractive(0);