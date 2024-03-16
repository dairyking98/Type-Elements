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
LAYOUT=["?zxqkjgdmpcfld,.taherisounwyv:",
        "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3⅌4$56“7”8’9[0]¼*⅓†⅔"];

Typeface="Iosevka Etoile";
Typesize=2.5;
Baseline_Gaps=[9.45, 4.725, 0];
Baseline_Offset=-1.9;
Baselines=Baseline_Gaps+[Baseline_Offset, Baseline_Offset, Baseline_Offset];
//Baselines=[9.52+Baseline_Offset, 4.74+Baseline_Offset, -.04+Baseline_Offset];//.02=

CharMod="⅌";
CharModFont="Noto Sans Mono";
CharModSize=2.5;




/* [Dimensions] */
Posthole_ID=1.984375;// 5/64 wire rod
OD_InnerTube=6.000;// 5mm ID x 6mm OD tube
OD_OuterTube=7.000;// 6mm ID x 7mm OD tube

Tube_Clearance=.05;

OD=75;
Shuttle_Thickness=1.6;
Shuttle_Width=13.26;
Folder_Thickness=9.525;// 3/8 thick
Folder_ID=9.6;
Folder_OD=18.762;
Folder_Clearance=.5;
Folder_SquashClearance=0;

Glyph_Depth=.8;
Finger_Thickness=1.8;// 

Spoke_Thickness=2.2;
Spoke_Height=8.3;
Spoke_Count=5;
Spoke_Spacing=45/4;
OuterSpokeChamferSize=1.5;

Rib_Diameter=46.8;
Rib_Thickness=2.6;


/* [Logo] */
Logo=true;
Line="Leonard Chau 2024";
Line2="2024";
LineFont="Average Mono";
LineSize=2;
LogoDepth=.1;



/* [Constants] */
Theta_Offset=8.3;
Theta=115.8;
Pin1=72.3;
Pin2=112.0;
Pin_Radius=7.6895;

Finger_Offset=asin((Finger_Thickness/2)/((OD-2*Shuttle_Thickness)/2))/2;//why /2????
//asin(Finger_Thickness/(2*(OD-2*Shuttle_Thickness)/2));
Char_Theta=360/94;//120/32;
Arc_Offset=2.62;

Spoke_Offset=asin(Spoke_Thickness/(2*(OD-2*Shuttle_Thickness)/2));

arc=(15*Char_Theta+Char_Theta/2)-Finger_Offset;

/* [Resin Support] */
RodDiameter=1.0;
ContactDiameter=.6;
RaftThickness=2;
RaftRadius=2;
MinRodHeight=2;
CutGroove=1;
BuildplateDiameter=2;
folderdiv=10;
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
            
//            translate([Folder_OD/2, 0, -Folder_Thickness/2])
//            rotate_extrude($fn=cyl_fn)
//            polygon([[0, 0], [0, Folder_Thickness], [Folder_Thickness/2, Folder_Thickness/2]]);
//             rotate([0, 0, Finger_Offset+Theta_Offset+Theta])
//        translate([Folder_OD/2-Folder_OD/8, 0])
//        sphere(r=Folder_OD/8, $fn=cyl_fn);
//        }
            
//        
//            rotate([0, 0, Theta_Offset+Finger_Offset+Theta])
//            translate([Folder_OD/2-Folder_Thickness/2, 0, -Folder_Thickness/2])
//            rotate_extrude($fn=cyl_fn)
//            polygon([[0, 0], [0, Folder_Thickness], [Folder_Thickness/2, Folder_Thickness/2]]);
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
    cylinder(h=Folder_Thickness+2*z, d=Posthole_ID, $fn=cyl_fn);
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
    translate([((OD/2-Shuttle_Thickness-OuterSpokeChamferSize)+Folder_ID/2+Folder_Clearance)/2, a*LogoDepth, Folder_Thickness/2])
    rotate([90, 0, a<0?180:0])
    children();
}

module LogoText(){
    linear_extrude(1)
    text(text=Line, size=LineSize, font=LineFont, halign="center", valign="center", $fn=text_fn);
}

module LeftShuttleAssembled(){
    union(){
        difference(){
            TextRing();
            IsolateArcSlice(1);
        }
        difference(){
            CenterAssembled(OD_OuterTube);
            translate([0, 0, Folder_Thickness/2-Folder_SquashClearance/2])
            cylinder(h=10, d=Folder_ID+Folder_Clearance, $fn=cyl_fn);
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
            cylinder(h=Folder_Thickness/2+z+Folder_SquashClearance/2, d=Folder_ID+Folder_Clearance, $fn=cyl_fn);
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

module ArrangeResinRods(Tube, RodH){
    color("lightgreen")
    union(){
    
    //Folder Ring Supports
    
        for (i=[0:360/folderdiv:360]){
        //if (i>Theta+Finger_Offset+Theta_Offset)
        rotate([0, 0, i])
        translate([(Folder_ID/2+Tube/2)/2, 0, 0])
        ResinRod(RodH);
        }
        
        //Pinhole Supports
        for (i=[Pin1+Finger_Offset, Pin2+Finger_Offset]){
            rotate([0, 0, i])
            translate([Pin_Radius, 0, 0])
            for (j=[0:90:360])
            rotate([0, 0, j])
            translate([Posthole_ID/2+ContactDiameter/2, 0, 0])
            ResinRod(RodH);
        }

        //Folder Supports 
        rotate([0, 0, Finger_Offset+Theta_Offset]){
            for (i=[0:Theta/thetadiv:Theta]){
                for (j=[(Folder_ID/2+Tube/2)/2+((Folder_OD/2)-(Folder_ID/2+Tube/2)/2)/2:((Folder_OD/2)-(Folder_ID/2+Tube/2)/2)/2:Folder_OD/2]){
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
            translate([Folder_ID/2, 0])
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
    union(){
    color("lightblue")
        translate([0, 0, ResSupportOffsets[0]])
        LeftShuttleAssembled();
        ArrangeResinRods(OD_OuterTube, ResSupportOffsets[0], $fn=resin_fn);
    }
}

module ResinRight(){
    union(){
    color("lightblue")
        translate([0, 0, Folder_Thickness+ResSupportOffsets[1]])
        rotate([180, 0, 0])
        RightShuttleAssembled();
        ArrangeResinRods(OD_InnerTube, ResSupportOffsets[1], $fn=resin_fn);
    }
}

module FinalPrint(){
    translate([-10, -25])
        ResinLeft();
    translate([10, 25])
        rotate([0, 0, 180])
        ResinRight();
}
//FinalPrint();
//LeftShuttleAssembled();
//ResinRight();
ResinLeft();
//if(Generate_Right_Shuttle==true)
//RightShuttleAssembled();
//if(Generate_Left_Shuttle==true)
//LeftShuttleAssembled(); 