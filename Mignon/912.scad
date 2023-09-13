
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
Cylinder_Top_Shaft_Diameter=7.2;
Cylinder_Bottom_Shaft_Diameter=14.6;
Pin_Height=1.8;
Pin_Width=1.7;
Min_Final_Character_Diameter=17.4;
Platen_Diameter=25.4;

//Top to Bottom on Legend, Bottom to Top on Element
Baseline=[1.8,6.8,11.8,16.8,21.8,26.8,31.8];
Baseline_Offset=[1.4,1.4,1.4,1.4,1.4,1.4,1.4];

Typeface_="Consolas";
Type_Size=3.3;
Debug_No_Minkowski=true;

$fn=12*10;

rotate([0,0,0])
cylinder(h=Cylinder_Height,d=Cylinder_Diameter);

module LetterText (SomeElement_Diameter,SomeBaseline,SomeBaseline_Offset, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomePlaten_Diameter,SomeMin_Final_Character_Diameter,SomeDebug){
    $fn = $preview ? 12 : 24;
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBaseline])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
            text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeBaseline+SomeBaseline_Offset])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1,r2=.75,r1=0,$fn=6);
    }
}
for (row=[0:1:len(Layout)-1]){
    for (n=[0:1:len(Layout[0])-1]){
        PickedChar=CharLegend[n];
        theta=-(360/(len(Layout[0]))*n);
        LetterText(Cylinder_Diameter-1,Baseline[row],Baseline_Offset[row],Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Min_Final_Character_Diameter,Debug_No_Minkowski);
    }
}