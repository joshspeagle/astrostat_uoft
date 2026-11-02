#!/usr/bin/env python3
"""Cross-check Research theme rosters against what people's bios actually say.

    python3 scripts/theme_fit.py                # every theme
    python3 scripts/theme_fit.py Galaxies       # one theme (substring, case-insensitive)
    python3 scripts/theme_fit.py --quiet        # findings only, skip the confirmed list
    python3 scripts/theme_fit.py --all          # include previously reviewed omissions

For each theme this reports two directions:

  MISSING  someone whose People-page bio uses this theme's vocabulary but who is
           not on the theme (and is not in REVIEWED_OMISSIONS).
  THIN     someone listed on the theme whose bio contains none of its keywords
           and whose bio is at least THIN_MIN_WORDS words long (unless listed
           in REVIEWED_MEMBERSHIPS).

Keyword presence is a prompt for review rather than automatic membership.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
PEOPLE = os.path.join(ROOT, 'data', 'people.json')
RESEARCH = os.path.join(ROOT, 'data', 'research.json')

CANDIDATE = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students',
             'ART Associates', 'Collaborators'}

# Strip institutional boilerplate before matching theme keywords so department
# or institute names ("Department of Statistical Sciences", "Data Sciences
# Institute") do not trigger false positives on Inference.
INSTITUTIONAL_BOILERPLATE = re.compile(
    r'Department of Statistical Sciences|Data Sciences Institute|'
    r'Canadian Statistical Sciences Institute|Astrostatistics',
    re.I,
)

THEME_WORDS = {
    'Star Formation': r'star[- ]form\w*|molecular cloud\w*|protostar\w*|young star\w*|'
                      r'stellar nurser\w*|feedback|outflow\w*|turbulence',
    'Stellar Evolution': r'stellar (?:evolution|population\w*|astrophysics)|asteroseismolog\w*|'
                         r'white dwarf\w*|binar\w+ star\w*|M[- ]dwarf\w*|stellar flare\w*|'
                         r'variable star\w*|metal[- ]poor|surface gravit\w*|stellar dating|'
                         r'gravitational wave\w*|magnetic activit\w*|gyrochronolog\w*',
    'Milky Way': r'Milky Way|Galactic|the Galaxy\b|our galaxy\b|globular cluster\w*|'
                 r'stellar stream\w*|astrometr\w*|chemodynamic\w*|interstellar|dust|Gaia|'
                 r'Local Group',
    'Inference': r'Bayesian|hierarchical|inference|MCMC|Markov chain|Hidden Markov|HMM\w*|'
                 r'uncertaint\w*|conformal|model (?:selection|comparison)|sampling|'
                 r'nonparametric\w*|simulation-based inference|calibrat\w*|'
                 r'misspecification|\bstatistic\w*|'
                 r'point process\w*|outlier detection|dimensionality reduction',
    'Dark Matter': r'dark matter|dark energy|cosmolog\w*|halo\w*|large[- ]scale structure|'
                   r'cosmic microwave background|CMB|reionization|DESI|Euclid|lensing|'
                   r'ultra[- ]diffuse',
    'AI': r'machine learning|deep learning|neural network\w*|foundation model\w*|\bAI\b|'
          r'statistical learning|artificial intelligence|interpretab\w*|explainab\w*|'
          r'emulator\w*|generative model\w*|normalizing flow\w*|transformer\w*|'
          r'embedding\w*|representation learning|computational imaging',
    'Galaxies': r'galaxies|galaxy (?:formation|evolution|survey\w*|cluster\w*)|quench\w*|'
                r'quiescent|stellar mass|high[- ]redshift|photometric redshift|morpholog\w*|'
                r'supermassive black hole\w*|JWST|reionization|distant galax\w+',
    'Transients': r'transient\w*|supernova\w*|\bFRB\w*|fast radio burst\w*|magnetar\w*|'
                  r'time[- ]domain|CHIME|technosignature\w*|SETI|extraterrestrial|'
                  r'kilonova\w*|explosi\w*',
}

# Explicit rulings from roster reviews (Nov 2026): (person_id, theme_title) pairs
# where a keyword appears in the bio (e.g. a past project or tangential phrase)
# and the group lead confirmed the person should not be added to that theme.
REVIEWED_OMISSIONS = {
    ('phil-van-lane', 'Inference'),
    ('catherine-zucker', 'Inference'),
    ('chloe-cheng', 'Stellar Evolution'),
    ('leo-watson', 'AI for Scientists'),
    ('ian-zhang', 'The Milky Way'),
    ('aviad-levis', 'The Milky Way'),
    ('nolan-koblischke', 'The Milky Way'),
    ('aviad-levis', 'Galaxies'),
    ('ting-li', 'Galaxies'),
    ('ting-li', 'Star Formation'),
}

# Explicit rulings where a member is on a theme (e.g. faculty lead or domain
# co-investigator) even though their short summary bio omits the theme's keywords.
REVIEWED_MEMBERSHIPS = {
    ('duo-xu', 'Inference'),
    ('alex-laroche', 'Inference'),
    ('aviad-levis', 'Inference'),
    ('haowen-zhang', 'Inference'),
    ('kevin-mckinnon', 'Stellar Evolution'),
    ('connor-stone', 'Stellar Evolution'),
    ('joshua-speagle', 'Dark Matter & Cosmology'),
    ('anika-slizewski', 'Dark Matter & Cosmology'),
    ('ian-zhang', 'AI for Scientists'),
    ('tri-nguyen', 'The Milky Way'),
    ('joshua-speagle', 'Star Formation'),
}

THIN_MIN_WORDS = 55


def load_helpers():
    """Reuse audit_site.py's roster helpers."""
    src = open(os.path.join(HERE, 'audit_site.py'), encoding='utf-8').read().split('def main(')[0]
    ns = {}
    exec(src, ns)
    return ns['theme_ids']


def themes(research, theme_ids):
    """[(title, {id, ...})] in page order."""
    return [(t['title'], {i for _, ids in theme_ids(t) for i in ids})
            for t in research['themes']]


def words_for(title):
    for key, pattern in THEME_WORDS.items():
        if key.lower() in title.lower():
            return re.compile(pattern, re.I)
    return None


def evidence(pattern, text, width=64):
    """Return the first matching phrase with surrounding context."""
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
    ap.add_argument('--all', action='store_true',
                    help='include previously reviewed omissions and memberships')
    args = ap.parse_args()

    theme_ids = load_helpers()
    with open(PEOPLE, encoding='utf-8') as fh:
        data = json.load(fh)
    with open(RESEARCH, encoding='utf-8') as fh:
        research = json.load(fh)

    people = [(p['id'], p['name'], s['heading'],
               INSTITUTIONAL_BOILERPLATE.sub('', re.sub(r'<[^>]+>', ' ', ' '.join(p['paragraphs']))))
              for s in data['sections'] if s['heading'] in CANDIDATE for p in s['people']]

    findings = 0
    for title, roster in themes(research, theme_ids):
        if args.theme and args.theme.lower() not in title.lower():
            continue
        pattern = words_for(title)
        if pattern is None:
            print(f"== {title}\n   no vocabulary defined - add one to THEME_WORDS\n")
            continue

        missing, thin, confirmed = [], [], []
        for pid, name, section, bio in people:
            on = pid in roster
            hit = pattern.search(bio)
            if on and hit:
                confirmed.append(name)
            elif on and not hit:
                if (not args.all) and (pid, title) in REVIEWED_MEMBERSHIPS:
                    confirmed.append(name)
                elif len(bio.split()) >= THIN_MIN_WORDS:
                    thin.append((name, section))
            elif hit and not on:
                if (not args.all) and (pid, title) in REVIEWED_OMISSIONS:
                    continue
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

    print(f"{findings} unreviewed candidate(s). Pass --all to view previously reviewed rulings.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
