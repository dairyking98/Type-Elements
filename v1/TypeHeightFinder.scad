Test_String="NOW IS THE TIME FOR ALL ";

Type_Size=1.9;//[1:.05:10]
Typeface_="OpenDyslexicMono";
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=1;//[0, 1];
//Individual Character Height Adjustments
Character_Modifieds="_";
Character_Modifieds_Offset=1;//[-1.5:.01:1.5]
Scale_Multiplier_Text=".";
Scale_Multiplier=1.4;
//BOTTOM LINE - 10 CPI
pica=25.4/10;
echo(is_string(pica));
elite=25.4/12;
Pitch_Custom=6;//.01
Pitch=2.6;//[2.54:2.54 mm 10pitch, 2.116666667:2.12 mm 12pitch, 2.6:2.6 mm, 2.3:2.3 mm, 1.69:1.69 mm 15pitch, 2.032:2.03 mm 12.5pitch]
echo(Pitch);
Blick_Bounding_Box=false;
Bennett_Bounding_Box=false;
Helios_Bounding_Box=false;
translate([0, 15, 0])
text(Test_String[1],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
Custom_Bounding_Box=false;
Bound_x=2.54;
Bound_y=3.43;

if (Custom_Bounding_Box==true){
translate([Bound_x/2, Bound_y/2])
#square([Bound_x, Bound_y], center=true);}

if (Blick_Bounding_Box==true){
translate([Pitch/2, 2.5/2])
#square([2.54, 2.5], center=true);
translate([Pitch/2, -.65/2])
#square([2.42, .65], center=true);}

if (Bennett_Bounding_Box==true){
translate([Pitch/2, 2.56/2])
#square([2.54, 2.56], center=true);
translate([Pitch/2, -.79/2])
#square([2.42, .79], center=true);}

if (Helios_Bounding_Box==true){
translate([Pitch/2, 2.87/2])
#square([2.54, 2.87], center=true);
//translate([Pitch/2, -.79/2])
//#square([2.42, .79], center=true);
}

for (n=[0:1:len(Test_String)-1]){
    x=search(Test_String[n], Scale_Multiplier_Text);
    y=search(Test_String[n], Character_Modifieds);
    translate([Pitch/2+Pitch*n,0,0])
    //translate([0,Test_String[n]==Character_Modifieds ?  Character_Modifieds_Offset : 0])
    translate([0, y==[] ? 0 : Character_Modifieds_Offset, 0])
    linear_extrude(1)
    //text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
    scale([x==[] ? 1: Scale_Multiplier, x==[] ? 1: Scale_Multiplier, 1])
    if (Weight_Adj_Mode==1)
                minkowski(){
                    text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
                    circle(r=1, $fn=44);
                }
            else if (Weight_Adj_Mode==0)
                difference(){
                    text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    }
                    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
                    circle(r=1, $fn=44);
    }
    }
}
//TOP LINE - AS TYPED
translate([0,5,0])
linear_extrude(1)
text(Test_String,size=Type_Size,halign="left",valign="baseline",font=Typeface_);