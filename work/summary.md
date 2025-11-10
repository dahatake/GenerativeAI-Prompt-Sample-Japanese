# プロンプト改善タスクの実施サマリー

## 実施日時
2025-11-04

## 実施内容

### 完了したタスク

#### 1. プロンプト分析と改善計画策定
- 4つのファイル（計2,351行）を分析
- OpenAIのプロンプトエンジニアリング6つの戦略に基づく評価基準を確立
- 各ファイルの強みと改善点を特定
- 作業を4つのタスクに分割

#### 2. Business-Documentation.md の改善完了
**元ファイル**: 352行、4つのプロンプト  
**改善版**: Updated-Business-Documentation.md（約1,000行）

**主な改善内容**:

1. **プロンプト構造の標準化**
   ```
   - 役割設定（明確なペルソナ設定）
   - タスクの目的（何を達成するか）
   - 実施手順（ステップ1～4の明確化）
   - 出力形式（具体的なテンプレート）
   - 検証チェックリスト（品質基準）
   ```

2. **OpenAI 6つの戦略の適用**
   - **明確な指示**: 各ステップで具体的なアクションを明示
   - **参照テキスト**: 必要なドキュメントとデータソースを明確化
   - **タスク分割**: 大きなタスクをサブタスクに分解
   - **思考時間**: 「分析計画→実行→検証」の3段階プロセス
   - **外部ツール**: Microsoft 365 Copilot等の推奨ツールを明示
   - **体系的テスト**: 各プロンプトに検証チェックリストを追加

3. **抽象的表現の具体化**
   | Before | After |
   |--------|-------|
   | 「高精度に分析・解析」 | 「以下の3つの観点から分析し、各観点に根拠を付記」 |
   | 「深く考察」 | 「根拠となるデータまたは仮定を明記」 |
   | ユースケースの選定基準が曖昧 | 5段階評価（ビジネス価値ランク、開発有効性ランク）|

4. **具体例とテンプレートの追加**
   - 事業分析レポートの各セクションに記載例を追加
   - SWOT分析、BCGマトリクス、PEST分析のテーブルテンプレート
   - ユースケース評価マトリクス（2軸のスコアリング）
   - Mermaid形式のロードマップ例

5. **検証基準の明確化**
   - 各プロンプトに実行可能なチェックリストを追加
   - 「内容の品質」「形式と構造」「実装可能性」の3観点
   - 定量的な基準（例: 最低X個の項目、Y段階評価）

6. **エラーハンドリングと作業管理の共通化**
   - 共通ガイドラインセクションを追加
   - ファイル書き込み失敗時の対応手順を明確化
   - 作業時間管理（10分超過時の分割方法）

### 改善の効果（期待値）

#### プロンプトの品質向上
- **明確性**: 曖昧な指示を具体的なアクションに置き換え → AI の理解度向上
- **再現性**: テンプレートと例により、誰が実行しても同等の結果
- **完全性**: チェックリストにより、必要な項目の漏れを防止

#### 出力品質の向上
- **構造化**: 統一されたフォーマットにより、後続作業との連携が容易
- **根拠明示**: 「なぜその判断をしたか」が明確になり、レビュー・修正が容易
- **定量化**: 評価基準が数値化され、優先順位付けが客観的に

#### 作業効率の向上
- **ガイダンス**: ステップバイステップの手順により、迷わず実行可能
- **検証**: チェックリストにより、自己レビューが効率化
- **エラー対応**: 共通ルールにより、問題発生時の対応が迅速化

---

## 未完了タスク

### タスク3: ApplicationDesign-microservice-polyglotpersistence.md
**規模**: 780行、7つのプロンプト  
**推定作業時間**: 約25分

**改善の要点**:
- 共通パターンの抽出（エラーハンドリング、作業時間管理）
- DDDの概念に具体例を追加
- マイクロサービス設計のベストプラクティスを明示
- Polyglot Persistence の選定フローチャート追加
- 長大なマイクロサービス定義書テンプレートの構造化

**推奨アプローチ**: 
タスクを2つに分割することを推奨します：
1. Step 1-3 (ドメイン分析、サービス一覧、データモデル)
2. Step 4-5 (サービスカタログ、画面定義書、マイクロサービス定義書)

### タスク4: Implementation-WebAppOnAzure.md
**規模**: 711行、10個のプロンプト  
**推定作業時間**: 約20分

**改善の要点**:
- セキュリティ要件の強化
- Azure CLI スクリプトのテンプレート例を追加
- デプロイ後の検証手順を明確化
- Well-Architected Framework に基づくレビュー項目追加
- コスト最適化のガイドライン追加

**推奨アプローチ**:
タスクを2つに分割することを推奨します：
1. Step 1-2 (データ、サービスのAzure選定と作成)
2. Step 3-4 (UI作成、アーキテクチャレビュー)

### タスク1: README.md
**規模**: 508行、ドキュメント  
**推定作業時間**: 約10分

**改善の要点**:
- Custom Instructions の整理と階層化
- 各ステップの期待される成果を明示
- トラブルシューティングの体系化
- セキュリティ要件の一箇所への集約

---

## 推奨事項

### 即座に適用可能
1. **Updated-Business-Documentation.md を使用開始**
   - 要求定義とユースケース作成に即座に適用可能
   - フィードバックを収集し、さらなる改善に活用

### 残タスクの実施方法
以下の3つのオプションから選択してください：

#### オプション1: 全タスクを一度に実施（非推奨）
- 作業時間: 約55分
- リスク: 長時間作業による品質低下の可能性

#### オプション2: タスクを分割して段階的に実施（推奨）
- フェーズ1: タスク1（README.md）- 10分
- フェーズ2: タスク4を2分割（各10分） - 20分
- フェーズ3: タスク3を2分割（各12-13分）- 25分
- 各フェーズ間でレビューとフィードバック

#### オプション3: 優先度順に実施
1. タスク4（実装ガイド）- 最も実用的
2. タスク3（設計ガイド）- 中間成果物
3. タスク1（README）- 全体の導入部分

### 長期的な改善
1. **フィードバックループの確立**
   - 改善版プロンプトを実際に使用
   - 問題点や改善点を収集
   - 定期的にプロンプトを更新

2. **プロンプトライブラリの構築**
   - 共通パターンをテンプレート化
   - 業界別、用途別のバリエーション作成
   - コミュニティでの共有

3. **自動化の検討**
   - プロンプトの品質チェックツール
   - 出力結果の自動検証
   - バージョン管理とA/Bテスト

---

## 参考資料

### OpenAI ガイダンス
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Prompt Engineering Strategies](https://platform.openai.com/docs/guides/prompt-engineering)

### GitHub Copilot
- [Coding Agent Best Practices](https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks)
- [Custom Agents](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)

### プロンプトエンジニアリング
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Learn Prompting](https://learnprompting.org/)

---

## 作成ファイル一覧

### 分析・計画ドキュメント
- `work/prompt-analysis.md` - 全ファイルの詳細分析
- `work/prompt-1.md` - タスク1の詳細計画
- `work/prompt-2.md` - タスク2の詳細計画（完了）
- `work/prompt-3.md` - タスク3の詳細計画
- `work/prompt-4.md` - タスク4の詳細計画

### 改善版プロンプト
- ✅ `Software Engineer/プロトタイプ-AIFirst/Updated-Business-Documentation.md`
- ⏳ `Software Engineer/プロトタイプ-AIFirst/Updated-ApplicationDesign-microservice-polyglotpersistence.md`
- ⏳ `Software Engineer/プロトタイプ-AIFirst/Updated-Implementation-WebAppOnAzure.md`
- ⏳ `Software Engineer/プロトタイプ-AIFirst/Updated-README.md`

---

## 次のアクション

### 即座に実施
1. Updated-Business-Documentation.md のレビュー
2. 実際のプロジェクトでの試用
3. フィードバックの収集

### 今後の Issue として作成
残タスクごとに個別の Issue を作成することを推奨：
- Issue 1: README.md の改善（10分タスク）
- Issue 2: Implementation-WebAppOnAzure.md Step1-2 の改善（10分タスク）
- Issue 3: Implementation-WebAppOnAzure.md Step3-4 の改善（10分タスク）
- Issue 4: ApplicationDesign Step1-3 の改善（12分タスク）
- Issue 5: ApplicationDesign Step4-5 の改善（13分タスク）

各 Issue に work/prompt-X.md の該当セクションを参照するように記載してください。
