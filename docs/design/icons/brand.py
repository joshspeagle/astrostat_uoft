"""Favicon / identity rasters built from the brand particle.

Three things here are load-bearing and each is asserted, not asserted-by-eye:

  * the polygon is shrunk by half a supersample pixel before it is drawn.
    ImageDraw.polygon fills inclusive of the far edge, so without this the
    shape is one supersample pixel oversize and the raster carries a 6%-alpha
    fringe on the right and bottom only. build_favicons() asserts that both
    rasters are identical to their own horizontal and vertical mirror.
  * favicon.ico embeds the hand-aligned 16 as its own frame
    (append_images), instead of letting Pillow resample the 32 down to 16.
    build_favicons() extracts the 16 frame back out and asserts it is
    byte-identical to favicon-16.png.
  * the dark rasters ship. #001f4e on Chrome's dark tab strip (#202124) is a
    contrast ratio of 1.00 -- invisible -- and prefers-color-scheme inside a
    favicon SVG is not honoured by Chromium, so the dark PNGs are linked with
    a media query. See the head snippet in NOTES.md.
"""
import os
from PIL import Image, ImageChops, ImageDraw
import geom

MARK_LIGHT = "#001f4e"
MARK_DARK = "#70a9ff"
PAGE_LIGHT = "#fefefe"
SS = 16  # supersample factor; BOX downsampling keeps integer edges exact


def favicon_svg(path):
    d = geom.particle_svg_path(12, 12, 10.5, tip=0.0, thick=1.15, shoulder=0.36)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" \
width="24" height="24" role="img" aria-label="ART">
  <style>
    .particle {{ fill: {MARK_LIGHT}; }}
    @media (prefers-color-scheme: dark) {{ .particle {{ fill: {MARK_DARK}; }} }}
  </style>
  <path class="particle" d="{d}"/>
</svg>
'''
    open(path, "w").write(svg)
    return d


def render_particle(size, R, tip, fg, bg, centre=None, thick=1.15, shoulder=0.3112):
    """Rasterise the particle at `size` px, area-averaged from a 16x draw.

    Vertices land on whole pixels, so the four arm tips and the axes stay
    crisp; only the concave diagonal flanks are antialiased. The point set is
    scaled in by half a supersample pixel first -- see the module docstring.
    """
    cx, cy = centre or (size / 2, size / 2)
    pts = geom.particle_points(cx, cy, R, tip=tip, thick=thick, steps=24,
                               shoulder=shoulder)
    k = (R * SS - 0.5) / (R * SS)
    pts = [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]
    big = Image.new("RGBA", (size * SS, size * SS), bg)
    ImageDraw.Draw(big).polygon([(x * SS, y * SS) for x, y in pts], fill=fg)
    return big.resize((size, size), Image.BOX)


def assert_symmetric(im, what):
    a = im.split()[3] if im.mode == "RGBA" else im.convert("L")
    for name, op in (("horizontal", Image.FLIP_LEFT_RIGHT),
                     ("vertical", Image.FLIP_TOP_BOTTOM)):
        diff = ImageChops.difference(a, a.transpose(op)).getbbox()
        assert diff is None, f"{what}: not {name}ly symmetric ({diff})"


def profile(im, thresh=128):
    """Painted width, row by row, at >= 50% alpha. The 16px hinting check."""
    a = (im.split()[3] if im.mode == "RGBA" else im.convert("L")).load()
    w, h = im.size
    return [sum(1 for i in range(w) if a[i, j] >= thresh) for j in range(h)]


def build(outdir):
    p = lambda n: os.path.join(outdir, n)
    d = favicon_svg(p("favicon.svg"))

    # 16 and 32: hand-aligned. Centre on a pixel boundary, arm tips 2px wide
    # and landing on integer rows/columns.
    mk = lambda size, R, sh, fg: render_particle(size, R=R, tip=1.0, shoulder=sh,
                                                 fg=fg, bg=(0, 0, 0, 0))
    f16 = mk(16, 7.0, 0.55, MARK_LIGHT)
    f32 = mk(32, 15.0, 0.40, MARK_LIGHT)
    assert_symmetric(f16, "favicon-16")
    assert_symmetric(f32, "favicon-32")
    assert f16.split()[3].getbbox() == (1, 1, 15, 15), f16.split()[3].getbbox()
    assert f32.split()[3].getbbox() == (1, 1, 31, 31), f32.split()[3].getbbox()
    f16.save(p("favicon-16.png"))
    f32.save(p("favicon-32.png"))

    # dark-theme twins. These SHIP -- see the module docstring.
    d16 = mk(16, 7.0, 0.55, MARK_DARK)
    d32 = mk(32, 15.0, 0.40, MARK_DARK)
    assert_symmetric(d16, "favicon-16-dark")
    assert_symmetric(d32, "favicon-32-dark")
    d16.save(p("favicon-16-dark.png"))
    d32.save(p("favicon-32-dark.png"))

    # .ico: embed BOTH hand-aligned rasters as their own frames. `sizes` lists
    # the entries to write and `append_images` supplies the bitmap for any size
    # it matches; without append_images Pillow resamples the 32 down to 16, and
    # without 16 in `sizes` the 16 entry is simply not written at all.
    f32.save(p("favicon.ico"), sizes=[(16, 16), (32, 32)], append_images=[f16])
    ico = Image.open(p("favicon.ico"))
    assert sorted(ico.ico.sizes()) == [(16, 16), (32, 32)], ico.ico.sizes()
    for size, want in (((16, 16), f16), ((32, 32), f32)):
        got = ico.ico.getimage(size).convert("RGBA")
        assert ImageChops.difference(got, want).getbbox() is None, \
            f"favicon.ico's {size[0]}x{size[0]} frame is not the hand-aligned raster"

    # knocked out of a solid mark square, 12% padding
    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"),
                       (512, "icon-512.png")):
        R = size * (1 - 2 * 0.12) / 2
        img = render_particle(size, R=R, tip=R * 0.045, shoulder=0.36,
                              fg=PAGE_LIGHT, bg=MARK_LIGHT)
        assert_symmetric(img, name)
        img.convert("RGB").save(p(name))

    print("favicon: 16px profile", profile(f16), "| 32px profile", profile(f32))
    print("favicon: .ico frames", sorted(ico.ico.sizes()), "| 16 frame == favicon-16.png")
    return d


if __name__ == "__main__":
    build(os.path.dirname(os.path.abspath(__file__)))
