# Astrostat@UofT (`astrostatuoft.com`)

[![Build and Deploy Static Site](https://github.com/joshspeagle/astrostat_uoft/actions/workflows/build-site.yaml/badge.svg)](https://github.com/joshspeagle/astrostat_uoft/actions/workflows/build-site.yaml)

Source repository for the **Astrostatistics Research Team (ART)** website at the University of Toronto, live at <https://astrostatuoft.com>.

## Content & Data Files

All three pages are generated at build time from JSON files in [`data/`](./data):

- **[`data/home.json`](./data/home.json)** — Home page (`/`): group overview (`#the-art`), annual workshop (`#statstro-workshop`), and career-stage pathways & postdoctoral fellowships (`#joining-the-art`). Rendered by [`build/render-home.js`](./build/render-home.js).
- **[`data/people.json`](./data/people.json)** — People page (`/people.html`): Faculty, Postdoctoral Researchers, Graduate Students, Undergraduate Students, ART Associates, Collaborators, and Recent Alumni. Rendered by [`build/render-people.js`](./build/render-people.js).
- **[`data/research.json`](./data/research.json)** — Research page (`/research.html`): the 8 research themes and their member/associate/collaborator ID lists. Rendered by [`build/render-research.js`](./build/render-research.js).

## Building & Verifying Locally

Requires **Node 22** (`.nvmrc`), **Git LFS** (for photos in `static/` and fonts in `fonts/`), and **Python 3**.

```bash
git lfs pull
npm ci
npm run build   # builds the static site into dist/
npm run check   # runs token checks, unit tests, strict content audit, and build output check
```

To preview the built site locally:

```bash
python3 -m http.server --directory dist 8000
```

## Maintenance & Routine Updates

| Command | Description |
|---|---|
| `npm run propose` | Run [`scripts/propose_updates.py`](./scripts/propose_updates.py) to compare the roster against `../joshspeagle.github.io`, check seasonal/year-of-study rollovers, and summarize audit and theme-fit status. |
| `python3 scripts/propose_updates.py --online` | Also check Gwen Eadie's group page and verify all external links across `data/*.json`. |
| `python3 scripts/propose_updates.py --apply-years` | Automatically increment graduate student `N`-th year labels in `data/people.json` for the new academic year. |
| `python3 scripts/audit_site.py --strict` | Verify cross-file invariants (IDs, cohorts, theme memberships, co-advisers, and image assets). |
| `python3 scripts/theme_fit.py --quiet` | Check for unreviewed keyword matches between People bios and Research themes. |
| `python3 scripts/sort_themes.py --apply` | Reorder `data/research.json` themes by total roster size. |
| `python3 scripts/add_headshot.py <src> <out.jpg>` | Center-crop, resize (`500×500`), and optimize a new headshot into `static/`. |

See [`CLAUDE.md`](./CLAUDE.md) for architecture details and [`docs/DESIGN.md`](./docs/DESIGN.md) for the design specification.
