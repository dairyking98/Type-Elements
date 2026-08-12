#!/usr/bin/env python3
"""
Regenerates CATALOG_INDEX.md from lib/layouts/hammond_catalog.py.

Import STATUS is computed here, never hand-maintained: each catalog entry's
description is classified into (keyboard, language, variant) and matched
against the layouts actually present in lib/layouts. Import a new layout,
re-run this, and the index updates itself - the counts in the document can
therefore never drift from the code.

The classifier encodes the catalogs' own lesson: typeface words never
change the layout, variant words (Fractions, Medical, Chemical, ...) do.

    .venv/bin/python3 gen_catalog_index.py
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.layouts.hammond_catalog import HAMMOND_CATALOG  # noqa: E402

# Typeface words - never change the layout, only how it looks.
FACES = ["Medium Roman", "Small Roman", "Large Roman", "Miniature Roman", "Petite Gothic",
         "Gothic Italic", "Large Gothic", "Medium Gothic", "Special Gothic", "Large Italic",
         "Small Italic", "Law Italic", "Italic Script", "Vertical Script", "Multigraph (Pica)",
         "Display Type", "Clarendon", "German Text", "Gothic", "Italic", "Attic",
         "Caps and Small Caps", "Old Style", "Roman"]
# Variant words - these DO change the figures row.
VARIANTS = ["Special Medical", "Special Chemical", "Special Fractions", "Fractions", "Medical",
            "Chemical", "Library", "Diacritical", "Mathematical", "Literary", "Astronomical",
            "Phonetic", "Check Writer", "Special", "New Orthography"]
LANGS = ["English-Yiddish", "Danish-Norwegian", "Swedish-Finnish", "Polish-German", "French-German",
         "Turkey-Persian", "Arabic-Persian-Turkish", "Dutch-German-French-English", "Hebrew-English",
         "Argentine Government", "Bell Visible Speech", "English Greek", "Small Greek", "Chilian",
         "Portuguese", "Hungarian", "Roumanian", "Esperanto", "Bulgarian", "Lithuanian", "Bohemian",
         "Armenian", "Servian", "Croatian", "Spanish", "English", "Russian", "Italian", "Yiddish",
         "Danish", "German", "French", "Polish", "Greek", "Dutch", "Arabic", "Gaelic", "Irish",
         "Braille"]

# (keyboard, language, variants) -> preset name. Keep in step with
# lib/layouts/hammond_layout.py; a preset missing here just shows as todo.
IMPORTED = {
    ("Ideal", "English", ()): "Ideal",
    ("Ideal", "English", ("Fractions",)): "Ideal, Fractions",
    ("Ideal", "Dutch", ()): "Ideal, Dutch",
    ("Ideal", "Spanish", ()): "Ideal, Spanish",
    ("Ideal", "Croatian", ()): "Ideal, Croatian",
    ("Ideal", "Danish", ("Fractions",)): "Ideal, Danish (Fractions)",
    ("Ideal", "Portuguese", ()): "Ideal, Portuguese",
    ("Ideal", "French", ()): "Ideal, French",
    ("Ideal", "German", ()): "Ideal, German",
    ("Ideal", "Roumanian", ()): "Ideal, Roumanian",
    ("Ideal", "Bohemian", ()): "Ideal, Bohemian",
    ("Ideal", "Polish", ()): "Ideal, Polish",
    ("Ideal", "Hungarian", ()): "Ideal, Hungarian",
    ("Ideal", "Italian", ()): "Ideal, Italian",
    ("Ideal", "Chilian", ()): "Ideal, Chilian",
    ("Universal", "English", ()): "Universal",
    ("Universal", "English", ("Fractions",)): "Universal, Fractions",
    ("Universal", "French", ()): "Universal, French",
    ("Universal", "Esperanto", ()): "Universal, Esperanto",
    ("Universal", "Italian", ()): "Universal, Italian",
    ("Universal", "Portuguese", ()): "Universal, Portuguese",
    ("Universal", "Roumanian", ()): "Universal, Roumanian",
    ("Universal", "Spanish", ()): "Universal, Spanish",
    ("Universal", "Chilian", ()): "Universal, Chilian",
    ("Universal", "Bohemian", ()): "Universal, Bohemian",
    ("Universal", "Bulgarian", ()): "Universal, Bulgarian",
    ("Universal", "Polish", ()): "Universal, Polish",
    ("Universal", "Dutch", ("Fractions",)): "Universal, Dutch (Fractions)",
    ("Universal", "Dutch", ()): "Universal, Dutch",
    ("Universal", "German", ()): "Universal, German",
    ("Universal", "Russian", ()): "Universal, Russian",
    ("Universal", "Swedish-Finnish", ()): "Universal, Swedish-Finnish",
    ("Universal", "Danish-Norwegian", ()): "Universal, Danish-Norwegian",
}
# Read, but one character will not resolve from the scan.
HELD = {
    "88": "blank slot vs under-inked `_`",
    "29B": "Latin-form `N` at position 14: plain N, or `\u2116` without its raised o?",
    "29": "same as 29B", "29A": "same as 29B",
    "49A": "figures row pairs duplicate row-0 letters; N/i unidentifiable",
    "35A": "same as 49A",
    "71A": "stem-with-bowl glyph: `¶`, `Þ` or other",
    "71F": "same as 71A", "34A": "same as 71A", "34D": "same as 71A",
    "50A": "same as 71A", "50C": "same as 71A",
    "41": "diagonal-fraction numerators",
    "162": "scan-damaged glyph after `4%`",
    "184": "prints four lines, not three",
    "23E": "one unidentifiable figure slot",
    "23F": "one unidentifiable figure slot",
    "23G": "one unidentifiable figure slot",
    "136": "chemical figures row not legible",
    "134A": "figures row prints \u00f3 twice; \u00ed absent from the shuttle",
    "56": "same as 134A", "64": "same as 134A",
    "7": "polytonic diacritics not separable at this resolution",
    "75": "same as 7", "82": "same as 7", "8": "same as 7",
    "112A": "same as 7", "112B": "same as 7",
}


def classify(desc):
    kb = "Ideal" if "Ideal" in desc else ""
    if "Universal" in desc:
        kb = kb + "/" + "Universal" if kb else "Universal"
    variants = [v for v in VARIANTS if v in desc and v != "New Orthography"]
    lang = next((l for l in LANGS if l in desc), "English")
    return kb or "?", lang, variants, "New Orthography" in desc


BY_NUMBER = {"29": "Universal, Russian (Old Style)",
             "29A": "Universal, Russian (Old Style)",
             "29B": "Universal, Russian (Old Style)"}


def status(num, desc):
    if num in BY_NUMBER:
        return "imported", BY_NUMBER[num]
    if num in HELD:
        return "held", HELD[num]
    kb, lang, variants, new_orth = classify(desc)
    if new_orth and lang == "German":
        if kb == "Ideal":
            return "imported", "Ideal, German (New Orthography)"
        if kb == "Universal" and not variants:
            return "imported", "Universal, German (New Orthography)"
        if kb == "Universal" and variants == ["Fractions"]:
            return "imported", "Universal, German (New Orthography, Fractions)"
    if lang == "Spanish" and kb == "Ideal" and "Caps and Small Caps" in desc:
        return "imported", "Ideal, Spanish (Caps and Small Caps)"
    if lang == "English" and kb == "Universal" and "Caps and Small Caps" in desc and not variants:
        return "imported", "Universal, Caps and Small Caps"
    hit = IMPORTED.get((kb, lang, tuple(v for v in variants if v == "Fractions")))
    if hit and not [v for v in variants if v != "Fractions"]:
        return "imported", hit
    return "todo", f"{kb} / {lang}" + (f" / {', '.join(variants)}" if variants else "")


def sort_key(num):
    m = re.match(r"(\d+)([A-Z]*)", num)
    return int(m.group(1)), m.group(2)


def main():
    rows = [(n, d, p, *status(n, d)) for n, d, p in HAMMOND_CATALOG]
    rows.sort(key=lambda r: sort_key(r[0]))
    n_imp = sum(1 for r in rows if r[3] == "imported")
    n_held = sum(1 for r in rows if r[3] == "held")
    n_todo = sum(1 for r in rows if r[3] == "todo")
    print(f"Hammond: {n_imp} imported / {n_held} held / {n_todo} todo, of {len(rows)}")

    doc = pathlib.Path("CATALOG_INDEX.md").read_text()
    head, sep, tail = doc.partition("| # | Description | Page | Status | Preset / note |")
    body = ["| # | Description | Page | Status | Preset / note |", "|---|---|---|---|---|"]
    for n, d, pg, st, note in rows:
        mark = {"imported": "**imported**", "held": "held", "todo": "todo"}[st]
        body.append(f"| {n} | {d} | {pg} | {mark} | {note} |")
    rest = tail.split("\n---\n", 1)[1] if "\n---\n" in tail else ""
    head = re.sub(r"\*\*\d+ of \d+ catalogued shuttles are covered \(\d+%\)\*\* — \d+ held on an unresolved character,\n\d+ not yet transcribed\.",
                  f"**{n_imp} of {len(rows)} catalogued shuttles are covered "
                  f"({100*n_imp//len(rows)}%)** — {n_held} held on an unresolved character,\n"
                  f"{n_todo} not yet transcribed.", head)
    pathlib.Path("CATALOG_INDEX.md").write_text(head + "\n".join(body) + "\n\n---\n" + rest)
    print("regenerated CATALOG_INDEX.md")
    return rows, n_imp, n_held, n_todo


if __name__ == "__main__":
    main()
