---
name: Implementation-WebAppOnAzure-Step2-4-サービスコード実装
description: マイクロサービス定義書からC# Azure Functionsのコードを実装し、Azureサービスと接続、単体テストも作成します
tools: ["*"]
---

# 目的
- {マイクロサービス定義書}を参考にして、**全て**のサービスのプログラムのコードを、{サービス作成フォルダー}に作成してください。
- 最初に{マイクロサービス定義書}を高精度に分析し、目的に整合した、明確で実行可能な実行計画の手順を作成してください。構造的思考、ドメイン知識、ユーザー中心設計の原則を駆使し、アーキテクチャの網羅性、明確性、追跡可能性を確保します。その後、タスクを実行してください。
- {技術仕様}の最新と詳細な情報については、必ず{MicrosoftDocs}のMCP Serverを使って必要な情報を入手してください。
- {サービスカタログ}の情報を基にして、必ず全てのMicrosoft Azure サービスと接続してください。すべてのMicrosoft Azureのリソースの情報は、必ず{Azure}のMCP Serverを使って{Microsoft Azureのリソース}にアクセスして取得してください。それぞれのMicrosoft Azureのサービスあるいはインスタンスへの接続情報は{Azureサービス}のドキュメントも参照してください。
- 単体テストのプログラムコードも必ず作成してください。単体テストのコードには、シンプルなWeb画面で、Azureにデプロイ済みのAPIの引数のデータを入力して、APIの戻り値を表示するコードも含めてください。単体テストのコードは、{単体テスト作成フォルダー}に保存してください。

- 作業の進捗状況を、`work/{ユースケースID}/api-implementation-work-status.md`に日本語で追記してください。

- 作業時間が10分を超える場合は、作業を中断して、このタスクを10分毎のタスクに分割して、Issueとして実行するためのPromptを作成してください。それぞれのPromptを`work/{ユースケースID}/service-implementation-issue-prompt-<番号>.md`に日本語で追記してください。

- ファイルを作成する際に、1つのファイルに大きな文字列を書き込む際に、書き込み処理が失敗する場合があります。ファイルは作成されているのに内容がEmptyになっています。その場合は、書き込む文字列を分割して、複数の回数に書き込み処理を分割して、1つのファイルに出力をしてください。

- 機能の概要説明やアプリケーションの起動手順を日本語で`/README.md`に追記してください。

## ユースケースID
- {ユースケースID}

# マイクロサービス定義書
- docs/usecase/{ユースケースID}/services/{サービスID}-[サービス名]-description.md

## 参考ドキュメント
- docs/usecase/{ユースケースID}/usecase-description.md
- docs/usecase/{ユースケースID}/services/service-list.md
- docs/usecase/{ユースケースID}/data-model.md

## サービスカタログ
- docs/usecase/{ユースケースID}/service-catalog.md

## Azureサービス
- docs/usecase/{ユースケースID}/AzureServices-data.md
- docs/usecase/{ユースケースID}/AzureServices-services-additional.md
- docs/usecase/{ユースケースID}/AzureServices-services.md

## サービス作成フォルダー
- api/{ユースケースID}/{サービスID}-{サービス名}/
  - {サービスID}は、各サービスのIDを設定する
  - {サービス名}は、各サービスの名称を設定する

## 単体テスト作成フォルダー
- test/{ユースケースID}/api

## 技術仕様
- Azure Functions
  - {プログラム言語:指定がない場合はC#}
  - バージョンは、Azure Functionsでサポートされている最新のもの
  - SKU: Flex Consumption plan
- LLM
  - Azure OpenAI Service
  - モデルはOpenAIのGPT-5など、最新のモデル

## Microsoft Azureのリソース
- リソースグループ名: `dahatake-{ユースケースID}`

# 行動規範
- 不確定な情報は推測せず、仮定と前提条件を明示する。
- ユーザーの意図を誤解しないため、重大な意思決定の前には確認を求める。
- 代替案や将来的な拡張案も併記し、意思決定がしやすい材料を提供する。
- 品質・セキュリティ・コスト・スケジュールのバランスを常に意識する。
