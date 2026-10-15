# Printer Selection

Companion to `resin-selection.md` — that doc covers the *material*, this one
covers the *machine*. Split because they trade against each other: pixel
geometry and resin viscosity both affect glyph edge sharpness, and diagnosing
a bad edge means knowing which one you changed.

---

## Status: partially recovered, answers lost

This shortlist was researched on **2026-07-26** across two sessions, 40
minutes before `resin-selection.md` was written — which is why that doc
cross-references a "printer shortlist" that never existed as a file.

**Both transcripts have since been deleted.** What survives is the prompt
history (`~/.claude/history.jsonl`), so the *requirements* below are
recovered verbatim but the *answers* are gone. Recovered 2026-09-01.

Treat everything under "Requirements" as settled — it is the user's own
words. Treat everything under "What matters" as re-derived afterward, and
"Candidate" as an open question, not a conclusion.

---

## Requirements (recovered verbatim, 2026-07-26)

> *"anycubic photon mono 4k is my printer - is it open source? any othe
> ropen source solutions?"*
>
> *"whats a good printer then, i have used formlabs ecosystem in the past
> and was really impressed with print quality and speed and resin quality
> but might be too expensive to get into still"*
>
> *"i need high detail, not large screen, my parts arent large. and more
> open sourcey the better. what i just learneda bout anycubic i dont like -
> is elegoo same"*
>
> *"ok if i have to run windows thats fine, i dont have a good way of
> getting files between os's tho... turbo-resin looks no longer maintained."*
>
> *"elegoo mars 5 ultra, how much it cost? anything close to it in price and
> capability with finer pixel?"*

Distilled:

1. **High detail, small screen.** Parts are not large — build volume is not
   a buying criterion here.
2. **Open-source-friendly preferred.** Something learned about Anycubic on
   2026-07-26 soured the vendor; whether Elegoo is equally closed was asked
   and never answered. `turbo-resin` (open MSLA firmware) was checked and
   found unmaintained.
3. **Formlabs is the known-good reference** from past experience — print
   quality, speed, and resin ecosystem all rated highly — but ruled out on
   cost.
4. **Windows is acceptable** if the tooling requires it. (It did: Photon
   Workshop is Windows-only in practice, and the resin work moved there.)

---

## Current machine, and the measured case for replacing it

Anycubic Photon Mono 4K:

```
3840 x 2400 · xy_pixel 35.0 x 35.0 um (square) · build 132.9 x 80.0 x 165 mm
```

The 35 um figure is the panel's true pitch; the build area is a masked
subset of the 134.4 x 84.0 mm panel span, which is why dividing build size
by resolution appears to give a non-square answer. **Pixels on this machine
are already square** — that is not a reason to upgrade, though it is worth
verifying on any candidate, since not every machine is.

The real evidence comes from UVtools' issue detector run on a genuine
sliced Selectric element (`01_selectric12_20260725.pwma`, 2026-07-26):

```
514 layers · 25.7 mm tall · 21.7 mL · 1 h 52 m · supports: none · AA: off
```

- **13 islands, every one exactly 1 px² (35 x 35 um)**, layers 82–190. Too
  small to adhere; they drop into the vat. Individually harmless — but they
  mean the glyph geometry is sitting *at* the machine's resolution limit.
  This is the single strongest argument for a finer pixel.
- **Anti-aliasing off**, on curved glyph edges at 35 um — hard pixel
  stepping on exactly the surfaces this project is graded on.
- 19 resin traps (6–21 px², layers 458–490) and 3 suction cups in the final
  12 layers, being the three element bodies closing over. Both are geometry/
  orientation problems, not resolution problems — listed here only so they
  aren't mistaken for evidence about the printer.

---

## What matters when choosing (re-derived 2026-09-01)

**XY pixel pitch is the dominant spec**, and the non-obvious corollary is
that **build volume works against you**: for a given LCD resolution, a
larger build area means larger pixels. Parts here are 25.7 mm tall, three
per plate, on a bed of 132.9 x 80 mm — a fraction of what is already
available. Buying a larger flagship machine would be paying money for
*worse* pixels. This matches requirement 1 exactly, and it is the reason
that requirement is correct rather than merely a preference.

Roughly halving the pitch (35 um to the ~18–20 um class) is about a 3.4x
improvement in pixel area and would eliminate the 1 px² island class
outright.

**Light collimation matters as much as pixel count.** A high-resolution
LCD with poor collimation blurs edges regardless of its pixel spec. This is
where cheap high-spec machines disappoint, and it is rarely on a datasheet —
look for measured light-uniformity reviews, not advertised resolution.

**DLP deserves genuine consideration.** For small parts where edge fidelity
is the entire point, a DLP projector gives sharper edges and far better
collimation than LCD at comparable pixel size. Its usual drawback — small
build volume — costs nothing here. It is the class most under-considered for
this specific use case.

**Openness.** Requirement 2 remains unresolved. Worth checking per
candidate: whether the slicer is cross-platform or Windows-only, whether
the file format is documented or reverse-engineered (UVtools support is a
good proxy), and whether third-party firmware exists and is maintained.
`turbo-resin` being dead removes the main open-firmware option, so
"open-sourcey" in practice now means *tooling* openness rather than firmware.

---

## Candidate

**Update 2026-10-15:** Formlabs announced the **Form Studio 1** — see
`formlabs-studio-1.md`. Same 35 µm pitch as the Mono 4K, so it is a
collimation/AA/process upgrade rather than a pitch upgrade — and the user
judged (2026-10-15, from experience) that pixel size was never the limiting
factor on the Mono 4K: 35 µm is past diminishing returns for these parts,
which supersedes the "pitch is the dominant spec" framing below.

**Elegoo Mars 5 Ultra** — the one concrete machine named on 2026-07-26. The
questions asked about it were never answered:

- What does it cost?
- Is anything at a similar price offering a **finer pixel**?
- Is Elegoo any more open than Anycubic?

Its appeal fits the requirements on paper: small-format, high-resolution,
consumer-priced. **Specifications are not recorded here on purpose** —
this market churns faster than the doc can, and stating a pitch or price
from memory would be worse than stating nothing. Verify against the vendor
before acting.

---

## Next steps

**Do these before spending money.** The current machine may be adequate once
the process is dialed, and both remaining experiments are free:

1. **Print the five exposure files** in `Desktop\ExposureTest_ABSLike3\`
   (see `resin-selection.md`). If 3.0 s is even 15 % long, glyph counters
   fill in and stems thicken — which looks exactly like insufficient
   resolution but is not. Diagnosing a printer against an uncalibrated
   exposure is how you buy hardware to fix a settings problem.
2. **Turn anti-aliasing on and reprint.** At 35 um with AA off, the machine
   is not delivering what it is capable of. Caveat: Photon Workshop's AA on
   this machine is emulated greyscale, so verify it helps rather than
   assuming.

Only if glyph edges are still unacceptable with exposure dialed and AA on is
the resolution ceiling demonstrated. Then:

3. **Re-run the Mars 5 Ultra pricing/pitch question** against live sources.
4. **Price a DLP option** in the same pass — it was never considered in the
   original research and is the strongest fit for small high-fidelity parts.
5. **Check tooling openness per candidate** (cross-platform slicer, UVtools
   support, maintained third-party firmware) to close requirement 2.
6. Record the answers here. The 2026-07-26 research was lost precisely
   because it lived only in a transcript.
