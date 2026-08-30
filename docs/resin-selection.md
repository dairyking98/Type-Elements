# Resin Selection

Notes on resin material choice for printing type elements, as distinct from
`resin-supports.md` (which covers support *geometry*, not material). Kept here
because the choice is really a legibility/durability tradeoff specific to
glyph faces, not a general printing note.

---

## Priorities for this use case

Type elements are graded on one thing above all: **glyph face fidelity**.
Sharp serifs, clean stroke edges, and legible small type at the scale these
elements print at matter more than surviving a drop or a hard strike. The
elements sit in a machine and take repeated but low-energy impact against a
ribbon/platen — not the kind of abuse a handled miniature takes. That reframes
the usual "detail vs. durability" resin tradeoff: durability past a fairly low
bar is wasted margin here, and buys real fidelity loss.

The exception is thin structural features that aren't glyph faces — support
necks, drive pins, boss walls (see `resin-supports.md`) — which take bending/
torque loads, not impact, and can still snap if a resin is too brittle at a
thin cross-section. Detail-vs-durability trades off against glyph sharpness;
it doesn't excuse ignoring wall thickness at those specific spots.

**Dimensional stability over time is a co-equal priority**, added after the
fact — see its own section below. It is not in tension with fidelity; both
point away from the same family.

---

## Current setup

Recorded 2026-08-29 by reading the actual installed state, not from memory.
The rig lives on the **laptop's Windows partition** (`/media/lchau/Windows`,
user `leona`), not in this repo and not on the Windows desktop box.

| | |
|---|---|
| Printer | Anycubic Photon Mono 4K — 3840x2400, 35 um pixel pitch, 132.9 x 80 x 165 mm |
| Slicer | Anycubic Photon Workshop 4.1.8 |
| Also installed | UVtools (generated the exposure tests below); Bambu Studio (FDM, unrelated) |
| Rejected | Lychee Slicer — requires an account and network access; installed 2026-07-26, uninstalled the same day |

**Active resin profile** (`active_resins` in Photon Workshop's `.pwsp`):

    Elegoo ABS-Like 3.0
    0.05 mm layer - 3.0 s exposure - 30 s bottom x 6 layers
    lift 5 mm @ 1.33 mm/s - retract 3.5 mm/s - 0.5 s rest

Sourced from Elegoo's official settings spreadsheet, **Mars 3 row** — Elegoo
publishes no Anycubic rows at all, and the Mars 3 is the closest analog
(also 4K mono at 35 um). The 3.0 s figure is corroborated by a second
cross-brand chart; the 30 s bottom is the top of Elegoo's verified band
rather than the 35 s an unverified PDF gave. These are **vendor-chart
starting values, not measured on this machine** — see the open exposure
test below.

Profile files, for anyone repeating this:

- `%LOCALAPPDATA%\ANYCUBIC\AnycubicPhotonWorkshop_V4.1.8\machine_type\Anycubic Photon Mono 4K.pwsp`
  — the real parameter sets (`user_resins`, `active_resins`)
- `...\resin_type\custom_resin_names.json` — the picker's index; name/brand/
  density/price only, no exposure values
- Backups: `Documents\PhotonWorkshop_profile_backup` (2026-07-26)

Siraya Tech's full 37-profile catalog is imported alongside the Elegoo entry
(38 custom profiles total). That was a bulk vendor-pack import for
convenience, **not** a shortlist of considered resins — don't read the
contents of that picker as a selection history.

---

## Resins tried

| Resin | Verdict | Notes |
|-------|---------|-------|
| Generic ABS-like | Reasonable middle ground | Good general toughness, but not what maximizes satisfaction here — leaves detail on the table without buying anything this use case needs. |
| Siraya Tech Blu (tough/ABS-like family) | Too strong for this purpose | Genuinely tough, cool resin to work with, but that same toughness (added elastomeric content, higher viscosity) made it hard to get fine glyph details right — soft/blurred edges on small type. |
| Siraya Tech ABS-Like Gray ("Fast" line) | Owned; no results recorded | Official values 1.6 s / 20 s bottom. Was the original target of the 2026-07-26 profile work before switching to the Elegoo. |
| Elegoo ABS-Like 3.0 | Owned; **currently active**; no results recorded | Profile above. No print results, measurements, or glyph-fidelity notes exist for it yet. |

**Takeaway:** the strength these tough resins add isn't spent on anything the
type elements need, and it's actively traded against the one thing that is
needed (sharp glyphs). Note that **every resin in the table is ABS-like** —
including both currently owned. The family has never actually been left.

---

## Dimensional stability over time

Added 2026-08-29. Prior resin work here optimized entirely for exposure
accuracy and plate adhesion; long-term dimensional drift was never
considered, and the resins on hand are the worst available choice for it.

Why it matters for this project specifically: character pitch on a ball or
wheel is a hard constraint. On a 33.4 mm Selectric sphere, 0.5 % of drift is
~0.17 mm of position error — enough to visibly misalign a strike.

### Two distinct phenomena, often conflated

**Cure shrinkage** — 1–8 % volumetric, during print plus post-cure. One-time
and compensable with a scale factor. This is what a `shrinkage_multiplier`
is for.

**Long-term drift** — the actual concern. Three mechanisms:

1. **Dark cure.** Unreacted monomer keeps polymerizing for weeks to months.
   The largest contributor, and mostly a *process* problem rather than a
   material one — under-cured parts keep shrinking.
2. **Physical aging and creep.** The glassy network relaxes. Strongly
   dependent on service temperature *relative to Tg*: a resin with Tg near
   room temperature creeps continuously; one with Tg well above it barely
   moves.
3. **Residual monomer as plasticizer.** Incompletely washed parts stay soft
   and creep for their whole service life.

### What resists it

The two specs that predict stability are **glass transition temperature
(Tg/HDT)** and **filler content**. High Tg plus filler is stable. This
inverts the usual intuition:

- **"Tough" / "ABS-like" / flexible resins are the worst case.** They buy
  toughness by lowering crosslink density and Tg — exactly the properties
  that produce creep. This is the family both currently-owned resins belong
  to.
- **Filled resins** (glass/ceramic) shrink and creep proportionally less
  because the filler does neither. Formlabs Rigid 10K / Rigid 4000 and
  Forward AM Ultracur3D RG are the engineering-grade examples.
- **High-Tg engineering resins** — e.g. Liqcreate Strong-X, Phrozen's
  high-temp lines — are marketed on exactly this property.
- **Cationic epoxy / epoxy-acrylate hybrids** shrink ~1–2 % instead of 5–8 %
  and age far better, but are slow-curing, humidity-sensitive, and largely
  industrial.

Treat specific product names as leads to verify rather than settled facts —
vendors reformulate under unchanged product names, and datasheets rarely
disclose that shrinkage is anisotropic (Z differs from XY).

### Process matters at least as much as brand

Wash thoroughly (residual monomer is the enemy), dry fully before curing,
post-cure warm (40–60 °C) and long — ideally water-submerged to defeat oxygen
inhibition — then store away from UV and heat. Ambient UV keeps crosslinking
parts for years: they shrink and embrittle on the shelf.

### How this interacts with the fidelity-first framing above

It mostly **agrees**. Standard/high-detail resins have higher crosslink
density, higher Tg, and no elastomeric content, so moving off the
ABS-like/tough family improves sharpness *and* stability together. The
"Resins to try next" list below is not in conflict with this section.

The one genuine tension is **filled** resins: filler is the strongest lever
on creep, but raises viscosity and scatters light, which is the exact
mechanism that blurs small type. If a filled resin is ever tried here, glyph
fidelity has to be re-checked from scratch rather than assumed.

### Compensation support in the codebase

Only Hammond has a shrinkage-compensation knob —
`config/hammond.yaml`'s `element.shrinkage_multiplier` (a v2 inheritance,
currently `1.00`, i.e. off). **No other machine has any global scale
compensation.** If a real per-resin shrinkage figure is ever measured, there
is currently nowhere to apply it on the cylinder or spherical families; that
is an open design decision, not an oversight to silently patch.

---

## Direction: trade strength for detail

Standard/high-detail resins are lower-viscosity and scatter less light during
cure, which is what actually produces sharp small-scale type — not a
side effect but the direct mechanism. Moving off the ABS-like/tough family
into this category should be a straight upgrade for glyph fidelity, at a
durability cost this use case mostly doesn't need to pay.

**Resins to try next:**

- **Phrozen Aqua-Gray 8K** — formulated specifically for high-res 8K/12K mono
  LCD screens rather than repurposed general-use resin. Matte grey finish is
  a practical bonus: glyph legibility is easy to inspect straight off the
  plate, no primer needed.
- **Phrozen TR250 LV** ("Low Viscosity") — same high-resolution-screen intent
  as Aqua-Gray, explicitly marketed for fine engraved text. Also a high-Tg
  formulation, so it is the one entry on this list that serves both the
  fidelity and the stability priority.
- **Siraya Tech Fast** (or a plain "Standard", non-ABS) — if the jump to
  full detail-resin brittleness feels too far, this is the middle-ground
  fallback: tougher than Aqua-Gray/TR250, softer edges than either, but
  still meaningfully sharper than the ABS-like/Blu family. **Caveat:** Siraya
  markets its ABS-Like Grey *as* the "Fast" line, so this entry and the
  Siraya ABS-Like Gray in the table above may be the same product. Confirm
  the exact SKU before treating this as a change of family rather than a
  relabel.

---

## Open items

- **The exposure calibration was generated but never run.** Five sliced
  files at 2.0 / 2.5 / 3.0 / 3.5 / 4.0 s sit in
  `Desktop\ExposureTest_ABSLike3\` (2026-07-26): ~0.62 mL and ~13 min each,
  40 layers at 0.05 mm, carrying a glyph strip, a bullseye target, graded
  bar grids, and the settings embossed on the part. Read them by picking the
  *lowest* exposure where the glyph strip stays crisp and the bullseye rings
  stay separated. **Do this before any shrinkage measurement** —
  over-exposure causes its own dimensional bloat and would confound the
  result.
- **No shrinkage baseline exists.** A coupon with known-length features,
  printed per candidate resin and measured at 24 h / 1 week / 1 month /
  6 months, would beat any datasheet — and would give the anisotropy that
  datasheets omit. The calibration infrastructure in v4
  (`CalibrationElement` / `CalibrationTextRing`, see `calibration.md`) is
  the obvious place to build it from.
- Does Aqua-Gray/TR250 brittleness cause snapping at the support-neck /
  boss-wall features documented in `resin-supports.md`, given those already
  take bending load rather than impact? Watch the IBM boss two-tier support
  and Hammond fence joints specifically — thinnest cross-sections in the
  current support systems.
- Record actual glyph-edge results here once a batch is printed in
  Aqua-Gray/TR250, alongside which printer/pixel-size it was printed on
  (see machine notes on printer shortlist — pixel geometry and resin
  viscosity both affect edge sharpness, worth separating the two variables).
- Older resin profiles from before this rig ("profiles ive used in the
  past") were wanted for cross-reference on 2026-07-26 but were not
  accessible then, and have not been located since. If they turn up, the
  "Resins tried" table is where they belong.
