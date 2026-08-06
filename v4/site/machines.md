---
layout: page
title: Machines
---

Every machine module exposes the same entry points
(`configure()`, `FullElement()`, `ResinPrint()`, `Additive()`,
`CalibrationElement()`, `CalibrationAdditive()`), but "cylindrical in
physical form" turned out not to predict how much code two machines
actually share - each one was verified function-by-function against its
real v2 (OpenSCAD) source before anything was ported, rather than
assumed from the physical shape.

## Cylinder family (`lib/cylinder_machine.py`)

| Machine | Shares with the rest of the family |
|---|---|
| **Blickensderfer** | Full - only diverges at the "drive pin trio" (`HollowSpace`/`DrivePin`/`ResinSupport`), which has a drive-pin countersink with 2 selectable styles. |
| **Postal** | Full - the same drive pin trio, but with no countersink at all. Otherwise a near-twin of Blickensderfer. |
| **Mignon** | Cylindrical in outward form only - diverges from `cylinder_machine.py` across essentially the whole body-construction half of the pipeline. |
| **Bennett** | Also cylindrical in form only - needed its own `tune.py` tabs, layouts, and field lists. |
| **Helios Klimax** | Cylindrical; treated the same way as Mignon/Bennett - diffed function-by-function against its own v2 source rather than assumed to reuse the shared module. |

## Spherical family (`lib/spherical_machine.py`)

| Machine | Notes |
|---|---|
| **Selectric12** | One of 3 real `Render_Mode` branches from the original `ibm.scad`, split into its own module. |
| **Selectric3** | Second branch. |
| **Selectric Composer** | Third branch - proportional-unit typing, byte-exact glyph alignment offsets preserved through the port. |

`spherical_machine.py` holds everything byte-identical across all three
branches; each machine module carries only its own layout data and
config.

## Hammond family - two machines, almost nothing shared between them

| Machine | Notes |
|---|---|
| **Hammond** | Genuinely reuses `cylinder_machine.place_on_cylinder`/`TextRing` - its arc reduces algebraically to a "fake cylinder." |
| **Hammond Split** | A from-scratch glyph pipeline and a third, independent resin-support scheme - shares almost nothing with Hammond despite the name. |

## Type Slug family - standalone, v1 ground truth

Never carried into v2 at all, so these are ported straight from v1.

| Machine | Shared lib |
|---|---|
| **Type Slug**, **Vogue Slug**, **Gauge Slug** | `lib/wing_slug.py` |
| **Oliver Slug**, **Lumi Slug** | `lib/box_slug.py` |

Nothing else remains on the roadmap for new machine ports.
