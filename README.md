# 3D Printed Type Elements for Typewriters
## Download OpenSCAD snapshot
Download a development snapshot of [OpenSCAD](https://openscad.org/downloads.html#snapshot).

## Open SCAD file
Open an OpenSCAD file. Use the Customizer on the right to create elements and adjust parameters.

## Creating a custom element
1. Install font for all users (right-click the font file > Install for all users).
2. Open an element file.
3. Preview the element and adjust parameters in the Customizer.

## Render and export
Preview → Render → Export STL.

### Meanings
- debug / no minkowski: render element without embossing (faster)
- preview / render / export: typical OpenSCAD workflow

## Documentation

- [Machine specifications](docs/machine-specs.md) — all dimensions and calibrated values per machine
- [Glyph pipeline](docs/glyph-pipeline.md) — how characters are rendered, draft angles, platen cutout, CharLegend
- [Resin support systems](docs/resin-supports.md) — CutGroove, rod geometry, per-machine support placement
- [Calibration procedures](docs/calibration.md) — sweep tests, debugging symptoms, procedure order
- [IBM Composer](docs/ibm-composer.md) — proportional unit system, hemisphere mapping, Composer vs Selectric
- [Refactoring plan](docs/refactoring-plan.md) — shared library architecture, extraction order, old vs new code style (executed as of v2.0, see [CHANGELOG.md](CHANGELOG.md))

## v2.0: shared library files
`v2/` holds the current, actively-developed set of machine files — a shared
`lib/` (glyph pipeline, resin support, core/shaft, layouts) plus one thin
file per machine. See [CHANGELOG.md](CHANGELOG.md) for what moved where and
which machines share the pipeline. Every v1 file below is untouched and
still opens/renders exactly as before.

- [lib/glyph_pipeline.scad](v2/lib/glyph_pipeline.scad)
- [lib/resin_support.scad](v2/lib/resin_support.scad)
- [lib/core_shaft.scad](v2/lib/core_shaft.scad)
- [lib/testing.scad](v2/lib/testing.scad) — shared calibration-sweep array generator
- lib/layouts/ — [blick](v2/lib/layouts/blick_layouts.scad), [bennett](v2/lib/layouts/bennett_layouts.scad), [mignon](v2/lib/layouts/mignon_layouts.scad), [ibm](v2/lib/layouts/ibm_layouts.scad), [hammond](v2/lib/layouts/hammond_layouts.scad) (postal.scad's single fixed layout stays inline, no separate file)
- [blickensderfer.scad](v2/blickensderfer.scad)
- [postal.scad](v2/postal.scad)
- [bennett.scad](v2/bennett.scad)
- [mignon.scad](v2/mignon.scad)
- [heliosklimax.scad](v2/heliosklimax.scad)
- [ibm.scad](v2/ibm.scad)
- [hammond.scad](v2/hammond.scad)
- [hammond_split.scad](v2/hammond_split.scad)

## v1 SCAD files by directory
The following directories (now under `v1/`) contain the original machine-specific type elements:
- Bennett
  - [BennettElement.scad](v1/Bennett/BennettElement.scad)
  - [BennettLayouts.scad](v1/Bennett/BennettLayouts.scad)
- Blickensderfer
  - [Blickensderfer2.scad](v1/Blickensderfer/Blickensderfer2.scad)
  - [BlickensderferElement.scad](v1/Blickensderfer/BlickensderferElement.scad)
  - [HebrewBlickensderferElement.scad](v1/Blickensderfer/HebrewBlickensderferElement.scad)
- Hammond
  - [GalgolicHammondShuttle.scad](v1/Hammond/GalgolicHammondShuttle.scad)
  - [HammondIndex.scad](v1/Hammond/HammondIndex.scad)
  - [HammondShuttle.scad](v1/Hammond/HammondShuttle.scad)
  - [HammondSplitShuttle.scad](v1/Hammond/HammondSplitShuttle.scad)
  - [HammondSplitShuttle2.scad](v1/Hammond/HammondSplitShuttle2.scad)
- HeliosKlimax
  - [HeliosKlimaxElement.scad](v1/HeliosKlimax/HeliosKlimaxElement.scad)
  - [HeliosKlimaxTester.scad](v1/HeliosKlimax/HeliosKlimaxTester.scad)
  - [imagetest.scad](v1/HeliosKlimax/imagetest.scad)
- IBM
  - [IBM2.scad](v1/IBM/IBM2.scad)
- Mignon
  - [MignonCylinder.scad](v1/Mignon/MignonCylinder.scad)
  - [MignonIndex.scad](v1/Mignon/MignonIndex.scad)
  - [MignonIndexLayouts.scad](v1/Mignon/MignonIndexLayouts.scad)
- Postal
  - [Postal.scad](v1/Postal/Postal.scad)


