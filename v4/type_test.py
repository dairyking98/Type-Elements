#!/usr/bin/env python3
"""
Builds a flat, CPI-spaced test block for quick font/legibility testing -
matches v2/blickensderfer.scad's TypeTest() spacing convention: each
character gets a FIXED-width slot of 25.4/cpi mm (typewriter fixed-pitch,
not proportional spacing), centered within it. Text may contain embedded
newlines for multiple stacked lines. Independent of the real cylindrical
element pipeline (no draft, no platen scallop, no placement-on-cylinder)
- just flat extruded outlines, for speed.

Usage:
    python3 type_test.py "line one\nline two" --cpi 10 --font-path /path/to/font.ttf --font-size-mm 3.7 --out output/blickensderfer_full_element.stl
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from glyph_poc import build_flat_text  # noqa: E402
import scad_primitives as sp  # noqa: E402


def build_type_test_line(text, cpi, font_path, font_size_mm, points_per_mm=8.0, depth=0.4,
                          line_spacing_mm=None):
    if line_spacing_mm is None:
        line_spacing_mm = font_size_mm * 1.6  # no v2 row-spacing convention applies here
        # (that's real element geometry, not a flat preview) - just a
        # reasonable multiple of font size so lines don't touch/overlap
    slot_mm = 25.4 / cpi
    parts = []
    for j, line in enumerate(text.split("\n")):
        n = len(line)
        y = -j * line_spacing_mm
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            mesh = build_flat_text(ch, points_per_mm, depth, font_size_mm=font_size_mm, font_path=font_path)
            # center horizontally on the character's own ink bbox, baseline
            # (y=0) unchanged - same convention as LogoText, see its docstring
            center_x = (mesh.bounds[0][0] + mesh.bounds[1][0]) / 2.0
            mesh.apply_translation([-center_x, 0, 0])
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
    parser.add_argument("--font-path", required=True)
    parser.add_argument("--font-size-mm", type=float, required=True)
    parser.add_argument("--points-per-mm", type=float, default=8.0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    mesh = build_type_test_line(args.text, args.cpi, args.font_path, args.font_size_mm, args.points_per_mm)
    print(f"TypeTest: verts={len(mesh.vertices)} faces={len(mesh.faces)} watertight={mesh.is_watertight}")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    mesh.export(args.out)
    print(f"wrote {args.out}")
