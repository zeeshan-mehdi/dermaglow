# Updraft Labs — website

Static site + one Cloudflare Pages Function (the contact form). No build step.

```
public/                 everything visitors see (Cloudflare serves only this folder)
  index.html            the whole site, one page
  styles.css, main.js   styles; nav, reveals, tabs, contact form, hero animation
  privacy/              privacy policy
  404.html, _headers    not-found page; security + cache headers
  robots.txt, sitemap.xml   generated — don't edit by hand
  brand/                logo system (SVG + PNG), app icon, favicon, social images, brand page, kit zip
  assets/               social-share image, apple-touch icon, project screenshots
functions/api/contact.js    POST /api/contact → emails the form to you (via Resend)
site.config.json        domain, email, booking link, location, socials  ← edit this
tools/configure.py      applies site.config.json everywhere
tools/brand/            code that generates the logo files (see its README)
wrangler.jsonc          generated Pages config
```

## Launch checklist

**1. Fill in `site.config.json`, then run `python3 tools/configure.py`.**
That one command updates the canonical/social-share URLs, search-engine data,
every email link, the "Book a call" buttons, the contact details, footer
social icons, `robots.txt`, `sitemap.xml` and `wrangler.jsonc`. Safe to re-run.

| Field | Example | Notes |
|---|---|---|
| `domain` | `updraftlabs.com` | no `https://`, no `www` |
| `email` | `hello@updraftlabs.com` | shown on the site |
| `booking_url` | `https://cal.com/updraft/30min` | optional — "Book a call" goes here instead of the form |
| `location` | `Islamabad, Pakistan` | optional |
| `social.*` | full profile URLs | empty ones are hidden |
| `contact_form.to_email` | | optional — inbox for form messages (defaults to `email`) |

**2. Create the Cloudflare Pages project.**
Workers & Pages → Create → Pages → Connect to Git → pick the repo.
Framework preset: **None** · Build command: *(empty)* · Build output directory: **`public`** ·
Root directory: **`updraft-labs`** (or empty once this lives in its own repo).
CLI alternative, from this folder: `npx wrangler pages deploy`.

**3. Connect the domain.** Pages project → Custom domains → add `yourdomain` and
`www.yourdomain`. If the domain is registered at Cloudflare, DNS is set automatically.
Redirect `www` → apex with Rules → Redirect Rules (or Bulk Redirects).

**4. Email.**
- Inbox: Cloudflare Email Routing (free) can forward `hello@yourdomain` to Gmail.
- Contact form: create a free [Resend](https://resend.com) account, verify the domain
  (it gives you DNS records to add in Cloudflare), create an API key, and add it as
  the **`RESEND_API_KEY`** secret: Pages project → Settings → Variables and Secrets.
  Until then the form still works — it opens the visitor's email app instead.

**5. After launch.** Submit `https://yourdomain/sitemap.xml` in Google Search Console
and Bing Webmaster Tools. Test the share card at opengraph.xyz.

## Adding content

- **Portfolio project** — in `public/index.html`, find `NEW PROJECT` inside `#work`; copy the
  commented card and put the screenshot (1600×1000) in `public/assets/work/`.
- **Team members** — find `PEOPLE` inside `#team`; uncomment and copy one `.person` per
  teammate, photos (600×600) in `public/assets/team/`.
- **Privacy policy** — `public/privacy/index.html`; review it before launch (it's a
  sensible starting point, not legal advice).

## Local preview

`npx wrangler pages dev` (includes the contact function) or
`python3 -m http.server 8787 -d public`.
