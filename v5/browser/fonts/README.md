# Bundled fonts

GNU FreeFont (FreeMono, FreeSans, FreeSerif), copied from Debian/Ubuntu's
`fonts-freefont-ttf` package (FreeSerif: the same release, from the font library). https://savannah.gnu.org/projects/freefont/

Copyright 2002-2012 GNU FreeFont contributors. Licensed GPL-3.0-or-later
**with the GNU font exception**: documents and models that embed or are made
with these fonts are not themselves covered by the GPL.

The in-browser engine uses them as defaults. A config's own font paths point
at files on someone else's computer, so wherever a font is missing in the
browser, one of these is substituted, and the app says so.

## FreeMono-ExtraLight.ttf

The default face. A lighter FreeMono derived by Leonard Chau (outline
thinning in FontForge, `~/fonts/tools/make-freemono-weight.py`, weight 200
"ExtraLight"), so it is GNU FreeFont too: GPL-3.0-or-later with the font
exception, the same as above.

## Noto Sans Mono.ttf

Hammond Split's second font, for the per sign (U+214C) - one of the few
free fonts that has it. Copyright 2022 The Noto Project Authors, SIL Open
Font License 1.1.

## Glass Antiqua.ttf

The Selectric Composer's default face. Copyright (c) 2011 Denis Masharov,
SIL Open Font License 1.1 (http://scripts.sil.org/OFL). It has no ¼ ½ ¾ -
the Composer layout's fraction slots warn as missing, as they always have.

## OCRA-TE.ttf

Stand-in for Monotype's **OCR-A II** (used by several logos and labels),
which is commercial and can't be redistributed. Built by `make_ocra.py` from
John Sauter's **public-domain** OCR-A (https://sourceforge.net/projects/ocr-a-font,
Debian's `fonts-ocr-a`), rescaled so a given size gives the same cap height and
character spacing as OCR-A II. Whenever a config names `OCR-A II Regular.ttf`,
the browser engine uses this font instead.
