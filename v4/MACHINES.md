# Machines: per-machine architecture

Split out of `README.md` to keep it direct - see
[`README.md`](README.md) for setup, usage and the machine list.

## Multiple machines (`lib/cylinder_machine.py`)

Blickensderfer and Postal are both "cylinder machines" - same physical
form, same v2 shared lib includes (`core_shaft.scad`, `resin_rod.scad`,
`resin_support.scad`, `glyph_pipeline.scad`), same `TextRing` radial-wrap
placement scheme. Everything structurally shared between them
(`Cylinder`/`Subtractive`/`FullElement`/`ResinPrint`/the whole Gauge
family/...) lives in `lib/cylinder_machine.py`. The only place the two
machines genuinely diverge in CODE, not just parameter values, is the
"drive pin trio" - `HollowSpace()`/`DrivePin()`/`ResinSupport()` -
Blickensderfer has a drive-pin countersink (2 selectable styles),
Postal has none at all. Those three functions live one-per-machine in
`lib/blickensderfer.py`/`lib/postal.py`.

**Dispatch mechanism**: each machine's `configure()` calls
`cylinder_machine._receive_config(g, name)` at the end, which copies
every config value AND the three trio function objects into
`cylinder_machine`'s own `globals()`. A function's `__globals__` is a
live reference to its defining module's dict, not a snapshot - so
`Subtractive()` (defined in `cylinder_machine.py`) calling `HollowSpace()`
as a bare name resolves it dynamically, against whichever machine
configured most recently. This directly mirrors OpenSCAD's own "last
include wins" dynamic module redefinition, which is how v2's shared lib
files achieve machine-specific behavior in the first place. Safe here
because `generate.py`/`export_glyphs.py` each configure exactly one
machine per process and exit - `tune.py` never imports these modules at
all, it only edits YAML and shells out to `generate.py` as a subprocess.
An `_active_machine` guard raises if a script ever tries to configure two
machines in the same process (not a real risk today, cheap insurance).

`config/postal.yaml`'s font paths point to the real fonts (`Alma
Mono.otf`, `FreeMono-Bold.otf`) - v2's real Postal font is a system font
family name ("Alma Mono" / "FreeMono:style=Bold"), not a file path, so
these are the actual matching files rather than a name lookup. Both are
CFF/cubic-curve OTFs, which used to silently mis-render (see [`LIMITATIONS.md`](LIMITATIONS.md)'s "TrueType-only outlines - RESOLVED") - now handled
correctly and verified end-to-end.

`python3 tune.py` (no args) starts at a machine picker listing all 15
machines (`MACHINES` in `tune.py`, grouped by real-world type-element
mechanism), and loads the picked machine's default config into tabs
scoped to that machine. Taking Postal as the example: a Postal-scoped
Element tab (27 fields vs. Blickensderfer's 32, since Postal has no
drive-pin countersink) and its own Layout tab - a single "QWERTY" preset,
since `v2/postal.scad` has only one physical layout, with no
preset-switching menu like Blickensderfer's (which has 8, including two
taken from the type-wheel catalog scans - see `LAYOUT_TRANSCRIPTION.md`)
- still hand-editable via Modify glyphs if you need something else. The tuner
form's status row gains a "Change Machine" button once a machine is
picked, which saves the current form and returns to the picker (uses
Textual's `recompose()` to fully rebuild the form - `TuneApp.SECTIONS`/
`.FIELDS`/`.LAYOUT_PRESETS` are instance attributes reset by
`_load_machine()` on every pick, not fixed for the process lifetime). The
old direct-launch usage (`python3 tune.py config/postal.yaml`) still
works and skips the picker. The Browse button (separate from Change
Machine) only switches between different configs of the SAME machine -
picking a config for a different machine there is refused with a log
message pointing at Change Machine instead, since Browse repopulates the
existing widgets in place rather than recomposing.

### Mignon (`lib/mignon.py`) - NOT a "cylinder machine"

Unlike Postal, Mignon does **not** share `cylinder_machine.py`'s body
construction - only its glyph placement pipeline (`TextRing`,
`CalibrationTextRing`) is genuinely reusable. Confirmed by direct
function-by-function comparison against `v2/mignon.scad`: no
`Core`/`ClipCylinder`/`WireBite`/`SpeedHoles`/`core_shaft.scad` family at
all (its shaft bore is one plain `rotate_extrude()` polygon), a 12-sided
polygon main body instead of a round cylinder, a stepped-boss+chamfer top
feature instead of a wire clip, a plain cut-through alignment keyway
instead of a countersunk drive pin, Minkowski cleanup at **both** ends
instead of top-only, and fully bespoke resin-support placement (no
`CutGroove`/`SpeedHoleSupport`/`DrivePinSupport`/`BottomSupports` - just a
raft ring plus rods at two radii). `lib/mignon.py` reimplements all of
this locally rather than extending `cylinder_machine.py`; see its module
docstring for the full comparison.

Two shared-module changes DID come out of this port (both backward-
compatible, regression-verified against Blickensderfer/Postal):

- **Row count.** `TextRing`/`CalibrationTextRing` hardcoded `for row in
  (0, 1, 2):` - Mignon has 7 physical rows, not 3 (`v2/mignon.scad`'s
  `Baseline_Regular`/`Cutout` are both 7-entry arrays). Changed to
  `range(len(DHIATENSOR))`, which reduces to the exact same 3-row loop
  for Blickensderfer/Postal's configs.
- **Placement formula overrides.** `place_on_cylinder()` hardcoded
  `Char_Protrusion` (the placement-stage radial protrusion) and `0.5`
  (the angle-half-step column-centering constant). Mignon's v2 source
  overrides both to 0 (`Letter_Placement_Protrusion`/`Angle_Half_Step`,
  `v2/mignon.scad:118-121` via `lib/glyph_pipeline.scad`'s own documented
  optional-override mechanism) - added as optional `placement_protrusion`/
  `angle_half_step` params, `None` (every Blickensderfer/Postal call site)
  preserving the exact original hardcoded behavior.

Also has no Shaft Gauge Test at all (`v2/mignon.scad:30`: "Shaft Gauge
Test... omitted" - confirmed, along with Bennett and Helios Klimax, via
the same explicit comment in their own files). `tune.py` handles this
generically - `SECTIONS_BY_MACHINE["mignon"]` simply has no `"Gauge"` key,
and both the Gauge tab and the Build tab's "Shaft Gauge" option check for
that key's presence rather than assuming every machine has one.

One real bug caught and fixed during this port: `v2/mignon.scad:120`'s
`Latitude_Int=-360/len(Layout[0])` is **negative** (columns wrap the
opposite rotational direction from Blickensderfer/Postal's positive
`360/columns`) - missed on the first pass (copied the positive formula
literally), caught via a direct render comparison, fixed by hardcoding
the sign flip in `mignon.py`'s own `configure()` (machine-specific, not a
`cylinder_machine.py` change).

**Layout tab.** `tune.py`'s Layout tab was written when Blickensderfer/
Postal (3 rows each) were the only machines and had "3" hardcoded as a
literal in nine places (`BASELINE_CUTOUT_KEYS`, row-preview widget
construction, custom-row seeding, save round-trip, etc.) - all now derive
the row count from the config (`len(layout.baseline_row)`, etc.), which
reduces to the same 3-row behavior for Blickensderfer/Postal
(regression-verified) and correctly handles Mignon's 7. All 30 of
Mignon's real named layout presets (German 4, Cyrillic, Bulgarian,
Georgian, etc.) were ported from `v2/lib/layouts/mignon_layouts.scad`
into `LAYOUT_PRESETS_MIGNON` (3 placeholder-empty presets in v2's own
source were excluded; two anomalous 13-character rows in v2's Georgian/
Greek data, unreachable by v2's own `Char_Legend` indexing, were
truncated to 12). `layout.rows`/`LAYOUT_PRESETS_MIGNON` are stored in RAW
KEYBOARD-LEGEND order (v2's own `Layout` array - what's printed on the
physical keyboard/manual), not the `Char_Legend`-remapped `Physical_
Layout` build order - `lib/mignon.py`'s `configure()` applies
`layout.char_legend` (`[7,8,9,10,11,0,1,2,3,4,5,6]`, matching
`v2/mignon.scad:88` exactly) to compute the actual build-time `DHIATENSOR`
itself, so the legend can be read/edited the way a person actually reads
it off the machine without hand-deriving the build order. See
SESSION_LOG.md parts 20-21 for the full account.

**Label - a genuine second engraved-text feature, not in v2.** v2/
mignon.scad's real `[Logo]` customizer section (confirmed end to end) has
exactly ONE engraved-text feature (`Cylinder_Label`), which is what this
app's `logo.*` config/"Logo" tab already drives. A second, independent
`label.*` feature was added anyway (v4-only, not a v2 port), with its
own "Label" tab - same field format as Logo (font/text/size/spacing/
height-offset), always placed 180
degrees opposite Logo's `position_offset_deg` (computed in `configure()`
as an invariant, not independently stored - moving Logo moves Label with
it). Defaults to empty text rather than duplicating Logo's default
verbatim: at Logo's real 15deg/char spacing a normal-length label already
spans most of the ring, so two identical strings 180 degrees apart would
overlap rather than sit cleanly opposite each other.

**Tallen (Plakatschrift) mode.** A display-type variant
(`v2/mignon.scad:109-115,197`, off by default like this file's real
untallened German 4 element) that adds `height_increase_mm` (3mm) to the
element height and shifts every baseline row by
`tallen_baseline_offset_mm` (-1.25mm) - cutout rows are NOT affected, a
real asymmetry in v2's own source, not an oversight. Previously
acknowledged-but-not-ported; now a real `element.tallen` toggle plus its
two magnitude fields, all exposed on the Element tab.

### Bennett (`lib/bennett.py`) - shares the glyph pipeline, bespoke body

Like Mignon, Bennett shares `cylinder_machine.py`'s glyph placement/text
pipeline (`TextRing`/`CalibrationTextRing`), but leaves `place_on_cylinder`'s
`placement_protrusion` at its DEFAULT (`Char_Protrusion`) rather than
passing 0, despite v2's own `Letter_Placement_Protrusion=0` - see
`lib/bennett.py`'s `configure()` for why that value doesn't survive
translation into v4's model (a real bug, caught after shipping: with
`placement_protrusion=0`, `min_final_character_diameter` was a dead config
field - every character's real-world protrusion pinned to
`Element_Diameter/2` no matter what it was set to. Mignon has the exact
same latent bug, not yet fixed). And, unlike Mignon, Bennett also reuses
`lib/core_shaft.scad`'s shared `SecondaryCore`/`CoreGrooves`/`CoreChamfer`/
`CoreEllipses` directly (`Core_Chamfer_Top=False` - no clip, so unlike
Blickensderfer/Postal there's no top chamfer under one; `Core_Taper_Top_Z`
= `Core_Top_Z` - the taper's own top landmark coincides with the absolute
top, again because there's no clip pushing it down). Bennett does NOT
override `Angle_Half_Step` the way Mignon does - v2 never sets it, so it
stays at the shared lib's default 0.5, verified algebraically: Bennett's
own `Theta=-(360/28*col+360/(2*28))` reduces to exactly
`(0.5+col)*Latitude_Int`, the same formula shape as Blickensderfer/Postal,
just with `Latitude_Int` negative instead of positive (same sign
convention as Mignon).

Everything else is fully bespoke, confirmed by direct comparison against
`v2/bennett.scad`: two positioner pins with a small chamfer cone
(`PositionerPins`) instead of a wire clip, a 9-point `rotate_extrude()`
polygon shaft bore (`HollowBody`, built from landmark arrays + an index
pattern, ported mechanically) instead of `core_shaft.scad`'s
`HollowSpace()`+`BottomSlopedSpace()` combination, a full 3-row x
28-column grid of physical alignment/screw holes (`AlignmentHoles`, no
Blickensderfer/Postal equivalent at all), two independent flat
whole-string engraved-text groups cut into the bottom face near the shaft
(`LabelText` - v2 calls `text()` directly per whole string with
`halign=valign="center"`, not a ring of individually angle-placed
characters like Blickensderfer/Postal's `LogoText` or Mignon's
`ElementLogo`/`ElementLabel` - see `cylinder_machine.build_text_string()`'s
docstring for
how whole-string layout was ported: each character placed at its natural
FreeType advance, the assembled string centered on its total advance
width - the same "native halign=center centers the ADVANCE box"
convention this codebase already established for `AlignedText`), a simple
fixed 8-hole `SpeedHoles` ring (own diameter/radius names, plus a
half-step angular phase offset Blickensderfer/Postal/Mignon's own
`SpeedHoles` don't have), top+bottom countersinks and an indicator
hole/roof taper, and fully bespoke resin-support placement (own
ring+groove+raft `rotate_extrude()`, 8+8+4 `ResinRod()` calls at three
different radii/heights - no `CutGroove`/`SpeedHoleSupport`/
`DrivePinSupport`/`BottomSupports` concepts at all, though it DOES reuse
`cylinder_machine._resin_rod()` for the rod primitive itself, same as
Mignon).

No Shaft Gauge Test (`v2/bennett.scad:24`: "Sections with no Bennett
equivalent (Print Tolerances, Shaft Gauge Test) are omitted" - same as
Mignon). Its one engraved-text feature lives under its own `label:` config
section/"Label" tab (not "Logo" - the field shapes don't correspond to
Blickensderfer/Postal/Mignon's Logo schema at all, no text_spacing/
position_offset_deg/radial_offset_mm concept). Composing this exposed a
latent `tune.py` bug: `_compose_tuner_ui()` unconditionally composed a
"Logo" tab for every machine (never previously exercised, since
Blickensderfer/Postal/Mignon all have one) - now guarded by `"Logo" in
self.SECTIONS`, matching the existing `"Label"`/`"Gauge"` guards right
next to it.

### Helios Klimax (`lib/helios.py`) - shares the glyph pipeline AND the core_shaft family, bespoke body otherwise

`v2/heliosklimax.scad` is unusually self-documenting - its own header
records a real v1->v2 byte-check correction history, and explicitly lists
what the ORIGINAL had no equivalent of at all: `SecondaryCore`/
`CoreGrooves`/`CoreChamfer`/`CoreEllipses` (no `core_shaft.scad` family
whatsoever), Logo/Label engraved text, and (same as Bennett/Mignon) a
Shaft Gauge Test. `TextRing`/`CalibrationTextRing`/`place_on_cylinder`
are shared the usual way (via `cylinder_machine._receive_config`).

**Deliberate v4-only enhancement, not a v2 port (explicit user
direction):** the shaft bore now ALSO reuses `cylinder_machine.py`'s
shared `Core()`/`CoreChamfer()`/`SecondaryCore()`/`CoreEllipses()`/
`CoreGrooves()` - the same "fancy core stuff" Blickensderfer/Postal/
Bennett have - in place of the plain straight bore the real v2 file had.
Since v2 never had this system for Helios, `element.core_chamfer`/
`core_bottom_offset`/`core_contact_length`/`core_web_*`/`core_groove_*`
are NOT real-machine numbers - they're starting estimates scaled from
Bennett's config (closest shaft diameter, 3.4mm vs Helios's 4.16mm),
meant to be tuned against the physical part the same way
`baseline_row`/`cutout_row` already are. `Core_Top_Z`/`Core_Taper_Top_Z`
follow Blickensderfer/Postal's "has a clip" convention (not Bennett/
Mignon's clip-less one), since Helios's own clip retainer puts it in that
same situation - this also required a `Clip_Height` bridging alias in
`configure()` (the shared functions reference that bare name; Helios's
own code uses `Element_Clip_Height`), and made `quality.cyl_fn` (declared
but unused by the original port) genuinely used for the first time.

Two real values `place_on_cylinder`'s own docstring had flagged as "not
yet verified" for Helios are now resolved: `angle_half_step=0` (no
half-column centering term, same as Mignon), and `placement_protrusion`
left at its default (`Char_Protrusion`) - NOT v2's raw `Letter_Placement_
Protrusion=-.05`. That raw value shipped once as a real bug (characters
sat far too deep/inset): v2's `LetterPlacement` and `PlatenCutout` are
two INDEPENDENT transforms, and `-.05` only ever moved the former (v2's
own comment: "a small built-in 0.05mm radial inset that only affects
placement, not the platen-cutout radius") - the latter, which actually
sets the visible strike depth, uses the same `Element_Diameter/2+
Platen_Diameter/2+Char_Protrusion` formula Blickensderfer/Postal do. v4
has no such split (one combined transform), so reproducing v2's real
low point requires `placement_protrusion=Char_Protrusion` - the exact
derivation `lib/bennett.py`'s port already had to make for the same
reason. See `SESSION_LOG.md` part 25.

**A genuine two-stage `difference()`, not a flattenable additive/
subtractive split.** v2's `Assemble()` nests three `difference()`s -
`AlignmentPinSupport()`/`ClipRetainer()` (two bosses) are added only
*after* the first round of cuts (`HollowingElement`/`MinkCleanup`/
`IndicatorHole`), then are themselves cut by a second round
(`AlignmentPinHole`/`WireClip`/the core_shaft family above). This isn't
cosmetic: `AlignmentPinSupport`'s boss position genuinely falls inside
`HollowingElement`'s own cavity extent (verified against the real config
values), so a naively flattened "union everything, subtract everything"
(the shape every other machine's `FullElement` uses) would incorrectly
eat the boss. `lib/helios.py`'s `_assemble()` reproduces the real staged
order directly - see its module docstring for the full derivation.
(`AlignmentPinSupport()` itself is currently disabled by explicit user
request - commented out, not deleted, in `lib/helios.py` - but the
two-stage structure stays regardless, since `ClipRetainer()` independently
needs it too; see `SESSION_LOG.md` part 28.)
`HollowingElement()` itself is a true `shapely` convex hull of 5 circles
(matching v2's `hull(){circle(); ...}` exactly, real rounded corners),
the same hull-then-revolve technique `WireBite()`/Mignon's
`AlignmentPin()` already use, rather than `cylinder_machine.
_hollow_space_profile()`'s hand-rounded point-list approximation - at
`resolution=32`/`sections=Surface_Fn`, same as every other revolve in
this file. (This briefly got dropped to a hardcoded lower value to work
around a slow diagnostic - see `generate.py`'s entry below for why that
diagnostic is gone entirely now instead, and `SESSION_LOG.md` parts
26-27 for the full story.)

`Resin_Support`/`Resin_Support_*` are declared in v2 but it never builds
any actual support geometry with them - `ResinSupport()`/`ResinPrint()`
here are a plain no-op/alias to `FullElement()` rather than inventing a
resin system that was never really there (unlike `Cyl_Fn`, which was
originally declared-but-unused the same way but is now wired up for real
by the core_shaft reuse above - see that note).

No Shaft Gauge Test, no Logo/Label tab (see the header note above) -
`SECTIONS_BY_MACHINE["helios"]` has no `"Gauge"`/`"Logo"`/`"Label"` key,
same generic-guard mechanism Mignon/Bennett already established. Layout
tab: two named presets (`German (Modified)` - v2's real default/only-used one -
and the superseded `GERMAN`, both inline in v2's source), 4 physical rows
(vs. everyone else's 3) - required zero additional `tune.py` literal-
count fixes, since the row-count-agnostic work from Mignon's port (see
"Layout tab" above) already covers this generically. See
`SESSION_LOG.md` parts 23-24 for the full audit pass and verification,
part 25 for the placement_protrusion fix, and part 26 for the
hollow-cavity performance fix above.


## Element assembly (`lib/blickensderfer.py`)

Ports `Additive()`/`Subtractive()`/`FullElement()` from
`v2/blickensderfer.scad` close to 1:1, in the same origin/orientation
convention (Z=0 at the bottom face of the main disk, Z+ up through the
clip end). `Subtractive()`'s parts are unioned into one mesh, then
subtracted from `Additive()` in a single `manifold3d` boolean - the same
build-solid-then-hollow order the real file already uses.

Ported features: `Cylinder`, `ClipCylinder`, `TextRing`, `Core`,
`CoreGrooves` (16 twisted friction grooves), `CoreChamfer`, `SecondaryCore`
(tapered friction-fit profile), `CoreEllipses` (web slots), `SpeedHoles`,
`HollowSpace` (the real chamfered/roofed barrel profile, not a plain
bore - see `scad_primitives.revolve_polygon`), `WireBite`, `DrivePin`,
`BottomSlopedSpace`, `TopMinkCleanup`, `LogoText`.

Not ported (out of scope so far): `Drive_Pin_Style=1` (old drive pin
variant).

### Facet-count knobs (`quality:` in the config)

Five separate `_fn` values, kept independent rather than sharing one
catch-all, per user direction - each covers a distinct surface family:

- `body_fn` - the main visible/cosmetic element body (`Cylinder`,
  `ClipCylinder`) only.
- `cyl_fn` - the inner shaft/core bore (`Core()`) only. Kept separate from
  `body_fn` even though both currently default to the same value (360).
- `surface_fn` - everything else structural: `HollowSpace`, `SpeedHoles`,
  chamfers, resin details.
- `platen_fn` - the real platen cutout cylinder (see `PIPELINE.md`
  above) - independent of the other four since it's a per-glyph boolean,
  not a body-level revolve.
- `minkowski_fn` - the draft cone kernel (see [`PIPELINE.md`](PIPELINE.md)) - by
  far the most cost-sensitive of the five, since `manifold3d`'s Minkowski
  cost scales with the product of the two operands' face counts, and the
  glyph operand's count is set by `flatness_tolerance_mm` (which replaced
  the old fixed-rate `points_per_mm`).

`quality:` also carries a sixth `_fn` key, `groove_fn`, which is NOT one
of the five above: it's the CoreGrooves twist angular sampling, not a
facet count for any surface.

### Resin print supports (`ResinPrint`)

Ports `lib/resin_rod.scad` (`ResinRod` -> `scad_primitives.resin_rod`, a
generic hull-of-spheres tapered support rod, reusable across future
machines) and `lib/resin_support.scad`'s cylinder-machine-family placement
logic (`CutGroove`, `SpeedHoleSupport(s)`, `DrivePinSupport`,
`BottomSupports`, `ResinPrint`) - shared between machines in
`lib/cylinder_machine.py` (see "Multiple machines"); only
`ResinSupport()` itself is machine-specific (the drive-pin trio).
`CutGroove()` - the breakaway ring - is built as `revolve(profile) -
revolve(hole1) - revolve(hole2)`: the real file's 2D difference happens
*before* `rotate_extrude()`, so each hole becomes a full 360deg toroidal
score line around the circumference, not discrete perforation points.

`ResinPrint()` unions `ResinSupport()` onto `FullElement()` (support
material to be broken off after printing, not subtracted). Off by default
(`build.resin_support: false` in the config) since it's only needed right
before slicing for print; enable via `--resin-support` or the config.

**`resin.raft`** (also on tune.py's Resin tab as "Continuous raft"): `false`
(default, both machines) - each support rod grows its own small raft
cone. `true` - one continuous raft plate shared by every rod, reaching
all the way to the element's center axis. This was originally two
separate hardcoded per-machine values (v2's Blickensderfer always used
individual rafts, Postal always used the continuous plate) - collapsed
into one shared, user-facing toggle (`cylinder_machine.resin_raft_config`
derives `Resin_Rod_Raft`/`Cut_Groove_Inner_X` from it) since the
continuous-plate option is genuinely useful for either machine, not
something that should silently differ by default between them. Verified
all 4 combinations (each machine x both settings) watertight/winding-
consistent/`is_volume`, and confirmed both machines' `false` default and
Postal's `true` reproduce byte-identical geometry to before this change.

### Shaft Gauge Test (`GaugeTestSet`)

Ported from v2's `[Shaft Gauge Test]` section (`blickensderfer.scad`
~265-267/517-589). Not part of the real element - a standalone 6-pocket
"revolver" calibration print for empirically finding
`element.core_id_offset` (the print-tolerance addition to the shaft's
minor diameter). Each of the 6 pockets bores the shaft passage at
`gauge.offset_start + n * gauge.offset_int` (n=0..5) and is engraved with
its own offset value (`GaugeText`) so you can read off which pocket you
test-fit on the real machine. `RevolverSolid()` (the hull of the 6
cylinder pockets) uses `trimesh.util.concatenate(...).convex_hull`, the
same pattern `CoreEllipses()` already used, since trimesh has no
hull-of-solids primitive. Build via `generate.py --gauge` or tune.py's
Build tab ("Shaft Gauge").

### Calibration (`CalibrationElement`)

Ported from v2's `Cutout_Test`/`Baseline_Test`/`Test_Layout` mechanism
(`lib/testing.scad`'s `testSweepArray` + `lib/glyph_pipeline.scad`'s
`TextRing`/`TextRingDebug`, ~line 407-451) - a real, already-designed v2
feature for empirically finding the right `layout.baseline_row`/
`cutout_row` values, not invented for v4. Unlike the Shaft Gauge Test,
this IS a real element (same `Subtractive()` hollow-out as a normal
build) - only the additive text ring differs: every physical position
strikes the SAME `calibration.test_char` (v2's `Test_Layout`, always on
here - the whole point is a consistent reference shape to compare across
positions), while `calibration.vary_baseline`/`vary_cutout` (independent
booleans, matching v2's own separate `Cutout_Test`/`Baseline_Test` flags
- usually only one is on at a time, but both CAN be on together, moving
by the same shared offset) get a per-column swept offset
(`calibration.start + calibration.interval * col`, matching
`testSweepArray`) instead of its row's normal fixed value. Default
`start: -0.7` (`interval: 0.05` unchanged) sweeps from -0.7mm to +0.65mm
across the 28 columns - both below AND above the reference, not just
above it.

**The reference (the row's own normal value being swept around) is
fixed, not read from whatever config is being built.** `generate.py
--calibrate`'s reference defaults to the config being built (same as
before, for direct CLI use), but `--calibration-reference-config PATH`
loads `layout.baseline_row`/`cutout_row` from a SEPARATE file instead -
tune.py always passes the MASTER config here, never the running copy.
This matters because the Element tab's baseline/cutout fields (see
below) write to the RUNNING copy: without a fixed reference, dialing in
a value from one calibration pass would shift where the NEXT pass
centers its sweep - chasing an already-moving target instead of
converging on the master's stable original value. `CalibrationTextRing`
always prints which reference arrays it's actually using, so this is
never ambiguous from the log.

Build via `generate.py --calibrate` (plus `--calibration-char`/
`--calibration-vary-baseline`/`--calibration-no-vary-baseline`/
`--calibration-vary-cutout`/`--calibration-no-vary-cutout`/
`--calibration-start`/`--calibration-interval`/
`--calibration-reference-config` overrides) or tune.py's Build tab
("Calibration Element") + its Calibration tab's two checkboxes. Prints
one line per
physical position - keyboard key, real placement angle, and the exact
cutout/baseline value used there (computed from the actual physical
placement angle via `PLACEMENT_MAP`, not v2's raw content-order `col` -
more directly useful for correlating against the printed part, and
avoids relying on Blickensderfer's non-identity `placement_map` lining up
with v2's o'clock-from-content-order convention, which only happens to
hold for Postal's identity map). `--calibrate` also writes a `.txt`
sidecar next to the STL with the same per-position lines; tune.py's Save
copies that sidecar alongside the saved STL too (like the existing
`.yaml` metadata sidecar), when the last build was a Calibration build.

Test-fit each position on the real machine, read off which column's value
looks/fits best, and enter it directly in that row's baseline/cutout field
on tune.py's Element tab (`layout.baseline_row`/`cutout_row` - list-valued,
so not part of the generic FIELDS mechanism, but exposed as 6 bespoke
per-row fields, `patch_yaml_list_item` patching just that one element of
the inline YAML list).

### HollowSpace margin is razor-thin by design at the current settings

At `separation_mm=2.0`, the character root lands at
`Element_Diameter/2 + Char_Protrusion - separation_mm = 15.5mm` - which is
*exactly* `HollowSpace`'s outer wall radius for the rows that fall in its
wide z-band. Zero real clearance. This is exactly why the element is
built solid-then-hollowed rather than pre-calibrated: the boolean handles
either case cleanly, precise pre-calculation would be fragile here.

`generate.py` used to print whether any root vertex actually lands
inside `HollowSpace` for the current settings, as a debug diagnostic -
removed (see `SESSION_LOG.md` part 27) as redundant: it never gated or
failed the build (purely informational), flipped between `True`/`False`
run to run at low `points_per_mm` from floating-point/mesh-resolution
noise at this exact boundary anyway (not actionable), and its `.contains()`
ray-cast (no `pyembree` acceleration in this environment) could take tens
of seconds against a large enough `HollowSpace()` mesh, running silently
AFTER the STL was already written - long enough that a user watching the
build finish would reasonably quit before it returned, which meant
`tune.py`'s f3d auto-launch (gated on the subprocess's exit code) never
fired. Confirmed exactly this way for Helios (part 26 measured 33
seconds on it alone) before removing the check across every machine
instead of chasing per-machine mesh-resolution workarounds.

