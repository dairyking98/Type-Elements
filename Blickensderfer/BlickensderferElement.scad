//Blickensderfer Type Elements
//11 September, 2023
//Leonard Chau

/* [Character Processing] */

/*
       DHIATENSOR DETAILS
         Z X K G | B V Q J    
       . P W F U | L C M Y ,  
       D H I A T | E N S O R  
   zxkg.pwfudhiatensorlcmy,bvqj
   ZXKG.PWFUDHIATENSORLCMY&BVQJ
   -^_(./'"!1234567890;?%¢$)@#:
   
       QWERTY DETAILS
       Q W E R T | Y U I O P  
       A S D F G | H J K L .  
         Z X C V | B N M ,    
   qwertasdfgzxcvbnm,hjkl.yuiop
   QWERTASDFGZXCVBNM?HJKL.YUIOP
   "#$%_/-¢@;23456789:!^1.&'(0)
*/
DHIATENSOR=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-^_(./'\"!1234567890;?%¢$)@#:"];
QWERTY=["qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
       "\"#$%_/-¢@;23456789:!^1.&'(0)"];

//Custom Lowercase Row
Custom_Lowercase="zxkg.pwfudhiatensorlcmy,bvqj";
//Custom Uppercase Row
Custom_Uppercase="ZXKG.PWFUDHIATENSORLCMY&BVQJ";
//Custom Figures Row
Custom_Figures="-^_(./'\"!1234567890;?%¢$)@#:";
CUSTOM=[Custom_Lowercase,Custom_Uppercase,Custom_Figures];
SELECTIONS=[DHIATENSOR,QWERTY,CUSTOM];
CharLegend=[14,15,16,17,18,19,20,21,22,23,24,25,26,27,0,1,2,3,4,5,6,7,8,9,10,11,12,13];

Layout_Selection=0;//[0:DHIATENSOR,1:QWERTY,2:Custom] 
//Type Size
Type_Size=3.55;//[1:.05:5]
Typeface_="Courier New";//exactly as shown installed in PC
Layout=SELECTIONS[Layout_Selection];
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=1;//[-1.5:.05:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.4;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
/* [Debug] */
//Excludes Draft Angles for Speedy Preview and Render
Debug_No_Minkowski=true;
//Number of Letter Columns Modeled
Columns_Rendered=28;//[2:1:28]
CharRenderLim=Columns_Rendered-1;
Series_Number="900";
Series_Size=3;
Series_Font="Century Schoolbook Monospace";

/* [Element Label] */
//Label Font Override
Cylinder_Label_Font_Override="";
//Label Text Override
Cylinder_Label_Override="";
//Label Size
Cylinder_Label_Size=.67*Type_Size;//[1:.05:3]
//Label Font
Cylinder_Label_Font= Cylinder_Label_Font_Override== "" ?  Typeface_ : Cylinder_Label_Font_Override;//"Courier New:style=bold";
Cylinder_Label= Cylinder_Label_Override== "" ? Typeface_ : Cylinder_Label_Override;
//Spacing Between Characters (Degrees)
Cylinder_Label_Spacing=8;
//Label Offset From Pin (Degrees)
Cylinder_Label_Offset=0;

/* [Character Positioning] */
//Distance From Top Plane to Baseline
Baselines=[4, 10.3, 16.1];
//Baseline Offsets
Baseline_Offset=[0, 0, 0];//[-1:.05:1]
//Distance from Top Plane to Cutout
Cutouts=[2.6, 8.86, 14.6];
//Cutout Offsets
Cutout_Offset=[0, 0, 0];//[-1:.05:1]
Baseline=Baselines-Baseline_Offset;
Cutout=Cutouts-Cutout_Offset;


echo("current baselines ", Baseline);
echo("current cutouts ", Cutout);

/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.3;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Platen Diameter
Platen_Diameter = 32.258;
//Final Minimum Character Height Radius
Final_Min_Character_Height_Radius = 17.49;

/* [Global Variables] */
//Universal Offset - do not change
e=.01;
Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 44;

/* [Main Element Details] */
//Faceted Cylinder Multiplier
Element_Facet_Multiplier=10;//[1:1:10]
//Element Radius
Element_Radius = 17;
//Element Height
Element_Height = 16.75;
//Center Shaft Diameter (Undersized for ream/drill)
Shaft_Diameter = 3.277; //3.297 for no drill out
//Radial Position for "Speed Holes"
Cutout_Position_Radius = 11.251;
//"Speed Hole Diameter"
Cutout_Hole_Diameter_Top = 5.568;
Cutout_Hole_Diameter_Bottom=7.3;
//Top Clip Diameter
Clip_Diameter = 7;
//Top Clip Height
Clip_Height = 3;
//Element Shell Thickness
Shell_Thickness = 1.5;
//Wire Clip Diameter
Wire_Diameter = .554;
//Amount of Wire Biting into Shaft
Wire_Clip_Shaft_Bite = .7;
CharacterRadius=Element_Radius-.5;
Inside_Radius=1;


Cylinder_Label_Radius=Element_Radius-2.3;

/* [Square Positioner Details] */
//Countersink Depth
Positioner_Depth = 2;
//Countersink Radius
Positioner_Support_Radius = 2.784;
//Square Slot Width
Square_Slot_Width = 3.937;
//Inside Support Radius
Square_Slot_Support_Radius = 3.65;
//Inside Support Height
Square_Slot_Support_Height = 3;


module LetterText (SomeCharacterRadius, SomeElement_Height, SomeBaseline, SomeCutout, SomeTypeface_, SomeType_Size, SomeChar, SomeTheta, SomePlaten_Diameter,SomeFinal_Min_Character_Height_Radius,SomeDebug, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    
            x=search(SomeChar, SomeScale_Multiplier_Text);
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeCharacterRadius,sin(SomeTheta)*SomeCharacterRadius,SomeElement_Height-SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
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
            
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeFinal_Min_Character_Height_Radius),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeFinal_Min_Character_Height_Radius),SomeElement_Height-SomeCutout])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug != true)
            rotate([0,-90,+SomeTheta])
            cylinder(h=1,r2=.75,r1=0);
    }
}

//Resin Print Support Shape
module ResinPrintSupportShape (SomeResin_Support_Cut_Groove_Thickness, SomeResin_Support_Height, SomeResin_Support_Thickness,SomeElement_Radius,SomeResin_Support_Cut_Groove_Diameter,SomeCutout_Position_Radius, Some_fn){
    rotate([180,0,0]){
        difference(){
            union(){
                difference(){
                    cylinder(h=SomeResin_Support_Height-.5,r=SomeElement_Radius, $fn=Some_fn);
                    translate([0,0,-.001])
                    cylinder(h=SomeResin_Support_Height+.002-.5,r=SomeElement_Radius-SomeResin_Support_Cut_Groove_Diameter/2-SomeResin_Support_Cut_Groove_Thickness, $fn=Some_fn);
                    rotate_extrude($fn=Some_fn){
                        translate([SomeElement_Radius,SomeResin_Support_Cut_Groove_Diameter/2])
                        circle(r=SomeResin_Support_Cut_Groove_Diameter/2, $fn=Some_fn);
                    }
                }
                rotate_extrude(){
                    polygon([[SomeElement_Radius,SomeResin_Support_Height],[SomeElement_Radius-SomeResin_Support_Cut_Groove_Diameter/2-SomeResin_Support_Cut_Groove_Thickness-SomeResin_Support_Thickness,SomeResin_Support_Height],[SomeElement_Radius-SomeResin_Support_Cut_Groove_Diameter/2-SomeResin_Support_Cut_Groove_Thickness-SomeResin_Support_Thickness,SomeResin_Support_Height-SomeResin_Support_Thickness],[SomeElement_Radius+SomeResin_Support_Thickness,SomeResin_Support_Height-SomeResin_Support_Thickness]]);
                }
                for (n=[0:1:5]){
                    translate([SomeCutout_Position_Radius*cos(60*n-30),SomeCutout_Position_Radius*sin(60*n-30),0]){
                    sphere(r=.3);
                    cylinder(h=1, r1=.3, r2=.6);
                    translate([0,0,1-.001])
                    cylinder(h=SomeResin_Support_Height-1,r=.6);
                    translate([0,0,SomeResin_Support_Height-SomeResin_Support_Thickness])
                    cylinder(h=SomeResin_Support_Thickness,r1=SomeResin_Support_Thickness+.6,r2=1.2);
                    }
                    for (m=[1:1:2]){
                        z=sqrt(25.45^2-(SomeCutout_Position_Radius*m/3*cos(60*n-30))^2-(SomeCutout_Position_Radius*m/3*sin(60*n-30))^2)-25.45+2.5;
                        translate([SomeCutout_Position_Radius*m/3*cos(60*n-30),SomeCutout_Position_Radius*m/3*sin(60*n-30),-z]){
                        sphere(r=.3);
                        cylinder(h=1, r1=.3, r2=.6);
                        translate([0,0,1-.001])
                        cylinder(h=SomeResin_Support_Height-1,r=.6);
                        translate([0,0,SomeResin_Support_Height-SomeResin_Support_Thickness+z])
                        cylinder(h=SomeResin_Support_Thickness,r1=SomeResin_Support_Thickness+.6,r2=1.2);
                        }
                    }
                }
            }
            for (n=[0:1:3]){
                theta=90*n;
                radius=(SomeElement_Radius-SomeResin_Support_Cut_Groove_Diameter/2-SomeResin_Support_Cut_Groove_Thickness-SomeResin_Support_Thickness-.5);
                translate([radius*cos(theta),radius*sin(theta),SomeResin_Support_Height])
                rotate([0,90,90*n])
                cylinder(h=5,r=1.5);
            }
        }
    }
}

union(){
difference(){
    //Union of Resin Support, Positioner Support, Label Text
    union(){
        //Cut Hollow, Holes, Shaft, Positioner, Clip
        difference(){
            //Union of Cylinder and Letters
            union(){
                for (row=[0:1:len(Layout)-1]){
                    for (n=[0:1:CharRenderLim]){
                        theta=-(360/len(Layout[0]))*n-360/(len(Layout[0])*2);
                        PickedChar=CharLegend[n];
                        //Place Characters
                        LetterText(CharacterRadius,Element_Height,Baseline[row],Cutout[row],Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Final_Min_Character_Height_Radius,Debug_No_Minkowski,Character_Modifieds,Character_Modifieds_Offset,Horizontal_Weight_Adj,Vertical_Weight_Adj,Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                    }
                }
                //Place Cylinder
                translate([0, 0, -e])
                cylinder(r=Element_Radius, h=Element_Height+Clip_Height+e, $fn=Cylinder_fn);
            }
            //Subtract Minkowski Leftovers and Form Clip Shaft
            translate([0, 0, Element_Height]){
                difference(){
                    cylinder(r=Element_Radius+5, h=5, $fn=Cylinder_fn);
                    translate([0, 0, -e])
                    cylinder(r=Clip_Diameter/2,h=5+2*e, $fn=Cylinder_fn);
                }
            }
            //Subtract Shaft
            translate([0,0,-e])
            cylinder(r=Shaft_Diameter/2, h=Element_Height+Clip_Height+2*e, $fn=Cylinder_fn); 
            //Subtract Top Holes
            for (n = [0:1:7]){
                translate([Cutout_Position_Radius*cos(45*n),Cutout_Position_Radius*sin(45*n),Element_Height/2])
                cylinder(h=Element_Height/2+e, r=Cutout_Hole_Diameter_Top/2, $fn=Cylinder_fn);
            }
            //Subtract Bottom Holes
            for (n = [1:1:5]){
                translate([Cutout_Position_Radius*cos(60*n),Cutout_Position_Radius*sin(60*n),-e])
                cylinder(h=Element_Height/2, r=Cutout_Hole_Diameter_Bottom/2, $fn=Cylinder_fn);
            }
            //Hollow Out Main Body
            rotate_extrude($fn=Cylinder_fn){
                difference(){
                    hull(){
                        translate([(Element_Radius-Shell_Thickness+Shaft_Diameter/2+Shell_Thickness)/2, Element_Height-Shell_Thickness-Inside_Radius])
                        circle(r=Inside_Radius);//1
                        translate([Shaft_Diameter/2+Shell_Thickness+Inside_Radius, Element_Height-Shell_Thickness-Inside_Radius-.5])
                        circle(r=Inside_Radius);//2
                        translate([Element_Radius-Shell_Thickness-Inside_Radius, Element_Height-Shell_Thickness-Inside_Radius-.5])
                        circle(r=Inside_Radius);//3
                        translate([Element_Radius-Shell_Thickness-Inside_Radius, Shell_Thickness+Inside_Radius])
                        circle(r=Inside_Radius);//4
                        translate([(Element_Radius-Shell_Thickness+Shaft_Diameter/2+Shell_Thickness)/2, Shell_Thickness+Inside_Radius])
                        circle(r=Inside_Radius);//5
                        translate([Shaft_Diameter/2+Shell_Thickness+1, Shell_Thickness+1])
                        circle(r=1);//6
                    }
                translate([0, -25.45+2.5])
                circle(r=25.45+Shell_Thickness);
                }
            }
        //Subtract Bottom Minkowski Leftovers
        rotate([0,180,0])
        cylinder(r=Element_Radius+5, h=5);
        //Subtract Wire Clip
        translate([0,-(Shaft_Diameter/2+Wire_Diameter/2-Wire_Clip_Shaft_Bite),Element_Height+Wire_Diameter/2])
        hull(){
            rotate([0,-90,0])
            cylinder(r=Wire_Diameter/2,h=8,center=true, $fn=Cylinder_fn);
            translate([0,-5,.5])
            rotate([0,-90,0])
            cylinder(r=Wire_Diameter/2+.5,h=8,center=true, $fn=Cylinder_fn);
        }
        //Label Text
        for (n=[0:len(Cylinder_Label)-1]){
            rotate([0,0,90-Cylinder_Label_Spacing*n+Cylinder_Label_Offset+(len(Cylinder_Label)-1)*Cylinder_Label_Spacing/2])
            translate([0, Cylinder_Label_Radius, Element_Height-.3])
            linear_extrude(.4)
            text(text=Cylinder_Label[n], size=Cylinder_Label_Size, font=Cylinder_Label_Font, valign="baseline", halign="center");
        }
        //Series Number Text
        translate([0, -Cutout_Position_Radius+Cutout_Hole_Diameter_Top/2+1, Element_Height])
        text(text=Series_Number, size=Series_Size, font=Series_Font, valign="baseline", halign="center");
    }
    //translate([Cutout_Position_Radius,0,Shell_Thickness])
    //minkowski(){
        //cube([Square_Slot_Width, Square_Slot_Width, Square_Slot_Support_Height], center=true);
        //cylinder(r=1, $fn=Cylinder_fn); //This failed in testing
    //Place Positioner Support
    translate([Cutout_Position_Radius,0,Shell_Thickness-e])
    cylinder(h=2*e+Square_Slot_Support_Height,r=Square_Slot_Support_Radius, $fn=Cylinder_fn);
    }
    //Subtract Positioner Hole and Countersink
    translate([Cutout_Position_Radius,0,-e]){
        cylinder(h=Positioner_Depth,r=Positioner_Support_Radius, $fn=Cylinder_fn);
        cube([Square_Slot_Width, Square_Slot_Width, 10], center=true);
    }
    //Subtract Sphere Clearance on Bottom
    translate([0,0,-25.45+2.5])
    sphere(r=25.45, $fn=Cylinder_fn);
    }
    //Placing Resin Support
    if (Generate_Support==true)
        translate([0,0,e])
        ResinPrintSupportShape(Resin_Support_Cut_Groove_Thickness,Resin_Support_Height,Resin_Support_Thickness,Element_Radius,Resin_Support_Cut_Groove_Diameter,Cutout_Position_Radius, Cylinder_fn);
}