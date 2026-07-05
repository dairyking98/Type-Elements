//Bennett Type Element
//September 14, 2023
//Leonard Chau

//render something?
Render=false;
XSection=false;
XSectionTheta=180;
testing_baseline=false;
testing_cutout=false;
testing_layout=false;
testing_console=false;
z=.001;
surface_fn=120;
alignmenthole_fn=40;
criticalcyl_fn=360;
resin_fn=20;
mink_fn=10;
text_fn=10;
/* [Character Details] */
CharLegend=[12,22,3,11,21,2,10,20,1,9,19,0,8,18,27,17,7,26,16,6,25,15,5,24,14,4,23,13];

//Custom Layout As Seen on Keyboard. Left to Right, Top to Bottom
Lowercase="qweruiopasdftyjkl,zxcvghbnm.";
Uppercase="QWERUIOPASDFTYJKL,ZXCVGHBNM.";
Figs="12347890\"#$%56;?:,£@_(&-)/'.";
CUSTOMLAYOUT=[Lowercase,Uppercase,Figs];
include <BennettLayouts.scad>


//Layout Selection
Layout_Selection=0; //[0:English, 1:British, 2:Custom, 3:International]
Layout=LAYOUTS[Layout_Selection];
//Typeface
Typeface_="FreeMono";
Type_Size=3.00;//[1:.05:10]
//Speedy Preview and Render with No Minkowski
Debug_No_Minkowski=true;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=32.9;
//Platen Diameter
Platen_Diameter=30;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=.1;//[-1.5:.05:1.5]
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
Alignment_Hole_Diameter=2;//.1
//1.94 a kiss too tight, bumping to 2.0
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
coreWebLength=6;
//secondary core with larger diameter to focus friction at ends of shaft hole along core contact lengths
coreSecondaryIDOffset=coreGrooveD/2+z;
grooveFn=40;
/* [Character Placement Details (Bottom Countersink Depth as Reference)] */
//[Lowercase, Uppercase, Figures] Row Height
Baseline=[15.35,9.2,2.75];//[-1:.05:1][14.95,8.8,2.35]


///baseline defaults before: [15.25,9.1,2.65]


//[Lowercase, Uppercase, Figures] Platen Cutout Height
Cutout=[16.35,10.65,4.50];//[-1:.05:1][16.35,10.65,4.5]
//[Lowercase, Uppercase, Figures] Alignment Hole Height
Alignment_Hole=[13.29,7.24,1.19];//.01;
//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Alignment Hole Height Offset
Testing_Offsets=[-.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7];

/* [Shuttle Label] */
//Shuttle Label 1
Shuttle_Label1a="Leonard";
Shuttle_Label1b="Chau";
//Shuttle Label 2
Shuttle_Label2="2025";
//Shuttle Label Size
Shuttle_Label_Size=1.7;
//Shuttle Label Font
Shuttle_Label_Font="OCR\\-A II";
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
Resin_Support_Contact_Point_Diameter=.8;
Resin_Support_Buildplate_Diameter=1.0;

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
            cylinder(h=5,d=Platen_Diameter,center=true,$fn=criticalcyl_fn);
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
            echo(char=LAYOUTS[1][row][PickedChar], baseline=Baseline[row]+ (testing_baseline==true?Testing_Offsets[column]:0), cutout=Cutout[row]+ (testing_cutout==true?Testing_Offsets[column]:0));
        }
    }
}

module Cylinder(){
    cylinder(h=Element_Height,d=Element_Diameter, $fn=surface_fn);
}

module PositionerPins(){
    for (n=[0:1:1]){
        theta=180*n+90;
        translate([Element_Positioner_Pin_Radius*cos(theta),Element_Positioner_Pin_Radius*sin(theta),-z]){
        cylinder(h=Element_Height+2*z,d=Element_Positioner_Pin_Diameter, $fn=criticalcyl_fn);
        
        //lil chamfer to clean up post print booger that drags on alignment pins
        translate([0, 0, Bottom_Countersink_Depth+Shell_Size])
        cylinder(h=2,d1=Element_Positioner_Pin_Diameter, d2=Element_Positioner_Pin_Diameter+1, $fn=criticalcyl_fn);
        }
    }
}
asd=1;
drop=.5;
module HollowBody(){
    RoofSlope=1/(Countersink_Diameter/2);
    XArray=[Shaft_Diameter/2+Shell_Size+coreSecondaryIDOffset, Shaft_Diameter/2+Shell_Size+coreSecondaryIDOffset+asd, ((Element_Diameter/2-Shell_Size)+(Shaft_Diameter/2+Shell_Size+coreSecondaryIDOffset))/2, Element_Diameter/2-Shell_Size-asd, Element_Diameter/2-Shell_Size];
    YArray=[Bottom_Countersink_Depth+Shell_Size, Bottom_Countersink_Depth+Shell_Size+drop, Bottom_Countersink_Depth+Shell_Size+drop+asd, Element_Height-Top_Countersink_Depth-Shell_Size-asd, Element_Height-Top_Countersink_Depth-Shell_Size, Element_Height-Top_Countersink_Depth-Shell_Size-asd-RoofSlope*(Countersink_Diameter/2-XArray[0]), Element_Height-Top_Countersink_Depth-Shell_Size-RoofSlope*(Countersink_Diameter/2-XArray[0])]; 
    XYPattern=[[0, 2], [0, 5], [1, 6], [3, 4], [4, 3], [4, 2], [3, 1], [2, 0], [1, 1]];
    polygonpath=[for (n=[0:len(XYPattern)-1]) [XArray[XYPattern[n][0]], YArray[XYPattern[n][1]]]];
    rotate_extrude($fn=surface_fn){
        polygon(polygonpath);
//        hull(){
//            dx=(Element_Diameter/2-Shell_Size-Inside_Radius)-(Shaft_Diameter/2+Shell_Size+Inside_Radius);
//            //Top Right
//            translate([Element_Diameter/2-Shell_Size-Inside_Radius, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth])
//            circle(r=Inside_Radius);
//            //Top Left
//            translate([Element_Diameter/2-Shell_Size-Inside_Radius-dx, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth-dx*(2/Countersink_Diameter)])
//            circle(r=Inside_Radius);
//            //Bottom Left
//            translate([Shaft_Diameter/2+Shell_Size+Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
//            circle(r=Inside_Radius);
//            //Bottom Right
//            translate([Element_Diameter/2-Shell_Size-Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
//            circle(r=Inside_Radius);
//            //Bottom
//            translate([(Element_Diameter/2-Shell_Size+Shaft_Diameter/2+Shell_Size)/2, Shell_Size+Inside_Radius+Bottom_Countersink_Depth])
//            circle(r=Inside_Radius);
//        }
        
    }
}

module AlignmentHoles(){
    for (row=[0:1:len(Layout)-1]){
        for (n=[0:1:len(Layout[0])-1]){
            theta=-(360/(len(Layout[0]))*n+360/(2*28));
            translate([(Element_Diameter)/2*cos(theta),(Element_Diameter)/2*sin(theta),Alignment_Hole[row]])
            rotate([0,-90,theta]){
                cylinder(h=Alignment_Hole_Depth-Alignment_Hole_Diameter/2,d=Alignment_Hole_Diameter, $fn=alignmenthole_fn);
//                    translate([0,0,-1])
//                    cylinder(h=1,d=Alignment_Hole_Diameter/*+2*Alignment_Hole_Chamfer*/, $fn=surface_fn);
                hull(){
                    translate([0, 0, Alignment_Hole_Chamfer])
                    cylinder(h=z, d=Alignment_Hole_Diameter, $fn=alignmenthole_fn);
                    translate([0, 0, -1])
                    scale([1, (Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer)/Alignment_Hole_Diameter, 1])
                    cylinder(h=1, d=Alignment_Hole_Diameter, $fn=alignmenthole_fn);
                }
//                    %cylinder(h=Alignment_Hole_Chamfer,d1=Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer,d2=Alignment_Hole_Diameter, $fn=surface_fn);
            }
            translate([((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*cos(theta),((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*sin(theta),Alignment_Hole[row]])
            sphere(d=Alignment_Hole_Diameter, $fn=alignmenthole_fn);
        }
    }
}

module LabelText(){
    translate([Shaft_Diameter/2+1.5+.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, 90])
    linear_extrude(2){
    text(text=Shuttle_Label1b, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");
    translate([0, 2.25, 0])
    text(text=Shuttle_Label1a, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");
    
    }
    translate([-Shaft_Diameter/2-1.75-.5, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
    rotate([180, 0, 90])
    linear_extrude(2)
    text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="center");
    
}

module SpeedHoles(){
    translate([0, 0, -z])
    for (n=[0:1:7]){
        theta=360/Speed_Hole_Quantity*n+360/(Speed_Hole_Quantity*2);
        translate([Speed_Hole_Radius*cos(theta),Speed_Hole_Radius*sin(theta),0])
        cylinder(h=Element_Height+2*z,d=Speed_Hole_Diameter, $fn=surface_fn);
    }
}

module MinkCleanup(){
    translate([0,0,Element_Height])
    cylinder(h=5,d=Element_Diameter+5, $fn=20);
    rotate([180, 0, 0])
    cylinder(h=5,d=Element_Diameter+5, $fn=20);
}

module CenterShaft(){
    translate([0, 0, -z])
    cylinder(h=Element_Height+2*z,d=Shaft_Diameter, $fn=criticalcyl_fn);
}

module TopCountersink(){
    translate([0,0,Element_Height-Top_Countersink_Depth])
    cylinder(h=Top_Countersink_Depth+z,d=Countersink_Diameter, $fn=surface_fn);
}

module BottomCountersink(){
    translate([0, 0, -z])
    cylinder(h=Bottom_Countersink_Depth+z,d=Countersink_Diameter, $fn=surface_fn);
}

module RoofTaper(){
    if (Generate_Support==true)
    translate([0, 0, Element_Height-Top_Countersink_Depth-1])
    cylinder(h=1+z, d2=Countersink_Diameter, d1=0, $fn=surface_fn);
}


module IndicatorHole(){
    translate([Element_Diameter/2-Shell_Size-Indicator_Diameter/2,0,Element_Height-Top_Countersink_Depth-Shell_Size-z-1])
    cylinder(h=5,d=Indicator_Diameter, $fn=surface_fn);
}

module ResinSupport(){
$fn=resin_fn;
    translate([0,0,-Resin_Support_Height+z]){
        difference(){
            //Create Ring
            translate([0, 0, .5])
            cylinder(d=Element_Diameter, h=Resin_Support_Height-.5, $fn=surface_fn);
            translate([0,0,-z])
            cylinder(h=Resin_Support_Height+2*z, r=Element_Diameter/2-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=surface_fn);
            //Cut Groove
            rotate_extrude($fn=surface_fn){
                translate([Element_Diameter/2,Resin_Support_Height-Resin_Support_Cut_Groove_Diameter/2])
                circle(r=Resin_Support_Cut_Groove_Diameter/2);
            }
        }
        //Create Raft
        rotate_extrude($fn=resin_fn){
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

s=.2;
module SecondaryCore(Offset){
    $fn=surface_fn;
    rotate_extrude(){
        polygon([[0, Bottom_Countersink_Depth+coreContactLength], [0, Element_Height-Top_Countersink_Depth-1+s], [Shaft_Diameter /2+Offset/2+coreSecondaryIDOffset, Element_Height-Top_Countersink_Depth-1+s], [Shaft_Diameter /2+Offset/2+coreSecondaryIDOffset, Element_Height-Top_Countersink_Depth-1+s], [Shaft_Diameter /2+Offset/2, Element_Height-Top_Countersink_Depth-1-coreSecondaryIDOffset+s], [Shaft_Diameter /2+Offset/2, Element_Height-Top_Countersink_Depth-1-coreContactLength+s], [Shaft_Diameter /2+Offset/2+coreSecondaryIDOffset, Element_Height-Top_Countersink_Depth-1-coreContactLength-coreSecondaryIDOffset+s], [Shaft_Diameter /2+Offset/2+coreSecondaryIDOffset, Bottom_Countersink_Depth+coreContactLength+coreSecondaryIDOffset], [Shaft_Diameter /2+Offset/2, Bottom_Countersink_Depth+coreContactLength]]);
    }
}

module CoreGrooves(Offset){
    for (n=[0:coreGrooveQty-1]){
        rotate([0, 0, 360/coreGrooveQty*n])
        linear_extrude(Element_Height-Top_Countersink_Depth-1+s+2*z, twist=360*(Element_Height-Top_Countersink_Depth-1+s+2*z)/(PI*(Shaft_Diameter +Offset))*(n%2==0?1:-1), $fn=surface_fn)
        translate([Shaft_Diameter /2+Offset/2, 0, -z])
        translate([0, 0, -z])
        circle(d=coreGrooveD, $fn=grooveFn);
    }
}

module CoreChamferShape(Offset){
    cylinder(d1=Shaft_Diameter +Offset+2*coreChamfer, d2=Shaft_Diameter +Offset, h=coreChamfer+z, $fn=surface_fn);
}

module CoreChamfer(Offset){
    translate([0, 0, Bottom_Countersink_Depth-z])
    CoreChamferShape(Offset);
//    translate([0, 0, Element_Height+z])
//    rotate([180, 0, 0])
//    CoreChamferShape(Offset+coreSecondaryIDOffset/2);
}

//module CoreEllipses(){
//    $fn=surface_fn;
//    for (n=[0:coreWebQty-1])
//    rotate([0, 0, n*360/coreWebQty])
//    translate([0, 0, Bottom_Countersink_Depth+(Element_Height  -Bottom_Countersink_Depth+  0  )/2-coreWebLength/2])
//    rotate([90, 0, 90])
//    hull(){
//        translate([0, coreWebWidth/2, 0])
//        cylinder(d=coreWebWidth, h=5);
//        translate([0, coreWebLength-coreWebWidth/2, 0])
//        cylinder(d=coreWebWidth, h=5);
//    }
//}


module CoreEllipses(){
    $fn=surface_fn;
    for (n=[0:coreWebQty-1])
    rotate([0, 0, n*360/coreWebQty])
    translate([0, 0, (Bottom_Countersink_Depth+coreContactLength+Element_Height-Top_Countersink_Depth-1-coreContactLength+s)/2-coreWebLength/2])
    rotate([90, 0, 90])
//    #sphere(r=1);
    hull(){
        translate([0, coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
        translate([0, coreWebLength-coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
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
        SecondaryCore(0);
        CoreGrooves(0);
        CoreChamfer(0);
        CoreEllipses();
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

if (Render==true){

difference(){
    ResinPrint();
    if (XSection==true)
    rotate([0, 0, XSectionTheta])
    translate([-50, 0, -50])
    cube(100);
}


}