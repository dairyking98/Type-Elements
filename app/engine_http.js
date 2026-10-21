// The LOCAL engine: v5/server.py over HTTP (see ENGINE_API.md). Same methods
// as engine_browser.js; engine.js picks which one the app uses.
//
// Where the engine is: when this page is served BY the engine (/app/ on
// the local server), same origin. When it's hosted elsewhere - the GitHub
// Pages copy at type-elements.leonardchau.com/app/ - it talks to an engine
// on the visitor's own computer, http://127.0.0.1:8090 unless they changed
// it (stored per browser).
const sameOrigin = location.protocol === "http:";   // the local server is plain http; the hosted copy is always https
export const DEFAULT_ENGINE = "http://127.0.0.1:8090";
let BASE = safeGet("te.engine") ?? (sameOrigin ? "" : DEFAULT_ENGINE);   // an address the user typed always wins
function safeGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
const api = (path) => BASE + path;

async function json(res) {
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const httpEngine = {
  kind: "local",
  label: "Local engine",
  get base() { return BASE || location.origin; },
  hosted: BASE !== "",
  setBase(url) { BASE = url.replace(/\/+$/, ""); try { localStorage.setItem("te.engine", BASE); } catch {} },
  ping: () => fetch(api("/api/machines"), { cache: "no-store" }).then((r) => r.ok),

  machines: () => fetch(api("/api/machines")).then(json),
  config: (m) => fetch(api(`/api/config/${m}`)).then(json),
  save: (m, body) => fetch(api(`/api/config/${m}`), {
    method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }).then(json),
  configs: (m) => fetch(api(`/api/configs/${m}`)).then(json),
  openConfig: (m, path) => post(api(`/api/config/${m}/open`), { path }),
  reset: (m) => fetch(api(`/api/config/${m}/reset`), { method: "POST" }).then(json),
  fonts: () => fetch(api("/api/fonts")).then(json),
  fontUrl: (path) => api(`/api/font?path=${encodeURIComponent(path)}`),
  outlines: (font, chars) => post(api("/api/outlines"), { font, chars }),
  glyphs: (body) => fetch(api("/api/glyphs"), {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }).then(json),
  stlUrl: (m) => api(`/api/stl/${m}?t=${Date.now()}`),
  legendUrl: (m, t) => api(`/api/legend/${m}?t=${t}`),
  reportUrl: () => api(`/api/coverage-report?t=${Date.now()}`),
  cancel: () => fetch(api("/api/build-cancel"), { method: "POST" }).then(json),
  defaultFontDir: () => fetch(api("/api/default-font-dir")).then(json).then((r) => r.path),
  saveCopy: (m, body) => post(api(`/api/save-copy/${m}`), body),
  settingsFile: (m, body) => post(api(`/api/settings-file/${m}`), body),
  coverageScan: (body) => post(api("/api/coverage-scan"), body),
  importSettings: (text) => post(api("/api/import-settings"), { text }),
  mappingUrl: (m) => api(`/api/mapping/${m}?t=${Date.now()}`),   // 404 unless the last build was a calibration
  resolveFont: (path) => Promise.resolve({ path, kind: "same" }),   // the local engine reads the disk directly
  profiles: (m) => fetch(api(`/api/profiles/${m}`)).then(json),
  saveProfile: (m, name) => post(api(`/api/profiles/${m}`), { name }),
  renameProfile: (m, old_, new_) => post(api(`/api/profiles/${m}/rename`), { old: old_, new: new_ }),
  deleteProfile: (m, name) => post(api(`/api/profiles/${m}/delete`), { name }),
  build: (m, opts, onEvent) => stream(api(`/api/build/${m}`), opts, onEvent),
  tool: (m, body, onEvent) => stream(api(`/api/tool/${m}`), body, onEvent),
};

function post(url, body) {
  return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(json);
}

// Streams a job's output: onEvent({line}|{partial}|{done}) per NDJSON record.
async function stream(url, body, onEvent) {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n");
    buf = parts.pop();
    for (const p of parts) if (p.trim()) onEvent(JSON.parse(p));
  }
  if (buf.trim()) onEvent(JSON.parse(buf));
}
