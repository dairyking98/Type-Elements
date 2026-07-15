# Text Centering & Dead Space (Technical Reference)

Every machine file calls `text()` with `halign="center"` (see [glyph-pipeline.md](glyph-pipeline.md) Step 1, `2DText(char)`). This doc covers what that centering actually does, why it matters for a typewriter element specifically, and what to do about it.

> **Correction (2026-07-13):** everything from here through the "Recommendation" section (i.e. everything before "Implemented: `Text_Align_Method`") was written on the claim that `halign="center"` centers on the glyph's ink bounding box. That was wrong, and it wasn't a minor error — it invalidated part of the original rationale for this feature. Empirically re-verified via `textmetrics()` (see the "Implemented" section's correction note for the actual numbers): **`halign="center"` centers on the ADVANCE box** (`offset.x == -advance.x/2` exactly, for every glyph/font tested, including glyphs with clearly asymmetric left/right bearing). Everything below down to "Implemented" is left for historical "why we started looking at this" framing only — treat every claim in that span about ink-bbox-vs-advance-width as wrong. Skip straight to "Implemented: `Text_Align_Method`" for the current, correct state.

## What `halign="center"` actually centers on (ORIGINAL — WRONG, see correction above)

OpenSCAD does not center on the font's advance width (the fixed pitch/em-box a monospace font defines for every glyph). It centers on the **ink bounding box** — the min/max X of the actual rendered outline geometry.

- Advance width is a layout metric: how far the "cursor" moves before the next glyph. In a monospace font this is constant across all characters (that's the whole point of monospace).
- Ink bounds are whatever the glyph's outline actually draws. A `.` or `1` or `i` can occupy a small fraction of the advance width; a `M` or `W` occupies nearly all of it.

`halign="center"` (and `halign="right"`/`"left"`) ignores the advance width and centers/aligns the ink box only. So for a glyph with a 1000-unit advance width but only 200 units of ink, centering does **not** split at the 500-unit mark of the em box — it centers the 200-unit shape wherever its ink happens to sit, and the ~800 units of side bearing are simply dropped from the calculation.

This also means bounding-box centering isn't the same as optical centering: a glyph like lowercase `j` has ink that includes a descender curl well to the left of the vertical stroke, so bbox-centering can visibly shift the stroke off from where the eye expects "centered" to land. (This last observation about `j` actually fits the *corrected* advance-box-centering model better than the ink-bbox model it was originally used to support — the vertical stroke sits near the advance-box center, while the descender curl pulls the *ink*-bbox center further left. In hindsight this was a clue the ink-bbox premise was wrong.)

---

## Why this matters here specifically (historical, see correction above)

Every element (Blickensderfer, Bennett, Mignon, Hammond, IBM, Postal) places one character per fixed circumferential slot via `LetterPlacement()` / `TextRing()` (see glyph-pipeline.md Step 2). The slot position is fixed by the layout array and `latitudeInt`, independent of which character occupies it — the code assumes each glyph is centered the same way relative to its slot.

Because centering is ink-bbox-based, not advance-width-based, narrow glyphs (`.`, `,`, `'`, `1`, `i`, `l`) can sit visually off-center within their slot compared to wide glyphs (`M`, `W`, `H`), even though the underlying `text()` call is identical apart from the character. On a physical strike element this shows up as inconsistent left/right ink position per character around the same latitude band — most noticeable on narrow punctuation and numeral glyphs, and on monospace fonts where the whole point of the font is that every slot should look uniformly placed.

The project already has a mechanism for the vertical equivalent of this problem — `Character_Modifieds` + `Character_Modifieds_Offset` shifts specific characters vertically (e.g. `` ` `` accents, `_` baseline). There is currently **no horizontal equivalent**.

---

## Options for accounting for dead space (historical, see correction above)

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

## Recommendation (historical, see correction above)

Option 1 (per-character horizontal offset) is the natural next step — it reuses the existing `Character_Modifieds` calibration workflow and requires no OpenSCAD version bump. Option 2 (`textmetrics()`) is the more correct fix if/when the project's minimum required OpenSCAD snapshot already includes it, since it removes per-font/per-character guesswork entirely rather than calibrating around it.

---

## Implemented: `Text_Align_Method` — selectable alignment behavior

Implemented in `AlignedText()` in `v2/lib/glyph_pipeline.scad` (used by `TwoDText()` in place of the old hardcoded `halign="center"` text() calls). Exposed as a Customizer setting alongside the other unified glyph-quality features.

### Correction: the original method 1/2 formulas were wrong, empirically re-derived

The first implementation assumed (per the now-corrected section above) that native `halign="center"` centers on ink. Built on that assumption: method 1 ("center on the advance box instead, to preserve native bearing") and method 2 ("pin the pen origin to a fixed slot pitch, letting native bearing carry through"). Both assumptions turned out to be broken once tested against real numbers:

Probed `textmetrics()` directly (`--enable=textmetrics`, `Courier Prime` "1": `advance.x=8.3279`, `position.x=1.4912` (LSB), `size.x=5.5424`):

```
predicted native halign="center" offset (IF ink-based, -(position.x+size.x/2)) = -4.2624
predicted native halign="center" offset (IF advance-based, -advance.x/2)       = -4.16395
ACTUAL measured halign="center" offset.x (from textmetrics(... halign="center")) = -4.16395   <- matches advance-based
```

Confirmed advance-based, not ink-based, exactly, across multiple glyphs/fonts including clearly asymmetric ones (LSB=1.4912 vs RSB=1.2943 for this glyph). Consequences for the original design:

- **Method 1 as originally coded (`translate([-advance.x/2,0])`) is mathematically identical to native `halign="center"` in every case** — not "similar for symmetric glyphs," genuinely the same operation always. This is why it visibly looked indistinguishable from legacy center: it *was* legacy center, recomputed by hand.
- **Method 2 as originally coded (pin the pen origin to `-P/2`) coincides with method 0 whenever the font's own `advance.x` equals `P` (=`25.4/Test_CPI`)** — sliding a box of width `advance.x` to align its left edge vs. its center at matching anchors lands the box in the same place when `advance.x == P`. A typewriter font properly designed for its target CPI has `advance.x ≈ P` by construction, so this was close to a guaranteed no-op for exactly the fonts this feature is meant for — not a coincidence of one glyph being symmetric, but a structural property of the formula. This is why "periods still seem near center" even under `textmetrics_left`.

Both were fixed by referencing the glyph's actual **ink position** (`position.x`/`size.x`), not just its advance box, since repositioning the advance box as a rigid whole can never change where the ink sits *inside* it.

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
| `halign_center` (current default, method 0) | native `halign="center"` (no separate translate; `Text_Align_X_Offset` still applies) | Centers the **advance box** (verified above — NOT ink). A `.` ends up wherever its native LSB/RSB places it inside a box centered at 0. This is today's behavior everywhere, unchanged. |
| `ink_center` (method 1, **renamed** from `textmetrics_center`) | `translate([-(position.x + size.x/2), 0])` | Centers the **ink** — a capability OpenSCAD has no native `halign` for. Makes the visible ink dead-center, *erasing* whatever native LSB/RSB asymmetry the font was drawn with (the opposite of method 0, which preserves that asymmetry inside a centered box). Genuinely differs from method 0 whenever a glyph's LSB≠RSB; verified on `Courier Prime` "1" — method 0 offset -4.16395 vs method 1 offset -4.2624 (a real, if often small, numeric difference — visually significant mainly for stronger-asymmetry glyphs/fonts). |
| `textmetrics_left` (method 2) | `translate([-(25.4/Test_CPI)/2 - position.x, 0])` | Pins the glyph's own **ink left edge** (`position.x`), not the pen origin, to the slot's fixed left edge `-P/2`. Guarantees a fixed, non-center ink position for narrow glyphs regardless of whether `advance.x` happens to equal `P` — verified on `Courier Prime` "1": offset -2.7612, clearly different from both method 0 and 1. Visually confirmed via rendered PNG: a period/digit sequence rendered at method 2 sits visibly toward the left of each slot vs. dead-center at methods 0/1. No longer resembles Composer's pen-origin-pinning escapement (see [ibm-composer.md](ibm-composer.md)) — that comparison from the original design no longer holds after this correction, since Composer pins the *pen origin*, not the *ink edge*. |
| `textmetrics_right` (method 3) | `translate([(25.4/Test_CPI)/2 - (position.x + size.x), 0])` | Mirror of method 2: pins the glyph's own **ink right edge** (`position.x + size.x`) to the slot's fixed right edge `P/2`, instead of the left edge. Same fixed-pitch guarantee as method 2, anchored to the opposite side of the slot — added specifically for right-aligning narrow punctuation (e.g. an apostrophe/quote that should hug the *next* character rather than sit flush left). |

`advance.x` and `P` are deliberately different: `advance.x` is per-glyph (from the font itself), `P` is the fixed slot pitch derived from `Test_CPI` and shared by every character in the row regardless of its own metrics.

### `Text_Align_X_Offset` — universal fine-tune, layered on all four methods

A single mm nudge added to whichever method's base `translate()` runs, so switching methods doesn't lose a manual correction. Defaults to 0 (no-op), same pattern as `Baseline_Z_Offset`/`Font_Weight_Offset` elsewhere in the file. This is the horizontal counterpart to the vertical `Character_Modifieds_Offset` mechanism, but global rather than per-character. Declared with a `[-5:.01:5]` Customizer slider (0.01mm step) for fine-tuning, same range as its `_Modified`/`_Modified2` counterparts below.

### `Text_Align_Modified_Chars`/`Text_Align_Method_Modified`/`Text_Align_X_Offset_Modified` — per-character override

The per-character `X` table flagged above as a future addition, now implemented. Mirrors `Character_Modifieds`/`Character_Modifieds_Font`/`Character_Modifieds_Offset`'s per-character-override pattern exactly, but for horizontal alignment: characters in `Text_Align_Modified_Chars` (a string, e.g. `".,:;"`) get `Text_Align_Method_Modified`/`Text_Align_X_Offset_Modified` instead of the top-level `Text_Align_Method`/`Text_Align_X_Offset`, resolved inside `AlignedText()` itself via the same `search(char, ...)!=[]` membership test `TextRing()` already uses for `Character_Modifieds`. This lets the main alphabet stay on whichever native method/offset is dialed in while thin punctuation (whose ink sits far from its advance-box center, the exact asymmetry this whole doc is about) gets its own independent method and offset.

`Text_Align_Modified_Chars=""` (default, every v2 machine file) is a no-op — `search(char, "")` never matches, so `Text_Align_Method_Modified`/`Text_Align_X_Offset_Modified` (both default `0`) never apply until a machine's Customizer panel is given actual characters to match. Declared in the same `/* [Glyph Quality (unified across all v2 machines)] */` group as `Text_Align_Method`/`Text_Align_X_Offset`, right after them, in all six lib-wired machine files.

### `Text_Align_Modified2_Chars`/`Text_Align_Method_Modified2`/`Text_Align_X_Offset_Modified2` — second, independent override set

A second copy of the same override mechanism, checked *before* `Text_Align_Modified_Chars` inside `AlignedText()` — a character matching both sets resolves to the Modified2 method/offset. Exists so two disjoint groups of characters can each get their own alignment treatment simultaneously, e.g. `Text_Align_Modified_Chars=".,:;"` pinned left via method 2 while `Text_Align_Modified2_Chars="'\""` is pinned right via the new method 3. Same `""`-default no-op convention, declared right after the Modified set in all six machine files.

### Implementation notes
- Requires an OpenSCAD snapshot with `textmetrics()` — already satisfied (README already points at a dev snapshot). **But `textmetrics()` is also gated behind OpenSCAD's experimental-feature flag**, separate from just having a new-enough snapshot: enable it via Edit → Preferences → Features → check "Text Metrics" in the GUI, or pass `--enable=textmetrics` for any CLI/headless render or STL export. Verified by rendering `Text_Align_Method=1` both ways: **without** the flag, OpenSCAD does not error — it prints easy-to-miss console warnings (`Ignoring unknown function 'textmetrics'`, `undefined operation`) and silently renders the glyph as if untranslated, i.e. it quietly falls back to unshifted `halign="left"` positioning instead of centering on the advance box. That's a wrong-geometry-with-no-error failure mode, exactly the kind that could ship into a physical part unnoticed. **Both method 1 and method 2 now call `textmetrics()`** (method 2 didn't originally, but needs `position.x` after the ink-edge-pinning fix) — the flag must be on for either.
- Implemented as a new `AlignedText(char, font, size)` module in `v2/lib/glyph_pipeline.scad`, called from all three `TwoDText()` branches (additive/subtractive/none weight-adjust) in place of the old duplicated `text(..., halign="center")` calls — one code path for all methods instead of four copies.
- **Declared in the Customizer** in all six lib-wired v2 machine files (`blickensderfer.scad`, `postal.scad`, `bennett.scad`, `mignon.scad`, `heliosklimax.scad`, `hammond.scad`), in the shared `/* [Glyph Quality (unified across all v2 machines)] */` group, right after `Typeface_2_Chars`. Both default to `0` (today's exact legacy behavior, verified by rendering each file's `TypeTest()` at method 0/2, and method 1 with `--enable=textmetrics`, across all six — no errors, no undefined-operation warnings).
- **Type-test string rendering wired too** — every machine's `TypeTest()` module (`FullElement`'s row-preview equivalent of Composer's `TextGaugeComposerLine2`) now calls `AlignedText(char, font, size)` instead of its own separate hardcoded `text(..., halign="center")` call, so the printed type test reflects whichever `Text_Align_Method`/`Text_Align_X_Offset` is set, matching the real element. (`postal.scad`'s `TypeTest()` uses its own `Test_Font`/`Test_Size` variables in place of `Font`/`Font_Size` — same wiring, different variable names.)

### `Show_Align_Bounds` — visual debug overlay for `TypeTest()`

A Customizer checkbox (declared in each machine's `/* [Type Test] */` group, next to `Test_CPI`), off by default. When on, `TypeTest()` draws a thin semi-transparent red frame (`AlignBoundsBox()` in `glyph_pipeline.scad`, `color("red", 0.35)` outline via `difference()` of two squares, not filled so it doesn't obscure the glyph) around each character's `P`-wide window (`25.4/Test_CPI`, the same reference `textmetrics_left` pins against), at the same position as that character. Preview (F5) only — not part of the physical element geometry, and not part of `TwoDText()`/the real glyph pipeline. Exists so ink-vs-slot position can actually be judged by eye instead of guessed, which is what surfaced the method 1/2 bugs above being hard to perceive without a reference frame. Visually verified via rendered PNG (`Text_Align_Method=2`, `Show_Align_Bounds=true`, `Courier Prime` "1."x7): boxes render as clean evenly-spaced frames, `1`/`.` glyphs visibly shift toward the left edge of their box at method 2 vs. sitting centered at methods 0/1.

### `Test_Content`/`Test_String_Text` — swap `TypeTest()`'s content for a custom string

A Customizer dropdown (declared in each machine's `/* [Type Test] */` group, right after `Test_CPI`) with two options:
- `0` = `Default` (unchanged behavior) — `TypeTest()` reconstructs today's content by joining every row of the machine's current physical layout array (`Layout`/`LAYOUT`/`Keyboard_Layout_Array`/`Element_Layout_Array`, depending on the file) into one flat string via the new shared `JoinRows(rows)` function in `glyph_pipeline.scad` (`len(rows)==0 ? "" : str(rows[0], JoinRows(rest))`, replacing each file's previous ad hoc `str(Array[0], Array[1], Array[2])` or flattening list comprehension — same output, one shared implementation).
- `1` = `Test String` — `TypeTest()` uses `Test_String_Text` verbatim instead.

Whichever content is selected feeds **both** of `TypeTest()`'s output lines: the embossed/CPI-spaced character row (each character run through `AlignedText()` individually, same as before) and the flat reference caption line beneath it (a single `text()` call at natural/proportional spacing, for comparing the CPI-spaced row against how the same text would read in a normal typeset line). Previously only `blickensderfer.scad`/`postal.scad` had this caption line at all (and their Customizer-declared `Test_String` field was dead code — silently shadowed by an identically-named local variable inside `TypeTest()` that always recomputed the default from the layout array); the caption line is now added to `bennett.scad`/`mignon.scad`/`hammond.scad`/`heliosklimax.scad` too, and the dead-code shadowing is fixed by renaming the Customizer field to `Test_String_Text` and the resolved value to a local `_testString`, so the toggle actually works everywhere. Verified by rendering all six files' `TypeTest()` in both `Test_Content` states.

### Explicitly NOT wired (questionable / out of scope for this pass)
- **`v2/hammond_split.scad`** — its own file header already states it is "NOT wired into lib/glyph_pipeline.scad": it builds glyph geometry via a completely independent two-sided `TextAssemble(side)` path with an `intersection()`/`Arc()` trim instead of the shared `TwoDText`/`PlatenCutout` pipeline, and has none of the shared lib's other unified features (weight-adjust modes, `Character_Modifieds`, `Typeface_2`, `Scale_Multiplier`) either. Forcing `AlignedText` in here would mean inventing new plumbing for a file already flagged (per its own comments) as a "different beast," closer to `ibm.scad`'s spherical geometry than the cylinder-family machines — left untouched, consistent with that file's existing stated scope.
- **`v2/ibm.scad`** (Composer + Selectric I/II) — untouched per earlier instruction not to touch Composer's calibrated geometry. Its current alignment model is documented in [ibm-composer.md](ibm-composer.md)'s "frozen — migration candidate" section. **Note the correction above changes this comparison**: Composer's `TextGaugeComposerLine2` pins the *pen origin* to a cumulative-advance position (proportional escapement), which is what `textmetrics_left` originally did too — but `textmetrics_left` now pins the *ink edge* instead, after the fix. The two are no longer the same idea; a future migration would need to pick one deliberately rather than assume they already match.
- **All `v1/` files** — untouched, per the README's existing invariant that v1 files "still open/render exactly as before." They predate the shared lib entirely and each has its own inline `halign="center"` calls; none of this work reaches them.
