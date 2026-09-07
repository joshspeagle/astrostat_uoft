import icons, os
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [("ink, light page", "#fefefe", "#0a0a0a"),
         ("link, light page", "#fefefe", "#2f559d"),
         ("mark, light page", "#fefefe", "#001f4e"),
         ("quiet, light page", "#fefefe", "#6b6b6b"),
         ("ink, dark page", "#0a0a0a", "#fefefe"),
         ("link, dark page", "#0a0a0a", "#91acde"),
         ("mark, dark page", "#0a0a0a", "#70a9ff"),
         ("quiet, dark page", "#0a0a0a", "#9b9b9b")]
rows = []
for name, bg, fg in CASES:
    ics = ''.join(f'<svg width="24" height="24"><use href="#icon-{s}"/></svg>'
                  for s, _, _ in icons.ICONS)
    rows.append(f'<div class="case" style="background:{bg};color:{fg}">'
                f'<span class="n">{name}</span>{ics}</div>')
html = f'''<!doctype html><meta charset="utf-8">
<title>ART theme sprite &mdash; currentColor test</title>
<style>
body{{font:14px/1.5 system-ui,sans-serif;margin:0;padding:24px;background:#f4f4f4}}
h1{{font-size:16px;margin:0 0 4px}}
p{{margin:0 0 20px;color:#555;max-width:60ch}}
.case{{display:flex;align-items:center;gap:16px;padding:12px 16px}}
.case .n{{width:150px;font-size:12px;opacity:.75}}
svg{{display:block}}
code{{background:#e6e6e6;padding:1px 4px}}
</style>
<h1>themes-sprite.svg &mdash; <code>currentColor</code> inheritance</h1>
<p>The sprite is inlined once at the top of the document; every glyph below is a
<code>&lt;use href="#icon-&hellip;"&gt;</code>. Nothing sets a colour on the glyphs &mdash; each row
sets <code>color</code> on its container, and the strokes follow it. If a row is
invisible or black, inheritance is broken.</p>
{icons.sprite()}
{''.join(rows)}
'''
open(os.path.join(HERE, 'sprite-test.html'), 'w').write(html)
