// Which characters a font has, read straight from its cmap table in the page
// - quick enough to sweep a whole font library (the browser's fonts, the
// synced folder) without copying anything into the engine. "Has" means the
// font maps the character; it can't tell a mapped-but-empty glyph (the
// engine's own build still warns about those).

function tableDir(dv, off) {
  const n = dv.getUint16(off + 4);
  const t = {};
  for (let i = 0; i < n; i++) {
    const r = off + 12 + i * 16;
    const tag = String.fromCharCode(dv.getUint8(r), dv.getUint8(r + 1), dv.getUint8(r + 2), dv.getUint8(r + 3));
    t[tag] = dv.getUint32(r + 8);
  }
  return t;
}

// -> (codepoint) => boolean, or null for a file that isn't a readable font
export function cmapOf(buf) {
  try {
    const dv = new DataView(buf);
    let off = 0;
    if (dv.getUint32(0) === 0x74746366) off = dv.getUint32(12);          // 'ttcf': the collection's first font
    const cmap = tableDir(dv, off).cmap;
    if (cmap === undefined) return null;
    const n = dv.getUint16(cmap + 2);
    let best = null, rank = -1;
    for (let i = 0; i < n; i++) {
      const r = cmap + 4 + i * 8;
      const plat = dv.getUint16(r), enc = dv.getUint16(r + 2), sub = cmap + dv.getUint32(r + 4);
      const fmt = dv.getUint16(sub);
      const score = fmt === 12 && (plat === 3 && enc === 10 || plat === 0) ? 3
        : fmt === 4 && (plat === 3 && enc === 1 || plat === 0) ? 2 : fmt === 4 ? 1 : -1;
      if (score > rank) { rank = score; best = sub; }
    }
    if (best === null || rank < 0) return null;
    if (dv.getUint16(best) === 12) {
      const groups = dv.getUint32(best + 12);
      const g = [];
      for (let i = 0; i < groups; i++) { const r = best + 16 + i * 12; g.push([dv.getUint32(r), dv.getUint32(r + 4), dv.getUint32(r + 8)]); }
      return (cp) => g.some(([a, b, s]) => cp >= a && cp <= b && s + (cp - a) !== 0);
    }
    const segX2 = dv.getUint16(best + 6), seg = segX2 / 2;
    const ends = best + 14, starts = ends + segX2 + 2, deltas = starts + segX2, ranges = deltas + segX2;
    return (cp) => {
      if (cp > 0xffff) return false;
      for (let i = 0; i < seg; i++) {
        const end = dv.getUint16(ends + i * 2);
        if (cp > end) continue;
        const start = dv.getUint16(starts + i * 2);
        if (cp < start) return false;
        const delta = dv.getInt16(deltas + i * 2), ro = dv.getUint16(ranges + i * 2);
        if (ro === 0) return ((cp + delta) & 0xffff) !== 0;
        const gi = dv.getUint16(ranges + i * 2 + ro + (cp - start) * 2);
        return gi !== 0 && ((gi + delta) & 0xffff) !== 0;
      }
      return false;
    };
  } catch { return null; }
}

// characters of `chars` (whitespace ignored) the font lacks; null = unreadable
export function missingIn(buf, chars) {
  const has = cmapOf(buf);
  if (!has) return null;
  return [...new Set([...chars].filter((c) => !/\s/.test(c)))].filter((c) => !has(c.codePointAt(0)));
}
