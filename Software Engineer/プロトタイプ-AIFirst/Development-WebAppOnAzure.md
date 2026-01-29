# Web Application の作成

典型的なHTMLベースのWebアプリケーションの作成と、AzureへのDeployを行います。
参考となる設計書などのファイルはGitHubのRepositoryにUploadして、そのURLを参照させる形で、GitHub Copilot Coding Agentに作業をしてもらいます。
MCP Server経由で、ベストプラクティスや仕様の確認をしたり。Azure上のリソースの読み取りや、作成なども行います。

- 作成するコード
  - Web UI
  - REST API
  - Data based

- 作成するリソース
  - Azureのリソースの作成
  - サービス部分のコードはGitHubからのCI/CDの設定

- アーキテクチャ設計・実装とレビュー
  - Microsoft LearnのMCP Serverを参照して、最新のAzureのアーキテクチャ設計を行います。

## Step.1. データ

### Step.1.1. Azure のデータ保存先の選択

それぞれのエンティティの適切なデータの保存を行います。Microsoft Azureの中で最適なサービスの候補を作成します。

ここではCloud利用に最適な、**Polyglot Persistence**のアーキテクチャを採用します。

- 使用するカスタムエージェント
  - Dev-WebAzure-DataDesign

```text
# タスク
Polyglot Persistenceに基づき、全エンティティの最適Azureデータストア選定と根拠/整合性方針を文書化する

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`
- `docs/usecase/{ユースケースID}/data-model.md`
- `docs/usecase/{ユースケースID}/services/service-list.md`

# 出力（必須）
1) 設計ドキュメント
- `docs/usecase/{ユースケースID}/AzureServices-data.md`
```

### Step.1.2. データサービスのAzure へのデプロイと、サンプルデータの登録

作成したAzureのサービスを参考にして、Azureのサービスを作成していきます。
`Microsoft Learn`の`MCP Server`を参照して、`Azure CLI`のコマンドを作成して、実行します。

- 使用するカスタムエージェント
  - Dev-WebAzure-DataDeploy

```text
# タスク
Azure CLIでデータ系サービスを最小構成で作成し、サンプルデータを変換・一括登録する（冪等・検証付き）

# 入力
- ユースケースID: {ユースケースID}
- データストア定義: `docs/usecase/{ユースケースID}/AzureServices-data.md`
- サービスカタログ: `docs/usecase/{ユースケースID}/service-catalog.md`
- 既存サンプルデータ: `data/{ユースケースID}/sample-data.json`

# 出力（必須）
## 1) 事前準備スクリプト（Linux）
- `infra/{ユースケースID}/create-azure-data-resources-prep.sh`
  - 目的: 必要ツール/拡張のインストール、az拡張、前提チェック（ログイン、サブスクリプション、権限）
  - 要件: `set -euo pipefail`、実行ログ、失敗時の分かりやすいメッセージ

## 2) リソース作成スクリプト（Linux）
- `infra/{ユースケースID}/create-azure-data-resources.sh`
  - 目的: データストアのAzureサービスを最小構成で作成
  - 要件:
    - 冪等（存在チェック→作成/更新）。再実行で落ちない
    - リージョン: 原則 Japan East。利用不可時は Japan West → East Asia → Southeast Asia の順で自動フォールバック
    - 可能ならサーバーレス/最小SKU/オートスケール最小
    - リソース名: `{サービス名}` をベースにし、衝突回避トークンを付与（必要な場合）
    - タグ付け（usecase, env, owner 等。具体は repo-wide 指示に従う）
    - 作成後に `az ... show/list` 等で存在/設定を検証し、重要値（URL/ID/リージョン）を出力

## 3) データ登録スクリプト（Linux）
- `data/{ユースケースID}/data-registration-script.sh`
  - 目的: サンプルデータを変換し、各サービスへ一括登録
  - 要件:
    - 入力データの場所/形式を明示（不明なら Questions）
    - 変換（必要な場合）と登録を分離し、ログに件数/結果を出す
    - 登録後に最小の検証（件数取得/サンプル取得/クエリ）を実施

## 4) ドキュメント更新
- サービスカタログ追記: `docs/usecase/{ユースケースID}/service-catalog.md`
  - 追記する表の列（重複禁止）:
    - ServiceID（独自ID。無いなら null または “TBD”）
    - マイクロサービス名
    - サービス種別（例: Cosmos DB / Blob Storage 等）
    - サービスURL（接続先のURI等。無ければ null）
    - Azure Resource ID（/subscriptions/... のresourceId）
    - リージョン
```

## Step.2. マイクロサービス 作成

REST APIのエンドポイントを作成します。

作成したデータベースを参照して、REST APIのエンドポイントを作成します。Azure Functions上に作成します。Azure Functionsは、殆どのシナリオでのREST APIの実行環境に適しています。

### Step.2.1. Azureのサービスのホスト先の選択

それぞれのサービスの適切なホスティング環境を選定します。Microsoft Azureの中で最適なサービスの候補を作成します。

- 使用するカスタムエージェント
  - Dev-WebAzure-ComputeDesign

```text
# タスク
ユースケース内の全マイクロサービスについて、最適な Azure コンピュート（ホスティング）を選定し、根拠・代替案・前提を設計書に記録する

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`
- `docs/usecase/{ユースケースID}/data-model.md`
- `docs/usecase/{ユースケースID}/services/service-list.md`

# 出力（必須）
1) 設計書（Markdown）
- `docs/usecase/{ユースケースID}/AzureServices-services.md`
```

### Step.2.2. 各サービスが利用する追加のAzureのサービスの選定

それぞれのサービスが追加で利用すると便利なAzureのサービスを選定します。例えばチャットボットであれば生成AI(Microsoft Foundry)を利用するなどです。

- 使用するカスタムエージェント
  - Dev-WebAzure-AddServiceDesign

```text
# タスク
サービス定義書の「外部依存・統合」から、追加で必要な Azure サービス（AI/認証/統合/運用等）を選定し、根拠（Microsoft Learn）付きで記録する

# 入力
- ユースケースID: {ユースケースID}
- ユースケース: `docs/usecase/{ユースケースID}/usecase-description.md`
- サービス一覧: `docs/usecase/{ユースケースID}/services/service-list.md`
- 各サービス定義書: `docs/usecase/{ユースケースID}/services/{サービスID}-{サービス名}-description.md`
- 既存採用済み（除外用）:
  - `docs/usecase/{ユースケースID}/AzureServices-services.md`
  - `docs/usecase/{ユースケースID}/AzureServices-data.md`

# 出力（必須）
1) 追加サービス設計（本成果物）
- `docs/usecase/{ユースケースID}/AzureServices-services-additional.md`
```

### Step.2.3. Azureの追加機能の作成

作成したAzureの追加機能の選定ドキュメントを参考にして、Azureのサービスを作成していきます。
`Microsoft Learn`の`MCP Server`を参照して、`Azure CLI`のコマンドを作成して、実行します。

- 使用するカスタムエージェント
  - Dev-WebAzure-AddServiceDeploy

```text
# タスク
Azure CLIで追加サービス（例: Azure OpenAI等）を作成し、サービスカタログ/README/進捗ログを更新する（Planner必須・10分分割・冪等）

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/AzureServices-services-additional.md`

# 出力（必須）
- Azure CLIスクリプト: `infra/{ユースケースID}/create-azure-additional-resources/`
- 依存ツール準備スクリプト: `infra/{ユースケースID}/create-azure-additional-resources-prep.sh`
- サービスカタログ: `docs/usecase/{ユースケースID}/service-catalog.md`
```

### Step.2.4. 各サービスのコードの作成

バックエンドとしてのサービス部分のアプリケーションのコードを作成します。

- 使用するカスタムエージェント
  - Dev-WebAzure-ServiceCoding-AzureFunctions
  - Azure Functions用です。Containerなどの場合は、適時修正してください。

```text
# タスク
マイクロサービス定義書から {サービスID} の C# Azure Functions を実装し、必要な Azure 依存に接続し、テストとドキュメントを作成する

# 入力
- ユースケースID: {ユースケースID}
- マイクロサービス定義書：
  - `docs/usecase/{ユースケースID}/services/{サービスID}-[サービス名]-description.md`
- 参考：
  - `docs/usecase/{ユースケースID}/usecase-description.md`
  - `docs/usecase/{ユースケースID}/services/service-list.md`
  - `docs/usecase/{ユースケースID}/data-model.md`
  - `docs/usecase/{ユースケースID}/service-catalog.md`
  - `docs/usecase/{ユースケースID}/AzureServices-*.md`

# 出力（必須）
- 実装：
  - `api/{ユースケースID}/{サービスID}-{サービス名}/` 配下に Azure Functions (C#) を作成
- テスト：
  - 単体テスト（xUnit, 決定的・外部依存はモック）：`test/{ユースケースID}/api/`
  - 手動スモーク UI（デプロイ済み API を叩く簡易 HTML/JS。自動 unit test に混ぜない）：
    - `test/{ユースケースID}/api/smoke-ui/index.html`
```

### Step.2.5. Azure Compute の作成

作成した各サービスのコードを、それぞれのAzureのCompute Serviceを作成して、デプロイをします。


- 使用するカスタムエージェント
  - Dev-WebAzure-ComputeDeploy-AzureFunctions

```text
# タスク
Azure Functions 作成→デプロイ、GitHub Actions で CI/CD 構築、API スモークテスト（＋手動UI）を追加する

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/service-catalog.md`
- デプロイ対象のプログラムコード: api/{ユースケースID}/{サービスID}-{サービス名}/
  - {サービスID}は、各サービスのIDを設定する
  - {サービス名}は、各サービスの名称を設定する

以下が未確定なら、Planner の Questions で確認する：
- {ユースケースID}
- {リソースグループ名}
- 対象サービス一覧（サービスID/サービス名、必要な Azure サービス種別）
- {MicrosoftDocs} MCP / {Azure MCP Server} の利用可否（認証方法）
- デプロイ方式（OIDC 可否、publish profile 可否）

# 出力（必須）- 章立ての数値はカスタムエージェントに準拠
## 2.1 Azure 作成スクリプト（Linux）
- 準備スクリプト：`infra/{ユースケースID}/create-azure-api-resources-prep.sh`
  - Azure CLI 前提のチェック/導入（必要なら）
- リソース作成スクリプト：`infra/{ユースケースID}/create-azure-api-resources.sh`
  - **べき等**：各リソースは `show/exists` で存在確認→無ければ作成→あれば skip
  - 作成後、必要な値（URL/Resource ID/リージョン等）を取得できるようにする
- 実行：Azure CLI スクリプトは **Azure MCP Server で認証後に実行**。CLI仕様は MicrosoftDocs MCP を参照。

## 2.2 GitHub Actions（CI/CD）
- ワークフローは `/.github/workflows/` に配置する。
- 原則：OIDC + `azure/login` を用いた認証（可能なら secret-less を優先）。
- Azure Functions へのデプロイは `Azure/functions-action` を使用（既存 Function App へデプロイ）。
- 例外：OIDC が不可能な場合のみ、publish profile 等の代替を採用（採用理由と手順を README に記載）。

## 2.4 テスト（自動 + 手動UI）
- 保存先：`test/{ユースケースID}/`
- 必須：
  1) 自動スモークテスト（HTTP で Functions の API を呼び出し、主要レスポンスを検証）
  2) 手動用のシンプル Web 画面（引数入力→API呼び出し→戻り値表示）
- 「単体テスト」と記載があるが、性質上は **API スモーク/統合寄り**である旨を README に明記（テスト名は “smoke” 等にする）。

## 2.5 進捗ログ
- `work/{ユースケースID}/api-azure-deploy-work-status.md` に日本語で追記。
- 推奨セクション：
  - 実施内容 / 作成・更新ファイル一覧 / 実行結果（成功/失敗・エラー要約）/ 次アクション

# 3. リージョン選択
- 既定：Japan East
- 利用不可/非対応の場合：Japan West → East Asia → Southeast Asia の順でフォールバック。
- 変更した場合は理由（例：機能非対応/クォータ）を work-status に記録。
```

## Step.3. UI 作成

`GitHub Spark`を使う場合は、全てのサンプルデータとドキュメントを、そのままPromptの中に書き込みます。

> [!IMPORTANT]
> GitHub Sparkは**React**と**TypeScript**しか対応していません。

GitHub Copilot Coding AgentのIssueとして使います。
Copilot君にIssueをAssignして、Issueのコメントに以下の様な内容を書いてください。

> [!IMPORTANT]
> ここでは、SPAあるいはStaticなHTMLの使用を前提にしています。

- 使用するカスタムエージェント
  - Dev-WebAzure-UICoding
  - HTML5のみです。SPAのフレームワークを使う場合は、適時修正してください。

```text
# タスク
画面定義書に基づき、1画面ずつUIを実装し、APIクライアント層でサービス接続を整備する（進捗記録・10分超は分割）

# UI実装技術: HTML5, JavaScript,のみ。フレームワーク不要

# 入力
- ユースケースID: {ユースケースID}
- 画面一覧・画面遷移図: `docs/usecase/{ユースケースID}/screen/screen-list.md`
- 画面定義書: `docs/usecase/{ユースケースID}/screen/{画面ID}-description.md`
- 参考: `docs/usecase/{ユースケースID}/usecase-description.md`, `data-model.md`
- サービス: `docs/usecase/{ユースケースID}/services/service-catalog.md`（またはリポジトリに存在するサービスカタログ）
- サンプル: `data/{ユースケースID}/sample-data.json`

# 出力（必須）
- `app/{ユースケースID}`
```

## Step.3.1. Webアプリケーションのデプロイ

作成したWebアプリケーションをAzure Static Web Appsにデプロイします。

> [!IMPORTANT]
> ここでは、SPAあるいはStaticなHTMLの使用を前提にしています。Webサーバー側でHTML画面を生成する場合は、Azure Web Appsへのデプロイがお勧めです。

- 使用するカスタムエージェント
  - Dev-WebAzure-UIDeploy-AzureStaticWebApps
  - Azure Static Web Apps用です。

```text
# タスク
Azure Static Web Apps にWebをデプロイし、GitHub Actionsで継続的デリバリーを構築する

# 入力
- ユースケースID: {ユースケースID}
- リソースグループ名: {リソースグループ名}
- リージョン優先順: East Asia -> Japan West -> Southeast Asia
- サービスカタログ: docs/usecase/{ユースケースID}/service-catalog.md


# 出力（必須）
- Azure CLIスクリプト保存先:
  - infra/{ユースケースID}/create-azure-webui-resources.sh
  - infra/{ユースケースID}/create-azure-webui-resources-prep.sh
```

Azure Static Web Appsの作成ができない場合があります。その場合は、以下の手順を試してください。

> ### ステップ1: Azureリソース作成
> cd infra/{ユースケースID}
> ./create-azure-webui-resources.sh
> ### ステップ2: デプロイトークンをコピー（スクリプト出力から）
> ### ステップ3: GitHub Secretsに設定
> #### 1. Settings > Secrets and variables > Actions
> #### 2. New repository secret
> #### 3. Name: AZURE_STATIC_WEB_APPS_API_TOKEN
> #### 4. Value: コピーしたトークン

## Step.4. アーキテクチャレビュー

Microsoftの公式ドキュメントの情報を活用して、展開されたアーキテクチャのレビューを行います。

### Step.4.1.WAFなどに沿ったアーキテクチャレビュー

- 使用するカスタムエージェント
  - QA-AzureArchitectureReview

```text
# タスク
デプロイ済みAzureリソースを棚卸しし、Azure Well-Architected Framework（5本柱）と Azure Security Benchmark v3 を根拠にアーキテクチャ/セキュリティをレビューし、Mermaid図付きレポートを生成する

# 入力
- ユースケースID: {ユースケースID}
- レビュー対象: リソースグループ名 = {リソースグループ名}
- 参考ドキュメント:
  - `docs/usecase/{ユースケースID}/usecase-description.md`
  - `docs/usecase/{ユースケースID}/service-catalog.md`
  - `docs/usecase/{ユースケースID}/AzureServices-services.md`
  - `docs/usecase/{ユースケースID}/AzureServices-data.md`
  - `docs/usecase/{ユースケースID}/AzureServices-services-additional.md`

# 出力（必須）
  - `docs/usecase/{ユースケースID}/Azure-ArchitectureReview-Report.md`
```

### Step.4.2. 整合性チェック


- 使用するカスタムエージェント
  - QA-AzureDependencyReview

```text
# タスク
デプロイ済みAzureリソース（サービスカタログ記載）と、app/api/infra/config等の参照・設定整合を点検し、証跡付きでレビューし、必要なら最小差分で修正する

# 入力
- ユースケースID: {ユースケースID}
- リソースグループ名: {リソースグループ名}
- Webソース: `app/`
- APIソース: `api/`
- 必読: `docs/usecase/{ユースケースID}/service-catalog.md`
- 参考:
  - `docs/usecase/{ユースケースID}/AzureServices-services.md`
  - `docs/usecase/{ユースケースID}/AzureServices-data.md`
  - `docs/usecase/{ユースケースID}/AzureServices-services-additional.md`

# 出力（必須）
- `docs/usecase/{ユースケースID}/All-DependencyReview-Report.md`
```
