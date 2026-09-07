import base64, os
import icons

HERE = os.path.dirname(os.path.abspath(__file__))
b64 = lambda n: base64.b64encode(open(os.path.join(HERE, n), 'rb').read()).decode()
img = lambda n: "data:image/png;base64," + b64(n)

SIZES = [15, 24, 32, 48]
SPRITE = icons.sprite()
FONTS = open(os.path.join(HERE, 'fonts.css')).read()

TOK = {
    'light': dict(page='#fefefe', ink='#0a0a0a', quiet='#6b6b6b', mark='#001f4e',
                  card='#eeeeee', fav='favicon-16.png', fav32='favicon-32.png'),
    'dark':  dict(page='#0a0a0a', ink='#fefefe', quiet='#9b9b9b', mark='#70a9ff',
                  card='#333333', fav='favicon-16-dark.png', fav32='favicon-32-dark.png'),
}


def panel(theme):
    t = TOK[theme]
    o = [f'<section class="panel {theme}">']
    o.append(f'<h1 class="ttl">{theme}</h1>')

    # --- grid of sizes -------------------------------------------------
    o.append('<div class="lbl">the eight themes at 15 / 24 / 32 / 48</div>')
    o.append('<table class="grid"><thead><tr><th></th>' +
             ''.join(f'<th>{s}</th>' for s in SIZES) + '</tr></thead><tbody>')
    for slug, label, _ in icons.ICONS:
        cells = ''.join(
            f'<td><svg class="ic" width="{s}" height="{s}"><use href="#icon-{slug}"/></svg></td>'
            for s in SIZES)
        o.append(f'<tr><th class="slug">{slug}</th>{cells}</tr>')
    o.append('</tbody></table>')

    # --- 15px strip, tight ---------------------------------------------
    o.append('<div class="lbl">15px, in a row &mdash; can you tell them apart?</div>')
    o.append('<div class="strip">' + ''.join(
        f'<svg class="ic" width="15" height="15"><use href="#icon-{s}"/></svg>'
        for s, _, _ in icons.ICONS) + '</div>')

    # --- beside the name ------------------------------------------------
    o.append('<div class="lbl">beside the theme name, h2</div>')
    for slug, label, _ in icons.ICONS:
        o.append(f'<div class="h2row"><svg class="ic" width="32" height="32">'
                 f'<use href="#icon-{slug}"/></svg><span>{label}</span></div>')

    # --- favicon --------------------------------------------------------
    o.append('<div class="lbl">favicon &mdash; the brand particle</div>')
    o.append('<div class="favrow">')
    for f, n, mag in ((t['fav'], 16, 8), (t['fav32'], 32, 8)):
        o.append(f'<figure><img class="px" src="{img(f)}" width="{n*mag}" '
                 f'height="{n*mag}"><figcaption>{n}px &times;{mag}</figcaption></figure>')
    o.append(f'<figure><img src="{img(t["fav"])}" width="16" height="16">'
             f'<figcaption>16</figcaption></figure>')
    o.append(f'<figure><img src="{img(t["fav32"])}" width="32" height="32">'
             f'<figcaption>32</figcaption></figure>')
    o.append(f'<figure class="svgfav"><div class="svgbox">{open(os.path.join(HERE,"favicon.svg")).read()}</div>'
             f'<figcaption>svg 96{" &mdash; light branch" if theme == "dark" else ""}</figcaption></figure>')
    o.append('</div>')

    o.append('<div class="lbl">app icons</div>')
    o.append('<div class="favrow">'
             f'<figure><img src="{img("apple-touch-icon.png")}" width="120" height="120">'
             '<figcaption>apple-touch 180</figcaption></figure>'
             f'<figure><img src="{img("icon-192.png")}" width="120" height="120">'
             '<figcaption>icon 192</figcaption></figure>'
             f'<figure><img src="{img("icon-512.png")}" width="120" height="120">'
             '<figcaption>icon 512</figcaption></figure>'
             '</div>')
    o.append('</section>')
    return '\n'.join(o)


CSS = """
%(fonts)s
*{box-sizing:border-box}
html,body{margin:0;padding:0;font-family:'Inclusive Sans',system-ui,sans-serif}
body{background:#fff}
.sheet{display:flex;width:1360px}
.panel{width:680px;padding:34px 40px 48px}
.light{background:#fefefe;color:#0a0a0a}
.dark{background:#0a0a0a;color:#fefefe}
.ttl{font-family:'Urbanist';font-weight:700;font-size:26px;margin:0 0 26px}
.lbl{font-size:11px;letter-spacing:.11em;text-transform:uppercase;
     margin:34px 0 12px;opacity:.62}
.panel .lbl:first-of-type{margin-top:0}
table.grid{border-collapse:collapse;width:100%%}
table.grid th{font-weight:400;font-size:11px;opacity:.62;padding:0 0 8px}
table.grid td{text-align:center;padding:9px 0;width:88px}
th.slug{text-align:left;font-size:12px;opacity:.85;font-weight:400}
.ic{color:inherit;display:inline-block;vertical-align:middle}
.strip{display:flex;gap:26px;align-items:center;padding:6px 0}
.h2row{display:flex;align-items:center;gap:14px;margin:6px 0 10px}
.h2row span{font-family:'Urbanist';font-weight:700;font-size:32px;line-height:1.2}
.favrow{display:flex;gap:28px;align-items:flex-end;flex-wrap:wrap}
figure{margin:0;text-align:center}
figcaption{font-size:10px;letter-spacing:.09em;text-transform:uppercase;
           opacity:.6;margin-top:8px}
img.px{image-rendering:pixelated}
.svgbox{width:96px;height:96px}
.svgbox svg{width:96px;height:96px}
.og{padding:40px;background:#f4f4f4;text-align:center}
.og img{width:600px;height:315px;display:block;margin:0 auto;
        outline:1px solid #d5d5d5}
.og .cap{font-size:11px;letter-spacing:.11em;text-transform:uppercase;
         color:#6b6b6b;margin-bottom:14px}
"""


def build():
    html = ['<!doctype html><meta charset="utf-8"><title>ART icons v2 &mdash; contact sheet</title>',
            '<style>' + CSS % dict(fonts=FONTS) + '</style>', SPRITE,
            '<div class="sheet">', panel('light'), panel('dark'), '</div>',
            '<div class="og"><div class="cap">og-image.png &mdash; 1200&times;630, shown at half size</div>'
            f'<img src="{img("og-image.png")}"></div>']
    open(os.path.join(HERE, 'sheet.html'), 'w').write('\n'.join(html))


if __name__ == '__main__':
    build()
