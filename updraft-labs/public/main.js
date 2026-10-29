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
const nav = document.getElementById("nav");
if (nav) {
  const onScroll = () => nav.classList.toggle("scrolled", scrollY > 8);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}
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
