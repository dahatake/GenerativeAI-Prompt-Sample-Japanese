// GitHub Pages の「分類・階層構造」を情報デザインの原則に基づいて監査します。
// 使い方: node tools/audit-structure.mjs （tools/build-notes.mjs の実行後に実行）
// 違反(ERROR)が1件でもあれば終了コード1で失敗し、デプロイを止めます。警告(WARN)は要約に表示します。
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const docs = join(root, "docs");
const { CATALOG, GROUPS } = await import(pathToFileURL(join(docs, "js", "catalog.js")).href);
const { FILES } = await import(pathToFileURL(join(docs, "js", "files.js")).href);
const index = JSON.parse(readFileSync(join(docs, "data", "index.json"), "utf8"));

const LIMITS = {
  groups: [3, 7],          // 第1階層の数：ミラーの法則（7±2）
  catsPerGroup: [2, 9],    // グループ内のカテゴリ数：一覧性と偏りの抑制
  maxDepth: 5,             // グループ > カテゴリ > フォルダー > サブフォルダー > Prompt まで（UIでは相対パスを1つの見出しにまとめ、体感4段）
  groupName: 14, catName: 24, desc: 90, hint: 24,
  flatFiles: 40            // 1カテゴリ直下のファイルが多すぎる場合は警告
};
const SLOTS = { castle: 12, town: 8 }; // RPGモードの建物ごとの収容人数（案内人1人を除く）

const results = [];
const check = (level, principle, ok, msg) => { if (!ok) results.push({ level, principle, msg }); };
const err = (p, ok, m) => check("ERROR", p, ok, m);
const warn = (p, ok, m) => check("WARN", p, ok, m);
const [gMin, gMax] = LIMITS.groups, [cMin, cMax] = LIMITS.catsPerGroup;

// 1. 網羅性 (Completeness)：リポジトリの全コンテンツがどこかのカテゴリに属する
const repoDirs = Object.keys(FILES);
const catDirs = CATALOG.map(c => c.dir);
for (const d of repoDirs) err("網羅性", catDirs.includes(d), `フォルダー「${d}」がカテゴリに未登録です（catalog.js の META と GROUPS に追加してください）`);
for (const d of catDirs) err("網羅性", repoDirs.includes(d), `カテゴリ「${d}」に対応するフォルダー/Promptが見つかりません`);
err("網羅性", new Set(catDirs).size === catDirs.length, "カテゴリ名が重複しています");

// 2. MECE：各カテゴリはちょうど1つのグループに属する
const owner = new Map();
for (const g of GROUPS) for (const d of g.dirs) owner.set(d, [...(owner.get(d) || []), g.id]);
for (const d of catDirs) {
  const o = owner.get(d) || [];
  err("MECE", o.length === 1, o.length === 0 ? `カテゴリ「${d}」がどのグループにも属していません` : `カテゴリ「${d}」が複数グループ(${o.join(",")})に重複しています`);
}
for (const d of owner.keys()) err("MECE", catDirs.includes(d), `GROUPS に存在しないカテゴリ「${d}」があります`);

// 3. 階層の幅 (Chunking)：グループ数とグループ内の数を認知負荷の範囲に収める
err("チャンク化", GROUPS.length >= gMin && GROUPS.length <= gMax, `グループ数が${GROUPS.length}です（${gMin}〜${gMax}に収めてください）`);
for (const g of GROUPS) {
  const n = g.dirs.length;
  err("チャンク化", n >= cMin && n <= cMax, `グループ「${g.name}」のカテゴリ数が${n}です（${cMin}〜${cMax}に収めてください）`);
}

// 4. 階層の深さ：深すぎる階層は探しにくい
let maxDepth = 0;
for (const c of CATALOG) for (const f of c.files) maxDepth = Math.max(maxDepth, 2 + f.path.split("/").length);
err("階層の深さ", maxDepth <= LIMITS.maxDepth, `階層が${maxDepth}段あります（最大${LIMITS.maxDepth}段）`);

// 5. ラベリング：識別しやすく、短く、一貫している
const ids = GROUPS.map(g => g.id);
err("ラベリング", new Set(ids).size === ids.length, "グループIDが重複しています");
err("ラベリング", new Set(GROUPS.map(g => g.name)).size === GROUPS.length, "グループ名が重複しています");
for (const g of GROUPS) {
  err("ラベリング", !!(g.icon && g.name && g.hint), `グループ「${g.id}」に icon / name / hint が必要です`);
  warn("ラベリング", (g.name || "").length <= LIMITS.groupName, `グループ名「${g.name}」が${LIMITS.groupName}文字を超えています`);
  warn("ラベリング", (g.hint || "").length <= LIMITS.hint, `グループの説明「${g.hint}」が${LIMITS.hint}文字を超えています`);
}
for (const c of CATALOG) {
  err("ラベリング", !!(c.icon && c.color && c.desc), `カテゴリ「${c.dir}」に icon / color / desc が必要です`);
  warn("ラベリング", c.dir.length <= LIMITS.catName, `カテゴリ名「${c.dir}」が${LIMITS.catName}文字を超えています`);
  warn("ラベリング", (c.desc || "").length <= LIMITS.desc, `カテゴリ「${c.dir}」の説明が${LIMITS.desc}文字を超えています`);
  err("ラベリング", c.kind !== "persona" || (c.role && c.role.length > 0), `職種カテゴリ「${c.dir}」に role が必要です`);
}

// 6. 一貫性：職種(persona)は「職種から探す」グループ、それ以外は他グループ
const roleGroup = GROUPS.find(g => g.id === "role");
err("一貫性", !!roleGroup, "「職種から探す」グループ(id: role)が必要です");
for (const c of CATALOG) {
  if (!roleGroup) break;
  err("一貫性", (c.kind === "persona") === (c.group === "role"), `カテゴリ「${c.dir}」の種別(${c.kind})とグループ(${c.group})が矛盾しています`);
}

// 7. バランス：偏りの大きい構造は探索を難しくする
const sizes = GROUPS.map(g => CATALOG.filter(c => c.group === g.id).reduce((s, c) => s + c.count, 0));
const total = sizes.reduce((a, b) => a + b, 0);
GROUPS.forEach((g, i) => warn("バランス", total === 0 || sizes[i] / total <= .6, `グループ「${g.name}」にPromptの${Math.round(sizes[i] / total * 100)}%が集中しています`));
for (const c of CATALOG) {
  const flat = c.files.filter(f => !f.group).length;
  warn("バランス", flat <= LIMITS.flatFiles, `カテゴリ「${c.dir}」の直下に${flat}件あります。サブフォルダーで分けてください`);
}

// 8. 到達性：どのPromptも検索・一覧・RPGのいずれの導線にも載っている
const itemKeys = new Set(index.items.map(i => `${i.d}/${i.p}`));
const fileKeys = CATALOG.flatMap(c => c.files.map(f => `${c.dir}/${f.path}`));
err("到達性", fileKeys.length === itemKeys.size && fileKeys.every(k => itemKeys.has(k)), `カタログ(${fileKeys.length}件)と検索インデックス(${itemKeys.size}件)が一致しません`);
for (const i of index.items) warn("到達性", !!i.t, `「${i.d}/${i.p}」に見出し(# タイトル)がありません`);
for (const c of CATALOG) err("到達性", c.count > 0 && !!c.startPath, `カテゴリ「${c.dir}」にPromptがありません`);

// 9. 表現間の整合：2D一覧 / 3D / RPG が同じ構造を使う
const rpgCount = {};
for (const g of GROUPS) {
  err("表現間の整合", !!(g.rpg && g.rpg.place && SLOTS[g.rpg.kind] && g.rpg.king), `グループ「${g.name}」のRPG設定(rpg.place/kind/king)が不足しています`);
  const cap = SLOTS[g.rpg && g.rpg.kind] || 0;
  rpgCount[g.id] = g.dirs.length;
  err("表現間の整合", g.dirs.length <= cap, `グループ「${g.name}」のカテゴリ数(${g.dirs.length})がRPGの建物の収容人数(${cap})を超えています`);
}
const html = readFileSync(join(docs, "index.html"), "utf8");
for (const id of ["catalogRoot", "viewRpg", "rpgCanvas", "mrpg", "m2d", "m3d"]) err("表現間の整合", html.includes(`id="${id}"`), `index.html に #${id} がありません`);
for (const f of ["js/rpg.js", "js/audio.js"]) err("表現間の整合", existsSync(join(docs, f)), `docs/${f} がありません`);

// ---- レポート ----
const errors = results.filter(r => r.level === "ERROR"), warns = results.filter(r => r.level === "WARN");
const lines = [];
lines.push("## 🧭 GitHub Pages 構造監査（情報デザイン）", "");
lines.push(`- 第1階層：**${GROUPS.length}グループ** ／ 第2階層：**${CATALOG.length}カテゴリ** ／ 第3階層以降：**${total}Prompt**（最大${maxDepth}段）`);
lines.push(`- 結果：${errors.length ? "❌" : "✅"} ERROR ${errors.length}件 ／ ⚠️ WARN ${warns.length}件`, "");
lines.push("| グループ | カテゴリ数 | Prompt数 | RPGの場所 |", "|---|---:|---:|---|");
GROUPS.forEach((g, i) => lines.push(`| ${g.icon} ${g.name} | ${g.dirs.length} | ${sizes[i]} | ${g.rpg ? g.rpg.place : "-"} |`));
if (results.length) {
  lines.push("", "| 区分 | 原則 | 内容 |", "|---|---|---|");
  results.forEach(r => lines.push(`| ${r.level === "ERROR" ? "❌ ERROR" : "⚠️ WARN"} | ${r.principle} | ${r.msg} |`));
}
const report = lines.join("\n");
console.log(report);
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, report + "\n");
for (const r of results) console.log(`::${r.level === "ERROR" ? "error" : "warning"} title=構造監査(${r.principle})::${r.msg}`);
process.exit(errors.length ? 1 : 0);
