//Shared Glyph Pipeline (v2.0 lib)
//Used by blickensderfer.scad, postal.scad, bennett.scad, mignon.scad.
//Every v2 machine file declares the FULL parameter set
//below directly (visible in its own Customizer panel) rather than relying on
//silent lib defaults - the is_undef() fallbacks here are a safety net, not
//the primary mechanism, now that "same feature set everywhere" is the goal.
//
//Include this AFTER the machine file has defined its own globals, so machine
//values win under OpenSCAD's "last assignment in file order" variable rule.
//This file defines modules/functions only - no colliding variable assignments.
//
//Dimensions/quality (every machine declares these under these exact names now
//- Element_Diameter/Platen_Diameter/Char_Protrusion/Baseline/Cutout are the
//canonical names adopted from Bennett/Mignon's original convention; Blick2/
//Postal's cylOD/platenOD/textProtrusion/charBaselines/platenBaselines were
//renamed to match):
//  z, Mink_Fn, Text_Fn, Cyl_Fn, Surface_Fn        - quality vars
//  Mink_On, Mink_Draft_Angle                     - draft angle control
//  Element_Diameter, Platen_Diameter, Char_Protrusion, Latitude_Int - dimensions
//  Font, Font_Size                             - base typeface
//  Physical_Layout                             - 2D array [row][col] of chars,
//                                                already resolved to the exact
//                                                physical column order and with
//                                                any machine-specific character
//                                                substitution already applied
//  Baseline, Cutout                           - per-row baseline arrays
//  Baseline_Z_Offset                            - Z added to every character's
//                                                placement/cutout height.
//                                                Blick2/Postal set this to
//                                                their Element_Height (their
//                                                Baseline/Cutout arrays are
//                                                negative-from-clip-end, so
//                                                this shifts them to absolute);
//                                                Bennett/Mignon set 0 (their
//                                                arrays are already absolute
//                                                heights from the bottom face).
//                                                This is a distinct concept
//                                                from the physical Element_Height
//                                                dimension, not the same thing
//                                                even though Blick2/Postal's
//                                                value happens to equal it.
//  Cutout_Test, Cutout_Test_Array, Baseline_Test, Baseline_Test_Array, Test_Layout, Test_Char
//
//Unified glyph-quality features (every v2 machine declares all of these):
//  Font_Weight_Offset, X_Font_Weight_Adj, Y_Font_Weight_Adj
//                       - offset()-based stroke weight (Blickensderfer2/
//                         Postal's original system). 0 = no-op.
//  Weight_Adj_Mode, Weight_Adj_Shape, Horizontal_Weight_Adj, Vertical_Weight_Adj
//                       - minkowski erosion/growth stroke-weight system
//                         (0=none/1=subtractive/2=additive), independent of
//                         and layered with Font_Weight_Offset above. Mode 0 is
//                         a no-op, reducing to exactly the offset+square
//                         system. Verified equivalent restructuring for
//                         Blick2/Postal: mirror() now wraps the whole mode
//                         branch instead of just the text() call, provably
//                         identical since minkowski(mirror(text),square) ==
//                         mirror(minkowski(text,square)) when square is
//                         centered (mirror-invariant).
//  Character_Modifieds, Character_Modifieds_Offset,
//  Character_Modifieds_Font, Character_Modifieds_Size
//                       - per-character override: characters in
//                         Character_Modifieds get their baseline shifted by
//                         Character_Modifieds_Offset AND their font/size
//                         swapped to Character_Modifieds_Font/_Size. Set
//                         Character_Modifieds_Font/_Size equal to a machine's
//                         own font/Font_Size for a no-op font swap (baseline
//                         offset still applies) - this is how Bennett/Mignon,
//                         whose original systems only ever shifted baseline,
//                         stay behaviorally identical while gaining the
//                         (unused-by-default) font-swap capability.
//  Scale_Multiplier_Text, Scale_Multiplier
//                       - per-character size override (e.g. make "." larger).
//                         Scale_Multiplier_Text="" = no-op.
//  Y_Scale               - vertical scale applied to the glyph before
//                         extrusion. 1 = no-op.
//  Typeface_2, Type_2_Size, Typeface_2_Chars
//                       - secondary-typeface-by-character system, independent
//                         of and resolved before Scale_Multiplier_Text sizing.
//                         Typeface_2_Chars="" = no-op.
//
//Optional (lib supplies a default if a machine file leaves these undefined -
//these are structural/composition knobs, not customizer-facing features, so
//they stay opt-in rather than part of the unified declared set above):
//  Placement_Map        - per-column index -> physical placement latitude.
//                         Default: identity (column N places at latitude N).
//  Row_Labels            - per-row name array used only by TextRingDebug's
//                         console echo (Cutout_Test/Baseline_Test/Test_Layout).
//                         Default: numeric "row 0"/"row 1"/etc. Blick2/Postal/
//                         Bennett/Hammond override this to their real
//                         ["lowercase","uppercase","figs"(,"math")] shift
//                         names.
//  Reference_Physical_Layout - a second Physical_Layout-shaped array, used only
//                         by TextRingDebug's console echo to identify which
//                         physical keyboard key/lever strikes a given
//                         position - independent of Test_Layout (which still
//                         collapses the actual RENDERED glyph to Test_Char)
//                         and independent of whatever content Layout is
//                         currently selected for printing. Default: same as
//                         Physical_Layout. Blickensderfer/Bennett/Mignon wire
//                         this from a dedicated Reference_Layout_Selection
//                         dropdown (reusing each machine's own layout preset
//                         list + its fixed keyboard->physical hardware remap)
//                         so switching what you're printing never changes
//                         what the echo calls a given physical position - the
//                         real keyboard's key labels are a hardware fact of
//                         the machine, not a function of what you're
//                         currently engraving.
//  Row_Font, Row_Font_Size - per-row font/size array. Default: global font/Font_Size
//                         repeated for every row.
//  Row_Font_Lock          - per-row boolean array. When true for a row, that row's
//                         Row_Font/Row_Font_Size always wins over a
//                         Character_Modifieds match (this is how
//                         Blickensderfer2's Hebrew row0 stays on fontHebrew
//                         regardless of Character_Modifieds). Default: all false.
//  Text_2D_Fn             - local $fn override inside TwoDText(). Default: inherit
//                         ambient $fn from the caller (matches Blickensderfer2).
//  Mink_H_Fixed            - override the shared draft-cone h=2. Default 2.
//  Letter_Placement_Protrusion - radial offset added at the placement stage
//                       (Element_Diameter/2 + this). Default: same as
//                       Char_Protrusion (Blickensderfer2/Postal's original
//                       behavior - their raw material stands proud of the
//                       plain element surface before any cutout trims it).
//                       Bennett/Mignon/Helios set this to 0: their placement
//                       radius is the raw Element_Diameter/2, with embed
//                       depth controlled instead by Letter_Extrude_Offset below
//                       - Char_Protrusion still applies in PlatenCutout's
//                       formula regardless of this override (verified
//                       algebraically: Bennett's Platen_Diameter/2+
//                       Min_Final_Character_Diameter/2 cutout radius is
//                       exactly Element_Diameter/2+Platen_Diameter/2+
//                       Char_Protrusion once Char_Protrusion is expanded, so
//                       the cutout side was never wrong - only the placement
//                       side needed this override).
//  Letter_Extrude_Offset, Letter_Extrude_Depth
//                       - Z offset/depth of the raw pre-cutout linear_extrude,
//                         in the LetterPlacement-local frame (local Z = radial
//                         direction once placed). Default 0/6 (Blickensderfer2/
//                         Postal). Bennett uses -.5/2 - since this raw block
//                         is always trimmed down by the (verified) PlatenCutout
//                         afterward, it only needs to be deep enough to contain
//                         the final shape, so this needed no separate
//                         verification beyond the cutout itself.
//  Angle_Half_Step         - constant added to `latitude` before multiplying by
//                         Latitude_Int, i.e. angle = (Angle_Half_Step+latitude)*
//                         Latitude_Int. Default .5 (Blickensderfer2/Postal/
//                         Bennett all center each column between latitude band
//                         edges this way). Mignon has no such half-column
//                         offset, so it sets this to 0.
//  Text_Align_Method, Text_Align_X_Offset
//                       - horizontal glyph alignment, see AlignedText() below
//                         and docs/text-centering.md for the full derivation.
//                         Default 0/0 = today's halign="center" (native
//                         OpenSCAD advance-box centering - see AlignedText's
//                         comment for the empirical correction, this is NOT
//                         ink-bbox centering despite earlier docs saying so)
//                         with no offset, i.e. a no-op for every machine file
//                         until explicitly opted into. Methods 1/2 read
//                         Test_CPI (already declared by every v2 machine for
//                         its own type-test string) and/or textmetrics() -
//                         no separate pitch parameter.

function minkTextR(draft_angle) = 2*tan(.5*draft_angle);

//Resolves Text_Align_Method (see text-centering.md for the full derivation
//AND its correction note - the original design assumed OpenSCAD's native
//halign="center" centers on ink bounds; empirically verified via textmetrics()
//probes that it actually centers on the ADVANCE box: measured offset.x at
//halign="center" equals -advance.x/2 exactly, for every glyph/font tested,
//including glyphs with clearly asymmetric left/right bearing. This changed
//what methods 1/2 needed to do to be genuinely different from method 0):
//  0 (default) = "halign_center" - native OpenSCAD centering. Centers the
//                ADVANCE box (verified, not ink). translate([Text_Align_X_Offset, 0]).
//  1 = "ink_center" - TRUE ink-bbox centering (position.x+size.x/2), a
//                capability OpenSCAD has no native halign for. Makes the
//                visible ink dead-center, ERASING whatever native left/right
//                bearing asymmetry the font was drawn with (opposite of
//                method 0, which preserves it inside a centered advance box).
//  2 = "textmetrics_left" - pins the glyph's own INK left edge (position.x),
//                not the pen origin, to a fixed external slot pitch
//                P=25.4/Test_CPI (i.e. -P/2), so translate =
//                -(25.4/Test_CPI)/2 - position.x. Guarantees the ink sits at
//                a fixed, non-center position for any narrow glyph, even
//                when the font's own advance.x happens to equal P (in which
//                case pinning the pen origin instead - the original design -
//                would coincide exactly with method 0, since sliding a
//                same-width box to align its left edge vs its center at
//                matching anchors produces the same final box position;
//                pinning the ink edge instead avoids that coincidence).
//Text_Align_X_Offset is a universal fine-tune nudge (mm) layered on top of
//whichever method is selected - same "_Offset defaults to 0 = no-op" pattern
//as Baseline_Z_Offset/Font_Weight_Offset elsewhere in this file.
//Both are new (no v2 machine file declares them yet) so they default via
//is_undef, matching this file's "Optional" fallback convention, until/unless
//promoted to the unified declared set with real Customizer sliders per machine.
//WARNING: methods 1 AND 2 require OpenSCAD's "Text Metrics" experimental
//feature enabled (Edit>Preferences>Features, or --enable=textmetrics on the
//CLI) - method 2 now reads position.x too, not just Test_CPI. Verified:
//without the flag, this does NOT error - it prints easy-to-miss console
//warnings and silently renders as if untranslated (glyph ends up unshifted
//halign="left", not centered/aligned). Confirm the flag is on before trusting
//method 1/2 output for anything physical.
//
//Text_Align_Modified_Chars/Text_Align_Method_Modified/Text_Align_X_Offset_Modified
//mirror Character_Modifieds/Character_Modifieds_Font/Character_Modifieds_Offset's
//per-character-override pattern, but for horizontal alignment instead of
//baseline/font: characters in Text_Align_Modified_Chars get
//Text_Align_Method_Modified/Text_Align_X_Offset_Modified instead of the
//top-level Text_Align_Method/Text_Align_X_Offset, so the main alphabet can
//stay on native advance-box centering while narrow punctuation (e.g. ".,:;")
//gets its own method+offset. Text_Align_Modified_Chars="" (default) = no-op,
//same empty-string convention as Typeface_2_Chars/Scale_Multiplier_Text.
module AlignedText(char, font, size){
    _modChars = is_undef(Text_Align_Modified_Chars) ? "" : Text_Align_Modified_Chars;
    _isModified = search(char, _modChars)!=[];
    _method = _isModified
        ? (is_undef(Text_Align_Method_Modified) ? 0 : Text_Align_Method_Modified)
        : (is_undef(Text_Align_Method) ? 0 : Text_Align_Method);
    _xOffset = _isModified
        ? (is_undef(Text_Align_X_Offset_Modified) ? 0 : Text_Align_X_Offset_Modified)
        : (is_undef(Text_Align_X_Offset) ? 0 : Text_Align_X_Offset);
    if (_method==1){
        _m = textmetrics(text=char, size=size, font=font);
        translate([-(_m.position.x+_m.size.x/2)+_xOffset, 0])
        text(text=char, size=size, font=font, valign="baseline", halign="left", $fn=Text_Fn);
    } else if (_method==2){
        _posX = textmetrics(text=char, size=size, font=font).position.x;
        translate([-(25.4/Test_CPI)/2-_posX+_xOffset, 0])
        text(text=char, size=size, font=font, valign="baseline", halign="left", $fn=Text_Fn);
    } else
        translate([_xOffset, 0])
        text(text=char, size=size, font=font, valign="baseline", halign="center", $fn=Text_Fn);
}

//Thin semi-transparent frame showing the width-`pitch` "character window"
//AlignedText's methods reason about (P=25.4/Test_CPI, centered on local x=0 -
//the same local frame TypeTest() places each character's AlignedText() call
//into), so the actual ink can be visually compared against it in preview
//(F5) - a filled/solid frame would obscure the glyph, hence outline-only
//with alpha. Not used by the physical element geometry, TypeTest()-only.
module AlignBoundsBox(pitch, height, thickness=0.05, alpha=0.35){
    color("red", alpha)
    difference(){
        square([pitch, height], center=true);
        square([max(pitch-2*thickness, 0), max(height-2*thickness, 0)], center=true);
    }
}

//2D glyph shape, mirrored so it reads correctly once placed facing outward.
//NOTE: preserves a pre-existing typo from Blick2/Postal - the y term of the
//weight-adjust square references "yFontWieghtAdj" (misspelled), which is
//always undef, so this branch only actually resolves when X_Font_Weight_Adj>0
//with Y_Font_Weight_Adj left at 0. Kept as-is for exact behavioral parity.
module TwoDText(char, font, size){
    $fn = is_undef(Text_2D_Fn) ? $fn : Text_2D_Fn;
    _weightAdjMode = Weight_Adj_Mode;
    //Typeface_2_Chars resolves BEFORE Scale_Multiplier_Text sizing, matching
    //Mignon's original precedence exactly.
    _isTypeface2 = search(char, Typeface_2_Chars)!=[];
    _font = _isTypeface2 ? Typeface_2 : font;
    _baseSize = _isTypeface2 ? Type_2_Size : size;
    _useSize = search(char, Scale_Multiplier_Text)==[] ? _baseSize : _baseSize*Scale_Multiplier;

    offset(Font_Weight_Offset)
    mirror([1, 0, 0]){
        if (_weightAdjMode==2)//Additive
            minkowski(){
                AlignedText(char, _font, _useSize);
                WeightAdjShape();
            }
        else if (_weightAdjMode==1)//Subtractive
            difference(){
                AlignedText(char, _font, _useSize);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        AlignedText(char, _font, _useSize);
                    }
                    WeightAdjShape();
                }
            }
        else //None - Blick2/Postal's original offset+square weight system
            minkowski(){
                AlignedText(char, _font, _useSize);
                if (X_Font_Weight_Adj>0 || Y_Font_Weight_Adj>0)
                square([z+X_Font_Weight_Adj, z+yFontWieghtAdj], center=true);
            }
    }
}

//Bennett's 2D weight-adjuster profile/shape, used by TwoDText's mode 1/2
module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=Mink_Fn);
}

//concave underside cutout so the character conforms to the platen curvature
module PlatenCutout(platenBaseline, latitude){
    _angleHalfStep = is_undef(Angle_Half_Step) ? .5 : Angle_Half_Step;
    rotate([0, 0, (_angleHalfStep+latitude)*Latitude_Int])
    translate([Element_Diameter/2+Platen_Diameter/2+Char_Protrusion, 0, platenBaseline])
    rotate([90, 0, 0])
    cylinder(d=Platen_Diameter, h=10, center=true, $fn=Cyl_Fn);
}

//places a glyph at its circumferential/axial position on the element
module LetterPlacement(textBaseline, latitude){
    _angleHalfStep = is_undef(Angle_Half_Step) ? .5 : Angle_Half_Step;
    //Letter_Placement_Protrusion: Blick2/Postal add the full Char_Protrusion to
    //BOTH the placement radius and the platen-cutout radius (their raw
    //material genuinely stands proud of the plain element surface before any
    //cutout trims it). Bennett/Mignon/Helios only need Char_Protrusion in the
    //cutout formula (verified algebraically for Bennett - see PlatenCutout);
    //their placement radius is the raw Element_Diameter/2, with embed depth
    //controlled instead by Letter_Extrude_Offset. Default keeps Blick2/Postal's
    //original behavior; Bennett/Mignon/Helios override this to 0.
    _placementProtrusion = is_undef(Letter_Placement_Protrusion) ? Char_Protrusion : Letter_Placement_Protrusion;
    rotate([0, 0, (_angleHalfStep+latitude)*Latitude_Int])
    translate([0, 0, textBaseline])
    translate([Element_Diameter/2+_placementProtrusion-z, 0, 0])
    rotate([90, 0, 90])
    children();
}

//full drafted single-character solid: extrude, platen cutout, minkowski taper
module LetterText(char, font, size, platenBaseline, textBaseline, latitude){
    $fn=Surface_Fn;
    _extrudeOffset = is_undef(Letter_Extrude_Offset) ? 0 : Letter_Extrude_Offset;
    _extrudeDepth = is_undef(Letter_Extrude_Depth) ? 6 : Letter_Extrude_Depth;
    _yScale = Y_Scale;
    //the draft cone is an arbitrary taper shape, not a calibrated dimension -
    //r2 comes from the draft angle (the physically meaningful parameter),
    //r1=0 (apex). h=2 is Blickensderfer2/Postal's already-proven "big enough,
    //not unreasonably large" value; every machine shares it unless it
    //explicitly needs something else via Mink_H_Fixed.
    _minkH = is_undef(Mink_H_Fixed) ? 2 : Mink_H_Fixed;
    _angleHalfStep = is_undef(Angle_Half_Step) ? .5 : Angle_Half_Step;
    //Skip_Platen_Cutout: Hammond strikes a flat anvil, not a curved platen, so
    //there's no concave cutout to carve - difference() with only the extruded
    //text child (no PlatenCutout operand) is just that child unchanged.
    _skipPlatenCutout = is_undef(Skip_Platen_Cutout) ? false : Skip_Platen_Cutout;
    minkowski(){
        difference(){
            LetterPlacement(textBaseline, latitude)
            translate([0, 0, _extrudeOffset])
            linear_extrude(_extrudeDepth)
            scale([1, _yScale, 1])
            TwoDText(char, font, size);
            if (!_skipPlatenCutout)
            PlatenCutout(platenBaseline, latitude);
        }
        if (Mink_On==true){
            rotate([0, -90, (_angleHalfStep+latitude)*Latitude_Int])
            cylinder(r1=0, r2=minkTextR(Mink_Draft_Angle), h=_minkH, $fn=Mink_Fn);
        }
    }
}

//Row_Labels: optional per-machine row-name array (default: numeric "row N").
//Found via testing with actual OpenSCAD (openscad-nightly) - the previous
//hardcoded 3-entry ["lowercase","uppercase","figs"] array only covered
//Blick2/Postal/Bennett's true 3-row shift-key machines; it silently printed
//"undef row" for Mignon (7 rows) and Helios Klimax (4 rows) whose rows don't
//even have that semantic meaning, and would have done the same for Hammond's
//4th (Math) row if that layout were selected.
//
//refChar vs char: refChar identifies which physical KEY/LEVER strikes this
//position (for correlating a real-machine impression test back to a key,
//e.g. Blickensderfer/Bennett/Mignon's Reference_Physical_Layout, wired from a
//dedicated Reference_Layout_Selection that's independent of whatever content
//Layout_Selection is being printed - the physical keyboard's key labels
//don't change just because you're test-printing a different language/layout).
//char is what's actually rendered (collapses to Test_Char under Test_Layout).
//Machines with no reference override (Postal/Helios/Hammond) pass the same
//value for both, so the two only ever diverge where a machine deliberately
//wired one in.
module TextRingDebug(row, col, char, refChar, platenBaseline, charBaseline){
    _rowLabels = is_undef(Row_Labels) ? [for (i=[0:len(Physical_Layout)-1]) str("row ", i)] : Row_Labels;
    oclock=(1-col/len(Physical_Layout[0]))*12;
    _charLabel = refChar==char ? str("'", char, "'") : str("keyboard key '", refChar, "' (rendered as '", char, "')");
    echo(str("character ", _charLabel, " on ", _rowLabels[row], " row at the ", round(oclock), "oclock position with platen cutout at ", platenBaseline, "mm and character baseline at ", charBaseline, "mm"));
}

//assembles every character in Physical_Layout onto the element
module TextRing(){
    _placementMap = is_undef(Placement_Map) ? [for (i=[0:len(Physical_Layout[0])-1]) i] : Placement_Map;
    _rowFont = is_undef(Row_Font) ? [for (i=[0:len(Physical_Layout)-1]) Font] : Row_Font;
    _rowFontSize = is_undef(Row_Font_Size) ? [for (i=[0:len(Physical_Layout)-1]) Font_Size] : Row_Font_Size;
    _rowFontLock = is_undef(Row_Font_Lock) ? [for (i=[0:len(Physical_Layout)-1]) false] : Row_Font_Lock;

    _referencePhysicalLayout = is_undef(Reference_Physical_Layout) ? Physical_Layout : Reference_Physical_Layout;

    for (row=[0:len(Physical_Layout)-1])
    for (col=[0:len(Physical_Layout[0])-1]){
        char=Test_Layout==false?Physical_Layout[row][col]:Test_Char;
        refChar=_referencePhysicalLayout[row][col];

        //charModsMatch drives the baseline offset unconditionally (matches
        //original: baseline offset never checked row-lock). fontIsCharMod
        //additionally respects Row_Font_Lock, since only font/size deferred to
        //the Hebrew-row override in the source files.
        charModsMatch = search(char, Character_Modifieds)!=[];
        fontIsCharMod = !_rowFontLock[row] && charModsMatch;

        useFont = fontIsCharMod ? Character_Modifieds_Font : _rowFont[row];
        useFontSize = fontIsCharMod ? Character_Modifieds_Size : _rowFontSize[row];

        placementLatitude = _placementMap[col];

        platenBaseline=Cutout[row]+
        (Cutout_Test==true?Cutout_Test_Array[col]:0);

        charBaseline_prime=Baseline[row]+(Baseline_Test==true?Baseline_Test_Array[col]:0);
        charBaseline=charModsMatch?charBaseline_prime+Character_Modifieds_Offset:charBaseline_prime;

        translate([0, 0, Baseline_Z_Offset])
        LetterText(char, useFont, useFontSize, platenBaseline, charBaseline, placementLatitude);
        if (Cutout_Test || Baseline_Test || Test_Layout)
            TextRingDebug(row, col, char, refChar, platenBaseline, charBaseline);
    }
}
