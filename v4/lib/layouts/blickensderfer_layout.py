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
    # NOTE both CHARIENSTU rows below end "WKJY", not "WKJU". v1
    # (v1/Blickensderfer/Blickensderfer2.scad:82,85,88) and v2
    # (v2/lib/layouts/blick_layouts.scad:18,21,24) both read "WKJU" for all
    # three CHARIENSTU variants - an error in the ORIGINAL source, not a v4
    # porting slip, and the same shape as the Hammond Ideal 'b'/'d' bug (see
    # hammond_layout.py). Two independent proofs: (1) mechanically, the
    # uppercase row's letter inventory came out as a-z with U DUPLICATED and
    # Y MISSING, while its own lowercase row is a clean a-z - no typewriter
    # omits Y; (2) the Blickensderfer type-wheel catalog scans (Bohemian
    # No. 426/443, "Catalog/20230113_0155.jpg") print "GMDB:WKJY" plainly at
    # 300%. DHIATENSOR was checked the same way and is clean in both rows.
    "CHARIENSTU_DE": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%¨+-/'\"ö1234567890äü!;?=ß§)",
    ],
    "CHARIENSTU_DE_MOD": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%*+-/'\"^1234567890`´!;?=@§)",
    ],
    # --- From the Blickensderfer type-wheel catalog scans (below) -------
    # Same DHIATENSOR letters, but the shifted row swaps two keys ("." key
    # shifts to & instead of "."; "," key shifts to ? instead of &) and the
    # figures row is entirely different, carrying ¼ ½ ¾ and £.
    # Shuttles: Elite Literary 381, Small Roman Literary 462, Extra Large
    # Roman Literary 307, Italic Literary 383, Script Literary 395,
    # Vertical Script Literary 213 - all six print identical rows, differing
    # only in typeface.
    "BRITISH_LITERARY": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/_¼!1234567890½+¾=£;*':",
    ],
    # QWERTY above is the American wheel; this is the British one, which
    # differs from it in EXACTLY one position - £ where American has $.
    # Shuttles: Small Roman 441, Large Roman 442.
    "QWERTY_BRITISH": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
        "\"#£%_/-¢@;23456789:!^1.&'(0)",
    ],
}

# Source for the two catalog-derived presets above, and the WKJY
# correction: 14 page scans of a Blickensderfer type-wheel catalog
# ("E:/Type Elements/Blickensderfer/Catalog/20230113_01{55..68}.jpg" on
# the Windows box), organised by language/market - ARMENIAN, BOHEMIAN,
# BRITISH (Imperial / Scientific / Literary / Universal), BRITISH-AMERICAN
# and more - each entry printed as "<Typeface> No. <n>. Code Word-<word>"
# followed by the same three 28-character rows this machine already uses.
# It confirms DHIATENSOR character for character.
#
# NOT imported, needing their own verification pass first (a wrong glyph
# silently builds a wrong wheel, same rule as the Hammond catalogs):
#   - Bohemian 426/443: CHARIENSTU letters with a Czech figures row whose
#     doubled dead-key accents (´ ´ and ˇ ˇ) can't be separated reliably
#     at this scan resolution.
#   - Armenian 218: full Armenian script, needs a font with those glyphs.
#   - The British Imperial/Scientific/Universal FRACTION variants (212,
#     E458, 331, 454, 300, 205, 350, 494, 379, 387, 371, 337, 217): each
#     packs a different dense fraction bank (⅛ ¼ ⅜ ½ ⅝ ¾ ⅞ in varying
#     slots) that needs per-entry checking rather than one shared reading.
#   - British Telegraph 376: a non-standard row shape, not the usual
#     three-row 28-column form.
#   - The remaining language sections on pages 0161-0168, not yet sampled.
