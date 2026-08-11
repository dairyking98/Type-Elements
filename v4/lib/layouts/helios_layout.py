"""
Helios Klimax keyboard layout presets (see blickensderfer_layout.py's
note).
"""

# Helios's layout arrays - GERMAN and GERMAN_MOD are from v2/
# heliosklimax.scad's [Key Mapping] section (LAYOUT=GERMAN_MOD is what v2
# actually assigns/uses; GERMAN is a real, if superseded, second array in
# the source, exposed here the same way Bennett's redundant CUSTOM preset
# is). ROTUNDA is a third real preset, NOT from v2 (v2 only ever carried
# GERMAN/GERMAN_MOD forward) - it's from v1/HeliosKlimax/
# HeliosKlimaxTester.scad's own Layouts=[GERMAN, GERMAN_MOD, ROTUNDA]
# (a real, live Layout_Selection=0/1/2 option there, not dead code - see
# lib/helios.py's module docstring for why Tester.scad is a real, richer
# source alongside Element.scad, not just a superseded prototype). Row 2
# differs by one real character (a long-s "$" stand-in for Rotunda
# blackletter's lowercase s at column 12, vs GERMAN_MOD's plain "s") and
# row 4 differs by one real character (XYÓß vs XY¢ß/XY₰ß) - transcribed
# exactly as v1 has them, not normalized to match the other two rows.
# All three share the same 4-row/21-column structure and identity
# placement_map (Physical_Layout=LAYOUT directly, no CharLegend remap).
LAYOUT_PRESETS_HELIOS = {
    "GERMAN_MOD": [
        "wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
        "\"()Z⁄J=,;XY¢ß&%/-_§?Q",
    ],
    "GERMAN": [
        "wertuionklpasdcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
        "\"()Z⅟J=,;XY₰ß&%/-_§?Q",
    ],
    "ROTUNDA": [
        "wertuionklpa$dcfghbvm",
        "WERTUIONKLPASDCFGHBVM",
        "'!+züjö.:xyä23456789q",
        "\"()Z⅟J=,;XYÓß&%/-_§?Q",
    ],
}
