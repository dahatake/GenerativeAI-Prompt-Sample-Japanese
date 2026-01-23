
# Azure Copilot Agent プロンプト集（日本語版）

Azure Copilot のエージェント (プレビュー):

https://learn.microsoft.com/ja-jp/azure/copilot/agents-preview

## 1. Deployments & Infrastructure

### Prompt: セキュアな分析基盤を構築
```text
本番運用に耐えるセキュアな分析環境を構築してください。大量データの収集・ETL・可視化まで行える構成を Azure 上に自動設計し、必要なリソース（Storage、Event Hub、Data Explorer、Network、監査設定）をすべて含む完全な IaC（Bicep）を生成してください。
```

### Prompt: Azure OpenAI を IaC でデプロイ

```text
私の `<subscription>` に Azure OpenAI をデプロイする Bicep テンプレートを生成してください。ネットワーク分離（Private Endpoint）、Managed Identity、Key Vault の構成も含めてください。
```

### Prompt: 既存リソースから逆 IaC を生成
```text
`<resourceGroup>` 内のリソース構成を分析し、等価な Bicep を生成してください。また、生成したテンプレートとの差分（What-if）も提示してください。
```

## 2. Observability（可観測性）

### Prompt: アラートのキャッチアップ
```text
過去30日間に発生した重大アラートを要約し、サービス別の原因分類、再発傾向、優先すべき対応をリスト化してください。
```

### Prompt: コンテナアプリの健全性診断
```text
`<containerAppName>` の CPU・メモリ・スケール履歴・エラーレートを分析し、健全性評価とライトサイジングの提案を行ってください。
```

### Prompt: 可観測性ギャップ分析
```text
サブスクリプション全体で診断設定が未構成のリソースを一覧化し、推奨ログカテゴリ／メトリクス／アラートルールを提示してください。
```


## 3. Optimization（最適化）

### Prompt: コスト要約と予測（Ignite デモ日本語版）
```text
今月と先月のコストを `<prod-sub>` と `<dev-sub>` ごとに要約し、サービス別内訳を示してください。また、来月のコスト予測も提示してください。
```

### Prompt: RI / Savings Plan の最適化
```text
過去90日間の使用量から、Reserved Instance / Savings Plan の最適な組み合わせを提案し、削減額・回収期間・リスクを併記してください。
```

### Prompt: 不要リソースの棚卸し
```text
30日以上未使用のディスク、NIC、パブリックIP、Snapshot を一覧化し、安全に削除するためのステップを提案してください。
```

## 4. Resiliency（高可用性）

### Prompt: ゾーン冗長でないリソースの一覧
```text
現在のサブスクリプションでゾーン冗長化されていないリソースを一覧化し、冗長構成案と移行手順を提示してください。
```

### Prompt: DR 設計の自動作成
```text
`<workload>` の RTO/RPO に基づき、セカンダリ地域への DR 構成（データ複製、フェールオーバー手順、DR テスト計画）を生成してください。
```

### Prompt: カオス検証シナリオ
```text
単一AZ障害・リージョン障害・依存サービス障害のカオス検証シナリオを作成し、判定基準・回復手順を提示してください。
```

## 5. Troubleshooting & Support

### Prompt: VM 接続不可のトラブルシュート（Ignite デモ日本語版）
```text
`<vmName>` に接続できません。ネットワーク、NSG、ルート、DNS、Identity の観点で段階的に切り分けてください。解決できない場合はサポートチケットを作成してください。
```

### Prompt: 500/503 エラーの原因分析
```text
`<appName>` の 500/503 エラーを直近24時間で分析し、デプロイや設定変更との相関を基に根本原因と暫定対処策を示してください。
```

### Prompt: データベース遅延の調査
```text
Azure SQL / MI の上位クエリ、待機イベント、リソース利用状況を分析し、インデックス改善・プラン修正・スケール案を提示してください。
```
