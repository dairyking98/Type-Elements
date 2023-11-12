
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

Layout_Selection=0;//[0:DHIATENSOR,1:QWERTY,2:Custom] 
//Type Size
Type_Size=3.3;//[2:.05:5] Comic Mono 3.1, Bonkersworking 2.6 , Consolas 3.3
Typeface_="Consolas";//exactly as shown installed in PC
Layout=SELECTIONS[Layout_Selection];
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=1;//[0:Subtractive, 1:Additive]
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
Baseline=[Low_Baseline,Upp_Baseline,Fig_Baseline];
Baseline_Offset=[0, 0, 0];


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
Cutout=[Low_Baseline_Offset, Upp_Baseline_Offset, Fig_Baseline_Offset];
Cutout_Offset=[0, 0, 0];
//Platen Diameter
Platen_Diameter = 32.258;
BaselineOffsets=[Low_Baseline_Offset,Upp_Baseline_Offset,Fig_Baseline_Offset];
//Final Minimum Character Height Radius
Final_Min_Character_Height_Radius = 17.49;


/* [Global Variables] */
//Universal Offset - do not change
e=.001;
Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 22;

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

module LetterText (SomeCharacterRadius, SomeElement_Height, SomeBaseline, SomeBaselineOffset, SomeCutout_Offset, SomeTypeface_, SomeType_Size, SomeChar, SomeTheta, SomePlaten_Diameter,SomeFinal_Min_Character_Height_Radius,SomeDebug, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode){
    $fn = $preview ? 22 : 44;
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
                    //circle(r=1, $fn=44);
                    square([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj], center=true);
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
                    circle(r=1);
                    }
                }
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeFinal_Min_Character_Height_Radius),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeFinal_Min_Character_Height_Radius),SomeElement_Height-SomeBaseline+SomeBaselineOffset+SomeCutout_Offset])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug != true)
            rotate([0,-90,+SomeTheta])
            cylinder(h=1,r2=.75,r1=0);
    }
}


for (row=[0:1:len(Layout)-1]){
                    for (n=[0:1:CharRenderLim]){
                        theta=-(360/len(Layout[0]))*n-360/(len(Layout[0])*2);
                        PickedChar=CharLegend[n];
                        //SomeCharacterRadius, SomeElement_Height, SomeBaseline, SomeBaselineOffset, SomeCutout_Offset, SomeTypeface_, SomeType_Size, SomeChar, SomeTheta, SomePlaten_Diameter,SomeFinal_Min_Character_Height_Radius,SomeDebug, SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode
                        LetterText(CharacterRadius,Element_Height,Baseline[row],BaselineOffsets[row],Cutout_Offset[row],Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Final_Min_Character_Height_Radius,Debug_No_Minkowski,Character_Modifieds,Character_Modifieds_Offset,Horizontal_Weight_Adj,Vertical_Weight_Adj,Weight_Adj_Mode);//Placing Letters
                        }}
                        
                        