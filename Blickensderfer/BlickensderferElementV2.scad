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

//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
DHIATENSOR=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-^_(./'\"!1234567890;?%¢$)@#:"];
QWERTY=["qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
       "\"#$%_/-¢@;23456789:!^1.&'(0)"];
SCANDI=["zxkg.pwfudhiatensorlcmy,bvqj",
            "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
            "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:"];
            
HEBREWENGLISH=["ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "זךכגװפףץצדהעאתןנםשרלסמיטבוקח",
        "-^_(./'\"!1234567890;?%¢$)@#:"];

            hebrew="זךכגװפףץצדהעאתןנםשרלסמיטבוקח";


//Custom Lowercase Row
Custom_Lowercase="zxkg.pwfudhiatensorlcmy,bvqj";
//Custom Uppercase Row
Custom_Uppercase="ZXKG.PWFUDHIATENSORLCMY&BVQJ";
//Custom Figures Row
Custom_Figures="-^_(./'\"!1234567890;?%¢$)@#:";
CUSTOM=[Custom_Lowercase,Custom_Uppercase,Custom_Figures];
SELECTIONS=[DHIATENSOR,QWERTY,CUSTOM,HEBREWENGLISH];
CharLegend=[14,15,16,17,18,19,20,21,22,23,24,25,26,27,0,1,2,3,4,5,6,7,8,9,10,11,12,13];

Layout_Selection=0;//[0:DHIATENSOR,1:QWERTY,2:SCANDI,3:Custom,4:HebrewEnglish] 
//Type Size
Type_Size=3.55;//[1:.05:5]
Typeface_="Courier New";//exactly as shown installed in PC
Layout=SELECTIONS[Layout_Selection];
//Replace figure "." with "*"?
Asterisk=true;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.4;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
/* [Debug] */
//Excludes Draft Angles for Speedy Preview and Render
Debug_No_Minkowski=true;
//Number of Letter Columns Modeled
Columns_Rendered=28;//[2:1:28]
CharRenderLim=Columns_Rendered-1;
Series_Number="499";
Series_Size=1.25;
Series_Font="Century Schoolbook Monospace";
//Baseline Offset of Series Text from Between Two Baselines
Series_OffsetFromHalfline=-.5;
//Lowercase Character to Place Series Text Below
Series_CharacterPosition=".";
//Degress Between Series Numbers
Series_AngleSpacing=4;
//Series Text Depth
Series_Depth=.2;
//Place Between Lowercase and Uppercase? Otherwise, Between Uppercase and Figures
Series_Row=0;//[0:Between lowercase and uppercase, 1:Between uppercase and figures]

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

module 2dText(){
    text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_);
}

module WeightAdjShape(){
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    if (Weight_Adj_Shape==0)
    square([1, 1], center=true);
    if (Weight_Adj_Shape==1)
    circle(r=1, $fn=44);
}

module LetterText (){
    $fn = $preview ? 22 : 44;
    x=search(Char, Scale_Multiplier_Text);
    minkowski(){
        difference(){
            translate([cos(Theta)*CharacterRadius,sin(Theta)*CharacterRadius,Element_Height-Baseline])
            translate([0,0,Char==Character_Modifieds ?  Character_Modifieds_Offset : 0])
            rotate([90,0,90+Theta])
            mirror([1,0,0])
            linear_extrude(2)
            scale([x==[] ? 1: Scale_Multiplier, x==[] ? 1: Scale_Multiplier, 1])
            if (Weight_Adj_Mode==2)
                minkowski(){
                    2dText();
                    WeightAdjShape();
                }
            else if (Weight_Adj_Mode==1)
                difference(){
                    2dText();
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        2dText();
                    }
                    WeightAdjShape();
                    }
                }
            else if (Weight_Adj_Mode==0)
            2dText();
            
            translate([cos(Theta)*(Platen_Diameter/2+Final_Min_Character_Height_Radius),sin(Theta)*(Platen_Diameter/2+Final_Min_Character_Height_Radius),Element_Height-Cutout])
            rotate([90,0,Theta])
            cylinder(h=5,d=Platen_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (Debug != true)
            rotate([0,-90,+Theta])
            cylinder(h=1,r2=.75,r1=0);
    }
}

module ResinPrintSupportShape (Resin_Support_Cut_Groove_Thickness, Resin_Support_Height, Resin_Support_Thickness,Element_Radius,Resin_Support_Cut_Groove_Diameter,Cutout_Position_Radius, _fn){
    rotate([180,0,0]){
        difference(){
            union(){
                difference(){
                    cylinder(h=Resin_Support_Height-.5,r=Element_Radius, $fn=_fn);
                    translate([0,0,-.001])
                    cylinder(h=Resin_Support_Height+.002-.5,r=Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=_fn);
                    rotate_extrude($fn=_fn){
                        translate([Element_Radius,Resin_Support_Cut_Groove_Diameter/2])
                        circle(r=Resin_Support_Cut_Groove_Diameter/2, $fn=_fn);
                    }
                }
                rotate_extrude(){
                    polygon([[Element_Radius,Resin_Support_Height],[Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness,Resin_Support_Height],[Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness,Resin_Support_Height-Resin_Support_Thickness],[Element_Radius+Resin_Support_Thickness,Resin_Support_Height-Resin_Support_Thickness]]);
                }
                for (n=[0:1:5]){
                    translate([Cutout_Position_Radius*cos(60*n-30),Cutout_Position_Radius*sin(60*n-30),0]){
                    sphere(r=.3);
                    cylinder(h=1, r1=.3, r2=.6);
                    translate([0,0,1-.001])
                    cylinder(h=Resin_Support_Height-1,r=.6);
                    translate([0,0,Resin_Support_Height-Resin_Support_Thickness])
                    cylinder(h=Resin_Support_Thickness,r1=Resin_Support_Thickness+.6,r2=1.2);
                    }
                    for (m=[1:1:2]){
                        z=sqrt(25.45^2-(Cutout_Position_Radius*m/3*cos(60*n-30))^2-(Cutout_Position_Radius*m/3*sin(60*n-30))^2)-25.45+2.5;
                        translate([Cutout_Position_Radius*m/3*cos(60*n-30),Cutout_Position_Radius*m/3*sin(60*n-30),-z]){
                        sphere(r=.3);
                        cylinder(h=1, r1=.3, r2=.6);
                        translate([0,0,1-.001])
                        cylinder(h=Resin_Support_Height-1,r=.6);
                        translate([0,0,Resin_Support_Height-Resin_Support_Thickness+z])
                        cylinder(h=Resin_Support_Thickness,r1=Resin_Support_Thickness+.6,r2=1.2);
                        }
                    }
                }
            }
            for (n=[0:1:3]){
                theta=90*n;
                radius=(Element_Radius-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness-Resin_Support_Thickness-.5);
                translate([radius*cos(theta),radius*sin(theta),Resin_Support_Height])
                rotate([0,90,90*n])
                cylinder(h=5,r=1.5);
            }
        }
    }
}