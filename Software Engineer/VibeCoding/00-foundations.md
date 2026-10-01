# 第 0 章 基礎: 原則・環境・Agent への指示設計

**ゴール**: 以降の章で使う「開発ループ」「恒久ルール (AGENTS.md)」「仕様テンプレ」「プロンプトの型」を準備する。

## 0.1 講義: Vibe Coding の開発ループ

```text
 Intent(やりたいこと)
   └▶ Spec(仕様+受入基準) ─▶ Plan(Agent に計画させる) ─▶ Implement(小さく実装)
        ▲                                                        │
        └──── Learn(仕様/AGENTS.md を更新) ◀── Verify(実行・テスト・レビュー) ◀┘
                                                   │ OK なら Commit
```

| 原則 | 説明 |
|---|---|
| 小さく縦に切る | 画面〜DB を貫く最小機能を 1 つずつ。横断的な大改修を一括で頼まない |
| 検証可能性 | 「動いた」の定義（テスト/コマンド/画面）を先に決める |
| 計画してから実装 | まず Plan（変更ファイル・手順・リスク）を出させ、承認してから実装させる |
| コンテキスト管理 | 長い会話は劣化する。区切りごとに新規セッション + AGENTS.md/Spec で再開 |
| 責任は人間 | 生成コードは自分が書いたものとしてレビュー・説明できること |

## 0.2 ハンズオン A: 環境準備（30 分）

1. ツール確認: `git --version`, `node --version`（LTS）, `docker --version`, `gh --version`
2. Agent を 1 つ選び、IDE/CLI で動作確認（「このフォルダの内容を説明して」）
3. リポジトリ作成:

```powershell
mkdir taskboard; cd taskboard
git init -b main
gh repo create taskboard --private --source . --remote origin   # 任意
```

4. `.gitignore`（`node_modules`, `.env`, `*.sqlite`, `dist`）を作成し初回コミット。

> **社内ルール確認**: 利用可能な Agent/モデル、コード・データの送信可否、OSS ライセンス方針を先に確認（第 8 章参照）。

## 0.3 ハンズオン B: AGENTS.md を書く（30 分）

Agent に毎回読ませる**恒久ルール**。短く具体的に。ルート直下に置く（ツールによっては `CLAUDE.md` / `.github/copilot-instructions.md` に同内容を置く）。

```markdown
# AGENTS.md
## プロジェクト
TaskBoard: チーム向けタスク管理。apps/api (Fastify+TS), apps/web (React+Vite+TS)。
## コマンド
- 依存導入: `npm install`
- テスト: `npm test` / Lint: `npm run lint` / 型: `npm run typecheck`
## ルール
- 変更前に docs/spec/ の該当仕様を読む。仕様にない機能は追加しない。
- API 変更は必ず docs/openapi.yaml を同時に更新する。
- 入力検証は Zod。DB アクセスは repository 層のみ。
- シークレットをコードに書かない。設定は環境変数(.env.example に項目のみ記載)。
- 新規ロジックにはテストを付ける。テストが通るまで完了としない。
- 1 回の変更は小さく。無関係なリファクタ禁止。
## 完了の定義
lint / typecheck / test が全て成功し、変更点と実行結果を要約する。
```

## 0.4 ハンズオン C: Spec テンプレートと Plan-first（30 分）

`docs/spec/_template.md`:

```markdown
# S-XXX タイトル
## 背景 / 目的
## ユーザーストーリー
## 受け入れ基準 (Given/When/Then, 箇条書きでテスト可能に)
## API / データ変更
## 非機能 (性能・セキュリティ・監査)
## スコープ外
## 未決事項
```

**Plan-first プロンプト（雛形）**

```text
docs/spec/S-001-*.md を読み、実装計画だけを出力してください（コードはまだ書かない）。
- 変更/追加するファイル一覧
- 手順（小さなコミット単位）
- テスト方針
- リスクと不明点（質問があれば先に列挙）
```

## 0.5 プロンプトの型（6 要素）

| 要素 | 例 |
|---|---|
| 目的 | 「タスクの一覧取得 API を追加」 |
| 文脈 | 参照すべきファイル/仕様（`@docs/spec/S-001.md`） |
| 制約 | 技術・禁止事項・スタイル |
| 受入基準 | 「`GET /tasks` が 200 と配列を返す。テスト通過」 |
| 出力形式 | 変更点の要約、実行したコマンド |
| 進め方 | 計画→承認→実装→検証 |

**悪い例**: 「タスク管理アプリ作って」
**良い例**: 「S-001 に従い、`apps/api` に `POST /tasks` を実装。Zod で title(1〜100字)必須。Vitest で正常/異常系テスト。完了後 `npm test` の結果を報告」

## 0.6 演習

1. 悪い例と良い例を同じ Agent に投げ、生成物・手戻り回数を比較し記録する
2. AGENTS.md に「Agent が一度間違えたルール」を 1 つ追加する

## 0.7 完了チェック

- [ ] Agent が動作し、リポジトリが Git 管理されている
- [ ] `AGENTS.md` と `docs/spec/_template.md` をコミットした
- [ ] Plan-first で依頼する流れを説明できる
