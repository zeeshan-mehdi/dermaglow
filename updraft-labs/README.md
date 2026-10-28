# updraftlabs — website

Static site (plain HTML/CSS/JS, no build step) for Updraft Labs.

```
index.html     the whole site, one page
styles.css     all styles
main.js        nav, scroll reveals, "Where AI fits" tabs, contact form, hero animation
404.html       not-found page (Cloudflare Pages serves it automatically)
_headers       security + cache headers for Cloudflare Pages
assets/        logo (mark.svg), social image (og.png), Dermaglow screenshots
```

## Deploy on Cloudflare Pages

1. Put this folder in its own GitHub repo (recommended), or keep it here.
2. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git.
3. Build settings: Framework preset **None**, build command **empty**,
   output directory **`/`** (or **`updraft-labs`** if it stays inside this repo).
4. After the first deploy: Custom domains → add your domain.

Or from a terminal: `npx wrangler pages deploy . --project-name updraft-labs`

## Things to update

- **Email**: `CONTACT_EMAIL` at the top of `main.js` (currently `hello@updraftlabs.ai`, a placeholder).
- **Domain**: once bought, make `og:image` in `index.html` an absolute URL (`https://<domain>/assets/og.png`).
- **Portfolio**: add projects in the `#work` section of `index.html` — copy a `.work` card.
- **Team**: the `#team` section lists disciplines; swap in people (photo, name, role) when ready.
- **Contact form**: it opens the visitor's email app (static site). For in-page submissions, plug in
  Formspree/Web3Forms or a Cloudflare Pages Function.

Local preview: `python3 -m http.server 8787` in this folder, then open http://localhost:8787.
