//Bennett Type Element
//September 14, 2023
//Leonard Chau

//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
testing_baseline=false;
testing_cutout=false;
testing_layout=false;
testing_console=false;
z=.001;
cyl_fn = 360;
resin_fn=20;
mink_fn=10;
text_fn=44;
/* [Character Details] */
CharLegend=[12,22,3,11,21,2,10,20,1,9,19,0,8,18,27,17,7,26,16,6,25,15,5,24,14,4,23,13];

//Custom Layout As Seen on Keyboard. Left to Right, Top to Bottom
Lowercase="qweruiopasdftyjkl,zxcvghbnm.";
Uppercase="QWERUIOPASDFTYJKL,ZXCVGHBNM.";
Figs="12347890\"#$%56;?:,£@_(&-)/'.";
CUSTOMLAYOUT=[Lowercase,Uppercase,Figs];
include <BennettLayouts.scad>


//Layout Selection
Layout_Selection=0; //[0:English, 1:British, 2:Custom]
Layout=LAYOUTS[Layout_Selection];
//Typeface
Typeface_="Compagnon Light";
Type_Size=3.05;//[1:.05:10]
//Speedy Preview and Render with No Minkowski
Debug_No_Minkowski=true;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=32.9;
//Platen Diameter
Platen_Diameter=30;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]

/* [Element Details] */
//Element Diameter
Element_Diameter=31.9;
//Element Height
Element_Height=18.65;
//Shaft Diameter
Shaft_Diameter=3.483;
//Element Positioner Pin Diameter
Element_Positioner_Pin_Diameter=2.6;
//Element Positioner Pin - Radial Position
Element_Positioner_Pin_Radius=4.813;
//Indicator Hole Diameter
Indicator_Diameter=2.2;
//Alignment Pin Hole Diameter
Alignment_Hole_Diameter=2;//1.94 a kiss too tight, bumping to 2.0
//Alignment Hole Depth
Alignment_Hole_Depth=2.4;
//Alignment Hole Chamfer Size
Alignment_Hole_Chamfer=.3;//.01
//Speed Hole Diameter
Speed_Hole_Diameter=6.1;
//Speed Hole - Radial Position
Speed_Hole_Radius=10.801;
//Number of Speed Holes
Speed_Hole_Quantity=8;
//Countersink Diameter
Countersink_Diameter=23.4;
//Top Countersink Depth
Top_Countersink_Depth=1.85;
//Bottom Countersink Depth
Bottom_Countersink_Depth=0.9;//.01
//Minimum Cylinder Thickness
Shell_Size=1;
//Radius of Inside Corners
Inside_Radius=.5;

/* [Character Placement Details (Bottom Countersink Depth as Reference)] */
//[Lowercase, Uppercase, Figures] Row Height
Baseline=[14.95,8.8,2.35];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Platen Cutout Height
Cutout=[16.35,10.65,4.5];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Alignment Hole Height
Alignment_Hole=[13.29,7.24,1.19];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Alignment Hole Height Offset
Testing_Offsets=[-.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7];

/* [Shuttle Label] */
//Shuttle Label 1
Shuttle_Label1="Leonard Chau";
//Shuttle Label 2
Shuttle_Label2="2023";
//Shuttle Label Size
Shuttle_Label_Size=1.2;
//Shuttle Label Font
Shuttle_Label_Font="Libertinus Mono";
//Shuttle Label Extrusion Deptth
Shuttle_Label_Depth=.2;

/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.2;
//Resin Support Height
Resin_Support_Height=6;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;//.001
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=1.2;
Resin_Support_Contact_Point_Diameter=.3;
Resin_Support_Buildplate_Diameter=1.2;

pyramidzoffset=1/cos(atan(2/Countersink_Diameter));

CharProtrusion=(Min_Final_Character_Diameter-Element_Diameter)/2;


module ResinRod (h,  dr, dc, t,db){
cylinder(h=h-1,d=dr);
translate([0,0,h-1])
cylinder(h=1, d2=dc, d1=dr);
cylinder(h=t,d2=2.4*.5+2*t,d1=2.4);
translate([0, 0, h])
sphere(d=dc);
}

module LetterPlacement(row, column, Theta){
    rotate ([0, 0, Theta])
    translate([Element_Diameter/2, 0, Baseline[row]])
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
module 2DText(Char, column){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, (y==[]?0:Character_Modifieds_Offset) + (testing_baseline==true?Testing_Offsets[column]:0), 0])
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
module LetterText(Char, row, column){
    minkowski(){
        difference(){
            translate([0, 0, -.5])
            linear_extrude(2)
            2DText(Char, column);
            translate([0, Cutout[row]-Baseline[row]+(testing_cutout==true?Testing_Offsets[column]:0), Platen_Diameter/2+CharProtrusion])
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
            Theta=-(360/(len(Layout[0]))*column+360/(2*28));
            PickedChar=CharLegend[column];
            Char=testing_layout==false?Layout[row][PickedChar]:"H";
            LetterPlacement(row, column, Theta)
            LetterText(Char, row, column);
            echo(char=Layout[row][PickedChar], baseline=Baseline[row]+ (testing_baseline==true?Testing_Offsets[column]:0), cutout=Cutout[row]+ (testing_cutout==true?Testing_Offsets[column]:0));
        }
    }
}

module Cylinder(){
    cylinder(h=Element_Height,d=Element_Diameter, $fn=cyl_fn);
}

module PositionerPins(){
    for (n=[0:1:1]){
        theta=180*n+90;
        translate([Element_Positioner_Pin_Radius*cos(theta),Element_Positioner_Pin_Radius*sin(theta),-z])
        cylinder(h=Element_Height+2*z,d=Element_Positioner_Pin_Diameter, $fn=cyl_fn);
    }
}

module HollowBody(){
    rotate_extrude($fn=cyl_fn){
        hull(){
            dx=(Element_Diameter/2-Shell_Size-Inside_Radius)-(Shaft_Diameter/2+Shell_Size+Inside_Radius);
            //Top Right
            translate([Element_Diameter/2-Shell_Size-Inside_Radius, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth])
            circle(r=Inside_Radius);
            //Top Left
            translate([Element_Diameter/2-Shell_Size-Inside_Radius-dx, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth-dx*(2/Countersink_Diameter)])
            circle(r=Inside_Radius);
            //Bottom Left
            translate([Shaft_Diameter/2+Shell_Size+Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
            circle(r=Inside_Radius);
            //Bottom Right
            translate([Element_Diameter/2-Shell_Size-Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
            circle(r=Inside_Radius);
            //Bottom
            translate([(Element_Diameter/2-Shell_Size+Shaft_Diameter/2+Shell_Size)/2, Shell_Size+Inside_Radius+Bottom_Countersink_Depth])
            circle(r=Inside_Radius);
        }
    }
}

module AlignmentHoles(){
    for (row=[0:1:len(Layout)-1]){
        for (n=[0:1:len(Layout[0])-1]){
            theta=-(360/(len(Layout[0]))*n+360/(2*28));
            translate([(Element_Diameter)/2*cos(theta),(Element_Diameter)/2*sin(theta),Alignment_Hole[row]])
            rotate([0,-90,theta]){
                cylinder(h=Alignment_Hole_Depth-Alignment_Hole_Diameter/2,d=Alignment_Hole_Diameter, $fn=cyl_fn);
//                    translate([0,0,-1])
//                    cylinder(h=1,d=Alignment_Hole_Diameter/*+2*Alignment_Hole_Chamfer*/, $fn=cyl_fn);
                hull(){
                    translate([0, 0, Alignment_Hole_Chamfer])
                    cylinder(h=z, d=Alignment_Hole_Diameter, $fn=cyl_fn);
                    translate([0, 0, -1])
                    scale([1, (Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer)/Alignment_Hole_Diameter, 1])
                    cylinder(h=1, d=Alignment_Hole_Diameter, $fn=cyl_fn);
                }
//                    %cylinder(h=Alignment_Hole_Chamfer,d1=Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer,d2=Alignment_Hole_Diameter, $fn=cyl_fn);
            }
            translate([((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*cos(theta),((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*sin(theta),Alignment_Hole[row]])
            sphere(d=Alignment_Hole_Diameter, $fn=cyl_fn);
        }
    }
}

module LabelText(){
    translate([Shaft_Diameter/2+1.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, 90])
    linear_extrude(2)
    text(text=Shuttle_Label1, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
    translate([-Shaft_Diameter/2-1.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, -90])
    linear_extrude(2)
    text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
    
}

module SpeedHoles(){
    translate([0, 0, -z])
    for (n=[0:1:7]){
        theta=360/Speed_Hole_Quantity*n+360/(Speed_Hole_Quantity*2);
        translate([Speed_Hole_Radius*cos(theta),Speed_Hole_Radius*sin(theta),0])
        cylinder(h=Element_Height+2*z,d=Speed_Hole_Diameter, $fn=cyl_fn);
    }
}

module MinkCleanup(){
    translate([0,0,Element_Height])
    cylinder(h=5,d=Element_Diameter);
    rotate([180, 0, 0])
    cylinder(h=5,d=Element_Diameter);
}

module CenterShaft(){
    translate([0, 0, -z])
    cylinder(h=Element_Height+2*z,d=Shaft_Diameter, $fn=cyl_fn);
}

module TopCountersink(){
    translate([0,0,Element_Height-Top_Countersink_Depth])
    cylinder(h=Top_Countersink_Depth+z,d=Countersink_Diameter, $fn=cyl_fn);
}

module BottomCountersink(){
    translate([0, 0, -z])
    cylinder(h=Bottom_Countersink_Depth+z,d=Countersink_Diameter, $fn=cyl_fn);
}

module RoofTaper(){
    if (Generate_Support==true)
    translate([0, 0, Element_Height-Top_Countersink_Depth-1])
    cylinder(h=1+z, d2=Countersink_Diameter, d1=0, $fn=cyl_fn);
}


module IndicatorHole(){
    translate([Element_Diameter/2-Shell_Size-Indicator_Diameter/2,0,Element_Height-Top_Countersink_Depth-Shell_Size-z])
    cylinder(h=5,d=Indicator_Diameter, $fn=cyl_fn);
}

module ResinSupport(){
$fn=resin_fn;
    translate([0,0,-Resin_Support_Height+z]){
        difference(){
            //Create Ring
            translate([0, 0, .5])
            cylinder(d=Element_Diameter, h=Resin_Support_Height-.5, $fn=cyl_fn);
            translate([0,0,-z])
            cylinder(h=Resin_Support_Height+2*z, r=Element_Diameter/2-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=cyl_fn);
            //Cut Groove
            rotate_extrude($fn=cyl_fn){
                translate([Element_Diameter/2,Resin_Support_Height-Resin_Support_Cut_Groove_Diameter/2])
                circle(r=Resin_Support_Cut_Groove_Diameter/2);
            }
        }
        //Create Raft
        rotate_extrude($fn=2*resin_fn){
            polygon([[Element_Diameter/2,0], [Element_Diameter/2-Resin_Support_Thickness,0], [Element_Diameter/2-Resin_Support_Thickness,Resin_Support_Thickness], [Element_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
        }
        //Create Outer 2 Rings of 8 Supports
        for (n=[0:1:7]){
            theta=360/8*n;
            translate([(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*cos(theta),(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*sin(theta),0]){
            ResinRod (Resin_Support_Height, Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
            }
            translate([Countersink_Diameter*cos(theta)/3,Countersink_Diameter*sin(theta)/3,0]){
            ResinRod (Resin_Support_Height+pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Countersink_Diameter/3), Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
            }
        }
        //Create Inner Ring of 4 Supports
        for (n=[0:1:3]){
            theta=90*n;
            translate([(Shaft_Diameter/2+1)*cos(theta),(Shaft_Diameter/2+1)*sin(theta),0]){
                ResinRod (Resin_Support_Height+pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Shaft_Diameter/2+1), Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
            }
        }
    }
}

module Assemble(){
    difference(){
        union(){
            Cylinder();
            TextRing();
        }
        PositionerPins();
        HollowBody();
        AlignmentHoles();
        LabelText();
        SpeedHoles();
        MinkCleanup();
        CenterShaft();
        TopCountersink();
        BottomCountersink();
        RoofTaper();
        IndicatorHole();
    }
}

module ResinPrint(){
    union(){
        translate([0, 0, Element_Height])
        rotate([0, 180, 0])
        Assemble();
        ResinSupport();
    }
}
if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
ResinPrint();