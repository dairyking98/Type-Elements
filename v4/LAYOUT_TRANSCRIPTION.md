# Layout transcription from primary sources

Record of transcribing real manufacturer type catalogs into v4's
`layout.rows` presets: what was read, what was imported, what was
deliberately left out, and — most importantly — **why each judgement call
went the way it did**. Several imports rest on reasoning rather than on
reading a glyph off a scan, and that reasoning is the part worth keeping.

All layout data lives in `lib/layouts/<machine>_layout.py`. This document
is the narrative; those modules are the source of truth for the values.

For the complete shuttle-by-shuttle enumeration with import status, see
[`CATALOG_INDEX.md`](CATALOG_INDEX.md) — 223 of 346 catalogued Hammond
shuttles are currently covered.

---

## Sources

| Source | Location | Form |
|---|---|---|
| Hammond, 1920 | `windows_tailscale:C:/Users/Leonard/Documents/Python/images to pdf/HammondTypeShuttleCatalogSmall.pdf` | 6 PDF pages (4 are two-page spreads), organised **by shuttle number** |
| Hammond, 1915 | `windows_tailscale:E:/Leonard/Typewriter/Books Manuals/Hammond_type_Catalog_1915.pdf` | 35 pages, organised **by language** |
| Blickensderfer | `windows_tailscale:E:/Type Elements/Blickensderfer/Catalog/20230113_01{55..68}.jpg` | 14 page scans, organised **by language/market** |

None have a text layer — all are scans, read as images. 200 dpi is enough
for the letter rows; individual ambiguous glyphs needed 300–600 % crops.

Higher-resolution originals exist if a glyph is ever contested: the
Hammond 1920 source TIFFs (`HammondShuttles143-148.tif`, ~300 MB each)
and the full-size `HammondTypeShuttleCatalog.pdf` (48 MB). The
Blickensderfer directory's `BLICKENSDERFER FONTS_..._2023.zip` is the
same page images zipped, not a separate source.

**These catalogs outrank `v1`/`v2` `.scad` on layout content.** That is a
deliberate, narrow exception to CLAUDE.md's "v2 is ground truth" rule:
v2 was itself transcribed from these catalogs, so where they disagree the
catalog is the earlier authority. It is *only* an exception for layout
character content — v2 remains ground truth for geometry and dimensions.

---

## Method

Four habits did most of the work. They generalise to any future catalog.

**1. Read by column, not by row.** Each column is one physical key with
three levels: unshifted / shifted / figure. The three rows therefore
constrain each other, and a reading that breaks the column is wrong even
if the glyph "looks like" something. This turned several judgement calls
into near-certainties (below), and let print artifacts be dismissed
rather than transcribed.

**2. Check the letter inventory.** Compare the lowercase row's letters
against the uppercase row's. A **duplicated letter plus a missing one**
is the signature of the transcription-error class that turned up twice.
This is mechanical, needs no scan, and found the Blickensderfer bug
independently of the catalog.

**3. Group by identical rows; typeface is not layout.** Most catalog
entries differ only in typeface — Small/Medium/Large Roman, Gothic,
Italic, Clarendon, Script all print the *same* rows. Within a keyboard
the letter rows are constant, so essentially all real variation is in the
figures row. ~80 Hammond entries collapse to a handful of layouts. One
preset per distinct layout; the typeface is the Font tab's job.

**4. When it can't be settled, don't import it.** A guessed glyph
silently builds a wrong shuttle — there is no error, just a wrong part.
No layout beats a wrong layout. Every exclusion below is recorded at its
definition site with the specific reason.

---

## Bugs found and fixed

Two real defects, both the same shape, both in the **original** source
rather than the v4 port, and both silently dropping a letter an English
typewriter cannot do without.

### Hammond Ideal — missing `b`

```
v1/Hammond/HammondSplitShuttle.scad:24   IDEAL=["?zxqkjgdmpcfld,…
v2/hammond_split.scad:76                 Ideal_Element=["?zxqkjgdmpcfld,…
```

`d` where the catalog reads `b` — leaving **`b` absent entirely and `d`
duplicated**. Every Ideal entry in both catalogs reads
`?zxqkjgbmpcfld,` / `!ZXQKJGBMPCFLD;`. Confirmed at 200 dpi.

### Blickensderfer CHARIENSTU — missing `Y`

```
v1/Blickensderfer/Blickensderfer2.scad:82,85,88   "XQZV&PFLOCHARIENSTUGMDB:WKJU"
v2/lib/layouts/blick_layouts.scad:18,21,24        "XQZV&PFLOCHARIENSTUGMDB:WKJU"
```

`U` where it should be `Y`, in both `CHARIENSTU_DE` and
`CHARIENSTU_DE_MOD`. Found by habit 2 — the uppercase row's inventory was
a–z with **U duplicated and Y missing**, while its own lowercase row was
clean. The catalog then confirmed it (`GMDB:WKJY`, Bohemian 426/443).

The same inventory check now passes on every Blickensderfer preset.
(`HEBREW_ENGL`'s row 0 is Hebrew, so the Latin check correctly does not
apply to it.)

### What the catalogs *confirmed* unchanged

- **Hammond `Universal`** — an independent transcription of the
  1920 catalog's Universal rows, reversed into this machine's storage
  order, came out byte-identical to the shipped preset on all three rows.
- **Hammond Ideal standard / fractions** — the 1915 catalog's English
  entries 37/10 and 1/2 match the 1920-derived layouts character for
  character, five years apart. Two independent printings agreeing is much
  stronger evidence than one.
- **Blickensderfer `DHIATENSOR`** — Small Roman 362 and Large Roman 409
  print it identically, differing only in typeface.

---

## Judgement calls

The decisions that were reasoned rather than simply read. Each records
what would have to be true for it to be wrong.

**`ƒ` not `f`** (Dutch Ideal, position 29). Row 0 already carries a
lowercase `f`; a figures row does not repeat a letter that has its own
key. The guilder sign is also the one currency mark a Dutch machine needs
that `£`/`$` don't cover. The 200 dpi scan shows the hooked italic form.

**`ç` not `¢`** (Spanish Ideal, position 4). At 600 % the glyph has a
cedilla hook and **no vertical stroke**; the `¢` in the CENT variant at
that same position clearly has one. The two were compared side by side.

**`1ó2` not `162`** (Spanish Ideal, positions 7–9). The accent is visible,
and a second `6` would collide with the `6` already at position 16. The
resulting accent set — á é í ó ú ñ ¡ ¿ plus `¨` as the diaeresis dead key
for ü — is complete and self-consistent for Spanish.

**`&` re-homed onto the shifted `.` key** (Universal Fractions). Nine
figure slots became fractions, displacing `&`; it reappears at the shifted
`.` position, which is the one key printing a bare dot at all three levels
on the catalog's own keyboard plate — i.e. the only spare slot. A
mechanical diff confirms exactly those 9 + 1 positions move and nothing
else.

**`ſ` not `ß`** (German, old orthography). Held for a while, then settled
by finding both printed on the SAME page in the same typeface and size —
Universal 119A (old orthography) beside Universal 117 (New Orthography),
catalog p.44. Side by side they are plainly different glyphs: 119A a
single descending stroke with a top hook and no bowl, 117 a clear bowl.
So old-orthography German shuttles carry long-s and New Orthography ones
carry eszett — and the same old/new split appears independently in the
Ideal pair 36 vs 36B. Two independent pairs agreeing is what made it
callable; one ambiguous glyph on its own would not have been.

The payoff was disproportionate: `Ideal, German` turns out to differ from
`Ideal, Dutch` in exactly ONE position (ƒ vs ſ), and resolving that single
character moved 18 catalogued shuttles from held to covered.

**An italic shuttle settled what the roman ones could not.** The guilder
`ƒ` had been argued for from structure (row 0 already has an `f`) rather
than seen cleanly. Dutch Universal 119E is an ITALIC face, and at that
size the hooked form is unmistakable in the same slot — so the reading is
now observed, not just inferred. Worth remembering as a tactic: when a
glyph will not resolve, look for the same layout in a different TYPEFACE
before reaching for a better scan.

**Greek is held on the diacritics, not the letters.** The Greek shuttles
(7, 75, 82, 8, 112A, 112B) are polytonic: alongside the alphabet they
carry standalone breathing and accent marks, and what appear to be
iota-subscript vowel forms. The letters read fine; assigning the *marks*
to codepoints is the problem — acute vs tonos, perispomeni vs a plain
tilde, psili vs a left quote are all distinguishable in principle and not
at this scan resolution. This one wants someone who reads polytonic
Greek, not a better crop.

**The inventory check can indict the SOURCE, not just the port.** It was
built to catch v1/v2 transcription errors, but on Bulgarian 31C it fired
against the catalog itself: `ж` is printed at both position 0 and
position 12 of row 0, while `ѫ` (big yus) — which pre-1945 Bulgarian
cannot do without — is absent from the shuttle entirely. A duplicated
letter alongside a missing one is precisely the signature. Either the
catalog has a typo or that glyph is not `ж`; either way it is not
importable, so all four Bulgarian entries are held. Worth knowing that
"primary source" does not mean "error-free" — it means *earlier*
authority.

**The letter-inventory check works on Cyrillic too**, and is what made a
Russian read trustworthy rather than a guess. Of the six pre-reform
letters absent from shuttle 143's row 0 (ж х ц э ѳ ѵ), five reappear in
its figures row — the shuttle is complete except ѳ (fita), which was
already rare in 1915 and abolished three years later. A misread letter
row would almost certainly have left that accounting broken. Note Ѵ
(izhitsa) genuinely is V-shaped, so a Latin-looking V there is the
correct character, not a Latin letter.

**Read the siblings, not just the entry.** Two holds were cleared this
way rather than by better optics. Roumanian Ideal 92's unresolved closing
mark was settled by Universal Roumanian 32C, which carries a bare ¸
(U+00B8) outright — once the language is known to have a standalone
cedilla, and the shape matches, no other reading is left. And the
Scandinavian pair settled each other: Swedish-Finnish and
Danish-Norwegian differ in exactly ONE letter position, å against æ, so
the catalog demonstrably had both and chose — neither is a misreading of
the other. Danish-Norwegian carrying Æ Ä Ö rather than Æ Ø Å is
historically odd, and was held on exactly that basis until its sibling
made the reading certain. It is recorded as read, not as one would
expect it to be.

**Two print artifacts dismissed, not transcribed.** Shuttle 26's row 0
`p:-` and 41's row 1 `P::` are both the `;`/`:` key, whose unshifted and
shifted forms are fixed by the keyboard. Transcribing them literally would
have invented characters that key cannot produce.

**"LARGE FRACTIONS" is a typeface, not a layout.** Shuttle 40 prints the
same rows as 26/52 in a larger fraction face.

**"Caps and Small Caps" is a typeface, not a layout.** Row 0 stores
**lowercase**, because on a small-caps face the lowercase codepoints *are*
the small capitals — a correctly-designed font then renders the row as the
catalog prints it, with the cases matching. Storing capitals would
hard-code the appearance into the layout and fight whatever font is
selected. Consequence: `Universal, Caps and Small Caps` (27, 27E)
collapses into `Universal, Standard` and is now defined by reference so
the two cannot drift. Spanish `5A` does **not** collapse — its figures-row
accented letters really are full capitals (`ÑÍÉÚ` where plain Spanish has
`ñíéú`), and those are reached by the *figure* shift rather than the case
shift, so that is a genuine character difference.

**Two spellings kept rather than one picked.** v1/v2 read `9[0]` where
every catalogued Ideal entry reads `9(0)`. Both survive as separate
presets — `Ideal (£)`/`Ideal (⅌)` preserve the shipped source history,
`Ideal, Fractions` preserves the printed catalog. Same treatment as the
pre-existing £/⅌ pair.

**Storage order is load-bearing and differs per machine.** `hammond`
stores rows **reversed**; `hammond_split` stores them in catalog reading
order (its `TextAssemble` does its own per-half `[14-i]`/`[29-i]`
reversal). Reversal is applied programmatically, never by retyping.

---

## What was imported

### Hammond (both machines — 10 presets on `hammond`, 11 on `hammond_split`)

Universal is qwerty; Ideal is Hammond's own proprietary arrangement, not a
qwerty remap. Both are real for both machines, so both are offered on
both.

| Layout | Shuttles covered |
|---|---|
| Universal, standard | 23/23B, 24/24B, 25/25A/25B, 158/158A, 180, 96, 134, 170, 68, 169, 97B, 28, 80, 145 |
| Universal, fractions | 26, 40 (LARGE), 52, 80A, 97 |
| Universal, caps & small caps | 27, 27E *(same rows as standard — typeface)* |
| Ideal, standard | 10/10A/10B/94, 37A, 51/51A/3B, 60, 118, 70, 144A |
| Ideal, fractions | 1/48/48A, 2, 3/3A, 4, 5, 6, 9 |
| Ideal, Dutch | 36A, 11A, 12A, 76A, 13A/102B, 91A, 78A |
| Ideal, Spanish | 65, 16, 46 |
| Ideal, Spanish (¢) | 65B, 16B, 46B |
| Ideal, Spanish caps & small caps | 5A |
| Ideal, Croatian | 58, 12C |
| Ideal, Danish (fractions) | 87 |
| Ideal, Portuguese | 63 |
| Ideal, French | 61, 14, 62, 15 |
| Ideal, German (New Orthography) | 36B, 114 |
| Ideal, German (old orthography) | 36, 11, 12 |
| Universal, German (New Orthography) | 117, 117A, 119C, 124, 145A |
| Universal, French | 69, 32, 32A, 67, 104, 104A, 85, 111, 111A, 134E, 145B |
| Universal, French-German-English | 32E |
| Universal, Esperanto | 135A, 135D |
| Universal, Italian | 134F, 73, 32B, 67A, 69A, 104B, 150B, 85A, 111B |
| Universal, Spanish | 33, 66, 66B, 47, 89, 28A, 68A |
| Universal, Portuguese | 150, 103, 103A, 103B, 159 |
| Universal, Roumanian | 32C, 32D, 97A |
| Universal, Swedish-Finnish | 93A, 90, 101, 101A, 101B, 134B |
| Universal, Danish-Norwegian | 55D, 90A, 93B, 101C, 134C |
| Ideal, Roumanian | 92 |
| Ideal, Bohemian | 54, 86, 120, 153C, 154A, 155A, 156A, 157A |
| Ideal, Polish | 155, 77, 154, 156, 157, 153B, 121 |
| Ideal, Hungarian | 152, 44, 57, 151, 74 |
| Universal, Chilian | 47A, 89A, 16A, 17A, 46A, 65A, 66A, 33A |
| Universal, Russian | 143 |
| Universal, Bohemian | 116 |
| Ideal, Italian | 61A, 14A, 62A, 15A |
| Universal, Dutch (Fractions) | 34D, 50C, 71F, 84C, 119E |
| Universal, German (New Orthography, Fractions) | 119C, 117D, 117E, 55F, 101E, 71E |

`hammond_split`'s `UNIVERSAL` also revives v2's `Qwerty_Element`
(`Layout_Selection=1`), which was complete in the source but never wired
into the picker — with two characters corrected against the catalog
(v2 had `⅌` and `§` where every catalogued Universal entry has `×` and
`^`, which `hammond.yaml`'s own Universal row already spelled correctly).

### Blickensderfer (8 presets)

| Layout | Shuttles covered |
|---|---|
| `BRITISH_LITERARY` | Elite Literary 381, Small Roman Literary 462, Extra Large Roman Literary 307, Italic Literary 383, Script Literary 395, Vertical Script Literary 213 |
| `QWERTY_BRITISH` | Small Roman 441, Large Roman 442 |

`BRITISH_LITERARY` keeps DHIATENSOR's letters but swaps two keys in the
shifted row (the `.` key shifts to `&`; the `,` key to `?`) and has a
wholly different figures row carrying ¼ ½ ¾ and £. `QWERTY_BRITISH`
differs from the existing (American) `QWERTY` in **exactly one position**
— `£` where it has `$`.

---

## What was NOT imported, and why

Recorded here in summary; the authoritative per-entry reasons live in
`CATALOG_SHUTTLES` in `lib/layouts/hammond_layout.py` and in the comment
block at the end of `lib/layouts/blickensderfer_layout.py`.

### Hammond 1920

- **41** Small Roman Fractions — a genuinely *different* second fractions
  scheme (diagonal fractions, and it keeps `&` in the figures row rather
  than moving it). Numerators not separable at this resolution.
- **162** Medium Gothic Fractions — right half matches the imported
  fractions layout exactly, but the left half's glyph after `4%` is
  scan-damaged.
- **184** Gothic Special Fractions — prints **four** lines, so it does not
  fit the three-row shape without deciding which line is the figures row.
- **23E / 23F / 23G / 136** — each differs from standard in only one or
  two figure slots, and those slots are exactly the unidentifiable ones.
- **Medical / chemical** (43, 43A, 107, 179, 21, 18) — purpose-made symbol
  sets with no reliable Unicode reading from this scan.
- **Diacritical / library** (113, 122, 48C) — bare combining accents
  printed in isolation; which precomposed/combining codepoint each means
  is a judgement call, not a reading.
- **Literary** (192, 193, 194) — subscript/superscript digit banks.
- **Non-Latin / special** — 195 Astronomical, 196/197 International
  Phonetic, 135/135B/135C Mathematical, 112C Greek, 59/20 German Text
  (fraktur), 165/167 Yiddish (Hebrew), 185 Check Writer (perforating,
  prints as dot matrices).

### Hammond 1915 (per-language)

Not scan-quality problems — these entries are legible — but each needs its
own character-by-character pass, and a wrong accent builds a wrong shuttle
just as silently as a wrong glyph.

- **Latin, accents only**: Croatian (58, 12C), Danish (87, 88),
  Portuguese (63, 63A, 63B, 106), Roumanian (92), Polish (156, 153B, 157),
  plus the language sections on pp. 10–20 not yet sampled.
- **Pre-reform Cyrillic**: Russian (49, 35), Servian (125) — use letters
  dropped in the 1918 reform (ѣ, і, hard-sign ъ) and need a font carrying
  them.
- **Ornate faces**: language-specific Vertical Script / Italic Script
  (e.g. 83A Chilian, 78A Dutch) whose forms make individual accent marks
  hard to separate even where the underlying layout is known.

### Blickensderfer

- **Bohemian 426/443** — CHARIENSTU letters with a Czech figures row whose
  doubled dead-key accents (`´ ´` and `ˇ ˇ`) cannot be separated reliably.
- **Armenian 218** — full Armenian script; needs a font with those glyphs.
- **British Imperial / Scientific / Universal fraction variants** (212,
  E458, 331, 454, 300, 205, 350, 494, 379, 387, 371, 337, 217) — each
  packs a different dense fraction bank (⅛ ¼ ⅜ ½ ⅝ ¾ ⅞ in varying slots)
  needing per-entry checking rather than one shared reading.
- **British Telegraph 376** — not the usual three-row 28-column shape.
- **Pages 0161–0168** — further language sections, not yet sampled.

---

## Font implications

A layout is only buildable if the selected font actually has its glyphs.
`font_coverage.py --preset MACHINE:"Preset Name"` reports this.

- **`OCR-A II Regular`**, configured for both Hammond machines, lacks the
  fractions and every accent. This is **not** a regression from the
  imports — it equally lacks `¢`/`°`/`×` from the already-shipped
  `Universal`, so every Hammond preset including the defaults is
  in the same position.
- **`AverageMono Mod`** covers all four per-language layouts and the
  fractions set with no missing glyphs.
- 529 of 1377 fonts in the library cover the Universal fractions set.
- The Caps and Small Caps entries need an actual small-caps face to look
  right — by design, since that is now the only thing distinguishing them.

---

## Remaining work, prioritised

**The test is character identification, not font availability.** A layout
gets catalogued as soon as every character can be identified and has a
Unicode codepoint. Whether a font on this machine currently carries the
glyphs is a separate, solvable problem — fonts can be found or made — and
is explicitly NOT a reason to leave a layout out. An earlier version of
this list got that wrong and parked the non-Latin scripts as "blocked on
fonts"; they are not blocked, just unworked. What genuinely blocks an
import is a character the scan will not resolve, since a guessed glyph
silently builds a wrong shuttle.

Ordered by value per unit of effort.

**1. Hammond 1915 Latin languages — biggest remaining vein, low risk.**
English, Dutch, Spanish, Croatian, Danish and Portuguese are done. Status
of the rest already sighted:

| Language | Shuttles | Page (PDF) | Status |
|---|---|---|---|
| Croatian | 58, 12C | 14 | **imported** |
| Danish | 87 | 14 | **imported** (fractions) |
| Danish | 88 | 14 | held — one slot: blank, or an under-inked `_`? |
| Portuguese | 63 | 20 | **imported** |
| Portuguese | 63A, 63B, 106 | 20 | unread |
| Roumanian | 92 | 20 | held — the mark closing row 1 won't separate from `¸` |
| Polish | 156, 153B, 157 | 20 | unread |
| French | 61, 14, 62, 15 | 16 | **imported** |
| French | 39 (Special) | 16 | unread — a fractions variant |
| German (New Orthography) | 36B, 114 | 16 | **imported** |
| German (old orthography) | 36, 11, 12 | 16 | **imported** — the `ſ` was settled, see below |
| Esperanto | 105 | 16 | letter rows clear (ĥ ĵ ŝ ĉ ĝ ŭ); figures row not yet resolved |
| French-German | 79 | 16 | unread |

**The catalog has a full index on PDF page 12**, listing every shuttle
number, its description and the page it appears on — including languages
not yet sighted anywhere above: Hungarian, Swedish-Finnish,
Danish-Norwegian, Italian, Bohemian, Polish-German, Argentine, Braille,
Turkey-Persian, Arabic, Arabic-Persian-Turkish, Bell Visible Speech, and
Dutch-German-French-English. Start there rather than paging through the
scans.

Pages 10–13, 15–19 and 21–35 have **not been sampled at all** — there are
more languages there than the table above. Each section is one layout
shared by several shuttles, so the yield per verified layout is high.
Difficulty is ordinary accented Latin.

**2. Blickensderfer pages 0161–0168 — 8 of 14 pages unsampled.** Only
0155–0160 have been read. Same by-language/market structure, same
three-row 28-column shape, same yield pattern. No known blockers.

**3. Hammond 1920 leftovers — small and fiddly.** 41, 162, 184,
23E/23F/23G, 136. Each is one or two unresolved figure slots, or a
non-standard row shape (184's four lines). Worth a pass with the
higher-resolution TIFF originals rather than more zooming on the small
PDF — that is the specific thing likely to settle 162's damaged glyph
after `4%` and 41's fraction numerators.

**4. Blickensderfer British fraction variants.** 212, E458, 331, 454,
300, 205, 350, 494, 379, 387, 371, 337, 217. Legible, but each packs a
*different* fraction bank, so this is thirteen separate verifications
rather than one shared reading — high effort, low yield per entry.

**5. Non-Latin scripts — transcribable, just unworked.** Hammond's
non-Latin sets (195 Astronomical, 196/197 Phonetic, 135/135B/135C
Mathematical, 112C Greek, 165/167 Yiddish), the 1915 pre-reform Cyrillic
(Russian 49/35, Servian 125), and Blickensderfer's Armenian 218. All of
these have complete Unicode coverage — the pre-reform Cyrillic letters
are ѣ U+0463, і U+0456, ъ U+044A, Ѳ U+0472 — so they meet the bar and
can be catalogued by anyone willing to read them carefully. They need
script familiarity, not a font.

One of these is easier than it looks: **59/20 German Text is Fraktur, a
TYPEFACE.** Its characters are ordinary German letters (umlauts and ß) in
a blackletter face, the same way "Caps and Small Caps" turned out to be a
face rather than an arrangement. It should be read as German, not as a
separate script.

**Not worth doing:** Hammond's medical/chemical (43, 43A, 107, 179, 21,
18), diacritical/library (113, 122, 48C) and literary (192, 193, 194)
sets, and Blickensderfer's British Telegraph 376. These are purpose-made
symbol banks with no reliable Unicode reading from these scans; they would
need a different, better source rather than more effort on this one.

## Continuing this work

1. Pick a target from the priority list above.
2. Render the page at 200 dpi (`pdftoppm -r 200 -png -f N -l N`), crop the
   entry, and zoom to 300–600 % for any contested glyph.
3. Apply the four habits above — especially the column reading and the
   letter-inventory check.
4. Verify every shuttle claimed to share a layout actually prints the same
   rows; don't extrapolate from one entry to its siblings.
5. Add the layout to the machine's `lib/layouts/` module, wire it into
   both Hammond machines if it's a Hammond layout (respecting the per-
   machine storage order), and add a `LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE`
   entry for `hammond`.
6. Run the hard gate (see CLAUDE.md) — adding a preset should leave every
   config's mesh output byte-identical, since it doesn't touch the active
   `layout.rows`.
7. Move the entry out of the "not imported" list and into
   `CATALOG_SHUTTLES`, with the shuttles it covers.

### Note on `config/blickensderfer.yaml`

Its row 2 reads `*` where the `DHIATENSOR` preset has `%`. That is a
deliberate hand-edit through the Layout tab (`modify_glyphs: true`), not
drift — don't "correct" it.
