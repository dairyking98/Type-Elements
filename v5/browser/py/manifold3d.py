"""
In-browser stand-in for the manifold3d Python wheel, delegating to manifold's
official WebAssembly build (the npm package manifold-3d, loaded by the page and
handed to Python as js.globalThis.__manifold). It covers the surface v4 and
trimesh's manifold boolean engine use, so neither changes:

    Mesh(vert_properties=, tri_verts=) / .vert_properties / .tri_verts
    Manifold(mesh=...)            m.to_mesh()
    m + n  m - n  m ^ n           Manifold.batch_boolean([...], OpType.Add)
    m.minkowski_sum(n)            Manifold.cylinder(h, r_low, r_high, circular_segments=, center=)
    m.translate / rotate / mirror / scale / transform
    m.num_tri() / num_vert() / volume() / is_empty() / status()
    triangulate(rings)            (trimesh's polygon triangulation engine)

Minkowski sums can be routed elsewhere (the worker pool) through
set_minkowski_hook(fn): fn(a, b) returns a Manifold, or None to compute here.
"""
import js
import numpy as np
from pyodide.ffi import to_js

_W = js.globalThis.__manifold
_minkowski_hook = None


def set_minkowski_hook(fn):
    global _minkowski_hook
    _minkowski_hook = fn


def _typed(arr, kind):
    a = np.ascontiguousarray(arr, dtype=np.float32 if kind == "f" else np.uint32)
    buf = to_js(a.tobytes()).buffer
    return js.Float32Array.new(buf) if kind == "f" else js.Uint32Array.new(buf)


def _np(jsarr, dtype):
    return np.frombuffer(jsarr.to_bytes(), dtype=dtype)


def _vec(v):
    return to_js([float(x) for x in v])


class OpType:
    Add = "add"
    Subtract = "subtract"
    Intersect = "intersect"


class Mesh:
    def __init__(self, vert_properties=None, tri_verts=None, **_ignored):
        self.vert_properties = np.asarray(vert_properties, dtype=np.float32).reshape(-1, 3) \
            if vert_properties is not None else np.zeros((0, 3), np.float32)
        self.tri_verts = np.asarray(tri_verts, dtype=np.uint32).reshape(-1, 3) \
            if tri_verts is not None else np.zeros((0, 3), np.uint32)


class Manifold:
    __slots__ = ("_m",)

    def __init__(self, mesh=None, _js=None):
        if _js is not None:
            self._m = _js
            return
        if mesh is None:
            self._m = _W.Manifold.new(_W.Mesh.new(_opts(np.zeros((0, 3)), np.zeros((0, 3)))))
            return
        self._m = _W.Manifold.new(_W.Mesh.new(_opts(mesh.vert_properties, mesh.tri_verts)))

    def __del__(self):
        try:
            self._m.delete()
        except Exception:
            pass

    # ------------------------------------------------------------ data
    def to_mesh(self):
        jm = self._m.getMesh()
        n = int(jm.numProp)
        verts = _np(jm.vertProperties, np.float32).reshape(-1, n)[:, :3]
        tris = _np(jm.triVerts, np.uint32).reshape(-1, 3)
        try:
            jm.delete()
        except Exception:
            pass
        return Mesh(verts, tris)

    def num_tri(self):
        return int(self._m.numTri())

    def num_vert(self):
        return int(self._m.numVert())

    def volume(self):
        return float(self._m.volume())

    def surface_area(self):
        return float(self._m.surfaceArea())

    def is_empty(self):
        return bool(self._m.isEmpty())

    def status(self):
        return str(self._m.status())

    # ------------------------------------------------------------ booleans
    def __add__(self, other):
        return Manifold(_js=self._m.add(other._m))

    def __sub__(self, other):
        return Manifold(_js=self._m.subtract(other._m))

    def __xor__(self, other):
        return Manifold(_js=self._m.intersect(other._m))

    @staticmethod
    def batch_boolean(manifolds, op):
        items = to_js([m._m for m in manifolds])
        fn = {OpType.Add: _W.Manifold.union, OpType.Subtract: _W.Manifold.difference,
              OpType.Intersect: _W.Manifold.intersection}[op]
        return Manifold(_js=fn(items))

    def minkowski_sum(self, other):
        if _minkowski_hook is not None:
            out = _minkowski_hook(self, other)
            if out is not None:
                return out
        return Manifold(_js=self._m.minkowskiSum(other._m))

    # ------------------------------------------------------------ transforms
    def translate(self, v, y=None, z=None):
        v = v if y is None else (v, y, z or 0.0)
        return Manifold(_js=self._m.translate(_vec(v)))

    def rotate(self, v, y=None, z=None):
        v = v if y is None else (v, y, z or 0.0)
        return Manifold(_js=self._m.rotate(_vec(v)))

    def mirror(self, normal):
        return Manifold(_js=self._m.mirror(_vec(normal)))

    def scale(self, v):
        v = (v, v, v) if np.isscalar(v) else v
        return Manifold(_js=self._m.scale(_vec(v)))

    def transform(self, m34):
        m = np.asarray(m34, dtype=float)
        if m.shape == (3, 4):
            m = np.vstack([m, [0, 0, 0, 1]])
        return Manifold(_js=self._m.transform(to_js(list(m.T.ravel()))))   # column-major

    # ------------------------------------------------------------ primitives
    @staticmethod
    def cylinder(height, radius_low, radius_high=-1.0, circular_segments=0, center=False):
        return Manifold(_js=_W.Manifold.cylinder(float(height), float(radius_low), float(radius_high),
                                                  int(circular_segments), bool(center)))

    @staticmethod
    def cube(size=(1.0, 1.0, 1.0), center=False):
        size = (size, size, size) if np.isscalar(size) else size
        return Manifold(_js=_W.Manifold.cube(_vec(size), bool(center)))

    @staticmethod
    def sphere(radius, circular_segments=0):
        return Manifold(_js=_W.Manifold.sphere(float(radius), int(circular_segments)))

    @staticmethod
    def hull_points(points):
        return Manifold(_js=_W.Manifold.hull(to_js([[float(c) for c in p] for p in points])))


def _opts(verts, tris):
    return js.Object.fromEntries(to_js([["numProp", 3], ["vertProperties", _typed(verts, "f")],
                                        ["triVerts", _typed(tris, "u")]]))


def triangulate(rings, epsilon=-1):
    """trimesh's polygon triangulation: rings[0] is the outer ring (CCW), the
    rest are holes; returns (n, 3) indices into the concatenated rings. Done
    with shapely's constrained Delaunay triangulation, which adds no new
    vertices - the same contract as manifold's own triangulate()."""
    import shapely
    from shapely.geometry import Polygon
    rings = [np.asarray(r, dtype=float)[:, :2] for r in rings]
    allv = np.vstack(rings)
    index = {(float(x), float(y)): i for i, (x, y) in enumerate(allv)}
    poly = Polygon(rings[0], rings[1:])
    tris = []
    for t in shapely.get_parts(shapely.constrained_delaunay_triangles(poly)):
        c = list(t.exterior.coords)[:3]
        ids = [index[(float(x), float(y))] for x, y in c]
        (x0, y0), (x1, y1), (x2, y2) = allv[ids[0]], allv[ids[1]], allv[ids[2]]
        if (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0) < 0:
            ids = [ids[0], ids[2], ids[1]]
        tris.append(ids)
    return np.asarray(tris, dtype=np.int64).reshape(-1, 3)
