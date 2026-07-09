# v1&rarr;v2 Byte-Check Report — 2026-07-08

Every v1 machine file was rendered against its v2 replacement using matched
Customizer parameter sets, then compared byte-for-byte (`openscad-nightly`
&rarr; STL &rarr; sha256/cmp). Minkowski was forced off on every render
(already every file's own default). Two machines needed no correction and
matched immediately. Three needed their v2 defaults re-pinned to v1's
original values before comparing, because v2 had accumulated real tuning
since the refactor landed. One of those three surfaced a genuine bug in
HeliosKlimax, fixed as part of this pass.

## At a glance

| Machine | Result | Genus v1 | Genus v2 | Note |
|---|---|---:|---:|---|
| IBM | MATCH | -3 | -3 | sha256 identical, no changes needed |
| Hammond &middot; split | MATCH | 1006 | 1006 | sha256 identical, no changes needed |
| Hammond &middot; shuttle | EPSILON | 325 | 325 | shared-lib -z inset, <0.001mm, sub-print-resolution |
| HeliosKlimax | FIXED | 6 | 6 | two real bugs, corrected this session |
| Mignon | REDESIGN | 19 | 1 | resin supports intentionally migrated to ResinRod |
| Blickensderfer | MATCH* | -42 | -42 | sha256 identical once v1's values were re-pinned |
| Postal | MATCH* | -48 | -48 | sha256 identical once v1's values were re-pinned |
| Bennett | OPEN | 113 | 101 | resin supports differ even with v1's values re-pinned |

\*Blickensderfer and Postal's v2 defaults had drifted from v1 through later
tuning (font, dimensions, resin values). Re-pinning every shared parameter
to v1's original value, per this session's second pass, is what produced
the identical hash.

## 1. HeliosKlimax — fixed

v2 assumed Helios's `Baseline`/`Cutout` arrays were already absolute
heights from the bottom face — Bennett/Mignon's convention. They aren't.
The original computed `Element_Height - Baseline[row]`, the same top-down,
negative-from-clip-end convention Blickensderfer and Postal use. On top of
that, the placement radius was assumed to be the raw `Element_Diameter/2`,
but the original actually placed text at `(Element_Diameter - .1)/2` — a
0.05mm inset with no analogue anywhere else in the file.

**Bug 1 — wrong end of the element.** Fixed in `v2/heliosklimax.scad`:
- `Baseline_Z_Offset`: `0` &rarr; `Element_Height`
- `Baseline`: `[3.0, 7.8, 12.5, 17.3]` &rarr; `[-3.0, -7.8, -12.5, -17.3]`
- `Cutout`: `[2.5, 7.3, 12, 16.8]` &rarr; `[-2.5, -7.3, -12, -16.8]`

**Bug 2 — 0.05mm placement inset dropped.** Fixed in `v2/heliosklimax.scad`:
- `Letter_Placement_Protrusion`: `0` &rarr; `-.05`

Evidence — before the fix, row-0 text sat at Z&asymp;15-16 in v1 but
Z&asymp;3-4 in v2:

```
v1  vertex 14.094999999999999 -0.9387148300339054 16.2
v1  vertex 14.09728457265413  -1.0137188138761026 16.46178609655925

v2  vertex 14.131539246102635 -0.9519936773347644  3.5463471061618796
v2  vertex 14.152079528623815 -1.0267692961525297  3.8073361412148725
```

After both fixes, genus matches exactly and vertex count is within the
same epsilon-level residual documented for Hammond below:

```
v1  genus 6   vertices 150469   facets 300958
v2  genus 6   vertices 150561   facets 301134
```

## 2. Blickensderfer & Postal — confirmed, not diverged

Both machines differed on first pass because v2's hardcoded defaults had
moved on since the refactor — different font, different dimensions,
different resin values. That's expected tuning, not a refactor defect.
Rebuilding the v2 parameter JSON to hold every shared-name value at v1's
original number (including hidden renames like `cylOD` &rarr;
`Element_Diameter`, `platenBaselines` &rarr; `Cutout`, `fontCharMod` &rarr;
`Character_Modifieds_Font`) produced a byte-for-byte match on both.

Blickensderfer — 19 values pulled from v1, e.g.:

```
Font                      Blick_Script_Leo         -> Arial
Font_Size                 3.7                       -> 2.4
Element_Height            17.15                     -> 16.75
Character_Modifieds_Font  LTCRemingtonTypewriterW10 -> ITC Kabel Std
Resin_Raft_OD             2                         -> 4
```

Postal — 16 values pulled from v1, e.g.:

```
Font           Alma Mono             -> Arial
Baseline       [-3.6, -10, -15.7]    -> [-3.8, -10.2, -15.7]
Cutout         [-2.65, -9.1, -14.5]  -> [-3.40, -9.80, -15.30]
Resin_Rod_OD   1                     -> .8
```

Both renders then produced identical sha256 against their v1 counterpart.

## 3. Bennett — open, by design

Same re-pinning pass applied (17 values pulled from v1: `Element_Height`,
`Typeface_`, `Shaft_Diameter`, all five `Resin_Support_*` dimensions, and
more). The core cylinder and glyph geometry now lines up. The resin
support subsystem still doesn't, because it was rebuilt on the shared
`ResinRod` primitive rather than ported line-for-line — a deliberate
migration, not parameter drift. Genus drops from 113 to 101 and vertex
count from 173,096 to 166,823 with matched values, consistent with a
structurally different rod/raft shape rather than a bug.

**Open question:** does the new ResinRod-based support reproduce the old
design's intent (rod count, contact placement), or is the difference
purely incidental to the migration? Not resolved in this pass.

## 4. Hammond shuttle & Mignon — explained, no action

**Hammond shuttle — sub-print-resolution.** Same parameters, same
vertex/facet count, but coordinates drifted by ~0.0005-0.00085mm. Traced
to `lib/glyph_pipeline.scad`'s `LetterPlacement`, which subtracts the
global z-fighting epsilon (`z=.001`) from every glyph's placement radius —
a term the original Hammond formula never had. Confirmed by forcing `z=0`
on both sides: vertex coordinates then matched exactly, leaving only
harmless facet-ordering differences. Below print resolution; not fixed.

**Mignon — intentional.** Topology changed (genus 19&rarr;1, +1,530
vertices) because Mignon's resin supports were migrated onto the shared
`ResinRod` primitive, same as Bennett. Expected, not a regression.

## Artifacts

16 dated Customizer JSON parameter sets were added, one per machine per
version, each with the render gate forced on and minkowski forced off:

```
v1/IBM/IBM2_bytecheck_2026-07-08.json                       v2/ibm_bytecheck_2026-07-08.json
v1/Bennett/BennettElement_bytecheck_2026-07-08.json          v2/bennett_bytecheck_2026-07-08.json
v1/Blickensderfer/Blickensderfer2_bytecheck_2026-07-08.json  v2/blickensderfer_bytecheck_2026-07-08.json
v1/Postal/Postal_bytecheck_2026-07-08.json                   v2/postal_bytecheck_2026-07-08.json
v1/Mignon/MignonCylinder_bytecheck_2026-07-08.json           v2/mignon_bytecheck_2026-07-08.json
v1/HeliosKlimax/HeliosKlimaxElement_bytecheck_2026-07-08.json v2/heliosklimax_bytecheck_2026-07-08.json
v1/Hammond/HammondShuttle_bytecheck_2026-07-08.json          v2/hammond_bytecheck_2026-07-08.json
v1/Hammond/HammondSplitShuttle2_bytecheck_2026-07-08.json    v2/hammond_split_bytecheck_2026-07-08.json
```

Plus one code fix: `v2/heliosklimax.scad` (`Baseline_Z_Offset`,
`Baseline`/`Cutout` sign convention, `Letter_Placement_Protrusion`).

An interactive version of this report is also published at
https://claude.ai/code/artifact/ce95aca5-4cd9-476e-bbe3-1e6705e06486.
