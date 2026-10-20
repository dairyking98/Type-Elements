#!/usr/bin/env python3
"""
Builds the in-browser engine bundle: every file the Pyodide engine needs,
packed into one file, OUTDIR/engine.pack, so starting the engine costs one
request (cacheable like any other) instead of one per file. Format: a 4-byte
little-endian header length, a JSON header [[engine path, size], ...], then
the files' bytes back to back. manifest.json lists the same files, for
people. The deploy workflow writes it
next to the app (/app/_engine/); for local testing, v5/ui/_engine/.

    python3 v5/browser/make_bundle.py v5/ui/_engine

What goes in: v4's code (lib/, generate.py, type_test.py, generate_legend.py,
font_coverage.py), its master configs and font profiles, its SVG assets,
v5/engine_core.py, the browser adapters (py/), and the bundled fonts.
Running copies and output files never do.
"""
import glob
import json
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V4 = os.path.join(ROOT, "v4")
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "v5", "ui", "_engine"))

files = {}   # engine path -> source path
for src in glob.glob(os.path.join(V4, "lib", "**", "*.py"), recursive=True):
    files["/v4/" + os.path.relpath(src, V4)] = src
for name in ("generate.py", "type_test.py", "generate_legend.py", "font_coverage.py"):
    files[f"/v4/{name}"] = os.path.join(V4, name)
for src in glob.glob(os.path.join(V4, "config", "*.yaml")):
    if not src.endswith(".running.yaml"):
        files["/v4/" + os.path.relpath(src, V4)] = src
for src in glob.glob(os.path.join(V4, "config", "profiles", "**", "*.yaml"), recursive=True):
    files["/persist-seed/profiles/" + os.path.relpath(src, os.path.join(V4, "config", "profiles"))] = src
for src in glob.glob(os.path.join(V4, "assets", "svg", "*.svg")):
    files["/v4/" + os.path.relpath(src, V4)] = src
files["/v5/engine_core.py"] = os.path.join(ROOT, "v5", "engine_core.py")
for src in glob.glob(os.path.join(HERE, "py", "*.py")):
    files["/shim/" + os.path.basename(src)] = src
for src in glob.glob(os.path.join(HERE, "fonts", "*.ttf")):
    files["/fonts/bundled/" + os.path.basename(src)] = src

if os.path.isdir(out):
    shutil.rmtree(out)
os.makedirs(out)
order = sorted(files)
blobs = [open(files[dest], "rb").read() for dest in order]
header = json.dumps([[dest, len(b)] for dest, b in zip(order, blobs)]).encode()
with open(os.path.join(out, "engine.pack"), "wb") as f:
    f.write(struct.pack("<I", len(header)) + header + b"".join(blobs))
total = sum(map(len, blobs))
with open(os.path.join(out, "manifest.json"), "w") as f:
    json.dump({"files": order, "bytes": total}, f)
print(f"{len(files)} files, {total / 1e6:.1f} MB -> {out}/engine.pack")
