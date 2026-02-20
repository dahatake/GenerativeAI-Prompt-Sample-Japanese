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

## 入力（必読）
- 必読ファイル
  - `docs/data-model.md`
  - `docs/service-list.md`
  - `docs/domain-analytics.md`
- 任意（存在すれば参照）
  - `docs/templates/agent-playbook.md`（社内テンプレ/語彙/表現ルールがある場合のみ）

## 成果物（必須）
- 設計ドキュメント（作成/更新）
  - `docs/Azure/AzureServices-data.md`
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
## 2. 入力（必読）
- リソースグループ名: `{リソースグループ名}`
- データストア定義: `docs/azure/AzureServices-data.md`
- サービスカタログ: `docs/service-catalog.md`
- サンプルデータ: `data/sample-data.json`

# 出力（必須）
- 事前準備スクリプト（必須）: `infra/azure/create-azure-data-resources-prep.sh`
- リソース作成スクリプト（必須）: `infra/azure/create-azure-data-resources.sh`
- データ登録スクリプト（必須）: `data/azure/data-registration-script.sh`
- ドキュメント更新（必須）: `docs/azure/service-catalog.md`：重複行を作らず追記
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
ユースケース内の全マイクロサービスについて、最適な Azure コンピュート（ホスティング）を選定し、根拠・代替案・前提・未決事項を設計書に記録する（ドキュメント作成特化）

### 入力（必読）
- リソースグループ名: `{リソースグループ名}`
- `docs/service-list.md`
- `docs/usecase-list.md`
- `docs/data-model.md`
- `docs/service-catalog.md`

### 成果物（必須）
- 設計書（Markdown）: `docs/azure/AzureServices-services.md`
```

### Step.2.2. 各サービスが利用する追加のAzureのサービスの選定

それぞれのサービスが追加で利用すると便利なAzureのサービスを選定します。例えばチャットボットであれば生成AI(Microsoft Foundry)を利用するなどです。

- 使用するカスタムエージェント
  - Dev-WebAzure-AddServiceDesign

```text
# タスク
サービス定義書の「外部依存・統合」から、追加で必要な Azure サービス（AI/認証/統合/運用等）を選定し、根拠（Microsoft Learn）付きで記録する

# Inputs（必読）
- リソースグループ名: `{リソースグループ名}`
- ユースケース: `docs//usecase-list.md`
- サービス一覧: `docs/service-list.md`
- 各サービス定義書: `docs/services/{サービスID}-{サービス名}-description.md`
- 既存採用済み（追加提案から除外）:
  - `docs/azure/AzureServices-services.md`
  - `docs/azure/AzureServices-data.md`

# Outputs（必須）
- 追加サービス設計（本成果物）:
  - `docs/azure/AzureServices-services-additional.md`
```

### Step.2.3. Azureの追加機能の作成

作成したAzureの追加機能の選定ドキュメントを参考にして、Azureのサービスを作成していきます。
`Microsoft Learn`の`MCP Server`を参照して、`Azure CLI`のコマンドを作成して、実行します。

- 使用するカスタムエージェント
  - Dev-WebAzure-AddServiceDeploy

```text
# タスク
 `docs/azure/AzureServices-services-additional.md` を根拠に、追加Azureサービスを **Azure CLI で冪等に作成**する。

# 入力
- リソースグループ名: `{リソースグループ名}`
- （任意だが推奨）`subscription` / `tenant` / 優先リージョン / 命名規則
根拠ファイル（必読）: `docs/azure/AzureServices-services-additional.md`

# 出力（必須）
- `infra/azure/create-azure-additional-resources-prep.sh`
- `infra/azure/create-azure-additional-resources/create.sh`
- （複数サービスの場合）`infra/azure/create-azure-additional-resources/services/<service>.sh`
- サービスカタログ: `docs/service-catalog.md` の表を更新する（重複行は作らない）。
```

### Step.2.4. 各サービスのコードの作成

バックエンドとしてのサービス部分のアプリケーションのコードを作成します。

- 使用するカスタムエージェント
  - Dev-WebAzure-ServiceCoding-AzureFunctions
    - Azure Functions用です。Containerなどの場合は、適時修正してください。

```text
# タスク
マイクロサービス定義書から全てのサービスの Azure Functions を実装し、テスト/最小ドキュメント/設定雛形まで揃える

# 入力
最低限ほしい情報：
- マイクロサービス定義書（例）：
  - `docs/services/{serviceId}-{serviceNameSlug}-description.md`
  - Azure Functionsのプログラミング言語: `C#（最新版のAzure Functionsでサポートされているもの）`
- 参照候補（存在すれば読む）：
  - `docs/service-list.md`
  - `docs/data-model.md`
  - `docs/service-catalog.md`
  - `docs/azure/AzureServices-*.md`

# 成果物（必須）
- 実装：
  - `api/{サービスID}-{サービス名}/` 配下に Azure Functionsを作成/更新
- テスト：
  - `test/api/` に単体テスト（外部I/Oはモック。CIで決定的に）
- 手動スモーク（任意だが推奨。自動テストに混ぜない）：
  - `test/api/smoke-ui/index.html`
```

### Step.2.5. Azure Compute の作成

作成した各サービスのコードを、それぞれのAzureのCompute Serviceを作成して、デプロイをします。


- 使用するカスタムエージェント
  - Dev-WebAzure-ComputeDeploy-AzureFunctions

```text
# タスク
サービスリストの全てのサービスを、Azure Functions用に作成/更新→デプロイ、GitHub Actions で CI/CD 構築、API スモークテスト（+手動UI）追加まで行う。AGENTS.mdのルールを守り、推測せず、根拠はリポジトリ内資料またはCLIヘルプ/実行結果で残す。

# Inputs（既定の参照場所）
- サービスリスト: `docs/service-list.md`
- サービスカタログ: `docs/service-catalog.md`
- リソースグループ名: `{リソースグループ名}`
- デプロイ対象コード: `api/{サービスID}-{サービス名}/`
- リージョン: `Japan East`（優先。利用不可なら `Japan West`、それも不可なら `Southeast Asia`）

# 出力（必須）
- Azure 作成スクリプト（Linux）: `infra/azure/create-azure-api-resources-prep.sh`
- GitHub Actions（CI/CD）
  - 配置: `/.github/workflows/`
  - 原則: OIDC + `azure/login`（可能なら secret-less を優先）
  - Functions デプロイ: Azure Functions 用公式 Action を利用（既存 Function App へデプロイ）
  - 例外: OIDC 不可の場合のみ publish profile 等を採用し、採用理由と設定手順を README に残す
  - 注意: Copilot が push しても workflow は自動実行されないことがあるため、PR 側でユーザーが実行承認できるよう説明を残す。

- サービスカタログ(更新): `docs/service-catalog.md` の表に追記/更新

- テスト（自動 + 手動UI）
  - 保存先: `test/{サービスID}-{サービス名}/`
  - 必須:
    1. 自動スモークテスト（HTTPでFunctions API呼び出し、主要レスポンス検証）
    2. 手動UI（最小の Web 画面：入力 → API呼び出し → 結果表示）
  - リポジトリ既存のテスト方式があればそれに従う。無ければ「依存追加なし」で動く最小構成を選ぶ。
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
画面定義書に基づき、全ての画面のUIを実装し、サービスカタログに基づくAPIクライアント層を整備する。

# 入力（参照順）

1. 画面定義書: `docs/screen/{画面ID}-description.md`
2. 画面一覧・遷移: `docs/screen-list.md`
3. サービスカタログ: `docs/service-catalog.md`
4. UI実装技術: `HTML5/CSS/JavaScript（リポジトリ既存規約に合わせる）`
5. 参考: `docs/usecase-list.md`
6. サンプルデータ: `data/sample-data.json`

# 出力（作る場所）
- 実装: `app/` 配下（既存構造がある場合はそれに合わせる）
```

## Step.3.1. Webアプリケーションのデプロイ

作成したWebアプリケーションをAzure Static Web Appsにデプロイします。

> [!IMPORTANT]
> ここでは、SPAあるいはStaticなHTMLの使用を前提にしています。Webサーバー側でHTML画面を生成する場合は、Azure Web Appsへのデプロイがお勧めです。


### Azure Static Web Appsを使う場合の、デプロイトークン設定

GitHubからのCI/CDで、GitHub側から設定をする際には、Azure Static Web AppsのデプロイトークンをGitHubのシークレットに設定する必要があります。
これはAzure Static Web Appsの作成後に**手動でしか設定が出来ません**ので、注意をしてください。

Azure 静的 Web アプリへのデプロイ:

https://docs.github.com/ja/enterprise-cloud@latest/actions/how-tos/deploy/deploy-to-third-party-platforms/azure-static-web-app

  - 「前提条件」のみを行ってください。


- 使用するカスタムエージェント
  - Dev-WebAzure-UIDeploy-AzureStaticWebApps
    - Azure Static Web Apps用です。

```text
# タスク
Azure Static Web Apps へのWebデプロイと、GitHub Actionsによる継続的デリバリー（CD）構築を、リポジトリ標準（AGENTS.md / skills）に従って実施する。

# Inputs（変数）
- リソースグループ名: `{リソースグループ名}`
- デプロイブランチ: `main` と PRプレビュー要否
- アプリの `app_location` / `api_location` / `output_location`（静的サイト/フレームワーク構成に依存）。以下がデフォルト
   - 実装: `app/`
   - APIクライアント層: `app/lib/api/`

既定（明示してよい仮定）
- リージョン優先: East Asia -> Japan West -> Southeast Asia

### 成果物（このジョブの対象）
1. `infra/azure/create-azure-webui-resources-prep.sh`
   - Linux bash。必要最小限の事前確認（az/login/拡張など）。冪等。
2. `infra/azure/create-azure-webui-resources.sh`
   - Azure Static Web Apps の作成/更新（az CLI）。冪等（既存時は安全に更新/終了）。
   - 実行可能性を重視し、CLIの妥当性は **実際に `az ... --help` / dry-run相当 / show** 等で確認する。
3. `.github/workflows/<deploy-workflow>.yml`（新規 or 更新）
   - GitHub Actions で SWA へデプロイ。
   - Secret `AZURE_STATIC_WEB_APPS_API_TOKEN` を参照（値は一切書かない）。
   - `app_location/api_location/output_location` は実ディレクトリ構造に合わせる。
4. `docs/service-catalog.md`
   - 作成したWebアプリURLを追記（取得できない場合は取得手順を追記）。
```

## Step.4. アーキテクチャレビュー

Microsoftの公式ドキュメントの情報を活用して、展開されたアーキテクチャのレビューを行います。

### Step.4.1.WAFなどに沿ったアーキテクチャレビュー

- 使用するカスタムエージェント
  - QA-AzureArchitectureReview

```text
# タスク
デプロイ済みAzureリソースを棚卸しし、Azure Well-Architected Framework（5本柱）と Azure Security Benchmark v3 を根拠にアーキテクチャ/セキュリティをレビューして、日本語のMermaid図付きレポートを生成する

- レビュー対象（いずれか）:
  - リソースグループ名: `{resourceGroupName}`
  - または サブスクリプション/範囲: `{subscriptionOrScope}`（RGが複数の場合）
- 参考ドキュメント（存在する範囲で）:
  - `docs/usecase-detail.md`
  - `docs/service-catalog.md`
  - `docs/azure/AzureServices-services.md`
  - `docs/azure/AzureServices-data.md`
  - `docs/azure/AzureServices-services-additional.md`

- 出力先（固定）:
  - `docs/azure/Azure-ArchitectureReview-Report.md`
```

### Step.4.2. 整合性チェック


- 使用するカスタムエージェント
  - QA-AzureDependencyReview

```text
# タスク
サービスカタログ準拠で Azure 依存（参照・設定・IaC）を証跡付きで点検し、必要なら最小差分で修正する

## 入力（未確定なら質問）
必須：
- リソースグループ名：`<resource-group>`（実環境照会を行う場合のみ必須）
- 必読：`docs/service-catalog.md`

推奨（存在するなら参照）：
- `docs/azure/AzureServices-services*.md`
- `docs/azure/AzureServices-data*.md`
- 参照先コード：`app/`, `api/`, `infra/`, `config/`, `.github/workflows/`

## 出力（固定）
- 最終成果物：`docs/azure/DependencyReview-Report.md`
```
