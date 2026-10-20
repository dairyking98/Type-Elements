// Minkowski worker that returns the RESULT mesh (the benchmark worker only
// returned timings). One manifold WASM instance per worker.
import Module from "https://cdn.jsdelivr.net/npm/manifold-3d@3.5.4/manifold.js";

const ready = Module().then((wasm) => { wasm.setup(); return wasm; });

self.onmessage = async ({ data: { id, glyph, cone } }) => {
  const { Manifold, Mesh } = await ready;
  const mk = (o) => new Manifold(new Mesh({ numProp: 3, vertProperties: new Float32Array(o.v), triVerts: new Uint32Array(o.f) }));
  const a = mk(glyph), b = mk(cone);
  const r = a.minkowskiSum(b);
  const m = r.getMesh();
  const n = m.numProp;
  const v = new Float32Array((m.vertProperties.length / n) * 3);
  for (let i = 0, j = 0; i < m.vertProperties.length; i += n, j += 3) { v[j] = m.vertProperties[i]; v[j + 1] = m.vertProperties[i + 1]; v[j + 2] = m.vertProperties[i + 2]; }
  const f = new Uint32Array(m.triVerts);
  a.delete(); b.delete(); r.delete();
  self.postMessage({ id, v: Array.from(v), f: Array.from(f) });
};
