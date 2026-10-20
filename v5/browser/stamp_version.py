#!/usr/bin/env python3
"""
Cache-busting for the published app: appends ?v=<version> to every local
script/style/module/worker reference in DIR, so a new deploy is never served
from a visitor's stale browser cache (GitHub Pages lets browsers cache files
for 10 minutes, and an ES-module graph can stay stale longer).

    python3 v5/browser/stamp_version.py _site/app <version>
"""
import glob
import os
import re
import sys

root, version = sys.argv[1], sys.argv[2]
names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, "*.js")) + glob.glob(os.path.join(root, "*.css")))
pattern = re.compile(r"""(["'])((?:\./)?(?:%s))\1""" % "|".join(re.escape(n) for n in names))
for path in glob.glob(os.path.join(root, "*.js")) + glob.glob(os.path.join(root, "*.html")):
    text = open(path, encoding="utf-8").read()
    new = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={version}{m.group(1)}", text)
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
        print("stamped", os.path.basename(path))
