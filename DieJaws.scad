//Keyring Pliers
z=.01;
cyl_fn=360;
mink_fn=30;
/* [Plier Variables] */


/* [Jaw Variables] */
Jaw_X=67.5;
Jaw_Y=12.6;
JawSlot=3.1;
JawSlot_YOffset=3.1;
JawSlot_X=13.7;
HingeHole_X=38.1;
HingeHole_Y=6;
JawWidth=7.7;
HingeHoleDiameter=4.7;
HingeClearanceDiameter=10;
Hinge_X=23;
Hinge_Y=13;
MaxJawBite=10.9;
FastnerDiameter=4;

/* [Embosser] */
Text=["C"];
TextSize=3;
TextFont="Courier New";
DieEdge=5;
TextYSpacing=4;
TextXSpacing=4;
EmbossHeight=1;
EmbossRadius=.3;
PaperThickness=.25;
DieHeight=Jaw_Y;





TextLengths=[for(i=[0:1:len(Text)-1]) len(Text[i])];
Die_X=(max(TextLengths)-1)*TextXSpacing+2*DieEdge;
Die_Y=(len(Text)-1)*TextYSpacing+2*DieEdge;

SlopeThetaInverse=atan(((EmbossHeight-EmbossRadius)/(EmbossHeight/2-EmbossRadius))^-1);
FemaleRadius=EmbossRadius/(1-sin(SlopeThetaInverse));
FemaleRadius_X=FemaleRadius*cos(SlopeThetaInverse);
FemaleRadius_Y=FemaleRadius*sin(SlopeThetaInverse);



module PlainJawXSection(){
    difference(){
    polygon([[0, 0], [HingeHole_X+JawWidth+z, 0], [HingeHole_X+JawWidth+z, Jaw_Y], [4, Jaw_Y], [0, Jaw_Y-JawSlot_YOffset-JawSlot]]);
    //square([HingeHole_X+PinToAxis+JawWidth/2, Jaw_Y]); 
    translate([-z, JawSlot_YOffset])
    square([z+JawSlot_X, JawSlot]);
    translate([HingeHole_X, HingeHole_Y])
    circle(d=HingeHoleDiameter, $fn=cyl_fn);
    translate([Hinge_X, Hinge_Y])
    circle(d=HingeClearanceDiameter, $fn=cyl_fn);
    }
}

module PlainJaw(){
    translate([0, JawWidth, 0])
    rotate([90, 0, 0])
    linear_extrude(JawWidth)
    PlainJawXSection();
}








module OrientJaw(){
    translate([0, JawWidth/2, 0])
    rotate([90, 0, 0])
    children();
}



module Post(){
    cylinder(h=PostHeight, d=PostDiameter, $fn=cyl_fn);
}



module Assembly(){
    OrientJaw()
    PlateJaw();

    translate([0, 0, 2*Jaw_Y+$t*MaxJawBite])
    rotate([180, 0, 0]){
        OrientJaw()
        PostJaw();
    }
    
    
    
}


module DieText(){
    translate([0, TextYSpacing*(len(Text)-1)/2])
    for (i=[0:1:len(Text)-1]){
        for (j=[0:1:len(Text[i])-1]){
        translate([-TextXSpacing*(len(Text[i])-1)/2+TextXSpacing*j, -TextYSpacing*i])
        text(text=Text[i][j], size=TextSize, font=TextFont, halign="center", valign="center");
        }
    }
}

module RadiusCorner(){
translate([0, 0, -EmbossRadius])
rotate_extrude($fn=mink_fn)
difference(){
square([FemaleRadius_X, EmbossRadius]);
translate([FemaleRadius_X, FemaleRadius_Y+EmbossRadius])
circle(r=FemaleRadius, $fn=mink_fn);
}
}

module MinkTextSlice(t){
    difference(){
        MinkText(t);
        translate([-100, -100, EmbossRadius])
        cube(200);
        translate([-100, -100, -100+EmbossRadius-z])
        cube([200, 200, 100]);
    }
}
//DieText();

module MinkText(t){
    minkowski(){
        linear_extrude(EmbossHeight)
        DieText();
        translate([0, 0, -EmbossHeight])
        
        hull(){
            cylinder(r=.5*EmbossHeight+t, h=z, $fn=mink_fn);
            translate([0, 0, EmbossHeight-EmbossRadius])
            sphere(r=EmbossRadius+t, $fn=mink_fn);
            
        }
    
    }
}

//RadiusCorner();
//FemaleDieMinkowski();
//MinkTextSlice(0);
//Assemble();

module MaleDie(){
    union(){
        MinkText(0);
        translate([-Die_X/2, -Die_Y/2, -DieHeight])
        cube([Die_X, Die_Y, DieHeight]);
    }
}

module FemaleDie(){
    difference(){
        translate([0, 0, DieHeight/2])
        cube([Die_X, Die_Y, DieHeight], center=true);
        {
         
            MinkText(PaperThickness);

            minkowski(){
                MinkTextSlice(PaperThickness);
                RadiusCorner();
            }
            
        }
    }
    
    
    
}

module Assemble(){
    difference(){
        union(){
            FemaleDie();
            MaleDie();
        }
        translate([0, -100, -100])
        cube([200, 200, 200]);
        
    }
}

//Now Attach Dies to Jaws!