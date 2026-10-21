// Job progress in steps, driven only by what the job reports - no clock,
// no history, no estimates: the same on a fast or a slow computer.
//
// A job may split itself into stage slices (engine_worker.js phase events:
// [start, end, label, share]). Within a slice its [n/N] loop (the engine's
// per-character log lines) fills `share` of it, one increment per item,
// and each new kind of log line after the loop takes a quarter of what is
// left of the slice. With no stages the whole bar is one slice.
//
//   const p = progressTracker();   p.event(ev) for each job event;
//   p.value() -> 0..1 (never goes back).

// "TextRing: [12/88] 'r'" -> "TextRing";  "--- pass 2: building" -> "--- pass"
export function signature(text) {
  const m = String(text).trim().match(/^[^\d[(:'"=,]{3,48}/);
  return m ? m[0].trim() : null;
}

export function progressTracker() {
  const seen = new Set();
  const st = { lo: 0, hi: 1, share: 0.65, n: null, loopDone: false, steps: 0 };
  let best = 0;
  function stage(p) { Object.assign(st, { lo: p[0], hi: p[1], share: p[3] ?? 0.65, n: null, loopDone: false, steps: 0 }); }
  function value() {
    const span = st.hi - st.lo, share = Math.max(0, st.share);
    const tail = (base, k) => base + (st.lo + span - base) * (1 - Math.pow(0.75, k));
    if (share <= 0) return tail(st.lo, st.steps);                                    // no loop: every new line is a step
    if (st.n === null) return st.lo + span * 0.04 * (1 - Math.pow(0.5, st.steps));    // before the loop
    if (!st.loopDone) return st.lo + span * (0.04 + (share - 0.04) * st.n);           // in the loop: per item
    return share >= 1 ? st.hi : tail(st.lo + span * share, st.steps);                // after it
  }
  return {
    event(ev) {
      if (ev.phase) { stage(ev.phase); return; }
      const text = ev.line ?? ev.partial;
      if (text === undefined) return;
      const m = String(text).match(/\[(\d+)\/(\d+)\]/);
      if (m) {
        const n = +m[1] / Math.max(+m[2], 1);
        if (st.n !== null && n < st.n - 0.5) { st.lo = value(); st.n = null; st.loopDone = false; st.steps = 0; }   // a second loop
        st.n = n;
        if (n >= 1 && !st.loopDone) { st.loopDone = true; st.steps = 0; }
        else if (n < 1) st.loopDone = false;
        return;
      }
      const s = signature(text);
      if (st.n !== null && !st.loopDone && ev.line !== undefined) { st.loopDone = true; st.steps = 0; }   // a plain line ends the loop
      if (s && !seen.has(s)) { seen.add(s); st.steps++; }
    },
    value() { best = Math.max(best, Math.min(value(), 0.995)); return best; },
    finish() {},
  };
}
