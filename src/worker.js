// The apex Worker. Static assets serve everything that exists on disk;
// this script only sees requests that match no file, and handles one route:
//
//   /get/ios, /get/android — count the click, then send the visitor on.
//
// Every store link on the site and the blog can point here instead of at
// the store directly, so the count is taken server-side: an ad-blocker
// cannot see it, and it costs the visitor one 302. Each hit is one row in
// the Workers Analytics Engine dataset bound as STORE_CLICKS (declared in
// wrangler.jsonc). If the binding is missing the redirect still works and
// nothing is counted — the link must never break because the counter is
// unconfigured.
//
// Query it in the Cloudflare dashboard (Analytics Engine → SQL):
//   SELECT blob1 AS store, blob2 AS src, count() AS clicks
//   FROM store_clicks WHERE timestamp > NOW() - INTERVAL '30' DAY
//   GROUP BY store, src ORDER BY clicks DESC
//
// `src` is set by the link itself (?src=hero, nav, blog-cta …) and names
// the placement; the referrer names the page. Together they answer "which
// button, on which page, from where".

import { deviceClass, trackPageView } from "./track.js";

const STORES = {
  ios: "https://apps.apple.com/app/id6790204292",
  android: "https://play.google.com/store/apps/details?id=com.app.dermaglow",
};


export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/get\/([a-z]+)\/?$/);
    if (m && request.method === "GET") return storeRedirect(request, env, m[1], url);
    if (url.pathname === "/stats" && request.method === "GET") return stats(request, env);
    // Anything else: the static site, including _redirects and _headers —
    // counted as a page view when it is an HTML page for a person.
    const asset = await env.ASSETS.fetch(request);
    ctx.waitUntil(trackPageView(request, asset, env));
    // Marker so "did the script run for this page?" is answerable from a
    // response header — the asset layer's cf-cache-status says nothing
    // about that.
    const response = new Response(asset.body, asset);
    response.headers.set("X-Counted", env.PAGE_VIEWS ? "1" : "0");
    return response;
  },
};

async function storeRedirect(request, env, store, url) {
  const target = STORES[store];
  if (!target) return new Response("Not found", { status: 404 });

  const src = (url.searchParams.get("src") || "direct").slice(0, 40);
  const referrer = request.headers.get("Referer") || "";
  let referrerHost = "";
  try { referrerHost = referrer ? new URL(referrer).host : ""; } catch { /* unparseable, leave blank */ }
  const country = request.headers.get("CF-IPCountry") || "";
  const device = deviceClass(request.headers.get("User-Agent") || "");

  if (env.STORE_CLICKS && device !== "bot") {
    try {
      env.STORE_CLICKS.writeDataPoint({
        blobs: [store, src, referrerHost, country, device],
        doubles: [1],
        indexes: [store],
      });
    } catch { /* counting is best-effort; the redirect is not */ }
  }

  return Response.redirect(target, 302);
}


// ── /stats — the click counts, in a browser, behind a password ─────────────
//
// Analytics Engine has no dashboard query UI; it has an SQL API that needs
// an API token. This route runs the queries server-side and renders them,
// so reading the numbers is a URL and a password rather than a curl.
//
// Needs two Worker secrets (Settings → Variables and Secrets, type Secret):
//   STATS_PASSWORD      whatever you choose; HTTP Basic, any username
//   CF_ANALYTICS_TOKEN  an API token with Account · Account Analytics · Read
// and CF_ACCOUNT_ID as a plain var (wrangler.jsonc). Missing any of them →
// 503 with a message saying which, never a half-working page.
//
// Counts use SUM(_sample_interval), not count(): Analytics Engine samples
// under heavy write load and _sample_interval is the weight that restores
// the true total. At this site's volume the two are identical; the habit
// costs nothing and stays correct if a post ever goes viral.

const SQL = {
  placements: `
    SELECT blob1 AS store, blob2 AS src, blob3 AS referrer, blob5 AS device,
           SUM(_sample_interval) AS clicks
    FROM store_clicks
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY store, src, referrer, device
    ORDER BY clicks DESC
    LIMIT 200 FORMAT JSON`,
  daily: `
    SELECT toStartOfInterval(timestamp, INTERVAL '1' DAY) AS day, blob1 AS store,
           SUM(_sample_interval) AS clicks
    FROM store_clicks
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY day, store
    ORDER BY day DESC, store FORMAT JSON`,
  countries: `
    SELECT blob4 AS country, SUM(_sample_interval) AS clicks
    FROM store_clicks
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY country
    ORDER BY clicks DESC
    LIMIT 15 FORMAT JSON`,
  // Page views come back grouped by visitor as well, and uniques are counted
  // here rather than in SQL: one query, and "distinct visitors" needs no
  // support for COUNT(DISTINCT) in the dataset's dialect.
  viewsByDay: `
    SELECT toStartOfInterval(timestamp, INTERVAL '1' DAY) AS day, blob1 AS host,
           blob6 AS visitor, SUM(_sample_interval) AS views
    FROM page_views
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY day, host, visitor
    LIMIT 10000 FORMAT JSON`,
  viewsByPage: `
    SELECT blob1 AS host, blob2 AS path, blob6 AS visitor, SUM(_sample_interval) AS views
    FROM page_views
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY host, path, visitor
    LIMIT 10000 FORMAT JSON`,
  viewsBySource: `
    SELECT blob3 AS referrer, blob7 AS utm, blob6 AS visitor, SUM(_sample_interval) AS views
    FROM page_views
    WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY referrer, utm, visitor
    LIMIT 10000 FORMAT JSON`,
};

/** Collapse visitor-grouped rows into {key → {visitors, views}}, sorted by visitors. */
function rollup(rows, keyOf) {
  const acc = new Map();
  for (const r of rows) {
    const k = keyOf(r);
    const e = acc.get(k) || { ...r, visitors: new Set(), views: 0 };
    e.visitors.add(r.visitor);
    e.views += Number(r.views);
    acc.set(k, e);
  }
  return [...acc.values()]
    .map((e) => ({ ...e, visitors: e.visitors.size }))
    .sort((a, b) => b.visitors - a.visitors || b.views - a.views);
}

async function stats(request, env) {
  const missing = ["STATS_PASSWORD", "CF_ANALYTICS_TOKEN", "CF_ACCOUNT_ID"].filter((k) => !env[k]);
  if (missing.length) {
    return new Response(`/stats is not configured: set ${missing.join(", ")} on the Worker.`, {
      status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }
  if (!(await authorised(request, env.STATS_PASSWORD))) {
    return new Response("Sign in to see the numbers.", {
      status: 401,
      headers: { "WWW-Authenticate": 'Basic realm="dermaglow stats", charset="UTF-8"' },
    });
  }

  const run = async (sql) => {
    const r = await fetch(
      `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/analytics_engine/sql`,
      { method: "POST", headers: { Authorization: `Bearer ${env.CF_ANALYTICS_TOKEN}` }, body: sql },
    );
    if (!r.ok) throw new Error(`Analytics Engine ${r.status}: ${(await r.text()).slice(0, 200)}`);
    return (await r.json()).data || [];
  };

  let placements, daily, countries, byDayRaw, byPageRaw, bySourceRaw;
  try {
    [placements, daily, countries, byDayRaw, byPageRaw, bySourceRaw] = await Promise.all([
      run(SQL.placements), run(SQL.daily), run(SQL.countries),
      run(SQL.viewsByDay), run(SQL.viewsByPage), run(SQL.viewsBySource),
    ]);
  } catch (err) {
    return new Response(`Could not read the dataset — ${err.message}`, {
      status: 502, headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  const total = placements.reduce((n, r) => n + Number(r.clicks), 0);
  const byStore = {};
  for (const r of placements) byStore[r.store] = (byStore[r.store] || 0) + Number(r.clicks);

  const days = rollup(byDayRaw, (r) => `${String(r.day).slice(0, 10)}|${r.host}`)
    .map((r) => ({ ...r, day: String(r.day).slice(0, 10) }))
    .sort((a, b) => (a.day < b.day ? 1 : a.day > b.day ? -1 : a.host.localeCompare(b.host)));
  const pages = rollup(byPageRaw, (r) => `${r.host}${r.path}`);
  const sources = rollup(bySourceRaw, (r) => `${r.referrer}|${r.utm}`)
    .map((r) => ({ ...r, source: r.utm ? `${r.utm} (tag)` : r.referrer || "direct / none" }));
  // Unique visitors across the period: distinct ids over all days. An id
  // rotates daily, so a person reading on three days counts three times —
  // stated on the page rather than hidden.
  const uniqueVisitors = new Set(byDayRaw.map((r) => `${String(r.day).slice(0, 10)}|${r.visitor}`)).size;
  const pageViews = byDayRaw.reduce((n, r) => n + Number(r.views), 0);
  const posts = pages.filter((r) => /^\/posts\//.test(r.path));

  return new Response(renderStats({ total, byStore, placements, daily, countries,
    uniqueVisitors, pageViews, days, pages, posts, sources }), {
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
  });
}

async function authorised(request, password) {
  const h = request.headers.get("Authorization") || "";
  if (!h.startsWith("Basic ")) return false;
  let given;
  try { given = atob(h.slice(6)).split(":").slice(1).join(":"); } catch { return false; }
  // Constant-time compare on equal-length digests, so the length of the
  // real password is not something a timing loop can learn.
  const enc = new TextEncoder();
  const [a, b] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(given)),
    crypto.subtle.digest("SHA-256", enc.encode(password)),
  ]);
  const x = new Uint8Array(a), y = new Uint8Array(b);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

const esc = (v) => String(v ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const n = (v) => Number(v).toLocaleString("en-GB");

function renderStats({ total, byStore, placements, daily, countries,
  uniqueVisitors, pageViews, days, pages, posts, sources }) {
  const rows = (arr, cols) => arr.map((r) =>
    `<tr>${cols.map((c) => `<td class="${c === "clicks" ? "n" : ""}">${c === "clicks" ? n(r[c]) : esc(r[c]) || "<span class=dim>—</span>"}</td>`).join("")}</tr>`,
  ).join("");
  const day = (r) => ({ ...r, day: String(r.day).slice(0, 10) });
  const vv = (arr, cols) => arr.map((r) =>
    `<tr>${cols.map((c) => `<td class="${c === "visitors" || c === "views" ? "n" : ""}">${
      c === "visitors" || c === "views" ? n(r[c]) : esc(r[c]) || "<span class=dim>—</span>"}</td>`).join("")}</tr>`,
  ).join("");
  const empty = (cols) => `<tr><td colspan="${cols}" class="dim">nothing yet</td></tr>`;
  return `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Store clicks — Dermaglow</title>
<style>
:root{--night:#0B0F0D;--card:#111815;--line:#1E3229;--on:#F2F5F1;--on2:#9DB3A8;--on3:#6B7D74;--mint:#7FD1AE}
body{margin:0;background:var(--night);color:var(--on);font:15px/1.5 system-ui,-apple-system,sans-serif;padding:32px 20px 80px}
main{max-width:920px;margin:0 auto;display:grid;gap:28px}
h1{font-size:22px;margin:0;font-weight:600}h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--on3);margin:0 0 10px;font-weight:600}
.sub{color:var(--on2);margin:4px 0 0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:14px 16px}
.tile b{display:block;font-size:28px;font-weight:600;color:var(--mint);font-variant-numeric:tabular-nums}
.tile span{color:var(--on3);font-size:12px;letter-spacing:.1em;text-transform:uppercase}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:6px}
table{border-collapse:collapse;width:100%;min-width:480px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:9px 14px;border-bottom:1px solid var(--line);white-space:nowrap}
th{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--on3);font-weight:600}
tr:last-child td{border-bottom:0}td.n{text-align:right;color:var(--mint)}.dim{color:var(--on3)}
p.note{color:var(--on3);font-size:13px;margin:0}
</style>
<main>
  <div><h1>Site &amp; blog</h1><p class="sub">Last 30 days, counted server-side on every page served. No cookies: a visitor is a daily-rotating hash of address and browser, so one person over three days counts as three. Bots excluded.</p></div>
  <div class="tiles">
    <div class="tile"><b>${n(uniqueVisitors)}</b><span>unique visitors</span></div>
    <div class="tile"><b>${n(pageViews)}</b><span>page views</span></div>
  </div>
  <section><h2>Blog posts</h2><div class="wrap"><table>
    <thead><tr><th>post</th><th class="n">visitors</th><th class="n">views</th></tr></thead>
    <tbody>${vv(posts, ["path", "visitors", "views"]) || empty(3)}</tbody>
  </table></div></section>
  <section><h2>All pages</h2><div class="wrap"><table>
    <thead><tr><th>host</th><th>page</th><th class="n">visitors</th><th class="n">views</th></tr></thead>
    <tbody>${vv(pages.slice(0, 40), ["host", "path", "visitors", "views"]) || empty(4)}</tbody>
  </table></div></section>
  <section><h2>Sources</h2><div class="wrap"><table>
    <thead><tr><th>where visitors came from</th><th class="n">visitors</th><th class="n">views</th></tr></thead>
    <tbody>${vv(sources.slice(0, 30), ["source", "visitors", "views"]) || empty(3)}</tbody>
  </table></div>
  <p class="note">The referring site, or the ?utm_source / ?src tag on a link you shared. "direct / none" is a typed or pasted address, or an app that strips the referrer — most messaging apps do.</p></section>
  <section><h2>Visitors by day</h2><div class="wrap"><table>
    <thead><tr><th>day</th><th>host</th><th class="n">visitors</th><th class="n">views</th></tr></thead>
    <tbody>${vv(days, ["day", "host", "visitors", "views"]) || empty(4)}</tbody>
  </table></div></section>

  <div style="margin-top:12px"><h1>Store-button clicks</h1><p class="sub">Counted at /get/&lt;store&gt; before the visitor is sent to the store.</p></div>
  <div class="tiles">
    <div class="tile"><b>${n(total)}</b><span>all clicks</span></div>
    ${Object.entries(byStore).map(([s, c]) => `<div class="tile"><b>${n(c)}</b><span>${esc(s)}</span></div>`).join("")}
  </div>
  <section><h2>By button and page</h2><div class="wrap"><table>
    <thead><tr><th>store</th><th>button (src)</th><th>page (referrer)</th><th>device</th><th class="n">clicks</th></tr></thead>
    <tbody>${rows(placements, ["store", "src", "referrer", "device", "clicks"]) || '<tr><td colspan="5" class="dim">nothing yet</td></tr>'}</tbody>
  </table></div>
  <p class="note">src is the placement tag on the link (nav, hero, blog-cta, or whatever a shared link carries). Empty page means the link was opened directly — typed, pasted, or from an app that strips the referrer.</p></section>
  <section><h2>By day</h2><div class="wrap"><table>
    <thead><tr><th>day</th><th>store</th><th class="n">clicks</th></tr></thead>
    <tbody>${rows(daily.map(day), ["day", "store", "clicks"]) || '<tr><td colspan="3" class="dim">nothing yet</td></tr>'}</tbody>
  </table></div></section>
  <section><h2>By country</h2><div class="wrap"><table>
    <thead><tr><th>country</th><th class="n">clicks</th></tr></thead>
    <tbody>${rows(countries, ["country", "clicks"]) || '<tr><td colspan="2" class="dim">nothing yet</td></tr>'}</tbody>
  </table></div></section>
</main>`;
}
