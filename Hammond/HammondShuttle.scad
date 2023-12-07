ENGLISH=["qazwsxedcrfvtgbyhnujmik,ol.p;-",
         "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
         "1\"@2#×3$+4%£5_¢6&*7'^8(°9).0=/"];
Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 44;
//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
//Arc Radius of Shuttle
Shuttle_Inner_Arc_Radius=36.52;
//Thickness of Shuttle
Shuttle_Thickness=1;
//Height of Text Protrusion
Shuttle_Text_Protrusion=.5;
//Height of Shuttle
Shuttle_Height=13.6;
//Distance to Rib Plane from Top of Shuttle to Top of Rib Plane
Shuttle_Rib_Plane=6.7;
//Thickness of Rib
Shuttle_Rib_Thickness=.4;
//Width of Rib from Arc Radius
Shuttle_Rib_Width=2.8;
//Distance from Arc Radius to Square Hole Far Edge
Shuttle_Square_Hole_Offset=6.4;
//Square Hole Width
Shuttle_Square_Hole_Width=2.67;//2.54+.13
//Square Hole Length
Shuttle_Square_Hole_Length=1.0;
//Square Hole Support Height
Shuttle_Pin_Support_Height=.5;
//Square Hole Radius
Shuttle_Square_Hole_Radius=.4;
//Offset For Secondary Rib Circle
Shuttle_Rib_Circle_Offset=39;
//Baselines for Figures, Uppercase, Lowercase
Baselines=[3.3, 8.25, 12.75];
//Baseline Offsets for Baselines
Baselines_Offset=[0, 0, 0];
Baseline=Baselines-Baselines_Offset;

Layout=ENGLISH;
Typeface_="OpenDyslexicMono";//"Consolas";
Type_Size=2.45;//[1:.05:5]
//Check for Speedy Preview
Debug_No_Minkowski=true;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1;
//Generate Support?
Resin_Support=true;
//Resin Support Raft Thickness
Resin_Support_Base_Thickness=2;
//Resin Support Rod Thickness
Resin_Support_Rod_Thickness=.8;
//Minimum Height From Raft
Resin_Support_Min_Height=1;
//Spacing Between Resin Support Rods
Resin_Support_Spacing=3;
//Resin Support Connecting Point Diameter
Resin_Support_Contact_Diameter=.3;

 module regular_polygon(order,size){
     angles=[ for (i = [0:order-1]) i*(360/order) ];
     coords=[ for (th=angles) [size/2*cos(th), size/2*sin(th)] ];
     polygon(coords);
 }
 
 module ResinRod (h, r1, r2){
    cylinder(h=h-1, r=r1);
    translate([0, 0, h-1]){
        cylinder(h=1, r1=r1, r2=r2);
        translate([0, 0, 1])
        sphere(r=r2);
    }
 }
 
 module RadiusSquare(x,y,r,fn){
    $fn=fn;
    hull(){
        translate([r, r])
        circle(r);
        translate([x-r, r])
        circle(r);
        translate([r, y-r])
        circle(r);
        translate([x-r, y-r])
        circle(r);
    }
 }
 
 module LetterText (SomeCharacterRadius, SomeElement_Height, SomeBaseline, SomeTypeface_, SomeType_Size, SomeChar, SomeCharNo, SomeFinal_Min_Character_Height_Radius,SomeDebug, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    
            x=search(SomeChar, SomeScale_Multiplier_Text);
            angle_pitch=120/32;
            minkowski(){
            rotate([0, 0, if (SomeCharNo <= 14) -60+angle_pitch/2+angle_pitch*SomeCharNo])
        
            rotate([0, 0, if (SomeCharNo >=15) angle_pitch/2+angle_pitch*(SomeCharNo-14)])
            translate([SomeCharacterRadius,0,SomeElement_Height-SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            

            rotate([90, 0, 90])
            mirror([1,0,0])
            linear_extrude(SomeFinal_Min_Character_Height_Radius)
            scale([x==[] ? 1: SomeScale_Multiplier, x==[] ? 1: SomeScale_Multiplier, 1])
            if (SomeWeight_Adj_Mode==2)
                minkowski(){
                    text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    //circle(r=1, $fn=44);
                    square([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj], center=true);
                }
            else if (SomeWeight_Adj_Mode==1)
                difference(){
                    text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
                    }
                }
            else if (SomeWeight_Adj_Mode==0)
            text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
            
        if (SomeDebug != true)
            rotate([0, 0, if (SomeCharNo <= 14) -60+angle_pitch/2+angle_pitch*SomeCharNo])
            rotate([0, 0, if (SomeCharNo >=15) angle_pitch/2+angle_pitch*(SomeCharNo-14)])
            rotate([0, -90, 0])
            cylinder(h=1,r2=.75,r1=0);
    }
}

z_offset=Shuttle_Inner_Arc_Radius*cos(60);
y_max=Shuttle_Inner_Arc_Radius*sin(60);
x_max=Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness/2;
x_min=Shuttle_Height-x_max;
echo("z_offset", z_offset);
echo("y_max", y_max);
echo("x_min", x_min);
echo("x_max", x_max);

if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
union(){
    rotate([0, -90, 0])
    translate([-Shuttle_Inner_Arc_Radius*cos(60), 0, -x_max])
    difference(){
        union(){
            difference(){
                //Join LetterText and Cylinder
                union(){
                    translate([0, 0, -.01])
                    linear_extrude(Shuttle_Height+.02)
                    regular_polygon(96, 2*Shuttle_Inner_Arc_Radius+2*Shuttle_Thickness);
                    for (row = [0:1:2]){
                        for (column = [0:1:29]){
                            LetterText (Shuttle_Inner_Arc_Radius+Shuttle_Thickness-.01, Shuttle_Height, Baseline[row], Typeface_, Type_Size, Layout[row][29-column], column, Shuttle_Text_Protrusion,Debug_No_Minkowski, Character_Modifieds,Character_Modifieds_Offset, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                        }
                    }
                }
                //Remove 2/3rds and Center
                translate([0, 0, -5])
                linear_extrude(Shuttle_Height+10){
                    polygon([[Shuttle_Inner_Arc_Radius*3*cos(60), -Shuttle_Inner_Arc_Radius*3*sin(60)],[0, 0],  [Shuttle_Inner_Arc_Radius*3*cos(60), Shuttle_Inner_Arc_Radius*3*sin(60)], [0, 100], [-100, 0], [0, -100]]);
                    circle(r=Shuttle_Inner_Arc_Radius, $fn=Cylinder_fn);                
                }
                //Clean Bottom Minkowski
                rotate([0, 180, 0])
                cylinder(r=Shuttle_Inner_Arc_Radius+5, h=5);
                //Clean Top Minkowski
                translate([0, 0, Shuttle_Height])
                cylinder(r=Shuttle_Inner_Arc_Radius+5, h=5);
            }
            //Joining Rib
            translate([0, 0, Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness]){
                linear_extrude(Shuttle_Rib_Thickness){
                    difference(){
                        union(){
                            difference(){
                                circle(r=Shuttle_Inner_Arc_Radius+.01, $fn=Cylinder_fn);
                                circle(r=Shuttle_Inner_Arc_Radius-Shuttle_Rib_Width, $fn=Cylinder_fn);
                                polygon([[0, 0], [Shuttle_Inner_Arc_Radius*cos(60), Shuttle_Inner_Arc_Radius*sin(60)], [Shuttle_Inner_Arc_Radius*cos(60), -Shuttle_Inner_Arc_Radius*sin(60)]]);
                            }
                            //Rib Circle
                            intersection(){
                                translate([Shuttle_Rib_Circle_Offset, 0, 0])
                                circle(d=21.5, $fn=Cylinder_fn);
                                circle(r=Shuttle_Inner_Arc_Radius, $fn=Cylinder_fn);
                            }
                        }
                    polygon([[Shuttle_Inner_Arc_Radius*3*cos(60), -Shuttle_Inner_Arc_Radius*3*sin(60)],[0, 0],  [Shuttle_Inner_Arc_Radius*3*cos(60), Shuttle_Inner_Arc_Radius*3*sin(60)], [0, 100], [-100, 0], [0, -100]]);
                    }
                }
            }
            //Pin Support
//            translate([Shuttle_Inner_Arc_Radius-Shuttle_Square_Hole_Offset, 0, Shuttle_Height-Shuttle_Rib_Plane])
//            cylinder(d1=Shuttle_Pin_Support_Diameter+2, d2=Shuttle_Pin_Support_Diameter, h=Shuttle_Pin_Support_Height, $fn=Cylinder_fn);
            translate([Shuttle_Inner_Arc_Radius-Shuttle_Square_Hole_Offset, 0, Shuttle_Height-Shuttle_Rib_Plane-.01])
            minkowski(){
                translate([0, -Shuttle_Square_Hole_Width/2])
                linear_extrude(.01)
                RadiusSquare(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width, Shuttle_Square_Hole_Radius, Cylinder_fn);
                cylinder(h=Shuttle_Pin_Support_Height-.01, r1=Shuttle_Pin_Support_Height, r2=0);
            }
        }
        //Pin Support Hole
        translate([Shuttle_Inner_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, Shuttle_Height-Shuttle_Rib_Plane-.01])
        minkowski(){
            cube([Shuttle_Square_Hole_Length-2*Shuttle_Square_Hole_Radius, Shuttle_Square_Hole_Width-2*Shuttle_Square_Hole_Radius, 100], center=true);
            sphere(r=Shuttle_Square_Hole_Radius, $fn=Cylinder_fn);
        }
    }
    if (Resin_Support==true){
        union(){
        
            //Under Large Arc
            for (y=[-30:Resin_Support_Spacing:30])
                for (x=[-x_min+Resin_Support_Contact_Diameter/2,-x_min*2/3, -x_min*1/3, x_max*1/3, x_max*2/3, x_max-Resin_Support_Contact_Diameter/2]){
                    h=sqrt(Shuttle_Inner_Arc_Radius^2-y^2)-z_offset+Resin_Support_Min_Height;
                    translate([x, y, -Resin_Support_Min_Height-.01])
                    ResinRod (h+.01, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2);
                }
                
                //Under Rib - Outer
                for (y=[-27:Resin_Support_Spacing:27])
                if (y>=9 || y<=-9)
                translate([0, y, -Resin_Support_Min_Height-.01]){
                    h=sqrt((Shuttle_Inner_Arc_Radius-Shuttle_Rib_Width)^2-y^2)-z_offset+Resin_Support_Min_Height;
                    ResinRod(h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                }
                
                //Under Rib - Inner
                else{
                a=1;
                b=-(Shuttle_Rib_Circle_Offset)*2;
                c=Shuttle_Rib_Circle_Offset^2+y^2-(21.5/2)^2;
                h=(-b-sqrt(b^2-4*a*c))/(2*a)-z_offset+Resin_Support_Min_Height+.01;
            translate([0, y, -Resin_Support_Min_Height-.01])
            ResinRod(h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                }
                
                //Under Rib - Outer 2
                y_component=Shuttle_Inner_Arc_Radius*cos(30);
                
                hull(){
                translate([0, y_component,  -Resin_Support_Min_Height-.01])
                ResinRod(Resin_Support_Min_Height+.01, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                translate([0, 29.5,  -Resin_Support_Min_Height-.01])
                    
                    ResinRod(Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                }
                hull(){
                translate([0, -y_component,  -Resin_Support_Min_Height-.01])
                ResinRod(Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                translate([0, -29.5,  -Resin_Support_Min_Height-.01])
                    
                    ResinRod(Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2); 
                }
                
                //Outer Corners
                hull(){
                for (x=[-x_min+Resin_Support_Contact_Diameter/2, x_max-Resin_Support_Contact_Diameter/2]){
                    translate([x, y_component, -Resin_Support_Min_Height-.01])
                    ResinRod (Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2);
                    }
                }
                
                hull(){
                for (x=[-x_min+Resin_Support_Contact_Diameter/2, x_max-Resin_Support_Contact_Diameter/2]){
                    translate([x, -y_component, -Resin_Support_Min_Height-.01])
                    ResinRod (Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2);
                    }
                }
                //Resin Raft
            translate([0, 0, -Resin_Support_Min_Height]){
                hull($fn=Cylinder_fn){
                    cube([(Resin_Support_Base_Thickness+x_max)*2, (Resin_Support_Base_Thickness+y_max)*2, .01], center=true);
                    translate([0, 0, -Resin_Support_Base_Thickness])
                    cube([x_max*2, y_max*2, .01], center=true);
                }
            }
        }
    }
}