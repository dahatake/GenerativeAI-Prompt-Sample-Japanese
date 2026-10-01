# 第 5 章 クラウド展開（Azure で 画面 + API + データ を連携）

**ゴール**: ローカルで動く TaskBoard を Azure に載せ、**Static Web Apps（UI）→ Container Apps（API）→ Azure Database for PostgreSQL** の構成で動かす。IaC 化し、CD で再現可能にする。

> 他クラウドの場合は「静的ホスティング / コンテナ実行基盤 / マネージド PostgreSQL / シークレット管理 / ログ基盤」に読み替える。Azure のコマンド・Bicep の最新仕様は公式ドキュメントで確認し、Agent に Azure MCP / ドキュメント検索ツールがあれば有効化すると精度が上がる。

## 5.1 講義: クラウド化の設計ポイント

| 観点 | 方針 |
|---|---|
| 構成 | UI: Static Web Apps / API: Container Apps / DB: PostgreSQL Flexible Server |
| 設定 | 環境変数 + Key Vault 参照。コードに秘密を置かない |
| 認証 | API → DB は可能なら **Managed Identity**（Entra 認証）。難しければ Key Vault 経由のパスワード |
| 環境 | `dev` / `prod` を IaC のパラメータで分離 |
| 可観測性 | Application Insights / Log Analytics、`/healthz` を用意 |
| コスト | dev は最小 SKU、**使い終わったら `azd down` / リソースグループ削除** |
| ネットワーク | 本番相当は Private Endpoint / VNet。ハンズオンでは簡略化し、差分を ADR に記録 |

## 5.2 ハンズオン A: 仕様と準備（20 分）

`docs/spec/S-004-cloud-deploy.md`

```markdown
# S-004 クラウド展開
## 受け入れ基準
- API が /healthz で 200 を返す（DB 接続確認を含む /readyz も）
- UI から API 経由でタスク追加・取得ができる（クラウド上）
- インフラは infra/ の IaC から空の RG に再現できる
- シークレットがリポジトリ/ログに出ない
- main へのマージで CD が dev に自動デプロイされる
## スコープ外
カスタムドメイン、WAF、マルチリージョン
```

前提: Azure サブスクリプション（**検証用**）、`az` / `azd` CLI、`az login`。

## 5.3 ハンズオン B: コンテナ化（30 分）

```text
apps/api 用の本番向け Dockerfile(マルチステージ, 非 root, .dockerignore 付き)を作成し、
ローカルで docker build / run して /healthz を確認。/healthz と /readyz を追加し、
SIGTERM で graceful shutdown するようにして。
```

## 5.4 ハンズオン C: IaC の生成（60 分）

```text
@docs/spec/S-004-cloud-deploy.md
Azure Developer CLI (azd) 構成と Bicep で、次を infra/ に作成して計画も示して:
Log Analytics + Application Insights, Container Apps Environment, Container App(api,
ユーザー割り当て Managed Identity), Container Registry, PostgreSQL Flexible Server(dev 最小 SKU),
Key Vault, Static Web App(web)。
リソース名は命名規則とパラメータ化、タグ(env, owner)付与、パブリック公開は最小限。
まず what-if で確認できる状態にして。デプロイはまだ実行しない。
```

人間のレビュー観点:

- [ ] 想定外に高額な SKU / 冗長構成が無い
- [ ] PostgreSQL のファイアウォールが `0.0.0.0/0` 全開になっていない
- [ ] シークレットが Bicep パラメータの平文/出力に出ていない
- [ ] RBAC は最小権限（Key Vault Secrets User など）
- [ ] 診断ログが Log Analytics に送られる

## 5.5 ハンズオン D: デプロイと動作確認（40 分）

```powershell
azd init        # 既存構成を使用
azd provision --preview   # 変更プレビュー
azd up          # 初回デプロイ
```

1. API の FQDN で `/healthz`, `/readyz` を確認
2. Web の URL から画面操作 → タスク追加
3. Application Insights の Live Metrics / ログでリクエストを確認
4. 失敗時は **ログ（`az containerapp logs show` など）を Agent に渡して**原因分析させる:

```text
以下は Container App のログです。起動に失敗する根本原因の仮説を可能性順に挙げ、
確認手順(コマンド)を示して。修正は私が確認してから実施。 <ログ貼り付け>
```

## 5.6 ハンズオン E: CD（OIDC）（30 分）

```text
GitHub Actions で main へのマージ時に dev へ azd deploy する workflow を作成。
Azure 認証は OIDC フェデレーション(長期シークレット不使用)。
prod は手動承認(environment protection)付きの別ジョブに。
```

## 5.7 つまずきポイント

| 症状 | 対処 |
|---|---|
| UI から API に届かない(CORS) | API の許可 Origin に Web の URL のみ設定。Web 側の API URL はビルド時/設定で注入 |
| API が DB に接続できない | FW/ネットワーク、接続文字列、Managed Identity のロール付与を確認 |
| コスト超過 | 検証後 `azd down --purge`。Cost Management で予算アラートを設定 |
| Agent がリソースを勝手に作る/消す | **本番サブスクリプションの認証を Agent に渡さない**。what-if → 人が承認 → 実行 |

## 5.8 完了チェック

- [ ] クラウド上で 画面→API→DB が動作する
- [ ] IaC から再現可能（`azd down` → `azd up`）
- [ ] CD が動き、シークレットは Key Vault/OIDC で管理
- [ ] ログ/メトリクスを確認できる。検証環境を片付けた

---

## 動作確認で判明した注意点(実機検証済み)

**検証範囲**: Azure(Container Apps + PostgreSQL Flexible Server + Static Web Apps + ACR)に `az deployment group create` で Bicep をデプロイし、ブラウザの E2E(SWA → ACA → PostgreSQL)が成功した。**`azd up` / GitHub Actions の OIDC デプロイ / Entra 認証は未検証**。

- `azd auth login` が必要。`azd config set auth.useAzCliAuth true` を使っても、MFA が必要なテナントがあると全テナント列挙で失敗することがある。その場合は `az deployment group create`、`az acr login` + `docker push`、`az containerapp update`、`npx @azure/static-web-apps-cli deploy --deployment-token <az staticwebapp secrets list の値>` で代替できる。変更前の確認は `az deployment group what-if`。
- 再プロビジョニングで Container App のイメージがプレースホルダーに戻る問題: `apiExists` パラメータ(`main.parameters.json` で `${SERVICE_API_RESOURCE_EXISTS=false}`)と、既存イメージを取得する `fetch-image.bicep` モジュールを分けて使う。同名の `existing` リソースを main.bicep 内に置くと循環依存になる。
- 組織ポリシーで Key Vault の `publicNetworkAccess` が強制的に Disabled になる環境では、Container Apps からのシークレット参照が失敗する(「unable to fetch secret」)。Bicep に `useKeyVault`(既定 false)を設け、既定では ACA のシークレットに DB 接続文字列を入れる。Key Vault を使う場合は Private Endpoint が必要。Key Vault はソフトデリートされ、削除後も名前が予約されるため `az keyvault purge` が必要。
- PostgreSQL 接続文字列は `sslmode=require` だと pg が警告を出す。`sslmode=verify-full` を使う(Azure の公開 CA で動作)。
- PostgreSQL ファイアウォールの 0.0.0.0-0.0.0.0 は「Azure サービスからの接続を許可」の意味で、インターネット全体ではない。本番は Private Endpoint を推奨。
- Dockerfile のビルドコンテキストはリポジトリルート。`.dockerignore` で `apps/web/package.json` を除外しない(`apps/web/*` + `!apps/web/package.json`)。コンテナは非 root で実行する。
- Web の `VITE_API_BASE` はビルド時に `apps/web/.env.production` へ書く(azure.yaml の `prepackage` フック)。`.env.production` と `.azure` は `.gitignore` に追加する。
- Container Apps の scale-to-zero は最初のリクエストが遅い。
- 検証後は不要なリソースを必ず削除する(`az group delete` または個別削除)。
