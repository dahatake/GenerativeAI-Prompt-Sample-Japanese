# Product Management - ユースケースなど作成

要求定義のドキュメントから、ユースケースを作成します

GitHub Copilot AgentへのIssue候補でもあります。

https://docs.github.com/ja/enterprise-cloud@latest/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot

### Step 1.フューチャーシナリオとユースケースの作成

ドキュメントとして、フューチャーシナリオとユースケースを作成します。

#### ツール

- GitHub Copilot Coding Agent

  GitHub Copilot の **Coding Agent**のIssueからCoding Agentに作業をしてもらう前提です。

  https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/


- 要求定義のドキュメントは、**Markdown**の形式にして、`/docs`フォルダに保存します。
- 各ステップでの**入力**と、**出力先**の、パスとファイル名は適時修正してください。
- そのファイル名でよい場合は、**削除**してください。重複情報が制御に悪い影響ができる可能性があるのと、トークン数を減らすためです。

#### Step 1.1. フューチャーシナリオの一覧作成

- 使用するカスタムエージェント
  - PM-FutureScenarioList

```text
# タスク
要求定義ドキュメントからFuture Scenarioを抽出し、価値(KPI)と実現性を踏まえた一覧を作成してリポジトリに保存する

# 入力
- 要求定義ドキュメント（常に参照すること）
  - `docs/docs/business-requirement.md`（プロジェクト内の該当ファイル）

# 出力先（リポジトリ相対パス）
- `docs/future_scenario/future-scenario-list.md`
```

#### Step. 1.2 フューチャーシナリオの詳細作成

- 使用するカスタムエージェント
  - PM-FutureScenarioDetail

```text
# タスク
Future Scenario一覧を読み、各FSの詳細（業務フロー/例外/運用/データ/制約/KPI）をUse Case化に直接使える粒度で作成し、FSごとのMarkdownに保存する

# 入力（必須）
- 要求定義ドキュメント：`docs/business-requirement.md`（常に参照）
- FS一覧：`/docs/future_scenario/future-scenario-list.md`

# 出力先（リポジトリ相対パス）
- `/docs/future_scenario/future-scenario-details-{FS-ID}.md`
```

#### Step. 2.1 ユースケース一覧作成 

- 使用するカスタムエージェント
  - PM-UseCaseList

```text
# タスク
要求定義と Future Scenario から「ソフトウェアで実現すべきユースケース」を抽出し、独自開発優先度を評価して一覧化する

# 入力（必須：常に参照）
- 要求定義ドキュメント：`docs/business-requirement.md`
- Future Scenario List：`docs/future_scenario/future-scenario-list.md`
- Future Scenario 詳細：`docs/future_scenario/future-scenario-details-{FS-ID}.md`

# 出力先（Markdown、固定）
- `/docs/usecase/usecase-list.md`
```

#### Step. 2.2 フューチャーシナリオとユースケースのマッピングカタログの作成 

- 使用するカスタムエージェント
  - PM-FutureScenarioUseCase-Catalog

```text
# タスク
要求定義とFS/UC成果物を突合し、FSステップ/例外 ↔ UCフロー対応表・逆引き・不整合修正案・Mermaid図を生成してカタログ表を作成する

# 入力（必須）
- 要求定義ドキュメント：`docs/business-requirement.md`
- FS一覧：`/docs/future_scenario/future-scenario-list.md`
- FS詳細：`/docs/future_scenario/future-scenario-details-{FS-ID}.md`
- UC一覧：`/docs/usecase/usecase-list.md`

# 出力先（リポジトリ相対パス）
- `/docs/usecase/fs-uc-catalog.md`
```

#### Step. 2.3 ユースケース作成

ユースケース一覧を参考にして、全てのユースケースについて、ユースケースを作成します。

- 使用するカスタムエージェント
  - PM-UseCaseDetail

```text
Use Case一覧から指定UCを1件だけ詳細化し、FS/要求定義と整合したUC定義書（フロー・例外・ルール・NFR・受入・図）を /docs/usecase/ に生成する

# 入力（必須：必ず参照）
- 要求定義ドキュメント：`docs/business-requirement.md`（常に参照）
- Future Scenario：
  - `/docs/future_scenario/future-scenario-list.md`
  - `/docs/future_scenario/future-scenario-details-{FS-ID}.md`
- Use Case一覧：`/docs/usecase/usecase-list.md`

# 出力先（Markdown）— テンプレ固定
- `/docs/usecase/usecase-<TARGET_UC_ID>.md`
```
