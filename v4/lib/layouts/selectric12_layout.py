"""
Selectric I/II 88-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S12-specific section (LOWERCASE88_US/
UPPERCASE88_US/S12_LC_HEMISPHERE88_US/S12_HEMISPHERE_MAP, ~lines 12-40 and
216-222).

The keyboard-order CHARACTER CONTENT (what v2 called LOWERCASE88_US/
UPPERCASE88_US) now lives in config/selectric12.yaml's layout.rows and
this module's own LAYOUT_PRESETS_SELECTRIC12 below (editable via the
Layout tab), not in the hemisphere data here - see lib/selectric12.py's
configure(), which concatenates the 4
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

# v4-only addition, not from v2 - S12_HEMISPHERE_MAP above is calibrated
# specifically for the US keyboard-order sequence (LOWERCASE88_US/
# UPPERCASE88_US's own real per-position key identity), NOT character-
# aware: index i just means "the i-th key reading a US keyboard
# left-to-right, top-to-bottom", so it only produces a correct typeball
# for a layout.rows whose i-th character is genuinely THAT SAME PHYSICAL
# US KEY, substituted in place. Confirmed by direct construction: the
# real Finnish/Swedish keyboard (tune.py's FINNISH_SWEDISH preset, see
# config/selectric12.yaml's layout.hemisphere_map) rearranges more than
# just character content relative to US - some physical keys' natural
# reading-order position genuinely differs (e.g. the row-0 case symbol
# key order), so feeding its OWN natural keyboard.rows content through
# S12_HEMISPHERE_MAP produces a WRONG typeball even though every
# character is present. Derived fresh (not v2 data - v2 never had a
# second S12 language) by inverting S12_HEMISPHERE_MAP against a real
# physical typeball reference, then round-tripped back to an exact match
# - see SESSION_LOG.md's 2026-08-06 chapter for the full derivation.
S12_HEMISPHERE_MAP_FINNISH_SWEDISH = [
    10, 4, 9, 6, 3, 2, 8, 7, 0, 1, 41, 27, 35, 22, 14, 30, 16, 34, 20, 24,
    28, 36, 33, 29, 23, 19, 42, 43, 12, 38, 13, 17, 26, 40, 5, 21, 18, 31,
    11, 15, 32, 39, 25, 37,
]
assert len(S12_HEMISPHERE_MAP_FINNISH_SWEDISH) == 44

# Named hemisphere maps, keyed by config/selectric12.yaml's
# layout.hemisphere_map value - see lib/selectric12.py's configure().
HEMISPHERE_MAPS = {
    "us": S12_HEMISPHERE_MAP,
    "finnish_swedish": S12_HEMISPHERE_MAP_FINNISH_SWEDISH,
}


def longitude_latitude(cases_lower, hemisphere_map=None):
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S12-specialized): for each
    keyboard index i, [longitude_col, latitude_row, lowercase_char,
    keyboard_index]. longitude_col/latitude_row are derived from
    hemisphere_map[i] % / // HEMISPHERE_COLS_PER_ROW - the hemisphere
    permutation's own column/row within the 11-wide physical ring.

    cases_lower - the flat 44-char keyboard-order lowercase string
    (config-driven now, see module docstring), not a hardcoded constant.
    hemisphere_map - which physical permutation to use (see HEMISPHERE_
    MAPS above) - None defaults to S12_HEMISPHERE_MAP (the real v2/US
    one), matching every caller before this parameter existed."""
    hemisphere_map = S12_HEMISPHERE_MAP if hemisphere_map is None else hemisphere_map
    assert len(cases_lower) == 44, (
        f"layout.rows' 4 lowercase rows must concatenate to exactly 44 "
        f"characters (the hemisphere map is a fixed 44-entry permutation "
        f"over this same sequence) - got {len(cases_lower)}")
    return [
        (hemisphere_map[i] % HEMISPHERE_COLS_PER_ROW,
         hemisphere_map[i] // HEMISPHERE_COLS_PER_ROW,
         cases_lower[i], i)
        for i in range(44)
    ]

# The 3 Selectric machines' layout.rows is 8 rows (4 lowercase then 4
# uppercase, keyboard reading order) instead of the cylinder family's
# 3-4 shift-row shape - see config/selectric12.yaml's layout.rows comment
# for why row boundaries here are cosmetic (only each case's flat
# concatenated length matters - lib/layouts/selectric*_layout.py's fixed
# hemisphere permutation indexes into that flat sequence, not these row
# boundaries). Ported directly from v2/lib/layouts/ibm_layouts.scad.
LAYOUT_PRESETS_SELECTRIC12 = {
    # v2 S12_88_Language==0 (LOWERCASE88_US/UPPERCASE88_US) - the only
    # real named language S12 has (S12_88_Language's other option is
    # Custom, i.e. this machine's own Modify glyphs switch).
    "UNITED_STATES": [
        "1234567890-=",
        "qwertyuiop½",
        "asdfghjkl;'",
        "zxcvbnm,./",
        "!@#$%¢&*()_+",
        "QWERTYUIOP¼",
        "ASDFGHJKL:\"",
        "ZXCVBNM,.?",
    ],
    # v4-only addition, not from v2 (v2's S12_88_Language only ever had
    # US/Custom - see UNITED_STATES's own comment). Real Finnish/Swedish
    # keyboard content, in genuine natural reading order (NOT pre-shuffled
    # to fake-fit S12_HEMISPHERE_MAP's US-specific position calibration -
    # an earlier attempt at that is exactly why this preset needs its own
    # hemisphere map at all: some of this layout's keys sit at a
    # genuinely different flat reading-order position than their US
    # equivalent, e.g. the row-0 symbol key ordering, so no amount of
    # character substitution alone reproduces the right typeball under
    # the US permutation). Requires config/selectric12.yaml's layout.
    # hemisphere_map: "finnish_swedish" (lib/layouts/selectric12_layout.
    # py's S12_HEMISPHERE_MAP_FINNISH_SWEDISH) - selecting this preset via
    # the Layout tab keeps that in sync automatically; hand-editing rows
    # via Modify glyphs starting from this preset must keep it set to
    # "finnish_swedish" too. Derived 2026-08-06 against a real physical
    # reference and round-tripped back to an exact match against it - see
    # SESSION_LOG.md's matching chapter for the full derivation, not
    # hand-arranged by eye.
    "FINNISH_SWEDISH": [
        "1234567890´ü",
        "qwertyuiop-",
        "asdfghjkl.,",
        "zxcvbnmåäö",
        "'+§=%?&()/`£",
        "QWERTYUIOP_",
        "ASDFGHJKL:\"",
        "ZXCVBNMÅÄÖ",
    ],
}


# Which hemisphere map each named layout preset above is built for.
#
# This is deliberately a many-to-one LAYOUT -> MAP-KEY pairing, not a map
# per layout: a hemisphere map is a physical key-position permutation
# (keyboard reading order -> typeball slot), so different layouts that
# share the same physical key arrangement legitimately share one map, and
# the maps themselves stay defined once in HEMISPHERE_MAPS above.
#
# The asserts below are the point of keeping this next to the presets. A
# preset missing from here does NOT fall back to a default - tune.py's
# _save_to_yaml only patches layout.hemisphere_map when this lookup hits,
# so the config silently keeps whatever the PREVIOUS preset wrote. Since
# these maps are position-only and not character-aware, a map mismatched
# to a layout yields a WRONG typeball with every character still present
# (see this module's docstring) - a silent bad-geometry failure. Failing
# at import instead makes adding a layout without pairing it impossible
# to miss.
PRESET_HEMISPHERE_MAP = {
    "UNITED_STATES": "us",
    "FINNISH_SWEDISH": "finnish_swedish",
}
assert set(PRESET_HEMISPHERE_MAP) == set(LAYOUT_PRESETS_SELECTRIC12), (
    "every LAYOUT_PRESETS_SELECTRIC12 layout preset must name its hemisphere map: "
    f"unpaired={sorted(set(LAYOUT_PRESETS_SELECTRIC12) - set(PRESET_HEMISPHERE_MAP))}")
assert set(PRESET_HEMISPHERE_MAP.values()) <= set(HEMISPHERE_MAPS), (
    "unknown hemisphere map key: "
    f"{sorted(set(PRESET_HEMISPHERE_MAP.values()) - set(HEMISPHERE_MAPS))}")
