---
name: art-website-update
description: Routine content, roster, and seasonal maintenance workflow for the Astrostatistics Research Team (ART) website (astrostatuoft.com). Use when adding or removing group members, moving graduates or postdocs to Recent Alumni, updating bios or fellowships, rolling over academic years, or running a periodic site check.
---

# Updating the ART Website (`astrostatuoft.com`)

## Step 0 — Preflight Discovery (`propose_updates.py`)

Before editing any files, run the preflight discovery script from the repository root:

```bash
python3 scripts/propose_updates.py --online
```

This script generates a structured Markdown **Update Proposal Digest** covering:
1. **Cross-repository sync (`../joshspeagle.github.io/assets/data/content.json`):** Identifies active UofT postdocs, doctoral students, or undergrads in Josh Speagle's personal website repository who are missing from `data/people.json`, as well as completed mentees who should move to `Recent Alumni`.
2. **Seasonal and date rollovers:** Flags graduate student `N`-th year labels that need incrementing (`--apply-years` applies them automatically), expiring `<b>On leave...</b>` notes, seasonal phrasing (`"This summer"`, `"incoming"`), and dated Home page photos.
3. **Internal audit & theme-fit summary:** Runs `scripts/audit_site.py` and `scripts/theme_fit.py --quiet`.
4. **Live web checks (`--online`):** Checks Gwen Eadie's group page (`https://www.astro.utoronto.ca/~eadie/students.html`) for newly listed mentees and verifies all external HTTP/HTTPS links across `data/home.json`, `data/people.json`, and `data/research.json`.

If the user has not already specified the exact edits to make, present the findings from the digest and confirm which items to apply before editing.

---

## Step 1 — Applying Roster & Content Updates

All three pages are generated from JSON files in `data/`:

| Page | Source file | Renderer |
|---|---|---|
| **Home** (`/`) | `data/home.json` | `build/render-home.js` |
| **People** (`/people.html`) | `data/people.json` | `build/render-people.js` |
| **Research** (`/research.html`) | `data/research.json` | `build/render-research.js` |

### 1. Adding a Person (`data/people.json` + `data/research.json`)

1. **Section placement (`data/people.json`):**
   - `Faculty`, `Postdoctoral Researchers`, `Graduate Students`, `Undergraduate Students`, `ART Associates`: card sections (`layout: "faculty"` or `"cards"`).
   - `Collaborators` (alphabetical by surname): co-advisers of current members and ongoing external collaborators (`layout: "compact"`).
   - `Recent Alumni` (reverse chronological by departure year): former postdocs and graduate students (`layout: "compact"`). Undergraduate alumni are not listed in `Recent Alumni`.
2. **Entry schema:**
   ```json
   {
     "id": "firstname-lastname",
     "name": "First Last",
     "image": "first_last.jpg",
     "alt": "First Last",
     "cohort": 2026,
     "paragraphs": [
       "<a href=\"https://example.com\">Website</a>",
       "First is a 1st-year Ph.D. student in the Department of Statistical Sciences co-supervised by <a href=\"https://joshspeagle.com\">Josh Speagle</a> and <a href=\"https://example.edu\">Co-Advisor</a>. Their research focuses on ..."
     ]
   }
   ```
   - `cohort` is required whenever a bio includes an `Nst/nd/rd/th-year` label (`expected_year = academic_year - cohort + 1`, where `academic_year` rolls over on September 1).
   - If no headshot is available yet, set `"image": null`; `build/render-people.js` automatically renders a 2-letter monogram tile (`.no-photo-initials`).
   - When a headshot is provided, process it with `python3 scripts/add_headshot.py <source-image> <first_last.jpg>` (`500×500` JPEG in `static/`).
   - Always list the **David A. Dunlap Department of Astronomy & Astrophysics** before the **Department of Statistical Sciences** when both are named.
   - Do not add repetitive inline links to UofT department homepages on student/postdoc cards; keep links focused on personal websites, fellowships, external institutions, surveys, and co-supervisors.
3. **Research themes (`data/research.json`):**
   - Every current member in `Faculty`, `Postdoctoral Researchers`, `Graduate Students`, and `ART Associates` must appear on at least one Research theme (`members` for Faculty/Postdocs/Grad/Undergrad; `associates` for ART Associates; `collaborators` for Collaborators).
   - Run `python3 scripts/theme_fit.py` to check which themes match the new bio's keywords, and run `python3 scripts/sort_themes.py --apply` if theme roster counts change the size ordering.

### 2. Moving a Member to `Recent Alumni`

1. Move their entry from their current section in `data/people.json` to the top of `Recent Alumni`.
2. Append their role and year to `name`: `"First Last (Ph.D. 2026)"`, `"First Last (M.Sc. 2026)"`, or `"First Last (Postdoc 2024-26)"`. Remove `"cohort"` if present.
3. Rewrite the bio's opening sentence to state their current position (`"First is now a ... at .... They completed their Ph.D. in ..."`).
4. Remove their `id` from all theme rosters in `data/research.json`, then run `python3 scripts/sort_themes.py --apply`.

### 3. Updating the Home Page (`data/home.json`)

- Group photo (`about.figure`), Statstro section (`workshop`), and career-stage pathways / postdoctoral fellowship pills (`joining.pathways`) live in `data/home.json`.
- Only update a group photo caption when replacing the photo file itself.

---

## Step 2 — Verification & Build Gate

Run the full verification and build suite before committing:

```bash
npm run build
npm run check
```

`npm run check` runs:
1. `python3 docs/check_tokens.py --quiet` — verifies WCAG contrast floors and ensures no hex color values appear outside `scss/_tokens.scss`.
2. `python3 scripts/test_audit.py` — runs the 35 unit tests for `audit_site.py`.
3. `python3 scripts/audit_site.py --strict` — verifies 0 content/roster/asset findings.
4. `./scripts/check_build_output.sh dist` — verifies all built files in `dist/`.
