"""Updraft Labs out in the world: production-ready artwork for physical pieces.

    python3 tools/brand/world.py public/brand/world

All text is outlined (no fonts needed by printers or embroiderers).
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import mark_paths, text_path, text_width, arc_text, cap_height, SLOPE

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
INK, PAPER, PAPER2, PAPER3 = "#121211", "#F2F0E9", "#E8E5DB", "#DDD9CC"
BLUE, MINT, TEAL, ORANGE = "#2443D6", "#86F5CF", "#0E9F79", "#FF5A1F"
ANGLE = math.degrees(math.atan(abs(SLOPE)))  # 21.8°, the logo's rising line

L, R, (bx0, by0, bx1, by1) = mark_paths()
MW, MH = bx1 - bx0, by1 - by0


def mark(x, y, h, left, right):
    s = h / MH
    return (f'<g transform="translate({x - bx0 * s:.2f} {y - by0 * s:.2f}) scale({s:.4f})">'
            f'<path d="{L}" fill="{left}"/><path d="{R}" fill="{right}"/></g>')


def mark_centered(cx, cy, h, left, right):
    w = MW * h / MH
    return mark(cx - w / 2, cy - h / 2, h, left, right)


def text(key, s, size, x, base, fill, wght=500, tracking=0.0, anchor="start", axes=None):
    w = text_width(key, s, size, wght, tracking, axes)
    x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
    d, _, _ = text_path(key, s, size, wght, tracking, x0, base, axes)
    return f'<path d="{d}" fill="{fill}"/>'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def save(name, w, h, body, title):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(svg(w, h, body, title))


# ------------------------------------------------------------- mission patch
def patch():
    S, c = 600, 300
    b = [f'<circle cx="{c}" cy="{c}" r="292" fill="{ORANGE}"/>',
         f'<circle cx="{c}" cy="{c}" r="292" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="3 5" opacity=".35"/>',
         f'<circle cx="{c}" cy="{c}" r="266" fill="{INK}"/>',
         f'<circle cx="{c}" cy="{c}" r="198" fill="{BLUE}"/>',
         f'<circle cx="{c}" cy="{c}" r="198" fill="none" stroke="{PAPER}" stroke-width="3"/>']
    b.append(f'<path d="{arc_text("mono", "UPDRAFT LABS · FLIGHT TEST", 27, c, c, 216, -90, 600, 0.12)}" fill="{PAPER}"/>')
    b.append(f'<path d="{arc_text("mono", "BOTTLENECK RESEARCH UNIT", 22, c, c, 244, 90, 500, 0.12, bottom=True)}" fill="{MINT}"/>')
    for ang in (180, 0):  # separator stars on the ring
        x, y = c + 231 * math.cos(math.radians(ang)), c + 231 * math.sin(math.radians(ang))
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{ORANGE}"/>')
    # drag lines low in the disc, lift lines rising to the right of the slice
    clip = f'<clipPath id="disc"><circle cx="{c}" cy="{c}" r="194"/></clipPath>'
    lines = []
    for i, y in enumerate(range(390, 470, 16)):
        xs = 300 + (y - 420) * 0.4
        lines.append(f'<line x1="100" y1="{y}" x2="{xs - 4:.1f}" y2="{y}" stroke="{PAPER}" stroke-width="3" stroke-dasharray="16 7" opacity=".55"/>')
        lines.append(f'<line x1="{xs + 4:.1f}" y1="{y - 22}" x2="500" y2="{y - 22}" stroke="{MINT}" stroke-width="4"/>')
    b.append(clip + f'<g clip-path="url(#disc)">{"".join(lines)}</g>')
    b.append(mark_centered(c, 262, 200, PAPER, MINT))
    save("updraft-patch.svg", S, S, "".join(b), "Updraft Labs mission patch")


# ------------------------------------------------------------- pilot wings
def wings():
    W, H, cx, cy = 1000, 440, 500, 232
    lengths = [372, 340, 304, 266, 226, 186]
    parts = []
    for side in (-1, 1):
        rot = -ANGLE * side            # wings rise at the logo's 2:5 angle
        g = []
        for k, ln in reversed(list(enumerate(lengths))):   # lower feathers first, upper ones overlap them
            y = cy - 62 + k * 21
            x0 = cx + side * 40
            tip = side * ln
            # broad feather with a pointed, swept tip
            d = (f"M{x0} {y} L{x0 + tip - side * 46} {y} Q{x0 + tip} {y} {x0 + tip} {y + 14} "
                 f"Q{x0 + tip - side * 10} {y + 30} {x0 + tip - side * 58} {y + 32} L{x0} {y + 32} Z")
            fill = INK if k % 2 == 0 else BLUE
            g.append(f'<path d="{d}" fill="{fill}" stroke="{PAPER}" stroke-width="4" stroke-linejoin="round"/>')
        parts.append(f'<g transform="rotate({rot:.2f} {cx} {cy})">{"".join(g)}</g>')
    b = ["".join(parts),
         f'<circle cx="{cx}" cy="{cy}" r="100" fill="{ORANGE}" stroke="{INK}" stroke-width="6"/>',
         f'<circle cx="{cx}" cy="{cy}" r="80" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>',
         mark_centered(cx, cy + 2, 108, "#2443D6", "#13C39A")]
    save("updraft-wings.svg", W, H, "".join(b), "Updraft Labs pilot wings pin")


# ------------------------------------------------------------- baggage tag
def bag_tag():
    W, H = 380, 920
    b = [f'<path d="M24 0 H356 a24 24 0 0 1 24 24 V896 a24 24 0 0 1 -24 24 H24 a24 24 0 0 1 -24 -24 V24 a24 24 0 0 1 24 -24z" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>',
         f'<rect x="0" y="120" width="{W}" height="62" fill="{ORANGE}"/>',
         f'<circle cx="190" cy="60" r="26" fill="none" stroke="{INK}" stroke-width="3"/><circle cx="190" cy="60" r="14" fill="{INK}" opacity=".08"/>',
         text("mono", "UPDRAFT LABS", 22, 190, 160, INK, 600, 0.16, "middle"),
         text("mono", "FROM", 16, 34, 236, INK, 500, 0.12),
         text("display", "DRG", 70, 34, 300, INK, 760),
         text("mono", "TO", 16, 346, 236, INK, 500, 0.12, "end"),
         text("display", "LFT", 70, 346, 300, BLUE, 760, anchor="end"),
         f'<line x1="34" y1="330" x2="346" y2="330" stroke="{INK}" stroke-width="2"/>',
         text("display", "LFT", 210, 190, 520, INK, 800, -0.02, "middle"),
         f'<line x1="34" y1="560" x2="346" y2="560" stroke="{INK}" stroke-width="2" stroke-dasharray="10 6"/>']
    rows = [("FLIGHT", "UL 001"), ("CLASS", "PARTNER"), ("SEQ", "0001")]
    for i, (k, v) in enumerate(rows):
        y = 600 + i * 46
        b.append(text("mono", k, 15, 34, y, INK, 500, 0.12))
        b.append(text("mono", v, 20, 346, y, INK, 600, 0.06, "end"))
    b.append(f'<rect x="0" y="736" width="{W}" height="44" fill="{MINT}"/>')
    b.append(text("mono", "PRIORITY · HANDLE WITH LIFT", 16, 190, 765, INK, 600, 0.12, "middle"))
    bars, x = [], 34
    widths = [3, 1, 2, 4, 1, 1, 3, 2, 1, 4, 2, 1, 3, 1, 2, 2, 4, 1, 3, 1, 1, 2, 4, 2, 1, 3, 1, 2]
    for i, wd in enumerate(widths):
        if i % 2 == 0:
            bars.append(f'<rect x="{x}" y="800" width="{wd * 3}" height="70" fill="{INK}"/>')
        x += wd * 3 + 2
        if x > 340:
            break
    b.append("".join(bars))
    b.append(mark(316, 806, 58, BLUE, TEAL))
    save("updraft-bag-tag.svg", W, H, "".join(b), "Updraft Labs baggage tag")


# ------------------------------------------------------------- data plate
def data_plate():
    W, H = 1040, 580
    b = [f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="26" fill="{PAPER3}" stroke="{INK}" stroke-width="5"/>',
         f'<rect x="46" y="46" width="{W - 92}" height="{H - 92}" rx="10" fill="none" stroke="{INK}" stroke-width="2"/>',
         f'<rect x="46" y="46" width="{W - 92}" height="96" rx="10" fill="{INK}"/><rect x="46" y="110" width="{W - 92}" height="32" fill="{INK}"/>']
    for x, y in ((26, 26), (W - 26, 26), (26, H - 26), (W - 26, H - 26)):
        b.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{PAPER2}" stroke="{INK}" stroke-width="3"/><path d="M{x - 5} {y} h10" stroke="{INK}" stroke-width="2"/>')
    b.append(text("display", "Updraft Labs", 52, 74, 112, PAPER, 760))
    b.append(mark(W - 126, 58, 70, "#3A5EF0", "#86F5CF"))
    fields = [("MANUFACTURER", "UPDRAFT LABS"), ("MODEL", "UL-1 “LIFT”"), ("SERIAL NO.", "0001"),
              ("YEAR BUILT", "2026"), ("TYPE", "AI · SOFTWARE · DESIGN"), ("SERVICE CEILING", "AS LONG AS IT TAKES")]
    for i, (k, v) in enumerate(fields):
        col, row = i % 2, i // 2
        x, y = 74 + col * 466, 200 + row * 92
        b.append(text("mono", k, 16, x, y, INK, 500, 0.14))
        b.append(f'<line x1="{x}" y1="{y + 50}" x2="{x + 426}" y2="{y + 50}" stroke="{INK}" stroke-width="1.5"/>')
        b.append(text("mono", v, 27, x, y + 40, INK, 600, 0.04))
    b.append(f'<line x1="74" y1="500" x2="290" y2="500" stroke="{INK}" stroke-width="3" stroke-dasharray="18 7"/>')
    b.append(f'<line x1="316" y1="488" x2="520" y2="488" stroke="{BLUE}" stroke-width="5"/>')
    b.append(text("mono", "FIND THE DRAG · ADD THE LIFT", 18, W - 74, 506, INK, 600, 0.14, "end"))
    save("updraft-data-plate.svg", W, H, "".join(b), "Updraft Labs data plate")


# ------------------------------------------------------------- this side up
def this_side_up():
    W, H = 700, 400
    b = [f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="{PAPER}" stroke="{INK}" stroke-width="12"/>',
         f'<rect x="6" y="6" width="210" height="{H - 12}" fill="{ORANGE}" stroke="{INK}" stroke-width="12"/>']
    for x in (70, 152):  # two shipping arrows
        b.append(f'<path d="M{x} 300 V170 h-30 l42 -72 l42 72 h-30 V300 z" fill="{INK}" transform="translate(-12 0)"/>')
    b.append(text("display", "THIS", 74, 252, 140, INK, 800))
    b.append(text("display", "SIDE UP", 74, 252, 222, BLUE, 800))
    b.append(f'<line x1="252" y1="262" x2="{W - 40}" y2="262" stroke="{INK}" stroke-width="2"/>')
    b.append(text("mono", "UPDRAFT LABS · HANDLE WITH LIFT", 18, 252, 306, INK, 600, 0.12))
    b.append(text("mono", "CONTENTS: YOUR NEXT RELEASE", 15, 252, 340, INK, 500, 0.12))
    save("updraft-this-side-up.svg", W, H, "".join(b), "Updraft Labs This Side Up sticker")


patch(); wings(); bag_tag(); data_plate(); this_side_up()
print("written to", OUT)
