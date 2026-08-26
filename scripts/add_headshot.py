#!/usr/bin/env python3
"""Prepare a headshot for static/ from a local file or a URL.

    python3 scripts/add_headshot.py <source> static/name.jpg [--anchor 0.5] [--size 500]

Square-crops, resizes and re-encodes as JPEG so new headshots match the
existing thumbnails (square, roughly 350-500px, well under the 244 KB that
trips webpack's asset size warning).

  --anchor  where the square sits vertically in a taller-than-wide image:
            0.0 flush to the top, 1.0 flush to the bottom, 0.5 centred.
            Portraits usually want a low value, since faces sit high in frame.
            Horizontal cropping is always centred.
  --size    output edge length in pixels (default 500).

Always eyeball the result before committing - there is no face detection here.
Remember static/ is Git LFS-tracked: `git lfs ls-files | grep <name>` should
list the file after `git add`, or it will commit as a pointer and render broken.
"""

import argparse
import io
import os
import sys
import urllib.request

from PIL import Image


def load(source):
    if source.startswith(('http://', 'https://')):
        req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return Image.open(io.BytesIO(r.read()))
    return Image.open(source)


def square_crop(im, anchor=0.5):
    w, h = im.size
    edge = min(w, h)
    left = (w - edge) // 2                          # horizontal: always centred
    top = int(round((h - edge) * anchor))           # vertical: caller's choice
    top = max(0, min(top, h - edge))
    return im.crop((left, top, left + edge, top + edge))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', help='local path or URL')
    ap.add_argument('dest', help='output path, e.g. static/jane_doe.jpg')
    ap.add_argument('--anchor', type=float, default=0.5,
                    help='vertical crop anchor, 0.0 top to 1.0 bottom (default 0.5)')
    ap.add_argument('--size', type=int, default=500, help='output edge in px (default 500)')
    ap.add_argument('--quality', type=int, default=85)
    args = ap.parse_args()

    if not 0.0 <= args.anchor <= 1.0:
        sys.exit('--anchor must be between 0.0 and 1.0')

    im = load(args.source).convert('RGB')
    before = im.size
    im = square_crop(im, args.anchor)
    im = im.resize((args.size, args.size), Image.LANCZOS)

    os.makedirs(os.path.dirname(args.dest) or '.', exist_ok=True)
    im.save(args.dest, 'JPEG', quality=args.quality, optimize=True)

    kb = os.path.getsize(args.dest) / 1024
    print(f"{before[0]}x{before[1]} -> {args.size}x{args.size}  {kb:.0f} KB  {args.dest}")
    if kb > 244:
        print("  warning: over 244 KB, which trips webpack's asset size warning")
    return 0


if __name__ == '__main__':
    sys.exit(main())
