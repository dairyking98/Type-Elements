//Custom Layout
1st_Row="";
2nd_Row="";
3rd_Row="";
4th_Row="";
5th_Row="";
6th_Row="";
7th_Row="";
CUSTOMLAYOUT=[1st_Row,2nd_Row,3rd_Row,4th_Row,5th_Row,6th_Row,7th_Row];
include <IndexLayouts.scad>

CharLegend=[7,8,9,10,11,0,1,2,3,4,5,6];
//Layout Selection
Layout_Selection=2; //[0:American?, 1:Custom Layout, 2:Deutsch 4, 3:English 4, 4:French 3, 5:International Schreibschrift, 6:Schwedisch 2]
Layout=Layouts[Layout_Selection];
//Index Length
Length=133;
//Index Width
Width=83;
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
Corner_Radius=9;
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


//for (r=[0:1:6]){
//    for (c=[0:1:11]){
//        xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
//        ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
//        translate([xpos, ypos])
//        text(text=Layout[r][c], size=Type_Size, halign="center", valign="center");
//    }
//}
//}

module Text (Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape){
    xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
        ypos=Edge_to_Row+(6-r)*(Width-2*Edge_to_Row)/6-Height_Offset;
        x=search(Layout[r][c],Character_Modifieds);
        translate([xpos, ypos])
        translate([0, x==[]?0:Character_Modifieds_Offset[x[0]]])
        //text(text=Layout[r][c], font=Typeface_, size=Type_Size, halign="center", valign="baseline");
        if (Weight_Adj_Mode==1)
                minkowski(){
                    text(Layout[r][c],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
                    if (Weight_Adj_Shape==0)
                    circle(r=1);
                    else
                    square([Horizontal_Weight_Adj*2, Vertical_Weight_Adj*2], center=true);
                }
            else if (Weight_Adj_Mode==0)
                difference(){
                    text(Layout[r][c],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Layout[r][c],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    }
                    scale([SomeHorizontal_Weight_Adj, SomeVertical_Weight_Adj])
                    circle(r=1);
                    }
                }
}
//projection()
translate([0,0,-1])
linear_extrude(1)
union(){
    difference(){
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
        //FIRST CUT:
        //CUT BACKGROUND
        if (Checker==true){
        for (x=[0:Square_Pattern_Pitch:Length]){
            for (y=[0:Square_Pattern_Pitch:Width]){
                translate([x,y])
                rotate([0,0,45])
                square(Square_Pattern_Size);
            }
        }
        }
        //CUT CENTER RECTANGLE
        translate([mid_x, mid_y])
        square([Length-2*mid_x, Width-2*mid_y]);
        
        
        for (r=[0:1:6]){
            for (c=[0:1:11]){
                xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
                ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
                translate([xpos, ypos])
                scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
                circle(d=Circle_Diameter);
            }
        }
    }//END CUTTING
    
    //BEGIN LINEWORK
    //BOLDING OUTER CIRCLES
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
    //BORDERING CENTER RECTANGLE
    
    translate([Length/2, Width/2]){
        difference(){
            square([mid_xl+Line_Width, mid_yw+Line_Width], center=true);
            square([mid_xl-Line_Width, mid_yw-Line_Width], center=true);
        }
    }//END LINEWORK
    
    //BEGIN PLACING CHARACTERS
    //PLACE BORDERING CHARACTERS
    for (r=[0,6]){
        for (c=[0:1:11]){
            Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);
        }
    }
    for (r=[1:1:5]){
        for (c=[0,11]){
        Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);
        }
    }//END BORDERING CHARACTERS
    
    //FILL HANDLING
    //IF LEFT SIDE FILL = FALSE
    if (Left_Side_Circle_Fill==false){
        for (r=[1:1:5]){
            for (c=[0:1:5]){
                Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);
            }
        }
    }
    else //IF LEFT SIDE FILL = TRUE
        for (r=[1:1:5]){
            for (c=[1:1:5]){
                xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
                ypos=Edge_to_Row+(6-r)*(Width-2*Edge_to_Row)/6;
                difference(){
                translate([xpos, ypos])
                scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
                circle(d=Circle_Diameter-Line_Width); 
                Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);}
            }
        }
    //IF RIGHT SIDE FILL = FALSE
    if (Right_Side_Circle_Fill==false){
        for (r=[1:1:5]){
            for (c=[6:1:11]){
                Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);
            }
        }
    }
    else //IF RIGHT SIDE FILL = TRUE
        for (r=[1:1:5]){
            for (c=[6:1:10]){
                xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
                ypos=Edge_to_Row+(6-r)*(Width-2*Edge_to_Row)/6;
                difference(){
                translate([xpos, ypos])
                scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
                circle(d=Circle_Diameter-Line_Width); 
                Text(Length, Width, r, c, Edge_to_Row, Edge_to_Column, Layout, Character_Modifieds, Character_Modifieds_Offset, Height_Offset, Type_Size, Typeface_, Weight_Adj_Mode, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Shape);}
            }
        }
    //IF LEFT SIDE BG FILL = TRUE
    if (Left_Side_Background_Fill==true){
        difference(){
            translate([mid_x, mid_y])
            square([mid_xl/2, mid_yw]);
            for (r=[0:1:6]){
                for (c=[0:1:11]){
                    xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
                    ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
                    translate([xpos, ypos])
                    scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
                    circle(d=Circle_Diameter);
                }
            }
        }
    }
    //IF RIGHT SIDE BG FILL = TRUE
    if (Right_Side_Background_Fill==true){
        difference(){
            translate([Length/2, mid_y])
            square([mid_xl/2, mid_yw]);
            for (r=[0:1:6]){
                for (c=[0:1:11]){
                    xpos=Edge_to_Column+c*(Length-2*Edge_to_Column)/11;
                    ypos=Edge_to_Row+r*(Width-2*Edge_to_Row)/6;
                    translate([xpos, ypos])
                    scale([1, (Circle_Diameter+2*Circle_Height_Bump)/Circle_Diameter])
                    circle(d=Circle_Diameter);
                }
            }
        }
    }
}
