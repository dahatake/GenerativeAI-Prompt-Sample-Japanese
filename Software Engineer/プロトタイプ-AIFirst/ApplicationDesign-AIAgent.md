````markdown
# AI Agent 設計 - 汎用 Agent（LLM + Tool + RAG）向け

AI Agentを設計・実装するための汎用設計ドキュメントです。  

# Step 1. アプリケーション定義（Application Definition）

## 目的
ユースケースを入力として、AI Agent の目的・スコープ・要求（機能/非機能/制約）を設計の土台として確定する。

## 含める内容（推奨）
- 目的 / KPI / 成功定義
- 対象ユーザー / 対象チャネル（Web/Mobile/Voice/社内ツール等）
- 対象タスク範囲（MVP/Phase）
- エスカレーション方針（いつ・誰へ・何を渡すか）
- セキュリティ・法務・コンプライアンス（PII、監査、規制）
- 非機能要件（性能、可用性、スケール、DR、運用体制）
- 外部依存（外部API、データ、検索、チケット/CRM 等）
- 未決事項（不明点の明示）

## 成果物
- `docs/usecase/{ユースケースID}/agent/agent-application-definition.md`

Prompt:

```text
# 役割
あなたは AI Agent（LLM + Tool + RAG）の設計と運用に精通した Senior Architect です。目的は、与えられたユースケース記述から「AI Agentアプリケーション定義書」を正確に作成することです。

# ミッション（最重要）
- 指定されたユースケース記述（<usecase-doc-path>）“だけ”を根拠に、{出力要件}に沿ったMarkdown文書を作成し、指定パスへ保存してください。
- 根拠のない断定、数値の捏造、存在しない依存関係や機能の作り話をしないでください。
- スコープ外の機能追加提案は本文に混ぜないでください（必要なら Open Questions に「示唆として1行」だけ）。

# 入力
- <usecase-doc-path> : ユースケース記述が書かれたファイルパス

# 出力（ファイル）
- docs/usecase/{ユースケースID}/agent/agent-application-definition.md

# 出力要件（見出し構成は固定）
以下の見出しをこの順序で必ず含めてください：
1. Overview
2. Scope
3. Requirements
4. NFR
5. Security & Compliance
6. Dependencies
7. Ops & Monitoring
8. Open Questions

# 文章・分量・形式（出力形状の固定）
- 余計な前置き・雑談・免責・一般論の長文は書かない（成果物中心）。
- 各セクションは「短い段落（最大2つ）＋箇条書き（推奨）」を基本にする。
- Requirements / NFR / Security & Compliance / Dependencies / Ops & Monitoring は箇条書きを優先する。
- ユースケース本文の記述に存在しない要素（例：具体的なSLA数値、特定クラウド製品名、規格準拠の断定）を勝手に追加しない。
- 不明点は本文で補完せず、Open Questions に箇条書きで列挙する。

# 不確実性・曖昧さの扱い（幻覚防止）
- 入力が曖昧・不足している場合：
  - もっとも単純で妥当な解釈に寄せる（勝手に要件を増やさない）。
  - それでも決められない点は「未確定」と明記し、Open Questions に回す。
- 数値・閾値・具体名を断定する必要があるのに根拠がない場合は「要確認」とする。

# 作業手順（ステップバイステップで実行）
1) <usecase-doc-path> を読み、ユースケースID（識別子）を抽出する（不明なら仮IDを置かず、Open Questions に「ユースケースIDの所在」を質問として追加）。
2) ユースケースから、目的 / 利用者 / 入力 / 出力 / 主要フロー / 例外 / 制約 を抜き出す。
3) {出力要件}の見出しにマッピングし、各項目を過不足なく記述する（スコープ逸脱禁止）。
4) 断定している文が「入力根拠あり」かを自己点検し、根拠が弱いものは表現を弱めるか Open Questions に移す。
5) Markdownを生成し、指定パスに保存する。

# 「10分を超える場合」の置き換えルール（再現可能なトリガ）
以下のいずれかに当てはまる場合、定義書の全文作成は“中断”し、代わりに Issue 実行用の分割Promptを作成してください：
- ユースケースが長大で、セクションごとに十分な根拠抽出がこのターンで完了しない
- 不明点が多く、Open Questions が15項目を超える見込み
- 複数ユースケース/複数システムが混在しており、分割しないと誤りリスクが高い

# Issue 用の分割Prompt作成ルール（中断時のみ）
- `work/agent-definition-prompt-<番号>.md` に日本語で追記する（<番号>は1から連番）。
- 各Promptには必ず含める：
  - 対象範囲（例：Requirements セクションのみ）
  - 入力として参照すべき箇所（見出し名や該当段落など、わかる範囲で）
  - 期待する出力（どのファイルのどの章を完成させるか）
  - 完了条件（箇条書きで3〜7個）
- スコープ外の提案は禁止（必要なら Open Questions に回す旨を明記）。

# ファイル書き込みの信頼性対策（ツール実装に依存するが必ず遵守）
- 1つのファイルに大きな文字列を書き込むと失敗し内容が空になることがある。
- そのため、ファイルへ書き込む際は「分割書き込み」を行う：
  - 目安：1回の書き込みは最大 8,000 文字程度に分割
  - 書き込み後にファイル内容が空でないことを確認し、空なら再試行して追記する
  - 最終的にファイルが完成していることを確認する

# 最終出力（このターンであなたが返すもの）
- 通常時：作成した `docs/usecase/{ユースケースID}/agent/agent-application-definition.md` の内容（Markdown全文）をそのまま出力し、同内容をファイルにも保存する。
- 中断時：`work/agent-definition-prompt-<番号>.md` に追記した各Promptの内容を、追記順に出力する（ファイルにも追記する）。
````

---

# Step 2. Agent 粒度設計とアーキテクチャ骨格（Agent Catalog + Components）

## 目的

ユースケースを適切な粒度で Agent に分割し（単一/複数/階層）、各Agentを実装可能なコンポーネントに分解する。

## 成果物

* `docs/usecase/{ユースケースID}/agent/agent-architecture.md`（Agent Catalog + Components + 図を統合）

Prompt:

````text
# Role / Mission
あなたは複雑な要件を、実装可能な粒度の複数Agent（または単体内の論理コンポーネント）に分割し、再現性高くアーキテクチャへ落とし込む Senior Architect です。

# PRIORITY (Conflict Resolution)
以下の優先順位で解釈し、矛盾があれば上位を優先する：
1) Output (STRICT) と MODE SWITCH
2) Design & Scope / Uncertainty rules
3) Decision Rules (Single vs Multi)
4) Section content requirements / ID Rules / Mermaid / JSON rules
5) その他

# CORE TASK
入力の Application Definition から、ユースケース用の AI Agent アーキテクチャ設計ドキュメント（agent-architecture.md）を再現性高く生成する。

# Inputs
- 入力ファイル: docs/usecase/{ユースケースID}/agent/agent-application-definition.md
- このファイル内容のみを根拠として設計する
- 不足は推測で埋めない。必ず「不明」「要確認」または明示した「仮定」にする。
- 入力は会話に貼り付けられる想定。以下のタグで渡される：
  <application_definition>
  ...内容...
  </application_definition>

# Output (STRICT)
- 通常モードの返答は **agent-architecture.md の本文（Markdown）だけ** を出力する。
- 前置き/解説/メタコメント/依頼の言い換え/余談は出力しない。

# TIME-BOX / MODE SWITCH (Priority)
- もし「この1回の返答で」通常モードの agent-architecture.md を完走できない（分量・複雑さ・制約により）と判断したら、直ちに「分割モード」に切り替える。
  - 分割モードでは agent-architecture.md は出力しない。
  - 代わりに、このタスクを“10分単位”のIssueとして実行するためのPromptを作成し、
    `work/agent-design-architecture-prompt-<番号>.md` に日本語で追記するための内容だけを出力する。
  - 出力形式（分割モード時のみ）：
    - ファイル名ごとにブロック化し、各ブロックは「追記用テキスト」だけを書く。
    - 文字列が大きくて書き込みが失敗しそうな場合は、同一ファイルを複数ブロックに分割し、
      各ブロックに「追記順序（1/3, 2/3...）」と「推奨分割単位（例: 2,000〜4,000字）」を明記する。

<output_verbosity_spec>
- 章立ては指定どおり。各章は簡潔に。長い散文は避け、箇条書きと表を優先する。
- 重要な結論（採用方式・分割点・HITL条件・SLA方針）は明確に書く。
- ユーザー依頼の言い換えはしない（意味が変わる場合のみ最小限）。
</output_verbosity_spec>

<design_and_scope_constraints>
- 実装するのは「ユーザーが要求した成果物（Agent一覧、AGC分解、Mermaid図、指定章立て）」のみ。
- 余計な新機能提案、別テンプレ、別ドキュメント生成、不要な補足はしない。
- 不明点を推測で断定しない。
- 指示が曖昧な場合は、最も単純で要件を満たす解釈を優先する（ただし仮定は明記する）。
</design_and_scope_constraints>

<uncertainty_and_ambiguity>
- 入力が曖昧/不足の場合は必ず次のどちらかを実施する（最大限ブレなく）：
  (A) 確認質問を最大3つまで箇条書きで提示 → その後に「仮定」を明示して続行
  (B) 2〜3の解釈案を提示 → 採用した解釈と「仮定」を明示して続行
- 根拠がない事項は「不明」「要確認」と書き、勝手に補完しない。
</uncertainty_and_ambiguity>

# Decision Rules: Single vs Multi (Boundary-based) + User Preference Override
- 原則は境界ベースで判断する（データ/権限/SLA/運用/変更頻度）。
- ただし **ユーザーが「シングルエージェントで設計したい」と明示した場合は、必ず Single を採用**し、
  境界上 Multi が妥当な場合でも、リスク/トレードオフを明記し、Split Candidates で移行計画を強化する。
- 逆にユーザーが「マルチエージェントで設計したい」と明示した場合は Multi を採用し、Single案は出さない。
- 境界判断の観点：
  - データ境界（機密区分/参照範囲）
  - 権限境界（Read/Write/External Send、承認/監査）
  - SLA境界（Fast/Deepの二極化）
  - 運用境界（監視/オンコール/変更管理の責任者）
  - 変更頻度境界（頻繁に変わる業務ルール vs 変わりにくいコネクタ/API）
- 以下のいずれかが明確なら、Multi（またはWorkflow分割）を優先（※ユーザー希望が無い場合）：
  - セキュリティ/コンプラ境界が異なる
  - 権限混在（特にWrite/外部送信）
  - SLA二極化
  - チーム分離
  - 多ドメイン拡張計画
- それ以外は Single を基本とし、単体内部を擬似マルチ（役割分離＋状態機械＋構造化中間成果）で設計する。

# Required Artifacts (MUST)
- 1) Agent粒度を設計し、Agent一覧（ID付与）を作成する
- 2) 各Agentをコンポーネント（AGC-xxx）に分解する（ID付与、表で提示）
- 3) Mermaidで「関係図」と「代表シーケンス図」を含めた agent-architecture.md を作成する

# ID Rules (Deterministic)
- Agent ID: AGT-{ユースケースID}-{NN} （NNは01,02,...）
- Component ID: AGC-{AGTのNN}-{MMM} （MMMは001,002,... 例: AGC-01-001）
- Skill/Toolが必要なら章末Appendixに最小限で列挙し、IDは SKL-{NNN}, TOL-{NNN}
  - ただし入力/要件に根拠があり必要な場合のみ。不要なら追加しない。

# Structured Intermediate Outputs (MUST be embedded in doc)
次のJSONスキーマを、Single/Multiに関わらず doc 内に掲載する（評価できる単体/連携の接続点）。
<structured_output_rules>
- 余計なフィールドを追加しない（スキーマ外フィールドは禁止）。
- 情報が無い場合は null を入れる（推測で埋めない）。
- 最終出力前に、入力を再スキャンして抜けがないか確認し、欠落があれば補正する。
</structured_output_rules>

必須JSON（サンプルとして各1つずつ掲載、各JSONは “例” であり値は入力に根拠のある範囲のみ。未知はnull）：
- IntentClassification
- PolicyDecision
- RetrievalPlan
- EvidencePack
- ActionPlan
- ExecutionResult
- UserResponseDraft
- AuditRecord

# Mermaid Requirements
- 「関係図」：flowchart TD で、Agent/主要コンポーネント/データ境界/HITL/監査ログの流れを示す
- 「代表シーケンス」：sequenceDiagram で、以下のうち入力に最も代表的なものを1本描く
  - Fast→Deep
  - Write(提案→承認→実行)
  - 失敗時のHITL分岐
- Mermaidは構文エラーが無いようにする（記号・矢印・参加者名の整合）

# EXECUTION PROCEDURE (Do internally, do not print)
1) 入力ファイルを読み、ユースケースIDを確定（パスから取得できない場合は、入力本文から最も妥当なIDを抽出し「仮定」で明示）。
2) 要件・制約・境界・SLA・権限・HITL・監査要件を抽出。
3) 曖昧/不足を検出し、<uncertainty_and_ambiguity>の(A)または(B)を実施してから設計を続行。
4) Single/Multiを決定（ユーザー希望があればそれを優先）し、理由とトレードオフを固定フォーマットで記述。
5) Agent設計 → Agent Inventory表を作成（指定カラム厳守）。
6) AGC分解：各Agentを最小限のAGCに分解し、AGC表を作る（ID重複なし）。
7) 必須JSONサンプルを8種すべて掲載（追加フィールド禁止、未知はnull）。
8) Mermaid図を2つ作る（関係図＋代表シーケンス）。
9) Final Quality Gateを満たすまで修正し、最後に入力を再スキャンして欠落を補正。

# Output Format: agent-architecture.md (Strict)
以下の章立てで Markdown を出力する。
- 章番号は欠番のない連番にする。
- Multi の場合は「Multi章」を出し、「Single章」は出さない。
- Single の場合は「Single章」を出し、「Multi章」は出さない。

【Multiの場合の章立て】
## 1. Architecture Decision
## 2. High-Level Architecture
## 3. AI Agent一覧（Agent Inventory）※個別詳細なし
## 4. AGC分解（Component Decomposition）
## 5. Multi採用時の理由
## 6. Split Candidates（Single → Multi移行計画）
## 7. Observability / Governance（運用・監査の最小セット）
## 8. Appendix（任意・最小限）
## 9. Mermaid

【Singleの場合の章立て】
## 1. Architecture Decision
## 2. High-Level Architecture
## 3. AI Agent一覧（Agent Inventory）※個別詳細なし
## 4. AGC分解（Component Decomposition）
## 5. Single採用時の擬似マルチ設計
## 6. Split Candidates（Single → Multi移行計画）
## 7. Observability / Governance（運用・監査の最小セット）
## 8. Appendix（任意・最小限）
## 9. Mermaid

# Section content requirements (within the fixed chapter list)

## 1. Architecture Decision
- 採用方式（Single / Multi）
- 判断根拠（境界ベース：該当項目を列挙）
- 主要トレードオフ（遅延P95/コスト/運用負債/監査可能性/拡張性）
- オーケストレーション方針（Sequential/Concurrent/Group review/Handoff）
- HITLの位置と条件
- （必要なら）確認質問(最大3つ) or 解釈案(2〜3) と、採用した仮定
- （ユーザーがSingle希望を出した場合）「ユーザー希望によりSingle採用」と明記し、境界上の懸念点も短く列挙する

## 2. High-Level Architecture
- 全体フロー（概念）
- データ境界
- 権限境界（Read/Write/External Send）
- SLA境界（Fast / Deep）
- 運用境界（監視・オンコール・変更管理）
- 構造化中間成果（必須JSON 8種：各1サンプル、未知はnull、追加フィールド禁止）

## 3. AI Agent一覧（Agent Inventory）※個別詳細なし
- 採番規約（ID規約をそのまま記載）
- 命名規約（短いルール）
- Agent Inventory（表）
  - Columns: AgentID | Name | Responsibility(1行) | Permission(R/W/Send) | Dependencies | SLA Lane(Fast/Deep) | HITL | Audit | Owner

## 4. AGC分解（Component Decomposition）
- 目的：Agentを実装可能な最小コンポーネントに分解する
- 形式：Agentごとに表を作る（または1つの統合表でも可）
- 各AGCに必ず入れる（表カラム固定）：
  - Columns: ComponentID | BelongsTo(AgentID) | Name | Responsibility(1行) | Inputs | Outputs | Permissions(R/W/Send) | Failure & Fallback(HITL含む) | Observability(log/metric)

## 5. Multi採用時の理由（Multiの場合のみ）
- Multi採用理由（境界ベース）
- 分割点（どの境界で切るか）
- 連携方針（受け渡し単位＝構造化中間成果、失敗時フォールバック、監査ログ連携）

## 5. Single採用時の擬似マルチ設計（Singleの場合のみ）
- 論理コンポーネント（Router/Policy Gate/Retriever/Composer/Executor/Handoff/Audit）
- 中間成果（必須JSONの役割：どの段で生成/検証するか）
- Skill設計方針（Tool直叩き禁止＋3回ルール：3回失敗でHITL/停止）
- Knowledge設計方針（参照宣言→根拠→引用）
- Write操作（提案→承認→実行：承認条件と監査）
- Fast / Deep 分離（ルーティング条件、SLA目標、フォールバック）

## 6. Split Candidates（Single → Multi移行計画）
- 分割候補一覧（表）
  - Columns: Candidate | Boundary 이유 | Trigger Metrics | Hand-off JSON | Owner
- 分割トリガー（定量：遅延/失敗率/監査指摘/権限混在 等）
- 受け渡し契約（スキーマ固定：必須JSONのどれを使うか明記）

## 7. Observability / Governance（運用・監査の最小セット）
- メトリクス（最小セット）
- ログ（最小セット、マスキング・相関ID含む）
- 変更管理（対象/手順/承認/版管理）

## 8. Appendix（任意・最小限）
- 用語辞書（必要なら）
- ナレッジカタログ（必要なら）
- Tool/Skillカタログ（必要なら：必要性に根拠がある場合のみ。不要なら出さない）

## 9. Mermaid
- (ここに関係図: flowchart TD)
- (ここに代表シーケンス: sequenceDiagram)

# Final Quality Gate (Do before output, but DO NOT print this checklist)
- 章番号が欠番なく連番になっている
- Single/Multiの不要章が出ていない
- AgentID/ComponentIDの重複がない
- Agent Inventory 表が指定カラムを満たす
- AGC分解 表が指定カラムを満たす
- 必須JSONが全て掲載され、追加フィールドがない（未知はnull）
- Mermaidが2つあり、構文上破綻していない
- 不明点は「不明/要確認」か、明示した「仮定」になっている

````


# Step 3. AI Agent 詳細設計

## 目的

Agentの実装に必要なコンポーネント利用する外部連携（Tools）と知識基盤（Knowledge/RAG）を、越権防止・根拠提示・運用可能性の観点で設計する。

Prompt:

```text
# Role
あなたは生成AI/AI Agent実装に精通した、上級ソフトウェアエンジニア兼アーキテクトです。

# Goal
入力ドキュメント（後述）を一次情報として参照し、指定された「AI Agent」について、実装に必要な具体的・論理的な詳細設計書をMarkdownで作成してください。
設計書は「契約（I/O・状態遷移・権限・例外・評価）」として書き、実装に直結する粒度にします。

# Scope discipline（重要）
- ユーザーが要求していない追加機能・別案の深掘り・別エージェントの設計はしない。
- ただし、重大な欠落や安全上の必須事項を発見した場合のみ、「Optional: ...」を最大3点まで末尾に列挙する（本文は増やさない）。

# Inputs（参照する一次情報）
- docs/usecase/{ユースケースID}/agent/agent-architecture.md
- docs/usecase/{ユースケースID}/agent/agent-application-definition.md（必要に応じて参照）

# Output（生成するファイル）
- docs/usecase/{ユースケースID}/agent/agent-detail-<Agent-ID>-<Agent名>.md

# 制約（冗長性と更新）
- 途中経過の実況はしない。
- 進捗更新は「新しい主要フェーズ開始」または「計画が変わった」場合のみ、1〜2文で行う。
- 不確実・不足情報は推測で埋めない。設計に必須なら「要確認/TBD/null」で明示する。

# 分割ルール（量ベース）
- 1回の応答で全章を高品質に書き切れない場合は、以下のいずれかで分割する：
  A) 章単位で分割して順に出力する（今回の応答では「章1〜章6」など範囲を明示）
  B) 先に「分割実行用Prompt」を複数作り、`work/agent-design-detail-prompt-<番号>.md`に追記する前提の内容として提示する
- 分割時も、各Promptは“どの入力を読むか・どの章を出すか・出力先ファイル”を明示し、単体で実行可能にする。

# ファイル書き込みの注意（実装環境向け）
- 大きい本文を書き込む際に失敗して空になる可能性がある前提で、書き込みは「章ごと」など小分けで行う想定にする。
- 追記が必要な場合は、追記順序と追記範囲を明記する。

# 設計のガイドライン（必ず遵守）
## 1) 詳細設計の基本原則
- 1エージェント＝1責務（Missionは1文、Doneは検証可能）
- “8つの境界”を必ず埋める（ゴール/責任/データ/行動/評価/運用/SLA/変化）
- 権限分離（Read/Write/External Send、Writeは承認ゲート前提、監査ログ）
- “3回ルール”でSkill化（手順連鎖が3回ならSkill化）
- 評価は最終出力だけでなく遷移判断も対象

## 2) 採用パターン（必要に応じて）
- Router/Orchestrator
- Guarded Execution（Policy Gate + Executor）
- RAG/Grounding Agent
- Planner–Executor
- Human Handoff
- Critic/Verifier

# 手順（Procedure）
1. 入力ドキュメントを読み、対象ユースケースとマルチ/シングル構成、対象Agent候補（Agent-ID/名称）を把握する。
2. 対象Agentを1つに確定し（アーキテクチャ記載に従う）、そのAgentだけの詳細設計を書く。
3. 以下の「出力形式テンプレ」に厳密に従い、空欄は推測で埋めずTBD/null/要確認を入れる。
4. 完了後に「完成判定チェック」でセルフレビューし、足りない章/欠落を補完してから最終出力する。
5. もし分割が必要なら、分割方針A/Bのいずれかで提示する。

# 出力形式テンプレ（この順番・見出しを厳守）
## AI Agent設計の詳細設計ドキュメント

### 1. Agent Overview
- Agent ID（採番規則）
- Agent Name（実装向け名称）
- Owner（開発/運用/承認者）
- Mission（1文）
- Non-Goals（やらないこと）
- ユースケース適用範囲（入力タイプ、対象ユーザー、対象システム）
- 前提（利用できるデータ、権限、環境）

### 2. Done Definition（完了条件）
- 成功条件（検証可能に）
- 失敗条件（根拠なし/禁止行為/SLA超過など）
- Partial successの扱い（縮退運転、Handoff）

### 3. Boundary Matrix（8境界）
- ゴール境界：
- 責任境界：
- データ境界：
- 行動境界：
- 評価境界：
- 運用境界：
- SLA境界：
- 変化境界：

### 4. Inputs / Outputs（I/O契約：実装の核）
#### 4.1 Input Contract
- 入力フィールド一覧（必須/任意）
- 正規化ルール（用語辞書、日付、単位、ID形式）
- 不足情報時の方針（確認質問は最大2つ、それ以外はTBD）

#### 4.2 Output Contract
- 出力形式（Markdownテンプレ/JSON Schema等）
- 必須項目（結論/根拠/次アクション/注意事項など）
- エラー出力（エラーコード、ユーザー向け文言、ログ向け詳細）
- （推奨）JSON Schema（余計なフィールド禁止、欠損はnull/TBD）

### 5. Conversation Design（対話仕様）
- 会話の型
- 確認質問の上限（最大2つ）
- Fast/Deep切替条件
- トーン/禁止表現/同意取得（外部送信前など）
- 多言語対応（必要なら）

### 6. State Machine / Flow（状態遷移）
- 状態一覧
- 遷移条件（ガード条件）
- 例外遷移（権限不足/障害/レート制限/データ不整合）
- Mermaid図（必須）

### 7. Tooling Design（ツール設計）
#### 7.1 Tool Catalog
- Tool ID/名称/目的
- 入力スキーマ/出力スキーマ
- タイムアウト/リトライ/冪等性
- 失敗分類（再試行可否、ユーザー通知/内部処理）

#### 7.2 Permission Model
- Read/Write/External Send区分
- RBACロールと許可範囲
- 承認が必要な操作一覧（実行前ゲート）

### 8. Policy & Guardrails（安全策）
- 禁止行為（PII/機密/危険操作など）
- 根拠提示要件（出典/ログ）
- データマスキング（ログ含む）
- 不確実時の振る舞い（保守的に、必要ならHandoff）

### 9. Error Handling & Resilience（例外・復旧）
- 障害/劣化/データ品質/セキュリティイベント時
- 縮退運転
- リトライ戦略（回数/バックオフ）
- Circuit breaker（連続失敗→Handoff）
- ユーザー向けメッセージテンプレ

### 10. Observability（ログ/メトリクス/トレース）
- ログ仕様（相関ID、ユーザーID扱い、マスキング）
- 監査ログ（判断ログ、実行ログ、根拠）
- メトリクス（P50/P95、逸脱率、拒否率、ツール成功率、介入率）
- アラート条件（SLO違反、失敗急増）

### 11. Evaluation Plan（評価・テスト）
- オフラインテストセット（代表/境界/攻撃的入力）
- 合格基準
- 遷移判断テスト（ルーティング/拒否/承認要求）
- 回帰テスト（プロンプト/ルール更新時）

### 12. System Prompt Instruction Format（実装用）
- Role / Goals / Non-Goals / Inputs / Tools / Procedure / Output format / Examples
- Safeguards（根拠なし→質問or断る、Writeは承認なしで行わない、不確実性の明示）

# 完成判定チェック（出力前に必ず実施）
1. Missionが1文
2. Doneが検証可能
3. 8境界が埋まっている
4. I/Oスキーマがある
5. 状態遷移が図で定義
6. Tool入出力・失敗時が定義
7. Write/外部送信に承認・監査
8. 例外/縮退/エスカレーションが決定
9. 評価（最終＋遷移判断）が定義

```
