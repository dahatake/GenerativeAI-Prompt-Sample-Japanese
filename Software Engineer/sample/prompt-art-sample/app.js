// 研修用の架空アプリ。意図的なバグを3つ含みます(Analyzer 側)。
const STORAGE_KEY_SAVE = 'prompts';

function loadPrompts() {
  // BUG #1: 保存は 'prompts' なのに、読み込みは 'promptList' を参照している
  return JSON.parse(localStorage.getItem('promptList') || '[]');
}

function savePrompt(entry) {
  const list = JSON.parse(localStorage.getItem(STORAGE_KEY_SAVE) || '[]');
  list.push(entry);
  localStorage.setItem(STORAGE_KEY_SAVE, JSON.stringify(list));
}

function buildText(text, purpose, tone) {
  const heads = { invite: 'ぜひお立ち寄りください', explain: '製品のポイントをご紹介します', survey: 'アンケートにご協力ください' };
  const tails = { friendly: '気軽にどうぞ!', formal: 'お待ち申し上げております。', energetic: '待ってます!' };
  return `${heads[purpose]}: ${text} ${tails[tone]}`;
}

function drawPreview(canvas, message) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#e8f1ff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#123';
  ctx.font = '16px sans-serif';
  ctx.fillText(message.slice(0, 40), 12, 40);
  if (message.length > 40) ctx.fillText(message.slice(40, 80), 12, 70);
}

function initBuilder() {
  const textEl = document.getElementById('promptText');
  const purposeEl = document.getElementById('purpose');
  const toneEl = document.getElementById('tone');
  const canvas = document.getElementById('previewCanvas');
  const msgEl = document.getElementById('builderMessage');

  document.getElementById('previewBtn').addEventListener('click', () => {
    drawPreview(canvas, buildText(textEl.value, purposeEl.value, toneEl.value));
  });
  document.getElementById('saveBtn').addEventListener('click', () => {
    if (!textEl.value.trim()) {
      msgEl.textContent = '入力テキストを入力してください。';
      return;
    }
    const message = buildText(textEl.value, purposeEl.value, toneEl.value);
    savePrompt({ text: message, purpose: purposeEl.value, tone: toneEl.value, savedAt: new Date().toISOString() });
    msgEl.textContent = '保存しました。';
  });
}

function analyze() {
  const items = loadPrompts();
  const errorEl = document.getElementById('analyzerError');
  errorEl.textContent = '';
  const listEl = document.getElementById('promptList');
  listEl.innerHTML = '';
  items.forEach((p) => {
    const li = document.createElement('li');
    li.textContent = `[${p.purpose}/${p.tone}] ${p.text}`;
    listEl.appendChild(li);
  });
  document.getElementById('statCount').textContent = items.length;
  document.getElementById('statAvgLength').textContent =
    Math.round(items.reduce((s, p) => s + p.text.length, 0) / items.length);
  // BUG #3: データ0件のとき items[0] が undefined で TypeError (Cannot read properties of undefined)
  document.getElementById('statLatest').textContent = items[items.length - 1].savedAt.slice(0, 10);
}

function initAnalyzer() {
  // BUG #2: HTML のボタン ID は analyzeBtn だが、analyzeButton を参照している
  const btn = document.getElementById('analyzeButton');
  if (btn) btn.addEventListener('click', analyze);
  analyze();
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('previewBtn')) initBuilder();
  if (document.getElementById('promptList')) initAnalyzer();
});
