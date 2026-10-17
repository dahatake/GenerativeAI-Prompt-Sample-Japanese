import { COPILOTS, PART_LABELS, BADGES } from "./data.js";
import { CATALOG, GROUPS } from "./catalog.js";
import { openNote, initSearch } from "./notes.js";
import { setCtx, urlFor } from "./ghlink.js";
import { initWizard } from "./wizard.js";
import { initAudio, sfx, setMood } from "./audio.js";
import { initTips } from "./tips.js";

initTips();

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ---------- State ---------- */
const KEY = "copilot-playground-v1";
const def = { xp: 0, done: [], labs: [], bestCombo: 0, orbs: 0, cams: [], konami: false, badges: [], theme: null };
let state = { ...def };
try { state = { ...def, ...JSON.parse(localStorage.getItem(KEY) || "{}") }; } catch { /* ignore */ }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* ignore */ } };

const level = xp => Math.floor(xp / 100) + 1;

export function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  $("#toasts").append(t);
  setTimeout(() => t.remove(), 3400);
}

function renderXP() {
  const lv = level(state.xp);
  $("#lv").textContent = "Lv." + lv;
  $("#xpfill").style.width = (state.xp % 100) + "%";
  $("#xptxt").textContent = state.xp + " XP";
}

function checkBadges() {
  let fresh = false;
  for (const b of BADGES) {
    if (!state.badges.includes(b.id) && b.cond(state)) {
      state.badges.push(b.id);
      fresh = true;
      toast(`${b.icon} バッジ獲得：${b.name}`);
      sfx("badge");
      burst(innerWidth / 2, innerHeight / 3, 80);
    }
  }
  if (fresh) renderBadges();
}

export function addXP(n, x, y) {
  const before = level(state.xp);
  state.xp += n;
  if (x !== undefined) floatText(`+${n} XP`, x, y);
  if (level(state.xp) > before) {
    toast(`🎉 レベルアップ！ Lv.${level(state.xp)}`);
    sfx("level");
    burst(innerWidth / 2, innerHeight / 2, 160);
  }
  renderXP();
  checkBadges();
  save();
}

function floatText(txt, x, y) {
  const el = document.createElement("div");
  el.textContent = txt;
  Object.assign(el.style, { position: "fixed", left: x + "px", top: y + "px", zIndex: 95, fontWeight: 800, color: "#ffd24a", pointerEvents: "none", textShadow: "0 2px 10px #000", transition: "all 1.2s cubic-bezier(.16,1,.3,1)" });
  document.body.append(el);
  requestAnimationFrame(() => { el.style.transform = "translateY(-70px) scale(1.4)"; el.style.opacity = 0; });
  setTimeout(() => el.remove(), 1300);
}

/* ---------- Confetti ---------- */
const cv = $("#confetti");
const cx = cv.getContext("2d");
let parts = [];
let confRunning = false;
function sizeConf() { cv.width = innerWidth; cv.height = innerHeight; }
sizeConf();
addEventListener("resize", sizeConf);
export function burst(x, y, n = 90) {
  if (reduce) return;
  const cols = ["#7f85f5", "#00b7c3", "#ff4fa3", "#ffb900", "#3fb950", "#ff8c00"];
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2, s = 4 + Math.random() * 10;
    parts.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 6, r: 3 + Math.random() * 5, c: cols[i % cols.length], rot: Math.random() * 6, vr: (Math.random() - .5) * .4, life: 110 + Math.random() * 40 });
  }
  if (!confRunning) { confRunning = true; requestAnimationFrame(tickConf); }
}
function tickConf() {
  cx.clearRect(0, 0, cv.width, cv.height);
  parts = parts.filter(p => p.life-- > 0);
  for (const p of parts) {
    p.vy += .3; p.vx *= .99; p.x += p.vx; p.y += p.vy; p.rot += p.vr;
    cx.save(); cx.translate(p.x, p.y); cx.rotate(p.rot);
    cx.globalAlpha = Math.min(1, p.life / 40);
    cx.fillStyle = p.c; cx.fillRect(-p.r, -p.r / 2, p.r * 2, p.r);
    cx.restore();
  }
  if (parts.length) requestAnimationFrame(tickConf); else { confRunning = false; cx.clearRect(0, 0, cv.width, cv.height); }
}

/* ---------- Background particles ---------- */
(function bg() {
  const c = $("#bg"), g = c.getContext("2d");
  if (reduce) return;
  let w, h, pts = [];
  const m = { x: -999, y: -999 };
  const init = () => {
    w = c.width = innerWidth; h = c.height = innerHeight;
    pts = Array.from({ length: Math.min(90, Math.floor(w * h / 18000)) }, () => ({ x: Math.random() * w, y: Math.random() * h, vx: (Math.random() - .5) * .4, vy: (Math.random() - .5) * .4 }));
  };
  init();
  addEventListener("resize", init);
  addEventListener("pointermove", e => { m.x = e.clientX; m.y = e.clientY; });
  (function loop() {
    g.clearRect(0, 0, w, h);
    const dark = document.documentElement.dataset.theme === "dark";
    const col = dark ? "180,190,255" : "90,100,200";
    for (const p of pts) {
      const dx = p.x - m.x, dy = p.y - m.y, d = Math.hypot(dx, dy);
      if (d < 140) { p.x += dx / d * 1.5; p.y += dy / d * 1.5; }
      p.x = (p.x + p.vx + w) % w; p.y = (p.y + p.vy + h) % h;
      g.fillStyle = `rgba(${col},.7)`; g.beginPath(); g.arc(p.x, p.y, 1.8, 0, 7); g.fill();
    }
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
      const d = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y);
      if (d < 120) { g.strokeStyle = `rgba(${col},${(1 - d / 120) * .25})`; g.beginPath(); g.moveTo(pts[i].x, pts[i].y); g.lineTo(pts[j].x, pts[j].y); g.stroke(); }
    }
    requestAnimationFrame(loop);
  })();
})();

/* ---------- Theme ---------- */
const root = document.documentElement;
root.dataset.theme = state.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
$("#theme").onclick = () => { root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark"; state.theme = root.dataset.theme; save(); };

/* ---------- Reveal / count-up / ripple ---------- */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  e.target.classList.add("in");
  $$("[data-count]", e.target).forEach(countUp);
  io.unobserve(e.target);
}), { threshold: .15 });
$$(".reveal").forEach((el, i) => { el.style.transitionDelay = (i % 4) * 90 + "ms"; io.observe(el); });
function countUp(el) {
  const to = +el.dataset.count; let n = 0;
  const t = setInterval(() => { n++; el.textContent = n; if (n >= to) clearInterval(t); }, 90);
}
document.addEventListener("pointerdown", e => {
  const b = e.target.closest(".btn");
  if (!b) return;
  const r = b.getBoundingClientRect(), s = Math.max(r.width, r.height);
  const d = document.createElement("span");
  d.className = "ripple";
  Object.assign(d.style, { width: s + "px", height: s + "px", left: e.clientX - r.left - s / 2 + "px", top: e.clientY - r.top - s / 2 + "px" });
  b.append(d); setTimeout(() => d.remove(), 650);
});
addEventListener("pointermove", e => {
  if (reduce) return;
  const t = $("#heroTitle");
  if (t) t.style.transform = `translate(${(e.clientX / innerWidth - .5) * -14}px,${(e.clientY / innerHeight - .5) * -10}px)`;
});

function renderBadges() {
  $("#badgeList").innerHTML = BADGES.map(b => `<div class="badge ${state.badges.includes(b.id) ? "on" : ""}"><span class="b">${b.icon}</span><small>${b.name}</small></div>`).join("");
}

$("#five").innerHTML = Object.values(PART_LABELS).map(p => `<li><span class="ic">${p.icon}</span><div><b>${p.label}</b><br><small>+${p.weight}pt</small></div></li>`).join("");

/* ---------- Before / After demo ---------- */
let demoIdx = 0, typeTimer;
function typeInto(el, text, speed = 22) {
  clearInterval(typeTimer);
  if (reduce) { el.textContent = text; return; }
  el.textContent = ""; el.classList.add("caret");
  let i = 0;
  typeTimer = setInterval(() => { el.textContent = text.slice(0, ++i); if (i >= text.length) { clearInterval(typeTimer); el.classList.remove("caret"); } }, speed);
}
function showDemo() {
  const c = COPILOTS[demoIdx % COPILOTS.length];
  $("#demoBad").textContent = c.bad;
  typeInto($("#demoGood"), c.good);
}
$("#demoNext").onclick = () => { demoIdx++; showDemo(); };
new IntersectionObserver((es, o) => { if (es[0].isIntersecting) { showDemo(); o.disconnect(); } }).observe($("#demo"));

/* ---------- Lesson modal ---------- */
let cur = null, lastFocus = null;
export function openLesson(id, tab = "learn") {
  cur = COPILOTS.find(c => c.id === id);
  lastFocus = document.activeElement;
  const sheet = $(".sheet");
  sheet.style.setProperty("--accent", cur.color);
  sheet.style.setProperty("--accent2", cur.color2);
  $("#mEmoji").textContent = cur.emoji;
  $("#mTitle").textContent = cur.name;
  $("#mTag").textContent = cur.tagline;
  buildLearn(); buildLab(); buildQuiz();
  setCtx("lesson", cur.cats[0] ? { url: urlFor(cur.cats[0]), label: `${cur.name}（${cur.cats[0]}）` } : null);
  $("#modal").hidden = false;
  setTab(tab);
  $("#mClose").focus();
  addXP(2);
}
function closeModal() { $("#modal").hidden = true; setCtx("lesson", null); lastFocus && lastFocus.focus && lastFocus.focus(); }
$("#mClose").onclick = closeModal;
$("#paneLearn").addEventListener("click", e => {
  const b = e.target.closest("[data-cat]");
  if (!b) return;
  const dir = b.dataset.cat;
  closeModal();
  if (mode === "3d") scene.start({ galaxy: true, dir }); else setTimeout(() => focusCat(dir), 50);
});
$("#modal").addEventListener("pointerdown", e => { if (e.target.id === "modal") closeModal(); });
addEventListener("keydown", e => { if (e.key === "Escape" && !$("#modal").hidden) closeModal(); });
function setTab(t) {
  $$(".tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === t));
  $("#paneLearn").hidden = t !== "learn"; $("#paneLab").hidden = t !== "lab"; $("#paneQuiz").hidden = t !== "quiz";
}
$$(".tabs button").forEach(b => b.onclick = () => setTab(b.dataset.tab));

function buildLearn() {
  $("#paneLearn").innerHTML = `
    ${cur.tips.map((t, i) => `<div class="tip"><b>TIP ${i + 1}</b><span>${t}</span></div>`).join("")}
    <div class="bubble bad"><small>😵 Before</small><p>${esc(cur.bad)}</p></div>
    <div class="bubble good"><small>✨ After</small><p>${esc(cur.good)}</p></div>
    <div class="links"><span class="mini">📚 関連するサンプルPrompt：</span>${cur.cats.map(d => `<button class="chip" data-cat="${esc(d)}">${(CATALOG.find(c => c.dir === d) || {}).icon || "📁"} ${esc(d)}</button>`).join("")}</div>`;
}

function buildLab() {
  const keys = Object.keys(PART_LABELS);
  $("#paneLab").innerHTML = `
    <p><b>お題：</b>${cur.lab.task}<br><small class="hint">要素にチェックを入れて、プロンプトを育てましょう。</small></p>
    <div class="parts">${keys.map(k => `
      <label class="part"><input type="checkbox" data-k="${k}"><span><b>${PART_LABELS[k].icon} ${PART_LABELS[k].label}</b> <small>+${PART_LABELS[k].weight}pt</small><small>${esc(cur.lab.parts[k])}</small></span></label>`).join("")}
    </div>
    <div class="meter"><i id="meterFill"></i></div>
    <div class="score"><span id="scoreTxt">0 / 100</span><span id="scoreMsg">まだ空っぽ…</span></div>
    <div class="out" id="labOut">（ここに完成したプロンプトが表示されます）</div>`;
  let lastScore = 0;
  $$("#paneLab input").forEach(inp => inp.onchange = e => {
    inp.closest(".part").classList.toggle("on", inp.checked);
    sfx("pop");
    const picked = $$("#paneLab input:checked").map(i => i.dataset.k);
    const score = picked.reduce((s, k) => s + PART_LABELS[k].weight, 0);
    $("#meterFill").style.width = score + "%";
    $("#scoreTxt").textContent = `${score} / 100`;
    $("#scoreMsg").textContent = score === 0 ? "まだ空っぽ…" : score < 40 ? "曖昧です 🌫️" : score < 70 ? "良くなってきた 🌤️" : score < 100 ? "あと一歩！ 🔥" : "完璧！ 🏆";
    typeInto($("#labOut"), keys.filter(k => picked.includes(k)).map(k => cur.lab.parts[k]).join("\n") || "（ここに完成したプロンプトが表示されます）", 8);
    if (score > lastScore && e.isTrusted) { const r = inp.getBoundingClientRect(); floatText("+" + PART_LABELS[inp.dataset.k].weight, r.left + 10, r.top); }
    lastScore = score;
    if (score === 100 && !state.labs.includes(cur.id)) {
      state.labs.push(cur.id);
      sfx("fanfare");
      burst(innerWidth / 2, innerHeight / 2, 160);
      addXP(30, innerWidth / 2, innerHeight / 2);
    }
  });
}

function buildQuiz() {
  let i = 0, score = 0, combo = 0;
  const pane = $("#paneQuiz");
  const render = () => {
    if (i >= cur.quiz.length) {
      const pass = score >= Math.ceil(cur.quiz.length / 2);
      pane.innerHTML = `<div class="result"><div class="big">${score === cur.quiz.length ? "🏆" : pass ? "🎉" : "💪"}</div><h3>${score} / ${cur.quiz.length} 正解</h3><p>${pass ? "ミッションクリア！" : "もう一度挑戦してみましょう。"}</p><button class="btn primary" id="retry">もう一度</button></div>`;
      $("#retry").onclick = () => { i = score = combo = 0; render(); };
      if (pass) {
        sfx("fanfare");
        burst(innerWidth / 2, innerHeight / 2, 220);
        if (!state.done.includes(cur.id)) { state.done.push(cur.id); addXP(25); }
      }
      return;
    }
    const q = cur.quiz[i];
    pane.innerHTML = `<div class="quiz-top"><span>Q${i + 1} / ${cur.quiz.length}</span><span class="combo" id="combo">🔥 COMBO x${combo}</span></div>
      <h4>${q.q}</h4>${q.a.map((a, n) => `<button class="opt" data-n="${n}">${"ABCD"[n]}. ${a}</button>`).join("")}<div id="why"></div>`;
    $$(".opt", pane).forEach(b => b.onclick = e => {
      const n = +b.dataset.n, ok = n === q.correct;
      $$(".opt", pane).forEach(o => { o.disabled = true; if (+o.dataset.n === q.correct) o.classList.add("ok"); });
      if (!ok) { b.classList.add("ng"); combo = 0; sfx("ng"); } else {
        sfx(combo >= 2 ? "combo" : "ok");
        score++; combo++; state.bestCombo = Math.max(state.bestCombo, combo);
        addXP(10 + combo * 2, e.clientX, e.clientY);
        burst(e.clientX, e.clientY, 40);
        const c = $("#combo"); c.textContent = `🔥 COMBO x${combo}`; c.classList.add("hot");
      }
      $("#why").innerHTML = `<div class="why">${ok ? "✅ 正解！" : "❌ 残念…"} ${q.why}</div><button class="btn primary" id="nx">${i + 1 >= cur.quiz.length ? "結果を見る" : "次へ →"}</button>`;
      $("#nx").onclick = () => { i++; render(); };
      $("#nx").focus();
    });
  };
  render();
}

/* ---------- Roulette / Konami ---------- */
$("#roulette").onclick = e => {
  const c = COPILOTS[Math.floor(Math.random() * COPILOTS.length)];
  burst(e.clientX, e.clientY, 50);
  toast(`🎲 お題：${c.name} の「${c.lab.task}」`);
  setTimeout(() => openLesson(c.id, "lab"), 600);
};
const KONAMI = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
let kpos = 0;
addEventListener("keydown", e => {
  kpos = e.key.toLowerCase() === KONAMI[kpos].toLowerCase() ? kpos + 1 : 0;
  if (kpos === KONAMI.length) {
    kpos = 0;
    document.body.classList.toggle("rainbow");
    state.konami = true; toast("🌈 レインボーモード！");
    burst(innerWidth / 2, innerHeight / 2, 250); addXP(50);
  }
});

/* ---------- Mode switch (2D / 3D) ---------- */
let scene = null, rpg = null, mode = "2d", savedY = 0, switching = false;
const VIEWS = { "2d": "#view2d", "3d": "#view3d", rpg: "#viewRpg" };
const wait = ms => new Promise(r => setTimeout(r, ms));

function focusCat(dir) {
  const el = dir && $(`.cat[data-dir="${CSS.escape(dir)}"]`);
  if (!el) return false;
  el.classList.add("in", "pulse");
  const box = el.querySelector(".cat-files");
  if (box.hidden) el.querySelector(".toggle").click();
  const top = el.getBoundingClientRect().top + scrollY - innerHeight / 4;
  scrollTo({ top, behavior: "instant" });
  setTimeout(() => el.classList.remove("pulse"), 2600);
  return true;
}

async function setMode(m, opts = {}) {
  if (switching) return;
  if (m === mode) { if (m === "3d" && scene) scene.start(opts); return; }
  switching = true;
  const prev = mode;
  try {
    if (m === "3d" && !scene) {
      toast("🪐 3Dワールドを読み込み中…");
      try {
        const mod = await import("./scene3d.js");
        scene = await mod.initScene({ state, save, addXP, toast, burst, openLesson, checkBadges, goTo2D: dir => setMode("2d", { dir }) });
      } catch (err) {
        console.error(err);
        toast("⚠️ 3Dを開始できませんでした（WebGL未対応またはCDN接続不可）");
        return;
      }
    }
    if (m === "rpg" && !rpg) {
      try {
        const mod = await import("./rpg.js");
        rpg = mod.initRpg({ state, save, addXP, toast, burst, checkBadges, sfx, setMood, exit: () => setMode("2d") });
      } catch (err) {
        console.error(err);
        toast("⚠️ RPGモードを開始できませんでした");
        return;
      }
    }
    mode = m;
    for (const k of Object.keys(VIEWS)) $("#m" + k).setAttribute("aria-selected", k === m);
    const from = $(VIEWS[prev]), to = $(VIEWS[m]);
    if (prev === "2d") savedY = scrollY;
    sfx(m === "2d" ? "whooshBack" : "whoosh");
    setMood({ "2d": "calm", "3d": "space", rpg: "rpgField" }[m]);
    to.classList.add(m === "2d" ? "entering" : "enter");
    to.hidden = false;
    if (m === "2d") {
      $("#bg").style.display = "";
      setCatCtx(opts.dir || null);
      if (!focusCat(opts.dir)) scrollTo({ top: savedY, behavior: "instant" });
    } else {
      $("#bg").style.display = "none";
      setCtx("cat", null);
      if (m === "3d") scene.start(opts); else rpg.start(opts);
    }
    void to.offsetWidth;
    to.classList.remove("entering", "enter");
    from.classList.add("leaving");
    await wait(750);
    from.hidden = true; from.classList.remove("leaving");
    if (prev === "3d" && scene) scene.stop();
    if (prev === "rpg" && rpg) rpg.stop();
  } finally {
    switching = false;
  }
}
$("#m2d").onclick = () => setMode("2d");
$("#m3d").onclick = () => setMode("3d");
$("#mrpg").onclick = () => setMode("rpg");
$("#toRpg").onclick = () => setMode("rpg");
$("#rpgBack").onclick = () => setMode("2d");
$("#to3d").onclick = () => setMode("3d");
$("#back2d").onclick = () => setMode("2d");
$("#galaxyBtn").onclick = () => setMode("3d", { galaxy: true });
/* ---------- Sample prompt catalog ---------- */
function fileList(c) {
  const groups = {};
  c.files.forEach(f => (groups[f.group] ||= []).push(f));
  return Object.entries(groups).map(([g, fs]) => `${g ? `<div class="grp">📁 ${esc(g)}</div>` : ""}<ul>${fs.map(f => `<li><button class="notelink" data-path="${esc(f.path)}">${f.path === "README.md" ? "📖 " : "📝 "}${esc(f.title)}</button></li>`).join("")}</ul>`).join("");
}
function catCard(c) {
  const big = c.kind === "persona";
  return `<article class="cat ${big ? "big" : ""} reveal" style="--c1:${c.color}" data-dir="${esc(c.dir)}">
    <div class="cat-top"><span class="cat-ic">${c.icon}</span><div>
      ${big ? `<span class="role">職種：${esc(c.role)}</span>` : ""}
      <h4>${esc(c.dir)}</h4></div><span class="count">${c.count}件</span></div>
    <p>${esc(c.desc)}</p>
    <div class="cat-actions">
      ${c.startPath ? '<button class="btn small primary start">📖 まず読む</button>' : ""}
      <button class="btn small toggle" aria-expanded="false">Promptを見る ▾</button>
      <button class="btn small to3d" title="3Dでこの星にズームイン">🪐 3Dで見る</button>
    </div>
    <div class="cat-files" hidden>${fileList(c)}</div>
  </article>`;
}
function setCatCtx(dir) { setCtx("cat", dir ? { url: urlFor(dir), label: dir } : null); }
function renderCatalog() {
  const total = CATALOG.reduce((s, c) => s + c.count, 0);
  const nav = `<nav class="grp-nav reveal" aria-label="カテゴリーの目次"><b>目次</b>${GROUPS.map(g => `<a href="#grp-${g.id}">${g.icon} ${esc(g.name)}<small>${g.dirs.length}</small></a>`).join("")}<span class="mini">全${CATALOG.length}カテゴリ／${total}Prompt</span></nav>`;
  const body = GROUPS.map(g => {
    const cs = CATALOG.filter(c => c.group === g.id);
    const n = cs.reduce((s, c) => s + c.count, 0);
    return `<section class="grp" id="grp-${g.id}" aria-labelledby="grp-${g.id}-h">
      <h3 class="cat-h reveal" id="grp-${g.id}-h">${g.icon} ${esc(g.name)} <small>${esc(g.hint)}・${cs.length}カテゴリ／${n}件</small></h3>
      <div class="${g.id === "role" ? "persona-grid" : "topic-grid"}">${cs.map(catCard).join("")}</div></section>`;
  }).join("");
  $("#catalogRoot").innerHTML = nav + body;
  $$(".cat").forEach(el => io.observe(el));
  $("#catalogRoot").onclick = e => {
    const card = e.target.closest(".cat");
    if (!card) return;
    const dir = card.dataset.dir, c = CATALOG.find(x => x.dir === dir);
    if (e.target.closest(".to3d")) { setMode("3d", { galaxy: true, dir }); return; }
    const nl = e.target.closest(".notelink");
    if (nl) { setCatCtx(dir); openNote(dir, nl.dataset.path); return; }
    if (e.target.closest(".start")) { setCatCtx(dir); openNote(dir, c.startPath); return; }
    const b = e.target.closest(".toggle");
    if (!b) return;
    const box = card.querySelector(".cat-files");
    const open = box.hidden;
    box.hidden = !open;
    b.setAttribute("aria-expanded", open);
    b.textContent = open ? "閉じる ▴" : "Promptを見る ▾";
    setCatCtx(open ? dir : null);
  };
}
window.addEventListener("note-copied", e => {
  const { x, y, key } = e.detail;
  burst(x, y, 45);
  state.copies = state.copies || [];
  if (!state.copies.includes(key)) { state.copies.push(key); addXP(3, x, y); } else floatText("📋", x, y);
  checkBadges();
});
initSearch();
initAudio();
initWizard({ state, save, addXP, toast, burst, checkBadges, setMode, focusCat });
renderXP(); renderBadges(); renderCatalog();
if (location.hash === "#3d") setMode("3d");
if (location.hash === "#rpg") setMode("rpg");
if (location.hash === "#galaxy") setMode("3d", { galaxy: true });
