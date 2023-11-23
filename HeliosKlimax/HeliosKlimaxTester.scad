GERMAN=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⅟J=,;XY₰ß&%/-_§?Q"];
       
GERMAN_MOD=["wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
       "\"()Z⁄J=,;XY¢ß&%/-_§?Q"];

TESTING=["hhhhhhhhhhhhhhhhhhhhh",
         "hhhhhhhhhhhhhhhhhhhhh",
         "hhhhhhhhhhhhhhhhhhhhh",
         "hhhhhhhhhhhhhhhhhhhhh"];
Cylinder_fn = $preview ? 60 : 360;
$fn = $preview ? 22 : 44;
LAYOUT=TESTING;
//From Top Plane
Baselines=[3.55, 9.55, 15.50, 21.7];
Baseline_Offset=[0, 0, 0, 0];
Baseline=Baselines-Baseline_Offset;
Cutouts=[2.2, 8.2, 14.2, 20.2];
Cutout_Offset=[0, 0, 0, 0];
Cutout=Cutouts-Cutout_Offset;

Element_Height=23.42;
Element_Diameter=27.15;
Element_Shaft_Diameter=3.793;//3.6+.143+.05 shaft+clearanceoffset+clearance  //4.16 scan diameter
Element_Min_Concave=28.19;
Element_SquareHole_Position=8.92;
Element_SquareHole_Width=4.10;
Element_SquareHole_Length=2.88;
Element_SquareHole_SupportHeight=3;
Element_IndicatorHole_Position=10;
Element_IndicatorHole_Diameter=2;
Element_Shell_Thickness=1.5;
Element_Inside_Radius=1;
Element_ClipHeight=3;
Element_ClipDiameter=7;
Element_WireDiameter=.554;
Element_ClipBite=.7;
Element_ClipAngle=180;

Platen_Diameter=30;

Typeface_="Kurinto Type";//"Consolas";
Type_Size=2.7;//2;
Debug_No_Minkowski=true;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.5;

Resin_Support=true;
Resin_Support_Base_Thickness=2;
Resin_Support_Rod_Thickness=.8;
Resin_Support_Min_Height=2;
Resin_Support_Contact_Diameter=.4;
Resin_Support_Cut_Groove_Diameter=.75;
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


module LetterText (SomeElement_Diameter,SomeBaseline,SomeCutout, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomePlaten_Diameter,SomeMin_Final_Character_Diameter,SomeDebug,SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    x=search(SomeChar, SomeScale_Multiplier_Text);
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBaseline])
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
                    
                
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1.5,r2=.75,r1=0);
    }
}
union(){
    difference(){
        union(){
            difference(){
                union(){
                    //Join Cylinder and LetterText
                    for (row=[0:1:3])
                        for (column=[0:1:20]){
                        theta=360/21;
                        /*
                        
                        Testing Stuff for locastan
                        
                        Remove Baseline_Testing=...
                        Remove Cutout_Testing=...
                        Remove "+Cutout_Testing[column]"
                        Remove "-Baseline_Testing[column]"
                        Remove char=..., baseline=..., cutout=..., echo(...
                        
                        Change LAYOUT=GERMAN
                        
                        */
                        Baseline_Testing=[-.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5];
                        Cutout_Testing=[-.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5];
                            LetterText(Element_Diameter-.1,Element_Height-Baseline[row]-Baseline_Testing[column],Element_Height-Cutout[row]+Cutout_Testing[column], Typeface_,Type_Size,LAYOUT[row][column],theta*(column),Platen_Diameter,Element_Min_Concave,Debug_No_Minkowski,Character_Modifieds,Character_Modifieds_Offset, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                            char=GERMAN[row][column];
                            baseline=Baseline[row]-Baseline_Testing[column];
                            cutout=Cutout[row]+Cutout_Testing[column];
                            echo(char=char,baseline=baseline, cutout=cutout);
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
                        translate([x_min, y_min])
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
                
                //Cutting Indicator Hole
                translate([Element_IndicatorHole_Position, 0, Element_Height-Element_Shell_Thickness/2])
                cylinder(h=6, d=Element_IndicatorHole_Diameter, $fn=Cylinder_fn, center=true);
            }
            
            //Adding Alignment Pin Support
            translate([-Element_SquareHole_Position, 0,Element_Shell_Thickness-.01])
            cylinder(h=Element_SquareHole_SupportHeight, d=Element_SquareHole_Width+2);
            
            //Adding Clip Retainer
            translate([0, 0, Element_Height-.01])
            cylinder(h=Element_ClipHeight, d=Element_ClipDiameter, $fn=Cylinder_fn);
        }
            
        //Cutting Alignment Pin Hole
        translate([-Element_SquareHole_Position, 0,Element_Shell_Thickness/2])
        cube([Element_SquareHole_Length, Element_SquareHole_Width, 10], center=true);
        
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
    }
    if (Resin_Support==true){
        difference(){
        
            union(){
                translate([0, 0, -Resin_Support_Min_Height])
                cylinder(d=Element_Diameter, h=Resin_Support_Min_Height+.01, $fn=Cylinder_fn);
                translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness])
                cylinder(h=Resin_Support_Base_Thickness, d1=Element_Diameter+2, d2=2+Element_Diameter+2*Resin_Support_Base_Thickness);
            }
            
            translate([0, 0, -Resin_Support_Min_Height-Resin_Support_Base_Thickness-.01])
            cylinder(d=Element_Diameter-Resin_Support_Cut_Groove_Diameter-Resin_Support_Cut_Groove_Thickness*2, h=Resin_Support_Min_Height+Resin_Support_Base_Thickness+2*.01, $fn=Cylinder_fn);
        
            rotate_extrude($fn=Cylinder_fn){
                translate([Element_Diameter/2, -Resin_Support_Cut_Groove_Diameter/2])
                circle(d=Resin_Support_Cut_Groove_Diameter, $fn=Cylinder_fn);
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
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                    translate([0, middle, 0])
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                }
                if (n%3==0){
                    rotate([0, 0, theta])
                    translate([0, inner, 0])
                    SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                }
                translate([-squareholeinner, 0, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                translate([-Element_SquareHole_Position, Element_SquareHole_Width/2, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                translate([-Element_SquareHole_Position, -Element_SquareHole_Width/2, 0])
                SupportRod(Resin_Support_Rod_Thickness, Resin_Support_Base_Thickness, Resin_Support_Contact_Diameter, Resin_Support_Min_Height+Resin_Support_Base_Thickness);
                
            }
        }
    }
}
