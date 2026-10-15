// Promptのコツ：没入型プレゼンテーション
const SLIDES = [
  {
    emoji: "🧩", title: "Promptは、これだけでいい", color: ["#7f85f5", "#00b7c3"],
    lead: "4つの材料を並べるだけ。むずかしい書き方は不要です。",
    points: [
      ["🎯", "目的", "何のためにやるのか"],
      ["✅", "やってほしい事", "「やってほしい事は xxx。」"],
      ["🚫", "やってはいけない事", "「やってはいけない事は yyy。」"],
      ["📎", "情報・データ", "参考にしてほしい材料"]
    ],
    note: "「メールから案件情報を抽出して」の「案件情報」は、文書の項目・自社アプリの入力項目・APIの呼び出し項目にもなります😊",
    prompt: "【目的】営業会議で使う、今週の新規案件の一覧を作りたい。\n【やってほしい事】下のメール本文から、案件名・顧客名・金額・期限を抽出して表にしてください。\n【やってはいけない事】メールに書かれていない情報の推測や補完。不明な項目は「要確認」と書いてください。\n【情報・データ】<メール本文>（ここに貼り付け）</メール本文>"
  },
  {
    emoji: "🗂️", title: "ファイルじゃなくて、情報を渡す", color: ["#f5a623", "#ff5d8f"],
    lead: "メール・会議・チャット・予定表・文書・音声・動画・コード。すべて「情報」にしておこう。",
    points: [
      ["📧", "メール・チャット", "要約・返信案づくりに"],
      ["🎙️", "会議・音声・動画", "議事録化・翻訳に"],
      ["📄", "文書・予定表", "校正・整理に"],
      ["💻", "コード", "レビュー・生成に"]
    ],
    note: "大切なのはファイルではなく情報。ファイルは量産できるので、情報管理を意識しましょう。",
    prompt: "先週の「顧客A社」に関するメール・Teamsチャット・会議の内容をすべて情報として参照し、現在の状況・決まっていること・未解決の課題を、A社への次回提案の観点で時系列にまとめてください。出典（日付と送信者／会議名）も併記してください。"
  },
  {
    emoji: "✍️", title: "言葉不足を補う", color: ["#3fb950", "#58a6ff"],
    lead: "AIは文脈を知りません。書き足すほど、答えは磨かれます。",
    points: [
      ["📌", "参考資料は明示する", "必要な部分だけ抜き出して貼るのも有効"],
      ["🔢", "手順は番号付きで", "実行の順番がブレない"],
      ["🧵", "話題が変わったら別スレッド", "引き継ぎは要旨をまとめて貼る"],
      ["🙅", "推論・想像させない", "分からないことは捏造せず聞いてもらう"]
    ],
    note: "迷ったら「具体的に・順番に・根拠つきで」と覚えましょう。",
    prompt: "次の手順で作業してください。\n1. 添付の「2025年度_売上.xlsx」の「東日本」シートだけを参照する。\n2. 前年同月比がマイナスの月を抽出する。\n3. 原因の仮説を3つ、根拠となるデータの該当セルとともに示す。\n4. 資料にない数値は推測せず、「データなし」と書く。"
  },
  {
    emoji: "❓", title: "「わかんない事を、私に聞いて」", color: ["#9b5cff", "#ff5d8f"],
    lead: "AIに質問させると、業務のKnow-Howを言語化するきっかけにもなります。",
    points: [
      ["🙋", "AIが質問する", "判断できないことは聞いてもらう"],
      ["📝", "選択式の質問票", "答えやすく、抜け漏れが減る"],
      ["💡", "デフォルト案つき", "答えなくても最良案で進む"],
      ["🚫", "捏造は禁止", "分からないことは分からないと言う"]
    ],
    note: "言葉不足を補い、その業務のKnow-Howを言語化するきっかけにもなります。",
    prompt: "あなたが自分で判断できない全ての事については、質問事項を15～100個リストアップして、選択式の質問票を作成して、私の回答を得るようにしてください。私が答えなかった場合に備えて、目的を考慮して複数の選択肢から最良のものをデフォルトの回答案として作成し、その理由も書いてください。捏造は絶対に禁止です。"
  },
  {
    emoji: "🎯", title: "複数の案を作ってもらう", color: ["#ff5d8f", "#f5a623"],
    lead: "1案だけで決めない。比べるから、いい選択ができる。",
    points: [
      ["🔀", "3〜5案を出してもらう", "切り口の違う案を並べる"],
      ["📊", "評価軸で比較", "コスト・効果・実現性など"],
      ["🏆", "おすすめと理由", "選んだ根拠まで言語化"],
      ["🔧", "良いとこ取り", "案を組み合わせて仕上げる"]
    ],
    note: "評価軸を先に決めておくと、比較がぐっと楽になります。",
    prompt: "新入社員向けのAI研修の進め方について、切り口の異なる案を4つ作成してください。それぞれ「コスト」「習得スピード」「現場での定着しやすさ」を5段階で評価した比較表にまとめ、最後に最もおすすめの案とその理由を述べてください。"
  }
];

const el = (tag, cls, text) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
};

export function initTips() {
  const stage = document.getElementById("ptStage");
  if (!stage) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const total = SLIDES.length;
  let idx = 0, typer = 0;

  const bg = el("div", "pt-bg");
  bg.setAttribute("aria-hidden", "true");
  for (let i = 0; i < 14; i++) {
    const o = el("i", "pt-orb");
    o.style.cssText = `--x:${Math.random() * 100}%;--s:${30 + Math.random() * 90}px;--d:${8 + Math.random() * 10}s;--dl:${-Math.random() * 10}s`;
    bg.append(o);
  }
  const prog = el("div", "pt-progress");
  const bar = el("span");
  prog.append(bar);
  const view = el("div", "pt-view");
  view.setAttribute("aria-live", "polite");
  const nav = el("div", "pt-nav");
  const prev = el("button", "pt-btn", "◀ 戻る");
  const next = el("button", "pt-btn pt-next", "次へ ▶");
  const dots = el("div", "pt-dots");
  SLIDES.forEach((s, i) => {
    const d = el("button", "pt-dot", s.emoji);
    d.setAttribute("aria-label", `${i + 1}. ${s.title}`);
    d.onclick = () => go(i);
    dots.append(d);
  });
  prev.type = next.type = "button";
  nav.append(prev, dots, next);
  stage.append(bg, prog, view, nav);

  function burst(x, y, colors) {
    if (reduce) return;
    for (let i = 0; i < 26; i++) {
      const p = el("i", "pt-conf");
      const a = Math.random() * Math.PI * 2, r = 60 + Math.random() * 140;
      p.style.cssText = `left:${x}px;top:${y}px;background:${colors[i % 2]};--dx:${Math.cos(a) * r}px;--dy:${Math.sin(a) * r - 40}px;--rot:${Math.random() * 720}deg`;
      stage.append(p);
      setTimeout(() => p.remove(), 1100);
    }
  }

  function type(target, text) {
    clearInterval(typer);
    if (reduce) { target.textContent = text; return; }
    target.textContent = "";
    let i = 0;
    typer = setInterval(() => {
      i += 2;
      target.textContent = text.slice(0, i);
      if (i >= text.length) clearInterval(typer);
    }, 22);
  }

  function render(dir) {
    const s = SLIDES[idx];
    stage.style.setProperty("--c1", s.color[0]);
    stage.style.setProperty("--c2", s.color[1]);
    bar.style.width = ((idx + 1) / total) * 100 + "%";
    [...dots.children].forEach((d, i) => d.classList.toggle("on", i === idx));
    prev.disabled = idx === 0;
    next.textContent = idx === total - 1 ? "🎉 もう一度" : "次へ ▶";

    const slide = el("div", "pt-slide " + (dir < 0 ? "from-left" : "from-right"));
    const hero = el("div", "pt-hero");
    hero.append(el("div", "pt-emoji", s.emoji), el("div", "pt-count", `TIP ${idx + 1} / ${total}`));
    const h = el("h3", "pt-title", s.title);
    const lead = el("p", "pt-lead", s.lead);

    const pts = el("div", "pt-points");
    s.points.forEach(([ic, t, d], i) => {
      const c = el("div", "pt-point");
      c.style.setProperty("--i", i);
      c.append(el("span", "pt-pic", ic));
      const w = el("div");
      w.append(el("b", "", t), el("small", "", d));
      c.append(w);
      c.addEventListener("click", ev => { const r = stage.getBoundingClientRect(); burst(ev.clientX - r.left, ev.clientY - r.top, s.color); });
      pts.append(c);
    });

    const box = el("div", "pt-prompt");
    const head = el("div", "pt-phead");
    head.append(el("span", "", "✨ Promptの具体例"));
    const copy = el("button", "pt-copy", "📋 コピー");
    copy.type = "button";
    copy.onclick = async e => {
      try { await navigator.clipboard.writeText(s.prompt); copy.textContent = "✅ コピーしました"; }
      catch { copy.textContent = "⚠️ コピー不可"; }
      const r = stage.getBoundingClientRect();
      burst(e.clientX - r.left, e.clientY - r.top, s.color);
      setTimeout(() => (copy.textContent = "📋 コピー"), 1600);
    };
    head.append(copy);
    const code = el("pre", "pt-code");
    const txt = el("code");
    code.append(txt);
    box.append(head, code);

    slide.append(hero, h, lead, pts, box, el("p", "pt-note", "💬 " + s.note));
    view.replaceChildren(slide);
    type(txt, s.prompt);
  }

  function go(n) {
    const d = n >= idx ? 1 : -1;
    idx = (n + total) % total;
    render(d);
  }
  prev.onclick = () => go(idx - 1);
  next.onclick = () => { if (idx === total - 1) { go(0); return; } go(idx + 1); };
  stage.addEventListener("keydown", e => {
    if (e.key === "ArrowRight") { e.preventDefault(); if (idx < total - 1) go(idx + 1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); if (idx > 0) go(idx - 1); }
  });
  let sx = null;
  stage.addEventListener("touchstart", e => (sx = e.touches[0].clientX), { passive: true });
  stage.addEventListener("touchend", e => {
    if (sx === null) return;
    const dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 60) { if (dx < 0 && idx < total - 1) go(idx + 1); else if (dx > 0 && idx > 0) go(idx - 1); }
    sx = null;
  });
  render(1);
}
