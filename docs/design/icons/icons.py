"""The eight ART research-theme glyphs, v2 + judge fixes.

Rules, stated once and never repeated inside a glyph:
  viewBox 0 0 24 24 . stroke currentColor . stroke-width 2 . round caps + joins
  fill none everywhere . geometry on a 0.5 grid . ink inset ~2 from the box.

Two measured constraints drive the fixed geometry:
  * no closed counter narrower than 3 units survives 15px at stroke 2, so no open
    circle below r2.5 and no ellipse minor radius below 2.5;
  * every glyph's painted ink bbox is centred on (12, 12) +/- 0.25.
"""
import math
import geom

STROKE_W = 2

# ---- dark-matter halo -------------------------------------------------------
# five LONG arcs on r=8.5. Cap-corrected: round caps add 1 unit at each end, so a
# 4.5 dash paints 6.5. The offset puts a GAP at 12 o'clock, so the ring has no
# four-fold symmetry and cannot be read as a brightness control or a spinner.
_R_HALO = 8.5
_N_DASH = 5
_PERIOD = 2 * math.pi * _R_HALO / _N_DASH        # 10.681
_PAINTED_DASH = 6.5
_DASH = _PAINTED_DASH - STROKE_W                 # 4.5
_GAP = _PERIOD - _DASH                           # 6.181
_TOP = _R_HALO * 1.5 * math.pi                   # arc length from 3 o'clock to 12
_OFF = (_DASH + _GAP / 2 - _TOP) % _PERIOD
_HALO = (f'stroke-dasharray="{_DASH:.3f} {_GAP:.3f}" '
         f'stroke-dashoffset="{_OFF:.3f}"')

# ---- star-formation cloud ---------------------------------------------------
# three lobes of UNEQUAL radius on a ring, so the silhouette is a cloud and not a
# trefoil. The centre is solved for, so the painted ink bbox lands on (12, 12).
_CLOUD_KW = dict(d=3.75, radii=(4.0, 5.0, 5.25))


def _cloud():
    x0, x1, y0, y1 = geom.cloud_extent(cx=12.0, cy=12.0, **_CLOUD_KW)
    dx, dy = 12 - (x0 + x1) / 2, 12 - (y0 + y1) / 2
    d, _, _ = geom.cloud_path(cx=12.0 + dx, cy=12.0 + dy, **_CLOUD_KW)
    return d, 12.0 + dx, 12.0 + dy


_CLOUD_D, _CLOUD_CX, _CLOUD_CY = _cloud()

ICONS = [
    # a bell whose tails LAND on the axis, so curve and axis are one figure, and
    # a mode tick running up from the axis to the foot of the apex.
    ("inference", "Inference", """
  <path d="M 3.5 18.5 H 20.5"/>
  <path d="M 3.5 18.5 C 8.5 18.5 9.5 5.5 12 5.5 C 14.5 5.5 15.5 18.5 20.5 18.5"/>
  <path d="M 12 18.5 V 15.5"/>"""),

    # small circle -> arrow -> large circle, on the diagonal. Both counters are
    # r2.5+, the head is 2.5 against a 7.07 shaft, and the tip closes on the ring.
    ("stellar-evolution", "Stellar Evolution", """
  <circle cx="5.5" cy="18.5" r="2.5"/>
  <path d="M 8.5 15.5 L 13.5 10.5"/>
  <path d="M 11 10.5 H 13.5 V 13"/>
  <circle cx="17.5" cy="6.5" r="3.5"/>"""),

    ("dark-matter-and-cosmology", "Dark Matter &amp; Cosmology", f"""
  <circle cx="12" cy="12" r="{_R_HALO:g}" {_HALO}/>
  <ellipse cx="12" cy="12" rx="2.5" ry="3.5"/>"""),

    # hub and three satellites, all three on one radius (9.19) and every spoke
    # collinear with hub-centre -> node-centre. Counters r3 / r2.5.
    ("ai-for-scientists", "AI for Scientists", """
  <circle cx="12" cy="12" r="3"/>
  <circle cx="5.5" cy="5.5" r="2.5"/>
  <circle cx="18.5" cy="5.5" r="2.5"/>
  <circle cx="5.5" cy="18.5" r="2.5"/>
  <path d="M 9 9 L 8 8"/>
  <path d="M 15 9 L 16 8"/>
  <path d="M 9 15 L 8 16"/>"""),

    # an edge-on disc, one outline: tapered to nothing at both ends, with a boxy
    # central bulge. No inner circle -- a lens with a round form inside it is an
    # eye, and a lens that comes to a point top and bottom is the brand sparkle.
    ("the-milky-way", "The Milky Way", """
  <path d="M 3.5 12 C 7 11.6 7.5 5.5 12 5.5 C 16.5 5.5 17 11.6 20.5 12 C 17 12.4 16.5 18.5 12 18.5 C 7.5 18.5 7 12.4 3.5 12 Z"/>"""),

    ("galaxies", "Galaxies", """
  <ellipse cx="9.5" cy="15" rx="6.5" ry="4" transform="rotate(-20 9.5 15)"/>
  <ellipse cx="18" cy="8" rx="4" ry="2.5" transform="rotate(-55 18 8)"/>"""),

    ("transients", "Transients", """
  <path d="M 3.5 20 H 8.5 L 11.5 4 C 13.5 12 15.5 19 21 19.5"/>"""),

    ("star-formation", "Star Formation", f"""
  <path d="{_CLOUD_D}"/>
  <circle cx="{_CLOUD_CX:g}" cy="{_CLOUD_CY:g}" r="2.5"/>"""),
]

# points that must stay OPEN (light) at every shipping size: the centre of every
# closed counter in the set. measure.py probes each one at 15px and 24px.
COUNTERS = {
    "stellar-evolution": [(5.5, 18.5), (17.5, 6.5)],
    "dark-matter-and-cosmology": [(12, 12)],
    "the-milky-way": [(12, 12)],
    "ai-for-scientists": [(12, 12), (5.5, 5.5), (18.5, 5.5), (5.5, 18.5)],
    "galaxies": [(9.5, 15), (18, 8)],
    "star-formation": [(_CLOUD_CX, _CLOUD_CY)],
}

SET_ATTRS = ('fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"')


def standalone(slug, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="24" height="24" {SET_ATTRS} role="img" '
            f'aria-label="{label}">{body}\n</svg>\n')


def sprite():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" style="display:none" '
             'aria-hidden="true">']
    for slug, label, body in ICONS:
        parts.append(f'  <symbol id="icon-{slug}" viewBox="0 0 24 24" '
                     f'{SET_ATTRS}>')
        parts.append('  ' + body.strip('\n').replace('\n', '\n  '))
        parts.append('  </symbol>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'
