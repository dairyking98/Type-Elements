/*Blickensderfer Element Type Height Finder
Top Line: Normal Text
Bottom Line: Monospaced (How it will look printed on page at 10 CPI)

Things to note: if you exceed limits of bounding box, characters may begin to 
overlap when using the element.

*/


Test_String="NOW IS THE TIME FOR ALL ";
//Universal Offset for "z fighting" - DO NOT CHANGE
e=.001;
//Cylinder Facet Number
cyl_fn = 360;
//Resin Support Facet Number
resin_fn=20;
//Minkowski Facet Number (Draft Angles)
mink_fn=10;
//Text Facet Number 
text_fn=44;
Type_Size=1.9;//[1:.05:10]
Typeface_="OpenDyslexicMono";
//Horizontal Weight Adjustment
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
//Vertical Weight Adjustment
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//Weight Adjustment Type
Weight_Adj_Mode=0;//[0:None, 1:Subtractive, 2:Additive]
//Weight Adjustment Shape
Weight_Adj_Shape=0;//[0:Square, 1:Circle]
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=1;//[-1.5:.01:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.0;
Pitch=2.54;//[2.54:Pica, 2.116666667:Elite, 2.6:Euro Pica, 2.3:Euro Elite, 6:Custom]
echo(Pitch);
Blick_Bounding_Box=false;
translate([0, 15, 0])
text(Test_String[1],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
Custom_Bounding_Box=false;
Bound_x=2.54;
Bound_y=3.43;

//2D Text Weight Adjuster Profile/Shape
module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=mink_fn);
}

//Creates 2D Text
module 2DText(Char){
    x=search(Char, Scale_Multiplier_Text);
    y=search(Char, Character_Modifieds);
    translate([0, y==[]?0:Character_Modifieds_Offset, 0])
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

if (Custom_Bounding_Box==true){
translate([Bound_x/2, Bound_y/2])
#square([Bound_x, Bound_y], center=true);}

if (Blick_Bounding_Box==true){
translate([Pitch/2, 2.5/2])
#square([2.54, 2.5], center=true);
translate([Pitch/2, -.65/2])
#square([2.42, .65], center=true);}



for (n=[0:1:len(Test_String)-1]){
    translate([Pitch/2+Pitch*n,0,0])
    2DText(Test_String[n]);
}
//TOP LINE - AS TYPED
translate([0,5,0])
linear_extrude(1)
text(Test_String,size=Type_Size,halign="left",valign="baseline",font=Typeface_);