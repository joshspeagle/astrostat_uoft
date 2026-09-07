# A route for prospective students and collaborators on the ART site

Notes and URLs behind everything here: `josh-sources.md`, `gwen-sources.md` (same directory).
Assessed 2026-09-07.

## (a) Assessment

**What each site offers.** Josh's site carries the whole thing. `sections.collaboration` in
`https://joshspeagle.com/assets/data/content.json`, rendered on his home page at the `#join` anchor,
is six cards covering postdocs (eleven named fellowship competitions with links), graduate students,
UofT undergraduates, Canadian undergraduates, international undergraduates, and visiting
researchers. Gwen's site has one page aimed at applicants,
`https://www.astro.utoronto.ca/~eadie/students.html`, and it is narrower than it first appears: the
graduate section is live and genuinely good — it is the only place either site explains the
*mechanism*, that both departments admit students and the supervisor is settled afterwards, that you
may apply to both, and that naming the faculty member is what routes your file to them — but the
"Prospective Undergraduate Students" block is **commented out in the HTML** (lines 91–94) and does
not render. There is no postdoc, funding, international, or visiting content on her site at all. She
already delegates the roster to us ("please see the ART website's People page"), so the pointer
currently runs one way only. Her page carries no date stamp and the CV it links is
`website_CV_Eadie_2024_09_25.pdf`.

**How current Josh's list is, and what I recommend.** Current, and I checked this rather than
trusting the stamp. `site.lastUpdated` is `2026-09-07` (today), but more to the point the
opportunities block itself was link-audited twelve days ago: commit `f723960` (2026-08-26, "Routine
content update: … collaboration") changed exactly two things in `sections.collaboration`, both
repairs of broken fellowship URLs (a mangled Arts & Science link, and Schmidt AI in Science
re-pointed to `schmidtfellows.utoronto.ca`). The six cards have been stable across the last twelve
commits to the file, and I independently re-checked sixteen of the URLs — every one resolves 200
except `datasciences.utoronto.ca/suds/`, which 403s the whole domain including its root, so that is
a bot-block on our proxy and not a dead page. **Recommendation: recreate it (DRAFT B), and point to
both sites at the end rather than instead.** Recreating is worth the maintenance cost because the
ART site is where a prospective student actually lands — Gwen's own page sends them here, and the
group has two faculty, so "see Josh's site" quietly makes the group look like one person's. But
recreate *selectively*: name five fellowships rather than eleven and drop the international-student
programs to a pointer, so the ART copy stays short enough to be maintainable and the exhaustive,
frequently-changing lists stay in the one place that is already being audited monthly. DRAFT A
remains the honest fallback if Josh would rather not maintain a second copy.

## (b) DRAFT A — minimal

**Home page.** New paragraph, after the Statstro figure and before `<p class="site-note">` in
`ejs/pages/home/body.html`:

```html
  <p>
    Prospective students, postdoctoral researchers, and collaborators are welcome to get in touch.
    Both faculty keep current information on how to join the group and what funding is available: <a
      href="https://www.astro.utoronto.ca/~eadie/students.html"><strong>Gwen Eadie</strong></a> on
    applying to the graduate programs, and <a href="https://joshspeagle.com/#join"><strong>Josh
        Speagle</strong></a> on fellowships and undergraduate research programs.
  </p>
```

**Under the Faculty heading.** One sentence:

> Both faculty supervise students in Astronomy & Astrophysics and in Statistical Sciences; their
> own sites list current openings and how to apply.

⚠ **This does not fit the People page as built.** `build/render-people.js` emits `<h2>` and then
goes straight into `<div class="grid-x …">` — there is no section-level note field, and unknown keys
are silently dropped, so adding `"note"` to the Faculty section in `data/people.json` would render
nothing. Two options: (i) a four-line renderer change accepting an optional `section.note` emitted
as a `<p>` between the heading and the grid — the clean fix, and reusable for other sections; or
(ii) append the sentence to `data.intro`, which is interpolated raw and so accepts inline HTML, but
puts it at the top of the page rather than under Faculty. I would do (i).

*(Aside, unrelated to this task: `CLAUDE.md` documents the People section key as
`"grid": "small-up-1 medium-up-2"`, but the renderer actually reads `layout: faculty|cards|compact`
and maps it to grid classes itself. The doc is stale on that point.)*

## (c) DRAFT B — fuller, as a Home-page section

Insert after the Statstro figure, before `<p class="site-note">`, in
`ejs/pages/home/body.html`. 217 words of prose. Bare `&` throughout (the audit flags `&amp;` where
the file writes a bare `&`); no lists over five items; no dates; no exclamation marks.

```html
  <h2>
    Joining the ART
  </h2>

  <p>
    The ART is glad to hear from people who want to work with us. Both faculty are jointly appointed
    between the <a href="https://www.statistics.utoronto.ca/">Department of Statistical Sciences</a>
    and the <a href="https://www.astro.utoronto.ca/">David A. Dunlap Department of Astronomy &
      Astrophysics</a>, and most routes into the group run through one of them.
  </p>

  <p>
    <b>Graduate students</b> are admitted by the departments rather than by individual supervisors,
    and the supervisor is settled after admission. The first step is an application to <a
      href="https://www.sgs.utoronto.ca/programs/astronomy-and-astrophysics/">Astronomy &
      Astrophysics</a> or to <a
      href="https://www.sgs.utoronto.ca/programs/statistics/">Statistical Sciences</a>; you may
    apply to either or both. Naming the faculty member you hope to work with is what brings your
    application to their attention, and writing to them beforehand is welcome.
  </p>

  <p>
    <b>Postdoctoral researchers</b> normally arrive on a fellowship, since openings depend on
    funding. Competitions that suit this group include the <a
      href="https://nserc-crsng.canada.ca/en/funding-opportunity/canada-postdoctoral-research-award-program">CPRA</a>,
    <a href="https://canssiontario.utoronto.ca/canssi-ontario-postdoctoral-fellowship-in-statistics/">CANSSI
      Ontario</a>, the <a href="https://www.dunlap.utoronto.ca/dunlap-fellowship/">Dunlap
      Fellowship</a>, <a href="https://www.cita.utoronto.ca/opportunities/post-docs/">CITA</a>, and
    <a href="https://schmidtfellows.utoronto.ca">Schmidt AI in Science</a>.
  </p>

  <p>
    <b>Undergraduates</b> usually join for a summer through a funded program: <a
      href="https://www.astro.utoronto.ca/academics/undergraduate-studies/surp-2/">SURP</a> in
    Astronomy & Astrophysics, <a href="https://www.statistics.utoronto.ca/UTSSRP">UTSSRP</a> in
    Statistical Sciences, <a href="https://datasciences.utoronto.ca/suds/">SUDS</a> at the Data
    Sciences Institute, or an <a
      href="https://nserc-crsng.canada.ca/en/funding-opportunity/undergraduate-student-research-awards">NSERC
      USRA</a>. Toronto undergraduates can also work with us during the year through the <a
      href="https://www.artsci.utoronto.ca/current/experiential-learning/research-opportunities/research-opportunities-program">Research
      Opportunity Program</a>.
  </p>

  <p>
    Visiting researchers and prospective collaborators are welcome to write directly. Fuller lists,
    including programs for international students, are kept on the faculty sites of
    <a href="https://www.astro.utoronto.ca/~eadie/students.html">Gwen Eadie</a> and <a
      href="https://joshspeagle.com/#join">Josh Speagle</a>.
  </p>
```

### Traceability of every factual claim

| Claim | Source |
|---|---|
| Both faculty jointly appointed between DoSS and DADDAA | Josh: `sections.about.content`. Gwen: students.html, "As joint-faculty between DADDAA and DoSS, I can supervise students in either department." Also already asserted in the existing `p.site-note` on the home page. |
| Departments admit, not supervisors | Josh card 1: "I cannot admit graduate students directly, so the first step is applying to one of our Master's or doctoral programs." |
| Supervisor settled after admission | Gwen students.html: "prospective students must first apply through the department and then choose a supervisor in year two of the program." Softened to "after admission" — see (d). |
| May apply to either or both departments | Gwen students.html: "you can apply to either or both departments" / "you may apply to either or both programs". |
| Naming the faculty member routes your file | Gwen students.html: DoSS asks for "a list of faculty you are interested in working with … then I will see your application"; DADDAA "you can mention my name in your personal statement, and then there is a good chance the admissions committee will flag it for me to see." |
| Writing beforehand is welcome | Josh card 1: "email me before you apply." Gwen: "Thank you for your interest in my research group." |
| Postdocs arrive on fellowships; openings depend on funding | Josh card 0, near-verbatim: "Openings depend on funding, so most people arrive through one of the fellowships below." |
| The five named fellowships + URLs | Josh card 0 `fellowships.links`; all five re-verified HTTP 200 on 2026-09-07. |
| SURP, UTSSRP, SUDS, NSERC USRA as summer routes | Josh card 3: "the summer programs below are the usual way in … each one comes with funding and a structured research term." Gwen's (commented-out) block names SURP, SUDS and the NSERC award too. |
| ROP as a during-the-year UofT route | Josh card 2: "both during the year and over the summer", ROP listed first. |
| Visiting researchers / collaborators welcome | Josh card 5, near-verbatim. |
| Department links (statistics.utoronto.ca, astro.utoronto.ca) | Already in use in the existing `p.site-note` on the home page. |

Link check, 2026-09-07, browser UA through the proxy: all sixteen URLs above returned 200, except
`https://datasciences.utoronto.ca/suds/` — 403, as does `https://datasciences.utoronto.ca/` itself,
so the domain WAF is blocking our proxy rather than the page being gone. (The home page already
links that domain.) `https://www.cita.utoronto.ca/opportunities/post-docs/` and CITA SURF both
returned 200; SURF gave one transient 502 from the proxy tunnel before succeeding.

## (d) Facts I could not verify

1. **"the supervisor is settled after admission."** Gwen writes the stronger and more specific
   "choose a supervisor in year two of the program", for *both* departments. I could not confirm
   from the departmental pages that year two is still the rule, or that it is the rule in both
   departments, so I weakened it to a claim her sentence entails either way. **Ask Gwen whether
   "in the second year" can be stated plainly** — it is the single most useful fact on either site
   and the vaguer version wastes it.
2. **"Competitions that suit this group."** My own framing. Josh's page lists eleven fellowships
   flat, with no ranking and no statement that any subset fits the ART better. I picked five for
   length (CPRA, CANSSI Ontario, Dunlap, CITA, Schmidt) on the reasoning that they span the
   astronomy/statistics/AI spread. **Josh should confirm the five, or swap them.** Four of the
   eleven carry "when available" or eligibility notes in his data (CANSSI CDPF, CANSSI Ontario, DSI;
   Provost is Black & Indigenous only; PCRA is a top-up not a fellowship) — I dropped those notes,
   and CANSSI Ontario is in my five while carrying a "when available" flag.
3. **Whether the ART wants a standing "we are recruiting" posture at all.** Josh's card 0 says
   openings depend on funding; nothing on either site says the group is currently taking students or
   postdocs. DRAFT B is written to describe routes, not to advertise openings, but that is a
   judgement call the faculty should ratify.
4. **Gwen's agreement to any of it.** Every claim I attribute to her comes from her page, but DRAFT
   B speaks for "both faculty" on the ART site. Her page is unmistakably less maintained than
   Josh's (undergraduate section commented out, 2024 CV, no date stamp), so a line on the ART site
   pointing at it may age badly. Worth asking whether she wants the pointer, and whether she wants
   the undergraduate block uncommented.
5. **Master's admission.** Josh's card says "Master's or doctoral programs"; Gwen's says
   "direct-entry PhD programs". These do not agree. I wrote around it by naming the programs and
   not the degree. **Unresolved — someone should say which degrees the group actually takes.**
6. **SUDS reachability**, above: 403 from here, believed a WAF block, not confirmed live.
7. **Four URLs I carried into the notes but did not check** (none appear in DRAFT B): PCRA, Provost,
   DSI postdoc, WSP, UTEA, Mitacs Globalink Research Award, ELAP, Study in Canada.
8. **Where the section should live.** I put it on the Home page because that is the only
   hand-written body partial left (People and Research are both data-driven now). If it grows past
   this length it wants its own page, which means a new entry in the `pages` array in
   `webpack.config.js`, a `crumbs.html`, and a sidebar nav item in `main.ejs` — a bigger change than
   this proposal covers.

## Owner rulings (7 Sep)
- Use DRAFT B (the "Joining the ART" section on Home), pointing to both faculty sites at the end.
- Degrees: doctoral only. Say the group takes graduate students through the doctoral programs.
- Supervisor timing differs by department and should be stated: in Astronomy & Astrophysics
  students choose a supervisor in the second year; in Statistical Sciences a supervisor is
  assigned during admission.
- Fellowships: the owner questioned cutting eleven to five (ruling pending; default: keep all).
- Fellowships: name ALL ELEVEN, one sentence introducing them then a compact list with each link
  and its eligibility note where it matters (CANSSI CDPF, CANSSI Ontario, DSI: "when available";
  PCRA: a research top-up; Provost's: for Black and Indigenous scholars). Add "keep the ART
  fellowship list in step with joshspeagle.com's" to the update skill's checklist.
