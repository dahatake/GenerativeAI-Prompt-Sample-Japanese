// RPGモード：ファミコン時代の2D RPG風に、街や城を巡ってサンプルPromptを探します。
// 画像・音声ファイルは使わず、キャラクター・地図タイル・効果音・BGMはすべてコードで生成したオリジナルです。
import { CATALOG, GROUPS } from "./catalog.js";
import { COPILOTS } from "./data.js";
import { openNote } from "./notes.js";

const T = 16, VW = 16, VH = 14;
const BLOCK = new Set("~^#PhB");
const DIRS = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
const KEYS = {
  ArrowUp: "up", w: "up", ArrowDown: "down", s: "down", ArrowLeft: "left", a: "left", ArrowRight: "right", d: "right",
  z: "a", Enter: "a", " ": "a", j: "a", x: "b", Escape: "b", Backspace: "b", k: "b"
};
const INK = "#101018";
const $ = s => document.querySelector(s);
const mk = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h; return c; };

/* ---------- ピクセル描画の道具 ---------- */
function outline(c) {
  const x = c.getContext("2d"), w = c.width, h = c.height, img = x.getImageData(0, 0, w, h), a = img.data;
  for (let i = 3; i < a.length; i += 4) a[i] = a[i] > 127 ? 255 : 0;
  x.putImageData(img, 0, 0);
  const op = (i, j) => i >= 0 && j >= 0 && i < w && j < h && a[(j * w + i) * 4 + 3] > 0;
  const add = [];
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (!op(i, j) && (op(i - 1, j) || op(i + 1, j) || op(i, j - 1) || op(i, j + 1))) add.push([i, j]);
  x.fillStyle = INK;
  add.forEach(([i, j]) => x.fillRect(i, j, 1, 1));
  return c;
}
const painter = x => (X, Y, W, H, col) => { x.fillStyle = col; x.fillRect(X, Y, W, H); };

/* ---------- キャラクター ---------- */
const PALS = [
  { h: "#6b4423", s: "#f5c9a0", c: "#d8403a", d: "#7a2a2a" },
  { h: "#2a2a3a", s: "#f0b890", c: "#3aa65c", d: "#1f6b38" },
  { h: "#e0b030", s: "#f5c9a0", c: "#7f85f5", d: "#464aa0", acc: ["long"] },
  { h: "#8a3a1a", s: "#e8b088", c: "#e08a20", d: "#8a5010" },
  { h: "#2a2a3a", s: "#f5c9a0", c: "#c04fa0", d: "#702a60", acc: ["long"] },
  { h: "#4a4a5a", s: "#f0b890", c: "#00a8b8", d: "#0a6a78", acc: ["hat"] },
  { h: "#303030", s: "#e8b088", c: "#a0a8b8", d: "#586070", acc: ["helm"] },
  { h: "#7a5a2a", s: "#f5c9a0", c: "#5a8ad8", d: "#2a4a90" }
];
const HERO = { h: "#5b3a1e", s: "#f5c9a0", c: "#3a6fd8", d: "#1c3a8a" };
const KING = { h: "#e8e8f0", s: "#f5c9a0", c: "#b01830", d: "#601020", acc: ["crown", "beard"] };
const MAYOR = { h: "#e8e8f0", s: "#f0b890", c: "#8a5a2a", d: "#4a2a10", acc: ["beard", "hat"] };
const spriteCache = new Map();
function charSprite(p, dir, f) {
  const key = JSON.stringify(p) + dir + f;
  if (spriteCache.has(key)) return spriteCache.get(key);
  const c = mk(16, 16), x = c.getContext("2d"), r = painter(x), acc = p.acc || [], b = "#7a4a1a", y = "#f0c030";
  if (dir === "side") {
    r(8, 6, 4, 4, p.h); r(4, 2, 8, 5, p.h); r(4, 6, 4, 4, p.s); r(5, 7, 1, 2, INK);
    r(4, 10, 8, 4, p.c); r(4, 12, 8, 1, y); r(6, 10, 3, 3, p.d); r(6, 13, 2, 1, p.s);
    if (f) { r(6, 14, 4, 1, p.d); r(6, 15, 4, 1, b); } else { r(5, 14, 3, 1, p.d); r(8, 14, 3, 1, p.d); r(4, 15, 3, 1, b); r(8, 15, 3, 1, b); }
    if (acc.includes("long")) r(9, 6, 3, 6, p.h);
  } else {
    r(4, 2, 8, 5, p.h); r(3, 4, 1, 4, p.h); r(12, 4, 1, 4, p.h);
    if (dir === "down") { r(5, 6, 6, 4, p.s); r(6, 7, 1, 2, INK); r(9, 7, 1, 2, INK); } else r(5, 6, 6, 4, p.h);
    r(3, 10, 10, 4, p.c); r(2, 10, 1, 3, p.c); r(13, 10, 1, 3, p.c); r(2, 13, 1, 1, p.s); r(13, 13, 1, 1, p.s); r(3, 12, 10, 1, y);
    r(4, 14, 3, 1, p.d); r(9, 14, 3, 1, p.d); r(4, 15, 3, 1, b); r(9, 15, 3, 1, b);
    if (acc.includes("long")) { r(3, 6, 2, 6, p.h); r(11, 6, 2, 6, p.h); }
    if (acc.includes("beard") && dir === "down") r(5, 9, 6, 2, "#e8e8f0");
  }
  if (acc.includes("crown")) { r(4, 1, 8, 2, y); r(4, 0, 1, 1, y); r(7, 0, 2, 1, y); r(11, 0, 1, 1, y); }
  if (acc.includes("helm")) { r(3, 1, 10, 4, "#9aa0b0"); if (dir === "down") r(5, 5, 6, 1, "#6a7080"); r(7, 0, 2, 1, "#d8403a"); }
  if (acc.includes("hat")) { r(2, 3, 12, 1, p.c); r(5, 0, 6, 3, p.c); }
  outline(c);
  let out = c;
  if ((dir !== "side" && f) || dir === "right") {
    out = mk(16, 16);
    const o = out.getContext("2d");
    o.translate(16, 0); o.scale(-1, 1); o.drawImage(c, 0, 0);
  }
  spriteCache.set(key, out);
  return out;
}
function signSprite() {
  const c = mk(16, 16), r = painter(c.getContext("2d"));
  r(7, 9, 2, 6, "#7a4a1a"); r(2, 3, 12, 7, "#c08a3a"); r(3, 4, 10, 1, "#7a4a1a"); r(3, 6, 10, 1, "#7a4a1a"); r(3, 8, 7, 1, "#7a4a1a");
  return outline(c);
}
const MONS = [
  { name: "ハルシネスライム", k: 0 },
  { name: "プロンプトゴースト", k: 1 },
  { name: "バグバット", k: 2 }
];
function monsterSprite(k) {
  const c = mk(32, 32), x = c.getContext("2d"), r = painter(x);
  if (k === 0) {
    for (let j = 0; j < 32; j++) for (let i = 0; i < 32; i++) {
      const dx = (i - 16) / 14, dy = (j - 19) / 11;
      if (dx * dx + dy * dy <= 1 && j > 7) r(i, j, 1, 1, j > 26 ? "#2a70c8" : "#4aa0f0");
    }
    r(7, 12, 4, 3, "#bfe0ff"); r(10, 19, 3, 4, INK); r(19, 19, 3, 4, INK); r(10, 19, 1, 1, "#fff"); r(19, 19, 1, 1, "#fff"); r(13, 25, 6, 1, INK);
    r(15, 4, 2, 4, "#2a70c8"); r(14, 2, 4, 3, "#f0c030");
  } else if (k === 1) {
    for (let j = 0; j < 32; j++) for (let i = 0; i < 32; i++) {
      const dx = (i - 16) / 10, dy = (j - 13) / 10;
      if (dx * dx + dy * dy <= 1 || (j >= 13 && j < 27 + (i % 6 < 3 ? 3 : 0) && i >= 6 && i < 26)) r(i, j, 1, 1, j > 22 ? "#b8b8d8" : "#e8e8f8");
    }
    r(11, 12, 3, 5, INK); r(18, 12, 3, 5, INK); r(14, 20, 4, 3, INK);
  } else {
    x.fillStyle = "#6a3a9c";
    x.beginPath(); x.moveTo(11, 15); x.lineTo(1, 6); x.lineTo(3, 18); x.lineTo(6, 16); x.lineTo(8, 25); x.lineTo(12, 20); x.fill();
    x.beginPath(); x.moveTo(21, 15); x.lineTo(31, 6); x.lineTo(29, 18); x.lineTo(26, 16); x.lineTo(24, 25); x.lineTo(20, 20); x.fill();
    for (let j = 0; j < 32; j++) for (let i = 0; i < 32; i++) { const dx = (i - 16) / 6, dy = (j - 17) / 8; if (dx * dx + dy * dy <= 1) r(i, j, 1, 1, "#8a52c0"); }
    r(11, 7, 3, 4, "#8a52c0"); r(18, 7, 3, 4, "#8a52c0"); r(13, 14, 2, 2, "#ff4040"); r(18, 14, 2, 2, "#ff4040"); r(14, 21, 4, 2, "#fff");
  }
  return outline(c);
}

/* ---------- 地図タイル ---------- */
const tileCache = {};
function tile(name, fn) { const c = mk(T, T); fn(painter(c.getContext("2d")), c.getContext("2d")); tileCache[name] = c; }
function initTiles() {
  const grass = (r, s = 0) => { r(0, 0, 16, 16, "#3da83d"); for (let i = 0; i < 6; i++) r((i * 7 + s * 3) % 15, (i * 5 + s * 7) % 14, 2, 1, "#2e8a2e"); };
  const floorBase = (r, a, b) => { r(0, 0, 16, 16, a); r(0, 7, 16, 1, b); r(0, 15, 16, 1, b); r(7, 0, 1, 8, b); r(3, 8, 1, 8, b); r(12, 8, 1, 8, b); };
  tile(".", r => grass(r));
  tile("T", r => { grass(r, 1); r(6, 11, 4, 4, "#6a3a1a"); r(2, 1, 12, 11, "#1e6a2a"); r(4, 0, 8, 2, "#1e6a2a"); r(4, 3, 3, 2, "#3a9a3a"); r(9, 6, 3, 2, "#3a9a3a"); });
  tile("^", (r, x) => {
    grass(r, 2);
    x.fillStyle = "#8a6a4a"; x.beginPath(); x.moveTo(0, 15); x.lineTo(8, 1); x.lineTo(16, 15); x.fill();
    x.fillStyle = "#6a4a30"; x.beginPath(); x.moveTo(8, 1); x.lineTo(16, 15); x.lineTo(9, 15); x.fill();
    r(6, 3, 4, 3, "#fff");
  });
  const water = (n, o) => tile(n, r => { r(0, 0, 16, 16, "#2850d0"); [[2, 3], [9, 2], [5, 9], [12, 11]].forEach(([a, b]) => r((a + o) % 15, b, 3, 1, "#5a8af0")); });
  water("~0", 0); water("~1", 3);
  tile("=", r => { r(0, 0, 16, 16, "#d8b070"); [[2, 3], [10, 5], [5, 11], [13, 12]].forEach(([a, b]) => r(a, b, 2, 1, "#b88a48")); });
  tile("C", r => {
    grass(r, 3);
    r(2, 6, 12, 9, "#c0c0cc"); r(1, 2, 4, 13, "#a8a8b8"); r(11, 2, 4, 13, "#a8a8b8");
    [1, 3].forEach(a => r(a, 1, 1, 2, "#a8a8b8")); [11, 13].forEach(a => r(a, 1, 1, 2, "#a8a8b8")); r(5, 4, 6, 2, "#c0c0cc");
    r(7, 0, 1, 4, "#6a4a1a"); r(8, 0, 3, 2, "#d8403a"); r(6, 10, 4, 5, INK); r(2, 8, 2, 1, "#6a6a80"); r(12, 8, 2, 1, "#6a6a80");
  });
  tile("V", r => {
    grass(r, 4);
    r(1, 8, 6, 6, "#e8d0a0"); r(9, 6, 6, 8, "#e8d0a0"); r(0, 6, 8, 2, "#d8403a"); r(1, 5, 6, 1, "#d8403a"); r(8, 4, 8, 2, "#3a6fd8"); r(9, 3, 6, 1, "#3a6fd8");
    r(3, 11, 2, 3, "#6a3a1a"); r(11, 10, 2, 4, "#6a3a1a"); r(10, 8, 2, 2, "#8ac0f0");
  });
  const brick = (r, a, b) => { r(0, 0, 16, 16, a); r(0, 5, 16, 1, b); r(0, 10, 16, 1, b); r(0, 15, 16, 1, b); r(4, 0, 1, 5, b); r(11, 6, 1, 4, b); r(4, 11, 1, 4, b); };
  tile("_brick", r => floorBase(r, "#8a8a98", "#6a6a7a"));
  tile("_wood", r => { r(0, 0, 16, 16, "#b88a50"); [3, 7, 11, 15].forEach(a => r(0, a, 16, 1, "#8a6030")); r(5, 0, 1, 3, "#8a6030"); r(11, 8, 1, 3, "#8a6030"); });
  tile("#", r => brick(r, "#4a4a68", "#2a2a3e"));
  tile("R", r => { r(0, 0, 16, 16, "#b01818"); r(0, 0, 2, 16, "#f0c030"); r(14, 0, 2, 16, "#f0c030"); r(7, 6, 2, 2, "#e04040"); });
  tile("D", r => { brick(r, "#4a4a68", "#2a2a3e"); r(3, 2, 10, 14, "#6a3a1a"); r(5, 0, 6, 2, "#6a3a1a"); r(4, 3, 8, 13, "#8a5a2a"); r(10, 9, 2, 2, "#f0c030"); });
  tile("P", (r) => { floorBase(r, "#8a8a98", "#6a6a7a"); r(4, 0, 8, 16, "#d8d8e4"); r(4, 0, 2, 16, "#f4f4fa"); r(10, 0, 2, 16, "#a8a8b8"); r(3, 0, 10, 2, "#c0c0d0"); r(3, 14, 10, 2, "#c0c0d0"); });
  tile("h", r => { r(0, 0, 16, 16, "#b01818"); r(2, 1, 12, 14, "#f0c030"); r(4, 3, 8, 7, "#d82040"); r(2, 10, 12, 2, "#c89820"); });
  tile("B", r => { brick(r, "#4a4a68", "#2a2a3e"); r(1, 1, 14, 14, "#6a3a1a"); r(1, 7, 14, 1, "#3a1a0a"); ["#d8403a", "#3a6fd8", "#3aa65c", "#f0c030", "#c04fa0"].forEach((col, i) => { r(2 + i * 3, 2, 2, 5, col); r(2 + ((i * 3 + 4) % 12), 9, 2, 5, ["#f0c030", "#3aa65c", "#d8403a"][i % 3]); }); });
}

/* ---------- 地図 ---------- */
const hash = (x, y, s = 0) => { let h = (x * 374761393 + y * 668265263 + s * 2147483647) | 0; h = (h ^ (h >>> 13)) * 1274126177 | 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967295; };
const vnoise = (x, y, s) => {
  const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const a = hash(xi, yi, s), b = hash(xi + 1, yi, s), c = hash(xi, yi + 1, s), d = hash(xi + 1, yi + 1, s);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
};
const SITES = [{ id: "role", x: 12, y: 9 }, { id: "work", x: 35, y: 9 }, { id: "make", x: 35, y: 27 }, { id: "learn", x: 12, y: 27 }];
const START = { x: 24, y: 18 };

function buildWorld() {
  const W = 48, H = 36, g = Array.from({ length: H }, () => Array(W).fill("~"));
  for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {
    const d = ((x - 24) / 21.5) ** 2 + ((y - 18) / 16) ** 2 + (vnoise(x / 4, y / 4, 1) - .5) * .55;
    if (d >= 1) continue;
    g[y][x] = vnoise(x / 3.2, y / 3.2, 2) > .68 ? "^" : vnoise(x / 2.6, y / 2.6, 3) > .62 ? "T" : vnoise(x / 3, y / 3, 5) > .8 ? "~" : ".";
  }
  const set = (x, y, c) => { if (x > 0 && y > 0 && x < W - 1 && y < H - 1) g[y][x] = c; };
  const events = {};
  for (const s of SITES) {
    for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) set(s.x + dx, s.y + dy, ".");
    for (let y = Math.min(s.y + 1, START.y); y <= Math.max(s.y + 1, START.y); y++) set(s.x, y, "=");
    for (let x = Math.min(s.x, START.x); x <= Math.max(s.x, START.x); x++) set(x, START.y, "=");
    const gr = GROUPS.find(q => q.id === s.id);
    set(s.x, s.y, gr.rpg.kind === "castle" ? "C" : "V");
    events[`${s.x},${s.y}`] = { enter: s.id };
  }
  return { id: "world", name: "Promptの せかい", w: W, h: H, tiles: g, npcs: [], events, bgm: "rpgField", world: true };
}

function buildPlace(gr) {
  const cats = CATALOG.filter(c => c.group === gr.id);
  const castle = gr.rpg.kind === "castle", W = castle ? 17 : 15, H = castle ? 14 : 11, cx = (W - 1) / 2;
  const t = Array.from({ length: H }, (_, y) => Array.from({ length: W }, (_, x) => (x === 0 || y === 0 || x === W - 1 || y === H - 1 ? "#" : "_")));
  for (let y = 2; y < H - 1; y++) t[y][cx] = "R";
  t[1][cx] = "h"; t[H - 1][cx] = "D";
  if (castle) { [[2, 2], [W - 3, 2]].forEach(([x, y]) => (t[y][x] = "P")); for (let x = 2; x < W - 2; x += 2) if (Math.abs(x - cx) > 1) t[0][x] = "B"; }
  const cols = castle ? [3, 6, cx + 2, cx + 5] : [2, 4, cx + 3, cx + 5], rows = castle ? [4, 7, 10] : [4, 7];
  const slots = rows.flatMap(y => cols.map(x => [x, y]));
  const npcs = [{ x: cx, y: 2, type: "king", pal: castle ? KING : MAYOR, dir: "down", name: gr.rpg.king }];
  cats.forEach((c, i) => npcs.push({ x: slots[i][0], y: slots[i][1], type: "cat", cat: c, pal: PALS[i % PALS.length], dir: "down", name: c.dir }));
  npcs.push({ x: cx + 3, y: H - 2, type: "sign", dir: "down", name: "あんないふだ" });
  return { id: gr.id, name: gr.rpg.place, w: W, h: H, tiles: t, npcs, group: gr, cats, floor: castle ? "_brick" : "_wood", bgm: castle ? "rpgCastle" : "rpgTown", start: { x: cx, y: H - 2 }, events: {} };
}

const paginate = (t, n = 56) => {
  const out = []; let cur = "";
  for (const part of t.match(/[^。！？]+[。！？]?/g) || [t]) {
    if (cur && (cur + part).length > n) { out.push(cur); cur = ""; }
    cur += part;
    while (cur.length > n + 14) { out.push(cur.slice(0, n)); cur = cur.slice(n); }
  }
  if (cur) out.push(cur);
  return out;
};
const level = xp => Math.floor(xp / 100) + 1;

export function initRpg({ state, save, addXP, toast, burst, checkBadges, sfx, setMood, exit }) {
  initTiles();
  const cvs = $("#rpgCanvas"), g = cvs.getContext("2d"), scr = $("#rpgScreen");
  g.imageSmoothingEnabled = false;
  const world = buildWorld();
  const maps = { world };
  GROUPS.forEach(gr => (maps[gr.id] = buildPlace(gr)));
  const monImgs = MONS.map(m => monsterSprite(m.k));
  const sign = signSprite();
  state.rpgCats = state.rpgCats || []; state.rpgPlaces = state.rpgPlaces || []; state.rpgWins = state.rpgWins || 0;

  const mkWin = cls => { const d = document.createElement("div"); d.className = "rpg-win " + cls; d.hidden = true; scr.append(d); return d; };
  const msgEl = mkWin("rpg-msg"), menuEl = mkWin("rpg-menu"), stEl = mkWin("rpg-status");
  msgEl.setAttribute("aria-live", "polite");

  const hero = { x: START.x, y: START.y, dir: "down", p: 0, moving: false, frame: 0, steps: 0, hp: 0 };
  const maxHp = () => 12 + (level(state.xp) - 1) * 3;
  hero.hp = maxHp();
  let map = world, active = false, raf = 0, last = 0, clock = 0, trans = null, msg = null, menu = null, battle = null, intro = false;
  const held = [];

  const busyModal = () => ["#noteModal", "#modal", "#wizModal"].some(s => $(s) && !$(s).hidden);
  const npcAt = (x, y) => map.npcs.find(n => n.x === x && n.y === y);
  const walkable = (x, y) => x >= 0 && y >= 0 && x < map.w && y < map.h && !BLOCK.has(map.tiles[y][x]) && !npcAt(x, y);

  /* ---------- メッセージ・メニュー ---------- */
  function say(text, then) {
    const pages = (Array.isArray(text) ? text : [text]).flatMap(t => paginate(t));
    msg = { pages, i: 0, acc: 0, shown: 0, done: false, finished: false, then };
    msgEl.hidden = false;
    renderMsg();
  }
  function renderMsg() {
    const m = msg, full = m.pages[m.i];
    msgEl.innerHTML = `<span class="tx"></span><i class="nx" ${m.done ? "" : "hidden"}>▼</i>`;
    msgEl.firstChild.textContent = full.slice(0, m.shown);
  }
  function advance() {
    const m = msg, full = m.pages[m.i];
    if (!m.done) { m.shown = full.length; m.done = true; renderMsg(); return; }
    sfx("rpgOk");
    if (m.i < m.pages.length - 1) { m.i++; m.shown = 0; m.acc = 0; m.done = false; renderMsg(); return; }
    m.finished = true;
    const t = m.then; m.then = null;
    if (t) t();
    if (msg === m && !menu) hideMsg();
  }
  function hideMsg() { msg = null; msgEl.hidden = true; }
  function openMenu(items, { cls = "m-tl", cancel = true, onCancel, status = false } = {}) {
    menu = { items, sel: 0, cancel, onCancel };
    menuEl.className = "rpg-win rpg-menu " + cls;
    menuEl.hidden = false;
    showStatus(status);
    renderMenu();
  }
  function renderMenu() {
    menuEl.innerHTML = menu.items.map((it, i) => `<div class="it${i === menu.sel ? " on" : ""}" data-i="${i}"><b>${i === menu.sel ? "▶" : ""}</b>${it.label.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]))}</div>`).join("");
  }
  function closeMenu() {
    menu = null; menuEl.hidden = true; showStatus(false);
    if (msg && msg.finished) hideMsg();
  }
  function choose(i) {
    const it = menu.items[i];
    closeMenu();
    sfx("rpgOk");
    it.fn();
  }
  function showStatus(on) {
    stEl.hidden = !on;
    if (on) stEl.innerHTML = `<div>ゆうしゃ</div><div>Lv ${level(state.xp)}</div><div>HP ${hero.hp}/${maxHp()}</div><div>XP ${state.xp}</div>`;
  }

  /* ---------- コマンド（Aボタン） ---------- */
  function commandMenu() {
    sfx("rpgOk");
    openMenu([
      { label: "はなす", fn: talk },
      { label: "つよさ", fn: stats },
      { label: "もくじ", fn: toc },
      { label: "おんがく", fn: toggleBgm },
      { label: "2Dへもどる", fn: exit }
    ], { status: true });
  }
  function stats() {
    const total = CATALOG.length;
    say([`ゆうしゃ Lv.${level(state.xp)}　けいけんち ${state.xp}　HP ${hero.hp}/${maxHp()}`, `おとずれた まち・しろ：${state.rpgPlaces.length}/${GROUPS.length}　はなした ばんにん：${state.rpgCats.length}/${total}　たおした モンスター：${state.rpgWins}`]);
  }
  function toc() {
    say(["【もくじ】 まちや しろごとに Promptが わけられているぞ。", ...GROUPS.map(gr => `${gr.rpg.place}（${gr.name}）：${CATALOG.filter(c => c.group === gr.id).map(c => c.dir).join("、")}`)]);
  }
  function toggleBgm() {
    const cb = $("#sBgm");
    cb.checked = !cb.checked;
    cb.dispatchEvent(new Event("input", { bubbles: true }));
    say(cb.checked ? "おんがくを ながした。" : "おんがくを とめた。");
  }
  function talk() {
    const [dx, dy] = DIRS[hero.dir], n = npcAt(hero.x + dx, hero.y + dy);
    if (!n) return say("そのほうこうには だれもいない。");
    const opp = { up: "down", down: "up", left: "right", right: "left" };
    n.dir = opp[hero.dir];
    if (n.type === "sign") {
      const gr = map.group;
      return say([`【${gr.rpg.place}】${gr.name}の あんないふだ。`, `ここには ${map.cats.map(c => `${c.dir}(${c.count})`).join("、")} の ばんにんが いる。`, "ばんにんに はなしかけて、ほしい Promptを さがそう。"]);
    }
    if (n.type === "king") {
      const gr = map.group, nPrompt = map.cats.reduce((s, c) => s + c.count, 0);
      return say([`「よくぞ きた、ぼうけんしゃよ。ここは ${gr.rpg.place}。`, `${gr.name}。${gr.hint}の Promptを あつめておる。`, `${map.cats.length}にんの ばんにんが ${nPrompt}この Promptを まもっておるぞ。」`]);
    }
    const c = n.cat;
    if (!state.rpgCats.includes(c.dir)) { state.rpgCats.push(c.dir); addXP(4); save(); checkBadges(); }
    say([`「わしは『${c.dir}』の ばんにんじゃ。」${c.role ? `（${c.role}）` : ""}`, c.desc, `ここには ${c.count}この Promptが ある。どうする？`], () => openMenu([
      { label: "ノートを ひらく", fn: () => open(c, c.startPath) },
      { label: "Promptを えらぶ", fn: () => pick(c, 0) },
      { label: "やめる", fn: () => { } }
    ], { cls: "m-ans" }));
  }
  function open(c, path) {
    if (!path) return say("まだ Promptが ないようじゃ。");
    openNote(c.dir, path);
  }
  function pick(c, page) {
    const per = 6, fs = c.files.slice(page * per, page * per + per);
    const items = fs.map(f => ({ label: f.title.slice(0, 20), fn: () => open(c, f.path) }));
    if ((page + 1) * per < c.files.length) items.push({ label: "つぎへ ▼", fn: () => pick(c, page + 1) });
    if (page > 0) items.push({ label: "まえへ ▲", fn: () => pick(c, page - 1) });
    items.push({ label: "やめる", fn: () => { } });
    openMenu(items, { cls: "m-ans" });
  }

  /* ---------- 画面遷移 ---------- */
  function fade(mid, d = .55) { trans = { t: 0, d, mid, swapped: false }; }
  function goMap(id, x, y, dir, snd) {
    fade(() => {
      map = maps[id];
      hero.x = x; hero.y = y; hero.dir = dir; hero.moving = false; hero.p = 0;
      $("#rpgLoc").textContent = "📍 " + map.name;
      setMood(map.bgm);
      sfx(snd);
      if (!map.world) {
        const healed = hero.hp < maxHp();
        hero.hp = maxHp();
        if (!state.rpgPlaces.includes(id)) { state.rpgPlaces.push(id); addXP(10); save(); checkBadges(); }
        say([`${map.name}に ついた。`, ...(healed ? ["HPが かいふくした！"] : [])]);
      }
    });
  }
  function enterTile() {
    const ev = map.events[`${hero.x},${hero.y}`];
    if (ev && ev.enter) {
      const m = maps[ev.enter];
      return goMap(ev.enter, m.start.x, m.start.y, "up", "rpgEnter");
    }
    if (map.tiles[hero.y][hero.x] === "D") {
      const s = SITES.find(q => q.id === map.id);
      return goMap("world", s.x, s.y + 1, "down", "rpgLeave");
    }
    if (map.world) {
      hero.steps++;
      const ch = map.tiles[hero.y][hero.x] === "T" ? .12 : .06;
      if (hero.steps > 8 && Math.random() < ch) { hero.steps = 0; fade(startBattle, .7); sfx("rpgEncounter"); }
    }
  }

  /* ---------- 戦闘（クイズ形式） ---------- */
  const quizzes = COPILOTS.flatMap(c => c.quiz);
  function startBattle() {
    const k = Math.floor(Math.random() * MONS.length);
    battle = { mon: MONS[k], img: monImgs[k], hp: 2, shake: 0, flash: 0 };
    setMood("rpgBattle");
    say([`${battle.mon.name}が あらわれた！`], battleMenu);
  }
  function battleMenu() {
    openMenu([
      { label: "たたかう", fn: ask },
      { label: "にげる", fn: flee }
    ], { status: true, cancel: false });
  }
  function ask() {
    const q = quizzes[Math.floor(Math.random() * quizzes.length)];
    say(["モンスターの もんだい！", q.q], () => openMenu(
      q.a.map((a, i) => ({ label: a, fn: () => answer(q, i === q.correct) })),
      { cls: "m-wide", onCancel: battleMenu }
    ));
  }
  function answer(q, ok) {
    const b = battle;
    if (ok) {
      sfx("rpgHit"); b.hp--; b.shake = .4;
      if (b.hp <= 0) return win();
      return say([`せいかい！ こうげきが きまった！`, q.why, `${b.mon.name}は まだ たおれない！`], battleMenu);
    }
    const dmg = 2 + Math.floor(Math.random() * 3);
    hero.hp = Math.max(0, hero.hp - dmg);
    sfx("rpgHurt"); b.flash = .4;
    say([`ざんねん！ ${b.mon.name}の こうげき！ ゆうしゃは ${dmg}ポイントの ダメージを うけた！`, q.why], hero.hp <= 0 ? lose : battleMenu);
  }
  function flee() {
    if (Math.random() < .75) { sfx("rpgFlee"); return say("うまく にげきれた！", endBattle); }
    hero.hp = Math.max(0, hero.hp - 2); sfx("rpgHurt"); battle.flash = .4;
    say("にげられない！ 2ポイントの ダメージ！", hero.hp <= 0 ? lose : battleMenu);
  }
  function win() {
    sfx("rpgWin");
    const xp = 12;
    state.rpgWins++; addXP(xp); save(); checkBadges();
    burst(innerWidth / 2, innerHeight / 2, 80);
    say([`${battle.mon.name}を たおした！`, `${xp}ポイントの けいけんちを かくとく！`], endBattle);
  }
  function lose() {
    sfx("rpgLose");
    say(["ゆうしゃは ちからつきた…", "きがつくと、はじまりの ばしょに もどっていた。"], () => {
      hero.hp = maxHp(); hero.x = START.x; hero.y = START.y;
      endBattle();
    });
  }
  function endBattle() { battle = null; hero.steps = 0; setMood(map.bgm); }

  /* ---------- 入力 ---------- */
  function press(k) {
    if (menu) {
      if (k === "up" || k === "down") { menu.sel = (menu.sel + (k === "up" ? -1 : 1) + menu.items.length) % menu.items.length; sfx("rpgCursor"); renderMenu(); }
      else if (k === "a") choose(menu.sel);
      else if (k === "b" && (menu.cancel || menu.onCancel)) { const f = menu.onCancel; closeMenu(); sfx("rpgCancel"); f && f(); }
    } else if (msg) {
      if (k === "a" || k === "b") advance();
    } else if (!trans && !battle && k === "a") commandMenu();
  }
  const typing = e => /INPUT|TEXTAREA|SELECT/.test((e.target.tagName || ""));
  function onKeyDown(e) {
    if (!active || busyModal() || typing(e) || e.ctrlKey || e.metaKey || e.altKey) return;
    const k = KEYS[e.key.length === 1 ? e.key.toLowerCase() : e.key];
    if (!k) return;
    e.preventDefault();
    if (k in DIRS) {
      if (!held.includes(k)) held.push(k);
      if (menu) press(k);
    } else if (!e.repeat) press(k);
  }
  function onKeyUp(e) {
    const k = KEYS[e.key.length === 1 ? e.key.toLowerCase() : e.key];
    const i = held.indexOf(k);
    if (i >= 0) held.splice(i, 1);
  }
  addEventListener("keydown", onKeyDown);
  addEventListener("keyup", onKeyUp);
  addEventListener("blur", () => (held.length = 0));
  $("#rpgPad").addEventListener("pointerdown", e => {
    const b = e.target.closest("button");
    if (!b) return;
    e.preventDefault();
    const k = KEYS[b.dataset.k];
    if (k in DIRS) { if (!held.includes(k)) held.push(k); if (menu) press(k); } else press(k);
  });
  const release = e => { const b = e.target.closest && e.target.closest("button[data-k]"); if (b) { const i = held.indexOf(KEYS[b.dataset.k]); if (i >= 0) held.splice(i, 1); } };
  $("#rpgPad").addEventListener("pointerup", release);
  $("#rpgPad").addEventListener("pointerleave", () => (held.length = 0), true);
  $("#rpgPad").addEventListener("pointercancel", () => (held.length = 0));
  menuEl.addEventListener("pointerdown", e => {
    const it = e.target.closest(".it");
    if (!it || !menu) return;
    menu.sel = +it.dataset.i; renderMenu(); choose(menu.sel);
  });
  msgEl.addEventListener("pointerdown", () => { if (msg && !menu) advance(); });

  /* ---------- 更新・描画 ---------- */
  function update(dt) {
    clock += dt;
    if (busyModal()) return;
    if (battle) { battle.shake = Math.max(0, battle.shake - dt); battle.flash = Math.max(0, battle.flash - dt); }
    if (trans) {
      trans.t += dt;
      if (!trans.swapped && trans.t >= trans.d / 2) { trans.swapped = true; trans.mid(); }
      if (trans.t >= trans.d) trans = null;
      return;
    }
    if (msg && !msg.done) {
      msg.acc += dt;
      const n = Math.min(msg.pages[msg.i].length, Math.floor(msg.acc * 32));
      if (n !== msg.shown) {
        if (n % 2 === 0) sfx("rpgTalk");
        msg.shown = n;
        if (n >= msg.pages[msg.i].length) msg.done = true;
        renderMsg();
      }
    }
    if (menu || msg || battle) return;
    if (hero.moving) {
      hero.p += dt / .17;
      if (hero.p >= 1) {
        const [dx, dy] = DIRS[hero.dir];
        hero.x += dx; hero.y += dy; hero.p = 0; hero.moving = false; hero.frame ^= 1;
        enterTile();
      }
    }
    if (!hero.moving && !trans && !menu && !msg && !battle && held.length) {
      const d = held[held.length - 1], [dx, dy] = DIRS[d];
      hero.dir = d;
      if (walkable(hero.x + dx, hero.y + dy)) hero.moving = true;
      else if (!hero.bumped) { hero.bumped = true; sfx("rpgBump"); setTimeout(() => (hero.bumped = false), 280); }
    }
  }
  function drawTile(ch, x, y) {
    let img;
    if (ch === "~") img = tileCache["~" + ((clock * 1.5) | 0) % 2];
    else if (ch === "_") img = tileCache[map.floor];
    else img = tileCache[ch];
    g.drawImage(img, x, y);
  }
  function render() {
    g.fillStyle = "#000"; g.fillRect(0, 0, 256, 224);
    if (battle) return drawBattle();
    const mx = map.w * T, my = map.h * T, [dx, dy] = DIRS[hero.dir], off = hero.moving ? hero.p * T : 0;
    const hx = hero.x * T + dx * off, hy = hero.y * T + dy * off;
    const cam = (p, m, v) => (m <= v ? -Math.floor((v - m) / 2) : Math.max(0, Math.min(m - v, Math.round(p + 8 - v / 2))));
    const cx = cam(hx, mx, 256), cy = cam(hy, my, 224);
    for (let ty = Math.floor(cy / T); ty <= Math.floor((cy + 223) / T); ty++) for (let tx = Math.floor(cx / T); tx <= Math.floor((cx + 255) / T); tx++) {
      if (tx < 0 || ty < 0 || tx >= map.w || ty >= map.h) continue;
      drawTile(map.tiles[ty][tx], tx * T - cx, ty * T - cy);
    }
    const ents = map.npcs.map(n => ({ y: n.y * T, n })).concat([{ y: hy, hero: true }]).sort((a, b) => a.y - b.y);
    for (const e of ents) {
      if (e.hero) {
        const f = hero.moving ? (hero.p < .5 ? hero.frame : hero.frame ^ 1) : hero.frame;
        g.drawImage(charSprite(HERO, hero.dir, f), Math.round(hx - cx), Math.round(hy - cy) - (hero.moving && hero.p > .25 && hero.p < .75 ? 1 : 0));
      } else if (e.n.type === "sign") g.drawImage(sign, e.n.x * T - cx, e.n.y * T - cy);
      else g.drawImage(charSprite(e.n.pal, e.n.dir, ((clock * 1.8 + e.n.x) | 0) % 2), e.n.x * T - cx, e.n.y * T - cy);
    }
    if (trans) {
      const h = trans.d / 2;
      g.fillStyle = `rgba(0,0,0,${trans.t < h ? trans.t / h : 1 - (trans.t - h) / h})`;
      g.fillRect(0, 0, 256, 224);
    }
  }
  function drawBattle() {
    const b = battle;
    g.fillStyle = "#101030"; g.fillRect(0, 0, 256, 224);
    g.strokeStyle = "#fff"; g.lineWidth = 2; g.strokeRect(24, 16, 208, 112);
    const sx = b.shake ? Math.round(Math.sin(clock * 60) * 4) : 0;
    g.drawImage(b.img, 96 + sx, 24, 64, 64);
    if (b.flash && ((clock * 20) | 0) % 2) { g.fillStyle = "rgba(255,40,40,.35)"; g.fillRect(0, 0, 256, 224); }
    if (trans) { g.fillStyle = `rgba(0,0,0,${trans.t < trans.d / 2 ? trans.t / (trans.d / 2) : 1 - (trans.t - trans.d / 2) / (trans.d / 2)})`; g.fillRect(0, 0, 256, 224); }
  }
  function loop(ts) {
    if (!active) return;
    const dt = Math.min(.05, (ts - last) / 1000 || 0);
    last = ts;
    update(dt); render();
    raf = requestAnimationFrame(loop);
  }

  return {
    start() {
      active = true; last = performance.now();
      document.activeElement && document.activeElement.blur && document.activeElement.blur();
      cvs.focus({ preventScroll: true });
      $("#rpgLoc").textContent = "📍 " + map.name;
      setMood(battle ? "rpgBattle" : map.bgm);
      cancelAnimationFrame(raf); raf = requestAnimationFrame(loop);
      if (!intro) {
        intro = true;
        say(["ようこそ、Promptの せかいへ！", "Aボタン（Z / Enter）で コマンドが ひらくぞ。", "4つの しろと まちを めぐって、Promptを あつめよう！"]);
      }
    },
    stop() { active = false; held.length = 0; cancelAnimationFrame(raf); }
  };
}
