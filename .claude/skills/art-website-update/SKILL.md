---
name: art-website-update
description: Use when the user asks to update the ART website / astrostatuoft.com — walks the 12-section checklist (home blurb, group photo, Statstro, footer date, the five People categories, research themes, nav), asking what changed in each. People edits go in data/people.json; run scripts/audit_people.py first and last.
---

# ART Website Update Checklist

Walk the sections below **in order**, asking the user what (if anything) has changed in each. People
edits go in `data/people.json`; Home and Research are hand-written HTML.

Run the audit **before** you start walking — it tells you what's already known to be wrong, so you
can lead each affected section with a concrete question instead of an open one:

```bash
python3 scripts/audit_people.py
```

It reports stale year-of-study labels, roster/Research drift, missing photos, and how far behind the
footer date is. Run it again at the end; everything except known-and-accepted items should be clear.

## Before you start

Confirm Git LFS is active, or every image you look at is a pointer stub (see "Photos" below):

```bash
git lfs install --local && git lfs pull
```

To see when each area genuinely last changed — use this instead of trusting any hand-kept log:

```bash
for f in ejs/pages/home/body.html ejs/pages/research/body.html data/people.json; do
  printf '%-32s %s\n' "$f" "$(git log -1 --format='%ad  %s' --date=short -- "$f")"
done
```

Note `data/people.json` only dates from the migration commit; for older People history use
`git log --follow -- ejs/pages/people/body.html`.

## The checklist

| # | Section | Where | What to ask about |
|---|---------|-------|-------------------|
| 1 | **Home — welcome blurb** | `ejs/pages/home/body.html` | Any change to how the group describes itself; links to Research/People |
| 2 | **Home — group photo** | `ejs/pages/home/body.html` + `static/` | Is there a newer group photo? The `<figcaption>` names everyone left-to-right — it must match both the photo and the current roster |
| 3 | **Home — Statstro** | `ejs/pages/home/body.html` | Was there a new Statstro? Update the blurb and swap in the latest workshop photo + caption |
| 4 | **People — Faculty** | `data/people.json` | Title changes, leave notes (e.g. `<b>On leave November 2025-2026.</b>`), new affiliations |
| 5 | **People — Postdocs** | `data/people.json` | Arrivals; departures (move to Recent Alumni, #8); fellowship name or host changes |
| 6 | **People — Grad Students** | `data/people.json` | New students (set `cohort`); graduations (→ Recent Alumni); the audit handles year-of-study bumps |
| 7 | **People — ART Associates / Collaborators** | `data/people.json` | Affiliated researchers and collaborators joining or leaving |
| 8 | **People — Recent Alumni** | `data/people.json` | Anyone who left since the last update. Rewrite the bio to lead with where they went, and add the credential suffix to the name |
| 9 | **Research — theme text** | `ejs/pages/research/body.html` | New or retired research directions; any theme blurb that no longer reflects the work |
| 10 | **Research — member lists** | `ejs/pages/research/body.html` | The three "involved" lists per theme. **Every roster change in #4–8 needs a matching edit here** — this is the most common miss; the audit catches departures but not "should X now be listed on this theme?" |
| 11 | **Nav / external links** | `ejs/main.ejs` | Sidebar nav (Home / People / Research / Statstro) |
| 12 | **Home — footer date** | `ejs/pages/home/body.html` | The small-print "It was last updated \<date\>." — **bump this last, every time** |

## Person entries (`data/people.json`)

```jsonc
{
  "name": "Kevin McKinnon",
  "image": "KevinMcK_headshot.jpg",   // filename in static/, or null if there's no photo
  "alt": "A picture of Kevin McKinnon.",
  "cohort": 2022,                     // grad students only; calendar year they started
  "paragraphs": [
    "<a href=\"https://www.kevinmckinnon.com\">Personal Website</a>",
    "Kevin is an <a href=\"...\">Eric and Wendy Schmidt AI in Science Postdoctoral Fellow</a> ...",
    "Kevin also works closely with <a href=\"...\">Aviad Levis</a>."
  ]
}
```

Conventions used throughout the file:

- **Paragraph order**: personal-website link → status note → bio → optional "also works closely
  with ..." / "also collaborates closely with ...".
- `paragraphs` are emitted **verbatim** inside `<p>` — inline HTML is intentional and unescaped.
  Keep `href`s quoted.
- Append to the right `sections[].people` array; array order is render order.
- **`cohort` is metadata only** — it never renders. It exists so the audit can compute the correct
  year-of-study each September. Set it on every new grad student.
- **Alumni names carry a credential suffix**: `"Samantha Berek (Ph.D. '25)"`,
  `"Michael Walmsley (PDF '23-25)"`. Add it when moving someone to Recent Alumni and rewrite the bio
  to lead with their destination ("Sam is now an NSF Fellow at ...").

### Moving someone to Recent Alumni

1. Cut the entry from its current section and append it to the `Recent Alumni` section.
2. Add the credential suffix to `name`; drop `cohort`.
3. Rewrite the first bio paragraph as "X is now ..." — where they went, not what they studied here.
4. Remove them from every Research theme list (#10). The audit flags this if you forget.

## Photos (Git LFS)

`static/` is Git LFS-tracked (`*.jpg`/`*.svg`/`*.ico`/`*.ttf`). **LFS must be active before you
touch an image** — otherwise a new file commits as a ~130-byte text pointer and renders broken for
everyone, while the build still reports success. Fresh containers often lack git-lfs:

```bash
apt-get install -y git-lfs && git lfs install --local && git lfs pull
find static ico ttf -type f -exec sh -c 'head -c 40 "$1" | grep -q git-lfs.github.com && echo "POINTER: $1"' _ {} \;
```

The check should print nothing. If it lists files, LFS did not fetch and any preview is wrong
(broken favicon, fallback fonts, missing headshots).

Adding a headshot:

1. Put the file in `static/` — a reasonably sized JPG, ideally square, matching the ~144px
   thumbnails already there.
2. Set `image` and `alt` in the person's entry (`alt` reads "A picture of \<Full Name\>.").
3. `git add static/<file>`, then confirm `git lfs ls-files | grep <file>` lists it.

## Finishing up

```bash
python3 scripts/audit_people.py               # should be clear, bar known exceptions
npm run build                                 # must succeed
python3 -m http.server 8000 --directory dist  # eyeball the changed pages
```

Bump the footer date (#12), then commit and push. CI (`build-check.yaml`) builds every PR and
non-`main` branch; merging to `main` triggers `build-site.yaml`, which publishes `dist/` to
`gh-pages` and updates astrostatuoft.com. **Never commit `dist/`.**
