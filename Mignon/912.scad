//Mignon 2, 3, 4 Type Cylinder
//September 13, 2023
//Leonard Chau


//As Seen on Legend - \ before "
Layout=["'\"%&(£$);:,.",
        "?PFUGQpfugq¼",
        "!VINABvinab½",
        "_LDETMldetm¾",
        "JKOSRZkosrzj",
        "/YCHWXychwx@",
        "#1234567890-"];
CharLegend=[6,7,8,9,10,11,0,1,2,3,4,5];

Cylinder_Height=40;
Cylinder_Diameter=16.5;
Cylinder_Top_Height_Offset=3;
Cylinder_Top_Radius=2;
Cylinder_Top_Diameter=14;
Cylinder_Top_Shaft_Diameter=7.2;
Cylinder_Bottom_Shaft_Diameter=14.6;
Pin_Height=1.7;
Pin_Width=1.7;
Min_Final_Character_Diameter=17.4;
Platen_Diameter=25.4;

//Top to Bottom on Legend, Bottom to Top on Element
Baseline=[1.8,6.8,11.8,16.8,21.8,26.8,31.8];
Cutout=[3.225,8.225,13.225,18.225,23.225,28.225,33.225];
Cutout_Offset=0;
Baseline_Offset=1;

Typeface_="Consolas";
Type_Size=3.3;
Debug_No_Minkowski=true;

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
            cylinder(h=1,r2=.75,r1=0,$fn=6);
    }
}

//Module Cylinder (SomeCylinder_Height,SomeCylinder_Top_Height_Offset,SomeCylinder_Diameter,SomeCylinder_Top_Radius,SomeCylinder_Top)

difference(){
    union(){
        for (row=[0:1:len(Layout)-1]){
            for (n=[0:1:len(Layout[0])-1]){
                PickedChar=CharLegend[n];
                theta=-(360/(len(Layout[0]))*n);
                LetterText(Cylinder_Diameter-1,Baseline[row],Baseline_Offset,Cutout[row],Cutout_Offset,Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Min_Final_Character_Diameter,Debug_No_Minkowski);
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