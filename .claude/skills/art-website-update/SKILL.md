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

It reports stale year-of-study labels, roster/Research drift in both directions, advisers of current
members who are missing from Collaborators, Research names left unlinked or written two different
ways, roster blocks out of order, missing photos, and how far behind the footer date is. Run it
again at the end; everything except known-and-accepted items should be clear.

**Use `--as-of` when the update targets the coming academic year.** Year-of-study labels roll over
in September. Doing an August update means writing labels for the year that has not started, and the
plain audit will then report all of them as wrong. Pin it to the year you are writing for:

```bash
python3 scripts/audit_site.py --as-of 2026-09-15
```

Otherwise you will report a pile of findings that are not findings, and — worse — be tempted to
"fix" correct labels back to the outgoing year.

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

### Row 11: the Research page

Each theme carries three lists — "ART members involved", "ART associates involved", "Collaborators
include" — repeating each person's name and link. There is **no shared data** with
`data/people.json`; that side is hand-written HTML, so every roster change in #4-10 has to be
mirrored here by hand. Two scripts do the mechanical part; the rest is judgment and belongs to the
user.

**Walk one theme at a time, and show the roster and the draft text together.** Josh asked for this
explicitly: seeing the people and the prose side by side is what makes it possible to say "that
sentence is too specific to what Duo and Ronan do" or "Maria doesn't belong here". Do not present
eight themes at once, and do not present rosters and prose in separate passes.

**Propose, don't ask.** Never ask which themes a person belongs to. Run the fit scan, read the bio,
and propose with the evidence quoted:

```bash
python3 scripts/theme_fit.py                 # every theme, both directions
python3 scripts/theme_fit.py Galaxies        # just one
```

It reports `MISSING` (bio uses the theme's vocabulary, person is not listed) and `THIN` (listed, but
the bio says nothing on the theme). Both directions matter — `MISSING` found Aviad Levis absent from
the AI theme despite being the most AI-central person on the page, and `THIN` is what exposed Maria
Drout sitting on Galaxies with a bio entirely about supernovae. **It is a prompt, not a verdict**:
keyword presence is not membership. Read the quoted phrase, decide, then take it to the user with
the evidence attached so they can correct rather than recall.

When a theme is renamed or rescoped, update its entry in `THEME_WORDS` in that script — otherwise it
quietly stops finding anything.

### Theme prose: the house style

This is where the most rework happened in one session, in both directions. Two failure modes, and
they pull opposite ways:

**Do not fragment the taxonomy.** The themes are deliberately broad and a little non-standard so the
site reads to astronomers *and* statisticians rather than to one field's specialists. Splitting a
theme into subfield labels ("Cosmology and Large-Scale Structure", "Dust and the ISM") makes it
narrower and more astronomy-coded, which is exactly wrong. If anything the pressure should run
toward **consolidation**. Josh on this: *"the whole point of the category is that this site is
interdisciplinary... what you seem to have done is just kind of fragmented and sliced them a bit,
which I think is actually the wrong move."*

**Do not write dense methodology prose.** Theme text is a general overview in plain language, not a
technical abstract. A paragraph of abstract capability-speak that "doesn't really say very much" is
an overcorrection, not a fix. Prefer concrete nouns and short sentences. Avoid in-field jargon
("quenching") unless the sentence explains it.

Titles are **terse** — `Inference`, `Galaxies`, `Transients` — with `AI for Scientists` the one
deliberate exception, because it states why the theme exists.

**Structural defect to look for: two closers bolted together.** When a theme has been broadened or
merged, the new material tends to get *appended* with its own "members of the ART do X" sentence,
leaving the paragraph with two endings and a visible seam ("The same question scales up."). This
happened on The Milky Way, Dark Matter & Cosmology and Transients. The fix is to **reweave into one
closer**, not to append. Symptom to grep for: two sentences beginning "Members of the ART" or "We
use and develop" in one paragraph.

**The text must cover its own roster.** After settling a theme's people, re-read the prose and ask
whether each person's kind of work is visible in it. Transients failed this badly — the heading said
Transients, the roster held SETI and supernovae people, and every sentence was about fast radio
bursts. Two of five people were invisible in their own theme.

**Technical detail outlives the person who did it.** Naming a specific method ties the page to
whoever ran it. `log-Gaussian Cox Processes and inhomogeneous Poisson Processes` sat in *two* themes
for a year after the student who used them had left. When someone departs, grep the Research page
for their **methods and objects**, not just their name.

Broad method families ("hierarchical Bayesian models") age better than specific ones and still
signal to statisticians, which is the audience half that named methods are there to reach.

### Removing a person is a multi-place edit

Dropping someone is never one deletion. Work the list:

1. Their entry in `data/people.json`.
2. **Other people's bios** — the trailing "also works closely with ..." lines name them.
3. **Every Research theme** they appear on (the audit lists these).
4. Their photo in `static/`.

Removing Pratika Dayal touched all four across five places. And check what the removal *orphans*:
taking her out left Haowen Zhang with no stated connection to the group at all, since her line was
his only one. A tie-line is optional — several associates have none — but losing the last one
silently is a regression worth flagging to the user rather than deciding alone.

### Occasional: reviewing the theme taxonomy itself

**Not part of every update.** The eight themes and their titles are stable; walking rosters and prose
is the routine job. Reopen the taxonomy only on a real trigger:

- a theme's roster has fallen to two or three people, or grown past about twenty
- several new arrivals share a research area that no theme names
- a whole line of work has left with a departing member
- the user asks

If it is triggered, research first — what has the group actually published recently? — and bring
evidence, not instinct. A roster-overlap number ("these two themes share seven people, Jaccard 0.50")
argues a merge far better than an opinion does. Then propose **consolidation or a rename**, not new
subdivisions, and re-read "Theme prose" above before drafting.

After any roster change, re-order the page by size:

```bash
python3 scripts/sort_themes.py            # report
python3 scripts/sort_themes.py --apply    # rewrite
```

Sorted by **total** roster size (members + associates + collaborators), largest first, so a theme
with many outside collaborators is not buried for having fewer people inside the group. Ties keep
their order, so it is idempotent.

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

## Cross-check against the faculty members' own sites first

`joshspeagle.github.io` carries `sections.mentorship.menteesByStage` in `assets/data/content.json`,
listing every current mentee with supervision type, co-supervisors, project and awards. It is the
single best source for who *should* be on the ART page, and it is usually more current than the ART
site. Read it before asking who joined:

```bash
python3 - <<'PY'
import json, re
c = json.load(open('../joshspeagle.github.io/assets/data/content.json'))
m = c['sections']['mentorship']['menteesByStage']
for stage, v in m.items():
    if stage == 'completed' or not isinstance(v, list):
        continue
    for e in v:
        print(f"{stage:16} {re.sub(r'<[^>]+>', '', e.get('name','')):32} {e.get('timelinePeriod','')}")
PY
```

Compare that against `scripts/roster.py` output. Differences run both ways and both are meaningful:
someone on the personal site but not on ART is usually a missing arrival; someone on ART but not on
the personal site is usually fine (Josh is not their supervisor). The same file supplies co-supervisor
names, project descriptions and fellowship names for drafting an entry, and its `news` section often
explains a departure — an alumni destination is frequently already written there.

Note the reverse direction too: people added to ART may still be missing from the personal site.
Collect those as you go and hand Josh the list at the end.

**Check Gwen Eadie's site as well.** The ART has two faculty members, and a large share of the group
is co-supervised by Gwen rather than Josh — several members' entries name her and not him. Josh's
mentorship data only covers his own mentees, so anyone supervised solely by Gwen will not appear
there at all and is invisible to the check above. Her site is
<https://www.astro.utoronto.ca/~eadie/>, which carries a students/group listing; it is hand-written
rather than structured data, so read it rather than parsing it.

Between the two sites you should be able to account for every current member. Anyone on the ART page
who appears on neither is worth querying — they may be an associate or collaborator rather than a
supervised member, or they may be stale.

## Verify existing bios against their own websites

Ask before spending the tokens, but this reliably finds drift, especially for postdocs and
affiliated researchers whose fellowships turn over. Dispatch a subagent per section rather than
checking by hand:

> Fact-check these N biographies against the person's own website, department profile and recent
> papers. Report only discrepancies, with a source URL for each. Do not rewrite. Flag: position and
> institution no longer current, a named fellowship that has ended, research description that no
> longer matches, and any personal website not currently linked. Be careful not to confuse people
> who share a name.

Tell it explicitly not to flag the year-of-study labels, which you have just deliberately bumped.

**Verify anything it reports before acting on it.** Two of its findings in one session were real
(a member had moved country; another's listed interest was actually past undergraduate work), but
it also reported an unlinked personal website that turned out to be an empty JavaScript shell, and
supplied Ph.D. details that were not on the person's own site.

## Sources go stale, including people's own sites

A personal site is authoritative for what someone claims, not for whether it is current. Seen in a
single session: a CV listing a finished postdoc as "present"; a student's own site a year behind on
year-of-study; a departmental profile still listing someone who had moved institutions. When Josh
contradicts a website about his own group, he is right.

Some sites refuse automated requests. A browser user-agent fixes most:

```bash
curl -sS -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 \
  (KHTML, like Gecko) Chrome/120 Safari/537.36" "$URL"
```

That recovers sites returning 403 to a plain fetch. LinkedIn (HTTP 999) and some department pages
stay blocked regardless.

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

Finding the image URL is often the fiddly part. Grepping the landing page for `<img>` can miss it,
because academic site templates keep the portrait somewhere else:

| Template | Where the portrait lives |
|---|---|
| Hugo (Wowchemy/Academic) | `/authors/admin/avatar_hu_<hash>.jpg` — note **`authors`**, plural, not `/author/` |
| Jekyll / plain | usually `/images/…` or `/assets/…`, linked from the landing page |
| Department profile | often blocks automated requests (Princeton returns 403) |
| LinkedIn | **not retrievable** — returns HTTP 999 to any unauthenticated client, so the photo cannot be fetched here even though it loads in a logged-in browser |

When a photo exists only somewhere unreachable, the fastest route is to ask the user to download it
and hand you the local path, then run `add_headshot.py` on that file — the processing is identical.

A screenshot of a **circular** profile photo can be recovered rather than rejected. Find the circle
by thresholding away the black surround and the phone's status bar, then crop the largest square
that fits *inside* the circle (side = radius x sqrt2), inset a few percent so antialiased edge
pixels do not leave dark wedges in the corners. Check the four corner means before accepting it —
a corner mean near zero means the square has escaped the circle and needs shrinking or shifting.
For someone just joining, asking them for a headshot they are happy with is usually better than
lifting a personal profile picture.

If a portrait is already square and smaller than 500px, pass `--size <its edge>` rather than
upscaling — enlarging past the source resolution just softens it.

Not everyone has a usable photo online. If you genuinely cannot find one, set `"image": null` and
tell the user it needs supplying rather than substituting something unsuitable like a GitHub avatar.
The audit lists entries with no photo, so it will not be forgotten.

Confirm LFS picked the file up, or it commits as a pointer and renders broken:

```bash
git add static/first_last.jpg && git lfs ls-files | grep first_last
```

**5. Anything still unconfirmed goes back to the user explicitly** — the exact fellowship title, a
graduation year, a date range. Do not quietly guess a credential that will sit on a real person's
public entry; say which parts are inferred and from what.

Existing members get the same treatment when their situation changes: a photo can be refreshed from
their site the same way, and a fellowship ending should be researched rather than assumed.

## Section conventions worth knowing before you edit

**Collaborators is alphabetical by surname, and the surname is not always the last word.**
Vianey Leos Barajas files under **Leos Barajas**, not Barajas. Sorting the list by its last token
silently moves her. Insert new entries at the right position rather than re-sorting the section.

**Only current members carry a trailing "also works closely with ..." paragraph.** Alumni entries
are a single bio paragraph (plus the website link). When moving someone to alumni, fold any
collaboration worth keeping into the bio in the past tense — dropping it can leave a collaborator
with no reference anywhere on the People page.

**A departure orphans a photo.** Remove the file from `static/` too; the audit lists unreferenced
files, and stale headshots accumulated there for years before this was noticed.

**Paragraphs are emitted verbatim, and the file writes `&` directly, not `&amp;`.** Easy to get
wrong when drafting; the audit now checks for it.

**Where a visiting or informally-supervised researcher goes.** ART Associates, not Graduate
Students, even when they are a doctoral student: the precedent is a Ph.D. candidate under informal
supervision listed there, and the section already carries people registered at other institutions.
Graduate Students is for students registered at Toronto and supervised within the group. Lead such
an entry with the home institution so the arrangement is unambiguous.

See **Section scope** above for which career stages belong in which section.

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

## Editing hand-written HTML safely

Both `body.html` files are hand-wrapped at ~120 columns, so a phrase you are certain of will often
not match the file: the line break lands somewhere you did not predict. Read the exact bytes first
rather than reconstructing them from memory:

```bash
sed -n '158,180p' ejs/pages/research/body.html        # and `| cat -A` if whitespace is in doubt
```

Then make every replacement assert it matched exactly once, and write only after all of them
succeed, so a bad guess changes nothing instead of applying half an edit:

```python
for old, new in edits:
    assert s.count(old) == 1, ('MISS', s.count(old), old[:70])
    s = s.replace(old, new)
open(path, 'w').write(s)      # after the loop, never inside it
```

Two traps worth naming. Splitting a roster line on commas cuts **inside** multi-line `<a>` tags and
makes linked names look bare — collapse the anchors first. And when replacing text inside a
paragraph, check for embedded links in the span you are rewriting; several theme paragraphs carry
`<a>` on ordinary words, and a careless rewrite drops them silently.

## Theme images

One per theme in `static/`, referenced from `ejs/pages/research/body.html`, square and ~500px, LFS
like every other image. Match the existing 48-88 KB range.

**An image can outlive the work it depicts.** `research_udg.jpg` showed an ultra-diffuse galaxy long
after the student whose work it illustrated had left. When a theme is rescoped or a line of work
ends, check the picture too, not just the prose.

Sourcing: NASA and Chandra imagery is public domain and the safest default; ESA/Hubble is CC BY 4.0;
ESA mission imagery is often CC BY-SA 3.0 IGO, which carries share-alike strings. Take the highest
resolution available, crop square around the subject, then downsample:

```python
im = Image.open(src)                       # crop a centred square, then
im.crop(box).resize((500, 500), Image.LANCZOS).save(dest, quality=88, optimize=True)
```

Keep the full credit line even when it is long — page credits elsewhere are short, but attribution
is the one place to be verbose rather than tidy. Confirm the file staged as an LFS pointer:

```bash
git add static/<file> && git cat-file -p :static/<file> | head -1   # must say git-lfs spec
```

## Finishing up

```bash
python3 scripts/audit_site.py --as-of <target>  # clear, bar known exceptions
python3 scripts/test_audit.py                   # the audit's own regression tests
python3 scripts/theme_fit.py --quiet            # nothing left unexplained
python3 scripts/sort_themes.py                  # themes still in size order?
npm run build                                   # must succeed
python3 -m http.server 8000 --directory dist    # eyeball the changed pages
```

Anything the audit still reports and you have deliberately decided to leave should be recorded
rather than remembered — `ADVISER_NOT_COLLABORATOR` in `audit_site.py` is the pattern: an explicit
exemption with a one-line reason and a date, so the finding stops recurring and the decision stays
visible.

Bump the footer date (#12), then commit and push. CI (`build-check.yaml`) builds every PR and
non-`main` branch; merging to `main` triggers `build-site.yaml`, which publishes `dist/` to
`gh-pages` and updates astrostatuoft.com. **Never commit `dist/`.**
