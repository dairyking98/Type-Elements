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



//all keyboard layouts
ALL88CASES=[COMPOSERCASES88, S12CASES88];



//set keyboard layout for character mapping
CASES88=ALL88CASES[Render_Mode];

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
ALL88HEMIS=[COMPOSER_HEMISPHERE_MAP, S12_HEMISPHERE_MAP];

HEMISPHERE_MAP=ALL88HEMIS[Render_Mode];

//echo(HEMISPHERE_MAP);
//create latitude, longitude integer array for one hemisphere
LATITUDE_LONGITUDE = [for (i=[0:len(HEMISPHERE_MAP)-1]) [HEMISPHERE_MAP[i][0]%11, ceil(HEMISPHERE_MAP[i][0]/11+.001)-1, CASES88[0][i], i]];
