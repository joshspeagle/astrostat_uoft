# docs/

Reference material for astrostatuoft.com. Read `DESIGN.md` before changing anything visual;
the rest is the record of how the September 2026 tune-up was decided, kept so the next pass
can build on it rather than rediscover it.

| Path | What it is | When to open it |
|---|---|---|
| `DESIGN.md` | The site's design canon: every colour, size, mark and space with its one role, in force. | Before any change to colour, type, spacing, icons or layout. |
| `check_tokens.py` | The palette as code. Reads the tokens from `scss/_tokens.scss`, measures every text/surface pair, exits 1 under the floors. CI runs it. | After any change to a colour. |
| `FOLLOW-UPS.md` | Items the owner deliberately parked (DNS, a "Recent work" section, small content questions). | When planning the next update. |
| `design/RECOMMENDATION.md` | The mockup round's verdict: three directions, three judges, the winning base, the grafts, and the canon amendments they required. | To understand why the shell looks the way it does. |
| `design/BRIEF.md`, `design/IMPLEMENTATION-BRIEF.md` | The brief the mockups were built to, with the owner's rulings, and the brief the rebuild was built to. | When something in the build seems arbitrary; the reason is usually here. |
| `design/mockups/` | The three self-contained mockup pages (open in a browser; they carry their own fonts and images), each direction's notes, and the winning direction's screenshots. | To compare a proposed change against what was chosen and what was rejected. |
| `design/icons/` | The eight theme icons and the sprite, the favicon and social-image sources, the contact sheet, and the generator: `python3 build.py` regenerates the glyphs, sprite, favicon rasters, social image and sheet from the repo's own mark and fonts, `mkappicon.py` the two app icons, and `measure.py` reports ink coverage and counter legibility at 15 and 24px. The scripts use Playwright's own Chromium; set `PW_CHROMIUM=/path/to/chrome` to override. | When a theme is added, renamed or rescoped: redraw the set, not one glyph, and re-run the sheet. Icon slugs must equal the theme ids in `data/research.json`. |
| `audit/2026-09/` | The eleven-lens audit: findings with evidence and verifier notes, the filterable report page, the link-check table, and the prospective-students proposal with its sources. | To check whether a defect is new or was known and deferred. |

Conventions carried by these files:

- **A token, once assigned, is never reassigned.** New roles get a token only when they recur.
- **Measure, don't judge.** Contrast, ink coverage and legibility are numbers; the scripts produce them.
- **Icons are a set.** A ninth glyph drawn alone will not match; the remedy is redrawing the set from
  `design/icons/build.py`.
- **The mockups are the reference, not the spec.** Where the built site and a mockup differ, the
  canon and the implementation brief say which is right.
