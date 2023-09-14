//Mignon 2, 3, 4 Type Cylinder
//September 13, 2023
//Leonard Chau


//ADD RESIN SUPPORT
/* [Character Details] */
//As Seen on Legend
LAYOUT=["'\"%&(£$);:,.",
        "?PFUGQpfugq¼",
        "!VINABvinab½",
        "_LDETMldetm¾",
        "JKOSRZkosrzj",
        "/YCHWXychwx@",
        "#1234567890-"];
CharLegend=[6,7,8,9,10,11,0,1,2,3,4,5];

//Custom Layout
1st_Row="";
2nd_Row="";
3rd_Row="";
4th_Row="";
5th_Row="";
6th_Row="";
7th_Row="";
CUSTOMLAYOUT=[1st_Row,2nd_Row,3rd_Row,4th_Row,5th_Row,6th_Row,7th_Row];

//Use Custom Layout?
Custom_Layout=false;
Layout= Custom_Layout==false ? LAYOUT : CUSTOMLAYOUT;
//Tallen the Element Height?
Tallen=false;
//Element Height Increase
Height_Increase=3;


Typeface_="Consolas";//As Installed on PC
Type_Size=3.3;//Type Size
Debug_No_Minkowski=true;//Speedy Preview and Render with No Minkowski

/* [Cylinder Details] */
//Total Cylinder Height
Cylinder_Height_=40;
Cylinder_Height= Tallen==true ? Cylinder_Height_+Height_Increase : Cylinder_Height_;
//Main Cylinder Diameter
Cylinder_Diameter=16.5;
//Height Drop From Top
Cylinder_Top_Height_Offset=3;
//Height Drop Chamfer Radius
Cylinder_Top_Radius=2;
//Height Drop Diameter
Cylinder_Top_Diameter=14;
//Inner Shaft Diameter
Cylinder_Top_Shaft_Diameter=7.2;
//Inner Mounting Diameter
Cylinder_Bottom_Shaft_Diameter=14.6;
//Max Pin Height
Pin_Height=1.8;
//Max Pin Width
Pin_Width=1.7;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=17.4;
//Platen Diameter
Platen_Diameter=25.4;

/* [Character Placement Details] */
//[1st, 2nd, 3rd, 4th, 5th, 6th, 7th] Baseline Height
Baseline=[1.8,6.8,11.8,16.8,21.8,26.8,31.8];
Cutout=[3.225,8.225,13.225,18.225,23.225,28.225,33.225];
Cutout_Offset=[0.6,0.6,0.6,0.6,0.6,0.6,0.6];//[0,0,0,0,0,0,0];
Baseline_Offset=[0.6,0.6,0.6,0.6,0.6,0.6,0.6]; //,0,0,0,0,0,0];//[1,1,1,1,1,1,1];


//Number of Facets of Cylinder
$fn=12*10;



module LetterText (SomeElement_Diameter,SomeBaseline,SomeBaseline_Offset,SomeCutout,SomeCutout_Offset, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomePlaten_Diameter,SomeMin_Final_Character_Diameter,SomeDebug){
    $fn = $preview ? 12 : 24;
    
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBaseline+SomeBaseline_Offset])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
            text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout+SomeCutout_Offset])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1.5,r2=.75,r1=0,$fn=6);
    }
}

//Module Cylinder (SomeCylinder_Height,SomeCylinder_Top_Height_Offset,SomeCylinder_Diameter,SomeCylinder_Top_Radius,SomeCylinder_Top)

difference(){
    union(){
        for (row=[0:1:len(Layout)-1]){
            for (n=[0:1:len(Layout[0])-1]){
                PickedChar=CharLegend[n];
                theta=-(360/(len(Layout[0]))*n);
                if (Layout[row][PickedChar] != " "){
                    LetterText(Cylinder_Diameter-1,Baseline[row],Baseline_Offset[row],Cutout[row],Cutout_Offset[row],Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Min_Final_Character_Diameter,Debug_No_Minkowski);
                }
                }
            }
        
        cylinder(h=Cylinder_Height-Cylinder_Top_Height_Offset,d=Cylinder_Diameter);
        translate([0,0,Cylinder_Height-Cylinder_Top_Radius])
        hull(){
            rotate_extrude($fn=60){
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
        }
    }
    
    translate([0,0,-.001])
    cylinder(h=Cylinder_Height+2*.001,d=Cylinder_Top_Shaft_Diameter);
    rotate_extrude(){
        polygon([[Cylinder_Bottom_Shaft_Diameter/2,0-.001],
            [Cylinder_Bottom_Shaft_Diameter/2,15],
            [0+.001,19],
            [0+.001,-.001]]);
    }
    rotate([90,0,90]){
        linear_extrude(){
            union(){
                translate([-Pin_Width/2,Pin_Width/2-Pin_Height])
                square([Pin_Width,Pin_Height]);
                translate([0,Pin_Height-Pin_Width/2])
                circle(d=Pin_Width);
            }
        }
    }
}