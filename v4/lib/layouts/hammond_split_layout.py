"""
Hammond Split keyboard layout presets (see blickensderfer_layout.py's
note). The CATALOG_* tables these are built from live in
hammond_layout.py, since the printed catalog covers both machines.
"""

from .hammond_layout import (
    CATALOG_IDEAL_FRACTIONS,
    CATALOG_IDEAL_STANDARD,
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
    "IDEAL (£)": [
        "?zxqkjgbmpcfld,.taherisounwyv:",
        "!ZXQKJGBMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3£4$56“7”8’9[0]¼*⅓†⅔",
    ],
    "IDEAL (⅌)": [
        "?zxqkjgbmpcfld,.taherisounwyv:",
        "!ZXQKJGBMPCFLD;-TAHERISOUNWYV&",
        "¾%⅞⅝½⅜1⅛2¢3⅌4$56“7”8’9[0]¼*⅓†⅔",
    ],
    # Catalog-derived (see CATALOG_* above). This machine stores rows in
    # catalog reading order, so they go in unreversed.
    #
    # "IDEAL, Fractions" is the same shuttle family as "IDEAL (£)" above
    # but transcribed from the catalog rather than from v1/v2, and the two
    # differ in one place: v1/v2 read "9[0]" where every catalogued Ideal
    # entry reads "9(0)" (square vs round brackets). Both are kept -
    # "IDEAL (£)"/"IDEAL (⅌)" preserve the source history v4 shipped with,
    # these preserve the printed catalog - rather than silently picking a
    # winner, same treatment as the £/⅌ pair itself.
    "IDEAL, Standard": list(CATALOG_IDEAL_STANDARD),
    "IDEAL, Fractions": list(CATALOG_IDEAL_FRACTIONS),
    # Universal (qwerty). v2/hammond_split.scad:80-82 already had this as
    # Qwerty_Element (Layout_Selection=1) but it was never wired into the
    # picker; ported here with two characters corrected against the
    # catalog - v2 had ⅌ at the '#'/× position and § at the '∧' position,
    # neither of which any catalogued Universal entry shows, and both of
    # which hammond.yaml's own Universal row already spells the catalog's
    # way (× and ^).
    "UNIVERSAL": list(CATALOG_UNIVERSAL_STANDARD),
}
