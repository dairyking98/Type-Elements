# Machine Specifications

All measured dimensions and calibrated values per machine. Values in the `.json` Customizer preset files are the authoritative source; this document is the summary reference.

---

## Coordinate conventions

**Z=0** is the drive-pin / reference face (seats against machine stop). `charBaselines` and `platenBaselines` are **negative offsets from Z=cylHeight** (the clip end). Absolute Z from reference = `cylHeight + charBaselines[row]`.

> Warning: the scad files are inconsistent. Blick/Postal use negative-from-clip-end. Bennett stores baselines as positive values from the bottom face. Helios stores them as positive from bottom. Reconcile when refactoring into shared library.

---

## Blickensderfer No. 5/7/9

**Active file:** `Blickensderfer/Blickensderfer2.scad`

| Parameter | Value | Notes |
|-----------|-------|-------|
| Element OD (`cylOD`) | 34 mm | Fixed |
| Text OD | 35 mm | Fixed |
| Element height (`cylHeight`) | **17.15 mm** | Evolved: 16.75→17.05→17.15 |
| Shaft ID (1/8" nominal) | 3.175 mm | Fixed |
| Shaft bore offset (`coreIDOffset`) | **0.14 mm** | Calibrated |
| Platen OD | 32.258 mm | Fixed |
| Rows × cols | 3 × 28 | Fixed |
| Char baselines from clip end | **[-4.0, -10.3, -16.1] mm** | Stable |
| Platen baselines from clip end | **[-2.55, -8.66, -14.45] mm** | See history below |
| Speed holes | 8 × ⌀5.568 mm at r=11.25 mm | Fixed |
| Drive pin width | 3.737 mm + offset 0.15 mm | New style |
| Drive pin radial | 10.9 mm | Calibrated (from 11.25 mm) |
| Drive pin style | 0 (new) | 1 = old style for early machines |
| Clip height | 3 mm, bite 0.7 mm | Settled |
| Clip wire OD | 0.554 mm | Fixed |
| Wall min thickness | 1.5 mm | Fixed |
| Char protrusion | 0.5 mm | Fixed |
| Draft angle | 55° | Fixed |
| Core grooves | 16 × ⌀0.6 mm | Toroidal bore grooves |

**Platen baseline calibration history:**

| Preset | Row 0 | Row 1 | Row 2 |
|--------|-------|-------|-------|
| jan 18 (first) | -2.60 | -8.66 | -14.60 |
| hebrew jan21 | -2.55 | -8.66 | -14.60 |
| MMS2 4/5 | -2.55 | -8.66 | -14.55 |
| MMS3 4/6 / 4/6 Leo | -2.55 | -8.66 | -14.50 |
| **tmp 4/12 → current** | **-2.55** | **-8.66** | **-14.45** |

**Fonts used:** FreeMono (3.0mm), Alma Mono (2.4mm), Souvenir Mono Rg (2.6mm), Clack (3.0mm), True_Vogue (3.3mm), Comic Mono (3.0mm), LTCRemingtonTypewriterW10 (2.6mm), custom scripts.

**Layouts:** DHIATENSOR (default), QWERTY, SCANDI, HEBREW_ENGL, CHARIENSTU_DE.

**CharLegend** (keyboard→element column mapping):
```
[13,12,11,10,9,8,7,6,5,4,3,2,1,0, 27,26,25,24,23,22,21,20,19,18,17,16,15,14]
 ← right half, reversed →          ← left half, reversed →
```

---

## Postal Model 3 (SN 14550)

**Active file:** `Postal/Postal.scad`

| Parameter | Value | Notes |
|-----------|-------|-------|
| Element OD | 32.8 mm | Fixed |
| Text OD | 34.1 mm | Fixed |
| Element height | 17.4 mm | Fixed |
| Shaft ID | 3.175 mm (1/8") | Fixed |
| Shaft bore offset | **0.20 mm** | Higher than Blick |
| Platen OD | 31.9 mm | Fixed |
| Rows × cols | 3 × 28 | Fixed |
| Char baselines from clip end | **[-3.6, -10.0, -15.7] mm** | Evolved from [-3.8,-10.2,-15.7] |
| Platen baselines from clip end | **[-2.65, -9.1, -14.5] mm** | Evolved from [-3.4,-9.8,-15.3] |
| Speed holes | 8 × ⌀5.2 mm at r=10.3 mm | Fixed |
| Drive pin width | 2.5 mm | Fixed |
| Drive pin radial | 11.5 mm | Calibrated |
| Clip bite | 0.7 mm | Calibrated |
| Char protrusion | 0.65 mm | Fixed |
| Draft angle | 55° | Fixed |
| Core grooves | 16 × ⌀0.6 mm | Same as Blick |

**Platen baseline history:** [-3.40,-9.80,-15.30] → [-3.00,-9.50,-14.50] → **[-2.65,-9.10,-14.50]**

---

## Bennett

**Active file:** `Bennett/BennettElement.scad`

| Parameter | Value |
|-----------|-------|
| Element OD | 31.9 mm |
| Element height | 18.65 mm |
| Shaft dia | 3.483 mm |
| Platen OD | 30 mm |
| Min char OD | 32.9 mm |
| Rows × cols | 3 × 28 |
| Baselines (**from bottom**) | [15.35, 9.2, 2.75] mm |
| Platen baselines (**from bottom**) | [16.35, 10.65, 4.50] mm |
| Speed holes | 8 × ⌀6.1 mm at r=10.801 mm |
| Countersink top | ⌀23.4 mm, depth 1.85 mm |
| Countersink bottom | ⌀23.4 mm, depth 0.9 mm |
| Positioner pin | ⌀2.6 mm at r=4.813 mm |
| Alignment holes | ⌀2.0 mm, depth 2.4 mm (at every char position on OD) |
| Shell thickness | 1.0 mm |

**Unique:** alignment holes at every character position on the outer diameter face.

---

## Mignon (AEG Mignon 2/3/4)

**Active file:** `Mignon/MignonCylinder.scad`

| Parameter | Value |
|-----------|-------|
| Cylinder OD | 18.64 mm |
| Cylinder height | 40.5 mm (43.5 mm Tallen/Plakatschrift variant) |
| Top shaft OD | 7.3 mm |
| Bottom mounting boss OD | 14.6 mm |
| Platen OD | 26.5 mm |
| Min char OD | 19.4 mm |
| Rows × cols | 7 × 12 |
| Baselines | [2.25, 7.55, 12.75, 17.8, 22.8, 28, 32.8] mm |
| Platen baselines | [2.7, 8.25, 13.6, 18.7, 23.7, 28.7, 33.6] mm |
| Top chamfer | ⌀10.5 mm at offset 3 mm |
| Pin | 1.8 mm height × 1.7 mm wide × 1.0 mm depth |

Layouts: 32+ languages via `MignonIndexLayouts.scad`.

---

## Helios Klimax

**Active file:** `HeliosKlimax/HeliosKlimaxElement.scad`

| Parameter | Value |
|-----------|-------|
| Element OD | 27.15 mm |
| Element height | 18.7 mm |
| Shaft dia | 4.16 mm |
| Platen OD | 30 mm |
| Min char OD | 28.19 mm |
| Rows × cols | 4 × 21 |
| Baselines (**from bottom**) | [3.0, 7.8, 12.5, 17.3] mm |
| Platen baselines (**from bottom**) | [2.5, 7.3, 12.0, 16.8] mm |
| Square shaft hole | 4.10 × 2.88 mm at r=8.92 mm |
| Clip | height 3 mm, dia 7 mm |
| Indicator hole | ⌀2.0 mm at r=10 mm |

Layout: GERMAN (WERTUION keyboard, 4 rows).

---

## Hammond Multiplex

**Active file:** `Hammond/HammondSplitShuttle2.scad`

Prints in two mirror-image halves that slide onto a central folder tube.

| Parameter | Value |
|-----------|-------|
| Anvil OD | 75 mm |
| Arc thickness | 1.6 mm |
| Arc height | 13.26 mm |
| Arc height offset | -2.62 mm |
| Glyph height | 0.8 mm |
| Rows | 3 (Normal), 4 (Math) |
| Chars per row | 30 |
| Degrees per char | 3.75° (=360/96) |
| Folder OD | 21 mm |
| Folder ID clearance | 12 + 0.4 mm |
| Folder thickness | 9.525 mm |
| Pin hole dia | 1.92 mm |
| Pin holes at | 68.27°, 109.97° |
| Pin radial | 7.95 mm |
| Rib OD | 46.8 mm, thickness 2.6 mm |
| Spoke count | 5, extent 45° |
| Left tube OD | 6.6548 mm |
| Right tube OD | 5.842 mm |
| Baselines from rib | [-1.9, 2.825, 7.55] mm |

Layouts: Ideal (default), QWERTY.

---

## IBM Selectric I/II and Composer

**Active file:** `IBM/IBM2.scad` (collaborative with Otto Koponen)

| Parameter | Value |
|-----------|-------|
| Sphere OD | 33.4 mm |
| Max char OD | 34.9 mm |
| Sphere center to top flat | 11.0 mm |
| Top flat thickness | 3.5 mm |
| Inside ID | 28.15 mm |
| Shaft ID | 8.8 mm |
| Boss OD | 11.6 mm |
| Rows | 4 (at ±0°, ±16.4°, ±32.8° longitude) |
| Chars per row | 22 per hemisphere = 44 total |
| Char spacing | 16.36°/char |
| Drive notch | 1.06 mm wide × 2.2 mm tall |
| Platen OD (Composer) | 43 mm |
| Platen OD (Selectric I/II) | 36 mm |
| Snoot droop compensation | 0.42 mm |

**Modes:** `RENDER_MODE=0` = IBM Composer 88-char; `RENDER_MODE=1` = Selectric I/II 88-char.

**Calibrated values:** `PLATEN_LONGITUDE_OFFSETS=[-1.05, -1.05, -1, -1.05]` (one per row).

See `docs/ibm-composer.md` for the proportional spacing system.

---

## Type Slugs

**Files:** `Type Slugs/TypeSlug.scad` and variants (Vogue, Oliver, Lumitype).

Flat individual slugs for conventional typebar machines (not type elements). Two characters per slug (upper/lower case). Parametric wing curve for typebar slot, platen cutout, Minkowski draft angle on glyph faces. Default body: 2.75 × 12.0 × 5.0 mm.
