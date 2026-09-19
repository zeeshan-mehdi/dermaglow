// Site + blog analytics. One file, served from the apex and loaded by both
// Cloudflare Pages projects, so the event names stay identical everywhere.
//
// PostHog, same project the app reports to, so web and app sit in one
// funnel view. Cookieless on purpose (persistence: "memory"): no identifier
// survives the tab, no consent banner is owed, and the numbers here are for
// ratios — which page, which placement — not for counting people. The true
// click count comes from /get/<store>, which is server-side and unblockable;
// this layer is the behaviour around it.
//
// The phc_ key is the public write-only project key, the same one shipped
// inside the app binary. Not a secret.
(function () {
  var KEY = "phc_wcLRCANWnpkAh5GDxU2zngqR6urufH9NLouTkX5asg2Y";
  var HOST = "https://us.i.posthog.com";

  // Official PostHog loader, verbatim.
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionManager persistence sessionPropsManager".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

  posthog.init(KEY, {
    api_host: HOST,
    persistence: "memory",
    disable_session_recording: true,
    capture_pageview: true,
    capture_pageleave: true,
    autocapture: false,
  });

  // store_click: any link marked data-store (the store buttons), whether
  // its href goes straight to the store or through /get/<store>. `src`
  // names the placement (data-src on the link), `page` the path it was on
  // — the same two fields the server-side row carries, so the two systems
  // reconcile by name.
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest && ev.target.closest("a[data-store]");
    if (!a) return;
    posthog.capture("store_click", {
      store: a.getAttribute("data-store"),
      src: a.getAttribute("data-src") || "direct",
      page: location.pathname,
      $send_beacon: true
    });
  }, { capture: true });
})();
