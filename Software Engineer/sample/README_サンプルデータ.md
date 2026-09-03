対応Prompt: [../README.md](../README.md)

※以下はすべて架空のサンプルデータです。実在の企業・個人・環境・識別子とは無関係です。

# 想定シナリオ
- 対象システム: 受発注 API「OrderFlow Core」
- リポジトリ構成: `apps/api`(Node.js 20 / TypeScript 5.6 / Fastify 5), `apps/web`(React 18), `packages/shared`, `infra/bicep`
- DB: Azure Database for PostgreSQL Flexible Server 16
- 実行環境: dev / stg / prod の3環境。今回は `stg` 前提
- 対応したい課題: モバイル回線の再送で `POST /purchase-orders` が二重登録される
- SLO: API p95 400ms 以下、受注登録成功率 99.95%以上
- セキュリティ制約: 取引先担当者メールと電話番号はPII。ログへ平文出力禁止
- 変更禁止: 認証基盤、監査基盤、既存の注文検索 API

## 1. プラン作成向け入力
```text
# タスク概要
OrderFlow Core の受注登録 API に idempotency key 対応を追加し、二重登録を防止したいです。

# 現在の実装
- `apps/api/src/routes/purchaseOrder/create.ts`
  - 受注ヘッダー INSERT 後に明細 INSERT
  - タイムアウト時の再送を考慮していない
- `apps/api/src/services/purchaseOrderService.ts`
  - DB トランザクション制御あり
  - リクエスト単位の重複検知なし
- `apps/api/src/db/schema.sql`
  - `purchase_orders(order_id uuid pk, tenant_id text, external_request_id text null, total_amount numeric(12,2), created_at timestamptz)`
  - `external_request_id` にユニーク制約なし
- `apps/api/test/purchase-order/create.test.ts`
  - 正常系とバリデーション系のみ

# 受け入れ条件
1. 同一 tenant_id + idempotency key + リクエストボディの組み合わせでは1件だけ登録される
2. 同一 key で異なるボディが来た場合は 409 を返す
3. レスポンス形式は現行互換を維持する
4. 監査ログに `idempotencyKeyHash` を残すが、生値は残さない
5. stg 環境の回帰テストが全件通る

# 非機能要件
- 新規依存パッケージ追加は原則禁止
- DB ロック競合で p95 が 450ms を超える場合は再設計案も提示
- 障害時のロールバック手順を用意

# 参考情報
- 先月の障害: 3G 回線利用の営業端末で 17件の重複登録
- ログ抜粋:
  - `2026-08-28T10:14:55Z WARN request timeout after 3000ms requestId=8f2...`
  - `2026-08-28T10:14:58Z INFO purchase order created orderId=7f1... tenant=tohoku-sales`
  - `2026-08-28T10:15:01Z INFO purchase order created orderId=ab4... tenant=tohoku-sales`
- 関係者
  - プロダクト責任者: 森田 友紀
  - テックリード: 佐々木 健
  - 監査担当: 中村 玲

# 出力してほしいもの
- 詳細な実装プラン
- 小さな Issue への分割
- 要確認事項
```

## 2. タスク実行向け入力
```text
# 承認済みプラン
- Issue 1: `schema-add-idempotency-constraint`
  - `external_request_id` を `idempotency_key_hash` に改名し、`tenant_id + idempotency_key_hash` の一意制約を追加
- Issue 2: `api-validate-request-fingerprint`
  - リクエストボディの SHA-256 を保存し、同一 key で差分があれば 409
- Issue 3: `audit-log-mask-key`
  - 監査ログにハッシュ値のみ保存
- Issue 4: `add-regression-tests`
  - 再送、競合、409、監査ログ確認のテスト追加

# 実装順
1. Issue 4 のテスト追加
2. Issue 1 / 2
3. Issue 3
4. 既存テスト + 対象テスト実行

# 変更対象として承認されたファイル
- `apps/api/src/routes/purchaseOrder/create.ts`
- `apps/api/src/services/purchaseOrderService.ts`
- `apps/api/src/lib/idempotency.ts` (新規作成可)
- `apps/api/src/db/schema.sql`
- `apps/api/test/purchase-order/create.test.ts`
- `CHANGELOG.md`

# 変更禁止
- `apps/web/**`
- `apps/api/src/routes/auth/**`
- `infra/**`

# 追加の判断
- ハッシュ方式は SHA-256 固定
- 既存データ移行は NULL 許容のまま段階導入
- stg では feature flag なしで有効化
```

## 3. レビュー向け入力
```text
# レビュー対象の目的
重複受注を防止しつつ既存 API 互換を維持できているか確認したいです。

# 変更概要
- `schema.sql`
  - `idempotency_key_hash text null`
  - `request_fingerprint text null`
  - `unique (tenant_id, idempotency_key_hash)`
- `purchaseOrderService.ts`
  - 同一 hash の既存受注取得
  - fingerprint 不一致時 `ConflictError`
- `create.ts`
  - ヘッダー `x-idempotency-key` を必須化
  - 監査ログへ `idempotencyKeyHash` を出力
- `create.test.ts`
  - 再送成功、差分409、ログマスキング、並列再送の4ケース追加

# レビュー用抜粋
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

# テスト結果
- `pnpm test --filter create.test.ts` : pass
- `pnpm lint apps/api` : pass
- `pnpm typecheck` : pass

# 未解決事項
- 古いクライアントが `x-idempotency-key` を送れない可能性あり
- 監査ログ保持期間は監査팀が次回会議で確定予定
```
