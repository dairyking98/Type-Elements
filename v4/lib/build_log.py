"""
Standardized console output AND safe output-file writes for generate.py/
tune.py's build pipeline -
extracted because the pattern was being hand-duplicated with real drift
(some machines' intermediate prints show only `watertight=`, others the
full `verts/faces/watertight/winding_consistent/is_volume/volume` set;
glyph_poc.py had its own unused, differently-formatted report() that
nothing actually called). Two independent conventions, both load-bearing:

- The "[n/total]" progress marker (progress_start/done/skipped) is not
  just cosmetic - tune.py's Build-tab progress bar
  (_update_progress/_PROGRESS_RE in tune.py) parses this literal
  "[digits/digits]" shape out of the subprocess's stdout to drive its
  0-95% range. Any per-character glyph-building loop needs to print this
  for every character or the progress bar just sits at 0% for the whole
  build (see SESSION_LOG.md part 61 for the real bug this caused for
  Hammond Split's own from-scratch TextAssemble()).
- mesh_report() is the one-line "label: verts=... watertight=..." summary
  every machine's Additive()/Subtractive()/ResinSupport()/generate.py's
  final output line already prints by hand - not parsed by tune.py, just
  the CLAUDE.md "hard gate" verification's actual source of truth.

flush=True everywhere - generate.py's stdout is piped (not a TTY) when
run from tune.py's subprocess, which fully block-buffers without it,
silently stalling live progress until the buffer fills or the process
exits (SESSION_LOG.md part 7).

atomic_export() is a third convention living here for the same reason:
every subprocess tune.py drives (generate.py AND type_test.py) writes its
final output mesh to a path tune.py's f3d --watch window may be actively
watching - a plain mesh.export() is not atomic (opens/truncates the
destination directly, then writes), so f3d's own independent filesystem
watcher can catch a 0-byte or partial file mid-write (SESSION_LOG.md
part 61/62).
"""

import os
import tempfile


def atomic_export(mesh, out_path):
    """Write mesh to out_path via a temp file in the SAME directory +
    os.replace() (a same-filesystem rename, atomic on POSIX) instead of a
    direct mesh.export(out_path) - see module docstring. Every call site
    that writes a final build-pipeline output mesh should use this, not
    a bare .export()."""
    out_dir = os.path.dirname(out_path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".tmp-", suffix=os.path.splitext(out_path)[1])
    os.close(fd)
    try:
        mesh.export(tmp_path)
        os.replace(tmp_path, out_path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def progress_start(prefix, n, total, detail):
    """Prints "prefix: [n/total] detail..." with no trailing newline -
    pair with progress_done()/progress_skipped() to finish the line.
    Matches cylinder_machine.TextRing's original convention exactly, so
    tune.py's _PROGRESS_RE keeps matching regardless of which machine's
    glyph loop is running."""
    print(f"{prefix}: [{n}/{total}] {detail}...", end="", flush=True)


def progress_line(prefix, n, total, detail):
    """One-shot version of progress_start() for loops with no per-item
    timing/skip-on-exception to report (e.g. CalibrationTextRing sweeps,
    which never fail per-character) - a single complete line instead of
    the start/done pair."""
    print(f"{prefix}: [{n}/{total}] {detail}...", flush=True)


def progress_done(elapsed_s):
    print(f" {elapsed_s:.2f}s", flush=True)


def progress_skipped(reason):
    print(f" SKIPPED ({reason})", flush=True)


def progress_summary(prefix, placed, skipped, elapsed_s):
    """skipped: a list of per-item failure records (whatever shape the
    caller wants - just used for its length/repr here), e.g.
    cylinder_machine.TextRing's (row, col, ch, error) tuples."""
    print(f"{prefix}: all characters built in {elapsed_s:.1f}s", flush=True)
    if skipped:
        print(f"{prefix}: placed {placed}, skipped {len(skipped)}: {skipped}", flush=True)


def mesh_report(mesh, label):
    """The standard one-line mesh summary - same fields/order/precision
    generate.py's own final-output line has always used (the CLAUDE.md
    "hard gate" verification's literal source of truth), now shared
    instead of each machine's intermediate Additive()/Subtractive()/
    ResinSupport() prints drifting to a subset of these fields by hand."""
    print(f"{label}: verts={len(mesh.vertices)} faces={len(mesh.faces)} "
          f"watertight={mesh.is_watertight} winding_consistent={mesh.is_winding_consistent} "
          f"is_volume={mesh.is_volume} volume={mesh.volume:.3f}mm3", flush=True)
