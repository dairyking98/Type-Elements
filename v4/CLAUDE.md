# v4 conventions

## tune.py: tooltip/help-text `Static` widgets

Any `Static` whose content is user-facing help/tooltip text (the
`.field-help`, `.picker-help`, and `.advanced-warning` CSS classes in
`TuneApp.CSS`, and any new class serving the same purpose) must follow
both rules below. Violating either reproduces the bug fixed in
`SESSION_LOG.md` part 22 (text clipped, or clipped input fields below
it).

1. **`height: auto` in the CSS class, never a fixed row count.** A
   fixed `height: N` clips any message longer than `N` lines instead of
   wrapping it. The containing `Vertical(classes="field-row")` (or
   equivalent) must also be `height: auto` (with `margin-bottom: 1` to
   keep the visual spacing that a fixed height used to provide) so it
   grows with its help text instead of clipping it.
2. **No manual `\n` line breaks in the string.** Write the text as one
   flowing string (ordinary adjacent-string-literal concatenation
   across source lines is fine). Textual wraps `Static` content to the
   widget's actual width automatically - a hand-inserted `\n` at some
   guessed width gets wrapped *again* on top of that, roughly doubling
   the rendered line count and pushing whatever is below it down the
   tab. (Manual `\n` is still correct where you're building literal
   file content, e.g. the YAML/txt headers in `save_config()` - this
   rule is only for text a `Static` renders in the TUI.)

Keep the wording itself short: 1-2 sentences, no fluff, no unnecessary
internal/source cross-references. Longer banners (`SECTION_INTROS`,
the Layout/Build/Type Test tab intros) should still fit in well under
10 rendered lines - if a description needs more than that, it likely
belongs in `README.md`/`SESSION_LOG.md` instead of a tab banner.
