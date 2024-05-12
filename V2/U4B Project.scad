Assert=true;


/* [1. Measure Your Machine] */
//Distance between fully extended blank typebar and platen 
Platen_To_Typebar_Gap=2;
//Shim Thickness
Shim_Thickness=.1016;//.0001 .004" brass shim
//Typebar width
Typebar_Width_=0.93;
Typebar_Width=Typebar_Width_+2*Shim_Thickness;
//Platen diameter
Platen_Diameter=25.4;

/* [2. Measure Your Type Slug] */
//Type slug height
Slug_Height=12.02;//.0001 U4B: 12.02 
//Type slug width 
Slug_Width=2.81;//.0001 U4B: 2.81
//Type slug depth from flat face
Slug_Depth=6;//.0001 U4B:
//Type slug's face thickness
Slug_Face_Thickness_=.57;//.0001 U4B: avg(.49+.65)=.57
Slug_Face_Thickness=Slug_Face_Thickness_-Shim_Thickness;
//Type slug width + minimum character height
Slug_Depth_Max=5.5;
//Minimum character protrustion
Char_Protrusion=.6265;//.0001 U4B: avg(.523+.63)=.6265 /*= Slug_Depth_Max - Slug_Depth;*/
//Distance from bottom of slug to first baseline
Baseline1=1.171;//.0001 U4B: 1.171

/* [3. Scan Slug for Baseline Motion] */
//Distance between first (bottom) character baseline and second (top) character baseline
Baseline_Motion=6.7765;//.0001 U4B: avg(6.807_6.746)=6.7765
//Cutout Baseline Offset
Cutout_Baseline_Offset=1.137;//.0001 U4B: avg(1.166+1.108)=1.137
//Baselines of characters
Baseline=[Baseline1, Baseline1+Baseline_Motion];
//Approximate cutout distances from bottom of slug to first (bottom) character cutout and second (top) character cutout
Approximate_Cutouts=[Baseline1+Cutout_Baseline_Offset, Baseline1+Baseline_Motion+Cutout_Baseline_Offset];



/* [4. Printing Cutout Tester Slugs] */
//Generate tester slug(s)
Indicator_Slug=true;
//Indicator slug first (bottom) character:
IndicatorChar1="h";
//Indicator slug second (top) character:
IndicatorChar2="H";
Indicator_Characters=[IndicatorChar1, IndicatorChar2];
//How many indicator slugs to print (odd number)
Indicator_Slug_Quantity=21;//[3:2:41]
//Cutout interval for testing cutouts
Indicator_Slug_Cutout_Interval=.1;
//Half the number of tester slugs - 1
Max_Half_Quantity=(Indicator_Slug_Quantity-1)/2;
//Range for cutout offsets
Cutout_Offset_Range=[ for (n=[-Max_Half_Quantity:1:Max_Half_Quantity])  n*Indicator_Slug_Cutout_Interval ];

Testing_Cutouts=[for (n=[0:1:Indicator_Slug_Quantity-1]) [Approximate_Cutouts[0]+Cutout_Offset_Range[n], Approximate_Cutouts[1]+Cutout_Offset_Range[n]]];


/* [?. Characters] */
//Pairs of characters, lower/first, top/second
//Layout="qQwWeErRtTyYuUiIoOpPaAsSdDfFgGhHjJkKlLzZxXcCvVbBnNmM..,,\'\"1!2@3#4$5%6^7&8*9(0)[]";

//u4b
Layout="qQwWeErRtTyYuUiIoOpPaAsSdDfFgGhHjJkKlLzZxXcCvVbBnNmM½¼@¢,?../¾2\"3#4$5%6_7&8'9(0)-*";
Slug_Pairs=[for (n=[0:2:len(Layout)-1]) [Layout[n], Layout[n+1]] ];

num_pairs=len(Slug_Pairs);
echo(num_pairs);

Slugs_Per_Row=11;
Slug_Spacing=2;//.1
Cutout=Approximate_Cutouts;

//Ring & cylinder gap
Ring_Cylinder_Gap=0;


//////////////
cyl_fn = 360;
resin_fn=20;
mink_fn=10;
text_fn=44;
z=.001;
Typeface_="Iosevka Fixed Slab";//As Installed on PC
Type_Size=3.10;//[1:.05:6]
Debug_No_Minkowski=true;//Speedy Preview and Render with No Minkowski
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=0;//[-1.5:.05:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//Typeslug Corner Radius
Face_Radius=.2;//[0:.05:1]
//Wing Radius
Wing_Radius=2;//[0:.05:5]
//G - Typeslug Wing Minimum Thickness
//Thickness at Typebar
Tapered_Thickness=2;
Wing_Thickness=(Tapered_Thickness-Typebar_Width)/2;//.5;//[0:.01:3]
//Gamma - Upper Wing Angle
Upper_Wing_Angle=0;//[0:1:90]
//Roh - Lower Wing Angle
Lower_Wing_Angle=0;//[0:1:90]

//Places character on correct baseline
module LetterPlacement(row){
    translate([0, Baseline[row], 0])
    children();
}

//2D text weight adjuster profile/shape
module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=mink_fn);
}

//Creates 2D text
module 2DText(Char){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, (y==[]?0:Character_Modifieds_Offset) /*+ (testing_baseline==true?Testing_Offsets[n]:0)*/, 0])
    mirror([1, 0, 0]){
        if (Weight_Adj_Mode==2)//Additive
            minkowski(){
                text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                WeightAdjShape();
            }
        if (Weight_Adj_Mode==1)//Subtractive
            difference(){
                text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
                    }
                    WeightAdjShape();
                }
            }
        if (Weight_Adj_Mode==0)//No Weight Adjustment
            text(Char,size=x==[] ? Type_Size:Type_Size*Scale_Multiplier,halign="center",valign="baseline",font=Typeface_, $fn=text_fn);
    }
}

module 2DTextTest(Char, fonta, sizea){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, (y==[]?0:Character_Modifieds_Offset) /*+ (testing_baseline==true?Testing_Offsets[n]:0)*/, 0])
    mirror([1, 0, 0]){
        if (Weight_Adj_Mode==2)//Additive
            minkowski(){
                text(Char,size=sizea,halign="center",valign="baseline",font=fonta, $fn=text_fn);
                WeightAdjShape();
            }
        if (Weight_Adj_Mode==1)//Subtractive
            difference(){
                text(Char,size=sizea,halign="center",valign="baseline",font=fonta, $fn=text_fn);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Char,size=sizea,halign="center",valign="baseline",fonta=font, $fn=text_fn);
                    }
                    WeightAdjShape();
                }
            }
        if (Weight_Adj_Mode==0)//No Weight Adjustment
            text(Char,size=sizea,halign="center",valign="baseline",font=fonta, $fn=text_fn);
    }
}

//Creates drafted angle text
module LetterText(Char, row){
    minkowski(){
        difference(){
            translate([0, 0, -z])
            linear_extrude(2)
            2DText(Char);
            translate([0, Cutout[row]-Baseline[row], Platen_Diameter/2+Char_Protrusion])
            rotate([0,90,0])
            cylinder(h=5,d=Platen_Diameter,center=true,$fn=cyl_fn);
        }
        if (Debug_No_Minkowski != true)
            translate([0, 0, -1])
            cylinder(h=2*Char_Protrusion,r2=0,r1=/*.75**/Char_Protrusion, $fn=mink_fn);
    }
    
}

module LetterTextTest(Char, row, font, size){
    minkowski(){
        difference(){
            translate([0, 0, -z])
            linear_extrude(2)
            2DTextTest(Char, font, size);
            translate([0, Cutout[row]-Baseline[row], Platen_Diameter/2+Char_Protrusion])
            rotate([0,90,0])
            cylinder(h=5,d=Platen_Diameter,center=true,$fn=cyl_fn);
        }
        if (Debug_No_Minkowski != true)
            translate([0, 0, -1])
            cylinder(h=2*Char_Protrusion,r2=0,r1=/*.75**/2*Char_Protrusion, $fn=mink_fn);
    }
    
}

//Assembles All Text Together
module DraftedText(n){
    for (row=[0, 1]){
        PickedChars=Slug_Pairs[n];
        Char=PickedChars[row];
        LetterPlacement(row)
        LetterText(Char, row);
    }
}

module DraftedTextTest(pair, font, size){
    for (row=[0, 1]){
        PickedChars=pair;
        Char=PickedChars[row];
        LetterPlacement(row)
        LetterTextTest(Char, row, font, size);
    }
}

module Rectangle(){
    translate([-.3/2, 0, 0])
    //linear_extrude(2)
    cube([.3, Slug_Height, 1]);
}

module CutoutTestSlug(n){
    difference(){
        minkowski(){
            difference(){
                Rectangle();
                for (row=[0, 1]){
                    translate([0, Testing_Cutouts[n][row], Platen_Diameter/2+Char_Protrusion])
                    rotate([0,90,0])
                    cylinder(h=5,d=Platen_Diameter,center=true,$fn=cyl_fn);
                    translate([0, Baseline[row], Char_Protrusion+.1])
                    rotate([0,90,0])
                    cube([.4, .1, 5], center=true);
                    //cylinder(h=5,d=.1,center=true,$fn=cyl_fn);
                    echo(str("n = ", n, ", cutout = ", Testing_Cutouts[n][row], ", baseline = ", Baseline[row], " (row ", str(row), ")"));
                    
                    echo(str( " baseline offset ", Baseline[row]-Testing_Cutouts[n][row], " mm from cutout"));
                    
                    echo(str( " cutout offset ", -Baseline[row]+Testing_Cutouts[n][row], " mm from baseline"));
                }
            }
            if (Debug_No_Minkowski != true)
                translate([0, 0, -1])
                cylinder(h=2*Char_Protrusion,r2=0,r1=.75*Char_Protrusion, $fn=mink_fn);
        }
    }
}

module SlugBody(){
    difference(){
        hull(){
            translate([0, 0, -Slug_Face_Thickness])
            hull(){
            translate([-Slug_Width/2+Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Slug_Face_Thickness, $fn=cyl_fn);
            translate([Slug_Width/2-Face_Radius, Face_Radius, 0])
            cylinder(r=Face_Radius, h=Slug_Face_Thickness, $fn=cyl_fn);
            translate([Slug_Width/2-Face_Radius, Slug_Height-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Slug_Face_Thickness, $fn=cyl_fn);
            translate([-Slug_Width/2+Face_Radius, Slug_Height-Face_Radius, 0])
            cylinder(r=Face_Radius, h=Slug_Face_Thickness, $fn=cyl_fn);
            }
            
            
           {translate([0, (Slug_Depth-Wing_Radius)*sin(Lower_Wing_Angle)+Wing_Radius, -Slug_Depth+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Typebar_Width+2*Wing_Thickness, center=true, $fn=cyl_fn);
            translate([0, Slug_Height-(Slug_Depth-Wing_Radius)*sin(Upper_Wing_Angle)-Wing_Radius, -Slug_Depth+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Typebar_Width+2*Wing_Thickness, center=true, $fn=cyl_fn);}   
        }
    translate([-10, 0])
    cube(20);
    }
    
}

module MinkCleanup(){
    difference(){
        translate([0, Slug_Height/2, -Slug_Depth/2])
        cube([20, 20, 20], center=true);
        hull(){
            translate([0, 0, -Slug_Face_Thickness])
            hull(){
                translate([-Slug_Width/2+Face_Radius, Face_Radius, 0])
                cylinder(r=Face_Radius, h=Slug_Face_Thickness+10, $fn=cyl_fn);
                translate([Slug_Width/2-Face_Radius, Face_Radius, 0])
                cylinder(r=Face_Radius, h=Slug_Face_Thickness+10, $fn=cyl_fn);
                translate([Slug_Width/2-Face_Radius, Slug_Height-Face_Radius, 0])
                cylinder(r=Face_Radius, h=Slug_Face_Thickness+10, $fn=cyl_fn);
                translate([-Slug_Width/2+Face_Radius, Slug_Height-Face_Radius, 0])
                cylinder(r=Face_Radius, h=Slug_Face_Thickness+10, $fn=cyl_fn);
            }
            
            translate([0, (Slug_Depth-Wing_Radius)*sin(Lower_Wing_Angle)+Wing_Radius, -Slug_Depth+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Typebar_Width+2*Wing_Thickness, center=true, $fn=cyl_fn);
            translate([0, Slug_Height-(Slug_Depth-Wing_Radius)*sin(Upper_Wing_Angle)-Wing_Radius, -Slug_Depth+Wing_Radius])
            rotate([0, 90, 0])
            cylinder(r=Wing_Radius, h=Typebar_Width+2*Wing_Thickness, center=true, $fn=cyl_fn);
        }
    }
}

module TypebarSlot(){
    translate([-Typebar_Width/2, Slug_Height/2-20, -Platen_To_Typebar_Gap+Char_Protrusion-10])
    cube([Typebar_Width, 40, 10]);
}

module BlankSlug(){
    difference(){
        SlugBody();
        TypebarSlot();
    }
}

module Slug(n){
    difference(){
        union(){
            BlankSlug();
            DraftedText(n);
        }
        TypebarSlot();
        MinkCleanup();
    }
}

module Slug2(pair){
    difference(){
        union(){
            BlankSlug();
            DraftedTextTest(pair, Typeface_, Type_Size);
        }
        TypebarSlot();
        MinkCleanup();
    }
}

module SlugTest(pair, font, size){
    difference(){
        union(){
            BlankSlug();
            DraftedTextTest(pair, font, size);
        }
        TypebarSlot();
        MinkCleanup();
    }
}

module TesterSlug(n){
    difference(){
        union(){
            BlankSlug();
            CutoutTestSlug(n);
        }
        TypebarSlot();
        MinkCleanup();
        
        if (len(str(n))==1){
        translate([-Slug_Width/2.5, Slug_Height/4, -.3])
        linear_extrude(.4)
        text(text=str(n), size=1);}
        if (len(str(n))==2){
        translate([-Slug_Width/2.5, Slug_Height*3/4, -.3])
        text(text=str(n/10-(n%10)/10), size=1);
        translate([-Slug_Width/2.5, Slug_Height/4, -.3])
        text(text=str(n-(n-(n%10))), size=1);
        }
    }
}

module SlugArray(){
    for (n=[0:1:len(Slug_Pairs)-1]){
        translate([
        n/(len(Slug_Pairs)-1)>.5?n*4-(len(Slug_Pairs)-1)/2*4:n*4, 
        n/(len(Slug_Pairs)-1)>.5?Slug_Height+2:0, 
        0])
        Slug(n);
    }
}

module TesterSlugArray(){
    for (n=[0:1:Indicator_Slug_Quantity-1]){
        translate([
        n/(Indicator_Slug_Quantity-1)>.5?-(Indicator_Slug_Quantity-1)/2*4+n*4:n*4, 
        n/(Indicator_Slug_Quantity-1)>.5?Slug_Height+3:0, 
        0])
        TesterSlug(n);
    }
}

module WJDentalArray1(){
//4x3 slugs, 
//2.5mm spacing
x_cords=[for (n=[0:1:3]) (Slug_Width+2.5)*n];
y_cords=[for (n=[0:1:2]) (Slug_Height+2.5)*n];
TestArray=[["hH", "hH", "hH"], [ "mM", "mM", "mM",], [ "eE", "eE", "eE",], [ "oO", "oO", "oO",]];
Fonts=["Comic Mono", "Century Schoolbook Monospace", "Courier New"];
Sizes=[3, 3.05, 3.05];
for (x=[0:1:3]){
    for (y=[0:1:2])
        translate([x_cords[x], y_cords[y], 0])
        SlugTest(TestArray[x][y], Fonts[y], Sizes[y]);
    }
}
    
module SlugArray2(){
    for (n=[0:1:len(Slug_Pairs)-1]){
    row=n/Slugs_Per_Row-n%Slugs_Per_Row/Slugs_Per_Row;
    translate([n*(Slug_Width+Slug_Spacing)-row*(Slug_Width+Slug_Spacing)*Slugs_Per_Row, row*(Slug_Height+Slug_Spacing)])
        Slug(n);
    }
}

//if (Assert==true)
//{}
//else
color("steelblue") 
//Slug2("hH");

//Slug(1);
//TesterSlug();
SlugArray2();
//WJDentalArray1();
//TesterSlugArray();