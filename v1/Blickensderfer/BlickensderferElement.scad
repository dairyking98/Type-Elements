//Blickensderfer Type Elements, V2 (Improved Code)
//26 March, 2024
//Leonard Chau
//leonard.chau@yahoo.com
//+1 510 461 4851
//leonardchau.com



/*
       DHIATENSOR DETAILS
         Z X K G | B V Q J    
       . P W F U | L C M Y ,  
       D H I A T | E N S O R  
   zxkg.pwfudhiatensorlcmy,bvqj
   ZXKG.PWFUDHIATENSORLCMY&BVQJ
   -^_(./'"!1234567890;?%¢$)@#:
   
       QWERTY DETAILS
       Q W E R T | Y U I O P  
       A S D F G | H J K L .  
         Z X C V | B N M ,    
   qwertasdfgzxcvbnm,hjkl.yuiop
   QWERTASDFGZXCVBNM?HJKL.YUIOP
   "#$%_/-¢@;23456789:!^1.&'(0)
*/

//Assert error message to stop OpenSCAD from freezing upon startup. Uncheck Automatic Preview, then uncheck Assert in customizer window
Assert=true;
//Excludes draft angles for speedy preview. Uncheck for final render.
Debug_No_Minkowski=true;
/* [Global Variables] */
//Universal Offset for "z fighting" - DO NOT CHANGE
e=.001;
//Cylinder Facet Number
cyl_fn = 360;
//Resin Support Facet Number
resin_fn=20;
//Minkowski Facet Number (Draft Angles)
mink_fn=10;
//Text Facet Number 
text_fn=44;

/* [Character Details] */
DHIATENSOR=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-^_(./'\"!1234567890;?%¢$)@#:"];
QWERTY=["qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
       "\"#$%_/-¢@;23456789:!^1.&'(0)"];
SCANDI=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:"];

//Custom Lowercase Row
Custom_Lowercase="zxkg.pwfudhiatensorlcmy,bvqj";
//Custom Uppercase Row
Custom_Uppercase="ZXKG.PWFUDHIATENSORLCMY&BVQJ";
//Custom Figures Row
Custom_Figures="-^_(./'\"!1234567890;?%¢$)@#:";
CUSTOM=[Custom_Lowercase,Custom_Uppercase,Custom_Figures];
SELECTIONS=[DHIATENSOR,QWERTY,SCANDI,CUSTOM];
CharLegend=[14,15,16,17,18,19,20,21,22,23,24,25,26,27,0,1,2,3,4,5,6,7,8,9,10,11,12,13];
//Layout of Element
Layout_Selection=0;//[0:DHIATENSOR,1:QWERTY,2:SCANDI,3:Custom] 
//Type Size
Type_Size=3.55;//[1:.05:5]
//Typeface (Font Name)
Typeface_="Courier New";
Layout=SELECTIONS[Layout_Selection];
//Offset the heights of these characters
Character_Modifieds="_";
//Height offset for the above characters (+ up / - down)
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
//Scale increase for these characters
Scale_Multiplier_Text=".";
//Scale factor value for the above characters
Scale_Multiplier=1.0;
//Horizontal Weight Adjustment
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
//Vertical Weight Adjustment
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//Weight Adjustment Type
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Weight Adjustment Shape
Weight_Adj_Shape=0;//[0:Square, 1:Circle]

/* [Series Number] */
//Element Series Number
Series_Number="";
//Element Series Number Font Size
Series_Size=1.25;
//Element Series Number Font
Series_Font="Century Schoolbook Monospace";
//Baseline Offset of Series Text from Between Two Baselines
Series_OffsetFromHalfline=-.5;
//Lowercase Character to Place Series Text Below
Series_CharacterPosition=".";
//Degres Between Series Numbers
Series_AngleSpacing=4;
//Series Text Depth
Series_Depth=.2;
//Series Number Placement
Series_Row=0;//[0:Between Lowercase and Uppercase, 1:Between Uppercase and Figures]

/* [Label] */
//Label Font Override
Cylinder_Label_Font_Override="";
//Label Text Override
Cylinder_Label_Override="";
//Label Size
Cylinder_Label_Size=.67*Type_Size;//[1:.05:3]
//Label Font
Cylinder_Label_Font= Cylinder_Label_Font_Override== "" ?  Typeface_ : Cylinder_Label_Font_Override;//"Courier New:style=bold";
Cylinder_Label= Cylinder_Label_Override== "" ? Typeface_ : Cylinder_Label_Override;
//Spacing Between Characters (Degrees)
Cylinder_Label_Spacing=8;
//Label Offset From Pin (Degrees)
Cylinder_Label_Offset=0;

/* [Logo] */
//Logo Offset From Pin (Degrees)
Cylinder_Logo_Offset=180;
//Logo Text Orientation
Cylinder_Logo_TextOrientation=180;
//Logo Text
Cylinder_Logo="Leonard Chau 2024";
//Logo Size
Cylinder_Logo_Size=Cylinder_Label_Size;
//Logo Font
Cylinder_Logo_Font=Cylinder_Label_Font;

/* [Character Positioning] */
//Distance From Top Plane to Baseline
Baselines=[4, 10.3, 16.1];
//Baseline Offsets
Baseline_Offset=[0, 0, 0];//[-1:.05:1]
//Distance from Top Plane to Cutout
Cutouts=[2.6, 8.86, 14.6];
//Cutout Offsets
Cutout_Offset=[0, 0, 0];//[-1:.05:1]
Baseline=Baselines-Baseline_Offset;
Cutout=Cutouts-Cutout_Offset;
//Platen Diameter
Platen_Diameter = 32.258;
//Final Minimum Character Height Radius
Final_Min_Character_Height_Radius = 17.49;



/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.3;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Raft Thickness
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;




/* [Main Element Details] */
//Faceted Cylinder Multiplier
Element_Facet_Multiplier=10;//[1:1:10]
//Element Radius
Element_Radius = 17;
//Element Height
Element_Height = 16.75;
//Center Shaft Diameter (Undersized for ream/drill)
Shaft_Diameter = 3.277; //3.297 for no drill out
//Radial Position for "Speed Holes"
Cutout_Position_Radius = 11.251;
//"Speed Hole Diameter"
Cutout_Hole_Diameter_Top = 5.568;
Cutout_Hole_Diameter_Bottom=7.3;
//Top Clip Diameter
Clip_Diameter = 7;
//Top Clip Height
Clip_Height = 3;
//Element Shell Thickness
Shell_Thickness = 1.5;
//Wire Clip Diameter
Wire_Diameter = .554;
//Amount of Wire Biting into Shaft
Wire_Clip_Shaft_Bite = .7;
CharacterRadius=Element_Radius-.5;
Inside_Radius=1;


Cylinder_Label_Radius=Element_Radius-2.3;

/* [Square Positioner Details] */
//Countersink Depth
Positioner_Depth = 2;
//Countersink Radius
Positioner_Support_Radius = 2.784;
//Square Slot Width
Square_Slot_Width = 3.937;
//Inside Support Radius
Square_Slot_Support_Radius = 3.65;
//Inside Support Height
Square_Slot_Support_Height = 3;


CharProtrusion=Final_Min_Character_Height_Radius-Element_Radius;

//Places Characters in Correct Spots
module LetterPlacement(row, column, Theta){
    rotate ([0, 0, Theta])
    translate([Element_Radius, 0, Element_Height-Baseline[row]])
    rotate([90, 0, 90])
    children();
}

//2D Text Weight Adjuster Profile/Shape
module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=mink_fn);
}

//Creates 2D Text
module 2DText(Char){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, y==[]?0:Character_Modifieds_Offset, 0])
    mirror([1, 0, 0]){
        if (Weight_Adj_Mode==2)//Additive
            minkowski(){
                text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                WeightAdjShape();
            }
        if (Weight_Adj_Mode==1)//Subtractive
            difference(){
                text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                    }
                    WeightAdjShape();
                }
            }
        if (Weight_Adj_Mode==0)//No Weight Adjustment
            text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
    }
}

//Creates Drafted Angle Text
module LetterText(Char, row){
    minkowski(){
        difference(){
            linear_extrude(2)
            2DText(Char);
            translate([0, Baseline[row]-Cutout[row], Platen_Diameter/2+CharProtrusion])
            rotate([0,90,0])
            cylinder(h=5,d=Platen_Diameter,center=true,$fn=cyl_fn);
        }
        if (Debug_No_Minkowski != true)
            translate([0, 0, -1])
            cylinder(h=1,r2=0,r1=.75, $fn=mink_fn);
    }
    
}

//Assembles All Text Together
module TextRing(){
    for (row=[0:1:len(Layout)-1]){
        for (column=[0:1:len(Layout[0])-1]){
            Theta=-(360/len(Layout[0]))*column-360/(len(Layout[0])*2);
            PickedChar=CharLegend[column];
            Char=Layout[row][PickedChar];
            LetterPlacement(row, column, Theta)
            LetterText(Char, row);
        }
    }
}

module Cylinder(){
    translate([0, 0, -e])
    cylinder(r=Element_Radius, h=Element_Height+Clip_Height+e, $fn=cyl_fn);
}

module FaceCleanup(){
    translate([0, 0, Element_Height]){
        difference(){
            cylinder(r=Element_Radius+5, h=5, $fn=cyl_fn);
            translate([0, 0, -e])
            cylinder(r=Clip_Diameter/2,h=5+2*e, $fn=cyl_fn);
        }
    }
    rotate([0,180,0])
    cylinder(r=Element_Radius+5, h=5);
}

module Shaft(){
    translate([0,0,-e])
    cylinder(r=Shaft_Diameter/2, h=Element_Height+Clip_Height+2*e, $fn=cyl_fn); 
}

module TopHoles(){
    for (n = [0:1:7]){
        rotate([0, 0, 45*n])
        translate([Cutout_Position_Radius,0,Element_Height/2])
        cylinder(h=Element_Height/2+e, r=Cutout_Hole_Diameter_Top/2, $fn=cyl_fn);
    }
}

module BottomHoles(){
    for (n = [1:1:5]){
        rotate([0, 0, 60*n])
        translate([Cutout_Position_Radius, 0, -e])
        cylinder(h=Element_Height/2, r=Cutout_Hole_Diameter_Bottom/2, $fn=cyl_fn);
    }
}

module HollowBody(){
    rotate_extrude($fn=cyl_fn){
        difference(){
            hull(){
                translate([(Element_Radius-Shell_Thickness+Shaft_Diameter/2+Shell_Thickness)/2, Element_Height-Shell_Thickness-Inside_Radius])
                circle(r=Inside_Radius);//1
                translate([Shaft_Diameter/2+Shell_Thickness+Inside_Radius, Element_Height-Shell_Thickness-Inside_Radius-.5])
                circle(r=Inside_Radius);//2
                translate([Element_Radius-Shell_Thickness-Inside_Radius, Element_Height-Shell_Thickness-Inside_Radius-.5])
                circle(r=Inside_Radius);//3
                translate([Element_Radius-Shell_Thickness-Inside_Radius, Shell_Thickness+Inside_Radius])
                circle(r=Inside_Radius);//4
                translate([(Element_Radius-Shell_Thickness+Shaft_Diameter/2+Shell_Thickness)/2, Shell_Thickness+Inside_Radius])
                circle(r=Inside_Radius);//5
                translate([Shaft_Diameter/2+Shell_Thickness+1, Shell_Thickness+1])
                circle(r=1);//6
            }
        translate([0, -25.45+2.5])
        circle(r=25.45+Shell_Thickness, $fn=cyl_fn);
        }
    }
}

module WireClip(){
    translate([0,-(Shaft_Diameter/2+Wire_Diameter/2-Wire_Clip_Shaft_Bite),Element_Height+Wire_Diameter/2])
    hull(){
        rotate([0,-90,0])
        cylinder(r=Wire_Diameter/2,h=8,center=true, $fn=cyl_fn);
        translate([0,-5,.5])
        rotate([0,-90,0])
        cylinder(r=Wire_Diameter/2+.5,h=8,center=true, $fn=cyl_fn);
    }
}

module LabelText(){
    for (n=[0:len(Cylinder_Label)-1]){
            rotate([0,0,180+90-Cylinder_Label_Spacing*n+Cylinder_Label_Offset+(len(Cylinder_Label)-1)*Cylinder_Label_Spacing/2])
            translate([0, Cylinder_Label_Radius, Element_Height-.3])
            linear_extrude(.4)
            text(text=Cylinder_Label[n], size=Cylinder_Label_Size, font=Cylinder_Label_Font, valign="baseline", halign="center");
    }
}

module LogoText(){
    for (n=[0:len(Cylinder_Logo)-1]){
            rotate([0,0,180-90+Cylinder_Label_Spacing*n-(len(Cylinder_Logo)-1)*Cylinder_Label_Spacing/2])
            
            translate([0, Cylinder_Label_Radius+1.5, Element_Height-.3])
            linear_extrude(.4)
            rotate([0, 0, 180])
            text(text=Cylinder_Logo[n], size=Cylinder_Logo_Size, font=Cylinder_Logo_Font, valign="baseline", halign="center", $fn=text_fn);
    }
}

module SeriesNoText(){
    for (n=[0:1:len(Series_Number)-1]){
        x=search(Series_CharacterPosition, Layout[1]);
        theta=-(360/len(Layout[0]))*x[0]-360/(len(Layout[0])*2);
        rotate([0, 0, theta-Series_AngleSpacing*(len(Series_Number)-1)/2 + Series_AngleSpacing*n])
        translate([-Element_Radius+Series_Depth, 0, Element_Height-(Baselines[Series_Row]+Baselines[Series_Row+1])/2+Series_OffsetFromHalfline])
        rotate([90, 0, -90])
        linear_extrude(2*Series_Depth)
        text(text=Series_Number[n], size=Series_Size, font=Series_Font, valign="baseline", halign="center", $fn=text_fn);
    }
}

module PositionerSupport(){
    translate([Cutout_Position_Radius,0,Shell_Thickness-e])
    cylinder(h=2*e+Square_Slot_Support_Height,r=Square_Slot_Support_Radius, $fn=cyl_fn);
}

module PositionerHole(){
    translate([Cutout_Position_Radius,0,-e]){
        cylinder(h=Positioner_Depth,r=Positioner_Support_Radius, $fn=cyl_fn);
        cube([Square_Slot_Width, Square_Slot_Width, 10], center=true);
    }
}

module SphereClearance(){
    translate([0,0,-25.45+2.5])
    sphere(r=25.45, $fn=cyl_fn);
}

module ResinPrintSupportShape(){
    $fn=resin_fn;
    rotate([180,0,0]){
        difference(){
            union(){
                difference(){
                    cylinder(h=Resin_Support_Height-.5,r=Element_Radius, $fn=360);
                    translate([0,0,-e])
                    cylinder(h=Resin_Support_Height+2*e-.5,r=Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=360);
                    rotate_extrude($fn=360){
                        translate([Element_Radius,Resin_Support_Cut_Groove_Diameter/2])
                        circle(r=Resin_Support_Cut_Groove_Diameter/2);
                    }
                }
                //Buildplate Raft
                rotate_extrude($fn=resin_fn*2){
                    polygon([[Element_Radius,Resin_Support_Height],[Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness,Resin_Support_Height],[Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness,Resin_Support_Height-Resin_Support_Thickness],[Element_Radius+Resin_Support_Thickness,Resin_Support_Height-Resin_Support_Thickness]]);
                }
                //Outer Support Rods
                for (n=[0:1:5]){
                    translate([Cutout_Position_Radius*cos(60*n-30),Cutout_Position_Radius*sin(60*n-30),0]){
                    sphere(r=.3);
                    cylinder(h=1, r1=.3, r2=.6);
                    translate([0,0,1-e])
                    cylinder(h=Resin_Support_Height-1,r=.6);
                    translate([0,0,Resin_Support_Height-Resin_Support_Thickness])
                    cylinder(h=Resin_Support_Thickness,r1=Resin_Support_Thickness+.6,r2=1.2);
                    }
                    //Inner Support Rods
                    for (m=[1:1:2]){
                        z=sqrt(25.45^2-(Cutout_Position_Radius*m/3*cos(60*n-30))^2-(Cutout_Position_Radius*m/3*sin(60*n-30))^2)-25.45+2.5;
                        translate([Cutout_Position_Radius*m/3*cos(60*n-30),Cutout_Position_Radius*m/3*sin(60*n-30),-z]){
                        sphere(r=.3);
                        cylinder(h=1, r1=.3, r2=.6);
                        translate([0,0,1-e])
                        cylinder(h=Resin_Support_Height-1,r=.6);
                        translate([0,0,Resin_Support_Height-Resin_Support_Thickness+z])
                        cylinder(h=Resin_Support_Thickness,r1=Resin_Support_Thickness+.6,r2=1.2);
                        }
                    }
                }
            }
            //Resin Drainage Holes
            for (n=[0:1:3]){
                theta=90*n;
                radius=(Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness-.5);
                translate([radius*cos(theta),radius*sin(theta),Resin_Support_Height])
                rotate([0,90,90*n])
                cylinder(h=5,r=1.5);
            }
        }
    }
}

//ResinPrintSupportShape();

if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
//if (Series_Number=="")
//assert(false,"Enter Serial Number");
else
Assemble();


module Assemble(){
    union(){
        difference(){
            union(){
                difference(){
                    union(){
                        TextRing();
                        Cylinder();
                    }
                    FaceCleanup();
                    Shaft();
                    TopHoles();
                    BottomHoles();
                    HollowBody();
                    WireClip();
                    LabelText();
                    LogoText();
                    SeriesNoText();
                }
                PositionerSupport();
            }
            PositionerHole();
            SphereClearance();
        }
        if (Generate_Support==true)
        translate([0,0,e])
        ResinPrintSupportShape();
    }
}


