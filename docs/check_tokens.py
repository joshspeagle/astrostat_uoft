#!/usr/bin/env python3
"""The ART site's colour canon as code.

Every hex value on this site lives in **scss/_tokens.scss** and nowhere else.
This script reads the palette back out of that file, holds the surfaces and
every pair the site draws, measures the contrast of each pair rather than
judging it, prints the full matrix and a PASS/FAIL line per declared pair, and
exits 1 if any declared pair is under its floor.

Floors: 4.5 for text, 3.0 for a mark the reader has to find or follow.
Decoration carries no information and has no floor; it is reported so that a
change to it is visible, never asserted.

docs/DESIGN.md is the prose; this is the arithmetic; the stylesheet is the
source. A pair this script does not list is a pair the site must not draw.

Usage:  python3 docs/check_tokens.py [--quiet]
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_SCSS = os.path.join(ROOT, "scss", "_tokens.scss")
FAVICON_SVG = os.path.join(ROOT, "ico", "favicon.svg")

# The role each token carries. The hexes come from the stylesheet; these are the
# meanings the canon assigns them, and the reason the pairs below are the only
# ones the site may draw.
ROLES = {
    "page":  "page surface",
    "card":  "card and roster surface",
    "wash":  "hero logo wash (decoration only)",
    "ink":   "body text and headings",
    "link":  "interactive text, focus ring, switch on-state",
    "mark":  "the ART mark and the sparkle favicon",
    "quiet": "captions, footer, dividers, switch off-track",
}


def read_palette(path=TOKENS_SCSS):
    """The $themes map in scss/_tokens.scss, as {theme: {token: (hex, role)}}.

    Parsed rather than restated: if the stylesheet and this script could each
    hold a copy of the palette, one of them would eventually be wrong.
    """
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    themes = {}
    for theme, body in re.findall(r"(light|dark):\s*\(([^)]*)\)", src):
        entries = dict(re.findall(r"([a-z]+):\s*(#[0-9a-fA-F]{6})", body))
        themes[theme] = {k: (v, ROLES.get(k, "")) for k, v in entries.items()}
    missing = [t for t in ("light", "dark")
               if sorted(themes.get(t, {})) != sorted(ROLES)]
    if missing:
        raise SystemExit(
            "%s: expected a $themes map with light and dark blocks naming "
            "exactly %s; could not read %s"
            % (path, ", ".join(sorted(ROLES)), " and ".join(missing)))
    return themes


TOKENS = read_palette()

SURFACES = ("page", "card", "wash")

# --------------------------------------------------------------------------
# Every pair the site actually draws: (ink token, surface token, kind, where).
# A pair not listed here is a pair the site must not draw.
# --------------------------------------------------------------------------

PAIRS = [
    ("ink",   "page",  "text",       "body copy, headings, roster names"),
    ("ink",   "card",  "text",       "People card and roster block text"),
    ("ink",   "wash",  "text",       "hero wordmark over the logo wash"),
    ("link",  "page",  "text",       "links in prose and navigation"),
    ("link",  "card",  "text",       "links inside a card or roster"),
    ("link",  "wash",  "mark",       "focus ring crossing the hero"),
    ("quiet", "page",  "text",       "figure captions and the site note"),
    ("quiet", "card",  "text",       "a caption set inside a card"),
    ("mark",  "page",  "mark",       "the ART mark, the favicon particle"),
    ("page",  "quiet", "mark",       "theme switch paddle, off"),
    ("page",  "link",  "mark",       "theme switch paddle, on"),
    ("wash",  "page",  "decoration", "the hero wash itself: carries nothing"),
]

FLOORS = {"text": 4.5, "mark": 3.0, "large": 3.0, "decoration": None}

# --------------------------------------------------------------------------
# Values this canon retired, kept here as the evidence for the ruling. These
# are measured and printed, never asserted: the point of the row is the number
# that failed. docs/DESIGN.md quotes them.
# --------------------------------------------------------------------------

RETIRED = [
    ("#888888", "light", "page",  "text", "one shared caption grey"),
    ("#888888", "light", "card",  "text", "one shared caption grey"),
    ("#888888", "dark",  "page",  "text", "one shared caption grey"),
    ("#888888", "dark",  "card",  "text", "one shared caption grey"),
    ("#82c7ce", "light", "card",  "mark", "teal, as an image placeholder fill"),
    ("#31767d", "dark",  "card",  "mark", "teal, as an image placeholder fill"),
    ("#333333", "light", "page",  "mark", "switch off-track borrowed from the dark card"),
]


def _channel(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------
# The two places outside the stylesheet that a hex is unavoidable: the favicon,
# which has to carry both themes itself because a browser tab has no CSS, and
# any other stylesheet file, which must carry none at all.
# --------------------------------------------------------------------------

def check_assets():
    """Report on the hexes written outside scss/_tokens.scss. Returns a list of
    complaints, empty when every one of them is a token doing its own job."""
    bad = []

    try:
        with open(FAVICON_SVG, encoding="utf-8") as fh:
            svg = fh.read()
    except OSError:
        return ["ico/favicon.svg is missing"]
    found = {h.lower() for h in re.findall(r"fill:\s*(#[0-9a-fA-F]{6})", svg)}
    want = {TOKENS["light"]["mark"][0].lower(), TOKENS["dark"]["mark"][0].lower()}
    if found != want:
        bad.append("ico/favicon.svg fills %s; the sparkle is the mark token, %s"
                   % (", ".join(sorted(found)) or "nothing", ", ".join(sorted(want))))

    scss = os.path.join(ROOT, "scss")
    # Every stylesheet under scss/, subdirectories included, so a partial that
    # comes back in a folder cannot smuggle a colour past the check.
    files = sorted(os.path.relpath(os.path.join(d, f), scss)
                   for d, _, fs in os.walk(scss) for f in fs)
    for name in files:
        if not name.endswith(".scss") or name == "_tokens.scss":
            continue
        with open(os.path.join(scss, name), encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                for hexv in re.findall(r"#[0-9a-fA-F]{3,8}\b", line):
                    bad.append("scss/%s:%d restates a colour (%s); the palette "
                               "lives in scss/_tokens.scss" % (name, n, hexv))
    return bad


def main(argv):
    quiet = "--quiet" in argv
    failures = []

    for theme in ("light", "dark"):
        toks = TOKENS[theme]

        if not quiet:
            print(f"\n{'=' * 74}\n{theme.upper()} THEME\n{'=' * 74}")
            print(f"\n{'token':<7} {'hex':<9} {'Y':>6}   role")
            print("-" * 74)
            for name, (hexv, role) in toks.items():
                print(f"{name:<7} {hexv:<9} {luminance(hexv) * 100:6.2f}   {role}")

            print(f"\ncontrast matrix (token x surface)\n" + "-" * 74)
            head = "        " + "".join(f"{s + ' (' + toks[s][0] + ')':>22}" for s in SURFACES)
            print(head)
            for name in toks:
                row = f"{name:<8}" + "".join(
                    f"{contrast(toks[name][0], toks[s][0]):>22.2f}" for s in SURFACES)
                print(row)

            print(f"\ndeclared pairs\n" + "-" * 74)

        for ink, surf, kind, where in PAIRS:
            ratio = contrast(toks[ink][0], toks[surf][0])
            floor = FLOORS[kind]
            if floor is None:
                verdict = "  --  "
            elif ratio >= floor:
                verdict = " PASS "
            else:
                verdict = " FAIL "
                failures.append((theme, ink, surf, kind, ratio, floor))
            if not quiet:
                need = "n/a" if floor is None else f"{floor:.1f}"
                print(f"[{verdict}] {ink:>5} on {surf:<5} {ratio:6.2f} "
                      f"(floor {need:>3}, {kind:<10}) {where}")

    print(f"\n{'=' * 74}\nRETIRED VALUES, measured for the record\n" + "-" * 74)
    for hexv, theme, surf, kind, what in RETIRED:
        surf_hex = TOKENS[theme][surf][0]
        ratio = contrast(hexv, surf_hex)
        floor = FLOORS[kind]
        note = "under floor" if ratio < floor else "clears floor"
        print(f"  {hexv} on {theme} {surf} ({surf_hex}) = {ratio:5.2f}  "
              f"floor {floor:.1f} {kind:<4} {note:<11} - {what}")

    assets = check_assets()
    print(f"\n{'=' * 74}\nHEXES OUTSIDE THE STYLESHEET\n" + "-" * 74)
    if assets:
        for line in assets:
            print(f"  [ FAIL ] {line}")
    else:
        print("  [ PASS ] ico/favicon.svg carries the mark token in both themes;")
        print("           no other stylesheet file names a colour.")

    print(f"\n{'=' * 74}")
    if failures or assets:
        print(f"{len(failures)} pair(s) under floor:")
        for theme, ink, surf, kind, ratio, floor in failures:
            print(f"  {theme}: {ink} on {surf} = {ratio:.2f}, floor {floor:.1f} ({kind})")
        return 1
    if assets:
        print(f"{len(assets)} colour(s) written outside scss/_tokens.scss:")
        for line in assets:
            print(f"  {line}")
        return 1
    print("All declared pairs clear their floor in both themes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
