# astrostat_uoft

Source for the [Astrostatistics Research Team (ART)](https://astrostatuoft.com) website at the
University of Toronto — live at **[astrostatuoft.com](https://astrostatuoft.com)**.

Three pages (Home, People, Research) plus a 404, built from data files and one HTML shell by
webpack into `dist/`, styled with hand-written SCSS on a seven-token palette — no CSS framework and
no JavaScript dependencies. GitHub Actions builds the site on every push to `main` and deploys
`dist/` straight to GitHub Pages, which serves the live domain.

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

**Prerequisite, one time:** the repository's Pages source must be set to **GitHub Actions** under
*Settings → Pages → Build and deployment → Source*. The workflow deliberately does not change
repository settings, so until that switch is made the build succeeds and the deploy step fails.
The custom domain is a Pages setting too — under the Actions source GitHub does not read a `CNAME`
file to set it.

Pushing to `main` then triggers `.github/workflows/build-site.yaml`, which builds the site,
validates the output, uploads `dist/` as a Pages artifact and deploys it with `actions/deploy-pages`.
There is no `gh-pages` branch in the loop any more, the workflow needs no write access to the
repository, and a deployment that does not land fails the run instead of reporting success. After
deploying it fetches the three pages from the live domain, and checks that the `www` subdomain still
redirects to the apex over a valid certificate, so a build that is green but not actually being
served cannot pass unnoticed.

Every pull request and non-`main` branch push also runs `.github/workflows/build-check.yaml`, the
same build plus validation without the deploy, so a broken edit is caught before it merges rather
than after it goes live. Both workflows validate the built output with the same script,
`scripts/check_build_output.sh`.

Rollback is a redeploy of an earlier successful run from the repository's **Environments →
github-pages** tab.

## Learn more

For the full architecture (how pages are assembled, the People- and Research-page data pipelines,
the site audit script, helper scripts for roster/theme maintenance, and the Git LFS setup in
detail), see [`CLAUDE.md`](./CLAUDE.md). The design canon — what every colour, type size and piece
of spacing means, and the script that measures it — is [`docs/DESIGN.md`](./docs/DESIGN.md).
