import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const categories = ["営業", "管理職", "人事", "日々のタスク", "会議", "音声入力", "Agent", "DALL-E", "Workshop", "sample"];
const env = { ...process.env, GITHUB_STEP_SUMMARY: "" };

function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), "pages-sync-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  for (const file of ["tools/build-notes.mjs", "tools/audit-structure.mjs", "docs/js/catalog.js", "docs/js/rpg.js", "docs/js/audio.js", "docs/index.html"]) {
    const target = join(dir, file);
    mkdirSync(dirname(target), { recursive: true });
    cpSync(join(root, file), target);
  }
  for (const category of categories) {
    mkdirSync(join(dir, category), { recursive: true });
    writeFileSync(join(dir, category, "README.md"), `# ${category}\n\nOriginal content\n`);
  }
  return dir;
}

function build(dir) {
  execFileSync(process.execPath, [join(dir, "tools", "build-notes.mjs")], { env });
  const index = JSON.parse(readFileSync(join(dir, "docs", "data", "index.json"), "utf8"));
  for (const item of index.items) {
    const notes = JSON.parse(readFileSync(join(dir, "docs", "data", index.dirs[item.d]), "utf8"));
    const source = readFileSync(join(dir, item.d, item.p), "utf8").replace(/^\uFEFF/, "");
    assert.equal(notes[item.p], source);
  }
  const files = readFileSync(join(dir, "docs", "js", "files.js"), "utf8");
  assert.deepEqual(JSON.parse(files.slice("export const FILES = ".length).trim().replace(/;$/, "")),
    Object.fromEntries(Object.keys(index.dirs).map(d => [d, index.items.filter(i => i.d === d).map(i => i.p)])));
  return index;
}

function audit(dir) {
  return spawnSync(process.execPath, [join(dir, "tools", "audit-structure.mjs")], { env, encoding: "utf8" });
}

test("Markdown edits, additions, renames and deletions update the published data", t => {
  const dir = fixture(t);
  const initial = build(dir);
  assert.equal(initial.items.length, categories.length);
  const folder = join(dir, "日々のタスク");
  const updated = "# Updated title\n\n```text\nNew prompt <tag> & 日本語\n```\n";
  writeFileSync(join(folder, "README.md"), updated);
  mkdirSync(join(folder, "nested"));
  writeFileSync(join(folder, "nested", "added.md"), "# Added\n\nSearchable addition\n");
  const changed = build(dir);
  assert.equal(changed.items.length, initial.items.length + 1);
  assert.equal(changed.items.find(i => i.d === "日々のタスク" && i.p === "README.md").t, "Updated title");
  assert.match(changed.items.find(i => i.p === "nested/added.md").x, /Searchable addition/);
  renameSync(join(folder, "nested", "added.md"), join(folder, "nested", "renamed.md"));
  const renamed = build(dir);
  assert.ok(renamed.items.some(i => i.p === "nested/renamed.md"));
  assert.ok(!renamed.items.some(i => i.p === "nested/added.md"));
  rmSync(join(folder, "nested", "renamed.md"));
  const deleted = build(dir);
  assert.equal(deleted.items.length, initial.items.length);
  assert.ok(!deleted.items.some(i => i.p === "nested/renamed.md"));
  assert.equal(audit(dir).status, 0);
});

test("empty or removed categories disappear from all catalog views and can return", t => {
  const dir = fixture(t);
  build(dir);
  assert.equal(audit(dir).status, 0);
  rmSync(join(dir, "管理職", "README.md"));
  rmSync(join(dir, "日々のタスク"), { recursive: true });
  const removed = build(dir);
  assert.equal(removed.dirs["管理職"], undefined);
  assert.equal(removed.dirs["日々のタスク"], undefined);
  assert.equal(readdirSync(join(dir, "docs", "data", "notes")).length, categories.length - 2);
  assert.ok(!existsSync(join(dir, "docs", "data", "notes", `${categories.length - 1}.json`)));
  assert.equal(audit(dir).status, 0);
  mkdirSync(join(dir, "日々のタスク"));
  writeFileSync(join(dir, "日々のタスク", "README.md"), "# Returned\n");
  assert.ok(build(dir).dirs["日々のタスク"]);
  assert.equal(audit(dir).status, 0);
});

test("unknown categories still fail the deployment audit", t => {
  const dir = fixture(t);
  mkdirSync(join(dir, "unregistered"));
  writeFileSync(join(dir, "unregistered", "README.md"), "# Unknown\n");
  assert.ok(build(dir).dirs.unregistered);
  const result = audit(dir);
  assert.equal(result.status, 1);
  assert.match(result.stdout, /unregistered/);
});

test("unknown group entries still fail the deployment audit", t => {
  const dir = fixture(t);
  const catalog = join(dir, "docs", "js", "catalog.js");
  writeFileSync(catalog, readFileSync(catalog, "utf8").replace('dirs: ["Software Engineer"', 'dirs: ["unregistered", "Software Engineer"'));
  build(dir);
  const result = audit(dir);
  assert.equal(result.status, 1);
  assert.match(result.stdout, /unregistered/);
});

test("sample assets and root documentation stay excluded, but shared samples remain included", t => {
  const dir = fixture(t);
  writeFileSync(join(dir, "README.md"), "# Repository guide\n");
  for (const sub of ["sample", "output", "package", "font", "images", "data", "Archive", "fixture-Data", ".hidden"]) {
    mkdirSync(join(dir, "Agent", sub));
    writeFileSync(join(dir, "Agent", sub, "excluded.md"), "# Excluded\n");
  }
  writeFileSync(join(dir, "Agent", ".hidden.md"), "# Hidden\n");
  const index = build(dir);
  assert.equal(index.items.length, categories.length);
  assert.ok(index.items.some(i => i.d === "sample"));
  assert.equal(audit(dir).status, 0);
});
