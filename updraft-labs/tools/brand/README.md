# Logo source

The Lift mark and wordmarks are generated from code, so they stay exact.

- `brand.py`: mark geometry (`mark_paths`) and outlined, kerned text (Geist / Instrument Serif via HarfBuzz)
- `generate.py`: writes every SVG in `public/brand/`
- `render.js`: Playwright renderer used for the PNG exports, social images and `public/assets/og.png`

Rebuild:

```sh
pip install fonttools uharfbuzz
mkdir -p tools/brand/fonts && cd tools/brand/fonts
curl -L -o 'Geist[wght].ttf' "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf"
curl -LO https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf
cd ../../.. && python3 tools/brand/generate.py public/brand
```

Then re-zip the kit: `cd public/brand && zip -r updraft-labs-brand-kit.zip . -x index.html -x favicon-48.png && zip -j updraft-labs-brand-kit.zip ../assets/og.png`
