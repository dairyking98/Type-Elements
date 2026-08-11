"""
Postal keyboard layout presets (see blickensderfer_layout.py's note).
"""

# Postal has exactly ONE named layout preset - v2/postal.scad has only
# one physical layout, no preset-switching menu like Blickensderfer's (see
# blickensderfer_layout.py's LAYOUT_PRESETS) - so "QWERTY" is both the
# only option and the default (matches config/postal.yaml's own
# layout.rows exactly: v2's
# Physical_Layout = Keyboard_Layout_Array[row][Element_Layout_Array_Map[col]],
# postal.scad:271-274 - same values, computed once in config/postal.yaml's
# comment rather than re-derived here).
LAYOUT_PRESETS_POSTAL = {
    "QWERTY": [
        "byhnujmik,ol.pqazwsxedcrfvtg",
        "BYHNUJMIK&OL?PQAZWSXEDCRFVTG",
        "!6_+7;=8:§9'-%\"(£2)ä3@ö4/ü5$",
    ],
}
