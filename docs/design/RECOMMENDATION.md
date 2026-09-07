# Design round: recommendation

Three directions were built as working HTML from the real copy and assets, screenshotted at
1440 and 390 in both themes, and scored by three independent judges (a canon keeper, a
first-time visitor on a phone, and the engineer who has to build and maintain it).

| Direction | Canon | Visitor | Engineer |
|---|---|---|---|
| **A. Sidebar, restructured** | **33** | **32** | **33** |
| B. Sidebar, conservative | 25 | 24 | 23 |
| C. Top bar, editorial | 26 | 27 | 25 |

## Sidebar or top bar

**Keep the sidebar, in A's restructured form.** All three judges reached this independently.
The honest case for the top bar is that a 240px column holding four links and a switch is
mostly empty, and on Home that is true. It stops being true the moment the column carries the
one thing the site lacks: an always-visible index of the page you are on. A's rail lists
People's sections with counts and Research's eight themes with their icons at zero vertical
cost. C's horizontal index costs a second sticky band and is already at its ceiling (it wraps
at 1440 and clips on a phone), and C spends nearly all of the brand's presence to get there.
B answers the small problems and leaves the two big ones (phone page length, navigation
unreachable at depth) where it found them.

## The base: Direction A

- The 300px topper is Home's alone. People and Research open with a ~90px masthead (mark,
  wordmark, one quiet subtitle line), so the page's own h1 is on the first screen.
- The rail holds mark, NAVIGATE (current page marked by weight and a hairline bar, Statstro
  with an external mark), DARK MODE, and ON THIS PAGE.
- On phones the rail collapses to a two-row sticky bar (mark and wordmark with the switch;
  the four links) and the index becomes an "On this page" disclosure under the h1.
- People cards on phones become a media row (photo beside name, website label and status;
  bio at the card's full width) - measured, because 2-up cards give 15-18 characters a line.
- Collaborators and Recent Alumni become compact rows.
- Roster labels are three words - MEMBERS / ASSOCIATES / COLLABORATORS - with a filled,
  open or absent square as the second channel.
- The "Personal Website" line becomes the WEBSITE label in the existing small-caps idiom.

## Grafts onto A (consolidated from the three judges)

1. **Image credit out of the prose** into a quiet caption under the figure, not italic (C).
2. **One card module for every section.** Faculty no longer renders 2-up at twice the size;
   one grid (`repeat(auto-fill, minmax(16rem, 1fr))`) so two faculty fill a row honestly.
3. **Compact row** = small photo, name as the link, then the text at the small step in a
   fixed two-column grid so rows align (B + C). No repeated "PERSONAL WEBSITE" column. With no
   new data field, the row carries the person's existing bio paragraphs at the small step;
   a one-line affiliation would need an optional field (question 1 below).
4. **Probe-line scrollspy** (a 1px line, exactly one section spans it) with an ordered
   fallback, JS-off degrading to a plain list of anchors, and `scroll-margin-top` on every
   anchor equal to the sticky height (C).
5. **Reveal the rail mark only after Home's topper has scrolled past**, so the logo is never
   drawn twice on one screen (B).
6. **A real skip link**, visible on focus - none of the three had one.
7. **Tap targets**: nav links and the switch clear 24px, 44px preferred, on phones.
8. **Use the empty column on Research**: the theme figure sits sticky beside prose and roster.
9. **Dense link runs** (rosters, compact rows): the rest underline is structure - 1px dotted
   in the quiet token - and turns solid link-colour on hover. Fixes the "wall of periwinkle".
10. **Measure** becomes `38rem` (about 68 characters of Inclusive Sans; `68ch` set ~90).
11. **Mobile Research order**: heading, prose, figure, roster - never a picture between the
    heading and the first sentence.

## Icons and favicon

Keep four and redraw four, as a set, judged at the 15px index size as well as 24/32/48:

- Keep: inference (tighten the mode tick), ai-for-scientists, galaxies (open the small
  ellipse), star-formation (firmer lobes, open core).
- Redraw: stellar-evolution (a rayed sun says "star" and is the universal light-mode glyph on
  a site with a dark-mode switch; draw small circle, arrow, large circle), milky-way (reads as
  the brand sparkle at 24px; draw an edge-on disc with a bulge or a spiral with a nucleus),
  dark-matter-cosmology (dashes dissolve at 24px; six to eight long dashes, upright),
  transients (the wifi glyph says "signal"; draw a light curve: flat, spike, decay tail).
- No fills anywhere; stroke stated once as 2px; shipped as one inline `<symbol>` sprite so
  `currentColor` works.
- Favicon: the sparkle particle. SVG for 32px and up with light/dark via
  `prefers-color-scheme`; 16 and 32 rasters hand-aligned to the pixel grid with the arms
  thickened about 15%; the 180 apple-touch and 512 manifest icons carry the particle knocked
  out of a periwinkle square so the large sizes still say ART.

## Canon amendments owed in the implementing commit

measure as a length; three-word roster labels; the open mark's 1.5px border named among the
permitted borders; the compact row may carry a thumbnail; icon stroke 2px and no fill; the
mobile collapse stated as a condition (two-row bar while there are four destinations, a Menu
control at five); wash and mark never share a screen (settled: keep both tokens); the quiet
underline for dense link runs; the mobile Research order; image credit as a quiet caption.

## Data model

Every person gets a stable `id` (already being added). Two faculty get a `short` display name
for rosters. Sections get a semantic `layout` (faculty / cards / compact) instead of grid
classes. Research moves to `data/research.json` with rosters by id, so the People and
Research pages cannot drift. No `role` field, per the owner's ruling.

## Implementation order, riskiest first

1. Shell: rewrite `ejs/main.ejs` around the rail, masthead vs topper, mobile bar, the inline
   pre-paint theme script, and drop Foundation JS and jQuery (CSS `position: sticky`).
2. Styles: tokens from DESIGN.md into SCSS; rebuild `index.scss` without Foundation.
3. Renderers: compact rows, card and section ids, ON THIS PAGE data, icon sprite hooks.
4. Icons redrawn, favicon set, social image, meta tags.
5. Copy pass, then verification with before/after screenshots.

## Questions for the owner

1. Compact rows: keep each person's full bio at small type (no data change, my default), or a
   one-line affiliation (adds an optional `line` field to those entries only)?
2. Keep the 300px topper on Home only, with the inner pages opening on the compact masthead?
3. Keep the counts beside section headings and in the index ("Faculty 2")?
4. Any of the four icon redraw ideas you would veto?
5. Large app icons as the sparkle in a periwinkle square: fine?
