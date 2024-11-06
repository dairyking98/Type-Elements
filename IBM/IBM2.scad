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
RENDER_VARIANT=0;//[0:plain, 1:resin print, 2:type test]
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
//element typeface
FONT="Arial";
//element type size
FONTSIZE=2.4;//.05
//type weight offset +/-
FONT_WEIGHT_OFFSET=0;//.01
//x weight adjustment 0+
X_WEIGHT_ADJUSTMENT=.01;
//y weight adjustment 0+
Y_WEIGHT_ADJUSTMENT=.01;
//x horiz alignment offset for composer
X_POS_OFFSET_COMPOSER=1.71;//.01
//y vert alignment offset for composer
Y_POS_OFFSET_COMPOSER=-1.5;//1.01;//.01
//y vert alignment offset for selectric 1/2
Y_POS_OFFSET_S12=-1.5;
//y pos offset
Y_POS_OFFSET=RENDER_MODE==0?Y_POS_OFFSET_COMPOSER:Y_POS_OFFSET_S12;
//h alignment 
H_ALIGNMENT=RENDER_MODE==0?"left":"center";
//minkowski draft angle
MINKOWSKI_ANGLE=60;
//minkowski bottom radius size
MINK_TEXT_R=2*tan(.5*MINKOWSKI_ANGLE);

/* [Typeball Dimensions] */
//sphere diameter
SPHERE_OD=33.4;
//sphere radius
SPHERE_R=SPHERE_OD/2;
//character-concave to character-concave diameter
MAX_OD=34.9;
//sphere center to top flat
TOPFLAT_TO_CENTER=11.0;//was 11.4;
//thickness of top flat
TOPFLAT_THICKNESS=4.5;
//shaft ID
SHAFT_ID=8.8;
//top shaft chamfer
TOP_CHAMFER=.7;
//inside ID
INSIDE_ID=28.15;
//shaft boss height
//BOSS_H=8.62;//was 8.07; now redundant replaced by BOSS_TO_CENTER
BOSS_TO_CENTER=2.5;//TOPFLAT_TO_CENTER-BOSS_H = 2.38;
//center to CENTER_TO_TOP of element
CENTER_TO_TOP=11;//TOPFLAT_TO_CENTER = 11;
//center to floor of element
FLOOR=10.7;//abs(TOPFLAT_TO_CENTER-ELEMENT_OAT) = 10.7;
//boss OD
BOSS_OD=11.6;
//skirt top OD
SKIRT_TOP_OD=32.3;
//skirt bottom OD
SKIRT_BOTTOM_OD=30.2;
//overall thickness of element
//ELEMENT_OAT=21.7;//was 22.0; now redundant - FLOOR + CENTER_TO_TOP = OAT
//angle between characters
LATITUDE_SPACING=360/22;
//angle between rows
LONGITUDE_SPACING=[32.8, 16.4, 0, -16.4];
//platen diameter
PLATEN_OD=45;
//radius of hollow section
HOLLOW_R=2;
//drive notch width
DRIVE_NOTCH_WIDTH=1.15;
//drive notch height
DRIVE_NOTCH_HEIGHT=2.2;
//drive notch theta from arrow
DRIVE_NOTCH_THETA_=131.8;
//detent valley from center
DETENT_VALLEY_TO_CENTER=6;
//detent teeth clock offset
DETENT_SKIRT_CLOCK_OFFSET=2.01;

/* [Character Polar Positioning Offsets] */
//individual platen cutout adjustment angles
PLATEN_LONGITUDE_OFFSETS=[0, 0, 0, 0];//.05
//individual baseline adjustment angles
BASELINE_LONGITUDE_OFFSETS=[0, 0, 0, 0];//.05
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
ROOF=CENTER_TO_TOP-TOPFLAT_THICKNESS;
//top flat radius
TOPFLAT_R=(SPHERE_R^2-TOPFLAT_TO_CENTER^2)^.5;

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
ZXCVBNM,.?
";

//uppercase composer layout on machine; left to right, top to bottom
LOWER_CASE_COMPOSER ="
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
";

//lowercase composer layout on machine; left to right, top to bottom
UPPER_CASE_COMPOSER ="
!†+$%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
";

//selectric 1/2 layout array
S12CASES88=[LOWERCASE88, UPPERCASE88];
//composer layout array
COMPOSERCASES88=[LOWER_CASE_COMPOSER,UPPER_CASE_COMPOSER];

//set keyboard layout
CASES88=RENDER_MODE==0?COMPOSERCASES88:S12CASES88;

//lowercase hemisphere of selectric 1/2 element from the top moving clockwise, top to bottom
S12_LC_HEMISPHERE88="
90652z48731
bhkentlcdux
wsi'.½oarvm
-yqp=j/,;fg
";

//lowercase hemisphere of composer element from the top moving clockwise, top to bottom
COMPOSER_LC_HEMISPHERE88="
.,634s10928
?-[cliatb75
xvumhnrodwk
=]zpyefgq;j
";

//set lowercase hemisphere
LC_HEMISPHERE88=RENDER_MODE==0?COMPOSER_LC_HEMISPHERE88:S12_LC_HEMISPHERE88;


//create lowercase layout to element hemisphere map
LC_LAYOUT_TO_HEMISPHERE_MAP = [for (i=[0:len(CASES88[0])-1]) search(CASES88[0][i], LC_HEMISPHERE88)];

//create latitude, longitude integer array for one hemisphere
LATITUDE_LONGITUDE = [for (i=[0:len(LC_LAYOUT_TO_HEMISPHERE_MAP)-1]) [LC_LAYOUT_TO_HEMISPHERE_MAP[i][0]%11, ceil(LC_LAYOUT_TO_HEMISPHERE_MAP[i][0]/11+.001)-1, CASES88[0][i], i]];

//character and point array for type testing composer
COMPOSER_PITCH_LIST=[

    ["M", 9], ["W", 9], ["m", 9],
    
    ["A", 8], ["D", 8], ["G", 8], ["H", 8], ["K", 8], ["N", 8], ["O", 8], ["Q", 8], ["R", 8], ["U", 8], ["V", 8], ["X", 8], ["Y", 8], ["w", 8], ["¾", 8], ["½", 8], ["&", 8], ["%", 8], ["@", 8], ["¼", 8], ["–", 8],
    
    ["B", 7], ["C", 7], ["E", 7], ["F", 7], ["L", 7], ["T", 7], ["Z", 7],
    
    ["P", 6], ["S", 6], ["b", 6], ["d", 6], ["h", 6], ["k", 6], ["n", 6], ["o", 6], ["p", 6], ["q", 6], ["u", 6], ["x", 6], ["y", 6], ["*", 6], ["†", 6], ["$", 6], ["+", 6], ["=", 6], ["0", 6], ["1", 6], ["2", 6], ["3", 6], ["4", 6], ["5", 6], ["6", 6], ["7", 6], ["8", 6], ["9", 6], ["]", 6],
    
    ["J", 5], ["a", 5], ["c", 5], ["e", 5], ["g", 5], ["v", 5], ["?", 5], ["[", 5], ["z", 5],
    
    ["I", 4], ["f", 4], ["r", 4], ["s", 4], ["t", 4], [":", 4], ["(", 4], [")", 4], ["!", 4], ["/", 4], ["(", 4],
    
    ["i", 3], ["j", 3], ["l", 3], [".", 3], [",", 3], [";", 3], ["’", 3], ["‘", 3], ["-", 3], [" ", 3], ["'", 3] //apostrophe not native to Composer

];

//string for type test
TESTSTRING="1234567890-=qwertyuiop?asdfghjkl][zxcvbnm,.;!†+$%/&*()–@QWERTYUIOP¾ASDFGHJKL¼½ZXCVBNM‘’:";
//picas per character array
TESTSTRINGPICAS = [0, for ( i = [0:len(TESTSTRING)-1] ) COMPOSER_PITCH_LIST[search(TESTSTRING[i], COMPOSER_PITCH_LIST)[0]][1]];
//cumulative picas per character array
CUMULATIVETESTSTRINGPICAS = cumulativeSum(TESTSTRINGPICAS);
//cpi spacing for type test
TESTCPI=10;
//unit spacing for type test of Composer
UNITSPERINCH=72;//[72:Red (12Units/Pica  72 Units/in), 84:Yellow (14Units/Pica  84 Units/in), 96:Blue (16 Units/Pica  96 Units/in)]
//mm distance per composer unit
UNITDIST=25.4/UNITSPERINCH;


/* [Resin Supports] */
//tip diameter
TIP_D=.8;
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
//web?
WEB=false;
//web ID
WEB_ID=BOSS_OD+1;
//web inner corner R
WEB_IR=1;
//web outer corner R
WEB_OR=2;
//web OD
WEB_OD=TOPFLAT_R*2-2;

echo("Top flat to boss must measure at 8.5mm or element is incorrectly represented. Adjust BOSS_TO_CENTER until print yields 8.5mm boss height.");

//cumulative sum vector fuction for composer type test pitch array
function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec)-1; newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];

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
module SingleMinkowski(char, latitude, longitude, plat_offset, base_offset){
    minkowski(){
        difference(){
            PositionText(latitude, longitude+base_offset)
            linear_extrude(6)
            Text(char);
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
    char=CASES88[case_int][hemi_int];
    latitude=LATITUDE_LONGITUDE[hemi_int][0]*LATITUDE_SPACING+case_int*180;
    longitude=LONGITUDE_SPACING[LATITUDE_LONGITUDE[hemi_int][1]];
    plat_offset=PLATEN_LONGITUDE_OFFSETS[LATITUDE_LONGITUDE[hemi_int][1]];
    base_offset=BASELINE_LONGITUDE_OFFSETS[LATITUDE_LONGITUDE[hemi_int][1]];
    if (SELECTIVE_RENDER==true && search(char, SELECTIVE_RENDER_CHARS)!= [])
    SingleMinkowski(char, latitude, longitude, plat_offset, base_offset);
    else if (SELECTIVE_RENDER==true && search(char, SELECTIVE_RENDER_CHARS)== []) {}
    else
    SingleMinkowski(char, latitude, longitude, plat_offset, base_offset);
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
    translate([0, 0, CENTER_TO_TOP-TOP_CHAMFER])
    cylinder(d1=SHAFT_ID, d2=SHAFT_ID+2*TOP_CHAMFER, h=TOP_CHAMFER, $fn=surface_fn);
    //inside radius
    translate([0, 0, -20])
    cylinder(d=INSIDE_ID, h=20+BOSS_TO_CENTER, $fn=surface_fn);
    //roof ish area
    rotate_extrude($fn=surface_fn)
    HollowProfile();
    //notch
    Notch();
    //detent teeth
    rotate([0, 0, DETENT_SKIRT_CLOCK_OFFSET])
    Teeth();
    //web
    if (WEB==true)
    ArrangeWeb();
}
//subtractive parts - inner radius
module HollowProfile(){
    hull(){
        translate([-HOLLOW_R+INSIDE_R, CENTER_TO_TOP-TOPFLAT_THICKNESS-2*HOLLOW_R, 0])
        scale([1, 2])
        circle(r=HOLLOW_R);
        translate([BOSS_R, 0, 0])
        square(1);
        translate([BOSS_R+HOLLOW_R, CENTER_TO_TOP-TOPFLAT_THICKNESS-HOLLOW_R, 0])
        scale([1, 1])
        circle(r=HOLLOW_R);

    }
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
}

//resin support tip, angle input
module ResinTip(a1){
    rotate([0, a1, 0])
    hull(){
        sphere(d=TIP_D);
        translate([0, 0, -TIP_H])
        sphere(d=ROD_D);
    }
}

//get rotated resin support tip x offset function
function ResinXOffset(a1)= sin(a1)*TIP_H;

//resin support rod
module ResinRod(h, a1){
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
    ResinTip(a1);
}

//assemble resin support rods
module ResinRodAssemble(){
    for (i=[0:22-1])
    
        //detent teeth supports
        rotate([0, 0, i*LATITUDE_SPACING+DETENT_SKIRT_CLOCK_OFFSET])
        translate([(SKIRT_BOTTOM_OD+INSIDE_ID)/4, 0, 0])
        ResinRod(0, 0);
    
    //boss supports
    for (i=[0:11]){
        rotate([0, 0, i*360/11]){
        
        if (i!=4){
        //boss supports
        translate([BOSS_R, 0, 0])
        ResinRod(FLOOR+BOSS_TO_CENTER, -45);
        //boss roof support supports
        hull(){
            translate([BOSS_R-ResinXOffset(-45), 0, 12])
            sphere(d=ROD_D);
            translate([(BOSS_OD+INSIDE_ID)/4, 0, 8])
            sphere(d=ROD_D);
        }
        //roof support supports
        hull(){
            translate([(BOSS_OD+INSIDE_ID)/4, 0, 4])
            sphere(d=ROD_D);
            rotate([0, 0, 360/11])
            translate([(BOSS_OD+INSIDE_ID)/4, 0, 0])
            sphere(d=ROD_D);
        }
        if (i!=3)
        //boss support supports
        hull(){
            translate([BOSS_R-ResinXOffset(-45), 0, 1])
            sphere(d=ROD_D);
            rotate([0, 0, 360/11])
            translate([BOSS_R-ResinXOffset(-45), 0, 7])
            sphere(d=ROD_D);
        }
        }
        
        //roof supports
        translate([(BOSS_OD+INSIDE_ID)/4, 0, 0])
        ResinRod(FLOOR+ROOF, 0);
        
        }
        
        
    //for notch supports
    n=10;//degrees off from notch 
    l=[3, 5];
    k=[n, -n];
    if (i==4)
        for (j=[0, 1]){
            //notch supports
            rotate([0, 0, DRIVE_NOTCH_THETA+k[j]])
            translate([BOSS_R, 0, 0])
            ResinRod(FLOOR+BOSS_TO_CENTER, -45);
            //notch support supports
            hull(){
                rotate([0, 0, DRIVE_NOTCH_THETA-k[j]])
                translate([BOSS_R-ResinXOffset(-45), 0, 12])
                sphere(d=ROD_D);
                rotate([0, 0, l[j]*360/11])
                translate([BOSS_R-ResinXOffset(-45), 0, 7])
                sphere(d=ROD_D);
            }
        }
    }
    


        
}

//assemble resin print
module ResinPrint(){
    translate([0, 0 , FLOOR])
    SubtractFromFull();
    ResinRodAssemble();
}

//monospaced type test gauge
module TextGauge(str, pitch)
{
    color("red")
    for ( i = [0:len(str)] )
    {
        translate([8,8])
        translate([i*22/pitch, 0, 0])
        offset(FONT_WEIGHT_OFFSET)
        text(size=FONTSIZE, font=FONT, halign="center", str[i]);
    }
}

//composer type test gauge
module TextGaugeComposer(str, unitdist)
{
    color("red")
    for ( i = [0:len(str)-1] )
    {
        translate([8,8])
        translate([CUMULATIVETESTSTRINGPICAS[i]*unitdist,0])
        
        offset(FONT_WEIGHT_OFFSET)
        text(size=FONTSIZE, font=FONT, halign="left", str[i]);
        echo(CUMULATIVETESTSTRINGPICAS[i]);
    }
}

//cumulative sum vector fuction for composer type test pitch array
function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec)-1; newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];

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
    translate([0, 0, ROOF-1])
    linear_extrude(6)
    2dWeb();
    translate([0, 0, CENTER_TO_TOP-TOP_CHAMFER])
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
                    TextGaugeComposer(TESTSTRING, UNITDIST);
                if (RENDER_MODE==1)
                    TextGauge(TESTSTRING, TESTCPI);
            }
            if (XSECTION==true && RENDER_VARIANT!=2)
            rotate([0, 0, XSECTION_THETA-90])
            translate([0, -50, -50])
            cube(100);
        }
    }
}

///EXECUTE CODE:
Render();