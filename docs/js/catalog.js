import { FILES } from "./files.js";

const BLOB = "https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese/blob/main/";
const TREE = "https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese/tree/main/";
const enc = p => p.split("/").map(encodeURIComponent).join("/");

// kind: persona = フォルダー名が職種・役割 / topic = テーマ・シナリオ
const META = [
  { dir: "Software Engineer", kind: "persona", role: "ソフトウェアエンジニア / IT担当者", icon: "👩‍💻", color: "#3fb950", desc: "要件定義・設計レビュー・技術調査・Vibe Coding・保守・IT Pro向けまで、開発ライフサイクル全体のPrompt。", start: "README.md" },
  { dir: "営業", kind: "persona", role: "営業担当", icon: "🤝", color: "#ff8c00", desc: "顧客の課題と自社の商品・サービスをマッチングして提案につなげるPrompt。" },
  { dir: "管理職", kind: "persona", role: "マネージャー / 管理職", icon: "🧭", color: "#7f85f5", desc: "お客様との面談前の情報収集など、マネジメント業務の準備を助けるPrompt。" },
  { dir: "人事", kind: "persona", role: "人事担当", icon: "🧑‍🤝‍🧑", color: "#ff4fa3", desc: "エントリーシート、新入社員の紹介、社員への待遇調査などのPrompt。" },
  { dir: "教育", kind: "persona", role: "教師・講師・学習者", icon: "🎓", color: "#00b7c3", desc: "問題作成・小テスト・個別学習・翻訳・英文採点・各種チュートリアルまで学びのPrompt。", start: "README.md" },
  { dir: "行政", kind: "persona", role: "行政職員", icon: "🏛️", color: "#8e4ec6", desc: "行政施策の評価など、公共分野での活用Prompt。", start: "README.md" },
  { dir: "データ分析", kind: "persona", role: "データアナリスト", icon: "📊", color: "#58a6ff", desc: "アンケート分析・データのマージ・分類モデル作成・データソース洗い出しのPrompt。", start: "README.md" },
  { dir: "Security", kind: "persona", role: "セキュリティ担当", icon: "🛡️", color: "#e5484d", desc: "Prompt Injection / Leaking などAI固有のリスクとその緩和策。" },
  { dir: "日々のタスク", kind: "topic", icon: "✅", color: "#3fb950", desc: "タスクの振り返り・漏れチェック・次にやることの洗い出し・メール分析。", start: "README.md" },
  { dir: "会議", kind: "topic", icon: "🗣️", color: "#7f85f5", desc: "議事録作成、ディスカッション、顧客ヒアリング中の情報整理。" },
  { dir: "ビジネス戦略や分析", kind: "topic", icon: "📈", color: "#ffb900", desc: "新規事業アイディア、AI投資判断、業務分析と改善策、報道状況の調査。" },
  { dir: "Agent", kind: "topic", icon: "🤖", color: "#ff8c00", desc: "戦略コンサルタントなど、特定の役割を持つAgentの作成Prompt。", start: "README.md" },
  { dir: "文書・画像作成", kind: "topic", icon: "🖼️", color: "#ff4fa3", desc: "レシピと画像の作成など、文書と画像を一緒に作るPrompt。" },
  { dir: "DALL-E", kind: "topic", icon: "🎨", color: "#ff4fa3", desc: "DALL-E 3 向けの画像生成Promptの作り方。", start: "README.md" },
  { dir: "Code Interpreter", kind: "topic", icon: "🐍", color: "#58a6ff", desc: "QRコード・アニメーションGIF・zip要約など、コードを実行して作る。", start: "README.md" },
  { dir: "数理最適化問題", kind: "topic", icon: "🧮", color: "#00b7c3", desc: "シフトスケジュール問題・巡回セールスマン問題を解く。", start: "README.md" },
  { dir: "音声入力", kind: "topic", icon: "🎙️", color: "#8e4ec6", desc: "音声入力した長文を整える活用例。", start: "README.md" },
  { dir: "便利なテクニック", kind: "topic", icon: "💡", color: "#ffb900", desc: "構造化カタログなど、Promptをよりよくするテクニック。", start: "README.md" },
  { dir: "Workshop", kind: "topic", icon: "🧑‍🏫", color: "#7f85f5", desc: "経営層向けなどワークショップ用のシナリオ。", start: "README.md" },
  { dir: "Workshop_English", kind: "topic", icon: "🌐", color: "#58a6ff", desc: "英語版のワークショップ。", start: "README.md" },
  { dir: "sample", kind: "topic", icon: "🧪", color: "#a4a8bd", desc: "各Promptで使える共通のサンプルデータと、その監査レポート。" }
];

const titleOf = p => p.split("/").pop().replace(/\.md$/, "").replace(/^\[[^\]]+\]\s*/, m => m.trim() + " ");

export const CATALOG = META.map(m => {
  const files = (FILES[m.dir] || []).map(p => ({
    path: p,
    title: p === "README.md" ? "はじめに（README）" : titleOf(p),
    group: p.includes("/") ? p.split("/").slice(0, -1).join("/") : "",
    url: BLOB + enc(m.dir + "/" + p)
  }));
  const readme = files.find(f => f.path === "README.md");
  return { ...m, files, count: files.length, url: TREE + enc(m.dir), startUrl: readme ? readme.url : (files[0] ? files[0].url : TREE + enc(m.dir)) };
});
