const BASE = "https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese";
const enc = p => p.split("/").map(encodeURIComponent).join("/");
export const urlFor = (dir, path) => (dir ? `${BASE}/${path ? "blob" : "tree"}/main/${enc(dir + (path ? "/" + path : ""))}` : BASE);

// 画面上部の GitHub リンクは、ここだけが github.com への唯一の出口です。
const ctx = { cat: null, lesson: null, note: null };
export function setCtx(key, val) {
  ctx[key] = val;
  const cur = ctx.note || ctx.lesson || ctx.cat;
  const a = document.getElementById("ghLink");
  if (!a) return;
  a.href = cur ? cur.url : BASE;
  document.getElementById("ghLabel").textContent = cur ? cur.label : "リポジトリ全体";
  a.title = cur ? `元の場所を GitHub で開く：${cur.label}` : "元のリポジトリを GitHub で開く";
}
