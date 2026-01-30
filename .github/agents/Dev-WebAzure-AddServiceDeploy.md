---
name: Dev-WebAzure-AddServiceDeploy
description: Azure CLIで追加サービス（例: Azure OpenAI等）を作成し、サービスカタログ/README/進捗ログを更新する（Planner必須・10分分割・冪等）
infer: false
tools: ["*"]
---

1. [Goal]目的の理解

   * 1.1 # このPromptの目的

     * `docs/usecase/{ユースケースID}/AzureServices-services-additional.md` を根拠に、追加Azureサービスを作成するための手順を確定し、（条件を満たす場合は）スクリプト作成・実行・ドキュメント更新までを行う。
   * 1.2 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
   * 1.3 # 大きい文字列の書き込み失敗対策（重要）

     * 重要ファイルを編集後、必ず読み直して「空でない」ことを確認する。
     * 空になっていたら、内容を分割して複数回の編集で再書き込みする（1回の差分を小さく）。
   * 1.4 # 入力（このファイル内の変数は“未置換なら停止して質問”）

     * 1.4.1 ## ユースケースID

       * {ユースケースID}
     * 1.4.2 ## 追加サービス定義（必読）

       * `docs/usecase/{ユースケースID}/AzureServices-services-additional.md`
   * 1.5 # 技術仕様（前提）

     * リソースグループ名: {リソースグループ名}
     * 優先リージョン: Japan East

       * 利用不可なら Japan West / East Asia / Southeast Asia / 最後は任意（※サービスごとの可用性はMicrosoftDocsで確認）
     * スケール: 最小構成（サーバーレス/オートスケールがあれば優先）
     * インスタンス名: {サービス名} を使用
     * 資格情報: ハードコード禁止（Key Vault / Managed Identity / 最小権限RBAC）
   * 1.6 # 生成物の保存先

     * Azure CLIスクリプト: `infra/{ユースケースID}/create-azure-additional-resources/`
     * 依存ツール準備スクリプト: `infra/{ユースケースID}/create-azure-additional-resources-prep.sh`
     * サービスカタログ: `docs/usecase/{ユースケースID}/service-catalog.md`
     * (Split Modeのみ)進捗ログ: `work/{ユースケースID}/data-azure-additionalservices-deploy-work-status.md`
     * (Split Modeのみ)分割Issue Prompt: `work/{ユースケースID}/data-azure-additionalservices-deploy-issue-prompt-<番号>.md`
     * README追記: `/README.md`

2. [Plan]作業手順の計画の立案

   * 2.1 各手順の概算見積もり（正確性不要）

     * 各手順の概算時間を見積もり、合計時間を算出する（このPrompt生成時に実見積もりは行わず、実行時に算出する）。
   * 2.2 分岐（10分ルール）

     * 合計作業時間が10分を超えない場合は、3. [Execution] を実行する。
     * 合計作業時間が10分を超える場合は、2.4 Split Mode に移行し、3. [Execution] はスキップする。
   * 2.3 ## 1) Planner（最初に必ず）

     * 追加サービス定義（AzureServices-services-additional.md）を読み、作成対象サービス一覧を抽出する。
     * 各サービスについて、以下を **MicrosoftDocs MCP** で確定する（推測禁止）：

       * 使用すべき `az` コマンド/引数、最小SKU/サーバーレス有無、リージョン制約、作成後に取得すべきURL/ID
       * Azure OpenAI の場合：作成→モデルデプロイの手順と“現時点で利用可能なモデル名”
     * Planner出力（/AGENTS.mdのテンプレ準拠）に、成果物ファイル構成（スクリプト名）と検証方法まで含める。
     * Plannerで概算見積もりを行い、2.2 の分岐に従う。
   * 2.4 ## 2) Split Mode（合計>10分のとき）

     * 10分程度の単位に分割し、各Promptを
       `work/{ユースケースID}/data-azure-additionalservices-deploy-issue-prompt-<番号>.md`
       に日本語で追記する（Parent Issue参照行を含める）。
     * 分割Promptは「Goal/Plan/Dependencies/Parallelism/Risks & Checks/Questions」で統一する。

3. [Execution]作業の実行（[Plan]は含めない）

   * 3.1 ### 3.1 依存ツール準備スクリプトを作成

     * `infra/{ユースケースID}/create-azure-additional-resources-prep.sh`
     * 要件：

       * Linux想定、冪等（再実行OK）、`set -euo pipefail`
       * Azure CLI など必要ツールの導入（MicrosoftDocsで確定した範囲のみ）
       * 秘密情報は扱わない/出力しない
   * 3.2 ### 3.2 追加サービス作成スクリプトを作成

     * 保存先：`infra/{ユースケースID}/create-azure-additional-resources/`
     * ファイル構成（推奨）：

       * `create.sh`（オーケストレーター：各サービス作成を順に呼ぶ）
       * `services/<service>.sh`（サービス別。複数サービスがある場合）
     * 要件：

       * 冪等：既存リソースがある場合は“作成済み判定→必要最小の更新”にする
       * 一時障害：指数バックオフで最大3回リトライ
       * 最小構成：最小SKU/サーバーレス/オートスケール優先（MicrosoftDocsで確定）
       * 出力（後工程で使う）：サービスID、サービス名、Azureサービス名、機能名、機能種類、URL、リージョン
   * 3.3 ### 3.3 Azure MCP でスクリプト実行

     * `prep.sh` → `create.sh` の順で実行する。
     * 実行結果から、カタログに必要な値（ID/URL/リージョン等）を確定する。
   * 3.4 ### 3.4 サービスカタログ更新（冪等）

     * `docs/usecase/{ユースケースID}/service-catalog.md` の「サービス」表を更新する。
     * 列（固定）：

       * サービスID | サービス名 | Azureのサービス名 | 機能名 | 機能の種類 | AzureサービスのURL | リージョン
     * 同じサービス（ID または サービス名）行が既にあれば更新し、重複行は作らない。
   * 3.5 ### 3.5 README更新（最小限）

     * `/README.md` に以下を短く追記する：

       * 機能概要（追加サービスの目的）
       * 起動/実行手順（prep.sh と create.sh の実行、前提条件）
       * 注意（資格情報の扱い、リージョン差異）

4. [Review]

   * 4.1 レビューを3度行う（観点は毎回変える）

     * 目的を達成できているか、整合性が取れているかを点検する。
   * 4.2 各レビューで問題点を10〜50個リストアップし、解決策を立案する

     * 解決策を実行し、成果物に反映する。
   * 4.3 3回のレビュー観点例（固定ではない）

     * レビュー1：要件充足/禁止事項/10分ルール/成果物パスの正しさ
     * レビュー2：冪等性/再実行性/リトライ/資格情報の扱い
     * レビュー3：ドキュメント整合（カタログ/README）/重複行回避/空書き込み対策の適用

5. [Finalize]レビュー後の最終版のみを作成する

   * 5.1 # 最終出力（人間レビュー用の短い要約）

     * 変更点を3行以内で要約：

       1. 何を作った/変えた
       2. どこ（パス）
       3. どう検証した
