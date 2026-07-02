# Glyph Pipeline (Technical Reference)

This is the core algorithm shared across all scripts. Every machine implements the same steps; only the machine geometry parameters differ.

---

## The Full Pipeline

```
AssembleMinkowski()
  └── for each (row, column):
        SingleMinkowski(char, font, size, platenBaseline, textBaseline, latitude)
          └── minkowski(
                difference(
                  PositionText(...)               // place glyph on element surface
                    └── linear_extrude(6)
                          └── 2DText(char)        // mirrored text shape
                  PlatenCutout(...)               // concave underside
                ),
                draft_cone                        // draft angle taper
              )
```

---

## Step 1: `2DText(char)` — 2D glyph shape

Renders a **mirrored** `text()` shape. Mirrored because the character is placed facing outward and then rotated 90° — the mirror pre-compensates so it reads correctly on paper.

Optional weight adjustments:
- **Additive** (`Weight_Adj_Mode=2`): `minkowski(text, small_square)` — fattens strokes
- **Subtractive** (`Weight_Adj_Mode=1`): erodes glyph edges inward
- **None** (`Weight_Adj_Mode=0`): plain `text()`

Per-character overrides (all files implement some variant of these):
- `Character_Modifieds` + `_Offset`: vertical shift (e.g. `_` baseline, `` ` `` accent)
- `Scale_Multiplier_Text` + `Scale_Multiplier`: size override (e.g. `.` made larger)
- `Typeface_2Chars` (some files): alternate font for specific characters

---

## Step 2: `PositionText()` / `LetterPlacement()` — place on cylinder

```openscad
// Blickensderfer2 approach:
rotate([0, 0, (.5 + latitude) * latitudeInt])  // circumferential position
translate([cylOD/2 + textProtrusion - z, 0, textBaseline])  // radial + axial
rotate([90, 0, 90])                             // orient face outward
```

The `.5` offset centers characters between latitude band edges. `textProtrusion = (textOD - cylOD) / 2` is how far character faces stand proud of the main cylinder OD. `textBaseline` is the axial (height) position of the character on the element.

For Hammond: replaces cylinder rotation with arc angle; `AnvilShape()` instead of cylinder cutout.
For IBM: uses spherical coordinate transforms derived from `LATITUDE_LONGITUDE` mapping.

---

## Step 3: `PlatenCutout()` — concave underside

```openscad
translate([cylOD/2 + platenOD/2 + textProtrusion, 0, platenBaseline])
rotate([90, 0, 0])
cylinder(d=platenOD, h=10, center=true);
```

This cylinder is subtracted from the extruded glyph solid. It carves the concave underside of each character so it conforms to the platen (paper roller) curvature. When the element strikes, the character makes even contact with the paper across the full face.

**Key insight:** `textBaseline` (where the glyph face sits axially) and `platenBaseline` (where the cutout cylinder center sits) are **independent** parameters calibrated separately. The cutout must be centered on the platen, not on the character face.

For IBM: The platen is spherical in effective geometry — the cutout is specified as a longitude angle offset (`PLATEN_LONGITUDE_OFFSETS`) rotated about the sphere center, not a simple axial translation.

---

## Step 4: `minkowski(diff_result, draft_cone)` — draft angle

```openscad
// The cone kernel:
cylinder(r1=minkTextR(minkDraftAngle), r2=0, h=2)
// where minkTextR(a) = 2 * tan(0.5 * a)
// For 55° draft: r1 = 2 * tan(27.5°) ≈ 1.04 mm
```

Minkowski-summing the glyph solid with an upward-pointing cone adds a taper to every face:
- **Print face** (outer surface): grows outward at the base, narrows at the tip — creates a draft angle so the character lifts cleanly off the ribbon/paper
- **Side walls**: angled inward toward the typing face

The cone tip points toward the cylinder center (downward in glyph-local coords), so the draft tapers toward the typing face.

**Performance:** `Debug_No_Minkowski=true` / `MINKOWSKI_OFF=true` skips this step entirely. Preview is fast; geometry is accurate except for missing draft angle. Always work in this mode unless checking the final taper.

`mink_fn` (typically 10–20) controls cone polygon count. Higher = rounder cone = smoother draft = slower render.

---

## Step 5: `MinkCleanup()` — trim Minkowski overflow

After Minkowski, the glyph solid overflows past the cylinder's top and bottom planes. Two large cylinders are subtracted to trim it flush:

```openscad
translate([0, 0, cylHeight])
cylinder(d=cylOD + 10, h=5);   // trim above clip end
rotate([0, 180, 0])
cylinder(d=cylOD + 10, h=5);   // trim below drive-pin end
```

In V2 files (Blickensderfer2, Postal) this is handled inside `Subtractive()`. In V1 files it's inlined in the main assembly `difference()`.

---

## CharLegend / elementLayoutArrayMap — keyboard order to element position

The physical order of characters around the element does **not** match keyboard left-to-right order. A mapping array translates:

```openscad
// Blickensderfer CharLegend — keyboard column → physical element column:
[13,12,11,10,9,8,7,6,5,4,3,2,1,0,  27,26,25,24,23,22,21,20,19,18,17,16,15,14]
 ←—— right half of keyboard, reversed ——→ ←—— left half of keyboard, reversed ——→
```

`TextRing()` iterates physical columns 0→27 and uses `CharLegend[col]` to pick the correct character from the layout array.

For IBM: `HEMISPHERE_MAP` performs the equivalent mapping on a 22-entry-per-hemisphere basis. Composer and Selectric I/II use different maps.

---

## Font requirements

Fonts must be installed **system-wide** ("Install for all users" on Windows, not per-user) before OpenSCAD can see them. The OpenSCAD font cache requires a restart after installing.

Common fonts used across machines:

| Font | Machine/use |
|------|-------------|
| Courier New | Default Blickensderfer |
| FreeMono | Bennett |
| Iosevka Fixed Slab / Iosevka Etoile | Hammond, Mignon |
| Comic Mono | Blickensderfer variant |
| Average Mono | Hammond |
| Noto Sans Mono | Special characters |
| OCR-A II | Labels / series numbers |
| Century Schoolbook Monospace | Series numbers |
| Kurinto Type | Helios Klimax |
| Shmulik CLM | Hebrew (Blickensderfer HEBREW_ENGL layout) |

---

## Hebrew / special layout notes

Hebrew is a layout variant (`HEBREW_ENGL`), not a separate machine:
- Row 0 uses `fontHebrew` (Shmulik CLM) at a different size
- Certain characters need combining diacritics appended: e.g. ל → לְ (final-kaf with niqqud shva)
- The `fontHebrewInsertNiqqud` workaround in Blickensderfer2 handles this via string concatenation
- All other rows are standard Latin

`HebrewBlickensderferElement.scad` is an older unmaintained one-off. `HEBREW_ENGL` in Blickensderfer2 is the current approach.

---

## Quality parameters (common across all files)

| Variable | Typical value | Purpose |
|----------|--------------|---------|
| `z` / `e` | 0.001–0.01 mm | Z-fighting epsilon |
| `cyl_fn` / `surfaceFn` | 120–360 | Cylinder polygon count |
| `mink_fn` | 10–20 | Minkowski cone polygon count |
| `text_fn` | 20–44 | Text curve polygon count |
| `resin_fn` | 20 | Support rod polygon count |

---

## Render gating

Every file has a guard that prevents accidental freeze-rendering during Customizer editing:

```openscad
// V2 pattern:
Render = false;
if (Render) { Assemble(); }

// V1 pattern:
Assert = true;
if (!Assert) { /* full assembly */ }
```

Always leave this gate enabled during parameter editing. Disable only to generate the final STL.
