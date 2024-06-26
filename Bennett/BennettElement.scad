//Bennett Type Element
//September 14, 2023
//Leonard Chau

//Assert error message to stop OpenSCAD from freezing upon startup
Assert=true;
testing_baseline=false;
testing_cutout=false;
testing_layout=false;
testing_console=false;
z=.001;
/* [Character Details] */
CharLegend=[12,22,3,11,21,2,10,20,1,9,19,0,8,18,27,17,7,26,16,6,25,15,5,24,14,4,23,13];

//Custom Layout As Seen on Keyboard. Left to Right, Top to Bottom
Lowercase="qweruiopasdftyjkl,zxcvghbnm.";
Uppercase="QWERUIOPASDFTYJKL,ZXCVGHBNM.";
Figs="12347890\"#$%56;?:,£@_(&-)/'.";
CUSTOMLAYOUT=[Lowercase,Uppercase,Figs];
include <BennettLayouts.scad>

TESTING=["HHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHH"];


//Layout Selection
Layout_Selection=0; //[0:English, 1:British, 2:Custom]
Layout=testing_layout?TESTING:LAYOUTS[Layout_Selection];
//Typeface
Typeface_="Compagnon Light";
Type_Size=3.05;//[1:.05:10]
//Speedy Preview and Render with No Minkowski
Debug_No_Minkowski=true;

Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.5;

//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=32.9;
//Platen Diameter
Platen_Diameter=30;
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
//Element Print Orientation
Flip_Orientation=true;
/* [Element Details] */
//Element Diameter
Element_Diameter=31.9;
//Element Height
Element_Height=18.65;
//Shaft Diameter
Shaft_Diameter=3.483;
//Element Positioner Pin Diameter
Element_Positioner_Pin_Diameter=2.564;
//Element Positioner Pin - Radial Position
Element_Positioner_Pin_Radius=4.813;
//Indicator Hole Diameter
Indicator_Diameter=2.2;
//Alignment Pin Hole Diameter
Alignment_Hole_Diameter=2;//1.94 a kiss too tight, bumping to 2.0
//Alignment Hole Depth
Alignment_Hole_Depth=2.4;
//Alignment Hole Chamfer Size
Alignment_Hole_Chamfer=0;//.01
//Speed Hole Diameter
Speed_Hole_Diameter=6.1;
//Speed Hole - Radial Position
Speed_Hole_Radius=10.801;
//Number of Speed Holes
Speed_Hole_Quantity=8;
//Countersink Diameter
Countersink_Diameter=23.4;
//Top Countersink Depth
Top_Countersink_Depth=1.85;
//Bottom Countersink Depth
Bottom_Countersink_Depth=1;//1
//Minimum Cylinder Thickness
Shell_Size=1;
//Radius of Inside Corners
Inside_Radius=.5;

/* [Character Placement Details (Bottom Countersink Depth as Reference)] */
//[Lowercase, Uppercase, Figures] Row Height
Baseline=[14.05,8,1.95];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Row Height Offset
Baseline_Offset=[0,0,0];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Platen Cutout Height
Cutout=[15.5,9.9,3.4];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Platen Cutout Height Offset
Cutout_Offset=[0,0,0];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Alignment Hole Height
Alignment_Hole=[12.29,6.24,0.19];//[-1:.05:1]
//[Lowercase, Uppercase, Figures] Alignment Hole Height Offset
Alignment_Hole_Offset=[0,0,0];//[-1:.05:1]

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

/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;//
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.2;
//Resin Support Height
Resin_Support_Height=6;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;//.001
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=1.2;
Resin_Support_Contact_Point_Diameter=.3;
Resin_Support_Buildplate_Diameter=1.2;
$fn = $preview ? 22 : 44;
Cylinder_fn= $preview ? 120 : 360;

pyramidzoffset=1/cos(atan(2/Countersink_Diameter));

module LetterText (SomeElement_Diameter,SomeBaseline,SomeBaseline_Offset,SomeCutout,SomeCutout_Offset, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomePlaten_Diameter,SomeMin_Final_Character_Diameter,SomeBottom_Countersink_Depth,SomeDebug,SomeCharacter_Modifieds,SomeCharacter_Modifieds_Offset, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    x=search(SomeChar, SomeScale_Multiplier_Text);
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBottom_Countersink_Depth+SomeBaseline+SomeBaseline_Offset])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
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
                        text(SomeChar,size=SomeType_Size,halign="center",valign="baseline",font=SomeTypeface_);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
                    }
                }
            else if (SomeWeight_Adj_Mode==0)
            text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
                    
                
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout+SomeCutout_Offset])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1.5,r2=.75,r1=0);
    }
}

module ResinRod (h,  dr, dc, t,db){

cylinder(h=h-1,d=dr);
translate([0,0,h-1])
cylinder(h=1, d2=dc, d1=dr);
cylinder(h=t,d2=2.4*.5+2*t,d1=2.4);
translate([0, 0, h])
sphere(d=dc);

}


Baseline_Testing=[-.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7];
Cutout_Testing=[-.65, -.6, -.55, -.5, -.45, -.4, -.35, -.3, -.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7];


if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
union(){
    //Flip and Rotate Final Element
    translate([0, 0, Flip_Orientation ?  Element_Height : 0])
    rotate([0, Flip_Orientation ? 180 : 0, 0])
    difference(){
        //Join LetterText and Cylinder
        union(){
            //Create LetterText
            for (row=[0:1:len(Layout)-1]){
                for (n=[0:1:len(Layout[0])-1]){
                    PickedChar=CharLegend[n];
                    theta=-(360/(len(Layout[0]))*n+360/(2*28));
                    if (Layout[row][PickedChar] != " "){
                    
                    testingbaseline=testing_baseline?Baseline_Testing[n]:0;
                    testingcutout=testing_cutout?Cutout_Testing[n]:0;
                    char=ENGLISH[row][n];
                    baseline=Baseline[row]-testingbaseline;
                    cutout=Cutout[row]+testingcutout;
                    if (testing_console==true)
                    echo(char=char,baseline=baseline, cutout=cutout);
                    
                        LetterText(Element_Diameter-1,Baseline[row],Baseline_Offset[row]+testingbaseline,Cutout[row],Cutout_Offset[row]-testingcutout,Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Min_Final_Character_Diameter,Bottom_Countersink_Depth,Debug_No_Minkowski,Character_Modifieds,Character_Modifieds_Offset, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                    }
                }
            }
            //Create Cylinder
            cylinder(h=Element_Height,d=Element_Diameter, $fn=Cylinder_fn);
        }
        //Cut Leftover Minkowski
        translate([0,0,Element_Height])
        cylinder(h=5,d=Element_Diameter, $fn=Cylinder_fn);
        //Cut Center Shaft, Bottom Countersink, Speed Holes, Alignment Pin Holes
        translate([0,0,-.001]){
            //Cut Center Shaft
            cylinder(h=Element_Height+2*.001,d=Shaft_Diameter, $fn=Cylinder_fn);
            //Cut Bottom Countersink
            cylinder(h=Bottom_Countersink_Depth,d=Countersink_Diameter, $fn=Cylinder_fn);
            
            //Pyramid Top of Element
            if (Generate_Support==true)
            translate([0, 0, Element_Height-Top_Countersink_Depth-1])
            cylinder(h=1+.001, d2=Countersink_Diameter, d1=0, $fn=Cylinder_fn);
            //Cut Speed Holes
            for (n=[0:1:7]){
                theta=360/Speed_Hole_Quantity*n+360/(Speed_Hole_Quantity*2);
                translate([Speed_Hole_Radius*cos(theta),Speed_Hole_Radius*sin(theta),0])
                cylinder(h=Element_Height+2*.001,d=Speed_Hole_Diameter, $fn=Cylinder_fn);
            }
            //Cut Alignment Shaft Holes
            for (n=[0:1:1]){
                theta=180*n+90;
                translate([Element_Positioner_Pin_Radius*cos(theta),Element_Positioner_Pin_Radius*sin(theta),0])
                cylinder(h=Element_Height+2*.001,d=Element_Positioner_Pin_Diameter, $fn=Cylinder_fn);
            }
        }
        //Cut Top Countersink
        translate([0,0,Element_Height-Top_Countersink_Depth])
        cylinder(h=Top_Countersink_Depth+.001,d=Countersink_Diameter, $fn=Cylinder_fn);
        //Cut Hollow Space
        rotate_extrude($fn=Cylinder_fn){
            hull(){
            dx=(Element_Diameter/2-Shell_Size-Inside_Radius)-(Shaft_Diameter/2+Shell_Size+Inside_Radius);
                    //Top Right
                    translate([Element_Diameter/2-Shell_Size-Inside_Radius, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth])
                    circle(r=Inside_Radius);
                    //Top Left
                    translate([Element_Diameter/2-Shell_Size-Inside_Radius-dx, Element_Height-Shell_Size-Inside_Radius-Top_Countersink_Depth-dx*(2/Countersink_Diameter)])
                    circle(r=Inside_Radius);
                    //Bottom Left
                    translate([Shaft_Diameter/2+Shell_Size+Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
                    circle(r=Inside_Radius);
                    //Bottom Right
                    translate([Element_Diameter/2-Shell_Size-Inside_Radius, Shell_Size+Inside_Radius+Bottom_Countersink_Depth+.5])
                    circle(r=Inside_Radius);
                    //Bottom
                    translate([(Element_Diameter/2-Shell_Size+Shaft_Diameter/2+Shell_Size)/2, Shell_Size+Inside_Radius+Bottom_Countersink_Depth])
                    circle(r=Inside_Radius);
            }
        }
        //Cut Front Indicator Hole
        translate([Element_Diameter/2-Shell_Size-Indicator_Diameter/2,0,Element_Height-Top_Countersink_Depth-Shell_Size-.001])
        cylinder(h=5,d=Indicator_Diameter, $fn=Cylinder_fn);
        //Cut Alignment Holes
        for (row=[0:1:len(Layout)-1]){
            for (n=[0:1:len(Layout[0])-1]){
                theta=-(360/(len(Layout[0]))*n+360/(2*28));
                translate([(Element_Diameter)/2*cos(theta),(Element_Diameter)/2*sin(theta),Bottom_Countersink_Depth+Alignment_Hole[row]])
                rotate([0,-90,theta]){
                    cylinder(h=Alignment_Hole_Depth-Alignment_Hole_Diameter/2,d=Alignment_Hole_Diameter, $fn=Cylinder_fn);
//                    translate([0,0,-1])
//                    cylinder(h=1,d=Alignment_Hole_Diameter/*+2*Alignment_Hole_Chamfer*/, $fn=Cylinder_fn);
                    hull(){
                    translate([0, 0, Alignment_Hole_Chamfer])
                    cylinder(h=z, d=Alignment_Hole_Diameter, $fn=Cylinder_fn);
                    translate([0, 0, -1])
                    scale([1, (Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer)/Alignment_Hole_Diameter, 1])
                    cylinder(h=1, d=Alignment_Hole_Diameter, $fn=Cylinder_fn);
                    }
//                    %cylinder(h=Alignment_Hole_Chamfer,d1=Alignment_Hole_Diameter+2*Alignment_Hole_Chamfer,d2=Alignment_Hole_Diameter, $fn=Cylinder_fn);
                    }
                translate([((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*cos(theta),((Element_Diameter/2)-Alignment_Hole_Depth+Alignment_Hole_Diameter/2)*sin(theta),Bottom_Countersink_Depth+Alignment_Hole[row]])
                sphere(d=Alignment_Hole_Diameter, $fn=Cylinder_fn);
            }
        }
        //Label Text
        translate([Shaft_Diameter/2+1.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
        rotate([180, 0, 90])
        linear_extrude(2)
        text(text=Shuttle_Label1, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
        translate([-Shaft_Diameter/2-1.25, 0, Bottom_Countersink_Depth+Shuttle_Label_Depth])
        rotate([180, 0, -90])
        linear_extrude(2)
        text(text=Shuttle_Label2, size=Shuttle_Label_Size, font=Shuttle_Label_Font, halign="center", valign="baseline");
    }
    //Generate Support Structure
    if (Generate_Support==true){
        translate([0,0,-Resin_Support_Height+.001]){
            difference(){
                //Create Ring
                translate([0, 0, .5])
                cylinder(d=Element_Diameter, h=Resin_Support_Height-.5, $fn=Cylinder_fn);
                translate([0,0,-.001])
                cylinder(h=Resin_Support_Height+2*.001, r=Element_Diameter/2-Resin_Support_Cut_Groove_Diameter/2-Resin_Support_Cut_Groove_Thickness, $fn=Cylinder_fn);
                //Cut Groove
                rotate_extrude($fn=Cylinder_fn){
                    translate([Element_Diameter/2,Resin_Support_Height-Resin_Support_Cut_Groove_Diameter/2])
                    circle(r=Resin_Support_Cut_Groove_Diameter/2, $fn=Cylinder_fn);
                }
            }
            //Create Chamfer
            rotate_extrude(){
                polygon([[Element_Diameter/2,0], [Element_Diameter/2-Resin_Support_Thickness,0], [Element_Diameter/2-Resin_Support_Thickness,Resin_Support_Thickness], [Element_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
            }
            //Create Outer 2 Rings of 8 Supports
            for (n=[0:1:7]){
                theta=360/8*n;
                translate([(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*cos(theta),(Countersink_Diameter+Resin_Support_Wire_Thickness)/2*sin(theta),0]){
                ResinRod (Resin_Support_Height, Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
//                    cylinder(h=Resin_Support_Height-1,r=Resin_Support_Wire_Thickness);
//                    translate([0,0,Resin_Support_Height-1])
//                    cylinder(h=1, r2=.3, r1=Resin_Support_Wire_Thickness);
//                    cylinder(h=Resin_Support_Thickness,r2=Resin_Support_Thickness,r1=1.2);
                }
                translate([Countersink_Diameter*cos(theta)/3,Countersink_Diameter*sin(theta)/3,0]){
                ResinRod (Resin_Support_Height+pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Countersink_Diameter/3), Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
//                cylinder(h=Resin_Support_Height+Top_Countersink_Depth-1,r=Resin_Support_Wire_Thickness);
//                translate([0,0,Resin_Support_Height+Top_Countersink_Depth-1])
//                cylinder(h=1, r2=.3, r1=Resin_Support_Wire_Thickness);
//                cylinder(h=Resin_Support_Thickness,r2=Resin_Support_Thickness,r1=1.2);
                }
            }
            //Create Inner Ring of 4 Supports
            for (n=[0:1:3]){
                theta=90*n;
                translate([(Shaft_Diameter/2+1)*cos(theta),(Shaft_Diameter/2+1)*sin(theta),0]){
                    ResinRod (Resin_Support_Height+pyramidzoffset+Top_Countersink_Depth-(2/Countersink_Diameter)*(Shaft_Diameter/2+1), Resin_Support_Wire_Thickness, Resin_Support_Contact_Point_Diameter, Resin_Support_Thickness, Resin_Support_Buildplate_Diameter);
//                cylinder(h=Resin_Support_Height+Top_Countersink_Depth-1,r=Resin_Support_Wire_Thickness);
//                translate([0,0,Resin_Support_Height+Top_Countersink_Depth-1])
//                cylinder(h=1, r2=.3, r1=Resin_Support_Wire_Thickness);
//                cylinder(h=Resin_Support_Thickness,r2=Resin_Support_Thickness,r1=1.2);
                }
            }
        }
    }
}