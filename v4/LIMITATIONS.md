# Known limitations

Split out of `README.md` to keep it direct - see
[`README.md`](README.md) for setup, usage and the machine list.

## Known limitations

- **TrueType-only outlines - RESOLVED.** CFF/OpenType (cubic-curve) fonts
  used to mis-parse silently - `contour_to_points` (`lib/glyph_poc.py`)
  only checked FreeType's on/off-curve bit, so a cubic off-curve point got
  misread as a lone quadratic control point, producing plausible-looking
  but geometrically wrong curves with no error raised (confirmed on
  `FreeMono-Bold.otf`: watertight-but-winding-inconsistent geometry).
  Fixed by checking the tag's low 2 bits (`FT_CURVE_TAG`: 0=quadratic,
  2=cubic) and subdividing a real cubic Bézier (`flatten_cubic()`, the
  cubic arm of the adaptive de Casteljau tracer) for cubic spans
  instead. Verified against real CFF fonts (`Alma Mono.otf`,
  `FreeMono-Bold.otf`) end-to-end through `generate.py config/postal.yaml`
  - fully watertight/winding-consistent/`is_volume`, 0 skipped characters
  - and confirmed byte-identical output on the quadratic (TrueType) path
  for Blickensderfer before/after. Note this is only about which curve
  format is INSIDE the file - `.otf` itself doesn't imply cubic (some OTF
  files are TrueType-flavored internally) and `.ttf` doesn't guarantee
  quadratic either; the code now handles either correctly regardless of
  file extension.
- **Self-intersecting drafts - RESOLVED.** The old per-vertex outline
  offset could fold through itself on narrow glyph features (71/84
  characters failed a `shapely` simplicity check at production settings -
  see git history for the detection/gated-repair machinery this used to
  need). A real Minkowski sum cannot produce a self-intersecting result on
  any input topology, so there is nothing left to detect or repair here;
  `TextRing()` no longer reports on this at all.
- **`place_on_cylinder()` needs `process=False`.** Reconstructing a mesh
  via `trimesh.Trimesh(vertices=..., faces=...)` with the default
  `process=True` silently re-runs vertex merging and corrupts already-valid
  geometry post-placement (reproduced with an identity transform alone:
  2195->1507 vertices, `watertight` True->False, nothing to do with the
  rotation/translation itself). Placement is a pure coordinate move - no
  topology change, no reprocessing needed.
- **Inter-character collisions are detected, not repaired.**
  `_check_inter_character_collisions()` in `lib/cylinder_machine.py`
  (shared, not per-machine) uses
  `trimesh.collision.CollisionManager` across all 84 placed parts (this is
  what that tool is actually for - checking DIFFERENT registered objects
  against each other - unlike an earlier, meaningless attempt earlier in
  this project's history that called it on a single mesh expecting
  self-intersection detection, which it never provided). At
  `separation_mm=2.0`, 61 adjacent-character pairs currently collide -
  confirmed real via a direct boolean intersection check (not just the
  collision manager's flag), and confirmed to sit right at the embedded
  root end (radius ~15.6mm, vs. the root anchor at 15.5mm), not near the
  visible outer surface - which is why it isn't visible just looking at
  the assembled ring from outside. Accepted as-is; there's no simple
  automatic geometric fix for two overlapping solids short of redoing
  their placement/size (or reducing `separation_mm`, which shrinks how far
  each root reaches - confirmed to eliminate collisions entirely at
  `separation_mm=1.0`, at the cost of less embedding-depth margin into the
  main body).
- **`FullElement`/`ResinPrint` run a detect + best-effort auto-repair
  pass** (`scad_primitives.check_and_repair()`) using trimesh's own
  `fill_holes`/`fix_winding`/`fix_inversion`/`fix_normals` on the final
  assembled solid, re-checking and reporting whether it actually helped.
  This targets combinatorial defects only (holes, inconsistent
  winding/normals) - it has no effect on overlapping geometry like the
  inter-character collisions above (confirmed: it never even runs there,
  since `watertight`/`winding_consistent`/`is_volume` all already report
  `True` for two overlapping-but-otherwise-valid solids).
- **`LogoText` centers horizontally on the ink bounding box, not the
  advance box** - unlike `TextRing` (which now does real advance-box
  centering, see [`PIPELINE.md`](PIPELINE.md)). Fine for a decorative logo, not
  attempted to match `v2`'s exact `halign=center` behavior there.
  Vertically, characters ARE aligned by baseline (`y=0`, FreeType's own
  pen-origin convention) rather than each character's own ink-bbox
  center - centering each character independently on its own ink bbox
  put 'L' (cap-height, no descender) and 'e' (x-height only) at different
  heights, breaking a common baseline across the ring.
- **`Drive_Pin_Style=1`** (the older drive pin variant) raises
  `NotImplementedError` - only the current/default style is ported.
- **`BottomSlopedSpace`'s `bottomX()`** (v2's name for it; v4 inlines the
  same formula) is ported from the real
  `lib/resin_support.scad` formula (`Bottom_Slope`/`Bottom_Z_Offset`), not
  approximated - flagging here only because an earlier draft of this file
  used a wrong approximation before the real formula was found; the
  current code is correct.
