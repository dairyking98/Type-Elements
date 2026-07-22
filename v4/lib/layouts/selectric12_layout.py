"""
Selectric I/II 88-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S12-specific section (LOWERCASE88_US/
UPPERCASE88_US/S12_LC_HEMISPHERE88_US/S12_HEMISPHERE_MAP, ~lines 12-40 and
216-222).

v2's layout strings are OpenSCAD multi-line string literals indexed
character-by-character including embedded newlines - CASES88[case][i] for
i in [0:43] only lines up with real keyboard characters if the reader
already knows OpenSCAD's exact string-literal newline semantics, which
isn't reproducible from the .scad source alone without a real OpenSCAD
interpreter to test against. Sidestepped here: v2's own
S12_HEMISPHERE_MAP is already a PRECOMPUTED, hardcoded permutation table
(44 entries, the comment above it in v2 says so explicitly) - copied
verbatim below, not re-derived. The keyboard-order strings are stripped
of all whitespace/newlines to a clean 44-character sequence (reading
order: row 0 left-to-right, then row 1, etc.) - self-consistent with
S12_HEMISPHERE_MAP's indices, which must refer to the same "real
characters only, in reading order" positions for the original v2 model
to have produced a sane typeball layout at all.

Physical layout: 4 rows x 11 hemisphere columns = 44 keyboard positions
per case; lowercase (case 0) and uppercase (case 1) sit on OPPOSITE
hemispheres (180 degrees apart) - see v2/ibm.scad:330-338,610-655.
"""

CHARS_PER_ROW = 22
HEMISPHERE_COLS_PER_ROW = 11
TOTAL_CHARS = 88

# v2/lib/layouts/ibm_layouts.scad:12-19 (LOWERCASE88_US), stripped of the
# leading/trailing/row-separating newlines that make the source read like
# a physical keyboard grid.
LOWERCASE88_US = "".join("""
1234567890-=
qwertyuiop½
asdfghjkl;'
zxcvbnm,./
""".split("\n"))

# v2/lib/layouts/ibm_layouts.scad:21-27 (UPPERCASE88_US)
UPPERCASE88_US = "".join("""
!@#$%¢&*()_+
QWERTYUIOP¼
ASDFGHJKL:"
ZXCVBNM,.?
""".split("\n"))

assert len(LOWERCASE88_US) == TOTAL_CHARS // 2 == 44
assert len(UPPERCASE88_US) == 44

# v2/lib/layouts/ibm_layouts.scad:222 - precomputed keyboard-index ->
# hemisphere-index permutation (44 entries, one per LOWERCASE88_US
# position). Copied verbatim, not re-derived (see module docstring).
S12_HEMISPHERE_MAP = [
    10, 4, 9, 6, 3, 2, 8, 7, 0, 1, 33, 37, 35, 22, 14, 30, 16, 34, 20, 24,
    28, 36, 27, 29, 23, 19, 42, 43, 12, 38, 13, 17, 41, 25, 5, 21, 18, 31,
    11, 15, 32, 40, 26, 39,
]
assert len(S12_HEMISPHERE_MAP) == 44


def longitude_latitude():
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S12-specialized): for each
    keyboard index i, [longitude_col, latitude_row, lowercase_char,
    keyboard_index]. longitude_col/latitude_row are derived from
    S12_HEMISPHERE_MAP[i] % / // HEMISPHERE_COLS_PER_ROW - the hemisphere
    permutation's own column/row within the 11-wide physical ring."""
    return [
        (S12_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         S12_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         LOWERCASE88_US[i], i)
        for i in range(44)
    ]
