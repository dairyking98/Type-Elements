"""
Keyboard/typeball layout data for every machine, one module per machine.

This package is the ONLY home for layout presets - tune.py imports them
from here and hardcodes none of its own. Adding a machine means adding a
<machine>_layout.py here and one entry per table below, not editing the
TUI.

The per-machine modules hold the presets themselves; the BY_MACHINE
tables below are the machine-name -> data indexes tune.py looks up, and
LAYOUT_PICKER_HELP is the Layout tab's per-machine banner prose (kept
with the data it describes, per CLAUDE.md's "one dict entry, not an
if/elif chain" rule).
"""

# RELATIVE imports are required here, not absolute "from lib.layouts...".
# This package is reachable under TWO names: tune.py/font_coverage.py reach
# it as "lib.layouts" (repo root on sys.path), while the machine modules
# reach it as plain "layouts" (lib/ itself is on sys.path - see
# lib/selectric12.py's "from layouts.selectric12_layout import ..."). An
# absolute import here only resolves under the first of those, and would
# also let the package load twice as two distinct module objects.
from .bennett_layout import LAYOUT_PRESETS_BENNETT
from .blickensderfer_layout import LAYOUT_PRESETS
from .hammond_layout import (
    CATALOG_IDEAL_BOHEMIAN,
    CATALOG_IDEAL_CROATIAN,
    CATALOG_IDEAL_DANISH_FRACTIONS,
    CATALOG_IDEAL_DUTCH,
    CATALOG_IDEAL_FRENCH,
    CATALOG_IDEAL_GERMAN,
    CATALOG_IDEAL_GERMAN_NEW_ORTHOGRAPHY,
    CATALOG_UNIVERSAL_ESPERANTO,
    CATALOG_UNIVERSAL_ITALIAN,
    CATALOG_UNIVERSAL_PORTUGUESE,
    CATALOG_UNIVERSAL_ROUMANIAN,
    CATALOG_UNIVERSAL_DANISH_NORWEGIAN,
    CATALOG_UNIVERSAL_SPANISH,
    CATALOG_UNIVERSAL_SWEDISH_FINNISH,
    CATALOG_UNIVERSAL_FRENCH,
    CATALOG_UNIVERSAL_FRENCH_GERMAN_ENGLISH,
    CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY,
    CATALOG_IDEAL_PORTUGUESE,
    CATALOG_IDEAL_ROUMANIAN,
    CATALOG_IDEAL_FRACTIONS,
    CATALOG_IDEAL_SPANISH,
    CATALOG_IDEAL_SPANISH_CAPS,
    CATALOG_IDEAL_SPANISH_CENT,
    CATALOG_IDEAL_STANDARD,
    CATALOG_SHUTTLES,
    CATALOG_UNIVERSAL_CAPS_SMALL_CAPS,
    CATALOG_UNIVERSAL_FRACTIONS,
    CATALOG_UNIVERSAL_STANDARD,
    LAYOUT_PRESETS_HAMMOND,
)
from .hammond_split_layout import LAYOUT_PRESETS_HAMMOND_SPLIT
from .helios_layout import LAYOUT_PRESETS_HELIOS
from .mignon_layout import LAYOUT_PRESETS_MIGNON
from .postal_layout import LAYOUT_PRESETS_POSTAL
from .selectric12_layout import (
    LAYOUT_PRESETS_SELECTRIC12,
    PRESET_HEMISPHERE_MAP as _s12_pairs,
)
from .selectric3_layout import (
    LAYOUT_PRESETS_SELECTRIC3,
    PRESET_HEMISPHERE_MAP as _s3_pairs,
)
from .selectric_composer_layout import (
    LAYOUT_PRESETS_SELECTRIC_COMPOSER,
)

LAYOUT_PRESETS_BY_MACHINE = {
    "blickensderfer": LAYOUT_PRESETS,
    "postal": LAYOUT_PRESETS_POSTAL,
    "mignon": LAYOUT_PRESETS_MIGNON,
    "bennett": LAYOUT_PRESETS_BENNETT,
    "helios": LAYOUT_PRESETS_HELIOS,
    "hammond": LAYOUT_PRESETS_HAMMOND,
    "hammond_split": LAYOUT_PRESETS_HAMMOND_SPLIT,
    "selectric12": LAYOUT_PRESETS_SELECTRIC12,
    "selectric3": LAYOUT_PRESETS_SELECTRIC3,
    "selectric_composer": LAYOUT_PRESETS_SELECTRIC_COMPOSER,
}
# layout.baseline_row/cutout_row that go WITH each of the row-count-
# varying presets above - only Hammond needs this (every other machine's
# presets keep the machine's one fixed row count). Applied in
# _save_to_yaml alongside patch_yaml_rows, since the generic per-row
# Input widgets (BASELINE_CUTOUT_KEYS) are sized for whatever row count
# was on disk at compose() time and can't grow/shrink themselves mid-
# session - see SESSION_LOG.md's Hammond chapter.
LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE = {
    "hammond": {
        "Universal": [3.74, -1.21, -5.71],
        "Universal, Math": [3.74, -1.21, -5.71, -9.89],
        # Ideal is an ordinary 3-row (non-Math) shuttle, so it takes the
        # same baselines as Universal - listed explicitly rather
        # than left to fall through, so switching Universal, Math -> Ideal
        # resizes baseline_row/cutout_row back down to 3 entries.
        "Ideal": [3.74, -1.21, -5.71],
        "Ideal, Fractions": [3.74, -1.21, -5.71],
        "Universal, Fractions": [3.74, -1.21, -5.71],
        "Universal, Caps and Small Caps": [3.74, -1.21, -5.71],
        "Ideal, Dutch": [3.74, -1.21, -5.71],
        "Ideal, Spanish": [3.74, -1.21, -5.71],
        "Ideal, Spanish (¢)": [3.74, -1.21, -5.71],
        "Ideal, Spanish (Caps and Small Caps)": [3.74, -1.21, -5.71],
        "Ideal, Croatian": [3.74, -1.21, -5.71],
        "Ideal, Danish (Fractions)": [3.74, -1.21, -5.71],
        "Ideal, Portuguese": [3.74, -1.21, -5.71],
        "Ideal, French": [3.74, -1.21, -5.71],
        "Ideal, German (New Orthography)": [3.74, -1.21, -5.71],
        "Ideal, German": [3.74, -1.21, -5.71],
        "Universal, German (New Orthography)": [3.74, -1.21, -5.71],
        "Universal, French": [3.74, -1.21, -5.71],
        "Universal, French-German-English": [3.74, -1.21, -5.71],
        "Universal, Esperanto": [3.74, -1.21, -5.71],
        "Universal, Italian": [3.74, -1.21, -5.71],
        "Universal, Portuguese": [3.74, -1.21, -5.71],
        "Universal, Roumanian": [3.74, -1.21, -5.71],
        "Ideal, Roumanian": [3.74, -1.21, -5.71],
        "Universal, Spanish": [3.74, -1.21, -5.71],
        "Universal, Swedish-Finnish": [3.74, -1.21, -5.71],
        "Universal, Danish-Norwegian": [3.74, -1.21, -5.71],
        "Ideal, Bohemian": [3.74, -1.21, -5.71],
    },
}
# v4-only, not a v1/v2 concept - which named layout.rows preset requires
# which layout.hemisphere_map value (see lib/layouts/selectric12_layout.
# py's/selectric3_layout.py's HEMISPHERE_MAPS). Read by _save_to_yaml
# whenever the Layout tab's preset dropdown (not Modify glyphs' custom
# rows) is what's being saved, so picking a named preset there keeps
# layout.hemisphere_map correct automatically.
#
# DERIVED from each machine module's own PRESET_HEMISPHERE_MAP, never
# hand-written here - the pairing belongs next to the presets it pairs,
# where that module's asserts can catch a layout that was added without
# naming a map. Duplicating it here is what would let the two drift.
#
# A machine absent from this index (Composer, and every non-Selectric
# machine) leaves the config's existing hemisphere_map untouched. That is
# deliberate rather than an omission for Composer specifically: it has a
# single fixed COMPOSER_HEMISPHERE_MAP shared by all 5 of its language
# presets, no HEMISPHERE_MAPS table to choose from, and no
# layout.hemisphere_map key in config/selectric_composer.yaml at all, so
# there is nothing for a pairing to select - writing one would emit a key
# lib/selectric_composer.py does not read.
LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE = {
    "selectric12": dict(_s12_pairs),
    "selectric3": dict(_s3_pairs),
}
# Layout tab's picker-help banner, one flowing string per machine (see
# CLAUDE.md's tooltip/help-text rules - no manual \n; add the next
# machine's entry here instead of an if/elif in _compose_layout_tab).
LAYOUT_PICKER_HELP = {
    "blickensderfer": (
        "All layouts share the same physical placement_map - only glyph "
        "content per row changes. HEBREW_ENGL needs a Hebrew-capable font "
        "path; v4 doesn't auto-switch fonts per layout like v2 did. "
        "BRITISH_LITERARY and QWERTY_BRITISH come from the Blickensderfer "
        "type-wheel catalog scans - QWERTY_BRITISH differs from QWERTY in "
        "exactly one position, £ where the American wheel has $."
    ),
    "postal": (
        "Postal has only one physical layout, QWERTY. Use Modify glyphs "
        "below to hand-edit the rows for anything else."
    ),
    "mignon": (
        "30 named layouts, all sharing the same 7-row/12-column physical "
        "layout - only glyph content changes per row. Rows are shown in "
        "keyboard-legend order; char_legend remaps this to build order "
        "internally."
    ),
    "bennett": (
        "Ported from v2/lib/layouts/bennett_layouts.scad's ENGLISH/BRITISH/"
        "INTERNATIONAL plus v2/bennett.scad's own CUSTOM (identical to "
        "ENGLISH by default - edit it via Modify glyphs below). All share "
        "the same 3-row/28-column layout. Rows are shown in keyboard-legend "
        "order (as printed on the physical keyboard/manual) - "
        "layout.char_legend remaps this to build order internally."
    ),
    "helios": (
        "GERMAN_MOD is v2's real default/only-used layout; GERMAN is a "
        "second array present in the source but superseded there. Both "
        "share the same 4-row/21-column physical layout, identity "
        "placement_map."
    ),
    "hammond": (
        "Universal is qwerty; Ideal is Hammond's own proprietary key "
        "arrangement, not a qwerty remap. Universal, Math has 4 rows instead "
        "of 3 - selecting it switches Shuttle_Height and the resin-support "
        "layout automatically (Is_Math derives from the row count) and "
        "resizes baseline_row/cutout_row to match. The rest come from "
        "Hammond's own 1920 and 1915 type-shuttle catalogs; most catalogued "
        "shuttles differ only in TYPEFACE, which is the Font tab's job, not "
        "a layout change - Caps and Small Caps deliberately has the same "
        "rows as Universal for that reason, so pair it with a "
        "small-caps font."
    ),
    "hammond_split": (
        "IDEAL is Hammond's proprietary key arrangement; UNIVERSAL is "
        "qwerty. Ideal (£) is the shipped default and Ideal (⅌) swaps the "
        "per-unit sign at that one figures-row position - both are real "
        "source-history values (SESSION_LOG.md part 77), and Char_Mod (Font "
        "& Alignment tab) only has an effect under Ideal (⅌). The rest come "
        "from Hammond's own 1920 and 1915 catalogs; the per-language entries "
        "keep the Ideal key order and substitute that language's "
        "characters. Caps and Small Caps is a typeface, not a layout - "
        "pair it with a small-caps font."
    ),
    "selectric12": (
        "8 rows: the first 4 are lowercase, the last 4 are uppercase/"
        "shifted, each in real keyboard reading order. Row boundaries are "
        "just for readability - the ball's fixed hemisphere map is keyed "
        "by each case's flat character count, so Modify glyphs can swap "
        "which character sits at a position but can't change any row's "
        "length. United States is v2's only real layout for this machine."
    ),
    "selectric3": (
        "8 rows: the first 4 are lowercase, the last 4 are uppercase/"
        "shifted. Row 4 of each case includes 2 extra ball-only "
        "characters (not reachable via the real Selectric III keyboard) "
        "folded in from v2's own 5th print-line. Like Selectric I/II, row "
        "lengths are fixed by the ball's hemisphere map - Modify glyphs "
        "can only swap which character sits at a position. Selectric III "
        "has no second real language variant in v2."
    ),
    "selectric_composer": (
        "8 rows: the first 4 are lowercase, the last 4 are uppercase/"
        "shifted. All 5 presets share the same hemisphere map (derived "
        "from United States only, per v2's own comment) and row-length "
        "shape - only glyph content differs. Modify glyphs can swap which "
        "character sits at a position but can't change any row's length."
    ),
}
