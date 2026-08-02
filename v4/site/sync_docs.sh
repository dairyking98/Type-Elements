#!/usr/bin/env bash
# Copies the real source-of-truth docs (README.md, SESSION_LOG.md,
# PACKAGING_PLAN.md, docs/*.md) into site/ with Jekyll front matter
# prepended, so the site always reflects whatever is actually in the repo
# at build time instead of a hand-duplicated copy that can drift.
set -euo pipefail
cd "$(dirname "$0")/.."  # now in v4/
SITE=site

inject() {
  local src="$1" dest="$2" title="$3"
  mkdir -p "$(dirname "$dest")"
  {
    printf -- '---\nlayout: page\ntitle: "%s"\n---\n\n' "$title"
    cat "$src"
  } > "$dest"
}

inject README.md "$SITE/readme.md" "README"
inject SESSION_LOG.md "$SITE/changelog.md" "Changelog"
inject PACKAGING_PLAN.md "$SITE/roadmap-packaging.md" "Packaging Plan"

for f in docs/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  title=$(basename "$f" .md | tr '_-' '  ')
  inject "$f" "$SITE/accessories/$base" "$title"
done

# example_renders/*.stl: one example STL per machine, published as-is so
# leonardchau.com's portfolio page can load them cross-origin instead of
# keeping its own duplicate copies.
mkdir -p "$SITE/assets/models"
for f in example_renders/*.stl; do
  [ -e "$f" ] || continue
  cp "$f" "$SITE/assets/models/$(basename "$f")"
done
