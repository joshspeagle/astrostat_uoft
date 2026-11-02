# Visual Design Specification (`astrostatuoft.com`)

This document specifies the visual design system for the **Astrostatistics Research Team (ART)** website: color tokens, typography, layout geometry, component rules, and icon specifications.

- **`scss/_tokens.scss`** is the single source of truth for all hex color values.
- **`python3 docs/check_tokens.py`** verifies contrast ratios against WCAG AA floors (`4.5:1` for text, `3.0:1` for graphical marks) across both light and dark themes and ensures no hex values appear outside `scss/_tokens.scss`.

---

## 1. Color System (`scss/_tokens.scss`)

Every color on the site belongs to one of seven semantic tokens defined in `scss/_tokens.scss` for `light` and `dark` themes:

| Token | Light | Dark | Role |
|---|---|---|---|
| `page` | `#fefefe` | `#0a0a0a` | Primary page background surface |
| `card` | `#eeeeee` | `#333333` | Card, pathway, and roster container surface |
| `wash` | `#91acde` | `#001f4e` | Decorative brand mark accent in the Home hero |
| `ink` | `#1c1c1c` | `#efefef` | Primary body copy and headings |
| `link` | `#0f62fe` | `#70a9ff` | Interactive links, focus rings, and switch active track |
| `mark` | `#001f4e` | `#70a9ff` | Sidebar ART brand mark and favicon sparkle |
| `quiet` | `#6b6b6b` | `#8c8c8c` | Captions, metadata labels, hairline borders, monogram badge, and switch off-track |

### Link Styling

- **Primary links (`a`):** Rendered in `--link` with a `1px dotted` underline (`text-underline-offset: 0.18em`) that becomes `solid` on `:hover`, `:focus`, and `:active`.
- **Quiet links (`.quiet-links a`):** Used inside dense biography cards (`.card-text`), compact rows (`.compact-list`), and Research rosters (`.roster`). Rendered in `--ink` with a `1px dotted var(--quiet)` underline at rest, transitioning to `--link` with a `solid` underline on `:hover` and `:focus`.

---

## 2. Typography (`scss/_fonts.scss`, `scss/_type.scss`)

Two self-hosted variable/static webfont families in `fonts/`:
- **Display & Headings (`Urbanist`, `700`):** Used for `h1`, `h2`, `h3`, `.wordmark`, `.rail-wordmark`, and `.no-photo-initials`.
- **Body & UI Labels (`Inclusive Sans`, `400` / `700`):** Used for body copy, captions, navigation links, and small-caps labels (`.label`, `.card-site a`).
- **CJK Name Suffixes (`.card-name-cjk`):** Parenthetical CJK characters in card headings (e.g. `(沈佳士)`) scale to `0.78em` (`font-weight: 600`) inside `<span class="nowrap card-name-cjk">` so bilingual faculty names remain on a single line.

| Step | CSS Variable | Size | Usage |
|---|---|---|---|
| `display` | `--display` | `clamp(2.25rem, 1.6rem + 2.2vw, 3.25rem)` | Home hero wordmark (`Astrostat@UofT`) |
| `h1` | `--h1` | `clamp(1.85rem, 1.45rem + 1.4vw, 2.5rem)` | Page title (`h1`) and desktop `.no-photo-initials` |
| `h2` | `--h2` | `clamp(1.375rem, 1.2rem + 0.6vw, 1.625rem)` | Section headings (`h2`) and masthead wordmark |
| `h3` | `--h3` | `1.125rem` (`18px`) | Card names (`.card-name`), pathway titles (`.pathway-title`), and subsections |
| `lede` | `--lede` | `1.1875rem` (`19px`) | Opening page lede paragraph (`.lede`) |
| `body` | `--body` | `1.0625rem` (`17px`) | Standard prose paragraphs (`max-width: 65ch`) |
| `small` | `--small` | `0.9375rem` (`15px`) | Card bios (`.card-bio`), compact bios,captions, and fellowship pills |
| `label` | `--label` | `0.75rem` (`12px`, uppercase, `+0.04em` tracking) | Rail section headers (`NAVIGATE`, `ON THIS PAGE`) and `WEBSITE` links |

---

## 3. Layout & Navigation (`scss/_layout.scss`)

- **Shell (`.shell`):** Max width `78rem` (`1248px`), centered.
- **Desktop (`>= 768px`):** Two-column CSS Grid (`grid-template-columns: var(--rail) minmax(0, 1fr)`, where `--rail` is `11.5rem` at `768px` and `15rem` at `1024px`).
  - Column 1 holds the sticky `.rail`: the `56px` ART mark (`.rail-mark`), `Navigate` links (`Home`, `People`, `Research`, `Statstro`), the `Dark mode` switch, and the scrollspy-enabled `On this page` index (`.rail-index`).
  - Column 2 holds `.hero` (on `Home`) or `.masthead` (on `People` and `Research`) in row 1, `<main id="main">` in row 2, and `.site-footer` in row 3.
- **Mobile (`< 768px`):** `.rail` collapses into a sticky two-row top bar (`mark` + `Astrostat@UofT` + `Dark mode` on row 1; horizontal navigation links on row 2), and a native `<details class="otp">` (`On this page`) disclosure sits directly below `<h1>`.

---

## 4. Components (`scss/_components.scss`)

### Home Hero (`.hero`) & Joining Pathways (`.pathway-grid`)
- **`.hero`:** Sits at the top of the content column (`grid-column: 2; grid-row: 1`) on the `--card` surface (`padding: var(--s5) var(--s6)`). Places `.hero-words` (`Astrostat@UofT` / `Astrostatistics Research Team` / `University of Toronto`) on the left and `.hero-mark` (in `--wash`) on the right (`flex-direction: row-reverse` on desktop, stacked on mobile) so the brand mark and text never overlap.
- **`.pathway-grid`:** A 2-column grid on desktop (`1` column on mobile) of `.pathway-card` blocks under `#joining-the-art` (`Graduate Students`, `Postdoctoral Researchers`, `Undergraduates`, `Visiting Researchers & Collaborators`). Postdoctoral fellowships are rendered as scannable `.fellowship-pill` links inside `.fellowship-list`.

### People Cards & Monogram Fallback (`build/render-people.js`)
- **`.card-grid-faculty`:** Balanced 2-column grid on desktop (`grid-template-columns: repeat(2, minmax(0, 1fr))`) for the Faculty section.
- **`.card-grid`:** Responsive `repeat(auto-fill, minmax(16rem, 1fr))` grid for Postdoctoral Researchers, Graduate Students, Undergraduate Students, and ART Associates. Below `34rem` container width (or `560px` viewport width), cards switch to the compact `@mixin media-row` layout (`88×88px` floated photo beside heading).
- **Missing-Photo Monogram (`.no-photo` / `.no-photo-initials`):** When a person has `"image": null`, `build/render-people.js` computes their 2-letter initials and renders `<div class="card-photo no-photo" aria-hidden="true"><span class="no-photo-initials">XX</span></div>` on the `--page` surface with a `1px solid var(--quiet)` border.
- **Compact Rows (`.compact-list`):** Single-column rows for `Collaborators` (with `56×56px` thumbnails) and `Recent Alumni`.

### Research Themes (`build/render-research.js`)
- Each `.theme` pairs a sticky right-hand square figure (`200px` at `>=768px`, `260px` at `>=1024px`) with `.theme-prose` and `.roster` on the left.
- `.roster` displays up to three rows (`ART members involved` with a filled square `.roster-mark`, `ART associates involved` with a stroked square `.roster-mark`, and `Collaborators include`).

---

## 5. Icons & Brand Assets (`svg/`, `ico/`, `docs/design/icons/`)

- **Theme Icons (`svg/themes-sprite.svg`):** Eight custom `24×24` stroke glyphs (`stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`, `stroke="currentColor"`), inlined on `Research` and referenced in both the `On this page` rail index and each theme `<h2>`.
- **Brand Mark (`svg/art-mark.svg`) & Favicons (`ico/`):** The full ART wordmark+sparkle symbol is inlined once per page (`#art-mark`). The four-pointed sparkle forms `ico/favicon.svg` (adapting between `#001f4e` and `#70a9ff` via `prefers-color-scheme`), `ico/favicon.ico`, `ico/favicon-16.png`, `ico/favicon-32.png`, `ico/apple-touch-icon.png`, and `ico/icon-512.png`.
