---
name: art-website-update
description: Use when the user asks to update the ART website / astrostatuoft.com — walks the section-by-section checklist (home blurb, group photo, Statstro, people by category, research themes, footer date), the data/people.json person-entry schema, and the People↔Research cross-check that catches most drift.
---

# ART Website Update Checklist

Walk each section below and ask what has changed. Most updates touch **`data/people.json`** (People
page) and **`ejs/pages/research/body.html`** (Research page member lists) — and a person change
almost always needs **both**.

| # | Section | Where | What to review | Last edited |
|---|---------|-------|----------------|-------------|
| 1 | **Home — welcome blurb** | `ejs/pages/home/body.html` | Intro paragraph, links to Research/People | 2025-06-28 |
| 2 | **Home — group photo** | `ejs/pages/home/body.html` + `static/` | Current photo + the `<figcaption>` naming everyone left-to-right. Check the caption still matches the roster. | 2025-09-09 |
| 3 | **Home — Statstro** | `ejs/pages/home/body.html` | Workshop blurb, most recent Statstro photo + caption | 2025-06-28 |
| 4 | **Home — footer note** | `ejs/pages/home/body.html` | The small-print "It was last updated \<date\>." — **bump this every time**. It currently lags the real edits by months. | 2025-06-26 |
| 5 | **People — Faculty** | `data/people.json` | 2 entries; leave notes / title changes | 2025-12 |
| 6 | **People — Postdocs** | `data/people.json` | Arrivals, departures (→ Recent Alumni), fellowship name changes | 2025-12 |
| 7 | **People — Grad Students** | `data/people.json` | Year-of-study bumps ("4th-year"→"5th-year"), new students, graduations | 2025-12 |
| 8 | **People — ART Associates** | `data/people.json` | Affiliated researchers not formally supervised | 2025-12-22 |
| 9 | **People — Collaborators** | `data/people.json` | 19 entries; the widest grid (`medium-up-4`) | 2025-12-18 |
| 10 | **People — Recent Alumni** | `data/people.json` | Move departures here; rewrite the bio to "X is now ..." and add the credential suffix to the name (see below) | 2025-12 |
| 11 | **Research — themes** | `ejs/pages/research/body.html` | 8 themes: blurb, image, and the three "involved" lists. **Syncing these with People is the most common miss** — see the cross-check below. | 2025-09-09 |
| 12 | **Nav / external links** | `ejs/main.ejs` | Sidebar nav (Home / People / Research / Statstro) | — |

Update the "Last edited" column as you go.

## Person entries (`data/people.json`)

```jsonc
{
  "name": "Kevin McKinnon",
  "image": "KevinMcK_headshot.jpg",          // filename in static/, or null for no photo
  "alt": "A picture of Kevin McKinnon.",
  "paragraphs": [
    "<a href=\"https://www.kevinmckinnon.com\">Personal Website</a>",
    "Kevin is an <a href=\"...\">Eric and Wendy Schmidt AI in Science Postdoctoral Fellow</a> ...",
    "Kevin also works closely with <a href=\"...\">Aviad Levis</a>."
  ]
}
```

Conventions actually used across the file:

- **Paragraph order**: personal-website link → any status note (e.g. `<b>On leave November 2025-2026.</b>`) → bio → optional "also works closely with ..." / "also collaborates closely with ...".
- `paragraphs` are emitted **verbatim** inside `<p>` — inline HTML is intentional and unescaped.
- **Alumni names carry a credential suffix**: `"Samantha Berek (Ph.D. '25)"`, `"Michael Walmsley (PDF '23-25)"`. Add it when moving someone to Recent Alumni, and rewrite the bio to lead with where they went ("Sam is now an NSF Fellow at ...").
- Add a person by appending to the right `sections[].people` array — array order is render order.
- `image: null` renders a broken `<img>`. **`J. Arturo Esquivel` is currently in this state** (no photo in `static/`) — worth fixing if a photo turns up.

## Adding a photo (Git LFS)

`static/` is Git LFS-tracked (`*.jpg`/`*.svg`/`*.ico`/`*.ttf`). **LFS must be active before you
touch an image** — otherwise a new file commits as a ~130-byte text pointer and renders broken for
everyone, while the build still reports success.

Fresh containers often lack git-lfs. Set up once per container, then confirm:

```bash
apt-get install -y git-lfs && git lfs install --local && git lfs pull
find static ico ttf -type f -exec sh -c 'head -c 40 "$1" | grep -q git-lfs.github.com && echo "POINTER: $1"' _ {} \;
```

The check should print nothing. If it lists files, LFS did not fetch and any preview you look at is
wrong (broken favicon, fallback fonts, missing headshots).

When adding a headshot:

1. Drop the file in `static/` — a reasonably sized JPG, ideally square, matching the ~144px
   thumbnails already there.
2. Set `image` and `alt` in the person's `data/people.json` entry (`alt` reads
   "A picture of \<Full Name\>.").
3. `git add static/<file>` and confirm `git lfs ls-files | grep <file>` shows it as LFS-tracked.

## People ↔ Research cross-check

Run this after any roster change. It matches on **surnames** against the plain text of the Research
page, so it copes with the two pages using different name forms and with unlinked mentions:

```bash
python3 - <<'PY'
import json, re
data = json.load(open('data/people.json'))
text = re.sub(r'<[^>]+>', ' ', open('ejs/pages/research/body.html').read())
CURRENT = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students', 'ART Associates'}
missing, stale = [], []
for sec in data['sections']:
    for p in sec['people']:
        surname = re.sub(r'\s*\([^)]*\)', '', p['name']).strip().split()[-1]
        seen = re.search(r'\b' + re.escape(surname) + r'\b', text) is not None
        if sec['heading'] in CURRENT and not seen:
            missing.append(p['name'] + '  (' + sec['heading'] + ')')
        if sec['heading'] == 'Recent Alumni' and seen:
            stale.append(p['name'])
print("Current members on no Research theme:", missing or "none")
print("Alumni still on Research (remove):", stale or "none")
PY
```

Both lists should be **empty** — that is the current state, so any output is a real finding.

Why surnames: the two pages deliberately use different name forms — Research uses short/familiar
ones (`Gwen Eadie`, `Josh Speagle`, `David Li`) while `people.json` uses full ones
(`Gwendolyn Eadie`, `Joshua S. Speagle (沈佳士)`, `David (Dayi) Li`), and some Research mentions are
plain text rather than links. Matching full names, or only `<a>` link text, yields mostly false
positives. Collaborators are excluded from the "missing" check since not all map to a theme.

## Finishing up

```bash
npm run build                                 # must succeed
python3 -m http.server 8000 --directory dist  # eyeball the changed pages
```

Then bump the home-page "last updated" date (#4), commit, and push. CI (`build-check.yaml`) builds
every PR/branch; merging to `main` triggers `build-site.yaml`, which publishes `dist/` to `gh-pages`
and updates astrostatuoft.com. **Never commit `dist/`.**
