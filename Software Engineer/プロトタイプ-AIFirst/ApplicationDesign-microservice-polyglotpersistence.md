# アプリケーション設計 - Microservice + Polyglot Persistence

ソフトウェアエンジニアがアプリケーション開発に着手するための入力情報となりえるドキュメントを作成します。
ユースケースは複数の候補から、1つずつ選択して、アプリケーション設計を進めていきます。

## ツール
GitHub CopilotはSoftware Engineeringについては比較的良いOutputを出してくれます。
ただし、GitHub CopilotのAgentは、デフォルトでFirewallの設定があり、MCP経由でないと外部の情報を参照ができません。
その点では、Microsoft 365 CopilotのGPT-5でも良いかもしれません。

GitHub Copilotには複数のAgentがあります。ご自分の好みのものを選択してください。

https://docs.github.com/ja/copilot/get-started/features

- GitHub Copilot Agent Mode
Visual Studio XなどのIDEに組み込まれたCopilotです。モデルを複数から選択できるメリットがあります。

- GitHub Copilot Coding Agent
Coding Agentの場合はDeep Reserch系の動作をすることもあって、若干時間を要しますが以下のメリットもあります。

  - GitHubのIssueとしてトラックできる
  - Issue発効後は、手元のPCなどで別作業がしやすい
  - バッチ的に複数のファイル作成がやりやすい

> [!NOTE]
> 作成結果は、GitHubのRepositryにドキュメントとして保存しておくことをお勧めします。


# Step. 1. マイクロサービスアプリケーション定義書の作成

ユースケースの情報があれば、画面やサービス、データなど各種のモデリングが可能です。
ここからはマイクロサービスでの設計の進め方をある程度踏襲して、具体的な関連情報を文章化していきます。

## Step. 1.1. ドメイン分析の実施

ここでは作成されたユースケースから、**1つだけ選択**して、業務上のドメイン分析を行います。

- 使用するカスタムエージェント
  - Arch-micro-DomainAnalytics

```text
# タスク
ユースケースからDDD観点でドメインモデリングを行い、Bounded Contextとドメインイベントを特定して docs/usecase/{ユースケースID}/domain-analytics.md を作成する

# 入力
- ユースケースID: {ユースケースID}
- 主文書: docs/usecase/{ユースケースID}/usecase-description.md

# 出力（必須）
- docs/usecase/{ユースケースID}/domain-analytics.md
```

## Step. 1.2. マイクロサービスの一覧の抽出

- 使用するカスタムエージェント
  - Arch-micro-ServiceIdentify

```text
# タスク
ドメイン分析（docs/usecase/{ユースケースID}）からマイクロサービス候補を抽出し、service-list.md と Mermaid コンテキストマップを作成する

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`
- `docs/usecase/{ユースケースID}/domain-analytics.md`

# 出力（必須）
- `docs/usecase/{ユースケースID}/services/service-list.md`
   - 形式：このファイル内に **(A)サマリ表 → (B)サービス候補詳細 → (C)Mermaidコンテキストマップ** の順で記載する。
```

# Step. 2. データモデル作成

- 使用するカスタムエージェント
  - Arch-DataModeling

```text
# タスク
ユースケース文書から全エンティティを抽出し、サービス境界と所有権を明確にしたデータモデル（Mermaid）と、日本語のサンプルデータ(JSON)を生成します

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`
- `docs/usecase/{ユースケースID}/domain-analytics.md`
- `docs/usecase/{ユースケースID}/services/service-list.md`

# 出力（必須）
## A) モデリングドキュメント
-  `docs/usecase/{ユースケースID}/data-model.md`

## B) サンプルデータ
- `data/{ユースケースID}/sample-data.json`
```

# Step. 3. 画面一覧と遷移図の作成

画面の設計に入ります。

- 使用するカスタムエージェント
  - Arch-UI-List

```text
# タスク
ユースケースの画面一覧（表）と画面遷移図（Mermaid flowchart）を作成し、ポータル（タブ）から各画面へ遷移できる構造を設計する

# 入力
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`（最優先）
- `docs/usecase/{ユースケースID}/services/service-list.md`（機能/責務の補助）
- `docs/usecase/{ユースケースID}/data-model.md`（表示/入力項目の補助）

# 出力（必須）
- `docs/usecase/{ユースケースID}/screen/screen-list.md`
```

# Step.4. サービスカタログ表の作成

このドキュメントを最終的に作りたかったのです!
画面とサービスとデータ。それぞれに識別のためのIDを付与して、今後、個々に仕様書として作成するドキュメントを紐づけます。

作業手順の中で**機能やAPI**の概要を作成している点をお忘れなく。

- カスタムエージェント
  - Arch-micro-ServiceCatalog

```text
# タスク
ユースケースの画面→機能→処理/API→SoTデータをマッピングしたサービスカタログを docs/usecase/<ユースケースID>/service-catalog.md に生成する

# 入力
- ユースケースID: {ユースケースID}
- 参照ドキュメント（存在しない場合は search で同等ファイルを特定し、差分を前提に明記）
  - `docs/usecase/{ユースケースID}/usecase-description.md`
  - `docs/usecase/{ユースケースID}/services/service-list.md`
  - `docs/usecase/{ユースケースID}/data-model.md`
  - `docs/usecase/{ユースケースID}/screen/screen-list.md`

# 出力（必須）
- `docs/usecase/{ユースケースID}/service-catalog.md`
```

# Step.5. 生成AIに最適化した各コンポーネントプロンプトの作成

> [!NOTE]
> これでもある程度は動きますが。もっとPromptとして最適化できると思います...

Step 3. で作成したユースケースの情報をもとに、生成AIに最適化したプロンプトを作成します。

## Step.5.1. 画面定義書の作成

画面定義書は、既存のドキュメントを強く意識している「人」が理解しやすいであろう構造化情報として作成されています。

- カスタムエージェント
  - Arch-UI-List

```text
# タスク
ユースケースの画面一覧（表）と画面遷移図（Mermaid flowchart）を作成し、ポータル（タブ）から各画面へ遷移できる構造を設計する

# 入力（必読）
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-description.md`（最優先）
- `docs/usecase/{ユースケースID}/services/service-list.md`（機能/責務の補助）
- `docs/usecase/{ユースケースID}/data-model.md`（表示/入力項目の補助）

# 出力（必須）
- `docs/usecase/{ユースケースID}/screen/screen-list.md`
```

## Step. 5.2. マイクロサービス定義書の作成

サービスの候補から、1つを選んで、マイクロサービス定義書に準拠したドキュメントを作成します。

- カスタムエージェント
  - Arch_Micro_Service_Detail

```text
# タスク
ユースケース配下の全サービスについて、マイクロサービス詳細仕様（API/イベント/データ所有/セキュリティ/運用）をテンプレに沿って作成する

# 入力（必読）
## ユースケースID
- {ユースケースID}

## 参考ドキュメント（必ず最初に読む）
- `docs/usecase/{ユースケースID}/usecase-description.md`
- `docs/usecase/{ユースケースID}/services/service-list.md`
- `docs/usecase/{ユースケースID}/service-catalog.md`
- `docs/usecase/{ユースケースID}/data-model.md`
- `data/{ユースケースID}/sample-data.json`（※値の転記は禁止。要約のみ）

# 成果物
## サービス詳細仕様（サービスごと。必ず作成する）
- `docs/usecase/{ユースケースID}/services/{サービスID}-{サービス名slug}-description.md`
  - slug規約：小文字、空白は `-`、英数と `-` のみ（不明なら `{サービスID}-description.md` でも可）
  - 本文：docs/templates/microservice-definition.md をコピーし、サービス情報で埋める（推測禁止、TBD＋根拠）
```
