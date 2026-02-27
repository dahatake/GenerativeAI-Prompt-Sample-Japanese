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


# Sample

**会員サービス**を題材にしたサンプルの要求定義や設計書などのサンプルです。

[サンプル](./samples/README.md)

# Step.1. GitHubのRepositoryの作成

GitHubのRepositoryを作成します。GitHub Sparkや、GitHub Copilot Coding Agentが作業をするためのリポジトリーです。

## Step.1.1. Custom Instructionsの作成

GitHubのRepositoryに、GitHub Copilot Coding Agentがより正確にタスクを実行できるような`.github/copilot-instructions.md`ファイルを作成します。

以下、例、です。

Microsoft DocsとAzureの**MCP Server**の指定がある点に注意してください。不要な場合は削除してください。

```text
# リポジトリ共通（repo-wide）カスタム指示

- 出力言語：日本語（コメント/ドキュメントも可能な限り日本語）。
- スコープ：ユーザー依頼の範囲「のみ」を実施。余計な機能追加・拡張はしない。
- 不確実性：根拠のない断定、ID/URL/ファイル名/数値の捏造は禁止。不足情報があれば質問は最大3つまで。前提は明示。
- 形式：見出し＋箇条書き中心。長い物語調は避け、簡潔に。
- 高リスク領域（法務/金融/コンプラ/安全等）：言い切りを避け、前提・根拠・確認事項を明示。

- Coding agent の実行ルール（Planner/分割/並列化/べき等性/再試行など）は `.github\agents\AGENTS.md` に従う。
- 常駐情報（用語、repo構成、テンプレ）は /docs/agent-playbook.md を参照。

```
Copilot を使用してタスクに取り組むためのベスト プラクティス:

https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks#adding-custom-instructions-to-your-repository

## Step. 1.2 MCP Server 設定
GitHubのRepositoryに、GitHub Copilot Coding AgentがMCP Serverを利用できるように設定します。

以下の両方のBlog Postを参考にしてください。Microsoft Learnと、AzureのMCP Serverの両方を設定します。

- GitHub Copilot Coding agent に Azure MCP Server の設定をする:

  https://learn.microsoft.com/ja-jp/azure/developer/azure-mcp-server/how-to/github-copilot-coding-agent

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

例えば、`ArchitectureDesign-microservice.md` の中で、ユースケース ID やファイルパスを変更できます:

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


#### 4. GitHub CopilotにIssueを自動的にアサインする認証設定

PAT（Personal Access Token）をシークレットに設定し使用します。

1. **Personal Access Token (PAT) を作成**

 - GitHub Settings → Developer settings → Personal access tokens (fine-grained)
 - 権限: `metadata: read`, `actions: read/write`, `contents: read/write`, `issues: read/write`, `pull_requests: read/write`
 - シークレット名: `COPILOT_PAT`
 
 **トークン文字列**が作成されるので、保存をする。


2. **リポジトリのシークレットに登録**
   - **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `COPILOT_PAT`
   - Value: 作成した PAT を貼り付け

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
- **PM-UseCaseDetail**: ユースケースの詳細定義書を作成

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

## Step.2. 要求定義などプロダクトマネジメントのドキュメントの整備

こちらのドキュメントを参考にしてください。

**Step 2.1. のユースケースの一覧まで**を行います。

なおMicrosoft 365 Copilotのリサーチツールの出力結果を、そのままMarkdownとして使用すると、根拠となった情報ソースへのURLや、サマリーのインフォグラフィックスのHTML文字列などが含まれています。
そのため、以下の様なPromptを使って、精緻なMarkdownのドキュメントを作成してください。その成型後の文字列をコピーしてMarkdownファイルとして保存します。

```text
{ドラフト文字}の中から、URLや、インフォグラフィックスや、HTML上での画像用の文字列などを削除して、精緻なMarkdownの文字列を作成してください。

# ドラフト文字列
(Microsoft 365 Copilotのリサーチツールの出力結果をここに貼り付け)
```

[要求定義の作成](/ビジネス戦略や分析/業務分析および改善策立案.md)

## Step.3. ユースケース作成

こちらのドキュメントを参考にしてください。

[ユースケース](./ProductManagement-Documentation.md)


## Step.4. アプリケーション設計

こちらのドキュメントを参考にしてください。

- microservicesアーキテクチャ と Polyglot Persistancyのアプリケーション設計

  主にWeb/スマホのアプリケーション

  [microservies](./ApplicationDesign-microservice-polyglotpersistence.md)

- AI Agentのアプリケーション設計

  [AI-Agent version](./ApplicationDesign-AIAgent.md)

  [AI-Agent-Simple version (まずはこちらをお勧め)](./ApplicationDesign-AIAgent-Simple.md)


## Step.5. アプリケーションのコードの実装と、Azureへのデプロイ

こちらのドキュメントを参考にしてください。

- Webアプリケーション

  [Webアプリ](./Development-WebAppOnAzure.md)

- AI Agent

  TBD

# 分割されたタスクを実行する

大きなジョブの場合は、途中でエラーになった際のリカバリーや、60分も待っていたのに結果が期待と大きく異なる事がある、といったリスクが考えられます。
そのため、このCustom Agentでは不正確ですが概算の作業時間を見積もって、10分程度でタスクが完了しそうな、つまり30-45分以内には終わるであろうタスクに分割をするように指示しています。
その際には `work`フォルダーにPromptが作成されています。

GitHub Copilot Coding agentで**sub Issue**として、既存のIssueの情報も参照できる状態にして、Taskを実行します。
その際のPromptの例です。

```text
以下のファイルの内容をPromptとして読み込んで、タスクとして実行してください。
- `work/future-scenario-detail-sub-1.md`
```


# うまくいかなかった時の対応例

以下は、作成する**量**や**タスクの複雑さ**に応じて。

### タスクが途中で終了する

> [!WARNING]
> 指示したタスクがすべて完了していないのに、GitHub Copilotがタスクを終了することがあります。その場合は、コメントでCopilotに指示を出して、再度Copilotにコードを生成してもらってください。あるいは、自分で作業を継続してください。

> 作業継続のPromptの例:

```text
@copilot
以下の作業の進捗状況のドキュメントも参考にして、残作業を実行してください。
- `work/{ユースケースID}/api-azure-deploy-work-status.md`
```

### 結果の妥当性チェック

結果の精度が低い場合もあります。各Promptの実行後のPull Requestの中で、`@copilot`で指定して、別タスクとしてチェックを行ってもらうのがおススメです。

```text
@copilot
あなたの回答は、私があなたに依頼した「目的」を達成できているのかを、毎回、異なる観点でレビューをして、問題点を10-50個リストアップをしてください。
リストアップした問題点に対する解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成してください。
このレビューは異なる観点で、3度行ってください。
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