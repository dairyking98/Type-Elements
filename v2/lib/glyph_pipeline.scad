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
//- Element_Diameter/Platen_Diameter/CharProtrusion/Baseline/Cutout are the
//canonical names adopted from Bennett/Mignon's original convention; Blick2/
//Postal's cylOD/platenOD/textProtrusion/charBaselines/platenBaselines were
//renamed to match):
//  z, minkFn, textFn, cylFn, surfaceFn        - quality vars
//  minkOn, minkDraftAngle                     - draft angle control
//  Element_Diameter, Platen_Diameter, CharProtrusion, latitudeInt - dimensions
//  font, fontSize                             - base typeface
//  physicalLayout                             - 2D array [row][col] of chars,
//                                                already resolved to the exact
//                                                physical column order and with
//                                                any machine-specific character
//                                                substitution already applied
//  Baseline, Cutout                           - per-row baseline arrays
//  baselineZOffset                            - Z added to every character's
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
//  cutoutTest, cutoutTestArray, baselineTest, baselineTestArray, testLayout, testChar
//
//Unified glyph-quality features (every v2 machine declares all of these):
//  fontWeightOffset, xFontWeightAdj, yFontWeightAdj
//                       - offset()-based stroke weight (Blickensderfer2/
//                         Postal's original system). 0 = no-op.
//  Weight_Adj_Mode, Weight_Adj_Shape, Horizontal_Weight_Adj, Vertical_Weight_Adj
//                       - minkowski erosion/growth stroke-weight system
//                         (0=none/1=subtractive/2=additive), independent of
//                         and layered with fontWeightOffset above. Mode 0 is
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
//                         own font/fontSize for a no-op font swap (baseline
//                         offset still applies) - this is how Bennett/Mignon,
//                         whose original systems only ever shifted baseline,
//                         stay behaviorally identical while gaining the
//                         (unused-by-default) font-swap capability.
//  Scale_Multiplier_Text, Scale_Multiplier
//                       - per-character size override (e.g. make "." larger).
//                         Scale_Multiplier_Text="" = no-op.
//  Y_Scale               - vertical scale applied to the glyph before
//                         extrusion. 1 = no-op.
//  Typeface_2, Type_2Size, Typeface_2Chars
//                       - secondary-typeface-by-character system, independent
//                         of and resolved before Scale_Multiplier_Text sizing.
//                         Typeface_2Chars="" = no-op.
//
//Optional (lib supplies a default if a machine file leaves these undefined -
//these are structural/composition knobs, not customizer-facing features, so
//they stay opt-in rather than part of the unified declared set above):
//  placementMap        - per-column index -> physical placement latitude.
//                         Default: identity (column N places at latitude N).
//  rowLabels            - per-row name array used only by TextRingDebug's
//                         console echo (cutoutTest/baselineTest/testLayout).
//                         Default: numeric "row 0"/"row 1"/etc. Blick2/Postal/
//                         Bennett/Hammond override this to their real
//                         ["lowercase","uppercase","figs"(,"math")] shift
//                         names.
//  referencePhysicalLayout - a second physicalLayout-shaped array, used only
//                         by TextRingDebug's console echo to identify which
//                         physical keyboard key/lever strikes a given
//                         position - independent of testLayout (which still
//                         collapses the actual RENDERED glyph to testChar)
//                         and independent of whatever content Layout is
//                         currently selected for printing. Default: same as
//                         physicalLayout. Blickensderfer/Bennett/Mignon wire
//                         this from a dedicated referenceLayoutSelection
//                         dropdown (reusing each machine's own layout preset
//                         list + its fixed keyboard->physical hardware remap)
//                         so switching what you're printing never changes
//                         what the echo calls a given physical position - the
//                         real keyboard's key labels are a hardware fact of
//                         the machine, not a function of what you're
//                         currently engraving.
//  rowFont, rowFontSize - per-row font/size array. Default: global font/fontSize
//                         repeated for every row.
//  rowFontLock          - per-row boolean array. When true for a row, that row's
//                         rowFont/rowFontSize always wins over a
//                         Character_Modifieds match (this is how
//                         Blickensderfer2's Hebrew row0 stays on fontHebrew
//                         regardless of Character_Modifieds). Default: all false.
//  text2DFn             - local $fn override inside TwoDText(). Default: inherit
//                         ambient $fn from the caller (matches Blickensderfer2).
//  minkHFixed            - override the shared draft-cone h=2. Default 2.
//  letterPlacementProtrusion - radial offset added at the placement stage
//                       (Element_Diameter/2 + this). Default: same as
//                       CharProtrusion (Blickensderfer2/Postal's original
//                       behavior - their raw material stands proud of the
//                       plain element surface before any cutout trims it).
//                       Bennett/Mignon/Helios set this to 0: their placement
//                       radius is the raw Element_Diameter/2, with embed
//                       depth controlled instead by letterExtrudeOffset below
//                       - CharProtrusion still applies in PlatenCutout's
//                       formula regardless of this override (verified
//                       algebraically: Bennett's Platen_Diameter/2+
//                       Min_Final_Character_Diameter/2 cutout radius is
//                       exactly Element_Diameter/2+Platen_Diameter/2+
//                       CharProtrusion once CharProtrusion is expanded, so
//                       the cutout side was never wrong - only the placement
//                       side needed this override).
//  letterExtrudeOffset, letterExtrudeDepth
//                       - Z offset/depth of the raw pre-cutout linear_extrude,
//                         in the LetterPlacement-local frame (local Z = radial
//                         direction once placed). Default 0/6 (Blickensderfer2/
//                         Postal). Bennett uses -.5/2 - since this raw block
//                         is always trimmed down by the (verified) PlatenCutout
//                         afterward, it only needs to be deep enough to contain
//                         the final shape, so this needed no separate
//                         verification beyond the cutout itself.
//  angleHalfStep         - constant added to `latitude` before multiplying by
//                         latitudeInt, i.e. angle = (angleHalfStep+latitude)*
//                         latitudeInt. Default .5 (Blickensderfer2/Postal/
//                         Bennett all center each column between latitude band
//                         edges this way). Mignon has no such half-column
//                         offset, so it sets this to 0.

function minkTextR(draft_angle) = 2*tan(.5*draft_angle);

//2D glyph shape, mirrored so it reads correctly once placed facing outward.
//NOTE: preserves a pre-existing typo from Blick2/Postal - the y term of the
//weight-adjust square references "yFontWieghtAdj" (misspelled), which is
//always undef, so this branch only actually resolves when xFontWeightAdj>0
//with yFontWeightAdj left at 0. Kept as-is for exact behavioral parity.
module TwoDText(char, font, size){
    $fn = is_undef(text2DFn) ? $fn : text2DFn;
    _weightAdjMode = Weight_Adj_Mode;
    //Typeface_2Chars resolves BEFORE Scale_Multiplier_Text sizing, matching
    //Mignon's original precedence exactly.
    _isTypeface2 = search(char, Typeface_2Chars)!=[];
    _font = _isTypeface2 ? Typeface_2 : font;
    _baseSize = _isTypeface2 ? Type_2Size : size;
    _useSize = search(char, Scale_Multiplier_Text)==[] ? _baseSize : _baseSize*Scale_Multiplier;

    offset(fontWeightOffset)
    mirror([1, 0, 0]){
        if (_weightAdjMode==2)//Additive
            minkowski(){
                text(text=char, size=_useSize, font=_font, valign="baseline", halign="center", $fn=textFn);
                WeightAdjShape();
            }
        else if (_weightAdjMode==1)//Subtractive
            difference(){
                text(text=char, size=_useSize, font=_font, valign="baseline", halign="center", $fn=textFn);
                minkowski(){
                    difference(){
                        square([10, 10], center=true);
                        text(text=char, size=_useSize, font=_font, valign="baseline", halign="center", $fn=textFn);
                    }
                    WeightAdjShape();
                }
            }
        else //None - Blick2/Postal's original offset+square weight system
            minkowski(){
                text(text=char, size=_useSize, font=_font, valign="baseline", halign="center", $fn=textFn);
                if (xFontWeightAdj>0 || yFontWeightAdj>0)
                square([z+xFontWeightAdj, z+yFontWieghtAdj], center=true);
            }
    }
}

//Bennett's 2D weight-adjuster profile/shape, used by TwoDText's mode 1/2
module WeightAdjShape(){
    if (Weight_Adj_Shape==0 && Weight_Adj_Mode!=0)
    square([Horizontal_Weight_Adj, Vertical_Weight_Adj], center=true);
    if (Weight_Adj_Shape==1 && Weight_Adj_Mode!=0)
    scale([Horizontal_Weight_Adj, Vertical_Weight_Adj])
    circle(r=1, $fn=minkFn);
}

//concave underside cutout so the character conforms to the platen curvature
module PlatenCutout(platenBaseline, latitude){
    _angleHalfStep = is_undef(angleHalfStep) ? .5 : angleHalfStep;
    rotate([0, 0, (_angleHalfStep+latitude)*latitudeInt])
    translate([Element_Diameter/2+Platen_Diameter/2+CharProtrusion, 0, platenBaseline])
    rotate([90, 0, 0])
    cylinder(d=Platen_Diameter, h=10, center=true, $fn=cylFn);
}

//places a glyph at its circumferential/axial position on the element
module LetterPlacement(textBaseline, latitude){
    _angleHalfStep = is_undef(angleHalfStep) ? .5 : angleHalfStep;
    //letterPlacementProtrusion: Blick2/Postal add the full CharProtrusion to
    //BOTH the placement radius and the platen-cutout radius (their raw
    //material genuinely stands proud of the plain element surface before any
    //cutout trims it). Bennett/Mignon/Helios only need CharProtrusion in the
    //cutout formula (verified algebraically for Bennett - see PlatenCutout);
    //their placement radius is the raw Element_Diameter/2, with embed depth
    //controlled instead by letterExtrudeOffset. Default keeps Blick2/Postal's
    //original behavior; Bennett/Mignon/Helios override this to 0.
    _placementProtrusion = is_undef(letterPlacementProtrusion) ? CharProtrusion : letterPlacementProtrusion;
    rotate([0, 0, (_angleHalfStep+latitude)*latitudeInt])
    translate([0, 0, textBaseline])
    translate([Element_Diameter/2+_placementProtrusion-z, 0, 0])
    rotate([90, 0, 90])
    children();
}

//full drafted single-character solid: extrude, platen cutout, minkowski taper
module LetterText(char, font, size, platenBaseline, textBaseline, latitude){
    $fn=surfaceFn;
    _extrudeOffset = is_undef(letterExtrudeOffset) ? 0 : letterExtrudeOffset;
    _extrudeDepth = is_undef(letterExtrudeDepth) ? 6 : letterExtrudeDepth;
    _yScale = Y_Scale;
    //the draft cone is an arbitrary taper shape, not a calibrated dimension -
    //r2 comes from the draft angle (the physically meaningful parameter),
    //r1=0 (apex). h=2 is Blickensderfer2/Postal's already-proven "big enough,
    //not unreasonably large" value; every machine shares it unless it
    //explicitly needs something else via minkHFixed.
    _minkH = is_undef(minkHFixed) ? 2 : minkHFixed;
    _angleHalfStep = is_undef(angleHalfStep) ? .5 : angleHalfStep;
    //skipPlatenCutout: Hammond strikes a flat anvil, not a curved platen, so
    //there's no concave cutout to carve - difference() with only the extruded
    //text child (no PlatenCutout operand) is just that child unchanged.
    _skipPlatenCutout = is_undef(skipPlatenCutout) ? false : skipPlatenCutout;
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
        if (minkOn==true){
            rotate([0, -90, (_angleHalfStep+latitude)*latitudeInt])
            cylinder(r1=0, r2=minkTextR(minkDraftAngle), h=_minkH, $fn=minkFn);
        }
    }
}

//rowLabels: optional per-machine row-name array (default: numeric "row N").
//Found via testing with actual OpenSCAD (openscad-nightly) - the previous
//hardcoded 3-entry ["lowercase","uppercase","figs"] array only covered
//Blick2/Postal/Bennett's true 3-row shift-key machines; it silently printed
//"undef row" for Mignon (7 rows) and Helios Klimax (4 rows) whose rows don't
//even have that semantic meaning, and would have done the same for Hammond's
//4th (Math) row if that layout were selected.
//
//refChar vs char: refChar identifies which physical KEY/LEVER strikes this
//position (for correlating a real-machine impression test back to a key,
//e.g. Blickensderfer/Bennett/Mignon's referencePhysicalLayout, wired from a
//dedicated referenceLayoutSelection that's independent of whatever content
//Layout_Selection is being printed - the physical keyboard's key labels
//don't change just because you're test-printing a different language/layout).
//char is what's actually rendered (collapses to testChar under testLayout).
//Machines with no reference override (Postal/Helios/Hammond) pass the same
//value for both, so the two only ever diverge where a machine deliberately
//wired one in.
module TextRingDebug(row, col, char, refChar, platenBaseline, charBaseline){
    _rowLabels = is_undef(rowLabels) ? [for (i=[0:len(physicalLayout)-1]) str("row ", i)] : rowLabels;
    oclock=(1-col/len(physicalLayout[0]))*12;
    _charLabel = refChar==char ? str("'", char, "'") : str("keyboard key '", refChar, "' (rendered as '", char, "')");
    echo(str("character ", _charLabel, " on ", _rowLabels[row], " row at the ", round(oclock), "oclock position with platen cutout at ", platenBaseline, "mm and character baseline at ", charBaseline, "mm"));
}

//assembles every character in physicalLayout onto the element
module TextRing(){
    _placementMap = is_undef(placementMap) ? [for (i=[0:len(physicalLayout[0])-1]) i] : placementMap;
    _rowFont = is_undef(rowFont) ? [for (i=[0:len(physicalLayout)-1]) font] : rowFont;
    _rowFontSize = is_undef(rowFontSize) ? [for (i=[0:len(physicalLayout)-1]) fontSize] : rowFontSize;
    _rowFontLock = is_undef(rowFontLock) ? [for (i=[0:len(physicalLayout)-1]) false] : rowFontLock;

    _referencePhysicalLayout = is_undef(referencePhysicalLayout) ? physicalLayout : referencePhysicalLayout;

    for (row=[0:len(physicalLayout)-1])
    for (col=[0:len(physicalLayout[0])-1]){
        char=testLayout==false?physicalLayout[row][col]:testChar;
        refChar=_referencePhysicalLayout[row][col];

        //charModsMatch drives the baseline offset unconditionally (matches
        //original: baseline offset never checked row-lock). fontIsCharMod
        //additionally respects rowFontLock, since only font/size deferred to
        //the Hebrew-row override in the source files.
        charModsMatch = search(char, Character_Modifieds)!=[];
        fontIsCharMod = !_rowFontLock[row] && charModsMatch;

        useFont = fontIsCharMod ? Character_Modifieds_Font : _rowFont[row];
        useFontSize = fontIsCharMod ? Character_Modifieds_Size : _rowFontSize[row];

        placementLatitude = _placementMap[col];

        platenBaseline=Cutout[row]+
        (cutoutTest==true?cutoutTestArray[col]:0);

        charBaseline_prime=Baseline[row]+(baselineTest==true?baselineTestArray[col]:0);
        charBaseline=charModsMatch?charBaseline_prime+Character_Modifieds_Offset:charBaseline_prime;

        translate([0, 0, baselineZOffset])
        LetterText(char, useFont, useFontSize, platenBaseline, charBaseline, placementLatitude);
        if (cutoutTest || baselineTest || testLayout)
            TextRingDebug(row, col, char, refChar, platenBaseline, charBaseline);
    }
}
