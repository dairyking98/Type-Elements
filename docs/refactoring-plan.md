# Refactoring Plan — Shared Library Architecture

Every script in this repo is "same but different": the same glyph pipeline repeated with slightly different parameter names and minor structural variations. This document identifies what to extract and the proposed target architecture.

---

## What is identical across all cylinder-based elements

(Applies to: Blickensderfer, Postal, Bennett, Mignon, Helios Klimax, partially IBM)

### 1. Glyph pipeline — 100% shared pattern

```
2DText(char) → linear_extrude → difference(platen_cutout) → minkowski(draft_cone)
```

All five pipeline modules (`2DText`, `WeightAdjShape`, `LetterText`, `LetterPlacement`, `TextRing`) are copy-pasted across every file with only parameter name variations. **This is the #1 extraction target.**

### 2. Quality/epsilon variables

Every file has `z`/`e` (z-fighting epsilon, 0.001–0.01), `cyl_fn`, `mink_fn`, `text_fn`, `resin_fn`. Pattern is identical; values differ slightly.

### 3. Render gating

Every file has a `Render=false` / `Assert=true` guard. Pattern is identical.

### 4. Character modification system

All files have:
- `Character_Modifieds` + `Character_Modifieds_Offset` — vertical shift per char
- `Scale_Multiplier_Text` + `Scale_Multiplier` — size override per char

### 5. Layout selection

All have a 2D array of layout strings, an index selector, and a `CharLegend` / `elementLayoutArrayMap` that reorders keyboard positions into physical element positions.

### 6. Resin support rod pattern

All define some variant of tip + rod + raft + cut groove. Geometry details differ but the concept is identical. See `docs/resin-supports.md`.

### 7. Assembly structure

All cylinder files use `difference(union(cylinder + textRing), union(shaft + hollow + holes + cleanup))` — either inline or as `Additive()` / `Subtractive()` / `Assemble()`.

---

## What must remain machine-specific

| Parameter group | Why it varies |
|----------------|---------------|
| Element OD / height | Every machine different |
| Shaft/core ID | 1/8" for Blick/Postal, others differ |
| Platen diameter | Every machine different |
| Row × column count | 3×28, 7×12, 4×21, 4×22/hem |
| Baselines and cutout positions | Measured per machine |
| Speed hole geometry | Size, qty, radial all machine-specific |
| Hollow interior profile | Machine-specific |
| Drive/retention mechanism | Wire clip, square slot, positioner pin, countersink |
| Clip top geometry | Present on Blick/Postal, absent on Mignon |
| Support placement | Follows part-specific geometry |
| Layout / keyboard maps | Machine + language specific |

---

## Proposed target architecture

```
Type-Elements/
├── lib/
│   ├── glyph_pipeline.scad      // 2DText, WeightAdjShape, LetterText, LetterPlacement, TextRing
│   ├── resin_support.scad       // ResinRod, CutGroove, parametric support assemblies
│   └── layouts/
│       ├── blick_layouts.scad   // DHIATENSOR, QWERTY, SCANDI, HEBREW_ENGL, CHARIENSTU_DE
│       ├── mignon_layouts.scad  // already exists as MignonIndexLayouts.scad — move here
│       ├── bennett_layouts.scad // already exists as BennettLayouts.scad — move here
│       └── hammond_layouts.scad
├── Blickensderfer/
│   └── Blickensderfer2.scad    // thin: machine dims + include lib/ + Assemble()
├── Postal/
│   └── Postal.scad             // thin: machine dims + include lib/ + Assemble()
├── Bennett/
│   └── BennettElement.scad     // thin wrapper
├── HeliosKlimax/
│   └── HeliosKlimaxElement.scad
├── Mignon/
│   ├── MignonCylinder.scad
│   └── MignonIndex.scad
├── Hammond/
│   └── HammondSplitShuttle2.scad  // arc geometry, separate from cylinder lib
└── IBM/
    └── IBM2.scad               // spherical geometry, separate from cylinder lib
```

---

## Code style: old (V1) vs. new (V2)

| Old style (V1, ~2023) | New style (V2, ~2025) |
|----------------------|----------------------|
| Parameters passed as long function args | Module-level globals, no arg passing |
| Inline assembly in `else` block | Named `Assemble()`, `Additive()`, `Subtractive()` |
| `Some*` parameter prefixes | Clean short names |
| Less test infrastructure | `cutoutTest`, `baselineTest`, `testLayout` |
| No `elementLayoutArrayMap` | Explicit keyboard→element mapping |
| Older `ResinPrintSupportShape()` | Parametric `ResinRod()` + `CutGroove()` |

**Gold standard:** `Blickensderfer/Blickensderfer2.scad` and `Postal/Postal.scad`. Use these as the reference when creating `lib/glyph_pipeline.scad`.

---

## Hammond: separate pattern

Hammond is structurally different (arc shuttle, not cylinder). Cannot share the cylinder glyph pipeline directly. It does share:
- Layout array format (same 3-row or 4-row string arrays)
- `2DText()` / `LetterText()` pattern (with `AnvilShape()` instead of platen cylinder cutout)
- Weight adjustment system
- Minkowski draft approach

`HammondSplitShuttle2.scad` (Jan 2026) supersedes all earlier Hammond files.

---

## Extraction order recommendation

1. **`lib/glyph_pipeline.scad`** — highest value, used by everything
   - Start from Blickensderfer2 as the reference implementation
   - Parameterize: cylOD, textOD, cylHeight, platenOD, rows, cols, latitudeInt, minkDraftAngle, textProtrusion
   - Keep character modification system as-is (copy verbatim, it's already clean)
   - Test: include in Blickensderfer2 and verify renders match current output exactly before touching Postal

2. **`lib/resin_support.scad`** — second priority
   - Extract `ResinRod()`, `CutGroove()` from Blickensderfer2
   - Parameterize everything; keep no hardcoded values

3. **`lib/layouts/`** — layout files
   - `mignon_layouts.scad` and `bennett_layouts.scad` already exist as included files — just move to `lib/layouts/` and update include paths
   - Extract Blick layouts from Blickensderfer2 into `blick_layouts.scad`

4. **Thin machine files** — after lib is stable
   - Each machine file becomes: parameters + `include <../lib/glyph_pipeline.scad>` + machine-specific body geometry + `Assemble()`

---

## Files that are unmaintained / reference-only

Do not invest refactoring effort in these:

| File | Status |
|------|--------|
| `Blickensderfer/BlickensderferElement.scad` | V1, superseded by Blickensderfer2 |
| `Blickensderfer/HebrewBlickensderferElement.scad` | One-off, superseded by HEBREW_ENGL layout in Blick2 |
| `Hammond/HammondShuttle.scad` | V1, superseded by HammondSplitShuttle2 |
| `Hammond/HammondSplitShuttle.scad` | V1.5, superseded by HammondSplitShuttle2 |
| `Hammond/GalgolicHammondShuttle.scad` | Special order, forgotten specifics |
| `TypeHeightFinder.scad` | Unmaintained utility |
| `HeliosKlimax/imagetest.scad` | Test file, not a deliverable |
