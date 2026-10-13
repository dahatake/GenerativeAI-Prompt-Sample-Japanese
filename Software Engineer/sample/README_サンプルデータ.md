対応Prompt: [../README.md](../README.md)

※以下はすべて架空のサンプルデータです。実在の企業・個人・環境・識別子とは無関係です。

README の「要求定義書を基軸にしたVibe Coding」の手順1〜3(`<request>` `<answers>` `<references>` `<constraints>` `<execution_options>` `<run_options>`)に差し替えて入力するためのデータです。

# 想定シナリオ
- 対象システム: 受発注 API「OrderFlow Core」
- リポジトリ構成: `apps/api`(Node.js 20 / TypeScript 5.6 / Fastify 5), `apps/web`(React 18), `packages/shared`, `infra/bicep`
- DB: Azure Database for PostgreSQL Flexible Server 16
- 実行環境: dev / stg / prod の3環境。今回は `stg` 前提
- 対応したい課題: モバイル回線の再送で `POST /purchase-orders` が二重登録される
- SLO: API p95 400ms 以下、受注登録成功率 99.95%以上
- セキュリティ制約: 取引先担当者メールと電話番号はPII。ログへ平文出力禁止
- 変更禁止: 認証基盤、監査基盤、既存の注文検索 API

# 同梱ファイル(`orderflow-core/`)
実際にリポジトリへ置いて Agent に読ませるための抜粋です。`<references>` にパスで指定します。

| ファイル | 内容 |
| --- | --- |
| [docs/catalog.md](./orderflow-core/docs/catalog.md) | 手順1〜3の `<management_files>` の `catalog` に置く、監査前の既存資産一覧 |
| [apps/api/src/db/schema.sql](./orderflow-core/apps/api/src/db/schema.sql) | 現行スキーマ(`external_request_id` にユニーク制約なし) |
| [apps/api/src/routes/purchaseOrder/create.ts](./orderflow-core/apps/api/src/routes/purchaseOrder/create.ts) | 再送を考慮していない現行の受注登録ルート |
| [apps/api/src/services/purchaseOrderService.ts](./orderflow-core/apps/api/src/services/purchaseOrderService.ts) | 重複検知のない現行サービス |
| [logs/purchase_order_events_2026-08-28.csv](./orderflow-core/logs/purchase_order_events_2026-08-28.csv) | 障害当日の受注イベント231件。tohoku-sales の重複17組(タイムアウト後に2回登録)と通常登録を含む |

`requirements-definition.md` は手順1の出力で作られるため同梱していません。完成イメージは [RequirementsDefinition](../RequirementsDefinition/) を参照してください。

## 1. 手順1: 要求定義書の作成
### 1-1. 初回(`<request>` と `<references>`)
```text
<request>
OrderFlow Core の受注登録 API に idempotency key 対応を追加し、二重登録を防止したいです。
受け入れの目安:
1. 同一 tenant_id + idempotency key + リクエストボディの組み合わせでは1件だけ登録される
2. 同一 key で異なるボディが来た場合は 409 を返す
3. レスポンス形式は現行互換を維持する
4. 監査ログに `idempotencyKeyHash` を残すが、生値は残さない
5. stg 環境の回帰テストが全件通る
</request>

<references>
- docs/catalog.md、apps/api/src/db/schema.sql、apps/api/src/routes/purchaseOrder/create.ts、apps/api/src/services/purchaseOrderService.ts
- logs/purchase_order_events_2026-08-28.csv(先月の障害: 3G 回線の営業端末で17件の重複登録)
- 非機能: API p95 400ms 以下。DB ロック競合で p95 が 450ms を超える場合は再設計案も提示。新規依存パッケージ追加は原則禁止
- 変更禁止: 認証基盤、監査基盤、既存の注文検索 API
- 承認者の役割: プロダクト責任者(森田 友紀)、テックリード(佐々木 健)、監査担当(中村 玲)
- ログ抜粋:
  - `2026-08-28T10:14:55Z WARN request timeout after 3000ms requestId=8f2b6a10`
  - `2026-08-28T10:14:58Z INFO purchase order created orderId=7f1c3e90 tenant=tohoku-sales`
  - `2026-08-28T10:15:01Z INFO purchase order created orderId=ab4d52e7 tenant=tohoku-sales`
</references>
```

### 1-2. 2回目(`<answers>`)
質問票と承認依頼の番号は、1回目の出力に合わせて読み替えてください。
```text
<answers>
- 古いクライアントが x-idempotency-key を送れない場合は、段階導入のため当面は任意ヘッダーにする(推奨どおり)
- 同一 key の保持期間は 24 時間
- FR-xxx(受注登録の重複防止): 承認
- 監査ログの保持期間は監査チームが次回会議で確定するため、保留
- 残りはすべて推奨どおり
</answers>
```

## 2. 手順2: 新規作成・機能追加・修正(Waveごと)
### 2-1. Wave 1(`<request>` / `<references>` / `<constraints>` / `<execution_options>`)
```text
<request>
承認済みの「受注登録の重複防止」を実装してください。
- `external_request_id` を `idempotency_key_hash` に改名し、`tenant_id + idempotency_key_hash` の一意制約を追加
- リクエストボディの SHA-256 を `request_fingerprint` に保存し、同一 key で差分があれば 409(`IDEMPOTENCY_PAYLOAD_MISMATCH`)
- 監査ログにはハッシュ値のみ保存
- 再送、競合、409、監査ログ確認のテストを先に追加
</request>

<references>
- docs/catalog.md、apps/api/src/db/schema.sql、apps/api/src/routes/purchaseOrder/create.ts、apps/api/src/services/purchaseOrderService.ts
</references>

<constraints>
- ハッシュ方式は SHA-256 固定
- 既存データ移行は NULL 許容のまま段階導入。stg では feature flag なしで有効化
- 変更してよい範囲: `apps/api/src/routes/purchaseOrder/create.ts`、`apps/api/src/services/purchaseOrderService.ts`、`apps/api/src/lib/idempotency.ts`(新規作成可)、`apps/api/src/db/schema.sql`、`apps/api/test/purchase-order/create.test.ts`、`CHANGELOG.md`
- 変更禁止: `apps/web/**`、`apps/api/src/routes/auth/**`、`infra/**`
- ログに取引先担当者のメール・電話番号を平文で出さない
</constraints>

<execution_options>
implement_scope: 承認済みすべて
git_push: しない
deploy: しない
deploy_targets: なし
paid_services: 使わない
budget: なし
external_exposure: 公開しない
</execution_options>
```

### 2-2. Wave 2(未解決事項の追加 / `<answers>`)
```text
<request>
x-idempotency-key を送れない古いクライアントを考慮し、ヘッダー未指定時は従来どおり登録できるようにしてください(必須化は行わない)。
</request>

<answers>
- Q-001: B
- Q-002: 推奨どおり
- 残りはすべて推奨どおり
</answers>
```

### 2-3. 実装結果のレビュー・確認に使う抜粋
Wave 1 の Pull Request を人が確認する場面や、手順3の期待値を考える材料として使います。
```ts
const idempotencyKey = request.headers['x-idempotency-key'];
const idempotencyKeyHash = createSha256(idempotencyKey);
const requestFingerprint = createSha256(JSON.stringify(request.body));
```

```ts
if (existing && existing.requestFingerprint !== requestFingerprint) {
  throw new ConflictError('IDEMPOTENCY_PAYLOAD_MISMATCH');
}
```

```ts
auditLogger.info('purchase_order_created', {
  tenantId,
  orderId: created.orderId,
  idempotencyKeyHash
});
```

- 検証結果: `pnpm test --filter create.test.ts` pass / `pnpm lint apps/api` pass / `pnpm typecheck` pass
- 未解決事項: 古いクライアントが `x-idempotency-key` を送れない可能性(2-2 で対応)、監査ログ保持期間は監査チームが次回会議で確定予定

## 3. 手順3: System Test の作成と実行
Wave の完了後に実行します。`<run_options>` の値は次のとおりです(要求定義書の受入基準から台帳が作られます)。
```text
<run_options>
max_minutes: 60
environment: local
auto_fix: しない
fix_max_attempts: 1
</run_options>
```
2回目以降は、台帳(`tests/system/ledger.json`)が作られている状態で同じ入力を送り、変更のあったケースだけが増分で実行されることを確認します。受入基準4(`idempotencyKeyHash` のみ記録)の異常系は、ログ出力に生の key が含まれないことを確かめるケースにしてください。
