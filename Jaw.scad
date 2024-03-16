//Keyring Pliers
z=.01;
cyl_fn=360;
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

/* [Custom Variables] */
PinToAxis=34;
FastnerDiameter=4;


/* [Plate Variables] */
RingID=14;
RingIDTop=11.3;
RingThickness=.5;
ProngWidth=2;
ProngCount=3;
PlateThickness=4;
ProngRadius=2;
PlateStep=2;
PlateGap=3.5;
CountersinkDepth=2;
CountersinkDiameter=7;
SlotDepth=.5;

/* [Post and Pad Variables] */
PostDiameter=5;
PostHeight=12;
RingGrooveDiameter=(RingID-RingIDTop)/2;

/* [Assembly] */
AssembleRotate=false;
PostOrPad=true;


module BlankPlateXSection(){
    hull(){
        translate([-PinToAxis/2, 0])
        circle(d=RingID+5, $fn=cyl_fn);
        translate([PinToAxis/2, 0])
        circle(d=RingID+5, $fn=cyl_fn);
    }
}

module KeyRingSection(){
    circle(d=RingID, $fn=cyl_fn);
    for (theta=[0:360/ProngCount:360*(ProngCount-1)/ProngCount]){
        rotate([0, 0, 180+theta])
        intersection(){
            circle(d=RingID+RingThickness*2, $fn=cyl_fn);
            translate([0, -ProngWidth/2])
            square([20, ProngWidth]);
        }

    }
}

module PlateXSection(){
    difference(){
        BlankPlateXSection();
        translate([PinToAxis/2, 0])
        KeyRingSection();
        translate([-PinToAxis/2, 0])
        circle(d=RingID-2*ProngRadius, $fn=cyl_fn);
        for (i=[0, 180])
        rotate([0, 0, i])
        translate([PinToAxis/2, -PlateGap/2])
        square([10, PlateGap]);
    }
}

module Plate(){
    difference(){
        linear_extrude(PlateThickness)
        PlateXSection();
        translate([PinToAxis/2, 0, PlateThickness-PlateStep])
        cylinder(h=5, d=RingID+2*RingThickness, $fn=cyl_fn);
        translate([-PinToAxis/2, 0, PlateThickness-SlotDepth])
        hull($fn=cyl_fn){
        rotate_extrude($fn=cyl_fn)
            translate([RingID/2-ProngRadius+2*RingThickness, 0])
            circle(r=ProngRadius, $fn=cyl_fn);
            rotate_extrude($fn=cyl_fn)
            translate([RingID/2-ProngRadius+2*RingThickness, 10])
            circle(r=ProngRadius, $fn=cyl_fn);
        }
        translate([0, 0, -z]){
            cylinder(d=FastnerDiameter, h=10, $fn=cyl_fn);
            cylinder(d=CountersinkDiameter, h=CountersinkDepth+z, $fn=cyl_fn);
        }
        translate([-100, -JawWidth/2, PlateThickness-SlotDepth])
        cube([200, JawWidth, 10]);
    }
}

module PlainJawXSection(){
    difference(){
    square([HingeHole_X+PinToAxis+JawWidth/2, Jaw_Y]); 
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

module PlateJaw(){
    difference(){
        difference(){
            linear_extrude(JawWidth)
            difference(){
                PlainJawXSection();
                PlateJawRemove();
                }
            }
            
        translate([HingeHole_X+PinToAxis/2, -z, JawWidth/2])
        rotate([-90, -90, 00]){
            RadiusJawShape();
            cylinder(h=20, d=FastnerDiameter, $fn=cyl_fn);
        }
    }
}

module PostJaw(){
    difference(){
        linear_extrude(JawWidth)
        difference(){
            PlainJawXSection();
            PostJawRemove();
        }
        
        translate([HingeHole_X+PinToAxis, -z, JawWidth/2])
        rotate([-90, -90, 00]){
            RadiusJawShape();
            cylinder(h=20, d=FastnerDiameter, $fn=cyl_fn);
        }
    }
}

module PlateJawRemove(){
    translate([HingeHole_X, 0])
    polygon([[0, Jaw_Y+z], [PinToAxis/2-Jaw_Y/2-1, Jaw_Y/2], [PinToAxis/2+Jaw_Y/2, Jaw_Y/2], [PinToAxis/2+Jaw_Y/2, 0-z], [PinToAxis+JawWidth/2+z, -z], [PinToAxis+JawWidth/2+z, Jaw_Y+z]]);
}


module PostJawRemove(){
    translate([HingeHole_X, 0])
    polygon([[0, -z], [PinToAxis+JawWidth/2+z, -z], [PinToAxis+JawWidth/2+z, Jaw_Y/2], [PinToAxis-JawWidth/2, Jaw_Y/2]]);
}

module OrientJaw(){
    translate([0, JawWidth/2, 0])
    rotate([90, 0, 0])
    children();
}

module RadiusJawShape(){
    difference(){
        translate([-10, 0, 0])
        cube(20);
        translate([0, 0, -z])
        cylinder(d=JawWidth, h=25, $fn=cyl_fn);
        
    }
}

module Post(){
    cylinder(h=PostHeight, d=PostDiameter, $fn=cyl_fn);
}

module Pad(){
    difference(){
        hull(){
            translate([0, 0, 2])
            rotate_extrude($fn=cyl_fn)
            translate([2, 0])
            circle(r=2, $fn=cyl_fn);
            translate([0, 0, PostHeight])
            cylinder(h=z, d=RingID+4, $fn=cyl_fn);
            }
        translate([0, 0, PostHeight])
        #rotate_extrude($fn=cyl_fn)
        translate([RingID/2, 0])
        circle(d=RingGrooveDiameter, $fn=cyl_fn);
    }
}

module Assembly(){
    OrientJaw()
    PlateJaw();

    translate([0, 0, 2*Jaw_Y+$t*MaxJawBite])
    rotate([180, 0, 0]){
        OrientJaw()
        PostJaw();
        translate([HingeHole_X+PinToAxis, 0, Jaw_Y])
        if (PostOrPad == false)
        Post();
        else
        Pad();
    }
    

    translate([HingeHole_X+PinToAxis/2, 0, -PlateThickness+SlotDepth])
    rotate([0, 0, AssembleRotate?180:0])
    Plate();
}

//OrientJaw()
//PostJaw();
//Pad();
OrientJaw()
PlateJaw();