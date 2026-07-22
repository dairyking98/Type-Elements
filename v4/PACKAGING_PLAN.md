# Packaging plan: portable single-executable v4 (Linux / Windows / macOS)

Status: **planned, not started.** Revisit when actually ready to begin
packaging work - not a near-term priority as of 2026-07-22.

## Goal

Ship v4 as a single portable executable per platform (Linux binary,
Windows `.exe`, macOS binary/app) that needs no `.venv`/repo checkout to
run. On first launch it creates its own working directories next to the
executable and downloads a pinned `f3d` binary if missing - true
portable/USB-stick semantics, not an installed app scattering files into
OS user-data dirs.

## Current state (why this isn't a small change)

- `tune.py`/`generate.py` resolve `config/`, `output/`,
  `f3d_top_view_cmds.txt` relative to `REPO_ROOT = dirname(__file__)`
  (`tune.py:179`). That assumption breaks the moment the app is a frozen
  single-file exe instead of a checked-out repo.
- `tune.py` shells out to `f3d` assumed present on `$PATH`
  (`tune.py:2631`, `subprocess.Popen(["f3d", "--watch", ...])`).
- `tune.py` drives `generate.py`/`type_test.py` as **separate subprocess
  script files** (`subprocess.Popen([sys.executable, ".../generate.py",
  ...])`, built at `tune.py:2652`/`2764`) with **live async-piped log
  streaming** into the TUI's log pane (`asyncio.create_subprocess_exec`
  at `tune.py:2910-2912`). This is a real feature (live progress in the
  log pane during Render), not incidental - any packaging approach that
  collapses this to an in-process call would need to solve streaming
  output some other way.
- `start.sh` (bash, `.venv`-based) is dev-only; irrelevant to the
  packaged app and doesn't need to change.
- `f3d` (the external viewer, invoked via `f3d --watch`) is
  [BSD-3-Clause](https://github.com/f3d-app/f3d/blob/master/LICENSE.md) -
  no licensing obstacle to redistributing/fetching its binary
  alongside v4; only obligation is including its license text
  somewhere in the distribution.

## Plan, phased so each step is independently verifiable

Each phase should be checked against the CLAUDE.md geometry hard-gate
(`generate.py ... --out /tmp/check.stl`, compare summary line) since
none of this is *supposed* to touch geometry code - if a phase changes
the summary line for any config, that's a regression to chase down.

1. **`lib/app_paths.py`** (new file, not edits to existing modules -
   keeps this refactor additive and easy to back out). Single source of
   truth for where config/output/f3d-cache live.
   - Dev mode: unchanged, repo-relative (today's behavior, via
     `REPO_ROOT`).
   - Frozen mode: everything next to the exe (`./config/`, `./output/`,
     `./f3d/`). On first run, creates those dirs and seeds `config/`
     from the bundled defaults if absent.
   - `tune.py`/`generate.py` swap their raw `REPO_ROOT` joins for calls
     into this module - mechanical call-site edits, not a rewrite.

2. **`lib/f3d_bootstrap.py`** (new file) - checks the cache dir for the
   pinned f3d version; downloads the matching platform asset from a
   pinned GitHub release tag (e.g.
   `https://github.com/f3d-app/f3d/releases/download/vX.Y.Z/...`) if
   missing, verifies it, `chmod +x` on Linux/Mac, returns its path.
   `tune.py`'s hardcoded `"f3d"` becomes `f3d_bootstrap.ensure_f3d_path()`,
   streamed through the existing `log_line()` pane so a first-run
   download isn't silent. Pin to a specific tagged release (not
   "latest") and bump deliberately when choosing to upgrade.

3. **Keep the subprocess architecture - don't collapse it to in-process
   calls**, to preserve live log streaming. Use a **self-re-exec
   sentinel**: the packaged binary's true entry point checks for
   `sys.argv[1] in ("--internal-generate", "--internal-typetest")` and
   dispatches straight to `generate.main()` / a new `type_test.main()`
   before touching Textual, so `tune.py`'s
   `subprocess.Popen([sys.executable, "--internal-generate", ...])`
   keeps working unmodified with no separate script files inside the
   bundle.
   - `generate.py` already has a clean `main()` behind
     `if __name__ == "__main__"` - no change needed there beyond calling
     it.
   - `type_test.py` currently has its argparse logic directly under
     `if __name__ == "__main__"` with no `main()` - needs one extracted
     (trivial mechanical refactor).

4. **PyInstaller, onefile, per-OS.** PyInstaller doesn't cross-compile,
   so use a GitHub Actions build matrix
   (`ubuntu-latest`/`windows-latest`/`macos-latest`); each runner does
   `pip install -r requirements.txt` + PyInstaller, uploads the artifact
   to a GitHub Release on tag push. `f3d` is **not** bundled at build
   time - fetched lazily per phase 2, keeping build artifacts small and
   decoupled from f3d's own release cadence.

5. **Smoke test each platform**: fresh empty directory, run the exe,
   confirm it creates `config/`/`output/`/`f3d/`, downloads f3d, and
   completes a Preview end-to-end.

## Open caveats (not blockers, just known rough edges)

- Unsigned macOS `.app`/binaries get Gatekeeper-quarantined - first run
  needs a right-click-Open, not a blocker unless distributing to
  non-technical users.
- `tune.py`'s `wmctrl -a f3d` window-raise call (`tune.py:2639`) is
  Linux/X11-only; already best-effort/non-fatal (`subprocess.run` to
  `DEVNULL`), so it should degrade gracefully (silently no-op) on
  Windows/Mac without further changes - worth confirming during phase 5
  smoke testing, not assumed.
- Decide at phase 1 time whether `lib/app_paths.py`'s frozen-mode
  detection uses `sys.frozen` (PyInstaller's own flag) vs. some other
  signal - `sys.frozen` is the standard PyInstaller convention and
  should be the default choice absent a reason otherwise.
