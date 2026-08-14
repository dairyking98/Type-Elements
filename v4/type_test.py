#!/usr/bin/env python3
"""
Builds a flat, CPI-spaced test block for quick font/legibility testing -
matches v2/blickensderfer.scad's TypeTest() spacing convention: each
character gets a FIXED-width slot of 25.4/cpi mm (typewriter fixed-pitch,
not proportional spacing). Within its slot, each character is positioned
via the same alignment_x_offset() convention the real element uses
(config's alignment.* - mode center/left, modified_left/right_chars
nudges), so Type Test matches the real struck-character placement, not
just a generic centered preview. Text may contain embedded newlines for
multiple stacked lines, spaced 25.4/lpi mm apart (same fixed-pitch
convention, vertically - default 6 lines per inch). Independent of the
real cylindrical element pipeline otherwise (no draft, no platen
scallop, no placement-on-cylinder) - just flat extruded outlines, for
speed.

Usage:
    python3 type_test.py "line one\nline two" --cpi 10 --lpi 6 --font-path /path/to/font.ttf --font-size-mm 3.7 --out output/blickensderfer_running.stl
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from glyph_poc import build_flat_text, ALIGN_MODE, ALIGN_CENTER_OFFSET_MM, ALIGN_LEFT_OFFSET_MM, \
    ALIGN_MODIFIED_LEFT_CHARS, ALIGN_MODIFIED_LEFT_OFFSET_MM, ALIGN_MODIFIED_RIGHT_CHARS, \
    ALIGN_MODIFIED_RIGHT_OFFSET_MM, ALIGN_CARET_DROP_MM, \
    ALIGN_UNDERSCORE_LIFT_MM  # noqa: E402
import build_log  # noqa: E402 - needs the lib/ sys.path.insert above first
import scad_primitives as sp  # noqa: E402


def _composer_unit_width(ch, pitch_list, default_units):
    """v2's SearchChar()/Composer_Pitch_List: FIRST match wins (OpenSCAD's
    search() semantics) - pitch_list is an ordered [char, units] list, not
    a dict, because a couple of real characters (u+umlaut/o+umlaut) appear
    twice in v2's own table with different unit values at each occurrence -
    see config/selectric_composer.yaml's type_test.pitch_list comment."""
    for c, units in pitch_list:
        if c == ch:
            return units
    return default_units


def build_type_test_line(text, cpi, font_path, font_size_mm, flatness_tolerance_mm=0.005, depth=0.4,
                          lpi=6.0, align_kwargs=None, mod_chars="", mod_font_path=None, mod_font_size_mm=None,
                          composer_pitch_list=None, composer_units_per_inch=None, composer_default_units=9):
    """mod_chars/mod_font_path/mod_font_size_mm: Hammond Split's Char_Mod
    convention (config char_mod.char/char_mod_font_path/char_mod_size_mm) -
    characters in mod_chars use mod_font_path/mod_font_size_mm instead of
    font_path/font_size_mm, same is_mod check as lib/hammond_split.py's
    TextAssemble(). Optional/no-op for every other machine (mod_chars
    defaults to "", so is_mod is never true).

    composer_pitch_list/composer_units_per_inch/composer_default_units:
    Selectric Composer's real proportional-spacing convention (v2/
    ibm.scad's Composer_Pitch_List/cumulativeSum/TextGaugeComposerLine2) -
    each character gets its own width in UNITS (composer_pitch_list, see
    _composer_unit_width()'s docstring for why it's an ordered list, not
    a dict), converted to mm via 25.4/composer_units_per_inch, replacing
    the fixed slot_mm/cpi spacing below entirely for that line.
    composer_default_units is v2's own fallback (9, the widest bucket)
    for a character with no pitch_list entry. composer_pitch_list=None
    (the default) keeps the original fixed-CPI behavior - a no-op for
    every machine except Selectric Composer.

    UNLIKE the fixed-CPI path below (which always anchors every glyph at
    its slot's CENTER regardless of align_kwargs' mode, matching the real
    struck element's own fixed-slot convention), the proportional path's
    anchor point itself depends on mode, since unit widths vary per
    character: mode="left" anchors each glyph at the LEFT edge of its own
    unit span (glyph's raw, unshifted pen origin then flows rightward
    from there with zero further shift - align_kwargs' own mode="left"
    branch already applies no shift - reproducing v2's real
    halign="left" flush-left flow, where each character starts exactly
    where the previous one's units ended, no gaps); mode="center" anchors
    each glyph at the CENTER of its own unit span (align_kwargs' own
    mode="center" branch centers the glyph's advance box there). Picking
    the wrong anchor for a given mode would either double up the
    centering (center-anchor + a redundant -advance/2 shift) or leave
    "left" mode's glyphs starting mid-span with a gap before them
    (center-anchor + zero shift) - this is Composer-only; the fixed-CPI
    path's fixed always-center-anchor is unaffected and correct as-is
    (see the exchange in SESSION_LOG.md's part 78 continuation).

    NOT ported here: v2's KBSTRING default test content (the full
    88-char keyboard string, auto-wrapped into 8 rows via hardcoded
    GetRow() breakpoints) or the CUSTOM_TEST_STRING toggle - the caller's
    own free-typed (optionally multi-line, via literal \\n) text is used
    exactly like every other machine's Type Test, just with proportional
    instead of fixed-pitch spacing. Composer's real line spacing (v2:
    Font_Size_Selected*2*row, tied to KBSTRING's fixed-row layout) is
    likewise NOT reproduced - lpi below still governs line spacing here,
    same as every other machine."""
    line_spacing_mm = 25.4 / lpi  # same fixed-pitch convention as cpi, just vertical
    slot_mm = 25.4 / cpi
    proportional = composer_pitch_list is not None
    unit_dist_mm = 25.4 / composer_units_per_inch if proportional else None
    parts = []
    for j, line in enumerate(text.split("\n")):
        n = len(line)
        y = -j * line_spacing_mm
        if proportional:
            widths = [_composer_unit_width(ch, composer_pitch_list, composer_default_units) for ch in line]
            starts = []
            cum = 0.0
            for w in widths:
                starts.append(cum)
                cum += w
            total_units = cum
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            is_mod = bool(mod_chars) and ch in mod_chars and mod_font_path and mod_font_size_mm
            ch_font_path = mod_font_path if is_mod else font_path
            ch_font_size_mm = mod_font_size_mm if is_mod else font_size_mm
            mesh = build_flat_text(ch, flatness_tolerance_mm, depth, font_size_mm=ch_font_size_mm, font_path=ch_font_path,
                                    align_kwargs=align_kwargs)
            if proportional:
                mode = (align_kwargs or {}).get("mode", "center")
                if mode == "left":
                    # left edge of this char's own unit span - align_kwargs'
                    # own mode="left" branch applies zero shift, so the
                    # glyph's raw pen origin lands exactly here and flows
                    # rightward with no gap before the next character.
                    x = (starts[i] - total_units / 2.0) * unit_dist_mm
                else:
                    # center of this char's own unit span - align_kwargs'
                    # own mode="center" branch centers the glyph's advance
                    # box on top of this anchor.
                    x = (starts[i] + widths[i] / 2.0 - total_units / 2.0) * unit_dist_mm
            else:
                x = (i - (n - 1) / 2.0) * slot_mm
            mesh.apply_translation([x, y, 0])
            parts.append(mesh)
    if not parts:
        raise ValueError("nothing to render - text was empty or all spaces/blank lines")
    return sp.union_all(parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--cpi", type=float, default=10.0, help="characters per inch (v2's Test_CPI, default 10)")
    parser.add_argument("--lpi", type=float, default=6.0, help="lines per inch, for multi-line text (default 6)")
    parser.add_argument("--font-path", required=True)
    parser.add_argument("--font-size-mm", type=float, required=True)
    parser.add_argument("--flatness-tolerance-mm", type=float, default=0.005)
    parser.add_argument("--align-mode", default=ALIGN_MODE, help='"center" or "left" (default: %(default)s)')
    parser.add_argument("--center-offset-mm", type=float, default=ALIGN_CENTER_OFFSET_MM)
    parser.add_argument("--left-offset-mm", type=float, default=ALIGN_LEFT_OFFSET_MM)
    parser.add_argument("--modified-left-chars", default=ALIGN_MODIFIED_LEFT_CHARS)
    parser.add_argument("--modified-left-offset-mm", type=float, default=ALIGN_MODIFIED_LEFT_OFFSET_MM)
    parser.add_argument("--modified-right-chars", default=ALIGN_MODIFIED_RIGHT_CHARS)
    parser.add_argument("--modified-right-offset-mm", type=float, default=ALIGN_MODIFIED_RIGHT_OFFSET_MM)
    parser.add_argument("--caret-drop-mm", type=float, default=ALIGN_CARET_DROP_MM)
    parser.add_argument("--underscore-lift-mm", type=float, default=ALIGN_UNDERSCORE_LIFT_MM)
    parser.add_argument("--mod-chars", default="",
                         help="Characters using --mod-font-path/--mod-font-size-mm instead of the base font "
                              "(Hammond Split's Char_Mod convention - no-op for other machines).")
    parser.add_argument("--mod-font-path", default=None)
    parser.add_argument("--mod-font-size-mm", type=float, default=None)
    parser.add_argument("--composer-config", default=None,
                         help="Path to a YAML config with a type_test.pitch_list/units_per_inch/default_units "
                              "section (Selectric Composer's real proportional-spacing convention, config/"
                              "selectric_composer.yaml). Replaces --cpi's fixed slot spacing entirely when given - "
                              "no-op for other machines.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    align_kwargs = dict(
        mode=args.align_mode,
        center_offset_mm=args.center_offset_mm,
        left_offset_mm=args.left_offset_mm,
        modified_left_chars=args.modified_left_chars,
        modified_left_offset_mm=args.modified_left_offset_mm,
        modified_right_chars=args.modified_right_chars,
        modified_right_offset_mm=args.modified_right_offset_mm,
        caret_drop_mm=args.caret_drop_mm,
        underscore_lift_mm=args.underscore_lift_mm,
    )
    composer_pitch_list = composer_units_per_inch = None
    composer_default_units = 9
    if args.composer_config:
        import yaml
        with open(args.composer_config, encoding="utf-8") as f:
            composer_cfg = yaml.safe_load(f)
        tt_cfg = composer_cfg["type_test"]
        composer_pitch_list = [tuple(pair) for pair in tt_cfg["pitch_list"]]
        composer_units_per_inch = tt_cfg["units_per_inch"]
        composer_default_units = tt_cfg.get("default_units", 9)
    mesh = build_type_test_line(args.text, args.cpi, args.font_path, args.font_size_mm, args.flatness_tolerance_mm,
                                 lpi=args.lpi, align_kwargs=align_kwargs, mod_chars=args.mod_chars,
                                 mod_font_path=args.mod_font_path, mod_font_size_mm=args.mod_font_size_mm,
                                 composer_pitch_list=composer_pitch_list,
                                 composer_units_per_inch=composer_units_per_inch,
                                 composer_default_units=composer_default_units)
    build_log.mesh_report(mesh, "TypeTest")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    build_log.atomic_export(mesh, args.out)
    print(f"wrote {args.out}", flush=True)
