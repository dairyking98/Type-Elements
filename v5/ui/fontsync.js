// A fonts folder on this computer, synced into the in-browser engine.
//
// The user picks the folder once (Chrome/Edge: showDirectoryPicker); its
// handle is kept in this page's IndexedDB and re-read on every visit, so a
// font added to the folder shows up next time with nothing to re-upload.
// Only an index (file name -> handle) lives in the page: a font library is
// too big to copy into browser storage, so a file is handed to the engine
// (engine.addSyncedFont, session only) when something actually needs it -
// it was picked, or a config or profile names it.
//
// The browser asks permission again on a later visit unless the user chose
// "Allow on every visit"; reconnect() must then run from a click.

const DB = "te.fontsync", STORE = "handles", KEY = "folder";
const FONT_RE = /\.(ttf|otf|ttc|otc)$/i;
const MAX_FILES = 20000;

export const supported = typeof window.showDirectoryPicker === "function";

// the same key webengine._font_key makes: "Antikor Mono-Hairline.ttf" == "AntikorMono-Hairline.otf"
export const fontKey = (name) => String(name).split(/[\\/]/).pop().replace(/\.[^.]+$/, "").toLowerCase().replace(/[^a-z0-9]/g, "");

function idb(mode, fn) {
  return new Promise((resolve, reject) => {
    const open = indexedDB.open(DB, 1);
    open.onupgradeneeded = () => open.result.createObjectStore(STORE);
    open.onerror = () => reject(open.error);
    open.onsuccess = () => {
      const tx = open.result.transaction(STORE, mode);
      const req = fn(tx.objectStore(STORE));
      tx.oncomplete = () => resolve(req?.result);
      tx.onerror = () => reject(tx.error);
    };
  });
}

export const state = { name: null, status: "none", files: [], byKey: new Map(), error: "" };
// status: none | needs-permission | scanning | ready | error
const listeners = new Set();
export function onChange(fn) { listeners.add(fn); return () => listeners.delete(fn); }
const changed = () => listeners.forEach((fn) => fn(state));

async function scan(handle) {
  state.status = "scanning"; state.name = handle.name; changed();
  const files = [];
  async function walk(dir, prefix) {
    for await (const [name, h] of dir.entries()) {
      if (files.length >= MAX_FILES) return;
      if (h.kind === "directory") await walk(h, prefix + name + "/");
      else if (FONT_RE.test(name)) files.push({ name, rel: prefix + name, handle: h });
    }
  }
  try {
    await walk(handle, "");
    files.sort((a, b) => a.name.localeCompare(b.name));
    state.files = files;
    state.byKey = new Map(files.map((f) => [fontKey(f.name), f]));
    state.status = "ready"; state.error = "";
  } catch (e) { state.status = "error"; state.error = String(e.message || e); }
  changed();
}

// on startup: re-read the folder if the browser still allows it
export async function restore() {
  if (!supported) return;
  let handle;
  try { handle = await idb("readonly", (s) => s.get(KEY)); } catch { return; }
  if (!handle) return;
  state.name = handle.name;
  const perm = await handle.queryPermission({ mode: "read" }).catch(() => "denied");
  if (perm === "granted") await scan(handle);
  else { state.status = "needs-permission"; changed(); }
}

// from a click: pick a folder (or grant access to the remembered one again)
export async function choose() {
  const handle = await window.showDirectoryPicker({ id: "te-fonts", mode: "read" });
  await idb("readwrite", (s) => s.put(handle, KEY));
  await scan(handle);
}
export async function reconnect() {
  const handle = await idb("readonly", (s) => s.get(KEY));
  if (!handle) return choose();
  if ((await handle.requestPermission({ mode: "read" })) === "granted") await scan(handle);
}
export async function forget() {
  await idb("readwrite", (s) => s.delete(KEY)).catch(() => {});
  Object.assign(state, { name: null, status: "none", files: [], byKey: new Map(), error: "" });
  changed();
}

export const match = (path) => state.byKey.get(fontKey(path)) || null;
export const bytes = async (f) => (await f.handle.getFile()).arrayBuffer();

// Hand a synced font to the engine; returns its engine path. Cached per
// session (the engine keeps the copy until the tab closes).
const sent = new Map();
export async function provide(engine, f) {
  if (!sent.has(f.rel)) sent.set(f.rel, bytes(f).then((buf) => engine.addSyncedFont(f.name, buf)).then((r) => r.path));
  try { return await sent.get(f.rel); } catch (e) { sent.delete(f.rel); throw e; }
}
// Every font in a config that this browser lacks but the folder has.
export async function provideMissing(engine, substitutions) {
  let n = 0;
  for (const s of substitutions || []) {
    if (s.kind !== "stand-in") continue;          // already the real font
    const f = match(s.from);
    if (f) { await provide(engine, f); n++; }
  }
  return n;
}
