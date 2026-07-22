"""
Selectric Composer 88-character keyboard/hemisphere layout data - ported
from v2/lib/layouts/ibm_layouts.scad's Composer-specific section
(LOWERCASECOMPOSER_US/UPPERCASECOMPOSER_US/C_US_HEMISPHERE88/
COMPOSER_HEMISPHERE_MAP, ~lines 97-231). US language only
(Composer_Language==0) - v2 also has UK/Nordic/German/Latin/Custom
variants (ALL_C in ibm_layouts.scad:197); not ported here, deferred the
same way lib/layouts/selectric12_layout.py defers S12_88_Language's
Custom variant.

Same "keyboard-order strings stripped of whitespace, hemisphere
permutation table copied verbatim" approach as
lib/layouts/selectric12_layout.py - see that module's docstring for why.
Composer shares the SAME physical ball/hemisphere geometry class as
Selectric I/II (88 chars, 4 rows x 11 hemisphere columns) - only the
keyboard layout and hemisphere mapping differ.
"""

CHARS_PER_ROW = 22
HEMISPHERE_COLS_PER_ROW = 11
TOTAL_CHARS = 88

# v2/lib/layouts/ibm_layouts.scad:100-105 (LOWERCASECOMPOSER_US)
LOWERCASECOMPOSER_US = "".join("""
1234567890-=
qwertyuiop?
asdfghjkl][
zxcvbnm,.;
""".split("\n"))

# v2/lib/layouts/ibm_layouts.scad:118-123 (UPPERCASECOMPOSER_US)
UPPERCASECOMPOSER_US = "".join("""
!†+$%/&*()–@
QWERTYUIOP¾
ASDFGHJKL¼½
ZXCVBNM‘’:
""".split("\n"))

assert len(LOWERCASECOMPOSER_US) == TOTAL_CHARS // 2 == 44
assert len(UPPERCASECOMPOSER_US) == 44

# v2/lib/layouts/ibm_layouts.scad:231 - precomputed keyboard-index ->
# hemisphere-index permutation (44 entries). Copied verbatim, not
# re-derived (see module docstring).
COMPOSER_HEMISPHERE_MAP = [
    6, 9, 3, 4, 21, 2, 20, 10, 8, 7, 12, 33, 41, 31, 38, 28, 18, 37, 24, 16,
    29, 36, 11, 17, 5, 30, 39, 40, 26, 43, 32, 15, 34, 13, 35, 22, 14, 23,
    19, 27, 25, 1, 0, 42,
]
assert len(COMPOSER_HEMISPHERE_MAP) == 44


def longitude_latitude():
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, Composer-specialized) - see
    lib/layouts/selectric12_layout.py's matching function docstring."""
    return [
        (COMPOSER_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         COMPOSER_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         LOWERCASECOMPOSER_US[i], i)
        for i in range(44)
    ]
