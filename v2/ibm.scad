//dairy's rendition of ibm selectric type element model

//      credit where it is due: https://selectricrescue.org/

//
//                              Creation date: November 4, 2024
//Leonard Chau & Otto Koponen   December 1, 2024       t(-.-t)
//
//v2.0: IBM's spherical geometry (dual Composer/Selectric render modes,
//hemisphere-based character mapping) is genuinely different from the
//cylinder-family machines (Blick2/Postal/Bennett/Mignon/Helios), so it does
//NOT go through lib/glyph_pipeline.scad - kept fully self-contained, per
//docs/refactoring-plan.md. Only Global Parameters and Render Parameters
//(RENDER->Render, XSECTION->X_Section, XSECTION_THETA->X_Section_Theta,
//MINK_ON->Mink_On, MINKOWSKI_ANGLE->Mink_Draft_Angle, mink_fn/text_fn/cyl_fn/
//surface_fn->camelCase) were renamed to match the cylinder-family convention;
//everything else (the large majority of the file - typeface, testing,
//language/layout, typeball dimensions, labels, resin supports) keeps its
//original SCREAMING_SNAKE_CASE, since inventing cylinder-machine-style names
//for concepts with no cylinder-machine equivalent would be false consistency
//rather than real unification. The newer unified glyph-quality features
//(Weight_Adj_Mode, Character_Modifieds, Scale_Multiplier, Y_Scale,
//Typeface_2) were NOT added here - IBM's own Text()/SingleMinkowski() would
//need genuinely new code to support them, not just a rename, which was
//scoped out of this pass. Original preserved at IBM/IBM2.scad. This file was
//IBM2.scad, moved to v2/ibm.scad.
//
//Follow-up consistency pass: Global/Render Parameters reordered to the exact
//same relative order every other v2 machine now uses (z, Mink_Fn, Text_Fn,
//Cyl_Fn, Surface_Fn, [extras] / Render, [extras], Mink_On, Mink_Draft_Angle,
//X_Section, X_Section_Theta, [extras]) - previously IBM had Mink_On declared
//after X_Section instead of before, an inconsistency caught when auditing all
//8 v2 files' Global/Render Parameters side by side. Also simplified a
//leftover no-op `$fn=$preview?44:44;` (both ternary branches were identical)
//to a plain `$fn=44;`.

/* [Global Parameters] */

//to help with z fighting
z=.001;
//minkowski facet number
Mink_Fn=20;
//text facet number
Text_Fn=20;
//cylinder facet number
Cyl_Fn=360;
//surface facet number
Surface_Fn=120;
//IBM-only: fixed facet count independent of $preview (was written as
//$preview?44:44, a no-op ternary left over from editing - simplified to the
//same constant it always evaluated to).
$fn=44;

/* [Render Parameters] */

//Render something
Render=false;
//Render selection
Render_Mode=0;//[0:Composer (88char), 1:Selectric I/II (88char), 2:Selectric III (96char)]
//Render variant
Render_Variant=0;//[0:plain, 1:resin print top up, 2:type test]
//Turn on minkowski
Mink_On=false;
//Minkowski draft angle
Mink_Draft_Angle=55;
//View Cross section (reordered after Mink_On/Mink_Draft_Angle to match every
//other v2 machine's canonical Render Parameters order)
X_Section=false;
//Cross section angle
X_Section_Theta=0;
//Degrees to rotate ball when rendering to prevent artifacts due to element aligning with pixel grid.
Render_Degree_Offset=-3;
//Enable Minkowski flat offset
Mink_Flat=false;
//Minkowski offset from text surface
Mink_Flat_Offset=.0;//.01
Minkowski_Flat_Offset=Mink_Flat==true?Mink_Flat_Offset:0;
//Minkowski vertical offset in degrees
Minkowski_Longitudinal_Offsets=[0, 0, 0, 0];
//Minkowski bottom radius size
function MINK_TEXT_R(draft_angle)=2*tan(.5*draft_angle);



/* [Testing Stuff] */
include <lib/testing.scad>
//Render only selected characters
Selective_Render=false;
//Characters to render
Selective_Render_Chars="sine";
//Enable rays
Rays=false;

//character and point array for type testing composer
Composer_Pitch_List=[

    ["M", 9], ["W", 9], ["m", 9],
    
    ["A", 8], ["D", 8], ["G", 8], ["H", 8], ["K", 8], ["N", 8], ["O", 8], ["Q", 8], ["R", 8], ["U", 8], ["V", 8], ["X", 8], ["Y", 8], ["w", 8], ["¾", 8], ["½", 8], ["&", 8], ["%", 8], ["@", 8], ["¼", 8], ["–", 8], ["Ö", 8], ["Ä", 8], ["Å", 8], ["Ü", 8], ["Ñ", 8], ["¨", 8], ["`", 8], ["Ø", 8],["—", 8], ["€", 8],
    
    ["B", 7], ["C", 7], ["E", 7], ["F", 7], ["L", 7], ["T", 7], ["Z", 7],
    
    ["P", 6], ["S", 6], ["b", 6], ["d", 6], ["h", 6], ["k", 6], ["n", 6], ["o", 6], ["p", 6], ["q", 6], ["u", 6], ["x", 6], ["y", 6], ["*", 6], ["†", 6], ["$", 6], ["+", 6], ["=", 6], ["0", 6], ["1", 6], ["2", 6], ["3", 6], ["4", 6], ["5", 6], ["6", 6], ["7", 6], ["8", 6], ["9", 6], ["]", 6], ["ñ", 6], ["ø", 6], ["ü", 6], ["ß", 6], ["¡", 6], ["¿", 6], ["ö", 6], ["£", 6], ["§", 6],
    
    ["J", 5], ["a", 5], ["c", 5], ["e", 5], ["g", 5], ["v", 5], ["?", 5], ["[", 5], ["z", 5], ["ˆ", 5], ["´", 5], ["ü", 5], ["ö", 5], ["ä", 5], ["å", 5], ["ç", 5],
    
    ["I", 4], ["f", 4], ["r", 4], ["s", 4], ["t", 4], [":", 4], ["(", 4], [")", 4], ["!", 4], ["/", 4], ["(", 4], ["ı", 4], ["Æ", 4],["»", 4],
    
    ["i", 3], ["j", 3], ["l", 3], [".", 3], [",", 3], [";", 3], ["’", 3], ["‘", 3], ["-", 3], ["'", 3], ["æ", 3], [" ", 3]//apostrophe not native to Composer

];


//Test platen cutout offsets
Cutout_Test=false;
//Base tilt to start incrementing from
Cutout_Test_Start=0;//.05
//Interval of angle offsets to test
Cutout_Test_Angle_Int=.05;//.05

//individual platen cutout adjustment angles
Platen_Longitude_Offsets=[-1.05, -1.05, -1, -1.05];//.05

//Test minkowski draft angles
Draft_Angle_Test=false;
Draft_Angle_Test_Start=50;
Draft_Angle_Test_Int=1;

//Test minkowski longitudinal offsets
Mink_Long_Offset_Test=false;
Mink_Long_Offset_Test_Start=0;
Mink_Long_Offset_Test_Int=1;

//Test platen diameters
Platen_Diameter_Test=false;
Platen_Diameter_Test_Start=30;
Platen_Diameter_Test_Int=1;


//TEST_ARRAY_MAP was a pure identity map ([0,1,2,...21]) - dead indirection,
//replaced directly by testSweepArray's own n=[0:count-1] loop below.
Cutout_Test_Angle_Array=testSweepArray(Cutout_Test_Start, Cutout_Test_Angle_Int, 22);
Draft_Angle_Test_Array=testSweepArray(Draft_Angle_Test_Start, Draft_Angle_Test_Int, 22);
Mink_Long_Offset_Test_Array=testSweepArray(Mink_Long_Offset_Test_Start, Mink_Long_Offset_Test_Int, 22);
Platen_Diameter_Test_Array=testSweepArray(Platen_Diameter_Test_Start, Platen_Diameter_Test_Int, 22);

/* [Language and Custom Layout] */

//Composer Language preset
Composer_Language=0;//[0:United States,1:United Kingdom,2:Nordic,3:German,4:Latin, 5:Custom]

//Selectric I/II 88 character Language Preset
S12_88_Language=0;//[0:United States, 1:Custom]


//lowercase layout for custom keyboard
CUSTOMLOWERCASE88="

IIIIIIIIIIII
IIIIIIIIIII
IIIIIIIIIII
IIIIIIIIII

";

//uppercase layout for custom keyboard
CUSTOMUPPERCASE88="

IIIIIIIIIIII
IIIIIIIIIII
IIIIIIIIIII
IIIIIIIIII

";


CUSTOMCASES88=[CUSTOMLOWERCASE88, CUSTOMUPPERCASE88];

/* [Typeface Stuff] */

//element typeface
Font="Arial";
//selectric I/II type size
Font_Size=2.4;//.05
// Composer font Cap Height in points, use instead of Font_Size!
Composer_Cap_Height=7;
//all font sizes (Selectric III reuses Selectric I/II's Font_Size as a
//starting default - both are direct point-size, not Composer's cap-height
//convention - tune via Font_Size directly if Selectric III needs its own)
All_Font_Sizes=[Composer_Cap_Height/2.834, Font_Size, Font_Size];
//global font size
Font_Size_Selected=All_Font_Sizes[Render_Mode];
//secondary element typeface
Font2="Times New Roman";
//secondary type size
Font2_Size=2.4;//.05
// Composer font 2 Cap Height in points, use instead of Font_Size!
Composer2_Cap_Height=7;
//all font2 sizes (Selectric III reuses Selectric I/II's Font2_Size as a
//starting default, same reasoning as All_Font_Sizes above)
All_Font2_Sizes=[Composer2_Cap_Height/2.834, Font2_Size, Font2_Size];
//global font2 size
Font2_Size_Selected=All_Font2_Sizes[Render_Mode];
//list of chars to adopt font2 parameters
Font2_Chars="";
//custom horizontal alignment characters
CUSTOMHALIGNCHARS="";
//custom horizontal alignment characters offset. -left +right
CUSTOMHALIGNOFFSET=0.2;
//custom vertical alignment characters
CUSTOMVALIGNCHARS="";
//custom vertical alignment characters offset
CUSTOMVALIGNOFFSET=-0.2;
//type weight offset +/-
Font_Weight_Offset=0;//.01
//x weight adjustment 0+
X_Weight_Adjustment=.0;//.001
//y weight adjustment 0+
Y_Weight_Adjustment=.0;//.01
//x horiz alignment offset for composer
X_Pos_Offset_Composer_=1.20;
X_Pos_Offset_Composer=Cutout_Test==false?X_Pos_Offset_Composer_:0;//.01
//y vert alignment offset for composer
Y_Pos_Offset_Composer=-1.30;//1.01;//.01
//x horiz alignment offset for selectric 1/2
X_Pos_Offset_S12=0;//.01
//y vert alignment offset for selectric 1/2
Y_Pos_Offset_S12=-1.5;
//all y offsets (Selectric III reuses Selectric I/II's offset as a starting
//default - same class of machine/typeface convention, tunable if wrong)
All_Y_Offsets=[Y_Pos_Offset_Composer, Y_Pos_Offset_S12, Y_Pos_Offset_S12];
//all x offsets
All_X_Offsets=[X_Pos_Offset_Composer, X_Pos_Offset_S12, X_Pos_Offset_S12];
//global y offset
Y_Pos_Offset=All_Y_Offsets[Render_Mode];
//global x offset
X_Pos_Offset=All_X_Offsets[Render_Mode];
//all h alignments
All_H_Alignments=["left", "center", "center"];
//h alignment 
H_Alignment=Cutout_Test==true?"center":All_H_Alignments[Render_Mode];

/* [ Type Testing Stuff] */

//Type test text color
Type_Test_Color="red";//["red","black","white"]

//Use custom test string?
CUSTOM_TEST_STRING=false;

//custom string for type test
Test_String_Custom="Sphinx of black quartz, judge my vow";

//cumulative sum vector function for composer type test pitch array
function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec)-1; newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];
//composer cumulative picas per character array
//CUMULATIVETESTSTRINGPICAS = cumulativeSum(Test_String_Picas);
//cpi spacing for type test of selectric I/II
Test_CPI=10;
//unit spacing for type test of Composer
Units_Per_Inch=72;//[72:Red (12Units/Pica  72 Units/in), 84:Yellow (14Units/Pica  84 Units/in), 96:Blue (16 Units/Pica  96 Units/in)]
//mm distance per composer unit
Unit_Dist=25.4/Units_Per_Inch;

Arrow_Color=
    (Render_Mode==1)   ? "white":  //SI/II
    (Render_Mode==2)   ? "yellow": //SIII
    (Units_Per_Inch==72) ? "red":    
    (Units_Per_Inch==84) ? "yellow":
    (Units_Per_Inch==96) ? "blue":
    "white" // fallback
    ;

/* [Typeball Print Tolerances] */


Top_Flat_Thickness=3.5;
//shaft ID
Shaft_ID=8.8;
//shaft r
Shaft_R=Shaft_ID/2;
//boss OD
Boss_OD=11.6;
//boss minimum clearange
Boss_Clearance=2.5;//.1
//boss step thicknesss
Boss_Step=0;//.1
//platen diameter composer
Platen_OD_C=43;
//platen diameter selectric 1/2
Platen_OD_S12=36;
//platen diameter (Selectric III reuses Selectric I/II's platen - same class
//of typewriter platen, tunable via Platen_OD_S12 if it turns out different)
Platen_OD_All=[Platen_OD_C, Platen_OD_S12, Platen_OD_S12];
Platen_OD=Platen_OD_All[Render_Mode];
//drive notch width
Drive_Notch_Width=1.06;//.01
//drive notch height
Drive_Notch_Height=2.2;
echo("Top flat to boss face must measure at 8.5mm (Leo's measured value) or element is incorrectly represented. Adjust Snoot_Droop_Compensation up,lowering height of boss, until print yields 8.5mm boss height.");
//amount to compensate for vat-facing boss face !CRITICAL FEATURE!
Snoot_Droop_Compensation=.42;//.01



/* [Typeball Dimensions] */

//sphere diameter
Sphere_OD=33.4;
//sphere radius
Sphere_R=Sphere_OD/2;
//character-concave to character-concave diameter
Max_OD=34.9;
//sphere center to top flat
Top_Flat_To_Center=11.0;//leo's measured value. dave's was was 11.4;
//thickness of top flat
//top shaft chamfer
Top_Chamfer=.7;
//inside ID
Inside_ID=28.15;
//calculated value of sphere center to boss face
Boss_To_Center_=2.5;//leo's calculated value. dave's was 2.38 (calculated);
//top flat radius
Top_Flat_R=(Sphere_R^2-Top_Flat_To_Center^2)^.5;
//center to detent teeth tips of element
Floor=10.7;//abs(Top_Flat_To_Center-ELEMENT_OAT) = 10.7;
//Selectric III (96char) added a third render mode alongside Composer/
//Selectric I-II - both of the following are now indexed [Composer,
//Selectric I/II, Selectric III] rather than a single flat 88-char value.
//chars per row/hemisphere-ring (Composer and Selectric I/II are both 4
//rows of 22; Selectric III is 4 rows of 24 per docs.google-cited reference
//https://github.com/selectricrescueatx/TypeElements SelectricElement96.scad)
Chars_Per_Row_All=[22, 22, 24];
//total characters (4 rows x Chars_Per_Row_All)
Total_Chars_All=[88, 88, 96];
//hemisphere columns per row (half of Chars_Per_Row_All - upper/lowercase
//sit on opposite hemispheres, 180 degrees apart)
Hemisphere_Cols_Per_Row_All=[11, 11, 12];
//angle between characters around a ring (this is a LONGITUDE quantity -
//renamed from the previous Latitude_Spacing, which was backwards: rotating
//around the ring changes longitude, not latitude)
Longitude_Step=360/Chars_Per_Row_All[Render_Mode];
//skirt top OD
Skirt_Top_OD=32.3;
//skirt bottom OD
Skirt_Bottom_OD=30.2;
//overall thickness of element
//echo(str(Floor+Top_Flat_To_Center, " (modeled) = 21.7 (measured)? Leo's measured overall thickness?"));
//tilt angle of each of the 4 rows from the equator (this is a LATITUDE
//quantity - renamed from the previous Longitude_Spacing, which was
//backwards: this is each row's elevation from the equator, not a
//longitude). Shared across all 3 render modes (same physical ball for
//Composer/Selectric I-II; Selectric III reuses these exact measured values
//rather than the reference repo's own [31.1, 15.7, 0, -15.7] - both are
//close, these are the ones that have been measured/tuned here).
Row_Latitudes=[32.8, 16.4, 0, -16.4];
//drive notch theta from arrow
Drive_Notch_Theta_=131.0;//.01
//detent valley from center
Detent_Valley_To_Center=6;
//detent teeth clock offset
Detent_Skirt_Clock_Offset=0;//.01
//modeled boss to center value
Boss_To_Center=Boss_To_Center_+Snoot_Droop_Compensation;

/* [Label Stuff] */

//Enable label
Label=true;
//Enable arrow
Arrow=true;
//Label for number label. Disabled in Composer mode
Label_No = "10";
//Label override for typeface label (leave blank to adopt font name)
Label_Text_Override="";
//Font override for number label (leave blank to adopt element typeface)
Label_No_Font_Override="";
//Font override for typeface label (leave blank to adopt element typeface)
Label_Font_Override="";
//Font size for number label
No_Label_Size=2;//0.25
//Vertical offset for number label. +up -down
No_Label_Offset=0;//0.25
//Font size for typeface label 
Font_Label_Size=2;//0.25
//Weight offset for font label.
Label_Font_Weight_Offset=0;//0.01
//Vertical offset for font label. +up -down
Font_Label_Offset=0;//0.25
//arrow from center 
Del_Base_From_Centre = 8.2;
//Label deboss depth
Del_Depth = 0.6;

/* [Character Polar Positioning Offsets] */

//individual baseline adjustment angles
Baseline_Longitude_Offsets=[0, 0, 0, 0];//.05




//SOME CALCULATED VARIABLES:

//skirt large radius
Skirt_Top_R=Skirt_Top_OD/2;
//center to skirt of element
Center_To_Skirt=(Sphere_R^2-Skirt_Top_R^2)^.5;
//platen radius
//PLATEN_R=Platen_OD/2;
//height of letter
Type_Altitude=(Max_OD-Sphere_OD)/2;
//inside radius
Inside_R=Inside_ID/2;
//inside boss radius
Boss_R=Boss_OD/2;
//compensated drive notch theta
Drive_Notch_Theta=Drive_Notch_Theta_+Detent_Skirt_Clock_Offset;
//center to roof of element
Roof=Top_Flat_To_Center-Top_Flat_Thickness;


//Selectric I/II and Composer language layouts, hemisphere maps, and the
//language/mode selection logic that combines them (CASES88, HEMISPHERE_MAP,
//LONGITUDE_LATITUDE, etc.) all moved to lib/layouts/ibm_layouts.scad - pure
//data plus straightforward combining logic, no geometry. Needs CUSTOMCASES88
//(above), S12_88_Language, Composer_Language, and Render_Mode already
//defined, which they are by this point in the file.
include <lib/layouts/ibm_layouts.scad>

/* [Resin Supports] */

//tip diameter
Tip_D=.9;
//notch tip diameter
Tip_Notch_D=.4;
//deg offset from notch for notch supports
Tip_Notch_Offset=12;
//tip inset
Tip_In=.4;
//tip height
Tip_H=1;
//rod diameter
Rod_D=1.2;
//rod base diameter
Rod_Base_C=.5;
//rod radius
Rod_R=Rod_D/2;
//base diameter on buildplate
Base_D=4;
//base thickness
Base_H=2;
//minimum support height
Min_Rod_H=2;

/* [Experimental Drain Holes] */

//Drain hole type
Drain=0;//[0:None, 1:Pair, 2:Web]
//Hole ID
Web_ID=Boss_OD+1;
//Hole inner corner R
Web_IR=1;
//Hole outer corner R
Web_OR=2;
//web OD
Web_OD=Top_Flat_R*2-2;


//rays
module Rays(){
    for (col=[0:Chars_Per_Row_All[Render_Mode]-1])
    for (row=[0:3])
    rotate([0, Row_Latitudes[row], col*Longitude_Step])
    rotate([0, -90, 0])
    #cylinder(r=.1, h=20);
}

//make solid element
module FullBody(){
union(){
    $fn=Surface_Fn;
    sphere(d=Sphere_OD);
    translate([0, 0, -Floor])
    cylinder(d1=Skirt_Bottom_OD, d2=Skirt_Top_OD, h=Floor-Center_To_Skirt);
    AssembleMinkowski();
    }
}

//2d text
module Text(char, font, size, customhalign, customvalign){
    $fn = Mink_Fn;
    offset(Font_Weight_Offset)
    minkowski(){
        translate([X_Pos_Offset-customhalign, Y_Pos_Offset+customvalign, 0])
        mirror([1, 0, 0])
        text(char, size=size, font=font, valign="baseline", halign=H_Alignment, $fn=Text_Fn);
        if (X_Weight_Adjustment>0 || Y_Weight_Adjustment>0)
        square([z+X_Weight_Adjustment, z+Y_Weight_Adjustment], center=true);
    }
}

//platen cutout
module PlatenCutout(longitude, latitude,platendia){
            platenr=platendia/2;
            rotate([0, -latitude, longitude])
            translate([Sphere_R+platenr+Type_Altitude, 0, 0])
            rotate([90, 0, 0])
            cylinder(d=platendia, h=10, center=true, $fn=Cyl_Fn);        
}

//position extruded character
module PositionText(longitude, latitude){
    rotate([90 - latitude, 0, 90 + longitude])
    translate([0, 0, Sphere_R+z])
    children();
//    linear_extrude(6)
//    Text(char);
}

////minkowski single character
//module SingleMinkowski(char, font, size, customhalign, customvalign, longitude, latitude, plat_offset, base_offset, minklongoffset, draft_angle){
//    minkowski(){
//        difference(){
//            PositionText(longitude, latitude+base_offset)
//            linear_extrude(6)
//            Text(char, font, size, customhalign, customvalign);
//            PlatenCutout(longitude, latitude+plat_offset);
//            
//        }
//        if (Mink_On==true){
//            rotate([90 - latitude, 0, 90 + longitude])
//            hull(){
//                translate([0, 0, -2])
//                cylinder(r1=MINK_TEXT_R(draft_angle), d2=0, h=2, $fn=Mink_Fn);
//                if (minklongoffset!=0){
//                    rotate([-minklongoffset, 0, 0])
//                    translate([0, 0, -2])
//                    cylinder(r1=MINK_TEXT_R(draft_angle), d2=0, h=2, $fn=Mink_Fn);
//                }
//            }
//        }
//    }
//}
//SingleMinkowski("A", "Courier New", 3, 0, 0, 0, 0, 0, 0, 0, 65);
//minkowski single character
module SingleMinkowski(char, font, size, customhalign, customvalign, longitude, latitude, plat_offset, base_offset, minklongoffset, draft_angle,platendia){
    union(){
    if (Mink_Flat==true){
    difference(){
        PositionText(longitude, latitude+base_offset)
        linear_extrude(6)
        Text(char, font, size, customhalign, customvalign);
        PlatenCutout(longitude, latitude+plat_offset,platendia);
        }
        }
    minkowski(){
        difference(){
        PositionText(longitude, latitude+base_offset)
        linear_extrude(6)
        Text(char, font, size, customhalign, customvalign);
        PlatenCutout(longitude, latitude+plat_offset,platendia);
        
    }
        if (Mink_On==true){
            rotate([90 - latitude, 0, 90 + longitude])
            hull(){
                translate([0, 0, -2-Minkowski_Flat_Offset])
                cylinder(r1=MINK_TEXT_R(draft_angle), d2=0, h=2, $fn=Mink_Fn);
                if (minklongoffset!=0){
                echo(char, minklongoffset);
                    translate([0, 0, -Minkowski_Flat_Offset])
                    rotate([-minklongoffset, 0, 0])
                    translate([0, 0, -2])
                    cylinder(r1=MINK_TEXT_R(draft_angle), d2=0, h=2, $fn=Mink_Fn);
                }
            }
        }
    }
    }
}

//always-US reference layouts (independent of Composer_Language/
//S12_88_Language custom selection) - used only for the debug echo's
//"US KB Char" column below, so it stays a stable reference regardless of
//which language/custom layout is actually active.
All_US_Cases=[C_US, S12_US, S3_US];

//cutout test console output array
 //[ Element Row, Element Column, US KB Char, Cutout Offset Value, Draft Angle, Mink Long Offset]
Char_Info = [for (case_int=[0:1]) for (hemi_int=[0:Hemisphere_Cols_Per_Row_All[Render_Mode]*4-1]) [
    (LONGITUDE_LATITUDE[hemi_int][1]),
    (LONGITUDE_LATITUDE[hemi_int][0]+case_int*180/Longitude_Step),
    (All_US_Cases[Render_Mode][case_int][hemi_int]),
    Cutout_Test?(Cutout_Test_Angle_Array[(LONGITUDE_LATITUDE[hemi_int][0]*Longitude_Step+case_int*180)/Longitude_Step]):Platen_Longitude_Offsets[LONGITUDE_LATITUDE[hemi_int][1]],
    Draft_Angle_Test?Draft_Angle_Test_Array[(LONGITUDE_LATITUDE[hemi_int][0]+case_int*180/Longitude_Step)]:Mink_Draft_Angle,
    Mink_Long_Offset_Test?Mink_Long_Offset_Test_Array[(LONGITUDE_LATITUDE[hemi_int][0]+case_int*180/Longitude_Step)]:Minkowski_Longitudinal_Offsets[LONGITUDE_LATITUDE[hemi_int][1]],Platen_Diameter_Test?Platen_Diameter_Test_Array[(LONGITUDE_LATITUDE[hemi_int][0]+case_int*180/Longitude_Step)]:Platen_OD,
 ]];

Char_Info_Row_Sorted = [for (row=[0:3]) for (char=[0:Total_Chars_All[Render_Mode]-1]) if (Char_Info[char][0]==row) [row, Char_Info[char][1], Char_Info[char][2], Char_Info[char][3], Char_Info[char][4], Char_Info[char][5],Char_Info[char][6]]];

Char_Info_Row_Col_Sorted = [for (row=[0:3]) for (longitude=[0:Chars_Per_Row_All[Render_Mode]-1])  for (n=[0:Total_Chars_All[Render_Mode]-1]) if (Char_Info[n][1]==longitude && Char_Info[n][0]==row)  [Char_Info[n][0], Char_Info[n][1], Char_Info[n][2], Char_Info[n][3], Char_Info[n][4], Char_Info[n][5],Char_Info[n][6]]];

All_Render_Mode_Labels=["US Composer", "US Selectric1/2", "US Selectric3"];

module ConsoleCutout(){
    for (i=[0:Total_Chars_All[Render_Mode]-1])
    echo(str(All_Render_Mode_Labels[Render_Mode], " KB char = ", Char_Info_Row_Col_Sorted[i][2], " on row ", Char_Info_Row_Col_Sorted[i][0], " and longitude ", Char_Info_Row_Col_Sorted[i][1], " ––– cutout offset: ", Char_Info_Row_Col_Sorted[i][3], " ––– draft angle: ", Char_Info_Row_Col_Sorted[i][4], " ––– mink long offset: ", Char_Info_Row_Col_Sorted[i][5], " ––– platen diameter: ",Char_Info_Row_Col_Sorted[i][6]));
}

//assemble minkowski characters
module AssembleMinkowski(){
    rotate([0, 0, -5*Longitude_Step])
    for (case_int=[0:1])
    for (hemi_int=[0:Hemisphere_Cols_Per_Row_All[Render_Mode]*4-1]){

        char=CASES88[case_int][hemi_int];
        uskbchar=All_US_Cases[Render_Mode][case_int][hemi_int];
        longitude=LONGITUDE_LATITUDE[hemi_int][0]*Longitude_Step+case_int*180;
        latitude=Row_Latitudes[LONGITUDE_LATITUDE[hemi_int][1]];
        
        plat_offset_test=Cutout_Test==true?Cutout_Test_Angle_Array[longitude/Longitude_Step]:0;
        draft_angle=Draft_Angle_Test==true?Draft_Angle_Test_Array[longitude/21]:Mink_Draft_Angle;
        //mink_long_offset_test
        
//        if (Cutout_Test==true){
//            //echo (str("united states keyboard char = ", uskbchar, " , element row = ", LONGITUDE_LATITUDE[hemi_int][1], " (0=top, 3=bottom), platen cutout offset = ", plat_offset_test, " degrees"));
//        }
            
        plat_offset=Cutout_Test==false?Platen_Longitude_Offsets[LONGITUDE_LATITUDE[hemi_int][1]]:0;
        base_offset=Baseline_Longitude_Offsets[LONGITUDE_LATITUDE[hemi_int][1]];
        font=search(char, Font2_Chars)==[]?Font:Font2;
        size=search(char, Font2_Chars)==[]?Font_Size_Selected:Font2_Size_Selected;
        customhalign=search(char, CUSTOMHALIGNCHARS)==[]?0:CUSTOMHALIGNOFFSET;
        customvalign=search(char, CUSTOMVALIGNCHARS)==[]?0:CUSTOMVALIGNOFFSET;
        minklongoffset=Mink_Long_Offset_Test==false?Minkowski_Longitudinal_Offsets[LONGITUDE_LATITUDE[hemi_int][1]]:Mink_Long_Offset_Test_Array[longitude/21];
        platendia=Platen_Diameter_Test==true?Platen_Diameter_Test_Array[longitude/21]:Platen_OD;
        //echo(platendia);
        
        if (Selective_Render==true && search(char, Selective_Render_Chars)!= [])
        SingleMinkowski(char, font, size, customhalign, customvalign, longitude, latitude, plat_offset+plat_offset_test, base_offset, minklongoffset, draft_angle,platendia);
        
        else if (Selective_Render==true && search(char, Selective_Render_Chars)== []) {}
        
        else
        SingleMinkowski(char, font, size, customhalign, customvalign, longitude, latitude, plat_offset+plat_offset_test, base_offset,minklongoffset, draft_angle,platendia);
    }
   
}




//subtractive parts
module SolidCleanup(){
    //top flat
    translate([0, 0, Top_Flat_To_Center])
    cylinder(r=Top_Flat_R+2, h=10);
    //center shaft
    cylinder(d=Shaft_ID, h=40, center=true, $fn=Cyl_Fn);
    //center shaft top chamfer
    translate([0, 0, Top_Flat_To_Center-Top_Chamfer])
    cylinder(d1=Shaft_ID, d2=Shaft_ID+2*Top_Chamfer, h=Top_Chamfer, $fn=Surface_Fn);
    //inside radius
    translate([0, 0, -20])
    cylinder(d=Inside_ID, h=20+Boss_To_Center, $fn=Surface_Fn);
    //roof ish area
    rotate_extrude($fn=Surface_Fn)
    HollowProfile3();
    //notch
    Notch();
    //detent teeth
    rotate([0, 0, Detent_Skirt_Clock_Offset])
    Teeth();
    //drain holes
    if (Drain!=0)
    ArrangeDrain();
    if (Drain!=2){
        if (Arrow==true)
        Del();
        if (Label==true)
        FontName();}
}

//subtractive parts - inner radius : experimental
module HollowProfile3(){
    newroofr=1;
    hull(){
        translate([-newroofr+Inside_R, Boss_To_Center+Boss_Clearance, 0])
        circle(r=newroofr);
        translate([Boss_R+Boss_Step, 0, 0])
        square([Inside_R-Boss_R-Boss_Step, 1]);
        translate([Boss_R+newroofr+Boss_Step, Boss_To_Center+Boss_Clearance, 0])
        circle(r=newroofr);
        translate([(Inside_R+Boss_R+Boss_Step)/2, Top_Flat_To_Center-Top_Flat_Thickness-newroofr])
        circle(r=newroofr);

    }
    
    translate([Boss_R, 0, 0])
    square([Boss_Step+z, Boss_To_Center+Boss_Clearance]);
}

//detent tooth profile. Narrowed for render modes with more teeth per row
//than the 22 this profile was tuned for (e.g. Selectric III's 24) - same
//reasoning and ratio as the reference repo's own
//scale([1.0,88/96,1.0]) on this identical polygon, generalized to this
//codebase's per-mode Chars_Per_Row_All instead of a hardcoded 88/96.
module Tooth(){
    translate([0, Detent_Valley_To_Center, -Floor-z])
    rotate([180, -90, 0])
    scale([1, Chars_Per_Row_All[1]/Chars_Per_Row_All[Render_Mode], 1])
    {
        // notch between teeth must be big enough to trap detent
        linear_extrude(30)
        polygon(points=[[0,1.9], [2.2,0.4], [3.2,0.14], [3.2, -0.14], [2.2, -0.4], [0,-1.9]]);
    }
}

//detent teeth profile - one tooth per character index position (24 for
//Selectric III instead of 22, a real mechanical count, not cosmetic)
module Teeth(){
    for (i=[0:Chars_Per_Row_All[Render_Mode]-1])
    rotate([0, 0, i*Longitude_Step])
    Tooth();
}

//drive notch
module Notch(){
    rotate([0, 0, Drive_Notch_Theta])
    translate([Shaft_ID/2-.5, -Drive_Notch_Width/2, Boss_To_Center-z])
    cube([4, Drive_Notch_Width, Drive_Notch_Height+Snoot_Droop_Compensation+z]);
}

//full body minus subtractive parts
module SubtractFromFull(){
    difference(){
        FullBody();
        SolidCleanup();
    }
    
    if (Rays==true)
    Rays();
}

//resin support tip, angle input, tip d
module ResinTip(a1,d){
    rotate([0, a1, 0])
    hull(){
        sphere(d=d);
        translate([0, 0, -Tip_H])
        sphere(d=Rod_D);
    }
}

//get rotated resin support tip x offset function
function ResinXOffset(a1)= sin(a1)*Tip_H;

//resin support rod, height, tip angle, tip diameter
module ResinRod(h, a1, d){
    xoffset = ResinXOffset(a1);
    translate([-xoffset, 0]){
        //base
        translate([0, 0, -Min_Rod_H-Base_H-Tip_H])
        cylinder(d1=Base_D, d2=Base_D+2*Base_H, h=Base_H);
        
        //rod
        hull(){
            translate([0, 0, -Tip_H+h-Tip_D/2+Tip_In])
            sphere(d=Rod_D);
            translate([0, 0, -Min_Rod_H-Base_H+Rod_D/2-Tip_H])
            sphere(d=Rod_D);
        }
        //base-rod chamfer
        translate([0, 0, -Min_Rod_H-Tip_H-z])
        cylinder(d1=Rod_D+2*Rod_Base_C, d2=Rod_D, h=Rod_Base_C);
    }
    //tip
    translate([0, 0, h-Tip_D/2+Tip_In])
    ResinTip(a1, d);
}

//assemble resin support rods
module ResinRodAssemble(){
    for (i=[0:Chars_Per_Row_All[Render_Mode]-1])

        //detent teeth supports
        rotate([0, 0, i*Longitude_Step+Detent_Skirt_Clock_Offset])
        translate([(Skirt_Bottom_OD+Inside_ID)/4, 0, 0])
        ResinRod(0, 0, Tip_D);
    
    //boss supports
    for (i=[0:11]){
        rotate([0, 0, i*360/11]){
        
            //roof-roof support-supports
            hull(){
                    translate([(Boss_R+Inside_R+Boss_Step)/2, 0, 6])
                    sphere(d=Rod_D);
                    rotate([0, 0, 360/11])
                    translate([(Boss_R+Inside_R+Boss_Step)/2, 0, 0])
                    sphere(d=Rod_D);
            }
            
        if (i!=4){
        
            //boss supports (outer corner)
//            translate([Boss_R, 0, 0])
//            ResinRod(Floor+Boss_To_Center, -45, Tip_D);
            
            //boss supports (directly under)
            translate([(Boss_R+Shaft_ID/2)/2, 0, 0])
            ResinRod(Floor+Boss_To_Center, 0, Tip_D);
            
            
            //boss-roof support-supports
            hull(){
//                translate([Boss_R-ResinXOffset(-45), 0, 12])//outer corner
                translate([(Boss_R+Shaft_ID/2)/2, 0, 12])//directly under
                sphere(d=Rod_D);
                translate([(Boss_R+Inside_R+Boss_Step)/2, 0, 8])
                sphere(d=Rod_D);
            }

            
            if (i!=3)
            //boss-boss support-supports
                hull(){
//                    translate([Boss_R-ResinXOffset(-45), 0, 1])//outer corner
                    translate([(Boss_R+Shaft_ID/2)/2-ResinXOffset(0), 0, 1])//directly under
                    sphere(d=Rod_D);
                    rotate([0, 0, 360/11])
//                    translate([Boss_R-ResinXOffset(-45), 0, 7])//outer corner
                    translate([(Boss_R+Shaft_ID/2)/2-ResinXOffset(0), 0, 7])//directly under
                    sphere(d=Rod_D);
                }
        }
        
        //roof supports
        translate([(Boss_R+Inside_R+Boss_Step)/2, 0, 0])
        ResinRod(Floor+Roof, 0, Tip_D);
        }
        
        
    //for notch supports
    n=Tip_Notch_Offset;//degrees off from notch 
    l=[3, 5];
    k=[n, -n];
    if (i==4)
        for (j=[0, 1]){
            //notch supports
            rotate([0, 0, Drive_Notch_Theta+k[j]])
//            translate([Boss_R, 0, 0])//outer corners
            translate([(Boss_R+Shaft_ID/2)/2, 0, 0])//directly under
            
            
//            ResinRod(Floor+Boss_To_Center, -45, Tip_Notch_D);//outer corners
            ResinRod(Floor+Boss_To_Center, 0, Tip_Notch_D);//directly under
            //notch support supports
            hull(){
                rotate([0, 0, Drive_Notch_Theta-k[j]])
//                translate([Boss_R-ResinXOffset(-45), 0, 12])//outer corners
                translate([(Boss_R+Shaft_ID/2)/2-ResinXOffset(0), 0, 12])//directly under
                sphere(d=Rod_D);
                rotate([0, 0, l[j]*360/11])
//                translate([Boss_R-ResinXOffset(-45), 0, 7])//outer corners
                translate([(Boss_R+Shaft_ID/2)/2-ResinXOffset(0), 0, 7])//directly under
                sphere(d=Rod_D);
            }
        }
    }
}

//assemble resin print
module ResinPrint(){
    union(){
    translate([0, 0 , Floor])
    SubtractFromFull();
    ResinRodAssemble();
    }
}

//monospaced type test gauge
module TextGauge(str, pitch)
{
    color(Type_Test_Color)
    for ( i = [0:len(str)] )
    {
        translate([8,8])
        translate([i*22/pitch, 0, 0])
        offset(Font_Weight_Offset)
        text(size=Font_Size_Selected, font=Font, halign="center", str[i]);
    }
}

//2d web shape
module TwoDWeb(){
hull(){
translate([Web_ID/2+Web_IR, 0, 0])
circle(r=Web_IR);
translate([Web_OD/2-Web_OR, 0, 0])
circle(r=Web_OR);
}
}

//extruded web hole
module ExtrudedWeb(){
    translate([0, 0, Roof-5])
    linear_extrude(8)
    TwoDWeb();
    translate([0, 0, Top_Flat_To_Center-Top_Chamfer])
    hull(){
    linear_extrude(z)
    TwoDWeb();
    translate([0, 0, Top_Chamfer+z])
    linear_extrude(z)
    offset(Top_Chamfer)
    TwoDWeb();
    }
}

//drain holes arranged
module ArrangeDrain(){
    for (i=[0:11])
        if (Drain==1 && i!=2&&i!=8){}
        else{
            rotate([0, 0, i*360/11+360/22])
            ExtrudedWeb();
            }
}


//render code
module Render(){
    if (Render==true){
        difference(){
            if (Render_Variant==0)
                SubtractFromFull();
            if (Render_Variant==1)
                ResinPrint();
            if (Render_Variant==2){
                if (Render_Mode==0)
                    TextGaugeComposerLine2(KBSTRING, Unit_Dist);
                if (Render_Mode==1 || Render_Mode==2)
                    TextGauge(Test_String_Custom, Test_CPI);
            }
            if (X_Section==true && Render_Variant!=2)
            rotate([0, 0, X_Section_Theta-90])
            translate([0, -50, -50])
            cube(100);
        }
        if (Cutout_Test==true||Draft_Angle_Test==true||Mink_Long_Offset_Test==true||Platen_Diameter_Test==true){
        ConsoleCutout();}
    }
}

// Alignment marker triangle on top face
module Del()
{
    translate([Del_Base_From_Centre, 0, Top_Flat_To_Center - Del_Depth])
    color(Arrow_Color)
    linear_extrude(Del_Depth+z)
    polygon(points=[[3.4,0],[0.4,1.3],[0.4,-1.3]]);
}

// Emboss a label onto top face
module FontName()
{
    translate([-8.5, 0, Top_Flat_To_Center - Del_Depth])
    color("darkslategrey")
    rotate([0,0,270])
    linear_extrude(Del_Depth+0.01)
    offset(Label_Font_Weight_Offset)
    Labels();
}

// Labels on the top of the ball, cosmetic
module Labels()
{
    {
        // Disable Label No for Composer balls
        if (Render_Mode!=0) { 
            translate([-0.1+No_Label_Offset,14,0])
        text(Label_No, size=No_Label_Size, font=Label_No_Font_Override==""?Font:Label_No_Font_Override, halign="center");
    }
        translate([0,0.6+Font_Label_Offset,0])
        text(Label_Text_Override==""?Font:Label_Text_Override, size=Font_Label_Size, font=Label_Font_Override==""?Font:Label_Font_Override, halign="center");
        
    }
}

//create array of picas per test string character function
function TestStringPicas(string)=[0, for ( i = [0:len(string)-1] ) SearchChar(string[i])==undef?9:Composer_Pitch_List[SearchChar(string[i])][1]];


//search char in composer list and return its units of spacing
function SearchChar(char)=search(char, Composer_Pitch_List)[0];

//get row of char with integer of keyboard input
function GetRow(int) =
    int <= 11 ? 0 :
    int <= 22 ? 1 :
    int <= 33 ? 2 :
    int <= 43 ? 3 :
    int <= 55 ? 4 :
    int <= 66 ? 5 :
    int <= 77 ? 6 : 7;

//composer type test gauge keyboard with keyboard string input
module TextGaugeComposerLine2(string, unitdist)
{
Str_Overridden = CUSTOM_TEST_STRING?Test_String_Custom:string;
Test_String_Picas = TestStringPicas(Str_Overridden);
Cum_Sum_Test_String_Picas = cumulativeSum(Test_String_Picas);
Cum_Sum_Test_String_Picas_Per_Line = [for (a=[0,12,23,34,44,56,67,78]) Cum_Sum_Test_String_Picas[a]];
    color(Type_Test_Color)
    for ( i = [0:len(Str_Overridden)-1] )
    {
        font=search(Str_Overridden[i], Font2_Chars)==[]?Font:Font2;
        size=search(Str_Overridden[i], Font2_Chars)==[]?Font_Size_Selected:Font2_Size_Selected;          
        customhalign=search(Str_Overridden[i], CUSTOMHALIGNCHARS)==[]?0:CUSTOMHALIGNOFFSET;
        customvalign=search(Str_Overridden[i], CUSTOMVALIGNCHARS)==[]?0:CUSTOMVALIGNOFFSET;
        row=CUSTOM_TEST_STRING?0:GetRow(i);
        echo(row);
        
        
        translate([10, -10, 0])
        translate([customhalign-Cum_Sum_Test_String_Picas_Per_Line[row]*unitdist, customvalign-Font_Size_Selected*2*row, 0])
        translate([Cum_Sum_Test_String_Picas[i]*unitdist,0])
        
        offset(Font_Weight_Offset)
        text(size=size, font=font, halign="left", Str_Overridden[i]);
    }
}

//Apply Render_Degree_Offset
rotate([0,0,$preview?0:Render_Degree_Offset])

///EXECUTE CODE:
Render();