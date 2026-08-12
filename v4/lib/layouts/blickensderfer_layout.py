"""
Blickensderfer keyboard layout presets - the named layouts offered by
tune.py's Layout tab picker.

Moved verbatim out of tune.py so layout DATA lives with the other layout
modules in this package rather than hardcoded in the TUI - see this
package's __init__.py for how the per-machine tables are aggregated.
"""

# Named Blickensderfer keyboard layouts, ported verbatim from
# v2/lib/layouts/blick_layouts.scad's DHIATENSOR/QWERTY/SCANDI/
# HEBREW_ENGL/CHARIENSTU_DE/CHARIENSTU_DE_MOD arrays. All share the same
# 3-row structure and the same physical placement_map/latitude_columns -
# only the glyph content per row differs, so switching presets only ever
# rewrites layout.rows. HEBREW_ENGL needs a Hebrew-capable font
# (font.path) to actually render correctly - v2 auto-switches Font_Hebrew
# when this layout is selected, v4 does not (no per-layout font-switching
# wired up), so you'll need to set font.path yourself too.
LAYOUT_PRESETS = {
    "DHIATENSOR": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    "QWERTY": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
        "\"#$%_/-¢@;23456789:!^1.&'(0)",
    ],
    "SCANDI": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-Å_(ä/'\"!1234567890;?åö$)ÄÖ:",
    ],
    "HEBREW_ENGL": [
        "זךכגװפףץצדהעאתןנםשרלסמיטבוקח",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢$)@#:",
    ],
    # NOTE both CHARIENSTU rows below end "WKJY", not "WKJU". v1
    # (v1/Blickensderfer/Blickensderfer2.scad:82,85,88) and v2
    # (v2/lib/layouts/blick_layouts.scad:18,21,24) both read "WKJU" for all
    # three CHARIENSTU variants - an error in the ORIGINAL source, not a v4
    # porting slip, and the same shape as the Hammond Ideal 'b'/'d' bug (see
    # hammond_layout.py). Two independent proofs: (1) mechanically, the
    # uppercase row's letter inventory came out as a-z with U DUPLICATED and
    # Y MISSING, while its own lowercase row is a clean a-z - no typewriter
    # omits Y; (2) the Blickensderfer type-wheel catalog scans (Bohemian
    # No. 426/443, "Catalog/20230113_0155.jpg") print "GMDB:WKJY" plainly at
    # 300%. DHIATENSOR was checked the same way and is clean in both rows.
    "CHARIENSTU_DE": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%¨+-/'\"ö1234567890äü!;?=ß§)",
    ],
    "CHARIENSTU_DE_MOD": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%*+-/'\"^1234567890`´!;?=@§)",
    ],
    # --- From the Blickensderfer type-wheel catalog scans (below) -------
    # Same DHIATENSOR letters, but the shifted row swaps two keys ("." key
    # shifts to & instead of "."; "," key shifts to ? instead of &) and the
    # figures row is entirely different, carrying ¼ ½ ¾ and £.
    # Shuttles: Elite Literary 381, Small Roman Literary 462, Extra Large
    # Roman Literary 307, Italic Literary 383, Script Literary 395,
    # Vertical Script Literary 213 - all six print identical rows, differing
    # only in typeface.
    "BRITISH_LITERARY": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/_¼!1234567890½+¾=£;*':",
    ],
    # QWERTY above is the American wheel; this is the British one, which
    # differs from it in EXACTLY one position - £ where American has $.
    # Shuttles: Small Roman 441, Large Roman 442.
    "QWERTY_BRITISH": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL.YUIOP",
        "\"#£%_/-¢@;23456789:!^1.&'(0)",
    ],
    # --- From the by-language pages of the same catalog scans ---------
    # German (404 Small Roman, 423 Large Roman, 378 Large Roman, 489
    # Italic). Its LETTER rows are identical to CHARIENSTU_DE's; the two
    # differ in four figures-row positions:
    #
    #     CHARIENSTU_DE   ¨ … ö … ä … ß      (from v1/v2)
    #     GERMAN          № … ä … ö … ₰      (from the catalog)
    #
    # So ö/ä are swapped, and the catalogued shuttle carries № (numero)
    # and ₰ (Pfennig, U+20B0 - printed as the Pf ligature, verified at
    # 700%) where v1/v2 have ¨ and ß. A German wheel with no ß looks
    # wrong until you count: Blickensderfer has 28 positions to Hammond's
    # 30, and this shuttle spends its scarce slots on the two symbols
    # German COMMERCE needed. Both are plausible real products, so
    # CHARIENSTU_DE is left alone rather than "corrected" into this.
    #
    # Its row 1 also ends WKJY, a third independent confirmation of the
    # WKJY fix at the top of this file.
    "GERMAN": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%№+-/'\"ä1234567890öü!;?=₰§)",
    ],
    # Danish (420 Small Roman). The same CHARIENSTU arrangement as GERMAN
    # with æ and ø taking the "." and "," keys - two positions in each
    # letter row, nothing else moved.
    "DANISH": [
        "xqzvæpflocharienstugmdbøwkjy",
        "XQZVÆPFLOCHARIENSTUGMDBØWKJY",
        "(%№+-/'\".1234567890,:!;?&£§)",
    ],
    # Hungarian (415 Small Roman). A wholly different letter arrangement -
    # not CHARIENSTU, not DHIATENSOR - built around "hiatensyrlcmo".
    #
    # It self-checks the same way the Hammond Czech and Polish shuttles
    # do: q/Q and x/X sit in the FIGURES row because Hungarian uses
    # neither natively, and row 0 accordingly contains no q and no x.
    "HUNGARIAN": [
        "zpkgüáwfuvhiatensyrlcmoébdöj",
        "ZPKGÜÁWFUVHIATENSYRLCMOÉBDÖJ",
        '§/&q%!;-ú.23456789,?:ÓóäQxX"',
    ],
    # --- The British-market wheels ------------------------------------
    # The fraction bank was originally deferred on the theory that "each
    # entry packs a different one". It doesn't: ten entries across three
    # catalog pages - Imperial 212, and Scientific E458, 412, 428, 363,
    # 393, 357, 454, 300, 205 - print this one layout character for
    # character, differing only in typeface. The eighths read
    # unambiguously at 800% (the 8 of ⅛ is a closed double loop, plainly
    # not the 3 of BRITISH_INDIA's ⅓ below).
    #
    # Its shifted row is BRITISH_LITERARY's, and its figures row is
    # BRITISH_LITERARY's with the fraction slots filled in - the two are
    # the same wheel at two levels of fraction coverage.
    "BRITISH_SCIENTIFIC_FRACTION": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/⅛¼⅜1234567890½⅝¾⅞£;@':",
    ],
    # Mimeograph 331, the one member of that group that is NOT identical:
    # it ends @": where the other ten end @':. Checked at 600% - two
    # distinct marks, not one apostrophe with a scanning artifact.
    "BRITISH_SCIENTIFIC_FRACTION_MIMEO": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/⅛¼⅜1234567890½⅝¾⅞£;@\":",
    ],
    # Small Roman 407½. DHIATENSOR with £ for $, in EXACTLY one position -
    # the same American/British relationship QWERTY and QWERTY_BRITISH
    # already have, on the other keyboard.
    "DHIATENSOR_BRITISH": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG.PWFUDHIATENSORLCMY&BVQJ",
        "-^_(./'\"!1234567890;?%¢£)@#:",
    ],
    # British-American Scientific (Large Roman 432, Small Roman 433). The
    # name is literal: it is the only wheel here carrying BOTH $ and £.
    # Three positions moved off DHIATENSOR to pay for it - shifted row
    # gains & at 4 and £ at 23, figures row gains § at 4.
    "BRITISH_AMERICAN": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY£BVQJ",
        "-^_(§/'\"!1234567890;?%¢$)@#:",
    ],
    # British-India Scientific (Narrow Roman 458). The fraction wheel
    # above with two substitutions: ⅓ for ⅛, and ₨ (U+20A8, printed as
    # the Rs ligature) for ⅞. Both verified at 900% against the
    # corresponding glyphs on the plain Scientific wheel.
    "BRITISH_INDIA": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/⅓¼⅜1234567890½⅝¾₨£;@':",
    ],
    # Chemical (English) No. 385. The figures row is a subscript bank -
    # ₁₂₃₄₅ before the full-size digits and ₆₇₈₉₀ after - for writing
    # formulae like H₂SO₄. Every one is a real codepoint (U+2080..2089),
    # so this transcribes exactly despite looking exotic.
    "CHEMICAL_ENGLISH": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG’PWFUDHIATENSORLCMY°BVQJ",
        "—+=(₁₂₃₄₅1234567890₆₇₈₉₀)@%:",
    ],
    # Cosmopolitan Scientific No. 328 - the multi-language accent wheel.
    # It spends nine slots on free-standing accents (^ ´ ` ¨ ~ ˘ ¸ °) and
    # the æ/œ ligatures, and pays for them by dropping the digit 1
    # entirely; æ sits in DHIATENSOR's "1" position and the remaining
    # digits keep their own slots. The mark before £ is a BREVE, not a
    # caron - confirmed at 700%, a smooth cup with no angular vertex.
    "COSMOPOLITAN": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/^´`æ234567890œ¨~˘£¸°':",
    ],
    # --- The Universal (QWERTY) market wheels -------------------------
    # All four below share a shifted row that differs from plain QWERTY's
    # in one position: & where QWERTY has "." (except CHEMICAL_UNIVERSAL,
    # which puts ’ there and ° in the "?" slot, matching CHEMICAL_ENGLISH
    # on the other keyboard).
    #
    # Universal fraction (Elite 350, Small Roman 494, Large Roman 379,
    # Italic 371, Script 337, Vertical Script 217) - six entries, one
    # layout. Cross-checks against QWERTY: digits 2-9 stay at positions
    # 10-17 and 1 stays at 21, exactly where the plain wheel has them.
    "UNIVERSAL_FRACTION": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL&YUIOP",
        "\"@/%;-⅛¼⅜½23456789⅝¾⅞1£:'(0)",
    ],
    # Universal literary (Small Roman Literary 203) - the QWERTY
    # counterpart of BRITISH_LITERARY, carrying only ¼ ½ ¾ where
    # UNIVERSAL_FRACTION carries the full eighths bank.
    "UNIVERSAL_LITERARY": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL&YUIOP",
        "\"*/%;-=¼!½23456789+¾_1£:'(0)",
    ],
    # Chemical, Universal (British) No. 222 - CHEMICAL_ENGLISH's subscript
    # bank on the QWERTY wheel.
    "CHEMICAL_UNIVERSAL": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM°HJKL’YUIOP",
        "₁₂₃₄₅+—=[;23456789%]@1£₆₇₈₉₀",
    ],
    # Universal Small Roman No. 367 - COSMOPOLITAN's accent bank on the
    # QWERTY wheel, and the one wheel here whose figures row does NOT
    # keep the digits in their usual slots: it splits them 2345 … 67890
    # around the accents and drops 1, so the row IS the mapping rather
    # than a permutation of the standard one.
    "UNIVERSAL_ACCENT": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL&YUIOP",
        "%2345/˘æ´`()¨°¸\"-:^'~œ£67890",
    ],
    # --- The American (English Fractional) wheels ----------------------
    # Elite 436, Small Roman 424, Large Roman 425. Identical to
    # BRITISH_SCIENTIFIC_FRACTION but for $ in place of £ - the same
    # single-position American/British split as QWERTY/QWERTY_BRITISH and
    # DHIATENSOR/DHIATENSOR_BRITISH.
    "DHIATENSOR_FRACTION": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/⅛¼⅜1234567890½⅝¾⅞$;@':",
    ],
    # Small Roman 447 - the odd one out of that group, and not a variant
    # of it at all: it moves the fractions to the FRONT of the figures
    # row (⅛¼½ where DHIATENSOR has -^_), keeps $, adds £ in the last
    # slot, and puts : where its siblings have ? in the shifted row.
    "DHIATENSOR_FRACTION_ALT": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY:BVQJ",
        "⅛¼½(-/'\"!1234567890;?%¢$)@#£",
    ],
    # English-Japanese Scientific (Small Roman 332, Large Roman 333).
    # The name is misleading and cost this entry a wrongly-deferred round:
    # there is no kana on it. It is a TRADING wheel - plain DHIATENSOR
    # letters whose figures row carries all three of ¥, $ and £, paid for
    # by dropping ⅜ and ¾ from the fraction bank.
    "ENGLISH_JAPANESE": [
        "zxkg.pwfudhiatensorlcmy,bvqj",
        "ZXKG&PWFUDHIATENSORLCMY?BVQJ",
        "\"()-%/⅛¼_1234567890½⅝¥$£;@':",
    ],
    # Universal Small Roman 494½ - UNIVERSAL_FRACTION with $ for £.
    "UNIVERSAL_FRACTION_US": [
        "qwertasdfgzxcvbnm,hjkl.yuiop",
        "QWERTASDFGZXCVBNM?HJKL&YUIOP",
        "\"@/%;-⅛¼⅜½23456789⅝¾⅞1$:'(0)",
    ],
    # --- Two more German wheels ---------------------------------------
    # Extra Large Roman 303. A third German reading, and the one that
    # settles what GERMAN above could not: it carries CHARIENSTU_DE's ¨
    # and ß, but GERMAN's ä/ö ORDER. So the catalog corroborates ¨/ß as
    # genuine (they are not errors that GERMAN's №/₰ correct), while
    # leaving CHARIENSTU_DE's ä-at-19/ö-at-8 as the minority reading -
    # two catalogued wheels put ä at 8. Not enough to overwrite a v1/v2
    # array on (unlike WKJY, there is no letter-inventory argument here,
    # just a 2-to-1 count), so all three ship side by side.
    "GERMAN_ESZETT": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%¨+-/'\"ä1234567890öü!;?=ß§)",
    ],
    # Large Roman 204 - the German fractional wheel. Gives up 1, ¨/№ and
    # ß to carry ¼ ½ ¾ and ⅟ (U+215F, the "1⁄" numerator used to build
    # arbitrary fractions - the same piece of type whose 3⁄ 5⁄ 7⁄ 9⁄
    # siblings are why Special British 387 is held below; here the ONE
    # form that does have a codepoint appears alone, so this one imports).
    "GERMAN_FRACTION": [
        "xqzv.pflocharienstugmdb,wkjy",
        "XQZV&PFLOCHARIENSTUGMDB:WKJY",
        "(%¼+-/'\"ä⅟23456789½öü!;?=¾§)",
    ],
}

# Source for the five catalog-derived presets above, and the WKJY
# correction: 14 page scans of a Blickensderfer type-wheel catalog
# ("E:/Type Elements/Blickensderfer/Catalog/20230113_01{55..68}.jpg" on
# the Windows box; local copy in ~/Blickensderfer-Catalog), organised by
# language/market - ARMENIAN, BOHEMIAN, BRITISH (Imperial / Scientific /
# Literary / Universal), BRITISH-AMERICAN, DANISH, GERMAN, HUNGARIAN and
# more - each entry printed as "<Typeface> No. <n>. Code Word-<word>"
# followed by the same three 28-character rows this machine already uses.
# It confirms DHIATENSOR character for character.
#
# All 14 pages have now been surveyed. Two shipped presets came back
# independently confirmed in bulk: every English Scientific entry (365,
# 407, 409, 455, 457, 356, 362, 374, 474, 440, 499, 201, 223, 308) prints
# DHIATENSOR, and every plain Universal entry (325, 406, 418, 364, 359,
# 497, 304, 216) prints QWERTY.
#
# NOT imported, needing their own verification pass first (a wrong glyph
# silently builds a wrong wheel, same rule as the Hammond catalogs):
#   - Bohemian 426/443: CHARIENSTU letters with a Czech figures row whose
#     doubled dead-key accents (´ ´ and ˇ ˇ) can't be separated reliably
#     at this scan resolution.
#   - Armenian 218: full Armenian script, needs a font with those glyphs.
#   - Special British 387: UNIVERSAL_FRACTION's row with its last five
#     slots given over to shilling numerators - 1⁄ 3⁄ 5⁄ 7⁄ 9⁄, each cast
#     as ONE piece of type. Only the first has a single codepoint (⅟,
#     U+215F); the rest would each need two, and layout.rows is strictly
#     one character per position. Held on that alone - the reading itself
#     is not in doubt.
#   - British Telegraph 376: a non-standard row shape, not the usual
#     three-row 28-column form.
#   - The Hebrew wheels beyond HEBREW_ENGL (354, 358, HEBREW-BRITISH 348,
#     HEBREW-ENGLISH No. 2 351) and Ancient Greek 309: both scripts read
#     cleanly at this resolution, but each needs a transcription pass of
#     its own rather than being folded into a Latin-wheel batch. Note 358
#     needs no reading at all when 354 is done - the catalog says in
#     PROSE that it is 354 with £ for $.
#   - Bulgarian 452½: Cyrillic, and the same case as the Hammond
#     Bulgarian shuttle - solvable by alphabet accounting, not yet done.
#
# TWO deferrals in this list turned out to be wrong, both from judging a
# group on one glance rather than reading it:
#   - "each fraction entry packs a different bank" - no. Twenty-one
#     entries collapse to four layouts (BRITISH_SCIENTIFIC_FRACTION,
#     UNIVERSAL_FRACTION and their $ twins DHIATENSOR_FRACTION /
#     UNIVERSAL_FRACTION_US), plus four genuine one- or two-position
#     variants (331, 458, 447, 387).
#   - "ENGLISH-JAPANESE 332/333: kana" - no kana on it whatsoever; it is
#     a Latin trading wheel carrying ¥ $ £, and imported above.
