# Direction B — Sidebar, conservative

## The direction in three sentences

B keeps every structural decision the site already made — the left sidebar, the breadcrumb bar,
the topper on all three pages, the flat grey card, the dotted link — and changes only what is
measurably broken: the 300px topper becomes a 168px masthead carrying an eighth of the colour ink,
the sidebar becomes a compact horizontal strip on phones instead of eating the first screen, the
theme switch is rebuilt so it actually renders, and both long pages gain a horizontal index of
section chips under the `h1` that sticks under the breadcrumb bar once you scroll past it. Nothing
moves that a returning visitor would have to re-learn; the page is the same page, drawn properly.
It is the restraint case, offered so the judges can see how much of the audit's complaint list can
be answered without restructuring anything.

## Files

- `mockup.html` — the deliverable, 1.14 MB, fully self-contained (only `data:` URIs; no `<link>`,
  no `@import`, no network reference of any kind).
- `build.py`, `parts_css.py`, `parts_icons.py` — the generator, kept so the copy can be re-pulled
  from `data/people.json` and `ejs/pages/research/body.html` rather than hand-transcribed.
- `shoot.py` — the screenshot harness. `shots/` — the 20 PNGs.

## Every decision, and why

### The topper

**Decision.** 300px full-bleed hero → a 168px masthead: the ART mark at 104px on the left, the
three wordmark lines set left beside it, everything else white space.

**Why.** The topper repeats identically on all three pages and carries nothing after the first
visit, so it was the largest area of pure decoration on the site. Cutting it in half is the single
biggest win available without moving anything. Making the wash a *contained glyph* rather than a
full-width wash behind the type is what reduces the colour ink: the bounding box of the pale
periwinkle goes from ~160,000 px² to ~19,200 px², a factor of 8.4, while the token itself stays at
full strength — the canon forbids weakening a token with alpha, so the reduction has to come from
area, not opacity. Left-aligning the wordmark turns a centred hero into a nameplate, which is what
a masthead is.

**Measured.** Topper height 168px at 1440 and 1600; 101px at 390; 123px at 360 (the wordmark takes
a second line there). Target was 160–180 desktop, "proportionally less" on phones.

**Cost, stated.** The `display` type step had to be retuned — `clamp(1.6rem, 1.1rem + 1.6vw,
2.5rem)` instead of DESIGN.md's `clamp(2.5rem, 1.5rem + 5vw, 5rem)`. The step's *role* is unchanged
(the topper wordmark, and nothing else), only its value. A 96px wordmark cannot live in a 168px
band. DESIGN.md's number was written for the hero and should be replaced by this one.

### The sidebar stays where it is

**Decision.** Left column, 11rem, sticky at `top: var(--s4)`, in this order: mark, NAVIGATE, four
destinations, theme toggle. Identical on all three pages.

**Why.** It is the thing the owner likes, it is cheap (176px of a 1200px shell), and it is the only
element that keeps navigation reachable at any scroll depth without a second sticky bar. Direction A
or C can argue for a top bar; B's job is to show that the sidebar is not what is wrong with the site.

**Current page** is marked three ways, per the canon's "hue is never the only channel": ink instead
of link, bold, and a 1px quiet hairline on the leading edge. The underline is dropped on the current
item, because it is not a destination.

**Statstro** carries the external mark — a 0.68em arrow in `currentColor` after the word. It is the
only external item in the navigation and the only place on the site that mark appears.

### The sidebar mark is drawn positive, not knocked out

Today it is a solid `mark`-coloured block with the logo knocked out of it. That is a 40×40 patch of
saturated navy repeated on every page. Drawn positive — the path itself in `mark` on the page
surface — it says the same thing with about a fifth of the ink. Same drawing, less of it.

### The mobile sidebar becomes a strip

**Decision.** Below 900px the sidebar becomes a horizontal strip pinned at `top: 0`: mark at the
left, the theme toggle at the right, the four nav links in a row. Below 480px the links drop to a
second line inside the strip (44px → 73px tall).

**Why.** Today the nav and toggle consume the entire first screen on a phone; the visitor's first
sight of the site is a menu. The strip is 73px at 390 and the first screen now shows the `h1`, the
whole lede and the top of the group photo (see `fold-home-mobile-dark.png` against
`baseline/index-mobile-light-fold.png`).

**Deviation from DESIGN.md, declared.** The canon says that at small widths navigation "collapses to
one control named *Menu*". It does not here. Four short destinations fit in one or two rows; a Menu
button would hide all four behind a tap and add a state to manage, and would buy back only ~30px.
If the site ever grows a fifth and sixth destination, the canon's rule is the right one and this
should revert.

### The in-page index

**Decision.** A horizontal row of chips directly under the `h1`, before the intro paragraph. People:
section name + count. Research: theme icon + theme name. It sticks under the breadcrumb bar
(`top: var(--crumb-h)`) once scrolled past. Current section is ink and bold, everything else is a
dotted link — the same current-item convention as the sidebar, so the reader learns it once.
The highlight is driven by an `IntersectionObserver` with `rootMargin: -96px 0 -55% 0`, taking the
topmost intersecting section; on phones the observer also scrolls the current chip into view inside
the row.

**Why here and not in the sidebar.** The sidebar is 176px wide; "Undergraduate Students 1" does not
fit in it, and a vertical index there would push the theme toggle below the fold. Under the `h1` the
row gets the full content width, it is read in the same left-to-right sweep as the page title, and
it needs no second sticky column.

**Home has no index.** One `h1`, one `h2`, two figures. An index of two items is a legend for a
thing that needs none, and the canon's navigation rule already says the index belongs to "the two
long pages".

**Measured cost.** At 1440 the seven People chips and the eight Research chips both wrap to two
lines, so the sticky stack is 40px (crumbs) + 76px (index) = 116px, 12.9% of a 900px viewport. On a
phone the index becomes a single scrolling line: 73px (strip) + 40px (index) = 113px, 13.4% of 844.
Between 700 and 899px the index wraps rather than scrolls, because there is room.

**Crumbs keep their bar but lose their rule** where an index follows, so the two sticky bars read as
one block with one hairline at the bottom rather than two stacked rules.

### People

- **Cards unchanged in structure**: photo, name, `PERSONAL WEBSITE` label line, status note, bio.
  No role line, no new field in `people.json`. Binding ruling, obeyed.
- **One card width across the page.** Faculty's 2-up grid is capped at 42rem, so a faculty card is
  ~324px and a postdoc card ~307px instead of 472px and 307px. Two people should not be drawn twice
  the size of the next two; the old 2-up grid made the faculty photographs the largest images on the
  site after the group photo.
- **Collaborators and Recent Alumni are compact rows** (approved ruling): no photo, one line each,
  name then affiliation, on the card surface, step-2 vertical padding, separated by space and never
  by a rule. Name and affiliation sit in a two-column grid (16rem / 18rem) so six rows align — the
  same fixed-label-column idiom the roster block already uses. On phones they stack, with the
  affiliation in `quiet` at `small`.
- **The role mark is *not* reused here.** The filled/open/none square means member vs associate vs
  collaborator *within a theme roster*. Collaborators on People is a section heading, not a role
  contrast, and giving the mark a second home would be the token reassignment the canon forbids.
- **2-up on phones**, as briefed. See the self-critique.

### Research

- **An icon beside each theme `h2`**, and the same icon in the chip. Drawn inline before the word,
  not hung in the margin: hanging it would put a 44px overhang into the sidebar gutter, which is
  24px wide. The `h2` therefore starts ~44px right of the prose. That is a real misalignment and it
  is the price of the icon being *beside its word* rather than floating.
- **One image side, not alternating.** The image is right, the prose left, at every theme; on
  phones the image goes above the prose. Alternation is a variation that carries no information:
  with eight themes it makes the reader re-find where the prose begins eight times, and the canon's
  own rule — a channel that distinguishes nothing should not be spent — applies to layout as much
  as to hue. Fixed on the right keeps `h2`, prose and roster on one left edge.
- **Roster block with marks.** Card surface, three rows, label in a fixed 11.5rem left column, a
  0.6em square before each label: filled (members) / open (associates) / absent (collaborators) —
  fill expressing an order that hue cannot. The words never go away. The mark sits in its own grid
  column so a label that wraps to two lines still aligns under itself.
- **The real labels wrap.** "ART associates involved:" does not fit 11.5rem at the label size, so
  every roster label sets on two lines. It reads fine at 1.35 leading, but DESIGN.md's 11.5rem was
  written assuming the shorter MEMBERS / ASSOCIATES / COLLABORATORS wording. Either the copy
  shortens or the column widens to 13.5rem; the canon should say which.

### The theme toggle

Rebuilt as a `<button role="switch" aria-checked>` carrying its state three ways, per canon: paddle
position, track colour (`quiet` off, `link` on) and a visible "Dark mode" text label that is also
its accessible name. Square, no radius, paddle in the page surface. All three switches in the
mockup are driven from one handler and stay in sync — the same code that would sync a switch across
a page load from `localStorage`.

### Colour

Every pair drawn in this mockup is one of the pairs DESIGN.md already declares and measures. No new
pair was introduced, and no token was given a second role. Specifically: `wash` appears only as the
topper glyph fill; `mark` only as the sidebar glyph; `quiet` as captions, the site note, the nav and
toggle labels, chip counts, the crumb separator, the divider hairlines and the toggle's off-track;
`ink` as body text, headings, roster names and the roster's role marks; `link` as every interactive
text and the focus ring.

## The token table used

| Token | Light | Dark | Role as drawn here |
|---|---|---|---|
| `--page` | `#fefefe` | `#0a0a0a` | Page surface; the sticky bars' ground; the toggle paddle. |
| `--card` | `#eeeeee` | `#333333` | People card, compact-row block, roster block. |
| `--wash` | `#91acde` | `#2f559d` | The topper glyph. Nothing else. |
| `--ink` | `#0a0a0a` | `#fefefe` | Body, headings, names, affiliations, roster marks, current nav/chip. |
| `--link` | `#2f559d` | `#91acde` | Links, nav, chips, focus ring, toggle on-track. |
| `--mark` | `#001f4e` | `#70a9ff` | The sidebar ART glyph. |
| `--quiet` | `#6b6b6b` | `#9b9b9b` | Captions, site note, labels, counts, hairlines, toggle off-track. |

Spacing, nine steps on a 4px base: `0.25 0.5 0.75 1 1.5 2 3 4.5 7` rem as `--s1`…`--s9`. Card
padding step 3; compact row step 2; section rhythm step 7 above an `h2`, step 4 below; grid gutters
step 5 at medium and up, step 4 below; shell gutter step 4.

Type, seven fluid steps, all `clamp()`:

| Step | Value | Used for |
|---|---|---|
| display | `clamp(1.6rem, 1.1rem + 1.6vw, 2.5rem)` **(retuned)** | The masthead wordmark's first line. |
| h1 | `clamp(2rem, 1.4rem + 2.6vw, 3rem)` | One per page. |
| h2 | `clamp(1.5rem, 1.2rem + 1.4vw, 2rem)` | Sections; themes. |
| h3 | `clamp(1.2rem, 1.08rem + .55vw, 1.45rem)` | A person's name; the masthead's second line. |
| body | `clamp(1rem, .94rem + .28vw, 1.125rem)` | Prose, bios, roster names, affiliations. |
| small | `clamp(.875rem, .85rem + .12vw, .94rem)` | Captions, site note, crumbs, masthead line 3. |
| label | `0.85rem` bold, `+0.04em`, uppercase | NAVIGATE, DARK MODE, PERSONAL WEBSITE, chips, roster labels. |

Measure capped at 68ch on every run of prose. Content shell 1200px. Radius 0, shadow none
everywhere; the only borders are the link underline, the focus ring and the hairlines.

## The eight theme icons

Drawn as a set in one sitting on a 24px grid, 2px stroke, round caps and joins, no fill,
`currentColor`, one idea per glyph:

| Theme | Glyph | Idea |
|---|---|---|
| Inference | interval with a centre dot | an estimate and its uncertainty |
| Stellar Evolution | small circle → arrow → large circle | a star's life |
| Dark Matter & Cosmology | dashed ring around a solid circle | a halo around what you can see |
| AI for Scientists | five nodes, four edges | a network |
| The Milky Way | spiral with a nucleus | a spiral galaxy, ours |
| Galaxies | two tilted ellipses and a dot | several galaxies |
| Transients | a spike with a decay tail | a light curve |
| Star Formation | a cloud with a circle inside | a star forming in a cloud |

Inference was drawn twice. The first attempt was a bell curve; in a chip row at 15px it and the
Transients light curve both read as "∧", which is a set-level failure — two of eight glyphs the
index cannot tell apart. Redrawing Inference as an interval fixed it. That is the canon's own rule
about a ninth glyph drawn later: a set is judged as a set, not glyph by glyph.

## What I would change in the real SCSS / EJS / JS

**SCSS.**
1. New `scss/_tokens.scss`: the seven colours per theme, nine spacing steps, seven type steps, the
   measure and the shell width, as CSS custom properties on `:root` and `html[data-theme="dark"]`.
   Every other partial reads them; no hex value survives outside this file (and `docs/check_tokens.py`
   is the only other place values are written down).
2. `_lightmode.scss` / `_darkmode.scss` shrink to the two token blocks. Everything else in them is
   already expressible as a token reference.
3. `_global.scss` gets the link rule (dotted → solid), the focus ring, the `.label` idiom, the card,
   the compact row, the roster block, the chips and the strip. Foundation's grid can stay for the
   cards; the sidebar/content split should become a two-column CSS grid so the sticky sidebar does
   not need Foundation's `data-sticky`.
4. Delete the `.switch` Foundation styles and write the toggle from scratch as above — the broken
   mobile switch is a Foundation-styling problem, not a markup one.

**EJS / `webpack.config.js`.**
5. `main.ejs`: the topper becomes the masthead markup (mark + three wordmark lines) instead of two
   stacked SVGs with `<text>` in them — the wordmark should be real text, not SVG text, so it
   inherits the type scale and is selectable and translatable.
6. `main.ejs`: give the page shell an `index` slot between the crumb bar and the body, and pass
   `pageKey` so the nav can set `aria-current="page"` at build time instead of by URL guessing.
7. `build/render-people.js`: emit `id`/`data-section` on each section and a chip row from the
   section list, with counts taken from `people.people.length` — the count then cannot drift from
   the roster. Emit the compact-row form when a section declares `"form": "rows"` in
   `people.json`, which is the one new key this direction needs (no `role` field, per the ruling).
   Compact rows need a short affiliation; take it from the bio's first sentence up to the first
   period rather than adding a field, and let a section opt out.
8. Move the Research page to data (`data/research.json`: theme, icon key, prose, image, three
   roster lists) and render it the way People is rendered. Eight themes × three roster rows is
   exactly the kind of repetition that should not be hand-maintained HTML, and `theme_fit.py` and
   `sort_themes.py` would then read data instead of regexing markup.
9. Icons ship as one `<symbol>` sprite inlined in `main.ejs` and referenced by `<use>`; the theme
   key in the data picks the symbol.

**JS.**
10. `js/index.js`: read the stored theme *before paint* via a tiny inline script in `<head>` so the
    site stops flashing the wrong theme, keep `localStorage`, and set `aria-checked` on the switch.
11. Add the ~25-line `IntersectionObserver` from this mockup for the index highlight, guarded on
    the element existing so Home pays nothing.
12. Drop Foundation's `data-sticky` and `drilldown` JS; `position: sticky` and a plain `<ul>` do
    both jobs, and that removes the dependency on jQuery for the whole nav.

## Honest self-critique

1. **2-up cards on a phone buy less than they look like they buy.** Measured on the eight postdoc
   cards at 390px: 4,671px 2-up against 6,498px 1-up — 28%, not the 50% the halved photo suggests.
   The photo shrinks from 358px to 171px, but the bio's measure drops to about 18 characters and the
   line count nearly doubles, giving most of it back. The honest fix for the length of the People
   page is not the grid, it is the bios: a 120-word bio is a 30-line column at that width. A
   horizontal card on phones — 96px photo at the left, text at the right, one per row — would keep a
   readable measure *and* beat both numbers; I did not build it because the brief specified 2-up.
   Someone should measure it before this ships.
2. **Two sticky bars is one more than I would like.** 116px on desktop and 113px on a phone is a
   real tax on a 844px screen, and it is the direct cost of "keep the breadcrumb bar" plus "add an
   index". The crumbs are two items and duplicate the sidebar; if they were dropped or merged into
   the index row, the tax halves. B keeps them because the brief said keep them, but if the judges
   are weighing B against a direction that drops the crumb bar, this is the line item to compare.
3. **The index does not scale past what it holds now.** Seven People chips wrap to two lines at
   1440 and eight Research chips do the same; a ninth theme or an eighth People section pushes
   toward three. On a phone the row scrolls sideways, which is conventional but does hide items with
   no affordance beyond the cut edge — the observer scrolling the current chip into view is what
   makes it usable, and a visitor who does not scroll never learns there are seven sections.
4. **The `h2` icon breaks the left edge on Research.** Inline placement indents every theme title
   ~44px past the prose and roster below it. Hanging the icon in the margin fixes the edge and
   collides with a 24px gutter. Neither is right; the real answer is probably a wider gutter, which
   is a layout change B is not allowed to make.
5. **Two ART marks stack in the top-left corner** — the masthead glyph in `wash` and the sidebar
   glyph in `mark`, about 60px apart. They are different tokens doing different jobs (decoration
   vs. the persistent brand anchor while scrolled) and they read as different things, but it is the
   one place where B looks like it is repeating itself. Revealing the sidebar mark only once the
   topper has scrolled past would solve it and costs one more observer.
6. **This is the minimum-change case and it inherits the content problems.** "Personal Website" is
   still the first line of every card fifty times over; the bios are still wildly uneven in length,
   which is what makes the cards square off with big empty grey feet; the Research prose is still a
   single 200-word paragraph per theme with no internal structure. None of that is a layout problem
   and none of it is fixed here.
7. **The mockup renders four of seven People sections and eight of nine postdocs.** Tanveer Karim
   has no headshot in the asset pack, and Graduate Students / Undergraduate Students / ART Associates
   are not built. The chip rows deliberately carry the *real* site counts (2 / 9 / 7 / 1 / 8 / 14 / 9)
   so the row's true width and wrapping can be judged; the three chips whose sections are not built
   scroll to the top of the People screen instead of to a section. Everything else — prose, bios,
   roster names, links, captions — is verbatim from `data/people.json`,
   `ejs/pages/home/body.html` and `ejs/pages/research/body.html`. The affiliations in the compact
   rows are condensed from the real bios, and the Recent Alumni destinations likewise; those two are
   the only strings on the page I wrote rather than copied.
8. **Not tested:** real screen readers, Safari (`position: sticky` inside a CSS grid item and
   `word-break: keep-all` both behave slightly differently there), forced-colours mode, and
   `prefers-reduced-motion` beyond disabling the two transitions.

## Verification actually run

- 20 screenshots: 2 themes × 2 viewports × (1 full page + 3 screen tops + 1 mid-People fold). Every
  one was looked at; three rounds of fixes came out of them (smooth-scroll defeating the fold shots;
  the index overflowing instead of wrapping on desktop; oversized faculty photos; the roster label
  wrapping under its own mark; the Inference and Transients glyphs colliding; the tablet range
  stacking the theme image too early; a CJK name breaking mid-run at 360px).
- No horizontal overflow: `scrollWidth === innerWidth` at 360, 390, 700, 1440 and 1600.
- Toggle: clicking one switch sets `data-theme` and `aria-checked` on all three; verified in-browser.
- Index: scrolling 200px into Postdoctoral Researchers reports exactly that chip as current.
- Self-containment: no `<link>`, no `@import`, every `src` is a `data:` URI.
