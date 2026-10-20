# Bundled fonts

GNU FreeFont (FreeMono, FreeSans), copied from Debian/Ubuntu's
`fonts-freefont-ttf` package. https://savannah.gnu.org/projects/freefont/

Copyright 2002-2012 GNU FreeFont contributors. Licensed GPL-3.0-or-later
**with the GNU font exception**: documents and models that embed or are made
with these fonts are not themselves covered by the GPL.

The in-browser engine uses them as defaults. A config's own font paths point
at files on someone else's computer, so wherever a font is missing in the
browser, one of these is substituted, and the app says so.

## OCRA-TE.ttf

Stand-in for Monotype's **OCR-A II** (used by several logos and labels),
which is commercial and can't be redistributed. Built by `make_ocra.py` from
John Sauter's **public-domain** OCR-A (https://sourceforge.net/projects/ocr-a-font,
Debian's `fonts-ocr-a`), rescaled so a given size gives the same cap height and
character spacing as OCR-A II. Whenever a config names `OCR-A II Regular.ttf`,
the browser engine uses this font instead.
