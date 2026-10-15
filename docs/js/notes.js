import { CATALOG } from "./catalog.js";
import { FILES } from "./files.js";
import { setCtx, urlFor } from "./ghlink.js";
import { sfx } from "./audio.js";

const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const meta = dir => CATALOG.find(c => c.dir === dir);
const cache = {};
let indexP = null;

async function getJSON(u) {
  const r = await fetch(u);
  if (!r.ok) throw new Error(u + " " + r.status);
  return r.json();
}
export const loadIndex = () => (indexP ||= getJSON("data/index.json"));
async function loadDir(dir) {
  const idx = await loadIndex();
  return (cache[dir] ||= getJSON("data/" + idx.dirs[dir]));
}

/* ---------- Markdown (最小限) ---------- */
function inline(s) {
  return esc(s)
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, t, u) => (/^https?:\/\//.test(u) && !/github\.com/i.test(u) ? `<a href="${u}" target="_blank" rel="noopener">${t}</a>` : t))
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>");
}
function mdHtml(src) {
  const L = src.split("\n"), out = [];
  let i = 0;
  while (i < L.length) {
    const l = L[i];
    if (!l.trim()) { i++; continue; }
    let m;
    if ((m = l.match(/^(#{1,6})\s+(.*)/))) { const n = Math.min(6, m[1].length + 1); out.push(`<h${n}>${inline(m[2])}</h${n}>`); i++; continue; }
    if (/^\s*([-*_])\1{2,}\s*$/.test(l)) { out.push("<hr>"); i++; continue; }
    if (/^\s*\|/.test(l) && /^\s*\|[\s:|-]+\|\s*$/.test(L[i + 1] || "")) {
      const row = r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => inline(c.trim()));
      const head = row(l); i += 2;
      const rows = [];
      while (i < L.length && /^\s*\|/.test(L[i])) rows.push(row(L[i++]));
      out.push(`<div class="tbl"><table><thead><tr>${head.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    if (/^\s*([-*+]|\d+[.)])\s+/.test(l)) {
      const ord = /^\s*\d/.test(l), items = [];
      while (i < L.length && /^\s*([-*+]|\d+[.)])\s+/.test(L[i])) { items.push(inline(L[i].replace(/^\s*([-*+]|\d+[.)])\s+/, ""))); i++; }
      out.push(`<${ord ? "ol" : "ul"}>${items.map(t => `<li>${t}</li>`).join("")}</${ord ? "ol" : "ul"}>`);
      continue;
    }
    if (/^\s*>/.test(l)) {
      const q = [];
      while (i < L.length && /^\s*>/.test(L[i])) q.push(inline(L[i++].replace(/^\s*>\s?/, "")));
      out.push(`<blockquote>${q.join("<br>")}</blockquote>`);
      continue;
    }
    const p = [];
    while (i < L.length && L[i].trim() && !/^(#{1,6}\s|\s*([-*+]|\d+[.)])\s|\s*>|\s*\|)/.test(L[i])) p.push(inline(L[i++]));
    if (!p.length) { p.push(inline(L[i++])); }
    out.push(`<p>${p.join("<br>")}</p>`);
  }
  return out.join("");
}

/* 文章中のコードブロック＝コピーして使える Prompt として切り出す */
function parse(text) {
  const L = text.split("\n"), blocks = [];
  let buf = [], code = null, heading = "", title = "";
  const flush = () => { if (buf.join("").trim()) blocks.push({ t: "md", s: buf.join("\n") }); buf = []; };
  for (const l of L) {
    const f = l.match(/^\s*(`{3,}|~{3,})\s*([\w-]*)/);
    if (code) {
      if (f && f[1][0] === code.fence[0] && f[1].length >= code.fence.length && !f[2]) { blocks.push({ t: "code", lang: code.lang, s: code.lines.join("\n"), h: heading }); code = null; }
      else code.lines.push(l);
      continue;
    }
    if (f) { flush(); code = { fence: f[1], lang: f[2], lines: [] }; continue; }
    const h = l.match(/^#{1,6}\s+(.*)/);
    if (h) { heading = h[1].trim(); if (!title) title = heading; }
    buf.push(l);
  }
  if (code) blocks.push({ t: "code", lang: code.lang, s: code.lines.join("\n"), h: heading });
  flush();
  return { blocks, title };
}

/* ---------- コピー ---------- */
export async function getPrompts(dir, path) {
  const text = (await loadDir(dir))[path];
  return text == null ? [] : parse(text).blocks.filter(b => b.t === "code");
}
export async function copyText(s) {
  try { await navigator.clipboard.writeText(s); return true; } catch { /* fallback */ }
  const t = document.createElement("textarea");
  t.value = s; t.style.cssText = "position:fixed;opacity:0";
  document.body.append(t); t.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch { /* ignore */ }
  t.remove();
  return ok;
}
const ph = s => esc(s).replace(/(\{\{[^}\n]{1,80}\}\}|【[^】\n]{1,50}】|〈[^〉\n]{1,50}〉)/g, '<mark class="ph">$1</mark>');
const TILT = [-1.1, .9, -.6, 1.2, -.9];
const COLORS = ["y", "p", "g", "b"];

/* ---------- ノート画面 ---------- */
let cur = null;
export async function openNote(dir, path) {
  const m = meta(dir);
  const root = $("#noteModal");
  if (root.hidden) sfx("open");
  root.hidden = false;
  document.body.classList.add("noting");
  const sheet = $("#noteSheet");
  sheet.innerHTML = '<div class="note-loading">📒 ノートを開いています…</div>';
  let text;
  try { text = (await loadDir(dir))[path]; } catch { text = null; }
  if (text == null) { sheet.innerHTML = '<div class="note-loading">ノートを読み込めませんでした。</div>'; return; }
  cur = { dir, path };
  const { blocks, title } = parse(text);
  const name = title || path.replace(/\.md$/, "");
  const sub = path.includes("/") ? path.split("/").slice(0, -1).join(" / ") : "";
  const codes = blocks.filter(b => b.t === "code");
  const files = FILES[dir] || [], pos = files.indexOf(path);
  setCtx("note", { url: urlFor(dir, path), label: `${dir} / ${path}` });
  let k = 0;
  const body = blocks.map(b => {
    if (b.t === "md") return `<div class="memo">${mdHtml(b.s)}</div>`;
    k++;
    const col = COLORS[(k - 1) % 4], tilt = TILT[(k - 1) % 5];
    return `<section class="sticky ${col}" style="--tilt:${tilt}deg" data-k="${k - 1}">
      <header><span class="pin">📌</span><b>Prompt ${k}${codes.length > 1 ? " / " + codes.length : ""}</b><span class="hd">${esc(b.h || "")}</span>
        <button class="copy" data-copy="${k - 1}" aria-label="このPromptをコピー">📋 コピー</button></header>
      <pre>${ph(b.s)}</pre><span class="stamp" aria-hidden="true">COPIED!</span></section>`;
  }).join("");
  sheet.innerHTML = `
    <button class="note-x" id="noteX" aria-label="閉じる">✕</button>
    <div class="spiral" aria-hidden="true">${"<i></i>".repeat(14)}</div>
    <div class="paper">
      <div class="tape"></div>
      <p class="crumb">${m ? m.icon : "📁"} ${esc(dir)}${sub ? " › " + esc(sub) : ""}</p>
      <h2>${esc(name)}</h2>
      <ol class="steps">
        <li><b>①</b> <span>📋 <em>コピー</em>を押す</span></li>
        <li><b>②</b> <span>💬 Copilot や ChatGPT に<em>貼り付け</em></span></li>
        <li><b>③</b> <span>✏️ <mark class="ph">光る部分</mark>だけ自分の内容に</span></li>
      </ol>
      <div class="note-actions">
        ${codes.length ? `<button class="btn small primary" data-copy="all-prompts">📋 Promptを全部コピー</button>` : ""}
        <button class="btn small" data-copy="doc">📄 ノート全文をコピー</button>
      </div>
      <div class="note-body">${body}</div>
      <nav class="note-nav">
        <button class="btn small" data-nav="-1" ${pos <= 0 ? "disabled" : ""}>‹ 前のノート</button>
        <span>${pos + 1} / ${files.length}</span>
        <button class="btn small" data-nav="1" ${pos >= files.length - 1 ? "disabled" : ""}>次のノート ›</button>
      </nav>
    </div>`;
  sheet.scrollTop = 0;
  const paper = $(".paper", sheet);
  paper.animate([{ transform: "rotateX(-12deg) translateY(30px)", opacity: 0 }, { transform: "none", opacity: 1 }], { duration: 520, easing: "cubic-bezier(.16,1,.3,1)" });
  sheet.onclick = async e => {
    if (e.target.closest("#noteX")) return closeNote();
    const nav = e.target.closest("[data-nav]");
    if (nav) return openNote(dir, files[pos + +nav.dataset.nav]);
    const b = e.target.closest("[data-copy]");
    if (!b) return;
    const w = b.dataset.copy;
    const s = w === "doc" ? text : w === "all-prompts" ? codes.map(c => c.s).join("\n\n---\n\n") : codes[+w].s;
    const ok = await copyText(s);
    const r = b.getBoundingClientRect();
    const card = b.closest(".sticky");
    if (card) { sfx("stamp"); card.classList.remove("done"); void card.offsetWidth; card.classList.add("done"); }
    b.classList.add("ok");
    const old = b.textContent;
    b.textContent = ok ? "✅ コピーしました！" : "⚠️ 選択してコピーしてください";
    setTimeout(() => { b.textContent = old; b.classList.remove("ok"); }, 1600);
    if (ok) window.dispatchEvent(new CustomEvent("note-copied", { detail: { x: r.left + r.width / 2, y: r.top, key: dir + "/" + path } }));
  };
  $("#noteX").focus();
}
export function closeNote() {
  $("#noteModal").hidden = true;
  document.body.classList.remove("noting");
  setCtx("note", null);
  cur = null;
}
addEventListener("keydown", e => {
  if (e.key === "Escape" && !$("#noteModal").hidden) { e.stopPropagation(); closeNote(); }
  if (!$("#noteModal").hidden && cur && (e.key === "ArrowRight" || e.key === "ArrowLeft") && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
    const files = FILES[cur.dir], p = files.indexOf(cur.path) + (e.key === "ArrowRight" ? 1 : -1);
    if (files[p]) openNote(cur.dir, files[p]);
  }
}, true);
$("#noteModal").addEventListener("pointerdown", e => { if (e.target.id === "noteModal") closeNote(); });

/* ---------- 検索 ---------- */
export function initSearch() {
  const q = $("#q"), box = $("#qres");
  let items = [], active = -1, timer;
  const run = async () => {
    const s = q.value.trim().toLowerCase();
    if (!s) { box.hidden = true; return; }
    const idx = await loadIndex();
    const words = s.split(/\s+/);
    const hits = [];
    for (const it of idx.items) {
      const t = it.t.toLowerCase(), f = (it.p + " " + it.d).toLowerCase(), x = it.x.toLowerCase();
      let sc = 0, ok = true;
      for (const w of words) {
        const a = t.includes(w) ? 6 : 0, b = f.includes(w) ? 3 : 0, c = x.includes(w) ? 1 : 0;
        if (!a && !b && !c) { ok = false; break; }
        sc += a + b + c;
      }
      if (ok) hits.push({ it, sc });
    }
    hits.sort((a, b) => b.sc - a.sc);
    items = hits.slice(0, 12).map(h => h.it);
    active = items.length ? 0 : -1;
    box.innerHTML = items.length
      ? items.map((it, i) => {
        const m = meta(it.d), w = words[0], at = it.x.toLowerCase().indexOf(w);
        const snip = at >= 0 ? it.x.slice(Math.max(0, at - 24), at + 60) : it.x.slice(0, 70);
        return `<button class="qi ${i === 0 ? "on" : ""}" data-i="${i}" style="--c1:${m ? m.color : "#7f85f5"}"><span class="qic">${m ? m.icon : "📝"}</span><span><b>${esc(it.t || it.p)}</b><small>${esc(it.d)}${it.p.includes("/") ? " / " + esc(it.p.split("/").slice(0, -1).join("/")) : ""}</small><small class="sn">…${esc(snip)}…</small></span></button>`;
      }).join("")
      : '<p class="qnone">🔍 見つかりませんでした。別の言葉（例：議事録、SQL、統計）で試してみてください。</p>';
    box.hidden = false;
  };
  const choose = i => { const it = items[i]; if (!it) return; box.hidden = true; q.blur(); openNote(it.d, it.p); };
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 90); });
  q.addEventListener("focus", () => { loadIndex(); if (q.value.trim()) run(); });
  q.addEventListener("keydown", e => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!items.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      box.querySelectorAll(".qi").forEach((b, i) => b.classList.toggle("on", i === active));
      box.querySelectorAll(".qi")[active].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") { e.preventDefault(); choose(Math.max(active, 0)); }
    else if (e.key === "Escape") { box.hidden = true; q.blur(); }
  });
  box.addEventListener("click", e => { const b = e.target.closest(".qi"); if (b) choose(+b.dataset.i); });
  document.addEventListener("pointerdown", e => { if (!e.target.closest(".searchbox")) box.hidden = true; });
  addEventListener("keydown", e => {
    if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); }
  });
}
