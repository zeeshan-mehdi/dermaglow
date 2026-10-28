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
document.getElementById("year").textContent = new Date().getFullYear();

// ---------- nav ----------
const nav = document.getElementById("nav");
const onScroll = () => nav.classList.toggle("scrolled", scrollY > 20);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

const toggle = document.querySelector(".nav-toggle");
const menu = document.getElementById("mobile-menu");
const setMenu = (open) => {
  toggle.setAttribute("aria-expanded", open);
  toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  menu.hidden = !open;
  nav.classList.toggle("scrolled", open || scrollY > 20);
};
toggle.addEventListener("click", () => setMenu(menu.hidden));
menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));

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
  el.style.setProperty("--d", Math.min(sibs.indexOf(el), 6) * 0.08 + "s");
  io.observe(el);
});

// ---------- pointer glow on cards ----------
document.querySelectorAll("[data-glow]").forEach((el) => {
  el.addEventListener("pointermove", (e) => {
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", e.clientX - r.left + "px");
    el.style.setProperty("--my", e.clientY - r.top + "px");
  });
});

// ---------- where AI fits ----------
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

// ---------- contact form ----------
// The site is static, so the form composes an email in the visitor's mail app.
const form = document.getElementById("contact-form");
const note = document.getElementById("form-note");
form.addEventListener("submit", (e) => {
  e.preventDefault();
  let ok = true;
  form.querySelectorAll("[required]").forEach((f) => {
    const bad = !f.value.trim() || (f.type === "email" && !/^\S+@\S+\.\S+$/.test(f.value));
    f.classList.toggle("invalid", bad);
    if (bad) ok = false;
  });
  if (!ok) {
    note.className = "form-note err";
    note.textContent = "Please add your name, a valid email and a short message.";
    return;
  }
  const d = new FormData(form);
  const interests = d.getAll("interest").join(", ") || "—";
  const subject = `New project enquiry — ${d.get("company") || d.get("name")}`;
  const body = [
    `Name: ${d.get("name")}`,
    `Email: ${d.get("email")}`,
    `Company: ${d.get("company") || "—"}`,
    `Interested in: ${interests}`,
    "",
    d.get("message"),
  ].join("\n");
  location.href = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  note.className = "form-note";
  note.textContent = `Opening your email app… If nothing happens, write to ${CONTACT_EMAIL}.`;
});
form.addEventListener("input", (e) => e.target.classList.remove("invalid"));

// ---------- hero: rising air ----------
(() => {
  const canvas = document.getElementById("sky");
  const ctx = canvas.getContext("2d");
  const COLORS = ["91,140,255", "125,211,252", "134,245,207", "190,170,255"];
  let w, h, dpr, parts, stars, raf, visible = true;
  const mouse = { x: -9999, y: -9999 };

  const makePart = (seedY) => ({
    x: Math.random() * w,
    y: seedY ? Math.random() * h : h + Math.random() * 80,
    v: 0.35 + Math.random() * 1.1,
    amp: 6 + Math.random() * 22,
    freq: 0.004 + Math.random() * 0.006,
    phase: Math.random() * Math.PI * 2,
    c: COLORS[(Math.random() * COLORS.length) | 0],
    trail: [],
    len: 14 + ((Math.random() * 22) | 0),
  });

  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    w = canvas.clientWidth;
    h = canvas.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.round(Math.min(160, (w * h) / 9000));
    parts = Array.from({ length: n }, () => makePart(true));
    stars = Array.from({ length: Math.round(n * 0.7) }, () => ({
      x: Math.random() * w, y: Math.random() * h * 0.8, r: Math.random() * 1.1 + 0.2, p: Math.random() * 6,
    }));
  };

  const frame = (t) => {
    ctx.clearRect(0, 0, w, h);
    for (const s of stars) {
      const a = 0.15 + 0.35 * (0.5 + 0.5 * Math.sin(t * 0.001 + s.p));
      ctx.fillStyle = `rgba(220,230,255,${a})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, 6.283);
      ctx.fill();
    }
    const cx = w / 2;
    ctx.lineCap = "round";
    for (const p of parts) {
      // rise faster near the centre column, curl as you climb
      const centre = 1 - Math.min(Math.abs(p.x - cx) / (w * 0.6), 1);
      p.y -= p.v * (1 + centre * 1.4);
      p.x += Math.sin(p.y * p.freq + p.phase + t * 0.0004) * 0.5 + (cx - p.x) * 0.0006;
      const dx = p.x - mouse.x, dy = p.y - mouse.y, dd = dx * dx + dy * dy;
      if (dd < 22000) { const f = (1 - dd / 22000) * 2.2; p.x += (dx / Math.sqrt(dd + 1)) * f; }
      const drawX = p.x + Math.sin(p.y * p.freq * 0.5 + p.phase) * p.amp;
      p.trail.push(drawX, p.y);
      if (p.trail.length > p.len * 2) p.trail.splice(0, 2);
      const fade = Math.min(1, p.y / (h * 0.35)) * Math.min(1, (h - p.y + 60) / 120);
      if (p.trail.length > 4) {
        ctx.strokeStyle = `rgba(${p.c},${0.55 * fade})`;
        ctx.lineWidth = 0.6 + p.v * 0.7;
        ctx.beginPath();
        ctx.moveTo(p.trail[0], p.trail[1]);
        for (let i = 2; i < p.trail.length; i += 2) ctx.lineTo(p.trail[i], p.trail[i + 1]);
        ctx.stroke();
        ctx.fillStyle = `rgba(${p.c},${0.9 * fade})`;
        ctx.beginPath();
        ctx.arc(drawX, p.y, 0.6 + p.v * 0.6, 0, 6.283);
        ctx.fill();
      }
      if (p.y < -40) Object.assign(p, makePart(false));
    }
    raf = visible ? requestAnimationFrame(frame) : 0;
  };

  resize();
  addEventListener("resize", () => { cancelAnimationFrame(raf); resize(); if (visible) raf = requestAnimationFrame(frame); });
  canvas.parentElement.addEventListener("pointermove", (e) => {
    const r = canvas.getBoundingClientRect();
    mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
  });
  canvas.parentElement.addEventListener("pointerleave", () => { mouse.x = mouse.y = -9999; });

  if (reduceMotion) {
    // a single still frame after letting the trails form
    visible = false;
    for (let i = 0; i < 60; i++) frame(i * 16);
    return;
  }
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible && !raf) raf = requestAnimationFrame(frame);
  }).observe(canvas);
})();
