"""Generate the Updraft Labs logo system (SVG) into an output folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import mark_paths, text_path, cap_height, LIFT

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

INK = "#06080F"
PAPER = "#F5F5F2"
PALETTES = {
    # left = drag (deep blue), right = lift (sky -> mint)
    "dark": dict(l0="#3A5EF0", l1="#5B8CFF", r0="#6FC8FF", r1="#86F5CF", text="#EEF1F7", muted="#8B93A7"),
    "light": dict(l0="#2443D6", l1="#3F6DF5", r0="#1C9FE0", r1="#13C39A", text="#0B1020", muted="#5F6679"),
}

L, RP, (bx0, by0, bx1, by1) = mark_paths()
MW, MH = bx1 - bx0, by1 - by0


def grads(p, pre="u"):
    # gradients in mark user space so every lockup shades identically
    return (f'<linearGradient id="{pre}L" gradientUnits="userSpaceOnUse" x1="24" y1="108" x2="60" y2="40">'
            f'<stop offset="0" stop-color="{p["l0"]}"/><stop offset="1" stop-color="{p["l1"]}"/></linearGradient>'
            f'<linearGradient id="{pre}R" gradientUnits="userSpaceOnUse" x1="60" y1="96" x2="96" y2="-3">'
            f'<stop offset="0" stop-color="{p["r0"]}"/><stop offset="1" stop-color="{p["r1"]}"/></linearGradient>')


def mark_group(x, y, h, fill=None, pre="u", animate=False):
    s = h / MH
    fl = fill or f"url(#{pre}L)"
    fr = fill or f"url(#{pre}R)"
    right = f'<path d="{RP}" fill="{fr}"/>'
    if animate:
        # starts as a whole blue U, then the right half rises and brightens
        right = f'<g class="lift">{right}<path class="was" d="{RP}" fill="{fl}"/></g>'
    return (f'<g transform="translate({x - bx0 * s:.3f} {y - by0 * s:.3f}) scale({s:.5f})">'
            f'<path d="{L}" fill="{fl}"/>{right}</g>')


ANIM = ("<style>.lift{animation:lift 1.25s cubic-bezier(.16,1,.3,1) .35s both}"
        ".was{animation:was 1s ease-out .45s both}"
        f"@keyframes lift{{from{{transform:translateY({LIFT:g}px)}}to{{transform:none}}}}"
        "@keyframes was{from{opacity:1}to{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.lift{animation:none}.was{animation:none;opacity:0}}</style>")


def svg(w, h, body, defs="", title="Updraft Labs"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>'
            + (f"<defs>{defs}</defs>" if defs else "") + body + "</svg>\n")


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


# ---------- mark only
pad = 0
for mode in ("dark", "light"):
    p = PALETTES[mode]
    write(f"updraft-mark-{mode}-bg.svg", svg(MW, MH, mark_group(0, 0, MH), grads(p), "Updraft Labs mark"))
write("updraft-mark-white.svg", svg(MW, MH, mark_group(0, 0, MH, "#FFFFFF"), title="Updraft Labs mark"))
write("updraft-mark-black.svg", svg(MW, MH, mark_group(0, 0, MH, INK), title="Updraft Labs mark"))
write("updraft-mark-animated.svg", svg(MW, MH, mark_group(0, 0, MH, animate=True), grads(PALETTES["dark"]) + ANIM, "Updraft Labs mark"))


# ---------- wordmark helpers
SIZE = 100.0
CAP = cap_height("geist", 600) * SIZE


def wordmark(x, base, p, solid=None, serif=False):
    d1, a1, _ = text_path("geist", "Updraft", SIZE, 620, -0.035, x, base)
    out = f'<path d="{d1}" fill="{solid or p["text"]}"/>'
    if serif:
        d2, a2, _ = text_path("serif-italic", "Labs", SIZE * 1.12, 400, -0.01, x + a1 + SIZE * 0.2, base)
        fill = solid or "url(#uT)"
        w = a1 + SIZE * 0.2 + a2
    else:
        d2, a2, _ = text_path("geist", "Labs", SIZE, 380, -0.02, x + a1 + SIZE * 0.23, base)
        fill = solid or p["muted"]
        w = a1 + SIZE * 0.23 + a2
    return out + f'<path d="{d2}" fill="{fill}"/>', w


def tgrad(p):
    return (f'<linearGradient id="uT" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{p["r0"]}"/>'
            f'<stop offset="1" stop-color="{p["r1"]}"/></linearGradient>')


# ---------- horizontal lockup: mark height = 2 x cap height, centred on caps
def horizontal(p, solid=None, serif=False, animate=False):
    mh = CAP * 2.0
    mw = MW * mh / MH
    gap = SIZE * 0.34
    top = 0.0
    base = top + mh / 2 + CAP / 2 + mh * 0.06  # nudge: the lifted arm rises above the caps
    words, ww = wordmark(mw + gap, base, p, solid, serif)
    W = mw + gap + ww
    descender = SIZE * 0.24
    H = max(mh, base + descender)
    body = mark_group(0, top, mh, solid, animate=animate) + words
    return W, H, body


for mode in ("dark", "light"):
    p = PALETTES[mode]
    for serif in (False, True):
        W, H, body = horizontal(p, serif=serif)
        tag = "-expressive" if serif else ""
        write(f"updraft-logo{tag}-{mode}-bg.svg", svg(W, H, body, grads(p) + tgrad(p)))
for mode in ("dark", "light"):
    W, H, body = horizontal(PALETTES[mode], animate=True)
    write(f"updraft-logo-{mode}-bg-animated.svg", svg(W, H, body, grads(PALETTES[mode]) + tgrad(PALETTES[mode]) + ANIM))
for col, nm in (("#FFFFFF", "white"), (INK, "black")):
    W, H, body = horizontal(PALETTES["dark"], solid=col)
    write(f"updraft-logo-{nm}.svg", svg(W, H, body))


# ---------- stacked lockup
def stacked(p, solid=None):
    mh = CAP * 3.4
    mw = MW * mh / MH
    _, ww = wordmark(0, 0, p)
    W = max(ww, mw)
    gap = SIZE * 0.42
    base = mh + gap + CAP
    words, _ = wordmark((W - ww) / 2, base, p, solid)
    body = mark_group((W - mw) / 2, 0, mh, solid) + words
    return W, base + SIZE * 0.24, body


for mode in ("dark", "light"):
    p = PALETTES[mode]
    W, H, body = stacked(p)
    write(f"updraft-logo-stacked-{mode}-bg.svg", svg(W, H, body, grads(p)))

# ---------- app icon / avatar: mark on a deep tile with a soft lift glow
def app_icon(size=1024, radius=0.225):
    p = PALETTES["dark"]
    rr = size * radius
    mh = size * 0.62
    mw = MW * mh / MH
    x = (size - mw) / 2 - size * 0.005
    y = (size - mh) / 2 + size * 0.012
    defs = grads(p)
    # flat ink tile, like the site: no glow, no gradient behind the mark
    body = f'<rect width="{size}" height="{size}" rx="{rr}" fill="#121211"/>' + mark_group(x, y, mh)
    return svg(size, size, body, defs, "Updraft Labs")


write("updraft-app-icon.svg", app_icon())

# ---------- favicon: adapts to light/dark browser chrome; wider gap so the split survives 16px
Lf, Rf, (fx0, fy0, fx1, fy1) = mark_paths(gap=11, lift=18)
fw, fh = fx1 - fx0, fy1 - fy0
side = max(fw, fh) + 8
ox, oy = (side - fw) / 2 - fx0, (side - fh) / 2 - fy0
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:.1f} {side:.1f}">'
       f'<style>.l{{fill:{PALETTES["light"]["l0"]}}}.r{{fill:{PALETTES["light"]["r0"]}}}'
       f'@media (prefers-color-scheme:dark){{.l{{fill:{PALETTES["dark"]["l1"]}}}.r{{fill:{PALETTES["dark"]["r1"]}}}}}</style>'
       f'<g transform="translate({ox:.2f} {oy:.2f})"><path class="l" d="{Lf}"/><path class="r" d="{Rf}"/></g></svg>\n')
write("favicon.svg", fav)
print("written to", OUT)
