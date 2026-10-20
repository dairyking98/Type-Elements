"""
Builds OCRA-TE.ttf, the in-browser stand-in for Monotype's OCR-A II (a
commercial font we can't redistribute), from John Sauter's public-domain
OCR-A (Debian's fonts-ocr-a, OCRA.ttf).

Same design, different proportions: per em the free font's glyphs are 14%
taller and its advance 18% wider. So the outlines are scaled (via
unitsPerEm) to OCR-A II's cap height, and every glyph gets OCR-A II's
advance (0.604 em), recentred - a logo or label at a given size_mm comes out
the same size as with the real thing.

    python3 make_ocra.py /usr/share/fonts/truetype/ocr-a/OCRA.ttf OCRA-TE.ttf
"""
import sys

from fontTools.ttLib import TTFont

CAP_FREE, CAP_II = 0.7398, 0.6489     # 'H' height / em, measured
ADV_II = 0.604                        # OCR-A II's (monospaced) advance / em

src, dst = sys.argv[1:3]
f = TTFont(src)
upem = round(f["head"].unitsPerEm * CAP_FREE / CAP_II)
f["head"].unitsPerEm = upem
adv = round(ADV_II * upem)
glyf, hmtx = f["glyf"], f["hmtx"]
for name in f.getGlyphOrder():
    width, lsb = hmtx[name]
    if width == 0:
        continue
    shift = (adv - width) // 2
    g = glyf[name]
    if g.numberOfContours > 0:      # simple glyph; composites follow their parts
        g.coordinates.translate((shift, 0))
        g.recalcBounds(glyf)
    hmtx[name] = (adv, lsb + shift)
f["hhea"].advanceWidthMax = adv
f["OS/2"].xAvgCharWidth = adv
for rec in f["name"].names:
    if rec.nameID in (1, 4, 16):
        rec.string = "OCR-A TE"
    elif rec.nameID == 6:
        rec.string = "OCR-A-TE"
f.save(dst)
print(f"{dst}: unitsPerEm {upem}, advance {adv}")
