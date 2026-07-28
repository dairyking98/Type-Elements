#!/usr/bin/env python3
"""
v4 legend-generation entry point (Mignon only - see lib/mignon_legend.py's
module docstring for what this ports from v1/Mignon/MignonIndex.scad).
Usage:

    python3 generate_legend.py config/mignon.yaml
    python3 generate_legend.py config/mignon_plakatschrift.yaml --out output/plakat_legend.svg

Writes a flat 2D SVG reference card - a completely separate output from
generate.py's 3D element build, sharing only lib/glyph_poc.py's contour/
composition helpers.
"""

import argparse
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import mignon_legend  # noqa: E402 - needs the lib/ sys.path.insert above first


def _atomic_write_text(text, out_path):
    """Same temp-file-then-os.replace() pattern as build_log.
    atomic_export() (mesh export) - avoids a reader ever seeing a
    truncated/partial file mid-write, for the same reason that matters
    there."""
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp_path, out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to a Mignon YAML config, e.g. config/mignon.yaml")
    parser.add_argument("--out", default=None,
                         help="output .svg path (default: <stem>_legend.svg inside the "
                              "config's own output.directory)")
    args = parser.parse_args()

    mignon_legend.configure(args.config)

    out_path = args.out
    if out_path is None:
        with open(args.config, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg["output"]["directory"])
        os.makedirs(out_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(cfg["output"]["stl_name"]))[0]
        out_path = os.path.join(out_dir, f"{stem}_legend.svg")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    svg_text = mignon_legend.render_svg()
    _atomic_write_text(svg_text, out_path)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
