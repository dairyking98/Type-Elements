"""
Selectric III 96-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S3-specific section (LOWERCASE96_US/
UPPERCASE96_US/S3_LC_HEMISPHERE96/S3_HEMISPHERE_MAP, ~lines 55-93).

The keyboard-order CHARACTER CONTENT (what v2 called LOWERCASE96_US/
UPPERCASE96_US) now lives in config/selectric3.yaml's layout.rows and
this module's own LAYOUT_PRESETS_SELECTRIC3 below (editable via the
Layout tab), not in the hemisphere data here - see lib/selectric3.py's
configure(). v2's 5 physical print-lines
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

# v4-only addition, not from v2 ("Selectric III has no language-variant
# preset in v2" per ibm_layouts.scad:203) - same reasoning as
# lib/layouts/selectric12_layout.py's S12_HEMISPHERE_MAP_FINNISH_SWEDISH:
# S3_HEMISPHERE_MAP above is a fixed, position-only permutation
# calibrated against the US keyboard's exact key ordering, so it only
# produces a correct typeball if layout.rows' i-th character is genuinely
# the same physical key the US layout had at that position. The real
# Finnish/Swedish Selectric III keyboard doesn't just substitute
# characters into the US positions - it's a real ISO layout (has the
# extra key left of Z that ANSI/US lacks, so its own row boundaries are
# 13/12/12/11 instead of US's 13/12/11/12) - so it needs its own
# permutation. Derived 2026-08-10 directly from a real physical
# ball-layout reference (not inverted through S3_HEMISPHERE_MAP the way
# S12's first attempt was) - each of the reference's 4 physical rows
# (12 lowercase + 12 uppercase chars, reading column 0..11) was matched
# by character identity against this layout's own natural keyboard rows
# (tune.py's FINNISH_SWEDISH preset below) to build the permutation,
# then round-tripped: replaying the derived permutation against the
# natural rows reproduces all 4 physical reference rows byte-for-byte
# (both cases), confirming it's a real bijection over 0..47, not a
# hand-arranged guess. Cross-checked against the reference's own "del
# triangle points at the digit 0" fact - keyboard index 10 ('0', shared
# with the US layout since both put a single symbol key before "1234567890")
# maps to physical slot 5 (row 0, column 5) here, matching
# S3_HEMISPHERE_MAP[10]==5 for the US table - i.e. both languages'
# alignment triangles reference the same real physical column.
S3_HEMISPHERE_MAP_FINNISH_SWEDISH = [
    1, 37, 4, 10, 7, 3, 6, 2, 8, 9, 5, 11, 12, 40, 26, 17, 29, 16, 42, 21,
    14, 28, 41, 23, 22, 31, 15, 27, 43, 45, 33, 39, 20, 44, 35, 34, 13, 46,
    0, 32, 18, 24, 19, 30, 25, 47, 38, 36,
]
assert len(S3_HEMISPHERE_MAP_FINNISH_SWEDISH) == 48

# Named hemisphere maps, keyed by config/selectric3.yaml's
# layout.hemisphere_map value - see lib/selectric3.py's configure().
HEMISPHERE_MAPS = {
    "us": S3_HEMISPHERE_MAP,
    "finnish_swedish": S3_HEMISPHERE_MAP_FINNISH_SWEDISH,
}


def longitude_latitude(cases_lower, hemisphere_map=None):
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S3-specialized) - see
    lib/layouts/selectric12_layout.py's matching function docstring.

    cases_lower - the flat 48-char keyboard-order lowercase string
    (config-driven now, see module docstring), not a hardcoded
    constant.
    hemisphere_map - which physical permutation to use (see HEMISPHERE_
    MAPS above) - None defaults to S3_HEMISPHERE_MAP (the real v2/US
    one), matching every caller before this parameter existed."""
    hemisphere_map = S3_HEMISPHERE_MAP if hemisphere_map is None else hemisphere_map
    assert len(cases_lower) == 48, (
        f"layout.rows' 4 lowercase rows must concatenate to exactly 48 "
        f"characters (the hemisphere map is a fixed 48-entry permutation "
        f"over this same sequence) - got {len(cases_lower)}")
    return [
        (hemisphere_map[i] % HEMISPHERE_COLS_PER_ROW,
         hemisphere_map[i] // HEMISPHERE_COLS_PER_ROW,
         cases_lower[i], i)
        for i in range(48)
    ]

LAYOUT_PRESETS_SELECTRIC3 = {
    # v2 has no language-variant preset for Selectric III at all
    # ("Selectric III has no custom-language variant yet",
    # ibm_layouts.scad:203) - LOWERCASE96_US/UPPERCASE96_US is the only
    # real layout.
    "UNITED_STATES": [
        "±1234567890-=",
        "qwertyuiop½]",
        "asdfghjkl;'",
        "zxcvbnm,./²§",
        "°!@#$%¢&*()_+",
        "QWERTYUIOP¼[",
        "ASDFGHJKL:\"",
        "ZXCVBNM,.?³¶",
    ],
    # v4-only addition, not from v2 (v2's Selectric III has no language
    # variant at all - see UNITED_STATES's own comment). Real Finnish/
    # Swedish Selectric III keyboard content, in genuine natural reading
    # order - it's a real ISO keyboard (has the extra key left of Z that
    # US/ANSI lacks), so its own row lengths are 13/12/12/11, not US's
    # 13/12/11/12. Requires config/selectric3.yaml's layout.
    # hemisphere_map: "finnish_swedish" (lib/layouts/selectric3_layout.
    # py's S3_HEMISPHERE_MAP_FINNISH_SWEDISH) - selecting this preset via
    # the Layout tab keeps that in sync automatically (see
    # LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE); hand-editing rows via
    # Modify glyphs starting from this preset must keep it set to
    # "finnish_swedish" too. Derived 2026-08-10 against a real physical
    # reference and round-tripped back to an exact match against it (see
    # lib/layouts/selectric3_layout.py's own derivation comment) - not
    # hand-arranged by eye.
    "FINNISH_SWEDISH": [
        "½1234567890+´",
        "qwertyuiopå¨",
        "asdfghjklöä'",
        "<zxcvbnm,.-",
        "§!\"£$%&/()=?`",
        "QWERTYUIOPÅ^",
        "ASDFGHJKLÖÄ*",
        ">ZXCVBNM;:_",
    ],
}
