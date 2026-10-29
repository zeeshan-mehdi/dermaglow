// Updraft Labs — site behaviour
// Change CONTACT_EMAIL once the domain's mailbox is set up; every
// [data-email] link and the contact form use it.
const CONTACT_EMAIL = "hello@updraftlabs.ai";

document.documentElement.classList.add("js");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

document.querySelectorAll("[data-email]").forEach((a) => {
  a.href = "mailto:" + CONTACT_EMAIL;
  a.textContent = CONTACT_EMAIL;
});
const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

// ---------- nav ----------
const toggle = document.querySelector(".nav-toggle");
const menu = document.getElementById("mobile-menu");
if (toggle && menu) {
  const setMenu = (open) => {
    toggle.setAttribute("aria-expanded", open);
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menu.hidden = !open;
  };
  toggle.addEventListener("click", () => setMenu(menu.hidden));
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
}

// ---------- reveal on scroll ----------
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      io.unobserve(e.target);
    });
  },
  { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
);
document.querySelectorAll(".reveal").forEach((el) => {
  // stagger siblings that reveal together
  const sibs = [...el.parentElement.children].filter((c) => c.classList.contains("reveal"));
  el.style.setProperty("--d", Math.min(sibs.indexOf(el), 6) * 0.07 + "s");
  io.observe(el);
});

// ---------- where AI fits ----------
if (document.querySelector(".fits-panel")) {
const FITS = {
  ops: {
    before: "Staff re-key data from emails and PDFs into three different systems, and orders wait days for a manual approval.",
    after: "Documents are read and validated automatically, routine approvals clear themselves, and people only see the exceptions.",
    how: "→ document AI · rules engine · system integrations",
  },
  support: {
    before: "Agents dig through old tickets, wikis and policy PDFs to answer the same questions every day.",
    after: "An assistant drafts accurate, cited answers from your own knowledge base; agents review, send and move on.",
    how: "→ RAG over docs & tickets · helpdesk integration",
  },
  sales: {
    before: "Reps spend their mornings researching leads and writing follow-ups by hand, and the CRM is always out of date.",
    after: "Leads arrive enriched and scored, follow-ups are drafted in your voice, and the CRM updates itself after every call.",
    how: "→ enrichment agents · call summaries · CRM sync",
  },
  finance: {
    before: "Invoices are matched to purchase orders line by line, and month-end close takes a week of spreadsheets.",
    after: "Invoices are extracted and matched automatically, anomalies are flagged, and reports build themselves.",
    how: "→ extraction pipelines · 3-way matching · dashboards",
  },
  marketing: {
    before: "Content calendars slip, competitor moves are noticed weeks late, and nobody knows which campaign actually worked.",
    after: "On-brand drafts in minutes, a daily competitor digest, and attribution you can trust.",
    how: "→ content workflows · market monitoring · analytics",
  },
  people: {
    before: "Hundreds of CVs screened by hand, and new hires spend weeks asking where things are.",
    after: "Candidates are shortlisted against clear criteria, and new hires ask an onboarding assistant that knows your company.",
    how: "→ screening assistants · internal knowledge bot",
  },
};
const tabs = document.querySelectorAll(".fits-tabs button");
const panel = document.querySelector(".fits-panel");
const showFit = (key) => {
  const f = FITS[key];
  document.getElementById("fit-before").textContent = f.before;
  document.getElementById("fit-after").textContent = f.after;
  document.getElementById("fit-how").textContent = f.how;
};
tabs.forEach((t) =>
  t.addEventListener("click", () => {
    if (t.getAttribute("aria-selected") === "true") return;
    tabs.forEach((x) => x.setAttribute("aria-selected", x === t));
    if (reduceMotion) return showFit(t.dataset.fit);
    panel.classList.add("swap");
    setTimeout(() => {
      showFit(t.dataset.fit);
      panel.classList.remove("swap");
    }, 220);
  })
);
showFit("ops");

}

// ---------- contact form ----------
if (document.getElementById("contact-form")) {
// Posts to /api/contact (functions/api/contact.js). If that isn't set up
// yet, or fails, the message opens in the visitor's email app instead.
const form = document.getElementById("contact-form");
const note = document.getElementById("form-note");
const setNote = (msg, err) => {
  note.className = "form-note" + (err ? " err" : "");
  note.textContent = msg;
};
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  let ok = true;
  form.querySelectorAll("[required]").forEach((f) => {
    const bad = !f.value.trim() || (f.type === "email" && !/^\S+@\S+\.\S+$/.test(f.value));
    f.classList.toggle("invalid", bad);
    if (bad) ok = false;
  });
  if (!ok) return setNote("Please add your name, a valid email and a short message.", true);

  const d = new FormData(form);
  const data = {
    name: d.get("name"),
    email: d.get("email"),
    company: d.get("company"),
    interests: d.getAll("interest"),
    message: d.get("message"),
    website: d.get("website"),
  };
  const btn = form.querySelector("button[type=submit]");
  btn.disabled = true;
  setNote("Sending…");
  try {
    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(data),
    });
    if (res.ok) {
      form.reset();
      return setNote("Thanks — message received. We'll reply within one business day.");
    }
    if (res.status === 422) return setNote("Please check your details and try again.", true);
  } catch {
    // network error: fall through to email
  } finally {
    btn.disabled = false;
  }
  const subject = `New project enquiry — ${data.company || data.name}`;
  const body = [
    `Name: ${data.name}`,
    `Email: ${data.email}`,
    `Company: ${data.company || "—"}`,
    `Interested in: ${data.interests.join(", ") || "—"}`,
    "",
    data.message,
  ].join("\n");
  location.href = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  setNote(`Opening your email app… If nothing happens, write to ${CONTACT_EMAIL}.`);
});
form.addEventListener("input", (e) => e.target.classList.remove("invalid"));

}

// ---------- Fig. 01: the wind tunnel ----------
// Flat, broken lines (drag) meet the slice, square to the logo's 2:5 rising
// line, and come out lifted, solid and coloured. The pointer is a thermal.
document.querySelectorAll("canvas[data-tunnel], #tunnel").forEach((canvas) => {
  const ctx = canvas.getContext("2d");
  const INK = "#121211", ORANGE = "#FF5A1F";
  const LIFT_COLS = ["#0E9F79", "#13B48A", "#2BC9A0", "#2443D6", "#3B5BE0", "#1A34B0"];
  const TAN = 0.4;
  const lost = canvas.dataset.tunnel === "lost"; // 404: lines fall instead of rising
  let W, H, dpr, raf = 0, visible = true, start = performance.now();
  const mouse = { x: -1e4, y: -1e4, tx: -1e4, ty: -1e4 };

  const size = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  const ease = (t) => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 4);

  const draw = (now) => {
    const t = (now - start) / 1000;
    mouse.x += (mouse.tx - mouse.x) * 0.12; mouse.y += (mouse.ty - mouse.y) * 0.12;
    ctx.clearRect(0, 0, W, H);

    // skew grid on the rising angle
    ctx.strokeStyle = "rgba(18,18,17,.07)"; ctx.lineWidth = 1;
    for (let k = -H; k < W + H; k += 44) { ctx.beginPath(); ctx.moveTo(k, H); ctx.lineTo(k + H / TAN, 0); ctx.stroke(); }

    const n = Math.max(14, Math.min(28, Math.round(H / 26)));
    const top = H * 0.14, bot = H * 0.9, gap = (bot - top) / (n - 1);
    const cx = W * (lost ? 0.42 : 0.47), cy = (top + bot) / 2;
    const lift = gap * 3.2 * ease((t - 0.3) / 1.6) * (lost ? -1 : 1);
    const breathe = reduceMotion ? 0 : Math.sin(t * 0.8) * gap * 0.25;

    for (let i = 0; i < n; i++) {
      const y = top + i * gap;
      const xs = cx + (y - cy) * TAN;
      const major = i % 4 === 0;
      const w = major ? 2.6 : 1.3;
      // drag: flat ink, broken, flowing
      ctx.strokeStyle = INK; ctx.lineWidth = w;
      ctx.setLineDash(major ? [] : [22 + (i % 3) * 6, 6]);
      ctx.lineDashOffset = reduceMotion ? 0 : -t * (34 + (i % 3) * 10);
      ctx.beginPath(); ctx.moveTo(-10, y); ctx.lineTo(xs - 5, y); ctx.stroke();
      ctx.setLineDash([]);
      // lift: solid, coloured, raised; a thermal under the pointer
      const col = i === Math.round(n * 0.6) ? ORANGE : LIFT_COLS[Math.min(LIFT_COLS.length - 1, Math.floor((i / n) * LIFT_COLS.length))];
      ctx.strokeStyle = col; ctx.lineWidth = w + 1.2;
      ctx.beginPath();
      for (let px = xs + 5; px <= W + 12; px += 6) {
        const yl = y - lift - breathe * ((px - xs) / W);
        const dx = px - mouse.x, dy = yl - mouse.y;
        const thermal = Math.exp(-(dx * dx + dy * dy) / (2 * 78 * 78)) * 30 * (lost ? -1 : 1);
        const yy = yl - thermal;
        px === xs + 5 ? ctx.moveTo(px, yy) : ctx.lineTo(px, yy);
      }
      ctx.stroke();
    }
    // the slice
    ctx.strokeStyle = ORANGE; ctx.lineWidth = 1.4; ctx.setLineDash([6, 5]);
    ctx.beginPath(); ctx.moveTo(cx + (top - 40 - cy) * TAN, top - 40); ctx.lineTo(cx + (bot + 40 - cy) * TAN, bot + 40); ctx.stroke();
    ctx.setLineDash([]);
    raf = visible && !(reduceMotion && t > 2.2) ? requestAnimationFrame(draw) : 0;
  };

  size();
  addEventListener("resize", () => { size(); if (!raf) raf = requestAnimationFrame(draw); });
  const host = canvas.parentElement;
  host.addEventListener("pointermove", (e) => {
    const r = canvas.getBoundingClientRect();
    mouse.tx = e.clientX - r.left; mouse.ty = e.clientY - r.top;
    if (mouse.x < -1e3) { mouse.x = mouse.tx; mouse.y = mouse.ty; }
    if (!raf) raf = requestAnimationFrame(draw);
  });
  host.addEventListener("pointerleave", () => { mouse.tx = mouse.ty = -1e4; mouse.x = mouse.y = -1e4; });
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible && !raf) raf = requestAnimationFrame(draw);
  }).observe(canvas);
});
