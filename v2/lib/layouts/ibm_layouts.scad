//IBM Selectric I/II + Composer layout data (v2.0 lib)
//Extracted from IBM2.scad. Pure data plus the straightforward language/mode
//selection logic that combines it - no geometry. Mirrors the same pattern as
//lib/layouts/bennett_layouts.scad: the CUSTOM entry point (CUSTOMCASES88)
//stays in ibm.scad itself (matching Bennett's CUSTOMLAYOUT staying local),
//so this file must be included AFTER CUSTOMCASES88 is defined. Also needs
//S12_88_Language, Composer_Language, and Render_Mode defined first (all in
//ibm.scad, earlier in the file).

/* [ Hidden] */
//Character Mapping - Selectric I/II 88char

//lowercase selectric 1/2 layout on machine; left to right, top to bottom
LOWERCASE88_US="
1234567890-=
qwertyuiop½
asdfghjkl;'
zxcvbnm,./
";

//uppercase selectric 1/2 layout on machine; left to right, top to bottom
UPPERCASE88_US="
!@#$%¢&*()_+
QWERTYUIOP¼
ASDFGHJKL:\"
ZXCVBNM,.?
";


//lowercase hemisphere of selectric 1/2 element from the top moving counter clockwise, top to bottom
S12_LC_HEMISPHERE88_US="
90652z48731
bhkentlcdux
wsi'.½oarvm
-yqp=j/,;fg
";

S12_US=[LOWERCASE88_US,UPPERCASE88_US];


S12_US_HEMISPHERE88=S12_LC_HEMISPHERE88_US;//I dont think hemisphere positions for keyboard to element will change for different languages

ALL_S12=[S12_US, CUSTOMCASES88];

S12CASES88=ALL_S12[S12_88_Language];

//Character Mapping - Selectric III 96char. Source: the reference repo
//https://github.com/selectricrescueatx/TypeElements (SelectricElement96.scad,
//CC BY 4.0, Dave Hayden/Steve Malikoff)'s LOWER_CASE/UPPER_CASE + charmap96 -
//see CHANGELOG.md for the derivation. Supersedes an earlier abandoned draft
//that had a bug (rows 2-3 still capitalized) and didn't include the extra
//²/§/³/¶ characters (on the ball but not reachable via the S3 keyboard,
//per the reference repo's own comment).

//lowercase selectric 3 layout on machine; left to right, top to bottom
LOWERCASE96_US="
±1234567890-=
qwertyuiop½]
asdfghjkl;'
zxcvbnm,./
²§
";

//uppercase selectric 3 layout on machine; left to right, top to bottom
UPPERCASE96_US="
°!@#$%¢&*()_+
QWERTYUIOP¼[
ASDFGHJKL:\"
ZXCVBNM,.?
³¶
";

S3_US=[LOWERCASE96_US, UPPERCASE96_US];

//lowercase hemisphere of selectric 3 element from the top moving counter
//clockwise, top to bottom. Row characters are re-derived from charmap96 -
//the FIRST derivation (matching charmap96's own column order p=0..11
//directly) rendered with the longitudinal order swapped/mirrored, caught by
//checking against a real Selectric III element. Reversing each row's
//column order fixed it, confirmed against the user's physical element -
//and this reversed order also happens to closely match (with 2 minor
//transcription typos fixed) an earlier abandoned draft of this same data.
S3_LC_HEMISPHERE96="
z²752064893/
;'istecbku§=
vmwdornaxh½±
-1.jqpyflg],
";

S3_US_HEMISPHERE96=S3_LC_HEMISPHERE96;//same reasoning as S12_US_HEMISPHERE88 - shift-case symmetry (charmap96 uses the same physical-position index for both cases), so uppercase reuses the lowercase hemisphere positions rather than needing its own map.

//hardcoded result of [for (i=[0:len(LOWERCASE96_US)-1]) search(LOWERCASE96_US[i], S3_LC_HEMISPHERE96)] - computed once with openscad-nightly, same as S12_HEMISPHERE_MAP below.
S3_HEMISPHERE_MAP = [[35], [37], [4], [10], [7], [3], [6], [2], [8], [9], [5], [36], [23], [40], [26], [17], [29], [16], [42], [21], [14], [28], [41], [34], [46], [31], [15], [27], [43], [45], [33], [39], [20], [44], [12], [13], [0], [32], [18], [24], [19], [30], [25], [47], [38], [11], [1], [22]];

/* [ Hidden ] */
// Character Mapping - Composer 88char

//uppercase composer layout on machine; left to right, top to bottom

//United States lowercase
LOWERCASECOMPOSER_US ="
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
";

//lowercase hemisphere of composer element from the top moving counter clockwise, top to bottom
C_US_HEMISPHERE88="
.,634s10928
?-[cliatb75
xvumhnrodwk
=]zpyefgq;j
";

//lowercase composer layout on machine; left to right, top to bottom

//United States uppercase
UPPERCASECOMPOSER_US ="
!†+$%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
";

//United Kingdom lowercase
LOWERCASECOMPOSER_UK ="
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
";

//United Kingdom uppercase
UPPERCASECOMPOSER_UK ="
!†+£%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
";

//Nordic lowercase
LOWERCASECOMPOSER_NO ="
1234567890-ø
qwertyuiopå
asdfghjklöä
zxcvbnm,.;
";

//Nordic uppercase
UPPERCASECOMPOSER_NO ="
»!?§%/&=()–Ø
QWERTYUIOPÅ
ASDFGHJKLÖÄ
ZXCVBNM‘’:
";

//Germany lowercase
LOWERCASECOMPOSER_DE ="
1234567890-ß
qwertyuiopü
asdfghjklöä
zxcvbnm,.;
";

//Germany uppercase
UPPERCASECOMPOSER_DE ="
!=+§%/&*()–?
QWERTYUIOPÜ
ASDFGHJKLÖÄ
ZXCVBNM‘’:
";


//Latin lowercase
LOWERCASECOMPOSER_LA ="
1234567890-ñ
qwertyuiopˆ
asdfghjkl´ç
zxcvbnm,.;
";

//Latin uppercase
UPPERCASECOMPOSER_LA ="
ı¿¡$!/&*()–Ñ
QWERTYUIOP¨
ASDFGHJKL`?
ZXCVBNM‘’:
";


C_US=[LOWERCASECOMPOSER_US,UPPERCASECOMPOSER_US];
C_UK=[LOWERCASECOMPOSER_UK,UPPERCASECOMPOSER_UK];
C_NO=[LOWERCASECOMPOSER_NO,UPPERCASECOMPOSER_NO];
C_DE=[LOWERCASECOMPOSER_DE,UPPERCASECOMPOSER_DE];
C_LA=[LOWERCASECOMPOSER_LA,UPPERCASECOMPOSER_LA];

ALL_C=[C_US, C_UK, C_NO, C_DE, C_LA, CUSTOMCASES88];

COMPOSERCASES88=ALL_C[Composer_Language];



//all keyboard layouts (Selectric III has no custom-language variant yet,
//unlike Composer/Selectric I-II - S3_US used directly)
ALL_CASES=[COMPOSERCASES88, S12CASES88, S3_US];



//set keyboard layout for character mapping
CASES88=ALL_CASES[Render_Mode];

//keyboard string
KBSTRING=str(CASES88[0], CASES88[1]);

//create lowercase layout to us element hemisphere map
LC_LAYOUT_TO_HEMISPHERE_MAP = [for (i=[0:len(S12_US[0])-1]) search(S12_US[0][i], S12_US_HEMISPHERE88)];

//echo(LC_LAYOUT_TO_HEMISPHERE_MAP);

//hardcoding of LC_LAYOUT_TO_HEMISPHERE_MAP:

S12_HEMISPHERE_MAP = [[10], [4], [9], [6], [3], [2], [8], [7], [0], [1], [33], [37], [35], [22], [14], [30], [16], [34], [20], [24], [28], [36], [27], [29], [23], [19], [42], [43], [12], [38], [13], [17], [41], [25], [5], [21], [18], [31], [11], [15], [32], [40], [26], [39]];

//create lowercase us layout to us element hemisphere map for composer
LC_COMP_LAYOUT_TO_HEMISPHERE_MAP = [for (i=[0:len(C_US[0])-1]) search(C_US[0][i], C_US_HEMISPHERE88)];

//echo(LC_COMP_LAYOUT_TO_HEMISPHERE_MAP);

//hardcoding of LC_COMP_LAYOUT_TO_HEMISPHERE_MAP:

COMPOSER_HEMISPHERE_MAP = [[6], [9], [3], [4], [21], [2], [20], [10], [8], [7], [12], [33], [41], [31], [38], [28], [18], [37], [24], [16], [29], [36], [11], [17], [5], [30], [39], [40], [26], [43], [32], [15], [34], [13], [35], [22], [14], [23], [19], [27], [25], [1], [0], [42]];

////all hemisphere layouts
ALL_HEMISPHERE_MAPS=[COMPOSER_HEMISPHERE_MAP, S12_HEMISPHERE_MAP, S3_HEMISPHERE_MAP];

HEMISPHERE_MAP=ALL_HEMISPHERE_MAPS[Render_Mode];

//echo(HEMISPHERE_MAP);
//create longitude (ring position), latitude (row) integer array for one
//hemisphere - field order matches the corrected LONGITUDE_LATITUDE name
//(previously LATITUDE_LONGITUDE, which had it backwards: field[0] is a
//ring/longitude position, field[1] is a row/latitude index)
LONGITUDE_LATITUDE = [for (i=[0:len(HEMISPHERE_MAP)-1]) [HEMISPHERE_MAP[i][0]%Hemisphere_Cols_Per_Row_All[Render_Mode], ceil(HEMISPHERE_MAP[i][0]/Hemisphere_Cols_Per_Row_All[Render_Mode]+.001)-1, CASES88[0][i], i]];
