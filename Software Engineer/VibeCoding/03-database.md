# 第 3 章 データ永続化（SQLite → PostgreSQL）

**ゴール**: メモリ保存を DB に置き換える。repository 抽象のおかげで **API/UI を変えずに**保存先を差し替える体験をする。

## 3.1 講義: 既存コードを壊さずに変える

- 変更は **Strangler（段階置換）**: 新 `SqliteTaskRepository` を追加 → 既存テストを同じ契約で流す → 切替。
- **契約テスト**: `TaskRepository` の共通テストスイートを作り、InMemory / SQLite / PostgreSQL すべてに同じテストを適用する。
- **スキーマはコードで管理**（マイグレーション）。Agent に DB を直接いじらせない。

## 3.2 ハンズオン A: 仕様と ADR（20 分）

`docs/spec/S-003-persistence.md`

```markdown
# S-003 永続化
## 受け入れ基準
- アプリを再起動してもタスクが残る
- repository の契約テストが InMemory/SQLite/PostgreSQL で共通に通る
- スキーマ変更はマイグレーションファイルで管理し、空 DB から全適用できる
- 接続情報は環境変数 DATABASE_URL のみ。コードに直書きしない
## スコープ外
読み取りレプリカ、パーティショニング
```

`docs/adr/0001-db-choice.md`: Agent に「SQLite(開発) と PostgreSQL(本番) の 2 段階にする案のトレードオフを ADR 形式で書いて」と依頼。**人間が決定理由を編集**する（意思決定は人間）。

## 3.3 ハンズオン B: 契約テスト → SQLite（50 分）

```text
@docs/spec/S-003-persistence.md
1. 既存 InMemory 向けテストを、TaskRepository 共通の契約テスト(runRepositoryContract(factory))に
   リファクタ。挙動は変えない。
2. SqliteTaskRepository とマイグレーション(0001_create_tasks)を追加し、契約テストを通す。
3. 起動時に REPO=memory|sqlite で切替可能に。既定は sqlite。
各ステップごとに npm test を実行し、通ってから次へ。ステップごとにコミット用メッセージ案も出して。
```

確認: サーバ再起動後に `GET /tasks` で前回のデータが残ること。

## 3.4 ハンズオン C: PostgreSQL + Docker Compose（60 分）

```text
docker-compose.yml に postgres(永続ボリューム付き)を追加し、PostgresTaskRepository と
同一スキーマのマイグレーションを実装。契約テストを PostgreSQL にも適用(テスト用コンテナを使用)。
DATABASE_URL は .env.example に項目のみ記載し、.env は git 管理外。
SQL は必ずパラメータ化クエリを使うこと。
```

```powershell
docker compose up -d db
npm run migrate
npm test
```

### レビュー観点（人間が必ず見る）

- [ ] 文字列連結の SQL がない（SQL インジェクション）
- [ ] インデックス（status, createdAt）が必要十分
- [ ] タイムゾーン: `timestamptz` を使用し UTC で保存
- [ ] 接続プール設定とクローズ処理
- [ ] マイグレーションが冪等で、ロールバック方針がある

## 3.5 演習: フルスタック起動

`docker compose up` 一発で **db + api + web** が起動するよう整備させる。

```text
docker-compose.yml を拡張し、db / api / web を一括起動。api は db の healthcheck を待つ。
README に起動手順と動作確認手順を追記して。
```

## 3.6 つまずきポイント

| 症状 | 対処 |
|---|---|
| Agent が DB を直接手で書き換える提案 | 「スキーマ変更は必ずマイグレーション」を AGENTS.md に |
| SQLite と PostgreSQL の SQL 方言差 | 差異は repository 内に閉じ込め、契約テストで検出 |
| テストデータの汚染 | テストごとにトランザクション/テーブル初期化 |

## 3.7 完了チェック

- [ ] 再起動してもデータが残る（SQLite / PostgreSQL 両方）
- [ ] 契約テストが 3 実装で通る
- [ ] `docker compose up` で全体が動く
- [ ] ADR を 1 本、自分の言葉で確定した

---

## 動作確認で判明した注意点(実機検証済み)

- SQLite は `better-sqlite3` が Node 24 / Windows でネイティブビルドに失敗することがある。組み込みの `node:sqlite`(`DatabaseSync`)を使うとフラグ不要で動く。
- マイグレーションは「起動のたびに全 SQL を再実行」では `ALTER TABLE` などで壊れる。`schema_migrations` テーブルで適用済みファイルを記録し、トランザクション内で実行する(PostgreSQL は advisory lock で多重実行を防ぐ)。ファイル名は `20261001000000_create_tasks.sql` のようなタイムスタンプ形式にする。「冪等」とは「適用済みを記録してスキップする」ことを指す。
- PostgreSQL の id が不正な UUID だとキャストエラーになるため、正規表現で事前に弾いて 404 を返す。
- ローカルに既存の PostgreSQL が 5432 を使っている場合がある。`docker-compose.yml` は `ports: ["${DB_PORT:-5432}:5432"]` とし、`DB_PORT=5433` で上書きする。
- 契約テスト(メモリ / SQLite / PostgreSQL 共通)は PostgreSQL では `TRUNCATE` を使うため、並行実行する場合は DB を分ける。
