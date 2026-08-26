#!/usr/bin/env python3
"""Consistency checks for the ART website's content.

Run from the repo root:

    python3 scripts/audit_site.py                    # report findings, exit 0
    python3 scripts/audit_site.py --strict           # exit 1 if anything is flagged
    python3 scripts/audit_site.py --as-of 2026-09-15 # test the seasonal checks

Stdlib only. Everything here is mechanical: it checks facts the content can be
made to answer for itself. Whether a research blurb or a bio still *reads*
correctly is not something this can know - that stays a human pass.
"""

import argparse
import datetime
import json
import os
import re
import sys

PEOPLE = 'data/people.json'
RESEARCH = 'ejs/pages/research/body.html'
HOME = 'ejs/pages/home/body.html'
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
    """Is this specific person named in `text`?

    Deliberately does not assume one given name and one surname. Dual
    surnames (common in Spanish- and Portuguese-speaking naming, among
    others) and dual given names both break that assumption, in opposite
    directions: matching on the last token alone conflated "Antonio Herrera
    Martin" with a different "Peter Martin", while requiring the full name
    missed "Rodrigo Barradas Herrera" wherever a shorter form was used.

    So: accept an exact full-name match, or any two adjacent tokens of the
    name appearing adjacently in the text, or a "<given> <later-token>" pair
    whose given name is compatible with one of the person's earlier tokens.
    """
    toks = name_tokens(name)
    if not toks:
        return False
    if re.search(r'\b' + re.escape(' '.join(toks)) + r'\b', text):
        return True
    # any adjacent pair from the name, e.g. "Barradas Herrera"
    for i in range(len(toks) - 1):
        pair = toks[i] + ' ' + toks[i + 1]
        if re.search(r'\b' + re.escape(pair) + r'\b', text):
            return True
    # a shortened given name in front of any later token of the name
    for i in range(1, len(toks)):
        anchor = toks[i]
        if len(anchor.rstrip('.')) < 2:
            continue
        for preceding in re.findall(r"([A-Za-z'\u00C0-\u017F-]+)\.?\s+" + re.escape(anchor) + r'\b', text):
            if any(_compatible(preceding, earlier) for earlier in toks[:i]):
                return True
    return False


def caption_names(home):
    """Names listed in the home page's group-photo caption."""
    m = re.search(r'From left to right:(.*?)</figcaption>', home, re.S)
    if not m:
        return []
    blob = re.sub(r'<[^>]+>', ' ', m.group(1))
    blob = re.sub(r'\(with (.*?) featured in the background\)', r', \1', blob)
    blob = blob.replace(' and ', ', ')
    out = []
    for chunk in blob.split(','):
        chunk = re.sub(r'\(.*?\)', '', chunk).strip(' .')
        if chunk and chunk[0].isupper():
            out.append(re.sub(r'\s+', ' ', chunk))
    return out


def research_linked_names(research):
    """Names used as link text inside the per-theme 'involved' lists."""
    names = set()
    for m in re.finditer(r'<strong>(?:ART members involved|ART associates involved|'
                         r'Collaborators include):</strong>(.*?)</p>', research, re.S):
        for a in re.finditer(r'<a [^>]*>(.*?)</a>', m.group(1), re.S):
            n = re.sub(r'\s+', ' ', a.group(1)).strip()
            if n and n[0].isupper() and ' ' in n:
                names.add(n)
    return names


# Cues that introduce someone who advises or collaborates with an ART member.
ADVISOR_CUE = re.compile(
    r'(co-supervis\w*|co-advis\w*|works closely with|collaborates closely with|'
    r'supervised by|advised by|working with)', re.I)

# A degree clause names a PAST supervisor, not a current collaborator.
DEGREE_CLAUSE = re.compile(r'(Ph\.?D|M\.?Sc|B\.?Sc|degree|doctorate)', re.I)

# Advisers deliberately left out of Collaborators. The section is for people the
# group works with on an ongoing basis; a one-off co-supervision does not qualify.
ADVISER_NOT_COLLABORATOR = {
    'Nolan Koblischke': 'co-supervises one SURP undergrad only (decided Aug 2026)',
}

NOT_A_PERSON = ('Department', 'Institute', 'University', 'Fellow', 'Program', 'Survey',
                'Telescope', 'Sciences', 'College', 'Award', 'Observatory', 'Collaboration',
                'Centre', 'Center', 'School', 'Array', 'Experiment')


def advisors_named(data):
    """People named as advising or collaborating with a CURRENT member.

    Skips Recent Alumni, whose entries describe where someone went and who they
    trained under, and skips degree clauses like "received his Ph.D. under the
    supervision of X", which name a past supervisor rather than a collaborator.
    """
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
    """Why a file in static/ might be unreferenced. Several reasons are benign."""
    stem = os.path.splitext(fname)[0].lower()
    if stem in used_stems:
        return 'spare copy of a file already in use'
    tokens = {t for t in re.split(r'[_\-.]+', stem) if len(t) > 2}
    for name, name_tokens in current_tokens.items():
        if len(tokens & name_tokens) >= 2 or (tokens & name_tokens and len(tokens) <= 2):
            return f'older headshot of {name}, who is still listed'
    if 'logo' in stem:
        return 'inlined as raw <svg> in main.ejs, not referenced by src'
    if re.search(r'20\d\d', stem) and re.search(r'group|statstro|art_|mrc', stem):
        return 'superseded dated photo (kept as history)'
    return None  # unexplained - possibly a departed member


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 if any check reports a finding')
    ap.add_argument('--as-of', metavar='YYYY-MM-DD',
                    help='pretend today is this date (for testing seasonal checks)')
    args = ap.parse_args()

    data = json.load(open(PEOPLE, encoding='utf-8'))
    research_raw = open(RESEARCH, encoding='utf-8').read()
    research_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', research_raw))
    home_raw = open(HOME, encoding='utf-8').read()
    home = re.sub(r'\s+', ' ', home_raw)
    shell = open(SHELL, encoding='utf-8').read()

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

            seen = mentioned(name, research_text)
            if section['heading'] in CURRENT and not seen:
                missing.append(f"{name} ({section['heading']})")
            if section['heading'] == 'Recent Alumni' and seen:
                lingering.append(name)

            if not person.get('image'):
                no_photo.append(f"{name} ({section['heading']})")

    known_surnames = {surname(n) for n in everyone}

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

    # Collaborators should cover everyone who co-advises a current member.
    collab = {p['name'] for s_ in data['sections']
              if s_['heading'] == 'Collaborators' for p in s_['people']}
    known = {surname(n) for n in list(collab) + list(everyone)}
    gaps = sorted(f"{nm}  <- advises {', '.join(sorted(who))}"
                  for nm, who in advisors_named(data).items()
                  if surname(nm) not in known
                  and nm not in ADVISER_NOT_COLLABORATOR)
    report('5c. Advisers of current members missing from Collaborators', gaps,
           'the section is defined as co-advisers of members plus people the group collaborates with')

    # The file writes & literally inside prose; &amp; is an inconsistency.
    amps = sorted(p['name'] for s_ in data['sections'] for p in s_['people']
                  if any('&amp;' in t for t in p['paragraphs']))
    report('5d. Entries using &amp; instead of a bare &', amps,
           'paragraphs are emitted verbatim, and the rest of the file writes & directly')

    unknown = sorted(n for n in research_linked_names(research_raw)
                     if surname(n) not in known_surnames)
    report('5. Names linked on Research matching nobody on People', unknown,
           'typo, or someone dropped from People but left on Research')

    # images
    refs = {}
    for path, text in {HOME: home_raw, RESEARCH: research_raw, SHELL: shell}.items():
        for m in re.finditer(r'src="/static/([^"]+)"', text):
            refs.setdefault(m.group(1), set()).add(path)
    for section in data['sections']:
        for person in section['people']:
            if person.get('image'):
                refs.setdefault(person['image'], set()).add(PEOPLE)
    broken = [f"{k}  <- {', '.join(sorted(v))}" for k, v in sorted(refs.items())
              if not os.path.exists(os.path.join('static', k))]
    report('6. Referenced images missing from static/', broken)
    report('7. Entries with no photo', no_photo)

    # group-photo caption vs roster
    cap = caption_names(home)
    cap_unknown, cap_alumni = [], []
    for n in cap:
        if surname(n) not in known_surnames:
            cap_unknown.append(n)
        else:
            match = next((k for k in everyone if surname(k) == surname(n)), None)
            if match and everyone[match] == 'Recent Alumni':
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

    # photo recency
    print("[9. Home-page photo recency]")
    figures = set(re.findall(r'<figure>.*?src="/static/([^"]+)".*?</figure>', home, re.S))
    dated = [(fn, int(re.search(r'(20\d\d)', fn).group(1)))
             for fn in figures if re.search(r'(20\d\d)', fn)]
    stalest = [f for f in dated if ay - f[1] >= 1]
    for fn, yr in sorted(stalest, key=lambda x: x[1]):
        print(f"      {fn} ({yr}) -- {ay - yr} academic year(s) old; is there a newer one?")
    if not stalest:
        print("      none look out of date")
    findings += len(stalest)
    print()

    # footer date
    print("[10. Home page 'last updated' line]")
    m = re.search(r'It was last updated ([A-Z][a-z]+ \d{1,2}, \d{4})', home)
    if not m:
        print("      could not find the line -- has the wording changed?")
        findings += 1
    else:
        try:
            stamped = datetime.datetime.strptime(m.group(1), '%B %d, %Y').date()
            age = (today - stamped).days
            print(f"      says {m.group(1)} ({age} days ago)")
            if age > 120:
                print("      -> bump it as part of this update")
                findings += 1
        except ValueError:
            print(f"      unparseable date: {m.group(1)}")
            findings += 1
    print()

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
