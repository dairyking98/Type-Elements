//Split Hammond 1 Shuttle
//Leonard Chau
//Jan 14, 2026
//
//v2.0: NOT wired into lib/glyph_pipeline.scad. Unlike HammondShuttle.scad
//(hammond.scad), this file's glyph pipeline builds two independent half-rings
//(TextAssemble(side) with its own per-side angle-sign/character-index
//formula) trimmed via intersection() with Arc() rather than a platen cutout,
//and has none of the shared lib's weight-adjust modes, Character_Modifieds
//baseline offset, Typeface_2, or Scale_Multiplier features - a bigger
//structural gap than HammondShuttle.scad had, closer to IBM's "different
//beast" spherical geometry than to the cylinder-family machines. Forcing it
//into the lib would mean inventing a two-sided wrapper and extending the lib
//for the Arc-intersection trim rather than a straightforward parameter
//mapping, so this file gets the same treatment as ibm.scad and hammond.scad's
//body/resin geometry for now: matching section headers plus safe renames
//only, no forced lib wiring, no new features invented for code untouched
//here. Confirmed with the user (re-asked after the first attempt got no
//response): keep this scope for now, but flagged as a real candidate for a
//follow-up pass unifying BOTH Hammond machines' glyph pipelines together,
//since hammond.scad and hammond_split.scad are more similar to each other
//(and to the cylinder family) than either is to IBM.
//
//Renames: render->Render (matches every other v2 machine's toggle name) -
//the original also had a wrapper `module Render(){ if(render==true){...} }`,
//which would collide with a variable named Render, so that wrapper is
//inlined into the standard `if (Render==true){...}` top-level gate instead
//(the same pattern every other v2 file already uses). Cyl_Fn/Mink_Fn/Text_Fn/
//Resin_Fn were already camelCase, no change needed. Original preserved at
//Hammond/HammondSplitShuttle2.scad. This file was HammondSplitShuttle2.scad,
//moved to v2/hammond_split.scad.
//
//Follow-up consistency pass: split the single merged "[Rendering]" section
//into the same Global Parameters / Render Parameters split every other v2
//machine uses, and renamed minkText->Mink_On, minkAngle->Mink_Draft_Angle to
//match every other machine's toggle/angle names - same concept, confirmed by
//the formula: Mink_Radius=tan(minkAngle/2)*Mink_Height reduces to exactly the
//shared lib's minkTextR(angle)=2*tan(.5*angle) once Mink_Height's default (2)
//is substituted in, so this was a pure rename, not a behavior change.
//Mink_Height/Mink_Radius have no equivalent elsewhere (this file's cone is
//parameterized by an explicit height rather than the lib's implicit h=2) and
//stay as hammond_split-only extras.

/* [Global Parameters] */
//to help with z fighting
z=.01;
//minkowski facet number
Mink_Fn=20;
//text facet number
Text_Fn=30;
//cylinder facet number
Cyl_Fn=120;
//resin support facet number
Resin_Fn=20;

/* [Render Parameters] */
//render something? (renamed from render)
Render=false;
//render mode
Render_Mode=1;//[0:Normal, 1:ResinPrint, 2:Type Test]
//render left shuttle?
Render_Left=true;
//render right shuttle?
Render_Right=true;
//turn minkowski on (renamed from minkText)
Mink_On=false;
//mink draft angle (renamed from minkAngle)
Mink_Draft_Angle=60;
//mink cone height - hammond_split-only extra, no equivalent elsewhere
Mink_Height=2;
//mink radius - hammond_split-only extra, derived the same way the shared
//lib's minkTextR() function does (see note above)
Mink_Radius=tan(Mink_Draft_Angle/2)*Mink_Height;

/* [Key Mapping] */
Ideal_Element=["?zxqkjgdmpcfld,.taherisounwyv:",
       "!ZXQKJGDMPCFLD;-TAHERISOUNWYV&",
       "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔"];

Qwerty_Element = ["qazwsxedcrfvtgbyhnujmik,ol.p;-",
          "QAZWSXEDCRFVTGBYHNUJMIK?OL.P:!",
          "1\"@2#⅌3$+4%£5_¢6&*7'§8(°9).0=/"];

Layouts = [[0, Ideal_Element],
            [1, Qwerty_Element]];
Layout_Selection = 0; //[0:Ideal, 1:Qwerty]
Layout=Layouts[Layout_Selection][1];

/* [Typeface Stuff] */
//font name
Type_Face="Average Mono";
//font size
Type_Size=2.95;
//modified characters
Char_Mod="⅌";
//modified character font
Char_Mod_Font="Noto Sans Mono";
//modified character size
Char_Mod_Size=2.7;

/* [Element Dimensions] */
//baseline gaps
Baseline_Gaps=[9.45, 4.725, 0];
//baseline offset
Baseline_Offset=-1.9;
//Baselines
Baselines=Baseline_Gaps+[Baseline_Offset, Baseline_Offset, Baseline_Offset];
//pin hole diameter
Pin_ID_Mm=1.92;
//pin hole radial distance
Pin_Radial=7.95;
//pin holes angular positions
Pin_Theta=[68.2683, 109.968];
//pin hole chamfer
Pin_ID_Chamfer=.25;
//left and right tube diameters
Tube_OD_Mm=[6.6548, 5.842];
//tube chamfer size
Tube_Chamfer=.5;
//Arc diameter
Arc_OD=75;
//Arc thickness
Arc_Thickness=1.6;
//Arc height
Arc_Height=13.26;
//Arc height offset
Arc_Height_Offset=-2.62;
//folder degree offset from center
Folder_Degree_Offset=8.3;
//folder degree rotational extrusion
Folder_Degrees=115.8;
//folding section ID
Folder_ID_Mm=12;
//folding section OD
Folder_OD=21;
//folder thickness
Folder_Thickness=9.525;
//folder close angular gap
Folder_Close_Gap=6;
Folder_Arc_Start=Folder_Close_Gap/2;
Folder_Glue_Hole_ID_Mm=1.15;
Folder_Glue_Groove_R=.8;
Folder_Glue_Groove_Depth=.2;
//glyph height
Glyph_Height=.8;
//alignment finger tip width
Finger_Thickness=1.8;
//spoke thickness
Spoke_Thickness=2.2;
//spoke height
Spoke_Height=8.3;
//spoke count
Spoke_Count=5;
//spoke angular extent
Spoke_Extent=45;
//spoke spacing
Spoke_Spacing=Spoke_Extent/(Spoke_Count-1);
//spoke chamfer size
Spoke_Chamfer=1.5;
//rib OD
Rib_OD=46.8;
//rib thickness
Rib_Thickness=2.6;
//rib radius
Rib_Radius=1;
//degrees per character
Char_Theta=360/96;

/* [Logo] */
//enable Logo?
Logo=true;
//Logo text
Logo_Text_1="Leonard Chau";
Logo_Text_2="2025";
//Logo font
Logo_Font="OCR\\A-II";
//Logo size
Logo_Size=1.9;
//Logo depth
Logo_Depth=.3;

/* [Type Test] */
//characters per inch for the flat type-test string
Test_CPI=10;

/* [Resin Offsets] */
//tube and pin offset
ID_Offset=.13;
//folder radial offset
Folder_Radial_Gap=.4;
//folder squash/sandwich offset
Folder_Squash_Clearance=.3;

//correction for tube and pin diameters
Tube_OD=Tube_OD_Mm+[ID_Offset, ID_Offset];
Pin_ID=Pin_ID_Mm+ID_Offset;
//left and right folder IDs
Folder_ID=[Folder_ID_Mm+Folder_Radial_Gap, Folder_ID_Mm-Folder_Radial_Gap];

Folder_Glue_Hole_ID=Folder_Glue_Hole_ID_Mm+ID_Offset;

/* [Resin Supports] */
//resin rod diameter
Resin_Rod_OD=.8;
//resin tip diameter
Resin_Tip_OD=.4;
//resin tip length
Resin_Tip_L=1;//.1
//resin rod inset in part
Resin_Inset=.3;
//resin rod minimum height
Resin_Min_Rod_Height=2;
//resin rod base diameter
Resin_Raft_OD=4;
//resin rod raft thickness
Resin_Raft_Thickness=2;

/* [Handy Variables] */
Folder_Half_Thickness=(Folder_Thickness-Folder_Squash_Clearance)/2;
Arc_Start=asin(Finger_Thickness/Arc_OD);
Arc_End=15*Char_Theta+Char_Theta/2;
Arc_Extent=Arc_End-Arc_Start;
Folder_Arc_End=Folder_Degrees+Folder_Degree_Offset;
Folder_Arc=Folder_Arc_End-Folder_Arc_Start;

/* [Resin Support Variables] */
Res_Z_Raise=Folder_ID[1]/2;
//for orienting the shuttle in the x direction
Res_X_Rot=(Arc_Start+Arc_Extent/2);
//folder support limits
Res_Folder_Lims=[-Folder_Arc_Start-Res_X_Rot, -Folder_Arc_Start-Res_X_Rot+Folder_Arc];
Res_Spacing=6;
Res_Angle=45;

function YZ(r, theta) = [sin(theta)*r, cos(theta)*r];

//number of yx pts on Arc
Res_Arc_Div=[15, 4];
//number of yx on folder
Res_Folder_Div=[12, 2];
//number of yx pts on folder face
Res_Folder_Face_Div=[3, 4];
//number of yx pts on ring
Res_Ring_Div=[8, 3];
Res_Ring_Start_End=[-45, 45];

Res_Arc_Y_Pts=[for (theta=[-Arc_Extent/2:Arc_Extent/(Res_Arc_Div[0]-1):Arc_Extent/2]) YZ((Arc_OD/2-Arc_Thickness), theta)[0]];
Res_Arc_Theta_Pts=[for (theta=[-Arc_Extent/2:Arc_Extent/(Res_Arc_Div[0]-1):Arc_Extent/2]) theta];
Res_Arc_Z_Pts=[for (theta=[-Arc_Extent/2:Arc_Extent/(Res_Arc_Div[0]-1):Arc_Extent/2]) YZ((Arc_OD/2-Arc_Thickness), theta)[1]];
Res_Arc_X_Pts=[for (x=[0:Res_Arc_Div[1]-1]) Arc_Height_Offset+Arc_Height/(Res_Arc_Div[1]-1)*x];

Res_Folder_Face_X_Pts=[for (x=[0:(Res_Folder_Face_Div[1]-1)]) x*Folder_Thickness/(Res_Folder_Face_Div[1]-1)];
Res_Folder_Face_R_Pts=[for (r=[0:(Res_Folder_Face_Div[0]-1)]) Folder_ID[0]/2+r*(Folder_OD/2-Folder_ID[0]/2)/(Res_Folder_Face_Div[0]-1)];
Res_Folder_Face_Y_Pts=[for (r=[0:(Res_Folder_Face_Div[0]-1)]) YZ(Res_Folder_Face_R_Pts[r], Folder_Arc_End-Res_X_Rot)[0]];
Res_Folder_Face_Z_Pts=[for (r=[0:(Res_Folder_Face_Div[0]-1)]) YZ(Res_Folder_Face_R_Pts[r], Folder_Arc_End-Res_X_Rot)[1]];

Res_Folder_X_Pts=[for (x=[0:(Folder_Half_Thickness+Folder_Squash_Clearance)/(len(Res_Folder_Div)):Folder_Half_Thickness+Folder_Squash_Clearance]) x];
Res_Folder_Theta_Pts=[for (theta=[Folder_Arc_Start-Res_X_Rot:Folder_Arc/(Res_Folder_Div[0]-1):Folder_Arc_End-Res_X_Rot]) theta];
Res_Folder_Y_Pts=[for (y=[0:Res_Folder_Div[0]-1]) YZ(Folder_ID[0]/2, Res_Folder_Theta_Pts[y])[0]];
Res_Folder_Z_Pts=[for (y=[0:Res_Folder_Div[0]-1]) YZ(Folder_ID[0]/2, Res_Folder_Theta_Pts[y])[1]];

Res_Ring_X_Pts=[for (x=[0:Folder_Half_Thickness/(Res_Ring_Div[1]-1):Folder_Half_Thickness]) x];
Res_Ring_Theta_Pts=[for (theta=[Res_Ring_Start_End[0]:(Res_Ring_Start_End[1]-Res_Ring_Start_End[0])/(Res_Ring_Div[0]-1):Res_Ring_Start_End[1]]) theta];
Res_Ring_Y_Pts=[for (y=[0:len(Res_Ring_Theta_Pts)-1]) YZ(Folder_ID[1]/2, Res_Ring_Theta_Pts[y])[0]];
Res_Ring_Z_Pts=[for (y=[0:len(Res_Ring_Theta_Pts)-1]) -YZ(Folder_ID[1]/2, Res_Ring_Theta_Pts[y])[1]];

module Arc(extra){
    rotate_extrude(15*Char_Theta+Char_Theta/2)
    translate([Arc_OD/2-Arc_Thickness, Arc_Height_Offset])
    square([Arc_Thickness+extra, Arc_Height]);
}

module Center(){
    cylinder(d=Folder_OD, h=Folder_Thickness);
}

module Spoke2D(){
    scale([Spoke_Thickness, Spoke_Height])
    circle(d=1);
}

module SpokeChamfer(){
    hull(){
        translate([0, 0, Spoke_Chamfer])
        linear_extrude(z)
        scale([(Spoke_Thickness+2*Spoke_Chamfer)/Spoke_Thickness, (Spoke_Height+2*Spoke_Chamfer)/Spoke_Height])
        Spoke2D();
        linear_extrude(z)
        Spoke2D();
    }
}

module Spoke(){
    translate([0, 0, Folder_Thickness/2])
    rotate([90, 0, 90]){
        linear_extrude(Arc_OD/2-Arc_Thickness+z)
        Spoke2D();
        translate([0, 0, Arc_OD/2-Arc_Thickness-Spoke_Chamfer])
        SpokeChamfer();
    }
}

module SpokeArranged(){
    rotate([0, 0, Folder_Degree_Offset])
    for (i=[0:Spoke_Count-1])
        rotate([0, 0, i*Spoke_Spacing])
        Spoke();
}

module Rib(){
    a=5;//outer angular padding for rib
    b=4;//inner thickness for rib
    hull(){
        rotate([0, 0, Folder_Degree_Offset-a/2])
        rotate_extrude(Spoke_Extent+a)
        translate([Rib_OD/2-Rib_Radius, Folder_Thickness/2])
        circle(r=Rib_Radius);

        rotate([0, 0, Folder_Degree_Offset])
        rotate_extrude(120)
        translate([Folder_OD/2-b/2-z, Folder_Thickness/2])
        circle(d=b);
    }

    hull(){
        rotate([0, 0, Folder_Degree_Offset])
        rotate_extrude(Spoke_Extent)
        translate([Folder_OD/2-z, 0, 0])
        polygon([[0,Folder_Thickness/2-Spoke_Height/2], [0,Folder_Thickness/2+Spoke_Height/2], [Folder_Thickness/2, Folder_Thickness/2]]);

        translate([0, 0, Folder_Thickness/2])
        rotate([-90, 0, 0])
        cylinder(d=3, h=10.5);
    }
}

module Text(char, font, size){
    mirror([1, 0, 0])
    text(char, font=font, size=size, halign="center", valign="baseline");
}

module TextPlacement(angle, height){
    rotate([0, 0, angle])
    translate([Arc_OD/2-1, 0, height])
    rotate([90, 0, 90])
    children();
}

module LetterText(char, font, size){
    difference(){
        minkowski(){
            linear_extrude(Glyph_Height+1)
            Text(char, font, size);

            if (Mink_On==true){
                translate([0, 0, -Mink_Height])
                cylinder(r1=Mink_Radius, r2=0, h=Mink_Height, $fn=Mink_Fn);
            }
        }

        translate([0, 0, -10])
        cube(20, center=true);
    }
}

module TextAssemble(side){
    for (baseline=[0, 1, 2])
    for (int=[0:14]){
        height=Baselines[baseline];
        angle=side==0?
            ((1+int)*Char_Theta): /*left side*/
            ((-1-(14-int))*Char_Theta); //right side
        char=side==0?
            Layout[baseline][14-int]: /*left side*/
            Layout[baseline][29-int];
        ismod=search(char, Char_Mod)==[]?false:true;
        font=ismod?Char_Mod_Font:Type_Face;
        size=ismod?Char_Mod_Size:Type_Size;

        TextPlacement(angle, height)
        LetterText(char, font, size);
    }
}

module TextRing(side){
    intersection(){
        TextAssemble(side);
        Mirror(side)
        Arc(Glyph_Height+1);
    }
}

module Tube(side){
    chamferbump=side==0?-z:(Folder_Half_Thickness+Folder_Squash_Clearance);
    translate([0, 0, -z])
    cylinder(d=Tube_OD[side], h=25);
    translate([0, 0, chamferbump]){
        translate([0, 0, -z])
        cylinder(d1=Tube_OD[side]+2*Tube_Chamfer, d2=Tube_OD[side], h=Tube_Chamfer+z);
        translate([0, 0, Folder_Half_Thickness-Tube_Chamfer])
        cylinder(d2=Tube_OD[side]+2*Tube_Chamfer, d1=Tube_OD[side], h=Tube_Chamfer+z);
    }
}

module FolderClearance(side){
    //height offset of cylinder
    hoffset=side==0?(Folder_Thickness/2-Folder_Squash_Clearance/2):-z;
    //start height of cylinder
    hstart=side==0?hoffset:-z;
    //height of cylinder
    h=side==0?15:(z+Folder_Thickness/2+Folder_Squash_Clearance/2);
    translate([0, 0, hstart])
    cylinder(d=Folder_ID[0], h=h);
}

module FolderCutaway(side){
    r=30;
    angles=[Folder_Arc_Start, Folder_Arc_End];
    xy=[[cos(angles[0])*r, sin(angles[0])*r], [cos(angles[1])*r, sin(angles[1])*r]];

    difference(){
        Mirror(side)
        translate([0, 0, -5])
        linear_extrude(25)
        polygon([xy[0], [0,0], xy[1], [-r, r], [-r, -r], [r, -r]]);

        translate([0, 0, -20])
        cylinder(d=Folder_ID[1], h=40);
    }
}

module Finger(){
    translate([Arc_OD/2-5, -Finger_Thickness/2, -10])
    cube([10, Finger_Thickness, 40]);
}

module PinHole(){
    translate([0, 0, -z]){
        cylinder(h=20, d=Pin_ID);
        cylinder(d1=Pin_ID+2*Pin_ID_Chamfer, d2=Pin_ID, h=Pin_ID_Chamfer);
    }
    translate([0, 0, Folder_Thickness-Pin_ID_Chamfer])
    cylinder(d1=Pin_ID, d2=Pin_ID+2*Pin_ID_Chamfer, h=Pin_ID_Chamfer+z);
}

module PinHoles(side){
    Mirror(side)
    for (pin=[0,1]){
        rotate([0, 0, Pin_Theta[pin]])
        translate([Pin_Radial, 0, 0])
        PinHole();
    }
}

module GlueHoles(side){
    height=side==0?Folder_Half_Thickness/2:Folder_Thickness-Folder_Half_Thickness/2;
    Folder_Glue_Hole_ID=.8;
    translate([0, 0, height])
    Mirror(side)
    for (n=[0, 180])
    rotate([0, 90, Folder_Arc_Start-(360-Folder_Arc)/2+90+n]){
        cylinder(h=Folder_ID[1]/2, d=Folder_Glue_Hole_ID);
        translate([0, 0, Folder_ID[1]/2-1])
        cylinder(d1=Folder_Glue_Hole_ID, d2=Folder_Glue_Hole_ID+2*Pin_ID_Chamfer, h=1);
    }
}

module GlueGroove(side){
    height=side==0?Folder_Half_Thickness/2:Folder_Thickness-Folder_Half_Thickness/2;
    translate([0, 0, height])
    rotate_extrude()
    translate([Tube_OD[side]/2-Folder_Glue_Groove_R+Folder_Glue_Groove_Depth, 0, 0])
    circle(r=Folder_Glue_Groove_R);
}

module Logo(side){
    if (Logo==true)
    rotate([0, 0, (side==0?1:-1)*Folder_Arc_Start])
    translate([16, 0, Folder_Thickness/2])
    rotate([90, 0, side==0?0:180])
    linear_extrude(Logo_Depth*2, center=true){
    translate([0, 0, 0])
    text(text=Logo_Text_1, size=Logo_Size, font=Logo_Font, halign="center", valign="center");
    translate([0, -2, 0])
    text(text=Logo_Text_2, size=Logo_Size, font=Logo_Font, halign="center", valign="center");
    }
}

module Mirror(side){
    if (side==1)
        mirror([0, 1, 0])
        children();
    else
        children();
}

module LeftAdditive(){
    $fn=Cyl_Fn;
    union(){
        Arc(0);
        Center();
        SpokeArranged();
        Rib();
    }
}

module Additive(side){
    union(){
        Mirror(side)
        LeftAdditive();
        TextRing(side);
    }
}

module Subtractive(side){
    $fn=120;
    union(){
        Tube(side);
        FolderClearance(side);
        FolderCutaway(side);
        Finger();
        PinHoles(side);
        GlueHoles(side);
        GlueGroove(side);
        Logo(side);
    }
}

module AssembleSide(side){
    difference(){
        Additive(side);
        Subtractive(side);
    }
}

module ResPrintOrient(side){
    pole=side==0?-1:1;
    translate([0, 0, Res_Z_Raise])
    rotate([0, -90, 0])
    rotate([0, 0, pole*Res_X_Rot])
    children();
}

module Assemble(){
    if (Render_Left)
    AssembleSide(0);
    if (Render_Right)
    AssembleSide(1);
}

function ResYOffset(theta)= -sin(theta)*(Resin_Tip_L+Resin_Tip_OD/2-Resin_Inset);
function ResZOffset(theta) = -cos(theta)*(Resin_Tip_L+Resin_Tip_OD/2-Resin_Inset);

module ResinTip(theta){
    hull(){
        rotate([-theta, 0, 0])
        translate([0, 0, -Resin_Tip_OD/2+Resin_Inset]){
            sphere(d=Resin_Tip_OD);
            translate([0, 0, -Resin_Tip_L])
            sphere(d=Resin_Rod_OD);
        }
    }
}

module ResinRod(h, theta){
    $fn=Resin_Fn;

    translate([0, 0, h])
    ResinTip(theta);

    ResinRodClean(h, theta);

    translate([0, ResYOffset(theta), -Resin_Min_Rod_Height-Resin_Raft_Thickness])
    cylinder(d1=Resin_Raft_OD, d2=Resin_Raft_OD+2*Resin_Raft_Thickness, h=Resin_Raft_Thickness);

}

module ResinRodClean(h, theta){
    $fn=Resin_Fn;

    hull(){
        translate([0, 0, -Resin_Min_Rod_Height-ResZOffset(theta)])
        rotate([-theta, 0, 0])
        translate([0, 0, -Resin_Tip_OD/2+Resin_Inset])
        translate([0, 0, -Resin_Tip_L])
        sphere(d=Resin_Rod_OD);

        translate([0, 0, h])
        rotate([-theta, 0, 0])
        translate([0, 0, -Resin_Tip_OD/2+Resin_Inset])
        translate([0, 0, -Resin_Tip_L])
        sphere(d=Resin_Rod_OD);
        }
}

module ResinFenceTopSphere(h, theta){
    $fn=Resin_Fn;
    translate([0, 0, h])
    rotate([-theta, 0, 0])
    translate([0, 0, -Resin_Tip_OD/2+Resin_Inset])
    translate([0, 0, -Resin_Tip_L])
    sphere(d=Resin_Rod_OD);
}

Res_Fence_Top_Offset=0;

module ResinFenceArcTop(){
    for (yint=[1:len(Res_Arc_Y_Pts)-1]){
            hull(){
            translate([0, Res_Arc_Y_Pts[yint], 0])
            ResinFenceTopSphere(Res_Arc_Z_Pts[yint]+Res_Z_Raise-Res_Fence_Top_Offset, Res_Arc_Theta_Pts[yint]);
            translate([0, Res_Arc_Y_Pts[yint-1], 0])
            ResinFenceTopSphere(Res_Arc_Z_Pts[yint-1]+Res_Z_Raise-Res_Fence_Top_Offset, Res_Arc_Theta_Pts[yint-1]);
            }
        }
}

module ResinFenceArcSide(yint){
    hull(){
        for (xint=[0,len(Res_Arc_X_Pts)-1])
        translate([-Res_Arc_X_Pts[xint], 0, 0])
        ResinFenceTopSphere(Res_Arc_Z_Pts[0]+Res_Z_Raise-Res_Fence_Top_Offset, Res_Arc_Theta_Pts[yint]);
        }
}

module ResinArcSupports(){
    for (xint=[0:len(Res_Arc_X_Pts)-1])
    for (yint=[0:len(Res_Arc_Y_Pts)-1])
    if (xint==0 || xint==len(Res_Arc_X_Pts)-1 || yint==0 || yint==len(Res_Arc_Y_Pts)-1)
    translate([-Res_Arc_X_Pts[xint], Res_Arc_Y_Pts[yint], 0])
    ResinRod(Res_Arc_Z_Pts[yint]+Res_Z_Raise, Res_Arc_Theta_Pts[yint]);
}

module ResinArcFenceSupport(){
    for (xint=[0,len(Res_Arc_X_Pts)-1])
    translate([-Res_Arc_X_Pts[xint], 0, 0]){
        intersection(){
            ResinKeepY();
            ResinFence();
        }

        ResinFenceArcTop();
    }

    for (yint=[0,len(Res_Arc_Y_Pts)-1])
    translate([0, Res_Arc_Y_Pts[yint], 0]){
        intersection(){
            ResinKeepX(yint);
            translate([0, ResYOffset(Res_Arc_Theta_Pts[yint]), 0])
            rotate([0, 0, 90])
            ResinFence();
        }
        ResinFenceArcSide(yint);
    }
}

module ResinKeepY(){
    hull(){
        for (yint=[0:len(Res_Arc_Y_Pts)-1])
        translate([0, Res_Arc_Y_Pts[yint], 0])
        ResinRodClean(Res_Arc_Z_Pts[yint]+Res_Z_Raise-Res_Fence_Top_Offset, Res_Arc_Theta_Pts[yint]);
    }
}

module ResinKeepX(yint){
    hull(){
        for (xint=[0,len(Res_Arc_X_Pts)-1])
        translate([-Res_Arc_X_Pts[xint], 0, 0])
        ResinRodClean(Res_Arc_Z_Pts[0]+Res_Z_Raise-Res_Fence_Top_Offset, Res_Arc_Theta_Pts[yint]);
    }
}

module ResinParallelBars(){
    $fn=Resin_Fn;
    for (n=[-20:20])
    translate([0, n*Res_Spacing, 0])
    cylinder(d=Resin_Rod_OD, h=100, center=true);
}

module ResinFence(){
    rotate([-Res_Angle, 0, 0])
    ResinParallelBars();
    rotate([Res_Angle, 0, 0])
    ResinParallelBars();
}

module ResinFolderSupports(side){
    Mirror(side)
    for (xint=[0:len(Res_Folder_Face_X_Pts)-1])
    for (yint=[0:len(Res_Folder_Face_Y_Pts)-1]){
        if (side == 0 && (yint!=0 || (xint+1)/len(Res_Folder_Face_X_Pts)>.5))
            translate([-Res_Folder_Face_X_Pts[xint], Res_Folder_Face_Y_Pts[yint], 0])
            ResinRod(Res_Folder_Face_Z_Pts[yint]+Res_Z_Raise, Folder_Arc_End-Res_X_Rot-90);

        if (side == 1 && (yint!=0 || (xint+1)/len(Res_Folder_Face_X_Pts)<=.5))
            translate([-Res_Folder_Face_X_Pts[xint], Res_Folder_Face_Y_Pts[yint], 0])
            ResinRod(Res_Folder_Face_Z_Pts[yint]+Res_Z_Raise, Folder_Arc_End-Res_X_Rot-90);
    }

    for (xint=[0:len(Res_Folder_X_Pts)-1])
    for (yint=[0:len(Res_Folder_Y_Pts)-1]){
        if (side==0 && xint!=0 && yint!=len(Res_Folder_Y_Pts)-1)
            translate([-Res_Folder_X_Pts[xint]-Folder_Half_Thickness, Res_Folder_Y_Pts[yint], 0])
            ResinRod(Res_Folder_Z_Pts[yint]+Res_Z_Raise, yint==0?0:Res_Folder_Theta_Pts[yint]);

        if (side==1 && xint!=len(Res_Folder_X_Pts)-1 && yint!=len(Res_Folder_Y_Pts)-1)
            Mirror(side)
            translate([-Res_Folder_X_Pts[xint], Res_Folder_Y_Pts[yint], 0])
            ResinRod(Res_Folder_Z_Pts[yint]+Res_Z_Raise, yint==0?0:Res_Folder_Theta_Pts[yint]);
    }
}

module ResinRingSupports(side){
    for (xint=[0:len(Res_Ring_X_Pts)-1])
    for (yint=[0:len(Res_Ring_Y_Pts)-1]){
        if (side==0)
            translate([-Res_Ring_X_Pts[xint], -Res_Ring_Y_Pts[yint], 0])
            ResinRod(Res_Ring_Z_Pts[yint]+Res_Z_Raise, Res_Ring_Theta_Pts[yint]);
        if (side==1)
            translate([-Res_Ring_X_Pts[xint]-(Folder_Half_Thickness+Folder_Squash_Clearance), -Res_Ring_Y_Pts[yint], 0])
            ResinRod(Res_Ring_Z_Pts[yint]+Res_Z_Raise, Res_Ring_Theta_Pts[yint]);
    }
}

module ResinSupports(side){
    ResinArcSupports();
    ResinFolderSupports(side);
    ResinRingSupports(side);
    ResinArcFenceSupport();
}

module ResinPrintHalf(side){
    ResPrintOrient(side)
    AssembleSide(side);
    ResinSupports(side);
}

module AssembleResin(){
    translate([0, 7, 0])
    rotate([0, 0, -90])
    ResinPrintHalf(0);
    translate([0, -7, 0])
    rotate([0, 0, 90])
    ResinPrintHalf(1);
}

//flat readable layout of the whole character set, for checking kerning/
//legibility at print size before generating full element geometry - same
//role as Blickensderfer/Postal's TypeTest. Layout here is a single flat
//30-char-per-row array (unlike TextAssemble's split left/right halves), so
//no side parameter is needed.
module TypeTest(){
    Test_Chars=[for (row=[0:len(Layout)-1]) for (col=[0:len(Layout[row])-1]) Layout[row][col]];
    for (n=[0:len(Test_Chars)-1]){
        char=Test_Chars[n];
        ismod=search(char, Char_Mod)!=[];
        font=ismod?Char_Mod_Font:Type_Face;
        size=ismod?Char_Mod_Size:Type_Size;
        translate([1/Test_CPI*25.4*n, 0, 0])
        text(text=char, size=size, font=font, halign="center", valign="baseline", $fn=Text_Fn);
    }
}

if (Render==true){
    if (Render_Mode==0)
        Assemble();
    if (Render_Mode==1)
        AssembleResin();
    if (Render_Mode==2)
        TypeTest();
}
