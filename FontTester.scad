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
Series_Size=1;
Series_Font="Century Schoolbook Monospace";
Series_OffsetFromHalfline=.75;
Series_CharacterPosition=".";
Series_AngleSpacing=4;
Series_Depth=.2;

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

translate([10, 10])
for (row=[0:1:2]){
    for (column=[0:1:21]){
    translate([column*7, row*7])
    text(Layout[row][column],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
    }}