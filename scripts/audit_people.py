#!/usr/bin/env python3
"""Consistency checks for the ART site's roster content.

Run from the repo root:

    python3 scripts/audit_people.py            # report findings, always exit 0
    python3 scripts/audit_people.py --strict   # exit 1 if anything is flagged

Checks (all stdlib, no dependencies):

  1. Year-of-study labels that have gone stale, using each person's `cohort`
     (the calendar year they started). Bumps every September.
  2. Grad-student entries carrying a year label but no `cohort`.
  3. Current members who appear on no Research theme, and alumni still listed
     there. Matched on surname, since the two pages use different name forms.
  4. Entries with no photo.
  5. How far behind the home page's "last updated" line is.
"""

import argparse
import datetime
import json
import re
import sys

PEOPLE = 'data/people.json'
RESEARCH = 'ejs/pages/research/body.html'
HOME = 'ejs/pages/home/body.html'

# Sections whose members are expected to appear on a Research theme.
CURRENT = {'Faculty', 'Postdoctoral Researchers', 'Graduate Students', 'ART Associates'}

YEAR_LABEL = re.compile(r'\b(\d)(?:st|nd|rd|th)-year\b')
ORDINALS = {1: '1st', 2: '2nd', 3: '3rd'}


def ordinal(n):
    return ORDINALS.get(n, f'{n}th')


def academic_year(today):
    """The calendar year an academic year starts in (rolls over in September)."""
    return today.year if today.month >= 9 else today.year - 1


def surname(name):
    """Last word of the name, ignoring any parenthetical suffix."""
    return re.sub(r'\s*\([^)]*\)', '', name).strip().split()[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 if any check reports a finding')
    ap.add_argument('--as-of', metavar='YYYY-MM-DD',
                    help='pretend today is this date (for testing seasonal checks)')
    args = ap.parse_args()

    data = json.load(open(PEOPLE, encoding='utf-8'))
    research_text = re.sub(r'<[^>]+>', ' ', open(RESEARCH, encoding='utf-8').read())
    home = re.sub(r'\s+', ' ', open(HOME, encoding='utf-8').read())

    today = (datetime.date.fromisoformat(args.as_of) if args.as_of
             else datetime.date.today())
    ay = academic_year(today)

    stale, no_cohort, missing, lingering, no_photo = [], [], [], [], []

    for section in data['sections']:
        for person in section['people']:
            name = person['name']
            paras = person['paragraphs']

            # 1 + 2: year-of-study labels
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

            # 3: People <-> Research
            seen = re.search(r'\b' + re.escape(surname(name)) + r'\b', research_text)
            if section['heading'] in CURRENT and not seen:
                missing.append(f"{name} ({section['heading']})")
            if section['heading'] == 'Recent Alumni' and seen:
                lingering.append(name)

            # 4: photos
            if not person.get('image'):
                no_photo.append(f"{name} ({section['heading']})")

    print(f"ART roster audit - {today.isoformat()} (academic year {ay}-{str(ay + 1)[2:]})\n")

    findings = 0

    print(f"[1] Stale year-of-study labels ({len(stale)})")
    for name, was, now in stale:
        print(f"      {name}: says {was}-year, should be {now}-year")
    findings += len(stale)
    if not stale:
        print("      none")

    print(f"\n[2] Year label but no `cohort` field ({len(no_cohort)})")
    for name in no_cohort:
        print(f"      {name}  -- add \"cohort\": <start year> so this can be checked")
    findings += len(no_cohort)
    if not no_cohort:
        print("      none")

    print(f"\n[3] Current members on no Research theme ({len(missing)})")
    for m in missing:
        print(f"      {m}")
    print(f"    Alumni still listed on Research ({len(lingering)})")
    for m in lingering:
        print(f"      {m}  -- remove from the theme lists")
    findings += len(missing) + len(lingering)
    if not missing and not lingering:
        print("      none")

    print(f"\n[4] Entries with no photo ({len(no_photo)})")
    for m in no_photo:
        print(f"      {m}")
    findings += len(no_photo)
    if not no_photo:
        print("      none")

    print("\n[5] Home page 'last updated' line")
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
                print("      -- bump it as part of this update")
                findings += 1
        except ValueError:
            print(f"      unparseable date: {m.group(1)}")
            findings += 1

    print(f"\n{findings} finding(s).")
    if args.strict and findings:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
