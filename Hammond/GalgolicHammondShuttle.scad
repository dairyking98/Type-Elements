//Layout=["-;p.lo,kimjunhybgtvfrcdexswzaq",
//        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
//        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1"];

//GALAGOLITIC

//       ⰀⰁⰂ ⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜ
//       ⰝⰞ  Ⱏ ⰠⰡ ⰢⰣ ⰤⰥ ⰦⰧ ⰨⰩ ⰪⰫ ⰬⰭ Ⱞ
Layout=["!?P.LO,KIMJUNHYBGTVFRCDEXSWZAQ",
        "ⰀⰁⰂ.ⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜ",
        "ⰝⰞ0.Ⱏ9ⰠⰡ8ⰢⰣ7ⰤⰥ6ⰦⰧ5ⰨⰩ4ⰪⰫ3ⰬⰭ2Ⱞ:1"];

GalChars="ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮ";
GalFont="Noto Sans Glagolitic";
GalFontSize=3;//.1

Galagolitic=[GalChars, GalFont, GalFontSize];


        
        
        
//DVORAK
//Layout=["zslvnrwtcmhgbdfxiykupje.qo,;a'",
//        "ZSLVNRWTCMHGBDFXIYKUPJE.QO?:A\"",
//        "/=0!)9°(8^☺7*&6¢_5£%4+$3×#2@-1"];




//DHIATENSOR
//Layout=["r, oyjsmqncbelvtugafkiwxhpzd.☺",
//        "R&☞OYJSMQNCBELVTUGAFKIWXHPZD.☼",
//        "0$ 9¢:8%#7?@6;)5!(4\"_3'^2/-1.☹"];
        
Print=true;
        
        //CAP chars that are FIGs to be FIG size
        CAPFIG_Mod="ⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝ";
        //LOWERCASE chars that must be added
        Lowercase_Mod="!?PLO,KIMJUNHYBGTVFRCDEXSWZAQ";
        //FIG chars that are duplicates and to be omitted
        FIG_Dupe=".";
        
OffsetChars=[["☼",1.4], ["☞",1.4]];
        
        
QP_Length=178;
ZExclamation_Length=200.4;
Center_to_Center_Height=40;
QW_Spacing=QP_Length/9;//21;
Y_Spacing=Center_to_Center_Height/2;//20;

row2_offset=2*QW_Spacing;
row3_offset=2/3*QW_Spacing;

//Height of FIGs from center
FIG_Offset=2.5;
//Height of LOWERCASE chars from center
Lowercase_Offset=-5.5;
//Height of CAPs chars from center
CAP_Offset=-4.5;
//Height of CAP char that is FIG dupe from center
FIG_Dupe_Offset=3;
//Height of CAP chars that are FIGs  from center
CAPFIG_Offset=-1.5;


//Legend font
Legend_Font="Franklin Gothic";
//CAP chars size
CAP_Size=6;
//FIGS size
FIG_Size=4;
//CAP chars that are FIGS size
CAPFIG_ModSize=4;

Circle_ID=14;
Circle_Thickness=.5;


module Text(n, size){

    ApplyGal=search(n, Galagolitic[0]);
    echo(ApplyGal);
    GalSize=ApplyGal==[]?size:Galagolitic[2];
    GalFont=ApplyGal==[]?Legend_Font:GalFont;

    text(text=n, size=GalSize, halign="center", valign="baseline", font=GalFont);
}


module Locate2(n){
    Y_Level=n%3;
    X_Column=n/3-n%3/3;
    
    
    
    RowSpaceMax=(ZExclamation_Length-QP_Length);
    
    ModRowSpace=RowSpaceMax*(n)/29;
    
    translate([X_Column*QW_Spacing+Y_Level/2*ModRowSpace, -Y_Level*Y_Spacing, 0])
    children();
}

module OutlinedCircle(){
    difference(){
        circle(d=Circle_ID+2*Circle_Thickness);
        circle(d=Circle_ID);
    }
}

module TextLayout2(){
    for (n=[0:1:len(Layout[0])-1]){
    
        
        
        CAPMod=search(Layout[1][29-n], CAPFIG_Mod);
        CAPSize=CAPMod==[]?CAP_Size:FIG_Size;
        
        LowercaseMod=search(Layout[0][29-n],Lowercase_Mod);
        LowercaseChar=LowercaseMod==[]?" ":Layout[0][29-n];
        
        FIGDupes=search(Layout[2][29-n], FIG_Dupe);
        FIGChar=FIGDupes==[]?Layout[2][29-n]:" ";
        
        Offset=search(Layout[1][29-n],OffsetChars);
        
        
        
        //CAP chars
        Locate2(n)
        translate([0, 
        (CAPMod==[]?CAP_Offset:0) +
        (FIGDupes==[]?0:FIG_Dupe_Offset) +
        (CAPMod==[]?0:CAPFIG_Offset) +
        (Offset==[]?0:OffsetChars[Offset[0]][1])
        
        , 0]) 
        Text(Layout[1][29-n],CAPSize);
        
        //FIG chars
        Locate2(n)
        translate([0, FIG_Offset, 0])
        Text(FIGChar,FIG_Size);
        
        //Lowercase chars
        Locate2(n)
        translate([0, Lowercase_Offset, 0])
        Text(LowercaseChar,FIG_Size);
        
        //Circles
        Locate2(n)
        OutlinedCircle();
    }
}

color("royalblue")

if (Print==true)
//linear_extrude(1)
Print();
//OutlinedCircle();
//Print();

module Print(){
difference(){
translate([ZExclamation_Length/2, -Center_to_Center_Height/2, 0])
cube([ZExclamation_Length+Circle_ID+5,Center_to_Center_Height+Circle_ID+5,  .1], center=true);
translate([0, 0, -.2])
linear_extrude(1)
TextLayout2();
echo ("Print Size= ", ZExclamation_Length+Circle_ID+5, Center_to_Center_Height+Circle_ID+5);
}
}