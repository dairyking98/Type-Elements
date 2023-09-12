Test_String="NOW IS THE TIME FOR ALL ";

Type_Size=1.9;
Typeface_="Wingdings";

//BOTTOM LINE - 10 CPI
for (n=[0:1:len(Test_String)-1]){
    translate([2.54/2+2.54*n,0,0])
    linear_extrude(1)
    text(Test_String[n],size=Type_Size,halign="center",valign="baseline",font=Typeface_);
    }

//TOP LINE - AS TYPED
translate([0,5,0])
linear_extrude(1)
text(Test_String,size=Type_Size,halign="left",valign="baseline",font=Typeface_);