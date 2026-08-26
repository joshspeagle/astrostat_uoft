---
name: art-website-update
description: Use when the user asks to update the ART website / astrostatuoft.com — walks the section checklist (home blurb, Statstro, the six People categories, research themes, deferred group-photo caption, footer date), asking what changed in each. People edits go in data/people.json; run scripts/audit_site.py first and last.
---

# ART Website Update Checklist

Walk the sections below **in order**, asking the user what (if anything) has changed in each. People
edits go in `data/people.json`; Home and Research are hand-written HTML.

Run the audit **before** you start walking — it tells you what's already known to be wrong, so you
can lead each affected section with a concrete question instead of an open one:

```bash
python3 scripts/audit_site.py
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

Walk these in order. Two rows are deliberately **out of page order** because they depend on the
roster being settled first — see the notes.

| # | Section | Where | What to ask about |
|---|---------|-------|-------------------|
| 1 | **Home — welcome blurb** | `ejs/pages/home/body.html` | Any change to how the group describes itself; links to Research/People |
| 2 | **Home — group photo** | `ejs/pages/home/body.html` + `static/` | *Is there a newer group photo?* Swap the image now. **Defer the caption to #11** — it names everyone left-to-right and can't be written until the roster is final |
| 3 | **Home — Statstro** | `ejs/pages/home/body.html` | Was there a new Statstro? Update the blurb and swap in the latest workshop photo + caption |
| 4 | **People — Faculty** | `data/people.json` | Title changes, leave notes, new affiliations |
| 5 | **People — Postdocs** | `data/people.json` | Arrivals; departures (→ #9); fellowship or host changes |
| 6 | **People — Grad Students** | `data/people.json` | New students (set `cohort`); graduations (→ #9). The audit supplies the year-of-study bumps — confirm them rather than asking open-endedly |
| 7 | **People — ART Associates** | `data/people.json` | Affiliated researchers joining or leaving (7 entries) |
| 8 | **People — Collaborators** | `data/people.json` | Collaborators joining or leaving (19 entries — the largest section, and the slowest-changing) |
| 9 | **People — Recent Alumni** | `data/people.json` | Anyone who left since the last update. See "Moving someone to Recent Alumni" |
| 10 | **Research — themes & member lists** | `ejs/pages/research/body.html` | Theme prose first, then the three "involved" lists. **Propose, don't ask** — see below |
| 11 | **Home — group photo caption** | `ejs/pages/home/body.html` | *Deferred from #2.* Now that the roster is final, write or verify the left-to-right caption. The audit cross-checks the names |
| 12 | **Wrap-up** | `ejs/main.ejs` | Any new pages or changed external links in the sidebar nav (Home / People / Research / Statstro — has never changed in the repo's history). Then the footer date |

### Row 10: propose, don't ask

Each of the 8 themes carries three lists — "ART members involved", "ART associates involved",
"Collaborators include" — repeating each person's name and link. There is no shared data with
`data/people.json`; it is hand-written HTML on that side, so every roster change in #4–9 has to be
mirrored here by hand.

Don't ask the user which themes a person belongs to. Instead:

- For each person **added** in #4–8, read their bio and **propose** the themes that fit, quoting the
  phrase that motivated each suggestion. Let the user correct rather than recall.
- For each person **removed** in #9, list the exact themes they currently appear in (the audit
  reports lingering alumni) and confirm removal from each.
- Match the surrounding convention: Research uses short/familiar name forms (`Gwen Eadie`,
  `Josh Speagle`) and links to personal sites where one exists.

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
python3 scripts/audit_site.py               # should be clear, bar known exceptions
npm run build                                 # must succeed
python3 -m http.server 8000 --directory dist  # eyeball the changed pages
```

Bump the footer date (#12), then commit and push. CI (`build-check.yaml`) builds every PR and
non-`main` branch; merging to `main` triggers `build-site.yaml`, which publishes `dist/` to
`gh-pages` and updates astrostatuoft.com. **Never commit `dist/`.**
