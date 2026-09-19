# dermaglowbeauty.com

## Store-click tracking

Every "Get the app" link points at `/get/ios` (later `/get/android`) with a
`?src=` naming the placement, instead of at the store. `functions/get/[store].js`
counts the hit server-side in Workers Analytics Engine and 302s to the store —
ad-blockers cannot see it. Requires one binding on the **apex** Pages project:
Settings → Bindings → Analytics Engine → variable `STORE_CLICKS`, dataset
`store_clicks`. Without it the redirect still works and nothing is counted.

`analytics.js` (served from the apex, loaded by the site and the blog) adds
cookieless PostHog page views and a `store_click` event with the same `src`,
into the app's PostHog project, for the behaviour around the click.

Query (Cloudflare → Analytics Engine → SQL):

    SELECT blob1 AS store, blob2 AS src, blob3 AS referrer, count() AS clicks
    FROM store_clicks WHERE timestamp > NOW() - INTERVAL '30' DAY
    GROUP BY store, src, referrer ORDER BY clicks DESC
