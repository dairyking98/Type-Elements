#!/usr/bin/env python3
"""
Generate static thumbnails for every model in example_renders/ (recursing
into subdirectories, e.g. example_renders/resin_support_renders/), rendered
through the same Three.js scene as the live interactive viewer (see
thumbnail_harness.html, which mirrors dairyking98.github.io's
assets/js/stl-viewer.js: dark charcoal part, white background) rather than
a separate native renderer - one visual source of truth instead of two
tools that can drift apart.

    python3 generate_thumbnails.py
    python3 generate_thumbnails.py --only bennett hammond-split-shuttle

Requires a Chrome/Chromium binary on PATH (headless, --enable-unsafe-
swiftshader for software WebGL - no GPU or X server needed).

Output goes to site/assets/thumbnails/<model>.png - same directory Jekyll
already serves assets/models/ from, so these publish at
https://type-elements.leonardchau.com/assets/thumbnails/<model>.png with
no extra deploy config. Portfolio site pages should link to that URL
directly rather than keeping their own copy.
"""

import argparse
import http.server
import os
import shutil
import subprocess
import sys
import threading

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(REPO_ROOT, "example_renders")
THUMBNAILS_DIR = os.path.join(REPO_ROOT, "site", "assets", "thumbnails")
HARNESS_NAME = "thumbnail_harness.html"

WIDTH, HEIGHT = 1600, 1200
# Generous fixed budget rather than polling for a ready signal - keeps this
# a plain CLI invocation (no DevTools Protocol scripting). Comfortably
# covers the largest example STL (~13MB) loading+parsing over localhost.
VIRTUAL_TIME_BUDGET_MS = 15000

CHROME_CANDIDATES = ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]


def find_chrome():
    for name in CHROME_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    sys.exit(
        "no Chrome/Chromium binary found on PATH (tried: "
        + ", ".join(CHROME_CANDIDATES)
        + ") - install one to generate thumbnails")


def start_server():
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=REPO_ROOT, **kw)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def render_thumbnail(chrome_path, port, stl_name, out_path):
    url = (
        f"http://127.0.0.1:{port}/{HARNESS_NAME}"
        f"?src=example_renders/{stl_name}&w={WIDTH}&h={HEIGHT}"
    )
    subprocess.run(
        [
            chrome_path,
            "--headless=new",
            "--enable-unsafe-swiftshader",
            "--disable-gpu",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--virtual-time-budget={VIRTUAL_TIME_BUDGET_MS}",
            f"--screenshot={out_path}",
            url,
        ],
        check=True,
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", nargs="+", metavar="MODEL",
        help="only regenerate these models (by STL basename, no extension)")
    args = parser.parse_args()

    os.makedirs(THUMBNAILS_DIR, exist_ok=True)
    chrome_path = find_chrome()

    stls = sorted(
        os.path.relpath(os.path.join(dirpath, f), MODELS_DIR)
        for dirpath, _, filenames in os.walk(MODELS_DIR)
        for f in filenames if f.endswith(".stl")
    )
    if args.only:
        wanted = set(args.only)
        stls = [f for f in stls if f[:-4] in wanted]
        missing = wanted - {f[:-4] for f in stls}
        if missing:
            sys.exit(f"no matching STL in {MODELS_DIR} for: {', '.join(sorted(missing))}")

    server = start_server()
    port = server.server_address[1]
    try:
        for stl_rel in stls:
            model = stl_rel[:-4]
            out_path = os.path.join(THUMBNAILS_DIR, f"{model}.png")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            render_thumbnail(chrome_path, port, stl_rel, out_path)
            print(f"rendered {model} -> {os.path.relpath(out_path, REPO_ROOT)}")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
