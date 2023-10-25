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
//Custom Figures Row - Put \ before "
Custom_Figures="\"#$%_/-¢@;23456789:!^1.&'(0)";
CUSTOM=[Custom_Lowercase,Custom_Uppercase,Custom_Figures];
SELECTIONS=[DHIATENSOR,QWERTY,CUSTOM];
CharLegend=[14,15,16,17,18,19,20,21,22,23,24,25,26,27,0,1,2,3,4,5,6,7,8,9,10,11,12,13];

//Keyboard Layout: 0 - DHIATENSOR, 1 - QWERTY, 2 - USE CUSTOM
Layout_Selection=0;//[0,1,2] 
//Type Size
Type_Size=3.3;//[2:.05:5] Comic Mono 3.1, Bonkersworking 2.6 , Consolas 3.3
Typeface_="Consolas";//exactly as shown installed in PC
Layout=SELECTIONS[Layout_Selection];
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=0;//[0, 1];
/* [Debug] */
//Excludes Draft Angles for Speedy Preview and Render
Debug_No_Minkowski=true;
//Number of Letter Columns Modeled
Columns_Rendered=28;//[2:1:28]
CharRenderLim=Columns_Rendered-1;


/* [Character Positioning - From Top Plane] */
//Lowercase Baseline
Low_Baseline = 3.5;
//Uppercase Baseline
Upp_Baseline = 9.8;
//Figures Baseline
Fig_Baseline = 15.5;
Baselines=[Low_Baseline,Upp_Baseline,Fig_Baseline];


/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.1;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;


/* [Character Platen Cutting] */
//Offset from Lowercase Baseline
Low_Baseline_Offset = 1.2;
//Offset from Uppercase Baseline
Upp_Baseline_Offset = 1.29;
//Offset from Figures Baseline
Fig_Baseline_Offset = 1.4;
//Platen Diameter
Platen_Diameter = 32.258;
BaselineOffsets=[Low_Baseline_Offset,Upp_Baseline_Offset,Fig_Baseline_Offset];
//Final Minimum Character Height Radius
SomeMin_Final_Character_Diameter = 17.49;


/* [Global Variables] */
//Universal Offset - do not change
e=.001;
Preview_Facets = 22;
Render_Facets = 44;
FACETS = $preview ? Preview_Facets : Render_Facets;
FONT_FACETS = FACETS;
$fn = FACETS;


/* [Main Element Details] */
//Faceted Cylinder Multiplier
Element_Facet_Multiplier=10;//[1:1:10]
//Element Radius
Element_Radius = 17;
//Element Height
Element_Height = 16.75;
//Center Shaft Diameter (Undersized for ream/drill)
Shaft_Diameter = 3.277; 
//Radial Position for "Speed Holes"
Cutout_Position_Radius = 11.251;
//"Speed Hole Diameter"
Cutout_Hole_Diameter = 5.568;
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


//Main Element Body
module Cylinder (SomeElement_Radius,SomeElement_Height,SomeClip_Diameter,SomeClip_Height,SomeShaft_Diameter,SomeCutout_Position_Radius,SomeElement_Height,SomeCutout_Hole_Diameter,SomeShell_Thickness,SomeSquare_Slot_Support_Height,SomeSquare_Slot_Support_Radius,SomeElement_Facet_Multiplier){
    difference(){
        $fn = 28*SomeElement_Facet_Multiplier;
        union(){
            difference() {
                difference(){
                    //Create Main Element Body
                    union(){
                        cylinder(r=SomeElement_Radius, h=SomeElement_Height);
                        cylinder(r=SomeClip_Diameter/2,h=SomeElement_Height+SomeClip_Height);
                    }
                    //Subtract Center Shaft
                    translate([0,0,-e]) cylinder(r=SomeShaft_Diameter/2, h=SomeElement_Height+3+2*e); 
                }
                //Subtract Top Holes
                for (n = [0:1:7]){
                    translate([SomeCutout_Position_Radius*cos(45*n),SomeCutout_Position_Radius*sin(45*n),Element_Height/2])
                    cylinder(h=SomeElement_Height/2+e, r=SomeCutout_Hole_Diameter/2);
                }
                //Subtract Bottom Holes
                for (n = [0:1:5]){
                    translate([SomeCutout_Position_Radius*cos(60*n),SomeCutout_Position_Radius*sin(60*n),-e])
                    cylinder(h=SomeElement_Height/2, r=SomeCutout_Hole_Diameter/2);
                }
                //Hollow Out Main Body
                rotate_extrude(){
                    polygon([[SomeClip_Diameter/2,3.6],[SomeClip_Diameter/2,SomeElement_Radius-SomeShell_Thickness],[SomeElement_Radius-SomeShell_Thickness,SomeElement_Height-SomeShell_Thickness],[SomeElement_Radius-SomeShell_Thickness,SomeShell_Thickness],[11.1,SomeShell_Thickness]]);
                }//3.6 and 11.1 for Sphere Clearance Cutout
            }
            //Working on Square Hole:
            //Joining Support Cylinder Around Square Hole
            translate([SomeCutout_Position_Radius,0,+e]){
                cylinder(h=SomeSquare_Slot_Support_Height+SomeShell_Thickness,r=SomeSquare_Slot_Support_Radius);
            }
        }
        //Cutting Square Hole and Countersink
        translate([Cutout_Position_Radius,0,-e]){
            cylinder(h=Positioner_Depth,r=Positioner_Support_Radius);
            cube([Square_Slot_Width, Square_Slot_Width, 10], center=true);
        }
        //Subtract Sphere Clearance on Bottom
        translate([0,0,-25.45+2.5]) sphere(r=25.45);
        //Cut Out Wire Clip
        translate([0,-(Shaft_Diameter/2+Wire_Diameter/2-Wire_Clip_Shaft_Bite),Element_Height+Wire_Diameter/2])
        hull(){
            rotate([0,-90,0])
            cylinder(r=Wire_Diameter/2,h=8,center=true);
            translate([0,-5,.5])
            rotate([0,-90,0])
            cylinder(r=Wire_Diameter/2+.5,h=8,center=true);
        }
    }
}

//Character Processing
module LetterText (SomeCharacterRadius, SomeElement_Height, SomeBaseline, SomeBaselineOffset, SomeTypeface_, SomeType_Size, SomeChar, SomeTheta, SomePlaten_Diameter,SomeMin_Final_Character_Diameter, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset,SomeDebug, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode){
    $fn = $preview ? 12 : 24;
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeCharacterRadius,sin(SomeTheta)*SomeCharacterRadius,SomeElement_Height-SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
            if (SomeWeight_Adj_Mode==1)
                minkowski(){
                    text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1, $fn=44);
                }
            else if (SomeWeight_Adj_Mode==0)
                difference(){
                    text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1, $fn=44);
                    }
                }
                    
                
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout+SomeCutout_Offset])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug != true)
            rotate([0,-90,+SomeTheta])
            cylinder(h=1,r2=.75,r1=0,$fn=6);
    }
}

//Cleanup Shape
module CleanupShape (SomeElement_Radius){
    difference(){
    cylinder(h=5,r=SomeElement_Radius+5);
    cylinder(h=6,r=SomeElement_Radius-5);
    }
}

//Resin Print Support Shape
module ResinPrintSupportShape (SomeResin_Support_Cut_Groove_Thickness, SomeResin_Support_Height, SomeResin_Support_Thickness,SomeElement_Radius,SomeResin_Support_Cut_Groove_Diameter,SomeCutout_Position_Radius){
    $fn=28*Element_Facet_Multiplier;
    rotate([180,0,0]){
        difference(){
            union(){
                difference(){
                    cylinder(h=SomeResin_Support_Height,r=SomeElement_Radius);
                    translate([0,0,-.001])
                    cylinder(h=SomeResin_Support_Height+.002,r=SomeElement_Radius-SomeResin_Support_Cut_Groove_Diameter/2-SomeResin_Support_Cut_Groove_Thickness);
                    rotate_extrude(){
                        translate([SomeElement_Radius,SomeResin_Support_Cut_Groove_Diameter/2])
                        circle(r=SomeResin_Support_Cut_Groove_Diameter/2);
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

difference(){
    union(){//Joining Resin Support
        difference(){//Cleaning up Top and Bottom of Cylinder
            union(){//Union of Cylinder and Letters
                for (row=[0:1:len(Layout)-1]){
                    for (n=[0:1:CharRenderLim]){
                        theta=-(360/len(Layout[0]))*n-360/(len(Layout[0])*2);
                        PickedChar=CharLegend[n];
                        LetterText(CharacterRadius,Element_Height,Baselines[row],BaselineOffsets[row],Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,SomeMin_Final_Character_Diameter,Character_Modifieds,Character_Modifieds_Offset,Debug_No_Minkowski,Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode);//Placing Letters
                    }
                }
                Cylinder(Element_Radius,Element_Height,Clip_Diameter,Clip_Height,Shaft_Diameter,Cutout_Position_Radius,Element_Height,Cutout_Hole_Diameter,Shell_Thickness,Square_Slot_Support_Height,Square_Slot_Support_Radius,Element_Facet_Multiplier);//Placing Main Cylinder Body
            }
        translate([0,0,Element_Height])
        CleanupShape(Element_Radius);//Cleaning Top of Element
        rotate([0,180,0])
        CleanupShape(Element_Radius);//Cleaning Bottom of Element
        }
        if (Generate_Support==true)
        translate([0,0,e])
        ResinPrintSupportShape(Resin_Support_Cut_Groove_Thickness,Resin_Support_Height,Resin_Support_Thickness,Element_Radius,Resin_Support_Cut_Groove_Diameter,Cutout_Position_Radius);//Placing Resin Support
    }
    
}
echo(len(Layout));