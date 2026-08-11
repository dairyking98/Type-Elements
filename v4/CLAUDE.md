# v4 conventions

## Workflow - commit directly to main by default

For routine changes in this repo, edit files directly in the existing
checkout and commit straight to `main` - no feature branch, no worktree,
no PR, unless explicitly asked for one (a large/risky change the user
wants reviewed separately, or an explicit "put this on a branch"/"open a
PR"). `.claude/settings.json`'s `worktree.bgIsolation: "none"` disables
the harness's default enforced-worktree-isolation behavior for
background sessions in this repo specifically, so this applies to fresh
agent sessions here too, not just interactive ones - don't reach for
`EnterWorktree`/branch-and-PR as the default move just because that's
the harness's out-of-the-box behavior elsewhere.

## OpenSCAD binary

Real OpenSCAD (not just v2 `.scad` source) is available for direct
cross-checks against v4's Python geometry, e.g. rendering a `text()`
glyph and diffing its STL bounding box against v4's own output for the
same font/size. The installed binary is the snap `openscad-nightly`
(`/snap/bin/openscad-nightly`), not `openscad` - there is no plain
`openscad` on PATH, so scripts/commands that shell out to OpenSCAD must
call `openscad-nightly` explicitly.

## Before writing new code

Search `lib/cylinder_machine.py` (shared across cylinder machines) and the
target machine's own module (`lib/blickensderfer.py`, `lib/postal.py`,
`lib/mignon.py`, `lib/bennett.py`, `lib/glyph_poc.py`,
`lib/scad_primitives.py`, `lib/resin_support.py`, `lib/build_log.py`) for
an existing function that already does what you're about to write before
adding a new one. Duplicated logic is how machines drift out of sync
silently - see "Porting a new machine" below for the same failure mode at
the machine-port level. `lib/build_log.py` specifically: if you're about
to `print(f"...verts=...watertight=...")` or a per-item `"[n/total] ..."`
progress line by hand, stop - see the "TUI (tune.py)" section below for
why both are load-bearing conventions, not style choices, and what
happens when a new machine's code doesn't use them (`SESSION_LOG.md`
parts 61-63).

## Geometry invariants

These are hard rules, not stylistic preferences - each one maps to a
confirmed, previously-shipped bug (see `README.md`/`SESSION_LOG.md` at
the cited section for the full incident).

- **Real machine numbers (dimensions, tolerances, offsets) live in config
  YAML, never hardcoded in code, no matter which machine.** This also
  covers facet-count/resolution constants (circle segments, revolve
  sections, etc.), not just physical dimensions - a hardcoded
  `resolution=6`/`sections=60` briefly shipped in Helios's
  `HollowingElement()` to route around an unrelated diagnostic's cost
  (see `SESSION_LOG.md` parts 26-27), which is exactly the kind of
  number this rule means to keep out of code: if a real reason exists to
  tune a facet count, it belongs in `config/<machine>.yaml`'s `quality:`
  section like every other `*_fn` knob; if there's no real reason (an
  invisible/internal feature that doesn't need its own tunable), don't
  invent a special-cased number for it at all - reuse the machine's
  existing `Surface_Fn`/`Cyl_Fn`/etc. This does NOT mean a new machine is
  expected to be config-only, though - that
  was true for Postal-following-Blickensderfer specifically (they share
  everything except the drive-pin trio: `README.md` "Multiple
  machines"), but Mignon diverges from `cylinder_machine.py` "across
  essentially the whole body-construction half of the pipeline" (its own
  module docstring) and Bennett needed its own `tune.py` tabs/layouts/
  field-lists. If the physical geometry genuinely differs, real new lib
  code is expected and correct - just keep the numeric constants for it
  in that machine's YAML. See "Porting a new machine" below.
- **Assembly booleans go through real `manifold3d`
  (`sp.union_all()`/`Manifold.batch_boolean()`), never
  `trimesh.util.concatenate()`.** Concatenate merges overlapping vertex/
  face arrays with no boolean resolution - confirmed via a 1148mm3
  double-counted-overlap bug. (`README.md` intro; `SESSION_LOG.md` part
  5.5)
- **The draft taper stays a real Minkowski sum
  (`manifold3d.Manifold.minkowski_sum`), never a per-vertex offset or
  OpenSCAD's `minkowski()`.** Per-vertex offsets can silently
  self-intersect on narrow/concave geometry; OpenSCAD's version is too
  slow at this scale. (`README.md` intro; `SESSION_LOG.md` parts 1-4)
- **Curvature/warp (e.g. the platen cutout) is applied to the base solid
  BEFORE the Minkowski sum, never patched onto the swept result after.**
  The cone's draft angle is only valid for the shape it was actually
  summed with; patching after leaves walls built as if the tip were
  flat. This lesson was learned twice. (`README.md` "Real platen
  cutout"; `SESSION_LOG.md` parts 5 and 6)
- **Glyph outline sampling (`glyph_poc.contour_to_points()`) is adaptive
  flatness-tolerance-based (recursive de Casteljau Bezier subdivision,
  `flatten_quadratic`/`flatten_cubic`), never a fixed points-per-mm
  rate.** Straight on-curve segments get ZERO subdivision (already flat);
  curves get exactly as many points as their OWN curvature needs at
  `flatness_tolerance_mm`. A fixed rate (the old `points_per_mm`,
  replaced fleet-wide) subdivided straight strokes at the same density as
  curves - measured leaving 46-71% of a straight-stroke glyph's points
  geometrically redundant, and directly inflating Minkowski cost (which
  scales with the product of the two operands' face counts). Confirmed
  1.3x-4.5x real build-time reduction with no correctness loss (volumes
  match the old fixed-rate output to within 0.03-1% across both
  quadratic/TrueType and cubic/CFF fonts). The platen cutout itself
  stays a real boolean cylinder subtraction (previous bullet) - a
  separate attempt to realize it as a per-vertex height-field instead
  was tried and abandoned (more post-Minkowski faces, not fewer; see
  `SESSION_LOG.md`).
- **No manual Y-breakpoint insertion is needed (and none exists) to help
  the real platen boolean cut along a long, adaptively-unsubdivided
  straight edge (e.g. 'd'/'l'/'k's stem) - the real boolean handles it
  correctly on its own.** A "sail/spike" artifact was suspected here
  mid-session (a triangle appearing to span nearly a character's full
  height and depth on AverageMono's 'd'/'p'/'k'/'N'/'V') and a shared-
  Y-breakpoint mechanism (matched to the platen cylinder's own
  `platen_fn` facet step) was built, then REMOVED again after two
  things became clear: (1) it introduced its own new defect - a fan of
  degenerate thin triangles in the flat 2D cap triangulation wherever a
  breakpoint-dense edge met an already-dense curve region like a serif,
  since inserting a boundary vertex doesn't constrain the interior
  triangulation to actually connect it across the stroke (no "rung"),
  leaving Delaunay to improvise and do it badly under mismatched point
  density; and (2) once checked with a properly SIZE-NORMALIZED
  metric (any face may not exceed 1.5x that character's own bounding-
  box diagonal, not an absolute mm threshold), the original "sail"
  concern was a false positive - confirmed 0 faces exceed that bound
  across every character in both AverageMono (cylinder family,
  `glyph_poc.build_glyph`) and FreeSans (spherical family,
  `spherical_machine.SingleMinkowskiChar`), all watertight/valid,
  neither one needing any breakpoint help. The real boolean cut was
  directly observed subdividing a stem's wall finely wherever the
  platen curve actually changes, and leaving it as one larger (but
  still in-silhouette, still flat, still correct) facet wherever the
  curve doesn't - exactly the adaptive behavior wanted, for free, with
  no pre-conditioning of the input contour.
- **`Manifold.simplify()`/`simplify_tolerance_mm` do not exist anywhere in
  the glyph pipeline, fleet-wide - no config key, no `tune.py` field, no
  function parameter, cylinder and spherical both.** The one place the
  name still appears is `lib/heightfield_poc.py`, the abandoned
  height-field experiment described at the end of this bullet - it is a
  standalone POC that nothing imports and that `generate.py`/`tune.py`
  never reach, so it is outside "the glyph pipeline" rather than an
  exception to the rule; don't treat its surviving
  `simplify_tolerance_mm` parameter as precedent for reintroducing one.
  This
  went through two stages: first disabled (every call site commented
  out but the parameter still threaded through every config/signature,
  in case the regression below reappeared), later fully deleted per
  explicit user direction once that risk was confirmed gone in practice
  (re-verified: deletion is a pure no-op - every affected config's
  `--no-minkowski` gate output is byte-identical before/after, since
  every real call site was already disabled). What used to call it (now
  just doesn't): `glyph_poc.build_glyph()` (both its no-Minkowski
  preview path and its post-Minkowski path),
  `glyph_poc.build_flat_text_drafted()` (post-Minkowski),
  `spherical_machine.SingleMinkowskiChar()` (BOTH its pre-Minkowski and
  post-Minkowski calls), `hammond_split._letter_text_drafted()` (post-
  Minkowski). The preview-path call was independently confirmed to
  reintroduce a sail/spike artifact on top of an otherwise-clean platen-
  cut mesh (worst offending triangle dropped from 2.10mm to 1.37mm the
  instant that one call was skipped, no other change) - whatever
  `simplify()` was doing with this much sparser adaptive-contour input,
  it wasn't safe anywhere, not just after Minkowski. `spherical_
  machine`'s pre-Minkowski call had a real, DIFFERENT, previously-
  documented reason to exist (552x speedup avoiding a 2206s-per-
  character regression on Alma Mono 'M', by shrinking `minkowski_sum`'s
  INPUT face count, not cleaning its output) - disabled anyway per
  explicit user direction ("disable all simplification"), then directly
  re-tested against that exact regression case: the same character/font/
  real-Minkowski build completed in 5.75s with zero `simplify()` calls
  anywhere. The adaptive contour tracing (this file's earlier bullet)
  already fixes the root cause that call was compensating for - a
  bloated, CSG-noise-heavy boolean-cut mesh from the old fixed-rate
  `points_per_mm` scheme no longer exists to explode through Minkowski
  in the first place, so the workaround for it is no longer needed
  either. User-confirmed in real use: full-font builds (all characters,
  real Minkowski) complete in under a minute at `flatness_tolerance_mm
  =0.01`. If a future regression like the 552x case above ever
  reappears, re-add `Manifold.simplify()` as a fresh, deliberate change -
  don't expect to find it lying around commented out anymore.
- **`build_glyph()` (struck characters) mirrors X after `x_shift`.
  `build_flat_text()`/`LogoText`/Type Test never mirror.** A struck
  element is a mirror image of the printed glyph, like a stamp - this
  shipped as a real bug once. (`README.md` "Character mirroring";
  `SESSION_LOG.md` part 7)
- **Reconstructing a `trimesh.Trimesh` from already-placed
  vertices/faces must pass `process=False`.** Default `process=True`
  silently re-runs vertex merging and corrupts valid topology, even with
  an identity transform. (`README.md` "place_on_cylinder()"; see
  `lib/cylinder_machine.py`, `lib/scad_primitives.py`, `lib/glyph_poc.py`
  for the existing correct call sites)
- **Calibration's reference baseline/cutout always comes from the fixed
  MASTER config, never the running config being edited.** Without a
  fixed reference, dialing in a value from one calibration pass shifts
  where the next pass centers its sweep - chasing an already-moving
  target instead of converging. `tune.py` always passes the master
  config here; `CalibrationTextRing` prints which reference arrays it
  used, so this is never ambiguous from the log. (`README.md`
  "Calibration")
- **Keep the five `quality.*_fn` facet-count knobs independent - don't
  merge them into one catch-all.** Per explicit user direction; each
  covers a distinct surface family. (`README.md` "Facet-count knobs")
  The five are `body_fn`/`cyl_fn`/`surface_fn`/`platen_fn`/
  `minkowski_fn`. Counting `quality.*_fn` keys in a config turns up a
  SIXTH, `groove_fn` - that one is deliberately not in the five because
  it isn't a facet count at all (CoreGrooves twist angular sampling, as
  its own config comment says); it's independent for the same reason,
  just not a member of that family.
- **`layout.latitude_columns` must stay in sync with `placement_map`/the
  physical layout.** It's intentionally not exposed in the Layout tab's
  named-preset picker - edit it directly in the YAML only if you really
  mean to change it. (`tune.py`, `_compose_layout_tab`)

## Porting a new machine

### Machine taxonomy - don't assume "cylindrical" implies "shares code"

- **Physical form and code-sharing are two separate axes - check both,
  don't infer one from the other.** Ported so far: Blickensderfer,
  Postal, Mignon, Bennett, Helios Klimax, Hammond, Hammond Split,
  IBM/Selectric (split into 3 machines - `selectric12`, `selectric3`,
  `selectric_composer` - sharing `lib/spherical_machine.py`; see below),
  and the standalone Type Slug family (`type_slug`/`vogue_slug`/
  `gauge_slug` sharing `lib/wing_slug.py`, `oliver_slug`/`lumi_slug`
  sharing `lib/box_slug.py` - ground truth v1, not v2, since this family
  was never carried into v2 at all; see `SESSION_LOG.md` part 75).
  Nothing else remains on the roadmap. All of Blickensderfer/Postal/
  Mignon/Bennett/Helios are cylindrical in outward form, but:
  - **Blickensderfer and Postal are near-twins** - they diverge in code
    only at the "drive pin trio" (`HollowSpace`/`DrivePin`/
    `ResinSupport`); everything else lives in `lib/cylinder_machine.py`
    and is genuinely shared. (`README.md` "Multiple machines")
  - **Mignon and Bennett are cylindrical in form only** - each diverges
    from `cylinder_machine.py` across most of the body-construction
    pipeline (Mignon's own module docstring: "essentially the whole
    body-construction half"; Bennett needed its own `tune.py` tabs/
    layouts/field-lists). Being cylindrical did not predict how much
    they could actually reuse.
  - Treat Helios the same way Mignon/Bennett were treated - diff its
    real v2 source against `cylinder_machine.py` function-by-function
    before assuming reuse, and don't assume it behaves like
    Blickensderfer/Postal just because it's cylindrical too.
  - **Hammond, Hammond Split, and IBM/Selectric are a different form
    factor entirely** - `cylinder_machine.py` was not the starting point
    for any of them. Hammond and Hammond Split themselves turned out to
    share almost nothing with EACH OTHER either, despite the shared name -
    Hammond genuinely reuses `cylinder_machine.place_on_cylinder`/
    `TextRing` for glyph placement (its arc reduces algebraically to a
    "fake cylinder" - see `lib/hammond.py`'s module docstring), while
    Hammond Split builds its own from-scratch glyph pipeline entirely and
    has a third, independent resin-support scheme (see `lib/hammond_
    split.py`'s module docstring). IBM/Selectric turned out to share
    nothing with the cylinder family either (verified function-by-function
    against `v2/ibm.scad` before writing anything, per this section's own
    rule) - its own shared module is `lib/spherical_machine.py`, holding
    everything byte-identical across the 3 real v2 `Render_Mode` branches,
    with `lib/selectric12.py`/`lib/selectric3.py`/`lib/selectric_
    composer.py` each carrying only their own layout data/config. Don't
    infer one new machine's code-sharing from another just because
    they're named alike or share a physical form.
  - `lib/cylinder_machine.py`'s own module docstring used to frame it as
    "Blickensderfer/Postal, and future family members" - that framing was
    stale (fixed to state the above explicitly) and should stay corrected;
    don't let it drift back to implying whole-module reuse for a new
    cylindrical machine.

### Before porting: always diff against the real v2 source

- **The real v2 source (`/home/lchau/github/Type-Elements/v2/<name>.scad`
  plus its `v2/lib/` includes) is the ground truth for a new machine's
  geometry and values - config YAML and lib code are ports of it, never
  invented independently.** Cross-reference specific v2 line numbers in
  comments/config when a v4 value or behavior corresponds to a v2
  variable, the way `config/bennett.yaml` and `lib/bennett.py` already
  do. When v4 intentionally drops or changes something from v2 (a dead
  customizer param, a resolved-differently default), say so explicitly
  in a comment instead of silently diverging - `bennett.yaml`'s
  dead-param callouts are the model to copy.
- **Don't assume a new machine reuses `lib/cylinder_machine.py` just
  because it looks similar on paper - verify function-by-function
  against the real v2 source first.** Mignon looked like Postal
  (another cylinder machine) but shared almost nothing structurally.
  (`SESSION_LOG.md` part 19; explicit warning for future machines in
  part 22)
- **`cylinder_machine.place_on_cylinder`'s docstring used to say
  Mignon/Bennett/Helios all pass a placement radius of 0 - that was
  already wrong for Bennett** (`lib/bennett.py`'s `configure()` deliberately
  does NOT pass 0, and explains why at length) **and has been corrected**
  to say so per-machine instead of asserting it from physical form. If
  you touch this docstring again, keep it stating the real, verified
  value per machine (not "Helios probably does X too") - a wrong
  assumption here is exactly what would make the next port repeat a
  bug Bennett already had to work around.

### Keep doing this (positive patterns, worth replicating verbatim)

- **Every machine module's entry points use the same names and
  near-identical signatures**: `configure(config_path)`,
  `_require_configured()`, `FullElement(...)`, `ResinPrint(...)`,
  `Additive(...)`, `CalibrationElement(...)`, `CalibrationAdditive(...)`,
  even accepting-but-ignoring a kwarg a given machine doesn't need
  (e.g. Mignon's `FullElement` accepts `render_core_groove` purely so
  `generate.py`'s uniform `build_fn(...)` call works across machines).
  Keep this consistent for the next machine even when its geometry
  doesn't need every kwarg.
- **A new machine's `Additive`/`Subtractive`/`ResinSupport`/per-character
  glyph-building code must use `lib/build_log.py`
  (`progress_start`/`progress_done`/`progress_skipped`/`progress_line`/
  `mesh_report`/`atomic_export`) from the very first commit, not as a
  follow-up fix.** This is not automatic just from importing the module -
  Hammond Split's own from-scratch `TextAssemble()` shipped without any
  progress instrumentation at all (no equivalent to `cylinder_machine.
  TextRing`'s per-character `[n/total]` print to inherit for free), which
  broke `tune.py`'s Build-tab progress bar for that one machine only,
  found and fixed in a separate follow-up session (`SESSION_LOG.md` parts
  60-63). A machine that reuses `cylinder_machine.TextRing`/
  `CalibrationTextRing` gets this for free; a machine with its own
  from-scratch glyph loop (the more likely case for a genuinely new form
  factor like IBM) does not, and needs it wired by hand, the way `lib/
  hammond_split.py`'s `TextAssemble()`/`CalibrationTextRing()` now are -
  treat those two functions as the template to copy.
- **`generate.py` dispatches via `importlib.import_module(cfg["machine"])`
  - the module filename must equal the config's `machine:` value.** This
  convention is load-bearing but not written down anywhere else; a new
  machine's module and `machine:` key must match exactly.
- **When two machines share a derivation, extract it into
  `lib/cylinder_machine.py` as a named function, the way
  `resin_raft_config()` was extracted for Blickensderfer/Postal's
  `resin.raft` toggle** - don't leave the same computation hand-copied
  into two machine modules. (Known still-open case: `Bottom_Slope`/
  `Bottom_Z_Offset` is currently duplicated byte-for-byte in
  `lib/blickensderfer.py` and `lib/postal.py` - extract it opportunistically
  if you're touching either.)
- **If the new machine has a different row/column count than existing
  ones, grep `tune.py` for hardcoded literal counts (`range(3)`, "3
  rows", etc.) rather than assuming the tab code is already generic.**
  Nine such literals had to be fixed for Mignon's 7 rows.
  (`SESSION_LOG.md` part 20)
- **`_receive_config()`'s globals-sync
  (`lib/cylinder_machine.py:_receive_config`) only picks up
  capital-leading names from the source module's globals, plus a
  hardcoded `z` exception.** A new machine-set global with a lowercase
  name is silently excluded - a `NameError` footgun, not a loud failure.

### Pick one convention, don't let it re-fork per machine

- **A config concept that already exists on another machine goes in the
  same top-level YAML section, every time - don't let it drift to a
  different section because it "feels like" it belongs elsewhere.**
  Two now-fixed outliers, kept here as the concrete example of what to
  avoid: the resin facet-count knob used to be `resin.resin_fn` for
  every machine except Mignon, which had it under `quality.resin_fn`
  (with the matching `tune.py` field living on the Quality tab instead
  of the Resin tab) - moved to `resin.resin_fn` to match the rest of the
  fleet. Separately, Hammond Split's Minkowski cone facet-count knob was
  spelled `quality.mink_fn` where every other machine spells the same
  concept `quality.minkowski_fn` - renamed to match. Both were pure
  key/section renames verified to produce byte-identical mesh output
  (same verts/faces/volume) before and after. Don't add a fifth variant
  or a differently-spelled knob for the next machine - match the
  established convention (`resin.resin_fn`, `quality.minkowski_fn`), or
  fix an existing outlier while you're in the area.
- **A list-valued config key that doesn't fit `tune.py`'s generic
  scalar `FIELDS` mechanism needs an explicit decision, made and
  written down, not a silent gap.** The two legitimate outcomes are (a)
  a bespoke per-item patcher, like `layout.baseline_row`/`cutout_row`
  got via `patch_yaml_list_item`, or (b) deliberately YAML-only with a
  one-line comment saying so, like `layout.placement_map`/
  `char_legend`. Bennett's `element.alignment_hole_height` (also a
  3-item list) used to get neither - silently unexposed with no comment -
  and has since been resolved as (b): see the comment above
  `ELEMENT_FIELDS_BENNETT` in `tune.py`. Any new list-valued key must
  land in (a) or (b) explicitly, the same way.
- **Reused geometry helpers that are "almost the same" across machines
  (e.g. the top/bottom Minkowski-cleanup cap, or a shaft-bore stand-in
  cylinder) should gain a parameter in the shared `cylinder_machine.py`
  version rather than being hand-copied per machine.** Mignon's and
  Bennett's `MinkCleanup()`/`CenterShaft()` are each independently
  reimplemented instead of sharing one parametrized version; Bennett's
  own `SpeedHoles()` comment already flags it as differing from
  `cylinder_machine.SpeedHoles()` by only a phase-offset constant.
  Treat a comment like that as a TODO to resolve during the *next*
  port that touches the same area, not permanent documentation of an
  accepted duplicate.
- **If a new machine's epsilon-style constant (`z` in `configure()`)
  needs a different magnitude than the existing machines use, say why
  in a comment.** Blickensderfer/Postal use `0.01`; Mignon/Bennett use
  `0.001`, with no comment anywhere explaining the change - don't add a
  third unexplained value.

### Process, not just files

- **Every machine port gets its own dated `SESSION_LOG.md` chapter with
  an explicit audit pass** - diff the new machine's config/lib/tune.py
  fields against sibling machines' equivalent fields and against the
  real v2 source, the way Mignon's port did (parts 19-21), not just a
  port-and-merge with no dedicated review. Bennett's port has no such
  chapter, and it correlates with Bennett having more small, undocumented
  inconsistencies (see "Pick one convention" above) than Mignon does.
  Don't skip this for Helios/Hammond/IBM even under time pressure.

## TUI (tune.py)

- **Never run headless `tune.py`/`TuneApp` against the real master or
  running config files - always point it at scratch copies.**
  `TuneApp.__init__` performs a real migration+save side effect on
  construction; this already overwrote a live `.running.yaml` once.
  (`SESSION_LOG.md` part 12, "Self-caught mistake"; reapplied as a
  standing warning in parts 13, 15, 18-20)
- **Use `Select.NULL`, not `Select.BLANK`.** In the installed `textual`
  version, `Select.BLANK` equals `False`, not a real sentinel.
  (`SESSION_LOG.md` part 7)
- **No layout data lives in `tune.py`. Every machine's keyboard/typeball
  layout presets live in `lib/layouts/<machine>_layout.py`, aggregated by
  `lib/layouts/__init__.py`, which `tune.py` imports.** Adding a machine
  means adding one module there plus one entry in each of that
  `__init__.py`'s `LAYOUT_PRESETS_BY_MACHINE`/`LAYOUT_PICKER_HELP` (and
  `LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE`/
  `LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE` if that machine needs them) -
  never a new `LAYOUT_PRESETS_*` dict in the TUI. Per explicit user
  direction; ~840 lines of preset data were moved out of `tune.py` to
  establish this, verified table-for-table identical before/after. Two
  consequences worth knowing:
  - **`lib/layouts/` is reachable under TWO module names** - `lib.layouts`
    (repo root on `sys.path`: `tune.py`, `font_coverage.py`) and plain
    `layouts` (`lib/` itself on `sys.path`: `lib/selectric12.py`'s `from
    layouts.selectric12_layout import ...`). So its internal imports MUST
    be relative (`from .hammond_layout import ...`); an absolute
    `from lib.layouts...` resolves under only one of the two names and
    would also let the package load twice as two distinct module objects.
  - **Keep it free of third-party imports** - it's pure data, so
    `font_coverage.py --preset` can read presets without dragging in
    `textual`/the whole TUI dependency stack (it used to `import tune`
    purely to reach these tables).
  - **A layout that needs a character/position mapping must NAME it, in
    the same module, via that machine's `PRESET_HEMISPHERE_MAP`** (see
    `lib/layouts/selectric12_layout.py`). The pairing is many-to-one on
    purpose - a hemisphere map is a physical key-position permutation, so
    several layouts can share one, and the maps stay defined once in
    `HEMISPHERE_MAPS`. `lib/layouts/__init__.py`'s
    `LAYOUT_PRESET_HEMISPHERE_MAP_BY_MACHINE` is DERIVED from those
    per-machine tables, never hand-written, so the two can't drift.
    This matters because an unpaired preset does NOT fall back to a
    default: `tune.py`'s `_save_to_yaml` only patches
    `layout.hemisphere_map` when the lookup hits, so the config silently
    keeps whatever the PREVIOUS preset wrote, and these maps are
    position-only (not character-aware) - a map mismatched to a layout
    builds a WRONG typeball with every character still present. Each
    module asserts full pairing coverage at import to turn that silent
    bad-geometry failure into a loud one; keep those asserts.
- **All build-pipeline console output goes through `lib/build_log.py`,
  not a hand-written `print()`.** Extracted after real drift was found:
  `glyph_poc.py` had its own `report()` that nothing in the actual
  pipeline called (wrong format, no `flush=True`), while the real,
  load-bearing pattern - `[n/total]` progress plus the one-line `verts=
  ... watertight=...` mesh summary - was hand-duplicated across
  `generate.py`/`cylinder_machine.py`/every machine module, drifting
  (some intermediate prints showed only `watertight=`, not the full
  `watertight/winding_consistent/is_volume/volume` set). Two conventions,
  both load-bearing, not cosmetic:
  - **`build_log.progress_start`/`progress_done`/`progress_skipped`/
    `progress_line` print the `"[n/total] ..."` shape `tune.py`'s
    Build-tab progress bar (`_update_progress`/`_PROGRESS_RE`) parses out
    of the subprocess's stdout to drive its 0-95% range.** Any per-
    character glyph-building loop needs to call these for every
    character or the progress bar just sits at 0% for the whole build,
    then jumps straight to 100% on completion - not a `tune.py` bug, a
    missing call in that machine's lib code. Blickensderfer/Postal/
    Mignon/Bennett/Helios/Hammond all get this for free by genuinely
    calling `cylinder_machine.TextRing`/`CalibrationTextRing`; Hammond
    Split builds its own from-scratch character loop (see `lib/hammond_
    split.py`'s module docstring) and initially shipped without matching
    instrumentation, reproducing exactly this symptom (`SESSION_LOG.md`
    part 61) - fixed by wiring `TextAssemble()`/`CalibrationTextRing()`
    through `build_log`, which also brought along `cylinder_machine.
    TextRing`'s other habit worth copying for free: catch a per-
    character exception, print `" SKIPPED (...)"`, and continue rather
    than aborting the whole build over one bad glyph. Any FUTURE machine
    with its own from-scratch glyph loop needs this wired by hand too -
    it is not automatic just from importing the module.
  - **`build_log.mesh_report(mesh, label)` is the one authoritative
    `verts=.../watertight=...` summary line format** - always the full
    field set (matching `generate.py`'s own final-output line, the
    literal source of truth the CLAUDE.md hard-gate verification below
    compares against), never a hand-abbreviated subset.
  - `cylinder_machine.CalibrationTextRing`'s own per-row/col line is
    intentionally NOT routed through `progress_start`/`done` (richer
    single-line content - position/angle/mm detail - that doesn't fit
    that two-part shape) but still satisfies `_PROGRESS_RE` on its own;
    left as a plain `print(..., flush=True)`, not a gap.
  - Every hand-written `verts=.../watertight=...` print across `generate.
    py`/`cylinder_machine.py`/`mignon.py`/`bennett.py`/`helios.py`/
    `hammond.py`/`hammond_split.py`/`type_test.py`/`export_glyphs.py` has
    been migrated to `build_log.mesh_report()` - this was a real, full
    sweep (`SESSION_LOG.md` part 63), not just the two files that
    happened to be touched when the module was first extracted. A new
    print of this shape anywhere is a regression, not a stylistic choice.
    Two `report()` functions still print a similar line and are NOT
    regressions: `glyph_poc.report()` and `heightfield_poc.report()`,
    both reached only from their own file's `__main__` block for
    inspecting one glyph interactively (deliberately more verbose - adds
    bbox - and never piped through `tune.py`'s subprocess, so they need
    no `flush=True`). Each says so in its own docstring. Nothing in the
    `generate.py`/`tune.py` build path calls either.
- **`generate.py`/`type_test.py`/`export_glyphs.py` write output meshes
  via `build_log.atomic_export()` (temp file in the same directory +
  `os.replace()`), never a bare `mesh.export(out_path)`.** `trimesh`'s
  own `export()` opens/truncates the destination directly - `tune.py`'s
  f3d `--watch` window has its own independent filesystem watcher and can
  fire on that truncate/open event before the write finishes, loading a
  0-byte or partial file. Every new call site that writes a final output
  mesh must go through `build_log.atomic_export()`, not add a new direct
  `.export()` call.
- **`tune.py` only ever points f3d's `--watch` at a path it has already
  confirmed exists** (`_ensure_f3d_after_build` tracks `self._f3d_
  out_path` and forces a fresh kill+relaunch whenever the requested path
  differs from what's currently being watched, which includes "first
  successful build this session"). f3d loads whatever file is current AT
  LAUNCH and only watches for *changes* after that - if it's ever pointed
  at a path before that path has a real file on disk (the very first
  Preview for a brand-new machine/output path, or a manually-started f3d
  aimed at a not-yet-built path), it shows an empty scene and its
  filesystem watch has no inode to attach to, so it never recovers even
  once the file is later created - reported as f3d's window persistently
  showing `"[EMPTY]"` no matter how many successful builds follow
  (`SESSION_LOG.md` part 61 - this, not the `atomic_export()` race above,
  turned out to be the real cause). Don't add a new f3d-launching call
  site that skips this tracking.
- **List-valued config keys (`layout.rows`, `baseline_row`/`cutout_row`)
  need their own bespoke patcher (see `patch_yaml_list_item`/the
  block-list patch in `tune.py`), not the generic single-scalar FIELDS
  mechanism.** (`SESSION_LOG.md` parts 17, 20)
- **Per-machine banner/help text (prose that varies by machine but isn't
  a per-field tooltip) goes in a dict keyed by machine name, defined
  once near the other per-machine tables (`LAYOUT_PRESETS_BY_MACHINE`
  etc.), never as a hand-written `if self.machine == "x": ... elif ...`
  chain inside a `_compose_*_tab` method.** A new machine should mean
  adding one dict entry, not growing a branch. `LAYOUT_PICKER_HELP` (used
  by `_compose_layout_tab`) is the template to copy - it replaced exactly
  this kind of if/elif chain, which is also where the manual-`\n` bug
  in the tooltip rule below was found live (Bennett's entry, fixed in
  the same pass). If you're adding banner text for a new machine and no
  such dict exists yet for that banner, create one rather than adding
  a branch to existing code.

### tooltip/help-text `Static` widgets

Any `Static` whose content is user-facing help/tooltip text (the
`.field-help`, `.picker-help`, and `.advanced-warning` CSS classes in
`TuneApp.CSS`, and any new class serving the same purpose) must follow
both rules below. Violating either reproduces the bug fixed in
`SESSION_LOG.md` part 22 (text clipped, or clipped input fields below
it).

1. **`height: auto` in the CSS class, never a fixed row count.** A
   fixed `height: N` clips any message longer than `N` lines instead of
   wrapping it. The containing `Vertical(classes="field-row")` (or
   equivalent) must also be `height: auto` (with `margin-bottom: 1` to
   keep the visual spacing that a fixed height used to provide) so it
   grows with its help text instead of clipping it.
2. **No manual `\n` line breaks in the string.** Write the text as one
   flowing string (ordinary adjacent-string-literal concatenation
   across source lines is fine). Textual wraps `Static` content to the
   widget's actual width automatically - a hand-inserted `\n` at some
   guessed width gets wrapped *again* on top of that, roughly doubling
   the rendered line count and pushing whatever is below it down the
   tab. (Manual `\n` is still correct where you're building literal
   file content, e.g. the YAML/txt headers in `_save_to_yaml()` - this
   rule is only for text a `Static` renders in the TUI.)

Keep the wording itself short: 1-2 sentences, no fluff, no unnecessary
internal/source cross-references. Longer banners (`SECTION_INTROS`,
the Layout/Build/Type Test tab intros) should still fit in well under
10 rendered lines - if a description needs more than that, it likely
belongs in `README.md`/`SESSION_LOG.md` instead of a tab banner.

## Verifying a geometry-affecting change (hard gate)

Before calling any change to glyph/mesh/assembly code done, run
`generate.py` for every config it could plausibly affect and compare the
final summary line against a pre-change baseline:

```
.venv/bin/python3 generate.py config/<name>.yaml --flatness-tolerance-mm 0.05 --cone-segments 12 --no-core-groove --no-minkowski --out /tmp/check.stl
```

(This line used to read `--points-per-mm 8`, which no longer parses -
that flag was removed fleet-wide when contour sampling became adaptive,
see "Geometry invariants" above. `--flatness-tolerance-mm` is its
replacement. Note `.venv/bin/python3`, not bare `python3` - `trimesh` and
the rest of the build stack are only installed in the venv.)

`--no-minkowski` skips the (slow, minutes-per-config) Minkowski draft
sweep - the gate only needs a change's effect on the underlying
glyph/assembly geometry to be visible, and the sweep is a separate,
already-covered invariant (see "Geometry invariants" above) that doesn't
need re-proving on every unrelated change. This means baseline numbers
recorded before this convention changed (with Minkowski enabled) are
NOT comparable to a `--no-minkowski` run - verts/faces/volume will
legitimately differ - so the first `--no-minkowski` run against any given
config after this change is a fresh baseline to record, not a mismatch
to chase down. A change that specifically touches Minkowski/draft-sweep
code still needs at least one real (Minkowski-enabled, no flag) gate run
on an affected config, since `--no-minkowski` can't verify that path at
all.

The last line before `wrote ...` (e.g. `ResinPrint: verts=42618
faces=85408 watertight=True winding_consistent=True is_volume=True
volume=5666.804mm3`) is deterministic run-to-run for unchanged inputs -
confirmed by running the same config twice. For any config/machine the
change was NOT meant to touch, this line must match exactly
(verts/faces/volume to the printed precision, watertight/
winding_consistent/is_volume all still `True`) against that config's own
`--no-minkowski` baseline. A mismatch on an "unaffected" config means the
change had a side effect that wasn't intended - chase it down before
considering the work finished, don't just note it and move on.

## SESSION_LOG.md discipline

For sessions that span multiple non-trivial steps, or that leave work
mid-stream, end the entry with a dated part header and a "Resuming
later" punch list (see e.g. part 14) so the next session - possibly
after a context/credit gap - can pick up without re-deriving where
things stand. Not needed for small, self-contained fixes.
