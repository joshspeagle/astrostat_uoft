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
| 2 | **Home — group photo** | `ejs/pages/home/body.html` + `static/` | *Is there a newer group photo?* Swap the image now. **Defer the caption to #12** |
| 3 | **Home — Statstro** | `ejs/pages/home/body.html` | Was there a new Statstro? Update the blurb and swap in the latest workshop photo + caption |
| 4 | **People — Faculty** | `data/people.json` | Title changes, leave notes, new affiliations |
| 5 | **People — Postdocs** | `data/people.json` | Arrivals; departures (→ #10); fellowship or host changes |
| 6 | **People — Graduate Students** | `data/people.json` | **Ph.D. *and* Masters students.** New students (set `cohort`); graduations (→ #10). The audit supplies the year-of-study bumps — confirm them rather than asking |
| 7 | **People — Undergraduates** | `data/people.json` | Current undergraduate students. **Listed while current only** — when they finish they are removed, *not* moved to Recent Alumni |
| 8 | **People — ART Associates** | `data/people.json` | Affiliated researchers joining or leaving |
| 9 | **People — Collaborators** | `data/people.json` | Collaborators joining or leaving (the largest section, and the slowest-changing) |
| 10 | **People — Recent Alumni** | `data/people.json` | Ph.D. and postdoc departures since the last update. See "Moving someone to Recent Alumni" |
| 11 | **Research — themes & member lists** | `ejs/pages/research/body.html` | Theme prose first, then the three "involved" lists. **Propose, don't ask** — see below |
| 12 | **Home — group photo caption** | `ejs/pages/home/body.html` | *Deferred from #2.* Only rewrite it if the photo changed — a caption describes the photo, not the current roster, so it may legitimately name people who have since left |
| 13 | **Wrap-up** | `ejs/main.ejs` | Any new pages or changed external links in the sidebar nav. Then the footer date |

### How to walk a People row: list first, then ask

Do **not** open a People section with "has anything changed?" — that asks the user to recall a
roster from memory. Print the current section first, then ask for additions and removals against
that list:

```bash
python3 scripts/roster.py "Postdoctoral Researchers"   # or: roster.py postdoc
python3 scripts/roster.py                              # every section
```

Each entry shows the person's name, a one-line summary of their stated role, their `cohort` if set,
and a `[NO PHOTO]` marker. Reading the list back is what surfaces the people who quietly need
moving, and it makes "add these two, drop that one" a much easier answer than an open question.

Work one section at a time and settle it before moving to the next. Sections done earlier feed the
later ones — Research theme lists (#11) and the group-photo caption (#12) both depend on the final
roster.

### Section scope (set June 2025, revised August 2026)

- **Recent Alumni is Ph.D. and postdoc level only.** Undergraduate and Masters-level people are
  never given alumni entries — when they finish, their entry is simply removed. The audit flags any
  `(B.Sc. ...)` / `(BA ...)` entry that appears in Recent Alumni.
- **Undergraduates are listed while current.** The section was dropped in June 2025 and restored in
  August 2026.
- **Graduate Students covers Ph.D. and Masters students** in one section.

### Row 11: propose, don't ask

Each of the 8 themes carries three lists — "ART members involved", "ART associates involved",
"Collaborators include" — repeating each person's name and link. There is no shared data with
`data/people.json`; it is hand-written HTML on that side, so every roster change in #4–10 has to be
mirrored here by hand.

Don't ask the user which themes a person belongs to. Instead:

- For each person **added** in #4–9, read their bio and **propose** the themes that fit, quoting the
  phrase that motivated each suggestion. Let the user correct rather than recall.
- For each person **removed** in #10, list the exact themes they currently appear in (the audit
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

Applies to **Ph.D. students and postdocs only**. Masters and undergraduate students are removed
outright when they finish — they do not get alumni entries.

1. Cut the entry from its current section and append it to the `Recent Alumni` section.
2. Add the credential suffix to `name`; drop `cohort`.
3. Rewrite the first bio paragraph as "X is now ..." — where they went, not what they studied here.
4. Remove them from every Research theme list (#10). The audit flags this if you forget.

## Adding a new person: do the legwork before asking

When the user names an arrival, they will usually give you a name, a rough title and a supervisor.
That is the starting point, not the entry. Research the rest yourself and bring back a finished
draft — a title the user half-remembers is not good enough to publish, because fellowship names are
official and appear on the live page.

**1. Confirm the official fellowship or position title.** Search for the actual programme. The user
may hedge ("I believe Research Excellence Fellow?") — verify it. The University of Toronto
[Research Excellence Postdoctoral Fellows Program](https://www.sgs.utoronto.ca/awards/research-excellence-postdoctoral-fellows-program/),
[Arts & Science Postdoctoral Fellowship](https://www.artsci.utoronto.ca), Dunlap, CITA (including
CITA National), and Eric and Wendy Schmidt AI in Science are all distinct, and each has a canonical
name and URL worth linking.

**2. Find their personal website.** Nearly everyone has one; it is the first paragraph of the entry
by convention. Search their name plus institution.

**3. Draft the blurb from primary sources.** Their own site, department profile, or Google Scholar.
Cover: current title and where, who they are co-supervised by, research focus in one or two
sentences, and prior degrees. Match the length of neighbouring entries — three to five sentences.
Do not pad.

**4. Get a headshot.** Take it from their personal or department website where one exists, and
process it to match the existing thumbnails (square, ~500px, well under 244 KB):

```bash
python3 scripts/add_headshot.py <url-or-path> static/first_last.jpg --anchor 0.1
```

`--anchor` sets where the square sits vertically in a taller-than-wide image: `0.0` flush to the
top, `0.5` centred, `1.0` bottom. Portraits usually want a low value since faces sit high in frame.
There is no face detection — **always open the result and look at it** before committing.

Not everyone has a usable photo online. If you cannot find one, set `"image": null` and tell the
user it needs supplying rather than substituting something unsuitable like a GitHub avatar. The
audit lists entries with no photo, so it will not be forgotten.

Confirm LFS picked the file up, or it commits as a pointer and renders broken:

```bash
git add static/first_last.jpg && git lfs ls-files | grep first_last
```

**5. Anything still unconfirmed goes back to the user explicitly** — the exact fellowship title, a
graduation year, a date range. Do not quietly guess a credential that will sit on a real person's
public entry; say which parts are inferred and from what.

Existing members get the same treatment when their situation changes: a photo can be refreshed from
their site the same way, and a fellowship ending should be researched rather than assumed.

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
