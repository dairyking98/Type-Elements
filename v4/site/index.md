---
layout: page
title: Type Elements
description: >-
  Make 3D-printable typewriter type elements from any font - Selectric
  balls, Blickensderfer wheels, Hammond shuttles and more. Preview in 3D,
  export a print-ready STL.
---

<style>
  .hero { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 24px; align-items: center; margin: 4px 0 28px; }
  .hero h2 { font-size: 34px; line-height: 1.1; margin: 0 0 12px; letter-spacing: -.01em; }
  .hero p { font-size: 18px; color: #555; margin: 0 0 18px; }
  .hero img { width: 100%; height: auto; }
  .cta { display: inline-block; background: #2f6fde; color: #fff !important; padding: 11px 20px; border-radius: 8px; font-weight: 600; text-decoration: none !important; margin: 0 10px 10px 0; }
  .cta.alt { background: transparent; color: #2f6fde !important; border: 1px solid #2f6fde; }
  .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin: 8px 0 28px; }
  .tile { border: 1px solid #e3e6eb; border-radius: 10px; padding: 14px 16px; }
  .tile b { display: block; font-size: 16px; margin-bottom: 4px; }
  .tile span { color: #666; font-size: 15px; }
  .mobile-note { display: none; background: #eef3fd; border-radius: 8px; padding: 10px 14px; font-size: 15px; margin-top: 6px; }
  @media (max-width: 760px) { .hero { grid-template-columns: 1fr; } .hero img { max-width: 360px; margin: 0 auto; display: block; } .mobile-note { display: block; } }
</style>

<div class="hero">
  <div>
    <h2>Typewriter type elements, from any font.</h2>
    <p>Pick a machine, choose a typeface, arrange the keyboard, and get a
    watertight STL of a working type element - a Selectric typeball, a
    Blickensderfer wheel, a Hammond shuttle - ready for a resin printer.</p>
    <a class="cta" href="/app/">Open the app</a>
    <a class="cta alt" href="/how-it-works/">How it works</a>
    <div class="mobile-note">On a phone? Read on here - building elements needs a computer for now.</div>
  </div>
  <img src="/assets/og/selectric-render.png" alt="A generated IBM Selectric typeball with resin supports, rendered in 3D" width="480" height="487">
</div>

<div class="tiles">
  <div class="tile"><b>10 machines</b><span>Selectric I/II, III and Composer, Blickensderfer, Postal, Mignon, Bennett, Helios Klimax and two Hammonds - plus five standalone type slugs.</span></div>
  <div class="tile"><b>Any font</b><span>Every character is cut from the real glyph outline, with a true draft taper and the platen's curvature.</span></div>
  <div class="tile"><b>Print-ready</b><span>Watertight solids with resin supports, plus an overhang check that flags islands before you slice.</span></div>
  <div class="tile"><b>Runs in the browser</b><span>The engine now runs in a browser tab - and renders faster than native Python. <a href="/v5-performance/">See the numbers</a>.</span></div>
</div>

## What's new - v5

**[The app](/app/)** is the new interface: settings grouped by task, every
font shown in its own typeface, the keyboard layout drawn in the real font
with missing characters flagged, live build logs and a 3D preview. Today it
drives the engine on your own computer (the page walks you through starting
it). A no-install version that runs entirely in your browser is close:
v4's own code already builds a full Selectric element in a tab, matching
the native output exactly, and with parallel workers it finishes faster
than native. [Read about v5](/v5/) · [Performance](/v5-performance/) ·
[Engine API](/v5-engine-api/) for anyone who wants to build their own
interface.

## Read more

- **[How it works](how-it-works)** - the Minkowski draft sum, real
  booleans, adaptive glyph outline sampling, and the geometry invariants
  that keep the pipeline correct.
- **[Machines](machines)** - every supported typewriter, and how much code
  each one actually shares with the others.
- **[Accessories](accessories)** - companion parts, like legend-card
  holders, that print alongside a machine's type elements.
- **[Behind the scenes](behind-the-scenes)** - concrete bugs and dead ends
  that shaped the design.
- **[Roadmap](roadmap)** · **[Changelog](changelog)** ·
  **[README](readme)** · **[License](license)** - print these for yourself
  freely; the software is GPL, the designs are non-commercial.

> The story behind it - collaborators, real prints, photos of the restored
> machines: [leonardchau.com/projects/type-elements](https://leonardchau.com/projects/type-elements/).

Source: [github.com/dairyking98/Type-Elements](https://github.com/dairyking98/Type-Elements)
(`v4/` is the engine, `v5/` the app).
