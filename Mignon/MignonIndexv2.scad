//Assert error message to stop OpenSCAD from freezing upon startup
Assert=false;
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
//Layout Selection
Layout_Selection=0; //[0:Custom Layout,1:English 2,2:English 3,3:English 4,4:German 2,5:German 4,6:German-French,7:German Fraktur - Gothic,8:German Fraktur - Prof. Stiehl,9:Bohemian 3,10:Bulgarian,11:Cyrillic,12:Danish 2,13:Danish 3,14:Esperanto,15:French 3,16:Georgian,17:Greek (new ortography),18:Dutch 2,19:Italian 3,20:Croatian-Slovenian,21:Latvian,22:Lithuanian,23:Polish 2,24:Portuguese 2,25:Romanian 1,26:Russian (new ortography),27:Russian 3,28:Spanish-American,29:International Script,30:Swedish 2,31:Ukrainian,32:Hungarian 2]
Layout=Layouts[Layout_Selection];
//Index Length
Length=133;//.1
//Index Width
Width=83;//.1
//Fill in Circles on Left
Left_Side_Circle_Fill=true;
//Fill in Background on Right
Right_Side_Background_Fill=true;
//Fill in Background on Left
Left_Side_Background_Fill=false;
//Fill in Circles on Right
Right_Side_Circle_Fill=false;
//Circle Diameter
Circle_Diameter=8;
//Circle Height Offset
Circle_Height_Bump=.8;
//Line Thickness
Line_Width=.3;
//Index Corner Radius
Corner_Radius=9;//.5
//Edge of Index to Column Center
Edge_to_Column=10.5;
//Edge of Index to Row Center
Edge_to_Row=9.5;
//Square Hole Size
Square_Pattern_Size=.5;
//Square Hole Pitch
Square_Pattern_Pitch=.8;
//Apply Checker Border? (slow - do last)
Checker=false;
//Font Name
Typeface_="Consolas";
//Font Size
Type_Size=5;//Type Size
//Horizontal Weight Adjustment
Horizontal_Weight_Adj=.001;//[.001:.001:1]
//Vertical Weight Adjustment
Vertical_Weight_Adj=.001;//[.001:.001:1]
//Weight Adjustment Mode
Weight_Adj_Mode=1;//[0:Subtractive, 1:Additive];
//Weight Adjustment Shape
Weight_Adj_Shape=0;//[0:Circle, 1:Square]
//Individual Character Height Adjustments
Character_Modifieds="_pgqjy()fbldtkh";
//Circle Center to Text Baseline Height
Height_Offset=2.1;
//Underscore Height Offset
Underscore_Offset=1;
//Descenders Height Offset
Descenders_Offset=.4;
//Parentheses Height Offset
Parentheses_Offset=.4;
//Ascenders Height Offset
Ascenders_Offset=-.5;
Character_Modifieds_Offset=[Underscore_Offset,Descenders_Offset,Descenders_Offset,Descenders_Offset,Descenders_Offset,Descenders_Offset,Parentheses_Offset,Parentheses_Offset, Ascenders_Offset, Ascenders_Offset, Ascenders_Offset, Ascenders_Offset, Ascenders_Offset, Ascenders_Offset, Ascenders_Offset];//[-.1:.05:2]
mid_x=(Edge_to_Column+(Edge_to_Column+1*(Length-2*Edge_to_Column)/11))/2;
mid_y=(Edge_to_Row+Edge_to_Row+1*(Width-2*Edge_to_Row)/6)/2;
half_line=Line_Width/2;
mid_xl=Length-2*mid_x;
mid_yw=Width-2*mid_y;

$fn=$preview?30:60;

text_fn=40;

Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;

//for (r=[0:1:6]){
//    for (c=[0:1:11]){
//        xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
//        ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
//        translate([xpos, ypos])
//        text(text=Layout[r][c], size=Type_Size, halign="center", valign="center");
//    }
//}
//}
//Circles that are filled in
PlakatCircleFillArray=[
[0,1,1,1,1,1,1,1,1,1,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,1,1,1,1,1,1,1,1,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,1,1,1,1,1,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0]];

//squares behind circles that are gray/checkered
PlakatBackgroundFillArray=[
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,0,0,0,0,0,0,1,1,1],
[1,1,1,0,0,0,0,0,0,1,1,1],
[1,1,1,1,1,1,1,1,1,1,1,1]];

//squares behind circles that are solid black
PlakatSolidFillAray=[
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0]];

//Circles that are filled in
NormalCircleFillArray=[
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,1,1,1,1,0,0,0,0,0,0],
[0,1,1,1,1,1,0,0,0,0,0,0],
[0,1,1,1,1,1,0,0,0,0,0,0],
[0,1,1,1,1,1,0,0,0,0,0,0],
[0,1,1,1,1,1,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0]];

NormalBackgroundFillArray=[
[1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1]];

 NormalSolidFillAray=[
[0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,1,1,1,1,1,0],
[0,0,0,0,0,0,1,1,1,1,1,0],
[0,0,0,0,0,0,1,1,1,1,1,0],
[0,0,0,0,0,0,1,1,1,1,1,0],
[0,0,0,0,0,0,1,1,1,1,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0]];



CircleFillArray=NormalCircleFillArray;
BackgroundFillArray=NormalBackgroundFillArray;
SolidFillArray=NormalSolidFillAray;




z=.001;

function LocateCenter(r,c) = [Edge_to_Column+c*(Length-2*Edge_to_Column)/11, Edge_to_Row+(6-r)*(Width-2*Edge_to_Row)/6];

function LocateBaseline(r,c)
= [Edge_to_Column+c*(Length-2*Edge_to_Column)/11, Edge_to_Row+(6-r)*(Width-2*Edge_to_Row)/6-Height_Offset];

XY=[(Edge_to_Column+2*(Length-2*Edge_to_Column)/11)-(Edge_to_Column+1*(Length-2*Edge_to_Column)/11), (Edge_to_Row+2*(Width-2*Edge_to_Row)/6)-(Edge_to_Row+1*(Width-2*Edge_to_Row)/6)];

module RadiusRectangle(){
    hull(){
        translate([Corner_Radius, Corner_Radius])
        circle(r=Corner_Radius);
        translate([Length-Corner_Radius, Corner_Radius])
        circle(r=Corner_Radius);
        translate([Length-Corner_Radius, Width-Corner_Radius])
        circle(r=Corner_Radius);
        translate([Corner_Radius, Width-Corner_Radius])
        circle(r=Corner_Radius);
    }
}

module CheckerPattern(){
    if (Checker==true){
        for (x=[0:Square_Pattern_Pitch:Length]){
            for (y=[0:Square_Pattern_Pitch:Width]){
                translate([x,y])
                rotate([0,0,45])
                square(Square_Pattern_Size);
            }
        }
    }
}

module CenterRectangle(){
    translate([mid_x, mid_y])
    square([Length-2*mid_x, Width-2*mid_y]);

}

module ClearHoles(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
            //xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
            //ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;       
            if (Layout[r][11-c]!=" ")
            translate(LocateCenter(r,c))
            scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
            circle(d=Circle_Diameter);
        }
    }
}

module LiningCircle(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
            xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
            ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
            translate([xpos, ypos])
            scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter]){
            difference(){
            circle(d=Circle_Diameter+Line_Width);
            circle(d=Circle_Diameter-Line_Width);}
            }
        }
    }
}

module LiningRectangle(){
    translate([Length/2, Width/2]){
        difference(){
            square([mid_xl+Line_Width, mid_yw+Line_Width], center=true);
            square([mid_xl-Line_Width, mid_yw-Line_Width], center=true);
        }
    }
}

module Rectangle(){
    square(XY+[z,z], center=true);
}
module ClearShape(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
        if (BackgroundFillArray[r][c]==0)
        translate(LocateCenter(r,c))
        Rectangle();
        
        
        }
    }
}

module SolidShape(){
    difference(){
    
    union(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
        if (SolidFillArray[r][c]==1)
        translate(LocateCenter(r,11-c))
        Rectangle();
        
        
        }
    }
    }
    ClearHoles();
    
    }
}

module LinedCircle(){
    scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter]){
        difference(){
            circle(d=Circle_Diameter+Line_Width);
            circle(d=Circle_Diameter-Line_Width);
        }
    }
}

module SolidCircle(){
    scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
    circle(d=Circle_Diameter+Line_Width);
}

module LineCircles(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
            if (CircleFillArray[r][c]==0 && Layout[r][c]!=" ")
            translate(LocateCenter(r,11-c))
            LinedCircle();
        }
        
    }
}

module DarkText(Char){
    difference(){
        SolidCircle();
        translate([0, -Height_Offset, 0])
        2DText(Char);
    }
}

module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=mink_fn);
}


module 2DText(Char){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, (y==[]?0:Character_Modifieds_Offset), 0])
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

module ArrangeText(){
    for (r=[0:1:6]){
        for (c=[0:1:11]){
            if (CircleFillArray[r][c]==0)
            translate(LocateBaseline(r,11-c))
            2DText(Layout[r][c]);
            if (CircleFillArray[r][c]==1)
            translate(LocateCenter(r,11-c))
            DarkText(Layout[r][c]);
            
            
        }
        
    }
    
}

//ClearShape();

//projection()
if (Assert==true)
assert(false,"Uncheck Automatic Preview and Assert");
else{
    Array2();
}

module Array2(){
    union(){
        difference(){
            RadiusRectangle();
            CheckerPattern();
            ClearHoles();
            ClearShape();
        }
        LineCircles();
        ArrangeText();
        SolidShape();
    }
}