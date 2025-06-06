# アプリケーションのプロトタイプ開発 (GitHub Copilot Coding Agent / GitHub Copilot for Azure)

要求定義の作成をしたドキュメントを入力データとして、プロトタイプの開発を行っていきます。

# プロトタイプの位置づけ

ここでは、ユーザーを早期に巻き込むフィードバックループを目的に以下の順番で進めていきます。

# ツール
GitHub Copilot の **Coding Agent**のIssueからCoding Agentに作業をしてもらう前提です。

https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/


- 現時点でプレビューです。プロダクション環境での利用には十二分に注意をしてください。Pull Requestをマージするかどうかは、**人**の判断ですので!
- AzureとCDで連携した後は、CopilotがPRを実行している際にGitHub Actionsでのジョブ実行を行います。その際に私たち人によるApprovalが必要です。ただ、そのGitHub Actionsのジョブがエラーになることがあります。

![Job Errorの例](/Software%20Engineer/プロトタイプwithAgents/images/image.png)

- その際には、PRのコメントに以下の様な指示をして、GitHub Copilotに修正をさせるのも手です。

```cmd
reviewのチェックで、github actionsのジョブがエラーになりました。原因をリストアップして、解決策を考えて、修正をしてください。
@copilot 
```


Microsoft Azure のSDKを使う場合は、GitHub Copilot for Azure を使います。

https://learn.microsoft.com/ja-jp/azure/developer/github-copilot-azure/introduction


# 1. 業務要件などビジネス面のドキュメントの整備

こちらのドキュメントを参考にしてください。

ここでおススメのツールは上記とは**別**で、Microsoft 365 Copilot Researcherです。

[要求定義の作成](/Software%20Engineer/プロトタイプwithAgents/要求定義作成.md)


# 2. UI 作成

**サンプルデータ**と、**機能要件のドキュメント**を添付します。

GitHub Copilot Coding AgentのIssueとして使います。Copilot君にIssueをAssignして、Issueのコメントに以下の様な内容を書いてください。

```cmd
Webアプリケーションのプロトタイプを作成してください。

添付のドキュメントはソフトウェアの機能要件です。この中の{機能要件の中から1つ}だけを作成します。

{機能要件ドキュメント}

# 範囲
- {機能要件の中から1つ}
- 機能ID（Requirement ID）: {あれば}

# 作成場所
- フォルダー: app

# 技術仕様
- HTML5のみ
- JavaScript

# データ
- 以下のファイルを参照する

{サンプルデータやデータモデルのドキュメント

# ノート
- README.md は、日本語で作成する
```

完成したら、Azure Static Web Appsにデプロイをします。これはAzureのPortalから行うのが簡単です。プロトタイプだという事もありまして。

クイック スタート: 静的 Web アプリを初めてビルドする:

https://learn.microsoft.com/ja-jp/azure/static-web-apps/get-started-portal?tabs=vanilla-javascript&pivots=github

- 最初の[リポジトリを作成する]は**不要**です。私たちはすでにGitHubのリポジトリを持っていますので。

# 3. API 作成

Github Copilot Coding Agentに**API**のプロトタイプを作成してもらいます。ただし、Azure FunctionsのSDKのコードは不正確なことが多いです。
ひな形まで作ってもらって。
そのあとは、Visual Studio Codeなどで、GitHub Copilot for Azureを使って、実装を進めます。

GitHub Copilot Coding AgentのIssueです。

終了後は、Visual Studio Codeで、**自分で実行確認をする**ことを強くお勧めします。GitHub Codespaceだと、GitHub Copilotで幾つか使えるモデルが少なかったり、SDKのインストールが追加で必要だったりするので、開発を継続することを考えると、**自分のPCやMacのVisual Studio Code**での開発・テストの実施をお勧めします。

```cmd
Azure Functionsで動作するREST APIのアプリケーションのプロトタイプを作成してください。
このAPIは以下のアプリケーションの中のJavaScriptのコードからREST APIで呼び出されます。

# 作成フォルダー
- api

# 呼び出し元のWebアプリケーション
- アプリケーション名: app
- JavaScriptのファイルの場所: app/js
	- それぞれの.jsファイルから、新規に作成するAPIを呼び出す

# 技術仕様
- Azure Functions v4
- C#
- .NET9.0
- Trigger: HTTP / inもoutも

# タスク
- APIが完成してAzure Functionsにデプロイをした後で、Webアプリケーション側のコードの変更を行う
- 単体で呼び出せるようにする
- 日本語の詳細なセットアップ手順書を作成する。手順書は作成フォルダーの中に作成する

# APIに実装する機能
- knowledgeshare-app/jsの関数の中で、HTMLの画面とやり取りするところは除外する
- それ以外のコードを、全てAPIとして実装する
- サンプルデータは、全てデータ管理のAPIの中に実装する
```


完成したら、Azure Functionsにデプロイをします。Visual Studio Codeから行うのが簡単です。

クイックスタート: Visual Studio Code を使用して Azure に C# 関数を作成する:

https://learn.microsoft.com/ja-jp/azure/azure-functions/create-first-function-vs-code-csharp

開発言語に応じて、周辺からドキュメントを探してみてください。

# 4. HTMLの画面とAPIの連携
GitHub Copilot Coding Agentに、HTMLの画面とAPIの連携を作成してもらいます。

## 4.1. APIの一覧取得

Visual Studio Code の **GitHub Copilot for Azure**を使って、APIの一覧取得のコードを作成します。
```
@azure Azure Functionsで動作しているREST APIの一覧を作成します。API名とURLをリストアップしてください。
```

## 2. APIの呼び出し

タスクとしてGitHubのIssueとして管理したい事もあり。GitHub Copilot Coding AgentにAPIの呼び出しを作成してもらいます。

```cmd
既存のJavaScriptのコードの中から、Azure Functions上で動作しているREST APIを呼び出すように修正をしてください。

# 変更対象
- Webアプリケーションの場所: app
  - JavaScriptのファイルの場所: app/js

# 関数の分類の例
## フロントエンド（Front）で主に実装・担当する関数

1. **イベントハンドラー**
   - 画面上のユーザー操作（クリック、入力、送信など）に反応する関数
   - 例: `onClickButton()`, `onInputChange()`

2. **UI操作・DOM操作**
   - 画面の表示・非表示、要素の追加・削除・更新など
   - 例: `showModal()`, `updateListView()`

3. **バリデーション（クライアント側）**
   - 入力値の形式チェックや必須項目の確認など
   - 例: `validateEmailFormat()`, `checkRequiredFields()`

4. **状態管理（クライアント側）**
   - 画面の状態や一時的なデータの保持
   - 例: `setCurrentTab()`, `updateLocalState()`

5. **初期化・セットアップ**
   - ページロード時の初期化処理
   - 例: `initPage()`, `loadInitialView()`

6. **エラーハンドリング（UI通知）**
   - エラー発生時の画面表示やユーザー通知
   - 例: `showErrorMessage()`

7. **ユーティリティ（フロント専用）**
   - 画面表示用のフォーマット変換など
   - 例: `formatDisplayDate()`

## バックエンド（Backend）で主に実装・担当する関数（将来REST API化する候補）

1. **データアクセス・データ取得**
   - データベースや外部サービスとのやりとり
   - 例: `fetchUserList()`, `saveOrderData()`

2. **データ加工・変換（ビジネスロジック）**
   - データの集計、フィルタリング、計算など
   - 例: `calculateTotalAmount()`, `filterActiveUsers()`

3. **バリデーション（サーバー側）**
   - セキュリティや整合性のための入力チェック
   - 例: `validateUserInputOnServer()`

4. **状態管理（サーバー側）**
   - ユーザーセッションやアプリ全体の状態管理
   - 例: `updateUserSession()`

5. **API通信**
   - REST APIとして外部公開する関数
   - 例: `getUserDataAPI()`, `postOrderAPI()`

6. **エラーハンドリング（サーバー側）**
   - サーバーでのエラー処理やログ記録
   - 例: `logError()`, `returnErrorResponse()`

7. **ユーティリティ（サーバー専用）**
   - サーバー側でのみ必要な共通処理
   - 例: `hashPassword()`, `generateToken()`


それぞれの.jsファイルから、最適なAzure Functions上のAPIを呼び出すように修正をしてください。

# Azure Functions REST API 仕様書
{4.1. APIの一覧取得で取得したAPIの仕様書をここに貼り付ける}
```
# 5. データを永続保存

データをAzure Cosmos DBへ保存をします。


Visual Studio Code の **GitHub Copilot for Azure**を使って、APIで使用しているデータをバックアップします。

```cmd
@azure Azure Cosmos DBにデータを移行させます。このAPIの中のデータを全て削除してもいいように、全てのデータをテキストファイルに出力してください。既存のコードは一切変更しないでください。
```

