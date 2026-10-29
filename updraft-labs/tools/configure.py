#!/usr/bin/env python3
"""Apply site.config.json to the site.

Run after editing site.config.json:

    python3 tools/configure.py

It rewrites the generated blocks in index.html (between <!-- @name --> and
<!-- /@name --> markers), every [data-email] link, CONTACT_EMAIL in main.js,
and regenerates robots.txt, sitemap.xml and wrangler.jsonc. Safe to re-run.
"""
import datetime
import html
import json
import pathlib
import re
import sys

PROJECT = pathlib.Path(__file__).resolve().parent.parent
ROOT = PROJECT / "public"  # the files Cloudflare Pages serves
cfg = json.loads((PROJECT / "site.config.json").read_text())

domain = cfg["domain"].strip().removeprefix("https://").removeprefix("http://").strip("/")
email = cfg["email"].strip()
booking = cfg.get("booking_url", "").strip()
location = cfg.get("location", "").strip()
social = {k: v.strip() for k, v in cfg.get("social", {}).items() if v.strip()}
form = cfg.get("contact_form", {})
base = f"https://{domain}"
e = html.escape

if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", domain):
    sys.exit(f"domain looks wrong: {domain!r} (use e.g. updraftlabs.com)")
if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
    sys.exit(f"email looks wrong: {email!r}")

# Pages listed in the sitemap: path -> file
PAGES = {"/": "index.html", "/brand/": "brand/index.html", "/privacy/": "privacy/index.html"}

ICONS = {
    "linkedin": ("LinkedIn", '<path d="M6.5 9.5v8M6.5 6.5v.01M10.5 17.5v-8M10.5 13a3 3 0 016 0v4.5"/>'),
    "x": ("X", '<path d="M5 5l14 14M19 5L5 19"/>'),
    "instagram": ("Instagram", '<rect x="4.5" y="4.5" width="15" height="15" rx="4.5"/><circle cx="12" cy="12" r="3.5"/><path d="M16.5 7.5v.01"/>'),
    "github": ("GitHub", '<path d="M9.5 19c-4 1.3-4-2-5.5-2.5M15 21v-3.4a3 3 0 00-.8-2.3c2.7-.3 5.3-1.3 5.3-5.8a4.5 4.5 0 00-1.2-3.1 4.2 4.2 0 00-.1-3.1s-1-.3-3.3 1.2a11.4 11.4 0 00-6 0C6.6 3 5.6 3.3 5.6 3.3a4.2 4.2 0 00-.1 3.1 4.5 4.5 0 00-1.2 3.1c0 4.5 2.6 5.5 5.3 5.8a3 3 0 00-.8 2.3V21"/>'),
}


def block(text, name, lines):
    """Replace the content between <!-- @name ... --> and <!-- /@name -->."""
    pat = re.compile(rf"([ \t]*)(<!-- @{name}\b[^>]*-->)\n.*?[ \t]*(<!-- /@{name} -->)", re.S)
    m = pat.search(text)
    if not m:
        sys.exit(f"marker <!-- @{name} --> not found")
    ind = m.group(1)
    body = "".join(f"{ind}{l}\n" for l in lines)
    return text[: m.start()] + f"{ind}{m.group(2)}\n{body}{ind}{m.group(3)}" + text[m.end():]


def emails(text):
    return re.sub(r'href="mailto:[^"]*"( data-email)>[^<]*<', f'href="mailto:{e(email)}"\\1>{e(email)}<', text)


org = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Updraft Labs",
    "url": base + "/",
    "logo": base + "/brand/updraft-app-icon-512.png",
    "email": email,
    "description": "AI and software studio that finds bottlenecks in businesses and builds the AI and software that removes them.",
    "foundingDate": cfg.get("founded", ""),
    "sameAs": list(social.values()) + ["https://buildyar.tech"],
}
if location:
    org["address"] = {"@type": "PostalAddress", "addressLocality": location}
org = {k: v for k, v in org.items() if v}

seo = [
    f'<link rel="canonical" href="{base}/">',
    f'<meta property="og:url" content="{base}/">',
    f'<meta property="og:site_name" content="Updraft Labs">',
    f'<meta property="og:image" content="{base}/assets/og.png">',
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    f'<meta name="twitter:image" content="{base}/assets/og.png">',
    '<script type="application/ld+json">' + json.dumps(org, ensure_ascii=False) + "</script>",
]

contact = [f'<li><span>Email</span><a href="mailto:{e(email)}" data-email>{e(email)}</a></li>']
if booking:
    contact.append(f'<li><span>Call</span><a href="{e(booking)}" target="_blank" rel="noopener">Book a 30-min call ↗</a></li>')
if location:
    contact.append(f"<li><span>Based in</span>{e(location)}</li>")
contact.append("<li><span>Response</span>Within 24 hours</li>")
contact.append("<li><span>Works with</span>Teams worldwide, remote-first</li>")

socials = []
if social:
    socials.append('<div class="socials">')
    for key, url in social.items():
        label, path = ICONS.get(key, (key.title(), '<circle cx="12" cy="12" r="7"/>'))
        socials.append(f'  <a href="{e(url)}" target="_blank" rel="noopener" aria-label="{label}"><svg viewBox="0 0 24 24">{path}</svg></a>')
    socials.append("</div>")

# index.html
p = ROOT / "index.html"
t = p.read_text()
t = block(t, "seo", seo)
t = block(t, "contact", contact)
t = block(t, "social", socials)
# "Book a call" links go straight to the calendar when there is one
t = re.sub(r'<a href="[^"]*"([^>]*) data-book>', lambda m: f'<a href="{e(booking) if booking else "#contact"}"{m.group(1)} data-book>', t)
p.write_text(emails(t))

# other pages
for f in ["404.html", "privacy/index.html", "brand/index.html"]:
    q = ROOT / f
    if q.exists():
        s = emails(q.read_text())
        s = re.sub(r'(<span data-domain>)[^<]*(</span>)', rf"\g<1>{domain}\2", s)
        q.write_text(s)

# main.js
js = ROOT / "main.js"
js.write_text(re.sub(r'const CONTACT_EMAIL = "[^"]*";', f'const CONTACT_EMAIL = "{email}";', js.read_text()))

# robots + sitemap
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
today = datetime.date.today().isoformat()
urls = "".join(f"  <url><loc>{base}{path}</loc><lastmod>{today}</lastmod></url>\n" for path in PAGES)
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n"
)

# wrangler.jsonc: a Worker serving public/ as static assets; vars are read by src/contact.js
wr = {
    "name": "updraft",  # the Worker's name in Cloudflare
    "main": "src/worker.js",
    "compatibility_date": "2026-09-01",
    "assets": {
        "directory": "public",
        "binding": "ASSETS",
        "not_found_handling": "404-page",
        "run_worker_first": ["/api/*"],
    },
    # Workers Logs (as set in the dashboard): request logs kept and searchable,
    # error grouping on; tracing off.
    "observability": {
        "enabled": False,
        "head_sampling_rate": 1,
        "redact_query_string": False,
        "logs": {"enabled": True, "head_sampling_rate": 1, "invocation_logs": True, "persist": True},
        "traces": {"enabled": False, "head_sampling_rate": 1, "persist": True},
        "issues": {"enabled": True},
    },
    "vars": {
        "CONTACT_TO": form.get("to_email") or email,
        "CONTACT_FROM": form.get("from_email") or f"website@{domain}",
        "SITE_DOMAIN": domain,
    },
}
(PROJECT / "wrangler.jsonc").write_text(
    "// Generated by tools/configure.py: edit site.config.json instead.\n" + json.dumps(wr, indent=2) + "\n"
)

print(f"Applied: {base}  ·  {email}  ·  {len(social)} social link(s)  ·  booking: {'yes' if booking else 'no'}")
