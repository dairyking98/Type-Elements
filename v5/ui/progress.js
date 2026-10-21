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
// With no history yet (or when a run leaves every saved route - a stage the
// timeline never had), it falls back to a model: within each stage slice the
// [n/N] loop fills `share` of it (0.65 unless the stage says), then the rest
// fills over a time guessed from how long the loop took, easing so that a
// longer tail keeps creeping instead of parking at 95%. The tail itself is
// learned across routes: lines after the characters (Additive, ResinSupport,
// ResinPrint...) are the same whichever route a render took, so each job
// also keeps how many seconds were left when each line appeared, and a run
// on a route with no timeline yet times its tail from those.
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
// the same, easing off more slowly: for a guessed duration, which may well
// run long - it keeps visibly moving (87% at 1x, 95% at 1.5x, 98% at 2x)
const creep = (x) => (x <= 0.8 ? Math.max(0, x) : 0.8 + 0.2 * (1 - Math.exp(-(x - 0.8) / 0.5)));
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

export function progressTracker(key) {
  const saved = loadAll()[key] || {};
  const shapes = saved.shapes || [];
  const tails = saved.tails || {};   // signature -> seconds left when it appeared (any route)
  const t0 = performance.now();
  const now = () => (performance.now() - t0) / 1000;
  const seen = new Map();            // signature -> seconds into this run
  let hist = shapes[0] || null;      // {total, marks: {sig: fraction}}
  let anchorF = 0, anchorT = 0;      // last known line reached: fraction, time
  let counter = null;                // latest [n/total] since the anchor
  let best = 0;
  // fallback model, kept up to date even while a timeline is in use
  const fb = { lo: 0, hi: 1, share: 0.65, t0: 0, n: null, loopT0: null, loopEnd: null, known: null };
  function stage(p) { Object.assign(fb, { lo: p[0], hi: p[1], share: p[3] ?? 0.65, t0: now(), n: null, loopT0: null, loopEnd: null, known: null }); }
  // -> [fraction, seconds left | null]
  function fallback() {
    const t = now(), span = fb.hi - fb.lo, last = fb.hi >= 1;
    const tailFrom = (start, tail) => {
      const v = fb.lo + span * (fb.share + (1 - fb.share) * creep((t - start) / tail));
      return [v, last && start + tail > t ? start + tail - t : null];
    };
    if (fb.known) {                                        // a line whose time-to-finish we've measured before
      const k = fb.known, left = k.rem - (t - k.t);
      return [k.v0 + (1 - k.v0) * creep((t - k.t) / k.rem), left > 0 ? left : null];
    }
    if (fb.share <= 0) {                                   // no loop: the rest at the pace the bar has gone so far
      const tail = Math.max(2, (fb.t0 * span) / Math.max(fb.lo, 0.05));
      return tailFrom(fb.t0, tail);
    }
    if (fb.n === null) return [fb.lo + span * 0.04 * (1 - Math.exp(-(t - fb.t0) / 4)), null];   // before any counter
    const loopDur = fb.loopEnd === null ? (t - fb.loopT0) / Math.max(fb.n, 0.02) : fb.loopEnd - fb.loopT0;
    const tail = Math.max(2, (loopDur * (1 - fb.share)) / fb.share);
    if (fb.loopEnd === null) {
      const v = fb.lo + span * (0.04 + (fb.share - 0.04) * fb.n);
      return [v, last && fb.n > 0.05 ? loopDur * (1 - fb.n) + (fb.share < 1 ? tail : 0) : null];
    }
    if (fb.share >= 1) return [fb.hi, null];
    return tailFrom(fb.loopEnd, tail);
  }

  function reanchor() {
    anchorF = 0; anchorT = 0;
    for (const [s, t] of seen) { const f = hist.marks[s]; if (f !== undefined && f >= anchorF) { anchorF = f; anchorT = t; } }
  }
  function pace() { return anchorF > 0.05 && anchorT > 0 ? clamp(anchorT / (anchorF * hist.total), 0.3, 3) : 1; }
  function nextMark() {
    let next = 1;
    for (const f of Object.values(hist.marks)) if (f > anchorF + 1e-6 && f < next) next = f;
    return next;
  }

  return {
    event(ev) {
      const text = ev.phase ? `phase ${ev.phase[2]}` : ev.line ?? ev.partial;
      if (ev.phase) stage(ev.phase);
      if (text === undefined) return;
      const m = !ev.phase && String(text).match(/\[(\d+)\/(\d+)\]/);
      const s = signature(text);
      if (s && !seen.has(s)) {
        seen.set(s, now());
        if (hist && hist.marks[s] === undefined) {          // off this timeline: is there one that has it?
          const other = shapes.find((h) => h.marks[s] !== undefined);
          if (other) { hist = other; reanchor(); counter = null; }
          else if (ev.phase) hist = null;                   // a stage no saved route has: this run's shape is new
        } else if (hist && hist.marks[s] >= anchorF) { anchorF = hist.marks[s]; anchorT = now(); counter = null; }
      }
      // past this stage's loop, a line with a measured time-to-finish times the rest
      if (s && !m && !ev.phase && fb.hi >= 1 && (fb.loopEnd !== null || fb.share <= 0) && tails[s] > 0
          && !(fb.known && fb.known.sig === s)) {
        fb.known = { sig: s, t: now(), rem: tails[s], v0: best };
      }
      if (m) {
        counter = +m[1] / Math.max(+m[2], 1);
        if (fb.n !== null && counter < fb.n - 0.5) {        // a second loop in this stage (Hammond split: one per half)
          fb.lo = fallback()[0]; fb.n = null; fb.loopT0 = null; fb.loopEnd = null;
        }
        if (fb.loopT0 === null) fb.loopT0 = now();
        fb.n = counter;
        if (counter < 1) fb.loopEnd = null;                 // still looping (a stray line in between isn't the end)
        else if (fb.loopEnd === null) fb.loopEnd = now();
      } else if (fb.n !== null && fb.loopEnd === null && ev.line !== undefined) {
        fb.loopEnd = now();                                 // a plain line after the loop: it's over
      }
    },
    value() {
      let est;
      if (hist) {
        const next = nextMark();
        const span = pace() * (next - anchorF) * hist.total;
        const x = Math.max(span > 0 ? (now() - anchorT) / span : 0, counter !== null ? counter * 0.98 : 0);
        est = anchorF + (next - anchorF) * ease(x);
      } else {
        est = fallback()[0];
      }
      best = Math.max(best, Math.min(est, 0.995));
      return best;
    },
    remaining() {
      if (hist) return Math.max(0, (1 - best) * pace() * hist.total);
      const left = fallback()[1];
      if (left !== null) return left;
      return fb.hi < 1 && best > 0.1 ? (now() * (1 - best)) / best : null;   // an earlier stage: this run's pace so far
    },
    finish(ok) {
      const total = now();
      if (!ok || total < 0.5) return;
      const marks = {}, left = {};
      for (const [s, t] of seen) { marks[s] = +(t / total).toFixed(4); left[s] = +(total - t).toFixed(2); }
      const shape = Object.keys(marks).sort().join("\n");
      const all = loadAll();
      const prev = (all[key]?.shapes || []).filter((h) => Object.keys(h.marks).sort().join("\n") !== shape);
      const oldTails = all[key]?.tails || {};
      delete all[key];                                      // re-insert: newest last, oldest dropped first
      all[key] = { shapes: [{ total, marks }, ...prev].slice(0, MAX_SHAPES), tails: { ...oldTails, ...left } };
      const keys = Object.keys(all);
      for (const k of keys.slice(0, Math.max(0, keys.length - MAX_JOBS))) delete all[k];
      saveAll(all);
    },
  };
}
