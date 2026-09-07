"""Measure the icon set instead of judging it.

For every glyph: painted ink coverage (share of the 24x24 box), the centre of the
painted ink bbox in 24-grid units, and the lightness of every closed counter at
the two shipping sizes. Run by build.py; `python3 measure.py` on its own too.
"""
import asyncio, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icons                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIG = 240                    # 10x the grid: the geometry measurement
SMALL = [15, 24]             # the sizes the site actually ships
PAD = 20


def _html():
    o = ['<!doctype html><meta charset="utf-8"><style>',
         'html,body{margin:0;padding:0;background:#fff;color:#000}',
         '.cell{position:absolute;background:#fff}', '</style>', icons.sprite()]
    y = 0
    pos = {}
    for slug, _, _ in icons.ICONS:
        pos[slug] = {}
        o.append(f'<svg class="cell" style="left:0px;top:{y}px" width="{BIG}" '
                 f'height="{BIG}"><use href="#icon-{slug}"/></svg>')
        pos[slug][BIG] = (0, y)
        x = BIG + PAD
        for s in SMALL:
            o.append(f'<svg class="cell" style="left:{x}px;top:{y}px" width="{s}" '
                     f'height="{s}"><use href="#icon-{slug}"/></svg>')
            pos[slug][s] = (x, y)
            x += s + PAD
        y += BIG + PAD
    return '\n'.join(o), pos, y


async def _shoot(path, w, h):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = await b.new_page(viewport={"width": w, "height": h},
                              device_scale_factor=1)
        await pg.goto("file://" + path)
        await pg.wait_for_timeout(400)
        shot = await pg.screenshot(full_page=True)
        await b.close()
    return shot


def run(verbose=True):
    html, pos, total_h = _html()
    hp = os.path.join(HERE, '_measure.html')
    open(hp, 'w').write(html)
    png = os.path.join(HERE, '_measure.png')
    open(png, 'wb').write(asyncio.run(_shoot(hp, BIG + 2 * PAD + sum(SMALL) + 40,
                                             total_h + 20)))
    im = Image.open(png).convert('L')
    rows = []
    for slug, _, _ in icons.ICONS:
        x, y = pos[slug][BIG]
        big = im.crop((x, y, x + BIG, y + BIG))
        px = big.load()
        ink = 0
        xs, ys = [], []
        for j in range(BIG):
            for i in range(BIG):
                if px[i, j] < 128:
                    ink += 1
                    xs.append(i)
                    ys.append(j)
        u = BIG / 24.0
        cov = 100.0 * ink / (BIG * BIG)
        cx = ((min(xs) + max(xs) + 1) / 2) / u
        cy = ((min(ys) + max(ys) + 1) / 2) / u
        w = (max(xs) + 1 - min(xs)) / u
        h = (max(ys) + 1 - min(ys)) / u
        inset = min(min(xs), min(ys), BIG - 1 - max(xs), BIG - 1 - max(ys)) / u
        counters = {}
        for s in SMALL:
            worst = 255
            for (gx, gy) in icons.COUNTERS.get(slug, []):
                ox, oy = pos[slug][s]
                q = im.crop((ox, oy, ox + s, oy + s)).load()
                i = min(max(int(gx * s / 24.0), 0), s - 1)
                j = min(max(int(gy * s / 24.0), 0), s - 1)
                best = max(q[min(i + di, s - 1), min(j + dj, s - 1)]
                           for di in (0, -1) for dj in (0, -1))
                worst = min(worst, best)
            counters[s] = worst if icons.COUNTERS.get(slug) else None
        rows.append(dict(slug=slug, cov=cov, cx=cx, cy=cy, w=w, h=h,
                         inset=inset, counters=counters))
    if verbose:
        print(f"{'glyph':24} {'ink%':>6} {'cx':>6} {'cy':>6} {'w':>5} {'h':>5} "
              f"{'inset':>5} {'c@15':>5} {'c@24':>5}")
        for r in rows:
            c15 = r['counters'][15]
            c24 = r['counters'][24]
            print(f"{r['slug']:24} {r['cov']:6.2f} {r['cx']:6.2f} {r['cy']:6.2f} "
                  f"{r['w']:5.1f} {r['h']:5.1f} {r['inset']:5.2f} "
                  f"{'-' if c15 is None else c15:>5} {'-' if c24 is None else c24:>5}")
        cs = [r['cov'] for r in rows]
        print(f"coverage {min(cs):.2f}-{max(cs):.2f}%  spread {max(cs)/min(cs):.2f}x  "
              f"| ink centre cy {min(r['cy'] for r in rows):.2f}-"
              f"{max(r['cy'] for r in rows):.2f}")
    os.remove(hp)
    os.remove(png)
    return rows


if __name__ == '__main__':
    run()
