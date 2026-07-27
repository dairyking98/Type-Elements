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

---

## Resins tried

| Resin | Verdict | Notes |
|-------|---------|-------|
| Generic ABS-like | Reasonable middle ground | Good general toughness, but not what maximizes satisfaction here — leaves detail on the table without buying anything this use case needs. |
| Siraya Tech Blu (tough/ABS-like family) | Too strong for this purpose | Genuinely tough, cool resin to work with, but that same toughness (added elastomeric content, higher viscosity) made it hard to get fine glyph details right — soft/blurred edges on small type. |

**Takeaway:** the strength these tough resins add isn't spent on anything the
type elements need, and it's actively traded against the one thing that is
needed (sharp glyphs).

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
  as Aqua-Gray, explicitly marketed for fine engraved text.
- **Siraya Tech Fast** (or a plain "Standard", non-ABS) — if the jump to
  full detail-resin brittleness feels too far, this is the middle-ground
  fallback: tougher than Aqua-Gray/TR250, softer edges than either, but
  still meaningfully sharper than the ABS-like/Blu family.

---

## Open questions for next round

- Does Aqua-Gray/TR250 brittleness cause snapping at the support-neck /
  boss-wall features documented in `resin-supports.md`, given those already
  take bending load rather than impact? Watch the IBM boss two-tier support
  and Hammond fence joints specifically — thinnest cross-sections in the
  current support systems.
- Record actual glyph-edge results here once a batch is printed in
  Aqua-Gray/TR250, alongside which printer/pixel-size it was printed on
  (see machine notes on printer shortlist — pixel geometry and resin
  viscosity both affect edge sharpness, worth separating the two variables).
