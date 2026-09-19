// /get/ios and /get/android — count the click, then send the visitor on.
//
// Every store link on the site and the blog points here instead of at the
// store directly, so the count is taken server-side: an ad-blocker cannot
// see it, and it costs the visitor one 302. Each hit is one row in the
// Workers Analytics Engine dataset bound as STORE_CLICKS (Pages project →
// Settings → Bindings → Analytics Engine → variable name STORE_CLICKS,
// dataset store_clicks). If the binding is missing the redirect still
// works and nothing is counted — the link must never break because the
// counter is unconfigured.
//
// Query it in the Cloudflare dashboard (Analytics Engine → SQL):
//   SELECT blob1 AS store, blob2 AS src, count() AS clicks
//   FROM store_clicks WHERE timestamp > NOW() - INTERVAL '30' DAY
//   GROUP BY store, src ORDER BY clicks DESC
//
// `src` is set by the link itself (?src=hero, nav, blog-cta …) and names
// the placement; the referrer names the page. Together they answer "which
// button, on which page, from where".

const STORES = {
  ios: "https://apps.apple.com/app/id6790204292",
  android: "https://play.google.com/store/apps/details?id=com.app.dermaglow",
};

// A stable, short label for the client, without the user agent itself —
// the UA string is high-cardinality and not something worth storing per click.
function deviceClass(ua) {
  if (/iPhone|iPad|iPod/i.test(ua)) return "ios";
  if (/Android/i.test(ua)) return "android";
  if (/bot|crawl|spider|preview|facebookexternalhit|Slackbot|WhatsApp/i.test(ua)) return "bot";
  return "desktop";
}

export async function onRequestGet({ request, params, env }) {
  const store = String(params.store || "").toLowerCase();
  const target = STORES[store];
  if (!target) return new Response("Not found", { status: 404 });

  const url = new URL(request.url);
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
