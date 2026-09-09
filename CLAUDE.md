# CLAUDE.md

## Project Overview

`docs/README.md` indexes the reference material: the design canon (`docs/DESIGN.md`), the palette
checker, the September 2026 audit and mockup round, the icon generator, and the parked follow-ups.

Website for the **Astrostatistics Research Team (ART)** at the University of Toronto — live at
**astrostatuoft.com**. Three pages (Home, People, Research) plus a 404, built from data files and
one HTML shell by **webpack** into `dist/`, styled with hand-written SCSS on a seven-token palette.
**No CSS framework and no JavaScript dependencies** — Foundation and jQuery were removed; the whole
bundle is ~2 KB of JS and ~12 KB of CSS. GitHub Actions builds on every push to `main` and
deploys `dist/` to GitHub Pages.

The rules the design answers to are in **`docs/DESIGN.md`** (the canon) and measured by
**`docs/check_tokens.py`**. Read the canon before changing anything visual.

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
- **Pages source (one-time prerequisite)**: *Settings → Pages → Build and deployment → Source* must
  be **GitHub Actions**. The workflow does not change repository settings, so if the source is still
  a branch the build passes and the deploy step fails. If a deploy fails with a Pages configuration
  error, check this first — it is a settings problem, not a workflow bug.
- **Deployment**: push to `main` → `.github/workflows/build-site.yaml` builds, validates, uploads
  `dist/` as a Pages artifact and deploys it with `actions/deploy-pages`. `gh-pages` is no longer in
  the loop and is not updated. The
  workflow holds `contents: read` only; the deploy job alone gets `pages: write` + `id-token: write`.
  `CNAME` and `.nojekyll` are written by the workflow, not tracked in the repo. **The custom domain
  now lives in the repository's Pages settings** — under the Actions source, GitHub does not read a
  `CNAME` file to set it (the file is still shipped, harmlessly, so the artifact mirrors `dist/`).
  After deploying, the workflow fetches the three pages from the live domain and fails the run if
  any is missing, empty, truncated or not ours — a 200 alone is not proof a page was served. It then
  checks that `https://www.<domain>/` still redirects to the apex, which also exercises the
  certificate (curl verifies it), so a DNS or cert regression on `www` shows up as a red build. That
  check names itself a domain problem rather than a bad deploy, since the site can be healthy
  while it fails. The domain is written once, as the workflow-level `SITE_DOMAIN`, and feeds both the
  `CNAME` the build ships and this check.
  Rollback: redeploy an earlier run from **Environments → github-pages**.
- **`www`**: `www.astrostatuoft.com` is a `CNAME` to `joshspeagle.github.io.`, set at the registrar
  (Squarespace, on nameservers inherited from Google Domains). GitHub issues the certificate and the
  301 to the apex once its DNS check passes; neither lives in this repo.
- **Manual runs**: `build-site` can be dispatched from the Actions tab on any ref, but the deploy
  job is guarded by `if: github.ref == 'refs/heads/main'`. A dispatch from a branch builds and
  validates without publishing, so a manual run cannot put a feature branch on the live site.
- **CI gate**: `.github/workflows/build-check.yaml` builds on every PR and non-`main` branch. The
  deploy job only runs on `main`, so this is what catches a broken edit *before* it merges. Both
  workflows check the built output with the same script, `scripts/check_build_output.sh`, so the
  publishing one can never validate less than the gating one.

## Architecture

### Page assembly

`webpack.config.js` defines a `pages` array (index / people / research / 404). Every entry carries
its `title`, `description`, canonical `url` and `nav` key, and either a `partial` (a hand-written
file), a `render` function, or an inline `body`. Each page renders `ejs/main.ejs` — the shared shell
holding `<head>`, the skip link, the icon sprite, the navigation rail, the hero or masthead, `main`
and the site footer.

| Page body | Source |
|---|---|
| home | `ejs/pages/home/body.html` (hand-written) |
| people | generated from `data/people.json` by `build/render-people.js` |
| research | generated from `data/research.json` by `build/render-research.js` |
| 404 | four lines inline in `webpack.config.js` |

The two data-driven renderers return `{ body, index }`. The `index` array is what the "On this
page" list is built from — People's section names with counts, Research's theme names with their
icons — so the index cannot drift from the sections it points at. `build/shell.js` assembles the
shell's data-driven parts (the sprite, the site nav, both copies of the index) and reads the
palette back out of `scss/_tokens.scss` for the `theme-color` meta tags and the web manifest.

**Breadcrumbs are gone.** There are no `crumbs.html` partials; the current page is marked in the
site nav instead (ink, bold, and a hairline quiet bar on the leading edge).

`webpack.config.js` also emits `dist/robots.txt`, `dist/sitemap.xml` and `dist/site.webmanifest`
from the same `pages` array, so the URL list cannot fall behind the pages. None of the three is
hand-committed.

The home partial may contain `{{LAST_UPDATED}}`, which `webpack.config.js` replaces with the date
of the last commit touching `data/` or `ejs/pages/` (`git log -1 --format=%cs`), formatted as
"September 7, 2026". It falls back to today's date when git is unavailable. Nobody types that date
by hand any more.

**Caveat:** that pathspec needs history behind the checkout. `actions/checkout` clones at depth 1
unless asked otherwise, and a lone commit is a root commit — git diffs it against the empty tree, so
every path matches and the date degrades to *the date of the build's own commit*, a CSS- or CI-only
push included. The build prints a `[last-updated] depth-1 checkout` warning when that happens, so
the degradation is visible in the Actions log rather than silent. **Both
`.github/workflows/*.yaml` now pass `fetch-depth: 0` to their checkout step, which is the fix —
don't drop it.** A deeper truncated clone (this dev container is one) answers the pathspec correctly
and gets no warning.

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
  parenthetical or credential suffix dropped (`Mairead Heiger (Ph.D. 2026)` -> `mairead-heiger`).
  Ids are addresses — keep them stable; renaming one breaks any link anyone has saved.
- `short` is optional and only for people the Research rosters write differently ("Gwen Eadie" for
  "Gwendolyn Eadie"). Without it a roster uses the name minus any parenthetical — which is right for
  a credential suffix and wrong when the parenthetical *is* part of the name, so
  "Isabelle (Liyuan) Huang" carries a `short` identical to her `name` to keep it.
- `layout` is the section's intent, not its column count: `faculty` and `cards` both render the
  **card module** (one grid, `repeat(auto-fill, minmax(16rem, 1fr))`, so every section's cards are
  the same size), and `compact` renders **compact rows** (Collaborators and Recent Alumni: a 56px
  square photo, the name as the link to their site, then the bio at the small step). The data file
  never names a breakpoint or a column count.
- On a **card**, `paragraphs` are split by shape, not by position: a paragraph that is nothing but a
  link becomes the website label line, a paragraph that is nothing but bold becomes the status note,
  and the rest are the bio. On a **compact row** the website link becomes the name itself.
- `image: null` emits **no `<img>` at all** — a `<div class="no-photo">` in the card surface holds
  the square instead. There is no placeholder fill: the canon says an image that is not there shows
  its surface and nothing else (the teal placeholder colour is retired). A Research theme with no
  `image` simply renders no figure. `audit_site.py` lists every such entry — prefer a real photo.
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
- **Every theme image sits on the same side** — the right-hand column, sticky beside the prose and
  the roster at wide widths, and between the prose and the roster on a phone. Nothing alternates,
  so adding or removing an `intro` paragraph no longer moves any picture (the old `media-flip` /
  `:nth-child(odd)` arrangement, and audit check 13 that watched it, are both gone).
- Roster labels are the three-word MEMBERS / ASSOCIATES / COLLABORATORS, each with a filled, open
  or absent square before it — the second channel is fill, not hue.

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
the roster, home-page photo recency, the `{{LAST_UPDATED}}` placeholder still being in the site note
in `ejs/main.ejs`, duplicate or missing ids (two people or two themes sharing one, or one person
listed twice in a row), and themes out of roster-size order. Plus an informational listing of
unreferenced files in `static/`, which is where a member removed outright (rather than moved to
Recent Alumni) shows up — it reads `srcset` as well as `src`, so the panorama width variants count
as referenced.

Four checks that used to live here are gone. Three because `data/research.json` cannot express the
states they looked for (names left unlinked, one person written more than one way, roster blocks out
of order), and check 13 because the stylesheet no longer decides a theme image's side at all.

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

`static/`, `ico/` and `fonts/` hold binaries tracked with **Git LFS** (`*.jpg`, `*.png`, `*.svg`,
`*.ico`, `*.ttf`, `*.woff2` — see `.gitattributes`). **`svg/` is the exception**: its two files are
inlined into every page at build time, so they are kept out of LFS as plain diffable text — a
pointer there would break the build rather than just a picture. Without LFS these files are ~130-byte
text pointers, and the site builds "successfully" with a broken favicon, fallback fonts, and broken
headshots.

Fresh containers (Claude Code web/remote) often lack git-lfs. Set it up first:

```bash
apt-get install -y git-lfs   # or: brew install git-lfs
git lfs install --local
git lfs pull                 # ~15 MB, fetches all 90 binary assets
```

Verify before trusting a preview or adding an image:

```bash
find static ico svg fonts -type f -exec sh -c 'head -c 40 "$1" | grep -q git-lfs.github.com && echo "POINTER: $1"' _ {} \;
```

Silence means everything is real. Adding a headshot requires LFS active, or the file commits as a
pointer and renders broken for everyone.

The two home-page panoramas are the only large assets left; they ship as `srcset` width variants
and still trip webpack's 244 KiB asset warning at the top end. That warning is expected for a hero
photograph. Prefer adding new headshots as ~500px JPEGs (`scripts/add_headshot.py` does this).

`ico/` holds the identity set copied to the site root by webpack: `favicon.svg` (both themes, by
`prefers-color-scheme`), `favicon.ico`, `favicon-16/32.png`, `apple-touch-icon.png` (180) and
`icon-512.png`. The last two are the full ART mark on a white tile; the small ones are the bare
sparkle. `svg/` holds the two inlined sources — `art-mark.svg` (one fill-less path, emitted as a
`<symbol>` and `<use>`d wherever the mark is drawn) and `themes-sprite.svg` (the eight Research
glyphs, whose symbol ids must match the theme ids in `data/research.json`). `static/og-image.png`
is the 1200×630 social card.

### Styling

`scss/index.scss` is the entry point and imports, in order, `_tokens`, `_fonts`, `_reset`, `_type`,
`_layout`, `_components`, `_print`. There is no CSS framework.

- **`scss/_tokens.scss` is the only place in the repo a hex value may be written.** It holds the
  `$themes` SCSS map (seven tokens × two themes), emits them as custom properties, and carries the
  seven type steps and the nine-step spacing scale. `docs/check_tokens.py` parses that map, measures
  every pair the site draws against its floor, and fails if any other `scss/` file names a colour:

  ```bash
  python3 docs/check_tokens.py     # runs in CI too, via build-check.yaml
  ```

- **Theming.** Light is the bare `:root` default; dark is redeclared under
  `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and again under
  `:root[data-theme="dark"]`, in that order, so an explicit choice beats the OS in both directions.
  An inline script at the top of `ejs/main.ejs`'s `<head>` sets `data-theme` from
  `localStorage.theme`, falling back to `prefers-color-scheme`, **before the stylesheet loads**, so
  there is no flash. `js/index.js` keeps the switch in step, writes the choice, and follows OS
  changes while nothing is stored. `data-theme` is never hard-coded in the HTML.

- **The shell has two shapes, one element.** `.rail` is a sticky left column at 768px and up and a
  sticky two-row bar below it — the same DOM, so there is one "Site" landmark and one nav to
  maintain. `_layout.scss` places the hero/masthead, rail, `main` and footer explicitly on the shell
  grid.

- **`js/index.js` is ~150 lines of vanilla ES2015+**: the theme switch, the scrollspy (a 1px probe
  line just below the sticky bar; exactly one section is current; ordered fallback), and revealing
  the rail mark once Home's hero has scrolled past. With JS off the theme still comes out right, the
  index is a plain list of working anchors, and the rail mark is simply shown.

## Task workflows (skills)

Detailed procedures live in `.claude/skills/` and load on demand:

- **`art-website-update`** — the section-by-section checklist to walk when the user asks to "update
  the ART website", plus the person-entry and theme templates for the two data files.
