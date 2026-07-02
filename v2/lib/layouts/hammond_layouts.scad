//Hammond Shuttle layout data (v2.0 lib)
//Pure data, copied verbatim from Hammond/HammondShuttle.scad - no logic.
//The combinator array is renamed Layouts->LAYOUTS to match Bennett's
//all-caps convention for the raw preset list (Layout_Selection/Layout stay
//local to hammond.scad, matching Bennett's own Layout_Selection/Layout split).

//IDEAL LAYOUT
Normal_I=["qazwsxedcrfvtgbyhnujmik,ol.p;-",
         "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
         "1\"@2#×3$+4%£5_¢6&*7'^8(°9).0=/"];

//UNIVERSAL LAYOUT
Normal_U=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1"];

//MATH LAYOUT
Math_U=["√·p.lo,kimjunhybgtvfrcdexswzaq",
        "∫:P∂LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0>)9<(8|'7*÷6]Γ5[∝4+Δ3×∑2_\"1",
        "―ₙ₀πλ₉ωκ₈φε₇τη₆βγ₅θψ₄ρδ₃ξσ₂ζα₁"];

//ATTIC
Attic=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/»0´)9°(8§'7*&6¢~5†ˆ4\"$3«”2`“1"];

//GLAGOLITIC
Glagolitic=["!?P.LO,KIMJUNHYBGTVFRCDEXSWZAQ",
        "ⰀⰁⰂ.ⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜ",
        "ⰝⰞ0.Ⱏ9ⰠⰡ8ⰢⰣ7ⰤⰥ6ⰦⰧ5ⰨⰩ4ⰪⰫ3ⰬⰭ2Ⱞ:1"];

//Glagolitic secondary-font character set - Typeface_2Chars in hammond.scad's
//Glyph Quality section (renamed from GalChars to match the Typeface_2*
//naming already unified across every other v2 machine).
GlagoliticChars="ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮ";

////DVORAK LAYOUT
DVORAK=["zslvnrwtcmhgbdfxiykupje.qo,;a'",
        "ZSLVNRWTCMHGBDFXIYKUPJE.QO?:A\"",
        "/=0!)9°(8^☺7*&6¢_5£%4+$3×#2@-1"];

//BLICKENSDERFER
DHIATENSOR=["r,🯁oyjsmqncbelvtugafkiwxhpzd.☺",
        "R&🯂OYJSMQNCBELVTUGAFKIWXHPZD.☼",
        "0$🯃9¢:8%#7?@6;)5!(4\"_3'^2/-1.☹"];

//Comic Mono
Comic=["-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9•(8^'7*&6`_5>%4+$3<#2@\"1"];

LAYOUTS=[[0, Normal_U, "Normal Universal"],
        [1, Normal_I, "Normal Ideal"],
        [2, Math_U, "Math Universal", "Math"],
        [3, DVORAK, "Custom DVORAK Layout"],
        [4, DHIATENSOR, "Custom DHIATENSOR Layout"],
        [5, Comic, "Custom Comic Mono Layout"],
        [6, Glagolitic, "Custom Glagolitic Layout"],
        [7, Attic, "Attic Peter Weigel Modified"]
        ];
