#!/usr/bin/env python3
"""
Phase 2 test harness helper: lists the v4 files the in-browser engine needs
(manifest.json) and copies the fonts a machine's config references into
_fonts/ (git-ignored) so the test page can fetch them. The page writes every
file into Pyodide's in-memory filesystem at the SAME path it has on disk, so
v4's configs (absolute font paths and all) work unchanged.

    python3 v5/browser/make_manifest.py selectric12
Then serve the REPO ROOT:  python3 -m http.server 8093   and open
    http://127.0.0.1:8093/v5/browser/phase2.html
"""
import glob
import json
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V4 = os.path.join(ROOT, "v4")
machine = sys.argv[1] if len(sys.argv) > 1 else "selectric12"

files = sorted(glob.glob(os.path.join(V4, "lib", "**", "*.py"), recursive=True))
files += [os.path.join(V4, "generate.py"), os.path.join(V4, "config", f"{machine}.yaml")]
files += sorted(glob.glob(os.path.join(V4, "assets", "svg", "*.svg")))

cfg = yaml.safe_load(open(os.path.join(V4, "config", f"{machine}.yaml")))
fonts = set()


def walk(node, key=""):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, k)
    elif isinstance(node, str) and node.lower().endswith((".ttf", ".otf", ".ttc", ".otc")) and os.path.isfile(node):
        fonts.add(node)


walk(cfg)
os.makedirs(os.path.join(HERE, "_fonts"), exist_ok=True)
font_map = {}
for i, p in enumerate(sorted(fonts)):
    dst = os.path.join(HERE, "_fonts", f"{i}{os.path.splitext(p)[1]}")
    shutil.copyfile(p, dst)
    font_map[p] = "/" + os.path.relpath(dst, ROOT)

manifest = {"machine": machine,
            "files": {"/" + os.path.relpath(f, ROOT): "/" + os.path.relpath(f, ROOT) for f in files},
            "fonts": font_map}
json.dump(manifest, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
print(f"{len(files)} v4 files, {len(font_map)} fonts -> manifest.json")
