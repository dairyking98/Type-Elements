"""
Selectric III 96-character keyboard/hemisphere layout data - ported from
v2/lib/layouts/ibm_layouts.scad's S3-specific section (LOWERCASE96_US/
UPPERCASE96_US/S3_LC_HEMISPHERE96/S3_HEMISPHERE_MAP, ~lines 55-93).

Same "keyboard-order strings stripped of whitespace, hemisphere
permutation table copied verbatim" approach as
lib/layouts/selectric12_layout.py - see that module's docstring for why.
Note the 5 physical print-lines in the v2 source (13+12+11+10+2=48
characters) do NOT correspond to the ball's 4 physical rows - that's a
keyboard-typing-layout artifact only; the real row assignment comes from
S3_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW, same formula as S12.

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

# v2/lib/layouts/ibm_layouts.scad:56-62 (LOWERCASE96_US)
LOWERCASE96_US = "".join("""
±1234567890-=
qwertyuiop½]
asdfghjkl;'
zxcvbnm,./
²§
""".split("\n"))

# v2/lib/layouts/ibm_layouts.scad:65-71 (UPPERCASE96_US)
UPPERCASE96_US = "".join("""
°!@#$%¢&*()_+
QWERTYUIOP¼[
ASDFGHJKL:"
ZXCVBNM,.?
³¶
""".split("\n"))

assert len(LOWERCASE96_US) == TOTAL_CHARS // 2 == 48
assert len(UPPERCASE96_US) == 48

# v2/lib/layouts/ibm_layouts.scad:93 - precomputed keyboard-index ->
# hemisphere-index permutation (48 entries). Copied verbatim, not
# re-derived (see module docstring).
S3_HEMISPHERE_MAP = [
    35, 37, 4, 10, 7, 3, 6, 2, 8, 9, 5, 36, 23, 40, 26, 17, 29, 16, 42, 21,
    14, 28, 41, 34, 46, 31, 15, 27, 43, 45, 33, 39, 20, 44, 12, 13, 0, 32,
    18, 24, 19, 30, 25, 47, 38, 11, 1, 22,
]
assert len(S3_HEMISPHERE_MAP) == 48


def longitude_latitude():
    """v2's LONGITUDE_LATITUDE (ibm.scad:243, S3-specialized) - see
    lib/layouts/selectric12_layout.py's matching function docstring."""
    return [
        (S3_HEMISPHERE_MAP[i] % HEMISPHERE_COLS_PER_ROW,
         S3_HEMISPHERE_MAP[i] // HEMISPHERE_COLS_PER_ROW,
         LOWERCASE96_US[i], i)
        for i in range(48)
    ]
