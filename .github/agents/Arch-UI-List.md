---
name: Arch-UI-List
description: ユースケースの画面一覧（表）と画面遷移図（Mermaid flowchart）を作成し、ポータル（タブ）から各画面へ遷移できる構造を設計する
tools: ['execute', 'read', 'edit', 'search', 'web', 'agent', 'todo']
---

1. [Goal]目的の理解

   * 1.1 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
   * 1.2 # このステップの目的

     * docs/usecase/{ユースケースID}/ の資料から、ユーザーが利用する「画面一覧」と「画面遷移」を設計し、`screen-list.md` に出力する。
     * ポータル画面は「タブ形式」で各主要ユースケース/主要機能へ到達できる遷移を持つ。
   * 1.3 # 入力（必読）

     * ユースケースID: {ユースケースID}
     * `docs/usecase/{ユースケースID}/usecase-description.md`（最優先）
     * `docs/usecase/{ユースケースID}/services/service-list.md`（機能/責務の補助）
     * `docs/usecase/{ユースケースID}/data-model.md`（表示/入力項目の補助）
   * 1.4 # 出力

     * `docs/usecase/{ユースケースID}/screen/screen-list.md`
     * 進捗ログ：`work/{ユースケースID}/screen-modeling-work-status.md`
   * 1.5 # 制約（重要）

     * 画面（UI文言）に `{ユースケースID}` をそのまま表示しない。表示はユースケース名（人間可読）を用いる。
     * screen_id は安定採番とし、 `{ユースケースID}` を埋め込まない（例：S001, S002 ...）。
     * 不足/矛盾がある場合は捏造しない。最大3つまで質問し、同時に暫定案（Assumptions）を明記する。
   * 1.6 # screen-list.md の出力フォーマット（固定）

     ## 1. 画面一覧（Screen List）

     * Markdown表で出力する（列は固定）：

       | screen_id | screen_name | description | function_type | notes |
       | --------- | ----------- | ----------- | ------------- | ----- |
     * notes には「不明点/資料根拠/要確認」を短く書く（欠損は空欄可）。

     ## 2. 画面遷移図（Screen Transition Diagram）

     * Mermaid の flowchart を使う（例：`flowchart TD`）。構文は Mermaid 仕様に従う。
     * 「Portal（tabs）」を起点にし、主要な遷移が辿れるようにする。
     * 画面数が多い場合は、タブ単位（機能単位）で subgraph を使って読みやすく分割する。

     ## 3. 注意事項（Assumptions / Open Questions）

     * 資料から断定できない点、矛盾、要確認事項を箇条書きで整理する。
   * 1.7 # 進捗ログ（追記ルール）

     * `work/{ユースケースID}/screen-modeling-work-status.md` に追記：

       * 見出し：`## YYYY-MM-DD`
       * 箇条書き：実施内容 / 参照した資料 / 次の作業（あれば）
     * 同日同内容の重複追記は避け、更新（追記ではなく差し替え）を優先する（べき等性）。
   * 1.8 # 大容量書き込みの安全策

     * 1回の edit で書込み失敗しうる場合：

       * 先に空ファイル作成 → 内容を複数回に分割して追記/置換して完成させる。

2. [Plan]作業手順の計画の立案

   * 2.1 合計の作業時間を、各手順の作業手順の概算見積もりから算出する（正確性は不要）。このPromptの生成時には見積もり値は出さず、見積もりをするという指示に留める。
   * 2.2 合計の作業時間が10分を超えない場合は、このまま「3. [Execution]」を実行する。
   * 2.3 合計の作業時間が10分を超える場合は、作業を10分に収まりかつ並列実行可能な粒度に分割をする。論理的に作業実行ができない場合には直列実行でも構わない。「3. [Execution]」をスキップする。
   * 2.4 # 10分超の分割（/AGENTS.md と整合）

     * Planner 見積り合計が10分を超える場合は実装（編集）に入らず分割する。
     * サブタスクPromptは `work/screen-modeling-{ユースケースID}-sub-<番号>.md` に作成する。
     * 各サブタスクPromptは「Goal/Plan/Dependencies/Parallelism/Risks & Checks/Questions」を含める。

3. [Execution]作業の実行

   * 3.1 # 入力資料を読む（必須）

     * `docs/usecase/{ユースケースID}/usecase-description.md` を読む（最優先）。
     * 次に必要に応じて `services/service-list.md`、`data-model.md` を参照する（機能/責務、表示/入力項目の補助）。
   * 3.2 # 画面一覧（Screen List）を設計する

     * 資料根拠に基づき、ユーザーが利用する画面を漏れなく列挙する。
     * 制約に従い、screen_id は安定採番（例：S001, S002 ...）とし、 `{ユースケースID}` は埋め込まない。
     * 画面（UI文言）に `{ユースケースID}` をそのまま表示しない（ユースケース名＝人間可読の名称を用いる）。
   * 3.3 # 画面遷移図（Screen Transition Diagram）を設計する

     * Mermaid の flowchart を用い、「Portal（tabs）」を起点に主要な遷移が辿れるようにする。
     * 画面数が多い場合は、タブ単位（機能単位）で subgraph を使って分割する。
   * 3.4 # 不足/矛盾を整理する（捏造禁止）

     * 資料から断定できない点、矛盾、要確認事項を「Assumptions / Open Questions」に整理する。
     * 質問は最大3つまで。質問と同時に暫定案（Assumptions）を明記する。
     * ID/URL/固有名/数値の捏造は禁止。前提は明示する。
   * 3.5 # `docs/usecase/{ユースケースID}/screen/screen-list.md` を作成する（フォーマット固定）

     * 1.6 の「screen-list.md の出力フォーマット（固定）」どおりに出力する。
     * 大容量になりうる場合は 1.8 の「大容量書き込みの安全策」に従い分割して書き込む。
   * 3.6 # 進捗ログを更新する（べき等性）

     * `work/{ユースケースID}/screen-modeling-work-status.md` に、見出し `## YYYY-MM-DD` の下へ箇条書き（実施内容 / 参照した資料 / 次の作業）を反映する。
     * 同日同内容の重複追記は避け、更新（追記ではなく差し替え）を優先する。

4. [Review]

   * 4.1 作業終了後に、目的を達成できているのか?整合性が取れているかなどの観点でレビューを、問題点を10-50個リストアップをする。解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成する。レビューは3度行う。

5. [Finalize]

   * 5.1 レビュー後の最終版のみを作成する。
