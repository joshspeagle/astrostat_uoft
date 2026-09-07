# astrostat_uoft

Source for the [Astrostatistics Research Team (ART)](https://astrostatuoft.com) website at the
University of Toronto — live at **[astrostatuoft.com](https://astrostatuoft.com)**.

Three pages (Home, People, Research), built from EJS-ish HTML partials by webpack into `dist/`,
styled with Foundation 6 + SCSS. GitHub Actions builds the site on every push to `main` and
publishes `dist/` to the `gh-pages` branch, which serves the live domain.

## Quick start

```bash
git clone https://github.com/joshspeagle/astrostat_uoft.git
cd astrostat_uoft

# Real images, fonts and icons are stored in Git LFS - without this step
# they check out as small text pointers and the site builds with broken
# headshots, a broken favicon and fallback fonts.
git lfs install --local
git lfs pull

npm ci                                       # install pinned dependencies
npm run build                                # webpack -> dist/
python3 -m http.server 8000 --directory dist # preview at http://localhost:8000
```

Requires Node 22+ (see `.nvmrc` / `engines` in `package.json`).

## Where content lives

- **People and Research pages**: edit `data/people.json` / `data/research.json` — both pages are
  generated from these files at build time. Do not hand-edit HTML for either page.
- **Home page**: hand-written HTML partial in `ejs/pages/home/body.html`.
- **Images, icons, fonts**: `static/`, `ico/`, `ttf/` — tracked with Git LFS.

`dist/` and `node_modules/` are never committed; CI builds `dist/` fresh on every publish.

## Deployment

Pushing to `main` triggers `.github/workflows/build-site.yaml`, which builds the site, validates
the output, and force-publishes `dist/` to `gh-pages` (the branch GitHub Pages serves as
astrostatuoft.com). Every pull request and non-`main` branch push also runs
`.github/workflows/build-check.yaml`, the same build plus validation without the publish step, so a
broken edit is caught before it merges rather than after it goes live.

## Learn more

For the full architecture (how pages are assembled, the People-page data pipeline, the site audit
script, helper scripts for roster/theme maintenance, and the Git LFS setup in detail), see
[`CLAUDE.md`](./CLAUDE.md). Supplementary docs, where present, live under `docs/`.
