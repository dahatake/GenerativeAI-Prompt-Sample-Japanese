# Product Management - ユースケースなど作成

要求定義のドキュメントから、ユースケースを作成します

## ツール

- GitHub Copilot Coding Agent

  GitHub Copilot の **Coding Agent**のIssueからCoding Agentに作業をしてもらう前提です。

  https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/


- 要求定義のドキュメントは、**Markdown**の形式にして、`/docs`フォルダに保存します。
- 各ステップでの**入力**と、**出力先**の、パスとファイル名は適時修正してください。
- そのファイル名でよい場合は、**削除**してください。重複情報が制御に悪い影響ができる可能性があるのと、トークン数を減らすためです。


# Step. 1 ユースケース作成

ユースケース一覧を参考にして、1つだけ選択したユースケースについて、ユースケースの詳細のドキュメントを作成します。

- 使用するカスタムエージェント
  - PM-UseCaseDetail

```text
Use Case一覧から指定UCを1件だけ詳細化し、要求定義ドキュメントと整合したUC定義書（フロー・例外・ルール・NFR・受入・図）を /docs/usecase/ に生成する

# 入力（必須：必ず参照）
- 要求定義ドキュメント：`docs/business-requirement.md`（常に参照）
- Use Case一覧：`/docs/usecase/usecase-list.md`
- ユースケースID: <TARGET_UC_ID>

# 出力先（Markdown）— テンプレ固定
- `/docs/usecase/usecase-<TARGET_UC_ID>.md`
```
