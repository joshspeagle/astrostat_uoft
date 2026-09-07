"""Render the 180 apple-touch and 512 manifest icons.

Owner ruling (7 Sep): the FULL ART mark on a page-surface (white) tile,
tight-cropped to the path's bounding box, centred, ~86% of the tile width.
Tight-cropping is done the way design/appicon-c.html does it: read the path's
getBBox() in the browser and rewrite the SVG viewBox to it.
"""
import io, os, pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]   # the repo root
MARK = (ROOT / 'svg/art-mark.svg').read_text()
MARK_TOKEN = '#001f4e'   # canon: the ART mark
PAGE_TOKEN = '#fefefe'   # canon: the page surface

SIDE = 512
SCALE = 3                # render 1536, box-downsample to 512 / 180

HTML = f"""<!doctype html><meta charset=utf-8><style>
html,body{{margin:0;padding:0;background:{PAGE_TOKEN}}}
#tile{{width:{SIDE}px;height:{SIDE}px;background:{PAGE_TOKEN};
 display:flex;align-items:center;justify-content:center;overflow:hidden}}
#tile svg{{width:86%;height:auto;display:block;color:{MARK_TOKEN}}}
#tile svg path{{fill:currentColor}}
</style><div id="tile">{MARK}</div>
<script>
// tight-crop: set the viewBox to the path's bounding box in user units
const s=document.querySelector('#tile svg'), p=s.querySelector('path');
const b=p.getBBox(), g=p.closest('g');
const m=g?g.transform.baseVal.consolidate().matrix:{{e:0,f:0}};
s.setAttribute('viewBox', `${{b.x+m.e}} ${{b.y+m.f}} ${{b.width}} ${{b.height}}`);
s.removeAttribute('preserveAspectRatio');
document.title = [b.x+m.e,b.y+m.f,b.width,b.height].map(n=>n.toFixed(2)).join(' ');
</script>"""

with sync_playwright() as pw:
    # Playwright's own browser resolution, unless PW_CHROMIUM names an executable.
    exe = os.environ.get('PW_CHROMIUM')
    br = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
    pg = br.new_page(viewport={'width': SIDE, 'height': SIDE}, device_scale_factor=SCALE)
    pg.set_content(HTML)
    print('bbox:', pg.title())
    shot = pg.locator('#tile').screenshot()
    br.close()

im = Image.open(io.BytesIO(shot)).convert('RGB')
print('rendered', im.size)
for out, px in (('ico/apple-touch-icon.png', 180), ('ico/icon-512.png', 512)):
    im.resize((px, px), Image.BOX if im.width % px == 0 else Image.LANCZOS).save(
        ROOT / out, optimize=True)
    print(out, px, (ROOT / out).stat().st_size, 'B')
