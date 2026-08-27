#!/usr/bin/env python3
"""Cross-check Research theme rosters against what people's bios actually say.

    python3 scripts/theme_fit.py                # every theme
    python3 scripts/theme_fit.py Galaxies       # one theme (substring, case-insensitive)
    python3 scripts/theme_fit.py --quiet        # findings only, skip the confirmed list

For each theme this reports two directions, and both matter:

  MISSING  someone whose People-page bio uses this theme's vocabulary but who is
           not on the theme. Usually a real omission.
  THIN     someone listed on the theme whose bio contains none of it, *and* whose
           bio is long enough that it had a fair chance to. Short collaborator
           bios are skipped rather than reported, since a two-sentence entry
           cannot be expected to name every theme its author works on.

It is a *prompt*, not a verdict. Keyword presence is not membership: read the
quoted phrase, decide, and take it to the user with the evidence attached. A
theme's vocabulary also drifts, so when a theme is renamed or rescoped, update
its entry in THEME_WORDS below or the check quietly stops finding anything.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
PEOPLE = os.path.join(ROOT, 'data', 'people.json')
RESEARCH = os.path.join(ROOT, 'ejs', 'pages', 'research', 'body.html')

# Sections whose people are candidates for a theme at all.
CANDIDATE = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students',
             'ART Associates', 'Collaborators'}

# Vocabulary per theme. Keyed by a substring of the <h2>, so a retitle that keeps
# the key word still matches. Keep these broad: they are a net, not a definition.
THEME_WORDS = {
    'Star Formation': r'star[- ]form\w*|molecular cloud\w*|protostar\w*|young star\w*|'
                      r'stellar nurser\w*|feedback|outflow\w*|turbulence',
    'Stellar Evolution': r'stellar (?:evolution|population\w*|astrophysics)|asteroseismolog\w*|'
                         r'white dwarf\w*|binar\w+ star\w*|M[- ]dwarf\w*|stellar flare\w*|'
                         r'variable star\w*|metal[- ]poor|surface gravit\w*|stellar dating|'
                         r'gravitational wave\w*|magnetic activit\w*',
    'Milky Way': r'Milky Way|Galactic|Galaxy\b|globular cluster\w*|stellar stream\w*|'
                 r'astrometr\w*|chemodynamic\w*|interstellar|dust|Gaia|Local Group',
    'Inference': r'Bayesian|hierarchical|inference|MCMC|Markov chain|uncertaint\w*|'
                 r'conformal|model (?:selection|comparison)|sampling|nonparametric\w*|'
                 r'simulation-based inference|calibrat\w*|misspecification|statistic\w*|'
                 r'data science|point process\w*|outlier detection|dimensionality reduction',
    'Dark Matter': r'dark matter|dark energy|cosmolog\w*|halo\w*|large[- ]scale structure|'
                   r'cosmic microwave background|CMB|reionization|DESI|Euclid|lensing|'
                   r'ultra[- ]diffuse',
    'AI': r'machine learning|deep learning|neural network\w*|foundation model\w*|\bAI\b|'
          r'statistical learning|'
          r'artificial intelligence|interpretab\w*|explainab\w*|emulator\w*|'
          r'generative model\w*|normalizing flow\w*|transformer\w*|embedding\w*|'
          r'representation learning|computational imaging|data[- ]driven',
    # "our galaxy" / "the Galaxy" means the Milky Way, so require the plural or an
    # explicit galaxy-formation phrase rather than the bare stem.
    'Galaxies': r'galaxies|galaxy (?:formation|evolution|survey\w*|cluster\w*)|quench\w*|'
                r'quiescent|stellar mass|high[- ]redshift|photometric redshift|morpholog\w*|'
                r'supermassive black hole\w*|JWST|reionization|distant galax\w+',
    'Transients': r'transient\w*|supernova\w*|\bFRB\w*|fast radio burst\w*|magnetar\w*|'
                  r'time[- ]domain|CHIME|technosignature\w*|SETI|extraterrestrial|'
                  r'kilonova\w*|explosi\w*',
}

ROSTER_LABELS = ('ART members involved', 'ART associates involved', 'Collaborators include')

# Below this length a bio simply has no room to mention a theme, so silence on it
# says nothing. Roughly the length of the shorter collaborator entries.
THIN_MIN_WORDS = 55


def load_helpers():
    """Reuse audit_site.py's name matching rather than reimplementing it."""
    src = open(os.path.join(HERE, 'audit_site.py'), encoding='utf-8').read().split('def main(')[0]
    ns = {}
    exec(src, ns)
    return ns['mentioned']


def themes(html):
    """[(title, roster_text)] in page order."""
    out = []
    parts = re.split(r'<h2>(.*?)</h2>', html, flags=re.S)
    for i in range(1, len(parts), 2):
        title = re.sub(r'&amp;', '&', parts[i]).strip()
        names = []
        for label in ROSTER_LABELS:
            m = re.search(label + r':</strong>(.*?)(?:<br>|</p>)', parts[i + 1], re.S)
            if m:
                names.append(re.sub(r'<[^>]+>', ' ', m.group(1)))
        out.append((title, ' , '.join(names)))
    return out


def words_for(title):
    for key, pattern in THEME_WORDS.items():
        if key.lower() in title.lower():
            return re.compile(pattern, re.I)
    return None


def evidence(pattern, text, width=64):
    """The first matching phrase with a little context, for the report."""
    m = pattern.search(text)
    if not m:
        return ''
    start = max(0, m.start() - width // 2)
    snippet = ' '.join(text[start:m.end() + width // 2].split())
    return ('...' if start else '') + snippet + '...'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('theme', nargs='?', help='only this theme (substring match)')
    ap.add_argument('--quiet', action='store_true', help='findings only')
    args = ap.parse_args()

    mentioned = load_helpers()
    data = json.load(open(PEOPLE, encoding='utf-8'))
    html = open(RESEARCH, encoding='utf-8').read()

    people = [(p['name'], s['heading'], re.sub(r'<[^>]+>', ' ', ' '.join(p['paragraphs'])))
              for s in data['sections'] if s['heading'] in CANDIDATE for p in s['people']]

    findings = 0
    for title, roster in themes(html):
        if args.theme and args.theme.lower() not in title.lower():
            continue
        pattern = words_for(title)
        if pattern is None:
            print(f"== {title}\n   no vocabulary defined - add one to THEME_WORDS\n")
            continue

        missing, thin, confirmed = [], [], []
        for name, section, bio in people:
            on = mentioned(name, roster)
            hit = pattern.search(bio)
            if on and hit:
                confirmed.append(name)
            elif on and not hit:
                # A short bio has no room to name a theme; that is not evidence.
                if len(bio.split()) >= THIN_MIN_WORDS:
                    thin.append((name, section))
            elif hit and not on:
                missing.append((name, section, evidence(pattern, bio)))

        print(f"== {title}   ({len(confirmed)} confirmed, {len(missing)} missing, {len(thin)} thin)")
        for name, section, ev in missing:
            print(f"   MISSING  {name} ({section})")
            print(f"            {ev}")
        for name, section in thin:
            print(f"   THIN     {name} ({section}) - bio says nothing on this theme")
        if confirmed and not args.quiet:
            print(f"   ok: {', '.join(confirmed)}")
        print()
        findings += len(missing) + len(thin)

    print(f"{findings} thing(s) to look at. Read the bio before acting on any of them.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
