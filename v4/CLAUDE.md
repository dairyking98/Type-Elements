# v4 conventions

## Before writing new code

Search `lib/cylinder_machine.py` (shared across cylinder machines) and the
target machine's own module (`lib/blickensderfer.py`, `lib/postal.py`,
`lib/mignon.py`, `lib/glyph_poc.py`, `lib/scad_primitives.py`) for an
existing function that already does what you're about to write before
adding a new one. Duplicated logic is how the two machines drift out of
sync silently - see "Porting a new machine" below for the same failure
mode at the machine-port level.

## Geometry invariants

These are hard rules, not stylistic preferences - each one maps to a
confirmed, previously-shipped bug (see `README.md`/`SESSION_LOG.md` at
the cited section for the full incident).

- **Real machine numbers live in config YAML, never hardcoded in code.**
  A second machine should mostly be a new YAML file under `config/`, not
  a code fork. (`README.md` "Usage"/"Multiple machines")
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

- **Don't assume a new machine reuses `lib/cylinder_machine.py` just
  because it looks similar on paper - verify function-by-function
  against the real v2 source first.** Mignon looked like Postal
  (another cylinder machine) but shared almost nothing structurally.
  (`SESSION_LOG.md` part 19; explicit warning for future machines in
  part 22)
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
