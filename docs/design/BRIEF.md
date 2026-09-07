# ART website — design brief (draft, pre-audit)

Owner: Josh Speagle. Site: astrostatuoft.com, three pages (Home, People, Research), built by webpack
from partials + data/people.json. This brief translates the owner's figure canon (ICONOGRAPHY.md)
into rules for a website. It will become docs/DESIGN.md in the repo.

## What the brand already is (keep — "redraw rather than redesign")

- **Mark**: "ART" in a heavy geometric sans with a diagonal streak of four-pointed sparkle stars
  crossing the letters (static/art-logo-mod.svg, single path). The four-pointed sparkle is the
  brand's *particle* — the smallest unit that still reads as ART.
- **Type**: Urbanist Bold (display) + Inclusive Sans Regular/Italic (body). Both self-hosted, OFL.
- **Hue**: periwinkle. Light theme: #2f559d (links), #91acde (logo wash), #001f4e (sidebar mark).
  Dark theme: #91acde (links), #2f559d (logo wash), #70a9ff (sidebar mark).
- **Surfaces**: flat. No border-radius, no shadows, no borders. Cards are a flat grey fill
  (#eeeeee / #333333). Links are dotted-underlined, solid on hover.
- **Neutrals**: #0a0a0a / #fefefe body, #888888 mid-grey for captions and the footer.
- The owner's personal site (joshspeagle.com) is a *different* brand (Inter + Source Serif 4,
  violet/cyan, rounded cards, glows). ART should stay distinct but borrow its *discipline*:
  tokens generated from one source, clamp() type scale, a spacing scale, aria-current nav.

## Principles carried over from the figure canon

1. **A token, once assigned, is never reassigned.** Every colour on the site carries exactly one
   role, written down. Periwinkle = ART / interactive. If teal (#82c7ce/#31767d) cannot be given
   a recurring role it is retired. A role gets a token only when it recurs.
2. **Hue is never the only channel.** Links keep an underline. State (dark mode, current page) is
   carried by text or shape as well as colour. Theme icons always sit beside their name.
3. **Restraint, deep register.** Colour covers ~1% of the page. Accents are dark and saturated in
   light mode, light and desaturated in dark mode — never bright mid-tones on both. The large
   pale-periwinkle logo wash across the top of every page is the single largest area of colour ink
   on the site and carries no information after the first visit.
4. **Measure, don't judge.** Every text/background pair has a contrast ratio recorded, at floors
   of 4.5 (text) and 3 (UI marks / large text). A script checks the tokens (the canon as code).
5. **Direct labels over legends.** Navigation and section indexes are words, with icons as a
   secondary channel. No icon-only controls except where a label would be absurd (the theme
   toggle), and there the accessible name is still the words.
6. **One idea to a panel.** A People card is: photo, name, one role line, bio. A Research theme
   is: image, prose, roster. A page has one hero, and only Home's hero is the big topper.
7. **Structure is grey at axis weight.** Rules, dividers and section markers are neutral, thin,
   and never in a token colour.
8. **Redraw rather than redesign.** Keep the mark, the fonts, flat surfaces and the dotted link.
   Change layout, hierarchy and codification. A returning visitor should recognise the site.

## Candidate roles that recur and might deserve a token (for the mockup round to test)

- Roster role on Research: member / associate / collaborator (8 themes x 3 = 24 occurrences).
  Candidate second channel: filled mark / open mark / no mark — inside the group, affiliated,
  outside — echoing the canon's own filled-vs-open convention. Words stay.
- Section identity on People (7 sections) and theme identity on Research (8 themes) — jump
  navigation needs a compact index; icons for the eight themes are the one place iconography
  clearly earns its keep. Style: 24px grid, single stroke weight, round joins, currentColor,
  one idea per glyph, drawn as a *set* so they share optical weight.
- Status notes on People ("on leave") — rare; no token, plain bold text as now.
- External vs internal links — an external-link mark on the nav item "Statstro" only; body links
  are almost all external so a mark on each would be noise.

## Known layout problems the mockups must answer

- No in-page wayfinding on two very long pages (People ~15,000px desktop, ~37,000px mobile).
- Mobile: nav + toggle consume the first screen; the switch renders broken; cards are 1-up with a
  full-width photo per person.
- The 300px topper repeats on every page; the sticky sidebar column at medium widths is narrow.
- People cards have no scannable role line; "Personal Website" is repeated 50 times as the
  first line of every card.
- Favicon is the whole logo squashed to 64px (unreadable at 16px); no SVG/apple-touch icon,
  no social preview image.

## Owner rulings (7 Sep 2026, before the mockup round)

- **The left sidebar is liked but not required.** The owner does not mind it and would keep it by
  default, but a top bar is a legitimate option if it is clearly better. The mockup round
  compares both, and the judges must say which is better *and why*, not assume either.
- **Compact rows for Collaborators and Recent Alumni are fine.**
- **No role line on People cards.** Do not add a `role` field to people.json. The card stays
  photo, name, website link, status note, bio.
