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

## 9. `tune.py` support for Postal

Closed out part 8's flagged follow-up. Split the module-level `SECTIONS`/
`FIELDS`/`LAYOUT_PRESETS` into `SECTIONS_BY_MACHINE`/`LAYOUT_PRESETS_BY_MACHINE`
(Postal's Element field list drops the 5 drive-pin-countersink keys that
don't exist in its config, everything else shared) and made
`TuneApp.SECTIONS`/`.FIELDS`/`.LAYOUT_PRESETS` instance attributes, fixed
once at startup from the launch config's `machine:` key. All method-level
references updated to `self.SECTIONS`/etc (a bulk regex pass, then fixed
a `self.self.` double-prefix bug the regex introduced on the two lines it
was defining, caught immediately via `grep`).

Deliberately scoped to NOT support hot-swapping between machines within
one running session - `compose()` only builds each tab's widgets once, so
a config for a different machine has a structurally different Element tab
(different KEYS, not just different values) that would need real widget
teardown/rebuild, not just repopulation. Added a guard in
`_switch_master_config` that peeks the target config's `machine:` key and
refuses the switch (clear log message pointing at relaunching directly)
if it doesn't match the machine tune.py was launched for.

Fixed `config/postal.yaml` missing a `type_test:` section (tune.py's Type
Test tab unconditionally reads `self.cfg["type_test"]["text"/"cpi"/"lpi"]`
- crashed on first boot test with a real `KeyError`, not a hypothetical
one). Also fixed a real hardcoded-machine-name bug found in the same
pass: `action_save`'s suggested STL filename was always
`f"blickensderfer_{timestamp}.stl"` regardless of which machine was
actually being tuned - now `f"{self.machine}_{timestamp}.stl"`.

Postal's Layout tab has an empty preset dropdown (v2/postal.scad has only
one physical layout, no preset-switching menu like Blickensderfer's 6) -
confirmed Textual's `Select` tolerates a genuinely empty options list
fine (tested directly, no crash) with `allow_blank=True` and a
machine-aware prompt string ("no named presets for this machine" instead
of "custom - not a known preset").

**Verified via headless `App.run_test()` boot tests** (not just visual
screenshots) against both configs: correct per-machine field counts (73
total/32 Element fields for Blickensderfer, 68/27 for Postal), correct
initial values, a save round-trip on a Postal-only-relevant field
(`drive_pin_radial`), and the cross-machine switch guard actually
refusing (confirmed `app.machine` stays `"postal"` and
`app.master_config_path` stays on `postal.yaml` after attempting to
switch to `blickensderfer.yaml`).

**Investigated the Postal font placeholders**: the user's local font
library DOES have real `Alma Mono.otf` and `FreeMono-Bold.otf` files
(found via `find`) - but checking their outlines directly via FreeType's
point tags confirmed both use CFF/cubic curves, not TrueType/quadratic -
exactly the silent-failure case documented in README's "Known
limitations" (`FreeMono-Bold.otf` was literally named there as the
confirmed example). Flagged this to the user rather than silently wiring
in known-broken fonts or guessing a substitute.

## 10. Cubic-curve (CFF/OpenType) outline support

User asked directly: "wait so my thing is not otf support?" - clarified
that OTF is just a container (can hold either TrueType/quadratic `glyf`
outlines, which already worked, or CFF/cubic outlines, which didn't) and
that the real gap was cubic Bezier support in `contour_to_points`
(`lib/glyph_poc.py`), not anything about the `.otf` extension itself.
User asked for the real fix rather than a font substitute.

**Root cause**: `contour_to_points` only checked FreeType's on-curve bit
(`tag & 1`) - every off-curve point was treated as a lone quadratic
control point via the TrueType "implied midpoint" convention. A CFF
outline's off-curve points come in PAIRS (two consecutive cubic control
points before the next on-curve point) - misreading them as quadratic
produced a plausible-looking but geometrically wrong curve, with no error
raised (the exact bug already documented, now actually understood at the
curve-math level instead of just observed as an OTF/TTF divide).

**Fix**: added `cubic_bezier()` (mirrors the existing `quadratic_bezier()`)
and a second per-point classification, `is_cubic = (tag & 0x3) == 2`
(FreeType's `FT_CURVE_TAG` macro - 0=quadratic off-curve, 1=on-curve,
2=cubic off-curve), checked before falling through to the existing
quadratic path. Cubic spans consume 3 points (this control + the
guaranteed-paired second control + the on-curve endpoint) instead of 1-2.

**Verified in layers**: (1) raw contour extraction against real
`Alma Mono.otf` - every character's contours are valid simple polygons
with sane, character-distinct ink dimensions (e.g. 'e' 1.5x1.53mm, 'M'
1.5x2.1mm, '.' 0.43x0.38mm at 3mm font size - not a degenerate
all-identical artifact); (2) full `build_glyph()` through the real
Minkowski pipeline on both the CFF font and a TrueType font side by side -
both watertight/winding-consistent/`is_volume`, different (correct)
per-character bounds; (3) `generate.py config/blickensderfer.running.yaml`
re-run to confirm the TrueType/quadratic path is completely unaffected -
byte-identical vert/face/volume numbers to before this change; (4) the
full `generate.py config/postal.yaml` pipeline (element and `--gauge`,
both fonts - `Alma Mono.otf` for the element, `FreeMono-Bold.otf` for
`LogoText`/`GaugeText`) end-to-end, watertight/winding-consistent/
`is_volume`, 0 characters skipped (previously 1, on the placeholder
font's missing glyph).

`config/postal.yaml`'s font paths were then switched from the TrueType
placeholders to the real `Alma Mono.otf`/`FreeMono-Bold.otf` files, since
the limitation blocking them is now fixed.

## 11. Machine picker on startup + Postal's QWERTY-only layout

User's explicit request: a machine-picker screen shown on startup
(closing out part 9/resuming-item-6's deferred "master GUI"), plus a
"Change Machine" button on the tuner form's status row that returns to
it, and Postal's Layout tab restricted to a single "QWERTY" preset (its
one real physical layout) instead of the empty dropdown from part 9.

**Considered a full Textual `Screen`-stack rewrite** (separate
`MachineSelectScreen`/`TunerScreen` classes, `push_screen`/
`switch_screen`) and rejected it as far more invasive than needed - nearly
every one of `TuneApp`'s ~40 methods reference `self.query_one(...)`,
and moving compose() to a Screen subclass raises real ambiguity about
whether `self.query_one` on the App still resolves against the active
screen's content (untested assumption, not worth risking on a 1200-line
file). Used Textual's `App.recompose()` instead (confirmed available in
the installed 8.2.8 - removes all mounted children and re-runs
`compose()`): `compose()` now branches on `self.machine is None` (picker)
vs. not (the existing tuner form, extracted unchanged into
`_compose_tuner_ui()`), and switching states is just setting
`self.machine`/calling `_load_machine()` then `await self.recompose()`.
Zero changes needed to any of the ~40 existing action/query methods -
they all still just call `self.query_one(...)`, now finding whichever
widgets the current `compose()` branch actually built.

**`_load_machine(config_path)`**: the master/running config bootstrap +
per-machine `SECTIONS`/`FIELDS`/`LAYOUT_PRESETS` setup that used to be
inline in `__init__` (part 9) is now its own method, callable both from
`__init__` (backward-compat direct CLI launch, `python3 tune.py
config/x.yaml` - still supported, skips the picker) and from the new
`_select_machine(machine_key)` (the picker's button handler). `MACHINES`
(new module dict, `{"blickensderfer": (label, config_path), "postal":
(...)}`) is the picker's source of truth and the only place a future
third machine needs to be registered.

**"Change Machine" button**: saves the current form first (reused
`_save_before_exit()` - same courtesy as quitting, so in-progress edits
aren't silently lost on a machine switch), then `self.machine = None;
await self.recompose()` - which is exactly what shows the picker again.
`_switch_master_config`'s existing cross-machine guard (part 9) is now
pointed at this button in its log message instead of "relaunch tune.py",
since there's now a proper in-app path for that.

**Postal's QWERTY preset**: `LAYOUT_PRESETS_POSTAL = {"QWERTY": [...]}`
(the same 3 rows already computed for `config/postal.yaml` from v2's
`Keyboard_Layout_Array`/`Element_Layout_Array_Map` in part 8 - reused
verbatim, not recomputed) replaces part 9's empty `{}` for Postal in
`LAYOUT_PRESETS_BY_MACHINE`. `_compose_layout_tab`'s help text made
properly machine-aware (checks `self.machine` directly now, not just
"are there any presets") since the old "no presets" branch no longer
applies but the Blickensderfer-specific "Ported from
v2/lib/layouts/blick_layouts.scad" text would have been wrong for
Postal's one preset too.

**Verified via headless `App.run_test()` + `pilot.click()`** (clicking
real buttons, not just calling methods directly): picker shows both
machines on a no-arg launch; clicking Postal recomposes into a
Postal-scoped form with the Layout tab's dropdown correctly
auto-selecting "QWERTY" (matches `config/postal.yaml`'s rows exactly, via
the existing `_current_layout_preset()` match-detection); clicking
"Change Machine" returns to the picker; picking Blickensderfer afterward
correctly rebuilds with its own full field set; direct CLI launch still
skips the picker entirely; a save round-trip works correctly on
freshly-recomposed widgets (confirming `self.inputs` isn't holding stale
references from a previous machine's form). Also confirmed visually via
screenshot (converted SVG->PNG with `convert`) - centered picker layout,
correct status text ("machine: Postal | master: config/postal.yaml"), all
three status-row buttons fit on one row.

## 12. Unified `resin.raft` toggle (was a silent per-machine divergence)

User caught a real issue: Postal's resin support didn't look "damn near
identical" to Blickensderfer's like everything else in the shared module -
Postal was growing one big continuous raft plate. Root cause: v2's two
machines genuinely differ here - Blickensderfer's `CutGroove()` ring sits
right at the wall (`Cut_Groove_Inner_X=0`) and each rod grows its own
small raft (`Resin_Rod_Raft=true`); Postal's `Cut_Groove_Inner_X=-14.9`
pushes the ring's inner profile point all the way to the element's center
axis, forming one continuous plate, and its rods grow no individual raft
of their own (`Resin_Rod_Raft=false`) - this was ported faithfully in
part 8, correctly reproducing each machine's real v2 behavior, but never
surfaced as an intentional *choice* - just two silently-diverging
per-machine config defaults.

User's fix, exactly as specified: a single "Continuous raft" checkbox on
the Resin tab - off (now the default for BOTH machines) = Blickensderfer's
original individual-raft behavior, on = Postal's original continuous-plate
behavior - available for EITHER machine now, not Postal-exclusive.

**Implementation**: added `cylinder_machine.resin_raft_config(
element_diameter, wall_min_thickness, raft_enabled)` - a real shared
function (not per-machine copy-paste) that derives both
`Resin_Rod_Raft`/`Cut_Groove_Inner_X` from the one boolean, called from
both `blickensderfer.py` and `postal.py`'s `configure()`. Removed the raw
`resin.rod_raft`/`resin.cut_groove_inner_x` YAML keys entirely (fully
derived now, not independently settable) and replaced with `resin.raft:
false` in both config files - `config/blickensderfer.yaml` and
`config/postal.yaml`'s `resin:` sections are now identical in shape.
tune.py's Resin tab field table (already shared between machines, part 9)
swapped its `cut_groove_inner_x` float field for a `raft` bool field
(automatic `Switch` widget via the existing generic FIELDS mechanism, no
special-casing needed).

**Verified all 4 combinations** (each machine x both settings) via direct
`generate.py --resin-support` runs: Blickensderfer `raft:false` (default)
reproduces the EXACT pre-change `ResinSupport` vert/face counts
(13648/27196); Postal `raft:true` reproduces Postal's exact pre-change
numbers (15851/31698) - confirming the derivation is mathematically
exact, not just visually similar; Postal `raft:false` (new default) and
Blickensderfer `raft:true` (a combination that never existed in v2) both
produce new, watertight/winding-consistent/`is_volume` geometry. Also
verified the new checkbox in tune.py (`Switch` widget, correct initial
value, save round-trip) via headless `App.run_test()`.

**Self-caught mistake**: an early headless test instantiated `TuneApp`
directly against the user's REAL master config paths (`config/
blickensderfer.yaml`) to check the new checkbox's default value, then
saved during the same test - this went through the real master/running
migration + save path and actually flipped `raft: true` in the user's
live, gitignored `config/blickensderfer.running.yaml` scratch file
(their real working config, with real customizations). Caught immediately
by checking `git status`/grepping the file after the test, fixed by hand
(set `raft: false` back, and removed the now-dead migrated-in
`rod_raft`/`cut_groove_inner_x` lines the same migration had left
behind) - the user's actual settings were otherwise untouched. Lesson for
future headless tests that exercise save paths: use a scratch copy of a
config, not the user's real master/running files, even for read-only-
seeming checks - `TuneApp.__init__` itself performs a real migration
side-effect on the running file as soon as it's constructed.

## 13. Matched Blickensderfer's and Postal's remaining resin values

Follow-up to part 12's `raft` unification - user asked to go further and
match the actual remaining resin VALUES too, not just the raft toggle.
First pass (wrong direction, corrected same turn): changed `config/
blickensderfer.yaml`'s `min_rod_height`/`raft_od`/`raft_thickness`/
`bottom_support_fractions`/`bottom_support_inner_angle_offset` to
Postal's values, on the assumption "match A to B" meant "make A become
B" without a stated target. User corrected immediately: "you made it
match up to postal, i wanted blickensderfer to be the standard" -
Blickensderfer's ORIGINAL v2 values are the standard both machines
unify against, not Postal's. Reverted `config/blickensderfer.yaml` back
to its original v2 numbers (`min_rod_height: 4.0`, `raft_od: 2.0`,
`raft_thickness: 1.0`, `bottom_support_fractions: [0.2]`,
`bottom_support_inner_angle_offset: 0.5`) and instead changed `config/
postal.yaml`'s values to match THOSE. The two files' `resin:` sections
are still byte-identical when parsed (`yaml.safe_load(...)['resin'] ==`
the other's) - just anchored to the opposite machine's original numbers
than the first pass.

Regression-verified both directions against the master config files
directly (not the user's real running copies - see part 12's lesson,
applied both times): fully watertight/winding-consistent/`is_volume` in
both passes. Final state's `ResinSupport` counts: Blickensderfer
13648/27196 (exactly its original pre-any-of-this-session's-changes
number, confirming the revert is exact), Postal 13719/27322 (now close
to Blickensderfer's, small remaining gap expected from the two machines'
different `Element_Diameter`/`Wall_Min_Thickness`/etc, not a bug).

## Resuming later

1. **Reapply or re-decide on `separation_mm=1.0`** (see "Where things
   stood" above) - `logo.radial_offset_mm` is back (part 6), but
   `separation_mm` is still the reverted `2.0`, still 61 collisions.
2. **Inter-character collisions** (61 at `separation_mm=2.0`) - no
   automatic fix short of redoing placement/size, or accepting the
   `separation_mm=1.0` tradeoff (verified to eliminate them, at the cost
   of embedding-depth margin).
3. **Performance** - if ~60-70s at full quality becomes annoying,
   `points_per_mm`/`quality.minkowski_fn` are the main levers, or
   `build.minkowski_enabled: false` for a ~3s undrafted preview - all
   wired through config + CLI (`--no-minkowski`).
4. Alignment offsets - the mechanism is built and now in real use (see
   the running config's `modified_left_offset_mm`/
   `modified_right_offset_mm`), but the base `center_offset_mm`/
   `left_offset_mm` knobs are still untouched at their 0.0 defaults.
5. `platen_fn`/`body_fn` are both set to 360 right now (per earlier
   direction, "may both be set at 360") - 720 was floated for `platen_fn`
   if the scallop needs to be smoother; not tested.

## 14. Roadmap: branch merged to main, next is Calibration then Mignon/Bennett/Helios

`v4-tui` was fast-forward merged into `main` and pushed (40 commits,
clean linear history, no divergence). New branch `v4-models` created off
`main` for the next phase: user's stated order is Mignon next (should
reuse a lot from `cylinder_machine.py`), then Bennett, then Helios (both
also cylinder-machine-family) - but the **Calibration feature** needs to
land FIRST, before diving into more machine ports, since every future
machine will want it too.

**Explicitly NOT started yet** - user is about to run out of credits,
asked for a plan only, will say "start" when ready to resume. This
section is that plan, written here specifically so it survives a
context/credit gap.

### What "Calibration" actually is (traced from v2, not guessed)

`v2/lib/testing.scad` (`testSweepArray(start, interval, count)` - a
trivial linear sweep, `[start + interval*n for n in 0..count-1]`) +
`v2/lib/glyph_pipeline.scad`'s `TextRing()`/`TextRingDebug()` (~line
407-451) implement a real, already-designed mechanism, not something to
invent from scratch:

- `Test_Layout` (bool): every position renders the same `Test_Char`
  instead of the real per-position character.
- `Cutout_Test` / `Baseline_Test` (bool, independent - test one variable
  at a time in practice): when on, adds a PER-COLUMN swept offset
  (`Cutout_Test_Array[col]` / `Baseline_Test_Array[col]`, each a 28-long
  `testSweepArray(start, interval, 28)`) onto that row's platen-cutout or
  character-baseline value - so each of the 28 physical positions around
  the ring gets a DIFFERENT offset of whichever variable is under test.
- Whenever any of the three is on, `TextRingDebug()` echoes one line per
  position: `"character keyboard key 'k' (rendered as 'X') on lowercase
  row at the 7 oclock position with platen cutout at 0.15mm and character
  baseline at 0mm"` - refChar (the real keyboard key physically at that
  slot) vs char (what's actually rendered, `Test_Char` under
  `Test_Layout`) are tracked separately for exactly this reason.
- Blickensderfer/Postal both default `Cutout_Test_Start=0`/
  `Cutout_Test_Int=.05` (Blick) or `.7`/`-.05` (Postal) - `testing.scad`'s
  own comment notes Bennett/Mignon/Helios/Hammond use a fixed literal
  offset array instead of a uniform sweep for this, since they already
  have measured values - not a blocker for v4's first pass (a uniform
  start+interval sweep, matching what the user asked for: "specified
  intervals of adjustment").

### v4 implementation shape (design, not yet built)

- **Shared, not per-machine**: `TextRing`/placement already live in
  `lib/cylinder_machine.py` (see part 8) - a `CalibrationElement()`-style
  function belongs there too, so it's automatically available to
  Mignon/Bennett/Helios the moment they're configured, not something
  reimplemented per machine.
- **Config**: new `calibration:` section (parallel to the existing
  `gauge:` section) - `test_char` (str), `variable` ("baseline" |
  "cutout"), `start` (float), `interval` (float). Both
  `config/blickensderfer.yaml` and `config/postal.yaml` need it added
  (shared schema, like `resin:`/`gauge:` already are).
- **Build dispatch**: extends the existing Build tab pattern (Element /
  Shaft Gauge) with a third option, Calibration - mirrors how Gauge was
  added (part 8's `GaugeTestSet`/`--gauge` precedent): a
  `--calibrate` flag on `generate.py`, a `CalibrationTextRing()` (or a
  `test_layout`/`test_variable` kwarg threaded through the existing
  `TextRing()`) that applies the swept per-column offset and forces
  `Test_Char` everywhere.
- **Console output**: reuse the already-established
  `print(..., flush=True)` pattern (part 7/8) - one line per position,
  same content as v2's `TextRingDebug` echo (keyboard key, row label,
  o'clock position, the actual cutout/baseline value used at that
  position).
- **tune.py**: new "Calibration" tab (test char field, a variable
  dropdown "baseline"/"cutout", start/interval fields) - added to
  `SECTIONS_COMMON` (shared between machines, like Resin/Gauge already
  are) so it's free for every future machine too. Build tab's dropdown
  gains "Calibration" as a third option.
- **Saved `.txt` mapping**: user's explicit ask - "when saving a test
  element, it also outputs a .txt of the keyboard mapping to set
  variable." `action_save()` (tune.py) already writes an STL + a `.yaml`
  sidecar per save (see the module docstring's Save explanation) - add a
  third sidecar, a `.txt` with the same per-position lines the console
  already printed, when `self._last_build_info["kind"] == "calibration"`
  (mirrors the existing `_last_build_info` tracking used for the STL/YAML
  metadata header).
- **No new "reference layout" abstraction needed** - v2's
  `Reference_Physical_Layout` (a keyboard-key-labels-vs-content-layout
  split, used by Blickensderfer/Bennett/Mignon for language/layout
  testing) has no v4 equivalent yet and isn't needed for a first pass -
  the "keyboard key at this position" in the console/`.txt` output can
  just be whatever `layout.rows`/`DHIATENSOR` currently has configured at
  that row/col (same source TextRing already reads), matching what
  Postal/Helios/Hammond do in v2 anyway (no reference override - refChar
  == char's position source).

### After Calibration lands

Mignon, then Bennett, then Helios, each following the extraction
playbook already proven twice (part 8's Blickensderfer/Postal split,
part 9's tune.py per-machine SECTIONS, part 12/13's shared resin
config) - read the real v2 file, diff it against `cylinder_machine.py`'s
existing shared functions to find genuine code-level divergences (not
just parameter values, per part 8's methodology), port only the
machine-specific pieces, add `config/<machine>.yaml`, regression-verify
against the master configs directly (not the user's running copies - see
part 12's lesson).

## 15. Calibration feature implemented (per part 14's plan)

User said "start plan" - implemented part 14's design as written, no
deviations from the mechanism (v2's `Cutout_Test`/`Baseline_Test`/
`Test_Layout` traced through `lib/testing.scad` + `lib/glyph_pipeline.
scad`'s `TextRing`/`TextRingDebug`).

**`lib/cylinder_machine.py`** (shared, per part 14's reasoning - free for
Mignon/Bennett/Helios later): `place_on_cylinder()` gained an optional
`baseline_mm=None` param (overrides `BASELINE_ROW[row]` when calibrating
that variable; `None`, every other caller, preserves the exact prior
behavior - zero risk to the real element path). New
`CalibrationTextRing()`/`CalibrationAdditive()`/`CalibrationElement()`
(mirroring `TextRing`/`Additive`/`FullElement`'s structure exactly) sweep
`start + interval*col` onto either `Cutout_Row[row]` or `Baseline_Row[row]`
per physical column, force `calibration.test_char` everywhere, and print
one line per position - keyboard key, o'clock-equivalent, and the exact
cutout/baseline values used.

**One deliberate deviation from v2, explained in both the code comment
and README**: the position label uses the REAL physical placement angle
(`PLACEMENT_MAP[col]` * `LATITUDE_INT`, matching `place_on_cylinder`'s own
angle formula) instead of v2's raw content-order `col`. Traced why: v2's
`TextRingDebug` computes o'clock from the loop's raw `col` (content-order
index into `Physical_Layout`), which only equals the true physical
position for machines with an IDENTITY `Placement_Map` (Postal - "no
Placement_Map override... the lib defaults Placement_Map to identity").
Blickensderfer's real `placement_map` is NOT identity
(`[13,12,11,...]`), so porting v2's formula literally would have
mislabeled every position for Blickensderfer specifically - decided this
was worth deviating on (with the reasoning documented) rather than
faithfully reproducing what looks like a latent v2 quirk.

**Config**: new `calibration:` section (`test_char: "X"`,
`variable: "cutout"`, `start: 0.0`, `interval: 0.05`) added to both
`config/blickensderfer.yaml` and `config/postal.yaml` identically (shared
schema, matching `gauge:`/`resin:`).

**`generate.py`**: `--calibrate` flag (+ `--calibration-char`/
`-variable`/`-start`/`-interval` overrides), mirrors `--gauge`'s
early-return structure. Writes the STL, then a `<stem>_mapping.txt`
sidecar with the same per-position lines the console printed - the
user's explicit ask ("when saving a test element, it also outputs a .txt
of the keyboard mapping").

**`tune.py`**: new shared "Calibration" tab (`test_char` input,
`variable` dropdown - added as a second special-cased Select alongside
the existing `mode` one, `start`/`interval` inputs), Build tab dropdown
gained a third "Calibration" option, `_run_build` dispatches `--calibrate`
(Minkowski forced the same way as a normal element build, since
Calibration DOES go through the real draft/placement pipeline unlike
Gauge). `action_save` now copies the `_mapping.txt` sidecar alongside the
saved STL too, gated on `self._last_build_info.get("target") ==
"calibration"` (reusing the existing `_last_build_info` tracking, same
pattern as the `.yaml` metadata sidecar).

**Verified thoroughly, at every layer**: direct `generate.py --calibrate`
on both machines (Blickensderfer default cutout-sweep AND Postal with
`--calibration-variable baseline`) - all 84 positions built, fully
watertight/winding-consistent/`is_volume`, `.txt` sidecar content spot-
checked (clean, correctly formatted, matches console output exactly).
Headless `tune.py` tests against SCRATCH COPIES of the configs (not the
user's real master/running files - part 12's lesson applied from the
start this time): Calibration tab fields/values, Build dropdown's third
option, a full save round-trip, AND the complete `_run_build` worker path
(real subprocess `generate.py` invocation via the Preview button) -
confirmed the STL and mapping `.txt` both get written and
`_last_build_info["target"] == "calibration"` is set correctly for
`action_save`'s new logic to key off.

## Resuming later

1. **Mignon, then Bennett, then Helios** - see part 14's extraction
   playbook. Calibration (this part) is done, so all three get it for
   free via `cylinder_machine.py`.
2. Everything in part 14's own original "Resuming later" list (the
   pre-existing backlog: `separation_mm`, inter-character collisions,
   performance, alignment offsets, `platen_fn`/`body_fn`) is still
   open - unrelated to Calibration, not touched this pass.

## 16. Two Calibration follow-up fixes from real usage

**Bug: Calibration Element ignored `--minkowski`/`--no-minkowski`.**
User: "right now, pressing preview renders it with minkowski." Root
cause: `generate.py`'s `--calibrate` branch parsed
`--minkowski`/`--no-minkowski` (and every other build-quality flag -
`--points-per-mm`/`--separation-mm`/`--cone-segments`/
`--simplify-tolerance-mm`/`--platen-fn`/`--draft-angle-deg`) but never
actually passed any of them to `CalibrationElement()` - so tune.py's
Preview button (which sends `--no-minkowski`) had zero effect; every
calibration build silently used the config's default (minkowski on),
the same ~36s path as Render regardless of which button was pressed.
Fixed by threading all of them through, matching the normal
`build_fn(...)` call exactly. Confirmed: `--no-minkowski` now takes
~1.4s (was ~36s regardless of the flag before the fix) - verified both
via direct CLI timing AND through `tune.py`'s actual `_run_build` worker
path (a real subprocess call, not just unit-testing the arg parsing).
Also renamed the Build tab's "Calibration" dropdown option to
"Calibration Element" (all UI text/docstrings quoting the old label
updated to match).

**Redesign: `calibration.variable` (single baseline-or-cutout choice)
replaced with two independent checkboxes.** User: "have checkboxes for
vary baselines, and vary cutouts. usually youll only have 1 checked at a
time." This is actually a MORE faithful port of v2 than the original
single-choice design - v2's `Cutout_Test`/`Baseline_Test` really are two
separate booleans (confirmed by re-reading part 14's own research), not
a single enum; the original single-`variable` implementation was an
unnecessary simplification. Replaced `calibration.variable: "cutout"`
with `calibration.vary_baseline: false`/`vary_cutout: true` (same net
default) in both config files, in `CalibrationTextRing`/`Additive`/
`Element`'s signatures (`vary_baseline`/`vary_cutout` bools instead of a
`variable` string), in both machines' `configure()`, and in
`generate.py`'s CLI (`--calibration-vary-baseline`/
`--calibration-no-vary-baseline` + the `-cutout` pair, mirroring the
`--minkowski`/`--no-minkowski` tri-state pattern). tune.py's Calibration
tab: the `variable` field's Select special-case removed entirely (two
plain `bool` fields get `Switch` widgets automatically via the existing
generic FIELDS mechanism - no special-casing needed, simpler than what
it replaced). Both CAN be checked together (moves baseline and cutout by
the same shared offset simultaneously) or both off (no sweep, every
position identical) - not just the "usually 1" case, though that's still
the expected normal usage the user described.

Verified all four on/off combinations (default cutout-only, baseline-only
override, both-on, both-off) via direct `generate.py --calibrate` runs -
all watertight/winding-consistent/`is_volume`, `.txt` mapping output
spot-checked to confirm baseline/cutout values actually move independently
per combination (both-on: both columns' values change together;
both-off: cutout stays pinned to its row's fixed value across every
column). tune.py's two `Switch` widgets verified via headless test
against a scratch config (not the user's real files) - correct initial
values, save round-trip.

## 17. `layout.baseline_row`/`cutout_row` exposed on the Element tab

User asked why calibration's cutout/baseline values print negative -
explained the coordinate convention (these arrays are "distance below the
clip end," not absolute Z - `place_on_cylinder`'s
`BASELINE_Z_OFFSET (=Element_Height) + baseline_mm` is what converts them
into an absolute position; the console/`.txt` output deliberately mirrors
the raw config value so it can be pasted straight back in). Immediate
follow-up: "missing the values to place baselines and cutouts in the
Element tab" - the whole point of Calibration is finding a number to dial
in, and there was no dial to turn without hand-editing the YAML.

`layout.baseline_row`/`cutout_row` are 3-element inline numeric arrays
(one per row) - list-valued, so they never fit the generic FIELDS
mechanism's one-scalar-per-key assumption (same reason `layout.rows`
needed its own bespoke block-list patcher back in the original tune.py
build-out). Added a matching bespoke mechanism for INLINE (not block)
lists: `patch_yaml_list_item(text, key, index, value)` - regex-matches
`key: [...]`, splits on commas, replaces just the one element, rejoins -
leaves everything else in the file untouched, same "surgical patch, not a
round-tripped YAML dump" philosophy the other patchers already use.

6 new bespoke `Input` fields (`baseline_row_0/1/2`, `cutout_row_0/1/2`,
labeled "Baseline row 0 (lowercase)" etc.) appended to the bottom of the
Element tab specifically (`_compose_section_tab` calls
`_compose_baseline_cutout_fields()` when `section == "Element"`) - not
folded into `SECTIONS_COMMON["Element"]` since they need
`patch_yaml_list_item` instead of `patch_yaml_value`, same reasoning
`BASELINE_CUTOUT_KEYS` (a module-level set of their 6 `self.inputs` keys)
exists for: `_collect_values`/`_save_to_yaml` both check membership to
route them to the list-item patcher instead of the generic scalar one,
and `_refresh_widgets_from_cfg` repopulates them explicitly (same pattern
Layout's custom rows and Type Test's fields already use for their own
bespoke widgets).

Verified: `patch_yaml_list_item` unit-tested directly against a
representative YAML snippet (patches only the targeted index, leaves
surrounding keys/formatting untouched); full headless round-trip against
a scratch config (initial values populate correctly, edit+save persists
correctly, a genuinely invalid value is rejected with an error log and
`None` return, matching every other field's error-handling convention);
visually confirmed via screenshot (renders cleanly at the bottom of the
scrollable Element tab, correct labels/values); `generate.py`'s normal
build path re-confirmed unaffected (byte-identical `ResinPrint` output).

## 18. Fixed Calibration's reference sourcing (was a real moving-target bug) + sweep defaults

User: "what is the reference baseline/cutout, is it sourced from the
running config, or default/master config - we would want to use a fixed
value, probably master because if we change config and use that as
reference, we could be chasing a value that is always changing after we
updated our config." Checked: `CalibrationTextRing` used the module
globals `BASELINE_ROW`/`CUTOUT_ROW`, set by `configure()` from whatever
config the process was given - for a real tune.py Preview/Render, that's
`self.config_path`, the RUNNING copy. Combined with part 17's new Element
tab fields (which write to that same running copy), this was a genuine
bug the user caught before it bit anyone: dial in a value from one
calibration pass, hit Preview again, and the sweep would silently
re-center on your just-saved edit instead of staying anchored - each
pass chasing the previous one's result instead of converging on a fixed
target.

**Fix**: `CalibrationTextRing`/`Additive`/`Element` gained
`reference_baseline_row`/`reference_cutout_row` parameters, defaulting to
the `BASELINE_ROW`/`CUTOUT_ROW` globals when not given (preserves exact
prior behavior for direct/CLI callers with no override). New
`generate.py --calibration-reference-config PATH` flag loads
`layout.baseline_row`/`cutout_row` from a SEPARATE file and passes them
in explicitly; `tune.py`'s `_run_build` always passes
`self.master_config_path` here for calibration builds. Also added a
summary print at the start of every `CalibrationTextRing` run
(`test_char=... vary_baseline=... vary_cutout=... start=...mm
interval=...mm - reference baseline_row=[...] cutout_row=[...]`) so which
reference is actually in effect is never ambiguous from the log - this
was as much the user's real question ("what is the reference... sourced
from") as it was a bug report, so making it visible closes the loop
properly instead of just fixing the code silently.

**Verified the fix is real, not just plausible**: built a scratch
"running" config with `baseline_row[0]` hand-edited to `-4.5` (simulating
an already-dialed-in value) against the real unmodified master
(`baseline_row[0]=-4`) - confirmed via direct CLI that
`--calibration-reference-config <master>` reports `reference
baseline_row=[-4, ...]` and produces `baseline=-4.7mm` at column 0
(`-4 + start(-0.7)`), NOT `-5.2mm` (what `-4.5 + -0.7` would give);
confirmed the opposite (no reference flag) correctly falls back to
whatever config was passed, for backward compat. Then reproduced the
exact real-world scenario end-to-end through `tune.py`'s actual
`_run_build` worker (real subprocess, scratch config, not the user's
real files): set `baseline_row_0` to `-4.5` via the Element tab widget,
ran Preview (which saves the running copy first, confirmed via `grep` -
the running file really did get `-4.5`), and the resulting `.txt` mapping
still showed `baseline=-4.0000mm` at column 0 (master's original,
untouched value) - the moving-target bug is gone.

**Sweep default changed**: user also asked for `calibration.start`'s
default to be `-0.7` (was `0.0`) "so we tet above and below the set
reference" - `0.0` only ever swept upward from the reference (0 to
`+interval*27`); `-0.7` (interval unchanged at `0.05`) now spans -0.7mm
to +0.65mm across the 28 columns, testing both directions. Changed in
both config files and both machines' `configure()` fallback defaults.

## 19. Mignon ported (first non-"cylinder machine")

User: "lets proceed with the roadmap. the next elements. slightly
different in that theres no gauge for them but there is calibration."
Dispatched an Explore agent for the same function-by-function comparison
methodology used for Postal (part 8) - the result was a much bigger
divergence than expected: unlike Postal (one drive-pin-trio difference),
**Mignon shares almost nothing structural with `cylinder_machine.py`** -
only the glyph placement pipeline (`TextRing`) and the Calibration
mechanism are genuinely reusable as-is. Confirmed directly from
`v2/mignon.scad`: no `Core`/`ClipCylinder`/`WireBite`/`SpeedHoles`/
`core_shaft.scad` family at all (plain `rotate_extrude()` shaft bore), a
12-sided polygon body instead of round, a stepped-boss+chamfer top
instead of a wire clip, a plain cut-through alignment keyway instead of a
countersunk drive pin, top+bottom Minkowski cleanup instead of top-only,
and fully bespoke resin-support placement (raft ring + rods at two radii,
none of `CutGroove`/`SpeedHoleSupport`/`DrivePinSupport`/
`BottomSupports`). Also: 7 physical rows/12 columns, not 3/28 - and no
Shaft Gauge Test at all (confirmed via `v2/mignon.scad:30`'s own comment,
also true for Bennett/Helios Klimax per their own files).

**Two shared, backward-compatible `cylinder_machine.py` changes** (both
regression-verified byte-identical against Blickensderfer/Postal):
1. `TextRing`/`CalibrationTextRing`'s hardcoded `for row in (0,1,2):` ->
   `range(len(DHIATENSOR))` - Mignon's 7-row `Baseline_Regular`/`Cutout`
   arrays needed this; reduces to the identical 3-row loop for the
   existing machines' configs.
2. `place_on_cylinder()` gained optional `placement_protrusion`/
   `angle_half_step` params (`None` = the exact prior hardcoded
   `Char_Protrusion`/`0.5` behavior) - v2's own documented optional-
   override mechanism (`lib/glyph_pipeline.scad`'s
   `Letter_Placement_Protrusion`/`Angle_Half_Step`, already designed for
   exactly this - Bennett/Mignon/Helios override both to 0). Verified
   `build_glyph()` itself needs NO Mignon-specific changes -
   `Letter_Extrude_Offset`/`Letter_Extrude_Depth` (v2's manual per-vertex
   depth tuning) have no v4 equivalent, since v4's real-Minkowski-sum
   architecture already auto-computes margin per-glyph.

**`lib/mignon.py`** (~380 lines, new file) reimplements the rest locally:
`PolygonCylinder`/`ElementChamfer`/`ElementLabel`/`MinkCleanup`/
`CenterShaft`/`HollowBody`/`AlignmentPin`/`ResinSupport`, plus its own
`Additive`/`FullElement`/`ResinPrint`/`CalibrationAdditive`/
`CalibrationElement` (can't reuse `cylinder_machine.CalibrationElement` -
it unconditionally builds `Cylinder()+ClipCylinder()`, which would crash
outright on Mignon's missing `Body_Fn`/`Clip_OD` globals). `ElementLabel`
reuses the same "flat, non-drafted" simplification `LogoText()` already
established for Blickensderfer/Postal's logo (v2's real version gets a
small sphere-minkowski rounding, cosmetic only, not the big draft-cone
struck characters get) - explicitly flagged as a known simplification,
not silently. `ResinPrint()` faithfully ports a genuine v2 quirk that
looked surprising at first: it FLIPS the whole element upside-down before
adding supports (`translate([0,0,Element_Height]) rotate([0,180,0])`,
`v2/mignon.scad:438-439`) - the label/chamfer end ends up facing the
build plate, the shaft/mechanical end faces away from supports.

`config/mignon.yaml`: real font found locally (`Iosevka Etoile.ttf` -
already genuine TrueType, no cubic-curve concern). Physical layout
(German 4 / `Layouts[5]`, 7 rows x 12 columns) computed programmatically
from `v2/lib/layouts/mignon_layouts.scad`'s `DEUTSCH4` array through
`Char_Legend`'s remap, same as Postal's `layout.rows` derivation - not
hand-transcribed. `resin.support_height`/`support_thickness` and several
`element:` keys are Mignon-only, not shared with Blickensderfer/Postal's
schema.

**`generate.py`**: the `HollowSpace()` character-root-containment check
was Blickensderfer/Postal-specific (Mignon has no `HollowSpace()` at all -
its hollow-out, `HollowBody()`, is a structurally different taper with no
equivalent diagnostic question) - changed to `if hasattr(bd,
"HollowSpace")` instead of assuming every machine has one.

**`tune.py`**: `SECTIONS_COMMON` trimmed to only the two genuinely-
universal tabs (Font & Alignment, Calibration) - Logo/Quality/Resin
split into `*_BLICKPOSTAL` and `*_MIGNON` variants (Mignon's schemas
diverge in all three, not just Element), and Gauge became fully optional
(`GAUGE_FIELDS`, only in `SECTIONS_BY_MACHINE["blickensderfer"/"postal"]`
- `compose()`'s Gauge tab and `_compose_build_tab()`'s "Shaft Gauge"
dropdown option both check `"Gauge" in self.SECTIONS` now instead of
assuming presence). Added `"mignon"` to `MACHINES`.

**One real bug found and fixed via direct visual verification** (not
just numeric watertight checks - rendered actual screenshots at multiple
angles, since a plausible-but-wrong character/column arrangement can
still be watertight): `v2/mignon.scad:120`'s `Latitude_Int=-360/
len(Layout[0])` is NEGATIVE - missed on the first implementation pass
(copied Blickensderfer/Postal's positive `360/columns` formula
literally). Caught by rendering the built element from multiple angles
and cross-checking against a rigorous, non-visual confirmation: exported
a single isolated glyph ('F') and inspected it from the exact "print
face" viewing direction, confirming `build_glyph()`'s existing struck-
character mirror (verified correct for Blickensderfer earlier this
session, and 100% shared/unchanged code - not something Mignon-specific
config could affect) was working exactly as intended the whole time; the
actually-wrong thing was column wrap direction, fixed by hardcoding the
sign flip in `mignon.py`'s own `configure()` (a real, sourced,
machine-specific value, not a `cylinder_machine.py` change).

**Verified thoroughly**: all 84 positions (7x12) build successfully with
`--no-minkowski` (fast path, ~0.7s) AND `--minkowski` (real full-quality
draft, ~53s) - fully watertight/winding-consistent/`is_volume` in both,
plus the resin-support/flip path and the Calibration path (including
`--calibration-vary-baseline` forcing BOTH sweep variables on
simultaneously). Visually confirmed via multiple `f3d` renders (isolated
single-glyph, plain element, full `ResinPrint` with supports) - real
12-sided body, correctly placed/legible-when-struck characters, working
resin support raft+rods. `tune.py` regression-verified for both existing
machines (identical field counts to before: 78/73 total fields including
Calibration's 5, matching the pre-restructuring 73/68 + 5 exactly) and
newly verified for Mignon (50 fields, no Gauge tab mounted, correct
Element/Resin values, save round-trip) via headless `App.run_test()`
against scratch config copies throughout - never the user's real files.

## 20. Layout tab was hardcoded to 3 rows everywhere - fixed for Mignon's 7, imported all 30 real presets

Right after the Mignon port landed, testing the Layout tab surfaced the
obvious gap: it was written when Blickensderfer/Postal (3 physical rows
each) were the only machines, and "3" had leaked into the code as a
literal in nine separate places rather than being derived from the
config. Mignon has 7 rows and, unlike Postal's single QWERTY preset, a
real catalog of ~30 named language layouts in
`v2/lib/layouts/mignon_layouts.scad` that were never imported.

**Importing the presets.** Read all 338 lines of
`mignon_layouts.scad` directly and transcribed its 33 raw layout
arrays. 3 are empty placeholders in v2 itself (`CUSTOMLAYOUT`,
`DEUTSCH_FRAKTUR_GOTISCH`, `DEUTSCH_FRAKTUR_PROF_STIEHL`) and were
excluded, leaving 30. Each row was passed through the same
`Char_Legend=[7,8,9,10,11,0,1,2,3,4,5,6]` remap used for Postal's
preset import (part 14/15) - v2 authors the raw arrays in one column
order and remaps them to physical placement order at load time, so a
literal transcription would have been wrong. Two rows (Georgian rows
2/4, Greek-new-ortography rows 3/4) have 13 characters in v2's source
where every other row has 12 - confirmed this is dead data in v2
itself (`Char_Legend` only ever indexes 0-11, so v2 never reads a
13th character either) and truncated to `r[:12]` rather than guessing
which character was erroneously included. Result:
`LAYOUT_PRESETS_MIGNON`, a 30-entry dict of 7-row layouts, verified
programmatically (all 30 x 7 x 12) before being pasted into `tune.py`
and registered in `LAYOUT_PRESETS_BY_MACHINE["mignon"]`.

**The `range(3)` sweep.** `grep -n "range(3)"` found nine hardcoded
occurrences across `tune.py`: `BASELINE_CUTOUT_KEYS` (a module-level
constant - had to become an instance attribute,
`self.BASELINE_CUTOUT_KEYS`, computed in `_load_machine()` from
`len(self.cfg["layout"]["baseline_row"])`, since row count now varies
per machine), `_compose_baseline_cutout_fields`'s `ROW_LABELS`
enumeration (silently dropped rows past index 3 - fixed to iterate
`range(len(values))` and only use `ROW_LABELS[i]` as an optional
parenthetical when in range), `_compose_layout_tab` (x2: the
row-preview widgets and the help text's literal word "3 rows"),
`_refresh_widgets_from_cfg` (x3), `on_select_changed`,
`on_switch_changed`, and `_save_to_yaml`'s custom-rows collection. All
now derive the count from actual data (`len(display_rows)`,
`len(current_rows)`, `len(arr)`, or `n_rows` read from config)
instead of a literal. Also restructured `_compose_layout_tab`'s
preset-help-text branch from `if blickensderfer / elif options / else`
to explicit per-machine `elif` branches - the old fallthrough would
have matched Mignon into Postal's "only one physical layout" copy,
since Mignon now has `options` truthy too, just with 30 instead of 1.

**Verification**, all via headless `App.run_test()` against scratch
config copies: Mignon - 30 presets load, dropdown correctly
auto-detects "German 4" as the current preset from `config/mignon.yaml`'s
rows, all 7 read-only preview widgets exist, all 14
`baseline_row_N`/`cutout_row_N` Element-tab fields present, switching
the dropdown to "Russian 3" + enabling "Modify glyphs" correctly seeds
all 7 custom-row `Input` widgets from `LAYOUT_PRESETS_MIGNON["Russian
3"]`, and a preset-switch-then-save round-trip writes the full 7 new
rows to `layout.rows`. Blickensderfer/Postal regression - both still
show exactly 6 baseline/cutout fields and 3 row widgets (unchanged),
Gauge tab still mounts, Postal's single QWERTY preset still
auto-detects correctly. Visually confirmed via an `App.run_test()`
SVG screenshot of Mignon's Layout tab: German 4 selected, all 7 rows
rendered with correct content, help text reads "7 rows" (not the old
hardcoded "3 rows").

## 21. Mignon Element/Logo tab audit: keyboard-legend layout order, a real second "Label" feature, Tallen mode

User audit request: make sure Mignon's Element tab (and "check all other
things") are genuinely Mignon-specific, not leftover Blickensderfer/Postal
material, and that nothing real from v2 is missing. Cross-checked
`ELEMENT_FIELDS_MIGNON`/`LOGO_FIELDS_MIGNON`/`QUALITY_FIELDS_MIGNON`/
`RESIN_FIELDS_MIGNON` and `config/mignon.yaml`'s actual numeric values
field-by-field against `v2/mignon.scad`'s real customizer sections - no
leaked Blickensderfer/Postal fields or wrong-machine values found (every
field list was already correctly scoped, every value matched v2 exactly).
Found and fixed three real, distinct gaps instead:

**Layout preset rows were stored in build order, not keyboard-legend
order.** The 30 presets imported in part 20 (and `config/mignon.yaml`'s
own `layout.rows`) were stored as v2's Char_Legend-remapped
`Physical_Layout` (`Char_Legend=[7,8,9,10,11,0,1,2,3,4,5,6]`,
`v2/mignon.scad:88,275`) - correct for driving the build directly, but not
how a person reads the legend off the actual keyboard/manual (v2's own,
separate `Layout` array). User's example: `7890-#123456` should read
`#1234567890-`. Algebraically, `keyboard = physical[5:] + physical[:5]`
is the *exact* inverse of the Char_Legend remap for this specific
7-then-5 split - verified both symbolically and by round-tripping every
row of every preset back through Char_Legend and confirming an exact
match against the original physical-order data (zero build-output change).
Applied that rotation to all 30 `LAYOUT_PRESETS_MIGNON` entries and to
`config/mignon.yaml`'s `layout.rows`, added `layout.char_legend:
[7,8,9,10,11,0,1,2,3,4,5,6]` to config, and added the actual remap step
(`DHIATENSOR = [[row[char_legend[c]] for c in ...] for row in
layout["rows"]]`) to `lib/mignon.py`'s `configure()` - previously
`DHIATENSOR` was just `layout["rows"]` verbatim, silently relying on the
stored data already being pre-remapped. Verified the rebuilt `DHIATENSOR`
is byte-identical to the old hardcoded physical-order string for German 4
- this is purely a display/edit-order change, the STL is unaffected.

**A genuine second "Label" engraved-text feature, not in v2 at all.**
Re-read v2/mignon.scad's real `[Logo]` customizer section (lines 218-236)
end to end - it contains exactly ONE engraved-text feature
(`Cylinder_Label`/`ElementLabel()`), which is what this app's existing
`logo.*` config/tune.py "Logo" tab already drives (schema-reuse naming,
not a second feature - confirmed Blickensderfer's real `[Logo]` section
the same way: one `LogoText()`, no separate label concept anywhere in v2).
User wants a second, independent one added anyway, same field format as
Logo, permanently 180 degrees opposite it. Implemented as a genuinely new
v4-only feature: extracted the placement math into
`_render_engraved_text(text, size, spacing, position_offset,
height_offset, font_path)`, renamed the existing function `ElementLabel`
-> `ElementLogo` (unchanged behavior, still reads `logo.*`), added a new
`ElementLabel()` reading a new `label.*` config section, with
`Label_Position_Offset` computed as `Logo_Position_Offset + 180.0` in
`configure()` (an invariant, not a stored/independently-editable value -
moving Logo moves Label with it). `Additive()`/`CalibrationAdditive()`
now union both. tune.py's `LOGO_FIELDS_MIGNON` gained 5 parallel
`label_*`-keyed fields (font/text/size/spacing/height-offset, no position
field since it's derived) in the same "Logo" tab, `label_font_path` added
to `FONT_PATH_FIELD_KEYS` for its own Browse button. Default `label.text`
is empty, NOT a copy of `logo.text` - checked the math first: at Logo's
real 15deg/char spacing, "Leonard Chau 2026" (18 chars) already spans
~255 degrees, so a second copy 180 degrees away would heavily overlap the
first instead of sitting cleanly opposite it (255+255 > 360). Verified via
direct `FullElement()` builds + `f3d` renders: default (empty label)
builds clean; a short test string ("TEST") renders legibly at the bottom
of the chamfer ring while "Leonard Chau 2026" occupies the top - visually
confirmed 180 degrees apart, no overlap.

**Tallen (Plakatschrift) mode - acknowledged missing in the original port
comment, now implemented.** `v2/mignon.scad:109-115,197`: a display-type
variant that adds `Height_Increase` (3mm) to `Element_Height` and shifts
every `Baseline` row by `Tallen_Baseline_Offset` (-1.25mm) when
`Tallen=true` - `Cutout` has no Tallen variant in v2 at all, a real
asymmetry (Baseline shifts, Cutout doesn't), not an oversight to fix.
Added `element.tallen`/`height_increase_mm`/`tallen_baseline_offset_mm`
to config (off by default, matching v2 and this file's real untallened
German 4 element), wired into `configure()`
(`Element_Height`/`BASELINE_ROW` both conditional on `Tallen`, `CUTOUT_ROW`
untouched), and exposed as three new `ELEMENT_FIELDS_MIGNON` entries.
Verified: `Tallen=false` reproduces the exact prior `Element_Height`
(40.5) and `BASELINE_ROW` values; `Tallen=true` gives 43.5 and every
baseline shifted by exactly -1.25 with `CUTOUT_ROW` unchanged; full builds
succeed watertight in both states.

Deliberately NOT touched, flagged as pre-existing/cross-machine gaps
rather than Mignon-specific bugs (would be real scope creep to fix here):
v2's "unified" glyph-quality system (`Weight_Adj_Mode`/`Scale_Multiplier`/
`Y_Scale`/`Text_Align_Method` and friends) has no v4 implementation for
ANY machine, not just Mignon (`grep` confirmed zero references anywhere
in `lib/*.py`). Same for `Character_Modifieds`/`Typeface_2` (per-character
baseline shift + secondary-font-by-character) - present in ALL THREE v2
machine files, not ported for any of them. Both belong in a dedicated
follow-up, not folded into a "make Mignon's existing fields correct" pass.

Regression-verified Blickensderfer/Postal: field counts unchanged
(78/73), no duplicate `self.inputs` keys introduced by the new
`label_*`/`tallen`/etc. keys (checked across the whole file, not just
Mignon's own section, since `self.inputs` is a single flat dict), no
Mignon-only keys leaked into their field sets.

## 22. tune.py help-text/tooltip `Static`s were clipped, then found to double-wrap once un-clipped

User report: tooltip/help messages in the TUI get cut off when longer
than their box. Traced to `.field-help`, `.picker-help`, and
`.advanced-warning` all being pinned to a fixed `height` (1 or 2 rows)
in `TuneApp.CSS` - any message longer than that was clipped instead of
wrapping. Worst offenders were the Gauge/Calibration `SECTION_INTROS`
banners: authored as 7-9 line strings but rendered squashed to a single
visible line. Fixed by switching `.field-help`/`.picker-help`/
`.advanced-warning` to `height: auto` (and `.field-row` to `height:
auto` + `margin-bottom: 1`, since it previously relied on a fixed
`height: 2` for both the Horizontal row and its optional help line).

That surfaced a second, distinct bug: those same banners (and the
Layout tab's per-machine notes, the Build tab's target explainer, the
Type Test intro) were hand-wrapped with embedded `\n` at some assumed
width. With the box now auto-sizing, Textual wrapped each
already-broken line a *second* time - confirmed via a headless
`App.run_test()` region check, Gauge's 7-line intro rendered at
`height=14`. On a normal-height terminal this pushed the real
Offset start/Offset int inputs (Gauge) and test_char/start/interval
inputs (Calibration) far enough down the tab to require scrolling past
the fold - reported by the user as the text "covering" the inputs and
making them impossible to edit. Fixed by removing every manual `\n`
line break from TUI-displayed help text (single flowing string, wraps
exactly once) and rewriting the wording shorter throughout - dropped
internal v2-source cross-references and redundant clauses. Re-verified
headlessly: Gauge's intro dropped from 14 rendered lines to 6, with
both its inputs landing at row 12/15 even in a 24-row terminal.
Short one-line field-level hints (e.g. "TrueType font for the struck
characters.") were already concise and left untouched.

New standing rule for any tooltip/help-text `Static` added to tune.py
from here on - see `CLAUDE.md`: `height: auto`, never a fixed row
count; no manual `\n` line breaks (let Textual wrap once); keep the
wording to 1-2 short sentences.

## 23. Helios Klimax ported (Bennett's own port, in between, has no log chapter - see CLAUDE.md's note on that)

Diffed `v2/heliosklimax.scad` (unusually, already self-documenting - its
own header records a real v1->v2 byte-check correction history) against
`lib/cylinder_machine.py` function-by-function per the standing rule, not
assumed from "it's cylindrical too". Result: even less shared than
Mignon/Bennett - Helios has no `SecondaryCore`/`CoreGrooves`/`CoreChamfer`/
`CoreEllipses` at all (v2's own header: "not applicable... in the
original"), no Logo/Label engraved text, and no Shaft Gauge Test (same
header: "Sections with no Helios equivalent... are omitted"). Only
`TextRing`/`CalibrationTextRing`/`place_on_cylinder` (via
`cylinder_machine._receive_config`) are genuinely reused; everything else
is new, bespoke code in `lib/helios.py`.

**Two real values resolved that `place_on_cylinder`'s docstring had
flagged as "not yet verified either way" for Helios:**
`placement_protrusion=-0.05` (v2's `Letter_Placement_Protrusion=-.05` - a
real, if small, built-in 0.05mm radial inset, distinct from the platen-
cutout radius which still uses the full `Char_Protrusion`) and
`angle_half_step=0` (no half-column centering term, same as Mignon). Both
threaded through as explicit `lib/helios.py` module globals
(`Placement_Protrusion`/`Angle_Half_Step`), same pattern Mignon's
`configure()` uses. Updated `place_on_cylinder`'s docstring to record
Helios's real verified value instead of leaving it as an open question.

**A genuine two-stage `difference()` in v2's `Assemble()`, not a simple
additive-minus-subtractive split.** v2 nests three `difference()`s:
`AlignmentPinSupport()`/`ClipRetainer()` (two bosses) are unioned in
*after* the first round of cuts (`HollowingElement`/`MinkCleanup`/
`IndicatorHole`), then themselves get cut by a second round
(`AlignmentPinHole`/`CenterShaftHole`/`WireClip`). Checked whether
flattening this into one "union everything, subtract everything" (the
pattern every other machine's `FullElement` uses) would actually change
the result, since that's a much simpler shape to write - it would have:
`AlignmentPinSupport`'s boss sits at radius 8.92mm, height range
[1.5, 4.5]mm, which falls *inside* `HollowingElement`'s own cavity extent
(radial span ~[4.58, 11.08]mm, height span ~[2.5, 16.2]mm, both computed
from the real config values) - in the true nested v2 order the boss is
added after that cut already happened, so it's untouched by it; a naive
flattened version would incorrectly eat the boss. `lib/helios.py`'s
`_assemble()` reproduces the real staged construction directly instead
(stage-1 cut, then union the bosses; `FullElement`'s own final
`.difference()` is only the genuine outer-scope cut). Documented at
length in the module docstring so the next person touching this file
doesn't "simplify" it back into the wrong flattened form.

**`HollowingElement()`'s true circular-hull cross-section**, ported as a
real `shapely` convex hull of 5 circles (matching v2's `hull(){circle();
circle(); ...}` exactly - true rounded corners) rather than
`cylinder_machine._hollow_space_profile()`'s hand-rounded point-list
approximation, the same technique `WireBite()`/`mignon.AlignmentPin()`
already use for a real hull-then-revolve/extrude.

**Two declared-but-unused v2 fields, preserved as such rather than wired
up or silently dropped** (v2's own header comment confirms both,
independently of this port): `Cyl_Fn` ("critical shaft/pin cylinder facet
number") is declared but never referenced anywhere in v2's real
`Assemble()`/`TypeTest()` - every cylinder there uses `Surface_Fn`
instead; kept in `config/helios.yaml`/`lib/helios.py`'s `configure()` for
schema parity, not read by any function. `Resin_Support`/
`Resin_Support_*` are declared but v2 never builds any actual support
geometry with them (no `ResinRod`/`CutGroove`-equivalent module anywhere
in the file) - `ResinSupport()`/`ResinPrint()` in `lib/helios.py` are
therefore a plain no-op/alias to `FullElement()`, so toggling tune.py's
always-present "Resin supports" checkbox does something sane (produces
the plain element) instead of an `AttributeError` for this one machine.
`Text_Fn`/`Text_2D_Fn` (v2's OpenSCAD `$fn` hook for glyph curves) was
*not* ported even as declared-but-unused, since it has no v4 equivalent
at all - v4's `build_glyph()` samples curves via `points_per_mm`
vector-tracing, not an OpenSCAD facet count.

**tune.py wiring**: `MACHINES["helios"]`, `SECTIONS_BY_MACHINE["helios"]`
(`Font & Alignment`/`Calibration`/`Quality`/`Resin`/`Element` only - no
`Logo`/`Label`/`Gauge` key, per the header note above),
`LAYOUT_PRESETS_HELIOS` (both of v2's inline arrays, `GERMAN_MOD` -
v2's real default/only-used one - and the superseded `GERMAN`, the same
"expose what's textually in the source" treatment Bennett's redundant
`CUSTOM` preset got), and a `LAYOUT_PICKER_HELP["helios"]` entry.
`BASELINE_CUTOUT_KEYS`/`ROW_LABELS`/the Layout tab's row-count logic were
already fully row-count-agnostic from Mignon's part-20 fix, so Helios's 4
rows (vs. everyone else's 3) needed zero additional literal-count fixes -
confirmed by grep, not just assumption. Verified the whole form actually
composes (not just that the dicts are well-formed) via a headless
`TuneApp(...).run_test()` against a scratch copy in `/tmp` (never the real
config, per the standing warning above) - all 8 expected tabs present,
no `Logo`/`Label`/`Gauge` tabs, no exceptions.

**Audit pass** (per CLAUDE.md's "every machine port gets its own dated
chapter" rule): cross-checked `ELEMENT_FIELDS_HELIOS`/
`QUALITY_FIELDS_HELIOS`/`RESIN_FIELDS_HELIOS` and `config/helios.yaml`'s
actual values field-by-field against v2's real customizer sections and
against Mignon/Bennett's equivalent lists - no leaked fields from another
machine, no missing real v2 field, `resin.*` lives under `resin:` (not
`quality:`, avoiding Mignon's known outlier - see CLAUDE.md "Pick one
convention"). No list-valued config key silently unexposed:
`layout.baseline_row`/`cutout_row` get the existing bespoke
`patch_yaml_list_item` treatment (row-count-agnostic already), `layout.
placement_map`/`rows` are deliberately YAML-only (same treatment as every
other machine).

**Verification** (hard gate): full-quality build (`generate.py
config/helios.yaml`, config defaults - Minkowski on, `points_per_mm=15`)
completed in ~62s, `FullElement: watertight=True winding_consistent=True
is_volume=True volume=4276.923mm3`, all 84 characters placed with zero
skips. 44 inter-character collisions were reported (detection-only, per
`_check_inter_character_collisions`'s existing design) - expected at
Helios's tight 21-column layout on a 27.15mm element, not a defect
introduced here. Fast preset (`--points-per-mm 8 --cone-segments 12
--no-minkowski`) verified clean across every build mode: plain
`FullElement`, `--resin-support` (byte-identical volume to plain,
confirming the no-op alias), `--cut-bodies`, and `--calibrate`. Confirmed
zero side effects on existing machines: `cylinder_machine.py`/
`scad_primitives.py`/`glyph_poc.py` were not touched by this port (Helios
needed none of their machine-specific pieces beyond
`TextRing`/`CalibrationTextRing`/`place_on_cylinder`), and a Blickensderfer
regression run reproduced the exact baseline from this file's own
"Verifying a geometry-affecting change" section byte-for-byte
(`verts=42618 faces=85408 ... volume=5666.804mm3`).

## 24. Helios's shaft bore upgraded to reuse cylinder_machine.py's core_shaft family

Follow-up to part 23, same session's continuation. Explicit user
direction: "we can reuse the cylinder machines design for chamfering the
inner shaft, bottom and top boss, then doing the fancy core stuff that
are on all the other cylinders" - i.e. swap Helios's plain straight
shaft-bore cylinder for the same `Core()`/`CoreChamfer()`/
`SecondaryCore()`/`CoreEllipses()`/`CoreGrooves()` family Blickensderfer/
Postal/Bennett already reuse from `lib/cylinder_machine.py`. A real,
deliberate DEVIATION from v2 (which part 23's own audit correctly
confirmed had none of this), not a porting correction - documented as
such in both `config/helios.yaml`'s header and `lib/helios.py`'s module
docstring, per CLAUDE.md's "say so explicitly instead of silently
diverging" rule.

**No v2 source of truth for the new dimensions.** `core_chamfer`/
`core_bottom_offset`/`core_contact_length`/`core_web_*`/`core_groove_*`
have no real Helios value to port - v2 simply never had this system.
Seeded from Bennett's config instead (closest shaft diameter of any
existing machine: 3.4mm vs. Helios's own 4.16mm, and a close element
height too: 18.0mm vs. 18.7mm) as starting estimates, explicitly flagged
in both files as not-real-machine-numbers, meant to be tuned against the
physical part the same iterative way `layout.baseline_row`/`cutout_row`
already are - not treated as final values.

**A real bridging-alias footgun, caught before it caused a `NameError`.**
`cylinder_machine.Core()` references the bare global name `Clip_Height`,
not `Element_Clip_Height` - every existing reuser of that function
(Blickensderfer/Postal) happens to already have a config field named
exactly that, so this had never been exercised with a differently-named
source field before. Helios's own code (`ClipRetainer()`/`WireClip()`/
the rest of this module) already used `Element_Clip_Height` throughout
from part 23's port, and renaming it everywhere purely to satisfy one
reused function would have been needless churn - added `Clip_Height` as
a second global for the same value in `configure()` instead, documented
inline as a bridging alias. This is exactly the class of bug CLAUDE.md's
`_receive_config()` warning already calls out ("a new machine-set global
with a lowercase name is silently excluded") generalized one step
further: not just casing, but genuine cross-machine naming mismatches
between a shared function's expectations and a new machine's own
config-derived names - worth checking for on any future reuse of an
existing shared function by a new machine.

**Core_Top_Z/Core_Taper_Top_Z convention chosen deliberately, not by
default.** Helios has a real clip (`ClipRetainer()`/`WireClip()`, ported
faithfully from v2 in part 23), the same situation Blickensderfer/Postal
are in (chamfer/taper sit under the clip, `Core_Taper_Top_Z=Element_
Height` distinct from `Core_Top_Z=Element_Height+Clip_Height`) - NOT
Bennett/Mignon's clip-less `Core_Taper_Top_Z=Core_Top_Z`. Picked by
matching Helios's own physical situation to the right sibling precedent,
not by copying whichever machine was edited most recently.

**Two-stage difference structure preserved.** The new core_shaft parts
join `AlignmentPinHole`/`WireClip` in the genuine final-stage cut
(`_final_cut()`, previously named for `CenterShaftHole` which this change
removes entirely, replaced by `Core(0)`) - all near the shaft axis
(radius well under `Element_Square_Hole_Position`=8.92mm), so none of
them reach back into `AlignmentPinSupport`'s boss the way a naive
single-difference flattening risked for `HollowingElement` in part 23.
Confirmed by the build succeeding watertight/single-volume, not just
reasoned about.

**`build.render_core_groove`/`quality.groove_fn`/`quality.cyl_fn`** added
to `config/helios.yaml` and threaded through `FullElement`/
`CalibrationElement`/`Subtractive` (previously `render_core_groove` was
accepted-but-ignored, matching Mignon's "no core groove system" pattern -
now genuinely honored, since there IS one). `quality.cyl_fn` goes from
declared-but-unused (part 23's finding, confirmed correct for the
original v2 file) to genuinely read, for the first time, by `Core()`'s
shaft-bore facet count.

**Verification** (hard gate): rebuilt at both fast
(`--points-per-mm 8 --cone-segments 12 --no-minkowski`) and full quality
(config defaults) - `FullElement: watertight=True winding_consistent=True
is_volume=True` in every case, all 84 characters placed with zero skips,
same 44 informational inter-character collisions as part 23 (unrelated
to this change, at the layout/font level not the shaft). Verified
`--no-core-groove` actually changes the output (verts/volume differ from
the default-on build) - confirms the toggle is genuinely wired, not
silently ignored the way it used to be. `--resin-support` still produces
a byte-identical volume to the plain build, confirming the no-op alias
survived this change untouched. No shared module
(`cylinder_machine.py`/`scad_primitives.py`/`glyph_poc.py`) was touched
in this follow-up at all - only `lib/helios.py`/`config/helios.yaml`/
`tune.py` - so no regression check against other machines was needed
this time (zero possible side effect).

## Resuming later

1. **Hammond/Hammond_split and IBM are next** - the last two machines on
   the original roadmap, and the first two that are NOT cylindrical in
   form at all (shuttle mechanism and spherical, respectively). Per
   CLAUDE.md's machine-taxonomy note, do not reach for
   `lib/cylinder_machine.py` as a starting point for either - they need
   their own from-scratch "what, if anything, is genuinely shared with an
   existing machine vs. `glyph_poc.py`/`scad_primitives.py`-level
   primitives only" exercise, the same one Mignon/Bennett/Helios each
   went through for the cylindrical family.
2. Bennett's port (between Mignon and Helios) has no `SESSION_LOG.md`
   chapter of its own - per CLAUDE.md, that's flagged as correlating with
   Bennett having more small undocumented inconsistencies than Mignon.
   Worth a dedicated retroactive audit pass if anyone's in that area.
3. Mignon's `TypeTest()` (v2/mignon.scad:449-466) was not ported -
   tune.py's Type Test tab still works for Mignon (it's a generic flat
   CPI/LPI preview, not machine-specific), but the real fixed-pitch
   TypeTest() module itself (JoinRows/AlignedText-based) has no v4
   equivalent for any machine yet, not just Mignon - pre-existing gap.
   Same is true for Helios's own `TypeTest()` (v2/heliosklimax.scad:366-383).
4. Everything in part 14's original "Resuming later" list (separation_mm,
   inter-character collisions, performance, alignment offsets,
   platen_fn/body_fn) is still open.
5. v2's "unified" glyph-quality system (Weight_Adj_Mode/Scale_Multiplier/
   Y_Scale/Text_Align_Method/Text_Align_Modified*) and the Character_
   Modifieds/Typeface_2 per-character override systems have no v4
   implementation for ANY machine (not Mignon-specific) - see part 21.
