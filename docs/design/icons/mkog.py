import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
# The mark is read from the repo's single source (svg/art-mark.svg, fill stripped).
A = {'logo_svg': open(os.path.join(REPO, 'svg', 'art-mark.svg')).read()}

def mark(fill, cls="mark"):
    s = A['logo_svg']
    s = s.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '').strip()
    s = re.sub(r'fill="#2f559d"', f'fill="{fill}"', s)
    if f'fill="{fill}"' not in s:
        s = s.replace('<svg ', f'<svg fill="{fill}" ', 1)
    s = s.replace('viewBox="0 0 534.98053 300"', 'viewBox="0 7.6 528.5 292.4"')
    s = s.replace('preserveAspectRatio="xMaxYMin meet"', '')
    s = s.replace('<svg ', f'<svg class="{cls}" ')
    return s

TOK = dict(page="#fefefe", ink="#0a0a0a", wash="#91acde", quiet="#6b6b6b",
           mark="#001f4e", link="#2f559d")

HTML = """<style>
%(fonts)s
html,body{margin:0;padding:0}
body{width:1200px;height:630px;background:%(page)s;overflow:hidden;
     font-family:'Inclusive Sans',system-ui,sans-serif}
.card{width:1200px;height:630px;box-sizing:border-box;
      padding:0 72px;display:flex;flex-direction:column;align-items:center;
      justify-content:center;text-align:center}
.markwrap{width:600px}
.mark{width:600px;height:auto;display:block}
.rule{width:88px;height:2px;background:%(quiet)s;margin:34px 0 30px}
.text{}
h1{font-family:'Urbanist',system-ui,sans-serif;font-weight:700;
   font-size:66px;line-height:1.05;letter-spacing:-.004em;margin:0;color:%(ink)s}
p{font-size:26px;line-height:1.45;margin:18px 0 0;color:%(quiet)s;white-space:nowrap}
</style>
<div class="card">
  <div class="markwrap">%(marksvg)s</div>
  <div class="rule"></div>
  <div class="text">
    <h1>Astrostat@UofT</h1>
    <p>Astrostatistics Research Team &middot; University of Toronto</p>
  </div>
</div>
"""

fonts = open('fonts.css').read()
d = dict(TOK); d.update(fonts=fonts, marksvg=mark(TOK["mark"]));
out = HTML % d
open('og-image.html', 'w').write(out)
