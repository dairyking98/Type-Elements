"""Locate a usable f3d binary: one already on PATH, a previously
bootstrapped copy, or a freshly downloaded pinned release build.

Order of preference (see v4/PACKAGING_PLAN.md phase 2 for the
shippable-app context this exists for): a system-installed f3d on PATH
wins if present (even if its version doesn't match PINNED_VERSION - just
warn, since v4's --watch/set_camera usage is simple enough that minor
version drift is very unlikely to actually break it), then a copy this
module already downloaded and cached, then a fresh download of the
pinned release asset for the current OS.

Only Linux and Windows x86_64 have a pinned asset today - f3d ships
macOS builds only as .dmg (no plain archive to extract without invoking
platform-specific mount tooling), so macOS always falls through to
"install f3d yourself" until that's actually needed.
"""

import hashlib
import os
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import urllib.request
import zipfile

PINNED_VERSION = "3.5.0"
_RELEASE_BASE = f"https://github.com/f3d-app/f3d/releases/download/v{PINNED_VERSION}"

# system -> (release asset filename, its sha256, path to the f3d
# executable inside the extracted archive)
_ASSETS = {
    "Linux": (
        f"F3D-{PINNED_VERSION}-Linux-x86_64.tar.gz",
        "3e4590c709e6ecd14ec3088527dd625f1ed79b970009eb3a4baef9b410650f10",
        f"F3D-{PINNED_VERSION}-Linux-x86_64/bin/f3d",
    ),
    "Windows": (
        f"F3D-{PINNED_VERSION}-Windows-x86_64.zip",
        "db57f9fb7e1bbe2c022ec19dab3fd1eb38545f8c7b3d29d3906a951936a2e897",
        f"F3D-{PINNED_VERSION}-Windows-x86_64/bin/f3d.exe",
    ),
}

# Dev-mode cache location, repo-relative like tune.py's own REPO_ROOT
# joins. Frozen/packaged mode (next to the exe) is app_paths.py's job
# (PACKAGING_PLAN.md phase 1, not yet built) to redirect this to.
_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "f3d_cache")

_VERSION_RE = re.compile(r"^F3D (\d+\.\d+\.\d+)")


def _default_log(msg):
    print(msg)


def _system_f3d(log):
    path = shutil.which("f3d")
    if path is None:
        return None
    try:
        out = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return path  # found it; couldn't probe its version, use it anyway
    match = _VERSION_RE.search(out)
    version = match.group(1) if match else None
    if version != PINNED_VERSION:
        log(f"[yellow]using system f3d {version or '(unknown version)'} on PATH "
            f"(tested against {PINNED_VERSION}) - camera/CLI behavior may differ[/yellow]")
    return path


def _cached_f3d(system):
    if system not in _ASSETS:
        return None
    _, _, exe_rel = _ASSETS[system]
    candidate = os.path.join(_CACHE_DIR, PINNED_VERSION, *exe_rel.split("/"))
    return candidate if os.path.isfile(candidate) else None


def _download_and_extract(system, log):
    if system not in _ASSETS or platform.machine().lower() not in ("x86_64", "amd64"):
        raise RuntimeError(
            f"no bootstrap-able f3d build for {system}/{platform.machine()} yet "
            "(only Linux/Windows x86_64 are pinned) - install f3d yourself and put it on PATH")

    asset_name, sha256, exe_rel = _ASSETS[system]
    version_dir = os.path.join(_CACHE_DIR, PINNED_VERSION)
    os.makedirs(version_dir, exist_ok=True)
    archive_path = os.path.join(version_dir, asset_name)

    log(f"[cyan]downloading f3d {PINNED_VERSION} ({asset_name})...[/cyan]")
    with urllib.request.urlopen(f"{_RELEASE_BASE}/{asset_name}") as resp, open(archive_path, "wb") as f:
        shutil.copyfileobj(resp, f)

    digest = hashlib.sha256()
    with open(archive_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    if digest.hexdigest() != sha256:
        os.remove(archive_path)
        raise RuntimeError(f"f3d download checksum mismatch for {asset_name} - aborting")

    log(f"[cyan]extracting {asset_name}...[/cyan]")
    if asset_name.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as z:
            z.extractall(version_dir)
    else:
        with tarfile.open(archive_path) as t:
            t.extractall(version_dir, filter="data")
    os.remove(archive_path)

    exe_path = os.path.join(version_dir, *exe_rel.split("/"))
    if system != "Windows":
        st = os.stat(exe_path)
        os.chmod(exe_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    log(f"[green]f3d {PINNED_VERSION} ready at {exe_path}[/green]")
    return exe_path


def ensure_f3d_path(log=_default_log):
    """Return a path to a runnable f3d binary, preferring PATH, then a
    previously bootstrapped copy, then a fresh pinned-release download.
    Raises RuntimeError if none of those are possible."""
    system = platform.system()

    system_path = _system_f3d(log)
    if system_path is not None:
        return system_path

    cached = _cached_f3d(system)
    if cached is not None:
        return cached

    return _download_and_extract(system, log)
