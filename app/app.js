import { createApp, reactive, ref, computed, watch, nextTick, onMounted } from "vue";
import { engine } from "./engine.js?v=e6f0c339dd";
import { Viewer } from "./viewer.js?v=e6f0c339dd";
import { progressTracker } from "./progress.js?v=e6f0c339dd";
import * as fontsync from "./fontsync.js?v=e6f0c339dd";
import * as localfonts from "./localfonts.js?v=e6f0c339dd";
import { missingIn } from "./coverage.js?v=e6f0c339dd";
import { zip, readZipText } from "./zip.js?v=e6f0c339dd";

// ---------------------------------------------------------------- grouping
// tune.py's per-machine sections (plus the controls it built by hand),
// regrouped by what the user is doing. A machine only sees groups it has
// something in; any section no group claims lands in Element.
const GROUPS = [
  { id: "typeface", label: "Typeface", icon: "Aa", sections: ["Font & Alignment", "Type test"], custom: "profiles",
    blurb: "Pick a font and size it - a type test shows it flat, like a printed page. When you like it, save it as a profile, then render and print." },
  { id: "layout", label: "Layout", icon: "⌨", sections: ["Character", "Row baselines"], custom: "layout",
    blurb: "Which character sits in which slot, drawn in the real font. Anything the font lacks is flagged red." },
  { id: "element", label: "Element", icon: "◎", sections: ["Element", "Cut groove & rib fit", "Cosmetics", "Bands", "Ticks"],
    blurb: "Physical dimensions of the element body - mostly real machine measurements." },
  { id: "branding", label: "Logo & label", icon: "✎", sections: ["Logo", "Label"],
    blurb: "Text and marks engraved on the element itself." },
  { id: "print", label: "Print prep", icon: "⬓", sections: ["Build", "Rib print", "Resin"],
    blurb: "Resin supports, print orientation, and the overhang check that runs after every build." },
  { id: "quality", label: "Quality", icon: "◆", sections: ["Quality"],
    blurb: "Facet counts and tessellation. Higher is smoother and slower." },
  { id: "tools", label: "Tests & tools", icon: "⚙", sections: ["Calibration", "Gauge"], custom: "tools",
    blurb: "Calibration sweeps, the shaft gauge and legend sheets." },
];
const TOOL_SECTIONS = ["Legend", "Legend output"];   // drawn inside the Tools page's own cards
const FONT_KEYS = new Set(["path", "font2_path", "font_path", "label_font_path", "legend_font_path", "label_font_override", "label_no_font_override"]);

// ---------------------------------------------------------------- fonts
const faces = reactive({});   // path -> css family name once loaded | "error"
let faceSeq = 0;
function fontFamily(path) {
  if (!path) return null;
  if (!(path in faces)) {
    faces[path] = null;
    const name = `tef${++faceSeq}`;
    // the in-browser engine hands over font bytes; the local engine a URL
    const source = engine.fontData ? engine.fontData(path) : Promise.resolve(`url("${engine.fontUrl(path)}")`);
    source.then((src) => new FontFace(name, src).load())
      .then((f) => { document.fonts.add(f); faces[path] = name; })
      .catch(() => { faces[path] = "error"; });
  }
  return faces[path];
}
// When the browser refuses a font file (Chrome's sanitizer rejects some
// fonts FreeType - and therefore the build - reads fine), text is drawn from
// the engine's own FreeType outlines instead, so previews still show the
// real shapes.
const outlines = reactive({});   // path -> { upem, ascender, descender, glyphs: {char: {d, adv} | null} }
const pendingOutline = {};
function needOutlines(path, text) {
  const have = outlines[path]?.glyphs || {};
  const missing = [...new Set([...text])].filter((c) => !(c in have) && !c.match(/\s/));
  if (!missing.length) return;
  const key = path + "\u0000" + missing.join("");
  if (pendingOutline[key]) return;
  pendingOutline[key] = engine.outlines(path, missing.join("")).then((r) => {
    const cur = outlines[path] || { upem: r.upem, ascender: r.ascender, descender: r.descender, glyphs: {} };
    outlines[path] = { ...cur, glyphs: { ...cur.glyphs, ...r.glyphs } };
  }).catch(() => {});
}
const FontText = {
  props: { path: String, text: String, fit: Boolean },
  setup(props) {
    const fam = computed(() => fontFamily(props.path));
    const lines = computed(() => String(props.text ?? "").split("\n"));
    const svgLines = computed(() => {
      if (fam.value !== "error") return null;
      needOutlines(props.path, props.text || "");
      const o = outlines[props.path];
      if (!o) return [];
      const h = o.ascender - o.descender;
      return lines.value.map((line) => {
        let x = 0;
        const parts = [];
        for (const c of line) {
          const g = o.glyphs[c];
          if (g) { parts.push({ d: g.d, x }); x += g.adv; }
          else x += o.upem * 0.5;
        }
        return { w: Math.max(x, 1), h, asc: o.ascender, parts };
      });
    });
    return { fam, lines, svgLines, famStyle };
  },
  template: `<span v-if="fam !== 'error'" class="ft" :style="famStyle(fam)">{{ text }}</span>
  <span v-else class="ft ft-svg"><span v-for="l in svgLines" class="ft-line">
    <svg :viewBox="'0 0 ' + l.w + ' ' + l.h" :style="{ height: '1.2em', width: (l.w / l.h * 1.2) + 'em' }" aria-hidden="true">
      <path v-for="p in l.parts" :d="p.d" :transform="'translate(' + p.x + ' ' + l.asc + ') scale(1 -1)'" fill="currentColor"/>
    </svg></span></span>`,
};

const famStyle = (fam, extra = {}) => (fam && fam !== "error" ? { fontFamily: `${fam}, var(--sans)`, ...extra } : extra);
const baseName = (p) => (p || "").split(/[\\/]/).pop();
const fontLabel = (p) => baseName(p).replace(/\.(ttf|otf|ttc|otc)$/i, "");
// Number steps: 0.1 (mm, degrees) unless the current value is already finer,
// then match its precision - 0.05 steps by 0.01, 0.005 by 0.001.
function stepOf(v) {
  const d = (String(v ?? "").split(".")[1] || "").replace(/e.*$/i, "").length;
  return d <= 1 ? 0.1 : Number((10 ** -Math.min(d, 6)).toFixed(Math.min(d, 6)));
}
const hex = (c) => "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");

// ---------------------------------------------------------------- state
const S = reactive({
  machines: [], machine: localStorage.getItem("te.machine") || null,
  data: null, edits: {}, rows: null, preset: null, group: localStorage.getItem("te.group") || "typeface", search: "",
  glyphs: { status: {}, unused: {} }, sel: null, profiles: [],
  job: { running: false, label: "", progress: 0, state: "", elapsed: 0, log: [], partial: "", issues: [],
         phase: "", eta: null },
  build: { target: "element", crossSection: false, crossAngle: 0, cutBodies: false, stl: null, last: null },
  coverage: { chars: "", dir: "", deep: false, report: false },
  legendStamp: 0, legendSettings: null, fonts: null, picker: null, toast: null,
  theme: localStorage.getItem("te.theme") || "auto", view: "settings", configs: null,
  engineDown: false, engineUrl: "", connecting: false, shared: false, forceDesktop: false,
  typeTestAuto: (() => { try { return !!localStorage.getItem("te.typeTestAuto"); } catch { return false; } })(),
  sync: { status: "none", name: null, count: 0, error: "" },   // fonts folder (fontsync.js)
  local: { status: "unknown", count: 0, error: "" },            // this computer's fonts (localfonts.js)
  access: false, previewText: "",
  helpAll: (() => { try { return localStorage.getItem("te.helpAll") === "1"; } catch { return false; } })(),   // show every setting's help
  helpOpen: {}, helpClosed: {},                                 // field key -> shown / hidden for just that one                               // the font-access popup; the picker's own preview text
  fontAdvanced: (() => { try { return !!localStorage.getItem("te.fontAdvanced"); } catch { return false; } })(),
  booting: false, engineStatus: null, bootedBefore: (() => { try { return !!localStorage.getItem("te.engineBooted"); } catch { return false; } })(), engineError: "", phoneLanding: false,
});

const fieldsByKey = computed(() => {
  const m = {};
  for (const s of S.data?.schema || []) for (const f of s.fields) m[f.key] = { ...f, section: s.section };
  return m;
});
const val = (key) => (key in S.edits ? S.edits[key] : fieldsByKey.value[key]?.value);
const dirty = computed(() => Object.keys(S.edits).length > 0 || S.rows !== null);
const layoutRows = computed(() => S.rows ?? S.data?.cfg?.layout?.rows ?? null);
const font2Chars = computed(() => String(val("font2_chars") ?? ""));
// A section only some build targets use (engine section_targets, e.g.
// Hammond's cut-groove settings) is hidden for the others.
const sectionApplies = (name) => {
  const t = S.data?.section_targets?.[name];
  return !t || t.includes(S.build.target);
};
const section = (name) => (sectionApplies(name) ? (S.data?.schema || []).find((s) => s.section === name) : undefined);

const groups = computed(() => {
  if (!S.data) return [];
  const claimed = new Set([...GROUPS.flatMap((g) => g.sections), ...TOOL_SECTIONS]);
  const orphans = S.data.schema.filter((s) => !claimed.has(s.section)).map((s) => s.section);
  return GROUPS.map((g) => {
    const secs = [...g.sections, ...(g.id === "element" ? orphans : [])].filter((n) => section(n));
    const n = secs.reduce((a, s) => a + section(s).fields.length, 0)
      + (g.custom === "tools" ? TOOL_SECTIONS.reduce((a, s) => a + (section(s)?.fields.length || 0), 0) : 0);
    const show = n > 0 || (g.custom === "layout" && layoutRows.value);   // Tests & tools only when it has something
    return show ? { ...g, sections: secs, count: n } : null;
  }).filter(Boolean);
});
const currentGroup = computed(() => groups.value.find((g) => g.id === S.group) || groups.value[0]);
const badGlyphs = computed(() => Object.entries(S.glyphs.status).filter(([, s]) => s !== "ok").map(([c]) => c));

// ---------------------------------------------------------------- actions
function toast(msg, kind = "info") {
  S.toast = { msg, kind };
  clearTimeout(toast.t);
  toast.t = setTimeout(() => (S.toast = null), 3600);
}

async function loadMachine(m, force = false) {
  if (!m) return;
  if (!force && dirty.value && !confirm("Discard unsaved changes?")) return;
  S.machine = m;
  localStorage.setItem("te.machine", m);
  S.data = await withSyncedFonts(m, await engine.config(m));
  S.edits = {}; S.rows = null; S.preset = null; S.sel = null;
  S.job.log = []; S.job.issues = []; S.job.state = ""; S.job.progress = 0;
  S.build.target = S.data.target;
  S.coverage.chars = (layoutRows.value || []).join("");
  if (S.data.migrated?.length) toast(`Added new settings from the master config: ${S.data.migrated.join(", ")}`);
  refreshGlyphs();
  engine.profiles(m).then((p) => (S.profiles = p)).catch(() => (S.profiles = []));
  viewer?.clear();
  const lastStl = engine.stlUrl(m);   // null in the browser engine until something is built
  try { S.build.stl = lastStl ? await viewer?.load(lastStl, { top: S.build.last?.kind === "type_test" }) : null; } catch { S.build.stl = null; }
}

// In the browser: a config font this browser doesn't have, but the synced
// folder or this computer's installed fonts do, is handed to the engine and
// the config re-read - the engine then swaps its stand-in for the real
// font (webengine.get_config). Matched by name: "Antikor Mono-Hairline.ttf"
// finds the installed AntikorMono-Hairline.
const localMatch = (path) => {
  if (S.local.status !== "granted") return null;
  const k = fontsync.fontKey(path);
  return localfonts.state.fonts.find((f) => fontsync.fontKey(f.ps) === k || fontsync.fontKey(f.full || "") === k) || null;
};
async function provideFont(path) {
  const f = fontsync.state.status === "ready" ? fontsync.match(path) : null;
  if (f) return { path: await fontsync.provide(engine, f), kind: "yours" };
  const l = localMatch(path);
  if (l) return { path: (await engine.addFont(l.ps + ".ttf", await localfonts.bytes(l))).path, kind: "yours" };
  return null;
}
async function withSyncedFonts(m, doc) {
  if (engine.kind !== "browser") return doc;
  let n = 0;
  try {
    for (const sub of doc.font_substitutions || []) if (sub.kind === "stand-in" && (await provideFont(sub.from))) n++;
    if (n) return await engine.config(m);
  } catch (e) { toast(`Your fonts: ${e.message || e}`, "bad"); }
  return doc;
}

// A font path from somewhere else (a profile, a settings file) -> this
// browser's copy of it: the synced folder's or this computer's, else the
// engine's own lookup.
async function resolveFont(path) {
  if (!path || engine.kind !== "browser") return { path, kind: "same" };
  return (await provideFont(path)) || engine.resolveFont(path);
}

// Help text: every setting can show its help under it - all at once (the
// topbar's Help button, remembered) or one at a time (its ⓘ button). It is
// always available as a hover tooltip too.
const helpShown = (key) => (S.helpAll ? !S.helpClosed[key] : !!S.helpOpen[key]);
const toggleHelp = (key) => { const m = S.helpAll ? S.helpClosed : S.helpOpen; m[key] = !m[key]; };
function setHelpAll(on) {
  S.helpAll = on; S.helpOpen = {}; S.helpClosed = {};
  try { localStorage.setItem("te.helpAll", on ? "1" : ""); } catch {}
}
const HelpButton = {
  props: ["k", "help"],
  setup: () => ({ helpShown, toggleHelp }),
  template: `<button v-if="help" type="button" class="help-btn" :class="{ on: helpShown(k) }" :aria-expanded="helpShown(k)"
    :title="helpShown(k) ? 'Hide help' : help" @click.prevent.stop="toggleHelp(k)">i</button>`,
};

function setVal(key, v) {
  const orig = fieldsByKey.value[key]?.value;
  const same = JSON.stringify(v) === JSON.stringify(orig) || (typeof orig === "number" && v !== "" && Number(v) === orig);
  if (same) delete S.edits[key]; else S.edits[key] = v;
  if (FONT_KEYS.has(key) || key === "font2_chars") refreshGlyphs();
}

async function save() {
  if (!dirty.value) return true;
  const body = { values: { ...S.edits } };
  if (S.rows !== null) { body.rows = S.rows; body.preset = S.preset; }
  let res;
  try { res = await engine.save(S.machine, body); } catch (e) { toast(String(e), "bad"); return false; }
  S.data = await withSyncedFonts(S.machine, res); S.edits = {}; S.rows = null; S.preset = null;
  if ((res.errors || []).length) { toast(res.errors.join(" · "), "bad"); refreshGlyphs(); return false; }
  toast(`Saved ${res.changed ?? ""} change${res.changed === 1 ? "" : "s"}`.replace("  ", " "), "ok");
  engine.profiles(S.machine).then((p) => (S.profiles = p));
  refreshGlyphs();
  return true;
}

function discard() { S.edits = {}; S.rows = null; S.preset = null; refreshGlyphs(); }

async function openConfigs() { S.configs = await engine.configs(S.machine); }
async function openConfig(path) {
  if (dirty.value && !confirm("Discard unsaved changes?")) return;
  await engine.openConfig(S.machine, path);
  S.configs = null;
  await loadMachine(S.machine, true);
  toast(`Opened ${baseName(path)}`);
}

// A settings file (from any download, or a config YAML) becomes its
// machine's running copy - the way to rebuild a print exactly.
async function importSettings(file) {
  if (!file) return;
  if (dirty.value && !confirm("Discard unsaved changes?")) return;
  try {
    let text;
    if (/\.zip$/i.test(file.name)) {
      const hit = await readZipText(file, (n) => /\.settings\.ya?ml$|\.ya?ml$/i.test(n));
      if (!hit) throw new Error("no settings file inside that .zip");
      text = hit.text;
    } else text = await file.text();
    const { machine } = await engine.importSettings(text);
    S.configs = null;
    await loadMachine(machine, true);
    toast(`Loaded the settings from ${file.name}`, "ok");
  } catch (e) { toast(String(e.message || e), "bad"); }
}

async function resetToMaster() {
  if (!confirm(`Replace ${S.data.label}'s running config with the master defaults? Every customization for this machine is lost.`)) return;
  S.data = await engine.reset(S.machine);
  S.edits = {}; S.rows = null; refreshGlyphs();
  toast("Reset to master defaults");
}

let glyphTimer;
function refreshGlyphs() {
  clearTimeout(glyphTimer);
  glyphTimer = setTimeout(async () => {
    const rows = layoutRows.value;
    if (!rows) { S.glyphs = { status: {}, unused: {} }; return; }
    try {
      S.glyphs = await engine.glyphs({ font: val("path"), font2: val("font2_path"), font2_chars: font2Chars.value, chars: rows.join("") });
    } catch { S.glyphs = { status: {}, unused: {} }; }
  }, 250);
}

function classify(line) {
  if (/WARNING/.test(line)) return "w";
  if (/^(Traceback|  File )|Error\b|FAILED/.test(line)) return "e";
  if (/^\$ |^wrote /.test(line)) return "c";
  if (/^OK|^done/.test(line)) return "ok";
  return "";
}

const narrow = () => matchMedia("(max-width: 1279px)").matches;

// One runner for every job (builds, type test, legend, coverage) - they all
// share the progress bar, the log and the issue summary.
const APP_VERSION = new URL(import.meta.url).searchParams.get("v") || "dev";

async function runJob(label, start, after, kind = null) {
  if (S.job.running) return;
  if (!(await save())) return;
  // the settings this job is built from, taken now (after the save, before
  // anything can change) so its download carries exactly them
  const stem = kind ? fileStem(kind) : null;
  const settings = kind ? engine.settingsFile(S.machine, {
    last_build: { kind, target: kind === "type_test" ? "type_test" : S.build.target, name: stem },
    engine: engine.kind, app: APP_VERSION,
  }).catch(() => null) : null;
  const j = S.job;
  Object.assign(j, { running: true, label, progress: 0, state: "", log: [], partial: "", issues: [], phase: "", eta: null });
  if (narrow()) S.view = "build";
  const t0 = Date.now();
  // see progress.js: timed from this job's previous runs, ticked smoothly
  const prog = progressTracker([engine.mode, S.machine, label, S.build.target].join("|"));
  const tick = setInterval(() => {
    j.elapsed = (Date.now() - t0) / 1000;
    j.progress = prog.value();
    j.eta = prog.remaining();
  }, 100);
  let rc = -1;
  try {
    await start((ev) => {
      prog.event(ev);
      if (ev.phase) j.phase = ev.phase[2];
      if (ev.line !== undefined) {
        j.partial = "";
        j.log.push({ t: ev.line, c: classify(ev.line) });
        if (/WARNING/.test(ev.line)) j.issues.push(ev.line.replace(/^\s*WARNING:\s*/, "").replace(/: WARNING:/, ":"));
        logScroll();
      } else if (ev.partial !== undefined) j.partial = ev.partial;
      if (ev.done !== undefined) rc = ev.done;
    });
  } catch (e) { j.log.push({ t: String(e.message || e), c: "e" }); }
  clearInterval(tick);
  prog.finish(rc === 0);
  j.running = false; j.eta = null;
  j.elapsed = (Date.now() - t0) / 1000;
  if (rc === 0) {
    j.progress = 1; j.state = "ok";
    j.log.push({ t: `${label} finished in ${j.elapsed.toFixed(1)}s`, c: "ok" });
    try { await after?.(); } catch (e) { j.log.push({ t: String(e.message || e), c: "e" }); }
    if (kind) S.build.last = { ...(S.build.last || {}), kind, name: stem, settings: await settings,
                               target: kind === "type_test" ? "type_test" : S.build.target, at: new Date().toISOString() };
  } else {
    j.state = "fail";
    if (rc > 0) j.log.push({ t: `${label} failed (exit ${rc})`, c: "e" });
    if (rc < 0 && j.log.length) j.log.push({ t: `${label} stopped`, c: "c" });
  }
  logScroll();
}

// File name for a download: the engine's machine_font_size stem (as of this
// build), what was built, and when - e.g. selectric12_FreeSans_2.4mm_2026-10-19_2231.
function fileStem(kind) {
  const d = new Date(), p = (n) => String(n).padStart(2, "0");
  const when = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`;
  const what = kind === "preview" ? "_preview" : kind === "type_test" ? "_typetest" : kind === "legend" ? "_legend" : "";
  return `${S.data?.export_name || S.machine}${what}_${when}`;
}

function runBuild(fast) {
  const b = S.build;
  const opts = { fast, target: b.target, cross_section: b.crossSection, cross_section_angle: b.crossAngle, cut_bodies: b.cutBodies };
  return runJob(fast ? "Preview" : "Render", (on) => engine.build(S.machine, opts, on), async () => {
    b.stl = await viewer.load(engine.stlUrl(S.machine));
  }, fast ? "preview" : "render");
}
const runTypeTest = () => runJob("Type test", (on) => engine.tool(S.machine, { tool: "type_test" }, on), async () => {
  S.build.stl = await viewer.load(engine.stlUrl(S.machine), { top: true });
}, "type_test");
const runLegend = () => runJob("Legend", (on) => engine.tool(S.machine, { tool: "legend" }, on),
  async () => { S.legendStamp = Date.now(); S.legendSettings = await engine.settingsFile(S.machine, { last_build: { kind: "legend", name: fileStem("legend") }, engine: engine.kind, app: APP_VERSION }).catch(() => null); });

// Every download is one .zip: the file itself, the settings it was made
// from (loads straight back in: Open config > Load a settings file) and,
// for a calibration build, its position -> tested value mapping.
async function fetchBytes(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return new Uint8Array(await r.arrayBuffer());
}
async function downloadBundle(fileUrl, ext, last) {
  try {
    const stem = last?.name || fileStem(last?.kind || "render");
    const entries = [{ name: `${stem}.${ext}`, data: await fetchBytes(fileUrl) }];
    const settings = last?.settings || (await engine.settingsFile(S.machine, { last_build: last, engine: engine.kind, app: APP_VERSION }));
    entries.push({ name: `${stem}.settings.yaml`, data: settings.text });
    if (last?.target === "calibration") {
      const m = engine.mappingUrl(S.machine);
      if (m) { try { entries.push({ name: `${stem}_mapping.txt`, data: await fetchBytes(m) }); } catch {} }
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(zip(entries));
    a.download = `${stem}.zip`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
  } catch (e) { toast(`Download failed: ${e.message || e}`, "bad"); }
}
const downloadBuild = () => downloadBundle(engine.stlUrl(S.machine), "stl", S.build.last);
const downloadLegend = () => downloadBundle(engine.legendUrl(S.machine, S.legendStamp), "svg", S.legendSettings ? { kind: "legend", name: S.legendSettings.name.replace(/\.settings\.yaml$/, ""), settings: S.legendSettings } : { kind: "legend" });
const runCoverage = (current) => runJob(current ? "Font check" : "Font scan", (on) => engine.tool(S.machine, {
  tool: current ? "coverage_current" : "coverage", chars: S.coverage.chars, font_dir: S.coverage.dir, deep: S.coverage.deep,
}, on), async () => { S.coverage.report = true; });

async function saveCopy() {
  try {
    const { settings, ...last } = S.build.last || {};
    const r = await engine.saveCopy(S.machine, { last_build: last });
    toast(`Saved a copy: ${r.path}`, "ok");
  } catch (e) { toast(String(e.message || e), "bad"); }
}

let logEl = null;
function logScroll() { nextTick(() => { if (logEl) logEl.scrollTop = logEl.scrollHeight; }); }

function applyTheme() {
  const t = S.theme;
  if (t === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t;
  localStorage.setItem("te.theme", t);
  // night inverts the light theme as a whole (style.css), the viewer included
  viewer?.setTheme(t === "dark" || (t === "auto" && matchMedia("(prefers-color-scheme: dark)").matches));
}

function openGroup(id) { S.group = id; S.search = ""; S.view = "settings"; localStorage.setItem("te.group", id); }

function jumpTo(f) {
  const g = groups.value.find((g) => g.sections.includes(f.section)) || (TOOL_SECTIONS.includes(f.section) && groups.value.find((g) => g.id === "tools"));
  if (g) openGroup(g.id);
  nextTick(() => {
    const el = document.getElementById(`f-${f.key}`);
    if (!el) return;
    el.scrollIntoView({ block: "center", behavior: "smooth" });
    el.classList.remove("hit"); void el.offsetWidth; el.classList.add("hit");
  });
}

// ---------------------------------------------------------------- layout editing
function setRows(rows, preset = null) {
  const same = JSON.stringify(rows) === JSON.stringify(S.data.cfg.layout.rows);
  S.rows = same ? null : rows;
  S.preset = same ? null : preset;
  refreshGlyphs();
}
function setChar(r, i, ch) {
  const rows = [...layoutRows.value];
  const arr = [...rows[r]];
  arr[i] = ch;
  rows[r] = arr.join("");
  setRows(rows);
}
function setRowText(r, text) { const rows = [...layoutRows.value]; rows[r] = text; setRows(rows); }
function applyPreset(name) {
  if (!name) return;
  setRows([...S.data.presets[name]], name);
  // show the baselines this preset brings (e.g. Hammond's 4-row Math) right
  // away, as pending edits - not only after Save
  const seeds = S.data.preset_baselines?.[name];
  const fields = S.data.schema.flatMap((s) => s.fields);
  for (const key of ["baseline_row", "cutout_row"]) {
    const f = fields.find((x) => x.key === key);
    if (!f) continue;
    if (seeds && S.rows !== null && JSON.stringify(seeds) !== JSON.stringify(f.value)) S.edits[key] = [...seeds];
    else delete S.edits[key];
  }
  S.sel = null;
  toast(`Preset "${name}" applied - Save to keep it`);
}

let viewer = null;

// ---------------------------------------------------------------- components
const FieldInput = {
  props: ["f"],
  setup(props) {
    const v = computed(() => val(props.f.key));
    const changed = computed(() => props.f.key in S.edits);
    const textFam = computed(() => (props.f.type === "textblock" ? fontFamily(val("path")) : null));
    const setItem = (i, x) => { const a = [...(v.value || [])]; a[i] = x === "" ? 0 : Number(x); setVal(props.f.key, a); };
    // rows are shift levels only on the 3-4 row machines (not the Mignon's 7-row index)
    const rowLabel = (i) => ((layoutRows.value || []).length <= 4 && ["lowercase", "uppercase", "figures", "math"][i]
      ? `Row ${i + 1} · ${["lowercase", "uppercase", "figures", "math"][i]}` : `Row ${i + 1}`);
    const ALIGN = ["left", "center", "right", "justify"];
    const isAlign = computed(() => props.f.options.length > 1 && props.f.options.every((o) => ALIGN.includes(o.value)));
    // paragraph-alignment glyph: [x, width] per bar
    const alignBars = (a) => ({ left: [[2, 16], [2, 10], [2, 14], [2, 8]], center: [[2, 16], [5, 10], [3, 14], [6, 8]],
      right: [[2, 16], [8, 10], [4, 14], [10, 8]], justify: [[2, 16], [2, 16], [2, 16], [2, 16]] }[a]);
    const step = computed(() => (props.f.type === "int" ? 1 : stepOf(v.value)));
    return { v, changed, setVal, setItem, textFam, famStyle, rowLabel, isAlign, alignBars, step, stepOf, helpShown };
  },
  components: { HelpButton },
  template: `
  <div class="field" :class="{ wide: f.type === 'floatlist' || f.type === 'textblock' }" :id="'f-' + f.key" :title="f.help || ''">
    <template v-if="f.type === 'bool'">
      <div class="switch-row"><label class="switch"><input type="checkbox" :checked="!!v" @change="setVal(f.key, $event.target.checked)">
        <span>{{ f.label }}</span><span v-if="changed" class="changed"></span></label><HelpButton :k="f.key" :help="f.help" /></div>
    </template>
    <template v-else>
      <label :for="'i-' + f.key">{{ f.label }}<span v-if="changed" class="changed"></span><HelpButton :k="f.key" :help="f.help" /></label>
      <div v-if="isAlign" class="seg-icons" role="radiogroup" :aria-label="f.label">
        <button v-for="o in f.options" :class="{ on: String(v) === o.value }" :title="o.label" :aria-label="o.label" role="radio" :aria-checked="String(v) === o.value" @click="setVal(f.key, o.value)">
          <svg viewBox="0 0 20 20" fill="currentColor"><rect v-for="(w, i) in alignBars(o.value)" :x="w[0]" :y="3 + i * 4" :width="w[1]" height="2" rx="1"/></svg>
        </button>
      </div>
      <select v-else-if="f.options.length" class="select" :id="'i-' + f.key" :value="String(v)" @change="setVal(f.key, $event.target.value)">
        <option v-for="o in f.options" :value="o.value">{{ o.label }}</option>
      </select>
      <div v-else-if="f.type === 'floatlist'" class="listrow">
        <div v-for="(x, i) in (v || [])" class="listitem">
          <span class="help">{{ f.key.startsWith('band') ? 'Band ' + (i + 1) : rowLabel(i) }}</span>
          <input class="input" type="number" :step="stepOf(x)" :value="x" @input="setItem(i, $event.target.value)">
        </div>
      </div>
      <textarea v-else-if="f.type === 'textblock'" class="input textblock" :id="'i-' + f.key" :value="v ?? ''"
                :style="famStyle(textFam)" @input="setVal(f.key, $event.target.value)"></textarea>
      <input v-else-if="f.type === 'int' || f.type === 'float'" class="input" type="number" :step="step"
             :id="'i-' + f.key" :value="v" @input="setVal(f.key, $event.target.value === '' ? '' : Number($event.target.value))">
      <input v-else class="input" :id="'i-' + f.key" :value="v ?? ''" @input="setVal(f.key, $event.target.value)">
    </template>
    <div v-if="f.help && helpShown(f.key)" class="help">{{ f.help }}</div>
  </div>`,
};

const FontField = {
  props: ["f", "sample"],
  components: { FontText, HelpButton },
  setup(props) {
    const path = computed(() => val(props.f.key) || "");
    const fam = computed(() => fontFamily(path.value));
    const changed = computed(() => props.f.key in S.edits);
    const pick = () => { S.picker = { key: props.f.key, label: props.f.label, current: path.value, sample: props.sample }; };
    const substituted = computed(() => (S.data.font_substitutions || []).find((s) => s.key === props.f.key && s.to === path.value));
    return { S, path, fam, changed, pick, fontLabel, setVal, famStyle, substituted, baseName, helpShown };
  },
  template: `
  <div class="field wide" :id="'f-' + f.key">
    <label>{{ f.label }}<span v-if="changed" class="changed"></span><HelpButton :k="f.key" :help="f.help" /></label>
    <div class="font-field">
      <div v-if="substituted && substituted.kind !== 'bundled'" class="note" :class="substituted.kind === 'stand-in' ? 'warn' : 'info'" style="margin:10px 12px 0">
        <template v-if="substituted.kind === 'yours'">Using your copy of {{ fontLabel(substituted.from) }}{{ S.sync.name && substituted.to.startsWith('/fonts/synced/') ? ' from the ' + S.sync.name + ' folder' : '' }}.</template>
        <template v-else-if="substituted.kind === 'bundled' || baseName(substituted.from) === baseName(substituted.to)">Using the copy of {{ fontLabel(substituted.to) }} that ships with the app - this config's own file is on another computer.</template>
        <template v-else>"{{ fontLabel(substituted.from) }}" isn't in this browser - using {{ fontLabel(substituted.to) }} for now. Sync a fonts folder that has it (Choose… below), or choose another font.</template>
      </div>
      <div v-if="!path" class="font-missing" style="color:var(--text-3)">No font set{{ f.key === 'font2_path' ? ' - these characters use the main font.' : '.' }}</div>
      <div v-else class="spec" :style="fam === null ? { opacity: .35 } : {}">
        <div class="name"><FontText :path="path" :text="fontLabel(path)" /></div>
        <div class="sample"><FontText :path="path" :text="sample || 'AaBbCc 0123456789 &?!'" /></div>
        <div v-if="fam === 'error'" class="help" style="margin-top:6px">Drawn from the font's outlines - this browser won't load the file directly, but the build reads it fine.</div>
      </div>
      <div class="meta">
        <span class="path" :title="path">{{ path || '—' }}</span>
        <button class="btn small" @click="pick" title="Pick a font: the app's own, this computer's, your fonts folder, or a file">Choose…</button>
        <button v-if="path && f.key !== 'path'" class="btn small ghost" @click="setVal(f.key, '')">Clear</button>
      </div>
    </div>
    <div v-if="f.help && helpShown(f.key)" class="help">{{ f.help }}</div>
  </div>`,
};

const SectionCard = {
  props: ["s", "title"],
  components: { FieldInput, FontField },
  setup(props) {
    const fonts = computed(() => props.s.fields.filter((f) => FONT_KEYS.has(f.key) && !f.list));
    const plain = computed(() => props.s.fields.filter((f) => !FONT_KEYS.has(f.key) && !f.list));
    const lists = computed(() => props.s.fields.filter((f) => f.list));
    const sampleFor = (key) => {
      const c = S.data.cfg;
      if (key === "path") return (layoutRows.value || []).join("\n") || null;   // one line per keyboard row
      if (key === "font2_path") return font2Chars.value || null;
      if (key === "font_path") return c.logo?.text || [c.label?.label1, c.label?.label2].filter(Boolean).join("  ") || null;
      if (key === "label_font_path") return [c.label?.label1, c.label?.label2, c.label?.text].filter(Boolean).join("  ") || null;
      return null;
    };
    return { fonts, plain, lists, sampleFor };
  },
  template: `
  <section class="card" :class="{ advanced: s.intro && s.intro.level === 'advanced' }">
    <div class="card-head"><h2>{{ title || s.section }}</h2><span class="sub">{{ s.fields.length }} setting{{ s.fields.length === 1 ? '' : 's' }}</span><span class="spacer"></span><slot name="actions"></slot></div>
    <div class="card-body">
      <div v-if="s.intro" class="note" :class="s.intro.level">{{ s.intro.text }}</div>
      <slot name="top"></slot>
      <div class="fields">
        <FontField v-for="f in fonts" :key="f.key" :f="f" :sample="sampleFor(f.key)" />
        <FieldInput v-for="f in plain" :key="f.key" :f="f" />
      </div>
      <div v-if="lists.length" class="help" style="margin-top:12px">Edited on the Layout page: {{ lists.map(f => f.label).join(', ') }}.</div>
      <slot></slot>
    </div>
  </section>`,
};

// The Typeface page's main card. Most people only change the font and its
// size, so those are all it shows; everything else that shapes the
// characters (alignment nudges, caret and underscore, the second font,
// draft angle) is one click away under Advanced.
const SIMPLE_FONT_KEYS = ["path", "size_mm", "composer_cap_height"];
const FontCard = {
  props: ["s"],
  components: { FieldInput, FontField },
  setup(props) {
    const simple = computed(() => SIMPLE_FONT_KEYS.map((k) => props.s.fields.find((f) => f.key === k)).filter(Boolean));
    const adv = computed(() => props.s.fields.filter((f) => !SIMPLE_FONT_KEYS.includes(f.key) && !f.list));
    const advFonts = computed(() => adv.value.filter((f) => FONT_KEYS.has(f.key)));
    const advPlain = computed(() => adv.value.filter((f) => !FONT_KEYS.has(f.key)));
    const advChanged = computed(() => adv.value.filter((f) => f.key in S.edits).length);
    const toggle = (open) => { S.fontAdvanced = open; try { localStorage.setItem("te.fontAdvanced", open ? "1" : ""); } catch {} };
    const sample = computed(() => (layoutRows.value || []).join("\n") || null);
    const active = computed(() => S.profiles.find((p) => p.active && !p.builtin) || S.profiles.find((p) => p.active));
    return { S, simple, advFonts, advPlain, advChanged, toggle, sample, active, FONT_KEYS, runTypeTest, fontsync };
  },
  template: `
  <section class="card" id="font-card">
    <div class="card-head"><h2>Font</h2><span class="sub">{{ active ? 'Profile: ' + active.name : 'Custom settings' }}</span>
      <span class="spacer"></span>
      <button class="btn small" :disabled="S.job.running" @click="runTypeTest" title="A flat plate of text in this font - quick to render, shown from above">Type test</button></div>
    <div class="card-body">
      <div v-if="S.sync.status === 'needs-permission'" class="note info" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <span style="flex:1;min-width:200px">Your fonts folder <b>{{ S.sync.name }}</b> needs your OK again this visit (Chrome asks unless you chose "Allow on every visit").</span>
        <button class="btn small primary" @click="fontsync.reconnect()">Reconnect</button></div>
      <div class="fields">
        <template v-for="f in simple" :key="f.key">
          <FontField v-if="FONT_KEYS.has(f.key)" :f="f" :sample="sample" />
          <FieldInput v-else :f="f" />
        </template>
      </div>
      <details class="adv" :open="S.fontAdvanced" @toggle="toggle($event.target.open)">
        <summary>Advanced: alignment, caret, second font, draft angle<span v-if="advChanged" class="chip dirty" style="margin-left:8px">{{ advChanged }} changed</span></summary>
        <div class="fields" style="margin-top:12px">
          <FontField v-for="f in advFonts" :key="f.key" :f="f" />
          <FieldInput v-for="f in advPlain" :key="f.key" :f="f" />
        </div>
      </details>
    </div>
  </section>`,
};

// Find a font -> size it -> like it, save it as a profile -> render,
// download, print -> come back, tweak, print again. Shown on the Typeface
// page as five steps that tick themselves off.
const WorkflowStrip = {
  setup() {
    const steps = computed(() => {
      const last = S.build.last?.kind;
      const prof = S.profiles.find((p) => p.active && !p.builtin) || S.profiles.find((p) => p.active);
      return [
        { n: 1, t: "Pick a font", done: !!val("path"), go: "font-card" },
        { n: 2, t: "Size it with a type test", done: last === "type_test" || last === "render" || last === "preview", go: "font-card" },
        { n: 3, t: "Save it as a profile", done: !!prof && !prof.builtin && !dirty.value, go: "profiles-card" },
        { n: 4, t: "Render & download", done: last === "render", go: null },
        { n: 5, t: "Print, tweak, repeat", done: false, go: null },
      ];
    });
    const go = (st) => {
      if (st.go) document.getElementById(st.go)?.scrollIntoView({ behavior: "smooth", block: "start" });
      else if (narrow()) S.view = "build";
    };
    return { steps, go };
  },
  template: `<ol class="flow">
    <li v-for="st in steps" :class="{ done: st.done }" :title="st.done ? 'Done' : 'Next: ' + st.t" @click="go(st)"><span class="n">{{ st.done ? '✓' : st.n }}</span>{{ st.t }}</li>
  </ol>`,
};

const ProfilesCard = {
  setup() {
    const name = ref("");
    const renaming = ref(null), renameTo = ref("");
    const active = computed(() => S.profiles.find((p) => p.active && !p.builtin) || S.profiles.find((p) => p.active));
    const mine = computed(() => S.profiles.filter((p) => !p.builtin));
    const builtin = computed(() => S.profiles.filter((p) => p.builtin));
    // Applying a profile: its font paths may come from another computer, so
    // each is resolved to this browser's copy (synced folder, added fonts)
    const apply = async (p) => {
      const byPath = Object.fromEntries(Object.values(fieldsByKey.value).map((f) => [f.path.join("."), f.key]));
      let n = 0;
      const missing = [];
      for (const [path, v] of Object.entries(p.values)) {
        const key = byPath[path];
        if (!key) continue;
        let value = v;
        if (FONT_KEYS.has(key) && v) {
          const r = await resolveFont(v).catch(() => ({ path: v, kind: "missing" }));
          value = r.path;
          if (r.kind === "missing") missing.push(fontLabel(v));
        }
        setVal(key, value); n++;
      }
      if (missing.length) toast(`"${p.name}" uses ${missing.join(", ")}, which isn't in this browser - it builds with a stand-in until you sync a fonts folder that has it. Save to keep.`, "bad");
      else toast(`Switched to "${p.name}" (${n} settings) - Save to keep it, or keep tweaking.`);
    };
    const saveAs = async (nm = name.value.trim()) => {
      if (!nm) return;
      if (!(await save())) return;
      S.profiles = await engine.saveProfile(S.machine, nm);
      toast(`Saved profile "${nm}"`, "ok"); name.value = "";
    };
    // overwrite the active profile with the current settings
    const update = async (p) => { if (confirm(`Replace "${p.name}" with the current font settings?`)) await saveAs(p.name); };
    const startRename = (p) => { renaming.value = p.name; renameTo.value = p.name; nextTick(() => document.getElementById("rename-input")?.select()); };
    const finishRename = async () => {
      const old = renaming.value, n = renameTo.value.trim();
      renaming.value = null;
      if (!old || !n || n === old) return;
      S.profiles = await engine.renameProfile(S.machine, old, n).catch((e) => (toast(e.message, "bad"), S.profiles));
    };
    const del = async (p) => { if (confirm(`Delete profile "${p.name}"?`)) S.profiles = await engine.deleteProfile(S.machine, p.name); };
    return { S, name, active, mine, builtin, apply, saveAs, update, renaming, renameTo, startRename, finishRename, del, dirty };
  },
  template: `
  <section class="card" id="profiles-card">
    <div class="card-head"><h2>Font profiles</h2><span class="sub">{{ active ? (dirty ? 'Edited from ' : 'Using ') + active.name : 'Current settings match no profile' }}</span></div>
    <div class="card-body">
      <p class="help" style="margin-top:0">A profile is a font plus everything on the Font card. Click one to switch to it; save one when you find a setting you like, and it's there for every machine.</p>
      <div class="profile-list">
        <div v-for="p in [...mine, ...builtin]" :key="p.name" class="profile" :class="{ on: p.active }" :title="p.active ? 'The current settings' : 'Switch to this profile'" @click="!p.active && renaming !== p.name && apply(p)">
          <template v-if="renaming === p.name">
            <input id="rename-input" class="input" style="flex:1" v-model="renameTo" @click.stop @keyup.enter="finishRename" @keyup.esc="renaming = null" @blur="finishRename">
          </template>
          <template v-else>
            <span class="pname">{{ p.name }}</span>
            <span v-if="p.builtin" class="chip" title="Ships with the app">built-in</span>
            <span v-if="p.active" class="chip ok">{{ dirty ? 'edited' : 'active' }}</span>
            <span class="spacer"></span>
            <template v-if="!p.builtin">
              <button v-if="p.active" class="btn small ghost" @click.stop="update(p)" title="Save the current settings into this profile">Update</button>
              <button class="btn small ghost" @click.stop="startRename(p)">Rename</button>
              <button class="btn small ghost danger" @click.stop="del(p)">Delete</button>
            </template>
          </template>
        </div>
      </div>
      <p v-if="!S.profiles.length" class="help">No profiles yet.</p>
      <div style="display:flex;gap:8px;margin-top:10px">
        <input class="input" style="flex:1" v-model="name" placeholder="Name these settings, e.g. Antikor 3.0 - first print" @keyup.enter="saveAs()">
        <button class="btn primary" :disabled="!name.trim()" @click="saveAs()">Save as profile</button>
      </div>
    </div>
  </section>`,
};

const LayoutPage = {
  components: { FontText },
  setup() {
    const fam = computed(() => fontFamily(val("path")));
    const fam2 = computed(() => fontFamily(val("font2_path") || val("path")));
    const sel = computed(() => S.sel);
    const selChar = computed(() => (sel.value ? [...layoutRows.value[sel.value.r]][sel.value.i] : null));
    const famFor = (c) => (font2Chars.value.includes(c) ? fam2.value : fam.value);
    const mainPath = computed(() => val("path"));
    const pathFor = (c) => (font2Chars.value.includes(c) ? (val("font2_path") || val("path")) : val("path"));
    const pick = (r, i) => { S.sel = S.sel && S.sel.r === r && S.sel.i === i ? null : { r, i }; };
    const presetNames = computed(() => Object.keys(S.data.presets || {}));
    const activePreset = computed(() => S.preset ?? (S.rows === null ? S.data.current_preset : null));
    const typed = ref("");
    watch(selChar, (c) => (typed.value = c ?? ""));
    const applyTyped = () => { if (sel.value && typed.value) setChar(sel.value.r, sel.value.i, [...typed.value][0]); };
    const showText = ref(false);
    // keyboard / element views (engine layout_views): every cell is a
    // [row, index] reference, so either view edits the same slots
    const views = computed(() => S.data.layout_views || []);
    const viewKey = computed(() => "te.layoutView." + S.machine);
    const viewId = ref(null);
    watch(views, (vs) => {
      let want = null;
      try { want = localStorage.getItem(viewKey.value); } catch {}
      viewId.value = vs.find((v) => v.id === want)?.id || vs[0]?.id || null;
    }, { immediate: true });
    const view = computed(() => views.value.find((v) => v.id === viewId.value) || null);
    const setView = (id) => { viewId.value = id; showText.value = false; try { localStorage.setItem(viewKey.value, id); } catch {} };
    const level = ref("all");                    // keys view: every level on each key, or one
    watch(view, () => { if (level.value !== "all" && !(view.value?.levels || [])[+level.value]) level.value = "all"; });
    const charAt = (ref_) => [...(layoutRows.value[ref_[0]] || "")][ref_[1]] ?? "";
    const isSel = (ref_) => sel.value && sel.value.r === ref_[0] && sel.value.i === ref_[1];
    const cellClass = (ref_) => {
      const c = charAt(ref_);
      return [S.glyphs.status[c] && S.glyphs.status[c] !== "ok" ? S.glyphs.status[c] : "", isSel(ref_) ? "sel" : "",
              c.trim() ? "" : "space", font2Chars.value.includes(c) ? "f2" : ""];
    };
    // corner of a key cap for each level: UPPER top-left, lower bottom-left, figures top-right, math bottom-right
    const CORNER = ["bl", "tl", "tr", "br"];
    const origLen = (r) => [...(S.data.cfg.layout.rows[r] || "")].length;
    const lenBad = (r, row) => S.data.fixed_row_lengths && !S.preset && [...row].length !== origLen(r);
    return { S, fam, famFor, mainPath, pathFor, pick, sel, selChar, presetNames, activePreset, applyPreset, setChar, setRowText,
             typed, applyTyped, showText, badGlyphs, layoutRows, font2Chars, famStyle, hex, lenBad, origLen,
             views, view, viewId, setView, level, charAt, cellClass, CORNER };
  },
  template: `
  <section class="card">
    <div class="card-head">
      <h2>Keyboard layout</h2><span class="sub">{{ activePreset ? activePreset : 'Custom' }} · {{ layoutRows.length }} rows</span>
      <span class="spacer"></span>
      <div class="seg show" role="tablist" aria-label="Layout view">
        <button v-for="v in views" :class="{ on: !showText && viewId === v.id }" @click="setView(v.id)" :title="v.note || v.label">{{ v.label }}</button>
        <button :class="{ on: showText }" @click="showText = !showText" title="Edit each stored row as a line of text">{{ views.length ? 'Text' : (showText ? 'Show grid' : 'Edit as text') }}</button>
      </div>
    </div>
    <div class="card-body">
      <div v-if="presetNames.length" class="field" style="margin-bottom:12px">
        <label>Preset</label>
        <select class="select" :value="activePreset || ''" @change="applyPreset($event.target.value)">
          <option value="" disabled>Custom (edited by hand)</option>
          <option v-for="n in presetNames" :value="n">{{ n }}</option>
        </select>
        <div v-if="S.data.layout_help" class="help">{{ S.data.layout_help }}</div>
      </div>
      <div v-if="badGlyphs.length" class="note bad">
        Character not found in the font: <b style="font-size:16px">{{ badGlyphs.join(' ') }}</b> - those slots would build empty or as a box.
        Click one and pick a replacement below.
      </div>
      <div v-else-if="Object.keys(S.glyphs.status).length" class="note ok">Every character is in the font.</div>
      <div v-if="S.data.fixed_row_lengths" class="help" style="margin:-4px 0 10px">On this machine each row maps onto fixed ball positions, so rows keep their exact length - swap characters, don't add or remove them.</div>
      <template v-if="!showText && view">
        <div v-if="view.kind === 'keys'" class="seg show small level-seg" role="radiogroup" aria-label="Shift level">
          <button :class="{ on: level === 'all' }" @click="level = 'all'">All levels</button>
          <button v-for="(lv, n) in view.levels" :class="{ on: level === String(n) }" @click="level = String(n)">{{ lv }}</button>
        </div>
        <div v-if="view.note" class="help" style="margin:0 0 8px">{{ view.note }}</div>
        <div class="kb-scroll"><div class="kb">
          <template v-if="view.kind === 'keys'">
            <div v-for="(krow, kr) in view.rows" class="kb-row keyrow" :style="{ '--n': krow.length, paddingLeft: (kr * 14) + 'px' }">
              <div class="kb-keys">
                <div v-for="(k, ki) in krow" class="keycap" :class="{ one: level !== 'all' }">
                  <template v-if="level === 'all'">
                    <div v-for="(ref_, lv) in k" class="kc" :class="[CORNER[lv], ...cellClass(ref_)]" :title="view.levels[lv] + ' · ' + hex(charAt(ref_) || ' ')"
                         @click="pick(ref_[0], ref_[1])"><FontText v-if="charAt(ref_).trim()" :path="pathFor(charAt(ref_))" :text="charAt(ref_)" /><template v-else>␣</template></div>
                  </template>
                  <div v-else-if="k[+level]" class="kc solo" :class="cellClass(k[+level])" :title="hex(charAt(k[+level]) || ' ')"
                       @click="pick(k[+level][0], k[+level][1])"><FontText v-if="charAt(k[+level]).trim()" :path="pathFor(charAt(k[+level]))" :text="charAt(k[+level])" /><template v-else>␣</template></div>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div v-for="(grow, gr) in view.rows" class="kb-row" :style="{ '--n': grow.length }">
              <span class="rn" :title="(view.row_labels || [])[gr]">{{ gr + 1 }}</span>
              <div class="kb-keys">
                <div v-for="(ref_, gi) in grow" class="key" :class="[...cellClass(ref_), view.shifted && view.shifted[ref_[0]] && view.shifted[ref_[0]][ref_[1]] ? 'shifted' : '']"
                     :title="hex(charAt(ref_) || ' ') + (view.shifted && view.shifted[ref_[0]] && view.shifted[ref_[0]][ref_[1]] ? ' · typed with Shift' : '')"
                     @click="pick(ref_[0], ref_[1])"><FontText v-if="charAt(ref_).trim()" :path="pathFor(charAt(ref_))" :text="charAt(ref_)" /><template v-else>␣</template></div>
              </div>
            </div>
          </template>
        </div></div>
      </template>
      <div v-else-if="!showText" class="kb-scroll"><div class="kb">
        <div v-for="(row, r) in layoutRows" class="kb-row" :style="{ '--n': [...row].length }">
          <span class="rn">{{ r + 1 }}</span>
          <div class="kb-keys">
            <div v-for="(c, i) in [...row]" class="key"
                 :title="hex(c) + (S.glyphs.status[c] && S.glyphs.status[c] !== 'ok' ? ' - ' + S.glyphs.status[c] + ' in font' : '')"
                 :class="[S.glyphs.status[c] && S.glyphs.status[c] !== 'ok' ? S.glyphs.status[c] : '', sel && sel.r === r && sel.i === i ? 'sel' : '', c.trim() ? '' : 'space', font2Chars.includes(c) ? 'f2' : '']"
                 @click="pick(r, i)"><FontText v-if="c.trim()" :path="pathFor(c)" :text="c" /><template v-else>␣</template></div>
          </div>
        </div>
      </div></div>
      <div v-else>
        <div v-for="(row, r) in layoutRows" class="field" style="margin-bottom:10px">
          <label>Row {{ r + 1 }} · {{ [...row].length }} slots</label>
          <input class="input" :value="row" :style="famStyle(fam, { fontSize: '18px', height: '40px' })" @change="setRowText(r, $event.target.value)">
          <div v-if="lenBad(r, row)" class="help" style="color:var(--bad)">Must stay {{ origLen(r) }} characters on this machine - this row won't save.</div>
        </div>
      </div>
    </div>
  </section>
  <section v-if="sel" class="card">
    <div class="card-head"><h2>Row {{ sel.r + 1 }}, slot {{ sel.i + 1 }}</h2><span class="sub">{{ hex(selChar) }}</span>
      <span class="spacer"></span><button class="btn small ghost" @click="S.sel = null">Close</button></div>
    <div class="card-body">
      <div style="display:flex;gap:16px;align-items:center;margin-bottom:14px;flex-wrap:wrap">
        <div class="key big" :class="S.glyphs.status[selChar] && S.glyphs.status[selChar] !== 'ok' ? S.glyphs.status[selChar] : ''"><FontText :path="pathFor(selChar)" :text="selChar" /></div>
        <div class="field" style="flex:1;min-width:180px">
          <label>Character</label>
          <div style="display:flex;gap:8px"><input class="input" v-model="typed" style="width:90px;font-size:18px" @keyup.enter="applyTyped">
            <button class="btn small" @click="applyTyped">Set</button></div>
          <div class="help">Type or paste any character, or pick one this font has below.</div>
        </div>
      </div>
      <div v-for="(chars, heading) in S.glyphs.unused" style="margin-bottom:12px">
        <div class="help" style="margin-bottom:4px">Unused {{ heading }} in this font · {{ chars.length }}</div>
        <div class="glyph-pal">
          <button v-for="c in chars.slice(0, 500)" :title="hex(c)" @click="setChar(sel.r, sel.i, c)"><FontText :path="mainPath" :text="c" /></button>
        </div>
      </div>
    </div>
  </section>`,
};

const ToolsPage = {
  components: { SectionCard },
  setup() {
    const tt = computed(() => section("Type test"));
    const legend = computed(() => section("Legend"));
    const legendOut = computed(() => section("Legend output"));
    const legendUrl = computed(() => (S.legendStamp ? engine.legendUrl(S.machine, S.legendStamp) : null));
    const presetNames = computed(() => Object.keys(S.data.presets || {}));
    const seedCoverage = (v) => {
      if (v === "__current__") S.coverage.chars = (layoutRows.value || []).join("");
      else if (S.data.presets[v]) S.coverage.chars = S.data.presets[v].join("");
    };
    const calib = computed(() => section("Calibration"));
    const gauge = computed(() => section("Gauge"));
    const buildAs = (target) => { S.build.target = target; runBuild(true); };
    // shaft gauge: the bore is the shaft (core_id_in, inches) + clearance (core_id_offset, mm)
    const gaugeFit = computed(() => {
      const shaft = (Number(val("core_id_in")) || 0) * 25.4;
      return { shaft, current: shaft + (Number(val("core_id_offset")) || 0) };
    });
    const bestPocket = ref(null);
    const useBestPocket = () => {
      if (!bestPocket.value) return;
      const c = Math.round((bestPocket.value - gaugeFit.value.shaft) * 1000) / 1000;
      setVal("core_id_offset", c);
      toast(`Shaft clearance set to ${c.toFixed(3)} mm (hole ${Number(bestPocket.value).toFixed(3)} mm) - Save to keep it`, "ok");
    };
    return { S, setVal, tt, legend, legendOut, legendUrl, runTypeTest, runLegend, runCoverage, presetNames, seedCoverage,
             calib, gauge, buildAs, engine, layoutRows, downloadLegend, gaugeFit, bestPocket, useBestPocket };
  },
  template: `
  <SectionCard v-if="calib" :s="calib">
    <template #actions><button class="btn small" :disabled="S.job.running" @click="buildAs('calibration')">Build calibration element</button></template>
  </SectionCard>
  <SectionCard v-if="gauge" :s="gauge" title="Shaft gauge">
    <template #actions><button class="btn small" :disabled="S.job.running" @click="buildAs('gauge')">Build shaft gauge</button></template>
    <div class="gauge-steps">
      <ol>
        <li>Build the shaft gauge, download it and print it.</li>
        <li>Slide each pocket onto the machine's real shaft. The unlabeled centre hole is your current fit ({{ gaugeFit.current.toFixed(3) }} mm); every outer pocket is engraved with its own hole diameter in mm.</li>
        <li>Pick the pocket that slides on smoothly without wobble and enter its number:</li>
      </ol>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-left:22px">
        <input class="input" type="number" step="0.005" style="width:110px" v-model.number="bestPocket" placeholder="e.g. 3.340" @keyup.enter="useBestPocket">
        <button class="btn small primary" :disabled="!bestPocket" @click="useBestPocket">Set shaft clearance</button>
        <span v-if="bestPocket" class="help">= {{ bestPocket }} − {{ gaugeFit.shaft.toFixed(3) }} mm shaft → clearance {{ (bestPocket - gaugeFit.shaft).toFixed(3) }} mm</span>
      </div>
      <p class="help" style="margin:8px 0 0 22px">4. Save. Every element for this machine then uses that hole size. If the best pocket is at either end, shift the first pocket offset and print again.</p>
    </div>
  </SectionCard>
  <SectionCard v-if="legend" :s="legend" title="Legend sheet">
    <template #actions><button class="btn small primary" :disabled="S.job.running" @click="runLegend">Generate legend</button></template>
    <div v-if="legendOut" class="fields" style="margin-top:14px">
      <div v-for="f in legendOut.fields" class="field" :key="f.key"><label>{{ f.label }}</label>
        <select class="select" :value="String(S.edits[f.key] ?? f.value)" @change="setVal(f.key, $event.target.value)">
          <option v-for="o in f.options" :value="o.value">{{ o.label }}</option></select></div>
    </div>
    <div v-if="legendUrl" class="legend-preview">
      <img :src="legendUrl" alt="Generated legend">
      <button class="btn small" @click="downloadLegend" title="The SVG plus the settings it was made from, in one .zip">Download</button>
    </div>
  </SectionCard>
`,
};

// Type test plate on the Typeface page: render a flat plate of text in the
// current font/alignment, optionally re-rendering after every change so a
// size or offset tweak shows up in the 3D view a few seconds later.
let autoTimer = null, autoPending = false;
watch(() => JSON.stringify(S.edits), () => {
  if (!S.typeTestAuto || !Object.keys(S.edits).length) return;
  clearTimeout(autoTimer);
  autoTimer = setTimeout(() => {
    if (S.job.running) { autoPending = true; return; }
    runTypeTest();
  }, 900);
});
watch(() => S.job.running, (running) => { if (!running && autoPending && S.typeTestAuto) { autoPending = false; runTypeTest(); } });

const TypeTestCard = {
  props: ["s"],
  components: { SectionCard },
  setup() {
    const toggleAuto = (v) => { S.typeTestAuto = v; try { localStorage.setItem("te.typeTestAuto", v ? "1" : ""); } catch {} };
    return { S, runTypeTest, toggleAuto };
  },
  template: `
  <section-card :s="s" title="Type test plate">
    <template #top><p class="help" style="margin-top:0">A flat plate of text in the current font and alignment - render it to check spacing, then print it before cutting a whole element. It shows up in the 3D view, seen from above.</p>
      <label class="switch" style="margin-bottom:10px"><input type="checkbox" :checked="S.typeTestAuto" @change="toggleAuto($event.target.checked)"><span>Re-render after every change</span></label></template>
    <template #actions><button class="btn small primary" :disabled="S.job.running" @click="runTypeTest">Render type test</button></template>
  </section-card>`,
};

// Font coverage, on the Typeface page with the rest of the font tools:
// which fonts have every character a layout needs.
const FontCoverageCard = {
  setup() {
    const presetNames = computed(() => Object.keys(S.data.presets || {}));
    const seedCoverage = (v) => {
      if (v === "__current__") S.coverage.chars = (layoutRows.value || []).join("");
      else if (S.data.presets[v]) S.coverage.chars = S.data.presets[v].join("");
    };
    return { S, runCoverage, presetNames, seedCoverage, engine, layoutRows };
  },
  template: `
  <section class="card">
    <div class="card-head"><h2>Font coverage</h2><span class="sub">which fonts have every character you need</span></div>
    <div class="card-body">
      <div class="fields">
        <div class="field wide">
          <label>Characters</label>
          <select class="select" @change="seedCoverage($event.target.value)" style="margin-bottom:6px">
            <option value="">Fill from…</option>
            <option v-if="layoutRows" value="__current__">Current layout</option>
            <option v-for="n in presetNames" :value="n">Preset: {{ n }}</option>
          </select>
          <textarea class="input textblock" v-model="S.coverage.chars" style="min-height:70px"></textarea>
        </div>
        <div class="field wide"><label>Font folder to search</label>
          <input class="input" v-model="S.coverage.dir" placeholder="e.g. /home/you/fonts or C:\\Windows\\Fonts"></div>
        <div class="field"><label class="switch"><input type="checkbox" v-model="S.coverage.deep"><span>Deep check (slow)</span></label>
          <div class="help">Also runs every glyph through the real outline pipeline.</div></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">
        <button class="btn primary" :disabled="S.job.running || !S.coverage.chars || !S.coverage.dir" @click="runCoverage(true)">Check current font</button>
        <button class="btn" :disabled="S.job.running || !S.coverage.chars || !S.coverage.dir" @click="runCoverage(false)">Scan the whole folder</button>
        <a v-if="S.coverage.report" class="btn ghost" :href="engine.reportUrl()" target="_blank">Open report</a>
      </div>
      <p class="help">Results stream into the build log. "Check current font" lists what the font is missing, the glyphs it has that you could swap in, and other fonts that cover the gap.</p>
    </div>
  </section>`,
};

// In the browser engine the check runs here in the page: each font's
// character map is read straight from the file (coverage.js), across the
// app's own fonts, this computer's installed fonts and the synced folder -
// whichever the user ticks. The local engine keeps its folder scan.
const COVERAGE_LIMIT = 400;
const BrowserCoverageCard = {
  components: { FontText },
  setup() {
    const presetNames = computed(() => Object.keys(S.data.presets || {}));
    const seedCoverage = (v) => {
      if (v === "__current__") S.coverage.chars = (layoutRows.value || []).join("");
      else if (S.data.presets[v]) S.coverage.chars = S.data.presets[v].join("");
    };
    const use = reactive({ app: true, local: true, folder: true });
    const busy = ref(""), result = ref(null);
    // every font to look at: {label, key, bytes(), choose()}
    async function sources() {
      const out = [];
      if (use.app) {
        if (!S.fonts) S.fonts = await engine.fonts();
        for (const f of S.fonts) out.push({ label: `${f.family} ${f.style}`.trim(), src: "app", path: f.path,
          bytes: () => engine.fontData(f.path), choose: async () => f.path });
      }
      if (use.local && S.local.status === "granted") for (const f of localfonts.state.fonts)
        out.push({ label: f.full || `${f.family} ${f.style}`, src: "computer", ps: f.ps, bytes: () => localfonts.bytes(f),
          choose: async () => (await engine.addFont(f.ps + ".ttf", await localfonts.bytes(f))).path });
      if (use.folder && S.sync.status === "ready") for (const f of fontsync.state.files)
        out.push({ label: f.name.replace(/\.(ttf|otf|ttc|otc)$/i, ""), src: "folder", rel: f.rel, bytes: () => fontsync.bytes(f),
          choose: () => fontsync.provide(engine, f) });
      return out;
    }
    const chars = computed(() => [...new Set([...S.coverage.chars].filter((c) => !/\s/.test(c)))].join(""));
    // The current font: what it lacks (font-2 characters are checked against font 2)
    async function checkCurrent() {
      busy.value = "Reading the current font…"; result.value = null;
      try {
        const f2 = String(val("font2_chars") || "");
        const main = [...chars.value].filter((c) => !f2.includes(c)).join(""), second = [...chars.value].filter((c) => f2.includes(c)).join("");
        const miss = [];
        for (const [path, cs] of [[val("path"), main], [val("font2_path") || val("path"), second]]) {
          if (!cs || !path) continue;
          const m = missingIn(await engine.fontData(path), cs);
          if (m === null) throw new Error(`can't read ${fontLabel(path)}`);
          miss.push(...m);
        }
        result.value = { kind: "current", missing: miss, font: fontLabel(val("path")) };
        if (miss.length) await scan(miss.join(""), true);
      } catch (e) { result.value = { kind: "error", text: String(e.message || e) }; }
      busy.value = "";
    }
    // Every font that has all of `need` (default: the whole character list)
    async function scan(need = chars.value, partial = false) {
      const list = await sources();
      const hits = [];
      let unreadable = 0;
      for (let k = 0; k < list.length; k++) {
        if (k % 25 === 0) { busy.value = `Checking fonts… ${k} / ${list.length}`; await new Promise((r) => setTimeout(r)); }
        let m;
        try { m = missingIn(await list[k].bytes(), need); } catch { m = null; }
        if (m === null) { unreadable++; continue; }
        if (!m.length) hits.push(list[k]);
        if (hits.length >= COVERAGE_LIMIT) break;
      }
      hits.sort((a, b) => a.label.localeCompare(b.label));
      if (partial) result.value = { ...result.value, fixes: hits, checked: list.length };
      else result.value = { kind: "scan", hits, checked: list.length, unreadable, need };
      busy.value = "";
    }
    const findAll = async () => { busy.value = "Gathering fonts…"; result.value = null; try { await scan(); } catch (e) { result.value = { kind: "error", text: String(e.message || e) }; busy.value = ""; } };
    const pick = async (hit) => {
      busy.value = `Loading ${hit.label}…`;
      try { setVal("path", await hit.choose()); toast(`Font set to ${hit.label} - Save to keep it`); }
      catch (e) { toast(String(e.message || e), "bad"); }
      busy.value = "";
    };
    // a preview face for each hit, loaded from its own bytes
    const faces = reactive({});
    let seq = 0;
    const faceOf = (hit) => {
      const key = hit.path || hit.ps || hit.rel;
      if (!(key in faces)) {
        faces[key] = null;
        const nm = `tec${++seq}`;
        Promise.resolve(hit.bytes()).then((b) => new FontFace(nm, b).load()).then((ff) => { document.fonts.add(ff); faces[key] = nm; }).catch(() => { faces[key] = ""; });
      }
      return faces[key] || null;
    };
    const sample = computed(() => S.previewText.trim() || chars.value.slice(0, 40) || "AaBbCc 0123");
    return { S, presetNames, seedCoverage, layoutRows, use, busy, result, checkCurrent, findAll, pick, faceOf, sample, chars,
             localOk: computed(() => S.local.status === "granted"), folderOk: computed(() => S.sync.status === "ready"),
             openAccess: () => (S.access = true) };
  },
  template: `
  <section class="card">
    <div class="card-head"><h2>Font coverage</h2><span class="sub">which fonts have every character you need</span></div>
    <div class="card-body">
      <div class="fields">
        <div class="field wide">
          <label>Characters</label>
          <select class="select" @change="seedCoverage($event.target.value)" style="margin-bottom:6px">
            <option value="">Fill from…</option>
            <option v-if="layoutRows" value="__current__">Current layout</option>
            <option v-for="n in presetNames" :value="n">Preset: {{ n }}</option>
          </select>
          <textarea class="input textblock" v-model="S.coverage.chars" style="min-height:70px"></textarea>
        </div>
        <div class="field wide"><label>Look in</label>
          <div style="display:flex;gap:16px;flex-wrap:wrap">
            <label class="switch"><input type="checkbox" v-model="use.app"><span>Fonts in the app</span></label>
            <label class="switch" :title="localOk ? '' : 'Allow access to this computer’s fonts first'"><input type="checkbox" v-model="use.local" :disabled="!localOk"><span>This computer's fonts{{ localOk ? ' (' + S.local.count + ')' : '' }}</span></label>
            <label class="switch" :title="folderOk ? '' : 'Sync a fonts folder first'"><input type="checkbox" v-model="use.folder" :disabled="!folderOk"><span>Fonts folder{{ folderOk ? ' · ' + S.sync.name + ' (' + S.sync.count + ')' : '' }}</span></label>
          </div>
          <div v-if="!localOk || !folderOk" class="help">More fonts to search: <a href="#" @click.prevent="openAccess">allow this computer's fonts or sync a folder</a>.</div>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center">
        <button class="btn primary" :disabled="!!busy || !chars" @click="checkCurrent">Check current font</button>
        <button class="btn" :disabled="!!busy || !chars" @click="findAll">Find fonts with all of these</button>
        <span v-if="busy" class="help">{{ busy }}</span>
      </div>
      <template v-if="result">
        <div v-if="result.kind === 'error'" class="note bad" style="margin-top:12px">{{ result.text }}</div>
        <template v-else-if="result.kind === 'current'">
          <div v-if="!result.missing.length" class="note ok" style="margin-top:12px">{{ result.font }} has every character.</div>
          <div v-else class="note warn" style="margin-top:12px">{{ result.font }} is missing <b style="font-size:16px">{{ result.missing.join(' ') }}</b>.
            <template v-if="result.fixes"> {{ result.fixes.length ? result.fixes.length + (result.fixes.length >= 400 ? '+' : '') + ' fonts have them - below.' : 'None of the ' + result.checked + ' fonts searched has them all.' }}</template></div>
        </template>
        <div v-else class="help" style="margin-top:12px">{{ result.hits.length }}{{ result.hits.length >= 400 ? '+' : '' }} of {{ result.checked }} fonts have all {{ result.need.length }} characters{{ result.unreadable ? ' (' + result.unreadable + ' couldn’t be read)' : '' }}.</div>
        <div v-if="(result.hits || result.fixes || []).length" class="list cov-list">
          <div v-for="h in (result.hits || result.fixes)" :key="h.path || h.ps || h.rel" class="font-row" @click="pick(h)" title="Use this font">
            <div class="preview" :style="faceOf(h) ? { fontFamily: faceOf(h) + ', var(--sans)' } : {}">{{ sample }}</div>
            <div class="fam">{{ h.label }} <span class="chip">{{ h.src }}</span></div>
          </div>
        </div>
      </template>
    </div>
  </section>`,
};

// Shown when the app opens (in-browser engine): two ways to bring the
// user's own fonts in, each needing the browser's OK - this computer's
// installed fonts, and a synced fonts folder. Both feed every font
// setting, the font picker and font coverage.
const ACCESS_SKIP = "te.accessSkip";
const AccessPrompt = {
  setup() {
    const err = ref("");
    const never = ref(false);
    const run = async (fn) => { err.value = ""; try { await fn(); } catch (e) { if (e.name !== "AbortError") err.value = String(e.message || e); } };
    const close = () => { if (never.value) { try { localStorage.setItem(ACCESS_SKIP, "1"); } catch {} } S.access = false; };
    return { S, err, never, run, close, localfonts, fontsync };
  },
  template: `
  <div class="modal-bg" @click.self="close">
    <div class="modal small fit" role="dialog" aria-modal="true" aria-labelledby="access-h">
      <div class="head"><h2 id="access-h">Use your own fonts?</h2><span class="spacer"></span><button class="btn small ghost" @click="close" aria-label="Close">✕</button></div>
      <div class="access-body">
        <p class="help" style="margin-top:0">The app ships with a few free fonts. Let it see yours and every font setting, the font picker and font coverage can use them. Nothing is uploaded - it all stays in this browser.</p>
        <div class="access-row">
          <div><b>Fonts installed on this computer</b><div class="help">The browser asks once.</div></div>
          <span v-if="S.local.status === 'granted'" class="chip ok">✓ {{ S.local.count }} fonts</span>
          <span v-else-if="S.local.status === 'unsupported'" class="help">Chrome or Edge only</span>
          <span v-else-if="S.local.status === 'loading'" class="help">Loading…</span>
          <button v-else class="btn small primary" @click="run(localfonts.request)">Allow</button>
        </div>
        <div class="access-row">
          <div><b>A fonts folder</b><div class="help">Pick it once; it's re-read every visit.</div></div>
          <span v-if="S.sync.status === 'ready'" class="chip ok">✓ {{ S.sync.name }} · {{ S.sync.count }}</span>
          <span v-else-if="!fontsync.supported" class="help">Chrome or Edge only</span>
          <span v-else-if="S.sync.status === 'scanning'" class="help">Reading…</span>
          <button v-else-if="S.sync.status === 'needs-permission'" class="btn small primary" @click="run(fontsync.reconnect)">Reconnect {{ S.sync.name }}</button>
          <button v-else class="btn small primary" @click="run(fontsync.choose)">Choose folder…</button>
        </div>
        <p v-if="err" class="help" style="color:var(--bad)">{{ err }}</p>
      </div>
      <div class="foot"><label class="help" style="display:flex;gap:6px;align-items:center;margin-right:auto"><input type="checkbox" v-model="never"> Don't ask when the app opens</label>
        <button class="btn primary" @click="close">{{ S.local.status === 'granted' || S.sync.status === 'ready' ? 'Done' : 'Not now' }}</button></div>
    </div>
  </div>`,
};

const FontPicker = {
  components: { FontText },
  setup() {
    const q = ref("");
    const manual = ref(S.picker.current || "");
    const list = ref(null);
    const listEl = ref(null);
    const visible = reactive({});
    let io;
    function observe() {
      io?.disconnect();
      io = new IntersectionObserver((ents) => ents.forEach((e) => { if (e.isIntersecting) visible[e.target.dataset.path] = true; }),
        { root: listEl.value, rootMargin: "300px" });
      listEl.value?.querySelectorAll(".font-row").forEach((el) => io.observe(el));
    }
    onMounted(async () => {
      if (!S.fonts) S.fonts = await engine.fonts();
      list.value = S.fonts;
      await nextTick();
      document.getElementById("font-q")?.focus();
      observe();
    });
    const shown = computed(() => {
      if (!list.value) return [];
      const toks = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      const r = toks.length ? list.value.filter((f) => { const h = (f.family + " " + f.style + " " + f.path).toLowerCase(); return toks.every((t) => h.includes(t)); }) : list.value;
      return r.slice(0, 800);
    });
    watch(shown, () => nextTick(observe));
    const famOf = (p) => (visible[p] ? fontFamily(p) : null);
    // the previews show the user's own text when they've typed some
    const sample = computed(() => S.previewText.trim() || (S.picker.sample || "AaBbCc 0123 &?!").split("\n")[0]);
    const choose = (p) => { setVal(S.picker.key, p); S.picker = null; };
    const close = () => (S.picker = null);
    // In-browser engine: the page can't see the disk, so fonts are added -
    // from the fonts installed on this computer (Chrome/Edge's Local Font
    // Access, asks permission once) or as uploaded files. Both are kept in
    // browser storage for next time.
    const browserMode = engine.kind === "browser";
    // this computer's fonts: one shared list (localfonts.js), loaded once allowed
    const localFonts = computed(() => (S.local.status === "granted" ? localfonts.state.fonts : null));
    const localErr = ref("");
    const busy = ref("");
    const canLocal = localfonts.supported;
    async function loadLocal() { localErr.value = ""; await localfonts.request(); if (S.local.status !== "granted") localErr.value = localfonts.state.error; }
    const shownLocal = computed(() => {
      if (!localFonts.value) return [];
      const toks = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      return localFonts.value.filter((f) => { const h = (f.family + " " + f.style + " " + f.full).toLowerCase(); return toks.every((t) => h.includes(t)); }).slice(0, 400);
    });
    async function addAndChoose(name, buffer) {
      busy.value = "Adding " + name + "…";
      try {
        const entry = await engine.addFont(name, buffer);
        S.fonts = null;
        choose(entry.path);
      } catch (e) { localErr.value = String(e.message || e); }
      busy.value = "";
    }
    const pickLocal = async (f) => addAndChoose(f.ps + ".ttf", await localfonts.bytes(f));
    const upload = async (ev) => { const file = ev.target.files[0]; if (file) addAndChoose(file.name, await file.arrayBuffer()); };
    // Installed-font previews: load each by its exact PostScript name with a
    // local() FontFace, only once its row scrolls into view. (Matching by
    // full name in CSS fails for most fonts - they fell back to the default.)
    const localFaces = reactive({});
    let localSeq = 0;
    function localFamily(f) {
      if (!visible["local:" + f.ps]) return null;
      if (!(f.ps in localFaces)) {
        localFaces[f.ps] = null;
        const name = `tel${++localSeq}`;
        new FontFace(name, `local("${f.ps.replace(/"/g, "")}")`).load()
          .then((ff) => { document.fonts.add(ff); localFaces[f.ps] = name; })
          .catch(() => { localFaces[f.ps] = ""; });
      }
      return localFaces[f.ps] || null;
    }
    watch(localFonts, () => nextTick(observe));
    // the synced fonts folder (fontsync.js): listed by file name, previews
    // read from the folder as rows scroll into view, handed to the engine
    // only when picked
    const syncOk = fontsync.supported;
    const shownSync = computed(() => {
      if (S.sync.status !== "ready") return [];
      const toks = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      return fontsync.state.files.filter((f) => { const h = f.rel.toLowerCase(); return toks.every((t) => h.includes(t)); }).slice(0, 600);
    });
    watch(shownSync, () => nextTick(observe));
    const syncFaces = reactive({});
    let syncSeq = 0;
    function syncFamily(f) {
      if (!visible["sync:" + f.rel]) return null;
      if (!(f.rel in syncFaces)) {
        syncFaces[f.rel] = null;
        const nm = `tes${++syncSeq}`;
        fontsync.bytes(f).then((buf) => new FontFace(nm, buf).load())
          .then((ff) => { document.fonts.add(ff); syncFaces[f.rel] = nm; })
          .catch(() => { syncFaces[f.rel] = ""; });
      }
      return syncFaces[f.rel] || null;
    }
    const syncErr = ref("");
    const syncDo = async (fn) => { syncErr.value = ""; try { await fn(); } catch (e) { if (e.name !== "AbortError") syncErr.value = String(e.message || e); } };
    const pickSync = async (f) => {
      busy.value = "Loading " + f.name + "…";
      try { choose(await fontsync.provide(engine, f)); } catch (e) { localErr.value = String(e.message || e); }
      busy.value = "";
    };
    const fontLabelOf = (f) => f.name.replace(/\.(ttf|otf|ttc|otc)$/i, "");
    return { S, q, manual, shown, list, listEl, visible, sample, choose, close,
             browserMode, localFonts, localErr, busy, canLocal, loadLocal, shownLocal, pickLocal, upload, localFamily,
             syncOk, shownSync, syncFamily, syncErr, syncDo, pickSync, fontsync, fontLabelOf };
  },
  template: `
  <div class="modal-bg" @click.self="close" @keydown.esc="close">
    <div class="modal" role="dialog" aria-modal="true">
      <div class="head"><h2>{{ S.picker.label }}</h2><span class="spacer"></span><button class="btn small ghost" @click="close" aria-label="Close">✕</button></div>
      <div class="tools" style="flex-wrap:wrap">
        <div class="search" style="flex:1;min-width:180px"><input id="font-q" class="input" style="width:100%" v-model="q" :placeholder="browserMode ? 'Search fonts…' : 'Search installed fonts…'" @keydown.esc="close"></div>
        <input class="input" style="flex:1;min-width:180px" v-model="S.previewText" placeholder="Preview your own text…" title="Every preview shows this text while it isn't empty" @keydown.esc="close">
        <span class="chip" v-if="list && !browserMode">{{ shown.length }}{{ shown.length === 800 ? '+' : '' }} / {{ list.length }}</span>
      </div>
      <div v-if="browserMode" class="tools" style="flex-wrap:wrap">
        <template v-if="syncOk">
          <button v-if="S.sync.status === 'none'" class="btn small primary" @click="syncDo(fontsync.choose)" title="Pick your fonts folder once - it's re-read every visit, and every font setting can use it">Sync a fonts folder…</button>
          <button v-else-if="S.sync.status === 'needs-permission'" class="btn small primary" @click="syncDo(fontsync.reconnect)">Reconnect the {{ S.sync.name }} folder</button>
          <span v-else-if="S.sync.status === 'scanning'" class="help">Reading {{ S.sync.name }}…</span>
          <template v-else-if="S.sync.status === 'ready'"><span class="chip ok">{{ S.sync.name }} · {{ S.sync.count }} fonts</span>
            <button class="btn small ghost" @click="syncDo(fontsync.choose)">Change folder</button></template>
        </template>
        <button v-if="canLocal && !localFonts" class="btn small" @click="loadLocal">Show fonts installed on this computer</button>
        <label class="btn small">Upload a font file…<input type="file" accept=".ttf,.otf,.ttc,.otc" style="display:none" @change="upload"></label>
        <span v-if="busy" class="help">{{ busy }}</span>
        <span v-if="localErr" class="help" style="color:var(--bad)">{{ localErr }}</span>
        <span v-if="!canLocal" class="help">This browser can't list installed fonts or sync a folder (Chrome and Edge can) - upload a font file instead.</span>
        <span v-if="syncErr" class="help" style="color:var(--bad)">{{ syncErr }}</span>
      </div>
      <div class="list" ref="listEl">
        <div v-if="!list" style="padding:20px;color:var(--text-3)">Loading fonts…</div>
        <div v-if="browserMode && list" class="list-label">In the app{{ list.some(f => f.source === 'yours') ? ' (bundled + yours)' : ' (bundled)' }}</div>
        <div v-for="f in shown" :key="f.path" class="font-row" :data-path="f.path" :class="{ sel: f.path === S.picker.current }" @click="choose(f.path)">
          <div class="preview"><FontText v-if="visible[f.path]" :path="f.path" :text="sample" /><span v-else>{{ sample }}</span></div>
          <div class="fam" :title="f.path">{{ f.family }} <span style="color:var(--text-3)">{{ f.style }}</span></div>
        </div>
        <template v-if="browserMode && S.sync.status === 'ready'">
          <div class="list-label">Your fonts folder · {{ S.sync.name }} · {{ shownSync.length }}{{ shownSync.length === 600 ? '+' : '' }} of {{ S.sync.count }}</div>
          <div v-for="f in shownSync" :key="f.rel" class="font-row" :data-path="'sync:' + f.rel" @click="pickSync(f)">
            <div class="preview" :style="syncFamily(f) ? { fontFamily: syncFamily(f) + ', var(--sans)' } : {}">{{ sample }}</div>
            <div class="fam" :title="f.rel">{{ fontLabelOf(f) }}</div>
          </div>
        </template>
        <template v-if="browserMode && localFonts">
          <div class="list-label">On this computer · {{ localFonts.length }} fonts · click one to use it</div>
          <div v-for="f in shownLocal" :key="f.ps" class="font-row" :data-path="'local:' + f.ps" @click="pickLocal(f)">
            <div class="preview" :style="localFamily(f) ? { fontFamily: localFamily(f) + ', var(--sans)' } : {}">{{ sample }}</div>
            <div class="fam">{{ f.family }} <span style="color:var(--text-3)">{{ f.style }}</span></div>
          </div>
          <p v-if="!shownLocal.length" class="help" style="padding:0 18px">No installed font matches "{{ q }}".</p>
        </template>
      </div>
      <div class="foot" v-if="!browserMode">
        <input class="input" style="flex:1;font-family:var(--mono);font-size:12px;min-width:0" v-model="manual" placeholder="…or paste a font file path">
        <button class="btn primary" :disabled="!manual" @click="choose(manual)">Use this file</button>
      </div>
    </div>
  </div>`,
};

const App = {
  components: { SectionCard, LayoutPage, ToolsPage, ProfilesCard, FontCard, WorkflowStrip, FontPicker, TypeTestCard, FontCoverageCard, BrowserCoverageCard, AccessPrompt },
  setup() {
    const viewerEl = ref(null);
    const logRef = ref(null);
    const searchHits = computed(() => {
      const toks = S.search.toLowerCase().split(/\s+/).filter(Boolean);
      if (!toks.length || !S.data) return [];
      return Object.values(fieldsByKey.value).filter((f) => {
        const h = (f.label + " " + f.key + " " + (f.help || "") + " " + f.section).toLowerCase();
        return toks.every((t) => h.includes(t));
      }).slice(0, 100);
    });
    const groupOf = (f) => (groups.value.find((g) => g.sections.includes(f.section)) || groups.value.find((g) => g.id === "tools"))?.label;
    // Phones can't run the local engine (yet), so they get a "what this is"
    // page instead of install steps they can't follow.
    const phone = computed(() => !S.forceDesktop && matchMedia("(pointer: coarse)").matches && innerWidth < 900);
    const shareLink = async () => {
      const url = "https://type-elements.leonardchau.com/app/";
      try {
        if (navigator.share) await navigator.share({ title: "Type Elements", text: "Typewriter type elements from any font - open on a computer", url });
        else { await navigator.clipboard.writeText(url); S.shared = true; }
      } catch {}
    };
    onMounted(async () => {
      viewer = new Viewer(viewerEl.value);
      logEl = logRef.value;
      applyTheme();
      matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme);
      start();
    });
    // Phones see a short "what this is" page first: the local engine can't run
    // on them, and the in-browser one is heavy for a phone. They can go on.
    async function start() {
      if (phone.value) { S.phoneLanding = true; return; }
      S.phoneLanding = false;
      if (engine.kind === "browser") { S.booting = true; engine.onStatus((s) => (S.engineStatus = s)); }
      else if (engine.hosted) S.connecting = true;
      const ok = await engine.ping().catch((e) => { S.engineError = String(e.message || e); return false; });
      S.connecting = false; S.booting = false;
      if (ok && engine.kind === "browser") { try { localStorage.setItem("te.engineBooted", "1"); } catch {} }
      if (!ok) { S.engineDown = true; S.engineUrl = engine.base; return; }
      if (engine.kind === "browser") {
        fontsync.onChange((st) => {
          const wasReady = S.sync.status === "ready";
          Object.assign(S.sync, { status: st.status, name: st.name, count: st.files.length, error: st.error });
          // a folder that just became readable may hold this config's fonts
          if (!wasReady && st.status === "ready" && S.machine && S.data && !dirty.value) loadMachine(S.machine, true);
        });
        localfonts.onChange((st) => {
          const was = S.local.status;
          Object.assign(S.local, { status: st.status, count: st.fonts.length, error: st.error });
          if (was !== "granted" && st.status === "granted" && S.machine && S.data && !dirty.value) loadMachine(S.machine, true);
        });
        // ask on open unless both are in place (or the user said not to)
        Promise.all([fontsync.restore(), localfonts.restore()]).then(() => {
          let skip = false;
          try { skip = !!localStorage.getItem(ACCESS_SKIP); } catch {}
          const localDone = S.local.status === "granted" || !localfonts.supported;
          const folderDone = S.sync.status === "ready" || !fontsync.supported;
          if (!skip && !(localDone && folderDone)) S.access = true;
        });
      }
      S.machines = (await engine.machines()).groups;
      const all = S.machines.flatMap((g) => g.machines.filter((m) => m.available).map((m) => m.key));
      await loadMachine(all.includes(S.machine) ? S.machine : all[0], true);
      engine.defaultFontDir().then((d) => { if (!S.coverage.dir) S.coverage.dir = d; }).catch(() => {});
      addEventListener("keydown", (e) => {
        const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName);
        if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); save(); }
        else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runBuild(!e.shiftKey); }
        else if (e.key === "/" && !typing) { e.preventDefault(); document.getElementById("search")?.focus(); }
        else if (e.key === "Escape" && S.picker) S.picker = null;
      });
      addEventListener("beforeunload", (e) => { if (dirty.value) e.preventDefault(); });
    }
    const tryOnPhone = () => { S.forceDesktop = true; start(); };
    const retryEngine = () => { engine.setBase(S.engineUrl); location.reload(); };
    return { S, setHelpAll, groups, currentGroup, section, dirty, save, discard, resetToMaster, openConfigs, openConfig, retryEngine, phone, shareLink, tryOnPhone, loadMachine, runBuild, saveCopy, downloadBuild, importSettings,
             viewerEl, logRef, searchHits, jumpTo, groupOf, engine, applyTheme, badGlyphs, openGroup,
             cancel: () => engine.cancel(), baseName, location,
             // the site's home page: same origin on the hosted site, the public site otherwise
             homeUrl: location.protocol === "https:" ? "/" : "https://type-elements.leonardchau.com/" };
  },
  template: `
  <div v-if="S.phoneLanding" class="connect">
    <div class="connect-card phone-card">
      <div class="brand" style="font-size:20px;margin-bottom:6px"><span class="dot">T</span>Type Elements</div>
      <img src="https://type-elements.leonardchau.com/assets/og/selectric-render.png" alt="A generated IBM Selectric typeball" class="phone-hero">
      <h1>Typewriter type elements, from any font.</h1>
      <p>Pick a machine, choose a typeface, arrange the keyboard, and export a print-ready 3D model of a working Selectric ball, Blickensderfer wheel or Hammond shuttle.</p>
      <p class="note info" style="margin:14px 0">Best on a computer. It runs entirely in your browser, which is a lot to ask of a phone - it may be slow or run out of memory.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn primary" @click="shareLink">{{ S.shared ? 'Link copied' : 'Send this link to myself' }}</button>
        <a class="btn" href="/">Read about it</a>
        <a class="btn ghost" href="/v5-performance/">How fast is it?</a>
      </div>
      <p class="help" style="margin-top:14px"><a href="#" @click.prevent="tryOnPhone">Try it here anyway</a></p>
    </div>
  </div>
  <div v-else-if="S.engineDown && engine.kind === 'browser'" class="connect">
    <div class="connect-card">
      <div class="brand" style="font-size:20px;margin-bottom:6px"><span class="dot">T</span>Type Elements</div>
      <h1>The engine couldn't start in this browser</h1>
      <p class="note bad">{{ S.engineError || 'Unknown error' }}</p>
      <p>It needs a recent Chrome, Edge or Firefox with WebAssembly. You can also run the engine on your computer instead.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn primary" @click="location.reload()">Try again</button>
        <button class="btn" @click="engine.setMode('local')">Use the local engine</button></div>
    </div>
  </div>
  <div v-else-if="S.engineDown" class="connect">
    <div class="connect-card">
      <div class="brand" style="font-size:20px;margin-bottom:6px"><span class="dot">T</span>Type Elements</div>
      <h1>Start the engine on your computer</h1>
      <p>This page is the interface. The geometry engine runs on your own machine - nothing is uploaded and no server does the work. It isn't answering at <code>{{ S.engineUrl }}</code>.</p>
      <ol>
        <li>Get the code: <code>git clone https://github.com/dairyking98/Type-Elements</code> (branch <code>web-gui</code>) and set up <code>v4/</code> per its README.</li>
        <li>Install the server's two extras: <code>v4/.venv/bin/python3 -m pip install fastapi uvicorn</code></li>
        <li>Run it: <code>v4/.venv/bin/python3 v5/server.py</code> (Windows: <code>v4\\.venv\\Scripts\\python v5\\server.py</code>)</li>
        <li>Come back and press Retry. Chrome/Edge may ask to let this site reach apps on your device - allow it.</li>
      </ol>
      <div class="row" style="display:flex;gap:8px;margin-top:14px">
        <input class="input" style="flex:1" v-model="S.engineUrl" aria-label="Engine address">
        <button class="btn primary" @click="retryEngine">Retry</button>
      </div>
      <p class="help">Or skip all that: <a href="#" @click.prevent="engine.setMode('browser')">run the engine in this browser instead</a> - nothing to install.</p>
    </div>
  </div>
  <div v-else class="shell">
    <header class="topbar">
      <a class="brand brand-link" :href="homeUrl" title="Type Elements home"><span class="dot">T</span><span class="label">Type Elements</span></a>
      <select class="select" :value="S.machine" @change="loadMachine($event.target.value)" style="width:190px;flex-shrink:1;min-width:120px" aria-label="Machine" title="Which typewriter the element is for - each keeps its own settings">
        <optgroup v-for="g in S.machines" :label="g.group">
          <option v-for="m in g.machines" :value="m.key" :disabled="!m.available">{{ m.label }}{{ m.warning ? ' — ⚠ untested' : '' }}</option>
        </optgroup>
      </select>
      <button v-if="S.data" class="chip chip-btn hide-md" :title="'Master: ' + S.data.master_path + ' · running copy: ' + S.data.running_path + ' · click to open a different config'" @click="openConfigs">{{ baseName(S.data.master_path) }} ▾</button>
      <span v-if="dirty" class="chip dirty">● Unsaved</span>
      <span v-else-if="S.data" class="chip ok hide-sm">Saved</span>
      <div class="seg" role="tablist">
        <button :class="{ on: S.view === 'settings' }" @click="S.view = 'settings'">Settings</button>
        <button :class="{ on: S.view === 'build' }" @click="S.view = 'build'">Preview{{ S.job.running ? ' ⟳' : '' }}</button>
      </div>
      <span class="spacer"></span>
      <div class="search"><input id="search" class="input" v-model="S.search" placeholder="Search settings   /" @focus="S.view = 'settings'"></div>
      <button class="btn hide-sm help-all" :class="{ on: S.helpAll }" @click="setHelpAll(!S.helpAll)" :aria-pressed="S.helpAll"
              :title="S.helpAll ? 'Hide the help under every setting (each ⓘ still shows its own)' : 'Show the help under every setting'">{{ S.helpAll ? 'Hide help' : 'Show help' }}</button>
      <button class="btn hide-sm" :disabled="!dirty" @click="discard" title="Throw away unsaved changes">Discard</button>
      <button class="btn primary" :disabled="!dirty" @click="save" title="Ctrl+S">Save</button>
      <select class="select hide-md" v-model="S.theme" @change="applyTheme" style="width:88px" aria-label="Theme" title="Theme">
        <option value="auto">Auto</option><option value="light">Light</option><option value="dark">Dark</option><option value="night" title="Every color inverted">Night</option>
      </select>
    </header>

    <div class="body" :class="'view-' + S.view">
      <div class="pills" v-if="S.view === 'settings'">
        <button v-for="g in groups" :class="{ on: currentGroup && g.id === currentGroup.id && !S.search }" :title="g.blurb" @click="openGroup(g.id)">{{ g.label }}{{ g.id === 'layout' && badGlyphs.length ? ' ●' : '' }}</button>
      </div>
      <nav class="nav">
        <div class="nav-label">{{ S.data ? S.data.label : '' }}</div>
        <button v-for="g in groups" class="nav-item" :class="{ active: currentGroup && g.id === currentGroup.id && !S.search }" :title="g.blurb" @click="openGroup(g.id)">
          <span class="ico">{{ g.icon }}</span>{{ g.label }}
          <span v-if="g.id === 'layout' && badGlyphs.length" class="flag" title="Characters missing from the font"></span>
          <span v-else-if="g.count" class="count">{{ g.count }}</span>
        </button>
        <div class="nav-label">Machine</div>
        <button class="nav-item" @click="openConfigs" title="Load a settings file from a download, or open another config for this machine"><span class="ico">⇪</span>Open config…</button>
        <button class="nav-item" @click="resetToMaster" title="Put every setting for this machine back to the app's defaults"><span class="ico">↺</span>Reset to defaults</button>
        <button v-if="engine.kind === 'browser'" class="nav-item" @click="S.access = true" title="Let the app use this computer's fonts or a fonts folder"><span class="ico">A</span>Your fonts…</button>
        <div class="nav-label">Engine</div>
        <button class="nav-item" :class="{ active: engine.mode === 'browser' }" @click="engine.mode !== 'browser' && engine.setMode('browser')" title="Runs entirely in this tab - nothing to install"><span class="ico">◍</span>In this browser</button>
        <button class="nav-item" :class="{ active: engine.mode === 'local' }" @click="engine.mode !== 'local' && engine.setMode('local')" title="v5/server.py running on this computer"><span class="ico">⌁</span>Local engine</button>
      </nav>

      <main class="main" v-if="S.data">
        <template v-if="S.search">
          <div class="page-head"><h1>Search</h1><p>{{ searchHits.length }} setting{{ searchHits.length === 1 ? '' : 's' }} match "{{ S.search }}".</p></div>
          <div class="card"><div class="card-body" style="padding:4px 0">
            <div v-for="f in searchHits" class="font-row" style="grid-template-columns:1fr auto" @click="jumpTo(f)">
              <div><div>{{ f.label }}</div><div style="font-size:12px;color:var(--text-3)">{{ f.help }}</div></div>
              <span class="chip">{{ groupOf(f) }} · {{ f.section }}</span>
            </div>
            <p v-if="!searchHits.length" class="help" style="padding:0 16px">Nothing matches.</p>
          </div></div>
        </template>
        <template v-else-if="currentGroup">
          <div class="page-head"><h1>{{ currentGroup.label }}</h1><p>{{ currentGroup.blurb }}</p></div>
          <WorkflowStrip v-if="currentGroup.id === 'typeface'" />
          <div v-if="S.data.warning" class="note advanced machine-warning">
            <b>{{ S.data.warning.short }}</b>
            <details><summary>Why</summary><p style="margin:6px 0 0;font-weight:400">{{ S.data.warning.long }}</p></details>
          </div>
          <LayoutPage v-if="currentGroup.custom === 'layout' && S.data.cfg.layout && S.data.cfg.layout.rows" />
          <template v-for="name in (currentGroup.custom === 'tools' ? [] : currentGroup.sections)" :key="name">
            <TypeTestCard v-if="name === 'Type test'" :s="section(name)" />
            <template v-else-if="name === 'Font & Alignment'"><FontCard :s="section(name)" /><ProfilesCard /></template>
            <SectionCard v-else :s="section(name)" />
          </template>
          <template v-if="currentGroup.id === 'typeface'"><BrowserCoverageCard v-if="engine.kind === 'browser'" /><FontCoverageCard v-else /></template>
          <ToolsPage v-if="currentGroup.custom === 'tools'" />
        </template>
      </main>
      <main class="main" v-else>
        <div v-if="S.booting" class="card boot-card">
          <div class="card-body">
            <h2 style="margin:0 0 6px;font-size:16px">Starting the engine in your browser</h2>
            <p v-if="S.bootedBefore" class="help" style="margin:0 0 12px">Everything comes from your browser's cache - starting Python and the engine takes a few seconds. Nothing is uploaded; everything runs on this computer.</p>
            <p v-else class="help" style="margin:0 0 12px">First visit downloads about 35 MB (Python, the geometry engine and Type Elements itself) - after that it's cached and starts in a few seconds. Nothing is uploaded; everything runs on this computer.</p>
            <div class="progress"><div :style="{ width: ((S.engineStatus && S.engineStatus.progress) || 0.03) * 100 + '%' }"></div></div>
            <p class="help" style="margin:8px 0 0">{{ S.engineStatus ? S.engineStatus.text : 'Starting…' }}</p>
          </div>
        </div>
        <div v-else-if="S.connecting" class="note info">Connecting to the engine on your computer at <b>{{ engine.base }}</b>…
          If your browser is asking whether this site may access apps or devices on your local network, choose <b>Allow</b>.</div>
        <p v-else style="color:var(--text-3)">Loading…</p>
      </main>

      <aside class="side">
        <div class="viewer" ref="viewerEl">
          <div class="overlay">
            <span v-if="S.build.stl" class="chip">{{ S.build.stl.size.x.toFixed(1) }} × {{ S.build.stl.size.y.toFixed(1) }} × {{ S.build.stl.size.z.toFixed(1) }} mm</span>
            <span v-if="S.build.stl" class="chip">{{ Math.round(S.build.stl.triangles).toLocaleString() }} triangles</span>
          </div>
          <div v-if="!S.build.stl" class="empty">Nothing built for this machine yet.<br>Preview is quick; Render adds the real draft angle.</div>
        </div>
        <div class="buildbar">
          <div class="row">
            <select class="select" v-model="S.build.target" style="flex:1;min-width:140px" aria-label="Build target" v-if="S.data" title="What to build: the element itself, or a test or helper part">
              <option v-for="t in S.data.targets" :value="t.value">{{ t.label }}</option>
            </select>
            <button class="btn" :disabled="S.job.running" @click="runBuild(true)" title="Quick, no draft angle (Ctrl+Enter)">Preview</button>
            <button class="btn primary" :disabled="S.job.running" @click="runBuild(false)" title="Full quality with draft (Ctrl+Shift+Enter)">Render</button>
            <button v-if="S.job.running" class="btn danger" @click="cancel">Stop</button>
          </div>
          <div class="row">
            <div class="progress" :class="S.job.state"><div :style="{ width: (S.job.progress * 100) + '%' }"></div></div>
            <span class="chip" style="min-width:64px;justify-content:center">{{ S.job.running ? S.job.label + ' ' : '' }}{{ S.job.elapsed ? S.job.elapsed.toFixed(0) + 's' : '—' }}<template v-if="S.job.running && S.job.eta != null && S.job.elapsed > 2">&nbsp;· ~{{ Math.max(1, Math.round(S.job.eta)) }}s left</template></span>
          </div>
          <div v-if="S.job.running && S.job.phase" class="help" style="margin-top:-4px">{{ S.job.label }}: {{ S.job.phase }}</div>
          <div class="row" v-if="S.build.stl && !S.job.running">
            <button class="btn small primary" @click="downloadBuild" title="One .zip: the STL, the settings it was built from (load them back with Open config), and a calibration's mapping">Download STL + settings</button>
            <button v-if="engine.kind !== 'browser'" class="btn small" @click="saveCopy" title="Timestamped copy + config sidecar in output/saved">Save a copy</button>
            <span class="help" style="flex-basis:100%">The .zip also holds every setting this was built from - Open config &gt; Load a settings file rebuilds it exactly.</span>
          </div>
          <details>
            <summary class="help" style="cursor:pointer">Debug views</summary>
            <div class="row" style="margin-top:8px">
              <label class="switch"><input type="checkbox" v-model="S.build.crossSection"><span>Cross-section at</span></label>
              <input class="input" type="number" v-model.number="S.build.crossAngle" :disabled="!S.build.crossSection" style="width:76px" title="Cut plane angle (deg)"><span class="help">°</span>
              <label class="switch"><input type="checkbox" v-model="S.build.cutBodies"><span>Only the cut bodies</span></label>
            </div>
          </details>
          <div v-if="S.job.issues.length" class="summary">
            <div v-for="i in S.job.issues.slice(0, 6)" class="item note warn" style="margin:0">{{ i }}</div>
            <div v-if="S.job.issues.length > 6" class="help">+{{ S.job.issues.length - 6 }} more in the log</div>
          </div>
          <div class="log" ref="logRef"><div v-for="l in S.job.log" :class="l.c">{{ l.t }}</div><div v-if="S.job.partial" class="c">{{ S.job.partial }}</div><div v-if="!S.job.log.length" class="c">Build output appears here.</div></div>
        </div>
      </aside>
    </div>

    <FontPicker v-if="S.picker" />
    <AccessPrompt v-if="S.access && !S.picker" />
    <div v-if="S.configs" class="modal-bg" @click.self="S.configs = null">
      <div class="modal small" role="dialog" aria-modal="true">
        <div class="head"><h2>Open a config for {{ S.data.label }}</h2><span class="spacer"></span><button class="btn small ghost" @click="S.configs = null">✕</button></div>
        <div class="tools" style="flex-wrap:wrap">
          <label class="btn small primary">Load a settings file…<input type="file" accept=".yaml,.yml,.zip" style="display:none" @change="importSettings($event.target.files[0]); $event.target.value = ''"></label>
          <span class="help">A download's .zip or its .settings.yaml - rebuilds that print exactly, on whichever machine it was for.</span>
          <p class="help" style="margin:0;flex-basis:100%">Or open a config below. Edits go to a running copy next to it; the config itself is never changed.</p></div>
        <div class="list">
          <div v-for="c in S.configs.configs" class="font-row" :class="{ sel: c.path === S.configs.current }" @click="openConfig(c.path)" style="grid-template-columns:1fr auto">
            <div><div>{{ c.label }}</div><div class="help" style="font-size:12px;color:var(--text-3)">{{ c.path }}</div></div>
            <span class="chip">{{ c.path === S.configs.default ? 'default' : c.kind }}</span>
          </div>
        </div>
        <div class="foot"><span class="help">Saved copies (Save a copy) appear here too.</span></div>
      </div>
    </div>
    <div v-if="S.toast" class="toast note" :class="S.toast.kind === 'bad' ? 'bad' : S.toast.kind === 'ok' ? 'ok' : 'info'">{{ S.toast.msg }}</div>
  </div>`,
};

createApp(App).mount("#app");
