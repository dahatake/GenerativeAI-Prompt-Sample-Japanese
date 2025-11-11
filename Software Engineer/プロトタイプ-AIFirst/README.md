# アプリケーションのプロトタイプ開発 (GitHub Copilot Coding Agent / GitHub Copilot for Azure)


# はじめに

Copilot を使用してタスクに取り組むためのベスト プラクティス

https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks


- プロダクション環境での利用には十二分に注意をしてください。Pull Requestをマージするかどうかは、**人**の判断ですので!

## ツール

- GitHub Copilot Coding Agent

  GitHub Copilot の **Coding Agent**のIssueからCoding Agentに作業をしてもらう前提です。

  https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/


  - Firewallの設定
    - いくつかのAzureリソースにアクセスするために、Firewallの設定が必要です。GitHubのリポジトリーの [Settings] - [Copilot] - [Coding agent] - [Internet access] - [Custom allowlist] で、以下のドメインを追加してください。
      - https://management.azure.com
      - https://login.microsoftonline.com
      - https://aka.ms
      - https://app.aladdin.microsoft.com
  - 判断はお任せしますが。多様なMCP Serverを使うために、一時的に、Firewallの設定を[Enable Firewall]を`Off`にしても良いかもしれません。
  　　
- GitHub Copilot Spark
  Reactでの画面作成とGitHubのRepositryとの同期による、プレビューが秀逸です。リポジトリーにクローンすることで、リポジトリー側での作業結果のプレビューとしても利用できます。

  https://github.com/features/spark?locale=ja

- Visual Studio Code + GitHub Copilot Agent Mode

  **Visual Studio Code**の利用も強くおススメします。
  - Markdownのプレビュー機能を活用して、ドキュメントの確認や編集
  - Azure MCP Serverを利用した、各種Azure上のリソース一覧の文字列作成
  - GitHubリポジトリへ人が作成するファイルの追加
  - GitHub Copilotが作成したコードのテストや修正
  - GitHub Copilot Agentモードによるコーディング支援

  - Microsoft Azure のSDKを使う場合は、GitHub Copilot for Azure を使います。

    https://learn.microsoft.com/ja-jp/azure/developer/github-copilot-azure/introduction


# Hands-on Lab

**会員サービス**を題材にしたサンプルの要求定義や設計書などを参考にして1時間程度で完了するハンズオンラボです。

[ハンズオンのテキスト](HOL.md)


# Step.1. GitHubのRepositoryの作成

GitHubのRepositoryを作成します。GitHub Sparkや、GitHub Copilot Coding Agentが作業をするためのリポジトリーです。

## Step.1.1. Custom Instructionsの作成

GitHubのRepositoryに、GitHub Copilot Coding Agentがより正確にタスクを実行できるような`.github/copilot-instructions.md`ファイルを作成します。

以下、例、です。

Microsoft DocsとAzureの**MCP Server**の指定がある点に注意してください。不要な場合は削除してください。

```text
## ガイダンス
GitHub Copilot Coding Agentは、以下のガイドラインに従ってタスクを実行します。
- プランの作成や実行に情報が不足している場合は、ユーザーに尋ねてください

## Microsoftの公式ドキュメントの検索

あなたは **MicrosoftDoc** という MCP サーバーにアクセスすることができます。このツールを使用することで、Microsoft の最新の公式ドキュメントを検索することが可能であり、その情報は、あなたの学習データセットに含まれている内容よりも詳細であったり、新しいものである可能性があります。

Microsoft Azure、C#、F#、ASP.NET、Microsoft.Extensions、NuGet、など、Microsoft のネイティブ技術の取り扱いに関する質問に対応する際には、特に具体的または限定的な内容に関する場合、このツールを調査目的で使用するようにしてください。

## Microsoft Azureのリソースの検索

あなたは **Azure** という MCP サーバーにアクセスすることができます。このツールを使用することで、Microsoft Azureのリソースの作成・更新・削除・読み取りが可能であり、あなたの「学習データセットに含まれている情報よりも正しいです。例えば次のようなコマンドを使用して他の AI エージェントから Azure リソースと対話できます。

- "すべてのリソース グループを表示する"
- "'documents' という名前のストレージ コンテナー内の BLOB を一覧表示する"
- "アプリ構成の 'ConnectionString' キーの値は何ですか?
- "過去 1 時間のエラーをログ分析ワークスペースに照会する"
- "すべての Cosmos DB データベースを表示する"

## リポジトリ構成

- `lib/`: 主要なライブラリパッケージを格納します。  
- `admin/`: 管理者向けインターフェースのコンポーネントを含みます。  
- `config/`: 設定ファイルおよびテンプレートを格納します。  
- `docs/`: ドキュメントを格納します。  
- `data/`: アプリケーションで使用するデータファイルを格納します。  
- `test/`: テスト用のヘルパーおよびフィクスチャを格納します。  
- `src/`: WebアプリケーションのBuild前のコードを格納します。  
- `app/`: WebアプリケーションのBuild後コードを格納します。
- `api/`: apiのコードを格納します。
- `infra/`: インフラストラクチャのコードを格納します。
- `work/`: 作業の進捗状況を記録します。

## アーキテクチャとデザイン原則

### 認証とセキュリティ
- **絶対に資格情報をハードコーディングしないでください**
- Azure Key Vaultを使用して機密情報を管理してください
- 可能な限りマネージド アイデンティティを使用してください
- 最小権限の原則に従ってRBACを設定してください
- データの暗号化と安全な接続を有効にしてください

### インフラストラクチャ as コード
- Azure Bicepを優先してIaCファイルを作成してください
- Terraformを使用する場合は、Azure用のベストプラクティスに従ってください
- すべてのリソース名にresource tokenを使用してください
- タグ付けとリソースの整理を適切に行ってください

### エラーハンドリングと信頼性
- 一時的な障害に対して指数バックオフでリトライロジックを実装してください
- 適切なログ記録と監視を追加してください
- 必要に応じてサーキット ブレーカー パターンを含めてください
- リソースの適切なクリーンアップを確保してください

### パフォーマンスとスケーリング
- データベース接続プーリングを使用してください
- 同時操作とタイムアウトを設定してください
- 戦略的にキャッシュを実装してください
- リソース使用量を監視してください
- バッチ操作を最適化してください

## コーディング標準

### 言語固有のベストプラクティス
各プログラミング言語のベストプラクティスに必ず従ってください：

#### Python
- PEP 8 スタイルガイドに従ってください
- 型ヒント（Type Hints）を使用してください
- docstringsで関数とクラスを文書化してください
- pytest を使用してテストを記述してください

#### JavaScript/TypeScript
- ESLint とPrettierを使用してコードの品質を保ってください
- TypeScriptを優先して使用してください
- 適切なエラー処理とログ記録を実装してください
- Jest または Vitest を使用してテストを記述してください

#### C#/.NET
- .NET のコーディング規約に従ってください
- nullable reference types を有効にしてください
- ConfigureAwaitを適切に使用してください
- xUnit を使用してテストを記述してください

### ドキュメント
- すべてのプロジェクトに包括的なREADME.mdを含めてください
- APIドキュメントを自動生成してください（OpenAPI/Swagger）
- インラインコメントで複雑なロジックを説明してください
- アーキテクチャの決定事項を記録してください

## AI とプロンプトエンジニアリング

### プロンプト設計
- 明確で具体的な指示を提供してください
- コンテキストと例を含めてください
- 段階的な思考プロセスを促進してください
- 出力形式を明確に指定してください

### セキュリティ考慮事項
- プロンプトインジェクション攻撃を防ぐための対策を実装してください
- 機密情報の漏洩を防ぐためのガードレールを設定してください
- ユーザー入力の適切な検証とサニタイゼーションを行ってください

## デプロイメントとCI/CD

### Azure CLI (azd)
- 可能な限り `az` コマンドを使用してください
- `azure.yaml` ファイルを適切に設定してください

### GitHub Actions
- セキュアなCI/CDパイプラインを設定してください
- Azure サービス プリンシパルまたはOIDCを使用してください
- 環境固有の設定を管理してください
- 自動テストとセキュリティスキャンを含めてください

## データ管理

### データベース操作
- パラメータ化クエリを使用してください
- 適切なインデックス戦略を実装してください
- 接続管理を適切に処理してください
- 暗号化を有効にしてください
- クエリパフォーマンスを監視してください

### ストレージ操作
- ファイルサイズに応じて適切な方法を選択してください（100MB未満は単純、以上は並列）
- 複数ファイルにはバッチ操作を使用してください
- 適切なアクセス層を設定してください
- 同時実行性を管理してください

## 品質保証

### テスト戦略
- 単体テスト、統合テスト、E2Eテストを含む包括的なテスト戦略を実装してください
- テストカバレッジ80%以上を目標にしてください
- モックとスタブを適切に使用してください
- テストデータの管理を適切に行ってください

### コード品質
- 静的コード解析ツールを使用してください
- コードレビューのガイドラインに従ってください
- 技術債務を定期的に評価し、対処してください
- パフォーマンステストを実施してください

## 特記事項

このプロジェクトは日本語環境での生成AI活用を主目的としているため：
- 日本語のコメントとドキュメントを優先してください
- 日本の法規制とコンプライアンス要件を考慮してください
- 日本語特有の自然言語処理の課題を理解してください
- 文化的な文脈とビジネス慣行を反映してください
```

Copilot を使用してタスクに取り組むためのベスト プラクティス:

https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks#adding-custom-instructions-to-your-repository

## Step. 1.2 MCP Server 設定
GitHubのRepositoryに、GitHub Copilot Coding AgentがMCP Serverを利用できるように設定します。

以下の両方のBlog Postを参考にしてください。Microsoft Learnと、AzureのMCP Serverの両方を設定します。

- GitHub Copilot Coding agent に Azure MCP Server の設定をする:

  https://qiita.com/dahatake/items/3230a92532c35fec7599

- GitHub Copilot Coding agent に Microsoft Learn Docs MCP Server の設定をする

  https://qiita.com/dahatake/items/4f6f0deb53333c0200ef

GitHub Copilot の Coding AgentのMCP Serverの設定文字列::

```text
{
  "mcpServers": {
    "Azure": {
      "type": "local",
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start"
      ],
      "tools": ["*"]
    },
    "MicrosoftDocs": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp",
      "tools": ["*"]
    }
  }
}
```


## Step. 1.3 Custom Agent の設定と利用

GitHub Copilot Coding Agent では、**Custom Agent** を利用することで、特定のタスクに特化した専門的なエージェントを使用できます。このリポジトリには、アプリケーション開発の各フェーズで利用できる Custom Agent が用意されています。

### Custom Agent とは

Custom Agent は、特定のドメインやタスクに特化した AI エージェントです。例えば、アーキテクチャ設計、ドメインモデリング、Azure リソースのデプロイなど、専門的な知識が必要なタスクを効率的に実行できます。

公式ドキュメント:
https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents

### 準備手順

#### 1. Custom Agent ファイルのダウンロード

このリポジトリの `.github/agents/` フォルダーには、様々な Custom Agent ファイルが格納されています。

Custom Agent ファイルの格納場所:
https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese/tree/main/.github/agents

以下のいずれかの方法で、Custom Agent ファイルを取得してください:

**方法1: Git Clone でリポジトリ全体を取得**

```bash
git clone https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese.git
```

**方法2: 特定のフォルダーのみダウンロード（推奨）**

GitHub の Web インターフェースから:
1. 上記のリンクから `.github/agents/` フォルダーにアクセス
2. 画面右上の「Download ZIP」または各ファイルを個別にダウンロード

または、Git のスパースチェックアウトを使用:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese.git
cd GenerativeAI-Prompt-Sample-Japanese
git sparse-checkout set .github/agents
```

#### 2. 自分のリポジトリへのコピー

ダウンロードした Custom Agent ファイルを、あなたのプロジェクトのリポジトリの `.github/agents/` フォルダー以下に全てコピーします。

```bash
# 例: ローカルでコピーする場合
cp -r GenerativeAI-Prompt-Sample-Japanese/.github/agents/* your-project/.github/agents/
```

フォルダー構造は以下のようになります:

```
your-project/
├── .github/
│   ├── agents/
│   │   ├── ArchitectureDesign-microservice-Step1-1.md
│   │   ├── ArchitectureDesign-microservice-Step1-2.md
│   │   ├── ArchitectureDesign-microservice-Step2.md
│   │   ├── Business-Documentation-Step2-1.md
│   │   ├── Business-Documentation-Step2-2.md
│   │   ├── Implementation-WebAppOnAzure-Step1-1.md
│   │   ├── Implementation-WebAppOnAzure-Step2-1.md
│   │   └── ... (その他の Custom Agent ファイル)
│   └── copilot-instructions.md
├── README.md
└── ... (その他のプロジェクトファイル)
```

#### 3. Custom Agent ファイルの編集（オプション）

各 Custom Agent ファイルは、プロジェクトの要件に応じてカスタマイズできます。

例えば、`ArchitectureDesign-microservice-Step1-1.md` の中で、ユースケース ID やファイルパスを変更できます:

```markdown
## ユースケースID
- UC-xxx  ← あなたのユースケース ID に変更

## ユースケース
  - docs/usecase/{ユースケースID}/usecase-description.md  ← パスを変更
```

**編集する際の注意点:**
- ファイル先頭の YAML フロントマター（`---` で囲まれた部分）の `name` と `description` は Custom Agent の識別に使用されるため、わかりやすい名前に変更することをおすすめします
- `tools: ["*"]` は全てのツールへのアクセスを許可する設定です。必要に応じて制限できます
- プロンプトの内容は、プロジェクトの具体的な要件に合わせて調整してください

### 利用手順

#### Issue 作成時に Custom Agent を選択

1. **GitHub リポジトリで Issue を作成**
   - リポジトリの「Issues」タブから「New issue」をクリック

2. **Copilot にアサイン**
   - Issue の右側サイドバーで「Assignees」から `@copilot` を選択
   - または、Issue のコメント欄で `@copilot` をメンションして作業を依頼

3. **Custom Agent を選択（重要）**
   - Issue 作成時または Copilot へのアサイン時に、右側サイドバーに「Copilot」セクションが表示されます
   - 「Select agent」または「エージェントを選択」ドロップダウンから、使用したい Custom Agent を選択
   - 例: 「Architecture-Design-Step1-1-ドメイン分析」を選択

4. **タスクの詳細を Issue に記述**
   - Custom Agent が適切に動作するために、タスクの詳細、要件、参照すべきファイルパス、ユースケースID、Azureのリソースグループ名などを明確に記述してください
   - 例:
     ```markdown
     ## タスク
     要求定義ドキュメント（docs/requirements.md）を基に、ドメインモデリングを実施してください。
     
     ## 参照ファイル
     - docs/requirements.md
     - docs/usecase/UC-001/usecase-description.md
     ```

5. **Copilot が作業を実行**
   - 選択した Custom Agent が、専門知識を活用してタスクを実行します
   - 進捗状況は Pull Request として確認できます

### 利用可能な Custom Agent 一覧

このリポジトリには以下のような Custom Agent が用意されています:

#### ビジネスドキュメント関連
- **BizReq-UseCaseList**: 要求定義からユースケースを抽出してリスト化
- **BizReq-UseCaseDetail**: ユースケースの詳細定義書を作成

#### アーキテクチャ設計関連
- **Arch-micro-DomainAnalytics**: DDDの観点でドメインモデリングを実施
- **Arch-micro-ServiceIdentify**: マイクロサービス候補をリストアップ
- **Arch-DataModeling**: データモデル設計
- **Arch-micro-ServiceDetail**: 各サービスの詳細仕様作成
- **Arch-UI-List**: 画面一覧と画面遷移図の作成
- **Arch-UI-Detail**: 全画面の詳細定義書作成
- **Arch-micro-ServiceCatalog**: 画面・機能・API・データのマッピング表作成

#### 実装関連（Azure Web App）
- **Impl-WebAzure-DataDesign**: Polyglot Persistenceアーキテクチャに基づくデータストア選定
- **Impl-WebAzure-DataDeploy**: Azure CLIスクリプトでデータストア作成とサンプルデータ登録
- **Impl-WebAzure-ComputeDesign**: 各マイクロサービスに最適なAzureホスティング環境の選定
- **Impl-WebAzure-AddServiceDesign**: 追加で必要なAzureサービスの選定
- **Impl-WebAzure-AddServiceDeploy**: Azure CLIスクリプトで追加サービスを作成
- **Impl-WebAzure-ServiceCoding**: サービスのコード実装と単体テスト作成
- **Impl-WebAzure-UICoding**: WebアプリケーションのUIコード実装

#### レビュー
- **QA-AzureDependencyReview**: Azureリソースの依存関係とコスト最適化のレビュー
- **QA-AzureArchitectureReview**: アーキテクチャとセキュリティのレビュー

### ヒント

- **適切な Custom Agent を選択**: タスクの内容に応じて、最も適した Custom Agent を選択することで、より高品質な結果が得られます
- **段階的に進める**: 大きなプロジェクトは、複数の Custom Agent を順番に使用して段階的に進めることをおすすめします
- **カスタマイズ**: Custom Agent ファイルはテンプレートです。プロジェクトの要件に応じて自由に編集・追加してください
- **フィードバック**: Custom Agent の実行結果を確認し、必要に応じて Issue のコメントで追加指示を出すことができます

## Step.2. 要求定義などビジネス面のドキュメントの整備

こちらのドキュメントを参考にしてください。

[要求定義の作成](Business-Documentation.md)

## Step.3. アプリケーション設計

こちらのドキュメントを参考にしてください。

- microservicesアーキテクチャ と Polyglot Persistancyのアプリケーション設計

  [microservies](ApplicationDesign-microservice-polyglotpersistence.md)


## Step.4. アプリケーションのコードの実装と、Azureへのデプロイ

こちらのドキュメントを参考にしてください。

- Webアプリケーション

  [Webアプリ](Implementation-WebAppOnAzure.md)


# うまくいかなかった時の対応例

以下は、作成する**量**や**タスクの複雑さ**に応じて。

### タスクが途中で終了する

> [!WARNING]
> 指示したタスクがすべて完了していないのに、GitHub Copilotがタスクを終了することがあります。その場合は、コメントでCopilotに指示を出して、再度Copilotにコードを生成してもらってください。あるいは、自分で作業を継続してください。

> 作業継続のPromptの例:

```text
@copilot
以下の作業の進捗状況のドキュメントも参考にして、残作業を実行してください。
- work/{ユースケースID}/api-azure-deploy-work-status.md
```

### 結果の妥当性チェック

結果の精度が低い場合もあります。各Promptの実行後のPull Requestの中で、`@copilot`で指定して、別タスクとしてチェックを行ってもらうのがおススメです。

```text
@copilot
作成された全ての成果物を高精度に分析・解析して、目的に整合しているかの妥当性の検証してください。
もし改善点がある場合は、どのように改善すれば正しい回答が得られるかを論理的かつプロフェッショナルとして考えてください。
最初にこのタスクに取り組むべきポイントについて、3～7項目程度の簡潔なチェックリストを作成してください。このステップでは各項目は概念レベルでまとめ、実装詳細には踏み込みません。
その後、作成したチェックリストを参考にして、正しい回答を得るためのに考えた内容をプロンプトに反映して再度実行してください。
```

### CI/CDのジョブがエラーになる

- Azureと連携した後は、CopilotがPRを実行している際にGitHub Actionsでのジョブ実行を行います。その際に私たち人によるApprovalが必要です。ただ、そのGitHub Actionsのジョブがエラーになることがあります。

![Job Errorの例](/Software%20Engineer/プロトタイプ-AIFirst//images/image.png)

- その際には、PRのコメントに以下の様な指示をして、GitHub Copilotに修正をさせるのも手です。

```text
@copilot 
reviewのチェックで、github actionsのジョブがエラーになりました。原因をリストアップして、解決策を考えて、修正をしてください。
```


## Coding Agentのタスクの実行エラーの対応策

> [!IMPORTANT]
> この状況になったら、即座にジョブを停止させてください。GitHub Actionsの課金に影響が考えられます。

Coding AgentのGitHub Actionsでのタスクが失敗することがあります。
Pull Requestの`Session`の中で、`Run Back command`が繰り返されて、何も処理が行われていません。以下の様なPromptをPull Requestのコメントとして投入して、GitHub Copilot君に修正させてください。

- エラーメッセージ

```cmd
  Run Bash command
  $ undefined
  No command provided. Please supply a valid command to execute.
```

Prompt:

```promot
@copilot ジョブの途中でコマンド文字列を生成できずに、ジョブを実行しようとして{エラーメッセージ}が表示されています。原因を究明して、対応策を検討して、問題を修正してください。
対応策が、うまくいかない場合は、`段階的アプローチ - 各セクションを個別のコミットで追加`を試してみてください。

### エラーメッセージ
Run Bash command
$ undefined
No command provided. Please supply a valid command to execute.
```