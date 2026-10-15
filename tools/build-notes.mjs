// リポジトリ内の Prompt (md) を読み込み、サイト用データ (docs/data, docs/js/files.js) を生成します。
// 使い方: node tools/build-notes.mjs
import { readdirSync, readFileSync, writeFileSync, mkdirSync, rmSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKIP_TOP = new Set(["docs", "tools", "node_modules"]);
const SKIP_SUB = new Set(["sample", "output", "package", "font", "images", "data", "Archive"]);

const walk = (dir, rel = "") => {
  let out = [];
  for (const name of readdirSync(dir)) {
    if (name.startsWith(".")) continue;
    const full = join(dir, name), r = rel ? rel + "/" + name : name;
    if (statSync(full).isDirectory()) {
      if (!rel && SKIP_TOP.has(name)) continue;
      if (rel && (SKIP_SUB.has(name) || name.endsWith("-Data"))) continue;
      out = out.concat(walk(full, r));
    } else if (name.endsWith(".md") && rel) out.push(r);
  }
  return out;
};

const byDir = {};
for (const p of walk(root).sort((a, b) => a.localeCompare(b, "ja"))) {
  const i = p.indexOf("/");
  (byDir[p.slice(0, i)] ||= []).push(p.slice(i + 1));
}

const plain = s => s
  .replace(/```[a-z]*\n?/gi, " ")
  .replace(/[#>*`|_~\-]+/g, " ")
  .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
  .replace(/\s+/g, " ")
  .trim();

const dataDir = join(root, "docs", "data");
rmSync(dataDir, { recursive: true, force: true });
mkdirSync(join(dataDir, "notes"), { recursive: true });

const index = { dirs: {}, items: [] };
Object.keys(byDir).forEach((dir, n) => {
  const notes = {};
  for (const p of byDir[dir]) {
    const text = readFileSync(join(root, dir, p), "utf8").replace(/^\uFEFF/, "");
    notes[p] = text;
    const title = (text.match(/^#\s+(.+)$/m) || [, ""])[1].trim();
    index.items.push({ d: dir, p, t: title, x: plain(text).slice(0, 2500) });
  }
  index.dirs[dir] = `notes/${n}.json`;
  writeFileSync(join(dataDir, `notes/${n}.json`), JSON.stringify(notes));
});
writeFileSync(join(dataDir, "index.json"), JSON.stringify(index));
writeFileSync(join(root, "docs", "js", "files.js"), "export const FILES = " + JSON.stringify(byDir, null, 2) + ";\n");
console.log(`${index.items.length} notes / ${Object.keys(byDir).length} folders`);
