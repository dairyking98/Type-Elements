//Split Hammond 1 Shuttle
//Leonard Chau
//February 17, 2024
        
/* [Checks] */
Assert=true;
No_Chamfer=true;
cyl_fn=360;
text_fn=30;
mink_fn=20;
z=.01;
resin_fn=20;
testing=false;
testingchar=".";

Generate_Left_Shuttle=true;
Generate_Right_Shuttle=true;

/* [Character Details] */
//Layout as "stamped"
//LAYOUT=["?zxqkjgdmpcfld,.taherisounwyv:",
//        "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
//        "¾%⅞⅝½⅜1⅛2¢3⅌4$56“7”8’9[0]¼*⅓†⅔"];

LAYOUT=["?zxqkjgdmpcfld,.taherisounwyv:",
        "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔"];

Typeface="Average Mono";
Typesize=2.95;
Baseline_Gaps=[9.45, 4.725, 0];
Baseline_Offset=-1.9;
Baselines=Baseline_Gaps+[Baseline_Offset, Baseline_Offset, Baseline_Offset];
//Baselines=[9.52+Baseline_Offset, 4.74+Baseline_Offset, -.04+Baseline_Offset];//.02=

CharMod="⅌";
CharModFont="Noto Sans Mono";
CharModSize=2.7;




/* [Dimensions] */
Posthole_ID=1.92;// 5/64 wire rod
PostholeID_ResinOffset=.25;
OD_InnerTube=5.842+.17;//measurement + clearance
OD_OuterTube=6.6548+.17;//measurement + clearance

Tube_Clearance=.05;

OD=75.0;
Shuttle_Thickness=1.6;
Shuttle_Width=13.26;
Folder_Thickness=9.525;// 3/8 thick
Folder_ID=12;//9.6;
Folder_OD=18.762;
Folder_Clearance=0.4;
Folder_SquashClearance=.2794;//.0001 //.5 for Full 3D
Folder_UpsideDownOffset=.0889;
FolderLocation=.5;//.2 for Full 3D, .5 for metal tube
Tube_ChamferSize=.5;

Glyph_Depth=.8;
Finger_Thickness=1.8;// 

Spoke_Thickness=2.2;
Spoke_Height=8.3;
Spoke_Count=5;
Spoke_Spacing=45/4;
OuterSpokeChamferSize=1.5;

Rib_Diameter=46.8;
Rib_Thickness=2.6;

//Tube length to bottom of folder
Tube_Length=24.2;
Tube_ID=5.05;
Tube_IDResinOffset=.25;
Tube_OD=6.6;


MyTube_OD=8;
MyFolder_ID=11;



/* [Logo] */
Logo=true;
Line="Leonard Chau 2024";
Line2="2024";
LineFont="OCR\\-A II";
LineSize=1.9;//.1
LogoDepth=.3;



/* [Constants] */
Theta_Offset=8.3;
Theta=115.8;
Pin1=72.3;
Pin2=112.0;
Pin_Radius=7.6895;

Finger_Offset=asin((Finger_Thickness/2)/((OD-2*Shuttle_Thickness)/2))/2;//why /2????
//asin(Finger_Thickness/(2*(OD-2*Shuttle_Thickness)/2));
Char_Theta=360/96;//360/94;//120/32;
Arc_Offset=2.62;

Spoke_Offset=asin(Spoke_Thickness/(2*(OD-2*Shuttle_Thickness)/2));

arc=(15*Char_Theta+Char_Theta/2)-Finger_Offset;

/* [Resin Support] */
RodDiameter=1.0;
ContactDiameter=.4;
RaftThickness=2;
RaftRadius=2;
MinRodHeight=2;
CutGroove=1;
BuildplateDiameter=2;
folderdiv=12;
thetadiv=3;
ribdiv=8;
arcdiv=15;
ResSupportOffsets=[Arc_Offset,Shuttle_Width-Arc_Offset-Folder_Thickness];




//Rib Math

slopeangle=Theta+45;
yint=sin(slopeangle)*Spoke_Thickness/2;
r=sin(slopeangle)*(Folder_OD/2-yint)/(1-sin(slopeangle));
//y=
//line=slope*x;
//x^2+y^2=(r+Folder_OD/2)^2
//(x-x1)^2+(y-y1)^2=



module Cylinder(){
    translate([0, 0, -Arc_Offset])
    cylinder(h=Shuttle_Width, d=OD, $fn=cyl_fn);
}

module IsolateArcSlice(a){
    rotate([0, 0, a*(15*Char_Theta+Char_Theta/2+Finger_Offset)])
    translate([0, 0,-50])
    rotate_extrude(angle=a*(360-15*Char_Theta-Char_Theta/2+Finger_Offset), $fn=cyl_fn)
    //translate([OD/2-Shuttle_Thickness, 0])
    square([OD, 100]);
    translate([OD/2-Shuttle_Thickness-z, 0, -50])
    cube([10, Finger_Thickness/2 ,100]);
    
}

module Center(){
    cylinder(d=Folder_OD, h=Folder_Thickness, $fn=cyl_fn);
}

module Folder(){
    cylinder(d=Folder_ID, h=Folder_Thickness, $fn=cyl_fn);
}

module Rib(){
    union(){
        hull($fn=cyl_fn){
            difference(){
    //        scale([Rib_Diameter, Rib_Diameter, Rib_Thickness])
    //        sphere(d=1, $fn=cyl_fn);
            
                hull($fn=cyl_fn){
                    rotate_extrude()
                    translate([Rib_Diameter/2-.5, 0])
                    circle(r=.5, $fn=cyl_fn);
                    rotate_extrude()
                    translate([Folder_OD/2-Folder_OD/4, 0])
                    circle(r=Folder_OD/8, $fn=cyl_fn);
                }
                
            
            rotate([0, 0, Finger_Offset+Theta_Offset+45])
            rotate_extrude(angle=180, $fn=cyl_fn)
            translate([0, -10])
            square([30, 20]);
            
            }
        rotate([0, 0, Finger_Offset+Theta_Offset+Theta])
        translate([Folder_OD/2-Folder_OD/8, 0])
        sphere(r=Folder_OD/8, $fn=cyl_fn);
        }
        
        translate([0, 0, -Folder_Thickness/2])
        hull($fn=cyl_fn){
            rotate([0, 0, Theta_Offset+Finger_Offset])
            
            rotate_extrude(angle=45, $fn=cyl_fn)
            InnerSpokeChamferProfile();
            translate([0, 0, Folder_Thickness/2])
            cylinder(h=z, d=Folder_OD, $fn=cyl_fn, center=true);
        }
            
//            translate([Folder_OD/2, 0, -Folder_Thickness*FolderLocation])
//            rotate_extrude($fn=cyl_fn)
//            polygon([[0, 0], [0, Folder_Thickness], [Folder_Thickness*FolderLocation, Folder_Thickness*FolderLocation]]);
//             rotate([0, 0, Finger_Offset+Theta_Offset+Theta])
//        translate([Folder_OD/2-Folder_OD/8, 0])
//        sphere(r=Folder_OD/8, $fn=cyl_fn);
//        }
            
//        
//            rotate([0, 0, Theta_Offset+Finger_Offset+Theta])
//            translate([Folder_OD/2-Folder_Thickness*FolderLocation, 0, -Folder_Thickness*FolderLocation])
//            rotate_extrude($fn=cyl_fn)
//            polygon([[0, 0], [0, Folder_Thickness], [Folder_Thickness*FolderLocation, Folder_Thickness*FolderLocation]]);
//        }

//            rotate([0, 0, Theta_Offset+Finger_Offset+45])
//            translate([Folder_OD/2, 0, 0])
//            rotate([45, 0, -90])
//            #cube([Folder_Thickness, Folder_Thickness, Folder_Thickness], center=true);
    }
}

module IsolateCenterSlice(x){
    rotate([0, 0, Theta_Offset+Theta+Finger_Offset])
    translate([0, 0,-z-5])
    rotate_extrude(angle=360-Theta, $fn=cyl_fn)
    square([OD/2-Shuttle_Thickness/2+z+x, Shuttle_Width+2*z+10]);
}

module SpokeShape(){
    scale([Spoke_Thickness, Spoke_Height])
    circle(d=1, $fn=cyl_fn);
}

module OuterSpokeChamfer(){
    hull($fn=cyl_fn){
        translate([0, 0, OuterSpokeChamferSize])
        linear_extrude(z)
        SpokeShape();
        scale([(Spoke_Thickness+2*OuterSpokeChamferSize)/Spoke_Thickness, (Spoke_Height+2*OuterSpokeChamferSize)/Spoke_Height])
        linear_extrude(z)
        SpokeShape();
    }
}

module InnerSpokeChamferProfile(){
polygon([[Folder_OD/2, 0], [Folder_OD/2, Folder_Thickness], [Folder_OD/2+Folder_Thickness/2, Folder_Thickness/2]]);
}

module ArrangeSpokes(){
    union(){
        difference(){
            rotate([0, 0, Theta_Offset+Finger_Offset])
                union(){
                for (i=[0:1:Spoke_Count-1]){
                    translate([0, 0, Folder_Thickness/2])
                    rotate([90, 0, 90+Spoke_Spacing*i]){
                        linear_extrude(OD/2-Shuttle_Thickness)
                        SpokeShape();
                        translate([0, 0, OD/2-Shuttle_Thickness+z])
                        rotate([180, 0, 0])
                        OuterSpokeChamfer();
                    }
                }
            }
            IsolateCenterSlice(1);
        }
        
        rotate([0, 0, Theta_Offset+Finger_Offset])
        translate([OD/2-Shuttle_Thickness, 0, Folder_Thickness/2])
        rotate([0, -90, 0])
        hull($fn=cyl_fn){
            translate([Spoke_Height/2, 0])
            cylinder(r1=OuterSpokeChamferSize, r2=0, h=OuterSpokeChamferSize, $fn=cyl_fn);
            translate([-Spoke_Height/2, 0])
            cylinder(r1=OuterSpokeChamferSize, r2=0, h=OuterSpokeChamferSize, $fn=cyl_fn);
        }
    }
}

module PinHole(){
    translate([0, 0, -z])
    cylinder(h=Folder_Thickness+2*z, d=Posthole_ID+PostholeID_ResinOffset, $fn=cyl_fn);
}

module ArrangePinHole(){
    rotate([0, 0, Pin1+Finger_Offset])
    translate([Pin_Radius, 0, 0])
    PinHole();
    rotate([0, 0, Pin2+Finger_Offset])
    translate([Pin_Radius, 0, 0])
    PinHole();
}

module Arc(){
    difference(){
        Ring();
        IsolateArcSlice();
    }
}

module CenterAssembled(Tube_OD){
    union(){
        difference(){
            union(){
                Center();
                translate([0, 0, Folder_Thickness/2])
                Rib();
                ArrangeSpokes();
            }
            IsolateCenterSlice(-2*OuterSpokeChamferSize);
            ArrangePinHole();
            cylinder(h=100, d=Tube_OD, $fn=cyl_fn, center=true);
        }
        difference(){
            Folder();
            cylinder(h=100, d=Tube_OD, $fn=cyl_fn, center=true);
        }
    }       
}

module TextPlacement(theta, h){
    rotate([0, 0, theta])
    translate([OD/2-Shuttle_Thickness/2, 0, h])
    rotate([90, 0, 90])
    children();
    
}

module LetterText(char){
    mod=search(char, CharMod);
    modsize=mod==[0]?CharModSize:Typesize;
    minkowski(){
        linear_extrude(Glyph_Depth+Shuttle_Thickness/2)
        mirror([1, 0, 0])
            text(char,size=mod==[0]?CharModSize:Typesize,halign="center",valign="baseline",font=mod==[0]?CharModFont:Typeface, $fn=text_fn);
            
        if (No_Chamfer==false){
            translate([0, 0, -(Glyph_Depth+Shuttle_Thickness/2)])
            cylinder(h=Glyph_Depth+Shuttle_Thickness/2,r1=.75*(Glyph_Depth+Shuttle_Thickness/2),r2=0, $fn=mink_fn);
        }
    }
}

module TextRing(){
    difference(){
        union(){
            for (h=[0:1:2]){
                for (c=[0:1:14]){
                    TextPlacement(-Char_Theta-Char_Theta*(14-c), Baselines[h])
                    LetterText(testing?testingchar:LAYOUT[h][29-c]);
                }
            
                for (c=[0:1:14]){
                    TextPlacement(Char_Theta+Char_Theta*c, Baselines[h])
                    LetterText(testing?testingchar:LAYOUT[h][14-c]);
                }
            }
            Cylinder();
        }
        cylinder(h=100, center=true, d=OD-2*Shuttle_Thickness, $fn=cyl_fn);

        translate([0, 0, Shuttle_Width-Arc_Offset])
        cylinder(h=10, d=OD*2);
        translate([0, 0, -Arc_Offset])
        rotate([180, 0, 0])
        cylinder(h=10, d=OD*2);
    }
}

module LocateLogo(a){
    rotate([0, 0, a*(Theta_Offset+Finger_Offset)])
    translate([((OD/2-Shuttle_Thickness-OuterSpokeChamferSize)+Folder_ID/2+Folder_Clearance*2)/2, a*LogoDepth, Folder_Thickness/2])
    rotate([90, 0, a<0?180:0])
    children();
}

module LogoText(){
    linear_extrude(1)
    text(text=Line, size=LineSize, font=LineFont, halign="center", valign="center", $fn=text_fn);
}

module TubeChamfer(Tube_OD){
    translate([0, 0, -z])
    cylinder(h=Tube_ChamferSize+z, d1=Tube_OD+2*Tube_ChamferSize, d2=Tube_OD, $fn=cyl_fn);
}

module LeftShuttleAssembled(){
    union(){
        difference(){
            TextRing();
            IsolateArcSlice(1);
        }
        difference(){
            CenterAssembled(OD_OuterTube);
            translate([0, 0, Folder_Thickness*FolderLocation-Folder_SquashClearance/2-Folder_UpsideDownOffset])
            cylinder(h=10, d=Folder_ID+Folder_Clearance*2, $fn=cyl_fn);
            translate([0, 0, Folder_Thickness*FolderLocation-Folder_SquashClearance/2-Folder_UpsideDownOffset])
            rotate([180, 0, 0])
            TubeChamfer(OD_OuterTube);
            if (Logo==true){
                LocateLogo(1)
                LogoText();
            }
        }
    }
}

module RightShuttleAssembled(){
    union(){
        difference(){
            TextRing();
            IsolateArcSlice(-1);
        }
        difference(){
            mirror([0, -1, 0])
            CenterAssembled(OD_InnerTube);
            translate([0, 0, -z])
            cylinder(h=Folder_Thickness*FolderLocation+z+Folder_SquashClearance/2, d=Folder_ID+Folder_Clearance*2, $fn=cyl_fn);
            translate([0, 0, Folder_Thickness*FolderLocation+Folder_SquashClearance/2])
            TubeChamfer(OD_InnerTube);
            
            
            
            LocateLogo(-1)
            LogoText();
        }
    }
}

module ResinRod(a){
    union(){
        translate([0, 0, -MinRodHeight-RaftThickness])
        cylinder(d1=BuildplateDiameter, d2=BuildplateDiameter+RaftThickness*2, h=RaftThickness);
        
        hull(){
            translate([0, 0, -MinRodHeight-RaftThickness])
            cylinder(h=z, d=RodDiameter);
            translate([0, 0, a-2-z])
            cylinder(h=z, d=RodDiameter);
        }
        
        hull(){
            translate([0, 0, a-2])
            cylinder(h=z, d=RodDiameter);
            translate([0, 0, a])
            sphere(d=ContactDiameter);
            
        }
    }
}

module ArcSupportXSection(){
    difference(){
    polygon([[0, 0], /*[-RaftThickness, RaftThickness], [0, RaftThickness],*/ [0, RaftThickness+MinRodHeight], [Shuttle_Thickness, RaftThickness+MinRodHeight], [Shuttle_Thickness, RaftThickness], [Shuttle_Thickness+RaftThickness, RaftThickness], [Shuttle_Thickness, 0]]);
    translate([0, MinRodHeight+RaftThickness-CutGroove/2])
    circle(d=CutGroove, $fn=cyl_fn);
    translate([Shuttle_Thickness, MinRodHeight+RaftThickness-CutGroove/2])
    circle(d=CutGroove, $fn=cyl_fn);
    translate([CutGroove/2, MinRodHeight+RaftThickness-CutGroove/2])
    circle(d=CutGroove/2, $fn=cyl_fn);
    translate([Shuttle_Thickness-CutGroove/2, MinRodHeight+RaftThickness-CutGroove/2])
    circle(d=CutGroove/2, $fn=cyl_fn);
    
    }
}

module ArrangeResinRods(Tube, RodH, side){
    color("lightgreen")
    union(){
    
    //Folder Ring Supports
    
        if (side=="right"){
            for (i=[0:360/folderdiv-6:360]){
            //if (i>Theta+Finger_Offset+Theta_Offset)
            rotate([0, 0, i]){
            translate([(Tube+ContactDiameter)/2, 0, 0])
            ResinRod(RodH);
            translate([(Folder_ID-ContactDiameter)/2, 0, 0])
            ResinRod(RodH);}
            }
        }
        
        if (side=="left"){
            for (i=[140:360/folderdiv-6:360]){
            //if (i>Theta+Finger_Offset+Theta_Offset)
            rotate([0, 0, i]){
            translate([(Folder_ID-ContactDiameter)/2, 0, 0])
            ResinRod(RodH+Folder_Thickness/2+Folder_SquashClearance/2);}
            }
            for (i=[0:360/folderdiv:360]){
            //if (i>Theta+Finger_Offset+Theta_Offset)
            rotate([0, 0, i])
            translate([(Tube+ContactDiameter)/2+Tube_ChamferSize, 0, 0])
            ResinRod(RodH+Folder_Thickness/2+Folder_SquashClearance/2);
            }
        }
        
        //Pinhole Supports
        for (i=[Pin1+Finger_Offset, Pin2+Finger_Offset]){
            rotate([0, 0, i])
            translate([Pin_Radius, 0, 0])
            for (j=[0:90:360])
            rotate([0, 0, j])
            translate([(Posthole_ID+PostholeID_ResinOffset)/2+ContactDiameter/2, 0, 0])
            ResinRod(RodH);
        }

        //Folder Supports 
        rotate([0, 0, Finger_Offset+Theta_Offset]){
            for (i=[0:Theta/thetadiv:Theta]){
                for (j=[
//                (Folder_ID/2+Tube/2)/2+((Folder_OD/2)-(Folder_ID/2+Tube/2)/2)/2
//                :((Folder_OD/2)-(Folder_ID/2+Tube/2)/2)/2
//                :Folder_OD/2
                (Folder_OD+Folder_ID+Folder_Clearance*2)/4
                :(((Folder_OD-ContactDiameter)/2)-((Folder_OD+Folder_ID+Folder_Clearance*2)/4))
                :(Folder_OD-ContactDiameter)/2
                ]){
                    rotate([0, 0, i])
                    translate([j, 0, 0])
                    if (i<(Pin1-Theta_Offset)-5 || i>(Pin1-Theta_Offset)+5)
                    ResinRod(RodH);
                }
            }
            
            //Folder Supports Intermediate
            rotate([0, 0, Theta/(2*thetadiv)])
            for (i=[0:1:thetadiv-1]){
            rotate([0, 0, i*Theta/thetadiv])
                translate([Folder_OD/2, 0])
                ResinRod(RodH);
            }
            
            //Folder Supports Corners
            for (i=[0, Theta])
            rotate([0, 0, i])
            translate([Folder_ID/2+Folder_Clearance*2, 0])
            ResinRod(RodH);
        }
        
        //Rib Supports
        
        
        rotate([0, 0, Theta_Offset+Finger_Offset])
                union(){
                for (i=[0:1:Spoke_Count-1]){
                    rotate([0, 0, Spoke_Spacing*i]){
                        for (j=[Folder_OD/2+1:(OD/2-Shuttle_Thickness-OuterSpokeChamferSize-(Folder_OD/2+1))/ribdiv:OD/2-Shuttle_Thickness-OuterSpokeChamferSize]){
                            translate([j, 0, 0])
                            ResinRod(RodH+(Folder_Thickness-Spoke_Height)/2);
                        }
                    }
                }
            }
        
        //Arc Support
//        difference(){
//        rotate_extrude($fn=cyl_fn)
//        translate([OD/2-Shuttle_Thickness, -RaftThickness-MinRodHeight, 0])
//        ArcSupportXSection();
//        IsolateArcSlice(1);
//        }


rotate([0, 0, Finger_Offset])
            rotate([0, 0, Finger_Offset])
            for (i=[0:arc/arcdiv:arc]){
                for (j=[OD/2-ContactDiameter/2, OD/2-Shuttle_Thickness+ContactDiameter/2]){
                    rotate([0, 0, i])
                    translate([j, 0, 0])
                    ResinRod(0);
                }
            }

    
    }
}

module ResinLeft(){
    $fn=resin_fn;
    union(){
    color("lightblue")
        translate([0, 0, ResSupportOffsets[0]])
        LeftShuttleAssembled();
        ArrangeResinRods(OD_OuterTube, ResSupportOffsets[0], "right", $fn=resin_fn);
    }
}

module ResinLeft2(){
    union(){
        color("lightblue")
        translate([0, 0, -Arc_Offset+Shuttle_Width])
        
        rotate([180, 0, 0])
        LeftShuttleAssembled();
        mirror([0, 1, 0])
        ArrangeResinRods(OD_OuterTube, ResSupportOffsets[1], "left", $fn=resin_fn);
    }
}


module ResinRight(){
    union(){
    color("lightblue")
        translate([0, 0, Folder_Thickness+ResSupportOffsets[1]])
        rotate([180, 0, 0])
        RightShuttleAssembled();
        ArrangeResinRods(OD_InnerTube, ResSupportOffsets[1], "right", $fn=resin_fn);
    }
}



module FinalPrint(){
    translate([-10, -25])
        ResinLeft();
    translate([10, 25])
        rotate([0, 0, 180])
        ResinRight();
}

module FinalPrint2(){
    translate([0, -10])
    
        rotate([0, 0, 10])
        ResinLeft2();
    translate([0, 10])
        rotate([0, 0, -10])
        ResinRight();
}



module Assemble(){
    LeftShuttleAssembled();
    RightShuttleAssembled();
}


module ResinRod2(h){
    $fn=resin_fn;
    union(){
        cylinder(d1=BuildplateDiameter, d2=BuildplateDiameter+RaftThickness*2, h=RaftThickness);
        cylinder(d=RodDiameter, h=h-2);
        translate([0, 0, h-2])
        cylinder(d1=RodDiameter, d2=ContactDiameter, h=2);
        translate([0, 0, h])
        sphere(d=ContactDiameter);
    }
}


//VertVariables
ribspacingedge=4;
ribspacingarchalf=5;
folderspacing=5;
//folderidspacing=3;
c=OD/2-Shuttle_Thickness;
zzoffset=Folder_ID/2+RaftThickness+MinRodHeight;
rotateoffset= -(Finger_Thickness/2)/(OD/2)*(180/PI)-arc/2;

module ConRod(p1, p2){
    $fn=resin_fn;
    hull(){
    translate(p1)
    sphere(d=RodDiameter);
    translate(p2)
    sphere(d=RodDiameter);
    }
}

module VOrientL(){
translate([0, 0, zzoffset])
rotate([0, -90, 0])
rotate([0, 0, rotateoffset])
LeftShuttleAssembled();
}

module VOrientR(){
translate([0, 0, zzoffset])
rotate([0, -90, 0])
rotate([0, 0, -rotateoffset])
RightShuttleAssembled();
}

module ArrangeRods2(s){
    for (y=[-1,1]){

        //Short Shuttle Tip Edges
        for (x=[0:Shuttle_Width/(ribspacingedge-1):Shuttle_Width]){
        z=c*sin(90-arc/2)+zzoffset;
        xint=Shuttle_Width/(ribspacingedge-1);
        yy=y*c*cos(90-arc/2);
        translate([x-Shuttle_Width+Arc_Offset,yy,0])
        ResinRod2(z);
        
        if (x-Shuttle_Width+Arc_Offset+xint <= Arc_Offset)
        for (zz=[0:((z-2)/5):z-2])
        if (zz-6>RodDiameter/2)
        ConRod([x-Shuttle_Width+Arc_Offset, yy, zz],[x-Shuttle_Width+Arc_Offset+xint,yy , zz-6]);
        
        
        }
        
        //Long Shuttle Arc Edge
        for (d=[Arc_Offset, -Shuttle_Width+Arc_Offset])
            for (yy=[0:(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1):(OD/2-Shuttle_Thickness)*cos(90-arc/2)]){
            
            yyint=(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1);
            
            z=((OD/2-Shuttle_Thickness)^2-yy^2)^.5+zzoffset;
            
            
            
            translate([d, y*yy, 0])
            ResinRod2(z);
            for (zz=[0:(z-2)/5 :z-2])
            if (zz-6>RodDiameter/2)
            if (yy-yyint>=0)
            
            ConRod([d ,y*yy , zz], [d ,y*(yy-yyint) ,zz-6 ]);
            
            }
    }
    
    //Folder Inner Corner Tall
    
//    for (x=[-Folder_Thickness, -Folder_Thickness*3/4])
//    translate([
//    x, 
//    (Folder_ID/2+Folder_Clearance)*cos(90-(Theta_Offset+rotateoffset)), 
//    ])
//    ResinRod2((Folder_ID/2+Folder_Clearance)*sin(90-(Theta_Offset+rotateoffset))+zzoffset);
    
    
    //Folder Inner Corner Short
    for (x=[-Folder_Thickness, -Folder_Thickness*3/4])
    for (theta=[
    (90-(Theta_Offset+rotateoffset)):
   
   ((90-(Theta_Offset+Theta+rotateoffset))-(90-(Theta_Offset+rotateoffset)))/3
   
   
   :(90-(Theta_Offset+Theta+rotateoffset))
   ])
    translate([
    x+s, 
    (Folder_ID/2+Folder_Clearance)*cos(theta), 0
    ])
    ResinRod2((Folder_ID/2+Folder_Clearance)*sin(theta)+zzoffset);
    
    //Folder Flat
    for (x=[0:Folder_Thickness/(folderspacing-1):Folder_Thickness])
    for (y=[(Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)), (((Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)))+((Folder_ID/2+Folder_Clearance)*cos(90-(Theta_Offset+Theta+rotateoffset))))/2])
    translate([
    -x+s, 
    y , 0
    ])
    ResinRod2((Folder_OD/2)*sin(90-(Theta_Offset+Theta+rotateoffset))+zzoffset);
    
    
    for (x=[0:(Folder_Thickness/2-Folder_SquashClearance/2)/2:(Folder_Thickness/2-Folder_SquashClearance/2)])
        for (y=[-5:2.5:5]){
        z=Folder_ID/2-((Folder_ID/2)^2-y^2)^.5;
            translate([-x+s, y, 0])
            #ResinRod2(zzoffset-Folder_ID/2+z);}
    
}

module VPrintL(){
    VOrientL();
    ArrangeRods2(0);
}

module VPrintR(){
    VOrientR();
    //translate([-Arc_Offset+Shuttle_Width/2, 0, 0])
    
    mirror([0, 1, 0])
    translate([-Shuttle_Width+2*Arc_Offset, 0, 0])
    mirror([1, 0, 0])
    ArrangeRods2(Folder_Thickness+Arc_Offset-Shuttle_Width+Arc_Offset);
}

module VResPrint(){
//translate([0, 21, 0])
    VPrintL();
    //translate([0, -21, 0])
    translate([-20, 0, 0])
    VPrintR();
}

VResPrint();




//LeftShuttleAssembled();


//Assemble();
//Assemble2();
//FinalPrint2();
//ResinLeft3();
//ResinRight3();
//FinalPrint2();
//FinalPrint();
//LeftShuttleAssembled();
//ResinRight();
//ResinLeft();
//if(Generate_Right_Shuttle==true)
//RightShuttleAssembled();
//if(Generate_Left_Shuttle==true)
//LeftShuttleAssembled(); 