"""Shared geometry for the ART icon family (v2, judge fixes applied)."""
import math

f = lambda v: f"{v:.3f}".rstrip('0').rstrip('.')


# ---------------------------------------------------------------- star-formation
def cloud_path(cx=12.0, cy=12.0, d=4.0, radii=(4.25, 4.75, 5.0),
               angles=(-90, 30, 150)):
    """Outline of the union of three circles of *unequal* radius on a ring.

    Unequal radii are what stop the three lobes reading as a trefoil; the ring
    radius `d` against the lobe radii sets how deep the valleys cut.
    """
    C = [(cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a)))
         for a in angles]

    def outer_isect(i, j):
        (x1, y1), (x2, y2) = C[i], C[j]
        ri, rj = radii[i], radii[j]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        a = (dist * dist + ri * ri - rj * rj) / (2 * dist)
        h = math.sqrt(max(ri * ri - a * a, 0.0))
        ux, uy = dx / dist, dy / dist
        mx, my = x1 + a * ux, y1 + a * uy
        p = (mx - uy * h, my + ux * h)
        q = (mx + uy * h, my - ux * h)
        return p if math.hypot(p[0] - cx, p[1] - cy) > math.hypot(q[0] - cx, q[1] - cy) else q

    V = [outer_isect(i, (i + 1) % 3) for i in range(3)]   # V[i] lies on lobes i and i+1

    seg = [f"M {f(V[0][0])} {f(V[0][1])}"]
    for i in range(3):
        k = (i + 1) % 3                       # the lobe both valleys sit on
        v0, v1 = V[i], V[k]
        a0 = math.atan2(v0[1] - C[k][1], v0[0] - C[k][0])
        a1 = math.atan2(v1[1] - C[k][1], v1[0] - C[k][0])
        sweep = (a1 - a0) % (2 * math.pi)     # sweep=1 is increasing angle (y down)
        large = 1 if sweep > math.pi else 0
        seg.append(f"A {f(radii[k])} {f(radii[k])} 0 {large} 1 {f(v1[0])} {f(v1[1])}")
    seg.append("Z")
    return " ".join(seg), C, V


def cloud_extent(**kw):
    """(xmin, xmax, ymin, ymax) of the cloud outline centreline."""
    _, C, _ = cloud_path(**kw)
    radii = kw.get('radii', (4.25, 4.75, 5.0))
    xs = [c[0] - r for c, r in zip(C, radii)] + [c[0] + r for c, r in zip(C, radii)]
    ys = [c[1] - r for c, r in zip(C, radii)] + [c[1] + r for c, r in zip(C, radii)]
    return min(xs), max(xs), min(ys), max(ys)


# ---------------------------------------------------------------- brand particle
def particle_points(cx, cy, R, tip=0.0, thick=1.15, steps=10, shoulder=0.3112):
    """Four-pointed sparkle as a flat point list (polygon-ready).

    R      arm reach from centre (equal on both axes)
    tip    half-width of the flat at each tip (0 = a true point)
    thick  arm thickening factor over the v1 particle
    """
    a = 0.2389 * thick * R      # half-width of the arm at depth b
    b = shoulder * R            # depth (from centre) at which the arm reaches a
    # solve: tip(0,-R) -> (-a,-b) extended meets left(-R,0) -> (-b,-a) extended
    t = R / ((R - b) + a)
    s = a * t                   # the flanks meet at (-s,-s) from centre

    def q(x, y, k):
        """rotate (x,y) by k*90 degrees clockwise (svg coords)"""
        for _ in range(k):
            x, y = -y, x
        return (cx + x, cy + y)

    def quad_bezier(p0, pc, p1, n=steps):
        out = []
        for i in range(1, n + 1):
            u = i / n
            m = 1 - u
            out.append((m * m * p0[0] + 2 * m * u * pc[0] + u * u * p1[0],
                        m * m * p0[1] + 2 * m * u * pc[1] + u * u * p1[1]))
        return out

    pts = []
    for k in range(4):
        # top tip, then down the right flank of the top arm into the corner,
        # then out along the top flank of the right arm to the right tip
        pts.append(q(-tip, -R, k))
        pts.append(q(tip, -R, k))
        p0 = q(a, -b, k)
        pc = q(s, -s, k)
        p1 = q(b, -a, k)
        pts.append(p0)
        pts.extend(quad_bezier(p0, pc, p1))
    return pts


def particle_svg_path(cx, cy, R, tip=0.0, thick=1.15, prec=3, shoulder=0.3112):
    a = 0.2389 * thick * R
    b = shoulder * R
    t = R / ((R - b) + a)
    s = a * t

    def q(x, y, k):
        for _ in range(k):
            x, y = -y, x
        return (cx + x, cy + y)

    g = lambda v: f"{v:.{prec}f}".rstrip('0').rstrip('.')
    d = []
    for k in range(4):
        p_tip_l = q(-tip, -R, k)
        p_tip_r = q(tip, -R, k)
        p0 = q(a, -b, k)
        pc = q(s, -s, k)
        p1 = q(b, -a, k)
        d.append(("M " if k == 0 else "L ") + f"{g(p_tip_l[0])} {g(p_tip_l[1])}")
        if tip:
            d.append(f"L {g(p_tip_r[0])} {g(p_tip_r[1])}")
        d.append(f"L {g(p0[0])} {g(p0[1])}")
        d.append(f"Q {g(pc[0])} {g(pc[1])} {g(p1[0])} {g(p1[1])}")
    d.append("Z")
    return " ".join(d)
