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
RENDER_VARIANT=0;//[0:plain, 1:resin print top up, 2:type test, 3:resin print top down]
//turn on minkowski?
MINK_ON=false;
//minkowski draft angle
MINKOWSKI_ANGLE=85;//.5
//minkowski bottom radius size
MINK_TEXT_R=2*tan(.5*MINKOWSKI_ANGLE);
//cross section?
XSECTION=false;
//cross section angle?
XSECTION_THETA=0;



/* [Testing Stuff] */
//whitelist render of characters?
SELECTIVE_RENDER=false;
//whitelisted characters to render?
SELECTIVE_RENDER_CHARS="sine";
//enable rays?
RAYS=false;

//character and point array for type testing composer
COMPOSER_PITCH_LIST=[

    ["M", 9], ["W", 9], ["m", 9],
    
    ["A", 8], ["D", 8], ["G", 8], ["H", 8], ["K", 8], ["N", 8], ["O", 8], ["Q", 8], ["R", 8], ["U", 8], ["V", 8], ["X", 8], ["Y", 8], ["w", 8], ["¾", 8], ["½", 8], ["&", 8], ["%", 8], ["@", 8], ["¼", 8], ["–", 8], ["Ö", 8], ["Ä", 8], ["Å", 8], ["Ü", 8], ["Ñ", 8], ["¨", 8], ["`", 8], ["Ø", 8],
    
    ["B", 7], ["C", 7], ["E", 7], ["F", 7], ["L", 7], ["T", 7], ["Z", 7],
    
    ["P", 6], ["S", 6], ["b", 6], ["d", 6], ["h", 6], ["k", 6], ["n", 6], ["o", 6], ["p", 6], ["q", 6], ["u", 6], ["x", 6], ["y", 6], ["*", 6], ["†", 6], ["$", 6], ["+", 6], ["=", 6], ["0", 6], ["1", 6], ["2", 6], ["3", 6], ["4", 6], ["5", 6], ["6", 6], ["7", 6], ["8", 6], ["9", 6], ["]", 6], ["ñ", 6], ["ø", 6], ["ü", 6], ["ß", 6], ["¡", 6], ["¿", 6], ["ö", 6], ["£", 6], ["§", 6],
    
    ["J", 5], ["a", 5], ["c", 5], ["e", 5], ["g", 5], ["v", 5], ["?", 5], ["[", 5], ["z", 5], ["ˆ", 5], ["´", 5], ["ü", 5], ["ö", 5], ["ä", 5], ["å", 5], ["ç", 5],
    
    ["I", 4], ["f", 4], ["r", 4], ["s", 4], ["t", 4], [":", 4], ["(", 4], [")", 4], ["!", 4], ["/", 4], ["(", 4], ["ı", 4], ["Æ", 4],["»", 4],
    
    ["i", 3], ["j", 3], ["l", 3], [".", 3], [",", 3], [";", 3], ["’", 3], ["‘", 3], ["-", 3], ["'", 3], ["æ", 3], [" ", 3]//apostrophe not native to Composer

];


//make an element with varying platen cutouts?
CUTOUT_TEST=false;
//interval of angle offsets to test
CUTOUT_TEST_ANGLE_INT=.1;
//CUTOUT_TEST_ANGLE_ARRAY_MAP=[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -11, -10, -9, -8, -7, -6];
CUTOUT_TEST_ANGLE_ARRAY_MAP=[-17, -18, -19, -20, -21, 0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -12, -14, -15, -16];
CUTOUT_TEST_ANGLE_ARRAY=[for (i=[0:21]) CUTOUT_TEST_ANGLE_ARRAY_MAP[i]*CUTOUT_TEST_ANGLE_INT];


/* [Typeface Stuff] */

//Composer Language preset
COMPOSER_LANGUAGE="US";//[US:United States,UK:United Kingdom,NO:Nordic,DE:German,LA:Latin]
//element typeface
FONT="Arial";
//selectric I/II type size
FONT_SIZE=2.4;//.05
// Composer font Cap Height in points, use instead of FONT_SIZE!
COMPOSER_CAP_HEIGHT=7;
//all font sizes
ALLFONTSIZES=[COMPOSER_CAP_HEIGHT/2.834, FONT_SIZE];
//global font size
FONTSIZE=ALLFONTSIZES[RENDER_MODE];
//secondary element typeface
FONT2="Times New Roman";
//secondary type size
FONT2_SIZE=2.4;//.05
// Composer font 2 Cap Height in points, use instead of FONT_SIZE!
COMPOSER2_CAP_HEIGHT=7;
//all font2 sizes
ALLFONT2SIZES=[COMPOSER2_CAP_HEIGHT/2.834, FONT2_SIZE];
//global font2 size
FONT2SIZE=ALLFONT2SIZES[RENDER_MODE];
//list of chars to adopt font2 parameters
FONT2CHARS="";
//custom horizontal alignment characters
CUSTOMHALIGNCHARS="";
//custom horizontal alignment characters offset. -left +right
CUSTOMHALIGNOFFSET=0.2;
//custom vertical alignment characters
CUSTOMVALIGNCHARS="";
//custom vertical alignment characters offset
CUSTOMVALIGNOFFSET=-0.2;
//type weight offset +/-
FONT_WEIGHT_OFFSET=0;//.01
//x weight adjustment 0+
X_WEIGHT_ADJUSTMENT=.0;//.01
//y weight adjustment 0+
Y_WEIGHT_ADJUSTMENT=.0;//.01
//x horiz alignment offset for composer
X_POS_OFFSET_COMPOSER_=1.20;
X_POS_OFFSET_COMPOSER=CUTOUT_TEST==false?X_POS_OFFSET_COMPOSER_:0;//.01
//y vert alignment offset for composer
Y_POS_OFFSET_COMPOSER=-1.30;//1.01;//.01
//x horiz alignment offset for selectric 1/2
X_POS_OFFSET_S12=0;//.01
//y vert alignment offset for selectric 1/2
Y_POS_OFFSET_S12=-1.5;
//all y offsets
ALLYOFFSETS=[Y_POS_OFFSET_COMPOSER, Y_POS_OFFSET_S12];
//all x offsets
ALLXOFFSETS=[X_POS_OFFSET_COMPOSER, X_POS_OFFSET_S12];
//global y offset
Y_POS_OFFSET=ALLYOFFSETS[RENDER_MODE];
//global x offset
X_POS_OFFSET=ALLXOFFSETS[RENDER_MODE];
//all h alignments
ALLHALIGNMENTS=["left", "center"];
//h alignment 
H_ALIGNMENT=CUTOUT_TEST==true?"center":ALLHALIGNMENTS[RENDER_MODE];

/* [ Type Testing Stuff] */

//Type test text color
TYPE_TEST_COLOR="red";//["red","black","white"]

//Use custom test string?
CUSTOM_TEST_STRING=false;

//custom string for type test
TESTSTRING_CUSTOM="1234567890-=qwertyuiop?asdfghjkl][zxcvbnm,.;!†+$%/&*()–@QWERTYUIOP¾ASDFGHJKL¼½ZXCVBNM‘’:";

//US
TESTARRAY_US =[
"1234567890-=",
"qwertyuiop?",
"asdfghjkl][",
"zxcvbnm,.;", 
"!†+$%/&*()–@",
"QWERTYUIOP¾",
"ASDFGHJKL¼½",
"ZXCVBNM‘’:
"];

//UK
TESTARRAY_UK =[
"1234567890-=",
"qwertyuiop?",
"asdfghjkl][",
"zxcvbnm,.;",
"!†+£%/&*()–@",
"QWERTYUIOP¾",
"ASDFGHJKL¼½",
"ZXCVBNM‘’:"
];

//Nordic
TESTARRAY_NO =[
"1234567890-ø",
"qwertyuiopå",
"asdfghjklöä",
"zxcvbnm,.;",
"»!?§%/&=()–Ø",
"QWERTYUIOPÅ",
"ASDFGHJKLÖÄ",
"ZXCVBNM‘’:"
];

//Germany
TESTARRAY_DE =[
"1234567890-ß",
"qwertyuiopü",
"asdfghjklöä",
"zxcvbnm,.;",
"!=+§%/&*()–?",
"QWERTYUIOPÜ",
"ASDFGHJKLÖÄ",
"ZXCVBNM‘’:"
];


//Latin/French
TESTARRAY_LA =[
"1234567890-ñ",
"qwertyuiopˆ",
"asdfghjkl´ç",
"zxcvbnm,.;",
"ı¿¡$!/&*()–Ñ",
"QWERTYUIOP¨",
"ASDFGHJKL`?",
"ZXCVBNM‘’:"
];


//Match test array to Composer Language unless custom is checked.
TESTARRAY=
    (CUSTOM_TEST_STRING==true)  ? [TESTSTRING_CUSTOM]:
    (COMPOSER_LANGUAGE=="US")   ? TESTARRAY_US:
    (COMPOSER_LANGUAGE=="UK")   ? TESTARRAY_UK:
    (COMPOSER_LANGUAGE=="NO")   ? TESTARRAY_NO:
    (COMPOSER_LANGUAGE=="DE")   ? TESTARRAY_DE:
    (COMPOSER_LANGUAGE=="LA")   ? TESTARRAY_LA:
    TESTARRAY_US;               //fallback default to US


//TESTARRAYS=[[TESTSTRING_CUSTOM], TESTARRAY_88KBLAYOUT];//, TESTSTRING_COMPOSERKB];

//preset for type testing strings?
//TESTSTRING_SELECTION=0;//[0:Custom, 1:Composer Keyboard US,2:Composer Keyboard UK,3:Composer Keyboard Nordic,4:Composer Keyboard German,5:Composer Keyboard Latin ]

//TESTARRAY=TESTARRAYS[TESTSTRING_SELECTION];

//composer picas per character array
//TESTSTRINGPICAS = [0, for ( i = [0:len(TESTSTRING)-1] ) COMPOSER_PITCH_LIST[search(TESTSTRING[i], COMPOSER_PITCH_LIST)[0]][1]];
//cumulative sum vector function for composer type test pitch array
function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec)-1; newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];
//composer cumulative picas per character array
//CUMULATIVETESTSTRINGPICAS = cumulativeSum(TESTSTRINGPICAS);
//cpi spacing for type test of selectric I/II
TESTCPI=10;
//unit spacing for type test of Composer
UNITSPERINCH=72;//[72:Red (12Units/Pica  72 Units/in), 84:Yellow (14Units/Pica  84 Units/in), 96:Blue (16 Units/Pica  96 Units/in)]
//mm distance per composer unit
UNITDIST=25.4/UNITSPERINCH;


/* [Typeball Dimensions] */

//sphere diameter
SPHERE_OD=33.4;
//sphere radius
SPHERE_R=SPHERE_OD/2;
//character-concave to character-concave diameter
MAX_OD=34.9;
//sphere center to top flat
TOPFLAT_TO_CENTER=11.0;//leo's measured value. dave's was was 11.4;
//thickness of top flat
TOPFLAT_THICKNESS=3;
//shaft ID
SHAFT_ID=8.8;
//shaft r
SHAFT_R=SHAFT_ID/2;
//top shaft chamfer
TOP_CHAMFER=.7;
//inside ID
INSIDE_ID=28.15;
//calculated calue of sphere center to boss face
BOSS_TO_CENTER_=2.5;//leo's calculated value. dave's was 2.38 (calculated);

//shaft boss height
//BOSS_H=8.62;//was 8.07; now redundant replaced by BOSS_TO_CENTER

echo("Top flat to boss face must measure at 8.5mm (Leo's measured value) or element is incorrectly represented. Adjust SNOOT_DROOP_COMPENSATION up,lowering height of boss, until print yields 8.5mm boss height.");

//dave's top flat to boss face/BOSS_HEIGHT/BOSS_H was 8.07

//top flat radius
TOPFLAT_R=(SPHERE_R^2-TOPFLAT_TO_CENTER^2)^.5;
//center to detent teeth tips of element
FLOOR=10.7;//abs(TOPFLAT_TO_CENTER-ELEMENT_OAT) = 10.7;
//boss OD
BOSS_OD=11.6;
//boss minimum clearange
BOSS_CLEARANCE=2.5;//.1
//boss step thicknesss
BOSS_STEP=1;//.1
//skirt top OD
SKIRT_TOP_OD=32.3;
//skirt bottom OD
SKIRT_BOTTOM_OD=30.2;
//overall thickness of element
echo(str(FLOOR+TOPFLAT_TO_CENTER, " (modeled) = 21.7 (measured)? Leo's measured overall thickness?"));
//ELEMENT_OAT=21.7;//leo's measured value. dave's was 22.0; 
//now redundant - FLOOR + CENTER_TO_TOP = OAT
//angle between characters
LATITUDE_SPACING=360/22;
//angle between rows
LONGITUDE_SPACING=[32.8, 16.4, 0, -16.4];
//platen diameter
PLATEN_OD=40;
//radius of hollow section
HOLLOW_R=2;
//drive notch width
DRIVE_NOTCH_WIDTH=1.12;//.01
//drive notch height
DRIVE_NOTCH_HEIGHT=2.2;
//drive notch theta from arrow
DRIVE_NOTCH_THETA_=131.0;//.01
//detent valley from center
DETENT_VALLEY_TO_CENTER=6;
//detent teeth clock offset
DETENT_SKIRT_CLOCK_OFFSET=0;//.01

/* [Label Stuff] */

//Enable label
LABEL=true;
//Enable arrow
ARROW=true;
//Label for number label. Disabled in Composer mode
LABEL_NO = "10";
//Label override for typeface label (leave blank to adopt font name)
LABEL_TEXT_OVERRIDE="";
//Font override for number label (leave blank to adopt element typeface)
LABEL_NO_FONT_OVERRIDE="";
//Font override for typeface label (leave blank to adopt element typeface)
LABEL_FONT_OVERRIDE="";
//Font size for number label
NO_LABEL_SIZE=2;
//Vertical offset for number label. +up -down
NO_LABEL_OFFSET=0;//0.25
//Font size for typeface label 
FONT_LABEL_SIZE=2;
//Vertical offset for font label. +up -down
FONT_LABEL_OFFSET=0;//0.25
//arrow from center 
DEL_BASE_FROM_CENTRE = 8.2;
//depth of arrow
DEL_DEPTH = 0.6;

/* [Character Polar Positioning Offsets] */

//individual platen cutout adjustment angles
PLATEN_LONGITUDE_OFFSETS=[-1.5, -1.5, -0.75, -0.5];//.05
//individual baseline adjustment angles
BASELINE_LONGITUDE_OFFSETS=[0, 0, 0, 0];//.05




//SOME CALCULATED VARIABLES:

//skirt large radius
SKIRT_TOP_R=SKIRT_TOP_OD/2;
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
//center to roof of element
ROOF=TOPFLAT_TO_CENTER-TOPFLAT_THICKNESS;

/* [Character Mapping - Custom 88char] */

//use custom keyboard layout?
CUSTOM=false;

//lowercase layout for custom keyboard
CUSTOMLOWERCASE88="

||||||||||||
|||||||||||
|||||||||||
||||||||||

";

//uppercase layout for custom keyboard
CUSTOMUPPERCASE88="

||||||||||||
|||||||||||
|||||||||||
||||||||||

";

//custom 88 layout array
CUSTOMCASES88=[CUSTOMLOWERCASE88, CUSTOMUPPERCASE88];

/* [Character Mapping - Selectric I/II 88char] */

//lowercase selectric 1/2 layout on machine; left to right, top to bottom
LOWERCASE88="
1234567890-=
qwertyuiop½
asdfghjkl;'
zxcvbnm,./
";

//uppercase selectric 1/2 layout on machine; left to right, top to bottom
UPPERCASE88="
!@#$%¢&*()_+
QWERTYUIOP¼
ASDFGHJKL:\"
ZXCVBNM,.?
";

//selectric 1/2 layout array
S12CASES88=[LOWERCASE88, UPPERCASE88];

//lowercase hemisphere of selectric 1/2 element from the top moving counter clockwise, top to bottom
S12_LC_HEMISPHERE88="
90652z48731
bhkentlcdux
wsi'.½oarvm
-yqp=j/,;fg
";


//SELECTRIC 3 STUFF I AM NOT WORRYING ABOUT FOR THE TIME BEING
////lowercase selectric 3 layout on machine; left to right, top to bottom
//LOWERCASE96="
//±1234567890-=
//qwertyuiop½[
//ASDFGHJKL;'
//ZXCVBNM,./
//";
//
////uppercase selectric 3 layout on machine; left to right, top to bottom
//UPPERCASE96="
//°!@#$%¢&*()_+
//QWERTYUIOP¼]
//ASDFGHJKL:\"
//ZXCVBNM.,?
//";
//
//
//S3CASES96=[LOWERCASE96, UPPERCASE96];


//lowercase hemisphere of selectric 3 element from the top moving counter clockwise, top to bottom
//S3_LC_HEMISPHERE96="
//z2752064893/
//;'istecbku§=
//vmwdornaxh½±
//-1.jpqyflg],
//";

/* [Character Mapping - Composer 88char] */

//uppercase composer layout on machine; left to right, top to bottom
LOWERCASECOMPOSER_US ="
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
";

//lowercase composer layout on machine; left to right, top to bottom

//United States
UPPERCASECOMPOSER_US ="
!†+$%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
";

//United Kingdom
LOWERCASECOMPOSER_UK ="
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
";

UPPERCASECOMPOSER_UK ="
!†+£%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
";

//Nordic
LOWERCASECOMPOSER_NO ="
1234567890-ø
qwertyuiopå
asdfghjklöä
zxcvbnm,.;
";

UPPERCASECOMPOSER_NO ="
»!?§%/&=()–Ø
QWERTYUIOPÅ
ASDFGHJKLÖÄ
ZXCVBNM‘’:
";

//Germany
LOWERCASECOMPOSER_DE ="
1234567890-ß
qwertyuiopü
asdfghjklöä
zxcvbnm,.;
";

UPPERCASECOMPOSER_DE ="
!=+§%/&*()–?
QWERTYUIOPÜ
ASDFGHJKLÖÄ
ZXCVBNM‘’:
";


//Latin/French
LOWERCASECOMPOSER_LA ="
1234567890-ñ
qwertyuiopˆ
asdfghjkl´ç
zxcvbnm,.;
";

UPPERCASECOMPOSER_LA ="
ı¿¡$!/&*()–Ñ
QWERTYUIOP¨
ASDFGHJKL`?
ZXCVBNM‘’:
";


US=[LOWERCASECOMPOSER_US,UPPERCASECOMPOSER_US];
UK=[LOWERCASECOMPOSER_UK,UPPERCASECOMPOSER_UK];
NO=[LOWERCASECOMPOSER_NO,UPPERCASECOMPOSER_NO];
DE=[LOWERCASECOMPOSER_DE,UPPERCASECOMPOSER_DE];
LA=[LOWERCASECOMPOSER_LA,UPPERCASECOMPOSER_LA];

COMPOSERCASES88=
    (COMPOSER_LANGUAGE=="US") ? US:
    (COMPOSER_LANGUAGE=="UK") ? UK:
    (COMPOSER_LANGUAGE=="NO") ? NO:
    (COMPOSER_LANGUAGE=="DE") ? DE:
    (COMPOSER_LANGUAGE=="LA") ? LA:
    US; //fallback default to US
    
//lowercase hemisphere of composer element from the top moving counter clockwise, top to bottom
COMPOSER_LC_HEMISPHERE_US="
.,634s10928
?-[cliatb75
xvumhnrodwk
=]zpyefgq;j
";

COMPOSER_LC_HEMISPHERE_UK="
.,634s10928
?-[cliatb75
xvumhnrodwk
=]zpyefgq;j
";

COMPOSER_LC_HEMISPHERE_NO="
.,634s10928
å-äcliatb75
xvumhnrodwk
øözpyefgq;j
";

COMPOSER_LC_HEMISPHERE_DE="
.,634s10928
ü-äcliatb75
xvumhnrodwk
ßözpyefgq;j
";

COMPOSER_LC_HEMISPHERE_LA="
.,634s10928
ˆ-çcliatb75
xvumhnrodwk
ñ´zpyefgq;j
";

COMPOSER_LC_HEMISPHERE88=
    (COMPOSER_LANGUAGE=="UK") ? COMPOSER_LC_HEMISPHERE_UK:
    (COMPOSER_LANGUAGE=="US") ? COMPOSER_LC_HEMISPHERE_US:
    (COMPOSER_LANGUAGE=="NO") ? COMPOSER_LC_HEMISPHERE_NO:
    (COMPOSER_LANGUAGE=="DE") ? COMPOSER_LC_HEMISPHERE_DE:
    (COMPOSER_LANGUAGE=="LA") ? COMPOSER_LC_HEMISPHERE_LA:
    COMPOSER_LC_HEMISPHERE_US; //fallback default to US

//composer layout array
//COMPOSERCASES88=[LOWERCASECOMPOSER88,UPPERCASECOMPOSER88];



//all keyboard layouts
ALL88CASES=[COMPOSERCASES88, S12CASES88];

//all hemisphere layouts
ALL88HEMIS=[COMPOSER_LC_HEMISPHERE88, S12_LC_HEMISPHERE88];



//set keyboard layout for character mapping
CASES88=ALL88CASES[RENDER_MODE];

//set lowercase hemisphere 
LC_HEMISPHERE88=ALL88HEMIS[RENDER_MODE];

//create lowercase layout to element hemisphere map
LC_LAYOUT_TO_HEMISPHERE_MAP = [for (i=[0:len(CASES88[0])-1]) search(CASES88[0][i], LC_HEMISPHERE88)];

//create latitude, longitude integer array for one hemisphere
LATITUDE_LONGITUDE = [for (i=[0:len(LC_LAYOUT_TO_HEMISPHERE_MAP)-1]) [LC_LAYOUT_TO_HEMISPHERE_MAP[i][0]%11, ceil(LC_LAYOUT_TO_HEMISPHERE_MAP[i][0]/11+.001)-1, CASES88[0][i], i]];



/* [Resin Printing Offsets] */
//amount to compensate for vat-facing boss face !CRITICAL FEATURE!
SNOOT_DROOP_COMPENSATION=.52;
//modeled boss to center value
BOSS_TO_CENTER=BOSS_TO_CENTER_+SNOOT_DROOP_COMPENSATION;

/* [Resin Supports] */

//tip diameter
TIP_D=.8;
//notch tip diameter
TIP_NOTCHD=.5;
//deg offset from notch for notch supports
TIP_NOTCHOFFSET=12;
//tip inset
TIP_IN=.4;
//tip height
TIP_H=1;
//rod diameter
ROD_D=1.2;
//rod radius
ROD_R=ROD_D/2;
//base diameter on buildplate
BASE_D=4;
//base thickness
BASE_H=2;
//minimum support height
MIN_ROD_H=2;

/* [Experimental Web] */

//web? disables label if checked
WEB=false;
//web ID
WEB_ID=BOSS_OD+1;
//web inner corner R
WEB_IR=1;
//web outer corner R
WEB_OR=2;
//web OD
WEB_OD=TOPFLAT_R*2-2;



//rays
module Rays(){
    for (lat=[0:21])
    for (long=[0:3])
    rotate([0, LONGITUDE_SPACING[long], lat*LATITUDE_SPACING])
    rotate([0, 90, 0])
    #cylinder(r=.1, h=20);
}

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
module Text(char, font, size, customhalign, customvalign){
    $fn = mink_fn;
    offset(FONT_WEIGHT_OFFSET)
    minkowski(){
        translate([X_POS_OFFSET-customhalign, Y_POS_OFFSET+customvalign, 0])
        mirror([1, 0, 0])
        text(char, size=size, font=font, valign="baseline", halign=H_ALIGNMENT, $fn=text_fn);
        if (X_WEIGHT_ADJUSTMENT>0 || Y_WEIGHT_ADJUSTMENT>0)
        square([z+X_WEIGHT_ADJUSTMENT, z+Y_WEIGHT_ADJUSTMENT], center=true);
    }
}

//platen cutout
module PlatenCutout(latitude, longitude){
            rotate([0, -longitude, latitude])
            translate([SPHERE_R+PLATEN_R+TYPE_ALTITUDE, 0, 0])
            rotate([90, 0, 0])
            cylinder(d=PLATEN_OD, h=10, center=true, $fn=cyl_fn);
}

//position extruded character
module PositionText(latitude, longitude){
    rotate([90 - longitude, 0, 90 + latitude])
    translate([0, 0, SPHERE_R+z])
    children();
//    linear_extrude(6)
//    Text(char);
}

//minkowski single character
module SingleMinkowski(char, font, size, customhalign, customvalign, latitude, longitude, plat_offset, base_offset){
    minkowski(){
        difference(){
            PositionText(latitude, longitude+base_offset)
            linear_extrude(6)
            Text(char, font, size, customhalign, customvalign);
            PlatenCutout(latitude, longitude+plat_offset);
            
        }
        if (MINK_ON==true){
            rotate([90 - longitude, 0, 90 + latitude])
            translate([0, 0, -2])
            cylinder(r1=MINK_TEXT_R, d2=0, h=2, $fn=mink_fn);
        }
    }
}


//assemble minkowski characters
module AssembleMinkowski(){
    rotate([0, 0, -5*LATITUDE_SPACING])
    for (case_int=[0:1])
    for (hemi_int=[0:43]){
    
        char=CUSTOM==true?CUSTOMCASES88[case_int][hemi_int]:CASES88[case_int][hemi_int];
        compkbchar=COMPOSERCASES88[case_int][hemi_int];
        latitude=LATITUDE_LONGITUDE[hemi_int][0]*LATITUDE_SPACING+case_int*180;
        longitude=LONGITUDE_SPACING[LATITUDE_LONGITUDE[hemi_int][1]];
        plat_offset_test=CUTOUT_TEST==true?CUTOUT_TEST_ANGLE_ARRAY[latitude/LATITUDE_SPACING]:0;
        
        if (CUTOUT_TEST==true){
            echo (str("composer keyboard char = ", compkbchar, " , element row = ", LATITUDE_LONGITUDE[hemi_int][1], " (0=top, 3=bottom), platen cutout offset = ", plat_offset_test, " degrees"));
        }
            
        plat_offset=PLATEN_LONGITUDE_OFFSETS[LATITUDE_LONGITUDE[hemi_int][1]];
        base_offset=BASELINE_LONGITUDE_OFFSETS[LATITUDE_LONGITUDE[hemi_int][1]];
        font=search(char, FONT2CHARS)==[]?FONT:FONT2;
        size=search(char, FONT2CHARS)==[]?FONTSIZE:FONT2SIZE;
        customhalign=search(char, CUSTOMHALIGNCHARS)==[]?0:CUSTOMHALIGNOFFSET;
        customvalign=search(char, CUSTOMVALIGNCHARS)==[]?0:CUSTOMVALIGNOFFSET;
        
        if (SELECTIVE_RENDER==true && search(char, SELECTIVE_RENDER_CHARS)!= [])
        SingleMinkowski(char, font, size, customhalign, customvalign, latitude, longitude, plat_offset+plat_offset_test, base_offset);
        
        else if (SELECTIVE_RENDER==true && search(char, SELECTIVE_RENDER_CHARS)== []) {}
        
        else
        SingleMinkowski(char, font, size, customhalign, customvalign, latitude, longitude, plat_offset+plat_offset_test, base_offset);
    }
}




//subtractive parts
module SolidCleanup(){
    //top flat
    translate([0, 0, TOPFLAT_TO_CENTER])
    cylinder(r=TOPFLAT_R+2, h=10);
    //center shaft
    cylinder(d=SHAFT_ID, h=40, center=true, $fn=cyl_fn);
    //center shaft top chamfer
    translate([0, 0, TOPFLAT_TO_CENTER-TOP_CHAMFER])
    cylinder(d1=SHAFT_ID, d2=SHAFT_ID+2*TOP_CHAMFER, h=TOP_CHAMFER, $fn=surface_fn);
    //inside radius
    translate([0, 0, -20])
    cylinder(d=INSIDE_ID, h=20+BOSS_TO_CENTER, $fn=surface_fn);
    //roof ish area
    rotate_extrude($fn=surface_fn)
    HollowProfile3();
    //notch
    Notch();
    //detent teeth
    rotate([0, 0, DETENT_SKIRT_CLOCK_OFFSET])
    Teeth();
    //web
    if (WEB==true)
    ArrangeWeb();
    if (WEB==false){
        if (ARROW==true)
        Del();
        if (LABEL==true)
        FontName();}
}
////subtractive parts - inner radius
//module HollowProfile(){
//    hull(){
//        translate([-HOLLOW_R+INSIDE_R, TOPFLAT_TO_CENTER-TOPFLAT_THICKNESS-2*HOLLOW_R, 0])
//        scale([1, 2])
//        circle(r=HOLLOW_R);
//        translate([BOSS_R, 0, 0])
//        square(1);
//        translate([BOSS_R+HOLLOW_R*2, TOPFLAT_TO_CENTER-TOPFLAT_THICKNESS-HOLLOW_R, 0])
//        scale([2, 1])
//        circle(r=HOLLOW_R);
//
//    }
//}
//
//
////subtractive parts - inner radius : experimental
//module HollowProfile2(){
//    newroofr=1;
//    hull(){
//        translate([-newroofr+INSIDE_R, BOSS_TO_CENTER+BOSS_CLEARANCE, 0])
//        circle(r=newroofr);
//        translate([BOSS_R, 0, 0])
//        square([INSIDE_R-BOSS_R, 1]);
//        translate([BOSS_R+newroofr, BOSS_TO_CENTER+BOSS_CLEARANCE, 0])
//        circle(r=newroofr);
//        translate([(INSIDE_R+BOSS_R)/2, TOPFLAT_TO_CENTER-TOPFLAT_THICKNESS-newroofr])
//        circle(r=newroofr);
//
//    }
//}

//subtractive parts - inner radius : experimental
module HollowProfile3(){
    newroofr=1;
    hull(){
        translate([-newroofr+INSIDE_R, BOSS_TO_CENTER+BOSS_CLEARANCE, 0])
        circle(r=newroofr);
        translate([BOSS_R+BOSS_STEP, 0, 0])
        square([INSIDE_R-BOSS_R-BOSS_STEP, 1]);
        translate([BOSS_R+newroofr+BOSS_STEP, BOSS_TO_CENTER+BOSS_CLEARANCE, 0])
        circle(r=newroofr);
        translate([(INSIDE_R+BOSS_R+BOSS_STEP)/2, TOPFLAT_TO_CENTER-TOPFLAT_THICKNESS-newroofr])
        circle(r=newroofr);

    }
    
    translate([BOSS_R, 0, 0])
    square([BOSS_STEP+z, BOSS_TO_CENTER+BOSS_CLEARANCE]);
}

//detent tooth profile
module Tooth(){
    translate([0, DETENT_VALLEY_TO_CENTER, -FLOOR-z])
    rotate([180, -90, 0])
    {
        // notch between teeth must be big enough to trap detent
        linear_extrude(30)
        polygon(points=[[0,1.9], [2.2,0.4], [3.2,0.14], [3.2, -0.14], [2.2, -0.4], [0,-1.9]]);
    }
}

//detent teeth profile
module Teeth(){
    for (i=[0:22-1])
    rotate([0, 0, i*LATITUDE_SPACING])
    Tooth();
}

//drive notch
module Notch(){
    rotate([0, 0, DRIVE_NOTCH_THETA])
    translate([SHAFT_ID/2-.5, -DRIVE_NOTCH_WIDTH/2, BOSS_TO_CENTER-z])
    cube([4, DRIVE_NOTCH_WIDTH, DRIVE_NOTCH_HEIGHT+z]);
}

//full body minus subtractive parts
module SubtractFromFull(){
    difference(){
        FullBody();
        SolidCleanup();
    }
    
    if (RAYS==true)
    Rays();
}

//resin support tip, angle input, tip d
module ResinTip(a1,d){
    rotate([0, a1, 0])
    hull(){
        sphere(d=d);
        translate([0, 0, -TIP_H])
        sphere(d=ROD_D);
    }
}

//get rotated resin support tip x offset function
function ResinXOffset(a1)= sin(a1)*TIP_H;

//resin support rod, height, tip angle, tip diameter
module ResinRod(h, a1, d){
    xoffset = ResinXOffset(a1);
    translate([-xoffset, 0]){
        //base
        translate([0, 0, -MIN_ROD_H-BASE_H-TIP_H])
        cylinder(d1=BASE_D, d2=BASE_D+2*BASE_H, h=BASE_H);
        
        //rod
        hull(){
            translate([0, 0, -TIP_H+h-TIP_D/2+TIP_IN])
            sphere(d=ROD_D);
            translate([0, 0, -MIN_ROD_H-BASE_H+ROD_D/2-TIP_H])
            sphere(d=ROD_D);
        }
    }
    //tip
    translate([0, 0, h-TIP_D/2+TIP_IN])
    ResinTip(a1, d);
}

//assemble resin support rods
module ResinRodAssemble(){
    for (i=[0:22-1])
    
        //detent teeth supports
        rotate([0, 0, i*LATITUDE_SPACING+DETENT_SKIRT_CLOCK_OFFSET])
        translate([(SKIRT_BOTTOM_OD+INSIDE_ID)/4, 0, 0])
        ResinRod(0, 0, TIP_D);
    
    //boss supports
    for (i=[0:11]){
        rotate([0, 0, i*360/11]){
        
            //roof-roof support-supports
            hull(){
                    translate([(BOSS_R+INSIDE_R+BOSS_STEP)/2, 0, 6])
                    sphere(d=ROD_D);
                    rotate([0, 0, 360/11])
                    translate([(BOSS_R+INSIDE_R+BOSS_STEP)/2, 0, 0])
                    sphere(d=ROD_D);
            }
            
        if (i!=4){
        
            //boss supports (outer corner)
//            translate([BOSS_R, 0, 0])
//            ResinRod(FLOOR+BOSS_TO_CENTER, -45, TIP_D);
            
            //boss supports (directly under)
            translate([(BOSS_R+SHAFT_ID/2)/2, 0, 0])
            ResinRod(FLOOR+BOSS_TO_CENTER, 0, TIP_D);
            
            
            //boss-roof support-supports
            hull(){
//                translate([BOSS_R-ResinXOffset(-45), 0, 12])//couter corner
                translate([(BOSS_R+SHAFT_ID/2)/2, 0, 12])//directly under
                sphere(d=ROD_D);
                translate([(BOSS_R+INSIDE_R+BOSS_STEP)/2, 0, 8])
                sphere(d=ROD_D);
            }

            
            if (i!=3)
            //boss-boss support-supports
                hull(){
//                    translate([BOSS_R-ResinXOffset(-45), 0, 1])//outer corner
                    translate([(BOSS_R+SHAFT_ID/2)/2-ResinXOffset(0), 0, 1])//directly under
                    sphere(d=ROD_D);
                    rotate([0, 0, 360/11])
//                    translate([BOSS_R-ResinXOffset(-45), 0, 7])//outer corner
                    translate([(BOSS_R+SHAFT_ID/2)/2-ResinXOffset(0), 0, 7])//directly under
                    sphere(d=ROD_D);
                }
        }
        
        //roof supports
        translate([(BOSS_R+INSIDE_R+BOSS_STEP)/2, 0, 0])
        ResinRod(FLOOR+ROOF, 0, TIP_D);
        }
        
        
    //for notch supports
    n=TIP_NOTCHOFFSET;//degrees off from notch 
    l=[3, 5];
    k=[n, -n];
    if (i==4)
        for (j=[0, 1]){
            //notch supports
            rotate([0, 0, DRIVE_NOTCH_THETA+k[j]])
//            translate([BOSS_R, 0, 0])//outer corners
            translate([(BOSS_R+SHAFT_ID/2)/2, 0, 0])//directly under
            
            
//            ResinRod(FLOOR+BOSS_TO_CENTER, -45, TIP_NOTCHD);//outer corners
            ResinRod(FLOOR+BOSS_TO_CENTER, 0, TIP_NOTCHD);//directly under
            //notch support supports
            hull(){
                rotate([0, 0, DRIVE_NOTCH_THETA-k[j]])
//                translate([BOSS_R-ResinXOffset(-45), 0, 12])//outer corners
                translate([(BOSS_R+SHAFT_ID/2)/2-ResinXOffset(0), 0, 12])//directly under
                sphere(d=ROD_D);
                rotate([0, 0, l[j]*360/11])
//                translate([BOSS_R-ResinXOffset(-45), 0, 7])//outer corners
                translate([(BOSS_R+SHAFT_ID/2)/2-ResinXOffset(0), 0, 7])//directly under
                sphere(d=ROD_D);
            }
        }
    }
}

//assemble resin print
module ResinPrint(){
    union(){
    translate([0, 0 , FLOOR])
    SubtractFromFull();
    ResinRodAssemble();
    }
}

//assemble resin print 2
module ResinPrint2(){
    rotate([0, 180, 0])
    translate([0, 0 , -TOPFLAT_TO_CENTER])
    union(){
    SubtractFromFull();

    
    
    ResinRodAssemble2();
    }
}

module ResinRodAssemble2(){
    //outer top flat supports
    for (i=[0:21])
    rotate([0, 0, i*360/21])
    translate([TOPFLAT_R-TIP_D/2, 0, 0])
    ResinRod(0, 0, TIP_D);
        for (i=[0:21])
    rotate([0, 0, i*360/21+360/42])
    translate([(SHAFT_R+TOP_CHAMFER+TOPFLAT_R)/2, 0, 0])
    ResinRod(0, 0, TIP_D);
            for (i=[0:11])
    rotate([0, 0, i*360/11+360/22])
    translate([SHAFT_R+TOP_CHAMFER+TIP_D/2, 0, 0])
    ResinRod(0, 0, TIP_D);
}

//monospaced type test gauge
module TextGauge(str, pitch)
{
    color(TYPE_TEST_COLOR)
    for ( i = [0:len(str)] )
    {
        translate([8,8])
        translate([i*22/pitch, 0, 0])
        offset(FONT_WEIGHT_OFFSET)
        text(size=FONTSIZE, font=FONT, halign="center", str[i]);
    }
}

////composer type test gauge
//module TextGaugeComposer(str, unitdist)
//{
//
//    //color("red")
//    for ( i = [0:len(str)-1] )
//    {
//        font=search(str[i], FONT2CHARS)==[]?FONT:FONT2;
//        size=search(str[i], FONT2CHARS)==[]?FONTSIZE:FONT2SIZE;
//        translate([8,8])
//        translate([CUMULATIVETESTSTRINGPICAS[i]*unitdist,0])
//        offset(FONT_WEIGHT_OFFSET)
//        text(size=size, font=font, halign="left", str[i]);
//        //echo(CUMULATIVETESTSTRINGPICAS[i]);
//    }
//}


//2d web shape
module 2dWeb(){
hull(){
translate([WEB_ID/2+WEB_IR, 0, 0])
circle(r=WEB_IR);
translate([WEB_OD/2-WEB_OR, 0, 0])
circle(r=WEB_OR);
}
}

//extruded web hole
module ExtrudedWeb(){
    translate([0, 0, ROOF-3])
    linear_extrude(8)
    2dWeb();
    translate([0, 0, TOPFLAT_TO_CENTER-TOP_CHAMFER])
    hull(){
    linear_extrude(z)
    2dWeb();
    translate([0, 0, TOP_CHAMFER+z])
    linear_extrude(z)
    offset(TOP_CHAMFER)
    2dWeb();
    }
}

//web holes arranged
module ArrangeWeb(){
    for (i=[0:11])
    rotate([0, 0, i*360/11+360/22])
    ExtrudedWeb();
}

//render code
module Render(){
    if (RENDER==true){
        difference(){
            if (RENDER_VARIANT==0)
                SubtractFromFull();
            if (RENDER_VARIANT==1)
                ResinPrint();
            if (RENDER_VARIANT==2){
                if (RENDER_MODE==0)
                    ArrangeComposerLines(TESTARRAY);
                if (RENDER_MODE==1)
                    TextGauge(TESTSTRING_CUSTOM, TESTCPI);
            }
            if (RENDER_VARIANT==3)
                ResinPrint2();
            if (XSECTION==true && RENDER_VARIANT!=2)
            rotate([0, 0, XSECTION_THETA-90])
            translate([0, -50, -50])
            cube(100);
        }
    }
}

// Alignment marker triangle on top face
module Del()
{
    translate([DEL_BASE_FROM_CENTRE, 0, TOPFLAT_TO_CENTER - DEL_DEPTH])
    color("white")  // TODO red triangle for Composer typeball
    linear_extrude(DEL_DEPTH+z)
    polygon(points=[[3.4,0],[0.4,1.3],[0.4,-1.3]]);
}

// Emboss a label onto top face
module FontName()
{
    translate([-8.5, 0, TOPFLAT_TO_CENTER - DEL_DEPTH])
    rotate([0,0,270])
    linear_extrude(DEL_DEPTH+0.01)
    Labels();
}

// Labels on the top of the ball, cosmetic
module Labels()
{
    {
        // Disable Label No for Composer balls
        if (RENDER_MODE!=0) { 
            translate([-0.1+NO_LABEL_OFFSET,14,0])
        text(LABEL_NO, size=NO_LABEL_SIZE, font=LABEL_NO_FONT_OVERRIDE==""?FONT:LABEL_NO_FONT_OVERRIDE, halign="center");
    }
        translate([0,0.6+FONT_LABEL_OFFSET,0])
        text(LABEL_TEXT_OVERRIDE==""?FONT:LABEL_TEXT_OVERRIDE, size=FONT_LABEL_SIZE, font=LABEL_FONT_OVERRIDE==""?FONT:LABEL_FONT_OVERRIDE, halign="center");
        
    }
}

//create array of picas per test string character function
function TestStringPicas(string)=[0, for ( i = [0:len(string)-1] ) COMPOSER_PITCH_LIST[search(string[i], COMPOSER_PITCH_LIST)[0]][1]];

//composer type test gauge line with string input
module TextGaugeComposerLine(str, unitdist)
{
TESTSTRINGPICAS = TestStringPicas(str);
CUMSUMTESTSTRINGPICAS = cumulativeSum(TESTSTRINGPICAS);
    if(is_string(str)==true){
    color(TYPE_TEST_COLOR)
    for ( i = [0:len(str)-1] )
    {
        font=search(str[i], FONT2CHARS)==[]?FONT:FONT2;
        size=search(str[i], FONT2CHARS)==[]?FONTSIZE:FONT2SIZE;          
        customhalign=search(str[i], CUSTOMHALIGNCHARS)==[]?0:CUSTOMHALIGNOFFSET;
        customvalign=search(str[i], CUSTOMVALIGNCHARS)==[]?0:CUSTOMVALIGNOFFSET;
        translate([customhalign, customvalign, 0])
        translate([CUMSUMTESTSTRINGPICAS[i]*unitdist,0])
        
        offset(FONT_WEIGHT_OFFSET)
        text(size=size, font=font, halign="left", str[i]);
        //echo(CUMULATIVETESTSTRINGPICAS[i]);
    }
    }
}


module ArrangeComposerLines(arrayOfStrings){
    lines=len(arrayOfStrings)-1;
    columns=2;
    translate([10, -10, 0])
    for (line=[0:lines]){
    stringinline=arrayOfStrings[line];
    
    translate([0, -8*line, ])
    TextGaugeComposerLine(stringinline, UNITDIST);
    }
    //echo(lines);
    //echo(arrayOfStrings);
}

///EXECUTE CODE:
Render();