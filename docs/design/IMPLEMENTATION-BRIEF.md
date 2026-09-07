# Brief: rebuild the shell, styles and scripts of astrostatuoft.com to Direction A

You are implementing the winning design direction in the real webpack stack. Everything below
is decided; do not re-open decisions. Where this brief is silent, the canon (DESIGN.md) rules;
where the canon is silent, the mockup (design/A-sidebar-restructured/mockup.html and its
generator parts_css.py / parts_html.py) is the reference; where both are silent, pick the
quieter option.

Read, in order: CONTEXT.md; the repo's CLAUDE.md; design/DESIGN.md (the canon);
design/RECOMMENDATION.md (base + grafts + canon amendments); the A mockup's NOTES.md and
parts_css.py; audit/FINDINGS.md for the ids cited below; impl/*/NOTES.md from round 1 (what
already changed: ids, research.json, renderers, fonts, CI).

## Outcome

Three pages that look like the A mockup with the grafts applied, in both themes, from 360px to
1600px, built by `npm run build` with no Foundation and no jQuery in the bundle, passing
`python3 docs/check_tokens.py`, `python3 scripts/audit_site.py`, `python3 scripts/test_audit.py`
and an axe scan with no violations, and documented in docs/DESIGN.md and CLAUDE.md.

## Decisions

### Shell (ejs/main.ejs)
- Landmarks: `<header>` (hero on Home, masthead elsewhere), `<nav aria-label="Site">`,
  `<nav aria-label="On this page">` (only on People and Research), `<main id="main">`,
  `<footer>` on every page carrying the site note (affiliations, credit, "Last updated
  {{LAST_UPDATED}}") - move it out of ejs/pages/home/body.html (F077, F070).
- First element in body: a skip link to #main, visually hidden until focused, then visible
  in the link token on the card surface (F006).
- Breadcrumbs are removed entirely (F038, F017, F050, F073): delete ejs/pages/*/crumbs.html and
  the crumbs partial wiring. The current page is marked in the site nav instead.
- The ART mark is inlined ONCE per page as an `<svg><symbol id="art-mark">` (path from
  static/art-logo-mod.svg with its fill attribute stripped; move the file to svg/art-mark.svg
  and delete static/art-logo.svg and static/art-logo-mod.svg) and referenced with `<use>`
  wherever it is drawn (F014). The rail mark is drawn positive in the mark token, no
  knockout rectangle, no mask (F057).
- Home only (pages config gets `hero: true`): the topper = the mark in the wash token as the
  backdrop with the wordmark as real HTML text over it - "Astrostat@UofT" at the display step,
  then "Astrostatistics Research Team" and "University of Toronto" - not SVG `<text>` (F008).
  It scales down on phones (the mark ~120px, text at the h1/body steps) and never prints the
  mark through the type illegibly. It is not a heading element; the page keeps its own h1.
- People and Research: a compact masthead (~90px): small mark + "Astrostat@UofT" in Urbanist
  Bold + a quiet one-line subtitle "Astrostatistics Research Team · University of Toronto".
- The rail (medium and up, `position: sticky`, no JS): mark; NAVIGATE label; Home / People /
  Research / Statstro (Statstro carries the external arrow glyph and an accessible name
  "Statstro (external site)"); the current page in ink, bold, with a hairline quiet bar on the
  leading edge; DARK MODE label + switch; then ON THIS PAGE label + the index for the current
  page (People: section names with counts; Research: theme names with their icons). The rail
  mark on Home is hidden while the hero is in view (IntersectionObserver) and shown after
  (graft 5); with JS off it is simply shown.
- Narrow widths (< 768px): the rail becomes a two-row sticky bar - row 1: mark, wordmark,
  DARK MODE switch; row 2: the four destinations. Nav links ≥ 44px tall tap targets (F033).
  The index becomes a `<details>` "On this page" disclosure directly under the h1.
- Scrollspy: a 1px probe line (graft 4); exactly one section current; ordered fallback;
  the current index item is ink + bold; on the mobile disclosure the current item scrolls
  into view. Every section anchor has `scroll-margin-top` equal to the sticky height. JS off:
  the index is a plain list of working anchors.
- Theme: an inline script in `<head>` before the stylesheet sets `data-theme` from
  `localStorage.theme` if present, else from `prefers-color-scheme` (F015, F005); the switch
  writes `localStorage.theme`; when nothing is stored, a media-query listener follows OS
  changes (F074). `data-theme` is not hard-coded in the HTML. Also emit
  `<meta name="color-scheme" content="light dark">`.
- The switch: a `<button role="switch" aria-checked>` (or the checkbox pattern) with the
  visible DARK MODE text as its label; track quiet (off) / link (on), paddle = page surface;
  ≥ 24px tall; focus ring per canon (F046, F048). No `label for` pointing at a `<ul>` (F049).
- Head: per-page `<meta name="description">` (from the pages config - write three good
  ones), `<link rel="canonical">` to https://astrostatuoft.com/<page>, Open Graph and Twitter
  card tags with og:image = /static/og-image.png (1200x630; copy from design/icons-v2/ when
  it exists, else leave the tag pointing at the path and note it), favicon set (favicon.svg,
  favicon.ico, apple-touch-icon.png, site.webmanifest from design/icons-v2/ if present),
  `theme-color` for both schemes. Remove `x-ua-compatible` and the `no-js` class (F088, F086).
- Research pages inline the theme icon sprite (svg/themes-sprite.svg, from design/icons-v2/
  if present, else design/icons/) once and reference `<use href="#icon-<theme id>">` beside
  each h2 and in the index. Icons inherit `currentColor`.
- Also emit dist/404.html (same shell, "Page not found", links to the three pages),
  dist/robots.txt and dist/sitemap.xml (F066) - from webpack (HtmlWebpackPlugin instance +
  a small generator), never hand-committed.

### Styles (scss/)
- Delete Foundation from the build: no `fdn` alias, no `foundation-sites` import, no
  `foundation-*` mixins; remove foundation-sites and jquery from package.json (npm uninstall,
  regenerate the lockfile). Write our own small SCSS: `_tokens.scss` (the palette as an SCSS
  map, ONE place for every hex; light on `:root`, dark under `[data-theme="dark"]`, and a
  `prefers-color-scheme: dark` block guarded by `:root:not([data-theme="light"])` for no-JS),
  `_reset.scss` (minimal), `_type.scss` (the seven clamp steps, label idiom, measure 38rem -
  canon amendment), `_layout.scss` (rail + main grid at 1200px, spacing scale variables),
  `_components.scss` (hero, masthead, nav, switch, index, card, compact row, roster, figure,
  footer, skip link), `_print.scss` (hide the rail, switch and index; keep content).
- docs/check_tokens.py must read the hex values FROM scss/_tokens.scss (parse the map), so
  the palette lives once; adapt the draft in design/check_tokens.py. It exits 1 on any pair
  under its floor. Add it to .github/workflows/build-check.yaml as a step.
- Cards: one module for every section (graft 2): grid `repeat(auto-fill, minmax(16rem, 1fr))`;
  contents in order photo (square, `aspect-ratio: 1/1`, width/height attrs, lazy), name (h3),
  WEBSITE label line (the small-caps idiom; render-people.js already marks link-only
  paragraphs with `.person-link` - restyle, do not change the data), status note (bold),
  bio. Below 560px the card is a media row: 88px photo beside name/WEBSITE/status, bio at full
  width (F002). Cards in a row square off at the bottom WITHOUT a global `.grid-x > .cell`
  rule (F001).
- Compact row (layout "compact": Collaborators, Recent Alumni): 56px square photo (only if
  the section has photos for everyone; render-people.js can check), the name as the link to
  their site when the first paragraph is a link-only paragraph, then the remaining bio
  paragraphs at the small step. One row per person, single column, card surface, step 2
  vertical padding, no rules between rows (owner ruling: no new data field; the full bio
  stays).
- Roster block: labels MEMBERS / ASSOCIATES / COLLABORATORS with the filled / open (1.5px
  border) / none square before the label; label column 11.5rem at medium+, stacked on small;
  names link to /people.html#<id>; in dense link runs (roster names, compact rows) the rest
  underline is 1px dotted in the quiet token and hover is 1px solid link (canon amendment).
- Research theme: h2 with icon; prose at the measure; the figure (image + quiet caption with
  the credit, not italic) sits in the right column and is `position: sticky` beside prose and
  roster at large widths (graft 8); on phones the order is h2, prose, figure, roster (graft 11).
- Links: dotted rest / solid hover in the link token, no colour.mix (canon). Focus ring 2px
  link at 2px offset everywhere. Radius 0, shadow none, borders only as the canon lists.
- No image-placeholder fill (teal is retired, F042); an `<img>` without a src is not emitted -
  render-people.js emits a `<div class="no-photo" aria-hidden="true">` on the card surface for
  `image: null` (F004) and the alt convention stays on real photos.
- Caption/footer/subtitle use the quiet token (F007). Every text size is one of the seven
  steps (F044); every length is on the spacing scale.

### Scripts (js/index.js)
Vanilla ES2015+, no dependencies: theme switch + persistence + OS listener; scrollspy;
rail-mark reveal on Home; that is all. Keep the file small and commented. webpack keeps
babel-loader only if a config exists; otherwise drop it.

### Renderers (build/)
- render-people.js: returns `{ body, index: [{ id, title, count }] }`; layouts faculty/cards
  → cards module, compact → compact rows; ids on sections and cards (already there); the
  `.no-photo` element; the WEBSITE label line; escape name/alt/heading.
- render-research.js: returns `{ body, index: [{ id, title, icon }] }`; markup per the above
  (figure with figcaption credit; roster rows with role classes `members|associates|
  collaborators`; names linking to people.html#id).
- webpack.config.js: pages carry `title`, `description`, `hero`, `render` (or `body`
  partial), `index`; main.ejs receives `page`, `body`, `index`, `lastUpdated`, `sprite`,
  `mark`. Remove the crumbs partials. Keep publicPath '/', no `base`.

### Docs
- Move design/DESIGN.md to docs/DESIGN.md with the canon amendments from RECOMMENDATION.md
  applied (measure 38rem; three-word labels; the open mark's border named; compact row may
  carry a thumbnail; icon stroke 2 / no fill; mobile collapse as a condition; wash and mark
  never on one screen; quiet underline for dense link runs; mobile Research order; credit as
  quiet caption). Record what the mockup round settled in a short "Settled" section and empty
  "Pending".
- CLAUDE.md: rewrite the Styling section (tokens, no Foundation, theme persistence now true,
  check_tokens.py), the architecture table (no crumbs, hero flag, index), the People/Research
  sections if round 1 has not already, and the audit list. Update the skill's mentions of
  Foundation grid classes / crumbs. Update README if it mentions Foundation.

## Verification before you return
1. `npm run build` clean; `ls -la dist/assets` and report bundle sizes before/after (JS was
   218 KB, CSS 53 KB).
2. `grep -ril "foundation\|jquery" dist/` returns nothing.
3. `python3 docs/check_tokens.py`, `python3 scripts/audit_site.py --strict`,
   `python3 scripts/test_audit.py` all pass.
4. Serve dist/ and screenshot all four pages (index, people, research, 404) at 390, 768 and
   1440 in both themes, full-page and fold, into impl/design/shots/. LOOK at every one and
   compare against the A mockup shots; fix what differs for the worse. Iterate at least
   three rounds.
5. In Playwright: toggle the theme on index, navigate to people - it sticks; reload - it
   sticks; with `localStorage` cleared, `color_scheme='light'` renders light on first paint
   (block the JS bundle and check `document.documentElement.dataset.theme` and the body
   background). Tab from the top: skip link visible, then nav, then switch (Space toggles);
   every focused element shows the ring. Fragment links (#recent-alumni, #galaxies) land with
   the heading fully visible below the sticky bar at 390 and 1440. No horizontal overflow at
   320/360/390/768. All `<img>` have naturalWidth > 0 except none (there should be no broken
   image glyph anywhere).
6. axe-core (npm i axe-core in a scratch dir, inject) on all three pages in both themes:
   zero violations; html-validate clean.
7. Write impl/design/NOTES.md: what changed file by file, the measurements above, and
   anything you deliberately deviated from the brief with the reason.

## Owner rulings (7 Sep, after the gallery)
- Compact rows carry the full bio at the small step. No new field.
- Topper on Home only; People and Research open on the compact masthead.
- Counts appear in the "On this page" index only, not beside section headings.
- App icons (180 apple-touch, 512 manifest): the FULL ART mark on a page-surface (white)
  tile, tight-cropped to the path's bounding box, centred, filling ~86% of the tile width.
  Not the sparkle-in-a-square. The small favicon stays the bare sparkle.
- Adopt the responsive panorama markup from impl/images/NOTES.md (srcset/sizes/width/height,
  lazy) for the two home-page group photos, re-deriving `sizes` from the new layout's actual
  column widths; then delete the full-resolution originals only if nothing references them.
- Round 1 hand-offs from impl/research-data/NOTES.md apply: give `.theme-figure` its own
  margin; drop the `:nth-child(odd)` alternation in favour of one fixed image side; anchors get
  `scroll-margin-top`; the Collaborators section is now `layout: compact` (design it as such).
