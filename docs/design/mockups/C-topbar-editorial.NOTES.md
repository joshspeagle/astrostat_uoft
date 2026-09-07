# Direction C — "Top bar, editorial"

## The direction in three sentences

The left sidebar becomes a sticky top bar carrying the mark, the wordmark, four
destinations and the theme toggle, so the content column starts at the top of the page and
runs the full width on every screen. Home keeps a hero built from the mark and the
three-line wordmark, redrawn at a fifth of the topper's area and on Home only; the two long
pages instead open with a title band and then a horizontal, sticky **section index** —
People by section name and count, Research by theme name and icon — that highlights the
section in view. Everything else is the canon applied literally: flat surfaces, dotted
links, one hue, structure in grey at hairline weight, and a second non-colour channel on
every distinction that carries argument.

---

## Every decision, and why

### The structural move: top bar instead of sidebar

| Decision | Why |
|---|---|
| Nav becomes a sticky top bar, same on all three pages | The sidebar's cost is not that it is ugly; it is that it takes a column *and* the 300px topper takes a band, so on desktop the content starts ~300px down and ~200px in, and at medium widths the sidebar column is too narrow to hold the nav comfortably. A 56px bar costs one band and no column. |
| The bar is sticky at every width, not just on scroll-up | The canon requires navigation to stay "reachable without a long scroll back". People runs 4,700px in this mockup with 16 people; the real page runs ~15,000px with 50. A nav you have to scroll 15,000px to reach is not navigation. |
| Order in the bar: mark, wordmark, destinations, toggle | The canon fixes the order of the navigation region. Reading order left to right is identity → where you can go → how the page looks. |
| Current page: ink instead of link, bold, plus a hairline quiet bar on its leading edge | Canon, literally: hue is never the only channel. Three channels (colour, weight, a mark) so it survives greyscale and colour-blind viewing. The hairline is on the *leading* (left) edge because that is what the canon says; in a horizontal bar it reads as a tick before the word rather than as a separator, because it hugs the item's padding. |
| External mark on *Statstro* only | Canon. Body links here are nearly all external, so a mark on each is noise; the one external item in the nav is the one place it says something. |
| Toggle: paddle position + track colour + the visible words "Dark mode" | Canon's three channels. The words are the accessible name, so `role="switch"` needs no `aria-label` fighting a hidden string. Track quiet when off, link when on; paddle is the page surface (5.28 and 7.12 against the two tracks in light, 7.12 and 8.64 in dark). |
| Below 768px the nav collapses to one control named **Menu**, and the current page name stays in the bar beside it | Canon: "at small widths it collapses to one control named *Menu* that never hides the name of the page you are on." |
| The Menu control has no border | Canon: "the only borders are the link underline, the focus ring and the divider." My first draft boxed it; the box was a fourth border and had to go. The chevron plus the ink weight carry the affordance. |
| Below 358px the wordmark drops and the mark carries the brand alone | 360px is the narrowest width the brief targets and the bar fits exactly there; the rule only fires below it, so a 320px phone degrades instead of overflowing. |

### The hero, and the topper's retreat

| Decision | Why |
|---|---|
| The mark sits beside the wordmark instead of behind it | Behind it, the wash has to be pale enough to read text over, which is what forces it to be a large, low-contrast field. Beside it, the mark can be smaller and the wordmark sits on the page surface at 19.63. |
| Measured: hero mark bounding box is **240 × 135 = 32,400 px²** on desktop, against the current topper's **~535 × 300 = 160,500 px²** — an 80% cut, and it appears on one page instead of three, so ~93% across the site | The canon's restraint clause: colour covers ~1% of the page, and the topper "carries no information after the first visit". This is the one number that decides whether a hero is restraint or decoration. |
| Inner pages get a title band (h1 + intro) instead of a topper | One idea to a panel; a page has one hero and only Home's is the big one. |
| The three lines take the display / h3 / small steps | A single display line and then a fast drop; the third line is institutional and does not need weight. |

### The section index

| Decision | Why |
|---|---|
| Horizontal, sticky directly under the top bar, on People and Research only | It is wayfinding for length. Home is 2,000px and needs none. |
| People shows section name + count; Research shows theme name + icon | Counts are the thing a visitor actually wants on People ("how many postdocs?"), and they are free — the renderer already knows. Themes have no natural number, so the second channel there is the glyph. |
| Current section: ink, bold, no underline | Canon for the in-page index is "ink instead of link, bold". I dropped the dotted underline on the current item as well, because a bold ink item still wearing the link idiom reads as a link you have not visited. Flagged below as a small extension of the canon. |
| Driven by an IntersectionObserver with a **1px probe line** 22% of a viewport below the sticky chrome | A percentage-band observer highlights whichever section shows *most*, which flickers near boundaries and highlights nothing at the very top or bottom. A 1px line means exactly one section spans it at any moment; the fallback picks the first section above the fold and the last one past the end. This is the canon's "measure, don't judge" applied to a UI state. |
| The index scrolls the current item into its own view | On a phone the index is a scroller and "Collaborators" is 800px off-screen to the right. A marker nobody can see marks nothing. The first draft got this wrong and the phone screenshot showed a highlight that was simply absent. |
| Index items take the **label** type step (0.85rem), not small | At `small`, the eight research themes with their icons measured 1,236px against 1,136px of content column, so "Star Formation" was clipped on a 1440px desktop — a scroller is correct on a phone and looks broken on a desktop. At the label step the set measures ~1,090px and fits. |

### People

| Decision | Why |
|---|---|
| Members keep full cards: photo, name, website line, status note, bio. No role line. | Owner ruling, binding. |
| The website line is the **label idiom** (bold, uppercase, tracked, label step) | Canon names "the People card's website line" as one of the things that idiom carries. It also solves half of the "Personal Website repeated fifty times" problem: at label weight and size it reads as a signpost rather than as the card's headline, which is what it was doing at body size. The other half is a content fix and is not mine to make. |
| One uniform card module: a 3-column grid on desktop for *every* section, so Faculty occupies two of three columns | My first draft honoured `medium-up-2` for Faculty, which gave the two faculty 510px photographs against the postdocs' 316px — two card sizes, and the largest photographs on the site attached to the shortest section. One module, one photo size, and the empty third column reads as deliberate space. |
| Collaborators and Recent Alumni are compact rows | Owner ruling, binding. |
| The compact row has **no photograph** | Here the direction brief ("small photo, name, affiliation, link") and the canon ("A compact row … is no photo, one line per person, name then affiliation") conflict. I obeyed the canon, and I would have argued for it anyway: the asset bundle carries headshots for four of the six collaborators and none of the alumni, so a photo column would have been part real and part empty grey square; and a row's whole point is that these people are present but not argued about — the context-grey idea applied to layout. **This is a deliberate deviation from the direction brief; judges should treat it as a proposal, not an oversight.** |
| The affiliation is the first sentence of the bio, compressed to a phrase, in ink at the small step — not in quiet | Quiet means caption, footer, divider. An affiliation is content. The row's hierarchy comes from weight and size, which is what the canon wants doing that job. |
| 2-up cards on phones | Measured on a 390px phone: the six postdoc cards are **3,023px** at 2-up and **4,873px** at 1-up — 504px per person against 812px, a 38% cut. That is the single biggest lever on the "37,000px People page" problem. The cost is a 17–20 character measure in the bio, which is why the bio drops to the small step below 768px. |

### Research

| Decision | Why |
|---|---|
| Each theme opens with its icon beside the `h2` | The eight themes are the one recurring identity set on the site, and the index needs to tell them apart at a glance. The glyph beside the heading is what teaches the code the index then uses. |
| The image is always on the same side (left) | Alternating sides makes the reader re-find the prose on every theme. Redraw rather than redesign, applied down a page: eight blocks, one layout. |
| The image is square from 768px up and 3:2 below | Square works beside prose; square at full phone width is a 358px block of decoration between the heading and the first sentence, and it was the largest single contributor to the Research page's mobile length. |
| The `(Image credit: …)` clause moves out of the prose into the figure's caption, in quiet at the small step, and loses its italics | The canon says italic is for the title of a work and nothing else, and the credit is a caption by definition — quiet already owns that role. The words are unchanged. |
| Roster: **filled / open / no square** before MEMBERS / ASSOCIATES / COLLABORATORS | Canon. Those three are ordered — inside, affiliated, outside — and fill expresses an order that hue does not. The words never go away; the mark is the second channel, never the only one. |
| The roster label column is a fixed 11.5rem so the three rows align, stacking below 640px | Canon. The label wraps to two lines at that width; the square aligns to the first line rather than to the block's centre. |

### Structure and surface

- Corner radius 0 and shadow none everywhere; the only borders are the link underline, the
  focus ring, the top-bar and index dividers.
- Sections are separated by space (step 7 above an `h2`), never by a rule; the two dividers
  that do exist are under the sticky bar and under the sticky index, where space cannot do
  the job because the content scrolls beneath them.
- Every length in the stylesheet is one of the nine spacing steps; every font-size is one of
  the seven type steps; hairlines and the 68ch measure are the two declared exceptions.

---

## The token table used

Nothing in the stylesheet restates a hex outside these two blocks; every rule references a
variable. This is the canon's `check_tokens.py` contract expressed in CSS.

| Token | Light | Dark | Role in this mockup |
|---|---|---|---|
| `--page` | `#fefefe` | `#0a0a0a` | Page surface; the top bar's and index's own background; the toggle paddle |
| `--card` | `#eeeeee` | `#333333` | People card, compact row, roster block, image placeholder |
| `--wash` | `#91acde` | `#2f559d` | The Home hero mark. Decoration; nothing else uses it |
| `--ink` | `#0a0a0a` | `#fefefe` | Body, headings, names, affiliations, current page, current section, roster marks |
| `--link` | `#2f559d` | `#91acde` | Links, focus ring, toggle on-track |
| `--mark` | `#001f4e` | `#70a9ff` | The ART mark in the top bar |
| `--quiet` | `#6b6b6b` | `#9b9b9b` | Captions, the site note, mockup notes, the two dividers, index counts, toggle off-track |

Pairs drawn, all from the canon's measured list: ink on page 19.63 · ink on card 17.06 /
12.53 · link on page 7.16 / 8.64 · link on card 6.23 / 5.51 · quiet on page 5.28 / 7.12 ·
quiet on card 4.59 / 4.55 · mark on page 15.94 / 8.30 · page on quiet 5.28 / 7.12 · page on
link 7.16 / 8.64. The wash is drawn only against the page (2.27 / 2.74) and carries nothing.
**No pair outside that list is drawn.**

### Type scale as used

| Step | Value | Where in this mockup |
|---|---|---|
| display | `clamp(2rem, 1.25rem + 3vw, 3.25rem)` | Hero line 1 only |
| h1 | `clamp(2rem, 1.4rem + 2.6vw, 3rem)` | Page title, once per screen |
| h2 | `clamp(1.5rem, 1.2rem + 1.4vw, 2rem)` | People sections, Research themes, Statstro |
| h3 | `clamp(1.2rem, 1.08rem + 0.55vw, 1.45rem)` | Card names, hero line 2 |
| body | `clamp(1rem, 0.94rem + 0.28vw, 1.125rem)` | Prose, bios (≥768px), roster names, row names |
| small | `clamp(0.875rem, 0.85rem + 0.12vw, 0.94rem)` | Captions, site note, nav links, affiliations, bios (<768px) |
| label | `0.85rem` | The label idiom, index items, index counts, page name in the mobile bar |

**One amendment I am proposing, not smuggling:** the canon's display step is
`clamp(2.5rem, 1.5rem + 5vw, 5rem)`, sized for a 300px topper. With the topper gone that
step renders an 80px line above a 48px `h1` on the same screen and the hero swallows the
page. I shrank it to `clamp(2rem, 1.25rem + 3vw, 3.25rem)`. If Direction C is chosen, that
line changes in DESIGN.md in the same commit.

---

## What would change in the real SCSS / EJS / JS

**SCSS** (`scss/`)

1. New `_tokens.scss`: the two `:root` blocks above plus the spacing scale, the type scale
   and `--measure`. `_lightmode.scss` and `_darkmode.scss` collapse into it —
   `data-theme` already drives everything, so the two files only ever held pairs of hexes.
2. Delete the teal variables and the `.thumbnail` placeholder fill; an unloaded image shows
   its surface. Delete `#888888`; `--quiet` replaces both of its uses.
3. New `_topbar.scss` (bar, brand, nav, `here`, external mark, toggle, Menu control, panel)
   and `_index.scss` (sticky scroller, item, count, `is-current`). Both are ~60 lines.
4. `_cards.scss`: one `.people-grid` with `repeat(2, …)` below 768px and `repeat(3, …)`
   above, replacing the per-section Foundation `small-up-*/medium-up-*` classes; plus
   `.person-row` for the compact form and `.roster` for the theme block.
5. Foundation's grid, media-object and thumbnail components stop being used on all three
   pages. Foundation's JS is already unused. That is the moment to check whether Foundation
   and jQuery can leave the bundle entirely.
6. Global: `border-radius: 0`, no shadows, the dotted/solid link rule, and a
   `:focus-visible` ring that is never removed.

**EJS / build** (`ejs/`, `build/`, `webpack.config.js`)

7. `main.ejs` loses the 300px topper and the sidebar column; it gains the top bar partial,
   which takes the current page key so `aria-current="page"` and the `here` span are set at
   build time rather than guessed by JS.
8. The hero becomes a Home-only partial. The mark stays a single inline SVG with its `fill`
   removed so CSS owns the colour — the file currently bakes `fill="#2f559d"` into the path,
   which is a hex outside the token table and would have to go.
9. `build/render-people.js` gains: a `layout: "card" | "row"` key per section (defaulting to
   card), the section index built from the section headings and `people.length`, and an
   `affiliation` field per person for the row form. `data/people.json` gains `affiliation`
   on Collaborators and Recent Alumni only — and, per the owner's ruling, **no `role`
   field**.
10. The Research page becomes data-driven the same way (`data/research.json`: theme, icon
    key, image, alt, prose, credit, three roster lists), which is what makes the index, the
    icon set and `sort_themes.py` all read from one place. Today `sort_themes.py` reorders
    `<h2>` blocks in HTML by regex; against JSON it becomes a two-line sort.
11. The icons ship as an inline SVG sprite (`<symbol>` per theme) emitted by the build, so
    the eight glyphs exist once and `currentColor` still works.

**JS** (`js/index.js`)

12. Theme: keep `localStorage`, and add a tiny blocking script in `<head>` that sets
    `data-theme` before first paint — today the toggle flashes light on a dark-mode reload.
13. Toggle: a `<button role="switch" aria-checked>` with a visible label, replacing the
    Foundation switch that renders broken on phones.
14. The section index: ~40 lines, one `IntersectionObserver` per page with the 1px probe
    line, the ordered fallback, and the reveal-into-view for the mobile scroller. Rebuild the
    observer on resize because the probe line is a pixel value.
15. The Menu control: `aria-expanded` and a `hidden` panel. No focus trap — it is four links
    and a switch, not a dialog.

**Other**

16. Favicon becomes the sparkle particle alone in the mark token, plus an SVG icon and an
    apple-touch icon; the whole logo at 16px is unreadable.

---

## Honest self-critique

### The sidebar question, argued rather than assumed

**What a visitor gains.** The content column starts at the top of the page and uses the full
width, so the first screen carries content instead of chrome — on Home, the wordmark, the
title and the whole lede are above the fold, where today the fold ends inside the topper.
Navigation stops disappearing: today the sidebar scrolls away and does not come back, so
reaching "Research" from the bottom of People means scrolling 15,000px; a sticky bar is
always one glance away. It frees the space the section index needs — the index and the bar
together are 102px, less than a third of what the topper alone spends, and they earn it on
every scroll rather than on the first visit. And it collapses honestly on a phone, where the
present sidebar plus topper consume the entire first screen.

**What is lost.** Two things, and they are real. First, the *quiet* of the sidebar: a
left-hand column with four words in it makes no claim on the reader's attention, while a
bar across the top is a horizontal band that the eye crosses on the way to every heading.
The site becomes very slightly more like every other site. Second, and more seriously, the
**scale of the identity**: at 300px tall the topper is unmistakably a group's homepage
banner, and 56px of top bar plus a 240px hero on one page is a much smaller claim. A
research group's site that stops announcing itself loses something that a usability
argument cannot price. If the owner's attachment to the sidebar is really an attachment to
that scale, Direction C is the wrong answer and should lose.

**How the mark keeps the brand present.** The mark is in the top bar on every page, at
28px, in the `mark` token, at 15.94 (light) and 8.30 (dark) against the page — well clear of
the mark floor, unlike the pale wash it replaces at 2.27. Today the mark appears in the
sidebar at a similar size and the *topper* carries the identity; Direction C swaps which of
the two is doing the work, so the brand is present at the top of every screen and stays
present as you scroll, rather than being large once and then gone. The wordmark
"Astrostat@UofT" sits beside it in ink at every width down to 358px. The full mark and the
three-line wordmark still exist, on Home, where a first-time visitor meets them.

### Where I think this mockup is weakest

1. **Two blues for one drawing on one screen.** On Home the mark appears twice: in the bar
   in the `mark` token and in the hero in the `wash` token. Both assignments are canon-
   correct — identity versus decoration — but a reader sees the same logo in two colours
   30px apart and reads it as a mistake, not as a code. This is the strongest evidence yet
   for the canon's own pending question about the wash; my own view is that the hero mark
   should take `mark` and the wash token should be retired with the topper, which would
   leave this direction with six tokens instead of seven. I did not make that change because
   the brief asked for a hero built from the wash-style mark, and retiring a token is the
   owner's call.
2. **2-up cards on a 360px phone give a 17-character measure.** The height saving is real
   and measured (38%), but a bio set 17 characters to the line is not comfortable reading,
   and hyphenation only softens it. If I were choosing freely I would hold 1-up below 400px
   with the photo at 40% width beside the name, and switch to 2-up from 400px — which keeps
   most of the saving and none of the ragged measure. The brief specified 2-up on phones and
   the mockup honours it, so a judge can see the cost and decide.
3. **The current-page hairline is the weakest of the three channels.** In a horizontal bar
   a vertical hairline before a word is easy to miss, and at a glance it can read as a
   separator between "Home" and the mark. Bold ink is doing nearly all the work. A 2px quiet
   underline beneath the current item would be far clearer, but "solid underline" already
   means hover on this site and the canon forbids reassigning it. If Direction C wins, this
   is the one rule I would ask the canon to re-open.
4. **The compact row deviates from the direction brief** (no photograph), for canon and
   asset reasons set out above. If the judges want photographs in rows, the canon's
   compact-row definition has to change too, and the site needs six more headshots.
5. **The section index does not survive JavaScript being off.** The items are real anchors
   and still jump, so nothing is broken, but the highlight is the one piece of wayfinding
   that is purely scripted. Everything else here works as static HTML.
6. **The `h1` on Home sits directly under the hero wordmark**, so the first screen carries
   "Astrostat@UofT" and then "Welcome to the ART!" — two headline-weight statements in
   400px. That is faithful to the current copy, not a design choice, and it is the thing I
   would raise in a copy pass rather than fix in CSS.
7. **The stubs are mockup scaffolding.** Three People sections and six Research themes are
   present as heading-only blocks so that the index is complete, real, and testable. They
   make the page look padded in a way the live page would not. Every one of them is labelled
   in quiet grey.

### What is in this mockup that is not the real page

- Six of nine postdoctoral researchers (the asset bundle carries no headshot for the other
  three); six of fourteen collaborators; two of nine recent alumni; two of eight research
  themes in full. All copy shown is verbatim from `data/people.json`,
  `ejs/pages/home/body.html` and `ejs/pages/research/body.html`; the six compact-row
  affiliations are the only text I wrote, and each is compressed from the first sentence of
  that person's own bio.
- The `people-deep` screenshots are taken **3,880px** (desktop) and **4,954px** (mobile)
  into the People screen rather than the ~1,200px the brief suggested. At 1,200px the
  viewport is in the middle of the postdoctoral grid; the compact rows begin further down
  because the real content above them is that long. The stated purpose of the shot — compact
  rows plus the section-index highlight in one frame — is what I aimed at.
