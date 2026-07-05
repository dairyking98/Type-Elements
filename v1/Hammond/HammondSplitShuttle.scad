//Split Hammond 1 Shuttle
//Leonard Chau
//February 17, 2024
        
/* [Checks] */
Render=false;
No_Chamfer=true;
cyl_fn=360;
text_fn=30;
mink_fn=20;
z=.01;
resin_fn=20;
testing=false;
testingchar=".";

GenStyle = 1; //[0:Normal, 1:ResinPrint, 2:ResinPrintL, 3:ResinPrintR, 4:NormalL, 5:NormalR]

/* [Character Details] */
//Layout as "stamped"
//LAYOUT=["?zxqkjgdmpcfld,.taherisounwyv:",
//        "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
//        "¾%⅞⅝½⅜1⅛2¢3⅌4$56“7”8’9[0]¼*⅓†⅔"];

IDEAL=["?zxqkjgdmpcfld,.taherisounwyv:",
       "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
       "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔"];
        
QWERTY = ["qazwsxedcrfvtgbyhnujmik,ol.p;-",
          "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
          "1\"@2#⅌3$+4%£5_¢6&*7'§8(°9).0=/"];
          
LAYOUTS = [[0, IDEAL],
            [1, QWERTY]];
layoutselection = 0; //[0:Ideal, 1:Qwerty]
LAYOUT=LAYOUTS[layoutselection][1];

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
//resin offset fot pin holes
Posthole_IDChamfer=.25;
PostholeID_ResinOffset=.25;
OD_InnerTube_=5.842;//measurement + clearance
OD_OuterTube_=6.6548;//measurement + clearance


OD=75.0;
Shuttle_Thickness=1.6;
Shuttle_Width=13.26;
Folder_ID=12;//.1 
//9.6 is og folder id
Folder_OD=18.762;
Folder_Clearance=0.4;
Folder_SquashClearance=.3683;//.2794;//.0001 //.5 for Full 3D
FolderLocation=.5;//.2 for Full 3D, .5 for metal tube
Tube_ChamferSize=.5;
Folder_Thickness_=9.525;// 3/8 thick

Folder_Thickness_Offset=.05;
Folder_Thickness=Folder_Thickness_+Folder_Clearance+Folder_Thickness_Offset-Folder_Thickness_Offset;

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
//embiggen tube hole diameter by this much
Tube_IDResinOffset=.17;
Tube_OD=6.6;

OD_InnerTube=OD_InnerTube_+Tube_IDResinOffset;
OD_OuterTube=OD_OuterTube_+Tube_IDResinOffset;



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
Pin1=68.55;//.01
Pin2=108.25;//.01
Pin_Radius=7.95;

Finger_Offset=asin((Finger_Thickness/2)/((OD-2*Shuttle_Thickness)/2))/2;//why /2????
//asin(Finger_Thickness/(2*(OD-2*Shuttle_Thickness)/2));
Char_Theta=360/96;//360/94;//120/32;
Arc_Offset=2.62;

Spoke_Offset=asin(Spoke_Thickness/(2*(OD-2*Shuttle_Thickness)/2));

arc=(15*Char_Theta+Char_Theta/2)-Finger_Offset;

/* [Resin Support] */
RodDiameter=1.0;//.1
ContactDiameter=.4;//.1
RodRaftChamfer=.5;
RaftThickness=2;//.1
RaftRadius=2;//.1
MinRodHeight=2;//.1
BuildplateDiameter=2;//.1
TipLength=1.8;//.1
TipInterference=1.2;//.1
folderdiv=12;
thetadiv=3;
ribdiv=8;
arcdiv=15;
ResSupportOffsets=[Arc_Offset,Shuttle_Width-Arc_Offset-Folder_Thickness];




//Rib Math

slopeangle=Theta+45;
yint=sin(slopeangle)*Spoke_Thickness/2;
r=sin(slopeangle)*(Folder_OD/2-yint)/(1-sin(slopeangle));



module Cylinder(){
    translate([0, 0, -Arc_Offset])
    cylinder(h=Shuttle_Width, d=OD, $fn=cyl_fn);
}

module IsolateArcSlice(a){
    rotate([0, 0, a*(15*Char_Theta+Char_Theta/2+Finger_Offset)])
    translate([0, 0,-50])
    rotate_extrude(angle=a*(360-15*Char_Theta-Char_Theta/2+Finger_Offset), $fn=cyl_fn)
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
    translate([0, 0, -z]){
        cylinder(h=Folder_Thickness+2*z, d=Posthole_ID+PostholeID_ResinOffset, $fn=cyl_fn);
        cylinder(h=Posthole_IDChamfer, d1=Posthole_ID+PostholeID_ResinOffset+2*Posthole_IDChamfer, d2=Posthole_ID+PostholeID_ResinOffset, $fn=cyl_fn);
    }
    translate([0, 0, Folder_Thickness+z-Posthole_IDChamfer])
    cylinder(h=Posthole_IDChamfer, d2=Posthole_ID+PostholeID_ResinOffset+2*Posthole_IDChamfer, d1=Posthole_ID+PostholeID_ResinOffset, $fn=cyl_fn);
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
            translate([0, 0, Folder_Thickness*FolderLocation-Folder_SquashClearance/2])
            cylinder(h=10, d=Folder_ID+Folder_Clearance*2, $fn=cyl_fn);
            translate([0, 0, Folder_Thickness*FolderLocation-Folder_SquashClearance/2])
            rotate([180, 0, 0])
            TubeChamfer(OD_OuterTube);
            translate([0, 0, -z])
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
            translate([0, 0, Folder_Thickness+z])
            rotate([0, 180, 0])
            TubeChamfer(OD_InnerTube);
            
            
            
            LocateLogo(-1)
            LogoText();
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

module Assemble(){
    LeftShuttleAssembled();
    RightShuttleAssembled();
}

//module ResinRod(h){
//    $fn=resin_fn;
//    union(){
//        cylinder(d1=BuildplateDiameter, d2=BuildplateDiameter+RaftThickness*2, h=RaftThickness);
//        cylinder(d=RodDiameter, h=h-TipLength-ContactDiameter/2+TipInterference);
//        translate([0, 0, h-TipLength-ContactDiameter/2+TipInterference])
//        cylinder(d1=RodDiameter, d2=ContactDiameter, h=TipLength);
//        translate([0, 0, h-ContactDiameter/2+TipInterference])
//        sphere(d=ContactDiameter);
//    }
//}
//ResinRod2(h=0, theta=45, tipd=.8, tiph=5, inset=.4, rodd=1.2, raftd=4, raftt=2, minh=8, fn=20);

module ResinRod2(h, theta, tipd, tiph, inset, rodd, raftd, raftt, minh, fn){
    $fn=fn;
    xoffset=sin(theta)*tiph;
    zoffset=cos(theta)*tiph;
    //tip
    translate([0, xoffset, -zoffset+h])
    rotate([theta, 0, 0])
    hull(){
        translate([0, 0, tiph-tipd/2+inset])
        sphere(d=tipd);
        sphere(d=rodd);
    }
    hull(){
        translate([0, xoffset, -zoffset+h])
        sphere(d=rodd);
        translate([0, xoffset, rodd/2])
        sphere(d=rodd);
    }
    translate([0, xoffset, 0]){
        cylinder(d1=raftd, d2=raftd+2*raftt, h=raftt);
        translate([0, 0, raftt-z])
        cylinder(d1=rodd+RodRaftChamfer*2, d2=rodd, h=RodRaftChamfer);
    }
    
}

//ArrangeRods2(0);
module ArrangeRods2(s){
    for (y=[-1,1]){

        //Short Shuttle Tip Edges
        for (x=[0:Shuttle_Width/(ribspacingedge-1):Shuttle_Width]){
        z=c*sin(90-arc/2)+zzoffset;
        xint=Shuttle_Width/(ribspacingedge-1);
        yy=y*c*cos(90-arc/2);
        translate([x-Shuttle_Width+Arc_Offset,yy,0])
        //ResinRod(z);
        ResinRod2(h=z, theta=-30*y, tipd=ContactDiameter, tiph=TipLength, inset=TipInterference, rodd=RodDiameter, raftd=BuildplateDiameter, raftt=RaftThickness, minh=MinRodHeight, fn=resin_fn);
        if (x-Shuttle_Width+Arc_Offset+xint <= Arc_Offset)
        for (zz=[0:((z-2)/5):z-2])
        if (zz-6>RodDiameter/2)
        ConRod([x-Shuttle_Width+Arc_Offset, yy+y*sin(-30)*TipLength, zz],[x-Shuttle_Width+Arc_Offset+xint,yy+y*sin(-30)*TipLength , zz-6]);
        
        
        }
        
        //Long Shuttle Arc Edge
        for (d=[Arc_Offset, -Shuttle_Width+Arc_Offset])
            for (yy=[0:(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1):(OD/2-Shuttle_Thickness)*cos(90-arc/2)]){
            
            yyint=(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1);
            theta=asin(yy/(OD/2-Shuttle_Thickness));
            
            z=((OD/2-Shuttle_Thickness)^2-yy^2)^.5+zzoffset;
            
            
            
            if (abs(theta)<25)
            translate([d, y*yy, 0])
            //#ResinRod(z);
            ResinRod2(h=z, theta=-theta*y, tipd=ContactDiameter, tiph=TipLength, inset=TipInterference, rodd=RodDiameter, raftd=BuildplateDiameter, raftt=RaftThickness, minh=MinRodHeight, fn=resin_fn);
            for (zz=[0:(z-2)/5 :z-2])
            if (zz-6>RodDiameter/2)
            if (yy-yyint>=0)
            
            ConRod([d ,y*yy-TipLength*sin(theta)*y , zz], [d ,y*(yy-yyint)-TipLength*sin(asin((yy-yyint)/(OD/2-Shuttle_Thickness)))*y ,zz-6 ]);
            
            }
    }
    

    
    
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
    ]){
    ResinRod2(h=(Folder_ID/2+Folder_Clearance)*sin(theta)+zzoffset, theta=theta<0?(-90+30):(-90+theta), tipd=ContactDiameter, tiph=TipLength, inset=TipInterference, rodd=RodDiameter, raftd=BuildplateDiameter, raftt=RaftThickness, minh=MinRodHeight, fn=resin_fn);}
    
    //Folder Flat
    for (x=[0:Folder_Thickness/(folderspacing-1):Folder_Thickness])
    for (y=[(Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)), (((Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)))+((Folder_ID/2+Folder_Clearance)*cos(90-(Theta_Offset+Theta+rotateoffset))))/2])
    translate([
    -x+s, 
    y , 0
    ])
    ResinRod2(h=(Folder_OD/2)*sin(90-(Theta_Offset+Theta+rotateoffset))+zzoffset, theta=(90-(Theta_Offset+Theta+rotateoffset)), tipd=ContactDiameter, tiph=TipLength, inset=TipInterference, rodd=RodDiameter, raftd=BuildplateDiameter, raftt=RaftThickness, minh=MinRodHeight, fn=resin_fn);
    
    
    for (x=[0:(Folder_Thickness/2-Folder_SquashClearance/2)/2:(Folder_Thickness/2-Folder_SquashClearance/2)])
        for (y=[-5:2.5:5]){
        theta=asin(y*2/Folder_ID);
        z=Folder_ID/2-((Folder_ID/2)^2-y^2)^.5;
            translate([-x+s, y, 0])
            ResinRod2(h=(zzoffset-Folder_ID/2+z), theta=theta, tipd=ContactDiameter, tiph=TipLength, inset=TipInterference, rodd=RodDiameter, raftd=BuildplateDiameter, raftt=RaftThickness, minh=MinRodHeight, fn=resin_fn);
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

//module ArrangeRods(s){
//    for (y=[-1,1]){
//
//        //Short Shuttle Tip Edges
//        for (x=[0:Shuttle_Width/(ribspacingedge-1):Shuttle_Width]){
//        z=c*sin(90-arc/2)+zzoffset;
//        xint=Shuttle_Width/(ribspacingedge-1);
//        yy=y*c*cos(90-arc/2);
//        translate([x-Shuttle_Width+Arc_Offset,yy,0])
//        ResinRod(z);
//        
//        if (x-Shuttle_Width+Arc_Offset+xint <= Arc_Offset)
//        for (zz=[0:((z-2)/5):z-2])
//        if (zz-6>RodDiameter/2)
//        ConRod([x-Shuttle_Width+Arc_Offset, yy, zz],[x-Shuttle_Width+Arc_Offset+xint,yy , zz-6]);
//        
//        
//        }
//        
//        //Long Shuttle Arc Edge
//        for (d=[Arc_Offset, -Shuttle_Width+Arc_Offset])
//            for (yy=[0:(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1):(OD/2-Shuttle_Thickness)*cos(90-arc/2)]){
//            
//            yyint=(OD/2-Shuttle_Thickness)*cos(90-arc/2)/(ribspacingarchalf-1);
//            
//            z=((OD/2-Shuttle_Thickness)^2-yy^2)^.5+zzoffset;
//            
//            
//            
//            translate([d, y*yy, 0])
//            ResinRod(z);
//            for (zz=[0:(z-2)/5 :z-2])
//            if (zz-6>RodDiameter/2)
//            if (yy-yyint>=0)
//            
//            ConRod([d ,y*yy , zz], [d ,y*(yy-yyint) ,zz-6 ]);
//            
//            }
//    }
//    
//
//    
//    
//    //Folder Inner Corner Short
//    for (x=[-Folder_Thickness, -Folder_Thickness*3/4])
//    for (theta=[
//    (90-(Theta_Offset+rotateoffset)):
//   
//   ((90-(Theta_Offset+Theta+rotateoffset))-(90-(Theta_Offset+rotateoffset)))/3
//   
//   
//   :(90-(Theta_Offset+Theta+rotateoffset))
//   ])
//    translate([
//    x+s, 
//    (Folder_ID/2+Folder_Clearance)*cos(theta), 0
//    ])
//    ResinRod((Folder_ID/2+Folder_Clearance)*sin(theta)+zzoffset);
//    
//    //Folder Flat
//    for (x=[0:Folder_Thickness/(folderspacing-1):Folder_Thickness])
//    for (y=[(Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)), (((Folder_OD/2)*cos(90-(Theta_Offset+Theta+rotateoffset)))+((Folder_ID/2+Folder_Clearance)*cos(90-(Theta_Offset+Theta+rotateoffset))))/2])
//    translate([
//    -x+s, 
//    y , 0
//    ])
//    ResinRod((Folder_OD/2)*sin(90-(Theta_Offset+Theta+rotateoffset))+zzoffset);
//    
//    
//    for (x=[0:(Folder_Thickness/2-Folder_SquashClearance/2)/2:(Folder_Thickness/2-Folder_SquashClearance/2)])
//        for (y=[-5:2.5:5]){
//        z=Folder_ID/2-((Folder_ID/2)^2-y^2)^.5;
//            translate([-x+s, y, 0])
//            ResinRod(zzoffset-Folder_ID/2+z);}
//    
//}

module VPrintL(){
    VOrientL();
    ArrangeRods2(0);
}

module VPrintR(){
    VOrientR();
    mirror([0, 1, 0])
    translate([-Shuttle_Width+2*Arc_Offset, 0, 0])
    mirror([1, 0, 0])
    ArrangeRods2(Folder_Thickness+Arc_Offset-Shuttle_Width+Arc_Offset);
}

module VResPrint(){
    VPrintL();
    translate([0, 41, 0])
    VPrintR();
}

module VResPrint(){
    VPrintL();
    translate([0, 41, 0])
    VPrintR();
}

if (Render == true){

if (GenStyle==1)
VResPrint();

if (GenStyle==0)
Assemble();

if (GenStyle==2)
VPrintL();

if (GenStyle==3)
VPrintR();

if (GenStyle==4)
LeftShuttleAssembled();

if (GenStyle==5)
RightShuttleAssembled();
}
