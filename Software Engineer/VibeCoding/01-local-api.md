# 第 1 章 ローカル API（メモリ保存）

**ゴール**: 最小の縦切りとして、Task の CRUD API をローカルで動かし、Vibe Coding ループを一周する。

## 1.1 講義: 最初の仕様は小さく

最初から DB・認証・UI を求めない。**メモリ保存の CRUD** に絞る。ただし後の成長のため **repository インターフェース**だけは最初から切る。

## 1.2 ハンズオン A: 仕様を書く（20 分）

`docs/spec/S-001-task-crud.md`:

```markdown
# S-001 タスク CRUD
## 目的
チームのタスクを登録・参照・更新・削除できる。
## Task
id(uuid) / title(1-100字,必須) / description(任意,最大1000字) /
status(todo|doing|done, 既定 todo) / createdAt / updatedAt
## 受け入れ基準
- POST /tasks → 201 と作成済み Task。title 不正は 400
- GET /tasks → 200 と配列（status クエリで絞り込み可）
- GET /tasks/{id} → 200 / 無ければ 404
- PATCH /tasks/{id} → 部分更新。無ければ 404
- DELETE /tasks/{id} → 204 / 無ければ 404
- エラー形式: { "error": { "code": string, "message": string } }
## スコープ外
認証、永続化、ページング
```

> 練習: Agent に「この仕様の曖昧な点を質問して」と依頼し、回答を仕様に反映する。

## 1.3 ハンズオン B: Plan → 実装（40 分）

**Step 1 計画**（コードを書かせない）

```text
@AGENTS.md @docs/spec/S-001-task-crud.md を読み、apps/api の実装計画を出してください。
Fastify + TypeScript + Zod + Vitest。TaskRepository インターフェースと
InMemoryTaskRepository を分けること。コードはまだ書かない。
```

計画を確認し、次を点検してから承認:
- ディレクトリ構成が `routes / schemas / repositories / app.ts / server.ts` に分離されているか
- `app.ts`（アプリ生成）と `server.ts`（listen）が分かれ、テスト容易か

**Step 2 実装**

```text
計画を承認します。まず雛形(package.json, tsconfig, lint, vitest 設定)だけ作成し、
`npm test` が空テストで通る状態にしてください。完了したら止まってください。
```

→ 確認後コミット。続けて:

```text
S-001 の受け入れ基準を先にテスト(Vitest + fastify.inject)として書き、失敗することを確認してから、
実装してテストを通してください。完了後 npm test / lint / typecheck の結果を報告してください。
```

## 1.4 ハンズオン C: 動作確認（20 分）

```powershell
npm run dev --workspace apps/api
curl -X POST http://localhost:3000/tasks -H "Content-Type: application/json" -d '{"title":"first"}'
curl http://localhost:3000/tasks
```

- 異常系（title 空、存在しない id）を手で確認
- 想定外の挙動があれば、**修正を頼む前に受け入れ基準へ追記**し、テストを足してから修正させる

## 1.5 ハンズオン D: OpenAPI を生成して固定（20 分）

```text
現在の実装から docs/openapi.yaml を生成してください。以後、API を変更する場合は
このファイルを同時に更新する規約を AGENTS.md に追記してください。
```

## 1.6 よくある失敗と対処

| 症状 | 対処 |
|---|---|
| 一度に大量のファイルを生成し把握不能 | Plan を細分化。雛形→テスト→実装の 3 コミット |
| テストを実装に合わせて書き換える | 「テストは仕様から。仕様に反するテストの変更は禁止」と AGENTS.md に追記 |
| 不要な依存が増える | 「新規依存は理由を提示し承認を得る」を AGENTS.md に追記 |

## 1.7 完了チェック

- [ ] 5 つのエンドポイントが curl で動く
- [ ] テスト・lint・型チェックが成功
- [ ] `docs/openapi.yaml` がある
- [ ] 3 回以上、小さくコミットした

---

## 動作確認で判明した注意点(実機検証済み)

- Windows では `curl` ではなく `curl.exe` を使うか `Invoke-RestMethod` を使う(Windows PowerShell 5.1 の `curl` は `Invoke-WebRequest` の別名)。PowerShell 7 では `-d '{"title":"x"}'` のようにそのまま書ける。`\"` でエスケープすると 400(不正な JSON)になる。
- Fastify の JSON パースエラーは `{error:{code,message}}` 形式にならない。エラー形式を統一したい場合は `setErrorHandler` で整形する。
- 初回の `npm install` / `vitest` は Windows のウイルス対策の影響で 30〜130 秒かかることがある。
- API テストは起動が遅い場合があるため、`vitest.config.ts` に `testTimeout: 20000` を設定する。
