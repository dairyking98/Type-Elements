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
    # Catalogued but NOT imported - each needs its own figures row (and in
    # a few cases a different letter row), transcribed and verified the
    # same way before it can be added:
    #   Universal fractions ...... 26, 41, 52, 162, 184, 40 (LARGE), 97,
    #                              80A, 23F, 23G
    #   Caps and Small Caps ...... 27, 27E, 136 (row 0 is caps, not
    #                              lowercase - a different row SHAPE)
    #   Medical/chemical ......... 43, 43A, 107, 179, 21, 18
    #   Diacritical/library ...... 113, 122, 48C
    #   Literary ................. 192, 193, 194
    #   Non-Latin / special ...... 195 Astronomical, 196/197 International
    #                              Phonetic, 135/135B/135C Mathematical,
    #                              112C Greek, 59/20 German Text,
    #                              165/167 Yiddish, 185 Check Writer
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
}
