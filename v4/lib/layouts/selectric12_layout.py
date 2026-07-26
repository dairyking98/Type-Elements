"""
Selectric I/II 88-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S12-specific section (LOWERCASE88_US/
UPPERCASE88_US/S12_LC_HEMISPHERE88_US/S12_HEMISPHERE_MAP, ~lines 12-40 and
216-222).

The keyboard-order CHARACTER CONTENT (what v2 called LOWERCASE88_US/
UPPERCASE88_US) now lives in config/selectric12.yaml's layout.rows and
tune.py's LAYOUT_PRESETS_SELECTRIC12 (editable via the Layout tab), not
here - see lib/selectric12.py's configure(), which concatenates the 4
lowercase + 4 uppercase rows into the flat 44-character-per-case strings
this module's longitude_latitude() consumes. Only the physical/fixed
hemisphere permutation (never user-editable - see tune.py's
_compose_layout_tab comment on placement_map-style constants) stays here.

v2's own S12_HEMISPHERE_MAP is a PRECOMPUTED, hardcoded permutation table
(44 entries, the comment above it in v2 says so explicitly) - copied
verbatim below, not re-derived. It refers to positions in the same "real
characters only, keyboard reading order" sequence as LOWERCASE88_US/
UPPERCASE88_US (row 0 left-to-right, then row 1, etc.) for the original
v2 model to have produced a sane typeball layout at all.

Physical layout: 4 rows x 11 hemisphere columns = 44 keyboard positions
per case; lowercase (case 0) and uppercase (case 1) sit on OPPOSITE
hemispheres (180 degrees apart) - see v2/ibm.scad:330-338,610-655.
"""

CHARS_PER_ROW = 22
HEMISPHERE_COLS_PER_ROW = 11
TOTAL_CHARS = 88

# v2/lib/layouts/ibm_layouts.scad:222 - precomputed keyboard-index ->
# hemisphere-index permutation (44 entries, one per keyboard-order
# position - see module docstring). Copied verbatim, not re-derived.
S12_HEMISPHERE_MAP = [
    10, 4, 9, 6, 3, 2, 8, 7, 0, 1, 33, 37, 35, 22, 14, 30, 16, 34, 20, 24,
    28, 36, 27, 29, 23, 19, 42, 43, 12, 38, 13, 17, 41, 25, 5, 21, 18, 31,
    11, 15, 32, 40, 26, 39,
]
assert len(S12_HEMISPHERE_MAP) == 44


def longitude_latitude(cases_lower):
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S12-specialized): for each
    keyboard index i, [longitude_col, latitude_row, lowercase_char,
    keyboard_index]. longitude_col/latitude_row are derived from
    S12_HEMISPHERE_MAP[i] % / // HEMISPHERE_COLS_PER_ROW - the hemisphere
    permutation's own column/row within the 11-wide physical ring.

    cases_lower - the flat 44-char keyboard-order lowercase string
    (config-driven now, see module docstring), not a hardcoded
    constant."""
    assert len(cases_lower) == 44, (
        f"layout.rows' 4 lowercase rows must concatenate to exactly 44 "
        f"characters (S12_HEMISPHERE_MAP is a fixed 44-entry permutation "
        f"over this same sequence) - got {len(cases_lower)}")
    return [
        (S12_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         S12_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         cases_lower[i], i)
        for i in range(44)
    ]
