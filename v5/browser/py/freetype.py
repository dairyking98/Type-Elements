"""
In-browser stand-in for freetype-py (which has no WebAssembly build),
written on fontTools (which Pyodide ships). It covers exactly the surface v4
uses, so v4's code runs unchanged:

    Face(path).units_per_EM / family_name / style_name
    face.get_char_index(code) / get_chars() / set_char_size(...)
    face.load_char(char, flags) / load_glyph(gid, flags)
    face.glyph.outline.points / tags / contours / n_contours / n_points
    face.glyph.advance.x
    FT_LOAD_NO_SCALE, FT_LOAD_NO_HINTING, FT_LOAD_DEFAULT

Always raw font units (v4 only ever loads with FT_LOAD_NO_SCALE).

Outlines match FreeType's FT_Outline conventions, which is what
glyph_poc.contour_to_points() walks:
  - TrueType (glyf): the table's own points and on/off flags, composites
    flattened - exactly what FreeType hands back. Tag 1 = on-curve,
    0 = quadratic off-curve.
  - CFF/OTF: drawn through a pen; tag 1 = on-curve, 2 = cubic off-curve
    (always a pair before the next on-curve point), matching FreeType's CFF
    loader.
"""
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

FT_LOAD_DEFAULT = 0
FT_LOAD_NO_SCALE = 1
FT_LOAD_NO_HINTING = 2


class _Vec:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y


class _Outline:
    def __init__(self, points=(), tags=(), contours=()):
        self.points = list(points)
        self.tags = list(tags)
        self.contours = list(contours)

    @property
    def n_contours(self):
        return len(self.contours)

    @property
    def n_points(self):
        return len(self.points)


class _Glyph:
    def __init__(self):
        self.outline = _Outline()
        self.advance = _Vec()


class _FTPen(BasePen):
    """Records a CFF outline as FreeType-style point/tag/contour arrays."""

    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.points, self.tags, self.contours = [], [], []
        self._start = None

    def _moveTo(self, p):
        self._start = len(self.points)
        self.points.append((round(p[0]), round(p[1])))
        self.tags.append(1)

    def _lineTo(self, p):
        self.points.append((round(p[0]), round(p[1])))
        self.tags.append(1)

    def _curveToOne(self, c1, c2, p):
        for q, tag in ((c1, 2), (c2, 2), (p, 1)):
            self.points.append((round(q[0]), round(q[1])))
            self.tags.append(tag)

    def _qCurveToOne(self, c, p):
        for q, tag in ((c, 0), (p, 1)):
            self.points.append((round(q[0]), round(q[1])))
            self.tags.append(tag)

    def _closePath(self):
        if self._start is None:
            return
        # FreeType doesn't repeat the start point at the end of a closed contour
        if len(self.points) - self._start > 1 and self.points[-1] == self.points[self._start] and self.tags[-1] == 1:
            self.points.pop()
            self.tags.pop()
        self.contours.append(len(self.points) - 1)
        self._start = None

    _endPath = _closePath


class Face:
    def __init__(self, path, index=0):
        self._font = TTFont(path, fontNumber=index, lazy=True)
        self._cmap = self._font.getBestCmap() or {}
        self._order = self._font.getGlyphOrder()
        self._gid = {name: i for i, name in enumerate(self._order)}
        self._glyphset = self._font.getGlyphSet()
        self._is_tt = "glyf" in self._font
        self.units_per_EM = self._font["head"].unitsPerEm
        hhea = self._font["hhea"] if "hhea" in self._font else None
        self.ascender = hhea.ascent if hhea else 0
        self.descender = hhea.descent if hhea else 0
        self.height = (hhea.ascent - hhea.descent + hhea.lineGap) if hhea else 0
        self.num_glyphs = len(self._order)
        name = self._font["name"]
        self.family_name = (name.getDebugName(1) or "").encode()
        self.style_name = (name.getDebugName(2) or "").encode()
        self.glyph = _Glyph()

    def set_char_size(self, *args, **kwargs):
        pass   # v4 only ever reads raw font units

    def get_char_index(self, code):
        if isinstance(code, str):
            code = ord(code)
        name = self._cmap.get(code)
        return self._gid.get(name, 0) if name else 0

    def get_chars(self):
        for code, name in sorted(self._cmap.items()):
            yield code, self._gid.get(name, 0)

    def load_char(self, char, flags=FT_LOAD_DEFAULT):
        self.load_glyph(self.get_char_index(char), flags)

    def load_glyph(self, gid, flags=FT_LOAD_DEFAULT):
        name = self._order[gid] if 0 <= gid < len(self._order) else self._order[0]
        g = _Glyph()
        g.advance.x = self._font["hmtx"][name][0]
        if self._is_tt:
            glyf = self._font["glyf"]
            coords, ends, flags_ = glyf[name].getCoordinates(glyf)
            g.outline = _Outline([(int(x), int(y)) for x, y in coords],
                                 [1 if (f & 1) else 0 for f in flags_], list(ends))
        else:
            pen = _FTPen(self._glyphset)
            self._glyphset[name].draw(pen)
            g.outline = _Outline(pen.points, pen.tags, pen.contours)
        self.glyph = g
