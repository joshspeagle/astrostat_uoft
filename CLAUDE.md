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

- **People page content goes in `data/people.json`**, not HTML. See "People page" below.
- Home and Research content are hand-written HTML partials in `ejs/pages/<page>/body.html`.
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
| `body` | `ejs/pages/<page>/body.html` (hand-written) — **except People**, see below |

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
      "heading": "Faculty",
      "grid": "small-up-1 medium-up-2",   // Foundation grid classes; controls cards per row
      "people": [
        {
          "name": "Gwendolyn Eadie",
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
- `image: null` renders an `<img>` with no `src`. This is only used for entries with no photo on
  file and produces a broken image on the live page — prefer supplying one.
- Section order in the file is the render order on the page.
- `"cohort": 2022` (grad students only — the calendar year they started) is **not rendered** — it exists so
  `scripts/audit_people.py` can compute the correct year-of-study each September and flag prose that
  has gone stale. Any key the renderer doesn't know about is ignored.

### Roster audit

```bash
python3 scripts/audit_people.py            # report findings, always exit 0
python3 scripts/audit_people.py --strict   # exit 1 if anything is flagged
python3 scripts/audit_people.py --as-of 2026-09-15   # test the seasonal checks
```

Stdlib-only. Checks stale year-of-study labels, grad entries missing `cohort`, People↔Research drift
(current members on no theme, alumni still listed), entries with no photo, and the age of the home
page's "last updated" line. Not wired into CI — a mid-PR roster edit can legitimately trip it; the
`art-website-update` skill runs it at the start and end of an update instead.

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
  the ART website", plus the person-entry template and the footer date.
