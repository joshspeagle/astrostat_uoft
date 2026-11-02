#!/usr/bin/env python3
"""Autonomous preflight discovery and update proposal generator for the ART website.

Run from the repo root:

    python3 scripts/propose_updates.py                  # offline checks + cross-repo sync
    python3 scripts/propose_updates.py --online         # also scrape Gwen's page & check URLs
    python3 scripts/propose_updates.py --as-of 2027-09-15
    python3 scripts/propose_updates.py --apply-years    # update stale Nth-year labels in place

Uses only the Python standard library. Produces a structured Markdown Update
Proposal Digest covering:
  1. Cross-repo roster sync against ../joshspeagle.github.io/assets/data/content.json
  2. Seasonal & date-triggered rollovers (grad student year-of-study, leave notes,
     seasonal wording, Home photo recency)
  3. Internal consistency & theme-fit checks (audit_site.py + theme_fit.py)
  4. Optional live web checks (--online: Gwen Eadie's group page + external link health)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PEOPLE_PATH = os.path.join(ROOT, 'data', 'people.json')
RESEARCH_PATH = os.path.join(ROOT, 'data', 'research.json')
HOME_PATH = os.path.join(ROOT, 'data', 'home.json')
SPEAGLE_CONTENT_PATH = os.path.abspath(
    os.path.join(ROOT, '..', 'joshspeagle.github.io', 'assets', 'data', 'content.json')
)

YEAR_LABEL = re.compile(r'\b(\d)(?:st|nd|rd|th)-year\b')
ORDINALS = {1: '1st', 2: '2nd', 3: '3rd'}
SEASONAL_CUES = re.compile(
    r'\b(this summer|this fall|this autumn|this spring|this winter|'
    r'starting in|incoming|will join)\b',
    re.I,
)
MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
}


def ordinal(n):
    return ORDINALS.get(n, f'{n}th')


def academic_year(today):
    return today.year if today.month >= 9 else today.year - 1


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html or '')).strip()


def load_audit_helpers():
    src = open(os.path.join(HERE, 'audit_site.py'), encoding='utf-8').read().split('def main(')[0]
    ns = {}
    exec(src, ns)
    return ns


def check_seasonal_and_years(people_data, home_data, today, apply_years=False):
    ay = academic_year(today)
    year_bumps = []
    leave_notes = []
    seasonal_phrases = []

    for section in people_data['sections']:
        for person in section['people']:
            name = person['name']
            for idx, para in enumerate(person['paragraphs']):
                m = YEAR_LABEL.search(para)
                if m and person.get('cohort') is not None:
                    stated = int(m.group(1))
                    expected = ay - person['cohort'] + 1
                    if stated != expected:
                        year_bumps.append((name, ordinal(stated), ordinal(expected)))
                        if apply_years and expected >= 1:
                            person['paragraphs'][idx] = YEAR_LABEL.sub(
                                f'{ordinal(expected)}-year', para, count=1
                            )

                if 'on leave' in para.lower():
                    clean = strip_tags(para)
                    expired = False
                    m_until = re.search(
                        r'until\s+([A-Za-z]+)\s+(20\d\d)', clean, re.I
                    )
                    if m_until:
                        m_num = MONTHS.get(m_until.group(1).lower(), 12)
                        yr = int(m_until.group(2))
                        if (today.year, today.month) >= (yr, m_num):
                            expired = True
                    leave_notes.append((name, clean, expired))

                m_seas = SEASONAL_CUES.search(strip_tags(para))
                if m_seas:
                    seasonal_phrases.append((name, m_seas.group(0), strip_tags(para)))

    if apply_years and year_bumps:
        with open(PEOPLE_PATH, 'w', encoding='utf-8') as fh:
            json.dump(people_data, fh, indent=2, ensure_ascii=False)
            fh.write('\n')

    photo_notes = []
    for key in ('about', 'workshop', 'events'):
        fig = home_data.get(key, {}).get('figure', {})
        src = fig.get('src', '')
        m_yr = re.search(r'(20\d\d)', src)
        if m_yr:
            yr = int(m_yr.group(1))
            if ay - yr >= 1:
                photo_notes.append((os.path.basename(src), yr, ay - yr))

    return {
        'year_bumps': year_bumps,
        'leave_notes': leave_notes,
        'seasonal_phrases': seasonal_phrases,
        'photo_notes': photo_notes,
    }


def check_speagle_sync(people_data, helpers):
    """Compare data/people.json against ../joshspeagle.github.io/assets/data/content.json."""
    if not os.path.exists(SPEAGLE_CONTENT_PATH):
        return {'available': False, 'path': SPEAGLE_CONTENT_PATH}

    with open(SPEAGLE_CONTENT_PATH, encoding='utf-8') as fh:
        sp = json.load(fh)

    mentees_by_stage = (
        sp.get('sections', {}).get('mentorship', {}).get('menteesByStage', {})
    )
    everyone = {
        p['name']: s['heading']
        for s in people_data['sections']
        for p in s['people']
    }
    match_person = helpers['match_person']

    missing_active = []
    active_matched = set()
    stage_map = (
        ('postdoctoral', 'Postdoctoral Researchers'),
        ('doctoral', 'Graduate Students'),
        ('bachelors', 'Undergraduate Students'),
    )
    for sp_key, art_section in stage_map:
        for item in mentees_by_stage.get(sp_key, []):
            if item.get('myCareerStage') != 'Assistant Professor':
                continue
            raw_name = strip_tags(item.get('name', ''))
            if not raw_name:
                continue
            matched = match_person(raw_name, everyone)
            if matched:
                active_matched.add(matched)
            else:
                missing_active.append((raw_name, art_section, item.get('timelinePeriod', '')))

    completed_still_active = []
    completed = mentees_by_stage.get('completed', {})
    if isinstance(completed, dict):
        for comp_key, comp_list in completed.items():
            if not isinstance(comp_list, list):
                continue
            for item in comp_list:
                raw_name = strip_tags(item.get('name', ''))
                if not raw_name:
                    continue
                matched = match_person(raw_name, everyone)
                if matched in active_matched:
                    continue
                if matched and everyone[matched] in (
                    'Postdoctoral Researchers',
                    'Graduate Students',
                    'Undergraduate Students',
                ):
                    completed_still_active.append(
                        (matched, everyone[matched], comp_key, strip_tags(item.get('currentStatus', '')))
                    )

    return {
        'available': True,
        'path': SPEAGLE_CONTENT_PATH,
        'missing_active': missing_active,
        'completed_still_active': completed_still_active,
    }


def check_online(people_data, research_data, home_data, helpers):
    """Fetch Gwen Eadie's group page and verify external URLs."""
    eadie_url = 'https://www.astro.utoronto.ca/~eadie/students.html'
    eadie_unmatched = []
    eadie_status = 'ok'
    everyone = {
        p['name']: s['heading']
        for s in people_data['sections']
        for p in s['people']
    }
    match_person = helpers['match_person']

    try:
        req = urllib.request.Request(
            eadie_url, headers={'User-Agent': 'ART-Website-Updater/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        for m in re.finditer(r'<(?:h[234]|b|strong|li)[^>]*>([^<]{4,60})</', html):
            text = m.group(1).strip()
            words = text.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
                if not match_person(text, everyone):
                    eadie_unmatched.append(text)
    except Exception as exc:
        eadie_status = f'unreachable ({exc})'

    urls = set()
    for blob in (
        json.dumps(people_data),
        json.dumps(research_data),
        json.dumps(home_data),
    ):
        for m in re.finditer(r'https?://[^\s"<>\\]+', blob):
            urls.add(m.group(0))

    broken_urls = []
    for url in sorted(urls):
        try:
            req = urllib.request.Request(
                url,
                method='HEAD',
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ARTSiteCheck/1.0)'},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status >= 400:
                    broken_urls.append((url, resp.status))
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 405):
                continue
            broken_urls.append((url, exc.code))
        except Exception as exc:
            broken_urls.append((url, str(exc)))

    return {
        'eadie_status': eadie_status,
        'eadie_unmatched': sorted(set(eadie_unmatched))[:15],
        'checked_count': len(urls),
        'broken_urls': broken_urls,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--online', action='store_true',
                    help='fetch external pages and check external links')
    ap.add_argument('--as-of', metavar='YYYY-MM-DD',
                    help='override current date for seasonal rollover checks')
    ap.add_argument('--apply-years', action='store_true',
                    help='automatically apply graduate student year-of-study bumps')
    args = ap.parse_args()

    today = (
        datetime.date.fromisoformat(args.as_of)
        if args.as_of
        else datetime.date.today()
    )
    ay = academic_year(today)

    with open(PEOPLE_PATH, encoding='utf-8') as fh:
        people_data = json.load(fh)
    with open(RESEARCH_PATH, encoding='utf-8') as fh:
        research_data = json.load(fh)
    with open(HOME_PATH, encoding='utf-8') as fh:
        home_data = json.load(fh)

    helpers = load_audit_helpers()
    seasonal = check_seasonal_and_years(
        people_data, home_data, today, apply_years=args.apply_years
    )
    sync = check_speagle_sync(people_data, helpers)

    audit_cmd = [sys.executable, os.path.join(HERE, 'audit_site.py'), '--as-of', today.isoformat()]
    audit_proc = subprocess.run(audit_cmd, cwd=ROOT, capture_output=True, text=True)
    theme_cmd = [sys.executable, os.path.join(HERE, 'theme_fit.py'), '--quiet']
    theme_proc = subprocess.run(theme_cmd, cwd=ROOT, capture_output=True, text=True)

    print(f"# ART Website Update Proposal Digest ({today.isoformat()}, AY {ay}-{str(ay + 1)[2:]})\n")

    print("## 1. Cross-Repository Roster Sync (`joshspeagle.github.io`)")
    if not sync['available']:
        print(f"- Sibling repo not found at `{sync['path']}` (skipped).")
    else:
        if sync['missing_active']:
            print("- **Active Speagle mentees not found on ART People page:**")
            for name, sec, period in sync['missing_active']:
                print(f"  - `{name}` ({sec}, {period})")
        else:
            print("- All active UofT postdocs and doctoral mentees in `joshspeagle.github.io` are present on the ART People page.")
        if sync['completed_still_active']:
            print("- **Completed mentees still listed in current ART sections:**")
            for name, sec, stage, status in sync['completed_still_active']:
                print(f"  - `{name}` (currently in `{sec}`, marked completed `{stage}`: {status})")
        else:
            print("- No completed mentees from `joshspeagle.github.io` are lingering in active ART sections.")
    print()

    print("## 2. Seasonal & Date-Triggered Checks")
    if seasonal['year_bumps']:
        action = "Applied" if args.apply_years else "Proposed"
        print(f"- **{action} graduate student year-of-study updates ({len(seasonal['year_bumps'])}):**")
        for name, old_yr, new_yr in seasonal['year_bumps']:
            print(f"  - `{name}`: `{old_yr}-year` -> `{new_yr}-year`")
    else:
        print("- **Graduate student year-of-study labels:** all match `cohort` for this academic year.")

    if seasonal['leave_notes']:
        print("- **Leave / status notes:**")
        for name, note, expired in seasonal['leave_notes']:
            flag = "EXPIRED / DUE FOR REMOVAL" if expired else "active"
            print(f"  - `{name}` ({flag}): \"{note}\"")
    else:
        print("- **Leave / status notes:** none present.")

    if seasonal['seasonal_phrases']:
        print("- **Seasonal phrases to review:**")
        for name, cue, text in seasonal['seasonal_phrases']:
            print(f"  - `{name}` (`{cue}`): {text[:100]}...")
    else:
        print("- **Seasonal phrases:** no time-sensitive seasonal wording flagged.")

    if seasonal['photo_notes']:
        print("- **Home page dated photos:**")
        for fname, yr, age in seasonal['photo_notes']:
            print(f"  - `{fname}` ({yr}, {age} academic year(s) old)")
    print()

    print("## 3. Internal Consistency & Theme-Fit Summary")
    audit_summary = [
        line for line in audit_proc.stdout.splitlines()
        if line.endswith('finding(s).') or line.endswith('unreviewed candidate(s).')
    ]
    for line in audit_summary:
        print(f"- `audit_site.py`: {line}")
    for line in theme_proc.stdout.splitlines():
        if 'unreviewed candidate(s)' in line:
            print(f"- `theme_fit.py`: {line}")
    print()

    if args.online:
        print("## 4. Live Web & External Link Checks (`--online`)")
        online = check_online(people_data, research_data, home_data, helpers)
        print(f"- **Gwen Eadie's group page:** `{online['eadie_status']}`")
        if online['eadie_unmatched']:
            print(f"  - Candidate headings/names not on ART page: {', '.join(online['eadie_unmatched'])}")
        print(f"- **External URLs checked:** {online['checked_count']}")
        if online['broken_urls']:
            print(f"  - **Broken or unreachable URLs ({len(online['broken_urls'])}):**")
            for url, code in online['broken_urls']:
                print(f"    - `{url}` -> `{code}`")
        else:
            print("  - All external URLs responded cleanly.")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
