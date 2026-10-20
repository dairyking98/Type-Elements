#!/usr/bin/env bash
# Copies the real source-of-truth docs (README.md, SESSION_LOG.md,
# PACKAGING_PLAN.md, LAYOUT_TRANSCRIPTION.md, CATALOG_INDEX.md,
# docs/*.md) into site/ with Jekyll front matter
# prepended, so the site always reflects whatever is actually in the repo
# at build time instead of a hand-duplicated copy that can drift.
set -euo pipefail
cd "$(dirname "$0")/.."  # now in v4/
SITE=site

# Repo-relative doc links (README.md's documentation table, and the
# cross-references the docs make to each other) are correct on GitHub but
# would 404 on the site, where each doc is published at its own pretty
# URL. Rewrite them on the way in so both work from one source.
rewrite_links() {
  sed -e 's|](PIPELINE\.md)|](/pipeline/)|g' \
      -e 's|](MACHINES\.md)|](/machines-detail/)|g' \
      -e 's|](TUNER\.md)|](/tuner/)|g' \
      -e 's|](LIMITATIONS\.md)|](/limitations/)|g' \
      -e 's|](LAYOUT_TRANSCRIPTION\.md)|](/layout-transcription/)|g' \
      -e 's|](CATALOG_INDEX\.md)|](/catalog-index/)|g' \
      -e 's|](SESSION_LOG\.md)|](/changelog/)|g' \
      -e 's|](PACKAGING_PLAN\.md)|](/roadmap-packaging/)|g' \
      -e 's|](README\.md)|](/readme/)|g' \
      -e 's|](CLAUDE\.md)|](https://github.com/dairyking98/Type-Elements/blob/main/v4/CLAUDE.md)|g' \
      -e 's|](\.\./LICENSE-DESIGNS)|](https://github.com/dairyking98/Type-Elements/blob/main/LICENSE-DESIGNS)|g' \
      -e 's|](\.\./LICENSE)|](https://github.com/dairyking98/Type-Elements/blob/main/LICENSE)|g' \
      -e 's|](\.\./NOTICE)|](https://github.com/dairyking98/Type-Elements/blob/main/NOTICE)|g' \
      -e 's|](\.\./CONTRIBUTING\.md)|](https://github.com/dairyking98/Type-Elements/blob/main/CONTRIBUTING.md)|g'
}

inject() {
  local src="$1" dest="$2" title="$3"
  mkdir -p "$(dirname "$dest")"
  {
    printf -- '---\nlayout: page\ntitle: "%s"\n---\n\n' "$title"
    rewrite_links < "$src"
  } > "$dest"
}

inject README.md "$SITE/readme.md" "README"
inject SESSION_LOG.md "$SITE/changelog.md" "Changelog"
inject PACKAGING_PLAN.md "$SITE/roadmap-packaging.md" "Packaging Plan"
inject LAYOUT_TRANSCRIPTION.md "$SITE/layout-transcription.md" "Layout Transcription"
inject CATALOG_INDEX.md "$SITE/catalog-index.md" "Catalog Index"
inject PIPELINE.md "$SITE/pipeline.md" "The Glyph Pipeline"
inject MACHINES.md "$SITE/machines-detail.md" "Machines (detail)"
inject TUNER.md "$SITE/tuner.md" "Interactive Tuner"
inject LIMITATIONS.md "$SITE/limitations.md" "Known Limitations"

# v5 (the app + engine API) keeps its own docs next to its code in ../v5/;
# published as a "v5" section. Their cross-links get the same pretty-URL
# rewrite, plus links into v5's source tree pointed at GitHub.
rewrite_v5() {
  rewrite_links | sed -e 's|](ENGINE_API\.md)|](/v5-engine-api/)|g' \
      -e 's|](docs/PERFORMANCE\.md)|](/v5-performance/)|g' \
      -e 's|](\.\./spike/RESULTS\.md)|](https://github.com/dairyking98/Type-Elements/blob/main/v5/spike/RESULTS.md)|g' \
      -e 's|](README\.md)|](/v5/)|g' \
      -e 's|](\.\./browser/README\.md)|](https://github.com/dairyking98/Type-Elements/blob/main/v5/browser/README.md)|g'
}
inject_v5() {
  local src="$1" dest="$2" title="$3"
  { printf -- '---\nlayout: page\ntitle: "%s"\n---\n\n' "$title"; rewrite_v5 < "$src"; } > "$dest"
}
inject_v5 ../v5/README.md "$SITE/v5.md" "v5: the app"
inject_v5 ../v5/ENGINE_API.md "$SITE/v5-engine-api.md" "v5 Engine API"
inject_v5 ../v5/docs/PERFORMANCE.md "$SITE/v5-performance.md" "v5 Performance"

for f in docs/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  title=$(basename "$f" .md | tr '_-' '  ')
  inject "$f" "$SITE/accessories/$base" "$title"
done

# example_renders/**/*.stl (recursive - e.g. resin_support_renders/):
# published as-is, preserving subdirectory structure, so leonardchau.com's
# portfolio page can load them cross-origin instead of keeping its own
# duplicate copies.
mkdir -p "$SITE/assets/models"
while IFS= read -r -d '' f; do
  rel="${f#example_renders/}"
  mkdir -p "$SITE/assets/models/$(dirname "$rel")"
  cp "$f" "$SITE/assets/models/$rel"
done < <(find example_renders -name '*.stl' -print0)

# example_renders/**/*.svg: generated legend cards, published the same way
# as the STLs above.
mkdir -p "$SITE/assets/legends"
while IFS= read -r -d '' f; do
  rel="${f#example_renders/}"
  mkdir -p "$SITE/assets/legends/$(dirname "$rel")"
  cp "$f" "$SITE/assets/legends/$rel"
done < <(find example_renders -name '*.svg' -print0)
