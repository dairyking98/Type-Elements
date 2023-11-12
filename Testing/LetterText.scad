module LetterText (Cutout, Typeface_, Type_Size, Char, Platen_Diameter, Min_Height, Draft_Angle, Debug, Horizontal_Weight_Adj, Vertical_Weight_Adj, Weight_Adj_Mode){
    $fn = $preview ? 12 : 24;
    translate([0, 0, -Min_Height])
    minkowski(){
        difference(){
            mirror([1,0,0])
            linear_extrude(2)
            if (Weight_Adj_Mode==1)
                minkowski(){
                    text(Char,size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
                    circle(r=1, $fn=44);
                }
            else if (Weight_Adj_Mode==0)
                difference(){
                    text(Char,size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(Char,size=Type_Size,halign="center",valign="baseline",font=Typeface_);
                    }
                    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
                    circle(r=1, $fn=44);
                    }
                }

                    
                
            translate([0, Cutout, (Platen_Diameter/2+Min_Height)])
            rotate([0, 90, 0])
            cylinder(h=5, d=Platen_Diameter, center=true, $fn = $preview ? 60 : 360);
        }
        if (Debug!=true)
            rotate([0,-180, 0])
            cylinder(h=1.5, r2=1.5*sin(Draft_Angle), r1=0, $fn = $preview ? 22 : 44);
    }
}

//LetterText(0, 1.5, "Consolas", 3, "A", 25.4, 2, 30, false, .001, .001, 1);