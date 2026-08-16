# Contributing

Contributions are welcome - new machines, layout transcriptions from
catalogs you own, bug fixes, calibration data from a real print.

Start with [`v4/CLAUDE.md`](v4/CLAUDE.md), which documents the
conventions and the hard-won geometry invariants. Most of them map to a
bug that actually shipped once. The
["Verifying a geometry-affecting change"](v4/CLAUDE.md) section is a hard
gate - run it before opening a PR that touches mesh code.

## Licensing your contribution

This project is dual-licensed (see [`NOTICE`](NOTICE)): code under
GPL-3.0-or-later, design data under CC BY-NC-SA 4.0. Contributions are
released under whichever applies to the files you touched.

**Code contributions need nothing beyond the GPL.** No contributor
agreement, no copyright assignment, no extra paperwork. Submit a patch,
it goes out under GPL-3.0-or-later, you keep your copyright, done.

**Design data contributions need one extra term**, for a specific and
narrow reason. The copyright holder sells physical prints; the software
is not sold. Design data is licensed non-commercially, so if a
contributed machine config arrived under that license alone, the
contributor's own non-commercial term would bar the copyright holder
from selling prints of that machine - a contribution would quietly
subtract from the project rather than add to it. The grant below exists
only to prevent that.

By opening a pull request, you agree that:

1. **You wrote it, or you have the right to submit it.** If it derives
   from someone else's work, say so in the PR, with the source and its
   license.

2. **Your contribution is released publicly** under the license that
   covers the files you changed - GPL-3.0-or-later for code, CC BY-NC-SA
   4.0 for design data. Everyone gets it on those terms, including you.

3. **If your contribution is design data** - anything under `v4/config/`,
   or model/render assets - **you additionally grant Leonard Chau** a
   perpetual, worldwide, non-exclusive, royalty-free, irrevocable license
   to use, reproduce, modify, publicly display, distribute, and
   sublicense it under any terms, including commercial ones. This does
   not apply to code contributions.

You keep the copyright to your work either way. Point 3 is a license
granted alongside the public one, not an assignment, and it takes
nothing away from you: your contribution remains available to everyone
else on the same non-commercial terms as the rest of the project.

This split works cleanly because of an existing project rule: real
machine numbers - dimensions, tolerances, offsets, facet counts - live
in config YAML and never in code (see [`v4/CLAUDE.md`](v4/CLAUDE.md),
"Geometry invariants"). Follow that rule and it is always obvious which
category your change falls into.

Sign off your commits to record this:

```
git commit -s
```

which appends a `Signed-off-by: Your Name <your@email>` line.

## What you can do with the result

To be explicit, because the dual license is easy to misread:

- **Print type elements for yourself** - yes, freely, including elements
  you designed by contributing here.
- **Give prints to other people** - yes, as long as no money changes
  hands, with attribution, under the same license.
- **Sell prints** - no. That is reserved to the copyright holder.
- **Fork the software, modify it, build on it** - yes. Keep it open,
  keep the attribution, publish your changes under the GPL.
- **Sell services around the software** (consulting, hosting, support) -
  yes, the GPL permits this. Selling the *type elements* is the part
  that is reserved.

If you want to sell prints commercially, ask - a separate license can be
granted. Contact details are at [leonardchau.com](https://leonardchau.com).
