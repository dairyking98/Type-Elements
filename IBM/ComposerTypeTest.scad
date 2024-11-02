COMPOSER_PITCH_LIST=[
    ["A", 8], ["B", 7], ["C", 7], ["D", 8], ["E", 7], ["F", 7], ["G", 8], ["H", 8],
    ["I", 4], ["J", 5], ["K", 8], ["L", 7], ["M", 9], ["N", 8], ["O", 8], ["P", 6],
    ["Q", 8], ["R", 8], ["S", 6], ["T", 7], ["U", 8], ["V", 8], ["W", 9], ["X", 8],
    ["Y", 8], ["Z", 7], ["a", 5], ["b", 6], ["c", 5], ["d", 6], ["e", 5], ["f", 4],
    ["g", 5], ["h", 6], ["i", 3], ["j", 3], ["k", 6], ["l", 3], ["m", 9], ["n", 6],
    ["o", 6], ["p", 6], ["q", 6], ["r", 4], ["s", 4], ["t", 4], ["u", 6], ["v", 5],
    ["w", 8], ["x", 6], ["y", 6], ["z", 5], [".", 3], [",", 3], [":", 4], [";", 3],
    ["'", 3], ["*", 6], ["†", 6], ["(", 4], [")", 4], ["!", 4], ["$", 6], ["+", 6],
    ["/", 4], ["?", 5], ["-", 3], ["¾", 8], ["½", 8], ["&", 8], ["_", 8], ["%", 8],
    ["=", 6], ["[", 5], ["]", 6], ["@", 8], ["¼", 8], ["0", 6], ["1", 6], ["2", 6],
    ["3", 6], ["4", 6], ["5", 6], ["6", 6], ["7", 6], ["8", 6], ["9", 6], [" ", 3]
];

//Test string
TESTSTRING="Hello World!";
UNITSPERINCH=72;//[72:Red (12Units/Pica  72 Units/in), 84:Yellow (14Units/Pica  84 Units/in), 96:Blue (16 Units/Pica  96 Units/in)]
UNITDIST=25.4/UNITSPERINCH;
LETTER_HEIGHT=2;//.05
TYPEBALL_FONT="Arial";

TESTSTRINGPICAS = [0, for ( i = [0:len(TESTSTRING)] ) COMPOSER_PITCH_LIST[search(TESTSTRING[i], COMPOSER_PITCH_LIST)[0]][1]];

CUMULATIVETESTSTRINGPICAS = cumulativeSum(TESTSTRINGPICAS);

color("red")
TextGauge(TESTSTRING, UNITDIST);


module ComposerTextGauge(str, unitdist)
{
    for ( i = [0:len(str)-1] )
    {
        // scale factor from LetterText() function, must match!
        
        faceScale = 2.25;

        translate([8,8])
        translate([CUMULATIVETESTSTRINGPICAS[i]*unitdist,-LETTER_HEIGHT/2])
        scale([0.5,0.5,0.1])
        //offset(CHARACTER_WEIGHT_ADJUSTMENT)
        text(size=LETTER_HEIGHT * faceScale, font=TYPEBALL_FONT, halign="left", str[i]);
    }
}

function cumulativeSum(vec) = [for (sum=vec[0], i=1; i<=len(vec); newsum=sum+vec[i], nexti=i+1, sum=newsum, i=nexti) sum];