#!/usr/bin/env python3
"""Order the Research page's themes by how many people they involve.

    python3 scripts/sort_themes.py            # report the order, change nothing
    python3 scripts/sort_themes.py --apply    # rewrite data/research.json

Themes are sorted by TOTAL roster size (members + associates + collaborators),
largest first. Total rather than members-only is deliberate: it keeps the
breadth of a theme visible, so one with many outside collaborators is not
pushed down the page for having fewer people inside the group.

Ties keep their current relative order, so re-running on an unchanged file is a
no-op and a tie never silently reshuffles the page.

Only the `themes` list is reordered; every theme keeps its own contents, and
the file is written back with the same 2-space indentation it is stored in.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.join(HERE, os.pardir, 'data', 'research.json')

ROSTER_KEYS = ('members', 'associates', 'collaborators')


def roster_counts(theme):
    """(members, associates, collaborators) named in one theme."""
    return tuple(len(theme.get(key) or []) for key in ROSTER_KEYS)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true',
                    help='rewrite the file instead of only reporting')
    args = ap.parse_args()

    data = json.load(open(RESEARCH, encoding='utf-8'))
    themes = data['themes']

    sized = []
    for pos, theme in enumerate(themes):
        mem, assoc, collab = roster_counts(theme)
        sized.append((mem + assoc + collab, pos, theme, mem, assoc, collab))

    # -total sorts descending; pos keeps ties in their current order
    ordered = sorted(sized, key=lambda r: (-r[0], r[1]))

    width = max(len(t['title']) for t in themes)
    print(f"{'#':<4}{'theme':<{width + 2}}{'mem':>4}{'assoc':>7}{'collab':>8}{'total':>7}   was")
    for new_pos, (total, old_pos, theme, mem, assoc, collab) in enumerate(ordered):
        moved = '' if new_pos == old_pos else f'  <- #{old_pos + 1}'
        print(f"{new_pos + 1:<4}{theme['title']:<{width + 2}}"
              f"{mem:>4}{assoc:>7}{collab:>8}{total:>7}   {old_pos + 1}{moved}")

    if [r[1] for r in ordered] == list(range(len(ordered))):
        print('\nalready in order; nothing to do')
        return 0

    if not args.apply:
        print('\nrun again with --apply to rewrite the page')
        return 0

    data['themes'] = [r[2] for r in ordered]
    with open(RESEARCH, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print(f'\nrewrote {os.path.relpath(RESEARCH, os.path.join(HERE, os.pardir))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
