"""
Selectric III 96-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S3-specific section (LOWERCASE96_US/
UPPERCASE96_US/S3_LC_HEMISPHERE96/S3_HEMISPHERE_MAP, ~lines 55-93).

The keyboard-order CHARACTER CONTENT (what v2 called LOWERCASE96_US/
UPPERCASE96_US) now lives in config/selectric3.yaml's layout.rows and
tune.py's LAYOUT_PRESETS_SELECTRIC3 (editable via the Layout tab), not
here - see lib/selectric3.py's configure(). v2's 5 physical print-lines
(13+12+11+10+2=48 characters) do NOT correspond to the ball's 4 physical
rows - that's a keyboard-typing-layout artifact only; the real row
assignment comes from S3_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
same formula as S12. layout.rows folds v2's trailing 2-char print-line
(the ²/§ / ³/¶ extras, on the ball but not reachable via the real
keyboard) into the 4th row rather than carrying a 5th row, so the Layout
tab's "8 rows, 4 lowercase + 4 uppercase" shape holds for every Selectric
machine - purely a display-grouping choice, the flat concatenated
character sequence (and therefore every S3_HEMISPHERE_MAP index) is
unchanged from v2's.

Physical layout: 4 rows x 12 hemisphere columns = 48 keyboard positions
per case; lowercase (case 0) and uppercase (case 1) sit on OPPOSITE
hemispheres, 180 degrees apart - see v2/ibm.scad:330-338,610-655. The
extra ²/§/³/¶ characters (on the physical ball but not reachable via the
real Selectric III keyboard, per the reference repo this was sourced
from) are included since they occupy real hemisphere positions.
"""

CHARS_PER_ROW = 24
HEMISPHERE_COLS_PER_ROW = 12
TOTAL_CHARS = 96

# v2/lib/layouts/ibm_layouts.scad:93 - precomputed keyboard-index ->
# hemisphere-index permutation (48 entries, one per keyboard-order
# position - see module docstring). Copied verbatim, not re-derived.
S3_HEMISPHERE_MAP = [
    35, 37, 4, 10, 7, 3, 6, 2, 8, 9, 5, 36, 23, 40, 26, 17, 29, 16, 42, 21,
    14, 28, 41, 34, 46, 31, 15, 27, 43, 45, 33, 39, 20, 44, 12, 13, 0, 32,
    18, 24, 19, 30, 25, 47, 38, 11, 1, 22,
]
assert len(S3_HEMISPHERE_MAP) == 48


def longitude_latitude(cases_lower):
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S3-specialized) - see
    lib/layouts/selectric12_layout.py's matching function docstring.

    cases_lower - the flat 48-char keyboard-order lowercase string
    (config-driven now, see module docstring), not a hardcoded
    constant."""
    assert len(cases_lower) == 48, (
        f"layout.rows' 4 lowercase rows must concatenate to exactly 48 "
        f"characters (S3_HEMISPHERE_MAP is a fixed 48-entry permutation "
        f"over this same sequence) - got {len(cases_lower)}")
    return [
        (S3_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         S3_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         cases_lower[i], i)
        for i in range(48)
    ]
