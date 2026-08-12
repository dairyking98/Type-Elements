"""
Selectric Composer 88-character keyboard/hemisphere layout data - ported
from v2/lib/layouts/ibm_layouts.scad's Composer-specific section
(LOWERCASECOMPOSER_US/UPPERCASECOMPOSER_US/C_US_HEMISPHERE88/
COMPOSER_HEMISPHERE_MAP, ~lines 97-231).

The keyboard-order CHARACTER CONTENT (what v2 called LOWERCASECOMPOSER_*/
UPPERCASECOMPOSER_*) now lives in config/selectric_composer.yaml's
layout.rows and this module's own LAYOUT_PRESETS_SELECTRIC_COMPOSER below
(editable via the Layout tab), not in the hemisphere data here - see
lib/selectric_composer.py's configure().
All 5 of v2's real language variants (US/UK/Nordic/German/Latin - ALL_C
in ibm_layouts.scad:100-197) are ported as named presets there now (v2's
Custom slot is the Layout tab's "Modify glyphs" switch instead). Per v2's
own comment ("I dont think hemisphere positions for keyboard to element
will change for different languages", same reasoning as
S12_US_HEMISPHERE88), COMPOSER_HEMISPHERE_MAP below was derived from the
US layout only and is reused unchanged across every language preset -
only which characters print at each fixed position changes.

Same "hemisphere permutation table copied verbatim" approach as
lib/layouts/selectric12_layout.py - see that module's docstring for why.
Composer shares the SAME physical ball/hemisphere geometry class as
Selectric I/II (88 chars, 4 rows x 11 hemisphere columns) - only the
keyboard layout and hemisphere mapping differ.
"""

CHARS_PER_ROW = 22
HEMISPHERE_COLS_PER_ROW = 11
TOTAL_CHARS = 88

# v2/lib/layouts/ibm_layouts.scad:231 - precomputed keyboard-index ->
# hemisphere-index permutation (44 entries, one per keyboard-order
# position - see module docstring). Copied verbatim, not re-derived.
COMPOSER_HEMISPHERE_MAP = [
    6, 9, 3, 4, 21, 2, 20, 10, 8, 7, 12, 33, 41, 31, 38, 28, 18, 37, 24, 16,
    29, 36, 11, 17, 5, 30, 39, 40, 26, 43, 32, 15, 34, 13, 35, 22, 14, 23,
    19, 27, 25, 1, 0, 42,
]
assert len(COMPOSER_HEMISPHERE_MAP) == 44


def longitude_latitude(cases_lower):
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, Composer-specialized) - see
    lib/layouts/selectric12_layout.py's matching function docstring.

    cases_lower - the flat 44-char keyboard-order lowercase string for
    whichever language preset is active (config-driven now, see module
    docstring), not a hardcoded constant."""
    assert len(cases_lower) == 44, (
        f"layout.rows' 4 lowercase rows must concatenate to exactly 44 "
        f"characters (COMPOSER_HEMISPHERE_MAP is a fixed 44-entry "
        f"permutation over this same sequence) - got {len(cases_lower)}")
    return [
        (COMPOSER_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         COMPOSER_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         cases_lower[i], i)
        for i in range(44)
    ]

# v2's ALL_C (ibm_layouts.scad:100-197) - all 5 real Composer language
# variants (v2's 6th ALL_C entry, Custom, is this machine's own Modify
# glyphs switch instead). All 5 share the identical row-length shape
# (12/11/11/10 per case) and the SAME fixed hemisphere permutation
# (COMPOSER_HEMISPHERE_MAP, derived from US only and reused across
# languages per v2's own comment - see lib/layouts/
# selectric_composer_layout.py) - only glyph content changes per preset.
LAYOUT_PRESETS_SELECTRIC_COMPOSER = {
    "United States": [
        "1234567890-=",
        "qwertyuiop?",
        "asdfghjkl][",
        "zxcvbnm,.;",
        "!†+$%/&*()–@",
        "QWERTYUIOP¾",
        "ASDFGHJKL¼½",
        "ZXCVBNM‘’:",
    ],
    "United Kingdom": [
        "1234567890-=",
        "qwertyuiop?",
        "asdfghjkl][",
        "zxcvbnm,.;",
        "!†+£%/&*()–@",
        "QWERTYUIOP¾",
        "ASDFGHJKL¼½",
        "ZXCVBNM‘’:",
    ],
    "Nordic": [
        "1234567890-ø",
        "qwertyuiopå",
        "asdfghjklöä",
        "zxcvbnm,.;",
        "»!?§%/&=()–Ø",
        "QWERTYUIOPÅ",
        "ASDFGHJKLÖÄ",
        "ZXCVBNM‘’:",
    ],
    "German": [
        "1234567890-ß",
        "qwertyuiopü",
        "asdfghjklöä",
        "zxcvbnm,.;",
        "!=+§%/&*()–?",
        "QWERTYUIOPÜ",
        "ASDFGHJKLÖÄ",
        "ZXCVBNM‘’:",
    ],
    "Latin": [
        "1234567890-ñ",
        "qwertyuiopˆ",
        "asdfghjkl´ç",
        "zxcvbnm,.;",
        "ı¿¡$!/&*()–Ñ",
        "QWERTYUIOP¨",
        "ASDFGHJKL`?",
        "ZXCVBNM‘’:",
    ],
}
