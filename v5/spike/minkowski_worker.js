// One Minkowski worker: its own manifold WASM instance, sums the pairs it is
// sent and reports time, triangle count and volume for each. Many of these
// run side by side - a character's sum doesn't depend on any other's, and
// separate workers need no cross-origin isolation (nothing shared).
import Module from "https://cdn.jsdelivr.net/npm/manifold-3d@3.5.4/manifold.js";

const ready = Module().then((wasm) => { wasm.setup(); return wasm; });

self.onmessage = async ({ data: { id, glyph, cone } }) => {
  const { Manifold, Mesh } = await ready;
  const mk = (o) => new Manifold(new Mesh({ numProp: 3, vertProperties: new Float32Array(o.v), triVerts: new Uint32Array(o.f) }));
  const a = mk(glyph), b = mk(cone);
  const t = performance.now();
  const r = a.minkowskiSum(b);
  const tris = r.numTri(), vol = r.volume();
  const dt = (performance.now() - t) / 1000;
  a.delete(); b.delete(); r.delete();
  self.postMessage({ id, dt, tris, vol });
};
