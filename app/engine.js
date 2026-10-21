// Which engine the app uses - the only place that decides. Both expose the
// same methods (see ENGINE_API.md):
//   browser - v4 running in this tab (Pyodide + WebAssembly). No install;
//             the default on the hosted site.
//   local   - v5/server.py on this computer. Needs the repo + Python; the
//             default when the page is served by that server.
// The choice is remembered per browser; setMode() switches and reloads.
import { httpEngine } from "./engine_http.js?v=a09a89460d";
import { browserEngine } from "./engine_browser.js?v=a09a89460d";

export { DEFAULT_ENGINE } from "./engine_http.js?v=a09a89460d";

function stored() { try { return localStorage.getItem("te.engineMode"); } catch { return null; } }
const servedByLocalEngine = location.protocol === "http:" && !location.pathname.includes("/_engine");
export const engineMode = stored() || (servedByLocalEngine ? "local" : "browser");
export const engine = engineMode === "local" ? httpEngine : browserEngine;
engine.mode = engineMode;
engine.setMode = (mode) => {
  try { localStorage.setItem("te.engineMode", mode); } catch {}
  location.reload();
};
