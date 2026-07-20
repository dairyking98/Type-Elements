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

## Before writing new code

Search `lib/cylinder_machine.py` (shared across cylinder machines) and the
target machine's own module (`lib/blickensderfer.py`, `lib/postal.py`,
`lib/mignon.py`, `lib/bennett.py`, `lib/glyph_poc.py`,
`lib/scad_primitives.py`) for an existing function that already does what
you're about to write before adding a new one. Duplicated logic is how
machines drift out of sync silently - see "Porting a new machine" below
for the same failure mode at the machine-port level.

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
- **`layout.latitude_columns` must stay in sync with `placement_map`/the
  physical layout.** It's intentionally not exposed in the Layout tab's
  named-preset picker - edit it directly in the YAML only if you really
  mean to change it. (`tune.py`, `_compose_layout_tab`)

## Porting a new machine

### Machine taxonomy - don't assume "cylindrical" implies "shares code"

- **Physical form and code-sharing are two separate axes - check both,
  don't infer one from the other.** Ported so far: Blickensderfer,
  Postal, Mignon, Bennett, Helios Klimax. Remaining, per the roadmap:
  Hammond/Hammond_split (shuttle mechanism - a different form factor from
  the cylindrical family), IBM (spherical - also a different form
  factor). All of Blickensderfer/Postal/Mignon/Bennett/Helios are
  cylindrical in outward form, but:
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
  - **Hammond/Hammond_split and IBM are a different form factor
    entirely** - don't reach for `cylinder_machine.py` as the starting
    point for either; they need their own equivalent of that
    exercise (identify what, if anything, is genuinely shared with an
    existing machine vs. `glyph_poc.py`/`scad_primitives.py`-level
    primitives only).
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
  Concrete outlier already in the codebase: the resin facet-count knob
  is `resin.resin_fn` for Blickensderfer/Postal/Bennett but
  `quality.resin_fn` for Mignon (with the matching `tune.py` field
  living on the Resin tab for three machines and the Quality tab for
  Mignon). Don't add a fifth variant - either match the majority
  (`resin.resin_fn`) for the next machine, or fix Mignon's placement
  while you're in the area.
- **A list-valued config key that doesn't fit `tune.py`'s generic
  scalar `FIELDS` mechanism needs an explicit decision, made and
  written down, not a silent gap.** The two legitimate outcomes are (a)
  a bespoke per-item patcher, like `layout.baseline_row`/`cutout_row`
  got via `patch_yaml_list_item`, or (b) deliberately YAML-only with a
  one-line comment saying so, like `layout.placement_map`/
  `char_legend`. Bennett's `element.alignment_hole_height` (also a
  3-item list) currently gets neither - it's silently unexposed in the
  UI with no comment explaining why it didn't get treatment (a). Don't
  repeat that: any new list-valued key must land in (a) or (b)
  explicitly.
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
- **All `generate.py`/`tune.py` prints that feed the TUI's log pane need
  `flush=True`.** Piped subprocess stdout is fully block-buffered
  otherwise, so live progress silently stalls until the buffer fills.
  (`SESSION_LOG.md` part 7)
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
   file content, e.g. the YAML/txt headers in `save_config()` - this
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
python3 generate.py config/<name>.yaml --points-per-mm 8 --cone-segments 12 --no-core-groove --out /tmp/check.stl
```

The last line before `wrote ...` (e.g. `ResinPrint: verts=42618
faces=85408 watertight=True winding_consistent=True is_volume=True
volume=5666.804mm3`) is deterministic run-to-run for unchanged inputs -
confirmed by running the same config twice. For any config/machine the
change was NOT meant to touch, this line must match exactly
(verts/faces/volume to the printed precision, watertight/
winding_consistent/is_volume all still `True`). A mismatch on an
"unaffected" config means the change had a side effect that wasn't
intended - chase it down before considering the work finished, don't
just note it and move on.

## SESSION_LOG.md discipline

For sessions that span multiple non-trivial steps, or that leave work
mid-stream, end the entry with a dated part header and a "Resuming
later" punch list (see e.g. part 14) so the next session - possibly
after a context/credit gap - can pick up without re-deriving where
things stand. Not needed for small, self-contained fixes.
