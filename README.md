# dermaglowbeauty.com

## Store-click tracking

The apex is a **Worker with static assets** (`wrangler.jsonc`), deployed by
Cloudflare's Git-connected Workers Build on every push to `main`. The deploy
command there must be plain `npx wrangler deploy` — the config file carries the
assets directory, the script and the bindings.

Store buttons carry `data-store`/`data-src`; their hrefs can point at
`/get/ios` (later `/get/android`) with `?src=` naming the placement instead of
at the store. `src/worker.js` counts the hit server-side in Workers Analytics
Engine (dataset `store_clicks`, binding `STORE_CLICKS`, declared in
`wrangler.jsonc`) and 302s to the store — ad-blockers cannot see it. If the
binding is missing the redirect still works and nothing is counted.

`analytics.js` (served from the apex, loaded by the site and the blog) adds
cookieless PostHog page views and a `store_click` event with the same `src`,
into the app's PostHog project, for the behaviour around the click.

**Reading the numbers:** `https://dermaglowbeauty.com/stats` (HTTP Basic, any
username, password = the `STATS_PASSWORD` secret). Needs two Worker secrets set
in the dashboard (Workers & Pages → dermaglow → Settings → Variables and
Secrets): `STATS_PASSWORD` and `CF_ANALYTICS_TOKEN` (an API token with
Account · Account Analytics · Read). Or query the SQL API directly:

    SELECT blob1 AS store, blob2 AS src, blob3 AS referrer, SUM(_sample_interval) AS clicks
    FROM store_clicks WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY store, src, referrer ORDER BY clicks DESC
