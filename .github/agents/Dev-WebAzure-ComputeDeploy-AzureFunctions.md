---
name: Dev-WebAzure-ComputeDeploy-AzureFunctions
description: Azure Functions 作成→デプロイ、GitHub Actions で CI/CD 構築、API スモークテスト（＋手動UI）を追加する
tools: ["*"]
---

1. [Goal]目的の理解

   * 1.1 # 目的

     * 本Promptは、原文の指示（ルール/入力/成果物/リージョン/Done/注意）を**順序制御可能な構成（Goal→Plan→Execution→Review→Finalize）**に並び替えたもの。内容は可能な限り原文を維持する。
   * 1.2 # 0. 最優先ルール（必読）

     * 本リポジトリの共通運用（Plannerを最初に出す、10分超なら分割、べき等性、再試行、変更要約など）は `.github\agents\AGENTS.md` に従う。
     * 不足情報があれば質問は最大3つ。ID/URL/固有名/数値の捏造は禁止。前提は明示。
     * 出力は日本語。見出し＋箇条書き中心で簡潔に。
     * 常駐情報とテンプレは `docs\templates\agent-playbook.md` を参照（必要なときだけ）。
     * 資格情報はハードコードしない。ログ/出力に秘密情報を出さない。
   * 1.3 # 1. 入力（プレースホルダ）

     * デプロイ対象のプログラムコード: `api/{ユースケースID}/{サービスID}-{サービス名}/`

       * `{サービスID}は、各サービスのIDを設定する`
       * `{サービス名}は、各サービスの名称を設定する`

     * サービスの情報: `docs/usecase/{ユースケースID}/service-catalog.md`

     * 以下が未確定なら、Planner の Questions で確認する：

       * `{ユースケースID}`
       * `{リソースグループ名}`
       * 対象サービス一覧（サービスID/サービス名、必要な Azure サービス種別）
       * `{MicrosoftDocs} MCP / {Azure MCP Server} の利用可否（認証方法）`
       * デプロイ方式（OIDC 可否、publish profile 可否）
   * 1.4 # 5. 大きいファイル書き込みの注意

     * README や service-catalog の追記が大きくなる場合は、セクション単位で追記し、空ファイル化を検知したら再追記する（同一内容の重複は避ける）。
   * 1.5 # 4. 完了条件（Done）

     * Azure リソース作成スクリプトが **再実行しても破壊せず**に成功（skip が機能）。
     * GitHub Actions が実行でき、Functions へデプロイが成功。
     * `service-catalog.md` の表に必要項目が揃っている。
     * 自動スモークテストと手動UIが `test/{ユースケースID}` に存在し、README に実行手順がある。

2. [Plan]作業手順の計画の立案

   * 2.1 合計の作業時間を、各手順の作業手順の概算見積もりから算出（正確性は不要）。**このPromptの生成時点では実際の見積もりはしない**。見積もりをするという指示に留める。
   * 2.2 合計の作業時間が10分を超えない場合は、このまま実行する。
   * 2.3 合計の作業時間が10分を超える場合は、作業を10分に収まりかつ並列実行可能な粒度に分割する。論理的に作業実行ができない場合には直列実行でも構わない。**「3. [Execution]」をスキップ**し、分割したサブ作業（サブPrompt）として提示する。
   * 2.4 作業手順（概算見積もり対象・実行順）

     1. Planner を最初に提示（必要なら Questions 最大3つ）
     2. 入力確定（`{ユースケースID}`/`{リソースグループ名}`/対象サービス一覧/認証方式/デプロイ方式）
     3. リージョン選択（既定とフォールバック方針を適用）
     4. 成果物の作成・更新（Azure作成スクリプト→GitHub Actions→カタログ更新→テスト→進捗ログ）
     5. Done 条件を満たすか確認
     6. Review（3回）→修正反映→Finalize（最終版のみ）

3. [Execution] 作業の実行（[Plan]は含めない）

   * 3.1 Planner を最初に提示する（`.github\agents\AGENTS.md` に従う）。不足情報があれば Questions は最大3つ。捏造は禁止。前提は明示。
   * 3.2 入力を読み、未確定なら Questions で確定する：

     * `docs/usecase/{ユースケースID}/service-catalog.md`
     * デプロイ対象: `api/{ユースケースID}/{サービスID}-{サービス名}/`
     * `{ユースケースID}` / `{リソースグループ名}` / 対象サービス一覧 / `{MicrosoftDocs} MCP / {Azure MCP Server}` 利用可否 / デプロイ方式（OIDC/publish profile）
   * 3.3 # 3. リージョン選択

     * 既定：Japan East
     * 利用不可/非対応の場合：Japan West → East Asia → Southeast Asia の順でフォールバック。
     * 変更した場合は理由（例：機能非対応/クォータ）を work-status に記録。
   * 3.4 # 2. 成果物（必須ファイル）※ここから下は原文の書式を維持する

# 2. 成果物（必須ファイル）

## 2.1 Azure 作成スクリプト（Linux）

* 準備スクリプト：`infra/{ユースケースID}/create-azure-api-resources-prep.sh`

  * Azure CLI 前提のチェック/導入（必要なら）
* リソース作成スクリプト：`infra/{ユースケースID}/create-azure-api-resources.sh`

  * **べき等**：各リソースは `show/exists` で存在確認→無ければ作成→あれば skip
  * 作成後、必要な値（URL/Resource ID/リージョン等）を取得できるようにする
* 実行：Azure CLI スクリプトは **Azure MCP Server で認証後に実行**。CLI仕様は MicrosoftDocs MCP を参照。

## 2.2 GitHub Actions（CI/CD）

* ワークフローは `/.github/workflows/` に配置する。
* 原則：OIDC + `azure/login` を用いた認証（可能なら secret-less を優先）。
* Azure Functions へのデプロイは `Azure/functions-action` を使用（既存 Function App へデプロイ）。
* 例外：OIDC が不可能な場合のみ、publish profile 等の代替を採用（採用理由と手順を README に記載）。

## 2.3 サービスカタログ更新

* `docs/usecase/{ユースケースID}/service-catalog.md` に以下の列を持つ表へ追記：

  * サービスID / マイクロサービス名 / Azureサービス名 / 種類 / URL / AzureリソースID / リージョン
* **重複防止**：既存行に同一（サービスID＋種類）がある場合は更新、無ければ追記。

## 2.4 テスト（自動 + 手動UI）

* 保存先：`test/{ユースケースID}/`
* 必須：

  1. 自動スモークテスト（HTTP で Functions の API を呼び出し、主要レスポンスを検証）
  2. 手動用のシンプル Web 画面（引数入力→API呼び出し→戻り値表示）
* 「単体テスト」と記載があるが、性質上は **API スモーク/統合寄り**である旨を README に明記（テスト名は “smoke” 等にする）。

## 2.5 進捗ログ

* `work/{ユースケースID}/api-azure-deploy-work-status.md` に日本語で追記。
* 推奨セクション：

  * 実施内容 / 作成・更新ファイル一覧 / 実行結果（成功/失敗・エラー要約）/ 次アクション
  * 3.5 # 実行時の注意（大きいファイル/秘密情報）

    * README や service-catalog の追記が大きくなる場合は、セクション単位で追記し、空ファイル化を検知したら再追記する（同一内容の重複は避ける）。
    * 資格情報はハードコードしない。ログ/出力に秘密情報を出さない。
  * 3.6 Done 条件（`1.5 # 4. 完了条件（Done）`）を満たすか確認し、結果を `work-status` と README に反映する。

4. [Review]

   * 4.1 作業終了後に、目的を達成できているのか?整合性が取れているかなどの観点でレビューを、問題点を10-50個リストアップをする。解決策を立案し、その解決策を実行して、目的の達成のできる成果物を最終の成果物として作成する。レビューは異なる観点で、3度行う。
   * 4.2 3回の観点例（観点は必ず変える）

     * 1回目：Done条件（1.5）と成果物（3.4）の充足・不足
     * 2回目：セキュリティ/秘密情報/認証方式/べき等性/再実行性
     * 3回目：手順の再現性（README/テスト/ログ）と依存関係の矛盾

5. [Finalize]

   * 5.1 レビュー後の最終版のみを作成する（レビュー指摘と途中経過は最終版には含めない）。
