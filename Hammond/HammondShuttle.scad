ENGLISH=["qazwsxedcrfvtgbyhnujmik,ol.p;-",
         "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
         "1\"@2#×3$+4%£5_¢6&*7'^8(°9).0=/"];

MATH=["qazwsxedcrfvtgbyhnujmik,ol.p·√",
         "QAZWSXEDCRFVTGBYHNUJMIK?OL∂P:∫",
        "1\"_2∑×3Δ+4∞[5Γ]6⁘*7'|8(<9)>0=/",
         "₁αζ₂σξ₃δρ₄ψθ₅γβ₆ητ₇εφ₈κω₉λπ₀ₙ-"];
         
 
Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 44;
//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
//Vertical or Horizontal Orientation?
Horizontal=false;
//Apply Testing Baselines?
testing=false;
//Testing Character
testchar="H";
testingoffsets=[-.7, -.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .66, .7, .75];
echo (len(testingoffsets));
//Global variable to prevent z-fighting
z=.001;

/* [Text Dimensions] */
//Baselines for Lowercase, Uppercase, Figures, and Math FROM BOTTOM RIB PLANE
Baselines=[3.74, -1.21, -5.71, -9.96];
//Baseline Offsets for Baselines
Baselines_Offset=[0, 0, 0, 0];
Layout_Selection=ENGLISH;
//Enable Math Layout and Design? (4 Rows)
Math=false;
Layout=Math?MATH:Layout_Selection;
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

/* [Shuttle Dimensions] */
//Arc Radius of Shuttle
Shuttle_Arc_Radius=36.52;
//Thickness of Shuttle
Shuttle_Thickness=1;
//Height of Text Protrusion
Shuttle_Text_Protrusion=.5;
//Height of Shuttle
Shuttle_Height_=13.6;
//Height of Math Shuttle
Shuttle_Height_Math=18;
Shuttle_Height=Math?Shuttle_Height_Math:Shuttle_Height_;
//Distance From Top of Shuttle to BOTTOM of RIB PLANE
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
////Vertical Resin Support Raft Thickness
Resin_Support_Base_Thickness=1.5;
//Vertical Resin Support Rod Thickness
Resin_Support_Rod_Thickness=.8;
//Vertical Minimum Height From Raft
Resin_Support_Min_Height=1;
//Vertical Spacing Between Resin Support Rods
Resin_Support_Spacing=3;
//Vertical Resin Support Connecting Point Diameter
Resin_Support_Contact_Diameter=.3;
//Vertical Resin Support Gap from Part Edges
Resin_Support_EdgeGap=.3;
//Vertical Resin Support Buildplate Radius
Resin_Support_Buildplate_Radius=.8;
//Horizontal Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.5;
//Horizontal Resin Support Cut Groove Minimum Thickness
Resin_Support_Cut_Groove_Min_Thickness=.2;

Baseline=Baselines+Baselines_Offset;
//Taper Variables
taper_inset_x=(Shuttle_Arc_Radius-z)*cos(60-Shuttle_Taper);
taper_inset_y=(Shuttle_Arc_Radius-z)*sin(60-Shuttle_Taper);
taper_outset_x=cos(60+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);
taper_outset_y=sin(60+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);

//Reorientation Variables, Global Variables
z_offset=Shuttle_Arc_Radius*cos(60);
y_max=Shuttle_Arc_Radius*sin(60);
x_max=Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness/2;
x_min=Shuttle_Height-x_max;
rib_bottomz=Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness;

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


 module regular_polygon(order,size){
     angles=[ for (i = [0:order-1]) i*(360/order) ];
     coords=[ for (th=angles) [size/2*cos(th), size/2*sin(th)] ];
     polygon(coords);
 }
 
 module ResinRod (h1, r1, r2, h2, r3){
    cylinder(h=h1-1, r=r1);
    cylinder(h=h2, r1=r3, r2=r3+h2);
    translate([0, 0, h1-1]){
        cylinder(h=1, r1=r1, r2=r2);
        if (h1>h2)
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
 
 module ConnectingRod (p1, p2, t){
    hull(){
        translate(p1)
        sphere(d=t);
        translate(p2)
        sphere(d=t);
    }
}
 
 module LetterText (SomeCharacterRadius, SomeBaseline, SomeTypeface_, SomeType_Size, SomeChar, SomeCharNo, SomeFinal_Min_Character_Height_Radius,SomeDebug, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    
            x=search(SomeChar, SomeScale_Multiplier_Text);
            angle_pitch=120/32;
            minkowski(){
            rotate([0, 0, if (SomeCharNo <= 14) -60+angle_pitch/2+angle_pitch*SomeCharNo])
        
            rotate([0, 0, if (SomeCharNo >=15) angle_pitch/2+angle_pitch*(SomeCharNo-14)])
            translate([SomeCharacterRadius,0,SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            

            rotate([90, 0, 90])
            mirror([1,0,0])
            linear_extrude(SomeFinal_Min_Character_Height_Radius)
            if (SomeWeight_Adj_Mode==2)
                minkowski(){
                    text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    //circle(r=1, $fn=44);
                    square([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj], center=true);
                }
            else if (SomeWeight_Adj_Mode==1)
                difference(){
                    text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
                    }
                }
            else if (SomeWeight_Adj_Mode==0)
            text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
            
        if (SomeDebug != true)
            rotate([0, 0, if (SomeCharNo <= 14) -60+angle_pitch/2+angle_pitch*SomeCharNo])
            rotate([0, 0, if (SomeCharNo >=15) angle_pitch/2+angle_pitch*(SomeCharNo-14)])
            rotate([0, -90, 0])
            cylinder(h=1,r2=.75,r1=0);
    }
}

if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
union(){
    rotate([0, Horizontal?0:-90, 0])
    translate([-Shuttle_Arc_Radius*cos(60), 0, Horizontal?0:-x_max])
    
    difference(){
        union(){
            difference(){
                //Join LetterText and Cylinder
                union(){
                    translate([0, 0, -z])
                    linear_extrude(Shuttle_Height+2*z)
                    regular_polygon(96, 2*Shuttle_Arc_Radius+2*Shuttle_Thickness);
                    for (row = [0:1:Math?3:2]){
                        for (column = [0:1:29]){
                        
                            testingbaseline=testing?testingoffsets[column]:0;
                            char=ENGLISH[row][column];
                            baseline=Baseline[row]-testingbaseline;
                            
                            if (testing==true)
                            echo(char=char,baseline=baseline);
                        
                            LetterText (Shuttle_Arc_Radius+Shuttle_Thickness-z, rib_bottomz+Baseline[row]+(testing?testingoffsets[column]:0), Typeface_, Type_Size, testing?testchar:Layout[row][29-column], column, Shuttle_Text_Protrusion,Debug_No_Minkowski, Character_Modifieds,Character_Modifieds_Offset, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                        }
                    }
                }
                
                //Remove 2/3rds and Center
                translate([0, 0, -5])
                linear_extrude(Shuttle_Height+10){
                    polygon([[Shuttle_Arc_Radius*3*cos(60), -Shuttle_Arc_Radius*3*sin(60)],[0, 0],  [Shuttle_Arc_Radius*3*cos(60), Shuttle_Arc_Radius*3*sin(60)], [0, 100], [-100, 0], [0, -100]]);
                    circle(r=Shuttle_Arc_Radius, $fn=Cylinder_fn);                
                }
                
                //Clean Bottom Minkowski
                rotate([0, 180, 0])
                cylinder(r=Shuttle_Arc_Radius+5, h=5);
                //Clean Top Minkowski
                translate([0, 0, Shuttle_Height])
                cylinder(r=Shuttle_Arc_Radius+5, h=5);
            
                //Groove Shape
                if (Groove==true){
                    translate([0, 0, rib_bottomz])
                    difference(){
                        cylinder(r=Shuttle_Arc_Radius+Shuttle_Groove_Depth, h=Shuttle_Rib_Thickness, $fn=Cylinder_fn);
                        for (n=[-2:1:2]){
                        rotate([0, 0, Shuttle_Groove_Nub_Angle*n])
                        translate([Shuttle_Arc_Radius+Shuttle_Groove_Depth, 0, 0])
                        cylinder(h=Shuttle_Rib_Thickness, r=Shuttle_Groove_Nub_Size, $fn=Cylinder_fn);
                        }
                    }
                    }
                
            
            }
            
            //Joining Rib
            if (Groove==false){
                translate([0, 0, rib_bottomz]){
                    linear_extrude(Shuttle_Rib_Thickness){
                        difference(){
                            union(){
                                difference(){
                                    circle(r=Shuttle_Arc_Radius+z, $fn=Cylinder_fn);
                                    circle(r=Shuttle_Arc_Radius-Shuttle_Rib_Width, $fn=Cylinder_fn);
                                    polygon([[0, 0], [Shuttle_Arc_Radius*cos(60), Shuttle_Arc_Radius*sin(60)], [Shuttle_Arc_Radius*cos(60), -Shuttle_Arc_Radius*sin(60)]]);
                                }
                                
                                //Rib Circle
                                intersection(){
                                    translate([Shuttle_Rib_Circle_Offset, 0, 0])
                                    circle(r=Shuttle_Rib_Circle, $fn=Cylinder_fn);
                                    circle(r=Shuttle_Arc_Radius, $fn=Cylinder_fn);
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
                }
            }
            
            //Pin Support
            if (Groove==false){
                translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset, 0, Shuttle_Height-Shuttle_Rib_Plane-z])
                minkowski(){
                    translate([0, -Shuttle_Square_Hole_Width/2])
                    linear_extrude(z)
                    RadiusSquare(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width, Shuttle_Square_Hole_Radius, Cylinder_fn);
                    cylinder(h=Shuttle_Pin_Support_Height-z, r1=Shuttle_Pin_Support_Height, r2=0);
                }
            }
        }
        if (Groove==false){
            //Pin Support Hole
            translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset, 0, 0])
            translate([0, -Shuttle_Square_Hole_Width/2, -z])
            linear_extrude(Shuttle_Height+z)
            RadiusSquare(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width, Shuttle_Square_Hole_Radius, Cylinder_fn);
            }
        
            
        //Shuttle Taper 
        for (a=[0,1]){
            b=[-z, Shuttle_Height-Shuttle_Rib_Plane];
            c=[rib_bottomz+z+(Groove?2:0), 10];
            d=[-1,1];
            translate([0, 0, b[a]])
            linear_extrude(c[a])
            polygon([[taper_inset_x, taper_inset_y], [taper_outset_x, taper_outset_y], (Shuttle_Arc_Radius-z)*[cos(60+z), sin(60+z)]]);
            translate([0, 0, b[a]])
            linear_extrude(c[a])
            polygon([[taper_inset_x, -taper_inset_y], [taper_outset_x, -taper_outset_y], (Shuttle_Arc_Radius-z)*[cos(60+z), -sin(60+z)]]);
        }
        
        //Label
        //angle_pitch=120/32;
            rotate([0, 0, 120/32*.25])
            translate([Shuttle_Arc_Radius+Shuttle_Thickness-Shuttle_Label_Depth, 0, Shuttle_Height/2])
            rotate([0, 90, 0])
            linear_extrude(2)
            text(text=Shuttle_Label1, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
            
            rotate([0, 0, -120/32+120/32*.25])
            translate([Shuttle_Arc_Radius+Shuttle_Thickness-Shuttle_Label_Depth, 0, Shuttle_Height/2])
            rotate([0, 90, 0])
            linear_extrude(2)
            text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
    }
    
    if (Resin_Support==true && Horizontal==false){
        union(){
            translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness]){
                //Under Large Arc
                for (y=[-(round(30/Resin_Support_Spacing)+1)*Resin_Support_Spacing:Resin_Support_Spacing:(round(30/Resin_Support_Spacing)+1)*Resin_Support_Spacing]){
                
                    if (abs(y)<=taper_inset_y)
                    for (x=[-x_min+Resin_Support_Contact_Diameter/2,-x_min*2/3, -x_min*1/3, x_max*1/3, x_max*2/3, x_max-Resin_Support_Contact_Diameter/2]){
                        h=sqrt(Shuttle_Arc_Radius^2-y^2)-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
                        translate([x, y,0])
                        ResinRod (h+z, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
                    }
                    if (Groove==false){
                        //Under Rib - Outer
                        if (abs(y)>cp1x && abs(y)<=innerarcintercept){
                                h=sqrt((Shuttle_Arc_Radius-Shuttle_Rib_Width)^2-y^2)-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
                            translate([0, y,0]){
                                ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                            }
                            if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
                            for (n=[-1,1])
                            ConnectingRod([0,y,h-1],[n*x_min*1/3,y,h-4],Resin_Support_Rod_Thickness);
                            }
                        
                        //Under Rib - Radius 
                        if (abs(y)<=cp1x && abs(y)>cp2x){
                            h=sqrt(Shuttle_Rib_Circle_Radius^2-(abs(y)-xprime)^2)+yprime-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
                            translate([0, y,0]){
                                ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                            }
                            if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
                            for (n=[-1,1])
                            ConnectingRod([0,y,h-1],[n*x_min*1/3,y,h-4],Resin_Support_Rod_Thickness);
                        }
                        
                        //Under Rib - Center
                        else if (abs(y)<=cp2x){
                            a=1;
                            b=-(Shuttle_Rib_Circle_Offset)*2;
                            c=Shuttle_Rib_Circle_Offset^2+y^2-(Shuttle_Rib_Circle)^2;
                            h=(-b-sqrt(b^2-4*a*c))/(2*a)-z_offset+Resin_Support_Min_Height+z+Resin_Support_Base_Thickness;
                        translate([0, y,0])
                        ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                        if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
                        for (n=[-1,1])
                        ConnectingRod([0,y,h-1],[n*x_min*1/3,y,h-4],Resin_Support_Rod_Thickness);
                        }
                    }
                }
                    
                    //Under Rib - Rib Thickness on Edges
                    //Associated Variables
                y_component_taper=(Shuttle_Arc_Radius+Shuttle_Taper_Step)*cos(30);
                z_component=(Shuttle_Taper_Step)*sin(30);
                y_component=(Shuttle_Arc_Radius)*cos(30)-.3;
                y_component_inner=y_component-Shuttle_Rib_Width*cos(30)-.2;
                //tall part
                if (Groove==false){
                hull(){
                    translate([0, -outerarcintercept+Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                  
                    translate([0, -innerarcintercept-Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                    }
                    //tall part
                    hull(){
                    translate([0, outerarcintercept-Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                    translate([0, innerarcintercept+Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                    }
                
                //buildplate part
                hull(){
                    translate([0, -outerarcintercept+Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                    translate([0, -innerarcintercept-Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                }
                //buildplate part
                hull(){
                    translate([0, outerarcintercept-Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                    translate([0, innerarcintercept+Resin_Support_EdgeGap, 0])
                    ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                }
                }
                //Outer Edge Supports
                hull(){
                    for (x=[-x_min+Resin_Support_Contact_Diameter/2+Resin_Support_EdgeGap, x_max-Resin_Support_Contact_Diameter/2-Resin_Support_EdgeGap]){
                        translate([x, y_component_taper,0])
                        ResinRod (Resin_Support_Min_Height+z_component+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                        }
                }
                
                hull(){
                    for (x=[-x_min+Resin_Support_Contact_Diameter/2+Resin_Support_EdgeGap, x_max-Resin_Support_Contact_Diameter/2-Resin_Support_EdgeGap]){
                        translate([x, -y_component_taper,0])
                        ResinRod (Resin_Support_Min_Height+z_component+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
                        }
                }
                
                hull(){
                    for (x=[-x_min+Resin_Support_Contact_Diameter/2+Resin_Support_EdgeGap, x_max-Resin_Support_Contact_Diameter/2-Resin_Support_EdgeGap]){
                        translate([x, y_component_taper,0])
                        ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
                        }
                }
                
                hull(){
                    for (x=[-x_min+Resin_Support_Contact_Diameter/2+Resin_Support_EdgeGap, x_max-Resin_Support_Contact_Diameter/2-Resin_Support_EdgeGap]){
                        translate([x, -y_component_taper,0])
                        ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
                        }
                }
                    
                
            }
        }
    }
    //Horizontal Resin Support
    if (Resin_Support==true && Horizontal==true){
    translate([-Shuttle_Arc_Radius*cos(60),0,0])
    rotate([0, 0, -60])
    rotate_extrude(angle=120, $fn=Cylinder_fn)
    difference(){
        polygon([
        [Shuttle_Arc_Radius, -Resin_Support_Cut_Groove_Diameter-Resin_Support_Base_Thickness],//1
                [Shuttle_Arc_Radius, 0],//2
                [Shuttle_Arc_Radius+Shuttle_Thickness, 0],//3
                [Shuttle_Arc_Radius+Shuttle_Thickness, -Resin_Support_Cut_Groove_Diameter],//4
                [Shuttle_Arc_Radius+Shuttle_Thickness+Resin_Support_Base_Thickness, -Resin_Support_Cut_Groove_Diameter],//5
                [Shuttle_Arc_Radius+Shuttle_Thickness,-Resin_Support_Cut_Groove_Diameter-Resin_Support_Base_Thickness],//6
            ]);
            translate([Shuttle_Arc_Radius+Resin_Support_Cut_Groove_Diameter/2+Resin_Support_Cut_Groove_Min_Thickness, -Resin_Support_Cut_Groove_Diameter/2]){
                hull(){
                    circle(d=Resin_Support_Cut_Groove_Diameter, $fn=Cylinder_fn);
                    translate([2, 0, -Resin_Support_Cut_Groove_Diameter/2])
                    circle(d=Resin_Support_Cut_Groove_Diameter, $fn=Cylinder_fn);
                }
            }
        }
    }
}