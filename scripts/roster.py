#!/usr/bin/env python3
"""Print the current roster, for reviewing one section at a time.

    python3 scripts/roster.py                             # every section
    python3 scripts/roster.py "Postdoctoral Researchers"  # one section
    python3 scripts/roster.py postdoc                     # case-insensitive substring

Prints each person with a one-line summary of their stated role, so a section
can be reviewed and corrected as a list rather than from memory.
"""

import json
import re
import sys

PEOPLE = 'data/people.json'


def summarize(person, width=150):
    """Opening of the bio, trimmed to a readable one-liner.

    Deliberately not split on the first period: names like "David A. Dunlap"
    and "Ph.D." abbreviate mid-sentence and would cut the summary short.
    """
    for para in person['paragraphs']:
        if para.strip().startswith('<a') and 'Personal Website' in para:
            continue
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', para)).strip()
        if len(text) <= width:
            return text
        cut = text[:width].rsplit(' ', 1)[0]
        return cut + '...'
    return ''


def main():
    data = json.load(open(PEOPLE, encoding='utf-8'))
    want = ' '.join(sys.argv[1:]).strip().lower()

    sections = [s for s in data['sections'] if not want or want in s['heading'].lower()]
    if not sections:
        print(f"No section matching {want!r}. Available:")
        for s in data['sections']:
            print('   ', s['heading'])
        return 1

    for section in sections:
        print(f"\n{section['heading']} ({len(section['people'])})")
        print('-' * (len(section['heading']) + 8))
        for i, person in enumerate(section['people'], 1):
            extra = f"  [cohort {person['cohort']}]" if person.get('cohort') else ''
            photo = '' if person.get('image') else '  [NO PHOTO]'
            print(f"{i:3}. {person['name']}{extra}{photo}")
            summary = summarize(person)
            if summary:
                print(f"     {summary}")
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
