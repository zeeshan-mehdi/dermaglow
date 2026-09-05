# Dermaglow Blog

Static blog for **blog.dermaglowbeauty.com**, built with [Astro](https://astro.build).

Lives in the same repo as the main marketing site (`dermaglowbeauty.com`) but is
published by a **separate Cloudflare Pages project** whose *root directory* is `blog`.
The two sites deploy independently from the same `git push`.

## Adding a post

Create a Markdown file in `src/content/blog/`. The filename becomes the URL:

`src/content/blog/vitamin-c-guide.md` -> `blog.dermaglowbeauty.com/posts/vitamin-c-guide/`

Use lowercase-hyphenated filenames — they are the permalink, so avoid renaming
after publishing (it breaks inbound links).

```markdown
---
title: "Your Post Title"
description: "One or two sentences. Used for SEO, social cards and the index page."
pubDate: 2026-09-10
tags: ["Ingredients", "Routine"]
heroEmoji: "🧴"
draft: false
---

Body content in Markdown. `## Headings` structure the article.
```

### Frontmatter fields

| Field | Required | Notes |
| --- | --- | --- |
| `title` | yes | Shown as H1 and in `<title>` |
| `description` | yes | Meta description + index blurb. Aim ~150 chars |
| `pubDate` | yes | `YYYY-MM-DD`. Controls sort order |
| `updatedDate` | no | Shows "Updated ..." on the post |
| `tags` | no | Defaults to `[]`. First 3 show on the index card |
| `heroEmoji` | no | Defaults to 🌿. The tile on the index card |
| `author` | no | Defaults to "Dermaglow" |
| `draft` | no | `true` hides it from production and RSS |

Committing the file to `main` is all that's needed — Cloudflare rebuilds and deploys
automatically. You can add posts straight through the GitHub web UI.

## What is generated for you

- Post index at `/`, newest first
- RSS feed at `/rss.xml`
- `sitemap-index.xml` + `sitemap-0.xml`
- Canonical URLs, Open Graph and Twitter card tags
- `BlogPosting` JSON-LD structured data per post
- A styled `/404`

## Local development

Requires **Node >= 22.12** (Astro 7). Check with `node -v`.

```bash
cd blog
npm install
npm run dev      # http://localhost:4321 — drafts visible
npm run build    # outputs to dist/
npm run preview  # serve the production build
```

Drafts are visible in `dev` and excluded from `build`.

## Deployment

| Setting | Value |
| --- | --- |
| Framework preset | Astro |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Root directory | `blog` |
| `NODE_VERSION` env var | `22` |

The apex site redirects `/blog/*` to this subdomain (see `../_redirects`), so the
unbuilt source in this folder is never served from `dermaglowbeauty.com`.
