// The in-browser engine: Pyodide running v4 + engine_core in this Web Worker,
// so the page stays responsive while it builds. Talks to engine_browser.js
// with messages:
//   page -> worker  {type:"init", base}            boot, base = URL of the bundle (_engine/engine.pack)
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
const STOPPED_FOR_POOL = 99;   // webengine.STOPPED_FOR_POOL: pass 1 stopped after the characters
const ONE_PASS = "--- every draft angle came from the cache";   // webengine.pool_record prints it mid-run
const MUTATING = new Set(["put_config", "reset_config", "open_config", "add_font", "profile_save", "profile_rename", "profile_delete"]);
const status = (text, progress) => postMessage({ type: "status", text, progress });

// trimesh isn't in Pyodide's own package set; a pinned wheel URL (rather than
// letting micropip ask PyPI which file to get) keeps every boot cacheable.
const TRIMESH = "https://files.pythonhosted.org/packages/05/98/716a473cfb24750858ddd5d14e6527539dd206583a46408d08eeb2844a75/trimesh-4.12.2-py3-none-any.whl";

// engine.pack (make_bundle.py): Type Elements' files in one request. The
// deploy stamps this worker with ?v=<version>, so the pack URL changes with
// every deploy and can come from the browser cache otherwise.
function fetchPack(base) {
  const v = new URL(import.meta.url).searchParams.get("v");
  return fetch(new URL("engine.pack" + (v ? `?v=${v}` : ""), base), v ? {} : { cache: "no-cache" }).then((r) => {
    if (!r.ok) throw new Error(`engine.pack: HTTP ${r.status}`);
    return r.arrayBuffer();
  });
}

function unpack(buf) {
  const n = new DataView(buf).getUint32(0, true);
  const index = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 4, n)));
  let at = 4 + n;
  for (const [dest, size] of index) {
    py.FS.mkdirTree(dest.slice(0, dest.lastIndexOf("/")) || "/");
    py.FS.writeFile(dest, new Uint8Array(buf, at, size));
    at += size;
  }
}

async function init(b) {
  base = b;
  const t0 = performance.now();
  // everything that only waits on the network starts at once
  const pack = fetchPack(base);
  pack.catch(() => {});   // reported where it's awaited
  const geometry = Module().then((wasm) => { wasm.setup(); globalThis.__manifold = wasm; });
  status("Starting Python…", 0.1);
  py = await loadPyodide();
  status("Loading Python libraries…", 0.2);
  await py.loadPackage(["numpy", "scipy", "shapely", "pyyaml", "fonttools", "networkx", "micropip"]);
  await py.runPythonAsync(`import micropip\nawait micropip.install("${TRIMESH}")`);
  status("Loading Type Elements…", 0.5);
  await geometry;
  unpack(await pack);
  py.FS.mkdirTree("/persist");
  py.FS.mount(py.FS.filesystems.IDBFS, {}, "/persist");
  await syncfs(true);
  // (the built-in font profiles are read from /v4/config/profiles in place)
  py.runPython(`
import sys
sys.path[:0] = ["/shim", "/v5", "/v4/lib", "/v4"]
`);
  status("Starting Type Elements…", 0.6);
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
    if (method === "add_font" || method === "add_synced_font") {
      raw = eng[method](args[0], py.toPy(new Uint8Array(args[1])));
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
      for (const line of parts) {
        // pass 1 found every draft angle cached, so it is the whole render:
        // from here on it's assembly (share 0 = no loop; progress.js)
        if (line.startsWith(ONE_PASS)) postMessage({ id, phase: [0.17, 1, "one pass: assembling", 0] });
        postMessage({ id, line });
      }
      if (buf) postMessage({ id, partial: buf });
      return bytes.length;
    },
  });
  py.setStderr({ write: (bytes) => { postMessage({ id, line: dec.decode(bytes) }); return bytes.length; } });
  return () => { if (buf) postMessage({ id, line: buf }); buf = ""; };
}

async function minkowskiPool(jobs, n, id) {
  const workers = Array.from({ length: n }, () => new Worker(new URL("minkowski_worker.js?v=041952ef47", import.meta.url), { type: "module" }));
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
    const usePool = spec.result.pool && workers > 1;   // webengine.job_argv: a build with real draft angles
    if (!usePool) {
      rc = eng.run_job(toPyList(argv));
    } else {
      // Pass 1 builds with each draft-angle (Minkowski) sum taken from the
      // cache or recorded, and stops once the characters are placed. If
      // every sum was cached it simply finishes: that IS the render. Else
      // the recorded sums go to the worker pool and pass 2 builds for real.
      // One job, up to three stages - slices of one progress bar
      // (phase = [start, end, label, share]) rather than bars that each
      // refill; share = how much of the slice its [n/N] loop is (progress.js).
      // The slices are measured, not guessed: a Hammond render spent 11% in
      // pass 1, 13% in the pool, then 14% replaying the characters and 62%
      // assembling.
      eng.pool_record(spec.result.glyph_loops || 1);
      postMessage({ id, phase: [0, 0.12, "placing characters (1 of 3)", 1] });
      postMessage({ id, line: "--- pass 1: placing characters; draft angles cached or recorded for the worker pool" });
      rc = eng.run_job(toPyList(argv));
      const recorded = rc === 0 || rc === STOPPED_FOR_POOL ? eng.pool_jobs().toJs() : [];
      if (recorded.length) {
        const jobs = recorded.map(([gv, gf, cv, cf]) => ({ gv: gv.buffer, gf: gf.buffer, cv: cv.buffer, cf: cf.buffer, weight: gf.byteLength }));
        const t = performance.now();
        postMessage({ id, phase: [0.12, 0.27, `draft angles on ${workers} workers (2 of 3)`, 1] });
        const results = await minkowskiPool(jobs, workers, id);
        postMessage({ id, line: `--- ${jobs.length} Minkowski sums on ${workers} workers in ${((performance.now() - t) / 1000).toFixed(1)}s` });
        eng.pool_replay(py.toPy(results.map((r) => [new Uint8Array(r.v), new Uint8Array(r.f)])));
        postMessage({ id, phase: [0.27, 1, "assembling (3 of 3)", 0.17] });
        postMessage({ id, line: "--- pass 2: building with the pool's results" });
        rc = eng.run_job(toPyList(argv));
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
      if (kind === "build" && body.target === "calibration") take("mapping", stl.replace(/\.stl$/i, "") + "_mapping.txt");
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
