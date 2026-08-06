#!/usr/bin/env python3
"""
One-off resin-supports-only render: exports ONLY a machine's resin-support
lattice (real print orientation, no body) - not a general per-machine
feature, generate.py's ResinPrint()/FullElement() targets remain the real
entry points for actual printable output. Useful for photographing/
illustrating what the support structure looks like on its own.

Usage:
    python3 generate_supports.py config/blickensderfer.yaml --out output/blickensderfer_supports.stl
    python3 generate_supports.py config/hammond_split.yaml --out output/hammond_split_supports.stl
    python3 generate_supports.py config/selectric12.yaml --out output/selectric12_supports.stl
"""

import argparse
import importlib
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import build_log  # noqa: E402 - needs the lib/ sys.path.insert above first
import scad_primitives as sp  # noqa: E402


def _cylinder_family_supports(mod):
    """Blickensderfer/Postal - ResinSupport() is the drive-pin-trio support
    lattice, already built in world/print orientation with no further
    transform needed (see cylinder_machine.ResinPrint())."""
    return mod.ResinSupport()


def _hammond_split_supports(mod):
    """Both halves, separated - same outer layout as AssembleResin(), just
    without each half's AssembleSide() body unioned in first. ResinSupports()
    is already built directly in the final print-position frame (see
    ResinPrintHalf()) - it does NOT go through ResPrintOrient() the way the
    body does, only the shared left/right placement transform does. An
    earlier version of this function wrongly ran ResPrintOrient() on the
    supports too, which put the lattice at the wrong position/orientation
    relative to where the real body ends up - caught because the standalone
    render didn't match the arrangement of a real Render w/ resin supports."""
    left = sp.scad_transform(mod.ResinSupports(0), ("translate", [0, 7, 0]), ("rotate", [0, 0, -90]))
    right = sp.scad_transform(mod.ResinSupports(1), ("translate", [0, -7, 0]), ("rotate", [0, 0, 90]))
    return sp.union_all([left, right])


def _spherical_supports(mod):
    """Selectric12/Selectric3/Selectric Composer - ResinRodAssemble() lives
    on the shared lib/spherical_machine.py (only FullElement/ResinPrint/
    Additive/TextGauge get re-exported onto each machine's own module -
    see e.g. lib/selectric12.py's import line), already in world/print
    orientation (see spherical_machine.ResinPrint(), which unions it
    against the body with no extra transform of its own)."""
    return mod.spherical_machine.ResinRodAssemble()


BUILDERS = {
    "blickensderfer": _cylinder_family_supports,
    "postal": _cylinder_family_supports,
    "hammond_split": _hammond_split_supports,
    "selectric12": _spherical_supports,
    "selectric3": _spherical_supports,
    "selectric_composer": _spherical_supports,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", help="path to a YAML config, e.g. config/blickensderfer.yaml")
    parser.add_argument("--out", required=True, help="output STL path")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    machine = cfg["machine"]
    if machine not in BUILDERS:
        raise SystemExit(f"generate_supports.py has no resin-support builder for machine {machine!r} "
                          f"- supported: {sorted(BUILDERS)}")

    mod = importlib.import_module(machine)
    mod.configure(args.config)
    support = BUILDERS[machine](mod)
    support, _, _, _ = sp.check_and_repair(support, label=f"{machine} resin supports")
    build_log.mesh_report(support, "ResinSupportsOnly")
    build_log.atomic_export(support, args.out)
    print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
