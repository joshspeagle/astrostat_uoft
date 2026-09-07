# ART website audit findings (7 Sep 2026)

90 findings after merging 126 raw findings from 11 lenses. Status: confirmed = survived adversarial verification; unverified = low/nit or mechanical, reviewed by hand. 'Effective severity' applies the verifiers' corrections.


## F001 [high (was critical)] `.grid-x > .cell { display: flex }` collapses the sticky breadcrumb bar and the sidebar to fit-content width

- **Status**: confirmed · **Effort**: S · **Category**: layout · **Lenses**: visual-design, ux-ia, behaviour-bugs
- **Location**: scss/index.scss:170-172; symptom in ejs/main.ejs:27 (#sidebar .sticky) and :63 (#breadcrumbs-wrapper)
- **Evidence**: At 1440px, #breadcrumbs-wrapper computes width 45.5px inside a 970px .cell.small-12; #sidebar .sticky computes 77.9px inside a 170px cell. A/B with the rule disabled: {sticky:170px, crumbs:970px}. Once stuck, Foundation writes the shrunken width as inline `max-width: 77.9375px` and never recomputes it — byte-identical after resizing to 390px. At scroll 1400 on Research, elementFromPoint(700,28) returns the body <p>; the crumb row prints over '…most stars have companions' with the line above sliced. Screenshots: sticky-overlap-research-light.png, crumb-overlap.png, t3-sidebar-1440-dark.png.
- **Problem**: A rule added to square off People roster-card rows applies to every cell on the site. The breadcrumb bar's opaque ground covers only the width of the word HOME, so 900+px of prose scrolls visibly through the sticky bar on every long page, and the sidebar reserves 170px (370px on mobile) for 78px of content — 'Research' measures 75px against that 78px box.
- **Recommendation**: Scope the rule to the card grids: `.grid-x[class*="-up-"] > .cell { display: flex }`, or emit a `.people-grid` class from build/render-people.js and target that. Add `width: 100%` to #breadcrumbs-wrapper. Re-verify crumbs = 970px and sidebar .sticky = 170px, and that card row heights stay equal; if Foundation still writes a stale inline max-width, replace data-sticky with CSS `position: sticky`.
- **Verifier note**: Recommendation as given is sound; only add a note that the exact evidence pixel value for #breadcrumbs-wrapper (45.5px) could not be reproduced verbatim (160px was measured on research.html) — the underlying defect and fix are unaffected.
- **Verifier note**: Keep the fix as proposed for the breadcrumbs overlap (this is the real, visible bug), but the sidebar-clipping framing should be dropped or downgraded to a minor/cosmetic note — verify first whether overflow:visible already neutralizes it before spending effort there. Severity should be 'high' rather than 'critical': the bug causes a persistent, visually broken reading experience on every long page at common desktop/tablet widths (a real reputational/usability problem for visitors), but nothing is functionally broken — all links, nav, and content remain reachable and clickable, no data or workflow is lost, and mobile widths are unaffected since the sticky doesn't engage there.

## F002 [high (was critical)] People page renders ~37,000px tall on phones — one column of full-width square headshots

- **Status**: confirmed · **Effort**: M · **Category**: mobile-layout · **Lenses**: mobile-responsive
- **Location**: data/people.json (`grid` values); build/render-people.js card markup; scss/index.scss:213-217
- **Evidence**: scrollHeight: 37,331px at 390x844 (44 viewport heights), 37,053px at 320x568, but 18,540px at 768px where medium-up-N kicks in. cardImgRect at 390px = 354x354 per person, 50 cards. First screen at 320px shows zero people. Screenshot people-390x844-light.png.
- **Problem**: Below the medium breakpoint every section is forced to small-up-1, so the site's main directory of 50 researchers is ~44 screens of scrolling with a full-bleed square photo per person. The `grid` field's small-up-1 half is the only thing that matters on the majority of real mobile traffic.
- **Recommendation**: Below `medium`, cap `.person-thumbnail` at 120-160px and lay the card out thumbnail-beside-text (the pattern already used by Research's `.media-object`), and/or set `small-up-2` for the denser sections. Either collapses the page from ~37,000px to a few thousand.
- **Verifier note**: The recommendation (cap thumbnail size and go thumbnail-beside-text on small screens, similar to Research's .media-object pattern, and/or use small-up-2 for denser sections) is sound and proportionate. One addition worth noting: whatever fix is chosen should preserve the .h3 two-line-name alignment logic already in scss/index.scss, since collapsing to a smaller thumbnail changes the card's flex layout. Severity is more accurately "high" than "critical" — the page is fully functional and content is reachable via scrolling (nothing is broken or inaccessible), it is a severe usability/UX regression on the majority-mobile audience rather than a site-breaking defect, so "critical" (implying broken functionality or data loss) overstates it slightly.
- **Verifier note**: Recommendation as written is reasonable and should be kept largely as-is: cap `.person-thumbnail` size below `medium` and switch to a thumbnail-beside-text layout (reusing the existing `.media-object` component already used on Research), and/or use `small-up-2` for denser sections via the `grid` field already in data/people.json. No change needed to the fix itself — only the severity label is off (should be 'high', not 'critical').

## F003 [high (was critical)] `<base href="/">` sends every fragment link to the home page from People and Research

- **Status**: confirmed · **Effort**: S · **Category**: correctness · **Lenses**: behaviour-bugs
- **Location**: webpack.config.js:63 (`base: '/'`); link at ejs/main.ejs:11
- **Evidence**: On /people.html, Tab focuses the skip link (href='#body'); Enter navigates http://localhost:8000/people.html -> http://localhost:8000/#body, landing on the home page ('Welcome to the ART!'). Same on research.html. dist/people.html head contains `<base href="/">`. Screenshots t8-skiplink-people-heading-hidden.png, t9-skip-people.png.
- **Problem**: The base tag resolves `#body` against the site root, so the only keyboard-accessibility affordance navigates users off the page they are on. Any future in-page anchor (a People section link, a Research theme deep link) breaks the same way — which also blocks the fix for the missing-anchors finding.
- **Recommendation**: Delete `base: '/'` from webpack.config.js:63; nothing depends on it (all template links are already root-absolute and assets are emitted with publicPath). Add a build assertion that `grep -c '<base' dist/*.html` is 0.
- **Verifier note**: Recommendation is sound and should stand as-is (delete `base: '/'` from webpack.config.js:63; all internal links are already root-absolute so nothing depends on it). Only the severity label is off — this should be tracked as "high" (real, fixable accessibility regression with small blast radius) rather than "critical."
- **Verifier note**: Recommendation is sound as-is: delete `base: '/'` from webpack.config.js:63 (publicPath: '/' already handles asset resolution, and a grep of ejs/ and data/ confirms no template relies on relative hrefs). Adding a CI grep assertion for `<base` in dist/*.html is a reasonable, low-cost guard. No changes needed to the recommendation itself, only to the severity.

## F017 [high] At mobile widths the breadcrumb bar paints over the dark-mode switch and swallows its taps

- **Status**: confirmed · **Effort**: S · **Category**: layout · **Lenses**: behaviour-bugs
- **Location**: scss/index.scss:42-56, :170-172, :313-315; ejs/main.ejs:49-58
- **Evidence**: 390x844 index.html: #sidebar cell bottom 302.4; its .sticky child bottom 318.4 (16px past its own cell); #dark-mode-control 286.4-318.4; #breadcrumbs-wrapper top 302.4. overlapPx 16. `document.elementFromPoint(48.97, 304.4)` returns DIV#breadcrumbs-wrapper, not the switch. Screenshots t5-390-switch-vs-breadcrumbs.png and t3-sidebar-320-dark.png show the toggle sliced horizontally.
- **Problem**: A 1rem margin from #nav collapses out of the flex-item cell, which does not grow to contain the sticky child, and the breadcrumb bar paints its opaque themed background over the overflow. Every user between 320 and 639px sees a chopped rectangle where the toggle should be, and taps on its bottom third do nothing.
- **Recommendation**: Do both: stop the margin escaping (`display: flow-root` or padding-top on `#sidebar .sticky`, or replace `#nav, #controls { margin: 1rem 0 }` with `margin-block: 0 1rem` plus a gap), and inside `breakpoint(small only)` give `#controls` a 1.5rem bottom margin. Re-measure that #dark-mode-control bottom is above #breadcrumbs-wrapper top at 320 and 390.
- **Verifier note**: Recommendation is reasonable and correctly scoped (fix the overflowing margin and/or add clearance in the small-only breakpoint); should also verify the fix doesn't break the `data-sticky-on="medium"` behavior at the medium breakpoint transition, and should explicitly re-test tap/click via elementFromPoint post-fix, not just visual inspection, since the defect is as much a tap-target bug as a rendering one.
- **Verifier note**: Recommendation stands as proportionate. Minor addendum: since a workaround already exists (tapping the switch's upper portion or the 'Dark mode' label text still toggles correctly), this is not a total functional blocker — worth noting in the writeup so it isn't escalated to 'critical'. Otherwise the flow-root/containment fix plus a small-only defensive margin on #controls, then re-measuring at 320/390, is exactly the right proportionate fix.

## F004 [medium (was high)] Leo Wu's card ships an <img> with no src: invalid HTML, a broken-image glyph, and alt text that claims a photo exists

- **Status**: confirmed · **Effort**: S · **Category**: content-rendering · **Lenses**: visual-design, brand-iconography, behaviour-bugs, copy-language
- **Location**: data/people.json:198-200 (`"image": null`); build/render-people.js:41-47; js/index.js:42-49; scss/index.scss:185-187, 199-203
- **Evidence**: html-validate: 'element-required-attributes: <img> is missing required src' on dist/people.html. With JS disabled the card shows Chromium's broken-image glyph plus the literal alt string (t7-nojs-leowu-broken-img.png). With JS the fill-in is a 24x24 SVG stretched to 287x287 (12x) on a teal ground, carrying `alt="A picture of Leo Wu."` and `aria-hidden="true"` simultaneously; it is hidden entirely under `breakpoint(small only)`. Pixel census: the only 14,554 #82c7ce pixels on the page are this one card. It is the sole occupant of a `medium-up-3` Undergraduate Students section.
- **Problem**: The most visible defect on the People page is an error state drawn larger and louder than any real content, announced to screen readers as a photograph of a named undergraduate that does not exist, present on desktop and absent on mobile. CLAUDE.md already warns that `image: null` produces a broken image.
- **Recommendation**: Get a headshot and run scripts/add_headshot.py (LFS must be active). Failing that, stop emitting a src-less <img>: in build/render-people.js render a designed placeholder (card-background plus initials in the display face at muted ink) with `alt=""`, drop the runtime patching at js/index.js:42-48, and show it at all breakpoints. Re-run html-validate to confirm the error clears.
- **Verifier note**: Recommendation is sound and proportionate (S effort): get a real headshot via add_headshot.py, or failing that stop emitting alt text claiming a photo exists for a placeholder — either drop alt to empty/generic on the null-image path in render-people.js, or design a proper placeholder. No change needed to the recommendation itself.
- **Verifier note**: Keep the primary recommendation (get Leo a real headshot via scripts/add_headshot.py — this is the right, low-effort fix and should be done regardless of any code change). If a placeholder path is pursued as a fallback for future missing photos, don't broadly rewrite the JS/SCSS fill-in system: (1) scope the alt text correctly — a placeholder should carry `alt=""` since it depicts no one, not the person's name; (2) cap/contain the SVG's rendered size (e.g. a fixed small icon centered on a card-colored background) instead of stretching a 24x24 glyph to fill the whole card via `width:100%`, which is what makes it visually dominate; (3) do not describe this as "drop the runtime patching at js/index.js:42-48" — that range bleeds into the separate, intentionally-retained research-thumbnail fallback (lines 46-49, currently dormant but deliberate); scope any JS/render-people.js change to the person-thumbnail path only. Showing the placeholder at all breakpoints (rather than hiding it on mobile) is reasonable once its size and alt text are fixed.

## F006 [medium (was high)] The skip link is never revealed on focus — the first tab stop on every page is invisible

- **Status**: confirmed · **Effort**: S · **Category**: keyboard-focus · **Lenses**: accessibility, behaviour-bugs, ux-ia
- **Location**: ejs/main.ejs:11 (`class="show-for-sr"`)
- **Evidence**: One Tab on index.html focuses the link (activeElement tag A, text 'Skip to main content', outline 'auto 1px rgb(16,16,16)') but it computes to w:1 h:1, position absolute, clip rect(0,0,0,0). Full-page screenshot while focused (tab1.png, t5-focus-1-skiplink.png) shows nothing on screen; the next Tab (tab2.png) clearly rings the Home nav link, so focus is visible elsewhere. foundation-sites/scss/components/_visibility.scss:98-109 gives the `:focus` unclip only to `.show-on-focus`, not `.show-for-sr`. Activation itself works.
- **Problem**: WCAG 2.4.7: a sighted keyboard or switch user tabs, sees no feedback anywhere, and cannot discover the one control that would let them skip the nav on a 37,000px page.
- **Recommendation**: Add `show-on-focus` alongside `show-for-sr` (already compiled in via foundation-visibility-classes), or author a `.skip-link:focus` rule that unclips it to a padded, themed box at top-left with z-index above the sticky bar's 5. Verify by tabbing once and screenshotting.
- **Verifier note**: Recommendation is correct as written: adding `show-on-focus` alongside `show-for-sr` (simplest, reuses Foundation's existing compiled rule) or an equivalent custom `.skip-link:focus` unclip rule with sufficient z-index both fully fix it. No changes needed to the proposed fix.
- **Verifier note**: Recommendation is sound as written (swap to `show-on-focus` or add a themed `:focus` unclip rule, verify with one Tab + screenshot) — keep it, just file/track it as a medium-severity polish item rather than a high-priority accessibility blocker, since the site's nav is short enough that the skip link's practical value to a sighted keyboard user is low even though the compliance gap is real.

## F007 [medium (was high)] $medium-gray fails WCAG AA in light mode at the two smallest sizes, under a comment asserting the opposite

- **Status**: confirmed · **Effort**: S · **Category**: color-contrast · **Lenses**: brand-iconography, visual-design, accessibility
- **Location**: scss/_global.scss:8; scss/index.scss:433-434 (comment), :448 (figcaption), :459 (.site-note)
- **Evidence**: #888888 on #fefefe = 3.51:1 (fails 4.5:1); on #0a0a0a = 5.58:1 (passes). axe-core reports color-contrast violations on all three uses on index.html in light mode and zero in dark. Applied at figcaption 13.6px and .site-note 12.8px — the two smallest sizes on the site, set ~94 characters wide. The comment reads verbatim: '$medium-gray ... reads correctly on both the white and the black ground, so it needs no per-theme handling.'
- **Problem**: A colour role was judged by eye rather than measured, and the judgement is written into the file as the reason not to give it per-theme handling. It inks the group-photo caption naming ten people and the entire affiliations/credits footer; links inside that footer read at 7.16:1, so only the links are comfortably readable.
- **Recommendation**: Add a `muted-ink` key to both theme maps (#5f5f5f on white ≈7.0:1, #9a9a9a on black ≈7.0:1) and drive figcaption and .site-note off `map.get($theme, "muted-ink")` inside the existing `@each $name, $theme in $themes` idiom. Replace the comment with the measured ratios; leave $medium-gray for non-text use.
- **Verifier note**: Recommendation is sound and proportionate (effort S): add a per-theme muted-ink color to both theme maps and drive figcaption/.site-note off it via the existing @each $themes idiom, replacing the incorrect comment with measured ratios. One caveat: 12-13px text is arguably still 'large text' territory only if bold/14pt+, which it isn't, so 4.5:1 is the right AA threshold to target (not the 3:1 large-text threshold) — the recommended ~7:1 pairing comfortably clears that with margin, which is appropriate given the caption also names individuals (dignity/legibility concern, not just decorative text).
- **Verifier note**: The fix itself is fine as proposed. Only the framing needs correction: this affects two decorative/secondary text elements on the Home page only (not a sitewide or primary-content issue), so it should be scoped and prioritized as a medium-severity legibility polish item, not a high-severity accessibility blocker. No change to the technical recommendation is needed.

## F008 [medium (was high)] The 300px topper prints the watermark through the wordmark and scales its type to 8.5px on a phone

- **Status**: confirmed · **Effort**: L · **Category**: layout · **Lenses**: brand-iconography, mobile-responsive, visual-design
- **Location**: ejs/main.ejs:12-25; scss/index.scss:27 ($-topper-height: 300px), :114-149
- **Evidence**: At 1440x900 #topper-logo occupies x=452.5-987.5 while #topper-text's three lines are centred on x=720 — the mark sits directly behind the type, the ART 'T' bar crossing 'Astrostatistics Research Team'. The page's own <h1> first paints at y=357 of 900 (39.7%). At 390x844 the .h3 line 'University of Toronto' (x=146-244) is 100% contained inside the logo box; SVG viewBox scale 0.325 renders the three lines at 26/15.6/10.4px, and at 320px scale 0.2667 gives 12.8px and 8.53px. The two SVGs use different preserveAspectRatio rules, so the collision shifts with viewport width. Identity is stated five times in the first screen. Screenshots topper-light.png, crop_topper_320.png, mobile-topper-switch.png.
- **Problem**: Two thirds of every first screen is a masthead identical on all three pages, in which neither the mark nor the wordmark reads, and whose institutional attribution falls to roughly half the smallest legible size on the commonest small phone — because the type size is a consequence of the layout rather than a decision.
- **Recommendation**: Set the three wordmark lines as real HTML in a `<header>`, sized per breakpoint (e.g. 3rem/1.5rem/1rem large, 1.75rem/1rem/0.875rem small, floor 14px) or with clamp(). Keep the ART mark as SVG but make it decorative (`aria-hidden`), positioned at a fixed offset from the wordmark rather than aligned against a different box, or drop it and let the sidebar mark be the only logo. Cut $-topper-height to ~180px large / ~120px small.
- **Verifier note**: Recommendation is reasonable and proportionate (real HTML headings sized per breakpoint/clamp, decorative mark, shrink topper height). One correction: don't cite 'different preserveAspectRatio rules' as the cause of the scale mismatch when filing/fixing — both SVGs already share preserveAspectRatio="xMaxYMin meet"; the actual cause is the two elements' differing viewBox aspect ratios combined with different CSS sizing (#topper-logo: max-height:100%, position:absolute vs #topper-text: max-height:$-topper-height, position:relative), so the fix should address that rather than 'unifying preserveAspectRatio'.
- **Verifier note**: Downgrade to medium and scope down the fix: the only genuinely actionable issue is the mobile "University of Toronto" line dropping to ~8-10px, which is below comfortable reading size. Fix that narrowly — set an explicit min font-size (e.g. via clamp() or a small-breakpoint override in scss/index.scss's `.h3`/`.h2` rules) so no topper line ever renders under ~14px, and optionally trim `$-topper-height` on small breakpoints to reduce how much vertical space the masthead claims. Do not treat the watermark-behind-wordmark layout or the "five-times identity" repetition as defects requiring a rewrite — screenshots show good contrast and full legibility there; converting the topper to plain HTML headings and decoupling the SVG mark from the wordmark is a legitimate future polish item but is L-effort redesign work disproportionate to the actual (mobile-only, one-line) legibility problem.

## F009 [medium (was high)] No section or person anchors on either long page — nothing is deep-linkable and there is no in-page navigation

- **Status**: confirmed · **Effort**: M · **Category**: information-architecture · **Lenses**: ux-ia, brand-iconography, seo-sharing
- **Location**: build/render-people.js:41 (`<h2>${section.heading}</h2>`), :46-50 (card div, `<span class="h3">` name); ejs/pages/research/body.html (8 bare <h2>)
- **Evidence**: `grep -o 'id="[^"]*"' dist/people.html | sort -u` returns only chrome ids — not one content id; all 7 People and 8 Research <h2> render with no attributes, and person names are `<span class="h3">`, not headings, so there is no document outline. Heading offsets on People desktop: Faculty 599 … Recent Alumni 12,549 of 14,919 (30,711 of 37,331 on mobile). Research: Inference 627 … Star Formation 5,127. The only navigation while scrolling is the four-item sidebar, which links nothing in-page.
- **Problem**: Fifty people behind 16 desktop screens (44 mobile) with no index, no shareable URL for a section or a person, and no browser heading navigation. It also blocks linking Research roster names to People cards, since no card has an address.
- **Recommendation**: Slugify headings into ids in build/render-people.js (`<h2 id="postdoctoral-researchers">`), give each card `id="person-<slug>"`, and promote the name span to a real `<h3>`; do the same for the 8 Research <h2>s. Render a jump list from `data.sections` under each page intro (text links in the existing small-caps label idiom, not icons), and add `scroll-margin-top` so anchors clear the sticky bar.
- **Verifier note**: Recommendation is sound and proportionate (slugify headings into ids, add person card ids, promote name span to real h3, add scroll-margin-top, add jump list) — no correction needed.
- **Verifier note**: Recommendation is fine as written; only the severity is overstated from high to medium.

## F010 [medium (was high)] No description, Open Graph or Twitter Card metadata on any page, and no image asset to point at

- **Status**: confirmed · **Effort**: M · **Category**: metadata · **Lenses**: seo-sharing, brand-iconography, copy-language
- **Location**: ejs/main.ejs:3-9; webpack.config.js:13 (`title: 'Astrostat@UofT'`), :60, :69 (templateParameters)
- **Evidence**: The full built <head> is charset, x-ua-compatible, viewport, title, base, favicon link, stylesheet. `grep -c 'name="description"' / 'property="og:' / 'name="twitter:'` returns 0 on all three dist pages. No image in static/ is both a real URL and correctly proportioned: art-logo.svg is inlined by the webpack svg rule (unusable as og:image), art_summer_2025.jpg is 3771x1509 (2.5:1, 542KB) against the 1.91:1 unfurlers crop to. The home title is a wordmark carrying no words a searcher would type.
- **Problem**: A link to astrostatuoft.com pasted into Slack, Teams, Twitter/X, iMessage, Discord or LinkedIn unfurls with no image and no description — and Twitter drops the card entirely without twitter:card. For a research group whose purpose is to be found and cited, the most-seen surface of the site is blank, and Google fabricates the snippet from whatever mid-page bio text it lands on.
- **Recommendation**: Add a `description` (and `path`) field per entry of the `pages` array in webpack.config.js, thread it through templateParameters, and emit `<meta name="description">`, og:title/description/type/url/image and `twitter:card=summary_large_image` in ejs/main.ejs. Retitle the home page 'Astrostat@UofT | Astrostatistics Research Team', keeping the existing suffix pattern. Build a purpose-made 1200x630 static/og-card.jpg (reduced mark plus 'Astrostatistics Research Team — University of Toronto'); do not point og:image at the group photo.
- **Verifier note**: The finding and recommendation are technically sound and the fix (description/OG/Twitter meta plus a purpose-built 1200x630 og-card image) is the right approach and reasonably scoped at M effort. However 'high' overstates impact: nothing is broken for actual site visitors, no content is incorrect, and this is purely a missed-opportunity/polish issue for link-unfurling and search snippets rather than a functional or correctness defect — medium is a better fit. The recommendation to avoid pointing og:image at the group photo (wrong aspect ratio, large faces, wouldn't crop well to 1.91:1) is well-reasoned and should stand as written.
- **Verifier note**: Recommendation as written is fine and should be kept, but severity should be lowered to medium: this is worth fixing (real, verified gap with a concrete everyday trigger — link shares of the group's site) but is polish/discoverability, not a functional break, for a site whose main traffic is unlikely to come through social unfurls in the first place.

## F011 [medium (was high)] The alternating Research theme images do not alternate — 7 of 8 sit right because one `<br>` is missing

- **Status**: confirmed · **Effort**: S · **Category**: css-bug · **Lenses**: visual-design, mobile-responsive, copy-language
- **Location**: scss/index.scss:295-304 (`.media-object &:nth-child(odd)`); ejs/pages/research/body.html:11,50,91,137,175,215,259 vs 299
- **Evidence**: Measured nthChild for the eight themes: 5, 9, 13, 17, 21, 25, 29 (all odd -> order:2, imgX 1005) and Star Formation at 32 (even -> order:0, imgX 335). At 768px, themes 1-7 have imgLeft 492.98 > txtLeft 142.98; only Star Formation is reversed. At 390px stacked, the same 7 put text before image and Star Formation image before text. Cause is in the source: every theme is a four-element run `<br><h2><div.media-object><div.theme-roster>`, and line 299 is the one <h2> with no <br> above it.
- **Problem**: nth-child counts headings, spacer <br>s and roster blocks, so the parity it reads has nothing to do with which theme it is. The page reads as seven identical right-image rows then one that looks broken, and the flipped row's prose starts at x=651 while its own roster below starts at x=335 — the only theme whose text does not align with its roster.
- **Recommendation**: Decide the intent and make it explicit rather than positional: emit `media-flip` on every second theme from a renderer and key the flip off that class, or delete scss/index.scss:295-304 and keep every image on one side. Either way delete the eight <br> spacers and let `section > h2 { margin-top }` carry the gap. The one-line stopgap is adding the missing <br> at body.html:299.
- **Verifier note**: Recommendation is sound and proportionate: the root cause is positional CSS (nth-child parity) driven by incidental sibling count rather than semantic intent, and the fix options (explicit media-flip class, or drop the alternation and the <br> spacers in favor of h2 margin-top) are the right menu of choices. The effort estimate (S) is reasonable — the minimal stopgap (add the missing <br> at line 299) is a one-line fix, though the more robust fix (explicit class instead of relying on sibling-count parity) is preferable long-term as noted.
- **Verifier note**: Recommendation is technically sound as written, but given the low real-world impact, the one-line stopgap (add the missing <br> before the Star Formation <h2> at body.html:299) is the proportionate fix to ship now; the larger refactor (explicit media-flip class from the renderer, dropping the <br>-based spacing for CSS margin) is a reasonable follow-up cleanup but shouldn't be sized/prioritized as urgently as the 'high' severity implied — it's a nice-to-have robustness improvement, not a fix for a user-facing failure.

## F012 [medium (was high)] On phones the nav chrome fills the first screen and then scrolls away permanently

- **Status**: confirmed · **Effort**: L · **Category**: mobile-navigation · **Lenses**: ux-ia, mobile-responsive
- **Location**: ejs/main.ejs:38-59 (sidebar `.sticky data-sticky-on="medium"`), :63 (breadcrumbs)
- **Evidence**: At 390x844: topper 0-98, nav 114-243, dark-mode control 258-318, breadcrumb 302-359, <h1> at y=360 — 42.7% of the fold is chrome; at 320x568 #body starts at y=342 of 568 (60%) and the first screen shows no page content at all. Probing people.html at scrollY 900/3000/8000: nav, breadcrumb and toggle all `vis:false` and stay off screen for the remaining 36,400px. `document.querySelector('footer')` is null; body.lastElementChild is SCRIPT. Screenshots index-320x568-light-fold.png, people-mobile-deep.png (scrollY 18000, zero navigation affordances).
- **Problem**: There is no mobile-adapted chrome: the same vertical sidebar renders in flow, sticky is disabled below medium, and there is no footer or back-to-top. A settings control outranks the content on every page, and from 2.4% of the way down People the only route to another page is a 36,000px scroll or browser chrome.
- **Recommendation**: Collapse the small-breakpoint chrome into one ~48px sticky bar (wordmark, three links or a menu button, theme toggle demoted to an icon button), target <h1> visible within the first 160px, and add a shared site footer partial with the nav links, affiliations and date. A back-to-top after ~2 viewports is a cheap addition.
- **Verifier note**: The recommendation (collapse chrome to a compact sticky bar, get h1 into the first ~160px, add a footer, consider back-to-top) is proportionate to the defect and reasonably scoped; effort estimate of L is fair given it touches shared layout, CSS breakpoints, and requires a new footer partial.
- **Verifier note**: Keep it to a proportionate fix: (1) add a shared footer partial (nav links, affiliations, last-updated date) rendered on all three pages — cheap, closes the "no way back to nav after a long scroll" gap, and CLAUDE.md already implies a footer/date exists elsewhere in the design backlog; (2) optionally lower the `data-sticky-on` breakpoint or add a lightweight sticky mini-header only if user testing / analytics actually show mobile visitors bouncing before scrolling past the nav. Skip the full L-effort redesign of the sidebar into a collapsed icon bar with menu button and demoted toggle — that's a disproportionate rebuild of the existing Foundation drilldown/sticky nav for a small, low-mobile-traffic academic site, and the "no content at all in the fold" justification for urgency doesn't hold up against the cited screenshots (the h1 and body copy are visible in both the 390x844 and 320x568 folds).

## F013 [medium (was high)] Two colour tokens swap roles between themes: the logo colour in one is the link colour in the other

- **Status**: confirmed · **Effort**: M · **Category**: colour-roles · **Lenses**: brand-iconography, visual-design
- **Location**: scss/_lightmode.scss:9,17,25; scss/_darkmode.scss:9,17,25; scss/ux/_switch.scss:23-25
- **Evidence**: Light: `$-palette-primary: #91acde`, `$-anchor-color: #2f559d`, `"logo-desaturated": $-palette-primary`. Dark: `$-palette-primary: #2f559d`, `$-anchor-color: #91acde`, same logo binding — the two hexes exactly exchanged. In dark mode #2f559d is simultaneously the topper watermark (scss/index.scss:156-158) and the switch's ON fill, both visible on one screen (topper-dark.png, sidebar-dark.png).
- **Problem**: A reader who learns '#91acde is the logo' in light mode meets it as 'this is a link' the moment they flip the toggle, on a control they operate themselves. Periwinkle carries three unrelated roles (watermark, switch-on, link) while the teal secondary token carries none.
- **Recommendation**: Give the logo its own key (`logo-ghost`) in both theme maps with a hue distinct from the anchor blue — the ~185deg teal currently wasted on palette-secondary is the obvious candidate — stop aliasing logo-desaturated to palette-primary, and give the switch's checked state its own `switch-on` key. Verify with a swatch sheet that no hex appears against two role names in either map.
- **Verifier note**: The recommendation (give the logo a distinct 'logo-ghost' key sourced from the currently-unused secondary/teal hue, and give switch-on its own token) is reasonable and low-risk, but should be framed as a design-system/brand-consistency cleanup rather than an urgent fix — no functional, readability, or accessibility harm results from the current aliasing.
- **Verifier note**: Downgrade to a nit/low-severity code-hygiene note rather than an M-effort visual-design fix. If addressed at all, just rename/comment the shared variable to make the intentional role-sharing explicit (e.g. note in the SCSS that logo-desaturated intentionally aliases palette-primary across themes) rather than introducing a new logo-only token and reassigning the secondary teal, which risks a less cohesive palette for a problem visitors cannot actually perceive.

## F014 [medium (was high)] The 11,784-character logo path is inlined twice per page, and two unreferenced copies ship as dead files

- **Status**: confirmed · **Effort**: S · **Category**: logo-usage · **Lenses**: brand-iconography, performance
- **Location**: ejs/main.ejs:15 and :33; static/art-logo.svg; static/art-logo-mod.svg; webpack.config.js:176-183
- **Evidence**: main.ejs holds two `<path d>` attributes of exactly 11,784 characters, byte-identical to each other and to static/art-logo-mod.svg. The two SVG blocks total 24,689 bytes and appear in all three pages: 84.4% of dist/index.html (29,242 B), 52.3% of research.html, 32.4% of people.html. static/art-logo.svg (13,195 B, Inkscape master) and art-logo-mod.svg (12,081 B) are copied to dist by CopyPlugin and referenced by nothing — audit_site.py lists both under unreferenced files.
- **Problem**: A logo revision has to be applied by hand in two places in one template or the topper and sidebar silently disagree, with no test that would catch it; and every visitor re-downloads the same geometry twice per page with no caching benefit, plus 25KB of dead LFS-tracked files.
- **Recommendation**: Define the path once as `<symbol id="art-mark" viewBox="0 0 534.98053 300">` in a hidden svg at the top of body in ejs/main.ejs and reference it twice with `<use href="#art-mark">` (the mask can point at the same symbol). Delete static/art-logo-mod.svg; keep art-logo.svg only if it is wanted as a downloadable master, and say so, otherwise delete it and drop both from LFS.
- **Verifier note**: The <symbol>/<use> dedup recommendation for the two inline copies in main.ejs is sound and worth doing (S effort, real bug-prevention value against the topper/sidebar silently diverging). However, the recommendation to delete static/art-logo-mod.svg and possibly static/art-logo.svg should be softened: audit_site.py already treats these as intentional, informational-only unreferenced files (source masters for the inline path, likely kept for provenance/regeneration via Inkscape), not accidental dead code — deleting them should be a deliberate decision by the site maintainer (confirm whether art-logo-mod.svg is only a build-time source for hand-copying into main.ejs) rather than treated as an obvious cleanup, and the finding should not claim they are 'referenced by nothing' as if that were a defect the audit tool failed to catch, since the tool already surfaces and contextualizes it correctly.
- **Verifier note**: Keep the symbol/use dedup idea, but reframe as a minor code-quality cleanup (not a performance fix — note in the writeup that gzip already eliminates almost all of the real transfer cost, so this is about template maintainability, not page weight) and bump effort from S to S/M to include manual visual QA in both themes across all three pages (topper + sticky sidebar mask) since there's no automated visual test. For the two static SVG files, just state plainly in the recommendation (as the audit tool already implies) that they are intentionally-kept source/master copies rather than 'dead' output artifacts, and let the maintainer decide whether to keep one as a downloadable master or drop both — don't frame their presence as a bug needing urgent fixing.

## F015 [medium (was high)] Every page hard-codes `data-theme="dark"`, so light-preference users get a full-page dark flash on every load

- **Status**: confirmed · **Effort**: S · **Category**: correctness · **Lenses**: behaviour-bugs, ux-ia
- **Location**: ejs/main.ejs:2; js/index.js:18-32, :49
- **Evidence**: With color_scheme='light' and all JS requests aborted, index.html after 600ms still has data-theme='dark', body background rgb(10,10,10), color rgb(254,254,254). Screenshot t2-fouc-nojs-lightpref-shows-DARK.png. The theme is only corrected after the bundle downloads, parses and `$(document).ready` fires; js/index.js:49 comments that 'putting this last may help with the fouc problem'.
- **Problem**: The whole viewport paints in the wrong theme until the 218KB bundle executes, on a site with no client-side routing, so it happens on every navigation — three times in a normal visit.
- **Recommendation**: Remove data-theme from the <html> tag and set it from a tiny render-blocking inline script at the top of <head>, before the stylesheet, reading localStorage then prefers-color-scheme. Alternatively make the light palette the bare `:root` default and re-declare only the dark tokens under `@media (prefers-color-scheme: dark)` plus `[data-theme="dark"]`, so the no-JS first paint is already correct.
- **Verifier note**: Recommendation is accurate and proportionate (a tiny render-blocking inline script in <head>, or restructuring CSS so light is the bare :root default with dark under media/attribute overrides) — no change needed.
- **Verifier note**: Keep the primary recommendation (small render-blocking inline script in <head>, before the stylesheet, that reads localStorage then prefers-color-scheme and sets data-theme immediately) — it's accurate and appropriately low effort. Drop or caveat the "alternative" of making light the bare :root default with dark under @media/[data-theme="dark"]: that would require reworking roughly 30 existing [data-theme="#{$name}"] selector blocks across scss/index.scss and _switch.scss, so it is meaningfully more than "S" effort compared to the inline-script fix and shouldn't be presented as an equally-sized option.

## F016 [medium (was high)] No contact information or route for prospective students anywhere on the site

- **Status**: confirmed · **Effort**: S · **Category**: information-architecture · **Lenses**: ux-ia, copy-language
- **Location**: ejs/pages/home/body.html:42-49; data/people.json:3 (People intro)
- **Evidence**: Across all three built pages, `grep -o 'mailto:[^"]*' dist/*.html` returns 0 matches; case-insensitive greps for 'contact', 'prospective', 'join us', 'opening', 'position', 'apply' return 0 on index.html and people.html and one incidental hit on research.html. The home body has 8 links, 6 external.
- **Problem**: CLAUDE.md frames prospective students as an audience; journalists and would-be collaborators have the same problem. There is no email, no statement of whether the group is recruiting, and no institutional contact — the only path is to leave for a faculty member's personal homepage and hunt. The site's primary conversion action is entirely unsupported.
- **Recommendation**: Add a short 'Join us / Contact' block on the home page after the lede (contact routes for Gwen and Josh, one sentence on how prospective grad students apply and to which departments, one on undergrad/summer opportunities), and repeat the contact line in the shared footer.
- **Verifier note**: Recommendation is reasonable and proportionate (effort S, additive content-only change). Could note the site isn't a total dead end — faculty personal websites linked from People entries may carry contact info — so scope could be softened to 'add an explicit contact/recruiting block' rather than implying zero path exists, but this doesn't change the core validity or severity.
- **Verifier note**: Keep the core recommendation (a short 'Join us' paragraph on the home page linking to Gwen's and Josh's contact/websites and the two departments' graduate-application pages) but drop it from high to medium severity and drop the footer-repetition ask — a single home-page mention is proportionate for a 3-page lab site that already links prominently to the departments and to both PIs' personal sites, which is the conventional place such contact info lives.

## F018 [medium (was high)] No bold weight of Inclusive Sans is shipped, so every bold word in body copy is synthetic

- **Status**: confirmed · **Effort**: S · **Category**: typography · **Lenses**: visual-design
- **Location**: scss/_fonts.scss:1-20; ttf/Inclusive_Sans/
- **Evidence**: ttf/ contains only InclusiveSans-Regular.ttf and -Italic.ttf (both usWeightClass 400) plus Urbanist-Bold and an undeclared Urbanist-BoldItalic. In-browser `document.fonts` lists exactly ['Inclusive Sans|400|normal|loaded', 'Inclusive Sans|400|italic|unloaded', 'Urbanist|700|normal|loaded']. 'Handgloves' at 100px measures 554.81px at weight 400 and 554.81px at 700 — identical advances, the signature of Chromium's synthetic bold. `.lede b` computes font-weight 700, family 'Inclusive Sans'.
- **Problem**: Faux bold carries load-bearing type: the home lede's group name, every <strong> call to action, the on-leave status note, the sidebar NAVIGATE/DARK MODE labels, PERSONAL WEBSITE on 44 cards, and ART MEMBERS INVOLVED on 8 rosters. At 14.7px it thickens strokes without redrawing counters, and those labels also use `font-variant: all-small-caps`, itself synthesised — a faked weight on faked small caps.
- **Recommendation**: Add InclusiveSans-Bold to ttf/Inclusive_Sans/ under LFS and declare it as a third @font-face at font-weight 700, then re-run the Handgloves 400-vs-700 width check and confirm the numbers differ.
- **Verifier note**: Recommendation is correct as written (add InclusiveSans-Bold.ttf under LFS, declare a 700 @font-face, re-verify with the Handgloves width check). Only adjustment: severity is inflated at 'high' — this is a purely cosmetic typography defect (faux-bold letterforms) with no functional, accessibility-blocking, or content-correctness impact; 'medium' better reflects that it's widespread but not user-facing-broken.
- **Verifier note**: Recommendation is fine as stated (add InclusiveSans-Bold under LFS, declare @font-face at weight 700, re-verify with the Handgloves width check) — keep it, but treat it as a minor polish/backlog item rather than something requiring urgent action, since no visitor-facing harm results from the current synthetic bold on small-caps utility labels.

## F019 [medium (was high)] jQuery plus the entire Foundation plugin set (218KB) ships for two features, one of them misapplied

- **Status**: confirmed · **Effort**: L · **Category**: unnecessary-payload · **Lenses**: performance
- **Location**: js/index.js:2; package.json; ejs/main.ejs:27, :40-45, :63
- **Evidence**: dist/assets/index.bundle.js is 217,798 bytes minified. `webpack --json` shows the full plugin set despite `import { Slider, Sticky, Drilldown }`: abide 28,718B, slider 23,222B, offcanvas 22,436B, drilldown 21,156B, reveal 17,830B, orbit 16,513B, sticky 15,452B, tabs, dropdownMenu, tooltip, dropdown, core, accordion, accordionMenu, responsiveAccordionTabs, equalizer, magellan and more, plus jquery (315,121B unminified). foundation-sites has no `sideEffects` field so the barrel cannot be tree-shaken. Of the three imports, Slider has zero data-slider usage anywhere in ejs/, and Drilldown is applied to a flat 4-item list with no submenu.
- **Problem**: Every page pays ~218KB of JS to run a dark-mode toggle, two sticky elements, and a nav that needs no drilldown machinery at all.
- **Recommendation**: Replace Foundation Sticky with CSS `position: sticky` (a media query standing in for data-sticky-on), drop the drilldown for a plain list or a small disclosure, and rewrite js/index.js's toggle and fill-in logic in vanilla JS. That removes jQuery and Foundation JS entirely.
- **Verifier note**: The recommendation (drop jQuery/Foundation JS entirely: CSS `position: sticky`, a plain/native disclosure nav instead of drilldown, vanilla JS for the toggle and image fill-in) is technically sound and proportionate to the payload savings described. However, given this is a small 3-page academic site rather than a performance-sensitive app, "high" severity overstates urgency — this is a worthwhile but non-blocking optimization, better characterized as medium severity. No change needed to the recommendation itself.
- **Verifier note**: Keep the diagnosis but scale down the fix: (1) drop the unused Slider import immediately — zero risk, no visible change, and shrinks the bundle for free; (2) optionally replace the two Foundation Sticky elements with CSS `position: sticky` since only "sticky-on-medium" behavior is used; (3) leave the Drilldown/jQuery/dark-mode-toggle rewrite as a lower-priority nice-to-have rather than treating the whole payload as a high-severity problem — on a low-traffic, cached, 3-page academic site the ~64KB gzipped cost is a real but minor inefficiency, not something that materially hurts visitors or justifies an L-effort full framework removal.

## F020 [medium (was high)] The People page ships 3.59MB across 54 requests with every headshot eager-loaded

- **Status**: confirmed · **Effort**: S · **Category**: unnecessary-payload · **Lenses**: performance
- **Location**: build/render-people.js:41-48 (img attrs); ejs/pages/research/body.html thumbnails; home page images
- **Evidence**: Playwright resource timing after networkidle on /people.html: 3,588,801 bytes over 54 resources, all images fetched regardless of scroll — largest radu_craiu.png 281,158B, peter_martin.jpg 246,983B, aviad_levis.jpg 231,815B, ryan_cloutier.jpg 174,599B, slizewski.jpg 160,817B, vianey_leos_barajas.jpg 151,196B. `grep -c 'loading=' dist/*.html` returns 0 on all three; the attrs array is built from class, src and alt only.
- **Problem**: A first visit downloads 3.59MB before any scrolling, most of it headshots dozens of screens below the fold, delaying interactivity and wasting data for visitors who never reach Alumni.
- **Recommendation**: Add `loading="lazy" decoding="async"` to the attrs array in build/render-people.js and to the hard-coded research thumbnails and home images, leaving the above-the-fold Faculty images eager.
- **Verifier note**: The core recommendation (add loading="lazy" decoding="async" to the attrs array in build/render-people.js, and to the hardcoded research thumbnails and home images) is correct and appropriately scoped/low-effort. One refinement: leaving all Faculty images eager is reasonable, but the same treatment should be considered for the first section of any other people/research grid that renders above the fold, rather than a blanket "first section eager" rule — check actual fold position per page rather than assuming section order alone determines eagerness. Otherwise the recommendation stands as proportionate to a medium-severity, S-effort cleanup.
- **Verifier note**: Recommendation itself is fine as-is (add loading=\"lazy\" decoding=\"async\" to the attrs array in build/render-people.js for non-Faculty sections, and to research/home thumbnails below the fold) — cheap, safe, no layout risk. Just downgrade severity from high to medium: this doesn't block or meaningfully delay page interactivity on a small static academic site served over HTTP/2, it's a bandwidth-courtesy improvement rather than a UX-breaking issue.

## F022 [medium (was high)] Home-page panorama photos ship at full resolution to every device with no responsive variants

- **Status**: confirmed · **Effort**: M · **Category**: unnecessary-payload · **Lenses**: performance
- **Location**: static/art_summer_2025.jpg (3771x1509, 542,255B), static/statstro_2026_group_photo.jpg (2000x694, 278,567B); plain <img> in ejs/pages/home/body.html
- **Evidence**: Rendered box measured with getBoundingClientRect: art_summer_2025 is 970x388 CSS px at 1440 and 370x148 at 390 — yet the same 3771px-wide 542KB file ships to both. Re-encoding to actual need: 1940px wide q82 -> 316,189B (42% smaller); 740px wide -> 56,497B (90% smaller than what phones download today). The Statstro photo shows the same pattern (370px need -> 58,052B vs 278,567B shipped).
- **Problem**: A phone downloads a 542KB desktop-retina image for a slot that only ever displays at 370 CSS px on that device.
- **Recommendation**: Generate ~740px and ~1940px variants for each panorama and serve with srcset/sizes (or <picture>); at minimum cap the sources at ~2000px wide, since nothing displays them larger even at 2x desktop.
- **Verifier note**: The recommendation (srcset/sizes or <picture>, or at minimum capping source width to ~2000px) is sound and proportionate to an M effort estimate. Severity is the only overstatement: this is a small academic team site, not a high-traffic or conversion-sensitive property, so the real-world cost of a 90%-larger-than-needed mobile download on two hero images is a moderate performance/UX nit rather than a high-severity issue. Recommend downgrading to medium.
- **Verifier note**: Recommendation is directionally correct and proportionate (M effort, srcset/sizes or <picture> with ~740px and ~1940px variants) — keep it, but severity should read as medium rather than high: this is a real, easily fixable payload win (67% of the mobile home-page's total bytes, 90% reducible on the largest image) but not a functional or accessibility break on a small, low-traffic academic site, so it shouldn't be triaged above genuine correctness/a11y bugs.

## F023 [medium (was high)] Research theme rosters are hand-duplicated from data/people.json with no source of truth

- **Status**: confirmed · **Effort**: L · **Category**: maintainability · **Lenses**: build-maintainability
- **Location**: ejs/pages/research/body.html (all 337 lines); data/people.json
- **Evidence**: people.json holds 50 people; research/body.html hand-types 24 `<p class="roster-row">` blocks across 8 themes, re-typing names and personal-site URLs already in the JSON (e.g. `<a href="https://joshspeagle.com">Josh Speagle</a>` independently in both files). CLAUDE.md documents four dedicated audit checks that exist only to detect the resulting drift, and states audit_site.py is not wired into CI.
- **Problem**: Every name change, URL change or roster move must be made correctly by hand in a second differently-formatted file, with nothing at build time enforcing agreement — the exact drift the People page's JSON design was built to avoid, which Research never got.
- **Recommendation**: Add data/research.json plus build/render-research.js wired into webpack.config.js as a `content` generator like the People partial, resolving member/associate names against data/people.json at build time and failing the build on an unknown name. That deletes the HTML partial and makes four of audit_site.py's checks structurally impossible rather than merely detectable.
- **Verifier note**: Recommendation is correct as written, but severity should be medium rather than high: this is real, verified technical debt with a clear architectural fix, but there is no current user-facing breakage and an existing (manual, deliberately-not-CI) compensating control already exists — audit_site.py's drift checks, run at the start/end of edits via the art-website-update skill. That mitigates but does not eliminate the risk, which is why this isn't low, but nothing is presently broken, which is why it isn't high.
- **Verifier note**: Keep as a real, worth-fixing maintainability finding but downgrade to medium and stage the fix rather than jumping to an L-effort rewrite: (1) low-effort first -- add a 5th research-page audit check comparing the href on each linked Research roster name against sites[name] from people.json and flagging mismatches (closes the currently-silent URL-drift path); (2) only pursue the full data/research.json + render-research.js generator later if roster churn or drift incidents actually prove frequent enough to justify an L-effort rewrite of a page that also carries hand-written prose and images per theme, not just rosters.

## F024 [medium (was high)] Both GitHub Actions workflows pin end-of-life Node 18, and the publish path uses older action majors than the PR gate

- **Status**: confirmed · **Effort**: S · **Category**: ci · **Lenses**: build-maintainability
- **Location**: .github/workflows/build-site.yaml:12-22; .github/workflows/build-check.yaml:20-30
- **Evidence**: build-site.yaml (which force-pushes to gh-pages) uses actions/checkout@v3 and actions/setup-node@v3 with node-version '18'; build-check.yaml uses @v4 for both, also on 18. Node 18 reached EOL in April 2025; GitHub has been deprecating Node16-era action runtimes.
- **Problem**: The workflow that actually publishes the live site runs on unsupported Node with the older action majors, and the two workflows have silently drifted despite doing near-identical setup — a bump applied to one is easy to forget in the other.
- **Recommendation**: Bump both to actions/checkout@v4, actions/setup-node@v4+ and node-version '22', add `cache: 'npm'` to both, and keep the setup steps identical (or factor into a reusable workflow) so they cannot drift again.
- **Verifier note**: Recommendation is reasonable as stated (bump to checkout@v4, setup-node@v4+, node-version '22', add npm caching, keep the two workflows in sync or factor into a reusable workflow). No change needed there beyond noting this is routine maintenance, not an urgent fix.
- **Verifier note**: Recommendation is fine as written (bump both workflows to checkout@v4/setup-node@v4+/node 22, add cache: 'npm', keep the two setup blocks identical or factor into a reusable workflow). Just downgrade severity from high to medium: the workflow is verified still succeeding on Node 18/v3 actions as of the most recent push (2026-09-02), so this is a proactive hygiene fix against a future deprecation, not a current break — and even a future failure would leave the last successful gh-pages build in place rather than taking the site down.

## F025 [medium (was high)] No schema.org structured data for the Organization or the 50-person roster

- **Status**: confirmed · **Effort**: L · **Category**: structured-data · **Lenses**: seo-sharing
- **Location**: build/render-people.js:19-67; data/people.json; ejs/main.ejs head
- **Evidence**: `grep -c 'application/ld+json'` returns 0 on all three pages. data/people.json already carries clean per-person fields (name, image) and, per the LINK_ONLY convention at render-people.js:12-17, a first paragraph that is frequently exactly `<a href="...">Personal Website</a>` — a ready-made sameAs URL — across 7 sections and 50 people.
- **Problem**: The highest-leverage discoverability gap: a real, structured research group with personal-site links already modelled in JSON emits zero machine-readable markup, forfeiting Organization and per-member Knowledge Graph surfacing.
- **Recommendation**: In build/render-people.js emit an `application/ld+json` block alongside the HTML: an Organization node (name, url, logo, member[]) plus one Person node per entry (name, image, sameAs from the existing LINK_ONLY regex). Add the Organization node to the head as well. Keep it purely additive to the visible markup.
- **Verifier note**: The recommendation itself (add an additive application/ld+json block with Organization + Person nodes using existing name/image/LINK_ONLY-derived sameAs data) is sound and reasonably scoped. However severity should be medium, not high: this is a pure SEO/discoverability enhancement with no functional breakage, no incorrect or missing visible content, and no accessibility impact — the site remains fully crawlable and correct without it. "High" should be reserved for user-facing defects or major discoverability blockers (e.g., missing meta tags, broken indexing), not for an absent nice-to-have enrichment.
- **Verifier note**: Keep the recommendation (additive JSON-LD in render-people.js plus an Organization node in ejs/main.ejs head) but treat it as a low-priority, opportunistic enhancement rather than a high-severity gap — nothing is broken or degraded for visitors today. If implemented, validate the generated JSON-LD (e.g., with Google's Rich Results Test or schema.org validator) since the source paragraphs contain raw inline HTML that must be safely stripped/escaped for JSON string values, and treat effort as M rather than L given that data-cleaning need.

## F026 [medium (was high)] Two dead external links in alumni bios, one of them inconsistent with the same person's link elsewhere

- **Status**: confirmed · **Effort**: S · **Category**: link-rot · **Lenses**: content-link-rot
- **Location**: data/people.json — Mairead Heiger bio (~line 430) and Steffani Grondin bio (~line 442)
- **Evidence**: `curl -L https://www.astro.utoronto.ca/~ting/` -> 404 (confirmed twice); that URL is linked as 'Ting Li' in Mairead Heiger's bio, while Ting Li's own People entry (lines 357-359) and two other bios (Anika Slizewski line 131, Tri Nguyen line 275) link her correctly to https://sazabi4.github.io (200). `curl -L https://fbroekgaarden.github.io` -> 404 with and without trailing slash; linked as 'Floor Broekgaarden' in Steffani Grondin's bio.
- **Problem**: Two links a real visitor would click return 404, and one of them is an internal inconsistency — the same person is linked correctly in three places and to a dead URL in a fourth.
- **Recommendation**: Change the Ting Li href in Mairead Heiger's paragraph to https://sazabi4.github.io to match her other listings. For Floor Broekgaarden, find the current site and update the href, or drop the link and leave plain text if no current URL can be confirmed.
- **Verifier note**: Same recommendation as given, but severity should be medium rather than high: these are two dead outbound links in alumni bios (not current-member or navigation content), low visitor traffic to these deep bio paragraphs, easy S-effort fix, and no functional/build breakage. The Ting Li fix is trivial (swap in the URL already used correctly three other places); the Floor Broekgaarden fix requires research to find a current URL or fall back to plain text.
- **Verifier note**: Recommendation is fine as written (swap Ting Li's href to https://sazabi4.github.io in Mairead's bio; verify/update or unlink Floor Broekgaarden's site in Steffani's bio) — just file it as a medium/low routine link-rot fix rather than high severity, since it affects alumni-bio prose links, not core navigation or current-member accuracy.

## F027 [medium (was high)] 'On leave November 2025-2026' is ambiguous and may already be stale

- **Status**: confirmed · **Effort**: S · **Category**: factual-accuracy · **Lenses**: copy-language
- **Location**: data/people.json:15
- **Evidence**: Line 15, the second paragraph of the first card on the People page: `"<b>On leave November 2025-2026.</b>"`. Today is 2026-09-07. It is the only status note in the file, so there is no house pattern to read it against.
- **Problem**: The range parses two ways: 'November 2025 to November 2026' (still running) or 'from November 2025 through the 2025-26 academic year' (ended months ago). Nothing on the page disambiguates it, and this single sentence governs whether a prospective student or collaborator emails a faculty member.
- **Recommendation**: Confirm the actual return date and replace with an end-dated form, e.g. `<b>On research leave until 1 November 2026.</b>`; if the leave has ended, delete the paragraph (CLAUDE.md's convention is website link, then status note, then bio, so removing the middle entry is safe). Use 'until <month year>' so audit_site.py can later flag it once the date passes.
- **Verifier note**: Recommendation is reasonable as written (confirm the real end date and use an unambiguous 'until <month year>' phrasing, or remove the note if the leave has ended) — just downgrade urgency/severity to medium rather than high, since it affects one bio line and requires no site-wide or structural change.
- **Verifier note**: Keep the recommendation's substance (confirm the real end date with Gwen and rephrase to an unambiguous 'until <month year>' form, or delete the note if leave has ended) but drop the invented specific day ('1 November 2026') — the source data only ever gave month/year granularity, so state it as 'On research leave until November 2026' (or whatever month is confirmed) rather than fabricating a day-level date not evidenced anywhere in the file.

## F028 [medium (was high)] The home page opens on a greeting <h1>, two exclamation marks and three hype words in one sentence

- **Status**: confirmed · **Effort**: S · **Category**: voice · **Lenses**: copy-language
- **Location**: ejs/pages/home/body.html:3-13
- **Evidence**: Lines 3-5: `<h1>Welcome to the ART!</h1>`. Lines 8-10: '…is an interdisciplinary research group using cutting-edge statistics and artificial intelligence to unravel the mysteries of the Universe!'
- **Problem**: This is the first text on the site and the furthest thing on it from the register the rest of the project keeps — restraint, measurement rather than adjectives. Two exclamation marks in four lines plus 'cutting-edge' and 'unravel the mysteries of the Universe' in one clause read as a brochure. Separately the only <h1> is a greeting, so the page's top-level heading carries no name for search results, screen-reader heading lists or link previews.
- **Recommendation**: Make the <h1> the group's name and rewrite the lede plainly: 'The Astrostatistics Research Team (ART) is an interdisciplinary group at the University of Toronto working across astrophysics, statistics, and machine learning, on problems that run from individual stars to the large-scale structure of the Universe.' Name the destinations in the two following links rather than praising them.
- **Verifier note**: The rewrite suggestion is reasonable in direction (name the group in the h1, dial back exclamation marks and superlatives) but should be treated as a copy-polish suggestion rather than a must-fix defect; the recommended replacement lede is also notably longer/denser than the original and could itself use trimming rather than being adopted verbatim.
- **Verifier note**: Keep the core suggestion (h1 should carry the group's name; trim the exclamation marks and hype adjectives like 'cutting-edge' and 'unravel the mysteries') but treat it as a quick copy-polish task, not a rewrite mandate — the maintainer can adjust the existing sentence rather than needing the fully scripted replacement paragraph provided. Severity should be low (nit-to-low), not high, since there is no functional, accessibility, or traffic impact for a small lab site.

## F030 [medium] No <main> or <header> landmark, and role="banner" sits on the wordmark SVG

- **Status**: unverified · **Effort**: S · **Category**: landmarks · **Lenses**: accessibility, behaviour-bugs, brand-iconography
- **Location**: ejs/main.ejs:12 (#topper div), :18 (svg role="banner"), :39 (#nav), :49 (#controls), :70 (#body div)
- **Evidence**: axe-core flags landmark-one-main and region on all three pages in both themes; on index.html the region violation names `<div id="nav">`, `<ul id="controls">` and the body wrapper, and on people.html 19 nodes including the <h1> and every section <h2>. html-validate reports prefer-native-element on #topper-text ('Prefer to use the native <header> element') on all three pages. #topper-logo has neither aria-hidden nor a title.
- **Problem**: Screen-reader users navigating by landmark get no main region on any page, the sidebar nav and theme control are exposed as unlabelled generic content, and the banner landmark that is claimed contains only three lines of wordmark text — excluding the nav and logo a banner would normally hold.
- **Recommendation**: Change `<div id="body">` to `<main id="body">` and `<div id="topper">` to `<header id="topper">`, drop role="banner" from the SVG, wrap the nav block in `<nav aria-label="Site">`, and add aria-hidden to #topper-logo and #sticky-logo (wrapping the sidebar mark in an `<a href="/" aria-label="Astrostat@UofT home">` also makes it the home link people expect). All are drop-in changes in the one shared template.

## F031 [medium] Foundation Drilldown recasts four plain links as an ARIA menubar and injects an invalid attribute

- **Status**: unverified · **Effort**: S · **Category**: aria-validity · **Lenses**: accessibility, behaviour-bugs, performance
- **Location**: ejs/main.ejs:41-48; js/index.js:2, :50; node_modules/foundation-sites/js/foundation.drilldown.js:54
- **Evidence**: Static markup has no role or aria-*; after `$(document).foundation()` axe reports a CRITICAL aria-allowed-attr violation on every page/theme: `<ul id="nav-drilldown" role="menubar" aria-multiselectable="false">` — aria-multiselectable is not allowed on menubar. Runtime inspection: hasSub false, aria 'menubar', all four items role="none" (/, /people.html, /research.html, statstro.com). Drilldown.js hard-codes the attribute at line 54.
- **Problem**: The site's primary navigation ships an ARIA-invalid combination — axe's most severely rated violation here — and four ordinary links are announced as an application menu with arrow-key semantics the widget does not implement, since there are no submenus.
- **Recommendation**: Delete data-drilldown (and data-back-button/data-auto-height) from ejs/main.ejs and drop Drilldown from the js/index.js import, keeping the .vertical.menu classes for styling; as a stopgap while the plugin stays, strip the attribute after init with `$('#nav-drilldown').removeAttr('aria-multiselectable')`. Confirm the list no longer reports role menubar.

## F032 [medium] Internal links hardcode the production domain instead of relative paths

- **Status**: confirmed · **Effort**: S · **Category**: correctness · **Lenses**: build-maintainability, ux-ia, copy-language
- **Location**: ejs/pages/home/body.html:11-12; ejs/pages/research/body.html:8
- **Evidence**: home/body.html links to https://astrostatuoft.com/research.html and .../people.html; research/body.html:8 links to `href=https://astrostatuoft.com/people.html` (also an unquoted attribute). `grep -o 'href="https://astrostatuoft.com[^"]*"' dist/*.html` returns index.html x2 and research.html x1. main.ejs's own nav correctly uses `/`, `/people.html`, `/research.html`. Because of this the link measurement counts 8/8 home-page links as external.
- **Problem**: On the localhost preview in CLAUDE.md's own workflow, a PR preview or a gh-pages fork, the site's two primary calls to action jump to the live site, so nobody reviewing a change ever exercises them — and a domain change would require grepping body content for hostnames the nav deliberately avoids.
- **Recommendation**: Change all three to `/research.html` and `/people.html`, and quote the research/body.html:8 href.
- **Verifier note**: Recommendation is correct and proportionate (effort S): change the three hrefs to relative paths (/research.html, /people.html) matching main.ejs's nav convention, and quote the research/body.html:8 attribute while at it.

## F033 [medium] Tap targets across the site fall below the 24x24 minimum, including the entire primary nav

- **Status**: confirmed · **Effort**: S · **Category**: touch-target · **Lenses**: ux-ia, mobile-responsive
- **Location**: ejs/main.ejs:41-47; compiled `#nav-drilldown li a{padding:.25rem 0}`; scss/ux/_switch.scss:3-5
- **Evidence**: At 390x844 the four nav links measure 78x25.6 with vertical gaps of [0,0,0] — the box is exactly the glyph, since the Foundation default gives 4px vertical and 0 horizontal padding (identical at 320/390/768/1024). 197 interactive elements measure under 24px in one dimension, including every 'Personal Website' link (96x19) and 279 card links at 19px line boxes. The switch paddle is 64x32; its input is 13x13.
- **Problem**: WCAG 2.5.8 sets 24x24 and platform guidance 44x44. Four stacked 20-26px links with no gap are a mis-tap generator on the control set a phone user needs most, and 19px inline links inside dense bios are close to unhittable at 279 per page.
- **Recommendation**: Give `#nav-drilldown li a` `min-height: 44px; display: flex; align-items: center` with padding (e.g. 0.6rem 0.75rem) widening the hit area to the sidebar column, and 4-8px vertical spacing at small widths. Raise card bio line-height to at least 1.6 so inline links clear 24px, and give .person-link its own padded row. Optionally bump $switch-height.
- **Verifier note**: Recommendation is reasonable and proportionate (CSS-only fix, effort S is accurate). One refinement: the WCAG 2.5.8 citation should be scoped to the primary nav and switch-input (clearly non-exempt standalone controls) rather than implying all 279 inline bio links are equally in violation, since WCAG 2.5.8 exempts targets 'in a sentence or block of text' — the fix for those (raising line-height to ~1.6) is still good practice but is a UX improvement rather than a strict WCAG failure fix.

## F034 [medium] All 50 headshot alt strings begin 'A picture of' and then repeat the name shown beneath

- **Status**: confirmed · **Effort**: M · **Category**: accessibility-copy · **Lenses**: copy-language, accessibility
- **Location**: data/people.json (all `alt` fields); build/render-people.js:44-50; ejs/pages/research/body.html:15
- **Evidence**: 50 of 50 entries have alt starting with the literal 'A picture of' (e.g. line 12 'A picture of Gwendolyn Eadie.' directly above line 10 name 'Gwendolyn Eadie'), and the renderer emits the image then `<span class="h3">${person.name}</span>` immediately beneath. Research thumbnail alts follow the same prefix pattern.
- **Problem**: Screen readers already announce the role, so every visitor hears 'image, A picture of Gwendolyn Eadie' followed one element later by 'Gwendolyn Eadie' — 50 times, doubling the page for a non-visual reader while adding nothing (WCAG H37/G94 guidance is explicit about this prefix).
- **Recommendation**: Make the headshots decorative: set `"alt": ""` throughout data/people.json and — required, or this makes things worse — change `if (person.alt) attrs.push(...)` at render-people.js:46 to always emit the attribute, otherwise the falsy empty string drops it and screen readers announce the filename. If the names are wanted, at minimum strip the prefix and period. Leave the genuinely descriptive Research thumbnail alts alone apart from the prefix.
- **Verifier note**: Recommendation is sound as written; no correction needed.

## F035 [medium] 44 links on the People page share the identical text 'Personal Website'

- **Status**: confirmed · **Effort**: S · **Category**: link-text · **Lenses**: accessibility, copy-language
- **Location**: data/people.json (44 link-only paragraphs); build/render-people.js:17, :51-54
- **Evidence**: `dist/people.html` contains the exact string `>Personal Website<` 44 times, each anchoring a different URL; render-people.js matches these with LINK_ONLY and tags them `class="person-link"`.
- **Problem**: In the links list that NVDA, JAWS and VoiceOver users navigate by (Insert+F7 / rotor), 44 consecutive entries read 'Personal Website' with no way to tell whose without leaving the list. It is also the site's single most-repeated phrase.
- **Recommendation**: Add a per-person accessible name in the renderer rather than editing 44 JSON strings: when LINK_ONLY matches, inject `aria-label="Personal website of ${person.name}"` into the anchor before emitting. Visible text and layout are unchanged; escape quotes defensively in case a name is ever edited.
- **Verifier note**: Recommendation is sound as written; no correction needed. One implementation nit: the injected aria-label should escape double quotes in person.name (e.g. via a small helper) to avoid breaking the attribute if a name is ever entered with a quote/apostrophe-adjacent character, and consider whether alt-text and aria-label wording should stay consistent (e.g. "Personal website of Gwendolyn Eadie" vs the existing alt "A picture of Gwendolyn Eadie.").

## F036 [medium] Nine headshots are upscaled past their source resolution even at DPR 1, and the two Faculty photos are the softest relative to their slot

- **Status**: confirmed · **Effort**: M · **Category**: imagery · **Lenses**: visual-design, performance
- **Location**: static/ (per data/people.json `image`); slots from scss/index.scss:213-217 and the `grid` values
- **Evidence**: Slots measured at 1440px: 454px (Faculty medium-up-2), 287.3px (medium-up-3), 204px (Collaborators medium-up-4). Under-resolved at DPR 1: Leo Wu 24, adam_muzzin 170, rodrigo_herrera 200, keith_vanderlinde 200, Phil_Headshot 267, mairead_heiger 280, and jacqueline_antwi-danso, tanveer_karim, christian_jespersen, ian_zhang all 270. At DPR 2 the two Faculty photos are 500px sources in a 908-device-pixel slot (1.82x stretch). Sources range 24px to 1092px — a 45x spread for three render sizes.
- **Problem**: The People page is mostly photographs, so sharpness is most of its visual quality, and it varies visibly card to card for no reason a reader can see; object-fit hides the mismatch from the layout but not from the eye.
- **Recommendation**: Set a source floor of 2x the largest slot an image can land in — 960px Faculty, 600px for the 3-up sections, 440px Collaborators — re-encode from originals with `add_headshot.py --size` where they exist, and list the rest for fresh photos. Add a check to scripts/audit_site.py flagging any static/*.jpg below the floor for its owner's section, which the script can already determine from data/people.json.
- **Verifier note**: Drop Leo Wu from the list of 'under-resolved headshots' — he has no photo on file at all (image: null), which is a distinct, already-tracked issue (audit_site.py's missing-photo check), not a resolution problem. Restate the finding as eight real headshots under-resolved for their slot, with a spread of ~170px-1092px (~6x), not 24px-1092px (~45x). The rest of the recommendation (2x-of-largest-slot floor per section, re-encoding via add_headshot.py, and a new audit_site.py check for below-floor sources) is reasonable and should stand.

## F037 [medium] Two PNG headshots are committed as raw git blobs because .gitattributes' LFS policy excludes PNG

- **Status**: unverified · **Effort**: S · **Category**: repo-hygiene · **Lenses**: build-maintainability, content-link-rot
- **Location**: .gitattributes:1-4; static/radu_craiu.png; static/renee_hlozek.png
- **Evidence**: .gitattributes tracks only *.ttf, *.svg, *.jpg, *.ico via filter=lfs. `git check-attr filter` returns 'unspecified' for both PNGs (vs 'lfs' for GwendolynEadie_2018.jpg), and `head -c 30` shows real \x89PNG binary, not the ~130-byte pointer text; 280,858B and 99,132B, added in commit 11f6f5e.
- **Problem**: CLAUDE.md documents static/ as LFS-tracked and gives a verification command (grep for pointer headers) that these two files silently pass by not matching any tracked pattern. ~380KB of binary sits in git history and is pulled by every clone regardless of LFS setup.
- **Recommendation**: Add `*.png filter=lfs diff=lfs merge=lfs -text` to .gitattributes and migrate the two files (`git lfs migrate import --include="*.png"`), or convert them to JPEG per CLAUDE.md's stated preference, which also fixes their size.

## F038 [medium] The sidebar nav never marks the current page, and the compensating breadcrumb is a one-item trail on Home

- **Status**: confirmed · **Effort**: S · **Category**: wayfinding · **Lenses**: brand-iconography, ux-ia
- **Location**: ejs/main.ejs:41-53, :63-68; ejs/pages/home/crumbs.html:1; scss/index.scss:42-69
- **Evidence**: Greps for aria-current, is-active and current across ejs/, js/ and scss/ return no match (one hit is a JS comment). All four nav links compute the identical colour rgb(47,85,157) and transparent background on all three pages. home/crumbs.html is, in full, `<li><span class="show-for-sr">Current: </span> Home</li>` inside a measured 57.34px sticky bar whose entire visible content is the word HOME. On Research the crumb reads 'Home » Research' — the same two words the nav shows three lines above.
- **Problem**: Two navigation systems occupy the top of every page and together convey less than one would: the nav says where you can go but not where you are, and on a flat three-page site the breadcrumb has no hierarchy to express.
- **Recommendation**: Pass the page name through templateParameters in webpack.config.js and emit `aria-current="page"` on the matching nav item, styled with two channels (body-font-color plus a 3px left rule in logo-saturated, padding shifted so text does not move). Then drop the breadcrumb bar — at minimum on Home via an empty crumbs.html — reclaiming 57px; put the page name in the mobile sticky header instead if a location cue is wanted there.
- **Verifier note**: Recommendation is reasonable and proportionate as written; no correction needed.

## F041 [medium] Fonts ship as TTF with no font-display — ~94KB avoidable and text invisible while they load

- **Status**: confirmed · **Effort**: S · **Category**: unnecessary-payload · **Lenses**: performance, visual-design
- **Location**: scss/_fonts.scss:1-21; dist/assets/fonts-*.ttf
- **Evidence**: InclusiveSans-Regular 57,124B + Italic 57,884B + Urbanist-Bold 42,636B = 157,644B. Converted with fontTools to WOFF2: 22,540 + 23,060 + 17,680 = 63,280B, a 59.8% reduction (94,364B saved). `grep -o '@font-face[^}]*}' dist/assets/index.css` shows no font-display in any of the three rules.
- **Problem**: Every first-time visitor downloads ~94KB more font data than necessary, and with no font-display the browser default (block) hides text in these faces for up to three seconds while the TTFs arrive.
- **Recommendation**: Add WOFF2 versions and list them first in each src with `format('woff2')` (TTF only as a fallback if pre-2016 support matters), and add `font-display: swap` to all three rules.
- **Verifier note**: Recommendation as stated is sound and proportionate (add WOFF2 first with TTF fallback, add font-display: swap to all three rules). No change needed.

## F042 [medium] The teal `palette-secondary` token has no role — its only painted appearance is behind the broken image

- **Status**: confirmed · **Effort**: M · **Category**: colour-roles · **Lenses**: visual-design, brand-iconography
- **Location**: scss/_lightmode.scss:10, _darkmode.scss:10; consumed at scss/index.scss:185-187, 285-289, 349-355
- **Evidence**: Three bindings only: `.card img` background (49 of 50 thumbnails are opaque JPEGs, so it shows on 1), `.media-object img` background (all 8 research thumbnails opaque, so 0), and the drilldown arrow colours — measured live, `#nav-drilldown ul` count 0 and `.js-drilldown-back` count 0, so those rules never match. Pixel census: the only exact #82c7ce pixels on people-desktop-light.png are 14,554 inside one 287x287 box; index and research register 1 pixel each (anti-aliasing).
- **Problem**: The palette declares two accent tokens and uses one. Teal is currently bound to 'image failed to load' — the one role you would never spend an accent on — while periwinkle carries watermark, switch-on and link simultaneously.
- **Recommendation**: Either retire palette-secondary from both theme maps and delete the dead drilldown rules at index.scss:349-355, or reassign the hue to a role the site actually has and periwinkle should not carry (the logo's own token, or the Research roster label accent across all eight themes). Write the binding down beside the variable either way.
- **Verifier note**: Recommendation is reasonable as stated (retire the token or reassign it, document the binding). One refinement: since the drilldown dead-code is provably structural (no nested nav levels exist, not just "measured 0 live"), the writeup could state that as a certainty rather than an empirical/pixel-census result — but this doesn't change the verdict or severity.

## F043 [medium] Favicon is a 24.8KB ICO that is illegible at 16px, with no SVG icon, apple-touch-icon, manifest or theme-color

- **Status**: confirmed · **Effort**: M · **Category**: favicon · **Lenses**: brand-iconography, seo-sharing
- **Location**: ico/favicon.ico; webpack.config.js:60; ejs/main.ejs:3-9
- **Evidence**: Decoded ICO: 4 entries (16/24/32/64px), all 32-bit uncompressed BMP, 24,838 bytes. Rendered at 8x (fav-16.png) the full logo — letterforms, diagonal streak and ~20 sparkles — is crushed into 16px and 'ART' is not readable. `grep -c` for apple-touch-icon, rel="manifest" and name="theme-color" returns 0 on all pages. static/art-logo.svg exists but is inlined only, never referenced as an icon.
- **Problem**: The tab icon is noise at the size it is actually seen, so the site has no recognisable mark in a tab or bookmark bar; 'Add to Home Screen' on iOS shows a screenshot thumbnail; and the mobile browser chrome never matches the light/dark theming the site specifically ships.
- **Recommendation**: Draw a reduced mark for small sizes (letterforms and streak, sparkles dropped) and ship icon.svg, a regenerated 16/32 favicon.ico with PNG-compressed entries (~2KB), a 180x180 apple-touch-icon on an opaque ground, and site.webmanifest; add two `<meta name="theme-color">` variants guarded by prefers-color-scheme, matching the two theme backgrounds.
- **Verifier note**: Recommendation is reasonable and proportionate to a medium-severity finding: a single bundled fix (reduced-mark SVG, regenerated compact ICO, apple-touch-icon, manifest, theme-color meta) rather than several separate high-effort asks. No change needed, though the effort estimate of "M" seems arguably light — designing a legible reduced mark, regenerating a compressed ICO, and producing an opaque-ground 180x180 PNG plus manifest and dual theme-color metas is more like 2-4 hours of combined design+implementation work, but that's a minor quibble not worth downgrading confidence over.

## F044 [medium] Nine type sizes, seven of them within 12% of each other, and a single 1.85x chasm

- **Status**: confirmed · **Effort**: M · **Category**: typography · **Lenses**: visual-design
- **Location**: scss/index.scss (font-size authored only at :39, :62, :120, :124, :128, :228, :235, :382, :427, :445, :457) — no h1/h2/h3 size authored anywhere
- **Evidence**: Measured: h1 48px, h2 40px, card name 21.6px, lede 19.71px, body 17.6px, breadcrumb 15.84px, card bio / roster row 14.72px, figcaption 13.6px, site-note 12.8px. Successive ratios 1.20, 1.85, 1.10, 1.12, 1.11, 1.08, 1.08, 1.06. h1/h2 are Foundation's $header-styles defaults untouched while `body { font-size: 110% }` moved the text sizes independently.
- **Problem**: Seven sizes sit inside a 1.06-1.12 band, below the threshold at which a step is perceived, so breadcrumb, card bio, caption and footer read as one size that wobbles and none signals rank; meanwhile the only real step is the 1.85x drop from h2, and h1 sits 1.2x above h2 so 'People' and 'Faculty' read as the same level.
- **Recommendation**: Author the whole scale rather than inheriting Foundation's: set $header-styles before importing Foundation and use one ratio (e.g. 1.25 from a 17.6px body: 34.4 / 27.5 / 22 / 17.6 / 14.1 / 11.3). Collapse breadcrumb, card bio, roster row and figcaption onto the single small step and keep only the footer below it — nine sizes to six. Note the mobile-readability finding: do not put primary card/roster prose below 16px.
- **Verifier note**: Recommendation is reasonable as a direction (author $header-styles, pick one ratio, collapse the clustered sizes) though the exact numeric scale proposed is just one illustrative option, not the only valid fix — that's fine for a recommendation, not a defect.

## F045 [medium] The `68ch` measure cap resolves to 94 characters per line, and is applied uniformly to the smallest text

- **Status**: confirmed · **Effort**: S · **Category**: typography · **Lenses**: visual-design
- **Location**: scss/index.scss:413-416 (`section > p { max-width: 68ch }`), :274-277, :410-412 (comment)
- **Evidence**: Computed max-width 913.75px on index and 815.93px on People/Research. The ch unit in Inclusive Sans is 13.44px while the average character in running text measures 8.68px — a 1.55x overestimate — so index prose is ~94 chars/line, People/Research ~94, figcaption 630px at 13.6px ~94, .site-note 593px at 12.8px ~94. At the other end `.card .card-section p` measures 271px (~45 chars) in 3-up grids and 188px (~31 chars) in the 4-up Collaborators grid; `.roster-names` measures 742px (~102 chars).
- **Problem**: The comment says the cap fixed a column running 'well past 100 characters'; measurement says it moved it from ~105 to 94, still 25% above the comfortable band and invisibly small a change. Applied uniformly it also governs the two smallest sizes on the site, while Collaborators cards run at 31 characters — the page has both failure modes at once and no band in between.
- **Recommendation**: Stop using ch. Set the measure in rem against a target: `max-width: 34rem` on `section > p`, `.media-object .main-section p` and `.roster-names`, and `30rem` on figcaption and .site-note since they are set smaller. Drop Collaborators from medium-up-4 to medium-up-3 so its bio column lands near 45 characters, or give that section a photo-and-name-only card.
- **Verifier note**: Recommendation is sound as written; no correction needed.

## F046 [medium] The dark-mode switch is loudest in the state you are not in, and both state indicators fail the 3:1 non-text floor

- **Status**: confirmed · **Effort**: S · **Category**: color-contrast · **Lenses**: visual-design
- **Location**: scss/ux/_switch.scss:14-26; tokens at _lightmode.scss:14-15 / _darkmode.scss:14-15
- **Evidence**: Light: OFF track #333333 on #fefefe = 12.53:1; ON track #91acde on #fefefe = 2.27:1; knob #fefefe on the ON track = 2.27:1. Dark: OFF #eeeeee on #0a0a0a = 17.06:1; ON #2f559d on #0a0a0a = 2.74:1; knob #0a0a0a on the ON track = 2.74:1. main.ejs ships data-theme="dark", so the shipped default state is the 2.74:1 one. Visible in index-desktop-dark-fold.png vs index-desktop-light-fold.png.
- **Problem**: WCAG 1.4.11 requires 3:1 for a control's state indicator. The relationship is inverted — the control shouts about the state you just left and whispers about the state you are in — and in both themes the knob-against-track separation, the thing that actually reads as on or off, is under the floor, leaving hue as effectively the only channel.
- **Recommendation**: Give the ON track a colour chosen for ratio rather than for being the brand primary — reuse each theme's anchor token (#2f559d in light with a #fefefe knob, 7.16:1; #91acde in dark with a #0a0a0a knob, 8.64:1) — and add a second channel that survives greyscale (a check/dot glyph or a 2px inset ring on the knob). Re-measure knob vs track against 3:1 in both themes.
- **Verifier note**: The recommendation is directionally sound (raise ON-track contrast, add a non-color channel) but the severity/effort framing could be tightened: this is a real WCAG 1.4.11 failure but affects only the dark-mode toggle control itself, is S-effort as stated, and 'medium' severity seems reasonable — not inflated. One caveat: the finding's framing that 'shipped default is the 2.74:1 state' is only true for the flash-of-initial-content before js/index.js runs (which immediately re-evaluates via prefers-color-scheme and can flip to light); this nuance doesn't undermine the core finding (both ON-track colors in both themes fail 3:1 regardless of which is 'default'), so no severity change needed, but the recommendation/write-up could clarify that the low-contrast state is reachable in both themes rather than leaning on the 'shipped default' framing.

## F047 [medium] People cards separate from the page by 1.15:1 in light mode with no border, shadow or radius

- **Status**: confirmed · **Effort**: S · **Category**: color · **Lenses**: visual-design
- **Location**: scss/_lightmode.scss:12 / _darkmode.scss:12 ($-card-background); scss/index.scss:174-208 (`card-container($border: none, $shadow: none)`, padding 0.5rem)
- **Evidence**: Card #eeeeee on page #fefefe = 1.15:1; card #333333 on page #0a0a0a = 1.57:1 — both under the 3:1 floor for a mark the reader must follow, and the two themes differ by 1.36x. Foundation's radius is not set, so fill is the only channel. Geometry: 8px of card fill around each photo (454px photo in a 470px card; 287px in 303px). Visible in people-desktop-light-fold.png and crop-people-desktop-light.png.
- **Problem**: In light mode the fill differs from the ground by 16 sRGB levels, so the photo's own edge reads as the card edge and the 8px band around it reads as a printing halo; below the photo the boundary vanishes entirely and adjacent bios in a row run together. Dark mode reads as a different design — panels vs floating photos.
- **Recommendation**: Commit to one channel and apply it identically in both themes: either a border around 2.5:1 against the page plus 2-4px more padding so the mat is deliberate, or drop the panel entirely — no fill, no padding, photo flush to the column, name and bio on the page ground — which also removes the light/dark asymmetry. Re-measure after.
- **Verifier note**: Recommendation is reasonable and proportionate (effort S): pick one differentiation channel (border or fill+padding) and apply symmetrically across themes, or drop the panel treatment. No change needed, though the "3:1 floor" framing borrows a WCAG text-contrast heuristic for what's a non-text decorative boundary — worth noting in the writeup that this is a design/visual-hierarchy heuristic, not a formal accessibility violation, so readers don't conflate it with an a11y compliance failure.

## F048 [medium] The dark-mode toggle has no visible focus indicator

- **Status**: unverified · **Effort**: S · **Category**: keyboard-focus · **Lenses**: behaviour-bugs
- **Location**: ejs/main.ejs:52-56; scss/ux/_switch.scss:7-9
- **Evidence**: `page.focus('#dark-mode-switch')` gives activeElement {id: dark-mode-switch, w:13, h:13, outline: 'auto 1px rgb(16,16,16)', opacity: '0'} — the focusable element is Foundation's hidden 13x13 checkbox at the paddle's corner, so the UA ring paints at zero alpha. The visible 64x32 label receives no focus styling; the only paddle rules are background swaps. Screenshot t5-focus-switch.png shows the paddle unchanged under focus. Space does toggle the theme.
- **Problem**: WCAG 2.4.7 on the site's only real control: it is reachable (tab stop 6) and it works, but nothing on screen says it is focused, so it is usable only by counting tab presses.
- **Recommendation**: Add `.switch-input:focus-visible ~ .switch-paddle { outline: 2px solid; outline-offset: 2px }` with the outline colour from each theme's anchor token. Consider the same for the nav links, whose current ring is the UA default `auto 1px rgb(16,16,16)` — near-invisible on the #0a0a0a dark ground.

## F049 [medium] `<label for="nav-drilldown">Navigate</label>` points at a <ul>, so it labels nothing

- **Status**: unverified · **Effort**: S · **Category**: aria-validity · **Lenses**: behaviour-bugs
- **Location**: ejs/main.ejs:40-41
- **Evidence**: html-validate reports on all three pages: 'valid-for: <label> "for" attribute must reference a labelable form control', selector `#nav > label` (index 1:25346, people 1:25355, research 1:25357). In the browser the label computes to display inline, 56.7x21, and clicking it does nothing since a <ul> is not labelable.
- **Problem**: NAVIGATE renders as a heading but is marked up as a form label for a non-control: screen readers get a label with no labelled element and the nav list has no accessible name, so it is announced as a bare list rather than as navigation. It is an invalid-HTML error on every page.
- **Recommendation**: Wrap the block in `<nav aria-labelledby="nav-heading">` and change the label to `<h2 id="nav-heading" class="sidebar-label">Navigate</h2>` (or a p/span if the outline matters), moving the `label { font-weight: bold; font-variant: all-small-caps }` rule at scss/index.scss:76-80 onto `.sidebar-label` so the DARK MODE label keeps the same look. #dark-mode-label is a legitimate label and can stay.

## F050 [medium] Fragment targets land under the fixed breadcrumb bar, hiding 57px of the page

- **Status**: unverified · **Effort**: S · **Category**: layout · **Lenses**: behaviour-bugs
- **Location**: ejs/main.ejs:63-68, :70; scss/index.scss:42-56
- **Evidence**: Jumping to #body puts scrollY at 357 with #body at top 0.3, while #breadcrumbs-wrapper is position:fixed from top 0 to 57.3 with an opaque themed background and z-index 5. `getComputedStyle('#body').scrollMarginTop` = '0px'; the page <h1> at top 0.3 is fully covered (hiddenPx 57). Screenshot t7-skiplink-lands-under-sticky-crumbs.png.
- **Problem**: Any fragment navigation — the skip link once the base-tag bug is fixed, a shared `people.html#faculty` deep link, a browser find-and-Enter jump — arrives at the right scroll position with the target invisible.
- **Recommendation**: Add `scroll-margin-top: 4.5rem` to #body and to anything that can be an anchor target (simplest: a `:target, #body` rule) inside `breakpoint(medium up)`, since the bar does not stick at small. Verify hiddenPx goes negative.

## F051 [medium] 87.5% of the site's CSS is never used on any page

- **Status**: unverified · **Effort**: M · **Category**: unnecessary-payload · **Lenses**: performance
- **Location**: dist/assets/index.css (52,951 bytes) from scss/index.scss importing Foundation's full component set
- **Evidence**: Chrome DevTools CSS.startRuleUsageTracking accumulated across index, people and research at 1440px plus a 390px load of index: 52,951 total bytes, 6,607 used (12.5%), 46,344 unused (87.5%).
- **Problem**: Every page parses and ships ~46KB of CSS for accordions, off-canvas, orbit carousels, tooltips and dropdowns this three-page site never renders.
- **Recommendation**: Import only the Foundation partials actually used (grid, card, switch, breadcrumbs, sticky, menu) instead of the full foundation.scss, or add a PurgeCSS pass against the three built HTML files as a webpack step.

## F052 [medium] The publish workflow has no post-build validation before force-pushing to gh-pages

- **Status**: unverified · **Effort**: S · **Category**: ci · **Lenses**: build-maintainability
- **Location**: .github/workflows/build-site.yaml:24-30 vs build-check.yaml:32-39
- **Evidence**: build-check.yaml has a 'Check expected pages were produced' step failing the job if dist/index.html, dist/people.html or dist/research.html is missing or empty. build-site.yaml goes straight from `npm run build` to writing CNAME/.nojekyll and publishing via s0/git-publish-subdir-action.
- **Problem**: webpack can exit 0 while emitting a truncated or empty page (a `content` generator returning '' , for instance) — exactly what build-check's extra step exists to catch — and the branch that actually goes live is the one without that net.
- **Recommendation**: Copy the 'Check expected pages were produced' step into build-site.yaml before the publish step.

## F053 [medium] Dart Sass @import deprecation fires today at the newest version the declared semver range already permits

- **Status**: unverified · **Effort**: M · **Category**: dependencies · **Lenses**: build-maintainability
- **Location**: package.json:28 (`"sass": "^1.68.0"`); scss/index.scss:7,8,15,25; scss/_global.scss:11
- **Evidence**: The lockfile pins 1.68.0. Trial-compiling the repo's own scss/index.scss with sass@1.104.0 (satisfying ^1.68.0) via `sass --load-path=node_modules --quiet-deps` exits 0 but prints 5 DEPRECATION WARNING [import] messages, one per repo-owned @import; quietDeps only silences dependency stylesheets, confirmed in the same trial.
- **Problem**: Nothing warns today, but any lockfile refresh, `npm update` or adjacent bump can re-resolve straight to 1.104.0 and start printing five warnings on every build — with @import scheduled for removal in Dart Sass 3.0.
- **Recommendation**: Migrate the five @import sites to @use/@forward as part of a deliberate, tested sass bump; until then pin sass to an exact 1.68.0 (no caret) so a routine install cannot silently jump minors.

## F054 [medium] render-people.js interpolates title, heading, name and alt into HTML with no escaping

- **Status**: unverified · **Effort**: S · **Category**: correctness · **Lenses**: build-maintainability
- **Location**: build/render-people.js:26, 36, 43, 50
- **Evidence**: `<h1>${data.title}</h1>`, `<h2>${section.heading}</h2>`, `alt="${person.alt}"` and `<span class="h3">${person.name}</span>` all interpolate raw JSON strings. Scanning all 50 entries for `"` or `<` in name/alt finds none today, and neither the renderer nor the CI JSON.parse step guards against it.
- **Problem**: CLAUDE.md documents `paragraphs` as intentionally raw HTML, but name/alt/heading/title are meant to be plain text. The first entry whose alt contains a double quote, or whose name carries a stray `<` or `&` from a paste, corrupts the surrounding attribute or breaks out of the tag with `npm run build` still exiting 0 and no audit check catching malformed markup.
- **Recommendation**: Add escapeHtml/escapeAttr helpers in build/render-people.js applied to title, heading, name and alt (leaving paragraphs unescaped as documented), and optionally run the built people.html through a parser in CI to catch malformed attributes before publish.

## F055 [medium] There is no written design canon, so colour, logo and icon decisions cannot be checked

- **Status**: confirmed · **Effort**: M · **Category**: design-canon · **Lenses**: brand-iconography
- **Location**: repo root (no docs/ICONOGRAPHY.md or equivalent); CLAUDE.md
- **Evidence**: CLAUDE.md documents the build, data format, audit script and helper scripts in detail and says nothing about colour roles, the logo, icons or the favicon; scripts/audit_site.py runs 13 content checks and zero visual ones. Four independent drifts documented in this audit — two hexes swapped between roles, a contrast claim written into a comment and wrong by measurement, one distinction named two ways across two pages, and a named token used once — would be caught by no reviewer or script today.
- **Problem**: The visual vocabulary lives only in SCSS variable names, and the names are aliases rather than roles (`logo-desaturated: $-palette-primary`), so the files cannot say which colour means what.
- **Recommendation**: Write a short docs/ICONOGRAPHY.md settling, in order: the token table (one row per role — page ink, muted ink, link, link-hover, logo, current-page marker, card ground, switch-on — one hex per theme with its measured ratio, and a rule that no hex appears twice); logo usage (appearances per page, minimum size, polarity, sparkles dropped in the small variant); the icon rule and its named exceptions; the roster vocabulary; and the exact head block. Then add a `--tokens` mode to scripts/audit_site.py that parses both theme maps, recomputes every ratio against its stated ground and fails on any hex bound to two roles.
- **Verifier note**: Recommendation is reasonable as written; no correction needed.

## F057 [medium] The sidebar mark inverts the logo's polarity and is cropped on all four edges

- **Status**: confirmed · **Effort**: M · **Category**: logo-usage · **Lenses**: brand-iconography
- **Location**: ejs/main.ejs:28-38 (mask id="logo", rect id="logo-rect"); scss/index.scss:160-162
- **Evidence**: Rendered at 6x (sticky-logo-light-6x.png, 468x264): the mark is knocked out of a solid #001f4e rect whose width/height are 100% of the viewBox, and the artwork touches every edge — the diagonal streak cut at bottom-left and top-right, the A's apex at the top edge, at least five sparkles sliced by the left, bottom and right. Rendered size on the page is 77.92x43.70 CSS px, so the ~20 sparkles are 3-4px each. The topper draws the same mark as a positive path on the page ground.
- **Problem**: The site's only persistent mark is a cropped version of the logo in the reverse polarity of the version 300px above it, so the reader has to recognise the same object twice.
- **Recommendation**: Pick one presentation: simplest is to draw the sidebar mark as a positive path in logo-saturated matching the topper and delete the mask/rect. If the knocked-out badge is wanted, inset the artwork ~6% on all sides (widen the viewBox or transform the mask group), drop the sparkles from the small variant, and use the same badge in the topper.
- **Verifier note**: Recommendation is reasonable as written; could optionally clarify that the crop is not sidebar-exclusive (topper shares the same viewBox) but only becomes a legibility problem at the sidebar's small rendered size — this doesn't change the fix needed.

## F058 [medium] A person's role is invisible once their card is more than a screen below its section heading

- **Status**: confirmed · **Effort**: M · **Category**: wayfinding · **Lenses**: ux-ia
- **Location**: build/render-people.js:51-61 (card markup: image, name span, paragraphs)
- **Evidence**: At 390x844, scrollY 18000: Andrew Saydjari's card is on screen while its governing `<h2>ART Associates</h2>` is at y=14,921 (3.6 screens above) and the next heading at 21,753. The card holds only photo, name, a Personal Website line and the bio — no role label. Section spans are large: Postdocs 2,326-9,412; Collaborators 21,753-30,711.
- **Problem**: Category is the most useful fact about a person here — postdoc, external collaborator, or someone who left — and it is carried only by a heading that is off screen for most of the page, including for anyone arriving deep in the page from a search result once anchors exist.
- **Recommendation**: Render a role/affiliation line inside each card under the name, from a new `role` key in data/people.json defaulting to the section heading (e.g. 'Postdoctoral Researcher · Dunlap Institute'), styled as a small-caps eyebrow like the existing .person-link. Optionally add a sticky section label on mobile once a mobile header exists.
- **Verifier note**: Recommendation is reasonable as stated; no correction needed.

## F059 [medium] Collaborators and Recent Alumni get full-weight cards and consume 42% of the People page

- **Status**: confirmed · **Effort**: M · **Category**: information-architecture · **Lenses**: ux-ia
- **Location**: data/people.json (section order and counts); build/render-people.js:34-70
- **Evidence**: Section counts: Faculty 2, Postdocs 9, Grads 7, Undergrads 1, Associates 8, Collaborators 14, Recent Alumni 9 (50 total; 23 of them non-members). Mobile offsets: Collaborators 21,753 -> Alumni 30,711 -> end 37,331 = 15,578 of 37,331px (41.7%); desktop 4,948 of 14,919 (33%). Every entry gets the identical photo-plus-bio card.
- **Problem**: Collaborators and alumni are rendered at exactly the same weight as the working group, so a visitor asking 'who are the current grad students?' or 'is this person still here?' pays for the whole roster, with no search, index or filter across 50 people.
- **Recommendation**: Add a per-section `density` option to data/people.json: full cards for Faculty/Postdocs/Grads/Undergrads, and a compact list (name, affiliation, link, no photo, 3-4 per row) for Collaborators and Recent Alumni — roughly halving the mobile page. Pair with the section jump list, and optionally a client-side name filter over the rendered cards.
- **Verifier note**: Recommendation is reasonable and proportionate as scoped (per-section density flag + compact card variant for Collaborators/Recent Alumni, plus a jump list); the optional client-side filter is a nice-to-have and could be dropped without weakening the core fix. Effort estimate of M is plausible given render-people.js and scss changes needed, though it undercounts slightly if a compact-card CSS variant and jump-list nav are both wanted well-polished (borderline M/L).

## F060 [medium] Research routes 91 clicks off-site with no path to the People page, and leaves 10 roster names unlinked

- **Status**: confirmed · **Effort**: M · **Category**: cross-page-linking · **Lenses**: ux-ia
- **Location**: ejs/pages/research/body.html (.roster-names spans)
- **Evidence**: dist/research.html body has 110 links, 109 external. Parsing .roster-names: 101 name occurrences, 91 wrapped in <a> to a personal homepage, 10 bare text; the four people with no link anywhere on Research are Anika Slizewski, Isabelle (Liyuan) Huang, Phil Van-Lane, Rodrigo Barradas Herrera. In the other direction dist/people.html has 279 body links, all 279 external — zero back to Research or Home. Screenshot roster-desktop.png shows the mixed run.
- **Problem**: The Research page is the natural entry point for a collaborator or journalist and every name on it is an exit door, sending the reader to a third-party site rather than to the bio and photo the site already holds; four members read as plain text among 91 links, which looks like an oversight.
- **Recommendation**: Once People cards have ids, link every roster name to `/people.html#person-<slug>` and keep the external personal-site link on the card where it already exists — all 101 names become clickable and consistent, and the duplicated personal URLs disappear. If an external link is still wanted inline, render it as a small trailing arrow after the internal link.
- **Verifier note**: Recommendation is reasonable as a direction (add id-based anchors on People cards and link roster names to them), though the "M" effort estimate should account for choosing a stable slug scheme and handling name variants (e.g., "Isabelle (Liyuan) Huang" parenthetical) consistently across both files — not just a mechanical link substitution.

## F062 [medium] The undergraduate entry is written in the present tense for a summer program that has ended

- **Status**: confirmed · **Effort**: S · **Category**: stale-content · **Lenses**: copy-language
- **Location**: data/people.json:197-204
- **Evidence**: Line 202: 'Leo is an undergraduate researcher in the <a href="...surp-2/">Summer Undergraduate Research Program (SURP)</a>…' — read on 2026-09-07, after the program has ended. There is also a 'Leo Watson' in Graduate Students, and this bio's first word is 'Leo'.
- **Problem**: The site cannot say whether he is still with the group, in the only card of the Undergraduate Students section; and two people are addressed by the same first name on one page.
- **Recommendation**: Decide the status: if the work continued, put the program in the past tense and the work in the present; if the placement ended, move the entry out of Undergraduate Students (and drop the now-empty section from `sections`). Either way begin the bio 'Leo Wu is…' to disambiguate, and supply a headshot.
- **Verifier note**: Recommendation is reasonable as stated (resolve tense/status, disambiguate the name, add a headshot); no change needed, though the headshot and null-image issue may already be covered by a separate audit finding, in which case that clause could be trimmed to avoid duplication.

## F064 [medium] Gwen Eadie and Josh Speagle are written one way on Research and another on People

- **Status**: confirmed · **Effort**: S · **Category**: consistency · **Lenses**: copy-language
- **Location**: data/people.json:10, :20; ejs/pages/research/body.html:38 and seven further roster rows
- **Evidence**: Diffing every Research roster name against every People name, exactly two differ: people.json 'Gwendolyn Eadie' and 'Joshua S. Speagle (沈佳士)' against research/body.html 'Gwen Eadie' and 'Josh Speagle', repeated across all eight themes. The other 48 match exactly. audit_site.py check [12] does not catch it because it only compares names within the Research page.
- **Problem**: Following 'Gwen Eadie' from a theme lands on a card headed 'Gwendolyn Eadie'; these are the two most-linked names on the site (6 and 7 of 8 themes), so it is the most-repeated inconsistency there is.
- **Recommendation**: Pick one form and apply it end to end — the bios already open 'Gwen is…' and 'Josh is…', so shortening the two People headings is the smaller edit; otherwise change all 15 Research anchor texts. Extend audit check [12] to compare Research anchor text against People `name` fields across pages, since nothing currently catches this class of drift.
- **Verifier note**: Recommendation is reasonable as written — shortening the two People-page headings (or bio-opening style) to match the widely-used short forms is the smaller edit than touching 15 Research anchors, and extending the audit is a fair proactive suggestion, not required to fix the finding itself.

## F065 [medium] People bios and Research roster names render at 14.72px, below the 16px mobile-readability floor

- **Status**: unverified · **Effort**: S · **Category**: typography · **Lenses**: mobile-responsive
- **Location**: scss/index.scss:235 (`.card p { font-size: 0.92rem }`); :382 (`.theme-roster .roster-row`)
- **Evidence**: Computed at 390x844: .card p, .person-link and .roster-row/.roster-names all 14.72px, because 0.92rem resolves off the 16px root rather than the body's 110% (17.6px) — while `#body p` computes 19.712px.
- **Problem**: These are not captions: .card p is the primary bio content for all 50 people and .roster-row is the primary 'who works on this' content on Research. Both sit under the 16px minimum for mobile body text, which some mobile browsers auto-boost, producing an inconsistent look.
- **Recommendation**: Raise both to at least 1rem (16px), or express them against the inherited body size (e.g. 0.85em ≈ 15px). Re-check the card layout afterwards, since `.h3 { min-height: 2.3em }` and line-height may need adjusting. Reconcile with the type-scale finding so the small step is set once, at a readable size.

## F066 [medium] No robots.txt, sitemap.xml or 404 page in the published output

- **Status**: unverified · **Effort**: M · **Category**: discoverability · **Lenses**: seo-sharing
- **Location**: dist/ root; .github/workflows/build-site.yaml (writes only CNAME and .nojekyll); webpack.config.js CopyPlugin (./static -> static only)
- **Evidence**: dist/robots.txt, dist/sitemap.xml and dist/404.html all return 'No such file or directory'; the publish workflow adds nothing else to the dist root.
- **Problem**: No sitemap means no explicit signal of the three canonical URLs (low impact at this size, zero cost to add), and more concretely any stale or mistyped link — from an old CV, a talk slide, a removed anchor — falls through to GitHub Pages' generic unbranded 404, a dead end for exactly the prospective students the site is trying to reach.
- **Recommendation**: Add a `static-root/` directory copied to the dist root by an extra CopyPlugin pattern, holding robots.txt (with the sitemap line), a hand-written 404.html reusing main.ejs's shell with the nav, and sitemap.xml (three URLs, either static or emitted by a small build/ script).

## F067 [medium] No canonical link tag on any page

- **Status**: unverified · **Effort**: S · **Category**: seo · **Lenses**: seo-sharing
- **Location**: ejs/main.ejs:3-8
- **Evidence**: `grep -c 'rel="canonical"'` returns 0 on all three dist pages; only `<base href="/">` is present.
- **Problem**: There is no explicit self-reference. Low risk today with one clean URL per page, but it removes any doubt once the site sees UTM-tagged links (a Statstro mailing, say) or is mirrored.
- **Recommendation**: Emit `<link rel="canonical" href="https://astrostatuoft.com/<pagepath>">` in ejs/main.ejs from a new per-page `path` field in the webpack.config.js pages array (index -> '', people -> 'people.html', research -> 'research.html').

## F068 [medium] Maryum Sayeed's bio describes a data-driven ML method but she is not on the AI for Scientists roster

- **Status**: unverified · **Effort**: S · **Category**: roster-consistency · **Lenses**: content-link-rot
- **Location**: ejs/pages/research/body.html:163; data/people.json (Postdoctoral Researchers, Maryum Sayeed)
- **Evidence**: scripts/theme_fit.py flags her MISSING under AI for Scientists. Her bio: 'She is the lead developer of The Swan, a data-driven method for predicting stellar surface gravities.' The theme intro (body.html:148-155) describes exactly that kind of work. The roster at line 163 lists Speagle, McKinnon, Dey, Xu, Jespersen, Laroche, Van-Lane, Zhang, Huang — not Sayeed, though she appears under Inference and Stellar Evolution.
- **Problem**: A member whose bio explicitly describes building a data-driven tool is absent from the theme whose description most closely matches it — the drift theme_fit.py exists to surface, with the bio evidence clearly supporting the flag rather than being heuristic noise.
- **Recommendation**: Add Maryum Sayeed to the ART members involved row for AI for Scientists (linking https://maryumsayeed.github.io/ to match her People entry), then re-run scripts/sort_themes.py since the theme's size changes.

## F005 [low (was high)] The dark-mode toggle is never persisted — the choice is discarded on every navigation and reload

- **Status**: confirmed · **Effort**: S · **Category**: correctness · **Lenses**: ux-ia, build-maintainability, behaviour-bugs
- **Location**: js/index.js:11-33; CLAUDE.md:166-168
- **Evidence**: Light-preferring context: toggle to dark on index.html -> data-theme='dark', `Object.entries(localStorage)` = []. Click the People nav link -> data-theme='light'. Reloading index.html also returns 'light'. `grep -rn localStorage js/ scss/ ejs/` returns zero matches; lines 18-32 re-derive the theme from matchMedia on every document.ready. CLAUDE.md states the theme is 'persisted to localStorage'. Screenshots t1a/t1b.
- **Problem**: The site's only user control is effectively decorative on a three-page site people navigate between, and the documentation asserts a persistence layer that was never implemented — so anyone told to 'fix theme persistence' hunts for a localStorage bug that does not exist.
- **Recommendation**: In initDarkModeToggle, read `localStorage.getItem('theme')` first (in try/catch — Safari private mode throws), fall back to matchMedia, and write on change. Correct the CLAUDE.md sentence in the same edit.
- **Verifier note**: Recommendation is reasonable as-is (read localStorage with try/catch, fall back to matchMedia, write on change, and fix the CLAUDE.md sentence in the same edit). One addition: the fallback logic should probably still respect matchMedia only when no stored preference exists, and should re-check matchMedia's listener (or not) consistently — but this is a minor implementation detail, not a flaw in the finding.
- **Verifier note**: Recommendation is fine as written (localStorage read-with-fallback + write-on-change, try/catch for private-mode Safari, plus correcting the CLAUDE.md sentence in the same edit) — no change needed to the fix itself, only to the severity label, since this affects a small slice of visitors on a low-traffic static site and causes no functional breakage.

## F021 [low (was high)] Two headshots served as PNG cost ~323KB more than an equivalent JPEG

- **Status**: confirmed · **Effort**: S · **Category**: image-encoding · **Lenses**: performance
- **Location**: static/radu_craiu.png (280,858B, 550x550, RGB); static/renee_hlozek.png (99,132B, 270x270, RGBA)
- **Evidence**: Re-encoded with Pillow at JPEG quality 85: radu_craiu -> 46,413B (83.5% smaller), renee_hlozek -> 10,420B (89.5% smaller); combined saving ~323KB on a page already transferring 3.59MB. Neither uses transparency in a way that matters for a square headshot card.
- **Problem**: Two of fifty headshots account for roughly a tenth of the People page's weight purely because of container choice.
- **Recommendation**: Re-encode both through scripts/add_headshot.py (or `image.convert('RGB').save(..., quality=85, optimize=True)`) and update the `image` fields in data/people.json to the new .jpg filenames — which also resolves their LFS-tracking problem.
- **Verifier note**: Recommendation is technically sound (re-encode via scripts/add_headshot.py and update data/people.json image fields to .jpg) but should be framed as a minor, low-priority cleanup rather than urgent — batch it with other stray-PNG-headshot fixes rather than treating it as a standalone high-priority item.
- **Verifier note**: The recommendation itself is fine as stated (re-encode the two files through scripts/add_headshot.py and update the corresponding image fields in data/people.json). But this belongs on a routine cleanup pass, not flagged as high-priority — on a small academic site there's no traffic/cost pressure that makes a one-time 323KB savings urgent.

## F029 [low (was high)] Subject-verb agreement error in the first bio on the People page

- **Status**: confirmed · **Effort**: S · **Category**: grammar · **Lenses**: copy-language
- **Location**: data/people.json:16
- **Evidence**: Line 16: 'Her research interests includes hierarchical Bayesian inference, generalized linear models, spatial point processes, and time series analysis...'
- **Problem**: A plain agreement error in the first sentence-and-a-half of the first card of the first section — the highest-traffic prose on the site after the home lede.
- **Recommendation**: Change 'Her research interests includes' to 'Her research interests include'; no other change to the sentence.
- **Verifier note**: Recommendation is correct as stated (change 'includes' to 'include'), but severity should be downgraded from 'high' to 'low'/'nit' — it's a one-word grammar fix, not a high-impact defect.
- **Verifier note**: Recommendation is correct as written (change 'includes' to 'include', no other edits) — only the severity label needs correction, from high to low.

## F039 [low (was medium)] Nothing distinguishes leaving the site: 'Statstro' sits in the primary nav styled exactly like the three internal items

- **Status**: confirmed · **Effort**: S · **Category**: link-affordance · **Lenses**: brand-iconography, ux-ia
- **Location**: ejs/main.ejs:46; scss/index.scss:104-112; data/people.json
- **Evidence**: `<li><a href="https://statstro.com/">Statstro</a></li>` has identical markup, identical computed style (rgb(47,85,157), dotted, no decoration) and an identical 78x26 box to Home/People/Research; no icon, rel, title or target. Every `#body a` on all three pages resolves to the same single style. Counts: 8 body links on Home, 279 on People across 130 hosts, 110 on Research (109 external).
- **Problem**: One token carries two roles the reader acts on differently — move within this site, and leave for someone else's. A first-time visitor treats a four-item nav as four sections of this site, and Statstro silently moves them to another domain with no route back; it is the worst place on the site for that failure because it is in the persistent nav.
- **Recommendation**: Do not decorate 279 bios. Mark departure where the two roles sit side by side and are indistinguishable: a small arrow glyph after Statstro only, in the link's colour at 0.75em, aria-hidden with an sr-only '(external site)', plus `rel="noopener"`; and one sentence in the People and Research intros stating the convention ('Names link to personal pages elsewhere'). Fix the Home page's own internal links at the same time.
- **Verifier note**: Recommendation as stated is reasonable and appropriately scoped (single nav item, not touching bios); no changes needed to it, though 'Fix the Home page's own internal links at the same time' is a scope-creep aside that could be dropped or split into a separate low-priority item since it's not the core defect described.

## F040 [low (was medium)] The home page's only handoffs are two adjectival phrases mid-sentence, and the same destination is praised with a different adjective on Research

- **Status**: confirmed · **Effort**: S · **Category**: conversion · **Lenses**: copy-language, ux-ia
- **Location**: ejs/pages/home/body.html:10-12; ejs/pages/research/body.html:8
- **Evidence**: home/body.html:11 `<strong>exciting work</strong>` (-> research.html), :12 `<strong>wonderful people</strong>` (-> people.html); research/body.html:8 `<strong>awesome people</strong>` (-> people.html). The home body has 8 links total, one <h1>, one <h2>, 1959px tall on desktop, with no card, button or visual entry point.
- **Problem**: The home page's job is to hand a visitor to People or Research and it does so only through two pieces of praise buried mid-sentence; the same page is 'wonderful' from Home and 'awesome' from Research. None of the three adjectives tells the reader anything about the destination.
- **Recommendation**: Name the destinations in the link text ('research', 'people') in both files, and add two explicit entry cards or a two-up link block under the lede stating what each holds ('Research: eight themes across astrophysics, statistics and AI'; 'People: 27 members and associates'), plus a third for Join us / Contact.
- **Verifier note**: Recommendation is reasonable in spirit (name destinations explicitly, add a two-up entry block) but the 'add two explicit entry cards plus a third for Join us/Contact' scope is larger than the finding warrants for an 'S' effort estimate — a lighter fix (just swap the adjectives so the same page isn't described two different ways, and optionally make link text destination-named) would resolve the core inconsistency without a redesign.

## F056 [low (was medium)] Member / associate / collaborator is drawn and named two different ways on the two pages that draw it

- **Status**: confirmed · **Effort**: S · **Category**: consistency · **Lenses**: brand-iconography
- **Location**: ejs/pages/research/body.html (8 .theme-roster blocks); data/people.json sections; scss/index.scss:369-408
- **Evidence**: Research repeats a small-caps gutter label 24 times (8 themes x 3 rows): 'ART MEMBERS INVOLVED:', 'ART ASSOCIATES INVOLVED:', 'COLLABORATORS INCLUDE:'. People uses 7 <h2> display headings: Faculty, Postdoctoral Researchers, Graduate Students, Undergraduate Students, ART Associates, Collaborators, Recent Alumni. 'ART Members' appears on Research and nowhere on People, and nothing on either page connects the vocabularies.
- **Problem**: One distinction, drawn 24 times on one page and 7 on the other, in two idioms with two different names; a reader who has learned the People categories has to re-learn them on Research.
- **Recommendation**: Settle the vocabulary once — either add a 'Members' super-heading on People covering Faculty/Postdocs/Grads/Undergrads, or rename the Research rows to 'ART Members (faculty, postdocs, students)' — then share one visual idiom across both pages (they already share the card fill) and record the three terms in the canon.
- **Verifier note**: Recommendation is reasonable in direction but the severity is overstated: this is a naming/IA polish issue, not a broken or misleading content defect — a reader can trivially infer that Research's 'ART members' corresponds to People's Faculty+Postdocs+Grads+Undergrads from context and the shared card styling already cited. Treat as a low-severity copy/IA cleanup (effort S is apt) rather than medium; no urgency to fix before other content-correctness issues.

## F061 [low (was medium)] The People page intro says nothing a reader did not already know

- **Status**: confirmed · **Effort**: S · **Category**: voice · **Lenses**: copy-language
- **Location**: data/people.json:3
- **Evidence**: Complete text: 'The ART is made up of researchers across astrophysics, statistics, and data science spanning a wide range of career stages. More information about individual members of the group can be found below.'
- **Problem**: Thirty-two words carrying one fact already stated in the home lede, plus a second sentence whose content is 'scroll down'. The page's own seven headings already show the career-stage range more precisely, and nothing orients a cold arrival: how big the group is, how ART Associate differs from Collaborator (stated nowhere on the site), or who to contact.
- **Recommendation**: Replace it with prose that does the job the headings cannot — define the three categories in the owner's own terms, and point prospective students and postdocs at the right contacts.
- **Verifier note**: Tighten the intro if desired, but treat 'define ART Associate vs Collaborator' and 'add contacts' as separate, larger content decisions for the site owner rather than folding them into this copy fix.

## F063 [low (was medium)] 'PDF' used as an abbreviation for postdoctoral fellow in three Recent Alumni headings

- **Status**: confirmed · **Effort**: S · **Category**: jargon · **Lenses**: copy-language
- **Location**: data/people.json:434, 443, 488 (and the Ph.D. entries at :426 and five more)
- **Evidence**: Card headings: "David (Dayi) Li (PDF '25-26)", "Michael Walmsley (PDF '23-25)", "Antonio Herrera Martin (PDF '21-24)", against "Mairead Heiger (Ph.D. '26)" and five further (Ph.D. '25) entries. Line 493 is also the only alumni bio that never says where the person is now — it opens 'Antonio (Tony) was a … Postdoctoral Fellow' where the other eight open 'X is now a …'.
- **Problem**: 'PDF' is in-group shorthand that collides with the file format, appears nowhere else on the site to be learned from, and sits in a heading with no surrounding sentence to recover the meaning. The two label shapes are also inconsistent in kind: Ph.D. takes a completion year while PDF takes a range.
- **Recommendation**: Expand and normalise: 'David (Dayi) Li (Postdoc 2025-26)', 'Michael Walmsley (Postdoc 2023-25)', 'Antonio Herrera Martin (Postdoc 2021-24)', and 'Mairead Heiger (Ph.D. 2026)' etc., dropping the apostrophe-year form throughout. Add a current-position opening sentence to the Antonio entry in the pattern the other eight use, or state that it is not known.
- **Verifier note**: The factual claims are accurate, but severity feels overstated at 'medium' for a jargon/copy nit — 'PDF' for postdoctoral fellow is reasonably guessable in an academic listing context (adjacent to 'Ph.D.'), and this doesn't affect functionality or mislead badly. 'Low' fits better. The recommendation itself (expand to 'Postdoc', normalize year format, add a current-position sentence to Antonio's entry) is reasonable and proportionate for a low-effort copy fix.

## F069 [low] Urbanist-BoldItalic.ttf ships in LFS but is declared and referenced nowhere

- **Status**: unverified · **Effort**: S · **Category**: dead-asset · **Lenses**: performance, visual-design
- **Location**: ttf/Urbanist/Urbanist-BoldItalic.ttf (43,900 bytes); scss/_fonts.scss
- **Evidence**: _fonts.scss declares only Urbanist-Bold (normal style); `grep -rn italic scss/` finds only the Inclusive Sans italic face, and no rule combines the Urbanist display mixin with font-style: italic. No markup or style rule can trigger a request for it.
- **Problem**: 43.9KB of LFS-tracked binary with no code path referencing it — repo bloat plus a false signal that bold-italic is an available style.
- **Recommendation**: Delete the file and its LFS entry, or add the missing @font-face if bold-italic display type is actually wanted.

## F070 [low] The footer 'last updated' date is a hand-typed literal

- **Status**: unverified · **Effort**: S · **Category**: maintainability · **Lenses**: build-maintainability, copy-language
- **Location**: ejs/pages/home/body.html:47-48
- **Evidence**: 'It was last updated August 26, 2026.' is a literal string; nothing in ejs/, webpack.config.js or build/ generates or checks it, and the art-website-update skill lists it as a manual checklist step. audit_site.py check [10] on 2026-09-07 reports 'says August 26, 2026 (12 days ago)'.
- **Problem**: The date is only as fresh as the last person who remembered the checklist step; a content change made outside that walk leaves a silently wrong claim on the live site.
- **Recommendation**: Derive it at build time — e.g. `git log -1 --format=%cd --date=format:'%B %-d, %Y' -- data/ ejs/` passed through templateParameters — replacing the hardcoded sentence and removing both the checklist step and audit check [10].

## F071 [low] The two Faculty headshots — the site's most prominent pair — are cropped at completely different scales

- **Status**: unverified · **Effort**: S · **Category**: imagery · **Lenses**: visual-design
- **Location**: static/GwendolynEadie_2018.jpg and Josh Speagle's headshot, side by side under Faculty on people.html
- **Evidence**: people-desktop-light-fold.png: in the 454x454 slot Gwen's head occupies about a third of the frame height with tree bark filling the right half; in the adjacent identical slot Josh's head fills roughly four fifths and is cropped through the top of the hair. crop-people-desktop-light.png shows one card at torso-and-cardigan where the other is still at chin and mouth.
- **Problem**: Same size, adjacent, first thing after the intro — the mismatch reads as carelessness. The rest of the page is more consistent only because most sources happen to be conventional crops; nothing enforces it.
- **Recommendation**: Re-crop both from originals to a stated convention (eyes on the upper third, head about 55-60% of frame height) with `scripts/add_headshot.py --anchor`, checking the output since there is no face detection, and record the convention in CLAUDE.md beside the `image` key.

## F072 [low] Nine unrelated vertical spacing values and eight `<br>` spacers doing work margins already do

- **Status**: unverified · **Effort**: M · **Category**: spacing · **Lenses**: visual-design
- **Location**: scss/index.scss:44, 208, 222, 231, 236, 314, 325, 370, 380, 388, 421, 436, 444, 456; ejs/pages/research/body.html:11,50,91,137,175,215,259,337
- **Evidence**: Authored values: 0.25, 0.35, 0.5, 0.6, 0.75, 1, 2, 2.5, 3.5rem — nine distinct steps off any common grid (0.35 and 0.6 are off a 0.25 step and off each other). On Research the gap above every <h2> measures 43px: a 40px margin-top from `section > h2` plus ~3px of line box from a <br> that the comment at index.scss:418-419 says was already replaced by real margins.
- **Problem**: No spacing scale, so every gap is a local decision. The <br>s are the visible cost — they add font-size-dependent height on top of a deliberate margin, are invisible to anyone reading the SCSS, and their presence or absence silently changes nth-child parity, which is how a spacer ended up deciding which side a photograph sits on.
- **Recommendation**: Define a four- or five-step scale in _global.scss and snap all fourteen authored values to it (0.35 and 0.6 move to 0.25 and 0.5 with no visible change). Delete the eight <br> elements and let `section > h2 { margin-top }` carry the whole gap.

## F073 [low] The sticky sidebar and sticky breadcrumb settle at different top offsets, shearing the two columns apart on scroll

- **Status**: unverified · **Effort**: S · **Category**: layout · **Lenses**: behaviour-bugs
- **Location**: ejs/main.ejs:27 (sidebar .sticky, no data-margin-top) vs :63-64 (#breadcrumbs-wrapper, data-margin-top="0")
- **Evidence**: people.html at 1440x900 scrolled to y=1200, both stuck: {sidebar: 17.59, crumbs: 0, logo: 17.59}. At rest both share top 300. Sampling scrollY 420-550 in 10px steps shows a steady 17.6px offset with no jitter. Screenshot t7-1440-stuck-sidebar-vs-crumbs.png.
- **Problem**: The sidebar block and the breadcrumb bar align at the top of the page and then shear by 17.6px the moment both stick, dropping the ART logo below the breadcrumb line for the rest of the scroll.
- **Recommendation**: Add `data-margin-top="0"` to the sidebar .sticky to match, or give both the same value; if the sticky behaviour moves to CSS, set the same `top` on both.

## F074 [low] An OS light/dark switch after page load is ignored

- **Status**: unverified · **Effort**: S · **Category**: correctness · **Lenses**: behaviour-bugs
- **Location**: js/index.js:18-32
- **Evidence**: A 390x844 context started in dark reports data-theme 'dark'; `emulate_media(color_scheme='light')` plus 500ms leaves it 'dark'. matchMedia is queried once at DOMContentLoaded with no change listener registered.
- **Problem**: Users on automatic day-night switching, or who flip the system setting in another window, keep the stale theme until reload. Minor alone, but the same one-shot-read shape as the persistence bug.
- **Recommendation**: Keep a reference to the MediaQueryList and add a `change` listener that re-applies the theme only while no explicit stored preference exists — fix it in the same edit as persistence.

## F075 [low] Four devDependencies are declared but never used by the build

- **Status**: unverified · **Effort**: S · **Category**: dependencies · **Lenses**: build-maintainability
- **Location**: package.json:19-25; webpack.config.js:97-153
- **Evidence**: style-loader, file-loader and exports-loader appear only in package.json (`grep -rln` excluding node_modules): the CSS rule uses MiniCssExtractPlugin.loader + css-loader, the font/ico/svg rules use webpack 5's built-in asset types, and no exports-loader rule exists. Top-level `csso` ^5.0.5 is required by nothing in the repo; csso-webpack-plugin vendors its own csso ^4.0.2, which is what actually runs.
- **Problem**: Four packages plus their transitive trees are installed, audited and dependency-bumped for zero build benefit, and it is unclear to a future maintainer whether removing them is safe.
- **Recommendation**: Remove style-loader, file-loader, exports-loader and csso from devDependencies, run npm install to regenerate the lockfile, and confirm the build still produces all three pages unchanged.

## F076 [low] babel-loader runs with no babel config and no node_modules exclude

- **Status**: unverified · **Effort**: S · **Category**: build-performance · **Lenses**: build-maintainability
- **Location**: webpack.config.js:139-145
- **Evidence**: The rule is `{ test: /\.js$/, use: ['babel-loader'] }` with no exclude, and no .babelrc/babel.config.* exists anywhere in the repo root.
- **Problem**: babel-loader is invoked on every resolved .js module including jquery and foundation-sites, with no presets to apply — paying parse and re-emit cost on third-party code for no transformation.
- **Recommendation**: Either add `exclude: /node_modules/` plus a real babel.config.js with a target-appropriate preset-env, or drop babel-loader entirely if no transpilation is needed for the project's browser targets.

## F077 [low] People and Research end with no footer — affiliations, credits and the update date exist only on Home

- **Status**: unverified · **Effort**: S · **Category**: trust-signals · **Lenses**: ux-ia
- **Location**: ejs/pages/home/body.html:42-49; ejs/main.ejs:70-73
- **Evidence**: `document.querySelector('footer')` is null on all three pages and body.lastElementChild is SCRIPT. The institutional affiliations (Statistical Sciences, DADDAA, Dunlap, DSI), the credit to Ellen Price and the last-updated line appear only in the home page's p.site-note; People and Research stop after the last card.
- **Problem**: A journalist or collaborator landing on Research or People from a search engine — likelier than the home page — never learns which departments the group belongs to and has no date by which to judge whether the roster is current. The 37,331px People page ends on a headshot with nothing after it.
- **Recommendation**: Move the affiliation/credit/date content into a shared `<footer>` in ejs/main.ejs rendered on all three pages, alongside the nav links and the contact line, with the date generated at build time.

## F078 [low] Five links to Radu Craiu's page use a superseded utstat.toronto.edu domain

- **Status**: unverified · **Effort**: S · **Category**: link-rot · **Lenses**: content-link-rot
- **Location**: data/people.json:169, :316; ejs/pages/research/body.html:46, :87, :295
- **Evidence**: `curl -L https://www.utstat.toronto.edu/craiu` -> 200, redirecting to https://utstat.utoronto.ca/craiu/. All five occurrences (Leo Watson's bio, Radu Craiu's own entry, and the Inference / Stellar Evolution / Dark Matter roster rows) still use the legacy host.
- **Problem**: Nothing is broken for visitors today, but five copies point at a subdomain the university has migrated off; if the redirect is retired there are five stale links to fix at once.
- **Recommendation**: Update all five to https://utstat.utoronto.ca/craiu/ in one pass across data/people.json and ejs/pages/research/body.html.

## F079 [low] Several links redirect to materially different canonical URLs after NASA and NSERC site consolidations

- **Status**: unverified · **Effort**: S · **Category**: link-rot · **Lenses**: content-link-rot
- **Location**: data/people.json (Duo Xu bio — hubblesite.org; Chloe Cheng and Steffani Grondin bios — nserc-crsng.gc.ca); ejs/pages/research/body.html:229, :231
- **Evidence**: curl -L final URLs: hubblesite.org/home -> science.nasa.gov/mission/hubble/; webb.nasa.gov -> science.nasa.gov/mission/webb/; webbtelescope.org/contents/articles/what-are-active-galactic-nuclei -> the science.nasa.gov explainer; www.nserc-crsng.gc.ca -> nserc-crsng.canada.ca/ and its students path -> the canada.ca funding-opportunity page. All 200 today.
- **Problem**: NASA has consolidated its Hubble and Webb microsites and NSERC has moved to canada.ca; the old URLs redirect for now but are no longer canonical.
- **Recommendation**: Update to the canonical URLs next time these paragraphs are touched — not urgent while the redirects resolve.

## F080 [low] The Transients paragraph ends in a 60-word sentence with two closers and a rare/rarely echo

- **Status**: unverified · **Effort**: S · **Category**: prose · **Lenses**: copy-language
- **Location**: ejs/pages/research/body.html:270-278
- **Evidence**: The closing sentence (lines 275-278) measures 60 words — the longest on the page by 8 — running 'Members of the ART are part of the CHIME FRB Collaboration, and work on fleeting signals of several kinds, … developing the statistical methods needed to draw conclusions from events that are rare, brief, and rarely seen twice.' The paragraph opens 'in most cases we get one chance to catch them.'
- **Problem**: Three defects stacked: the sentence ends twice (membership, then the work, then a trailing participial clause), it repeats the root within four words, and the closing triple restates the paragraph's own opening — so it finishes where it started.
- **Recommendation**: Split at the second closer and cut the echo: end the first sentence after '…might not be natural at all.', then 'The methods have to draw conclusions from events that are brief, rare, and seldom seen twice.' Two sentences, one closer, argument unchanged.

## F081 [low] The Milky Way theme defines (MW) and (M31) and never uses either again

- **Status**: unverified · **Effort**: S · **Category**: prose · **Lenses**: copy-language
- **Location**: ejs/pages/research/body.html:186-195
- **Evidence**: Line 187 introduces 'the Milky Way (MW), Andromeda (M31)'; `grep -c 'MW\b'` over the file returns 1 — the definition itself — and M31 likewise appears once. The paragraph's longest sentence is 52 words hanging three coordinated verb phrases off one participial opener, with 'chemodynamical' unglossed. Line 190 capitalises 'The Galaxy' to mean the Milky Way, a convention stated nowhere.
- **Problem**: Two abbreviations are introduced and never cashed in, asking the reader to hold two codes for nothing; the second-longest sentence on the page carries the densest jargon; and a non-astronomer reads the capitalised 'The Galaxy' as a typo.
- **Recommendation**: Drop both parentheticals, change 'The Galaxy' to 'The Milky Way', gloss chemodynamical modelling in a clause, and break the three-verb sentence after the second verb.

## F082 [low] Dark Matter theme: 'exciting new data sets', a lowercase 'universe', and a news-aggregator link doing a term's work

- **Status**: unverified · **Effort**: S · **Category**: prose · **Lenses**: copy-language
- **Location**: ejs/pages/research/body.html:103, :108, :111, :236
- **Evidence**: Line 108: 'How well do our formation theories … hold up against exciting new data sets from Gaia … JWST … DESI … LSST?' — 'exciting' is the only hype adjective left in the eight theme paragraphs, and 'data sets' contradicts 'datasets' at lines 22, 69 and 154. Lines 103 and 111 write 'the universe' lowercase while lines 228, 233 and 271 capitalise it. Line 236 anchors the term 'high redshift' to a Yahoo News New Zealand aggregator page headlined 'NASA Webb telescope spots impossible…'.
- **Problem**: Three small wobbles the reader meets within two screens: a hype adjective the rest of the page avoids, both spellings of the same word, and a definitional-looking link pointing at an unstable aggregator URL in a claim register ('impossible') the page is otherwise careful not to use.
- **Recommendation**: Change line 108 to 'hold up against new data from…', capitalise Universe at 103 and 111, and repoint 'high redshift' at a stable definitional source (Wikipedia), matching how globular clusters and stellar streams are already linked in the same paragraph.

## F083 [low] Four of five scripts/*.py helpers have no test coverage, including the one that rewrites a tracked file

- **Status**: unverified · **Effort**: M · **Category**: test-coverage · **Lenses**: build-maintainability
- **Location**: scripts/roster.py, scripts/sort_themes.py, scripts/theme_fit.py, scripts/add_headshot.py; scripts/test_audit.py
- **Evidence**: scripts/test_audit.py is thorough — 26 regression cases over audit_site.py's `mentioned`, `caption_names`, `academic_year` and `theme_rosters`, all passing — but it imports nothing from the other four scripts, and no other test file does either.
- **Problem**: sort_themes.py rewrites ejs/pages/research/body.html in place under `--apply`, reordering <h2> blocks by roster size — a destructive operation on hand-authored HTML with no test guarding its parsing and reordering, while the analogous parser in audit_site.py is well guarded.
- **Recommendation**: Add regression tests for sort_themes.py at minimum: a fixture body.html in known-wrong order, asserting `--apply` produces the expected order and is byte-stable on a second run.

## F084 [nit] The status note and the website link use two different idioms inside the same card

- **Status**: unverified · **Effort**: S · **Category**: consistency · **Lenses**: brand-iconography
- **Location**: data/people.json (Gwendolyn Eadie); scss/index.scss:241-251
- **Evidence**: crop-people-desktop-light.png shows 'PERSONAL WEBSITE' as a blue small-caps label (keyed off the person-link class at index.scss:247-251) directly above 'On leave November 2025-2026.' set as bold body prose. Parsing data/people.json for status-shaped paragraphs returns exactly one match.
- **Problem**: Two pieces of card metadata, adjacent, in two idioms — the bold sentence reads as an unusually emphatic first line of the bio rather than a standing fact about the person.
- **Recommendation**: Do not invent a status token for one occurrence. Add a `person-note` class in build/render-people.js for a paragraph whose whole content is a `<b>`, styled like .person-link but in muted ink, so the card reads label / label / prose. Revisit if a second note appears.

## F085 [nit] The footer runs affiliations, a design credit and a date into one paragraph with an ambiguous 'It', and the two photo captions use different shapes

- **Status**: unverified · **Effort**: S · **Category**: voice · **Lenses**: copy-language
- **Location**: ejs/pages/home/body.html:42-49, :17, :39
- **Evidence**: Lines 46-48: 'This website was built and designed with the gracious help of Ellen Price. It was last updated August 26, 2026.' Caption line 17 reads 'ART Group photo (Summer 2025). From left to right: …' with 'Group' capitalised mid-sentence and a parenthetical '(with Alejandro Ortega Cruz Prieto featured in the background)', against line 39's 'Group photo from Statstro 2026.'
- **Problem**: One paragraph carries three unrelated things, and 'It was last updated' can attach to the website or to the credit sentence's subject; a bare 'last updated' also does not say what was updated. The two captions are inconsistent in shape and capitalisation.
- **Recommendation**: Split the block: keep the affiliations as their own paragraph, then a separate site-note line 'Site design by Ellen Price. Content last updated 26 August 2026.' with the date stamped at build time. Normalise the first caption to 'Group photo, summer 2025. From left to right: …' and rephrase the parenthetical plainly.

## F086 [nit] The `no-js` class on <html> is dead markup

- **Status**: unverified · **Effort**: S · **Category**: dead-code · **Lenses**: build-maintainability
- **Location**: ejs/main.ejs:2; js/index.js
- **Evidence**: `<html class="no-js" lang="en" data-theme="dark">`; `grep -rn no-js js/ scss/` finds only that declaration — no .no-js selector in any SCSS file and no classList.remove call in the JS.
- **Problem**: A progressive-enhancement pattern with neither half implemented: it does nothing today but reads as though it should, which will mislead the next person who tries to rely on it.
- **Recommendation**: Remove the class, or implement both halves (a `.no-js` rule in SCSS and a `document.documentElement.classList.remove('no-js')` early in js/index.js).

## F087 [nit] README.md is two lines; all onboarding lives only in CLAUDE.md

- **Status**: unverified · **Effort**: S · **Category**: documentation · **Lenses**: build-maintainability
- **Location**: README.md
- **Evidence**: Full contents: '# astrostat_uoft' and 'Astrostatistics Research Team (ART) Website'. Every build, LFS, preview, architecture and helper-script instruction lives exclusively in CLAUDE.md (8.8KB), framed as agent instructions.
- **Problem**: A human contributor or reviewer landing on the GitHub repo page sees no dev-workflow content in the file GitHub renders by default.
- **Recommendation**: Move the Development Workflow section into README.md with CLAUDE.md referencing it, or add a short README pointing explicitly at CLAUDE.md as the setup source.

## F088 [nit] Obsolete X-UA-Compatible meta tag still shipped

- **Status**: unverified · **Effort**: S · **Category**: cleanup · **Lenses**: seo-sharing
- **Location**: ejs/main.ejs:5
- **Evidence**: `<meta http-equiv="x-ua-compatible" content="ie=edge" />` present verbatim and rendered on all three dist pages.
- **Problem**: The tag exists only to force IE's rendering mode; IE is fully retired, so it is dead markup.
- **Recommendation**: Delete the line.

## F089 [nit] Methodology caveat: 12 external links could not be verified from this environment

- **Status**: unverified · **Effort**: S · **Category**: methodology-caveat · **Lenses**: content-link-rot
- **Location**: links.tsv rows for yorku.ca (5), physics.yorku.ca, banting.fellowships-bourses.gc.ca, www.jwst.nasa.gov, www.ligo.caltech.edu (2) — CURL_ERR(60); chime-frb.ca, kremer.northwestern.edu, linanecib.com — CURL_ERR(56)
- **Evidence**: curl with the session CA bundle still fails 'unable to get local issuer certificate', reproduced with Python requests. The proxy status endpoint logs the CURL_ERR(56) hosts as 'connect_rejected: gateway answered 502 to CONNECT' — a proxy-side event, not a destination response. www.cita.utoronto.ca failed the same way on the first pass and returned 200 on retry.
- **Problem**: Not a finding about the website — a limitation of this link-check run, recorded so these URLs are treated as neither passing nor broken.
- **Recommendation**: Re-check these 12 hosts from an unrestricted network before acting either way.

## F090 [nit] Methodology caveat: 13 external links return 403 to automated requests, likely bot-blocking

- **Status**: unverified · **Effort**: S · **Category**: methodology-caveat · **Lenses**: content-link-rot
- **Location**: links.tsv: datasciences.utoronto.ca (x3), three github.com repos, www.astro.umontreal.ca/~lpl/, www.columbia.edu, eventhorizontelescope.org, web.astro.princeton.edu, www.ox.ac.uk, www.turing.ac.uk/people/researchers/anna-scaife, skyandtelescope.org
- **Evidence**: All 13 returned HTTP 403 to curl with a browser User-Agent through the proxy. GitHub, university WAFs and news sites commonly 403 non-browser clients; 13 unrelated domains failing identically is consistent with anti-bot blocking rather than 13 broken pages.
- **Problem**: These cannot be reported as broken — a curl request is not what a real visitor's browser sends, and these hosts differentiate.
- **Recommendation**: Spot-check two or three in a real browser (datasciences.utoronto.ca first, since several bios link it); do not action the rest without that check.

# Gaps raised by the completeness critic


## Nobody compared the site to the owner's own site, joshspeagle.com, which has already solved six of the confirmed findings
- **Why**: Same PI, same field, and joshspeagle.com links to astrostatuoft.com four times — including from a "Join Our Team" section — so visitors cross between them and the two read as different organisations. More usefully, the sibling site already ships the exact things six confirmed ART findings ask for: a generated token system, real font weights, a fluid type scale, OG metadata, aria-current on the nav, rel=noopener on external links. The tune-up should port an existing, owner-approved system rather than invent a second one, and the "no written design canon" finding has a ready answer next door. It also reframes the "no contact information" finding: the recruitment funnel already exists on the personal site (mailto:j.speagle@utoronto.ca, a #join section) and dead-ends on the ART site.
- **Check**: curl https://joshspeagle.com/ and its assets/css/tokens.css and assets/css/fonts.css; compare against scss/_lightmode.scss, _darkmode.scss, _global.scss, _fonts.scss and the compiled dist/assets/index.css. Grep joshspeagle.com's HTML for links back to astrostatuoft.com.
- **Observed**: joshspeagle.com/assets/css/tokens.css is machine-generated ("generated from assets/data/tokens.json by scripts/build_tokens.py. Do NOT hand-edit") and defines --font-serif/--font-sans/--font-mono, a clamp() scale (--fs-display through --fs-label), an 8-step --space-1..9 scale, four radii, and named colour roles in both a default dark and a [data-theme="light"] block (--bg-0 #06080f / #f6f6f1, --text, --text-2, --text-3, --violet, --cyan, --blue, five --cat-* categoricals, two shadows). fonts.css self-hosts Inter (300/400/500/600/700 + italic) and Source Serif 4 (400/600/700 + italic) as WOFF2, every face with font-display: swap. The page carries og:type/og:site_name/og:locale/og:title/og:description and a meta description; its nav uses aria-current="page" and its external links use target="_blank" rel="noopener". ART, by contrast: two @font-face families as unhashed TTF with no font-display and no bold face (scss/_fonts.scss:1-20), colour defined as two Sass maps with no shared vocabulary (_lightmode.scss/_darkmode.scss), zero OG tags, zero aria-current, zero rel=noopener (grep 'noopener' dist/*.html = 0 on all three pages). joshspeagle.com links to https://astrostatuoft.com/ 4 times and carries mailto:j.speagle@utoronto.ca plus a 'Join Our Team' anchor; the ART site has no email address anywhere.

## jQuery is imported by source but declared in no package.json — the build only works because it is a peer dependency of foundation-sites
- **Why**: js/index.js:1 does `import * as $ from 'jquery'`, but jquery appears nowhere in package.json. It resolves today only because npm 7+ auto-installs foundation-sites' peer dependency. Under `--legacy-peer-deps`, `--omit=peer`, pnpm's default isolated layout, or yarn 1, `npm install && npm run build` fails outright. CI compounds this by running `npm install` rather than `npm ci`, so the lockfile is advisory and the resolution can drift between runs. This also changes the sequencing of the confirmed "drop jQuery plus the entire Foundation plugin set" recommendation: the undeclared import must be either declared or removed, and it cannot simply be left alone if Foundation goes.
- **Check**: grep jquery package.json; npm ls jquery; inspect package-lock.json's node_modules/jquery entry; then move node_modules/jquery aside and run npm run build.
- **Observed**: `grep -n jquery package.json` → no match (package.json has no `dependencies` block at all; all 16 packages are devDependencies). `npm ls jquery` → `astrostat_uoft@1.0.0 └── foundation-sites@6.8.1 ├── jquery@3.7.1`. package-lock.json's node_modules/jquery entry is `{"version":"3.7.1", "dev": true, "peer": true}` and foundation-sites has no `dependencies` field. With node_modules/jquery temporarily moved aside, `npm run build` emitted `webpack 5.101.3 compiled with 33 errors`, e.g. `Cannot find module 'jquery'` while analyzing node_modules/foundation-sites/js/foundation.util.touch.js. Restored and rebuilt; dist/index.html is byte-identical to the live site again. .github/workflows/build-check.yaml:34 runs `npm install`, not `npm ci`.

## www.astrostatuoft.com does not resolve — every lens audited the build, nobody audited the live domain
- **Why**: Anyone who types or is auto-linked to www.astrostatuoft.com gets a DNS failure, not a redirect. This is a live, user-facing defect on the deployed site that no amount of source-level fixing touches, and GitHub Pages handles it for free once a www CNAME record exists (Pages then 301s www → apex). It is the single cheapest fix in the whole audit and it is invisible from the repo.
- **Check**: getent hosts www.astrostatuoft.com and getent hosts astrostatuoft.com; curl -I http://astrostatuoft.com/ to check HTTPS enforcement; curl -I https://astrostatuoft.com/ | grep -i strict for HSTS.
- **Observed**: `getent hosts www.astrostatuoft.com` → no A/AAAA record. `getent hosts astrostatuoft.com` → four GitHub Pages addresses (2606:50c0:800{0,1,2,3}::153). http→https works: `curl -I http://astrostatuoft.com/` → 301 to https://astrostatuoft.com/. No Strict-Transport-Security header is returned on the https response. Separately verified while here: the live site is byte-identical to the local build on all three pages (index 29,242 B, people 76,106 B, research 47,238 B all `cmp` clean against dist/), so there is no gh-pages drift — that assumption, which several findings rest on, holds.

## data/people.json has no structured fields for role, links, research themes or alumni year — three separate confirmed recommendations all require the same schema change nobody proposed
- **Why**: Every person object carries only name, image, alt, paragraphs and (for grads) cohort. Role, personal website, institution and alumni year exist only as free-form HTML inside `paragraphs`. That means three confirmed findings cannot actually be implemented as written: schema.org Person markup has no jobTitle/url/affiliation to emit; "a person's role is invisible once their card scrolls" has no role field to surface; and "Research theme rosters are hand-duplicated with no source of truth" cannot be generated from people.json because no person carries a themes list. All three need one schema extension, and doing it once is a different (and much better) piece of work than doing three patches. It also affects the confirmed "44 links share the identical text 'Personal Website'" finding — the link URL is buried in prose, so it cannot be relabelled programmatically.
- **Check**: Parse data/people.json and enumerate the key set on every person object; check for any key the renderer or audit would use for role/theme/url.
- **Observed**: Across 50 people in 7 sections the only keys present are name, image, alt, paragraphs and cohort — no unknown keys, no role, no url, no themes, no year. Section counts: Faculty 2, Postdoctoral Researchers 9, Graduate Students 7, Undergraduate Students 1, ART Associates 8, Collaborators 14, Recent Alumni 9. build/render-people.js consumes exactly those keys. ejs/pages/research/body.html stores roster names as bare text spans with no id linking back to a person record.

## Presentation is stored inside the content data file: Foundation grid classes live in data/people.json
- **Why**: Each section carries `"grid": "small-up-1 medium-up-3"` — raw Foundation class names — in the file CLAUDE.md and the art-website-update skill send maintainers to for content edits. This is a direct conflict with two confirmed recommendations: purging the 87.5% of unused CSS (or replacing Foundation) silently breaks the People layout unless people.json is rewritten in the same change, and the critical "People page renders ~37,000px tall on phones" fix is a *data* edit, not a CSS edit, so it will not be found by anyone working in scss/. It is also the reason a non-technical roster edit can change page layout.
- **Check**: grep '"grid"' data/people.json; confirm those class names exist in the compiled CSS; read build/render-people.js to see they are emitted verbatim.
- **Observed**: data/people.json contains `"grid": "small-up-1 medium-up-2"` (×1), `"small-up-1 medium-up-3"` (×5) and `"small-up-1 medium-up-4"` (×1). All of small-up-1, medium-up-2, medium-up-3 and medium-up-4 are present in dist/assets/index.css, emitted by `@include foundation-xy-grid-classes` (scss/index.scss:19). The strings pass straight through build/render-people.js into the section wrapper's class attribute.

## CI validates nothing about the output — no HTML validation, link check, or a11y scan — and the content audit that does exist reports clean today
- **Why**: build-check.yaml only parses the JSON, runs the audit helper unit tests, builds, and asserts three files are non-empty. A single HTML validator step would have caught three separately-confirmed findings before merge (an <img> with no src, `<label for="nav-drilldown">` pointing at a <ul>, and Drilldown's invalid injected ARIA attribute). Meanwhile scripts/audit_site.py — the project's one quality gate — reports 2 benign findings today while ~80 real defects stand, and its name-consistency check has a specific blind spot: it compares name forms only *across Research themes*, never People-vs-Research, which is exactly the confirmed drift it fails to catch. Recommending fixes without recommending the guardrail means the same class of defect returns on the next roster update.
- **Check**: Read .github/workflows/build-check.yaml; ls for eslint/stylelint/htmlvalidate/pa11y/lighthouse configs; grep package.json for lint/test scripts; run python3 scripts/audit_site.py and read scripts/audit_site.py around line 425.
- **Observed**: build-check.yaml steps: checkout, setup-node 18, `node -e "JSON.parse(...)"`, `python3 scripts/test_audit.py`, `npm install && npm run build`, then a loop asserting dist/{index,people,research}.html is non-empty. No eslint/stylelint/htmlvalidate/prettier/pa11y/lighthouse config exists in the repo and package.json has exactly one script (`build`). `python3 scripts/audit_site.py` → "2 finding(s)": Leo (Hanbang) Wu has no photo, and the 2025 home-page group photo is one academic year old. scripts/audit_site.py:425 comments "12. the same person written two different ways across themes" — scoped to Research only. Concretely: data/people.json says 'Gwendolyn Eadie' and 'Joshua S. Speagle (沈佳士)'; ejs/pages/research/body.html says 'Gwen Eadie' 6× and 'Josh Speagle' 7×; audit checks 5 and 12 both report 0.

## 12 npm advisories (7 high) and no dependency-update mechanism at all
- **Why**: The build-backend lens covered Node 18 EOL and stale action majors but not the dependency tree itself. There is no dependabot.yml and no renovate config, so nothing will ever propose an update; combined with `npm install` (not `npm ci`) in CI, the toolchain both rots and drifts. To be accurate about severity: `npm audit --omit=dev` reports 0 vulnerabilities, so nothing reaches a visitor — this is a build/CI supply-chain exposure (a compromised transitive dep executing in the Actions runner that holds write access to gh-pages), not a site security hole. Worth saying plainly so it is not over- or under-prioritised.
- **Check**: npm audit and npm audit --omit=dev; ls -a .github/ for dependabot.yml; check for renovate.json.
- **Observed**: `npm audit` → "12 vulnerabilities (2 low, 3 moderate, 7 high)": serialize-javascript RCE and ReDoS via copy-webpack-plugin and terser-webpack-plugin, plus two webpack buildHttp allowedUris/SSRF advisories. `npm audit --omit=dev` → "found 0 vulnerabilities". `ls -a .github/` → only `workflows/`; no dependabot.yml, no renovate.json anywhere in the repo. devDependency majors are 2023-era (copy-webpack-plugin ^11, sass-loader ^13, css-loader ^6, babel-loader ^9, webpack-cli ^5).

## Licensing and attribution: no LICENSE file, and the OFL font licences and Material Symbols notice are never shipped with the assets that require them
- **Why**: package.json declares `"license": "MIT"` but there is no LICENSE file in the repo, so the declaration is unenforceable and the 50 identifiable people's photographs it contains have no stated terms or documented removal path (LFS history retains a departed member's photo permanently — the audit's "unreferenced files in static/" check surfaces the symptom but nothing addresses the retention question). Separately, both bundled typefaces are SIL Open Font License, which requires the licence and copyright notice accompany redistribution: ttf/*/OFL.txt exists in the repo but webpack's CopyPlugin copies only ./static, so the fonts are served from /assets/*.ttf with no licence beside them. The two Material Symbols SVGs (Apache-2.0, attribution required) are inlined into the bundle with no NOTICE. This is a whole compliance dimension no lens touched, and it is nearly free to fix.
- **Check**: ls for a LICENSE file; grep license in package.json; find ttf -name 'OFL*'; find dist -iname '*licen*' -o -iname '*OFL*'; cat dist/assets/index.bundle.js.LICENSE.txt; read svg/README.md and the CopyPlugin config in webpack.config.js.
- **Observed**: No LICENSE/LICENCE/COPYING at repo root; package.json:9 says `"license": "MIT"`. ttf/Inclusive_Sans/OFL.txt and ttf/Urbanist/OFL.txt exist in the repo. The only licence artefact in dist/ is dist/assets/index.bundle.js.LICENSE.txt, which contains solely the jQuery 3.7.1 MIT banner; the three shipped faces (dist/assets/fonts-InclusiveSans-Regular.ttf, -Italic.ttf, fonts-Urbanist-Bold.ttf) ship with no OFL text. svg/README.md says only "Icons in this directory are from Google's Material Symbols. Please see their documentation and license" — that note is not carried into the built site; js/index.js:4-5 imports both SVGs into the bundle.

## The site never states what the group has produced — no publications, papers, news or events anywhere
- **Why**: The Research page describes eight themes in prose with not a single citation, and there is no news, no talks, no events and no publication list on any page. The only freshness signal on the entire site is a hand-typed "last updated" date in the home-page footer (itself a confirmed low finding). A prospective student or collaborator cannot answer "is this group active, and what have they actually done?" — which is the primary job of an academic group site and the reason people arrive from the PI's 'Join Our Team' link. No lens covered site-level content strategy or information scent; they audited the pages that exist rather than asking what page is missing. There is also no data file or feed that a publications section could be built from, so this interacts with the schema gap above.
- **Check**: grep -io 'publication|arxiv|ads.harvard|preprint|paper|news|talk|seminar' across dist/*.html; compare with the nav of joshspeagle.com.
- **Observed**: Across all three built pages the combined grep for publication/arxiv/ads.harvard/preprint/paper/news returns exactly 2 hits, both the word "news" on research.html (the news-aggregator link already flagged as a low finding). Zero arXiv, ADS, DOI or journal links site-wide. The nav is four items: Home, People, Research, Statstro. joshspeagle.com's nav by comparison carries Publications, Software, Talks, Teaching, Mentorship, Biography, News, Awards, Service and a CV PDF.

## Three confirmed findings are actually one chain — fixing any of them alone still leaves deep links broken
- **Why**: `<base href="/">` sending fragments to the home page (critical), "no section or person anchors on either long page" (high), and "fragment targets land under the fixed breadcrumb bar" (medium) are filed as three independent items, but they are sequential dependencies on one feature. Remove the base tag and there is still nothing to link to; add anchors while the base tag stands and they still route to home; do both and every target lands 57px under the sticky bar. Whoever schedules the work needs to see them as one unit or the feature will be reported fixed while still not working. A related, unstated consequence of the same base tag plus root-absolute URLs: dist/ cannot be previewed from file:// or served from any subpath (a PR preview, a staging URL), which is why every lens needed a server rooted at /.
- **Check**: grep the built HTML for the base tag and for the shape of every internal href; then in a browser click a fragment link on people.html and observe where it lands.
- **Observed**: dist/index.html head contains `<base href="/">`. Every internal reference in the built pages is root-absolute: `/people.html`, `/research.html`, `/static/...`, `/assets/index.css`, `/assets/index.bundle.js` — there is not one relative path, so opening dist/index.html directly, or hosting under a subpath, breaks all CSS, JS, images and navigation. The People page emits `<h1>People` then seven bare `<h2>` section headings (Faculty, Postdoctoral Researchers, Graduate Students, Undergraduate Students, ART Associates, Collaborators, Recent Alumni) with no id attributes; Research emits `<h1>Research` and eight bare `<h2>`.

## No print or PDF consideration anywhere — the People roster prints to 22 pages with the topper and an empty sidebar column on every one
- **Why**: Nobody looked at print, and academic rosters do get printed and PDF'd (visitor packets, committee handouts, grant appendices). The 52,951-byte stylesheet contains no print rules of the site's own — the single `@media print` occurrence is Foundation's shared `print, screen and (min-width:40em)` heading-size block. Consequences measured under print emulation: the 300px topper still occupies a third of page one, the sidebar still reserves ~170px of every page for navigation chrome that means nothing on paper, cards split across page breaks because nothing sets break-inside: avoid, and the 44 "Personal Website" links print as bare unresolvable words because no rule expands href. Honest severity: low. It is included because it is a dimension with zero coverage, and a ten-line @media print block fixes all of it.
- **Check**: Search dist/assets/index.css for @media print and read the matched block; then in Playwright call page.emulate_media(media='print'), measure #topper and #sidebar geometry, and page.pdf() the People page.
- **Observed**: The only @media print in dist/assets/index.css is 189 bytes long: `@media print,screen and (min-width:40em){.h1,h1{font-size:3rem}...}` — Foundation's heading scale, no print-specific rules. Under Chromium print emulation on people.html: #topper height 300px, #sidebar width 169.98px, in both light and dark. page.pdf() produces a 22-page, 4.3MB PDF. Chromium forces black text and drops backgrounds in print, so dark mode does not print invisibly — that particular worry is not real; the wasted chrome, the un-expanded links and the split cards are.

## The undergraduate section is a one-person section and the roster has no policy for sections that empty out or grow without bound
- **Why**: Two confirmed findings touch this obliquely — "Collaborators and Recent Alumni get full-weight cards and consume 42% of the People page" and "the undergraduate entry is written in the present tense for a summer program that has ended" — but neither asks the structural question: what happens to a section when it has one member, or none, and what bounds Recent Alumni. Undergraduate Students currently renders a `medium-up-3` grid containing exactly one card (the one with no photo), so the section header, the grid and the broken-image glyph are all spent on a single stale entry; a summer-only program will empty it entirely next cycle and nothing in the renderer or the skill says whether an empty section should disappear. Recent Alumni has 9 entries and no year field and no retention rule, so it grows monotonically and will eventually dominate the page. These are cheap decisions to make now and expensive to retrofit once the design is rebuilt around today's counts.
- **Check**: Count people per section in data/people.json; read build/render-people.js for empty-section handling; read .claude/skills/art-website-update/SKILL.md for a stated policy on empty sections or alumni retention.
- **Observed**: Section sizes: Faculty 2, Postdoctoral Researchers 9, Graduate Students 7, Undergraduate Students 1, ART Associates 8, Collaborators 14, Recent Alumni 9 — 50 total. Undergraduate Students carries `"grid": "small-up-1 medium-up-3"` for its single member, Leo (Hanbang) Wu, who is also the sole `"image": null` entry and the sole finding of the audit's check 7. Collaborators + Recent Alumni = 23 of 50 people (46% of entries). No person record carries a year or end-date field, and the 517-line art-website-update SKILL.md documents how to move someone into Recent Alumni but states no rule for when they leave it or what to do with a section that reaches zero.