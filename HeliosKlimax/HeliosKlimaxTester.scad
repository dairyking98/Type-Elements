GERMAN=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⅟J=,;XY₰ß&%/-_§?Q"];
       
GERMAN_MOD=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⁄J=,;XY¢ß&%/-_§?Q"];

TESTING=["HHHHHHHHHHHHHHHHHHHHH",
         "HHHHHHHHHHHHHHHHHHHHH",
         "HHHHHHHHHHHHHHHHHHHHH",
         "HHHHHHHHHHHHHHHHHHHHH"];
         
ROTUNDA=["wertuionklpa$dcfghbvm",
         "WERTUIONKLPASDCFGHBVM",
         "'!+züjö.:xyä23456789q",
        "\"()Z⅟J=,;XYÓß&%/-_§?Q"];         

         
Layouts=[GERMAN, GERMAN_MOD, ROTUNDA];
         
Cylinder_fn = $preview ? 60 : 360;
$fn = $preview ? 22 : 44;

//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
testing_console=false;
testing_layout=false;
testing_baseline=false;
testing_cutout=false;
/* [Element Dimensions] */
//From Top Plane
Baselines=[3.55, 9.55, 15.50, 21.7];
//Baselines=[4.15, 9.15, 15.50, 21.7];//after Locastan Test
//Positive - up; Negative - down
Baseline_Offset=[-.1, -.1, -.1, -.1];
Baseline=Baselines-Baseline_Offset;
//From Top Plane
Cutouts=[2.2, 8.2, 14.2, 20.2];//.05
//Positive - up; Negative - down
Cutout_Offset=[0, 0, 0, 0];
Cutout=Cutouts-Cutout_Offset;
//Height of Element
Element_Height=23.42;
//Diameter of Element
Element_Diameter=27.15;
//Diameter of Central Shaft
Element_Shaft_Diameter=3.826;

//3.6 + .143 * 2 + .05 | shaft + offset + clearance  ?????
//4.16 locastan scan diameter

//4.1 locastan caliper diameter
//3.5 rpolt caliper
//4.1 + .326 | shaft + clearance and offset for locastan calipers
//3.5 + .326 richard polt shaft + clearance and offset for rpolt calipers


//Minimum Diameter Across 2 Characters
Element_Min_Concave=28.19;
//Radial Position for Square Hole
Element_SquareHole_Position=8.92;
//Width of Square Hole
Element_SquareHole_Width=4.126;

//4.1 + .326 | locastan caliper + clearance and offset
//3.9 + .326 | rpolt clearance and offset

//Length of Square Hole
Element_SquareHole_Length=3.206;
//Height of Inside Square Hole Support
Element_SquareHole_SupportHeight=3;
//Radial Position for Indicator
Element_IndicatorHole_Position=9.5;
//Diameter of Indicator Hole
Element_IndicatorHole_Diameter=3;//.2
//Thickness of Element
Element_Shell_Thickness=1.5;
//Radius of Inside Corners
Element_Inside_Radius=1;
//Height of Element Clip
Element_ClipHeight=3;
Element_ClipDiameter=Element_Shaft_Diameter+2*Element_Shell_Thickness;
//Diameter of Wire Clip
Element_WireDiameter=.554;
//Amount of Bite into Central Shaft
Element_ClipBite=.7;
//Rotation of Clip Position
Element_ClipAngle=0;
//Enable Speed Holes?
Element_Speedhole=true;
//Diameter of Speed Hole
Element_SpeedholeDiameter=4;
//Number of Speed Holes
Element_SpeedholeCount=4;//[0:2:6]
//Diameter of Platen
Element_Platen_Diameter=30;



/* [Logo Details] */
SVG_Logo=true;
SVG_Scale=.03;//.002


/* [Character Details] */
Layout=0;//[0:German, 1:German Mod, 2:Rotunda]
LAYOUT=testing_layout?TESTING:Layouts[Layout];
Typeface_="Average Mono";//"Consolas";
Type_Size=3;//.1
Debug_No_Minkowski=true;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Individual Character Height Adjustments
Character_Modifieds="";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Character_Modifieds_Font="";
Character_Modifieds_Size=2;//.1
Scale_Multiplier_Text=".";
Scale_Multiplier=1.5;

/* [Element Label] */
Element_Label=true;
Element_Label_Text="Leonard Chau 2024";
Element_Label_Font="Average Mono";
Element_Label_Size=2;
Element_Label_Radius=11.25;
Element_Label_Degree=10;//s=r*deg*pi/180    deg=s*180/(r*pi)   =2.6*180/(Element_Label_Radius*pi()
Element_Label_Depth=.3;//.1
Element_Label_Offset=180;

Element_Label2=true;
Element_Label2_Text="Rotunda";
Element_Label2_Size=Type_Size;
Element_Label2_Radius=11.25;
Element_Label2_Degree=10;
Element_Label2_Offset=180;

/* [Resin Support] */
//Enable Resin Support?
Resin_Support=true;
//Thickness of Raft
Resin_Support_Base_Thickness=2;
//Width of Raft Ring
Resin_Support_Raft_Width=4;
//Thickness of Resin Support Rod
Resin_Support_Rod_Thickness=1;
//Minimum Height of Resin Support
Resin_Support_Min_Height=2;
//Diameter of Resin Support Contact
Resin_Support_Contact_Diameter=.6;
//Diameter of Resin Support Cut Groove
Resin_Support_Cut_Groove_Diameter=.75;
//Thickness of Resin Support Cut Groove
Resin_Support_Cut_Groove_Thickness=.2;

module SupportRod (RodThickness, BaseThickness, ContactDiameter, Height){
    union(){
    cylinder(d1=2, d2=2+BaseThickness, h=BaseThickness);
    cylinder(d=RodThickness, h=Height-1);
    translate([0, 0, Height-1])
    cylinder(d1=RodThickness, d2=ContactDiameter, h=1);
    translate([0, 0, Height])
    sphere(d=ContactDiameter);
    }
}


module LetterText (SomeElement_Diameter,SomeBaseline,SomeCutout, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomeElement_Platen_Diameter,SomeMin_Final_Character_Diameter,SomeDebug,SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    x=search(SomeChar, SomeScale_Multiplier_Text);
    y=search(SomeChar, Character_Modifieds);
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
            if (SomeWeight_Adj_Mode==2)
                minkowski(){
                    text(SomeChar,size=x==[] ? SomeType_Size:Character_Modifieds_Size,halign="center",valign="baseline",font=y==[]?SomeTypeface_:Character_Modifieds_Font);
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    //circle(r=1, $fn=44);
                    square([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj], center=true);
                }
            else if (SomeWeight_Adj_Mode==1)
                difference(){
                    text(SomeChar,size=x==[] ? SomeType_Size:Character_Modifieds_Size,halign="center",valign="baseline",font=y==[]?SomeTypeface_:Character_Modifieds_Font);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(SomeChar,size=x==[] ? SomeType_Size:Character_Modifieds_Size,halign="center",valign="baseline",font=y==[]?SomeTypeface_:Character_Modifieds_Font);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
                    }
                }
            else if (SomeWeight_Adj_Mode==0)
            text(SomeChar,size=x==[] ? SomeType_Size:Character_Modifieds_Size,halign="center",valign="baseline",font=y==[]?SomeTypeface_:Character_Modifieds_Font);
                    
                
            translate([cos(SomeTheta)*(SomeElement_Platen_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomeElement_Platen_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomeElement_Platen_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1.5,r2=.75,r1=0);
    }
}

module RotateText(string, font){
    for (i=[0:1:len(Element_Label_Text)-1]){
        rotate([0, 0, -Element_Label_Degree*i])
        translate([0, Element_Label_Radius, 0])
        text(text=string[i], size=Element_Label_Size, font=font, halign="center", valign="baseline");
    }
}



if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
union(){
    difference(){
        union(){
            difference(){
                union(){
                    //Join Cylinder and LetterText
                    for (row=[0:1:3])
                        for (column=[0:1:20]){
                        theta=360/21;
                        
                        //TESTING FOR LOCASTAN
                        Baseline_Testing=[-.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5];
                        Cutout_Testing=[-.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5];
                        testingbaseline=testing_baseline?Baseline_Testing[column]:0;
                        testingcutout=testing_cutout?Cutout_Testing[column]:0;
                        char=GERMAN[row][column];
                        baseline=Baseline[row]+testingbaseline;
                        cutout=Cutout[row]/*-testingcutout*/;
                        
                        if (testing_console==true)
                        echo(char=char,baseline=baseline, cutout=cutout);
                        
                        //testingbaseline, testingcutout = 0 when testing=false
                        //END TESTING FOR LOCASTAN
                        
                        
                            LetterText(Element_Diameter-.1,Element_Height-Baseline[row]-testingbaseline,Element_Height-Cutout[row]+testingcutout, Typeface_,Type_Size,LAYOUT[row][column],theta*(column),Element_Platen_Diameter,Element_Min_Concave,Debug_No_Minkowski,Character_Modifieds,Character_Modifieds_Offset, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                            
                        }
                        translate([0, 0, -.01])
                        cylinder(h=Element_Height+2*.01, d=Element_Diameter, $fn=Cylinder_fn);
                }
                
                //Hollowing Element
                x_min=Element_Shaft_Diameter/2+Element_Shell_Thickness+Element_Inside_Radius;
                        x_max=Element_Diameter/2-Element_Shell_Thickness-Element_Inside_Radius;
                        y_min=Element_Shell_Thickness+Element_Inside_Radius;
                        y_max=Element_Height-Element_Shell_Thickness-Element_Inside_Radius;
                rotate_extrude($fn=Cylinder_fn){
                    hull(){
                    
                        //Bottom Left
                        translate([x_min, y_min+(-1/(Element_Diameter/2-Element_Shell_Thickness)*x_min+1)])
                        circle(r=Element_Inside_Radius, $fn=Cylinder_fn);
                        //Top Left
                        
                        translate([x_min, y_max-.5])
                        circle(r=Element_Inside_Radius, $fn=Cylinder_fn);
                        //Top Right
                        translate([x_max, y_max-.5])
                        circle(r=Element_Inside_Radius, $fn=Cylinder_fn);
                        //Top
                        translate([(x_min+x_max)/2, y_max])
                        circle(r=Element_Inside_Radius, $fn=Cylinder_fn);
                        //Bottom Right
                        translate([x_max, y_min])
                        circle(r=Element_Inside_Radius, $fn=Cylinder_fn);
                    }
                }
                
                //Cleaning Top and Bottom Minkowski
                translate([0, 0, Element_Height])
                cylinder(d=Element_Diameter+5, h=5);
                rotate([0, 180, 0])
                cylinder(d=Element_Diameter+5, h=5);
                
                //Pyramid-ing Bottom Surface
                rotate_extrude($fn=Cylinder_fn){
                    polygon([[0, -.01], [0, 1], [(Element_Diameter/2-Element_Shell_Thickness)+(Element_Diameter/2-Element_Shell_Thickness)*.01, -.01]]);
                }
//                translate([0, 0, -.01]);
//                cylinder(h=1+.01, d1=Element_Diameter-Element_Shell_Thickness*2, d2=0);
                
                //Cutting Indicator Hole
                translate([Element_IndicatorHole_Position, 0, Element_Height-Element_Shell_Thickness/2])
                cylinder(h=6, d=Element_IndicatorHole_Diameter, $fn=Cylinder_fn, center=true);
            }
            
            //Adding Alignment Pin Support
            translate([-Element_SquareHole_Position, 0,Element_Shell_Thickness-.01])
            cylinder(h=Element_SquareHole_SupportHeight, d=Element_SquareHole_Width+2, $fn=Cylinder_fn);
            
            //Adding Clip Retainer
            translate([0, 0, Element_Height-.01])
            cylinder(h=Element_ClipHeight, d=Element_ClipDiameter, $fn=Cylinder_fn);
        }
            
        //Cutting Alignment Pin Hole
        translate([-Element_SquareHole_Position, 0,Element_Height/2-1.11])//Removed Top Clearance
        cube([Element_SquareHole_Length, Element_SquareHole_Width, Element_Height+2*.01], center=true);
        
        //Cutting Center Shaft Hole
        translate([0, 0, -.01])
        cylinder(h=Element_Height+Element_ClipHeight+2*.01, d=Element_Shaft_Diameter, $fn=Cylinder_fn);
        
        //Cutting Wire Clip
        rotate([0, 0, Element_ClipAngle])
        translate([0, -Element_Shaft_Diameter/2-Element_WireDiameter/2+Element_ClipBite, Element_Height+Element_WireDiameter/2])
        hull(){
                rotate([0,-90,0])
                cylinder(r=Element_WireDiameter/2,h=8,center=true, $fn=Cylinder_fn);
                translate([0,-5,.5])
                rotate([0,-90,0])
                cylinder(r=Element_WireDiameter/2+.5,h=8,center=true, $fn=Cylinder_fn);
        }
        
        //Cutting Top Speed Holes
        if (Element_Speedhole==true){
            for (n=[0:1:Element_SpeedholeCount]){
                
                theta=(n+1)*360/(Element_SpeedholeCount+2);
                if (theta!=180){
                    rotate([0, 0, theta])
                    translate([(Element_Diameter+Element_ClipDiameter)/4, 0, Element_Height/2])
                    cylinder(d=Element_SpeedholeDiameter, h=Element_Height, $fn=Cylinder_fn);
                }
            }
        }
        
        if (Element_Label==true){
            translate([0, 0, Element_Height-Element_Label_Depth])
            rotate([0, 0, Element_Label_Offset])
            rotate([0, 0, 90+(len(Element_Label_Text)-1)*Element_Label_Degree/2])
            linear_extrude(Element_Label_Depth+.01)
            RotateText(Element_Label_Text, Element_Label_Font);
        }
        
        if (Element_Label2==true){
            translate([0, 0, Element_Height-Element_Label_Depth])
            rotate([0, 0, Element_Label2_Offset])
            rotate([0, 0, 90+(len(Element_Label2_Text)-1)*Element_Label2_Degree/2])
            linear_extrude(Element_Label_Depth+.01)
            RotateText(Element_Label2_Text, Typeface_);
        }
        
        if (SVG_Logo==true){
            translate([-6.25, 0, Element_Height-Element_Label_Depth])
            rotate([0, 0, 90])
            //rotate([0, 0, 90+(len(Element_Label_Text)-1)*Element_Label_Degree/2])
            linear_extrude(Element_Label_Depth+.01)
            scale([SVG_Scale, SVG_Scale])
import("helios-klimax.svg", center=true);
        }
        //Cross Section
//        rotate([0, 90, 0])
//        translate([-50, -50, 0])
//        cube([100, 100, 100]);
        
    }
    
    
    if (Resin_Support==true){
        difference(){
        
            union(){
                //Ring Body
                translate([0, 0, -Resin_Support_Min_Height])
                cylinder(d=Element_Diameter, h=Resin_Support_Min_Height+.01, $fn=Cylinder_fn);
                //Ring Chamfer
                translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness])
                cylinder(h=Resin_Support_Base_Thickness, d1=Element_Diameter+Resin_Support_Raft_Width, d2=Resin_Support_Raft_Width+Element_Diameter+2*Resin_Support_Base_Thickness);
            }
            
            translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness-.01])
            cylinder(d=Element_Diameter-Resin_Support_Cut_Groove_Diameter-Resin_Support_Cut_Groove_Thickness*2, h=Resin_Support_Min_Height+Resin_Support_Base_Thickness+2*.01, $fn=Cylinder_fn);
        
            rotate_extrude($fn=Cylinder_fn){
                translate([Element_Diameter/2, -Resin_Support_Cut_Groove_Diameter/2])
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=Cylinder_fn);
            }
            
            //Drainage Holes
            for (n=[0:1:3]){
                rotate([0, 0, 90*n])
                translate([Element_Diameter/2, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness])
                rotate([0, 90, 0])
                cylinder(r=1.5, h=10, center=true);
            }
        }
        translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness]){
            for (n=[0:1:11]){
                theta=360/12*n;
                //SupportRod (RodThickness, BaseThickness, ContactDiameter, Height)
                outer=Element_SquareHole_Position+1/2*Element_SquareHole_Length+Resin_Support_Contact_Diameter/2;
                inner=Element_Shaft_Diameter/2+Resin_Support_Contact_Diameter/2;
                middle=(outer+inner)/2;
                squareholeinner=Element_SquareHole_Position-1/2*Element_SquareHole_Length-Resin_Support_Contact_Diameter/2;
                rotate([0, 0, theta]){
                    translate([0, outer, 0])
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*outer+1));
                    translate([0, middle, 0])
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*middle+1));
                }
                if (n%3==0){
                    rotate([0, 0, theta])
                    translate([0, inner, 0])
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*inner+1));
                }
                translate([-squareholeinner, 0, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*squareholeinner+1));
                translate([-Element_SquareHole_Position, Element_SquareHole_Width/2+Resin_Support_Contact_Diameter/2, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*sqrt(Element_SquareHole_Position^2+(Element_SquareHole_Width/2+Resin_Support_Contact_Diameter/2)^2)+1));
                translate([-Element_SquareHole_Position, -Element_SquareHole_Width/2-Resin_Support_Contact_Diameter/2, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness+(-1/(Element_Diameter/2-Element_Shell_Thickness)*sqrt(Element_SquareHole_Position^2+(Element_SquareHole_Width/2+Resin_Support_Contact_Diameter/2)^2)+1));
                
            }
        }
    }
}
