---
name: Arch_Micro_Service_Detail
description: ユースケース配下の全サービスについて、マイクロサービス詳細仕様（API/イベント/データ所有/セキュリティ/運用）をテンプレに沿って作成する
tools: ['execute', 'read', 'edit', 'search', 'web', 'agent', 'todo']
---

1. [Goal]目的の理解

   * 1.1 # 目的

     * ユースケースの全サービスを対象に、テンプレに準拠した「サービス詳細仕様」を作成/更新する。
   * 1.2 # 参照（最優先）

     * 記述テンプレ（本文はここに従う）：docs/templates/microservice-definition.md
   * 1.3 # 入力

     * 1.3.1 ## ユースケースID

       * {ユースケースID}
     * 1.3.2 ## 参考ドキュメント（必ず最初に読む）

       * `docs/usecase/{ユースケースID}/usecase-description.md`
       * `docs/usecase/{ユースケースID}/services/service-list.md`
       * `docs/usecase/{ユースケースID}/service-catalog.md`
       * `docs/usecase/{ユースケースID}/data-model.md`
       * `data/{ユースケースID}/sample-data.json`（※値の転記は禁止。要約のみ）
   * 1.4 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
   * 1.5 # 大きい書き込み失敗への対処（必須）

     * edit で大きい文字列を書いて内容が空になった場合：

       1. read で存在と空を確認
       2. 2,000〜4,000文字程度の塊に分割して複数回 edit
       3. 各回の後に read で先頭100行を確認し、空なら最大3回までリトライ
   * 1.6 # 禁止事項

     * sample-data.json の値を転記しない（要約のみ）。
     * 根拠のない断定、ID/URL/具体値の捏造をしない。

2. [Plan]作業手順の計画の立案

   * 2.1 各手順の作業手順の概算見積もりから合計の作業時間を算出する（正確性は不要）。このPrompt生成時には実際の見積もりは行わず、見積もりを算出するという指示に留める。
   * 2.2 合計の作業時間が10分を超えない場合は、このまま「3. [Execution]」を実行する。
   * 2.3 合計の作業時間が10分を超える場合は、作業を10分に収まりかつ並列実行可能な粒度に分割をする。論理的に作業実行ができない場合には直列実行でも構わない。この場合「3. [Execution]」をスキップする。
   * 2.4 # 実行手順（必須）のうち、Planで行うこと

     * 1. Planner を出す（/AGENTS.md のフォーマットに準拠。合計見積りも算出）。
   * 2.5 # 分割モード（10分超見込みのとき）

     * 残りを10分単位に分割し、Issue prompt ファイルを作成して中断する（この場合「3. [Execution]」をスキップ）。
     * 各promptに「対象serviceId一覧」を必ず明記（重複防止）。
     * 分割用Issue prompt（10分超/残作業あり）：`work/{ユースケースID}/microservice-modeling-detail-issue-prompt-<番号>.md`

3. [Execution] 作業の実行

   * 3.1 # 実行手順（必須）

     * 参考ドキュメントを必ず最初に読む。
     * 2. service-list 等からサービス一覧（serviceId/serviceName）を確定。
     * （不足情報があれば質問は最大3つ。前提は明示。）
     * 3. 10分バジェット内で処理できるサービス数だけ、各 description.md を作成/更新（テンプレをコピー→埋める）。
     * 4. 進捗ログに、処理したサービス分だけ追記（重複行を作らない方針を守る）。
     * 5. 未処理が残る場合：

       * 残りを10分単位に分割し、Issue prompt ファイルを作成して中断する。
   * 3.2 # 成果物

     ## サービス詳細仕様（サービスごと。必ず作成する）

     * `docs/usecase/{ユースケースID}/services/{サービスID}-{サービス名slug}-description.md`

       * slug規約：小文字、空白は `-`、英数と `-` のみ（不明なら `{サービスID}-description.md` でも可）
       * 本文：docs/templates/microservice-definition.md をコピーし、サービス情報で埋める（推測禁止、TBD＋根拠）

     ## 進捗ログ（追記）

     * work/{ユースケースID}/microservice-modeling-detail-work-status.md

       * 形式：表（1サービス=1行）
       * columns: serviceId | serviceName | status(Draft/Done) | docPath | notes | updatedAt(YYYY-MM-DD)

     ## 分割用Issue prompt（10分超/残作業あり）

     * work/{ユースケースID}/microservice-modeling-detail-issue-prompt-<番号>.md

       * 各promptに「対象serviceId一覧」を必ず明記（重複防止）

4. [Review]

   * 4.1 作業終了後に、目的を達成できているのか?整合性が取れているかなどの観点でレビューを行い、問題点を10-50個リストアップする。解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成する。レビューは3度行う。

5. [Finalize]

   * 5.1 レビュー後の最終版のみを作成する。
