// Server-side page-view counting, shared by the apex Worker and the blog
// Worker so both hosts land in one dataset with one schema.
//
// One row per HTML page served: host, path, referrer host, country, device
// class, a visitor id and the utm_source if the link carried one. The
// visitor id is SHA-256(salt · UTC date · IP · user agent), truncated — it
// tells two views apart from one person on the same day and nothing more.
// It rotates at midnight UTC, is never stored with the IP, and cannot be
// turned back into one without the salt. No cookie, so nothing to consent
// to. "Unique visitors" here means "distinct ids that day".
//
// Dataset: page_views (binding PAGE_VIEWS). Blobs, in order:
//   1 host  2 path  3 referrer host  4 country  5 device  6 visitor  7 utm_source

export function deviceClass(ua) {
  if (/iPhone|iPad|iPod/i.test(ua)) return "ios";
  if (/Android/i.test(ua)) return "android";
  if (/bot|crawl|spider|preview|facebookexternalhit|Slackbot|WhatsApp|HeadlessChrome|Lighthouse/i.test(ua)) return "bot";
  return "desktop";
}

async function visitorId(request, salt) {
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const ua = request.headers.get("User-Agent") || "";
  const day = new Date().toISOString().slice(0, 10);
  const bytes = new TextEncoder().encode(`${salt}|${day}|${ip}|${ua}`);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest).slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Call after the asset response is known; counts only real HTML page loads. */
export async function trackPageView(request, response, env) {
  if (!env.PAGE_VIEWS || request.method !== "GET" || response.status !== 200) return;
  if (!(response.headers.get("Content-Type") || "").includes("text/html")) return;
  // Prefetches and prerenders are the browser guessing, not a person reading.
  if (/prefetch|prerender/i.test(request.headers.get("Sec-Purpose") || request.headers.get("Purpose") || "")) return;
  const ua = request.headers.get("User-Agent") || "";
  const device = deviceClass(ua);
  if (device === "bot") return;

  const url = new URL(request.url);
  let referrerHost = "";
  try { referrerHost = new URL(request.headers.get("Referer") || "").host; } catch { /* none */ }
  // A visit from our own pages is navigation, not a source.
  if (referrerHost === url.host) referrerHost = "";
  const utm = (url.searchParams.get("utm_source") || url.searchParams.get("src") || "").slice(0, 40);
  const country = request.headers.get("CF-IPCountry") || "";
  const visitor = await visitorId(request, env.VISITOR_SALT || "dermaglow");
  const path = url.pathname.replace(/\/index\.html$/, "/").slice(0, 120);

  try {
    env.PAGE_VIEWS.writeDataPoint({
      blobs: [url.host, path, referrerHost, country, device, visitor, utm],
      doubles: [1],
      indexes: [url.host],
    });
  } catch { /* best-effort */ }
}
