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
cutout radius which still uses the full `Char_Protrusion`) **- WRONG,
see part 25: this directly copied v2's raw value without re-deriving it
for v4's different transform structure, the exact mistake `lib/bennett.py`'s
port had already made and fixed. Corrected to `Char_Protrusion`
(the default).** and
`angle_half_step=0` (no half-column centering term, same as Mignon,
still correct). Both
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

## 25. Helios's placement_protrusion was wrong - characters sat too deep (user-reported)

User report: "min final char diameter is not working correctly. right
now the glyphs are inset into the element too much." Traced to
`lib/helios.py`'s `configure()` setting `Placement_Protrusion=-0.05` -
copied directly from v2's own `Letter_Placement_Protrusion=-.05`
(v2/heliosklimax.scad:268) during part 23's port. That was exactly the
mistake `lib/bennett.py`'s port had already made and fixed, documented at
length in `cylinder_machine.place_on_cylinder`'s own docstring - which
part 23 read (and even edited a neighboring line of) without applying
its lesson to Helios. Should have been caught during the original port;
wasn't, until it showed up as a physically-wrong build.

**The actual bug.** v2's `LetterPlacement` (where the raw pre-cutout
character block is positioned) and `PlatenCutout` (the cutting cylinder
that trims it down to its final visible shape) are TWO INDEPENDENT
transforms in v2. `Letter_Placement_Protrusion=-.05` only ever moves the
former - v2/heliosklimax.scad's own file-header comment confirms this
explicitly: "a small built-in 0.05mm radial inset that only affects
placement, not the platen-cutout radius." The latter - which is what
actually determines the physical strike depth, the thing `min_final_
character_diameter` is supposed to control - uses a completely
independent formula, confirmed by this same file's own "v2.0" comment:
`Element_Diameter/2+Platen_Diameter/2+Char_Protrusion`, the EXACT SAME
formula Blickensderfer/Postal use. v4's `build_glyph()`/
`place_on_cylinder()` have no such split at all - the platen scallop is
baked into one local mesh, placed by a single radial offset
(`placement_protrusion`) - so `place_on_cylinder`'s own docstring proves
the visible low point lands at exactly `Element_Diameter/2+
placement_protrusion`. Passing v2's raw `-0.05` (a value that in v2 only
ever affected the OTHER, unrelated transform) pinned the low point far
closer to the axis than the real machine's `min_final_character_diameter`
(28.19mm) implies - `Char_Protrusion` here is `(28.19-27.15)/2=0.52mm`,
vs. the wrongly-configured `-0.05mm`: over half a millimeter of extra,
wrong inset. `min_final_character_diameter`/`Char_Protrusion` were
effectively dead config values, the identical failure mode Bennett's
port found and named explicitly (`lib/bennett.py`'s own docstring: "with
`placement_protrusion=0`... `min_final_character_diameter` was a dead
config field").

**Fix**: removed the `Placement_Protrusion` global and the
`placement_protrusion=Placement_Protrusion` kwarg from both `Additive()`'s
`TextRing()` call and `CalibrationAdditive()`'s `CalibrationTextRing()`
call - omitting it lets `place_on_cylinder` fall through to its own
default (`Char_Protrusion`), exactly matching Blickensderfer/Postal/
Bennett's treatment. `angle_half_step=0` is untouched - a real, unrelated
v2 value with no two-transform split to worry about (angle placement is
a single unified transform in both v2 and v4). Corrected the stale
claims this introduced: `cylinder_machine.place_on_cylinder`'s own
docstring (previously asserted Helios "genuinely" needed a nonzero
value, now explains Helios needs the SAME re-derivation Bennett needed,
for the same reason), `lib/helios.py`'s module docstring/`configure()`
comment, `config/helios.yaml`'s build section comment, and `README.md`'s
Helios writeup - all previously stated the wrong -0.05 value as verified
fact rather than flagging it as unresolved/needing the same treatment
Bennett got.

**Lesson, stated plainly since it already cost a shipped bug once:**
reading a docstring that documents a prior fix is not the same as
applying its reasoning to new code in the same sitting - `place_on_
cylinder`'s docstring explicitly named this exact pitfall before part 23
ever touched Helios, and it was still missed. Any future machine that
reuses `place_on_cylinder` needs its OWN check for whether v2's
`LetterPlacement`/`PlatenCutout` (or equivalent) are one transform or
two, not a default assumption either way, and not a straight copy of
whatever raw customizer value v2 happened to expose for the block-
placement stage specifically.

**Verification** (hard gate): rebuilt at fast preset
(`--points-per-mm 8 --cone-segments 12 --no-minkowski`) - watertight,
single volume, all 84 characters placed with zero skips, same
informational-only inter-character collision set as before (unrelated to
this fix). No shared module was touched beyond the docstring correction
above (comment-only, zero logic change) - no cross-machine regression
risk.

## 26. f3d never auto-launched for Helios previews - a 33-second diagnostic hiding after "wrote ..." (user-reported)

User report: ran a Quick Preview for a Helios element, watched it finish
successfully (opened the STL afterward and it looked correct), but f3d
never auto-opened - and quitting the TUI printed a scary-looking
`Exception ignored in: <function BaseSubprocessTransport.__del__>` /
`RuntimeError: Event loop is closed` traceback. That traceback is just
asyncio cleanup noise (fires whenever a subprocess transport is
garbage-collected after the event loop that owned it has already
closed) - a symptom, not the cause. Ruled out a hard crash first
(headless `TuneApp().run_test()` boots the picker and composes Helios's
form fine, and a direct rebuild of the STL succeeds watertight/is_volume
and renders correctly in f3d standalone - see the render check earlier
this session) before finding the real bug.

**Root cause**: `tune.py`'s `_run_build()` only launches f3d after
`generate.py`'s subprocess reports `returncode == 0`
(`lib/cylinder_machine.py`'s `TuneApp._run_build`, unchanged this
session). `generate.py` prints `wrote <path>` as soon as the STL is on
disk, but then - for any machine defining `HollowSpace()` - runs one
more diagnostic step: `hollow.contains(part.vertices)` per character, to
report whether any struck character's root reaches the hollow cavity.
Timed it directly: for Helios, that ONE diagnostic call took **33
seconds** (`lib/helios.py`'s `HollowingElement()`/`HollowSpace()` mesh
had 95,760 faces - `.contains()` has no `pyembree` acceleration in this
environment, confirmed by `import trimesh.ray.ray_pyembree` failing, so
it falls back to an O(points x faces) ray-cast). The user saw `wrote
...` scroll by (looking done, especially since the fast build itself
only takes ~2.6s) and quit before the still-running subprocess finished
its extra diagnostic pass - killing it before `returncode == 0` was ever
observed, so f3d's launch branch never ran. Confirmed the same
diagnostic on Blickensderfer takes 0.18s against a 2,682-face
`HollowSpace()` mesh - not a universally slow path, specific to Helios's
own mesh being ~36x heavier for this one internal, invisible feature.

**Why Helios's hollow-cavity mesh was so much heavier**: two compounding
factors, both introduced during part 23's port, neither justified by
anything actually visible in the printed part. (1)
`HollowingElement()`'s profile is a `shapely` convex hull of 5 circles
(`resolution=32` each) - unlike a single-circle hull elsewhere (e.g.
`WireBite()`), 5 SEPARATE circles each contribute their own arc segments
to the hull boundary, compounding into 134 profile points (measured),
vs. Blickensderfer's fixed 9-point hand-designed profile. (2) the
revolve used `sections=Surface_Fn`, and Helios's own config default for
`surface_fn` is 360 (vs. Blickensderfer's 120) - appropriate for
genuinely visible exterior surfaces (`Cylinder`/`ClipRetainer`/
`WireClip`) but wasted on a cavity that's entirely internal and never
seen once printed.

**Fix** (SUPERSEDED - see part 27: hardcoding a resolution/sections
value to route around a diagnostic's cost, instead of questioning
whether the diagnostic should exist, was the wrong fix - reverted, the
diagnostic itself was removed instead): `HollowingElement()` now uses a
fixed `resolution=6`/`sections=60` (not `Surface_Fn`) for its own
hull/revolve, chosen empirically to land close to Blickensderfer's own
face count (3,480 vs. 2,682) rather than picked arbitrarily. Diagnostic
timing: 33s -> 1.12s (~29x). Full Quick Preview, end-to-end via `generate.py`
exactly as `tune.py` invokes it: ~4.2s total (previously would have been
~2.6s build + 33s diagnostic ~ 36s) - comfortably inside normal
patience. Full-quality Render also got faster as a side effect (the
actual boolean cut is lighter too, not just the diagnostic): ~44s vs.
the ~79s measured in part 25, still watertight/is_volume/single-volume,
identical character placement (still 84/84 placed, same 16
informational inter-character collisions, unrelated to this change).

**Lesson**: an arbitrary "looks smooth enough" resolution choice made
during initial geometry porting (part 23's `resolution=32`, chosen with
no real justification beyond "seemed fine") had a real, compounding
downstream cost in a totally different code path (a debug diagnostic in
`generate.py`, not the geometry construction itself) that wasn't
exercised/timed until a real user workflow (Quick Preview -> auto-launch
f3d) hit it. For any internal/invisible geometry feature (a cavity, a
web, a fillet nobody will ever see or touch), default to a LOW,
deliberately-chosen resolution rather than reusing the same high-fidelity
knob visible exterior surfaces need - and time diagnostic/debug code
paths too, not just the main build, before considering a port done.

## 27. Removed the HollowSpace() diagnostic entirely instead of working around its cost; undid part 26's hardcoded resolution

User pushback on part 26's fix, and correct: (1) the `HollowSpace()`
"does any character root reach the hollow cavity" diagnostic in
`generate.py` is redundant - it never gated or failed a build (purely
informational), and its value was already known to be noisy/
non-actionable (the "HollowSpace margin is razor-thin by design" section
of `README.md` already documented that it flips `True`/`False` run to
run from floating-point noise at low `points_per_mm` - never a reliable
signal in the first place). Removing the SLOW THING rather than
optimizing around it is the right call when the slow thing wasn't
pulling its weight to begin with. (2) Part 26's fix - hardcoding
`resolution=6`/`sections=60` directly in `lib/helios.py` - was flagged
correctly as violating CLAUDE.md's real-numbers-live-in-config rule,
generalized here to cover facet-count/resolution constants too, not just
physical dimensions/tolerances/offsets: a magic number invented to route
around a cost imposed by a DIFFERENT piece of code (the diagnostic) has
no business being hardcoded into unrelated geometry construction code,
config or otherwise - the fact that the diagnostic could just be deleted
proves the resolution never needed to change at all.

**Removed**: the whole `HollowSpace()`-diagnostic block from
`generate.py`'s `main()` (the `.contains()` per-character ray-cast and
its print line), plus the now-dead-code comment two branches earlier
that referenced it. This is shared code, run for every machine - the
diagnostic is gone for Blickensderfer/Postal too, not just Helios (their
own `HollowSpace()` GEOMETRY functions are untouched and still load-
bearing - `cylinder_machine.Subtractive()` still calls them for the real
cut; only the EXTRA diagnostic call site in `generate.py` is gone).

**Reverted**: `lib/helios.py`'s `HollowingElement()` back to
`resolution=32`/`sections=Surface_Fn` - the same numbers every other
revolve in the file uses, no special case. Since the diagnostic that
motivated the lower values is gone, and the actual boolean cut was NEVER
the bottleneck (measured at 2.6s in part 26, whether the diagnostic ran
or not), there was no remaining reason to keep the geometry
lower-fidelity. Also deleted `HollowSpace()` itself from `lib/helios.py`
- it existed ONLY as an alias so the (now-removed) diagnostic could find
it via `hasattr(bd, "HollowSpace")`; with that caller gone, it was dead
code (Helios's real build calls `HollowingElement()` directly, never
`HollowSpace()`).

**Verification** (hard gate, since `generate.py` is shared): reran
`generate.py` for all five machines (Blickensderfer/Postal/Mignon/
Bennett/Helios) at fast settings - all watertight/single-volume, zero
errors. Blickensderfer reproduces this file's own documented baseline
byte-for-byte (`verts=42618 faces=85408 ... volume=5666.804mm3`),
confirming the diagnostic removal has no effect on any actual build
output (it only ever printed an extra line after the STL was already
exported). Helios's own numbers after reverting the resolution exactly
match what they were immediately after part 24 (before part 26's
detour) - `verts=109100 faces=218224 volume=4206.382mm3` at the same
fast-preview-with-core-groove settings - confirming the revert is a
clean, complete undo with no incidental drift.

**Lesson**: when a diagnostic/debug code path turns out to be
expensive, the first question should be "does this check still earn its
cost" before "how do I make it cheaper" - especially for a check that
was already known to be flaky/non-actionable. Optimizing a check that
shouldn't exist just entrenches it, and in this case would have meant
carrying a hardcoded, config-rule-violating magic number indefinitely
for a problem that had a strictly better fix available.

## 28. Disabled Helios's alignment-pin boss (user request); documented Resin supports as a no-op on the Build tab

Two small, explicit user requests, not bugs.

**Disabled `AlignmentPinSupport()`** (the boss `AlignmentPinHole()` is
cut through, v2's real support material around the alignment pin) -
commented out rather than deleted, per the user's own instruction, so it
can be reinstated later without re-deriving it from v2. Removed its call
from `_assemble()`'s union list; left `AlignmentPinHole()` itself
untouched (still cuts through the plain wall now, thinner than with the
boss - the user asked to remove the boss specifically, not the hole/pin
mechanism). Updated the module docstring's "Two-stage difference"
explanation and the `_assemble()`-adjacent comment to stop describing
the boss as active, while keeping the geometric reasoning for why the
two-stage `difference()` structure is still necessary regardless
(`ClipRetainer()` independently needs the same staging - it overlaps
`MinkCleanup()`'s top cutting cylinder's z-range - so disabling the boss
doesn't simplify `_assemble()`'s architecture, just removes one union
member from it). Verified: still watertight/single-volume, volume
dropped by ~52mm3 (the boss's own material), matching expectations.

**Documented "Resin supports" as a no-op for Helios on the Build tab.**
The checkbox is always shown regardless of machine (`_compose_build_tab`
has no per-machine gating for it, unlike the Gauge/Logo/Label tabs which
check `"X" in self.SECTIONS`), and toggling it for Helios silently does
nothing observable - `ResinPrint()` is already a plain alias to
`FullElement()` (part 23: v2 declares `Resin_Support`/`Resin_Support_*`
but never builds any actual support geometry). Added a new
`RESIN_SUPPORT_UNAVAILABLE_NOTE` dict (keyed by machine name, `""` via
`.get()` for every machine that DOES have real resin supports modeled)
appended to the existing help `Static` beneath the checkbox, following
CLAUDE.md's per-machine-banner-text rule (`LAYOUT_PICKER_HELP` is the
template - a dict lookup, not an `if self.machine == "x"` branch).
Verified via a headless `TuneApp(...).run_test()` against scratch copies
of both a Helios and a Blickensderfer config: the note text is present
for Helios, absent for Blickensderfer.

**Verification**: rebuilt Helios at fast settings (watertight/is_volume,
84/84 characters placed) and reran the Blickensderfer regression
(`generate.py` untouched this round, but `tune.py`'s shared
`_compose_build_tab` was touched, so machine-neutrality was worth
reconfirming) - reproduces the documented baseline byte-for-byte.

## 29. Hammond port (hammond.scad only) - audit, config/lib/tune.py, verified

Ported `hammond.scad` (the arc-shaped shuttle body) per the roadmap's next
item. `hammond_split.scad` deferred - see below, it turned out to be a
different machine in all but name.

**Audit pass** (per CLAUDE.md's explicit requirement for every machine
port). Diffed `v2/hammond.scad` (1105 lines) + `v2/hammond_split.scad`
(771 lines) + their `v2/lib/` includes against `lib/cylinder_machine.py`/
`lib/scad_primitives.py`/`lib/bennett.py`/`lib/mignon.py` function-by-
function, per CLAUDE.md's porting checklist, before writing anything.
Findings:

- **hammond.scad and hammond_split.scad are NOT near-twins** (unlike
  Blickensderfer/Postal) - `hammond_split.scad` has zero `include`
  statements (fully self-contained, its own inlined `TextAssemble`/
  `TextPlacement`/`LetterText`/`TextRing(side)` glyph placement, not
  wired to the shared `glyph_pipeline.scad` at all) and its own header
  explicitly calls itself "closer to IBM's spherical geometry" than the
  cylinder family. It's a completely different two-piece spoke/folder
  assembly (`Arc`/`Spoke*`/`Tube`/`FolderClearance`/`GlueHoles`), unrelated
  config variable names, and a third independent resin-support
  implementation. Deferred to its own future port - `config/hammond.yaml`
  and `lib/hammond.py` cover `hammond.scad` only, with a header comment
  saying so explicitly.
- **hammond.scad DOES genuinely share the glyph-placement pipeline** with
  the cylinder family, despite being a different form factor - its own
  v2 header comment (added during v2's OWN internal migration to the
  shared `lib/glyph_pipeline.scad`) proves the arc's Theta formula
  reduces algebraically to the shared lib's
  `(Angle_Half_Step+latitude)*Latitude_Int`, by treating the arc as a
  "fake cylinder" of diameter `2*Shuttle_Arc_Radius`. So
  `lib/hammond.py` reuses `cylinder_machine.place_on_cylinder`/
  `TextRing`/`CalibrationTextRing` (same as Mignon/Bennett/Helios) -
  confirmed empirically, not just by re-reading the comment: an early
  smoke test with the real numbers placed 90/90 characters with 0 skips.
- Body geometry (`ShuttleCylinder`/`AnvilShape`/`Rib`/`PinSupport`/
  `ShuttleTaper`/`Label`) shares nothing with `cylinder_machine.py` and is
  new code - `v2/lib/resin_support.scad`'s own header already flagged
  Hammond (and IBM) as keeping "their own angle-aware rod systems," not
  the shared placement layer.

**Resin support redesigned, not ported byte-for-byte** - explicit user
direction: reuse the existing shared rod shape
(`cylinder_machine._resin_rod()`, the same primitive Mignon/Bennett
already reuse) rather than porting Hammond's own v2 `ResinRod`/`RodTip`
(two independently-invented rod primitives), and treat the angled
reinforcement rod between adjacent support rods (gusseting/bracing) as
the one genuinely new piece. Added `sp.connecting_rod()` to
`lib/scad_primitives.py` (a hull of two spheres between arbitrary points,
ported from v2's `ConnectingRod()` at `v2/hammond.scad:419`) for this.
Placement itself (`lib/hammond.py`'s `ResinSupport()`) is a from-scratch
grid+raycast scheme against the real, already print-oriented mesh
(finds the lowest surface point per (X,Y) grid cell via
`trimesh`'s ray-mesh intersector, drops a rod there, braces grid
neighbors together with a gusset) rather than v2's own ~140-line,
8-tier `VertResinSupport2` - deliberately simpler, real v2 numbers
(`Resin_Support_Spacing`) still drive the grid pitch. Verified: 132 rods,
131 braced, on the real 90-character element.

**Shared-code fix required**: `build_glyph()`'s real platen-cutout step
(`lib/glyph_poc.py`) unconditionally computed
`platen_radius_real_mm = 1.0/(2.0*platen_radius_mm)` - a real division by
zero for Hammond, which strikes a flat anvil (`Skip_Platen_Cutout=true`
in v2) and so has no curved platen at all (`platen_diameter=0`,
`PLATEN_RADIUS_MM=0.0`, an intentional, not fallback, value - deriving it
from `1/platen_diameter` like every other machine would ALSO divide by
zero, so it's set directly in `configure()`). Fixed by adding a real
`if platen_radius_mm > 0` branch (skip building/subtracting the platen
cutting cylinder entirely, and skip the now-unnecessary block-margin
sizing) rather than trying to make 0 a numerically-safe magic value -
this is the exact v4 equivalent of v2/lib/glyph_pipeline.scad's own
`if (!_skipPlatenCutout) PlatenCutout(...)` conditional. Every existing
machine has a real platen (`platen_radius_mm>0`), so this is purely
additive - confirmed via the full 5-machine regression below.

**Shared-code promotion**: `lib/bennett.py`'s private `_build_text_string`
helper (whole-string flat text, halign=center/valign=baseline) was needed
identically for Hammond's `Label()` (two engraved strings,
`Shuttle_Label1`/`Shuttle_Label2`), so promoted it to
`cylinder_machine.build_text_string()` per CLAUDE.md's "extract shared
derivations instead of hand-copying" rule, and switched `lib/bennett.py`'s
`LabelText()` to call the shared version (removing the now-dead private
copy and its now-unused `freetype`/`build_flat_text`/
`get_glyph_contours_and_advance` imports).

**tune.py wiring**: added the `MACHINES` picker entry, `SECTIONS_BY_MACHINE
["hammond"]` (`Label` tab - matching Bennett's whole-string-label
convention, not `Logo` - plus `Quality`/`Resin`/`Element`, no `Gauge` -
Hammond has no Shaft Gauge Test either), and the matching `LABEL_FIELDS_
HAMMOND`/`QUALITY_FIELDS_HAMMOND`/`RESIN_FIELDS_HAMMOND`/`ELEMENT_FIELDS_
HAMMOND` tuples. Row-count handling in the Layout tab is already generic
(`n_rows = len(self.cfg["layout"]["baseline_row"])`, not a hardcoded `3`
anywhere), so no literal-count fixes were needed for Hammond's 3-row/
30-column layout, unlike Mignon's 7-row port. Found via a headless
`TuneApp(...).run_test()` smoke test (scratch config copy, per CLAUDE.md's
standing warning) that `layout.placement_map`/`latitude_columns`/
`cutout_row`/`modify_glyphs` are read unconditionally by tune.py even
though `lib/hammond.py` itself doesn't need them stored (it could compute
`PLACEMENT_MAP` from column count, and `CUTOUT_ROW` is dead/unused) -
added all four as literal YAML keys instead, matching how every other
machine stores them, per CLAUDE.md's "pick one convention" rule. Named
layout presets (`LAYOUT_PRESETS_BY_MACHINE`) not wired for Hammond - falls
back to `{}` (no crash, just no picker options) - Hammond's other 7 real
v2 layout presets (Normal Ideal/Math Universal/DVORAK/DHIATENSOR/Comic
Mono/Glagolitic/Attic) are listed in `config/hammond.yaml`'s header
comment but not yet selectable from the TUI.

**Verification**: ran the CLAUDE.md hard-gate command for all 5 existing
machines (blickensderfer/postal/mignon/bennett/helios) before and after -
byte-for-byte identical to the documented baselines (blickensderfer:
`verts=42618 faces=85408 ... volume=5666.804mm3`, matching the example in
CLAUDE.md itself). Hammond's own `ResinPrint`: `verts=47945 faces=96858
watertight=True winding_consistent=True is_volume=True volume=4292.355mm3`
(90/90 characters placed, 0 skipped), reproduced identically across two
separate runs.

**Deferred / open questions**:

- **`Groove=true`** (v2's alternate snap-fit/groove assembly variant -
  `GroovedShuttle()`/`Groove()`/`PinSupport2()`) is deferred entirely -
  `Groove=false` (the default, and the only variant `ResinPrint`'s real v2
  dispatch path exercises) is the only one ported.
- **`hammond_split.scad`** - a separate future port, per the audit above.
- No dedicated `Calibration`/named-layout-preset support in the TUI yet
  (see tune.py wiring note above).

## 30. Hammond follow-up: real relief-height bug, tune.py quit crash, config format bug

Three fixes found via actual user testing (real console preview of the
Hammond machine), not derivable from re-reading v2's source alone.

**Character relief height was wrong** (user-reported: "the letters aren't
protruding correctly"). Part 29 flagged this as an open question but
guessed it might be faithful to v2 as-is; it was not - measuring the
actual built mesh (bare shell's own outer radius vs. a real character's
outer radius with the part-29 numbers) showed characters landing at
37.94mm vs. the shell's own 37.935mm surface - essentially flush, ~0mm
of real relief. Root cause: `Letter_Placement_Protrusion=Shuttle_
Thickness` (v2:380, what part 29 passed as `place_on_cylinder`'s
`placement_protrusion`) is only where the character's BLOCK ROOT/anchor
sits, flush with the shell surface - v2's real extrude chain
(`Letter_Extrude_Offset=-.5`, `Letter_Extrude_Depth=Shuttle_Text_
Protrusion+.5`, v2:381-382) pushes the ink-bearing FRONT face an
*additional* `Shuttle_Text_Protrusion` (0.9mm) past that anchor - a
distinction part 29's algebraic re-derivation missed (it correctly
verified v2's real placement RADIUS matches, but conflated "root anchor"
with "visible front face"). Fixed by passing
`placement_protrusion=Shuttle_Thickness+Shuttle_Text_Protrusion` in both
`Additive()`/`CalibrationAdditive()`. Verified: a real character now
protrudes ~0.906mm past the shell surface (0.9mm expected). Full
`ResinPrint` rebuild still watertight/valid (volume rose slightly,
4292.355mm3 -> 4373.674mm3, matching the added ink-relief material).
**Lesson**: an algebraic re-derivation that "matches the real v2 value"
for one specific transform doesn't guarantee the SEMANTICS were mapped
correctly onto v4's differently-structured pipeline - visual/measured
verification against the actual built mesh is what actually caught this,
not another round of reading the same v2 source more carefully.

**tune.py crashed quitting from the machine picker** (`self.machine is
None`, `_save_before_exit()` unconditionally iterating `self.FIELDS`,
which is only set once a machine is loaded) - pre-existing bug, not
Hammond-specific, surfaced by testing the new picker entry. Fixed with an
early return when no machine is loaded (nothing to save).

**`config/hammond.yaml`'s `type_test.text`** used a plain quoted string
instead of the `|-` block-scalar format `patch_yaml_text_block()`
requires - fixed to match every other machine's config. A stale
`config/hammond.running.yaml` (bootstrapped from the master before this
fix landed, and never auto-resynced - a scratch file, gitignored) had to
be deleted by hand once for the running copy to pick up the corrected
master; not a recurring issue once regenerated.

**Also requested**: `resin.orientation` (`vertical`/`horizontal`) added to
`config/hammond.yaml` and wired into `lib/hammond.py`'s `ResinPrint()`
and `tune.py`'s `RESIN_FIELDS_HAMMOND`. "vertical" is v2's real
`VertResinPrint2` orientation (`rotate([0,-90,0])` then
`translate(-Z_Offset,0,-X_Max)`, unchanged from part 29); "horizontal" is
v2's real `HorizResinPrint` orientation - turned out to be simpler than
expected: NO rotation at all, just `translate(-Z_Offset,0,0)` (prints
flat, in the shuttle's own natural as-built frame - the arc's own X/Y/Z
axes are already the print axes, v2 doesn't reorient it for this path).
`ResinSupport()`'s grid+raycast+gusset scheme (part 29) needed zero
changes for this - it already builds against whatever oriented mesh it's
handed, so adding a second orientation was just a different pre-
transform, not new support-placement code, unlike a v2-faithful port
would have needed (v2's `HorizResinSupport2` is a completely separate
~90-line placement scheme from `VertResinSupport2`). Verified both:
vertical reproduces part 29/30's exact baseline (`volume=4373.674mm3`,
unchanged); horizontal is a new, different, valid, watertight result
(`verts=29375 faces=59046 volume=2645.954mm3`, 49 rods/41 braced - fewer
than vertical's 132/131, consistent with a flatter print needing less
support density).

**Still not started**: the `Groove`/rib assembly toggle (`RibAssembled()`
vs. `GroovedShuttle()` - almost certainly what "rendering with or without
the rib" means, `Groove=true` being the deferred variant from part 29).
Unlike the orientation toggle, this needs real NEW body-geometry code
(`Groove()`/`PinSupport2()`/`GroovedShuttle()`/`ResinChamfer()`, ported
from v2/hammond.scad following the same pattern as `Rib()`/
`PinSupport()`/`RibAssembled()`), not just a different transform - scoped
as its own follow-up, explicitly deferred again by user choice this
round (asked which of the two to do first; orientation was picked).

## 31. Hammond rib/groove assembly toggle (element.groove)

Ported v2's second, mutually-exclusive assembly mechanism - user
specifically wanted this next since it "also affects the resin support."

**New config**: `element.groove` (bool, default `false`) plus the real v2
values it needs - `shuttle_groove_nub_angle`, `groove_tab_width`,
`groove_opening_offset`, `support_groove_thickness` (derives
`Support_Groove_R` for `ResinChamfer()`). `Shuttle_Groove_Depth`/
`Shuttle_Groove_Nub_Size` are both `Shuttle_Thickness/2` (derived, not
independently tunable, matching v2:259-260). Confirmed `PinSupport2()`/
`Groove_Retaining_Pin_Diameter` are declared in v2 but never actually
called/referenced anywhere in `v2/hammond.scad` - dead code, not ported,
same treatment as `bennett.yaml`'s dead-param callouts.

**New lib/hammond.py functions**: `GrooveShape()` (a circumferential
snap-fit slot cut into the shell's inner surface via a disk+tab 2D union
minus 4 angled nub-cylinder cutouts, v2:484-500) and `ResinChamfer()` (a
small cone-frustum chamfer at the shell's bottom-inner edge, v2:789-792).
Naming note: the v2 module is literally called `Groove()`, but Python
has one namespace for module globals (unlike OpenSCAD's separate module/
variable namespaces) - naming the function `Groove()` would silently
shadow the `Groove` config boolean the moment `configure()` ran (hit this
live: `TypeError: 'bool' object is not callable` calling `hammond.
Groove()` after `configure()` had already overwritten it) - renamed to
`GrooveShape()` to avoid the collision.

`Additive()`/`CalibrationAdditive()` now branch on `Groove`: `false`
unions `RibAssembled()` onto the shell (unchanged, existing path);
`true` subtracts `GrooveShape()` and `ResinChamfer()` from the shell
instead, with no `RibAssembled()` at all - matching v2's real
`GroovedShuttle()` vs. `RibbedShuttle()` split exactly (mutually
exclusive assembly mechanisms, not a partial/additive variant).
`ShuttleTaper()`'s Z-depth also depends on `Groove` (v2:571's
`c=[Rib_Bottom_Z+z+(Groove?2:0), 10]`) - was hardcoded to the
`Groove=false` case in part 29, now reads the real flag.

**Resin support needed zero changes** - confirmed the user's own
intuition ("it also affects the resin support") is about the GEOMETRY
changing, not the support CODE: `ResinSupport()`'s grid+raycast+gusset
scheme (part 29) finds attachment points by ray-casting against whatever
mesh it's handed, so it automatically adapted to the groove variant's
different underlying shape with no changes needed - unlike v2, where
`HorizResinSupport2`/`VertResinSupport2` both have to explicitly branch
on `Groove` throughout their own hardcoded placement logic.

**Verified all 4 combinations** (groove x orientation) via `generate.py`,
all watertight/valid/is_volume=True:
- groove=false, vertical (existing baseline, unchanged): `volume=4373.674mm3`
- groove=true, vertical: `verts=45556 faces=92136 volume=4196.261mm3`
  (132 rods/131 braced - lower volume than the rib variant, consistent
  with removing the rib+pin material)
- groove=false, horizontal (from part 30, unchanged)
- groove=true, horizontal: `verts=17197 faces=34406 volume=1887.059mm3`
  (only 8 rods/0 braced - sparser support grid than the other 3 combos,
  worth a closer look if this combination is used for a real print, but
  not a crash/invalid-geometry issue)

**tune.py**: added `groove` (bool) plus the 4 new real-value fields to
`ELEMENT_FIELDS_HAMMOND`. Headless `TuneApp(...).run_test()` smoke test
(scratch config, per standing warning) confirms compose/save/quit all
still work (70 fields now, up from 64).

## 32. Connecting-rod bracing pattern corrected; resin.orientation is a dropdown

Two user-reported fixes.

**Connecting rods didn't match v2's real pattern.** Part 29's
`ResinSupport()` braced grid-adjacent rods in BOTH directions (i+1,j AND
i,j+1) with a level, tip-to-tip connection. Re-checked every one of v2's
own `ConnectingRod()` call sites (v2:627,638,643-658,671,683) - all of
them connect two points sharing the SAME angular/lateral position but
DIFFERENT longitudinal position (never laterally between two different
angular rows), and always drop the brace a few mm below the rod's own
tip contact point (e.g. v2:671's `h-1 -> h-4`) rather than connecting
flush at the very top. Fixed `ResinSupport()` to match both properties:
braces only along the i (longitudinal) grid axis now, and each endpoint
drops by a fixed `brace_drop=1.5mm` below its own tip (clamped to
`Resin_Min_Rod_Height`) before connecting - a real diagonal brace
supporting the rod's upper region, not a flat cross-tie at the top.

Verified all 4 groove x orientation combinations still watertight/valid
after the change (volumes shifted slightly from part 31's numbers, as
expected - roughly half as much bracing material now that only one
direction is braced): groove=false/vertical `volume=4301.835mm3`,
groove=true/vertical `volume=4141.871mm3`, groove=false/horizontal
`volume=2612.998mm3`, groove=true/horizontal unchanged at
`volume=1887.059mm3` (0 braced either way for that combination, see part
31's open item about its sparse grid).

**`resin.orientation` is now a dropdown**, not a free-text field -
mirrors the existing `elif key == "mode":` special-case in
`_compose_section_tab` (the only other string-enum field, `alignment.
mode`) rather than inventing a new generic mechanism - `_collect_values`/
`_load_current` already read/write `Select`/`Input` widgets identically
via `.value`, so no changes needed there.

## 33. Hammond resin support: real VertResinSupport2 port (abandoned the redesign)

Part 32's fix wasn't enough - user reported the connecting rods were
"still incorrect": wrong direction/orientation, not attached correctly,
wrong placement, all at once. Rather than guess a fourth time, re-pulled
the exact v2 source (v2/hammond.scad:596-735) and did a real, literal
port of `VertResinSupport2()` for the "vertical" orientation - same
tiers, same coordinates, same `ConnectingRod`/`ResinRod` call sites -
replacing the grid+raycast redesign entirely for that case (parts 29-32's
approach is kept ONLY as `_ResinSupportRaycastGrid()`, now used
exclusively for "horizontal", since v2's own real horizontal-orientation
support scheme, `HorizResinSupport2`, is a separate ~90-line algorithm
never in scope to port).

**Key derivation, worth recording since it wasn't obvious from the code
alone**: v2's own `ResinRod(h1,r1,r2,h2,r3)` has its RAFT at local z=0
and TIP at local z=h1 (confirmed by reading its full body -
`cylinder(h=h1-1,r=r1)` from z=0, tip taper at z=[h1-1,h1]) - a
DIFFERENT convention from the shared `cylinder_machine._resin_rod(h)`,
whose raft sits at z=-(Resin_Min_Rod_Height+Resin_Raft_Thickness) and tip
near z=h. `VertResinSupport2()` wraps its whole union in
`translate([0,0,-Resin_Support_Min_Height-Resin_Support_Base_Thickness])`
(v2:611) to place it correctly relative to the body. Reconciled by
re-basing every `ResinRod` call's h1 through a local `_rod()` helper
(`h = h1 - (Resin_Min_Rod_Height+Resin_Raft_Thickness)` before calling
the shared primitive - the shared primitive's own raft-position
convention already IS that same shift, so this reproduces v2's real
final world position without applying the outer translate twice) and
every `ConnectingRod` endpoint through `_crod()` (which DOES subtract the
shift explicitly, since `sp.connecting_rod` has no such built-in
convention to double up with).

**Real values added**: `resin.edge_gap` (`Resin_Support_Edge_Gap`, v2:314)
and `Inner_Arc_Intercept`/`Outer_Arc_Intercept` (v2:343-344, derived in
`configure()`) - both needed by the "Under Rib - Rib Thickness on Edges"
tier, neither previously ported since the redesign didn't need them.

**Simplification kept** (not what was reported wrong): v2's `ResinRod`
tip radius (`r2`) is two-tier - `Resin_Support_Contact_Diameter` for most
rods, `Resin_Support_Contact_Diameter_Rib` for the "under rib" tiers -
collapsed to the single configured `Resin_Tip_OD` for every rod, since
the shared `cylinder_machine._resin_rod()` reads that from config rather
than taking a per-call override. A genuinely minor cosmetic difference
(0.4mm vs an unported ~0.2mm tip point), not a placement/structural one.

**Verified** all 3 affected combinations via `generate.py` (horizontal
was untouched by this change, reproduces part 32's exact
`volume=2612.998mm3` baseline):
- groove=false, vertical: `verts=85097 faces=171186 volume=4765.334mm3`
  (1300 parts - watertight/winding_consistent/is_volume=True)
- groove=true, vertical: `verts=65166 faces=131000 volume=4275.807mm3`
  (924 parts - fewer tiers, "Under Rib Supports"/"Under Rib - Rib
  Thickness on Edges" are both `if (Groove==false)` in v2, faithfully
  skipped here too)
- groove=false, horizontal: unchanged (`volume=2612.998mm3`, raycast
  fallback)

Also spot-checked (outside the STL export) that the oriented body and
the new `ResinSupport()` land in physically sensible relative positions
without any extra normalization step: body's own lowest point sits at
world Z≈0 (matching v2's real design - no artificial "shift to
buildplate" hack needed here, unlike the horizontal raycast fallback,
which has no analytic reference and still needs one).

`tune.py`: added `edge_gap` to `RESIN_FIELDS_HAMMOND` (71 fields now, up
from 70). Headless smoke test confirms compose/save/quit still work.

## 34. Hammond: groove dropdown, Math layout preset, auto-derived Is_Math

Three more requests in one pass: the groove checkbox should be a
dropdown too, there's a "Math shuttle" layout variant to wire up (check
v1, might not be in v2), and `Is_Math` should auto-follow row count
instead of being a separate toggle.

**Checked v1 first, per the request** -
`v1/Hammond/HammondShuttle.scad` (the pre-v2-migration original) has the
exact same `Layouts`/`IsMath`/`Math_U` system v2 already has (confirmed
line-by-line: same 4-row `Math_U` array, same `IsMath=search(...,
"Math")` derivation) - nothing extra hiding in v1. "Math Universal"
(`LAYOUTS[2]` in `v2/lib/layouts/hammond_layouts.scad`) is the only real
"math shuttle" variant, and it's the one now wired up.

**`Is_Math` is now derived, not a toggle** - `element.is_math` removed
from `config/hammond.yaml` entirely; `lib/hammond.py`'s `configure()`
computes `Is_Math = len(cfg["layout"]["rows"]) == 4` instead (Math
Universal is the only 4-row preset; everything else is 3). Removed the
now-dead `is_math` field from `ELEMENT_FIELDS_HAMMOND` and the
now-unused `baseline_row_math` YAML key (its real value, -9.89, moved to
the preset data below instead of sitting unused in the master config).

**Two layout presets added** (`LAYOUT_PRESETS_HAMMOND` in `tune.py`):
"Normal Universal" (the existing default, 3 rows) and "Math Universal"
(4 rows, `v2/lib/layouts/hammond_layouts.scad`'s `Math_U`). This is the
first machine whose presets differ in ROW COUNT, which the existing
preset-picker infrastructure wasn't fully built for - `patch_yaml_rows`
itself was already "row-count-agnostic" (writes however many rows it's
given), but two real problems surfaced from actually testing the switch,
not just reading the code:

1. **`baseline_row`/`cutout_row` also need to grow to 4 entries** when
   Math Universal is selected (`TextRing`'s `n_rows = len(reference_
   baseline_row)` would otherwise stay at 3, silently dropping the 4th
   row's characters). No existing mechanism resizes these - the per-row
   `BASELINE_CUTOUT_KEYS` Input widgets are a fixed set sized once at
   `_load_machine()` time. Added `LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE`
   (keyed by machine, then preset name - only Hammond has an entry, since
   no other machine's presets vary in row count) plus a new
   `patch_yaml_inline_list()` (replaces a whole `key: [...]` array,
   unlike `patch_yaml_list_item` which only patches one element) -
   applied in `_save_to_yaml` right after `patch_yaml_rows`, overwriting
   whatever the (now-stale-length) `BASELINE_CUTOUT_KEYS` loop had just
   written.
2. **Selecting a longer preset crashed immediately** - `on_select_changed`
   (and `on_switch_changed`, and `_refresh_widgets_from_cfg`) all update
   per-row preview/edit widgets by iterating `range(len(new_rows))` and
   querying `#layout-original-row-{i}`/`#layout-custom-row-{i}` - fine
   when every preset has the same row count (true for every other
   machine), but Math Universal's 4th row has no matching widget (the
   fixed set from compose() time only has 3) - immediate `NoMatches` on
   selecting the dropdown value. Fixed with a new `_update_row_widget()`
   helper (query + no-op if missing, used at all 4 call sites) and a
   `self.inputs.get()` guard in `_refresh_widgets_from_cfg`'s
   `baseline_row`/`cutout_row` widget-sync loop (a plain dict lookup,
   raises `KeyError` not `NoMatches`, needed the same fix for the same
   reason). The read-only preview/edit widgets for a 4th row don't
   *appear* until a recompose (switching machine and back, or
   restarting) - a known, accepted UX gap, not a crash.

**`element.groove` is now a dropdown** ("Rib" / "No Rib (Groove)"),
matching the `mode`/`orientation` pattern - added as a `key == "groove"`
special case checked BEFORE the generic `typ is bool` branch (order
matters in the if/elif chain; `groove`'s type is still `bool`, so the
generic branch would otherwise catch it first and render a Switch).
`_collect_values`/`_load_current` needed no changes - both already treat
Select and Switch widgets identically via `.value` for a `bool`-typed
field.

**Verified**: `Is_Math` auto-derivation (3-row config -> `False`/
`Shuttle_Height=16.6`; 4-row config -> `True`/`Shuttle_Height=21.24`);
full `generate.py` build on a hand-built 4-row Math config (120
characters = 4x30, 0 skipped, `ResinSupport: 1852 parts`,
`volume=5765.334mm3`, watertight/winding_consistent/is_volume=True);
Normal Universal regression unchanged (`volume=4765.334mm3`); a full
headless `TuneApp` cycle - switch to Math Universal via the dropdown,
save, confirm `rows`/`baseline_row`/`cutout_row` all landed correctly in
the RUNNING config (not the master - tripped over this distinction
myself mid-debugging) - then a real `generate.py` build from that exact
tune.py-written config reproduces the same `volume=5765.334mm3`
byte-for-byte; groove dropdown save round-trips correctly
(`groove: true` written and read back).

## 35. Hammond: real HorizGroovedResin3 port; fixed a wrong rod-height clamp

Two bugs reported after visual inspection of an actual render - neither
was visible from the numbers alone (both builds were watertight/valid
throughout).

**"The resin rods in horizontal position are totally fucked up, need to
use cut groove."** Re-read v2's real `ResinPrint()` dispatcher (v2:1060-
1073) precisely for the first time - it only ever calls two functions:
`VertResinPrint2()` for `Resin_Support_Orientation==0` and
`HorizGroovedResin3()` for `==1`. `HorizResinPrint`/`HorizResinSupport2`/
`HorizGroovedResin`/`HorizGroovedResin2` (the functions parts 29-32's
raycast fallback was modeled loosely on/named after) are ALL
unreferenced legacy code in v2, never actually called by anything. The
real horizontal support (`HorizGroovedResin3`, v2:1006-1021) is a
completely different architecture from `VertResinSupport2` - not
individual rods at all, but a single swept, perforated breakaway-groove
RING (`Resin2Profile()`, a wall-hugging trough cross-section with two
circular "cut groove" perforations at its top corners, revolved +-60
degrees around the shuttle's real angular extent). Ported faithfully:
added `sp.revolve_polygon_partial(profile, start_deg, end_deg, sections)`
to `scad_primitives.py` (a real `rotate_extrude(angle=)` equivalent -
built as a full `revolve_polygon()` intersected with a wedge solid
spanning the angle range, reusing the already-tested full-revolve code
and a real manifold boolean instead of hand-triangulating two end caps),
then `HorizGroovedResinSupport()` (the swept ring minus the two
perforation cuts minus a shifted `ShuttleTaper()`, matching v2 exactly).

Also discovered while re-reading the dispatcher: `HorizGroovedResin3`
**always** calls `GroovedShuttle()` regardless of the `Groove` config
value (v2:1006-1021 never checks `Groove` at all, unlike
`VertResinPrint2` which does) - a real, deliberate v2 restriction: this
orientation is only ever paired with the snap-fit groove body. Added
`force_groove` to `Additive()`/`FullElement()`/`Subtractive()`/
`ShuttleTaper()` (threaded all the way through, since `ShuttleTaper()`'s
own Groove-conditional taper depth needs to match the forced body too -
found this by comparing `Subtractive` vertex counts between a
`groove: false` config and a `groove: true` config with orientation
forced to horizontal, which should be identical and initially weren't).
Also fixed: when resin support is off, v2 returns the plain body for
EITHER orientation with NO reorientation at all (v2:1067-1072) - `Resin
Print()` previously still applied the vertical rotate/translate in that
case; now matches v2 exactly.

**"There's a broken resin rod in the vertical direction... missing the
base of the rod."** Traced to a defensive clamp in part 33's port
(`_rod()`'s `h = max(h, -Resin_Raft_Thickness + 0.05)`), added out of
caution without checking whether it was ever actually needed. Computed
the real degenerate threshold (where `cylinder_machine._resin_rod`'s tip
sphere would invert past its base sphere) directly from its own tip_z/
lower_z formulas: around h=-2.58 with this config's default values. The
smallest real h1 anywhere in the port (`Outer Edge Supports`' `h_edge2 =
Resin_Raft_Thickness`, giving `h=-Resin_Min_Rod_Height=-2.0`) is well
above that threshold - already valid, non-degenerate - but the clamp's
own floor (-1.45) was HIGHER than -2.0, so it silently pulled that one
rod 0.55mm out of its correct position every time. v2 itself has no such
guard on `ResinRod()` either. Removed the clamp entirely rather than
tightening the threshold - checked all constant-h1 call sites
algebraically first to confirm none of them actually need one.

**Verified**: all 4 groove x orientation combinations rebuilt and
watertight/valid. Horizontal now correctly forces the grooved body
regardless of config (`groove: false` and `groove: true` configs produce
byte-identical `verts=21040 faces=42080 volume=2339.334mm3` when
orientation is horizontal - confirming the force_groove fix). Vertical
groove=false with the clamp removed: `volume=4765.334mm3` (topologically
different vert/face count from before the fix - 85096/171184 vs.
85097/171186 - confirming the affected rod's geometry actually changed,
not just cosmetically identical). Math Universal layout regression
unchanged (`volume=5765.334mm3`). Spot-checked Blickensderfer (the only
other machine using `scad_primitives.py`, which gained the new
`revolve_polygon_partial` function) - unaffected, exact baseline match.

## 36. Hammond: horizontal-ribbed support (real HorizResinSupport2 port) + FDM part export targets

Two more requests: horizontal orientation shouldn't be forced to the
grooved body if the ribbed one can be "properly supported" instead, and
a Build-tab dropdown for exporting the shuttle and rib as separate FDM
parts (no resin supports needed for those).

**Un-forced Groove for horizontal, ported the real ribbed-horizontal
support.** Part 35 found `HorizGroovedResin3` always uses
`GroovedShuttle()` and concluded (wrongly) that horizontal orientation
was ONLY ever paired with the groove body in v2. The user pointed at
`HorizResinPrint2()`/`HorizResinSupport2()` (v2:952-963, 864-950) -
confirmed identical in `v1/Hammond/HammondShuttle.scad` too (only
casing/whitespace differ from v2, no logic changes) - real, complete,
carefully-built functions supporting the RIBBED body horizontally: along
the rib's own back edge and around the center drive-pin hole, exactly
matching the user's own description before I'd re-read the source. v2's
`ResinPrint()` dispatcher (v2:1060-1073) only calls `VertResinPrint2`/
`HorizGroovedResin3` directly, but that doesn't mean the other Horiz*
functions are dead - `HorizResinPrint2`/`HorizResinSupport2` are just not
wired into that particular dispatcher's two `Resin_Support_Orientation`
values in the exported customizer, unlike the genuinely-unreferenced
`HorizResinPrint`/`HorizGroovedResin`/`HorizGroovedResin2`.

`ResinPrint()`'s horizontal branch now dispatches on `Groove` (same as
vertical, no longer forced): `Groove=true` -> `HorizGroovedResinSupport()`
(part 35, unchanged); `Groove=false` -> new `HorizRibbedResinSupport()`.
Ported the real tiers faithfully: Outer Supports (23 angular positions
around both wall-adjacent radii), thetamax/taper-step edge supports,
`Inner_Arc_Intercept` supports, the "under Pinhole" 4-rod cross pattern,
three dense angular fan patterns, and the theta-dependent Under Rib -
Outer/Radius/Center tiers (the only ones that actually vary per
iteration - the rest are loop-invariant in v2 itself, since neither the
pinhole block nor the fans reference the outer loop's `y`/`theta` at
all, just shadow the name - hoisted out and built once here, same
optimization as part 33's "at the taper" block). Rod shape is a NEW
`_rod2()` helper wrapping the shared `cylinder_machine._resin_rod()` -
`ResinRod2(h)` is a THIRD bespoke v2 rod primitive (distinct from both
`ResinRod`/part 29's `RodTip`), with its own tip-position convention
(`h - Resin_Tip_OD/2 + Tip_Interference`, not `h` directly) - added the
real `Tip_Interference` (v2:324, 1.2mm - a genuine tip overlap/
interference-fit depth, not negligible) and `Shuttle_Pin_Support_
Height2` (v2:236 - otherwise only used by the dead `PinSupport2()`, but
real and needed here) to `config/hammond.yaml`.

Verified: `HorizRibbedResinSupport()` standalone (watertight,
`volume=1015.11mm3`); full `generate.py` build, horizontal+groove=false
(`verts=36310 faces=72864 volume=2961.561mm3`, watertight/valid,
`Additive: verts=13820` confirming the RIBBED body is used, not forced-
groove); horizontal+groove=true and vertical both reproduce their exact
pre-this-part baselines unchanged.

**FDM part-export targets** ("it does not have to be grooved if
properly supported... will be printed with FDM so no need for supports
here" - a separate, simpler ask on top of the above). Added `--hammond-
part {shuttle_minus_rib,shuttle_plus_rib,rib_only}` to `generate.py` -
plain geometry exports, no resin-print orientation/support machinery at
all (FDM's own slicer handles supports). `shuttle_minus_rib`/
`shuttle_plus_rib` are `FullElement(force_groove=True/False)` (already
existed via part 35's `force_groove` param); `rib_only` is a new
`hammond.RibOnly()` (just `RibAssembled()` alone, meant to be printed
separately and glued to a `shuttle_minus_rib` shell afterward). Wired
into `tune.py`'s Build tab as 3 more `build.target` dropdown options,
gated on `self.machine == "hammond"` (matching the existing `has_gauge`
pattern) - selecting one of these ignores the Resin supports checkbox
entirely (documented in a new help `Static`), since `generate.py`'s
`--hammond-part` branch runs before the resin dispatch. Verified all 3
targets individually (watertight/valid: `rib_only` `volume=128.927mm3`,
`shuttle_minus_rib` `volume=1810.135mm3`, `shuttle_plus_rib`
`volume=1960.523mm3`) and via a full headless `TuneApp` cycle
(select `rib_only`, save, confirm the constructed subprocess command is
`generate.py ... --hammond-part rib_only`, then actually ran that exact
command).

## Resuming later

1. **Hammond follow-up work (parts 30-31)**: (a) DONE - `resin.
   orientation` (vertical/horizontal print); (b) DONE - `element.groove`
   (rib vs. snap-fit assembly, part 31); (c) the groove+horizontal
   combination's sparse resin-support grid (8 rods, 0 braced) is worth
   revisiting if that combination is actually used for a real print -
   may need a finer grid pitch for very flat/low-relief footprints;
   (d) go through `tune.py`'s Hammond tabs field-by-field against
   `config/hammond.yaml` for anything still missing (named layout
   presets, Calibration wiring - see part 29's open items).
2. **Hammond_split.scad and IBM are next** - `hammond.scad` itself is
   done (part 29). `hammond_split.scad` turned out to share almost
   nothing with `hammond.scad` (see part 29's audit) - treat it as its
   own from-scratch port, not a quick follow-on. IBM (spherical) is still
   fully unstarted.
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
