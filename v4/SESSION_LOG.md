# v4 session log

Chronological record of this session's work, for resuming later. See
`README.md` for the architecture/usage reference of the *current* state;
this file is the history and the "what's next."

## Where things stand right now (latest session, branch `v4-tui`)

- **`tune.py`, an interactive `textual` TUI, was built essentially from
  scratch this session** and now covers the entire config: Font &
  Alignment, Type Test, Resin, Gauge, Build, Layout, Quality, Logo,
  Element tabs, a master/running/saved config-tier system, a real file
  browser (`textual-fspicker`) for font paths and Save, and an f3d
  auto-launch/raise integration for live preview. See README's
  "Interactive tuner" section for the current-state reference; this log
  section (part 7 below) has the blow-by-blow.
- **Critical correctness fix: struck characters were never mirrored.** A
  struck type element must carry a mirror image of the printed glyph
  (same reason a stamp/slug is cut reversed) - v2's `TwoDText` does this
  (`mirror([1,0,0])`), v4 never did until this session. Fixed in
  `build_glyph()`; also resolved the previously-reported "x offset wrong
  direction" bug as a side effect (same missing mirror). See README's
  "Character mirroring" section.
- **Shaft Gauge Test ported from v2** (`GaugeTestSet` and its whole
  supporting cast) - a standalone calibration print for finding
  `element.core_id_offset`, plus its own Gauge config section and tuner
  tab. See README's "Shaft Gauge Test" section.
- **Draft angle is now config-driven** (`build.draft_angle_deg`, default
  55 - the real machine value) instead of a fixed `glyph_poc.py` constant.
  Exposed on tune.py's Font & Alignment tab.
- Everything from the previous session (the real-Minkowski-sum draft
  rewrite, the real platen cutout, the facet-count/preview config
  expansion) is unchanged and still the current mechanism - see "Where
  things stood" below (renamed from "right now") and parts 1-6 for that
  history.

## Where things stood at the end of the previous session

- **Branch at the time: `v2-refactor`.** The draft taper mechanism had
  just been completely rewritten: `build_glyph` in `lib/glyph_poc.py`
  builds it via a real Minkowski sum (`manifold3d.Manifold.
  minkowski_sum`), replacing the per-vertex outline-offset approach (and
  its self-union patch, added and then removed again that same session -
  see below) entirely. That old code is gone, not kept behind a flag.
- Every character that was broken at any point that session - `H`, `e`,
  `m`, `^`, `M`, `A`, `i`, `o`, `0` - was confirmed clean: watertight,
  winding-consistent, `is_volume=True`, no self-intersection possible by
  construction, correct platen scallop on both curvy and straight-stroke
  letters.
- **Real cost accepted: generation time.** A boolean CSG call replaces
  plain coordinate math. ~60-70s for the full 84-character ring + assembly
  at the config's default quality (`points_per_mm=15`, `cone_segments=16`),
  ~16-35s at faster settings (`--points-per-mm 8 --cone-segments 12` or
  lower) with only minor visual quality loss - see README's "Performance"
  section.
- **Known-accepted, still open, unrelated to the draft mechanism:** 61
  inter-character collisions at `separation_mm=2.0` (confirmed real via
  direct boolean intersection, sitting at the embedded root end - not
  visible from outside), and the `HollowSpace` margin flag (flickers
  `True`/`False` run to run from floating-point noise at a razor-thin
  boundary - documented, not new).
- **`separation_mm=1.0` still NOT reapplied.** Earlier in that session it
  was found to eliminate the inter-character collisions entirely (at the
  cost of less embedding-depth margin) - undone by the full revert (see
  "The detour" below) and never reintroduced. Config still has
  `separation_mm=2.0`, still 61 collisions. `logo.radial_offset_mm` WAS
  reapplied (see part 6 below), but at the real v2 value (1.5), not the
  earlier session's tuned value for the now-reverted `separation_mm=2.0`
  near-miss investigation - re-check if that near-miss matters again.
- **Real platen cutout + facet-count/preview config expansion (part 6,
  most recent work) landed on top of all of the above** - see that
  section for the current state of `quality.*`/`logo.radial_offset_mm`/
  `build.minkowski_enabled`.

## 1. Started from last session's resume point: the naive-offset baseline

Picked up with the per-vertex draft offset (`make_back`/
`orthogonal_offset_vertex`/`join_front_back`) still in its accepted,
detection-only state (self-intersection on tight glyphs, not repaired).
Investigated a visible artifact on the ring: the `H` self-intersecting
fold, first suspected to be caused by `LogoText`'s "Leonard Chau 2025"
engraving crossing the DHIATENSOR `k`/`K`/`_` column (a real, separate,
near-miss - the logo character `a` in "Leonard" landed within 0.17deg of
that column's angle, only 0.37mm of Z clearance) - fixed by adding a
`logo.radial_offset_mm` knob and re-sweeping it against both the character
band and `SpeedHoles` clearance.

But the fold on `H`/`k`/`K` turned out to be a separate, pre-existing
issue: the same self-intersecting-draft-offset limitation documented in
`README.md`, just grown large enough to be visually obvious once
`DEFAULT_SEPARATION_MM` had been bumped from the real 0.5mm to 2.0mm in an
earlier session (for embedding-depth margin - see the code comment history
for why). Swept `separation_mm` from 0.5 to 2.0 and confirmed the fold's
*magnitude* scales with it (expansion width = `separation_mm *
tan(27.5deg)`), even though the underlying self-intersection is present at
every value tested, even the real 0.5mm.

This led to checking the actual physical tradeoff directly:
`embedding_depth_mm = separation_mm - Char_Protrusion` - at the real
0.5mm value, the character root lands EXACTLY on the main cylinder's own
surface radius, zero embedding. Confirmed the self-intersecting fold
becomes visually obvious somewhere between `separation_mm=0.6` and `0.7`.

## 2. Gated self-union repair - implemented, then found to be unsafe

Implemented a loop-type-aware self-union repair in `build_glyph`:
classify each outline loop as outer-island vs. hole using the *un-offset
front loop's* signed area (a severely self-intersecting hole, like `e`'s,
can flip its own post-offset signed area, so classification has to happen
before the offset is applied) - self-union only when every non-simple loop
is an outer island, never a hole (confirmed earlier: self-union caps a
hole with a spurious flat membrane instead of fixing it). This cut
unresolved self-intersection from 71/84 to 11/84 at `separation_mm=0.5`.

User found this had NOT actually fixed everything - `^` still showed a
visible artifact. Investigation found the real problem: `manifold3d`'s
`mesh.union(mesh)` on a MULTI-ISLAND glyph (a disjoint dot separate from
its stem - `i`, `j`, `;`, `?`) doesn't reliably keep the islands separate;
it can weld them together and lose real volume (confirmed on `i`:
12.47+3.25=15.72mm3 of real islands before repair, only 10.85mm3 survived
after, replaced by zero-volume debris). Also found manifold3d's boolean
routinely produces dozens of disconnected zero-volume debris slivers even
on genuinely single-island repairs (36/48 repaired characters, up to 94
slivers on `8`) - harmless to `watertight`/`is_volume` checks but real
debris in the final STL.

Fixed both: gated self-union to single-island glyphs only (multi-island
non-simple glyphs, 4/84, stay detection-only), and stripped near-zero-
volume components after any self-union. Net result at that point: 44
auto-repaired, 27 genuinely unrepaired (down from 71 broken originally).

## 3. The detour: "completely reapproach this at a different angle"

Tried `separation_mm=2.0` (the original, most-broken setting) with the
gated self-union repair active - 48 auto-repaired, 23 still unrepaired,
watertight throughout. But then `m` still showed a visible fold even with
the repair in place, and the user called for a full stop: "characters
still fucking up... undo all measures we did." Reverted `config/
blickensderfer.yaml`, `lib/blickensderfer.py`, `lib/glyph_poc.py` to the
last commit (`67ea8d4`) - back to the naive-offset baseline, detection-
only, no self-union, none of the separation/logo-radius tuning above.

Discussed real alternatives instead of continuing to patch the per-vertex
technique: (1) resume the unfinished `shapely.buffer()`-based lofted taper
on the (still-preserved) `v4-real-offset` branch, or (2) check whether a
REAL Minkowski sum via `manifold3d` (which this whole project originally
avoided for performance reasons) is viable now. Checked - `manifold3d`
exposes `Manifold.minkowski_sum`/`Manifold.cylinder` directly. Prototyped
it on `H`/`e`/`m`/`o`/`i`/`^` (the hardest failures): all watertight,
winding-consistent, `is_volume=True`, zero self-intersection by
construction - including `e` and `m`, which nothing in the naive-offset
line of work had ever fully resolved. Measured cost: ~16-66s for the full
ring depending on quality settings, vs. ~3-6s before. Decided to build
this in as the real replacement.

## 4. Building the real Minkowski-sum draft mechanism

Rewrote `build_glyph` in `lib/glyph_poc.py`: extrude the flat glyph into a
thin prism, `Manifold.cylinder()` for the draft cone, `minkowski_sum()`,
convert back to `trimesh`. Removed the now-dead `back_loops_are_simple`/
`classify_back_loops`/self-union machinery entirely (kept `make_back`/
`orthogonal_offset_vertex`/`join_front_back`/`make_front`, since
`build_flat_text` - `LogoText`'s flat-engrave pipeline - still uses them
with zero offset, which never had a self-intersection problem). Wired a
new `cone_segments` knob through `TextRing`/`Additive`/`FullElement`/
`ResinPrint`/`generate.py`/the config, alongside `points_per_mm`. Updated
`TextRing`'s reporting to drop the now-impossible self-intersection
checks, keeping only inter-character collision detection (a genuinely
separate, placement-driven issue).

Found and fixed three real, separate bugs while building this, in order:

**Bug 1 - doubled depth.** First version extruded the prism to the full
`separation_mm` height AND gave the cone its own full `separation_mm`
height. Minkowski sum ADDS extents in each dimension, so the result came
out `[0, 2*separation_mm]`, not `[0, separation_mm]` (confirmed: `H`'s
z-range was `[0, 4.0]` at `separation_mm=2.0`). Fixed by shrinking the
prism to a thin sliver (`tip_h`, ~0.01mm) sitting at the tip end, letting
the cone alone carry (almost) the full depth.

**Bug 2 - cone origin/dilation direction reversed.** User caught this:
"the minkowski cone shape origin is wrong, the origin should be at the
tip." `manifold3d`'s `cylinder()` places its local origin at the
`radius_low` end - the first fix attempt flipped `radius_low`/
`radius_high` AND translated, which canceled out and put the dilation
back at the TIP instead of the root (confirmed directly: tip came out
wider than root, exactly backwards - `watertight`/`is_volume` don't catch
a reversed-but-still-valid draft, only checking cross-section width at
`z=0` vs. `z=separation_mm` does). Fixed by keeping the cone's original
wide-at-bottom/apex-at-top construction and only translating the whole
cone by `-cone_height`, landing the apex exactly at the origin. Verified:
root width minus tip width = exactly `2*expansion_width_mm`.

**Bug 3 - manifold3d's raw triangulation noise.** User spotted "facet
angles are inconsistent... like a poorly done minkowski" on straight
edges (`M`'s strokes). Confirmed: a single straight wall came out as ~24
near-coplanar micro-triangles with normals wobbling by a fraction of a
degree - real CSG-algorithm noise, not a geometry error (face-normal
check on the wall showed the wobble directly; `Manifold.simplify()`
collapsed 2918 triangles down to 182 at even 0.0005mm tolerance, into a
single flat face per straight run). Added `simplify_tolerance_mm` (default
0.005mm, config + CLI knob) applied to the `minkowski_sum` result.

User also asked whether reducing the prism's height ("just do a slice of
the curved part") would speed up the Minkowski call. Tested directly:
face count (and timing) is unaffected by `tip_h` - a straight extrusion's
face count depends on its 2D cross-section, not its Z-thickness. The real
cost driver is `points_per_mm` (already exposed), and the cap
triangulation is already minimal (`triangle_args='p'`, no added Steiner
points) - no free win available there.

## 5. Bug 4 - platen curve applied in the wrong order

User: "are you doing minkowski first, then adjusting the top surface for
platen curvature? ... the draft angle loses angle spec after adjustment."
Correct diagnosis. The version at that point warped only the SWEPT
RESULT's top ring into the platen parabola, after the Minkowski sum -
meaning the cone's own geometry (and therefore the realized draft angle)
was only ever valid for a flat tip; nudging just the final ring left the
walls built as if the tip were still flat. Visible specifically on
horizontal runs far from `radius_y_offset` (the platen's tangent point) -
`M`/`A`'s bottoms, not `L`/`I`'s mostly-vertical runs which stay close to
it. Confirmed this also matches how the real `v2/lib/glyph_pipeline.scad`
avoids the problem: `PlatenCutout()` is subtracted from the base
extrusion BEFORE the `minkowski()` call there, never patched onto the
result after.

Fixed by moving the platen Z-warp to the PRISM's top cap, before the
Minkowski sum, instead of the swept result's top ring after. Verified
numerically (root width minus tip width still exactly
`2*expansion_width_mm` - the warp doesn't disturb the dilation amount)
and visually (`M`/`A`'s bottoms now match `L`/`I`'s clean quality, no
faceting).

Also had to re-verify the earlier `simplify()`-before-warp ordering bug
from step 4 didn't reappear: `simplify()` must run on the CURVED result
now (after the prism warp + Minkowski sum), not on a still-flat
intermediate, or it aggressively over-collapses large flat regions before
they're curved (confirmed: straight-stroke letters lost platen-curve
fidelity while curvy letters looked fine only because their outline's own
curve-driven vertex density happened to survive). Final order per
character: warp prism top cap -> Minkowski sum -> simplify.

## 5.5. Checkpoint, then a real assembly bug found by inspection

Committed and pushed the Minkowski rewrite (README/SESSION_LOG rewritten
to match). Then, from exporting every character to its own STL for visual
inspection (`export_glyphs.py`, new this round - real per-row config
values, not generic defaults, so what you see matches the actual
element), user noticed no clean edge forms where a character meets the
main cylinder in their viewer.

Root cause: `TextRing()`/`Additive()` were the only two assembly functions
in `lib/blickensderfer.py` using `trimesh.util.concatenate()` to combine
parts - everything else (`Subtractive`, `SpeedHoles`, `DrivePin`,
`ResinSupport`, ...) already used `sp.union_all()` (a real `manifold3d`
boolean). `concatenate()` just merges vertex/face arrays with zero
boolean resolution, so wherever a character's embedded root overlapped
the main `Cylinder()` (by design - that's what "embedded" means) or two
characters overlapped each other (61 confirmed pairs), both surfaces
stayed fully intact and superimposed - no new edge formed at the actual
intersection. Confirmed via volume: concatenating measured 1148mm3 MORE
than a real union of the same parts (the double-counted overlap).

Fixed both call sites to use `sp.union_all()`. Also switched
`union_all()`'s own implementation from a sequential `trimesh.union()`
fold to `manifold3d`'s native `Manifold.batch_boolean()` - ~30x faster on
the real 86-part case (2.43s -> 0.08s, identical volume), since the fix
now unions far more parts than `union_all`'s original ~12-part use cases.
Committed and pushed separately from the Minkowski rewrite.

## 6. Real platen cutout + facet-count/preview config expansion

User: "the parabola should be a cylinder like blickensderfer" - confirmed
the platen mechanism was still taking the flat glyph's top-face vertices
and moving each one's Z by the small-angle-approximation formula (a
vertex nudge, not a real swept surface), and asked for the real thing.
Also asked for several new config knobs: `logo.radial_offset_mm` back
(reverted in "the detour", never reapplied), a `minkowski_enabled`
toggle for fast previews, and separate facet-count (`_fn`) knobs per
surface family instead of the existing `surface_fn` catch-all - clarified
in conversation: inner shaft (`cyl_fn`, unchanged) and outer cosmetic
body should be SEPARATE knobs (not merged), both may be set to 360; the
platen cutout needs its own `platen_fn` once it's a real cylinder.

**Real platen cutout**: `platen_radius_mm` (the existing small-angle
approximation coefficient, `1/(2*Rp)`) is inverted to recover the real
platen radius `Rp` - no new parameter needed. Built as an actual
`Manifold.cylinder()` (axis along X via `.rotate([0,90,0])`, tangent to
the tip plane at `y=radius_y_offset`), boolean-subtracted
(`Manifold.__sub__`) from the glyph block BEFORE the Minkowski sum - same
ordering lesson as part 5, just with a real cylinder instead of a warp
now. Verified the construction directly (cylinder bounds/tangent-point
sampled and checked against the exact circle formula, then a synthetic
carved-block test checked point-by-point against `z = sep + Rp -
sqrt(Rp^2-(y-off)^2)`) before wiring it into `build_glyph` - a synthetic
test with too-small margin caught a real design requirement along the
way: the block must be tall enough, PER GLYPH, that the cylinder reaches
every Y this specific glyph spans, or the corners farthest from
`radius_y_offset` survive uncut (still flat) instead of following the
real curve. Margin is now computed per-glyph from the exact bulge formula
(`Rp - sqrt(Rp^2 - dy_max^2)`), not a fixed guess.

Confirmed the real cylinder's own axis position/radius depend only on
`radius_y_offset`/`Rp` - both per-ROW constants - so it's identical for
every character in a row by construction, addressing a design question
raised mid-session about keeping node/curve consistency across a row
without needing to explicitly force it.

Verified: `z_max` values match the old parabola approximation to within
0.0006mm (expected - the parabola IS that circle's small-angle
approximation), same watertight/`is_volume`/volume figures as before,
visually clean on `H`/`M`/`A`/`e` (the platen-order failure cases from
part 5). Per-character timing actually improved slightly (no more
per-vertex Python loop).

**`minkowski_enabled` toggle**: when `false`, `build_glyph` skips the
Minkowski sweep entirely and returns the scalloped-but-undrafted block -
correct platen curve and placement, no taper. Full ring + assembly in
~3s vs. ~22-70s depending on quality settings - verified end-to-end via
`generate.py --no-minkowski`.

**Facet-count reorganization** (`quality:` in the config): added `body_fn`
(main visible cylinder body - `Cylinder`/`ClipCylinder`, was incorrectly
sharing `surface_fn` with unrelated detail surfaces), `platen_fn` (the
new real cutout cylinder), and renamed the Minkowski cone's segment count
from `build.cone_segments` to `quality.minkowski_fn` (grouped with the
other four `_fn` knobs now) - old `build.cone_segments` key still works
as a fallback for configs that haven't been updated. `cyl_fn` (inner
shaft/core) and `surface_fn` (other structural detail) are unchanged.

**`logo.radial_offset_mm` reapplied** at the real v2 value (1.5mm) - NOT
the earlier session's tuned value (which was specific to the
now-reverted `separation_mm=2.0` near-miss investigation in part 1). Real
value confirmed via the config comment to still land within ~0.4mm of a
DHIATENSOR column at this exact text/spacing - not currently an issue,
worth re-checking if either changes.

## 7. Building `tune.py`, an interactive config TUI (new session, branch `v4-tui`)

Started from a request to stop hand-editing YAML between test renders.
Built `tune.py` (`textual`) incrementally, tab by tab, fixing real bugs
found along the way:

**Core structure.** A generic `SECTIONS`/`FIELDS` table drives most tabs
(`(yaml_key, [path, into, cfg], type, label, help_text)` tuples), so most
new config fields only need one table entry to get compose/collect/
save/reload behavior for free - used for the later Gauge and draft-angle
additions. A few tabs (Layout, Build, Type Test) are bespoke since they
need dropdowns/switches/multi-line text rather than plain fields.

**Config tiers.** Editing the master YAML directly risked losing the
"known-good, matches v2" reference file to exploratory tuning. Built a
three-tier scheme instead: master is read-only from the TUI's
perspective; all edits/saves go to a gitignored `*.running.yaml` scratch
copy, auto-created and auto-migrated (`_migrate_running_config` backfills
missing top-level AND nested keys from master into a stale running copy
without touching customizations) on load; an explicit Save writes the
running copy out to wherever you choose via a real file browser
(`textual-fspicker`'s `FileSave`/`FileOpen`, added after a plain
`Input`-based path field proved error-prone for font paths especially).

**Workflow buttons and f3d integration.** Iterated through several designs
for "how do I see what I just changed": an initial manual "launch f3d"
button, then auto-launch/raise on Render (`_ensure_f3d_after_build()` -
starts f3d fresh if not running, or `wmctrl -a f3d` to raise an existing
window), then a dedicated Top View camera for text preview specifically
(`f3d_top_view_cmds.txt`'s `set_camera top`, via f3d's `--command-script`
flag - found by `strings`-ing `libf3d.so` for camera-related command
names after a hand-derived `--camera-direction=0,0,-1` guess came out
rotated 90° wrong, confirmed by direct user testing) plus
`--camera-orthographic`. f3d is killed on quit/terminal-close so it
doesn't accumulate zombie windows across tuning sessions.

**Type Test tab.** A flat, non-cylindrical CPI/LPI-spaced text preview
(`type_test.py`) for instant font/legibility iteration, independent of
the real element pipeline - persists its own text/CPI/LPI to
`type_test:` in the config. Later given the same modified-left/right
alignment handling as the real `TextRing`, so what you see here actually
matches final placement.

**Bug: quit didn't save.** Plain `q` never fires while any Input/TextArea
has focus (Textual consumes it as literal typed text, not a binding) -
easy to hit by accident after typing in a field and hitting `q` out of
habit. Fixed by adding `ctrl+q` as a second, reliable binding (needed
`loop.add_signal_handler`, not plain `signal.signal()` - the latter was
found to leave signals unfired for seconds while the event loop is
blocked) and having both quit paths save first (`_save_before_exit`).

**Bug: `Select.BLANK` crashes on mount.** In the installed `textual`
version, `Select.BLANK` is aliased to the plain boolean `False`, not the
real "no selection" sentinel (`Select.NULL`) - using it as a value
crashes `Select`'s own mount-time validation. All usages (Layout tab's
preset dropdown) fixed to `Select.NULL`. Discovered while testing the
Gauge tab, only surfaced once the real config's `layout.rows` first
became genuinely "custom" (non-matching any preset).

**Layout tab: preset editor with a live read-only preview + unlock.** A
dropdown of presets (QWERTY, DHIATENSOR, ...), 3 read-only rows previewing
whichever preset is currently selected, and a "Modify glyphs" switch that
reveals 3 editable rows (seeded from whichever preset was showing when
unlocked) whose hand-edited content is what actually gets saved to
`layout.rows` - not the preset dropdown's value - whenever the switch is
on (`layout.modify_glyphs: true` in the config, matching how the running
config already looked from earlier hand-editing).

**Bug: Layout tab's read-only preview stopped updating on dropdown
change.** Root cause: the preview-row helper
(`_display_rows_for_preset()`) derived "the current preset" from
`self.cfg` (disk state, only refreshed on save/reload), not the
dropdown's own live in-widget value - so browsing the dropdown without
saving left the preview frozen on whatever was last saved. Fixed by
adding a second helper, `_rows_for_layout_select_value(value)`, that
takes the live value directly and is used by both `on_select_changed`
(browsing) and `on_switch_changed` (seeding the editable rows on unlock)
instead of the disk-state-based one - `_display_rows_for_preset()` itself
is unchanged and still correct for its own remaining callers
(`compose()`/`_refresh_widgets_from_cfg()`, where `self.cfg` and the
dropdown are legitimately in sync). Verified via direct headless tests; a
first test run gave a false negative from a `True -> True` no-op Switch
reassignment (the real config already had `modify_glyphs: true`), which
looked like the fix hadn't worked until re-tested with a genuine
`False -> True` transition.

**Build tab: iterated to a dropdown + independent checkbox.** First pass
was a 3-option dropdown (Element Only / Element Resin Print / Shaft
Gauge, `build.target` string) added alongside the new Gauge tab port
(next item). Simplified per direct feedback to a 2-option dropdown
(Element / Shaft Gauge) plus a separate "Resin supports" checkbox,
independent of which target is selected - Element uses the checkbox to
choose `FullElement()` vs `ResinPrint()`; Shaft Gauge always builds with
its own resin supports built in regardless of the checkbox, since a gauge
print can't stand on its own. `_refresh_widgets_from_cfg` maps any stale
`target: "resin"` value (from the first-pass 3-option version) back to
`"element"` for backward compatibility with configs saved during that
window.

**Gauge tab: ported v2's `[Shaft Gauge Test]` feature.** `GaugeTestSet`
and its supporting module (`CylinderGauge`, `GaugeResinSupport`,
`GaugeResinSupportsRaft`, `RevolverSolid`, `GaugeText`,
`GaugeTestSubtractive`) added to `lib/blickensderfer.py`, ported closely
from `blickensderfer.scad`. `RevolverSolid()` (hull of the 6 gauge-pocket
cylinders) uses `trimesh.util.concatenate(...).convex_hull`, matching the
existing `CoreEllipses()` pattern, since trimesh has no hull-of-solids
primitive. Found and fixed a real porting bug: `GaugeText()`'s
`sp.scad_transform` had rotate/translate in the wrong order relative to
v2's source (`translate() rotate([0,90,0])`, translate outermost) -
caught because the text mesh's own Z-center bounds came out at ~-2.57
instead of the expected 11.325; fixed by reordering to
`("translate", [...]), ("rotate", [0, 90, 0])`. New tuner tab added with
`Gauge_Offset_Start`/`Gauge_Offset_Int` fields and an explanatory banner
about the calibration workflow (print, test-fit each numbered pocket on
the real machine, set `core_id_offset` to whichever fits).
Tab order was also changed to Font & Alignment, Type Test, Resin,
**Gauge**, Build, Layout, Quality, Logo, Element per direct request.

**Progress output during Render.** `generate.py`'s stdout is piped (not a
TTY) when run as a subprocess from `tune.py`'s Render button, so Python
defaults to full block buffering - without explicit `flush=True`,
progress wouldn't appear live in the TUI's log pane at all until the
whole process finished. Added `flush=True` throughout the pipeline's
prints, plus new per-character progress lines in `TextRing()`
(`"TextRing: [n/total] building 'x' (row R, col C)... 0.42s"`) so a ~60s
render shows visible incremental progress instead of a long silent pause.

**Critical fix: struck characters were never mirrored.** User noticed
printed characters were coming out backwards. Root cause: v2's
`TwoDText` wraps every struck glyph in `mirror([1,0,0])` (a struck type
element must carry a mirror image of the printed glyph, the same reason
a rubber stamp or hot-metal slug is cut in reverse) - `build_glyph()`
never did this. Fixed by negating X on the already-shifted contours,
applied AFTER `x_shift` (matching v2's translate-then-mirror order):
`contours_mm = [c * np.array([-1.0, 1.0]) for c in contours_mm]`. This
also mathematically resolved the previously-reported "x offset applied in
the wrong direction" bug as a side effect (verified:
`printed_x = -(-(x_local + x_shift)) = x_local + x_shift`, matching Type
Test's already-correct convention) - both bugs were the same missing
mirror. Deliberately scoped to `build_glyph()` (struck characters) only -
`build_flat_text()` (`LogoText`, Type Test) is untouched, since that text
is read directly and must never be mirrored.

**Draft angle made configurable.** `glyph_poc.py`'s `MINK_DRAFT_ANGLE`/
`DRAFT_HALF_ANGLE_RAD` were fixed module constants with no override.
Added `DEFAULT_DRAFT_ANGLE_DEG` + a `draft_angle_deg` parameter to
`build_glyph()`, threaded through `configure()`/`TextRing`/`Additive`/
`FullElement`/`ResinPrint`, a new `build.draft_angle_deg: 55.0` config
field, a `--draft-angle-deg` CLI flag, and a tuner field on Font &
Alignment (right after the modified-left/right offset fields). Verified
via a direct `build_glyph()` comparison (55° vs 30° producing correctly
different, both-watertight geometry), a save round-trip test, and a full
`generate.py` regression run.

**Investigated but found to already be correct:** a report that "Render
Test Text" wasn't persisting past the Font/Type Test tabs turned out to
already work as intended (the button lives outside `TabbedContent` in the
`#buttons` panel, visible from every tab) - likely a stale-process
artifact on the reporting end, not a real bug; left as-is.

**Explored but not yet started: shared-module split + Postal port.**
Research phase complete - an Explore agent compared `postal.scad` against
`blickensderfer.scad` and confirmed Postal is a strict simplification of
the same cylinder-machine family (same `TextRing`/`LetterPlacement`
radial-wrap scheme, same four shared v2 lib includes); the only
code-level (not just parameter-value) divergence found is the
`HollowSpace`/`DrivePin`/`ResinSupport` "drive pin trio" - Blickensderfer
has 2 selectable drive-pin styles plus a countersink, Postal has one
plain rectangular extrude, no countersink. Everything else differs only
in parameter values (many already config-driven in v4). Design sketched
but not validated or implemented: a new `cylinder_machine.py` shared
module that each machine's `configure()` populates via a globals-dict
sync (`cylinder_machine.__dict__.update({k: v for k, v in g.items() if
not k.startswith("__")})`) so shared functions can call
machine-overridden functions (like `HollowSpace`) as ordinary bare
names - directly mirroring OpenSCAD's own dynamic
redefinition-across-includes behavior. Per this project's established
refactor convention (see memory: build new files, don't edit originals
in place), the plan is `cylinder_machine.py` + `postal.py` as new files
alongside `blickensderfer.py`, not edits to it. Not started.

## 8. Shared-module split + Postal port, implemented

Validated the part-7 design via a Plan agent before writing code (see
that agent's report for the full reasoning) - core verdict: the
globals-sync dispatch mechanism is sound (a function's `__globals__` is a
live reference to its defining module's dict, not a snapshot, so
`cylinder_machine.__dict__.update(...)` really does reproduce OpenSCAD's
"last include wins"), with two refinements: filter the sync to
uppercase-leading keys only (`k[:1].isupper()`, avoiding leaking stray
imports like `np`/`trimesh` into `cylinder_machine`'s namespace - plus one
explicit exception, the lowercase epsilon constant `z`, found the hard
way when `ClipCylinder()` immediately `NameError`'d on first test run),
and an `_active_machine` guard against a future script configuring two
machines in one process (not a real risk today - `generate.py`/
`export_glyphs.py` each configure exactly once and exit; `tune.py` never
imports these modules, only shells out to `generate.py`). The validation
pass also caught a second real code-level divergence the original
research had missed: `BottomSlopedSpace()`'s floor-Z literal is `0` in
Blickensderfer, `-z` in Postal (both files' own comment: "to help with z
fighting") - added as a third machine-set global,
`Bottom_Sloped_Space_Floor_Z`.

**Extraction**: moved everything structurally shared (`Cylinder`,
`ClipCylinder`, `TextRing`, `Additive`, `Core`, `SpeedHoles`,
`BottomSlopedSpace`, `TopMinkCleanup`, `WireBite`, `SecondaryCore`,
`CoreGrooves`, `CoreChamfer(Shape)`, `CoreEllipses`, `LogoText`,
`Subtractive`, `FullElement`, the whole resin-support helper family,
`ResinPrint`, the whole Gauge family) into new `lib/cylinder_machine.py`.
`lib/blickensderfer.py` now holds only `configure()` and its own
`HollowSpace`/`DrivePin`/`ResinSupport` (the countersink versions),
re-exporting `FullElement`/`ResinPrint`/`GaugeTestSet` from
`cylinder_machine` so `generate.py`'s existing `bd.FullElement(...)` etc.
calls needed zero changes.

**Regression-verified the extraction didn't change Blickensderfer's
output at all**: ran `generate.py config/blickensderfer.running.yaml
--no-minkowski --no-core-groove` before the refactor (via `git stash`) and
after - byte-identical vertex/face counts, volume, and watertight/
winding/is_volume flags in both the plain-element and `--gauge` build
paths.

**Postal port**: `lib/postal.py` ports v2/postal.scad's `HollowSpace()`
(plain revolve, no countersink at all), `DrivePin()` (a single centered
box, no sink cylinder unioned on - v2's `DrivePin(Offset)` takes an
unused `Offset` param, dropped in the port since nothing calls it with
one), and `ResinSupport()` (no per-style ternary, plain-pin half-extents).
`config/postal.yaml` populated from `v2/postal.scad`'s own values -
`layout.rows` computed programmatically from v2's
`Keyboard_Layout_Array`/`Element_Layout_Array_Map` (`Physical_Layout`,
postal.scad:271-274) rather than hand-transcribed, to avoid a 28-character
transcription error. Two known placeholders flagged in the config's own
comments: font paths (v2's real Postal fonts, "Alma Mono"/"FreeMono:
style=Bold", are system font family names, not `.ttf` file paths v4
needs - reusing Blickensderfer's font files until real replacements are
sourced) and `quality.body_fn` (v2's Postal uses DIFFERENT Fn values for
`Cylinder()` vs `ClipCylinder()` - `Cyl_Fn`/`Surface_Fn` respectively -
but v4's shared `Body_Fn` knob only has one value; set to Postal's
`Cyl_Fn`, making `Cylinder()` exact and `ClipCylinder()` harmlessly
over-faceted).

Added a `machine:` config key (`generate.py`/`export_glyphs.py` peek it
before import, default `"blickensderfer"` for zero-touch backward compat
with existing configs) and dispatch via `importlib.import_module`.

**Verified end-to-end**: `generate.py config/postal.yaml` (plain element,
`--gauge`, and via `export_glyphs.py`) all produce watertight/
winding-consistent/`is_volume` output with no code errors (one character,
'%', skipped for a missing glyph in the placeholder font - expected, not
a bug). Also directly verified the `_active_machine` guard fires
(`RuntimeError`) when a test script configures Blickensderfer then Postal
in the same process.

**Explicitly out of scope for this pass, flagged as follow-up**:
`tune.py` support for Postal - its `SECTIONS` table is hardcoded to
Blickensderfer's exact field set (e.g. the "Element" tab's
`drive_pin_countersink_depth`/`drive_pin_style`/etc, none of which exist
in Postal's schema) and would `KeyError` immediately if pointed at
`config/postal.yaml`. Needs a per-machine `SECTIONS` variant chosen from
the config's `machine:` key - orthogonal UI work, not started. Sourcing
real Postal font files is also a prerequisite content task, not a code
problem.

## Resuming later

1. **`tune.py` support for Postal** - per-machine `SECTIONS`/`FIELDS`
   table needed; see part 8 above.
2. **Source real Postal font files** (currently placeholders reusing
   Blickensderfer's fonts - see `config/postal.yaml`'s comments).
3. **Reapply or re-decide on `separation_mm=1.0`** (see "Where things
   stood" above) - `logo.radial_offset_mm` is back (part 6), but
   `separation_mm` is still the reverted `2.0`, still 61 collisions.
4. **Inter-character collisions** (61 at `separation_mm=2.0`) - no
   automatic fix short of redoing placement/size, or accepting the
   `separation_mm=1.0` tradeoff (verified to eliminate them, at the cost
   of embedding-depth margin).
5. **Performance** - if ~60-70s at full quality becomes annoying,
   `points_per_mm`/`quality.minkowski_fn` are the main levers, or
   `build.minkowski_enabled: false` for a ~3s undrafted preview - all
   wired through config + CLI (`--no-minkowski`).
6. Alignment offsets - the mechanism is built and now in real use (see
   the running config's `modified_left_offset_mm`/
   `modified_right_offset_mm`), but the base `center_offset_mm`/
   `left_offset_mm` knobs are still untouched at their 0.0 defaults.
7. `platen_fn`/`body_fn` are both set to 360 right now (per earlier
   direction, "may both be set at 360") - 720 was floated for `platen_fn`
   if the scallop needs to be smoother; not tested.
8. A "master GUI" to pick which machine (Blickensderfer/Postal/...) to
   tune - now that Postal exists (part 8 above), this is unblocked; still
   waiting on `tune.py`'s own per-machine `SECTIONS` support (item 1
   above) first.
