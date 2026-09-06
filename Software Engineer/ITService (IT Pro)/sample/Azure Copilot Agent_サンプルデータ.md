対応Prompt: [../Azure Copilot Agent.md](../Azure Copilot Agent.md)

※以下はすべて架空のサンプルデータです。実在の企業・個人・環境・識別子とは無関係です。以下のサブスクリプション名・ID・リソース名は学習用です。生成されるコマンドや IaC は本番環境へ実行しないでください。

# 共通前提
- 会社: 星空フーズデジタル株式会社
- 対象基盤: EC・配送・需要予測を支える Azure 環境
- 主リージョン: Japan East
- DR リージョン: Japan West
- 監査要件: J-SOX 相当、監査ログ1年保持
- セキュリティ: PII と取引先契約情報を扱うため Private Link / Key Vault / Managed Identity 優先

## 1. セキュアな分析基盤を構築
```text
# 追加条件
- 1日 2.5TB の受注・配送イベントを収集
- 主要ソース: 店舗POS、EC、配送トラッキング、問い合わせチャネル
- 90日分は高速分析、1年分は低コスト保管
- 分析利用者: データアナリスト 25名、運用監査 6名
- ネットワーク: インターネット非公開、社内VPN と ExpressRoute 経由のみ
- 必須: Bicep、RBAC、診断設定、Key Vault、Private Endpoint、監査ログ、タグ設計
```

## 2. Azure OpenAI を IaC でデプロイ
```text
# 置換値
- <subscription>: `11111111-2222-3333-4444-555555555555`

# 補足要件
- リソースグループ: `rg-hoshizora-ai-sim-jpe`
- Azure OpenAI 名: `aoai-hoshizora-sim-jpe`
- モデル候補: `gpt-4o-mini`, `text-embedding-3-large`
- 接続元は `aca-chat-sim-jpe` と `func-rag-sim-jpe` のみ
- Key Vault 名: `kv-hoshizora-sim-jpe`
- Private DNS zone も含める
```

## 3. 既存リソースから逆 IaC を生成
```text
# 置換値
- <resourceGroup>: `rg-order-analytics-sim-jpe`

# 現在の主なリソース
- Storage Account: `storderanalsimjpe`
- Event Hubs Namespace: `evh-order-sim-jpe`
- Azure Data Explorer Cluster: `adx-order-sim-jpe`
- Log Analytics Workspace: `law-order-sim-jpe`
- Container Apps Environment: `cae-order-sim-jpe`
- Private Endpoints: storage / adx / key vault 用が各1つ

# 期待する差分確認
- タグ欠落
- 診断設定不足
- SKU の過不足
- ネットワーク公開設定の差分
```

## 4. アラートのキャッチアップ
```text
# 直近30日の重大アラート抜粋
1. `prod-app-5xx-spike` / App Service / Sev2 / 8回 / 原因候補: デプロイ直後の接続タイムアウト
2. `adx-hot-cache-pressure` / Data Explorer / Sev2 / 5回 / 原因候補: 月末分析ジョブ集中
3. `storage-private-endpoint-dns-fail` / Storage / Sev1 / 2回 / 原因候補: DNS zone link 漏れ
4. `containerapps-cpu-throttle` / Container Apps / Sev2 / 11回 / 原因候補: リビジョンの CPU 過小設定
5. `sql-deadlock-burst` / Azure SQL / Sev1 / 3回 / 原因候補: 在庫更新バッチ競合

# 欲しい整理軸
- サービス別
- 再発傾向
- 今週優先すべき対応
```

## 5. コンテナアプリの健全性診断
```text
# 置換値
- <containerAppName>: `ca-order-score-sim-jpe`

# メトリクス
- CPU 使用率: 平均 72%、p95 94%
- メモリ使用率: 平均 61%、p95 88%
- レプリカ数: 平日ピーク時 2→10、自動縮退は夜間 1
- エラーレート: 2.8%、特定のリビジョン `order-score--20260831-3` で 5xx 増加
- 平均応答時間: 920ms、p95 2.9s

# 補足
- イメージ: `ghcr.io/example/order-score:1.4.7`
- 現設定: 0.5 vCPU / 1Gi
- 依存先: Azure Cache for Redis, Azure SQL
```

## 6. 可観測性ギャップ分析
```text
# 対象サブスクリプション
- `sub-prod-hoshizora-sim`

# 未構成候補
- Azure Functions `func-nightly-import-sim` : AppLogs 未送信
- Service Bus Namespace `sb-order-sim-jpe` : OperationalLogs 未送信
- Key Vault `kv-b2b-sim-jpe` : AuditEvent 未送信
- API Management `apim-edge-sim-jpe` : GatewayLogs 未送信
- PostgreSQL Flexible Server `psql-core-sim-jpe` : QueryStore 監視未整備

# 既存の集約先
- Log Analytics: `law-shared-obsv-sim-jpe`
```

## 7. コスト要約と予測
```text
# 置換値
- <prod-sub>: `sub-prod-hoshizora-sim`
- <dev-sub>: `sub-dev-hoshizora-sim`

# 今月(8月)コスト
- prod: ¥4,820,000
  - AKS ¥1,420,000
  - Data Explorer ¥980,000
  - App Service ¥760,000
  - Azure SQL ¥640,000
  - Network/その他 ¥1,020,000
- dev: ¥1,360,000
  - AKS ¥420,000
  - Container Apps ¥210,000
  - Azure SQL ¥190,000
  - OpenAI ¥180,000
  - その他 ¥360,000

# 先月(7月)コスト
- prod: ¥4,120,000
- dev: ¥1,180,000

# 特記事項
- 8月下旬に需要予測 PoC が増え、OpenAI と AKS が上振れ
```

## 8. RI / Savings Plan の最適化
```text
# 過去90日の主要利用量
- App Service PremiumV3 P2v3: 6台 x 24h 稼働
- Azure SQL Business Critical 8 vCore: 2台 x 常時稼働
- D8ds_v5 VM: 12台、平均稼働率 82%
- AKS ノード(Standard_D4ds_v5): 常時 9〜14台

# 制約
- 1年コミット優先、3年は CFO 承認が必要
- 年末商戦で 11月〜12月は +30% の負荷見込み
- 一部ワークロードは来期に Container Apps へ移行可能性あり
```

## 9. 不要リソースの棚卸し
```text
# 30日以上未使用候補
- Managed Disk `disk-old-etl-sim-01` / 512GiB / 最終アタッチ 46日前
- NIC `nic-bastion-test-sim` / 接続先なし / 58日前
- Public IP `pip-unused-vpn-sim` / 未割当 / 73日前
- Snapshot `snap-sql-20260501-sim` / 保持ルール外 / 121日前

# 削除時の制約
- 本番切り戻しに使う資産は除外
- 削除前に所有者確認とタグ確認を必須化したい
```

## 10. ゾーン冗長でないリソースの一覧
```text
# 主要リソース抜粋
- Azure SQL `sql-order-sim-jpe` : zone redundant 無効
- App Service Plan `asp-bff-sim-jpe` : 単一ゾーン
- Redis `redis-core-sim-jpe` : 非ゾーン冗長
- NAT Gateway `nat-edge-sim-jpe` : 単一ゾーン

# 制約
- 予算増は月額 +15% まで
- RTO 2時間、RPO 15分
```

## 11. DR 設計の自動作成
```text
# 置換値
- <workload>: `受注・配送統合ワークロード`

# RTO/RPO
- RTO: 120分
- RPO: 15分

# 依存サービス
- Azure SQL, Redis, Blob, Service Bus, OpenAI, Container Apps
- 外部配送会社 API 2社

# 業務上の優先順位
1. 受注受付
2. 在庫引当
3. 配送通知
4. 分析ダッシュボード
```

## 12. カオス検証シナリオ
```text
# 検証対象
- 単一AZ障害
- Japan East リージョン障害
- 外部配送 API 応答 20秒遅延
- Redis キャッシュ全面喪失
- SQL 読み取り遅延急増

# 判定で見たい指標
- 注文受付継続可否
- 自動フェールオーバー時間
- 失敗時の手動Runbook有無
- 顧客通知の遅延時間
```

## 13. VM 接続不可のトラブルシュート
```text
# 置換値
- <vmName>: `vm-batch-admin-sim-01`

# 症状
- Azure Bastion 経由の RDP 接続がタイムアウト
- 2日前までは接続可能

# 構成
- VNet: `vnet-shared-sim-jpe`
- Subnet: `snet-admin`
- NSG: 3389 は Bastion subnet からのみ許可
- UDR: 既定ルートが Azure Firewall へ
- DNS: カスタム DNS `10.20.0.4`
- Identity: システム割り当て Managed Identity 有効

# 直近変更
- Firewall ルール更新
- NSG の IaC 再適用
```

## 14. 500/503 エラーの原因分析
```text
# 置換値
- <appName>: `app-order-bff-sim-jpe`

# 直近24時間の状況
- 503 が 11:40〜12:05 に集中
- 500 は 18:10 以降に断続発生
- デプロイ: `2026-08-31T11:32:00+09:00` に v2.14.0
- 設定変更: 同日 17:55 に SQL 接続プール上限を 80→30 へ変更

# ログ抜粋
- `System.TimeoutException: Timeout expired while getting connection from pool`
- `HttpRequestException: Response status code 503 from pricing-api`

# SLO
- p95 400ms
- 月間 99.95%
```

## 15. データベース遅延の調査
```text
# 対象
- Azure SQL Database `sqldb-order-core-sim`

# 直近観測
- CPU 82% 前後
- Data IO 78%
- Waits: `LCK_M_X`, `PAGEIOLATCH_SH`, `RESOURCE_SEMAPHORE`

# 上位クエリ
1. 注文一覧検索
   - 平均 1840ms
   - `WHERE tenant_id = @tenant AND created_at >= @from ORDER BY created_at DESC`
2. 在庫引当更新
   - 平均 920ms
   - 同時更新で deadlock 3件
3. 請求集計バッチ
   - 平均 12.4s

# 現状インデックス
- `orders(tenant_id, created_at)` なし
- `inventory_allocations(order_id)` のみ

# 制約
- スキーマ変更は夜間メンテナンスのみ
- 業務停止を伴う作業は不可
```
