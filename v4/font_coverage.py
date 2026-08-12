#!/usr/bin/env python3
"""
Scans a font library for glyph coverage against a target character set - a
named machine layout preset (lib/layouts' LAYOUT_PRESETS_BY_MACHINE), a
config's currently active layout.rows, or a literal string - and reports
which fonts have every glyph, which are close, and which are missing what.

Same "mapped in cmap but drawn with zero contours" vs "not in the font's
character map at all" distinction FONT_AUDIT.md's manual investigation
found matters (e.g. Blackletter Asterisk's blank +=£§äöü, both real gaps
but different in kind) - here as a reusable tool instead of a one-off pass.

Usage:
    python3 font_coverage.py --preset hammond:"Universal, Math"
    python3 font_coverage.py --preset hammond:"Universal, Math" --font-dir ~/fonts/Library
    python3 font_coverage.py --chars "ABCabc0123" --font-dir ~/fonts
    python3 font_coverage.py --config config/hammond.yaml --out report.md

    # also runs each glyph through the real contour/triangulate pipeline
    # (catches the self-intersection/all-off-curve/debris-contour classes
    # FONT_AUDIT.md found - slow, minutes over a 1000+ font library):
    python3 font_coverage.py --preset hammond:"Universal, Math" --deep

--preset reads lib/layouts, which is plain data with no third-party
imports, so it no longer needs tune.py's TUI dependency stack installed.
"""

import argparse
import os
import sys

import freetype
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from glyph_poc import (  # noqa: E402
    load_font_face, get_glyph_contours_and_advance, classify_and_triangulate,
    em_to_mm_scale, FONT_SIZE_MM, DEFAULT_FLATNESS_TOLERANCE_MM,
)

FONT_EXTS = {".ttf", ".otf", ".ttc", ".otc"}
DEFAULT_FONT_DIR = os.path.expanduser("~/fonts")


def charset_from_preset(spec):
    machine, sep, preset = spec.partition(":")
    if not sep:
        raise SystemExit(f'--preset expects MACHINE:"Preset Name", got {spec!r}')
    # lib/layouts is plain data with no third-party imports, so --preset no
    # longer drags in tune.py's TUI dependency stack (it used to import tune
    # purely to reach these tables, which meant textual had to be installed).
    from lib.layouts import LAYOUT_PRESETS_BY_MACHINE
    presets = LAYOUT_PRESETS_BY_MACHINE.get(machine)
    if presets is None:
        raise SystemExit(f"unknown machine {machine!r} - choices: "
                          f"{sorted(LAYOUT_PRESETS_BY_MACHINE)}")
    rows = presets.get(preset)
    if rows is None:
        raise SystemExit(f"unknown preset {preset!r} for {machine!r} - choices: {sorted(presets)}")
    return "".join(rows)


def charset_from_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)
    rows = cfg["layout"]["rows"]
    return "".join(rows)


def find_fonts(font_dir):
    paths = []
    for root, _dirs, files in os.walk(font_dir):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in FONT_EXTS:
                paths.append(os.path.join(root, fn))
    return sorted(paths)


def check_font(font_path, charset, deep=False):
    try:
        face = load_font_face(font_path)
    except Exception as e:
        return {"error": str(e)}

    scale = em_to_mm_scale(FONT_SIZE_MM, face.units_per_EM) if face.units_per_EM else 1.0
    ok, blank, missing, deep_errors = [], [], [], []
    for ch in charset:
        gid = face.get_char_index(ord(ch))
        if gid == 0:
            missing.append(ch)
            continue
        face.load_glyph(gid, freetype.FT_LOAD_NO_SCALE)
        if face.glyph.outline.n_contours == 0:
            blank.append(ch)
            continue
        if deep:
            try:
                contours, _advance = get_glyph_contours_and_advance(
                    ch, DEFAULT_FLATNESS_TOLERANCE_MM, scale, font_path=font_path)
                classify_and_triangulate(contours)
            except Exception as e:
                deep_errors.append((ch, str(e)))
                continue
        ok.append(ch)

    return {
        "family": (face.family_name or b"").decode(errors="replace"),
        "style": (face.style_name or b"").decode(errors="replace"),
        "ok": ok, "blank": blank, "missing": missing, "deep_errors": deep_errors,
    }


def format_chars(chars):
    return "".join(chars) if chars else "-"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--preset", metavar='MACHINE:"Preset Name"',
                      help='e.g. hammond:"Universal, Math"')
    src.add_argument("--config", help="config YAML to read layout.rows from")
    src.add_argument("--chars", help="literal character set string")
    parser.add_argument("--font-dir", default=DEFAULT_FONT_DIR,
                         help=f"searched recursively for .ttf/.otf/.ttc (default: {DEFAULT_FONT_DIR})")
    parser.add_argument("--deep", action="store_true",
                         help="also run each glyph through the real contour/triangulate pipeline")
    parser.add_argument("--out", help="write the full per-font breakdown as markdown to this path")
    args = parser.parse_args()

    if args.preset:
        charset = charset_from_preset(args.preset)
    elif args.config:
        charset = charset_from_config(args.config)
    else:
        charset = args.chars
    charset = list(dict.fromkeys(charset))  # de-dupe, keep first-seen order
    total_chars = len(charset)

    font_dir = os.path.expanduser(args.font_dir)
    fonts = find_fonts(font_dir)
    if not fonts:
        raise SystemExit(f"no .ttf/.otf/.ttc files found under {font_dir}")

    print(f"target charset ({total_chars} unique): {''.join(charset)}")
    print(f"scanning {len(fonts)} fonts under {font_dir}{' (deep mode)' if args.deep else ''}...\n",
          flush=True)

    results = []
    for i, font_path in enumerate(fonts, 1):
        rel = os.path.relpath(font_path, font_dir)
        r = check_font(font_path, charset, deep=args.deep)
        r["path"] = font_path
        r["rel"] = rel
        results.append(r)
        if i % 100 == 0 or i == len(fonts):
            print(f"  [{i}/{len(fonts)}] scanned", flush=True)

    errored = [r for r in results if "error" in r]
    scored = [r for r in results if "error" not in r]
    for r in scored:
        bad = len(r["blank"]) + len(r["missing"]) + len(r["deep_errors"])
        r["coverage"] = (total_chars - bad) / total_chars if total_chars else 1.0
    scored.sort(key=lambda r: (-r["coverage"], r["rel"].lower()))

    perfect = [r for r in scored if r["coverage"] == 1.0]
    print(f"\n{len(perfect)}/{len(scored)} fonts have every glyph "
          f"({len(errored)} unreadable, skipped):\n")
    for r in perfect:
        label = f"{r['family']} {r['style']}".strip() or r["rel"]
        print(f"  OK  {r['rel']}  ({label})")

    partial = [r for r in scored if r["coverage"] < 1.0]
    print(f"\n{len(partial)} fonts missing something - closest matches first:\n")
    for r in partial[:40]:
        n_bad = len(r["blank"]) + len(r["missing"]) + len(r["deep_errors"])
        err_chars = [c for c, _e in r["deep_errors"]]
        print(f"  {r['coverage']*100:5.1f}%  {r['rel']}  "
              f"(missing={format_chars(r['missing'])} blank={format_chars(r['blank'])}"
              f"{' errors=' + format_chars(err_chars) if err_chars else ''})")
    if len(partial) > 40:
        print(f"  ... and {len(partial) - 40} more (see --out for the full list)")

    if errored:
        print(f"\n{len(errored)} fonts couldn't be read:\n")
        for r in errored:
            print(f"  ERROR  {r['rel']}  ({r['error']})")

    if args.out:
        with open(args.out, "w") as f:
            f.write(f"# Font coverage report\n\n")
            f.write(f"Target charset ({total_chars} unique): `{''.join(charset)}`\n\n")
            f.write(f"Scanned {len(fonts)} fonts under `{font_dir}`"
                    f"{' (deep mode)' if args.deep else ''}.\n\n")
            f.write(f"## Full coverage ({len(perfect)})\n\n")
            for r in perfect:
                label = f"{r['family']} {r['style']}".strip() or r["rel"]
                f.write(f"- `{r['rel']}` ({label})\n")
            f.write(f"\n## Partial coverage ({len(partial)})\n\n")
            for r in partial:
                f.write(f"- `{r['rel']}` — {r['coverage']*100:.1f}%")
                if r["missing"]:
                    f.write(f" — missing (not in cmap): `{format_chars(r['missing'])}`")
                if r["blank"]:
                    f.write(f" — blank (mapped, no contours): `{format_chars(r['blank'])}`")
                if r["deep_errors"]:
                    chars = format_chars([c for c, _e in r["deep_errors"]])
                    f.write(f" — pipeline errors: `{chars}`")
                f.write("\n")
            if errored:
                f.write(f"\n## Unreadable ({len(errored)})\n\n")
                for r in errored:
                    f.write(f"- `{r['rel']}` — {r['error']}\n")
        print(f"\nwrote full report to {args.out}")


if __name__ == "__main__":
    main()
