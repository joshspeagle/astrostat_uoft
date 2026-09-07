#!/usr/bin/env python3
"""Rebuild the whole ART icon + identity set.

    python3 build.py          # svgs, sprite, favicons, og-image, sheet, test page

Needs Pillow and Playwright (chromium). Everything else is stdlib.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import icons, brand, measure, mkog, mktest, mksheet   # noqa: E402


def sh(*a):
    subprocess.run([sys.executable] + list(a), cwd=HERE, check=True)


def main():
    for slug, label, body in icons.ICONS:
        open(os.path.join(HERE, slug + '.svg'), 'w').write(
            icons.standalone(slug, label, body))
    open(os.path.join(HERE, 'themes-sprite.svg'), 'w').write(icons.sprite())
    brand.build(HERE)
    measure.run()
    sh('mkog.py')
    sh('mktest.py')
    sh('mksheet.py')
    # rasters, at 2x then box-down for clean text
    from PIL import Image
    sh('shoot.py', os.path.join(HERE, 'og-image.html'), '_og2x.png', '1200', '630', 'view')
    # BOX, not LANCZOS: an exact 2:1 area average, so the 2px rule downsamples to
    # a solid 2px of #6b6b6b instead of a ringing hairline that is not a token.
    Image.open(os.path.join(HERE, '_og2x.png')).resize((1200, 630), Image.BOX)\
         .convert('RGB').save(os.path.join(HERE, 'og-image.png'))
    os.remove(os.path.join(HERE, '_og2x.png'))
    sh('shoot.py', os.path.join(HERE, 'sheet.html'), '_sheet2x.png', '1360', '900', 'full')
    im = Image.open(os.path.join(HERE, '_sheet2x.png'))
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).convert('RGB')\
      .save(os.path.join(HERE, 'sheet.png'))
    os.remove(os.path.join(HERE, '_sheet2x.png'))
    print('built', len(icons.ICONS), 'glyphs + sprite + favicons + og + sheet')


if __name__ == '__main__':
    main()
