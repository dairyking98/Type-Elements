// The in-browser engine: Pyodide running v4 + engine_core in this Web Worker,
// so the page stays responsive while it builds. Talks to engine_browser.js
// with messages:
//   page -> worker  {type:"init", base}            boot, base = URL of the bundle (_engine/)
//                   {type:"call", id, method, args}  one engine call (JSON in, JSON out)
//                   {type:"job", id, kind, machine, body, workers}   build / tool, streamed
//   worker -> page  {type:"status", text, progress}  boot progress
//                   {type:"ready", seconds}
//                   {id, result} | {id, error}       call result
//                   {id, line} | {id, partial}       job output, then {id, done, files}
// User state (running configs, profiles, added fonts) lives in /persist, an
// IndexedDB-backed folder synced after every change.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";
import Module from "https://cdn.jsdelivr.net/npm/manifold-3d@3.5.4/manifold.js";

let py, eng, base;
const MUTATING = new Set(["put_config", "reset_config", "open_config", "add_font", "profile_save", "profile_rename", "profile_delete"]);
const status = (text, progress) => postMessage({ type: "status", text, progress });

async function init(b) {
  base = b;
  const t0 = performance.now();
  status("Loading the geometry engine…", 0.05);
  const wasm = await Module();
  wasm.setup();
  globalThis.__manifold = wasm;
  status("Loading Python…", 0.15);
  py = await loadPyodide();
  status("Loading Python libraries…", 0.35);
  await py.loadPackage(["numpy", "scipy", "shapely", "pyyaml", "fonttools", "networkx", "micropip"]);
  await py.runPythonAsync(`import micropip\nawait micropip.install("trimesh==4.12.2")`);
  status("Loading Type Elements…", 0.7);
  const man = await (await fetch(new URL("manifest.json", base), { cache: "no-cache" })).json();
  await Promise.all(man.files.map(async (dest) => {
    const buf = new Uint8Array(await (await fetch(new URL(dest.slice(1), base), { cache: "no-cache" })).arrayBuffer());
    py.FS.mkdirTree(dest.slice(0, dest.lastIndexOf("/")) || "/");
    py.FS.writeFile(dest, buf);
  }));
  py.FS.mkdirTree("/persist");
  py.FS.mount(py.FS.filesystems.IDBFS, {}, "/persist");
  await syncfs(true);
  // first visit: seed the font profiles that ship with v4
  py.runPython(`
import os, shutil, sys
sys.path[:0] = ["/shim", "/v5", "/v4/lib", "/v4"]
if not os.path.isdir("/persist/profiles") and os.path.isdir("/persist-seed/profiles"):
    shutil.copytree("/persist-seed/profiles", "/persist/profiles")
`);
  status("Starting…", 0.92);
  eng = py.pyimport("webengine");
  await syncfs(false);
  postMessage({ type: "ready", seconds: (performance.now() - t0) / 1000 });
}

const syncfs = (populate) => new Promise((res, rej) => py.FS.syncfs(populate, (e) => (e ? rej(e) : res())));

async function call({ id, method, args }) {
  try {
    if (method === "font_bytes") {
      const data = eng.font_bytes(args[0]).toJs();
      return postMessage({ id, result: data }, [data.buffer]);
    }
    let raw;
    if (method === "add_font") {
      raw = eng.add_font(args[0], py.toPy(new Uint8Array(args[1])));
      raw = JSON.stringify({ result: raw.toJs({ dict_converter: Object.fromEntries }) });
    } else {
      raw = eng.call(method, JSON.stringify(args || []));
    }
    const msg = JSON.parse(raw);
    if (MUTATING.has(method) && !msg.error) await syncfs(false);
    postMessage({ id, ...msg });
  } catch (e) {
    postMessage({ id, error: { status: 500, detail: String(e.message || e) } });
  }
}

// stdout from v4's scripts -> page, line by line; an unterminated line
// (build_log.progress_start) goes out as `partial` so progress bars move.
function captureOutput(id) {
  let buf = "";
  const dec = new TextDecoder();
  py.setStdout({
    write: (bytes) => {
      buf += dec.decode(bytes, { stream: true });
      const parts = buf.split("\n");
      buf = parts.pop();
      for (const line of parts) postMessage({ id, line });
      if (buf) postMessage({ id, partial: buf });
      return bytes.length;
    },
  });
  py.setStderr({ write: (bytes) => { postMessage({ id, line: dec.decode(bytes) }); return bytes.length; } });
  return () => { if (buf) postMessage({ id, line: buf }); buf = ""; };
}

async function minkowskiPool(jobs, n, id) {
  const workers = Array.from({ length: n }, () => new Worker(new URL("minkowski_worker.js?v=47d1df6d5d", import.meta.url), { type: "module" }));
  const queue = jobs.map((j, i) => ({ i, ...j })).sort((a, b) => b.weight - a.weight);
  const out = new Array(jobs.length);
  let done = 0;
  await Promise.all(workers.map((w) => new Promise((resolve, reject) => {
    w.onerror = (e) => reject(new Error(e.message || "Minkowski worker failed"));
    const next = () => {
      const job = queue.shift();
      if (!job) return resolve();
      w.onmessage = ({ data }) => {
        out[data.i] = data;
        done++;
        postMessage({ id, partial: `Minkowski sums on ${n} workers: [${done}/${jobs.length}]` });
        next();
      };
      w.postMessage({ i: job.i, gv: job.gv, gf: job.gf, cv: job.cv, cf: job.cf }, [job.gv, job.gf, job.cv, job.cf]);
    };
    next();
  })));
  workers.forEach((w) => w.terminate());
  return out;
}

async function job({ id, kind, machine, body, workers }) {
  const flush = captureOutput(id);
  let rc = 1;
  try {
    const spec = JSON.parse(eng.call("job_argv", JSON.stringify([kind, machine, body])));
    if (spec.error) throw new Error(spec.error.detail);
    const { argv, stl, legend, report } = spec.result;
    postMessage({ id, line: "$ " + argv.join(" ") });
    const toPyList = (a) => py.toPy(a);
    const usePool = kind === "build" && !body.fast && workers > 1 && ["element", "calibration", "normal"].includes(body.target || "element")
      && !body.cut_bodies;
    if (!usePool) {
      rc = eng.run_job(toPyList(argv));
    } else {
      // pass 1: build with every Minkowski sum recorded, not computed
      // One job, three stages - report them as slices of one progress bar
      // (phase = [start, end, label]) instead of three bars that each refill.
      eng.pool_record();
      postMessage({ id, phase: [0, 0.25, "building (1 of 3)"] });
      postMessage({ id, line: "--- pass 1: building, Minkowski sums recorded for the worker pool" });
      rc = eng.run_job(toPyList(argv));
      if (rc === 0) {
        const recorded = eng.pool_jobs().toJs();
        const jobs = recorded.map(([gv, gf, cv, cf]) => ({ gv: gv.buffer, gf: gf.buffer, cv: cv.buffer, cf: cf.buffer, weight: gf.byteLength }));
        if (jobs.length) {
          const t = performance.now();
          postMessage({ id, phase: [0.25, 0.75, `draft angles on ${workers} workers (2 of 3)`] });
          const results = await minkowskiPool(jobs, workers, id);
          postMessage({ id, line: `--- ${jobs.length} Minkowski sums on ${workers} workers in ${((performance.now() - t) / 1000).toFixed(1)}s` });
          eng.pool_replay(py.toPy(results.map((r) => [new Uint8Array(r.v), new Uint8Array(r.f)])));
          postMessage({ id, phase: [0.75, 1, "assembling (3 of 3)"] });
          postMessage({ id, line: "--- pass 2: building with the pool's results" });
          rc = eng.run_job(toPyList(argv));
        }
      }
      eng.pool_clear();
    }
    flush();
    const files = {};
    const take = (key, path) => {
      try {
        const data = py.FS.readFile(path);
        files[key] = data.buffer;
      } catch {}
    };
    if (rc === 0) {
      if (kind === "build" || body.tool === "type_test") take("stl", stl);
      if (body.tool === "legend") take("legend", legend);
      if (String(body.tool).startsWith("coverage")) take("report", report);
    }
    postMessage({ id, done: rc, files }, Object.values(files));
  } catch (e) {
    flush();
    try { eng.pool_clear(); } catch {}
    postMessage({ id, line: String(e.message || e) });
    postMessage({ id, done: rc || 1, files: {} });
  }
}

let queue = Promise.resolve();
onmessage = ({ data }) => {
  if (data.type === "init") {
    queue = queue.then(() => init(data.base)).catch((e) => postMessage({ type: "failed", detail: String(e.message || e) }));
    return;
  }
  // one thing at a time: Pyodide is single-threaded
  queue = queue.then(() => (data.type === "job" ? job(data) : call(data)));
};
