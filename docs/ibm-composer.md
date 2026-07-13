# IBM Composer — Reference

**File:** `IBM/IBM2.scad` (collaborative with Otto Koponen, Nov–Dec 2024)

---

## What the IBM Composer is

The IBM Selectric Composer (1966) is a proportional-spacing variant of the Selectric typeball. Unlike a standard Selectric (fixed-pitch), the Composer assigns each character a discrete unit width. The operator types a line once to count units, then types it again with the correct justification offset. Output was used as camera-ready copy for offset printing before desktop publishing.

The Composer ball is **dimensionally identical** to a Selectric I/II ball — physically interchangeable. The difference is in the machine's escapement mechanism, not the ball geometry.

---

## Proportional unit system

Every character has an assigned width in **units**. A unit is a fraction of a pica:

| Ball color | Units/pica | Units/inch | `UNITSPERINCH` |
|------------|-----------|-----------|----------------|
| Red | 12 | 72 | 72 |
| Yellow | 14 | 84 | 84 |
| Blue | 16 | 96 | 96 |

`UNITDIST = 25.4 / UNITSPERINCH` gives mm per unit.

### Unit widths per character (`COMPOSER_PITCH_LIST`)

| Width | Characters |
|-------|-----------|
| 9 units | M, W, m |
| 8 units | A, D, G, H, N, O, Q, T, U, V, X, Y, Z, n, o, u, w, x, y, €, ¥ |
| 7 units | B, C, E, F, K, L, P, R, S, b, c, d, e, g, h, k, l, p, q, r, s, t, v, z |
| 6 units | J, a, †, —, –, ˆ |
| 5 units | I, f, 0–9, !, ?, &, ¡, ¿, ¼, ½, ¾, %, (, ), ´, ç |
| 4 units | . , : ; ' " ` ¨ |
| 3 units | i, j, space |

Range is 3–9 units. This matches the published IBM Composer unit table.

### Type test line (`TextGaugeComposerLine2`)

Renders a physical type test by looking up each character's unit width in `COMPOSER_PITCH_LIST`, computing prefix sums with `cumulativeSum()`, and translating each character to `cumulativePicas[i] * UNITDIST` mm from the left margin. Print the test slab, ink it, press against paper to verify spacing.

---

## Hemisphere mapping (keyboard → ball position)

The physical position of characters on the ball does NOT match keyboard order. Two independent maps are used:

```openscad
// Composer: keyboard position → hemisphere index
COMPOSER_HEMISPHERE_MAP = [[6],[9],[3],[4],[21],[2],[20],[10],[8],[7],[12],[33],
                            [41],[31],[38],[28],[18],[37],[24],[16],[29],[36],[11],
                            [17],[5],[30],[39],[40],[26],[43],[32],[15],[34],[13],
                            [35],[22],[14],[23],[19],[27],[25],[1],[0],[42]];

// Selectric I/II: different map
S12_HEMISPHERE_MAP = [[10],[4],[9],[6],[3],[2],[8],[7],[0],[1],[33],[37],[35],[22],
                      [14],[30],[16],[34],[20],[24],[28],[36],[27],[29],[23],[19],
                      [42],[43],[12],[38],[13],[17],[41],[25],[5],[21],[18],[31],
                      [11],[15],[32],[40],[26],[39]];
```

`LATITUDE_LONGITUDE` converts these to `[latitude_index, longitude_row, char, keyboard_index]` tuples for rendering.

---

## Composer vs Selectric differences in the model

| Feature | Composer | Selectric I/II |
|---------|---------|----------------|
| `RENDER_MODE` | 0 | 1 |
| `H_ALIGNMENT` | `"left"` | `"center"` |
| Platen OD | 43 mm | 36 mm |
| `X_POS_OFFSET` | 1.20 mm | 0 mm |
| `Y_POS_OFFSET` | -1.30 mm | -1.5 mm |
| Font size input | `COMPOSER_CAP_HEIGHT` in **points** (÷2.834 to get mm) | `FONT_SIZE` in mm |
| Hemisphere map | `COMPOSER_HEMISPHERE_MAP` | `S12_HEMISPHERE_MAP` |

When `CUTOUT_TEST=true`, `H_ALIGNMENT` is forced to `"center"` and position offsets zero out to remove variables during calibration.

---

## Per-character alignment overrides

```openscad
CUSTOMHALIGNCHARS = "..."  // characters needing custom horizontal alignment
CUSTOMVALIGNCHARS = "..."  // characters needing custom vertical alignment
FONT2CHARS = "..."         // characters rendered in secondary font FONT2
```

These are separate from the global `Character_Modifieds` system used in cylinder elements.

---

## Current alignment model (frozen — migration candidate)

**Do not touch this section's code without recalibrating from scratch — Composer's geometry is already physically tuned.** Noted here only so a future migration onto the shared `glyph_pipeline.scad` alignment methods (see [text-centering.md](text-centering.md)'s proposed `Text_Align_Method`) can be checked for bit-identical output before it replaces this.

Composer already implements, by hand, the same idea as the proposed `textmetrics_left` method — it just predates `textmetrics()` and uses a hand-authored width table instead of live font metrics:

- **Ball placement** (`Text()` in `ibm.scad`): `H_ALIGNMENT="left"` for Composer (vs `"center"` for Selectric I/II) — i.e. natural/un-shifted glyph rendering, not ink-bbox centering. Per-character correction comes from `CUSTOMHALIGNCHARS`/`CUSTOMHALIGNOFFSET` (and the `Y` equivalents), an additive `translate` applied on top of the natural render — conceptually the same per-character override pattern as `Character_Modifieds_Offset` elsewhere, but Composer's own table, kept separate ("These are separate from the global `Character_Modifieds` system used in cylinder elements").
- **Type test line** (`TextGaugeComposerLine2`): each character is rendered `halign="left"` (natural, unshifted) and placed via `translate([Cum_Sum_Test_String_Picas[i]*unitdist, 0])` — a running cumulative sum of `COMPOSER_PITCH_LIST` unit widths (IBM's published per-character unit table, not a measured font metric). This is exactly the escapement model: pin each glyph's natural pen origin to a computed left position and let it advance from there, rather than centering it in a slot.

The difference from the proposed `textmetrics_left` method is only the source of the per-character width: Composer uses `COMPOSER_PITCH_LIST` (a fixed table matching the physical machine's published unit spacing), while the new method would derive the same kind of value live from `textmetrics()`'s `advance`/`position` fields. If the two are ever unified, the check is whether `textmetrics()` on the actual font in use reproduces `COMPOSER_PITCH_LIST`'s unit widths closely enough — if not, Composer should keep its own table rather than drift from its calibrated state.

---

## Snoot droop compensation

`SNOOT_DROOP_COMPENSATION=0.42 mm` — the boss face droops downward under gravity during resin curing (ball is printed with boss facing the vat). This lowers the boss height in the model by 0.42 mm so the printed boss measures exactly correct (8.5 mm from top flat to boss face).
