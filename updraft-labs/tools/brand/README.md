# Logo source

The Lift mark and wordmarks are generated from code, so they stay exact.

- `brand.py`: mark geometry (`mark_paths`) and outlined, kerned text (Geist / Instrument Serif via HarfBuzz)
- `generate.py`: writes every SVG in `public/brand/`
- `social.py`: renders the PNG exports, app icons, favicon.ico, social images and `public/assets/og.png`, then rebuilds the brand-kit zip (uses `render.js`, a small Playwright renderer)

Geometry (v2): a U with outer radius 36 and inner 16, arm tops on one rising line (slope 2:5), sliced square to that line, right half lifted 16 with a visible gap of 7. The constants sit at the top of the mark section in `brand.py`.

Rebuild:

```sh
pip install fonttools uharfbuzz
mkdir -p tools/brand/fonts && cd tools/brand/fonts
curl -L -o 'Geist[wght].ttf' "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf"
curl -LO https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf
cd ../../.. && python3 tools/brand/generate.py public/brand && python3 tools/brand/social.py
```
