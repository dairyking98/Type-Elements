# Formlabs Form Studio 1 — evaluation and purchase plan

Companion to `printer-selection.md` (the machine) and `resin-selection.md`
(the material). Written 2026-10-15, one day after Formlabs announced the
printer, so **almost everything here is vendor data** — there is no
independent review yet. Re-check before acting on any number.

Sources: the Founders Edition store page (read directly in the browser,
2026-10-14), formlabs.com/3d-printers/form-studio-1/, the Wash+Cure product
page, the Alpha Grey TDS (rev. 2026-09-28), the press release, and one
hands-on review (Fauxhammer — **sponsored**: Formlabs supplied the unit and
hosted the reviewer). URLs at the bottom.

---

## Verdict up front

**A good fit. Buy it — the open question is the resin, not the printer.**

- **Pixel pitch is 35 µm, the same as the Photon Mono 4K — and that is
  fine.** User's call, 2026-10-15, from hands-on experience: pixel size was
  never the limiting factor on the Mono 4K, 35 µm is already past the point
  of diminishing returns for these parts, and the Formlabs print engine
  outperforms consumer MSLA at the same pitch. This **supersedes the
  "pitch is the dominant spec" framing** in `printer-selection.md` for this
  decision. (The 13 single-pixel islands on the Selectric slice are a
  geometry detail — they fall in the vat harmlessly — not a quality limit.)
- Where the edge quality actually comes from at equal pitch: a collimated
  backlight (lens array), Formlabs' pre-tuned **supersampling**
  anti-aliasing, Low Force Display peel (gentler on fine features), resin
  heating to 45 °C, validated per-resin profiles, and the Formlabs workflow
  already rated highly from past use. Those are the "collimation matters as
  much as pixel count" and "AA off" weaknesses of the Mono 4K.
- **It does not answer the shrinkage question.** No Alpha resin publishes
  shrinkage, water absorption, UV-aging or creep data, and the Alpha family
  sits in the low-HDT, high-elongation band that `resin-selection.md`
  identifies as the *worst* class for long-term stability. The stable
  Formlabs resins (Rigid 4000/10K) only run in "compatible" mode, with
  caveats (below). Stability has to be measured, on any printer — and asked
  of Formlabs directly (see "Asking Formlabs" below).

---

## Printer specs (vendor)

| | Form Studio 1 | Form 4 (for reference) | Photon Mono 4K (current) |
|---|---|---|---|
| Technology | MSLA, Low Force Display | MSLA, LFD | MSLA |
| Pixel | **35 µm** | 50 µm | 35 µm |
| Light | 28 LEDs + plano-convex lens array, 405 nm, 6 mW/cm² | 60 LEDs, 16 mW/cm² | — |
| Anti-aliasing | pre-tuned supersampling (Formlabs resins only; third-party gets a basic blur) | — | emulated greyscale, currently **off** |
| Build volume | 200 × 125 × 235 mm (5.9 L) | 200 × 125 × 210 mm | 132.9 × 80 × 165 mm |
| Layer height | 25–250 µm | 25–200 µm | — |
| Max speed | 130 mm/h (Alpha Fast); 40 mm/h average | 100 mm/h | — |
| XY tolerance, 1–30 mm | **±0.5 %** (floor ±0.08 mm) | ±0.15 % (floor ±0.02 mm) | not measured |
| XY tolerance, 31–80 mm | ±0.2 % (floor ±0.08 mm) | ±0.2 % (floor ±0.06 mm) | |
| Resin handling | auto-dispense from 1 L cartridge; resin heated to 45 °C | auto + mixer | manual pour |
| Filled-resin mixer | **none** | yes | none |
| Connectivity | Wi-Fi, Ethernet, USB-C; camera (can be capped/disabled/unplugged) | | USB stick |
| Software | PreForm only — "not compatible with third-party slicers" | | Photon Workshop |
| Reliability | "testing in progress"; page variously says 99 % and 92 % | 98.7 % (independent) | |
| Warranty | 1 year | | |

### Things in that table that matter here

- **±0.5 % on 1–30 mm features.** A Selectric element is ~25–33 mm, so this
  is ±0.13–0.17 mm — the same magnitude `resin-selection.md` calls "enough to
  visibly misalign a strike". It is notably looser than the Form 4 in exactly
  our size band. *If* the error is systematic (a scale), it is compensable;
  if it is part-to-part scatter, it isn't. Unknown until measured.
- **No mixer.** Rigid 4000/10K are glass-filled; filler settles. On this
  printer that means shaking the cartridge and stirring the tank by hand
  before every print — and is a reason the stable resins are "compatible",
  not "supported".
- **Supersampling AA is Formlabs-materials-only.** Third-party resins in
  Open Material Mode (e.g. Phrozen TR250 LV, Elegoo ABS-Like 3.0) get a
  basic blur. Whether *non-native Formlabs* resins (Rigid 4000) get the full
  supersampling is unconfirmed.

---

## Packages and add-ons (store page, 2026-10-14, excl. tax)

| Item | Price | Notes |
|---|---|---|
| **Base** | $699 | printer, Resin Tank, aluminium Build Platform. Ships by Nov 24 |
| **Complete** | **$948** | printer, Resin Tank, **Build Platform Flex**, **Form Studio Wash+Cure**. Ships by **Jan 8** |
| **Professional** | $1,647 | printer, Resin Tank, Build Platform Flex, Form Wash V2 + Form Cure V2. Ships by Nov 24 |
| Founders perks (all packages) | — | first Alpha bottle $29, 30 % off up to $200 at Form Now, accessories box. Through **Nov 30** or while stock lasts |
| Resin Tank | $55 | Alpha resins, Flexible 80A, True Cast |
| Resin Tank Pro | $79 | **required** for Tough 1500 V2, non-Alpha Formlabs resins, and all third-party resin |
| Build Platform Flex | $135 | quick-release |
| Build Platform (aluminium) | $65 | |
| Build Platform Jig | $35 | |
| VOC Extractor | $179 | GREENGUARD Gold only with Alpha + this; pushes delivery to Jan 22 |
| Wash+Cure Rinse Bucket | $59 | second bucket for a two-stage wash |
| Form Cure V2 (120 V) | $499 (list $999) | **heated** cure |
| Form Wash V2 | $399 (list $699) | |
| Pro Service Plan | $99 / 1 yr, $199 / 3 yr | priority support, extended warranty, accidental coverage |

Tanks: rated for **>75,000 layers** (≈190 prints of 39 mm at 100 µm). The
film is **not replaceable** — a worn tank is a whole new tank. No lockout
at the rating, per the review.

### Form Studio Wash+Cure ($199 standalone; included in Complete)

10 L bucket, magnetic impeller, IPA / TPM / Resin Washing Solution, basket
lifts out to drip-dry. Cure: 24 LEDs at 405 nm, 48 W, 24 cm turntable,
24.5 cm max part height. **No heater.**

That last point matters for stability: `resin-selection.md` recommends a
warm (40–60 °C) post-cure to defeat dark cure, and Formlabs' own Alpha Grey
TDS lists the "max strength" cure as 5 min **at 60 °C in Form Cure V2** —
the Wash+Cure default is 5 min unheated. Rigid 10K requires heat outright.

---

## Resins (store page and TDS)

All Alpha resins: 1 L / 1.1 kg cartridges, Form Studio 1 only (not Form 4),
standard Resin Tank. "Skin-safe after post-processing", low odour.

| Resin | $ /L | UTS MPa | Modulus MPa | Flex. str. MPa | Elong. % | Izod J/m | HDT @0.45 MPa | Layer | Avg speed | Pitch |
|---|---|---|---|---|---|---|---|---|---|---|
| **Alpha Model** | 42 | 40 | 1980 | 57 | 24 | 35 | **49 °C** | 50 µm | 13 mm/h | "best fine features, most matte" |
| Alpha Fast | 29 | 46 | 2230 | 78 | 34 | 37 | 59 °C | 150 µm | 90 mm/h | fastest |
| **Alpha Grey** | 36 | 43 | 2150 | 75 | 34 | 39 | 55 °C (48 @1.8 MPa; Tg 88 °C; Shore 74D) | 100 µm | 40 mm/h | speed/aesthetics |
| Alpha Clear | 36 | 38 | 1870 | 63 | 32 | 39 | 57 °C | 100 µm | 40 mm/h | |
| Alpha Black | 36 | 42 | 2020 | 65 | 36 | 33 | 55 °C | 100 µm | 40 mm/h | |
| Alpha White | 36 | 35 | 1690 | 63 | 26 | 34 | 51 °C | 100 µm | 40 mm/h | |
| Tough 1500 V2 | 79 | 34 | 1460 | 41 | 155 | 42 | 66 °C (53 @1.8) | — | — | PP-like; **Resin Tank Pro** |
| Flexible 80A V2 | 199 | | | | | | | | | elastomer; skipped for now |
| True Cast | 199 | | | | | | | | | wax-filled casting resin |

**Not published for any Alpha resin:** shrinkage (cure or long-term),
water absorption, UV aging/yellowing, creep. The Alpha Grey TDS was checked
specifically.

### "Compatible" Formlabs resins (Resin Tank Pro, cartridge dispensing, your own settings)

Rigid 4000 (glass-filled), Rigid 10K (glass-filled, needs heated cure),
Tough 2000 V2 (HDT 70 °C, "creep resistance"), Grey/White/Black/Clear V5,
Precision Model, High Temp, Fast Model, and others. **Not listed:** Grey Pro,
Draft. Formlabs warns that performance "may be lower" and properties "may
differ from published values" in this mode.

### Assessment against this project's priorities

- **Glyph fidelity:** Alpha Model is the obvious pick — it is the one resin
  explicitly tuned for fine features, at 50 µm layers, with thin features
  that "flex instead of snapping" (relevant to the support necks and boss
  walls in `resin-supports.md`). The review notes the first Alpha Model
  profile printed fat support tips; Formlabs shipped a fixed profile.
- **Stability:** every Alpha resin has HDT 49–59 °C and 24–36 %
  elongation — the toughened, lower-crosslink profile that
  `resin-selection.md` flags as most prone to creep and dark-cure drift.
  Alpha Black has the highest published Tg (91 °C; 99 °C with heated
  cure), Grey 88 °C. Alpha Model, the fidelity pick, has the *lowest* HDT. That is the real
  tradeoff on this machine.
- **Tough 1500 V2:** not for type elements — lowest modulus of the lot and
  155 % elongation; glyphs need stiffness.
- **Rigid 4000/10K** are the strongest stability candidates the printer can
  run, but in compatible mode: no validated profile, hand-mixing filler with
  no mixer, AA support unconfirmed, and Rigid 10K needs a heated cure the
  Wash+Cure can't give. Filler also scatters light, so glyph fidelity has to
  be re-checked from scratch.

---

## Openness

- **No Linux PreForm.** Windows/macOS only; Wine reports are poor (black
  window on Wine 9–10, USB unverified). PreForm runs on the Windows desktop
  (`desktop.lan`, .88) and talks to the printer over Ethernet/Wi-Fi on the
  LAN or by USB-C. Fits requirement 4 of `printer-selection.md` ("Windows is
  fine").
- **Closed slicer** — PreForm only. A step backwards from requirement 2 in
  tooling terms (UVtools would not apply).
- **Open Material Mode is included free**, so any 405 nm resin can be
  printed, at the cost of manual pour, own exposure (set as energy dose, not
  seconds), the $79 Pro tank, and basic-blur AA only.
- Works offline over USB-C per the review; account requirement and firmware
  lock-in are not stated anywhere.

Net: more closed than the Anycubic in slicer terms, more open than its
reputation in material terms. Requirement 2 ("open-sourcey") is traded for
requirement 3 (the Formlabs experience).

---

## Purchase plan — optimized for bang for buck

Rule applied: buy only what the first month of printing will use; defer
anything whose need a test will decide; take every launch discount that
costs nothing extra.

### Why Complete, not Base or Professional

| Route | Cost | Gets you |
|---|---|---|
| Base | $699 | printer, standard tank, aluminium platform — no wash/cure |
| Base + Flex ($135) + Wash+Cure ($199) à la carte | $1,033 | = Complete, plus a spare aluminium platform |
| **Complete** | **$948** | printer, tank, Flex platform, Wash+Cure — **$85 under à la carte** |
| Complete + Form Cure V2 ($499) | $1,447 | adds heated cure; still keeps the Wash+Cure |
| Professional | $1,647 | Wash V2 + Cure V2 instead of Wash+Cure — **$200 more** than the row above for less kit |

Complete is the value point. Professional is never the efficient choice:
if heated cure is ever needed, Complete + Cure V2 is $200 cheaper.
*Exception:* if an Anycubic (or other 405 nm) wash & cure station is
already on hand, Base + Flex ($834) saves $114 — but the Formlabs Wash+Cure
is unheated too, so it is not a capability downgrade either way, and Base
loses the Flex plate's value for small, hard-to-pry parts.

### The cart

| Tier | Item | Price | Running total |
|---|---|---|---|
| Core | Form Studio 1 **Complete** — colour **Aqua** (Founders, user's pick 2026-10-15) | $948 | $948 |
| Core | **Alpha Model** (founders: first Alpha bottle $29, list $42) | $29 | $977 |
| Recommended | **Alpha Black** | $36 | $1,013 |
| Recommended | Extra standard Resin Tank (one per resin) | $55 | **$1,068** |
| Optional | Wash+Cure Rinse Bucket (two-stage wash) | $59 | $1,127 |

**$1,068** is the recommendation — no sales tax, shipping to Oregon (resins/tanks may still add shipping). Core alone ($977) is a complete,
working setup if a second resin can wait.

Spend the $29 first-bottle discount on **Alpha Model** — it is the dearest
Alpha ($13 saved), whereas on Alpha Fast it would save nothing.

### Alpha Black vs Alpha Grey — Black

Mechanically they are a wash: Black 42 MPa / 2020 MPa / 36 % / HDT 55 °C,
Grey 43 MPa / 2150 MPa / 34 % / HDT 55 °C. So the choice is decided by
optics and aging, and both favour Black:

- **UV aging.** The concern is ambient UV continuing to cure (shrink,
  embrittle) parts on the shelf. A dense black pigment confines UV
  absorption to the outer skin — the same reason carbon black is the
  standard UV stabilizer in commodity plastics. *General polymer practice,
  not Formlabs data* — whether Alpha Black is carbon-pigmented is
  unpublished, and it is one of the questions for Formlabs below.
- **Edge sharpness.** Strongly pigmented resins limit light bleed past the
  exposed pixel (less over-cure), which tends to help fine features.
- **Cost of the choice:** black is the hardest colour to *inspect* — fine
  glyph defects don't show without raking light or a macro photo. Alpha
  Model (matte neutral) covers inspection, so carrying Black as the second
  resin costs nothing there.

The TDS confirms it (Alpha Black, rev. 2026-09-28): **Tg 91 °C** default
post-cure / **99 °C** max-strength (60 °C Form Cure V2) vs Grey's 88 °C;
HDT 55.5 / 48.1 °C (0.45 / 1.8 MPa), 58 / 50.4 °C max-strength; Shore 72D.
No water absorption, shrinkage, UV-aging or pigment data. Black is
marginally the *more* stable on the one stability proxy published.

### Deferred — buy only when a test says so

| Item | Price | Trigger |
|---|---|---|
| Resin Tank Pro | $79 | only to try Rigid 4000 (stability) or a third-party resin. With the printer choice settled, the ABS-Like 3.0 A/B comparison is no longer worth $79 |
| Form Cure V2 (heated) | $499 (list $999) | only if the shrinkage coupon shows Alpha resins drifting and heated cure is the fix. *Ask Formlabs whether $499 is launch-only* — if it is, revisit before Nov 30 |
| Rigid 4000 | — | after the Pro tank, if Alpha drifts |
| VOC Extractor | $179 | only if the printer lives in a living space; delays delivery to Jan 22 |
| Flexible 80A V2 | $199 | parked by user, 2026-10-15 |

### Skip

Service plan (1-year warranty covers launch defects), Tough 1500 V2,
True Cast, Form Wash V2, extra build platforms. The Founders "30 % off at
Form Now" perk is a print *service* credit — no value here.

### Running costs not on the store page

- **IPA:** the Wash+Cure bucket is 10 L. Filling it is a real first-day
  cost; factor in a few litres of 99 % IPA, or use TPM / Resin Washing
  Solution (also supported).
- **Tanks** are consumables (>75,000 layers, non-replaceable film): $55
  each, roughly every ~190 average prints.
- **Shipping:** free for the printer only; resins/tanks may add shipping.

### Timing

- Founders pricing/perks run **through Nov 30**. Complete ships by **Jan 8**
  (Base/Professional by Nov 24); the press release says shipping starts
  Nov 16.
- Use the wait: start the shrinkage coupon now so there is a clock already
  running when the Studio 1 arrives.

---

## Asking Formlabs

There is no published answer on Alpha resin aging, so ask. Pre-purchase
questions go to **Sales**: https://formlabs.com/company/contact/sales/
(fields: first/last name, business email, phone, country, "How can we help
you?"; "aim to respond within 10 minutes" in business hours) or call
**+1 833 489 0545** (9–6 ET). Technical support for owners:
https://support.formlabs.com/s/contact-support

**Sent 2026-10-15** via the Sales form (reply to dairyking98@gmail.com / phone). The
final version asked three questions — the draft below was trimmed and edited
before sending: (1) shrinkage / long-term stability / water-absorption data for
*every* resin Studio 1 runs (all Alpha, Tough 1500 V2, Rigid 4000/10K, Tough 2000
V2, Grey V5) and which is most stable; (2) whether heated cure in Form Cure V2
reduces long-term shrinkage/creep or only adds strength; (3) whether $948 Complete
and the $499 Cure V2 add-on are launch promotions, until when, and whether Cure V2
can be added at $499 after the printer order. **Reply: pending** — record it here.

Original draft (superseded):

> I'm planning to buy a Form Studio 1 Complete (Founders Edition) to print
> small precision parts (~25–33 mm) where dimensional stability over years
> matters more than toughness. Before I order:
>
> 1. Do you have data on post-cure shrinkage and long-term dimensional
>    stability for the Alpha resins — especially Alpha Model and Alpha
>    Black — e.g. dimensional change over months, under ambient UV, and
>    with humidity? Water absorption figures?
> 2. Does heated post-cure (Form Cure V2 at 60 °C) improve long-term
>    stability versus the unheated Wash+Cure, or only strength?
> 3. Is Alpha Black pigmented with carbon black (i.e. UV-blocking)?
> 4. Is the XY tolerance on 1–30 mm features (±0.5 %) mostly a systematic
>    scale error that can be compensated, or part-to-part variation?
> 5. Do "compatible" Formlabs resins like Rigid 4000 get the same
>    supersampling anti-aliasing on Form Studio 1 as Alpha resins? And
>    without a mixer, how should glass-filled resins be handled?
> 6. Is the $499 Form Cure V2 price a launch promotion, and until when?
> 7. What is the return policy on Form Studio 1?

Submitting it means entering your name/email/phone — do that yourself, or
say the word and Claude fills it in the open tab for you to review before
sending.

---

## Before and after it arrives

1. **Now:** send the Formlabs questions above.
2. **Now:** build the shrinkage coupon (`resin-selection.md` open items) and
   print it in Elegoo ABS-Like 3.0 on the Mono 4K. Measure at 24 h / 1 wk /
   1 mo / 6 mo, half in a dark box, half on a windowsill. This is the only
   multi-month item, and nothing Formlabs publishes substitutes for it.
3. **Day one:** print the same Selectric element and the same coupon in
   Alpha Model and Alpha Black; start their clocks too. Check whether the
   ±0.5 % XY error is a consistent scale (compensable) or scatter.
4. If Alpha resins drift on the coupon: buy the Pro tank and trial
   **Rigid 4000** (hand-stirred), and decide on Form Cure V2 then.
5. Record results here and in `resin-selection.md`'s table.

---

## Open questions

- Real-world XY accuracy on ~25–33 mm parts — systematic or random?
- Does supersampling AA apply to non-native Formlabs resins (Rigid 4000)?
- Alpha resin long-term dimensional stability — unpublished; asked of
  Formlabs, and the coupon test regardless.
- Alpha Black pigment (carbon black?) — unpublished; asked of Formlabs.
- Return policy — check before ordering.
- Account requirement and firmware downgrade policy — unstated.

---

## Sources

- Store page: https://formlabs.com/products/form-studio-1-complete-founders-edition/
- Product page: https://formlabs.com/3d-printers/form-studio-1/
- Wash+Cure: https://formlabs.com/products/form-studio-wash-cure/
- Alpha Grey TDS: https://formlabs.com/materials/tds/alpha-grey-resin/
- Studio 1 material compatibility: https://formlabs.com/products/materials/form-studio-1/
- Press release (2026-10-14): https://formlabs.com/company/press/formlabs-introduces-form-studio-1/
- Fauxhammer review (sponsored): https://www.fauxhammer.com/news/formlabs-form-studio-1-review-the-new-benchmark-for-home-resin-printing-2/
- DEVELOP3D launch coverage: https://develop3d.com/3d-printing/form-studio-1-entry-level-formlabs/
- PreForm on Linux thread: https://forum.formlabs.com/t/preform-for-linux-desktop/46338
- Post-build shrinkage from continued cure (Chartoff 1993): https://utw10945.utweb.utexas.edu/Manuscripts/1993/1993-28-Chartoff.pdf
