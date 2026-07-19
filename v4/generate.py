#!/usr/bin/env python3
"""
v4 generation entry point. Usage:

    python3 generate.py config/blickensderfer.yaml
    python3 generate.py config/blickensderfer.yaml --points-per-mm 20 --separation-mm 1.5

All real-machine parameters live in the config file, not in code - see
config/blickensderfer.yaml for the full parameter set and comments.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import blickensderfer as bd  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to a YAML config, e.g. config/blickensderfer.yaml")
    parser.add_argument("--points-per-mm", type=float, default=None,
                         help="override build.points_per_mm from the config")
    parser.add_argument("--separation-mm", type=float, default=None,
                         help="override build.separation_mm from the config")
    parser.add_argument("--cone-segments", type=int, default=None,
                         help="override build.cone_segments from the config - circular "
                              "segments for the draft's Minkowski cone kernel, trades "
                              "roundness for generation speed")
    parser.add_argument("--simplify-tolerance-mm", type=float, default=None,
                         help="override build.simplify_tolerance_mm from the config - "
                              "collapses manifold3d's minkowski_sum over-triangulation "
                              "noise on flat regions")
    parser.add_argument("--platen-fn", type=int, default=None,
                         help="override quality.platen_fn from the config - circular "
                              "segments for the real platen cutout cylinder")
    parser.add_argument("--minkowski", dest="minkowski_enabled", action="store_true", default=None,
                         help="force the Minkowski draft sweep on, regardless of the config")
    parser.add_argument("--no-minkowski", dest="minkowski_enabled", action="store_false",
                         help="skip the Minkowski draft sweep (fast, undrafted preview - "
                              "correct platen curve/placement, no taper) regardless of "
                              "the config")
    parser.add_argument("--no-core-groove", action="store_true",
                         help="skip CoreGrooves (slow) regardless of the config")
    parser.add_argument("--resin-support", dest="resin_support", action="store_true", default=None,
                         help="add ResinPrint()'s support rods/breakaway ring, regardless of the config")
    parser.add_argument("--no-resin-support", dest="resin_support", action="store_false",
                         help="skip resin supports, regardless of the config")
    parser.add_argument("--gauge", action="store_true",
                         help="build the Shaft Gauge Test set (a small calibration test "
                              "print for finding element.core_id_offset) instead of the "
                              "real element - see blickensderfer.GaugeTestSet")
    parser.add_argument("--out", default=None,
                         help="override output.directory/output.stl_name from the config "
                              "(full path to the .stl to write)")
    args = parser.parse_args()

    bd.configure(args.config)

    render_core_groove = False if args.no_core_groove else None  # None = use config default

    out_path = args.out
    if out_path is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), bd.OUTPUT_DIR)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, bd.OUTPUT_STL_NAME)

    if args.gauge:
        # not part of the real element at all - no char placement, no
        # HollowSpace intersection check (nothing to check it against)
        full = bd.GaugeTestSet(render_core_groove=render_core_groove)
        print(f"GaugeTestSet: verts={len(full.vertices)} faces={len(full.faces)} "
              f"watertight={full.is_watertight} winding_consistent={full.is_winding_consistent} "
              f"is_volume={full.is_volume} volume={full.volume:.3f}mm3", flush=True)
        full.export(out_path)
        print(f"wrote {out_path}", flush=True)
        return

    resin_support = args.resin_support if args.resin_support is not None else bd.DEFAULT_RESIN_SUPPORT

    build_fn = bd.ResinPrint if resin_support else bd.FullElement
    full, char_parts = build_fn(
        points_per_mm=args.points_per_mm,
        separation_mm=args.separation_mm,
        render_core_groove=render_core_groove,
        cone_segments=args.cone_segments,
        simplify_tolerance_mm=args.simplify_tolerance_mm,
        platen_fn=args.platen_fn,
        minkowski_enabled=args.minkowski_enabled,
    )

    label = "ResinPrint" if resin_support else "FullElement"
    print(f"{label}: verts={len(full.vertices)} faces={len(full.faces)} "
          f"watertight={full.is_watertight} winding_consistent={full.is_winding_consistent} "
          f"is_volume={full.is_volume} volume={full.volume:.3f}mm3", flush=True)

    full.export(out_path)
    print(f"wrote {out_path}", flush=True)

    hollow = bd.HollowSpace()
    any_hit = any(hollow.contains(part.vertices).any() for part in char_parts)
    print(f"any character root vertex falls inside HollowSpace: {any_hit}", flush=True)


if __name__ == "__main__":
    main()
