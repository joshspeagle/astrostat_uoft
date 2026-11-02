# CLAUDE.md

Instructions for agents working in `astrostat_uoft`, the website repository for the **Astrostatistics Research Team (ART)** at the University of Toronto (live at <https://astrostatuoft.com>).

For routine roster, bio, or seasonal updates, use the `/art-website-update` skill (`.claude/skills/art-website-update/SKILL.md`), which starts with `python3 scripts/propose_updates.py`.

## Affiliation & Content Conventions

- **Affiliation ordering:** Always list the **David A. Dunlap Department of Astronomy & Astrophysics** first, then the **Department of Statistical Sciences**, followed by affiliated institutes (**Dunlap Institute for Astronomy & Astrophysics**, **Canadian Institute for Theoretical Astrophysics (CITA)**, and **Data Sciences Institute**).
- **Hyperlink density:** Keep links on the `Research` page (`data/research.json`) focused on official surveys, observatories, and instruments (`Gaia`, `JWST`, `DESI`, `Rubin/LSST`, `CHIME`, `LIGO`), avoiding general-encyclopedia or pop-science explainers. In `data/people.json`, link each person's website, fellowships, external institutions, and co-supervisors/collaborators while avoiding repetitive links on UofT department boilerplate outside the Faculty section.

## Architecture & Build Pipeline

The site is a static 3-page (`Home`, `People`, `Research` + `404`) webpack 5 build where all page content is data-driven from JSON files under `data/`:

| Page | Output | Data source | Renderer |
|---|---|---|---|
| **Home** | `dist/index.html` | `data/home.json` | `build/render-home.js` |
| **People** | `dist/people.html` | `data/people.json` | `build/render-people.js` |
| **Research** | `dist/research.html` | `data/research.json` | `build/render-research.js` |
| **404** | `dist/404.html` | inline in `webpack.config.js` | `build/shell.js` |

### Key Directories & Files

- **`data/home.json`** — Structured content for the Home page: `#the-art` (intro lede and group photo figure), `#statstro-workshop` (Statstro overview and workshop photo figure), and `#joining-the-art` (intro paragraph and four `.pathway-card` entries for Graduate Students, Postdoctoral Researchers with `.fellowship-pill` items, Undergraduates, and Visiting Researchers & Collaborators).
- **`data/people.json`** — Single source of truth for the People page and Research roster lookups. Organized into 7 sections:
  - `Faculty` (`layout: "faculty"` -> 2-column `.card-grid-faculty` on desktop)
  - `Postdoctoral Researchers`, `Graduate Students`, `Undergraduate Students`, `ART Associates` (`layout: "cards"` -> `.card-grid`)
  - `Collaborators`, `Recent Alumni` (`layout: "compact"` -> `.compact-list`)
  - When `"image": null`, `build/render-people.js` renders a 2-letter monogram badge (`.no-photo-initials`) inside `.no-photo`.
  - Parenthetical CJK name suffixes (e.g. `(沈佳士)`) are wrapped in `.card-name-cjk` (`0.78em`) so faculty headings stay on a single line.
- **`data/research.json`** — Single source of truth for the Research page. Each of the 8 themes (`inference`, `stellar-evolution`, `dark-matter-and-cosmology`, `ai-for-scientists`, `the-milky-way`, `galaxies`, `transients`, `star-formation`) has `id`, `title`, `image`, `alt`, `credit`, `paragraphs`, and ID arrays (`members`, `associates`, `collaborators`). Every ID must match an entry in `data/people.json`. Themes are ordered by total roster size (`python3 scripts/sort_themes.py --apply`).
- **`ejs/main.ejs` & `build/shell.js`** — Shared HTML shell: `<head>` metadata and OpenGraph tags, inline theme-settlement script, SVG symbol sprite (`svg/art-mark.svg` and `svg/themes-sprite.svg`), sticky left navigation rail (`.rail`), Home hero banner (`.hero`), inner-page masthead (`.masthead`), `<main id="main">`, and `.site-footer` (`{{LAST_UPDATED}}` substituted from the latest git commit touching `data/` or `ejs/`).
- **`scss/`** — Stylesheets compiled into `dist/assets/index.css`:
  - `scss/_tokens.scss` — The sole file allowed to contain hex color values (`page`, `card`, `wash`, `ink`, `link`, `mark`, `quiet` in `light` and `dark` themes), verified by `python3 docs/check_tokens.py`.
  - `scss/_fonts.scss`, `scss/_type.scss`, `scss/_layout.scss`, `scss/_components.scss`, `scss/_print.scss`.
- **`js/index.js`** — Dependency-free client script (~110 lines) handling light/dark theme persistence (`localStorage.theme`) and scrollspy (`[data-spy]` / `[data-spy-for]`).
- **`static/`** — Headshots (`500×500` JPEG, tracked in Git LFS), responsive group/workshop photos (`800w`, `1400w`, `2000w`/`2400w`), theme illustrations, and `og-image.png`.

## Commands & Verification Gates

- **Install dependencies** (Node 22, see `.nvmrc`):
  ```bash
  npm ci
  ```
- **Build site to `dist/`:**
  ```bash
  npm run build
  ```
- **Run full verification suite** (token contrast + hex check, unit tests, strict content audit, and build output check):
  ```bash
  npm run check
  ```
- **Generate autonomous update proposal digest** (cross-repo sync with `../joshspeagle.github.io`, seasonal/year rollovers, audit & theme-fit summary):
  ```bash
  npm run propose
  python3 scripts/propose_updates.py --online   # also check Gwen Eadie's site & external URLs
  ```

## Maintenance Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `scripts/propose_updates.py` | Preflight discovery: diffs roster against `../joshspeagle.github.io/assets/data/content.json`, flags graduate student year-of-study rollovers (`--apply-years`), checks leave notes and seasonal wording, runs `audit_site.py` + `theme_fit.py`, and optionally checks Gwen Eadie's page and external URLs (`--online`). |
| `scripts/audit_site.py` | Cross-file consistency audit (`--strict` exits 1 on findings): checks `cohort` vs `N`-th year labels, verifies current members appear on >= 1 Research theme and alumni appear on 0, checks co-advisers against `Collaborators`, verifies image references in `static/`, checks ID uniqueness, and verifies theme size ordering. |
| `scripts/test_audit.py` | Unit tests (35 assertions) for `audit_site.py` name matching, ID validation, and academic-year rollover logic. |
| `scripts/theme_fit.py` | Compares People bios against Research theme vocabularies (`THEME_WORDS`), filtering previously reviewed non-memberships (`REVIEWED_OMISSIONS`) and domain memberships (`REVIEWED_MEMBERSHIPS`) unless `--all` is passed. |
| `scripts/roster.py` | Prints a per-person theme count matrix (`--markdown` for PR summaries). |
| `scripts/sort_themes.py` | Sorts themes in `data/research.json` by total roster size (`--apply` to write). |
| `scripts/add_headshot.py` | Crops, resizes (`500×500`), and compresses (`quality=85`) a headshot into `static/` (requires Pillow). |
| `scripts/check_build_output.sh` | Verifies all expected HTML, CSS, JS, font, icon, and image files exist and are non-empty in `dist/`. |

## Deployment & CI

- **`.github/workflows/build-check.yaml`** runs on pull requests to `main`: executes `docs/check_tokens.py`, `scripts/test_audit.py`, `scripts/audit_site.py --strict`, `npm run build`, and `scripts/check_build_output.sh dist`.
- **`.github/workflows/build-site.yaml`** runs on pushes to `main` (and daily via cron): runs all verification gates, builds `dist/`, and deploys to GitHub Pages (`astrostatuoft.com`). Never commit `dist/` or `node_modules/`.
