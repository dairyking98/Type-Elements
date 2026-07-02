# Calibration Procedures

**The core challenge:** A printed element must physically fit the machine shaft, engage the drive mechanism correctly, AND strike characters at exactly the right position on paper with the right contact area. Every physical machine is slightly different; values must be found empirically.

---

## Parameters requiring calibration (in order)

| # | Parameter | What it controls | Test |
|---|-----------|-----------------|------|
| 1 | `coreIDOffset` | Shaft bore sliding fit | Gauge Set |
| 2 | `drivePinWidthOffset` | Drive pin slot fit | Manual fit |
| 3 | `charBaselines[row]` | Character height on element (vertical strike position on paper) | Baseline sweep |
| 4 | `platenBaselines[row]` / `PLATEN_LONGITUDE_OFFSETS[row]` | Platen cutout depth (contact area match) | Cutout sweep |
| 5 | `minkDraftAngle` / `MINKOWSKI_ANGLE` | Character taper angle (IBM only; others use fixed 55°) | Draft sweep |
| 6 | `fontSize` / `fontWeightOffset` | Character size and stroke weight | Type test |

Do not skip to step 4 if step 1 is not done. Each depends on the previous.

---

## Test modes (Blickensderfer2 / Postal)

### `testLayout=true` + `testChar="H"` — single character

Renders the same character at every column (0–27) across all 3 rows. Use `H` — symmetric, has verticals and horizontals, easy to judge impression evenness at any angle.

Use to verify element body geometry before worrying about character layout.

### `cutoutTest=true` — platen cutout depth sweep

```openscad
cutoutTestStart = 0        // starting offset
cutoutTestInt = 0.05       // mm increment per column
// Column n gets: platenBaseline + n * cutoutTestInt
// Column 0 = +0.00 mm, column 27 = +1.35 mm
```

`TestDebug()` prints a console table mapping column → offset.

**Reading result:** Install element, type by cycling through all character positions. The column with the most even ink coverage across the full character face = correct offset. Multiply best column × `cutoutTestInt`, add that to `platenBaselines[row]`.

### `baselineTest=true` — character height sweep

Same sweep pattern, offsets `charBaselines[row]` instead.

**Reading result:** Find column where characters fall at the correct vertical position relative to original element strike position. Apply correction.

### `renderMode=2` — Gauge Set (shaft tolerance)

Six shaft holes side by side, each 25 µm larger than the previous:
```openscad
gaugeOffsetStart = 0
gaugeOffsetInt = 0.025   // 25µm per slot
// Slots at: 0, 0.025, 0.050, 0.075, 0.100, 0.125 mm added to coreIDmm
```

Print, try each hole on shaft. Loosest hole with no lateral play = correct `coreIDOffset`. Typical: `0.14 mm` (Blick), `0.20 mm` (Postal).

### `renderMode=3` — Type Test (2D flat layout)

All characters flat at `testCPI` spacing. Use to verify font/size choices and catch missing characters before printing a full element.

---

## Test modes (IBM2)

IBM2 has 4 sweep tests, each mapping across the 22 latitude positions.

### `CUTOUT_TEST` — platen cutout angle offset sweep

```openscad
CUTOUT_TEST_START = 0
CUTOUT_TEST_ANGLE_INT = 0.05  // degrees per latitude
```

Sweeps the platen cutout longitude angle. `ConsoleCutout()` dumps a full table: character, row, latitude, cutout offset, draft angle. When `CUTOUT_TEST=true`, alignment is forced to center and position offsets are zeroed to isolate this variable.

Final calibrated values: `PLATEN_LONGITUDE_OFFSETS=[-1.05, -1.05, -1, -1.05]`.

### `DRAFTANGLE_TEST` — draft angle sweep

```openscad
DRAFTANGLE_TEST_START = 50
DRAFTANGLE_TEST_INT = 1    // 1° per latitude
```

Sweeps draft angle 50°–71°. Find angle giving clearest impression without smearing.

### `MINK_LONG_OFFSET_TEST` — longitudinal Minkowski offset

Tilts the draft cone longitudinally (toward/away from equator) per row. Final values: `MINKOWSKI_LONGITUDINAL_OFFSETS=[0, 0, 0, 0]`.

### `PLATEN_DIAMETER_TEST` — platen diameter sweep

```openscad
PLATEN_DIAMETER_TEST_START = 30
PLATEN_DIAMETER_TEST_INT = 1   // 1mm per latitude
```

Useful when a machine's platen has been re-covered with different diameter rubber.

### `SELECTIVE_RENDER="sine"` + `SELECTIVE_RENDER_CHARS`

Renders only specific characters. Speeds up render when debugging individual glyphs.

### `XSECTION=true` — cross-section view

Cross-sections the element at angle `XSECTION_THETA`. Verify platen cutout depth, wall thickness, and character protrusion before printing.

---

## Calibration procedure (new element design)

### Step 1: Shaft fit
1. `renderMode=2`, print gauge set
2. Find loosest slot with no play
3. Record and lock `coreIDOffset` in `.json`

### Step 2: Drive pin fit
1. Print test element with `Debug_No_Minkowski=true`
2. Check drive pin slot engages without forcing
3. Adjust `drivePinWidthOffset` (typically 0.10–0.20 mm)

### Step 3: Baseline height
1. `testLayout=true`, `testChar="H"`, `baselineTest=true`
2. Print with supports
3. Install, type across all positions against a ruled reference line
4. Find column with best vertical centering; compute `best_column × baselineTestInt`
5. Apply correction to `charBaselines[row]` for each row

### Step 4: Platen cutout depth
1. `cutoutTest=true`, `testChar="H"` (or all chars)
2. Print and install
3. Look for even ink coverage across character face
4. Find best column; apply `best_column × cutoutTestInt` to `platenBaselines[row]`

### Step 5: Font size and weight
1. `renderMode=3` (type test)
2. Compare against original element typeface sample
3. Adjust `fontSize`, `fontWeightOffset`, `xFontWeightAdj`, `yFontWeightAdj`

---

## Calibration procedure (existing design, new machine instance)

Shaft/drive pin offsets often don't change for the same machine model. Start at Step 3. Check platen diameter if the platen has been re-covered.

---

## Debugging by symptom

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Characters print too high | `charBaselines` too high | Baseline sweep, decrease |
| Characters print too low | `charBaselines` too low | Baseline sweep, increase |
| Uneven impression: heavy top, light bottom (or vice versa) | `platenBaselines` offset wrong | Cutout sweep |
| Faint in center, dark at edges | Cutout too deep (over-curved) | Cutout sweep, adjust |
| Faint at edges, dark in center | Cutout too shallow (under-curved) | Cutout sweep, adjust |
| Won't slide onto shaft | `coreIDOffset` too small | Gauge set, increase |
| Wobbles on shaft | `coreIDOffset` too large | Gauge set, decrease |
| Characters smear on upstroke | Draft angle too shallow | Increase draft angle |
| Characters blurry / too wide | Font weight too high or draft too steep | Decrease `fontWeightOffset` / draft |
| Specific character prints badly | Per-char modifier needed | `charMods`, `charModsBaselineOffset`, `Scale_Multiplier` |

---

## Saving calibrated values

**Current practice:** Values live in the `.json` Customizer preset file. Fragile — no machine serial, no date.

**Better practice:**
- One `.json` preset per machine instance (e.g. `Blickensderfer2_SN12345.json`)
- Comment block in the `.scad` listing locked values and their source date
- Include calibration history in comments when a value changes (see machine-specs.md for Blick platen baseline history as example)

Every new machine file should include all test modes from day one. Copy from Blickensderfer2. This costs nothing and prevents re-discovering calibration methodology on every new machine.
