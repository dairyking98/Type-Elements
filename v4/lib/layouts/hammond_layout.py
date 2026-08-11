"""
Hammond keyboard layout presets, plus the shared Hammond type-shuttle
catalog data both Hammond machines draw on (CATALOG_*).

hammond_split_layout.py imports the CATALOG_* tables from here - they are
defined once, in this module, because the printed catalog covers both
machines. Note the two machines store rows in OPPOSITE orders; see
CATALOG_UNIVERSAL_STANDARD's comment.
"""

# ---------------------------------------------------------------------
# Hammond type-shuttle catalog (both Hammond machines)
# ---------------------------------------------------------------------
# Primary source: the Hammond Typewriter Company's own "ENGLISH Type
# Shuttles for the Hammond Typewriter" catalog, Form QQ-10M-11-20-W
# (Nov 1920). Every entry is "<shuttle number>-<typeface>", followed by
# three 30-character rows printed as two 15-character halves - which is
# exactly this family's layout.rows/latitude_columns=30 shape.
#
# Two keyboards, and they are NOT interchangeable layouts:
#   Universal - qwerty, the familiar arrangement.
#   Ideal     - Hammond's own proprietary arrangement, a different set of
#               key positions entirely (not a qwerty remap).
# Both appear in the catalog and both are real for either machine, so
# both are offered on hammond AND hammond_split below. NOTE the storage
# order differs per machine and is load-bearing: hammond stores rows
# REVERSED (see its "Normal Universal" preset), hammond_split stores them
# in catalog reading order (lib/hammond_split.py's TextAssemble does its
# own per-half [14-i]/[29-i] reversal). The reversal is applied
# programmatically below rather than by hand-retyping the strings.
#
# The catalog's ~80 entries collapse to a handful of distinct LAYOUTS -
# most differ only in typeface (a font choice here, not a layout), and
# within a keyboard the letter rows are constant, so all real variation
# is in the figures row. Only the three layouts verified character-by-
# character against the scan are defined here; CATALOG_SHUTTLES records
# which numbered shuttles each one covers, and which catalogued variants
# are deliberately NOT imported yet.
CATALOG_UNIVERSAL_STANDARD = [
    "qazwsxedcrfvtgb" "yhnujmik,ol.p;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    '1"@2#×3$+4%£5_¢' "6&*7'^8(°9).0=/",
]
CATALOG_IDEAL_STANDARD = [
    "?zxqkjgbmpcfld," ".taherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "=%@÷#×1+2¢3£4$5" "6“7”8’9(0)°’_”/",
]
CATALOG_IDEAL_FRACTIONS = [
    "?zxqkjgbmpcfld," ".taherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "¾%⅞⅝½⅜1⅛2¢3£4$5" "6“7”8’9(0)¼*⅓†⅔",
]
# Universal with a 9-fraction figures row. Reading the catalog by COLUMN
# (each column is one physical key: unshifted / shifted / figure) shows
# what this shuttle actually did, and the three rows corroborate each
# other: nine figure slots became fractions (#×+ &*^ °.= -> ⅜⅔⅓ ⅝⅛½
# ¼¾⅞), and the "&" those displaced was re-homed onto the shifted "."
# key - which is why row 1 is untouched but row 2 reads ...?OL&P:! where
# standard reads ...?OL.P:!. That "." key is the one with a bare dot on
# all three levels (visible on the "UNIVERSAL" KEYBOARD plate, p.2), so
# it was the only spare slot to move & into.
CATALOG_UNIVERSAL_FRACTIONS = [
    "qazwsxedcrfvtgb" "yhnujmik,ol.p;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL&P:!",
    '1"@2⅜⅔3$⅓4%£5_¢' "6⅝⅛7'½8(¼9)¾0⅞/",
]
# Caps and Small Caps: the UNSHIFTED row types capitals too, so rows 0/1
# differ only in their punctuation (the same ,/./;/- vs ?/./:/! split
# every other layout has). The catalog prints row 0 in visibly smaller
# capitals - that is the TYPEFACE (small caps), not a different
# character, and v4 selects it via the Font tab like any other typeface,
# so both rows carry the same letters here. Figures row is standard.
CATALOG_UNIVERSAL_CAPS_SMALL_CAPS = [
    "QAZWSXEDCRFVTGB" "YHNUJMIK,OL.P;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    '1"@2#×3$+4%£5_¢' "6&*7'^8(°9).0=/",
]
# Which catalogued shuttles use each layout above, and what was left out.
# Reference data for the Layout tab's help banner and for anyone adding
# the remaining variants later - not consumed as layout content itself.
CATALOG_SHUTTLES = {
    "universal_standard": (
        "23/23B Medium Roman, 24/24B Small Roman, 25/25A/25B Large Roman, "
        "158/158A Minature Roman, 180 Petite Gothic, 96 Medium Gothic, "
        "134 Large Gothic, 170 Clarendon, 68 Small Italic, "
        "169 Medium Italic, 97B Large Gothic Italic, 28 Law Italic, "
        "80 Vertical Script, 145 Multigraph (Pica)"
    ),
    "ideal_standard": (
        "10/10A/10B/94 Medium Roman, 37A Small Roman, 51/51A/3B Large "
        "Roman, 60 Gothic Italic, 118 Law Italic, 70 Vertical Script, "
        "144A Multigraph (Pica)"
    ),
    "ideal_fractions": (
        "1/48/48A Medium Roman, 2 Small Roman, 3/3A Large Roman, "
        "4 Gothic, 5 Caps and Small Caps, 6 Italic, 9 Attic"
    ),
    "universal_fractions": (
        "26 Small Roman, 40 Medium Roman (LARGE FRACTIONS), 52 Large "
        "Roman, 80A Vertical Script, 97 Large Gothic Italic"
    ),
    "universal_caps_small_caps": "27, 27E",
    # Catalogued but NOT imported, with the reason each one was left out.
    # These are deliberate exclusions, not an unworked backlog: where the
    # scan does not settle a character beyond doubt, no layout is better
    # than a guessed one, since a wrong glyph here silently builds a wrong
    # shuttle. Anything added later needs the same character-by-character
    # verification the imported layouts got.
    #
    #   41 Small Roman FRACTIONS - a SECOND, different fractions scheme:
    #     diagonal fractions (⅔ ⅓ ⅛ ½ ¼ ¾) rather than the stacked set
    #     above, and it keeps & in the figures row instead of moving it to
    #     the shifted "." key. Legible in outline but several fraction
    #     numerators are not separable at this scan resolution.
    #   162 Medium Gothic FRACTIONS - right half matches
    #     CATALOG_UNIVERSAL_FRACTIONS exactly, but the left half reads
    #     "...3=⅓4%?5´+" where that layout has "...3$⅓4%£5_¢"; the
    #     character after "4%" is damaged in the scan and cannot be
    #     called.
    #   184 Gothic SPECIAL FRACTIONS - prints FOUR lines, not three (an
    #     extra dense fraction bank), so it does not fit the 3-row shape
    #     at all without deciding which line is the real figures row.
    #   23E/23F/23G Medium Roman - near-standard, each differing in one
    #     or two figure slots (23E has an unidentifiable glyph where
    #     standard has "+"; 23F/23G mix single fractions into otherwise
    #     standard rows). Too close to standard to guess at.
    #   136 Caps and Small Caps SPECIAL CHEMICAL - caps rows as 27/27E,
    #     but the chemical figures row is not legible enough to call.
    #   Medical/chemical ......... 43, 43A, 107, 179, 21, 18 - purpose-made
    #     symbol sets (dose/measure/chemical marks) with no reliable
    #     Unicode reading from this scan.
    #   Diacritical/library ...... 113, 122, 48C - bare combining accents
    #     printed in isolation; which precomposed/combining codepoint each
    #     one means is a judgement call, not a reading.
    #   Literary ................. 192, 193, 194 - subscript/superscript
    #     digit banks and reference marks, ambiguous at this resolution.
    #   Non-Latin / special ...... 195 Astronomical, 196/197 International
    #     Phonetic, 135/135B/135C Mathematical, 112C Greek, 59/20 German
    #     Text (fraktur), 165/167 Yiddish (Hebrew), 185 Check Writer
    #     (perforating, prints as dot matrices) - each needs its own script
    #     expertise and, for several, a font that has the glyphs at all.
    "not_imported": "see the comment above this key",
}
# v2/lib/layouts/hammond_layouts.scad's LAYOUTS[0]/LAYOUTS[2] (Normal_U/
# Math_U) - the two real presets that differ in ROW COUNT (3 vs 4), which
# no other machine's layout presets do. "Math Universal" is the "math
# shuttle" variant - confirmed identical in v1/Hammond/HammondShuttle.scad
# (the pre-v2-migration original), nothing extra hiding there. Is_Math
# auto-derives from len(rows)==4 (lib/hammond.py's configure()), so
# selecting this preset alone is enough to switch Shuttle_Height/the Xx
# resin-support array - see LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE below
# for how baseline_row/cutout_row (which ALSO need a 4th entry for this
# preset) get resized to match.
LAYOUT_PRESETS_HAMMOND = {
    "Normal Universal": [
        "-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1",
    ],
    "Math Universal": [
        "√·p.lo,kimjunhybgtvfrcdexswzaq",
        "∫:P∂LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0>)9<(8|'7*÷6]Γ5[∝4+Δ3×∑2_\"1",
        "―ₙ₀πλ₉ωκ₈φε₇τη₆βγ₅θψ₄ρδ₃ξσ₂ζα₁",
    ],
    # Ideal keyboard (Hammond's own proprietary layout, NOT qwerty) - the
    # same two shuttles LAYOUT_PRESETS_HAMMOND_SPLIT carries, reversed into
    # this machine's storage order. See CATALOG_SHUTTLES for the source and
    # the shuttle numbers each one covers.
    "Ideal": [r[::-1] for r in CATALOG_IDEAL_STANDARD],
    "Ideal, Fractions": [r[::-1] for r in CATALOG_IDEAL_FRACTIONS],
    "Universal, Fractions": [r[::-1] for r in CATALOG_UNIVERSAL_FRACTIONS],
    "Universal, Caps and Small Caps": [
        r[::-1] for r in CATALOG_UNIVERSAL_CAPS_SMALL_CAPS
    ],
}
