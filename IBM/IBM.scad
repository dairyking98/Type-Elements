//dairy's rendition of ibm selectric type element model
//Leonard Chau      November 4, 2024       t(-.-t)

/* [Global Parameters] */
z=.001;
$fn=180;
mink_fn=20;

/* [Rendering] */
//render something?
RENDER=false;
//render selection?
RENDER_MODE=0;//[0:Composer Element]
//render variant?
RENDER_VARIANT=0;//[0:plain, 1:resin print]
//turn on minkowski?
MINK_ON=false;

/* [Typeface Stuff] */
FONT="Arial";
FONTSIZE=3;
FONT_WEIGHT_OFFSET=0;//.01
X_WEIGHT_ADJUSTMENT=.01;
Y_WEIGHT_ADJUSTMENT=.01;
X_POS_OFFSET=1;
Y_POS_OFFSET=-1;


/* [Typeball Dimensions] */
//sphere diameter
SPHERE_OD=33.4;
//character-concave to character-concave diameter
MAX_OD=34.9;
//sphere center to top flat
TOPFLAT_TO_CENTER=11.4;
//shaft ID
SHAFT_ID=28.15;
//shaft boss height
BOSS_H=8.07;
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

CASES88=[LOWER_CASE_COMPOSER,UPPER_CASE_COMPOSER];

//type element mapping starting at arrow, moving clockwise from the top, from top to bottom
ELEMENTMAP88="
s10928’‘/+$S!()†*.,634

iatb75¾_½CLIATB&%?-[cl

nrodwkXVUMHNRODWKxvumh

efgq;j@¼ZPYEFGQ:J=]zpy
";

//array for character, latitude integer, and longitude integer
CHAR_LAT_LONG=[for (i=[0:1]) for (j=[0:len(CASES88[0])-1]) 

    [CASES88[i][j], ceil(search(CASES88[i][j], str(ELEMENTMAP88))[0]/22+.001)-1, search(CASES88[i][j], str(ELEMENTMAP88))[0]%22]

];


echo(CHAR_LAT_LONG);






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



//make solid element
module FullBody(){
union(){
    sphere(d=SPHERE_OD);
    translate([0, 0, -FLOOR])
    cylinder(d1=SKIRT_BOTTOM_OD, d2=SKIRT_TOP_OD, h=FLOOR-CENTER_TO_SKIRT);
    }
}

module Text(char){
    offset(FONT_WEIGHT_OFFSET)
    minkowski(){
        translate([X_POS_OFFSET, Y_POS_OFFSET, 0])
        mirror([1, 0, 0])
        text(char, size=FONTSIZE, font=FONT, valign="baseline", halign="left");
        square([z+X_WEIGHT_ADJUSTMENT, z+Y_WEIGHT_ADJUSTMENT], center=true);
    }
}

module PlatenCutout(char){
            rotate([0, -GetLong(char), GetLat(char)])
            translate([SPHERE_R+PLATEN_R+TYPE_ALTITUDE, 0, 0])
            rotate([90, 0, 0])
            cylinder(d=PLATEN_OD, h=10, center=true);
}

module PositionText(char){
    rotate([90 - GetLong(char), 0, 90 + GetLat(char)])
    translate([0, 0, SPHERE_R-2])
    linear_extrude(6)
    Text(char);
}

module Render(){
    if (RENDER==true){
        FullBody();
    }
}

function GetLat(char)= CHAR_LAT_LONG[search(char, CHAR_LAT_LONG)[0]][2]*LATITUDE_SPACING;

function GetLong(char)= LONGITUDE_SPACING[CHAR_LAT_LONG[search(char, CHAR_LAT_LONG)[0]][1]];

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



Render();
SingleMinkowski("n");

//PlatenCutout(0, 2);