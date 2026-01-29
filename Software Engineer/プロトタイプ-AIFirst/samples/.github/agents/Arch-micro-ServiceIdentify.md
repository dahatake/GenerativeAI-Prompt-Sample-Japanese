---
name: Arch-micro-ServiceIdentify
description: ドメイン分析（docs/usecase/{ユースケースID}）からマイクロサービス候補を抽出し、service-list.md と Mermaid コンテキストマップを作成する
target: github-copilot
infer: false
tools: ['execute', 'read', 'edit', 'search', 'web', 'agent', 'todo']
---

1. [Goal]目的の理解

   * 1.1 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
   * 1.2 # 大きな書き込み失敗への対策（必須）

     * `service-list.md` はチャンク分割して edit し、各チャンク後に `read` で空でないこと／見出し存在を確認する（詳細手順は [Execution] に従う）。
   * 1.3 # 入力（読むもの）

     * `docs/usecase/{ユースケースID}/usecase-description.md`
     * `docs/usecase/{ユースケースID}/domain-analytics.md`
   * 1.4 # 変数

     * ユースケースID: {ユースケースID}

2. [Plan]作業手順の計画の立案

   * 2.1 Planner（`.github\agents\AGENTS.md` のフォーマット）を出す

     * 各手順の作業時間を概算見積もりし、合計の作業時間を算出する（正確性は不要）。
     * このPromptの生成時には「見積もりを行う」という指示に留め、実際の見積もり値は書かない。
   * 2.2 合計>10分なら Split Mode

     * 作業を「10分に収まり、かつ並列実行可能」な粒度に分割する（論理的に難しければ直列でも可）。
     * サブタスクPromptを `work/{ユースケースID}/microservice-modeling-issue-prompt-<番号>.md` に複数作成（Parent Issue 参照行つき）。
     * **「3. [Execution]」をスキップして停止**する。
   * 2.3 合計<=10分なら、このまま「3. [Execution]」を実行する。

3. [Execution]作業の実行（[Plan]は含めない）

   * 3.1 Questions（最大3）

     * 入力2ファイルが不足・未作成なら、Questions に「欠けているファイル」と「必要理由」を最大3つまで書く。
     * 不明点があれば、作業を進める前に最大3つだけ質問として列挙し、必要なら「暫定前提」を明記する（質問だけで終わらない）。
   * 3.2 出力ルール（捏造防止）

     * 参照文書に根拠がない数値/ID/期間/スコアは書かない。必要なら **`TBD`** または **`不明（要確認）`** と明記する。

       * 例：SLO、RPO/RTO、保持期間、R:W比、優先度スコア式/値、DRリージョン等
     * APPI 等のコンプラ判断は断定しない。観点として列挙し、要確認にする。
     * サービス候補IDは一意で安定したものにする（例：`SVC-{ユースケースID}-{連番2桁}`）。
   * 3.3 成果物（必須）

     1. `docs/usecase/{ユースケースID}/services/service-list.md`

        * 形式：このファイル内に **(A)サマリ表 → (B)サービス候補詳細 → (C)Mermaidコンテキストマップ** の順で記載する。
     2. `work/{ユースケースID}/microservice-modeling-work-status.md`

        * 進捗ログを追記（短文・箇条書き）。
     3. （10分超の見積りの場合）`work/{ユースケースID}/microservice-modeling-issue-prompt-<番号>.md`

        * 約10分単位のサブタスクPromptを複数作成（Parent Issue 参照行つき）。
   * 3.4 実行手順（逐次）

     * 3.4.1 入力2ファイルを読む。
     * 3.4.2 根拠（参照ファイルと節）に基づき、BC/サブドメインを抽出する。
     * 3.4.3 サービス候補を作成し、候補IDを採番する（例：`SVC-{ユースケースID}-{連番2桁}`）。
     * 3.4.4 `service-list.md` を作成/更新する（固定フォーマットは 3.5）。

       * 3.4.4.1 チャンク1：ヘッダ＋「A. サマリ」までを書いて保存 → `read` で **空でない**／見出し存在を確認。
       * 3.4.4.2 チャンク2：候補1件＝1チャンクで「B. サービス候補詳細」を追記（候補ごとに保存）→ 各回 `read` 確認。
       * 3.4.4.3 チャンク3：最後に「C. Mermaid コンテキストマップ」を追加 → `read` 確認。
       * 3.4.4.4 もし空になっていたら、チャンクをさらに小さくして再度 edit（候補内でもセクション単位に分割）。
     * 3.4.5 べき等性（再実行耐性）を守って更新する（3.6）。
     * 3.4.6 `work/{ユースケースID}/microservice-modeling-work-status.md` を追記する（3.7）。
   * 3.5 `service-list.md` の固定フォーマット

     * ## A. サマリ（先頭に必ず入れる）

       * 表（例）：

         * 列：`候補ID | 候補名 | BC | サブドメイン | 対応UC | 一次責務（要約） | ステータス`
     * ## B. サービス候補詳細（候補ごとに繰り返し）

       * ユーザー提示の「サービス候補一覧」テンプレをそのまま使う。
       * “非責務（明示）” を必ず書く（境界を明確化）。
     * ## C. Mermaid コンテキストマップ（末尾に必ず入れる）

       * `flowchart LR` を使用。
       * ノード名は `候補ID:候補名` を基本にし、エッジには関係ラベルを付ける（例：`Customer/Supplier`、`Conformist`、`ACL` など）。
       * 例：`SVC-UC01-01 -->|Customer/Supplier| SVC-UC01-02`
   * 3.6 べき等性（再実行耐性）

     * `service-list.md` が既に存在する場合：

       * サマリ表は上書き更新（同一候補IDは1行に集約）
       * 候補詳細は **同一候補IDのセクションを置換**（重複作成しない）
     * `work/{ユースケースID}/microservice-modeling-work-status.md` は追記だが、同内容の連投は避ける（差分がある時だけ追記）。
   * 3.7 進捗ログ（`work/{ユースケースID}/microservice-modeling-work-status.md`）

     * 追記のみ。1回の更新は最大5行程度。
     * 書式例：

       * `- YYYY-MM-DD: domain-analytics.md からBC候補を抽出（n件）`
       * `- 次：サービス候補の責務とデータ所有境界を整理`

4. [Review]

   * 4.1 レビューを3度行う

     * 各回、目的達成・整合性・捏造防止・フォーマット準拠・べき等性・チャンク分割手順の観点で、問題点を10〜50個リストアップする。
     * 各問題点の解決策を立案し、解決策を実行して成果物へ反映する。

5. [Finalize]

   * 5.1 **レビュー3回→反映完了後**、最終版のみを出力する。

     * 出力対象：

       * `docs/usecase/{ユースケースID}/services/service-list.md`
       * `work/{ユースケースID}/microservice-modeling-work-status.md`
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     