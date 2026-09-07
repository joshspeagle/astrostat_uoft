# Direction A — Sidebar, restructured

## The direction in three sentences

The left sidebar stays, and earns its width: below the mark, the four destinations and the
theme switch, it carries an in-page index of the current page — People's sections with their
counts, Research's eight themes with their icons — and highlights the section you are
reading. The 300px topper is Home's alone; People and Research open with a compact masthead
about 90px tall, so the page's own `h1` is on the first screen instead of the third. At
narrow widths the whole rail collapses into one sticky two-line top bar (mark and wordmark
with the labelled switch, then the four links), the index becomes an "On this page"
disclosure under the `h1`, Collaborators and Recent Alumni become compact rows, and the
People card turns into a photo-beside-name media row so a phone reads a bio at full measure.

## Files

- `mockup.html` — the deliverable, 1.1 MB, self-contained, zero external requests
  (fonts, logo, headshots and theme images are all `data:` URIs; icons are inline SVG).
- `build.py`, `parts_css.py`, `parts_html.py`, `content.py` — the generator. `content.py`
  holds the copy, lifted verbatim from `ejs/pages/home/body.html`, `data/people.json` and
  `ejs/pages/research/body.html`.
- `thumbs.py` / `thumbs.json` — 128px square crops of eight `static/` headshots, generated
  locally for the compact rows (`mockup-assets/assets.json` ships four of the six
  collaborators and neither alumnus). Nothing in the repo was modified.
- `shoot.py` — the Playwright run. `check.py` — the 360 / 768 / 1600 responsive and
  toggle-click verification.

## Screenshots (`shots/`, 20 PNGs)

| | light | dark |
|---|---|---|
| whole file, desktop 1440×900 | `full-desktop-light.png` | `full-desktop-dark.png` |
| whole file, mobile 390×844 | `full-mobile-light.png` | `full-mobile-dark.png` |
| Home fold, desktop | `fold-home-desktop-light.png` | `fold-home-desktop-dark.png` |
| People fold, desktop | `fold-people-desktop-light.png` | `fold-people-desktop-dark.png` |
| Research fold, desktop | `fold-research-desktop-light.png` | `fold-research-desktop-dark.png` |
| People deep scroll, desktop | `fold-people-scroll-desktop-light.png` | `fold-people-scroll-desktop-dark.png` |
| Home fold, mobile | `fold-home-mobile-light.png` | `fold-home-mobile-dark.png` |
| People fold, mobile | `fold-people-mobile-light.png` | `fold-people-mobile-dark.png` |
| Research fold, mobile | `fold-research-mobile-light.png` | `fold-research-mobile-dark.png` |
| People deep scroll, mobile | `fold-people-scroll-mobile-light.png` | `fold-people-scroll-mobile-dark.png` |

One deliberate deviation from the shot list: the "deep scroll" shot was asked for at ~1200px
into the People screen "so the compact rows and the section-index highlight are visible".
At 1200px the viewport lands inside the postdoc card grid — the highlight is visible, the
compact rows are not. The shot is taken 110px above the Collaborators heading instead, which
is where both are on screen at once. That is the stated purpose of the shot; the literal
offset was not.

## Every design decision, and why

### Navigation

1. **The rail is kept and given a second job.** A sidebar that holds four links and a toggle
   is 240px of page paying for about 160px of content, which is the honest case against it.
   Adding the in-page index makes the column carry the one thing the site most lacks:
   wayfinding on a page that runs ~15,000px. The rail is `position: sticky` so the index is
   always one glance away, and it scrolls internally (`max-height: 100vh`) so a long index
   can never exceed the viewport.
2. **Canon order is followed exactly**: mark, four destinations, theme toggle, then the index.
   The toggle sitting *between* the destinations and the index looks slightly odd at first
   and was kept anyway — the canon fixes the order so that the region is identical on every
   page, and Home (which has no index) then ends at the same control every page ends at.
3. **Current page is marked three ways**: ink instead of link, bold, and a 2px quiet bar on
   the leading edge. Never colour alone.
4. **Statstro is the only item with the external arrow.** It is the only destination that
   leaves the site, so the mark says something; a mark on every body link would be noise.
5. **Home has no in-page index.** Home is one screen of prose and two figures; an index of
   two headings is a signpost pointing at itself. The canon's "a role gets a token only when
   it recurs" applies to page furniture too.

### The topper

6. **The 300px topper is Home only.** It is the largest area of colour on the site and it
   carries nothing after the first visit. On Home it is the front door and it stays. On the
   inner pages it is replaced by a masthead of the wordmark and one quiet subtitle line,
   about 90px tall, which puts `h1` at roughly y=170 on desktop instead of y=390.
7. **The mark is not repeated in the inner-page masthead.** The mark sits at the top of the
   rail and the wordmark sits at the top of the content column; they align on one line, so
   the identity reads as one unit without being drawn twice. On Home the rail mark is the
   persistent identity once the topper has scrolled away, which is why it appears there too.

### The in-page index

8. **Counts on People, icons on Research.** They are different questions. On People the
   useful fact is how many people are in a section; on Research it is which theme this is,
   and eight recurring identities is exactly the case the canon says iconography earns.
9. **The highlight is ink + bold, never a colour swap.** The link's dotted underline is
   dropped on the current item so the row reads as a state rather than a destination.
10. **Scrollspy rule**: the last section whose top has crossed a reading line 120px down the
    viewport; if none has, the first section still on screen. `IntersectionObserver` (with
    `rootMargin: -80px 0 -45% 0`) drives the repaint, and a passive `scroll` listener covers
    the case where no boundary is crossed for a long section. Each screen observes only its
    own sections, so the three pages in this one file do not fight.
11. **Six of the eight Research themes are listed but not drawn** in this mockup. They are
    rendered as quiet non-links with their icons, so the icon set can be judged as a set,
    with a one-line note saying why they are inert.

### Narrow widths

12. **One sticky two-line top bar.** Row 1 is mark, wordmark, the visible label DARK MODE and
    the switch; row 2 is the four links. Two rows rather than one because at 360px a single
    row cannot hold four labelled destinations *and* a labelled switch, and the canon forbids
    hiding the switch's label. The bar is 66–76px, which is 8% of a 844px screen; today's nav
    plus a 300px topper consumes the whole first screen.
13. **The current-page bar rotates with the axis.** In the rail it is a leading-edge bar; in
    the top bar it is a 2px quiet rule under the word. Same role, same token, same weight —
    the edge it sits on follows the direction of the list.
14. **The index becomes a native `<details>` disclosure** under the `h1`, on the card surface.
    In the mockup People's is open and Research's is closed so both states are visible;
    shipped, both would be closed.
15. **The switch is redrawn as a real switch** — 44×24 track, 20px square paddle, no radius —
    with `role="switch"`, `aria-checked`, and a visible `DARK MODE` label that is also its
    accessible name. State is carried by paddle position *and* track colour (quiet off, link
    on). It is 40×22 in the top bar. The current site's switch renders broken below ~640px;
    this one is the same object at every width.

### People

16. **No role line, no `role` field** — the owner's ruling. The card is photo, name, website
    link, status note, bio, in that fixed order.
17. **"Personal Website" becomes a `WEBSITE` label.** The repeated first line of ~50 cards is
    fixed where the canon says it should be — in the card template — by demoting it into the
    small-caps label idiom rather than by weakening the link token. It is still a real,
    dotted, link-token link; it is just no longer a body-size sentence repeated fifty times.
18. **Collaborators and Recent Alumni are compact rows**: 48px photo, the name *as* the link
    to their site, and a one-line affiliation lifted from the first sentence of the bio.
    Two per row on desktop, one on mobile. Six collaborators cost 300px instead of ~2,600px.
19. **Names link to sites on compact rows; cards keep a separate `WEBSITE` line.** On a
    one-line row the name is the only thing worth clicking; on a card the name is an `h3`
    and headings should not be links.
20. **A person with no site on file is plain ink** (Mairead Heiger), never a dead link.

### Research

21. **The icon sits beside the `h2`, at 1.05em of the heading and stroke 2.3**, so it holds
    optical weight against Urbanist Bold. Same glyph, same size relationship, in the index.
22. **The image is always on the right.** The current page alternates sides theme by theme,
    which makes the reader re-find the text column eight times. One side, always.
23. **The roster block gets the fill mark**: filled square = member (inside the group), open
    square = associate (affiliated), no square = collaborator (outside). Ordered, and drawn
    as an order. The words never go away; the mark is the second channel.
24. **Roster labels are three words at most** — MEMBERS / ASSOCIATES / COLLABORATORS — in the
    label idiom, in a fixed 11.5rem column so the three rows align. "ART members involved:"
    is a sentence, and the canon says a label is never a sentence.

### Measurement

25. **`68ch` was measured and rejected as written.** Inclusive Sans' zero is ~0.66em, so
    `68ch` at body size is 816px, which sets ~90 characters to the line. The mockup uses
    `--measure: 38rem` (608px ≈ 68 characters of this face). The canon's *intent* (68
    characters) is kept; its *implementation* (`68ch`) should become a length. This is the
    one change the mockup makes to `docs/DESIGN.md` as written.
26. **Colour was not re-judged.** Every pair drawn here is a pair `check_tokens.py` already
    declares and passes: ink/link/quiet on page and card, ink on wash, page-on-quiet and
    page-on-link for the switch. No new pair was invented.

## Token table used

Exactly the canon's seven, one role each, no additions.

| Token | Light | Dark | Used in this mockup for |
|---|---|---|---|
| `--page` | `#fefefe` | `#0a0a0a` | body, top-bar ground, switch paddle, compact-row photo backstop |
| `--card` | `#eeeeee` | `#333333` | People cards, compact-row blocks, roster blocks, the "On this page" disclosure |
| `--wash` | `#91acde` | `#2f559d` | the Home topper logo fill, and nothing else |
| `--ink` | `#0a0a0a` | `#fefefe` | body, headings, current nav item, current index item, roster marks |
| `--link` | `#2f559d` | `#91acde` | every link, the focus ring, the switch's on-track |
| `--mark` | `#001f4e` | `#70a9ff` | the rail mark and the top-bar mark |
| `--quiet` | `#6b6b6b` | `#9b9b9b` | crumbs, captions, counts, affiliations, site note, dividers, switch off-track, current-page bar, inert index rows |

Type — the canon's seven steps, unchanged, all `clamp()`:
`display 2.5→5rem` (Home topper only) · `h1 2→3rem` · `h2 1.5→2rem` · `h3 1.2→1.45rem`
(card names) · `body 1→1.125rem` · `small .875→.94rem` (captions, bios, roster names,
affiliations) · `label .85rem` (NAVIGATE, DARK MODE, ON THIS PAGE, WEBSITE, crumbs, section
counts, roster labels).

Spacing — the canon's nine steps on a 4px base, `0.25 0.5 0.75 1 1.5 2 3 4.5 7` rem. No
other length in the stylesheet except the hairline, the measure, the rail width (15rem), the
roster label column (11.5rem), the switch geometry and the fixed photo sizes (88px card
media-row, 48px / 44px compact row).

Marks — radius 0 and shadow 0 everywhere (verified by grep on the built file). Links are 1px
dotted at rest, solid on hover/focus/active, never mixed toward the surface. Focus is 2px
solid link at 2px offset. Icons: 24px grid, 2px stroke, round caps and joins, no fill,
`currentColor`, one idea per glyph.

### The eight theme glyphs, drawn as a set

| Theme | Glyph | Idea |
|---|---|---|
| Inference | bell curve with a vertical at the mode | a distribution and an estimate of it |
| Stellar Evolution | a star inside a cycle arrow | one star through its life |
| Dark Matter & Cosmology | a dashed ring around a solid core | unseen halo, seen matter |
| AI for Scientists | three nodes, two edges | a network |
| The Milky Way | a thin inclined disc with a bulge | our galaxy seen from inside it |
| Galaxies | two ellipses, one large one small | an interacting pair |
| Transients | a flat line with one sharp spike | a light curve |
| Star Formation | a cloud with a core | a protostar in its cloud |

The four-pointed sparkle is deliberately *not* used in any glyph: it is the brand particle
and is reserved for the mark and the favicon.

## What I would change in the real SCSS / EJS / JS

**SCSS.** Add `scss/_tokens.scss` holding the seven colours per theme as custom properties
on `:root` and `html[data-theme="dark"]`, plus the nine spacing steps and seven type steps,
and import it first from `index.scss`. `_lightmode.scss` and `_darkmode.scss` then shrink to
the two token blocks and nothing else — no rule outside `_tokens` may name a hex. Replace
`_global.scss`'s hardcoded sizes with the `clamp()` steps. New partials: `ux/_rail.scss`
(sticky rail, nav, index), `ux/_topbar.scss` (the narrow collapse), `ux/_card.scss`
(card and the ≤560px float media-row), `ux/_rows.scss` (compact rows), `ux/_roster.scss`
(label column and the three fill marks), `ux/_masthead.scss`. `ux/_switch.scss` is rewritten
to the 44×24 geometry above. Foundation's grid classes can go: three `grid-template-columns`
rules replace `small-up-N medium-up-N` and remove the reason `grid` lives in `people.json`.

**EJS / build.** `main.ejs` grows the rail and the top bar, and takes two new locals: `page`
(for `aria-current`) and `toc` (an array of `{anchor, label, right, icon}`). The compact
masthead and the topper become a conditional on `page === 'index'`.
`build/render-people.js` emits `id`/`data-sec` on each section, a count, and switches on a
new per-section `"form": "card" | "row"` key in `data/people.json` (default `card`) so
Collaborators and Recent Alumni render as rows; it also builds the People `toc` array so the
index cannot drift from the sections. `paragraphs[0]` keeps its current shape — the renderer
detects a lone anchor as the website line and emits it as the label, so no data migration is
needed. The Research page should become data-driven the same way
(`data/research.json` with `{anchor, icon, heading, image, alt, prose, members, associates,
collaborators}`), which also gives `sort_themes.py`, `theme_fit.py` and `audit_site.py`
something structured to read instead of regexing HTML. Icons ship as one inline SVG sprite
emitted into every page by `main.ejs`.

**JS.** `js/index.js` keeps the `localStorage` theme, but sets `data-theme` from an inline
head script *before* first paint to kill the flash, and drives `aria-checked` on the switch
rather than a checkbox hack. Add ~25 lines of scrollspy: observe `[data-sec]`, paint
`aria-current="true"` on the matching index link by the reading-line rule above, and guard
the whole thing behind `if ('IntersectionObserver' in window)` — with no JS the index is
still a working list of jump links. jQuery and Foundation's JS are not needed by anything
here.

**Assets.** `art-logo-mod.svg` needs `fill="currentColor"` on its path instead of the baked
`#2f559d`, so one file serves the wash, the rail mark and the favicon in both themes. The
favicon becomes the sparkle particle alone.

## Honest self-critique

- **I did not do "2-up cards on phones", which the direction brief asked for.** At 390px, two
  columns with a 16px gutter and a 12px gap give a 173px card and, after step-3 padding, a
  149px text column — about 18 characters to the line against a floor of roughly 35. I
  measured it rather than judged it and took the other road: below 560px the card becomes a
  media row, an 88px photo floated beside the name, website label and status note, with the
  bio at the card's full width (~40 characters). It costs about 500px per person instead of
  ~720px today — most of the length saving 2-up would have bought, without the ransom-note
  column. It is a one-line media-query change to switch back if the judges disagree, and the
  measurement is the argument, not my taste.
- **The sidebar is still 240px of nothing on Home**, where there is no index to put in it.
  Home's rail holds a mark, four links and a switch and then stops, and that is the strongest
  argument a top bar has in this comparison. A fair reading is that Direction A is clearly
  right on People and Research and merely acceptable on Home.
- **The index is a list of headings, not a map.** On People it is four rows here and seven on
  the real page; on Research it is eight. Neither is long enough to need scrolling, which is
  lucky, because a rail index that itself scrolls is a worse problem than no index.
- **Two small canon amendments are owed.** (a) The open roster mark needs a 1.5px border, and
  the canon's "the only borders are the link underline, the focus ring and the divider" does
  not list it; the mark is sanctioned in the same document, so the sentence should name it.
  (b) The compact row here has a photo, where the canon's definition says "no photo" — the
  direction brief asked for one, and it does help identify a face on a page that is otherwise
  all faces. One of the two should give; my preference is the canon, because the photo costs
  48px and buys recognition on exactly the rows where a reader is scanning for a name.
- **Bold is synthesised.** Only Urbanist Bold and Inclusive Sans Regular/Italic were
  available, so every `<b>`, `<strong>` and label in Inclusive Sans is a faux bold. The real
  site should ship Inclusive Sans SemiBold or Bold; the label idiom depends on it, because
  small caps at regular weight go muddy.
- **The theme figure leaves a tall empty column** beside the roster on Research when the
  prose runs long. It is honest whitespace and matches the current page, but a sticky figure
  or a wider image would use it better, and I did not try either.
- **`ch` was the only measured surprise, and I only caught it because the line looked long.**
  Every other value here I inherited from the canon and did not re-derive. If the canon is
  wrong somewhere else in the same way, this mockup reproduces the error faithfully.
