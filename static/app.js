// Coding Practice — single-page frontend. No build step; plain ES modules.

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const main = $("#main");

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pct = (x) => `${Math.round(x * 100)}%`;
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
  if (res.status === 401 && !path.startsWith("/auth/")) { showLogin(); throw Object.assign(new Error("Please sign in."), { status: 401 }); }
  if (!res.ok) throw Object.assign(new Error(data.error || `HTTP ${res.status}`), { status: res.status });
  return data;
}

// ------------------------------------------------------------------ accounts (shared mode)

let me = { multi_user: false, user: null };

function showLogin() {
  document.body.classList.add("signed-out");
  const signup = me.signup;
  main.innerHTML = `<div class="page"><div class="card auth-card">
    <h1 style="margin-top:0">Coding Practice</h1>
    <p class="sub">Sign in to continue where you left off. Your progress is private to your account.</p>
    <div class="tabs auth-tabs">${signup ? `<button class="tab active" data-m="login">Sign in</button><button class="tab" data-m="signup">Create account</button>` : ""}</div>
    <form id="auth-form" autocomplete="on">
      <label>Username<input name="username" autocomplete="username" required minlength="3" maxlength="24" pattern="[a-z0-9_]+" title="lowercase letters, digits or _"></label>
      <label>Password<input name="password" type="password" autocomplete="current-password" required minlength="8"></label>
      <label class="invite" hidden>Invite code<input name="invite" autocomplete="off"></label>
      <button class="btn primary" type="submit">Sign in</button>
      <div class="auth-err" role="alert"></div>
    </form></div></div>`;
  let mode = "login";
  const form = $("#auth-form");
  for (const b of $$(".auth-tabs .tab")) b.addEventListener("click", () => {
    mode = b.dataset.m;
    $$(".auth-tabs .tab").forEach((x) => x.classList.toggle("active", x === b));
    $(".invite", form).hidden = mode !== "signup";
    $("input[name=invite]", form).required = mode === "signup";
    form.password.autocomplete = mode === "signup" ? "new-password" : "current-password";
    $("button[type=submit]", form).textContent = mode === "signup" ? "Create account" : "Sign in";
  });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(form));
    body.username = (body.username || "").trim().toLowerCase();
    try {
      await api(`/auth/${mode}`, { method: "POST", body });
      me = await api("/auth/me");
      document.body.classList.remove("signed-out");
      renderUserFoot();
      router();
    } catch (err) { $(".auth-err", form).textContent = err.message; }
  });
}

function renderUserFoot() {
  const foot = $(".sidebar-foot");
  $("#user-foot")?.remove();
  if (!me.multi_user || !me.user) return;
  foot.insertAdjacentHTML("afterbegin", `<span id="user-foot" class="foot-link" title="Signed in">${esc(me.user)} · <a href="#" id="sign-out">Sign out</a></span>`);
  $("#sign-out").addEventListener("click", async (e) => {
    e.preventDefault();
    await api("/auth/logout", { method: "POST", body: {} }).catch(() => {});
    me.user = null;
    renderUserFoot();
    showLogin();
  });
}

let toastTimer;
function toast(msg, kind = "") {
  const t = $("#toast");
  t.textContent = msg;
  t.className = `show ${kind}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = ""), 2600);
}

function timeAgo(iso) {
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  if (s < 86400 * 7) return `${Math.floor(s / 86400)}d ago`;
  return new Date(iso).toLocaleDateString();
}

function store(key, val) {
  try {
    if (val === undefined) return JSON.parse(localStorage.getItem(key));
    localStorage.setItem(key, JSON.stringify(val));
  } catch (e) { return null; }
}

// ------------------------------------------------------------------ markdown

const slug = (s) => s.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^\w]+/g, "-").replace(/^-|-$/g, "");
const CALLOUTS = {
  NOTE: ["note", "Note"], TIP: ["tip", "Tip"], WARNING: ["warning", "Watch out"],
  DANGER: ["danger", "Common mistake"], EXAM: ["exam", "Exam-ready answer"],
  INTERVIEW: ["interview", "Interview question"], SYNTAX: ["syntax", "Syntax"],
  DEFINITION: ["exam", "Definition"], KEY: ["note", "Key idea"],
};

const renderer = new marked.Renderer();
renderer.code = function ({ text, lang }) {
  lang = (lang || "").trim().split(/\s+/)[0];
  if (lang === "mermaid") return `<div class="mermaid">${esc(text)}</div>`;
  let html;
  try {
    html = lang && hljs.getLanguage(lang) ? hljs.highlight(text, { language: lang }).value : esc(text);
  } catch (e) { html = esc(text); }
  const tag = lang && !["text", "plain", "output"].includes(lang) ? `<span class="lang-tag">${esc(lang)}</span>` : "";
  return `<pre>${tag}<code class="hljs">${html}</code></pre>`;
};
marked.use({ renderer, gfm: true });

let mermaidLoading = null;
function loadMermaid() {
  if (!mermaidLoading) {
    mermaidLoading = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = "/vendor/mermaid.min.js";
      s.onload = () => resolve(window.mermaid);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  return mermaidLoading;
}

function md(src) {
  return marked.parse(src || "");
}

async function renderMarkdown(el, src) {
  el.innerHTML = md(src);
  // GitHub-style callouts: > [!EXAM] ...
  for (const bq of $$("blockquote", el)) {
    const first = bq.firstElementChild;
    const m = first && first.innerHTML.match(/^\s*\[!(\w+)\]\s*(.*)/s);
    if (!m) continue;
    const [cls, label] = CALLOUTS[m[1].toUpperCase()] || ["note", m[1]];
    const rest = m[2].replace(/^<br>\s*/, "");
    let title = label;
    // "[!TIP] Custom title" on the first line overrides the label
    const nl = rest.indexOf("\n");
    const firstLine = nl === -1 ? rest : rest.slice(0, nl);
    let body = rest;
    if (firstLine.trim() && !firstLine.includes("<") && firstLine.length < 80 && nl !== -1) {
      title = firstLine.trim();
      body = rest.slice(nl + 1);
    }
    first.innerHTML = body;
    if (!first.innerHTML.trim()) first.remove();
    const div = document.createElement("div");
    div.className = `callout callout-${cls}`;
    div.innerHTML = `<div class="callout-title">${esc(title)}</div>`;
    div.append(...bq.childNodes);
    bq.replaceWith(div);
  }
  const seen = {};
  for (const h of $$("h2, h3", el)) {
    let id = slug(h.textContent) || "section";
    seen[id] = (seen[id] || 0) + 1;
    if (seen[id] > 1) id += `-${seen[id]}`;
    h.id = id;
  }
  const nodes = $$(".mermaid", el);
  if (nodes.length) {
    try {
      const mm = await loadMermaid();
      if (!el.isConnected) return;     // the page changed while mermaid was loading
      const dark = (document.documentElement.dataset.theme || "dark") === "dark";
      mm.initialize({ startOnLoad: false, theme: dark ? "dark" : "default", securityLevel: "loose", fontFamily: "Inter, system-ui, sans-serif" });
      await mm.run({ nodes });
    } catch (e) { console.warn("mermaid", e); }
  }
}

// ------------------------------------------------------------------ sidebar

let languages = [];

async function refreshSidebar() {
  try { languages = await api("/languages"); } catch (e) { languages = []; }
  const route = location.hash.slice(2).split("/");
  const activeLang = ["lang", "topic", "problem", "milestone", "review", "problems"].includes(route[0]) ? route[1] : null;
  $("#nav").innerHTML = [
    `<a class="nav-item ${!route[0] ? "active" : ""}" href="#/">${icon("home")} Dashboard</a>`,
    ...languages.map((l) => `
      <a class="nav-item ${activeLang === l.id ? "active" : ""}" href="#/lang/${l.id}">
        <span class="lang-badge" style="background:${l.color}">${esc(l.icon)}</span> ${esc(l.name)}
        <span class="pct">${Math.round(l.pct)}%</span>
      </a>`),
  ].join("");
  const totalDone = languages.reduce((a, l) => a + l.plan.done_today, 0);
  const totalTarget = languages.reduce((a, l) => a + l.plan.target, 0);
  $("#today").innerHTML = `
    <div class="side-title"><span>Today's target</span><span>${totalDone}/${totalTarget}</span></div>
    ${languages.map((l) => {
      const p = l.plan;
      const ratio = p.target ? Math.min(1, p.done_today / p.target) : 1;
      const left = Math.max(0, p.target - p.done_today);
      const sub = l.with_content === 0 ? "No content yet"
        : p.remaining === 0 && p.target === 0 ? "Everything available is done"
        : left === 0 ? "Target met — keep going if you can"
        : `${plural(left, "task")} to go${p.avg != null ? ` · pace ${p.avg}/day` : ""}`;
      return `<a class="today-card" href="#/lang/${l.id}">
        <div class="today-row"><span>${esc(l.name)}</span><b>${p.done_today} / ${p.target}</b></div>
        <div class="bar ${ratio >= 1 ? "" : "blue"}"><span style="width:${ratio * 100}%"></span></div>
        <div class="today-sub">${sub}</div>
      </a>`;
    }).join("")}`;
}

function icon(name) {
  const paths = {
    home: "M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
    lock: "M6 10V8a6 6 0 0 1 12 0v2h1v11H5V10zm2 0h8V8a4 4 0 0 0-8 0z",
    check: "M5 12.5 10 17l9-10",
  };
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="${name === "check" ? "none" : "currentColor"}" stroke="${name === "check" ? "currentColor" : "none"}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="${paths[name]}"/></svg>`;
}

// ------------------------------------------------------------------ router

let cleanup = null;
const routes = [
  [/^$/, viewDashboard],
  [/^lang\/([\w-]+)$/, viewLanguage],
  [/^topic\/([\w-]+)\/([\w-]+)(?:\/(lesson|quiz|problems))?$/, viewTopic],
  [/^problem\/([\w-]+)\/([\w.-]+)$/, viewProblem],
  [/^milestone\/([\w-]+)\/(\d)$/, viewMilestone],
  [/^review\/([\w-]+)$/, viewReview],
  [/^problems\/([\w-]+)$/, viewProblems],
  [/^settings$/, viewSettings],
];

async function router() {
  if (cleanup) { try { await cleanup(); } catch (e) {} cleanup = null; }
  if (me.multi_user && !me.user) return showLogin();
  const path = location.hash.replace(/^#\/?/, "");
  refreshSidebar();
  for (const [re, fn] of routes) {
    const m = path.match(re);
    if (m) {
      main.innerHTML = `<div class="loading">Loading…</div>`;
      main.scrollTop = 0;
      try { await fn(...m.slice(1)); } catch (e) { showError(e); }
      return;
    }
  }
  main.innerHTML = `<div class="page"><div class="empty"><h3>Page not found</h3><a href="#/">Back to dashboard</a></div></div>`;
}

function showError(e) {
  console.error(e);
  main.innerHTML = `<div class="page"><div class="empty"><h3>${e.status === 403 ? "Locked" : "Something went wrong"}</h3>
    <p>${esc(e.message)}</p><a class="btn" href="javascript:history.back()">Go back</a></div></div>`;
}

window.addEventListener("hashchange", router);

// ------------------------------------------------------------------ heatmap

function heatLevel(n) {
  if (!n) return 0;
  if (n < 5) return 1;
  if (n < 12) return 2;
  if (n < 25) return 3;
  return 4;
}

function heatmapSVG(hm) {
  const cell = 11, gap = 3, top = 18, left = 30;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const start = new Date(today);
  start.setDate(start.getDate() - 52 * 7 - today.getDay());
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  let rects = "", months = "", lastMonth = -1;
  const d = new Date(start);
  let col = 0;
  while (d <= today) {
    const row = d.getDay();
    if (row === 0 && d.getDate() <= 7 && d.getMonth() !== lastMonth) {
      lastMonth = d.getMonth();
      months += `<text x="${left + col * (cell + gap)}" y="10">${d.toLocaleString("en", { month: "short" })}</text>`;
    }
    const k = iso(d);
    const c = hm.cells[k] || { total: 0 };
    rects += `<rect class="cell" data-day="${k}" x="${left + col * (cell + gap)}" y="${top + row * (cell + gap)}" width="${cell}" height="${cell}" fill="var(--heat-${heatLevel(c.total)})"/>`;
    if (row === 6) col++;
    d.setDate(d.getDate() + 1);
  }
  const days = ["", "Mon", "", "Wed", "", "Fri", ""].map((t, i) => t ? `<text x="0" y="${top + i * (cell + gap) + 9}">${t}</text>` : "").join("");
  const w = left + (col + 1) * (cell + gap);
  return `<svg width="${w}" height="${top + 7 * (cell + gap)}" role="img" aria-label="Activity heatmap">${months}${days}${rects}</svg>`;
}

function bindHeatTips(root, hm) {
  let tip;
  root.addEventListener("mouseover", (e) => {
    const r = e.target.closest("rect.cell");
    if (!r) return;
    const c = hm.cells[r.dataset.day] || { total: 0 };
    const date = new Date(r.dataset.day + "T00:00").toLocaleDateString("en", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
    const parts = [];
    if (c.lesson_read) parts.push(plural(c.lesson_read, "lesson"));
    if (c.mcq_answer) parts.push(plural(c.mcq_answer, "MCQ"));
    if (c.submission) parts.push(plural(c.submission, "submission"));
    tip = tip || Object.assign(document.createElement("div"), { className: "heat-tip" });
    tip.innerHTML = `<b>${c.total ? plural(c.total, "activity").replace("activitys", "activities") : "No activity"}</b> on ${date}${parts.length ? `<br>${parts.join(" · ")}` : ""}`;
    document.body.appendChild(tip);
    const b = r.getBoundingClientRect();
    tip.style.left = `${Math.max(8, b.left + b.width / 2 - tip.offsetWidth / 2)}px`;
    tip.style.top = `${b.top - tip.offsetHeight - 8}px`;
  });
  root.addEventListener("mouseout", (e) => { if (e.target.closest("rect.cell") && tip) tip.remove(); });
}

// ------------------------------------------------------------------ dashboard

async function viewDashboard() {
  const filter = store("heatFilter") || "";
  const data = await api(`/dashboard${filter ? `?lang=${filter}` : ""}`);
  const t = data.totals;
  const solved = t.problem_completed || 0;
  const hm = data.heatmap;
  const kindLabel = { lesson_read: ["Studied", "var(--accent)"], quiz_passed: ["Passed quiz", "var(--green)"], problem_completed: ["Solved", "var(--green)"], quiz_taken: ["Took quiz", "var(--yellow)"], submission: ["Submitted", "var(--purple)"] };
  const hour = new Date().getHours();
  const greet = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const totalActs = Object.values(hm.cells).reduce((a, c) => a + c.total, 0);

  main.innerHTML = `<div class="page">
    <div class="page-head"><div><h1>${greet}${(me.user || me.name) ? ", " + esc(me.user || me.name) : ""}</h1><div class="sub">${new Date().toLocaleDateString("en", { weekday: "long", month: "long", day: "numeric" })} · ${hm.streak ? `${plural(hm.streak, "day")} streak — don't break it` : "Start a streak today"}</div></div></div>

    <div class="grid grid-4" style="margin-bottom:16px">
      <div class="card stat"><div class="label">Current streak</div><div class="value">${hm.streak}<span class="muted small"> days</span></div><div class="hint">Best: ${hm.best_streak} days</div></div>
      <div class="card stat"><div class="label">Lessons studied</div><div class="value">${t.lesson_read || 0}</div><div class="hint">${languages.reduce((a, l) => a + l.with_content, 0)} topics ready to study</div></div>
      <div class="card stat"><div class="label">Problems solved</div><div class="value">${solved}</div><div class="hint">${t.submission || 0} submissions total</div></div>
      <div class="card stat"><div class="label">MCQs answered</div><div class="value">${t.mcq_answer || 0}</div><div class="hint">${t.quiz_passed || 0} topic quizzes passed</div></div>
    </div>

    <div class="card" style="margin-bottom:16px">
      <div class="card-head"><h2>${totalActs} activities in the last year</h2>
        <div class="right seg" id="heat-filter">
          <button data-l="" class="${!filter ? "on" : ""}">All</button>
          ${languages.map((l) => `<button data-l="${l.id}" class="${filter === l.id ? "on" : ""}">${esc(l.name)}</button>`).join("")}
        </div>
      </div>
      <div class="heat-wrap heat" id="heat">${heatmapSVG(hm)}</div>
      <div class="heat-legend"><span class="muted" style="margin-right:auto">Counts lessons studied, MCQs answered and code submissions · ${hm.active_days} active days</span>Less ${[0, 1, 2, 3, 4].map((i) => `<i style="background:var(--heat-${i})"></i>`).join("")} More</div>
    </div>

    <h2 style="font-size:16px;margin:26px 0 12px">Today's plan</h2>
    <div class="grid grid-3" style="margin-bottom:16px">
      ${data.languages.map((l) => planCard(l)).join("")}
    </div>

    <div class="grid grid-2">
      <div class="card">
        <div class="card-head"><h2>Languages</h2></div>
        ${data.languages.map((l) => `
          <a class="lang-card" href="#/lang/${l.id}" style="color:inherit;text-decoration:none;border-top:1px solid var(--border-soft)">
            <div class="top"><span class="lang-badge" style="background:${l.color};height:28px;min-width:34px;font-size:12px">${esc(l.icon)}</span>
              <div><h3>${esc(l.name)}</h3><div class="muted small">${l.complete}/${l.total} topics · ${l.with_content} with content · ${l.problems} problems · ${l.mcqs} MCQs</div></div>
              <div class="big">${Math.round(l.pct)}%</div></div>
            <div class="bar"><span style="width:${l.pct}%"></span></div>
            <div class="ms-row">${l.milestones.map((m) => `<div class="ms ${m.problems && m.done === m.problems ? "done" : m.unlocked ? "open" : ""}">${m.unlocked ? "" : "🔒 "}M${m.n} · ${m.requires_pct}%</div>`).join("")}</div>
          </a>`).join("")}
      </div>
      <div class="card">
        <div class="card-head"><h2>Recent activity</h2></div>
        ${data.recent.length ? `<ul class="activity">${data.recent.map((r) => {
          const [label, color] = kindLabel[r.kind] || [r.kind, "var(--muted)"];
          const extra = r.kind === "submission" || r.kind === "quiz_taken" ? ` · ${pct(r.value)}` : "";
          return `<li><span class="dot" style="background:${color}"></span><span><b>${label}</b> <span class="mono small">${esc(r.ref)}</span>${extra}</span><span class="pill">${esc(r.lang)}</span><span class="when">${timeAgo(r.ts)}</span></li>`;
        }).join("")}</ul>` : `<div class="empty"><h3>Nothing yet</h3>Pick a language on the left and start with its first topic.</div>`}
      </div>
    </div>
  </div>`;

  bindHeatTips($("#heat"), hm);
  $("#heat-filter").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    store("heatFilter", b.dataset.l);
    viewDashboard();
  });
}

function taskLink(lang, t) {
  if (t.kind === "problem") return `#/problem/${lang}/${t.problem}`;
  return `#/topic/${lang}/${t.topic}/${t.kind === "quiz" ? "quiz" : "lesson"}`;
}

function planCard(l) {
  const p = l.plan;
  const left = Math.max(0, p.target - p.done_today);
  const maxWeek = Math.max(1, ...p.week.map((w) => w.n));
  return `<div class="card plan-card">
    <h3><span class="lang-badge" style="background:${l.color}">${esc(l.icon)}</span>${esc(l.name)}
      <span class="spacer"></span>${l.with_content === 0 ? `<span class="pill">no content yet</span>` : `<span class="pill ${left ? "blue" : "green"}">${left ? `${left} left today` : "target met"}</span>`}</h3>
    <div class="plan-nums">
      <div><b>${p.done_today}/${p.target}</b>today</div>
      <div><b>${p.avg ?? "—"}</b>avg / day (14d)</div>
      <div><b>${p.remaining}</b>tasks left</div>
      <div><b>${p.eta ? new Date(p.eta).toLocaleDateString("en", { month: "short", day: "numeric", year: "2-digit" }) : "—"}</b>finish at pace</div>
    </div>
    <div class="bar ${p.done_today >= p.target ? "" : "blue"}"><span style="width:${p.target ? Math.min(100, (100 * p.done_today) / p.target) : 100}%"></span></div>
    <div class="week" title="Tasks completed in the last 7 days">${p.week.map((w, i) => `<span class="${i === 6 ? "today" : ""}" style="height:${(100 * w.n) / maxWeek}%" title="${w.day}: ${w.n}"></span>`).join("")}</div>
    ${p.next.length ? `<ul class="plan-list" style="margin-top:10px">${p.next.slice(0, 5).map((t) => `<li><span class="k">${t.kind}</span><a href="${taskLink(l.id, t)}">${esc(t.title)}</a></li>`).join("")}${p.next.length > 5 ? `<li class="muted small">+ ${p.next.length - 5} more</li>` : ""}</ul>`
      : `<div class="muted small" style="margin-top:10px">${p.remaining ? "Today's target is done. Anything extra raises tomorrow's pace." : "Nothing left with content yet — new topics appear as content is added."}</div>`}
    ${p.deadline ? `<div class="muted small" style="margin-top:8px">Deadline ${p.deadline} needs ${p.required}/day</div>` : ""}
  </div>`;
}

// ------------------------------------------------------------------ language

async function viewLanguage(lid) {
  const d = await api(`/lang/${lid}`);
  const collapsed = store(`collapsed:${lid}`) || {};
  const firstOpen = d.modules.findIndex((m) => m.complete < m.topics.length);
  const nextTask = d.plan.next[0] || null;

  main.innerHTML = `<div class="page">
    <div class="page-head">
      <div>
        <div class="crumbs"><a href="#/">Dashboard</a> / <span>${esc(d.name)}</span></div>
        <h1><span class="lang-badge" style="background:${d.color};height:30px;min-width:38px;font-size:13px;vertical-align:4px">${esc(d.icon)}</span> ${esc(d.name)}</h1>
        <div class="sub">${d.complete} of ${d.total} topics complete · ${d.with_content} topics have content · ${d.problems} coding problems · ${d.mcqs} MCQs</div>
      </div>
      <div class="actions">
        <a class="btn" href="#/problems/${lid}">All problems</a>
        <a class="btn" href="#/review/${lid}">Revision quiz</a>
        ${nextTask ? `<a class="btn primary" href="${taskLink(lid, nextTask)}">Continue: ${esc(nextTask.title)}</a>` : ""}
      </div>
    </div>
    <div class="bar" style="height:8px;margin-bottom:22px"><span style="width:${d.pct}%"></span></div>

    ${d.errors.length ? `<div class="error-box" style="margin-bottom:16px">Content warnings:\n${d.errors.map(esc).join("\n")}</div>` : ""}

    <div class="ms-cards">
      ${d.milestones.map((m) => `
        <a class="ms-card ${m.unlocked ? "" : "locked"}" ${m.unlocked ? `href="#/milestone/${lid}/${m.n}"` : ""}>
          <div class="n">Special quiz ${m.n}</div>
          <h3>${["Foundations Gauntlet", "Builder's Trial", "Architect's Exam", "Grandmaster Final"][m.n - 1]}</h3>
          <div class="muted small">${m.unlocked ? `${m.done}/${m.problems} hard problems solved` : `🔒 Unlocks at ${m.requires_pct}% of topics (${Math.round(d.pct)}% now)`}</div>
        </a>`).join("")}
    </div>

    ${d.modules.map((m, i) => {
      const isCollapsed = collapsed[m.name] ?? (i !== firstOpen && m.complete === 0 && i > firstOpen + 1);
      const ratio = m.topics.length ? m.complete / m.topics.length : 0;
      return `<div class="card module ${isCollapsed ? "collapsed" : ""}" data-m="${esc(m.name)}">
        <div class="module-head"><span class="chev">▾</span><h2>${esc(m.name.replace(/^\d+\s*/, ""))}</h2>
          <span class="muted small">${m.complete}/${m.topics.length}</span><span class="spacer"></span>
          <div class="bar mbar"><span style="width:${ratio * 100}%"></span></div></div>
        <div class="topic-list">${m.topics.map((t) => topicRow(lid, t)).join("")}</div>
      </div>`;
    }).join("")}
  </div>`;

  $$(".module-head").forEach((h) => h.addEventListener("click", () => {
    const card = h.parentElement;
    card.classList.toggle("collapsed");
    const c = store(`collapsed:${lid}`) || {};
    c[card.dataset.m] = card.classList.contains("collapsed");
    store(`collapsed:${lid}`, c);
  }));
}

function topicRow(lid, t) {
  const st = t.complete ? "done" : t.started ? "prog" : "";
  const meta = t.has_content ? [
    t.lesson ? `<span class="pill ${t.read ? "green" : ""}">Lesson</span>` : "",
    t.mcqs ? `<span class="pill ${t.quiz_passed ? "green" : t.quiz_best != null ? "yellow" : ""}">Quiz${t.quiz_best != null ? ` ${pct(t.quiz_best)}` : ""}</span>` : "",
    t.problems ? `<span class="pill ${t.problems_done === t.problems_total ? "green" : t.problems_done ? "yellow" : ""}">Code ${t.problems_done}/${t.problems_total}</span>` : "",
  ].join("") : `<span class="pill">Coming soon</span>`;
  return `<a class="topic-row ${t.has_content ? "" : "soon"}" href="#/topic/${lid}/${t.id}">
    <span class="status-icon ${st}">${t.complete ? "✓" : ""}</span>
    <div><div class="t-title">${esc(t.title)} <span class="lvl lvl-${t.level}">· ${t.level}</span></div><div class="t-sum">${esc(t.summary)}</div></div>
    <div class="t-meta">${meta}</div>
  </a>`;
}

// ------------------------------------------------------------------ topic

async function viewTopic(lid, tid, tab) {
  const t = await api(`/topic/${lid}/${tid}`);
  tab = tab || (t.lesson ? "lesson" : t.mcqs ? "quiz" : "problems");
  const st = t.status;
  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/">Dashboard</a> / <a href="#/lang/${lid}">${esc(t.lang_name)}</a> / <span>${esc(t.module.replace(/^\d+\s*/, ""))}</span></div>
    <div class="page-head" style="margin-bottom:14px">
      <div><h1>${esc(t.title)}</h1><div class="sub"><span class="lvl lvl-${t.level}">${t.level}</span> · ${esc(t.summary)}</div></div>
      <div class="actions">${st.complete ? `<span class="pill green" style="font-size:13px;padding:4px 12px">✓ Topic complete</span>` : ""}</div>
    </div>
    <div class="tabs" style="margin-bottom:22px">
      <a class="tab ${tab === "lesson" ? "active" : ""}" href="#/topic/${lid}/${tid}/lesson">Lesson ${st.read ? "✓" : ""}</a>
      <a class="tab ${tab === "quiz" ? "active" : ""}" href="#/topic/${lid}/${tid}/quiz">Quiz <span class="count">${t.mcqs}</span></a>
      <a class="tab ${tab === "problems" ? "active" : ""}" href="#/topic/${lid}/${tid}/problems">Coding <span class="count">${st.problems_done}/${t.problems.length}</span></a>
    </div>
    <div id="tab-body"></div>
  </div>`;
  const body = $("#tab-body");
  if (tab === "lesson") return renderLesson(body, t);
  if (tab === "quiz") return renderQuizIntro(body, t);
  return renderTopicProblems(body, t);
}

async function renderLesson(body, t) {
  if (!t.lesson) {
    body.innerHTML = `<div class="card empty"><h3>Lesson coming soon</h3>This topic is in the curriculum but its lesson hasn't been written yet.
      ${t.mcqs || t.problems.length ? `<p><a class="btn" href="#/topic/${t.lang}/${t.id}/${t.mcqs ? "quiz" : "problems"}">Go to the ${t.mcqs ? "quiz" : "coding problems"}</a></p>` : ""}</div>`;
    return;
  }
  body.innerHTML = `<div class="topic-layout">
    <article class="prose" id="lesson"></article>
    <aside class="toc" id="toc"></aside>
  </div>`;
  const art = $("#lesson");
  await renderMarkdown(art, t.lesson);
  const heads = $$("h2, h3", art);
  $("#toc").innerHTML = heads.length ? `<div class="side-title">On this page</div>${heads.map((h) => `<a href="#" data-id="${h.id}" class="${h.tagName.toLowerCase()}">${esc(h.textContent)}</a>`).join("")}` : "";
  $("#toc").addEventListener("click", (e) => {
    const a = e.target.closest("a[data-id]");
    if (!a) return;
    e.preventDefault();
    document.getElementById(a.dataset.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  const tocLinks = $$("#toc a");
  const onScroll = () => {
    let cur = heads[0];
    for (const h of heads) if (h.getBoundingClientRect().top < 120) cur = h;
    tocLinks.forEach((a) => a.classList.toggle("active", cur && a.dataset.id === cur.id));
  };
  main.addEventListener("scroll", onScroll);
  cleanup = () => main.removeEventListener("scroll", onScroll);
  onScroll();

  const end = document.createElement("div");
  end.className = "card lesson-end";
  const paint = (read) => {
    end.innerHTML = read
      ? `<span class="pill green" style="font-size:13px;padding:4px 12px">✓ Studied</span><span class="muted">Now prove it.</span><span class="spacer"></span>
         <button class="btn ghost sm" id="unread">Mark as not studied</button>
         ${t.mcqs ? `<a class="btn primary" href="#/topic/${t.lang}/${t.id}/quiz">Take the quiz →</a>` : t.problems.length ? `<a class="btn primary" href="#/topic/${t.lang}/${t.id}/problems">Start coding →</a>` : t.next ? `<a class="btn primary" href="#/topic/${t.lang}/${t.next.id}">Next: ${esc(t.next.title)} →</a>` : ""}`
      : `<div><b>Finished reading?</b><div class="muted small">Marking it studied counts toward today's target and your heatmap.</div></div><span class="spacer"></span>
         <button class="btn primary" id="mark-read">Mark lesson as studied</button>`;
    $("#mark-read", end)?.addEventListener("click", async () => {
      await api(`/lesson/${t.lang}/${t.id}`, { method: "POST", body: { read: true } });
      toast("Lesson marked as studied", "good");
      paint(true);
      refreshSidebar();
    });
    $("#unread", end)?.addEventListener("click", async () => {
      await api(`/lesson/${t.lang}/${t.id}`, { method: "POST", body: { read: false } });
      paint(false);
      refreshSidebar();
    });
  };
  paint(t.status.read);
  art.appendChild(end);
}

function renderQuizIntro(body, t) {
  if (!t.mcqs) {
    body.innerHTML = `<div class="card empty"><h3>No quiz yet</h3>MCQs for this topic haven't been added yet.</div>`;
    return;
  }
  body.innerHTML = `<div class="quiz">
    <div class="card card-pad" style="margin-bottom:16px">
      <h2 style="font-size:17px;margin-bottom:6px">Topic quiz</h2>
      <p class="muted" style="margin:0 0 14px">${t.quiz_size} questions drawn from a bank of ${t.mcqs} (theory, code-reading and output prediction). Unseen and previously-missed questions come first.
      Score <b>${pct(t.quiz_pass)}</b> or more to pass. Some questions have more than one correct answer — those say so.</p>
      <div class="row">
        <button class="btn primary" id="start-quiz">${t.attempts.length ? "Retake quiz" : "Start quiz"}</button>
        ${t.status.quiz_passed ? `<span class="pill green">Passed · best ${pct(t.status.quiz_best)}</span>` : t.status.quiz_best != null ? `<span class="pill yellow">Best ${pct(t.status.quiz_best)}</span>` : ""}
      </div>
    </div>
    ${t.attempts.length ? `<div class="card"><div class="card-head"><h2>Attempts</h2></div><table class="table"><tr><th>When</th><th>Score</th><th></th></tr>
      ${t.attempts.map((a) => `<tr><td>${timeAgo(a.ts)}</td><td class="mono">${a.correct}/${a.total}</td><td>${a.correct / a.total >= t.quiz_pass ? `<span class="pill green">pass</span>` : `<span class="pill red">below ${pct(t.quiz_pass)}</span>`}</td></tr>`).join("")}</table></div>` : ""}
  </div>`;
  $("#start-quiz").addEventListener("click", async () => {
    const q = await api(`/quiz/${t.lang}/${t.id}`);
    runQuiz(body, q.questions, {
      submit: (payload) => api(`/quiz/${t.lang}/${t.id}`, { method: "POST", body: payload }),
      passMark: t.quiz_pass,
      after: (res) => `
        ${res.passed ? (t.problems.length ? `<a class="btn primary" href="#/topic/${t.lang}/${t.id}/problems">Now the coding problems →</a>` : t.next ? `<a class="btn primary" href="#/topic/${t.lang}/${t.next.id}">Next topic →</a>` : "") : `<a class="btn" href="#/topic/${t.lang}/${t.id}/lesson">Re-read the lesson</a>`}
        <button class="btn" id="retake">Retake</button>`,
      onAfter: () => $("#retake")?.addEventListener("click", () => renderQuizIntro(body, t) || $("#start-quiz").click()),
    });
  });
}

function runQuiz(body, questions, opts) {
  const answers = {};
  body.innerHTML = `<div class="quiz">
    <div id="q-result"></div>
    ${questions.map((q, i) => `
      <div class="card q-card" data-q="${esc(q.id)}">
        <div class="q-num">Question ${i + 1} of ${questions.length}
          <span class="pill">${esc(q.type)}</span><span class="pill diff-${esc(q.difficulty)}">${esc(q.difficulty)}</span>
          ${q.topic ? `<span class="pill">${esc(q.topic)}</span>` : ""}
          ${q.multi ? `<span class="pill purple">select all that apply</span>` : ""}</div>
        <div class="q-text">${md(q.question)}</div>
        ${q.code ? md("```" + (q.lang || guessLang(q.code)) + "\n" + q.code + "\n```") : ""}
        <div class="opts">${q.options.map((o, j) => `
          <label class="opt" data-i="${o.i}">
            <input type="${q.multi ? "checkbox" : "radio"}" name="q-${esc(q.id)}" value="${o.i}">
            <span class="ol">${"ABCDEF"[j]}</span><span class="otext">${marked.parseInline(o.text)}</span>
          </label>`).join("")}</div>
        <div class="explain-slot"></div>
      </div>`).join("")}
    <div class="quiz-bar"><span class="muted" id="q-count">0 of ${questions.length} answered</span><span class="spacer"></span><button class="btn primary" id="q-submit">Submit answers</button></div>
  </div>`;
  const count = () => {
    const n = Object.values(answers).filter((a) => a.length).length;
    $("#q-count").textContent = `${n} of ${questions.length} answered`;
  };
  body.onchange = (e) => {
    const card = e.target.closest(".q-card");
    if (!card || card.classList.contains("graded")) return;
    const id = card.dataset.q;
    answers[id] = $$("input:checked", card).map((x) => +x.value);
    $$(".opt", card).forEach((o) => o.classList.toggle("selected", $("input", o).checked));
    count();
  };
  $("#q-submit").addEventListener("click", async () => {
    const n = Object.values(answers).filter((a) => a.length).length;
    if (n < questions.length && !confirm(`You've answered ${n} of ${questions.length}. Unanswered questions count as wrong. Submit anyway?`)) return;
    const res = await opts.submit({ ids: questions.map((q) => q.id), answers });
    for (const g of res.graded) {
      const card = body.querySelector(`.q-card[data-q="${CSS.escape(g.id)}"]`);
      card.classList.add("graded");
      $$("input", card).forEach((x) => (x.disabled = true));
      $$(".opt", card).forEach((o) => {
        const i = +o.dataset.i;
        o.classList.remove("selected");
        if (g.answer.includes(i)) o.classList.add("right");
        else if (g.chosen.includes(i)) o.classList.add("wrong");
      });
      $(".explain-slot", card).innerHTML = `<div class="explain"><b style="color:var(${g.correct ? "--green" : "--red"})">${g.correct ? "Correct." : "Not quite."}</b> ${md(g.explanation)}</div>`;
    }
    const ratio = res.correct / res.total;
    const passed = res.passed ?? (opts.passMark ? ratio >= opts.passMark : null);
    $("#q-result").innerHTML = `<div class="card quiz-result">
      <div class="score" style="color:var(${passed === false ? "--red" : "--green"})">${res.correct}/${res.total}</div>
      <div><div style="font-weight:600;font-size:16px">${passed === null ? "Revision complete" : passed ? "Passed" : `Not passed — you need ${pct(opts.passMark)}`}</div>
        <div class="muted">Read every explanation below, especially for the ones you got right by guessing.</div></div>
      <div class="spacer"></div><div class="row">${opts.after(res)}</div></div>`;
    $(".quiz-bar").remove();
    main.scrollTo({ top: 0, behavior: "smooth" });
    opts.onAfter?.();
    refreshSidebar();
  });
}

function guessLang(code) {
  if (/#include|printf\(|int main/.test(code)) return /std::|cout|template|class\s/.test(code) ? "cpp" : "c";
  return "python";
}

function renderTopicProblems(body, t) {
  if (!t.problems.length) {
    body.innerHTML = `<div class="card empty"><h3>No coding problems yet</h3>Problems for this topic haven't been added yet.</div>`;
    return;
  }
  body.innerHTML = `<div class="card">${problemTable(t.lang, t.problems)}</div>
    <p class="muted small" style="margin-top:12px">Solutions unlock when a submission passes at least 75% of the tests. A problem only counts as completed at 100%.</p>`;
}

const STATE_PILL = {
  new: `<span class="pill">Not started</span>`,
  attempted: `<span class="pill red">Not completed</span>`,
  unlocked: `<span class="pill yellow">Not completed · solution unlocked</span>`,
  completed: `<span class="pill green">✓ Completed</span>`,
};

function problemTable(lid, probs, extraCol) {
  return `<table class="table"><tr><th style="width:36px"></th><th>Problem</th>${extraCol ? "<th>Topic</th>" : ""}<th>Difficulty</th><th>Status</th><th>Best</th></tr>
    ${probs.map((p) => `<tr>
      <td><span class="status-icon ${p.state === "completed" ? "done" : p.state !== "new" ? "prog" : ""}">${p.state === "completed" ? "✓" : ""}</span></td>
      <td><a href="#/problem/${lid}/${p.id}"><b>${esc(p.title)}</b></a> ${p.multi_file ? `<span class="pill purple">multi-file</span>` : ""}<div class="muted small">${p.tags.map(esc).join(" · ")}</div></td>
      ${extraCol ? `<td class="small"><a href="#/topic/${lid}/${p.topic}" class="muted">${esc(p.topic_title)}</a></td>` : ""}
      <td class="diff-${esc(p.difficulty)}">${esc(p.difficulty)}</td>
      <td>${STATE_PILL[p.state]}</td>
      <td class="mono small">${p.state === "new" ? "—" : pct(p.best)}</td>
    </tr>`).join("")}</table>`;
}

// ------------------------------------------------------------------ problem

async function viewProblem(lid, pid) {
  const p = await api(`/problem/${lid}/${pid}`);
  main.innerHTML = `<div class="page wide"><div class="prob">
    <section class="prob-left">
      <div class="tabs" id="ptabs">
        <button class="tab active" data-t="desc">Description</button>
        <button class="tab" data-t="sol">${p.solution ? "Solution" : "🔒 Solution"}</button>
        <button class="tab" data-t="subs">Submissions <span class="count">${p.submissions.length}</span></button>
      </div>
      <div class="prob-body" id="pbody"></div>
    </section>
    <section class="prob-right">
      <div class="ed-bar" id="files"></div>
      <div class="editor-host" id="editor"></div>
      <div class="run-bar">
        <span class="lock-note">${icon("lock")} Paste disabled · no autocomplete — type it yourself</span>
        <span class="spacer"></span>
        <button class="btn ghost sm" id="reset">Reset</button>
        <button class="btn sm" id="toggle-custom">Custom input</button>
        <button class="btn" id="run">Run <kbd>Ctrl+⏎</kbd></button>
        <button class="btn primary" id="submit">Submit <kbd>Ctrl+⇧+⏎</kbd></button>
      </div>
      <div class="results collapsed" id="results">
        <div class="results-head"><span id="res-title">Results</span><span class="spacer"></span><button class="btn ghost sm" id="res-toggle">Show</button></div>
        <div class="results-body" id="res-body"><div class="muted">Run your code against the sample tests, or submit to run all ${p.tests_total} tests.</div></div>
      </div>
    </section>
  </div></div>`;

  // --- left panel
  let solution = p.solution;
  const showTab = async (name) => {
    $$("#ptabs .tab").forEach((b) => b.classList.toggle("active", b.dataset.t === name));
    const el = $("#pbody");
    el.scrollTop = 0;
    if (name === "desc") {
      el.innerHTML = `
        <div class="crumbs"><a href="#/lang/${lid}">${esc(p.lang_name)}</a> / ${p.milestone ? `<a href="#/milestone/${lid}/${p.milestone}">Special quiz ${p.milestone}</a>` : `<a href="#/topic/${lid}/${p.topic}/problems">${esc(p.topic_title)}</a>`}</div>
        <div class="prob-title">${esc(p.title)}</div>
        <div class="prob-meta"><span class="diff-${esc(p.difficulty)}" style="font-weight:600">${esc(p.difficulty)}</span>
          <span id="state-pill">${STATE_PILL[p.state]}</span>
          ${p.meta.tags ? p.meta.tags.split(",").map((x) => `<span class="pill">${esc(x.trim())}</span>`).join("") : ""}
          ${p.attempts ? `<span class="muted small">best ${pct(p.best)} · ${plural(p.attempts, "attempt")}</span>` : ""}</div>
        <div class="prose" id="stmt"></div>
        <h3 style="font-size:15px;margin:22px 0 10px">Sample tests</h3>
        ${p.samples.map((s, i) => `<div class="sample"><div class="sample-head">Example ${i + 1}</div><div class="sample-grid">
          <div><label>Input (stdin)</label><pre>${esc(s.input)}</pre></div><div><label>Expected output</label><pre>${esc(s.output ?? "(computed by judge)")}</pre></div></div></div>`).join("")}
        <p class="muted small">${p.tests_total} tests in total; the rest are hidden. ${p.meta.time_limit ? `Time limit ${p.meta.time_limit}s.` : ""}</p>
        ${p.hints.length ? `<div class="hint-box">${p.hints.map((h, i) => `<details class="card" style="padding:8px 14px;margin-bottom:8px"><summary style="cursor:pointer;font-weight:500">Hint ${i + 1}</summary><div class="prose" style="font-size:14px;margin-top:6px">${md(h)}</div></details>`).join("")}</div>` : ""}
        <div class="row" style="margin-top:22px">${p.prev ? `<a class="btn sm" href="#/problem/${lid}/${p.prev}">← Previous</a>` : ""}<span class="spacer"></span>${p.next ? `<a class="btn sm" href="#/problem/${lid}/${p.next}">Next →</a>` : ""}</div>`;
      await renderMarkdown($("#stmt"), p.statement);
    } else if (name === "sol") {
      if (!solution) {
        el.innerHTML = `<div class="locked-panel"><div class="big-lock">🔒</div><h3 style="color:var(--text)">Solution locked</h3>
          <p>Pass at least <b>${pct(p.unlock_score)}</b> of the tests in one submission to unlock the reference solution.<br>Your best so far: <b>${pct(p.best)}</b>.</p>
          <p class="small">Even after unlocking, the problem stays <b>not completed</b> until you pass 100%.</p></div>`;
      } else {
        el.innerHTML = `<div class="prose" id="sol"></div>`;
        const files = Object.entries(solution.files || {});
        const showFiles = files.length > 1 || !/```/.test(solution.md);
        await renderMarkdown($("#sol"), (solution.md || "") + (showFiles ? "\n\n## Reference implementation\n\n" + files.map(([n, c]) => `**${n}**\n\n\`\`\`${extLang(n)}\n${c}\n\`\`\``).join("\n\n") : ""));
      }
    } else {
      const subs = (await api(`/problem/${lid}/${pid}`)).submissions;
      el.innerHTML = subs.length ? `<table class="table"><tr><th>When</th><th>Tests</th><th>Score</th><th></th></tr>
        ${subs.map((s) => `<tr><td>${timeAgo(s.ts)}</td><td class="mono">${s.passed}/${s.total}</td>
          <td><span class="pill ${s.score >= 1 ? "green" : s.score >= p.unlock_score ? "yellow" : "red"}">${pct(s.score)}</span></td>
          <td><button class="btn ghost sm" data-sub="${s.id}">Load code</button></td></tr>`).join("")}</table>`
        : `<div class="empty"><h3>No submissions yet</h3></div>`;
      el.onclick = async (e) => {
        const b = e.target.closest("[data-sub]");
        if (!b) return;
        if (!confirm("Replace the code in the editor with this submission?")) return;
        const s = await api(`/submission/${lid}/${b.dataset.sub}`);
        for (const [n, c] of Object.entries(s.files)) if (docs[n]) docs[n].setValue(c);
        toast("Submission loaded into the editor");
      };
    }
  };
  $("#ptabs").addEventListener("click", (e) => { const b = e.target.closest(".tab"); if (b) showTab(b.dataset.t); });
  showTab("desc");

  // --- editor
  const mode = p.editor_mode;
  const starters = p.starters;
  const initial = { ...starters, ...(p.draft || {}) };
  const names = Object.keys(starters);
  const docs = {};
  for (const n of names) docs[n] = CodeMirror.Doc(initial[n] ?? "", modeFor(n, mode));
  let current = names[0];
  const cm = CodeMirror($("#editor"), {
    value: docs[current], theme: "cp", lineNumbers: true, indentUnit: 4, tabSize: 4,
    indentWithTabs: false, matchBrackets: true, styleActiveLine: true, lineWrapping: false,
    dragDrop: false, spellcheck: false, autocorrect: false, autocapitalize: false,
    extraKeys: {
      Tab: (c) => c.somethingSelected() ? c.indentSelection("add") : c.replaceSelection(" ".repeat(c.getOption("indentUnit")), "end"),
      "Shift-Tab": (c) => c.indentSelection("subtract"),
      "Ctrl-Enter": () => run(false), "Cmd-Enter": () => run(false),
      "Shift-Ctrl-Enter": () => run(true), "Shift-Cmd-Enter": () => run(true),
      "Ctrl-/": "toggleComment",
    },
  });
  cm.swapDoc(docs[current]);
  // You type every character: block paste and drag-and-drop.
  cm.on("beforeChange", (_c, ch) => {
    if (ch.origin === "paste" || ch.origin === "drop") {
      ch.cancel();
      toast("Paste is disabled here — type it out, that's how syntax sticks.", "bad");
    }
  });
  cm.getWrapperElement().addEventListener("drop", (e) => e.preventDefault(), true);
  cm.getInputField().addEventListener("paste", (e) => { e.preventDefault(); }, true);

  const renderFiles = () => {
    $("#files").innerHTML = names.map((n) => `<button class="ftab ${n === current ? "active" : ""}" data-f="${esc(n)}">${esc(n)}</button>`).join("")
      + `<span class="spacer"></span><span class="muted small mono">${esc(p.lang_name)}</span>`;
  };
  renderFiles();
  $("#files").addEventListener("click", (e) => {
    const b = e.target.closest(".ftab");
    if (!b) return;
    current = b.dataset.f;
    cm.swapDoc(docs[current]);
    renderFiles();
    cm.focus();
  });
  setTimeout(() => { cm.refresh(); cm.focus(); }, 30);

  const files = () => Object.fromEntries(names.map((n) => [n, docs[n].getValue()]));
  let dirty = false, saveTimer;
  const saveDraft = async () => {
    if (!dirty) return;
    dirty = false;
    try { await api(`/draft/${lid}/${pid}`, { method: "PUT", body: { files: files() } }); } catch (e) {}
  };
  cm.on("change", () => { dirty = true; clearTimeout(saveTimer); saveTimer = setTimeout(saveDraft, 1500); });
  cleanup = saveDraft;
  window.onbeforeunload = () => { if (dirty) saveDraft(); };

  $("#reset").addEventListener("click", () => {
    if (!confirm("Reset all files to the starter code? Your current code will be lost.")) return;
    for (const n of names) docs[n].setValue(starters[n] ?? "");
  });

  // --- custom input
  let customOpen = false;
  $("#toggle-custom").addEventListener("click", () => {
    customOpen = !customOpen;
    $("#toggle-custom").classList.toggle("blue", customOpen);
    openResults();
    if (customOpen) {
      $("#res-title").textContent = "Custom input";
      $("#res-body").innerHTML = `<textarea class="custom-input" id="cin" placeholder="Type stdin here, then press Run">${esc(p.samples[0]?.input || "")}</textarea><div id="cout"></div>`;
    } else {
      $("#res-title").textContent = "Results";
      $("#res-body").innerHTML = `<div class="muted">Run uses the sample tests now.</div>`;
    }
  });

  const results = $("#results");
  const openResults = () => { results.classList.remove("collapsed"); $("#res-toggle").textContent = "Hide"; };
  $("#res-toggle").addEventListener("click", () => {
    results.classList.toggle("collapsed");
    $("#res-toggle").textContent = results.classList.contains("collapsed") ? "Show" : "Hide";
    cm.refresh();
  });

  let busy = false;
  async function run(submit) {
    if (busy) return;
    busy = true;
    $("#run").disabled = $("#submit").disabled = true;
    openResults();
    const body = $("#res-body");
    const useCustom = customOpen && !submit;
    const cin = useCustom ? $("#cin").value : null;
    if (!useCustom) { $("#res-title").textContent = submit ? "Submission" : "Sample run"; body.innerHTML = `<div class="muted">${submit ? "Judging against all tests…" : "Running sample tests…"}</div>`; }
    else $("#cout").innerHTML = `<div class="muted" style="margin-top:8px">Running…</div>`;
    saveDraft();
    try {
      const res = await api(`/${submit ? "submit" : "run"}/${lid}/${pid}`, { method: "POST", body: { files: files(), ...(useCustom ? { custom_input: cin } : {}) } });
      if (useCustom) renderCustom(res);
      else renderResult(res, submit);
      if (submit) afterSubmit(res);
    } catch (e) {
      body.innerHTML = `<div class="error-box">${esc(e.message)}</div>`;
    } finally {
      busy = false;
      $("#run").disabled = $("#submit").disabled = false;
      cm.refresh();
    }
  }
  $("#run").addEventListener("click", () => run(false));
  $("#submit").addEventListener("click", () => run(true));

  function renderCustom(res) {
    const out = $("#cout");
    if (!res.compiled) { out.innerHTML = `<div class="verdict bad" style="margin-top:10px">Compilation error</div><div class="error-box">${esc(res.compile_output)}</div>`; return; }
    const r = res.custom;
    out.innerHTML = `<div class="row" style="margin:10px 0"><span class="verdict ${r.status === "OK" ? "ok" : "bad"}" style="font-size:15px">${r.status === "OK" ? "Finished" : r.status === "TLE" ? "Time limit exceeded" : "Runtime error"}</span><span class="muted small">${r.time_ms} ms</span></div>
      <div class="io" style="grid-template-columns:1fr ${r.stderr ? "1fr" : ""}"><div><label>Your output</label><pre>${esc(r.stdout) || '<span class="muted">(empty)</span>'}</pre></div>${r.stderr ? `<div><label>stderr</label><pre style="color:var(--red)">${esc(r.stderr)}</pre></div>` : ""}</div>
      ${res.compile_output ? `<details style="margin-top:8px"><summary class="muted small">Compiler warnings</summary><pre class="error-box">${esc(res.compile_output)}</pre></details>` : ""}`;
  }

  function renderResult(res, submit) {
    const body = $("#res-body");
    if (!res.compiled) {
      body.innerHTML = `<div class="verdict bad">Compilation Error</div><pre class="error-box" style="margin-top:10px">${esc(res.compile_output)}</pre>`;
      return;
    }
    const all = res.passed === res.total;
    const unlockable = res.score >= p.unlock_score;
    const verdict = all ? (submit ? "Accepted" : "All samples passed") : res.results.find((r) => r.status === "CE") ? "Compilation Error"
      : res.results.some((r) => r.status === "TLE") && !res.passed ? "Time Limit Exceeded"
      : res.results.some((r) => r.status === "RE") && !res.passed ? "Runtime Error" : submit && unlockable ? "Partially correct" : "Wrong Answer";
    const cls = all ? "ok" : submit && unlockable ? "mid" : "bad";
    const firstShown = res.results.find((r) => !r.passed && r.input !== undefined) || res.results.find((r) => r.input !== undefined);
    body.innerHTML = `
      <div class="row"><div class="score-ring" style="--p:${res.score * 100};--c:var(${all ? "--green" : unlockable ? "--yellow" : "--red"})" data-label="${pct(res.score)}"></div>
        <div><div class="verdict ${cls}">${verdict}</div><div class="muted small">${res.passed}/${res.total} ${submit ? "tests" : "sample tests"} passed${submit ? ` · ${all ? "problem completed" : unlockable ? "solution unlocked, but not completed" : `need ${pct(p.unlock_score)} to unlock the solution`}` : ""}</div></div></div>
      ${res.compile_output ? `<details style="margin-top:8px"><summary class="muted small">Compiler warnings</summary><pre class="error-box">${esc(res.compile_output)}</pre></details>` : ""}
      <div class="test-chips">${res.results.map((r) => `<span class="chip ${r.passed ? "pass" : "fail"} ${r === firstShown ? "sel" : ""}" data-i="${r.index}" title="${r.sample ? "sample" : "hidden"} · ${r.time_ms} ms">${r.passed ? "✓" : "✗"} ${r.sample ? "S" : "T"}${r.index} ${r.passed ? "" : r.status}</span>`).join("")}</div>
      <div id="test-detail"></div>`;
    const detail = (r) => {
      const el = $("#test-detail");
      if (!r || r.input === undefined) { el.innerHTML = r ? `<div class="muted small">Hidden test ${r.index}: ${r.passed ? "passed" : r.status} in ${r.time_ms} ms. Details are shown for samples and the first failing hidden test.</div>` : ""; return; }
      el.innerHTML = `<div class="muted small" style="margin-bottom:6px">${r.sample ? "Sample" : "Hidden"} test ${r.index} · ${r.status} · ${r.time_ms} ms</div>
        <div class="io"><div><label>Input</label><pre>${esc(r.input)}</pre></div><div><label>Expected</label><pre>${esc(r.expected)}</pre></div>
        <div><label>Your output</label><pre style="color:var(${r.passed ? "--green" : "--red"})">${esc(r.got) || '<span class="muted">(empty)</span>'}</pre></div></div>
        ${r.stderr ? `<pre class="error-box" style="margin-top:8px">${esc(r.stderr)}</pre>` : ""}`;
    };
    detail(firstShown);
    $(".test-chips", body).addEventListener("click", (e) => {
      const c = e.target.closest(".chip");
      if (!c) return;
      $$(".chip", body).forEach((x) => x.classList.toggle("sel", x === c));
      detail(res.results.find((r) => r.index === +c.dataset.i));
    });
  }

  function afterSubmit(res) {
    if (!res.compiled) return;
    p.state = res.state;
    const pill = $("#state-pill");
    if (pill) pill.innerHTML = STATE_PILL[res.state];
    if (res.solution) {
      solution = res.solution;
      $('#ptabs [data-t="sol"]').textContent = "Solution";
    }
    if (res.newly_completed) toast("Completed! Counted toward today's target.", "good");
    else if (res.newly_unlocked) toast("Solution unlocked — but this stays 'not completed' until 100%.", "good");
    $('#ptabs [data-t="subs"] .count').textContent = String(+$('#ptabs [data-t="subs"] .count').textContent + 1);
    refreshSidebar();
  }
}

function extLang(name) {
  const ext = name.split(".").pop();
  return { py: "python", c: "c", h: "c", cpp: "cpp", cc: "cpp", hpp: "cpp" }[ext] || "";
}

function modeFor(name, fallback) {
  const ext = name.split(".").pop();
  return { py: "python", c: "text/x-csrc", h: "text/x-csrc", cpp: "text/x-c++src", cc: "text/x-c++src", hpp: "text/x-c++src" }[ext] || fallback;
}

// ------------------------------------------------------------------ milestone

const MS_NAMES = ["Foundations Gauntlet", "Builder's Trial", "Architect's Exam", "Grandmaster Final"];
const MS_DESC = [
  "Bigger problems that stitch together everything from the first quarter: control flow, data structures and functions under pressure.",
  "Multi-step programs that need clean decomposition, careful edge cases and the right data structure.",
  "Hard algorithmic and design problems: you plan before you type, and efficiency matters.",
  "The final exam. Long, complex problems at interview-killer difficulty combining algorithms, design and language mastery.",
];

async function viewMilestone(lid, n) {
  const m = await api(`/milestone/${lid}/${n}`);
  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/">Dashboard</a> / <a href="#/lang/${lid}">${esc(m.lang_name)}</a> / <span>Special quiz ${n}</span></div>
    <div class="page-head"><div><h1>Special quiz ${n}: ${MS_NAMES[n - 1]}</h1><div class="sub">${MS_DESC[n - 1]}</div></div></div>
    ${m.unlocked ? (m.problems_list.length ? `<div class="card">${problemTable(lid, m.problems_list)}</div>`
      : `<div class="card empty"><h3>Unlocked — problems coming soon</h3>This special quiz's problems haven't been written yet.</div>`)
      : `<div class="card empty"><h3>🔒 Locked</h3>Complete ${m.requires_pct}% of all ${esc(m.lang_name)} topics to unlock. You're at ${Math.round(m.pct)}%.
         <div class="bar" style="max-width:320px;margin:16px auto 0"><span style="width:${Math.min(100, (100 * m.pct) / m.requires_pct)}%"></span></div>
         ${m.guide ? `<p style="margin-top:14px">You can read the study guide below now and prepare in advance.</p>` : ""}</div>`}
    ${m.guide ? `<h2 style="margin:28px 0 12px">Study guide</h2><article class="prose card" id="ms-guide"></article>` : ""}
  </div>`;
  if (m.guide) await renderMarkdown($("#ms-guide"), m.guide);
}

// ------------------------------------------------------------------ review

async function viewReview(lid) {
  const lang = languages.find((l) => l.id === lid);
  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/">Dashboard</a> / <a href="#/lang/${lid}">${esc(lang?.name || lid)}</a> / <span>Revision</span></div>
    <div class="page-head"><div><h1>Revision quiz</h1><div class="sub">15 questions mixed from every topic you've started, weighted toward the ones you get wrong.</div></div></div>
    <div id="rv"></div></div>`;
  let q;
  try {
    q = await api(`/review/${lid}`);
  } catch (e) {
    $("#rv").innerHTML = `<div class="card empty"><h3>Nothing to revise yet</h3>${esc(e.message)}<p><a class="btn" href="#/lang/${lid}">Open the curriculum</a></p></div>`;
    return;
  }
  runQuiz($("#rv"), q.questions, {
    submit: (payload) => api(`/review/${lid}`, { method: "POST", body: payload }),
    after: () => `<button class="btn primary" id="again">Another round</button>`,
    onAfter: () => $("#again")?.addEventListener("click", () => viewReview(lid)),
  });
}

// ------------------------------------------------------------------ problems list

async function viewProblems(lid) {
  const probs = await api(`/lang/${lid}/problems`);
  const lang = languages.find((l) => l.id === lid);
  let f = store(`pfilter:${lid}`) || { state: "all", diff: "all", q: "" };
  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/">Dashboard</a> / <a href="#/lang/${lid}">${esc(lang?.name || lid)}</a> / <span>Problems</span></div>
    <div class="page-head"><div><h1>All problems</h1><div class="sub">${probs.length} problems · ${probs.filter((p) => p.state === "completed").length} completed</div></div></div>
    <div class="filters">
      <input class="input" id="pq" placeholder="Search title or tag" value="${esc(f.q)}" style="min-width:240px">
      <div class="seg" id="fs">${["all", "new", "attempted", "unlocked", "completed"].map((s) => `<button data-v="${s}" class="${f.state === s ? "on" : ""}">${s === "unlocked" ? "75%+" : s}</button>`).join("")}</div>
      <div class="seg" id="fd">${["all", "Easy", "Medium", "Hard", "Expert"].map((s) => `<button data-v="${s}" class="${f.diff === s ? "on" : ""}">${s}</button>`).join("")}</div>
    </div>
    <div class="card" id="plist"></div></div>`;
  const paint = () => {
    store(`pfilter:${lid}`, f);
    const q = f.q.toLowerCase();
    const list = probs.filter((p) => (f.state === "all" || p.state === f.state) && (f.diff === "all" || p.difficulty === f.diff)
      && (!q || p.title.toLowerCase().includes(q) || p.tags.join(" ").toLowerCase().includes(q) || p.topic_title.toLowerCase().includes(q)));
    $("#plist").innerHTML = list.length ? problemTable(lid, list, true) : `<div class="empty">No problems match.</div>`;
  };
  $("#pq").addEventListener("input", (e) => { f.q = e.target.value; paint(); });
  for (const [id, key] of [["#fs", "state"], ["#fd", "diff"]]) {
    $(id).addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      f[key] = b.dataset.v;
      $$(`${id} button`).forEach((x) => x.classList.toggle("on", x === b));
      paint();
    });
  }
  paint();
}

// ------------------------------------------------------------------ settings

async function viewSettings() {
  const s = await api("/settings");
  main.innerHTML = `<div class="page" style="max-width:820px">
    <div class="page-head"><div><h1>Settings</h1><div class="sub">How today's target is calculated, per language.</div></div></div>
    <div class="card card-pad" style="margin-bottom:16px">
      <h2 style="margin-bottom:8px">How the daily target works</h2>
      <div class="prose" style="font-size:14px">${md(`Every lesson studied, topic quiz passed and coding problem completed is one **task**.

- **Pace target** = your average tasks/day over the last 14 days × 1.1 (a gentle 10% push), never below your daily minimum.
- **Deadline target** (optional) = tasks remaining ÷ days left until the date you set.
- **Today's target** is the larger of the two. Do more today and your average — and tomorrow's target — rise; slack off and it eases back, but never below the minimum.`)}</div>
    </div>
    <div class="card"><table class="table"><tr><th>Language</th><th>Daily minimum (tasks)</th><th>Finish by (optional)</th></tr>
      ${languages.map((l) => `<tr><td><span class="lang-badge" style="background:${l.color}">${esc(l.icon)}</span> ${esc(l.name)}</td>
        <td><input class="input" type="number" min="1" max="200" data-l="${l.id}" data-k="daily_min" value="${s[l.id]?.daily_min ?? 4}" style="width:90px"></td>
        <td><input class="input" type="date" data-l="${l.id}" data-k="deadline" value="${s[l.id]?.deadline ?? ""}"></td></tr>`).join("")}
    </table>
    <div style="padding:14px 18px;border-top:1px solid var(--border)" class="row"><span class="spacer"></span><button class="btn primary" id="save">Save</button></div></div>
  </div>`;
  $("#save").addEventListener("click", async () => {
    const body = {};
    for (const inp of $$("input[data-l]")) {
      body[inp.dataset.l] = body[inp.dataset.l] || {};
      body[inp.dataset.l][inp.dataset.k] = inp.dataset.k === "daily_min" ? +inp.value || 4 : inp.value;
    }
    try {
      await api("/settings", { method: "POST", body });
      toast("Saved", "good");
      refreshSidebar();
    } catch (e) { toast(e.message, "bad"); }
  });
}

// ------------------------------------------------------------------ theme + boot

function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $("#hljs-theme").href = t === "light" ? "/vendor/hljs/github.min.css" : "/vendor/hljs/github-dark.min.css";
  store("theme", t);
}
$("#theme-toggle").addEventListener("click", () => {
  applyTheme((document.documentElement.dataset.theme || "dark") === "dark" ? "light" : "dark");
  router();
});
applyTheme(document.documentElement.dataset.theme || store("theme") || "dark");
api("/auth/me").then((m) => { me = m; }).catch(() => {}).finally(() => { renderUserFoot(); router(); });
