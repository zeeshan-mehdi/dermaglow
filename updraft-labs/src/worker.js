// updraft — static site from public/, plus the contact-form endpoint.
// Only /api/* reaches this script (run_worker_first in wrangler.jsonc); every
// other request is answered by the asset layer directly.
import { handleContact } from "./contact.js";

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/contact") {
      if (request.method !== "POST") return new Response("Method not allowed", { status: 405, headers: { allow: "POST" } });
      return handleContact(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};
