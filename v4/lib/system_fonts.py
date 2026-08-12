"""
Enumerates the fonts INSTALLED on this machine, for tune.py's font
pickers (font.path / logo.font_path / label.*_font_path /
legend.legend_font_path - see tune.py's FONT_PATH_FIELD_KEYS). Pure
enumeration + name reading: nothing here touches geometry, and nothing
in the build pipeline imports it - configs still store a plain absolute
path, exactly as before. This only changes how that path gets CHOSEN in
the TUI (pick a font by name instead of hunting for its file).

Platform coverage - Linux and Windows are the two real targets (see
win_setup.bat/lin_setup.sh):

  Linux: `fc-list` (fontconfig) is the source of truth, not a hardcoded
    directory list. It already knows every directory the system is
    actually configured to serve fonts from, INCLUDING per-user ones
    added by hand - e.g. this repo's own font library lives in
    ~/fonts (one <dir> line in ~/.config/fontconfig/fonts.conf), which
    no fixed /usr/share/fonts-style list would ever find. If fc-list
    isn't on PATH (a stripped container, fontconfig not installed), we
    fall back to scanning the well-known directories below - a strictly
    smaller set, hence the fallback and not the default.
  Windows: no fontconfig, so it IS a directory scan - the machine-wide
    %WINDIR%\\Fonts plus %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts, which
    is where "Install for me only" (the non-admin default since Win10
    1809) puts fonts. Scanning both directories rather than reading the
    HKLM/HKCU "Fonts" registry keys gets the same files with no registry
    dependency, and the family/style names come from the font's own name
    table via freetype either way.
  macOS: the standard three directories, for completeness - untested,
    it isn't a supported build platform for this repo.

Family/style names come from the font file itself (fontconfig's name on
Linux, freetype's name table elsewhere), never from the filename - a
filename is frequently a renamed/version-numbered copy that doesn't say
which typeface it holds, which is the whole reason a name-based picker
beats a file browser here.

One entry per FILE, deduped by path: a config field holds a path and
nothing else (no face index), so a .ttc collection that fontconfig
reports as several faces collapses to its first face here - picking it
selects the file, and the pipeline loads face 0, matching what
glyph_poc.load_font_face() would do with that path anyway.

Results are cached module-level (list_system_fonts(refresh=True) rebuilds)
since a full Windows/fallback scan reads a few hundred font files through
freetype and the TUI re-opens its picker many times per session.
"""

import os
import subprocess
import sys
from collections import namedtuple

import freetype

# The four extensions the build pipeline can actually load - same set as
# font_coverage.py's FONT_EXTS. fontconfig happily reports .pfb/.pcf.gz/
# bitmap fonts too; offering one in the picker would just produce a font
# the glyph pipeline can't use, so they're filtered out here rather than
# failing later at build time.
FONT_EXTS = (".ttf", ".otf", ".ttc", ".otc")

# path: absolute path to the font file (what a config's font path key
# stores). family/style: the font's own internal names, for display.
FontEntry = namedtuple("FontEntry", "path family style")

_FALLBACK_FONT_DIRS = {
    # Linux - only used when fc-list is unavailable (see module docstring)
    "linux": (
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        "~/.local/share/fonts",
        "~/.fonts",
    ),
    "win32": (
        "%WINDIR%/Fonts",
        "%LOCALAPPDATA%/Microsoft/Windows/Fonts",
    ),
    "darwin": (
        "/System/Library/Fonts",
        "/Library/Fonts",
        "~/Library/Fonts",
    ),
}

_cache = None


def _platform_key():
    if sys.platform.startswith("win"):
        return "win32"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def _expand(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def _read_names(path):
    """The font's own family/style, via freetype's name table. Returns
    (family, style) with a filename-derived family as the last resort -
    a font with no usable name table is still selectable, it just shows
    as its filename instead of vanishing from the picker."""
    try:
        face = freetype.Face(path)
        family = (face.family_name or b"").decode("utf-8", errors="replace").strip()
        style = (face.style_name or b"").decode("utf-8", errors="replace").strip()
    except Exception:
        return os.path.splitext(os.path.basename(path))[0], ""
    if not family:
        family = os.path.splitext(os.path.basename(path))[0]
    return family, style


def _fc_list_fonts():
    """fontconfig's view of every installed font. Returns None (not an
    empty list) when fc-list can't be run at all, so the caller can tell
    "no fontconfig here, fall back to a directory scan" apart from
    "fontconfig ran and genuinely reports nothing"."""
    try:
        out = subprocess.run(
            ["fc-list", "--format", "%{file}\\t%{family}\\t%{style}\\n"],
            capture_output=True, text=True, timeout=30, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    entries = []
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        path = parts[0]
        # fontconfig returns COMMA-SEPARATED alternates for both fields
        # (localized names, and the "Foo Condensed,Foo Condensed Thin"
        # family/subfamily split of a large family) - the first is the
        # primary name, the rest are aliases nobody needs to see here.
        family = parts[1].split(",")[0].strip() if len(parts) > 1 else ""
        style = parts[2].split(",")[0].strip() if len(parts) > 2 else ""
        entries.append((path, family, style))
    return entries


def _scan_dirs_fonts(dirs):
    """Recursive directory scan - the Windows path, and Linux's fallback
    when fc-list is missing. Names come from freetype since there's no
    fontconfig to ask."""
    entries = []
    for d in dirs:
        root = _expand(d)
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                if not name.lower().endswith(FONT_EXTS):
                    continue
                path = os.path.join(dirpath, name)
                family, style = _read_names(path)
                entries.append((path, family, style))
    return entries


def list_system_fonts(extra_paths=(), refresh=False):
    """Every installed font this machine can offer, sorted by family then
    style, one FontEntry per file.

    extra_paths: additional font FILES to fold in (not directories) -
    tune.py passes whatever path the config currently holds, so a font
    that lives outside any installed location (a one-off file picked with
    the File button) still shows up in the picker as the current
    selection instead of silently missing from the list. Not cached with
    the rest, so a changed current-font is always reflected."""
    global _cache
    if _cache is None or refresh:
        raw = None
        if _platform_key() == "linux":
            raw = _fc_list_fonts()
        if raw is None:
            raw = _scan_dirs_fonts(_FALLBACK_FONT_DIRS[_platform_key()])
        _cache = _dedupe(raw)
    entries = dict((e.path, e) for e in _cache)
    for path in extra_paths:
        if not path:
            continue
        path = _expand(path)
        if path in entries or not os.path.isfile(path):
            continue
        family, style = _read_names(path)
        entries[path] = FontEntry(path, family, style)
    return _sorted(entries.values())


def _dedupe(raw):
    """One entry per path (see module docstring - .ttc collections are
    reported once per face by fontconfig), extension-filtered to what the
    pipeline can load."""
    by_path = {}
    for path, family, style in raw:
        if not path.lower().endswith(FONT_EXTS):
            continue
        path = _expand(path)
        if path in by_path:
            continue
        if not family:
            family = os.path.splitext(os.path.basename(path))[0]
        by_path[path] = FontEntry(path, family, style)
    return _sorted(by_path.values())


def _sorted(entries):
    return sorted(entries, key=lambda e: (e.family.lower(), e.style.lower(), e.path))


def display_name(entry):
    """"Family Style" as one string, with the near-universal "Regular"
    style suppressed - matches the "Currently selected: ..." label
    tune.py already shows under every font path field
    (_font_display_name), so the picker and that label read the same."""
    if entry.style and entry.style.lower() != "regular":
        return f"{entry.family} {entry.style}"
    return entry.family


if __name__ == "__main__":
    # Quick check that enumeration works on a given machine - not part of
    # any build path (nothing in generate.py/tune.py's build pipeline
    # calls this file's __main__), just `python3 lib/system_fonts.py`.
    fonts = list_system_fonts()
    print(f"{len(fonts)} installed fonts ({_platform_key()})")
    for e in fonts[:20]:
        print(f"  {display_name(e)}  <-  {e.path}")
