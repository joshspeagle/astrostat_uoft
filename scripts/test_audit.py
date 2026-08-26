#!/usr/bin/env python3
"""Regression tests for the name matching in audit_site.py.

    python3 scripts/test_audit.py

Name matching here is deliberately not "first token is the given name, last
token is the surname". Dual surnames and dual given names each break that
assumption in opposite directions, and getting it wrong produces silent false
positives (flagging someone who left as still present) or false negatives
(missing a real one). These cases pin the behaviour down.
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
caption_names = _ns['caption_names']
academic_year = _ns['academic_year']

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

    # academic year rolls over in September, not January
    for date, expected in ((datetime.date(2026, 8, 31), 2025),
                           (datetime.date(2026, 9, 1), 2026),
                           (datetime.date(2027, 1, 15), 2026)):
        got = academic_year(date)
        if got != expected:
            failures.append(f"academic_year({date}) == {got}, expected {expected}")

    total = len(NAME_CASES) + 4 + 3
    if failures:
        print(f"{len(failures)} of {total} checks FAILED:\n")
        for f in failures:
            print("  " + f)
        return 1
    print(f"all {total} checks pass")
    return 0


if __name__ == '__main__':
    sys.exit(main())
