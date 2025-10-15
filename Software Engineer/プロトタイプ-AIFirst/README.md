# アプリケーションのプロトタイプ開発 (GitHub Copilot Coding Agent / GitHub Copilot for Azure)

ここでは、ユーザーを早期に巻き込むフィードバックループを目的に以下の順番で進めていきます。

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


# はじめに

Copilot を使用してタスクに取り組むためのベスト プラクティス

https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks


- プロダクション環境での利用には十二分に注意をしてください。Pull Requestをマージするかどうかは、**人**の判断ですので!

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



## Step.2. 要求定義などビジネス面のドキュメントの整備

こちらのドキュメントを参考にしてください。

[要求定義の作成](Documentation.md)

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

- また、結果の精度が低い場合もあります。各Promptの実行後のPull Requestの中で、`@copilot`で指定して、別タスクとしてチェックを行ってもらうのがおススメです。

```text
@copilot
妥当性チェックを行ってください。その際には、作成された全てを高精度に分析し、目的に整合しているかを検証してください。
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
