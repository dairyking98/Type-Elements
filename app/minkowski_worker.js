// One Minkowski worker for the in-browser engine's pool: its own manifold
// WASM instance. Takes a glyph and a draft cone as raw float32 vertex /
// uint32 triangle buffers, returns the sum the same way (all transferred,
// not copied). See engine_worker.js.
import Module from "https://cdn.jsdelivr.net/npm/manifold-3d@3.5.4/manifold.js";

const ready = Module().then((wasm) => { wasm.setup(); return wasm; });

self.onmessage = async ({ data: { i, gv, gf, cv, cf } }) => {
  const { Manifold, Mesh } = await ready;
  const mk = (v, f) => new Manifold(new Mesh({ numProp: 3, vertProperties: new Float32Array(v), triVerts: new Uint32Array(f) }));
  const a = mk(gv, gf), b = mk(cv, cf);
  const r = a.minkowskiSum(b);
  const m = r.getMesh();
  const n = m.numProp;
  const v = new Float32Array((m.vertProperties.length / n) * 3);
  for (let s = 0, d = 0; s < m.vertProperties.length; s += n, d += 3) {
    v[d] = m.vertProperties[s]; v[d + 1] = m.vertProperties[s + 1]; v[d + 2] = m.vertProperties[s + 2];
  }
  const f = new Uint32Array(m.triVerts);
  a.delete(); b.delete(); r.delete();
  self.postMessage({ i, v: v.buffer, f: f.buffer }, [v.buffer, f.buffer]);
};
