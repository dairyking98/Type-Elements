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
    python3 type_test.py "line one\nline two" --cpi 10 --lpi 6 --font-path /path/to/font.ttf --font-size-mm 3.7 --out output/blickensderfer_full_element.stl
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from glyph_poc import build_flat_text, ALIGN_MODE, ALIGN_CENTER_OFFSET_MM, ALIGN_LEFT_OFFSET_MM, \
    ALIGN_MODIFIED_LEFT_CHARS, ALIGN_MODIFIED_LEFT_OFFSET_MM, ALIGN_MODIFIED_RIGHT_CHARS, \
    ALIGN_MODIFIED_RIGHT_OFFSET_MM  # noqa: E402
import scad_primitives as sp  # noqa: E402


def build_type_test_line(text, cpi, font_path, font_size_mm, points_per_mm=8.0, depth=0.4,
                          lpi=6.0, align_kwargs=None):
    line_spacing_mm = 25.4 / lpi  # same fixed-pitch convention as cpi, just vertical
    slot_mm = 25.4 / cpi
    parts = []
    for j, line in enumerate(text.split("\n")):
        n = len(line)
        y = -j * line_spacing_mm
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            mesh = build_flat_text(ch, points_per_mm, depth, font_size_mm=font_size_mm, font_path=font_path,
                                    align_kwargs=align_kwargs)
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
    parser.add_argument("--points-per-mm", type=float, default=8.0)
    parser.add_argument("--align-mode", default=ALIGN_MODE, help='"center" or "left" (default: %(default)s)')
    parser.add_argument("--center-offset-mm", type=float, default=ALIGN_CENTER_OFFSET_MM)
    parser.add_argument("--left-offset-mm", type=float, default=ALIGN_LEFT_OFFSET_MM)
    parser.add_argument("--modified-left-chars", default=ALIGN_MODIFIED_LEFT_CHARS)
    parser.add_argument("--modified-left-offset-mm", type=float, default=ALIGN_MODIFIED_LEFT_OFFSET_MM)
    parser.add_argument("--modified-right-chars", default=ALIGN_MODIFIED_RIGHT_CHARS)
    parser.add_argument("--modified-right-offset-mm", type=float, default=ALIGN_MODIFIED_RIGHT_OFFSET_MM)
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
    )
    mesh = build_type_test_line(args.text, args.cpi, args.font_path, args.font_size_mm, args.points_per_mm,
                                 lpi=args.lpi, align_kwargs=align_kwargs)
    print(f"TypeTest: verts={len(mesh.vertices)} faces={len(mesh.faces)} watertight={mesh.is_watertight}")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    mesh.export(args.out)
    print(f"wrote {args.out}")
