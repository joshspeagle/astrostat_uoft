# astrostat_uoft

Source for the [Astrostatistics Research Team (ART)](https://astrostatuoft.com) website at the
University of Toronto — live at **[astrostatuoft.com](https://astrostatuoft.com)**.

Three pages (Home, People, Research) plus a 404, built from data files and one HTML shell by
webpack into `dist/`, styled with hand-written SCSS on a seven-token palette — no CSS framework and
no JavaScript dependencies. GitHub Actions builds the site on every push to `main` and publishes
`dist/` to the `gh-pages` branch, which serves the live domain.

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
- **Images, icons, fonts**: `static/`, `ico/`, `svg/`, `fonts/` — the binaries are tracked with
  Git LFS.
- **Look and feel**: `scss/` (the palette lives once, in `scss/_tokens.scss`) and `ejs/main.ejs`.
  The rules those files answer to are in [`docs/DESIGN.md`](./docs/DESIGN.md); run
  `python3 docs/check_tokens.py` after any change to colour.

`dist/` and `node_modules/` are never committed; CI builds `dist/` fresh on every publish.

## Deployment

Pushing to `main` triggers `.github/workflows/build-site.yaml`, which builds the site, validates
the output, and force-publishes `dist/` to `gh-pages` (the branch GitHub Pages serves as
astrostatuoft.com). Every pull request and non-`main` branch push also runs
`.github/workflows/build-check.yaml`, the same build plus validation without the publish step, so a
broken edit is caught before it merges rather than after it goes live.

## Learn more

For the full architecture (how pages are assembled, the People- and Research-page data pipelines,
the site audit script, helper scripts for roster/theme maintenance, and the Git LFS setup in
detail), see [`CLAUDE.md`](./CLAUDE.md). The design canon — what every colour, type size and piece
of spacing means, and the script that measures it — is [`docs/DESIGN.md`](./docs/DESIGN.md).
