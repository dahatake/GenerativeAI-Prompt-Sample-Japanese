# 体系的 Vibe Coding シラバス（分散アプリケーション開発者向け）

小さなアプリを **ローカル → UI 連携 → DB 永続化 → テスト/CI → クラウド → 機能追加 → 複数 Coding Agent 並列開発** へと段階的に育てながら、Vibe Coding を体系的に身につけるコースです。

## 1. 対象と到達目標

| 項目 | 内容 |
|---|---|
| 対象 | 大企業で分散アプリを設計・開発している Software Engineer（Vibe Coding 初心者） |
| 前提 | Git / REST API / コンテナの基礎知識。Node.js か Python のいずれかの実務経験 |
| 総時間 | 約 20〜24 時間（1 回 2〜3 時間 × 8〜10 回。各章は単独でも実施可） |
| 題材 | **TaskBoard**: 小規模チーム向けタスク管理（画面 + REST API + DB） |

修了時にできること:

1. 意図（Intent）を仕様・受け入れ基準に落とし、Agent に安全に実装させられる
2. 小さなアプリを、構成を壊さず UI・DB・クラウドへ段階的に成長させられる
3. テスト・CI・レビューで「Vibe の品質」を担保できる
4. 機能追加を Spec 駆動で繰り返せる
5. 複数の Coding Agent を、衝突させずに並列で動かせる

## 2. Vibe Coding の定義と本コースの立ち位置

- **Vibe Coding**: 自然言語で意図を伝え、Agent が生成したコードを「動かして確かめながら」育てる開発スタイル。
- **本コースの方針（重要）**: 「雰囲気で丸投げ」ではなく **仕様 → 小さな単位で依頼 → 実行/テストで検証 → コミット** のループを徹底する。大企業の品質・セキュリティ要件に耐える **Disciplined Vibe Coding** を目指す。

## 3. 使用ツール（いずれか 1 つ以上。章ごとに差し替え可能）

| 役割 | 例 |
|---|---|
| IDE 内 Agent | GitHub Copilot（Agent mode）, Cursor など |
| CLI Agent | GitHub Copilot CLI, Claude Code, Codex CLI など |
| クラウド Agent | GitHub Copilot coding agent（Issue 割り当て → PR 作成） |
| 実行環境 | Node.js LTS, Docker Desktop, Git, GitHub CLI (`gh`) |
| クラウド | Azure（Container Apps / Static Web Apps / PostgreSQL Flexible Server）。AWS 等でも読み替え可 |

> ツールの UI・コマンドは頻繁に変わります。本書は「考え方 + 汎用プロンプト」を中心とし、コマンドは実施時に公式ドキュメントで確認してください。

## 4. カリキュラム全体像

| 章 | タイトル | アプリの成長 | 主な学習内容 | 時間 |
|---|---|---|---|---|
| [00](./00-foundations.md) | 基礎: 原則・環境・Agent への指示設計 | （準備） | Vibe Coding ループ、AGENTS.md、Spec、プロンプト型 | 2h |
| [01](./01-local-api.md) | ローカル API（メモリ保存） | CRUD API が動く | 仕様→実装→検証、最小の縦切り | 2h |
| [02](./02-ui.md) | 画面の追加 | 画面 ⇄ API 連携 | UI 生成、契約（OpenAPI）駆動、ブラウザ検証 | 2.5h |
| [03](./03-database.md) | データ永続化 | SQLite → PostgreSQL (Docker Compose) | リポジトリ抽象、マイグレーション、環境差分 | 2.5h |
| [04](./04-quality-ci.md) | 品質ゲート | テスト + CI + セキュリティ | テスト生成の作法、Agent 出力のレビュー、CI | 2.5h |
| [05](./05-cloud.md) | クラウド展開 | Azure 上で画面/API/DB が連携 | コンテナ化、IaC、Managed Identity、可観測性 | 3h |
| [06](./06-feature-addition.md) | 機能追加 | 認証・コメント・通知など | Spec 駆動の変更、リグレッション防止 | 2.5h |
| [07](./07-multi-agent.md) | 複数 Agent 並列開発 | 並列で機能を同時追加 | worktree 分離、役割分担、統合、衝突解消 | 3h |
| [08](./08-governance-appendix.md) | ガバナンスと付録 | （運用） | 企業利用の注意、チェックリスト、プロンプト集 | 1.5h |

## 5. アーキテクチャの成長（段階図）

```text
Stage1  [curl/REST Client] -> [API(Node, in-memory)]
Stage2  [Browser UI(React)] -> [API(in-memory)]
Stage3  [Browser UI]        -> [API] -> [SQLite -> PostgreSQL(Docker)]
Stage4  同上 + テスト + GitHub Actions
Stage5  [Static Web Apps] -> [Container Apps(API)] -> [Azure DB for PostgreSQL]
                                   |-> Key Vault / Managed Identity / App Insights
Stage6  + 認証(Entra ID) + コメント + 通知(非同期: Service Bus など)
Stage7  上記機能を複数 Agent が worktree/ブランチごとに並列実装
```

## 6. 技術スタック（既定。置換可）

- Backend: Node.js + TypeScript + Fastify + Zod、テストは Vitest
- Frontend: React + Vite + TypeScript
- DB: SQLite（開発初期）→ PostgreSQL
- 契約: OpenAPI（`docs/openapi.yaml`）を単一の真実とする
- Python 派の読み替え: FastAPI + Pydantic + pytest + SQLAlchemy/Alembic（プロンプト中の技術名を差し替えるだけ）

## 7. 評価（修了条件）

各章末の「完了チェック」をすべて満たし、最終成果物として以下を確認:

- [ ] クラウド上で画面から API 経由で DB に読み書きできる
- [ ] CI が緑（lint / test / build / 依存脆弱性スキャン）
- [ ] `AGENTS.md`・`docs/spec/*`・`docs/openapi.yaml` が最新
- [ ] 2 つ以上の機能を複数 Agent で並列実装し、PR 経由で統合した

## 8. リポジトリ構成（完成形）

```text
taskboard/
├─ AGENTS.md                # Agent への恒久ルール
├─ docs/
│  ├─ spec/                 # 機能ごとの仕様 (S-001-*.md)
│  ├─ openapi.yaml
│  ├─ adr/                  # 設計判断記録
│  └─ prompts/              # 再利用プロンプト
├─ apps/
│  ├─ api/                  # Fastify API
│  └─ web/                  # React UI
├─ infra/                   # Bicep など IaC
├─ docker-compose.yml
└─ .github/workflows/
```

## 9. 進め方のコツ（全章共通）

1. **1 回の依頼は 1 つの検証可能な成果**にする（目安: 差分 300 行以内）
2. 依頼前に **Git を clean な状態**にする。気に入らなければ `git restore` / `git reset`
3. 生成後は **実行して確かめる**（テスト・curl・ブラウザ）。読むだけで信用しない
4. 通ったらすぐ **コミット**（Agent の暴走からの復帰点）
5. Agent が間違えたら、修正指示よりも **仕様・AGENTS.md の不足を直す**

---

## 動作確認済み環境と検証結果

教材のフローを実際に実行して検証した(Windows 11、Node 24、npm 11、Docker 29、Azure CLI 2.90、PowerShell 7.6)。

| 検証範囲 | 結果 |
|---|---|
| 第1章 API(Fastify + Zod + Vitest) | 成功 |
| 第2章 UI(React/Vite、単体・E2E) | 成功 |
| 第3章 メモリ / SQLite / PostgreSQL | 成功(永続化も確認) |
| 第4章 CI の各ステップ(ローカル再現) | 成功。GitHub Actions 上は未実行 |
| 第5章 Azure(ACA + PostgreSQL + SWA、az CLI でデプロイ) | 成功(クラウド E2E 確認) |
| 第6章 機能追加(v2 をクラウドへ) | 成功 |
| 第7章 2 エージェント並行(worktree) | 成功(マージ衝突と意味的衝突を解消) |

**未検証**: `azd up`(azd の認証で失敗したため az CLI で代替)、GitHub Actions の OIDC デプロイ、Entra 認証、Service Bus、Key Vault + Private Endpoint、S-005/S-006 に対応する UI 変更。各章末の「動作確認で判明した注意点」を参照。
