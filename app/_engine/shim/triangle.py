"""
In-browser stand-in for the `triangle` package (Shewchuk's Triangle, a C
extension with no WebAssembly build). v4 asks trimesh for the triangle
engine explicitly (glyph_poc.py, triangle_args='p'), and trimesh calls
triangulate({"vertices", "segments", "holes"?}, "p") expecting
{"vertices", "triangles"} back.

'p' means: triangulate the planar straight-line graph with every input
vertex kept and no quality refinement. Here: polygonize the segments,
drop faces that contain a hole point, and run shapely's constrained
Delaunay triangulation on each remaining face. It adds no vertices, so
triangles index straight into the input vertices, same as Triangle with 'p'.
The triangulation can differ from Triangle's, but it covers the same region,
so the solid (and its volume) is the same.
"""
import numpy as np
import shapely
from shapely.geometry import LineString, Point


def triangulate(tri, opts="p"):
    verts = np.asarray(tri["vertices"], dtype=float)[:, :2]
    segs = np.asarray(tri.get("segments", []), dtype=int)
    holes = [Point(h) for h in np.asarray(tri.get("holes", []), dtype=float).reshape(-1, 2)]
    index = {(float(x), float(y)): i for i, (x, y) in enumerate(verts)}
    lines = [LineString([verts[a], verts[b]]) for a, b in segs]
    faces = [f for f in shapely.get_parts(shapely.polygonize(lines))
             if not any(f.contains(h) for h in holes)]
    out = []
    for face in faces:
        for t in shapely.get_parts(shapely.constrained_delaunay_triangles(face)):
            ids = [index.get((float(x), float(y))) for x, y in list(t.exterior.coords)[:3]]
            if None in ids:
                continue   # a vertex the input didn't have - never expected with 'p'
            (x0, y0), (x1, y1), (x2, y2) = verts[ids[0]], verts[ids[1]], verts[ids[2]]
            if (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0) < 0:
                ids = [ids[0], ids[2], ids[1]]
            out.append(ids)
    return {"vertices": verts, "triangles": np.asarray(out, dtype=np.int64).reshape(-1, 3)}
