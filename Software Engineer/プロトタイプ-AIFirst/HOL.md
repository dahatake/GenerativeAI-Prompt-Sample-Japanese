# ハンズオン

特徴的なステップのPromptを行います。

# 環境準備

ここでは、2つのDeep Research型のCopilotを使用します。安心・安全に業務でも使えるようにするためです。

- Business Engineering
  - Microsoft 365 Copilot: **リサーチツール**
    - Microsoft 365 のライセンスに加えて、Microsoft 365 Copilotの追加ライセンスが必要です。
        https://www.microsoft.com/ja-jp/microsoft-365-copilot/pricing
    - 自分のアカウントで、Microsoft 365 Copilot Chatの画面にリサーチツールが表示されない場合は、**管理者に問い合わせて**有効化してもらう必要があります。
        https://learn.microsoft.com/ja-jp/copilot/agents?toc=%2Fcopilot%2Fmicrosoft-365%2Ftoc.json&bc=%2Fcopilot%2Fmicrosoft-365%2Fbreadcrumb%2Ftoc.json
 
 - Software Engineering
   - GitHub Copilot **Coding agent**
     - GitHub Copilot Pro、GitHub Copilot Pro+、GitHub Copilot Business、GitHub Copilot Enterprise プランが必要です。
        https://docs.github.com/ja/copilot/concepts/agents/coding-agent/about-coding-agent
    - 自分のアカウントでGitHubにログインして、Copilotが表示されない場合は、**管理者に問い合わせて**有効化してもらう必要があります。

- GitHub Desktop か Visual Studio Code

  どちらでも構いません。使い慣れたツールを使ってください。

  `GitHub Desktop`は、GitHubのリポジトリーとローカルPCのフォルダーを同期するために使用します。以下からダウンロードしてインストールしてください。

    https://github.com/apps/desktop

  `Visual Studio Code`などのコードエディタでも、GitHubリポジトリーとローカルPCのフォルダーを同期できます。その場合は、`GitHub拡張機能`をインストールしてください。

# バッチとインタラクティブの相互処理

大量にスケールさせるバッチ型のPromptと。深く探索を行っていくインタラクティブ型のPromptを組み合わせて使用します。

ここで行う分量であれば、何を使っても出来ますが。以下でツールを分けてくさい。

- バッチ = GitHub Copilot Coding agent
- インタラクティブ = GitHub Copilot Agent Mode (Plan Mode)


## 1. 複数画面作成 - バッチ型

目的：このプロンプトをGitHub Copilot のAgent Modeに投入します。2画面HTMLと共通JSを生成するように促します。


```text
# 目的
GitHub Copilotを活用して、プロンプトアートサンプルのHTMLおよびJavaScriptプログラムを生成し、さらにそれをバッチ型・インタラクティブ型のプロンプトでプログラム修正・バグ発見・修正提案まで実行するプロセスを設計してください。

## 作業フロー
1.要件整理
  - HTMLは二画面（Builder画面／Analyzer画面）。
  - 共通JSで両画面のロジックを共有。
  - 生成AIに使うためのプロンプト一式を用意（作成・図式化・バグ特定＆修正提案）。
  - 意図的なバグをコードに埋め込む（学習用）。
2. 設計方針
  - Builder画面：テキスト＋選択UIから「プロンプト」を作り、Canvasに簡易描画、LocalStorageへ保存。
  - Analyzer画面：保存済みプロンプトを読み込み、リスト表示・分析出力（ただし意図的バグで動かない箇所あり）。
  - JSは1ファイル（app.js）でモジュール化。
  - バグはAnalyzer側に寄せて、Builderは概ね動くようにして学習しやすくする。
3.意図的バグの設置
  - バグ#1（Storageキー不一致）：保存は prompts、読込は promptList を参照 → Analyzerに何も出ない。
  - バグ#2（ボタンID不一致）：Analyzer側のイベント登録が analyzeButton を参照、HTMLは analyzeBtn → クリック反応なし。
4. プロンプト設計
  - プログラム作成プロンプト：Copilotに仕様通りの2画面＋共通JSを生成させる1本。
  - バッチ型プロンプト：大量の成果物（テストケース、課題票、ログ設計、図式）を一括生成。
  - インタラクティブ①：コードの図式化（Mermaid）＋日本語の構造説明。
  - インタラクティブ②：バグ報告文字列から、原因特定・コード位置・修正案（パッチ）・再現＆検証手順を提案。
5. 提供＆利用手順
  - まずサンプルコードを配布・動作確認。
  - 次にインタラクティブ①で構造理解、②でバグ修正演習。
  - バッチ型で大量成果物を生成し、ワークショップ成果にまとめる。

もしもプログラム自体や分析対象コードが不完全・不足している場合は、その旨を明記し、適切なエラーメッセージと共に分析・修正プロンプトを出してください。

- 各コード例は必ずMarkdownのコードブロック形式で出力してください。
- バッチ型とインタラクティブ型は必ずそれぞれ別の説明文とプロンプト例を含めてください。
- バグ報告・修正案はリスト形式で具体的に出してください。
- 分析対象が存在しない・不完全な場合の出力サンプルも含めてください。

### Output Verbosity
- 各説明やプロンプト例は1～2文・2パラグラフ程度、長くて6行以内とし、簡潔にまとめてください。
- 出力は必要十分な範囲で、具体性・構造の明瞭さを重視してください。
- 完全かつ実用的な内容を、指定の長さ内で優先的に返答してください。
- ユーザーが短文で追加指示をした場合も、必要な内容が過不足なく揃うよう十分に記述し、途中で回答を省略しないでください。
- 丁寧さや気配り表現が増えても、文章自体の長さは拡張しないでください（「Do not increase length to restate politeness.」）。

```

# 2. AI Firstでの大量バッチ処理

## 1. ビジネス要件の作成: Microsoft 365 Copilot

- Microsoft 365 Copilot Chatにログインします。

  https://m365.cloud.microsoft/chat

- メモ帳などのテキストエディタを開きます。Promptは投入前にテキストエディタで編集・保存しておくのが便利です。

- 以下のPromptの内容をコピーして、テキストエディタに貼り付けます。
  [Prompt](Business-Documentation.md#step-1-事業分析ドキュメントの作成)

- `目的`と`ガイドライン`の間に、以下の内容を追記します。

```text
# サービス企画 

まず「ロイヤルティプログラム」とは、企業がお客様に継続的に自社の商品やサービスを利用してもらうために、購入や利用に応じてポイントや特典を提供する仕組みです。 

【特徴】としては、
1. お客様のロイヤルティ（忠誠心）を高める：リピート利用を促すことで長期的な関係を築く。 
2. 顧客データの蓄積とパーソナライズ：購入履歴や行動データをもとに、お客様ごとに最適な特典を提供できる。
3. ビジネスにおける競争優位性：特典やポイント制度によって、お客様のロイヤルティを高め、他社との差別化を図ることができる。 

【ペルソナ】としては、たとえば以下のような顧客層を想定できます。 
- よく同じ店舗やブランドを利用する常連客。 
- あるいはポイントや特典に対して敏感な新規顧客。 
- また、定期的にサービスや商品を利用するファミリー層なども考えられます。 

【生成AIの活用】としては、 
- お客様とのやり取りから自然言語処理を使ってパーソナライズした特典を提案する。 
- 音声入力や音声コマンドを使って、少ないスタッフでもスムーズにオペレーションできるようにする。 
- さらに、購入データをもとにAIが次の購買予測を行い、最適なキャンペーンを自動で打つ。
```

- 編集したPromptの内容をMicrosoft 365 Copilot Chatに貼り付けて、実行します。

> [!TIP]
> コーヒーやお茶の時間です。Copilot君の作業終了まで、**5-10分程度**かかります。ですが、**直ぐに**Webブラウザーのタブを新規に開くか、別のインスタンスを起動させて、次のステップに進んでもよいです。

- 実行後には、かなり長い文章が作成されます。文字列の一番最後にある`応答のコピー`ボタンを押して、文章全体をコピーします。その文字列をメモ帳などのテキストエディタに貼り付けて**Markdownのファイル**としてファイル名を`business-requirement.md`として自分のPCに保存します。

## 2. GitHub に新規リポジトリーの作成
GitHubにログインして、新しいリポジトリーを作成します。

- リポジトリー名は任意です。例えば`hve-hol`などとします。
- Visibilityは、**Private** 設定がお勧めです。

## 3. サンプルの要求定義などのドキュメント ファイルのアップロード
このフォルダー以下にある`samples`フォルダーの全てのフォルダーとファイルを、GitHubの新規リポジトリーにアップロードします。

`samples`フォルダーの構造:
```text
samples
 ├── .github/agents           : GitHub CopilotのCustom Agentの定義
 │    ├── Arch-micro-ServiceIdentify.md
 │    ├── Arch-UI-Detail
 │    └── Impl-WebAzure-UICoding
 ├── data/sample-data.json    : サンプルデータ
 ├── docs                     : サンプルの要求定義書や設計書
 │    ├── business-requirement.md
 │    ├── domain-analytics.md
 │    └── ...
 └── .gitignore
```

GitHub DesktopやVisual Studio Codeを使用して、ローカルPCのフォルダーとGitHubリポジトリーを同期してください。

もし、Step.1が完了していたら、`business-requirement.md`は、自分が作成したものに置き換えてください。

## 4. Microsoft Learn MCP Serverの設定

Microsoft Learnから、C#やMicrosoft Azureに関する詳細な情報を取得できるように設定します。


> [!WARNING]
> Microsoft LearnのMCP Serverの利用は、以下の使用条件を慎重に確認してください。
https://learn.microsoft.com/ja-jp/training/support/mcp#requirements

- GitHubで作成したリポジトリーに移動します。
- `Settings`タブを選択します。
- 左側のメニューから、`Copilot` > `Coding agent`を選択します。
- `MCP Conditions`セクションで、以下の文字列を貼り付けます。

```text
{
  "mcpServers": {
    "MicrosoftDocs": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp",
      "tools": ["*"]
    }
  }
}
```

## 5. microservice モデリング

サンプルのファイルを参考にして、以下のPromptをGitHub Copilot Coding agentに投げかけて、microservice モデリングを行います。

- GitHubのリポジトリーに移動します
- `Issue`タブを選択します
- `New issue`ボタンを押して、新しいIssueを作成します
- 各項目に以下の情報を入力します。
    - Title: マイクロサービスのモデリング
    - Add a description: 以下のPromptをコピーして貼り付けます。

    ```text
    {参考ドキュメント}にあるドキュメントを参考にして、マイクロサービスのモデリングを行ってください。モデリングの結果は、{作成ファイル}にMarkdown形式で保存してください。
    
    ## 参考ドキュメント
      - docs/usecase-description.md
      - docs/domain-analytics.md
    
    ## 作成ファイル
      - docs/service-list.md
    ```

- `Assignees`で、**Copilot**を選択します。
- 以下の様に`Custom Agent`の選択ができます。**Arch-micro-ServiceIdentify**を選択します。

  ![Custom Agentの選択](./images/assign-githubcopilot-customagent.jpg)

- 画面下の緑色の`Create`ボタンを押して、Issueを作成します。

> [!TIP]
> コーヒーやお茶の時間です。Copilot君の作業終了まで、**5-10分程度**かかります。ですが、**直ぐに**Webブラウザーのタブを新規に開くか、別のインスタンスを起動させて、次のステップに進んでもよいです。

参考:
https://docs.github.com/ja/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr

- Issueに紐づいている`Pull Request`を表示して作業結果を確認します。**Copilot finished work on behalf of <ユーザー名>**という出力がされていれば、タスクは完了しています。
- Pull Requestの中に`view sessions`というボタンが表示されている場合は、クリックして内容を確認します。**Copilotがどのような作業を行ったか**が、わかります。
- `File changed`タブにて作成・変更・削除されたファイルが確認できます。自分でレビューしてください。
- 大丈夫であれば、`Ready for review`を押してレビューの準備をします。
- マージをします。


## 6. Azureのデータサービスのデザイン

それぞれのMicroserviceのワークロードを考慮したうえでMicrosoft Azureのデータサービスを選定します。

- GitHubで新しいIssueを作成します
- 各項目に以下の情報を入力します。
    - Title: Microsoft Azureのデータサービスの選定
    - Add a description: 以下のPromptをコピーして貼り付けます。

    ```text
    {参考ドキュメント}にあるドキュメントを参考にして、Microsoft Azureで最適なデータサービスを選定してください。分析の結果は、{作成ファイル}にMarkdown形式で保存してください。
    
    ## 参考ドキュメント
      - docs/usecase-description.md
      - docs/data-model.md
      - docs/service-list.md

    ## 作成ファイル
      - docs/AzureServices-data.md
    ```

- `Assignees`で、**Copilot**を選択します。
- `Custom Agent`は、**Impl-WebAzure-DataDesign**を選択します。
- 画面下の緑色の`Create`ボタンを押して、Issueを作成します。
- Pull RequestでのCopilotの作業が完了したら、内容を確認してマージします。

## 7. 画面定義書の作成

一つだけ画面の設計と実装を行います。Step.5あるいはStep.6の実行直後でも構いません。

- GitHubで新しいIssueを作成します
- 各項目に以下の情報を入力します。
    - Title: 画面定義書の作成
    - Add a description: 以下のPromptをコピーして貼り付けます。

    ```text
    {参考ドキュメント}にあるドキュメントを参考にして、{作成画面}で指定している画面定義書を作成してください。画面の中で利用するデータは{サンプルデータファイル}から利用してくさい。画面定義書は、{作成ファイル}にMarkdown形式で保存してください。
    
    ## 作成画面
      - SCR-006-001: ポータル画面

    ## 参考ドキュメント
      - docs/usecase-description.md
      - docs/service-list.md
      - docs/data-model.md

    ## 作成ファイル
      - docs/UI-SCR-006-001.md

    ## サンプルデータファイル
      - data/sample-data.json
    ```

- `Assignees`で、**Copilot**を選択します。
- `Custom Agent`の選択は、**Arch-UI-Detail**を選択します。
- 画面下の緑色の`Create`ボタンを押して、Issueを作成します。
- Pull RequestでのCopilotの作業が完了したら、内容を確認してマージします。

## 8. 画面のコーディング

Step 7 で作成した画面定義書に基づいて、画面のコーディングを行います。

- GitHubで新しいIssueを作成します
- 各項目に以下の情報を入力します。
    - Title: Web画面の実装
    - Add a description: 以下のPromptをコピーして貼り付けます。

    ```text
    {参考ドキュメント}にあるドキュメントを参考にして、{作成画面}で指定しているWeb画面のコードを作成してください。画面の中で利用するデータは{サンプルデータファイル}から利用してくさい。作成したコードは{作成フォルダ}に保存してください。
    
    ## 作成画面
      - docs/UI-SCR-006-001.md

    ## 参考ドキュメント
      - docs/usecase-description.md
      - docs/service-list.md
      - docs/data-model.md

    ## 技術仕様
      - HTML5とJavaScript

    ## 作成フォルダ
      - apps
    ```

- `Assignees`で、**Copilot**を選択します。
- `Custom Agent`の選択は、**Arch-UI-Detail**を選択します。
- 画面下の緑色の`Create`ボタンを押して、Issueを作成します。
- Pull RequestでのCopilotの作業が完了したら、内容を確認してマージします。

## 8. 動作確認

作成した画面は、HTMLのみです。ローカルにダウンロードして、Webブラウザーで表示できます。

それ以外ついては、ドキュメントの作成のみです。GitHub上で内容を確認してください。