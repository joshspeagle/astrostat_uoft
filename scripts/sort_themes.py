#!/usr/bin/env python3
"""Order the Research page's themes by how many people they involve.

    python3 scripts/sort_themes.py            # report the order, change nothing
    python3 scripts/sort_themes.py --apply    # rewrite ejs/pages/research/body.html

Themes are sorted by TOTAL roster size (members + associates + collaborators),
largest first. Total rather than members-only is deliberate: it keeps the
breadth of a theme visible, so one with many outside collaborators is not
pushed down the page for having fewer people inside the group.

Ties keep their current relative order, so re-running on an unchanged file is a
no-op and a tie never silently reshuffles the page.

The file is treated as a list of <h2>-delimited blocks. Everything before the
first <h2> (the intro) and the trailing </section> are left alone; only whole
blocks move, so the markup inside a theme is never touched.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.join(HERE, os.pardir, 'ejs', 'pages', 'research', 'body.html')

ROSTER_LABELS = ('ART members involved', 'ART associates involved',
                 'Collaborators include')


def split_themes(html):
    """(preamble, [(title, block)], tail) where block excludes its own <h2>."""
    marks = [m.start() for m in re.finditer(r'^  <h2>', html, re.M)]
    if not marks:
        raise SystemExit('no <h2> theme headings found')
    tail_at = html.rindex('</section>')
    preamble = html[:marks[0]]
    bounds = marks + [tail_at]
    themes = []
    for i, start in enumerate(marks):
        chunk = html[start:bounds[i + 1]]
        title = re.match(r'  <h2>(.*?)</h2>', chunk, re.S).group(1)
        themes.append((title, chunk))
    return preamble, themes, html[tail_at:]


def roster_counts(block):
    """(members, associates, collaborators) named in one theme block."""
    counts = []
    for label in ROSTER_LABELS:
        m = re.search(label + r':</strong>(.*?)(?:<br>|</p>)', block, re.S)
        if not m:
            counts.append(0)
            continue
        text = re.sub(r'<[^>]+>', '', m.group(1))
        counts.append(len([n for n in text.split(',') if n.strip()]))
    return tuple(counts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true',
                    help='rewrite the file instead of only reporting')
    args = ap.parse_args()

    html = open(RESEARCH, encoding='utf-8').read()
    preamble, themes, tail = split_themes(html)

    sized = []
    for pos, (title, block) in enumerate(themes):
        mem, assoc, collab = roster_counts(block)
        sized.append((mem + assoc + collab, pos, title, block, mem, assoc, collab))

    # -total sorts descending; pos keeps ties in their current order
    ordered = sorted(sized, key=lambda r: (-r[0], r[1]))

    width = max(len(re.sub(r'&amp;', '&', t)) for _, _, t, _, _, _, _ in sized)
    print(f"{'#':<4}{'theme':<{width + 2}}{'mem':>4}{'assoc':>7}{'collab':>8}{'total':>7}   was")
    for new_pos, (total, old_pos, title, _, mem, assoc, collab) in enumerate(ordered):
        moved = '' if new_pos == old_pos else f'  <- #{old_pos + 1}'
        print(f"{new_pos + 1:<4}{re.sub('&amp;', '&', title):<{width + 2}}"
              f"{mem:>4}{assoc:>7}{collab:>8}{total:>7}   {old_pos + 1}{moved}")

    if [r[1] for r in ordered] == list(range(len(ordered))):
        print('\nalready in order; nothing to do')
        return 0

    if not args.apply:
        print('\nrun again with --apply to rewrite the page')
        return 0

    open(RESEARCH, 'w', encoding='utf-8').write(
        preamble + ''.join(r[3] for r in ordered) + tail)
    print(f'\nrewrote {os.path.relpath(RESEARCH, os.path.join(HERE, os.pardir))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
