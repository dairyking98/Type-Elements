// The engine adapter - the ONLY module that knows where the work happens.
// Today: the local Python server (v5/server.py, see ENGINE_API.md) over HTTP. Later: an
// in-browser engine (Pyodide + manifold WASM in a Web Worker) exposing the
// same methods, so the static UI can be published to GitHub Pages and run
// entirely on the visitor's machine.

async function json(res) {
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const engine = {
  kind: "local server",

  machines: () => fetch("/api/machines").then(json),
  config: (m) => fetch(`/api/config/${m}`).then(json),
  save: (m, body) => fetch(`/api/config/${m}`, {
    method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }).then(json),
  configs: (m) => fetch(`/api/configs/${m}`).then(json),
  openConfig: (m, path) => post(`/api/config/${m}/open`, { path }),
  reset: (m) => fetch(`/api/config/${m}/reset`, { method: "POST" }).then(json),
  fonts: () => fetch("/api/fonts").then(json),
  fontUrl: (path) => `/api/font?path=${encodeURIComponent(path)}`,
  outlines: (font, chars) => post("/api/outlines", { font, chars }),
  glyphs: (body) => fetch("/api/glyphs", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }).then(json),
  stlUrl: (m) => `/api/stl/${m}?t=${Date.now()}`,
  legendUrl: (m, t) => `/api/legend/${m}?t=${t}`,
  reportUrl: () => `/api/coverage-report?t=${Date.now()}`,
  cancel: () => fetch("/api/build-cancel", { method: "POST" }).then(json),
  defaultFontDir: () => fetch("/api/default-font-dir").then(json).then((r) => r.path),
  saveCopy: (m, body) => post(`/api/save-copy/${m}`, body),
  profiles: (m) => fetch(`/api/profiles/${m}`).then(json),
  saveProfile: (m, name) => post(`/api/profiles/${m}`, { name }),
  renameProfile: (m, old_, new_) => post(`/api/profiles/${m}/rename`, { old: old_, new: new_ }),
  deleteProfile: (m, name) => post(`/api/profiles/${m}/delete`, { name }),
  build: (m, opts, onEvent) => stream(`/api/build/${m}`, opts, onEvent),
  tool: (m, body, onEvent) => stream(`/api/tool/${m}`, body, onEvent),
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
