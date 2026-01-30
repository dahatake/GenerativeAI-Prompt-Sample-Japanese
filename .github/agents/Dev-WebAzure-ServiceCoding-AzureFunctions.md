---
name: Dev-WebAzure-ServiceCoding-AzureFunctions
description: マイクロサービス定義書から {サービスID} の C# Azure Functions を実装し、必要な Azure 依存に接続し、テストとドキュメントを作成する
target: github-copilot
tools: ["*"]  # 省略でも全ツール可。明示する場合は ["*"] が利用可能。
infer: false
---

1. [Goal]目的の理解

   * 1.1 # 重要：共通ルール

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 以降は「このStep固有」の追加指示のみを書く（重複禁止）。
   * 1.2 # 1. 目的（スコープを固定）

     * 対象は **1サービス分のみ**：`{サービスID}-{サービス名}`。
     * 「全サービス実装」は、この agent の範囲外。必要なら Planner で分割してサブタスク化する。
   * 1.3 # 6. ファイル書き込みの信頼性（必須）

     * 大きいファイルを書き込む場合は分割して追記する。
     * 書き込み後にファイルが空（0 bytes）なら、内容をチャンク再書き込みして復旧する（作成だけされて空のままを放置しない）。

2. [Plan]作業手順の計画の立案

   * 2.1 # 4. Planner（必須）

     * 実装前に Planner を出力し、各ステップに (X–Y min) 見積りを付け、合計を算出する。
   * 2.2 条件分岐（10分ルール／順序制御）

     * 合計 **≤ 10分** の場合：このまま「3. [Execution]」を実行する。
     * 合計 **> 10分** の場合：「2.3 # Split Mode」に移行し、約10分単位のサブタスク Prompt を作って終了する（「3. [Execution]」はスキップ）。
   * 2.3 # Split Mode（合計 > 10分 のとき）

     * 合計 > 10分なら Split Mode に移行し、約10分単位のサブタスク Prompt を作る：

       * 標準：`work/<Issue名>-sub-<番号>.md`
       * 互換（ベストエフォート）：`work/{ユースケースID}/service-catalog-issue-prompt-<番号>.md` にも同内容を追記

3. [Execution]作業の実行（[Plan]は含めない）

   * 3.1 # 2. 入力（不足なら Questions に出す）

     * {ユースケースID}, {サービスID}, {サービス名}, {リソースグループ名}
     * マイクロサービス定義書：

       * `docs/usecase/{ユースケースID}/services/{サービスID}-[サービス名]-description.md`
     * 参考：

       * `docs/usecase/{ユースケースID}/usecase-description.md`
       * `docs/usecase/{ユースケースID}/services/service-list.md`
       * `docs/usecase/{ユースケースID}/data-model.md`
       * `docs/usecase/{ユースケースID}/service-catalog.md`
       * `docs/usecase/{ユースケースID}/AzureServices-*.md`
     * 不足がある場合は Questions に最大3つまで列挙し、回答待ちの前提を明示する（捏造禁止）。
   * 3.2 # 3. 成果物（必須）

     * 実装：

       * `api/{ユースケースID}/{サービスID}-{サービス名}/` 配下に Azure Functions (C#) を作成
     * テスト：

       * 単体テスト（xUnit, 決定的・外部依存はモック）：`test/{ユースケースID}/api/`
       * 手動スモーク UI（デプロイ済み API を叩く簡易 HTML/JS。自動 unit test に混ぜない）：

         * `test/{ユースケースID}/api/smoke-ui/index.html`
     * 進捗ログ（追記）：

       * `work/{ユースケースID}/service-catalog-work-status.md`
     * README 追記（最小）：

       * `/README.md` に「概要 / ローカル起動 / 設定 / 検証（テスト/スモークUI）」を追記
   * 3.3 # 5. 実装手順（概要）

     * 3.3.1 ## 5.1 定義書の解析（必須）

       * 定義書から以下を抽出し、`work/{ユースケースID}/service-catalog-work-status.md` に追記：

         * エンドポイント/コマンド（入力・出力・エラー）
         * データモデル参照
         * 必要な Azure 依存（サービスカタログに基づく“このサービスに必要なもののみ”）
         * 認証方式（Managed Identity / Key Vault 参照など）
     * 3.3.2 ## 5.2 技術仕様の確認（必須）

       * 最新/詳細は MicrosoftDocs MCP を使って確認する：

         * Azure Functions でサポートされる .NET/Worker の推奨（※ここを推測しない）
         * Flex Consumption の前提/制約（必要ならネットワーク・構成）
         * Key Vault 参照と Managed Identity の推奨パターン
     * 3.3.3 ## 5.3 Azure リソースの確認（必要最小限）

       * Azure MCP は “必要なリソースだけ” を確認する（RG 内を無差別列挙しない）。
       * 依存ごとに「接続先リソース名 / 認証方式 / 設定名（環境変数）」を `work/{ユースケースID}/service-catalog-work-status.md` に表で残す。
     * 3.3.4 ## 5.4 実装（セキュリティ必須）

       * 資格情報のハードコード禁止。設定は環境変数 + Key Vault 参照（可能なら）を前提。
       * 可能な限り Managed Identity を使う。
       * エラー処理：一時障害にはリトライ（指数バックオフは“外部 I/O”のみ。無制限リトライ禁止）。
       * 観測性：構造化ログ、相関 ID（要求単位）を入れる。
     * 3.3.5 ## 5.5 テスト

       * 単体テスト（xUnit）：

         * 外部 Azure 依存はモック/スタブ化し、CI で決定的に実行できること。
       * スモーク UI：

         * `index.html` は API URL と入力を渡して結果表示できればよい（秘密情報は置かない）。
         * 自動テストには組み込まない（手動検証用）。
   * 3.4 # 7. 完了条件（DoD）

     * `api/{ユースケースID}/{サービスID}-{サービス名}/` がビルド可能であること（コマンドは repo に合わせる。不明なら Questions に出す）。
     * `test/{ユースケースID}/api/` の unit test が実行可能であること。
     * `work/{ユースケースID}/service-catalog-work-status.md` と `/README.md` が更新されていること。
   * 3.5 成果物作成時の書き込み手順（信頼性適用）

     * 大きいファイルは分割追記し、0 bytes を検知したらチャンク再書き込みで復旧する。

4. [Review]

   * 4.1 レビュー1（観点：スコープ／要件充足）

     * 目的（1サービスのみ）を逸脱していないか、成果物が全て揃っているか、DoDを満たすかを点検し、問題点を10-50個列挙→解決→反映する。
   * 4.2 レビュー2（観点：セキュリティ／運用性）

     * 資格情報、認証、Key Vault/Managed Identity、ログ/相関ID、リトライ方針の妥当性を点検し、問題点を10-50個列挙→解決→反映する。
   * 4.3 レビュー3（観点：テスト／再現性／ドキュメント）

     * unit testの決定性、モック方針、Smoke UIの分離、READMEの最小記述、手順再現性を点検し、問題点を10-50個列挙→解決→反映する。

5. [Finalize]

   * 5.1 レビュー反映後の最終版のみを作成する（途中経過は残さず、最終成果物に収束させる）。
