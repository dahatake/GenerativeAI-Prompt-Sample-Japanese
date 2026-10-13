# カタログ(既存資産の一覧)

研修用の架空データです。手順1〜3のPromptの `<management_files>` が指す `docs/catalog.md` の「監査前」の状態を表します。

| 区分 | 名前 | 場所 | 関連する要求ID | 備考 |
| --- | --- | --- | --- | --- |
| API | `POST /purchase-orders` | `apps/api/src/routes/purchaseOrder/create.ts` | FR-010 | 受注登録。重複検知なし |
| API | `GET /purchase-orders` | `apps/api/src/routes/purchaseOrder/search.ts` | FR-011 | 注文検索。変更禁止 |
| サービス | `purchaseOrderService` | `apps/api/src/services/purchaseOrderService.ts` | FR-010 | トランザクション制御あり |
| テーブル | `purchase_orders` / `purchase_order_lines` | `apps/api/src/db/schema.sql` | FR-010 | `external_request_id` にユニーク制約なし |
| 共通部品 | 監査ログ出力 | `apps/api/src/lib/auditLogger.ts` | NFR-SEC-002 | 変更禁止 |
| 共通部品 | 認証ミドルウェア | `apps/api/src/routes/auth/` | NFR-SEC-001 | 変更禁止 |
| テスト | 受注登録の正常系・バリデーション系 | `apps/api/test/purchase-order/create.test.ts` | FR-010 | 再送・競合のテストなし |
