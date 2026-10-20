import { createApp, reactive, ref, computed, watch, nextTick, onMounted } from "vue";
import { engine } from "./engine.js";
import { Viewer } from "./viewer.js";

// ---------------------------------------------------------------- grouping
// tune.py's per-machine sections (plus the controls it built by hand),
// regrouped by what the user is doing. A machine only sees groups it has
// something in; any section no group claims lands in Element.
const GROUPS = [
  { id: "typeface", label: "Typeface", icon: "Aa", sections: ["Font & Alignment"], custom: "profiles",
    blurb: "The fonts every struck character is cut from, with sizing and alignment. Save a combination as a profile to reuse it." },
  { id: "layout", label: "Layout", icon: "⌨", sections: ["Character", "Row baselines"], custom: "layout",
    blurb: "Which character sits in which slot, drawn in the real font. Anything the font lacks is flagged red." },
  { id: "element", label: "Element", icon: "◎", sections: ["Element", "Cosmetics", "Bands", "Rib", "Ticks"],
    blurb: "Physical dimensions of the element body - mostly real machine measurements." },
  { id: "branding", label: "Logo & label", icon: "✎", sections: ["Logo", "Label"],
    blurb: "Text and marks engraved on the element itself." },
  { id: "print", label: "Print prep", icon: "⬓", sections: ["Build", "Resin"],
    blurb: "Resin supports, print orientation, and the overhang check that runs after every build." },
  { id: "quality", label: "Quality", icon: "◆", sections: ["Quality"],
    blurb: "Facet counts and tessellation. Higher is smoother and slower." },
  { id: "tools", label: "Tests & tools", icon: "⚙", sections: ["Calibration", "Gauge"], custom: "tools",
    blurb: "Calibration sweeps, the shaft gauge, type-test plates, legend sheets and font coverage." },
];
const TOOL_SECTIONS = ["Type test", "Legend", "Legend output"];   // drawn inside the Tools page's own cards
const FONT_KEYS = new Set(["path", "font2_path", "font_path", "label_font_path", "legend_font_path"]);

// ---------------------------------------------------------------- fonts
const faces = reactive({});   // path -> css family name once loaded | "error"
let faceSeq = 0;
function fontFamily(path) {
  if (!path) return null;
  if (!(path in faces)) {
    faces[path] = null;
    const name = `tef${++faceSeq}`;
    new FontFace(name, `url("${engine.fontUrl(path)}")`).load()
      .then((f) => { document.fonts.add(f); faces[path] = name; })
      .catch(() => { faces[path] = "error"; });
  }
  return faces[path];
}
const famStyle = (fam, extra = {}) => (fam && fam !== "error" ? { fontFamily: `${fam}, var(--sans)`, ...extra } : extra);
const baseName = (p) => (p || "").split(/[\\/]/).pop();
const fontLabel = (p) => baseName(p).replace(/\.(ttf|otf|ttc|otc)$/i, "");
const hex = (c) => "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");

// ---------------------------------------------------------------- state
const S = reactive({
  machines: [], machine: localStorage.getItem("te.machine") || null,
  data: null, edits: {}, rows: null, preset: null, group: localStorage.getItem("te.group") || "typeface", search: "",
  glyphs: { status: {}, unused: {} }, sel: null, profiles: [],
  job: { running: false, label: "", progress: 0, state: "", elapsed: 0, log: [], partial: "", issues: [] },
  build: { target: "element", crossSection: false, crossAngle: 0, cutBodies: false, stl: null, last: null },
  coverage: { chars: "", dir: "", deep: false, report: false },
  legendStamp: 0, fonts: null, picker: null, toast: null,
  theme: localStorage.getItem("te.theme") || "auto", view: "settings",
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
const section = (name) => (S.data?.schema || []).find((s) => s.section === name);

const groups = computed(() => {
  if (!S.data) return [];
  const claimed = new Set([...GROUPS.flatMap((g) => g.sections), ...TOOL_SECTIONS]);
  const orphans = S.data.schema.filter((s) => !claimed.has(s.section)).map((s) => s.section);
  return GROUPS.map((g) => {
    const secs = [...g.sections, ...(g.id === "element" ? orphans : [])].filter((n) => section(n));
    const n = secs.reduce((a, s) => a + section(s).fields.length, 0)
      + (g.custom === "tools" ? TOOL_SECTIONS.reduce((a, s) => a + (section(s)?.fields.length || 0), 0) : 0);
    const show = n > 0 || (g.custom === "layout" && layoutRows.value) || g.custom === "tools";
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
  S.data = await engine.config(m);
  S.edits = {}; S.rows = null; S.preset = null; S.sel = null;
  S.job.log = []; S.job.issues = []; S.job.state = ""; S.job.progress = 0;
  S.build.target = S.data.target;
  S.coverage.chars = (layoutRows.value || []).join("");
  if (S.data.migrated?.length) toast(`Added new settings from the master config: ${S.data.migrated.join(", ")}`);
  refreshGlyphs();
  engine.profiles(m).then((p) => (S.profiles = p)).catch(() => (S.profiles = []));
  viewer?.clear();
  try { S.build.stl = await viewer?.load(engine.stlUrl(m)); } catch { S.build.stl = null; }
}

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
  S.data = res; S.edits = {}; S.rows = null; S.preset = null;
  if (res.errors.length) { toast(res.errors.join(" · "), "bad"); refreshGlyphs(); return false; }
  toast(`Saved ${res.changed} change${res.changed === 1 ? "" : "s"}`, "ok");
  engine.profiles(S.machine).then((p) => (S.profiles = p));
  refreshGlyphs();
  return true;
}

function discard() { S.edits = {}; S.rows = null; S.preset = null; refreshGlyphs(); }

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
async function runJob(label, start, after) {
  if (S.job.running) return;
  if (!(await save())) return;
  const j = S.job;
  Object.assign(j, { running: true, label, progress: 0, state: "", log: [], partial: "", issues: [] });
  if (narrow()) S.view = "build";
  const t0 = Date.now();
  const tick = setInterval(() => (j.elapsed = (Date.now() - t0) / 1000), 250);
  let rc = -1;
  try {
    await start((ev) => {
      const text = ev.line ?? ev.partial;
      if (text !== undefined) {
        const m = text.match(/\[(\d+)\/(\d+)\]/);
        if (m) j.progress = 0.95 * (+m[1] / Math.max(+m[2], 1));
      }
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
  j.running = false;
  j.elapsed = (Date.now() - t0) / 1000;
  if (rc === 0) {
    j.progress = 1; j.state = "ok";
    j.log.push({ t: `${label} finished in ${j.elapsed.toFixed(1)}s`, c: "ok" });
    try { await after?.(); } catch (e) { j.log.push({ t: String(e.message || e), c: "e" }); }
  } else {
    j.state = "fail";
    if (rc > 0) j.log.push({ t: `${label} failed (exit ${rc})`, c: "e" });
    if (rc < 0 && j.log.length) j.log.push({ t: `${label} stopped`, c: "c" });
  }
  logScroll();
}

function runBuild(fast) {
  const b = S.build;
  const opts = { fast, target: b.target, cross_section: b.crossSection, cross_section_angle: b.crossAngle, cut_bodies: b.cutBodies };
  return runJob(fast ? "Preview" : "Render", (on) => engine.build(S.machine, opts, on), async () => {
    b.stl = await viewer.load(engine.stlUrl(S.machine));
    b.last = { kind: fast ? "preview" : "render", target: b.target, at: new Date().toISOString() };
  });
}
const runTypeTest = () => runJob("Type test", (on) => engine.tool(S.machine, { tool: "type_test" }, on), async () => {
  S.build.stl = await viewer.load(engine.stlUrl(S.machine), { top: true });
  S.build.last = { kind: "type_test", at: new Date().toISOString() };
});
const runLegend = () => runJob("Legend", (on) => engine.tool(S.machine, { tool: "legend" }, on),
  async () => { S.legendStamp = Date.now(); });
const runCoverage = (current) => runJob(current ? "Font check" : "Font scan", (on) => engine.tool(S.machine, {
  tool: current ? "coverage_current" : "coverage", chars: S.coverage.chars, font_dir: S.coverage.dir, deep: S.coverage.deep,
}, on), async () => { S.coverage.report = true; });

async function saveCopy() {
  try {
    const r = await engine.saveCopy(S.machine, { last_build: S.build.last });
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
    const rowLabel = (i) => ["lowercase", "uppercase", "figures", "math"][i] ? `Row ${i + 1} · ${["lowercase", "uppercase", "figures", "math"][i]}` : `Row ${i + 1}`;
    return { v, changed, setVal, setItem, textFam, famStyle, rowLabel };
  },
  template: `
  <div class="field" :class="{ wide: f.type === 'floatlist' || f.type === 'textblock' }" :id="'f-' + f.key" :title="f.help || ''">
    <template v-if="f.type === 'bool'">
      <label class="switch"><input type="checkbox" :checked="!!v" @change="setVal(f.key, $event.target.checked)">
        <span>{{ f.label }}</span><span v-if="changed" class="changed"></span></label>
    </template>
    <template v-else>
      <label :for="'i-' + f.key">{{ f.label }}<span v-if="changed" class="changed"></span></label>
      <select v-if="f.options.length" class="select" :id="'i-' + f.key" :value="String(v)" @change="setVal(f.key, $event.target.value)">
        <option v-for="o in f.options" :value="o.value">{{ o.label }}</option>
      </select>
      <div v-else-if="f.type === 'floatlist'" class="listrow">
        <div v-for="(x, i) in (v || [])" class="listitem">
          <span class="help">{{ f.key.startsWith('band') ? 'Band ' + (i + 1) : rowLabel(i) }}</span>
          <input class="input" type="number" step="any" :value="x" @input="setItem(i, $event.target.value)">
        </div>
      </div>
      <textarea v-else-if="f.type === 'textblock'" class="input textblock" :id="'i-' + f.key" :value="v ?? ''"
                :style="famStyle(textFam)" @input="setVal(f.key, $event.target.value)"></textarea>
      <input v-else-if="f.type === 'int' || f.type === 'float'" class="input" type="number" :step="f.type === 'int' ? 1 : 'any'"
             :id="'i-' + f.key" :value="v" @input="setVal(f.key, $event.target.value === '' ? '' : Number($event.target.value))">
      <input v-else class="input" :id="'i-' + f.key" :value="v ?? ''" @input="setVal(f.key, $event.target.value)">
    </template>
    <div v-if="f.help && f.help.length < 160" class="help">{{ f.help }}</div>
  </div>`,
};

const FontField = {
  props: ["f", "sample"],
  setup(props) {
    const path = computed(() => val(props.f.key) || "");
    const fam = computed(() => fontFamily(path.value));
    const changed = computed(() => props.f.key in S.edits);
    const pick = () => { S.picker = { key: props.f.key, label: props.f.label, current: path.value, sample: props.sample }; };
    return { path, fam, changed, pick, fontLabel, setVal, famStyle };
  },
  template: `
  <div class="field wide" :id="'f-' + f.key">
    <label>{{ f.label }}<span v-if="changed" class="changed"></span></label>
    <div class="font-field">
      <div v-if="!path" class="font-missing" style="color:var(--text-3)">No font set{{ f.key === 'font2_path' ? ' - these characters use the main font.' : '.' }}</div>
      <div v-else-if="fam === 'error'" class="font-missing">This font file isn't on this computer: {{ path }}</div>
      <div v-else class="spec" :style="fam ? famStyle(fam) : { opacity: .35 }">
        <div class="name">{{ fontLabel(path) }}</div>
        <div class="sample">{{ sample || 'AaBbCc 0123456789 &?!' }}</div>
      </div>
      <div class="meta">
        <span class="path" :title="path">{{ path || '—' }}</span>
        <button class="btn small" @click="pick">Choose…</button>
        <button v-if="path && f.key !== 'path'" class="btn small ghost" @click="setVal(f.key, '')">Clear</button>
      </div>
    </div>
    <div v-if="f.help" class="help">{{ f.help }}</div>
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
      if (key === "path") return (layoutRows.value || []).join("").replace(/\s/g, "").slice(0, 64) || null;
      if (key === "font2_path") return font2Chars.value || null;
      if (key === "font_path") return c.logo?.text || [c.label?.label1, c.label?.label2].filter(Boolean).join("  ") || null;
      if (key === "label_font_path") return [c.label?.label1, c.label?.label2, c.label?.text].filter(Boolean).join("  ") || null;
      return null;
    };
    return { fonts, plain, lists, sampleFor };
  },
  template: `
  <section class="card">
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

const ProfilesCard = {
  setup() {
    const name = ref("");
    const active = computed(() => S.profiles.find((p) => p.active));
    const apply = (p) => {
      const byPath = Object.fromEntries(Object.values(fieldsByKey.value).map((f) => [f.path.join("."), f.key]));
      let n = 0;
      for (const [path, v] of Object.entries(p.values)) if (byPath[path]) { setVal(byPath[path], v); n++; }
      toast(`Applied "${p.name}" (${n} settings)${p.unset.length ? ` - ${p.unset.length} left as they were` : ""}. Save to keep.`);
    };
    const saveAs = async () => {
      if (!name.value.trim()) return;
      if (!(await save())) return;
      S.profiles = await engine.saveProfile(S.machine, name.value.trim());
      toast(`Saved profile "${name.value.trim()}"`, "ok"); name.value = "";
    };
    const rename = async (p) => {
      const n = prompt("Rename profile", p.name);
      if (n && n !== p.name) S.profiles = await engine.renameProfile(S.machine, p.name, n).catch((e) => (toast(e.message, "bad"), S.profiles));
    };
    const del = async (p) => { if (confirm(`Delete profile "${p.name}"?`)) S.profiles = await engine.deleteProfile(S.machine, p.name); };
    return { S, name, active, apply, saveAs, rename, del };
  },
  template: `
  <section class="card">
    <div class="card-head"><h2>Font profiles</h2><span class="sub">{{ active ? 'Active: ' + active.name : 'No profile matches the current settings' }}</span></div>
    <div class="card-body">
      <div v-if="S.profiles.length" class="profile-list">
        <div v-for="p in S.profiles" class="profile" :class="{ on: p.active }">
          <span class="pname">{{ p.name }}</span>
          <span v-if="p.active" class="chip ok">active</span>
          <span class="spacer"></span>
          <button class="btn small" :disabled="p.active" @click="apply(p)">Apply</button>
          <button class="btn small ghost" @click="rename(p)">Rename</button>
          <button class="btn small ghost danger" @click="del(p)">Delete</button>
        </div>
      </div>
      <p v-else class="help" style="margin-top:0">No saved profiles yet.</p>
      <div style="display:flex;gap:8px;margin-top:10px">
        <input class="input" style="flex:1" v-model="name" placeholder="Save current font settings as…" @keyup.enter="saveAs">
        <button class="btn" :disabled="!name.trim()" @click="saveAs">Save profile</button>
      </div>
    </div>
  </section>`,
};

const LayoutPage = {
  setup() {
    const fam = computed(() => fontFamily(val("path")));
    const fam2 = computed(() => fontFamily(val("font2_path") || val("path")));
    const sel = computed(() => S.sel);
    const selChar = computed(() => (sel.value ? [...layoutRows.value[sel.value.r]][sel.value.i] : null));
    const famFor = (c) => (font2Chars.value.includes(c) ? fam2.value : fam.value);
    const pick = (r, i) => { S.sel = S.sel && S.sel.r === r && S.sel.i === i ? null : { r, i }; };
    const presetNames = computed(() => Object.keys(S.data.presets || {}));
    const activePreset = computed(() => S.preset ?? (S.rows === null ? S.data.current_preset : null));
    const typed = ref("");
    watch(selChar, (c) => (typed.value = c ?? ""));
    const applyTyped = () => { if (sel.value && typed.value) setChar(sel.value.r, sel.value.i, [...typed.value][0]); };
    const showText = ref(false);
    const origLen = (r) => [...(S.data.cfg.layout.rows[r] || "")].length;
    const lenBad = (r, row) => S.data.fixed_row_lengths && !S.preset && [...row].length !== origLen(r);
    return { S, fam, famFor, pick, sel, selChar, presetNames, activePreset, applyPreset, setChar, setRowText,
             typed, applyTyped, showText, badGlyphs, layoutRows, font2Chars, famStyle, hex, lenBad, origLen };
  },
  template: `
  <section class="card">
    <div class="card-head">
      <h2>Keyboard layout</h2><span class="sub">{{ activePreset ? activePreset : 'Custom' }} · {{ layoutRows.length }} rows</span>
      <span class="spacer"></span>
      <button class="btn small" @click="showText = !showText">{{ showText ? 'Show grid' : 'Edit as text' }}</button>
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
      <div v-if="!showText" class="kb">
        <div v-for="(row, r) in layoutRows" class="kb-row" :style="{ '--n': [...row].length }">
          <span class="rn">{{ r + 1 }}</span>
          <div class="kb-keys">
            <div v-for="(c, i) in [...row]" class="key"
                 :title="hex(c) + (S.glyphs.status[c] && S.glyphs.status[c] !== 'ok' ? ' - ' + S.glyphs.status[c] + ' in font' : '')"
                 :class="[S.glyphs.status[c] && S.glyphs.status[c] !== 'ok' ? S.glyphs.status[c] : '', sel && sel.r === r && sel.i === i ? 'sel' : '', c.trim() ? '' : 'space', font2Chars.includes(c) ? 'f2' : '']"
                 :style="famStyle(famFor(c))" @click="pick(r, i)">{{ c.trim() ? c : '␣' }}</div>
          </div>
        </div>
      </div>
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
        <div class="key big" :class="S.glyphs.status[selChar] && S.glyphs.status[selChar] !== 'ok' ? S.glyphs.status[selChar] : ''" :style="famStyle(famFor(selChar))">{{ selChar }}</div>
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
          <button v-for="c in chars.slice(0, 500)" :style="famStyle(fam)" :title="hex(c)" @click="setChar(sel.r, sel.i, c)">{{ c }}</button>
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
    return { S, setVal, tt, legend, legendOut, legendUrl, runTypeTest, runLegend, runCoverage, presetNames, seedCoverage,
             calib, gauge, buildAs, engine, layoutRows };
  },
  template: `
  <SectionCard v-if="calib" :s="calib">
    <template #actions><button class="btn small" :disabled="S.job.running" @click="buildAs('calibration')">Build calibration element</button></template>
  </SectionCard>
  <SectionCard v-if="gauge" :s="gauge" title="Shaft gauge">
    <template #actions><button class="btn small" :disabled="S.job.running" @click="buildAs('gauge')">Build shaft gauge</button></template>
  </SectionCard>
  <SectionCard v-if="tt" :s="tt" title="Type test plate">
    <template #top><p class="help" style="margin-top:0">A flat plate of text in the current font and alignment - print it to check spacing before cutting a whole element.</p></template>
    <template #actions><button class="btn small primary" :disabled="S.job.running" @click="runTypeTest">Render type test</button></template>
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
      <a class="btn small" :href="legendUrl" download>Download SVG</a>
    </div>
  </SectionCard>
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

const FontPicker = {
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
    const sample = S.picker.sample || "AaBbCc 0123 &?!";
    const choose = (p) => { setVal(S.picker.key, p); S.picker = null; };
    const close = () => (S.picker = null);
    return { S, q, manual, shown, list, listEl, famOf, sample, choose, close, famStyle };
  },
  template: `
  <div class="modal-bg" @click.self="close" @keydown.esc="close">
    <div class="modal" role="dialog" aria-modal="true">
      <div class="head"><h2>{{ S.picker.label }}</h2><span class="spacer"></span><button class="btn small ghost" @click="close" aria-label="Close">✕</button></div>
      <div class="tools">
        <div class="search" style="flex:1"><input id="font-q" class="input" style="width:100%" v-model="q" placeholder="Search installed fonts…" @keydown.esc="close"></div>
        <span class="chip" v-if="list">{{ shown.length }}{{ shown.length === 800 ? '+' : '' }} / {{ list.length }}</span>
      </div>
      <div class="list" ref="listEl">
        <div v-if="!list" style="padding:20px;color:var(--text-3)">Loading installed fonts…</div>
        <div v-for="f in shown" :key="f.path" class="font-row" :data-path="f.path" :class="{ sel: f.path === S.picker.current }" @click="choose(f.path)">
          <div class="preview" :style="famOf(f.path) ? famStyle(famOf(f.path)) : { color: 'var(--text-3)' }">{{ sample }}</div>
          <div class="fam" :title="f.path">{{ f.family }} <span style="color:var(--text-3)">{{ f.style }}</span></div>
        </div>
      </div>
      <div class="foot">
        <input class="input" style="flex:1;font-family:var(--mono);font-size:12px;min-width:0" v-model="manual" placeholder="…or paste a font file path">
        <button class="btn primary" :disabled="!manual" @click="choose(manual)">Use this file</button>
      </div>
    </div>
  </div>`,
};

const App = {
  components: { SectionCard, LayoutPage, ToolsPage, ProfilesCard, FontPicker },
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
    onMounted(async () => {
      viewer = new Viewer(viewerEl.value);
      logEl = logRef.value;
      applyTheme();
      matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme);
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
    });
    return { S, groups, currentGroup, section, dirty, save, discard, resetToMaster, loadMachine, runBuild, saveCopy,
             viewerEl, logRef, searchHits, jumpTo, groupOf, engine, applyTheme, badGlyphs, openGroup,
             cancel: () => engine.cancel(), baseName };
  },
  template: `
  <div class="shell">
    <header class="topbar">
      <div class="brand"><span class="dot">T</span><span class="label">Type Elements</span></div>
      <select class="select" :value="S.machine" @change="loadMachine($event.target.value)" style="width:190px;flex-shrink:1;min-width:120px" aria-label="Machine">
        <optgroup v-for="g in S.machines" :label="g.group">
          <option v-for="m in g.machines" :value="m.key" :disabled="!m.available">{{ m.label }}</option>
        </optgroup>
      </select>
      <span v-if="S.data" class="chip hide-md" :title="S.data.running_path">{{ baseName(S.data.running_path) }}</span>
      <span v-if="dirty" class="chip dirty">● Unsaved</span>
      <span v-else-if="S.data" class="chip ok hide-sm">Saved</span>
      <div class="seg" role="tablist">
        <button :class="{ on: S.view === 'settings' }" @click="S.view = 'settings'">Settings</button>
        <button :class="{ on: S.view === 'build' }" @click="S.view = 'build'">Preview{{ S.job.running ? ' ⟳' : '' }}</button>
      </div>
      <span class="spacer"></span>
      <div class="search"><input id="search" class="input" v-model="S.search" placeholder="Search settings   /" @focus="S.view = 'settings'"></div>
      <button class="btn hide-sm" :disabled="!dirty" @click="discard">Discard</button>
      <button class="btn primary" :disabled="!dirty" @click="save" title="Ctrl+S">Save</button>
      <select class="select hide-md" v-model="S.theme" @change="applyTheme" style="width:88px" aria-label="Theme" title="Theme">
        <option value="auto">Auto</option><option value="light">Light</option><option value="dark">Dark</option>
      </select>
    </header>

    <div class="body" :class="'view-' + S.view">
      <div class="pills" v-if="S.view === 'settings'">
        <button v-for="g in groups" :class="{ on: currentGroup && g.id === currentGroup.id && !S.search }" @click="openGroup(g.id)">{{ g.label }}{{ g.id === 'layout' && badGlyphs.length ? ' ●' : '' }}</button>
      </div>
      <nav class="nav">
        <div class="nav-label">{{ S.data ? S.data.label : '' }}</div>
        <button v-for="g in groups" class="nav-item" :class="{ active: currentGroup && g.id === currentGroup.id && !S.search }" @click="openGroup(g.id)">
          <span class="ico">{{ g.icon }}</span>{{ g.label }}
          <span v-if="g.id === 'layout' && badGlyphs.length" class="flag" title="Characters missing from the font"></span>
          <span v-else-if="g.count" class="count">{{ g.count }}</span>
        </button>
        <div class="nav-label">Machine</div>
        <button class="nav-item" @click="resetToMaster"><span class="ico">↺</span>Reset to defaults</button>
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
          <div v-if="S.data.warning && ['element', 'print'].includes(currentGroup.id)" class="note warn" :title="S.data.warning.long">{{ S.data.warning.short }}</div>
          <LayoutPage v-if="currentGroup.custom === 'layout' && S.data.cfg.layout && S.data.cfg.layout.rows" />
          <template v-for="name in (currentGroup.custom === 'tools' ? [] : currentGroup.sections)" :key="name">
            <SectionCard :s="section(name)" />
            <ProfilesCard v-if="name === 'Font & Alignment'" />
          </template>
          <ToolsPage v-if="currentGroup.custom === 'tools'" />
        </template>
      </main>
      <main class="main" v-else><p style="color:var(--text-3)">Loading…</p></main>

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
            <select class="select" v-model="S.build.target" style="flex:1;min-width:140px" aria-label="Build target" v-if="S.data">
              <option v-for="t in S.data.targets" :value="t.value">{{ t.label }}</option>
            </select>
            <button class="btn" :disabled="S.job.running" @click="runBuild(true)" title="Quick, no draft angle (Ctrl+Enter)">Preview</button>
            <button class="btn primary" :disabled="S.job.running" @click="runBuild(false)" title="Full quality with draft (Ctrl+Shift+Enter)">Render</button>
            <button v-if="S.job.running" class="btn danger" @click="cancel">Stop</button>
          </div>
          <div class="row">
            <div class="progress" :class="S.job.state"><div :style="{ width: (S.job.progress * 100) + '%' }"></div></div>
            <span class="chip" style="min-width:64px;justify-content:center">{{ S.job.running ? S.job.label + ' ' : '' }}{{ S.job.elapsed ? S.job.elapsed.toFixed(0) + 's' : '—' }}</span>
          </div>
          <div class="row" v-if="S.build.stl && !S.job.running">
            <a class="btn small" :href="engine.stlUrl(S.machine)" download>Download STL</a>
            <button class="btn small" @click="saveCopy" title="Timestamped copy + config sidecar in output/saved">Save a copy</button>
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
    <div v-if="S.toast" class="toast note" :class="S.toast.kind === 'bad' ? 'bad' : S.toast.kind === 'ok' ? 'ok' : 'info'">{{ S.toast.msg }}</div>
  </div>`,
};

createApp(App).mount("#app");
