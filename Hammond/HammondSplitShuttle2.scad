//Split Hammond 1 Shuttle
//Leonard Chau
//Jan 14, 2026
        
/* [Rendering] */
//render something?
render=false;
//render mode
renderMode=1;//[0:Normal, 1:ResinPrint]
//render left shuttle?
renderLeft=true;
//render right shuttle?
renderRight=true;
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
resinFn=20;

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
folderGlueHoleIDmm=1.15;
folderGlueGrooveR=.8;
folderGlueGrooveDepth=.2;
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
logoText1="Leonard Chau";
logoText2="2025";
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

folderGlueHoleID=folderGlueHoleIDmm+IDOffset;



/* [Resin Supports] */
//resin rod diameter
resinRodOD=.8;
//resin tip diameter
resinTipOD=.4;
//resin tip length
resinTipL=1;//.1
//resin rod inset in part
resinInset=.3;
//resin rod minimum height
resinMinRodHeight=2;
//resin rod base diameter
resinRaftOD=4;
//resin rod raft thickness
resinRaftThickness=2;

/* [Handy Variables] */
folderHalfThickness=(folderThickness-folderSquashClearance)/2;
arcStart=asin(fingerThickness/arcOD);
arcEnd=15*charTheta+charTheta/2;
arc=arcEnd-arcStart;
folderArcEnd=folderDegrees+folderDegreeOffset;
folderArc=folderArcEnd-folderArcStart;

/* [Resin Support Variables] */
resZRaise=folderID[1]/2;
//for orienting the shuttle in the x direction
resXRot=(arcStart+arc/2);
//folder support limits
resFolderLims=[-folderArcStart-resXRot, -folderArcStart-resXRot+folderArc];
resSpacing=6;
resAngle=45;

function YZ(r, theta) = [sin(theta)*r, cos(theta)*r];

//number of yx pts on arc
resArcDiv=[15, 4];
//number of yx on folder
resFolderDiv=[12, 2];
//number of yx pts on folder face
resFolderFaceDiv=[3, 4];
//number of yx pts on ring
resRingDiv=[8, 3];
resRingStartEnd=[-45, 45];

resArcYPts=[for (theta=[-arc/2:arc/(resArcDiv[0]-1):arc/2]) YZ((arcOD/2-arcThickness), theta)[0]];
resArcThetaPts=[for (theta=[-arc/2:arc/(resArcDiv[0]-1):arc/2]) theta];
resArcZPts=[for (theta=[-arc/2:arc/(resArcDiv[0]-1):arc/2]) YZ((arcOD/2-arcThickness), theta)[1]];
resArcXPts=[for (x=[0:resArcDiv[1]-1]) arcHeightOffset+arcHeight/(resArcDiv[1]-1)*x];

resFolderFaceXPts=[for (x=[0:(resFolderFaceDiv[1]-1)]) x*folderThickness/(resFolderFaceDiv[1]-1)];
resFolderFaceRPts=[for (r=[0:(resFolderFaceDiv[0]-1)]) folderID[0]/2+r*(folderOD/2-folderID[0]/2)/(resFolderFaceDiv[0]-1)];
resFolderFaceYPts=[for (r=[0:(resFolderFaceDiv[0]-1)]) YZ(resFolderFaceRPts[r], folderArcEnd-resXRot)[0]];
resFolderFaceZPts=[for (r=[0:(resFolderFaceDiv[0]-1)]) YZ(resFolderFaceRPts[r], folderArcEnd-resXRot)[1]];

resFolderXPts=[for (x=[0:(folderHalfThickness+folderSquashClearance)/(len(resFolderDiv)):folderHalfThickness+folderSquashClearance]) x];
resFolderThetaPts=[for (theta=[folderArcStart-resXRot:folderArc/(resFolderDiv[0]-1):folderArcEnd-resXRot]) theta];
resFolderYPts=[for (y=[0:resFolderDiv[0]-1]) YZ(folderID[0]/2, resFolderThetaPts[y])[0]];
resFolderZPts=[for (y=[0:resFolderDiv[0]-1]) YZ(folderID[0]/2, resFolderThetaPts[y])[1]];

resRingXPts=[for (x=[0:folderHalfThickness/(resRingDiv[1]-1):folderHalfThickness]) x];
resRingThetaPts=[for (theta=[resRingStartEnd[0]:(resRingStartEnd[1]-resRingStartEnd[0])/(resRingDiv[0]-1):resRingStartEnd[1]]) theta];
resRingYPts=[for (y=[0:len(resRingThetaPts)-1]) YZ(folderID[1]/2, resRingThetaPts[y])[0]];
resRingZPts=[for (y=[0:len(resRingThetaPts)-1]) -YZ(folderID[1]/2, resRingThetaPts[y])[1]];
echo(resRingZPts);






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
    folderGlueHoleID=.8;
    translate([0, 0, height])
    Mirror(side)
    for (n=[0, 180])
    rotate([0, 90, folderArcStart-(360-folderArc)/2+90+n]){
        cylinder(h=folderID[1]/2, d=folderGlueHoleID);
        translate([0, 0, folderID[1]/2-1])
        cylinder(d1=folderGlueHoleID, d2=folderGlueHoleID+2*pinIDChamfer, h=1);
    }
}

module GlueGroove(side){
    height=side==0?folderHalfThickness/2:folderThickness-folderHalfThickness/2;
    translate([0, 0, height])
    rotate_extrude()
    translate([tubeOD[side]/2-folderGlueGrooveR+folderGlueGrooveDepth, 0, 0])
    circle(r=folderGlueGrooveR);
}

module Logo(side){
    if (logo==true)
    
//    translate
    rotate([0, 0, (side==0?1:-1)*folderArcStart])
    translate([16, 0, folderThickness/2])
    rotate([90, 0, side==0?0:180])
    linear_extrude(logoDepth*2, center=true){
    translate([0, 0, 0])
    text(text=logoText1, size=logoSize, font=logoFont, halign="center", valign="center");
    translate([0, -2, 0])
    text(text=logoText2, size=logoSize, font=logoFont, halign="center", valign="center");
    }
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
        Logo(side);
    }
}

module AssembleSide(side){
    difference(){
        Additive(side);
        Subtractive(side);
    }
}

module ResPrintOrient(side){
    pole=side==0?-1:1;
    translate([0, 0, resZRaise])
    rotate([0, -90, 0])
    rotate([0, 0, pole*resXRot])
    children();
}

module Assemble(){
    if (renderLeft)
    AssembleSide(0);
    if (renderRight)
    AssembleSide(1);
}

function ResYOffset(theta)= -sin(theta)*(resinTipL+resinTipOD/2-resinInset);
function ResZOffset(theta) = -cos(theta)*(resinTipL+resinTipOD/2-resinInset);

module ResinTip(theta){
    hull(){
        rotate([-theta, 0, 0])
        translate([0, 0, -resinTipOD/2+resinInset]){
            sphere(d=resinTipOD);
            translate([0, 0, -resinTipL])
            sphere(d=resinRodOD);
        }
    }
}

module ResinRod(h, theta){
    $fn=resinFn;
    
    translate([0, 0, h])
    ResinTip(theta);
    
    ResinRodClean(h, theta);
    
    translate([0, ResYOffset(theta), -resinMinRodHeight-resinRaftThickness])
    cylinder(d1=resinRaftOD, d2=resinRaftOD+2*resinRaftThickness, h=resinRaftThickness);
    
}

module ResinRodClean(h, theta){
    $fn=resinFn;
    
    hull(){
        translate([0, 0, -resinMinRodHeight-ResZOffset(theta)])
        rotate([-theta, 0, 0])
        translate([0, 0, -resinTipOD/2+resinInset])
        translate([0, 0, -resinTipL])
        sphere(d=resinRodOD);
        
        translate([0, 0, h])
        rotate([-theta, 0, 0])
        translate([0, 0, -resinTipOD/2+resinInset])
        translate([0, 0, -resinTipL])
        sphere(d=resinRodOD);
        }
}

module ResinFenceTopSphere(h, theta){
    $fn=resinFn;
    translate([0, 0, h])
    rotate([-theta, 0, 0])
    translate([0, 0, -resinTipOD/2+resinInset])
    translate([0, 0, -resinTipL])
    sphere(d=resinRodOD);
}

resFenceTopOffset=0;

module ResinFenceArcTop(){
    
    for (yint=[1:len(resArcYPts)-1]){
            hull(){
            translate([0, resArcYPts[yint], 0])
            ResinFenceTopSphere(resArcZPts[yint]+resZRaise-resFenceTopOffset, resArcThetaPts[yint]);
            translate([0, resArcYPts[yint-1], 0])
            ResinFenceTopSphere(resArcZPts[yint-1]+resZRaise-resFenceTopOffset, resArcThetaPts[yint-1]);
            }
        }
    
}

module ResinFenceArcSide(yint){
    hull(){
        for (xint=[0,len(resArcXPts)-1])
        translate([-resArcXPts[xint], 0, 0])
        ResinFenceTopSphere(resArcZPts[0]+resZRaise-resFenceTopOffset, resArcThetaPts[yint]);
        }
}


module ResinArcSupports(){
    for (xint=[0:len(resArcXPts)-1])
    for (yint=[0:len(resArcYPts)-1])
    if (xint==0 || xint==len(resArcXPts)-1 || yint==0 || yint==len(resArcYPts)-1)
    translate([-resArcXPts[xint], resArcYPts[yint], 0])
    ResinRod(resArcZPts[yint]+resZRaise, resArcThetaPts[yint]);
}

module ResinArcFenceSupport(){
    for (xint=[0,len(resArcXPts)-1])
    translate([-resArcXPts[xint], 0, 0]){
        intersection(){
            ResinKeepY();
            ResinFence();
        }
    
        ResinFenceArcTop();
    }

    for (yint=[0,len(resArcYPts)-1])
    translate([0, resArcYPts[yint], 0]){
        intersection(){
            ResinKeepX(yint);
            translate([0, ResYOffset(resArcThetaPts[yint]), 0])
            rotate([0, 0, 90])
            ResinFence();
        }
        ResinFenceArcSide(yint);
    }
}

module ResinKeepY(){
    hull(){
        for (yint=[0:len(resArcYPts)-1])
        translate([0, resArcYPts[yint], 0])
        ResinRodClean(resArcZPts[yint]+resZRaise-resFenceTopOffset, resArcThetaPts[yint]);
    }
}

module ResinKeepX(yint){
    hull(){
        for (xint=[0,len(resArcXPts)-1])
        translate([-resArcXPts[xint], 0, 0])
        ResinRodClean(resArcZPts[0]+resZRaise-resFenceTopOffset, resArcThetaPts[yint]);
    }
}

module ResinParallelBars(){
    $fn=resinFn;
    for (n=[-20:20])
    translate([0, n*resSpacing, 0])
    cylinder(d=resinRodOD, h=100, center=true);
}

module ResinFence(){
    rotate([-resAngle, 0, 0])
    ResinParallelBars();
    rotate([resAngle, 0, 0])
    ResinParallelBars();
}


module ResinFolderSupports(side){
    Mirror(side)
    for (xint=[0:len(resFolderFaceXPts)-1])
    for (yint=[0:len(resFolderFaceYPts)-1]){
        if (side == 0 && (yint!=0 || (xint+1)/len(resFolderFaceXPts)>.5))
            translate([-resFolderFaceXPts[xint], resFolderFaceYPts[yint], 0])
            ResinRod(resFolderFaceZPts[yint]+resZRaise, folderArcEnd-resXRot-90);
        
        if (side == 1 && (yint!=0 || (xint+1)/len(resFolderFaceXPts)<=.5))
            translate([-resFolderFaceXPts[xint], resFolderFaceYPts[yint], 0])
            ResinRod(resFolderFaceZPts[yint]+resZRaise, folderArcEnd-resXRot-90);
    }
        
    for (xint=[0:len(resFolderXPts)-1])
    for (yint=[0:len(resFolderYPts)-1]){
        if (side==0 && xint!=0 && yint!=len(resFolderYPts)-1) 
            translate([-resFolderXPts[xint]-folderHalfThickness, resFolderYPts[yint], 0])
            ResinRod(resFolderZPts[yint]+resZRaise, yint==0?0:resFolderThetaPts[yint]);
        
        if (side==1 && xint!=len(resFolderXPts)-1 && yint!=len(resFolderYPts)-1)
            Mirror(side)
            translate([-resFolderXPts[xint], resFolderYPts[yint], 0])
            ResinRod(resFolderZPts[yint]+resZRaise, yint==0?0:resFolderThetaPts[yint]);
    }
}

module ResinRingSupports(side){
    for (xint=[0:len(resRingXPts)-1])
    for (yint=[0:len(resRingYPts)-1]){
        if (side==0)
            translate([-resRingXPts[xint], -resRingYPts[yint], 0])
            ResinRod(resRingZPts[yint]+resZRaise, resRingThetaPts[yint]);
        if (side==1)
            translate([-resRingXPts[xint]-(folderHalfThickness+folderSquashClearance), -resRingYPts[yint], 0])
            ResinRod(resRingZPts[yint]+resZRaise, resRingThetaPts[yint]);
    }
}

module ResinSupports(side){
    ResinArcSupports();
    ResinFolderSupports(side);
    ResinRingSupports(side);
    ResinArcFenceSupport();
}



module ResinPrintHalf(side){
    ResPrintOrient(side)
    AssembleSide(side);
    ResinSupports(side);
}

module AssembleResin(){
    translate([0, 7, 0])
    rotate([0, 0, -90])
    ResinPrintHalf(0);
    translate([0, -7, 0])
    rotate([0, 0, 90])
    ResinPrintHalf(1);
}

module Render(){
    if (render==true){
        if (renderMode==0)
            Assemble();
        if (renderMode==1)
            AssembleResin();
    }
}

Render();

//    ResinPrintHalf(1);


//FolderCutaway(0);

//Subtractive(0);
//color("red")
//translate([0, z, 0])
//ResPrintOrient(1)
//Assemble(1);
//translate([0, -z, 0])
//Assemble(0);
//Subtractive(0);