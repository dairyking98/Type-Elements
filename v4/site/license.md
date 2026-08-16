---
layout: page
title: License
---

This project is dual-licensed. Which license applies depends on whether
you are looking at **software** or at **designs**.

| | License | Covers |
|---|---|---|
| **Software** | [GPL-3.0-or-later](https://github.com/dairyking98/Type-Elements/blob/main/LICENSE) | The Python pipeline, the interactive tuner, the OpenSCAD sources, scripts |
| **Designs** | [CC BY-NC-SA 4.0](https://github.com/dairyking98/Type-Elements/blob/main/LICENSE-DESIGNS) | Machine dimension and calibration configs, the STL files published on this site, renders, documentation |

## In plain terms

**Print type elements for yourself — yes, freely.** That is what this
project exists for. These machines are a century old and the parts have
not been manufactured in decades. Print a typewheel, fix your
Blickensderfer, print a shuttle for your Hammond. No permission needed,
no fee, no strings.

**Give prints to other people — yes**, as long as no money changes
hands. Print a set for a friend, for your restoration club, for someone
on a forum who has been hunting for a part for years. Credit the project
and pass it on under the same terms.

**Sell prints — no.** Commercial sale of type elements is reserved to
the copyright holder. If you want to sell them,
[get in touch](https://leonardchau.com) — a separate license can be
granted, and the answer is not automatically no.

**Fork and modify the software — yes.** Change it, port a new machine,
build something else on top of it. The one condition is that it stays
open: publish your changes under the GPL and keep the attribution.

## Why the split

The output of a GPL program is not covered by the GPL. If only the code
were licensed, anyone could fork the pipeline — entirely legally — run
it, generate their own STL files, and sell prints. The copyleft would
not reach that far.

So the machine dimension and calibration data is licensed separately.
That data is the part you cannot produce a working type element without:
the diameters, tolerances, protrusions and offsets that make a printed
part actually fit a real machine, most of it arrived at by measuring
originals and iterating through failed prints.

## Contributing

Contributions are welcome — new machines, layouts transcribed from
catalogs you own, bug fixes, calibration data from a real print. Code
contributions need nothing beyond the GPL: no contributor agreement, no
copyright assignment. See
[CONTRIBUTING.md](https://github.com/dairyking98/Type-Elements/blob/main/CONTRIBUTING.md)
for the one extra term that applies to contributed design data, and why
it exists.

## Attribution and third-party work

IBM Selectric geometry was developed jointly with **Otto Koponen**, with
reference material and measurements courtesy of
[Selectric Rescue](https://selectricrescue.org/).

Keyboard layouts were transcribed from original manufacturer type
catalogs — see [Layout Transcription](/layout-transcription/). The
historical character arrangements themselves are fact, not anyone's
property; the transcription and encoding of them here is the project's
own work.

## A note on fonts

No fonts are distributed with this project — configs reference them by
system path. But a generated type element contains glyph outlines from
whatever font built it. The license above covers the type element
geometry: the body, the draft taper, the placement. It does not cover
the letterforms. Some commercial font licenses restrict embedding
outlines in derived works or physical products, so if you publish or
sell prints, that part is between you and the font's own license.

Full details, including the third-party dependency list, are in
[NOTICE](https://github.com/dairyking98/Type-Elements/blob/main/NOTICE).
