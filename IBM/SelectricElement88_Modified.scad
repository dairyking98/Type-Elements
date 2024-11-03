
/* --------- START --------- */
// Keyboard layout

// US Selectric 88 character
LOWER_CASE88 = str(
    "1234567890-=",
    "qwertyuiop½",
    "asdfghjkl;'",
    "zxcvbnm,./"
);

UPPER_CASE88 = str(
    "!@#$%¢&*()_+",
    "QWERTYUIOP¼",
    "ASDFGHJKL:\"",
    "ZXCVBNM,.?"
);

// US Selectric Composer
LOWER_CASE_COMPOSER = str(
    "1234567890-=",
    "qwertyuiop?",
    "asdfghjkl][",
    "zxcvbnm,.;"
);

UPPER_CASE_COMPOSER = str(
    "!†+$%/&*()–@",
    "QWERTYUIOP¾",
    "ASDFGHJKL¼½",
    "ZXCVBNM‘’:"
);

COMPOSER_PITCH_LIST=[

    ["M", 9], ["W", 9], ["m", 9],
    
    ["A", 8], ["D", 8], ["G", 8], ["H", 8], ["K", 8], ["N", 8], ["O", 8], ["Q", 8], ["R", 8], ["U", 8], ["V", 8], ["X", 8], ["Y", 8], ["w", 8], ["¾", 8], ["½", 8], ["&", 8], ["%", 8], ["@", 8], ["¼", 8], ["–", 8],
    
    ["B", 7], ["C", 7], ["E", 7], ["F", 7], ["L", 7], ["T", 7], ["Z", 7],
    
    ["P", 6], ["S", 6], ["b", 6], ["d", 6], ["h", 6], ["k", 6], ["n", 6], ["o", 6], ["p", 6], ["q", 6], ["u", 6], ["x", 6], ["y", 6], ["*", 6], ["†", 6], ["$", 6], ["+", 6], ["=", 6], ["0", 6], ["1", 6], ["2", 6], ["3", 6], ["4", 6], ["5", 6], ["6", 6], ["7", 6], ["8", 6], ["9", 6], ["]", 6],
    
    ["J", 5], ["a", 5], ["c", 5], ["e", 5], ["g", 5], ["v", 5], ["?", 5], ["[", 5], ["z", 5],
    
    ["I", 4], ["f", 4], ["r", 4], ["s", 4], ["t", 4], [":", 4], ["(", 4], [")", 4], ["!", 4], ["/", 4], ["(", 4],
    
    ["i", 3], ["j", 3], ["l", 3], [".", 3], [",", 3], [";", 3], ["’", 3], ["‘", 3], ["-", 3], [" ", 3], ["'", 3] //apostrophe not native to Composer

];



/* [Create Parameters] */
//Turns off minkowski() (TAPERED TEXT) for fast preview
MINK_OFF=true;
//Turns on Composer layout and left alignment
COMPOSER=false;
//Amount of offset from center of left edge of text 
COMPOSER_CENTER_OFFSET=3;//.01
COMPOSER_VERT_OFFSET=0.5; // Vertical offset for Composer elements 
//Render mode
GENMODE=0;//[0:Render, 1:ResinPrint, 2:TestString]

UPPER_CASE=COMPOSER?UPPER_CASE_COMPOSER:UPPER_CASE88;
LOWER_CASE=COMPOSER?LOWER_CASE_COMPOSER:LOWER_CASE88;

/* [Testing Stuff] */
//Generate cross section
XSECTION=false;
//Cross section angle
XSECTIONTHETA=0;//30
//String for type test
TESTSTRING="1234567890-=qwertyuiop?asdfghjkl][zxcvbnm,.;!†+$%/&*()–@QWERTYUIOP¾ASDFGHJKL¼½ZXCVBNM‘’:";
//CPI spacing for type test
TESTCPI=10;
//Render only specific characters
SPECIFICRENDER=false;
//List of specific rendered characters
SPECIFICRENDERLIST=":";
//Unit spacing for type test of Composer
UNITSPERINCH=72;//[72:Red (12Units/Pica  72 Units/in), 84:Yellow (14Units/Pica  84 Units/in), 96:Blue (16 Units/Pica  96 Units/in)]
UNITDIST=25.4/UNITSPERINCH;

// The name of the font, as understood by the system.
// Note: if the system doesn't recognize the font it
// will silently fall back to a default!
/* [Font Stuff] */
TYPEBALL_FONT = "Vogue";

// The font height, adjusted for the desired pitch
// (Note that this is multiplied by faceScale=2.25 in LetterText())
LETTER_HEIGHT = 2.75;

TESTSTRINGPICAS = [0, for ( i = [0:len(TESTSTRING)-1] ) COMPOSER_PITCH_LIST[search(TESTSTRING[i], COMPOSER_PITCH_LIST)[0]][1]];

CUMULATIVETESTSTRINGPICAS = cumulativeSum(TESTSTRINGPICAS);

echo(TESTSTRINGPICAS);

// Offset each glyph by this amount, making the characters heavier or lighter
CHARACTER_WEIGHT_ADJUSTMENT = -0.05;

// balance the vertical smear with extra horizontal weight
HORIZONTAL_WEIGHT_ADJUSTMENT = 0.2;

// If g/j/p/q/y in bottom row extend into the detent teeth area, we'll need to trim them back out
TRIM_DESCENDERS = true;


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
//Font size for typeface label 
FONT_LABEL_SIZE=2;

// -------------------
// Render
// -------------------

// preview a single letter
//LetterText(LETTER_HEIGHT, LETTER_ALTITUDE, TYPEBALL_FONT, "8");

// preview text at the given pitch
//TextGauge("This is example text at 12 pitch", 12);

// render the full type ball


// ---------- END ----------




// ############################### Selectric_II_typeball.scad ###############################
// Custom typeball ("golfball") type element for IBM Selectric II typewriters

// based on original project by Steve Malikoff
// https://www.thingiverse.com/thing:4126040

// Modifications by Dave Hayden (dave@selectricrescue.org), last update 2023.07.07

// Huge thanks to Sam Ettinger for his feedback and
// for proving that resin-printed Selectric balls
// actually work, to Stephen Cook for his expert
// advice, and of course to Steve Malikoff for
// bringing the dream to life

// Note: STL generation is *much* faster using the command line, with the --enable all flag

// This work is released under the CC BY 4.0 license:
// https://creativecommons.org/licenses/by/4.0/

// You are free to:
// Share — copy and redistribute the material in any medium or format
// Adapt — remix, transform, and build upon the material for any purpose, even commercially.

// Under the following terms:
// Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
// No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

// Original project notes:
// ----------------------------------------
//
// NOTE1:   USING A REGULAR FDM PRINTER MAY NOT ACHIEVE THE RESOLUTION REQUIRED, PERHAPS A RESIN PRINT 
//          WOULD WORK BETTER
// NOTE2:   THIS IS FOR AMUSEMENT PURPOSES ONLY, NOT INTENDED FOR SERIOUS USE. HAVE FUN!
// NOTE3:   I AM NOT RESPONSIBLE FOR ANY DAMAGE THIS PRINT MAY CAUSE TO YOUR TYPEWRITER, USE AT OWN RISK.
//
// In memory of John Thompson, an Australian IBM OPCE from whom I "inherited" his Selectric CE tool set:
//      http://qccaustralia.org/vale.htm
//
// Copyright (C) Steve Malikoff 2020 
// Written in Brisbane, Australia
// LAST UPDATE  20200125


// ---------------------------------------------------
// Font and cosmetic parameters
// ---------------------------------------------------

// See SelectricElementExample.scad for parameters expected to be defined before including this one. 

// ---------------------------------------------------
/* [Typeball Parameters (some are hardcoded and do not appear here)] */
// ---------------------------------------------------

// How far the type's contact face projects outwards above the ball surface
LETTER_ALTITUDE = 1.8;

// Tweak tilt of characters per row for better descenders/balance. Ordered top to bottom. Amount is backwards rotation: top goes back and bottom goes forward
ROW_TILT_ADJUST = [ 0, 0.5, 1, 2 ];

// amount of curvature on the letter faces. Using a value a bit larger than the actual platen seems to give a better print
PLATEN_DIA = 45;

// Rendering granularity for F5 preview and F6 render. Rendering takes a while.
PREVIEW_FACETS = 22;
RENDER_FACETS = 44;

FACETS = $preview ? PREVIEW_FACETS : RENDER_FACETS;
FONT_FACETS = FACETS;
$fn = FACETS;

// --- probably shouldn't mess with stuff below ---

// Parameters have been tuned for printing on a Creality Halot One resin printer, using Sunlu ABS-Like resin

// angle between the four rows of type
TILT_ANGLE = 16.4;

// top row is just a bit high :-/
TOP_ROW_ADJUSTMENT = -0.3;

// add a slot opposite the alignment notch. What's it for? Who knows?
SLOT = true;

TYPEBALL_RAD = 33.4 / 2;
INSIDE_RAD = 14.3;//.01 //originally 28.15 / 2;
INSIDE_CURVE_START = 3.3;//.01 //originally 2
TYPEBALL_HEIGHT = 21.5;
TYPEBALL_TOP_ABOVE_CENTRE = 11.4; // Flat top is this far above the sphere centre
TYPEBALL_TOP_THICKNESS = 1.65;

// Label params
DEL_BASE_FROM_CENTRE = 8.2;
DEL_DEPTH = 0.6;

// Detent teeth skirt parameters
TYPEBALL_SKIRT_TOP_RAD = 31.9 / 2;
TYPEBALL_SKIRT_BOTTOM_RAD = 30.5 / 2;
TYPEBALL_SKIRT_TOP_BELOW_CENTRE = -sqrt(TYPEBALL_RAD^2-TYPEBALL_SKIRT_TOP_RAD^2);  // Where the lower latitude of the sphere meets the top of the skirt
SKIRT_HEIGHT = TYPEBALL_HEIGHT - TYPEBALL_TOP_ABOVE_CENTRE+ TYPEBALL_SKIRT_TOP_BELOW_CENTRE;
TOOTH_PEAK_OFFSET_FROM_CENTRE = 6.1; // Lateral offset of the tilt ring detent pawl

// Parameters for the centre boss that goes onto tilt ring spigot (upper ball socket)
BOSS_INNER_RAD = 4.4; // Originally 4.35
BOSS_OUTER_RAD = 5.8;
BOSS_HEIGHT = 8.07;
NOTCH_ANGLE = 131.8; // Must be exact! If not, ball doesn't detent correctly
NOTCH_WIDTH = 1.40; // Should be no slop here, either
NOTCH_DEPTH = 2;
NOTCH_HEIGHT = 2.2;
SLOT_ANGLE = NOTCH_ANGLE + 180;
SLOT_WIDTH = 1.9;
SLOT_DEPTH = 0.4;

// Inside reinforcement ribs
RIBS = 11;
RIB_LENGTH = 8.75;//.01
RIB_WIDTH = 2;
RIB_HEIGHT = 2.5;

// Character layout
CHARACTERS_PER_LATITUDE = 22;   // For Selectric I and II. 4 x 22 = 88 characters total.
CHARACTER_LONGITUDE = 360 / CHARACTERS_PER_LATITUDE; // For Selectric I and II

EPSILON = 0.001; // to fix z-fighting in preview




/* [Resin Supports] */
//Tip diameter
TIP=.8;
//Tip height
TIPH=2;
//Rod diameter
ROD=1.2;
//Raft diameter (build plate)
RAFTD=4;
//Raft thickness
RAFTH=2;
//Minimum resin rod height
MINRODH=5;





//////////////EXECUTE CODE:
Render();








/////////////////MODULES AND FUNCTIONS:


//Render based on GENMODE selection
module Render(){
    difference(){
        if (GENMODE==0)
        TypeBall();
        if (GENMODE==1)
        ResinPrint();
        if (GENMODE==2){
            if (COMPOSER==false)
                TextGauge(TESTSTRING, TESTCPI);
            if (COMPOSER==true)
                TextGaugeComposer(TESTSTRING, UNITDIST);
            }
        if (XSECTION==true && GENMODE != 2)
        rotate([0, 0, XSECTIONTHETA])
        translate([0, -50, -50])
        cube(100);
    }
}


//Resin support rod
module ResinRod(h){
    union(){
        translate([0, 0, -RAFTH-MINRODH]){
            cylinder(h=RAFTH, d1=RAFTD, d2=RAFTD+2*RAFTH);
            cylinder(h=RAFTH+MINRODH-TIPH+h, d=ROD);
            translate([0, 0, RAFTH+MINRODH-TIPH+h])
            cylinder(h=TIPH, d1=ROD, d2=TIP);
        }
        translate([0, 0, h])
        sphere(d=TIP);
    }
}

module ResinTip(p){
    hull(){
        sphere(d=ROD);
        translate(p)
        sphere(d=TIP);
        
    }
}




// Labels on the top of the ball, cosmetic
module Labels()
{
    offset(r=0.12)
    {
        // Disable Label No for Composer balls
        if (COMPOSER==false) { 
            translate([-0.1,14,0])
        text(LABEL_NO, size=NO_LABEL_SIZE, font=LABEL_NO_FONT_OVERRIDE==""?TYPEBALL_FONT:LABEL_NO_FONT_OVERRIDE, halign="center");
    }
        translate([0,0.6,0])
        text(LABEL_TEXT_OVERRIDE==""?TYPEBALL_FONT:LABEL_TEXT_OVERRIDE, size=FONT_LABEL_SIZE, font=LABEL_FONT_OVERRIDE==""?TYPEBALL_FONT:LABEL_FONT_OVERRIDE, halign="center");
        
    }
}


//Create Resin Print
module ResinPrint(){
    translate([0,0, -TYPEBALL_SKIRT_TOP_BELOW_CENTRE + SKIRT_HEIGHT])
    TypeBall();
    ResinRodAssemble();
}

module ResinRodAssemble(){
    color("purple"){
        for (i=[0:CHARACTERS_PER_LATITUDE - 1])
        {
            rotate([0, 0, i * CHARACTER_LONGITUDE])
            {
                translate([(INSIDE_RAD+TYPEBALL_SKIRT_BOTTOM_RAD)/2, 0, 0])
                ResinRod(-.2);
                
                hull(){
                        translate([(INSIDE_RAD+TYPEBALL_SKIRT_BOTTOM_RAD)/2, 0, -TIPH])
                        sphere(d=ROD);
                        rotate([0, 0, CHARACTER_LONGITUDE])
                        translate([(INSIDE_RAD+TYPEBALL_SKIRT_BOTTOM_RAD)/2, 0, -MINRODH])
                        sphere(d=ROD);
                }
            }
        }
        for (i=[0:RIBS-1]){
            
            rotate([0, 0, i * 360/11])
            translate([0, 9, 0])
            {
                ResinRod(SKIRT_HEIGHT-TYPEBALL_SKIRT_TOP_BELOW_CENTRE+TYPEBALL_TOP_ABOVE_CENTRE - TYPEBALL_TOP_THICKNESS - RIB_HEIGHT-.5);
                
                if (i==1){
                    translate([0, 0, SKIRT_HEIGHT-TYPEBALL_SKIRT_TOP_BELOW_CENTRE+TYPEBALL_TOP_ABOVE_CENTRE-BOSS_HEIGHT-.2-(9-BOSS_OUTER_RAD-ROD)-1])
                    ResinTip([.3, -(9-BOSS_OUTER_RAD), 9-(BOSS_OUTER_RAD+BOSS_INNER_RAD)/2-ROD+1]);
                }
                
                else if(i==2){
                    translate([0, 0, SKIRT_HEIGHT-TYPEBALL_SKIRT_TOP_BELOW_CENTRE+TYPEBALL_TOP_ABOVE_CENTRE-BOSS_HEIGHT-.2-(9-BOSS_OUTER_RAD-ROD)-1])        
                    ResinTip([1.2, -(9-BOSS_OUTER_RAD)-.1, 9-(BOSS_OUTER_RAD+BOSS_INNER_RAD)/2-ROD+1]);}
                    
                else {
                    translate([0, 0, SKIRT_HEIGHT-TYPEBALL_SKIRT_TOP_BELOW_CENTRE+TYPEBALL_TOP_ABOVE_CENTRE-BOSS_HEIGHT-.2-(9-BOSS_OUTER_RAD-ROD)-1])
                    ResinTip([0, -(9-BOSS_OUTER_RAD), 9-(BOSS_OUTER_RAD+BOSS_INNER_RAD)/2-ROD+1]);
                }
            }
            
            rotate([0, 0, i * 360/11])
            
            hull(){
                translate([0, 9, 0])
                sphere(d=ROD);
                rotate([0, 0, 360/11])
                translate([0, 9, 6])
                sphere(d=ROD);
            }
        }
    }
}




// ---------------------------------------------------
// Rendering
// ---------------------------------------------------

// The entire typeball model proper.
module TypeBall()
{
    //if ( is_undef(PREVIEW_LABEL) || !PREVIEW_LABEL )
    {
        difference()
        {
            color("turquoise")
            SelectricLayout88();
            TrimTop();
            
            if ( !is_undef(TRIM_DESCENDERS) && TRIM_DESCENDERS )
            {
                // trim any bits that extended into the detent teeth
                translate([0,0, TYPEBALL_SKIRT_TOP_BELOW_CENTRE - SKIRT_HEIGHT-EPSILON])
                DetentTeeth();
            }
            
            translate([0,0,-20+INSIDE_CURVE_START])
            cylinder(r=INSIDE_RAD, h=20, $fn=$preview ? 60 : 360); // needs to be smooth!
        }
    }

    difference()
    {
        HollowBall();
        if (SLOT) Slot();
        if (LABEL==true){
            Notch();
            FontName();
        }
        if (ARROW==true){
            Del();
        }
    }
}


// Keyboard location of each letter on the ball
charmap88 =
   [ 0,  2,  6,  7,  3, 34,  1,  4,  5,  9,  8,
    35, 18, 25, 36, 31, 16, 39, 14, 30, 28, 38,
    40, 37, 15, 23, 20, 22, 42, 33, 19, 24, 13,
    27, 26, 32, 41, 43, 29, 11, 21, 12, 17, 10 ];

charmapComposer =
   [ 7,  1,  8,  9,  0, 24,  3,  2,  5, 41, 42,
     4,  6, 38, 16, 23, 19, 31, 36, 33, 10, 22,
    30, 13, 25, 20, 15, 39, 28, 40, 18, 37, 35,
    29, 43, 12, 27, 26, 14, 17, 21, 34, 32, 11 ];
    
charmap=COMPOSER?charmapComposer:charmap88;

module SelectricLayout88()
{
    ROWCHARS = CHARACTERS_PER_LATITUDE/2;
    
    for ( l=[0:3] )
    {
        tiltAngle = (2-l) * TILT_ANGLE + (l==0?TOP_ROW_ADJUSTMENT:0);
        
        for ( p=[0:ROWCHARS-1] )
        {
            SpecificPass = search(LOWER_CASE[charmap[ROWCHARS*l+p]], SPECIFICRENDERLIST);
            if (SPECIFICRENDER==true && SpecificPass==[])
            {}
            
            else
            GlobalPosition(TYPEBALL_RAD, tiltAngle, (5-p)*CHARACTER_LONGITUDE, ROW_TILT_ADJUST[l])
            LetterText(LETTER_HEIGHT, LETTER_ALTITUDE, TYPEBALL_FONT, LOWER_CASE[charmap[ROWCHARS*l+p]]);
        }

        for ( p=[0:ROWCHARS-1] )
        {
            SpecificPass = search(UPPER_CASE[charmap[ROWCHARS*l+p]], SPECIFICRENDERLIST);
            if (SPECIFICRENDER==true && SpecificPass==[])
            {}
            
            else
            GlobalPosition(TYPEBALL_RAD, tiltAngle, (ROWCHARS+5-p)*CHARACTER_LONGITUDE, ROW_TILT_ADJUST[l])
            LetterText(LETTER_HEIGHT, LETTER_ALTITUDE, TYPEBALL_FONT, UPPER_CASE[charmap[ROWCHARS*l+p]]);
        }
    }
}

// position child (a typeface letter) at global latitude and longitude on sphere of given radius
module GlobalPosition(r, latitude, longitude, rotAdjust)
{
    x = r * cos(latitude);
    y = 0;
    z = r * sin(latitude); 
    
    rotate([0, 0, longitude])
    translate([x, y, z])
    rotate([0, 90 - latitude - rotAdjust, 0])
    children();
}

//// generate reversed embossed text, tapered outwards to ball surface, face curved to match platen
module LetterText(someTypeSize, someHeight, typeballFont, someLetter, platenDiameter=PLATEN_DIA)
{
    $fn = $preview ? 12 : 24;
    faceScale = 2.25;
 
    rotate([0,180,90])
    minkowski()
    {
        intersection()
        {
            translate([0,-someTypeSize/2,-someHeight])
            scale([0.5,0.5,2.0])
            linear_extrude(height=1)
            offset(CHARACTER_WEIGHT_ADJUSTMENT)
            minkowski()
            {
                if (COMPOSER==true){
                    translate([-COMPOSER_CENTER_OFFSET, COMPOSER_VERT_OFFSET, 0])
                    text(size=someTypeSize * faceScale, font=typeballFont, halign="left", someLetter);
                    
                }
                
                if (COMPOSER==false){
                    text(size=someTypeSize * faceScale, font=typeballFont, halign="center", someLetter);
                }
                if (MINK_OFF==false)
                polygon([[-HORIZONTAL_WEIGHT_ADJUSTMENT/2,0],[HORIZONTAL_WEIGHT_ADJUSTMENT/2,0],[HORIZONTAL_WEIGHT_ADJUSTMENT/2,EPSILON],[-HORIZONTAL_WEIGHT_ADJUSTMENT/2,EPSILON]]);
            }

            translate([0,0,-platenDiameter/2-someHeight/2+0.121])
            rotate([0,90,0])
            difference()
            {
                cylinder(h=100, r=platenDiameter/2+0.01, center=true, $fn=$preview ? 60 : 360);
                cylinder(h=100, r=platenDiameter/2, center=true, $fn=$preview ? 60 : 360);
            }

        }
        if (MINK_OFF==false)
        cylinder(h=someHeight, r1=0, r2=0.75*someHeight);
    }
}

// The unadorned ball shell with internal ribs
module HollowBall()
{
    difference(){
        union(){
            difference()
            {
                Ball();
                
                translate([0,0,-20+INSIDE_CURVE_START])
                cylinder(r=INSIDE_RAD, h=20, $fn=$preview ? 60 : 360); // needs to be smooth!
            }
            Ribs();
        }
        difference(){
            sphere(50, $fn=10);
            sphere(r=TYPEBALL_RAD, $fn=$preview ? 40 : 160);
            translate([-25, -25, -50])
            cube(50);
        }
    }
    
}

module Ball()
{
    arbitraryRemovalBlockHeight = 20;
    
    // Basic ball, trimmed flat top and bottom
    difference()
    {
        sphere(r=TYPEBALL_RAD, $fn=$preview ? 40 : 160);
 
        translate([-50,-50, TYPEBALL_TOP_ABOVE_CENTRE-EPSILON])
            cube([100,100,arbitraryRemovalBlockHeight]);
        
        translate([-50,-50, TYPEBALL_SKIRT_TOP_BELOW_CENTRE - arbitraryRemovalBlockHeight])   // ball/skirt fudge factor
            cube([100,100,arbitraryRemovalBlockHeight]);
        
        intersection()
        {
            sphere(r=sqrt(INSIDE_RAD^2+INSIDE_CURVE_START^2), $fn=$preview ? 60 : 160);
            translate([-20,-20,INSIDE_CURVE_START-EPSILON])
                cube([40,40,20]);
        }
    }

    // Fill top back in
    TopFace();

    // Detent teeth skirt
    DetentTeethSkirt();
    CentreBoss();
}

//////////////////////////////////////////////////////////////////////////
//// Detent teeth around bottom of ball
module DetentTeethSkirt()
{
    // Detent teeth skirt
    difference()
    {
        translate([0,0, TYPEBALL_SKIRT_TOP_BELOW_CENTRE - SKIRT_HEIGHT])
        cylinder(r2=TYPEBALL_SKIRT_TOP_RAD, r1=TYPEBALL_SKIRT_BOTTOM_RAD, h=SKIRT_HEIGHT, $fn=160);
        
        translate([0,0, TYPEBALL_SKIRT_TOP_BELOW_CENTRE - SKIRT_HEIGHT-EPSILON])
        DetentTeeth();
    }
}

// Ring of detent teeth in skirt
module DetentTeeth()
{
    for (i=[0:CHARACTERS_PER_LATITUDE - 1])
    {
        rotate([0, 0, i * CHARACTER_LONGITUDE])
        Tooth();
    }
}

module Tooth()
{
    translate([0, TOOTH_PEAK_OFFSET_FROM_CENTRE, 0])
    rotate([180, -90, 0])
    {
        // notch between teeth must be big enough to trap detent
        linear_extrude(30)
        polygon(points=[[0,1.9], [2.2,0.4], [3.2,0.14], [3.2, -0.14], [2.2, -0.4], [0,-1.9]]);
    }
}

// Flat top of typeball, punch tilt ring spigot hole through and subtract del triangle
module TopFace()
{
    r = sqrt(TYPEBALL_RAD^2-TYPEBALL_TOP_ABOVE_CENTRE^2);
    
    // Fill top back in, after the inside sphere was subtracted before this fn was called
    difference()
    {
        union(){
        translate([0, 0, TYPEBALL_TOP_ABOVE_CENTRE - TYPEBALL_TOP_THICKNESS - RIB_HEIGHT])
        cylinder(r=r+2, h=TYPEBALL_TOP_THICKNESS+RIB_HEIGHT);
        }

        translate([0, 0, TYPEBALL_TOP_ABOVE_CENTRE - TYPEBALL_TOP_THICKNESS - RIB_HEIGHT - EPSILON])
        cylinder(h=RIB_HEIGHT/2, r1=r, r2=0);
            
        translate([0, 0, TYPEBALL_TOP_ABOVE_CENTRE - TYPEBALL_TOP_THICKNESS - RIB_HEIGHT - EPSILON])
        cylinder(r=BOSS_INNER_RAD,h=TYPEBALL_TOP_THICKNESS*2+RIB_HEIGHT, $fn=360);
        
        //Del();
    }   
}

// Alignment marker triangle on top face
module Del()
{
    translate([DEL_BASE_FROM_CENTRE, 0, TYPEBALL_TOP_ABOVE_CENTRE - DEL_DEPTH + EPSILON])
    color("white")  // TODO red triangle for Composer typeball
    linear_extrude(DEL_DEPTH)
    polygon(points=[[3.4,0],[0.4,1.3],[0.4,-1.3]]);
}

// Emboss a label onto top face
module FontName()
{
    translate([-8.5, 0, TYPEBALL_TOP_ABOVE_CENTRE - DEL_DEPTH])
    rotate([0,0,270])
    linear_extrude(DEL_DEPTH+0.01)
    Labels();
}

// Clean up any base girth bits of T0-ring characters projecting above top face
module TrimTop()
{
    translate([-50,-50, TYPEBALL_TOP_ABOVE_CENTRE])
    cube([100,100,20]);
}

// Tilt ring boss assembly
module CentreBoss()
{
    translate([0,0, TYPEBALL_TOP_ABOVE_CENTRE - BOSS_HEIGHT])
    difference()
    {
        cylinder(r=BOSS_OUTER_RAD, h=BOSS_HEIGHT);

        translate([0,0,-EPSILON])
        cylinder(r=BOSS_INNER_RAD, h=BOSS_HEIGHT+2*EPSILON, $fn=360);
    }    
}

// The full-length slot in the tilt ring boss at the (not quite) half past one o'clock position
// XXX - S2 doesn't use this. Which Selectric does? Composer?
module Slot()
{
    rotate([0, 0, SLOT_ANGLE])
    translate([0, -SLOT_WIDTH/2, 0])
    cube([SLOT_DEPTH + BOSS_INNER_RAD, SLOT_WIDTH, 40]);
}

// The partial-length slot in the tilt ring boss at the (not quite) half past seven o'clock position
module Notch()
{
    rotate([0, 0, NOTCH_ANGLE])
    translate([0, -NOTCH_WIDTH/2, TYPEBALL_TOP_ABOVE_CENTRE - BOSS_HEIGHT - EPSILON])
    cube([NOTCH_DEPTH + BOSS_INNER_RAD, NOTCH_WIDTH, NOTCH_HEIGHT + EPSILON]);
}

// The reinforcement spokes on the underside of the top face, from the tilt ring boss 
// to the inner sphere wall
module Ribs()
{
    segment = 360 / RIBS;
    
    for (i=[0:RIBS - 1])
    {
        rotate([0, 5, -360.0/44 + segment * i])
        translate([BOSS_OUTER_RAD - 1.5, -RIB_WIDTH/2, TYPEBALL_TOP_ABOVE_CENTRE - TYPEBALL_TOP_THICKNESS - 0.8 * RIB_HEIGHT])
        cube([RIB_LENGTH, RIB_WIDTH, RIB_HEIGHT]);
    }
}

// tool for determining correct LETTER_HEIGHT
module TextGauge(str, pitch)
{
    color("red")
    for ( i = [0:len(str)] )
    {
        // scale factor from LetterText() function, must match!
        faceScale = 2.25;

        translate([8,8])
        translate([i*22/pitch,-LETTER_HEIGHT/2])
        scale([0.5,0.5,0.1])
        offset(CHARACTER_WEIGHT_ADJUSTMENT)
        text(size=LETTER_HEIGHT * faceScale, font=TYPEBALL_FONT, halign="center", str[i]);
    }
}

module TextGaugeComposer(str, unitdist)
{
    color("red")
    for ( i = [0:len(str)-1] )
    {
        // scale factor from LetterText() function, must match!
        
        faceScale = 2.25;

        translate([8,8])
        translate([CUMULATIVETESTSTRINGPICAS[i]*unitdist,-LETTER_HEIGHT/2])
        scale([0.5,0.5,0.1])
        offset(CHARACTER_WEIGHT_ADJUSTMENT)
        text(size=LETTER_HEIGHT * faceScale, font=TYPEBALL_FONT, halign="left", str[i]);
        echo(CUMULATIVETESTSTRINGPICAS[i]);
    }
}

function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec)-1; newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];