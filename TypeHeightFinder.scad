Test_String="NOW IS THE TIME FOR ALL ";

Type_Size=1.9;//[1:.05:5]
Typeface_="OpenDyslexicMono";
Horizontal_Weight_Adj=.001;//[.001:.001:.2]
Vertical_Weight_Adj=.001;//[.001:.001:.2]
//0 For subtractive, 1 for additive
Weight_Adj_Mode=1;//[0, 1];

//BOTTOM LINE - 10 CPI
pica=25.4/10;
echo(is_string(pica));
elite=25.4/12;
Pitch=2.6;//[2.54:Pica, 2.116666667:Elite, 2.6:Euro Pica, 2.3:Euro Elite]
echo(Pitch);
translate([0, 15, 0])
text(Test_String[1],size=Type_Size,halign="center",valign="baseline",font=Typeface_);

for (n=[0:1:len(Test_String)-1]){
    translate([Pitch/2+Pitch*n,0,0])
    linear_extrude(1)
    //text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
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