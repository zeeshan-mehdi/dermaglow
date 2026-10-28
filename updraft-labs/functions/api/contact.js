// POST /api/contact — emails a contact-form submission via Resend.
//
// Needs the RESEND_API_KEY secret (Pages project → Settings → Variables and
// Secrets) and a sending domain verified in Resend. CONTACT_TO / CONTACT_FROM
// come from wrangler.toml. Without the key it answers 503 and the page falls
// back to opening the visitor's email app.

const LIMITS = { name: 120, email: 200, company: 160, message: 5000 };

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

export async function onRequestPost({ request, env }) {
  if (!env.RESEND_API_KEY) return json({ ok: false, error: "not_configured" }, 503);

  let d;
  try {
    d = await request.json();
  } catch {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  // Bots fill the hidden "website" field; pretend it worked.
  if (d.website) return json({ ok: true });

  const f = {};
  for (const [k, max] of Object.entries(LIMITS)) f[k] = String(d[k] ?? "").trim().slice(0, max);
  const interests = (Array.isArray(d.interests) ? d.interests : []).map(String).slice(0, 10).join(", ");
  if (!f.name || !f.message || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email)) {
    return json({ ok: false, error: "invalid" }, 422);
  }

  const rows = [["Name", f.name], ["Email", f.email], ["Company", f.company || "—"], ["Interested in", interests || "—"]];
  const htmlBody =
    `<table>${rows.map(([k, v]) => `<tr><td><b>${k}</b></td><td>${esc(v)}</td></tr>`).join("")}</table>` +
    `<p style="white-space:pre-wrap">${esc(f.message)}</p>` +
    `<p style="color:#888">Sent from the contact form · ${esc(request.headers.get("cf-ipcountry") || "")}</p>`;

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({
      from: `Updraft Labs website <${env.CONTACT_FROM}>`,
      to: [env.CONTACT_TO],
      reply_to: f.email,
      subject: `New enquiry — ${f.company || f.name}`,
      html: htmlBody,
      text: rows.map(([k, v]) => `${k}: ${v}`).join("\n") + "\n\n" + f.message,
    }),
  });
  if (!res.ok) {
    console.log("resend failed", res.status, await res.text());
    return json({ ok: false, error: "send_failed" }, 502);
  }
  return json({ ok: true });
}
