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
RESEARCH = 'data/research.json'
HOME = 'ejs/pages/home/body.html'
SHELL = 'ejs/main.ejs'
RENDER_RESEARCH = 'build/render-research.js'
STYLE = 'scss/index.scss'

# Sections whose members are expected to appear on at least one Research theme.
CURRENT = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students', 'ART Associates'}

YEAR_LABEL = re.compile(r'\b(\d)(?:st|nd|rd|th)-year\b')
ORDINALS = {1: '1st', 2: '2nd', 3: '3rd'}


def read_optional(path):
    """File contents, or None if it is not there. Used by checks that reach
    outside the content files, so a missing file skips the check rather than
    crashing the audit."""
    try:
        with open(path, encoding='utf-8') as fh:
            return fh.read()
    except OSError:
        return None


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

    Since the Research page became data/research.json, membership is an id
    lookup and this is only needed where names still appear as free text: the
    home page's group-photo caption (below) and scripts/theme_fit.py.

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
    # A parenthetical inside the *text* ("Isabelle (Liyuan) Huang") splits an
    # otherwise adjacent pair, so match against a paren-stripped copy as well.
    text = text + '\n' + re.sub(r'\s*\([^)]*\)', '', text)
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


def match_person(name, everyone):
    """Which roster entry a free-text name refers to, if any."""
    for known in everyone:
        if mentioned(known, name) or mentioned(name, known):
            return known
    return None


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


ROSTER_KEYS = (('members', 'ART members involved'),
               ('associates', 'ART associates involved'),
               ('collaborators', 'Collaborators include'))


def entry_id(entry):
    """A roster entry is an id, or {'id': ..., 'note': 'McMaster'}."""
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
    """[(theme, label, id)] for roster entries that name nobody on the People page.

    The build fails on these too (see build/render-research.js); the check is
    here so a mid-edit data file can be looked at without running webpack.
    """
    labels = dict(ROSTER_KEYS)
    out = []
    for theme in research['themes']:
        for key, ids in theme_ids(theme):
            for i in ids:
                if i not in known:
                    out.append((theme['title'], labels[key], i))
    return out


def duplicate_ids(research, people):
    """Ids that appear where exactly one was meant.

    Three ways this goes wrong: two People entries claiming one id (which would
    make an anchor ambiguous), two themes claiming one theme id, and one person
    listed twice in the same roster row.
    """
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
    """[(title, total roster size)] in page order - the key sort_themes.py uses."""
    return [(t['title'], sum(len(ids) for _, ids in theme_ids(t)))
            for t in research['themes']]


def out_of_size_order(research):
    """Themes that sit above a larger one. Ties are fine; sort_themes.py keeps them."""
    totals = theme_totals(research)
    out = []
    for i, (title, total) in enumerate(totals):
        bigger = [t for t, n in totals[i + 1:] if n > total]
        if bigger:
            out.append(f'{title} ({total}) sits above {bigger[0]}')
    return out


def flip_not_wired(renderer, style):
    """Is the alternating side of the theme images still decided by position?

    build/render-research.js marks every second theme `media-flip`, saying which
    side its image belongs on. If scss/index.scss does not key off that class,
    the flip still comes from a `:nth-child(odd)` rule that counts *all* of the
    section's children - the intro paragraphs included. It happens to alternate
    correctly today; adding or removing a single intro paragraph in
    data/research.json swaps every theme to the other side, and nothing about
    editing prose suggests it could do that.

    Both arguments are file contents. The check is skipped if either file is
    missing, and goes quiet as soon as the stylesheet mentions `media-flip`.
    """
    if renderer is None or style is None:
        return []
    if 'media-flip' not in renderer:
        return []                      # the renderer no longer states the flip
    if 'media-flip' in style:
        return []                      # wired up
    where = ''
    for i, line in enumerate(style.splitlines(), 1):
        if 'nth-child' in line:
            where = f' ({STYLE}:{i})'
            break
    return [f'{RENDER_RESEARCH} emits `media-flip` but {STYLE} never uses it'
            f'{where}; the image side still depends on how many intro '
            f'paragraphs data/research.json has']


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
    'Chris Maddison': "co-supervises an associate's Ph.D. via the DSI fellowship, "
                      'not otherwise involved with the group (decided Sep 2026)',
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
    research = json.load(open(RESEARCH, encoding='utf-8'))
    on_theme = research_ids(research)
    home_raw = open(HOME, encoding='utf-8').read()
    home = re.sub(r'\s+', ' ', home_raw)
    shell = open(SHELL, encoding='utf-8').read()
    renderer_src = read_optional(RENDER_RESEARCH)
    style_src = read_optional(STYLE)

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

            # Membership is now an id in data/research.json, not a name spelled
            # out in prose, so this is an exact lookup rather than a text search.
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
        for m in re.finditer(r'src="/static/([^"]+)"', text):
            refs.setdefault(m.group(1), set()).add(path)
    for section in data['sections']:
        for person in section['people']:
            if person.get('image'):
                refs.setdefault(person['image'], set()).add(PEOPLE)
    broken = [f"{k}  <- {', '.join(sorted(v))}" for k, v in sorted(refs.items())
              if not os.path.exists(os.path.join('static', k))]
    report('6. Referenced images missing from static/', broken)
    report('7. Entries with no photo',
           no_photo + [f"{t['title']} (Research theme)" for t in research['themes']
                       if not t.get('image')])

    # group-photo caption vs roster
    cap = caption_names(home)
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

    # footer date - built from the last commit date (see webpack.config.js),
    # so the only thing left to check is that the placeholder is still there.
    print("[10. Home page 'last updated' line]")
    if '{{LAST_UPDATED}}' in home:
        print("      generated at build time from the last commit touching "
              "data/ or ejs/pages/")
        print("      (on CI's shallow checkout that degrades to the build's own "
              "commit -- see webpack.config.js)")
    else:
        print("      the {{LAST_UPDATED}} placeholder is gone from "
              f"{HOME} -- has someone typed a literal date back in?")
        findings += 1
    print()

    # --- Research data-file consistency ---
    # Three checks that used to live here - names left unlinked, one person
    # written two ways, roster blocks out of order - are gone: with ids and a
    # renderer none of those states can be expressed any more.

    report('11. Duplicate or missing ids', duplicate_ids(research, data),
           'an id is a page anchor (/people.html#<id>), so it has to be unique')

    report('12. Research themes out of size order', out_of_size_order(research),
           'run `python3 scripts/sort_themes.py --apply` to reorder them')

    report('13. Theme image sides decided by sibling position',
           flip_not_wired(renderer_src, style_src),
           'replace the `&:nth-child(odd)` rule under `.media-object` with '
           '`&.media-flip`')

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
