// The IN-BROWSER engine: v4 + engine_core running under Pyodide in a Web
// Worker (engine_worker.js), with a pool of Minkowski workers. Nothing is
// installed and nothing leaves this computer. Same methods as engine_http.js
// (the local engine); engine.js picks which one the app uses.
//
// Differences a UI may care about:
//   - first use downloads ~35 MB (cached by the browser afterwards);
//     onStatus(fn) reports boot progress;
//   - fonts are served as bytes (fontData) rather than URLs;
//   - fonts must be added (addFont) - the browser can't see the disk;
//   - results (STL, legend, report) are object URLs held in memory.

const BUNDLE = new URL("_engine/", import.meta.url);
let worker, ready, nextId = 1;
const pending = new Map();      // id -> {resolve, reject} for calls, {onEvent, resolve} for jobs
const urls = { stl: {}, legend: {}, report: null, mapping: {} };
const statusListeners = new Set();
let lastStatus = { text: "Engine not started", progress: 0 };

function boot() {
  if (ready) return ready;
  worker = new Worker(new URL("engine_worker.js?v=d6fd7c4e55", import.meta.url), { type: "module" });
  ready = new Promise((resolve, reject) => {
    worker.onmessage = ({ data }) => {
      if (data.type === "status") { lastStatus = data; statusListeners.forEach((fn) => fn(data)); return; }
      if (data.type === "ready") { lastStatus = { text: `Engine ready (${data.seconds.toFixed(1)} s)`, progress: 1, ready: true }; statusListeners.forEach((fn) => fn(lastStatus)); resolve(); return; }
      if (data.type === "failed") { lastStatus = { text: data.detail, progress: 0, failed: true }; statusListeners.forEach((fn) => fn(lastStatus)); reject(new Error(data.detail)); return; }
      const p = pending.get(data.id);
      if (!p) return;
      if (p.onEvent) {
        if (data.done !== undefined) { pending.delete(data.id); p.resolve(data); }
        else p.onEvent(data);
      } else {
        pending.delete(data.id);
        if (data.error) { const e = new Error(data.error.detail); e.status = data.error.status; p.reject(e); }
        else p.resolve(data.result);
      }
    };
    worker.onerror = (e) => reject(new Error(e.message || "engine worker failed to start"));
  });
  worker.postMessage({ type: "init", base: BUNDLE.href });
  return ready;
}

async function call(method, ...args) {
  await boot();
  const id = nextId++;
  const transfer = args.filter((a) => a instanceof ArrayBuffer);
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    worker.postMessage({ type: "call", id, method, args }, transfer);
  });
}

async function job(kind, machine, body, onEvent) {
  await boot();
  const id = nextId++;
  const workers = Math.max(1, Math.min(16, (navigator.hardwareConcurrency || 4) - 1));
  const res = await new Promise((resolve) => {
    pending.set(id, { onEvent, resolve });
    worker.postMessage({ type: "job", id, kind, machine, body, workers });
  });
  const keep = (bucket, key, buf, type) => {
    if (!buf) return;
    if (key === null) { if (urls.report) URL.revokeObjectURL(urls.report); urls.report = URL.createObjectURL(new Blob([buf], { type })); return; }
    if (urls[bucket][key]) URL.revokeObjectURL(urls[bucket][key]);
    urls[bucket][key] = URL.createObjectURL(new Blob([buf], { type }));
  };
  keep("stl", machine, res.files?.stl, "model/stl");
  keep("legend", machine, res.files?.legend, "image/svg+xml");
  if (kind === "build") {                    // a calibration's position -> value mapping, else none
    if (urls.mapping[machine]) URL.revokeObjectURL(urls.mapping[machine]);
    urls.mapping[machine] = null;
    keep("mapping", machine, res.files?.mapping, "text/plain");
  }
  if (res.files?.report) keep("report", null, res.files.report, "text/markdown");
  onEvent({ done: res.done });
}

export const browserEngine = {
  kind: "browser",
  label: "In this browser",
  hosted: false,                       // nothing to connect to
  get base() { return "this browser"; },
  onStatus(fn) { statusListeners.add(fn); fn(lastStatus); return () => statusListeners.delete(fn); },
  start: boot,
  ping: () => boot().then(() => true),

  machines: () => call("machines"),
  config: (m) => call("get_config", m),
  save: (m, body) => call("put_config", m, body),
  reset: (m) => call("reset_config", m),
  configs: (m) => call("list_configs", m),
  openConfig: (m, path) => call("open_config", m, { path }),
  fonts: () => call("fonts"),
  fontData: (path) => call("font_bytes", path).then((u8) => u8.buffer),
  fontUrl: () => null,
  addFont: (name, buffer) => call("add_font", name, buffer),
  addSyncedFont: (name, buffer) => call("add_synced_font", name, buffer),
  resolveFont: (path) => call("resolve_font", path),
  settingsFile: (m, body) => call("settings_file", m, body),
  importSettings: (text) => call("import_settings", { text }),
  mappingUrl: (m) => urls.mapping[m] || null,
  outlines: (font, chars) => call("outlines", { font, chars }),
  glyphs: (body) => call("glyphs", body),
  defaultFontDir: () => call("default_dir").then((r) => r.path),
  profiles: (m) => call("profiles", m),
  saveProfile: (m, name) => call("profile_save", m, { name }),
  renameProfile: (m, old_, new_) => call("profile_rename", m, { old: old_, new: new_ }),
  deleteProfile: (m, name) => call("profile_delete", m, { name }),

  build: (m, opts, onEvent) => job("build", m, opts, onEvent),
  tool: (m, body, onEvent) => job("tool", m, body, onEvent),
  stlUrl: (m) => urls.stl[m] || null,
  legendUrl: (m) => urls.legend[m] || null,
  reportUrl: () => urls.report,
  async cancel() {
    // Pyodide can't be interrupted mid-build: restart the worker. Saved state
    // is in browser storage, so nothing is lost but the running job.
    worker?.terminate();
    worker = null; ready = null;
    for (const [id, p] of pending) { pending.delete(id); p.onEvent ? p.resolve({ done: -1, files: {} }) : p.reject(new Error("stopped")); }
    boot();
    return { cancelled: true };
  },
  // "Save a copy": in a browser that means downloading it.
  async saveCopy(m, body = {}) {
    const url = urls.stl[m];
    if (!url) throw new Error("nothing built yet");
    const stamp = new Date().toISOString().replace(/[:T]/g, "-").slice(0, 16);
    const a = document.createElement("a");
    a.href = url; a.download = `${body.last_build?.name || `${m}_${stamp}`}.stl`; a.click();
    return { path: `${a.download} (downloaded)` };
  },
};
