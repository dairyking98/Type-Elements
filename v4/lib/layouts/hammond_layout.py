"""
Hammond keyboard layout presets, plus the shared Hammond type-shuttle
catalog data both Hammond machines draw on (CATALOG_*).

hammond_split_layout.py imports the CATALOG_* tables from here - they are
defined once, in this module, because the printed catalog covers both
machines. Note the two machines store rows in OPPOSITE orders; see
CATALOG_UNIVERSAL_STANDARD's comment.
"""

# ---------------------------------------------------------------------
# Hammond type-shuttle catalog (both Hammond machines)
# ---------------------------------------------------------------------
# Primary source: the Hammond Typewriter Company's own "ENGLISH Type
# Shuttles for the Hammond Typewriter" catalog, Form QQ-10M-11-20-W
# (Nov 1920). Every entry is "<shuttle number>-<typeface>", followed by
# three 30-character rows printed as two 15-character halves - which is
# exactly this family's layout.rows/latitude_columns=30 shape.
#
# Two keyboards, and they are NOT interchangeable layouts:
#   Universal - qwerty, the familiar arrangement.
#   Ideal     - Hammond's own proprietary arrangement, a different set of
#               key positions entirely (not a qwerty remap).
# Both appear in the catalog and both are real for either machine, so
# both are offered on hammond AND hammond_split below. NOTE the storage
# order differs per machine and is load-bearing: hammond stores rows
# REVERSED (see its "Universal" preset), hammond_split stores them
# in catalog reading order (lib/hammond_split.py's TextAssemble does its
# own per-half [14-i]/[29-i] reversal). The reversal is applied
# programmatically below rather than by hand-retyping the strings.
#
# The catalog's ~80 entries collapse to a handful of distinct LAYOUTS -
# most differ only in typeface (a font choice here, not a layout), and
# within a keyboard the letter rows are constant, so all real variation
# is in the figures row. Only layouts verified character-by-character
# against the scan are defined here (see also the 1915 per-language
# section further down); CATALOG_SHUTTLES records which numbered shuttles
# each one covers, and which catalogued variants are deliberately NOT
# imported yet, with the reason for each.
CATALOG_UNIVERSAL_STANDARD = [
    "qazwsxedcrfvtgb" "yhnujmik,ol.p;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    '1"@2#×3$+4%£5_¢' "6&*7'^8(°9).0=/",
]
CATALOG_IDEAL_STANDARD = [
    "?zxqkjgbmpcfld," ".taherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "=%@÷#×1+2¢3£4$5" "6“7”8’9(0)°’_”/",
]
CATALOG_IDEAL_FRACTIONS = [
    "?zxqkjgbmpcfld," ".taherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "¾%⅞⅝½⅜1⅛2¢3£4$5" "6“7”8’9(0)¼*⅓†⅔",
]
# Universal with a 9-fraction figures row. Reading the catalog by COLUMN
# (each column is one physical key: unshifted / shifted / figure) shows
# what this shuttle actually did, and the three rows corroborate each
# other: nine figure slots became fractions (#×+ &*^ °.= -> ⅜⅔⅓ ⅝⅛½
# ¼¾⅞), and the "&" those displaced was re-homed onto the shifted "."
# key - which is why row 1 is untouched but row 2 reads ...?OL&P:! where
# standard reads ...?OL.P:!. That "." key is the one with a bare dot on
# all three levels (visible on the "Universal" KEYBOARD plate, p.2), so
# it was the only spare slot to move & into.
CATALOG_UNIVERSAL_FRACTIONS = [
    "qazwsxedcrfvtgb" "yhnujmik,ol.p;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL&P:!",
    '1"@2⅜⅔3$⅓4%£5_¢' "6⅝⅛7'½8(¼9)¾0⅞/",
]
# Caps and Small Caps (27, 27E). The catalog prints row 0 in visibly
# smaller capitals, but row 0 stores LOWERCASE, not capitals: on a small-
# caps face the lowercase codepoints ARE the small capitals, so a
# correctly-designed font renders this row exactly as the catalog shows
# while the two cases still line up. Storing capitals here instead would
# hard-code the appearance into the layout and then fight whatever font
# is selected.
#
# The consequence is that this collapses to CATALOG_UNIVERSAL_STANDARD -
# which is the right answer, and the same conclusion the rest of this
# file keeps reaching: "Caps and Small Caps" is a TYPEFACE, like Gothic
# or Clarendon, not a key arrangement. It stays a named entry so the
# picker documents shuttles 27/27E, and is defined by reference so the
# two can never drift apart.
CATALOG_UNIVERSAL_CAPS_SMALL_CAPS = list(CATALOG_UNIVERSAL_STANDARD)

# ---------------------------------------------------------------------
# Per-language Ideal layouts (1915 catalog)
# ---------------------------------------------------------------------
# Second primary source: "Hammond_type_Catalog_1915.pdf", 35pp, organised
# BY LANGUAGE rather than by shuttle number - each section (Croatian,
# Danish, Dutch, English, Polish, Portuguese, Roumanian, Russian, Servian,
# Spanish, ...) lists the shuttles cut for that language. It independently
# CONFIRMS the 1920-catalog layouts above: its English entries 37/10 match
# CATALOG_IDEAL_STANDARD and 1/2 match CATALOG_IDEAL_FRACTIONS character
# for character, five years apart.
#
# The layouts below keep the Ideal key ORDER and substitute the
# language's own characters into it, so they diff against
# CATALOG_IDEAL_STANDARD in only a few positions outside the figures row
# (Dutch 3 in row 0 / 1 in row 1; Spanish 1 in row 0 / 0 in row 1).
CATALOG_IDEAL_DUTCH = [
    "özxqkjgbmpcfld," "ütaherisounwyvä",
    "!ZXQKJGBMPCFLD;" ".TAHERISOUNWYV&",
    # Position 29 is ƒ, the guilder sign, NOT a plain "f": row 0 already
    # carries a lowercase f (in "...bmpcfld"), and a figures row does not
    # repeat a letter that already has its own key. The scan shows the
    # hooked/crossed italic form at 200dpi, and the guilder is the one
    # currency mark a Dutch machine would need that £/$ don't cover.
    "¾%@?½:1-2§3£4$5" "6„7”8’9(0)¼*_ƒ/",
]
CATALOG_IDEAL_SPANISH = [
    "?zxqkjgbmpcfld," "átaherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    # ç (cedilla hook, no vertical stroke) - distinct from the ¢ that the
    # CENT variant below carries at that same position; both were checked
    # at 200dpi. ¨ is the diaeresis dead key (Spanish ü). The full
    # accent set á é í ó ú ñ ¡ ¿ is present and self-consistent.
    "¨%/_ç¡1ó2.3£4$5" "6“7”8’9(0)ñíéú¿",
]
# Same Spanish shuttle family, but ½ and ¢ where the above has ¨ and ç -
# those two positions are the ONLY difference between them.
CATALOG_IDEAL_SPANISH_CENT = [
    "?zxqkjgbmpcfld," "átaherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "½%/_¢¡1ó2.3£4$5" "6“7”8’9(0)ñíéú¿",
]
# Spanish Caps and Small Caps (5A). Row 0 stores lowercase for the same
# reason as the Universal pair above - the small-caps face supplies the
# small capitals the catalog prints.
#
# Unlike that pair this does NOT collapse into its plain sibling: the
# accented letters in the FIGURES row really are full capitals here
# (ÑÍÉÚ, where CATALOG_IDEAL_SPANISH has ñíéú), and those are reached by
# the figure shift rather than the case shift, so they are a genuine
# character difference rather than a font one. Row 2 is left exactly as
# printed.
CATALOG_IDEAL_SPANISH_CAPS = [
    "?zxqkjgbmpcfld," "átaherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "¨%/_ç¡1ó2.3£4$5" "6“7”8’9(0)ÑÍÉÚ¿",
]
# Croatian (58 Medium Roman, 12C Large Roman). Rows 0/1 are identical to
# CATALOG_IDEAL_DUTCH's - the ö/ü/ä in the three "extra" slots are not a
# transcription slip: this is a 1915 catalog and Croatia was still
# Austria-Hungary, where German was co-official, so a Croatian machine
# carrying German vowels is exactly what you would expect. All the
# language-specific characters are in the figures row.
CATALOG_IDEAL_CROATIAN = [
    "özxqkjgbmpcfld," "ütaherisounwyvä",
    "!ZXQKJGBMPCFLD;" ".TAHERISOUNWYV&",
    "ž%Ž?ć:Ć-2§3č4Č5" "6„7”8=9(+)Š*_š/",
]
# Danish, fractions (87 Medium Roman). Note this layout SHIFTS relative to
# every other Ideal one: æ takes position 14 (where the others have ","),
# which pushes "," into position 15 and "." into 15 of the shifted row -
# so the diff against the standard Ideal rows is 4 positions in row 0, not
# the 1-3 the other languages show.
CATALOG_IDEAL_DANISH_FRACTIONS = [
    "øzxqkjgbmpcfldæ" ",taherisounwyvå",
    "ØZXQKJGBMPCFLDÆ" ".TAHERISOUNWYVÅ",
    "¾¼%÷½×1:2-3⅓4⅔5" "6”7⅛8’9_0⅜£⅝⅞/&",
]
# Portuguese (63 Medium Roman). Full ã/õ/ç set in the letter rows plus
# á/ê/ó/ô/ú/é in the figures row.
CATALOG_IDEAL_PORTUGUESE = [
    "ãzxqkjgbmpcfldç" "õtaherisounwyv.",
    "ÃZXQKJGBMPCFLDÇ" "ÕTAHERISOUNWYV&",
    'á%/!ê;ó,2:3£4$5' "6+7\"8'9(ôú-)é°?",
]
# French (61 Small Roman, 14 Medium Roman, 62 Large Roman, 15 Italic).
# Only one position outside the figures row differs from English Ideal -
# é replaces "." at position 15 - so the whole language fits in row 2.
CATALOG_IDEAL_FRENCH = [
    "?zxqkjgbmpcfld," "étaherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "¨%/èçù1à2.3£4$5" "6“7”8’9(0)ûôîêâ",
]
# German, New Orthography (36B Small Roman, 114 Medium Roman). Its letter
# rows match CATALOG_IDEAL_DUTCH's except that row 1 carries capital
# Ö/Ü/Ä where Dutch has !/./& - and the figures row ends in ß where Dutch
# ends in ƒ.
#
# That ƒ/ß pairing is worth noting: the same physical slot holds each
# language's own extra character - the Dutch guilder, the German eszett -
# which independently corroborates the ƒ reading argued for above.
#
# The OLD-orthography German shuttles (36, 11, 12) are NOT here: they
# print a different glyph in that slot, a stem with a top-right hook and
# a foot serif that reads as long-s (ſ, U+017F) rather than the clearly
# looped ß that 36B prints. Old-orthography German really did use long-s,
# so that is plausible rather than a misprint - but ß is also needed in
# both orthographies, which makes an ſ-only shuttle odd. Not confident
# enough to call, so held.
CATALOG_IDEAL_GERMAN_NEW_ORTHOGRAPHY = [
    "özxqkjgbmpcfld," "ütaherisounwyvä",
    "ÖZXQKJGBMPCFLD." "ÜTAHERISOUNWYVÄ",
    "¾%&?½:1-2§3;4!5" "6„7”8’9(0)¼*_ß/",
]
# German, OLD orthography (36, 11, 12 Ideal). Identical to
# CATALOG_IDEAL_DUTCH in every position but one: ſ (long s, U+017F) where
# Dutch has ƒ (guilder).
#
# That slot was held for a while because ſ and a worn ß are easy to
# confuse. It was settled by finding the two printed on the SAME page in
# the same typeface and size - Universal 119A (old orthography) against
# Universal 117 (New Orthography), catalog p.44 - where they are plainly
# different glyphs: 119A a single descending stroke with a top hook and
# no bowl, 117 a clear bowl. Old-orthography German shuttles carry ſ, New
# Orthography ones carry ß, and the same old/new split shows up
# independently in the Ideal pair 36 vs 36B. Two independent pairs
# agreeing is what made this callable.
CATALOG_IDEAL_GERMAN = [
    "özxqkjgbmpcfld," "ütaherisounwyvä",
    "!ZXQKJGBMPCFLD;" ".TAHERISOUNWYV&",
    "¾%@?½:1-2§3£4$5" "6„7”8’9(0)¼*_ſ/",
]
# ---------------------------------------------------------------------
# Per-language UNIVERSAL layouts (1915 catalog)
# ---------------------------------------------------------------------
# The per-language work above is all IDEAL. The catalog carries Universal
# (qwerty) equivalents for most of the same languages - German, Russian,
# Italian, French, Swedish-Finnish, Spanish, Dutch and more - which is the
# single largest un-imported group; see CATALOG_INDEX.md for the count.
# These keep the Universal key ORDER and substitute the language's own
# characters into it, exactly as the Ideal ones do.
#
# German, New Orthography (117, 117A Italic; 119C Gothic Italic; 124 Large
# Italic; 145A Multigraph): ü/ä/ö take the ./;/- slots at the end of row
# 0, their capitals take the same slots in row 1, and the figures row
# carries ß.
CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY = [
    "qazwsxedcrfvtgb" "yhnujmik,olüpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK.OLÜPÄÖ",
    "1„@2“:3!#4%?5_-" "6&*7’§8(ß9);0=/",
]
# French (69 Large Roman, 32/32A Medium Roman, 67 Small Roman, 104/104A
# Italic, 85/111/111A Vertical Script, 134E Large Gothic, 145B
# Multigraph). é takes the "." slot in row 0; row 1 is unchanged from
# English, and the whole language lives in the figures row.
CATALOG_UNIVERSAL_FRENCH = [
    "qazwsxedcrfvtgb" "yhnujmik,olép;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    "1”è2¨ù3$à4%£5_û" "6&ô7’î8(â9)ê0ç/",
]
# Trilingual French-German-English (32E) - the German vowels ö/ä/ü are
# folded into the FIGURES row rather than given their own keys, which is
# how one shuttle covers three languages: ° and ¾/¼ take the slots French
# alone leaves free.
CATALOG_UNIVERSAL_FRENCH_GERMAN_ENGLISH = [
    "qazwsxedcrfvtgb" "yhnujmik,olép°-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:¾",
    '½"è2öù3äà4%£5üû' "6&ô7'î8(â9)ê¼ç/",
]
# Esperanto (135A, 135D). All six accented letters are present -
# ĉ ĝ ĥ ĵ ŝ ŭ - five of them in the letter rows and ĥ/ŭ in the figures
# row, so the language is fully typeable from one shuttle.
CATALOG_UNIVERSAL_ESPERANTO = [
    "qazwsxedcrfvtgb" "yhnujmikŝolĉpĵĝ",
    "QAZWSXEDCRFVTGB" "YHNUJMIKŜOLĈPĴĜ",
    '1"@2/×3$+4%!5_-' "6ĥ;7':8(,9).0?ŭ",
]
# Italian (134F Large Gothic, 73/32B Medium Roman, 67A Small Roman,
# 69A Large Roman, 104B/150B Italic, 85A/111B Vertical Script).
# Full à/è/é/ì/ò/ù plus ç. Note this diverges from Universal French in
# row 0 as well as the figures row - Italian puts ’ where French has ","
# and moves ./, to the end - so it is not just a figures-row swap.
CATALOG_UNIVERSAL_ITALIAN = [
    "qazwsxedcrfvtgb" "yhnujmik’olép.,",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL;P:!",
    "1”+2×ù3¨=4%°5_à" "6&-7èò8(ì9)§0ç/",
]
# Portuguese (150 Italic, 103/103A/103B Medium Roman, 159 Small Roman).
# ã/õ/ç in the letter rows, á/ê/ó/ô/é in the figures row, plus º the
# masculine ordinal indicator - the mark that makes it unmistakably
# Portuguese rather than Spanish.
CATALOG_UNIVERSAL_PORTUGUESE = [
    "qazwsxedcrfvtgb" "yhnujmik,olãpçõ",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OLÃPÇÕ",
    '1";2:á3$_4%£5ê-' "6&ó7'ô8(§9)éº./",
]
# Roumanian (32C, 32D Medium Roman, 97A Gothic Italic). Carries the full
# breve/cedilla set - ă ĕ ĭ ŭ, ş, ţ - plus â/î/ê, and a standalone ¸
# (cedilla, U+00B8) as its own character in the figures row.
CATALOG_UNIVERSAL_ROUMANIAN = [
    "qazwsxedcrfvtgb" "yhnujmik,olĕp;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    "1“¸2ş”3§ă4%ĭ5_ŭ" "6&*7’î8(â9)ê0ţ/",
]
# Roumanian, Ideal (92). Held for a while on the mark closing row 1,
# which would not separate from ¸ at 600%. Settled by the Universal
# Roumanian shuttle (32C) above, which carries ¸ (U+00B8) outright as a
# standalone figures-row character: once the language is known to have a
# bare cedilla in its repertoire, and the shape matches, it is the only
# reading left. Same corroborate-from-a-sibling-shuttle move that settled
# the German ſ.
#
# ş/ţ are the CEDILLA codepoints (U+015F/U+0163), not the modern
# comma-below ș/ț - the cedilla forms are what 1915 Romanian typography
# used, and what the Universal shuttle prints.
CATALOG_IDEAL_ROUMANIAN = [
    "îzxqkjgbmpcfld," "ătaherisounwyvĭ",
    ";ZXQKJGBMPCFLDŭ" "ĕTAHERISOUNWYV¸",
    "!%/?_:1-2.3â4ê5" "6ţ7*8’9ş0§“(”)&",
]
# Spanish (33 Medium Roman, 66/66B Small Roman, 47 Large Roman, 89
# Vertical Script, 28A Law Italic, 68A Italic). Same ¨/½ split the Ideal
# Spanish shuttles have - 66B carries ½ where 33 carries ¨.
CATALOG_UNIVERSAL_SPANISH = [
    "qazwsxedcrfvtgb" "yhnujmik,oláp;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    '1"@2¨¡3$¿4%£5_ñ' "6&ó7'í8(ú9)é0ç/",
]
# The two Scandinavian shuttles are a matched pair, and reading them
# together is what makes each trustworthy: they differ in exactly ONE
# letter position - å for Swedish-Finnish, æ for Danish-Norwegian - plus
# two figures-row slots. The catalog demonstrably had both å and æ and
# chose between them, so neither is a misreading of the other.
#
# Danish-Norwegian carrying Æ Ä Ö rather than Æ Ø Å is historically
# unusual (Danish needs ø), and it was held on that basis until the pair
# above settled it. Recorded as read, not as one might expect it to be.
CATALOG_UNIVERSAL_SWEDISH_FINNISH = [
    "qazwsxedcrfvtgb" "yhnujmik,olåpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OLÅPÄÖ",
    '1"ü2:é3!à4%£5+-' "6&½7*#8(.9);0=/",
]
CATALOG_UNIVERSAL_DANISH_NORWEGIAN = [
    "qazwsxedcrfvtgb" "yhnujmik,olæpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OLÆPÄÖ",
    '1"ü2:é3!à4%£5+-' "6&½7'§8(.9);0=/",
]
# Bohemian/Czech, Ideal (54, 86, 120, 153C Gothic, 154A/155A/156A Roman,
# 157A Italic). Full caron/ring set: ž č š ř ě ů ň plus á í é ý and
# ö/ü/ä.
#
# It self-checks in a satisfying way: q and w live in the FIGURES row,
# not the letter rows, because Czech does not use them in native words -
# and sure enough row 0 contains neither. A misreading of the letter rows
# would almost certainly have broken that.
CATALOG_IDEAL_BOHEMIAN = [
    "žzxčkjgbmpcfld," "átaherisounšyvř",
    "ŽZXČKJGBMPCFLD:" ".TAHERISOUNŠYVŘ",
    'q%Q?íé1-2ö3ü4ä5' "6ě7\"8'9ů&úňwýW/",
]
# Polish, Ideal (155 Small Roman, 77/154 Medium Roman, 156 Large Roman,
# 157 Italic, 153B Gothic, 121 Polish-German). Complete Polish set:
# ł ż ą ę ź ć ś ń ó with their capitals.
#
# Same self-check Bohemian passes: q and Q sit in the FIGURES row because
# Polish has no native q, and row 0 contains none. Two languages
# independently putting their unused Latin letters on the figure shift is
# a good sign both letter rows were read correctly.
CATALOG_IDEAL_POLISH = [
    "łzxżkjgbmpcfld," "ątaherisounwyvę",
    "ŁZXŻKJGBMPCFLD." "ĄTAHERISOUNWYVĘ",
    'q%Q?Źź1-2&3Ć4ć5' "6:7\"8'9ś¨ŚńóŃÓ/",
]
# Hungarian, Ideal (152 Small Roman, 44/57 Medium Roman, 151 Large Roman,
# 74 Gothic Italic). Complete Hungarian vowel set including the
# double-acute ő and ű that no other language here needs.
#
# Figures-row position 0 is the digit 1, not a bare vertical bar, and the
# row proves it internally: digits 2/3/4/5 sit at exactly their standard
# Ideal positions (8/10/12/14) while 1 has moved from position 6 to 0,
# displacing "=" - which then reappears in the right half at position 27.
# Every character is accounted for, so no slot is left needing a glyph
# that is not there.
CATALOG_IDEAL_HUNGARIAN = [
    "özxqkjgbmpcfld," "átaherisounwyvé",
    "ÖZXQKJGBMPCFLD;" "ÁTAHERISOUNWYVÉ",
    "1%!?.:*-2§3Ú4ú5" "6ű7ő8Ü9üäÓ&ó=”/",
]
# Chilian (47A Large Roman, 89A Vertical Script, 16A/17A/46A/65A/66A/33A).
# Differs from CATALOG_UNIVERSAL_SPANISH in exactly three positions: ä/ö
# replace ¨/¡ and ü replaces ç. German vowels on a Chilean shuttle is not
# a slip - Chile had a large German-speaking population by 1915, and this
# is the shuttle that serves both.
CATALOG_UNIVERSAL_CHILIAN = [
    "qazwsxedcrfvtgb" "yhnujmik,oláp;-",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    '1"@2äö3$¿4%£5_ñ' "6&ó7'í8(ú9)é0ü/",
]
# Russian (143 Large Roman). Pre-reform orthography: і (U+0456), ѣ yat
# (U+0462/3) and Ѵ izhitsa (U+0474) are all present, along with № .
#
# The letter-inventory check works here too, and is what makes a Cyrillic
# read trustworthy: of the six pre-reform letters absent from row 0
# (ж х ц э ѳ ѵ), five reappear in the FIGURES row. Only ѳ (fita) is
# genuinely missing from this shuttle, which is unremarkable - fita was
# rare by 1915 and was abolished outright three years later.
#
# Note Ѵ reads as a Latin-looking V because izhitsa IS V-shaped; that is
# the character, not a Latin letter.
CATALOG_UNIVERSAL_RUSSIAN = [
    "йфяіычувѣкъсеам" "нпигртшоьщлбздю",
    "ЙФЯІЫЧУВѢКЪСЕАМ" "НПИГРТШОЬЩЛБЗДЮ",
    '1Ѵ-2%"3э!4Э:5ц.' "6Ц№7х,8Х/9ж(0Ж)",
]
# Bohemian/Czech, Universal (116 Medium Roman). Not a simple substitution
# into the qwerty order - it uses all THREE levels of three keys to fit
# Czech in. At positions 5/10/13 the unshifted level carries ě/é/í, the
# shift level keeps the Latin capital X/F/G, and the FIGURE level carries
# the Latin lowercase x/f/g. Row 0 accordingly contains no x, f or g.
#
# That three-level split is itself the check: a misread would almost
# certainly have put a lowercase Latin letter back into row 0.
CATALOG_UNIVERSAL_BOHEMIAN = [
    "qazšsěedcrévtíb" "yhnujmik,olápčř",
    "QAZŠSXEDCRFVTGB" "YHNUJMIK;OL.PČŘ",
    '1„%2“x3ď!4f:5g-' "6§ň7úť8(?9)ůýq/",
]
# Italian, Ideal (61A Small Roman, 14A Medium Roman, 62A Large Roman,
# 15A Italic). Three positions apart from CATALOG_IDEAL_FRENCH: ì and ò
# take the £/$ slots, and row 0 ends "." rather than ":". Everything
# Italian needs (à è é ì ò ù) plus ç and the circumflex set it shares
# with French.
CATALOG_IDEAL_ITALIAN = [
    "?zxqkjgbmpcfld," "étaherisounwyv.",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "¨%/èçù1à2.3ì4ò5" "6“7”8’9(0)ûôîêâ",
]
# Dutch, Universal, FRACTIONS (34D, 50C, 71F, 84C, 119E). ¼/½/¾ take the
# @/#/_ slots. The guilder is confirmed here rather than argued: 119E is
# an ITALIC shuttle, and at that size the hooked ƒ is unmistakable where
# the roman faces left it debatable.
CATALOG_UNIVERSAL_DUTCH_FRACTIONS = [
    "qazwsxedcrfvtgb" "yhnujmik,olüpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    "1„¼2“½3$¾4%£5_-" "6&*7’§8(ƒ9);0=/",
]
# German, Universal, New Orthography, FRACTIONS (119C, 117D, 117E, 55F,
# 101E, 71E). Identical to CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY
# except ¼/½/¾ at positions 2/8/13 - the same three slots Dutch uses for
# its fractions, which is a good sign both were read right.
CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY_FRACTIONS = [
    "qazwsxedcrfvtgb" "yhnujmik,olüpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK.OLÜPÄÖ",
    "1„¼2“:3!½4%?5¾-" "6&*7’§8(ß9);0=/",
]
# Dutch, Universal (71A, 117B, 34A, 50A, 119B). Position 5 is ⅌, the PER
# SIGN (U+214C) - identified by the machine's owner, not from the scan,
# after it resisted reading in three different faces.
#
# It also explains something in the source: v2/hammond_split.scad's
# Qwerty_Element carries ⅌ at position 5 and § at position 20, which are
# exactly the two positions where Dutch/German Universal differ from
# ENGLISH Universal. An earlier note here called those two characters
# errors "that no catalogued Universal entry shows" - that was wrong, and
# is corrected in hammond_split_layout.py. They show up here.
# QUOTE MARKS: position 4 of the Universal German/Dutch figures row is
# “ (U+201C), not ” — verified at 600% on shuttle 71A, where the raised
# pair curls the same way as the low „ beside it (6-shaped, not 9-shaped).
# All five layouts sharing that row half are spelled from that one
# verified instance.
#
# NOT verified, and deliberately left as read: the IDEAL family's quote at
# its own position (the "6„7”8’" run). Dutch and German diverge here in
# real typography - German pairs „…“ while Dutch pairs „…” - so this is
# not safe to normalise by convention. If it matters, check it directly.
CATALOG_UNIVERSAL_DUTCH = [
    "qazwsxedcrfvtgb" "yhnujmik,olüpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    "1„@2“⅌3$#4%£5_-" "6&*7’§8(ƒ9);0=/",
]
# German, Universal, OLD orthography (119A, 84, 34, 50, 71, 117, 119).
# Differs from CATALOG_UNIVERSAL_DUTCH in exactly ONE position: ſ where
# Dutch has ƒ - precisely the same single-character relationship their
# Ideal counterparts have. Two independent keyboard families showing the
# same guilder/long-s split is about as good as corroboration gets here.
CATALOG_UNIVERSAL_GERMAN = [
    "qazwsxedcrfvtgb" "yhnujmik,olüpäö",
    "QAZWSXEDCRFVTGB" "YHNUJMIK?OL.P:!",
    "1„@2“⅌3$#4%£5_-" "6&*7’§8(ſ9);0=/",
]
# Russian, Universal, OLD STYLE (29, 29A, 29B) - a different arrangement
# from CATALOG_UNIVERSAL_RUSSIAN (143), not a typeface variant of it.
#
# Position 14 really is a Latin N, confirmed by eye against the print:
# Cyrillic Н is H-shaped, and the numero sign prints with its raised "o"
# elsewhere in this same catalog (143), which this glyph lacks.
#
# Same inventory check as 143 and the same result: of the six pre-reform
# letters absent from row 0 (ж х ц э ѳ ѵ - here х ш щ э ѳ ѵ), five
# reappear in the figures row, with only ѳ (fita) genuinely absent.
CATALOG_UNIVERSAL_RUSSIAN_OLD_STYLE = [
    "ыацвсзедчрфжтгб" "юінуямикьолъпѣй",
    "ЫАЦВСЗЕДЧРФЖТГБ" "ЮІНУЯМИКЬОЛЪПѢЙ",
    '1х-2Х"3э?4Э:5N.' "6%;7ш,8Ш/9щѵ§ЩѴ",
]
# Bulgarian, Universal (31C, 29C, 42C, 115C). Pre-1945 orthography, and
# the only layout here that needed BOTH yus letters distinguished.
#
# This one was held twice and resolved by accounting rather than by
# reading. The letter-inventory check first fired against the CATALOG:
# position 0 looked like a second ж, which would have duplicated a letter
# while leaving the alphabet short. It is ѫ (big yus). That fixed row 0
# but left the figures-row pair looking like ж/Ж too.
#
# What settled it: with ѫ at position 0, row 0 holds 30 distinct letters
# and no duplicates, and pre-1945 Bulgarian's 33 letters are short by
# exactly three - х, щ and ѭ. х/Х and щ/Щ are plainly in the figures row,
# leaving exactly ѭ unaccounted for and exactly one unidentified pair
# left to hold it. ѭ (iotified big yus) is visually ѫ plus the iotified
# element, which is why the two read alike at this resolution.
#
# Note ѣ (yat) is ALSO on this shuttle, at position 28, and is a plainly
# different shape - stem, top crossbar, bottom bowl. It was briefly
# proposed for position 0; that would have put yat on the wheel twice.
#
# The "I" at position 22 is a Latin I, not Cyrillic І - the alphabet is
# complete without it, so it is an extra symbol rather than a letter.
CATALOG_UNIVERSAL_BULGARIAN = [
    "ѫацвсзедчрфжтгб" "юшнуямикьолъпѣй",
    "ѪАЦВСЗЕДЧРФЖТГБ" "ЮШНУЯМИКЬОЛЪПѢЙ",
    '1х-2Х"3&?4ѭ:5§.' "6%;7Ѭ,8I/9щ(0Щ)",
]
# Chilian, Ideal (65A Small Roman, 16A Medium Roman, 46A Large Roman,
# 17A Italic, 83A Vertical Script). Three positions apart from
# CATALOG_IDEAL_SPANISH: ü/ö/ä replace ¨/ç/¡ - the same German-vowel
# substitution CATALOG_UNIVERSAL_CHILIAN makes against Universal Spanish,
# arrived at independently on the other keyboard.
CATALOG_IDEAL_CHILIAN = [
    "?zxqkjgbmpcfld," "átaherisounwyv:",
    "!ZXQKJGBMPCFLD;" "-TAHERISOUNWYV&",
    "ü%/_öä1ó2.3£4$5" "6“7”8’9(0)ñíéú¿",
]
# Polish, Universal (141 Large Roman, 30 Medium Roman, 150C Italic).
# Same structural signature as CATALOG_IDEAL_POLISH: ż takes the x key,
# and x/X move to the FIGURE shift, so row 0 contains no x. Two
# keyboards independently doing that with the same letter is a good sign
# both letter rows were read correctly.
#
# ó is the one Polish letter not cut on this shuttle; the acute at
# position 28 is the dead key for composing it.
CATALOG_UNIVERSAL_POLISH = [
    "qazwsżedcrfvtgb" "yhnujmikąolłpćś",
    "QAZWSŻEDCRFVTGB" "YHNUJMIKĄOLŁPĆŚ",
    '1x-2X"3ń?4ę:5§.' "6%;7ź,8Ź/9!(0')",
]
# Which catalogued shuttles use each layout above, and what was left out.
# Reference data for the Layout tab's help banner and for anyone adding
# the remaining variants later - not consumed as layout content itself.
CATALOG_SHUTTLES = {
    "universal_standard": (
        "23/23B Medium Roman, 24/24B Small Roman, 25/25A/25B Large Roman, "
        "158/158A Minature Roman, 180 Petite Gothic, 96 Medium Gothic, "
        "134 Large Gothic, 170 Clarendon, 68 Small Italic, "
        "169 Medium Italic, 97B Large Gothic Italic, 28 Law Italic, "
        "80 Vertical Script, 145 Multigraph (Pica)"
    ),
    "ideal_standard": (
        "10/10A/10B/94 Medium Roman, 37A Small Roman, 51/51A/3B Large "
        "Roman, 60 Gothic Italic, 118 Law Italic, 70 Vertical Script, "
        "144A Multigraph (Pica)"
    ),
    "ideal_fractions": (
        "1/48/48A Medium Roman, 2 Small Roman, 3/3A Large Roman, "
        "4 Gothic, 5 Caps and Small Caps, 6 Italic, 9 Attic"
    ),
    "universal_fractions": (
        "26 Small Roman, 40 Medium Roman (LARGE FRACTIONS), 52 Large "
        "Roman, 80A Vertical Script, 97 Large Gothic Italic"
    ),
    "universal_caps_small_caps": "27, 27E",
    # 1915 catalog, per-language Ideal shuttles
    "ideal_dutch": (
        "36A Small Roman, 11A Medium Roman, 12A Large Roman, 76A Gothic "
        "Italic, 13A/102B Italic, 91A Italic Script, 78A Vertical Script"
    ),
    "ideal_spanish": "65 Small Roman, 16 Medium Roman, 46 Large Roman",
    "ideal_spanish_cent": (
        "65B Small Roman, 16B Medium Roman, 46B Large Roman"
    ),
    "ideal_spanish_caps": "5A Caps and Small Caps",
    "ideal_croatian": "58 Medium Roman, 12C Large Roman",
    "ideal_danish_fractions": "87 Medium Roman, Fractions",
    "ideal_portuguese": "63 Medium Roman",
    "ideal_french": "61 Small Roman, 14 Medium Roman, 62 Large Roman, 15 Italic",
    "ideal_german_new_orthography": "36B Small Roman, 114 Medium Roman",
    "ideal_german": "36 Small Roman, 11 Medium Roman, 12 Large Roman (old orthography)",
    "universal_french": (
        "69 Large Roman, 32/32A Medium Roman, 67 Small Roman, 104/104A "
        "Italic, 85/111/111A Vertical Script, 134E Large Gothic, "
        "145B Multigraph (Pica)"
    ),
    "universal_french_german_english": "32E Medium Roman",
    "universal_esperanto": "135A, 135D Medium Roman",
    "ideal_roumanian": "92 Medium Roman",
    "ideal_chilian": "65A, 16A, 46A, 17A, 83A",
    "ideal_italian": "61A Small Roman, 14A Medium Roman, 62A Large Roman, 15A Italic",
    "ideal_hungarian": "152 Small Roman, 44/57 Medium Roman, 151 Large Roman, 74 Gothic Italic",
    "ideal_polish": (
        "155 Small Roman, 77/154 Medium Roman, 156 Large Roman, "
        "157 Italic, 153B Gothic, 121 Polish-German"
    ),
    "ideal_bohemian": (
        "54/86/120 Medium Roman, 153C Gothic, 154A/155A/156A Roman, "
        "157A Italic"
    ),
    "universal_portuguese": "150 Italic, 103/103A/103B Medium Roman, 159 Small Roman",
    "universal_dutch": "71A, 117B, 34A, 50A, 119B",
    "universal_german": "119A, 84, 34, 50, 71, 117, 119 (old orthography)",
    "universal_polish": "141 Large Roman, 30 Medium Roman, 150C Italic",
    "universal_bulgarian": "31C, 29C, 42C, 115C",
    "universal_russian_old_style": "29, 29A, 29B",
    "universal_dutch_fractions": "34D, 50C, 71F, 84C, 119E",
    "universal_german_new_orthography_fractions": "119C, 117D, 117E, 55F, 101E, 71E",
    "universal_bohemian": "116 Medium Roman",
    "universal_chilian": "47A Large Roman, 89A Vertical Script, 16A/17A/46A/65A/66A/33A",
    "universal_russian": "143 Large Roman",
    "universal_spanish": "33 Medium Roman, 66/66B Small Roman, 47 Large Roman, 89 Vertical Script",
    "universal_swedish_finnish": "93A Small Roman, 90 Italic, 101/101A/101B Large Roman, 134B Large Gothic",
    "universal_danish_norwegian": "55D, 90A, 93B, 101C, 134C",
    "universal_roumanian": "32C/32D Medium Roman, 97A Gothic Italic",
    "universal_italian": (
        "134F Large Gothic, 73/32B Medium Roman, 67A Small Roman, "
        "69A Large Roman, 104B/150B Italic, 85A/111B Vertical Script"
    ),
    "universal_german_new_orthography": (
        "117/117A Italic, 119C Gothic Italic, 124 Large Italic, "
        "145A Multigraph (Pica)"
    ),
    # 1915-catalog languages NOT imported yet.
    #
    # THE TEST IS CHARACTER IDENTIFICATION, NOT FONT AVAILABILITY. A
    # layout is catalogued as soon as every character can be identified
    # and has a Unicode codepoint; whether any font on this machine
    # currently carries the glyphs is a separate, solvable problem (fonts
    # can be found or made), and is NOT a reason to leave a layout out.
    # An earlier version of this list wrongly treated "no font here" as a
    # blocker - it isn't, and the non-Latin scripts below are all
    # transcribable on that basis whenever someone works through them.
    # What genuinely blocks an import is a character the scan will not
    # resolve, since a guessed glyph silently builds a wrong shuttle.
    #
    #   Held on ONE unresolved character each:
    #     Danish 88 - the figures row shows a gap at right-half position
    #       8, where its sibling 87 has "_". Blank wheel slot or an
    #       under-inked underscore? The two are indistinguishable here,
    #       and they are different characters.
    #   Not yet read (no blocker known, just unworked): Polish (156,
    #     153B, 157), Portuguese 63A/63B/106, Croatian/Danish/Portuguese
    #     siblings beyond the ones imported, and every language section on
    #     pp.10-13, 15-19 and 21-35, which have not been sampled at all.
    #   Non-Latin, transcribable, needs script care rather than a font:
    #     Russian (49, 35) and Servian (125) use pre-1918 letters, all
    #     encoded - ѣ U+0463, і U+0456, ъ U+044A, Ѳ U+0472. Greek (112C),
    #     Armenian (218, Blickensderfer) and Yiddish/Hebrew (165, 167)
    #     likewise have complete Unicode coverage.
    #   Hardest to read, regardless of script: the language-specific
    #     Vertical Script / Italic Script faces (83A Chilian, 78A Dutch,
    #     106 Portuguese, 70/91A) - ornate forms make individual accent
    #     marks hard to separate even where the layout is known.
    #
    # Catalogued but NOT imported, with the reason each one was left out.
    # These are deliberate exclusions, not an unworked backlog: where the
    # scan does not settle a character beyond doubt, no layout is better
    # than a guessed one, since a wrong glyph here silently builds a wrong
    # shuttle. Anything added later needs the same character-by-character
    # verification the imported layouts got.
    #
    #   41 Small Roman FRACTIONS - a SECOND, different fractions scheme:
    #     diagonal fractions (⅔ ⅓ ⅛ ½ ¼ ¾) rather than the stacked set
    #     above, and it keeps & in the figures row instead of moving it to
    #     the shifted "." key. Legible in outline but several fraction
    #     numerators are not separable at this scan resolution.
    #   162 Medium Gothic FRACTIONS - right half matches
    #     CATALOG_UNIVERSAL_FRACTIONS exactly, but the left half reads
    #     "...3=⅓4%?5´+" where that layout has "...3$⅓4%£5_¢"; the
    #     character after "4%" is damaged in the scan and cannot be
    #     called.
    #   184 Gothic SPECIAL FRACTIONS - prints FOUR lines, not three (an
    #     extra dense fraction bank), so it does not fit the 3-row shape
    #     at all without deciding which line is the real figures row.
    #   23E/23F/23G Medium Roman - near-standard, each differing in one
    #     or two figure slots (23E has an unidentifiable glyph where
    #     standard has "+"; 23F/23G mix single fractions into otherwise
    #     standard rows). Too close to standard to guess at.
    #   136 Caps and Small Caps SPECIAL CHEMICAL - caps rows as 27/27E,
    #     but the chemical figures row is not legible enough to call.
    #   Medical/chemical ......... 43, 43A, 107, 179, 21, 18 - purpose-made
    #     symbol sets (dose/measure/chemical marks) with no reliable
    #     Unicode reading from this scan.
    #   Diacritical/library ...... 113, 122, 48C - bare combining accents
    #     printed in isolation; which precomposed/combining codepoint each
    #     one means is a judgement call, not a reading.
    #   Literary ................. 192, 193, 194 - subscript/superscript
    #     digit banks and reference marks, ambiguous at this resolution.
    #   Non-Latin / special ...... 195 Astronomical, 196/197 International
    #     Phonetic, 135/135B/135C Mathematical, 112C Greek, 59/20 German
    #     Text (fraktur), 165/167 Yiddish (Hebrew), 185 Check Writer
    #     (perforating, prints as dot matrices) - each needs its own script
    #     expertise and, for several, a font that has the glyphs at all.
    "not_imported": "see the comment above this key",
}
# PRESET NAMING CONVENTION (both Hammond machines, keep it):
#     <Keyboard>[, <Language>][ (<Variant>)]
# A comma introduces the LANGUAGE, or the variant when there is no
# language; parentheses hold the variant once a language is already
# named. So: "Universal", "Universal, Math", "Universal, Fractions",
# "Ideal, Dutch", "Ideal, Spanish (¢)", "Ideal, Danish (Fractions)".
# Title Case throughout, on BOTH machines - hammond_split used to spell
# the same two keyboards ALL CAPS ("IDEAL, Dutch"), and hammond's first
# two presets predated the convention entirely ("Normal Universal",
# "Math Universal"). Both were normalised; no config stores a preset
# NAME, only its rows, so that rename was safe.
# v2/lib/layouts/hammond_layouts.scad's LAYOUTS[0]/LAYOUTS[2] (Normal_U/
# Math_U) - the two real presets that differ in ROW COUNT (3 vs 4), which
# no other machine's layout presets do. "Universal, Math" is the "math
# shuttle" variant - confirmed identical in v1/Hammond/HammondShuttle.scad
# (the pre-v2-migration original), nothing extra hiding there. Is_Math
# auto-derives from len(rows)==4 (lib/hammond.py's configure()), so
# selecting this preset alone is enough to switch Shuttle_Height/the Xx
# resin-support array - see LAYOUT_PRESET_BASELINE_ROW_BY_MACHINE below
# for how baseline_row/cutout_row (which ALSO need a 4th entry for this
# preset) get resized to match.
LAYOUT_PRESETS_HAMMOND = {
    "Universal": [
        "-;p.lo,kimjunhybgtvfrcdexswzaq",
        "!:P.LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0.)9°(8^'7*&6¢_5£%4+$3×#2@\"1",
    ],
    "Universal, Math": [
        "√·p.lo,kimjunhybgtvfrcdexswzaq",
        "∫:P∂LO?KIMJUNHYBGTVFRCDEXSWZAQ",
        "/=0>)9<(8|'7*÷6]Γ5[∝4+Δ3×∑2_\"1",
        "―ₙ₀πλ₉ωκ₈φε₇τη₆βγ₅θψ₄ρδ₃ξσ₂ζα₁",
    ],
    # Ideal keyboard (Hammond's own proprietary layout, NOT qwerty) - the
    # same two shuttles LAYOUT_PRESETS_HAMMOND_SPLIT carries, reversed into
    # this machine's storage order. See CATALOG_SHUTTLES for the source and
    # the shuttle numbers each one covers.
    "Ideal": [r[::-1] for r in CATALOG_IDEAL_STANDARD],
    "Ideal, Fractions": [r[::-1] for r in CATALOG_IDEAL_FRACTIONS],
    "Universal, Fractions": [r[::-1] for r in CATALOG_UNIVERSAL_FRACTIONS],
    "Universal, Caps and Small Caps": [
        r[::-1] for r in CATALOG_UNIVERSAL_CAPS_SMALL_CAPS
    ],
    # Per-language Ideal shuttles (1915 catalog)
    "Ideal, Dutch": [r[::-1] for r in CATALOG_IDEAL_DUTCH],
    "Ideal, Spanish": [r[::-1] for r in CATALOG_IDEAL_SPANISH],
    "Ideal, Spanish (¢)": [r[::-1] for r in CATALOG_IDEAL_SPANISH_CENT],
    "Ideal, Spanish (Caps and Small Caps)": [r[::-1] for r in CATALOG_IDEAL_SPANISH_CAPS],
    "Ideal, Croatian": [r[::-1] for r in CATALOG_IDEAL_CROATIAN],
    "Ideal, Danish (Fractions)": [r[::-1] for r in CATALOG_IDEAL_DANISH_FRACTIONS],
    "Ideal, Portuguese": [r[::-1] for r in CATALOG_IDEAL_PORTUGUESE],
    "Ideal, French": [r[::-1] for r in CATALOG_IDEAL_FRENCH],
    "Ideal, German (New Orthography)": [
        r[::-1] for r in CATALOG_IDEAL_GERMAN_NEW_ORTHOGRAPHY
    ],
    "Ideal, German": [r[::-1] for r in CATALOG_IDEAL_GERMAN],
    "Universal, German (New Orthography)": [
        r[::-1] for r in CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY
    ],
    "Universal, French": [r[::-1] for r in CATALOG_UNIVERSAL_FRENCH],
    "Universal, French-German-English": [
        r[::-1] for r in CATALOG_UNIVERSAL_FRENCH_GERMAN_ENGLISH
    ],
    "Universal, Esperanto": [r[::-1] for r in CATALOG_UNIVERSAL_ESPERANTO],
    "Universal, Italian": [r[::-1] for r in CATALOG_UNIVERSAL_ITALIAN],
    "Universal, Portuguese": [r[::-1] for r in CATALOG_UNIVERSAL_PORTUGUESE],
    "Universal, Roumanian": [r[::-1] for r in CATALOG_UNIVERSAL_ROUMANIAN],
    "Ideal, Roumanian": [r[::-1] for r in CATALOG_IDEAL_ROUMANIAN],
    "Universal, Spanish": [r[::-1] for r in CATALOG_UNIVERSAL_SPANISH],
    "Universal, Swedish-Finnish": [
        r[::-1] for r in CATALOG_UNIVERSAL_SWEDISH_FINNISH
    ],
    "Universal, Danish-Norwegian": [
        r[::-1] for r in CATALOG_UNIVERSAL_DANISH_NORWEGIAN
    ],
    "Ideal, Bohemian": [r[::-1] for r in CATALOG_IDEAL_BOHEMIAN],
    "Ideal, Polish": [r[::-1] for r in CATALOG_IDEAL_POLISH],
    "Ideal, Hungarian": [r[::-1] for r in CATALOG_IDEAL_HUNGARIAN],
    "Universal, Chilian": [r[::-1] for r in CATALOG_UNIVERSAL_CHILIAN],
    "Universal, Russian": [r[::-1] for r in CATALOG_UNIVERSAL_RUSSIAN],
    "Universal, Bohemian": [r[::-1] for r in CATALOG_UNIVERSAL_BOHEMIAN],
    "Ideal, Italian": [r[::-1] for r in CATALOG_IDEAL_ITALIAN],
    "Universal, Dutch (Fractions)": [
        r[::-1] for r in CATALOG_UNIVERSAL_DUTCH_FRACTIONS
    ],
    "Universal, German (New Orthography, Fractions)": [
        r[::-1] for r in CATALOG_UNIVERSAL_GERMAN_NEW_ORTHOGRAPHY_FRACTIONS
    ],
    "Universal, Dutch": [r[::-1] for r in CATALOG_UNIVERSAL_DUTCH],
    "Universal, German": [r[::-1] for r in CATALOG_UNIVERSAL_GERMAN],
    "Universal, Russian (Old Style)": [
        r[::-1] for r in CATALOG_UNIVERSAL_RUSSIAN_OLD_STYLE
    ],
    "Universal, Bulgarian": [r[::-1] for r in CATALOG_UNIVERSAL_BULGARIAN],
    "Ideal, Chilian": [r[::-1] for r in CATALOG_IDEAL_CHILIAN],
    "Universal, Polish": [r[::-1] for r in CATALOG_UNIVERSAL_POLISH],
}
