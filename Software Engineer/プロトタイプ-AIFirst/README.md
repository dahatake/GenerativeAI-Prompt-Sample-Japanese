# アプリケーションのプロトタイプ開発 (GitHub Copilot Coding Agent / GitHub Copilot for Azure)

ここでは、ユーザーを早期に巻き込むフィードバックループを目的に以下の順番で進めていきます。

# ツール

- GitHub Copilot Coding Agent

  GitHub Copilot の **Coding Agent**のIssueからCoding Agentに作業をしてもらう前提です。

  https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/

- GitHub Copilot Spark
  Reactでの画面作成とGitHubのRepositryとの同期による、プレビューが秀逸です。

  https://github.com/features/spark?locale=ja

- Visual Studio Code

  **Visual Studio Code**の利用も強くおススメします。
  - Markdownのプレビュー機能を活用して、ドキュメントの確認や編集
  - Azure MCP Serverを利用した、各種Azure上のリソース一覧の文字列作成
  - GitHubリポジトリへ人が作成するファイルの追加
  - GitHub Copilotが作成したコードのテストや修正
  - GitHub Copilot Agentモードによるコーディング支援

## 必読ドキュメント!!!

Copilot を使用してタスクに取り組むためのベスト プラクティス

https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks


- 現時点でプレビューです。プロダクション環境での利用には十二分に注意をしてください。Pull Requestをマージするかどうかは、**人**の判断ですので!
- AzureとCDで連携した後は、CopilotがPRを実行している際にGitHub Actionsでのジョブ実行を行います。その際に私たち人によるApprovalが必要です。ただ、そのGitHub Actionsのジョブがエラーになることがあります。

![Job Errorの例](/Software%20Engineer/プロトタイプ-AIFirst//images/image.png)

- その際には、PRのコメントに以下の様な指示をして、GitHub Copilotに修正をさせるのも手です。

```text
reviewのチェックで、github actionsのジョブがエラーになりました。原因をリストアップして、解決策を考えて、修正をしてください。
@copilot 
```
Microsoft Azure のSDKを使う場合は、GitHub Copilot for Azure を使います。

https://learn.microsoft.com/ja-jp/azure/developer/github-copilot-azure/introduction


# 1. 要求定義などビジネス面のドキュメントの整備

こちらのドキュメントを参考にしてください。

[要求定義の作成](Documentation.md)

# 2. 論理設計

こちらのドキュメントを参考にしてください。

[アプリケーション設計](applicationDesign.md)

# 3. Prompt用のドキュメント作成

## 作成結果のドキュメントの保存場所

幾つかのファイルはGitHubのRepositoryにUploadして、そのURLを参照させる形で、GitHub Copilot Coding Agentに作業をしてもらいます。


### /docs フォルダーに置きたいドキュメント
- ユースケース
  - コードの元となるドキュメント。画面一覧、サービス一覧、マッピング表なども、強い関連性を考慮するとこのファイルに入れておくのが良いかと思います。
  - ファイル名の例: UC-001.md
  - [Prompt](applicationDesign.md#step12-ユースケース作成)
- マイクロサービス定義書
  - REST APIのエンドポイント
  - ファイル名の例: UC-001_DashboardService.md
  - [Prompt](applicationDesign.md#step32-マイクロサービスの作成)
- データモデル
  - データの定義。アプリケーションの場合は、Azure Cosmos DBのSQL API (ドキュメント型)のモデルがおススメ
  - ファイル名の例: UC-001-DataModel.md
  - [Prompt](applicationDesign.md#step-23-データモデル作成)


# 3. GitHubのRepositoryの作成

GitHubのRepositoryを作成します。GitHub Sparkや、GitHub Copilot Coding Agentが作業をするためのリポジトリーです。


# 4. Custom Instructionsの作成

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

あなたは **Azure** という MCP サーバーにアクセスすることができます。このツールを使用することで、Azure Model Context Protocol (MCP) サーバーには、自然言語プロンプトを使用して Azure サービスを操作するために既存のクライアントから使用できる多くのツールが公開されています。 たとえば、Azure MCP サーバーを使用して、Visual Studio Code の GitHub Copilot エージェント モードまたは次のようなコマンドを使用して他の AI エージェントから Azure リソースと対話できます。

- "すべてのリソース グループを表示する"
- "'documents' という名前のストレージ コンテナー内の BLOB を一覧表示する"
- "アプリ構成の 'ConnectionString' キーの値は何ですか?
- "過去 1 時間のエラーをログ分析ワークスペースに照会する"
- "すべての Cosmos DB データベースを表示する"

## リポジトリ構成

- `internal/`: 他の GitHub サービスとの連携に関するロジックを含みます。  
- `lib/`: 主要なライブラリパッケージを格納します。  
- `admin/`: 管理者向けインターフェースのコンポーネントを含みます。  
- `config/`: 設定ファイルおよびテンプレートを格納します。  
- `docs/`: ドキュメントを格納します。  
- `data/`: アプリケーションで使用するデータファイルを格納します。  
- `test/`: テスト用のヘルパーおよびフィクスチャを格納します。  
- `labs/`: 実験的なコードやプロトタイプを格納します。
- `src/`: WebアプリケーションのBuild前のコードを格納します。  
- `app/`: WebアプリケーションのBuild後コードを格納します。
- `api/`: apiのコードを格納します。
- `infra/`: インフラストラクチャのコードを格納します。

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

### Azure Developer CLI (azd)
- 可能な限り `azd` コマンドを使用してください
- `azd up` でのデプロイ前に `azd provision --preview` で検証してください
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


# 5. UI 作成

**サンプルデータ**と、**画面定義のドキュメント**をリポジトリーにUploadして、そのファイルのURLを参照させます。

GitHub Sparkを使う場合は、全てのサンプルデータとドキュメントを、そのままPromptの中に書き込みます。

> [!IMPORTANT]
> GitHub Sparkは**React**と**TypeScript**しか対応していません。

GitHub Copilot Coding AgentのIssueとして使います。Copilot君にIssueをAssignして、Issueのコメントに以下の様な内容を書いてください。

## 5.1. Webアプリケーションのプロトタイプ作成

```text
# 役割
あなたは、世界最高峰のソフトウェアエンジニアであり、同時に卓越したUX/UIデザイナーです。ユーザー中心設計（UCD）と最新のWeb技術（React, TypeScript, Tailwind CSS, Next.jsなど）に精通し、ビジネス価値とユーザー体験を両立させるWebアプリケーションを設計・実装します。アクセシビリティ、レスポンシブデザイン、パフォーマンス最適化、そして美的感覚に優れたUIを追求します。

## 行動指針
- ユーザーの目的と文脈を深く理解し、最適なUX/UIを提案する
- コードは読みやすく、再利用性が高く、最新のベストプラクティスに準拠する
- デザインは直感的で、視覚的にも洗練されていること
- アクセシビリティ（WCAG）と国際化（i18n）を常に考慮する
- フィードバックを迅速に反映し、継続的に改善する

# 目的
- {画面定義書}に基づいて、Webアプリケーションの画面を作成の実行計画を作成してください。
  - {画面定義}.md

# 実行計画
- 最初に画面定義書を実行計画を高精度に分析し、目的に整合した、明確で実行可能な実行計画の手順を作成してください。構造的思考、ドメイン知識、ユーザー中心設計の原則を駆使し、画面定義書の網羅性、明確性、追跡可能性を確保します。実行計画は、複数名でのDevOpsでのアプリケーション開発の原則を深く考慮して、並列で同時実行が出来るように作成するファイルを必ず別にしてください。

## 作成フォルダ
- `{app/フォルダ名}`

## 技術仕様
- HTML5のみ使用
- JavaScript

## 注意事項
- 機能の概要説明やアプリケーションの起動手順を日本語で`/README.md`に記載する。
```

## 5.1.1. (Option) 複数のWeb画面を一度に表示

複数のWeb画面を一度に表示させる際には、以下の様なIssueを作成して、GitHub Copilot Coding Agentに作業をしてもらいます。

```text
以下のアプリケーションの画面を一度に見る事ができる、[生産調整アプリケーション]を作成する

# 作成フォルダ
## 作成フォルダ
- `{app/フォルダ名}`


# 技術仕様
- 参照されるアプリケーション
  - [生産調整エージェント]
    - フォルダー名: adjustment-agent
  - [KPIモニタリングアプリケーション]
    - フォルダー名: kpi-monitoring-app
- HTML5のみで、それぞれの画面を参照する。独自の画面は作らない
- 画面上部にアプリケーションの一覧名が表示されているタブを作成してください。タブを切り替えると画面の下に、そのアプリケーションが表示されるようにしてください。
- 各アプリケーション参照のURLは、ルートからの絶対パスで指定をしてください。
- Azure Static Web Appsにデプロイできるようにする
- 現在あるすべてのGitHub Actionsは削除する

## 注意事項
- 機能の概要説明やアプリケーションの起動手順を日本語で`/README.md`に追記する。
```

## 5.1.2. (Option) マルチエージェントのグループチャットのサンプル

マルチエージェントのグループチャットのサンプルです。

```text
[KPIモニタリングアプリケーション]と連携して、AIエージェントが生産の変更が可能かどうかを議論して、その議論の経過状況を確認できる画面を作成してください。

# 作成フォルダー
- app/adjustment-agent

# 技術仕様
- デモ用。サンプルデータを作成して、それを使う
- HTML5のみ
- 画面はチャットの形式
- アクターとしてAIエージェントがグループチャットをする。JP工場エージェント、US工場エージェント、販売総合管理エージェント、販売ローカル管理エージェント、畠山さん(人)、榎並さん(人)
  - 工場エージェントは、生産の調整が可能かどうかを現在の生産実績と、生産能力をもとにコメントする
  - 販売エージェントは、店舗での売り上げをもとにしてコメントする
  - 人は、工場と販売のエージェントの会話に割り込んで、人らしい生産量の調整をする
- 生産量の調整が必要なビジネス上の理由
  - JPで梅雨が通常より長く続いており、アイスAが昨年より需要下振れが予想され、スナックBが売られている
  - JP向けにスナックBを生産していた工場Aは増産枠がなく工場振替生産が必要
  - JPのアイスA の販売店では工場Dのライン連続生産を担保できないため、他事業間での調整が必要
- 画面に変更調整の指示をするというボタンを追加。そのボタンを押したら次の処理を実行
- その後、実行計画を作成する。実行計画は、画面に動的に作成したステップを順番に実行していく
- そのボタンを押したら、複数のエージェントが自分がどのデータを変更したらいいのかを画面でコメントする
- 調整後に、調整結果の要約を作成して画面に表示する

## 注意事項
- 機能の概要説明やアプリケーションの起動手順を日本語で`/README.md`に追記する。
```

## 5.2. 妥当性チェック

実施後のPull Requestの中で、`@copilot`で指定して、別タスクとしてチェックを行ってもらうのがおススメです。

```text
実行計画で作成した手順が全て完了した後で、妥当性チェックを行ってください。その際には、作成された全てが高精度に分析し、目的に整合しているかを検証してください。
もし改善点がある場合は、どのように改善すれば正しい回答が得られるかを論理的かつプロフェッショナルとして考えてください。
最初にこのタスクに取り組むべきポイントについて、3～7項目程度の簡潔なチェックリストを作成してください。このステップでは各項目は概念レベルでまとめ、実装詳細には踏み込みません。
その後、作成したチェックリストを参考にして、正しい回答を得るためのに考えた内容をプロンプトに反映して再度実行してください。
```

# 6. データ

> [!WARNING]
> 作業中です。

それぞれのエンティティの適切なデータの保存を行います。Microsoft Azureの中で最適なサービスの候補を作成します。
Microsoft LearnのMCP Serverを参照します。

## 6.1. データサービスの選定

GitHub Copilot でもいいですし。Microsoft 365 Copilot Chatでもいいかと思います。

ここではCloud利用に最適な、Polyglot Persistenceのアーキテクチャを採用します。

```text
全てのエンティティの保存先のMicrosoft Azureのサービスを決定します。ユースケースを分析・解析して、{実行プラン}を必ず参照して、エンティティ毎に、データをどのMicrosoft Azureのサービスを使用すべきかを決定してください。なぜ、そのMicrosoft Azureのサービスにしたのかの具体的で説得力のある説明もしてください。

Microsoft Azureのサービスやアーキテクチャについては、以下のMCP Serverから得られる情報も参考にしてください。

# MCP Server
- MicrosoftDocs

# 対象エンティティ
- docs/uc-01-entities.md

# ユースケース
- docs/uc-01-usercase.md

# 実行プラン
- Polyglot Persistenceのアーキテクチャを採用します
- Polyglot Persistence（ポリグロット・パーシステンス）とは、**アプリケーションの異なる部分に最適なデータストアを選択して使い分けるアーキテクチャ**です。これにより、性能、スケーラビリティ、開発効率などを最適化できます。

以下に、Polyglot Persistenceを設計する際の**詳細な手順**をステップバイステップで解説します。

## 1. 要件の整理とデータの分類

まずは、アプリケーション全体の要件を整理し、扱うデータを以下の観点で分類します：

- **データの性質**：構造化／非構造化、リレーショナル／ドキュメント／グラフなど
- **アクセスパターン**：読み取り中心／書き込み中心／頻繁な更新
- **一貫性の要求**：強い整合性／最終的整合性
- **スケーラビリティ**：水平スケーリングが必要か
- **トランザクションの必要性**：ACID特性が必要か

## 2. データストアの選定

分類したデータごとに、最適なデータストアを選定します。以下は代表的な選択肢です：

| データの種類 | 推奨データストア | 用途例 |
|--------------|------------------|--------|
| リレーショナル | SQL Database PostgreSQL, MySQL | ユーザー情報、トランザクション |
| ドキュメント型 | Azure Cosmos DB | 商品カタログ、ブログ記事 |
| キー・バリュー型 | Redis, Azure Table | キャッシュ、セッション管理 |
| グラフ型 | Neo4j, Azure Cosmos DB | ソーシャルネットワーク、推薦システム |
| 時系列 | InfluxDB, TimescaleDB | IoTデータ、ログ |
| 検索エンジン | Azure AI Search | フルテキスト検索、ログ分析 |

## 3. データモデルの設計

各データストアに対して、以下を設計します：

- スキーマ（必要に応じて）
- インデックス
- リレーション（または参照）
- データの正規化／非正規化の方針

---

## 4. データの整合性と同期戦略

複数のデータストアを使う場合、整合性の確保が重要です。以下の戦略を検討します：

- **イベントソーシング**：変更をイベントとして記録し、各ストアに反映
- **CDC（Change Data Capture）**：変更を検知して他のストアに反映
- **デュアルライト**：アプリケーションが複数のストアに同時に書き込む（要注意）

## 5. ドキュメントとナレッジ共有

- 各データストアの用途と設計理由を明記
- 開発者向けのガイドライン整備
- 運用手順書の作成
```


データをAzure Cosmos DBへ保存をします。

## 6.2. Azure Cosmos DBの作成

Azure Portalから、Azure Cosmos DBを作成します。NoSQL APIを選択してください。
Serverlessプランを選択するのがおススメです。

クイックスタート: Azure portal を使用して Azure Cosmos DB for NoSQL アカウントを作成する

https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/quickstart-portal

> [!WARNING]
> 作業中です。


# 7. REST API 作成

Azure Functionsを使う場合は、事前にMicrosoft Learnの**MCP Server**を参照できるようであれば、設定を行うことを強くお勧めします。

Github Copilot Coding Agentに**API**のプロトタイプを作成してもらいます。ただし、Azure FunctionsのSDKのコードは不正確なことが多いです。
ひな形まで作ってもらって。
そのあとは、Visual Studio Codeなどで、GitHub Copilot for Azureを使って、実装を進めます。

終了後は、Visual Studio Codeで、**自分で実行確認をする**ことを強くお勧めします。GitHub Codespaceだと、GitHub Copilotで幾つか使えるモデルが少なかったり、SDKのインストールが追加で必要だったりするので、開発を継続することを考えると、**自分のPCやMacのVisual Studio Code**での開発・テストの実施をお勧めします。

Azure Functions でサポートされている言語:
https://learn.microsoft.com/ja-jp/azure/azure-functions/supported-languages?tabs=isolated-process%2Cv4&pivots=programming-language-csharp

## 7.1. 要求定義のドキュメントで定義したAPIからの作成

画面内の処理について、以下のドキュメントを作成済みの場合は、そちらを優先します。このPromptにAPI部分のみを記載して、GitHub Copilot Coding Agentに作業をしてもらいます。

[マッピング表](Documentation-and-design.md#step-35-マッピング表の作成)

[マイクロサービスの定義書](Documentation-and-design.md#step42-マイクロサービスの作成)

```text
{マイクロサービスの定義書}を参考にして、マクロサービスのREST APIを、{作成フォルダー}に作成してください。

# マイクロサービス定義
{マイクロサービス定書の文字列}

# 作成フォルダー
- api/{Service名}

# 技術仕様
- Azure Functions v4
- C#
- .NET9.0
- Trigger: HTTP
- Bind: inもoutもHTTP

## 注意事項
- このREST APIは、{ユースケース}の一部分となります。
  - docs/UC-{001}.md
- {技術仕様}の詳細については、以下のMCP Serverを使って必要な情報を入手してください。
  - MicrosoftDocs
- 機能の概要説明やアプリケーションの起動手順を日本語で`/README.md`に追記する。
```

Coding Agentの作業が終了するまで待ちます。終了後のbranchは**削除せずに**残しておいてください**。後で、Visual Studio Codeでの開発に使います。

## 7.2. Azure Functionsのアカウントから、Azure Cosmos DBのNoSQL APIへ接続するための
認証・認可設定 - マネージドIDの設定

Azure Functionsから、Azure Cosmos DBへの認証を、マネージドIDを使って行います。

チュートリアル: マネージ ID と SQL バインドを使用して Azure SQL に関数アプリを接続する:

https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-identity-access-azure-sql-with-managed-identity

- このドキュメントは、Azure SQL Databaseを使っていますが、Azure Cosmos DBのNoSQL APIでも同様の手順で設定が可能です。


Azure Functions 2.x 以降での Azure Cosmos DB のトリガー:

https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger?tabs=python-v2%2Cisolated-process%2Cextensionv4%2Cnodejs-v4&pivots=programming-language-csharp#identity-based-connections



## 7.3. Azure Comsmos DBへのデータ登録処理の実装

Azure FunctionsのREST APIの中に、Azure Cosmos DBへデータを登録する処理を実装します。

GitHub Copilot Coding AgentのIssueです。

```text
Azure FunctionsのREST APIの中に、Azure Cosmos DBのNoSQL APIへデータを登録する処理を実装してください。

# Applicationの場所
- api/{api-name}

# タスク
- 既存のコードの中のデータモデルで定義されているデータ構造を参照します。Azure Cosmos DBのNoSQL APIのドキュメントを参照して、データ登録の処理を実装してください。
- 適切なデータベース、コンテナの作成もしてください。
- 既存のサンプルデータ作成の処理はコメントアウトしてください。

# Azure Cosmos DBのNoSQL APIのURI
- {Azure Cosmos DBのNoSQL APIのURIをここに貼り付ける}

# 参考ドキュメント:
- https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/quickstart-dotnet
```

## 7.4. Azure Functionsへデプロイ

REST APIのエンドポイント(FQDN)を作るために、Azure Functionsへデプロイをします。**Visual Studio Code**から行うのが簡単です。

- Visual Studio CodeやGitHub Desktopなどを使って、Coding Agentが作成したコードをローカルにクローンします。
- Visual Studio Codeで、Azure Functions Toolsなどを使って、ローカルでの動作確認をします。

クイックスタート: Visual Studio Code を使用して Azure に C# 関数を作成する:

https://learn.microsoft.com/ja-jp/azure/azure-functions/create-first-function-vs-code-csharp


開発言語に応じて、周辺からドキュメントを探してみてください。

## 7.5. Azure上で動作しているAPIの一覧取得

Azure CLIを使用して、Azure上で動作しているAPIの一覧を取得します。実行場所は、**Visual Studio Code**の**ターミナル**がおススメです。

```cmd
az functionapp function list --name <Azure Functionsのインスタンス名> --resource-group <Azure Functionsのリソースグループ名> --query "[].{Name:name, Endpoint:invokeUrlTemplate}" --output table > docs/functions-list.md
```
先に作成したAPIのURLを取得して、**テキストファイル**に出力します。ここでは`functions-list.md`ファイルにしています。複数回実施されても問題がないように、ファイル名はサービス名を付けるなど一意になるようにしてください。

このテキストファイルは、マッピングファイルに反映されたら、削除しても構いません。

## 7.5.1. Azure FunctionsにデプロイされたURLのドキュメントへの記載


マッピング表のファイルと取得結果のファイルの双方を参照させて、マイクロサービスの一覧に追記します。


```text
詳細マッピング表のSCR-02の当該API IDのエンドポイントを、`docs/kpi-cat-url.txt`の当該EndPointで置き換えてください。
```

正しく反映されたら、GitHubのリポジトリにPushします。


# 8. HTMLの画面とREST APIの連携
GitHub Copilot Coding Agentに、HTMLの画面とAPIの連携を作成してもらいます。


## 8.1. REST APIの呼び出し

> [!WARNING]
> 作業中です。


タスクとしてGitHubのIssueとして管理したい事もあり。GitHub Copilot Coding AgentにAPIの呼び出しを作成してもらいます。

```text
画面を制御するコード内でREST APIのエンドポイント呼び出しを実装します。現状はスタブ呼び出しとなっています。
スタブ呼び出しから、REST APIのエンドポイントを呼び出す実装に変更してください。

# 対象コードファイル
- `app/js/api.js`

# マッピング情報
- `docs/uc-01_mapping.md`
  - エンドポイントURL: Azure FunctionsのHTTPエンドポイントのURL

# 置き換え対象画面と機能・サービス
- 画面ID: `SCR-02`
- SoT: `KPI-01`

編集は対象ファイル内に限定し、リポジトリのコーディングスタイルに従い、レビューしやすい差分を作成してください。
```



## 9. Azure への展開

> [!WARNING]
> 作業中です。

Azure Developer CLI (azd)を使用して、作成したコードをAzureにデプロイするスクリプトを作成します。

どのフォルダーのアプリを、Azure上のどのサービスにデプロイするかを明示します。

Microsoft LearnのMCP Serverを参照するように指摘もします。 

```text
指定したアプリケーションフォルダ内のファイルを、指定したMicrosoft Azureの各サービス（例：Azure Static Web Apps）にデプロイするためのAzure Developer CLIコマンドを生成してください。コマンドの実行手順も日本語で、`README.md`ファイルに作成してください。

**MicrosoftDocs**のMCP Serverを**必ず**使って、Azure Developer CLIの仕様を注意深く確認してください。Microsoft Azureの各サービスの仕様も、注意深く確認をしてください。

# 対象アプリケーションのデプロイ設定
- フォルダ: {/}
  - 作成するAzureサービス: {Azure Static Web App}

```