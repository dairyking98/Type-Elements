# Resin Support Systems

All type elements are printed in resin (SLA/MSLA). Support structures are hand-crafted in OpenSCAD, not slicer-generated, because glyph faces are functional surfaces that must never receive support contact points.

---

## Why slicer auto-supports are insufficient

1. **Glyph faces must be contact-free.** A slicer sees only geometry. It will place tip contacts on character faces, leaving pits that damage the printing surface.
2. **The CutGroove is calibrated engineering.** A precision circumferential groove at the element OD lets the entire support raft snap off cleanly with a fingernail. Not reproducible with generic slicer supports.
3. **Placement follows part-specific geometry** (sloped bottoms, speed hole positions, boss anatomy) that requires domain knowledge encoded in formulas, not auto-detection.

---

## Universal rod geometry (`ResinRod`)

All machines use a variant of the same compound geometry:

```
[contact sphere: d=resinTipOD]    ← partially embeds into part surface (resinInset depth)
[neck / break point]               ← thinnest point; snaps here on removal
[rod: d=resinRodOD]               ← vertical shaft
[raft: d=resinRaftOD]             ← base plate on buildplate
```

Built as `hull()` of spheres + cylinder raft. The partial inset (`resinInset ≈ 0.3 mm`) creates positive grip that separates cleanly rather than peeling.

Hammond and IBM add a `theta` angle parameter: the tip tilts to match the surface normal so the rod breaks away cleanly on curved/spherical geometry.

### Calibrated parameters by machine

| Parameter | Blick2 | Postal | Hammond | IBM |
|-----------|--------|--------|---------|-----|
| `resinRodOD` | 1.0 mm | 0.8 mm | 0.8 mm | 1.2 mm |
| `resinTipOD` | 0.6 mm | 0.4 mm | 0.4 mm | 0.9 mm |
| `resinTipL` | 1 mm | 1 mm | 1 mm | 1 mm |
| `resinInset` | 0.3 mm | 0.3 mm | 0.3 mm | 0.4 mm |
| `resinMinRodH` | 4 mm | 2 mm | 2 mm | 2 mm |
| `resinRaftOD` | 2 mm | 4 mm | 4 mm | 4 mm |
| `resinRaftThickness` | 1 mm | 2 mm | 2 mm | 2 mm |

IBM also uses a finer notch tip: `TIP_NOTCHD=0.4 mm` for tight areas near the drive notch.

---

## CutGroove — cylinder machine breakaway system (Blick, Postal)

The most important support feature. A `rotate_extrude()` circumferential groove cut into the outer wall just above the raft level:

```openscad
module CutGroove() {
    rotate_extrude()
    translate([cylOD/2 - wallMinThickness, 0])
    difference() {
        polygon([...])           // trapezoidal wall cross-section
        circle(d=resinGrooveOD)  // inner tangent cut
        circle(d=resinGrooveOD)  // outer tangent cut
    }
}
```

Two tangent circles (`d=resinGrooveOD=0.8 mm`) create a necked-down bridge `resinGrooveThickness=0.3 mm` thick — strong enough to survive printing, snaps off with fingernail pressure. The groove is at radius `cylOD/2 - wallMinThickness` so snapping it removes the entire raft without touching the element body.

There is no slicer equivalent. Must be modeled.

---

## Cylinder machine support placement (Blick, Postal)

### `bottomZ(X)` — sloped bottom geometry

The cylinder bottom is not flat; it slopes from the core upward to the outer wall. Support rod heights are computed exactly:

```openscad
function bottomZ(X) = bottomSlope * X + bottomZOffset
// bottomSlope derived from coreBottomOffset and wall geometry
```

All rods use `h = bottomZ(radial_position)` so tips land on the slope surface.

### Support groups

| Module | Rods | Placement |
|--------|------|-----------|
| `SpeedHoleSupport()` | 4 per speed hole × 7 holes = 28 | Cardinal tangent points of each hole perimeter; hole 0 skipped (drive pin area) |
| `DrivePinSupport()` | 4 | Cardinal points around drive pin countersink |
| `BottomSupports()` | 8×2 = 16 | One at 20% between core inner wall and outer wall per sector; one at core chamfer edge |

Full assembly:
```openscad
module ResinSupport() {
    CutGroove();
    SpeedHoleSupports();
    DrivePinSupport();
    BottomSupports();
}
```

---

## IBM Typeball supports

No CutGroove (spherical geometry has no suitable groove location). All rods have angle parameter for surface-normal alignment.

### Regions requiring support

| Region | Why |
|--------|-----|
| Detent teeth (bottom skirt) | Lowest feature, prints first |
| Boss face (central boss, faces down) | Large flat face toward vat = maximum peel force |
| Roof (top flat) | Interior ceiling, overhangs inward |
| Notch areas (drive notch) | Narrow slot creates overhang on both sides |

### Boss region: two-tier support

Primary rod from buildplate to boss face, plus secondary rods ("support-of-supports") from buildplate to primary rod midpoints at heights 7 mm and 12 mm. Prevents long thin rods from deflecting and misplacing the boss contact point.

### `SNOOT_DROOP_COMPENSATION=0.42 mm`

Not a support parameter — compensates for boss face drooping under gravity during resin curing when printed face-down. Lowers the boss height in the model by 0.42 mm so the printed boss measures exactly correct.

---

## Hammond Split Shuttle supports

Most complex system. Every rod must account for the surface normal angle at its contact point.

### `ResinRod(h, theta)` — angle-aware rod

`theta` is the surface tangent angle. `ResYOffset(theta)` and `ResZOffset(theta)` position the raft base so the rod stands vertically from the buildplate even though the tip is angled to the surface.

### `ResinFence()` — X-pattern grid fence

Two sets of parallel bars at ±45°:
```openscad
module ResinFence() {
    rotate([-resAngle, 0, 0]) ResinParallelBars();
    rotate([ resAngle, 0, 0]) ResinParallelBars();
}
```
`ResinParallelBars()` = thin cylinders (`d=resinRodOD`) spaced `resSpacing=6 mm` apart. The X-pattern provides lateral stability to the arc.

### `ResinFenceArcTop()` — connecting top rail

Chains adjacent rod tops with `hull()` segments, forming a continuous rail along the arc top edge. Prevents arc curvature from separating tips from the surface between layers.

### Full assembly groups

```
ResinSupports(side):
  ├── ResinArcSupports()        ← perimeter dot-grid on arc face
  ├── ResinArcFenceSupport()    ← edge X-fence + top rail
  ├── ResinFolderSupports(side) ← central folder hub (left/right differ)
  └── ResinRingSupports(side)   ← folder ring/tube section
```

---

## Comparison across machines

| Feature | Blick/Postal | IBM | Hammond |
|---------|-------------|-----|---------|
| CutGroove breakaway | Yes (circumferential) | No | No |
| Tip angle param | No (vertical only) | Yes | Yes |
| bottomZ sloped-surface calc | Yes | No (sphere) | No (arc) |
| Support-of-supports | No | Yes (boss) | No |
| Fence/grid system | No | No | Yes |
| Per-hole cardinal supports | Yes | No | No |
| Separate fine tip size | No | Yes (notch) | No |
