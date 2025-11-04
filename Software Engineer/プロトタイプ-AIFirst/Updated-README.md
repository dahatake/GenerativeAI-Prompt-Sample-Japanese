# Updated Prompt Files - 改善版プロンプトファイル

このディレクトリには、OpenAIのプロンプトエンジニアリングガイドに基づいて改善されたプロンプトファイルが含まれています。

## 📂 ファイル一覧

### ✅ 完了
- **Updated-Business-Documentation.md** - 要求定義とユースケース作成のガイド

### ⏳ 作成予定
- Updated-README.md - プロトタイプ開発のメインガイド
- Updated-ApplicationDesign-microservice-polyglotpersistence.md - マイクロサービス設計ガイド
- Updated-Implementation-WebAppOnAzure.md - Azure実装ガイド

## 🎯 改善のポイント

### OpenAI プロンプトエンジニアリング 6つの戦略

すべての改善版プロンプトは、以下の6つの戦略に基づいています：

1. **明確な指示 (Write Clear Instructions)**
   - 具体的で詳細な要件
   - 期待される出力形式の明示
   - 曖昧さの排除

2. **参照テキストの提供 (Provide Reference Text)**
   - 必要な背景情報の提供
   - 参照すべきドキュメントの明示

3. **複雑なタスクの分割 (Split Complex Tasks)**
   - 大きなタスクを小さなステップに分解
   - 各ステップが明確で実行可能

4. **モデルに考える時間を与える (Give Model Time to Think)**
   - ステップバイステップの推論
   - 分析計画→実行→検証のプロセス

5. **外部ツールの使用 (Use External Tools)**
   - 必要なツールやAPIの明示
   - 技術仕様の具体的な記述

6. **体系的なテスト (Test Changes Systematically)**
   - 検証可能な成果物の定義
   - 品質基準の明確化

## 📊 改善の効果

### Before（元のプロンプト）
```text
# 目的
- 対象企業の過去30年間の事業をAs-Isとして高精度に分析・解析して
  課題を抽出します。
```

### After（改善版プロンプト）
```text
# 実施手順

## ステップ1: 分析計画の作成
まず、以下の項目について3～7項目の簡潔なチェックリストを作成してください：
- 分析に必要なデータと情報源
- 使用する分析フレームワーク（PEST, 5 Forces, SWOT等）
- 分析の順序と依存関係
- 期待される成果物

## ステップ2: 情報収集と分析
各分析フレームワークを適用する際は、以下を明記してください：
- **分析の根拠**: 使用したデータソースまたは仮定
- **定量データ**: 可能な限り数値を含める
- **比較基準**: 業界平均、競合他社等
```

## 🔄 移行ガイド

### 既存プロンプトからの移行

#### ステップ1: 評価
現在使用しているプロンプトの課題を確認：
- [ ] 出力結果が曖昧で解釈の余地がある
- [ ] 実行手順が不明確
- [ ] 検証基準がない
- [ ] 抽象的な表現が多い

#### ステップ2: 改善版の適用
該当する改善版プロンプトを使用：
- 要求定義作成 → Updated-Business-Documentation.md
- （今後追加予定の他のガイド）

#### ステップ3: カスタマイズ
プロジェクト固有の要件に合わせて調整：
- ユースケースIDの形式
- ファイルパス
- リソースグループ名
- 技術スタック

#### ステップ4: フィードバック
使用結果を記録し、継続的に改善：
- 問題点の記録
- 改善案の提案
- コミュニティへの共有

## 📖 使い方

### 1. 直接コピー＆ペースト
GitHub Copilot Coding Agent の Issue に直接コピーして使用できます。

### 2. テンプレートとして使用
プロジェクトに合わせて以下をカスタマイズ：
- `{ユースケースID}` → プロジェクト固有のID形式
- `docs/` → プロジェクトのドキュメントパス
- 技術仕様セクション → 使用する技術スタック

### 3. 段階的に適用
まず一部のプロンプトで試用し、効果を確認してから全体に展開。

## 🎓 学習リソース

### OpenAI 公式ガイド
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Prompt Engineering Strategies](https://platform.openai.com/docs/guides/prompt-engineering)

### GitHub Copilot
- [Coding Agent Best Practices](https://docs.github.com/ja/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks)
- [Custom Agents](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)

### プロンプトエンジニアリング
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Learn Prompting](https://learnprompting.org/)

## 🤝 貢献

プロンプトの改善提案は以下の方法で：

1. **Issue を作成**
   - 改善が必要な箇所を明記
   - 期待される動作を説明
   - 可能であれば改善案を提示

2. **Pull Request**
   - 改善版プロンプトを作成
   - 変更の意図と効果を説明
   - テスト結果を添付

3. **ディスカッション**
   - 使用経験の共有
   - ベストプラクティスの議論
   - 新しいユースケースの提案

## 📝 更新履歴

### 2025-11-04
- Updated-Business-Documentation.md を作成
- OpenAI 6つの戦略を完全適用
- 具体例とテンプレートを追加
- 検証チェックリストを追加

## 📞 サポート

質問や問題がある場合：
- GitHub Issues でお問い合わせください
- ディスカッションでコミュニティに質問
- [GitHub Copilot サポート](https://support.github.com/)

---

**注意**: これらの改善版プロンプトは継続的に更新されます。定期的に最新版を確認してください。
