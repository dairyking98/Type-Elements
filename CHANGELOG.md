# Changelog

## v2.0 — Shared library refactor

Executes `docs/refactoring-plan.md`'s target architecture. All work lives in
`v2/`; nothing in the original per-machine directories (`Blickensderfer/`,
`Postal/`, `Bennett/`, `Mignon/`, `HeliosKlimax/`, `IBM/`, `Hammond/`) was
modified or deleted — every v2 file names its V1 original in its own header
comment.

### New: `v2/lib/`

- `glyph_pipeline.scad` — the shared `TwoDText`/`WeightAdjShape`/
  `PlatenCutout`/`LetterPlacement`/`LetterText`/`TextRing` pipeline used by
  every cylinder-family machine (Blickensderfer, Postal, Bennett, Mignon,
  Helios Klimax) plus `hammond.scad` (HammondShuttle). Every machine declares
  the full canonical variable set directly (same names, same Customizer
  section order) rather than relying on silent per-machine defaults — see the
  file's own header comment for the complete parameter list and the
  per-machine equivalence notes (numeric verification for Bennett's platen
  cutout, algebraic verification for Helios, structural-analogy verification
  for Hammond's placement/baseline axis mapping).
- `resin_support.scad` — Blickensderfer2/Postal's `ResinRod`/`CutGroove`/
  `SpeedHoleSupport`/`DrivePinSupport`/`BottomSupports` system. Not shared by
  Bennett/Mignon/Helios/IBM/Hammond, whose resin-support geometry is
  genuinely different (see `docs/resin-supports.md`) and stays local to each
  v2 file.
- `core_shaft.scad` — Blickensderfer2/Postal/Bennett's core-groove/chamfer
  system (`SecondaryCore`, `CoreGrooves`, `CoreChamfer`, `CoreEllipses`).
  Mignon and Helios Klimax have no equivalent groove system.
- `layouts/` — pure layout data extracted verbatim: `blick_layouts.scad`,
  `bennett_layouts.scad`, `mignon_layouts.scad`, `ibm_layouts.scad`,
  `hammond_layouts.scad`.
- `testing.scad` — `testSweepArray(start, interval, count)`, the linear
  sweep-array formula (`start + interval*n`) shared by Blickensderfer2/
  Postal's `cutoutTestArray`/`baselineTestArray` and IBM's four independent
  sweep arrays (`CUTOUT_TEST_ANGLE_ARRAY`/`DRAFTANGLE_TEST_ARRAY`/
  `MINK_LONG_OFFSET_TEST_ARRAY`/`PLATEN_DIAMETER_TEST_ARRAY`) — wiring IBM
  into it also removed `TEST_ARRAY_MAP`, a dead identity-map indirection.
  Bennett/Mignon/Helios Klimax/Hammond use a fixed literal array of
  already-measured offsets instead of a uniform sweep, so there's nothing of
  theirs to extract here — only per-machine data, not duplicated logic. Also
  removed the dead, never-referenced `testing_console` variable from Bennett/
  Mignon/Helios Klimax, and Mignon's unused `TESTING` legend-array leftover.

### New: `v2/` thin machine files

| v2 file | Was | Glyph pipeline | Notes |
|---|---|---|---|
| `blickensderfer.scad` | `Blickensderfer/Blickensderfer2.scad` | shared lib | reference implementation for the lib |
| `postal.scad` | `Postal/Postal.scad` | shared lib | |
| `bennett.scad` | `Bennett/BennettElement2.scad` | shared lib | verified numerically equivalent to V1 |
| `mignon.scad` | `Mignon/MignonCylinder2.scad` | shared lib | V1 `Assert` render gate converted to `Render` |
| `heliosklimax.scad` | `HeliosKlimax/HeliosKlimaxElement.scad` | shared lib | V1 had no render gate at all — added one |
| `ibm.scad` | `IBM/IBM2.scad` | local (spherical geometry) | layout data extracted to `lib/layouts/ibm_layouts.scad`; Global/Render Parameters aligned to the shared convention |
| `hammond.scad` | `Hammond/HammondShuttle.scad` | shared lib | V1 `Assert` render gate converted to `Render`; added `skipPlatenCutout` to the lib to support Hammond's flat-anvil strike (no curved platen) |
| `hammond_split.scad` | `Hammond/HammondSplitShuttle2.scad` | local (two-sided arc geometry) | structurally further from the shared pipeline than `hammond.scad` — flagged as a candidate for a follow-up pass unifying both Hammond machines together |

Not migrated (per `docs/refactoring-plan.md`'s own "unmaintained/reference-only"
table): `BlickensderferElement.scad`, `HebrewBlickensderferElement.scad`,
`HammondSplitShuttle.scad`, `GalgolicHammondShuttle.scad`, `HammondIndex.scad`,
`TypeHeightFinder.scad`, `imagetest.scad`. Note: the plan doc listed
`HammondShuttle.scad` as superseded by `HammondSplitShuttle2.scad` — that
turned out to be wrong (they're two distinct machine types still in use, not
sequential versions), so both were migrated.

### Verified vs. not-yet-verified

Verified by code-level equivalence review throughout (algebraic/numeric
checks for the trickier transform-composition cases, called out in each
file's own header comment). `openscad-nightly` became available mid-refactor
(2026.06.12 snap) and all 8 `v2/` files were confirmed to actually parse and
render to non-degenerate STL geometry with zero warnings/errors:
`blickensderfer.scad`, `postal.scad`, `bennett.scad`, `mignon.scad`,
`heliosklimax.scad`, `ibm.scad`, `hammond.scad`, `hammond_split.scad`.

That pass caught one real bug pre-dating this refactor's later files:
`blickensderfer.scad`/`postal.scad` (the two earliest "gold standard"
references) still used lowercase `render`/`xSection`/`xSectionTheta` with a
separate `module Render(){}` wrapper, never renamed to the `Render`/
`XSection`/`XSectionTheta` top-level-gate convention every machine migrated
afterward received - so `-D Render=true` silently did nothing on those two
files. Fixed to match every other machine.

It also caught a real bug in the shared lib itself: `TextRingDebug`'s console
echo (fires when `cutoutTest`/`baselineTest`/`testLayout` is enabled) had a
hardcoded 3-entry `["lowercase","uppercase","figs"]` row-label array that
only fit Blick2/Postal/Bennett's true 3-row shift-key machines - it silently
printed `"undef row"` for Mignon (7 rows) and Helios Klimax (4 rows), and
would have for Hammond's 4th (Math) row too. Fixed with an optional
`rowLabels` lib parameter (default: numeric `"row N"`); Blickensderfer2/
Postal/Bennett/Hammond set it to their real shift names, Mignon/Helios
Klimax use the numeric default since their rows have no such semantic name.

### Reference-keyboard identification for the console echo

`testLayout=true` collapses every physical position's rendered glyph to a
single `testChar`, on purpose - it makes different positions' print quality
directly comparable on the physical part. But that also collapsed the
console echo's character label to the same `testChar` everywhere, making it
impossible to identify which keyboard key/lever a good-impression position
corresponded to on the real machine.

Fixed by decoupling the echo's label from the rendered character:
`TextRingDebug` now takes a `refChar` alongside `char`, and `TextRing`
computes it from an optional `referencePhysicalLayout` (default: falls back
to `physicalLayout` itself, so it's already fixed for every machine even
without further wiring). Blickensderfer/Bennett/Mignon - the machines with
both multiple selectable content layouts and a fixed hardware
keyboard→physical remap (`elementLayoutArrayMap`/`CharLegend`) - additionally
wire in a dedicated `referenceLayoutSelection` dropdown (reusing each
machine's own layout preset list), independent of whatever content
`Layout_Selection` is currently being printed. The physical keyboard's key
labels are a hardware fact of the machine, not a function of what you're
currently engraving, so switching what you're printing never changes what
the echo calls a given physical position. Postal/Helios Klimax/Hammond don't
get a dedicated dropdown - either they have only one fixed layout, or (for
Hammond) the layout array is already in physical/lever order with no
separate keyboard remap step - so the default fallback already reports the
correct reference character.

Example echo line with `testLayout=true` and Bennett's default
`referenceLayoutSelection=0` (English): `character keyboard key 'g'
(rendered as 'H') on lowercase row at the 3oclock position with platen
cutout at ...` - press the g lever on the real machine, find the best
impression, then find "keyboard key 'g'" in the console log.

Still not independently re-verified beyond "renders without error/warning":
- `$fn`-dependent curve smoothness (visual quality, not something a
  render-to-STL pass checks)
- minkowski draft-cone geometry for machines whose `minkOn`/mink toggle is
  off by default (Bennett, Mignon, Helios Klimax, Hammond) and so were
  accepted by structural analogy rather than a from-scratch numeric
  derivation - turning `minkOn=true` renders without error, but the actual
  taper shape against the original hasn't been compared point-by-point
