//Type Slug
//Leonard Chau
//October 5, 2023
$fn= $preview ? 10 : 40;
//B - Typeslug Width
Body_Width=2.75;
//A - Typeslug Length
Body_Length=12.0;
//C - Typeslug Height
Body_Height=5;
Face_Thickness=.5;
Face_Radius=.2;
//Wing Radius
Wing_Radius=2;
//P - Platen Shift Motion
Platen_Shift_Motion=6.6;
//O - Baselines Shift Motion
Baselines_Shift_Motion=6.6;
//D - Typebar Slot Width
Body_Slot_Width=0.93;
//G - Typeslug Wing Minimum Thickness
Wing_Thickness=.5;
//From Bottom of Slug to Lowercase Platen Centerline Cut
Aligning_Cut=2.5;
////From Bottom of Slug to Uppercase Platen Centerline Cut
Baseline=2;
//R - Platen Diameter
Platen_Diameter=25.4;
//F - Typeslug Face Thickness
Bottom_Thickness=1;
//Alpha - Draft Angle of Characters
Draft_Angle=60;
//E - Minimum Height of Characters
Engraving_Depth=.5;
//Gamma - Upper Wing Angle
Upper_Wing_Angle=20;
//Roh - Lower Wing Angle
Lower_Wing_Angle=10;//roh
//Lower Case Character
Lower_Char="e";
//Upper Case Character
Upper_Char="E";
//Type Size
Type_Size=2.8;
//Font
Typeface="Courier Prime";
//SVG Size in mm
SVG_Size=2;
SVG_Scale=1/40*SVG_Size;
//SVG Extrusion Height
SVG_Depth=.05;
//Percentage of Length from Bottom to Top
SVG_Location=.5;
//SVG File
SVG_File="AR1.svg";
//Render Without Minkowski (fast)
Debug_No_Minkowski=true;

difference(){
    union(){
        //Create Solid Type Body
        
        hull(){
            translate([0, 0, -Face_Thickness])
            hull(){
            translate([-Body_Width/2+Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness);
            translate([Body_Width/2-Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness);
            translate([Body_Width/2-Face_Radius, Body_Length-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness);
            translate([-Body_Width/2+Face_Radius, Body_Length-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness);
            }
            
            translate([0, (Body_Height-Wing_Radius)*sin(Lower_Wing_Angle)+Wing_Radius, -Body_Height+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Body_Slot_Width+2*Wing_Thickness, center=true, $fn=360);
            translate([0, Body_Length-(Body_Height-Wing_Radius)*sin(Upper_Wing_Angle)-Wing_Radius, -Body_Height+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Body_Slot_Width+2*Wing_Thickness, center=true, $fn=360);
        }
        //SVG Logo
        minkowski(){
        linear_extrude(SVG_Depth)
        translate([0, Body_Length*SVG_Location, 0])
        scale([SVG_Scale, SVG_Scale, SVG_Scale])
        import(SVG_File, center=true);
        if (Debug_No_Minkowski!=true)
            translate([0,0,-Engraving_Depth*1.5])
            cylinder(h=Engraving_Depth*1.5, r1=sin(Draft_Angle)*Engraving_Depth*1.5, r2=0);
        }
        //Create Draft Angle Text
        minkowski(){
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
    //Draft Angle Shape
	if (Debug_No_Minkowski!=true)
        translate([0,0,-Engraving_Depth*1.5])
        cylinder(h=Engraving_Depth*1.5, r1=sin(Draft_Angle)*Engraving_Depth*1.5, r2=0);
        }
    }
    
    
    //Typebar Slot
    translate([0, Body_Length/2, -Bottom_Thickness-(Body_Height+1)/2])
    cube([Body_Slot_Width, Body_Length+1, Body_Height+1], center=true);
    //Clean Top Chamfers
    translate([0, Body_Length/2, 0]){
        difference(){
            cube([Body_Width*1.5, Body_Length*1.5, 20], center=true);
            cube([Body_Width, Body_Length, 21], center=true);
        }
    }
    
   
//    //Side Wings
//    rotate([-90, 0, 0]){
//    translate([0, 0, -.001]){
//        linear_extrude(Body_Length+.002)
//        polygon([[Body_Width/2, Face_Thickness], [Body_Width/2+1, 0], [Body_Width/2+1, Body_Height+.001], [Body_Slot_Width/2+Wing_Thickness, Body_Height+.001]]);
//        mirror([1, 0, 0])
//        linear_extrude(Body_Length+.002)
//        polygon([[Body_Width/2, Face_Thickness], [Body_Width/2+1, 0], [Body_Width/2+1, Body_Height+.001], [Body_Slot_Width/2+Wing_Thickness, Body_Height+.001]]);
//        }
//    }
}