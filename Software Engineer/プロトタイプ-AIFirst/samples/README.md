# サンプルプロジェクト - AI活用型ロイヤルティプログラムシステム

## 概要

このフォルダには、**AI活用型ロイヤルティプログラムシステム**の開発プロジェクトのサンプルが格納されています。具体的には、UC-006「生成AI搭載カスタマーサポートチャットボット」を題材に、GitHub Copilot Agentを活用したプロダクトマネジメントからアーキテクチャ設計、実装までの一連の開発プロセスを示す実例です。

本サンプルは、以下の目的で作成されています:

- **GitHub Copilot Agent の活用例**: カスタムエージェント定義を用いた、自動化された開発プロセスの実演
- **要求定義からプロトタイプまでの実例**: ビジネス要求定義から、ドメイン分析、サービス設計、画面設計、データモデル設計までの一貫したドキュメント体系
- **マイクロサービスアーキテクチャの適用例**: DDD（ドメイン駆動設計）とポリグロット永続性を考慮したサービス分割例
- **生成AI活用システムの具体例**: Azure OpenAIを使ったカスタマーサポートの実装イメージ

---

## フォルダー構造

```
samples/
├── .github/
│   └── agents/                      # GitHub Copilot カスタムエージェント定義
│       ├── Arch-micro-ServiceIdentify.md  # マイクロサービス候補抽出エージェント
│       ├── Arch-UI-Detail.md              # 画面定義書作成エージェント
│       └── Dev-WebAzure-UICoding.md       # Web UI実装エージェント
├── data/
│   └── sample-data.json             # UC-006用サンプルデータ
├── docs/
│   ├── business-requirement.md      # ビジネス要求定義書
│   ├── data-model.md                # データモデル設計書
│   ├── domain-analytics.md          # ドメイン分析書
│   ├── screen-list.md               # 画面一覧と画面遷移図
│   ├── service-list.md              # マイクロサービス候補一覧
│   └── usecase-description.md       # ユースケース記述書
└── README.md                        # このファイル
```

---

## 各ファイルの説明

### `.github/agents/` - GitHub Copilot カスタムエージェント定義

GitHub Copilot Agentに作業を依頼するための、カスタムエージェント定義ファイル群です。各エージェントは特定の開発タスクに特化しており、Issueやチャットから呼び出して自動化された作業を実行できます。

#### `Arch-micro-ServiceIdentify.md`
- **目的**: ドメイン分析結果からマイクロサービス候補を抽出し、サービス一覧とコンテキストマップを作成
- **入力**: `docs/usecase/{ユースケースID}/usecase-description.md`, `domain-analytics.md`
- **出力**: `service-list.md` と Mermaid コンテキストマップ
- **主要機能**:
  - ドメイン分析に基づくサービス境界の識別
  - アグリゲート、エンティティ、イベントの抽出
  - データ所有権とストレージ選択の提案
  - べき等性と再試行可能な作業実行

#### `Arch-UI-Detail.md`
- **目的**: 指定ユースケースの全画面について、実装可能な画面定義書を作成
- **入力**: `screen-list.md`, `usecase-description.md`, `service-list.md`, `data-model.md`, `sample-data.json`
- **出力**: `docs/usecase/{ユースケースID}/screen/{画面ID}-description.md`
- **主要機能**:
  - 画面レイアウト・UI/UXの詳細設計
  - アクセシビリティ、セキュリティ考慮事項の記載
  - データ連携の仕様明記
  - 10分超の作業は自動分割

#### `Dev-WebAzure-UICoding.md`
- **目的**: 画面定義書に基づき、1画面ずつUIを実装し、APIクライアント層を整備
- **入力**: `screen-list.md`, `{画面ID}-description.md`, `service-catalog.md`, `sample-data.json`
- **出力**: `app/{ユースケースID}` フォルダ配下のHTML/JavaScript実装
- **主要機能**:
  - HTML5とJavaScript（またはReact等）でのUI実装
  - APIクライアント層の設計と実装
  - 進捗管理と段階的実装
  - 大きいファイルの書き込み失敗対策

---

### `data/` - サンプルデータ

#### `sample-data.json`
- **内容**: UC-006「生成AI搭載カスタマーサポートチャットボット」のサンプルデータ
- **含まれるエンティティ**:
  - ConversationSession（会話セッション）
  - Message（メッセージ）
  - ConversationContext（会話コンテキスト）
  - Intent（インテント）
  - KnowledgeBaseArticle（知識ベース記事）
  - Agent（カスタマーサポートエージェント）
  - EscalationCriteria（エスカレーション基準）
- **用途**: 
  - UI実装時のモックデータ
  - 開発・テスト環境での動作確認
  - データモデルの理解促進

---

### `docs/` - プロジェクトドキュメント

#### `business-requirement.md`
- **概要**: ロイヤルティプログラムの現状分析と戦略的方向性を示すビジネス要求定義書
- **主要セクション**:
  - Executive Summary（要約）
  - Company Overview（企業概要）
  - As-Is Analysis（現状分析）- PEST分析、Porter 5 Forces分析
  - ロイヤルティプログラムの定義と特徴
  - 顧客ペルソナ
  - 生成AI活用事例と今後の可能性
- **特徴**: 
  - 過去10年間のロイヤルティプログラム市場の分析
  - 生成AI活用による差別化戦略の提案
  - データに基づいた現状把握と課題抽出

#### `usecase-description.md`
- **概要**: UC-006「生成AI搭載カスタマーサポートチャットボット」の詳細なユースケース記述
- **主要セクション**:
  - ユースケース名、ID、目的
  - アクター（主要/副次的）
  - ステークホルダーと関心事
  - 前提条件、終了条件（成功時/失敗時）
  - 基本フロー、代替フロー、例外フロー
  - ビジネスルール、非機能要件
- **用途**: プロダクトマネジメント、開発の基礎資料

#### `domain-analytics.md`
- **概要**: UC-006のドメイン分析書（DDD: ドメイン駆動設計の基礎）
- **主要セクション**:
  - ユビキタス言語（共通語彙の定義）
  - 境界づけられたコンテキスト（Bounded Context）の識別
  - アグリゲート、エンティティ、値オブジェクトの抽出
  - ドメインイベントの定義
  - 非機能要件（SLO/SLA）
- **用途**: マイクロサービス設計の入力、サービス境界の決定

#### `service-list.md`
- **概要**: マイクロサービスアーキテクチャとして実装するためのサービス候補一覧
- **含まれるサービス例**:
  - SVC-006-001: 会話管理サービス
  - SVC-006-002: AI推論サービス
  - SVC-006-003: 知識管理サービス
  - SVC-006-004: エージェント管理サービス
  - SVC-006-005: 分析・モニタリングサービス
- **各サービスの記載内容**:
  - 一次責務（SRP: 単一責任の原則）
  - 非責務（明示的に担当しないこと）
  - ドメインモデル（エンティティ、イベント、不変条件）
  - データ所有・ストレージ選択
  - API設計の方向性
  - 技術スタック候補
- **用途**: アーキテクチャ設計、実装計画の立案

#### `screen-list.md`
- **概要**: UC-006で必要な画面の一覧と画面遷移図
- **含まれる画面例**:
  - **顧客向け画面**:
    - SCR-006-001: ポータル画面
    - SCR-006-002: チャット画面
    - SCR-006-003: 会話履歴画面
    - SCR-006-004: 満足度評価画面
  - **管理者向け画面**:
    - SCR-006-005: エージェントダッシュボード
    - SCR-006-006: エージェントチャット画面
    - SCR-006-007: 知識ベース管理画面
    - SCR-006-008: AIエンジニア設定画面
    - SCR-006-009: モニタリング・分析画面
- **画面遷移図**: Mermaid形式のフローチャート
- **用途**: UI/UX設計、画面定義書作成の基礎資料

#### `data-model.md`
- **概要**: UC-006のデータモデル設計書（詳細なエンティティ定義）
- **設計原則**:
  - マイクロサービスアーキテクチャにおけるデータ所有権
  - 最終的整合性（Eventual Consistency）
  - データ品質とセキュリティ（APPI、GDPR準拠）
- **主要エンティティ**:
  - 会話管理関連（ConversationSession, Message, ConversationContext）
  - AI推論関連（Intent, ExtractedEntity, PromptTemplate, InferenceLog）
  - 知識管理関連（KnowledgeBaseArticle, ArticleVersion）
  - エージェント管理関連（Agent, AgentMetrics）
  - エスカレーション関連（EscalationCriteria, EscalationDecision）
- **各エンティティの記載内容**:
  - 属性（フィールド名、型、制約）
  - リレーション
  - インデックス設計
  - 暗号化対象フィールド
  - データ保持期間
- **用途**: データベース設計、API設計、実装の詳細仕様

---

## 使い方

### 1. GitHub Copilot Agent を使った開発プロセスの実行

このサンプルを参考に、新しいユースケースで同様の開発プロセスを実行できます:

1. **要求定義の作成**: `business-requirement.md` を参考に、ビジネス課題と目標を定義
2. **ユースケース記述**: `usecase-description.md` を参考に、ユースケースを詳細化
3. **ドメイン分析**: `Arch-micro-ServiceIdentify.md` エージェントを呼び出してサービス候補を抽出
4. **画面設計**: `Arch-UI-Detail.md` エージェントで画面定義書を作成
5. **実装**: `Dev-WebAzure-UICoding.md` エージェントでUIコードを生成

### 2. サンプルデータの活用

`data/sample-data.json` を参考に、以下の用途に活用できます:

- UI実装時のモックデータとして使用
- APIのレスポンス例として参照
- テストケース作成の基礎データ

### 3. ドキュメントの再利用

`docs/` 配下のドキュメントは、テンプレートとして再利用可能です:

- 自社のロイヤルティプログラムやカスタマーサポートシステムに適用
- セクション構成や記載内容を参考に、独自のドキュメントを作成
- エージェント定義の入力・出力フォーマットとして活用

---

## 関連リンク

- [GitHub Copilot Coding Agent](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/)
- [GitHub Copilot へのタスク割り当て](https://docs.github.com/ja/enterprise-cloud@latest/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot)
- [プロトタイプ-AIFirst - 親フォルダのREADME](../README.md)
- [ProductManagement-Documentation.md](../ProductManagement-Documentation.md) - ユースケース作成の手順

---

## ライセンス

このサンプルは、親リポジトリのライセンス（[LICENSE](../../../LICENSE)）に従います。
