//Mignon 2, 3, 4 Type Cylinder
//September 13, 2023
//Leonard Chau


//ADD RESIN SUPPORT
/* [Character Details] */
//As Seen on Legend
/*LAYOUT=["'\"%&(£$);:,.",
          "?PFUGQpfugq¼",
        "!VINABvinab½",
        "_LDETMldetm¾",
        "JKOSRZkosrzj",
        "/YCHWXychwx@",
        "#1234567890-"];
LAYOUT=["&():\"!?'äöü_",
        "§PFUGQpfugq;",
        "JVINABvinabj",
        "/LDETMldetm,",
        "%KOSRZkosrz=",
        "¾YCHWXychwx+",
        "½¼23456789.-"];
*/
TESTING=["HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH"];

Assert=true;
testing_layout=false;
testing_baseline=false;
testing_cutout=false;
cyl_fn = 360;
resin_fn=20;
mink_fn=10;
text_fn=44;
z=.001;
//Custom Layout
1st_Row="";
2nd_Row="";
3rd_Row="";
4th_Row="";
5th_Row="";
6th_Row="";
7th_Row="";
CUSTOMLAYOUT=[1st_Row,2nd_Row,3rd_Row,4th_Row,5th_Row,6th_Row,7th_Row];
include <MignonIndexLayouts.scad>
CharLegend=[7,8,9,10,11,0,1,2,3,4,5,6];
Layout_Selection=5; //[0:Custom Layout,1:English 2,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]

Layout=Layouts[Layout_Selection];
Tallen=false;
//Element Height Increase
Height_Increase=3;


Typeface_="Iosevka Etoile";//As Installed on PC
Type_Size=2.45;//[1:.05:6]
Debug_No_Minkowski=true;//Speedy Preview and Render with No Minkowski
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]

//Label Text
Cylinder_Label="Label";
//Label Size
Cylinder_Label_Size=0.51*Type_Size;
//Label Font
Cylinder_Label_Font=Typeface_;
//Label Height Offset From Chamfer Base
Cylinder_Label_Height_Offset=.5;
//Spacing Between Characters (Degrees)
Cylinder_Label_Spacing=15;
//Label Offset From Pin (Degrees)
Cylinder_Label_Offset=0;

/* [Cylinder Details] */
Cylinder_Shape=0;//[0:Polygonal, 1:Cylindrical]
//Total Cylinder Height
Cylinder_Height_=40.5;
Cylinder_Height= Tallen==true ? Cylinder_Height_+Height_Increase : Cylinder_Height_;
//Main Cylinder Diameter
Cylinder_Diameter=18.64;
//Height Drop From Top
Cylinder_Top_Height_Offset=3;
//Height Drop Chamfer Radius
//Cylinder_Top_Radius=2;
//Height Drop Chamfer Size
Cylinder_Top_Chamfer=2;
//Height Drop Diameter
Cylinder_Top_Diameter=10.5;
//Inner Shaft Diameter
Cylinder_Top_Shaft_Diameter=7.3;
//Inner Mounting Diameter
Cylinder_Bottom_Shaft_Diameter=14.6;
//Max Pin Height
Pin_Height=1.8;
//Max Pin Width
Pin_Width=1.7;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=19.4;
//Platen Diameter
Platen_Diameter=26.5;

/* [Character Placement Details] */
//[1st, 2nd, 3rd, 4th, 5th, 6th, 7th] Baseline Height
Baseline=[2.25, 7.55, 12.75, 17.8, 22.8, 28, 32.8];
Cutout=[3.3, 8.55, 13.7, 18.7, 23.7, 28.7, 33.4];
Testing_Offsets=[-.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, .6];


/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.1;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=1.0;
//Resin Support Contact Point Diameter
Resin_Support_Contact_Point=.6;


CharProtrusion=(Min_Final_Character_Diameter-Cylinder_Diameter)/2;


module LetterPlacement(row, column, Theta){
    rotate ([0, 0, Theta])
    translate([Cylinder_Diameter/2, 0, Baseline[row]])
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
            translate([0, 0, -1])
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
            Theta=-(360/(len(Layout[0]))*column);
            PickedChar=CharLegend[column];
            Char=testing_layout==false?Layout[row][PickedChar]:"H";
            LetterPlacement(row, column, Theta)
            LetterText(Char, row, column);
            echo(char=Layout[row][PickedChar], baseline=Baseline[row]+ (testing_baseline==true?Testing_Offsets[column]:0), cutout=Cutout[row]+ (testing_cutout==true?Testing_Offsets[column]:0));
        }
    }
}

 module regular_polygon(order,SomeCylinder_Diameter){
     angles=[ for (i = [0:order-1]) i*(360/order) ];
     coords=[ for (th=angles) [SomeCylinder_Diameter/2*cos(th), SomeCylinder_Diameter/2*sin(th)] ];
     polygon(coords);
 }


//Polygonal Shape
module PolygonCylinder(){
    linear_extrude(Cylinder_Height-Cylinder_Top_Height_Offset)
    rotate([0,0,360/24])
    regular_polygon(12,Cylinder_Diameter);
}

module ElementChamfer(){
    translate([0,0,Cylinder_Height-Cylinder_Top_Height_Offset-z]){
        /*hull(){//Element Top
            rotate_extrude($fn=cyl_fn){
                translate([Cylinder_Top_Diameter/2-Cylinder_Top_Radius,0,0])
                union(){
                    intersection(){
                        circle(r=Cylinder_Top_Radius);
                        translate([0,-Cylinder_Top_Radius])
                        square([Cylinder_Top_Radius,Cylinder_Top_Radius*2]);
                    }
                    translate([0,-Cylinder_Top_Radius*2])
                    square([Cylinder_Top_Radius,Cylinder_Top_Radius*2]);
                    }
            }
        }*/
        //Chamfer Top
        cylinder(d=Cylinder_Top_Diameter, h=Cylinder_Top_Height_Offset+z, $fn=cyl_fn);
        cylinder(d1=Cylinder_Top_Diameter+Cylinder_Top_Chamfer*2, d2=Cylinder_Top_Diameter, h=Cylinder_Top_Chamfer, $fn=cyl_fn);
    }
}

module ElementLabel(){
    for (n=[0:len(Cylinder_Label)-1]){
        rotate([0,0,Cylinder_Label_Spacing*n+Cylinder_Label_Offset-(len(Cylinder_Label)-1)*Cylinder_Label_Spacing/2])
        translate([Cylinder_Top_Diameter/2+Cylinder_Top_Chamfer, 0, Cylinder_Height-Cylinder_Top_Height_Offset])
        rotate([45, 0, 90])
        translate([0, Cylinder_Label_Height_Offset, -.05])
        minkowski(){
            linear_extrude(.09)
            text(text=Cylinder_Label[n], size=Cylinder_Label_Size, font=Cylinder_Label_Font, valign="baseline", halign="center");
            if (Debug_No_Minkowski!=true)
            scale([1,1,3])
            sphere(r=.05);
        }
    }
}

module CenterShaft(){
    translate([0,0,-z])
        cylinder(h=Cylinder_Height+2*z,d=Cylinder_Top_Shaft_Diameter, $fn=cyl_fn);
}


module HollowBody(){
    rotate_extrude($fn=cyl_fn){//Hollow Out Cylinder
        polygon([[Cylinder_Bottom_Shaft_Diameter/2,0-z],
            [Cylinder_Bottom_Shaft_Diameter/2,Cylinder_Height-Cylinder_Top_Height_Offset-4],
            [Cylinder_Top_Shaft_Diameter/2-z,Cylinder_Height-Cylinder_Top_Height_Offset],
            [0+z,-z]]);
    }
}

module AlignmentPin(){
    rotate([90,0,90]){
        linear_extrude(){//Cut Pin
            union(){
                hull(){
                    circle(d=Pin_Width, $fn=cyl_fn);
                    translate([0,Pin_Height-Pin_Width/2])
                    circle(d=Pin_Width, $fn=cyl_fn);   
                }
            }
        }
    }
}

module ResinSupport(){
$fn=resin_fn;
translate([0,0,-Resin_Support_Height+z]){
        rotate_extrude(){
                polygon([[Cylinder_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,Resin_Support_Thickness], [Cylinder_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
            }
            for (n=[0:1:11]){
                r1=(Cylinder_Diameter+Cylinder_Bottom_Shaft_Diameter)/4-.1;
                theta=360/12*n+360/12;
                translate([r1*cos(theta),r1*sin(theta),1]){
                    cylinder(h=Resin_Support_Height-2+Cylinder_Top_Height_Offset,d=Resin_Support_Wire_Thickness);
                    translate([0,0,Resin_Support_Height-2+Cylinder_Top_Height_Offset])
                    cylinder(h=1, d2=Resin_Support_Contact_Point, d1=Resin_Support_Wire_Thickness);
                }
                r2=(Cylinder_Top_Shaft_Diameter+Cylinder_Top_Diameter)/4;
                translate([r2*cos(theta+360/24),r2*sin(theta+360/24),1]){
                    if (n%2==0){
                        cylinder(h=-2+Resin_Support_Height,d=Resin_Support_Wire_Thickness);
                        translate([0,0,-2+Resin_Support_Height])
                        cylinder(h=1, d2=Resin_Support_Contact_Point, d1=Resin_Support_Wire_Thickness);
                    }
                }
            }
        }

}

module Assemble(){
    difference(){
        union(){
            TextRing();
            ElementChamfer();
            ElementLabel();
            if (Cylinder_Shape==0)
            PolygonCylinder();
            if (Cylinder_Shape==1)
            cylinder(d=Cylinder_Diameter, h=Cylinder_Height-Cylinder_Top_Height_Offset, $fn=cyl_fn);
        }
        CenterShaft();
        HollowBody();
        AlignmentPin();
    }
}

module ResinPrint(){
    union(){
        translate([0, 0, Cylinder_Height])
        rotate([0, 180, 0])
        Assemble();
        ResinSupport();
    }
    
}

if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
ResinPrint();