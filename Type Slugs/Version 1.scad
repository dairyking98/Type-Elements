//Type Slug
//Leonard Chau
//October 5, 2023
$fn=40;
Body_Width=2.75;//B
Body_Length=12.0;//A
Body_Height=5;//C
Platen_Shift_Motion=6.6;//P
Baselines_Shift_Motion=6.6;//O
Body_Slot_Width=0.93;//D
Wing_Thickness=.5;//G
Aligning_Cut=2.5;//Bottom of slug to lowercase cut centerline
Baseline=2;//Bottom of slug to lowercase baseline
Platen_Diameter=25.4;//R
Bottom_Thickness=1;//F
Draft_Angle=60;//alpha
Engraving_Depth=.5;//E
Upper_Wing_Angle=12;//gamma
Lower_Wing_Angle=10;//roh

Lower_Char="e";
Upper_Char="E";
Type_Size=3.05;
Typeface="Courier Prime";
SVG_Scale=1/40;
SVG_Depth=.2;
SVG_Location=.45;
SVG_File="AR1.svg";
Debug_No_Minkowski=true;


difference(){
    union(){
//Create Solid Type Body
        translate([-Body_Width/2, 0, -Body_Height])
        cube([Body_Width, Body_Length, Body_Height]);
        
//Create Draft Angle Text
        minkowski(){
        {
        translate([0,SVG_Location*Body_Length, 0])
        linear_extrude(SVG_Depth)
        scale([SVG_Scale, SVG_Scale, SVG_Scale])
        import(SVG_File);
        difference(){
            translate([0, Baseline, 0])
            mirror([1, 0, 0]){
            linear_extrude(2)
            text(text=Lower_Char, font=Typeface, size=Type_Size, halign="center", valign="baseline");
            linear_extrude(2)
            translate([0, Baselines_Shift_Motion, 0])
            text(text=Upper_Char, font=Typeface, size=Type_Size, halign="center", valign="baseline");
            }
            
//Platen Cutout
            translate([0,Aligning_Cut, Engraving_Depth+Platen_Diameter/2])
            rotate([0, 90, 0]){
                cylinder(h=Body_Width, d=Platen_Diameter, center=true, $fn=360);
                translate([0,Platen_Shift_Motion,0])
                cylinder(h=Body_Width, d=Platen_Diameter, center=true, $fn=360);
            }
        }
        }
        
    //Draft Angle Shape
	if (Debug_No_Minkowski!=true)
        translate([0,0,-Engraving_Depth*1.5])
        cylinder(h=Engraving_Depth*1.5, r1=sin(Draft_Angle)*Engraving_Depth*1.5, r2=0);
        }
    }

    rotate([-90, 0, 0]){
        
//Cut Typebar Slot
        translate([-Body_Slot_Width/2, Bottom_Thickness, -.001])
        linear_extrude(Body_Length+.002)
        square([Body_Slot_Width, 10]);

//Cut Wing Tapers
        translate([0, 0, -.001]){
            linear_extrude(Body_Length+.002)
            #polygon([[Body_Width/2, 0], [Body_Width/2, -Engraving_Depth], [Body_Width/2+1, -Engraving_Depth], [Body_Width/2+1, Body_Height], [Body_Slot_Width/2+Wing_Thickness, Body_Height]]);
            mirror([1, 0, 0])
            linear_extrude(Body_Length+.002)
            #polygon([[Body_Width/2, 0], [Body_Width/2, -Engraving_Depth], [Body_Width/2+1, -Engraving_Depth], [Body_Width/2+1, Body_Height], [Body_Slot_Width/2+Wing_Thickness, Body_Height]]);
        }
    }
    
//Cut Upper Wing Angle
translate([Body_Width/2+.001, Body_Length, 0])
rotate([90, 0, -90])
linear_extrude(10)
polygon([[-.001, 0], [Body_Height*1.5*sin(Upper_Wing_Angle), -Body_Height*1.5*cos(Upper_Wing_Angle)], [-Engraving_Depth, -Body_Height*1.5], [-Engraving_Depth, Engraving_Depth], [0, Engraving_Depth]]);

//Cut Lower Wing Angle
translate([-Body_Width/2-.001, 0, 0])
rotate([90, 0, 90])
linear_extrude(10)
polygon([[-.001, 0], [Body_Height*1.5*sin(Upper_Wing_Angle), -Body_Height*1.5*cos(Upper_Wing_Angle)], [-Engraving_Depth, -Body_Height*1.5], [-Engraving_Depth, Engraving_Depth], [0, Engraving_Depth]]);


}

