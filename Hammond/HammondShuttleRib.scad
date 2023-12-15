Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 44;
//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
//Global variable to prevent z-fighting
z=.001;

/* [Shuttle Dimensions] */
//Arc Radius of Shuttle
Shuttle_Arc_Radius=36.52;
//Thickness of Shuttle
Shuttle_Thickness=1;
//Height of Text Protrusion
Shuttle_Text_Protrusion=.5;
//Height of Shuttle
Shuttle_Height=13.6;
//Height of Math Shuttle
Shuttle_Height_Math=18;
//Distance to Rib Plane from Top of Shuttle to Top of Rib Plane
Shuttle_Rib_Plane=6.7;
//Thickness of Rib
Shuttle_Rib_Thickness=.34;/*
.2794 is original measurement + .06 printer offset

*/
//Width of Rib from Arc Radius
Shuttle_Rib_Width=2.8;
//Distance from Arc Radius to Square Hole Far Edge
Shuttle_Square_Hole_Offset=6.47;//6.47 is OEM measurement
//Square Hole Width
Shuttle_Square_Hole_Width=2.67;//2.54 OEM measurement + .13 printer offset
//Square Hole Length
Shuttle_Square_Hole_Length=2.67;
//Square Hole Support Height
Shuttle_Pin_Support_Height=.5;
//Square Hole Radius
Shuttle_Square_Hole_Radius=.4;
//Distance From Flat Plane to Center Rib Hump
Shuttle_Rib_Hump_Distance=10;
//Shuttle Rib Circle Radius
Shuttle_Rib_Circle=100;
//Rib Circle Radius to Rib
Shuttle_Rib_Circle_Radius=8;
//Degrees for Shuttle Taper
Shuttle_Taper=2;
//Offset From Arc Radius for Taper
Shuttle_Taper_Step=.5;

Groove=false;
Shuttle_Groove_Depth=.5;
Shuttle_Groove_Nub_Size=.5;
Shuttle_Groove_Nub_Angle=29;

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

/* [Support Structure] */
//Generate Support?
Resin_Support=true;
//Resin Support Raft Thickness
Resin_Support_Base_Thickness=1.5;
//Resin Support Rod Thickness
Resin_Support_Rod_Thickness=.8;
//Minimum Height From Raft
Resin_Support_Min_Height=1;
//Spacing Between Resin Support Rods
Resin_Support_Spacing=3;
//Resin Support Connecting Point Diameter
Resin_Support_Contact_Diameter=.3;
//Resin Support Gap from Part Edges
Resin_Support_EdgeGap=.3;
//Resin Support Buildplate Radius
Resin_Support_Buildplate_Radius=.8;

grooverad=Shuttle_Arc_Radius+Shuttle_Groove_Depth;

//Taper Variables
taper_inset_x=(Shuttle_Arc_Radius-z)*cos(60-Shuttle_Taper);
taper_inset_y=(Shuttle_Arc_Radius-z)*sin(60-Shuttle_Taper);
taper_outset_x=cos(60+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);
taper_outset_y=sin(60+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);
echo (taper_inset_x);

//Reorientation Variables, Global Variables
z_offset=Shuttle_Arc_Radius*cos(60);
y_max=Shuttle_Arc_Radius*sin(60);
x_max=Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness/2;
x_min=Shuttle_Height-x_max;

//Offset For Secondary Rib Circle
Shuttle_Rib_Circle_Offset=z_offset+Shuttle_Rib_Circle+Shuttle_Rib_Hump_Distance;


//Support Variables
innerarcintercept=sqrt((Shuttle_Arc_Radius-Shuttle_Rib_Width)^2-z_offset^2);
outerarcintercept=sqrt((Shuttle_Arc_Radius)^2-z_offset^2);
                
//Shuttle Rib Radius Variables
yprime=(2*Shuttle_Rib_Circle_Offset)^-1*(Shuttle_Rib_Circle_Offset^2+(Shuttle_Arc_Radius-Shuttle_Rib_Circle_Radius-Shuttle_Rib_Width)^2-(Shuttle_Rib_Circle_Radius+Shuttle_Rib_Circle)^2);
xprime=sqrt((Shuttle_Arc_Radius-Shuttle_Rib_Circle_Radius-Shuttle_Rib_Width)^2-yprime^2);
thetaa=atan(yprime/xprime);
theta2=atan((Shuttle_Rib_Circle_Offset-yprime)/xprime);
cp1x=Shuttle_Arc_Radius*cos(thetaa);//limit of resin support
cp1y=Shuttle_Arc_Radius*sin(thetaa);
cp2x=xprime-Shuttle_Rib_Circle_Radius*cos(theta2);//limit of resin support
cp2y=yprime+(Shuttle_Rib_Circle_Radius)*sin(theta2);

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

difference(){
    linear_extrude(Shuttle_Rib_Thickness){
        difference(){
            union(){
                difference(){
                    circle(r=grooverad, $fn=Cylinder_fn);
                    circle(r=Shuttle_Arc_Radius-Shuttle_Rib_Width, $fn=Cylinder_fn);
                    polygon([[0, 0], [Shuttle_Arc_Radius*cos(60), Shuttle_Arc_Radius*sin(60)], [Shuttle_Arc_Radius*cos(60), -Shuttle_Arc_Radius*sin(60)]]);
                }
                
                //Rib Circle
                intersection(){
                    translate([Shuttle_Rib_Circle_Offset, 0, 0])
                    circle(r=Shuttle_Rib_Circle, $fn=Cylinder_fn);
                    circle(r=grooverad, $fn=Cylinder_fn);
                }
                
                //Add Rib Circle Radius
                for (n=[-1, 1])
                difference(){
                    polygon([[yprime, n*xprime], [cp1y, n*cp1x], [sqrt(Shuttle_Arc_Radius^2-(n*cp2x)^2),n*cp2x], [cp2y, n*cp2x] ]);
                    translate([yprime, n*xprime, 0])
                circle(r=Shuttle_Rib_Circle_Radius, $fn=360);
                }
            }
            
        polygon([[Shuttle_Arc_Radius*3*cos(60), -Shuttle_Arc_Radius*3*sin(60)],[0, 0],  [Shuttle_Arc_Radius*3*cos(60), Shuttle_Arc_Radius*3*sin(60)], [0, 100], [-100, 0], [0, -100]]);
        }
    }
    translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, -Shuttle_Square_Hole_Width/2, -5])
    linear_extrude(20)
    RadiusSquare(Shuttle_Square_Hole_Length,Shuttle_Square_Hole_Width,Shuttle_Square_Hole_Radius,Cylinder_fn);

    translate([0, 0, -5])
        for (n=[-2:1:2]){
        rotate([0, 0, Shuttle_Groove_Nub_Angle*n])
        translate([Shuttle_Arc_Radius+Shuttle_Groove_Depth, 0, 0])
        cylinder(h=10, r=Shuttle_Groove_Nub_Size, $fn=Cylinder_fn);
        }
    

}