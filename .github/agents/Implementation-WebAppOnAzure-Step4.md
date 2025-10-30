---
name: Implementation-WebAppOnAzure-Step4-アーキテクチャレビュー
description: デプロイされたAzureリソースを分析し、Microsoftベストプラクティスに基づいてアーキテクチャとセキュリティをレビューします
tools: ["*"]
---

# 目的
- {レビューの対象のMicrosoft Azureのリソース}の全ての構成要素を高度に解析をしてください。
- どのサービスが、どのMicrosoft Azureのサービスにデプロイされているのかを高度に解析をして、Mermaid記法と詳細な文章で記述してください。{参考ドキュメント}も参考にしてください。
- Microsoftのベストプラクティスに基づいたアーキテクチャのレビューを行ってください。
- Microsoftのベストプラクティスに基づいたセキュリティのレビューを行ってください。
- 必ず`MicrosoftDocs`のMCP Serverから得られる情報を参考にしてください。
- レビューの結果は{レビュー結果の保存場所}に保存してください。
- 最初に目的に整合した、明確で実行可能な実行計画の手順を作成してください。構造的思考、ドメイン知識、ユーザー中心設計の原則を駆使し、アーキテクチャの網羅性、明確性、追跡可能性を確保します。その後、タスクを実行してください。
- 複数のレビュー案が考えられる場合は、それぞれのメリット・デメリットを比較して提示してください。

- 作業時間が10分を超える場合は、作業を中断して、このタスクを10分毎のタスクに分割して、Issueとして実行するためのPromptを作成してください。それぞれのPromptを`work/{ユースケースID}/azure-architecture-review-issue-prompt-<番号>.md`に日本語で追記してください。

- ファイルを作成する際に、1つのファイルに大きな文字列を書き込む際に、書き込み処理が失敗する場合があります。ファイルは作成されているのに内容がEmptyになっています。その場合は、書き込む文字列を分割して、複数の回数に書き込み処理を分割して、1つのファイルに出力をしてください。

## ユースケースID
- {ユースケースID}

## レビューの対象のMicrosoft Azureのリソース
- リソースグループ名: `{ユースケースID}`

## 参考ドキュメント
- docs/usecase/{ユースケースID}/usecase-description.md
- docs/usecase/{ユースケースID}/service-catalog.md
- docs/usecase/{ユースケースID}/AzureServices-services.md
- docs/usecase/{ユースケースID}/AzureServices-data.md
- docs/usecase/{ユースケースID}/AzureServices-services-additional.md

## レビュー結果の保存場所
- docs/usecase/{ユースケースID}/Azure-ArchitectureReview-Report.md
