"""Render PNG exports and social images from the SVGs in public/brand.

    python3 tools/brand/social.py      (run after generate.py; needs Node + Playwright)
"""
import json, os, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(HERE, "..", "..", "public"))
B, A = os.path.join(PUB, "brand"), os.path.join(PUB, "assets")


def read(name):
    return open(os.path.join(B, name)).read()


def sized(svg, h):
    import re
    return re.sub(r' width="[\d.]+" height="[\d.]+"', f' style="height:{h}px;width:auto"', svg, count=1)


mark, logo = read("updraft-mark-dark-bg.svg"), read("updraft-logo-light-bg.svg")
# both SVGs name their gradients uL/uR; rename the mark's so each keeps its own colours
mark = mark.replace('id="uL"', 'id="mL"').replace("url(#uL)", "url(#mL)").replace('id="uR"', 'id="mR"').replace("url(#uR)", "url(#mR)")
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&display=swap">'
CSS = ("<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#fff;color:#0B1020;font-family:Geist;position:relative;overflow:hidden}"
       ".h{font-weight:600;letter-spacing:-0.04em;line-height:1.02}.h span{color:#2443D6}.s{color:#687084}"
       ".panel{position:absolute;top:0;bottom:0;display:grid;place-items:center;"
       "background:radial-gradient(closest-side at 60% 40%,rgba(63,109,245,.35),transparent),#0B1020}</style>")


def page(w, h, inner):
    return f"<html><head>{FONTS}{CSS}</head><body style='width:{w}px;height:{h}px'>{inner}</body></html>"


og = page(1200, 630, f"""
<div style="position:absolute;left:72px;top:64px">{sized(logo, 44)}</div>
<div class="h" style="position:absolute;left:70px;top:206px;font-size:90px">Find the drag.<br><span>Add the lift.</span></div>
<div class="s" style="position:absolute;left:72px;bottom:66px;font-size:24px">AI &amp; software studio</div>
<div class="panel" style="left:780px;right:0">{sized(mark, 300)}</div>""")

banner = page(1584, 396, f"""
<div class="panel" style="left:0;width:560px">{sized(mark, 220)}</div>
<div style="position:absolute;right:96px;top:84px;text-align:right">
<div class="h" style="font-size:78px">Find the drag.<br><span>Add the lift.</span></div>
<div class="s" style="margin-top:22px;font-size:22px">AI &amp; software studio · Process audits · Automation · Product</div></div>""")

avatar = f"""<html><body style="margin:0;width:800px;height:800px;display:grid;place-items:center;background:#0B1020">
<div style="margin-top:10px">{sized(mark, 400)}</div></body></html>"""

jobs = [
    dict(src=f"{B}/updraft-app-icon.svg", w=1024, h=1024, out=f"{B}/updraft-app-icon-1024.png", transparent=True),
    dict(src=f"{B}/updraft-app-icon.svg", w=512, h=512, out=f"{B}/updraft-app-icon-512.png", transparent=True),
    dict(src=f"{B}/updraft-app-icon.svg", w=180, h=180, out=f"{A}/apple-touch-icon.png"),
    dict(src=f"{B}/favicon.svg", w=32, h=32, out=f"{B}/favicon-32.png", transparent=True),
    dict(src=f"{B}/favicon.svg", w=48, h=48, out=f"{B}/favicon-48.png", transparent=True),
    dict(src=f"{B}/updraft-logo-dark-bg.svg", w=1440, h=284, out=f"{B}/updraft-logo-dark-bg.png", transparent=True),
    dict(src=f"{B}/updraft-logo-light-bg.svg", w=1440, h=284, out=f"{B}/updraft-logo-light-bg.png", transparent=True),
    dict(src=f"{B}/updraft-logo-stacked-dark-bg.svg", w=1000, h=740, iw=900, ih=700, out=f"{B}/updraft-logo-stacked-dark-bg.png", transparent=True),
    dict(src=f"{B}/updraft-logo-stacked-light-bg.svg", w=1000, h=740, iw=900, ih=700, out=f"{B}/updraft-logo-stacked-light-bg.png", transparent=True),
    dict(src=f"{B}/updraft-mark-dark-bg.svg", w=680, h=1040, out=f"{B}/updraft-mark-dark-bg.png", transparent=True),
    dict(src=f"{B}/updraft-mark-light-bg.svg", w=680, h=1040, out=f"{B}/updraft-mark-light-bg.png", transparent=True),
    dict(html=og, w=1200, h=630, out=f"{A}/og.png", wait=1500),
    dict(html=banner, w=1584, h=396, out=f"{B}/updraft-linkedin-banner.png", wait=1500),
    dict(html=avatar, w=800, h=800, out=f"{B}/updraft-social-avatar.png"),
]
jp = os.path.join(HERE, ".jobs.json")
json.dump(jobs, open(jp, "w"))
subprocess.run(["node", os.path.join(HERE, "render.js"), jp], check=True)
os.remove(jp)

from PIL import Image
Image.open(f"{B}/favicon-48.png").save(os.path.join(PUB, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

kit = os.path.join(B, "updraft-labs-brand-kit.zip")
with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(B)):
        if f.endswith((".svg", ".png")) and f != "favicon-48.png":
            z.write(os.path.join(B, f), f)
    z.write(os.path.join(A, "og.png"), "og.png")
print("rendered", len(jobs), "images; kit:", kit)
