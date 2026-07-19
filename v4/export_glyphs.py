#!/usr/bin/env python3
"""
Exports every character in the configured layout as its own STL file, for
visual inspection one-by-one - not part of generate.py's normal flow.
Uses the same build_glyph() call TextRing() makes (real per-row
radius_y_offset_mm/platen_radius_mm from the config, real alignment), so
what you see here matches what ends up on the actual element.

Usage:
    python3 export_glyphs.py config/blickensderfer.yaml
    python3 export_glyphs.py config/blickensderfer.yaml --out-dir output/glyphs --points-per-mm 8 --cone-segments 12
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import blickensderfer as bd  # noqa: E402
from glyph_poc import build_glyph  # noqa: E402


def safe_name(ch):
    return ch if ch.isalnum() else f"u{ord(ch):04x}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--out-dir", default="output/glyphs")
    parser.add_argument("--points-per-mm", type=float, default=None)
    parser.add_argument("--separation-mm", type=float, default=None)
    parser.add_argument("--cone-segments", type=int, default=None)
    parser.add_argument("--simplify-tolerance-mm", type=float, default=None)
    args = parser.parse_args()

    bd.configure(args.config)
    points_per_mm = args.points_per_mm or bd.DEFAULT_POINTS_PER_MM
    separation_mm = args.separation_mm or bd.DEFAULT_SEPARATION_MM
    cone_segments = args.cone_segments or bd.DEFAULT_CONE_SEGMENTS
    simplify_tolerance_mm = (args.simplify_tolerance_mm if args.simplify_tolerance_mm is not None
                              else bd.DEFAULT_SIMPLIFY_TOLERANCE_MM)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    total = sum(len(row) for row in bd.DHIATENSOR)
    done = 0
    for row, row_chars in enumerate(bd.DHIATENSOR):
        for col, ch in enumerate(row_chars):
            done += 1
            try:
                mesh = build_glyph(
                    ch, points_per_mm, separation_mm=separation_mm, row=row,
                    align_kwargs=bd.ALIGN_KWARGS, font_path=bd.FONT_PATH, font_size_mm=bd.FONT_SIZE_MM,
                    radius_y_offset_mm=bd.CUTOUT_ROW[row] - bd.BASELINE_ROW[row],
                    platen_radius_mm=bd.PLATEN_RADIUS_MM, cone_segments=cone_segments,
                    simplify_tolerance_mm=simplify_tolerance_mm)
            except Exception as e:
                print(f"[{done}/{total}] row{row}_col{col:02d}_{safe_name(ch)} SKIPPED: {e}")
                continue
            fname = f"row{row}_col{col:02d}_{safe_name(ch)}.stl"
            mesh.export(os.path.join(out_dir, fname))
            flag = "" if mesh.is_watertight and mesh.is_volume else "  <-- NOT watertight/is_volume!"
            print(f"[{done}/{total}] {fname}  verts={len(mesh.vertices)} "
                  f"watertight={mesh.is_watertight} is_volume={mesh.is_volume}{flag}")

    print(f"\nwrote {total} files to {out_dir}")


if __name__ == "__main__":
    main()
