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
MAINJS = open(os.path.join(PUB, "main.js")).read()
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800'
         '&family=Geist:wght@300..700&family=Geist+Mono:wght@400;500&display=swap">')
CSS = ("<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#F2F0E9;color:#121211;font-family:Geist;position:relative;overflow:hidden}"
       ".h{font-family:'Bricolage Grotesque';font-weight:760;font-variation-settings:'opsz' 96,'wdth' 92;letter-spacing:-0.025em;line-height:.92}"
       ".h em{font-style:normal;color:#2443D6}.m{font-family:'Geist Mono';text-transform:uppercase;letter-spacing:.08em}"
       ".fig{position:absolute;top:0;bottom:0;background:#E8E5DB;border-left:1px solid #121211}.fig canvas{width:100%;height:100%;display:block}"
       ".tag{position:absolute;font-family:'Geist Mono';font-size:15px;letter-spacing:.08em;text-transform:uppercase;background:#F2F0E9;padding:6px 10px;box-shadow:inset 0 0 0 1.5px #121211}"
       ".frame{position:absolute;inset:0 26px;border-left:1.5px solid #121211;border-right:1.5px solid #121211;pointer-events:none}</style>")


def page(w, h, inner):
    return (f"<html><head>{FONTS}{CSS}</head><body style='width:{w}px;height:{h}px'>{inner}"
            f"<div class='frame'></div><script>{MAINJS}</script></body></html>")


og = page(1200, 630, f"""
<div style="position:absolute;left:66px;top:58px">{sized(logo, 46)}</div>
<div class="h" style="position:absolute;left:64px;top:214px;font-size:98px">Find the drag.<br><em>Add the lift.</em></div>
<div class="m" style="position:absolute;left:66px;bottom:60px;font-size:17px">AI · Software · Design · Growth</div>
<div class="fig" style="left:660px;right:26px"><canvas id="tunnel"></canvas><span class="tag" style="left:16px;top:16px">Fig. 01 — The lift</span></div>""")

banner = page(1584, 396, f"""
<div class="fig" style="left:26px;width:640px;border-left:0;border-right:1px solid #121211"><canvas id="tunnel"></canvas></div>
<div style="position:absolute;right:86px;top:74px;text-align:right">
<div class="h" style="font-size:76px">Find the drag.<br><em>Add the lift.</em></div>
<div class="m" style="margin-top:26px;font-size:16px">AI &amp; software studio · Process audits · Automation · Product</div></div>""")

avatar = f"""<html><body style="margin:0;width:800px;height:800px;display:grid;place-items:center;background:#121211">
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
    dict(html=og, w=1200, h=630, out=f"{A}/og.png", wait=3200),
    dict(html=banner, w=1584, h=396, out=f"{B}/updraft-linkedin-banner.png", wait=3200),
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
    for f in sorted(os.listdir(os.path.join(B, "world"))):
        z.write(os.path.join(B, "world", f), "world/" + f)
    for f in ("updraft-labs-brand-film.mp4", "updraft-labs-brand-film-poster.jpg"):
        if os.path.exists(os.path.join(B, f)):
            z.write(os.path.join(B, f), f)
print("rendered", len(jobs), "images; kit:", kit)
