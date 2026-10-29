"""Render the Updraft Labs brand film (12.4 s, 1920x1080, 30 fps).

    python3 tools/brand/film.py      (needs Node + Playwright + ffmpeg)

Serves public/ locally, captures the live site, renders every frame
deterministically from film/reel.template.html, and encodes
public/brand/updraft-labs-brand-film.mp4 plus a poster frame.
"""
import functools, http.server, os, re, shutil, subprocess, tempfile, threading

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(HERE, "..", "..", "public"))
B = os.path.join(PUB, "brand")

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


handler = functools.partial(Quiet, directory=PUB)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"

work = tempfile.mkdtemp(prefix="updraft-film-")
shots, frames = os.path.join(work, "shots"), os.path.join(work, "frames")
os.makedirs(shots); os.makedirs(frames)
subprocess.run(["node", os.path.join(HERE, "film", "caps.js"), base, shots], check=True)
srv.shutdown()

logo = open(os.path.join(B, "updraft-logo-light-bg.svg")).read()
logo = re.sub(r' width="[\d.]+" height="[\d.]+"', ' class="lockup"', logo, count=1)
end = logo
for a in ("uL", "uR", "uT"):
    end = end.replace(f'id="{a}"', f'id="e{a[1]}"').replace(f"url(#{a})", f"url(#e{a[1]})")
page = (open(os.path.join(HERE, "film", "reel.template.html")).read()
        .replace("{{SHOTS}}", shots).replace("{{WORLD}}", os.path.join(B, "world"))
        .replace("{{LOGO}}", logo).replace("{{LOGO_END}}", end))
reel = os.path.join(work, "reel.html")
open(reel, "w").write(page)

subprocess.run(["node", os.path.join(HERE, "film", "render.js"), reel, frames, "1920", "1080", "30", "12.4", "1"], check=True)
out = os.path.join(B, "updraft-labs-brand-film.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(frames, "%04d.png"),
                "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
from PIL import Image
Image.open(os.path.join(frames, "0040.png")).convert("RGB").save(os.path.join(B, "updraft-labs-brand-film-poster.jpg"), quality=88)
shutil.rmtree(work)
print("film:", out)
