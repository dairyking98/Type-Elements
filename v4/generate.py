#!/usr/bin/env python3
"""
v4 generation entry point. Usage:

    python3 generate.py config/blickensderfer.yaml
    python3 generate.py config/blickensderfer.yaml --points-per-mm 20 --separation-mm 1.5

All real-machine parameters live in the config file, not in code - see
config/blickensderfer.yaml for the full parameter set and comments.
"""

import argparse
import importlib
import math
import os
import sys
import tempfile

import numpy as np
import trimesh
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import build_log  # noqa: E402 - needs the lib/ sys.path.insert above first


def _apply_cross_section(mesh, angle_deg):
    """Debug-only: clips mesh to one side of a vertical plane through the
    machine's central (Z) axis at angle_deg (degrees, measured in the XY
    plane) - a cutaway view for inspecting internal geometry (hollow
    space, drive pin, resin supports, ...) without printing/viewing the
    whole opaque part. angle_deg=None (the default, nothing passed on the
    CLI) is a no-op - this never changes output for a normal build.

    Uses manifold3d's own Manifold.trim_by_plane rather than
    trimesh.intersections.slice_mesh_plane - tried that first, but its
    triangulated cap left FullElement (no resin supports) non-watertight/
    non-volume after the cut even off-axis, while manifold3d's native
    half-space trim (the same engine scad_primitives.union_all() already
    uses for real assembly booleans, per CLAUDE.md) produced a clean
    watertight result in the same case."""
    if angle_deg is None:
        return mesh
    from manifold3d import Manifold, Mesh as ManifoldMesh

    angle_rad = math.radians(angle_deg)
    normal = (math.cos(angle_rad), math.sin(angle_rad), 0.0)
    manifold = Manifold(mesh=ManifoldMesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32)))
    trimmed = manifold.trim_by_plane(normal, 0.0)
    result = trimmed.to_mesh()
    return trimesh.Trimesh(vertices=result.vert_properties, faces=result.tri_verts, process=False)


def _atomic_export(mesh, out_path):
    """trimesh's mesh.export(path) opens/truncates the destination file
    directly, then writes - not atomic. tune.py's f3d --watch window has
    its own filesystem watcher, independent of tune.py telling it to
    reload, and can fire on that truncate/open event before the write
    completes, briefly (or, on a slow/loaded disk, not so briefly) loading
    a 0-byte or partial STL - reported as f3d showing "[EMPTY]" right
    after a Preview/Render. Writing to a temp file in the SAME directory
    (so the final os.replace is a same-filesystem rename, atomic on POSIX)
    and renaming it into place means the destination path only ever shows
    either the complete previous file or the complete new one, never a
    partial write in between - the standard fix for this class of race,
    not specific to any one machine."""
    out_dir = os.path.dirname(out_path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".tmp-", suffix=os.path.splitext(out_path)[1])
    os.close(fd)
    try:
        mesh.export(tmp_path)
        os.replace(tmp_path, out_path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _load_machine(config_path):
    """Peeks the config's `machine:` key (blickensderfer/postal/...) and
    imports the matching module - see lib/cylinder_machine.py's docstring
    for how the two machine modules share code. Defaults to
    "blickensderfer" when absent, so pre-Postal configs need no changes."""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return importlib.import_module(cfg.get("machine", "blickensderfer"))


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
    parser.add_argument("--draft-angle-deg", type=float, default=None,
                         help="override build.draft_angle_deg from the config - half-angle "
                              "of the Minkowski draft cone each character is swept with "
                              "(real machine value 55deg)")
    parser.add_argument("--minkowski", dest="minkowski_enabled", action="store_true", default=None,
                         help="force the Minkowski draft sweep on, regardless of the config")
    parser.add_argument("--no-minkowski", dest="minkowski_enabled", action="store_false",
                         help="skip the Minkowski draft sweep (fast, undrafted preview - "
                              "correct platen curve/placement, no taper) regardless of "
                              "the config")
    parser.add_argument("--minkowski-text", dest="minkowski_text", action="store_true", default=None,
                         help="force Mignon's Logo/Label draft-cone text on, regardless of the "
                              "config (logo.minkowski_text) - no-op for machines without this "
                              "option")
    parser.add_argument("--no-minkowski-text", dest="minkowski_text", action="store_false",
                         help="force Mignon's Logo/Label text to the plain flat extrude "
                              "(fast), regardless of the config - no-op for machines without "
                              "this option")
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
    parser.add_argument("--calibrate", action="store_true",
                         help="build a Calibration element (sweeps baseline or platen "
                              "cutout per physical column, same test character struck "
                              "everywhere) instead of the real element, for empirically "
                              "finding layout.baseline_row/cutout_row - see calibration.* "
                              "in the config and cylinder_machine.CalibrationTextRing")
    parser.add_argument("--calibration-char", default=None,
                         help="override calibration.test_char from the config")
    parser.add_argument("--calibration-vary-baseline", dest="calibration_vary_baseline",
                         action="store_true", default=None,
                         help="override calibration.vary_baseline from the config (force on)")
    parser.add_argument("--calibration-no-vary-baseline", dest="calibration_vary_baseline",
                         action="store_false",
                         help="override calibration.vary_baseline from the config (force off)")
    parser.add_argument("--calibration-vary-cutout", dest="calibration_vary_cutout",
                         action="store_true", default=None,
                         help="override calibration.vary_cutout from the config (force on)")
    parser.add_argument("--calibration-no-vary-cutout", dest="calibration_vary_cutout",
                         action="store_false",
                         help="override calibration.vary_cutout from the config (force off)")
    parser.add_argument("--calibration-start", type=float, default=None,
                         help="override calibration.start from the config")
    parser.add_argument("--calibration-interval", type=float, default=None,
                         help="override calibration.interval from the config")
    parser.add_argument("--calibration-reference-config", default=None,
                         help="load layout.baseline_row/cutout_row from THIS config as the "
                              "calibration sweep's fixed reference/anchor, instead of the "
                              "config being built (which may have already-edited, in-progress "
                              "values) - pass the MASTER config here so repeated calibration "
                              "passes always sweep around the same fixed point, not a moving "
                              "target that shifts every time you dial in a value")
    parser.add_argument("--out", default=None,
                         help="override output.directory/output.stl_name from the config "
                              "(full path to the .stl to write)")
    parser.add_argument("--cross-section-angle-deg", type=float, default=None,
                         help="debug: clip the final mesh to one side of a vertical plane "
                              "through the machine's central axis at this angle (degrees) - "
                              "applies to any build target (element/gauge/calibration); "
                              "omit to disable (default)")
    parser.add_argument("--hammond-part", default=None,
                         choices=["rib_only"],
                         help="Hammond only: export just the rib+pin-support assembly by "
                              "itself (hammond.RibOnly()), no resin supports, meant to be "
                              "printed separately and glued to a Shuttle build (with the "
                              "Rib checkbox off) afterward. This used to be one of three "
                              "FDM-part-export choices ('shuttle_minus_rib'/'shuttle_plus_rib'"
                              "/'rib_only') - the other two are now redundant with a normal "
                              "Shuttle build (element.groove/the Build tab's Rib checkbox "
                              "already selects the with-rib/without-rib shell variant, and "
                              "Resin supports off already skips resin geometry), so only "
                              "'rib_only' remains as its own dedicated flag.")
    parser.add_argument("--cut-bodies", action="store_true",
                         help="debug: export the union of Subtractive()'s negative/cutter "
                              "tool bodies (HollowSpace, DrivePin, core grooves, ...) "
                              "instead of doing the real additive-subtractive difference - "
                              "lets you verify what's actually about to be removed. Only "
                              "applies to the plain Element/Resin build path (ignored with "
                              "--gauge/--calibrate); composes with --cross-section-angle-deg")
    args = parser.parse_args()

    bd = _load_machine(args.config)
    bd.configure(args.config)

    # Minkowski_Text is a plain module global (like Logo_Text/Cylinder_Shape/
    # etc.), not threaded through build_fn's kwargs the way minkowski_enabled
    # is - overriding it here directly, same effect. hasattr guards machines
    # without this option (everything but Mignon) as a no-op.
    if args.minkowski_text is not None and hasattr(bd, "Minkowski_Text"):
        bd.Minkowski_Text = args.minkowski_text

    render_core_groove = False if args.no_core_groove else None  # None = use config default

    out_path = args.out
    if out_path is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), bd.OUTPUT_DIR)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, bd.OUTPUT_STL_NAME)

    if args.gauge:
        # not part of the real element at all - no char placement
        full = bd.GaugeTestSet(render_core_groove=render_core_groove)
        full = _apply_cross_section(full, args.cross_section_angle_deg)
        build_log.mesh_report(full, "GaugeTestSet")
        _atomic_export(full, out_path)
        print(f"wrote {out_path}", flush=True)
        return

    if args.calibrate:
        # a real element (Additive-Subtractive, same hollow-out as a
        # normal build), just with CalibrationTextRing() swapped in for
        # TextRing() - see cylinder_machine.CalibrationElement. Same
        # build-quality kwargs as the normal build_fn call below - this
        # DOES go through build_glyph/TextRing's real draft/placement
        # pipeline (unlike --gauge), so --minkowski/--no-minkowski etc.
        # need to actually reach it, not just be parsed and dropped.
        reference_baseline_row = reference_cutout_row = None
        if args.calibration_reference_config:
            with open(args.calibration_reference_config) as f:
                ref_cfg = yaml.safe_load(f)
            reference_baseline_row = ref_cfg["layout"]["baseline_row"]
            reference_cutout_row = ref_cfg["layout"]["cutout_row"]
        full, mapping_lines = bd.CalibrationElement(
            test_char=args.calibration_char,
            vary_baseline=args.calibration_vary_baseline,
            vary_cutout=args.calibration_vary_cutout,
            start=args.calibration_start,
            interval=args.calibration_interval,
            reference_baseline_row=reference_baseline_row,
            reference_cutout_row=reference_cutout_row,
            points_per_mm=args.points_per_mm,
            separation_mm=args.separation_mm,
            render_core_groove=render_core_groove,
            cone_segments=args.cone_segments,
            simplify_tolerance_mm=args.simplify_tolerance_mm,
            platen_fn=args.platen_fn,
            minkowski_enabled=args.minkowski_enabled,
            draft_angle_deg=args.draft_angle_deg,
        )
        full = _apply_cross_section(full, args.cross_section_angle_deg)
        build_log.mesh_report(full, "CalibrationElement")
        _atomic_export(full, out_path)
        print(f"wrote {out_path}", flush=True)
        # .txt sidecar - the user's explicit ask: a durable keyboard-key/
        # position -> tested-value mapping alongside the STL, not just a
        # console scrollback you have to have caught live
        mapping_path = os.path.splitext(out_path)[0] + "_mapping.txt"
        with open(mapping_path, "w") as f:
            f.write("\n".join(mapping_lines) + "\n")
        print(f"wrote {mapping_path}", flush=True)
        return

    if args.hammond_part:
        if not hasattr(bd, "RibOnly"):
            print(f"--hammond-part is only meaningful for hammond (got machine={bd.__name__!r})",
                  file=sys.stderr, flush=True)
            sys.exit(1)
        full = bd.RibOnly()
        char_parts = []
        label = f"hammond --hammond-part {args.hammond_part}"
        full = _apply_cross_section(full, args.cross_section_angle_deg)
        build_log.mesh_report(full, label)
        _atomic_export(full, out_path)
        print(f"wrote {out_path}", flush=True)
        return

    if args.cut_bodies:
        # Subtractive() alone is fully independent of Additive()/TextRing
        # character placement (see cylinder_machine.Subtractive() and its
        # per-machine equivalents in mignon.py/bennett.py) - skipping the
        # glyph pipeline entirely also makes this debug view fast.
        full = bd.Subtractive(render_core_groove)
        char_parts = []
        label = "Subtractive (cut bodies)"
    else:
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
            draft_angle_deg=args.draft_angle_deg,
        )
        label = "ResinPrint" if resin_support else "FullElement"
    full = _apply_cross_section(full, args.cross_section_angle_deg)

    build_log.mesh_report(full, label)

    _atomic_export(full, out_path)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
