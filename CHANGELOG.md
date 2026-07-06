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
- `resin_support.scad` — Blickensderfer2/Postal's `CutGroove`/
  `SpeedHoleSupport`/`DrivePinSupport`/`BottomSupports` placement system
  (the single-rod primitive itself now lives in `resin_rod.scad`, see below).
  Not shared by Helios/IBM/Hammond, whose resin-support geometry is genuinely
  different (see `docs/resin-supports.md`) and stays local to each v2 file.
- `resin_rod.scad` — the universal single resin-support-rod shape (`hull()`
  tapered tip + `hull()` capsule shaft + optional raft frustum), split out of
  `resin_support.scad` so machines with their own placement pattern can still
  reuse the one rod primitive. `resin_support.scad` includes it internally,
  so Blickensderfer2/Postal need no changes. Bennett and Mignon now include
  it directly (see below) - see `docs/resin-supports.md`.
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

### Global/Render Parameters naming consistency

An audit (prompted by a direct check across all 8 files) found that Global
Parameters and Render Parameters weren't actually consistent, despite the
stated goal - some machines only *bridged* their old names to the canonical
ones deep in the "Glyph pipeline lib wiring" section rather than renaming the
declarations themselves, and the declared order silently diverged between
files:

- **Bennett/Mignon/Helios Klimax**: Global Parameters still declared
  `surface_fn`/`criticalcyl_fn`/`resin_fn`/`mink_fn`/`text_fn` (their original
  underscore-style names) and bridged them to `surfaceFn`/`cylFn`/`resinFn`/
  `minkFn`/`textFn` in a separate block further down. Renamed the
  declarations directly and removed the now-redundant bridging blocks.
  Helios's `minkFn` had no independent value at all (aliased to `text_fn`) -
  given its own literal (`minkFn=20`, matching every other machine's
  default; inert unless `minkOn` is enabled).
- **Render Parameters order**: Blickensderfer2/Postal declare `minkOn`/
  `minkDraftAngle` *before* `XSection`/`XSectionTheta`; Bennett/Mignon/Helios
  Klimax/IBM had drifted to the opposite order. Reordered the latter four to
  match Blickensderfer2/Postal (the original reference files).
- **IBM**: also had a leftover no-op `$fn=$preview?44:44;` (both ternary
  branches identical) - simplified to `$fn=44;`.
- **Hammond**: Global Parameters already used canonical camelCase names but
  in the wrong order - reordered to match.
- **Hammond split**: had no separate Global Parameters section at all
  (merged into a single `[Rendering]` block, its own original header before
  this refactor), and used `minkText`/`minkAngle` instead of `minkOn`/
  `minkDraftAngle`. Split the section and renamed both - confirmed a pure
  rename, not a behavior change: `minkRadius=tan(minkAngle/2)*minkHeight`
  reduces to exactly the shared lib's `minkTextR(angle)=2*tan(.5*angle)` once
  `minkHeight`'s default (2) is substituted in.

Re-verified after this pass: all 8 files still render to clean STL with zero
warnings/errors, and the reference-keyboard echo feature (Bennett tested
directly) still works correctly.

### Capital_Snake_Case naming convention across all 8 files

Converted every top-level variable in `v2/` (lib files + all 8 machine
files) from a three-way mix of conventions - camelCase (`minkFn`, `cutoutTest`),
underscore-style leftovers (`surface_fn`, `criticalcyl_fn`), and IBM's own
SCREAMING_SNAKE_CASE (`RENDER_MODE`, `MINK_FLAT`) - to a single
`Capital_Snake_Case` convention everywhere (`Mink_Fn`, `Cutout_Test`,
`Render_Mode`, `Mink_Flat`). Rationale: OpenSCAD's Customizer panel displays
variable names with underscores converted to spaces but preserves letter
case, so `Weight_Adj_Mode` reads as "Weight Adj Mode" in the sidebar while
`WEIGHT_ADJ_MODE` would read as "WEIGHT ADJ MODE" - full-caps for every field
in the panel, not just the handful that should stand out. Modules and
functions were deliberately left in their existing PascalCase/camelCase
forms (`TextRing`, `minkTextR`, `testSweepArray`) since they're never shown
in the Customizer and staying visually distinct from data variables is its
own useful signal.

Scope decisions:
- Data-preset arrays that function like named constants (layout content in
  `lib/layouts/*.scad` - `DHIATENSOR`, `LAYOUTS`, etc. - and each machine's
  own `CUSTOM*`-prefixed entry-point arrays, e.g. Bennett/Mignon's
  `CUSTOMLAYOUT`, IBM's `CUSTOMCASES88`) were left as ALL-CAPS, matching the
  precedent already set for `lib/layouts/`.
- Module-local temporary variables (leading-underscore convention, e.g.
  `_placementMap` inside `TextRing()`) and module/function parameter names
  (e.g. `TwoDText(char, font, size)`) were left alone - never Customizer-
  visible, changing them serves no part of the stated goal.
- IBM's own SCREAMING_SNAKE_CASE settings/dimensions were converted too
  (`RENDER_MODE`->`Render_Mode`, `BOSS_OD`->`Boss_OD`) for true consistency,
  keeping known dimension abbreviations (OD, ID, IR, OR, R, D, H, CPI)
  uppercase rather than title-casing them into something like `Od`.

Caught three real bugs along the way, all from names that were supposed to
be identical across files/modules but weren't (or became so during the
rename):
- `lib/layouts/ibm_layouts.scad` referenced `RENDER_MODE`/`COMPOSER_LANGUAGE`/
  `S12_88_LANGUAGE` by their pre-rename names - a separate file from
  `ibm.scad` that's easy to forget when renaming the declaring file. Fixed.
- IBM's `FONT2SIZE` (computed, `RENDER_MODE`-selected) and `FONT2_SIZE`
  (literal, `2.4`) are two genuinely different variables that both wanted to
  become `Font2_Size` - the exact same collision class already handled for
  `FONTSIZE`/`FONT_SIZE` earlier in the same file, just missed the second
  instance. Renamed the computed one to `Font2_Size_Selected`, matching its
  sibling `Font_Size_Selected`.
- Hammond's `AnvilID` (raw literal, `66.0`) and `Anvil_ID` (computed,
  `AnvilID+2*anviliroffset`) collapsed to the same name the same way.
  Renamed the raw literal to `Anvil_ID_Raw`.
- A more subtle one caught only by testing, not by the duplicate-declaration
  check: the auto-rename script renamed every occurrence of `font`,
  including the `font=` *keyword argument name* inside `text()` calls (an
  OpenSCAD builtin parameter, not a variable of ours) - `openscad-nightly`
  flagged this immediately as "variable Font not specified as parameter."
  Fixed by reverting keyword-argument-position occurrences back to lowercase
  `font=` everywhere, leaving genuine variable references as `Font`.

Also found (and left alone, since they're pre-existing and already proven
safe): `Render`/`module Render()` in `ibm.scad` and `Groove`/
`module Groove()` in `hammond.scad` are same-named variable/module pairs
that already existed before this pass and render without any issue -
OpenSCAD keeps separate namespaces for variables vs. modules/functions.
Two *new* collisions introduced by this rename (`Arc`/`module Arc()` and
`Logo`/`module Logo()` in `hammond_split.scad`) were checked the same way;
`Arc` (a computed angle colliding with unrelated arc-drawing geometry) was
renamed to `Arc_Extent` for clarity, `Logo` (a boolean toggle named after the
feature it enables, matching the already-accepted `Render`/`Groove`
pattern) was left as-is.

Re-verified after every file: renders to clean STL with zero warnings/
errors, no duplicate top-level declarations, and the `Test_Layout`/
`Baseline_Test`/`Cutout_Test` calibration echoes (including the reference-
keyboard feature) produce correct output on every machine.

Still not independently re-verified beyond "renders without error/warning":
- `$fn`-dependent curve smoothness (visual quality, not something a
  render-to-STL pass checks)
- minkowski draft-cone geometry for machines whose `Mink_On`/mink toggle is
  off by default (Bennett, Mignon, Helios Klimax, Hammond) and so were
  accepted by structural analogy rather than a from-scratch numeric
  derivation - turning `Mink_On=true` renders without error, but the actual
  taper shape against the original hasn't been compared point-by-point

### Bennett/Mignon migrated onto the shared `ResinRod()` primitive

Bennett and Mignon each hand-rolled their own resin-support-rod shape
(Bennett: flat cylinder shaft + 1mm cone taper + sphere tip + a base cone
flare with a `db` buildplate-diameter parameter that was accepted but never
actually used, the flare was hardcoded to `2.4` instead; Mignon: cylinder
shaft + 1mm cone tip ending in a flat disk, no sphere at all). Both were
already structurally close to Blickensderfer2/Postal's shared `ResinRod(h)`
(`lib/resin_rod.scad`, split out of `resin_support.scad` above), so this was
a faithful port of the rod shape only - each machine's own rod *placement*
(Bennett's 2 outer rings + 1 inner ring with a `Pyramidzoffset` curvature
correction; Mignon's 2 interleaved 12-fold rings) stays local, since neither
matches Blick/Postal's speed-hole/sloped-floor placement system.

Both wire `Resin_Rod_Raft=false`/`Resin_Min_Rod_Height=0`/
`Resin_Raft_Thickness=0` since each already builds its own separate raft/
groove ring directly in `ResinSupport()` - same override pattern Postal
already uses for the same reason. Bennett's previously-dead `db` parameter
(`Resin_Support_Buildplate_Diameter`) is now actually wired to
`Resin_Raft_OD`, though it goes unused while `Resin_Rod_Raft=false`.

One real discrepancy caught mid-migration: Bennett's original centered its
tip sphere directly *at* z=h (`translate([0,0,h]) sphere(d=dc)`), so the
sphere's true apex sat at `h+dc/2`, not `h`. A first pass set
`Resin_Inset=0` (a "faithful port"), which actually under-reached the
original by `dc/2` (~0.35mm) - fixed by setting
`Resin_Inset=Resin_Support_Contact_Point_Diameter/2` instead, which restores
the exact original apex height. Confirmed by re-rendering: the STL's genus
(a coarse topology fingerprint) matched Bennett's pre-migration baseline
exactly (89) once fixed, versus 81 with the `Resin_Inset=0` mistake. Mignon
needed no such correction - its original tip was a flat disk with zero
embed, exactly matching `Resin_Inset=0`.

Verified with `openscad-nightly`: Blickensderfer2/Postal's resin-print STL
is byte-for-byte identical before/after the `resin_rod.scad` split (the
placement lib's behavior is untouched). Bennett/Mignon's full resin-print
renders manifold with zero errors post-migration, and isolated
`ResinSupport()` renders + mid-part cross-sections were checked visually to
confirm every rod still reaches its target contact point with no floating
gaps.

### `Mink_On` naming unified across all v2 machines

Bennett/Mignon/Helios Klimax each carried a leftover `Debug_No_Minkowski`
boolean (`Debug_No_Minkowski=true; Mink_On=!Debug_No_Minkowski;`) - two names
for the same toggle, inconsistent with Blickensderfer2/Postal/IBM/Hammond/
`hammond_split.scad`, which all declare `Mink_On=false;` directly. Collapsed
to the single name everywhere: same default (`false`), same behavior.
Mignon's `ElementLabel()` had one other live reference
(`if (Debug_No_Minkowski!=true)`), updated to the equivalent
`if (Mink_On==true)`. `docs/glyph-pipeline.md` and `docs/calibration.md`'s
mentions of the old name updated to match. Verified byte-identical STL
output before/after for all three machines.

### `v2/ibm.scad`: added Selectric III (96char) as a third `Render_Mode`

Adds `Render_Mode=2` alongside the existing Composer (88char) and Selectric
I/II (88char) modes - 4 rows of 24 characters instead of 22, same physical
ball shell (`Sphere_OD`/`Inside_ID` etc. unchanged - Selectric II and III
typeballs are the same shell, just a different character layout/count).

Character layout data (`LOWERCASE96_US`/`UPPERCASE96_US`/
`S3_LC_HEMISPHERE96`/`S3_HEMISPHERE_MAP` in `lib/layouts/ibm_layouts.scad`)
is derived from https://github.com/selectricrescueatx/TypeElements
(`SelectricElement96.scad`, CC BY 4.0, Dave Hayden/Steve Malikoff)'s
`LOWER_CASE`/`UPPER_CASE`/`charmap96` - re-derived here (row-by-row from
`charmap96`), not copied verbatim, since the reference repo builds the ball
with a different placement algorithm (one combined 24-position ring per
row) than this codebase's two-opposite-hemispheres-180-degrees-apart
convention. First attempt used `charmap96`'s own column order (p=0..11)
directly per row and initially matched that file's own "Keyboard location
of each letter on the ball" comment exactly - but checking the rendered
result against a real physical Selectric III element found the
longitudinal order (position going around each ring) came out mirrored.
Fixed by reversing each row's column order; the reversed order also turned
out to closely match (module 2 minor transcription typos) an earlier
abandoned draft of this same data already sitting in this file, commented
out. `S3_HEMISPHERE_MAP` was computed the same way the existing
`S12_HEMISPHERE_MAP`/`COMPOSER_HEMISPHERE_MAP` were (a `search()`-based
derivation, run once with `openscad-nightly` and hardcoded), not
hand-derived. This supersedes that earlier abandoned draft (commented out,
marked "I AM NOT WORRYING ABOUT FOR THE TIME BEING") which also had a real
bug - rows 2-3 of its `LOWERCASE96` were still capitalized - and didn't
include the reference repo's extra `²`/`§`/`³`/`¶` characters (present on
the ball but not reachable via the S3 keyboard).

Row latitudes (the 4-row tilt array, shared across all three modes) keep
this codebase's own existing measured values (`[32.8, 16.4, 0, -16.4]`)
rather than adopting the reference repo's own tuned values
(`[31.1, 15.7, 0, -15.7]`) - both are close, these are the ones already
proven out here.

Also fixed a real naming bug while touching this: `Latitude_Spacing` (the
`360/22` angle between characters around a ring) and `Longitude_Spacing`
(the 4-row tilt array) were swapped relative to standard geographic
convention - tracing actual usage showed the ring-position value was being
called "latitude" and the row-tilt value "longitude", backwards both ways.
Renamed to `Longitude_Step`/`Row_Latitudes` respectively, and cascaded the
same fix through every local variable/parameter that used `lat`/`long`/
`latitude`/`longitude` (`LATITUDE_LONGITUDE` -> `LONGITUDE_LATITUDE`,
`PlatenCutout`/`PositionText`/`SingleMinkowski`'s parameter names, etc.) -
purely a rename, no behavior change (verified byte-identical STL for
Composer/Selectric I-II before and after).

Every place that hardcoded "22 characters per row" / "88 total" now reads
from `Chars_Per_Row_All`/`Total_Chars_All`/`Hemisphere_Cols_Per_Row_All`
(indexed `[Composer, Selectric I/II, Selectric III]`), following the same
`All_Font_Sizes[Render_Mode]`-style indexing idiom already used throughout
this file. This included one genuinely mechanical (not cosmetic) count:
`Teeth()`'s detent-tooth loop, since the tilt-ring detent mechanism needs
one tooth per character index position (24 for Selectric III), confirmed by
the reference repo's own `DetentTeeth()` using the same
`CHARACTERS_PER_LATITUDE` for its tooth count.

Not extended to Selectric III (deferred, not required for a working
render): the `testSweepArray(...,22)`-based calibration sweep arrays
(`Cutout_Test_Angle_Array`/`Draft_Angle_Test_Array`/etc.) are still
fixed at length 22, so `Cutout_Test=true`/`Draft_Angle_Test=true` will
show `undef` for the last 2 characters of each Selectric III row. The
character mapping itself is unaffected (confirmed via the
`Char_Info_Row_Col_Sorted` debug echo: all 96 characters appear exactly
once, correctly positioned, with the two apparent "duplicates" - `,`/`.`
each appearing twice - being intentional/correct, matching the reference
repo's own source data where the comma/period keys have no distinct
shifted symbol).

Verified: Composer/Selectric I-II render byte-identical STL before and
after every step of this change (including the longitudinal-order fix, which
touches Selectric-III-only data). Selectric III renders manifold with zero
errors/warnings and its character-position mapping was checked against the
user's own physical Selectric III element - which is what caught the
mirrored longitudinal order in the first derivation attempt.

`Tooth()`'s detent-notch profile is narrowed for render modes with more
teeth per row than the 22 it was tuned for, matching a difference found by
diffing the reference repo's `SelectricElement88.scad` against
`SelectricElement96.scad`: the 96-char file applies
`scale([1.0,88/96,1.0])` to the identical tooth polygon, since 24 teeth
around the same ring need to be individually narrower than 22 to avoid
touching. Generalized to `scale([1, Chars_Per_Row_All[1]/
Chars_Per_Row_All[Render_Mode], 1])` (a no-op for Composer/Selectric I-II,
since both use the same 22-count). This codebase's tooth-ring radius
(`Detent_Valley_To_Center=6`) is nearly identical to the reference repo's
(`TOOTH_PEAK_OFFSET_FROM_CENTRE=6.1`), so the same crowding the reference
repo's own maintainers found applies here too - a side-by-side render
comparison didn't show obvious tooth overlap even without this fix, but a
thin overlap is easy to miss visually and would still silently fuse in the
boolean union, so the reference repo's own established fix was applied
rather than relying on that inconclusive visual check.

### `Resin_Detent_Clock_Offset`: decoupled from `Detent_Skirt_Clock_Offset`

The tooth-width narrowing above shifts each tooth's angular position
slightly, which also nudged `ResinRodAssemble()`'s "detent teeth supports"
resin rod ring, since it shared `Detent_Skirt_Clock_Offset` (the actual
teeth geometry's clock alignment) for its own placement. Added a separate
`Resin_Detent_Clock_Offset` (default 0, same as before) so the resin rod
ring's clocking can be tuned independently of the teeth geometry itself -
`Drive_Notch_Theta` and `Teeth()` still use `Detent_Skirt_Clock_Offset`
unchanged. Verified Composer/Selectric I-II still render byte-identical
(both offsets default to 0, so behavior is unchanged unless one is tuned
away from the other going forward).
