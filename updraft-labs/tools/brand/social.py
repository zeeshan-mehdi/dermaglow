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


mark, logo = read("updraft-mark-dark-bg.svg"), read("updraft-logo-dark-bg.svg")
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700'
         '&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap">')
BG = ("background:radial-gradient(60% 80% at 78% 40%, rgba(91,140,255,.22), transparent 60%),"
      "radial-gradient(40% 60% at 95% 95%, rgba(134,245,207,.14), transparent 70%),#06080f;")
GRAIN = ('<div style="position:absolute;inset:0;opacity:.06;background-image:url(&quot;data:image/svg+xml,'
         '%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27160%27 height=%27160%27%3E%3Cfilter id=%27n%27%3E'
         '%3CfeTurbulence type=%27fractalNoise%27 baseFrequency=%27.9%27 numOctaves=%273%27/%3E%3C/filter%3E'
         '%3Crect width=%27100%25%27 height=%27100%25%27 filter=%27url(%23n)%27/%3E%3C/svg%3E&quot;)"></div>')
EM = ("font-family:Instrument Serif;font-style:italic;background:linear-gradient(100deg,#5b8cff,#7dd3fc 45%,#86f5cf);"
      "-webkit-background-clip:text;color:transparent;padding-right:.08em;letter-spacing:-0.01em")

og = f"""<html><head>{FONTS}</head><body style="margin:0;width:1200px;height:630px;position:relative;overflow:hidden;{BG}font-family:Geist;color:#eef1f7">{GRAIN}
<div style="position:absolute;right:-50px;top:30px;opacity:.10">{sized(mark, 640)}</div>
<div style="position:absolute;left:84px;top:86px">{sized(logo, 64)}</div>
<div style="position:absolute;left:84px;top:236px;font-size:92px;font-weight:500;letter-spacing:-0.045em;line-height:.98">Find the drag.<br><span style="{EM}">Add the lift.</span></div>
<div style="position:absolute;left:86px;bottom:74px;font-family:Geist Mono;font-size:20px;letter-spacing:.12em;text-transform:uppercase;color:#7dd3fc">AI · Software · Design · Growth</div></body></html>"""

banner = f"""<html><head>{FONTS}</head><body style="margin:0;width:1584px;height:396px;position:relative;overflow:hidden;{BG}font-family:Geist;color:#eef1f7">{GRAIN}
<div style="position:absolute;left:470px;top:-90px;opacity:.08">{sized(mark, 560)}</div>
<div style="position:absolute;right:96px;top:84px;text-align:right">
<div style="font-size:66px;font-weight:500;letter-spacing:-0.04em;line-height:1.02">Find the drag.<br><span style="{EM}">Add the lift.</span></div>
<div style="margin-top:26px;font-family:Geist Mono;font-size:17px;letter-spacing:.12em;text-transform:uppercase;color:#7dd3fc">AI &amp; software studio · Process audits · Automation · Product</div></div></body></html>"""

avatar = f"""<html><body style="margin:0;width:800px;height:800px;display:grid;place-items:center;background:radial-gradient(55% 55% at 60% 38%, rgba(125,211,252,.22), transparent 70%),linear-gradient(#101833,#05070d)">
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
    dict(html=og, w=1200, h=630, out=f"{A}/og.png", wait=1200),
    dict(html=banner, w=1584, h=396, out=f"{B}/updraft-linkedin-banner.png", wait=1200),
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
