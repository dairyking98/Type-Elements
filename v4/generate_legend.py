#!/usr/bin/env python3
"""
v4 legend-generation entry point. Usage:

    python3 generate_legend.py config/mignon.yaml
    python3 generate_legend.py config/hammond.yaml --out output/hammond_legend.svg

Dispatches on the config's machine: key to import <machine>_legend (e.g.
mignon -> lib/mignon_legend.py, hammond/hammond_split -> lib/
hammond_legend.py) - same importlib convention generate.py uses for the
real 3D build modules (see generate.py's _load_machine()), so adding a
new machine's legend just means adding a new lib/<machine>_legend.py
with the same configure()/render_svg() entry points, no changes needed
here. Only machines with an actual v1 index/legend card to port get a
<machine>_legend module - not every machine has one.

Writes a flat 2D SVG reference card - a completely separate output from
generate.py's 3D element build, sharing only lib/glyph_poc.py's contour/
composition helpers.
"""

import argparse
import importlib
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))


def _load_legend_module(config_path):
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    machine = cfg.get("machine")
    module_name = {"hammond_split": "hammond_legend"}.get(machine, f"{machine}_legend")
    try:
        return importlib.import_module(module_name), cfg
    except ModuleNotFoundError:
        print(f"no legend generator for machine={machine!r} (looked for lib/{module_name}.py)",
              file=sys.stderr, flush=True)
        sys.exit(1)


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
    parser.add_argument("config", help="path to a YAML config with a legend generator, "
                                        "e.g. config/mignon.yaml or config/hammond.yaml")
    parser.add_argument("--out", default=None,
                         help="output .svg path (default: <stem>_legend.svg inside the "
                              "config's own output.directory)")
    args = parser.parse_args()

    legend_module, cfg = _load_legend_module(args.config)
    legend_module.configure(args.config)

    out_path = args.out
    if out_path is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg["output"]["directory"])
        os.makedirs(out_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(cfg["output"]["stl_name"]))[0]
        out_path = os.path.join(out_dir, f"{stem}_legend.svg")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    svg_text = legend_module.render_svg()
    _atomic_write_text(svg_text, out_path)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
