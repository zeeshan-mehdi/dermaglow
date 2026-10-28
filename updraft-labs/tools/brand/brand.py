"""Updraft Labs brand geometry: the Lift mark and outlined wordmarks."""
import math, functools, os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    "geist": os.path.join(HERE, "fonts", "Geist[wght].ttf"),
    "serif-italic": os.path.join(HERE, "fonts", "InstrumentSerif-Italic.ttf"),
}

# ---------------------------------------------------------------- the mark
# v2. A U sliced in two. The left half (drag) stays put; the right half (lift)
# has risen. Arm tops sit on one rising line (slope 2:5) and the slice is cut
# at right angles to it, so every straight edge shares one of two directions.
CX, CY, R, r = 60.0, 72.0, 36.0, 16.0
SLOPE = -0.4            # rising line: y falls 2 for every 5 across
Y0 = 42.0               # rising line height at the left arm's outer edge
LIFT = 16.0             # how far the right half has risen (4/9 of R)
GAP = 7.0               # visible gap between the halves after the lift
CUT_DEG = -math.degrees(math.atan(abs(SLOPE)))  # slice is square to the rising line


def mark_paths(gap=GAP, lift=LIFT, y0=Y0, slope=SLOPE, cut_deg=None, R=R, r=r):
    """Return (left_d, right_d, bbox). `gap` is the visible gap after the lift."""
    if cut_deg is None:
        cut_deg = -math.degrees(math.atan(abs(slope)))
    a = math.radians(cut_deg)
    d = (math.sin(a), -math.cos(a))   # along the slice, pointing up
    n = (math.cos(a), math.sin(a))    # across the slice
    # a vertical lift also moves the right half across the slice; compensate
    g = gap - lift * abs(math.sin(a))
    xl0, xl1, xr0, xr1 = CX - R, CX - r, CX + r, CX + R
    px, py = CX, CY + (R + r) / 2      # slice passes mid-thickness at the bottom

    def top(x):
        return y0 + slope * (x - xl0)

    def hit(rad, off):
        qx, qy = px + n[0] * off - CX, py + n[1] * off - CY
        b = 2 * (qx * d[0] + qy * d[1])
        c = qx * qx + qy * qy - rad * rad
        disc = math.sqrt(b * b - 4 * c)
        pts = [(CX + qx + t * d[0], CY + qy + t * d[1]) for t in ((-b + disc) / 2, (-b - disc) / 2)]
        return max((p for p in pts if p[1] >= CY), key=lambda p: p[1])

    lo, li, ro, ri = hit(R, -g / 2), hit(r, -g / 2), hit(R, g / 2), hit(r, g / 2)
    f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
    left = (f"M{f(xl0)} {f(top(xl0))} L{f(xl1)} {f(top(xl1))} L{f(xl1)} {f(CY)} "
            f"A{f(r)} {f(r)} 0 0 0 {f(li[0])} {f(li[1])} L{f(lo[0])} {f(lo[1])} "
            f"A{f(R)} {f(R)} 0 0 1 {f(xl0)} {f(CY)} Z")
    P = lambda x, y: f"{f(x)} {f(y - lift)}"
    right = (f"M{P(*ri)} A{f(r)} {f(r)} 0 0 0 {P(xr0, CY)} L{P(xr0, top(xr0))} "
             f"L{P(xr1, top(xr1))} L{P(xr1, CY)} A{f(R)} {f(R)} 0 0 1 {P(*ro)} Z")
    return left, right, (xl0, top(xr1) - lift, xr1, max(lo[1], CY + R))


# ---------------------------------------------------------------- type
@functools.lru_cache(None)
def _font(key, wght):
    path = FONTS[key]
    tt = TTFont(path)
    if "fvar" in tt:
        tt = instancer.instantiateVariableFont(tt, {"wght": wght})
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    if "fvar" in TTFont(path):
        font.set_variations({"wght": wght})
    return tt, font


def text_path(key, text, size, wght=400, tracking=0.0, x=0.0, baseline=0.0):
    """Return (svg path d, advance width, (xmin, ymin, xmax, ymax)) for text set
    at `size` px with harfbuzz shaping (kerning) and `tracking` in em."""
    tt, font = _font(key, wght)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = size / upem
    pen = SVGPathPen(gs)
    bpen = BoundsPen(gs)
    pen_x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        ox = x + (pen_x + pos.x_offset) * s
        oy = baseline - pos.y_offset * s
        t = (s, 0, 0, -s, ox, oy)
        gs[name].draw(TransformPen(pen, t))
        gs[name].draw(TransformPen(bpen, t))
        pen_x += pos.x_advance + tracking * upem
    adv = (pen_x - tracking * upem) * s
    return pen.getCommands(), adv, bpen.bounds


def cap_height(key, wght=400):
    tt, _ = _font(key, wght)
    os2 = tt["OS/2"]
    return getattr(os2, "sCapHeight", 700) / tt["head"].unitsPerEm
