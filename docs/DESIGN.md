# Design

This document is the website's canon: the fixed meaning of every colour, mark, type size
and piece of spacing on astrostatuoft.com. Each meaning is held the same on every page, so a
visitor learns the code once and then reads the site instead of decoding it. Check it before
changing anything, and when a change introduces a role the canon does not yet name, add the
role here in the same commit.

The whole file rests on one rule. **A token, once assigned, is never reassigned.** Once a
colour or a mark means something, it means that everywhere else. A visitor who has to learn
the code a second time has lost the code.

It stays short for two reasons: a vocabulary is only worth anything if every token in it is
used often, and every token added makes every later page harder to read. **A role gets a
token only when it recurs.**

Every section headed "(canon)" is in force. "Pending" records what is still open; it is
currently empty, and a new question goes there in the same commit as the change that raises
it.

## The words this file uses

- A **role** is what a drawn thing stands for: a link, the group's mark, a caption, the page
  you are on.
- A **token** is the colour, size, mark or space that stands for a role. The canon is the list
  of which token stands for which role.
- A **surface** is a background ink is set on. There are three: page, card, hero wash. Every
  contrast measurement here names its surface.
- A **theme** is one of the two complete token assignments, light and dark, chosen by
  `data-theme` on `<html>`.
- The **brand particle** is the four-pointed sparkle from the ART mark — the smallest unit of
  the logo that still reads as ART, and the site's one piece of pure identity.
- **Structure** is ink that stands for no role: a divider, a position marker. Structure is
  grey at hairline weight and never in a token colour.
- The **floors** are the two contrast ratios everything is measured against: **4.5 for text,
  3.0 for a mark the reader has to find or follow.**

## The canon as code

`scss/_tokens.scss` holds the palette — its `$themes` map is the one place in the repo a hex
value from this document may be written. `docs/check_tokens.py` **reads that map back out**,
holds the surfaces and every pair the site draws, and measures each pair rather than judging
it. It also checks the two places a hex is unavoidable outside CSS: `ico/favicon.svg`, which
has to carry both themes itself because a browser tab has no stylesheet, and every other
`scss/` file, which must carry none. Run it before and after any change to colour. **A pair
the script does not list is a pair the site must not draw.**

```
python3 docs/check_tokens.py     # matrix + PASS/FAIL per pair; exit 1 on failure
```

## Palette (canon)

Seven tokens per theme, one role each. Periwinkle is the brand hue and the only hue on the
site; everything else is a neutral.

| Token | Light | Dark | Role |
|---|---|---|---|
| **page** | `#fefefe` | `#0a0a0a` | The page surface. |
| **card** | `#eeeeee` | `#333333` | The card and roster-block surface. |
| **wash** | `#91acde` | `#2f559d` | The hero logo fill, on Home. Decoration; carries nothing. |
| **ink** | `#0a0a0a` | `#fefefe` | Body text, headings, roster names, role marks. |
| **link** | `#2f559d` | `#91acde` | Interactive text, the focus ring, the switch's on-state. |
| **mark** | `#001f4e` | `#70a9ff` | The ART mark and the sparkle favicon. |
| **quiet** | `#6b6b6b` | `#9b9b9b` | Captions, the site note, dividers, the switch's off-track. |

Two rulings sit behind that table.

**Teal is retired.** `#82c7ce` / `#31767d` had one job: filling the box behind an image that
has not loaded. That is a state, not a role, and a state does not earn a hue. The one real
candidate for a second hue — member against associate against collaborator — is better
carried by mark fill, because those three are *ordered* and fill expresses an order that hue
does not. Teal also failed on its own terms, never clearing the mark floor on the surface it
sat on (1.64 light, 2.42 dark), and `#82c7ce` is the bright mid-tone register this project's
figure canon rejects. Its two uses become the card surface (placeholder) and quiet grey (the
drilldown arrows, which are structure).

**Caption grey is split by theme.** One shared `#888888` failed the text floor on three of the
four surfaces it was set on (3.51 light page, 3.06 light card, 3.56 dark card). It is
replaced by a **quiet** token that moves with its theme like every other token: `#6b6b6b`
light, `#9b9b9b` dark, each the nearest value to the original that clears 4.5 on both of that
theme's reading surfaces.

**The wash and the link share two hexes across the themes.** `#91acde` is the wash in light
and the link in dark; `#2f559d` is the reverse. This is recorded rather than fixed, on one
condition: the wash is *only* ever the hero's logo fill — never text, never a mark, never a
fill behind interactive text — and within a single theme no hex carries two roles, which is
the rule that matters. Whether toggling makes the swap jarring is for the mockup round.

**The wash is exempt from both floors** (2.27 light, 2.74 dark) because it carries no
information after the first visit. What sits *on* it is not exempt: the wordmark clears 8.64
and 7.16.

### The measurement

Output of `python3 docs/check_tokens.py`, which exits 0:

```text
==========================================================================
LIGHT THEME
==========================================================================

token   hex            Y   role
--------------------------------------------------------------------------
page    #fefefe    99.11   page surface
card    #eeeeee    85.50   card and roster surface
wash    #91acde    40.80   hero logo wash (decoration only)
ink     #0a0a0a     0.30   body text and headings
link    #2f559d     9.54   interactive text, focus ring, switch on-state
mark    #001f4e     1.53   the ART mark and the sparkle favicon
quiet   #6b6b6b    14.70   captions, footer, dividers, switch off-track

contrast matrix (token x surface)
--------------------------------------------------------------------------
                page (#fefefe)        card (#eeeeee)        wash (#91acde)
page                      1.00                  1.15                  2.27
card                      1.15                  1.00                  1.98
wash                      2.27                  1.98                  1.00
ink                      19.63                 17.06                  8.64
link                      7.16                  6.23                  3.15
mark                     15.94                 13.86                  7.01
quiet                     5.28                  4.59                  2.32

declared pairs
--------------------------------------------------------------------------
[ PASS ]   ink on page   19.63 (floor 4.5, text      ) body copy, headings, roster names
[ PASS ]   ink on card   17.06 (floor 4.5, text      ) People card and roster block text
[ PASS ]   ink on wash    8.64 (floor 4.5, text      ) hero wordmark over the logo wash
[ PASS ]  link on page    7.16 (floor 4.5, text      ) links in prose and navigation
[ PASS ]  link on card    6.23 (floor 4.5, text      ) links inside a card or roster
[ PASS ]  link on wash    3.15 (floor 3.0, mark      ) focus ring crossing the hero
[ PASS ] quiet on page    5.28 (floor 4.5, text      ) figure captions and the site note
[ PASS ] quiet on card    4.59 (floor 4.5, text      ) a caption set inside a card
[ PASS ]  mark on page   15.94 (floor 3.0, mark      ) the ART mark, the favicon particle
[ PASS ]  page on quiet   5.28 (floor 3.0, mark      ) theme switch paddle, off
[ PASS ]  page on link    7.16 (floor 3.0, mark      ) theme switch paddle, on
[  --  ]  wash on page    2.27 (floor n/a, decoration) the hero wash itself: carries nothing

==========================================================================
DARK THEME
==========================================================================

token   hex            Y   role
--------------------------------------------------------------------------
page    #0a0a0a     0.30   page surface
card    #333333     3.31   card and roster surface
wash    #2f559d     9.54   hero logo wash (decoration only)
ink     #fefefe    99.11   body text and headings
link    #91acde    40.80   interactive text, focus ring, switch on-state
mark    #70a9ff    39.04   the ART mark and the sparkle favicon
quiet   #9b9b9b    32.78   captions, footer, dividers, switch off-track

contrast matrix (token x surface)
--------------------------------------------------------------------------
                page (#0a0a0a)        card (#333333)        wash (#2f559d)
page                      1.00                  1.57                  2.74
card                      1.57                  1.00                  1.75
wash                      2.74                  1.75                  1.00
ink                      19.63                 12.53                  7.16
link                      8.64                  5.51                  3.15
mark                      8.30                  5.30                  3.03
quiet                     7.12                  4.55                  2.60

declared pairs
--------------------------------------------------------------------------
[ PASS ]   ink on page   19.63 (floor 4.5, text      ) body copy, headings, roster names
[ PASS ]   ink on card   12.53 (floor 4.5, text      ) People card and roster block text
[ PASS ]   ink on wash    7.16 (floor 4.5, text      ) hero wordmark over the logo wash
[ PASS ]  link on page    8.64 (floor 4.5, text      ) links in prose and navigation
[ PASS ]  link on card    5.51 (floor 4.5, text      ) links inside a card or roster
[ PASS ]  link on wash    3.15 (floor 3.0, mark      ) focus ring crossing the hero
[ PASS ] quiet on page    7.12 (floor 4.5, text      ) figure captions and the site note
[ PASS ] quiet on card    4.55 (floor 4.5, text      ) a caption set inside a card
[ PASS ]  mark on page    8.30 (floor 3.0, mark      ) the ART mark, the favicon particle
[ PASS ]  page on quiet   7.12 (floor 3.0, mark      ) theme switch paddle, off
[ PASS ]  page on link    8.64 (floor 3.0, mark      ) theme switch paddle, on
[  --  ]  wash on page    2.74 (floor n/a, decoration) the hero wash itself: carries nothing

==========================================================================
RETIRED VALUES, measured for the record
--------------------------------------------------------------------------
  #888888 on light page (#fefefe) =  3.51  floor 4.5 text under floor - one shared caption grey
  #888888 on light card (#eeeeee) =  3.06  floor 4.5 text under floor - one shared caption grey
  #888888 on dark page (#0a0a0a) =  5.58  floor 4.5 text clears floor - one shared caption grey
  #888888 on dark card (#333333) =  3.56  floor 4.5 text under floor - one shared caption grey
  #82c7ce on light card (#eeeeee) =  1.64  floor 3.0 mark under floor - teal, as an image placeholder fill
  #31767d on dark card (#333333) =  2.42  floor 3.0 mark under floor - teal, as an image placeholder fill
  #333333 on light page (#fefefe) = 12.53  floor 3.0 mark clears floor - switch off-track borrowed from the dark card

==========================================================================
HEXES OUTSIDE THE STYLESHEET
--------------------------------------------------------------------------
  [ PASS ] ico/favicon.svg carries the mark token in both themes;
           no other stylesheet file names a colour.

==========================================================================
All declared pairs clear their floor in both themes.
```

## Type (canon)

**Two families, one job each.** **Urbanist Bold** is display: the hero wordmark and
`h1`–`h3`, nothing else. **Inclusive Sans** Regular and Italic is everything else, labels
included. Both are self-hosted and OFL. A third family is a third voice, and the site has two
things to say.

**The scale is seven steps and every size on the site is one of them**, fluid with `clamp()`
so no breakpoint restates a size:

| Step | Size | Line-height | Where |
|---|---|---|---|
| display | `clamp(2.5rem, 1.5rem + 5vw, 5rem)` | 1.0 | The hero wordmark only (Home). |
| h1 | `clamp(2rem, 1.4rem + 2.6vw, 3rem)` | 1.15 | One per page, naming the page. |
| h2 | `clamp(1.5rem, 1.2rem + 1.4vw, 2rem)` | 1.2 | Page sections; Research themes. |
| h3 | `clamp(1.2rem, 1.08rem + 0.55vw, 1.45rem)` | 1.15 | A person's name on a card. |
| body | `clamp(1rem, 0.94rem + 0.28vw, 1.125rem)` | 1.6 | Prose, bios, roster names. |
| small | `clamp(0.875rem, 0.85rem + 0.12vw, 0.94rem)` | 1.5 | Captions, the site note, compact rows, rosters. |
| label | `0.85rem` | 1.0 | The small-caps idiom below. |

**The measure is `38rem`, capped on every run of prose** — bios, captions and the site note
included. The content column is wider on purpose: the extra width is for grids, photographs
and rosters, not for line length.

The canon asked for 68 characters and said `68ch` until the mockup round measured it:
Inclusive Sans' zero is 0.66em, so `68ch` at body size sets about 90 characters. **The
intent is 68 characters; the implementation is a length**, because `ch` is a property of a
face rather than of the design.

**A label is bold, all-small-caps Inclusive Sans, tracked `+0.04em`, at most three words.**
That one idiom carries every recurring signpost: NAVIGATE, DARK MODE, ON THIS PAGE, the
roster's **MEMBERS / ASSOCIATES / COLLABORATORS** — three words, not the sentences "ART
members involved:" they replaced — and the People card's website line. Small caps at body weight go
muddy, so the weight is part of the idiom. **A label is never a sentence**; a signpost that
has grown into one is prose.

**Italic is for the title of a work and nothing else.** Emphasis is bold, because the one
recurring emphatic thing on the site is a status note ("On leave November 2025–2026") and
that is already bold. Never italicise a paragraph.

## Spacing and layout (canon)

**The spacing scale is nine steps on a 4px base** — `0.25 0.5 0.75 1 1.5 2 3 4.5 7` rem — and
no length in the stylesheet may be anything else, hairlines and the measure excepted.

- **Content max-width is 1200px**, centred, gutter step 4 either side.
- **Grid gutters are step 5 at medium and up, step 4 below.**
- **The navigation region** holds, in this order: the mark, the four destinations (Home,
  People, Research, Statstro), the theme switch, and on the two long pages the in-page index.
  These rules hold whether it is a left column or a top bar. It is identical and in the same
  order on all three pages; it is always words, with icons only beside words; the current page
  is marked; and it stays reachable without a long scroll back.
- **How it collapses is a condition, not a shape.** While there are four destinations it
  becomes a sticky two-row bar — mark, wordmark and the labelled switch, then the four words —
  which fits at 360px and hides nothing. At five destinations that stops fitting and the bar
  becomes one control named *Menu* that never hides the name of the page you are on. Tap
  targets in it are 44px tall.
- **A card** is a flat fill on the card surface, padding step 3, square photo at full card
  width (`aspect-ratio: 1/1; object-fit: cover`). Contents in one fixed order: photo, name,
  website label line, status note, bio. Cards in a row square off at the bottom.
  **There is one card module and every section uses it** — one grid,
  `repeat(auto-fill, minmax(16rem, 1fr))`, so two faculty fill a row at the same size as
  everybody else rather than being drawn at twice the size.
- **A narrow column turns the card into a media row**: an 88px photo beside the name, the
  website line and the status note, with the bio at the card's full width beneath. The
  condition is the column's width, not the window's. Two columns at 390px give 15–18
  characters to the line, which is why this is a row and not a second column.
- **A compact row** — the form for Collaborators and Recent Alumni — is one person per row on
  the card surface, step 2 of vertical padding, separated by space and never by a rule: the
  name as the link to their site, then their text at the small step. **It may carry a square
  thumbnail** (56px), and does wherever every entry in the section has a photo — on a page that
  is otherwise all faces, a face is how a reader finds a name. A row with a photo for some
  people and a blank for others is worse than a section with none, so it is all or nothing.
- **A roster block** is the card surface, one row per role, the label in a fixed left column
  (11.5rem at medium and up, stacked below on small) so the three rows align.
- **A figure** is full column width; its caption is the measure, small, quiet, step 3
  beneath. **An image credit is part of that caption, not of the prose**, and it is not
  italic — italic is for the title of a work.
- **A Research theme's figure sits in the right-hand column and is sticky** beside the prose
  and the roster, always on the same side: a page that alternates makes the reader re-find the
  text column once per theme. On a phone the order is heading, prose, figure, roster —
  **never a picture between a heading and its first sentence**.
- **Section rhythm** is step 7 above an `h2`, step 4 below. **Sections are separated by space,
  never by a rule.**

## Marks and lines (canon)

- **A link is underlined 1px dotted at rest and 1px solid on hover, active and focus**, in the
  link token at full strength in both states. The underline is never mixed toward its surface
  and never given alpha: a token that stops printing the same has stopped naming its role.
  Density in a link-heavy bio is a content problem, fixed in the content.
- **In a dense run of links the rest underline is structure**: 1px dotted in the quiet token,
  turning 1px solid in the link token on hover, active and focus. This applies to roster rows
  and compact rows, where the links are a list rather than a sentence and full-strength
  underlines read as a wall of periwinkle. The link token still colours the word.
- **The focus ring is 2px solid link at 2px offset, on every focusable thing, never removed.**
  Focus means "this is the thing you can act on", which is what the link token already means,
  so it is the same role and not a new one. Worst case 3.15, over the wash.
- **The theme switch carries its state three ways**: paddle position, track colour (quiet off,
  link on), and a visible text label that is also its accessible name and is never hidden. The
  paddle is the page surface.
- **A divider is 1px quiet grey**, used only where space cannot do the job.
- **An image that has not loaded shows its surface and nothing else** — no fill, no spinner, no
  icon. The `alt` text carries the meaning, so it is written to. A person with **no photo on
  file** is not an image at all: no `<img>` is emitted, and the space it would have taken is
  drawn in the card surface, which is to say not drawn.
- **Corner radius is 0 and shadow is none, everywhere.** The only borders are the link
  underline, the focus ring, the divider, and the **1.5px border of the open roster mark** —
  which is sanctioned in this document under "Roles that recur" and so is named here too.

## Iconography (canon)

**An icon appears only beside its word, never instead of it, and only for a role that recurs
across the site.** An icon that appears once is decoration.

**The grid is 24px, the stroke 2px, joins and caps round, `fill: none` everywhere, colour
`currentColor`** — so an icon inherits whatever token its text is in and cannot disagree with
it. Stroke and fill are stated once, on the `<symbol>`, and never inside a glyph; no dot,
node or core is ever filled. One idea per glyph.

**The eight Research themes are the one sanctioned icon set**, the one place iconography
earns its keep: eight recurring identities a jump index has to tell apart at a glance. They
are drawn as a *set*, in one sitting, from one grid, so they share optical weight. A ninth
drawn later, alone, will not match; the remedy is to redraw the set.

**The sparkle particle is the favicon.** The wordmark squashed to 16px is unreadable; the
particle alone, in the mark token on the page surface, is legible at every size, and this is
the only place it appears on its own. **The large app icons are the opposite case**: at 180px
and 512px there is room for the whole mark, so the apple-touch and manifest icons carry the
full ART mark in the mark token on a page-surface tile, tight-cropped to the artwork and
filling about 86% of the tile.

**The wash and the mark are never drawn on one screen.** They are the same artwork in two
tokens, and two of the same thing is not identity, it is noise. On Home the hero draws the
mark in the wash and the rail's mark stands down until the hero has scrolled past; everywhere
else there is no wash and the mark is drawn where it belongs.

Forbidden: icon-only navigation, decorative icons, emoji anywhere in the interface or the
content, filled icons, and any icon colour but `currentColor`.

## Roles that recur (canon)

| Role | Channels | Token? |
|---|---|---|
| Member / associate / collaborator | the word, plus a small square before the label: **filled** / **open** / **none** | No. Ink. |
| Current page in navigation | ink instead of link, bold, and a hairline quiet bar on the leading edge | No. |
| Current section in the in-page index | ink instead of link, bold, no underline | No. |
| A skip link | the link token on the card surface, hidden until focused | No. |
| External link | the word, plus a small arrow glyph after it, `currentColor` — on *Statstro* only | No. |
| Status note on a People card | bold body text on its own line | No. |
| Caption, site note | the quiet token, small | Yes: **quiet**. |

**The roster's second channel is fill, not hue.** Filled is inside the group, open is
affiliated, absent is outside — an order, drawn as one. The words never go away; the mark is
the second channel and never the only one.

**Only Statstro takes the external mark.** Body links here are almost all external, so a mark
on each is noise; the one external item in the navigation is the one place it says
something.

## Both themes (canon)

**A token maps between themes by lightness within one hue. The role never moves.** Deep and
saturated on the light ground, pale and desaturated on the dark. A token that would need a
*different hue* in one theme is a token doing two jobs.

**Every rule here is checked in both themes.** A screenshot in one theme is half a check;
`check_tokens.py` measures both, and a change that passes in one and fails in the other is a
failed change.

## Owner rulings (canon)

Settled 7 September 2026. Not open.

- **Collaborators and Recent Alumni are compact rows**, per the definition under Spacing, and
  they carry each person's full text at the small step. No new data field.
- **A People card gets no role line, and `data/people.json` gets no `role` field.** The card is
  photo, name, website link, status note, bio.
- **The hero is Home's alone.** People and Research open on a compact masthead — small mark,
  the wordmark, one quiet subtitle line — so the page's own `h1` is on the first screen.
- **Counts appear in the "On this page" index only**, never beside a section heading. The index
  is where "how many" is a useful thing to know; the heading is where it is clutter.
- **The large app icons are the full mark on a page-surface tile**, not the sparkle in a
  coloured square. The small favicon stays the bare sparkle.

## Settled by the mockup round (7 September 2026)

Each of these was open in the previous draft and is now closed, on evidence from three built
directions judged by three independent readers (see the design round's RECOMMENDATION).

- **Sidebar, not top bar.** A rail holding four links and a switch is 240px paying for 160px,
  which is the honest case against it. It stops being true the moment the column carries the
  in-page index — People's sections with their counts, Research's eight themes with their
  icons — at zero vertical cost. A horizontal index costs a second sticky band and is already
  at its ceiling at 1440px.
- **The topper is Home's alone**, and becomes a hero of the mark in the wash with the wordmark
  as real HTML text over it, not SVG `<text>`. It put `h1` at roughly y=390 on the inner pages;
  the masthead puts it at y=170.
- **The in-page index lives in the rail**, and at narrow widths becomes a native `<details>`
  disclosure directly under the `h1`. The current section is marked by a 1px probe line: the
  last section whose top has crossed it, the first if none has. Exactly one is ever current.
  With no JavaScript the index is a plain list of working anchors.
- **The mobile collapse is a two-row sticky bar** — see the condition under Spacing.
- **People card density on phones is a media row**, not two columns — see the card rules under
  Spacing. It was measured, not judged.
- **The repeated "Personal Website" line becomes the website label line**, in the small-caps
  label idiom. It is still a real, dotted, link-token link; it is no longer a body-size
  sentence repeated fifty times. The fix is in the card template, as the canon required.
- **The wash and the link keep sharing two hexes across themes.** Within one theme no hex
  carries two roles, which is the rule that matters, and the wash is now confined to a single
  element on a single page. What the sharing risked — the two being confusable — is answered
  instead by the rule that the wash and the mark are never on one screen.

## Pending

Nothing. Every question this document has asked has been answered above. A new one goes here
in the same commit as the change that raises it.
