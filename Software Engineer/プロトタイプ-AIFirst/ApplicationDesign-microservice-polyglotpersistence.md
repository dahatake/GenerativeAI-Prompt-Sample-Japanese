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
  - Arch-Micro-DomainAnalytics

```text
# タスク
ユースケース文書を根拠に、DDD観点でドメイン分析（Bounded Context / ユビキタス言語 / 集約 / ドメインイベント / コンテキストマップ等）を整理し、docs/domain-analytics.md を作成する。

# 入力
- ユースケース文書: `docs/usecase-list.md`

### 2.3 出力（必須）
- `docs/domain-analytics.md`
```

## Step. 1.2. マイクロサービスの一覧の抽出

- 使用するカスタムエージェント
  - Arch-Micro-ServiceIdentify

```text
# タスク
docs/ のドメイン分析からマイクロサービス候補を抽出し、service-list.md（サマリ表＋候補詳細＋Mermaidコンテキストマップ）を作成/更新する。

# 入力
- `docs/usecase-list.md`
- `docs/domain-analytics.md`

# 出力（必須）
- `docs/service-list.md`
  - 構成は必ず以下の順：
    - **A. サマリ（表）**
    - **B. サービス候補詳細（候補ごと）**
    - **C. Mermaid コンテキストマップ（末尾）**
```

# Step. 2. データモデル作成

- 使用するカスタムエージェント
  - Arch-DataModeling

```text
# タスク
ユースケース文書から全エンティティを抽出し、サービス境界と所有権を明確にしたデータモデル（Mermaid）と、日本語のサンプルデータ(JSON)を生成します

# 入力
- `docs/domain-analytics.md`
- `docs/service-list.md`

# 出力（必須）
## A) モデリングドキュメント
- `docs/data-model.md`

### B) サンプルデータ
- 原則：`data/<USECASE_ID>/sample-data.json`
```

# Step. 3. 画面一覧と遷移図の作成

画面の設計に入ります。

- 使用するカスタムエージェント
  - Arch-UI-List

```text
# タスク
docs/ の資料から、ユースケースと画面の関係性のベストプラクティスを示したうえで、アクターの中の「人」毎の画面一覧（表）と画面遷移図（Mermaid）を設計し、screen-list.md と進捗ログを作成・更新する。

# 入力
- 最優先：
  - `docs/service-list.md`（機能/責務の補助）
  - `docs/data-model.md`（表示/入力項目の補助）

- 補助（指定があるときだけ）：
  - ユースケースID: {ユースケースID}
  - `docs/usecase/{ユースケースID}/usecase-detail.md`

# 出力（必須）
- 主要成果物：`docs/screen-list.md`
```

# Step.4. サービスカタログ表の作成

このドキュメントを最終的に作りたかったのです!
画面とサービスとデータ。それぞれに識別のためのIDを付与して、今後、個々に仕様書として作成するドキュメントを紐づけます。

作業手順の中で**機能やAPI**の概要を作成している点をお忘れなく。

- カスタムエージェント
  - Arch-micro-ServiceCatalog

```text
# タスク
既存ドキュメントを根拠に、画面→機能→処理/API→SoTデータをマッピングしたサービスカタログを docs/service-catalog.md に生成/更新する（推測禁止、出典必須）。

# 入力（優先順位順）
原則として次の4ファイルを読む。無い場合は `search` で同等の資料を特定し、差分（不足・代替）を明記する。
- `docs/service-list.md`
- `docs/data-model.md`
- `docs/screen-list.md`
- `docs/usecase/{ユースケースID}/usecase-detail.md`

# 出力（必須）
- `docs/service-catalog.md`
```

# Step.5. 生成AIに最適化した各コンポーネントプロンプトの作成

> [!NOTE]
> これでもある程度は動きますが。もっとPromptとして最適化できると思います...

Step 3. で作成したユースケースの情報をもとに、生成AIに最適化したプロンプトを作成します。

## Step.5.1. 画面定義書の作成

画面定義書は、既存のドキュメントを強く意識している「人」が理解しやすいであろう構造化情報として作成されています。

- カスタムエージェント
  - Arch-UI-Detail

```text
# タスク
docs/screen-list.md の全画面について、実装に使える画面定義書（UX/A11y/セキュリティ含む）を docs/usecase/<ユースケースID>/screen/ に生成・更新する。

# 入力（必読）
- ユースケースID: {ユースケースID}
- `docs/usecase/{ユースケースID}/usecase-detail.md.md`（最優先）
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
- `docs/usecase/{ユースケースID}/usecase-detail.md.md`
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
