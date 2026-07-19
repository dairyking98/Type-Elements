# Font audit — `/home/lchau/fonts/Custom & Modified`

Triggered by: `TextRing: [43/84] building 'E' (row 1, col 14)... SKIPPED (A
linearring requires at least 4 coordinates.)` on Blick Script Leo. User asked
for a full sweep of the Custom & Modified library for similar issues.

## Result

**Every character that failed across all 27 fonts (52 glyph-instances) was
fixed by three targeted patches to `lib/glyph_poc.py`. Zero font files were
edited.** What looked like 18 broken fonts needing individual repair turned
out to be a handful of edge cases in our own outline-processing code, plus a
small amount of genuine (and harmless, sub-visual) font debris that the same
code fix also absorbs.

Verified three ways after the fix:
- Full 90-character × 27-font sweep: 0 errors (was 52), 0 regressions (every
  font's ok/error/empty/missing totals match the pre-fix run exactly).
- Area-diff regression check: 90 hole-heavy glyphs (`e o a g B O Q 8 & @ R m n
  D P` across 6 fonts already passing before the fix) compared old algorithm
  vs. new, byte-for-byte same silhouette area on all 90 (0.000% diff).
- Full `build_glyph()` (not just the low-level contour/triangulate steps) on
  all 20 originally-broken characters: all 20 now produce watertight,
  `is_volume=True` meshes end-to-end.

## Root causes found

### 1. All-off-curve TrueType contours (not a font bug)

TrueType allows a contour made entirely of off-curve points — a legal,
common shorthand for small round details (dots, bullet circles, the "00"
bubbles in a `%`) where every consecutive pair of off-curve points implies
its own on-curve midpoint, so the loop closes with no explicit anchor point
anywhere. FreeType and FontForge both handle this correctly. Our own
`contour_to_points()` (`lib/glyph_poc.py`) required at least one real
on-curve point to seed its walk and raised `StopIteration` when a contour had
none — flagging perfectly valid glyphs as broken.

Affected (all confirmed clean/intentional font data): Berolina `%`, Goudy
Italic `i`/`j`, Olympe TRIAL `.`, Royal Vogue (+v3) `%`.

**Fix:** when a contour has zero on-curve points, synthesize the same
implied on-curve point FreeType uses internally — the midpoint of the last
and first points — before walking. (`contour_to_points`, ~line 181)

### 2. Overlapping outer islands + fragile hole-nesting (not a font bug)

`classify_and_triangulate()` assigned each hole to a single "tightest
containing shell" and triangulated each outer shell independently, assuming
outer shells never overlap each other. That assumption fails on
hand-digitized script fonts, which are routinely built from several
separately-drawn pen-stroke shapes that deliberately overlap where they
should join. When a tiny decorative loop sat inside the overlap zone of 2-3
different strokes, the raw containment-count "depth" came out inconsistent
(no single shell was the correct "immediate parent"), and `min()` on an
empty candidate list raised `ValueError`.

Affected (confirmed valid, non-self-intersecting geometry — same bug present
in Blick Script's *un-modified original*, so not introduced by any of the
"Mod"/"Leo"/"Swedish Chars" edits): Blick Script `3`/`E`, Blick Script -
Swedish Chars `3`/`E`, Blick Script Mod `3`/`E`.

**Fix:** replaced per-shell containment assignment with real boolean
geometry — union same-depth material, subtract same-depth holes, ascending
by nesting depth (standard even/odd nested-contour composition). Union
doesn't care whether its inputs already overlap, so overlapping strokes are
no longer a special case. (`classify_and_triangulate`, full rewrite)

### 3. Self-intersecting contours (pre-existing in the source designs, not
introduced by any Custom & Modified edit)

A handful of glyphs have a genuine tiny self-crossing in their outline —
confirmed present even in the untouched original source fonts (verified
against Peter Wiegel's original Rotunda, the base AverageMono.otf, and the
original Moderne Fraktur UNZ1), so these predate and are unrelated to any
edit made in this library. All are sub-visual: `.buffer(0)` (shapely's
standard self-intersection repair) reproduces the exact same silhouette
area, confirming the fix removes a zero/negligible-area glitch, not
reshaping the letterform.

Affected: AverageMono Mod `6`, Blick Script `3`/`E` (also caught by #2),
Blick Script Mod `3`, Mono Fraktur - Monospaced `T`, Rotunda Pommerania `s`,
Spencerian `R`.

**Fix:** `.buffer(0)` every contour polygon before both depth-classification
and the union/difference composition. (`classify_and_triangulate`)

### 4. Stray debris contours (genuine, harmless font-editing leftovers)

A handful of glyphs carry a leftover 1-2 point "contour" — an orphaned
control point from some past edit, not real geometry. A contour that short
can never enclose area, so `Polygon()` itself already rejects it before
`.buffer(0)` gets a chance ("A linearring requires at least 4 coordinates").

Affected: Blackletter Asterisk `R` (inherited by Blackletter Mod), Blick
Script - Swedish Chars `E`, Blick Script Leo `3`/`E`, Tremble 308 `b`.

**Fix:** drop any contour with fewer than 3 points before constructing
Polygon objects. (`classify_and_triangulate`, top of function)

## Changes made

`lib/glyph_poc.py` only:
- `contour_to_points()`: synthesize an implied on-curve start point for
  all-off-curve contours.
- `classify_and_triangulate()`: drop <3-point debris contours; `.buffer(0)`
  every remaining contour; replace shell/hole containment assignment with
  real per-depth-level union/difference composition.

No font files in `Custom & Modified` were modified. (An earlier pass of this
investigation produced FontForge-side repaired copies for AverageMono Mod
and Blackletter Asterisk/Mod before the deeper root cause — #2/#3 above —
was found; those copies are redundant with the pipeline fix and were
discarded.)

## Remaining — coverage gaps, not corruption, not auto-fixable

These are real characters simply not drawn in these fonts. Restoring them
requires actual glyph design work, not a mechanical fix, so they're left
as-is pending a decision on whether/how to fill them in.

**Blank but mapped** (cmap entry exists, glyph has zero contours):
- Blackletter Asterisk: `+ = £ § ä ö ü` (Blackletter Mod inherits these plus
  its already-intentional blank `*`)
- Blick Vertical Script: `£ § ä ö ü`
- Olympe TRIAL / Olympe TRIAL Light: `" $ ¢ £` (both)
- Spencerian: `^ £ §`

**Missing entirely** (not in the font's character map at all — informational
only, ~183 instances across the library, heaviest in Shmulik CLM which is a
Hebrew/niqqud font and largely not expected to cover this Latin charset).

## Methodology

Audit driven directly through the real pipeline calls (`get_glyph_contours_
and_advance` → `classify_and_triangulate`, the same two calls `build_glyph`/
`TextRing` make) against the union of every character used by either
machine layout (`config/blickensderfer.yaml` + `config/postal.yaml`, 90
unique characters), across all 27 `.ttf`/`.otf` files in `Custom & Modified`.
