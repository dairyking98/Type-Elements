"""
Hammond Split keyboard layout presets (see blickensderfer_layout.py's
note). The CATALOG_* tables these are built from live in
hammond_layout.py, since the printed catalog covers both machines.
"""

from .hammond_layout import (
    CATALOG_IDEAL_CROATIAN,
    CATALOG_IDEAL_DANISH_FRACTIONS,
    CATALOG_IDEAL_DUTCH,
    CATALOG_IDEAL_FRENCH,
    CATALOG_IDEAL_GERMAN,
    CATALOG_IDEAL_GERMAN_NEW_ORTHOGRAPHY,
    CATALOG_UNIVERSAL_ESPERANTO,
    CATALOG_UNIVERSAL_FRENCH,
    CATALOG_UNIVERSAL_FRENCH_GERMAN_ENGLISH,
    CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY,
    CATALOG_IDEAL_PORTUGUESE,
    CATALOG_IDEAL_FRACTIONS,
    CATALOG_IDEAL_SPANISH,
    CATALOG_IDEAL_SPANISH_CAPS,
    CATALOG_IDEAL_SPANISH_CENT,
    CATALOG_IDEAL_STANDARD,
    CATALOG_UNIVERSAL_CAPS_SMALL_CAPS,
    CATALOG_UNIVERSAL_FRACTIONS,
    CATALOG_UNIVERSAL_STANDARD,
)

# Two real "Ideal_Element" variants for the figures row's £/⅌ position -
# see SESSION_LOG.md part 77's archaeology. v1's oldest source
# (HammondSplitShuttle.scad, Feb 2024) had a commented-out "Layout as
# 'stamped'" figures row using ⅌ (the per-unit sign - also Char_Mod's
# own default value, config/hammond_split.yaml's char_mod.char) in place
# of £ at the same position; every later revision (HammondSplitShuttle2.
# scad onward, including v2/hammond_split.scad and v4's shipped default)
# uses £ there instead, with no trace of the ⅌ variant left in the
# source. Both are real historical values, not invented - installed as
# two selectable presets (per explicit user request) rather than picking
# one. Rows 0/1 are identical between them; only row 2's one £/⅌
# character differs.
LAYOUT_PRESETS_HAMMOND_SPLIT = {
    "Ideal (£)": [
        "?zxqkjgbmpcfld,.taherisounwyv:",
        "!ZXQKJGBMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔",
    ],
    "Ideal (⅌)": [
        "?zxqkjgbmpcfld,.taherisounwyv:",
        "!ZXQKJGBMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3⅌4$56“7”8’9[0]¼*⅓†⅔",
    ],
    # Catalog-derived (see CATALOG_* above). This machine stores rows in
    # catalog reading order, so they go in unreversed.
    #
    # "Ideal, Fractions" is the same shuttle family as "Ideal (£)" above
    # but transcribed from the catalog rather than from v1/v2, and the two
    # differ in one place: v1/v2 read "9[0]" where every catalogued Ideal
    # entry reads "9(0)" (square vs round brackets). Both are kept -
    # "Ideal (£)"/"Ideal (⅌)" preserve the source history v4 shipped with,
    # these preserve the printed catalog - rather than silently picking a
    # winner, same treatment as the £/⅌ pair itself.
    "Ideal, Standard": list(CATALOG_IDEAL_STANDARD),
    "Ideal, Fractions": list(CATALOG_IDEAL_FRACTIONS),
    # Universal (qwerty). v2/hammond_split.scad:80-82 already had this as
    # Qwerty_Element (Layout_Selection=1) but it was never wired into the
    # picker; ported here with two characters corrected against the
    # catalog - v2 had ⅌ at the '#'/× position and § at the '∧' position,
    # neither of which any catalogued Universal entry shows, and both of
    # which hammond.yaml's own Universal row already spells the catalog's
    # way (× and ^).
    "Universal": list(CATALOG_UNIVERSAL_STANDARD),
    "Universal, Fractions": list(CATALOG_UNIVERSAL_FRACTIONS),
    "Universal, Caps and Small Caps": list(
        CATALOG_UNIVERSAL_CAPS_SMALL_CAPS
    ),
    # Per-language Ideal shuttles (1915 catalog)
    "Ideal, Dutch": list(CATALOG_IDEAL_DUTCH),
    "Ideal, Spanish": list(CATALOG_IDEAL_SPANISH),
    "Ideal, Spanish (¢)": list(CATALOG_IDEAL_SPANISH_CENT),
    "Ideal, Spanish (Caps and Small Caps)": list(CATALOG_IDEAL_SPANISH_CAPS),
    "Ideal, Croatian": list(CATALOG_IDEAL_CROATIAN),
    "Ideal, Danish (Fractions)": list(CATALOG_IDEAL_DANISH_FRACTIONS),
    "Ideal, Portuguese": list(CATALOG_IDEAL_PORTUGUESE),
    "Ideal, French": list(CATALOG_IDEAL_FRENCH),
    "Ideal, German (New Orthography)": list(
        CATALOG_IDEAL_GERMAN_NEW_ORTHOGRAPHY
    ),
    "Ideal, German": list(CATALOG_IDEAL_GERMAN),
    "Universal, German (New Orthography)": list(
        CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY
    ),
    "Universal, French": list(CATALOG_UNIVERSAL_FRENCH),
    "Universal, French-German-English": list(
        CATALOG_UNIVERSAL_FRENCH_GERMAN_ENGLISH
    ),
    "Universal, Esperanto": list(CATALOG_UNIVERSAL_ESPERANTO),
}
