//Hammond Type Shuttle Improved
//28 March, 2023
//Leonard Chau

Assert=true;
testing_baseline=false;
testing_cutout=false;
testing_layout=false;
z=.001;
cyl_fn = 360;
resin_fn=20;
mink_fn=10;
text_fn=44;
Testing_Offsets=[-.7, -.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .66, .7, .75];

//IDEAL LAYOUT
Normal_I=["qazwsxedcrfvtgbyhnujmik,ol.p;-",
         "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
         "1\"@2#×3$+4%£5_¢6&*7'^8(°9).0=/"];
         
//UNIVERSAL LAYOUT
Normal_U=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1"];

//MATH LAYOUT
Math_U=["√·p.lo,kimjunhybgtvfrcdexswzaq",
        "∫:P∂LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0>)9<(8|'7*÷6]Γ5[∝4+Δ3×∑2_\"1",
        "―ₙ₀πλ₉ωκ₈φε₇τη₆βγ₅θψ₄ρδ₃ξσ₂ζα₁"];



//ATTIC
Attic=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/»0´)9°(8§'7*&6¢~5†ˆ4\"$3«”2`“1"];

//GLAGOLITIC
Glagolitic=["!?P.LO,KIMJUNHYBGTVFRCDEXSWZAQ",
        "ⰀⰁⰂ.ⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜ",
        "ⰝⰞ0.Ⱏ9ⰠⰡ8ⰢⰣ7ⰤⰥ6ⰦⰧ5ⰨⰩ4ⰪⰫ3ⰬⰭ2Ⱞ:1"];
        
GalChars="ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮ";
GalFont="Noto Sans Glagolitic";
GalFontSize=2;//.1

//FRAKTUR

   

////DVORAK LAYOUT
DVORAK=["zslvnrwtcmhgbdfxiykupje.qo,;a'",
        "ZSLVNRWTCMHGBDFXIYKUPJE.QO?:A\"",
        "/=0!)9°(8^☺7*&6¢_5£%4+$3×#2@-1"];

//BLICKENSDERFER
DHIATENSOR=["r,🯁oyjsmqncbelvtugafkiwxhpzd.☺",
        "R&🯂OYJSMQNCBELVTUGAFKIWXHPZD.☼",
        "0$🯃9¢:8%#7?@6;)5!(4\"_3'^2/-1.☹"];

//Comic Mono
Comic=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9•(8^'7*&6`_5>%4+$3<#2@\"1"];



Layouts=[[0, Normal_U, "Normal Universal"],
        [1, Normal_I, "Normal Ideal"],
        [2, Math_U, "Math Universal", "Math"],
        [3, DVORAK, "Custom DVORAK Layout"],
        [4, DHIATENSOR, "Custom DHIATENSOR Layout"],
        [5, Comic, "Custom Comic Mono Layout"],
        [6, Glagolitic, "Custom Glagolitic Layout"],
        [7, Attic, "Attic Peter Weigel Modified"]
        ];
Layout_Selection=0;//[0:Normal_U, 1:Normal_I, 2:Math, 3:DVORAK, 4:DHIATENSOR, 5:ComicMono, 6:Glagolitic, 7:Attic]
Layout=Layouts[Layout_Selection][1];
IsMath=search(Layouts[Layout_Selection][3], "Math")==undef?0:1;
     
/* [Text Dimensions] */
//Baselines for Lowercase, Uppercase, Figures, and Math FROM BOTTOM RIB PLANE
Baseline=[3.74, -1.21, -5.71, -9.89];//Math ??? step between fig and math measure
Typeface_="Iosevka Fixed Slab";//"Consolas";
Type_Size=3.10;//[1:.05:5]
//Check for Speedy Preview
Debug_No_Minkowski=true;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=-.4;//[-1.5:.05:1.5]
Scale_Multiplier_Text="";
Scale_Multiplier=1.0;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]

/* [Shuttle Dimensions] */
Shuttle_Arc_Radius_ShrinkageMultiplier=1.00;//.001
//Arc Radius of Shuttle
Anvil_OD=73.15;
Shuttle_Arc_Radius=(Anvil_OD/2)*Shuttle_Arc_Radius_ShrinkageMultiplier;//36.52
angle_pitch=(120/32)/Shuttle_Arc_Radius_ShrinkageMultiplier;///120/32;

//Thickness of Shuttle
Shuttle_Thickness=1.36;//.01
//Height of Text Protrusion
Shuttle_Text_Protrusion=.9;
//Height of Shuttle
NormalShuttle_Height=13.6;
Shuttle_Height_Offset=3;

MathShuttle_Height=18.24;
Shuttle_Height=(IsMath==0?NormalShuttle_Height:MathShuttle_Height)+Shuttle_Height_Offset;


//Shuttle_Height=Layout
//Distance From Top of Shuttle to BOTTOM of RIB PLANE
Shuttle_Rib_Plane=6.7+Shuttle_Height_Offset;
//Thickness of Rib
Shuttle_Rib_Thickness=.24;//.01
/*
.2794 is original measurement + .06 printer offset

*/
//Width of Rib from Arc Radius
Shuttle_Rib_Width=2.9;
//Distance from Arc Radius to Square Hole Far Edge
Shuttle_Square_Hole_Offset=6.4;//6.47 is OEM measurement
//Square Hole Width
Shuttle_Square_Hole_Width=2.67;//2.54 OEM measurement + .13 printer offset
//Square Hole Length
Shuttle_Square_Hole_Length=1.60;//.01//1.2
//Square Hole Support Height
Shuttle_Pin_Support_Height=1.5;
Shuttle_Pin_Support_Base_Width=6;
Shuttle_Pin_Support_Base_Length=7.8;//.1
Shuttle_Pin_Support_HeightOffset=1.5;//.1
Shuttle_Pin_Support_Height2=2;//.1

//Support Pin Diameter
Shuttle_Pin_Support_Diameter=4.1;
Shuttle_Pin_Support_Chamfer=.3;
//Square Hole Radius
Shuttle_Square_Hole_Radius=.4;
//Distance From Flat Plane to Center Rib Hump
Shuttle_Rib_Hump_Distance=9;
//Shuttle Rib Circle Radius
Shuttle_Rib_Circle=159;
//Rib Circle Radius to Rib
Shuttle_Rib_Circle_Radius=19;
//Degrees for Shuttle Taper
Shuttle_Taper=2;
//Offset From Arc Radius for Taper
Shuttle_Taper_Step=.5;
//Anvil Inner Diameter
AnvilID=66.0;//.01
anviliroffset=Shuttle_Arc_Radius-Anvil_OD/2;
Anvil_ID=AnvilID+2*anviliroffset;

Groove=false;
Shuttle_Groove_Depth=Shuttle_Thickness/2;
Shuttle_Groove_Nub_Size=Shuttle_Thickness/2;
Shuttle_Groove_Nub_Angle=29;
Groove_RetainingPinDiameter=.54+.15;
Groove_TabWidth=3+.15;
Groove_OpeningOffset=.5;//.1

/* [Shuttle Label] */
//Shuttle Label 1
Shuttle_Label1="Leonard Chau";
//Shuttle Label 2
Shuttle_Label2="2024";
//Shuttle Label Size
Shuttle_Label_Size=1.3;
//Shuttle Label Font
Shuttle_Label_Font="OCR\\-A II";
//Shuttle Label Extrusion Deptth
Shuttle_Label_Depth=.2;

/* [Support Structure] */
//Generate Support?
Resin_Support=true;
//Resin Support Orientation
Resin_Support_Orientation=0;//[0:Vertical, 1:Horizontal]
////Vertical Resin Support Raft Thickness
Resin_Support_Base_Thickness=1.5;
//Vertical Resin Support Rod Thickness
Resin_Support_Rod_Thickness=.9;
//Vertical Minimum Height From Raft
Resin_Support_Min_Height=2;
//Vertical Spacing Between Resin Support Rods
Resin_Support_Spacing=3;
//Vertical Resin Support Connecting Point Diameter
Resin_Support_Contact_Diameter=.4;
//Rib Contact Diameter
Resin_Support_Contact_Diameter_Rib=.2;
//Vertical Resin Support Gap from Part Edges
Resin_Support_EdgeGap=.1;
//Vertical Resin Support Buildplate Radius
Resin_Support_Buildplate_Radius=.8;
//Horizontal Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.5;
//Horizontal Resin Support Cut Groove Minimum Thickness
Resin_Support_Cut_Groove_Min_Thickness=.2;
SupportGrooveThickness=.5;
SupportGrooveR=.5*(Shuttle_Thickness-SupportGrooveThickness);


TipInterference=1.2;//.1



//Taper Variables
taper_inset_x=(Shuttle_Arc_Radius-z)*cos(angle_pitch*16-Shuttle_Taper);
taper_inset_y=(Shuttle_Arc_Radius-z)*sin(angle_pitch*16-Shuttle_Taper);
taper_outset_x=cos(angle_pitch*16+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);
taper_outset_y=sin(angle_pitch*16+z)*(Shuttle_Arc_Radius+Shuttle_Taper_Step);

//Reorientation Variables, Global Variables
z_offset=Shuttle_Arc_Radius*cos(angle_pitch*16);
y_max=Shuttle_Arc_Radius*sin(angle_pitch*16);
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
cp1x=Shuttle_Arc_Radius*cos(thetaa)-2;//limit of resin support
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
 
 module LetterPlacement(row, column, Theta){
    rotate ([0, 0, Theta])
    translate([Shuttle_Arc_Radius+Shuttle_Thickness, 0, rib_bottomz+Baseline[row]])
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
    
    z=search(Char, GalChars);
    textsize=x==[]? 
        z==[]?Type_Size:GalFontSize
        :Type_Size*Scale_Multiplier;
    
    textfont=z==[]?Typeface_:GalFont;
    
    y=search(Char, Character_Modifieds);
    
    
    
    translate([0, (y==[]?0:Character_Modifieds_Offset) + (testing_baseline==true?Testing_Offsets[column]:0), 0])
    mirror([1, 0, 0]){
        if (Weight_Adj_Mode==2)//Additive
            minkowski(){
                text(Char,size=textsize,halign="center",valign="baseline",font=textfont, $fn=text_fn);
                WeightAdjShape();
            }
        if (Weight_Adj_Mode==1)//Subtractive
            difference(){
                text(Char,size=textsize,halign="center",valign="baseline",font=textfont, $fn=text_fn);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Char,size=textsize,halign="center",valign="baseline",font=textfont, $fn=text_fn);
                    }
                    WeightAdjShape();
                }
            }
        if (Weight_Adj_Mode==0)//No Weight Adjustment
            text(Char,size=textsize,halign="center",valign="baseline",font=textfont, $fn=text_fn);
    }
}

//Creates Drafted Angle Text
module LetterText(Char, row, column){
    minkowski(){
        translate([0, 0, -.5])
        linear_extrude(Shuttle_Text_Protrusion+.5)
        2DText(Char, column);
        if (Debug_No_Minkowski != true)
            translate([0, 0, -1])
            cylinder(h=1,r2=0,r1=.75, $fn=mink_fn);
    }
    
}

//Assembles All Text Together
module TextRing(){
    for (row=[0:1:len(Layout)-1]){
        for (column=[0:1:len(Layout[0])-1]){
            //angle_pitch=120/32;
            Theta= column <= 14 ? -angle_pitch*16+angle_pitch/2+angle_pitch*column :  angle_pitch/2+angle_pitch*(column-14);
            Char=testing_layout==false?Layout[row][column]:" ";
            LetterPlacement(row, column, Theta)
            LetterText(Char, row, column);
            echo(char=Layout[row][column], baseline=Baseline[row]+ (testing_baseline==true?Testing_Offsets[column]:0));
        }
    }
}

module ShuttleCylinder(){
    translate([0, 0, -z])
        linear_extrude(Shuttle_Height+2*z)
        //regular_polygon(96, 2*Shuttle_Arc_Radius+2*Shuttle_Thickness);
        circle(r=Shuttle_Arc_Radius+Shuttle_Thickness, $fn=cyl_fn);
                    
}

module AnvilShape(){
    translate([0, 0, -5])
        linear_extrude(Shuttle_Height+10){
            polygon([[Shuttle_Arc_Radius*3*cos(16*angle_pitch), -Shuttle_Arc_Radius*3*sin(16*angle_pitch)],[0, 0],  [Shuttle_Arc_Radius*3*cos(16*angle_pitch), Shuttle_Arc_Radius*3*sin(16*angle_pitch)], [0, 100], [-100, 0], [0, -100]]);
            circle(r=Shuttle_Arc_Radius, $fn=cyl_fn);                
        }
}

module MinkCleanup(){
    //Clean Bottom Minkowski
    rotate([0, 180, 0])
    cylinder(r=Shuttle_Arc_Radius+5, h=5);
    //Clean Top Minkowski
    translate([0, 0, Shuttle_Height])
    cylinder(r=Shuttle_Arc_Radius+5, h=5);
}



module Rib(){
    translate([0, 0, rib_bottomz]){
        linear_extrude(Shuttle_Rib_Thickness){
            difference(){
                union(){
                    difference(){
                        circle(r=Shuttle_Arc_Radius+z, $fn=cyl_fn);
                        circle(r=Shuttle_Arc_Radius-Shuttle_Rib_Width, $fn=cyl_fn);
                        polygon([[0, 0], [Shuttle_Arc_Radius*cos(angle_pitch*16), Shuttle_Arc_Radius*sin(angle_pitch*16)], [Shuttle_Arc_Radius*cos(angle_pitch*16), -Shuttle_Arc_Radius*sin(angle_pitch*16)]]);
                    }
                    
                    //Rib Circle
                    intersection(){
                        translate([Shuttle_Rib_Circle_Offset, 0, 0])
                        circle(r=Shuttle_Rib_Circle, $fn=cyl_fn);
                        circle(r=Shuttle_Arc_Radius, $fn=cyl_fn);
                    }
                    
                    //Add Rib Circle Radius
                    for (n=[-1, 1])
                    difference(){
                        polygon([[yprime, n*xprime], [cp1y, n*cp1x],  [30,n*20],[sqrt(Shuttle_Arc_Radius^2-(n*cp2x)^2),n*cp2x], [cp2y, n*cp2x] ]);
                        translate([yprime, n*xprime, 0])
                    circle(r=Shuttle_Rib_Circle_Radius, $fn=360);
                    }
                }
                
            polygon([[Shuttle_Arc_Radius*cos(angle_pitch*16), -Shuttle_Arc_Radius*sin(angle_pitch*16)],[z_offset, 0],  [Shuttle_Arc_Radius*cos(angle_pitch*16), Shuttle_Arc_Radius*sin(angle_pitch*16)], [0, 100], [-100, 0], [0, -100]]);
            }
        }
    }
}

module Groove(){
    union(){
        translate([0, 0, rib_bottomz])
        difference(){
            union(){
                cylinder(r=Shuttle_Arc_Radius+Shuttle_Groove_Depth, h=Shuttle_Rib_Thickness, $fn=cyl_fn);
                translate([0, -Groove_TabWidth/2, -Groove_OpeningOffset/2])
                cube([50, Groove_TabWidth, Shuttle_Rib_Thickness+Groove_OpeningOffset]);
            }
            for (n=[-2, -1, 1, 2]){
            rotate([0, 0, Shuttle_Groove_Nub_Angle*n])
            translate([Shuttle_Arc_Radius+Shuttle_Groove_Depth, 0, -z])
            cylinder(h=Shuttle_Rib_Thickness+2*z, r=Shuttle_Groove_Nub_Size, $fn=cyl_fn);
            }
        }
        //translate([Shuttle_Arc_Radius+Shuttle_Thickness/2, 0,-50])
        //#cylinder(h=100, d=Groove_RetainingPinDiameter, $fn=cyl_fn);
    }
}

//Groove();

module PinSupportHull(){
    hull(){
        translate([0, -Shuttle_Square_Hole_Width/2, Shuttle_Pin_Support_Height])
        linear_extrude(z)
        RadiusSquare(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width, Shuttle_Square_Hole_Radius, cyl_fn);
        translate([0-Shuttle_Pin_Support_Base_Length/2+Shuttle_Square_Hole_Length/2+Shuttle_Pin_Support_HeightOffset, -Shuttle_Pin_Support_Base_Width/2])
        linear_extrude(z)
        RadiusSquare(Shuttle_Pin_Support_Base_Length, Shuttle_Pin_Support_Base_Width, Shuttle_Square_Hole_Radius, cyl_fn);
    }
}

//PinSupportHull();

module PinSupport(){     
    difference(){
        union(){
            translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset, 0, Shuttle_Height-Shuttle_Rib_Plane-z])
    //    #sphere(r=1);
            PinSupportHull();
        
            translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset, 0, Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness+z])
            
            rotate([180, 0, 0])
            PinSupportHull();
        }
     
     //Inner Anvil ID clearance
        difference(){
        cylinder(h=40, d=Anvil_ID+10, $fn=cyl_fn, center=true);
        cylinder(h=41, r=Anvil_ID/2+.3, $fn=cyl_fn, center=true);
        }
    }
}

module PinSupportHole(){
    translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset, 0, 0])
    translate([0, -Shuttle_Square_Hole_Width/2, -z])
    linear_extrude(Shuttle_Height+z)
    RadiusSquare(Shuttle_Square_Hole_Length, Shuttle_Square_Hole_Width, Shuttle_Square_Hole_Radius, cyl_fn);
}

module PinSupport2(){

    difference(){

    
        union(){
        translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, rib_bottomz+z])
        rotate([180,0,0]){
            cylinder(d=Shuttle_Pin_Support_Diameter, h=Shuttle_Pin_Support_Height2+z-Shuttle_Pin_Support_Chamfer, $fn=cyl_fn);
            translate([0, 0, Shuttle_Pin_Support_Height2-Shuttle_Pin_Support_Chamfer-z])
            cylinder(d1=Shuttle_Pin_Support_Diameter,d2=Shuttle_Pin_Support_Diameter-Shuttle_Pin_Support_Chamfer*2, h=Shuttle_Pin_Support_Chamfer+z, $fn=cyl_fn);
            
            

            //translate([0, 0, -z])
            //cylinder(d=Shuttle_Pin_Support_Diameter, h=Shuttle_Pin_Support_Height2+z-Shuttle_Pin_Support_Chamfer, $fn=cyl_fn);
            //translate([0, 0, Shuttle_Pin_Support_Height2-Shuttle_Pin_Support_Chamfer])
            //cylinder(d2=Shuttle_Pin_Support_Diameter, d1=Shuttle_Pin_Support_Diameter+Shuttle_Pin_Support_Chamfer*2, h=Shuttle_Pin_Support_Chamfer, $fn=cyl_fn);
        
        
        
        }
        
        translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, rib_bottomz+Shuttle_Rib_Thickness-z]){
            cylinder(d=Shuttle_Pin_Support_Diameter, h=Shuttle_Pin_Support_Height2+z-Shuttle_Pin_Support_Chamfer-1, $fn=cyl_fn);
            translate([0, 0, Shuttle_Pin_Support_Height2-Shuttle_Pin_Support_Chamfer-z-1])
            cylinder(d1=Shuttle_Pin_Support_Diameter,d2=Shuttle_Pin_Support_Diameter-Shuttle_Pin_Support_Chamfer*2, h=Shuttle_Pin_Support_Chamfer+z, $fn=cyl_fn);
        
        
        }
        
        }
        
        difference(){
            cylinder(h=20, d=Anvil_ID+10, $fn=cyl_fn, center=true);
            cylinder(h=21, r=Anvil_ID/2+.3, $fn=cyl_fn, center=true);
        }
        
    translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, rib_bottomz+z])
    rotate([180,0,0])
    translate([0, 0, Shuttle_Pin_Support_Height2])//-Shuttle_Square_Hole_Length+z])
    //cylinder(d1=Shuttle_Square_Hole_Length, d2=Shuttle_Pin_Support_Diameter-Shuttle_Pin_Support_Chamfer*2, h=Shuttle_Square_Hole_Length, $fn=cyl_fn);
    sphere(d=Shuttle_Pin_Support_Diameter-Shuttle_Pin_Support_Chamfer*2-.5, $fn=cyl_fn);
    }
    
//    translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, rib_bottomz+Shuttle_Rib_Thickness-z])
//    cylinder(d1=Shuttle_Pin_Support_Diameter, d2=Shuttle_Pin_Support_Diameter-Shuttle_Pin_Support_Chamfer*2, h=Shuttle_Pin_Support_Chamfer+z+1, $fn=cyl_fn);
}

module ShuttleTaper(){
    for (a=[0,1]){
        b=[-z, Shuttle_Height-Shuttle_Rib_Plane];
        c=[rib_bottomz+z+(Groove?2:0), 10];
        d=[-1,1];
        translate([0, 0, b[a]])
        linear_extrude(c[a])
        polygon([[taper_inset_x, taper_inset_y], [taper_outset_x, taper_outset_y], (Shuttle_Arc_Radius-z)*[cos(angle_pitch*16+z), sin(angle_pitch*16+z)]]);
        translate([0, 0, b[a]])
        linear_extrude(c[a])
        polygon([[taper_inset_x, -taper_inset_y], [taper_outset_x, -taper_outset_y], (Shuttle_Arc_Radius-z)*[cos(angle_pitch*16+z), -sin(angle_pitch*16+z)]]);
    }
}

module Label(){
    rotate([0, 0, angle_pitch*.25])
    translate([Shuttle_Arc_Radius+Shuttle_Thickness-Shuttle_Label_Depth, 0, (Shuttle_Height-Shuttle_Height_Offset)/2])
    rotate([0, 90, 0])
    linear_extrude(2)
    text(text=Shuttle_Label1, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
    
    rotate([0, 0, -angle_pitch+angle_pitch*.25])
    translate([Shuttle_Arc_Radius+Shuttle_Thickness-Shuttle_Label_Depth, 0, (Shuttle_Height-Shuttle_Height_Offset)/2])
    rotate([0, 90, 0])
    linear_extrude(2)
    text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
}

module RodTip(){
    cylinder(h=1, r1=Resin_Support_Rod_Thickness/2, r2=Resin_Support_Contact_Diameter/2);
    translate([0, 0, 1])
    sphere(r=Resin_Support_Contact_Diameter/2);
}

xnotmath=[-x_min+Resin_Support_Contact_Diameter/2,-x_min*2/3, -x_min*1/3, x_max*1/3, x_max*2/3, x_max-Resin_Support_Contact_Diameter/2];

xmath=[-x_min+Resin_Support_Contact_Diameter/2,-x_min*2/3, -x_min*1/3, x_max*1/4, x_max*2/4, x_max*3/4, x_max-Resin_Support_Contact_Diameter/2];

xx=IsMath==0?xnotmath:xmath;
xxx=IsMath==0?3:4;

module VertResinSupport2(){
    $fn=resin_fn;
    translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness])
    union(){
        //Under Large Arc
        thetamax=angle_pitch*32*PI/180-2*Shuttle_Taper*PI/180;
        thetaspacing=Resin_Support_Spacing/Shuttle_Arc_Radius;
        for (s=[-1,1]){
        
        
            for (x=xx){
        
                //Under Shuttle Arc Radius
                for (theta=[0:thetaspacing:thetamax/2]){
                    translate([x, 0, -z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness])
                    rotate([theta*180/PI*s, 0, ])
                    translate([0, 0, Shuttle_Arc_Radius-1])
                    RodTip();
                    y=(Shuttle_Arc_Radius-1)*cos(90+theta*180/PI*s);
                    za=(Shuttle_Arc_Radius-1)*sin(90+theta*180/PI*s);
                    ConnectingRod([x, y, za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height], [x, y, Resin_Support_Rod_Thickness], Resin_Support_Rod_Thickness);
                    translate([x, y, 0])
                    ResinRod (Resin_Support_Min_Height, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
                    
                    //at the taper
                    translate([x, 0, -z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness])
                    rotate([thetamax/2*180/PI*s, 0, ])
                    translate([0, 0, Shuttle_Arc_Radius-1])
                    RodTip();
                    y1=(Shuttle_Arc_Radius-1)*cos(90+thetamax/2*180/PI*s);
                    z1=(Shuttle_Arc_Radius-1)*sin(90+thetamax/2*180/PI*s);
                    ConnectingRod([x, y1, z1-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height], [x, y1-.5*-s, Resin_Support_Rod_Thickness], Resin_Support_Rod_Thickness);
                    
                    //Under Shuttle Arc ConRods
                    if (abs(y)<=taper_inset_y-Resin_Support_Spacing)
                    for (n=[0,1]){
                    ConnectingRod(
                        [[-x_min*2/3, x_max*(IsMath==0?2:3)/xxx][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2],
                        [[-(x_min-Resin_Support_Contact_Diameter/2), (x_max-Resin_Support_Contact_Diameter/2)][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2-3],
                    Resin_Support_Rod_Thickness);
                    
                    ConnectingRod(
                        [[-x_min*1/3, x_max*1/xxx][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2],
                        [[-x_min*2/3, x_max*2/xxx][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2-3],
                    Resin_Support_Rod_Thickness);
                    
                    if (IsMath==1){
                    ConnectingRod(
                        [[-x_min*1/3, x_max*2/xxx][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2],
                        [[-x_min*2/3, x_max*3/xxx][n],y,za-z_offset+Resin_Support_Base_Thickness+Resin_Support_Min_Height-2-3],
                    Resin_Support_Rod_Thickness);
                    }
                    
                    }
                //}
            //}
        
            
                //Under Rib Supports
                //for (y=[-(round(30/Resin_Support_Spacing)+1)*Resin_Support_Spacing:Resin_Support_Spacing:(round(30/Resin_Support_Spacing)+1)*Resin_Support_Spacing]){

                    if (Groove==false){
                        //Under Rib - Outer
//                        if (abs(y)>cp1x && abs(y)<=innerarcintercept){
//                            h=sqrt((Shuttle_Arc_Radius-Shuttle_Rib_Width)^2-y^2)-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
//                        translate([0, y,0])
//                            #ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
//                            if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
//                                for (n=[-x_min*1/3,x_max*1/3])
//                                ConnectingRod([0,y,h-1],[n,y,h-4],Resin_Support_Rod_Thickness);
//                            
//                        }
                        
                        //Under Rib - Radius 
                        if (abs(y)<=cp1x && abs(y)>cp2x){
                            h=sqrt(Shuttle_Rib_Circle_Radius^2-(abs(y)-xprime)^2)+yprime-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
                            translate([0, y,0])
                            ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                            if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
                                for (n=[-x_min*1/3,x_max*1/xxx])
                                ConnectingRod([0,y,h-1],[n,y,h-4],Resin_Support_Rod_Thickness);
                                
                        }
                        
//                        //Under Rib - Center
                        if (abs(y)<=cp2x){
                        d=Shuttle_Rib_Circle_Offset-z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness;
                        h=d-(Shuttle_Rib_Circle^2-y^2)^.5+z;
                    translate([0, y,0])
                    ResinRod (h, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
                    if (h-1>=3+Resin_Support_Base_Thickness+Resin_Support_Min_Height)
                        for (n=[-x_min*1/3,x_max*1/xxx])
                            ConnectingRod([0,y,h-1],[n,y,h-4],Resin_Support_Rod_Thickness);
                        }
                        
                    }
                //}
                }
            }
        }
    
//        translate([10, 0, -z_offset+Resin_Support_Min_Height+Resin_Support_Base_Thickness])
//        rotate([-angle_pitch*16, 0, 0])
//        translate([0, 0, Shuttle_Arc_Radius])
//        %sphere(r=1);        
        //Under Rib - Rib Thickness on Edges
        //Associated Variables
        y_component_taper=(Shuttle_Arc_Radius+Shuttle_Taper_Step)*cos(90-angle_pitch*16);
        z_component=(Shuttle_Taper_Step)*sin(90-angle_pitch*16);
        y_component=(Shuttle_Arc_Radius)*cos(90-angle_pitch*16)-.3;
        y_component_inner=y_component-Shuttle_Rib_Width*cos(90-angle_pitch*16)-.2;
            
        //tall part
        if (Groove==false){
            translate([0, -outerarcintercept+Resin_Support_EdgeGap, 0])
            ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
            
            translate([0, -innerarcintercept-Resin_Support_EdgeGap, 0])
            ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, 0, Resin_Support_Buildplate_Radius);
            
            //tall part
            translate([0, outerarcintercept-Resin_Support_EdgeGap, 0])
            ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
            translate([0, innerarcintercept+Resin_Support_EdgeGap, 0])
            ResinRod (Resin_Support_Min_Height+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, 0, Resin_Support_Buildplate_Radius);
        
            //buildplate part
            //hull(){
                //translate([0, -outerarcintercept+Resin_Support_EdgeGap, 0])
                //ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                //translate([0, -innerarcintercept-Resin_Support_EdgeGap, 0])
                //ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
            //}
            
            //buildplate part
            //hull(){
                //translate([0, outerarcintercept-Resin_Support_EdgeGap, 0])
                //ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
                //translate([0, innerarcintercept+Resin_Support_EdgeGap, 0])
                //ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter_Rib/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius); 
            //}
        }
            
            
        //Outer Edge Supports
        for (x=xx){
            translate([x, y_component_taper,0])
            ResinRod (Resin_Support_Min_Height+z_component+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
        }
         
        //??
        for (x=xx){
            translate([x, -y_component_taper,0])
            ResinRod (Resin_Support_Min_Height+z_component+Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, 0, Resin_Support_Buildplate_Radius);
        }
            
        //??
        for (x=xx){
            translate([x, y_component_taper,0])
            ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
        }
            
        //??
        for (x=xx){
            translate([x, -y_component_taper,0])
            ResinRod (Resin_Support_Base_Thickness, Resin_Support_Rod_Thickness/2, Resin_Support_Contact_Diameter/2, Resin_Support_Base_Thickness, Resin_Support_Buildplate_Radius);
        }
        
    }
}

module HorizResinSupport(){
    $fn=resin_fn;
    translate([-Shuttle_Arc_Radius*cos(angle_pitch*16),0,0])
    rotate([0, 0, -angle_pitch*16])
    rotate_extrude(angle=120, $fn=cyl_fn)
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
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=cyl_fn);
                translate([2, 0, -Resin_Support_Cut_Groove_Diameter/2])
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=cyl_fn);
            }
        }
    }
}

module RibAssembled(){
    difference(){
        union(){
            Rib();
            PinSupport();
            //PinSupport2();
        }
        PinSupportHole();
    }
}

module RibbedShuttle(){
    difference(){
        union(){
            difference(){
                union(){
                    TextRing();
                    ShuttleCylinder();
                }
                AnvilShape();
                MinkCleanup();
            }
            RibAssembled();
        }
        ShuttleTaper();
        Label();
    }
}

module ResinChamfer(){
    $fn=cyl_fn;
    cylinder(r1=Anvil_OD/2+SupportGrooveR, r2=Anvil_OD/2, h=SupportGrooveR);
}  

module GroovedShuttle(){
    difference(){
        difference(){
            union(){
                TextRing();
                ShuttleCylinder();
            }
            AnvilShape();
            MinkCleanup();
            Groove();
            ResinChamfer();
        }
        ShuttleTaper();
        Label();
    }
}

//VertResinPrint2();
module VertResinPrint2(){
    union(){
        rotate([0, -90, 0])
        translate([-Shuttle_Arc_Radius*cos(angle_pitch*16), 0, -x_max])
        if (Groove==false)
        RibbedShuttle();
        else
        GroovedShuttle();
        if (Resin_Support==true)
        VertResinSupport2();
    }
}

module HorizResinPrint(){
    union(){
        translate([-Shuttle_Arc_Radius*cos(angle_pitch*16), 0, 0])
        GroovedShuttle();
        translate([-Shuttle_Arc_Radius*cos(angle_pitch*16),0,0])
        rotate([0, 0, -angle_pitch*16])
        rotate_extrude(angle=120, $fn=cyl_fn)
        difference(){
            polygon([
            [Shuttle_Arc_Radius, -Resin_Support_Cut_Groove_Diameter-Resin_Support_Base_Thickness],//1
                    [Shuttle_Arc_Radius, 0],//2
                    [Shuttle_Arc_Radius+Shuttle_Thickness, 0],//3
                    [Shuttle_Arc_Radius+Shuttle_Thickness, -Resin_Support_Cut_Groove_Diameter],//4
                    [Shuttle_Arc_Radius+Shuttle_Thickness+Resin_Support_Base_Thickness, -Resin_Support_Cut_Groove_Diameter],//5
                    [Shuttle_Arc_Radius+Shuttle_Thickness,-Resin_Support_Cut_Groove_Diameter-Resin_Support_Base_Thickness],//6
                ]);
            translate([Shuttle_Arc_Radius+Resin_Support_Cut_Groove_Diameter/2+Resin_Support_Cut_Groove_Min_Thickness, -Resin_Support_Cut_Groove_Diameter/2])
            hull(){
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=cyl_fn);
                translate([2, 0, -Resin_Support_Cut_Groove_Diameter/2])
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=cyl_fn);
            }
        }
    }
}

module ResinRod2(h){
    $fn=resin_fn;
    union(){
        translate([0, 0, -2-Resin_Support_Base_Thickness])
        cylinder(r1=Resin_Support_Buildplate_Radius, r2=Resin_Support_Buildplate_Radius+Resin_Support_Base_Thickness, h=Resin_Support_Base_Thickness);
        translate([0, 0, -Resin_Support_Base_Thickness-2])
        cylinder(d=Resin_Support_Rod_Thickness, h=h+Resin_Support_Base_Thickness-Resin_Support_Contact_Diameter/2+TipInterference);
        translate([0, 0, h-2-Resin_Support_Contact_Diameter/2+TipInterference])
        cylinder(d1=Resin_Support_Rod_Thickness, d2=Resin_Support_Contact_Diameter, h=2);
        translate([0, 0, h-Resin_Support_Contact_Diameter/2+TipInterference])
        sphere(d=Resin_Support_Contact_Diameter);
    }
}

module HorizResinSupport2(){
    $fn=resin_fn;
    translate([-z_offset, 0, 0])
    union(){
        
        
        //Outer Supports
        for (theta=[-60:120/22:60])
        for (x=[Anvil_OD/2+Resin_Support_Contact_Diameter/2, Anvil_OD/2+Shuttle_Thickness-Resin_Support_Contact_Diameter/2])
        if (abs(theta) <59.9|| x ==Anvil_OD/2+Shuttle_Thickness)
        rotate([0, 0, theta])
        translate([x, 0, 0])
        ResinRod2(0);
        
        for (theta=[thetamax/2*180/PI,-thetamax/2*180/PI])
        rotate([0, 0, theta])
        translate([Anvil_OD/2, 0, 0])
        ResinRod2(0);
        
        for (theta=[60,-60])
        rotate([0, 0, theta])
        translate([Anvil_OD/2+Shuttle_Taper_Step, 0, 0])
        ResinRod2(0);
        
        for (s=[-1,1])
        for (y=innerarcintercept)//[innerarcintercept, outerarcintercept])
        translate([z_offset,s*y, 0])
        ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
        
        
        
        
        
        thetamax=angle_pitch*32*PI/180-2*Shuttle_Taper*PI/180;
        thetaspacing=Resin_Support_Spacing/Shuttle_Arc_Radius;
        
        
        for (s=[-1,1])
        for (theta=[0:thetaspacing:thetamax/2]){
        
            y=(Shuttle_Arc_Radius-1)*cos(90+theta*180/PI*s);
            
            //Under Rib - Outer
            if (abs(y)>cp1x && abs(y)<=innerarcintercept){
                x=sqrt((Shuttle_Arc_Radius-Shuttle_Rib_Width)^2-y^2);
            translate([x, y,0])
                ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
            }
            
            //Under Rib - Radius 
            if (abs(y)<=cp1x && abs(y)>cp2x){
                x=sqrt(Shuttle_Rib_Circle_Radius^2-(abs(y)-xprime)^2)+yprime;
                translate([x, y,0])
                ResinRod2 (Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness); 
            }
            
            //Under Rib - Center
            if (abs(y)<=cp2x){
                d=Shuttle_Rib_Circle_Offset;
                x=d-(Shuttle_Rib_Circle^2-y^2)^.5+z;
            translate([x, y,0])
            ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
            }
            
            //under Pinhole
            translate([Shuttle_Arc_Radius-Shuttle_Square_Hole_Offset+Shuttle_Square_Hole_Length/2, 0, 0])
            for (r=[0, 180])
            rotate([0, 0, r]){
                translate([0,-Shuttle_Square_Hole_Width/2-Resin_Support_Contact_Diameter/2, 0])
                ResinRod2 (Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness - (Shuttle_Pin_Support_Height2-1) );
                translate([Shuttle_Square_Hole_Length/2+Resin_Support_Contact_Diameter/2, 0, 0])
                ResinRod2 (Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness - (Shuttle_Pin_Support_Height2-1) );
            }
            
            
            for (theta=[-40:5:40])
            rotate([0, 0, theta])
            translate([Shuttle_Arc_Radius-2.5, 0, 0])
            ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
            
            for (s=[-1,1]){
            for (theta=[5:5:25])
            rotate([0, 0, s*theta])
            translate([Shuttle_Arc_Radius-5, 0, 0])
            ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
            
            
            for (theta=[3:6:15])
            rotate([0, 0, s*theta])
            translate([Shuttle_Arc_Radius-7.5, 0, 0])
            ResinRod2(Shuttle_Height-Shuttle_Rib_Plane-Shuttle_Rib_Thickness);
           
            
            }
        }
    }
}

module HorizResinPrint2(){
    union(){
    translate([-z_offset, 0, 0])
    translate([0, 0, Shuttle_Height])
        rotate([180, 0, 0])
        RibbedShuttle();
        if (Resin_Support==true)
        
        HorizResinSupport2();
        }
    
}

module HorizGroovedResin(){
    thetamax=angle_pitch*32*PI/180-2*Shuttle_Taper*PI/180;
    translate([-z_offset, 0, 0])
    union(){
        GroovedShuttle();
                //Outer Supports
        for (theta=[-60:120/22:60])
        for (x=[Anvil_OD/2+Resin_Support_Contact_Diameter/2, Anvil_OD/2+Shuttle_Thickness-Resin_Support_Contact_Diameter/2])
        if (abs(theta) <59.9|| x ==Anvil_OD/2+Shuttle_Thickness)
        //if (abs(theta)> 1)//remove center
        rotate([0, 0, theta])
        translate([x, 0, 0])
        ResinRod2(0);
        
        for (theta=[thetamax/2*180/PI,-thetamax/2*180/PI])
        rotate([0, 0, theta])
        translate([Anvil_OD/2+Resin_Support_Contact_Diameter/2, 0, 0])
        ResinRod2(0);
        
        for (theta=[60-atan(Resin_Support_Contact_Diameter/Anvil_OD),-60+atan(Resin_Support_Contact_Diameter/Anvil_OD)])//
        for (xxx=[Anvil_OD/2+Shuttle_Taper_Step+Resin_Support_Contact_Diameter/2, Anvil_OD/2+Shuttle_Thickness-Resin_Support_Contact_Diameter/2])
        rotate([0, 0, theta])
        translate([xxx, 0, 0])
        ResinRod2(0);
    }
}

module HorizGroovedResin2(){
    thetamax=angle_pitch*32*PI/180-2*Shuttle_Taper*PI/180;
    translate([-z_offset, 0, 0])
    union(){
        GroovedShuttle();
        difference(){
        rotate([0, 0, -60])
        rotate_extrude(angle=120, $fn=360)
        Resin2Profile();//
        translate([0, 0, -Resin_Support_Min_Height])
        ShuttleTaper();
        }
    }
}

module HorizGroovedResin3(){
    thetamax=angle_pitch*32*PI/180-2*Shuttle_Taper*PI/180;
    translate([-z_offset, 0, 0])
    union(){
        rotate([180, 0, 0])
        translate([0, 0, -Shuttle_Height])
        GroovedShuttle();
        difference(){
        rotate([0, 0, -60])
        rotate_extrude(angle=120, $fn=360)
        Resin2Profile();//
        translate([0, 0, -Resin_Support_Min_Height])
        ShuttleTaper();
        }
    }
}



module Resin2Profile(){
    translate([Anvil_OD/2, 0, 0])
    difference(){
        polygon([[0,0], 
        [Shuttle_Thickness, 0], [Shuttle_Thickness, -Resin_Support_Min_Height], 
        [Shuttle_Thickness/2+Resin_Support_Buildplate_Radius+Resin_Support_Base_Thickness, -Resin_Support_Min_Height], 
        [Shuttle_Thickness/2+Resin_Support_Buildplate_Radius, -Resin_Support_Min_Height-Resin_Support_Base_Thickness], 
        [Shuttle_Thickness/2-Resin_Support_Buildplate_Radius, -Resin_Support_Min_Height-Resin_Support_Base_Thickness], 
        [Shuttle_Thickness/2-Resin_Support_Buildplate_Radius-Resin_Support_Base_Thickness, -Resin_Support_Min_Height], 
        [0, -Resin_Support_Min_Height]]);
        translate([Shuttle_Thickness, -SupportGrooveR, 0])
        circle(r=SupportGrooveR, $fn=resin_fn);
        translate([0, -SupportGrooveR, 0])
        circle(r=SupportGrooveR, $fn=resin_fn);
    }
}

module Resin3Profile(){
    translate([Anvil_OD/2, 0, 0])
    difference(){
        polygon([[0,0], 
        [Shuttle_Thickness, 0], [Shuttle_Thickness, -Resin_Support_Min_Height], 
        [Shuttle_Thickness/2+Resin_Support_Buildplate_Radius+Resin_Support_Base_Thickness, -Resin_Support_Min_Height], 
        [Shuttle_Thickness/2+Resin_Support_Buildplate_Radius, -Resin_Support_Min_Height-Resin_Support_Base_Thickness], 
        [Shuttle_Thickness/2-Resin_Support_Buildplate_Radius, -Resin_Support_Min_Height-Resin_Support_Base_Thickness], 
        [Shuttle_Thickness/2-Resin_Support_Buildplate_Radius-Resin_Support_Base_Thickness, -Resin_Support_Min_Height], 
        [0, -Resin_Support_Min_Height]]);
        
        hull(){
            translate([0, -SupportGrooveR+z, 0])
            circle(r=SupportGrooveR, $fn=resin_fn);
            translate([-SupportGrooveR+Shuttle_Thickness-SupportGrooveThickness, -SupportGrooveR+z, 0])
            circle(r=SupportGrooveR, $fn=resin_fn);
        }
    }
}


module ResinPrint(){
        echo(Resin_Support);
    if (Resin_Support){
        if (Resin_Support_Orientation==0)
        VertResinPrint2();
//        if (Resin_Support_Orientation==1)// && Groove==0)
//        HorizResinPrint2();
        if (Resin_Support_Orientation==1)
        HorizGroovedResin3();
    }
    if (!Resin_Support){
        if (Groove)
        GroovedShuttle();
        if (!Groove)
        RibbedShuttle();
    }
}

//RibAssembled();
//RibbedShuttle();
if (Assert==false)
ResinPrint(); 
//Rib();
//HorizResinPrint2();

//GroovedShuttle();

//HorizGroovedResin();
//difference(){
//VertResinPrint2();
//VertResinPrint2();

//Groove();

//PinSupportHull();
//TextRing();
//RibbedShuttle();
//rotate([90, 0, 0])
//translate([-50, -50, 0])
//cube(100);
//translate([0,1,0])
//rotate([-90, 0, 0])
//translate([-50, -50, 0])
//cube(100);
//}
//PinSupport();
//VertResinSupport();
