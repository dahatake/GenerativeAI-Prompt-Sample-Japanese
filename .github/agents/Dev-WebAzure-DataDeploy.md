---
name: Dev-WebAzure-DataDeploy
description: Azure CLIでデータ系サービスを最小構成で作成し、サンプルデータを変換・一括登録する（冪等・検証付き）
tools: ["*"]
---

1. [Goal]目的の理解

   * 1.1 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
     * 資格情報をハードコードしない（Key Vault / 環境変数 / Managed Identity 前提）。秘密情報をログに出さない。
   * 1.2 # このStepのゴール

     * `docs/usecase/{ユースケースID}/AzureServices-data.md` に列挙された「データストア」サービス群を、Azure上に最小構成で作成する。
     * 作成後、サンプルデータを各サービスに適切に変換して一括登録し、登録結果を検証する。
     * ドキュメント（サービスカタログ/進捗/README）を事実ベースで更新する。
   * 1.3 # Inputs（必読）

     * データストア定義: `docs/usecase/{ユースケースID}/AzureServices-data.md`
     * サービスカタログ: `docs/usecase/{ユースケースID}/service-catalog.md`
     * 既存サンプルデータの所在（このファイルに明記がなければ Questions で確認）
   * 1.4 # MCP（MicrosoftDocs / Azure）利用ルール

     * 最新仕様が必要な箇所だけ MicrosoftDocs MCP で確認する（例: 対象サービスの作成CLI、最小SKU、データ投入方法）。
     * 取得した要点はスクリプト内コメントに「根拠（ドキュメント名/節）」として短く残す。
     * Azure上での実行は Azure MCP Server を使う。認証/権限不足で実行できない場合は、止めて “原因/必要な権限/代替実行手順” を明記する。
   * 1.5 # ファイル書き込み失敗（Empty化）対策（必須）

     * 大きな本文を書き込んだ後は「ファイルが空でない」ことを必ず検証する。
     * 空の場合は、本文を分割して複数回に分けて書き込み、最終的に内容が揃ったことを再検証する。
   * 1.6 # 変数

     * ユースケースID: {ユースケースID}

2. [Plan]作業手順の計画の立案

   * 2.1 各手順の作業手順の概算見積もりから合計作業時間を算出する（正確性は不要）。このPrompt生成時点では実見積りはせず、「見積もること」という指示に留める。
   * 2.2 合計の作業時間が10分を超えない場合は、このまま「3. [Execution]」を実行する。
   * 2.3 合計の作業時間が10分を超える場合は、作業を10分に収まりかつ並列実行可能な粒度に分割する。論理的に作業実行ができない場合には直列実行でも構わない。この場合「3. [Execution]」をスキップする。
   * 2.4 # Split Mode（合計>10分）

     * `work/{ユースケースID}/data-azure-deploy-issue-prompt-<番号>.md` に、約10分単位のPromptを日本語で作る。
     * 推奨分割（例）:

       1. AzureServices-data.md の解析＋作成対象/最小構成の決定
       2. prep.sh 作成＋検証
       3. create-azure-data-resources.sh 作成＋検証
       4. data-registration-script.sh 作成＋検証
       5. service-catalog / work-status / README 更新

3. [Execution]作業の実行

   * 3.1 # 実行順序（逐次）

     1. Inputs（必読）を読み、`AzureServices-data.md` の「データストア」サービス群を作成対象として確定する（不足は Questions に集約）。
     2. 必要な箇所のみ MicrosoftDocs MCP で最新仕様を確認し、要点をスクリプト内コメントに「根拠（ドキュメント名/節）」として短く残す。
     3. `infra/{ユースケースID}/create-azure-data-resources-prep.sh` を作成する（要件は Outputs を満たす）。
     4. `infra/{ユースケースID}/create-azure-data-resources.sh` を作成する（冪等、リージョン自動フォールバック、最小構成、検証出力など Outputs の要件を満たす）。
     5. `data/{ユースケースID}/data-registration-script.sh` を作成する（変換と登録の分離、ログ、登録後検証など Outputs の要件を満たす）。
     6. 作成したスクリプト／手順に基づき、作成結果・登録結果を検証する（権限不足等で実行不可なら停止し、原因/必要権限/代替手順を明記）。
     7. `docs/usecase/{ユースケースID}/service-catalog.md`、`work/{ユースケースID}/data-azure-deploy-work-status.md`、`/README.md` を事実ベースで更新する（未確定事項は書かない）。
   * 3.2 # Outputs（必ず作る/更新する）

     # Outputs（必ず作る/更新する）

     ## 1) 事前準備スクリプト（Linux）

     * `infra/{ユースケースID}/create-azure-data-resources-prep.sh`

       * 目的: 必要ツール/拡張のインストール、az拡張、前提チェック（ログイン、サブスクリプション、権限）
       * 要件: `set -euo pipefail`、実行ログ、失敗時の分かりやすいメッセージ

     ## 2) リソース作成スクリプト（Linux）

     * `infra/{ユースケースID}/create-azure-data-resources.sh`

       * 目的: データストアのAzureサービスを最小構成で作成
       * 要件:

         * 冪等（存在チェック→作成/更新）。再実行で落ちない
         * リージョン: 原則 Japan East。利用不可時は Japan West → East Asia → Southeast Asia の順で自動フォールバック
         * 可能ならサーバーレス/最小SKU/オートスケール最小
         * リソース名: `{サービス名}` をベースにし、衝突回避トークンを付与（必要な場合）
         * タグ付け（usecase, env, owner 等。具体は repo-wide 指示に従う）
         * 作成後に `az ... show/list` 等で存在/設定を検証し、重要値（URL/ID/リージョン）を出力

     ## 3) データ登録スクリプト（Linux）

     * `data/{ユースケースID}/data-registration-script.sh`

       * 目的: サンプルデータを変換し、各サービスへ一括登録
       * 要件:

         * 入力データの場所/形式を明示（不明なら Questions）
         * 変換（必要な場合）と登録を分離し、ログに件数/結果を出す
         * 登録後に最小の検証（件数取得/サンプル取得/クエリ）を実施

     ## 4) ドキュメント更新

     * サービスカタログ追記: `docs/usecase/{ユースケースID}/service-catalog.md`

       * 追記する表の列（重複禁止）:

         * ServiceID（独自ID。無いなら null または “TBD”）
         * マイクロサービス名
         * サービス種別（例: Cosmos DB / Blob Storage 等）
         * サービスURL（接続先のURI等。無ければ null）
         * Azure Resource ID（/subscriptions/... のresourceId）
         * リージョン
     * 進捗ログ追記（日本語）: `work/{ユースケースID}/data-azure-deploy-work-status.md`

       * 形式: 日付/実施内容/結果/次アクション/課題
     * README追記: `/README.md`

       * このStepで確定した“事実”のみ（作成したスクリプト、実行手順、検証手順）。未確定事項は書かない。

4. [Review]

   * 4.1 作業終了後に、目的を達成できているのか?整合性が取れているかなどの観点でレビューを、問題点を10-50個リストアップをする。解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成する。レビューは異なる観点で、3度行う。

5. [Finalize]

   * 5.1 レビュー後の最終版のみを作成する。
