"""
Bennett keyboard layout presets (see blickensderfer_layout.py's note).
"""

# Bennett's 4 named layouts, ported verbatim from v2/lib/layouts/
# bennett_layouts.scad's ENGLISH/BRITISH/INTERNATIONAL arrays plus
# v2/bennett.scad's own CUSTOMLAYOUT (Lowercase/Uppercase/Figs - identical
# content to ENGLISH by default, a real, if redundant, 4th LAYOUTS entry
# in v2's own source, not an omission here). All 4 share the same
# 3-row/28-column structure and identity placement_map. Rows are shown in
# keyboard-legend order (as printed on the physical keyboard), matching
# config/bennett.yaml's layout.char_legend remap - see lib/bennett.py's
# configure().
LAYOUT_PRESETS_BENNETT = {
    "English": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"#$%56;?:,£@_(&-)/'.",
    ],
    "British": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"¾$%56;?:½£@_(&-)/'¼",
    ],
    "Custom": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKL,ZXCVGHBNM.",
        "12347890\"#$%56;?:,£@_(&-)/'.",
    ],
    "International": [
        "qweruiopasdftyjkl,zxcvghbnm.",
        "QWERUIOPASDFTYJKLÖZXCVGHBNMÄ",
        "1234789üà#£%56?Ååö§@:(&-)/\"ä",
    ],
}
