#!/usr/bin/env python3
"""Regression tests for audit_site.py: name matching, and the id checks.

    python3 scripts/test_audit.py

Name matching is deliberately not "first token is the given name, last token is
the surname". Dual surnames and dual given names each break that assumption in
opposite directions, and getting it wrong produces silent false positives
(flagging someone who left as still present) or false negatives (missing a real
one). These cases pin the behaviour down. It is now used only where names are
still free text - the home page's group-photo caption - because Research
rosters name people by id.

The id checks are the other half: with data/research.json pointing at
data/people.json by id, the failure mode is no longer a misspelled name but a
dangling or duplicated id, which these cases pin down instead.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Load the helpers without running main()
_src = open(os.path.join(HERE, 'audit_site.py'), encoding='utf-8').read().split('def main(')[0]
_ns = {}
exec(_src, _ns)
mentioned = _ns['mentioned']
match_person = _ns['match_person']
caption_names = _ns['caption_names']
academic_year = _ns['academic_year']
theme_ids = _ns['theme_ids']
research_ids = _ns['research_ids']
unknown_ids = _ns['unknown_ids']
duplicate_ids = _ns['duplicate_ids']
out_of_size_order = _ns['out_of_size_order']
flip_not_wired = _ns['flip_not_wired']

import datetime

ROSTER = ("Gwen Eadie, Josh Speagle, Rodrigo Barradas Herrera, Peter Martin, "
          "Maria Garcia, David Li, Ann B Lee, Renee Hlozek, "
          "Isabelle (Liyuan) Huang, Adam Muzzin (York), Seiji Fujimoto")

NAME_CASES = [
    # (name, expected, why)
    ("Rodrigo Barradas Herrera", True,  "dual surname, full form present"),
    ("Antonio Herrera Martin",   False, "shares only 'Martin' with a different Peter Martin"),
    ("Gwendolyn Eadie",          True,  "short given name 'Gwen' used in the text"),
    ("Joshua S. Speagle (沈佳士)", True,  "short given name, middle initial, CJK suffix"),
    ("David (Dayi) Li",          True,  "parenthetical middle name is ignored"),
    ("Maria Jose Garcia Lopez",  True,  "dual given and dual surname, both shortened"),
    ("Peter Martin",             True,  "exact match"),
    ("Ann B Lee",                True,  "middle initial without a period"),
    ("Renee Hlozek",             True,  "exact match"),
    ("Someone Entirely Absent",  False, "genuinely not present"),
    ("Martin Peterson",          False, "token overlap in the wrong order is not a match"),
    # the parenthetical here is in the TEXT, not the name: "Isabelle (Liyuan) Huang"
    # splits the adjacent pair the matcher looks for, which silently hid her from the
    # "on no research theme" check until the text was normalised too.
    ("Isabelle (Liyuan) Huang", True,  "parenthetical in the text, name carries it too"),
    ("Isabelle Huang",          True,  "bare name against a parenthetical form in the text"),
    ("Muzzin Fujimoto",         False, "stripping '(York)' must not join across the comma"),
]

# A research.json with the defects the id checks exist to catch:
#   - "leo-watson" is on a theme but is not an id in the people fixture
#   - "tri-nguyen" is listed twice in the same row
#   - both themes claim the id "alpha"
#   - the larger theme sits below the smaller one
RESEARCH = {
    'themes': [
        {
            'id': 'alpha',
            'title': 'Alpha',
            'image': 'alpha.jpg',
            'members': ['christian-kragh-jespersen'],
            'associates': [{'id': 'tri-nguyen', 'note': 'Northeastern'}, 'tri-nguyen'],
            'collaborators': [],
        },
        {
            'id': 'alpha',
            'title': 'Beta',
            'image': 'beta.jpg',
            'members': ['christian-kragh-jespersen', 'leo-watson'],
            'associates': ['tri-nguyen'],
            'collaborators': ['jo-bovy'],
        },
    ],
}

PEOPLE = {
    'sections': [
        {'heading': 'Postdoctoral Researchers', 'layout': 'cards', 'people': [
            {'id': 'christian-kragh-jespersen', 'name': 'Christian Kragh Jespersen'},
            {'id': 'tri-nguyen', 'name': 'Tri Nguyen'},
        ]},
        {'heading': 'Collaborators', 'layout': 'compact', 'people': [
            {'id': 'jo-bovy', 'name': 'Jo Bovy'},
            {'id': 'jo-bovy', 'name': 'Jo Bovy (duplicate entry)'},
            {'name': 'Nobody Atall'},
        ]},
    ],
}

CAPTION = ('<figcaption>ART Group photo (Summer 2025). From left to right: Kevin McKinnon, '
           'Gwen Eadie, and Josh Speagle (with Alejandro Ortega Cruz Prieto featured in the '
           'background).</figcaption>')


def main():
    failures = []

    for name, expected, why in NAME_CASES:
        got = mentioned(name, ROSTER)
        if got != expected:
            failures.append(f"mentioned({name!r}) == {got}, expected {expected} - {why}")

    names = caption_names(CAPTION)
    for expect in ('Kevin McKinnon', 'Gwen Eadie', 'Josh Speagle', 'Alejandro Ortega Cruz Prieto'):
        if expect not in names:
            failures.append(f"caption_names missed {expect!r}; got {names}")

    # the caption is the one place names are still free text, so the audit
    # resolves them against the roster with mentioned()
    roster = {'Gwendolyn Eadie': 'Faculty', 'Samantha Berek (Ph.D. \'25)': 'Recent Alumni'}
    if match_person('Gwen Eadie', roster) != 'Gwendolyn Eadie':
        failures.append('match_person did not resolve a short given name in the caption')
    if match_person('Sam Berek', roster) != "Samantha Berek (Ph.D. '25)":
        failures.append('match_person did not resolve a caption name to an alumni entry')
    if match_person('Alejandro Ortega Cruz Prieto', roster) is not None:
        failures.append('match_person matched somebody who is not on the People page')

    # --- Research ids (checks 3, 4, 5, 11, 12) ---
    known = {p['id'] for sec in PEOPLE['sections'] for p in sec['people'] if p.get('id')}

    # a roster entry may be a bare id or {'id': ..., 'note': ...}; both count
    rows = dict(theme_ids(RESEARCH['themes'][0]))
    if rows['associates'] != ['tri-nguyen', 'tri-nguyen']:
        failures.append(f"theme_ids did not unwrap a noted entry: {rows['associates']}")
    if rows['collaborators'] != []:
        failures.append('theme_ids should report an empty row as empty')

    # who is on a theme, and on which
    where = research_ids(RESEARCH)
    if where.get('jo-bovy') != {'Beta'}:
        failures.append(f"research_ids put jo-bovy on {where.get('jo-bovy')}, expected Beta")
    if where.get('christian-kragh-jespersen') != {'Alpha', 'Beta'}:
        failures.append('research_ids should report every theme a person is on')
    if 'nobody-atall' in where:
        failures.append('research_ids invented an id that is not in the file')

    # an id naming nobody must be caught (the build fails on it too)
    bad = unknown_ids(RESEARCH, known)
    if [(t, i) for t, _, i in bad] != [('Beta', 'leo-watson')]:
        failures.append(f'unknown_ids reported {bad}, expected only leo-watson on Beta')
    if bad and bad[0][1] != 'ART members involved':
        failures.append(f'unknown_ids mislabelled the row: {bad[0][1]}')
    if unknown_ids(RESEARCH, known | {'leo-watson'}):
        failures.append('unknown_ids flagged an id that is on the People page')

    # duplicates: two people with one id, two themes with one id, one person
    # listed twice in a row, and a person with no id at all
    dupes = duplicate_ids(RESEARCH, PEOPLE)
    for expect in ('jo-bovy (People) is used by more than one person',
                   'Nobody Atall (People) has no id',
                   'alpha (Research) is used by more than one theme',
                   'tri-nguyen listed twice under ART associates involved on Alpha'):
        if expect not in dupes:
            failures.append(f'duplicate_ids missed {expect!r}; got {dupes}')

    # theme order: Beta (4) sits below Alpha (3)
    order = out_of_size_order(RESEARCH)
    if len(order) != 1 or not order[0].startswith('Alpha'):
        failures.append(f'out_of_size_order reported {order}, expected Alpha above Beta')
    if out_of_size_order({'themes': list(reversed(RESEARCH['themes']))}):
        failures.append('out_of_size_order flagged a correctly ordered file')

    # the theme-flip check: it fires only while the renderer states the flip and
    # the stylesheet still decides it by sibling position
    EMITS = "    const flip = i % 2 === 1 ? ' media-flip' : '';"
    NO_FLIP = "    const flip = '';"
    NTH = '.media-object {\n  &:nth-child(odd) {\n    order: 2;\n  }\n}'
    KEYED = '.media-object {\n  &.media-flip {\n    order: 2;\n  }\n}'
    for renderer, style, want, why in (
        (EMITS,   NTH,   True,  'renderer flips, stylesheet does not know the class'),
        (EMITS,   KEYED, False, 'stylesheet keys off media-flip'),
        (NO_FLIP, NTH,   False, 'renderer no longer states the flip'),
        (None,    NTH,   False, 'renderer missing - check is skipped'),
        (EMITS,   None,  False, 'stylesheet missing - check is skipped'),
    ):
        got = bool(flip_not_wired(renderer, style))
        if got != want:
            failures.append(f'flip_not_wired == {got}, expected {want} ({why})')

    # it should cite the offending line, so the one-line fix is findable
    cited = flip_not_wired(EMITS, NTH)
    if not cited or ':2' not in cited[0]:
        failures.append(f'flip_not_wired did not cite the nth-child line: {cited}')

    # academic year rolls over in September, not January
    for date, expected in ((datetime.date(2026, 8, 31), 2025),
                           (datetime.date(2026, 9, 1), 2026),
                           (datetime.date(2027, 1, 15), 2026)):
        got = academic_year(date)
        if got != expected:
            failures.append(f"academic_year({date}) == {got}, expected {expected}")

    total = len(NAME_CASES) + 4 + 3 + 14 + 6
    if failures:
        print(f"{len(failures)} of {total} checks FAILED:\n")
        for f in failures:
            print("  " + f)
        return 1
    print(f"all {total} checks pass")
    return 0


if __name__ == '__main__':
    sys.exit(main())
