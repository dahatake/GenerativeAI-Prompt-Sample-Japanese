import { CATALOG } from "./catalog.js";
import { getPrompts, copyText, openNote } from "./notes.js";

const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const PERSONAS = CATALOG.filter(c => c.kind === "persona");
const TITLES = ["コピーしてみよう", "貼り付けて使おう", "探し方3つ", "3Dで遊ぼう"];

export function initWizard(api) {
  const { state, save, addXP, toast, burst, checkBadges, setMode, focusCat } = api;
  const modal = $("#wizModal"), box = $("#wiz");
  let step = 0, dir = 1, pick = null, demo = null, copied = false, lastFocus = null;

  const cat = () => PERSONAS.find(p => p.dir === pick) || null;

  async function loadDemo() {
    demo = null;
    const c = cat() || CATALOG.find(x => x.dir === "会議");
    for (const f of c.files.filter(f => f.path !== "README.md").slice(0, 10)) {
      const ps = await getPrompts(c.dir, f.path);
      if (ps.length) { demo = { c, f, text: ps[0].s }; return; }
    }
  }

  const screens = [
    () => {
      const c = demo ? demo.c : null;
      return `<h2 id="wizTitle">まず、Promptをコピーしてみよう</h2>
        <p>${c ? `<b>${c.icon} ${esc(c.dir)}</b> の「${esc(demo.f.title)}」から、実際のPromptを1つ取り出しました。` : "Promptを読み込んでいます…"}</p>
        ${demo ? `<section class="sticky y" style="--tilt:-.8deg"><header><span class="pin">📌</span><b>Prompt</b><button class="copy ${copied ? "ok" : ""}" id="wCopy">${copied ? "✅ コピーしました！" : "📋 コピー"}</button></header><pre>${esc(demo.text.length > 700 ? demo.text.slice(0, 700) + "\n…（続きは全文をコピーすると入ります）" : demo.text)}</pre></section>
        <p class="w-note">👆 「📋 コピー」を押してください。${copied ? "<b>できました！</b> 次へ進みましょう。" : "押すとパソコンのクリップボードに入ります。"}</p>
        <p><button class="btn small" id="wOpenNote">📒 ノートで全文を見る</button></p>` : '<div class="note-loading">📒 読み込み中…</div>'}`;
    },
    () => `<h2 id="wizTitle">Copilot や ChatGPT に貼り付けよう</h2>
      <ol class="w-steps">
        <li><b>1</b><span>お使いのAIの<b>入力欄</b>を開く</span></li>
        <li><b>2</b><span><kbd>Ctrl</kbd> + <kbd>V</kbd>（Macは <kbd>⌘</kbd> + <kbd>V</kbd>）で<b>貼り付け</b></span></li>
        <li><b>3</b><span><mark class="ph">光っている部分</mark>（<code>{{…}}</code> や 【…】）を<b>自分の内容に書き換える</b></span></li>
        <li><b>4</b><span>送信！ 思ったのと違えば「もっと短く」「表にして」と<b>追加でお願い</b>すればOK</span></li>
      </ol>
      <div class="w-links">
        <a class="btn small" href="https://m365.cloud.microsoft/chat" target="_blank" rel="noopener">🧑‍💼 Microsoft 365 Copilot ↗</a>
        <a class="btn small" href="https://copilot.microsoft.com/" target="_blank" rel="noopener">✨ Copilot ↗</a>
        <a class="btn small" href="https://chatgpt.com/" target="_blank" rel="noopener">💬 ChatGPT ↗</a>
      </div>
      <p class="w-note">⚠️ 機密情報・個人情報は入力しない／答えは鵜呑みにせず確認する、が大原則です。</p>`,
    () => `<h2 id="wizTitle">もっと探す3つの方法</h2>
      <div class="w-ways">
        <button class="w-way" data-way="search"><span>🔎</span><b>① 検索する</b><small>画面上部の入力欄に「議事録」「SQL」など。<kbd>/</kbd> キーでも入力できます</small></button>
        <button class="w-way" data-way="list"><span>🗂️</span><b>② 一覧から選ぶ</b><small>職種カード → 「Promptを見る」→ クリックでノートが開きます</small></button>
        <button class="w-way" data-way="3d"><span>🪐</span><b>③ 3Dで探検する</b><small>星をクリックでズームイン。奥のPromptまで飛び込めます</small></button>
      </div>
      <p class="w-note">カードをクリックすると、ガイドを閉じてその場で試せます。（ガイドは「🧭 使い方ガイド」でいつでも再開できます）</p>`,
    () => `<h2 id="wizTitle">3Dモードの遊び方（3Dが初めてでも安心）</h2>
      <ul class="w-points">
        <li><b>🖱 ドラッグ</b><span>見る向きを変える</span></li>
        <li><b>🎡 ホイール</b><span>近づく・遠ざかる</span></li>
        <li><b>🌟 星をクリック</b><span>ズームイン。もう一度クリックでノートが開く</span></li>
        <li><b>⎋ Esc</b><span>ズームアウト</span></li>
        <li><b>🎥 カメラ設定</b><span>「かんたん」タブで好きな雰囲気を選ぶだけ。酔いやすい方は「落ち着いた発表」がおすすめ</span></li>
      </ul>
      <div class="w-links"><button class="btn small primary" id="w3d">🪐 いま3Dを体験する</button></div>
      <p class="w-note">🏅 このガイドを最後まで見ると、バッジ「ガイド修了」を獲得できます。</p>`
  ];

  function render() {
    const last = step === screens.length - 1;
    box.innerHTML = `
      <button class="icon-btn w-x" id="wX" aria-label="ガイドを閉じる">✕</button>
      <div class="w-prog" role="progressbar" aria-valuemin="1" aria-valuemax="${screens.length}" aria-valuenow="${step + 1}">
        ${TITLES.map((t, i) => `<button class="w-dot ${i < step ? "past" : ""} ${i === step ? "now" : ""}" data-go="${i}" ${i > step ? "disabled" : ""} title="${t}"><i>${i < step ? "✓" : i + 1}</i><span>${t}</span></button>`).join("")}
      </div>
      <div class="w-body ${dir > 0 ? "fwd" : "back"}">${screens[step]()}</div>
      <footer class="w-foot">
        <button class="btn small ghost" id="wSkip">${last ? "" : "スキップ"}</button>
        <span class="w-count">${step + 1} / ${screens.length}</span>
        <span>
          <button class="btn small" id="wBack" ${step === 0 ? "disabled" : ""}>‹ 戻る</button>
          ${last ? '<button class="btn small primary" id="wDone">閉じる</button>' : `<button class="btn small primary" id="wNext" >次へ ›</button>`}
        </span>
      </footer>`;
    const nx = $("#wNext") || $("#wDone");
    if (nx && !nx.disabled) nx.focus();
  }

  async function go(n) {
    if (n < 0 || n >= screens.length) return;
    dir = n > step ? 1 : -1;
    if (n === 0 && !demo) { step = n; render(); await loadDemo(); copied = false; }
    step = n;
    render();
    if (n === screens.length - 1 && !state.guideDone) {
      state.guideDone = true; save(); addXP(20); burst(innerWidth / 2, innerHeight / 3, 140); checkBadges();
    }
  }

  async function finish(action) {
    close();
    if (action === "cat" && cat()) { setTimeout(() => focusCat(cat().dir), 80); }
    if (action === "search") { $("#q").focus(); toast("🔎 キーワードを入力してみましょう（例：議事録）"); }
  }

  function open(startAt = 0) {
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("noting");
    copied = false;
    step = 0; dir = 1;
    go(startAt);
  }
  function close() {
    modal.hidden = true;
    document.body.classList.remove("noting");
    state.guideSeen = true; save();
    lastFocus && lastFocus.focus && lastFocus.focus();
  }

  box.addEventListener("click", async e => {
    const t = e.target;
    if (t.closest("#wX") || t.closest("#wSkip")) return close();
    if (t.closest("#wDone")) return finish("close");
    if (t.closest("#wNext")) return go(step + 1);
    if (t.closest("#wBack")) return go(step - 1);
    const dot = t.closest("[data-go]");
    if (dot && !dot.disabled) return go(+dot.dataset.go);
    if (t.closest("#wCopy")) {
      const ok = await copyText(demo.text);
      copied = ok;
      const r = t.closest("#wCopy").getBoundingClientRect();
      if (ok) { burst(r.left + r.width / 2, r.top, 60); addXP(3, r.left, r.top); window.dispatchEvent(new CustomEvent("guide-copied")); }
      render();
      return;
    }
    if (t.closest("#wOpenNote")) { const d = demo; close(); openNote(d.c.dir, d.f.path); return; }
    const way = t.closest("[data-way]");
    if (way) {
      close();
      if (way.dataset.way === "search") { $("#q").focus(); $("#q").value = "議事録"; $("#q").dispatchEvent(new Event("input")); }
      else if (way.dataset.way === "list") setTimeout(() => { const d = (cat() || PERSONAS[0]).dir; location.hash = "#samples"; focusCat(d); }, 80);
      else setMode("3d", { galaxy: true, dir: cat() ? cat().dir : null });
      return;
    }
    if (t.closest("#w3d")) { close(); setMode("3d", { galaxy: true, dir: cat() ? cat().dir : null }); return; }
    const en = t.closest("[data-end]");
    if (en) finish(en.dataset.end);
  });
  addEventListener("keydown", e => {
    if (modal.hidden) return;
    if (e.key === "Escape") { e.stopPropagation(); close(); }
    else if (e.key === "ArrowRight" && !$("#wNext")?.disabled && step < screens.length - 1) go(step + 1);
    else if (e.key === "ArrowLeft" && step > 0) go(step - 1);
  }, true);
  modal.addEventListener("pointerdown", e => { if (e.target === modal) close(); });

  $("#guideBtn").onclick = () => open();
  const hg = $("#heroGuide");
  if (hg) hg.onclick = () => open();
  if (!state.guideSeen && location.hash !== "#3d" && location.hash !== "#rpg" && location.hash !== "#galaxy") setTimeout(() => { if (modal.hidden && $("#noteModal").hidden) open(); }, 1200);
  return { open };
}
