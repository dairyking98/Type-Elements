# Text Centering & Dead Space (Technical Reference)

Every machine file calls `text()` with `halign="center"` (see [glyph-pipeline.md](glyph-pipeline.md) Step 1, `2DText(char)`). This doc covers what that centering actually does, why it matters for a typewriter element specifically, and what to do about it.

---

## What `halign="center"` actually centers on

OpenSCAD does not center on the font's advance width (the fixed pitch/em-box a monospace font defines for every glyph). It centers on the **ink bounding box** — the min/max X of the actual rendered outline geometry.

- Advance width is a layout metric: how far the "cursor" moves before the next glyph. In a monospace font this is constant across all characters (that's the whole point of monospace).
- Ink bounds are whatever the glyph's outline actually draws. A `.` or `1` or `i` can occupy a small fraction of the advance width; a `M` or `W` occupies nearly all of it.

`halign="center"` (and `halign="right"`/`"left"`) ignores the advance width and centers/aligns the ink box only. So for a glyph with a 1000-unit advance width but only 200 units of ink, centering does **not** split at the 500-unit mark of the em box — it centers the 200-unit shape wherever its ink happens to sit, and the ~800 units of side bearing are simply dropped from the calculation.

This also means bounding-box centering isn't the same as optical centering: a glyph like lowercase `j` has ink that includes a descender curl well to the left of the vertical stroke, so bbox-centering can visibly shift the stroke off from where the eye expects "centered" to land.

---

## Why this matters here specifically

Every element (Blickensderfer, Bennett, Mignon, Hammond, IBM, Postal) places one character per fixed circumferential slot via `LetterPlacement()` / `TextRing()` (see glyph-pipeline.md Step 2). The slot position is fixed by the layout array and `latitudeInt`, independent of which character occupies it — the code assumes each glyph is centered the same way relative to its slot.

Because centering is ink-bbox-based, not advance-width-based, narrow glyphs (`.`, `,`, `'`, `1`, `i`, `l`) can sit visually off-center within their slot compared to wide glyphs (`M`, `W`, `H`), even though the underlying `text()` call is identical apart from the character. On a physical strike element this shows up as inconsistent left/right ink position per character around the same latitude band — most noticeable on narrow punctuation and numeral glyphs, and on monospace fonts where the whole point of the font is that every slot should look uniformly placed.

The project already has a mechanism for the vertical equivalent of this problem — `Character_Modifieds` + `Character_Modifieds_Offset` shifts specific characters vertically (e.g. `` ` `` accents, `_` baseline). There is currently **no horizontal equivalent**.

---

## Options for accounting for dead space

### 1. Per-character horizontal offset (mirrors the existing vertical mechanism)
Add a `Character_Modifieds_X_Offset` (or fold into the existing `_Offset` as an `[x,y]` pair) and apply it as a `translate([x_offset, 0, 0])` around the `text()` call in `2DText(char)`, the same way `Character_Modifieds_Offset` already nudges vertically. Lowest effort, consistent with the existing pattern, but values are found empirically per font/char (same as baseline calibration).

### 2. `textmetrics()` — compute real advance width and self-center
Recent OpenSCAD dev snapshots expose `textmetrics(text=char, size=_useSize, font=_font)`, which returns the actual advance (`advance_x`) and the ink bounding box (position + size) separately. Instead of relying on `halign="center"`, use `halign="left"` and manually `translate([-advance_x/2, ...])` (or center on the bbox `textmetrics()` reports, whichever convention the layout wants). This gives explicit control and removes the guesswork of option 1 — it's the correct long-term fix, but it requires a dev snapshot with `textmetrics()` support and touches every call site in `2DText(char)`.

### 3. Force a consistent bounding box via an invisible reference shape
`union()` the glyph with two zero-size (or negligible, e.g. 0.001mm) markers placed at `(0,0)` and `(advance_width, glyph_height)` before centering, then `difference()` them back out (or just leave them — at that size they don't affect the printed geometry). This expands the bbox OpenSCAD centers on to match the full advance box rather than the ink box, without needing `textmetrics()`. Cheap trick, but the "known" advance width has to come from somewhere — either measured once per font (most monospace fonts publish it, e.g. via `fc-query` or the font's `hmtx` table) or approximated from a wide reference glyph (see option 4).

### 4. Reference-glyph trick: render as `text="H" + char`, discard the `H`
Render the target character in the same string as a known wide reference glyph (e.g. `M` or `H`), let bbox-centering use their combined ink extent, then keep only the target glyph's geometry (e.g. via a bounding cutout matching where the reference glyph would fall, or extruding at different heights and slicing). More fragile and harder to reason about than options 1–3; only worth it if `textmetrics()` isn't available and per-character calibration (option 1) is too slow to do for a large character set.

### 5. Do nothing for wide/symmetric glyphs, calibrate only the offenders
Not every glyph needs correction — wide glyphs (`M`, `W`, `H`, most uppercase and most digits in a true monospace font) already have ink extent close to the advance width, so bbox-centering and advance-centering roughly agree. In practice only a handful of narrow/asymmetric glyphs per font (`.`, `,`, `'`, `1`, `i`, `l`, `j`) need a correction at all. Combine with option 1: only populate `Character_Modifieds` for the glyphs that visibly need it, found the same way `charBaselines` sweeps are done today (see [calibration.md](calibration.md)).

---

## Recommendation

Option 1 (per-character horizontal offset) is the natural next step — it reuses the existing `Character_Modifieds` calibration workflow and requires no OpenSCAD version bump. Option 2 (`textmetrics()`) is the more correct fix if/when the project's minimum required OpenSCAD snapshot already includes it, since it removes per-font/per-character guesswork entirely rather than calibrating around it.

---

## Implemented: `Text_Align_Method` — selectable alignment behavior

Implemented in `AlignedText()` in `v2/lib/glyph_pipeline.scad` (used by `TwoDText()` in place of the old hardcoded `halign="center"` text() calls). Exposed as a Customizer setting alongside the other unified glyph-quality features. This lets a well-designed font (correct side bearings) just work, while a font with quirky metrics can fall back to legacy centering.

For a typewriter specifically, "dead center" is not always correct — e.g. a `.` sitting at true ink-bbox-center reads as too high/central for how a typebar actually strikes a period. Real typewriter fonts are drawn with the period's ink intentionally off-center within its own advance box (slightly left, typically), and that's the behavior that should survive into the model, not get erased by bbox-centering.

All three modes below render the same physical glyph outline — they differ only in the `translate()` applied before the un-centered (`halign="left"`) render. `P` = the fixed physical slot pitch, computed as `25.4/Test_CPI` — reusing the `Test_CPI` global every v2 machine file already declares for its own type-test string escapement (`translate([1/Test_CPI*25.4*n, ...])`), rather than introducing a new pitch parameter. `textmetrics(...)` returns three fields per glyph:

```
0                    position.x         position.x+size.x              advance.x
|                         |                    |                            |
pen origin ─────── LSB ──►│◄──── ink (size.x) ─►│◄──────── RSB ─────────────►│ next glyph's pen origin
```

- `position.x` = left side bearing (LSB) — gap from pen origin to first ink pixel.
- `size.x` = ink width.
- `advance.x` = full pen-to-pen pitch = LSB + ink width + RSB. This is a per-glyph value read from the font, distinct from `P`.

| Method | Formula (before `text(..., halign="left")`) | Behavior |
|---|---|---|
| `halign_center` (current default) | `translate([-(position.x + size.x/2), 0])` | Centers the **ink**. Ignores side bearing entirely — a `.` lands dead-center in its own ink box regardless of what the font designer intended. This is today's behavior everywhere. |
| `textmetrics_center` | `translate([-advance.x/2, 0])` | Centers the glyph's **own advance box** (per-glyph `advance.x`), preserving whatever LSB/RSB asymmetry the font was drawn with. For a well-drawn typewriter font, a `.` naturally ends up slightly left-of-center here — because the font says so, not because we special-cased it. |
| `textmetrics_left` | `translate([-(25.4/Test_CPI)/2, 0])` | Pins the natural pen origin (unshifted `halign="left"`) to the slot's fixed left edge `-P/2`. Does **not** reference `position.x`/`size.x`/`advance.x` at all — no `textmetrics()` call needed for this mode. The font's native LSB shows up in the final ink position automatically (ink lands at `-P/2 + position.x`), simply because nothing shifted it away. This is the "Composer style" — `TextGaugeComposerLine2` already does exactly this (cumulative-width translate + plain `halign="left"`, no further ink-based correction), just with hand-authored widths instead of live `textmetrics()`. |

`advance.x` and `P` are deliberately different: `advance.x` is per-glyph (from the font itself), `P` is the fixed slot pitch derived from `Test_CPI` and shared by every character in the row regardless of its own metrics. They only coincide for a character whose own `advance.x` happens to equal `P` (i.e. the font is genuinely monospaced at exactly the target CPI).

### `Text_Align_X_Offset` — universal fine-tune, layered on all three methods

A single mm nudge added to whichever method's base `translate()` runs, so switching methods doesn't lose a manual correction. Defaults to 0 (no-op), same pattern as `Baseline_Z_Offset`/`Font_Weight_Offset` elsewhere in the file. This is the horizontal counterpart to the vertical `Character_Modifieds_Offset` mechanism, but global rather than per-character — a per-character `X` table (`Character_Modifieds_X_Offset`, mirroring the existing `_Offset`) is still open as a future addition (see Option 1 above) if a global nudge isn't granular enough once real fonts are tested.

### Implementation notes
- Requires an OpenSCAD snapshot with `textmetrics()` — already satisfied (README already points at a dev snapshot). **But `textmetrics()` is also gated behind OpenSCAD's experimental-feature flag**, separate from just having a new-enough snapshot: enable it via Edit → Preferences → Features → check "Text Metrics" in the GUI, or pass `--enable=textmetrics` for any CLI/headless render or STL export. Verified by rendering `Text_Align_Method=1` both ways: **without** the flag, OpenSCAD does not error — it prints easy-to-miss console warnings (`Ignoring unknown function 'textmetrics'`, `undefined operation`) and silently renders the glyph as if untranslated, i.e. it quietly falls back to unshifted `halign="left"` positioning instead of centering on the advance box. That's a wrong-geometry-with-no-error failure mode, exactly the kind that could ship into a physical part unnoticed. `Text_Align_Method=2` (`textmetrics_left`) is unaffected since it never calls `textmetrics()`.
- Implemented as a new `AlignedText(char, font, size)` module in `v2/lib/glyph_pipeline.scad`, called from all three `TwoDText()` branches (additive/subtractive/none weight-adjust) in place of the old duplicated `text(..., halign="center")` calls — one code path for all methods instead of four copies.
- **Declared in the Customizer** in all six lib-wired v2 machine files (`blickensderfer.scad`, `postal.scad`, `bennett.scad`, `mignon.scad`, `heliosklimax.scad`, `hammond.scad`), in the shared `/* [Glyph Quality (unified across all v2 machines)] */` group, right after `Typeface_2_Chars`. Both default to `0` (today's exact legacy behavior, verified by rendering each file's `TypeTest()` at method 0/2, and method 1 with `--enable=textmetrics`, across all six — no errors, no undefined-operation warnings).
- **Type-test string rendering wired too** — every machine's `TypeTest()` module (`FullElement`'s row-preview equivalent of Composer's `TextGaugeComposerLine2`) now calls `AlignedText(char, font, size)` instead of its own separate hardcoded `text(..., halign="center")` call, so the printed type test reflects whichever `Text_Align_Method`/`Text_Align_X_Offset` is set, matching the real element. (`postal.scad`'s `TypeTest()` uses its own `Test_Font`/`Test_Size` variables in place of `Font`/`Font_Size` — same wiring, different variable names.)

### Explicitly NOT wired (questionable / out of scope for this pass)
- **`v2/hammond_split.scad`** — its own file header already states it is "NOT wired into lib/glyph_pipeline.scad": it builds glyph geometry via a completely independent two-sided `TextAssemble(side)` path with an `intersection()`/`Arc()` trim instead of the shared `TwoDText`/`PlatenCutout` pipeline, and has none of the shared lib's other unified features (weight-adjust modes, `Character_Modifieds`, `Typeface_2`, `Scale_Multiplier`) either. Forcing `AlignedText` in here would mean inventing new plumbing for a file already flagged (per its own comments) as a "different beast," closer to `ibm.scad`'s spherical geometry than the cylinder-family machines — left untouched, consistent with that file's existing stated scope.
- **`v2/ibm.scad`** (Composer + Selectric I/II) — untouched per earlier instruction not to touch Composer's calibrated geometry. Its current alignment model is documented in [ibm-composer.md](ibm-composer.md)'s "frozen — migration candidate" section; it already does something conceptually equivalent to `textmetrics_left` by hand (`Test_CPI`-driven `25.4/CPI` escapement math is exactly the same formula `textmetrics_left` now uses), so unifying it later should be straightforward, but is a separate, deliberate migration, not a side effect of this pass.
- **All `v1/` files** — untouched, per the README's existing invariant that v1 files "still open/render exactly as before." They predate the shared lib entirely and each has its own inline `halign="center"` calls; none of this work reaches them.
