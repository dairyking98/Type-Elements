# Layout transcription from primary sources

Record of transcribing real manufacturer type catalogs into v4's
`layout.rows` presets: what was read, what was imported, what was
deliberately left out, and — most importantly — **why each judgement call
went the way it did**. Several imports rest on reasoning rather than on
reading a glyph off a scan, and that reasoning is the part worth keeping.

All layout data lives in `lib/layouts/<machine>_layout.py`. This document
is the narrative; those modules are the source of truth for the values.

For the complete shuttle-by-shuttle enumeration with import status, see
[`CATALOG_INDEX.md`](CATALOG_INDEX.md) — 258 of 346 catalogued Hammond
shuttles and 73 of 84 sighted Blickensderfer shuttles are currently
covered. Both tables are generated, so those counts cannot drift from
the code.

---

## Sources

| Source | Location | Form |
|---|---|---|
| Hammond, 1920 | `windows_tailscale:C:/Users/Leonard/Documents/Python/images to pdf/HammondTypeShuttleCatalogSmall.pdf` | 6 PDF pages (4 are two-page spreads), organised **by shuttle number** |
| Hammond, 1915 | `windows_tailscale:E:/Leonard/Typewriter/Books Manuals/Hammond_type_Catalog_1915.pdf` | 35 pages, organised **by language** |
| Blickensderfer | `windows_tailscale:E:/Type Elements/Blickensderfer/Catalog/20230113_01{55..68}.jpg` (local copy: `~/Blickensderfer-Catalog`) | 14 page scans, organised **by language/market** |

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

## Preset naming

One convention, all ten machines:

    <Keyboard>[, <Language>][ (<Variant>)]

Title Case. A comma introduces the language, or the variant when there is
no language; parentheses hold the variant once a language is named, with
multiple variants comma-separated inside the one pair. So `Universal`,
`Universal, Math`, `Ideal, Spanish (¢)`,
`DHIATENSOR, British (Fractions, Mimeograph)`.

"Keyboard" is whatever axis that machine's own sources divide its range
along — Ideal/Universal for the Hammonds, the letter arrangement
(DHIATENSOR/QWERTY/CHARIENSTU) for Blickensderfer. A machine with only
one keyboard starts at the language: Bennett's `British`, Selectric's
`United States`.

This was a Hammond-only rule while six other machines spelled their
presets `SCREAMING_SNAKE` (`QWERTY_BRITISH`, `UNITED_STATES`,
`GERMAN_MOD`). Unified in one pass, verified by checking that every
renamed key still maps to byte-identical rows and that no unrenamed
preset moved.

Two consequences worth knowing:

- A `SCREAMING_SNAKE` name in a code comment is now a **quote of a v1/v2
  `.scad` array**, not a v4 preset. `blickensderfer_layout.py`,
  `helios_layout.py` and the two Selectric modules all carry such quotes
  deliberately and say so.
- Renaming is safe because **no config stores a preset name**, only the
  rows it produced — the picker is a template chooser, not persisted
  state. The one place names are stored is `blickensderfer_catalog.py`'s
  preset column, and `gen_catalog_index.py` exits non-zero when one stops
  resolving.

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

`U` where it should be `Y`, in both CHARIENSTU arrays (v4's
`CHARIENSTU, German` and `CHARIENSTU, German (Modified)`). Found by
habit 2 — the uppercase row's inventory was
a–z with **U duplicated and Y missing**, while its own lowercase row was
clean. The catalog then confirmed it (`GMDB:WKJY`, Bohemian 426/443).

The same inventory check now passes on every Blickensderfer preset.
(`DHIATENSOR, Hebrew-English`'s row 0 is Hebrew, so the Latin check
correctly does not apply to it.)

### What the catalogs *confirmed* unchanged

- **Hammond `Universal`** — an independent transcription of the
  1920 catalog's Universal rows, reversed into this machine's storage
  order, came out byte-identical to the shipped preset on all three rows.
- **Hammond Ideal standard / fractions** — the 1915 catalog's English
  entries 37/10 and 1/2 match the 1920-derived layouts character for
  character, five years apart. Two independent printings agreeing is much
  stronger evidence than one.
- **Blickensderfer `DHIATENSOR`** — fourteen English Scientific entries
  (365, 407, 409, 455, 457, 356, 362, 374, 474, 440, 499, 201, 223, 308)
  all print it identically, differing only in typeface. `QWERTY` gets the
  same treatment from eight Universal entries (325, 406, 418, 364, 359,
  497, 304, 216).
- **Blickensderfer `WKJY`** — German 423's row 1 was a *third*
  independent confirmation of the `WKJU`→`WKJY` correction above, after
  the letter-inventory check and the Bohemian scan.

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

**`⅌` — the one the scans could not give up.** Universal position 5
resisted three faces and every zoom: a p-like form with a bowl and a
stroke. It is the PER SIGN (U+214C), identified by the machine's owner
rather than from the page. That single character was gating 19
catalogued shuttles — Universal German, Universal Dutch, and the German
fractions family — which is why it was worth stopping to ask rather than
guessing.

It also corrected something already written down. An earlier note here
called v2's `⅌` and `§` in `Qwerty_Element` transcription errors,
"neither of which any catalogued Universal entry shows". They are at
positions 5 and 20 — exactly the two positions where Dutch and German
Universal differ from English Universal, and both characters appear
there in the catalog. v2's array is English Universal with the Char_Mod
character swapped in, not a botched transcription. Corrected at the
definition site.

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

**Cap height is evidence.** Hungarian Universal read as `ó` twice in its
figures row, which looked like the duplicate signature. At 700% the first
reaches the full height of the adjacent digits and the second sits at
x-height: `Ó` and `ó`, not a duplicate at all. The inventory agreed —
Ideal Hungarian carries both cases, and reading both as lowercase would
have left `Ó` absent from the shuttle entirely.

**A missing letter is only evidence if the letter should be there.** The
same entry appeared to be missing `í`, which reinforced the false
duplicate reading. It isn't missing: no Hungarian shuttle on either
keyboard carries `í`, per the machine's owner. The check is only as good
as the alphabet you compare against, and for a 1915 shuttle that alphabet
is a question about the machine, not about the language.

**Derive a near-identical variant, don't retype it.** The three
Mathematical shuttles differ in exactly two figures-row positions — 135
`*`/`|`, 135B `{`/`}`, 135C `ν`/`μ`. 135B is built from 135 by
substituting those two characters programmatically, so the only
difference between the two presets is the one actually observed.
Retyping four 30-character rows of Greek and mathematical symbols to
change two of them is precisely how a transcription error gets
introduced — the thing this whole document exists to avoid.

This also confirmed the shipped `Universal, Math` layout, which came from
v2 rather than the catalog: it matches shuttle 135 character for
character.

**Quote marks are a real character, and I got five of them wrong.** The
Universal German/Dutch figures row has `“` (U+201C) at position 4, not
`”` — at 600% the raised pair curls the same way as the `„` beside it
(6-shaped, not 9-shaped). Five layouts had been imported with the wrong
one. Corrected from that single verified instance, since all five share
that row half.

The IDEAL family's quote was deliberately NOT normalised to match.
German and Dutch genuinely diverge here — German pairs `„…“`, Dutch pairs
`„…”` — so "make them consistent" would be exactly the wrong instinct.
It stays as read, flagged as unverified, rather than tidied into a
plausible uniformity.

**Bulgarian: solved by accounting, not by reading.** Three glyphs on this
shuttle would not resolve visually at any zoom. What settled them was
counting the alphabet. With `ѫ` at position 0, row 0 holds 30 distinct
letters and no duplicates; pre-1945 Bulgarian has 33; the three absent
are `х`, `щ` and `ѭ`; `х/Х` and `щ/Щ` are plainly in the figures row —
leaving *exactly* `ѭ` unaccounted for and *exactly* one unidentified pair
left to hold it. The layout is forced, without ever reading the glyph.

The same accounting rejected a plausible-sounding alternative. `Ѣ` (yat)
was proposed for position 0, and the form is stylised enough to invite
it — but yat is already on this shuttle at position 28, in a plainly
different shape (stem, top crossbar, bottom bowl), and putting it at
position 0 too would have duplicated a letter while leaving the alphabet
short. The count says which readings are *possible*, not just which are
plausible.

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
| Universal, Dutch | 71A, 117B, 34A, 50A, 119B |
| Universal, German | 119A, 84, 34, 50, 71, 117, 119 |
| Universal, Russian (Old Style) | 29, 29A, 29B |
| Universal, Bulgarian | 31C, 29C, 42C, 115C |
| Ideal, Chilian | 65A, 16A, 46A, 17A, 83A |
| Universal, Polish | 141, 30, 150C |
| Universal, Math (braces) | 135B |
| Universal, Math (Greek) | 135C |
| Universal, Hungarian | 134A, 56, 64 |

`hammond_split`'s `UNIVERSAL` also revives v2's `Qwerty_Element`
(`Layout_Selection=1`), which was complete in the source but never wired
into the picker — with two characters corrected against the catalog
(v2 had `⅌` and `§` where every catalogued Universal entry has `×` and
`^`, which `hammond.yaml`'s own Universal row already spelled correctly).

### Blickensderfer (28 presets, 20 of them from the catalog)

All 14 pages have now been read: **73 of the 84 shuttles they contain**
are covered. See [`CATALOG_INDEX.md`](CATALOG_INDEX.md) for the
per-entry table.

| Layout | Shuttles covered |
|---|---|
| `DHIATENSOR, British (Fractions)` | Imperial 212, and Scientific E458, 412, 428, 435, 405, 363, 393, 357, 454, 300, 205 |
| `QWERTY, British (Fractions)` | Elite 350, Small Roman 494, Large Roman 379, Italic 371, Script 337, Vertical Script 217 |
| `DHIATENSOR (Fractions)` | English Fractional 436, 424, 425 |
| `DHIATENSOR, British (Literary)` | Elite Literary 381, Small Roman Literary 462, Extra Large Roman Literary 307, Italic Literary 383, Script Literary 395, Vertical Script Literary 213 |
| `CHARIENSTU, German (Pfennig)` | Small Roman 404, Large Roman 423, Large Roman 378, Italic 489 |
| `QWERTY, British` | Small Roman 441, Large Roman 442 |
| `DHIATENSOR, British-American` | Large Roman 432, Small Roman 433 |
| `DHIATENSOR, English-Japanese` | Small Roman 332, Large Roman 333 |
| `DHIATENSOR (Chemical)` / `QWERTY, British (Chemical)` | 385 / 222 |
| `DHIATENSOR, Cosmopolitan` / `QWERTY, Cosmopolitan` | 328 / 367 |
| `DHIATENSOR, British-India` / `DHIATENSOR, British` / `QWERTY, British (Literary)` | 458 / 407½ / 203 |
| `QWERTY (Fractions)` / `DHIATENSOR (Fractions, Alternate)` | 494½ / 447 |
| `CHARIENSTU, German (Eszett)` / `CHARIENSTU, German (Fractions)` | 303 / 204 |
| `CHARIENSTU, Danish` / `DHIATENSOR, Hungarian` | 420 / 415 |

Much of this catalog is one layout in many typefaces, and the same few
one-position swaps recur across markets:

- **`$` ↔ `£`** is the American/British split, and it is *only* that one
  position, four times over: `QWERTY` / `QWERTY, British`,
  `DHIATENSOR` / `DHIATENSOR, British`,
  `DHIATENSOR (Fractions)` / `DHIATENSOR, British (Fractions)`, and
  `QWERTY (Fractions)` / `QWERTY, British (Fractions)`.
- **`DHIATENSOR, British-American`** is the wheel that refuses to
  choose — the only one carrying both `$` and `£`, paid for with three
  moved slots.
- **`DHIATENSOR, British-India`** is the British fraction wheel with `₨`
  for `⅞` and `⅓` for `⅛`.
- **`DHIATENSOR, English-Japanese`** carries `¥`, `$` and `£` at once.

Two of the four wheels that aren't a fraction bank are symbol banks:
`CHEMICAL_*` swap the figures row for subscript digits (`₁₂₃₄₅` before
the full-size digits, `₆₇₈₉₀` after, for formulae like H₂SO₄), and
the two `Cosmopolitan` wheels spend nine slots on free-standing
accents plus æ/œ, paying for them by dropping the digit `1` entirely.

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

Eleven of the 84 sighted shuttles, all for reasons of script or of type
that has no codepoint — none for image quality, which is consistently
better here than in the Hammond scans.

- **Bohemian 426/443** — CHARIENSTU letters with a Czech figures row whose
  doubled dead-key accents (`´ ´` and `ˇ ˇ`) cannot be separated reliably.
- **Armenian 218**, **Ancient Greek 309**, **Hebrew 354/358/348/351** —
  whole scripts, each needing its own pass rather than being folded into
  a Latin-wheel batch. 358 needs no reading at all once 354 is done: the
  catalog says in prose that it is 354 with `£` for `$`.
- **Bulgarian 452½** — Cyrillic; the same case as the Hammond Bulgarian
  shuttle, which alphabet accounting eventually solved.
- **Special British 387** — `QWERTY, British (Fractions)`'s row with its
  last five slots given to shilling numerators `1⁄ 3⁄ 5⁄ 7⁄ 9⁄`, each cast as one
  piece of type. Only the first has a codepoint (`⅟`, U+215F), and
  `layout.rows` is strictly one character per position. The reading
  itself is not in doubt.
- **British Telegraph 376** — not the usual three-row 28-column shape.

**Two entries in this list used to be wrong, and both failed the same
way — a group judged on one glance instead of read.**

- *"Each fraction entry packs a different bank."* It doesn't. Twenty-one
  entries collapse to four layouts plus four genuine one- or
  two-position variants. This one deferral was hiding a sixth of the
  whole catalog.
- *"English-Japanese 332/333: kana."* There is no kana on it. It is a
  Latin trading wheel carrying `¥ $ £`.

The lesson is narrow and worth keeping: a shared *heading* ("Fractional",
"English-Japanese") predicts nothing about the rows underneath it. Read
one entry per group before deferring the group.

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

**2. Blickensderfer — done, except for scripts.** All 14 pages have been
read; 73 of their 84 shuttles are imported. What is left is the eleven
in "What was NOT imported" above, of which seven are whole scripts
(Armenian, Greek, Hebrew ×4, Bulgarian) and the rest are Bohemian's
dead-key accents, 387's shilling type and 376's odd shape.

The bigger Blickensderfer gap is now the **missing pages**, not unread
ones: the scans hold catalog pages 3–14, 18 and 21, so pages 1–2, 15–17,
19–20 are absent — roughly 42 more shuttles at this catalog's steady six
per page. Alphabetically, 15–17 fall between English-Japanese and German
(so French and Esperanto sit there) and 19–20 between German and Greek.
Nothing can be done about these without more scans.

**3. Hammond 1920 leftovers — small and fiddly.** 41, 162, 184,
23E/23F/23G, 136. Each is one or two unresolved figure slots, or a
non-standard row shape (184's four lines). Worth a pass with the
higher-resolution TIFF originals rather than more zooming on the small
PDF — that is the specific thing likely to settle 162's damaged glyph
after `4%` and 41's fraction numerators.

**4. Non-Latin scripts — transcribable, just unworked.** Hammond's
non-Latin sets (195 Astronomical, 196/197 Phonetic, 135/135B/135C
Mathematical, 112C Greek, 165/167 Yiddish), the 1915 pre-reform Cyrillic
(Russian 49/35, Servian 125), and Blickensderfer's Armenian 218,
Ancient Greek 309, Bulgarian 452½ and Hebrew 354/358/348/351. All of
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
