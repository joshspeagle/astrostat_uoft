# CLAUDE.md

## Project Overview

Website for the **Astrostatistics Research Team (ART)** at the University of Toronto — live at
**astrostatuoft.com**. Three pages (Home, People, Research) built from EJS-ish partials by
**webpack** into `dist/`, styled with **Foundation 6** + SCSS. GitHub Actions builds on every push
to `main` and publishes `dist/` to the `gh-pages` branch.

This is a *different stack* from the personal site at `joshspeagle.github.io` (which pre-renders
static HTML with Python and commits the output). Here **`dist/` is never committed** — CI builds it.
There is no "stale build" problem and nothing to regenerate before pushing.

## Development Workflow

```bash
npm install                                  # one-time
git lfs install --local && git lfs pull      # one-time: fetch real images/fonts (see below)
npm run build                                # webpack -> dist/
python3 -m http.server 8000 --directory dist # local preview
```

- **People and Research content goes in `data/people.json` and `data/research.json`**, not HTML.
  See the two sections below.
- Home content is a hand-written HTML partial, `ejs/pages/home/body.html`.
- Never commit `dist/` or `node_modules/` (both gitignored).
- **Deployment**: push to `main` → `.github/workflows/build-site.yaml` builds and force-publishes
  `dist/` to `gh-pages`, which serves astrostatuoft.com (the `CNAME` is written by the workflow, not
  tracked in the repo).
- **CI gate**: `.github/workflows/build-check.yaml` builds on every PR and non-`main` branch. The
  publish job only runs on `main`, so this is what catches a broken edit *before* it merges.

## Architecture

### Page assembly

`webpack.config.js` defines a `pages` array (index / people / research). Each page renders
`ejs/main.ejs` — the shared shell holding `<head>`, the logo topper, the sidebar nav, the dark-mode
toggle, and the breadcrumb bar — and injects two partials:

| Partial | Source |
|---|---|
| `crumbs` | `ejs/pages/<page>/crumbs.html` (hand-written) |
| `body` (home) | `ejs/pages/home/body.html` (hand-written) |
| `body` (people) | generated from `data/people.json` by `build/render-people.js` |
| `body` (research) | generated from `data/research.json` by `build/render-research.js` |

The home partial may contain `{{LAST_UPDATED}}`, which `webpack.config.js` replaces with the date
of the last commit touching `data/` or `ejs/pages/` (`git log -1 --format=%cs`), formatted as
"September 7, 2026". It falls back to today's date when git is unavailable. Nobody types that date
by hand any more.

**Caveat:** that pathspec needs history behind the checkout. `actions/checkout` clones at depth 1
unless asked otherwise, and a lone commit is a root commit — git diffs it against the empty tree, so
every path matches and the date degrades to *the date of the build's own commit*, a CSS- or CI-only
push included. The build prints a `[last-updated] depth-1 checkout` warning when that happens, so
the degradation is visible in the Actions log rather than silent. **Adding `fetch-depth: 0` to the
checkout step in both `.github/workflows/*.yaml` is the fix.** A deeper truncated clone (this dev
container is one) answers the pathspec correctly and gets no warning.

**Gotcha:** `main.ejs` is compiled by html-webpack-plugin's default **lodash** template loader, not
by EJS, despite the file extension. In lodash templates `<%= %>` is *unescaped* interpolation (the
reverse of EJS), which is why raw HTML partials inject correctly. Partials are read as plain strings
and are **not** themselves compiled — template tags inside a `body.html` will not execute. Any
looping or data-driven markup has to happen in Node, in `webpack.config.js` or a `build/` module.

### People page (data-driven)

The People page is generated from **`data/people.json`** by `build/render-people.js`, wired into
`webpack.config.js` as a `content` generator rather than a `filename`. There is no
`ejs/pages/people/body.html` — don't recreate it.

```jsonc
{
  "title": "People",
  "intro": "The ART is made up of researchers across ...",
  "sections": [
    {
      "heading": "Faculty",                 // also the section's anchor: #faculty
      "layout": "faculty",                  // "faculty" | "cards" | "compact"
      "people": [
        {
          "id": "gwendolyn-eadie",          // stable slug; the card's anchor and the
                                            // key data/research.json rosters point at
          "name": "Gwendolyn Eadie",
          "short": "Gwen Eadie",            // optional: how Research rosters write her
          "image": "GwendolynEadie_2018.jpg",  // filename in static/; rendered as /static/<image>
          "alt": "A picture of Gwendolyn Eadie.",
          "paragraphs": [                      // raw inline HTML, rendered in order as <p>...</p>
            "<a href=\"...\">Personal Website</a>",
            "<b>On leave November 2025-2026.</b>",
            "Gwen is an Assistant Professor of Astrostatistics, ..."
          ]
        }
      ]
    }
  ]
}
```

- `paragraphs` entries are emitted **verbatim** inside `<p>` — inline `<a>`, `<b>`, `&` etc. are
  intentionally not escaped. Convention is website link first, then any status note, then the bio.
  Everything else (`title`, `heading`, `name`, `alt`) is plain text and **is** HTML-escaped.
- `id` is required and must be unique: it is the card's `id` attribute, so `/people.html#<id>` links
  to the person, and it is how `data/research.json` names them. Kebab-case the name with any
  parenthetical or credential suffix dropped (`Mairead Heiger (Ph.D. '26)` -> `mairead-heiger`).
  Ids are addresses — keep them stable; renaming one breaks any link anyone has saved.
- `short` is optional and only for people the Research rosters write differently ("Gwen Eadie" for
  "Gwendolyn Eadie"). Without it a roster uses the name minus any parenthetical — which is right for
  a credential suffix and wrong when the parenthetical *is* part of the name, so
  "Isabelle (Liyuan) Huang" carries a `short` identical to her `name` to keep it.
- `layout` is the section's intent, not its column count: `faculty` (2-up), `cards` (3-up) and
  `compact` (4-up — Collaborators and Recent Alumni, whose entries are a name and a line or two
  rather than a bio). The Foundation grid classes live in `build/render-people.js`, so the data file
  never names a breakpoint.
- `image: null` renders an `<img>` with no `src`; `js/index.js` fills those in with a flat
  palette-coloured placeholder rather than a broken image. Both renderers do this (a theme with no
  `image` behaves the same way), and `audit_site.py` lists every such entry — prefer supplying a
  real photo.
- Section order in the file is the render order on the page.
- Each section `<h2>` gets a slug id (`#postdoctoral-researchers`) and each card gets the person's
  id plus `data-section`, so both a section and a person are linkable.
- `"cohort": 2022` (grad students only — the calendar year they started) is **not rendered** — it exists so
  `scripts/audit_site.py` can compute the correct year-of-study each September and flag prose that
  has gone stale. Any key the renderer doesn't know about is ignored.

### Research page (data-driven)

The Research page is generated from **`data/research.json`** by `build/render-research.js`, wired
into `webpack.config.js` the same way as People. There is no `ejs/pages/research/body.html` —
don't recreate it.

```jsonc
{
  "title": "Research",
  "intro": ["raw HTML paragraph, rendered as <p>...</p>"],
  "themes": [
    {
      "id": "dark-matter-and-cosmology",  // anchor (#dark-matter-and-cosmology) and data-icon
      "title": "Dark Matter & Cosmology",
      "image": "research_darkmatter.jpg", // filename in static/, square
      "alt": "A composite image of the Bullet Cluster, ...",
      "credit": "X-ray NASA/CXC/CfA/...", // rendered as "Image credit: ..." under the image
      "paragraphs": ["raw HTML, verbatim, one <p> each"],
      "members":      ["gwendolyn-eadie", "joshua-speagle"],
      "associates":   ["haowen-zhang"],
      "collaborators": ["jo-bovy", { "id": "ryan-cloutier", "note": "McMaster" }]
    }
  ]
}
```

- Rosters are **ids into `data/people.json`**, never names. A name, its short form and its personal
  site are written once, on the People page; an id that names nobody **fails the build** with the
  theme and row that carry it. That is what makes the old drift between the two pages impossible
  rather than merely detectable.
- Each roster name links to `/people.html#<id>` — the person's own card — instead of off-site.
  An entry may carry a `"note"` for an affiliation shown in parentheses after the name.
- A roster row whose list is empty is not rendered. Row order is always members, associates,
  collaborators; the renderer, not the file, decides that.
- `paragraphs` and `intro` are raw HTML, verbatim, exactly as on the People page. `title`, `alt`
  and `credit` are plain text and are escaped.
- Theme order in the file is the order on the page — `scripts/sort_themes.py` maintains it.
- The renderer marks every second theme `media-flip`, stating which side its image belongs on.
  **`scss/index.scss` does not key off that class yet** — the flip still comes from an
  `:nth-child(odd)` rule counting every child of the section, intro paragraphs included, so adding
  or removing one `intro` paragraph swaps all eight images to the other side. Audit check 13 flags
  this until the rule becomes `&.media-flip`.

### Site audit

```bash
python3 scripts/audit_site.py            # report findings, always exit 0
python3 scripts/audit_site.py --strict   # exit 1 if anything is flagged
python3 scripts/audit_site.py --as-of 2026-09-15   # test the seasonal checks
```

Stdlib-only: stale year-of-study labels, grad entries missing `cohort`, People↔Research drift in
both directions (a current member on no theme, an alumnus still on one), roster ids matching nobody
on People, advisers of current members missing from Collaborators, `&amp;` where the file writes a
bare `&`, missing image files, People entries and themes with no photo, group-photo caption names vs
the roster, home-page photo recency, the `{{LAST_UPDATED}}` placeholder still being in the home
partial, duplicate or missing ids (two people or two themes sharing one, or one person listed twice
in a row), themes out of roster-size order, and whether the stylesheet still decides the side a
theme image lands on by sibling position instead of the `media-flip` class the renderer emits. Plus
an informational listing of unreferenced files
in `static/`, which is where a member removed outright (rather than moved to Recent Alumni) shows up.

Three checks that used to live here are gone, because `data/research.json` cannot express the states
they looked for: names left unlinked, one person written more than one way, and roster blocks out of
order.

Not wired into CI — a mid-PR roster edit can legitimately trip it; the `art-website-update` skill
runs it at the start and end of an update instead.

### Helper scripts

```bash
python3 scripts/roster.py [section]        # list the roster with ids, or one section, for review
python3 scripts/add_headshot.py <src> static/name.jpg [--anchor 0.1] [--size 500]
python3 scripts/sort_themes.py [--apply]   # order Research themes by roster size
python3 scripts/theme_fit.py [theme]       # theme rosters vs what bios actually say
python3 scripts/test_audit.py              # regression tests for the audit helpers
```

`theme_fit.py` cross-checks each Research theme's roster (by id) against the People-page bios in
both directions: `MISSING` (bio uses the theme's vocabulary but the person is not listed) and `THIN`
(listed, but the bio says nothing on the theme, and is long enough that it had a fair chance to).
It is a prompt, not a verdict — read the quoted evidence before acting. Update `THEME_WORDS` when a
theme is renamed or rescoped, or it quietly stops finding anything.

`sort_themes.py` reorders the `themes` list in `data/research.json` by **total** roster size
(members + associates + collaborators), largest first — total rather than members-only so a theme
with many outside collaborators is not pushed down for having fewer people inside the group. Ties
keep their existing order, so it is idempotent. `--apply` rewrites the file with the same 2-space
JSON formatting; without it the script only reports. Run it after any roster change.

`add_headshot.py` square-crops, resizes and re-encodes a local file or URL so new headshots match
the existing thumbnails. `--anchor` places the square vertically (0.0 top, 0.5 centre, 1.0 bottom);
portraits usually want a low value. There is no face detection - always look at the output.
Requires Pillow (`pip install Pillow`); everything else here is stdlib.

### Images and Git LFS

`static/`, `ico/`, and `ttf/` are tracked with **Git LFS** (`*.jpg`, `*.svg`, `*.ico`, `*.ttf` — see
`.gitattributes`). Without LFS these files are ~130-byte text pointers, and the site builds
"successfully" with a broken favicon, fallback fonts, and broken headshots.

Fresh containers (Claude Code web/remote) often lack git-lfs. Set it up first:

```bash
apt-get install -y git-lfs   # or: brew install git-lfs
git lfs install --local
git lfs pull                 # ~15 MB, fetches all 90 binary assets
```

Verify before trusting a preview or adding an image:

```bash
find static ico ttf -type f -exec sh -c 'head -c 40 "$1" | grep -q git-lfs.github.com && echo "POINTER: $1"' _ {} \;
```

Silence means everything is real. Adding a headshot requires LFS active, or the file commits as a
pointer and renders broken for everyone.

Several PNGs in `static/` are large (up to 1.8 MB) and trip webpack's asset size warning. The
warnings are pre-existing and harmless; prefer adding new headshots as reasonably sized JPGs.

### Styling

`scss/index.scss` is the entry point, importing `_global`, `_fonts`, `_lightmode`, `_darkmode`, and
`ux/_switch`. Theming is driven by `data-theme` on `<html>`, toggled by `js/index.js` and persisted
to `localStorage`. Foundation is aliased to `fdn` in webpack's `resolve.alias`.

## Task workflows (skills)

Detailed procedures live in `.claude/skills/` and load on demand:

- **`art-website-update`** — the section-by-section checklist to walk when the user asks to "update
  the ART website", plus the person-entry and theme templates for the two data files.
