#!/usr/bin/env python3
"""
Type Elements v5 - local engine server.

v5 splits the program in two:

  * the ENGINE - v4's geometry pipeline (generate.py and friends, untouched)
    behind the JSON API documented in ENGINE_API.md;
  * the UI - any static web front end (default: v5/ui/) that talks only to
    that API. Swap it with --ui to try a completely different interface
    without touching a line of geometry.

    v4/.venv/bin/python3 v5/server.py --open                 # http://127.0.0.1:8090
    v4/.venv/bin/python3 v5/server.py --ui path/to/my-ui     # someone else's front end
    v4/.venv/bin/python3 v5/server.py --config-dir DIR       # scratch configs for testing

This file is only the HTTP layer: routes, CORS, and running jobs as
subprocesses with live output. What every endpoint actually does lives in
engine_core.py, which the in-browser engine (Pyodide in a Web Worker) runs
too - so the two engines can't drift apart. Localhost-only unless --host
says otherwise.
"""

import argparse
import asyncio
import json
import os
import sys
from types import SimpleNamespace

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import engine_core as core
from engine_core import EngineError

V5 = os.path.dirname(os.path.abspath(__file__))
DEFAULT_UI = os.path.join(V5, "ui")
# The hosted UI (GitHub Pages) may call this local engine from another origin.
# Only those origins are allowed; allow_private_network answers Chrome's
# Private/Local Network Access preflight for a public page reaching 127.0.0.1.
HOSTED_UI_ORIGINS = ["https://type-elements.leonardchau.com", "https://dairyking98.github.io"]

app = FastAPI(title="Type Elements engine")
BUILD = SimpleNamespace(proc=None)


@app.exception_handler(EngineError)
def engine_error(_request: Request, e: EngineError):
    return JSONResponse({"detail": e.detail}, status_code=e.status)


# ------------------------------------------------------------------ config

@app.get("/api/machines")
def machines():
    return core.machines()


@app.get("/api/config/{machine}")
def get_config(machine):
    return core.get_config(machine)


@app.put("/api/config/{machine}")
def put_config(machine, body: dict = Body(...)):
    return core.put_config(machine, body)


@app.post("/api/config/{machine}/reset")
def reset_config(machine):
    return core.reset_config(machine)


@app.get("/api/configs/{machine}")
def list_configs(machine):
    return core.list_configs(machine)


@app.post("/api/config/{machine}/open")
def open_config(machine, body: dict = Body(...)):
    return core.open_config(machine, body)


# ------------------------------------------------------------------ fonts

@app.get("/api/fonts")
def fonts():
    return core.fonts()


@app.post("/api/coverage-scan")
def coverage_scan(body: dict = Body(...)):
    return core.coverage_scan(body)


@app.get("/api/default-font-dir")
def default_dir():
    return core.default_dir()


@app.get("/api/font")
def font_file(path: str):
    if not core.allowed_font(path):
        raise HTTPException(404, "font not available")
    # Vary: Origin - the same file is fetched same-origin (local UI) and
    # cross-origin (hosted UI); without it the browser can reuse a cached
    # copy that lacks the CORS header and the font fails to load.
    return FileResponse(os.path.abspath(os.path.expanduser(path)), headers={"Vary": "Origin"})


@app.post("/api/outlines")
def outlines(body: dict = Body(...)):
    return core.outlines(body)


@app.post("/api/glyphs")
def glyphs(body: dict = Body(...)):
    return core.glyphs(body)


# ------------------------------------------------------------------ jobs

def run_streamed(cmd):
    """Runs one subprocess (generate.py, type_test.py, generate_legend.py,
    font_coverage.py) and streams its output as NDJSON lines ({"line": ...},
    {"partial": ...} for an unterminated progress line, then {"done": rc})."""
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")

    async def stream():
        yield json.dumps({"line": "$ " + " ".join(os.path.basename(c) if i < 2 else c
                                                    for i, c in enumerate(cmd))}) + "\n"
        BUILD.proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=core.V4, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
        buf = b""
        while True:
            chunk = await BUILD.proc.stdout.read(4096)
            if not chunk:
                break
            buf += chunk
            *lines, buf = buf.split(b"\n")
            for raw in lines:
                yield json.dumps({"line": raw.decode("utf-8", errors="replace")}) + "\n"
            if buf:  # progress_start() prints without a newline - surface the partial line too
                yield json.dumps({"partial": buf.decode("utf-8", errors="replace")}) + "\n"
        if buf:
            yield json.dumps({"line": buf.decode("utf-8", errors="replace")}) + "\n"
        rc = await BUILD.proc.wait()
        yield json.dumps({"done": rc}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/api/build/{machine}")
async def build(machine, body: dict = Body(...)):
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")
    return run_streamed(core.build_command(machine, body))


@app.post("/api/tool/{machine}")
async def tool(machine, body: dict = Body(...)):
    if BUILD.proc and BUILD.proc.returncode is None:
        raise HTTPException(409, "a job is already running")
    return run_streamed(core.tool_command(machine, body))


@app.post("/api/build-cancel")
def cancel():
    if BUILD.proc and BUILD.proc.returncode is None:
        BUILD.proc.terminate()
        return {"cancelled": True}
    return {"cancelled": False}


@app.get("/api/stl/{machine}")
def stl(machine):
    path = core.stl_path(machine)
    return FileResponse(path, media_type="model/stl", filename=os.path.basename(path))


@app.get("/api/mapping/{machine}")
def mapping(machine):
    path = core.mapping_path(machine)
    return FileResponse(path, media_type="text/plain", filename=os.path.basename(path))


@app.get("/api/legend/{machine}")
def legend_svg(machine):
    path = core.legend_path(machine)
    return FileResponse(path, media_type="image/svg+xml", filename=os.path.basename(path))


@app.get("/api/coverage-report")
def coverage_report():
    if not os.path.isfile(core.COVERAGE_REPORT):
        raise HTTPException(404, "no report yet")
    return FileResponse(core.COVERAGE_REPORT, media_type="text/markdown", filename="font_coverage_report.md")


@app.post("/api/save-copy/{machine}")
def save_copy(machine, body: dict = Body(default={})):
    return core.save_copy(machine, body)



@app.post("/api/settings-file/{machine}")
def settings_file(machine, body: dict = Body(default={})):
    return core.settings_file(machine, body)


@app.post("/api/import-settings")
def import_settings(body: dict = Body(...)):
    return core.import_settings(body)


# ------------------------------------------------------------------ font profiles

@app.get("/api/profiles/{machine}")
def profiles(machine):
    return core.profiles(machine)


@app.post("/api/profiles/{machine}")
def profile_save(machine, body: dict = Body(...)):
    return core.profile_save(machine, body)


@app.post("/api/profiles/{machine}/rename")
def profile_rename(machine, body: dict = Body(...)):
    return core.profile_rename(machine, body)


@app.post("/api/profiles/{machine}/delete")
def profile_delete(machine, body: dict = Body(...)):
    return core.profile_delete(machine, body)


@app.get("/")
def root():
    return RedirectResponse("/app/")


def main():
    p = argparse.ArgumentParser(description="Type Elements local engine + web UI")
    p.add_argument("--config-dir", default=None, help="directory of master configs (default v4/config)")
    p.add_argument("--host", default="127.0.0.1", help="localhost only by default")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--open", action="store_true", help="open the UI in the default browser")
    p.add_argument("--ui", default=DEFAULT_UI,
                   help="directory of the front end to serve (default v5/ui). Any static site that "
                        "speaks ENGINE_API.md works - point this at your own to swap the whole UI.")
    p.add_argument("--allow-origin", action="append", default=[], metavar="URL",
                   help="also let this origin call the API, e.g. http://localhost:5173 for a UI on a "
                        "JS dev server (repeatable). The hosted site is always allowed.")
    args = p.parse_args()
    app.add_middleware(CORSMiddleware, allow_origins=HOSTED_UI_ORIGINS + args.allow_origin, allow_methods=["*"],
                       allow_headers=["*"], allow_private_network=True)
    if not os.path.isfile(os.path.join(args.ui, "index.html")):
        p.error(f"--ui {args.ui!r} has no index.html")
    app.mount("/app", StaticFiles(directory=os.path.abspath(args.ui), html=True), name="ui")
    if args.config_dir:
        core.configure(config_dir=args.config_dir)
    if args.open:
        import threading
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{args.host}:{args.port}/")).start()
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    sys.exit(main())
