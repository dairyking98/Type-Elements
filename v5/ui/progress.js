// Job progress that is smooth and roughly honest about time.
//
// The engine's log only counts inside loops ("[12/88]"), so a bar driven by
// counters alone races through the characters, then sits still through the
// body, supports and export. Instead, every finished job leaves a timeline:
// the fraction of its run at which each kind of log line first appeared
// (keyed by the line's leading words, e.g. "TextRing", "ResinPrint"). The
// next run of the same job (machine + job + target + engine) uses it:
//   * reaching a known line jumps to its fraction;
//   * between lines, elapsed time fills in, at the pace this run is going
//     (a run half as fast as last time moves half as fast), easing off near
//     the next line rather than passing it;
//   * a loop counter in the current stretch can push it further.
// A job can take differently shaped routes (a browser Render that finds all
// its draft angles cached skips two stages), so up to 3 timelines are kept
// per job and the one matching the lines seen so far is used.
// With no history yet it falls back to stage slices + counters.
//
//   const p = progressTracker(key);   p.event(ev) for each job event;
//   p.value() -> 0..1 (never goes back);  p.remaining() -> seconds | null;
//   p.finish(ok) saves the timeline when the job succeeded.

const STORE = "te.progress.v1";
const MAX_JOBS = 80, MAX_SHAPES = 3;

function loadAll() { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch { return {}; } }
function saveAll(all) { try { localStorage.setItem(STORE, JSON.stringify(all)); } catch {} }

// "TextRing: [12/88] 'r'" -> "TextRing";  "--- pass 2: building" -> "--- pass"
export function signature(text) {
  const m = String(text).trim().match(/^[^\d[(:'"=,]{3,48}/);
  return m ? m[0].trim() : null;
}

// slope-1 ramp that eases into 1 instead of reaching it
const ease = (x) => (x <= 0.8 ? Math.max(0, x) : 0.8 + 0.2 * (1 - Math.exp(-(x - 0.8) / 0.2)));
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

export function progressTracker(key) {
  const shapes = loadAll()[key]?.shapes || [];
  const t0 = performance.now();
  const now = () => (performance.now() - t0) / 1000;
  const seen = new Map();            // signature -> seconds into this run
  let hist = shapes[0] || null;      // {total, marks: {sig: fraction}}
  let anchorF = 0, anchorT = 0;      // last known line reached: fraction, time
  let counter = null;                // latest [n/total] since the anchor
  let phase = [0, 1];
  let best = 0;

  function reanchor() {
    anchorF = 0; anchorT = 0;
    for (const [s, t] of seen) { const f = hist.marks[s]; if (f !== undefined && f >= anchorF) { anchorF = f; anchorT = t; } }
  }
  function pace() { return anchorF > 0.05 && anchorT > 0 ? clamp(anchorT / (anchorF * hist.total), 0.3, 3) : 1; }
  function nextMark() {
    let fb = 1;
    for (const f of Object.values(hist.marks)) if (f > anchorF + 1e-6 && f < fb) fb = f;
    return fb;
  }

  return {
    event(ev) {
      const text = ev.phase ? `phase ${ev.phase[2]}` : ev.line ?? ev.partial;
      if (ev.phase) phase = ev.phase;
      if (text === undefined) return;
      const m = !ev.phase && String(text).match(/\[(\d+)\/(\d+)\]/);
      const s = signature(text);
      if (s && !seen.has(s)) {
        seen.set(s, now());
        if (hist && hist.marks[s] === undefined) {          // off this timeline: is there one that has it?
          const other = shapes.find((h) => h.marks[s] !== undefined);
          if (other) { hist = other; reanchor(); counter = null; }
        } else if (hist && hist.marks[s] >= anchorF) { anchorF = hist.marks[s]; anchorT = now(); counter = null; }
      }
      if (m) counter = +m[1] / Math.max(+m[2], 1);
    },
    value() {
      let est;
      if (hist) {
        const fb = nextMark();
        const span = pace() * (fb - anchorF) * hist.total;
        const x = Math.max(span > 0 ? (now() - anchorT) / span : 0, counter !== null ? counter * 0.98 : 0);
        est = anchorF + (fb - anchorF) * ease(x);
      } else {
        est = phase[0] + (phase[1] - phase[0]) * 0.95 * (counter ?? 0);
      }
      best = Math.max(best, Math.min(est, 0.995));
      return best;
    },
    remaining() {
      if (!hist) return null;
      return Math.max(0, (1 - best) * pace() * hist.total);
    },
    finish(ok) {
      const total = now();
      if (!ok || total < 0.5) return;
      const marks = {};
      for (const [s, t] of seen) marks[s] = +(t / total).toFixed(4);
      const shape = Object.keys(marks).sort().join("\n");
      const all = loadAll();
      const prev = (all[key]?.shapes || []).filter((h) => Object.keys(h.marks).sort().join("\n") !== shape);
      delete all[key];                                      // re-insert: newest last, oldest dropped first
      all[key] = { shapes: [{ total, marks }, ...prev].slice(0, MAX_SHAPES) };
      const keys = Object.keys(all);
      for (const k of keys.slice(0, Math.max(0, keys.length - MAX_JOBS))) delete all[k];
      saveAll(all);
    },
  };
}
