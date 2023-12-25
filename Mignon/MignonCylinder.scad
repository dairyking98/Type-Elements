//Mignon 2, 3, 4 Type Cylinder
//September 13, 2023
//Leonard Chau


//ADD RESIN SUPPORT
/* [Character Details] */
//As Seen on Legend
/*LAYOUT=["'\"%&(£$);:,.",
          "?PFUGQpfugq¼",
        "!VINABvinab½",
        "_LDETMldetm¾",
        "JKOSRZkosrzj",
        "/YCHWXychwx@",
        "#1234567890-"];
LAYOUT=["&():\"!?'äöü_",
        "§PFUGQpfugq;",
        "JVINABvinabj",
        "/LDETMldetm,",
        "%KOSRZkosrz=",
        "¾YCHWXychwx+",
        "½¼23456789.-"];
*/
TESTING=["HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH",
         "HHHHHHHHHHHH"];

Assert=false;
testing=false;
//Custom Layout
1st_Row="";
2nd_Row="";
3rd_Row="";
4th_Row="";
5th_Row="";
6th_Row="";
7th_Row="";
CUSTOMLAYOUT=[1st_Row,2nd_Row,3rd_Row,4th_Row,5th_Row,6th_Row,7th_Row];
include <MignonIndexLayouts.scad>
CharLegend=[7,8,9,10,11,0,1,2,3,4,5,6];
Layout_Selection=0; //[0:English 2,1:Custom Layout,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]

Layout=testing?TESTING:Layouts[Layout_Selection];
Tallen=false;
//Element Height Increase
Height_Increase=3;

Testing_Offsets=[-.25, -.2, -.15, -.1, -.05, 0, .05, .1, .15, .2, .25, .3];


Typeface_="Iosevka Etoile";//As Installed on PC
Type_Size=2.45;//[1:.05:6]
Debug_No_Minkowski=true;//Speedy Preview and Render with No Minkowski
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-.1:.05:.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.5;

//Label Text
Cylinder_Label="Label";
//Label Size
Cylinder_Label_Size=0.51*Type_Size;
//Label Font
Cylinder_Label_Font=Typeface_;
//Label Height Offset From Chamfer Base
Cylinder_Label_Height_Offset=.5;
//Spacing Between Characters (Degrees)
Cylinder_Label_Spacing=15;
//Label Offset From Pin (Degrees)
Cylinder_Label_Offset=0;

/* [Cylinder Details] */
//Total Cylinder Height
Cylinder_Height_=40.5;
Cylinder_Height= Tallen==true ? Cylinder_Height_+Height_Increase : Cylinder_Height_;
//Main Cylinder Diameter
Cylinder_Diameter=18.64;
//Height Drop From Top
Cylinder_Top_Height_Offset=3;
//Height Drop Chamfer Radius
//Cylinder_Top_Radius=2;
//Height Drop Chamfer Size
Cylinder_Top_Chamfer=2;
//Height Drop Diameter
Cylinder_Top_Diameter=10.5;
//Inner Shaft Diameter
Cylinder_Top_Shaft_Diameter=7.3;
//Inner Mounting Diameter
Cylinder_Bottom_Shaft_Diameter=14.6;
//Max Pin Height
Pin_Height=1.8;
//Max Pin Width
Pin_Width=1.7;
//Max Minimum Diameter Across 2 Concave Characters
Min_Final_Character_Diameter=19.4;
//Platen Diameter
Platen_Diameter=26.5;

/* [Character Placement Details] */
//[1st, 2nd, 3rd, 4th, 5th, 6th, 7th] Baseline Height
Baseline=[2.4, 7.55, 12.7, 17.7, 22.7, 27.7, 32.55];
Baseline_Offset=[0, 0, 0, 0, 0, 0, 0];//GET NEW OFFSETS
Cutout=[3.3, 8.55, 13.7, 18.7, 23.7, 28.7, 33.4];
Cutout_Offset=[0, 0, 0, 0, 0, 0, 0];//GET NEW OFFSETS
echo(Baseline+Baseline_Offset);

echo (Cutout+Cutout_Offset);


/* [Resin Print Support] */
//Generate Print Support?
Generate_Support=true;
//Resin Support Cut Groove Thickness
Resin_Support_Cut_Groove_Thickness=.1;
//Resin Support Height
Resin_Support_Height=4;
//Resin Support Chamfer Size
Resin_Support_Thickness=2;
//Resin Support Cut Groove Diameter
Resin_Support_Cut_Groove_Diameter=.75;
//Resin Support Wire Thickness
Resin_Support_Wire_Thickness=.6;
//Resin Support Contact Point Diameter
Resin_Support_Contact_Point=.2;
Cylinder_fn = $preview ? 360 : 360;
$fn = $preview ? 22 : 44;


module LetterText (SomeElement_Diameter,SomeBaseline,SomeCutout, SomeTypeface_,SomeType_Size,SomeChar,SomeTheta,SomePlaten_Diameter,SomeMin_Final_Character_Diameter,SomeCharacter_Modifieds, SomeCharacter_Modifieds_Offset, SomeDebug, SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj, SomeWeight_Adj_Mode, SomeScale_Multiplier, SomeScale_Multiplier_Text){
    $fn = $preview ? 22 : 44;
    x=search(SomeChar, SomeScale_Multiplier_Text);
    minkowski(){
        difference(){
            translate([cos(SomeTheta)*SomeElement_Diameter/2,sin(SomeTheta)*SomeElement_Diameter/2,SomeBaseline])
            translate([0,0,SomeChar==SomeCharacter_Modifieds ?  SomeCharacter_Modifieds_Offset : 0])
            rotate([90,0,90+SomeTheta])
            mirror([1,0,0])
            linear_extrude(2)
            if (SomeWeight_Adj_Mode==2)
                minkowski(){
                    text(SomeChar,size=x==[] ? SomeType_Size:SomeType_Size*SomeScale_Multiplier,halign="center",valign="baseline",font=SomeTypeface_);
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
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
                    
                
            translate([cos(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),sin(SomeTheta)*(SomePlaten_Diameter/2+SomeMin_Final_Character_Diameter/2),SomeCutout])
            rotate([90,0,SomeTheta])
            cylinder(h=5,d=SomePlaten_Diameter,center=true,$fn=$preview ? 60 : 360);
        }
        if (SomeDebug!=true)
            rotate([0,-90,SomeTheta])
            cylinder(h=1.5,r2=.75,r1=0);
    }
}

 module regular_polygon(order,SomeCylinder_Diameter){
     angles=[ for (i = [0:order-1]) i*(360/order) ];
     coords=[ for (th=angles) [SomeCylinder_Diameter/2*cos(th), SomeCylinder_Diameter/2*sin(th)] ];
     polygon(coords);
 }
//Module Cylinder (SomeCylinder_Height,SomeCylinder_Top_Height_Offset,SomeCylinder_Diameter,SomeCylinder_Top_Radius,SomeCylinder_Top)

if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else
union(){
    translate([0, 0, Cylinder_Height])
    rotate([0, 180, 0])
    difference(){
        union(){ //Place Letters onto Blank Cylinder
            for (row=[0:1:len(Layout)-1]){
                for (n=[0:1:len(Layout[0])-1]){
                    PickedChar=CharLegend[n];
                    theta=-(360/(len(Layout[0]))*n);
                    if (Layout[row][PickedChar] != " "){
                    
                    testingbaseline=testing?Testing_Offsets[PickedChar]:0;
                        testingcutout=testing?Testing_Offsets[PickedChar]:0;
                        char=Layouts[Layout_Selection][row][PickedChar];
                        baseline=Baseline[row]-testingcutout;
                        cutout=Cutout[row]+testingcutout;
                        
                        if (testing==true)
                        echo(char=char,baseline=baseline, cutout=cutout);
                    
                        LetterText(Cylinder_Diameter-1,Baseline[row]+Baseline_Offset[row]-testingbaseline,Cutout[row]+Cutout_Offset[row]+testingcutout,Typeface_,Type_Size,Layout[row][PickedChar],theta,Platen_Diameter,Min_Final_Character_Diameter,Character_Modifieds, Character_Modifieds_Offset, Debug_No_Minkowski, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode, Scale_Multiplier, Scale_Multiplier_Text);
                    }
                    }
                }//Polygonal Shape
            linear_extrude(Cylinder_Height-Cylinder_Top_Height_Offset)
             rotate([0,0,360/24])
            regular_polygon(12,Cylinder_Diameter);
            translate([0,0,Cylinder_Height-Cylinder_Top_Height_Offset-.001]){
            /*hull(){//Element Top
                rotate_extrude($fn=Cylinder_fn){
                    translate([Cylinder_Top_Diameter/2-Cylinder_Top_Radius,0,0])
                    union(){
                        intersection(){
                            circle(r=Cylinder_Top_Radius);
                            translate([0,-Cylinder_Top_Radius])
                            square([Cylinder_Top_Radius,Cylinder_Top_Radius*2]);
                        }
                        translate([0,-Cylinder_Top_Radius*2])
                        square([Cylinder_Top_Radius,Cylinder_Top_Radius*2]);
                        }
                }
            }*/
            //Chamfer Top
            cylinder(d=Cylinder_Top_Diameter, h=Cylinder_Top_Height_Offset+.001, $fn=Cylinder_fn);
            cylinder(d1=Cylinder_Top_Diameter+Cylinder_Top_Chamfer*2, d2=Cylinder_Top_Diameter, h=Cylinder_Top_Chamfer, $fn=Cylinder_fn);
            }
            //Label Top
            for (n=[0:len(Cylinder_Label)-1]){
            rotate([0,0,Cylinder_Label_Spacing*n+Cylinder_Label_Offset-(len(Cylinder_Label)-1)*Cylinder_Label_Spacing/2])
            translate([Cylinder_Top_Diameter/2+Cylinder_Top_Chamfer, 0, Cylinder_Height-Cylinder_Top_Height_Offset])
            rotate([45, 0, 90])
            translate([0, Cylinder_Label_Height_Offset, -.05])
            minkowski(){
            linear_extrude(.09)
            text(text=Cylinder_Label[n], size=Cylinder_Label_Size, font=Cylinder_Label_Font, valign="baseline", halign="center");
            if (Debug_No_Minkowski!=true)
            scale([1,1,3])
            sphere(r=.05);
            }
            }
        }
        translate([0,0,-.001])//Cut Center Shaft Hole
        cylinder(h=Cylinder_Height+2*.001,d=Cylinder_Top_Shaft_Diameter, $fn=Cylinder_fn);
        rotate_extrude($fn=Cylinder_fn){//Hollow Out Cylinder
            polygon([[Cylinder_Bottom_Shaft_Diameter/2,0-.001],
                [Cylinder_Bottom_Shaft_Diameter/2,Cylinder_Height-Cylinder_Top_Height_Offset-4],
                [Cylinder_Top_Shaft_Diameter/2-.001,Cylinder_Height-Cylinder_Top_Height_Offset],
                [0+.001,-.001]]);
        }
        rotate([90,0,90]){
            linear_extrude(){//Cut Pin
                union(){
                    hull(){
                        circle(d=Pin_Width, $fn=Cylinder_fn);
                        translate([0,Pin_Height-Pin_Width/2])
                        circle(d=Pin_Width, $fn=Cylinder_fn);   
                    }
                }
            }
        }
    }
    //RESIN SUPPORT STRUCTURE
    if (Generate_Support==true){
    translate([0,0,-Resin_Support_Height+.001]){
        rotate_extrude(){
                polygon([[Cylinder_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,0], [Cylinder_Top_Shaft_Diameter/2,Resin_Support_Thickness], [Cylinder_Diameter/2+Resin_Support_Thickness,Resin_Support_Thickness]]);
            }
            for (n=[0:1:11]){
                r1=(Cylinder_Diameter+Cylinder_Bottom_Shaft_Diameter)/4-.1;
                theta=360/12*n+360/12;
                translate([r1*cos(theta),r1*sin(theta),1]){
                    cylinder(h=Resin_Support_Height-2+Cylinder_Top_Height_Offset,r=Resin_Support_Wire_Thickness);
                    translate([0,0,Resin_Support_Height-2+Cylinder_Top_Height_Offset])
                    cylinder(h=1, r2=Resin_Support_Contact_Point, r1=Resin_Support_Wire_Thickness);
                }
                r2=(Cylinder_Top_Shaft_Diameter+Cylinder_Top_Diameter)/4;
                translate([r2*cos(theta+360/24),r2*sin(theta+360/24),1]){
                    if (n%2==0){
                        cylinder(h=-2+Resin_Support_Height,r=Resin_Support_Wire_Thickness);
                        translate([0,0,-2+Resin_Support_Height])
                        cylinder(h=1, r2=Resin_Support_Contact_Point, r1=Resin_Support_Wire_Thickness);
                    }
                }
            }
        }
    }
}