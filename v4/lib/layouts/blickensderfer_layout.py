"""
Blickensderfer keyboard layout presets - the named layouts offered by
tune.py's Layout tab picker.

Moved verbatim out of tune.py so layout DATA lives with the other layout
modules in this package rather than hardcoded in the TUI - see this
package's __init__.py for how the per-machine tables are aggregated.
"""

# Named Blickensderfer keyboard layouts, ported verbatim from
# v2/lib/layouts/blick_layouts.scad's DHIATENSOR/QWERTY/SCANDI/
# HEBREW_ENGL/CHARIENSTU_DE/CHARIENSTU_DE_MOD arrays. All share the same
# 3-row structure and the same physical placement_map/latitude_columns -
# only the glyph content per row differs, so switching presets only ever
# rewrites layout.rows. HEBREW_ENGL needs a Hebrew-capable font
# (font.path) to actually render correctly - v2 auto-switches Font_Hebrew
# when this layout is selected, v4 does not (no per-layout font-switching
# wired up), so you'll need to set font.path yourself too.
LAYOUT_PRESETS = {
    "DHIATENSOR": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    "QWERTY": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
        "\"#$%_/-¢@;23456789:!^1.&'(0)",
    ],
    "SCANDI": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:",
    ],
    "HEBREW_ENGL": [
        "זךכגװפףץצדהעאתןנםשרלסמיטבוקח",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    "CHARIENSTU_DE": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJU",
        "(%¨+-/'\"ö1234567890äü!;?=ß§)",
    ],
    "CHARIENSTU_DE_MOD": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJU",
        "(%*+-/'\"^1234567890`´!;?=@§)",
    ],
}
