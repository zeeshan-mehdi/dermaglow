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
# A U cut in two. The left half (drag) stays put; the right half (lift) has
# risen. Arm tops are cut along one rising line.
CX, CY, R, r = 60.0, 72.0, 36.0, 16.0


def mark_paths(gap=4.0, lift=14.0, y0=50.0, slope=-0.5, aligned=False):
    def top(x):
        return y0 + slope * (x - 24)

    hx = gap / 2
    ox = CX - hx
    oy = CY + math.sqrt(R * R - (ox - CX) ** 2)
    iy = CY + math.sqrt(r * r - (ox - CX) ** 2)
    left = (f"M24 {top(24):.3f} L44 {top(44):.3f} L44 {CY} A{r} {r} 0 0 0 {ox:.3f} {iy:.3f} "
            f"L{ox:.3f} {oy:.3f} A{R} {R} 0 0 1 24 {CY} Z")
    ox2 = CX + hx
    oy2 = CY + math.sqrt(R * R - (ox2 - CX) ** 2) - lift
    iy2 = CY + math.sqrt(r * r - (ox2 - CX) ** 2) - lift
    cy = CY - lift
    t76, t96 = (top(76), top(96)) if aligned else (top(76) - lift, top(96) - lift)
    right = (f"M{ox2:.3f} {iy2:.3f} A{r} {r} 0 0 0 76 {cy} L76 {t76:.3f} L96 {t96:.3f} "
             f"L96 {cy} A{R} {R} 0 0 1 {ox2:.3f} {oy2:.3f} Z")
    # bounds
    ys = [top(24), CY + R, t96]
    return left, right, (24.0, min(ys), 96.0, CY + R)


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
