// The fonts installed on this computer (Chrome/Edge's Local Font Access).
// One shared list for the font picker and font coverage. The browser asks
// once; after that the permission sticks and the list loads by itself.

export const supported = typeof window.queryLocalFonts === "function";
export const state = { status: supported ? "unknown" : "unsupported", fonts: [], error: "" };
// status: unsupported | unknown | prompt | granted | denied | loading
const listeners = new Set();
export function onChange(fn) { listeners.add(fn); return () => listeners.delete(fn); }
const changed = () => listeners.forEach((fn) => fn(state));

async function load() {
  state.status = "loading"; changed();
  try {
    const fonts = await window.queryLocalFonts();
    const seen = new Set();   // one entry per PostScript name (Windows can report a font twice)
    state.fonts = fonts.filter((f) => !seen.has(f.postscriptName) && seen.add(f.postscriptName))
      .map((f) => ({ ps: f.postscriptName, family: f.family, style: f.style, full: f.fullName, data: f }))
      .sort((a, b) => a.family.localeCompare(b.family) || a.style.localeCompare(b.style));
    state.status = state.fonts.length ? "granted" : "denied";
    if (!state.fonts.length) state.error = "The browser didn't share any fonts.";
  } catch (e) {
    state.status = "denied";
    state.error = "The browser didn't allow access to installed fonts (" + (e.message || e) + ").";
  }
  changed();
}

// on startup: load the list if permission was already given
export async function restore() {
  if (!supported) return;
  let perm = "prompt";
  try { perm = (await navigator.permissions.query({ name: "local-fonts" })).state; } catch {}
  if (perm === "granted") await load();
  else { state.status = perm === "denied" ? "denied" : "prompt"; changed(); }
}

// from a click: ask
export const request = () => load();

export const bytes = async (f) => (await f.data.blob()).arrayBuffer();
