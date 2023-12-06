//Type Slug
//Leonard Chau
//October 5, 2023
/* [Global] */
$fn= $preview ? 10 : 40;
//Render Without Minkowski (fast)
Debug_No_Minkowski=true;

/* [Characters] */
//Alpha - Draft Angle of Characters
Draft_Angle=60;//[0:1:90]
//E - Minimum Height of Characters
Engraving_Depth=.5;//[0:.05:2]
//Gamma - Upper Wing Angle
Upper_Wing_Angle=20;//[0:1:90]
//Roh - Lower Wing Angle
Lower_Wing_Angle=10;//[0:1:90]
//Lower Case Character
Lower_Char="e";
//Upper Case Character
Upper_Char="E";
//Type Size
Type_Size=3;//[1:.05:5]
//Font
Typeface="CMU Typewriter Text";
//Enable SVG Logo?
SVG_Enable=false;
SVG_Vogue_Enable=true;
//SVG Size in mm
SVG_Size=2;//[0:.05:5]
SVG_V1_Size=1;
SVG_Scale=1/40*SVG_Size;
SVG_V1=1/80*SVG_V1_Size;
//SVG Extrusion Height
SVG_Depth=.05;//[0:.05:1]
//Percentage of Length from Bottom to Top
SVG_Location=.55;//[0:.05:1]
//SVG File
SVG_File="AR1.svg";
//Copyright Engraving Depth
Copyright_Depth=.1;//[0:.01:.1]
//Copyright Engraving Text
Copyright_Text="© Leonard Chau 2023";
//Copyright Text Font
Copyright_Font="Courier Prime";
Minkowski_Multiplier=1.6;

/* [Slug Details] */
//B - Typeslug Width
Body_Width=2.75;//[1:.05:5]
//A - Typeslug Length
Body_Length=12.0;//[5:.05:20]
//C - Typeslug Height
Body_Height=5;//[1:.05:10]
//Typeslug Face Thickness
Face_Thickness=.5;//[1:.05:3]
//Typeslug Corner Radius
Face_Radius=.2;//[0:.05:1]
//Wing Radius
Wing_Radius=2;//[0:.05:5]
//P - Platen Shift Motion
Platen_Shift_Motion=6.6;//[1:.05:10]
//O - Baselines Shift Motion
Baselines_Shift_Motion=6.6;//[1:.05:10]
//D - Typebar Slot Width
Body_Slot_Width=0.93;//[0:.01:3]
//G - Typeslug Wing Minimum Thickness
Wing_Thickness=.5;//[0:.01:3]
//From Bottom of Slug to Lowercase Platen Centerline Cut
Aligning_Cut=3.25;//[0:.05:5]
////From Bottom of Slug to Lowercase Baseline
Baseline=2;//[0:.05:5]
//R - Platen Diameter
Platen_Diameter=25.4;//[20:.05:40]
//F - Typeslug Face Thickness
Bottom_Thickness=1;//[0:.05:1]

/* [Resin Support] */
Resin_Support=true;
Raft_Thickness=2;
Wire_Thickness=.6;
Support_Height=2;
Support_Pitch=2;

/* [Loop] */
Loop=true;
Loop_Thickness=.75;//[0:.01:5]
Loop_Diameter=Body_Width;//[1:.01:5]
Loop_Rotation=0;//[0:45:180]


union(){
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
        if (SVG_Enable==true){
            minkowski(){
            linear_extrude(SVG_Depth)
            translate([0, Body_Length*SVG_Location, 0])
            scale([SVG_Scale, SVG_Scale, SVG_Scale])
            import(SVG_File, center=true);
            if (Debug_No_Minkowski!=true)
                translate([0,0,-Engraving_Depth*Minkowski_Multiplier])
                cylinder(h=Engraving_Depth*Minkowski_Multiplier, r1=sin(Draft_Angle)*Engraving_Depth*Minkowski_Multiplier, r2=0);
            }
        }
        if (SVG_Vogue_Enable==true){
            minkowski(){
            linear_extrude(SVG_Depth)
            translate([0, Body_Length*SVG_Location, 0])
            scale([SVG_Scale, SVG_Scale, SVG_Scale])
            import(SVG_File, center=true);
            if (Debug_No_Minkowski!=true)
                translate([0,0,-Engraving_Depth*Minkowski_Multiplier])
                cylinder(h=Engraving_Depth*Minkowski_Multiplier, r1=sin(Draft_Angle)*Engraving_Depth*Minkowski_Multiplier, r2=0);
            }
        }
        //Create Draft Angle Text
        minkowski(){
            difference(){
                translate([0, Baseline, 0])
                mirror([1, 0, 0]){
                #linear_extrude(2)
                text(text=Lower_Char, font=Typeface, size=Type_Size, halign="center", valign="baseline");
                #linear_extrude(2)
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
        translate([0,0,-Engraving_Depth*Minkowski_Multiplier])
        cylinder(h=Engraving_Depth*Minkowski_Multiplier, r1=sin(Draft_Angle)*Engraving_Depth*Minkowski_Multiplier, r2=0);
        }
    }
    //Clean Exposed Minkowski Manifold
    difference(){
        translate([0, Body_Length/2, -Body_Height/2])
        cube([20, 20, 20], center=true);
        hull(){
            translate([0, 0, -Face_Thickness])
            hull(){
            translate([-Body_Width/2+Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness+10);
            translate([Body_Width/2-Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness+10);
            translate([Body_Width/2-Face_Radius, Body_Length-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness+10);
            translate([-Body_Width/2+Face_Radius, Body_Length-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Face_Thickness+10);
            }
            
            translate([0, (Body_Height-Wing_Radius)*sin(Lower_Wing_Angle)+Wing_Radius, -Body_Height+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Body_Slot_Width+2*Wing_Thickness, center=true, $fn=360);
            translate([0, Body_Length-(Body_Height-Wing_Radius)*sin(Upper_Wing_Angle)-Wing_Radius, -Body_Height+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Body_Slot_Width+2*Wing_Thickness, center=true, $fn=360);
        }
    }
    //Typebar Slot
    translate([0, Body_Length/2, -Bottom_Thickness-(Body_Height+1)/2])
    cube([Body_Slot_Width, Body_Length+1, Body_Height+1], center=true);
    //Copyright
//    translate([0, Body_Length/2, -Bottom_Thickness+Copyright_Depth-.001])
//    rotate([0, 180, -90])
//    linear_extrude(Copyright_Depth)
//    text(text=Copyright_Text, font=Copyright_Font, size=Body_Slot_Width*.75, halign="center", valign="center");

    translate([Body_Width/2-Copyright_Depth, Body_Length/2, -Face_Thickness+.1])
    rotate([90, 0, 90])
    linear_extrude(Copyright_Depth+.01)
    #text(text=Copyright_Text, font=Copyright_Font, size=Body_Slot_Width*.75, halign="center", valign="center");
}

    if (Resin_Support==true){
    union(){
            translate ([0, Body_Length/2,-Body_Height-Support_Height]){
                hull(){
                    cube([Body_Width+4, Body_Length+4, .001], center=true);
                    translate([0, 0, -Raft_Thickness])
                    cube([Body_Width, Body_Length, .001], center=true);
                }
                
                
            }
            for (x=[(Body_Height-Wing_Radius)*sin(Lower_Wing_Angle)+Wing_Radius:Support_Pitch:Body_Length-(Body_Height-Wing_Radius)*sin(Upper_Wing_Angle)-Wing_Radius]){
                for (y=[1, -1]){
                    translate([y*(Body_Slot_Width/2+Wing_Thickness/2), x, -Body_Height-Support_Height]){
                        cylinder(h=Support_Height-1, d=Wire_Thickness);
                        translate([0, 0, Support_Height-1])
                        cylinder(d1=Wire_Thickness, d2=.3);
                        translate([0, 0, Support_Height])
                        sphere(d=.3);
                    }
                }
            }
        }
    }
    if (Loop==true){
        translate([0, Body_Length/*+Loop_Diameter/2-Loop_Thickness*/, -Loop_Thickness/2])
        rotate([0, Loop_Rotation, 0])
        rotate_extrude($fn=360){
            translate([Loop_Diameter/2-Loop_Thickness/2, 0])
            circle(d=Loop_Thickness, $fn=360);
        }
    }
}