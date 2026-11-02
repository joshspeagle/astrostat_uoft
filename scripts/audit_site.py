#!/usr/bin/env python3
"""Consistency checks for the ART website's content and assets.

Run from the repo root:

    python3 scripts/audit_site.py                    # report findings, exit 0
    python3 scripts/audit_site.py --strict           # exit 1 if anything is flagged
    python3 scripts/audit_site.py --as-of 2026-09-15 # test the seasonal checks

Uses only the Python standard library. Checks cross-file invariants across
data/people.json, data/research.json, data/home.json, ejs/main.ejs, and static/.
"""

import argparse
import datetime
import json
import os
import re
import sys

PEOPLE = 'data/people.json'
RESEARCH = 'data/research.json'
HOME = 'data/home.json'
SHELL = 'ejs/main.ejs'

# Sections whose members are expected to appear on at least one Research theme.
CURRENT = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students', 'ART Associates'}

YEAR_LABEL = re.compile(r'\b(\d)(?:st|nd|rd|th)-year\b')
ORDINALS = {1: '1st', 2: '2nd', 3: '3rd'}


def ordinal(n):
    return ORDINALS.get(n, f'{n}th')


def academic_year(today):
    """Calendar year the current academic year started in (rolls over in September)."""
    return today.year if today.month >= 9 else today.year - 1


def surname(name):
    return re.sub(r'\s*\([^)]*\)', '', name).strip().split()[-1]


def name_tokens(name):
    """Name split into word tokens, ignoring any parenthetical suffix."""
    bare = re.sub(r'\s*\([^)]*\)', '', name).strip()
    return [t for t in re.split(r'\s+', bare) if t and t != '-']


def _compatible(a, b):
    """Same given name allowing for a short form (Gwen/Gwendolyn, Josh/Joshua)."""
    a, b = a.rstrip('.'), b.rstrip('.')
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a)


def mentioned(name, text):
    """Return True if `name` is referenced in `text`.

    Handles dual surnames and parenthetical nicknames by matching:
    - the full name,
    - any two adjacent tokens of the name appearing adjacently in `text`, or
    - a `<given> <later-token>` pair whose given name is compatible with one
      of the person's earlier tokens.
    """
    toks = name_tokens(name)
    if not toks:
        return False
    text = text + '\n' + re.sub(r'\s*\([^)]*\)', '', text)
    if re.search(r'\b' + re.escape(' '.join(toks)) + r'\b', text):
        return True
    for i in range(len(toks) - 1):
        pair = toks[i] + ' ' + toks[i + 1]
        if re.search(r'\b' + re.escape(pair) + r'\b', text):
            return True
    for i in range(1, len(toks)):
        anchor = toks[i]
        if len(anchor.rstrip('.')) < 2:
            continue
        for preceding in re.findall(r"([A-Za-z'\u00C0-\u017F-]+)\.?\s+" + re.escape(anchor) + r'\b', text):
            if any(_compatible(preceding, earlier) for earlier in toks[:i]):
                return True
    return False


def match_person(name, everyone):
    """Return the roster entry name that a free-text name refers to, if any."""
    for known in everyone:
        if mentioned(known, name) or mentioned(name, known):
            return known
    return None


def caption_names(home):
    """Names listed in the Home page's group-photo caption (accepts dict, JSON, or HTML)."""
    caption_str = ''
    if isinstance(home, dict):
        caption_str = home.get('about', {}).get('figure', {}).get('caption', '')
    elif isinstance(home, str):
        stripped = home.strip()
        if stripped.startswith('{'):
            try:
                parsed = json.loads(stripped)
                caption_str = parsed.get('about', {}).get('figure', {}).get('caption', '')
            except ValueError:
                caption_str = home
        else:
            caption_str = home

    m = re.search(r'[Ll]eft to right:(.*?)(?:</figcaption>|$)', caption_str, re.S)
    if not m:
        return []
    blob = re.sub(r'<[^>]+>', ' ', m.group(1))
    blob = re.sub(r'\(?with (.*?)(?: featured)? in the background\)?', r', \1', blob)
    blob = blob.replace(' and ', ', ')
    out = []
    for chunk in blob.split(','):
        chunk = re.sub(r'\(.*?\)', '', chunk).strip(' .')
        if chunk and chunk[0].isupper():
            out.append(re.sub(r'\s+', ' ', chunk))
    return out


ROSTER_KEYS = (('members', 'ART members involved'),
               ('associates', 'ART associates involved'),
               ('collaborators', 'Collaborators include'))


def entry_id(entry):
    """A roster entry is an id string, or {'id': ..., 'note': '...'}."""
    return entry['id'] if isinstance(entry, dict) else entry


def theme_ids(theme):
    """[(key, [id, ...])] for one theme, in members/associates/collaborators order."""
    return [(key, [entry_id(e) for e in theme.get(key) or []]) for key, _ in ROSTER_KEYS]


def research_ids(research):
    """id -> {theme title, ...} for everyone named anywhere on Research."""
    out = {}
    for theme in research['themes']:
        for _, ids in theme_ids(theme):
            for i in ids:
                out.setdefault(i, set()).add(theme['title'])
    return out


def unknown_ids(research, known):
    """[(theme, label, id)] for roster entries that do not match any People id."""
    labels = dict(ROSTER_KEYS)
    out = []
    for theme in research['themes']:
        for key, ids in theme_ids(theme):
            for i in ids:
                if i not in known:
                    out.append((theme['title'], labels[key], i))
    return out


def duplicate_ids(research, people):
    """Ids that appear more than once or are missing."""
    out = []
    seen = set()
    for section in people['sections']:
        for person in section['people']:
            pid = person.get('id')
            if not pid:
                out.append(f"{person['name']} (People) has no id")
            elif pid in seen:
                out.append(f'{pid} (People) is used by more than one person')
            else:
                seen.add(pid)

    seen = set()
    labels = dict(ROSTER_KEYS)
    for theme in research['themes']:
        tid = theme.get('id')
        if not tid:
            out.append(f"{theme['title']} (Research) has no id")
        elif tid in seen:
            out.append(f'{tid} (Research) is used by more than one theme')
        else:
            seen.add(tid)
        for key, ids in theme_ids(theme):
            for i in sorted({i for i in ids if ids.count(i) > 1}):
                out.append(f"{i} listed twice under {labels[key]} on {theme['title']}")
    return out


def theme_totals(research):
    """[(title, total roster size)] in page order (used by sort_themes.py)."""
    return [(t['title'], sum(len(ids) for _, ids in theme_ids(t)))
            for t in research['themes']]


def out_of_size_order(research):
    """Themes that sit above a strictly larger theme."""
    totals = theme_totals(research)
    out = []
    for i, (title, total) in enumerate(totals):
        bigger = [t for t, n in totals[i + 1:] if n > total]
        if bigger:
            out.append(f'{title} ({total}) sits above {bigger[0]}')
    return out


# Cues that introduce someone who advises or collaborates with an ART member.
ADVISOR_CUE = re.compile(
    r'(co-supervis\w*|co-advis\w*|works closely with|collaborates closely with|'
    r'supervised by|advised by|working with)', re.I)

# A degree clause names a past supervisor, not a current collaborator.
DEGREE_CLAUSE = re.compile(r'(Ph\.?D|M\.?Sc|B\.?Sc|degree|doctorate)', re.I)

# Advisers deliberately omitted from Collaborators (one-off co-supervision).
ADVISER_NOT_COLLABORATOR = {
    'Nolan Koblischke': 'co-supervises one SURP undergrad only (decided Aug 2026)',
    'Chris Maddison': "co-supervises an associate's Ph.D. via the DSI fellowship, "
                      'not otherwise involved with the group (decided Sep 2026)',
}

NOT_A_PERSON = ('Department', 'Institute', 'University', 'Fellow', 'Program', 'Survey',
                'Telescope', 'Sciences', 'College', 'Award', 'Observatory', 'Collaboration',
                'Centre', 'Center', 'School', 'Array', 'Experiment')


def advisors_named(data):
    """People named as advising or collaborating with a current member."""
    found = {}
    for section in data['sections']:
        if section['heading'] in ('Recent Alumni', 'Collaborators'):
            continue
        for person in section['people']:
            for para in person['paragraphs']:
                for m in ADVISOR_CUE.finditer(para):
                    before = re.sub(r'<[^>]+>', '', para[max(0, m.start() - 70):m.start()])
                    if DEGREE_CLAUSE.search(before):
                        continue
                    for a in re.finditer(r'<a [^>]*>([^<]+)</a>',
                                         para[m.start():m.start() + 400]):
                        nm = re.sub(r'\s+', ' ', a.group(1)).strip()
                        if (nm and nm[0].isupper() and ' ' in nm and len(nm.split()) <= 4
                                and not any(w in nm for w in NOT_A_PERSON)):
                            found.setdefault(nm, set()).add(person['name'])
    return found


def classify_orphan(fname, used_stems, current_tokens):
    """Classify why a file in static/ might be unreferenced."""
    stem = os.path.splitext(fname)[0].lower()
    if stem in used_stems:
        return 'spare copy of a file already in use'
    tokens = {t for t in re.split(r'[_\-.]+', stem) if len(t) > 2}
    for name, name_toks in current_tokens.items():
        if len(tokens & name_toks) >= 2 or (tokens & name_toks and len(tokens) <= 2):
            return f'older headshot of {name}, who is still listed'
    if 'logo' in stem:
        return 'inlined as raw <svg> in main.ejs, not referenced by src'
    if re.search(r'20\d\d', stem) and re.search(r'group|statstro|art_|mrc', stem):
        return 'superseded dated photo (kept as history)'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 if any check reports a finding')
    ap.add_argument('--as-of', metavar='YYYY-MM-DD',
                    help='pretend today is this date (for testing seasonal checks)')
    args = ap.parse_args()

    with open(PEOPLE, encoding='utf-8') as fh:
        data = json.load(fh)
    with open(RESEARCH, encoding='utf-8') as fh:
        research = json.load(fh)
    with open(HOME, encoding='utf-8') as fh:
        home_raw = fh.read()
    home_data = json.loads(home_raw)
    with open(SHELL, encoding='utf-8') as fh:
        shell = fh.read()

    on_theme = research_ids(research)
    today = (datetime.date.fromisoformat(args.as_of) if args.as_of
             else datetime.date.today())
    ay = academic_year(today)

    everyone = {}
    stale, no_cohort, missing, lingering, no_photo = [], [], [], [], []

    for section in data['sections']:
        for person in section['people']:
            name = person['name']
            everyone[name] = section['heading']
            paras = person['paragraphs']

            label = next((YEAR_LABEL.search(p) for p in paras if YEAR_LABEL.search(p)), None)
            if label:
                stated = int(label.group(1))
                cohort = person.get('cohort')
                if cohort is None:
                    no_cohort.append(name)
                else:
                    expected = ay - cohort + 1
                    if expected != stated:
                        stale.append((name, ordinal(stated), ordinal(expected)))

            themes = on_theme.get(person.get('id'), set())
            if section['heading'] in CURRENT and not themes:
                missing.append(f"{name} ({section['heading']})")
            if section['heading'] == 'Recent Alumni' and themes:
                lingering.append(f"{name}  <- {', '.join(sorted(themes))}")

            if not person.get('image'):
                no_photo.append(f"{name} ({section['heading']})")

    print(f"ART site audit - {today.isoformat()} "
          f"(academic year {ay}-{str(ay + 1)[2:]})\n")
    findings = 0

    def report(title, items, note=None):
        nonlocal findings
        print(f"[{title}] ({len(items)})")
        for i in items:
            print(f"      {i}")
        if not items:
            print("      none")
        if note and items:
            print(f"      -> {note}")
        findings += len(items)
        print()

    report('1. Stale year-of-study labels',
           [f"{n}: says {w}-year, should be {r}-year" for n, w, r in stale])
    report('2. Year label but no `cohort`',
           [f"{n}  -- add \"cohort\": <start year>" for n in no_cohort])
    report('3. Current members on no Research theme', missing)
    report('4. Alumni still listed on Research', lingering,
           'remove them from the theme lists')

    ug_alumni = [n for n, sec in everyone.items()
                 if sec == 'Recent Alumni'
                 and re.search(r"\((?:B\.?A|B\.?Sc|BSc|BA)\b", n)]
    report('5b. Undergraduate-level entries in Recent Alumni', ug_alumni,
           'undergrads are listed while current only; they do not get alumni entries')

    collab = {p['name'] for s_ in data['sections']
              if s_['heading'] == 'Collaborators' for p in s_['people']}
    known = {surname(n) for n in list(collab) + list(everyone)}
    gaps = sorted(f"{nm}  <- advises {', '.join(sorted(who))}"
                  for nm, who in advisors_named(data).items()
                  if surname(nm) not in known
                  and nm not in ADVISER_NOT_COLLABORATOR)
    report('5c. Advisers of current members missing from Collaborators', gaps,
           'the section covers co-advisers of members plus ongoing group collaborators')

    amps = sorted(p['name'] for s_ in data['sections'] for p in s_['people']
                  if any('&amp;' in t for t in p['paragraphs']))
    report('5d. Entries using &amp; instead of a bare &', amps,
           'paragraphs in data/people.json write & directly')

    people_ids = {p['id'] for s_ in data['sections'] for p in s_['people'] if p.get('id')}
    report('5. Research roster ids matching nobody on People',
           [f'{i}  <- {label} on {title}'
            for title, label, i in unknown_ids(research, people_ids)],
           'typo, or someone dropped from People but left on Research; '
           'this also fails the build')

    # images
    refs = {}
    for theme in research['themes']:
        if theme.get('image'):
            refs.setdefault(theme['image'], set()).add(RESEARCH)
    for path, text in {HOME: home_raw, SHELL: shell}.items():
        for m in re.finditer(r'/static/([^"\s,]+)', text):
            refs.setdefault(m.group(1), set()).add(path)
    for section in data['sections']:
        for person in section['people']:
            if person.get('image'):
                refs.setdefault(person['image'], set()).add(PEOPLE)
    broken = [f"{k}  <- {', '.join(sorted(v))}" for k, v in sorted(refs.items())
              if not os.path.exists(os.path.join('static', k))]
    report('6. Referenced images missing from static/', broken)

    # Entries with no photo are informational now that build/render-people.js
    # renders an intentional monogram + sparkle tile for null images.
    missing_theme_images = [f"{t['title']} (Research theme)" for t in research['themes']
                            if not t.get('image')]
    report('7. Research themes with no image', missing_theme_images)
    print(f"[7b. People entries using monogram fallback tile] ({len(no_photo)}) - informational")
    for item in no_photo:
        print(f"      {item}")
    if not no_photo:
        print("      none")
    print()

    # group-photo caption vs roster
    cap = caption_names(home_data)
    cap_unknown, cap_alumni = [], []
    for n in cap:
        match = match_person(n, everyone)
        if not match:
            cap_unknown.append(n)
        elif everyone[match] == 'Recent Alumni':
            cap_alumni.append(f"{n} (now in Recent Alumni)")
    print(f"[ii. Group-photo caption] ({len(cap)} names parsed) - informational")
    if not cap:
        print("      could not parse the caption -- has the wording changed?")
        findings += 1
    else:
        print("      A caption describes the photo, not the current roster, so names")
        print("      that have since left are expected. Only rewrite it when the photo")
        print("      itself changes.")
        for n in cap_unknown:
            print(f"      {n}  -- no longer anywhere on the People page")
        for n in cap_alumni:
            print(f"      {n}")
        if not cap_unknown and not cap_alumni:
            print("      all names match current members")
    print()

    # photo recency (informational)
    print("[iii. Home-page photo recency] - informational")
    figures = set()
    for sec_key in ('about', 'workshop', 'events'):
        fig = home_data.get(sec_key, {}).get('figure', {})
        src = fig.get('src', '')
        if src.startswith('/static/'):
            figures.add(src[len('/static/'):])
    dated = [(fn, int(re.search(r'(20\d\d)', fn).group(1)))
             for fn in figures if re.search(r'(20\d\d)', fn)]
    stalest = [f for f in dated if ay - f[1] >= 1]
    for fn, yr in sorted(stalest, key=lambda x: x[1]):
        print(f"      {fn} ({yr}) -- {ay - yr} academic year(s) old; check if a newer group photo is available")
    if not stalest:
        print("      none look out of date")
    print()

    print("[10. Site note 'last updated' line]")
    if '{{LAST_UPDATED}}' in shell:
        print("      generated at build time from the last commit touching "
              "data/ or ejs/")
    else:
        print("      the {{LAST_UPDATED}} placeholder is gone from "
              f"{SHELL} -- has someone typed a literal date back in?")
        findings += 1
    print()

    report('11. Duplicate or missing ids', duplicate_ids(research, data),
           'an id is a page anchor (/people.html#<id>), so it has to be unique')

    report('12. Research themes out of size order', out_of_size_order(research),
           'run `python3 scripts/sort_themes.py --apply` to reorder them')

    # orphans (informational)
    used_stems = {os.path.splitext(r)[0].lower() for r in refs}
    orphans = sorted(set(os.listdir('static')) - set(refs))
    current_tokens = {
        n: {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'-]+", n) if len(t) > 2}
        for n in everyone
    }
    unexplained = [(f, classify_orphan(f, used_stems, current_tokens)) for f in orphans]
    odd = [f for f, why in unexplained if why is None]
    print(f"[i. Unreferenced files in static/] ({len(orphans)}) - informational, not a finding")
    for f, why in unexplained:
        print(f"      {f:<32} {why or 'unexplained - possibly a departed member'}")
    if odd:
        print(f"\n      {len(odd)} unexplained. A headshot with no entry can mean someone was")
        print("      removed outright rather than moved to Recent Alumni - worth a look.")
    print()

    print(f"{findings} finding(s).")
    return 1 if (args.strict and findings) else 0


if __name__ == '__main__':
    sys.exit(main())
