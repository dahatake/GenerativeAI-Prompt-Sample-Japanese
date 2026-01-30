---
name: Dev-WebAzure-UIDeploy-AzureStaticWebApps
description: Azure Static Web Apps にWebをデプロイし、GitHub Actionsで継続的デリバリーを構築する
tools: ["*"]
---

1. [Goal]目的の理解

   * 1.1 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。

   * 1.2 # 0. 前提（変数）

     * ユースケースID: {ユースケースID}
     * リソースグループ名: {リソースグループ名}
     * リージョン優先順: East Asia -> Japan West -> Southeast Asia
     * Azure CLIスクリプト保存先:

       * infra/{ユースケースID}/create-azure-webui-resources.sh
       * infra/{ユースケースID}/create-azure-webui-resources-prep.sh
     * サービスカタログ: docs/usecase/{ユースケースID}/service-catalog.md
     * 進捗ログ: work/{ユースケースID}/screen-azure-deploy-work-status.md

   * 1.3 # 不足情報の扱い（最大3つまで質問）

     * 不足情報（例: サブスクリプション、対象ブランチ、アプリのビルド出力パス）があれば最大3つまで質問し、仮定も併記する（捏造禁止）。

2. [Plan]作業手順の計画の立案

   * 2.1 合計の作業時間を、各手順の概算見積もりから算出する（正確性は不要）。このPromptの生成時には見積もりは行わず、見積もりをするという指示に留める。

   * 2.2 合計の作業時間が **10分を超えない** 場合は、このまま実行する。

   * 2.3 合計の作業時間が **10分を超える** 場合は、作業を10分に収まりかつ並列実行可能な粒度に分割する（論理的に難しい場合は直列でも可）。この場合は **「3. [Execution]」をスキップ** する。

   * 2.4 # 1. 必須プロセス（Planner）

     * リポジトリ既定ルール（/AGENTS.md）に従い、実装前に必ず Planner を出力する。
     * 見積り合計が10分を超える場合：実装に入らず分割モードへ。

       * 分割Promptを `work/{ユースケースID}/screen-azure-deploy-issue-prompt-<番号>.md` に日本語で作成する（各Promptに Goal/Plan/成果物/検証/依存/Parent参照を含める）。
       * 分割Prompt作成後は終了し、実装（3章）は行わない。

3. [Execution]作業の実行（[Plan]は含めない／分割モード時は本章を出力しない）

   * 3.1 # 2. 成果物（このジョブで必ず作る/更新するもの）

     1. infra/{ユースケースID}/create-azure-webui-resources-prep.sh

        * Linux bash。必要ツール/パッケージのインストール（最小限）。
     2. infra/{ユースケースID}/create-azure-webui-resources.sh

        * Azure Static Web Apps の作成（Azure CLI）。冪等（既存があれば安全に終了/更新）。
        * Azure CLIの正確な引数・コマンドは MicrosoftDocs（MCP Server）で確認して反映する。
     3. .github/workflows/<適切な名前>.yml（新規 or 更新）

        * GitHub Actions で SWA へデプロイ。基本は deployment token を Secret `AZURE_STATIC_WEB_APPS_API_TOKEN` として参照する。
        * app_location/api_location/output_location 等の構成は Static Web Apps のビルド構成に従い、実プロジェクト構造に合わせて設定する。
     4. docs/usecase/{ユースケースID}/service-catalog.md

        * 作成できた WebアプリのURLを追記（CLI出力 or `az staticwebapp show` 等で取得）。
     5. work/{ユースケースID}/screen-azure-deploy-work-status.md

        * 進捗を日本語で追記（書式は下記）。
     6. README.md

        * 依頼範囲に限定して「機能概要（1段落）」＋「起動手順（最小）」を追記。

   * 3.2 # 3. 認証・セキュリティ（このタスクに必要な最小限）

     * 資格情報/トークンをコードやコミットに直書きしない。
     * SWAデプロイは原則 deployment token（推奨）を使用し、GitHub Secrets に `AZURE_STATIC_WEB_APPS_API_TOKEN` を設定する前提でワークフローを書く。

       * ※Secrets設定が必要な場合は「手動手順」をREADMEまたはwork-statusに短く記録する（Secrets値は書かない）。

   * 3.3 # 4. GitHub Actions 要件（最小）

     * main（または指定ブランチ）への push でデプロイ、必要なら PR でもプレビュー（要件が不明なら質問）。
     * 公式例に準拠しつつ、リポジトリの実ディレクトリ構造に合わせて設定する。

   * 3.4 # 5. 進捗ログの書式（追記ルール）

     * work/{ユースケースID}/screen-azure-deploy-work-status.md に追記する行は以下：

       * YYYY-MM-DD HH:MM: 実施内容 / 結果 / 次アクション

   * 3.5 # 6. 空ファイル対策（書き込み失敗時）

     * ファイルが作成されたのに内容が空の場合：

       1. 書き込み対象文字列を分割（セクション単位）して複数回で追記
       2. 書き込み後にファイルサイズ/先頭数行を確認
       3. それでも失敗する場合は、分割粒度をさらに小さくして再試行

   * 3.6 # 実行ステップ（逐次実行）

     1. 不足情報（例: サブスクリプション、対象ブランチ、アプリのビルド出力パス）が成果物の作成/更新に影響する場合、最大3つまで質問し、仮定も併記する（捏造禁止）。
     2. `infra/{ユースケースID}/create-azure-webui-resources-prep.sh` を作成/更新する。
     3. `infra/{ユースケースID}/create-azure-webui-resources.sh` を作成/更新する（MicrosoftDocs（MCP Server）でAzure CLI引数を確認して反映、冪等）。
     4. `.github/workflows/<適切な名前>.yml` を作成/更新する（`AZURE_STATIC_WEB_APPS_API_TOKEN` 参照、ディレクトリ構造に整合）。
     5. `docs/usecase/{ユースケースID}/service-catalog.md` にWebアプリURLを追記する（CLI出力 or `az staticwebapp show` 等）。
     6. `work/{ユースケースID}/screen-azure-deploy-work-status.md` に指定書式で追記する。
     7. `README.md` に依頼範囲で追記する（機能概要1段落＋起動手順最小）。

4. [Review]

   * 4.1 作業終了後に、目的を達成できているのか?整合性が取れているかなどの観点でレビューを、問題点を10-50個リストアップをする。解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成する。レビューは異なる観点で、3度行う。

     * 観点1：要件充足（成果物1)〜6)、URL追記、ログ、README）
     * 観点2：セキュリティ/運用（Secrets、トークン直書き禁止、手動手順記録）
     * 観点3：冪等性/再現性/整合性（既存時挙動、スクリプト実行性、設定整合）

   * 4.2 # 7. 完了条件（Acceptance Criteria）

     * SWA リソースが作成され、URLが service-catalog.md に追記されている。
     * GitHub Actions のワークフローがリポジトリに存在し、`AZURE_STATIC_WEB_APPS_API_TOKEN` を参照している。
     * prep.sh / resources.sh がLinux bashで実行可能で、冪等性に配慮されている。
     * work-status と README が依頼範囲で更新されている。

5. [Finalize]

   * 5.1 レビュー後の最終版のみを作成する。

     * レビューで立案した解決策を反映した最終成果物のみを提示する（中間案・レビューの問題リストは最終成果物に混ぜない）。
