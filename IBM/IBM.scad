//dairy's rendition of ibm selectric type element model
//Leonard Chau      November 4, 2024       t(-.-t)

/* [Global Parameters] */
z=.001;
$fn=$preview?44:44;
mink_fn=20;
text_fn=20;
cyl_fn=360;
surface_fn=120;

/* [Rendering] */
//render something?
RENDER=false;
//render selection?
RENDER_MODE=0;//[0:Composer (88char), 1:Selectric I/II (88char)]
//render variant?
RENDER_VARIANT=0;//[0:plain, 1:resin print]
//turn on minkowski?
MINK_ON=false;
//cross section?
XSECTION=false;
XSECTION_THETA=0;
//selective render?
SELECTIVE_RENDER=false;
//selective render chars?
SELECTIVE_RENDER_CHARS="sine";

/* [Typeface Stuff] */
FONT="Arial";
FONTSIZE=3;
FONT_WEIGHT_OFFSET=0;//.01
X_WEIGHT_ADJUSTMENT=.01;
Y_WEIGHT_ADJUSTMENT=.01;
X_POS_OFFSET_COMPOSER=1.5;//.1
Y_POS_OFFSET_COMPOSER=-1;
Y_POS_OFFSET_S12=-.5;
Y_POS_OFFSET=RENDER_MODE==0?Y_POS_OFFSET_COMPOSER:Y_POS_OFFSET_S12;
H_ALIGNMENT=RENDER_MODE==0?"left":"center";


/* [Typeball Dimensions] */
//sphere diameter
SPHERE_OD=33.4;
//character-concave to character-concave diameter
MAX_OD=34.9;
//sphere center to top flat
TOPFLAT_TO_CENTER=11.4;
//shaft ID
SHAFT_ID=8.8;
//inside ID
INSIDE_ID=28.15;
//shaft boss height
BOSS_H=8.07;
//boss OD
BOSS_OD=13.8;
//skirt top OD
SKIRT_TOP_OD=32.3;
//skirt bottom OD
SKIRT_BOTTOM_OD=30.2;
//overall thickness of element
ELEMENT_OAT=22.0;
//angle between characters
LATITUDE_SPACING=360/22;
//angle between rows
LONGITUDE_SPACING=[32.8, 16.4, 0, -16.4];
//platen diameter
PLATEN_OD=45;
//radius of hollow section
HOLLOW_R=2;
//drive notch width
DRIVE_NOTCH_WIDTH=1.4;
//drive notch height
DRIVE_NOTCH_HEIGHT=2.2;
//drive notch theta from arrow
DRIVE_NOTCH_THETA_=131.8;
//detent valley from center
DETENT_VALLEY_TO_CENTER=6;
//detent teeth clock offset
DETENT_SKIRT_CLOCK_OFFSET=1.5;


/* [Character Mapping] */

//lowercase layout on machine; left to right, top to bottom
LOWERCASE88="

1234567890-=
qwertyuiop½
asdfghjkl;'
zxcvbnm,./

";

//uppercase layout on machine; left to right, top to bottom
UPPERCASE88="
!@#$%¢&*()_+
QWERTYUIOP¼
ASDFGHJKL:\"
ZXCVBNM,.?"
;

//uppercase composer layout on machine; left to right, top to bottom
LOWER_CASE_COMPOSER = str(
    "1234567890-=",
    "qwertyuiop?",
    "asdfghjkl][",
    "zxcvbnm,.;"
);

//lowercase composer layout on machine; left to right, top to bottom
UPPER_CASE_COMPOSER = str(
    "!†+$%/&*()_@",
    "QWERTYUIOP¾",
    "ASDFGHJKL¼½",
    "ZXCVBNM‘’:"
);

S12CASES88=[LOWERCASE88, UPPERCASE88];
COMPOSERCASES88=[LOWER_CASE_COMPOSER,UPPER_CASE_COMPOSER];
CASES88=COMPOSERCASES88;

//type element mapping starting at arrow, moving clockwise from the top, from top to bottom

S1288="";

COMPOSERMAP88="
s10928’‘/+$S!()†*.,634

iatb75¾_½CLIATB&%?-[cl

nrodwkXVUMHNRODWKxvumh

efgq;j@¼ZPYEFGQ:J=]zpy
";

MAP88=COMPOSERMAP88;

//array for character, latitude integer, and longitude integer
CHAR_LAT_LONG=[for (i=[0:1]) for (j=[0:len(CASES88[0])-1]) 

    [CASES88[i][j], ceil(search(CASES88[i][j], str(MAP88))[0]/22+.001)-1, search(CASES88[i][j], str(MAP88))[0]%22]

];

//print master array to console
echo(CHAR_LAT_LONG);

/* [Resin Supports] */
TIP_D=.8;
TIP_H=1;
ROD_D=1.2;
ROD_R=ROD_D/2;
BASE_D=4;
BASE_H=2;




/* [Calculated Variables] */

//sphere radius
SPHERE_R=SPHERE_OD/2;
//skirt large radius
SKIRT_TOP_R=SKIRT_TOP_OD/2;
//center to ceiling of element
CEILING=TOPFLAT_TO_CENTER;
//center to floor of element
FLOOR=abs(TOPFLAT_TO_CENTER-ELEMENT_OAT);
//center to skirt of element
CENTER_TO_SKIRT=(SPHERE_R^2-SKIRT_TOP_R^2)^.5;
//platen radius
PLATEN_R=PLATEN_OD/2;
//height of letter
TYPE_ALTITUDE=(MAX_OD-SPHERE_OD)/2;
//inside radius
INSIDE_R=INSIDE_ID/2;
//inside boss radius
BOSS_R=BOSS_OD/2;
//compensated drive notch theta
DRIVE_NOTCH_THETA=DRIVE_NOTCH_THETA_+DETENT_SKIRT_CLOCK_OFFSET;



//make solid element
module FullBody(){
union(){
    $fn=surface_fn;
    sphere(d=SPHERE_OD);
    translate([0, 0, -FLOOR])
    cylinder(d1=SKIRT_BOTTOM_OD, d2=SKIRT_TOP_OD, h=FLOOR-CENTER_TO_SKIRT);
    AssembleMinkowski();
    }
}

//2d text
module Text(char){
    offset(FONT_WEIGHT_OFFSET)
    minkowski(){
        translate([RENDER_MODE==0?X_POS_OFFSET_COMPOSER:0, Y_POS_OFFSET, 0])
        mirror([1, 0, 0])
        text(char, size=FONTSIZE, font=FONT, valign="baseline", halign=H_ALIGNMENT, $fn=text_fn);
        square([z+X_WEIGHT_ADJUSTMENT, z+Y_WEIGHT_ADJUSTMENT], center=true);
    }
}

//platen cutout
module PlatenCutout(char){
            rotate([0, -GetLong(char), GetLat(char)])
            translate([SPHERE_R+PLATEN_R+TYPE_ALTITUDE, 0, 0])
            rotate([90, 0, 0])
            cylinder(d=PLATEN_OD, h=10, center=true, $fn=cyl_fn);
}

//position extruded character
module PositionText(char){
    rotate([90 - GetLong(char), 0, 90 + GetLat(char)])
    translate([0, 0, SPHERE_R+z])
    linear_extrude(6)
    Text(char);
}

//render code
module Render(){
    if (RENDER==true){
        difference(){
            SubtractFromFull();
            if (XSECTION==true)
            rotate([0, 0, XSECTION_THETA])
            translate([0, -50, -50])
            cube(100);
        }
    }
}

//get latitude function with char input
function GetLat(char)= CHAR_LAT_LONG[search(char, CHAR_LAT_LONG)[0]][2]*LATITUDE_SPACING;

//get longitude function with char input
function GetLong(char)= LONGITUDE_SPACING[CHAR_LAT_LONG[search(char, CHAR_LAT_LONG)[0]][1]];

//minkowski single character
module SingleMinkowski(char){
    minkowski(){
        difference(){
            PositionText(char);
            PlatenCutout(char);
            
        }
        if (MINK_ON==true){
            rotate([90 - GetLong(char), 0, 90 + GetLat(char)])
            translate([0, 0, -2])
            cylinder(d1=1.75, d2=0, h=2, $fn=mink_fn);
        }
    }
}

//assemble minkowski characters
module AssembleMinkowski(){
    for (i=[0:len(CHAR_LAT_LONG)-1])
    if (SELECTIVE_RENDER==true && search(CHAR_LAT_LONG[i][0], SELECTIVE_RENDER_CHARS)!= [])
    SingleMinkowski(CHAR_LAT_LONG[i][0]);
    else if (SELECTIVE_RENDER==true && search(CHAR_LAT_LONG[i][0], SELECTIVE_RENDER_CHARS)== []) {}
    else
    SingleMinkowski(CHAR_LAT_LONG[i][0]);
}

//subtractive parts
module SolidCleanup(){
    //form flat top
    translate([0, 0, TOPFLAT_TO_CENTER])
    cylinder(d=26, h=10);
    //center shaft
    cylinder(d=SHAFT_ID, h=40, center=true, $fn=cyl_fn);
    //inside radius
    translate([0, 0, -20])
    cylinder(d=INSIDE_ID, h=20+TOPFLAT_TO_CENTER-BOSS_H, $fn=surface_fn);
    HollowProfile();
    Notch();
    rotate([0, 0, DETENT_SKIRT_CLOCK_OFFSET])
    Teeth();
}

//subtractive parts - inner radius
module HollowProfile(){
    rotate_extrude($fn=surface_fn)
    hull(){
        translate([-HOLLOW_R+INSIDE_R, TOPFLAT_TO_CENTER-BOSS_H, 0])
        scale([1, 2])
        circle(r=HOLLOW_R);
        translate([BOSS_R+HOLLOW_R, TOPFLAT_TO_CENTER-BOSS_H, 0])
        scale([1, 2])
        circle(r=HOLLOW_R);
    }
}

module Tooth(){
    translate([0, DETENT_VALLEY_TO_CENTER, -FLOOR-z])
    rotate([180, -90, 0])
    {
        // notch between teeth must be big enough to trap detent
        linear_extrude(30)
        polygon(points=[[0,1.9], [2.2,0.4], [3.2,0.14], [3.2, -0.14], [2.2, -0.4], [0,-1.9]]);
    }
}

module Teeth(){
    for (i=[0:22-1])
    rotate([0, 0, i*LATITUDE_SPACING])
    Tooth();
}


module Notch(){
    rotate([0, 0, DRIVE_NOTCH_THETA])
    translate([SHAFT_ID/2-.5, -DRIVE_NOTCH_WIDTH/2, TOPFLAT_TO_CENTER-BOSS_H-z])
    cube([4, DRIVE_NOTCH_WIDTH, DRIVE_NOTCH_HEIGHT+z]);
}

//full body minus subtractive parts
module SubtractFromFull(){
    difference(){
        FullBody();
        SolidCleanup();
    }
}

module ResinRod(p1, theta){
    hull(){
        //sphere
    }
}

Render();

